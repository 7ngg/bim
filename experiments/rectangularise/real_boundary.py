"""Is a real dwelling's boundary representable as an Envelope at all?

Ticket 58. Every Envelope the solver has ever been handed is parametric -- a
bounding box minus at most two notch rectangles, sized from a formula. ADR 0029
fitted the second family to real dwellings on **area, perimeter and bbox
occupancy**, which are three moments; a fitted summary is not a boundary. Before
a real-boundary arm can be built, two things have to be known, and neither is
measured anywhere on this map:

  1. **How many rectangles a real outline needs.** `Envelope.parts` is a disjoint
     rectangular decomposition of the interior, and `scenarios.ground_truth`
     gives every part at least one room -- so a dwelling whose outline needs more
     rectangles than it has rooms cannot be a fixture at any budget. This
     computes the EXACT minimum by the Lipski/Ohtsuki theorem (min rectangles =
     reflex - independent chords - holes + 1), not a greedy upper bound.

  2. **Whether those parts can hold rooms.** `_guillotine` dissects each part and
     every leaf must clear `_leaf_ok` -- 1.0 m per side, 3.0 m2, aspect 4. A
     minimum partition is free to emit slivers, so the count alone does not say
     the fixture is buildable.

The boundary itself is not re-derived: it is `keep_largest_component(watershed(
geoms)) >= 0`, the same 250 mm cell mask `envelope_approx` measures ADR 0003's
notch loss against, so every number here is comparable with `notches_all` and
`envelope_loss_by_k` in the same fit record rather than merely similar to it.

Reads `out/swiss_fit_k2.json` and the cached `out/swiss_dw.pkl`; writes
`out/real_boundary.log` and the per-dwelling series `series/real_boundary.json.gz`.
Costs ~0.4 s/dwelling (the watershed), so it samples rather than scanning.

Run: ../../venv/Scripts/python.exe real_boundary.py [n]
"""
import gzip
import json
import pickle
import statistics as st
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

import numpy as np
from shapely import from_wkt
from shapely.affinity import rotate
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fit_rects import (BAND, MIN_ROOM_AREA, _poly, dwelling_frame,  # noqa: E402
                       keep_largest_component, max_rect_in_mask, watershed)

OUT = Path(__file__).resolve().parent / "out"
SERIES = Path(__file__).resolve().parent / "series"

# `scenarios._leaf_ok`, verbatim, in 250 mm cells. A part of the Envelope that
# fails these cannot receive a room, and `ground_truth` gives every part one.
MIN_SIDE = 4          # 1.0 m
MIN_PIECE_AREA = 48   # 3.0 m2
MAX_ASPECT = 4


def frame_geoms(items):
    """One dwelling's rooms, rotated into its own frame -- `fit_rects`' step."""
    geoms = []
    for _st, wkt in items:
        g = _poly(from_wkt(wkt))
        if g is not None and g.area >= MIN_ROOM_AREA:
            geoms.append(g)
    if not (BAND[0] <= len(geoms) <= BAND[1]):
        return None
    ang, cen = dwelling_frame(geoms)
    if ang is None:
        return None
    return [rotate(g, -ang, origin=cen) for g in geoms]


def crop(mask):
    """Trim to the bounding box, so lattice indices are the Envelope's own."""
    ys, xs = np.nonzero(mask)
    return mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def corners(mask):
    """Reflex and convex lattice vertices of the cell mask's boundary.

    At a lattice point, look at the four cells that meet there. One inside is a
    convex corner, three inside is a reflex corner, two diagonal is a pinch --
    a point where the region touches itself. A pinch is counted separately: it
    is not a chord endpoint and it is why a raster boundary is not always a
    simple polygon.
    """
    ny, nx = mask.shape
    pad = np.zeros((ny + 2, nx + 2), dtype=bool)
    pad[1:-1, 1:-1] = mask
    reflex, convex, pinch = [], [], 0
    for y in range(ny + 1):
        for x in range(nx + 1):
            q = (int(pad[y, x]) + int(pad[y, x + 1])
                 + int(pad[y + 1, x]) + int(pad[y + 1, x + 1]))
            if q == 1:
                convex.append((y, x))
            elif q == 3:
                reflex.append((y, x))
            elif q == 2 and (pad[y, x] == pad[y + 1, x + 1]) \
                    and (pad[y, x] != pad[y, x + 1]):
                pinch += 1
    return reflex, convex, pinch


