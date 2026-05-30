# agentic-project

Software-development SDLC toolkit for projects assisted by Claude Code.

## What this is

`agentic-project` is a reusable scaffold that gives a software project a
three-mode SDLC workflow (plan / implement / review), a backlog and task
taxonomy, subagent definitions and a library of skills for sprint-driven
development. Drop it into a new project to inherit the workflow without
re-deriving it from scratch.

Battle-tested in: [nest](../../finance/nest), [taskdb](../taskdb).

Sister toolkit: [agentic-team](../agentic-team) — Slack-driven daemon
agents for operations-style work (PA, bookkeeping, multi-agent teams).
Both consume the same Claude Code harness.

## Consuming this toolkit

When starting a new project that should use this SDLC, copy the two
template files into the new repo:

- [templates/project-README.md](templates/project-README.md) — replace
  the placeholders and rename to `README.md` at the consumer's root
- [templates/project-CLAUDE.md](templates/project-CLAUDE.md) — same,
  rename to `CLAUDE.md`

Then symlink the toolkit's `agentic/` subtrees into the consumer's
`.claude/` via [`.claude/setup_claude_dir.sh`](.claude/setup_claude_dir.sh).

## Repository layout

```
agentic-project/
├── agentic/
│   ├── guides/         Shared doctrine (SDLC, testing, layout, ...)
│   ├── skills/         Sprint / task / backlog / testing skills
│   ├── agents/         Subagent definitions (groomer, planner, ...)
│   ├── scripts/        Shared scripts (e.g. setup-worktree.sh)
│   └── hooks/          Hook templates
├── templates/          Files consumers copy at adoption time
└── .claude/            Symlinks into agentic/
```

## Developing the toolkit itself

See [CLAUDE.md](CLAUDE.md) for the operating principles when working on
the toolkit directly (as opposed to working on a consumer project).

## Status

Battle-hardened in nest and taskdb. Skills, guides and the SDLC workflow
are stable. New skills and guides are added as patterns prove themselves
in real projects.

## Planned additions

- **Headless inspection gate in `/sprint-review`** —
  [Qodana](https://www.jetbrains.com/qodana/) wired as a once-per-sprint
  static-analysis pass, with SARIF + HTML report living alongside the
  per-sprint coverage summary. Closes the gap where IntelliJ-only
  inspections (`DataFlowIssue`, `ThrowableNotThrown`,
  `SameParameterValue`, override-contract weakening, etc.) currently
  only surface in the operator's IDE and are invisible to the
  orchestrator agent. Patterned in taskdb (OPS-10-0001); the generic
  skill + guide updates fold back here once the taskdb-side
  implementation is settled.
- _(Future entries land here when a consumer project prototypes a
  cross-cutting pattern worth promoting back.)_
