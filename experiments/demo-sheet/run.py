"""Baku Brief -> retrieval -> warp -> projection -> a dimensioned sheet set.

THE FIRST TIME ANYTHING ON THIS MAP HAS BEEN DRAWN. Ticket 59 joined the warp to
the projection and measured it; nothing then asked the result for a drawing.
This closes that: one MIDA Brief becomes a Plan and the Plan becomes sheet 1
(general arrangement, dimensioned, annotated) and sheet 2 (door, window and room
schedules) as PNG and DXF, with `annotation.md` section 13's twelve predicates
run before any file is written.

WHAT IS JOINED, AND WHERE EACH PIECE COMES FROM

  Brief       `briefs_az.py` -- MIDA's own published room schedules, eyvan
              excluded, aspect defaulted from the corpus bucket.
  retrieval   `absolute_area.admissible_pool` -- proposer.md section 2.2.1's
              gate, all three terms, and NOT the bucket. Ticket 60.
  warp        `fit_warp.warp_model` through `project_join.warp_geom`, at
              `hold_ring=True`, so the candidate tiles its Envelope exactly.
  projection  `solver-toy/solver.project` at the shipped config, with ONE
              deliberate change from ticket 59's arm: the four softenable
              families are posted HARD. That arm softened `coverage`,
              `exterior`, `wet_cluster` and `circulation` because it was
              measuring starvation, and 191 of its 273 candidates then failed
              the validator on exactly those rules. A demo sheet is not a
              measurement -- a Plan that reaches the drawing layer has to have
              passed the bar, so the refusals are taken as INFEASIBLE instead.
  drawing     `src/bim_engine` -- openings.md and annotation.md, executed.

Run:
    ./venv/Scripts/python.exe experiments/demo-sheet/run.py            5 briefs
    ./venv/Scripts/python.exe experiments/demo-sheet/run.py 12 --k=8 --otaq=2,3
    ./venv/Scripts/python.exe experiments/demo-sheet/run.py --soft     ticket 59's arm

Writes `out/<brief>-sheet1.png`, `-sheet2.png`, `.dxf` and `out/run.json`.
"""
from __future__ import annotations

import json
import pathlib
import random
import sys
import time
import traceback
from collections import Counter, defaultdict

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)

for p in ("src", "experiments/warp", "experiments/solver-toy",
          "experiments/region-profile", "experiments/rectangularise"):
    sys.path.insert(0, str(ROOT / p))

import briefs_az                                                  # noqa: E402
import project_join                                               # noqa: E402
from absolute_area import MARKET, admissible_pool, pair_targets   # noqa: E402
from project_join import (COLLAPSE, EXPOSURE, GRID_MM, SHIPPED_TAU,   # noqa: E402
                          T_INT_MM, WINDOW_MIN, WORKERS, brief_from_warp,
                          envelope_from_frame, floors_m2, kinds_for, load,
                          rooms_grid, warp_geom)
from scenarios import Proposal                                    # noqa: E402
from solver import SolveConfig, project                           # noqa: E402
from validate import check as validate_check                      # noqa: E402

from bim_engine import (build, check, dimensions, dxf, openings,   # noqa: E402
                        preview, profile, sheet as sheet_mod, tags)

SEED = 20260830
SOFT_FAMILIES = ("coverage", "exterior", "wet_cluster", "circulation")


