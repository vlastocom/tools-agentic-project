---
stack: vite-react-typescript
applies-to: Vite + React + TypeScript SPAs
---

# Frontend code layout guide

**Applicability:** Vite + React + TypeScript SPA. If your project's
frontend is on a different stack (Next.js, Remix, SvelteKit, Solid,
plain HTML, no frontend at all), **delete this file at adoption time**
and replace with the stack-specific equivalent.

This guide defines how the project's React SPA is organised: the source tree, where
unit / integration / E2E tests live, environment-specific build modes, and the
supporting tooling (Vite, Vitest, Playwright, ESLint, TypeScript).

It applies to any Vite + React + TypeScript project in this organisation; the
specific versions (React 19.2, Vite 8, Vitest 4.1, Playwright 1.59, TS 5.9) are
the current project's values, kept current in
[infrastructure-design.md §20.1](../../docs/infrastructure-design.md).

## Directory layout

```
<frontend-dir>/
├── e2e/                           # Playwright E2E tests (outside src/)
│   ├── <feature-area>/            # Grouped by feature, e.g. projects/, tasks/
│   │   └── *.spec.ts              # One spec per user flow
│   ├── helpers.ts                 # Shared helpers (login, reachability, UUIDs)
│   └── tsconfig.json              # E2E-only tsconfig (separate from the app)
├── public/                        # Static assets copied verbatim into the build
├── src/
│   ├── main.tsx                   # Entry point; mounts <App /> into #root
│   ├── App.tsx                    # Router, providers, global layout
│   ├── index.css                  # Global CSS (sparingly — prefer MUI theme)
│   ├── vite-env.d.ts              # Vite-generated ambient types
│   ├── api/                       # REST client, typed query functions
│   │   ├── restClient.ts
│   │   ├── restClient.test.ts
│   │   └── tasks.ts               # Domain-specific API surfaces
│   ├── components/                # Reusable components
│   │   └── <ComponentName>/       # One folder per component
│   │       ├── <ComponentName>.tsx
│   │       ├── <ComponentName>.test.tsx
│   │       └── index.ts           # Re-export
│   ├── config/                    # Runtime config: env-var parsing, feature flags
│   ├── constants/                 # Enum-like frozen arrays, magic numbers
│   ├── pages/                     # Route-level components
│   │   └── <PageName>/
│   │       ├── <PageName>.tsx
│   │       └── <PageName>.test.tsx
│   ├── store/                     # Redux Toolkit
│   │   ├── index.ts               # store creation + rootReducer
│   │   ├── hooks.ts               # typed useAppDispatch, useAppSelector
│   │   └── slices/
│   │       └── <slice>.ts
│   ├── test/                      # Test infrastructure (not test files)
│   │   ├── setup.ts               # Vitest setup (extends expect, MSW)
│   │   ├── test-utils.tsx         # render() wrapper with providers
│   │   ├── constants.ts           # Shared timeouts, fixture IDs
│   │   └── integration/           # Cross-component integration tests
│   ├── theme/                     # MUI theme: dark palette, typography
│   ├── types/                     # Domain TypeScript types (shared across modules)
│   └── utils/                     # Cross-cutting helpers; keep thin
├── .env.devlocal                  # Laptop dev (Vite dev server)
├── .env.dev                       # Docker-dev environment
├── .env.stage                     # Stage environment
├── .env.prod                      # Production environment
├── .gitignore
├── .dockerignore
├── Dockerfile                     # Multi-stage build
├── eslint.config.js               # Flat config (ESLint 9)
├── index.html                     # Vite entry; the only HTML file
├── package.json
├── package-lock.json
├── playwright.config.ts
├── tsconfig.json                  # Main app config
├── tsconfig.node.json             # vite/vitest config files
├── vite.config.ts
└── vitest.config.ts
```

## The three test layers

Three kinds of tests, three lanes, three runners. No mixing.

