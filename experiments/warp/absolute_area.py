"""Does a Room that asks for 12 m2 get 12 m2?

Ticket 54. ADR 0018's headline warp fidelity -- best-of-8 worst-room deviation
p50 0.056 -- is a **proportion** result. `fit_warp.py:373-384` scales the Brief's
per-room targets onto the donor's covered area before comparing:

    scale = (W * H * fill) / sum(targets)
    targets = [a * scale for a in targets]

which normalises absolute area away. That was correct for what `fit_warp` was
measuring (can a warp hold a donor's *shares*?) and it is the wrong quantity for
everything downstream, because `dim.statutory_min_area` is **hard** -- living 16,
bedroom_double 10, kitchen 8 m2 in AZ -- on the argument that a Plan reaching its
soft target clears the floor by construction. That argument is exactly as good as
the warp's ability to deliver a stated `target_area`.

Three things this rig does that `fit_warp` does not:

1. **No renormalisation.** The Brief's targets enter in absolute m2 and stay there.
2. **The box is sized the way ADR 0020 writes it**, from the Brief and the
   candidate's own notch share, not drawn from a donor:

       interior = target_area * (1 + f)      f = 0.0575, brief.md 5 rung 1
       box      = interior / (1 - s)         s = the candidate's notch share

   Measured as written. If the level comes out wrong, that is a finding about the
   rung's arithmetic and it belongs in the answer -- resizing the box until the
   result looks good would be the renormalisation defect one level up.
3. **The quantity is the Space, not the part.** ADR 0001: `Space = erode(U parts,
   t_int/2)`, t_int = 150. ADR 0010 makes that the finished face, which is the
   plane `dim.statutory_min_area` and `dim.min_area` both bind. Erosion is
   systematically negative, so measuring the centreline part instead would bias
   the answer optimistic in exactly the direction that matters.

Three arms:

  `self`   -- the candidate is the Brief's own dwelling. The arrangement already
              matches the programme exactly, so this is the most favourable case
              the rig can construct and its deviations are **floors**.
  `cross`  -- the candidate is a different, gate-admitted dwelling and targets are
              paired onto its rooms by type, largest to largest. Retrieval as it
              actually runs.
  `calib`  -- `cross` with the box scaled so that Sum(Space) = target_area exactly.
              Separates the *level* error (the rung's arithmetic) from the
              *distribution* error (the warp's own).

    python experiments/warp/absolute_area.py [n] [--time=3.0] [--arms=self,cross,calib]

Reads `out/dwelling_rooms.json` (build it with `room_area_spread.py` first) and
`../rectangularise/out/swiss_fit_k2.json` read-only. Writes `out/absolute_area.json`.
"""

from __future__ import annotations

import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from shapely.geometry import box as shp_box
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fit_warp import (COLLAPSE, GRID_MM, MIN_SIDE, MIN_SIDE_DEFAULT,      # noqa: E402
                      AREA_TOL, ASPECT_TOL, SEED, W_STATED, W_INVENTED,
                      STATED_SHARE, coord_frame, uniform, warp_model)

OUT = HERE / "out"
FIT = HERE.parent / "rectangularise" / "out" / "swiss_fit_k2.json"
ROOMS = OUT / "dwelling_rooms.json"

T_INT_MM = 150                  # ADR 0010: 120 half-brick + 2 x 15 finish
ERODE_MM = T_INT_MM / 2         # ADR 0001: erode(U parts, t_int/2)
F_PARTITION = 0.0575            # brief.md 5 rung 1, p50 of Sum(Space) at t_int 150

