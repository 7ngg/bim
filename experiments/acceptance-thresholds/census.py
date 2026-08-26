"""One pass over Swiss Dwellings for every ENGINE_CHOICE threshold at once.

Ticket 20, *Fit the ENGINE_CHOICE acceptance thresholds to the corpora*.

Measured on the RAW polygons, not on the converted tiling. Two reasons, both
from the ticket's own instructions:

  1. Every predicate here is well-defined on a polygon -- area, aspect via
     bbox, circulation share, wet-group count, jamb return -- and the ticket
     says prefer the raw polygons for exactly those.
  2. Swiss room polygons are CLEAR polygons (inner faces): `probe_swiss.py`
     measured a p50 nearest-neighbour gap of 99 mm, i.e. no two room polygons
     touch, ever. So the erosion the ticket warns about -- `t_int/2` off a
     centreline rectangle -- MUST NOT be applied here. It applies to
     `swiss_fit_k2.json`'s `parts`, which are centreline. `parts.py` handles
     that arm separately.

Everything is measured in the dwelling's OWN frame (minimum rotated rectangle
of the room union), because the corpus is geo-referenced and a raw axis-aligned
bbox would measure the site's north angle.

Emits out/swiss_census.json.

Run: python experiments/acceptance-thresholds/census.py [n]
"""
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from shapely import from_wkt
from shapely.affinity import rotate
from shapely.geometry import box
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "rectangularise"))
import measure_swiss as MS  # noqa: E402  -- loader, repairs and frame, reused verbatim

OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)

BAND = MS.BAND            # C13: 4-10 engine rooms
TAU = MS.TAU              # 0.30 m wall-width tolerance for the contact graph
MIN_ROOM_AREA = MS.MIN_ROOM_AREA

# Morphological closing radius for the Envelope interior. buffer(+r).buffer(-r)
# fills every internal partition up to 2r wide and restores the outer boundary,
# so the result is the interior at the INNER FACE of the exterior wall -- which
# is what `envelope_clear_area` means. 2r = 300 mm is comfortably above the
# corpus-optimal internal thickness of 146 mm measured by ticket 33.
CLOSE_R = TAU / 2

# Corpus label -> the class this system reasons in. Two already-decided rules
# and nothing invented here:
#   {ROOM, BEDROOM, STUDIO} collapse to one class (*What the model proposes*)
#   BATHROOM splits at ergonomic.corpus_label_split.threshold_m2 (2.4)
COLLAPSE = {
    "ROOM": "room*", "BEDROOM": "room*", "STUDIO": "room*",
    "LIVING_ROOM": "living", "LIVING_DINING": "living_dining",
    "DINING": "dining", "KITCHEN": "kitchen",
    "KITCHEN_DINING": "kitchen_dining", "CORRIDOR": "corridor",
    "STOREROOM": "storage",
}
BATH_SPLIT_M2 = 2.4
CIRC = {"corridor"}
WET = {"kitchen", "bathroom", "wc", "kitchen_dining"}

OPENINGS = {"DOOR", "WINDOW", "ENTRANCE_DOOR"}
# An opening's own footprint reaches through the wall body; only the part that
# lands on a room's clear face is the reveal we can measure a return against.
EDGE_REACH = 0.40        # m: how far off a room edge an opening centroid may sit
MIN_EDGE_LEN = 0.30      # m: below this a boundary edge is a rasterisation stub


def classify(t, area):
    if t == "BATHROOM":
        return "wc" if area < BATH_SPLIT_M2 else "bathroom"
    return COLLAPSE.get(t, t.lower())


def wet_groups(geoms, idx):
    """Number of maximal sets of wet rooms connected through a shared wall.

    `wet.plumbing_group_count`'s group is "connected by shared WallSegments".
    Corpus rooms never touch, so contact is a buffered intersection at TAU --
    the same test `measure_swiss.contact_graph` uses, and the same one the
    solver's potential-circulation layer is defined over.
    """
    if not idx:
        return 0, []
    bufs = {i: geoms[i].buffer(TAU / 2, join_style=2, mitre_limit=2.0) for i in idx}
    adj = defaultdict(set)
    for a in range(len(idx)):
        for b in range(a + 1, len(idx)):
            i, j = idx[a], idx[b]
            inter = MS._op(lambda p, q: p.intersection(q), bufs[i], bufs[j])
            if inter is not None and not inter.is_empty and inter.area > 1e-9:
                adj[i].add(j)
                adj[j].add(i)
    seen, groups = set(), []
    for i in idx:
        if i in seen:
            continue
        stack, comp = [i], []
        seen.add(i)
        while stack:
            v = stack.pop()
            comp.append(v)
            for w in adj[v]:
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        groups.append(comp)
    return len(groups), groups


