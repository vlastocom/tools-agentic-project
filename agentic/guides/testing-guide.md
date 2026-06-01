# Testing Guide

Comprehensive testing guide for projects on this template, covering both backend
(Java/Spring Boot) and frontend (React/TypeScript) testing. Adapt the
stack-specific sections (Vitest, JUnit, Testcontainers, Playwright) to your
project's actual choices; the layered structure (unit → integration → E2E) and
the per-task discipline ([SDLC §6 — Tests per task](sdlc-workflow-guide.md#6-tests-per-task))
are stack-agnostic.

---

## 1. General Principles

### The Testing Pyramid

```
         _______________
        /               \
       / E2E Tests (10%) \
      /                   \
     /  Integration (20%)  \
    /                       \
   /    Unit Tests (70%)     \
  /___________________________\
```

- **70% Unit Tests**: Fast, isolated tests for individual components, services, hooks and utilities
- **20% Integration Tests**: Test component interactions, database operations, Redux state, routing
- **10% E2E Tests**: Critical user flows only (login, dashboard, key features)

### Why This Distribution?

- Unit tests are fast, reliable and straightforward to debug
- Integration tests catch interaction bugs without E2E overhead
- E2E tests are slow but catch real-world issues

### Test Behaviour, Not Implementation

- Test what the user sees and does (frontend) or what the API returns (backend)
- Do not test internal state or implementation details
- Do not test third-party libraries (Material UI, Spring Security, etc.) — trust that they work

### Arrange-Act-Assert

All tests should follow the Arrange-Act-Assert pattern for clarity and consistency.

---

## 2. Backend Testing

### 2.1 Overview

| Aspect             | Unit Tests                | Integration Tests           |
|--------------------|---------------------------|-----------------------------|
| **Database**       | H2 in-memory (MySQL mode) | Real MySQL                  |
| **Spring context** | Partial or none           | Full `@SpringBootTest`      |
| **Speed**          | Fast (~seconds)           | Slower (~minutes)           |
| **Dependencies**   | None                      | Running MySQL container     |
| **Profile**        | `test`                    | `integration-test`          |
| **Gradle task**    | `./gradlew test`          | `./gradlew integrationTest` |

### 2.2 Project Structure

```
src/
├── test/                              # Unit tests
│   ├── java/com/vlasto/finance/nest/
│   │   ├── audit/                     # Audit aspect and context tests
│   │   ├── datafetcher/               # GraphQL DataFetcher tests
│   │   ├── entity/                    # Entity tests
│   │   ├── repository/                # Repository tests (@DataJpaTest)
│   │   ├── security/                  # Security filter tests
│   │   ├── service/                   # Service layer tests
│   │   └── NestApplicationTests.java  # Application context test
│   └── resources/
│       └── application-test.yml       # H2 in-memory config
│
├── integration-test/                  # Integration tests
│   ├── java/com/vlasto/finance/nest/
│   │   ├── datafetcher/               # GraphQL integration tests
│   │   ├── http/                      # HTTP-level authentication tests
│   │   ├── service/                   # Service integration tests
│   │   └── testutil/                  # Test helpers (see section 2.7)
│   └── resources/
│       └── application-integration-test.yml  # Real MySQL config
│
database/dev/integration-test/         # Per-class cleanup scripts
├── AuditServiceIntegrationTest.cleanup.sql
├── AuthenticationDataFetcherIntegrationTest.cleanup.sql
├── AuthenticationHttpIntegrationTest.cleanup.sql
├── BookDataFetcherIntegrationTest.cleanup.sql
└── SystemStatsDataFetcherIntegrationTest.cleanup.sql
```

### 2.3 File Naming Conventions

| Test Type        | Pattern                           | Example                            |
|------------------|-----------------------------------|------------------------------------|
| Unit test        | `{ClassName}Test.java`            | `BookServiceTest.java`             |
| Integration test | `{ClassName}IntegrationTest.java` | `AuditServiceIntegrationTest.java` |

### 2.4 Unit Tests

Unit tests use Mockito for dependency isolation and H2 in-memory database for repository tests.

#### Service Layer Tests

Mock all dependencies with `@Mock` and inject the subject with `@InjectMocks`:

```java
@ExtendWith(MockitoExtension.class)
@DisplayName("BookService")
class BookServiceTest {
    @Mock private BookRepository bookRepository;
    @InjectMocks private BookService bookService;

    @Test
    void getBooksByAccountId_shouldReturnBooks() {
        // Arrange
        when(bookRepository.findByAccountId(accountId)).thenReturn(expectedBooks);

        // Act
        List<Book> result = bookService.getBooksByAccountId(accountId);

        // Assert
        assertThat(result).hasSize(2);
        verify(bookRepository, times(1)).findByAccountId(accountId);
    }
}
```

#### Repository Tests

Use `@DataJpaTest` for a lightweight JPA test slice with the H2 database:

```java
@DataJpaTest
@ActiveProfiles("test")
class BookRepositoryTest {
    @Autowired private BookRepository bookRepository;

    @Test
    void findByAccountId_shouldReturnBooksForAccount() {
        // Test repository queries against H2
    }
}
```

#### GraphQL DataFetcher Tests

Use full Spring context with mocked services to test the GraphQL layer:

```java
@SpringBootTest
@ActiveProfiles("test")
class BookDataFetcherTest {
    @Autowired DgsQueryExecutor dgsQueryExecutor;
    @MockitoBean BookService bookService;

    @Test
    void getBooksShouldReturnBooks() {
        when(bookService.getBooksByAccountId(accountId)).thenReturn(List.of(book));

        List<String> bookNames = dgsQueryExecutor.executeAndExtractJsonPath(
            booksQuery(), "data.books[*].name", booksVariables(accountId.toString())
        );

        assertThat(bookNames).containsExactly("Test Book");
    }
}
```

#### Security Tests

When testing DataFetchers that require authentication, manually populate the security context:

```java
@BeforeEach
void setUp() {
    SecurityContextHolder.getContext().setAuthentication(
        new UsernamePasswordAuthenticationToken(testUser, null, List.of())
    );
}

@AfterEach
void tearDown() {
    SecurityContextHolder.clearContext();
}
```

### 2.5 Integration Tests

Integration tests run against a real MySQL database and use the full Spring context.

#### Common Annotations

```java
@SpringBootTest
@ActiveProfiles("integration-test")
@DisplayName("Test suite description")
```

#### Test Lifecycle Pattern

```java
@BeforeAll
static void resetDatabase(@Autowired TestDataCleanupHelper helper) {
    helper.resetDatabase();  // Reset to clean state once per class
}

@BeforeEach
void setUp() {
    cleanupHelper.dataCleanupForClass(this.getClass());  // Per-test cleanup
    userHelper.reset();                                    // Clear cached users
    testUser = userHelper.getTestUser(1);                  // Lazy-load test user
}
```

#### Async Testing with Awaitility

For asynchronous operations (e.g. audit logging), use Awaitility:

```java
await().atMost(500, MILLISECONDS).until(() -> auditRepository.count() > 0);
```

#### HTTP-Level Tests

For end-to-end HTTP testing (e.g. the authentication flow):

```java
@SpringBootTest(webEnvironment = RANDOM_PORT)
@ActiveProfiles("integration-test")
class AuthenticationHttpIntegrationTest {
    private MockMvc mockMvc;

    @BeforeEach
    void setUp() {
        mockMvc = MockMvcBuilders.webAppContextSetup(webApplicationContext)
            .apply(springSecurity()).build();
    }

    @Test
    void fullAuthenticationFlowLoginAndQuery() throws Exception {
        mockMvc.perform(post("/graphql")
            .contentType(MediaType.APPLICATION_JSON)
            .content(loginMutation))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data.login.accessToken").isNotEmpty());
    }
}
```

#### Writing Cleanup Scripts

Each integration test class requires a cleanup script at
`database/dev/integration-test/{ClassName}.cleanup.sql`. The script must:

1. Delete dependent records (Audit, UserSecurity, roles)
2. Preserve the Root user
3. Use MySQL session variables for referencing the Root user

Example:

```sql
-- Delete all audit records
delete from Audit where true;

set @rootId = (select id from User where email = 'root');

-- Delete test users (except Root)
delete from UserSecurity where id != @rootId;
delete from UserSystemRole where user_id != @rootId;
delete from UserAccountRole where user_id != @rootId;
delete from User where id != @rootId;
```

See the [integration test utilities README](../../src/integration-test/java/com/vlasto/finance/nest/testutil/README.md)
for full documentation of `TestDataCleanupHelper`, `UserDataHelper` and `AccountDataHelper`.

### 2.6 Assertion and Mocking Libraries

| Library         | Purpose                     | Usage                             |
|-----------------|-----------------------------|-----------------------------------|
| **AssertJ**     | Fluent assertions           | `assertThat(result).hasSize(2)`   |
| **Mockito**     | Mocking (unit tests)        | `@Mock`, `@InjectMocks`, `when()` |
| **MockitoBean** | Mocking (Spring tests)      | `@MockitoBean` on field           |
| **Awaitility**  | Async testing (integration) | `await().atMost(...).until(...)`  |

**Important:** **AssertJ** (`assertThat`) is strongly preferred for all backend assertions over
JUnit's built-in assertions (`assertEquals`, `assertTrue`, `assertThrows`, etc.). AssertJ provides
more readable assertions, better failure messages and a consistent fluent API across the codebase.

```java
// Correct — use AssertJ
assertThat(result).isEqualTo("expected");
assertThat(list).hasSize(3).contains("item");
assertThatThrownBy(() -> service.doSomething(null))
        .isInstanceOf(IllegalArgumentException.class);

// Incorrect — do not use JUnit assertions
assertEquals("expected", result);
assertTrue(list.size() == 3);
assertThrows(IllegalArgumentException.class, () -> service.doSomething(null));
```

### 2.7 Test Data Helpers

Integration tests use three helper classes for test data management:

- **`TestDataCleanupHelper`** — manages database cleanup using the privileged `creator` user
  and per-class SQL cleanup scripts (25% faster than programmatic cleanup)
- **`UserDataHelper`** — creates and caches test users with lazy initialisation (1-based indexing)
- **`AccountDataHelper`** — creates and manages test accounts (0-based indexing)

Full documentation: [testutil/README.md](../../src/integration-test/java/com/vlasto/finance/nest/testutil/README.md)

### 2.8 Running Backend Tests

#### Prerequisites

- **Unit tests**: No external dependencies required (H2 in-memory database)
- **Integration tests**: Running MySQL container and the `DB_PASSWORD` environment variable

#### Starting the Database

```bash
docker-compose -p nest-dev -f docker-compose.yml -f docker-compose.dev.yml up -d db
# Wait for "ready for connections" in the logs
docker logs nest-db-dev --follow
```

#### Gradle Commands

```bash
# Run unit tests
./gradlew test

# Run integration tests
./gradlew integrationTest

# Run both
./gradlew test integrationTest

# Run a specific test class
./gradlew test --tests BookServiceTest

# Generate coverage report
./gradlew test jacocoTestReport

# Verify coverage threshold
./gradlew test jacocoTestCoverageVerification
```

#### IntelliJ Run Configurations

| Configuration                | What It Does                               |
|------------------------------|--------------------------------------------|
| Local - Test API             | Run unit tests with coverage               |
| Local - Test API Integration | Run integration tests (requires MySQL)     |
| Local - Clean build API      | Full clean build with all tests + coverage |

See [.run/README.md](../../.run/README.md) for full details.

#### Credential Management

Tests that connect to MySQL require the `DB_PASSWORD` environment variable.
Three options for setting it up:

1. **`scripts/set-build-env.sh`** (recommended) — run once after cloning; generates `options.txt`
   and `gradle.properties.local` from `.secrets/db-creator.txt`
2. **Manual `gradle.properties.local`** — create the file with
   `systemProp.DB_PASSWORD=<password>` (the file is in `.gitignore`)
3. **Environment variable** — `export DB_PASSWORD=$(cat .secrets/db-creator.txt)` before
   running Gradle

All passwords are stored in `.secrets/` (never committed) and referenced via environment
variables — never hardcoded in configuration files.

### 2.9 Code Coverage (JaCoCo)

| Setting              | Value                                                   |
|----------------------|---------------------------------------------------------|
| **Minimum coverage** | 70%                                                     |
| **Exclusions**       | `**/entity/**`, `**/config/**`                          |
| **Reports**          | HTML (`build/reports/jacoco/test/html/index.html`), XML |

```bash
# Generate the report
./gradlew test jacocoTestReport

# Enforce the threshold
./gradlew test jacocoTestCoverageVerification
```

---

## 3. Frontend Testing

### 3.1 Overview

| Tool                            | Purpose                     |
|---------------------------------|-----------------------------|
| **Vitest**                      | Test runner and assertions  |
| **React Testing Library**       | Component testing           |
| **@testing-library/user-event** | User interaction simulation |
| **@testing-library/jest-dom**   | DOM matchers                |
| **Playwright**                  | E2E testing                 |
| **@vitest/coverage-v8**         | Code coverage               |

### 3.2 Project Structure

```
nest-ui/
├── src/
│   ├── components/
│   │   ├── Header/
│   │   │   ├── index.tsx
│   │   │   └── Header.test.tsx            # Co-located unit test
│   │   └── Sidebar/
│   │       ├── index.tsx
│   │       └── Sidebar.test.tsx
│   ├── pages/
│   │   └── Login/
│   │       ├── index.tsx
│   │       └── Login.test.tsx
│   ├── utils/
│   │   ├── formatters.ts
│   │   └── formatters.test.ts
│   └── test/
│       ├── setup.ts                       # Vitest setup (jest-dom matchers, cleanup)
│       ├── test-utils.tsx                 # renderWithProviders helper
│       └── integration/
│           └── *.integration.test.tsx     # Cross-cutting integration tests
├── e2e/                                   # Playwright E2E tests
│   ├── auth/
│   │   └── login.spec.ts
│   └── dashboard/
│       └── dashboard.spec.ts
├── vitest.config.ts
└── playwright.config.ts
```

### 3.3 File Naming Conventions

| Test Type        | Pattern                  | Example                          |
|------------------|--------------------------|----------------------------------|
| Unit test        | `*.test.tsx`             | `Login.test.tsx`                 |
| Integration test | `*.integration.test.tsx` | `auth-flow.integration.test.tsx` |
| E2E test         | `*.spec.ts`              | `login.spec.ts`                  |

Unit and integration tests are **co-located** with the source files they test. Cross-cutting
integration tests that span multiple pages or components (e.g. routing, full app flows) live in
`src/test/integration/`. E2E tests live in the `e2e/` directory at the project root.

### 3.4 Setup

#### Test Setup File (`src/test/setup.ts`)

```typescript
import { expect, afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'
import * as matchers from '@testing-library/jest-dom/matchers'

// Extend Vitest's expect with jest-dom matchers
expect.extend(matchers)

// Cleanup after each test
afterEach(() => {
  cleanup()
})
```

#### Test Utilities (`src/test/test-utils.tsx`)

The `renderWithProviders` function wraps components with all required providers (Redux store,
BrowserRouter, ThemeProvider) for testing:

```typescript
import { renderWithProviders, screen, userEvent } from '@/test/test-utils'

// Usage in tests:
renderWithProviders(<Login />)
```

See `nest-ui/src/test/test-utils.tsx` for the full implementation.

### 3.5 Unit Tests

**Purpose**: Test individual components, hooks and functions in isolation.

```typescript
import { describe, it, expect, vi } from 'vitest'
import { renderWithProviders, screen, userEvent } from '@/test/test-utils'
import Login from './index'

describe('Login', () => {
  it('renders login form', () => {
    renderWithProviders(<Login />)
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('enables submit button when fields are filled', async () => {
    const user = userEvent.setup()
    renderWithProviders(<Login />)

    await user.type(screen.getByLabelText(/email/i), 'test@example.com')
    await user.type(screen.getByLabelText(/password/i), 'password123')

    expect(screen.getByRole('button', { name: /sign in/i })).toBeEnabled()
  })
})
```

**What to test**: rendering, props, user interactions, conditional rendering, error states,
utility function return values.

### 3.6 Integration Tests

**Purpose**: Test how multiple components work together (Redux state, routing, form flows).

```typescript
describe('Login Flow Integration', () => {
  it('redirects to dashboard after successful login', async () => {
    const user = userEvent.setup()
    renderWithProviders(<App />)

    await user.click(screen.getByRole('link', { name: /login/i }))
    await user.type(screen.getByLabelText(/email/i), 'test@example.com')
    await user.type(screen.getByLabelText(/password/i), 'password123')
    await user.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => {
      expect(window.location.pathname).toBe('/')
    })
  })
})
```

### 3.7 E2E Tests (Playwright)

**Purpose**: Test complete user flows in a real browser.

#### Prerequisites

Running `npm run test:e2e` (and the `:ui`, `:headed`, `:debug` variants) automatically:

1. Brings up the dev MySQL and Mailpit containers (no-op if already running).
2. Applies every `database/dev/e2e/*.sql` seed script in alphabetical order — the
   dev DB is wiped to a known state every run.
3. Stops any backend currently on port 8090 and starts a fresh one with the `dev`
   profile (mirrors the IntelliJ "Local - Run API" run configuration). Logs at
   `/tmp/nest-api-e2e.log`.
4. Waits for `/actuator/health` to return UP, then hands over to Playwright.
5. The Playwright `webServer` config spins up the frontend dev server itself.

The orchestration lives in [`scripts/e2e-setup.sh`](../../scripts/e2e-setup.sh). To
stop the backend started by the setup (e.g. before launching the IntelliJ run config),
use [`scripts/e2e-teardown.sh`](../../scripts/e2e-teardown.sh) — it leaves the DB
and Mailpit containers running.

#### Test Data

The E2E initialisation script creates nine test users (`test1@example.com` through
`test9@example.com`) with passwords `password1` through `password9`, and six test accounts.
The primary test user is `test4@example.com` / `password4` as this user has access to multiple
accounts.

See the [E2E initialisation script](../../database/dev/e2e/01-initialise.sql) for the full
test data definition, and §3.7.1 below for the fixture-ownership rules that govern which
spec file is allowed to mutate which user/account.

#### 3.7.1 Fixture Isolation

**Playwright runs spec files in parallel.** Two specs that mutate the same seeded user or
account will race each other — passing most of the time and flaking at the worst moments.
"Flaky" is never an acceptable disposition: if two E2E runs with the same code give different
failures, you have a fixture-contention bug. Find the mutator/reader pair and migrate one of
them.

**The rule:** every seeded fixture (user or account) is either **shared read-only** or **owned
exclusively by one spec file**. No exceptions.

##### Current ownership

| Fixture           | Kind      | Owner                     | Allowed mutations                           |
|-------------------|-----------|---------------------------|---------------------------------------------|
| TEST1–TEST6       | Shared    | *(none)*                  | Read-only — assertions, login, visibility   |
| TEST7             | Mutation  | `users-list.spec.ts`      | Suspend / reactivate                        |
| TEST8             | Mutation  | `user-details.spec.ts`    | Profile edit, system-role toggle            |
| TEST9             | Mutation  | `account-details.spec.ts` | Add + remove owner on ACCOUNT3              |
| ACCOUNT1–ACCOUNT3 | Shared    | *(none)*                  | Read-only — role-count assertions, etc.     |
| ACCOUNT4          | Shared    | *(none)*                  | Read-only — row-click / open-details target |
| ACCOUNT5          | Mutation  | `account-details.spec.ts` | Rename, suspend / reactivate, archive       |
| ACCOUNT6          | Mutation  | `user-details.spec.ts`    | Target for add/remove-role flow             |
| *Runtime-created* | Ephemeral | `accounts-list.spec.ts`   | Create-account flow; archived on cleanup    |

##### When adding a new mutation test

One of three paths:

1. **Claim an unclaimed fixture.** Add a row above and migrate the test to use it.
2. **Add a new seed fixture.** Bump `test10@example.com` / `ACCOUNT7` in
   [`database/dev/e2e/01-initialise.sql`](../../database/dev/e2e/01-initialise.sql) and the
   matching entry in [`nest-ui/src/test/constants.ts`](../../nest-ui/src/test/constants.ts).
   Prefer this when the new test's mutations don't fit any existing fixture's semantics
   (e.g. it needs an archived or suspended starting state).
3. **Create the fixture at runtime.** Use a timestamp-suffixed name to avoid re-run
   collisions, and clean up at the end of the test (archive, delete, etc.). Prefer this
   when the fixture is ephemeral by nature (e.g. an account created specifically to test
   the create flow).

##### When an E2E test suddenly flakes

Before re-running:

1. Run the failing spec **in isolation** (`npm run test:e2e -- path/to/spec`). If it passes,
   you have a fixture-contention bug with another spec.
2. Grep the repo for the fixture name. Any spec outside the declared owner that appears in
   the results is the offender.
3. Migrate one of the conflicting specs to a dedicated fixture (add a row to the table above).

Never mark the test `test.skip` or wrap it in `test.retry` to paper over the flake — the next
maintainer will inherit the same mystery.

#### Writing E2E Tests

```typescript
import { test, expect } from '@playwright/test'

test.describe('Login Flow', () => {
  test('user can login with valid credentials', async ({ page }) => {
    await page.goto('/login')

    await page.fill('[name="email"]', 'test4@example.com')
    await page.fill('[name="password"]', 'password4')
    await page.click('button[type="submit"]')

    await expect(page).toHaveURL(/\/$/)
    await expect(page.locator('h1')).toContainText('Dashboard')
  })
})
```

#### Page Object Model

Use the Page Object Model for reusable page interactions:

```typescript
// e2e/pages/LoginPage.ts
export class LoginPage {
  constructor(private page: Page) {}

  async login(email: string, password: string) {
    await this.page.fill('[name="email"]', email)
    await this.page.fill('[name="password"]', password)
    await this.page.click('button[type="submit"]')
  }
}
```

#### WSL Note

Headed mode (`--headed`) requires an X11 server (like VcXsrv or WSLg). Use UI mode (`--ui`)
or headless mode for WSL development.

### 3.8 Query Priority (React Testing Library)

When selecting elements in tests, use queries in this priority order:

1. `getByRole` (most preferred — matches accessibility roles)
2. `getByLabelText` (for form elements)
3. `getByPlaceholderText`
4. `getByText`
5. `getByTestId` (last resort)

Always prefer `userEvent` over `fireEvent` for realistic user interaction simulation.

### 3.9 Running Frontend Tests

```bash
cd nest-ui

# Unit and integration tests
npm test                   # Watch mode (development)
npm run test:run           # Run once (CI)
npm run test:coverage      # Run with coverage
npm run test:ui            # Visual test runner

# E2E tests
npm run test:e2e           # Run all E2E tests
npm run test:e2e:ui        # Interactive UI mode
npm run test:e2e:debug     # Step-through debugging
npm run test:e2e:headed    # Headed browser (requires X11)

# Specific tests
npm test Login.test.tsx                              # Specific file
npm test -- --run src/components/NotAuthorized        # Specific directory
npx playwright test e2e/auth/protected-routes.spec.ts # Specific E2E test

# Type checking
npm run typecheck          # tsc --noEmit (strict mode)
npm run check              # All static checks
```

### 3.10 Code Coverage (Vitest)

| Metric     | Target | Minimum |
|------------|-------:|--------:|
| Lines      |    85% |     80% |
| Functions  |    85% |     80% |
| Branches   |    80% |     75% |
| Statements |    85% |     80% |

Coverage exclusions: `node_modules/`, `src/test/`, `*.config.ts`, `*.d.ts`, `**/index.ts`

```bash
npm run test:coverage
# HTML report: nest-ui/coverage/index.html
```

---

## 4. Database Users and Permissions

Tests use different database users depending on the test type:

| User      | Used By                     | Permissions                     |
|-----------|-----------------------------|---------------------------------|
| `api`     | Integration tests (runtime) | SELECT, INSERT (limited DELETE) |
| `creator` | TestDataCleanupHelper       | ALL PRIVILEGES on nestdb        |
| `root`    | Manual operations           | Full system privileges          |

The `api` user intentionally cannot delete from the `Audit` table (audit logs are immutable).
The `TestDataCleanupHelper` uses the `creator` user for cleanup operations that require
broader permissions.

---

## 5. CI/CD Integration

### Backend

```bash
# Full CI pipeline
./gradlew clean build test jacocoTestReport jacocoTestCoverageVerification
```

### Frontend

```bash
cd nest-ui

# Full CI pipeline
npm run check && npm run test:coverage && npm run test:e2e
```

### GitHub Actions Example

```yaml
name: Test

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: ${{ secrets.DB_ROOT_PASSWORD }}
          MYSQL_DATABASE: nestdb
        ports:
          - 3306:3306
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '25'
      - run: ./gradlew test jacocoTestReport
        env:
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}

  frontend-unit-tests:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: nest-ui
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '24'
      - run: npm ci
      - run: npm run test:coverage
      - uses: codecov/codecov-action@v3
        with:
          files: ./nest-ui/coverage/lcov.info

  frontend-e2e-tests:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: nest-ui
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '24'
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run test:e2e
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: nest-ui/playwright-report/
```

---

## 6. Troubleshooting

### Backend

| Problem                                      | Solution                                                                      |
|----------------------------------------------|-------------------------------------------------------------------------------|
| `DB_PASSWORD not set`                        | Run `scripts/set-build-env.sh` (see section 2.8)                              |
| `java.net.ConnectException` in tests         | Start the database: `docker-compose -p nest-dev ... up -d db`                 |
| Integration tests leave stale data           | Check the cleanup script in `database/dev/integration-test/`                  |
| JaCoCo coverage below threshold              | Review `build/reports/jacoco/test/html/index.html` for uncovered areas        |
| `allowMultiQueries` error in cleanup scripts | Verify JDBC URL includes `?allowMultiQueries=true` in `TestDataCleanupHelper` |

### Frontend

| Problem                       | Solution                                                            |
|-------------------------------|---------------------------------------------------------------------|
| `Cannot find module` in tests | Verify `src/test/setup.ts` is correctly referenced in Vitest config |
| Playwright tests timeout      | Increase timeout in `playwright.config.ts` (default: 30s)           |
| Coverage threshold not met    | Run `npm run test:coverage` and review the HTML report              |
| Mock not working in Vitest    | Ensure `vi.mock()` is called before the imports that use it         |
| Playwright fails on WSL       | Run `sudo npx playwright install-deps` for system libraries         |
| Headed mode fails on WSL      | Use `--ui` mode instead (headed requires X11 server)                |

---

## 7. Quick Reference

### Backend Commands

| Task                      | Command                                         |
|---------------------------|-------------------------------------------------|
| Run unit tests            | `./gradlew test`                                |
| Run integration tests     | `./gradlew integrationTest`                     |
| Run all tests             | `./gradlew test integrationTest`                |
| Generate coverage report  | `./gradlew test jacocoTestReport`               |
| Verify coverage threshold | `./gradlew test jacocoTestCoverageVerification` |
| Run specific test class   | `./gradlew test --tests BookServiceTest`        |

### Frontend Commands

| Task                   | Command                  |
|------------------------|--------------------------|
| Run tests (watch mode) | `npm test`               |
| Run tests (once)       | `npm run test:run`       |
| Run with coverage      | `npm run test:coverage`  |
| Visual test runner     | `npm run test:ui`        |
| TypeScript type check  | `npm run typecheck`      |
| Run E2E tests          | `npm run test:e2e`       |
| Run E2E with UI        | `npm run test:e2e:ui`    |
| Debug E2E tests        | `npm run test:e2e:debug` |
