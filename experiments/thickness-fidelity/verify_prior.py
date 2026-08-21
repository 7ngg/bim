"""Ticket 33 — independently verify the prior this ticket is built on.

C11: a finding from before may be reused only after independent verification.
The prior is *Which region profiles ship in v1*, measured by
`experiments/corpus-smoke/wall_thickness_swiss.py` over a 200,000-wall random
sample of Swiss Dwellings `separator/WALL` rows:

    p1 42 · p5 61 · p25 109 · p50 169 · p75 267 · p95 440 · p99 590
    within +/-2 mm of a multiple of 10: 59.1 %   (uniform noise: 50 %)
    even millimetres:                   59.2 %
    most common snapped value: 80 mm at 5.60 %; top 20 cumulative 70.5 %
    8-entry catalogue covers 58.5 % at +/-10 mm; 12-entry 70.9 %

This reproduces exactly that statistic on a **different sample** — the 1-in-10
FLOOR sample in `out/cache.pkl.gz`, which is a different draw with a different
clustering structure — and then does the one thing the prior did not: splits it
by whether the wall is internal to a dwelling.

Run:  python experiments/thickness-fidelity/verify_prior.py
"""
from __future__ import annotations

import gzip
import json
import math
import pickle
from collections import Counter
from pathlib import Path

import numpy as np
from shapely import from_wkt, make_valid

OUT = Path(__file__).resolve().parent / "out"

CANDIDATES = [
    [100, 150, 200, 250, 300],
    [80, 100, 120, 150, 180, 200, 250, 300],
    [80, 100, 120, 140, 160, 180, 200, 240, 250, 300, 350, 400],
]


def minor_side(wkt_s):
    try:
        p = from_wkt(wkt_s)
    except Exception:
        return None
    if p is None or p.is_empty:
        return None
    if not p.is_valid:
        p = make_valid(p)
        if p.geom_type in ("GeometryCollection", "MultiPolygon"):
            parts = [q for q in p.geoms if q.geom_type == "Polygon"]
            if not parts:
                return None
            p = max(parts, key=lambda q: q.area)
    if p.geom_type != "Polygon" or p.area <= 0:
        return None
    mrr = p.minimum_rotated_rectangle
    if mrr is None or mrr.is_empty or mrr.geom_type != "Polygon" or mrr.area <= 0:
        return None
    if p.area / mrr.area < 0.95:
        return None
    c = list(mrr.exterior.coords)[:4]
    a = math.dist(c[0], c[1])
    b = math.dist(c[1], c[2])
    return round(min(a, b) * 1000)


def report(t, label):
    n = len(t)
    s = np.array(t, float)
    print(f"\n--- {label}   n = {n:,}")
    print("percentiles (mm):  " + "  ".join(
        f"p{q}={np.percentile(s, q):.0f}" for q in (1, 5, 25, 50, 75, 95, 99)))
    near10 = sum(1 for x in t if min(x % 10, 10 - x % 10) <= 2)
    even = sum(1 for x in t if x % 2 == 0)
    print(f"within +/-2 mm of a multiple of 10: {100 * near10 / n:.1f}%  (uniform 50%)")
    print(f"even millimetres:                   {100 * even / n:.1f}%  (uniform 50%)")
    top = Counter(round(x / 10) * 10 for x in t).most_common(20)
    print(f"most common snapped value: {top[0][0]} mm at {100*top[0][1]/n:.2f}%   "
          f"top 20 cumulative {100*sum(c for _, c in top)/n:.1f}%")
    for cat in CANDIDATES:
        hit = sum(1 for x in t if any(abs(x - c) <= 10 for c in cat))
        print(f"   {len(cat):2d}-entry catalogue, +/-10 mm: {100 * hit / n:5.1f}%")


def main() -> None:
    with gzip.open(OUT / "cache.pkl.gz", "rb") as fh:
        cache = pickle.load(fh)
    allw = [w for ws in cache["walls"].values() for w in ws]
    print(f"WALL separators on the 1-in-{cache['stride']} floor sample: {len(allw):,}")

    t, skipped = [], 0
    for wkt_s in allw:
        v = minor_side(wkt_s)
        if v is None:
            skipped += 1
        else:
            t.append(v)
    print(f"measured: {len(t):,}   skipped as non-rectangular: {skipped:,}")
    report(t, "ALL WALL separators — the prior's exact statistic")

    # Split by the classification measure.py produced.
    with gzip.open(OUT / "walls.json.gz", "rt", encoding="utf-8") as fh:
        d = json.load(fh)
    dwl = d["dwellings"]
    ti = [int(round(w["t_mrr"])) for r in dwl for w in r["internal"]]
    tb = [int(round(w["t_mrr"])) for r in dwl for w in r["boundary"]]
    report(ti, "INTERNAL walls only — separates two rooms of one dwelling")
    report(tb, "BOUNDARY walls only — exterior or party, one room only")


if __name__ == "__main__":
    main()
