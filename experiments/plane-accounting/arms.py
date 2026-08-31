"""Does ADR 0039's encoding fit the budget, and what does it buy?

Ticket 77, items 1-3. An A/B on the PROJECTION, over the same warped candidates
`project_join.py` joined, with two things changed from that run:

  1. **The warp posts the statutory floor.** `project_join.py` calls
     `fit_warp.warp_model`, which does not; ADR 0033 shipped the floor after that
     run. Its **14 of 273** is therefore pre-ADR 0033 and cannot be quoted as the
     incumbent -- so the incumbent is re-run here, not cited. The swap is
     `warp_model` -> `constrained_warp.warp_model_constrained(area_floor_cells=
     ...)`, exactly `floor_warp.py`'s `floor` limb, inside `project_join`'s own
     `hold_ring` iteration so LIMIT 1's witness guarantee survives.

  2. **The warp runs ONCE per candidate and every projection arm consumes the
     same geometry.** An A/B on the projection may not re-warp between arms:
     `warp_model` is a CP-SAT solve under a wall-clock limit and is not
     reproducible between runs. Every arm below sees byte-identical Envelope,
     Rooms, Brief and Proposal.

FIVE ARMS

  A      plane="solver"              the incumbent -- (250w - t)(250h - t)
  B      plane="bar"                 ADR 0039 decisions 1-2
  Bc     plane="bar", corners=True   B plus the corner term decision 5 drops
  Acap   A + `dim.max_area`          item 3, on the lenient plane
  Bcap   B + `dim.max_area`          item 3, on the bar plane

`solver.py` posts NO cap at all -- H4 posts min_w, min_h, min_area and aspect and
nothing else -- so `Acap` and `Bcap` are both new model, and the false pass ADR
0039 describes is a property of the spec until they run.

The cap is `dim.max_area`: `k[class] x target` where the Room has a target,
`absolute_cap[class]` where it has none. Read from `rules.json#/area_bands` and
`room-constraints.json#/ergonomic/area_band_classes/resolution` -- never
transcribed. Every Room here has a target, so the `k` limb is the one exercised.

WHAT IS NOT VARIED. Everything else is `project_join.py`'s, verbatim and by
import: `mm_affine`, `erode_minima`, `t_int_mm` 150, tau = 4, 15 s, 4 workers,
`SOFT`, `WINDOW_MIN`, the exposure preset, the Brief construction, the
`--parts=1` primary arm. This file adds no configuration of its own.

    python experiments/plane-accounting/arms.py [n] [--time=3.0] [--limit=15]
                                                [--seed=0] [--tag=main]
    python experiments/plane-accounting/arms.py --selftest
"""

from __future__ import annotations

import json
import io
import random
import sys
import time
import zlib
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "solver-toy"))
sys.path.insert(0, str(HERE.parent / "warp"))

from bar_plane import (CORNER_MM2, GRID_MM, bar_area_mm2,            # noqa: E402
                       interior_corners, project_plane, reflex_on_sides,
                       solver_area_mm2, true_bar_area_mm2)

import project_join as PJ                                            # noqa: E402
from project_join import (SHIPPED_TAU, SOFT, T_INT_MM, WINDOW_MIN,   # noqa: E402
                          WORKERS, ERG_AREA, brief_from_warp, envelope_from_frame,
                          floors_m2, kinds_for, rooms_grid)
from fit_warp import (COLLAPSE, MIN_SIDE, MIN_SIDE_DEFAULT, SEED,    # noqa: E402
                      STATED_SHARE, W_INVENTED, W_STATED, coord_frame,
                      uniform)
from absolute_area import (F_PARTITION, MARKET, admissible_pool,     # noqa: E402
                           floors_for, joins, notch_share, outside_of,
                           pair_targets, part_targets_cells, rects_mm, space_m2)
from constrained_warp import warp_model_constrained                  # noqa: E402
from scenarios import Proposal                                       # noqa: E402
from solver import SolveConfig                                       # noqa: E402

OUT = HERE / "out"
ARMS = ("A", "B", "Bc", "Acap", "Bcap")
PLANE = {"A": "solver", "B": "bar", "Bc": "bar", "Acap": "solver", "Bcap": "bar"}
CORNERS = {"Bc": True}
CAPPED = ("Acap", "Bcap")


