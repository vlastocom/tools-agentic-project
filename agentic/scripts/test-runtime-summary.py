#!/usr/bin/env python3
"""
test-runtime-summary.py — emit the Test runtime block for a sprint's
coverage summary.

Reads test reports from one or more suites (each in its own framework's
default reporter format), computes per-suite total / count / avg / max,
optionally diffs against a previous sprint's coverage file, and emits
a Markdown block.

Usage (typical):

    test-runtime-summary.py \\
        --suite "backend-unit"        --junit-xml 'build/test-results/test/*.xml' \\
        --suite "backend-integration" --junit-xml 'build/test-results/integrationTest/*.xml' \\
        --suite "frontend-unit"       --vitest-json 'frontend/test-results/vitest.json' \\
        --suite "e2e"                 --playwright-json 'playwright-report/results.json' \\
        --baseline docs/sprints/2026-04-28.coverage.md \\
        --avg-threshold-pct 5 \\
        --max-threshold-pct-of-avg 25 \\
        --out docs/sprints/2026-05-19.test-runtime.md

Each --suite NAME applies to the next --junit-xml / --vitest-json /
--playwright-json that follows it. Order: --suite first, then the
report-source flag for that suite.

Output is a Markdown block with a header, a per-suite table (current
metrics, deltas, threshold-trip indicators), and a flagged-deviations
list. Suitable for embedding in a sprint coverage summary.

Exit codes:
    0   Success — block emitted (regardless of whether thresholds tripped)
    1   Usage error
    2   Report parsing failure
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional


@dataclass
class TestCase:
    """A single test-case timing observation."""
    name: str
    duration_s: float


@dataclass
class SuiteAggregate:
    """Aggregated metrics for one suite."""
    suite: str
    count: int
    total_s: float
    avg_ms: float
    max_test_name: str
    max_ms: float


@dataclass
class SuiteDelta:
    """Per-suite current-vs-baseline comparison + threshold trips."""
    current: SuiteAggregate
    baseline: Optional[SuiteAggregate]
    avg_delta_pct: Optional[float]
    max_delta_pct_of_avg: Optional[float]
    avg_tripped: bool = False
    max_tripped: bool = False
    flags: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Parsers — one per supported reporter format. Each returns an iterator of
# TestCase. Add a new parser here when adding a new framework.
# ---------------------------------------------------------------------------

def parse_junit_xml_glob(pattern: str) -> Iterator[TestCase]:
    """Parse JUnit-style XML test reports. `pattern` may include shell globs."""
    paths = glob.glob(pattern)
    if not paths:
        print(f"warning: no JUnit XML files matched {pattern!r}", file=sys.stderr)
        return
    for path in paths:
        try:
            tree = ET.parse(path)
        except ET.ParseError as exc:
            raise SystemExit(f"failed to parse JUnit XML {path}: {exc}")
        # JUnit XML has <testsuite> root or <testsuites><testsuite>...
        root = tree.getroot()
        suites = [root] if root.tag == "testsuite" else root.findall(".//testsuite")
        for suite in suites:
            for case in suite.findall("testcase"):
                duration = float(case.get("time", "0") or "0")
                classname = case.get("classname", "")
                name = case.get("name", "")
                full = f"{classname}.{name}" if classname else name
                yield TestCase(name=full, duration_s=duration)


def parse_vitest_json(path: str) -> Iterator[TestCase]:
    """Parse Vitest's JSON reporter output (structure ~ Jest)."""
    data = json.loads(Path(path).read_text())
    # Vitest emits `testResults` (per-file) each with `assertionResults`
    for file_result in data.get("testResults", []):
        for case in file_result.get("assertionResults", []):
            full = ".".join(case.get("ancestorTitles", []) + [case.get("title", "")])
            duration_ms = case.get("duration") or 0  # may be None on skipped
            yield TestCase(name=full, duration_s=float(duration_ms) / 1000.0)


