"""Is the corpus's windowless kitchen a `taxça-mətbəx`, or a dark room behind a door?

Ticket 51. Two documents on this map read the same statistic the same way:

  ticket 26 §6 -- "84.7 % adjoin a windowed habitable room -- borrowed daylight,
  the taxca-metbex arrangement AzDTN names"
  ticket 51    -- "84.7 % of the real cases are ... an open kitchen zone of a
  windowed living space"

**Adjacency is not openness.** AzDTN 2.7-2 cl. 5.7's `taxça-mətbəx` is a niche --
a recess open to the room it sits in, >= 5 m2, named in the norm as a term distinct
from `mətbəx`. A separate KITCHEN with a **door** onto a windowed living room is not
that. It is a windowless kitchen, which cl. 9.12 forbids outright.

Both documents rest on a geometric adjacency test, which cannot tell the two apart.
This one can, in one direction: Swiss Dwellings ships ~715,000 `opening` rows, so a
DOOR polygon lying on the shared boundary is positive evidence of a **door**, and a
door is positive evidence of **not a niche**.

⚠️ **The test is one-sided on purpose.** Absence of a door polygon is not evidence
of an open threshold -- the corpus may simply not model one, or the two rooms may
merely touch without connecting. So this can falsify the niche reading and cannot
confirm it, and the finding is reported that way round.

Run: ./venv/Scripts/python.exe experiments/corpus-smoke/kitchen_niche_test.py
     (~8 min: one pass over geometries.csv keeping every opening)
"""

from __future__ import annotations

import json
import pickle
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
from shapely import wkt
from shapely.ops import unary_union
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parents[2]
GEOM = ROOT / "data/corpora/swiss-dwellings/swiss-dwellings-v3.0.0/geometries.csv"
FITS = ROOT / "experiments/rectangularise/out"
OUT = Path(__file__).resolve().parent / "out"

NEEDS_WINDOW = {"ROOM", "LIVING_DINING", "BEDROOM", "LIVING_ROOM", "DINING",
                "KITCHEN_DINING", "STUDIO", "KITCHEN"}
HABITABLE = NEEDS_WINDOW - {"KITCHEN"}
BRIDGE = 0.12
NEAR_M = 0.60          # an opening sits in the wall, not in the room polygon
ADJOIN_M = 0.30        # two rooms sharing a partition
NICHE_MIN_M2 = 5.0     # AzDTN 2.7-2 cl. 5.7


def pct(a, b):
    return f"{100 * a / b:5.2f}%" if b else "    - "


def rule(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


def main():
    OUT.mkdir(exist_ok=True)
    dw, _ = pickle.load(open(FITS / "swiss_dw.pkl", "rb"))
    floors = {(s, f) for (s, f, _a) in dw}
    print(f"{len(dw):,} dwellings on {len(floors):,} floors", file=sys.stderr)

    cols = ["site_id", "floor_id", "entity_type", "entity_subtype", "geometry"]
    wins, doors = defaultdict(list), defaultdict(list)
    subtypes = Counter()
    for ch in pd.read_csv(GEOM, usecols=cols, chunksize=500_000, dtype=str):
        ch = ch[ch.entity_type == "opening"]
        if ch.empty:
            continue
        ch = ch[[k in floors for k in zip(ch.site_id, ch.floor_id)]]
        for s, f, sub, g in zip(ch.site_id, ch.floor_id, ch.entity_subtype,
                                ch.geometry):
            u = str(sub).upper()
            subtypes[u] += 1
            try:
                p = wkt.loads(g)
            except Exception:
                continue
            if p.is_empty:
                continue
            if u.startswith("WINDOW"):
                wins[(s, f)].append(p)
            else:
                doors[(s, f)].append(p)
        print(f"  ... {sum(subtypes.values()):,} openings", file=sys.stderr,
              flush=True)
    print("opening subtypes:", dict(subtypes.most_common()), file=sys.stderr)

    stat = Counter()
    areas = []
    for i, (key, rooms) in enumerate(dw.items()):
        if i % 5000 == 0:
            print(f"  ... {i:,}/{len(dw):,}", file=sys.stderr, flush=True)
        site, floor, _apt = key
        polys, subs = [], []
        for sub, g in rooms:
            try:
                p = wkt.loads(g) if isinstance(g, str) else g
            except Exception:
                continue
            if p.is_empty or p.geom_type != "Polygon":
                continue
            polys.append(p)
            subs.append(sub)
        if "KITCHEN" not in subs:
            continue
        env = unary_union([p.buffer(BRIDGE) for p in polys]).buffer(-BRIDGE)
        if env.is_empty:
            continue
        if env.geom_type == "MultiPolygon":
            env = max(env.geoms, key=lambda p: p.area)
        if env.geom_type != "Polygon":
            continue
        band_env = env.exterior.buffer(NEAR_M)
        fw = [w for w in wins.get((site, floor), ()) if w.intersects(band_env)]
        tree = STRtree(fw) if fw else None

        def glazed(p):
            if tree is None:
                return False
            b = p.exterior.buffer(NEAR_M)
            return any(fw[j].intersects(b) for j in tree.query(b))

        lit = [p for sub, p in zip(subs, polys)
               if sub in HABITABLE and glazed(p)]
        lit_union = unary_union(lit) if lit else None
        fd = doors.get((site, floor), ())
        dtree = STRtree(fd) if fd else None

        for sub, p in zip(subs, polys):
            if sub != "KITCHEN" or glazed(p):
                continue
            stat["windowless kitchens"] += 1
            areas.append(p.area)
            if lit_union is None or not p.buffer(ADJOIN_M).intersects(lit_union):
                stat["  no lit neighbour at all"] += 1
                continue
            stat["  adjoins a windowed habitable room"] += 1
            if p.area >= NICHE_MIN_M2:
                stat["    ...and clears cl. 5.7's 5 m2"] += 1
            # is there a DOOR on the shared boundary with the lit neighbour?
            shared = p.buffer(ADJOIN_M).intersection(lit_union.buffer(ADJOIN_M))
            hit = False
            if dtree is not None and not shared.is_empty:
                hit = any(fd[j].intersects(shared) for j in dtree.query(shared))
            stat["    DOOR on the shared boundary" if hit
                 else "    no door polygon on the shared boundary"] += 1

    rule("Windowless kitchens — niche, or dark room behind a door?")
    n = stat["windowless kitchens"]
    for k, v in stat.items():
        print(f"{k:<48}{v:>8,}  {pct(v, n)}")
    if areas:
        print(f"\nmedian windowless-kitchen area {st.median(areas):.1f} m2  "
              f"(ticket 26 measured 6.8 on 549)")
    adj = stat["  adjoins a windowed habitable room"]
    door = stat["    DOOR on the shared boundary"]
    json.dump(dict(stat), open(OUT / "kitchen_niche_test.json", "w"), indent=1)
    # ASCII only past here: this repo's console is cp1252 and the schwa in
    # `taxça-mətbəx` raises UnicodeEncodeError, which killed a 9-minute run
    # AFTER it had printed every number and BEFORE it wrote the json.
    print(f"\nOf the adjoining kitchens the map reads as `taxca-metbex`, "
          f"{pct(door, adj)} carry a DOOR on that shared boundary.")
    print("A niche has no door. This falsifies the niche reading for that share;")
    print("the remainder is UNDETERMINED, not confirmed -- see the docstring.")


if __name__ == "__main__":
    main()