def holes(mask):
    """Complement components enclosed by the region -- ticket 53's void, here as
    a topological fact about the outline rather than as unassigned floor."""
    ny, nx = mask.shape
    pad = np.zeros((ny + 2, nx + 2), dtype=bool)
    pad[1:-1, 1:-1] = mask
    free = ~pad
    seen = np.zeros_like(free)
    q = deque([(0, 0)])
    seen[0, 0] = True
    while q:                                   # flood the outside
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < ny + 2 and 0 <= xx < nx + 2 and free[yy, xx] \
                    and not seen[yy, xx]:
                seen[yy, xx] = True
                q.append((yy, xx))
    inner = free & ~seen
    n = 0
    seen2 = np.zeros_like(inner)
    for sy in range(ny + 2):
        for sx in range(nx + 2):
            if not inner[sy, sx] or seen2[sy, sx]:
                continue
            n += 1
            q = deque([(sy, sx)])
            seen2[sy, sx] = True
            while q:
                y, x = q.popleft()
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < ny + 2 and 0 <= xx < nx + 2 and inner[yy, xx] \
                            and not seen2[yy, xx]:
                        seen2[yy, xx] = True
                        q.append((yy, xx))
    return n


def _inside_segment(mask, p, q, horizontal):
    """Does the open segment between two lattice points lie inside the region?

    A chord runs along a lattice line; it is interior iff the cells on BOTH
    sides of every unit step it crosses are inside the mask.
    """
    ny, nx = mask.shape

    def cell(y, x):
        return 0 <= y < ny and 0 <= x < nx and mask[y, x]

    if horizontal:
        y = p[0]
        for x in range(min(p[1], q[1]), max(p[1], q[1])):
            if not (cell(y - 1, x) and cell(y, x)):
                return False
    else:
        x = p[1]
        for y in range(min(p[0], q[0]), max(p[0], q[0])):
            if not (cell(y, x - 1) and cell(y, x)):
                return False
    return True


def chords(mask, reflex):
    """Interior chords joining two reflex vertices, split by orientation."""
    by_row, by_col = defaultdict(list), defaultdict(list)
    for (y, x) in reflex:
        by_row[y].append(x)
        by_col[x].append(y)
    hor, ver = [], []
    for y, xs in by_row.items():
        xs.sort()
        for a, b in zip(xs, xs[1:]):
            if _inside_segment(mask, (y, a), (y, b), True):
                hor.append((y, a, b))
    for x, ys in by_col.items():
        ys.sort()
        for a, b in zip(ys, ys[1:]):
            if _inside_segment(mask, (a, x), (b, x), False):
                ver.append((x, a, b))
    return hor, ver


def _hopcroft(adj, nl, nr):
    """Maximum bipartite matching, Hungarian augmenting paths. Small graphs."""
    matchR = [-1] * nr
    res = 0
    for u in range(nl):
        seen = [False] * nr
        stack = [(u, iter(adj[u]))]
        # iterative DFS so a pathological dwelling cannot blow the stack
        path = []
        while stack:
            node, it = stack[-1]
            advanced = False
            for v in it:
                if seen[v]:
                    continue
                seen[v] = True
                path.append((node, v))
                if matchR[v] == -1:
                    for (a, b) in path:
                        matchR[b] = a
                    res += 1
                    stack.clear()
                    advanced = True
                    break
                stack.append((matchR[v], iter(adj[matchR[v]])))
                advanced = True
                break
            if not stack:
                break
            if not advanced:
                stack.pop()
                if path:
                    path.pop()
    return res


def min_rectangles(mask):
    """Exact minimum rectangle partition: reflex - independent chords - holes + 1.

    Lipski et al. / Ohtsuki. The maximum set of pairwise non-crossing chords is
    the maximum independent set of the chord intersection graph, which is
    bipartite (horizontal against vertical), so Koenig gives it as
    |H| + |V| - maximum matching.
    """
    reflex, _convex, pinch = corners(mask)
    h = holes(mask)
    hor, ver = chords(mask, reflex)
    adj = [[] for _ in hor]
    for i, (y, x1, x2) in enumerate(hor):
        for j, (x, y1, y2) in enumerate(ver):
            if x1 <= x <= x2 and y1 <= y <= y2:
                adj[i].append(j)
    m = _hopcroft(adj, len(hor), len(ver))
    indep = len(hor) + len(ver) - m
    return max(1, len(reflex) - indep - h + 1), {
        "reflex": len(reflex), "chords_h": len(hor), "chords_v": len(ver),
        "indep": indep, "holes": h, "pinch": pinch,
    }


