"""The bar the two-part cost has to clear: seed-to-seed spread on the same model.

Ticket 78 item 2. `seeds.py` is ticket 77's, at `--parts=1`. The comparison that
needs this one is **`B` against `Bn`** — the join term alone, one change apart —
because it is small by construction and a point estimate cannot say whether it is
real. ADR 0040 set the bar and this clears it or does not.

Arms `A`, `Bn`, `B`: the incumbent, the naive per-part generalisation, and the
join term added. Six CP-SAT seeds each, on warped geometry produced ONCE so every
arm sees the same instance, stratified by room count.

    python experiments/plane-accounting/seeds_parts.py [k] [--seeds=6]
                                                       [--tag=seedsp]
"""

from __future__ import annotations

import io
import json
import statistics as st
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "solver-toy"))
sys.path.insert(0, str(HERE.parent / "warp"))
sys.path.insert(0, str(HERE.parent / "room-rectangles"))

import arms as AR                                                    # noqa: E402
import arms_parts as AP                                              # noqa: E402
import project_join as PJ                                            # noqa: E402
from absolute_area import MARKET, pair_targets                       # noqa: E402
from fit_warp import COLLAPSE                                        # noqa: E402
from parts_plane import project_parts_plane                          # noqa: E402
from project_join import (SHIPPED_TAU, SOFT, T_INT_MM, WINDOW_MIN,   # noqa: E402
                          WORKERS, brief_from_warp, envelope_from_frame,
                          floors_m2, kinds_for, rooms_grid)
from scenarios import Proposal                                       # noqa: E402
from seeds import stratified                                         # noqa: E402
from solver import SolveConfig                                       # noqa: E402
from solver_parts import PartConfig                                  # noqa: E402

OUT = HERE / "out"
ARMS = ("A", "Bn", "B")


def one(brief_rec, cand, tlim, limit, exposure, seeds):
    r = {"brief": brief_rec["k"], "cand": cand["k"], "n": cand["n"]}
    ct = [COLLAPSE.get(t, t) for t in cand["types"]]
    targets = pair_targets(ct, cand["parts"], brief_rec["rooms"])
    if targets is None:
        return None
    targets = [max(a, MARKET.get(t, 0.0)) for a, t in zip(targets, ct)]
    w = AR.warp_floor(cand, brief_rec["aspect"], targets, tlim,
                      key=brief_rec["k"] + cand["k"], post_floor=True)
    if w["status"] != "OK":
        return None
    types = w["types"]
    kinds, has_hall = kinds_for(types)
    if not has_hall:
        return None
    floors = floors_m2(types)
    env = envelope_from_frame(w["spans"], w["gx"], w["gy"], exposure)
    rooms = rooms_grid(w["spans"], w["gx"], w["gy"])
    b = brief_from_warp(f"warp-{cand['n']}", env, rooms, types, kinds,
                        floors, 0)
    proposal = Proposal(boxes=[rr[0] for rr in rooms], kinds=kinds,
                        label="warped")
    pc = PartConfig(parts_proposal={i: list(rr) for i, rr in enumerate(rooms)})
    r["n_faces"] = len(env.all_faces())
    r["interior_cells"] = env.interior_area
    r["n_two_part"] = sum(1 for rr in rooms if len(rr) > 1)
    r["shapes"] = [AP.shape_of(rr) for rr in rooms]

    for arm in ARMS:
        walls, firsts, builds, sts = [], [], [], []
        for sd in seeds:
            cfg = SolveConfig(workers=WORKERS, time_limit_s=limit, seed=sd,
                              fix_relations=True,
                              relation_confidence=SHIPPED_TAU, soft=SOFT,
                              area_units="mm_affine", erode_minima=True,
                              t_int_mm=T_INT_MM, window_min=WINDOW_MIN)
            res = project_parts_plane(b, proposal, cfg, pc, caps=None,
                                      **AP.KNOBS[arm]).solve
            walls.append(res.wall_time_s)
            builds.append(res.build_time_s)
            firsts.append(res.time_to_first)
            sts.append(res.status)
            r[f"vars_{arm}"] = res.model_stats["variables"]
            r[f"cons_{arm}"] = res.model_stats["constraints"]
        ft = [f for f in firsts if f is not None]
        r[arm] = {"wall": [round(x, 4) for x in walls],
                  "build": [round(x, 4) for x in builds],
                  "first": [None if f is None else round(f, 4) for f in firsts],
                  "status": sts,
                  "wall_med": round(st.median(walls), 4),
                  "wall_spread": round(max(walls) - min(walls), 4),
                  "first_med": round(st.median(ft), 4) if ft else None,
                  "first_spread": round(max(ft) - min(ft), 4) if ft else None}
    return r


def main():
    args = sys.argv[1:]
    opt = {a.split("=")[0]: a.split("=")[1] for a in args if "=" in a}
    k = int(args[0]) if args and not args[0].startswith("--") else 30
    seeds = tuple(range(int(opt.get("--seeds", 6))))
    tag = opt.get("--tag", "seedsp")
    tlim = float(opt.get("--time", 3.0))
    limit = float(opt.get("--limit", PJ.SHIPPED_LIMIT))
    exposure = opt.get("--exposure", PJ.EXPOSURE)
    skip = int(opt.get("--skip", 0))

    pairs, _ns, _nd, _nc = AR.sample_of(120, parts=2)
    sel = stratified(pairs, k)
    print(f"{len(sel)} candidates, {len(seeds)} seeds, arms {','.join(ARMS)} "
          f"= {len(sel) * len(seeds) * len(ARMS)} solves", flush=True)
    OUT.mkdir(exist_ok=True)
    rows, t0 = [], time.perf_counter()
    jl = io.open(OUT / f"seedsp_rows_{tag}.jsonl", "a", encoding="utf-8")
    for i, (bi, brief_rec, cand) in enumerate(sel[skip:]):
        r = one(brief_rec, cand, tlim, limit, exposure, seeds)
        if r:
            r["brief_i"] = bi
            rows.append(r)
            jl.write(json.dumps(r) + "\n")
            jl.flush()
        el = time.perf_counter() - t0
        print(f"  {skip+i+1:>3}/{len(sel)}  n={cand['n']:<3} "
              f"k2={r['n_two_part'] if r else '-'} {el:.0f}s", flush=True)
    jl.close()
    print(f"done: {len(rows)} rows in {time.perf_counter()-t0:.0f}s")


if __name__ == "__main__":
    main()
