#!/usr/bin/env python3
"""Quick summary of audio rings + crash thread from last_run_report.json."""
import json

r = json.load(open('build/last_run_report.json'))
print('reason:', r.get('reason'))
seh = r.get('seh', {})
print(f"seh: addr=0x{seh.get('address',0):x}  decoded_vaddr=0x{seh.get('decoded_vaddr',0):x}  access={seh.get('access')}")
status = r.get('status', {})
print(f"frame={status.get('frame')}  send_dl={status.get('send_dl')}  submit_audio={status.get('submit_audio')}  sp_complete={status.get('sp_complete')}")
print()

for key in ('audio_afx_in', 'audio_afx_out', 'audio_mbp_pre', 'audio_mbp_disp'):
    block = r.get(key, {})
    seq = block.get('seq', 0)
    evs = block.get('events', [])
    print(f"{key}: seq={seq}  ring_size={len(evs)}")
    for e in evs[-8:]:
        print(f"  {e}")
    print()

# Crash thread
crash_addr = seh.get('address', 0)
print('=== Crash thread (rip == seh.address) ===')
for t in r.get('threads', []):
    if t.get('rip') == crash_addr:
        print(f"tid={t.get('tid')} name={t.get('name')!r}")
        for fr in t.get('frames', [])[:10]:
            print(f"  [{fr['i']}] 0x{fr['pc']:x}  {fr['name']}  {fr['file']}:{fr['line']}")
        break
