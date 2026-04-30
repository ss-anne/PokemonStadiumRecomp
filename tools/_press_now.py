"""Send a Start press to a running runner."""
import socket, json, time, sys

def call(c, t=2):
    s = socket.create_connection(("127.0.0.1", 4371), timeout=t)
    s.sendall((c + "\n").encode())
    buf = b""
    while not buf.endswith(b"\n"):
        x = s.recv(65536)
        if not x: break
        buf += x
    s.close()
    return json.loads(buf.decode().strip())

btn = sys.argv[1] if len(sys.argv) > 1 else "Start"
ms = int(sys.argv[2]) if len(sys.argv) > 2 else 200
print(f"pressing {btn} for {ms}ms")
call(json.dumps({"cmd":"set_button","name":btn,"down":True}))
time.sleep(ms / 1000.0)
call(json.dumps({"cmd":"set_button","name":btn,"down":False}))

# peek state after
time.sleep(0.5)
r = call(json.dumps({"cmd":"rdram_peek","addr":0x80075668,"n":8}))
print("state after:", r.get("hex"))
