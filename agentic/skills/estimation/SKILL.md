---
name: estimation
description: Estimate or re-estimate the approximate duration of a task, feature, epic or project implementation
---

Observe the [Backlog structure guide](../../guides/backlog-structure.md) for any work. 

# Estimation guidelines and principles

Use these principles to estimate for the backlog items (tasks, features, epics) and the project as a whole.

Use your own estimation methodology and enhance it with the following principles:

* Estimate items in **elapsed engineering days** (physical days we expect to complete the work)
* Where possible use your own internal data available to you (e.g. tokens spent on previous similar tasks, etc.)
* Where available, **use the historical data**: Extract Start date and End date of items from the backlog.
  These are actual recorded values from our previous work.
  Look for items of similar complexity and perceived size and use the consensus of those as a guideline.
* Large, complex items:
    * Break them down into smaller logical items for estimation (e.g. epic into tasks, large tasks into smaller subtasks)
    * Estimate each of them individually and add them up together to get the total estimate
* Estimation should assume the dependencies of the task have been all completed
  (i.e. task estimate should not include time spent on dependencies)
* The estimate should be **buffer**-free
* The result should be a number in elapsed engineering days, plus a confidence level (high, medium, low)
  expressing your confidence in the estimate, e.g. based on the amount of data available.
* Be as accurate as possible, but don't agonise over the accuracy.
  The estimation is a guideline for project sizing, not a commitment.

# Estimating / re-estimating backlog items

* When asked to estimate or re-estimate a backlog item, ALWAYS record the new estimate in the backlog
  * If the backlog item is a task, update the `Estimated duration` field in the `Tasks` section
  * If the backlog item is a sprint, update the `Estimated duration` field in the `Sprints` section
* If you re-estimate a task, update the estimated duration of any applicable sprint as well
* Do these changes automatically, no need to ask for an approval

# References
* [The backlog](../../../docs/backlog.md)
* [Backlog structure guide](../../guides/backlog-structure.md)
* Skills to maintain the backlog:
  * /backlog-management
  * /backlog-validation
* Skills to manage MD files (including the backlog):
  * /md-file-editing
* Sprint changes:
  * /sprint-management
