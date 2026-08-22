"""A WC's area, from fixtures rather than from an area threshold.

recommend.py (F) returned a `wc` cap of 2.40 m2 at p95, p99, p99.5 AND p99.9.
That is not a measurement. The reporting class `wc` is DEFINED as
`BATHROOM area < 2.4` -- `ergonomic.corpus_label_split`'s fitted splitter -- so
the class is truncated at 2.4 by construction and any percentile of it returns
the splitter back. A cap fitted that way would be circular.

Swiss Dwellings carries BATHTUB / SHOWER / TOILET / SINK point features, which is
how `experiments/region-profile/bathroom_fixture_split.py` fitted the splitter in
the first place. This re-reads that ground truth for the UPPER tail, restricted to
the same in-band (4-10 room) dwellings as the rest of ticket 37, and asks how big
a real toilet-only room actually gets.

ResPlan cannot be corrected the same way: it carries a `bathroom` label and no
fixtures at all, so every ResPlan `wc` figure in this ticket is the splitter and
is reported as unusable rather than quoted.

Run: python experiments/room-area-bands/wc_fixture_truth.py
"""
import collections
import json
from pathlib import Path

import numpy as np
import pandas as pd
from shapely import from_wkt
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parents[2]
GEOM = ROOT / "data" / "corpora" / "swiss-dwellings" / "swiss-dwellings-v3.0.0" / "geometries.csv"
RECT_OUT = ROOT / "experiments" / "rectangularise" / "out"
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)

MD5_EMPTY = "d41d8cd98f00b204e9800998ecf8427e"
WET = {"BATHTUB", "SHOWER", "TOILET", "SINK", "WASHING_MACHINE"}
COLS = ["site_id", "apartment_id", "floor_id", "unit_usage",
        "entity_type", "entity_subtype", "geometry"]
PCTS = [5, 25, 50, 75, 90, 95, 99, 99.5, 99.9]


def main():
    in_band = {r["k"] for r in json.load(open(RECT_OUT / "swiss_rects.json"))["recs"]}
    print(f"in-band dwellings: {len(in_band)}", flush=True)

    baths = collections.defaultdict(list)   # floor_id -> [(key, poly)]
    feats = collections.defaultdict(list)   # floor_id -> [(kind, point)]
    for chunk in pd.read_csv(GEOM, usecols=COLS, chunksize=500_000, dtype=str):
        res = chunk[(chunk["unit_usage"] == "RESIDENTIAL") &
                    (chunk["apartment_id"] != MD5_EMPTY)]
        a = res[(res["entity_type"] == "area") &
                (res["entity_subtype"] == "BATHROOM")]
        for s, f, ap, wkt in zip(a["site_id"], a["floor_id"], a["apartment_id"],
                                 a["geometry"]):
            key = f"{s}|{f}|{ap}"
            if key not in in_band:
                continue
            g = from_wkt(wkt)
            if g is not None and not g.is_empty and g.area > 0:
                baths[f].append((key, g))
        fx = res[(res["entity_type"] == "feature") &
                 (res["entity_subtype"].isin(WET))]
        for f, st, wkt in zip(fx["floor_id"], fx["entity_subtype"], fx["geometry"]):
            g = from_wkt(wkt)
            if g is not None and not g.is_empty:
                feats[f].append((st, g.representative_point()))

    rows = []
    for fid, items in baths.items():
        polys = [g for _, g in items]
        tree = STRtree(polys)
        bag = [set() for _ in polys]
        for kind, pt in feats.get(fid, ()):
            for idx in tree.query(pt):
                if polys[idx].contains(pt):
                    bag[idx].add(kind)
                    break
        for (key, g), fxs in zip(items, bag):
            rows.append((g.area, frozenset(fxs)))

    bathing = {"BATHTUB", "SHOWER"}
    has_bath = np.array([a for a, fx in rows if fx & bathing])
    pan_only = np.array([a for a, fx in rows if not (fx & bathing) and "TOILET" in fx])
    unlabelled = [a for a, fx in rows if not fx]

    lines = []

    def w(s=""):
        print(s)
        lines.append(s)

    w()
    w("WC AND BATHROOM AREA FROM FIXTURE GROUND TRUTH")
    w(f"  in-band BATHROOM rooms: {len(rows)}")
    w(f"    bathroom (BATHTUB or SHOWER present): {len(has_bath)} "
      f"({100*len(has_bath)/len(rows):.1f}%)")
    w(f"    wc       (TOILET, no bathing fixture): {len(pan_only)} "
      f"({100*len(pan_only)/len(rows):.1f}%)")
    w(f"    no fixture found, unusable           : {len(unlabelled)} "
      f"({100*len(unlabelled)/len(rows):.1f}%)")
    w()
    w("  %-10s %7s | %s" % ("class", "n", " ".join("%7s" % f"p{p}" for p in PCTS) + "     max"))
    for label, v in (("bathroom", has_bath), ("wc", pan_only)):
        w("  %-10s %7d | %s %7.2f"
          % (label, len(v), " ".join("%7.2f" % np.percentile(v, p) for p in PCTS),
             v.max()))
    w()
    w("  Threshold-split (area < 2.4) for comparison -- the circular figure:")
    thr_wc = np.array([a for a, _ in rows if a < 2.4])
    w("  %-10s %7d | %s %7.2f"
      % ("wc (thr)", len(thr_wc),
         " ".join("%7.2f" % np.percentile(thr_wc, p) for p in PCTS), thr_wc.max()))
    w()
    w("  Overlap the splitter cannot see:")
    w(f"    real WCs at or above 2.4 m2 : {(pan_only >= 2.4).sum()} "
      f"({100*(pan_only >= 2.4).mean():.1f}% of real WCs)")
    w(f"    real WCs above 4.0 m2       : {(pan_only > 4.0).sum()} "
      f"({100*(pan_only > 4.0).mean():.2f}%)")
    w(f"    real bathrooms below 2.4 m2 : {(has_bath < 2.4).sum()} "
      f"({100*(has_bath < 2.4).mean():.1f}% of real bathrooms)")

    (OUT / "wc_fixture_truth.txt").write_text("\n".join(lines), encoding="utf-8")
    json.dump({"wc_pan_only": {f"p{p}": float(np.percentile(pan_only, p)) for p in PCTS},
               "bathroom_fixture": {f"p{p}": float(np.percentile(has_bath, p)) for p in PCTS},
               "n_wc": len(pan_only), "n_bathroom": len(has_bath)},
              open(OUT / "wc_fixture_truth.json", "w"), indent=1)
    print(f"\nwrote {OUT/'wc_fixture_truth.txt'}")


if __name__ == "__main__":
    main()
