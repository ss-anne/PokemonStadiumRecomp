"""Check whether thread20_rsp is running by querying the trace ring."""
import socket, json

def call(c):
    s = socket.create_connection(("127.0.0.1", 4371), timeout=3)
    s.sendall((c + "\n").encode())
    buf = b""
    while not buf.endswith(b"\n"):
        x = s.recv(65536)
        if not x: break
        buf += x
    s.close()
    return json.loads(buf.decode().strip())

r = call(json.dumps({"cmd":"trace_recent","n":512}))
ents = r.get("entries", [])
print("trace ring last 512 entries — checking for rsp-thread calls")
print(f"  total: {len(ents)}")
search = [
    "func_80000BA4",   # thread20_rsp
    "func_80000D54",   # rsp_init
    "func_800007D4",   # cart-DMA worker
    "func_800005C0",   # LeoCJCreateLeoManager wrapper
    "func_8000C8F8",   # other init
    "func_80003DC4",   # PERS-SZP requester (caller side)
    "func_80003B30",   # DMA chunker
    "func_80000E80",   # OSIoMesg builder
    "func_80000E2C",   # message poster
]
for term in search:
    matches = [i for i, e in enumerate(ents) if term in e]
    print(f"  {term}: {len(matches)} hits")
