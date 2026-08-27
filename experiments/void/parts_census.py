"""Ticket 53 fact-finding, NOT committed. The combinatorial void the ENGINE sees.

`void_census.py` measures uncovered floor against the real dwelling. The engine
never sees the real dwelling -- it sees `parts[]`. So the quantity that decides
this ticket is the enclosed complement of the PARTS frame, which is exactly what
`absolute_area.notch_share` already returns as its second value.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path("experiments/warp").resolve()))
from absolute_area import notch_share, COLLAPSE
from collections import Counter, defaultdict

OUT = Path(__file__).resolve().parent / "out"

FIT = Path("experiments/rectangularise/out/swiss_fit_k2.json")
fits = [r for r in json.load(open(FIT)) if r["status"] in ("OPTIMAL", "FEASIBLE")]
print(f"fits OPTIMAL/FEASIBLE: {len(fits):,}")

rows = []
for f in fits:
    s, v = notch_share(f["parts"])
    bbox_cells = None
    # absolute bbox area in cells so we can turn the share into m2
    x0 = min(p[0] for pl in f["parts"] for p in pl); y0 = min(p[1] for pl in f["parts"] for p in pl)
    x1 = max(p[2] for pl in f["parts"] for p in pl); y1 = max(p[3] for pl in f["parts"] for p in pl)
    bbox_cells = (x1-x0)*(y1-y0)
    rows.append({"k": f["k"], "n": f["n"], "s": s, "void": v,
                 "bbox_m2": bbox_cells*0.0625,
                 "void_m2": v*bbox_cells*0.0625,
                 "worst_iou": min(f["iou"]), "cell_agreement": f["cell_agreement"],
                 "env_loss": f["envelope_loss"]})

def q(v, p):
    s = sorted(v); return s[max(0, min(len(s)-1, int(round(p/100*(len(s)-1)))))]

vs = [r["void"] for r in rows]
vm = [r["void_m2"] for r in rows]
print("\nENCLOSED VOID, share of parts bbox")
print("  p50 %.5f  p75 %.5f  p90 %.5f  p95 %.5f  p99 %.5f  max %.5f"
      % tuple(q(vs,p) for p in (50,75,90,95,99,100)))
print("ENCLOSED VOID, m2")
print("  p50 %.3f  p75 %.3f  p90 %.3f  p95 %.3f  p99 %.3f  max %.3f"
      % tuple(q(vm,p) for p in (50,75,90,95,99,100)))
for t in (0.0, 0.25, 0.5, 1.0, 2.0, 3.0):
    n = sum(1 for x in vm if x > t)
    print("  dwellings with enclosed void > %4.2f m2: %6.2f%%  (%d)" % (t, 100*n/len(vm), n))

print("\nBY ROOM COUNT (share with void > 0.5 m2)")
byn = defaultdict(list)
for r in rows: byn[r["n"]].append(r)
for n in sorted(byn):
    if len(byn[n]) < 30: continue
    g = byn[n]
    print("  n=%2d  N=%5d  >0.5m2 %5.2f%%  void p90 %.3f m2  s p50 %.4f"
          % (n, len(g), 100*sum(1 for r in g if r["void_m2"]>0.5)/len(g),
             q([r["void_m2"] for r in g],90), q([r["s"] for r in g],50)))

print("\nVOID vs FIDELITY PROXIES (is the void already visible to worst-room IoU?)")
for lo, hi in ((0,0.0001),(0.0001,0.25),(0.25,0.5),(0.5,1.0),(1.0,99)):
    g = [r for r in rows if lo <= r["void_m2"] < hi]
    if not g: continue
    print("  void %5.2f-%5.2f m2  N=%5d (%5.2f%%)  worst-IoU p50 %.3f  cell_agree p50 %.3f  env_loss p50 %.3f"
          % (lo, hi, len(g), 100*len(g)/len(rows),
             q([r["worst_iou"] for r in g],50), q([r["cell_agreement"] for r in g],50),
             q([r["env_loss"] for r in g],50)))

print("\nWOULD 47's IoU<0.30 HARD GATE ALREADY REMOVE THEM?")
big = [r for r in rows if r["void_m2"] > 0.5]
print("  of %d dwellings with void > 0.5 m2, %.2f%% have worst-room IoU < 0.30"
      % (len(big), 100*sum(1 for r in big if r["worst_iou"] < 0.30)/max(1,len(big))))
print("  index-wide, %.2f%% have worst-room IoU < 0.30" % (100*sum(1 for r in rows if r["worst_iou"]<0.30)/len(rows)))
OUT.mkdir(exist_ok=True); json.dump(rows, open(OUT / "parts_census.json", "w"))
