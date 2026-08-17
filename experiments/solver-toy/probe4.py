import sys
from scenarios import scenario
from solver import SolveConfig, project
from validate import check

def run(n, label, **kw):
    b,t,p = scenario(n)
    cfg = SolveConfig(workers=4, **kw)
    r = project(b,p,cfg)
    ok = check(b, r.rooms)["ok"] if r.rooms else None
    f = check(b, r.rooms)["failures"][:2] if r.rooms else []
    print(f"n={n:2d} {label:26s} {r.status:10s} wall={r.wall_time_s:6.2f} "
          f"first={r.time_to_first if r.time_to_first is None else round(r.time_to_first,2)} "
          f"obj={r.objective} rel={r.model_stats.get('fixed_relations')} valid={ok} {f}")
    sys.stdout.flush()

for n in (8,12,24):
    run(n, "fix_rel hard", time_limit_s=30, fix_relations=True)
    run(n, "fix_rel + soft cov", time_limit_s=30, fix_relations=True, soft=("coverage",))
    run(n, "soft cov only", time_limit_s=30, soft=("coverage",))
