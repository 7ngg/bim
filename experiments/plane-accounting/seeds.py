"""The bar the cost has to clear: seed-to-seed spread on the same model.

Ticket 77 item 1. A single wall time is not evidence -- II.1's whole finding is
that doubling the multiplication count *"is not measurable against the
seed-to-seed spread"*, and it is that spread, not a point estimate, that says
whether ADR 0039's per-Room accounting layer fits.

Part II's idiom, restated here: **six CP-SAT seeds per arm per candidate**, on
warped geometry produced ONCE so both arms see the same instance. Reported per
candidate as a median and a spread, then paired.

Two things this measures that `arms.py` cannot:

  - the spread itself, which is the denominator of every claim about the cost;
  - **time to first Plan**, which is what an interactive re-solve would feel and
    which II.1's table is stated in, so the two are comparable.

Runs on a stratified subsample by room count -- 6 seeds x 2 arms is 12 solves
per candidate and the full 291 would be four hours.

    python experiments/plane-accounting/seeds.py [k] [--seeds=6] [--tag=seeds]
"""

from __future__ import annotations

import io
import json
import statistics as st
import sys
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "solver-toy"))
sys.path.insert(0, str(HERE.parent / "warp"))

import arms as AR                                                    # noqa: E402
import project_join as PJ                                            # noqa: E402
from bar_plane import project_plane                                  # noqa: E402
from project_join import (SHIPPED_TAU, SOFT, T_INT_MM, WINDOW_MIN,   # noqa: E402
                          WORKERS, brief_from_warp, envelope_from_frame,
                          floors_m2, kinds_for, rooms_grid)
from fit_warp import COLLAPSE                                        # noqa: E402
from absolute_area import MARKET, pair_targets                       # noqa: E402
from scenarios import Proposal                                       # noqa: E402
from solver import SolveConfig                                       # noqa: E402

OUT = HERE / "out"
SEEDS = (0, 1, 2, 3, 4, 5)
ARMS = ("A", "B", "Bc")


def stratified(pairs, k):
    """`k` candidates, spread over the room counts the join actually produces,
    so the cost is not read off the small end where it is cheapest."""
    by_n = defaultdict(list)
    for p in pairs:
        by_n[p[2]["n"]].append(p)
    out, ns = [], sorted(by_n)
    i = 0
    while len(out) < k and any(by_n.values()):
        n = ns[i % len(ns)]
        if by_n[n]:
            out.append(by_n[n].pop(0))
        i += 1
        if i > 20 * k:
            break
    return out


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
    r["n_faces"] = len(env.all_faces())
    r["interior_cells"] = env.interior_area

    for arm in ARMS:
        walls, firsts, builds, sts = [], [], [], []
        for sd in seeds:
            cfg = SolveConfig(workers=WORKERS, time_limit_s=limit, seed=sd,
                              fix_relations=True,
                              relation_confidence=SHIPPED_TAU, soft=SOFT,
                              area_units="mm_affine", erode_minima=True,
                              t_int_mm=T_INT_MM, window_min=WINDOW_MIN)
            res = project_plane(b, proposal, cfg, plane=AR.PLANE[arm],
                                corners=AR.CORNERS.get(arm, False), caps=None)
            walls.append(res.wall_time_s)
            builds.append(res.build_time_s)
            firsts.append(res.time_to_first)
            sts.append(res.status)
            if arm == ARMS[0]:
                r["vars_A"] = res.model_stats["variables"]
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
    k = int(args[0]) if args and not args[0].startswith("--") else 36
    seeds = tuple(range(int(opt.get("--seeds", 6))))
    tag = opt.get("--tag", "seeds")
    tlim = float(opt.get("--time", 3.0))
    limit = float(opt.get("--limit", PJ.SHIPPED_LIMIT))
    exposure = opt.get("--exposure", PJ.EXPOSURE)

    pairs, n_sample, n_donors, n_cands = AR.sample_of(120)
    sel = stratified(pairs, k)
    print(f"{len(sel)} candidates, {len(seeds)} seeds, arms {','.join(ARMS)} "
          f"= {len(sel) * len(seeds) * len(ARMS)} solves", flush=True)
    OUT.mkdir(exist_ok=True)
    rows, t0 = [], time.perf_counter()
    for i, (bi, brief_rec, cand) in enumerate(sel):
        r = one(brief_rec, cand, tlim, limit, exposure, seeds)
        if r:
            r["brief_i"] = bi
            rows.append(r)
        el = time.perf_counter() - t0
        print(f"  {i+1:>3}/{len(sel)}  n={cand['n']:<3} {el:.0f}s", flush=True)
        json.dump(rows, io.open(OUT / f"seeds_rows_{tag}.json", "w",
                                encoding="utf-8"))
    print(f"done: {len(rows)} rows in {time.perf_counter()-t0:.0f}s")


if __name__ == "__main__":
    main()
