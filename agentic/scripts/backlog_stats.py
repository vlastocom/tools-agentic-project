#!/usr/bin/env python3
"""
Backlog Statistics Script

Generates statistics and reports about the backlog status with hierarchical
box-drawing tables, priority breakdowns, and completion progress bars.

Usage:
    python scripts/backlog_stats.py              # Human-readable format
    python scripts/backlog_stats.py --format json  # JSON output

Exit code: Always 0 (informational only)
"""

import sys
import os
import json
import argparse
from collections import defaultdict, Counter

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backlog_utils import (
    read_backlog,
    parse_tasks_table,
    parse_task_details,
    parse_epics,
    parse_areas,
    parse_sprints,
    extract_epic_from_task_id,
    merge_task_info,
    VALID_STATUSES
)


# ── Box-drawing table renderer ────────────────────────────────────────────────

def render_box_table(headers, rows, alignments=None):
    """
    Render a table with box-drawing borders.

    Args:
        headers:    List of header strings.
        rows:       List of lists (one inner list per row).
        alignments: List of '<', '>', or '^' per column (left, right, centre).
                    Defaults to left for column 0, centre for the rest.

    Returns:
        Multi-line string with the rendered table.
    """
    cols = len(headers)
    if alignments is None:
        alignments = ['<'] + ['^'] * (cols - 1)

    # Calculate minimum column widths from content
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    # Add padding
    widths = [w + 2 for w in widths]

    def fmt_cell(text, width, align):
        inner = width - 2
        if align == '>':
            return ' ' + text.rjust(inner) + ' '
        elif align == '^':
            return ' ' + text.center(inner) + ' '
        else:
            return ' ' + text.ljust(inner) + ' '

    def horizontal(left, mid, right, fill='─'):
        parts = [fill * w for w in widths]
        return left + mid.join(parts) + right

    lines = []
    # Top border
    lines.append(horizontal('┌', '┬', '┐'))

    # Header row — always centred
    hdr_cells = [fmt_cell(headers[i], widths[i], '^') for i in range(cols)]
    lines.append('│' + '│'.join(hdr_cells) + '│')

    # Separator
    lines.append(horizontal('├', '┼', '┤'))

    # Data rows
    for row in rows:
        cells = [fmt_cell(row[i], widths[i], alignments[i]) for i in range(cols)]
        lines.append('│' + '│'.join(cells) + '│')

    # Bottom border
    lines.append(horizontal('└', '┴', '┘'))

    return '\n'.join(lines)


# ── Data helpers ──────────────────────────────────────────────────────────────

def _area_code_from_epic(epic_id):
    """Extract area code from epic ID (e.g. 'AUTH-02' -> 'AUTH')."""
    return epic_id.split('-')[0] if epic_id else 'UNKNOWN'


def _format_count_pct(count, total):
    """Format a count with its percentage, e.g. '12 (14%)'."""
    if total == 0:
        return '0 (0%)'
    pct = round(count / total * 100)
    return f'{count} ({pct}%)'


def _format_aligned_count_pct_columns(raw_rows, count_pct_col_indices):
    """
    Format rows so that count and percentage sub-parts align independently
    within each column.

    Args:
        raw_rows:             List of lists. Count/pct columns hold (count, total)
                              tuples; other columns hold plain strings.
        count_pct_col_indices: Set of column indices that contain (count, total) data.

    Returns:
        List of lists with all cells as formatted strings.
    """
    if not raw_rows:
        return []

    cols = len(raw_rows[0])

    # Pre-compute pct values and determine max widths per column
    max_count_w = {}
    max_pct_w = {}
    pct_values = []  # parallel structure: pct_values[row][col] = pct int

    for row in raw_rows:
        row_pcts = {}
        for ci in count_pct_col_indices:
            count, total = row[ci]
            pct = round(count / total * 100) if total else 0
            row_pcts[ci] = pct
            cw = len(str(count))
            pw = len(str(pct))
            max_count_w[ci] = max(max_count_w.get(ci, 0), cw)
            max_pct_w[ci] = max(max_pct_w.get(ci, 0), pw)
        pct_values.append(row_pcts)

    # Format rows: count is right-aligned, pct% is right-aligned,
    # variable gap sits between count and opening paren.
    # Target cell width per column = max_count_w + max_pct_w + 4  ("·(xx%)")
    # Layout: {count:>cw}{gap}({pct:>pw}%)
    formatted = []
    for ri, row in enumerate(raw_rows):
        out = []
        for ci in range(cols):
            if ci in count_pct_col_indices:
                count, total = row[ci]
                pct = pct_values[ri][ci]
                cstr = str(count).rjust(max_count_w[ci])
                pstr = f'({pct}%)'.rjust(max_pct_w[ci] + 3)  # +3 for '(' and '%)'
                out.append(f'{cstr} {pstr}')
            else:
                out.append(row[ci])
        formatted.append(out)

    return formatted


