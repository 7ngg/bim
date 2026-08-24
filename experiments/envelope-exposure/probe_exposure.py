"""Brief feasibility over exposure x room count.

Counts, per cell, how many of five seeds produce a **Brief at all** --
`scenarios.make_brief`'s CP-SAT room-type assignment, which must satisfy H8
(every habitable room touches an exterior wall over a window's width) together
with wet clustering and circulation. This is UPSTREAM of the solve, so nothing
here is a timing result.

The result the map rests on: the failure is **not monotone in n**.
`flat_single_aspect` fails at 6, 7 and 8, mostly fails at 9, and succeeds at 10
-- which is where `scenarios.envelope_for` switches from an L to a U and the
second notch adds exterior run on the one live edge. So a claim of the form
"dead from n rooms" is measuring the envelope that n selects, not n.

Caveat the map carries with it: this is the toy's own minima and its own
generator, not the shipped ergonomic layer. It corroborates a direction and
settles no number.

Run:  ../../venv/Scripts/python.exe probe_exposure.py
"""
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
