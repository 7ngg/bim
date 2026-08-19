"""Is Swiss Dwellings' generic ROOM label usable as a Brief room type?

ROOM is 82,618 of 319,896 kept rooms — 26%, the most common label in the corpus,
and more common than BEDROOM (22,997). A Brief never says "room"; it says bedroom,
study, nursery. If ROOM is an unlabelled bedroom the corpora are usable as-is; if
it is a grab bag, both routes inherit a labelling problem nobody has flagged.

Sampled: first N rows of geometries.csv, areas only.

Run: python experiments/retrieval-coverage/room_label_probe.py
"""

from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from shapely import from_wkt

ROOT = Path(__file__).resolve().parents[2]
GEOM = ROOT / "data" / "corpora" / "swiss-dwellings" / "swiss-dwellings-v3.0.0" / "geometries.csv"
MD5_EMPTY = "d41d8cd98f00b204e9800998ecf8427e"
LIMIT = 4_000_000

areas = defaultdict(list)
seen = 0
for chunk in pd.read_csv(GEOM, usecols=["apartment_id", "unit_usage", "entity_type",
                                        "entity_subtype", "geometry"],
                         chunksize=500_000, dtype=str):
    seen += len(chunk)
    a = chunk[(chunk["entity_type"] == "area") &
              (chunk["unit_usage"] == "RESIDENTIAL") &
              (chunk["apartment_id"] != MD5_EMPTY)]
    for st, wkt in zip(a["entity_subtype"].fillna("<NA>"), a["geometry"]):
        g = from_wkt(wkt)
        if g is not None and not g.is_empty:
            areas[st].append(g.area)
    if seen >= LIMIT:
        break

print(f"sampled {seen:,} rows\n")
print(f"{'subtype':<18}{'n':>8}{'p5':>8}{'p25':>8}{'median':>8}{'p75':>8}{'p95':>8}{'CV':>7}")
for st in sorted(areas, key=lambda s: -len(areas[s])):
    v = np.array(areas[st])
    if len(v) < 50:
        continue
    q = np.percentile(v, [5, 25, 50, 75, 95])
    print(f"{st:<18}{len(v):>8,}" + "".join(f"{x:>8.1f}" for x in q)
          + f"{v.std()/v.mean():>7.2f}")
