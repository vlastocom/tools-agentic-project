# Base instructions for CLAUDE

Please bootstrap from this file wherever needed.

<!--
    ==============================================================
    This is a TEMPLATE. Placeholders are wrapped in < > angle
    brackets. Replace them at project-creation time with the
    project's actual values. Leave the guide references intact —
    those are the organisation's shared doctrine and apply to
    every project.
    ==============================================================
-->

## Mission

<ONE-OR-TWO-PARAGRAPH STATEMENT OF WHAT THIS PROJECT DOES AND WHY IT
EXISTS. Derived from the README; edit both in sync.>

## Operating principles

1. Explicitly grant yourself [permissions](docs/permissions.md)
2. Follow the [spelling and grammar rules](agentic/guides/spelling-and-grammar-rules.md)
3. Run every diff through the [code-quality checklist](agentic/guides/code-quality-checklist.md)
   before declaring work done — this is the consolidated catch-net for
   the patterns that have historically drifted (unused imports, long
   sentences, dangling doc-comments, stale class refs, NPE-prone chains,
   magic strings, hand-rolled serialisation, etc.). The
   [code-reviewer](agentic/agents/code-reviewer.md) treats every miss as
   at-least a `should-fix`
4. Follow the [SDLC workflow guide](agentic/guides/sdlc-workflow-guide.md) —
   this defines the three-mode cadence (plan / implement / review), the
   artefact taxonomy, the stop-and-ask contract, the TDD rule, and the
   skill/subagent inventory this project uses
5. Make yourself acquainted with [skills available to you](agentic/guides/skills-overview.md)
6. Maintain the [backlog](docs/backlog.md) per the [backlog structure](agentic/guides/backlog-structure.md)
7. Follow the [database scripts guide](agentic/guides/database-scripts-guide.md)
   when writing or reviewing SQL, schema migrations and seed data
   *(remove if the project has no database)*
8. Follow the [date and time guide](agentic/guides/date-time-guide.md) for
   every date or time value across the database, API, and front end
9. Follow the [testing guide](agentic/guides/testing-guide.md) when writing
   or reviewing unit, integration, or end-to-end tests
10. Follow the [backend code layout guide](agentic/guides/backend-code-layout-guide.md)
    for the Gradle / Java / Spring Boot source-set layout, package-by-layer
    structure, and build configuration
    *(remove or replace if the project's backend uses a different stack)*
11. Follow the [frontend code layout guide](agentic/guides/frontend-code-layout-guide.md)
    for the React SPA source tree, test layout, environment modes and
    tooling (Vite, Vitest, Playwright, ESLint, TypeScript)
    *(remove or replace if the project has no React front end)*
12. Follow the [local development environment guide](agentic/guides/local-development-environment-guide.md)
    for first-time developer setup, secrets bootstrap and IntelliJ run
    configurations

## Workflow

Initial design — follow this when starting a new project or a major new
feature area:

1. Read the [README.md](README.md) to understand the mission.
2. **Interactive requirements stage:**
   - Through questions and answers, discover the detailed requirements
   - Keep asking questions until everything is clear enough to proceed
   - Document everything in [requirements.md](docs/requirements.md)
3. Operator reviews; edits; approves.
4. Create the design artefacts (in this order):
   - [Data model](docs/data-model.md)  *(if the project has persistent state)*
   - [Infrastructure design](docs/infrastructure-design.md)
   - [System design](docs/system-design.md)
   - [Deployment plan](docs/deployment-plan.md)  *(if the project is deployed)*
5. Operator reviews each artefact interactively.
6. Plan tasks in the backlog (`/sprint-planning`).
7. Operator reviews the plan.
8. Execute tasks per the SDLC workflow below.

For the tasks, strictly follow this workflow (per
[sdlc-workflow-guide.md](agentic/guides/sdlc-workflow-guide.md)):

1. `/sprint-planning` — interactive. Ends with grooming + task-planning
   subagents producing plans. Operator reviews and approves.
2. `/sprint-implementation` — unattended. Orchestrator dispatches
   per-task pipelines (task-implementation → integration-testing →
   code-reviewing → task-wrapup). E2E tasks are regular tasks running
   the same pipeline. Stops on the triggers listed in
   [sdlc-workflow-guide.md §7](agentic/guides/sdlc-workflow-guide.md#7-stop-and-ask-contract-detailed).
3. `/sprint-review` — interactive. Operator reviews the sprint outcome,
   coverage summary, E2E flows, decisions, deviations. Skill commits
   and pushes.

## Environment

<IF THIS PROJECT HAS A FIXED DEV ENVIRONMENT, LIST ANYTHING PERSISTENTLY
USEFUL HERE. OTHERWISE DELETE THIS SECTION.>

Examples of persistently-useful facts:
- Operating-system assumption (e.g. "Dev on Linux / WSL2 only")
- The concrete names of this project's NAS / hosts (if any)
- Any non-obvious toolchain requirements not derivable from build files
