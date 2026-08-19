"""Retrieval coverage — pass 3, the honest test.

Pass 2 asked each real dwelling for peers matching ITS OWN multiset and ITS OWN
envelope. That flatters retrieval: in the corpus those two came as a pair, so the
programme and the shape were designed together.

A Homeowner's Brief does not work that way. They state the flat they already have
and the rooms they want, and nothing guarantees the corpus ever paired them.

So: hold the multiset, swap the envelope for one drawn from a different dwelling
of the same room count (which preserves the real area/room-count correlation),
and re-ask. Same tolerances.

Also caches per-dwelling records so later passes need no 1 GB re-read.

Run: python experiments/retrieval-coverage/cross_coverage.py
"""

import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from shapely import from_wkt
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
GEOM = ROOT / "data" / "corpora" / "swiss-dwellings" / "swiss-dwellings-v3.0.0" / "geometries.csv"
OUT = Path(__file__).resolve().parent / "out"
CACHE = OUT / "dwelling_records.json"

NOT_A_ROOM = {
    "SHAFT", "VOID", "OUTDOOR_VOID", "LIGHTWELL", "ELEVATOR", "STAIRCASE",
    "TECHNICAL_AREA", "BALCONY", "LOGGIA", "TERRACE", "GARDEN", "PATIO",
    "WINTERGARTEN",
}
MD5_EMPTY = "d41d8cd98f00b204e9800998ecf8427e"
COLS = ["apartment_id", "site_id", "floor_id", "unit_usage",
        "entity_type", "entity_subtype", "geometry"]
AREA_TOL, ASPECT_TOL = 0.10, 0.15
SEED = 20260819


def build_cache():
    rooms, polys = defaultdict(Counter), defaultdict(list)
    for chunk in pd.read_csv(GEOM, usecols=COLS, chunksize=500_000, dtype=str):
        a = chunk[(chunk["entity_type"] == "area") &
                  (chunk["unit_usage"] == "RESIDENTIAL") &
                  (chunk["apartment_id"] != MD5_EMPTY)]
        a = a[~a["entity_subtype"].isin(NOT_A_ROOM)]
        for s, f, ap, st, wkt in zip(a["site_id"], a["floor_id"], a["apartment_id"],
                                     a["entity_subtype"].fillna("<NA>"), a["geometry"]):
            rooms[(s, f, ap)][st] += 1
            polys[(s, f, ap)].append(wkt)
    recs = []
    for k, c in rooms.items():
        gs = [g for g in (from_wkt(w) for w in polys[k]) if g is not None and not g.is_empty]
        if not gs:
            continue
        u = unary_union([g.buffer(0) for g in gs])
        mrr = u.minimum_rotated_rectangle
        if not hasattr(mrr, "exterior"):
            continue
        cc = np.asarray(mrr.exterior.coords)[:-1]
        if len(cc) < 4:
            continue
        e = np.linalg.norm(np.diff(np.vstack([cc, cc[:1]]), axis=0), axis=1)
        w, d = sorted(e[:2])
        if w <= 0.01:
            continue
        recs.append({"k": "|".join(k), "ms": sorted(c.items()), "n": sum(c.values()),
                     "area": float(sum(g.area for g in gs)),
                     "aspect": float(d / w)})
    json.dump(recs, open(CACHE, "w"))
    return recs


def main():
    OUT.mkdir(exist_ok=True)
    recs = json.load(open(CACHE)) if CACHE.exists() else build_cache()
    for r in recs:
        r["ms"] = tuple((a, b) for a, b in r["ms"])
    print(f"dwellings: {len(recs):,}")

    by_ms = defaultdict(list)
    by_n = defaultdict(list)
    for r in recs:
        by_ms[r["ms"]].append(r)
        by_n[r["n"]].append(r)

    rng = random.Random(SEED)
    bands = {"4-6": range(4, 7), "7-10": range(7, 11), "11-15": range(11, 16)}
    print(f"\nBRIEF = this dwelling's multiset + ANOTHER dwelling's envelope "
          f"(same room count)")
    print(f"{'band':<8}{'briefs':>9}{'pool=0':>10}{'<3':>9}{'median':>9}{'>=20':>9}")
    dump = {}
    for b, rng_n in bands.items():
        sel = [r for r in recs if r["n"] in rng_n]
        pools = []
        for r in sel:
            donor = rng.choice(by_n[r["n"]])
            tgt_area, tgt_aspect = donor["area"], donor["aspect"]
            pools.append(sum(1 for p in by_ms[r["ms"]]
                             if abs(p["area"] - tgt_area) <= AREA_TOL * tgt_area
                             and abs(p["aspect"] - tgt_aspect) <= ASPECT_TOL * tgt_aspect))
        pools.sort()
        m = len(pools)
        z = sum(1 for x in pools if x == 0)
        print(f"{b:<8}{m:>9,}{z:>10,}{sum(1 for x in pools if x<3):>9,}"
              f"{pools[m//2]:>9,}{sum(1 for x in pools if x>=20):>9,}")
        dump[b] = {"briefs": m, "zero": z, "lt3": sum(1 for x in pools if x < 3),
                   "median": pools[m//2], "ge20": sum(1 for x in pools if x >= 20),
                   "zero_pct": round(100*z/m, 1)}

    # how much of the loss is area vs proportion
    print("\nwhich half of the envelope constraint does the damage (4-10 rooms)")
    sel = [r for r in recs if 4 <= r["n"] <= 10]
    rng = random.Random(SEED)
    for label, use_area, use_aspect in (("multiset only", False, False),
                                        ("+ area", True, False),
                                        ("+ aspect", False, True),
                                        ("+ both", True, True)):
        rng2 = random.Random(SEED)
        pools = []
        for r in sel:
            d = rng2.choice(by_n[r["n"]])
            c = 0
            for p in by_ms[r["ms"]]:
                if use_area and abs(p["area"] - d["area"]) > AREA_TOL * d["area"]:
                    continue
                if use_aspect and abs(p["aspect"] - d["aspect"]) > ASPECT_TOL * d["aspect"]:
                    continue
                c += 1
            pools.append(c)
        pools.sort()
        z = sum(1 for x in pools if x == 0)
        print(f"  {label:<16} median={pools[len(pools)//2]:>5,}  "
              f"pool=0 {z:>6,} ({100*z/len(pools):.1f}%)")

    json.dump(dump, open(OUT / "cross_coverage.json", "w"), indent=1)
    print(f"\nwrote {OUT/'cross_coverage.json'} and cached {CACHE.name}")


if __name__ == "__main__":
    main()