def _build_hierarchy(tasks, areas, epics):
    """
    Build area -> epic -> [tasks] hierarchy.

    Returns:
        ordered_areas: list of (area_code, area_short_name)
        area_epics:    dict  area_code -> [(epic_id, epic_short_name)]
        epic_tasks:    dict  epic_id -> [task]
    Only areas/epics that have at least one task are included.
    """
    # Index area and epic metadata
    area_map = {a.code: a.short_name for a in areas}
    epic_map = {e.epic_id: e.short_name for e in epics}

    # Group tasks by epic
    epic_task_map = defaultdict(list)
    for t in tasks:
        eid = extract_epic_from_task_id(t.task_id)
        epic_task_map[eid].append(t)

    # Group epics by area, preserving parse order
    area_epic_order = defaultdict(list)
    seen_epics = set()
    for e in epics:
        ac = _area_code_from_epic(e.epic_id)
        if e.epic_id in epic_task_map and e.epic_id not in seen_epics:
            area_epic_order[ac].append((e.epic_id, epic_map.get(e.epic_id, e.epic_id)))
            seen_epics.add(e.epic_id)

    # Ordered areas (only those with tasks)
    ordered_areas = []
    for a in areas:
        if a.code in area_epic_order:
            ordered_areas.append((a.code, a.short_name))

    return ordered_areas, dict(area_epic_order), dict(epic_task_map)


def _count_by_field(task_list, field, values):
    """Count tasks grouped by a field value."""
    c = Counter(getattr(t, field) for t in task_list)
    return {v: c.get(v, 0) for v in values}


# ── BacklogStats ──────────────────────────────────────────────────────────────

