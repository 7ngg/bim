"""Ticket 53: does the void have a KNOWN OWNER, and does absorption return it?

The watershed labels every 250 mm cell with the donor Room that owns it, so a
void component is not anonymous floor -- the real dwelling says whose it was.
Two questions the answer turns on:
  A. is a void component's donor ownership CLEAN (one Room owns most of it)?
  B. when a part can absorb it, is that part the SAME Room the donor gave it to?
If A and B are high, absorption is a restoration. If B is low, "grow whatever
fits" is inventing, and the arbitrariness we just criticised in the solver is
merely moved one layer upstream.
"""
import json, sys, pickle
from collections import Counter
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path("experiments/rectangularise").resolve()))
sys.path.insert(0, str(Path("experiments/warp").resolve()))
from shapely import from_wkt
from measure_swiss import _poly, MIN_ROOM_AREA
from fit_rects import watershed, keep_largest_component, envelope_approx
from absolute_area import notch_share

ASPECT = 3.02
def comps(mask):
    ny, nx = mask.shape; seen = np.zeros_like(mask); out = []
    for y in range(ny):
        for x in range(nx):
            if mask[y, x] and not seen[y, x]:
                st=[(y,x)]; seen[y,x]=True; cells=[]
                while st:
                    a,b=st.pop(); cells.append((a,b))
                    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        p,q=a+dy,b+dx
                        if 0<=p<ny and 0<=q<nx and mask[p,q] and not seen[p,q]:
                            seen[p,q]=True; st.append((p,q))
                out.append(cells)
    return out

dw, keys = pickle.load(open("experiments/rectangularise/out/swiss_dw.pkl", "rb"))
fits = [r for r in json.load(open("experiments/rectangularise/out/swiss_fit_k2.json"))
        if r["status"] in ("OPTIMAL", "FEASIBLE")]

clean=[]; n_comp=0; absorbable=0; faithful=0; done=0
for rec in fits:
    parts = rec.get("parts") or [[r] for r in rec["rects"]]
    s, v = notch_share(parts)
    if v <= 0: continue
    items = dw.get(tuple(rec["k"].split("|")))
    if items is None: continue
    geoms=[_poly(from_wkt(w)) for _st,w in items]
    geoms=[g for g in geoms if g is not None and g.area>=MIN_ROOM_AREA]
    if not geoms: continue
    lab,x0,y0 = watershed(geoms)
    if lab is None: continue
    lab = keep_largest_component(lab)
    env,notches,info,(oy,ox) = envelope_approx(lab>=0)
    ny,nx = env.shape
    L = lab[oy:oy+ny, ox:ox+nx]
    covered=np.zeros(env.shape,dtype=bool)
    owner=np.full(env.shape,-1,dtype=np.int16)
    for ri,pl in enumerate(parts):
        for a,b,c,d in pl:
            covered[b:d,a:c]=True; owner[b:d,a:c]=ri
    unc = env & ~covered
    edge=np.zeros(env.shape,dtype=bool); edge[0,:]=edge[-1,:]=True; edge[:,0]=edge[:,-1]=True
    pad=np.pad((~env)|edge,1,constant_values=True)
    touch=(pad[:-2,1:-1]|pad[2:,1:-1]|pad[1:-1,:-2]|pad[1:-1,2:])
    done+=1
    if done>500: break
    for cells in comps(unc):
        m=np.zeros(env.shape,dtype=bool)
        for cy,cx in cells: m[cy,cx]=True
        if (m&touch).any(): continue
        n_comp+=1
        labs=[L[cy,cx] for cy,cx in cells if L[cy,cx]>=0]
        if not labs: continue
        c0=Counter(labs).most_common(1)[0]
        clean.append(c0[1]/len(cells))
        # can one part absorb it, and is that part the donor owner's part?
        ys=[c[0] for c in cells]; xs=[c[1] for c in cells]
        vy0,vy1,vx0,vx1=min(ys),max(ys)+1,min(xs),max(xs)+1
        if len(cells)!=(vy1-vy0)*(vx1-vx0): continue
        hit=None
        for ri,pl in enumerate(parts):
            for (a,b,c,d) in pl:
                g=None
                if b==vy0 and d==vy1:
                    if c==vx0: g=(a,b,vx1,d)
                    elif a==vx1: g=(vx0,b,c,d)
                if a==vx0 and c==vx1:
                    if d==vy0: g=(a,b,c,vy1)
                    elif b==vy1: g=(a,vy0,c,d)
                if g is None: continue
                w,h=g[2]-g[0],g[3]-g[1]
                if max(w,h)/min(w,h)>ASPECT: continue
                hit=ri; break
            if hit is not None: break
        if hit is None: continue
        absorbable+=1
        # the DONOR room index that owns the void, mapped through the fit's room order
        faithful += (hit == c0[0]) if c0[0] < len(parts) else 0

def q(v,p):
    s=sorted(v); return s[max(0,min(len(s)-1,int(round(p/100*(len(s)-1)))))]
print(f"{done} voided dwellings, {n_comp} enclosed void components")
print("A. donor ownership purity (share of the component's cells owned by ONE donor Room)")
print("   p10 %.2f  p50 %.2f  p90 %.2f   >=0.80 in %.1f%% of components"
      % (q(clean,10),q(clean,50),q(clean,90),100*sum(1 for c in clean if c>=0.80)/len(clean)))
print(f"B. of {absorbable} single-part-absorbable components, {faithful} "
      f"({100*faithful/max(1,absorbable):.1f}%) are absorbed by the SAME Room the donor gave it to")
