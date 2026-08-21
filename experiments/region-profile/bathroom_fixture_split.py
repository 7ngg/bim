"""Where does a WC stop and a bathroom start, measured against fixtures?

*What the model proposes* found one `BATHROOM` label in Swiss Dwellings spanning
p5 1.5 m2 to p95 6.3 m2 -- a WC at one end, a family bathroom at the other -- and
handed the splitting threshold to *Ergonomic minima and the constraint table's
missing half*, because the threshold is the boundary between two rooms' derived
minima and inventing a second number on the Proposer side would create a table to
drift against this one.

The derivation gives two candidate boundaries:

    3.6 m2   the `shower_room` ergonomic floor (1900 x 1900)
    4.0 m2   the `bathroom` ergonomic floor  (1900 x 2150)

This script does not assume them. Swiss Dwellings carries `feature` rows --
BATHTUB (24,759), SHOWER (8,428), TOILET (38,918), SINK -- so the split has a
GROUND TRUTH: a BATHROOM area containing a bathtub or a shower is a bathroom; one
containing only a toilet and/or a sink is a WC. We measure the area distribution
of each class and score the candidate thresholds against it.

Join is geometric: `feature` rows carry no area_id, so a feature belongs to the
area polygon that contains its representative point, within the same floor_id.

Run: python experiments/region-profile/bathroom_fixture_split.py
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

WET_FIXTURES = {"BATHTUB", "SHOWER", "TOILET", "SINK", "WASHING_MACHINE"}
CANDIDATES = (3.0, 3.4, 3.6, 4.0, 4.4)

COLS = ["apartment_id", "floor_id", "unit_usage",
        "entity_type", "entity_subtype", "geometry"]


def load() -> tuple[dict, dict]:
    """floor_id -> [(area_index, polygon)] for BATHROOMs, and -> [(kind, point)]."""
    baths: dict[str, list] = collections.defaultdict(list)
    feats: dict[str, list] = collections.defaultdict(list)
    for chunk in pd.read_csv(GEOM, usecols=COLS, chunksize=500_000, dtype=str):
        res = chunk[(chunk["unit_usage"] == "RESIDENTIAL") &
                    (chunk["apartment_id"] != MD5_EMPTY)]
        a = res[(res["entity_type"] == "area") &
                (res["entity_subtype"] == "BATHROOM")]
        for fid, wkt in zip(a["floor_id"], a["geometry"]):
            g = from_wkt(wkt)
            if g is not None and not g.is_empty and g.area > 0:
                baths[fid].append(g)
        f = res[(res["entity_type"] == "feature") &
                (res["entity_subtype"].isin(WET_FIXTURES))]
        for fid, st, wkt in zip(f["floor_id"], f["entity_subtype"], f["geometry"]):
            g = from_wkt(wkt)
            if g is not None and not g.is_empty:
                feats[fid].append((st, g.representative_point()))
    return baths, feats


def main() -> None:
    baths, feats = load()
    n_floors = len(baths)
    rows = []  # (area_m2, frozenset(fixtures))
    for fid, polys in baths.items():
        tree = STRtree(polys)
        bag: list[set] = [set() for _ in polys]
        for kind, pt in feats.get(fid, ()):
            for idx in tree.query(pt):
                if polys[idx].contains(pt):
                    bag[idx].add(kind)
                    break
        for poly, fx in zip(polys, bag):
            rows.append((poly.area, frozenset(fx)))

    total = len(rows)
    bathing = {"BATHTUB", "SHOWER"}
    has_bath = [a for a, fx in rows if fx & bathing]
    pan_only = [a for a, fx in rows if not (fx & bathing) and "TOILET" in fx]
    empty = [a for a, fx in rows if not fx]
    other = total - len(has_bath) - len(pan_only) - len(empty)

    print(f"BATHROOM areas on {n_floors} floors: {total}")
    print(f"  with a BATHTUB or SHOWER (a bathroom): {len(has_bath)} "
          f"({100 * len(has_bath) / total:.1f}%)")
    print(f"  TOILET and/or SINK only    (a WC)    : {len(pan_only)} "
          f"({100 * len(pan_only) / total:.1f}%)")
    print(f"  no fixture found (unusable)          : {len(empty)} "
          f"({100 * len(empty) / total:.1f}%)")
    print(f"  sink only, no toilet                 : {other}")
    print()

    def pct(v, q):
        return np.percentile(v, q) if len(v) else float("nan")

    print(f"{'class':28s} {'n':>7} {'p5':>6} {'p25':>6} {'p50':>6} {'p75':>6} {'p95':>6}")
    for label, v in (("bathroom (bath/shower)", has_bath), ("wc (pan only)", pan_only)):
        print(f"{label:28s} {len(v):7d} " +
              " ".join(f"{pct(v, q):6.2f}" for q in (5, 25, 50, 75, 95)))
    print()

    print("Scoring a threshold T: area < T -> wc, area >= T -> bathroom.")
    print(f"{'T (m2)':>8} {'bathrooms called wc':>21} {'wcs called bathroom':>21} {'total wrong':>12}")
    labelled = [(a, True) for a in has_bath] + [(a, False) for a in pan_only]
    n_lab = len(labelled)
    for t in CANDIDATES:
        fn = sum(1 for a, is_bath in labelled if is_bath and a < t)
        fp = sum(1 for a, is_bath in labelled if not is_bath and a >= t)
        print(f"{t:8.1f} {fn:11d} ({100*fn/n_lab:4.1f}%) {fp:11d} ({100*fp/n_lab:4.1f}%)"
              f" {100*(fn+fp)/n_lab:11.1f}%")


if __name__ == "__main__":
    main()
