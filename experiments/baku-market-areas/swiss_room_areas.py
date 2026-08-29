"""Measure Swiss Dwellings v3.0.0 per-room areas by entity_subtype, with site
concentration, so the AZ market_default tier has a MEASURED comparator.

Streams geometries.csv (1.09 GB). Writes JSON to out.json next to this file.
"""
import csv, json, os, sys
from collections import defaultdict
import numpy as np
import shapely

csv.field_size_limit(10**9)

ROOT = r"C:\Users\tng\g2p\bim-engine\data\corpora\swiss-dwellings\swiss-dwellings-v3.0.0"
SRC = os.path.join(ROOT, "geometries.csv")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "swiss_room_areas.json")

# subtype -> list of (area, site_id, apartment_id)
areas = defaultdict(list)
sites = defaultdict(lambda: defaultdict(int))      # subtype -> site -> count
apts = defaultdict(set)                            # subtype -> set(apartment_id)
n_rows = 0
n_area_rows = 0

BATCH = 20000
buf_wkt, buf_meta = [], []

def flush():
    global buf_wkt, buf_meta
    if not buf_wkt:
        return
    geoms = shapely.from_wkt(buf_wkt)
    a = shapely.area(geoms)
    for val, (sub, site, apt) in zip(a, buf_meta):
        areas[sub].append(float(val))
        sites[sub][site] += 1
        apts[sub].add(apt)
    buf_wkt, buf_meta = [], []

with open(SRC, "r", encoding="utf-8", newline="") as f:
    r = csv.DictReader(f)
    for row in r:
        n_rows += 1
        if row["entity_type"] != "area":
            continue
        if row["unit_usage"] != "RESIDENTIAL":
            continue
        n_area_rows += 1
        buf_wkt.append(row["geometry"])
        buf_meta.append((row["entity_subtype"], row["site_id"], row["apartment_id"]))
        if len(buf_wkt) >= BATCH:
            flush()
flush()

res = {"n_rows": n_rows, "n_residential_area_rows": n_area_rows, "types": {}}
for sub, vals in sorted(areas.items(), key=lambda kv: -len(kv[1])):
    v = np.array(vals)
    sc = sites[sub]
    top_site, top_n = max(sc.items(), key=lambda kv: kv[1])
    res["types"][sub] = {
        "n_rooms": int(v.size),
        "n_sites": len(sc),
        "n_apartments": len(apts[sub]),
        "top_site": top_site,
        "top_site_rooms": top_n,
        "top_site_share": round(top_n / v.size, 4),
        "min": round(float(v.min()), 2),
        "p05": round(float(np.percentile(v, 5)), 2),
        "p25": round(float(np.percentile(v, 25)), 2),
        "p50": round(float(np.percentile(v, 50)), 2),
        "p75": round(float(np.percentile(v, 75)), 2),
        "p95": round(float(np.percentile(v, 95)), 2),
        "max": round(float(v.max()), 2),
        "mean": round(float(v.mean()), 2),
    }

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1)
print("rows", n_rows, "residential area rows", n_area_rows, "types", len(res["types"]))
