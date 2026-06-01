# Skills overview

This guide describes the available skills, their purpose and how they relate to each other.

Skills are defined in `agentic/skills/` and symlinked from `.claude/skills/`.
They are invoked with `/<skill-name>` (e.g. `/task-planning`).

## Skill inventory

| Skill                                                         | Purpose                                                         |
|---------------------------------------------------------------|-----------------------------------------------------------------|
| [task-planning](../skills/task-planning/SKILL.md)             | Plan a task, document in `docs/tasks/`, wait for approval       |
| [task-implementation](../skills/task-implementation/SKILL.md) | Implement the code with unit tests, pause for review            |
| [unit-testing](../skills/unit-testing/SKILL.md)               | Write and run unit tests (Vitest / JUnit)                       |
| [integration-testing](../skills/integration-testing/SKILL.md) | Write and run integration tests, pause for review               |
| [e2e-testing](../skills/e2e-testing/SKILL.md)                 | Write and run Playwright E2E tests, pause for review            |
| [task-wrapup](../skills/task-wrapup/SKILL.md)                 | Update documentation, backlog and commit with approval          |
| [backlog-management](../skills/backlog-management/SKILL.md)   | Add, update or remove backlog items (tasks, epics, areas)       |
| [backlog-grooming](../skills/backlog-grooming/SKILL.md)       | Groom the backlog or a specific epic                            |
| [backlog-validation](../skills/backlog-validation/SKILL.md)   | Validate backlog structure, consistency and document links      |
| [backlog-reporting](../skills/backlog-reporting/SKILL.md)     | Generate backlog statistics (text or JSON)                      |
| [backlog-review](../skills/backlog-review/SKILL.md)           | Show the prioritised top of the backlog                         |
| [sprint-planning](../skills/sprint-planning/SKILL.md)         | Plan a new sprint                                               |
| [sprint-start](../skills/sprint-start/SKILL.md)               | Start a planned sprint                                          |
| [sprint-management](../skills/sprint-management/SKILL.md)     | Add or remove tasks from a sprint                               |
| [sprint-close](../skills/sprint-close/SKILL.md)               | Close an open sprint                                            |
| [code-reviewing](../skills/code-reviewing/SKILL.md)           | Review code changes for quality, security and best practices    |
| [codebase-stats](../skills/codebase-stats/SKILL.md)           | Report LOC by language plus backend and frontend test coverage  |
| [estimation](../skills/estimation/SKILL.md)                   | Estimate or re-estimate task, epic or sprint duration           |
| [git-push](../skills/git-push/SKILL.md)                       | Push changes to a remote repository                             |
| [kit-reconciliation](../skills/kit-reconciliation/SKILL.md)   | Diff a consumer project's agentic kit against this template; produce classified findings |
| [md-file-editing](../skills/md-file-editing/SKILL.md)         | Enforce Markdown formatting, spelling and link validation rules |

## Workflows

Workflows are defined in [CLAUDE.md](../../CLAUDE.md) and chain skills together.

### Task implementation workflow

```
task-planning ──► task-implementation ──► integration-testing ──► e2e-testing ──► task-wrapup
                        │                                                            │
                        ▼                                                            ▼
                   unit-testing                                              backlog-management
                                                                             backlog-validation
                                                                               md-file-editing
```

### Backlog grooming workflow

```
backlog-grooming ──► backlog-management ──► backlog-validation
```

## Skill dependencies

The diagram below shows which skills invoke or reference other skills.

```
task-planning ─────────────► task-implementation
task-implementation ───────► unit-testing, integration-testing, e2e-testing, task-wrapup
task-wrapup ───────────────► backlog-management, backlog-validation, md-file-editing

backlog-management ────────► backlog-validation, md-file-editing
backlog-grooming ──────────► backlog-management
backlog-validation           (standalone — no downstream skills)
backlog-reporting            (standalone — no downstream skills)
backlog-review               (standalone — no downstream skills)

sprint-planning ───────────► backlog-management, backlog-validation, md-file-editing,
                             sprint-start, sprint-close, sprint-management
sprint-start ──────────────► backlog-management, backlog-validation, md-file-editing
sprint-management ─────────► backlog-management, backlog-validation, md-file-editing,
                             estimation, sprint-start, sprint-close
sprint-close ──────────────► backlog-management, backlog-validation, md-file-editing,
                             sprint-management

estimation ────────────────► backlog-management, backlog-validation, md-file-editing,
                             sprint-management

code-reviewing ────────────► codebase-stats
codebase-stats               (standalone — no downstream skills)
git-push                     (standalone — no downstream skills)
md-file-editing              (standalone — no downstream skills)
```

## Adding a new skill

1. Create a directory under `agentic/skills/<skill-name>/`
2. Add a `SKILL.md` file with frontmatter (`name`, `description`) and the skill body
3. The skill is automatically available via the `.claude/skills` symlink
4. Add a References section listing relevant guides and related skills
5. If the skill is part of a workflow, update [CLAUDE.md](../../CLAUDE.md)
6. Update this guide
