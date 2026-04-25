---
name: sprint-review
description: Use this skill to batch-review a completed sprint. Walks through each .complete.md, the coverage summary with deltas, the E2E flows, and the aggregated decisions/deviations. Supports a rework path for tasks the operator critiques. Closes the sprint, commits, and pushes on accept.
---

# Sprint review

You are running the **review phase** of a closed-implementation sprint
per [SDLC workflow guide §5.5](../../guides/sdlc-workflow-guide.md#55-sprint-review--interactive-main-conversation).
This skill is interactive — the operator audits the batch of work the
orchestrator produced.

## Pre-flight

Refuse to start unless:

1. There is exactly one sprint in `OPEN` status in `docs/backlog.md`.
2. Every task in the sprint is in `DONE`, `DROP`, or marked
   `Failed-out` in the sprint log. (No tasks in `TODO`/`DOING`/`GROOM`.)
3. `docs/sprints/<sprint-id>.coverage.md` exists. (Produced by
   `/sprint-implementation` at termination.)
4. `docs/sprints/<sprint-id>.md` (the sprint log) exists.

If any check fails, report the specific failure. The most common is
"orchestrator hasn't finished yet" — point at `/sprint-implementation`.

## Review walk-through

### Step 1 — Sprint goal attainment

Read the sprint definition in `docs/backlog.md` and compare against
the Completed list in `docs/sprints/<sprint-id>.md`. Summarise to the
operator: was the main goal achieved? Each additional goal? Any
goal-relevant work failed-out?

### Step 2 — Task-by-task

For each `.complete.md` in `docs/tasks/` that was wrapped this sprint
(use the Completed list from the sprint log to enumerate), present a
short summary:

- **Delivered** — from the task's `## Wrap-up → Delivered`
- **Decisions** — bullet list from `## Decisions`
- **Deviations** — bullet list from `## Deviations`

Operator skims or asks for the full task doc. At each task the
operator may **direct rework** — see Step 4 below.

### Step 3 — Coverage and runtime review

Read `docs/sprints/<sprint-id>.coverage.md` aloud (i.e. surface its
content to the operator):

- **Coverage** table with deltas — flag any negative delta in red
- **E2E** — list specs that ran, with durations from the runtime
  block; flag any flake or timing surprise
- **Test runtime** — read every threshold trip flagged in the
  block. **Each trip needs explicit operator disposition**:
  - **Accept** — log in the sprint log's Decision log: "Accepted
    runtime trip on `<suite>`: `<reason>`. Baseline rolls forward."
  - **Rework** — direct rework on the offending task per Step 4

### Step 4 — Rework path (per-task or per-trip)

When the operator critiques a wrapped task or accepts that a runtime
trip needs fixing:

1. Identify `<original-id>`. Confirm with the operator.
2. Create a new rework task in `docs/backlog.md` using
   `/backlog-management`:
   - ID: next sequence in the same epic
     (`<original-area>-<original-epic>-<next-seq>`)
   - Short Name: "Rework of `<original-id>` — `<reason>`"
   - Type: matches the original (or `TECHNICAL` for runtime fixes)
   - Status: `GROOM` initially
3. Add a **`depends_on` link** from the rework task to `<original-id>`
   in the `TaskDependencies`-equivalent section of the backlog.
4. Capture the operator's critique notes in the rework task's detail
   block — these become the seed for `task-groomer` / `task-planner`
   when the task is picked up.
5. Operator chooses scheduling:
   - **Run in this sprint** — Add the rework task to the current
     OPEN sprint via `/sprint-management`. Hand control back to
     `/sprint-implementation` to pick it up. The current
     `/sprint-review` pauses; resume here when the rework is wrapped.
   - **Roll to next sprint** — Add to a `PLANNING` sprint candidate
     list (or note it for the operator's next `/sprint-planning`
     invocation).
6. Append the rework task's row to the sprint log's
   `## Tasks reworked` section with the link to the original.

### Step 5 — Failed-out tasks

For each task in the sprint log's `Failed-out:` list, the operator
chooses:

- **Drop** — set the original task's Status to `DROP` in the backlog.
- **Roll forward** — keep at `TODO`, will be candidates next sprint.
- **Break smaller** — operator drafts smaller follow-up tasks (use
  `/backlog-management`). The original goes to `DROP` or stays `TODO`
  depending on whether the smaller tasks fully replace it.

### Step 6 — Final disposition

Once the operator says "accept the sprint":

1. Set the sprint's Status from `OPEN` to `CLOSED` in
   `docs/backlog.md`. Set End date to today (UTC).
2. Append a final summary entry to the sprint log's Decision log:
   "Sprint closed at `<UTC ISO>` after operator review."
3. Validate the backlog (`/backlog-validation`).
4. Propose a git commit message summarising the sprint (delivered
   tasks, key decisions, any rework introduced). Operator edits or
   accepts.
5. Commit with the agreed message.
6. Push (unless the operator prefers to push manually).
7. Prompt: "Start the next sprint? Run `/sprint-planning` if yes."

## What you do not do

- You do **not** modify task plans or implementations during review.
  If a task needs work, that's the rework path (Step 4).
- You do **not** invent rework tasks without operator direction. Every
  rework is operator-initiated.
- You do **not** delete or unwind any `.complete.md`. History stays;
  rework supersedes.

## See also

- [SDLC workflow guide §5.5 — sprint review](../../guides/sdlc-workflow-guide.md#55-sprint-review--interactive-main-conversation)
- [SDLC workflow guide §3.4 — sprint coverage summary](../../guides/sdlc-workflow-guide.md#34-sprint-coverage-summary)
- [SDLC workflow guide §3.6 — test runtime monitoring](../../guides/sdlc-workflow-guide.md#36-test-runtime-monitoring)
- Manual override: `/sprint-close` (force-close by hand if needed —
  bypasses Steps 4 and 5)
- Mid-sprint task adds/removes: `/sprint-management`
- Previous step: `/sprint-implementation`
- Next step: `/sprint-planning` (start the next sprint)
