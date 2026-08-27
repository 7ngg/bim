"""Ticket 53, the decisive arm. Three treatments of the enclosed void in the warp:

  free      what ships. The void is in the objective at weight zero, so it is
            where slack goes for free.
  weighted  penalise its area. Removes the amplification, buys nothing else.
  charged   the void's area is added to its RECEIVING Room's area sum, so the
            Room's deviation is measured on what it will actually hold once the
            solver closes the hole (H3, exact tiling). The void stops being
            unowned the moment it belongs to somebody -- no weight, no free
            parameter, one line.
"""
import json, random, sys
from collections import Counter
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path("experiments/warp").resolve()))
from ortools.sat.python import cp_model
import fit_warp as FW
import absolute_area as A

ASPECT_HARD, JOIN = FW.ASPECT_HARD, FW.JOIN_UNITS
CFG = {"mode": "free", "voids": [], "recv": []}

def void_spans_and_receiver(parts):
    """Enclosed complement components as frame spans, each with the bordering
    Room holding the largest share of its perimeter -- the best rule derivable
    from the Proposal alone (28.4% donor-faithful; the donor's own owner is
    recorded in the index and is what the engine uses)."""
    xs, ys, spans = A.coord_frame(parts)
    nx, ny = len(xs)-1, len(ys)-1
    occ = np.full((ny, nx), -1, dtype=np.int16)
    for ri, pl in enumerate(spans):
        for (a, b, c, d) in pl: occ[c:d, a:b] = ri
    free = occ < 0
    seen = np.zeros_like(free); out = []
    for y in range(ny):
        for x in range(nx):
            if free[y, x] and not seen[y, x]:
                st=[(y,x)]; seen[y,x]=True; cells=[]
                while st:
                    p,q=st.pop(); cells.append((p,q))
                    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        u,v=p+dy,q+dx
                        if 0<=u<ny and 0<=v<nx and free[u,v] and not seen[u,v]:
                            seen[u,v]=True; st.append((u,v))
                yy=[c[0] for c in cells]; xx=[c[1] for c in cells]
                if min(yy)==0 or max(yy)==ny-1 or min(xx)==0 or max(xx)==nx-1: continue
                share=Counter()
                for cy,cx in cells:
                    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        u,v=cy+dy,cx+dx
                        if 0<=u<ny and 0<=v<nx and occ[u,v]>=0: share[occ[u,v]]+=1
                if not share: continue
                out.append(((min(xx),max(xx)+1,min(yy),max(yy)+1),
                            max(share, key=lambda r:(share[r], r))))
    return out

