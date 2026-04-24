#!/usr/bin/env python3
"""
Backlog Validator Script

Validates the structure and consistency of docs/backlog.md file.

Usage:
    python agentic/scripts/validate_backlog.py

Exit codes:
    0 - Validation passed
    1 - Validation failed (errors found)
"""

import sys
import os
import re
from typing import List, Set

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backlog_utils import (
    read_backlog,
    parse_tasks_table,
    parse_task_details,
    parse_epics,
    parse_areas,
    parse_sprints,
    merge_task_info,
    validate_task_id,
    validate_epic_id,
    validate_status,
    validate_priority,
    validate_task_type,
    validate_sprint_id,
    validate_sprint_status,
    extract_epic_from_task_id,
    BACKLOG_PATH,
    TASKS_DIR,
    VALID_STATUSES,
    VALID_PRIORITIES,
    VALID_TASK_TYPES,
    VALID_SPRINT_STATUSES
)


class ValidationError:
    """Represents a validation error."""

    def __init__(self, category: str, message: str, severity: str = 'ERROR'):
        self.category = category
        self.message = message
        self.severity = severity

    def __str__(self):
        return f"[{self.severity}] {self.category}: {self.message}"


class BacklogValidator:
    """Validates backlog structure and consistency."""

    def __init__(self, backlog_path=None):
        self.backlog_path = backlog_path if backlog_path is not None else BACKLOG_PATH
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []

    def add_error(self, category: str, message: str):
        """Add a validation error."""
        self.errors.append(ValidationError(category, message, 'ERROR'))

    def add_warning(self, category: str, message: str):
        """Add a validation warning."""
        self.warnings.append(ValidationError(category, message, 'WARNING'))

    def validate(self) -> bool:
        """
        Run all validations.

        Returns:
            True if validation passed (no errors), False otherwise
        """
        try:
            content = read_backlog(self.backlog_path)
        except FileNotFoundError:
            self.add_error('File', f'Backlog file not found: {self.backlog_path}')
            return False
        except Exception as e:
            self.add_error('File', f'Error reading backlog: {e}')
            return False

        # Run validation checks
        self.validate_structure(content)
        self.validate_task_ids(content)
        self.validate_epic_ids(content)
        self.validate_task_table_vs_details(content)
        self.validate_statuses_and_priorities(content)
        self.validate_task_types(content)
        self.validate_documentation_links(content)
        self.validate_no_duplicate_ids(content)
        self.validate_dependencies(content)
        self.validate_sprints(content)

        return len(self.errors) == 0

    def validate_structure(self, content: str):
        """Validate overall document structure."""
        required_sections = [
            '## Sprints',
            '## Areas',
            '## Epics',
            '## Tasks',
            '## Task Details'
        ]

        for section in required_sections:
            if section not in content:
                self.add_error('Structure', f'Missing required section: {section}')

        # Check for section separators
        section_count = content.count('## ')
        separator_count = content.count('\n---\n')

        # Should have separators between major sections (not exact count due to sprint separators)
        if separator_count < 3:
            self.add_warning('Structure', f'Expected more section separators (---), found {separator_count}')

        # Validate Tasks table structure
        if '## Tasks' in content:
            tasks_section_match = re.search(r'## Tasks\n\n(.*?)(?=\n---)', content, re.DOTALL)
            if tasks_section_match:
                tasks_section = tasks_section_match.group(1)
                # Use regex to allow variable whitespace padding in column headers
                header_pattern = (
                    r'\|\s*ID\s*\|\s*Type\s*\|\s*Priority\s*\|\s*Short Name\s*\|'
                    r'\s*Status\s*\|\s*Est\. Duration\s*\|\s*Sprint\s*\|'
                )
                if not re.search(header_pattern, tasks_section):
                    self.add_error('Structure', 'Tasks table missing correct header')
                if not re.search(r'\|-+\|-+\|-+\|-+\|-+\|-+\|-+\|', tasks_section):
                    self.add_error('Structure', 'Tasks table missing separator row')

    def validate_task_ids(self, content: str):
        """Validate all task IDs follow correct format."""
        tasks = parse_tasks_table(content)

        for task in tasks:
            if not validate_task_id(task.task_id):
                self.add_error(
                    'Task ID Format',
                    f'Task ID "{task.task_id}" does not follow format <EPIC-ID>-<4-DIGIT-NUMBER>'
                )

    def validate_epic_ids(self, content: str):
        """Validate all epic IDs follow correct format."""
        epics = parse_epics(content)

        for epic in epics:
            if not validate_epic_id(epic.epic_id):
                self.add_error(
                    'Epic ID Format',
                    f'Epic ID "{epic.epic_id}" does not follow format <AREA>-<2-DIGIT-NUMBER>'
                )

    def validate_task_table_vs_details(self, content: str):
        """Validate consistency between Tasks table and Task Details."""
        table_tasks = parse_tasks_table(content)
        detail_tasks = parse_task_details(content)

        table_ids = {task.task_id for task in table_tasks}
        detail_ids = set(detail_tasks.keys())

        # Check for tasks in table but not in details
        missing_details = table_ids - detail_ids
        for task_id in missing_details:
            self.add_error(
                'Task Consistency',
                f'Task {task_id} in Tasks table but missing detail section'
            )

        # Check for tasks in details but not in table
        missing_table = detail_ids - table_ids
        for task_id in missing_table:
            self.add_error(
                'Task Consistency',
                f'Task {task_id} has detail section but missing from Tasks table'
            )

    def validate_statuses_and_priorities(self, content: str):
        """Validate all statuses and priorities are valid."""
        tasks = parse_tasks_table(content)

        for task in tasks:
            if not validate_status(task.status):
                self.add_error(
                    'Task Status',
                    f'Task {task.task_id} has invalid status "{task.status}". '
                    f'Valid: {", ".join(sorted(VALID_STATUSES))}'
                )

            if not validate_priority(task.priority):
                self.add_error(
                    'Task Priority',
                    f'Task {task.task_id} has invalid priority "{task.priority}". '
                    f'Valid: {", ".join(sorted(VALID_PRIORITIES))}'
                )

    def validate_task_types(self, content: str):
        """Validate all task types are valid."""
        tasks = parse_tasks_table(content)

        for task in tasks:
            if not validate_task_type(task.task_type):
                self.add_error(
                    'Task Type',
                    f'Task {task.task_id} has invalid type "{task.task_type}". '
                    f'Valid: {", ".join(sorted(VALID_TASK_TYPES))}'
                )

    def validate_documentation_links(self, content: str):
        """Validate documentation links (now sourced from Task Details)."""
        table_tasks = parse_tasks_table(content)
        detail_tasks = parse_task_details(content)
        tasks = merge_task_info(table_tasks, detail_tasks)

        for task in tasks:
            if task.documentation:
                # "No documentation" is a valid sentinel for tasks completed
                # without a documentation file (e.g. retroactively closed tasks)
                if task.documentation == 'No documentation':
                    continue

                # Check format — accept <taskID>.md or <taskID>.complete.md
                valid_formats = {
                    f'{task.task_id}.md',
                    f'{task.task_id}.complete.md',
                }
                if task.documentation not in valid_formats:
                    self.add_warning(
                        'Documentation Link',
                        f'Task {task.task_id} documentation "{task.documentation}" '
                        f'does not match expected format '
                        f'"{task.task_id}.md" or "{task.task_id}.complete.md"'
                    )

                # Check if file exists — resolve against the project's tasks dir so
                # this runs from any cwd.
                doc_path = TASKS_DIR / task.documentation
                if not doc_path.exists():
                    self.add_error(
                        'Documentation File',
                        f'Task {task.task_id} references docs/tasks/{task.documentation} which does not exist'
                    )

    def validate_no_duplicate_ids(self, content: str):
        """Check for duplicate task or epic IDs."""
        tasks = parse_tasks_table(content)
        task_ids = [task.task_id for task in tasks]
        seen = set()
        for task_id in task_ids:
            if task_id in seen:
                self.add_error('Duplicate ID', f'Duplicate task ID: {task_id}')
            seen.add(task_id)

        epics = parse_epics(content)
        epic_ids = [epic.epic_id for epic in epics]
        seen = set()
        for epic_id in epic_ids:
            if epic_id in seen:
                self.add_error('Duplicate ID', f'Duplicate epic ID: {epic_id}')
            seen.add(epic_id)

    def validate_dependencies(self, content: str):
        """Validate task dependencies reference existing tasks."""
        table_tasks = parse_tasks_table(content)
        detail_tasks = parse_task_details(content)

        all_task_ids = {task.task_id for task in table_tasks}

        for task_id, detail in detail_tasks.items():
            for dep_id in detail.dependencies:
                if dep_id not in all_task_ids:
                    self.add_warning(
                        'Dependency',
                        f'Task {task_id} depends on {dep_id} which does not exist'
                    )

    def validate_sprints(self, content: str):
        """Validate sprint definitions and references."""
        sprints = parse_sprints(content)
        tasks = parse_tasks_table(content)

        sprint_ids = set()
        open_count = 0

        for sprint in sprints:
            # Validate sprint ID format
            if not validate_sprint_id(sprint.sprint_id):
                self.add_error(
                    'Sprint ID',
                    f'Sprint ID "{sprint.sprint_id}" does not follow YYYY-MM-DD format'
                )

            # Validate sprint status
            if sprint.status and not validate_sprint_status(sprint.status):
                self.add_error(
                    'Sprint Status',
                    f'Sprint {sprint.sprint_id} has invalid status "{sprint.status}". '
                    f'Valid: {", ".join(sorted(VALID_SPRINT_STATUSES))}'
                )

            if sprint.status == 'OPEN':
                open_count += 1

            sprint_ids.add(sprint.sprint_id)

        # At most one sprint should be OPEN
        if open_count > 1:
            self.add_error(
                'Sprint Status',
                f'Found {open_count} OPEN sprints — at most one should be OPEN'
            )

        # Tasks referencing a sprint must have a matching sprint defined
        for task in tasks:
            if task.sprint and task.sprint not in sprint_ids:
                self.add_error(
                    'Sprint Reference',
                    f'Task {task.task_id} references sprint "{task.sprint}" '
                    f'which is not defined in the Sprints section'
                )

    def print_results(self):
        """Print validation results."""
        if not self.errors and not self.warnings:
            print("✓ Backlog validation passed!")
            return

        if self.errors:
            print(f"\n❌ Found {len(self.errors)} error(s):\n")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print(f"\n⚠ Found {len(self.warnings)} warning(s):\n")
            for warning in self.warnings:
                print(f"  {warning}")

        print()


def main():
    """Main entry point."""
    validator = BacklogValidator()

    print("Validating backlog structure...")
    success = validator.validate()
    validator.print_results()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
