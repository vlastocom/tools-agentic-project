---
name: sprint-close
description: Manual override to flip an OPEN sprint to CLOSED. Subsumed by `/sprint-review` Step 6 — use this only when you need to close a sprint by hand without the full review walk-through.
---

# /sprint-close

> **Manual override.** Under the SDLC workflow (see
> [sdlc-workflow-guide.md §5.5](../../guides/sdlc-workflow-guide.md#55-sprint-review--interactive-main-conversation)),
> sprints are taken from OPEN to CLOSED by Step 6 of `/sprint-review`,
> after the operator has walked through every wrapped task, the
> coverage summary and runtime block, and any rework path. Use this
> skill only when you need to flip the status by hand — e.g. a sprint
> from before the new workflow, or recovering from a failed run.
>
> **Bypasses** the rework path (Step 4) and failed-out disposition
> (Step 5) of `/sprint-review`. Anything you skip you take on yourself
> to handle.

Follow these steps to update the sprint section of [the backlog](../../../docs/backlog.md):

1. Identify the sprint currently in `OPEN`. If none, refuse.
2. Confirm the sprint is closable:
   - Every task in the sprint has Status `DONE` or `DROP`. (Tasks in
     `TODO`, `DOING`, or `GROOM` block closure — surface them and
     suggest `/sprint-management` to move them out.)
   - The sprint's success criteria are met (or you have explicit
     operator direction to close anyway).
3. If not closable, report the blockers and stop. Do not close.
4. Update the backlog:
   - Set the sprint's `Status` to `CLOSED`.
   - Set the sprint's `End date` to today (UTC, `YYYY-MM-DD`).
5. Present the change for approval. Iterate until approved.
6. Validate the backlog (`/backlog-validation`).
7. Commit and push the backlog change.

## See also

- [SDLC workflow guide §5.5 — sprint review](../../guides/sdlc-workflow-guide.md#55-sprint-review--interactive-main-conversation)
- Normal flow: `/sprint-review` (replaces this skill end-to-end and
  also handles rework + commit/push)
- [Backlog structure guide](../../guides/backlog-structure.md)
- Related: `/sprint-management`, `/backlog-management`,
  `/backlog-validation`, `/md-file-editing`
