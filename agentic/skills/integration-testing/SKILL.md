---
name: integration-testing
description: Use this skill to manually run the integration-tester subagent on a single task. Escape hatch around the `/sprint-implementation` per-task pipeline.
---

# /integration-testing

Manually invoke the `integration-tester` subagent on a single task.

This is an **escape hatch**. Under the SDLC workflow (see
[sdlc-workflow-guide.md §5.2](../../guides/sdlc-workflow-guide.md#52-sprint-implementation--unattended-orchestrator)),
integration testing normally runs as the second step of the per-task
pipeline inside `/sprint-implementation`, after `task-implementer`
returns clean. Use this skill when you want to:

- Re-run integration tests on a task after a redirect or fix.
- Add or update integration tests for a task that was implemented out
  of band.
- Test the integration-tester subagent in isolation.

## Pre-flight

1. Identify the `<TASK-ID>`. Confirm:
   - The task has an approved plan in `docs/tasks/<TASK-ID>.md` with
     `## Plan → ### Test Strategy → Integration tests` populated.
   - The implementation is in place (either in the main worktree or a
     dedicated task worktree).
   - `agentic/agents/integration-tester.md` exists.
   - `scripts/setup-worktree.sh` exists in the project root.
2. If running outside the orchestrator, decide whether to use a fresh
   worktree (clean baseline) or operate on the existing one. Default to
   `isolation: "worktree"` for parity with the pipeline.

## Invocation

```
Agent(
    subagent_type: "integration-tester",
    isolation: "worktree",
    prompt: "Before any other work, run `bash scripts/setup-worktree.sh`.
             If it errors or doesn't exist, stop. Then run integration
             tests for task <TASK-ID> per the plan in
             docs/tasks/<TASK-ID>.md and the rules in
             agentic/agents/integration-tester.md. Read warnings and
             stderr signals as first-class evidence — do not dismiss
             them as flaky."
)
```

## On return

- **Clean** — task doc updated with `## Test outcomes → Integration`.
  Coverage report path captured. Next: run `/e2e-testing <TASK-ID>` (or
  hand back to the orchestrator).
- **BLOCKED** — open question or persistent failure surfaced in the
  task doc. Surface to operator, capture answer, re-invoke.

## Reminders the integration-tester subagent enforces

The agent definition is the authoritative spec; this is a quick
reminder of what it is contractually held to:

- **Never ignore failed tests.** A failure outside the task's apparent
  scope most likely indicates a side effect introduced by this task.
  Diagnose and fix before proceeding (see [SDLC §5.4.2 — test signals](../../guides/sdlc-workflow-guide.md#542-test-signals)).
- **Read stderr.** Apollo `Missing field`, React `act()`, jsdom
  `Not implemented`, tear-down race messages — each is evidence.
- **Do not weaken assertions** to make a failure go away. Find root
  cause first.
- **Stop and ask** on the five triggers per [SDLC §7](../../guides/sdlc-workflow-guide.md#7-stop-and-ask-contract-detailed).

## See also

- [Testing guide](../../guides/testing-guide.md)
- [SDLC workflow guide §5.2, §5.4.2, §7](../../guides/sdlc-workflow-guide.md)
- Subagent definition: `agentic/agents/integration-tester.md`
- Previous step: `/task-implementation`
- Next step: `/e2e-testing`
