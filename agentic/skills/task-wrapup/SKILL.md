---
name: task-wrapup
description: Use this skill to finalise a completed task — update documentation, backlog and commit.
---

# Task Wrap-up

Follow these steps after implementation and testing are complete and approved.

## Step 1: Documentation

1. **Check project documentation** — review all relevant `*.md` files and ensure they are up to date with the changes
2. **Consider new documentation** — if new guides or README files are needed, ask for confirmation before creating them
3. **Update the task document** and rename it from `docs/tasks/<taskID>.md` to `<taskID>.complete.md`
4. **Update the backlog** - use `/backlog-management`
   - Update the task status to **DONE**
   - Update the **End date** field in Task Details to the current date (YYYY-MM-DD)
   - Update the link to the task document in the **Documentation** field to reflect the new file name

## Step 2: Pre-commit checks

1. Run all relevant tests:
   - Unit tests (`npx vitest run` / `./gradlew test`)
   - Integration tests (`./gradlew integrationTest`) if applicable
   - E2E tests (`npx playwright test`) if applicable
2. Ensure TypeScript compilation succeeds with no errors: `npx tsc --noEmit`
3. Run the linter: `npm run lint`
4. Validate the backlog: `/backlog-validation`
5. Check spelling and grammar in any modified `.md` files

## Step 3: Commit

1. **Present all changes** to the user and **wait for explicit approval** before committing
2. Use descriptive commit messages:
   - First line: brief summary in imperative mood (50-72 characters)
   - Body: detailed explanation of what and why (not how)
   - Include the task ID reference (e.g. `AUTH-02-0016`)
3. Commits should be atomic — one logical change per commit
4. **Never commit without explicit approval**

## References

- [Spelling and grammar rules](../../guides/spelling-and-grammar-rules.md)
- Backlog updates: `/backlog-management`
- Backlog validation: `/backlog-validation`
- Markdown editing: `/md-file-editing`
