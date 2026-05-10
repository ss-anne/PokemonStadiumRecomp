"""Pull rt64_segments + status, then compute resolved kseg0 addrs for
the seg-3 border-decoration anchors that the menu DLs reference.
"""
import socket, json

def ask(cmd):
    s = socket.socket(); s.settimeout(3); s.connect(('127.0.0.1',4371))
    s.sendall((json.dumps(cmd)+'\n').encode())
    return json.loads(s.recv(8192).decode())

print('STATUS:', ask({'cmd':'status'}))
print()
r = ask({'cmd':'rt64_segments'})
print('seq=', r.get('seq'))
for i, v in enumerate(r['segments']):
    print(f'  seg[{i:2d}] = 0x{v:08x}')

print()
print('--- seg-3 anchors used by Game Pak Check + Mode Select DLs ---')
seg3 = r['segments'][3]
for off in (0x0a820, 0x0b820, 0x0c820, 0x0d820,
            0x0f240, 0x0f280, 0x0f2c0, 0x0f300, 0x0f340,
            0x0f380, 0x0f400, 0x0f480, 0x0f500, 0x0f780):
    phys = seg3 + off
    print(f'  seg3+0x{off:05x}  -> phys 0x{phys:08x}  -> kseg0 0x{0x80000000+phys:08x}')

if 'segments' in r and r['segments'][2]:
    seg2 = r['segments'][2]
    print()
    print('--- seg-2 anchors used by Mode Select DL ---')
    for off in (0x000c80, 0x000d80, 0x000e80, 0x000f80):
        phys = seg2 + off
        print(f'  seg2+0x{off:05x}  -> phys 0x{phys:08x}  -> kseg0 0x{0x80000000+phys:08x}')
