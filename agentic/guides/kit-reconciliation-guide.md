# Kit reconciliation guide

This guide documents the **methodology** behind the
[kit-reconciliation skill](../skills/kit-reconciliation/SKILL.md): how
to compare this template's agentic kit against a consumer project's
kit, classify the drifts, and produce actionable findings.

The skill itself is the **operational** version (procedure + output
shape). This guide is the **conceptual** version (what counts as
drift, why directionality matters, how to classify edge cases, what
not to do).

## 1. Why this is needed

This template is adopted by consumer projects via **copy at adoption
time** — there is no automatic sync. Once forked, consumers and
template drift in both directions:

- **Template moves forward.** Bug fixes (e.g. setup-worktree SIGPIPE
  hardening), new doctrine (e.g. SDLC §6.2-6.4 test-per-task rules),
  new artefacts (e.g. the `code-quality-checklist.md` guide). Older
  consumers don't see these unless someone pulls them across.
- **Consumers move forward.** Real use surfaces real problems and
  real solutions. A consumer that runs the orchestrator across a
  full sprint discovers that worktrees need to be cleaned up
  immediately after merge, or that a 3-parallel ceiling reads better
  than the dependency graph's permissive default. Those discoveries
  should flow back so the next adopter doesn't re-discover them.

Without reconciliation, the template stagnates and consumers
duplicate effort. Reconciliation is the periodic ritual that keeps
the kit alive.

## 2. What is "the kit"?

The kit is **the set of files a consumer received at adoption from
this template**, plus the structural conventions (symlinks,
directory layout) the template prescribes. Concretely:

```
<consumer-root>/
├── .claude/                        ← symlinks → ../agentic/* (structure)
│   ├── settings.json               ← in-kit (project may have overrides)
│   └── setup_claude_dir.sh         ← in-kit
├── agentic/                        ← in-kit (every file under this is in scope)
│   ├── agents/*.md                 ← in-kit
│   ├── guides/**/*.md              ← in-kit
│   ├── hooks/*                     ← in-kit
│   ├── scripts/*                   ← in-kit
│   └── skills/*/SKILL.md           ← in-kit
├── scripts/setup-worktree.sh       ← in-kit
├── CLAUDE.md                       ← compared against templates/project-CLAUDE.md
├── README.md                       ← compared against templates/project-README.md
├── .claudeignore                   ← in-kit
└── .gitignore                      ← only the agentic-relevant blocks are in-kit
```

**Out of scope** (project-owned, never compared):

- `docs/` and everything under it (except for misfiled doctrine
  detection — see §4.4)
- Source code (`src/`, `<app>-ui/`, etc.)
- Build configuration (`build.gradle`, `package.json`, `vite.config.ts`)
- Docker / deployment artefacts (`docker-compose*.yml`, `Dockerfile`)
- Per-machine state (`.env`, `options.txt`, `.secrets/<value>.txt`)
- IDE config (`.idea/`, `.vscode/`)

The boundary is sharp on purpose: confusing kit-stuff with
project-stuff makes reconciliation noisy and reviewer-hostile.

## 3. Directionality

Every finding has one of two natural flow directions, and
distinguishing them is the most important judgement call in the
methodology.

### 3.1 Template → consumer (CATCH-UP)

The template has content the consumer is missing. The consumer
should pull from the template.

**Diagnostic:** the file (or section) exists in the template, exists
or is missing in the consumer, and the consumer's version is the
older or absent one. Either:

- The file is present in template but absent in consumer (the
  consumer adopted before the file existed).
- The file is present in both but the template's version has additive
  content the consumer's doesn't — and the additive content is
  doctrine-shaped (a new rule, a new section, a new helper) rather
  than a refinement of an existing rule.

**Example:** A consumer forked before the seven subagents existed
under `agentic/agents/`. The template has them; the consumer doesn't.
That's CATCH-UP — copy the agent files across.

### 3.2 Consumer → template (BACKPORT)

The consumer has content the template should absorb. The consumer's
change is something other projects would benefit from.

**Diagnostic:** the change in the consumer is **generic** (or has a
generic core that can be split out from project-specific bits). A
consumer is the natural source for these because real use surfaces
them faster than abstract template design.

Common BACKPORT shapes:

- **Bug fixes** in template-supplied scripts (e.g. setup-worktree
  SIGPIPE).
