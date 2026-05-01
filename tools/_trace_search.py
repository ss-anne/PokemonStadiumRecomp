"""Pull large trace_recent window and search for specific functions."""
import json, socket, sys

def call(cmd, t=4.0):
    s=socket.create_connection(("127.0.0.1",4371),timeout=t)
    s.sendall((json.dumps(cmd)+"\n").encode())
    s.settimeout(t); buf=b""
    while True:
        try: c=s.recv(65536)
        except: break
        if not c: break
        buf+=c
        if buf.endswith(b"\n"): break
    s.close()
    return json.loads(buf.decode().strip())

n = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
tr = call({"cmd":"trace_recent","n":n})
entries = tr.get("entries", [])
print(f"got {len(entries)} entries (write_idx={tr.get('write_idx')})")

# Look for render-path functions
targets = ["func_843010EC","func_84300E88","func_84300FBC","func_800078D4","func_8002B07C","func_800293CC","fragment62_entry","process_geo_layout","func_80007778","func_80006C6C"]
print()
for t in targets:
    cnt = sum(1 for e in entries if e == t)
    if cnt:
        # find first index
        idx = entries.index(t) if t in entries else -1
        print(f"  {t}: {cnt} hits (first idx {idx})")
print()

# Top 20 most common
from collections import Counter
c = Counter(entries)
print("Top 20 functions:")
for fn, cnt in c.most_common(20):
    print(f"  {cnt:5}  {fn}")
