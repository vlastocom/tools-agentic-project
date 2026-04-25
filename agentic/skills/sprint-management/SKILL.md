---
name: sprint-management
description: Use this skill to add or remove tasks from an existing sprint mid-flight. Useful for scope change, rework tasks added during `/sprint-review`, or pulling tasks out that should not have been included.
---

> **Where this fits in the SDLC workflow.** Sprint scope is normally
> set during `/sprint-planning` (Phases 1–3) and is not expected to
> change once the sprint is `OPEN`. The two legitimate mid-flight
> changes this skill handles:
>
> - **Adding a rework task** during `/sprint-review` Step 4 (operator
>   directs rework on a wrapped task; the rework task lands here for
>   inclusion in the current sprint or a follow-up).
> - **Removing or replacing a task** that turns out wrong-shaped after
>   the sprint opened — the operator decides; this skill executes the
>   backlog edits.
>
> See [SDLC workflow guide §5.5](../../guides/sdlc-workflow-guide.md#55-sprint-review--interactive-main-conversation)
> for the rework path.

# Instructions for adding new tasks to a sprint

Follow these steps strictly to add new tasks to a sprint:

1. Identify the target sprint:
    * Extract it from the prompt
    * If not present, default to the currently OPEN sprint
    * If no sprint is OPEN, use the most recent PLANNING sprint
    * If neither of these exist, refuse to continue
2. Clarify the set of tasks to add to the sprint
    * Identify the tasks, which are the dependencies of the requested set of tasks and add them to the changeset
      (Rationale: We cannot complete the requested tasks without completing the dependencies)
        * Work recursively, identify the dependencies of the dependencies, etc., until you have the full set of tasks to add to the sprint
3. Present the change for approval or refinement
    * List tasks in a tabular form (columns: ID, type, priority, short name, status, estimated duration)
    * Evaluate and highlight changes to the fields of the sprint:
        * Main goal
        * Additional goals
        * Success criteria
        * Estimated duration (you may need to estimate the duration of the new tasks and update the backlog first)
4. Process any refinement requests, i.e.
    * Process any refinement feedback
    * Present the updated change
    * Continue refining this until the change is approved
5. Once the change is approved, make backlog changes:
    * For each task in the changeset, set the `Sprint` field to the current sprint ID in the `Tasks` section
    * Update the sprint fields in the `Sprints` section accordingly, recording new field values (Main goal, Additional goals, Success criteria, Estimated duration)
6. Once the change is made, let me review it
7. Process any refinement feedback I have and wait for my approval
8. Once approved, commit and push the backlog changes

# Instructions for removing tasks from a sprint

Follow these steps strictly to remove tasks from a sprint:

1. Identify the target sprint:
    * Extract it from the prompt
    * If not present, default to the currently OPEN sprint
    * If no sprint is OPEN, use the most recent PLANNING sprint
    * If neither of these exist, refuse to continue
2. Clarify the set of tasks to remove from the sprint
    * Identify the tasks, which are dependent on the set of tasks requested to be removed and add them to the changeset
      (Rationale: if we do not complete the requested tasks, the tasks dependent on them cannot be completed either)
        * Work recursively, identify the dependants of the dependants, etc., until you have the full set of tasks to remove from the sprint
3. Present the change for approval or refinement
    * List tasks in a tabular form (columns: ID, type, priority, short name, status, estimated duration)
    * Evaluate and highlight changes to the fields of the sprint:
        * Main goal
        * Additional goals
        * Success criteria
        * Estimated duration (re-estimate the duration of these tasks and update the backlog first)
4. Process any refinement requests, i.e.
    * Process any refinement feedback
    * Present the updated change
    * Continue refining this until the change is approved
5. Once the change is approved, make backlog changes:
    * For each task in the changeset, clear the `Sprint` field in the `Tasks` section
    * Update the sprint fields in the `Sprints` section accordingly, recording new field values (Main goal, Additional goals, Success criteria, Estimated duration)
6. Once the change is made, let me review it
7. Process any refinement feedback I have and wait for my approval
8. Upon approval, validate the backlog structure and consistency (/backlog-validation), then commit and push the backlog changes

# References
* [SDLC workflow guide §5.5 — sprint review and rework path](../../guides/sdlc-workflow-guide.md#55-sprint-review--interactive-main-conversation)
* [The backlog](../../../docs/backlog.md)
* [Backlog structure guide](../../guides/backlog-structure.md)
* Skills to maintain the backlog:
    * /backlog-management
    * /backlog-validation
* Skills to manage MD files (including the backlog):
    * /md-file-editing
* Sprint orchestration skills:
    * /sprint-planning (sets initial scope; OPEN at end of Phase 4)
    * /sprint-implementation (unattended orchestrator)
    * /sprint-review (rework path lives here)
* Manual overrides (use only when the orchestration skills do not fit):
    * /sprint-start (flip PLANNING → OPEN by hand)
    * /sprint-close (flip OPEN → CLOSED by hand)
