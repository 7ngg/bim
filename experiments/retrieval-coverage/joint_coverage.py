"""Retrieval coverage over Swiss Dwellings — pass 2, the joint constraint.

Pass 1 measured room-multiset pools. A multiset match is necessary and not
sufficient: retrieval-and-warp must also land the arrangement inside the Brief's
Envelope. Warping a plan from a 6 x 12 slab into a 9 x 8 near-square does not move
geometry, it invents arrangement.

So the number that decides the route is the JOINT pool: dwellings sharing the
Brief's room multiset AND close in envelope size AND close in envelope
proportion. Under C6 that pool size is the candidate count.

Envelope proxy: minimum-area rotated rectangle of the union of the dwelling's
rooms. Swiss Dwellings polygons sit in arbitrary global orientation, so an
axis-aligned bbox would measure the site's north angle, not the flat.

Run: python experiments/retrieval-coverage/joint_coverage.py
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from shapely import from_wkt
from shapely.geometry import MultiPolygon
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
GEOM = ROOT / "data" / "corpora" / "swiss-dwellings" / "swiss-dwellings-v3.0.0" / "geometries.csv"
OUT = Path(__file__).resolve().parent / "out"

NOT_A_ROOM = {
    "SHAFT", "VOID", "OUTDOOR_VOID", "LIGHTWELL", "ELEVATOR", "STAIRCASE",
    "TECHNICAL_AREA", "BALCONY", "LOGGIA", "TERRACE", "GARDEN", "PATIO",
    "WINTERGARTEN",
}
# md5("") — 5,091 rows of unattributed areas. Ticket 12 drops these; without the
# drop the tail carries six phantom 74-room "dwellings".
MD5_EMPTY = "d41d8cd98f00b204e9800998ecf8427e"

COLS = ["apartment_id", "site_id", "floor_id", "unit_usage",
        "entity_type", "entity_subtype", "geometry"]

AREA_TOL = 0.10     # +/- 10% total floor area
ASPECT_TOL = 0.15   # +/- 15% envelope aspect ratio


def band(n):
    if n <= 3:
        return "1-3"
    if n <= 6:
        return "4-6"
    if n <= 10:
        return "7-10"
    if n <= 15:
        return "11-15"
    return "16+"


BANDS = ["1-3", "4-6", "7-10", "11-15", "16+"]


def collect():
    rooms = defaultdict(Counter)
    polys = defaultdict(list)
    reader = pd.read_csv(GEOM, usecols=COLS, chunksize=500_000, dtype=str)
    for chunk in reader:
        a = chunk[(chunk["entity_type"] == "area") &
                  (chunk["unit_usage"] == "RESIDENTIAL") &
                  (chunk["apartment_id"] != MD5_EMPTY)]
        a = a[~a["entity_subtype"].isin(NOT_A_ROOM)]
        for s, f, ap, st, wkt in zip(a["site_id"], a["floor_id"], a["apartment_id"],
                                     a["entity_subtype"].fillna("<NA>"), a["geometry"]):
            k = (s, f, ap)
            rooms[k][st] += 1
            polys[k].append(wkt)
    return rooms, polys


def envelope_of(wkts):
    """(total room area m2, envelope area m2, aspect >= 1) from the min rotated rect."""
    gs = [from_wkt(w) for w in wkts]
    gs = [g for g in gs if g is not None and not g.is_empty]
    if not gs:
        return None
    total = float(sum(g.area for g in gs))
    u = unary_union([g.buffer(0) for g in gs])
    if u.is_empty:
        return None
    mrr = u.minimum_rotated_rectangle
    c = np.asarray(mrr.exterior.coords)[:-1] if hasattr(mrr, "exterior") else None
    if c is None or len(c) < 4:
        return None
    e = np.linalg.norm(np.diff(np.vstack([c, c[:1]]), axis=0), axis=1)
    w, d = sorted(e[:2])
    if w <= 0.01:
        return None
    return total, float(w * d), float(d / w)


def main():
    OUT.mkdir(exist_ok=True)
    rooms, polys = collect()
    print(f"dwellings (md5-empty dropped): {len(rooms):,}")
    hist = Counter(sum(c.values()) for c in rooms.values())
    print(f"  >=16: {sum(v for k, v in hist.items() if k >= 16):,}"
          f"   >=24: {sum(v for k, v in hist.items() if k >= 24):,}"
          f"   mean: {sum(k*v for k, v in hist.items())/len(rooms):.2f}   "
          f"(ticket 12: 66 / 1 / 6.82)")

    recs = []
    skipped = 0
    for k, c in rooms.items():
        e = envelope_of(polys[k])
        if e is None:
            skipped += 1
            continue
        total, env_area, aspect = e
        recs.append({"key": k, "ms": tuple(sorted(c.items())), "n": sum(c.values()),
                     "area": total, "env": env_area, "aspect": aspect})
    print(f"envelope computed for {len(recs):,}; skipped {skipped}")

    by_ms = defaultdict(list)
    for r in recs:
        by_ms[r["ms"]].append(r)

    print(f"\n{'band':<8}{'dwellings':>10}{'median exact':>14}{'median joint':>14}"
          f"{'joint=0':>9}{'joint<3':>9}{'joint>=20':>11}")
    out = {}
    for b in BANDS:
        sel = [r for r in recs if band(r["n"]) == b]
        if not sel:
            continue
        exact, joint = [], []
        for r in sel:
            peers = by_ms[r["ms"]]
            exact.append(len(peers) - 1)
            j = sum(1 for p in peers
                    if p["key"] != r["key"]
                    and abs(p["area"] - r["area"]) <= AREA_TOL * r["area"]
                    and abs(p["aspect"] - r["aspect"]) <= ASPECT_TOL * r["aspect"])
            joint.append(j)
        exact.sort(); joint.sort()
        me, mj = exact[len(exact)//2], joint[len(joint)//2]
        z = sum(1 for x in joint if x == 0)
        lt3 = sum(1 for x in joint if x < 3)
        ge20 = sum(1 for x in joint if x >= 20)
        print(f"{b:<8}{len(sel):>10,}{me:>14,}{mj:>14,}{z:>9,}{lt3:>9,}{ge20:>11,}")
        out[b] = {"n": len(sel), "median_exact": me, "median_joint": mj,
                  "joint_zero": z, "joint_lt3": lt3, "joint_ge20": ge20}

    common = [r for r in recs if 4 <= r["n"] <= 10]
    jj = []
    for r in common:
        peers = by_ms[r["ms"]]
        jj.append(sum(1 for p in peers
                      if p["key"] != r["key"]
                      and abs(p["area"] - r["area"]) <= AREA_TOL * r["area"]
                      and abs(p["aspect"] - r["aspect"]) <= ASPECT_TOL * r["aspect"]))
    jj.sort()
    n = len(jj)
    print(f"\ncommon band 4-10 rooms: {n:,} dwellings")
    print(f"  joint pool  p5={jj[n//20]}  p25={jj[n//4]}  median={jj[n//2]}"
          f"  p75={jj[3*n//4]}  p95={jj[19*n//20]}")
    print(f"  joint pool = 0: {sum(1 for x in jj if x==0):,} "
          f"({100*sum(1 for x in jj if x==0)/n:.1f}%)")
    print(f"  joint pool < 20 (C6 headroom): {sum(1 for x in jj if x<20):,} "
          f"({100*sum(1 for x in jj if x<20)/n:.1f}%)")

    asp = sorted(r["aspect"] for r in recs)
    print(f"\nenvelope aspect ratio: p5={asp[len(asp)//20]:.2f} "
          f"median={asp[len(asp)//2]:.2f} p95={asp[19*len(asp)//20]:.2f}")
    fill = sorted(r["area"]/r["env"] for r in recs if r["env"] > 0)
    print(f"rooms/min-rotated-rect fill: p5={fill[len(fill)//20]:.2f} "
          f"median={fill[len(fill)//2]:.2f} p95={fill[19*len(fill)//20]:.2f}")

    json.dump(out, open(OUT / "joint_coverage.json", "w"), indent=1)
    print(f"\nwrote {OUT/'joint_coverage.json'}")


if __name__ == "__main__":
    main()
