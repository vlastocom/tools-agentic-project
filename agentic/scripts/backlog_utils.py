#!/usr/bin/env python3
"""
Common utilities for backlog maintenance scripts.

This module provides shared functions for parsing, validating, and manipulating
the backlog.md file.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Project root, resolved from this file's location so scripts work regardless of
# the shell's current working directory. This file lives at
# ``agentic/scripts/backlog_utils.py`` — two parents up is the project root.
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
BACKLOG_PATH: Path = PROJECT_ROOT / 'docs' / 'backlog.md'
TASKS_DIR: Path = PROJECT_ROOT / 'docs' / 'tasks'


@dataclass
class Task:
    """Represents a task from the backlog."""
    task_id: str = ""
    task_type: str = ""
    priority: str = ""
    short_name: str = ""
    status: str = ""
    sprint: str = ""
    est_duration: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""
    dependencies: List[str] = None
    documentation: str = ""
    notes: str = ""

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class Sprint:
    """Represents a sprint from the backlog."""
    sprint_id: str = ""
    status: str = ""
    main_goal: str = ""
    additional_goals: str = ""
    estimated_duration: str = ""
    start_date: str = ""
    end_date: str = ""


@dataclass
class Epic:
    """Represents an epic from the backlog."""
    epic_id: str
    short_name: str
    description: str
    success_criteria: str = ""
    requirements_reference: str = ""


@dataclass
class Area:
    """Represents an area from the backlog."""
    code: str
    short_name: str
    description: str


# Valid values for task fields
VALID_STATUSES = {'GROOM', 'TODO', 'DOING', 'DONE', 'DROP'}
VALID_PRIORITIES = {'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'UNNECESSARY'}
VALID_TASK_TYPES = {'FEATURE', 'TECHNICAL', 'BUG'}
VALID_SPRINT_STATUSES = {'PLANNING', 'OPEN', 'CLOSED'}

# ID format patterns
EPIC_ID_PATTERN = re.compile(r'^[A-Z]+-\d{2}$')
TASK_ID_PATTERN = re.compile(r'^[A-Z]+-\d{2}-\d{4}$')
SPRINT_ID_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def read_backlog(file_path=None) -> str:
    """Read the backlog file and return its contents.

    Defaults to the project's ``docs/backlog.md`` resolved from this module's
    location, so callers do not need to be in the project root. Pass an explicit
    path to override.
    """
    path = Path(file_path) if file_path is not None else BACKLOG_PATH
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_backlog(content: str, file_path=None) -> None:
    """Write content to the backlog file.

    Defaults to the project's ``docs/backlog.md`` resolved from this module's
    location, so callers do not need to be in the project root. Pass an explicit
    path to override.
    """
    path = Path(file_path) if file_path is not None else BACKLOG_PATH
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def extract_section(content: str, section_name: str) -> Optional[str]:
    """
    Extract a major section from the backlog.

    Args:
        content: Full backlog content
        section_name: Name of section (e.g., "Tasks", "Epics")

    Returns:
        Section content or None if not found
    """
    pattern = rf'## {section_name}\n\n(.*?)(?=\n---\n\n##|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    return match.group(1) if match else None


def parse_tasks_table(content: str) -> List[Task]:
    """
    Parse the Tasks table and return list of Task objects.

    Args:
        content: Full backlog content

    Returns:
        List of Task objects from the table
    """
    tasks_section = extract_section(content, 'Tasks')
    if not tasks_section:
        return []

    # Extract table rows (skip header and separator)
    # Use regex that allows variable whitespace padding in header columns
    table_match = re.search(
        r'\|\s*ID\s*\|\s*Type.*?\n\|.*?\n(.*?)(?=\n---|\n\n##|\Z)',
        tasks_section,
        re.DOTALL
    )
    if not table_match:
        return []

    tasks = []
    for line in table_match.group(1).strip().split('\n'):
        if not line.strip():
            continue

        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 7:
            continue

        tasks.append(Task(
            task_id=parts[1],
            task_type=parts[2],
            priority=parts[3],
            short_name=parts[4],
            status=parts[5],
            est_duration=parts[6],
            sprint=parts[7],
        ))

    return tasks


def parse_task_details(content: str) -> Dict[str, Task]:
    """
    Parse Task Details section and return dict of task_id -> Task.

    Args:
        content: Full backlog content

    Returns:
        Dict mapping task IDs to Task objects with detailed info
    """
    details_section_match = re.search(
        r'## Task Details\n\n(.*)',
        content,
        re.DOTALL
    )
    if not details_section_match:
        return {}

    details_content = details_section_match.group(1)
    tasks = {}

    # Find all task detail sections
    task_pattern = r'####\s+([A-Z]+-\d{2}-\d{4}):\s+(.*?)\n\n(.*?)(?=\n####|\n###|\Z)'
    for match in re.finditer(task_pattern, details_content, re.DOTALL):
        task_id = match.group(1)
        short_name = match.group(2).strip()
        detail_text = match.group(3).strip()

        # Parse the Field/Value table
        start_date = ""
        end_date = ""
        dependencies = []
        documentation = ""

        for line in detail_text.split('\n'):
            if '|' not in line or line.startswith('|--') or line.startswith('| Field'):
                continue
            cols = [c.strip() for c in line.split('|')]
            if len(cols) < 3:
                continue
            field = cols[1]
            value = cols[2]
            if '**Start date**' in field:
                start_date = value
            elif '**End date**' in field:
                end_date = value
            elif '**Dependencies**' in field:
                dependencies = [d.strip() for d in re.findall(r'[A-Z]+-\d{2}-\d{4}', value)]
            elif '**Documentation**' in field:
                # Extract filename from markdown link like [file.md](tasks/file.md)
                link_match = re.search(r'\[([^\]]+)\]', value)
                documentation = link_match.group(1) if link_match else value

        # Extract description — prose text after the table
        # Find the last table row or separator, then take everything after it
        description = ""
        in_table = True
        desc_lines = []
        for line in detail_text.split('\n'):
            if in_table:
                if line.startswith('|'):
                    continue
                # First non-table line — switch to description mode
                in_table = False
            desc_lines.append(line)
        description = '\n'.join(desc_lines).strip()

        tasks[task_id] = Task(
            task_id=task_id,
            short_name=short_name,
            start_date=start_date,
            end_date=end_date,
            description=description,
            dependencies=dependencies,
            documentation=documentation,
        )

    return tasks


def merge_task_info(table_tasks: List[Task], detail_tasks: Dict[str, Task]) -> List[Task]:
    """
    Merge task information from table and details sections.

    Args:
        table_tasks: Tasks from the Tasks table
        detail_tasks: Tasks from Task Details section

    Returns:
        List of complete Task objects
    """
    merged = []
    for task in table_tasks:
        if task.task_id in detail_tasks:
            detail = detail_tasks[task.task_id]
            task.start_date = detail.start_date
            task.end_date = detail.end_date
            task.description = detail.description
            task.dependencies = detail.dependencies
            task.documentation = detail.documentation
            task.notes = detail.notes
        merged.append(task)
    return merged


def validate_task_id(task_id: str) -> bool:
    """Check if task ID follows the correct format."""
    return bool(TASK_ID_PATTERN.match(task_id))


def validate_epic_id(epic_id: str) -> bool:
    """Check if epic ID follows the correct format."""
    return bool(EPIC_ID_PATTERN.match(epic_id))


def validate_status(status: str) -> bool:
    """Check if status is valid."""
    return status in VALID_STATUSES


def validate_task_type(task_type: str) -> bool:
    """Check if task ID follows the correct format."""
    return task_type in VALID_TASK_TYPES


def validate_priority(priority: str) -> bool:
    """Check if priority is valid."""
    return priority in VALID_PRIORITIES


def validate_sprint_id(sprint_id: str) -> bool:
    """Check if sprint ID follows the YYYY-MM-DD format."""
    return bool(SPRINT_ID_PATTERN.match(sprint_id))


def validate_sprint_status(status: str) -> bool:
    """Check if sprint status is valid."""
    return status in VALID_SPRINT_STATUSES


def extract_epic_from_task_id(task_id: str) -> str:
    """Extract epic ID from task ID (e.g., 'AUTH-02-0001' -> 'AUTH-02')."""
    parts = task_id.split('-')
    if len(parts) >= 3:
        return f"{parts[0]}-{parts[1]}"
    return ""


def parse_sprints(content: str) -> List[Sprint]:
    """
    Parse Sprints section and return list of Sprint objects.

    Args:
        content: Full backlog content

    Returns:
        List of Sprint objects
    """
    sprints_section = extract_section(content, 'Sprints')
    if not sprints_section:
        return []

    sprints = []
    sprint_pattern = r'### Sprint (\S+)\n\n\| Field\s+\| Value\s+\|(.*?)(?=\n### Sprint|\n---|\Z)'

    for match in re.finditer(sprint_pattern, sprints_section, re.DOTALL):
        sprint_id = match.group(1)
        table_content = match.group(2)

        sprint = Sprint(sprint_id=sprint_id)

        for line in table_content.split('\n'):
            if '|' not in line or line.startswith('|--'):
                continue
            cols = [c.strip() for c in line.split('|')]
            if len(cols) < 3:
                continue
            field = cols[1]
            value = cols[2]
            if '**Status**' in field:
                sprint.status = value
            elif '**Main goal**' in field:
                sprint.main_goal = value
            elif '**Additional goals**' in field:
                sprint.additional_goals = value
            elif '**Estimated duration**' in field:
                sprint.estimated_duration = value
            elif '**Start date**' in field:
                sprint.start_date = value
            elif '**End date**' in field:
                sprint.end_date = value

        sprints.append(sprint)

    return sprints


def parse_epics(content: str) -> List[Epic]:
    """
    Parse Epics section and return list of Epic objects.

    Args:
        content: Full backlog content

    Returns:
        List of Epic objects
    """
    epics_section = extract_section(content, 'Epics')
    if not epics_section:
        return []

    epics = []
    epic_pattern = r'### Epic ([A-Z]+-\d{2})\n\n\| Field\s+\| Value\s+\|(.*?)(?=\n### Epic|\n---|\Z)'

    for match in re.finditer(epic_pattern, epics_section, re.DOTALL):
        epic_id = match.group(1)
        table_content = match.group(2)

        # Extract fields from table
        short_name = ""
        description = ""
        success_criteria = ""
        requirements_ref = ""

        for line in table_content.split('\n'):
            if '**Short name**' in line:
                short_name = line.split('|')[2].strip()
            elif '**Description**' in line:
                description = line.split('|')[2].strip()
            elif '**Success Criteria**' in line or '**Success criteria**' in line:
                success_criteria = line.split('|')[2].strip()
            elif '**Requirements Reference**' in line or '**Requirements reference**' in line:
                requirements_ref = line.split('|')[2].strip()

        epics.append(Epic(
            epic_id=epic_id,
            short_name=short_name,
            description=description,
            success_criteria=success_criteria,
            requirements_reference=requirements_ref
        ))

    return epics


def parse_areas(content: str) -> List[Area]:
    """
    Parse Areas section and return list of Area objects.

    Args:
        content: Full backlog content

    Returns:
        List of Area objects
    """
    areas_section = extract_section(content, 'Areas')
    if not areas_section:
        return []

    areas = []
    area_pattern = r'### Area: (.*?)\n\n\| Field\s+\| Value\s+\|(.*?)(?=\n### Area:|\n---|\Z)'

    for match in re.finditer(area_pattern, areas_section, re.DOTALL):
        area_name = match.group(1).strip()
        table_content = match.group(2)

        code = ""
        short_name = ""
        description = ""

        for line in table_content.split('\n'):
            if '**Code**' in line:
                code = line.split('|')[2].strip()
            elif '**Short name**' in line:
                short_name = line.split('|')[2].strip()
            elif '**Description**' in line:
                description = line.split('|')[2].strip()

        areas.append(Area(
            code=code,
            short_name=short_name,
            description=description
        ))

    return areas


if __name__ == '__main__':
    # Simple test
    content = read_backlog()
    tasks = parse_tasks_table(content)
    print(f"Parsed {len(tasks)} tasks from table")

    details = parse_task_details(content)
    print(f"Parsed {len(details)} task details")

    sprints = parse_sprints(content)
    print(f"Parsed {len(sprints)} sprints")

    epics = parse_epics(content)
    print(f"Parsed {len(epics)} epics")

    areas = parse_areas(content)
    print(f"Parsed {len(areas)} areas")
