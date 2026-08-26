"""What shape a real dwelling's exterior ring is, per bbox side.

`EXPOSURE_PRESETS` in `solver-toy/geometry.py` is a **four-vector** -- a fraction
of exterior run per bbox edge, keyed W/E/S/N. Every number ever fitted to it came
from `dataset-inventory.md` §1.5, which publishes a **scalar**: the fraction of a
dwelling's perimeter that faces outside. A scalar cannot fit a four-vector, so
`corpus_median` and `flat_single_aspect` were fitted by choosing a ring shape by
hand and then tuning one number until the scalar matched.

This measures the vector. Per dwelling:

  1. weld the rooms across their walls (§1.5's BRIDGE_M fix -- without it the
     script measures the largest single room, which is the defect this ticket
     exists to repair),
  2. find the dwelling's dominant wall direction and rotate it axis-aligned,
  3. classify every boundary segment as exterior or party by §1.5's PARTY_GAP_M
     rule, and assign it to W/E/S/N by its outward normal,
  4. report, per side, exterior run / bbox edge length -- which is exactly what a
     preset's four numbers mean.

Writes `series/dwelling_sides.json.gz`: one record per dwelling, so a later
percentile off this study costs seconds rather than a re-scan of a 1.09 GB corpus.
Per `experiments/thickness-fidelity/`'s rule: if you add a statistic to this
study, add its inputs to the series.

Run: ../../venv/Scripts/python.exe fit_presets.py [n_floors]
"""

import gzip
import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
from shapely import wkt
from shapely.affinity import rotate
from shapely.geometry import LineString, MultiLineString
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
GEOM = ROOT / "data" / "corpora" / "swiss-dwellings" / "swiss-dwellings-v3.0.0" / "geometries.csv"
OUT = Path(__file__).resolve().parent / "series"

# All three constants are §1.5's, unchanged, so the scalar this script derives is
# comparable with the published one rather than merely similar to it.
NULL_APT = "d41d8cd98f00b204e9800998ecf8427e"
NOT_A_ROOM = {"SHAFT", "VOID", "OUTDOOR_VOID", "LIGHTWELL", "ELEVATOR", "STAIRCASE",
              "TECHNICAL_AREA", "BALCONY", "LOGGIA", "TERRACE", "GARDEN", "PATIO",
              "WINTERGARTEN"}
PARTY_GAP_M = 0.45
BRIDGE_M = 0.12

# A side carrying less than this much of its own bbox edge is not an aspect. A
# window plus its two piers is about 1.5 m; below that the side cannot hold one,
# so counting it as an aspect would name a dwelling dual-aspect on a sliver.
MATERIAL_SIDE = 0.15

N_FLOORS = int(sys.argv[1]) if len(sys.argv) > 1 else 600
SIDES = ("W", "E", "S", "N")


def dominant_angle(poly) -> float:
    """The dwelling's wall direction, in degrees, folded into [0, 90).

    Edge-length-weighted histogram of boundary segment angles mod 90. Swiss
    dwellings sit on an arbitrary geo-referenced bearing; without this every
    dwelling's bbox is a diagonal hull and the four sides are meaningless.
    """
    hist = [0.0] * 90
    xs, ys = poly.exterior.coords.xy
    for i in range(len(xs) - 1):
        dx, dy = xs[i + 1] - xs[i], ys[i + 1] - ys[i]
        L = math.hypot(dx, dy)
        if L < 0.05:
            continue
        a = math.degrees(math.atan2(dy, dx)) % 90.0
        hist[int(a) % 90] += L
    best = max(range(90), key=lambda k: hist[k])
    # refine to the length-weighted mean inside the winning degree bucket
    return float(best) + 0.5


def side_of(p, q) -> str:
    """Which bbox edge a boundary segment faces, from its outward normal.

    Shapely exteriors are counter-clockwise, so the outward normal of the
    segment p->q is (dy, -dx).
    """
    dx, dy = q[0] - p[0], q[1] - p[1]
    nx, ny = dy, -dx
    if abs(nx) >= abs(ny):
        return "E" if nx > 0 else "W"
    return "N" if ny > 0 else "S"


