---
name: task-implementation
description: Use this skill when implementing a planned task — writing code, running unit tests and reviewing test coverage.
---

# Task Implementation

Follow these steps to implement a task after the plan has been approved.

## Prerequisites

- An approved plan exists in `docs/tasks/<taskID>.md` (created by `/task-planning`)
- Mark the task as DOING and set the start date (`/backlog-management`)

## Steps

1. **Backlog management:** When starting to work on a task, update the backlog first:
   - Update the task status to **DOING**
   - Update the task **Start date** field in Task Details to the current date (YYYY-MM-DD)
2. **Implement the code** exactly as described in the approved plan
   - Follow the coding styles and conventions as set up in IntelliJ IDEA
   - **Java `final` keyword:** Use `final` for all local variables and method parameters that are never reassigned — this applies to both production code and test code
   - **Java explicit types — no `var`:** In Java code, always declare local variables with their explicit type (e.g. `final Set<UserAccountRole> roles = ...`), never with `var`. The inferred type is easy to misread in diff reviews. This applies to both production and test code.
   - **Java imports vs FQCNs:** Always reference classes via an `import` rather than a fully-qualified class name in the body of the file. The only exception is genuine name disambiguation (e.g. when two classes with the same simple name are needed in the same file). This applies to both production and test code, including nested types (`import com.foo.Outer.Inner;`).
   - **Java import ordering and grouping:** Match IntelliJ IDEA's default Java import layout so that re-running *Optimize Imports* produces no diff. Group imports in the order:
     (1) `java.*` / `javax.*` / `jakarta.*`, (2) all other non-static imports, (3) static imports — separated by blank lines. Within each group, sort alphabetically by the fully-qualified name. Prefer explicit imports over wildcard (`import com.foo.Bar;` rather than `import com.foo.*;`) unless the file already uses a wildcard for that package.
   - Follow the [UI design guide](../../../docs/guides/ui-design-guide.md) for frontend changes
   - Follow the [Apollo Client usage guide](../../../docs/guides/apollo-client-usage.md) for GraphQL integration
   - Follow the [audit implementation guide](../../../docs/guides/audit-implementation-guide.md) for audit-related changes
3. **Discuss deviations** — if the approach needs to change:
   - Discuss with the user and provide code suggestions before implementing
   - Explain the concepts behind the suggestion
   - Update the plan document automatically to reflect any agreed changes
4. **Write unit tests** as you go — use `/unit-testing` for detailed guidelines
5. **Review existing tests** — when you touch any source file, always review the tests for that module:
   - Check for completeness, good practice and overlaps
   - Make changes as needed — aim for the simplest but most comprehensive set of tests
6. **Boy Scout Rule** — leave the campsite better than you found it. If you detect any technical
   debt which is small and fixable without heavy reengineering in the files/code you are changing,
   fix it immediately **in the whole file**: rename misleading or ambiguous variables/methods to
   improve quality, optimise imports, refactor code duplications, update/remove outdated comments,
   etc. — make the code cleaner than you found it. If a larger change is required, create a new
   task in an appropriate epic of the CLEANUP area instead.
7. **Run unit tests**, report results including changes in test coverage
8. **Never ignore test signals** — this is the strongest rule in the workflow. Every signal from
   a test run is evidence, not background noise:
   - Test failures, test timeouts, and Vitest's `Errors N error(s)` lines must be root-caused.
     "Flaky" is not an explanation — read the stack trace and form a concrete hypothesis about
     what causes the failure before re-running.
   - `stderr` warnings (Apollo `No more mocked responses` / `Missing field` / `Unknown query
     in refetchQueries`, React `act()` warnings, jsdom `Not implemented` errors) are also
     signals. Treat them as failures-in-waiting. Each one hides a future regression.
   - After root-causing, choose one: (a) fix in scope if small; (b) file a backlog task in
     CLEANUP-01 with the root cause, affected files and acceptance criteria; (c) explicitly
     defer with justification. Never "dismiss" as pre-existing without a pointer.
   - A signal that looks identical to a pre-existing one may be a new regression you
     introduced. Always verify which before waving past it.
9. **Pause for review** — once the implementation is complete, let the user review and approve the code before continuing to integration testing

## Error handling and debugging

When encountering errors:
- Read error messages carefully and diagnose the root cause
- Check recent changes that might have introduced the issue

When fixing bugs:
- Identify the root cause before implementing a fix
- **First reproduce the bug with a failing test** — this confirms the bug exists and prevents regression
- Only after seeing the test fail, implement the fix
- Verify the test now passes
- Document the issue and fix in commit messages

## References

- [Testing guide](../../guides/testing-guide.md)
- [UI design guide](../../../docs/guides/ui-design-guide.md)
- [Apollo Client usage guide](../../../docs/guides/apollo-client-usage.md)
- [Audit implementation guide](../../../docs/guides/audit-implementation-guide.md)
- Previous step: `/task-planning`
- Testing: `/unit-testing`, `/integration-testing`, `/e2e-testing`
- Next step: `/task-wrapup`
