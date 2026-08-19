"""Does Swiss Dwellings supply the real exterior/party exposure distribution?

ADR 0003 makes the Envelope an ordered ring of edges, each `exterior` or `party`,
and *Building scope and envelope handling* flagged that every solver timing on the
map was measured at 100% exterior exposure. This measures what the exposure ring
actually looks like in real flats: per dwelling, what fraction of the Envelope
perimeter faces outside rather than a neighbour or a communal core.

Run: python experiments/corpus-smoke/exposure_swiss_dwellings.py [n_floors]
"""

import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
from shapely import wkt
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
GEOM = ROOT / "data" / "corpora" / "swiss-dwellings" / "swiss-dwellings-v3.0.0" / "geometries.csv"
NULL_APT = "d41d8cd98f00b204e9800998ecf8427e"       # md5("") — unattributed areas
NOT_A_ROOM = {"SHAFT", "VOID", "OUTDOOR_VOID", "LIGHTWELL", "ELEVATOR", "STAIRCASE",
              "TECHNICAL_AREA", "BALCONY", "LOGGIA", "TERRACE", "GARDEN", "PATIO",
              "WINTERGARTEN"}
# A neighbour's wall is not an exterior wall. Anything within this of another
# occupied area is treated as party rather than exterior — one party wall plus
# two finishes.
PARTY_GAP_M = 0.45

N_FLOORS = int(sys.argv[1]) if len(sys.argv) > 1 else 150


def main() -> None:
    cols = ["apartment_id", "site_id", "floor_id", "unit_usage",
            "entity_type", "entity_subtype", "geometry"]

    # Pass 1 — pick floors that actually have neighbours to be party with.
    counts = defaultdict(set)
    for ch in pd.read_csv(GEOM, usecols=[c for c in cols if c != "geometry"],
                          chunksize=1_000_000, dtype=str):
        a = ch[(ch.entity_type == "area") & (ch.unit_usage == "RESIDENTIAL")
               & (ch.apartment_id != NULL_APT)]
        for s, f, ap in zip(a.site_id, a.floor_id, a.apartment_id):
            counts[(s, f)].add(ap)
    multi = sorted(k for k, v in counts.items() if len(v) >= 2)
    random.seed(20260819)
    pick = set(random.sample(multi, min(N_FLOORS, len(multi))))
    print(f"floors with >=2 residential apartments: {len(multi):,}; sampling {len(pick)}")

    # Pass 2 — geometry, for the sampled floors only.
    dwell = defaultdict(list)     # (site,floor,apt) -> interior room polygons
    occupied = defaultdict(list)  # (site,floor) -> every occupied area polygon
    for ch in pd.read_csv(GEOM, usecols=cols, chunksize=500_000, dtype=str):
        ch = ch[ch.entity_type == "area"]
        if ch.empty:
            continue
        key = list(zip(ch.site_id, ch.floor_id))
        ch = ch[[k in pick for k in key]]
        if ch.empty:
            continue
        for s, f, ap, usage, sub, g in zip(ch.site_id, ch.floor_id, ch.apartment_id,
                                           ch.unit_usage, ch.entity_subtype, ch.geometry):
            if sub in NOT_A_ROOM:
                continue
            try:
                poly = wkt.loads(g)
            except Exception:
                continue
            if poly.is_empty:
                continue
            occupied[(s, f)].append(poly)
            if usage == "RESIDENTIAL" and ap != NULL_APT:
                dwell[(s, f, ap)].append(poly)

    fracs, rings = [], Counter()
    for (s, f, ap), polys in dwell.items():
        env = unary_union(polys)
        if env.is_empty or env.geom_type not in ("Polygon", "MultiPolygon"):
            continue
        if env.geom_type == "MultiPolygon":
            env = max(env.geoms, key=lambda p: p.area)      # largest connected part
        boundary = env.exterior
        others = [p for p in occupied[(s, f)] if not p.intersects(env.buffer(-0.05))]
        if not others:
            continue
        near = unary_union([p.buffer(PARTY_GAP_M) for p in others])
        free = boundary.difference(near)
        total = boundary.length
        if total <= 0:
            continue
        ext = free.length / total
        fracs.append(ext)
        rings[round(ext * 4) / 4] += 1

    if not fracs:
        print("no dwellings scored")
        return
    fracs.sort()
    q = statistics.quantiles(fracs, n=20)
    print(f"\ndwellings scored: {len(fracs):,}")
    print(f"exterior fraction of Envelope perimeter:")
    print(f"  p5 {q[0]:.2f}  p25 {q[4]:.2f}  median {statistics.median(fracs):.2f}"
          f"  p75 {q[14]:.2f}  p95 {q[18]:.2f}  mean {statistics.mean(fracs):.2f}")
    print(f"  at or above 0.99 (fully detached, what every map timing assumed): "
          f"{sum(1 for x in fracs if x >= 0.99)} ({100*sum(1 for x in fracs if x>=0.99)/len(fracs):.1f}%)")
    for k in sorted(rings):
        print(f"  ~{k:.2f} exterior : {rings[k]:>5}")


if __name__ == "__main__":
    main()