- **Operational hygiene** discovered the hard way (e.g. worktree
  clean-up after merge — only visible after running many sprints).
- **New doctrine** that consolidates repeated review feedback (e.g.
  the code-quality checklist as a hygiene gate).
- **Tighter contracts** for existing rules (e.g. "all-three-layer
  tests in the originating task; no dedicated test tasks").

**Example:** The consumer has a `code-quality-checklist.md` not in
the template. Most of it is stack-agnostic; some is Java-specific.
BACKPORT, with the recommendation to split into generic body +
Java/Spring appendix.

### 3.3 The two directions interact

A finding can be both CATCH-UP and BACKPORT in different parts of the
same file. The consumer's version may have a generic improvement (to
backport) AND be missing a template-side bug fix (to catch up). The
methodology handles this by classifying **per change**, not per file.

The skill's output table groups by category, not by file, so the
operator sees both halves of such a finding in their natural
sections.

## 4. Classification scheme

Each diff (or each MISSING / CONSUMER_ONLY file) gets one of seven
categories. The skill enforces this enumeration; pick the closest
match and reason inline.

### 4.1 CATCH-UP

Already defined in §3.1. Operator action: pull from template.

### 4.2 BACKPORT

Already defined in §3.2. Operator action: PR into template.

### 4.3 PROJECT-SPECIFIC

The consumer has a real difference but it's plainly project-bound.

Examples:

- A `testing-guide.md` paragraph mentioning the consumer's specific
  framework version or class name.
- A `local-development-environment-guide.md` section describing the
  consumer's specific NAS hostname or port allocation.
- A `backend-code-layout-guide.md` adapted for the consumer's
  particular Spring Boot version.

Operator action: **none.** The finding is recorded so the operator
knows it was considered and explicitly classified as project-specific
(rather than silently missed). PROJECT-SPECIFIC findings sit in their
own section of the report so they're easy to skim past.

### 4.4 MISFILED-IN-CONSUMER

A doctrine file lives under `docs/guides/` in the consumer when the
template's same-purpose file lives under `agentic/guides/`. The
consumer's instance is misfiled because doctrine should live next to
the skills and agents that reference it.

Detection: scan the consumer's `docs/guides/` for files whose name
or content substantively matches a file in template's
`agentic/guides/`. A close name match (`testing-guide.md`,
`date-time-guide.md`) is a strong signal. Content overlap (large
sections matching, similar headings) is a softer signal.

Operator action: **relocate inside the consumer** (move the file from
`docs/guides/` to `agentic/guides/` and update every reference). If
the template's version has evolved past the consumer's, the operator
should resolve to the template version (CATCH-UP) at the same time.

### 4.5 MISFILED-IN-TEMPLATE

The opposite — a project-specific document lives under `agentic/` in
the consumer when it belongs under `docs/`. Examples:

- A consumer's per-project requirements document under
  `agentic/guides/requirements/`.
- A consumer's specific design document accidentally placed under
  `agentic/`.

(Note: project-agnostic requirements **for the agentic tooling
itself** are correctly placed under `agentic/guides/requirements/`.
This is a meta-tooling exception and not the same as a misfiled
project requirements document.)

Operator action: relocate inside the consumer.

### 4.6 EXTRA-IN-CONSUMER

A file exists only in the consumer's `agentic/` — not in the template
and not flagged as misfiled. Three sub-cases:

- **Backport candidate** — the file is a new generic artefact (e.g.
  the consumer originated a `code-quality-checklist.md`). Re-classify
  as BACKPORT.
