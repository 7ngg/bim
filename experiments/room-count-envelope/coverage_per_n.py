"""Ticket 21: retrieval coverage PER ROOM COUNT, including 1-3 which
proposer.md 2.1's table never measured (it starts at 4-6).

Same method as experiments/retrieval-coverage/collapsed_coverage.py -- cross-paired
Brief (this dwelling's multiset + another dwelling's envelope, same room count),
{ROOM,BEDROOM,STUDIO} -> PRIVATE collapse, +-10% area / +-15% aspect gate.
Reuses that experiment's cached dwelling records.
"""
import json, random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "experiments" / "retrieval-coverage" / "out" / "dwelling_records.json"
COLLAPSE = {"ROOM": "PRIVATE", "BEDROOM": "PRIVATE", "STUDIO": "PRIVATE"}
AREA_TOL, ASPECT_TOL = 0.10, 0.15
SEED = 20260819

recs = json.load(open(CACHE))
for r in recs:
    c = Counter()
    for t, k in r["ms"]:
        c[COLLAPSE.get(t, t)] += k
    r["ms"] = tuple(sorted(c.items()))

by_ms, by_n = defaultdict(list), defaultdict(list)
for r in recs:
    by_ms[r["ms"]].append(r)
    by_n[r["n"]].append(r)

print(f"dwellings: {len(recs):,}   (collapsed, cross-paired, +-10%/+-15%)\n")
print(f"{'n':>3}{'briefs':>9}{'pool=0':>9}{'zero%':>8}{'median':>8}{'>=20':>8}{'ge20%':>8}")
rows = {}
for n in sorted(by_n):
    if n > 14:
        continue
    rng = random.Random(SEED)
    sel = by_n[n]
    pools = []
    for r in sel:
        d = rng.choice(by_n[n])
        pools.append(sum(1 for p in by_ms[r["ms"]]
                         if abs(p["area"] - d["area"]) <= AREA_TOL * d["area"]
                         and abs(p["aspect"] - d["aspect"]) <= ASPECT_TOL * d["aspect"]))
    pools.sort()
    m = len(pools)
    z = sum(1 for x in pools if x == 0)
    g = sum(1 for x in pools if x >= 20)
    print(f"{n:>3}{m:>9,}{z:>9,}{100*z/m:>7.1f}%{pools[m//2]:>8,}{g:>8,}{100*g/m:>7.1f}%")
    rows[n] = {"briefs": m, "zero": z, "zero_pct": round(100*z/m, 1),
               "median": pools[m//2], "ge20": g, "ge20_pct": round(100*g/m, 1)}

out = Path(__file__).resolve().parent / "coverage_per_n.json"
json.dump(rows, open(out, "w"), indent=1)
print(f"\nwrote {out}")
