---
name: e2e-testing
description: Use this skill to manually run the e2e-tester subagent on a single task. Escape hatch around the `/sprint-implementation` per-task pipeline. Honours the widest-flow rule.
---

# /e2e-testing

Manually invoke the `e2e-tester` subagent on a single task.

This is an **escape hatch**. Under the SDLC workflow (see
[sdlc-workflow-guide.md §5.2](../../guides/sdlc-workflow-guide.md#52-sprint-implementation--unattended-orchestrator)),
E2E testing normally runs as the third step of the per-task pipeline
inside `/sprint-implementation`, after integration tests pass. Use this
skill when you want to:

- Re-run E2E for a task after a redirect or fix.
- Add or update an E2E flow for a task that was implemented out of band.
- Test the e2e-tester subagent in isolation.

## Pre-flight

1. Identify the `<TASK-ID>`. Confirm:
   - The task has an approved plan in `docs/tasks/<TASK-ID>.md` with
     `## Plan → ### Test Strategy → E2E directive` filled in (one of
     **extend** / **branch** / **write-new** / **no E2E phase**).
   - Integration tests are green for this task.
   - `agentic/agents/e2e-tester.md` exists.
   - `scripts/setup-worktree.sh` exists in the project root.
2. If the directive is **no E2E phase**, this skill should not run —
   the planner already determined no UI flow exists or is touched.

## Invocation

```
Agent(
    subagent_type: "e2e-tester",
    isolation: "worktree",
    prompt: "Before any other work, run `bash scripts/setup-worktree.sh`.
             If it errors or doesn't exist, stop. Then exercise the
             E2E flow for task <TASK-ID> per the directive in
             docs/tasks/<TASK-ID>.md (## Plan → ### Test Strategy → E2E
             directive). Apply the widest-flow rule per SDLC §6.5 —
             extend an existing widest-flow spec wherever the user
             journey already passes through this code. Follow the
             rules in agentic/agents/e2e-tester.md."
)
```

## On return

- **Clean** — task doc updated with `## Test outcomes → E2E` (specs
  run, durations, pass/fail). Next: run `/code-reviewing <TASK-ID>` (or
  hand back to the orchestrator).
- **BLOCKED** — open question, environment failure, or persistent
  flake surfaced in the task doc. Surface to operator, capture answer
  or fix, re-invoke.

## Reminders the e2e-tester subagent enforces

The agent definition is the authoritative spec; this is a quick
reminder of what it is contractually held to:

- **Widest-flow rule.** Prefer extending an existing E2E spec that
  already touches the same user journey. Branch only if the existing
  spec would become unwieldy. Write a new spec only as last resort.
- **Persistent side effects > transient UI elements.** Verify the
  durable state change (row in a table, form reset) rather than a
  Snackbar that auto-hides.
- **Scope locators to containers** when overlapping text exists
  (dialog vs. background grid).
- **Clean up stale state at the start** of mutating tests; do not
  assume a pristine database.
- **Stop and ask** on the five triggers per [SDLC §7](../../guides/sdlc-workflow-guide.md#7-stop-and-ask-contract-detailed).

## See also

- [Testing guide](../../guides/testing-guide.md)
- [SDLC workflow guide §5.2, §6.5 (widest-flow), §7](../../guides/sdlc-workflow-guide.md)
- Subagent definition: `agentic/agents/e2e-tester.md`
- Previous step: `/integration-testing`
- Next step: `/code-reviewing`
