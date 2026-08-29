"""Does the projection solve rescue a starved warped candidate?

Ticket 59. **No warped Proposal on this map has ever reached the projection
solve.** `dim.statutory_min_area` is `site: both` -- the solver posts it and the
validator evaluates it -- and every starvation figure published (54's 30,7 %,
56's 25,5 %, 57's best-of-*m* curve, 60's 4,4 % at Brief level) was measured on
the **warped rectangles**, before any projection. `fit_warp.py` imports
`experiments/solver-toy/` for `rank_relations` / `select_relations` and nothing
else; `solver-toy`'s own Envelopes are fixtures or real dwellings, never warped
candidates.

This closes that join. One warped candidate becomes one solver-toy `Brief` plus
one `Proposal`, `project()` runs at the shipped config, and the SAME function
measures the delivered Space on both sides -- `absolute_area.space_m2`, ADR
0001's `erode(U parts, t_int/2)` on ADR 0010's finished face. Proposal-level and
Plan-level starvation are then the same quantity read at two points in the
pipeline, which is the only way the comparison means anything.

WHAT IS JOINED, AND WHERE EACH PIECE COMES FROM

  Envelope     the ADR 0020 box the warp solved into, at `hold_ring`: `W x H`
               grid cells, with EVERY uncovered frame cell posted as a notch.
               So the warped rectangles tile the Envelope exactly and the
               candidate is its own **witness** -- the guarantee Parts I-III
               have and 58's real arm could not get. See LIMIT 1.
  Brief.rooms  `max(ergonomic, statutory)` per Room, the same table
               `absolute_area.floors_for` publishes, as a CLEAR-plane area and a
               clear-plane short side. See LIMIT 2 for the grid arithmetic.
  Proposal     the warped rectangles themselves, in grid units.
  adjacency    the donor's own, read off the warped rectangles at the same
               30 % / 10 % sampling `real_arm.brief_from_truth` uses.
  config       `real_arm.py`'s, with ONE change: `t_int_mm` 150 rather than 100.
               The warp measures Space at `t_int` 150 (ADR 0010's shipped layer
               set) and a join that solved at 100 would be comparing two planes.
               Every published solver timing on this map is at 100, so the wall
               times here are NOT comparable with Part II or ADR 0029 and are
               reported as their own measurement.

THREE LIMITS, STATED BEFORE ANY NUMBER

  LIMIT 1 -- **ADR 0028's void is carried as an Envelope obstacle, not as a
  charged span.** The shipped contract puts `voids: [(span, receiving_room)]` on
  the Proposal and hands the floor to a Room; solver-toy's `Proposal` has no such
  field. Posting the void as a notch instead makes the tiling exact by
  construction, which is what buys the witness. It means this arm cannot see the
  void's Plan-level cost -- that is §2.2.8's, measured there at p90 1,50 m2
  charged -- and it makes the arm **optimistic about H3 and about nothing else**.

  LIMIT 2 -- **the width floor is restated, not moved.** Under
  `erode_minima=True` the solver binds `cw = 250w - t_int >= min_w * 250`, so
  passing `MIN_SIDE - 1` reproduces the warp's own `w >= MIN_SIDE` exactly, for
  every type in the table. Checked in `_check_min_side_identity()`, which runs
  on import. The area floor binds as `amm >= min_area * 250^2`, which is the
  clear plane in m2 exactly -- that is the plane `dim.statutory_min_area` and
  `dim.min_area` both bind, and it is why `minima_are_clear_grid` is off.

  LIMIT 3 -- **`--parts=1` is 46,4 % of the converted index and it is not a
  random half.** `solver-toy/solver.py` gives a Room ONE rectangle; ADR 0014
  gives it one or two. The primary arm therefore runs on donors whose every Room
  is a single rectangle -- 1,076 of 2,317 -- where the two formulations agree
  exactly. Those donors skew small (59,3 % at n = 6 against 31,4 % at n = 9).
  `--parts=2` runs the rest through `room-rectangles/solver_parts.py`'s Design A
  (`parts_proposal`), and carries its own caveat: that rig binds the Room's
  `min_area` on the PRIMARY part where ADR 0014 binds it on the Room, so it is
  strictly stricter. A false refusal it finds is real; a false refusal it misses
  may be hidden by that strictness. Both directories are imported read-only.

Reads `out/dwelling_rooms.json` and `../rectangularise/out/swiss_fit_k2.json`.
Writes `out/project_join.json` and every row to `out/project_join_rows.json` --
`acceptance-thresholds/`'s standing rule, because a re-run is ~1 h.

    python experiments/warp/project_join.py [n] [--k=6] [--parts=1] [--time=3.0]
                                            [--limit=15] [--exposure=corpus_median]
    python experiments/warp/project_join.py --selftest
"""

from __future__ import annotations

import json
import math
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "solver-toy"))
sys.path.insert(0, str(HERE.parent / "room-rectangles"))

from fit_warp import (COLLAPSE, GRID_MM, MIN_SIDE, MIN_SIDE_DEFAULT,      # noqa: E402
                      AREA_TOL, ASPECT_TOL, ASPECT_HARD, SEED,
                      W_STATED, W_INVENTED, STATED_SHARE,
                      coord_frame, uniform, warp_model, profile)
