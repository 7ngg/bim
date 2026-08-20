"""Rectangularising real rooms - the measurement, on Swiss Dwellings.

Ticket 22. Four questions:
  1. what does each candidate conversion cost, per room (IoU, area error)?
  2. does the dwelling still tile / do rectangles collide?
  3. does the contact graph survive?
  4. where is the reject threshold, and how many dwellings does it drop?

Rooms in this corpus are CLEAR polygons (inner faces) separated by wall bodies --
no two room polygons touch, ever (probe_swiss.py: p50 nearest-neighbour gap 99 mm).
So adjacency is measured with a wall-width tolerance, never with touches().

Everything is measured in the dwelling's OWN frame: the corpus is geo-referenced,
so a raw axis-aligned bbox measures the site's north angle. Axis comes from the
minimum-area rotated rectangle of the union of the dwelling's rooms.

Run: python experiments/rectangularise/measure_swiss.py [n_lir]
"""
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from shapely import contains_xy, from_wkt, make_valid, set_precision
from shapely.affinity import rotate
from shapely.geometry import box
from shapely.ops import unary_union

# Real corpus polygons are not all valid. Every set operation below goes through
# these, and every repair is counted rather than swallowed.
REPAIRS = Counter()


def _poly(g):
    """Largest polygonal component of a possibly-invalid geometry."""
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


def _op(fn, *gs):
    """A set operation that survives a side-location conflict.

    GEOS raises on a small number of real dwellings; snapping to a 1 mm grid --
    the model's own resolution, per ADR 0001 -- clears every case seen.
    """
    def snap(x):
        if isinstance(x, list):
            return [set_precision(g, 0.001) for g in x if g is not None]
        return set_precision(x, 0.001)

    try:
        return fn(*gs)
    except Exception:
        REPAIRS["snapped"] += 1
        try:
            return fn(*[snap(g) for g in gs])
        except Exception:
            REPAIRS["dropped"] += 1
            return None


def _area(g):
    return g.area if g is not None else 0.0

ROOT = Path(__file__).resolve().parents[2]
GEOM = ROOT / "data" / "corpora" / "swiss-dwellings" / "swiss-dwellings-v3.0.0" / "geometries.csv"
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)

NOT_A_ROOM = {
    "SHAFT", "VOID", "OUTDOOR_VOID", "LIGHTWELL", "ELEVATOR", "STAIRCASE",
    "TECHNICAL_AREA", "BALCONY", "LOGGIA", "TERRACE", "GARDEN", "PATIO",
    "WINTERGARTEN",
}
MD5_EMPTY = "d41d8cd98f00b204e9800998ecf8427e"
COLS = ["apartment_id", "site_id", "floor_id", "unit_usage",
        "entity_type", "entity_subtype", "geometry"]

# C13: v1's Proposer serves 4-10 Brief-named rooms.
BAND = (4, 10)
TAU = 0.30           # wall-width tolerance for the contact graph, m
DOOR_CONTACT = 1.00  # contact run a door needs: ~900 structural + t_int (ADR 0001 c3)
RASTER = 0.05        # m per cell for the largest-inscribed-rectangle raster
MIN_ROOM_AREA = 0.5  # m^2; below this a polygon is an annotation fragment


# ---------------------------------------------------------------- conversions

def bbox_rect(g):
    return box(*g.bounds)


def lir_rect(g):
    """Largest inscribed AXIS-ALIGNED rectangle, by raster + max-rectangle-in-histogram."""
    x0, y0, x1, y1 = g.bounds
    nx = max(1, int(math.ceil((x1 - x0) / RASTER)))
    ny = max(1, int(math.ceil((y1 - y0) / RASTER)))
    if nx * ny > 400_000:
        return None
    xs = x0 + (np.arange(nx) + 0.5) * RASTER
    ys = y0 + (np.arange(ny) + 0.5) * RASTER
    gx, gy = np.meshgrid(xs, ys)
    inside = contains_xy(g, gx.ravel(), gy.ravel()).reshape(ny, nx)

    best = (0, 0, 0, 0, 0)  # area_cells, r0, c0, r1, c1
    heights = np.zeros(nx, dtype=np.int64)
    for i in range(ny):
        heights = np.where(inside[i], heights + 1, 0)
        stack = []
        for j in range(nx + 1):
            h = int(heights[j]) if j < nx else 0
            start = j
            while stack and stack[-1][1] >= h:
                s, sh = stack.pop()
                a = sh * (j - s)
                if a > best[0]:
                    best = (a, i - sh + 1, s, i, j - 1)
                start = s
            stack.append((start, h))
    if best[0] == 0:
        return None
    _, r0, c0, r1, c1 = best
    return box(x0 + c0 * RASTER, y0 + r0 * RASTER,
               x0 + (c1 + 1) * RASTER, y0 + (r1 + 1) * RASTER)


