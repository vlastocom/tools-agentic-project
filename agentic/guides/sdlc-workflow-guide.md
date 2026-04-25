# SDLC workflow guide

This guide documents the **software-development lifecycle (SDLC) workflow** used
across this organisation's agentic projects — the cadence between planning,
implementation, and review, how work flows between the human operator and
autonomous agents, and the artefacts each phase produces.

It is **project-agnostic**. Every concrete filename, path, or tool choice is
phrased as a shape ("the project", "the backlog") rather than as a specific
instance.

Concretes (which database? which language? which CI?) live in project-specific
docs under `docs/` or in other guides in this directory.

## 1. Purpose and scope

### Why we have a documented workflow

Without a shared rhythm, agent-assisted development tends to two failure modes:

1. **Over-supervised** — the operator is in every decision, pace collapses to
   human speed, and the agent isn't actually doing the lion's share of work.
2. **Under-supervised** — the agent goes far on a bad premise, burns cycles,
   and the operator rediscovers the problem a day late.

This workflow aims for a **middle path**: the agent works unattended by
default, but stops immediately on a small, well-defined set of triggers. The
operator joins at three cadences — sprint planning, any mid-sprint block, and
sprint review — and the rest of the time the agent runs.

### Applicability

Follow this workflow when:

- The project has a **backlog** (per the [backlog structure](backlog-structure.md))
- Work is organised into **sprints** with explicit goals
- The operator is **one person** or a small trusted group — the workflow
  explicitly does not model multi-team coordination, change-advisory boards,
  or formal sign-off chains

## 2. The three modes at a glance

Every unit of work passes through three operator-relationship modes, in order:

```
                  ┌──────────────┐
 PLAN             │   operator   │ ←─── interactive, iterative
 (attended)       │    present   │      tightly-coupled discussion
                  └──────┬───────┘
                         │ plan approved
                         ▼
                  ┌──────────────┐
 IMPLEMENT        │  agent runs  │ ←─── operator away by default
 (unattended)     │   unattended │      interrupted only by stop-and-ask
                  └──────┬───────┘      triggers
                         │ sprint done
                         ▼
                  ┌──────────────┐
 REVIEW           │   operator   │ ←─── operator reviews a self-contained
 (attended)       │    present   │      batch; coverage + summaries already
                  └──────────────┘      generated — reads, doesn't compute
```

| Mode        | Operator role                    | Agent role                                | Expected cadence |
|-------------|----------------------------------|-------------------------------------------|------------------|
| **Plan**    | interactive, approves            | proposes, drafts, iterates with operator | hours per sprint |
| **Implement**| absent; answers blocks          | executes end-to-end through task cycle   | days per sprint  |
| **Review**  | audits batch, accepts or kicks back | produces summaries, coverage reports  | hours per sprint |

## 3. Artefact taxonomy

Work produces long-lived artefacts that outlive any individual agent run. The
artefacts are **append-only** wherever feasible — past state is never erased,
only extended.

### 3.1 Backlog

`docs/backlog.md` — the single source of truth for what work exists, structured
per [backlog-structure.md](backlog-structure.md). Sprint goals, areas, epics,
tasks, and a consolidated task table live here. The backlog is **the input**
to planning and **the record** of progress (task status transitions).

### 3.2 Task document

Every task gets a single evolving file: `docs/tasks/<TASK-ID>.md` (renamed to
`<TASK-ID>.complete.md` at wrap-up). This file is the **task's memory across
agent invocations** and the **review artefact for the operator**. Sections are
appended, not rewritten:

