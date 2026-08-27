"""Ticket 53: can the solver DERIVE the void's owner from the Proposal alone?

If it can, zoning's precedent binds -- "the node set is derivable, so there is
nothing the Proposal could add" -- and a contract field must be refused. Three
candidate derivable rules, scored against the donor's own watershed ownership.
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

def comps(mask):
    ny,nx=mask.shape; seen=np.zeros_like(mask); out=[]
    for y in range(ny):
        for x in range(nx):
            if mask[y,x] and not seen[y,x]:
                st=[(y,x)]; seen[y,x]=True; cells=[]
                while st:
                    a,b=st.pop(); cells.append((a,b))
                    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        p,q=a+dy,b+dx
                        if 0<=p<ny and 0<=q<nx and mask[p,q] and not seen[p,q]:
                            seen[p,q]=True; st.append((p,q))
                out.append(cells)
    return out

dw,_=pickle.load(open("experiments/rectangularise/out/swiss_dw.pkl","rb"))
fits=[r for r in json.load(open("experiments/rectangularise/out/swiss_fit_k2.json"))
      if r["status"] in ("OPTIMAL","FEASIBLE")]
n=0; agree_edge=0; agree_small=0; agree_big=0; ties=0; done=0
for rec in fits:
    parts=rec.get("parts") or [[r] for r in rec["rects"]]
    s,v=notch_share(parts)
    if v<=0: continue
    items=dw.get(tuple(rec["k"].split("|")))
    if items is None: continue
    geoms=[_poly(from_wkt(w)) for _st,w in items]
    geoms=[g for g in geoms if g is not None and g.area>=MIN_ROOM_AREA]
    if not geoms: continue
    lab,x0,y0=watershed(geoms)
    if lab is None: continue
    lab=keep_largest_component(lab)
    env,_nt,_i,(oy,ox)=envelope_approx(lab>=0)
    ny,nx=env.shape; L=lab[oy:oy+ny,ox:ox+nx]
    covered=np.zeros(env.shape,dtype=bool)
    for ri,pl in enumerate(parts):
        for a,b,c,d in pl: covered[b:d,a:c]=True
    unc=env&~covered
    edge=np.zeros(env.shape,dtype=bool); edge[0,:]=edge[-1,:]=True; edge[:,0]=edge[:,-1]=True
    pad=np.pad((~env)|edge,1,constant_values=True)
    touch=(pad[:-2,1:-1]|pad[2:,1:-1]|pad[1:-1,:-2]|pad[1:-1,2:])
    done+=1
    if done>500: break
    room_area={ri:sum((c-a)*(d-b) for a,b,c,d in pl) for ri,pl in enumerate(parts)}
    for cells in comps(unc):
        m=np.zeros(env.shape,dtype=bool)
        for cy,cx in cells: m[cy,cx]=True
        if (m&touch).any(): continue
        labs=[L[cy,cx] for cy,cx in cells if L[cy,cx]>=0]
        if not labs: continue
        truth=Counter(labs).most_common(1)[0][0]
        if truth>=len(parts): continue
        # shared edge length with each Room, in cells
        share=Counter()
        for cy,cx in cells:
            for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                p,q=cy+dy,cx+dx
                if 0<=p<ny and 0<=q<nx and covered[p,q]:
                    for ri,pl in enumerate(parts):
                        if any(a<=q<c and b<=p<d for a,b,c,d in pl):
                            share[ri]+=1; break
        if not share: continue
        n+=1
        top=max(share.values())
        winners=[r for r,c in share.items() if c==top]
        ties += len(winners)>1
        agree_edge += truth in winners and len(winners)==1
        nb=list(share)
        agree_small += (min(nb,key=lambda r:room_area[r])==truth)
        agree_big   += (max(nb,key=lambda r:room_area[r])==truth)
print(f"{n} enclosed void components with a donor owner, over {done} dwellings")
print(f"  derivable rule 'largest shared edge'  agrees with the donor: {100*agree_edge/n:.1f}%"
      f"   (ambiguous ties in {100*ties/n:.1f}% of components)")
print(f"  derivable rule 'smallest bordering Room'                  : {100*agree_small/n:.1f}%")
print(f"  derivable rule 'largest bordering Room'                   : {100*agree_big/n:.1f}%")
