"""What `dim.statutory_min_area` costs when the WARP posts it, not the solve.

Ticket 64. `acceptance-bar.md` §11.1 refused a Proposal-level *screen* -- a
filter between the warp and the solve -- on three grounds. It did not decide the
different thing: posting the floor as a hard constraint inside the warp's own
CP-SAT model, which changes what the warp EMITS rather than what survives it.
None of the three grounds transfers: a constraint does not refuse, it re-sizes;
the sound arithmetic form bounds a screen and not the warp's gap variables; and
the warp IS the expensive step, so there is no cheaper half to skip.

## What is posted, and on which plane

Per Room, `sum(part areas) >= floor`, in grid cells. Three properties, each of
which is a decision:

  PER ROOM, NOT PER PART.  `dim.statutory_min_area`'s own statement says so and
  ADR 0014 binds it there. `sum(areas)` is already a variable in the model.

  LINEAR.  The part areas are existing `AddMultiplicationEquality` products and
  the floor is a constant, so the constraint adds NO product. Contrast ADR
  0020's notch invariant, which costs one product per notch cell. This is the
  cheapest constraint on the map.

  ON ADR 0001's PLANE.  The floor is a Space area; the objective runs on
  centreline parts. `part_targets_cells` already converts one to the other with
  `space_m2`'s own erosion -- interior edges only, the Envelope boundary free --
  so the same call converts the floor. That is the plane
  `dim.statutory_min_area` is stated on.

  WARNING: it is NOT `solver.py`'s plane, which erodes all four sides including
  the Envelope's and reads a perimeter Room 3,92 % smaller (p50) than the bar
  does. Mirroring that here would propagate a defect the map has already
  published (`acceptance-bar.md` §11.1) into a second file, so that two
  components agree on being wrong. The gap it leaves is measured below as
  `plane_gap_refusals` and it belongs to a separate ticket.

## The baseline is `both`, not `free`

`proposer.md` §2.2.2 point 6 already puts the void in the programme (ADR 0028)
and ADR 0020's notch invariant is decided, so the SPEC's warp is
`constrained_warp.py`'s `both` arm, not its `free` control. Pricing the floor
against `free` would report it cheaper than production will ever see it. `free`
and `floor` are kept as the historical pair.

## What is reported, and one number is a trap

`worst_dev` RISES BY CONSTRUCTION when the floor binds: the Room grows away from
a target that sat below its own legal floor, and that deviation is the
constraint working, not damage. The honest damage measure is
`worst_dev_unbound` -- worst relative deviation over the Rooms the floor did NOT
move. Quote that one.

Run: python experiments/warp/floor_warp.py [n] [--time=3.0] [--lenient]
"""

from __future__ import annotations

import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fit_warp import (COLLAPSE, GRID_MM, MIN_SIDE, MIN_SIDE_DEFAULT,   # noqa: E402
                      SEED, W_STATED, W_INVENTED, STATED_SHARE,
                      coord_frame, uniform)
from absolute_area import (OUT, MARKET, F_PARTITION,                   # noqa: E402
                           bucket_pool, pair_targets, notch_share, joins,
                           rects_mm, outside_of, space_m2, part_targets_cells,
                           frame_components, realised_frame_areas, pct,
                           floors_for)
from constrained_warp import (NOTCH_TOL, receiving_room,               # noqa: E402
                              warp_model_constrained, load)

ARMS = ("free", "floor", "both", "bothfloor")
FLOOR_ARMS = ("floor", "bothfloor")
NOTCH_ARMS = ("both", "bothfloor")
SOLVER_T_INT = 150              # what `solver.py` erodes on all four sides