class BacklogStats:
    """Generate statistics about the backlog."""

    def __init__(self):
        self.stats = {}
        self._tasks = []
        self._areas = []
        self._epics = []

    def generate(self) -> dict:
        """Generate all statistics and return as dict."""
        try:
            content = read_backlog()
        except Exception as e:
            return {'error': f'Failed to read backlog: {e}'}

        table_tasks = parse_tasks_table(content)
        detail_tasks = parse_task_details(content)
        self._tasks = merge_task_info(table_tasks, detail_tasks)
        self._epics = parse_epics(content)
        self._areas = parse_areas(content)

        tasks = self._tasks
        ordered_areas, area_epics, epic_tasks = _build_hierarchy(
            tasks, self._areas, self._epics
        )

        # ── overall counts ────────────────────────────────────────────────
        self.stats['total_tasks'] = len(tasks)
        self.stats['total_epics'] = len(self._epics)
        self.stats['total_areas'] = len(self._areas)
        self.stats['by_status'] = dict(Counter(t.status for t in tasks))
        self.stats['by_priority'] = dict(Counter(t.priority for t in tasks))

        # ── hierarchical status breakdown ─────────────────────────────────
        status_order = ['GROOM', 'TODO', 'DOING', 'DONE', 'DROP']
        has_doing = any(t.status == 'DOING' for t in tasks)
        active_statuses = [s for s in status_order if has_doing or s != 'DOING']

        hierarchy = []
        for area_code, area_name in ordered_areas:
            area_tasks_all = []
            epic_rows = []
            for epic_id, epic_name in area_epics.get(area_code, []):
                etasks = epic_tasks.get(epic_id, [])
                area_tasks_all.extend(etasks)
                epic_rows.append({
                    'id': epic_id,
                    'name': epic_name,
                    'counts': _count_by_field(etasks, 'status', active_statuses),
                    'total': len(etasks),
                    'priority_counts': _count_by_field(
                        [t for t in etasks if t.status in ('GROOM', 'TODO', 'DOING')],
                        'priority', ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
                    ),
                    'tasks': etasks,
                })
            hierarchy.append({
                'code': area_code,
                'name': area_name,
                'counts': _count_by_field(area_tasks_all, 'status', active_statuses),
                'total': len(area_tasks_all),
                'priority_counts': _count_by_field(
                    [t for t in area_tasks_all if t.status in ('GROOM', 'TODO', 'DOING')],
                    'priority', ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
                ),
                'epics': epic_rows,
                'tasks': area_tasks_all,
            })

        self.stats['hierarchy'] = hierarchy
        self.stats['active_statuses'] = active_statuses

        # ── sprint summary ────────────────────────────────────────────────
        sprints = parse_sprints(content)
        sprint_status_map = {s.sprint_id: s.status for s in sprints}

        by_sprint = defaultdict(lambda: {'total': 0, 'done': 0, 'dropped': 0, 'status': ''})
        unassigned = 0
        for t in tasks:
            if t.sprint:
                by_sprint[t.sprint]['status'] = sprint_status_map.get(t.sprint, '')
                if t.status == 'DROP':
                    by_sprint[t.sprint]['dropped'] += 1
                else:
                    by_sprint[t.sprint]['total'] += 1
                    if t.status == 'DONE':
                        by_sprint[t.sprint]['done'] += 1
            else:
                unassigned += 1
        self.stats['sprint_summary'] = {
            'sprints': dict(by_sprint),
            'unassigned': unassigned,
            'assigned': len(tasks) - unassigned,
        }

        # ── documentation coverage ────────────────────────────────────────
        done_tasks = [t for t in tasks if t.status == 'DONE']
        done_with_docs = sum(
            1 for t in done_tasks
            if t.documentation and t.documentation != 'No documentation'
        )
        self.stats['documentation'] = {
            'done_total': len(done_tasks),
            'done_with_docs': done_with_docs,
            'coverage_pct': round(done_with_docs / len(done_tasks) * 100) if done_tasks else 0,
        }

        # ── blocked tasks ─────────────────────────────────────────────────
        done_ids = {t.task_id for t in tasks if t.status == 'DONE'}
        blocked = []
        for t in tasks:
            if t.status in ('GROOM', 'TODO', 'DOING') and t.dependencies:
                unresolved = [d for d in t.dependencies if d not in done_ids]
                if unresolved:
                    blocked.append({
                        'task_id': t.task_id,
                        'short_name': t.short_name,
                        'waiting_on': unresolved,
                    })
        self.stats['blocked_tasks'] = blocked

        # ── dependency stats (kept for JSON compat) ───────────────────────
        self.stats['tasks_with_dependencies'] = sum(1 for t in tasks if t.dependencies)

        return self.stats

    # ── Human-readable output ─────────────────────────────────────────────────

    def print_human_readable(self):
        """Print statistics as professional box-drawing tables."""
        if 'error' in self.stats:
            print(f"Error: {self.stats['error']}")
            return

        self._print_status_table()
        print()
        self._print_priority_table()
        print()
        self._print_progress_bars()
        print()
        self._print_additional_stats()

    def _print_status_table(self):
        """Section 1: Overall statistics table with area/epic hierarchy."""
        hierarchy = self.stats['hierarchy']
        active_statuses = self.stats['active_statuses']
        tasks = self._tasks
        total = len(tasks)

        print('TASK STATUS OVERVIEW')
        print()

        headers = ['Area / Epic'] + active_statuses + ['TOTAL']
        alignments = ['<'] + ['>'] * (len(active_statuses) + 1)
        # Column indices that hold (count, total) tuples
        cpct_cols = set(range(1, 1 + len(active_statuses)))

        # Build rows with raw (count, total) tuples for status columns
        raw_rows = []

        # Top row: Nest total
        nest_counts = _count_by_field(tasks, 'status', active_statuses)
        nest_row = ['Nest']
        for s in active_statuses:
            nest_row.append((nest_counts[s], total))
        nest_row.append(str(total))
        raw_rows.append(nest_row)

        # Area and epic rows with tree connectors
        for ai, area in enumerate(hierarchy):
            is_last_area = (ai == len(hierarchy) - 1)
            area_connector = ' \u2514' if is_last_area else ' \u251c'
            area_row = [f'{area_connector} {area["code"]}']
            for s in active_statuses:
                area_row.append((area['counts'][s], area['total']))
            area_row.append(str(area['total']))
            raw_rows.append(area_row)

            area_prefix = '  ' if is_last_area else ' \u2502'
            for ei, epic in enumerate(area['epics']):
                is_last_epic = (ei == len(area['epics']) - 1)
                epic_connector = '\u2514' if is_last_epic else '\u251c'
                epic_row = [f'{area_prefix}   {epic_connector} {epic["id"]}']
                for s in active_statuses:
                    epic_row.append((epic['counts'][s], epic['total']))
                epic_row.append(str(epic['total']))
                raw_rows.append(epic_row)

        rows = _format_aligned_count_pct_columns(raw_rows, cpct_cols)
        print(render_box_table(headers, rows, alignments))

    def _print_priority_table(self):
        """Section 2: Open tasks by priority."""
        hierarchy = self.stats['hierarchy']
        priorities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        open_tasks = [t for t in self._tasks if t.status in ('GROOM', 'TODO', 'DOING')]

        print('OPEN TASKS BY PRIORITY')
        print()

        headers = ['Area / Epic'] + priorities + ['TOTAL']
        alignments = ['<'] + ['>'] * (len(priorities) + 1)
        cpct_cols = set(range(1, 1 + len(priorities)))

        raw_rows = []

        # Nest total
        nest_total = len(open_tasks)
        nest_pri = _count_by_field(open_tasks, 'priority', priorities)
        nest_row = ['Nest']
        for p in priorities:
            nest_row.append((nest_pri[p], nest_total))
        nest_row.append(str(nest_total))
        raw_rows.append(nest_row)

        for ai, area in enumerate(hierarchy):
            is_last_area = (ai == len(hierarchy) - 1)
            area_connector = ' \u2514' if is_last_area else ' \u251c'
            area_open = [t for t in area['tasks'] if t.status in ('GROOM', 'TODO', 'DOING')]
            area_total = len(area_open)
            area_row = [f'{area_connector} {area["code"]}']
            for p in priorities:
                area_row.append((area['priority_counts'][p], area_total))
            area_row.append(str(area_total))
            raw_rows.append(area_row)

            area_prefix = '  ' if is_last_area else ' \u2502'
            for ei, epic in enumerate(area['epics']):
                is_last_epic = (ei == len(area['epics']) - 1)
                epic_connector = '\u2514' if is_last_epic else '\u251c'
                epic_open = [t for t in epic['tasks'] if t.status in ('GROOM', 'TODO', 'DOING')]
                epic_total = len(epic_open)
                epic_row = [f'{area_prefix}   {epic_connector} {epic["id"]}']
                for p in priorities:
                    epic_row.append((epic['priority_counts'][p], epic_total))
                epic_row.append(str(epic_total))
                raw_rows.append(epic_row)

        rows = _format_aligned_count_pct_columns(raw_rows, cpct_cols)
        print(render_box_table(headers, rows, alignments))

    def _print_progress_bars(self):
        """Section 3: Completion progress bars per area/epic."""
        hierarchy = self.stats['hierarchy']
        bar_width = 50

        print('COMPLETION PROGRESS')
        print('(excludes DROP status and LOW priority tasks)')
        print()

        def _progress_data(task_list):
            """Return (done, total, bar_string) for relevant tasks."""
            relevant = [
                t for t in task_list
                if t.status != 'DROP' and t.priority != 'LOW'
            ]
            total = len(relevant)
            done = sum(1 for t in relevant if t.status == 'DONE')
            if total == 0:
                filled = 0
            else:
                filled = round(done / total * bar_width)
            bar = '\u2593' * filled + '\u2591' * (bar_width - filled)
            return done, total, bar

        # Collect raw row data: (label, bar, done, total)
        raw_data = []

        # Nest row
        done, total, bar = _progress_data(self._tasks)
        raw_data.append(('Nest', bar, done, total))

        for ai, area in enumerate(hierarchy):
            is_last_area = (ai == len(hierarchy) - 1)
            area_connector = ' \u2514' if is_last_area else ' \u251c'
            done, total, bar = _progress_data(area['tasks'])
            raw_data.append((f'{area_connector} {area["code"]}', bar, done, total))

            area_prefix = '  ' if is_last_area else ' \u2502'
            for ei, epic in enumerate(area['epics']):
                is_last_epic = (ei == len(area['epics']) - 1)
                epic_connector = '\u2514' if is_last_epic else '\u251c'
                done, total, bar = _progress_data(epic['tasks'])
                raw_data.append((
                    f'{area_prefix}   {epic_connector} {epic["id"]}',
                    bar, done, total
                ))

        # Compute max widths for done and total sub-columns
        max_done_w = max(len(str(d)) for _, _, d, _ in raw_data)
        max_total_w = max(len(str(t)) for _, _, _, t in raw_data)
        max_pct_w = max(
            len(str(round(d / t * 100) if t else 0))
            for _, _, d, t in raw_data
        )

        # Format into string rows for the box table
        rows = []
        for label, bar, done, total in raw_data:
            pct = round(done / total * 100) if total else 0
            fraction = f'{str(done).rjust(max_done_w)}/{str(total).ljust(max_total_w)}'
            pct_str = f'({str(pct).rjust(max_pct_w)}%)'
            rows.append([label, bar, fraction, pct_str])

        headers = ['Area / Epic', 'Progress', 'Done', '%']
        alignments = ['<', '<', '>', '>']
        print(render_box_table(headers, rows, alignments))

    def _print_additional_stats(self):
        """Section 4: Sprint summary, documentation coverage, blocked tasks."""
        sprint = self.stats['sprint_summary']
        docs = self.stats['documentation']
        blocked = self.stats['blocked_tasks']

        print('ADDITIONAL STATISTICS')
        print()

        # Sprint summary
        print('Sprint summary')
        print(f'  Assigned to sprint: {sprint["assigned"]}   '
              f'Unassigned: {sprint["unassigned"]}')
        for name, info in sorted(sprint['sprints'].items()):
            done_pct = round(info['done'] / info['total'] * 100) if info['total'] else 0
            status_label = f' [{info["status"]}]' if info.get('status') else ''
            dropped_label = f', {info["dropped"]} dropped' if info.get('dropped') else ''
            print(f'  {name}{status_label}: {info["done"]}/{info["total"]} done ({done_pct}%{dropped_label})')
        print()

        # Documentation coverage
        print('Documentation coverage (DONE tasks)')
        print(f'  {docs["done_with_docs"]}/{docs["done_total"]} documented ({docs["coverage_pct"]}%)')
        print()

        # Blocked tasks
        print(f'Blocked tasks ({len(blocked)})')
        if blocked:
            for b in blocked:
                deps = ', '.join(b['waiting_on'])
                print(f'  {b["task_id"]}: {b["short_name"]}')
                print(f'    waiting on: {deps}')
        else:
            print('  None')
        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate backlog statistics'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )

    args = parser.parse_args()

    stats_generator = BacklogStats()
    stats = stats_generator.generate()

    if args.format == 'json':
        # Strip non-serialisable internal data from hierarchy for JSON
        json_stats = {}
        for k, v in stats.items():
            if k == 'hierarchy':
                clean = []
                for area in v:
                    a = {key: val for key, val in area.items() if key != 'tasks'}
                    a['epics'] = [
                        {ek: ev for ek, ev in e.items() if ek != 'tasks'}
                        for e in area['epics']
                    ]
                    clean.append(a)
                json_stats[k] = clean
            else:
                json_stats[k] = v
        print(json.dumps(json_stats, indent=2))
    else:
        stats_generator.print_human_readable()

    sys.exit(0)


if __name__ == '__main__':
    main()
