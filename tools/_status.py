import json, socket
s=socket.create_connection(("127.0.0.1",4371),timeout=3)
s.sendall(b'{"cmd":"status"}\n')
buf=b""
while True:
    c=s.recv(65536)
    if not c: break
    buf+=c
    if buf.endswith(b"\n"): break
s.close()
d=json.loads(buf.decode().strip())
for k,v in d.items(): print(f"  {k}: {v}")