# `dim.statutory_min_area`, AzDTN 2.7-2 cl. 5.7, through
# profiles.AZ.rooms.mapping.rooms.<erg_key>.az_area. Only three corpus labels
# reach a floor: the living family, the private family and the kitchen. The
# other six map to a null az_area, which room-constraints.json says means NO
# STATUTORY FLOOR, and their ergonomic minima (0.5-1.7 m2) are inert.
#
# PRIVATE is the one genuinely ambiguous limb: the corpus collapses
# {ROOM, BEDROOM, STUDIO} and cannot say single from double, so both floors are
# reported. `bedroom_double` 10 is the ticket's own naming and the primary.
STAT_FLOOR = {
    "KITCHEN": 8.0,             # kitchen
    "KITCHEN_DINING": 6.0,      # kitchen_zone_in_diner
    "PRIVATE": 10.0,            # bedroom_double
}
STAT_FLOOR_LENIENT = dict(STAT_FLOOR, PRIVATE=8.0)      # bedroom_single
LIVING_FAMILY = ("LIVING_ROOM", "LIVING_DINING")
LIVING_1OTAQ, LIVING_2PLUS = 15.0, 16.0                 # when_otaq_count guard
HABITABLE = ("PRIVATE", "LIVING_ROOM", "LIVING_DINING")  # ADR 0013: otaq

# `dim.market_default_area`'s target, the same mapping. This is the line the
# argument under test is stated against -- *a Plan that reaches its soft target
# clears the statutory floor by construction* -- so the `market` arm raises every
# Brief target onto it and asks whether the delivered Space still clears.
MARKET = {"KITCHEN": 9.0, "KITCHEN_DINING": 6.0, "PRIVATE": 12.0,
          "LIVING_ROOM": 16.0, "LIVING_DINING": 16.0, "BATHROOM": 3.2}


def floors_for(types, lenient=False):
    """max(ergonomic, statutory) per room. The ergonomic layer never binds on the
    three limbs that carry a statutory floor -- living 3.7 against 15/16, kitchen
    1.8 against 8, bedroom_double 3.1 against 10 -- so the statutory value IS the
    floor where one exists and there is nothing to take a max against."""
    otaq = sum(1 for t in types if t in HABITABLE)
    tbl = STAT_FLOOR_LENIENT if lenient else STAT_FLOOR
    liv = LIVING_1OTAQ if otaq == 1 else LIVING_2PLUS
    return [liv if t in LIVING_FAMILY else tbl.get(t) for t in types]


def notch_share(parts):
    """ADR 0020's `s`: the share of the bounding box taken by the two largest
    boundary-touching components of the complement. Voids -- components that touch
    nothing -- are deliberately excluded, which is the whole point: `uncovered` in
    a fit record sums the two together and that is why nobody had noticed."""
    x0 = min(p[0] for pl in parts for p in pl)
    y0 = min(p[1] for pl in parts for p in pl)
    x1 = max(p[2] for pl in parts for p in pl)
    y1 = max(p[3] for pl in parts for p in pl)
    g = np.zeros((y1 - y0, x1 - x0), dtype=bool)
    for pl in parts:
        for a, b, c, d in pl:
            g[b - y0:d - y0, a - x0:c - x0] = True
    # 4-connected components of the complement, by flood fill. No scipy: the
    # environment is pinned and a measurement is not a reason to move a pin.
    ny, nx = g.shape
    seen = g.copy()
    touching, enclosed = [], 0
    for sy in range(ny):
        for sx in range(nx):
            if seen[sy, sx]:
                continue
            stack, cells, on_border = [(sy, sx)], 0, False
            seen[sy, sx] = True
            while stack:
                y, x = stack.pop()
                cells += 1
                if y in (0, ny - 1) or x in (0, nx - 1):
                    on_border = True
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    py, px = y + dy, x + dx
                    if 0 <= py < ny and 0 <= px < nx and not seen[py, px]:
                        seen[py, px] = True
                        stack.append((py, px))
            if on_border:
                touching.append(cells)
            else:
                enclosed += cells
    bbox = g.size
    return sum(sorted(touching, reverse=True)[:2]) / bbox, enclosed / bbox


def space_m2(rects):
    """ADR 0001 consequence: the Space is `erode(U parts, t_int/2)`, which is
    strictly larger than the union of the parts' own erosions -- the band across a
    two-part Room's join comes back. Done on the union, with shapely, so a
    two-part Room is not quietly under-measured."""
    u = unary_union([shp_box(*r) for r in rects])
    e = u.buffer(-ERODE_MM, join_style=2)
    return max(0.0, e.area) / 1e6