from absolute_area import (F_PARTITION, MARKET, T_INT_MM,                 # noqa: E402
                           admissible_pool, floors_for, joins, notch_share,
                           outside_of, pair_targets, part_targets_cells, pct,
                           rects_mm, space_m2)

from geometry import Envelope, Rect, adjacency_matrix                     # noqa: E402
from scenarios import Brief, Proposal, RoomSpec                           # noqa: E402
from solver import SolveConfig, project                                   # noqa: E402
from validate import check                                                # noqa: E402

OUT = HERE / "out"
FIT = HERE.parent / "rectangularise" / "out" / "swiss_fit_k2.json"
ROOMS = OUT / "dwelling_rooms.json"

SHIPPED_LIMIT = 15.0            # C10, ADR 0019 -- re-affirmed by ADR 0029
SHIPPED_TAU = 4                 # C10
DOOR_MIN_ADR = mm_door = 4      # 1,0 m in grid units, `real_arm.DOOR_MIN_ADR`
WINDOW_MIN = 4                  # solver-toy's WINDOW_MIN, 1,0 m of exterior run
WORKERS = 4
EXPOSURE = "corpus_median"      # the re-fitted p50; 63,3 % of real dwellings

# LIMIT 4 -- **the toy's three programme predicates are posted soft, and that is
# a decision this file has to defend.** H4/H5 stay hard: minimum side, minimum
# area and `dim.aspect_ratio_hard` are the predicates `dim.statutory_min_area`
# lives among and the whole of what this ticket measures. H8/H9/H10 do not, and
# each is a placeholder the shipped registry has already moved past:
#
#   H8  `exterior`     binds off an EXPOSURE PRESET, and a warped candidate
#                      carries no exposure -- the ring is ADR 0003 §7's, fixed
#                      per candidate, and `frontage_reach` is a §2.2 field the
#                      Proposal does not yet hold. At any preset the assignment
#                      of donor rooms to exterior edges is arbitrary.
#   H9  `wet_cluster`  demands ONE plumbing cluster. `wet.plumbing_group_count`
#                      has been **3** since ADR 0023 -- the tail reaches three at
#                      14.14 % of real dwellings -- so the toy's rule rejects
#                      dwellings the shipped rule admits.
#   H10 `circulation`  routes around the toy's `PRIVATE`, which includes the wet
#                      types; `circ.no_private_transit` is about sleeping rooms.
#                      Ticket 30 hands `room-constraints.json` `is_sleeping` for
#                      exactly this reason and says it may NOT be folded into
#                      `is_private`.
#
# 58 named this trap from the other side -- `assign_kinds` and `ground_truth` are
# the toy's placeholders and "neither may be quoted as `room-constraints.json`'s
# cost". Leaving them hard would have measured them rather than the floor. What
# they would have cost is on the record for free, in `witness_fails`: whether
# the warped candidate satisfies each of them is computed with no solve at all.
SOFT = ("coverage", "exterior", "wet_cluster", "circulation")

# ---------------------------------------------------------------------------
# The corpus vocabulary, onto solver-toy's kind sets.
#
# The kind string is read by `solver.py` ONLY through CIRCULATION / HABITABLE /
# PRIVATE / WET; `STANDARDS` is never consulted, because a `RoomSpec` carries its
# own minima. `STOREROOM` therefore maps to a kind that is in NO set -- shipped
# `storage.is_wet` is false and mapping it to the toy's `utility` would have put
# a storeroom in the plumbing cluster and made H9 harder for a reason no rule
# has. The first CORRIDOR becomes the `hall` that holds `brief.entry`.
# ---------------------------------------------------------------------------
KIND = {"PRIVATE": "bedroom", "LIVING_ROOM": "living", "LIVING_DINING": "living",
        "DINING": "dining", "KITCHEN": "kitchen", "KITCHEN_DINING": "kitchen",
        "BATHROOM": "bathroom", "WC": "wc", "CORRIDOR": "corridor",
        "STOREROOM": "storage"}

# `ergonomic.rooms[*].min_area.v`, READ through `corpus_label_map`. Used only
# where `floors_for` returns None -- the limbs AzDTN publishes no floor for. The
# ones that carry a statutory floor never take a max against these (living 3,7
# against 15/16, kitchen 1,8 against 8, bedroom_double 3,1 against 10).
#
# It was ten literals, correct on every cell when ticket 69 checked them -- which
# is the point: it is the same class of object as `MARKET`, which had drifted on
# four of six within a day of ADR 0035. This one had not drifted YET.
ERG_AREA = profile.ergonomic_area_table()
HALL_AREA = profile.ergonomic_min_area_m2("hall")   # the invented circulation Room


def _check_min_side_identity() -> None:
    """LIMIT 2. `min_w = MIN_SIDE - 1` under `erode_minima` binds identically to
    the warp's `min_side = MIN_SIDE`, for every type this probe can emit.

        solver:  250*w - t_int >= 250*(MIN_SIDE - 1)   <=>   w >= MIN_SIDE - 0.4
        warp:    w >= MIN_SIDE

    which agree on the integers exactly while t_int < 250. Asserted rather than
    argued, because getting it wrong silently makes the projection stricter than
    the warp and every false refusal below would be the rig's."""
    for t in set(list(MIN_SIDE) + list(KIND)):
        ms = MIN_SIDE.get(t, MIN_SIDE_DEFAULT)
        lo = math.ceil((250 * (ms - 1) + T_INT_MM) / 250)
        assert lo == ms, f"{t}: solver floor {lo} != warp floor {ms}"


