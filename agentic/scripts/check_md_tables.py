#!/usr/bin/env python3
"""Check Markdown table formatting without modifying files.

Compares each file against the output of format_md_tables.format_tables()
and reports any differences with line numbers.

Usage:
    python agentic/scripts/check_md_tables.py [FILE ...]

Exit codes:
    0  All tables are correctly formatted
    1  Formatting issues found (or file read errors)
"""

import sys
from pathlib import Path

# Allow importing the sibling module regardless of how the script is invoked
sys.path.insert(0, str(Path(__file__).resolve().parent))

from format_md_tables import format_tables  # noqa: E402


def check_file(path: str) -> list[str]:
    """Return a list of human-readable issue descriptions for *path*."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            original = fh.read()
    except OSError as exc:
        return [f"ERROR: cannot read {path}: {exc}"]

    formatted = format_tables(original)

    if original == formatted:
        return []

    orig_lines = original.split("\n")
    fmt_lines = formatted.split("\n")

    issues: list[str] = []
    max_lines = max(len(orig_lines), len(fmt_lines))

    for i in range(max_lines):
        orig = orig_lines[i] if i < len(orig_lines) else "<missing>"
        fmt = fmt_lines[i] if i < len(fmt_lines) else "<missing>"

        if orig != fmt:
            issues.append(
                f"  Line {i + 1}:\n"
                f"    actual:   {orig}\n"
                f"    expected: {fmt}"
            )

    return issues


def main() -> int:
    files = sys.argv[1:]

    if not files:
        print("Usage: python agentic/scripts/check_md_tables.py [FILE ...]",
              file=sys.stderr)
        return 1

    total_issues = 0

    for path in files:
        issues = check_file(path)
        if issues:
            print(f"\n{path}: {len(issues)} line(s) with formatting issues:")
            for issue in issues:
                print(issue)
            total_issues += len(issues)
        else:
            print(f"{path}: ✓ all tables correctly formatted")

    if total_issues:
        print(f"\n✗ {total_issues} issue(s) found across {len(files)} file(s)")
        return 1

    print(f"\n✓ All {len(files)} file(s) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
