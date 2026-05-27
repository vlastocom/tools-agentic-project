# Working on the agentic-project toolkit

This repo IS the toolkit. Changes here propagate to consumers via copy at
adoption time (no automatic sync today — see TODO under "Open problems"
below).

## Mission

Provide a generic, reusable SDLC scaffold for software projects that use
Claude Code. Keep it generic; project-specific bits belong in the
consumer.

## Operating principles

1. **Generic-only.** A change to a guide, skill or subagent here must
   serve at least two consumers (current or anticipated). Project-specific
   variants live in the consumer.
2. **Templates are self-explanatory.** Files under `templates/` are what
   consumers receive at adoption. Anyone who reads them cold must be able
   to fill the placeholders without further instructions.
3. **Follow the [spelling and grammar rules](agentic/guides/spelling-and-grammar-rules.md).**
4. **Markdown edits**: follow the [md-file-editing](agentic/skills/md-file-editing/SKILL.md) skill.
5. **Commits require operator review.** Present the commit message and
   wait for explicit approval before running `git commit`.

## Sister toolkit

[agentic-team](../agentic-team) — Slack-driven daemon agents for
operations-style work. If your change here might affect both toolkits
(e.g. a shared guide or a common skill), check both before changing.

## Open problems

- **Propagation back to consumers.** Today a skill or guide change here
  is copied manually into each consumer. A reconciliation tool is its
  own project; see notes in `agentic-team` design docs once they land.

## Workflow

This toolkit doesn't run its own SDLC — changes are small, incremental
and operator-driven. For each change:

1. Identify which guide / skill / template is affected.
2. Make the change.
3. If it affects an existing consumer, note the consumer in the commit
   message so the operator knows where to manually reconcile.
4. Present the commit message for approval, then commit.
