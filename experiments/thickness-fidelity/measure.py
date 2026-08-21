"""Ticket 33 — classify every Swiss Dwellings wall as internal-to-a-dwelling or
not, and measure the two numbers our `t_int` is supposed to stand for.

The prior on the map (*Which region profiles ship in v1*,
`experiments/corpus-smoke/wall_thickness_swiss.py`) censused the minor side of
the minimum rotated rectangle over **all** `separator/WALL` polygons — exterior,
party and partition together — and reported p25 109 / p50 169 / p75 267. This
script does not re-run that. It asks the question the profile actually poses:
**what does a wall that separates two rooms of the same dwelling measure**, and
**how far apart are the two Space polygons it separates**.

Two numbers per station, because ADR 0010 made them different questions:

  `t_mrr`  minor side of the wall polygon's minimum rotated rectangle — what the
           surveyor drew as the wall body.
  `gap`    perpendicular distance from the wall's centreline to room A plus the
           same to room B — the **face-to-face separation of two Spaces**, which
           is by construction the plane ADR 0010 puts our `t_int` total on, and
           the arithmetic ticket 33 and ticket 27 were handed.

Method, per dwelling `(floor_id, apartment_id)`:

  1. take that dwelling's room polygons (corpus rooms are CLEAR polygons; no two
     ever touch — `experiments/rectangularise/probe_swiss.py`);
  2. take every WALL on the same floor, whatever its own `apartment_id`;
  3. keep walls that are genuine straight strips (`area / mrr.area >= 0.95`,
     the same gate the prior census used);
  4. probe K stations along each wall's centreline, casting perpendicular both
     ways;
  5. a station is INTERNAL when both sides land on *different rooms of this
     dwelling*, and BOUNDARY when only one side does. A wall is internal to the
     dwelling in proportion to its internal stations.

Repairs follow `experiments/rectangularise/measure_swiss.py`: `make_valid`, then
a 1 mm snap (ADR 0001's own resolution), each counted rather than swallowed.

Run:  python experiments/thickness-fidelity/measure.py [max_dwellings]
"""
from __future__ import annotations

import gzip
import json
import math
import pickle
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import shapely
from shapely import STRtree, from_wkt, make_valid, set_precision
from shapely.geometry import Point

OUT = Path(__file__).resolve().parent / "out"
CACHE = OUT / "cache.pkl.gz"

STATIONS = 7          # probe points per wall, spread over the middle 80 %
D_MAX = 0.60          # m; furthest a room may sit from a centreline and count
PERP_TOL = 0.30       # m; how far off perpendicular the nearest room point may sit
STRIP = 0.95          # area / mrr.area gate — same as the prior census
MIN_LEN = 0.30        # m; shorter walls are junction stubs, not walls
MIN_ROOM_AREA = 0.5   # m^2; below this an `area` polygon is an annotation fragment
CLOSE = 0.35          # m; morphological closing radius — bridges gaps up to 700 mm
CLOSE_RADII = (0.25, 0.35, 0.50)   # sensitivity band for the same closing

REPAIRS: Counter[str] = Counter()


def _poly(g):
    if g is None or g.is_empty:
        return None
    if not g.is_valid:
        REPAIRS["invalid"] += 1
        g = make_valid(g)
    if g.geom_type in ("GeometryCollection", "MultiPolygon"):
        parts = [p for p in g.geoms if p.geom_type == "Polygon" and not p.is_empty]
        if not parts:
            return None
        g = max(parts, key=lambda p: p.area)
    return g if g.geom_type == "Polygon" and not g.is_empty else None


def mrr_axes(p):
    """(thickness_m, length_m, centre, unit_along, unit_normal) or None."""
    mrr = p.minimum_rotated_rectangle
    if mrr is None or mrr.is_empty or mrr.geom_type != "Polygon" or mrr.area <= 0:
        return None
    if p.area / mrr.area < STRIP:
        return None
    c = list(mrr.exterior.coords)[:4]
    e1 = (c[1][0] - c[0][0], c[1][1] - c[0][1])
    e2 = (c[2][0] - c[1][0], c[2][1] - c[1][1])
    l1 = math.hypot(*e1)
    l2 = math.hypot(*e2)
    if min(l1, l2) <= 1e-9:
        return None
    if l1 >= l2:
        length, thick, along = l1, l2, e1
    else:
        length, thick, along = l2, l1, e2
    u = (along[0] / length, along[1] / length)
    n = (-u[1], u[0])
    cx = sum(x for x, _ in c) / 4.0
    cy = sum(y for _, y in c) / 4.0
    return thick, length, (cx, cy), u, n


