---
name: backlog-grooming
description: Use this skill when asked to groom the backlog, epics or tasks.
---

# Backlog Grooming Guidelines

Always follow the [backlog structure guide](../../guides/backlog-structure.md) and use `/backlog-management` for any changes.

## Grooming the backlog
1. Switch to the backlog grooming mode
2. Thoroughly analyse the content of the backlog, including linked requirement documents.
3. Suggest the following categories of tasks:
   * **Duplicates:** Tasks, which appear to be duplicates of other tasks in the backlog
   * **Completed as a side effect:** Tasks, which look like they may have been completed
   * **Not relevant:** Tasks, which look like they are not relevant to the requirements any more
   * **Needs grooming:** Tasks, which are not clear enough to be implemented
4. Present these tasks to me for review
5. Follow the instructions on changes to the backlog based on the review and update the backlog accordingly during the process.
6. After every change is finished, present the list from step 3 again
7. Once the process is completed, prepare the commit with a message, wait for the approval
8. Commit and push the changes
9. Exit the backlog grooming mode

## Grooming an epic
1. Switch to the epic grooming mode
2. Thoroughly analyse and review the intent of the epic, including linked requirement documents and documentation of completed tasks.
3. Suggest changes in the following categories:
    * **Duplicates:** Tasks, which appear to be duplicates of other tasks in the epic
    * **Completed as a side effect:** Tasks, which look like they may have been completed
    * **Not relevant:** Tasks, which look like they are not relevant to the intentions of the epic any more
    * **Needs grooming:** Tasks, which are not clear enough to understand and plan for. For this category list the questions that need to be answered.
    * **Needs breaking down:** Tasks, which are too large to execute in one session and need to be split into smaller tasks.
4. Follow the instructions on changes to the backlog based on the review and update the backlog accordingly
5. After every change is finished, present the list from step 3 again
6. Once the process is completed, prepare the commit with a message, wait for the approval
7. Commit and push the changes
8. Exit the epic grooming mode

## General grooming instructions
1. Tag any clarification questions that need to be answered with an identifier, e.g. Q1, Q2, Q3, etc., so I can easily address them in my response.
2. Make changes to the item (task, epic) wording based on the answers
3. Re-review the matter at hand and look whether more clarifications are required. If so, repeat steps 1-3, until you have all the information you need.

## Testing tasks
Do not create standalone "write tests" tasks for functionality that can be tested as part of
the implementation task. Unit and integration tests are part of the standard task implementation
workflow (`/task-implementation` → `/integration-testing`) and should not be split out.

Only create a separate testing task when there is a genuine missing dependency — e.g. E2E tests
that require UI components not yet built, or integration tests that depend on a service that
has not been implemented yet.
