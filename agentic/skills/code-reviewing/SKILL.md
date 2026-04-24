---
name: code-reviewing
description: Use this skill when reviewing pull requests and diffs. Reviews the code for quality, security, best practices, validates the low level design and user interface design. 
---

# Code Reviewer Skill

When reviewing code changes (code diffs, pull requests or any unstaged code), act as a Senior Engineer 
and follow these steps systematically:

## 1. Context & Purpose
*   Understand the goal of the PR from the context of the task being worked on. If unclear, ask for clarification.
*   Identify the scope: is this a hotfix, a new feature or refactoring?
*   Check for adherence to the SOLID principles and DRY (Don't Repeat Yourself) principle.

## 2. Review Checklist
Analyse the code for the following:

*   **Security**: Check for OWASP Top 10 vulnerabilities (SQL injection, XSS, insecure data handling, hardcoded credentials).
*   **Correctness & Logic**: Do the changes actually fulfill the intent? Look for race conditions and edge cases.
*   **TODOs**: All TODO comments must contain a backlog task ID. Do not commit any code, where this rule is violated. List the comment and its location and propose creating the appropriate task.
*   **Error Handling**: Are errors caught, logged and handled gracefully? Are any actions audited as per [Audit requirements](../../../docs/requirements/05-auditing.md)?
*   **Maintainability & Readability**: Is the code clear? Are variable/function names descriptive?
*   **Dead code**: Check for unused imports, unused fields, unused variables, unused methods and unreachable code. These are common leftovers after refactoring.
*   **Duplicate expressions**: Look for repeated identical expressions within a method body (e.g. calling `UUID.fromString(id)` multiple times on the same argument). Extract these into a `final` local variable and reuse it.
*   **Performance**: Look for $N+1$ query issues, inefficient algorithms or unnecessary computations.
*   **Testing**: Do tests cover the new logic comprehensively? Are existing tests passing? Are the tests (front end and backend) roughly matching the [testing pyramid](../../guides/testing-guide.md#the-testing-pyramid)?
*   **Test-run signals**: Scan the test output for unhandled errors (Vitest's `Errors N error(s)` line), timeouts, tear-down races, and `stderr` warnings from Apollo MockedProvider / React `act()` / jsdom. These are first-class review concerns even when every test is "green". Flag each distinct signal in the review with a specific root-cause hypothesis; the reviewee must either fix or file a CLEANUP task. "Flaky" and "pre-existing" are not acceptable dispositions without a backlog pointer.
*   **Comments**: Please review all changes in comments and make sure that they are clear, concise and follow [spelling and grammar rules](../../guides/spelling-and-grammar-rules.md)

## 3. Project metrics

Before delivering findings, gather and report the current LOC and test-coverage
picture. This contextualises every finding — a "low coverage" comment means more when
the number is shown.

### 3.1 Lines of code by language

Run `cloc` on the project root, excluding generated and vendor directories:

```bash
cloc /home/vlasto/src/finance/nest \
    --exclude-dir=node_modules,.gradle,build,dist,.next,coverage,.claude,playwright-report,test-results
```

Report the *Code* column by language in a compact table (Java, TypeScript, TSX, SQL,
HTML, Markdown — drop anything with fewer than ~50 lines of code). Skip the
`files`/`blank`/`comment` columns in the review output.

### 3.2 Backend test coverage (Jacoco — unit tests only)

Jacoco currently runs only for the unit-test task (`./gradlew test` →
`build/reports/jacoco/test/jacocoTestReport.xml`). If the report is stale or missing,
refresh it with `./gradlew test`, then parse the XML to summarise per-package coverage.

```bash
# Per-package INSTRUCTION coverage, sorted worst first
python3 - <<'PY'
import xml.etree.ElementTree as ET
root = ET.parse('/home/vlasto/src/finance/nest/build/reports/jacoco/test/jacocoTestReport.xml').getroot()
rows = []
for pkg in root.iter('package'):
    miss = cov = 0
    for c in pkg.findall('counter'):
        if c.get('type') == 'INSTRUCTION':
            miss = int(c.get('missed')); cov = int(c.get('covered'))
    total = miss + cov
    pct = 100.0 * cov / total if total else 0.0
    rows.append((pkg.get('name'), total, pct))
rows.sort(key=lambda r: r[2])
for name, total, pct in rows:
    print(f'{pct:5.1f}%  {total:>6}  {name}')
PY
```

Roll this up to a summary table in the review output: overall coverage %, and the
bottom 3-5 packages with the lowest coverage (flag any package below 70% — that is
the project-wide threshold enforced in `build.gradle`).

Integration tests do NOT currently produce a Jacoco report — call this out if any
class in the PR is exercised primarily via integration tests (its unit coverage may
look artificially low).

### 3.3 Frontend test coverage (Vitest / c8)

If the PR touches `nest-ui/`, regenerate and summarise:

```bash
npm --prefix /home/vlasto/src/finance/nest/nest-ui run test:coverage -- --reporter=json-summary
```

Vitest writes `nest-ui/coverage/coverage-summary.json`. Report the *total* line
coverage and flag files in the PR scope with line coverage below 70%.

For backend-only PRs this section can be skipped with a one-line "frontend unchanged —
Vitest coverage not re-run".

### 3.4 Highlighting gaps

In the review output, call out:

1. **Files newly introduced in this PR** whose coverage is below 70% — a
   concrete failure for this specific change.
2. **Files modified in this PR** whose coverage has *dropped* or is still below 70% —
   the PR is compounding an existing gap.
3. **Neighbour files at risk**: classes the PR touches indirectly (e.g. services it
   newly depends on) whose coverage is low — a follow-up concern, not a blocker.

Keep the metrics compact: one LOC table + one coverage table + a short
"coverage gaps" bullet list. Do not paste raw tool output into the review.

## 4. Feedback Structure

Provide feedback in a constructive, actionable tone. For each finding, use:

1.  **Issue**: Describe the problem (e.g. "Potential SQL injection").
2.  **Impact**: Explain why it matters (e.g. "Attacker can read the user database").
3.  **Suggested Fix**: Provide a code snippet or refactoring suggestion.

Please number the findings (e.g. FINDING-1, FINDING-2, etc.), so I can easily reference them in my answers.

## 5. Output Formatting
*   Summarise findings with: **[Critical]**, **[Important]** or **[Suggestion]**.
*   If everything looks good, provide a summary of what was done well.
*   Put the metrics section (from step 3) near the top of the review, before the findings, so the reader sees the size and coverage picture first.

## 6. Project-Specific Rules
*   Use TypeScript strictly; no `any` types.
*   Prefer functional programming patterns over imperative loops when appropriate.
*   Log errors using `logger.error` rather than `console.log`.
