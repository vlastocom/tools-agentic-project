#!/usr/bin/env python3
"""Format Markdown tables so that every column has a consistent width.

Rules (from /md-file-editing skill):
  1. Every row in a table must have the same column widths.
  2. Each cell is padded with at least one space on each side.
  3. The separator row's dashes fill the full column width.
  4. Alignment markers (:) in the separator row are preserved.

Usage:
    python agentic/scripts/format_md_tables.py [FILE ...]

If no files are given, the script reads from stdin and writes to stdout.
With file arguments, each file is reformatted **in place**.

Exit codes:
    0  All files processed (or no changes needed)
    1  Error reading/writing a file
"""

import re
import sys


def _parse_row(line: str) -> list[str]:
    """Split a pipe-delimited table row into raw cell strings."""
    s = line
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return s.split("|")


def _is_separator(cells: list[str]) -> bool:
    return all(re.match(r"^[\s:]*-+[\s:]*$", c) for c in cells)


def _alignment(cell: str) -> str:
    c = cell.strip()
    if c.startswith(":") and c.endswith(":"):
        return "center"
    if c.endswith(":"):
        return "right"
    return "left"


def _format_table(lines: list[str]) -> list[str]:
    rows = [_parse_row(ln) for ln in lines]

    # Find the separator row
    sep_idx = next((i for i, r in enumerate(rows) if _is_separator(r)), None)
    if sep_idx is None:
        return lines  # not a real table

    num_cols = len(rows[0])
    alignments = [_alignment(c) for c in rows[sep_idx]]

    # Measure the widest stripped content per column (excluding separator)
    widths = [0] * num_cols
    for i, cells in enumerate(rows):
        if i == sep_idx:
            continue
        for j, cell in enumerate(cells):
            if j < num_cols:
                widths[j] = max(widths[j], len(cell.strip()))

    result: list[str] = []
    for i, cells in enumerate(rows):
        if i == sep_idx:
            parts: list[str] = []
            for j in range(num_cols):
                w = widths[j]
                a = alignments[j] if j < len(alignments) else "left"
                if a == "center":
                    parts.append(":" + "-" * w + ":")
                elif a == "right":
                    parts.append("-" * (w + 1) + ":")
                else:
                    parts.append("-" * (w + 2))
            result.append("|" + "|".join(parts) + "|")
        else:
            parts = []
            for j in range(num_cols):
                content = cells[j].strip() if j < len(cells) else ""
                w = widths[j]
                a = alignments[j] if j < len(alignments) else "left"
                if a == "center":
                    pad = w - len(content)
                    lp = pad // 2
                    rp = pad - lp
                    parts.append(" " * (lp + 1) + content + " " * (rp + 1))
                elif a == "right":
                    parts.append(" " + content.rjust(w) + " ")
                else:
                    parts.append(" " + content.ljust(w) + " ")
            result.append("|" + "|".join(parts) + "|")
    return result


def format_tables(text: str) -> str:
    """Return *text* with every Markdown table reformatted."""
    lines = text.split("\n")
    # Identify table spans: consecutive lines starting with '|'
    tables: list[tuple[int, int]] = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("|"):
            start = i
            while i < len(lines) and lines[i].startswith("|"):
                i += 1
            tables.append((start, i))
        else:
            i += 1

    # Process in reverse so indices stay valid
    for start, end in reversed(tables):
        lines[start:end] = _format_table(lines[start:end])

    return "\n".join(lines)


# -- CLI ------------------------------------------------------------------- #

def main() -> int:
    files = sys.argv[1:]

    if not files:
        # stdin → stdout mode
        text = sys.stdin.read()
        sys.stdout.write(format_tables(text))
        return 0

    errors = 0
    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                original = fh.read()
        except OSError as exc:
            print(f"ERROR: cannot read {path}: {exc}", file=sys.stderr)
            errors += 1
            continue

        formatted = format_tables(original)

        if formatted != original:
            try:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(formatted)
                print(f"  Formatted: {path}")
            except OSError as exc:
                print(f"ERROR: cannot write {path}: {exc}", file=sys.stderr)
                errors += 1
        else:
            print(f"  No changes: {path}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
