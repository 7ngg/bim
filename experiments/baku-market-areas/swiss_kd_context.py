"""Second pass: what dwellings do the 41 KITCHEN_DINING rooms live in, and how
rare is the type at dwelling level? Also dwelling-level otaq-ish counts."""
import csv, json, os
from collections import defaultdict, Counter
import numpy as np, shapely

csv.field_size_limit(10**9)
ROOT = r"C:\Users\tng\g2p\bim-engine\data\corpora\swiss-dwellings\swiss-dwellings-v3.0.0"
SRC = os.path.join(ROOT, "geometries.csv")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "swiss_kd_context.json")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

apt = defaultdict(list)   # apartment_id -> [(subtype, area)]
apt_site = {}
BATCH = 20000
bw, bm = [], []
def flush():
    global bw, bm
    if not bw: return
    a = shapely.area(shapely.from_wkt(bw))
    for v, (aid, sub, site) in zip(a, bm):
        apt[aid].append((sub, float(v))); apt_site[aid] = site
    bw, bm = [], []

with open(SRC, "r", encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
        if row["entity_type"] != "area" or row["unit_usage"] != "RESIDENTIAL":
            continue
        bw.append(row["geometry"])
        bm.append((row["apartment_id"], row["entity_subtype"], row["site_id"]))
        if len(bw) >= BATCH: flush()
flush()

# habitable-ish / otaq-ish set, mirroring counts_as_otaq true types
OTAQ = {"ROOM", "BEDROOM", "LIVING_ROOM", "LIVING_DINING", "DINING", "STUDIO"}
INDOOR = {"ROOM","BEDROOM","LIVING_ROOM","LIVING_DINING","DINING","STUDIO","KITCHEN",
          "KITCHEN_DINING","BATHROOM","CORRIDOR","STOREROOM","STAIRCASE","TECHNICAL_AREA"}

kd_apts = [a for a, rs in apt.items() if any(s == "KITCHEN_DINING" for s, _ in rs)]

res = {
  "n_apartments_total": len(apt),
  "n_apartments_with_kitchen_dining": len(kd_apts),
  "share_with_kitchen_dining": round(len(kd_apts)/len(apt), 6),
  "n_sites_with_kitchen_dining": len({apt_site[a] for a in kd_apts}),
  "kd_dwellings": [],
}
for a in kd_apts:
    rs = apt[a]
    res["kd_dwellings"].append({
        "site": apt_site[a],
        "kd_area": round(sum(v for s, v in rs if s == "KITCHEN_DINING"), 2),
        "rooms": sorted([(s, round(v, 1)) for s, v in rs]),
        "indoor_area": round(sum(v for s, v in rs if s in INDOOR), 1),
        "otaq_like": sum(1 for s, _ in rs if s in OTAQ),
        "has_separate_kitchen": any(s == "KITCHEN" for s, _ in rs),
        "has_living": any(s in {"LIVING_ROOM","LIVING_DINING"} for s, _ in rs),
    })
res["kd_dwellings"].sort(key=lambda d: (d["site"], d["kd_area"]))
res["site_counts"] = Counter(apt_site[a] for a in kd_apts).most_common()

# dwelling total indoor area by otaq-like count, all apartments -- the band comparator
by_n = defaultdict(list)
for a, rs in apt.items():
    n = sum(1 for s, _ in rs if s in OTAQ)
    by_n[n].append(sum(v for s, v in rs if s in INDOOR))
res["indoor_area_by_otaq_like"] = {
    str(n): {"n_dwellings": len(v), "p25": round(float(np.percentile(v,25)),1),
             "p50": round(float(np.percentile(v,50)),1),
             "p75": round(float(np.percentile(v,75)),1)}
    for n, v in sorted(by_n.items()) if n <= 6 and len(v) >= 30}
json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
print("apts", len(apt), "kd apts", len(kd_apts))
