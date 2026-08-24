"""How many rectangles does a real room need, allowing a stated tolerance?

`rectilinear_k.py` asks for an EXACT decomposition, which makes k hostage to a
single 250 mm cell: one pipe boxing, one door reveal, one wall two degrees off
axis, and k jumps. `why_k.py` tried to separate those out with a morphological
clean-up whose operator does not do what its name says (see `morphology.py`), so
its 0.5833 and 0.3103 are measured against "the room eroded by 500 mm all round"
rather than "the room with small hardware erased".

This replaces both readings with one that needs no morphology and states its own
threshold: for each room, the area covered by its best k inscribed rectangles,
for k = 1, 2, 3 -- and `k_tol`, the smallest k reaching a stated coverage. That
is the question a drawn plan actually poses. "Can this room be drawn as two
rectangles without a visible lie?" is a tolerance question, not an exactness one.

Also reported, from the corrected morphology and labelled with the size it
really is: k after opening+closing at 500 mm, which is the grid's own resolution
limit -- nothing narrower than a cell is representable whatever any of this says.

Run: python experiments/room-rectangles/k_tolerance.py [n_dwellings]
"""
from __future__ import annotations

import hashlib
import json
import math
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from shapely import from_wkt
from shapely.affinity import rotate

HERE = Path(__file__).resolve().parent
RECT = HERE.parents[0] / "rectangularise"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RECT))

from fit_rects import max_rect_in_mask  # noqa: E402
from measure_swiss import (  # noqa: E402
    BAND, COLS, GEOM, MD5_EMPTY, MIN_ROOM_AREA, NOT_A_ROOM, _poly, dwelling_frame,
)
from morphology import clean, selftest  # noqa: E402
from rectilinear_k import GRID, guillotine_k, rasterise  # noqa: E402
from why_k import offaxis_fraction  # noqa: E402

OUT = HERE / "out"
OUT.mkdir(parents=True, exist_ok=True)
KMAX = 3
TOL = 0.98
CLEAN_CELLS = 2                     # 500 mm, and this one really is 500 mm


def _area(r):
    return (r[2] - r[0]) * (r[3] - r[1])


def greedy_cover(m, k):
    """Cumulative area of the k largest inscribed rectangles, greedily.

    A lower bound on the optimum, so every coverage reported here is if
    anything pessimistic about what k rectangles can do.
    """
    rest = m.copy()
    out, tot = [], 0
    for _ in range(k):
        if not rest.any():
            break
        r = max_rect_in_mask(rest)
        if r is None:
            break
        tot += _area(r)
        rest[r[1]:r[3], r[0]:r[2]] = False
        out.append(tot)
    while len(out) < k:
        out.append(tot)
    return out


def best_two(m):
    """Greedy raced against every guillotine cut, as `why_k.best_two_cover`."""
    best = greedy_cover(m, 2)[1]
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
            best = max(best, _area(ra) + _area(rb))
    return best


def measure(m):
    total = int(m.sum())
    if total == 0:
        return None
    g = greedy_cover(m, KMAX)
    cov = [g[0] / total, max(g[1], best_two(m)) / total, g[2] / total]
    cov[2] = max(cov[2], cov[1])
    k_tol = next((i + 1 for i, c in enumerate(cov) if c >= TOL), KMAX + 1)
    return cov, k_tol


def main():
    n_target = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
    selftest()
    dw = defaultdict(list)
    for chunk in pd.read_csv(GEOM, usecols=COLS, chunksize=500_000, dtype=str):
        a = chunk[(chunk["entity_type"] == "area") &
                  (chunk["unit_usage"] == "RESIDENTIAL") &
                  (chunk["apartment_id"] != MD5_EMPTY)]
        a = a[~a["entity_subtype"].isin(NOT_A_ROOM)]
        for s, f, ap, stp, wkt in zip(a["site_id"], a["floor_id"],
                                      a["apartment_id"],
                                      a["entity_subtype"].fillna("<NA>"),
                                      a["geometry"]):
            dw[(s, f, ap)].append((stp, wkt))
    keys = sorted(dw.keys())
    keys.sort(key=lambda k: hashlib.md5("|".join(k).encode()).hexdigest())

    rows, done = [], 0
    for key in keys:
        if done >= n_target:
            break
        geoms, types = [], []
        for stp, wkt in dw[key]:
            g = _poly(from_wkt(wkt))
            if g is not None and g.area >= MIN_ROOM_AREA:
                geoms.append(g)
                types.append(stp)
        if not (BAND[0] <= len(geoms) <= BAND[1]):
            continue
        ang, cen = dwelling_frame(geoms)
        if ang is None:
            continue
        geoms = [rotate(g, -ang, origin=cen) for g in geoms]
        ok, buf = True, []
        for g, t in zip(geoms, types):
            x0, y0, x1, y1 = g.bounds
            nx = max(1, int(math.ceil((x1 - x0) / GRID)))
            ny = max(1, int(math.ceil((y1 - y0) / GRID)))
            if nx * ny > 12_000:
                ok = False
                break
            m = rasterise(g, x0, y0, nx, ny)
            got = measure(m)
            if got is None:
                continue
            cov, ktol = got
            mc = clean(m, CLEAN_CELLS)
            kc = guillotine_k(mc) if mc.any() else None
            buf.append({
                "dwelling": done, "type": t, "area": g.area,
                "k_exact": guillotine_k(m) or 99,
                "k_clean500": kc or 99,
                "cov1": cov[0], "cov2": cov[1], "cov3": cov[2],
                "k_tol": ktol,
                "offaxis": offaxis_fraction(g),
            })
        if not ok:
            continue
        rows += buf
        done += 1
        if done % 200 == 0:
            print(f"  {done}", flush=True)

    (OUT / "k_tolerance.json").write_text(json.dumps(rows))
    report(rows, done)


