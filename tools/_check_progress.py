"""Sample twice to see if anything is incrementing."""
import socket, json, time
def call(c):
    s = socket.create_connection(("127.0.0.1", 4371), timeout=3)
    s.sendall((c + "\n").encode())
    b = b""
    while not b.endswith(b"\n"):
        x = s.recv(65536)
        if not x: break
        b += x
    s.close()
    return json.loads(b.decode().strip())

r1 = call("status")
print("frame1=", r1.get("frame"), "send_dl=", r1.get("send_dl"))
time.sleep(2.0)
r2 = call("status")
print("frame2=", r2.get("frame"), "send_dl=", r2.get("send_dl"),
      "delta_frame=", r2.get("frame") - r1.get("frame"),
      "delta_dl=", r2.get("send_dl") - r1.get("send_dl"))
