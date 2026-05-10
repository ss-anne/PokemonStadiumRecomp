"""Second-pass peek of every distinct SETTIMG address from the Game
Pak Check DL. Tag each as ZERO / NONZERO so we can see whether
anything has changed since the first probe and which addresses still
have no texture content.
"""
import socket, json, struct

def ask(cmd):
    s = socket.socket(); s.settimeout(5); s.connect(('127.0.0.1',4371))
    s.sendall((json.dumps(cmd)+'\n').encode())
    return json.loads(s.recv(32768).decode())

# All distinct SETTIMG addresses from Game Pak Check (resolved).
# segmented: gSegments[3] = 0x001a8550 → +offset, kseg0 base 0x80000000.
SEG3 = 0x801a8550
ADDRS = [
    # segmented seg-3 addresses (resolved kseg0)
    ('seg3+0xa820 (slab1, RGBA16)',     SEG3 + 0x0a820),
    ('seg3+0xb820 (slab2, RGBA16)',     SEG3 + 0x0b820),
    ('seg3+0xc820 (slab3, RGBA16)',     SEG3 + 0x0c820),
    ('seg3+0xd820 (slab4, RGBA16)',     SEG3 + 0x0d820),
    ('seg3+0xf240 (deco I16, used 4)',  SEG3 + 0x0f240),
    ('seg3+0xf280 (deco I16)',          SEG3 + 0x0f280),
    ('seg3+0xf2c0 (deco I16, used 8)',  SEG3 + 0x0f2c0),
    ('seg3+0xf300 (deco I16)',          SEG3 + 0x0f300),
    ('seg3+0xf340 (deco I16, used 8)',  SEG3 + 0x0f340),
    ('seg3+0xf400 (deco I16, used 4)',  SEG3 + 0x0f400),
    ('seg3+0xf780 (wallpaper)',         SEG3 + 0x0f780),
    # kseg0 direct addresses from the histogram
    ('kseg0 0x80151460 (used 2)',  0x80151460),
    ('kseg0 0x80151d60 (used 2)',  0x80151d60),
    ('kseg0 0x80152ae0 (used 2)',  0x80152ae0),
]

def status(addr, n=64):
    r = ask({'cmd':'rdram_peek','addr':addr,'n':n})
    h = r.get('hex','')
    if not h:
        return None, None
    raw = bytes.fromhex(h)
    nonzero = sum(1 for b in raw if b != 0)
    first8 = raw[:8].hex()
    return nonzero, first8

print(f"{'addr':<40s}  nonzero/total  first8")
for name, addr in ADDRS:
    nz, first8 = status(addr, 64)
    if nz is None:
        print(f"  {name:<38s}  ERROR")
    else:
        tag = 'ALL-ZERO' if nz == 0 else f'{nz}/64'
        print(f"  {name:<38s}  {tag:<13s}  {first8}")
