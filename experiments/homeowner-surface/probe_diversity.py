"""PROTOTYPE PROBE — how different are four survivors of ONE Brief, by exposure?

The map's *Variant generation and ranking* patch carries a "deliberately
unpatched asymmetry": a stated Envelope gets no diversity axis, so flats get
less variety than bungalows. This measures it on the same Brief.

Metric: rasterise each solved layout on the 250 mm grid, label every interior
cell with its room KIND, and take the mean pairwise fraction of cells whose
kind differs. 0 = identical layouts, 1 = nothing in common.
"""
import os, sys, itertools
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,"..","solver-toy"))
from scenarios import scenario
from solver import SolveConfig, project

SEEDS=(20260817,991,4242,77,1234,5150)

def label_grid(env, rooms, kinds):
    g={}
    for r,k in zip(rooms,kinds):
        for x in range(r.x1,r.x2):
            for y in range(r.y1,r.y2): g[(x,y)]=k
    return g

def run(n, exposure):
    grids=[]
    for seed in SEEDS:
        try: brief,truth,prop = scenario(n,seed=seed,exposure=exposure)
        except Exception: continue
        res = project(brief, prop, SolveConfig(time_limit_s=6))
        if not res.rooms: continue
        grids.append(label_grid(brief.env,res.rooms,[s.kind for s in brief.rooms]))
    if len(grids)<2: return None,len(grids)
    ds=[]
    for a,b in itertools.combinations(grids,2):
        keys=set(a)|set(b)
        ds.append(sum(1 for k in keys if a.get(k)!=b.get(k))/len(keys))
    return sum(ds)/len(ds), len(grids)

print(f"{'n':>3} {'exposure':>20} {'survivors':>10} {'mean pairwise difference':>26}")
for n in (5,7):
    for e in ("detached","corpus_median"):
        d,k = run(n,e)
        print(f"{n:>3} {e:>20} {k:>10} {('%.3f'%d) if d is not None else '  n/a':>26}")
