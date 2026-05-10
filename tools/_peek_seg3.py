"""Peek RDRAM at the resolved seg-3 anchors for the menu border
textures + wallpaper. Pretty-print as 16-bit big-endian texels so we
can eyeball whether the data is plausible I/16b texture content.
"""
import socket, json, struct, sys

def ask(cmd):
    s = socket.socket(); s.settimeout(5); s.connect(('127.0.0.1',4371))
    s.sendall((json.dumps(cmd)+'\n').encode())
    return json.loads(s.recv(32768).decode())

def hexdump_16b(name, addr, hex_payload):
    if not hex_payload:
        print(f'{name} 0x{addr:08x}: NO DATA')
        return
    raw = bytes.fromhex(hex_payload)
    print(f'\n{name} 0x{addr:08x} ({len(raw)} bytes):')
    # 16-bit BE words, 8 per row.
    for row in range(0, len(raw), 16):
        words = []
        for j in range(0, 16, 2):
            if row + j + 2 <= len(raw):
                w = struct.unpack('>H', raw[row+j:row+j+2])[0]
                words.append(f'{w:04x}')
        print('  ', ' '.join(words))

anchors = [
    ('seg3+0xf240 (corner-1 8x8 I16)', 0x801b7790, 128),
    ('seg3+0xf340 (corner-3 8x8 I16)', 0x801b7890, 128),
    ('seg3+0xf400 (corner-bracket 16x16 I16)', 0x801b7950, 128),
    ('seg3+0xf780 (wallpaper start)',  0x801b7cd0, 128),
    ('seg3+0xa820 (warning slab 1 RGBA16)',  0x801b2d70, 64),
]

for name, addr, n in anchors:
    r = ask({'cmd':'rdram_peek','addr':addr,'n':n})
    hexdump_16b(name, addr, r.get('hex',''))
