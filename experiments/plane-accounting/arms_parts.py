"""What does the bar plane owe a two-part Room, and what does paying it cost?

Ticket 78. `arms.py` is the same A/B at `--parts=1`; this is `--parts=2`, over
the **1 235 of 2 292** converted dwellings (53,9 %) that hold at least one
two-part Room. Everything not named below is `arms.py`'s and is imported from
it: the warp with ADR 0033's floor posted, the caps read off `rules.json`, the
sampling, the exposure preset, `mm_affine`, tau = 4, 15 s, 4 workers.

FIVE ARMS, and the middle three are one change apart each

  A     solver plane, area floor on the PART      the incumbent -- `solver_parts`
  Ar    solver plane, area floor on the ROOM      ADR 0014's binding site
  Bn    bar plane, no join term, ROOM             the naive generalisation
  B     bar plane + join term, ROOM               ADR 0039 generalised
  Bcap  B + `dim.max_area` on the ROOM            the cap, at Room level

`A -> Ar` moves the area floor from the primary part to the Room, which is what
ADR 0014 and `dim.statutory_min_area` both say and what `project_join.py`
LIMIT 3 records the rig as getting wrong. `Ar -> Bn` changes the plane and
nothing else. `Bn -> B` adds the shared-edge band, and it is the term this
ticket exists to price: **nothing else differs between those two models**.

WHY `Bn` IS A REAL ARM AND NOT A STRAW MAN.  It is what ADR 0039's encoding
does if it is applied to a two-part Room without being re-derived -- the per-side
form, per part, summed. It subtracts a band along the shared edge twice, so it
reads the Room `2 x 75 x 250 x J` short. At ADR 0014's join floor of 4 grid
units that is 150 000 mm2 = 0,15 m2 off a Room, before anything else.

    python experiments/plane-accounting/arms_parts.py [n] [--time=3.0]
                                                      [--limit=15] [--tag=parts]
    python experiments/plane-accounting/arms_parts.py --selftest
"""

from __future__ import annotations

import io
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "solver-toy"))
sys.path.insert(0, str(HERE.parent / "warp"))
sys.path.insert(0, str(HERE.parent / "room-rectangles"))

import arms as A1                                                    # noqa: E402
import project_join as PJ                                            # noqa: E402
from absolute_area import (MARKET, outside_of, pair_targets,         # noqa: E402
                           space_m2)
from bar_plane import GRID_MM                                        # noqa: E402
from fit_warp import COLLAPSE, SEED                                  # noqa: E402
from parts_plane import (JOIN_MM2_PER_UNIT, bar_union_mm2,           # noqa: E402
                         join_units, project_parts_plane,
                         solver_union_mm2, true_union_mm2)
from project_join import (SHIPPED_TAU, SOFT, T_INT_MM, WINDOW_MIN,   # noqa: E402
                          WORKERS, ERG_AREA, brief_from_warp,
                          envelope_from_frame, floors_m2, kinds_for, rooms_grid)
from scenarios import Proposal                                       # noqa: E402
from solver import SolveConfig                                       # noqa: E402
from solver_parts import PartConfig                                  # noqa: E402

OUT = HERE / "out"
ARMS = ("A", "Ar", "Bn", "B", "Bcap")
KNOBS = {
    "A":    dict(plane="solver", join=False, room_area=False),
    "Ar":   dict(plane="solver", join=False, room_area=True),
    "Bn":   dict(plane="bar",    join=False, room_area=True),
    "B":    dict(plane="bar",    join=True,  room_area=True),
    "Bcap": dict(plane="bar",    join=True,  room_area=True),
}
CAPPED = ("Bcap",)


def shape_of(parts):
    """`L`, `T`, `Z`, `rectangle` or `single`.

    Two rectangles sharing an edge make four shapes, not one. ADR 0014 argues
    the k <= 2 cap on the ground that an L is drawn and a T or a Z is left over,
    and the cap does not separate them -- so the report counts them.
    """
    if len(parts) < 2:
        return "single"
    p, q = parts
    if p.x2 == q.x1 or q.x2 == p.x1:
        lo1, hi1, lo2, hi2 = p.y1, p.y2, q.y1, q.y2
    elif p.y2 == q.y1 or q.y2 == p.y1:
        lo1, hi1, lo2, hi2 = p.x1, p.x2, q.x1, q.x2
    else:
        return "apart"
    f_lo, f_hi = lo1 == lo2, hi1 == hi2
    if f_lo and f_hi:
        return "rectangle"
    if f_lo or f_hi:
        return "L"
    if (lo1 < lo2 and hi2 < hi1) or (lo2 < lo1 and hi1 < hi2):
        return "T"
    return "Z"


