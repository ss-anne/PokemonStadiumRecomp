import json, sys
d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "build/whitescreen.json"))
diag = d.get("diagnostics", {})
print("diagnostics keys:", list(diag.keys()))
for k, v in diag.items():
    print(f"--- {k} ---")
    if isinstance(v, dict):
        for k2, v2 in v.items():
            if isinstance(v2, list):
                print(f"  {k2}: ({len(v2)} entries) ...")
                for e in v2[-20:]:
                    print("    ", e)
            else:
                s = str(v2)
                print(f"  {k2}:", s[:400])
    else:
        print(" ", str(v)[:500])
