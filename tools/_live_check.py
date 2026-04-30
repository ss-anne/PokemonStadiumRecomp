"""Quick check of live runner state."""
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

print("status:", call("status"))
print("gCurrentGameState peek:", call(json.dumps({"cmd":"rdram_peek","addr":0x80075668,"n":4})))
r = call("interesting_fns")
fns = {f["name"]: f["count"] for f in r.get("fns", [])}
for n in ("Game_Thread","fragment17_entry","fragment36_entry","fragment37_entry",
          "func_80029310","func_800293CC","func_82100C98","fragment62_entry"):
    print(f"  {n}: {fns.get(n, '?')}")