def part_targets_cells(space_targets, seed_rects):
    """The objective runs on centreline parts; the Brief states Space areas. Add
    back each Room's own erosion overhead, read off its shape at the affine seed:
    a centreline w x h delivers (w - 150)(h - 150), so the overhead is
    150 * (w + h) - 22500 per part. An estimate -- the shape moves under the warp
    -- and it only steers the objective. Every number reported below is measured
    with `space_m2` on the solved geometry, so whatever this misses shows up as
    deviation rather than hiding in it."""
    out = []
    for a, rects in zip(space_targets, seed_rects):
        over = sum(T_INT_MM * ((r[2] - r[0]) + (r[3] - r[1])) - T_INT_MM ** 2
                   for r in rects)
        out.append(max(1, round((a * 1e6 + over) / GRID_MM ** 2)))
    return out


def rects_mm(spans, gx, gy):
    cx, cy = [0], [0]
    for v in gx:
        cx.append(cx[-1] + v)
    for v in gy:
        cy.append(cy[-1] + v)
    return [[(cx[a] * GRID_MM, cy[c] * GRID_MM, cx[b] * GRID_MM, cy[d] * GRID_MM)
             for a, b, c, d in pl] for pl in spans]


def joins(spans):
    jx, jy = [], []
    for pl in spans:
        if len(pl) != 2:
            continue
        (a1, b1, c1, d1), (a2, b2, c2, d2) = pl
        if d1 == c2 or d2 == c1:
            jx.append((max(a1, a2), min(b1, b2)))
        elif b1 == a2 or b2 == a1:
            jy.append((max(c1, c2), min(d1, d2)))
    return jx, jy


def pair_targets(cand_types, cand_parts, brief_rooms):
    """The Brief's rooms onto the candidate's, by type, largest onto largest --
    `fit_warp.assign_targets`'s rule. The order is the CANDIDATE's own part area,
    descending: pairing in index order instead would hand the Brief's biggest
    bedroom to whichever bedroom the corpus happened to list first, and every
    deviation that produced would belong to the rig. Returns None when the
    candidate cannot host the programme, which is a retrieval miss and not a
    fidelity result."""
    pool = defaultdict(list)
    for t, a in brief_rooms:
        pool[t].append(a)
    for t in pool:
        pool[t].sort(reverse=True)
    take, out = defaultdict(int), [0.0] * len(cand_types)
    order = sorted(range(len(cand_types)),
                   key=lambda i: -sum((p[2] - p[0]) * (p[3] - p[1])
                                      for p in cand_parts[i]))
    for i in order:
        t = cand_types[i]
        lst = pool.get(t, [])
        if take[t] >= len(lst):
            return None
        out[i] = lst[take[t]]
        take[t] += 1
    return out


def pct(xs, p):
    if not xs:
        return float("nan")
    s = sorted(xs)
    return s[min(len(s) - 1, int(p * len(s)))]


def run_one(cand, aspect, targets_m2, tlim, calibrate=False, key=""):
    """One warp. Returns per-room delivered Space area in m2, or a status."""
    parts, types = cand["parts"], [COLLAPSE.get(t, t) for t in cand["types"]]
    xs, ys, spans = coord_frame(parts)
    if len(xs) < 2 or len(ys) < 2:
        return {"status": "DEGENERATE"}
    s, void = notch_share(parts)
    if s >= 0.60:
        return {"status": "NOTCH"}

    target_area = sum(targets_m2)
    scale, got = 1.0, None
    for _ in range(6 if calibrate else 1):
        interior = target_area * (1.0 + F_PARTITION) * scale
        box_m2 = interior / (1.0 - s)
        Hm = (box_m2 * 1e6 / aspect) ** 0.5
        W = max(4, round(aspect * Hm / GRID_MM))
        H = max(4, round(Hm / GRID_MM))

        seed = (uniform(xs, W), uniform(ys, H))
        tgt_cells = part_targets_cells(targets_m2, rects_mm(spans, *seed))
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
        got = [space_m2(r) for r in solved]
        # The level, decomposed. Sum(Space)/target_area is a product of three
        # terms and each has a different owner:
        #   1.0575                 the rung's inflation      (brief.md 5 rung 1)
        #   covered / interior     what the box actually holds after `s`
        #   Sum(Space) / covered   the erosion, ADR 0001
        # Reporting the product alone would say the level is wrong without saying
        # which term is wrong, and they are fixed in different files.
        covered = sum((r[2] - r[0]) * (r[3] - r[1])
                      for pl in solved for r in pl) / 1e6
        cov_over_int = covered / interior
        space_over_cov = sum(got) / covered if covered else 0.0
        if not calibrate:
            break
        tot = sum(got)
        if tot <= 0:
            return {"status": "EMPTY"}
        if abs(tot - target_area) / target_area < 0.002:
            break
        scale *= target_area / tot
    return {"status": "OK", "got": got, "types": types, "s": s, "void": void,
            "target_area": target_area, "targets": targets_m2,
            "cov_over_int": cov_over_int, "space_over_cov": space_over_cov,
            "n_rooms": len(types)}


