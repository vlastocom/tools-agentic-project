---
name: unit-testing
description: Use this skill when writing or reviewing unit tests for frontend or backend code.
---

# Unit Testing

Unit tests form the base of the [testing pyramid](../../guides/testing-guide.md#the-testing-pyramid) (70% of all tests).
They should be fast, isolated and comprehensive.

## Frontend (Vitest)

Follow the [testing guide](../../guides/testing-guide.md) strictly.

1. **Test file location:** colocate with the source file (e.g. `Component.test.tsx` next to `Component.tsx`)
2. **Naming:** use `describe` blocks matching the component/function name, `it` blocks describing the behaviour
3. **Rendering:** use `@testing-library/react` — test behaviour, not implementation details
4. **Mocking:**
   - Mock Apollo Client with `MockedProvider` for GraphQL components
   - Mock Redux store with a test utility wrapper where needed
   - Prefer dependency injection over module mocking where practical
5. **Coverage targets:** aim for high coverage on business logic; do not chase 100% on boilerplate

## Backend (JUnit + Spring Boot)

1. **Test file location:** mirror the source package structure under `src/test/java/`
2. **Naming:** `<ClassName>Test.java`
3. **Annotations:** use `@ExtendWith(MockitoExtension.class)` for unit tests (no Spring context)
4. **Mocking:** use Mockito for dependencies
5. **Assertions:** prefer AssertJ fluent assertions

## Running tests

```bash
# Frontend
npx vitest run                          # All unit tests
npx vitest run src/path/to/file.test.tsx  # Single file

# Backend
./gradlew test                          # All unit tests
./gradlew test --tests "com.<org>.<project>.ClassName"  # Single class
```

## Guidelines

- Write tests as you implement — do not defer testing to a later step
- When modifying existing code, review and update the existing tests for that module
- Aim for the simplest but most comprehensive set of tests — avoid redundant test cases
- Test edge cases and error paths, not just the happy path

## References

- [Testing guide](../../guides/testing-guide.md)
- Parent workflow: `/task-implementation`
