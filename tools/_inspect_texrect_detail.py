"""Walk a captured DL and emit full state for every G_TEXRECT
(SETTIMG, SETTILE, SETTILESIZE, LOADBLOCK, TEXTURE all tracked
through the DL). Filter by screen-Y range to focus on suspect
corruption regions. Flag suspicious format/stride combinations.

F3DEX2 reference for the relevant fields:
  G_SETTIMG (0xFD): w0 = (op<<24)|(fmt<<21)|(siz<<19)|width
                    w1 = source addr
  G_SETTILE (0xF5): w0 = (op<<24)|(fmt<<21)|(siz<<19)|(line<<9)|tmem
                    w1 = (tile<<24)|(palette<<20)|(cmt<<18)|(maskt<<14)|
                         (shiftt<<10)|(cms<<8)|(masks<<4)|shifts
  G_SETTILESIZE (0xF2): w0 = (op<<24)|(uls<<12)|ult
                        w1 = (tile<<24)|(lrs<<12)|lrt
  G_LOADBLOCK (0xF3): w0 = (op<<24)|(uls<<12)|ult
                      w1 = (tile<<24)|(lrs<<12)|dxt
  G_TEXTURE (0xD7): w0 = (op<<24)|(mipmap<<11)|(tile<<8)|on
                    w1 = (scaleS<<16)|scaleT
  G_TEXRECT (0xE4): w0 = (op<<24)|(lrx<<12)|lry
                    w1 = (tile<<24)|(ulx<<12)|uly
   followed by RDPHALF_1 (s/t) and RDPHALF_2 (dsdx/dtdy)
"""
import struct, sys

PATH = sys.argv[1] if len(sys.argv) > 1 else "build/last_run_dl_gamepakcheck.bin"
Y_LO  = int(sys.argv[2]) if len(sys.argv) > 2 else 0
Y_HI  = int(sys.argv[3]) if len(sys.argv) > 3 else 480

FMT = {0:"RGBA",1:"YUV",2:"CI",3:"IA",4:"I"}
SIZ = {0:"4b",1:"8b",2:"16b",3:"32b"}
SIZ_BITS = {0:4,1:8,2:16,3:32}

with open(PATH, "rb") as f:
    data = f.read()

# Tracked state (per tile = 8 tiles).
class Tile:
    fmt = siz = line = tmem = pal = 0
    cms = cmt = masks = maskt = shifts = shiftt = 0
    uls = ult = lrs = lrt = 0
    block_uls = block_ult = block_lrs = block_dxt = 0  # last LOADBLOCK params

tiles = [Tile() for _ in range(8)]
timg_addr = 0
timg_fmt = 0
timg_siz = 0
timg_width = 0
tex_on = 0
tex_tile = 0
tex_scaleS = 0
tex_scaleT = 0

