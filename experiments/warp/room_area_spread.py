"""Does an affine warp land a retrieved dwelling's rooms on the Brief's targets?

Ticket 23, item 5. `proposer.md` 2.2 gates retrieval on the room multiset, on
**total** floor area (+-10 %) and on envelope aspect (+-15 %). Nothing in the gate
looks at a *per-room* area. If the warp is one anisotropic scale of the whole
tiling -- the cheapest thing it could be, and the only thing that preserves every
separation direction by construction -- then each retrieved room's area lands at

    warped_area = corpus_room_area * (envelope_area / corpus_dwelling_area)

and the Brief asked for `target_area`. This measures the ratio of those two, over
the same cross-paired Briefs `retrieval-coverage/cross_coverage.py` used, in the
same collapsed vocabulary, at the same seed.

The bound it is scored against is `dim.max_area` -- hard, site `both`,
`k[type] x target_area`, `docs/research/room-area-bands.md` 6.1. There is no
lower bound in the bar; 0.70 is reported as a Homeowner-visible floor, not a rule.

    python experiments/warp/room_area_spread.py
"""

from __future__ import annotations

import json
import random
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from shapely import from_wkt
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
GEOM = ROOT / "data" / "corpora" / "swiss-dwellings" / "swiss-dwellings-v3.0.0" / "geometries.csv"
OUT = Path(__file__).resolve().parent / "out"
CACHE = OUT / "dwelling_rooms.json"

NOT_A_ROOM = {
    "SHAFT", "VOID", "OUTDOOR_VOID", "LIGHTWELL", "ELEVATOR", "STAIRCASE",
    "TECHNICAL_AREA", "BALCONY", "LOGGIA", "TERRACE", "GARDEN", "PATIO",
    "WINTERGARTEN",
}
MD5_EMPTY = "d41d8cd98f00b204e9800998ecf8427e"
COLS = ["apartment_id", "site_id", "floor_id", "unit_usage",
        "entity_type", "entity_subtype", "geometry"]
AREA_TOL, ASPECT_TOL, SEED = 0.10, 0.15, 20260819
COLLAPSE = {"ROOM": "PRIVATE", "BEDROOM": "PRIVATE", "STUDIO": "PRIVATE"}

# `k[type]` from docs/research/room-area-bands.md 6.1, in the corpus vocabulary.
K = {"PRIVATE": 2.18, "BATHROOM": 2.23, "WC": 3.36, "KITCHEN": 2.56,
     "LIVING_DINING": 2.02, "LIVING_ROOM": 2.35, "CORRIDOR": 3.28,
     "DINING": 3.67, "STOREROOM": 8.15}
K_DEFAULT = 2.5


def build_cache():
    rooms, polys = defaultdict(list), defaultdict(list)
    for chunk in pd.read_csv(GEOM, usecols=COLS, chunksize=500_000, dtype=str):
        a = chunk[(chunk["entity_type"] == "area") &
                  (chunk["unit_usage"] == "RESIDENTIAL") &
                  (chunk["apartment_id"] != MD5_EMPTY)]
        a = a[~a["entity_subtype"].isin(NOT_A_ROOM)]
        for s, f, ap, sub, wkt in zip(a["site_id"], a["floor_id"], a["apartment_id"],
                                      a["entity_subtype"].fillna("<NA>"), a["geometry"]):
            rooms[(s, f, ap)].append(sub)
            polys[(s, f, ap)].append(wkt)
    recs = []
    for key, subs in rooms.items():
        gs, kept = [], []
        for sub, w in zip(subs, polys[key]):
            g = from_wkt(w)
            if g is None or g.is_empty:
                continue
            gs.append(g.buffer(0))
            kept.append((COLLAPSE.get(sub, sub), float(g.area)))
        if not gs:
            continue
        u = unary_union(gs)
        mrr = u.minimum_rotated_rectangle
        if not hasattr(mrr, "exterior"):
            continue
        cc = np.asarray(mrr.exterior.coords)[:-1]
        if len(cc) < 4:
            continue
        e = np.linalg.norm(np.diff(np.vstack([cc, cc[:1]]), axis=0), axis=1)
        w_, d_ = sorted(e[:2])
        if w_ <= 0.01:
            continue
        recs.append({"k": "|".join(key), "rooms": kept, "n": len(kept),
                     "area": float(sum(a for _, a in kept)),
                     "aspect": float(d_ / w_)})
    OUT.mkdir(exist_ok=True)
    json.dump(recs, open(CACHE, "w"))
    return recs


def ms_of(rec):
    return tuple(sorted(Counter(t for t, _ in rec["rooms"]).items()))