def scan(n_floors: int):
    cols = ["apartment_id", "site_id", "floor_id", "unit_usage",
            "entity_type", "entity_subtype", "geometry"]

    counts = defaultdict(set)
    for ch in pd.read_csv(GEOM, usecols=[c for c in cols if c != "geometry"],
                          chunksize=1_000_000, dtype=str):
        a = ch[(ch.entity_type == "area") & (ch.unit_usage == "RESIDENTIAL")
               & (ch.apartment_id != NULL_APT)]
        for s, f, ap in zip(a.site_id, a.floor_id, a.apartment_id):
            counts[(s, f)].add(ap)
    multi = sorted(k for k, v in counts.items() if len(v) >= 2)
    random.seed(20260819)                       # §1.5's seed
    pick = set(random.sample(multi, min(n_floors, len(multi))))
    print(f"floors with >=2 residential apartments: {len(multi):,}; sampling {len(pick)}")

    dwell = defaultdict(list)
    occupied = defaultdict(list)
    for ch in pd.read_csv(GEOM, usecols=cols, chunksize=500_000, dtype=str):
        ch = ch[ch.entity_type == "area"]
        if ch.empty:
            continue
        key = list(zip(ch.site_id, ch.floor_id))
        ch = ch[[k in pick for k in key]]
        if ch.empty:
            continue
        for s, f, ap, usage, sub, g in zip(ch.site_id, ch.floor_id, ch.apartment_id,
                                           ch.unit_usage, ch.entity_subtype, ch.geometry):
            if sub in NOT_A_ROOM:
                continue
            try:
                poly = wkt.loads(g)
            except Exception:
                continue
            if poly.is_empty:
                continue
            occupied[(s, f)].append(poly)
            if usage == "RESIDENTIAL" and ap != NULL_APT:
                dwell[(s, f, ap)].append(poly)
    return dwell, occupied


def measure(dwell, occupied):
    recs = []
    for (s, f, ap), polys in dwell.items():
        env = unary_union([p.buffer(BRIDGE_M) for p in polys]).buffer(-BRIDGE_M)
        if env.is_empty or env.geom_type not in ("Polygon", "MultiPolygon"):
            continue
        if env.geom_type == "MultiPolygon":
            env = max(env.geoms, key=lambda p: p.area)
        others = [p for p in occupied[(s, f)] if not p.intersects(env.buffer(-0.05))]
        if not others:
            continue
        near = unary_union([p.buffer(PARTY_GAP_M) for p in others])

        boundary = env.exterior
        free = boundary.difference(near)          # the exterior run, unrotated
        total = boundary.length
        if total <= 0:
            continue
        scalar = free.length / total              # §1.5's published quantity

        # Rotate dwelling and its free run together onto the wall direction.
        ang = dominant_angle(env)
        pivot = env.centroid
        env_r = rotate(env, -ang, origin=pivot)
        free_r = rotate(free, -ang, origin=pivot) if free.length > 0 else free
        x1, y1, x2, y2 = env_r.bounds
        bw, bh = x2 - x1, y2 - y1
        if bw <= 0 or bh <= 0:
            continue

        run = {k: 0.0 for k in SIDES}
        parts = ([] if free_r.is_empty else
                 list(free_r.geoms) if isinstance(free_r, MultiLineString) else [free_r])
        for ls in parts:
            if not isinstance(ls, LineString):
                continue
            cs = list(ls.coords)
            for i in range(len(cs) - 1):
                p, q = cs[i], cs[i + 1]
                L = math.hypot(q[0] - p[0], q[1] - p[1])
                if L <= 0:
                    continue
                run[side_of(p, q)] += L

        denom = {"W": bh, "E": bh, "S": bw, "N": bw}
        frac = {k: run[k] / denom[k] for k in SIDES}
        recs.append({
            "id": f"{s}/{f}/{ap}",
            "scalar": scalar,
            "area": env.area,
            # H8 binds on exterior RUN, not on a fraction of perimeter: a room
            # needs a window's width of facade, and a fraction only transfers
            # between two dwellings whose perimeters match. `n_rooms` is the
            # dwelling's polygon count after NOT_A_ROOM filtering, which is the
            # engine's room count including circulation.
            "n_rooms": len(polys),
            "perimeter": total,
            "ext_run": free.length,
            "bbox": [bw, bh],
            "run": run,
            "frac": frac,
            "sat": sum(1 for k in SIDES if frac[k] > 1.0),
        })
    return recs


def family(frac) -> str:
    """Name the ring shape: which of the four sides carry a material aspect."""
    live = [k for k in SIDES if frac[k] >= MATERIAL_SIDE]
    n = len(live)
    if n == 0:
        return "none"
    if n == 1:
        return "single"
    if n == 2:
        return "opposite" if set(live) in ({"W", "E"}, {"S", "N"}) else "adjacent"
    if n == 3:
        return "three"
    return "four"


