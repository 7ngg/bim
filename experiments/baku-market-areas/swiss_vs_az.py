"""Third pass: for each AZ market_default cell, what share of the real Swiss
retrieval pool sits BELOW the target the solver aims at."""
import csv, json, os
from collections import defaultdict
import numpy as np, shapely
csv.field_size_limit(10**9)
ROOT = r"C:\Users\tng\g2p\bim-engine\data\corpora\swiss-dwellings\swiss-dwellings-v3.0.0"
SRC = os.path.join(ROOT, "geometries.csv")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "swiss_vs_az.json")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
KEEP = {"ROOM","BEDROOM","LIVING_ROOM","LIVING_DINING","DINING","KITCHEN",
        "KITCHEN_DINING","BATHROOM","STUDIO"}
vals = defaultdict(list)
bw, bm = [], []
def flush():
    global bw, bm
    if not bw: return
    for v, s in zip(shapely.area(shapely.from_wkt(bw)), bm): vals[s].append(float(v))
    bw, bm = [], []
with open(SRC, "r", encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
        if row["entity_type"]!="area" or row["unit_usage"]!="RESIDENTIAL": continue
        if row["entity_subtype"] not in KEEP: continue
        bw.append(row["geometry"]); bm.append(row["entity_subtype"])
        if len(bw)>=20000: flush()
flush()
# AZ market_default targets against the Swiss classes they would be applied to
CHECK = [("living_room_2plus", 16.0, ["LIVING_ROOM"]),
         ("living_room_2plus", 16.0, ["LIVING_DINING"]),
         ("bedroom_single", 9.0, ["ROOM","BEDROOM"]),
         ("bedroom_double", 12.0, ["ROOM","BEDROOM"]),
         ("kitchen", 9.0, ["KITCHEN"]),
         ("kitchen_zone_in_diner", 6.0, ["KITCHEN_DINING"]),
         ("bathroom", 3.2, ["BATHROOM"]),
         ("bathroom_combined", 3.8, ["BATHROOM"])]
res = {}
for name, t, cls in CHECK:
    a = np.array(sum((vals[c] for c in cls), []))
    res[f"{name} vs {'+'.join(cls)}"] = {
        "az_market_default": t, "n": int(a.size),
        "swiss_p50": round(float(np.median(a)),2),
        "share_below_target": round(float((a < t).mean()),4),
        "target_percentile_in_pool": round(float((a < t).mean()*100),2),
        "ratio_p50_over_target": round(float(np.median(a))/t, 2)}
json.dump(res, open(OUT,"w"), indent=1)
print(json.dumps(res, indent=1))
