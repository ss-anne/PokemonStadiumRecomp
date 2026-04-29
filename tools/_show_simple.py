import json
d = json.load(open("build/last_drive.json"))
for p in d.get("peeks", []):
    h = p.get("hex", "?")
    print(p.get("_spec", "?"))
    print(" ", h[:160])
    print()