def _check_floor_transcription() -> None:
    """`absolute_area.STAT_FLOOR` is a HAND TRANSCRIPTION of
    `room-constraints.json`, and nothing in the repo binds the two.

    That was tolerable while the table only *measured*. It is not tolerable now
    that it CONSTRAINS geometry: a drifted value does not produce a wrong
    number in a report, it produces a warp that sizes rooms to a floor no
    regulator wrote — which is the C8 failure from the inside. Asserted on
    import, in the file that posts the constraint, for the same reason
    `project_join._check_min_side_identity` is.

    ⚠️ This is an assertion, not a fix. The fix is for `STAT_FLOOR` to be READ
    from the JSON rather than copied beside it; see the ticket's resolution."""
    import json as _json
    from pathlib import Path as _P
    from absolute_area import (STAT_FLOOR, STAT_FLOOR_LENIENT,
                               LIVING_1OTAQ, LIVING_2PLUS)
    src = _P(__file__).resolve().parents[2] / "data" / "standards" / "room-constraints.json"
    if not src.exists():                       # rigs may run without the repo data
        return
    areas = _json.load(open(src, encoding="utf-8"))["profiles"]["AZ"]["rooms"]["areas_m2"]

    def floor(key):
        cell = (areas.get(key) or {}).get("statutory_floor")
        return cell["v"] if cell else None

    for code_v, erg_key in ((STAT_FLOOR["KITCHEN"], "kitchen"),
                            (STAT_FLOOR["KITCHEN_DINING"], "kitchen_zone_in_diner"),
                            (STAT_FLOOR["PRIVATE"], "bedroom_double"),
                            (STAT_FLOOR_LENIENT["PRIVATE"], "bedroom_single"),
                            (LIVING_1OTAQ, "living_room_1room_flat"),
                            (LIVING_2PLUS, "living_room_2plus")):
        got = floor(erg_key)
        assert got == code_v, (
            "statutory floor drift: absolute_area has %r for %s, "
            "room-constraints.json publishes %r" % (code_v, erg_key, got))


_check_floor_transcription()


def floors_m2(types, lenient=False):
    """`dim.statutory_min_area` only -- the rule this ticket is about. Where
    AzDTN publishes no floor the entry is 0 and nothing is posted: the ergonomic
    floor is `dim.min_area`'s, a different rule, and `MIN_SIDE` already carries
    its linear half into this model. Posting both would price two rules and
    report one."""
    return [f or 0.0 for f in floors_for(types, lenient=lenient)]


