---
name: e2e-testing
description: Use this skill when writing or running end-to-end (Playwright) tests after integration tests are approved.
---

# End-to-End Testing

E2E tests form the top of the [testing pyramid](../../guides/testing-guide.md#the-testing-pyramid) (10% of all tests).
Only test critical user flows — keep the count minimal.

## Steps

1. **Review the plan** — check the E2E tests documented in the task plan and verify they are still current with the implementation
2. **Implement the tests** following the guidelines below
3. **Run the tests** and ensure they pass
4. **Pause for review** — let the user review and approve the E2E tests before continuing

## Guidelines

- Use [Playwright](https://playwright.dev/) with TypeScript
- Test files go in `nest-ui/e2e/` organised by feature area
- Test only critical user-visible workflows — login, navigation, key form submissions
- Use page object patterns where the test touches multiple pages
- Prefer `getByRole`, `getByText` and `getByTestId` selectors over CSS selectors
- Keep tests independent — each test should set up its own state and not depend on other tests
- Use realistic test data from the E2E database scripts (`database/dev/e2e/`)

### Assertions

- **Prefer persistent side effects over transient UI elements.** Verify that a mutation
  succeeded by checking durable state changes (data appearing in a table, form resetting, button
  becoming disabled) rather than transient elements like Snackbars or toasts. Transient elements
  auto-hide and create flaky timing issues.
- **Scope locators to the relevant container** when background and foreground share similar text.
  For example, use `dialog.getByText(...)` instead of `page.getByText(...)` when a dialog
  overlays a grid that has matching column headers.

### Data mutations

- **Handle leftover state from previous failed runs.** Tests that mutate data should check for
  stale state at the start and clean it up before proceeding, rather than assuming the database
  is pristine. This prevents cascading failures when a previous run failed mid-test.

### MUI and React specifics

- **Playwright's `fill()` can fail on React controlled MUI TextFields** after component
  re-renders (e.g. after an Apollo refetch resets form state). Use click + select-all + keyboard
  typing instead:
  ```typescript
  async function fillTextField(page: Page, locator: Locator, value: string) {
      await locator.click()
      await page.keyboard.press('Control+a')
      await page.keyboard.type(value)
  }
  ```

## Running tests

```bash
# All E2E tests
npx playwright test --config=nest-ui/playwright.config.ts

# Single test file
npx playwright test nest-ui/e2e/auth/login.spec.ts

# With UI mode for debugging
npx playwright test --ui
```

## When to skip E2E tests

- Pure backend changes with no UI impact
- Refactoring that does not change user-visible behaviour
- Documentation-only changes

## References

- [Testing guide](../../guides/testing-guide.md)
- [Playwright documentation](https://playwright.dev/docs/intro)
- [E2E test data scripts](../../../database/dev/e2e)
- Parent workflow: `/task-implementation`
- Related: `/unit-testing`, `/integration-testing`