```
# <TASK-ID>: <short name>

## Plan
    Written by the task-planner agent. Technical approach, affected files,
    acceptance criteria, test strategy, estimated cycle.

## Progress log
    Date-stamped entries from the task-implementation / integration-testing
    agents. What was attempted, what worked, what didn't.

## Decisions
    Each non-trivial choice made during implementation, with rationale.
    "Used Set<T> over List<T> because ordering doesn't matter and we need
    de-duplication."

## Deviations
    Places where the work departed from the plan. Minor deviations are
    logged here. Major deviations trigger stop-and-ask (§7).

## Test outcomes
    Per-run summary of unit + integration + (for E2E tasks) e2e test
    results, with links to HTML coverage reports.

## Open questions
    Written when an agent blocks. Populated on block; cleared on resume.
    See §7.

## Review notes
    From the code-reviewing subagent. Must-fix / should-fix / consider
    items (§5.4.3).

## Wrap-up
    Final state, written by the task-wrapup agent. Summary of delivered
    change, any follow-up tasks surfaced, links to coverage.
```

The task file is the **handshake** between agents: each agent reads the
preceding sections and appends its own.

### 3.3 Sprint log

`docs/sprints/<sprint-id>.md` — a running dashboard maintained by the
sprint-implementation orchestrator during execution. Operator can read it at
any time to see sprint state without scrolling conversation:

```
# Sprint <id>

## Status
    <PLANNING | OPEN | CLOSED>  last-updated: <UTC timestamp>

## Queue
    [pending tasks, in scheduled order]

## Active
    [task currently being worked, with the phase it's in]

## Blocked
    [tasks blocked on operator input; link to each task's Open Questions]

## Failed-out
    [tasks dropped from the sprint because they couldn't be delivered;
     each has a short reason]

## Completed
    [wrapped tasks, in completion order]

## Decision log
    Sprint-level decisions — changes to the plan, answers to operator
    questions, interventions.
```

### 3.4 Sprint coverage summary

`docs/sprints/<sprint-id>.coverage.md` — produced by the orchestrator as its
final act before handing back to the operator. Self-contained reading:

- Per-source-set (unit / integration) coverage numbers + HTML link
- Frontend coverage numbers + HTML link
- E2E: specs run, pass/skip/fail counts + report link
- Coverage delta vs. previous sprint

### 3.5 CHANGELOG

Updated during sprint-wrapup with one section per released version (if any
release artefacts were produced).

## 4. Skills and subagents inventory

Two primitives in Claude Code:

- **Skill** = instructions loaded into the current (main) conversation when
  invoked. Works in-context. Best when the operator is actively iterating.
- **Subagent** = a separate Claude instance spawned with its own conversation
  and context. Clean slate per invocation. Best for unattended, bounded work.

### 4.1 Slash commands (user-invokable)

| Command                      | Kind           | When                                           |
|------------------------------|----------------|------------------------------------------------|
| `/sprint-planning`           | skill          | Open a new sprint                              |
| `/sprint-implementation`     | skill (orch.)  | Kick off the unattended implement phase        |
| `/sprint-review`             | skill          | Batch-review a just-completed sprint           |
| `/task-planning <TASK-ID>`   | skill          | Re-plan a specific task (escape hatch)         |
| `/task-implementation <TASK-ID>` | skill      | Manually invoke the implementer on one task    |
| `/integration-testing <TASK-ID>` | skill      | Manual integration-test run                    |
| `/e2e-testing <SPEC>`        | skill          | Manual E2E run                                 |
| `/code-reviewing <TASK-ID>`  | skill          | Manual code review                             |
| `/task-wrapup <TASK-ID>`     | skill          | Manual wrap-up                                 |

The "skill" rows above load instructions into the main conversation. Most of
them delegate to a subagent under the hood — the slash command is the
user-facing verb; the subagent is the worker.

### 4.2 Subagents

