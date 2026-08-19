"""Second ResPlan pass: count rooms correctly (multipart geometries), and
work out what units the geometry is actually in."""
import io, pickle, statistics, sys
from collections import Counter
from pathlib import Path
from shapely.geometry.base import BaseMultipartGeometry

ROOT = Path(__file__).resolve().parents[2]
PKL = ROOT / "data" / "corpora" / "resplan" / "ResPlan.pkl"
ALLOWED = {("shapely.io","from_wkb"),("numpy","dtype"),
           ("numpy._core.multiarray","scalar"),("numpy.core.multiarray","scalar")}
class R(pickle.Unpickler):
    def find_class(self, m, n):
        if (m,n) not in ALLOWED: raise pickle.UnpicklingError(f"blocked {m}.{n}")
        return super().find_class(m,n)

def parts(g):
    if g is None: return []
    if isinstance(g,(list,tuple)): return [x for e in g for x in parts(e)]
    if isinstance(g, BaseMultipartGeometry): return [x for x in g.geoms if not x.is_empty]
    return [] if g.is_empty else [g]

plans = R(open(PKL,"rb")).load()
CLASSES = ["living","kitchen","bedroom","bathroom","balcony","garden","parking","pool"]
HABITABLE = ["living","kitchen","bedroom","bathroom"]

hist, hab_hist = Counter(), Counter()
scales, wall_depths, areas = [], [], []
per_class = Counter()
for p in plans:
    n = 0
    for k in CLASSES:
        c = len(parts(p.get(k)))
        per_class[k] += c
        n += c
    hist[n] += 1
    hab_hist[sum(len(parts(p.get(k))) for k in HABITABLE)] += 1
    inner = parts(p.get("inner"))
    if inner and p.get("area"):
        px_area = sum(g.area for g in inner)
        if px_area > 0:
            scales.append((p["area"]/px_area) ** 0.5)   # metres per pixel
    if p.get("wall_depth"): wall_depths.append(float(p["wall_depth"]))
    if p.get("area"): areas.append(float(p["area"]))

print(f"plans: {len(plans)}")
print(f"mean rooms/plan  (8 classes): {sum(k*v for k,v in hist.items())/len(plans):.2f}")
print(f"mean habitable/plan (4 core): {sum(k*v for k,v in hab_hist.items())/len(plans):.2f}")
print(f"rooms/plan histogram: {dict(sorted(hist.items()))}")
print(f"plans with >=16 rooms: {sum(v for k,v in hist.items() if k>=16)}")
print(f"max rooms in any plan: {max(hist)}")
print(f"total room polygons: {sum(per_class.values())}  by class: {dict(per_class)}")
s = statistics.median(scales)
print(f"\nmetres per geometry unit: median {s:.6f}  (min {min(scales):.4f} max {max(scales):.4f})")
print(f"  -> a 256-unit span is {256*s:.2f} m at the median scale")
wd = statistics.median(wall_depths)
print(f"wall_depth: median {wd:.3f} units = {wd*s*100:.1f} cm at median scale")
print(f"area m2: median {statistics.median(areas):.1f}  mean {statistics.mean(areas):.1f}")
# rectangularity, on a sample
import itertools
rect = tot = 0
for p in itertools.islice(plans, 2000):
    for k in CLASSES:
        for g in parts(p.get(k)):
            tot += 1
            if g.area > 0 and abs(g.area - g.envelope.area) / g.envelope.area < 0.02: rect += 1
print(f"rectangular room polygons (2% tol, first 2000 plans): {rect}/{tot} = {100*rect/tot:.1f}%")