_check_min_side_identity()


# ---------------------------------------------------------------------------
# The warp, with its geometry retained.
# ---------------------------------------------------------------------------
def warp_geom(cand, aspect, targets_m2, tlim, key="", hold_ring=True):
    """`absolute_area.run_one` with the solved frame kept rather than discarded.

    Every step is that function's, in the same order, off the same primitives --
    `coord_frame`, `notch_share`, `part_targets_cells`, `warp_model`, `rects_mm`,
    `outside_of`, `space_m2`. `--selftest` asserts the two return identical
    per-room Space areas on a sample, so this cannot drift into a second warp.
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
    scale, gx, gy, solved = 1.0, None, None, None
    W = H = 0
    for _ in range(6 if hold_ring else 1):
        interior = want_interior * scale
        box_m2 = interior / (1.0 - s)
        Hm = (box_m2 * 1e6 / aspect) ** 0.5
        W = max(4, round(aspect * Hm / GRID_MM))
        H = max(4, round(Hm / GRID_MM))

        seed = (uniform(xs, W), uniform(ys, H))
        seed_rects = rects_mm(spans, *seed)
        tgt_cells = part_targets_cells(targets_m2, seed_rects,
                                       outside_of(seed_rects))
        jx, jy = joins(spans)
        rng = random.Random(SEED ^ (hash(key) & 0xFFFF))
        weights = [W_STATED if rng.random() < STATED_SHARE else W_INVENTED
                   for _ in types]
        mins = [MIN_SIDE.get(t, MIN_SIDE_DEFAULT) for t in types]
        res, name = warp_model(spans, len(xs) - 1, len(ys) - 1, tgt_cells, W, H,
                               weights, mins, jx, jy, tlim, seed=seed)
        if res is None:
            return {"status": name}
        gx, gy, _opt = res
        solved = rects_mm(spans, gx, gy)
        covered = sum((r[2] - r[0]) * (r[3] - r[1])
                      for pl in solved for r in pl) / 1e6
        if not hold_ring:
            break
        if covered <= 0:
            return {"status": "EMPTY"}
        if abs(covered - want_interior) / want_interior < 0.002:
            break
        scale *= want_interior / covered

    outside = outside_of(solved)
    got = [space_m2(r, outside) for r in solved]
    return {"status": "OK", "got": got, "types": types, "s": s, "void": void,
            "spans": spans, "gx": gx, "gy": gy, "W": W, "H": H,
            "solved": solved, "targets": targets_m2, "target_area": target_area,
            "n_rooms": len(types),
            "covered_m2": round(sum((r[2] - r[0]) * (r[3] - r[1])
                                    for pl in solved for r in pl) / 1e6, 4)}


# ---------------------------------------------------------------------------
# Frame -> Envelope
# ---------------------------------------------------------------------------
def _cum(v):
    c = [0]
    for x in v:
        c.append(c[-1] + x)
    return c


def envelope_from_frame(spans, gx, gy, exposure=EXPOSURE, name="warped"):
    """The ADR 0020 box with every uncovered frame cell posted as a notch.

    LIMIT 1: this puts ADR 0028's enclosed void into `notches` alongside ADR
    0020's boundary notch, because the toy `Proposal` has no `voids` field to
    hand it to a Room. `Envelope._notch_is_exterior` then types the two
    correctly anyway -- a boundary-touching notch flush with an exterior bbox run
    sees daylight, an enclosed one does not -- so H8 reads the right faces.

    Cells are merged into maximal rectangles greedily (grow right, then down),
    which matters only for `all_faces()`' cost: the shape is identical either
    way because `contains()` is a union test.
    """
    nx, ny = len(gx), len(gy)
    cx, cy = _cum(gx), _cum(gy)
    cov = [[False] * ny for _ in range(nx)]
    for parts in spans:
        for (a, b, c, d) in parts:
            for i in range(a, b):
                for j in range(c, d):
                    cov[i][j] = True

    free = [[not cov[i][j] for j in range(ny)] for i in range(nx)]
    notches = []
    for j in range(ny):
        for i in range(nx):
            if not free[i][j]:
                continue
            i2 = i
            while i2 + 1 < nx and free[i2 + 1][j]:
                i2 += 1
            j2 = j
            while j2 + 1 < ny and all(free[q][j2 + 1] for q in range(i, i2 + 1)):
                j2 += 1
            for q in range(i, i2 + 1):
                for r in range(j, j2 + 1):
                    free[q][r] = False
            notches.append(Rect(cx[i], cy[j], cx[i2 + 1], cy[j2 + 1]))

    W, H = cx[-1], cy[-1]
    parts_rects = tuple(Rect(cx[a], cy[c], cx[b], cy[d])
                        for pl in spans for (a, b, c, d) in pl)
    return Envelope(name, W, H, tuple(notches), parts_rects, exposure)


def rooms_grid(spans, gx, gy):
    """Each Room's parts as grid-unit `Rect`s, largest part first."""
    cx, cy = _cum(gx), _cum(gy)
    out = []
    for pl in spans:
        rs = [Rect(cx[a], cy[c], cx[b], cy[d]) for (a, b, c, d) in pl]
        rs.sort(key=lambda r: -r.area)
        out.append(rs)
    return out


