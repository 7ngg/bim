"""Sanity checks that must pass before any timing number is believable."""

from __future__ import annotations

import sys

from geometry import tiling_defects
from scenarios import ROOM_COUNTS, scenario
from solver import SolveConfig, project
from validate import check


def main() -> int:
    bad = 0
    for n in ROOM_COUNTS:
        brief, truth, proposal = scenario(n)
        env = brief.env
        # 1. the ground truth really is a valid Plan for this Brief
        v = check(brief, truth)
        d = tiling_defects(truth, env)
        print(f"[{n:>2} rooms] envelope {env.name} interior={env.interior_area} cells "
              f"({env.interior_area * (brief.grid_mm/1000)**2:.1f} m2)")
        print(f"           ground truth: {'VALID' if v['ok'] else 'INVALID'} "
              f"uncovered={d['uncovered_cells']} overlap={d['pairwise_overlap_area']}")
        for f in v["failures"][:6]:
            print("             !", f)
            bad += 1
        # 2. the Proposal really is broken, the way a generative model breaks
        pd = tiling_defects(proposal.boxes, env)
        print(f"           proposal: overlap={pd['overlap_pct_of_room_area']:.1f}% of room area, "
              f"uncovered={pd['uncovered_pct_of_interior']:.1f}% of interior, "
              f"outside={pd['cells_outside_envelope']} cells")
        print(f"           brief: {len(brief.required_adj)} required, "
              f"{len(brief.forbidden_adj)} forbidden adjacencies, entry="
              f"{brief.rooms[brief.entry].name}")

    # 3. the model builds and solves at all on the smallest case
    brief, truth, proposal = scenario(8)
    res = project(brief, proposal, SolveConfig(time_limit_s=30))
    print(f"\n8-room solve: {res.status} in {res.wall_time_s:.2f}s "
          f"(build {res.build_time_s:.2f}s) vars={res.model_stats['variables']} "
          f"cons={res.model_stats['constraints']}")
    if res.rooms:
        v = check(brief, res.rooms)
        print("             validator:", "VALID" if v["ok"] else "INVALID")
        for f in v["failures"][:8]:
            print("               !", f)
            bad += 1
    else:
        bad += 1
        print("             core:", res.infeasibility_core)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