def gate_pool(brief, by_ms, by_n):
    """The shipped three-term admissibility gate, read against the BRIEF rather
    than against a donor Envelope -- ADR 0020 fixes `interior` from the Brief, so
    the Brief's `target_area` and aspect are what a candidate is admitted on."""
    adm = [p for p in by_ms.get(brief["ms"], []) if p["k"] != brief["k"]]
    if adm:
        return adm
    return [p for p in by_n.get(brief["n"], [])
            if p["k"] != brief["k"]
            and abs(brief["area"] - p["area"]) <= AREA_TOL * p["area"]
            and abs(brief["aspect"] - p["aspect"]) <= ASPECT_TOL * p["aspect"]]


def summarise(rows, lenient=False):
    dev, rel, tot_rel = [], [], []
    per_type = defaultdict(list)
    fails, fails_lenient, n_plans = 0, 0, 0
    room_fail = defaultdict(lambda: [0, 0])
    # The conditional arm. A Swiss dwelling is entitled to a 6 m2 kitchen and AZ
    # is not, so a raw fail share counts Briefs that were already below the floor
    # before the warp touched them -- that failure is the Brief's, and no bound in
    # brief.md 9.4 catches it (bound 1 is a sum, not a per-room test). The number
    # the argument under test actually rests on is this one: of the Rooms whose
    # OWN stated target clears the floor, how many does the warp push under it.
    cond_rooms = cond_fail = 0
    cond_plans = cond_plan_fail = 0
    cond_type = defaultdict(lambda: [0, 0])
    cond_margin = defaultdict(list)
    for r in rows:
        got, tgt, types = r["got"], r["targets"], r["types"]
        n_plans += 1
        floors = floors_for(types)
        floors_l = floors_for(types, lenient=True)
        bad = bad_l = False
        eligible, pushed_under = False, False
        for g, t, ty, fl, fl_l in zip(got, tgt, types, floors, floors_l):
            dev.append(g - t)
            rel.append((g - t) / t if t > 0 else 0.0)
            per_type[ty].append((g - t) / t if t > 0 else 0.0)
            if fl is not None:
                room_fail[ty][1] += 1
                if g < fl:
                    room_fail[ty][0] += 1
                    bad = True
                if t >= fl:                     # the Brief itself was compliant
                    eligible = True
                    cond_rooms += 1
                    cond_type[ty][1] += 1
                    cond_margin[ty].append(g - fl)
                    if g < fl:
                        cond_fail += 1
                        cond_type[ty][0] += 1
                        pushed_under = True
            if fl_l is not None and g < fl_l:
                bad_l = True
        fails += bad
        fails_lenient += bad_l
        if eligible:
            cond_plans += 1
            cond_plan_fail += pushed_under
        tot_rel.append((sum(got) - r["target_area"]) / r["target_area"])
    return {
        "plans": n_plans,
        "rooms": len(dev),
        "abs_dev_m2": {p: round(pct(dev, q), 3) for p, q in
                       (("p05", .05), ("p25", .25), ("p50", .50),
                        ("p75", .75), ("p95", .95))},
        "rel_dev": {p: round(pct(rel, q), 4) for p, q in
                    (("p05", .05), ("p25", .25), ("p50", .50),
                     ("p75", .75), ("p95", .95))},
        "share_under": round(sum(1 for d in dev if d < 0) / max(1, len(dev)), 4),
        "mean_rel": round(sum(rel) / max(1, len(rel)), 4),
        "plan_total_rel": {p: round(pct(tot_rel, q), 4) for p, q in
                           (("p05", .05), ("p50", .50), ("p95", .95))},
        "mean_plan_total_rel": round(sum(tot_rel) / max(1, len(tot_rel)), 4),
        "per_type_rel_p50": {t: round(pct(v, .5), 4)
                             for t, v in sorted(per_type.items())},
        "per_type_n": {t: len(v) for t, v in sorted(per_type.items())},
        "statutory_fail_share": round(fails / max(1, n_plans), 4),
        "statutory_fail_share_bedroom_single": round(
            fails_lenient / max(1, n_plans), 4),
        "room_fail_by_type": {t: [c, n, round(c / max(1, n), 4)]
                              for t, (c, n) in sorted(room_fail.items())},
        "level_terms_p50": {
            "rung_inflation": 1.0 + F_PARTITION,
            "covered_over_interior": round(
                pct([r["cov_over_int"] for r in rows], .5), 4),
            "space_over_covered": round(
                pct([r["space_over_cov"] for r in rows], .5), 4),
        },
        "conditional": {
            "rooms_whose_target_clears": cond_rooms,
            "of_which_delivered_below": cond_fail,
            "room_share": round(cond_fail / max(1, cond_rooms), 4),
            "plans_with_such_a_room": cond_plans,
            "of_which_lose_one": cond_plan_fail,
            "plan_share": round(cond_plan_fail / max(1, cond_plans), 4),
            # Ticket item 3: the kitchen on its own. AZ floors it at 8,0 and the
            # Swiss p50 is 8,04, so it is the limb with no headroom against the
            # corpus and the one where a small deviation crosses the floor.
            "by_type": {t: [c, n, round(c / max(1, n), 4)]
                        for t, (c, n) in sorted(cond_type.items())},
            # How much room the delivered Space has above its floor, in m2. A
            # distribution centred just above zero is a rule passing by luck.
            "margin_m2_by_type": {
                t: {p: round(pct(v, q), 3) for p, q in
                    (("p05", .05), ("p25", .25), ("p50", .50))}
                for t, v in sorted(cond_margin.items())},
        },
    }