def residuals(env, rooms, eout=None):
    """Per ROOM: the three planes, the truth, and the residual decomposed.

    `rooms` is a list of part lists, in GRID units. `bar_nj` is the naive
    per-part sum -- what `Bn` posts -- so `bar - bar_nj` IS the join term.
    """
    out = []
    for parts in rooms:
        b = bar_union_mm2(env, parts, join=True)
        bn = bar_union_mm2(env, parts, join=False)
        a = solver_union_mm2(parts, T_INT_MM)
        t = true_union_mm2(env, parts)
        rec = {"bar": b, "bar_nj": bn, "solver": a, "true": t,
               "resid": t - b, "resid_nj": t - bn,
               "join": join_units(parts), "parts": len(parts),
               "shape": shape_of(parts)}
        if eout is not None:
            rm = [(q.x1 * GRID_MM, q.y1 * GRID_MM,
                   q.x2 * GRID_MM, q.y2 * GRID_MM) for q in parts]
            rec["chk"] = round(space_m2(rm, eout) * 1e6)
        out.append(rec)
    return out


def one(brief_rec, cand, tlim, limit, seed, exposure, arms=ARMS,
        post_floor=True):
    r = {"brief": brief_rec["k"], "cand": cand["k"], "n": cand["n"]}
    ct = [COLLAPSE.get(t, t) for t in cand["types"]]
    targets = pair_targets(ct, cand["parts"], brief_rec["rooms"])
    if targets is None:
        r["status"] = "no_pairing"
        return r
    targets = [max(a, MARKET.get(t, 0.0)) for a, t in zip(targets, ct)]

    t0 = time.perf_counter()
    w = A1.warp_floor(cand, brief_rec["aspect"], targets, tlim,
                      key=brief_rec["k"] + cand["k"], post_floor=post_floor)
    r["warp_s"] = round(time.perf_counter() - t0, 3)
    if w["status"] != "OK":
        r["status"] = "warp_" + w["status"]
        r["floor_rooms"] = w.get("floor_rooms")
        return r

    types = w["types"]
    kinds, has_hall = kinds_for(types)
    if not has_hall:
        r["status"] = "no_hall"
        return r
    floors = floors_m2(types)
    r.update(types=types, floors=[round(f, 2) for f in floors],
             targets=[round(t, 3) for t in targets],
             s=round(w["s"], 5), void=round(w["void"], 5),
             W=w["W"], H=w["H"], covered_m2=w["covered_m2"],
             floor_rooms=w["floor_rooms"])

    r["prop_space"] = [round(g, 4) for g in w["got"]]
    r["prop_starved"] = any(g < f - 1e-9 for g, f in zip(w["got"], floors))

    env = envelope_from_frame(w["spans"], w["gx"], w["gy"], exposure)
    rooms = rooms_grid(w["spans"], w["gx"], w["gy"])
    b = brief_from_warp(f"warp-{cand['n']}", env, rooms, types, kinds,
                        floors, seed)
    r["interior_cells"] = env.interior_area
    r["n_notches"] = len(env.notches)
    r["n_faces"] = len(env.all_faces())
    r["sum_floors_m2"] = round(sum(floors), 4)
    r["n_two_part"] = sum(1 for rr in rooms if len(rr) > 1)
    r["prop_shapes"] = [shape_of(rr) for rr in rooms]

    eout = A1.env_outside(env)
    r["prop_resid"] = residuals(env, rooms, eout)

    proposal = Proposal(boxes=[rr[0] for rr in rooms], kinds=kinds,
                        label="warped")
    pc = PartConfig(parts_proposal={i: list(rr) for i, rr in enumerate(rooms)})
    r["leg_min"] = pc.leg_min
    r["leg_join"] = pc.leg_join
    cfg = SolveConfig(workers=WORKERS, time_limit_s=limit, seed=seed,
                      fix_relations=True, relation_confidence=SHIPPED_TAU,
                      soft=SOFT, area_units="mm_affine",
                      erode_minima=True, t_int_mm=T_INT_MM,
                      window_min=WINDOW_MIN)
    caps = A1.caps_mm2(types, targets)
    r["caps_mm2"] = caps

    for arm in arms:
        kw = dict(KNOBS[arm])
        res = project_parts_plane(b, proposal, cfg, pc,
                                  caps=caps if arm in CAPPED else None, **kw)
        s = res.solve
        a = {"status": s.status, "wall": round(s.wall_time_s, 4),
             "build": round(s.build_time_s, 4), "objective": s.objective,
             "vars": s.model_stats["variables"],
             "cons": s.model_stats["constraints"],
             "mults": s.model_stats["multiplications"],
             "parts": s.model_stats["parts"],
             "clits": s.model_stats["contact_lits"],
             "cints": s.model_stats["contact_ints"],
             "jints": s.model_stats["join_ints"],
             "first": (round(s.time_to_first, 4)
                       if s.time_to_first is not None else None)}
        if s.rooms:
            solved = [[s.rooms[p] for p in res.parts_of[i]]
                      for i in range(len(types))]
            rd = residuals(env, solved, eout)
            a["resid"] = rd
            a["shapes"] = [d["shape"] for d in rd]
            a["cov_slack"] = s.violations.get("uncovered_area", 0)
            plan_rects = [[(q.x1 * GRID_MM, q.y1 * GRID_MM,
                            q.x2 * GRID_MM, q.y2 * GRID_MM) for q in parts]
                          for parts in solved]
            outside = outside_of(plan_rects)
            plan = [space_m2(rs, outside) for rs in plan_rects]
            a["plan_space"] = [round(g, 4) for g in plan]
            a["plan_starved"] = any(g < f - 1e-9 for g, f in zip(plan, floors))
            a["plan_starved_rooms"] = sum(1 for g, f in zip(plan, floors)
                                          if g < f - 1e-9)
            a["over_cap"] = [i for i, (d, c) in enumerate(zip(rd, caps))
                             if d["true"] > c]
            a["cap_binds_bar"] = [i for i, (d, c) in enumerate(zip(rd, caps))
                                  if d["bar"] > c]
            a["cap_binds_solver"] = [i for i, (d, c) in enumerate(zip(rd, caps))
                                     if d["solver"] > c]
        elif s.status == "INFEASIBLE":
            # `project_join.one`'s ablation, verbatim: drop the statutory limb,
            # keep the ergonomic floor, and see whether the model comes back.
            erg = [ERG_AREA.get(t, 0.5) for t in types]
            b2 = brief_from_warp(f"abl-{cand['n']}", env, rooms, types, kinds,
                                 erg, seed)
            b2.required_adj, b2.forbidden_adj = b.required_adj, b.forbidden_adj
            ab = project_parts_plane(b2, proposal, cfg, pc,
                                     caps=caps if arm in CAPPED else None, **kw)
            a["ablate_status"] = ab.solve.status
            a["refused_by_floor"] = ab.solve.status in ("OPTIMAL", "FEASIBLE")
            if arm in CAPPED:
                ac = project_parts_plane(b, proposal, cfg, pc, caps=None, **kw)
                a["ablate_cap_status"] = ac.solve.status
                a["refused_by_cap"] = ac.solve.status in ("OPTIMAL", "FEASIBLE")
        r[arm] = a

    r["status"] = r[arms[0]]["status"]
    return r