def shared_run(g1, g2):
    """Length of shared wall between two clear polygons, in metres.

    The buffered intersection is a band roughly TAU deep along the shared wall;
    its length is area/TAU. Approximate on purpose: `wet.shared_wall_length` is
    a soft ranking term, and what it needs is a distribution, not a survey.
    """
    a = g1.buffer(TAU / 2, join_style=2, mitre_limit=2.0)
    b = g2.buffer(TAU / 2, join_style=2, mitre_limit=2.0)
    inter = MS._op(lambda p, q: p.intersection(q), a, b)
    if inter is None or inter.is_empty:
        return 0.0
    return inter.area / TAU


def edges_of(poly):
    """Axis-aligned boundary edges of a clear polygon, in the dwelling frame.

    Each is (x0, y0, x1, y1, length, axis) with axis 0 for a horizontal edge.
    A room's clear edge runs corner to corner, which is precisely the clear run
    a WallSegment offers an Opening -- the quantity `open.fits_segment` bounds.
    """
    out = []
    cs = list(poly.exterior.coords)
    for (x0, y0), (x1, y1) in zip(cs, cs[1:]):
        dx, dy = x1 - x0, y1 - y0
        if abs(dx) < 0.02 and abs(dy) < 0.02:
            continue
        if abs(dy) <= 0.02:
            out.append((x0, y0, x1, y1, abs(dx), 0))
        elif abs(dx) <= 0.02:
            out.append((x0, y0, x1, y1, abs(dy), 1))
        # a slanted edge belongs to no axis-aligned WallSegment; skip it
    return out


def jamb_returns(poly, ops):
    """Observed jamb return per opening incident on this room, in metres.

    An opening is assigned to the ONE boundary edge nearest its centroid --
    never to every edge it happens to lie within reach of, which double-counts
    a door near a corner onto the perpendicular wall as well. The return is
    then the gap from the opening's structural edge to the nearer end of that
    edge's clear run. Returns (kind, structural_width, run_length, min_return).
    """
    edges = [e for e in edges_of(poly) if e[4] >= MIN_EDGE_LEN]
    if not edges:
        return [], []
    out = []
    on_edge = defaultdict(list)   # edge index -> (a, b, kind), for the piers
    for kind, og in ops:
        c = og.centroid
        best, bestd, besti = None, 1e9, -1
        for ei, (x0, y0, x1, y1, L, axis) in enumerate(edges):
            lo, hi = ((min(x0, x1), max(x0, x1)) if axis == 0
                      else (min(y0, y1), max(y0, y1)))
            off = y0 if axis == 0 else x0
            along, perp = (c.x, c.y) if axis == 0 else (c.y, c.x)
            # distance from the centroid to the edge SEGMENT, not its line
            d_along = max(lo - along, 0.0, along - hi)
            d = math.hypot(d_along, perp - off)
            if d < bestd:
                bestd, best, besti = d, (lo, hi, off, axis, L), ei
        if bestd > EDGE_REACH:
            continue
        lo, hi, off, axis, L = best
        ox0, oy0, ox1, oy1 = og.bounds
        a, b = (ox0, ox1) if axis == 0 else (oy0, oy1)
        if b <= lo + 1e-9 or a >= hi - 1e-9:
            continue
        a, b = max(a, lo), min(b, hi)
        w = b - a
        if w < 0.4:              # not the along-wall extent of this opening
            continue
        out.append((kind, w, L, min(a - lo, hi - b)))
        on_edge[besti].append((a, b, kind))

    # AZ.openings.min_pier_mm: the wall left between two structural openings on
    # ONE run. Handed to this ticket by *Opening placement rules* as the only
    # unfitted constant openings.md adds.
    piers = []
    for ei, items in on_edge.items():
        if len(items) < 2:
            continue
        items.sort()
        for (a0, b0, k0), (a1, b1, k1) in zip(items, items[1:]):
            gap = a1 - b0
            if gap >= -0.05:
                piers.append((k0, k1, max(gap, 0.0)))
    return out, piers