def pair_by_type(target_rooms, pool_rooms):
    """The only assignment retrieval can make: same type, largest to largest."""
    by_t_target, by_t_pool = defaultdict(list), defaultdict(list)
    for t, a in target_rooms:
        by_t_target[t].append(a)
    for t, a in pool_rooms:
        by_t_pool[t].append(a)
    for t in by_t_target:
        for tgt, src in zip(sorted(by_t_target[t], reverse=True),
                            sorted(by_t_pool[t], reverse=True)):
            yield t, tgt, src


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(p * len(xs)))]


def main():
    recs = json.load(open(CACHE)) if CACHE.exists() else build_cache()
    print(f"dwellings: {len(recs):,}")
    for r in recs:
        r["ms"] = ms_of(r)

    by_ms, by_n = defaultdict(list), defaultdict(list)
    for r in recs:
        by_ms[r["ms"]].append(r)
        by_n[r["n"]].append(r)

    bands = {"4-6": range(4, 7), "7-10": range(7, 11)}
    MAXPOOL = 20
    summary = {}
    for band, rr in bands.items():
        rng = random.Random(SEED)
        sel = [r for r in recs if r["n"] in rr]
        ratios, over_k, under70 = [], 0, 0
        per_pool_worst = []
        pool_members = 0
        pooled_briefs = 0
        for r in sel:
            d = rng.choice(by_n[r["n"]])
            pool = [p for p in by_ms[r["ms"]]
                    if p["k"] != r["k"]
                    and abs(p["area"] - d["area"]) <= AREA_TOL * d["area"]
                    and abs(p["aspect"] - d["aspect"]) <= ASPECT_TOL * d["aspect"]]
            if not pool:
                continue
            pooled_briefs += 1
            if len(pool) > MAXPOOL:
                pool = rng.sample(pool, MAXPOOL)
            for p in pool:
                pool_members += 1
                s = d["area"] / p["area"]
                worst_hi, worst_lo, breach = 1.0, 1.0, False
                for t, tgt, src in pair_by_type(r["rooms"], p["rooms"]):
                    ratio = (src * s) / tgt
                    ratios.append(ratio)
                    worst_hi = max(worst_hi, ratio)
                    worst_lo = min(worst_lo, ratio)
                    if ratio > K.get(t, K_DEFAULT):
                        breach = True
                if breach:
                    over_k += 1
                if worst_lo < 0.70:
                    under70 += 1
                per_pool_worst.append((worst_lo, worst_hi))
        print(f"\nband {band}: {pooled_briefs:,} briefs with a pool, "
              f"{pool_members:,} (brief, pool member) pairs, {len(ratios):,} rooms")
        print(f"  per-room warped/target ratio: "
              f"p5 {pct(ratios,0.05):.3f}  p25 {pct(ratios,0.25):.3f}  "
              f"median {pct(ratios,0.5):.3f}  p75 {pct(ratios,0.75):.3f}  "
              f"p95 {pct(ratios,0.95):.3f}  p99 {pct(ratios,0.99):.3f}")
        adev = [abs(x - 1) for x in ratios]
        print(f"  |ratio-1|: median {st.median(adev):.3f}  "
              f"p90 {pct(adev,0.90):.3f}  p99 {pct(adev,0.99):.3f}")
        print(f"  candidates breaching dim.max_area (k[type] x target): "
              f"{over_k:,}/{pool_members:,} = {100*over_k/pool_members:.1f}%")
        print(f"  candidates with a room below 0.70 x target:           "
              f"{under70:,}/{pool_members:,} = {100*under70/pool_members:.1f}%")
        lo = [a for a, _ in per_pool_worst]
        hi = [b for _, b in per_pool_worst]
        print(f"  per-candidate worst room: smallest median {st.median(lo):.3f}, "
              f"largest median {st.median(hi):.3f}")
        summary[band] = {
            "briefs_with_pool": pooled_briefs, "pairs": pool_members,
            "rooms": len(ratios),
            "ratio_p5": pct(ratios, 0.05), "ratio_p50": pct(ratios, 0.5),
            "ratio_p95": pct(ratios, 0.95), "ratio_p99": pct(ratios, 0.99),
            "absdev_p50": st.median(adev), "absdev_p90": pct(adev, 0.90),
            "breach_max_area_pct": 100 * over_k / pool_members,
            "below_070_pct": 100 * under70 / pool_members,
        }
    OUT.mkdir(exist_ok=True)
    json.dump(summary, open(OUT / "room_area_spread.json", "w"), indent=1)
    print(f"\nwrote {OUT/'room_area_spread.json'}")


if __name__ == "__main__":
    main()
