"""Can the warp CREATE a void in a donor that had none? If it can, gating the
donor buys nothing. Combinatorially it cannot -- every gap is >= 1 cell and the
frame's incidence is fixed -- but that is an argument and this is the check."""
import json, random, sys
from pathlib import Path
sys.path.insert(0, str(Path("experiments/warp").resolve()))
import absolute_area as A
CAP={}; _o=A.rects_mm
def spy(sp,gx,gy):
    out=_o(sp,gx,gy); CAP["rects"]=out; return out
A.rects_mm=spy
fits=[r for r in json.load(open("experiments/rectangularise/out/swiss_fit_k2.json")) if r["status"] in ("OPTIMAL","FEASIBLE")]
recs={r["k"]:r for r in json.load(open("experiments/warp/out/dwelling_rooms.json"))}
cands=[]
for f in fits:
    r=recs.get(f["k"])
    if not r or f["n"]!=r["n"]: continue
    c=dict(f); c.update(area=r["area"],aspect=r["aspect"],rooms=r["rooms"],k=f["k"])
    s,v=A.notch_share(f["parts"]); c["s"],c["void"]=s,v; cands.append(c)
clean=[c for c in cands if c["void"]==0]
rng=random.Random(20260819); sample=rng.sample(clean,60)
grew=0; ok=0; worst=0.0
for c in sample:
    CAP.clear()
    r=A.run_one(c,c["aspect"],[a for _,a in c["rooms"]],1.0,key=c["k"],hold_ring=False)
    if r["status"]!="OK" or "rects" not in CAP: continue
    ok+=1
    parts=[[[int(v//250) for v in q] for q in pl] for pl in CAP["rects"]]
    s2,v2=A.notch_share(parts)
    if v2>0:
        grew+=1; worst=max(worst,v2)
print(f"{ok} clean donors warped: {grew} acquired an enclosed void (worst share {worst:.5f})")
