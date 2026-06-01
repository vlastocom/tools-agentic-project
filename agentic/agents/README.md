# Subagent definitions

Per-subagent Markdown files go in this directory. Each file defines one
subagent — name, description, tools, system prompt.

Consult [sdlc-workflow-guide.md §4](../guides/sdlc-workflow-guide.md)
for the expected subagent inventory:

- `task-groomer`
- `task-planner`
- `task-implementer`
- `integration-tester`
- `e2e-tester`
- `code-reviewer`
- `task-wrapper`

Each project may add its own, but these seven are what the SDLC
workflow references directly.

File naming: one `<agent-name>.md` per agent.