| Layer               | Runner        | Location                                 | What it tests                                       | Speed        |
|---------------------|---------------|------------------------------------------|-----------------------------------------------------|--------------|
| **Unit**            | Vitest        | `*.test.ts(x)` colocated with source     | A single component / module in isolation           | ms           |
| **Integration**     | Vitest + MSW  | `*.integration.test.tsx` colocated, or `src/test/integration/*` | Multiple components wired with real providers; API stubbed by MSW | tens of ms   |
| **End-to-end**      | Playwright    | `e2e/**/*.spec.ts`                       | Real browser against real UI + real API + real DB  | seconds      |

Conventions:

- **Naming:** `Button.test.tsx` (unit), `apolloClient.integration.test.tsx`
  (integration), `users-list.spec.ts` (E2E). The `.spec.ts` suffix is reserved for
  Playwright so you can tell at a glance; Vitest picks up `.test.*`.
- **Colocation for unit/integration.** A component's test lives next to it. If the
  test gets too fat, that's a hint the component should be split.
- **Separation for E2E.** `e2e/` is outside `src/` so the production bundle does not
  accidentally sweep it up, and so Playwright has its own `tsconfig.json`.
- **`src/test/` is not where tests live.** It is where *test infrastructure* lives —
  setup files, render wrappers, constants, shared MSW handlers.

### Vitest config (`vitest.config.ts`)

```typescript
export default defineConfig({
    plugins: [react()],
    test: {
        globals: true,
        environment: 'jsdom',
        setupFiles: './src/test/setup.ts',
        css: true,
        exclude: ['**/node_modules/**', '**/dist/**', '**/e2e/**'],
        coverage: {
            provider: 'v8',
            reporter: ['text', 'json', 'html', 'lcov'],
            exclude: [
                'node_modules/', 'dist/', 'e2e/',
                'src/test/', 'src/config/', 'src/constants/', 'src/types/',
                '**/*.d.ts', '**/*.config.*', '**/mockData',
                'src/main.tsx', 'src/App.tsx', 'src/store/index.ts',
            ],
            thresholds: { lines: 80, functions: 75, branches: 75, statements: 80 },
        },
    },
    resolve: { alias: { '@': path.resolve(__dirname, './src') } },
})
```

Rationale:

- **`environment: 'jsdom'`** — a pure JS DOM; no real browser needed for unit /
  integration tests.
- **`exclude: ['**/e2e/**']`** — critical. Without this, Vitest tries to run
  Playwright specs as unit tests and fails on the `@playwright/test` imports.
- **`setupFiles: './src/test/setup.ts'`** — loaded before every test file. Extends
  `expect` with jest-dom matchers, sets up the MSW server, polyfills
  `matchMedia` / `IntersectionObserver` (JSDOM lacks them).
- **Coverage thresholds.** 80% lines/statements, 75% functions/branches. Below
  those the build fails. The excludes are defensive — pure type files, entry
  points, config live outside the coverage net.

### Playwright config (`playwright.config.ts`)

```typescript
export default defineConfig({
    testDir: './e2e',
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 2 : 0,
    workers: process.env.CI ? 1 : undefined,
    reporter: 'html',
    use: {
        baseURL: 'http://localhost:3000',
        trace: 'on-first-retry',
    },
    projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
    webServer: {
        command: 'npm run dev',
        url: 'http://localhost:3000',
        reuseExistingServer: !process.env.CI,
    },
})
```

Notes:

- **Single project (Chromium) by default.** Firefox and WebKit are commented out
  in the template; enable them per-project only when a specific spec needs them.
  Three browsers means three times the CI time for minimal marginal value.
- **`reuseExistingServer: !process.env.CI`** — locally, leave `npm run dev` running
  and Playwright will reuse it; in CI, Playwright spawns its own and tears down.
- **`trace: 'on-first-retry'`** — only captures the full trace on a failing run,
  not on every green test. Disk cheap, CI log budget preserved.
- **`workers: 1` in CI.** Determinism over throughput. Locally, `fullyParallel`
  plus the default worker count is fine.