def area_preserving_rect(g):
    """bbox proportion, true area, anchored on the polygon centroid.

    Neither inflates nor deflates area -- the number per-room target-area
    conditioning consumes stays the room's real one.
    """
    x0, y0, x1, y1 = g.bounds
    w, h = x1 - x0, y1 - y0
    if w <= 0 or h <= 0:
        return None
    k = math.sqrt(g.area / (w * h))
    c = g.centroid
    return box(c.x - w * k / 2, c.y - h * k / 2, c.x + w * k / 2, c.y + h * k / 2)


CONVERSIONS = {"bbox": bbox_rect, "lir": lir_rect, "apr": area_preserving_rect}


# ---------------------------------------------------------------- contact graph

def relations(geoms):
    """Per-pair separation direction, the thing the solver actually reads.

    A pair is ASSERTED on an axis when some line separates the two entirely, and
    ABSTAINS otherwise. The test is a bounds test, so this is exactly what the
    Proposal transmits -- see CONTEXT.md, `Separation direction`.
    """
    b = [g.bounds for g in geoms]
    rel = {}
    for i in range(len(geoms)):
        for j in range(i + 1, len(geoms)):
            x = "L" if b[i][2] <= b[j][0] else "R" if b[j][2] <= b[i][0] else None
            y = "B" if b[i][3] <= b[j][1] else "A" if b[j][3] <= b[i][1] else None
            rel[(i, j)] = (x, y)
    return rel


def compare_relations(true_rel, conv_rel):
    """preserved / weakened (asserted -> abstain) / spurious / flipped (confident-wrong)."""
    out = Counter()
    for k, t in true_rel.items():
        c = conv_rel[k]
        for a in (0, 1):
            if t[a] == c[a]:
                out["same"] += 1
            elif t[a] is not None and c[a] is None:
                out["weakened"] += 1
            elif t[a] is None and c[a] is not None:
                out["spurious"] += 1
            else:
                out["flipped"] += 1
        if t == (None, None) and c != (None, None):
            out["pair_spurious"] += 1
        if t != (None, None) and c == (None, None):
            out["pair_weakened"] += 1
    return out


def contact_graph(geoms, tau=TAU, min_run=DOOR_CONTACT):
    """Pairs sharing a wall run of at least `min_run`.

    Both polygons are dilated by tau/2 (mitred) and intersected; the overlap
    area divided by tau approximates the shared run. Works identically on clear
    polygons separated by a wall and on rectangles that already touch.
    """
    fat = [_poly(g.buffer(tau / 2, join_style=2, mitre_limit=2.0)) for g in geoms]
    edges = set()
    for i in range(len(geoms)):
        if fat[i] is None:
            continue
        for j in range(i + 1, len(geoms)):
            if fat[j] is None or not fat[i].intersects(fat[j]):
                continue
            run = _area(_op(lambda a, b: a.intersection(b), fat[i], fat[j])) / tau
            if run >= min_run:
                edges.add((i, j))
    return edges


# ---------------------------------------------------------------- per dwelling

def dwelling_frame(geoms):
    """Rotation angle (deg) and origin putting this dwelling on its own axis."""
    u = _op(unary_union, geoms)
    if u is None or u.is_empty:
        return None, None
    mrr = u.minimum_rotated_rectangle
    if not hasattr(mrr, "exterior"):
        return None, None
    cc = np.asarray(mrr.exterior.coords)
    e = cc[1] - cc[0]
    return math.degrees(math.atan2(e[1], e[0])) % 90.0, u.centroid


