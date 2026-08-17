"""Ticket item 5: what happens when the Proposal is infeasible, and when the
Brief is."""
import copy, sys
from scenarios import scenario, degenerate_proposal, shuffled_proposal
from solver import SolveConfig, project
from validate import check

def show(tag, b, p, cfg):
    r = project(b, p, cfg)
    v = check(b, r.rooms) if r.rooms else None
    print(f"{tag:38s} {r.status:10s} wall={r.wall_time_s:6.2f} "
          f"first={None if r.time_to_first is None else round(r.time_to_first,2)} "
          f"obj={r.objective} valid={None if v is None else v['ok']} "
          f"core={r.infeasibility_core}")
    if v and not v["ok"]:
        for f in v["failures"][:3]: print("      !", f)
    sys.stdout.flush()

BEST = dict(workers=4, fix_relations=True, soft=("coverage",), time_limit_s=30)

for n in (8, 12, 24):
    b, t, p = scenario(n)
    # A: worthless Proposal — every room a unit box in one corner.
    show(f"n={n} degenerate proposal",
         b, degenerate_proposal(t, p.kinds), SolveConfig(**{**BEST, "fix_relations": False}))
    # B: topologically hostile Proposal — right boxes, wrong rooms.
    show(f"n={n} shuffled proposal", b, shuffled_proposal(t, p.kinds, 1), SolveConfig(**BEST))

# C: a genuinely impossible Brief - one pair both required and forbidden.
b, t, p = scenario(12)
bad = copy.deepcopy(b)
pair = bad.required_adj[0]
bad.forbidden_adj = sorted(set(bad.forbidden_adj) | {pair})
show("n=12 contradictory Brief (hard)", bad, p, SolveConfig(**BEST))
show("n=12 contradictory Brief (soft)", bad, p,
     SolveConfig(workers=4, fix_relations=True, time_limit_s=30,
                 soft=("coverage","required_adj","exterior","wet_cluster","circulation")))
