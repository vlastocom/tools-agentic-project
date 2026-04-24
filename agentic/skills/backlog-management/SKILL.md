---
name: backlog-management
description: Use this skill when asked to add, update, remove or review any backlog items (sprints, tasks, epics, areas)
---

# Backlog Management Guidelines

## Core Principles

- Use a hierarchical structure: **Areas** → **Epics** → **Tasks**
- Tasks are organised in **Sprints** — sprints can contain tasks from multiple epics and areas
- Maintain specific status values (`GROOM`, `TODO`, `DOING`, `DONE`, `DROP`) and priorities (`CRITICAL`, `HIGH`, etc.)
- Follow the strict `backlog.md` structure defined in the [backlog structure guide](../../guides/backlog-structure.md)
- ALWAYS update the "Last Updated" date in the top section of the file when making changes
- ALWAYS validate with `/backlog-validation` before committing changes

## What to update where

| Operation                       | Tasks table | Task Details |
|---------------------------------|:-----------:|:------------:|
| Adding a new task               |     Yes     |     Yes      |
| Updating status, priority, type |     Yes     |      No      |
| Updating sprint assignment      |     Yes     |      No      |
| Updating estimated duration     |     Yes     |      No      |
| Adding/updating description     |     No      |     Yes      |
| Adding/updating dependencies    |     No      |     Yes      |
| Adding documentation link       |     No      |     Yes      |
| Updating start/end dates        |     No      |     Yes      |
| Reordering tasks                |     Yes     |     Yes      |

## Adding backlog items

When adding a new task, epic or area:

1. ALWAYS document all mandatory fields as specified in the [backlog structure guide](../../guides/backlog-structure.md) — ask for clarification if any information is missing
2. ALWAYS check the rest of the backlog for similar or duplicate items — if found, present them and confirm whether a new item is necessary
3. Append the item at the appropriate location (area, epic, end of the task list for that epic)
4. ALWAYS identify gaps between the intent, documented requirements and existing items — suggest additions or updates for review
5. Use `/backlog-validation` to check the consistency of changes and fix any issues
6. Wait for the changes to be reviewed and approved
7. Once approved, commit and push

- **Before committing any backlog changes**, you **must**:
    - Run `/backlog-validation`
    - Check table formatting with `python agentic/scripts/check_md_tables.py docs/backlog.md`
      (or auto-fix with `python agentic/scripts/format_md_tables.py docs/backlog.md`)
    - Update the "Last Updated" date in the header
    - Check for spelling and grammar errors (see [spelling and grammar rules](../../guides/spelling-and-grammar-rules.md))

## References

- [The backlog](../../../docs/backlog.md)
- [Backlog structure guide](../../guides/backlog-structure.md)
- [Spelling and grammar rules](../../guides/spelling-and-grammar-rules.md)
- Validation: `/backlog-validation`
- Markdown editing: `/md-file-editing`
- Sprint changes: `/sprint-planning`, `/sprint-management`, `/sprint-start`, `/sprint-close`
