---
name: sprint-close
description: Use this skill to close an open sprint.
---

# Instructions for closing an open sprint

Follow the following steps to update the sprint section of [the backlog](../../../docs/backlog.md):

1. Identify which sprint is currently in the OPEN state
2. Check the sprint is ready to be closed. To be ready, it must meet the following criteria:
    *  All tasks, which are part of this sprint, must have the state of DONE or DROP
        * If there are tasks in other states, the sprint MUST NOT be closed.
            * Report these as a reason to refuse to close the sprint
            * Suggest moving these out of the sprint using the `/sprint-management` skill.
    *  Evaluate if the tasks which are DONE have achieved the sprint success criteria
3. If the sprint is not ready, report any issues with the previous check and DO NOT CLOSE THE SPRINT.
   Wait for further instructions.
4. If the sprint is ready to be closed, make the backlog changes:
    * Set Sprint Status to `CLOSED`
    * Set the Sprint `End date` to today's date (YYYY-MM-DD)
5. Present the changes made for the approval
6. Fix any issues that may arise and present the change again for approval. Repeat until the change is approved
7. Upon approval, validate the backlog structure and consistency (/backlog-validation), then commit and push the backlog changes 

# References

* [The backlog](../../../docs/backlog.md)
* [Backlog structure guide](../../guides/backlog-structure.md)
* Skills to maintain the backlog:
    * /backlog-management
    * /backlog-validation
* Skills to manage MD files (including the backlog):
    * /md-file-editing
