# Backlog structure

The [backlog.md](../../docs/backlog.md) file follows a specific structure that must be maintained when making updates.

## Backlog hierarchy and structure

### Top level: Areas
Areas represent top-level functional blocks of the system's functional breakdown.
You must document the following field for each area in [the backlog](../../docs/backlog.md).
The fields, which are not marked as "(Optional)" are mandatory.

* **Code:** Area code (e.g. AUTH), this is used to compose EPIC and TASK IDs
* **Short name:** 1–5 words describing the area
* **Description:** More detailed description of the area (1–2 paragraphs)

### Middle level: Epics
These represent major features of the system. Before we start working on them.

For grooming purposes, before the work starts a set of high-level requirements should exist 
in the [requirements directory](../../docs/requirements).

You must document the following field for each epic in [the backlog](../../docs/backlog.md).
The fields, which are not marked as "(Optional)" are mandatory.


- **ID:** Epic ID (format: `<AREA>-<2-DIGIT-NUMBER>`, e.g. `AUTH-01`)
   - New epics in the same area will get incremented number (e.g. `AUTH-02` after `AUTH-01`)
- **Short name:** Short name of the epic (1-5 words)
- **Description:** Description of the epic (1-2 paragraphs)
- **Success criteria:** (optional) List of success criteria for the epic, once groomed
- **Requirements reference:** (optional) Link to requirements document (where available)
   - Requirements field may also reference particular chapters in the requirement documents
   - If requirements do not exist, the epic should not yet be considered groomed
- **Estimated duration:** (optional) Estimated duration of the epic in elapsed engineering days

### Leaf level: Tasks
Tasks represent individual user stories and/or technical tasks to be completed as part of the epic.
Document the following fields for each task in [the backlog](../../docs/backlog.md).
The fields, which are not marked as "(Optional)" are mandatory.

- **ID:** <EPIC-ID>-<4-DIGIT-NUMBER>, e.g. `AUTH-01-0001`
   - Tasks in the same epic will get incremented number, e.g. `AUTH-01-0002` after `AUTH-01-0001`
   - The ID also serves as a reference to the epic and, conversely, the area
- **Type:** Type of the task (BUG, TECHNICAL, FEATURE)
- **Priority:** Priority as per the above list of priorities
- **Status:** Status of the task as per the above list of statuses
- **Short name:** A short name of the task (1–10 words)
- **Sprint:** (Optional) ID of the sprint this task is part of
- **Estimated duration:** (Optional) Estimated duration of the task in elapsed engineering days
- **Start date:** (Optional) Date the work on the task started (YYYY-MM-DD)
- **End date:** (Optional) Date the work on the task finished (YYYY-MM-DD)
- **Description:** (Optional) A description of the task (1–2 paragraphs), story elaboration
- **Dependencies:** (Optional) A list of task IDs that this task depends on
- **Documentation:** (Optional) A link to the task documentation (if available), e.g.:
    - [plan](../../docs/tasks/NEST-00-0001.md), or
    - [documentation](../../docs/tasks/AUTH-02-0001.complete.md)

### Sprints
Sprints represent a set of tasks to be completed within a specific time frame.
The fields, which are not marked as "(Optional)" are mandatory.

Each sprint has the following fields:
- **ID:** Sprint ID (format: YYYY-MM-DD - based on the start date of the sprint)
- **Main goal:** A short description of the sprint's main goal (1-2 paragraphs, identifying the main goal)
- **Additional goals:** (optional) A short list of additional goals for the sprint
- **Success criteria:** (optional) A list of criteria to measure the success of the sprint
- **Status:** Sprint status
- **Estimated duration:** Estimated duration of the sprint in elapsed engineering days (summed durations of all tasks in the sprint)
- **Start date:** (optional) The actual start date of the sprint (YYYY-MM-DD)
- **End date:** (optional) The actual end date of the sprint (YYYY-MM-DD)

## Field values used in the backlog

### Sprint status

The following are the possible values for the status field of a sprint:

- PLANNING: A future sprint, which is being prepared
- OPEN: A sprint we currently work on
- CLOSED: A sprint that has been completed. It should not have any incomplete tasks in it.

### Task priority

The following is a descending list of priorities assigned to each task:

