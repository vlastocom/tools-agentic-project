---
name: task-planning
description: Use this skill to manually run the task-planner subagent on a single task. Escape hatch around `/sprint-planning`'s Phase 3.
---

# /task-planning

Manually invoke the `task-planner` subagent on a single task.

This is an **escape hatch**. Under the SDLC workflow (see
[sdlc-workflow-guide.md §5.1](../../guides/sdlc-workflow-guide.md#51-sprint-planning--interactive-main-conversation)),
task planning normally runs as Phase 3 of `/sprint-planning`. Use this
skill when you want to:

- Re-plan a specific task whose plan turned out wrong (e.g. after
  operator feedback that came outside the normal flow).
- Re-plan a single task whose context changed mid-sprint (a dependency
  got rescoped).
- Test the planner subagent in isolation.
- Plan an out-of-band task (one created during sprint review or as a
  rework dependency).

## Pre-flight

1. Identify the `<TASK-ID>`. Confirm:
   - The task exists in `docs/backlog.md` with a clear Description and
     Requirements Reference (i.e. it has been groomed; if not, run
     `/sprint-planning` Phase 2 grooming on it first or invoke a
     `task-groomer` subagent manually).
   - `docs/tasks/<TASK-ID>.md` either does not exist yet, or its
     `## Plan` is the section you intend to replace.
2. Confirm `agentic/agents/task-planner.md` exists.

## Invocation

Spawn the planner with `isolation: "worktree"`:

```
Agent(
    subagent_type: "task-planner",
    isolation: "worktree",
    prompt: "Produce the ## Plan section for task <TASK-ID> in
             docs/tasks/<TASK-ID>.md per agentic/agents/task-planner.md.
             Apply the widest-flow rule for the E2E directive in Test
             Strategy. Stop and ask only on design choices the docs
             cannot resolve.
             [If re-planning: append context — what about the previous
              plan was wrong, what direction to take instead.]"
)
```

## On return

- **Clean** — `docs/tasks/<TASK-ID>.md` has a `## Plan` section. Present
  to operator for approval.
- **BLOCKED** — task doc has an `## Open questions` section. Surface to
  operator, capture answer in `## Decisions`, re-invoke.

## What this skill is not

- Not a replacement for `/sprint-planning`. If you're starting a new
  sprint, run that — it does grooming + planning + sprint-state setup
  for the whole task set in batch.
- Not a sub-step of `/sprint-implementation`. The orchestrator does
  not re-plan tasks mid-sprint; if the implementer needs a re-plan,
  it stops and asks the operator, who then invokes this skill.

## See also

- [SDLC workflow guide §5.1](../../guides/sdlc-workflow-guide.md#51-sprint-planning--interactive-main-conversation)
- Subagent definition: `agentic/agents/task-planner.md`
- Previous step: `/sprint-planning` (the normal context)
- Next step: `/task-implementation` (or `/sprint-implementation` if
  the orchestrator should pick this up)
