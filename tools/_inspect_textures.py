"""Extract every G_SETTIMG → G_SETTILE → G_LOADBLOCK → G_TEXRECT chain
from a captured DL and surface the (texture_addr, format, sizing,
target screen rect) tuples. Lets us spot:

  - SETTIMG addresses that are out of RDRAM (bad source pointer).
  - SETTILE formats that don't match the source pixel layout.
  - TEXRECT screen extents that suggest tiny border rules / divider
    lines (the visible corruption pattern in the menu screens).
"""
import struct, sys

PATH = sys.argv[1] if len(sys.argv) > 1 else "build/last_run_dl_pleaseselect.bin"
DL_START = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x80246180

with open(PATH, "rb") as f:
    data = f.read()

# F3DEX2 texture format / size lookup tables.
FMT = {0:"RGBA",1:"YUV",2:"CI",3:"IA",4:"I"}
SIZ = {0:"4b",1:"8b",2:"16b",3:"32b"}

i = 0
cur_timg = None       # (addr, fmt, siz)
cur_tile = None       # (uls,ult,lrs,lrt,palette,etc) for tile 0
last_settile = None   # (fmt,siz,line,tmem,tile,palette,cms,maskt,...)
texrects = []
n = 0

print(f"DL @ {DL_START:#010x}  size {len(data)} cmds {len(data)//8}")
print()

while i + 8 <= len(data):
    w0 = struct.unpack(">I", data[i:i+4])[0]
    w1 = struct.unpack(">I", data[i+4:i+8])[0]
    op = (w0 >> 24) & 0xFF
    n += 1

    if op == 0xFD:  # G_SETTIMG
        fmt = (w0 >> 21) & 0x7
        siz = (w0 >> 19) & 0x3
        cur_timg = (w1, fmt, siz)
    elif op == 0xF5:  # G_SETTILE
        fmt = (w0 >> 21) & 0x7
        siz = (w0 >> 19) & 0x3
        line = (w0 >> 9) & 0x1FF
        tmem = w0 & 0x1FF
        tile = (w1 >> 24) & 0x7
        palette = (w1 >> 20) & 0xF
        last_settile = (fmt, siz, line, tmem, tile, palette)
    elif op == 0xE4:  # G_TEXRECT
        # G_TEXRECT is 64 bits + 64 bits of follow (G_RDPHALF_1 + G_RDPHALF_2)
        ulx = (w1 >> 12) & 0xFFF
        uly = w1 & 0xFFF
        lrx = (w0 >> 12) & 0xFFF
        lry = w0 & 0xFFF
        tile = (w1 >> 24) & 0x7
        # Read the next two cmds for s,t,dsdx,dtdy
        if i + 24 <= len(data):
            n0 = struct.unpack(">I", data[i+8:i+12])[0]
            n1 = struct.unpack(">I", data[i+12:i+16])[0]
            m0 = struct.unpack(">I", data[i+16:i+20])[0]
            m1 = struct.unpack(">I", data[i+20:i+24])[0]
        else:
            n0=n1=m0=m1=0
        # ULX/ULY/LRX/LRY are 10.2 fixed-point screen coords.
        ulx_p = ulx / 4
        uly_p = uly / 4
        lrx_p = lrx / 4
        lry_p = lry / 4
        w_p = lrx_p - ulx_p
        h_p = lry_p - uly_p
        timg = cur_timg
        st = last_settile
        texrects.append({
            "off": i,
            "screen": (ulx_p, uly_p, w_p, h_p),
            "timg_addr": timg[0] if timg else None,
            "timg_fmt": FMT.get(timg[1], "?") if timg else None,
            "timg_siz": SIZ.get(timg[2], "?") if timg else None,
            "tile_fmt": FMT.get(st[0], "?") if st else None,
            "tile_siz": SIZ.get(st[1], "?") if st else None,
            "tile_line": st[2] if st else None,
            "tile_tmem": st[3] if st else None,
        })
    i += 8

print(f"=== G_TEXRECT count: {len(texrects)} ===\n")

# Categorize by screen extent.
print("=== TINY rects (likely border lines, w<=4 or h<=4) ===")
for t in texrects:
    sx, sy, sw, sh = t["screen"]
    if sw <= 4 or sh <= 4:
        print(f"  off=+{t['off']:#06x}  screen=({sx:7.2f},{sy:7.2f}) {sw:6.2f}x{sh:6.2f}  "
              f"timg={t['timg_addr']:#010x} fmt={t['timg_fmt']}/{t['timg_siz']}  "
              f"tile={t['tile_fmt']}/{t['tile_siz']} line={t['tile_line']} tmem={t['tile_tmem']}")

print()
print("=== Suspicious texture addresses (out of typical RDRAM 0x80000000-0x80800000) ===")
for t in texrects:
    a = t["timg_addr"]
    if a is None: continue
    if a < 0x80000000 or a >= 0x80800000:
        sx, sy, sw, sh = t["screen"]
        print(f"  off=+{t['off']:#06x}  screen=({sx:7.2f},{sy:7.2f}) {sw:6.2f}x{sh:6.2f}  "
              f"timg={a:#010x} fmt={t['timg_fmt']}/{t['timg_siz']}")

print()
print("=== Distinct SETTIMG addresses (count by addr) ===")
from collections import Counter
addrs = Counter(t["timg_addr"] for t in texrects)
for a, c in addrs.most_common(20):
    print(f"  {a:#010x}  used by {c} texrect(s)")