def measure(key, items, do_lir):
    geoms, types = [], []
    for st, wkt in items:
        g = _poly(from_wkt(wkt))
        if g is None or g.area < MIN_ROOM_AREA:
            continue
        geoms.append(g)
        types.append(st)
    n = len(geoms)
    if not (BAND[0] <= n <= BAND[1]):
        return None

    ang, cen = dwelling_frame(geoms)
    if ang is None:
        return None
    geoms = [rotate(g, -ang, origin=cen) for g in geoms]

    # The dwelling's solve-domain stand-in: rooms grown by half a wall so the
    # corpus's clear polygons close into one connected region (ADR 0001, reversed).
    env = _op(unary_union, [_poly(g.buffer(TAU / 2, join_style=2, mitre_limit=2.0))
                            for g in geoms])
    if env is None or env.is_empty:
        return None
    env_bbox = box(*env.bounds)

    rec = {"k": key, "n": n, "types": types,
           "area": [g.area for g in geoms],
           "env_area": env.area, "env_bbox_area": env_bbox.area,
           "holes": sum(len(g.interiors) for g in geoms),
           "verts": [len(g.exterior.coords) - 1 for g in geoms]}

    # Graph2Plan's claim, on this corpus: is the bbox a lossless ENCODING of the
    # room once the envelope is known? (bbox n env, not bbox alone)
    rec["g2p_ratio"] = [
        (_area(_op(lambda a, b: a.intersection(b), bbox_rect(g), env)) / g.area
         if g.area > 0 else 0.0)
        for g in geoms
    ]

    true_edges = contact_graph(geoms)
    rec["edges_true"] = len(true_edges)
    true_rel = relations(geoms)
    rec["pairs"] = len(true_rel)
    rec["pairs_asserted"] = sum(1 for v in true_rel.values() if v != (None, None))

    for name, fn in CONVERSIONS.items():
        if name == "lir" and not do_lir:
            continue
        rects, ok = [], True
        for g in geoms:
            r = fn(g)
            if r is None or r.is_empty:
                ok = False
                break
            rects.append(r)
        if not ok:
            rec[name] = None
            continue
        iou, aerr = [], []
        for g, r in zip(geoms, rects):
            inter = _area(_op(lambda a, b: a.intersection(b), g, r))
            union = _area(_op(lambda a, b: a.union(b), g, r))
            iou.append(inter / union if union > 0 else 0.0)
            aerr.append((r.area - g.area) / g.area if g.area > 0 else 0.0)
        ov = 0.0
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                if rects[i].intersects(rects[j]):
                    ov += _area(_op(lambda a, b: a.intersection(b), rects[i], rects[j]))
        cov = _op(unary_union, rects)
        out = _area(_op(lambda a, b: a.difference(b), cov, env)) if cov is not None else 0.0
        e2 = contact_graph(rects)
        cmp = compare_relations(true_rel, relations(rects))
        rec[name] = {
            "rel": dict(cmp),
            "iou": iou, "aerr": aerr,
            "overlap": ov,
            "overlap_frac": ov / sum(g.area for g in geoms),
            "outside_env": out / cov.area if cov is not None and cov.area else 0.0,
            "edges": len(e2),
            "lost": len(true_edges - e2),
            "gained": len(e2 - true_edges),
        }
    return rec


# ---------------------------------------------------------------- driver

def main():
    n_lir = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    dw = defaultdict(list)
    for chunk in pd.read_csv(GEOM, usecols=COLS, chunksize=500_000, dtype=str):
        a = chunk[(chunk["entity_type"] == "area") &
                  (chunk["unit_usage"] == "RESIDENTIAL") &
                  (chunk["apartment_id"] != MD5_EMPTY)]
        a = a[~a["entity_subtype"].isin(NOT_A_ROOM)]
        for s, f, ap, st, wkt in zip(a["site_id"], a["floor_id"], a["apartment_id"],
                                     a["entity_subtype"].fillna("<NA>"), a["geometry"]):
            dw[(s, f, ap)].append((st, wkt))
    print(f"dwellings loaded: {len(dw)}", flush=True)

    # Deterministic sample order by key hash -- not the first N, which is one site.
    keys = sorted(dw.keys())
    keys.sort(key=lambda k: hashlib.md5("|".join(k).encode()).hexdigest())

    recs, skipped = [], Counter()
    for i, k in enumerate(keys):
        r = measure("|".join(k), dw[k], do_lir=(i < n_lir))
        if r is None:
            skipped["out_of_band_or_degenerate"] += 1
            continue
        recs.append(r)
        if len(recs) % 2500 == 0:
            print(f"  measured {len(recs)}", flush=True)
    print(f"measured {len(recs)}, skipped {dict(skipped)}, repairs {dict(REPAIRS)}",
          flush=True)
    json.dump({"repairs": dict(REPAIRS), "n_dwellings_total": len(dw), "recs": recs},
              open(OUT / "swiss_rects.json", "w"))
    print(f"wrote {OUT / 'swiss_rects.json'}", flush=True)


if __name__ == "__main__":
    main()