# ---------------------------------------------------------------------------
# Brief construction
# ---------------------------------------------------------------------------
def kinds_for(types):
    """Corpus types onto toy kinds. The first CORRIDOR becomes the `hall`."""
    out, seen_hall = [], False
    for t in types:
        k = KIND.get(t, "storage")
        if k == "corridor" and not seen_hall:
            k, seen_hall = "hall", True
        out.append(k)
    return out, seen_hall


def floors_m2(types):
    """`max(ergonomic, statutory)` per Room, in m2 -- the plane
    `dim.statutory_min_area` binds. `floors_for` publishes the statutory limb;
    where AzDTN is silent the ergonomic minimum is the floor and nothing takes a
    max against it."""
    stat = floors_for(types)
    return [s if s is not None else ERG_AREA.get(t, 0.5)
            for t, s in zip(types, stat)]


def brief_from_warp(name, env, rooms, types, kinds, floors, seed,
                    required_frac=0.30, forbidden_frac=0.10):
    """`real_arm.brief_from_truth` with the room types SUPPLIED by the corpus
    rather than assigned by `assign_kinds`.

    That is the whole difference, and it is deliberate: 58 found `assign_kinds`
    refuses a real dwelling on the programme -- `COMPOSITION` wants a median 5
    habitable Rooms against a median 4 typed cells -- so an arm that ran it would
    be measuring the toy's placeholder composition rule and not the warp. A
    warped candidate arrives with its Room types already decided, which is what
    the Proposal contract says it carries (§1).
    """
    n = len(rooms)
    primary = [r[0] for r in rooms]
    specs = specs_for(types, kinds, floors)
    adj_door = adjacency_matrix(primary, DOOR_MIN_ADR)
    adj_any = adjacency_matrix(primary, 1)
    true_pairs = [(i, j) for i in range(n) for j in range(i + 1, n)
                  if adj_door[i][j]]
    non_pairs = [(i, j) for i in range(n) for j in range(i + 1, n)
                 if not adj_any[i][j]]
    rng = random.Random(seed)
    rng.shuffle(true_pairs)
    rng.shuffle(non_pairs)
    required = sorted(true_pairs[: max(1, round(len(true_pairs) * required_frac))]) \
        if true_pairs else []
    forbidden = sorted(non_pairs[: max(1, round(len(non_pairs) * forbidden_frac))]) \
        if non_pairs else []
    entry = kinds.index("hall")
    return Brief(name=name, env=env, grid_mm=GRID_MM, rooms=specs, entry=entry,
                 required_adj=required, forbidden_adj=forbidden,
                 door_min=DOOR_MIN_ADR, max_aspect=ASPECT_HARD)


def specs_for(types, kinds, floors):
    """`RoomSpec`s on the CLEAR plane. LIMIT 2: `min_w = MIN_SIDE - 1` binds
    identically to the warp's `min_side`, and `min_area` in grid cells binds as
    `amm >= min_area * 250^2`, which is m2 exactly."""
    out = []
    for i, (t, k, fl) in enumerate(zip(types, kinds, floors)):
        ms = MIN_SIDE.get(t, MIN_SIDE_DEFAULT) - 1
        out.append(RoomSpec(f"{k}{i}", k, ms, ms, round(fl * 16)))
    return out


# ---------------------------------------------------------------------------
# One candidate, end to end
# ---------------------------------------------------------------------------
def _solve(b, proposal, cfg, rooms, k2):
    if k2:
        from solver_parts import PartConfig, project_parts               # noqa: E402
        pc = PartConfig(parts_proposal={i: rr for i, rr in enumerate(rooms)})
        pr = project_parts(b, proposal, cfg, pc)
        return pr.solve, pr.parts_of
    return project(b, proposal, cfg), None


