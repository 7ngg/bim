from scenarios import scenario
from solver import SolveConfig, project
from validate import check
for n in (8,12,24):
    b,t,p = scenario(n)
    r = project(b,p,SolveConfig(time_limit_s=20, workers=4))
    v = check(b, r.rooms) if r.rooms else {"ok":False,"failures":["no solution"]}
    print(f"n={n:2d} {r.status:10s} wall={r.wall_time_s:6.2f} build={r.build_time_s:5.2f} "
          f"first={r.time_to_first} obj={r.objective} bound={r.best_bound} "
          f"vars={r.model_stats['variables']} cons={r.model_stats['constraints']} "
          f"valid={v['ok']}")
    print("   trace:", [(round(a,2),o) for a,o in r.trace][:12])
    for f in v.get("failures",[])[:3]: print("    !",f)
