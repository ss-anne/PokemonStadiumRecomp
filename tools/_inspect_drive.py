"""Pretty-print the most recent _dbg_drive.py report."""
import json, sys
d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "build/last_drive.json"))
diag = d.get("diagnostics", {})
print("post-wait status:", diag.get("status"))
print("peeks:", d.get("peeks"))
print("runner_exit_code:", d.get("runner_exit_code", "STILL_RUNNING"))
errlog = d.get("errlog_tail_file") or ""
print("errlog tail (last 1200):")
print(errlog[-1200:])
