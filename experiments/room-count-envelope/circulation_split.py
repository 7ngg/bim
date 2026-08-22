"""Ticket 21: how many of a dwelling's interior rooms does a Homeowner NOT name?

brief.md §3: `corridor` and `entrance_lobby` are invented by `resolve`, not stated.
So the engine's room count = Homeowner-named count + invented circulation.
The 4-10 band (C13, proposer.md §3) is measured on the ENGINE count.
This measures the gap, per dwelling, on the same filter as dataset-inventory.md §1.3.
"""
from collections import Counter
from pathlib import Path
import pandas as pd

GEOM = Path("data/corpora/swiss-dwellings/swiss-dwellings-v3.0.0/geometries.csv")
NULL_HASH = "d41d8cd98f00b204e9800998ecf8427e"
EXCLUDE = {"SHAFT","VOID","OUTDOOR_VOID","LIGHTWELL","ELEVATOR","STAIRCASE",
           "TECHNICAL_AREA","BALCONY","LOGGIA","TERRACE","GARDEN","PATIO","WINTERGARTEN"}
# What `resolve` invents rather than the Homeowner stating it.
CIRC = {"CORRIDOR"}
IDS = ["entity_type","entity_subtype","unit_usage","site_id","floor_id","apartment_id"]

total = Counter()   # key -> interior rooms
circ  = Counter()   # key -> circulation rooms
subs  = Counter()

reader = pd.read_csv(GEOM, usecols=IDS, chunksize=1_000_000, dtype=str)
for chunk in reader:
    a = chunk[(chunk.entity_type == "area") &
              (chunk.unit_usage == "RESIDENTIAL") &
              (chunk.apartment_id != NULL_HASH)]
    a = a[~a.entity_subtype.isin(EXCLUDE)]
    keys = list(zip(a.site_id, a.floor_id, a.apartment_id))
    total.update(keys)
    subs.update(a.entity_subtype.fillna("<NA>").value_counts().to_dict())
    c = a[a.entity_subtype.isin(CIRC)]
    circ.update(zip(c.site_id, c.floor_id, c.apartment_id))

print(f"dwellings: {len(total)}")
print("\ninterior-room subtypes (top 20):")
for s, n in subs.most_common(20):
    print(f"  {s:22s} {n:>7}")

# per-dwelling: engine count vs homeowner-named count
gap = Counter()
named_hist = Counter()
eng_hist = Counter()
joint = Counter()
for k, n in total.items():
    c = circ.get(k, 0)
    gap[c] += 1
    named_hist[n - c] += 1
    eng_hist[n] += 1
    joint[(n - c, n)] += 1

N = len(total)
print("\ncirculation rooms per dwelling (the k in engine = named + k):")
for c in sorted(gap):
    print(f"  k={c}: {gap[c]:>6}  ({100*gap[c]/N:5.2f}%)")

def band(h, lo, hi):
    return sum(v for kk, v in h.items() if lo <= kk <= hi)

print("\nengine-count histogram (matches inventory 1.4):")
print("  " + "  ".join(f"{k}:{eng_hist[k]}" for k in sorted(eng_hist)))
print("\nhomeowner-named histogram:")
print("  " + "  ".join(f"{k}:{named_hist[k]}" for k in sorted(named_hist)))

print(f"\nengine 4-10:  {band(eng_hist,4,10):>6}  ({100*band(eng_hist,4,10)/N:5.2f}%)")
print(f"engine <4:    {band(eng_hist,0,3):>6}  ({100*band(eng_hist,0,3)/N:5.2f}%)")
print(f"engine >10:   {band(eng_hist,11,99):>6}  ({100*band(eng_hist,11,99)/N:5.2f}%)")
print(f"\nnamed 4-10:   {band(named_hist,4,10):>6}  ({100*band(named_hist,4,10)/N:5.2f}%)")
print(f"named <4:     {band(named_hist,0,3):>6}  ({100*band(named_hist,0,3)/N:5.2f}%)")
print(f"named >10:    {band(named_hist,11,99):>6}  ({100*band(named_hist,11,99)/N:5.2f}%)")

# The product question: if a Homeowner is told "3-9 rooms", what engine counts land?
print("\nfor each named count: engine-count distribution (named -> engine)")
for nm in range(1, 13):
    row = {e: v for (n_, e), v in joint.items() if n_ == nm}
    if not row: continue
    tot = sum(row.values())
    out_of_band = sum(v for e, v in row.items() if e < 4 or e > 10)
    print(f"  named {nm:>2}: n={tot:>6}  engine " +
          " ".join(f"{e}:{v}" for e, v in sorted(row.items())) +
          f"   | out-of-band {100*out_of_band/tot:5.2f}%")