def measure(key, rooms, ops):
    geoms, types = [], []
    for st, wkt in rooms:
        g = MS._poly(from_wkt(wkt))
        if g is None or g.area < MIN_ROOM_AREA:
            continue
        geoms.append(g)
        types.append(st)
    n = len(geoms)
    if not (BAND[0] <= n <= BAND[1]):
        return None

    ang, cen = MS.dwelling_frame(geoms)
    if ang is None:
        return None
    geoms = [rotate(g, -ang, origin=cen) for g in geoms]
    ogeoms = []
    for st, wkt in ops:
        g = MS._poly(from_wkt(wkt))
        if g is None:
            continue
        ogeoms.append((st, rotate(g, -ang, origin=cen)))

    areas = [g.area for g in geoms]
    cls = [classify(t, a) for t, a in zip(types, areas)]

    # Aspect on the raw polygon's own bbox: the ticket names "aspect via bbox"
    # as one of the predicates that is well-defined on a polygon.
    dims = []
    for g in geoms:
        bx0, by0, bx1, by1 = g.bounds
        dims.append((bx1 - bx0, by1 - by0))

    # Envelope interior at the inner face of the exterior wall.
    u = MS._op(unary_union, geoms)
    if u is None or u.is_empty:
        return None
    closed = MS._op(lambda g: g.buffer(CLOSE_R, join_style=2, mitre_limit=2.0)
                    .buffer(-CLOSE_R, join_style=2, mitre_limit=2.0), u)
    if closed is None or closed.is_empty:
        return None
    mrr = closed.minimum_rotated_rectangle
    if hasattr(mrr, "exterior"):
        cc = np.asarray(mrr.exterior.coords)
        s1 = math.hypot(*(cc[1] - cc[0]))
        s2 = math.hypot(*(cc[2] - cc[1]))
        env_long, env_short = max(s1, s2), min(s1, s2)
    else:
        env_long = env_short = 0.0
    env_bbox = box(*closed.bounds)

    widx = [i for i, c in enumerate(cls) if c in WET]
    ngroups, groups = wet_groups(geoms, widx)
    runs = []
    for gcomp in groups:
        for a in range(len(gcomp)):
            for b in range(a + 1, len(gcomp)):
                r = shared_run(geoms[gcomp[a]], geoms[gcomp[b]])
                if r > 0:
                    runs.append(r)

    jam, piers = [], []
    for i, g in enumerate(geoms):
        near = [(st, og) for st, og in ogeoms
                if og.distance(g) < EDGE_REACH]
        js, ps = jamb_returns(g, near)
        for kind, w, L, ret in js:
            jam.append([cls[i], kind, round(w, 4), round(L, 4), round(ret, 4)])
        for k0, k1, gap in ps:
            piers.append([k0, k1, round(gap, 4)])

    return {
        "k": key, "n": n, "cls": cls,
        "area": [round(a, 4) for a in areas],
        "dim": [[round(w, 4), round(h, 4)] for w, h in dims],
        "env_area": round(closed.area, 4),
        "env_bbox_area": round(env_bbox.area, 4),
        "env_long": round(env_long, 4), "env_short": round(env_short, 4),
        "wet_groups": ngroups,
        "wet_runs": [round(r, 4) for r in runs],
        "n_entrance": sum(1 for st, _ in ogeoms if st == "ENTRANCE_DOOR"),
        "jambs": jam,
        "piers": piers,
    }


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    rooms, ops = defaultdict(list), defaultdict(list)
    for chunk in pd.read_csv(MS.GEOM, usecols=MS.COLS, chunksize=500_000, dtype=str):
        chunk = chunk[(chunk["unit_usage"] == "RESIDENTIAL") &
                      (chunk["apartment_id"] != MS.MD5_EMPTY)]
        a = chunk[chunk["entity_type"] == "area"]
        a = a[~a["entity_subtype"].isin(MS.NOT_A_ROOM)]
        for s, f, ap, st, g in zip(a["site_id"], a["floor_id"], a["apartment_id"],
                                   a["entity_subtype"].fillna("<NA>"), a["geometry"]):
            rooms[(s, f, ap)].append((st, g))
        o = chunk[chunk["entity_type"] == "opening"]
        o = o[o["entity_subtype"].isin(OPENINGS)]
        for s, f, ap, st, g in zip(o["site_id"], o["floor_id"], o["apartment_id"],
                                   o["entity_subtype"].fillna("<NA>"), o["geometry"]):
            ops[(s, f, ap)].append((st, g))
    print(f"dwellings loaded: {len(rooms)}", flush=True)

    keys = sorted(rooms.keys())
    keys.sort(key=lambda k: hashlib.md5("|".join(k).encode()).hexdigest())
    if limit:
        keys = keys[:limit]

    recs, skipped = [], Counter()
    for i, k in enumerate(keys):
        r = measure("|".join(k), rooms[k], ops.get(k, []))
        if r is None:
            skipped["out_of_band_or_degenerate"] += 1
            continue
        recs.append(r)
        if len(recs) % 5000 == 0:
            print(f"  measured {len(recs)}", flush=True)
    print(f"measured {len(recs)}, skipped {dict(skipped)}, "
          f"repairs {dict(MS.REPAIRS)}", flush=True)
    json.dump({"repairs": dict(MS.REPAIRS), "n_dwellings_total": len(rooms),
               "bath_split_m2": BATH_SPLIT_M2, "close_r_m": CLOSE_R,
               "recs": recs}, open(OUT / "swiss_census.json", "w"))
    print(f"wrote {OUT / 'swiss_census.json'}", flush=True)


if __name__ == "__main__":
    main()