# ---------------------------------------------------------------------------
def selftest(pairs, tlim=3.0, n=6):
    """Two statements before any timing.

    1. `warp_floor(post_floor=False)` IS `project_join.warp_geom` -- `arms.py`'s
       own check, re-run on the two-part sample because it is a different
       population.
    2. On every warped Proposal in that sample the oracle equals `space_m2` to
       the mm2, two-part Rooms included. `selftest_parts.py` P3 checks four
       synthetic Envelopes; this checks the real ones.
    """
    A1.selftest(pairs, tlim, n=n)
    ok = two = 0
    shapes = {}
    for (_bi, brief_rec, cand) in pairs[:n]:
        ct = [COLLAPSE.get(t, t) for t in cand["types"]]
        tg = pair_targets(ct, cand["parts"], brief_rec["rooms"])
        if tg is None:
            continue
        tg = [max(a, MARKET.get(t, 0.0)) for a, t in zip(tg, ct)]
        w = A1.warp_floor(cand, brief_rec["aspect"], tg, tlim,
                          key=brief_rec["k"] + cand["k"])
        if w["status"] != "OK":
            continue
        env = envelope_from_frame(w["spans"], w["gx"], w["gy"], PJ.EXPOSURE)
        rooms = rooms_grid(w["spans"], w["gx"], w["gy"])
        eout = A1.env_outside(env)
        for d in residuals(env, rooms, eout):
            assert d["true"] == d["chk"], (cand["k"], d)
            if d["parts"] > 1:
                two += 1
                assert d["bar"] - d["bar_nj"] == JOIN_MM2_PER_UNIT * d["join"]
            shapes[d["shape"]] = shapes.get(d["shape"], 0) + 1
            ok += 1
    print(f"  ok  oracle == space_m2 on {ok} warped Rooms ({two} two-part); "
          f"shapes {shapes}")