def adr_0021_door_min(keys, arm="max"):
    """ADR 0021 / openings.md section 8, in grid units, for one Brief.

    `circ.potential_reachability` admits a contact edge at `structural opening
    width + t_int + 400`, because a clear run of `w + 400` is what section 3.2's
    jamb-and-nib arithmetic needs and a centreline run loses `t_int` to the two
    perpendicular walls. THE RIG DOES NOT POST THAT. `real_arm.DOOR_MIN_ADR` is
    a single `mm(1.0)` -- 1000 mm centreline, 850 clear at t_int 150 -- which is
    below every door in the catalogue: a 700 door needs 1100 clear, a 900 needs
    1300.

    The consequence is the one openings.md section 8 predicts in terms: a solve
    passes potential circulation on a run and the placement layer then has
    nowhere to put the door. It is not hypothetical -- the first ten Briefs run
    through this pipeline produced it twice, on 2-otaq dwellings, as
    `no door run reaches R01, R05`.

    `Brief.door_min` is ONE SCALAR, so this posts the Brief's WIDEST receiving
    door and over-reserves for a wc by 200 mm. Making it per-pair is a change to
    `solver-toy/solver.py`'s `_contact`, which belongs to whoever holds ticket
    43; it is written up rather than done here.
    """
    import math
    ws = []
    for k in keys:
        try:
            ws.append(int(profile.catalogue(
                profile.door_entry_for(k))["opening_w"]))
        except KeyError:
            continue                       # hall / corridor never receive
    if not ws:
        return project_join.DOOR_MIN_ADR
    w = max(ws) if arm == "max" else min(ws)
    need = (w + profile.T_INT_MM + profile.JAMB_RETURN_MM
            + profile.LEADING_EDGE_NIB_MM)
    return int(math.ceil(need / profile.GRID_MM))


# ---------------------------------------------------------------------------
# Serving one Brief
# ---------------------------------------------------------------------------
def erg_keys_for(types):
    """Corpus labels -> ergonomic keys, with the first CORRIDOR becoming the
    invented `hall`. `resolve` invents exactly one hall (openings.md section 7),
    and `corridor` is `reachable_in_v1: false`, so a donor carrying two is a
    donor v1's vocabulary cannot express."""
    out, seen = [], False
    for t in types:
        k = profile.erg_key(t)
        if k == "corridor" and not seen:
            k, seen = "hall", True
        out.append(k)
    return out, seen


def serve(brief, by_ms, k, tlim, limit, soft, rng, door_min_mode="adr"):
    """Best of pool -- C6's own semantics. Every admitted donor is warped and
    projected; the survivors are ranked and the best one is drawn."""
    pool = admissible_pool(brief, by_ms)
    rec = {"brief": brief["k"], "otaq": brief["otaq"], "n": brief["n"],
           "target_m2": brief["area"], "listed_m2": brief["listed_internal_m2"],
           "eyvan_m2": brief["eyvan_m2"], "pool": len(pool), "tried": 0,
           "warp_refused": 0, "infeasible": 0, "invalid": 0,
           "unplaceable": 0, "candidates": []}
    if not pool:
        rec["status"] = "no_pool"        # section 2.2.1: hand it to source B
        return rec, None
    picks = rng.sample(pool, min(k, len(pool)))
    best = None
    for cand in picks:
        rec["tried"] += 1
        try:
            got = _one(brief, cand, tlim, limit, soft, door_min_mode)
        except Exception as exc:                      # noqa: BLE001
            rec["candidates"].append({"cand": cand["k"], "status": "error",
                                      "detail": repr(exc)})
            continue
        rec["candidates"].append(got["row"])
        if got["row"]["status"].startswith("warp_"):
            rec["warp_refused"] += 1
        elif got["row"]["status"] == "INFEASIBLE":
            rec["infeasible"] += 1
        elif not got["row"]["valid"]:
            rec["invalid"] += 1
        elif not got["row"].get("placed"):
            rec["unplaceable"] += 1
        elif best is None or got["row"]["worst_dev"] < best["row"]["worst_dev"]:
            best = got
    rec["status"] = "served" if best else "no_survivor"
    if best:
        rec["chosen"] = best["row"]
    return rec, best


