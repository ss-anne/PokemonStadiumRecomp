"""Trigger dump_threads."""
import socket
s = socket.create_connection(("127.0.0.1", 4371), timeout=5)
s.sendall(b"dump_threads\n")
print(s.recv(2048).decode())
s.close()