def pct(xs, p):
    xs = sorted(xs)
    if not xs:
        return float("nan")
    k = (len(xs) - 1) * p / 100.0
    lo, hi = int(math.floor(k)), int(math.ceil(k))
    return xs[lo] if lo == hi else xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def report(recs):
    n = len(recs)
    print(f"\ndwellings scored: {n:,}")

    sc = [r["scalar"] for r in recs]
    print("\nscalar exterior fraction of perimeter (reproduces dataset-inventory.md §1.5):")
    print(f"  p5 {pct(sc,5):.2f}  p25 {pct(sc,25):.2f}  median {statistics.median(sc):.2f}"
          f"  p75 {pct(sc,75):.2f}  p95 {pct(sc,95):.2f}")
    print(f"  >=0.99: {sum(1 for x in sc if x >= 0.99)} "
          f"({100*sum(1 for x in sc if x>=0.99)/n:.1f}%)")
    print(f"  median area {statistics.median([r['area'] for r in recs]):.1f} m2")

    fam = Counter(family(r["frac"]) for r in recs)
    print(f"\nring shape -- sides carrying >= {MATERIAL_SIDE:.2f} of their own bbox edge:")
    for k in ("none", "single", "adjacent", "opposite", "three", "four"):
        if fam[k]:
            print(f"  {k:>9}: {fam[k]:>5}  {100*fam[k]/n:5.1f}%")

    print("\nper-side fraction, sorted high-to-low within each dwelling "
          "(rotation-invariant, so this is the ring's PROFILE):")
    ranked = [sorted((r["frac"][k] for k in SIDES), reverse=True) for r in recs]
    for i, lab in enumerate(("1st", "2nd", "3rd", "4th")):
        col = [row[i] for row in ranked]
        print(f"  {lab}: p25 {pct(col,25):.2f}  median {statistics.median(col):.2f}"
              f"  p75 {pct(col,75):.2f}  mean {statistics.mean(col):.2f}")

    print("\nper-side profile of the MEDIAN-scalar decile "
          "(the dwellings a 'typical' preset must model):")
    band = sorted(recs, key=lambda r: abs(r["scalar"] - statistics.median(sc)))[:max(1, n // 10)]
    ranked_b = [sorted((r["frac"][k] for k in SIDES), reverse=True) for r in band]
    for i, lab in enumerate(("1st", "2nd", "3rd", "4th")):
        col = [row[i] for row in ranked_b]
        print(f"  {lab}: median {statistics.median(col):.2f}")
    print(f"  ring shapes in that band: "
          f"{dict(Counter(family(r['frac']) for r in band).most_common())}")

    print("\nper-side profile of the p25-scalar decile "
          "(what 'a poorly-exposed flat' really looks like):")
    band = sorted(recs, key=lambda r: abs(r["scalar"] - pct(sc, 25)))[:max(1, n // 10)]
    ranked_b = [sorted((r["frac"][k] for k in SIDES), reverse=True) for r in band]
    for i, lab in enumerate(("1st", "2nd", "3rd", "4th")):
        col = [row[i] for row in ranked_b]
        print(f"  {lab}: median {statistics.median(col):.2f}")
    print(f"  ring shapes in that band: "
          f"{dict(Counter(family(r['frac']) for r in band).most_common())}")

    print("\nper-side profile of the p5-scalar decile (the genuine single-aspect tail):")
    band = sorted(recs, key=lambda r: abs(r["scalar"] - pct(sc, 5)))[:max(1, n // 10)]
    ranked_b = [sorted((r["frac"][k] for k in SIDES), reverse=True) for r in band]
    for i, lab in enumerate(("1st", "2nd", "3rd", "4th")):
        col = [row[i] for row in ranked_b]
        print(f"  {lab}: median {statistics.median(col):.2f}")
    print(f"  ring shapes in that band: "
          f"{dict(Counter(family(r['frac']) for r in band).most_common())}")

    sat = sum(1 for r in recs if r["sat"])
    print(f"\nsides where exterior run exceeds the bbox edge (concavity): "
          f"{sat} dwellings ({100*sat/n:.1f}%) -- a preset caps at 1.0 and "
          f"cannot express these")


def main() -> None:
    dwell, occupied = scan(N_FLOORS)
    recs = measure(dwell, occupied)
    if not recs:
        print("no dwellings scored")
        return
    OUT.mkdir(exist_ok=True)
    with gzip.open(OUT / "dwelling_sides.json.gz", "wt", encoding="utf-8") as fh:
        json.dump(recs, fh)
    print(f"wrote {OUT / 'dwelling_sides.json.gz'} ({len(recs)} records)")
    report(recs)


if __name__ == "__main__":
    main()