def _one(brief, cand, tlim, limit, soft, door_min_mode="adr"):
    ct = [COLLAPSE.get(t, t) for t in cand["types"]]
    targets = pair_targets(ct, cand["parts"], brief["rooms"])
    row = {"cand": cand["k"], "n": cand["n"]}
    if targets is None:
        row["status"] = "warp_no_pairing"
        return {"row": row}
    targets = [max(a, MARKET.get(t, 0.0)) for a, t in zip(targets, ct)]

    t0 = time.perf_counter()
    w = warp_geom(cand, brief["aspect"], targets, tlim,
                  key=brief["k"] + cand["k"], hold_ring=True)
    row["warp_s"] = round(time.perf_counter() - t0, 3)
    if w["status"] != "OK":
        row["status"] = "warp_" + w["status"]
        return {"row": row}

    types = w["types"]
    kinds, has_hall = kinds_for(types)
    if not has_hall:
        row["status"] = "warp_no_hall"
        return {"row": row}
    floors = floors_m2(types)
    env = envelope_from_frame(w["spans"], w["gx"], w["gy"], EXPOSURE)
    rooms = rooms_grid(w["spans"], w["gx"], w["gy"])
    keys, _ = erg_keys_for(types)
    # `brief_from_warp` reads `project_join.DOOR_MIN_ADR` at call time for BOTH
    # the posted `door_min` and the required-adjacency sample, so the two cannot
    # be raised separately -- and raising only one would post a required
    # adjacency the threshold then refuses.
    was = project_join.DOOR_MIN_ADR
    if door_min_mode in ("max", "min"):
        project_join.DOOR_MIN_ADR = adr_0021_door_min(keys, door_min_mode)
    row["door_min_units"] = project_join.DOOR_MIN_ADR
    try:
        b = brief_from_warp("demo-%d" % cand["n"], env, rooms, types, kinds,
                            floors, SEED)
    finally:
        project_join.DOOR_MIN_ADR = was
    proposal = Proposal(boxes=[rr[0] for rr in rooms], kinds=kinds,
                        label="warped")
    cfg = SolveConfig(workers=WORKERS, time_limit_s=limit, seed=SEED,
                      fix_relations=True, relation_confidence=SHIPPED_TAU,
                      soft=SOFT_FAMILIES if soft else (),
                      area_units="mm_affine", erode_minima=True,
                      t_int_mm=T_INT_MM, window_min=WINDOW_MIN)
    t0 = time.perf_counter()
    res = project(b, proposal, cfg)
    row["solve_s"] = round(time.perf_counter() - t0, 3)
    row["status"] = res.status
    if not res.rooms:
        row["valid"] = False
        row["worst_dev"] = 9e9
        return {"row": row}

    v = validate_check(b, res.rooms[:len(types)], window_min=WINDOW_MIN)
    row["valid"] = bool(v["ok"])
    row["fails"] = sorted({f.split(" ")[0] for f in v["failures"]}) or None

    got = [_space_m2(r) for r in res.rooms[:len(types)]]
    row["worst_dev"] = round(max(abs(g - t) / max(t, 1e-6)
                                 for g, t in zip(got, targets)), 4)
    row["sum_space_m2"] = round(sum(got), 3)
    row["target_sum_m2"] = round(sum(targets), 3)

    out = {"row": row, "env": env, "res": res, "types": types,
           "targets": targets, "brief": b}
    if not row["valid"]:
        return out
    # PLACEMENT IS PART OF SERVING, NOT PART OF DRAWING. openings.md section 4.2
    # step 3 rejects a Plan whose doors cannot be placed and does not re-solve
    # it, so a candidate that cannot be drawn is not a survivor -- and with a
    # pool behind it the right answer is the next donor, not a sheet with a door
    # missing.
    try:
        plan = to_plan(brief["k"], out, {})
        openings.place(plan)
        out["plan"] = plan
        row["placed"] = True
    except Exception as exc:                          # noqa: BLE001
        row["placed"] = False
        row["place_error"] = str(exc)[:200]
    return out


def _space_m2(r):
    """ADR 0001's erosion, on ADR 0010's finished face -- the same quantity
    `absolute_area.space_m2` publishes, for one rectangle."""
    w = r.w * GRID_MM - T_INT_MM
    h = r.h * GRID_MM - T_INT_MM
    return max(0, w) * max(0, h) / 1e6


# ---------------------------------------------------------------------------
# Plan and sheets
# ---------------------------------------------------------------------------
def to_plan(name, got, provenance):
    env, res, types = got["env"], got["res"], got["types"]
    keys, _ = erg_keys_for(types)
    parts = [[(r.x1, r.y1, r.x2, r.y2)] for r in res.rooms[:len(types)]]
    notches = [(n.x1, n.y1, n.x2, n.y2) for n in env.notches]
    plan = build.make_plan(name, env.W, env.H, notches, env.all_faces(),
                           parts, list(types), keys, entrance_side="N",
                           provenance=provenance)
    plan.entrance_side = pick_entrance_side(plan)
    return plan


