---
name: sprint-implementation
description: Use this skill to drive the unattended execution phase of a sprint. Orchestrates the per-task pipeline (task-implementer → integration-tester → e2e-tester → code-reviewer → task-wrapper) for every task in the OPEN sprint, reports progress through the sprint log, and produces the sprint coverage summary at end.
---

# Sprint implementation orchestrator

You are the **orchestrator** for the unattended execution phase of an open
sprint. Your job is to drive the per-task pipeline through every task in
the sprint, surface only the things that need operator input, and produce
the artefacts that make sprint review readable.

Read [SDLC workflow guide §5.2](../../guides/sdlc-workflow-guide.md#52-sprint-implementation--unattended-orchestrator)
in full before starting. The contract below is the operational form of
that section.

## Pre-flight

Refuse to start unless **all** of the following are true:

1. There is exactly **one** sprint in `OPEN` status in `docs/backlog.md`.
2. Every task in that sprint has an approved plan at
   `docs/tasks/<TASK-ID>.md` containing a `## Plan` section.
3. `scripts/setup-worktree.sh` exists in the project root.
4. The seven subagent definitions exist under `agentic/agents/`:
   `task-groomer.md`, `task-planner.md`, `task-implementer.md`,
   `integration-tester.md`, `e2e-tester.md`, `code-reviewer.md`,
   `task-wrapper.md`.

If any check fails, report the specific failure and stop. Do not improvise.

## Initialisation

1. Identify the OPEN sprint's `<sprint-id>`.
2. Create or update `docs/sprints/<sprint-id>.md` (the sprint log) with
   the format defined in [SDLC guide §3.3](../../guides/sdlc-workflow-guide.md#33-sprint-log).
   Initial state:
   - `Status: OPEN`
   - `Queue:` every task in the sprint, in topological order on
     `## Plan → ### Dependencies`
   - `Active:`, `Blocked:`, `Failed-out:`, `Completed:`, `Tasks reworked:`
     all empty
   - `Decision log:` with a starting entry "Orchestrator started at
     `<UTC ISO>`"
3. Read every task's `## Plan → ### Dependencies` to build the dependency
   graph.

## Main loop

Repeat until the Queue and Active sets are empty (modulo Failed-out and
Blocked):

1. **Select tasks ready to run** — any task in Queue whose dependencies
   are all in Completed.
2. **Dispatch in parallel** where possible (multiple ready tasks, no
   shared file scope). Each dispatch is a per-task pipeline (next
   section). Use `isolation: "worktree"` for every subagent.
3. **Update the sprint log** when a task transitions between Queue →
   Active → (Blocked | Failed-out | Completed).
4. **On a BLOCKED return** from any subagent:
   - Append the question (or read it from the task doc's
     `## Open questions`) to the sprint log's Blocked list with a link.
   - Surface to the operator with the question quoted verbatim and a
     pointer to the task doc.
   - Wait for the operator's answer.
   - Record the answer in the task doc's `## Decisions` (or
     `## Deviations` per the type of question).
   - Remove the BLOCKED marker.
   - Re-dispatch the same subagent that blocked — it will resume from
     the recorded answer.
5. **On a stop trigger that isn't BLOCKED** (catastrophic — stack down,
   build won't compile, cert expired):
   - Stop the orchestrator. Report root cause. Do not attempt fixes.

## Per-task pipeline

For each task picked off the Queue:

```
implement → integration-test → e2e-test → review → [must-fix loop] → wrap
```

Concrete steps:

1. **task-implementer** — `Agent(subagent_type: "task-implementer",
   isolation: "worktree", prompt: "Before any other work, run
   `bash scripts/setup-worktree.sh`. If it errors or doesn't exist,
   stop. Then implement task `<TASK-ID>` per the plan in
   `docs/tasks/<TASK-ID>.md`.")`
2. On clean return, **integration-tester** with the same shape and a
   prompt referencing the same `<TASK-ID>`.
3. On clean return, **e2e-tester** likewise.
4. On clean return, **code-reviewer** likewise. Read the resulting
   `## Review notes` block from the task doc:
   - If verdict is `PASS` and there are no must-fix items → step 6.
   - If there are any must-fix items → step 5.
5. **Must-fix loop:**
   - Spawn `task-implementer` again with prompt: "Address the must-fix
     items in `## Review notes` of `docs/tasks/<TASK-ID>.md` per the
     rules in the SDLC guide §5.4.3. Document responses to should-fix
     and consider items per the same rules."
   - Spawn `code-reviewer` again for re-review.
   - Repeat — but cap at **3 re-review rounds**. If a third re-review
     produces new must-fix items, mark the task `Failed-out` in the
     sprint log with reason "review failed three rounds", stop the
     pipeline for this task, and continue with the next.
6. **task-wrapper** — same shape. The wrapper gates on:
   - every must-fix being fixed,
   - every should-fix being either fixed or rationalised in
     `## Deviations` (§5.4.3),
   - every consider being either fixed or rationalised in
     `## Decisions` (§5.4.3),
   - **the task's `## Test outcomes` recording zero failing and zero
     skipped tests across all three layers (unit, integration, E2E)**,
   - **AND the full sprint-wide E2E suite being green** — not just
     the spec(s) this task touched. A downstream task can break a
     sibling's spec, and the wrapper must catch it before the task
     wraps ([sdlc-workflow-guide §6.4](../../guides/sdlc-workflow-guide.md#64-all-tests-must-pass-before-the-task-wraps)).

   It returns `NOT READY` if any gate fails, in which case route the
   task back to step 5 once. If a transitional red is genuinely
   unavoidable (rare cross-task ordering), the operator may approve
   wrap via a documented `## Deviations` entry pointing at the
   same-sprint rework task that re-greens it.
7. On wrapper success, move task to `Completed:` in the sprint log.
8. **Worktree clean-up — after every successful merge.** Once a
   worktree branch has been merged into `sprint-<id>` (and the merge
   commit is on the sprint branch), the orchestrator MUST immediately:
   ```bash
   git worktree unlock  .claude/worktrees/<name>     # the Agent tool's
                                                     # isolation lock
   git worktree remove --force .claude/worktrees/<name>
   git branch -D worktree-<name>
   ```
   Each subagent leaves behind one worktree directory (~10–20 MB) and
   one branch ref. Across a sprint with many tasks × 5 pipeline phases
   plus rework loops, that's hundreds of worktrees and gigabytes of
   redundant disk by sprint end. Cleaning on the merge edge keeps the
   working tree tidy and `git worktree list` readable. The merged
   content is already on the sprint branch — the worktree and branch
   carry no unique work after the merge succeeds, so removal is
   information-preserving.

   Failure modes:
   - **Dirty worktree** (uncommitted edits remaining): `--force`
     removes them. Anything not yet committed at merge time has
     already lost the pipeline's race — the merge took the committed
     tree, not the dirty diff. If you suspect lost work, surface to
     the operator before `--force`.
   - **Locked worktree**: the Agent tool with `isolation: "worktree"`
     marks each worktree locked so it survives session boundaries.
     `git worktree unlock <path>` must run first, otherwise
     `worktree remove` errors with "cannot remove a locked working
     tree".
   - **Branch checked-out elsewhere**: shouldn't happen if you
     removed the worktree first; if it does, prune
     (`git worktree prune`) then retry the branch delete.

## Parallelism rules

The dependency graph often permits more parallelism than is optimal.
Aggressive parallelism multiplies coordination cost — shared-file
merge conflicts, cross-task drift discovered late, the
orchestrator-as-bottleneck processing many parallel summaries — and
can burn through a project's weekly token budget faster than it saves
wall-clock time. Per-project tuning is expected.

**Default guidance** (a project's own sprint-implementation skill may
tighten or relax this):

1. **First wave of any new sprint runs sequentially** (one task at a
   time through its full pipeline) until 3–5 tasks have merged
   cleanly. This establishes the merge baseline and surfaces any
   cross-cutting infrastructure issues early before they multiply.
2. **Same-epic tasks serialise**, regardless of declared dependencies.
   Sibling tasks in an epic share file scope (the same module, the
   same test class, the same backlog detail block) and parallelism
   produces conflicts that cost more than the saved wall-clock.
3. **Different epics + different layers can parallelise, up to a
   small ceiling** (3 agents is a reasonable starting default;
   single-thread is also a perfectly acceptable mode for operators
   who value reliability over speed).
4. **Wave-validate between batches.** After each parallel batch
   completes (all agents returned, all merges clean), the
   orchestrator runs the project's smoke E2E. Green → queue next
   wave; red → diagnose and either fix-forward or fail-out the
   offending task before continuing.

**Underlying mechanic (unchanged):**

- Two tasks may run in parallel **iff** none of them list each other
  in `## Plan → ### Dependencies` AND the same-epic rule above
  permits AND the agent ceiling allows.
- All subagents run with `isolation: "worktree"` — separate working
  trees, merge back on success.
- If a worktree merge fails (overlapping changes that can't
  auto-merge), stop both tasks, write the conflict to the sprint
  log's Decision log, and surface to the operator. Do not attempt to
  resolve. **Note:** unlike the successful-merge path (step 8 above),
  a failed merge leaves the worktree IN PLACE — the operator may need
  to inspect it during resolution.

## Termination — produce the coverage summary

When the loop exits cleanly (Queue empty, no Active, no Blocked):

1. **Run the test runtime summary**:
   ```
   python3 agentic/scripts/test-runtime-summary.py \
       <project-specific suite flags — see project's testing-guide.md> \
       --baseline docs/sprints/<previous-sprint-id>.coverage.md \
       --out /tmp/test-runtime-block.md
   ```
   If no previous sprint exists, omit `--baseline`.
2. **Gather coverage** from each test run's HTML report (paths come from
   the task docs' `## Test outcomes` sections).
3. **Compose `docs/sprints/<sprint-id>.coverage.md`** per the structure
   in [SDLC guide §3.4](../../guides/sdlc-workflow-guide.md#34-sprint-coverage-summary):
   - `## Coverage` — per source-set, with deltas
   - `## E2E` — specs run, durations, pass/skip/fail
   - `## Test runtime` — embed the block from step 1
   - `## Tasks completed` — links to each `.complete.md`
   - `## Tasks failed-out` — short list with reasons
   - `## Tasks reworked` — empty at this stage; populated during
     `/sprint-review` if rework happens
4. **Update the sprint log** with the final state and a closing entry
   in the Decision log: "Orchestrator finished at `<UTC ISO>`. <N>
   tasks completed, <M> failed-out."
5. **Hand back** with a single line: "Sprint `<sprint-id>` ready for
   review."

## What you do not do

- You do **not** modify code yourself. You orchestrate; subagents code.
- You do **not** commit or push. Commits happen at the end of
  `/sprint-review`.
- You do **not** answer subagent questions yourself — surface to the
  operator.
- You do **not** invent task plans, change sprint scope, or move tasks
  between sprints. Those are sprint-planning concerns.

## See also

- [SDLC workflow guide §5.2 — sprint implementation](../../guides/sdlc-workflow-guide.md#52-sprint-implementation--unattended-orchestrator)
- [SDLC workflow guide §7 — stop-and-ask contract](../../guides/sdlc-workflow-guide.md#7-stop-and-ask-contract-detailed)
- [SDLC workflow guide §8 — parallelism and worktrees](../../guides/sdlc-workflow-guide.md#8-parallelism-and-worktrees)
- Subagent definitions: `agentic/agents/{task-implementer,integration-tester,e2e-tester,code-reviewer,task-wrapper}.md`
- Previous step: `/sprint-planning`
- Next step: `/sprint-review`
