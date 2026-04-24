---
name: backlog-reporting
description: Use this skill when asked for backlog statistics, project status reports, during sprint planning to review metrics or when you need the backlog metrics internally for other tasks.
---

# Backlog Reporting

The list of metrics available from the `backlog_stats.py` script can be found in the
[backlog scripts guide](../../guides/backlog-scripts.md).

## Human-readable report

When asked to display backlog statistics, generate them using

```bash
python agentic/scripts/backlog_stats.py
```

## JSON report

When the metrics are needed for other tasks or computations, generate them using

```bash
python agentic/scripts/backlog_stats.py --format json
```
