---
name: sprint-planning
description: Use this skill to plan a new sprint. Interactive — you and the operator agree the sprint goal and task set; the skill then runs grooming and planning subagents in parallel, batches operator questions, presents plans for review, and marks the sprint OPEN.
---

# Sprint planning

You are running the **planning phase** of a sprint per
[SDLC workflow guide §5.1](../../guides/sdlc-workflow-guide.md#51-sprint-planning--interactive-main-conversation).
This skill is interactive — the operator is in the conversation with
you. After agreeing the sprint scope, you spawn subagents to do the
grooming and planning work, batch their questions to the operator, and
finalise.

## Pre-flight

Refuse to start unless **all** of the following are true:

1. No sprint is currently `OPEN` in `docs/backlog.md`. (Close the
   previous sprint via `/sprint-review` first.)
2. The seven subagent definitions exist under `agentic/agents/`.
3. The candidate task set has rows in the backlog (sprint planning
   curates from existing tasks; it does not invent them).

## Phase 1 — Sprint goal and task selection (interactive)

1. **Clarify the sprint goal.** Discuss with the operator:
   - **Main goal** (1–2 sentences)
   - **Additional goals** (optional, lower priority)
   - **Success criteria** — derive from the goal, refine
2. **Identify candidate tasks.** From `docs/backlog.md`:
   - Tasks already in `TODO` that contribute to the main goal
   - Their transitive dependencies (recursively, until the dep set is
     closed)
   - Tasks contributing to additional goals + their dependencies
   - Flag any **gaps** — tasks the goal needs but the backlog doesn't
     have yet. Surface them; let the operator decide whether to add
     them or scope the goal narrower.
3. **Estimate the sprint duration.** Sum task estimates; surface tasks
   without estimates (use `/estimation` to fill them).
4. **Present the plan in tabular form** (per [backlog-structure.md](../../guides/backlog-structure.md))
   and grouped by goal:
   - The tasks that achieve the main goal (with their dependencies)
   - One group per additional goal
   Iterate with the operator until they approve.
5. **Write the sprint definition** into `docs/backlog.md` per the
   structure guide. Status `PLANNING`.

## Phase 2 — Grooming (subagents, parallel)

For every task in the agreed sprint, spawn a `task-groomer` subagent in
parallel:

```
Agent(subagent_type: "task-groomer",
      isolation: "worktree",
      prompt: "Groom task <TASK-ID>. Read its row in docs/backlog.md
               and the design docs it references. Confirm or improve
               the Description and Requirements Reference per
               agentic/agents/task-groomer.md. If anything is
               ambiguous, surface it as an Open Question.")
```

Wait for all groomers. Then:

1. **Aggregate operator-questions** from every task doc that has an
   `## Open questions` section.
2. **Present them to the operator in batch** — short, focused.
3. **Apply the operator's answers** to each task doc:
   - If the answer informs grooming (description / requirements
     reference), update the backlog row directly.
   - If the answer is a planning-time decision, leave it in the task
     doc's `## Decisions` for the planner to consume.
4. **Re-spawn `task-groomer`** for any task whose initial groomer
   blocked, now with the answer in `## Decisions`. Repeat until every
   task is in `<!-- GROOMED: ... -->` state.

## Phase 3 — Planning (subagents, parallel)

For every groomed task, spawn a `task-planner` subagent in parallel:

```
Agent(subagent_type: "task-planner",
      isolation: "worktree",
      prompt: "Produce the ## Plan section for task <TASK-ID> in
               docs/tasks/<TASK-ID>.md per agentic/agents/task-planner.md.
               Apply the widest-flow rule for the E2E directive in
               Test Strategy. Stop and ask only on design choices the
               existing docs cannot resolve.")
```

Wait for all planners. Then:

1. **Aggregate any new operator-questions** raised during planning.
   Same batch flow as Phase 2.
2. **Present the plans to the operator** for review. The operator may:
   - Accept all plans → proceed.
   - Redirect specific plans — re-spawn the planner for that task with
     the operator's redirect appended to the prompt.

## Phase 4 — Mark the sprint OPEN (subsumes the old `/sprint-start`)

Once the operator has accepted the plans:

1. Update the sprint's status in `docs/backlog.md` from `PLANNING` to
   `OPEN`.
2. Set the sprint's Start date to today (UTC, `YYYY-MM-DD`).
3. Validate the backlog (`/backlog-validation`).
4. Commit the backlog and task-doc changes with a sensible message
   ("Sprint `<sprint-id>`: open with N tasks, plans approved").
5. Push (or, if the operator prefers, hand back without pushing).
6. Hand back with: "Sprint `<sprint-id>` is OPEN. Tasks: N. Estimated
   duration: D engineering days. Run `/sprint-implementation` to begin."

## What you do not do

- You do **not** code, plan or groom yourself — those are subagent jobs.
- You do **not** invent tasks. If a gap surfaces, the operator decides
  whether to add a backlog task (use `/backlog-management`) and
  recursively re-plan.
- You do **not** start the implementation. That is `/sprint-implementation`.

## Small-task fast path

For tasks estimated at ≤ 0.5 engineering days, grooming and planning
collapse into a single subagent run (the planner does light grooming
implicitly) — **unless** the task is type `BUG`, in which case
grooming is mandatory because the bug-reproduction failing test is
the grooming output (per [SDLC §5.1](../../guides/sdlc-workflow-guide.md#small-task-fast-path)).

## See also

- [SDLC workflow guide §5.1 — sprint planning](../../guides/sdlc-workflow-guide.md#51-sprint-planning--interactive-main-conversation)
- [SDLC workflow guide §6 — TDD rule](../../guides/sdlc-workflow-guide.md#6-tdd-rule)
- [Backlog structure guide](../../guides/backlog-structure.md)
- Subagent definitions: `agentic/agents/{task-groomer,task-planner}.md`
- Manual override: `/sprint-start` (set OPEN by hand if needed —
  bypasses Phase 4 of this skill)
- Adding/removing tasks mid-sprint: `/sprint-management`
- Next step: `/sprint-implementation`