# ---------------------------------------------------------------------------
# `dim.max_area`, read rather than transcribed.
# ---------------------------------------------------------------------------
def _load_caps():
    rules = json.load(io.open(ROOT / "data/acceptance/rules.json", encoding="utf-8"))
    rc = json.load(io.open(ROOT / "data/standards/room-constraints.json",
                           encoding="utf-8"))
    bands = rules["area_bands"]["classes"]
    res = rc["ergonomic"]["area_band_classes"]["resolution"]
    # `project_join` speaks the CORPUS vocabulary (PRIVATE, LIVING_ROOM, ...)
    # and `resolution` is keyed by the profile's nineteen Room types. The bridge
    # is each class's own `corpus_label`, which names the corpus population the
    # band was measured on -- so it is read off the band, not invented here.
    by_corpus = {
        "PRIVATE": "room*", "LIVING_ROOM": "living_room",
        "LIVING_DINING": "living_dining", "DINING": "dining",
        "KITCHEN": "kitchen", "KITCHEN_DINING": "kitchen_dining",
        "BATHROOM": "bathroom", "WC": "wc", "CORRIDOR": "corridor",
        "STOREROOM": "storeroom",
    }
    for corpus, cls in by_corpus.items():
        assert cls in bands, f"{cls} missing from area_bands"
    # cross-check: every class named here is one `resolution` also reaches
    reachable = {v["class"] for v in res.values()}
    for cls in by_corpus.values():
        assert cls in reachable, f"{cls} unreachable from room-constraints"
    return {c: (bands[cls]["k"], bands[cls]["absolute_cap"])
            for c, cls in by_corpus.items()}


CAPS = _load_caps()


def caps_mm2(types, targets_m2):
    """Per-Room `dim.max_area` in mm2. `k x target` -- every Room in this rig
    carries a target, so the `absolute_cap` limb is a fallback that does not
    fire and is asserted rather than used."""
    out = []
    for t, a in zip(types, targets_m2):
        k, abs_cap = CAPS[t]
        assert a > 0, (t, a)
        out.append(int(round(k * a * 1e6)))
    return out


# ---------------------------------------------------------------------------
# The warp, with the floor posted and the geometry retained.
# ---------------------------------------------------------------------------
def warp_floor(cand, aspect, targets_m2, tlim, key="", post_floor=True):
    """`project_join.warp_geom` with `warp_model` swapped for the constrained
    form and ADR 0033's floor posted. Every other line is that function's.

    `--selftest` asserts the two agree cut-vector for cut-vector when the floor
    is NOT posted, so `post_floor=False` here IS `project_join`'s warp and the
    swap introduces nothing of its own.
    """
    parts, types = cand["parts"], [COLLAPSE.get(t, t) for t in cand["types"]]
    xs, ys, spans = coord_frame(parts)
    if len(xs) < 2 or len(ys) < 2:
        return {"status": "DEGENERATE"}
    s, void = notch_share(parts)
    if s >= 0.60:
        return {"status": "NOTCH"}

    target_area = sum(targets_m2)
    want_interior = target_area * (1.0 + F_PARTITION)
    fl_m2 = [f or 0.0 for f in floors_for(types)]
    scale, gx, gy, solved = 1.0, None, None, None
    W = H = 0
    for _ in range(6):
        interior = want_interior * scale
        box_m2 = interior / (1.0 - s)
        Hm = (box_m2 * 1e6 / aspect) ** 0.5
        W = max(4, round(aspect * Hm / GRID_MM))
        H = max(4, round(Hm / GRID_MM))

        seed = (uniform(xs, W), uniform(ys, H))
        seed_rects = rects_mm(spans, *seed)
        outside_seed = outside_of(seed_rects)
        tgt_cells = part_targets_cells(targets_m2, seed_rects, outside_seed)
        # `floor_warp.run_arm`'s two lines, verbatim: the SAME converter the
        # targets use, and a zero floor stays zero rather than becoming the
        # vacuous 1 cell `part_targets_cells` floors at.
        fl_all = part_targets_cells(fl_m2, seed_rects, outside_seed)
        fl_cells = [c if f > 0 else 0 for c, f in zip(fl_all, fl_m2)]

        jx, jy = joins(spans)
        # zlib.crc32, not hash(): `hash()` on a str is salted per process, so
        # this line drew a different OBJECTIVE in every process it ran in --
        # `project_join.py:227`, the line this file copies verbatim, was
        # repaired at ticket 82 and this copy did not follow. Ticket 83.
        rng = random.Random(SEED ^ (zlib.crc32(key.encode()) & 0xFFFF))
        weights = [W_STATED if rng.random() < STATED_SHARE else W_INVENTED
                   for _ in types]
        mins = [MIN_SIDE.get(t, MIN_SIDE_DEFAULT) for t in types]
        res, name = warp_model_constrained(
            spans, len(xs) - 1, len(ys) - 1, tgt_cells, W, H, weights, mins,
            jx, jy, tlim, seed=seed,
            area_floor_cells=fl_cells if post_floor else None)
        if res is None:
            return {"status": name, "floor_rooms": sum(1 for f in fl_m2 if f > 0)}
        gx, gy, _opt = res
        solved = rects_mm(spans, gx, gy)
        covered = sum((r[2] - r[0]) * (r[3] - r[1])
                      for pl in solved for r in pl) / 1e6
        if covered <= 0:
            return {"status": "EMPTY"}
        if abs(covered - want_interior) / want_interior < 0.002:
            break
        scale *= want_interior / covered

    outside = outside_of(solved)
    got = [space_m2(r, outside) for r in solved]
    return {"status": "OK", "got": got, "types": types, "s": s, "void": void,
            "spans": spans, "gx": gx, "gy": gy, "W": W, "H": H,
            "solved": solved, "targets": targets_m2, "floors": fl_m2,
            "floor_rooms": sum(1 for f in fl_m2 if f > 0),
            "n_rooms": len(types),
            "covered_m2": round(sum((r[2] - r[0]) * (r[3] - r[1])
                                    for pl in solved for r in pl) / 1e6, 4)}