def measure_dwelling(room_recs, wall_polys, other_recs=()):
    """Return (rooms, internal_walls, boundary_walls) for one dwelling."""
    rooms, rtypes = [], []
    for st, wkt in room_recs:
        p = _poly(from_wkt(wkt))
        if p is None or p.area < MIN_ROOM_AREA:
            continue
        rooms.append(p)
        rtypes.append(st)
    if len(rooms) < 2:
        return None
    others = [q for q in (_poly(from_wkt(w)) for _, w in other_recs)
              if q is not None and q.area >= MIN_ROOM_AREA]
    tree = STRtree(rooms)

    internal, boundary = [], []
    for wp in wall_polys:
        ax = mrr_axes(wp)
        if ax is None:
            continue
        thick, length, (cx, cy), u, n = ax
        if length < MIN_LEN:
            continue

        n_int = n_bnd = n_void = 0
        gaps, dplus, dminus, pairs, excess = [], [], [], [], []
        for k in range(STATIONS):
            f = 0.10 + 0.80 * (k / max(1, STATIONS - 1))
            s = (k / max(1, STATIONS - 1) - 0.5) * length * 0.80
            px, py = cx + u[0] * s, cy + u[1] * s
            P = Point(px, py)

            side = {1: None, -1: None}
            cand = tree.query(shapely.buffer(P, D_MAX))
            for i in cand:
                r = rooms[i]
                ln = shapely.shortest_line(r, P)
                if ln is None or ln.is_empty:
                    continue
                (qx, qy), _ = list(ln.coords)[0], None
                dx, dy = qx - px, qy - py
                d = math.hypot(dx, dy)
                if d > D_MAX or d < 1e-9:
                    continue
                if abs(dx * u[0] + dy * u[1]) > PERP_TOL:
                    continue                      # nearest point is off to the side
                sgn = 1 if (dx * n[0] + dy * n[1]) >= 0 else -1
                if side[sgn] is None or d < side[sgn][1]:
                    side[sgn] = (i, d)

            a, b = side[1], side[-1]
            if a is not None and b is not None and a[0] != b[0]:
                n_int += 1
                gaps.append(a[1] + b[1])
                dplus.append(a[1])
                dminus.append(b[1])
                pairs.append((a[0], b[0]))
                excess.append(round((a[1] + b[1] - thick) * 1000, 1))
            elif a is not None or b is not None:
                n_bnd += 1
            else:
                n_void += 1

        rec = {
            "t_mrr": round(thick * 1000, 1),
            "len": round(length, 4),
            "n_int": n_int, "n_bnd": n_bnd, "n_void": n_void,
        }
        if n_int:
            rec["gap"] = round(float(np.median(gaps)) * 1000, 1)
            rec["gap_lo"] = round(float(np.min(gaps)) * 1000, 1)
            rec["gap_hi"] = round(float(np.max(gaps)) * 1000, 1)
            rec["d_asym"] = round(abs(float(np.median(dplus)) -
                                      float(np.median(dminus))) * 1000, 1)
            rec["len_int"] = round(length * n_int / STATIONS, 4)
            rec["excess"] = excess          # per-station (gap - t_mrr), mm
            rec["gaps"] = [round(g * 1000, 1) for g in gaps]
            rec["pairs"] = sorted({tuple(sorted(int(x) for x in p)) for p in pairs})
            internal.append(rec)
        elif n_bnd:
            rec["len_bnd"] = round(length * n_bnd / STATIONS, 4)
            boundary.append(rec)

    # Independent, AREA-based estimate of the same internal-partition footprint,
    # so the wall-by-wall figure has something to be checked against. A
    # morphological closing at CLOSE m bridges every internal gap up to 2*CLOSE
    # wide without pushing the dwelling's outer boundary out, and the closing
    # minus the rooms IS the material between them.
    # Anything the apartment holds that is not a room -- shafts, stairs,
    # balconies -- is subtracted, or the closing would count it as partition.
    fill = {}
    closed_area = None
    try:
        u = shapely.union_all(rooms)
        blank = shapely.union_all(others) if others else None
        for r in CLOSE_RADII:
            closed = shapely.buffer(shapely.buffer(u, r, join_style="mitre"),
                                    -r, join_style="mitre")
            gapland = shapely.difference(closed, u)
            if blank is not None:
                gapland = shapely.difference(gapland, blank)
            fill[f"{r:g}"] = round(float(shapely.area(gapland)), 4)
            if r == CLOSE:
                closed_area = round(float(shapely.area(closed)), 4)
    except Exception:
        REPAIRS["closing"] += 1
    fill_area = fill.get(f"{CLOSE:g}")

    return {
        "n_rooms": len(rooms),
        "types": rtypes,
        "room_area": [round(r.area, 4) for r in rooms],
        "sum_area": round(sum(r.area for r in rooms), 4),
        "fill_area": fill_area,
        "fill_by_r": fill,
        "closed_area": closed_area,
        "n_other": len(others),
        "internal": internal,
        "boundary": boundary,
    }


def main() -> None:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    with gzip.open(CACHE, "rb") as fh:
        cache = pickle.load(fh)
    rooms_by_dw = cache["rooms"]
    other_by_dw = cache.get("other", {})
    walls_by_floor = cache["walls"]
    print(f"dwellings in cache: {len(rooms_by_dw):,}  stride {cache['stride']}")

    keys = sorted(rooms_by_dw)
    if limit:
        keys = keys[:limit]

    wall_cache: dict[str, list] = {}
    out, t0, skipped = [], time.time(), 0
    for i, key in enumerate(keys, 1):
        floor, apt = key.split("|", 1)
        if floor not in wall_cache:
            ws = []
            for wkt in walls_by_floor.get(floor, []):
                p = _poly(from_wkt(wkt))
                if p is not None:
                    ws.append(p)
            wall_cache = {floor: ws}          # floors are contiguous in `keys`
        try:
            rec = measure_dwelling(rooms_by_dw[key], wall_cache[floor],
                                   other_by_dw.get(key, ()))
        except Exception:
            REPAIRS["dropped"] += 1
            rec = None
        if rec is None:
            skipped += 1
        else:
            rec["k"] = key
            out.append(rec)
        if i % 1000 == 0:
            print(f"  {i:>6,}/{len(keys):,}  {time.time() - t0:6.0f}s  "
                  f"kept {len(out):,}", flush=True)

    print(f"\ndwellings measured: {len(out):,}   skipped: {skipped:,}")
    print(f"repairs: {dict(REPAIRS)}")
    dest = OUT / "walls.json.gz"
    with gzip.open(dest, "wt", encoding="utf-8") as fh:
        json.dump({"stride": cache["stride"], "repairs": dict(REPAIRS),
                   "stations": STATIONS, "dwellings": out}, fh)
    print(f"wrote {dest}  ({dest.stat().st_size / 1e6:.0f} MB)")


if __name__ == "__main__":
    main()