- CRITICAL: The task is important for correct functioning of the feature it is related to
- HIGH: Must do
- MEDIUM: Should do (default priority)
- LOW: Nice to have
- UNNECESSARY: Not needed, won't do

### Task status

The following are the possible values for the status field of a task. By default, new tasks should be by default
in the "GROOM" state, until all task fields are clarified.

- GROOM: Task requires more information and/or breaking down into smaller tasks
- TODO: Task is ready to be worked on
- DOING: Task is currently being worked on
- DONE: Task has been completed
- DROP: Task will not be worked on

### Task type

The following are the possible values for the task type field:

- BUG: A defect discovered during development, testing, production or release
- TECHNICAL: A technical task, which does not require user interaction or input
- FEATURE: A user-facing change, requiring either user interaction or input

## Backlog markdown document structure

```markdown
## Sprints

### [Sprint ID] (Sprint entries should be in reverse chronological order, i.e. most recent first)

[Table with fields: ID, Status, Main goal, Additional goals, Success criteria, Estimated duration, Start Date, End Date]

[Repeat for all sprints]

---

## Areas
### Area: <Area Name>
[Table with fields: Code, Short name, Description]

[Repeat for all areas]

---

## Epics
### Epic <EPIC-ID>
[Table with fields: ID, Short name, Description, Success Criteria, Requirements Reference, Estimated Duration]

[Repeat for all epics]

---

## Tasks
[Single consolidated table with all tasks]

Columns: ID | Type | Priority | Short Name | Status | Estimated Duration | Sprint

- ID: Task identifier in format <EPIC-ID>-<4-DIGIT-NUMBER>
- Type: BUG | TECHNICAL | FEATURE
- Priority: CRITICAL | HIGH | MEDIUM | LOW | UNNECESSARY
- Short Name: Brief task description (1-10 words)
- Status: GROOM | TODO | DOING | DONE | DROP
- Estimated duration: Estimated duration of the task in elapsed engineering days
- Sprint: Sprint ID (YYYY-MM-DD) or empty

---

## Task Details
### <EPIC-ID>

#### <TASK-ID>: <Short Name>

[Table with fields: Start Date, End Date, Dependencies (<TASK-ID>, <TASK-ID>, ...), Documentation]

[Detailed task description, which may include subsections like "Current", "Expected", "Scope", "Acceptance Criteria", "Notes", etc.]


[Repeat for all tasks in the epic]

[Repeat epic sections for all epics]
```

### Key Structural Rules

1. **Section Order**: Sprints → Areas → Epics → Tasks → Task Details
2. **Separators**: Use `---` between major sections
3. **Tables**:
   - Sprints, Areas and Epics use Field/Value tables (2 columns)
   - Tasks use a single consolidated table with field columns
   - All tables must have a header row and separator row for proper Markdown rendering
4. **Task Information**:
   - Short fields (ID, Type, Priority, Short Name, Status, Sprint, Estimated Duration) appear ONLY in the Tasks table
   - Long fields (Start date, End date, Description, Dependencies, Documentation, Notes) appear ONLY in the Task Details section
   - Do not repeat fields in both sections
5. **Documentation Links**:
   - Must be relative Markdown links: `[<TASK-ID>.complete.md](tasks/<TASK-ID>.complete.md)`
   - Only present for tasks with actual documentation files
   - Appears in the Task Details Field/Value table, not in the Tasks table
6. **Task Details Organization**:
   - Grouped by epic using `### <EPIC-ID>` headers
   - Each task uses `#### <TASK-ID>: <Short Name>` header
   - Order tasks within epic by task ID (ascending)
7. Sprints
   - Order sprints in a reverse chronological order, i.e. most recent first
   - Sprint IDs are formatted as `YYYY-MM-DD` (representing the first day of the sprint, i.e. should be consistent with the start date field)
   - There should only be one sprint with the OPEN status at any given time
   - More than one sprint may be in the PLANNING status at any given time
   - When moving tasks between sprints, remember to update other sprint fields, in particular the sprint duration
   - Tasks are assigned to sprints by updating the task field "Sprint" with the appropriate sprint ID.
   - Use /sprint-planning skill to plan and maintain sprints
