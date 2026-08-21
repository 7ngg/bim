"""Does a derived ergonomic floor reject real homes?

*Acceptance validator spec* made the ergonomic minimum the ENTIRE hard reject set
of the acceptance bar, and *Rectangularising real rooms* set the principle that
decides whether a number is right: every corpus dwelling is a real, built, QA'd
home, so a hard rule that rejects them measures what our model cannot express,
not what is wrong with the data.

So a derived floor is not self-justifying. This measures, per room type:

  * the area distribution, and
  * the SHORT and LONG side of each room's minimum rotated rectangle -- which is
    axis-free, and so is the honest corpus analogue of the (min_short, min_long)
    pair the ergonomic layer publishes. `Rectangularising real rooms` measured
    0.0% of rooms rectangular in the corpus's own geo-referenced coordinates, so
    an axis-aligned bounding box is not usable here.

Read the p1 column as the falsification test: a published floor above it rejects
real dwellings at a rate the acceptance bar cannot afford, and the derivation
that produced it used the wrong clearance primitive.

BATHROOM is split by fixture, not by area -- see bathroom_fixture_split.py.

Run: python experiments/region-profile/ergonomic_floor_probe.py
"""

from __future__ import annotations

import collections
from pathlib import Path

import numpy as np
import pandas as pd
from shapely import from_wkt
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parents[2]
GEOM = ROOT / "data" / "corpora" / "swiss-dwellings" / "swiss-dwellings-v3.0.0" / "geometries.csv"
MD5_EMPTY = "d41d8cd98f00b204e9800998ecf8427e"

# Corpus label -> our room type. SHAFT, BALCONY, ELEVATOR and the commercial
# labels are dropped: *Acquire the datasets* found SHAFTs outnumber bathrooms and
# counting them as rooms is one of the three ways ticket 18's SQL was wrong.
LABEL_MAP = {
    "ROOM": "private",
    "BEDROOM": "private",
    "LIVING_ROOM": "living",
    "LIVING_DINING": "living_dining",
    "DINING": "dining",
    "KITCHEN": "kitchen",
    "KITCHEN_DINING": "kitchen_dining",
    "CORRIDOR": "corridor",
    "CORRIDORS_AND_HALLS": "hall",
    "LOBBY": "entrance_lobby",
    "STOREROOM": "storage",
    "WASH_AND_DRY_ROOM": "utility",
}
BATHING = {"BATHTUB", "SHOWER"}
FIXTURES = BATHING | {"TOILET", "SINK", "WASHING_MACHINE"}
COLS = ["apartment_id", "floor_id", "unit_usage",
        "entity_type", "entity_subtype", "geometry"]


def short_long(poly) -> tuple[float, float]:
    """Sides of the minimum rotated rectangle, in metres, shorter first."""
    xs, ys = poly.minimum_rotated_rectangle.exterior.coords.xy
    pts = list(zip(xs, ys))[:4]
    if len(pts) < 4:
        return 0.0, 0.0
    a = float(np.hypot(pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]))
    b = float(np.hypot(pts[2][0] - pts[1][0], pts[2][1] - pts[1][1]))
    return (a, b) if a <= b else (b, a)


def main() -> None:
    rooms: dict[str, list] = collections.defaultdict(list)
    bath_by_floor: dict[str, list] = collections.defaultdict(list)
    feats: dict[str, list] = collections.defaultdict(list)

    for chunk in pd.read_csv(GEOM, usecols=COLS, chunksize=500_000, dtype=str):
        res = chunk[(chunk["unit_usage"] == "RESIDENTIAL") &
                    (chunk["apartment_id"] != MD5_EMPTY)]
        a = res[res["entity_type"] == "area"]
        for fid, st, wkt in zip(a["floor_id"], a["entity_subtype"].fillna(""), a["geometry"]):
            if st != "BATHROOM" and st not in LABEL_MAP:
                continue
            g = from_wkt(wkt)
            if g is None or g.is_empty or g.area <= 0:
                continue
            if st == "BATHROOM":
                bath_by_floor[fid].append(g)
            else:
                rooms[LABEL_MAP[st]].append(g)
        f = res[(res["entity_type"] == "feature") &
                (res["entity_subtype"].isin(FIXTURES))]
        for fid, st, wkt in zip(f["floor_id"], f["entity_subtype"], f["geometry"]):
            g = from_wkt(wkt)
            if g is not None and not g.is_empty:
                feats[fid].append((st, g.representative_point()))

    # BATHROOM splits by fixture, not by area.
    for fid, polys in bath_by_floor.items():
        tree = STRtree(polys)
        bag: list[set] = [set() for _ in polys]
        for kind, pt in feats.get(fid, ()):
            for idx in tree.query(pt):
                if polys[idx].contains(pt):
                    bag[idx].add(kind)
                    break
        for poly, fx in zip(polys, bag):
            if fx & BATHING:
                rooms["bathroom" if "BATHTUB" in fx else "shower_room"].append(poly)
            elif "TOILET" in fx:
                rooms["wc"].append(poly)

    cache = ROOT / "experiments" / "region-profile" / "out" / "room_dims.npz"
    cache.parent.mkdir(parents=True, exist_ok=True)
    blob = {}
    for kind, polys in rooms.items():
        sl = [short_long(p) for p in polys]
        blob[kind] = np.array([[x[0] * 1000, x[1] * 1000, p.area]
                               for x, p in zip(sl, polys)])
    np.savez_compressed(cache, **blob)
    print(f"cached {sum(len(v) for v in blob.values())} rooms -> {cache}")
    print()

    qs = (1, 5, 25, 50)
    print("Swiss Dwellings, RESIDENTIAL areas. Sides are the minimum rotated")
    print("rectangle, in mm. `area` in m2. A published floor above the p1 column")
    print("rejects real, built dwellings.")
    print()
    hdr = f"{'room type':16s} {'n':>7} |" + "".join(f"{f'short p{q}':>10}" for q in qs)
    hdr += " |" + "".join(f"{f'long p{q}':>10}" for q in qs)
    hdr += " |" + "".join(f"{f'area p{q}':>10}" for q in qs)
    print(hdr)
    for kind in sorted(rooms):
        polys = rooms[kind]
        sl = [short_long(p) for p in polys]
        s = np.array([x[0] for x in sl]) * 1000
        lg = np.array([x[1] for x in sl]) * 1000
        ar = np.array([p.area for p in polys])
        row = f"{kind:16s} {len(polys):7d} |"
        row += "".join(f"{np.percentile(s, q):10.0f}" for q in qs)
        row += " |" + "".join(f"{np.percentile(lg, q):10.0f}" for q in qs)
        row += " |" + "".join(f"{np.percentile(ar, q):10.2f}" for q in qs)
        print(row)


if __name__ == "__main__":
    main()
