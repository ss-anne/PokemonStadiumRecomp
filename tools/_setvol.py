"""Set runtime audio volume via TCP."""
import socket, json, sys
v = float(sys.argv[1]) if len(sys.argv) > 1 else 0.3
s = socket.create_connection(("127.0.0.1", 4371), timeout=3)
s.sendall(f'{{"cmd":"set_volume","value":{v}}}\n'.encode())
b = b""
while not b.endswith(b"\n"):
    c = s.recv(4096)
    if not c: break
    b += c
print(b.decode().strip())
s.close()
