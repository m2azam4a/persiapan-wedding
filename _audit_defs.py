# -*- coding: utf-8 -*-
import json
from pathlib import Path
from collections import defaultdict

p = Path(r"D:\Isi Otak Azam\Persiapan Wedding\wedding-planner-html\js\definitions.js")
defs = json.loads(p.read_text(encoding="utf-8").replace("window.WP_DEFINITIONS = ", "", 1).rstrip().rstrip(";"))

within = []
for tid, d in defs.items():
    steps = d.get("langkah") or []
    seen = {}
    for i, s in enumerate(steps):
        key = s.strip().lower()
        if key in seen:
            within.append((tid, d["nama"], seen[key] + 1, i + 1, s[:140]))
        else:
            seen[key] = i

step_to_tasks = defaultdict(set)
for tid, d in defs.items():
    for s in d.get("langkah") or []:
        step_to_tasks[s.strip()].add(tid)

shared = [(s, sorted(tids)) for s, tids in step_to_tasks.items() if len(tids) >= 15]
shared.sort(key=lambda x: -len(x[1]))

generic_markers = [
    "pecah jadi 3 bagian kecil",
    "tulis di notes hp: “tujuan pekerjaan ini",
    "tulis di notes hp: \"tujuan pekerjaan ini",
    "setiap selesai 1 bagian, foto",
]
generic_tasks = []
for tid, d in defs.items():
    blob = " | ".join(d.get("langkah") or []).lower()
    hits = sum(1 for m in generic_markers if m in blob)
    if hits >= 1 and "pecah jadi 3 bagian kecil" in blob:
        generic_tasks.append((tid, d["nama"], d["phase"]))

print("TASKS", len(defs))
print("WITHIN_DUP", len(within))
for row in within[:40]:
    print("WDUP", row[0], "|", row[1][:55], "|#", row[2], "&", row[3], "|", row[4])

print("\nSHARED_TEXTS", len(shared))
for s, tids in shared[:30]:
    print(f"\nSHARE[{len(tids)}] {s}")

print("\nGENERIC_COUNT", len(generic_tasks))
for tid, nama, phase in sorted(generic_tasks, key=lambda x: (x[2], x[0])):
    print("GEN", tid, phase, "|", nama)

# pair-wise near duplicate within task (same first 40 chars)
print("\nNEAR_WITHIN")
near = 0
for tid, d in defs.items():
    steps = [s.strip() for s in d.get("langkah") or []]
    for i in range(len(steps)):
        for j in range(i + 1, len(steps)):
            a, b = steps[i], steps[j]
            if a == b:
                continue
            if a[:50] == b[:50] and len(a) > 50:
                near += 1
                if near <= 25:
                    print(tid, "|", i + 1, "&", j + 1, "|", a[:90], "||", b[:90])
print("NEAR_TOTAL", near)
