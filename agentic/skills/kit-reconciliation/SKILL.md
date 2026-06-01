---
name: kit-reconciliation
description: Compare another project's agentic kit (agents, guides, skills, scripts, gitignore patterns, CLAUDE.md/README templates) against this template's kit. Produce a categorised, itemised findings report classifying each drift as template→project catch-up, project→template backport, project-specific keep, or misfiled. Use before a periodic sync of an existing consumer project, or whenever the operator suspects drift in either direction.
---

# Kit reconciliation

You are running a **drift audit** between this template (the
agentic-project repo) and another consumer project that previously
adopted this template by copy. Your output is a single Markdown report
with classified, ID-tagged findings the operator can act on.

This skill does **not** apply fixes. Reconciliation actions
(backporting, syncing, relocating) are subsequent operator decisions
that happen as their own work items, not silently inside this skill.

Read [kit-reconciliation-guide.md](../../guides/kit-reconciliation-guide.md)
in full before starting. The contract below is the operational form of
that guide.

## Pre-flight

Refuse to start unless **all** of the following are true:

1. You know the **template repo path** — typically the repo you are
   running this skill from. Confirm with the operator if ambiguous.
2. You know the **consumer project path(s)** — one path per project to
   reconcile. The operator passes these as arguments to the skill, or
   names them interactively.
3. Both paths are readable filesystem trees (not URLs, not remotes).
4. Each consumer has a recognisable `agentic/` directory at its root.
   If not, the project does not follow this template's pattern and
   reconciliation does not apply — stop and surface that fact.

## The kit inventory

These are the paths considered part of "the kit" for comparison
purposes. Anything **outside** this list is treated as project-owned
content and is not part of the reconciliation.

| Path                                   | Comparison mode                                                                 |
|----------------------------------------|---------------------------------------------------------------------------------|
| `agentic/agents/*.md`                  | Per-file diff. README list-of-agents is also diffed.                           |
| `agentic/guides/*.md`                  | Per-file diff. Sub-directories below `guides/` are diffed recursively.          |
| `agentic/skills/*/SKILL.md`            | Per-file diff at the SKILL.md level.                                            |
| `agentic/scripts/*.py`, `*.sh`         | Per-file diff. Ignore `__pycache__/`.                                           |
| `agentic/hooks/*`                      | Per-file diff (typically thin).                                                 |
| `scripts/setup-worktree.sh`            | Diff against template's reference script.                                       |
| `templates/project-CLAUDE.md`          | Diff against the consumer's actual `CLAUDE.md` (special case — see §"Consumer-template files"). |
| `templates/project-README.md`          | Diff against the consumer's actual `README.md` (same special case).             |
| `.claudeignore`                        | Diff at the file level.                                                         |
| `.gitignore`                           | Diff only the **agentic-kit-relevant blocks** (`.claude/*`, `.secrets/*`, `.claude/worktrees/`); ignore project-specific blocks. |

The `docs/` directory is NEVER compared at the file level — its
content is project-owned by design. But `docs/` IS scanned for
**misfiled** doctrine: consumer files under `docs/guides/` that have
a same-named (or substantively-same-content) sibling in template's
`agentic/guides/` are flagged as misfiled (Finding category F.D —
see classification scheme).

### Consumer-template files

`templates/project-CLAUDE.md` and `templates/project-README.md` are
*not* expected to be copied verbatim into a consumer — they're scaffolds
with `<PLACEHOLDER>` text that get filled in at adoption. So the
comparison is **structural**, not textual:

- Find the consumer's `CLAUDE.md` (or `README.md`) at the consumer
  root.