def run_arm(cand, aspect, targets_m2, tlim, arm, key="", lenient=False):
    """One warp under one arm. The box is sized exactly as `constrained_warp`
    and `absolute_area.run_one` size it -- ADR 0020, from the Brief -- so every
    number here is comparable with both."""
    parts, types = cand["parts"], [COLLAPSE.get(t, t) for t in cand["types"]]
    xs, ys, spans = coord_frame(parts)
    if len(xs) < 2 or len(ys) < 2:
        return {"status": "DEGENERATE"}
    s, _void = notch_share(parts)
    if s >= 0.60:
        return {"status": "NOTCH"}
    nx, ny = len(xs) - 1, len(ys) - 1
    notch_cells, void_comps = frame_components(spans, nx, ny)
    owner = {id(c): receiving_room(c, spans, nx, ny) for c in void_comps}

    interior = sum(targets_m2) * (1.0 + F_PARTITION)
    box_m2 = interior / (1.0 - s)
    Hm = (box_m2 * 1e6 / aspect) ** 0.5
    W = max(4, round(aspect * Hm / GRID_MM))
    H = max(4, round(Hm / GRID_MM))

    seed = (uniform(xs, W), uniform(ys, H))
    seed_rects = rects_mm(spans, *seed)
    outside_seed = outside_of(seed_rects)
    tgt_cells = part_targets_cells(targets_m2, seed_rects, outside_seed)
    fl_m2 = floors_m2(types, lenient=lenient)
    # The SAME converter the targets use, so the floor and the objective are
    # stated on one plane. A zero floor stays zero -- `part_targets_cells`
    # returns at least 1 cell, which would post a vacuous but non-None floor.
    fl_cells_all = part_targets_cells(fl_m2, seed_rects, outside_seed)
    fl_cells = [c if f > 0 else 0 for c, f in zip(fl_cells_all, fl_m2)]

    jx, jy = joins(spans)
    rng = random.Random(SEED ^ (hash(key) & 0xFFFF))
    weights = [W_STATED if rng.random() < STATED_SHARE else W_INVENTED
               for _ in types]
    mins = [MIN_SIDE.get(t, MIN_SIDE_DEFAULT) for t in types]

    t0 = time.perf_counter()
    res, name = warp_model_constrained(
        spans, nx, ny, tgt_cells, W, H, weights, mins, jx, jy, tlim, seed=seed,
        notch_cells=notch_cells if arm in NOTCH_ARMS else None,
        notch_share_target=s if arm in NOTCH_ARMS else None,
        void_comps=void_comps if arm in NOTCH_ARMS else None,
        void_owner=owner if arm in NOTCH_ARMS else None,
        weight_void=arm in NOTCH_ARMS, notch_tol=NOTCH_TOL,
        area_floor_cells=fl_cells if arm in FLOOR_ARMS else None)
    dt = time.perf_counter() - t0

    # How much of the programme the floor actually claims -- the arithmetic
    # headroom §11.1's ground 2 turns on, recomputed on THIS sample.
    floor_over_interior = sum(fl_m2) / max(1e-9, interior)
    binding = sum(1 for f in fl_m2 if f > 0)
    if res is None:
        return {"status": name, "secs": round(dt, 3), "donor_s": round(s, 4),
                "floor_rooms": binding,
                "floor_over_interior": round(floor_over_interior, 4)}
    gx, gy, _opt = res
    solved = rects_mm(spans, gx, gy)
    outside = outside_of(solved)
    got = [space_m2(r, outside) for r in solved]
    notch_a, void_a, bbox = realised_frame_areas(notch_cells, void_comps, gx, gy)

    # ADR 0001's plane, measured on the solved geometry -- the posted floor was a
    # seed-shape estimate, so whether it HELD is a measurement and not a claim.
    short = [round(f - g, 4) for g, f in zip(got, fl_m2) if f > 0 and g < f - 1e-9]
    # `solver.py`'s stricter plane on the same rectangles: every part eroded on
    # all four sides. What the projection would read off this same candidate.
    solver_a = [sum(max(0, (x2 - x1) - SOLVER_T_INT) * max(0, (y2 - y1) - SOLVER_T_INT)
                    for (x1, y1, x2, y2) in pl) / 1e6 for pl in solved]
    plane_short = [round(f - a, 4) for a, f in zip(solver_a, fl_m2)
                   if f > 0 and a < f - 1e-9]

    dev = [(abs(g - t) / t, f > 0 and g >= f - 1e-9 and t < f)
           for g, t, f in zip(got, targets_m2, fl_m2) if t > 0]
    # A Room the floor MOVED is one whose target sat below its own legal floor.
    # Its deviation is the constraint working; excluding it is the whole point.
    unbound = [d for d, moved in dev if not moved]
    return {"status": "OK", "secs": round(dt, 3),
            "worst_dev": round(max(d for d, _ in dev), 4) if dev else None,
            "worst_dev_unbound": round(max(unbound), 4) if unbound else None,
            "moved_rooms": sum(1 for _, mv in dev if mv),
            "floor_rooms": binding,
            "floor_over_interior": round(floor_over_interior, 4),
            "floor_short": short, "floor_held": not short,
            "plane_short": plane_short, "plane_held": not plane_short,
            "donor_s": round(s, 4),
            "s_drift": round(notch_a / bbox - s, 4) if bbox else 0.0,
            "void_m2": round(void_a, 4), "n_void_comps": len(void_comps),
            "space_total": round(sum(got), 3)}


def summarise(res, keys, idx, arm, base):
    st = Counter(r["status"] for r in res)
    ok = [r for r in res if r["status"] == "OK"]
    lost = [k for k in keys if idx[base][k]["status"] == "OK"
            and idx[arm][k]["status"] != "OK"]
    gained = [k for k in keys if idx[base][k]["status"] != "OK"
              and idx[arm][k]["status"] == "OK"]
    ub = [r["worst_dev_unbound"] for r in ok if r["worst_dev_unbound"] is not None]
    return {
        "cases": len(res), "status": dict(st),
        "infeasible": st.get("INFEASIBLE", 0),
        "infeasible_share": round(st.get("INFEASIBLE", 0) / max(1, len(res)), 4),
        "ok": len(ok),
        "secs_per_warp_p50": round(pct([r["secs"] for r in res], .5), 3),
        "worst_dev_p50": round(pct([r["worst_dev"] for r in ok], .5), 4),
        "worst_dev_p90": round(pct([r["worst_dev"] for r in ok], .9), 4),
        "worst_dev_unbound_p50": round(pct(ub, .5), 4) if ub else None,
        "worst_dev_unbound_p90": round(pct(ub, .9), 4) if ub else None,
        "moved_rooms_total": sum(r["moved_rooms"] for r in ok),
        "floor_held": sum(1 for r in ok if r["floor_held"]),
        "floor_violations": len(ok) - sum(1 for r in ok if r["floor_held"]),
        "plane_gap_refusals": len(ok) - sum(1 for r in ok if r["plane_held"]),
        "vs_" + base: {"base_ok_arm_not": len(lost), "arm_ok_base_not": len(gained),
                       "net_cost": len(lost) - len(gained),
                       "net_cost_share": round((len(lost) - len(gained))
                                               / max(1, len(keys)), 4)},
    }


