#!/usr/bin/env python3
"""
Markdown Link Checker

Traverses all subdirectories from the project root, reads every .md file,
extracts all links, and checks whether they point to existing files or
directories.

Usage:
    python agentic/scripts/check_all_md_links.py

Exit codes:
    0 - All links are valid
    1 - One or more broken links found
"""

import os
import re
import sys
import urllib.parse

# Project root is two levels up from the agentic/scripts/ directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Directories to skip during traversal
SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.idea', 'dist', 'build', '.gradle'}

# Pattern to match Markdown links: [text](target) and [text](target "title")
# Also matches image links: "![alt](src)"
LINK_PATTERN = re.compile(r'!?\[(?:[^\[\]]|\[[^\]]*\])*\]\(([^)]+)\)')


def find_md_files(root: str) -> list[str]:
    """Find all .md files under the given root, skipping excluded directories."""
    md_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune directories we want to skip (modifying dirnames in-place)
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            if filename.lower().endswith('.md'):
                md_files.append(os.path.join(dirpath, filename))
    md_files.sort()
    return md_files


def extract_links(filepath: str) -> list[tuple[int, str, str]]:
    """
    Extract all Markdown links from a file.

    Skips links inside fenced code blocks (``` or ~~~) and inline code spans
    (backtick-delimited).

    Returns a list of (line_number, raw_match, target) tuples.
    """
    links = []
    in_code_block = False
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for line_number, line in enumerate(f, start=1):
            stripped = line.strip()
            # Toggle fenced code block state
            if stripped.startswith('```') or stripped.startswith('~~~'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            # Remove inline code spans before searching for links
            line_without_code = re.sub(r'`[^`]+`', '', line)
            for match in LINK_PATTERN.finditer(line_without_code):
                raw = match.group(0)
                target = match.group(1).strip()
                # Strip optional title from the target (e.g. 'path "title"')
                title_match = re.match(r'^(\S+)\s+"[^"]*"$', target)
                if title_match:
                    target = title_match.group(1)
                links.append((line_number, raw, target))
    return links


def is_external_or_special(target: str) -> bool:
    """Return True if the target is a URL, mailto, or anchor-only link."""
    if target.startswith(('#', 'http://', 'https://', 'mailto:', 'ftp://')):
        return True
    parsed = urllib.parse.urlparse(target)
    if parsed.scheme:
        return True
    return False


def resolve_link(md_file: str, target: str) -> bool:
    """
    Check whether a relative link target resolves to an existing file or
    directory.
    """
    # Strip any fragment (anchor) from the target
    target_no_fragment = target.split('#')[0]
    if not target_no_fragment:
        # Pure anchor link (e.g. #section) — already filtered, but just in case
        return True

    # URL-decode the path (e.g. %20 -> space)
    target_no_fragment = urllib.parse.unquote(target_no_fragment)

    # Resolve relative to the directory containing the markdown file
    base_dir = os.path.dirname(md_file)
    resolved = os.path.normpath(os.path.join(base_dir, target_no_fragment))

    return os.path.exists(resolved)


def main() -> int:
    md_files = find_md_files(PROJECT_ROOT)

    if not md_files:
        print("No Markdown files found.")
        return 0

    broken_count = 0
    warning_count = 0

    for md_file in md_files:
        links = extract_links(md_file)
        for line_number, raw_match, target in links:
            if is_external_or_special(target):
                continue

            # Strip fragment for path checks
            target_path = target.split('#')[0]
            if not target_path:
                continue
            target_path = urllib.parse.unquote(target_path)

            # Warn about absolute filesystem paths
            if os.path.isabs(target_path):
                warning_count += 1
                rel_path = os.path.relpath(md_file, PROJECT_ROOT)
                print(f"W{warning_count}: {rel_path} (L{line_number}): Absolute path (use relative instead)")
                print(f"    {raw_match}")
                continue

            if not resolve_link(md_file, target):
                broken_count += 1
                rel_path = os.path.relpath(md_file, PROJECT_ROOT)
                print(f"{broken_count}: {rel_path} (L{line_number}): Invalid link")
                print(f"    {raw_match}")

    if broken_count == 0 and warning_count == 0:
        print(f"Checked {len(md_files)} Markdown files — all links are valid.")
        return 0
    else:
        summary_parts = []
        if broken_count:
            summary_parts.append(f"{broken_count} broken link(s)")
        if warning_count:
            summary_parts.append(f"{warning_count} warning(s)")
        print(f"\nFound {' and '.join(summary_parts)} across {len(md_files)} Markdown files.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