def report(rows, ndw):
    n = len(rows)
    print(f"\ndwellings {ndw}, rooms {n}, tolerance {TOL:.2f}\n")

    print("=" * 92)
    print(f"1. SMALLEST k REACHING {TOL:.0%} COVERAGE, BY TYPE")
    print("=" * 92)
    print(f"{'type':<16}{'n':>6}{'k_tol=1':>9}{'k_tol<=2':>10}{'k_tol<=3':>10}"
          f"{'exact k=1':>11}{'clean500 k=1':>14}{'cov2 median':>13}")
    by = defaultdict(list)
    for r in rows:
        by[r["type"]].append(r)
    order = sorted(by.items(), key=lambda kv: -len(kv[1]))
    for t, rs in order + [("ALL", rows)]:
        m = len(rs)
        if m < 50:
            continue
        print(f"{t:<16}{m:>6}"
              f"{sum(r['k_tol'] == 1 for r in rs) / m:>9.4f}"
              f"{sum(r['k_tol'] <= 2 for r in rs) / m:>10.4f}"
              f"{sum(r['k_tol'] <= 3 for r in rs) / m:>10.4f}"
              f"{sum(r['k_exact'] == 1 for r in rs) / m:>11.4f}"
              f"{sum(r['k_clean500'] == 1 for r in rs) / m:>14.4f}"
              f"{st.median(r['cov2'] for r in rs):>13.4f}")

    print()
    print("=" * 92)
    print("2. WHOLE DWELLINGS WITHIN k")
    print("=" * 92)
    dws = defaultdict(list)
    for r in rows:
        dws[r["dwelling"]].append(r)
    for lab, fn in (("k_tol", lambda r, c: r["k_tol"] <= c),
                    ("exact", lambda r, c: r["k_exact"] <= c),
                    ("clean500", lambda r, c: r["k_clean500"] <= c)):
        line = []
        for cap in (1, 2, 3):
            s = sum(all(fn(r, cap) for r in rs) for rs in dws.values())
            line.append(f"<= {cap}: {s / len(dws):.4f}")
        print(f"   {lab:<10}" + "   ".join(line))

    print()
    print("=" * 92)
    print("3. WHAT TWO RECTANGLES COVER")
    print("=" * 92)
    for lab, sel in (("all rooms", lambda r: True),
                     ("exact k >= 3", lambda r: r["k_exact"] >= 3),
                     ("k_tol >= 3", lambda r: r["k_tol"] >= 3)):
        v = sorted(r["cov2"] for r in rows if sel(r))
        if not v:
            continue
        p = lambda q: v[max(0, min(len(v) - 1, int(q * len(v))))]  # noqa: E731
        print(f"   {lab:<14} n={len(v):>6}  median {st.median(v):.4f}"
              f"  p25 {p(0.25):.4f}  p5 {p(0.05):.4f}"
              f"  >=0.95 {sum(x >= 0.95 for x in v) / len(v):.4f}")

    print()
    print("=" * 92)
    print("4. WHAT IS LEFT AT k_tol >= 3 -- SHAPE, OR AN OFF-AXIS WALL?")
    print("=" * 92)
    for lo, hi, lab in ((1, 1, "k_tol = 1"), (2, 2, "k_tol = 2"),
                        (3, 99, "k_tol >= 3")):
        rs = [r for r in rows if lo <= r["k_tol"] <= hi]
        if not rs:
            continue
        print(f"   {lab:<12} n={len(rs):>6}  off-axis >10% of perimeter: "
              f"{sum(r['offaxis'] > 0.10 for r in rs) / len(rs):.4f}")


if __name__ == "__main__":
    main()
