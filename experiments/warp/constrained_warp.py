"""The warp model with the two constraints it owes, and what they cost.

Ticket 57, obligation 2. `fit_warp.warp_model` is the shipped warp and it posts
neither of the two constraints this map has since decided it holds:

  **ADR 0020's amendment** -- the notch share is held at the `s` the box was
  derived from. `absolute_area.py`'s `ring` / `ringmarket` / `ringpool` arms
  reach that invariant by **re-sizing the box** in a fixed point, deliberately,
  because pinning the cut lines means editing `warp_model`, which carries ADR
  0018's published numbers. So the invariant has been *arrived at* and never
  *posted*.

  **ADR 0028** -- the enclosed void is charged to its receiving Room and
  weighted. `experiments/void/` measured this one at 9/90 INFEASIBLE on all four
  arms, but against the **free** notch.

Both constrain the same solve, so their joint INFEASIBLE cost is one number and
not two. That number is what this measures.

## The encoding

The frame's cell *set* is fixed by `spans` -- which cells a part covers is
combinatorial and the warp moves only the gap sizes -- so the complement's
components are fixed too, and only their areas move. That is what makes both
constraints cheap:

    total uncovered  =  W*H - sum(area_r)          linear, W*H is a CONSTANT
    void             =  sum over enclosed cells of gx[i]*gy[j]
    notch            =  total uncovered - void

Only the **void** needs per-cell products, and voids are small (p50 zero cells).
The notch -- the big region -- falls out by subtraction with no product at all.

Arms, paired on the same candidates:

  `free`     -- `warp_model` as shipped. The control.
  `notch`    -- notch share pinned to the donor's `s`.
  `void`     -- void charged to its receiving Room and weighted.
  `both`     -- the genuinely constrained model. Nothing on this map has run it.

Run: python experiments/warp/constrained_warp.py [n] [--time=3.0] [--census]
"""

from __future__ import annotations

import json
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from ortools.sat.python import cp_model

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fit_warp import (COLLAPSE, GRID_MM, MIN_SIDE, MIN_SIDE_DEFAULT,   # noqa: E402
                      SEED, ASPECT_HARD, JOIN_UNITS, W_STATED, W_INVENTED,
                      STATED_SHARE, coord_frame, uniform)
from absolute_area import (FIT, ROOMS, OUT, MARKET, F_PARTITION,       # noqa: E402
                           bucket_pool, pair_targets, notch_share, joins,
                           rects_mm, outside_of, space_m2, part_targets_cells,
                           frame_components, realised_frame_areas, pct)

ARMS = ("free", "notch", "void", "both")
NOTCH_TOL = 0.02        # share points; the frame is integer cells and `s` is not


def receiving_room(comp, spans, nx, ny):
    """ADR 0028: the donor's own recorded owner. This corpus record does not
    carry it yet -- §2.2.1 lists `voids` as one of five fields `fit_rects.py`
    still owes -- so this uses 2.2.8's own stated fallback, the largest
    bordering Room, which is what the spec says to do where the record is
    missing. It is the fallback, not the rule, and it is why this rig prices the
    constraint's COST and not its fidelity."""
    owner = defaultdict(int)
    cells = set(comp)
    for r, parts in enumerate(spans):
        for (a, b, c, d) in parts:
            for (x, y) in cells:
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if a <= x + dx < b and c <= y + dy < d:
                        owner[r] += 1
    if not owner:
        return None
    best = max(owner.items(), key=lambda kv: kv[1])[0]
    return best


