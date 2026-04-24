#!/usr/bin/env python3
"""Codebase statistics — lines of code and test-coverage reporting.

Produces a compact summary of the project:

* ``--loc``                lines of code by language (via ``cloc``)
* ``--backend-coverage``   overall + worst-package JaCoCo coverage for the backend
* ``--frontend-coverage``  overall Vitest line coverage plus optional per-file scopes
* ``--all``                runs all three sections (the default when no flag is given)

The script is stdlib only and zero-config — it assumes the standard project
layout (``build/reports/jacoco/test/jacocoTestReport.xml`` and
``nest-ui/coverage/coverage-summary.json``). Missing reports trigger a clear
warning plus a suggested refresh command.

Usage:
    python agentic/scripts/codebase_stats.py                      # all sections
    python agentic/scripts/codebase_stats.py --loc
    python agentic/scripts/codebase_stats.py --backend-coverage
    python agentic/scripts/codebase_stats.py --frontend-coverage \\
        --scope pages/Admin/AccountsPage.tsx

Exit codes:
    0  all requested sections produced output
    1  a requested section genuinely failed (missing tool, failed coverage run,
       or missing XML combined with ``--strict``)
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable

# Project root is two directories above this script (agentic/scripts/ -> project).
PROJECT_ROOT = Path(__file__).resolve().parents[2]

CLOC_EXCLUDES = (
    "node_modules,.gradle,build,dist,.next,coverage,.claude,"
    "playwright-report,test-results"
)

BACKEND_THRESHOLD = 70.0  # Matches build.gradle jacocoTestCoverageVerification.
FRONTEND_THRESHOLD = 70.0

JACOCO_REPORT = PROJECT_ROOT / "build" / "reports" / "jacoco" / "test" / "jacocoTestReport.xml"
BACKEND_SOURCES = PROJECT_ROOT / "src" / "main" / "java"
FRONTEND_DIR = PROJECT_ROOT / "nest-ui"
FRONTEND_COVERAGE = FRONTEND_DIR / "coverage" / "coverage-summary.json"
FRONTEND_SRC = FRONTEND_DIR / "src"


# ── Output helpers ────────────────────────────────────────────────────────────


def _warn(msg: str) -> None:
    """Print a warning prefixed ``warning:`` to stderr."""
    print(f"warning: {msg}", file=sys.stderr)


def _error(msg: str) -> None:
    """Print an error prefixed ``error:`` to stderr."""
    print(f"error: {msg}", file=sys.stderr)


def _print_header(title: str) -> None:
    """Print a section header line."""
    print(title)


# ── LOC section ───────────────────────────────────────────────────────────────


def run_cloc(min_loc: int = 50) -> bool:
    """Run cloc and print a compact by-language code table.

    Drops languages with fewer than ``min_loc`` code lines. Returns True on
    success, False if cloc is missing or the invocation failed.
    """
    if shutil.which("cloc") is None:
        _error("cloc is not installed — install it (e.g. `sudo apt install cloc`)")
        return False

    cmd = [
        "cloc",
        str(PROJECT_ROOT),
        f"--exclude-dir={CLOC_EXCLUDES}",
        "--csv",
        "--quiet",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        _error(f"cloc failed (exit {result.returncode}):\n{result.stderr.strip()}")
        return False

    rows: list[tuple[str, int, int]] = []
    total_files = 0
    total_code = 0
    for raw in result.stdout.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        parts = raw.split(",")
        # Header: "files,language,blank,comment,code,..."
        if parts[0] == "files":
            continue
        if len(parts) < 5:
            continue
        try:
            files = int(parts[0])
            code = int(parts[4])
        except ValueError:
            continue
        language = parts[1]
        if language == "SUM":
            total_files = files
            total_code = code
            continue
        if code < min_loc:
            continue
        rows.append((language, files, code))

    if not rows:
        _warn("cloc produced no rows above the minimum threshold")
        return True

    rows.sort(key=lambda r: r[2], reverse=True)

    lang_w = max(len("Language"), max(len(r[0]) for r in rows))
    files_w = max(len("Files"), max(len(str(r[1])) for r in rows))
    code_w = max(len("Code"), max(len(f"{r[2]:,}") for r in rows))

    _print_header("Lines of code by language")
    print(f"  {'Language'.ljust(lang_w)}  {'Files'.rjust(files_w)}  {'Code'.rjust(code_w)}")
    print(f"  {'-' * lang_w}  {'-' * files_w}  {'-' * code_w}")
    for language, files, code in rows:
        print(
            f"  {language.ljust(lang_w)}  "
            f"{str(files).rjust(files_w)}  "
            f"{f'{code:,}'.rjust(code_w)}"
        )
    print(f"  {'-' * lang_w}  {'-' * files_w}  {'-' * code_w}")
    print(
        f"  {'TOTAL'.ljust(lang_w)}  "
        f"{str(total_files).rjust(files_w)}  "
        f"{f'{total_code:,}'.rjust(code_w)}"
    )
    return True


# ── Backend coverage section ──────────────────────────────────────────────────


def _latest_source_mtime(root: Path) -> float:
    """Return the latest mtime across all ``*.java`` files under ``root``, or 0."""
    latest = 0.0
    if not root.exists():
        return latest
    for path in root.rglob("*.java"):
        try:
            mt = path.stat().st_mtime
        except OSError:
            continue
        if mt > latest:
            latest = mt
    return latest


def _package_instruction_coverage(xml_path: Path) -> tuple[float, list[tuple[str, int, float]]]:
    """Parse the JaCoCo report and return overall pct and per-package rows.

    Each row is ``(package_name, instruction_total, instruction_pct)``.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    overall_missed = 0
    overall_covered = 0
    rows: list[tuple[str, int, float]] = []

    for pkg in root.iter("package"):
        p_missed = 0
        p_covered = 0
        for counter in pkg.findall("counter"):
            if counter.get("type") == "INSTRUCTION":
                p_missed = int(counter.get("missed", "0"))
                p_covered = int(counter.get("covered", "0"))
                break
        total = p_missed + p_covered
        pct = (100.0 * p_covered / total) if total else 0.0
        rows.append((pkg.get("name", "?"), total, pct))
        overall_missed += p_missed
        overall_covered += p_covered

    overall_total = overall_missed + overall_covered
    overall_pct = (100.0 * overall_covered / overall_total) if overall_total else 0.0
    return overall_pct, rows


