"""Cross-coverage again, with the room-type vocabulary a Brief actually uses.

room_label_probe.py showed ROOM (82,618, 26% of the corpus) has BEDROOM's area
distribution — median 14.4 vs 14.0, CV 0.29 vs 0.22 — so it is an unlabelled
private habitable room, not a grab bag. Passes 1-3 counted ROOM and BEDROOM as
different types, which splits a pool that a Brief would treat as one.

Collapse {ROOM, BEDROOM, STUDIO} -> PRIVATE and re-measure. LIVING_ROOM,
LIVING_DINING and DINING are NOT collapsed: open-plan versus separate is a real
Brief distinction, not a labelling artefact.

Run: python experiments/retrieval-coverage/collapsed_coverage.py
"""

import json
import random
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parent / "out"
CACHE = OUT / "dwelling_records.json"
AREA_TOL, ASPECT_TOL, SEED = 0.10, 0.15, 20260819
COLLAPSE = {"ROOM": "PRIVATE", "BEDROOM": "PRIVATE", "STUDIO": "PRIVATE"}

recs = json.load(open(CACHE))
for r in recs:
    c = Counter()
    for t, k in r["ms"]:
        c[COLLAPSE.get(t, t)] += k
    r["ms"] = tuple(sorted(c.items()))
print(f"dwellings: {len(recs):,}")

by_ms, by_n = defaultdict(list), defaultdict(list)
for r in recs:
    by_ms[r["ms"]].append(r)
    by_n[r["n"]].append(r)
print(f"distinct multisets: {len(by_ms):,}  (was 1,190 uncollapsed)")

bands = {"4-6": range(4, 7), "7-10": range(7, 11), "11-15": range(11, 16),
         "16+": range(16, 200)}


def report(title, cross):
    print(f"\n{title}")
    print(f"{'band':<8}{'briefs':>9}{'pool=0':>9}{'pct':>7}{'<3':>8}{'median':>9}{'>=20':>9}")
    out = {}
    for b, rr in bands.items():
        rng = random.Random(SEED)
        sel = [r for r in recs if r["n"] in rr]
        if not sel:
            continue
        pools = []
        for r in sel:
            d = rng.choice(by_n[r["n"]]) if cross else r
            pools.append(sum(1 for p in by_ms[r["ms"]]
                             if p["k"] != r["k"]
                             and abs(p["area"] - d["area"]) <= AREA_TOL * d["area"]
                             and abs(p["aspect"] - d["aspect"]) <= ASPECT_TOL * d["aspect"]))
        pools.sort()
        m = len(pools)
        z = sum(1 for x in pools if x == 0)
        print(f"{b:<8}{m:>9,}{z:>9,}{100*z/m:>6.1f}%{sum(1 for x in pools if x<3):>8,}"
              f"{pools[m//2]:>9,}{sum(1 for x in pools if x>=20):>9,}")
        out[b] = {"briefs": m, "zero": z, "zero_pct": round(100*z/m, 1),
                  "median": pools[m//2], "ge20": sum(1 for x in pools if x >= 20)}
    return out


a = report("SELF-PAIRED (dwelling's own envelope) - the optimistic bound", False)
b = report("CROSS-PAIRED (another dwelling's envelope) - the honest test", True)
json.dump({"self": a, "cross": b}, open(OUT / "collapsed_coverage.json", "w"), indent=1)
print(f"\nwrote {OUT/'collapsed_coverage.json'}")