- **Project-specific** — the file is bespoke to this consumer (e.g.
  a custom skill that only makes sense for this project's domain).
  Re-classify as PROJECT-SPECIFIC.
- **In-flight WIP** — the file is part of work in progress that isn't
  ready to ship anywhere yet (e.g. an `agentic.new/` directory in
  taskdb at one point). Flag for operator decision; usually the right
  action is to either finish-and-promote or delete.

### 4.7 STRUCTURAL-MISMATCH

The repo structure itself differs — not the contents of files but the
layout of directories and symlinks. Examples:

- The consumer is missing the `.claude/guides` symlink.
- The consumer's `agentic/agents/` directory has only a `.gitkeep`
  where the template has seven agent files.
- The consumer has no `templates/` directory but the template does.
- The consumer has no `scripts/setup-worktree.sh`.

Surface these as **top-level findings before any per-file work**.
They often subsume many per-file findings (no point reporting
"agent X is missing" individually when "all agents are missing"
captures it once).

## 5. Genericness assessment

For every BACKPORT or EXTRA-IN-CONSUMER finding, also tag
**genericness**:

| Tag                            | Meaning                                                                                      | Action                                                                                                |
|--------------------------------|----------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| **Fully generic**              | Language- and stack-agnostic. Applies to every project that uses this template.              | Backport verbatim.                                                                                    |
| **Mixed**                      | Partly generic core, partly stack-specific. The split is identifiable.                       | Recommend a split: generic part in main file; stack-specific in clearly-marked appendix or sibling.  |
| **Stack-specific (isolated)**  | The change is stack-bound but already lives in a stack-bound guide / file.                   | Backport to the same stack-bound location in template.                                                |
| **Project-specific**           | The change is bespoke to this consumer's domain or values.                                   | Re-classify as PROJECT-SPECIFIC.                                                                      |

Don't be afraid to recommend a refactor as part of the backport. The
template's authors expect to do work when accepting backports —
that's the price of keeping the kit clean.

## 6. Anti-patterns

Things that look like reconciliation but aren't:

### 6.1 Mtime-driven decisions

Older mtime ≠ outdated. Newer mtime ≠ better. The file system's
timestamps are advisory only; **substance decides direction**. A file
that hasn't been touched in a year may still be the canonical
version; a file that was touched yesterday may be a wrong-direction
edit that should be reverted.

### 6.2 "Just copy the newer one"

Verbatim file replacement is rarely the right reconciliation action.
The consumer's version may have project-specific bits laced through
the doctrine; the template's version may have improvements that
should land but not the consumer's tweaks. Almost every
non-trivial reconciliation is a **merge**, not a copy.

### 6.3 Auto-applying findings

The reconciliation skill is **read-only**. It produces the findings;
the operator decides which to apply, in what order, and with what
adaptations. Auto-application loses the human judgement step that
sorts CATCH-UP from BACKPORT from PROJECT-SPECIFIC.

### 6.4 Reconciliation as silent cleanup

A reconciliation pass that finds nothing is suspicious. If you've
just run it on a long-lived consumer and the report is empty, you've
probably scoped it wrong (skipped a path, used the wrong base
template version) — not "found nothing genuinely drifted."

### 6.5 Conflating kit with project content

The kit is the shared scaffolding. The project's source code, design
docs, backlog and tasks are not part of the kit. Reconciliation
**must not** touch them. If you find yourself diffing
`docs/data-model.md` or `src/main/...`, you've crossed the boundary
— stop.

## 7. When to run reconciliation

- **Before a planned template-pull** — diff first, decide what to
  pull and what to keep, then pull.
- **After a sprint where the consumer evolved kit-shaped doctrine**
  — capture the backport candidates before they get forgotten.
- **When a consumer feels "stale"** — kit symptoms (skill brief
  doesn't match observed behaviour, an agent references a guide that
  doesn't exist) often have kit-drift root causes.
- **Quarterly on every active consumer** as a default cadence,
  unless one of the above already triggered it recently.

## 8. Format conventions for findings reports

Stable across consumers so reports are comparable over time:

- Finding IDs are `F001`, `F002`, … per report. Restart at `F001`
  for each consumer (reports are per-consumer, not cumulative).
- Group findings by **action direction**, not by file. Sections:
  BACKPORT, CATCH-UP, PROJECT-SPECIFIC, MISFILED, EXTRA-IN-CONSUMER,
  STRUCTURAL.
- Every finding has: ID, one-sentence summary, source (which file /
  block), genericness tag (where applicable), and recommended action.
- Always end with a **coverage caveat** listing what was diffed in
  detail vs skimmed, so the next reconciliation pass knows where to
  look harder.

## 9. See also

- [kit-reconciliation/SKILL.md](../skills/kit-reconciliation/SKILL.md) —
  the operational form of this methodology
- [sdlc-workflow-guide.md §9](sdlc-workflow-guide.md#9-claude--agentic-directory-pattern) —
  the `.claude/` ↔ `agentic/` symlink pattern that defines the kit
  structurally
- [skills-overview.md](skills-overview.md) — the canonical skill
  inventory; useful to cross-reference when classifying a consumer's
  skill diffs
