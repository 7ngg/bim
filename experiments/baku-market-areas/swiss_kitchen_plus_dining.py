"""A defensible proxy for a `metbex-yemek otagi`, since Swiss KITCHEN_DINING is
not one (see the findings note SS4.1).

A metbex-yemek otagi IS the kitchen and IS the dining room. The ergonomic key
`kitchen_dining` is likewise "packed from kitchen and dining". So the corpus
question that matches the object is: in dwellings that have BOTH a KITCHEN and a
DINING room, what does KITCHEN + DINING sum to? That is the area a single room
would have to hold to do both jobs.

Reported alongside it, as an upper reference, the dwellings' LIVING_DINING, which
is the corpus's own large combined-use room.
"""
import csv, json, os
from collections import defaultdict
import numpy as np, shapely

csv.field_size_limit(10**9)
ROOT = r"C:\Users\tng\g2p\bim-engine\data\corpora\swiss-dwellings\swiss-dwellings-v3.0.0"
SRC = os.path.join(ROOT, "geometries.csv")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "swiss_kitchen_plus_dining.json")
KEEP = {"KITCHEN", "DINING", "LIVING_DINING", "KITCHEN_DINING"}

apt = defaultdict(lambda: defaultdict(float))
apt_site, bw, bm = {}, [], []

def flush():
    global bw, bm
    if not bw:
        return
    for v, (aid, sub, site) in zip(shapely.area(shapely.from_wkt(bw)), bm):
        apt[aid][sub] += float(v)
        apt_site[aid] = site
    bw, bm = [], []

with open(SRC, "r", encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
        if row["entity_type"] != "area" or row["unit_usage"] != "RESIDENTIAL":
            continue
        if row["entity_subtype"] not in KEEP:
            continue
        bw.append(row["geometry"])
        bm.append((row["apartment_id"], row["entity_subtype"], row["site_id"]))
        if len(bw) >= 20000:
            flush()
flush()

def stats(vals, sites):
    a = np.array(vals)
    from collections import Counter
    c = Counter(sites)
    top, topn = c.most_common(1)[0]
    return {"n_dwellings": int(a.size), "n_sites": len(c),
            "top_site": top, "top_site_share": round(topn / a.size, 4),
            "min": round(float(a.min()), 2),
            "p25": round(float(np.percentile(a, 25)), 2),
            "p50": round(float(np.median(a)), 2),
            "p75": round(float(np.percentile(a, 75)), 2),
            "p95": round(float(np.percentile(a, 95)), 2),
            "max": round(float(a.max()), 2)}

res = {}
both = [(a, r) for a, r in apt.items() if r.get("KITCHEN") and r.get("DINING")]
res["kitchen_plus_dining_sum"] = stats([r["KITCHEN"] + r["DINING"] for _, r in both],
                                       [apt_site[a] for a, _ in both])
res["kitchen_only_in_those"] = stats([r["KITCHEN"] for _, r in both],
                                     [apt_site[a] for a, _ in both])
res["dining_only_in_those"] = stats([r["DINING"] for _, r in both],
                                    [apt_site[a] for a, _ in both])
ld = [(a, r) for a, r in apt.items() if r.get("LIVING_DINING")]
res["living_dining_reference"] = stats([r["LIVING_DINING"] for _, r in ld],
                                       [apt_site[a] for a, _ in ld])
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
