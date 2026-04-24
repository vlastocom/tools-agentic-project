# Backlog scripts overview

This document describes helper scripts used to manage and report on the backlog.

| Script                | Purpose                                                                            |
|-----------------------|------------------------------------------------------------------------------------|
| `backlog_utils.py`    | Core library — dataclasses, parsers and validators used by all other scripts       |
| `validate_backlog.py` | Validates the structure and consistency of the backlog against the expected format |
| `check_doc_links.py`  | Checks that documentation links in Task Details point to existing files            |
| `backlog_stats.py`    | Generates statistics and reports (text or JSON) about the backlog status           |
| `format_md_tables.py` | Reformats Markdown tables in place so that column widths are consistent            |
| `check_md_tables.py`  | Validates Markdown table formatting without modifying files (read-only)            |

All scripts are in the [agentic/scripts](../scripts) directory.
They require Python 3.8+ and use only standard libraries.
All scripts must be run from the **project root directory**.

---

## backlog_utils.py

**Location:** [agentic/scripts/backlog_utils.py](../scripts/backlog_utils.py)

**Purpose:** Core library that all other backlog scripts depend on.
Provides dataclasses, parsing functions and field validators for the backlog.

**Dataclasses:** `Task`, `Sprint`, `Epic`, `Area`

**Key functions:**

| Function                   | Description                                                           |
|----------------------------|-----------------------------------------------------------------------|
| `read_backlog()`           | Read the backlog file and return its contents as a string             |
| `parse_tasks_table()`      | Parse the Tasks table into a list of `Task` objects                   |
| `parse_task_details()`     | Parse the Task Details section (Field/Value tables + descriptions)    |
| `merge_task_info()`        | Merge table tasks with detail tasks into complete `Task` objects      |
| `parse_sprints()`          | Parse the Sprints section into a list of `Sprint` objects             |
| `parse_epics()`            | Parse the Epics section into a list of `Epic` objects                 |
| `parse_areas()`            | Parse the Areas section into a list of `Area` objects                 |
| `validate_task_id()`       | Check task ID format (`AREA-NN-NNNN`)                                 |
| `validate_status()`        | Check task status is valid (`GROOM`, `TODO`, `DOING`, `DONE`, `DROP`) |
| `validate_task_type()`     | Check task type is valid (`FEATURE`, `TECHNICAL`, `BUG`)              |
| `validate_sprint_id()`     | Check sprint ID format (`YYYY-MM-DD`)                                 |
| `validate_sprint_status()` | Check sprint status (`PLANNING`, `OPEN`, `CLOSED`)                    |

**Usage as a script:** Displays a quick summary of what the parser found.

```
python agentic/scripts/backlog_utils.py
```

**Example output:**

```
Parsed 110 tasks from table
Parsed 110 task details
Parsed 1 sprints
Parsed 15 epics
Parsed 13 areas
```

---

## validate_backlog.py

**Location:** [agentic/scripts/validate_backlog.py](../scripts/validate_backlog.py)

**Purpose:** Validates the backlog structure and data consistency.
Exits with code 0 on success, 1 if errors are found. Warnings do not cause a non-zero exit.

**Usage:**

```
python agentic/scripts/validate_backlog.py
```

**Checks performed:**

| Check                        | Description                                                                    |
|------------------------------|--------------------------------------------------------------------------------|
| Document structure           | Required sections exist (`Sprints`, `Areas`, `Epics`, `Tasks`, `Task Details`) |
| Tasks table format           | Header columns and separator row match the expected 7-column layout            |
| Task ID format               | Every task ID matches `AREA-NN-NNNN`                                           |
| Epic ID format               | Every epic ID matches `AREA-NN`                                                |
| Table vs Details consistency | Every task in the table has a detail section and vice versa                    |
| Statuses and priorities      | All values are from the allowed sets                                           |
| Task types                   | All values are `FEATURE`, `TECHNICAL` or `BUG`                                 |
| Documentation links          | Filenames follow the `<ID>.complete.md` convention and files exist             |
| Duplicate IDs                | No duplicate task or epic IDs                                                  |
| Dependencies                 | Referenced task IDs exist in the table                                         |
| Sprint IDs                   | Follow `YYYY-MM-DD` format                                                     |
| Sprint statuses              | Are `PLANNING`, `OPEN` or `CLOSED`; at most one sprint is `OPEN`               |
| Sprint references            | Tasks referencing a sprint have a matching sprint definition                   |

---

## check_doc_links.py

**Location:** [agentic/scripts/check_doc_links.py](../scripts/check_doc_links.py)

**Purpose:** Verifies documentation links in the backlog are valid and files exist.
Also reports DONE tasks that have no documentation.

**Usage:**

```
python agentic/scripts/check_doc_links.py
```

Exits with code 0 when all checks pass, 1 when issues are found.

**What it checks:**
- Documentation filenames follow the `<ID>.complete.md` convention
- Referenced files exist in `docs/tasks/`
- Every DONE task has a documentation entry (empty documentation on a DONE task is flagged)

---

## backlog_stats.py

**Location:** [agentic/scripts/backlog_stats.py](../scripts/backlog_stats.py)

**Purpose:** Generates statistics and reports about the backlog.

**Usage:**

```
python agentic/scripts/backlog_stats.py              # Human-readable tables
python agentic/scripts/backlog_stats.py --format json # JSON output
```

**Human-readable sections:**

| Section                | Content                                                               |
|------------------------|-----------------------------------------------------------------------|
| Task Status Overview   | Area/epic hierarchy with per-status counts and percentages            |
| Open Tasks by Priority | Same hierarchy filtered to open tasks, broken down by priority        |
| Completion Progress    | Progress bars per area/epic (excludes DROP and LOW priority)          |
| Sprint Summary         | Tasks assigned vs unassigned, per-sprint completion with status label |
| Documentation Coverage | Percentage of DONE tasks with documentation                           |
| Blocked Tasks          | Tasks with unresolved dependencies                                    |

---

## format_md_tables.py

**Location:** [agentic/scripts/format_md_tables.py](../scripts/format_md_tables.py)

**Purpose:** Reformats Markdown tables in place so that every column has a consistent
width. Preserves alignment markers (`:`) in separator rows.

**Usage:**

```
python agentic/scripts/format_md_tables.py docs/backlog.md          # Reformat in place
echo '| a | b |\n|---|---|\n| long value | c |' | python agentic/scripts/format_md_tables.py  # stdin → stdout
```

Exits with code 0 on success, 1 on file read/write errors.

---

## check_md_tables.py

**Location:** [agentic/scripts/check_md_tables.py](../scripts/check_md_tables.py)

**Purpose:** Validates Markdown table formatting without modifying files.
Compares each file against the output of `format_md_tables.format_tables()` and
reports any differences with line numbers.

**Usage:**

```
python agentic/scripts/check_md_tables.py docs/backlog.md
python agentic/scripts/check_md_tables.py docs/*.md
```

Exits with code 0 when all tables are correctly formatted, 1 when issues are found.
