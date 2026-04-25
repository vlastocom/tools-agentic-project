---
name: code-reviewing
description: Use this skill to manually run the code-reviewer subagent on a single task. Escape hatch around the `/sprint-implementation` per-task pipeline. Produces the `## Review notes` block with must-fix / should-fix / consider taxonomy.
---

# /code-reviewing

Manually invoke the `code-reviewer` subagent on a single task.

This is an **escape hatch**. Under the SDLC workflow (see
[sdlc-workflow-guide.md §5.2](../../guides/sdlc-workflow-guide.md#52-sprint-implementation--unattended-orchestrator)
and [§5.4](../../guides/sdlc-workflow-guide.md#54-code-review)),
code review normally runs as the fourth step of the per-task pipeline
inside `/sprint-implementation`, after E2E. Use this skill when you
want to:

- Re-review a task whose first review identified must-fix items that
  have since been addressed (the must-fix loop normally handles this,
  but you can drive it manually).
- Review a task that was implemented out of band.
- Test the code-reviewer subagent in isolation.

## Pre-flight

1. Identify the `<TASK-ID>`. Confirm:
   - The task has an implementation in place and tests are green
     (integration + E2E if applicable).
   - `docs/tasks/<TASK-ID>.md` exists with `## Plan` and
     `## Test outcomes` populated.
   - `agentic/agents/code-reviewer.md` exists.
   - `scripts/setup-worktree.sh` exists in the project root.

## Invocation

```
Agent(
    subagent_type: "code-reviewer",
    isolation: "worktree",
    prompt: "Before any other work, run `bash scripts/setup-worktree.sh`.
             If it errors or doesn't exist, stop. Then review the
             implementation and tests for task <TASK-ID> per the rules
             in agentic/agents/code-reviewer.md. Produce the
             `## Review notes` block in docs/tasks/<TASK-ID>.md using
             the must-fix / should-fix / consider taxonomy from
             SDLC §5.4.3. Include the project-metrics section
             (LOC + coverage table) at the top of the review.
             [If re-reviewing: append context — what the prior must-fix
              items were and a pointer to where they were addressed.]"
)
```

## On return

The code-reviewer writes `## Review notes` into the task doc with a
verdict (`PASS` / `FAIL`) and itemised findings:

- **must-fix** — blocks wrap-up; route through the must-fix loop.
- **should-fix** — defaults to "fix"; skipping requires rationale in
  `## Deviations`.
- **consider** — defaults to "fix"; skipping requires rationale in
  `## Deviations`.

Next steps depending on outcome:

- **PASS, no must-fix** — proceed to `/task-wrapup`.
- **PASS, must-fix items present** — re-invoke `/task-implementation`
  with the must-fix list, then re-invoke this skill. Cap at three
  re-review rounds (fourth round failure → mark task `Failed-out`
  per [SDLC §5.4.4](../../guides/sdlc-workflow-guide.md#544-must-fix-loop-cap)).
- **BLOCKED** — open question or environment problem in the task doc.
  Surface to operator, capture answer, re-invoke.

## Reminders the code-reviewer subagent enforces

The agent definition is the authoritative spec; this is a quick
reminder of what it is contractually held to:

- **Project metrics section first** — LOC + coverage table, before
  findings. The reader sees the size and coverage picture before any
  finding.
- **Test-run signals are first-class** — Vitest `Errors N error(s)`
  lines, timeouts, tear-down races, Apollo / React `act()` / jsdom
  warnings. "Flaky" or "pre-existing" without a CLEANUP backlog
  pointer is not an acceptable disposition.
- **TODOs must reference a backlog task ID.** Otherwise: must-fix or
  file the task.
- **Number findings** (FINDING-1, FINDING-2, …) so subsequent
  conversation can reference them.
- **Stop and ask** on the five triggers per [SDLC §7](../../guides/sdlc-workflow-guide.md#7-stop-and-ask-contract-detailed).

## See also

- [SDLC workflow guide §5.4 — code review](../../guides/sdlc-workflow-guide.md#54-code-review)
- [SDLC workflow guide §5.4.3 — disposition rules](../../guides/sdlc-workflow-guide.md#543-disposition-rules)
- [SDLC workflow guide §5.4.4 — must-fix loop cap](../../guides/sdlc-workflow-guide.md#544-must-fix-loop-cap)
- Subagent definition: `agentic/agents/code-reviewer.md`
- Previous step: `/e2e-testing`
- Next step: `/task-wrapup`
