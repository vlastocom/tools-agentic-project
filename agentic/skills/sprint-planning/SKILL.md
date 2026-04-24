---
name: sprint-planning
description: Use this skill to plan new sprints
---

# Sprint planning instructions

Follow the exact steps for planning a new sprint:

1. Clarify the goals for the sprint with me. There will be a main goal and possibly additional goals of lower priority.
2. Identify the `key tasks` in the backlog across all areas and epics, which need to be completed to achieve the sprint goals.
3. Add all tasks, which the `key tasks` depend on. Continue recursively, adding dependencies of dependencies, etc.
4. Identify `gaps`, i.e. tasks, which do not exist yet, but are required to achieve the sprint goals.
5. Present the sprint plan to me in the following format for approval:
    * **Sprint ID:** Will be today's date in YYYY-MM-DD format
    * **Status:** Will be set to `PLANNING` at this stage
    * **Sprint goals:** List of sprint goals with the main goal of the sprint highlighted.
    * **Success criteria:** A list of criteria. Try to generate them from the sprint goals and refine with me.
    * **Estimated sprint duration:** Your __estimate__ of the sprint duration, based on our previous progress.
        * Where the individual tasks do not have an estimated duration yet, estimate those first (and update in the backlog)
        * Use /estimation skill to estimate the duration of a task and the sprint duration
    * **Sprint backlog:** A list of selected sprint tasks, which should be completed in the sprint
        * Report tasks in the tabular format with the following columns:
            * ID
            * Type
            * Priority
            * Short name
            * Estimated time to complete the task (estimate based on previous task durations or perceived complexity)
        * Group tasks in the following groups: 
            * The tasks which achieve the main sprint goal, plus their dependencies
            * For each additional goal, the tasks and their dependencies, which achieve that goal
6. Refine the content with me, e.g. add or remove tasks, change success criteria or sprint goals. 
    * When updating the content of the sprint:
        * Consider and highlight any changes in the sprint goals and success criteria
        * Re-estimate the sprint duration
    * After such operations, present the result again for approval 
7. When the plan is approved, update the backlog:
    * Unless it exists, create a new sprint section
        * Follow [backlog structure guide](../../guides/backlog-structure.md) for structure of the fields recorded
    * In the `Tasks` section, update every selected task of the sprint by setting the sprint ID to the `Sprint` column 
8. Once you make the changes in the backlog file, wait for the approval and process any additional requests, always coming back for the approval.
9. Upon approval, validate the backlog structure and consistency (/backlog-validation), then commit and push the backlog changes

# See also

1. Starting a sprint: Use /sprint-start skill
2. Closing the sprint: Use /sprint-close skill
3. Adding and removing tasks from the sprint: Use /sprint-management skill

# References
* [The backlog](../../../docs/backlog.md)
* [Backlog structure guide](../../guides/backlog-structure.md)
* Skills to maintain the backlog:
    * /backlog-management
    * /backlog-validation
* Skills to manage MD files (including the backlog):
    * /md-file-editing
* Skills to manage sprints:
    * /sprint-start
    * /sprint-close
    * /sprint-management
