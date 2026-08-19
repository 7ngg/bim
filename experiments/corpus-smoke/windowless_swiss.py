"""The nine ~0.00-exterior dwellings: real windowless homes, or a bad heuristic?

`exposure_swiss_dwellings.py` measured the exterior fraction of 569 dwellings
and found nine at roughly zero. `dataset-inventory.md` 1.5 flagged them as
"genuinely windowless units, which would fail acceptance rule H8 outright and
are worth inspecting before they are treated as noise", and *Solver timing
variance sweep* inherited the question, because the answer decides whether H8 is
correct or is rejecting homes that exist.

The corpus can settle it. Swiss Dwellings ships ~715,000 `opening` rows, so a
dwelling either has WINDOW openings on its boundary or it does not, and that is
independent of the 0.45 m party-gap judgement the exposure measurement rests on:

* windows present  -> the exposure heuristic mis-classified a real elevation as
  party, and the p25/median quantiles are biased low at the bottom tail.
* no windows       -> the units are genuinely windowless, H8 as posted rejects
  them, and the map has to say whether that is intended.

Same sample as the exposure run (same seed, same floor count), so the dwellings
inspected here are exactly the ones that scored ~0.00 there.

Run: python experiments/corpus-smoke/windowless_swiss.py [n_floors]
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
NULL_APT = "d41d8cd98f00b204e9800998ecf8427e"
NOT_A_ROOM = {"SHAFT", "VOID", "OUTDOOR_VOID", "LIGHTWELL", "ELEVATOR", "STAIRCASE",
              "TECHNICAL_AREA", "BALCONY", "LOGGIA", "TERRACE", "GARDEN", "PATIO",
              "WINTERGARTEN"}
PARTY_GAP_M = 0.45
NEAR_BOUNDARY_M = 0.60      # an opening sits in the wall, not in the room polygon

N_FLOORS = int(sys.argv[1]) if len(sys.argv) > 1 else 150
FLAT = 0.02                 # "~0.00 exterior"


def main() -> None:
    cols = ["apartment_id", "site_id", "floor_id", "unit_usage",
            "entity_type", "entity_subtype", "geometry"]

    counts = defaultdict(set)
    for ch in pd.read_csv(GEOM, usecols=[c for c in cols if c != "geometry"],
                          chunksize=1_000_000, dtype=str):
        a = ch[(ch.entity_type == "area") & (ch.unit_usage == "RESIDENTIAL")
               & (ch.apartment_id != NULL_APT)]
        for s, f, ap in zip(a.site_id, a.floor_id, a.apartment_id):
            counts[(s, f)].add(ap)
    multi = sorted(k for k, v in counts.items() if len(v) >= 2)
    random.seed(20260819)                       # identical to the exposure run
    pick = set(random.sample(multi, min(N_FLOORS, len(multi))))
    print(f"floors sampled: {len(pick)} (same seed and count as the exposure run)")

    dwell = defaultdict(list)
    subtypes = defaultdict(Counter)
    occupied = defaultdict(list)
    openings = defaultdict(list)                # (site,floor) -> (subtype, poly)
    for ch in pd.read_csv(GEOM, usecols=cols, chunksize=500_000, dtype=str):
        ch = ch[ch.entity_type.isin(("area", "opening"))]
        if ch.empty:
            continue
        ch = ch[[k in pick for k in zip(ch.site_id, ch.floor_id)]]
        if ch.empty:
            continue
        for s, f, ap, usage, et, sub, g in zip(
                ch.site_id, ch.floor_id, ch.apartment_id, ch.unit_usage,
                ch.entity_type, ch.entity_subtype, ch.geometry):
            try:
                poly = wkt.loads(g)
            except Exception:
                continue
            if poly.is_empty:
                continue
            if et == "opening":
                openings[(s, f)].append((str(sub), poly))
                continue
            if sub in NOT_A_ROOM:
                continue
            occupied[(s, f)].append(poly)
            if usage == "RESIDENTIAL" and ap != NULL_APT:
                dwell[(s, f, ap)].append(poly)
                subtypes[(s, f, ap)][str(sub)] += 1

    rows = []
    for (s, f, ap), polys in dwell.items():
        env = unary_union(polys)
        if env.is_empty or env.geom_type not in ("Polygon", "MultiPolygon"):
            continue
        if env.geom_type == "MultiPolygon":
            env = max(env.geoms, key=lambda p: p.area)
        boundary = env.exterior
        others = [p for p in occupied[(s, f)] if not p.intersects(env.buffer(-0.05))]
        if not others:
            continue
        near = unary_union([p.buffer(PARTY_GAP_M) for p in others])
        total = boundary.length
        if total <= 0:
            continue
        ext = boundary.difference(near).length / total

        band = boundary.buffer(NEAR_BOUNDARY_M)
        win = doors = 0
        for sub, op in openings[(s, f)]:
            if not op.intersects(band):
                continue
            if sub.upper().startswith("WINDOW"):
                win += 1
            elif sub.upper().startswith("DOOR") or "ENTRANCE" in sub.upper():
                doors += 1
        rows.append({"key": (s, f, ap), "ext": ext, "rooms": len(polys),
                     "area": env.area, "windows": win, "doors": doors,
                     "subtypes": subtypes[(s, f, ap)]})

    rows.sort(key=lambda r: r["ext"])
    print(f"dwellings scored: {len(rows)}")
    flat = [r for r in rows if r["ext"] < FLAT]
    print(f"at ~0.00 exterior (< {FLAT}): {len(flat)}\n")

    print(f"{'ext':>5} {'rooms':>5} {'area m2':>8} {'wins':>5} {'doors':>5}  subtypes")
    for r in flat:
        st = ", ".join(f"{k}x{v}" for k, v in r["subtypes"].most_common(6))
        print(f"{r['ext']:5.3f} {r['rooms']:5d} {r['area']:8.1f} "
              f"{r['windows']:5d} {r['doors']:5d}  {st}")

    if flat:
        wl = [r for r in flat if r["windows"] == 0]
        print(f"\nof the {len(flat)}: {len(wl)} carry no WINDOW opening on the "
              f"boundary band, {len(flat)-len(wl)} do.")

    # Control: does the window count track the exterior fraction at all? If it
    # does, the heuristic is measuring something real and the zeros mean it.
    have = [r for r in rows if r["windows"] > 0]
    print(f"\ncontrol over all {len(rows)} scored dwellings:")
    print(f"  with >=1 boundary window: {len(have)} "
          f"({100*len(have)/len(rows):.1f}%)")
    for lo, hi in ((0.0, 0.02), (0.02, 0.15), (0.15, 0.30), (0.30, 0.45),
                   (0.45, 1.01)):
        b = [r for r in rows if lo <= r["ext"] < hi]
        if not b:
            continue
        print(f"  ext {lo:.2f}-{hi:.2f}: n={len(b):>4} "
              f"median windows {statistics.median([r['windows'] for r in b]):>4.1f} "
              f"median rooms {statistics.median([r['rooms'] for r in b]):>4.1f}")


if __name__ == "__main__":
    main()
