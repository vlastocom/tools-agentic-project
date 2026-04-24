---
name: codebase-stats
description: Report lines of code by language plus backend (JaCoCo) and frontend (Vitest) test coverage summaries for the project.
---

# Codebase Statistics

Use this skill to produce the "project metrics" snapshot required by
`/code-reviewing` (lines of code plus backend and frontend coverage) or for ad-hoc
audits of the codebase.

The skill wraps `agentic/scripts/codebase_stats.py`, a stdlib-only Python helper
that calls `cloc`, reads the existing JaCoCo XML report and the Vitest
`coverage-summary.json`. It is safe to re-run and needs no configuration.

## When to use

- Gathering the metrics block at the top of a code review (step 3 of
  `/code-reviewing`).
- Checking overall coverage and the worst-covered packages before or after a
  substantial change.
- Auditing how many lines of code each language contributes to the project.

## Usage

Run the script from the project root:

```bash
# All three sections (default — same as --all)
python agentic/scripts/codebase_stats.py

# Individual sections
python agentic/scripts/codebase_stats.py --loc
python agentic/scripts/codebase_stats.py --backend-coverage
python agentic/scripts/codebase_stats.py --frontend-coverage

# Per-file frontend coverage for specific files under the PR scope
python agentic/scripts/codebase_stats.py --frontend-coverage \
    --scope pages/Admin/AccountsPage.tsx \
    --scope pages/Admin/components/AccountsList.tsx
```

Flags:

- `--loc` — runs `cloc` with the project exclude list, prints a compact
  per-language table (drops languages below 50 lines of code).
- `--backend-coverage` — parses `build/reports/jacoco/test/jacocoTestReport.xml`,
  prints overall INSTRUCTION coverage and the five lowest-covered packages.
  Flags anything below the 70% project threshold. If the report is missing it
  warns and suggests `./gradlew test`; pair with `--strict` to fail the script.
- `--frontend-coverage` — reads `nest-ui/coverage/coverage-summary.json` and, if
  missing, regenerates it via `npm --prefix nest-ui run test:coverage`. Prints
  overall line coverage and (with `--scope`) per-file breakdowns.
- `--scope <suffix>` — repeatable; limits the frontend per-file output to files
  whose path ends with the given suffix.
- `--strict` — treat a missing JaCoCo report as a failure (exit 1).

## Output

Example default run:

```
Lines of code by language
  Language      Files    Code
  ------------  -----  ------
  Markdown        117  23,286
  Java            158  20,584
  TypeScript      157  17,640
  ...
  TOTAL           543  77,968

Backend coverage (JaCoCo INSTRUCTION)
  Overall:  96.6%
  Lowest 5 packages:
      Cov%  Instr  Package
    ------  -----  -----------------------------------
       8.5     82  com/vlasto/finance/nest              BELOW
      91.2   1047  com/vlasto/finance/nest/audit
      ...
  Packages below 70%: 1

Frontend coverage (Vitest lines)
  Overall:  94.2%  (4885/5183 lines)
```

## References

- Script: [codebase_stats.py](../../scripts/codebase_stats.py)
- Related skill: [code-reviewing](../code-reviewing/SKILL.md)
- Backend threshold reference: `build.gradle` (jacocoTestCoverageVerification)