def pick_entrance_side(plan):
    """ADR 0003 section 7 fixes the entrance edge before the solve, by SIDE and
    never by ring index. This rig has no such field on the record, so it is
    chosen here and declared: the side the hall meets, PARTY BEFORE EXTERIOR --
    a flat's front door comes off the common landing, and a party edge hosts no
    window, so spending it on the entrance costs the dwelling nothing."""
    halls = [s for s in plan.spaces if s.key == "hall"]
    if not halls:
        return "N"
    hall = halls[0]
    best = None
    for run in openings.envelope_runs(plan):
        if hall.ref not in (run.a, run.b):
            continue
        f = openings.face_for_run(plan, run)
        if f is None or f.side is None:
            continue
        key = (f.is_exterior, -run.length, f.side)
        if best is None or key < best[0]:
            best = (key, f.side)
    return best[1] if best else "N"


def draw(plan, job, stem, audience="practitioner"):
    if not plan.openings:
        openings.place(plan)
    wall = build.wall_region(plan)
    foot = build.footprint(plan)
    fx0, fy0, fx1, fy1 = foot.bounds
    # The ladder depends on the scale (a sub-rung is paper millimetres) and the
    # scale depends on how far the ladder reaches, so it is solved by taking the
    # ladder at the first rung of section 9's list and re-deriving if the sheet
    # that falls out is at a different scale.
    dims = dimensions.derive(plan, sheet_mod.LADDER[0][1])
    sh = sheet_mod.choose(plan, dims, (int(fx1 - fx0), int(fy1 - fy0)))
    if sh.scale != sheet_mod.LADDER[0][1]:
        dims = dimensions.derive(plan, sh.scale)
        sh = sheet_mod.choose(plan, dims, (int(fx1 - fx0), int(fy1 - fy0)))
    tg = tags.place(plan, sh.scale,
                    obstacles=tags.obstacles_for(plan, dims, sh.scale))
    a1 = sheet_mod.title_attribs(plan, sh, job, 1, 2)
    a2 = sheet_mod.title_attribs(plan, sh, job, 2, 2)
    notes = sheet_mod.general_notes(plan)
    preview.sheet1(plan, dims, tg, sh, wall, foot, a1, notes,
                   str(OUT / (stem + "-sheet1.png")))
    preview.sheet2(plan, sh, a2, str(OUT / (stem + "-sheet2.png")))

    # section 1's OTHER presentation, from the SAME derivation. The eager
    # preview renders the `both` audience -- poche, swings, glazing, room tags
    # and nothing else: no chains, no opening marks, no sheet furniture, no area
    # fraction. One derivation, one override key space, no second annotation
    # engine to drift against the first. The tag ladder is audience-split at
    # step 2 (section 7.1), so a tag that would degrade to a bare room number
    # here leaders out instead, because the room schedule it would point at is
    # `practitioner` and this presentation filters it out.
    tg_home = tags.place(plan, sh.scale, audience="both",
                         obstacles=tags.obstacles_for(plan, dims, sh.scale))
    preview.sheet1(plan, dims, tg_home, sh, wall, foot, a1, notes,
                   str(OUT / (stem + "-preview.png")), audience="both")
    path, report = dxf.write(plan, dims, tg, sh, wall, foot, a1, a2, notes,
                             str(OUT / (stem + ".dxf")), enforce=False)
    return {"sheet": sh.size, "scale": sh.scale,
            "extent_paper": [round(v, 1) for v in sh.extent_paper],
            "doors": len([o for o in plan.openings if o.is_door]),
            "windows": len([o for o in plan.openings if o.kind == "window"]),
            "chains": len(dims.chains), "runnings": len(dims.runnings),
            "tag_ladder": sorted({t.step for t in tg}),
            "tag_ladder_preview": sorted({t.step for t in tg_home}),
            "check": {k: v[0] for k, v in report.results.items()},
            "check_failures": report.failures,
            "dxf": pathlib.Path(path).name}


