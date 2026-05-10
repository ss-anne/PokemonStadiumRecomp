"""Dump every G_LOADBLOCK + preceding G_SETTIMG / G_SETTILE state from
a captured DL. Output enough to compute the byte count Stadium asks
for, and compare to what RT64's loadBlockOperation actually loads.
"""
import struct, sys

PATH = sys.argv[1] if len(sys.argv) > 1 else "build/last_run_dl_gamepakcheck.bin"

with open(PATH, "rb") as f:
    data = f.read()

FMT = {0:"RGBA",1:"YUV",2:"CI",3:"IA",4:"I"}
SIZ_NAME = {0:"4b",1:"8b",2:"16b",3:"32b"}
SIZ_BITS = {0:4,1:8,2:16,3:32}

class Tile:
    fmt = siz = line = tmem = pal = 0
    uls = ult = lrs = lrt = 0
    block_uls = block_ult = block_lrs = block_dxt = 0

tiles = [Tile() for _ in range(8)]
timg = (0, 0, 0, 0)  # addr, fmt, siz, width

i = 0
events = []
while i + 8 <= len(data):
    w0 = struct.unpack(">I", data[i:i+4])[0]
    w1 = struct.unpack(">I", data[i+4:i+8])[0]
    op = (w0 >> 24) & 0xFF
    if op == 0xFD:
        timg_fmt = (w0 >> 21) & 0x7
        timg_siz = (w0 >> 19) & 0x3
        timg_width = (w0 & 0xFFF) + 1
        timg_addr = w1
        timg = (timg_addr, timg_fmt, timg_siz, timg_width)
    elif op == 0xF5:
        fmt = (w0 >> 21) & 0x7
        siz = (w0 >> 19) & 0x3
        line = (w0 >> 9) & 0x1FF
        tmem = w0 & 0x1FF
        ti = (w1 >> 24) & 0x7
        t = tiles[ti]
        t.fmt, t.siz, t.line, t.tmem = fmt, siz, line, tmem
    elif op == 0xF2:
        uls = (w0 >> 12) & 0xFFF
        ult = w0 & 0xFFF
        ti = (w1 >> 24) & 0x7
        lrs = (w1 >> 12) & 0xFFF
        lrt = w1 & 0xFFF
        t = tiles[ti]
        t.uls, t.ult, t.lrs, t.lrt = uls, ult, lrs, lrt
    elif op == 0xF3:
        uls = (w0 >> 12) & 0xFFF
        ult = w0 & 0xFFF
        ti = (w1 >> 24) & 0x7
        lrs = (w1 >> 12) & 0xFFF
        dxt = w1 & 0xFFF
        t = tiles[ti]
        t.block_uls, t.block_ult, t.block_lrs, t.block_dxt = uls, ult, lrs, dxt
        # Compute what RT64 would load and what HW would load.
        timg_addr, timg_fmt, timg_siz, timg_width = timg
        # RT64's wordCount uses loadTile.siz (the tile size, i.e. t.siz).
        rt64_wordcount = ((lrs - uls) >> (4 - t.siz)) + 1
        rt64_bytes = rt64_wordcount * 8
        # Hardware-correct wordCount uses texture.siz.
        hw_wordcount = ((lrs - uls) >> (4 - timg_siz)) + 1
        hw_bytes = hw_wordcount * 8
        events.append({
            "off": i,
            "tile": ti,
            "tile_fmt": FMT.get(t.fmt, "?"),
            "tile_siz": SIZ_NAME.get(t.siz, "?"),
            "tile_line": t.line,
            "tile_tmem": t.tmem,
            "timg_fmt": FMT.get(timg_fmt, "?"),
            "timg_siz": SIZ_NAME.get(timg_siz, "?"),
            "timg_width": timg_width,
            "block_uls": uls,
            "block_lrs": lrs,
            "block_dxt": dxt,
            "rt64_bytes": rt64_bytes,
            "hw_bytes": hw_bytes,
            "mismatch": (t.siz != timg_siz),
        })
    i += 8

print(f"DL: {PATH}  LOADBLOCK count: {len(events)}\n")
print(f"{'off':>6}  {'tile':>4}  {'TIMG':>10}  {'TILE':>10}  "
      f"{'block uls,lrs,dxt':>20}  {'RT64 bytes':>10}  {'HW bytes':>10}  diff?")
for e in events:
    flag = " *** SIZE MISMATCH" if e["mismatch"] else ""
    diff = "" if e["rt64_bytes"] == e["hw_bytes"] else f"  DIFFER ({e['rt64_bytes']} vs {e['hw_bytes']})"
    print(f"+{e['off']:#06x}  {e['tile']:>4}  {e['timg_fmt']:>4}/{e['timg_siz']:<4} "
          f" {e['tile_fmt']:>4}/{e['tile_siz']:<4}  "
          f"{e['block_uls']:>5},{e['block_lrs']:>5},{e['block_dxt']:>5}  "
          f"{e['rt64_bytes']:>10}  {e['hw_bytes']:>10}  {flag}{diff}")
