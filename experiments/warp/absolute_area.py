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
  `market` -- `cross` with every target raised onto `dim.market_default_area`.
  `ring`   -- `cross` with the Envelope's edge ring held fixed before the solve,
              which is what ADR 0003 consequence 7 says the engine does and what
              this rig does not get for free. `ringmarket` is the same over
              `market`'s targets, `ringpool` the same over `pool`'s. Ticket 56.

    python experiments/warp/absolute_area.py [n] [--time=3.0] [--arms=self,cross,calib]

Reads `out/dwelling_rooms.json` (build it with `room_area_spread.py` first) and
`../rectangularise/out/swiss_fit_k2.json` read-only. Writes `out/absolute_area.json`.
"""

from __future__ import annotations

import json
import random
import sys
import zlib
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from shapely.geometry import box as shp_box
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fit_warp import (COLLAPSE, GRID_MM, MIN_SIDE, MIN_SIDE_DEFAULT,      # noqa: E402
                      AREA_TOL, ASPECT_TOL, SEED, W_STATED, W_INVENTED,
                      STATED_SHARE, coord_frame, uniform, warp_model,
                      profile)

OUT = HERE / "out"
FIT = HERE.parent / "rectangularise" / "out" / "swiss_fit_k2.json"
ROOMS = OUT / "dwelling_rooms.json"

T_INT_MM = profile.T_INT_MM     # ADR 0010: 120 half-brick + 2 x 15 finish
ERODE_MM = T_INT_MM / 2         # ADR 0001: erode(U parts, t_int/2)
F_PARTITION = 0.0575            # brief.md 5 rung 1, p50 of Sum(Space) at t_int 150

# `dim.market_default_area`'s target per corpus label -- `brief.md` 9.2's ladder,
# resolved. This is the line the argument under test is stated against -- *a Plan
# that reaches its soft target clears the statutory floor by construction* -- so
# the `market` arm raises every Brief target onto it and asks whether the
# delivered Space still clears.
#
# ⚠️ IT WAS A LITERAL AND IT HAD DRIFTED ON FOUR OF SIX CELLS, one day after
# ADR 0035 re-fitted the market tier to Baku: PRIVATE 12,0 against 13,2, both
# living limbs 16,0 against 17,6, and KITCHEN_DINING 6,0 -- which is not drift
# but the read ADR 0034 decision 2 forbids outright. 6,0 is the `metbex zonasi`
# cell (`referent: part`), a sound floor and never a target; the ladder's rung 2
# gives the room 18,8. `market_default_table` enforces that refusal at the read.
# Ticket 69.
#
# Resolved at the UNGUARDED limb, which is what the literal encoded: a per-
# dwelling otaq resolution would change the arm rather than repair it.
MARKET = profile.market_default_table()

# Ticket 56 adds `ring` and `ringmarket`. `market` raises every target onto
# `dim.market_default_area`; `ring` holds the Envelope's ring fixed before the
# solve, which is what ADR 0003 consequence 7 says the engine does.
ARM_NAMES = ("self", "cross", "calib", "market", "ring", "ringmarket")
MARKET_ARMS = ("market", "ringmarket")
RING_ARMS = ("ring", "ringmarket")


def floors_for(types, lenient=False):
    """`dim.statutory_min_area`'s AZ limb per room, None where the profile is
    silent. The ergonomic layer never binds on the limbs that carry a statutory
    floor -- living 3,7 against 15/16, kitchen 1,8 against 8, bedroom_double 3,1
    against 10 -- so the statutory value IS the floor where one exists and there
    is nothing to take a max against.

    ⚠️ TWO THINGS THIS USED TO GET WRONG, ticket 69. It hand-implemented the
    `when_otaq_count` guard rather than resolving it, and it counted otaq off a
    HABITABLE tuple that OMITTED `DINING` -- whose `counts_as_otaq` is true in
    the profile. A dwelling with a living room and a dining room counted one otaq
    where the profile counts two, and took `living_room_1room_flat`'s 15,0 where
    the guard says `living_room_2plus`'s 16,0: a hard floor 1 m2 low, on the
    largest room in the plan. The otaq set is now read, and the guard resolved.

    ⚠️ It also had no `living_dining_kitchen` limb, so `floors_for` returned None
    on the open-plan type while the bar bound it at site `both` -- ADR 0036's
    hole. It is still None, but now BECAUSE the profile publishes a null az_area
    for that row (ADR 0036 withdrew the unlicensed read), not because the table
    forgot it. A hand copy can be wrong by omission, and this one was."""
    keys = [profile.erg_key(t, lenient) for t in types]
    otaq = profile.otaq_count(keys)
    return [profile.statutory_floor_m2(k, otaq) for k in keys]


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


def frame_components(spans, nx, ny):
    """The complement's 4-connected components over the frame's FIXED cell grid.

    Which cells a part covers is combinatorial -- the warp moves gap sizes, never
    the index spans -- so the components are fixed once per donor and only their
    areas move. Returns `(notch_cells, void_components)` on the same split
    `notch_share` makes: the two largest boundary-touching components are ADR
    0020's notch, everything enclosed is ADR 0028's void.

    Ticket 57. This exists because `notch_share` takes MILLIMETRE rectangles and
    flood-fills a boolean array of that many cells. On the donor's own integer
    parts that is small; on solved geometry it is ~80 million cells per plan, so
    the realised shares have to be read off the frame instead."""
    cov = np.zeros((ny, nx), dtype=bool)
    for parts in spans:
        for (a, b, c, d) in parts:
            cov[c:d, a:b] = True
    seen = cov.copy()
    touching, enclosed = [], []
    for sy in range(ny):
        for sx in range(nx):
            if seen[sy, sx]:
                continue
            stack, cells, on_border = [(sy, sx)], [], False
            seen[sy, sx] = True
            while stack:
                y, x = stack.pop()
                cells.append((x, y))
                if y in (0, ny - 1) or x in (0, nx - 1):
                    on_border = True
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    py, px = y + dy, x + dx
                    if 0 <= py < ny and 0 <= px < nx and not seen[py, px]:
                        seen[py, px] = True
                        stack.append((py, px))
            (touching if on_border else enclosed).append(cells)
    touching.sort(key=len, reverse=True)
    return [c for comp in touching[:2] for c in comp], enclosed


def realised_frame_areas(notch_cells, void_comps, gx, gy):
    """Notch, void and bbox in m2 under a solved gap pair. Exact, and O(cells)."""
    def area(cells):
        return sum(gx[i] * gy[j] for (i, j) in cells)
    cell_m2 = GRID_MM ** 2 / 1e6
    return (area(notch_cells) * cell_m2,
            sum(area(c) for c in void_comps) * cell_m2,
            sum(gx) * sum(gy) * cell_m2)


def outside_of(plan_rects):
    """Everything on the far side of the Envelope: the exterior, and the notch,
    which is an Envelope edge and not a partition.

    Ticket 56. The tiled region here is the Envelope box minus its notch --
    ADR 0020's `box = interior/(1 - s)` -- and ADR 0001 tiles the **solve domain**,
    the Envelope dilated outward by `t_int/2`. The two differ by a 75 mm ring
    around the whole dwelling. Dilating a 250 mm cell frame by 75 mm is below its
    own quantisation, so the construction is honoured on the measurement plane
    instead (see `space_m2`), and this is the region that plane needs.

    Enclosed voids are deliberately NOT included. A void is bounded by wall on
    every side, so its edges cost erosion exactly as an interior edge does; the
    notch and the exterior do not, because the erosion there lands on the external
    wall's inner face. `notch_share` already draws that same line, which is why
    it separates boundary-touching complement components from enclosed ones."""
    omega = unary_union([shp_box(*r) for pl in plan_rects for r in pl])
    x0, y0, x1, y1 = omega.bounds
    bb = shp_box(x0 - 1000, y0 - 1000, x1 + 1000, y1 + 1000)
    comp = bb.difference(omega)
    parts = list(getattr(comp, "geoms", [comp]))
    return unary_union([g for g in parts if g.intersects(bb.boundary)])


def space_m2(rects, outside):
    """ADR 0001 consequence: the Space is `erode(U parts, t_int/2)`, which is
    strictly larger than the union of the parts' own erosions -- the band across a
    two-part Room's join comes back. Done on the union, with shapely, so a
    two-part Room is not quietly under-measured.

    **Only interior edges erode.** ADR 0001's tiling edge on the domain boundary
    sits at exterior-inner-face + `t_int/2`, so eroding lands it precisely on the
    face and costs no floor -- *"one rule, no special case for perimeter rooms"*
    is a statement about the rule, not about the arithmetic. Eroding a room's
    outer edge as well charges every dwelling a 75 mm ring it does not lose:
    3.7 % of interior at p50 here, which is larger than the whole level error
    ticket 54 attributed to `brief.md` §5 rung 1.

    Modelled by eroding the room's parts UNION the region outside the Envelope,
    then trimming back: a boundary edge is interior to that union and survives,
    an edge shared with another Room does not. Exactly equal to ADR 0001's
    construction for area, with no grid quantisation."""
    u = unary_union([shp_box(*r) for r in rects])
    e = unary_union([u, outside]).buffer(-ERODE_MM, join_style=2)
    return max(0.0, e.intersection(u).area) / 1e6


def part_targets_cells(space_targets, seed_rects, outside):
    """The objective runs on centreline parts; the Brief states Space areas. Add
    back each Room's own erosion overhead, read off its shape at the affine seed.

    Ticket 56: the overhead is measured with the same rule the result is measured
    with, rather than charged as `150 * (w + h) - 22500` on all four sides of every
    part. A perimeter Room loses nothing at the Envelope, so the flat charge
    over-stated its overhead and steered the objective to over-size exactly the
    rooms that sit on the boundary. An estimate -- the shape moves under the warp
    -- and it only steers the objective. Every number reported below is measured
    with `space_m2` on the solved geometry, so whatever this misses shows up as
    deviation rather than hiding in it."""
    out = []
    for a, rects in zip(space_targets, seed_rects):
        gross = sum((r[2] - r[0]) * (r[3] - r[1]) for r in rects)
        over = gross - space_m2(rects, outside) * 1e6
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


def run_one(cand, aspect, targets_m2, tlim, calibrate=False, key="",
            hold_ring=False, wseed=None, dtime=None):
    """One warp. Returns per-room delivered Space area in m2, or a status.

    `hold_ring` (ticket 56) makes the rig agree with the engine about what is
    fixed before the solve. ADR 0003 consequence 7, as amended, fixes the
    Envelope's edge ring **per candidate, before that candidate's solve**, so the
    notch is a given and `covered` is identically `interior`. This rig cannot pin
    the ring where it belongs -- the notch is implicit in the uncovered cells of
    `warp_model`, which lives in `fit_warp.py` and carries ADR 0018's published
    numbers -- so it recovers the same invariant by fixed point on the box.

    It is not `calibrate`. `calibrate` scales until Sum(Space) hits `target_area`,
    which buys the rooms margin the engine does not give them and is the
    renormalisation defect ticket 54 refused one level up. This enforces a
    constraint the engine actually has, and leaves the erosion where it falls."""
    parts, types = cand["parts"], [COLLAPSE.get(t, t) for t in cand["types"]]
    xs, ys, spans = coord_frame(parts)
    if len(xs) < 2 or len(ys) < 2:
        return {"status": "DEGENERATE"}
    s, void = notch_share(parts)
    if s >= 0.60:
        return {"status": "NOTCH"}

    target_area = sum(targets_m2)
    want_interior = target_area * (1.0 + F_PARTITION)
    scale, got = 1.0, None
    # Ticket 82. Whether the CAP actually bound is the mechanism behind every
    # timed figure here: a solve that reaches OPTIMAL cannot vary with machine
    # load, and one stopped by the clock can. `hold_ring` runs this loop up to
    # six times and the pair is only cap-free if EVERY iteration proved
    # optimality, so the flag is an AND over the fixed point.
    all_opt = True
    for _ in range(6 if (calibrate or hold_ring) else 1):
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
        # Ticket 82. `hash()` on a str is salted per process unless
        # PYTHONHASHSEED is set, so this line drew a DIFFERENT objective weight
        # vector in every process -- W_STATED 8 against W_INVENTED 1, at a 30 %
        # coin flip, per room. `wseed` makes the draw explicit: None keeps the
        # shipped (salted) path byte-for-byte so nothing published moves under
        # a measurement, and an int fixes it. Measured by `repro_floor.py`.
        rng = random.Random(SEED ^ ((zlib.crc32(key.encode()) if wseed is None else wseed)
                                    & 0xFFFF))
        weights = [W_STATED if rng.random() < STATED_SHARE else W_INVENTED
                   for _ in types]
        mins = [MIN_SIDE.get(t, MIN_SIDE_DEFAULT) for t in types]
        res, name = warp_model(spans, len(xs) - 1, len(ys) - 1, tgt_cells, W, H,
                               weights, mins, jx, jy, tlim, seed=seed,
                               dtime=dtime)
        if res is None:
            return {"status": name}
        gx, gy, _opt = res
        all_opt = all_opt and bool(_opt)
        solved = rects_mm(spans, gx, gy)
        outside = outside_of(solved)
        got = [space_m2(r, outside) for r in solved]
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
        if hold_ring:
            # the Envelope is fixed before the solve, so covered IS `interior`.
            # Report the term against the interior the Brief asked for, not
            # against the scaled box the fixed point is walking.
            cov_over_int = covered / want_interior
            if covered <= 0:
                return {"status": "EMPTY"}
            if abs(covered - want_interior) / want_interior < 0.002:
                break
            scale *= want_interior / covered
            continue
        if not calibrate:
            break
        tot = sum(got)
        if tot <= 0:
            return {"status": "EMPTY"}
        if abs(tot - target_area) / target_area < 0.002:
            break
        scale *= target_area / tot
    # Ticket 57, obligation 1. Sum(Space) and per-room deviation were reported and
    # the hole BETWEEN the parts was not, which is why ADR 0028's measurements had
    # to be made from outside this rig in `experiments/void/`. The frame's bbox
    # decomposes exactly four ways and every term is now on the record:
    #
    #     bbox = Sum(Space) + erosion + notch + enclosed void
    #
    # `s` and `void` above are the DONOR's shares, read off the seed. These are
    # the REALISED ones, read off the solved rectangles, and they are not the same
    # number: proposer.md 2.2.8 measures the warp amplifying the donor's void 2.2x
    # because it is the one region of the frame carrying no target. On
    # `acceptance-thresholds/`'s standing rule -- if you add a statistic, add its
    # inputs to the record -- so a later reader can re-derive these without a
    # 15-minute re-solve.
    ncells, vcomps = frame_components(spans, len(xs) - 1, len(ys) - 1)
    notch_a, void_a, bbox_m2 = realised_frame_areas(ncells, vcomps, gx, gy)
    s_real = notch_a / bbox_m2 if bbox_m2 else 0.0
    void_real = void_a / bbox_m2 if bbox_m2 else 0.0
    return {"status": "OK", "got": got, "types": types, "s": s, "void": void,
            "all_optimal": all_opt,
            "target_area": target_area, "targets": targets_m2,
            "cov_over_int": cov_over_int, "space_over_cov": space_over_cov,
            "n_rooms": len(types),
            # realised, on the solved frame
            "s_realised": round(s_real, 5), "void_realised": round(void_real, 5),
            "bbox_m2": round(bbox_m2, 4),
            "notch_m2": round(notch_a, 4),
            "void_m2": round(void_a, 4),
            "covered_m2": round(covered, 4),
            "space_m2_total": round(sum(got), 4),
            "erosion_m2": round(covered - sum(got), 4)}


def admissible_pool(brief, by_ms):
    """proposer.md 2.2.1's gate, all three terms, read against the BRIEF rather
    than against a donor Envelope -- ADR 0020 fixes `interior` from the Brief, so
    the Brief's `target_area` and aspect are what a candidate is admitted on.

    *"The gate's first term is an exact match, so the bucket is the pool and the
    other two terms are a scan of it."* An empty return is a real product state --
    2.2.1's *"outside the gate, do not retrieve; hand the Brief to source B"* --
    and not a miss to be papered over. Ticket 60."""
    return [p for p in by_ms.get(brief["ms"], [])
            if p["k"] != brief["k"]
            and abs(brief["area"] - p["area"]) <= AREA_TOL * p["area"]
            and abs(brief["aspect"] - p["aspect"]) <= ASPECT_TOL * p["aspect"]]


def bucket_pool(brief, by_ms, by_n):
    """**Not the gate.** The multiset bucket unscanned, with an off-multiset
    fallback -- what this rig ran until ticket 60, and what every published
    `absolute_area` arm before it was measured through.

    Kept, named, and no longer the default, for one reason: the converted sample
    cannot reach production depth under the gate. Median pool is 9 and 5 against
    production's 86.6 and 58.7, no Brief holds 64, and a best-of-m curve fitted
    on it returns a floor of zero with a zero-width interval -- a shallow-
    censoring artefact. This is the **depth proxy** the curve needs, and its
    price is measured: `gate_effect.py` finds its members decline **36.2 %**
    against an admitted donor's **27.6 %** (paired within Brief, sign test
    p = 0.0001) and carry a worst-room deviation 68 % worse at p50. So a curve
    fitted here **under-states** what production depth buys, and 82.4 % of what
    it returns is floor the shipped gate refuses (`gate_sites.py`).

    Use it only where depth is the quantity and membership is not. Never for a
    per-candidate statistic."""
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
        # Ticket 57, obligation 1: the realised hole. `bbox` decomposes as
        # Sum(Space) + erosion + notch + enclosed void, and only the first two
        # were ever reported here. The void is the term ADR 0028 charges to a
        # receiving Room, and `model.no_unassigned_area` is HARD, so the solver is
        # required to close it -- realised void is floor the Homeowner is handed
        # without asking. Donor-vs-realised is the amplification 2.2.8 measures.
        "unassigned": {
            "void_m2": {p: round(pct([r["void_m2"] for r in rows], q), 4)
                        for p, q in (("p50", .50), ("p90", .90), ("p99", .99))},
            "void_max_m2": round(max([r["void_m2"] for r in rows], default=0), 4),
            "share_with_any_void": round(
                sum(1 for r in rows if r["void_m2"] > 1e-9) / max(1, len(rows)), 4),
            "share_void_over_0p5_m2": round(
                sum(1 for r in rows if r["void_m2"] >= 0.5) / max(1, len(rows)), 4),
            "donor_void_p50_m2": round(
                pct([r["void"] * r["bbox_m2"] for r in rows], .5), 4),
            "amplification_p50": round(pct(
                [r["void_m2"] / (r["void"] * r["bbox_m2"])
                 for r in rows if r["void"] * r["bbox_m2"] > 1e-9], .5), 3),
            "notch_m2_p50": round(pct([r["notch_m2"] for r in rows], .5), 4),
            "erosion_m2_p50": round(pct([r["erosion_m2"] for r in rows], .5), 4),
            "void_share_of_bbox_p50": round(
                pct([r["void_realised"] for r in rows], .5), 5),
            "notch_share_realised_p50": round(
                pct([r["s_realised"] for r in rows], .5), 4),
            "notch_share_donor_p50": round(pct([r["s"] for r in rows], .5), 4),
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


def run_pool(sample, by_ms, by_n, rng, tlim, k, hold_ring=False, pick=None):
    """Best-of-pool, which is what C6 actually does: generate many, reject most,
    show survivors. A Brief is SERVED if at least one of its `k` candidates puts
    every Room at or above its floor.

    This is not derivable from the per-candidate share, and the temptation to
    derive it is a trap this map has already fallen into once. ADR 0018
    consequence 3: declines are correlated within a pool because every candidate
    for one Brief shares the Envelope -- *"independence would predict a 1e-6
    Brief-level loss against a measured 6.9 %"*. Every target is raised onto
    `dim.market_default_area` first, so this is the argument under test at the
    level the Homeowner meets it.

    `pick` defaults to `admissible_pool`, the shipped gate. Ticket 60: it used to
    be `bucket_pool`, which is not the gate, and a Brief the gate leaves blank was
    being counted as served on a pool of a different room programme."""
    pick = pick or (lambda b: admissible_pool(b, by_ms))
    served = starved = no_pool = 0
    per_brief = []
    for brief in sample:
        pool = pick(brief)
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
                        key=brief["k"] + cand["k"], hold_ring=hold_ring)
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
    pooldef = "gate"          # ticket 60; `bucket` reproduces the pre-60 rig
    suffix = ""               # ticket 60; keeps two pool definitions off each other
    for a in sys.argv[1:]:
        if a.startswith("--time="):
            tlim = float(a.split("=", 1)[1])
        if a.startswith("--arms="):
            arms = a.split("=", 1)[1].split(",")
        if a.startswith("--pool="):
            pool_k = int(a.split("=", 1)[1])
        if a.startswith("--pooldef="):
            pooldef = a.split("=", 1)[1]
        if a.startswith("--suffix="):
            suffix = a.split("=", 1)[1]
    if pooldef not in ("gate", "bucket"):
        raise SystemExit("--pooldef must be 'gate' (2.2.1) or 'bucket' (pre-60)")

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
    if pooldef == "gate":
        def pick(b):
            return admissible_pool(b, by_ms)
    else:
        def pick(b):
            return bucket_pool(b, by_ms, by_n)
    print("pool definition: %s" % ("2.2.1's three-term gate" if pooldef == "gate"
                                   else "the pre-60 bucket, NOT the gate"))

    out, status = {}, defaultdict(Counter)
    for arm in [a for a in arms if a in ARM_NAMES]:
        rows, misses = [], 0
        for brief in sample:
            if arm == "self":
                cand, targets = brief, [a for _, a in brief["rooms"]]
            else:
                pool = pick(brief)
                if not pool:
                    misses += 1
                    continue
                cand = rng.choice(pool)
                ct = [COLLAPSE.get(t, t) for t in cand["types"]]
                targets = pair_targets(ct, cand["parts"], brief["rooms"])
                if targets is None:
                    misses += 1
                    continue
                if arm in MARKET_ARMS:
                    # every target raised onto dim.market_default_area's line,
                    # which is what the soft objective pulls toward. This is the
                    # argument under test stated literally: if a Plan that reaches
                    # its soft target clears the statutory floor by construction,
                    # this arm fails nothing.
                    targets = [max(a, MARKET.get(t, 0.0))
                               for a, t in zip(targets, ct)]
            r = run_one(cand, brief["aspect"], targets, tlim,
                        calibrate=(arm == "calib"), key=brief["k"] + cand["k"],
                        hold_ring=(arm in RING_ARMS))
            status[arm][r["status"]] += 1
            if r["status"] == "OK":
                rows.append(r)
        # Every row, not just the summary. `acceptance-thresholds/`'s rule, which
        # is the reason a new statistic off that study costs seconds: if you add a
        # statistic, add its inputs to the record. A re-run here is ~20 min an arm.
        json.dump(rows, open(OUT / f"absolute_area_rows_{arm}{suffix}.json", "w"))
        out[arm] = summarise(rows)
        out[arm]["retrieval_misses"] = misses
        out[arm]["solver_status"] = dict(status[arm])
        print(f"\n=== arm {arm}: {len(rows)} plans, "
              f"{dict(status[arm])}, retrieval misses {misses} ===")
        print(json.dumps(out[arm], indent=1))

    if "pool" in arms:
        out["pool"] = run_pool(sample, by_ms, by_n, rng, tlim, pool_k, pick=pick)
    if "ringpool" in arms:
        out["ringpool"] = run_pool(sample, by_ms, by_n, rng, tlim, pool_k,
                                   hold_ring=True, pick=pick)

    out["_meta"] = {"n_requested": n_arg, "time_limit_s": tlim, "seed": SEED,
                    "t_int_mm": T_INT_MM, "f_partition": F_PARTITION,
                    "notch_share_p50": round(pct([a for a, _ in s_all], .5), 4),
                    "void_share_p50": round(pct([b for _, b in s_all], .5), 4),
                    "void_share_p90": round(pct([b for _, b in s_all], .9), 4)}
    OUT.mkdir(exist_ok=True)
    json.dump(out, open(OUT / f"absolute_area{suffix}.json", "w"), indent=1)
    print("\nwrote", OUT / "absolute_area.json")


if __name__ == "__main__":
    main()
