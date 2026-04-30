import socket, json
s = socket.create_connection(("127.0.0.1", 4371), timeout=3)
s.sendall(b"interesting_fns\n")
b = b""
while not b.endswith(b"\n"):
    c = s.recv(65536)
    if not c: break
    b += c
s.close()
r = json.loads(b.decode().strip())
for f in r.get("fns", []):
    if f["count"] > 0:
        print(f"  {f['name']}: {f['count']}")