def run_pool(sample, by_ms, by_n, rng, tlim, k):
    """Best-of-pool, which is what C6 actually does: generate many, reject most,
    show survivors. A Brief is SERVED if at least one of its `k` candidates puts
    every Room at or above its floor.

    This is not derivable from the per-candidate share, and the temptation to
    derive it is a trap this map has already fallen into once. ADR 0018
    consequence 3: declines are correlated within a pool because every candidate
    for one Brief shares the Envelope -- *"independence would predict a 1e-6
    Brief-level loss against a measured 6.9 %"*. Every target is raised onto
    `dim.market_default_area` first, so this is the argument under test at the
    level the Homeowner meets it."""
    served = starved = no_pool = 0
    per_brief = []
    for brief in sample:
        pool = gate_pool(brief, by_ms, by_n)
        if not pool:
            no_pool += 1
            continue
        picks = rng.sample(pool, min(k, len(pool)))
        ok, tried = False, 0
        for cand in picks:
            ct = [COLLAPSE.get(t, t) for t in cand["types"]]
            targets = pair_targets(ct, cand["parts"], brief["rooms"])
            if targets is None:
                continue
            targets = [max(a, MARKET.get(t, 0.0)) for a, t in zip(targets, ct)]
            r = run_one(cand, brief["aspect"], targets, tlim,
                        key=brief["k"] + cand["k"])
            if r["status"] != "OK":
                continue
            tried += 1
            if all(g >= fl for g, fl in zip(r["got"], floors_for(r["types"]))
                   if fl is not None):
                ok = True
                break
        if tried == 0:
            no_pool += 1
            continue
        served += ok
        starved += not ok
        per_brief.append(ok)
    n = served + starved
    return {"briefs": n, "pool_k": k, "served": served, "starved": starved,
            "brief_loss_share": round(starved / max(1, n), 4),
            "briefs_with_no_usable_candidate": no_pool}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n_arg = int(args[0]) if args else 400
    tlim = 3.0
    pool_k = 8
    arms = ["self", "cross", "calib", "market"]
    for a in sys.argv[1:]:
        if a.startswith("--time="):
            tlim = float(a.split("=", 1)[1])
        if a.startswith("--arms="):
            arms = a.split("=", 1)[1].split(",")
        if a.startswith("--pool="):
            pool_k = int(a.split("=", 1)[1])

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
    print(f"converted dwellings joined to the room cache: {len(cands):,}")

    by_ms, by_n = defaultdict(list), defaultdict(list)
    for c in cands:
        by_ms[c["ms"]].append(c)
        by_n[c["n"]].append(c)

    s_all = [notch_share(c["parts"]) for c in cands]
    print("notch share s  p10 %.4f p25 %.4f p50 %.4f p75 %.4f p90 %.4f  "
          "(ADR 0020 p50 0.1255)"
          % tuple(pct([a for a, _ in s_all], q) for q in (.1, .25, .5, .75, .9)))
    print("enclosed void share of bbox  p50 %.4f p90 %.4f p99 %.4f"
          % tuple(pct([b for _, b in s_all], q) for q in (.5, .9, .99)))

    rng = random.Random(SEED)
    sample = rng.sample(cands, min(n_arg, len(cands)))

    out, status = {}, defaultdict(Counter)
    for arm in [a for a in arms if a in ("self", "cross", "calib", "market")]:
        rows, misses = [], 0
        for brief in sample:
            if arm == "self":
                cand, targets = brief, [a for _, a in brief["rooms"]]
            else:
                pool = gate_pool(brief, by_ms, by_n)
                if not pool:
                    misses += 1
                    continue
                cand = rng.choice(pool)
                ct = [COLLAPSE.get(t, t) for t in cand["types"]]
                targets = pair_targets(ct, cand["parts"], brief["rooms"])
                if targets is None:
                    misses += 1
                    continue
                if arm == "market":
                    # every target raised onto dim.market_default_area's line,
                    # which is what the soft objective pulls toward. This is the
                    # argument under test stated literally: if a Plan that reaches
                    # its soft target clears the statutory floor by construction,
                    # this arm fails nothing.
                    targets = [max(a, MARKET.get(t, 0.0))
                               for a, t in zip(targets, ct)]
            r = run_one(cand, brief["aspect"], targets, tlim,
                        calibrate=(arm == "calib"), key=brief["k"] + cand["k"])
            status[arm][r["status"]] += 1
            if r["status"] == "OK":
                rows.append(r)
        # Every row, not just the summary. `acceptance-thresholds/`'s rule, which
        # is the reason a new statistic off that study costs seconds: if you add a
        # statistic, add its inputs to the record. A re-run here is ~20 min an arm.
        json.dump(rows, open(OUT / f"absolute_area_rows_{arm}.json", "w"))
        out[arm] = summarise(rows)
        out[arm]["retrieval_misses"] = misses
        out[arm]["solver_status"] = dict(status[arm])
        print(f"\n=== arm {arm}: {len(rows)} plans, "
              f"{dict(status[arm])}, retrieval misses {misses} ===")
        print(json.dumps(out[arm], indent=1))

    if "pool" in arms:
        out["pool"] = run_pool(sample, by_ms, by_n, rng, tlim, pool_k)

    out["_meta"] = {"n_requested": n_arg, "time_limit_s": tlim, "seed": SEED,
                    "t_int_mm": T_INT_MM, "f_partition": F_PARTITION,
                    "notch_share_p50": round(pct([a for a, _ in s_all], .5), 4),
                    "void_share_p50": round(pct([b for _, b in s_all], .5), 4),
                    "void_share_p90": round(pct([b for _, b in s_all], .9), 4)}
    OUT.mkdir(exist_ok=True)
    json.dump(out, open(OUT / "absolute_area.json", "w"), indent=1)
    print("\nwrote", OUT / "absolute_area.json")


if __name__ == "__main__":
    main()
