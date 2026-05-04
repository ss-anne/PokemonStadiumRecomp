#!/usr/bin/env python3
"""Show trace_recent around the crash."""
import json

r = json.load(open('build/last_run_report.json'))
tr = r.get('trace_recent', {})
ents = tr.get('entries', [])
print(f"trace_recent: write_idx={tr.get('write_idx')}, n_entries={len(ents)}")
print("Last 60 entries:")
for n in ents[-60:]:
    print(f"  {n}")