def warp_model_constrained(spans, nx, ny, targets, W, H, weights, min_side,
                           joins_x, joins_y, tlim, seed=None,
                           notch_cells=None, notch_share_target=None,
                           void_comps=None, void_owner=None, weight_void=False,
                           notch_tol=NOTCH_TOL, area_floor_cells=None):
    """`fit_warp.warp_model` plus the two constraints. Deliberately a COPY and
    not an edit: `fit_warp.py` carries ADR 0018's published numbers and ticket 56
    declined to touch it for the same reason."""
    m = cp_model.CpModel()
    gx = [m.NewIntVar(1, W, "gx%d" % i) for i in range(nx)]
    gy = [m.NewIntVar(1, H, "gy%d" % j) for j in range(ny)]
    m.Add(sum(gx) == W)
    m.Add(sum(gy) == H)
    for lo, hi in joins_x:
        if hi > lo:
            m.Add(sum(gx[lo:hi]) >= JOIN_UNITS)
    for lo, hi in joins_y:
        if hi > lo:
            m.Add(sum(gy[lo:hi]) >= JOIN_UNITS)

    cell = {}

    def cell_area(i, j):
        """gx[i] * gy[j], memoised. The only products the constraints add."""
        if (i, j) not in cell:
            v = m.NewIntVar(1, W * H, "c%d_%d" % (i, j))
            m.AddMultiplicationEquality(v, [gx[i], gy[j]])
            cell[(i, j)] = v
        return cell[(i, j)]

    # ADR 0028: each enclosed component's area, charged to its receiving Room.
    charged = defaultdict(list)
    void_terms = []
    for comp in (void_comps or []):
        r = void_owner.get(id(comp)) if void_owner else None
        area_terms = [cell_area(i, j) for (i, j) in comp]
        void_terms.extend(area_terms)
        if r is not None:
            charged[r].extend(area_terms)

    room_areas = []
    devs = []
    for r, parts in enumerate(spans):
        areas = []
        for p, (a, b, c, d) in enumerate(parts):
            wv = m.NewIntVar(1, W, "w%d_%d" % (r, p))
            hv = m.NewIntVar(1, H, "h%d_%d" % (r, p))
            m.Add(wv == sum(gx[a:b]))
            m.Add(hv == sum(gy[c:d]))
            m.Add(wv >= min_side[r])
            m.Add(hv >= min_side[r])
            m.Add(wv <= ASPECT_HARD * hv)
            m.Add(hv <= ASPECT_HARD * wv)
            av = m.NewIntVar(1, W * H, "a%d_%d" % (r, p))
            m.AddMultiplicationEquality(av, [wv, hv])
            areas.append(av)
        area = sum(areas) + sum(charged.get(r, []))   # ADR 0028's charge
        room_areas.append(sum(areas))
        # Ticket 64: `dim.statutory_min_area`, posted HARD, per Room and not per
        # part (ADR 0014 -- and the rule's own statement says so). LINEAR: the
        # part areas are already variables and the floor is a constant, so this
        # adds no product to a model whose cost is its multiplications. The
        # constant arrives in cells from `part_targets_cells`, which converts a
        # Space area with `space_m2`'s own erosion rule -- so the floor binds on
        # ADR 0001's plane, the one `dim.statutory_min_area` is stated on, and
        # NOT on `solver.py`'s stricter four-side one.
        if area_floor_cells is not None and area_floor_cells[r]:
            m.Add(area >= area_floor_cells[r])
        e = m.NewIntVar(0, 20_000, "e%d" % r)
        m.Add(e * targets[r] >= 1000 * (area - targets[r]))
        m.Add(e * targets[r] >= 1000 * (targets[r] - area))
        devs.append(e)

    # ADR 0020's amendment, over exactly the region `s` measures.
    #
    # The tempting encoding is `W*H - sum(part areas) - void`, which is linear and
    # free. It is also WRONG on 27,5 % of donors: `notch_share` defines `s` as the
    # **two largest** boundary-touching components, and 27,5 % of the corpus has
    # three or more, so the free encoding holds a region strictly larger than the
    # one the ADR names. Constrain the cells `s` is actually read off, at the cost
    # of one product per notch cell (p50 6, p90 12 -- next to the model's own
    # ~2 x rooms, nothing).
    if notch_share_target is not None and notch_cells:
        lo = int(round(max(0.0, notch_share_target - notch_tol) * W * H))
        hi = int(round(min(1.0, notch_share_target + notch_tol) * W * H))
        notch_expr = sum(cell_area(i, j) for (i, j) in notch_cells)
        m.Add(notch_expr >= lo)
        m.Add(notch_expr <= hi)

    worst = m.NewIntVar(0, 20_000, "worst")
    m.AddMaxEquality(worst, devs)
    obj = worst * (1000 * len(devs)) + sum(weights[r] * d
                                           for r, d in enumerate(devs))
    if weight_void and void_terms:
        # 2.2.8's `weighted` term: the void is no longer a free sink. Weighted at
        # the stated-room weight so it is comparable to a Room's own deviation.
        obj = obj + W_STATED * sum(void_terms)
    m.Minimize(obj)

    if seed:
        sx, sy = seed
        for v, val in zip(gx, sx):
            m.AddHint(v, val)
        for v, val in zip(gy, sy):
            m.AddHint(v, val)

    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = tlim
    s.parameters.num_workers = 1
    st_ = s.Solve(m)
    name = s.StatusName(st_)
    if st_ not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, name
    return ([s.Value(v) for v in gx], [s.Value(v) for v in gy],
            st_ == cp_model.OPTIMAL), name