def run_backend_coverage(strict: bool = False) -> bool:
    """Print backend JaCoCo coverage summary. Return True on success."""
    if not JACOCO_REPORT.exists():
        msg = (
            f"JaCoCo report missing at {JACOCO_REPORT.relative_to(PROJECT_ROOT)} — "
            "run `./gradlew test` to regenerate it"
        )
        if strict:
            _error(msg)
            return False
        _warn(msg)
        return True

    # Staleness check — report should not be older than the latest source file.
    report_mtime = JACOCO_REPORT.stat().st_mtime
    latest_src = _latest_source_mtime(BACKEND_SOURCES)
    stale = latest_src > report_mtime

    try:
        overall_pct, rows = _package_instruction_coverage(JACOCO_REPORT)
    except ET.ParseError as exc:
        _error(f"failed to parse JaCoCo XML: {exc}")
        return False

    _print_header("Backend coverage (JaCoCo INSTRUCTION)")
    if stale:
        _warn(
            "JaCoCo report appears stale (older than the latest source change) — "
            "consider `./gradlew test`"
        )
    flag = "" if overall_pct >= BACKEND_THRESHOLD else f"  BELOW {BACKEND_THRESHOLD:.0f}%"
    print(f"  Overall: {overall_pct:5.1f}%{flag}")

    if not rows:
        _warn("no packages found in JaCoCo report")
        return True

    # Exclude empty packages (no instructions — nothing to cover) from the
    # "below threshold" view, since they skew the picture.
    scored = [r for r in rows if r[1] > 0]
    scored.sort(key=lambda r: (r[2], r[0]))
    bottom = scored[:5]

    if not bottom:
        _warn("no packages with instructions found in JaCoCo report")
        return True

    name_w = max(len("Package"), max(len(r[0]) for r in bottom))
    instr_w = max(len("Instr"), max(len(str(r[1])) for r in bottom))

    print(f"  Lowest {len(bottom)} packages:")
    print(f"    {'Cov%'.rjust(6)}  {'Instr'.rjust(instr_w)}  {'Package'.ljust(name_w)}")
    print(f"    {'-' * 6}  {'-' * instr_w}  {'-' * name_w}")
    for name, total, pct in bottom:
        flag = "  BELOW" if pct < BACKEND_THRESHOLD else ""
        print(
            f"    {f'{pct:5.1f}'.rjust(6)}  "
            f"{str(total).rjust(instr_w)}  "
            f"{name.ljust(name_w)}{flag}"
        )

    below = [r for r in scored if r[2] < BACKEND_THRESHOLD]
    if below:
        print(f"  Packages below {BACKEND_THRESHOLD:.0f}%: {len(below)}")
    return True


# ── Frontend coverage section ─────────────────────────────────────────────────


