"""Verbose dump of _dbg_drive report."""
import json, sys
d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "build/last_drive.json"))
for e in d.get("events", []):
    print(" ", e.get("kind"), {k:v for k,v in e.items() if k not in ("t","kind")})
print()
print("diagnostics keys:", list(d.get("diagnostics", {}).keys()))
print("runner_exit_code:", d.get("runner_exit_code", "STILL_RUNNING"))
print("errlog non-empty?:", bool((d.get("errlog_tail_file") or "").strip()))
