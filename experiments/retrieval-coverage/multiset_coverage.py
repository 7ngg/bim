"""Retrieval coverage over Swiss Dwellings — pass 1, room multiset only.

Ticket 08 asks whether retrieval-and-warp can serve a Brief at all. A Brief names
a room multiset; retrieval needs a real dwelling whose multiset is close enough
that warping moves geometry rather than inventing arrangement.

Leave-one-out over real dwellings, which are the friendliest possible Briefs:
they came from the corpus. If retrieval is thin here it is thinner on invented
Briefs.

C6 generates many candidates and rejects most, so the number that matters is not
"is there a match" but "how big is the pool" — under retrieval the pool size IS
the candidate count.

Run: python experiments/retrieval-coverage/multiset_coverage.py
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
GEOM = ROOT / "data" / "corpora" / "swiss-dwellings" / "swiss-dwellings-v3.0.0" / "geometries.csv"
OUT = Path(__file__).resolve().parent / "out"

# Identical filter to experiments/corpus-smoke/smoke_swiss_dwellings.py, so the
# room-count histogram here must reproduce ticket 12's numbers exactly.
NOT_A_ROOM = {
    "SHAFT", "VOID", "OUTDOOR_VOID", "LIGHTWELL", "ELEVATOR", "STAIRCASE",
    "TECHNICAL_AREA", "BALCONY", "LOGGIA", "TERRACE", "GARDEN", "PATIO",
    "WINTERGARTEN",
}
COLS = ["apartment_id", "site_id", "floor_id", "unit_usage",
        "entity_type", "entity_subtype"]


def load_multisets():
    """dwelling key -> Counter of room subtypes."""
    per_dwelling = defaultdict(Counter)
    subtypes = Counter()
    reader = pd.read_csv(GEOM, usecols=COLS, chunksize=1_000_000, dtype=str)
    for chunk in reader:
        a = chunk[(chunk["entity_type"] == "area") &
                  (chunk["unit_usage"] == "RESIDENTIAL")]
        a = a[~a["entity_subtype"].isin(NOT_A_ROOM)]
        subtypes.update(a["entity_subtype"].fillna("<NA>").value_counts().to_dict())
        for s, f, ap, st in zip(a["site_id"], a["floor_id"],
                                a["apartment_id"], a["entity_subtype"].fillna("<NA>")):
            per_dwelling[(s, f, ap)][st] += 1
    return per_dwelling, subtypes


def key_of(counter):
    return tuple(sorted(counter.items()))


def band(n):
    if n <= 3:
        return "1-3"
    if n <= 6:
        return "4-6"
    if n <= 10:
        return "7-10"
    if n <= 15:
        return "11-15"
    return "16+"


BANDS = ["1-3", "4-6", "7-10", "11-15", "16+"]


def main():
    OUT.mkdir(exist_ok=True)
    per_dwelling, subtypes = load_multisets()
    print(f"dwellings: {len(per_dwelling):,}")
    total_rooms = sum(sum(c.values()) for c in per_dwelling.values())
    print(f"rooms: {total_rooms:,}  mean/dwelling: {total_rooms/len(per_dwelling):.2f}")

    print(f"\nroom subtypes kept ({len(subtypes)}):")
    for k, v in subtypes.most_common():
        print(f"    {k:<26} {v:>8,}")

    # exact-multiset pools
    pools = Counter()
    for c in per_dwelling.values():
        pools[key_of(c)] += 1
    print(f"\ndistinct exact multisets: {len(pools):,}")

    rows = []
    for k, c in per_dwelling.items():
        n = sum(c.values())
        rows.append((n, band(n), pools[key_of(c)] - 1))   # leave-one-out pool

    hist = Counter(n for n, _, _ in rows)
    print("\nroom-count histogram (sanity vs ticket 12):")
    for n in sorted(hist):
        if n <= 20 or hist[n] > 0:
            print(f"    {n:>3} rooms  {hist[n]:>7,}")
    print(f"    >=16: {sum(v for k, v in hist.items() if k >= 16):,}"
          f"   >=24: {sum(v for k, v in hist.items() if k >= 24):,}")

    print("\nLEAVE-ONE-OUT EXACT-MULTISET POOL SIZE, by room-count band")
    print(f"{'band':<8}{'dwellings':>10}{'pool=0':>9}{'1-2':>8}{'3-9':>8}"
          f"{'10-49':>8}{'50+':>8}{'median':>8}")
    buckets = defaultdict(list)
    for n, b, p in rows:
        buckets[b].append(p)
    for b in BANDS:
        v = buckets.get(b, [])
        if not v:
            continue
        v_sorted = sorted(v)
        med = v_sorted[len(v_sorted) // 2]
        z = sum(1 for x in v if x == 0)
        a = sum(1 for x in v if 1 <= x <= 2)
        c3 = sum(1 for x in v if 3 <= x <= 9)
        c10 = sum(1 for x in v if 10 <= x <= 49)
        c50 = sum(1 for x in v if x >= 50)
        print(f"{b:<8}{len(v):>10,}{z:>9,}{a:>8,}{c3:>8,}{c10:>8,}{c50:>8,}{med:>8,}")

    allp = sorted(p for _, _, p in rows)
    z = sum(1 for x in allp if x == 0)
    print(f"\nall dwellings: {len(allp):,}  pool=0: {z:,} ({100*z/len(allp):.1f}%)"
          f"  median pool: {allp[len(allp)//2]:,}")

    json.dump({"n_dwellings": len(per_dwelling),
               "distinct_multisets": len(pools),
               "pool_by_band": {b: sorted(buckets[b]) for b in BANDS if buckets.get(b)}},
              open(OUT / "multiset_pools.json", "w"))
    # multisets themselves, for pass 2 (edit-distance-1 neighbours)
    json.dump([[list(map(list, k)), v] for k, v in pools.items()],
              open(OUT / "multisets.json", "w"))
    print(f"\nwrote {OUT/'multiset_pools.json'} and {OUT/'multisets.json'}")


if __name__ == "__main__":
    main()