def run_arm(cand, aspect, targets_m2, tlim, arm, key="", notch_tol=NOTCH_TOL):
    """One warp under one arm. The box is sized exactly as `absolute_area.run_one`
    sizes it -- ADR 0020, from the Brief -- so the arms are comparable to it."""
    parts, types = cand["parts"], [COLLAPSE.get(t, t) for t in cand["types"]]
    xs, ys, spans = coord_frame(parts)
    if len(xs) < 2 or len(ys) < 2:
        return {"status": "DEGENERATE"}
    s, void = notch_share(parts)
    if s >= 0.60:
        return {"status": "NOTCH"}
    nx, ny = len(xs) - 1, len(ys) - 1
    notch_cells, void_comps = frame_components(spans, nx, ny)
    owner = {}
    for comp in void_comps:
        owner[id(comp)] = receiving_room(comp, spans, nx, ny)

    target_area = sum(targets_m2)
    interior = target_area * (1.0 + F_PARTITION)
    box_m2 = interior / (1.0 - s)
    Hm = (box_m2 * 1e6 / aspect) ** 0.5
    W = max(4, round(aspect * Hm / GRID_MM))
    H = max(4, round(Hm / GRID_MM))

    seed = (uniform(xs, W), uniform(ys, H))
    seed_rects = rects_mm(spans, *seed)
    tgt_cells = part_targets_cells(targets_m2, seed_rects, outside_of(seed_rects))
    jx, jy = joins(spans)
    rng = random.Random(SEED ^ (hash(key) & 0xFFFF))
    weights = [W_STATED if rng.random() < STATED_SHARE else W_INVENTED
               for _ in types]
    mins = [MIN_SIDE.get(t, MIN_SIDE_DEFAULT) for t in types]

    t0 = time.perf_counter()
    res, name = warp_model_constrained(
        spans, nx, ny, tgt_cells, W, H, weights, mins, jx, jy, tlim, seed=seed,
        notch_cells=notch_cells if arm in ("notch", "both") else None,
        notch_share_target=s if arm in ("notch", "both") else None,
        void_comps=void_comps if arm in ("void", "both") else None,
        void_owner=owner if arm in ("void", "both") else None,
        weight_void=arm in ("void", "both"), notch_tol=notch_tol)
    dt = time.perf_counter() - t0
    if res is None:
        return {"status": name, "secs": round(dt, 3),
                "n_void_comps": len(void_comps), "donor_s": round(s, 4)}
    gx, gy, _opt = res
    solved = rects_mm(spans, gx, gy)
    outside = outside_of(solved)
    got = [space_m2(r, outside) for r in solved]
    # Read off the FRAME, never off the millimetre geometry: `notch_share` flood
    # fills a boolean array one cell per square millimetre, which on solved
    # geometry is ~80 million cells a plan.
    notch_a, void_a, bbox = realised_frame_areas(notch_cells, void_comps, gx, gy)
    s_real = notch_a / bbox if bbox else 0.0
    dev = [abs(g - t) / t for g, t in zip(got, targets_m2) if t > 0]
    return {"status": "OK", "secs": round(dt, 3), "got": got,
            "worst_dev": round(max(dev), 4) if dev else None,
            "donor_s": round(s, 4), "s_realised": round(s_real, 4),
            "s_drift": round(s_real - s, 4),
            "void_m2": round(void_a, 4),
            "donor_void_m2": round(void * bbox, 4),
            "n_void_comps": len(void_comps), "bbox_m2": round(bbox, 3),
            "space_total": round(sum(got), 3), "target_area": round(target_area, 3)}


def load():
    recs = {r["k"]: r for r in json.load(open(ROOMS))}
    fits = [r for r in json.load(open(FIT)) if r["status"] in ("OPTIMAL", "FEASIBLE")]
    cands = []
    for f in fits:
        r = recs.get(f["k"])
        if not r or f["n"] != r["n"]:
            continue
        c = dict(f)
        c.update(area=r["area"], aspect=r["aspect"], rooms=r["rooms"], k=f["k"])
        c["ms"] = tuple(sorted(Counter(COLLAPSE.get(t, t)
                                       for t, _ in r["rooms"]).items()))
        cands.append(c)
    by_ms, by_n = defaultdict(list), defaultdict(list)
    for c in cands:
        by_ms[c["ms"]].append(c)
        by_n[c["n"]].append(c)
    return cands, by_ms, by_n