- Compare the **Operating principles list**, **Workflow section**,
  and **References to agentic/guides/*** between the two.
- A consumer principle that's missing from the template's scaffold
  but present in the consumer's actual file is a **backport candidate**
  iff it's generic (e.g. F002 in this conversation's worked example).
- A scaffold principle that's missing from the consumer's actual file
  is a **catch-up candidate**.

## Procedure

### Step 1 — Inventory both sides

For each kit path category in the table above, list every file present
in the template and every file present in the consumer. Build four
sets:

- `BOTH` — file present in both
- `TEMPLATE_ONLY` — file only in template
- `CONSUMER_ONLY` — file only in consumer
- `MISFILED` — `docs/guides/<X>` in consumer where template has
  `agentic/guides/<X>` (or content-substantively-matching X)

### Step 2 — Diff every BOTH file

For each file in `BOTH`, run:

```bash
diff -u <template-path> <consumer-path>
```

Capture which sections / lines differ. Note timestamps when relevant
(an older mtime in the consumer is a weak signal it's behind; a newer
mtime is a weak signal it's ahead).

### Step 3 — Classify every difference

For each diff (or for each MISSING / CONSUMER_ONLY file), assign one
of these categories:

| Category               | Meaning                                                                            | Resulting action                                            |
|------------------------|------------------------------------------------------------------------------------|-------------------------------------------------------------|
| **CATCH-UP**           | Template has content the consumer is missing (CONSUMER older, or file missing).    | Consumer should pull from template.                         |
| **BACKPORT**           | Consumer has substantive additions that look **generic** — useful to other projects too. | Consumer's change should be backported to template.         |
| **PROJECT-SPECIFIC**   | Consumer differs but the difference is clearly project-bound (project name, project-specific tech, project-specific values). | Keep in consumer; not a backport.                           |
| **MISFILED-IN-CONSUMER** | Doctrine file lives under `docs/` in the consumer but `agentic/guides/` in template. | Relocate inside the consumer; potentially also a CATCH-UP for the template-current version. |
| **MISFILED-IN-TEMPLATE** | Project-specific content lives under `agentic/` in the consumer but should be in `docs/`. | Relocate inside the consumer.                               |
| **EXTRA-IN-CONSUMER**  | File exists only in the consumer's `agentic/`. Investigate per Step 4.             | Either BACKPORT, mark PROJECT-SPECIFIC, or recognise as in-flight WIP. |
| **STRUCTURAL-MISMATCH** | The repo structure itself differs (e.g. missing `.claude/guides` symlink, missing `agentic/agents/` content, no `templates/` directory). | Surface as a top-level structural finding before any per-file work. |

The classification is a judgement call. Document the reasoning
inline with each finding (one short sentence). When uncertain, mark
the finding "needs operator triage" and let the operator decide.

### Step 4 — Genericness assessment for BACKPORT and EXTRA-IN-CONSUMER

For every finding tagged BACKPORT or EXTRA-IN-CONSUMER, also assess
**how generic** the change is:

- **Fully generic** — language-agnostic; applies to every project on
  the template. Backport verbatim.
- **Mixed** — partly generic, partly stack-specific. Recommend a
  split: generic core into main file, stack-specific bits into a
  clearly-marked appendix or separate file.
- **Stack-specific (already isolated)** — the change is stack-bound
  (Spring Boot, Vite, etc.) but already lives in a stack-bound guide.
  Backport to template's same stack-bound location.
- **Project-specific** — re-classify as PROJECT-SPECIFIC (no backport).

### Step 5 — Produce the findings report

Write a Markdown file at the path the operator requested (default:
`/tmp/<consumer-name>-reconciliation.md`). Structure:

1. **Orientation** — one-paragraph summary of where the consumer sits
   relative to the template (ahead / behind / mixed / parallel).
2. **Findings table**, grouped by direction:
   - **Section A — BACKPORT** (consumer → template)
   - **Section B — CATCH-UP** (template → consumer)
   - **Section C — PROJECT-SPECIFIC** (no action — recorded so the
     operator knows they were considered)
   - **Section D — MISFILED** (relocate inside consumer)
   - **Section E — EXTRA-IN-CONSUMER** (investigate)
   - **Section F — STRUCTURAL** (top-level mismatches)
3. **Coverage caveat** — list which paths you diffed in detail vs
   skimmed, so the operator knows where additional findings may hide.
4. **Priority guidance** — your recommendation for which findings
   should be acted on first.

Each finding has a stable ID (`F001`, `F002`, …) within the report so
the operator can reference findings in follow-up conversation. IDs
restart at `F001` for each consumer (the reports are per-consumer, not
cumulative).

### Step 6 — Hand back

Return with:

- Path to the report file.
- One-paragraph executive summary (under 100 words).
- Top three findings the operator should look at first, by ID.

Do **not** apply any of the findings. The skill ends here.

## What you do not do

- You do **not** apply backports, catch-ups, relocations, or any other
  reconciliation action. Those are subsequent operator decisions.
- You do **not** diff the consumer's `docs/`, source code, build
  files, or anything outside the kit inventory.
- You do **not** modify any file in either repo — this skill is
  read-only.
- You do **not** assume "newer mtime" means "better" or "older mtime"
  means "should be replaced". File mtimes are advisory only; substance
  decides direction.

## See also

- [kit-reconciliation-guide.md](../../guides/kit-reconciliation-guide.md) —
  the methodology background, classification rationale, anti-patterns
- [sdlc-workflow-guide.md §9](../../guides/sdlc-workflow-guide.md#9-claude--agentic-directory-pattern) —
  the `.claude/` ↔ `agentic/` symlink pattern that defines what "the
  kit" is structurally
- The worked example from the first run of this skill is preserved
  in the repo as the conversation transcript that produced it; future
  runs follow the same format.
