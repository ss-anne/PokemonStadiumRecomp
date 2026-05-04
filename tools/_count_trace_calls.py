#!/usr/bin/env python3
"""Count function calls in trace ring around the crash."""
import json

r = json.load(open('build/last_run_report.json'))
ents = r.get('trace_recent', {}).get('entries', [])
print('Total entries in trace ring:', len(ents))
counts = {}
for e in ents:
    counts[e] = counts.get(e, 0) + 1
for k in ('n_alFxPull','n_alMainBusPull','n_alSavePull','n_alAudioFrame'):
    print(f'  {k}: {counts.get(k, 0)}')
print()
for k in ('n_alFxPull','n_alMainBusPull'):
    idxs = [i for i, e in enumerate(ents) if e == k]
    if idxs:
        print(f'{k} last 5 indices in ring: {idxs[-5:]}')
print()
# Show what's around the LAST n_alMainBusPull entry in ring
last_mbp = [i for i, e in enumerate(ents) if e == 'n_alMainBusPull']
if last_mbp:
    li = last_mbp[-1]
    lo, hi = max(0, li - 5), min(len(ents), li + 6)
    print(f'Context around last n_alMainBusPull (idx {li}):')
    for i in range(lo, hi):
        marker = '  >' if i == li else '   '
        print(f'{marker} [{i}] {ents[i]}')