def one(brief_rec, cand, tlim, limit, seed, exposure, k2=False):
    r = {"brief": brief_rec["k"], "cand": cand["k"], "n": cand["n"]}
    ct = [COLLAPSE.get(t, t) for t in cand["types"]]
    targets = pair_targets(ct, cand["parts"], brief_rec["rooms"])
    if targets is None:
        r["status"] = "no_pairing"
        return r
    targets = [max(a, MARKET.get(t, 0.0)) for a, t in zip(targets, ct)]

    t0 = time.perf_counter()
    w = warp_geom(cand, brief_rec["aspect"], targets, tlim,
                  key=brief_rec["k"] + cand["k"], hold_ring=True)
    r["warp_s"] = round(time.perf_counter() - t0, 3)
    if w["status"] != "OK":
        r["status"] = "warp_" + w["status"]
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
             W=w["W"], H=w["H"], covered_m2=w["covered_m2"])

    # ---- Proposal level: the quantity every published figure is measured on --
    prop = [round(g, 4) for g in w["got"]]
    r["prop_space"] = prop
    r["prop_short"] = [round(f - g, 4) for g, f in zip(w["got"], floors) if g < f]
    r["prop_starved"] = any(g < f for g, f in zip(w["got"], floors))
    r["prop_starved_rooms"] = sum(1 for g, f in zip(w["got"], floors) if g < f)

    env = envelope_from_frame(w["spans"], w["gx"], w["gy"], exposure)
    rooms = rooms_grid(w["spans"], w["gx"], w["gy"])
    b = brief_from_warp(f"warp-{cand['n']}", env, rooms, types, kinds,
                        floors, seed)
    r["interior_cells"] = env.interior_area
    r["interior_m2"] = round(env.interior_area * (GRID_MM / 1000) ** 2, 4)
    r["sum_floors_m2"] = round(sum(floors), 4)      # the arithmetic screen, R1
    r["n_notches"] = len(env.notches)
    r["exterior_fraction"] = round(env.exterior_fraction, 4)

    # ---- the witness: is the warped candidate itself a valid Plan? -----------
    wit = check(b, [rr[0] for rr in rooms], window_min=WINDOW_MIN)
    r["witness_ok"] = bool(wit["ok"])
    r["witness_fails"] = [f.split(" ")[0] for f in wit["failures"]] or None

    proposal = Proposal(boxes=[rr[0] for rr in rooms], kinds=kinds,
                        label="warped")
    cfg = SolveConfig(workers=WORKERS, time_limit_s=limit, seed=seed,
                      fix_relations=True, relation_confidence=SHIPPED_TAU,
                      soft=SOFT, area_units="mm_affine",
                      erode_minima=True, t_int_mm=T_INT_MM,
                      window_min=WINDOW_MIN)
    res, parts_of = _solve(b, proposal, cfg, rooms, k2)
    r["status"] = res.status
    r["wall"] = round(res.wall_time_s, 4)
    r["objective"] = res.objective

    # ---- attribution. The projection posts the floor HARD (`site: both`), so a
    # returned Plan is never starved and a refusal can only appear as
    # INFEASIBLE. Which constraint refused it is not in `infeasibility_core` --
    # that only covers the SOFTABLE families -- so it is settled by ablation:
    # re-solve with the statutory limb dropped and the ergonomic floor left in
    # place, which is `fit_warp.py --no-min`'s shape one level up. Run only on
    # the refusals, so it costs nothing on the common path.
    if res.status == "INFEASIBLE":
        erg = [ERG_AREA.get(t, 0.5) for t in types]
        b2 = brief_from_warp(f"abl-{cand['n']}", env, rooms, types, kinds,
                             erg, seed)
        b2.required_adj, b2.forbidden_adj = b.required_adj, b.forbidden_adj
        a_res, _ = _solve(b2, proposal, cfg, rooms, k2)
        r["ablate_status"] = a_res.status
        r["refused_by_floor"] = a_res.status in ("OPTIMAL", "FEASIBLE")

    if not res.rooms:
        r.update(plan_space=None, plan_starved=None, plan_valid=None)
        return r

    if k2 and parts_of:
        plan_rects = [[(res.rooms[p].x1 * GRID_MM, res.rooms[p].y1 * GRID_MM,
                        res.rooms[p].x2 * GRID_MM, res.rooms[p].y2 * GRID_MM)
                       for p in parts_of[i] if res.rooms[p].area > 0]
                      for i in range(len(types))]
    else:
        plan_rects = [[(rr.x1 * GRID_MM, rr.y1 * GRID_MM,
                        rr.x2 * GRID_MM, rr.y2 * GRID_MM)] for rr in res.rooms]
    outside = outside_of(plan_rects)
    plan = [space_m2(rs, outside) for rs in plan_rects]
    r["plan_space"] = [round(g, 4) for g in plan]
    r["plan_short"] = [round(f - g, 4) for g, f in zip(plan, floors) if g < f]
    r["plan_starved"] = any(g < f for g, f in zip(plan, floors))
    r["plan_starved_rooms"] = sum(1 for g, f in zip(plan, floors) if g < f)

    if k2:
        # `validate.check` is Room-indexed and `project_parts` returns a
        # PART-indexed list, so the k <= 2 arm needs that directory's own
        # checker -- imported read-only, like everything else here.
        import validate_parts                                        # noqa: E402
        from solver_parts import PartConfig                           # noqa: E402
        v = validate_parts.check(
            b, {i: [res.rooms[p] for p in parts_of[i]]
                for i in range(len(types))},
            leg_min=PartConfig().leg_min, leg_join=PartConfig().leg_join,
            window_min=WINDOW_MIN)
    else:
        v = check(b, res.rooms[:len(types)], window_min=WINDOW_MIN)
    r["plan_valid"] = bool(v["ok"])
    r["plan_fails"] = sorted({f.split(" ")[0] for f in v["failures"]}) or None
    r["survivor"] = bool(v["ok"]) and res.objective is not None \
        and res.objective < cfg.soft_weight
    return r


# ---------------------------------------------------------------------------
def load():
    recs = {r["k"]: r for r in json.load(open(ROOMS))}
    fits = [r for r in json.load(open(FIT)) if r["status"] in ("OPTIMAL", "FEASIBLE")]
    cands = []
    for f in fits:
        rr = recs.get(f["k"])
        if not rr or f["n"] != rr["n"]:
            continue
        c = dict(f)
        c.update(area=rr["area"], aspect=rr["aspect"], rooms=rr["rooms"], k=f["k"])
        c["ms"] = tuple(sorted(Counter(COLLAPSE.get(t, t)
                                       for t, _ in rr["rooms"]).items()))
        cands.append(c)
    return cands


