"""One-shot peeks against an already-running runner."""
import socket, json, sys

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

# Peek targets passed as argv: ADDR:N
for spec in sys.argv[1:]:
    addr_s, n_s = spec.split(":")
    addr = int(addr_s, 0)
    n = int(n_s, 0)
    r = call(json.dumps({"cmd":"rdram_peek","addr":addr,"n":n}))
    hex_str = r.get("hex", "")
    # Format as 4-byte BE words
    words = []
    for i in range(0, len(hex_str), 8):
        words.append(hex_str[i:i+8])
    print(f"{spec}:")
    for i, w in enumerate(words):
        print(f"  +0x{i*4:03X}: 0x{w}")
    print()