def main():
    args = sys.argv[1:]
    opt = {a.split("=")[0]: a.split("=")[1] for a in args if "=" in a}
    tlim = float(opt.get("--time", 3.0))
    limit = float(opt.get("--limit", PJ.SHIPPED_LIMIT))
    tag = opt.get("--tag", "parts")
    exposure = opt.get("--exposure", PJ.EXPOSURE)
    n_briefs = int(opt.get("--briefs", 120))
    skip = int(opt.get("--skip", 0))
    arms = tuple(opt["--arms"].split(",")) if "--arms" in opt else ARMS

    pairs, n_sample, n_donors, n_cands = A1.sample_of(n_briefs, parts=2)
    if "--selftest" in args:
        selftest(pairs, tlim)
        return
    n = int(args[0]) if args and not args[0].startswith("--") else 0
    if n:
        pairs = pairs[:n]
    total = len(pairs)
    pairs = pairs[skip:]
    print(f"{total} (Brief, candidate) pairs from {n_sample} Briefs, "
          f"{n_donors:,} two-part donors of {n_cands:,}; arms {','.join(arms)}"
          + (f"; skipping the first {skip}" if skip else ""), flush=True)

    # ⚠️ Rows are APPENDED, one JSON object per line, and flushed. A whole-list
    # dump per pair rewrites ~5 MB every 30 s and loses everything back to the
    # last complete write if the process dies mid-dump -- which it did once
    # here, at pair 174 of 332, and cost 88 pairs. `--skip` plus an append log
    # makes a kill cost one pair.
    OUT.mkdir(exist_ok=True)
    rows = []
    jl = io.open(OUT / f"armsp_rows_{tag}.jsonl", "a", encoding="utf-8")
    t0 = time.perf_counter()
    for i, (bi, brief_rec, cand) in enumerate(pairs):
        r = one(brief_rec, cand, tlim, limit, SEED, exposure, arms=arms)
        r["brief_i"] = bi
        rows.append(r)
        el = time.perf_counter() - t0
        print(f"  {skip+i+1:>4}/{total} b{bi:<4} n={r['n']:<3} "
              f"k2={r.get('n_two_part', '-'):<3} {r['status']:<14} "
              f"{el:.0f}s ({el/(i+1):.2f} s/pair)", flush=True)
        jl.write(json.dumps(r) + "\n")
        jl.flush()
    jl.close()
    meta = {"pairs": total, "n_briefs": n_sample, "donors": n_donors,
            "cands": n_cands, "warp_time_limit_s": tlim,
            "solve_time_limit_s": limit, "tau": SHIPPED_TAU,
            "t_int_mm": T_INT_MM, "workers": WORKERS, "exposure": exposure,
            "seed": SEED, "arms": list(arms), "parts": 2,
            "secs": round(time.perf_counter() - t0, 1)}
    json.dump(meta, io.open(OUT / f"armsp_meta_{tag}.json", "w",
                            encoding="utf-8"), indent=1)
    print(f"done: {len(rows)} rows in {meta['secs']:.0f}s "
          f"-> out/armsp_rows_{tag}.jsonl")


if __name__ == "__main__":
    main()