def selftest(cands, tlim=3.0, n=12):
    """`warp_geom` must return exactly `absolute_area.run_one`'s Space areas."""
    from absolute_area import run_one
    rng = random.Random(SEED)
    by_ms = defaultdict(list)
    for c in cands:
        by_ms[c["ms"]].append(c)
    tried = ok = 0
    for brief in rng.sample(cands, 400):
        pool = admissible_pool(brief, by_ms)
        if not pool:
            continue
        cand = rng.choice(pool)
        ct = [COLLAPSE.get(t, t) for t in cand["types"]]
        tg = pair_targets(ct, cand["parts"], brief["rooms"])
        if tg is None:
            continue
        tg = [max(a, MARKET.get(t, 0.0)) for a, t in zip(tg, ct)]
        key = brief["k"] + cand["k"]
        a = run_one(cand, brief["aspect"], tg, tlim, key=key, hold_ring=True)
        b = warp_geom(cand, brief["aspect"], tg, tlim, key=key, hold_ring=True)
        tried += 1
        assert a["status"] == b["status"], (a["status"], b["status"])
        if a["status"] == "OK":
            assert max(abs(x - y) for x, y in zip(a["got"], b["got"])) < 1e-9, \
                "warp_geom has drifted from run_one"
            ok += 1
        if tried >= n:
            break
    print(f"selftest: {tried} candidates, {ok} solved, "
          f"warp_geom == run_one on every one")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n_arg = int(args[0]) if args else 120
    k = 6
    tlim = 3.0
    limit = SHIPPED_LIMIT
    parts = 1
    exposure = EXPOSURE
    suffix = ""
    for a in sys.argv[1:]:
        if a.startswith("--k="):
            k = int(a.split("=", 1)[1])
        if a.startswith("--time="):
            tlim = float(a.split("=", 1)[1])
        if a.startswith("--limit="):
            limit = float(a.split("=", 1)[1])
        if a.startswith("--parts="):
            parts = int(a.split("=", 1)[1])
        if a.startswith("--exposure="):
            exposure = a.split("=", 1)[1]
        if a.startswith("--suffix="):
            suffix = a.split("=", 1)[1]

    if any(a.startswith("--report") for a in sys.argv):
        # Re-summarise a finished run from its rows, so a new statistic off this
        # study costs seconds rather than the two hours the solves take.
        rows = json.load(open(OUT / f"project_join_rows{suffix}.json"))
        out = summarise(rows)
        out["by_brief"] = brief_level(rows)
        if "--planes" in sys.argv:
            out["planes"] = planes(rows, load(), tlim)
        print(json.dumps(out, indent=1))
        json.dump(out, open(OUT / f"project_join{suffix}.json", "w"), indent=1)
        return

    cands = load()
    print(f"converted dwellings joined to the room cache: {len(cands):,}")
    if "--selftest" in sys.argv:
        selftest(cands, tlim)
        return

    # LIMIT 3. Donors are restricted by part count; Briefs are not.
    if parts == 1:
        donors = [c for c in cands if all(x == 1 for x in c["k_used"])]
    else:
        donors = [c for c in cands if any(x == 2 for x in c["k_used"])]
    print(f"--parts={parts}: {len(donors):,} donors of {len(cands):,} "
          f"({100 * len(donors) / len(cands):.1f} %)")

    by_ms = defaultdict(list)
    for c in donors:
        by_ms[c["ms"]].append(c)

    rng = random.Random(SEED)
    sample = rng.sample(cands, min(n_arg, len(cands)))

    rows, skipped = [], Counter()
    t_start = time.perf_counter()
    for bi, brief in enumerate(sample):
        pool = admissible_pool(brief, by_ms)
        if not pool:
            skipped["no_pool"] += 1
            continue
        picks = rng.sample(pool, min(k, len(pool)))
        for cand in picks:
            r = one(brief, cand, tlim, limit, SEED, exposure, k2=(parts == 2))
            r["brief_i"] = bi
            rows.append(r)
            if r["status"] not in ("OPTIMAL", "FEASIBLE", "INFEASIBLE", "UNKNOWN"):
                skipped[r["status"]] += 1
            print(f"  b{bi:<4} n={r['n']:<3} {r['status']:<14} "
                  f"prop={'STARVED' if r.get('prop_starved') else 'ok':<8}"
                  f"plan={'STARVED' if r.get('plan_starved') else ('ok' if r.get('plan_starved') is False else '-'):<8}"
                  f"{r.get('wall', 0):.2f}s", flush=True)
        json.dump(rows, open(OUT / f"project_join_rows{suffix}.json", "w"))
    print(f"\ntotal {time.perf_counter() - t_start:.0f} s")

    out = summarise(rows)
    out["_meta"] = {"n_briefs": len(sample), "pool_k": k, "parts": parts,
                    "warp_time_limit_s": tlim, "solve_time_limit_s": limit,
                    "tau": SHIPPED_TAU, "t_int_mm": T_INT_MM,
                    "exposure": exposure, "seed": SEED,
                    "donors": len(donors), "skipped": dict(skipped)}
    OUT.mkdir(exist_ok=True)
    json.dump(out, open(OUT / f"project_join{suffix}.json", "w"), indent=1)
    print(json.dumps(out, indent=1))
    print("\nwrote", OUT / f"project_join{suffix}.json")


