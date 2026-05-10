"""Targeted second peek pass: verify the seg-3 RGBA16 slabs are
genuinely empty (multi-row dump) and inspect the kseg0 controller-
candidate textures used by the same DL.
"""
import socket, json, struct

def ask(cmd):
    s = socket.socket(); s.settimeout(5); s.connect(('127.0.0.1',4371))
    s.sendall((json.dumps(cmd)+'\n').encode())
    return json.loads(s.recv(32768).decode())

def hexdump_16b(name, addr, n):
    r = ask({'cmd':'rdram_peek','addr':addr,'n':n})
    h = r.get('hex','')
    if not h:
        print(f'{name} 0x{addr:08x}: NO DATA  err={r.get("error")}')
        return
    raw = bytes.fromhex(h)
    print(f'\n{name} 0x{addr:08x} ({len(raw)} bytes):')
    for row in range(0, len(raw), 16):
        words = []
        for j in range(0, 16, 2):
            if row + j + 2 <= len(raw):
                w = struct.unpack('>H', raw[row+j:row+j+2])[0]
                words.append(f'{w:04x}')
        print('  ', ' '.join(words))

# Slab 1 was zero — read more rows of it.
hexdump_16b('seg3+0xa820 slab 1 (256 bytes ~ 8 rows of 16 RGBA16 pixels)', 0x801b2d70, 256)

# Cross-screen kseg0 textures used 10x and 9x in the menu DLs.
hexdump_16b('kseg0 0x80151d60 (used 10x)', 0x80151d60, 128)
hexdump_16b('kseg0 0x80147920 (used 9x)',  0x80147920, 128)

# Try the seg3 corner BEFORE the slab to compare to "good" content.
hexdump_16b('seg3+0xa720 (just before slab 1)', 0x801b2c70, 64)
