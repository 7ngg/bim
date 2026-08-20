"""What makes a room need more than two rectangles?

`rectilinear_k.py` says 22% of rooms need k >= 3. That number is an upper bound
with three known inflators, and the decision in ticket 28 turns on which of them
is doing the work:

  1. GUILLOTINE ONLY. A pinwheel needs a non-guillotine partition and gets
     counted worse than it is.
  2. RASTER STAIRCASES. A real wall a couple of degrees off axis becomes a
     staircase at 250 mm, and a staircase needs one rectangle per step. This is
     not architecture, it is the grid.
  3. TRIVIAL NOTCHES. A pipe boxing, a door reveal, a chimney breast. Each adds a
     reflex corner and therefore a rectangle, and none of them is a room shape.

Against one real cause: the room genuinely is a T, U, S or Z.

Four diagnostics per room:
  k_raw       k as rectilinear_k.py measures it
  k_clean     k after a morphological open+close at 500 mm, which erases any
              feature narrower than that -- inflator 3
  offaxis     share of perimeter more than 2 deg off the dwelling axis -- inflator 2
  iou2        area covered by the best two inscribed rectangles, over room area:
              what capping at k = 2 would actually cost, in area rather than count

Run: python experiments/rectangularise/why_k.py [n_dwellings]
"""
import hashlib
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from shapely import from_wkt
from shapely.affinity import rotate

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fit_rects import max_rect_in_mask  # noqa: E402
from measure_swiss import (  # noqa: E402
    BAND, COLS, GEOM, MD5_EMPTY, MIN_ROOM_AREA, NOT_A_ROOM, _poly, dwelling_frame,
)
from rectilinear_k import GRID, guillotine_k, rasterise  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
CLEAN_CELLS = 2   # 500 mm structuring element


def _shift_all(m, r):
    """Logical AND / OR over every offset within a (2r+1) square, via padding."""
    h, w = m.shape
    pad = np.pad(m, r, constant_values=False)
    stack = []
    for dy in range(2 * r + 1):
        for dx in range(2 * r + 1):
            stack.append(pad[dy:dy + h, dx:dx + w])
    return np.stack(stack)


def erode(m, r):
    return _shift_all(m, r).all(axis=0)


def dilate(m, r):
    return _shift_all(m, r).any(axis=0)


def clean(m, r=CLEAN_CELLS):
    """Opening then closing: drop protrusions and fill notches narrower than r."""
    return erode(dilate(erode(dilate(m, r), r), r), r)


def offaxis_fraction(g):
    """Share of perimeter length more than 2 degrees off an axis."""
    cc = np.asarray(g.exterior.coords)
    d = np.diff(cc, axis=0)
    L = np.hypot(d[:, 0], d[:, 1])
    ang = np.degrees(np.arctan2(np.abs(d[:, 1]), np.abs(d[:, 0])))
    off = np.minimum(ang, 90.0 - ang) > 2.0
    return float(L[off].sum() / L.sum()) if L.sum() else 0.0


def best_two_cover(m):
    """Area covered by the best two inscribed rectangles, as a share of the room.

    Greedy (largest inscribed, then largest inscribed of the remainder) raced
    against every guillotine cut (largest inscribed each side). Both are lower
    bounds on the true optimum, so the reported cost of capping at k = 2 is if
    anything overstated.
    """
    total = int(m.sum())
    if total == 0:
        return 0.0
    r1 = max_rect_in_mask(m)
    if r1 is None:
        return 0.0
    a1 = (r1[2] - r1[0]) * (r1[3] - r1[1])
    rest = m.copy()
    rest[r1[1]:r1[3], r1[0]:r1[2]] = False
    best = a1
    if rest.any():
        r2 = max_rect_in_mask(rest)
        if r2 is not None:
            best = max(best, a1 + (r2[2] - r2[0]) * (r2[3] - r2[1]))
    h, w = m.shape
    for axis in (0, 1):
        n = w if axis == 0 else h
        for c in range(1, n):
            a = m[:, :c] if axis == 0 else m[:c, :]
            b = m[:, c:] if axis == 0 else m[c:, :]
            if not a.any() or not b.any():
                continue
            ra, rb = max_rect_in_mask(a), max_rect_in_mask(b)
            if ra is None or rb is None:
                continue
            s = ((ra[2] - ra[0]) * (ra[3] - ra[1]) +
                 (rb[2] - rb[0]) * (rb[3] - rb[1]))
            if s > best:
                best = s
    return best / total