def pool_run(sample, by_ms, by_n, tlim, m, lenient, raw):
    """Brief-level survival at pool depth -- the number the per-candidate rate
    cannot give.

    §11.1's own warning: "a per-candidate rate is not this number". The floor
    refuses a share of CANDIDATES; what it costs the product is the share of
    BRIEFS left with no clearing candidate at all, and retrieval draws from a
    pool whose production median is 9 at 4-6 rooms and 5 at 7-10 (§2.2.7). A
    9,9 % candidate cost against a pool of 8 is a very different number from a
    9,9 % Brief cost, and only this arm can tell them apart.

    Reported three ways, because they answer different questions:
      served          -- the Brief has at least one candidate the warp returns
      served_clean    -- at least one candidate that also MEETS every floor
      clean_share     -- of the Briefs served, how many are served cleanly
    """
    out = {}
    for arm in ("both", "bothfloor"):
        served = clean = total = 0
        depth = []
        for brief in sample:
            pool = bucket_pool(brief, by_ms, by_n)
            if not pool:
                continue
            total += 1
            ok = ok_clean = 0
            for cand in pool[:m]:
                ct = [COLLAPSE.get(t, t) for t in cand["types"]]
                tg = pair_targets(ct, cand["parts"], brief["rooms"])
                if tg is None:
                    continue
                if not raw:
                    tg = [max(a, MARKET.get(t, 0.0)) for a, t in zip(tg, ct)]
                r = run_arm(cand, brief["aspect"], tg, tlim, arm,
                            key=brief["k"] + cand["k"], lenient=lenient)
                if r["status"] == "OK":
                    ok += 1
                    ok_clean += bool(r["floor_held"])
            depth.append(ok)
            served += ok > 0
            clean += ok_clean > 0
        out[arm] = {
            "briefs": total, "m": m,
            "served": served,
            "served_share": round(served / max(1, total), 4),
            "served_clean": clean,
            "served_clean_share": round(clean / max(1, total), 4),
            "clean_share_of_served": round(clean / max(1, served), 4),
            "pool_depth_p50": round(pct(depth, .5), 2),
            "pool_depth_p10": round(pct(depth, .1), 2),
        }
        print("  pool arm %-10s served %d/%d  clean %d/%d  depth p50 %.1f"
              % (arm, served, total, clean, total, pct(depth, .5)))
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n_arg = int(args[0]) if args else 150
    tlim = 3.0
    lenient = "--lenient" in sys.argv
    # `constrained_warp` and `absolute_area` both raise every target onto
    # `dim.market_default_area` (kitchen 9,0 against a floor of 8,0; PRIVATE
    # 12,0 against 10,0; living 16,0 against 15/16), which is §11.1 ground 2's
    # own stated condition. Under it NO target sits below its floor, so the
    # constraint can never fight the objective and a fidelity cost cannot
    # appear even in principle. `--raw` drops the raise and uses the donor's
    # own paired areas, which is the case `brief.md` §6.1 permits -- a stated
    # target is sovereign, and §9.4 bounds 1 and 3 still read the ergonomic
    # minimum rather than `max(ergonomic, statutory)`. That is the arm where
    # the floor overrides a sovereign target, and it is the one to quote for
    # fidelity damage.
    raw = "--raw" in sys.argv
    pool_m = 0
    for a in sys.argv[1:]:
        if a.startswith("--pool="):
            pool_m = int(a.split("=", 1)[1])
    for a in sys.argv[1:]:
        if a.startswith("--time="):
            tlim = float(a.split("=", 1)[1])

    cands, by_ms, by_n = load()
    rng = random.Random(SEED)
    sample = rng.sample(cands, min(n_arg, len(cands)))
    print("sample %d Briefs | time %.1fs | PRIVATE floor %s | targets %s | arms %s\n"
          % (len(sample), tlim, "8,0 (single)" if lenient else "10,0 (double)",
             "raw (sovereign)" if raw else "raised onto market_default",
             ",".join(ARMS)))

    if pool_m:
        # Brief-level, at depth. Answers the only question the per-candidate
        # arms cannot: does the floor cost a Brief its whole pool, or does the
        # pool absorb it -- which is what a pool is for (ADR 0005, §11.1 step 1).
        res = pool_run(sample, by_ms, by_n, tlim, pool_m, lenient, raw)
        res["_meta"] = {"briefs_requested": n_arg, "m": pool_m,
                        "time_limit_s": tlim, "seed": SEED,
                        "lenient_private_floor": lenient, "raw_targets": raw}
        print("\n" + json.dumps(res, indent=1))
        OUT.mkdir(exist_ok=True)
        json.dump(res, open(OUT / ("floor_warp_pool%d.json" % pool_m), "w"), indent=1)
        print("\nwrote %s" % (OUT / ("floor_warp_pool%d.json" % pool_m)))
        return

    pairs = []
    for brief in sample:
        pool = bucket_pool(brief, by_ms, by_n)
        if not pool:
            continue
        cand = rng.choice(pool)
        ct = [COLLAPSE.get(t, t) for t in cand["types"]]
        targets = pair_targets(ct, cand["parts"], brief["rooms"])
        if targets is None:
            continue
        if not raw:
            targets = [max(a, MARKET.get(t, 0.0)) for a, t in zip(targets, ct)]
        pairs.append((brief, cand, targets))
    print("paired (Brief, donor) cases: %d\n" % len(pairs))

    rows = {}
    for arm in ARMS:
        res = []
        for brief, cand, targets in pairs:
            r = run_arm(cand, brief["aspect"], targets, tlim, arm,
                        key=brief["k"] + cand["k"], lenient=lenient)
            r["brief"], r["donor"], r["n"] = brief["k"], cand["k"], brief["n"]
            res.append(r)
        rows[arm] = res
        print("  arm %-10s %s" % (arm, dict(Counter(r["status"] for r in res))))

    idx = {a: {(r["brief"], r["donor"]): r for r in rows[a]} for a in ARMS}
    keys = list(idx["free"])
    out = {"free": summarise(rows["free"], keys, idx, "free", "free"),
           "floor": summarise(rows["floor"], keys, idx, "floor", "free"),
           "both": summarise(rows["both"], keys, idx, "both", "free"),
           "bothfloor": summarise(rows["bothfloor"], keys, idx, "bothfloor", "both")}

    # The two-pass shape: post the floor, and where THAT is INFEASIBLE fall back
    # to the unconstrained warp and let the projection decide. It cannot lose a
    # candidate the baseline had, by construction -- this counts how often the
    # second pass fires and what the first pass buys on the rest.
    fired = [k for k in keys if idx["bothfloor"][k]["status"] != "OK"
             and idx["both"][k]["status"] == "OK"]
    both_ok = [k for k in keys if idx["both"][k]["status"] == "OK"]
    out["_two_pass"] = {
        "candidates_baseline_serves": len(both_ok),
        "second_pass_fires": len(fired),
        "second_pass_share": round(len(fired) / max(1, len(both_ok)), 4),
        "floor_posted_on_first_pass": round(1 - len(fired) / max(1, len(both_ok)), 4),
    }
    # Ground 2's arithmetic headroom, recomputed: Sigma statutory floors against
    # the candidate's own derived interior.
    hof = [r["floor_over_interior"] for r in rows["free"]
           if "floor_over_interior" in r]
    out["_headroom"] = {"sum_floors_over_interior":
                        {q: round(pct(hof, v), 4)
                         for q, v in (("p50", .5), ("p90", .9), ("p99", .99))},
                        "max": round(max(hof), 4) if hof else None,
                        "cases": len(hof)}
    out["_meta"] = {"n_requested": n_arg, "cases": len(pairs), "time_limit_s": tlim,
                    "seed": SEED, "lenient_private_floor": lenient,
                    "raw_targets": raw,
                    "baseline": "both (proposer.md 2.2.2 point 6 + ADR 0020)"}

    print("\n" + json.dumps(out, indent=1))
    OUT.mkdir(exist_ok=True)
    suffix = ("_lenient" if lenient else "") + ("_raw" if raw else "")
    json.dump(rows, open(OUT / ("floor_warp_rows%s.json" % suffix), "w"))
    json.dump(out, open(OUT / ("floor_warp%s.json" % suffix), "w"), indent=1)
    print("\nwrote %s" % (OUT / ("floor_warp%s.json" % suffix)))


if __name__ == "__main__":
    main()