E2E tests require a pre-populated database; see
[database-scripts-guide.md §dev/e2e](database-scripts-guide.md#databasedeve2e--playwright-e2e-fixtures).
`package.json`'s `test:e2e` script runs `../scripts/e2e-setup.sh` first to load the
fixtures, then Playwright.

### `src/test/setup.ts` essentials

```typescript
import { expect, afterEach, beforeAll, afterAll, vi } from 'vitest'
import { cleanup } from '@testing-library/react'
import * as matchers from '@testing-library/jest-dom/matchers'
import { setupServer } from 'msw/node'
import fetch from 'cross-fetch'

expect.extend(matchers)

export const server = setupServer()
beforeAll(() => {
    server.listen({ onUnhandledRequest: 'warn' })
    global.fetch = fetch as any
})
afterAll(() => server.close())
afterEach(() => {
    cleanup()
    server.resetHandlers()
})

// JSDOM lacks these — polyfill with no-ops
Object.defineProperty(window, 'matchMedia', { writable: true, value: vi.fn(/*…*/) })
window.IntersectionObserver = class { /*…*/ } as any
window.URL.createObjectURL = vi.fn(() => 'mocked-url')
window.URL.revokeObjectURL = vi.fn()
```

- **MSW server is process-wide** (`export const server`). Individual tests import
  `server` and call `server.use(…)` to override handlers for a single test.
- **`onUnhandledRequest: 'warn'`** — not `'error'`. A forgotten MSW handler is a
  bug but shouldn't nuke an unrelated test. Promote to `'error'` once the suite is
  stable.
- **`cleanup()` and `server.resetHandlers()` run in `afterEach`** to prevent
  cross-test leakage.

## Environment modes

Four `.env` files, each picking a different backend target and Sentry config. The
file is chosen by Vite's `--mode <name>` flag, which maps to one of the suffixes
`.env.<mode>`:

| File              | Mode        | Triggered by              | Target                                   |
|-------------------|-------------|---------------------------|------------------------------------------|
| `.env.devlocal`   | `devlocal`  | `npm run dev`             | Local Vite dev server + local API        |
| `.env.dev`        | `dev`       | `npm run dev:docker`      | Docker-Compose dev stack                 |
| `.env.stage`      | `stage`     | `npm run build:stage`     | Staging on NAS                           |
| `.env.prod`       | `prod`      | `npm run build` / `build:prod` | Production on NAS                   |

### Variable naming

Vite exposes to the client **only** variables prefixed `VITE_`. Anything else
stays server-side. The standard set:

```
VITE_API_URL=                      # base URL of the backend
VITE_APP_VERSION=                  # from git describe, baked at build time
VITE_SENTRY_DSN=                   # optional; empty disables Sentry
VITE_SENTRY_HOST=                  # optional; for self-hosted Sentry
VITE_SENTRY_TUNNEL=                # optional; ad-blocker workaround
VITE_SENTRY_ENVIRONMENT=           # overrides MODE for Sentry event tags
VITE_SENTRY_ENABLED=               # true/false; defaults to "auto in prod"
VITE_SENTRY_TRACES_SAMPLE_RATE=    # 0.0–1.0
```

All of the above are read through `src/config/env.ts`, a single module that parses
`import.meta.env`, validates the values, and exposes a typed `env` object. No
component reads `import.meta.env.VITE_FOO` directly — that pattern scatters
string-typed env access across the codebase.

## TypeScript config split

### `tsconfig.json` — application code

```json
{
    "compilerOptions": {
        "target": "ES2020",
        "lib": ["ES2020", "DOM", "DOM.Iterable"],
        "module": "ESNext",
        "moduleResolution": "bundler",
        "allowImportingTsExtensions": true,
        "isolatedModules": true,
        "moduleDetection": "force",
        "noEmit": true,
        "jsx": "react-jsx",
        "esModuleInterop": true,
        "allowSyntheticDefaultImports": true,
        "strict": true,
        "noUnusedLocals": true,
        "noUnusedParameters": true,
        "noFallthroughCasesInSwitch": true,
        "noUncheckedIndexedAccess": true,
        "baseUrl": ".",
        "paths": { "@/*": ["./src/*"] },
        "types": ["vitest/globals", "@testing-library/jest-dom", "node"],
        "skipLibCheck": true,
        "useDefineForClassFields": true
    },
    "include": ["src", "vitest.config.ts", "vite.config.ts"]
}
```

Key choices:

- **`strict: true`** plus the four extra strict-ness flags
  (`noUnusedLocals`, `noUnusedParameters`, `noFallthroughCasesInSwitch`,
  `noUncheckedIndexedAccess`). `noUncheckedIndexedAccess` is the big one — it
  makes every array access return `T | undefined`, catching off-by-one bugs at
  compile time.
- **`moduleResolution: "bundler"`** — the modern default; Vite's resolution.
- **`@/*` alias** — always prefer `@/api/tasks` over `../../api/tasks`.
- **`types` explicit** — pulling in vitest globals, jest-dom matchers, node types.
  Everything else comes from `@types/*` on demand.

### `tsconfig.node.json` — config files

```json
{
    "compilerOptions": {
        "target": "ES2022",
        "lib": ["ES2023"],
        "module": "ESNext",
        "moduleResolution": "bundler",
        "allowImportingTsExtensions": true,
        "isolatedModules": true,
        "moduleDetection": "force",
        "noEmit": true,
        "strict": true,
        "types": ["node"]
    },
    "include": ["vite.config.ts", "vitest.config.ts"]
}
```

This exists because `vite.config.ts` and `vitest.config.ts` run in Node, not in the
browser. They need `@types/node` but not `lib: DOM`. Keeping them in a separate
project lets the main `tsconfig.json` stay DOM-focused.

### `e2e/tsconfig.json` — Playwright tests

Its own config because E2E tests import `@playwright/test` types the main project
doesn't need, and import through the `@/` alias so shared constants
(`@/test/constants.ts`) can be reused.

## ESLint (flat config)

```javascript
import js from '@eslint/js'
import tseslint from 'typescript-eslint'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'

export default tseslint.config(
    { ignores: ['dist', 'coverage'] },
    {
        extends: [js.configs.recommended, ...tseslint.configs.recommended],
        files: ['**/*.{ts,tsx}'],
        plugins: { 'react-hooks': reactHooks, 'react-refresh': reactRefresh },
        rules: {
            ...reactHooks.configs.recommended.rules,
            'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
            '@typescript-eslint/no-explicit-any': 'warn',
        },
    },
)
```

The flat config (ESLint 9+) replaces the legacy `.eslintrc.*` hierarchy with a
single JS module. What we get:

- **TypeScript ESLint recommended rules.**
- **React hooks rules** — the `useEffect` / `useMemo` dependency-array lint.
- **react-refresh** — warns when a file exports a non-component alongside a
  component, which breaks HMR.
- **`no-explicit-any: warn`, not `error`** — intentional. `any` in a TS file is a
  smell we want to see in PR diffs, not a blocker that triggers developers to add
  `eslint-disable` comments.

Run via `npm run lint`; the script caps at `--max-warnings 50` so the bar cannot
silently slip.

## `package.json` scripts

```json
{
    "scripts": {
        "dev":         "vite --mode devlocal",
        "dev:docker":  "vite --mode dev",
        "build":       "tsc && vite build --mode prod",
        "build:dev":   "tsc && vite build --mode dev",
        "build:stage": "tsc && vite build --mode stage",
        "build:prod":  "tsc && vite build --mode prod",
        "typecheck":   "tsc --noEmit",
        "lint":        "eslint . --report-unused-disable-directives --max-warnings 50",
        "check":       "npm run typecheck",
        "preview":     "vite preview",
        "test":          "vitest",
        "test:ui":       "vitest --ui",
        "test:run":      "vitest run",
        "test:coverage": "vitest run --coverage",
        "test:watch":    "vitest watch",
        "test:e2e":       "bash ../scripts/e2e-setup.sh && playwright test",
        "test:e2e:ui":    "bash ../scripts/e2e-setup.sh && playwright test --ui",
        "test:e2e:headed":"bash ../scripts/e2e-setup.sh && playwright test --headed",
        "test:e2e:debug": "bash ../scripts/e2e-setup.sh && playwright test --debug",
        "test:e2e:setup": "bash ../scripts/e2e-setup.sh"
    }
}
```

Patterns:

- **`build` always does `tsc && vite build`.** A type error must fail the build.
  Vite itself does not type-check — it strips types and leaves them to `tsc`.
- **`test` alone is watch mode**, `test:run` is one-shot. This matches the mental
  model: "`test` while working, `test:run` in CI".
- **E2E always sets up fixtures first** (`bash ../scripts/e2e-setup.sh`). That
  script lives outside the UI project because it's part of the project-wide tool
  set (see [Database scripts guide](database-scripts-guide.md)).

## Component convention

Every non-trivial component gets its own folder:

```
src/components/TaskCard/
├── TaskCard.tsx          # the component
├── TaskCard.test.tsx     # unit tests
├── TaskCard.module.css   # scoped CSS if needed (usually: MUI's sx prop instead)
└── index.ts              # `export { TaskCard } from './TaskCard'`
```

Import via `@/components/TaskCard`, never
`@/components/TaskCard/TaskCard`. The `index.ts` re-export is the whole reason
components live in folders — it keeps call sites stable when internals split.

Trivially small components (a single styled wrapper) may live as a bare `.tsx`
file under `components/`. Threshold: if you need a sibling file (test, CSS,
subcomponent), make it a folder.

## Page convention

Pages mirror components but live under `pages/` and correspond 1:1 to routes:

```
src/pages/TaskList/
├── TaskList.tsx
├── TaskList.test.tsx
└── index.ts
```

A page component's responsibilities: fetch data, arrange `components/`, dispatch
redux actions. A page should not re-implement UI that a reusable `component`
could. If it does, extract.

## Redux Toolkit

```
src/store/
├── index.ts              # configureStore, rootReducer, RootState / AppDispatch types
├── hooks.ts              # export const useAppDispatch = () => useDispatch<AppDispatch>()
└── slices/
    ├── tasksSlice.ts
    ├── projectsSlice.ts
    └── uiSlice.ts
```

- **One slice per domain.** `tasksSlice`, `projectsSlice`, `sprintsSlice`. UI
  concerns (open modals, selected rows) live in `uiSlice`.
- **Never `useDispatch` / `useSelector` directly.** Always go through the typed
  wrappers in `store/hooks.ts` so you get `RootState` inference for free.
- **RTK Query** is built in to Redux Toolkit and is a reasonable alternative to a
  hand-rolled API layer. For this project we're choosing a simpler `fetch`-based
  `api/*.ts` with manual cache invalidation; revisit if the cache-coherence
  concerns become real.

## MUI theme

```
src/theme/
├── index.ts              # `export const theme = createTheme({ … })`
├── palette.ts            # dark palette per requirements §5.3
├── typography.ts
└── components.ts         # MUI component default prop overrides
```

One theme, one palette, dark by default. If a light palette becomes a requirement
later, it lives next to the dark palette here and is selected via a `theme.mode`
toggle in `uiSlice`.

## Anti-patterns

- **Running Vitest and Playwright against the same files.** They use different
  globals; a file imported by both will fail at runtime. Keep `e2e/` outside
  `src/` and `vitest.config.ts`'s `exclude` list aligned.
- **Reading `import.meta.env` directly in components.** Hides env-variable use,
  makes testing painful. Go through `@/config/env.ts`.
- **`any` in new code.** `no-explicit-any: warn` means new `any` shows up in PR
  diffs. Either pin down the type or write an inline comment justifying the
  escape hatch.
- **Deeply nested relative imports.** `../../../../components/TaskCard`
  indicates a structural problem; the `@/*` alias is almost always the right fix.
- **`Accept` tests that rely on specific network timing.** E2E tests use
  Playwright's auto-waiting (`expect(locator).toBeVisible()`); `waitForTimeout`
  is always a bug.

## See also

- [Backend code layout guide](backend-code-layout-guide.md) — the backend counterpart
- [Testing guide](testing-guide.md) — unit / integration / E2E doctrine
- [Database scripts guide](database-scripts-guide.md) — the `dev/e2e/` fixtures
  that Playwright depends on