def parse_playwright_json(path: str) -> Iterator[TestCase]:
    """Parse Playwright's JSON reporter output (`results.json`)."""
    data = json.loads(Path(path).read_text())
    # Recurse through `suites` → `specs` → `tests` → `results` (see PW reporter docs).
    def walk(node: dict, parents: list[str]) -> Iterator[TestCase]:
        for suite in node.get("suites", []):
            yield from walk(suite, parents + [suite.get("title", "")])
        for spec in node.get("specs", []):
            spec_title = spec.get("title", "")
            for test in spec.get("tests", []):
                results = test.get("results", []) or []
                # Sum across retries; report a single timing per test
                duration_ms = sum(r.get("duration", 0) for r in results)
                full = " > ".join(parents + [spec_title])
                yield TestCase(name=full, duration_s=duration_ms / 1000.0)
    yield from walk(data, [])


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def aggregate(suite_name: str, cases: list[TestCase]) -> SuiteAggregate:
    if not cases:
        return SuiteAggregate(
            suite=suite_name, count=0, total_s=0.0,
            avg_ms=0.0, max_test_name="(none)", max_ms=0.0,
        )
    total_s = sum(c.duration_s for c in cases)
    count = len(cases)
    avg_ms = (total_s / count) * 1000.0
    slowest = max(cases, key=lambda c: c.duration_s)
    return SuiteAggregate(
        suite=suite_name, count=count, total_s=total_s,
        avg_ms=avg_ms, max_test_name=slowest.name, max_ms=slowest.duration_s * 1000.0,
    )


# ---------------------------------------------------------------------------
# Baseline reading — extract the Test-runtime block from a previous
# sprint's coverage Markdown.
# ---------------------------------------------------------------------------

# The block we emit (and read back) starts with `## Test runtime` and is
# followed by a Markdown table whose data rows look like:
#   | <suite> | <count> | <total>s | <avg>ms | <max-test-name> (<max>ms) | ...
# Δ columns and tripped column are ignored — we don't compound deltas.
BASELINE_TABLE_PATTERN = re.compile(
    r"^\|\s*([^|]+?)\s*\|"                  # 1: suite
    r"\s*([\d.]+)\s*\|"                     # 2: count
    r"\s*([\d.]+)s\s*\|"                    # 3: total_s
    r"\s*([\d.]+)ms\s*\|"                   # 4: avg_ms
    r"\s*(.+?)\s+\(([\d.]+)ms\)\s*\|",      # 5: max_test_name, 6: max_ms
    re.MULTILINE,
)


def read_baseline(path: Optional[str]) -> dict[str, SuiteAggregate]:
    if not path or not Path(path).exists():
        return {}
    text = Path(path).read_text()
    # Find the start of `## Test runtime`; if absent, no baseline.
    start = text.find("## Test runtime")
    if start < 0:
        return {}
    # The block ends at the next `## ` header or end of file.
    end = text.find("\n## ", start + 1)
    block = text[start:end if end > 0 else len(text)]
    out: dict[str, SuiteAggregate] = {}
    for match in BASELINE_TABLE_PATTERN.finditer(block):
        suite, count, total, avg, max_name, max_ms = match.groups()
        out[suite.strip()] = SuiteAggregate(
            suite=suite.strip(),
            count=int(float(count)),
            total_s=float(total),
            avg_ms=float(avg),
            max_test_name=max_name.strip(),
            max_ms=float(max_ms),
        )
    return out


# ---------------------------------------------------------------------------
# Threshold computation
# ---------------------------------------------------------------------------

def compare(current: SuiteAggregate, baseline: Optional[SuiteAggregate],
            avg_pct: float, max_pct_of_avg: float) -> SuiteDelta:
    if baseline is None or baseline.count == 0:
        return SuiteDelta(current=current, baseline=baseline,
                          avg_delta_pct=None, max_delta_pct_of_avg=None)
    avg_delta_pct = ((current.avg_ms - baseline.avg_ms) / baseline.avg_ms) * 100.0
    # Δmax expressed as a percentage of the **current** sprint's avg.
    max_delta_pct_of_avg = (
        ((current.max_ms - baseline.max_ms) / current.avg_ms) * 100.0
        if current.avg_ms > 0 else 0.0
    )
    delta = SuiteDelta(current=current, baseline=baseline,
                       avg_delta_pct=avg_delta_pct,
                       max_delta_pct_of_avg=max_delta_pct_of_avg)
    if avg_delta_pct > avg_pct:
        delta.avg_tripped = True
        delta.flags.append(
            f"Δavg {avg_delta_pct:+.1f}% exceeds threshold +{avg_pct:.0f}%"
        )
    if max_delta_pct_of_avg > max_pct_of_avg:
        delta.max_tripped = True
        delta.flags.append(
            f"Δmax {max_delta_pct_of_avg:+.1f}%-of-avg exceeds threshold +{max_pct_of_avg:.0f}%"
            f" (slowest: {current.max_test_name})"
        )
    return delta


# ---------------------------------------------------------------------------
# Markdown formatting
# ---------------------------------------------------------------------------

def fmt_pct(p: Optional[float]) -> str:
    return "—" if p is None else f"{p:+.1f}%"


