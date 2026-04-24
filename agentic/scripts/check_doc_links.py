#!/usr/bin/env python3
"""
Documentation Link Checker Script

Verifies all documentation links in the backlog are valid and files exist.
Can also check for completed tasks without documentation.

Usage:
    python scripts/check_doc_links.py          # Check only
    python scripts/check_doc_links.py --fix    # Fix broken relative paths

Exit codes:
    0 - All checks passed
    1 - Issues found
"""

import sys
import os
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backlog_utils import (
    read_backlog,
    parse_tasks_table,
    parse_task_details,
    merge_task_info,
    TASKS_DIR,
)


class DocumentationChecker:
    """Checks documentation links and completeness."""

    def __init__(self):
        self.issues = []
        self.fixed = []

    def check(self, fix_mode: bool = False) -> bool:
        """
        Run documentation checks.

        Args:
            fix_mode: If True, attempt to fix issues

        Returns:
            True if no issues found (or all fixed), False otherwise
        """
        try:
            content = read_backlog()
        except Exception as e:
            print(f"Error reading backlog: {e}")
            return False

        table_tasks = parse_tasks_table(content)
        detail_tasks = parse_task_details(content)
        tasks = merge_task_info(table_tasks, detail_tasks)

        # Check each task with documentation
        for task in tasks:
            if task.documentation and task.documentation != 'No documentation':
                self._check_doc_link(task, fix_mode)

        # Check for completed tasks without documentation
        # "No documentation" is a valid sentinel for tasks completed without
        # a documentation file (e.g. retroactively closed tasks)
        for task in tasks:
            if task.status == 'DONE' and not task.documentation:
                self.issues.append(
                    f"Task {task.task_id} is DONE but has no documentation"
                )

        return len(self.issues) == 0

    def _check_doc_link(self, task, fix_mode: bool):
        """Check documentation link for a single task."""
        doc_filename = task.documentation

        # Check filename format — accept <taskID>.md or <taskID>.complete.md
        valid_filenames = {
            f'{task.task_id}.md',
            f'{task.task_id}.complete.md',
        }
        if doc_filename not in valid_filenames:
            self.issues.append(
                f"Task {task.task_id}: Documentation filename '{doc_filename}' "
                f"should be '{task.task_id}.md' or '{task.task_id}.complete.md'"
            )

        # Check if file exists — resolve against the project's tasks dir so
        # this runs from any cwd.
        doc_path = TASKS_DIR / doc_filename
        if not doc_path.exists():
            self.issues.append(
                f"Task {task.task_id}: Documentation file not found: docs/tasks/{doc_filename}"
            )
        else:
            # File exists - good!
            pass

    def print_results(self):
        """Print check results."""
        if not self.issues and not self.fixed:
            print("✓ All documentation links are valid!")
            return

        if self.fixed:
            print(f"\n✓ Fixed {len(self.fixed)} issue(s):\n")
            for fix in self.fixed:
                print(f"  {fix}")

        if self.issues:
            print(f"\n❌ Found {len(self.issues)} issue(s):\n")
            for issue in self.issues:
                print(f"  {issue}")

        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Check documentation links in backlog'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to fix broken links (currently not implemented)'
    )

    args = parser.parse_args()

    if args.fix:
        print("Note: Fix mode not yet implemented. Running in check-only mode.\n")

    checker = DocumentationChecker()

    print("Checking documentation links...")
    success = checker.check(fix_mode=args.fix)
    checker.print_results()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