def greedy_parts(mask, cap=400):
    """Largest-inscribed-rectangle partition -- an UPPER bound on the part count.

    Greedy LIR takes the fattest rectangle first and leaves the residue in thin
    pieces, so its per-part dimensions are a PESSIMISTIC witness: they say a
    room-sized partition was not found this way, never that none exists. Read it
    beside `slab_parts`, which fails the other way.
    """
    m = mask.copy()
    out = []
    while m.any() and len(out) < cap:
        r = max_rect_in_mask(m)
        if r is None:
            break
        x1, y1, x2, y2 = r
        out.append((x2 - x1, y2 - y1, (x2 - x1) * (y2 - y1)))
        m[y1:y2, x1:x2] = False
    return out


def slab_parts(mask):
    """Full-height column partition: cut at every x where the column changes.

    This is `envelope_fit.build`'s own shape -- it makes parts full-height
    columns wherever it can, for exactly the reason `ground_truth` needs -- so it
    is the fair heuristic to hold the real boundary to. It over-counts where a
    dwelling is articulated on the horizontal axis and under-counts nothing.
    """
    ny, nx = mask.shape
    out = []
    x = 0
    while x < nx:
        col = mask[:, x]
        x2 = x + 1
        while x2 < nx and np.array_equal(mask[:, x2], col):
            x2 += 1
        # each maximal run of rows in this column block is one rectangle
        y = 0
        while y < ny:
            if not col[y]:
                y += 1
                continue
            y2 = y
            while y2 < ny and col[y2]:
                y2 += 1
            out.append((x2 - x, y2 - y, (x2 - x) * (y2 - y)))
            y = y2
        x = x2
    return out


def leaf_ok(w, h, a):
    return (w >= MIN_SIDE and h >= MIN_SIDE and a >= MIN_PIECE_AREA
            and w <= MAX_ASPECT * h and h <= MAX_ASPECT * w)


def pct(xs, p):
    return float(np.percentile(xs, p)) if xs else float("nan")