def _ensure_frontend_coverage(force: bool = False) -> bool:
    """Ensure the Vitest coverage-summary.json file exists. Return True on success."""
    if FRONTEND_COVERAGE.exists() and not force:
        return True
    if not (FRONTEND_DIR / "package.json").exists():
        _error(f"frontend package.json missing at {FRONTEND_DIR}")
        return False
    print("  Running Vitest coverage (this may take a minute)…")
    cmd = [
        "npm", "--prefix", str(FRONTEND_DIR),
        "run", "test:coverage", "--",
        "--coverage.reporter=json-summary",
    ]
    result = subprocess.run(cmd, capture_output=False, text=True, check=False)
    if result.returncode != 0:
        _error("Vitest coverage run failed")
        return False
    return FRONTEND_COVERAGE.exists()


def _normalise_path(path: str) -> str:
    """Return the path relative to ``nest-ui/src`` if possible, else the raw path."""
    try:
        rel = Path(path).resolve().relative_to(FRONTEND_SRC.resolve())
        return str(rel)
    except ValueError:
        return path


def run_frontend_coverage(scopes: Iterable[str] | None = None) -> bool:
    """Print Vitest total line coverage and per-scope file coverage."""
    if not _ensure_frontend_coverage():
        return False

    try:
        with FRONTEND_COVERAGE.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        _error(f"failed to read {FRONTEND_COVERAGE}: {exc}")
        return False

    total = data.get("total", {})
    lines = total.get("lines", {})
    total_pct = lines.get("pct", 0.0)
    total_total = lines.get("total", 0)
    total_covered = lines.get("covered", 0)

    _print_header("Frontend coverage (Vitest lines)")
    flag = "" if total_pct >= FRONTEND_THRESHOLD else f"  BELOW {FRONTEND_THRESHOLD:.0f}%"
    print(f"  Overall: {total_pct:5.1f}%  ({total_covered}/{total_total} lines){flag}")

    scope_list = [s for s in (scopes or []) if s]
    if not scope_list:
        return True

    # Build a lookup of absolute-ish paths to entries (skip "total").
    entries = {k: v for k, v in data.items() if k != "total"}

    print("  Scoped files:")
    any_row = False
    for scope in scope_list:
        matches: list[tuple[str, float, int, int]] = []
        for path, metrics in entries.items():
            if path.endswith(scope):
                m_lines = metrics.get("lines", {})
                matches.append((
                    _normalise_path(path),
                    m_lines.get("pct", 0.0),
                    m_lines.get("covered", 0),
                    m_lines.get("total", 0),
                ))
        if not matches:
            print(f"    {scope}: no matching file in coverage report")
            continue
        for rel, pct, covered, tot in matches:
            flag = "  BELOW" if pct < FRONTEND_THRESHOLD else ""
            print(f"    {rel}: lines {pct:5.1f}%  ({covered}/{tot}){flag}")
            any_row = True

    if not any_row and scope_list:
        return True
    return True


# ── CLI ───────────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argparse parser."""
    parser = argparse.ArgumentParser(
        description="Report lines of code and test coverage for the Nest project."
    )
    parser.add_argument("--loc", action="store_true", help="report lines of code by language")
    parser.add_argument(
        "--backend-coverage", action="store_true",
        help="report backend JaCoCo coverage summary"
    )
    parser.add_argument(
        "--frontend-coverage", action="store_true",
        help="report frontend Vitest line-coverage summary"
    )
    parser.add_argument(
        "--all", action="store_true",
        help="run all sections (default when no section flag is given)"
    )
    parser.add_argument(
        "--scope", action="append", default=[],
        help="restrict frontend per-file coverage to files ending with this suffix "
             "(repeatable, e.g. --scope pages/Admin/AccountsPage.tsx)"
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="treat missing backend reports as failures instead of warnings"
    )
    return parser


def main() -> int:
    """Script entry point. Returns the intended exit code."""
    parser = build_parser()
    args = parser.parse_args()

    # Determine active sections — default (no flag) = --all.
    any_section = args.loc or args.backend_coverage or args.frontend_coverage or args.all
    run_all = args.all or not any_section

    do_loc = run_all or args.loc
    do_backend = run_all or args.backend_coverage
    do_frontend = run_all or args.frontend_coverage

    if args.scope and not do_frontend:
        _warn("--scope ignored because frontend coverage was not requested")

    ok = True
    first = True

    def _sep() -> None:
        """Insert a blank line between sections, but not before the first."""
        nonlocal first
        if not first:
            print()
        first = False

    if do_loc:
        _sep()
        ok = run_cloc() and ok

    if do_backend:
        _sep()
        ok = run_backend_coverage(strict=args.strict) and ok

    if do_frontend:
        _sep()
        ok = run_frontend_coverage(scopes=args.scope) and ok

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
