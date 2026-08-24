"""PROTOTYPE PROBE — at which exposure does make_brief stop finding a
room-type assignment, per room count? Fast: Brief construction only, no solve."""
import os, sys
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,"..","solver-toy"))
from scenarios import scenario
EXPS=["detached","terrace_mid","flat_corner","corpus_median","flat_single_aspect"]
print(f"{'n':>3} " + " ".join(f"{e:>19}" for e in EXPS))
for n in range(4,11):
    cells=[]
    for e in EXPS:
        ok=0
        for seed in (20260817,991,4242,77,1234):
            try: scenario(n,seed=seed,exposure=e); ok+=1
            except Exception: pass
        cells.append(f"{ok}/5")
    print(f"{n:>3} " + " ".join(f"{c:>19}" for c in cells))