def planes(rows, cands, tlim):
    """The two area planes, on the same rectangles, with no solve.

    `absolute_area.space_m2` is ADR 0001's: `erode(U parts, t_int/2)` with the
    region OUTSIDE the Envelope unioned in first, so a Room's boundary edge costs
    no floor -- the tiling edge on the domain boundary already sits at
    exterior-inner-face + `t_int/2`. Ticket 56 removed exactly this defect from
    this rig and measured it at **3,7 % of `interior` at p50**.

    `solver.py`'s is `amm = (250w - t)(250h - t)`, which erodes ALL FOUR sides of
    every Room including the ones on the Envelope. It cannot do otherwise: ADR
    0001 tiles the solve domain, the box dilated by `t_int/2`, and 75 mm is below
    the 250 mm grid's own quantisation (`brief.md` §5.3 -- the domain is a THIRD
    quantity). So the projection reads a perimeter Room smaller than the bar
    does, and is strictly stricter than `dim.statutory_min_area` requires.

    This measures the gap on the population that matters -- warped candidates --
    and it is why a candidate can be Proposal-OK on ADR 0001's plane and still be
    refused by the solve on the floor. No solver runs here."""
    by_k = {c["k"]: c for c in cands}
    per_room, per_cand, cross = [], [], 0
    n = both_starved = only_solver = 0
    for r in rows:
        if r.get("prop_starved") is None:
            continue
        b, c = by_k.get(r["brief"]), by_k.get(r["cand"])
        if not b or not c:
            continue
        ct = [COLLAPSE.get(t, t) for t in c["types"]]
        tg = pair_targets(ct, c["parts"], b["rooms"])
        if tg is None:
            continue
        tg = [max(a, MARKET.get(t, 0.0)) for a, t in zip(tg, ct)]
        w = warp_geom(c, b["aspect"], tg, tlim, key=b["k"] + c["k"],
                      hold_ring=True)
        if w["status"] != "OK":
            continue
        floors = floors_m2(w["types"])
        n += 1
        # the solver's plane, on the SAME rectangles: sum over parts of the
        # four-side erosion, which is what `amm` computes per part.
        solver_a = [sum(max(0, (x2 - x1) - T_INT_MM) * max(0, (y2 - y1) - T_INT_MM)
                        for (x1, y1, x2, y2) in pl) / 1e6 for pl in w["solved"]]
        for a1, a0, fl in zip(w["got"], solver_a, floors):
            per_room.append((a1 - a0) / a1 if a1 else 0.0)
            if a1 >= fl > a0:
                cross += 1
        adr = any(g < f for g, f in zip(w["got"], floors))
        sol = any(g < f for g, f in zip(solver_a, floors))
        per_cand.append((sum(w["got"]) - sum(solver_a)) / max(1e-9, sum(w["got"])))
        both_starved += adr and sol
        only_solver += sol and not adr
    return {"candidates": n, "rooms": len(per_room),
            "room_shortfall": {q: round(pct(per_room, v), 4) for q, v in
                               (("p10", .1), ("p50", .5), ("p90", .9))},
            "candidate_shortfall": {q: round(pct(per_cand, v), 4) for q, v in
                                    (("p10", .1), ("p50", .5), ("p90", .9))},
            "rooms_crossing_a_floor": cross,
            "rooms_crossing_share": round(cross / max(1, len(per_room)), 4),
            "starved_on_both_planes": both_starved,
            "starved_only_on_the_solver_plane": only_solver}


def brief_level(rows):
    """What §11.1 actually needs: the share of BRIEFS with no usable candidate,
    read at the Proposal and again at the Plan.

    A per-candidate rate is not this number and 54's README already carries the
    trap -- compounding a per-candidate share into a Brief-level one is 780x
    wrong, because declines are correlated within a Brief (§7.6: conditional
    decline reaches 88.9 % by the seventh candidate). This is the paired
    quantity, computed over the same pool draw on both sides."""
    by = defaultdict(list)
    for r in rows:
        if r.get("prop_starved") is not None:
            by[r["brief_i"]].append(r)
    prop_ok = plan_ok = both = 0
    rescued, n = 0, 0
    depth = []
    for bi, rs in by.items():
        n += 1
        depth.append(len(rs))
        p = any(not r["prop_starved"] for r in rs)
        q = any(r["status"] in ("OPTIMAL", "FEASIBLE") and not r.get("plan_starved")
                for r in rs)
        prop_ok += p
        plan_ok += q
        both += p and q
        rescued += q and not p
    return {"briefs_with_a_pool": n,
            "pool_depth_p50": round(pct(depth, .5), 1) if depth else None,
            "served_at_proposal": prop_ok,
            "served_at_plan": plan_ok,
            "starved_at_proposal_share": round(1 - prop_ok / max(1, n), 4),
            "starved_at_plan_share": round(1 - plan_ok / max(1, n), 4),
            "briefs_the_solve_rescues": rescued}


