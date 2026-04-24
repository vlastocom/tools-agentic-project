---
name: sprint-start
description: Use this skill to start a new sprint.
---

# Instructions for starting a new sprint

Follow the following steps to update the sprint section of [the backlog](../../../docs/backlog.md):

1. If there is currently an open sprint (status=OPEN), refuse to start a new one
2. Clarify the sprint to be started
    * Look for the sprint, which is still in PLANNING state. If there are more of those, pick the oldest one.
    * Display the fields in the sprint as documented:
        * ID
        * Main goal
        * Additional goals
        * Success criteria
        * Estimated duration
        * Table of tasks which are in this sprint
            * Task ID
            * Task type
            * Priority
            * Short name
3. Once confirmed, make the backlog changes:
   * Set Sprint Status to `OPEN`
   * Set the Sprint Start date to today's date (YYYY-MM-DD)
4. Present the changes made for the approval
5. Fix any issues that may arise and present the change again for approval. Repeat until the change is approved
6. Upon approval, validate the backlog structure and consistency (/backlog-validation), then commit and push the backlog changes

# References

* [The backlog](../../../docs/backlog.md)
* [Backlog structure guide](../../guides/backlog-structure.md)
* Skills to maintain the backlog:
    * /backlog-management
    * /backlog-validation
* Skills to manage MD files (including the backlog):
    * /md-file-editing
