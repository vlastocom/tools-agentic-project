---
name: integration-testing
description: Use this skill when writing or running integration tests after the implementation is approved.
---

# Integration Testing

Integration tests form the middle layer of the [testing pyramid](../../guides/testing-guide.md#the-testing-pyramid) (20% of all tests).
They verify component interactions, data flow and API contracts.

## Steps

1. **Review the plan** — check the integration tests documented in the task plan and verify they are still current with the implementation
2. **Implement the tests** following the guidelines below
3. **Run the tests** and ensure they pass
4. **Run the full integration test suite** to check for regressions and side effects
5. **Never ignore failed tests** — the repository is always assumed to be in a clean state. If
   any test fails, even one that appears unrelated to the current work, investigate it. A failure
   outside your scope most likely indicates a test side effect or contamination introduced by your
   changes. Diagnose and fix it before proceeding.
6. **Debug issues** as needed — investigate root causes rather than working around failures
7. **Pause for review** — let the user review and approve the integration tests before continuing

## Frontend integration tests (Vitest)

Follow the [frontend testing guide](../../guides/testing-guide.md).

- Test component interactions with Redux store, React Router and Apollo Client together
- Use `MockedProvider` with realistic GraphQL responses
- Test navigation flows and route guards
- Test form submission flows end to end within the component tree

## Backend integration tests (Spring Boot)

- Test files go in `src/integration-test/java/` (separate source set)
- Use `@SpringBootTest` with a test database
- Test GraphQL queries and mutations through the DGS framework test utilities
- Test service-to-repository integration with actual database queries
- See [test database setup](../../../src/integration-test/java/com/vlasto/finance/nest/testutil/README.md) for configuration

## Running tests

```bash
# Frontend integration tests (same runner, different scope)
npx vitest run src/path/to/file.integration.test.tsx

# Backend integration tests
./gradlew integrationTest
```

## References

- [Testing guide](../../guides/testing-guide.md)
- [Test utilities README](../../../src/integration-test/java/com/vlasto/finance/nest/testutil/README.md)
- Parent workflow: `/task-implementation`
- Related: `/unit-testing`, `/e2e-testing`
