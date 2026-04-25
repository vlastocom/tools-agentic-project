---
name: task-wrapup
description: Use this skill to manually run the task-wrapper subagent to finalise a single task. Escape hatch around the `/sprint-implementation` per-task pipeline. Renames the task doc to `.complete.md`, updates the backlog, and gates on review dispositions.
---

# /task-wrapup

Manually invoke the `task-wrapper` subagent to finalise a single task.

This is an **escape hatch**. Under the SDLC workflow (see
[sdlc-workflow-guide.md §5.2](../../guides/sdlc-workflow-guide.md#52-sprint-implementation--unattended-orchestrator)
and [§5.4.3](../../guides/sdlc-workflow-guide.md#543-disposition-rules)),
wrap-up normally runs as the final step of the per-task pipeline
inside `/sprint-implementation`, after a passing review. Use this
skill when you want to:

- Wrap up a task that was reviewed clean out of band.
- Re-attempt wrap-up after the previous attempt returned `NOT READY`
  (because should-fix or consider items were left undone without a
  rationale in `## Deviations`).
- Test the task-wrapper subagent in isolation.

## Pre-flight

1. Identify the `<TASK-ID>`. Confirm:
   - `docs/tasks/<TASK-ID>.md` exists with a `## Review notes` block
     and verdict `PASS` (no outstanding must-fix items).
   - All tests are green for this task (unit / integration / E2E as
     applicable).
   - `agentic/agents/task-wrapper.md` exists.
   - `scripts/setup-worktree.sh` exists in the project root.

## Invocation

```
Agent(
    subagent_type: "task-wrapper",
    isolation: "worktree",
    prompt: "Before any other work, run `bash scripts/setup-worktree.sh`.
             If it errors or doesn't exist, stop. Then wrap up task
             <TASK-ID> per the rules in agentic/agents/task-wrapper.md.
             Gate on every should-fix and consider item in
             `## Review notes` being either fixed or rationalised in
             `## Deviations` per SDLC §5.4.3. If gating fails, return
             NOT READY with the specific items listed."
)
```

## On return

- **Clean** — the wrapper has:
  - Renamed `docs/tasks/<TASK-ID>.md` → `docs/tasks/<TASK-ID>.complete.md`.
  - Filled in `## Wrap-up → Delivered` summary.
  - Updated the backlog row's Status to `DONE` and End date to today
    (UTC).
  - Updated the `Documentation` field to point to the new
    `.complete.md` filename.
  - Run pre-commit checks (lint, type-check, test runs as applicable).

  Next: surface to operator (or hand back to `/sprint-implementation`
  to move on to the next task).

- **NOT READY** — should-fix or consider items remain unaddressed and
  not rationalised. Route back to `/task-implementation` with the
  outstanding list, then re-invoke `/code-reviewing`, then re-invoke
  this skill.

- **BLOCKED** — environment problem (lint/type/test failure that the
  wrapper cannot resolve) or open question. Surface to operator,
  resolve, re-invoke.

## Reminders the task-wrapper subagent enforces

The agent definition is the authoritative spec; this is a quick
reminder of what it is contractually held to:

- **Disposition gating** — every should-fix and consider must be
  fixed or have a rationale in `## Deviations`. Empty rationale =
  NOT READY.
- **Rename, do not copy** the task doc to `.complete.md`. Move git
  history with the rename.
- **Backlog row update is part of wrap-up**, not a separate step.
- **No commit, no push.** Commits happen at sprint review (per
  [SDLC §5.5](../../guides/sdlc-workflow-guide.md#55-sprint-review--interactive-main-conversation));
  out-of-band wrap-ups commit when the operator says so.
- **Stop and ask** on the five triggers per [SDLC §7](../../guides/sdlc-workflow-guide.md#7-stop-and-ask-contract-detailed).

## See also

- [SDLC workflow guide §5.4.3 — disposition rules](../../guides/sdlc-workflow-guide.md#543-disposition-rules)
- [SDLC workflow guide §5.5 — sprint review (commit/push happens here)](../../guides/sdlc-workflow-guide.md#55-sprint-review--interactive-main-conversation)
- Subagent definition: `agentic/agents/task-wrapper.md`
- Previous step: `/code-reviewing`
- Next step: hand back to `/sprint-implementation`, or wait for
  `/sprint-review` to commit.