| Subagent              | Spawned by                                       | Context brief                          | Output                                          |
|-----------------------|--------------------------------------------------|----------------------------------------|-------------------------------------------------|
| `task-groomer`        | `/sprint-planning`                               | Backlog + task row                     | Updates the task row's Description + Requirements Reference so it's plannable |
| `task-planner`        | `/sprint-planning` (after groom) or `/task-planning` | Groomed task row + relevant design docs | `docs/tasks/<TASK-ID>.md` with `## Plan` section populated |
| `task-implementer`    | `/sprint-implementation` per task                | Task doc                               | Code changes + `## Progress log` / `## Decisions` / `## Deviations` |
| `integration-tester`  | `/sprint-implementation` after implement         | Task doc + code changes                | Integration tests committed; `## Test outcomes` updated |
| `e2e-tester`          | `/sprint-implementation` after integration tests | Task doc + running dev / stage stack   | E2E spec extended / branched / created per plan; `## Test outcomes` updated |
| `code-reviewer`       | `/sprint-implementation` after E2E tests         | Task doc + diff                        | `## Review notes` with findings (§5.4.3)       |
| `task-wrapper`        | `/sprint-implementation` after review closed     | Task doc                               | Renames file to `.complete.md`; updates backlog row; writes `## Wrap-up` |

All subagents run in `isolation: "worktree"` for safety (§8).

### 4.3 Why the split

- **Fresh context = independent judgement.** The code-reviewer subagent hasn't
  lived inside the implementation; it sees the diff cold. Caller bias can't
  leak in.
- **Bounded scope.** Each subagent has one job; easier to brief, easier to
  audit.
- **Parallelism.** Subagents spawned in parallel don't share context, so
  they can't corrupt each other's working state (§8).

## 5. Phase reference

### 5.1 `/sprint-planning` — interactive, main conversation

**Input:** backlog in its current state; operator's intent for the next
sprint.

**Sequence:**

1. Operator opens `/sprint-planning`. Skill loads.
2. Iterate with operator on:
   - Sprint main goal (1–2 sentences)
   - Additional goals (optional)
   - Success criteria
   - Candidate task list (drawing from `TODO` tasks in the backlog, sized
     to the sprint capacity)
   - Estimated duration
3. Once operator approves the task list, skill writes the sprint definition
   to the backlog (status `PLANNING`).
4. Skill spawns **grooming subagents** in parallel — one per sprint task,
   in worktrees. Each agent ensures its task row has:
   - A clear, 1–2-paragraph Description
   - A Requirements Reference pointing at a concrete design doc / section
   - Any ambiguity surfaced as a **question to the operator**, written to
     a per-task questions file
5. When all grooming agents return, skill:
   - Presents accumulated operator-questions in batch
   - Operator answers; skill updates task rows
6. Skill spawns **task-planning subagents** in parallel. Each produces
   `docs/tasks/<TASK-ID>.md` with `## Plan`.
7. Skill presents the plans to the operator for review.
8. Iterate: operator may redirect specific plans (`/task-planning <TASK-ID>
   --revise`); skill re-spawns the planner with the redirect.
9. Once operator approves all plans, skill marks the sprint `PLANNING →
   OPEN` in the backlog and hands off.

**Output:** Sprint is in `OPEN` status (ready for implementation). Every task
has a `docs/tasks/<TASK-ID>.md` with a `## Plan`. Every task row has a
concrete Description and Requirements Reference.

#### Small-task fast path

For tasks estimated at ≤ 0.5 engineering days, grooming and planning can
collapse into a single subagent run (the `task-planner` does light grooming
implicitly) **unless** the task type is `BUG`, in which case the grooming
phase is mandatory — bug reproduction is the grooming output, and the plan
must lead with the **TDD test** that reproduces it (§8).

### 5.2 `/sprint-implementation` — unattended orchestrator

**Input:** Sprint in `OPEN` status; every task has an approved plan.

**Sequence:**

The orchestrator runs in the main conversation as a dispatcher. It does not
code — it reads the sprint log, picks the next task (or tasks, for
parallelism — §8), and dispatches a pipeline of subagents:

```
┌─── task ───┐
│ implementer │ ──▶ writes/edits code + unit tests, updates Progress log
└─────┬──────┘
      │
      ▼
┌───────────────────┐
│ integration-tester│ ──▶ adds integration tests, runs full suite
└─────┬─────────────┘
      │
      ▼
┌──────────────┐
│ e2e-tester   │ ──▶ extends / branches / writes E2E spec per plan,
└─────┬────────┘     runs against the dev or stage stack
      │
      ▼
┌──────────────┐
│ code-reviewer │ ──▶ writes Review notes
└─────┬────────┘
      │
      ▼    (if Review notes contain any 'must-fix' items)
┌──────────────┐
│ implementer  │ ──▶ addresses must-fix items
└─────┬────────┘
      │
      ▼    (→ re-review)
      …
      │
      ▼    (Review passes)
┌──────────────┐
│ task-wrapper │ ──▶ rename to .complete.md, update backlog
└──────────────┘
```

