"""Pretty-print the most recent _dbg_drive.py peek results."""
import json
d = json.load(open("build/last_drive.json"))
for p in d.get("peeks", []):
    h = p.get("hex", "?")
    print(p["_spec"])
    for i in range(0, len(h), 8):
        addr_off = i // 2
        print(f"  +0x{addr_off:03X}: 0x{h[i:i+8]}")
    print()
