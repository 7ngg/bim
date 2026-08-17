import time
from scenarios import scenario, Proposal
from solver import SolveConfig, LayoutProjector
from validate import check
from ortools.sat.python import cp_model

# Does the model admit the KNOWN-GOOD ground truth? If not, the model is wrong.
for n in (8,12,24):
    b,t,p = scenario(n)
    cfg = SolveConfig(time_limit_s=30, workers=4, hint=False)
    lp = LayoutProjector(b, p, cfg)
    m = lp.m
    for i,r in enumerate(t):
        m.Add(lp.x1[i]==r.x1); m.Add(lp.x2[i]==r.x2)
        m.Add(lp.y1[i]==r.y1); m.Add(lp.y2[i]==r.y2)
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds=30; s.parameters.num_workers=4
    t0=time.perf_counter(); st=s.Solve(m); dt=time.perf_counter()-t0
    print(f"n={n:2d} truth admitted? {s.StatusName(st)} in {dt:.2f}s")
