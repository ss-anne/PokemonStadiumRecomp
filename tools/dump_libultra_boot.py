"""
dump_libultra_boot.py — pull the libultra boot trace from a running
PokemonStadiumRecomp.exe and write it as one event per line.

The runtime should already be running (the ring is always-on; we
just query the existing snapshot). Default port 4371.
"""
import json
import socket
import sys


def send(host: str, port: int, cmd: str, timeout: float = 1.0) -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect((host, port))
    s.sendall((cmd + "\n").encode("ascii"))
    buf = b""
    while b"\n" not in buf:
        chunk = s.recv(65536)
        if not chunk:
            break
        buf += chunk
    s.close()
    return buf.split(b"\n", 1)[0].decode("ascii", "replace")


def main():
    host = "127.0.0.1"
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4371
    out_path = sys.argv[2] if len(sys.argv) > 2 else None

    status = send(host, port, "status")
    sys.stderr.write("STATUS=" + status + "\n")

    chunk_size = 1024
    start = 0
    total = None
    rows = []
    while True:
        cmd = json.dumps({"cmd": "libultra_boot", "start": start, "n": chunk_size})
        resp_raw = send(host, port, cmd)
        try:
            resp = json.loads(resp_raw)
        except json.JSONDecodeError:
            sys.stderr.write("bad json: " + resp_raw[:500] + "\n")
            break
        if total is None:
            total = resp.get("count", 0)
            sys.stderr.write(f"TOTAL boot events={total} cap={resp.get('capacity')}\n")
        for ev in resp.get("events", []):
            rows.append(ev)
        start += chunk_size
        if start >= total:
            break

    sys.stderr.write(f"collected {len(rows)} events\n")

    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            for ev in rows:
                f.write(json.dumps(ev) + "\n")
        sys.stderr.write(f"wrote {out_path}\n")
    else:
        for ev in rows:
            print(json.dumps(ev))


if __name__ == "__main__":
    main()
