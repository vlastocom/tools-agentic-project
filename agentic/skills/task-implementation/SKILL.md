---
name: task-implementation
description: Use this skill to manually run the task-implementer subagent on a single task. Escape hatch around the `/sprint-implementation` per-task pipeline.
---

# /task-implementation

Manually invoke the `task-implementer` subagent on a single task.

This is an **escape hatch**. Under the SDLC workflow (see
[sdlc-workflow-guide.md §5.2](../../guides/sdlc-workflow-guide.md#52-sprint-implementation--unattended-orchestrator)),
task implementation normally runs as the first step of the per-task
pipeline inside `/sprint-implementation`. Use this skill when you want
to:

- Re-run the implementer on a task whose first pass was off-track
  (after operator redirect).
- Implement a task without invoking the full orchestrator (e.g.
  out-of-band task added during sprint review).
- Test the implementer subagent in isolation.

## Pre-flight

1. Identify the `<TASK-ID>`. Confirm:
   - The task has an approved plan in `docs/tasks/<TASK-ID>.md` with a
     `## Plan` section (created by `/task-planning` or
     `/sprint-planning` Phase 3).
   - `scripts/setup-worktree.sh` exists in the project root.
   - `agentic/agents/task-implementer.md` exists.
2. Update the backlog row's Status to `DOING` and Start date to today
   (UTC) before dispatching — these belong with the start of work, not
   with the agent itself.

## Invocation

Spawn the implementer with `isolation: "worktree"`:

```
Agent(
    subagent_type: "task-implementer",
    isolation: "worktree",
    prompt: "Before any other work, run `bash scripts/setup-worktree.sh`.
             If it errors or doesn't exist, stop. Then implement task
             <TASK-ID> per the plan in docs/tasks/<TASK-ID>.md. Follow
             the rules in agentic/agents/task-implementer.md, including
             TDD for any task with testable behaviour, and the five
             stop-and-ask triggers.
             [If re-running for must-fix: append the must-fix list
              from the prior `## Review notes`.]"
)
```

## On return

- **Clean** — task doc updated with `## Progress log`, `## Decisions`,
  `## Deviations`. Code changes in the worktree. Next: run
  `/integration-testing <TASK-ID>` (or hand back to the orchestrator).
- **BLOCKED** — open question in the task doc. Surface to operator,
  capture answer, re-invoke.

## Reminders the implementer subagent enforces

The agent definition is the authoritative spec; this is a quick
reminder of what it is contractually held to:

- **TDD-first** for every BUG / FEATURE / TECHNICAL-with-testable-
  behaviour task (see [SDLC §6](../../guides/sdlc-workflow-guide.md#6-tdd-rule)).
  Exempt: pure scaffolding / config / tooling.
- **Never ignore test signals.** Failed tests, failing test setups,
  warning lines on stderr (Apollo `Missing field`, React `act()`,
  jsdom `Not implemented`) are all evidence — read the stack trace,
  form a hypothesis, root-cause before re-running.
- **Boy Scout Rule** in scope only. Tidy what you touch; file a
  CLEANUP backlog task for anything bigger.
- **Stop and ask** on the five triggers (decision points, 3+ rounds
  no progress, uncertainty, major plan deviation, unrelated broken
  thing) per [SDLC §7](../../guides/sdlc-workflow-guide.md#7-stop-and-ask-contract-detailed).

## See also

- [SDLC workflow guide §5.2, §6, §7](../../guides/sdlc-workflow-guide.md)
- Subagent definition: `agentic/agents/task-implementer.md`
- Previous step: `/task-planning`
- Next step: `/integration-testing`, then `/e2e-testing`, then
  `/code-reviewing`, then `/task-wrapup` — or hand control back to
  `/sprint-implementation` to drive the rest of the pipeline.
