#!/usr/bin/env python3
"""Find the thread that crashed and its callstack."""
import json

r = json.load(open('build/last_run_report.json'))
seh = r['seh']
crash_addr = seh['address']
print(f'crash_addr=0x{crash_addr:x}')
print(f'fault_host=0x{seh.get("fault_host",0):x}')
print(f'rdram_off=0x{seh.get("rdram_off",0):x}  decoded_vaddr=0x{seh.get("decoded_vaddr",0):x}  access={seh.get("access")}')
print()

threads = r.get('threads', [])
print(f'Total threads: {len(threads)}')
print()

# Threads with Stadium-recomp / extras / pkmnstadium frames
print('=== Threads with Stadium-related frames ===')
for t in threads:
    frames = t.get('frames', [])
    matched = False
    for f in frames:
        n = f.get('name','')
        fl = f.get('file','')
        if ('PokemonStadiumRecomp' in fl or 'extras' in fl or 'recompiled' in fl
            or 'pkmnstadium_' in n or 'funcs_' in fl or 'funcs_' in n
            or '_alFx' in n or 'MainBus' in n or 'n_al' in n
            or 'recomp' in n.lower()):
            matched = True
            break
    if not matched:
        continue
    print(f"tid={t.get('tid')} name={t.get('name')!r} rip=0x{t.get('rip',0):x}")
    for fr in frames[:12]:
        print(f"  [{fr['i']}] 0x{fr['pc']:x}  {fr['name']}  {fr['file']}:{fr['line']}")
    print()

# Threads with NO name but with frames containing Stadium pcs
print('=== Unnamed threads with non-trivial frames ===')
for t in threads:
    if t.get('name'): continue
    frames = t.get('frames', [])
    if not frames: continue
    top = frames[0]
    if 'ZwWaitForSingleObject' in top.get('name','') or 'NtDelayExecution' in top.get('name',''):
        continue
    print(f"tid={t.get('tid')} rip=0x{t.get('rip',0):x}")
    for fr in frames[:10]:
        print(f"  [{fr['i']}] 0x{fr['pc']:x}  {fr['name']}  {fr['file']}:{fr['line']}")
    print()