E2E tests are a **phase inside the per-task pipeline**, not a separate
class of tasks. Whenever a task introduces user-visible behaviour, the
e2e-tester extends or writes the E2E spec that exercises that behaviour.

The planner specifies, in the task's `## Plan → ## Test strategy`, the
**widest E2E flow** this task's functionality can plausibly extend or
anchor — and which of these the e2e-tester should do:

- **extend** an existing spec — the new behaviour is a natural
  continuation of an existing flow
- **branch** — create a sister spec at the point of divergence — the
  new behaviour represents a distinct sub-flow from a shared starting
  point
- **write new** — no prior spec covers this surface

Tasks without user-visible behaviour (pure backend services, scaffolding,
config, infra-only work) get an empty E2E phase: the e2e-tester reads the
plan, sees `no E2E phase`, returns immediately. This is the same shape as
the integration-tester for tasks without integration surfaces.

When wider flows emerge as features land in sequence — e.g. project
creation, then area creation, then epic creation — the planner's
widest-flow rule causes each subsequent task's plan to extend the prior
spec, so the test grows naturally with the system. No "happy-path
cross-feature task" is needed; the cross-feature flow is the destination
the per-task extends arrive at.

After each task completes, the orchestrator:

- Updates `docs/sprints/<sprint-id>.md` (Completed list)
- Picks the next task

When **all** tasks are wrapped or failed-out, the orchestrator:

1. Generates `docs/sprints/<sprint-id>.coverage.md`
2. Writes the final state to the sprint log
3. Hands back to the operator with a single line: "Sprint X ready for review."

**Termination conditions:**

- **Normal completion** — every task wrapped or failed-out.
- **Operator interrupt** — operator re-enters conversation and asks to
  pause. Orchestrator finishes the current agent's current run, writes
  state, hands back.
- **Catastrophic** — build system broken, DB unreachable, cert expired.
  Orchestrator stops, reports root cause, waits.

### 5.3 Stop-and-ask contract — the interrupt triggers

An agent **must** stop and ask the operator in each of these cases:

1. **Decision point** — any choice that materially affects other tasks, the
   architecture, or the product. Not: a naming choice for a local variable.
2. **3+ iterations without progress** — three attempts at fixing a failing
   test (or compiler error, or integration failure) where each attempt leaves
   the failure count the same or worse.
3. **Genuine uncertainty** — "I don't know which of two paths to take, and
   picking wrong wastes more than it saves".
4. **Major deviation from plan** — the plan said X, reality demands Y, and Y
   affects downstream tasks.
5. **Unrelated broken thing** — agent discovers something broken that isn't
   in the plan. Stop, report, don't fix silently.

An agent **must not** stop for:

- Small, reversible local choices (variable names, import ordering, minor
  refactors).
- Questions the plan already answered — re-read the plan first.
- Tool or dependency discoveries that don't change the approach.

**Mechanics of a stop:**

1. Agent appends the question to the task doc's `## Open questions` section
   with a timestamp.
2. Agent writes `BLOCKED` as the current status into the task doc's first
   line (conventional marker `<!-- STATUS: BLOCKED -->`).
