#!/usr/bin/env python3
"""Inspect the n_alMainBusPull crash from last_run artifacts."""
import json

with open('build/last_run_report.json', 'r') as f:
    r = json.load(f)

# SEH
print('=== SEH ===')
seh = r.get('seh', {})
print(f"  decoded_vaddr=0x{seh.get('decoded_vaddr',0):08x}  access={seh.get('access')}")
print()

# trace_recent
tr = r.get('trace_recent', {})
events = tr.get('events', tr) if isinstance(tr, dict) else tr
if isinstance(events, list):
    print(f'=== trace_recent ({len(events)} events, last 60) ===')
    for e in events[-60:]:
        if isinstance(e, dict):
            pc = e.get('pc', 0)
            tag = e.get('tag', e.get('kind', e.get('type', '')))
            extra = ''
            for k in ('a0','a1','a2','a3','v0','s0','s7','ra','seq','ms'):
                if k in e:
                    v = e[k]
                    if isinstance(v, int) and k not in ('seq','ms'):
                        extra += f' {k}=0x{v:x}'
                    else:
                        extra += f' {k}={v}'
            print(f"  pc=0x{pc:08x} {tag}{extra}")
        else:
            print(f'  {e}')
print()

# libultra_recent — has thread context
lu = r.get('libultra_recent', {})
events = lu.get('events', lu) if isinstance(lu, dict) else lu
if isinstance(events, list):
    print(f'=== libultra_recent ({len(events)} events, last 30) ===')
    for e in events[-30:]:
        if isinstance(e, dict):
            print(f"  {e}")
        else:
            print(f'  {e}')
print()

# mesg_recent
mr = r.get('mesg_recent', {})
events = mr.get('events', mr) if isinstance(mr, dict) else mr
if isinstance(events, list):
    print(f'=== mesg_recent (last 20 of {len(events)}) ===')
    for e in events[-20:]:
        print(f"  {e}")
print()

# threads with callstacks
print('=== threads (audio + named) ===')
for t in r.get('threads', []):
    name = t.get('name', '')
    keys = list(t.keys())
    if 'Audio' in name or 'audio' in name.lower() or name in ('Gfx Thread','SP Task Thread','SDLAudioP2',''):
        if name == '':
            # Skip generic threads unless they have something interesting
            for k in keys:
                if k not in ('tid','id'):
                    if isinstance(t[k], list) and len(t[k]) > 0:
                        print(f"  tid={t.get('tid')} name='' keys={keys}")
                        break
            continue
        print(f"  tid={t.get('tid')} name={name!r} keys={keys}")
        for k in keys:
            if k in ('tid','name'): continue
            v = t[k]
            if isinstance(v, list) and len(v) > 0:
                print(f"    {k}: ({len(v)} entries, last 8)")
                for x in v[-8:]:
                    print(f"      {x}")
            elif isinstance(v, dict):
                print(f"    {k}: {v}")
            else:
                print(f"    {k}={v}")