# ---------------------------------------------------------------------------
def env_outside(env):
    """The region outside the ENVELOPE -- `outside_of` on the Envelope's own
    parts rather than on a Plan's Rooms.

    The distinction matters because this rig posts `coverage` SOFT (H3 is in
    `project_join.SOFT`), so a returned Plan may leave interior cells
    unassigned; `outside_of(plan_rects)` then reads a boundary-touching GAP as
    outside and a Room's edge on it stops eroding. The solver cannot know where
    slack will land, so the encoding is Envelope-relative by construction, and
    the two coincide exactly when H3 holds -- which is the shipped state,
    `model.no_unassigned_area`.
    """
    return outside_of([[(p.x1 * GRID_MM, p.y1 * GRID_MM,
                         p.x2 * GRID_MM, p.y2 * GRID_MM)] for p in env.parts])


def _residuals(env, rects, eout=None):
    """Per-Room: the two planes, the truth, and the exact residual decomposed.

    `rects` are single-rectangle Rooms in GRID units -- the `--parts=1` arm.
    With `eout`, each Room also carries `chk` -- `space_m2` measured against the
    Envelope's own outside. That is T2 at corpus scale: shapely on the real
    geometry against the integer identity, and they must agree to the mm2.
    """
    out = []
    for r in rects:
        b = bar_area_mm2(env, r, T_INT_MM)
        a = solver_area_mm2(r, T_INT_MM)
        c = interior_corners(env, r)
        x = reflex_on_sides(env, r)
        t = b + CORNER_MM2 * (c - x)
        rec = {"bar": b, "solver": a, "true": t, "corners": c, "reflex": x,
               "resid": t - b}
        if eout is not None:
            rm = [(r.x1 * GRID_MM, r.y1 * GRID_MM,
                   r.x2 * GRID_MM, r.y2 * GRID_MM)]
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
    w = warp_floor(cand, brief_rec["aspect"], targets, tlim,
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

    prop_space = [round(g, 4) for g in w["got"]]
    r["prop_space"] = prop_space
    r["prop_starved"] = any(g < f - 1e-9 for g, f in zip(w["got"], floors))
    r["prop_starved_rooms"] = sum(1 for g, f in zip(w["got"], floors) if g < f - 1e-9)

    env = envelope_from_frame(w["spans"], w["gx"], w["gy"], exposure)
    rooms = rooms_grid(w["spans"], w["gx"], w["gy"])
    b = brief_from_warp(f"warp-{cand['n']}", env, rooms, types, kinds,
                        floors, seed)
    r["interior_cells"] = env.interior_area
    r["n_notches"] = len(env.notches)
    r["n_faces"] = len(env.all_faces())
    r["sum_floors_m2"] = round(sum(floors), 4)

    # The warped candidate, measured on both planes before any solve. This is
    # the free half of item 4: the residual on the Proposal's own geometry.
    eout = env_outside(env)
    r["prop_resid"] = _residuals(env, [rr[0] for rr in rooms], eout)

    proposal = Proposal(boxes=[rr[0] for rr in rooms], kinds=kinds,
                        label="warped")
    cfg = SolveConfig(workers=WORKERS, time_limit_s=limit, seed=seed,
                      fix_relations=True, relation_confidence=SHIPPED_TAU,
                      soft=SOFT, area_units="mm_affine",
                      erode_minima=True, t_int_mm=T_INT_MM,
                      window_min=WINDOW_MIN)
    caps = caps_mm2(types, targets)
    r["caps_mm2"] = caps

    for arm in arms:
        res = project_plane(b, proposal, cfg, plane=PLANE[arm],
                            corners=CORNERS.get(arm, False),
                            caps=caps if arm in CAPPED else None)
        a = {"status": res.status, "wall": round(res.wall_time_s, 4),
             "build": round(res.build_time_s, 4),
             "objective": res.objective,
             "vars": res.model_stats["variables"],
             "cons": res.model_stats["constraints"],
             "mults": res.model_stats["multiplications"],
             "clits": res.model_stats["contact_lits"],
             "cints": res.model_stats["contact_ints"],
             "cov_slack": res.model_stats["cov_slack"]}
        if res.rooms:
            rects = res.rooms[:len(types)]
            rd = _residuals(env, rects, eout)
            a["resid"] = rd
            plan_rects = [[(q.x1 * GRID_MM, q.y1 * GRID_MM,
                            q.x2 * GRID_MM, q.y2 * GRID_MM)] for q in rects]
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
            a["headroom_m2"] = [round((c - d["true"]) / 1e6, 4)
                                for d, c in zip(rd, caps)]
        elif res.status == "INFEASIBLE":
            # Which constraint refused: `project_join.one`'s ablation, verbatim.
            erg = [ERG_AREA.get(t, 0.5) for t in types]
            b2 = brief_from_warp(f"abl-{cand['n']}", env, rooms, types, kinds,
                                 erg, seed)
            b2.required_adj, b2.forbidden_adj = b.required_adj, b.forbidden_adj
            ab = project_plane(b2, proposal, cfg, plane=PLANE[arm],
                               corners=CORNERS.get(arm, False),
                               caps=caps if arm in CAPPED else None)
            a["ablate_status"] = ab.status
            a["refused_by_floor"] = ab.status in ("OPTIMAL", "FEASIBLE")
            if arm in CAPPED:
                # A capped arm has a second suspect. Drop the cap, keep the
                # floor, and the two ablations separate them.
                ac = project_plane(b, proposal, cfg, plane=PLANE[arm],
                                   corners=CORNERS.get(arm, False), caps=None)
                a["ablate_cap_status"] = ac.status
                a["refused_by_cap"] = ac.status in ("OPTIMAL", "FEASIBLE")
        r[arm] = a

    r["status"] = r[arms[0]]["status"]
    return r


# ---------------------------------------------------------------------------
def sample_of(n_briefs=120, k=6, parts=1):
    """`project_join.main()`'s sampling, verbatim, so the incumbent arm here and
    the **14 of 273** it is replacing are drawn from the SAME (Brief, candidate)
    pairs. Same `SEED`, same pool rule, same `--parts=1` restriction."""
    cands = PJ.load()
    if parts == 1:
        donors = [c for c in cands if all(x == 1 for x in c["k_used"])]
    else:
        donors = [c for c in cands if any(x == 2 for x in c["k_used"])]
    by_ms = defaultdict(list)
    for c in donors:
        by_ms[c["ms"]].append(c)
    rng = random.Random(SEED)
    sample = rng.sample(cands, min(n_briefs, len(cands)))
    pairs = []
    for bi, brief in enumerate(sample):
        pool = admissible_pool(brief, by_ms)
        if not pool:
            continue
        for cand in rng.sample(pool, min(k, len(pool))):
            pairs.append((bi, brief, cand))
    return pairs, len(sample), len(donors), len(cands)


def selftest(pairs, tlim=3.0, n=8):
    """`warp_floor(post_floor=False)` IS `project_join.warp_geom`."""
    same = 0
    for (_bi, brief_rec, cand) in pairs[:n]:
        ct = [COLLAPSE.get(t, t) for t in cand["types"]]
        tg = pair_targets(ct, cand["parts"], brief_rec["rooms"])
        if tg is None:
            continue
        tg = [max(a, MARKET.get(t, 0.0)) for a, t in zip(tg, ct)]
        key = brief_rec["k"] + cand["k"]
        a = PJ.warp_geom(cand, brief_rec["aspect"], tg, tlim, key=key,
                         hold_ring=True)
        b = warp_floor(cand, brief_rec["aspect"], tg, tlim, key=key,
                       post_floor=False)
        assert a["status"] == b["status"], (a["status"], b["status"])
        if a["status"] != "OK":
            continue
        assert a["gx"] == b["gx"] and a["gy"] == b["gy"], cand["k"]
        assert [round(g, 6) for g in a["got"]] == [round(g, 6) for g in b["got"]]
        same += 1
    print(f"  ok  warp_floor(post_floor=False) == project_join.warp_geom on "
          f"{same} candidates, cut vector for cut vector")
    return same


def main():
    args = sys.argv[1:]
    opt = {a.split("=")[0]: a.split("=")[1] for a in args if "=" in a}
    tlim = float(opt.get("--time", 3.0))
    limit = float(opt.get("--limit", PJ.SHIPPED_LIMIT))
    seed = SEED
    tag = opt.get("--tag", "main")
    exposure = opt.get("--exposure", PJ.EXPOSURE)
    post_floor = opt.get("--floor", "1") != "0"
    n_briefs = int(opt.get("--briefs", 120))
    arms = tuple(opt["--arms"].split(",")) if "--arms" in opt else ARMS

    pairs, n_sample, n_donors, n_cands = sample_of(n_briefs)
    if "--selftest" in args:
        selftest(pairs, tlim)
        return
    n = int(args[0]) if args and not args[0].startswith("--") else 0
    if n:
        pairs = pairs[:n]
    print(f"{len(pairs)} (Brief, candidate) pairs from {n_sample} Briefs, "
          f"{n_donors:,} one-part donors of {n_cands:,}; arms {','.join(arms)}",
          flush=True)

    OUT.mkdir(exist_ok=True)
    rows = []
    t0 = time.perf_counter()
    for i, (bi, brief_rec, cand) in enumerate(pairs):
        r = one(brief_rec, cand, tlim, limit, seed, exposure, arms=arms,
                post_floor=post_floor)
        r["brief_i"] = bi
        rows.append(r)
        el = time.perf_counter() - t0
        print(f"  {i+1:>4}/{len(pairs)} b{bi:<4} n={r['n']:<3} "
              f"{r['status']:<14} {el:.0f}s ({el/(i+1):.2f} s/pair)", flush=True)
        json.dump(rows, io.open(OUT / f"arms_rows_{tag}.json", "w",
                                encoding="utf-8"))
    meta = {"pairs": len(pairs), "n_briefs": n_sample, "donors": n_donors,
            "warp_time_limit_s": tlim, "solve_time_limit_s": limit,
            "tau": SHIPPED_TAU, "t_int_mm": T_INT_MM, "workers": WORKERS,
            "exposure": exposure, "seed": seed, "post_floor": post_floor,
            "arms": list(arms), "secs": round(time.perf_counter() - t0, 1)}
    json.dump(meta, io.open(OUT / f"arms_meta_{tag}.json", "w",
                            encoding="utf-8"), indent=1)
    print(f"done: {len(rows)} rows in {meta['secs']:.0f}s "
          f"-> out/arms_rows_{tag}.json")


if __name__ == "__main__":
    main()