def summarise(rows):
    """The confusion matrix, and why it is NOT (Proposal-starved x Plan-starved).

    `dim.statutory_min_area` is `site: both`, so the projection **posts** it: a
    Plan that comes back has already met every floor, and Plan-level starvation
    cannot appear as an under-floor Room. It appears as INFEASIBLE. So the
    quantity a Proposal-level screen has to be judged against is *served* --
    the projection returned a Plan -- and the two error modes are:

      FALSE REFUSAL  the screen refuses (Proposal-starved) and the projection
                     would have served it. Pure yield loss, off a pool whose
                     median depth under the shipped gate is 9 at 4-6 rooms and
                     5 at 7-10.
      FALSE PASS     the screen admits and the projection then refuses ON THE
                     FLOOR -- established by ablation, not by assumption, since
                     a refusal can also be H1/H2/H5/H7's or the fixed relations'.
                     Costs one solve slot.
    """
    reached = [r for r in rows if r.get("prop_starved") is not None]
    got = [r for r in reached if r["status"] in ("OPTIMAL", "FEASIBLE")]
    inf = [r for r in reached if r["status"] == "INFEASIBLE"]
    unk = [r for r in reached if r["status"] == "UNKNOWN"]
    out = {
        "candidates": len(rows),
        "reached_the_solve": len(reached),
        "status": dict(Counter(r["status"] for r in rows)),
        "witness_ok": sum(1 for r in reached if r.get("witness_ok")),
        "witness_fails": dict(Counter(f for r in reached
                                      for f in (r.get("witness_fails") or []))),
    }
    if not reached:
        return out
    out["prop_starved_share"] = round(
        sum(1 for r in reached if r["prop_starved"]) / len(reached), 4)

    # A returned Plan that is starved anyway would mean the floor was not posted.
    bad = [r for r in got if r.get("plan_starved")]
    out["served_but_starved"] = len(bad)

    served = {id(r) for r in got if not r.get("plan_starved")}
    floor_refused = {id(r) for r in inf if r.get("refused_by_floor")}
    ps = [r for r in reached if r["prop_starved"]]
    po = [r for r in reached if not r["prop_starved"]]
    out["confusion"] = {
        "prop_starved_served": sum(1 for r in ps if id(r) in served),
        "prop_starved_refused": sum(1 for r in ps if id(r) not in served),
        "prop_ok_served": sum(1 for r in po if id(r) in served),
        "prop_ok_refused": sum(1 for r in po if id(r) not in served),
    }
    if ps:
        out["false_refusal_rate"] = round(
            sum(1 for r in ps if id(r) in served) / len(ps), 4)
    if po:
        out["false_pass_rate"] = round(
            sum(1 for r in po if id(r) in floor_refused) / len(po), 4)
    out["infeasible"] = len(inf)
    out["infeasible_on_the_floor"] = len(floor_refused)
    out["ablate_status"] = dict(Counter(r.get("ablate_status") for r in inf))
    out["unknown"] = len(unk)
    out["served_share"] = round(len(served) / len(reached), 4)

    # R1, the only SOUND cheap screen there is: a candidate whose own derived box
    # cannot hold the sum of its floors. Free -- it is arithmetic on two numbers
    # already in the record -- and its power is the question.
    r1 = [r for r in reached if r.get("sum_floors_m2", 0) > r.get("interior_m2", 0)]
    out["R1_fires"] = len(r1)
    out["R1_fires_share"] = round(len(r1) / len(reached), 4)
    out["R1_false_refusals"] = sum(1 for r in r1 if id(r) in served)
    ratio = [r["sum_floors_m2"] / r["interior_m2"] for r in reached
             if r.get("interior_m2")]
    out["sum_floors_over_interior"] = {q: round(pct(ratio, v), 4) for q, v in
                                       (("p50", .5), ("p90", .9), ("p99", .99),
                                        ("max", 1.0))}

    walls = [r["wall"] for r in reached if "wall" in r]
    out["wall_s"] = {q: round(pct(walls, v), 3) for q, v in
                     (("p10", .1), ("p50", .5), ("p90", .9), ("p99", .99))}
    out["wall_at_cap"] = sum(1 for w in walls if w >= 14.5)
    warps = [r["warp_s"] for r in reached if "warp_s" in r]
    out["warp_s"] = {q: round(pct(warps, v), 3) for q, v in
                     (("p50", .5), ("p90", .9))}
    out["plan_valid"] = sum(1 for r in got if r.get("plan_valid"))
    out["survivors"] = sum(1 for r in got if r.get("survivor"))
    out["plan_fails"] = dict(Counter(f for r in got
                                     for f in (r.get("plan_fails") or [])))
    d = [(sum(r["plan_space"]) - sum(r["prop_space"])) / sum(r["prop_space"])
         for r in got if r.get("plan_space") and sum(r["prop_space"]) > 0]
    out["sum_space_delta"] = {q: round(pct(d, v), 4) for q, v in
                              (("p10", .1), ("p50", .5), ("p90", .9))}

    # Per band, because 7-10 rooms is where 57 found depth buys nothing.
    out["by_band"] = {}
    for lab, lo, hi in (("4-6", 4, 6), ("7-10", 7, 10)):
        band = [r for r in reached if lo <= r["n"] <= hi]
        if not band:
            continue
        bps = [r for r in band if r["prop_starved"]]
        out["by_band"][lab] = {
            "candidates": len(band),
            "prop_starved_share": round(len(bps) / len(band), 4),
            "served_share": round(sum(1 for r in band if id(r) in served)
                                  / len(band), 4),
            "false_refusal_rate": (round(sum(1 for r in bps if id(r) in served)
                                         / len(bps), 4) if bps else None),
        }
    return out


if __name__ == "__main__":
    main()
