"""How many rectangles does a real room actually need?

The whole engine places ONE rectangle per Room. That premise came from the solver
formulation and every downstream ticket inherited it; nobody measured what it
costs, because the alternative got filed under the map's *Non-orthogonal
geometry* fog -- which is a category error. An L-shaped room is orthogonal. It is
a union of two axis-aligned rectangles, and CP-SAT places two rectangles exactly
as happily as one.

So: for each real room, what is the smallest k such that the room is a union of k
axis-aligned rectangles? k = 1 is the current model. k = 2 is an L. k = 3 is a T,
U, S or Z.

Decomposition is GUILLOTINE -- recursively cut on a full-width or full-height
line -- so the k reported is an UPPER BOUND on the true minimum partition. Every
shape that needs a non-guillotine partition (a pinwheel) is counted as worse than
it is, which biases the answer against the case being made here.

Measured in the dwelling's own frame at the 250 mm solve grid, so k is what the
SOLVER would need, not what the polygon happens to store.

Run: python experiments/rectangularise/rectilinear_k.py [n_dwellings]
"""
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from shapely import contains_xy, from_wkt
from shapely.affinity import rotate

sys.path.insert(0, str(Path(__file__).resolve().parent))
from measure_swiss import (  # noqa: E402
    BAND, COLS, GEOM, MD5_EMPTY, MIN_ROOM_AREA, NOT_A_ROOM, _poly, dwelling_frame,
)

OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)
GRID = 0.25
KMAX = 4


def rasterise(g, x0, y0, nx, ny):
    cx = x0 + (np.arange(nx) + 0.5) * GRID
    cy = y0 + (np.arange(ny) + 0.5) * GRID
    gx, gy = np.meshgrid(cx, cy)
    return contains_xy(g, gx.ravel(), gy.ravel()).reshape(ny, nx)


def is_rect(m):
    ys, xs = np.nonzero(m)
    if len(ys) == 0:
        return False
    return bool(m[ys.min():ys.max() + 1, xs.min():xs.max() + 1].all()) and \
        int(m.sum()) == (ys.max() - ys.min() + 1) * (xs.max() - xs.min() + 1)


_MEMO = {}


def guillotine_k(m, budget=KMAX):
    """Smallest k <= budget with a guillotine partition into k rectangles.

    Memoised on the trimmed sub-mask: real rooms repeat the same small shapes
    constantly, and without the cache the recursion is exponential in the cut
    positions -- measured, it does not finish.
    """
    ys, xs = np.nonzero(m)
    if len(ys) == 0:
        return 0
    sub = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    key = (sub.shape, sub.tobytes(), budget)
    hit = _MEMO.get(key)
    if hit is not None:
        return hit[0]

    if is_rect(sub):
        _MEMO[key] = (1,)
        return 1
    if budget <= 1:
        _MEMO[key] = (None,)
        return None

    h, w = sub.shape
    best = None
    lim = budget
    for axis in (0, 1):
        n = w if axis == 0 else h
        for c in range(1, n):
            a = sub[:, :c] if axis == 0 else sub[:c, :]
            b = sub[:, c:] if axis == 0 else sub[c:, :]
            if not a.any() or not b.any():
                continue
            ka = guillotine_k(a, lim - 1)
            if ka is None:
                continue
            kb = guillotine_k(b, lim - ka)
            if kb is None:
                continue
            t = ka + kb
            if best is None or t < best:
                best, lim = t, min(lim, t)
                if best == 2:
                    break
        if best == 2:
            break
    _MEMO[key] = (best,)
    return best


def main():
    n_target = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
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

    per_room = Counter()
    by_type = defaultdict(Counter)
    per_dwelling_max = Counter()
    done = 0
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
        worst = 0
        ok = True
        for g, t in zip(geoms, types):
            x0, y0, x1, y1 = g.bounds
            nx = max(1, int(math.ceil((x1 - x0) / GRID)))
            ny = max(1, int(math.ceil((y1 - y0) / GRID)))
            if nx * ny > 20_000:
                ok = False
                break
            kk = guillotine_k(rasterise(g, x0, y0, nx, ny))
            lab = str(kk) if kk else "0"
            if kk is None:
                lab = f">{KMAX}"
                kk = KMAX + 1
            per_room[lab] += 1
            by_type[t][lab] += 1
            worst = max(worst, kk)
        if not ok:
            continue
        per_dwelling_max[min(worst, KMAX + 1)] += 1
        done += 1
        if done % 250 == 0:
            print(f"  {done}", flush=True)

    n = sum(per_room.values())
    print(f"\ndwellings {done}, rooms {n}\n")
    print("=" * 70)
    print("RECTANGLES NEEDED PER ROOM  (guillotine, so an upper bound)")
    print("=" * 70)
    order = [str(i) for i in range(1, KMAX + 1)] + [f">{KMAX}"]
    cum = 0
    for lab in order:
        c = per_room.get(lab, 0)
        if not c:
            continue
        cum += c
        print(f"  k = {lab:<3} {c:>7}  {c / n:.4f}   cumulative {cum / n:.4f}")

    print("\n" + "=" * 70)
    print("BY ROOM TYPE — share needing at most k")
    print("=" * 70)
    print(f"{'type':<18} {'n':>7} {'k=1':>8} {'<=2':>8} {'<=3':>8}")
    for t, c in sorted(by_type.items(), key=lambda kv: -sum(kv[1].values())):
        tot = sum(c.values())
        if tot < 500:
            continue
        k1 = c.get("1", 0) / tot
        k2 = (c.get("1", 0) + c.get("2", 0)) / tot
        k3 = k2 + c.get("3", 0) / tot
        print(f"{t:<18} {tot:>7} {k1:>8.4f} {k2:>8.4f} {k3:>8.4f}")

    print("\n" + "=" * 70)
    print("PER DWELLING — every room within k rectangles")
    print("=" * 70)
    tot = sum(per_dwelling_max.values())
    cum = 0
    for i in range(1, KMAX + 2):
        c = per_dwelling_max.get(i, 0)
        cum += c
        lab = str(i) if i <= KMAX else f">{KMAX}"
        print(f"  all rooms k <= {lab:<3} {cum:>7}  {cum / tot:.4f}")

    json.dump({"per_room": dict(per_room),
               "by_type": {k: dict(v) for k, v in by_type.items()},
               "per_dwelling_max": {str(k): v for k, v in per_dwelling_max.items()}},
              open(OUT / "rectilinear_k.json", "w"))


if __name__ == "__main__":
    main()
