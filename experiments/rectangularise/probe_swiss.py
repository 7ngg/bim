"""Probe: what does a Swiss Dwellings dwelling actually look like, geometrically?

Questions this answers before any harness is written:
  - do room polygons abut, or are they separated by wall bodies?
  - are they simple polygons, or multi/holed?
  - what axis are they on, and how much does the axis choice move rectangularity?
  - how rectangular are they, really (nobody has measured this corpus)?

Run: python experiments/rectangularise/probe_swiss.py
"""
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from shapely import from_wkt
from shapely.affinity import rotate
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
GEOM = ROOT / "data" / "corpora" / "swiss-dwellings" / "swiss-dwellings-v3.0.0" / "geometries.csv"

NOT_A_ROOM = {
    "SHAFT", "VOID", "OUTDOOR_VOID", "LIGHTWELL", "ELEVATOR", "STAIRCASE",
    "TECHNICAL_AREA", "BALCONY", "LOGGIA", "TERRACE", "GARDEN", "PATIO",
    "WINTERGARTEN",
}
MD5_EMPTY = "d41d8cd98f00b204e9800998ecf8427e"
COLS = ["apartment_id", "site_id", "floor_id", "unit_usage",
        "entity_type", "entity_subtype", "geometry"]

N_CHUNKS = 2   # enough for a few thousand dwellings


def dominant_axis(polys):
    """Length-weighted histogram of edge directions mod 90 degrees."""
    acc = np.zeros(900)  # 0.1 degree bins over [0, 90)
    for p in polys:
        cc = np.asarray(p.exterior.coords)
        d = np.diff(cc, axis=0)
        L = np.hypot(d[:, 0], d[:, 1])
        ang = np.degrees(np.arctan2(d[:, 1], d[:, 0])) % 90.0
        for a, l in zip(ang, L):
            acc[int(a * 10) % 900] += l
    return acc.argmax() / 10.0


def main():
    rows = []
    for i, chunk in enumerate(pd.read_csv(GEOM, usecols=COLS, chunksize=500_000, dtype=str)):
        rows.append(chunk)
        if i + 1 >= N_CHUNKS:
            break
    df = pd.concat(rows)
    a = df[(df["entity_type"] == "area") &
           (df["unit_usage"] == "RESIDENTIAL") &
           (df["apartment_id"] != MD5_EMPTY)]
    a = a[~a["entity_subtype"].isin(NOT_A_ROOM)]
    print(f"area rows in sample: {len(a)}")

    dw = defaultdict(list)
    for s, f, ap, st, wkt in zip(a["site_id"], a["floor_id"], a["apartment_id"],
                                 a["entity_subtype"].fillna("<NA>"), a["geometry"]):
        dw[(s, f, ap)].append((st, wkt))
    print(f"dwellings in sample: {len(dw)}")

    # --- geometry shape census -------------------------------------------
    kinds, nholes, nverts = Counter(), Counter(), Counter()
    for k, items in dw.items():
        for st, wkt in items:
            g = from_wkt(wkt)
            kinds[g.geom_type] += 1
            if g.geom_type == "Polygon":
                nholes[len(g.interiors)] += 1
                nverts[min(len(g.exterior.coords) - 1, 20)] += 1
    print("\ngeom types:", dict(kinds))
    print("interior rings:", dict(sorted(nholes.items())))
    print("exterior vertex count (capped at 20):", dict(sorted(nverts.items())))

    # --- do rooms abut, or is there a wall gap? --------------------------
    gaps = []
    sample = [k for k in dw if 4 <= len(dw[k]) <= 10][:300]
    for k in sample:
        gs = [from_wkt(w).buffer(0) for _, w in dw[k]]
        gs = [g for g in gs if not g.is_empty and g.area > 0.5]
        for i in range(len(gs)):
            best = min((gs[i].distance(gs[j]) for j in range(len(gs)) if j != i),
                       default=None)
            if best is not None:
                gaps.append(best)
    gaps = np.array(gaps)
    if len(gaps):
        print(f"\nnearest-neighbour room gap, m  (n={len(gaps)}):")
        for q in (5, 25, 50, 75, 95):
            print(f"  p{q:<3} {np.percentile(gaps, q):.4f}")
        print(f"  share exactly 0 (touching): {(gaps < 1e-9).mean():.3f}")
        print(f"  share < 1 mm:               {(gaps < 0.001).mean():.3f}")

    # --- axis + rectangularity -------------------------------------------
    print("\naxis and rectangularity, 300 dwellings:")
    stats = {"mrr": [], "hist": [], "raw": []}
    ang_diff = []
    for k in sample:
        gs = [from_wkt(w).buffer(0) for _, w in dw[k]]
        gs = [g for g in gs if not g.is_empty and g.area > 0.5 and g.geom_type == "Polygon"]
        if len(gs) < 3:
            continue
        u = unary_union(gs)
        mrr = u.minimum_rotated_rectangle
        if not hasattr(mrr, "exterior"):
            continue
        cc = np.asarray(mrr.exterior.coords)
        e = cc[1] - cc[0]
        a_mrr = math.degrees(math.atan2(e[1], e[0])) % 90.0
        a_hist = dominant_axis(gs)
        d = abs(a_mrr - a_hist)
        ang_diff.append(min(d, 90 - d))
        cen = u.centroid
        for name, ang in (("raw", 0.0), ("mrr", a_mrr), ("hist", a_hist)):
            for g in gs:
                gg = rotate(g, -ang, origin=cen) if ang else g
                bb = gg.bounds
                bba = (bb[2] - bb[0]) * (bb[3] - bb[1])
                stats[name].append(gg.area / bba if bba > 0 else 0.0)
    for name in ("raw", "mrr", "hist"):
        v = np.array(stats[name])
        print(f"  {name:<5} n={len(v):<6} rect(1%)={np.mean(v > 0.99):.3f} "
              f"rect(2%)={np.mean(v > 0.98):.3f} rect(5%)={np.mean(v > 0.95):.3f} "
              f"median fill={np.median(v):.4f}")
    ad = np.array(ang_diff)
    print(f"\n  |mrr axis - hist axis|, deg: median {np.median(ad):.2f}  "
          f"p95 {np.percentile(ad, 95):.2f}  share >2deg {np.mean(ad > 2):.3f}")


if __name__ == "__main__":
    main()