def format_markdown(deltas: list[SuiteDelta], avg_pct: float,
                    max_pct_of_avg: float) -> str:
    lines: list[str] = []
    lines.append("## Test runtime")
    lines.append("")
    lines.append(
        f"Thresholds: Δavg > +{avg_pct:.0f}%, "
        f"Δmax > +{max_pct_of_avg:.0f}% of current-sprint avg. "
        "Trips are flagged as deviations and require explicit operator "
        "disposition at sprint review (sdlc-workflow-guide.md §3.6, §5.5)."
    )
    lines.append("")
    lines.append(
        "| Suite | Tests | Total | Avg | Max (slowest test) | Δ avg | Δ max (% of avg) | Tripped |"
    )
    lines.append(
        "|-------|-------|-------|-----|--------------------|-------|------------------|---------|"
    )
    for d in deltas:
        c = d.current
        tripped = "—"
        if d.avg_tripped or d.max_tripped:
            tripped_parts = []
            if d.avg_tripped:
                tripped_parts.append("avg")
            if d.max_tripped:
                tripped_parts.append("max")
            tripped = "**" + "+".join(tripped_parts) + "**"
        lines.append(
            f"| {c.suite} | {c.count} | {c.total_s:.2f}s | {c.avg_ms:.1f}ms | "
            f"{c.max_test_name} ({c.max_ms:.0f}ms) | "
            f"{fmt_pct(d.avg_delta_pct)} | {fmt_pct(d.max_delta_pct_of_avg)} | {tripped} |"
        )
    lines.append("")
    flagged = [d for d in deltas if d.avg_tripped or d.max_tripped]
    if flagged:
        lines.append("### Threshold trips — require sprint-review disposition")
        lines.append("")
        for d in flagged:
            lines.append(f"- **{d.current.suite}**:")
            for f in d.flags:
                lines.append(f"  - {f}")
        lines.append("")
        lines.append(
            "Operator at sprint review chooses for each trip: "
            "**accept** (justified, log in sprint Decision log) or "
            "**rework** (create a rework task per §5.5)."
        )
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Emit Test-runtime block for a sprint coverage summary.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--suite", action="append", required=True,
                    help="Suite name. Each --suite is followed by exactly one "
                         "report-source flag describing how to read its results.")
    ap.add_argument("--junit-xml", action="append", default=[],
                    help="Glob for JUnit-style XML files for the preceding --suite.")
    ap.add_argument("--vitest-json", action="append", default=[],
                    help="Path to a Vitest JSON reporter file.")
    ap.add_argument("--playwright-json", action="append", default=[],
                    help="Path to a Playwright JSON reporter (results.json).")
    ap.add_argument("--baseline", default=None,
                    help="Path to the previous sprint's .coverage.md, if any.")
    ap.add_argument("--avg-threshold-pct", type=float, default=5.0,
                    help="Threshold for Δavg, as percent of baseline avg. Default 5.")
    ap.add_argument("--max-threshold-pct-of-avg", type=float, default=25.0,
                    help="Threshold for Δmax, as percent of current sprint avg. Default 25.")
    ap.add_argument("--out", default=None,
                    help="Write the Markdown block to this path. Default: stdout.")
    args = ap.parse_args(argv)

    # Pair --suite N with the Nth report-source. We accept the report
    # sources in any order (junit, vitest, playwright); the count must
    # match --suite count, total.
    sources: list[tuple[str, str]] = []
    for s in args.junit_xml:
        sources.append(("junit-xml", s))
    for s in args.vitest_json:
        sources.append(("vitest-json", s))
    for s in args.playwright_json:
        sources.append(("playwright-json", s))
    if len(sources) != len(args.suite):
        print(
            f"error: --suite count ({len(args.suite)}) does not match "
            f"report-source count ({len(sources)}). Each --suite needs one "
            f"of --junit-xml / --vitest-json / --playwright-json.",
            file=sys.stderr,
        )
        return 1

    baseline = read_baseline(args.baseline)

    deltas: list[SuiteDelta] = []
    for suite_name, (kind, src) in zip(args.suite, sources):
        if kind == "junit-xml":
            cases = list(parse_junit_xml_glob(src))
        elif kind == "vitest-json":
            cases = list(parse_vitest_json(src))
        elif kind == "playwright-json":
            cases = list(parse_playwright_json(src))
        else:
            print(f"error: unknown report kind {kind!r}", file=sys.stderr)
            return 2
        current = aggregate(suite_name, cases)
        deltas.append(compare(current, baseline.get(suite_name),
                              args.avg_threshold_pct,
                              args.max_threshold_pct_of_avg))

    block = format_markdown(deltas, args.avg_threshold_pct,
                            args.max_threshold_pct_of_avg)

    if args.out:
        Path(args.out).write_text(block)
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        print(block)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