i = 0
texrects = []
while i + 8 <= len(data):
    w0 = struct.unpack(">I", data[i:i+4])[0]
    w1 = struct.unpack(">I", data[i+4:i+8])[0]
    op = (w0 >> 24) & 0xFF

    if op == 0xFD:  # G_SETTIMG
        timg_fmt = (w0 >> 21) & 0x7
        timg_siz = (w0 >> 19) & 0x3
        timg_width = (w0 & 0xFFF) + 1   # 0-based + 1
        timg_addr = w1
    elif op == 0xF5:  # G_SETTILE
        fmt = (w0 >> 21) & 0x7
        siz = (w0 >> 19) & 0x3
        line = (w0 >> 9) & 0x1FF
        tmem = w0 & 0x1FF
        tile = (w1 >> 24) & 0x7
        pal = (w1 >> 20) & 0xF
        cmt = (w1 >> 18) & 0x3
        maskt = (w1 >> 14) & 0xF
        shiftt = (w1 >> 10) & 0xF
        cms = (w1 >> 8) & 0x3
        masks = (w1 >> 4) & 0xF
        shifts = w1 & 0xF
        t = tiles[tile]
        t.fmt, t.siz, t.line, t.tmem, t.pal = fmt, siz, line, tmem, pal
        t.cms, t.cmt, t.masks, t.maskt, t.shifts, t.shiftt = cms, cmt, masks, maskt, shifts, shiftt
    elif op == 0xF2:  # G_SETTILESIZE
        uls = (w0 >> 12) & 0xFFF
        ult = w0 & 0xFFF
        tile = (w1 >> 24) & 0x7
        lrs = (w1 >> 12) & 0xFFF
        lrt = w1 & 0xFFF
        t = tiles[tile]
        t.uls, t.ult, t.lrs, t.lrt = uls, ult, lrs, lrt
    elif op == 0xF3:  # G_LOADBLOCK
        uls = (w0 >> 12) & 0xFFF
        ult = w0 & 0xFFF
        tile = (w1 >> 24) & 0x7
        lrs = (w1 >> 12) & 0xFFF
        dxt = w1 & 0xFFF
        t = tiles[tile]
        t.block_uls, t.block_ult, t.block_lrs, t.block_dxt = uls, ult, lrs, dxt
    elif op == 0xD7:  # G_TEXTURE
        tex_on = w0 & 0x1
        tex_tile = (w0 >> 8) & 0x7
        tex_scaleS = (w1 >> 16) & 0xFFFF
        tex_scaleT = w1 & 0xFFFF
    elif op == 0xE4:  # G_TEXRECT
        lrx = (w0 >> 12) & 0xFFF
        lry = w0 & 0xFFF
        tile_idx = (w1 >> 24) & 0x7
        ulx = (w1 >> 12) & 0xFFF
        uly = w1 & 0xFFF
        n0 = struct.unpack(">I", data[i+8:i+12])[0]   if i+12<=len(data) else 0
        n1 = struct.unpack(">I", data[i+12:i+16])[0]  if i+16<=len(data) else 0
        m0 = struct.unpack(">I", data[i+16:i+20])[0]  if i+20<=len(data) else 0
        m1 = struct.unpack(">I", data[i+20:i+24])[0]  if i+24<=len(data) else 0
        # n1 = (s<<16) | t — texture coord at (ulx, uly) in 10.5 fixed
        s = (n1 >> 16) & 0xFFFF
        t = n1 & 0xFFFF
        # m1 = (dsdx<<16) | dtdy — UV step per pixel in 5.10 fixed
        dsdx = (m1 >> 16) & 0xFFFF
        dtdy = m1 & 0xFFFF
        T = tiles[tile_idx]
        # Convert sign-extended 5.10 to float
        def s5_10(x):
            x &= 0xFFFF
            if x & 0x8000: x -= 0x10000
            return x / 1024.0
        # 10.2 fixed-point screen coords
        ulxp = ulx / 4.0
        ulyp = uly / 4.0
        lrxp = lrx / 4.0
        lryp = lry / 4.0
        wp = lrxp - ulxp
        hp = lryp - ulyp
        # Tile size in texels
        tile_w_texels = ((T.lrs - T.uls) >> 2) + 1
        tile_h_texels = ((T.lrt - T.ult) >> 2) + 1
        # Texrect U/V step
        dsdx_f = s5_10(dsdx)
        dtdy_f = s5_10(dtdy)
        # Bytes per texel for tile
        tile_bpt = SIZ_BITS.get(T.siz, 0) / 8.0
        # Expected line stride bytes for this tile width
        expected_line_words = max(1, int((tile_w_texels * tile_bpt + 7) // 8))
        texrects.append({
            "off": i,
            "tile_idx": tile_idx,
            "screen": (ulxp, ulyp, wp, hp),
            "uv": (s, t, dsdx_f, dtdy_f),
            "timg_addr": timg_addr,
            "timg_fmt": FMT.get(timg_fmt, "?"),
            "timg_siz": SIZ.get(timg_siz, "?"),
            "timg_width": timg_width,
            "tile_fmt": FMT.get(T.fmt, "?"),
            "tile_siz": SIZ.get(T.siz, "?"),
            "tile_line": T.line,
            "tile_tmem": T.tmem,
            "tile_pal": T.pal,
            "tile_cms": T.cms,
            "tile_cmt": T.cmt,
            "tile_masks": T.masks,
            "tile_maskt": T.maskt,
            "tile_w": tile_w_texels,
            "tile_h": tile_h_texels,
            "block_lrs": T.block_lrs,
            "block_dxt": T.block_dxt,
            "expected_line_words": expected_line_words,
            "tile_bpt": tile_bpt,
        })
    i += 8

# Filter by screen Y range
hits = [t for t in texrects if Y_LO <= t["screen"][1] <= Y_HI]
print(f"DL: {PATH}  total TEXRECTs: {len(texrects)}  in Y={Y_LO}..{Y_HI}: {len(hits)}\n")

def fmt_flags(t):
    flags = []
    if t["timg_fmt"] != t["tile_fmt"] or t["timg_siz"] != t["tile_siz"]:
        flags.append(f"FMT_MISMATCH(timg={t['timg_fmt']}/{t['timg_siz']} tile={t['tile_fmt']}/{t['tile_siz']})")
    if t["tile_line"] != t["expected_line_words"]:
        flags.append(f"LINE_MISMATCH(line={t['tile_line']} expect={t['expected_line_words']})")
    if t["tile_w"] <= 0 or t["tile_h"] <= 0:
        flags.append(f"BAD_TILESIZE(w={t['tile_w']} h={t['tile_h']})")
    if t["uv"][2] != 1.0 or t["uv"][3] != 1.0:
        flags.append(f"NON_UNIT_UV(dsdx={t['uv'][2]:.3f} dtdy={t['uv'][3]:.3f})")
    return ", ".join(flags) if flags else ""

for t in hits:
    sx, sy, sw, sh = t["screen"]
    flags = fmt_flags(t)
    line = (f"+{t['off']:#06x}  scr=({sx:6.1f},{sy:6.1f}) {sw:5.1f}x{sh:4.1f}  "
            f"tile{t['tile_idx']} {t['tile_fmt']}/{t['tile_siz']} {t['tile_w']}x{t['tile_h']} "
            f"line={t['tile_line']} (expect~{t['expected_line_words']})  "
            f"timg=0x{t['timg_addr']:08x} {t['timg_fmt']}/{t['timg_siz']}  "
            f"dsdx/dtdy={t['uv'][2]:.2f}/{t['uv'][3]:.2f}")
    print(line)
    if flags:
        print(f"        !! {flags}")