def census(cands, n):
    """How big is the frame, and how many cells do the constraints touch? The
    encoding above is only cheap if the void is small; this is the check."""
    rng = random.Random(SEED)
    sel = rng.sample(cands, min(n, len(cands)))
    nxs, nys, cells, notches, voids, ncomp = [], [], [], [], [], []
    for c in sel:
        xs, ys, spans = coord_frame(c["parts"])
        if len(xs) < 2 or len(ys) < 2:
            continue
        nx, ny = len(xs) - 1, len(ys) - 1
        nc, vc = frame_components(spans, nx, ny)
        nxs.append(nx)
        nys.append(ny)
        cells.append(nx * ny)
        notches.append(len(nc))
        voids.append(sum(len(v) for v in vc))
        ncomp.append(len(vc))
    print("frame census over %d donors" % len(nxs))
    for name, v in (("nx", nxs), ("ny", nys), ("cells nx*ny", cells),
                    ("notch cells", notches), ("void cells", voids),
                    ("void components", ncomp)):
        print("  %-18s p50 %6.1f  p90 %6.1f  p99 %6.1f  max %6d"
              % (name, pct(v, .5), pct(v, .9), pct(v, .99), max(v)))
    print("  donors with any void: %.1f%%"
          % (100 * sum(1 for v in ncomp if v) / max(1, len(ncomp))))
    print("\nProducts the constraints add = void cells (the notch falls out of")
    print("W*H - sum(part areas), which is linear). Compare to the model's own")
    print("~2 x rooms multiplications.")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n_arg = int(args[0]) if args else 150
    tlim = 3.0
    for a in sys.argv[1:]:
        if a.startswith("--time="):
            tlim = float(a.split("=", 1)[1])

    cands, by_ms, by_n = load()
    print("converted dwellings joined to the room cache: " + format(len(cands), ","))
    if "--census" in sys.argv:
        census(cands, 600)
        return

    rng = random.Random(SEED)
    sample = rng.sample(cands, min(n_arg, len(cands)))
    print("sample %d Briefs | time %.1fs | arms %s\n"
          % (len(sample), tlim, ",".join(ARMS)))

    # One candidate per Brief, drawn once and shared by every arm: the arms are
    # PAIRED on the same (Brief, donor) pair, so a difference between them is the
    # constraint and not the draw.
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
        targets = [max(a, MARKET.get(t, 0.0)) for a, t in zip(targets, ct)]
        pairs.append((brief, cand, targets))
    print("paired (Brief, donor) cases: %d\n" % len(pairs))

    out, rows = {}, {}
    for arm in ARMS:
        res, t0 = [], time.perf_counter()
        for brief, cand, targets in pairs:
            r = run_arm(cand, brief["aspect"], targets, tlim, arm,
                        key=brief["k"] + cand["k"])
            r["brief"] = brief["k"]
            r["donor"] = cand["k"]
            r["n"] = brief["n"]
            res.append(r)
        rows[arm] = res
        st = Counter(r["status"] for r in res)
        ok = [r for r in res if r["status"] == "OK"]
        voided = [r for r in ok if r["n_void_comps"] > 0]
        out[arm] = {
            "cases": len(res), "status": dict(st),
            "infeasible": st.get("INFEASIBLE", 0),
            "infeasible_share": round(st.get("INFEASIBLE", 0) / max(1, len(res)), 4),
            "ok": len(ok),
            "secs_total": round(time.perf_counter() - t0, 1),
            "secs_per_warp_p50": round(pct([r["secs"] for r in res], .5), 3),
            "worst_dev_p50": round(pct([r["worst_dev"] for r in ok], .5), 4),
            "worst_dev_p90": round(pct([r["worst_dev"] for r in ok], .9), 4),
            "s_drift_p50": round(pct([r["s_drift"] for r in ok], .5), 4),
            "s_drift_p90": round(pct([abs(r["s_drift"]) for r in ok], .9), 4),
            "void_m2_p50": round(pct([r["void_m2"] for r in ok], .5), 4),
            "void_m2_p90": round(pct([r["void_m2"] for r in ok], .9), 4),
            "void_m2_max": round(max([r["void_m2"] for r in ok], default=0), 4),
            "voided_cases": len(voided),
            "voided_worst_dev_p50": round(pct([r["worst_dev"] for r in voided], .5), 4)
            if voided else None,
        }
        print("=== arm %-6s %s ===" % (arm, dict(st)))
        print(json.dumps(out[arm], indent=1))

    # The paired comparison the ticket asks for: which cases does `both` refuse
    # that `free` accepts, on the SAME (Brief, donor) pair.
    idx = {arm: {(r["brief"], r["donor"]): r for r in rows[arm]} for arm in ARMS}
    keys = list(idx["free"])
    disc = {}
    for arm in ("notch", "void", "both"):
        lost = [k for k in keys
                if idx["free"][k]["status"] == "OK"
                and idx[arm][k]["status"] != "OK"]
        gained = [k for k in keys
                  if idx["free"][k]["status"] != "OK"
                  and idx[arm][k]["status"] == "OK"]
        disc[arm] = {"free_ok_arm_not": len(lost), "arm_ok_free_not": len(gained),
                     "net_cost": len(lost) - len(gained),
                     "net_cost_share": round((len(lost) - len(gained))
                                             / max(1, len(keys)), 4)}
    out["_paired"] = disc
    print("\n=== paired against `free`, same (Brief, donor) ===")
    print(json.dumps(disc, indent=1))

    # The tolerance sweep. A single tolerance answers "what does THIS band cost";
    # the ticket asks what the constraint costs, and that is only meaningful as a
    # function of how hard the invariant is held. The band is in share points and
    # the frame is integer cells, so at tol 0 the constraint is asking for an
    # exact cell count and some INFEASIBLE is arithmetic rather than geometry --
    # which is itself the finding, if it is where the cost appears.
    print("\n=== `both`, notch tolerance sweep (share points) ===")
    sweep = {}
    for tol in (0.04, 0.02, 0.01, 0.005, 0.0):
        res = []
        for brief, cand, targets in pairs:
            r = run_arm(cand, brief["aspect"], targets, tlim, "both",
                        key=brief["k"] + cand["k"], notch_tol=tol)
            r["brief"], r["donor"] = brief["k"], cand["k"]
            res.append(r)
        st = Counter(r["status"] for r in res)
        ok = [r for r in res if r["status"] == "OK"]
        by_key = {(r["brief"], r["donor"]): r for r in res}
        lost = sum(1 for k in keys
                   if idx["free"][k]["status"] == "OK"
                   and by_key[k]["status"] != "OK")
        sweep[tol] = {
            "infeasible": st.get("INFEASIBLE", 0),
            "infeasible_share": round(st.get("INFEASIBLE", 0) / max(1, len(res)), 4),
            "free_ok_arm_not": lost,
            "net_cost_share": round(lost / max(1, len(keys)), 4),
            "s_drift_p90": round(pct([abs(r["s_drift"]) for r in ok], .9), 4),
            "worst_dev_p50": round(pct([r["worst_dev"] for r in ok], .5), 4),
            "void_m2_p90": round(pct([r["void_m2"] for r in ok], .9), 4),
            "secs_per_warp_p50": round(pct([r["secs"] for r in res], .5), 3)}
        print("  tol %-6s infeas %3d (%.1f%%)  lost-vs-free %3d  |s_drift| p90 %.4f"
              "  dev p50 %.4f  %.2fs"
              % (tol, sweep[tol]["infeasible"],
                 100 * sweep[tol]["infeasible_share"], lost,
                 sweep[tol]["s_drift_p90"], sweep[tol]["worst_dev_p50"],
                 sweep[tol]["secs_per_warp_p50"]))
    out["_notch_tol_sweep"] = {str(k): v for k, v in sweep.items()}

    out["_meta"] = {"n_requested": n_arg, "cases": len(pairs), "time_limit_s": tlim,
                    "seed": SEED, "notch_tol_share": NOTCH_TOL}
    OUT.mkdir(exist_ok=True)
    json.dump(rows, open(OUT / "constrained_warp_rows.json", "w"))
    json.dump(out, open(OUT / "constrained_warp.json", "w"), indent=1)
    print("\nwrote %s" % (OUT / "constrained_warp.json"))


if __name__ == "__main__":
    main()