def main():
    n_target = int(sys.argv[1]) if len(sys.argv) > 1 else 700
    dw = defaultdict(list)
    for chunk in pd.read_csv(GEOM, usecols=COLS, chunksize=500_000, dtype=str):
        a = chunk[(chunk["entity_type"] == "area") &
                  (chunk["unit_usage"] == "RESIDENTIAL") &
                  (chunk["apartment_id"] != MD5_EMPTY)]
        a = a[~a["entity_subtype"].isin(NOT_A_ROOM)]
        for s, f, ap, st, wkt in zip(a["site_id"], a["floor_id"], a["apartment_id"],
                                     a["entity_subtype"].fillna("<NA>"), a["geometry"]):
            dw[(s, f, ap)].append((st, wkt))
    keys = sorted(dw.keys())
    keys.sort(key=lambda k: hashlib.md5("|".join(k).encode()).hexdigest())

    rows, done = [], 0
    for k in keys:
        if done >= n_target:
            break
        geoms, types = [], []
        for st, wkt in dw[k]:
            g = _poly(from_wkt(wkt))
            if g is not None and g.area >= MIN_ROOM_AREA:
                geoms.append(g)
                types.append(st)
        if not (BAND[0] <= len(geoms) <= BAND[1]):
            continue
        ang, cen = dwelling_frame(geoms)
        if ang is None:
            continue
        geoms = [rotate(g, -ang, origin=cen) for g in geoms]
        ok = True
        buf = []
        for g, t in zip(geoms, types):
            x0, y0, x1, y1 = g.bounds
            nx = max(1, int(math.ceil((x1 - x0) / GRID)))
            ny = max(1, int(math.ceil((y1 - y0) / GRID)))
            if nx * ny > 12_000:
                ok = False
                break
            m = rasterise(g, x0, y0, nx, ny)
            if not m.any():
                continue
            kr = guillotine_k(m)
            mc = clean(m)
            kc = guillotine_k(mc) if mc.any() else None
            buf.append({
                "type": t,
                "k_raw": kr if kr else 99,
                "k_clean": kc if kc else 99,
                "offaxis": offaxis_fraction(g),
                "iou2": best_two_cover(m),
                "area": g.area,
            })
        if not ok:
            continue
        rows += buf
        done += 1
        if done % 200 == 0:
            print(f"  {done}", flush=True)

    n = len(rows)
    hard = [r for r in rows if r["k_raw"] >= 3]
    print(f"\ndwellings {done}, rooms {n}, of which k>=3: {len(hard)} "
          f"({len(hard) / n:.4f})\n")

    print("=" * 72)
    print("1. DOES A 500 mm CLEAN-UP REMOVE IT?  (inflator 3: trivial notches)")
    print("=" * 72)
    move = Counter()
    for r in hard:
        move[min(r["k_clean"], 5)] += 1
    for kk in sorted(move):
        lab = str(kk) if kk < 5 else ">=5"
        print(f"   k>=3 rooms that clean to k = {lab:<4} {move[kk]:>6}"
              f"  {move[kk] / len(hard):.4f}")
    still = sum(v for kk, v in move.items() if kk >= 3)
    print(f"\n   -> {1 - still / len(hard):.4f} of k>=3 rooms are k<=2 once features"
          f" narrower than 500 mm are erased")

    print("\n" + "=" * 72)
    print("2. ARE THEY EVEN RECTILINEAR?  (inflator 2: raster staircases)")
    print("=" * 72)
    for lab, sub in (("all rooms", rows), ("k = 1", [r for r in rows if r["k_raw"] == 1]),
                     ("k = 2", [r for r in rows if r["k_raw"] == 2]),
                     ("k >= 3", hard)):
        v = np.array([r["offaxis"] for r in sub])
        if not len(v):
            continue
        print(f"   {lab:<10} n={len(v):>6}  off-axis perimeter: median {np.median(v):.4f}"
              f"  p90 {np.percentile(v, 90):.4f}  share >10%: {np.mean(v > 0.10):.4f}")

    print("\n" + "=" * 72)
    print("3. WHAT DOES CAPPING AT TWO RECTANGLES ACTUALLY COST, IN AREA?")
    print("=" * 72)
    for lab, sub in (("all rooms", rows), ("k >= 3 only", hard)):
        v = np.array([r["iou2"] for r in sub])
        print(f"   {lab:<12} coverage by best 2 rects: median {np.median(v):.4f}"
              f"  p25 {np.percentile(v, 25):.4f}  p5 {np.percentile(v, 5):.4f}"
              f"  >=0.95: {np.mean(v >= .95):.4f}")

    print("\n" + "=" * 72)
    print("4. WHICH ROOMS ARE GENUINELY COMPLEX")
    print("=" * 72)
    by = defaultdict(list)
    for r in rows:
        by[r["type"]].append(r)
    print(f"{'type':<16} {'n':>6} {'k>=3 raw':>9} {'k>=3 clean':>11} {'iou2 med':>9}")
    for t, sub in sorted(by.items(), key=lambda kv: -len(kv[1])):
        if len(sub) < 300:
            continue
        raw = np.mean([r["k_raw"] >= 3 for r in sub])
        cln = np.mean([r["k_clean"] >= 3 for r in sub])
        i2 = np.median([r["iou2"] for r in sub])
        print(f"{t:<16} {len(sub):>6} {raw:>9.4f} {cln:>11.4f} {i2:>9.4f}")


if __name__ == "__main__":
    main()
