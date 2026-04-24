---
name: backlog-review
description: Use this skill when asked to 'show the top of the backlog' or 'show the backlog'
---

Present the **prioritised** table of tasks:

* Skip the tasks which are in the DROP or DONE status
* Show columns:
    * ID
    * Priority
    * Sprint
    * Status
    * Short name
* Order the list by using COMPOSITE KEY made of the following criteria in this hierarchical order:
    * Sprint ID: ascending (+ the tasks with the sprint field not set are placed after the tasks assigned to a sprint)
    * Status: In the following order: DOING, GROOM, TODO
    * Priority: descending (+ the tasks with the priority field not set are placed at the end)
    * ID: ascending
* Limit the output to:
    * The tasks which are assigned to a sprint
    * Append 20 top tasks with no sprint assigned.
* If there is no active task being worked on (DOING state), suggest which of the tasks we should work on next.