3. Agent returns control to its caller (orchestrator or main).
4. Orchestrator propagates `BLOCKED` to the sprint log; surfaces **the
   question** (not the agent's investigation) in a terse prompt to the
   operator.
5. Operator answers; answer appended to the task doc's `## Decisions` with
   its own timestamp.
6. Orchestrator re-dispatches the blocked agent with a brief like "you were
   blocked on question X; the answer is Y; continue".

Re-dispatched agents are idempotent — they read the task doc, figure out
where they left off, and resume. No state lives only in the agent's
conversation.

### 5.4 Code-reviewing subagent specifics

#### 5.4.1 Brief

The code-reviewing subagent receives a tight brief:

- Link to the task doc (plan + progress log + decisions + deviations)
- `git diff` against the sprint's base commit
- Test outcomes (unit, integration)
- Pointer to relevant design docs (from `docs/` or guides)

It **does not** get the implementer's conversation history — that's the
point.

#### 5.4.2 Expected questions

The reviewer is briefed to check:

- Does the diff match the plan? (correctness to spec)
- Is the diff minimal? (no gratuitous refactors, no unrelated changes)
- Do the tests exercise the change? (TDD ground truth)
- Any obvious correctness issues, security concerns, or contract violations?
- Readability for a reader who didn't author it.
- Adherence to the project's code-layout guides (if present).

#### 5.4.3 Finding taxonomy

Reviewer writes findings into the task doc's `## Review notes`, classified:

| Class       | Meaning                                        | Implementer action                                   |
|-------------|------------------------------------------------|------------------------------------------------------|
| **must-fix**| Correctness bug, security issue, contract violation | Fix before proceeding to wrap-up                  |
| **should-fix**| Style, readability, naming                   | Fix unless a stated reason not to                    |
| **consider**| Alternative approach, suggestion                | Respond inline: "fixed" / "noted" / "disagree: why"  |

Re-review happens after `must-fix` items are addressed. A re-review that
produces new `must-fix` items that were not apparent in the first pass is
allowed once; on the third round of new must-fix findings, the task is
**failed-out** of the sprint.

### 5.5 `/sprint-review` — interactive, main conversation

**Input:** Sprint in `OPEN` status with all tasks wrapped or failed-out.
Coverage summary and sprint log exist.

**Sequence:**

1. Operator opens `/sprint-review`. Skill loads.
2. Skill walks the operator through:
   - **Sprint goal attainment** — did the completed work match the
     sprint goals? Read from sprint log + coverage.
   - **Task-by-task**: for each `.complete.md`, summarise delivered change
     + any decisions or deviations. Operator skims in depth or skips.
   - **Coverage summary** — operator reads `<sprint-id>.coverage.md`
     alongside the skill; any dip gets attention.
   - **E2E flows** — explicit walk-through of E2E specs run, per spec:
     what the flow covered, outcome, any flake.
   - **Decisions and deviations** — aggregate list from all task docs.
   - **Failed-out tasks** — what the operator wants to do: drop, roll
     forward to next sprint, or break smaller.
3. Once operator accepts the sprint, skill:
   - Marks the sprint `OPEN → CLOSED` in the backlog.
   - Writes a final sprint summary to the sprint log.
   - Proposes the git-commit message; operator edits or accepts.
   - Commits and pushes (or stops if the operator wants to stage first).
4. Skill prompts "Start the next sprint?" — yes → loops back to
   `/sprint-planning`.

## 6. TDD rule

**Red-green is mandatory for any task that introduces testable behaviour.**
In practice:

- Any **BUG** task: write the failing test that reproduces the bug first.
  That test becomes the acceptance criterion.
- Any **FEATURE** task: the test that exercises the feature exists and
  fails before the implementation exists.
- Any **TECHNICAL** task that produces a service, function, or module
  (things that can be unit-tested): same rule.

**Exempt:**

- Scaffolding / config / tooling tasks where there's nothing to red-green.
  Examples: `npm create vite`, `gradle init`, issuing a Let's Encrypt cert,
  configuring a reverse-proxy rule.
- Documentation-only tasks.

The implementation agent is briefed with this rule. A reviewer that sees a
non-exempt task with tests written after the fact flags it as a **must-fix**.

## 7. Stop-and-ask contract (detailed)

Repeated here for prominence. Agents stop immediately on:

1. **Decision point** affecting scope, API, data model, or downstream tasks.
2. **3+ iterations without progress** on the same failing artefact (test
   still red, compiler still erroring, integration still failing). Track
   attempts; after the third, stop.
3. **Genuine uncertainty** where one path costs materially more than the
   other if wrong.
4. **Major deviation from plan** — anything that affects downstream tasks,
   invalidates a test, or requires the plan to be re-approved.
5. **Unrelated broken thing** — never fix silently; always surface.

Ignore small, local, reversible choices. Move.

## 8. Parallelism and worktrees

### 8.1 The default is parallel where safe

`/sprint-implementation` examines the plan graph and runs tasks in parallel
**where their dependencies allow**. A task whose plan lists any uncompleted
dependency in `## Plan → Dependencies` waits.

### 8.2 Worktree isolation

Every subagent runs with `isolation: "worktree"`. Each gets its own git
worktree branched from the sprint's base commit. This has two consequences:

- Two parallel agents cannot mutate the same file concurrently — they are
  in different working trees.
- When an agent finishes, the orchestrator merges its worktree branch
  back into the sprint branch.

### 8.3 Merge conflicts are operator concerns

If two parallel agents modify overlapping files and the merge fails, the
orchestrator does **not** attempt to resolve — it stops, reports the
conflict, writes the conflicted state to the sprint log, and waits for the
operator.

This is by design. An automated merge resolver would have to understand the
design intent of both changes, which it doesn't. Stopping is cheap and
correct.

### 8.4 Sequential is fine

If the sprint's plan graph is highly linear, parallelism is minimal and
that's fine — the sequential execution is simpler and still faster than
operator-attended work.

## 9. `.claude/` ↔ `agentic/` directory pattern

### 9.1 Why two directories

Claude Code reads configuration and subagent/skill definitions from a
`.claude/` directory at the repo root. But:

- `.claude/` is conventionally gitignored (contains per-machine settings).
- The actual content (skills, agents, hooks, scripts, guides) is the core
  value of the project and should be committed.

Resolution: keep the real content under `agentic/` (committed), and make
`.claude/` a set of **symlinks** into `agentic/`. The symlinks themselves
are committed via `git add -f`.

### 9.2 Layout

```
<project-root>/
├── .claude/
│   ├── setup_claude_dir.sh     ← the setup script (§9.3)
│   ├── settings.json           ← Claude Code settings (permissions etc.)
│   ├── agents   → ../agentic/agents    (symlink, force-committed)
│   ├── guides   → ../agentic/guides    (symlink, force-committed)
│   ├── hooks    → ../agentic/hooks     (symlink, force-committed)
│   ├── scripts  → ../agentic/scripts   (symlink, force-committed)
│   └── skills   → ../agentic/skills    (symlink, force-committed)
└── agentic/
    ├── agents/                 ← subagent definitions (.md files)
    ├── guides/                 ← this file and its siblings
    ├── hooks/                  ← Claude Code hooks
    ├── scripts/                ← utility scripts
    └── skills/                 ← skill definitions (.md files)
```

### 9.3 The setup script

Lives at `.claude/setup_claude_dir.sh`. Idempotent. Iterates every
subdirectory in `agentic/` and creates a corresponding symlink in `.claude/`.
Force-adds each symlink to git so the tracked symlink survives `.claude/`'s
gitignore.

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
AGENTIC_DIR="${REPO_ROOT}/agentic"
CLAUDE_DIR="${REPO_ROOT}/.claude"

for target in "${AGENTIC_DIR}"/*/; do
    name="$(basename "${target}")"
    link="${CLAUDE_DIR}/${name}"
    ln -sfn "../agentic/${name}" "${link}"
    git -C "${REPO_ROOT}" add -f "${link}"
done
```

### 9.4 Operator first-time setup

For a new project that follows this pattern:

```bash
git clone <project-url>
cd <project>
./.claude/setup_claude_dir.sh       # create the symlinks
```

The symlinks are already tracked (they were committed at project creation),
so usually the script is a no-op on clone. Running it is still safe:
`ln -sfn` is idempotent, `git add -f` is idempotent for already-tracked
paths.

### 9.5 Adding a new top-level directory

When the project gains a new `agentic/<new-dir>/`, re-run the setup script.
It picks up the new directory and creates the symlink.

### 9.6 Per-machine `.claude/settings.local.json`

Claude Code supports a `settings.local.json` sibling file for per-machine
overrides. It is gitignored. The committed `settings.json` contains the
project defaults (permissions, additional directories, etc.); the local
file is for a developer's personal preferences.

## 10. Project template

A ready-to-clone scaffold lives in a sibling `agentic-project/` repo (or
equivalent per-organisation convention), populated with:

- `.claude/` with the setup script and a permissive default
  `settings.json`
- `agentic/` with empty `agents/` and `hooks/` directories, populated
  `skills/` (the reusable skill set), `scripts/` (the reusable utilities),
  and `guides/` (this guide and its generic siblings)
- `CLAUDE.md` template with placeholders for project mission
- `README.md` template with placeholders for project description
- `.gitignore` / `.claudeignore` defaults

To bootstrap a new project, clone the template, fill in the placeholders,
and add project-specific guides under `agentic/guides/` as the work reveals
them.

## 11. Worked example — a one-sprint loop

A concrete walk-through of the cadence. Times are illustrative, not
prescriptive.

### Day 0 — Sprint planning (1–2 hours, attended)

- Operator: `/sprint-planning`
- Iterate with skill: sprint goal = "auth-module MVP"; pick 7 tasks from
  backlog (AUTH-01-0001 .. AUTH-01-0007)
- Skill spawns 7 grooming subagents in parallel
- Two return with operator-questions; operator answers both (5 min)
- Skill spawns 7 planning subagents; all return
- Operator reviews plans; redirects 1 ("use zod instead of yup"); planner
  re-runs; plan accepted
- Sprint status → `OPEN`; control handed off

### Day 1–5 — Sprint implementation (unattended, ~4 days of agent time)

- Operator: `/sprint-implementation`
- Orchestrator picks AUTH-01-0001 (no deps); spawns `task-implementer`
  subagent; it codes + writes unit tests
- Implementer returns; orchestrator spawns `integration-tester`; tests
  pass
- Orchestrator spawns `code-reviewer`; returns 2 must-fix items
- Orchestrator spawns `task-implementer` again with "address must-fix";
  returns
- Re-review: clean
- Orchestrator spawns `task-wrapper`; task renamed to `.complete.md`;
  backlog updated
- Next task …

Mid-day 3, AUTH-01-0004 implementation agent blocks on "the plan says
store session tokens in Redis, but Redis isn't in our infra — how should
I proceed?". Orchestrator surfaces this via the mechanism in §5.3.
Operator answers ("use an in-memory store for MVP; Redis is a follow-up
task"). Implementation resumes.

End of day 5: orchestrator writes sprint coverage summary; hands back
with "Sprint 2026-MM-DD ready for review."

### Day 6 — Sprint review (1–2 hours, attended)

- Operator: `/sprint-review`
- Reviews each task's `.complete.md` — most are skim, two get deeper
  reading
- Reads coverage summary — backend 82% lines (up from 78%), frontend
  76% lines (up from 70%), E2E 5 specs green
- One failed-out task (AUTH-01-0006): operator decides to roll it into
  the next sprint with a tighter plan
- Operator accepts sprint; skill commits + pushes with generated message

Total operator time: ~3–4 hours across 6 calendar days. Agent time: ~4
days of unattended work.

## 12. See also

- [backlog-structure.md](backlog-structure.md) — the structure the workflow operates on
- [skills-overview.md](skills-overview.md) — specific skill definitions
- [testing-guide.md](testing-guide.md) — what the integration-testing and e2e-testing
  agents know about
- [backend-code-layout-guide.md](backend-code-layout-guide.md),
  [frontend-code-layout-guide.md](frontend-code-layout-guide.md),
  [database-scripts-guide.md](database-scripts-guide.md) — project-shape
  guides the implementation agent consults
- [local-development-environment-guide.md](local-development-environment-guide.md) —
  operator first-time setup for the project itself
