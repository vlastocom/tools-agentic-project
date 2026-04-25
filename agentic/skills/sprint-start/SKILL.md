---
name: sprint-start
description: Manual override to flip a PLANNING sprint to OPEN. Subsumed by `/sprint-planning` Phase 4 — use this only when you need to set OPEN by hand (e.g. PLANNING sprint that pre-existed the new workflow).
---

# /sprint-start

> **Manual override.** Under the SDLC workflow (see
> [sdlc-workflow-guide.md §5.1](../../guides/sdlc-workflow-guide.md#51-sprint-planning--interactive-main-conversation)),
> sprints are taken from PLANNING to OPEN automatically by Phase 4 of
> `/sprint-planning`, after grooming and planning subagents have run
> and the operator has accepted the plans. Use this skill only when
> you need to flip the status by hand — e.g. a sprint that pre-existed
> the new workflow, or when recovering from an aborted run.

Follow these steps to update the sprint section of [the backlog](../../../docs/backlog.md):

1. If a sprint is currently `OPEN`, refuse to start a new one. (Close
   it via `/sprint-review` first.)
2. Identify the sprint to start:
   - Look for the sprint in `PLANNING` state. If multiple, pick the
     oldest.
   - Display its fields per [backlog-structure.md](../../guides/backlog-structure.md):
     ID, Main goal, Additional goals, Success criteria, Estimated
     duration, and the table of tasks (ID, type, priority, short name).
3. Once the operator confirms, update the backlog:
   - Set the sprint's `Status` to `OPEN`.
   - Set the sprint's `Start date` to today (UTC, `YYYY-MM-DD`).
4. Present the change for approval. Iterate until approved.
5. Validate the backlog (`/backlog-validation`).
6. Commit and push the backlog change.

## See also

- [SDLC workflow guide §5.1 — sprint planning](../../guides/sdlc-workflow-guide.md#51-sprint-planning--interactive-main-conversation)
- Normal flow: `/sprint-planning` (replaces this skill end-to-end)
- [Backlog structure guide](../../guides/backlog-structure.md)
- Related: `/backlog-management`, `/backlog-validation`,
  `/md-file-editing`
