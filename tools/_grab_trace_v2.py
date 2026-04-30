"""Grab live trace_recent to see what Game_Thread is doing."""
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

r = call("trace_recent")
events = r.get("events", [])
print(f"trace tail (last {min(40, len(events))} events):")
for e in events[-40:]:
    print(" ", e)
