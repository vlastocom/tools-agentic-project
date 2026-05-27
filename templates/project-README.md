# <PROJECT NAME>

<!--
    ==============================================================
    This is a TEMPLATE README. Replace the placeholders wrapped in
    < > angle brackets with your project's values, then trim the
    sections you don't need. Keep the structure — it maps to
    CLAUDE.md and is what the SDLC workflow expects.
    ==============================================================
-->

<ONE-LINE TAGLINE — WHAT DOES THIS PROJECT DO?>

## Mission

<ONE-TO-THREE-PARAGRAPH STATEMENT. What problem does this project solve?
Who is it for? Why is it built the way it is?>

## Top-level features

<BULLETED LIST OF THE PRIMARY CAPABILITIES THE PROJECT OFFERS. Phrase
each one as a user-visible outcome where possible.>

- <capability 1>
- <capability 2>
- <capability 3>

## Status

- **Current phase:** <e.g. "Design", "Bootstrap sprint", "GA", "Maintenance">
- **Latest release:** <tag or "pre-release">
- **Entry point for new contributors:** [CLAUDE.md](CLAUDE.md)

## Getting started

### Prerequisites

<LIST THE TOOLS A NEW OPERATOR NEEDS. Examples:>

- <runtime-1> version <X.Y>
- <runtime-2> version <X.Y>
- Docker + Docker Compose v2
- Claude Code CLI (for agent-assisted development)

### First-time setup

```bash
git clone <repo-url>
cd <project-dir>

# 1. Wire up the .claude/ symlinks to agentic/
./.claude/setup_claude_dir.sh

# 2. Provision secrets (if any)
<PROJECT-SPECIFIC SECRET BOOTSTRAP — often ./scripts/generate-secret.sh <name>>

# 3. Bring up the stack (if any)
<PROJECT-SPECIFIC LOCAL-STACK COMMAND — often docker compose up -d>
```

### Everyday commands

<LIST THE HANDFUL OF COMMANDS A DEVELOPER USES DAILY. Examples:>

| What                          | How                                     |
|-------------------------------|-----------------------------------------|
| Run unit tests                | `<command>`                             |
| Run integration tests         | `<command>`                             |
| Run E2E tests                 | `<command>`                             |
| Build deployment image        | `<command>`                             |
| Deploy to <stage / prod>      | `<command>`                             |

## Repository layout

```
<project-root>/
├── .claude/                   Claude Code config (symlinks into agentic/)
├── agentic/                   Shared agent content (guides, skills, scripts, agents, hooks)
├── docs/                      Project docs: requirements, design artefacts, playbooks
│   ├── backlog.md             The enumerated work (per backlog-structure.md)
│   ├── tasks/                 Per-task artefacts (<TASK-ID>.md → .complete.md)
│   └── sprints/               Per-sprint logs and coverage summaries
├── scripts/                   Project-specific operator scripts
├── <source directories>       <e.g. src/, frontend/, etc.>
├── CLAUDE.md                  Agent bootstrap — read this first
└── README.md                  This file
```

## Workflow

This project uses the organisation-wide
[SDLC workflow](agentic/guides/sdlc-workflow-guide.md): interactive
sprint-planning → unattended implementation with stop-and-ask triggers →
interactive sprint-review. See the guide for the full cadence,
artefacts, and the skill / subagent inventory.

## Documentation

- [CLAUDE.md](CLAUDE.md) — agent operating principles and workflow entry
- [docs/requirements.md](docs/requirements.md) — product requirements
- [docs/data-model.md](docs/data-model.md) — schema and invariants
- [docs/infrastructure-design.md](docs/infrastructure-design.md) — deployment topology
- [docs/system-design.md](docs/system-design.md) — application architecture
- [docs/deployment-plan.md](docs/deployment-plan.md) — ops and release procedures
- [docs/backlog.md](docs/backlog.md) — enumerated work

## License

<LICENSE NAME OR "Proprietary — internal use only">