# ---------------------------------------------------------------------------
def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n = int(args[0]) if args else 5
    k = 8
    tlim, limit = 3.0, 15.0
    soft = "--soft" in sys.argv
    # THREE ARMS ON ONE THRESHOLD, paired on the same Briefs and the same
    # donors. `rig` is what the map posts today; `min` and `max` are ADR 0021
    # read at the narrowest and the widest catalogue door, which are the two
    # ways a per-pair rule can be forced into `Brief.door_min`'s one scalar.
    door_min_mode = "max"
    for a in sys.argv[1:]:
        if a.startswith("--door-min="):
            door_min_mode = a.split("=", 1)[1]
    if "--rig-door-min" in sys.argv:
        door_min_mode = "rig"
    otaq = [2, 3]
    draw_sheets = "--no-draw" not in sys.argv
    for a in sys.argv[1:]:
        if a.startswith("--k="):
            k = int(a.split("=", 1)[1])
        if a.startswith("--time="):
            tlim = float(a.split("=", 1)[1])
        if a.startswith("--limit="):
            limit = float(a.split("=", 1)[1])
        if a.startswith("--otaq="):
            otaq = [int(x) for x in a.split("=", 1)[1].split(",")]

    cands = load()
    by_ms = defaultdict(list)
    for c in cands:
        by_ms[c["ms"]].append(c)
    print("converted donors joined to the room cache: %d" % len(cands))

    briefs = briefs_az.build(by_ms, otaq=otaq)
    print("MIDA Briefs: %s" % json.dumps(briefs_az.census(briefs)))
    rng = random.Random(SEED)
    rng.shuffle(briefs)
    briefs = briefs[:n]

    rows, drawn = [], 0
    for b in briefs:
        t0 = time.perf_counter()
        rec, best = serve(b, by_ms, k, tlim, limit, soft, rng, door_min_mode)
        rec["serve_s"] = round(time.perf_counter() - t0, 2)
        if best is not None:
            prov = {"brief": b["k"], "donor": best["row"]["cand"],
                    "otaq": b["otaq"], "target_m2": b["area"],
                    "listed_m2": b["listed_internal_m2"],
                    "aspect_src": b["aspect_src"]}
            job = {"project": "%d otaq · Bakı · %s m²"
                   % (b["otaq"], ("%.1f" % b["area"]).replace(".", ",")),
                   "job": b["k"].upper(), "client": "demo"}
            try:
                plan = best.get("plan") or to_plan(b["k"], best, prov)
                plan.provenance = prov
                if draw_sheets:
                    rec["drawing"] = draw(plan, job, b["k"])
                    drawn += 1
            except Exception as exc:                  # noqa: BLE001
                rec["drawing"] = {"error": repr(exc),
                                  "trace": traceback.format_exc()[-900:]}
        rows.append(rec)
        d = rec.get("drawing", {})
        print("  %-9s otaq=%d n=%-2d pool=%-4d %-12s %s"
              % (b["k"], b["otaq"], b["n"], rec["pool"], rec["status"],
                 ("%s 1:%d  %d doors  %d windows  check %s"
                  % (d.get("sheet"), d.get("scale", 0), d.get("doors", 0),
                     d.get("windows", 0),
                     "OK" if not d.get("check_failures") else
                     d.get("check_failures"))
                  if "sheet" in d else d.get("error", ""))), flush=True)

    summary = {"briefs": len(rows), "drawn": drawn,
               "served": sum(1 for r in rows if r["status"] == "served"),
               "no_pool": sum(1 for r in rows if r["status"] == "no_pool"),
               "no_survivor": sum(1 for r in rows if r["status"] == "no_survivor"),
               "soft_families": SOFT_FAMILIES if soft else (),
               "door_min": door_min_mode,
               "unplaceable_candidates": sum(r["unplaceable"] for r in rows),
               "tried_candidates": sum(r["tried"] for r in rows),
               "pool_k": k, "seed": SEED, "otaq": otaq,
               "check_all_pass": all(not r.get("drawing", {}).get("check_failures")
                                     for r in rows if "drawing" in r),
               "rows": rows}
    (OUT / ("run_%s.json" % door_min_mode)).write_text(
        json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUT / "run.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False),
                                  encoding="utf-8")
    print()
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"},
                     indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
