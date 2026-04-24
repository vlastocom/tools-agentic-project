---
name: task-planning
description: Use this skill to plan for the task you are asked to work on.
---

# Task Planning

Follow these steps to plan a task before implementation begins.

## Steps

1. **Explore the codebase** and identify what needs to be modified
    - Read relevant source files, tests and configuration
    - Understand existing patterns and conventions before proposing changes
2. **Check the requirements directory** (`docs/requirements/`) for requirements beyond the prompt
3. **Ask clarifying questions** if the ask is ambiguous — do not assume anything
4. **Plan the testing approach** following the [testing pyramid](../../guides/testing-guide.md#the-testing-pyramid):
    - 70% Unit tests — fast, isolated tests
    - 20% Integration tests — component interactions, Redux, routing
    - 10% E2E tests — critical user flows only
    - Document the required unit, integration and E2E tests in the plan
    - **Integration tests must be part of the implementation task** — do not defer them to
      a separate task unless a genuine dependency is missing (e.g. a required service or
      component has not been built yet). If the code being implemented can be integration-tested
      now, plan the tests now.
    - **E2E tests should be planned for any user flow that can be fully exercised with the
      components being built in this task.** Only defer E2E tests when they require UI
      components from other tasks that have not been built yet.
5. **Document the plan** in the task document at `docs/tasks/<taskID>.md` (e.g. `docs/tasks/NEST-00-0001.md`)
6. **Present the plan** and explicitly ask: *"Should I proceed with this implementation plan?"*
7. **Wait for explicit approval** (e.g. "yes", "approved", "proceed", "go ahead") before implementing
8. If **modifications are requested**, update the plan and ask for approval again
9. Update the backlog (use `/backlog-management`):
   - Set the task **Status** field to "TODO"
   - Update the **Documentation** field with a link to the task document using the format
     `[<taskID>.md](tasks/<taskID>.md)` (e.g. `[AUTH-04-0007.md](tasks/AUTH-04-0007.md)`)
10. Once approved, proceed with `/task-implementation`

## Notes

- For **small bug fixes** or **documentation-only changes**, a lightweight plan is sufficient — skip integration/E2E test planning if no new behaviour is added
- For **exploratory tasks** or **research**, create a lightweight plan with findings rather than full implementation steps
- Always ask if unsure whether a formal plan is needed

## References

- [Testing guide](../../guides/testing-guide.md)
- [Requirements directory](../../../docs/requirements/)
- Next step: `/task-implementation`