def warp_model_v(spans, nx, ny, targets, W, H, weights, min_side,
                 joins_x, joins_y, tlim, aspect=True, seed=None):
    m = cp_model.CpModel()
    gx=[m.NewIntVar(1,W,f"gx{i}") for i in range(nx)]
    gy=[m.NewIntVar(1,H,f"gy{j}") for j in range(ny)]
    m.Add(sum(gx)==W); m.Add(sum(gy)==H)
    for lo,hi in joins_x:
        if hi>lo: m.Add(sum(gx[lo:hi])>=JOIN)
    for lo,hi in joins_y:
        if hi>lo: m.Add(sum(gy[lo:hi])>=JOIN)
    vareas={}
    for (a,b,c,d), recv in CFG["voids"]:
        wv=m.NewIntVar(1,W,f"vw{a}_{c}"); hv=m.NewIntVar(1,H,f"vh{a}_{c}")
        m.Add(wv==sum(gx[a:b])); m.Add(hv==sum(gy[c:d]))
        av=m.NewIntVar(1,W*H,f"va{a}_{c}"); m.AddMultiplicationEquality(av,[wv,hv])
        vareas.setdefault(recv,[]).append(av)
    devs=[]
    for r,parts in enumerate(spans):
        areas=[]
        for p,(a,b,c,d) in enumerate(parts):
            wv=m.NewIntVar(1,W,f"w{r}_{p}"); hv=m.NewIntVar(1,H,f"h{r}_{p}")
            m.Add(wv==sum(gx[a:b])); m.Add(hv==sum(gy[c:d]))
            m.Add(wv>=min_side[r]); m.Add(hv>=min_side[r])
            if aspect:
                m.Add(wv<=ASPECT_HARD*hv); m.Add(hv<=ASPECT_HARD*wv)
            av=m.NewIntVar(1,W*H,f"a{r}_{p}"); m.AddMultiplicationEquality(av,[wv,hv])
            areas.append(av)
        if CFG["mode"] in ("charged", "both"):
            areas += vareas.get(r, [])          # <-- THE ONE LINE
        area=sum(areas)
        e=m.NewIntVar(0,20_000,f"e{r}")
        m.Add(e*targets[r] >= 1000*(area-targets[r]))
        m.Add(e*targets[r] >= 1000*(targets[r]-area))
        devs.append(e)
    worst=m.NewIntVar(0,20_000,"worst"); m.AddMaxEquality(worst,devs)
    obj = worst*(1000*len(devs)) + sum(weights[r]*d for r,d in enumerate(devs))
    if CFG["mode"] in ("weighted", "both"):
        allv=[a for v in vareas.values() for a in v]
        if allv: obj = obj + 2000*sum(allv)
    m.Minimize(obj)
    if seed:
        sx,sy=seed
        for v,val in zip(gx,sx): m.AddHint(v,val)
        for v,val in zip(gy,sy): m.AddHint(v,val)
    s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=tlim; s.parameters.num_workers=1
    st=s.Solve(m); name=s.StatusName(st)
    if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE): return None,name
    return ([s.Value(v) for v in gx],[s.Value(v) for v in gy],st==cp_model.OPTIMAL),name

A.warp_model=warp_model_v
CAP={}; _o=A.rects_mm
def spy(sp,gx,gy):
    out=_o(sp,gx,gy); CAP["rects"]=out; return out
A.rects_mm=spy

fits=[r for r in json.load(open("experiments/rectangularise/out/swiss_fit_k2.json"))
      if r["status"] in ("OPTIMAL","FEASIBLE")]
recs={r["k"]:r for r in json.load(open("experiments/warp/out/dwelling_rooms.json"))}
cands=[]
for f in fits:
    r=recs.get(f["k"])
    if not r or f["n"]!=r["n"]: continue
    c=dict(f); c.update(area=r["area"],aspect=r["aspect"],rooms=r["rooms"],k=f["k"])
    s,v=A.notch_share(f["parts"]); c["s"],c["void"]=s,v
    cands.append(c)
voided=[c for c in cands if c["void"]>0]
rng=random.Random(20260819); sample=rng.sample(voided,90)
def q(v,p):
    if not v: return float("nan")
    s=sorted(v); return s[max(0,min(len(s)-1,int(round(p/100*(len(s)-1)))))]
print(f"{len(sample)} voided candidates, self-paired targets, 1.5 s cap\n")
for mode in ("free", "weighted", "charged", "both"):
    CFG["mode"]=mode
    rv,dv,st=[],[],Counter()
    for c in sample:
        CFG["voids"]=void_spans_and_receiver(c["parts"])
        CAP.clear()
        r=A.run_one(c,c["aspect"],[a for _,a in c["rooms"]],1.5,key=c["k"],hold_ring=False)
        st[r["status"]]+=1
        if r["status"]!="OK" or "rects" not in CAP: continue
        parts=[[[int(x//250) for x in p] for p in pl] for pl in CAP["rects"]]
        _s2,v2=A.notch_share(parts)
        bb=((max(p[2] for pl in CAP["rects"] for p in pl)-min(p[0] for pl in CAP["rects"] for p in pl))
           *(max(p[3] for pl in CAP["rects"] for p in pl)-min(p[1] for pl in CAP["rects"] for p in pl)))/1e6
        rv.append(v2*bb)
        dv.append(max(abs(g-t)/t for g,t in zip(r["got"],r["targets"]) if t>0))
    print("%-9s realised void m2 p50 %.3f p90 %.3f max %.3f | worst-room dev p50 %.4f p90 %.4f | %s"
          % (mode,q(rv,50),q(rv,90),q(rv,100),q(dv,50),q(dv,90),dict(st)))
