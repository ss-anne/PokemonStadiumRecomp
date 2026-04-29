"""Quick peek of running runner's game state."""
import socket, json

def call(cmd):
    s = socket.create_connection(("127.0.0.1", 4371), timeout=3)
    s.sendall((cmd + "\n").encode())
    buf = b""
    while not buf.endswith(b"\n"):
        c = s.recv(65536)
        if not c: break
        buf += c
    s.close()
    return json.loads(buf.decode().strip())

print("status:", call("status"))
print()
print("gCurrentGameState peek:",
      call(json.dumps({"cmd":"rdram_peek","addr":0x80075668,"n":8})))
print()
r = call(json.dumps({"cmd":"trace_recent","n":24}))
print("last 24 trace entries:")
for e in r.get("entries", []):
    print(" ", e)