def main():
    n_target = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    recs = [r for r in json.load(open(OUT / "swiss_fit_k2.json"))
            if r.get("envelope_loss_by_k")]
    dw, _keys = pickle.load(open(OUT / "swiss_dw.pkl", "rb"))
    print(f"fit records: {len(recs)}; sampling the first {n_target} in fit order",
          flush=True)

    rows = []
    for r in recs:
        if len(rows) >= n_target:
            break
        items = dw.get(tuple(r["k"].split("|")))
        if items is None:
            continue
        geoms = frame_geoms(items)
        if geoms is None:
            continue
        lab, _x0, _y0 = watershed(geoms)
        if lab is None:
            continue
        mask = crop(keep_largest_component(lab) >= 0)
        if mask.sum() < 16:
            continue
        k, info = min_rectangles(mask)
        parts = greedy_parts(mask)
        slabs = slab_parts(mask)
        rows.append({
            "k": r["k"], "n": len(geoms), "status": r["status"],
            "cells": int(mask.sum()),
            "bbox": [int(mask.shape[1]), int(mask.shape[0])],
            "min_rects": k,
            "greedy_rects": len(parts),
            "greedy_bad": sum(1 for p in parts if not leaf_ok(*p)),
            "greedy_min_side": min((min(p[0], p[1]) for p in parts), default=0),
            "slab_rects": len(slabs),
            "slab_bad": sum(1 for p in slabs if not leaf_ok(*p)),
            "slab_narrow": sum(1 for p in slabs if min(p[0], p[1]) < 11),
            "notches_all": r.get("notches_all"),
            "loss2": r["envelope_loss_by_k"]["2"],
            **info,
        })
        if len(rows) % 50 == 0:
            print(f"  {len(rows)}", flush=True)

    SERIES.mkdir(exist_ok=True)
    with gzip.open(SERIES / "real_boundary.json.gz", "wt", encoding="utf-8") as fh:
        json.dump(rows, fh)

    n = len(rows)
    print(f"\ndwellings measured: {n}")
    print("=" * 74)
    print("1. HOW MANY RECTANGLES A REAL OUTLINE NEEDS (exact minimum)")
    print("=" * 74)
    mr = [r["min_rects"] for r in rows]
    print(f"   min rectangles: p25 {pct(mr,25):.0f}  median {st.median(mr):.0f}  "
          f"p75 {pct(mr,75):.0f}  p90 {pct(mr,90):.0f}  max {max(mr)}")
    print(f"   share expressible as bbox minus <=2 notch RECTANGLES "
          f"(min_rects <= 3): {sum(x <= 3 for x in mr)/n:.4f}")
    for cut in (1, 2, 3, 4, 6, 8, 12):
        print(f"   min_rects <= {cut:>2}: {sum(x <= cut for x in mr)/n:.4f}")

    print("\n" + "=" * 74)
    print("2. THE `ground_truth` GATE: every part of the Envelope gets a room")
    print("=" * 74)
    ok = [r for r in rows if r["min_rects"] <= r["n"]]
    print(f"   min_rects <= n_rooms: {len(ok)/n:.4f}   "
          f"({n - len(ok)} dwellings need more rectangles than they have rooms)")
    for lo, hi in ((3, 5), (6, 7), (8, 9), (10, 12), (13, 20)):
        g = [r for r in rows if lo <= r["n"] <= hi]
        if g:
            print(f"   n_rooms {lo}-{hi}  n={len(g):>4}  "
                  f"median min_rects {st.median([r['min_rects'] for r in g]):.0f}  "
                  f"share min_rects <= n: "
                  f"{sum(r['min_rects'] <= r['n'] for r in g)/len(g):.4f}")

    print("\n" + "=" * 74)
    print("3. CAN THE PARTS HOLD ROOMS? (greedy partition, an UPPER bound)")
    print("=" * 74)
    print("   Two heuristics that fail in opposite directions. Neither proves a")
    print("   room-sized partition impossible; both agreeing is the finding.")
    for tag in ("greedy", "slab"):
        v = [r[f"{tag}_rects"] for r in rows]
        print(f"\n   {tag}: rectangles median {st.median(v):.0f}  "
              f"p90 {pct(v,90):.0f}   ratio to minimum median "
              f"{st.median([r[f'{tag}_rects']/r['min_rects'] for r in rows]):.2f}")
        print(f"   {tag}: dwellings with EVERY part clearing `_leaf_ok` "
              f"(1.0 m / 3.0 m2 / aspect 4): "
              f"{sum(r[f'{tag}_bad'] == 0 for r in rows)/n:.4f}")
        print(f"   {tag}: median share of parts failing it: "
              f"{st.median([r[f'{tag}_bad']/r[f'{tag}_rects'] for r in rows]):.4f}")
    print(f"\n   slab: dwellings with every part >= 2.75 m on its short side "
          f"(`envelope_fit.MIN_COL`, the habitable floor): "
          f"{sum(r['slab_narrow'] == 0 for r in rows)/n:.4f}")

    print("\n" + "=" * 74)
    print("4. WHAT THE OUTLINE IS MADE OF")
    print("=" * 74)
    print(f"   reflex vertices: median {st.median([r['reflex'] for r in rows]):.0f}"
          f"  p90 {pct([r['reflex'] for r in rows],90):.0f}")
    print(f"   enclosed holes: {Counter(r['holes'] for r in rows).most_common(5)}")
    print(f"   dwellings with a pinch point (boundary touches itself): "
          f"{sum(r['pinch'] > 0 for r in rows)/n:.4f}")

    print("\n" + "=" * 74)
    print("5. AGAINST WHAT ADR 0003 ALREADY MEASURES")
    print("=" * 74)
    print("   min_rects against the fit's own notch count:")
    for na in range(0, 6):
        g = [r for r in rows if r["notches_all"] == na]
        if g:
            print(f"   notches_all = {na}  n={len(g):>4}  "
                  f"median min_rects {st.median([r['min_rects'] for r in g]):.0f}"
                  f"  median loss2 {st.median([r['loss2'] for r in g]):.4f}")
    tail = [r for r in rows if r["loss2"] > 0.10]
    rest = [r for r in rows if r["loss2"] <= 0.10]
    for name, g in (("envelope-loss tail (>0.10)", tail), ("rest", rest)):
        if g:
            print(f"   {name}: n={len(g)}  median min_rects "
                  f"{st.median([r['min_rects'] for r in g]):.0f}  "
                  f"share min_rects <= n_rooms "
                  f"{sum(r['min_rects'] <= r['n'] for r in g)/len(g):.4f}")


if __name__ == "__main__":
    main()
