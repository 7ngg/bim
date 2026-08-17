import sys, time
from scenarios import scenario, Proposal
from solver import SolveConfig, LayoutProjector, project
from validate import check

n = 12
b,t,p = scenario(n)

def run(label, cfg, hint_boxes=None):
    lp = LayoutProjector(b, p if hint_boxes is None else Proposal(list(hint_boxes), p.kinds, "x"), cfg)
    r = lp.solve()
    ok = check(b, r.rooms)["ok"] if r.rooms else None
    print(f"{label:32s} {r.status:10s} wall={r.wall_time_s:6.2f} first={r.time_to_first} obj={r.objective} valid={ok}")
    sys.stdout.flush()
    return r

run("baseline 60s", SolveConfig(time_limit_s=60, workers=4))
run("hint=truth 60s", SolveConfig(time_limit_s=60, workers=4), hint_boxes=t)
run("no hint 60s", SolveConfig(time_limit_s=60, workers=4, hint=False))
run("coverage slack 60s", SolveConfig(time_limit_s=60, workers=4, soft=("coverage",)))
run("all soft 60s", SolveConfig(time_limit_s=60, workers=4, soft=("coverage","required_adj","exterior","wet_cluster","circulation")))
