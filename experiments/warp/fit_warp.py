"""The warp as a solve over the source tiling's cut lines.

Ticket 23, item 2. A converted corpus dwelling (ADR 0008/0016) is a rectangular
tiling of a bbox-minus-notches Envelope, one or two parts per Room. Write the
distinct x-coordinates of every part edge as an increasing vector and the gaps
between them as `gx`; likewise `gy`. Every part's width is a contiguous sum of
`gx`, every part's height a contiguous sum of `gy`, and **the tiling's combinatorics
are entirely carried by the index spans** -- they do not depend on the gap values
at all, as long as every gap stays positive.

Two consequences, and the first is a theorem rather than a measurement:

  * Any strictly increasing per-axis map preserves the sign of every separation
    cost, so a warp of this shape has **zero confident-wrong relations and zero
    reversals against the source dwelling, by construction, for every dwelling
    and every target**. `proposer.md` 5.2's severity is identically 0.
  * The gaps are therefore free to be *chosen*, and the obvious thing to choose
    them for is the Brief's per-room `target_area`, which `room_area_spread.py`
    shows a uniform scale misses by a median 21 %.

So the warp is a CP-SAT programme -- the same toolchain as the conversion and the
projection, no new dependency -- over `2 * (len(gx) + len(gy))` integers:

    minimise  sum_r  w_r * |area_r - target_r|
    s.t.      sum(gx) = W,  sum(gy) = H
              gx_i >= 1, gy_j >= 1                      (grid units)
              part width  >= min_w[type],  part height >= min_h[type]
              two-part Rooms keep ADR 0014's join

`area_r` is bilinear, so this alternates: fix `gy`, solve for `gx` (areas linear),
fix `gx`, solve for `gy`. Seeded from the uniform scale, which is the affine warp.

This measures the residual: how close can a warp get to a Brief's per-room targets
while keeping the retrieved arrangement exactly?

    python experiments/warp/fit_warp.py [n] [--iters=4] [--time=1.0]
"""

from __future__ import annotations

import json
import random
import statistics as st
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

from ortools.sat.python import cp_model

# Read-only import of the shipped extractor, so the relation check below is the
# solver's own and not a copy of it -- `proposer.md` 5.1. Same pattern
# `experiments/envelope-exposure/` uses; nothing here writes to solver-toy.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "solver-toy"))
from geometry import Rect                       # noqa: E402
from solver import rank_relations, select_relations   # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
FIT = HERE.parent / "rectangularise" / "out" / "swiss_fit_k2.json"
ROOMS = OUT / "dwelling_rooms.json"

GRID_MM = 250
AREA_TOL, ASPECT_TOL, SEED = 0.10, 0.15, 20260819
COLLAPSE = {"ROOM": "PRIVATE", "BEDROOM": "PRIVATE", "STUDIO": "PRIVATE"}

# `ergonomic.rooms[*].min_clear_short` from data/standards/room-constraints.json,
# converted to the CENTRELINE rectangle the conversion emits -- clear + t_int per
# ADR 0001 -- and rounded UP onto the grid, because this is a floor.
#   ceil((min_clear_short + 150) / 250)
MIN_SIDE = {"PRIVATE": 8,        # bedroom_double 1650 -> 1800
            "LIVING_ROOM": 8,    # living        1850 -> 2000
            "LIVING_DINING": 8,  # living_dining 1850 -> 2000
            "DINING": 6,         # dining        1300 -> 1450
            "KITCHEN": 5,        # kitchen        900 -> 1050
            "BATHROOM": 5,       # bathroom      1000 -> 1150
            "WC": 4,             # wc             800 ->  950
            "CORRIDOR": 5,       # corridor       900 -> 1050
            "STOREROOM": 3}      # storage        600 ->  750
MIN_SIDE_DEFAULT = 5
JOIN_UNITS = 5                  # ADR 0014: 900 clear, 1 100 realisable -> 4.4 -> 5
ASPECT_HARD = 3                 # dim.aspect_ratio_hard, per PART (ADR 0014)
W_STATED = 8                    # a stated target is sovereign -- brief.md 6.1
W_INVENTED = 1
STATED_SHARE = 0.30             # probe only: how many of a Brief's targets are stated


def warp_model(spans, nx, ny, targets, W, H, weights, min_side,
               joins_x, joins_y, tlim, aspect=True, seed=None):
    """The whole warp, as one CP-SAT model over both cut-line vectors.

    Not an alternation. A Room's area is bilinear in the two gap vectors, and
    CP-SAT takes that directly through `AddMultiplicationEquality`; alternating
    would freeze one axis and manufacture infeasibility on a constraint -- the
    aspect cap above all -- that couples them.

        minimise  1000 * n * worst_dev  +  sum_r w_r * dev_r     (per-mille)
        s.t.      sum(gx) = W,  sum(gy) = H,  every gap >= 1
                  every part's span >= its Room's realisable minimum, both axes
                  every part's aspect within dim.aspect_ratio_hard
                  every two-part Room's shared edge >= ADR 0014's join

    Returns `(gx, gy)` or None when the target Envelope genuinely cannot host
    this arrangement at the ergonomic floor -- which is a refusal, not a bug:
    retrieval declines and the Brief falls to source B (ADR 0005).
    """
    m = cp_model.CpModel()
    gx = [m.NewIntVar(1, W, f"gx{i}") for i in range(nx)]
    gy = [m.NewIntVar(1, H, f"gy{j}") for j in range(ny)]
    m.Add(sum(gx) == W)
    m.Add(sum(gy) == H)
    for lo, hi in joins_x:
        if hi > lo:
            m.Add(sum(gx[lo:hi]) >= JOIN_UNITS)
    for lo, hi in joins_y:
        if hi > lo:
            m.Add(sum(gy[lo:hi]) >= JOIN_UNITS)

    # Deviation is measured in **per-mille of the Room's own target**, never in
    # cells. An absolute objective spends every gap on the living room, because
    # 5 % of 30 m2 outweighs 40 % of a WC -- exactly backwards: the bar and the
    # Homeowner both read the *worst* room.
    devs = []
    for r, parts in enumerate(spans):
        areas = []
        for p, (a, b, c, d) in enumerate(parts):
            wv = m.NewIntVar(1, W, f"w{r}_{p}")
            hv = m.NewIntVar(1, H, f"h{r}_{p}")
            m.Add(wv == sum(gx[a:b]))
            m.Add(hv == sum(gy[c:d]))
            m.Add(wv >= min_side[r])
            m.Add(hv >= min_side[r])
            if aspect:
                m.Add(wv <= ASPECT_HARD * hv)
                m.Add(hv <= ASPECT_HARD * wv)
            av = m.NewIntVar(1, W * H, f"a{r}_{p}")
            m.AddMultiplicationEquality(av, [wv, hv])
            areas.append(av)
        area = sum(areas)
        e = m.NewIntVar(0, 20_000, f"e{r}")
        m.Add(e * targets[r] >= 1000 * (area - targets[r]))
        m.Add(e * targets[r] >= 1000 * (targets[r] - area))
        devs.append(e)
    worst = m.NewIntVar(0, 20_000, "worst")
    m.AddMaxEquality(worst, devs)
    m.Minimize(worst * (1000 * len(devs))
               + sum(weights[r] * d for r, d in enumerate(devs)))

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


def coord_frame(parts):
    """Distinct coordinates and per-part index spans, both axes."""
    xs = sorted({c for pl in parts for p in pl for c in (p[0], p[2])})
    ys = sorted({c for pl in parts for p in pl for c in (p[1], p[3])})
    xi = {c: i for i, c in enumerate(xs)}
    yi = {c: i for i, c in enumerate(ys)}
    spans = [[(xi[p[0]], xi[p[2]], yi[p[1]], yi[p[3]]) for p in pl] for pl in parts]
    return xs, ys, spans


def uniform(xs, W):
    """The affine warp: scale the coordinate vector, keep it strictly increasing."""
    span = xs[-1] - xs[0]
    out, prev = [], -1
    for i, c in enumerate(xs):
        v = round((c - xs[0]) * W / span)
        v = max(v, prev + 1)
        out.append(v)
        prev = v
    # pull the last onto W without breaking monotonicity
    out[-1] = max(W, out[-2] + 1)
    return [out[i + 1] - out[i] for i in range(len(out) - 1)]


def envelope_units(d):
    """A donor dwelling's Envelope as an integer grid box at its own aspect."""
    Hm = (d["area"] * 1e6 / d["aspect"]) ** 0.5
    return max(4, round(d["aspect"] * Hm / GRID_MM)), max(4, round(Hm / GRID_MM))


def assign_targets(types, parts, src_rooms):
    """Pair the Brief's rooms onto the source's, by type, largest to largest."""
    tgt = defaultdict(list)
    for t, a in src_rooms:
        tgt[COLLAPSE.get(t, t)].append(a)
    for t in tgt:
        tgt[t].sort(reverse=True)
    take, targets = defaultdict(int), [0.0] * len(types)
    order = sorted(range(len(types)),
                   key=lambda i: -sum((p[2] - p[0]) * (p[3] - p[1]) for p in parts[i]))
    for i in order:
        lst = tgt.get(types[i], [])
        if take[types[i]] >= len(lst):
            return None
        targets[i] = lst[take[types[i]]]
        take[types[i]] += 1
    return targets


def warp_one(rec, src, d, tlim, rng=None):
    """Warp one converted dwelling into one donor Envelope.

    Returns the fitted warp's **worst-room relative area deviation**, or None
    when the warp declines -- the Envelope cannot host this arrangement at the
    ergonomic floor and inside `dim.aspect_ratio_hard`.
    """
    rng = rng or random.Random(SEED)
    W, H = envelope_units(d)
    parts, types = rec["parts"], [COLLAPSE.get(t, t) for t in rec["types"]]
    xs, ys, spans = coord_frame(parts)
    if len(xs) < 2 or len(ys) < 2:
        return None
    targets = assign_targets(types, parts, src["rooms"])
    if targets is None:
        return None
    cells = sum((p[2] - p[0]) * (p[3] - p[1]) for pl in parts for p in pl)
    bx = (max(p[2] for pl in parts for p in pl) - min(p[0] for pl in parts for p in pl))
    by = (max(p[3] for pl in parts for p in pl) - min(p[1] for pl in parts for p in pl))
    fill = cells / max(1, bx * by)
    scale = (W * H * fill) / (sum(targets) * 1e6 / GRID_MM ** 2)
    targets = [max(1, round(a * 1e6 / GRID_MM ** 2 * scale)) for a in targets]

    weights = [W_STATED if rng.random() < STATED_SHARE else W_INVENTED
               for _ in types]
    min_side = [MIN_SIDE.get(t, MIN_SIDE_DEFAULT) for t in types]
    join_x, join_y = joins_of(spans)
    seed = (uniform(xs, W), uniform(ys, H))
    res, _status = warp_model(spans, len(seed[0]), len(seed[1]), targets, W, H,
                              weights, min_side, join_x, join_y, tlim, seed=seed)
    if res is None:
        return None
    gx, gy, _opt = res
    cx, cy = [0], [0]
    for v in gx:
        cx.append(cx[-1] + v)
    for v in gy:
        cy.append(cy[-1] + v)
    dev = []
    for pl, t in zip(spans, targets):
        a = sum((cx[b] - cx[a_]) * (cy[d2] - cy[c]) for a_, b, c, d2 in pl)
        dev.append(abs(a - t) / t)
    return max(dev)


def joins_of(spans):
    """ADR 0014's shared edge, as an index span on the axis it runs along."""
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


def main():
    n_arg = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 300
    iters = 4
    tlim = 1.0
    no_aspect = "--no-aspect" in sys.argv
    no_min = "--no-min" in sys.argv
    for a in sys.argv[1:]:
        if a.startswith("--iters="):
            iters = int(a.split("=")[1])
        if a.startswith("--time="):
            tlim = float(a.split("=")[1])

    fits = [r for r in json.load(open(FIT)) if r["status"] in ("OPTIMAL", "FEASIBLE")]
    recs = {r["k"]: r for r in json.load(open(ROOMS))}
    fits = [r for r in fits if r["k"] in recs]
    print(f"converted dwellings joined to the coverage cache: {len(fits):,}")

    # index the full corpus so a Brief's pool is the real one
    for r in recs.values():
        r["ms"] = tuple(sorted(Counter(COLLAPSE.get(t, t) for t, _ in r["rooms"]).items()))
    by_ms, by_n = defaultdict(list), defaultdict(list)
    for r in recs.values():
        by_ms[r["ms"]].append(r)
        by_n[r["n"]].append(r)

    rng = random.Random(SEED)
    sample = rng.sample(fits, min(n_arg, len(fits)))

    aff_dev, fit_dev, aff_worst, fit_worst = [], [], [], []
    times, solved, skipped = [], 0, 0
    infeasible_axis = 0
    st_dev, inv_dev = [], []
    declined, optimal = [], 0
    statuses = Counter()
    gated_out = 0
    cw_affine = cw_fitted = rev_fitted = 0
    sev_affine = sev_fitted = 0
    asserted_total = 0
    for rec in sample:
        src = recs[rec["k"]]
        # A Brief the way cross_coverage.py builds one: this dwelling's programme,
        # a different dwelling's envelope -- and then **the shipped three-term gate**,
        # so the source is one retrieval would actually have admitted. Warping into
        # an ungated envelope measures the absence of the gate, not the warp.
        cands = [p for p in by_n[src["n"]] if p["k"] != src["k"]]
        if not cands:
            continue
        d = rng.choice(cands)
        if src["ms"] != d["ms"] and not (
                abs(src["area"] - d["area"]) <= AREA_TOL * d["area"]
                and abs(src["aspect"] - d["aspect"]) <= ASPECT_TOL * d["aspect"]):
            # this source is outside the gate for this envelope -- retrieval would
            # never have offered it. Draw the envelope from the admitted set.
            adm = [p for p in by_ms[src["ms"]]
                   if p["k"] != src["k"]
                   and abs(src["area"] - p["area"]) <= AREA_TOL * p["area"]
                   and abs(src["aspect"] - p["aspect"]) <= ASPECT_TOL * p["aspect"]]
            if not adm:
                gated_out += 1
                continue
            d = rng.choice(adm)
        # the target envelope, as a grid-unit box of the donor's area and aspect
        env_area_mm2 = d["area"] * 1e6
        asp = d["aspect"]
        Hm = (env_area_mm2 / asp) ** 0.5
        Wm = asp * Hm
        W = max(4, round(Wm / GRID_MM))
        H = max(4, round(Hm / GRID_MM))

        parts = rec["parts"]
        types = [COLLAPSE.get(t, t) for t in rec["types"]]
        xs, ys, spans = coord_frame(parts)
        if len(xs) < 2 or len(ys) < 2:
            continue

        # per-Room target area, in grid cells: the Brief's own rooms, scaled so
        # the programme fills the donor envelope exactly.
        tgt_m2 = defaultdict(list)
        for t, a in src["rooms"]:
            tgt_m2[COLLAPSE.get(t, t)].append(a)
        for t in tgt_m2:
            tgt_m2[t].sort(reverse=True)
        take = defaultdict(int)
        order = sorted(range(len(types)),
                       key=lambda i: -sum((p[2] - p[0]) * (p[3] - p[1]) for p in parts[i]))
        targets = [0] * len(types)
        ok = True
        for i in order:
            t = types[i]
            lst = tgt_m2.get(t, [])
            if take[t] >= len(lst):
                ok = False
                break
            targets[i] = lst[take[t]]
            take[t] += 1
        if not ok:
            skipped += 1
            continue
        # Scale the programme onto the **covered** area, not the bbox. The source
        # frame carries its own notches and voids -- a median 13.1 % of bbox on
        # the converted corpus -- and no choice of gaps can hand that back. Asking
        # the fit for W*H would demand 13 % more floor than the arrangement holds,
        # which reads as deviation and refusal that belong to the rig.
        src_cells = sum((p[2] - p[0]) * (p[3] - p[1]) for pl in parts for p in pl)
        bx1 = min(p[0] for pl in parts for p in pl)
        by1 = min(p[1] for pl in parts for p in pl)
        bx2 = max(p[2] for pl in parts for p in pl)
        by2 = max(p[3] for pl in parts for p in pl)
        fill = src_cells / max(1, (bx2 - bx1) * (by2 - by1))
        scale = (W * H * fill) / (sum(targets) * 1e6 / GRID_MM ** 2)
        targets = [max(1, round(a * 1e6 / GRID_MM ** 2 * scale)) for a in targets]

        # brief.md 6.1: a stated target is sovereign, an invented one is ours to
        # flex. The share is a probe parameter, never a shipped constant.
        stated = [rng.random() < STATED_SHARE for _ in types]
        weights = [W_STATED if s else W_INVENTED for s in stated]
        min_side = [1 if no_min else MIN_SIDE.get(t, MIN_SIDE_DEFAULT)
                    for t in types]

        # ADR 0014's join, as an index span on whichever axis the two parts
        # share an edge along.
        join_x, join_y = [], []
        for pl in spans:
            if len(pl) != 2:
                continue
            (a1, b1, c1, d1), (a2, b2, c2, d2) = pl
            if d1 == c2 or d2 == c1:                # stacked: shared edge runs in x
                join_x.append((max(a1, a2), min(b1, b2)))
            elif b1 == a2 or b2 == a1:              # side by side: shared edge in y
                join_y.append((max(c1, c2), min(d1, d2)))

        gx = uniform(xs, W)
        gy = uniform(ys, H)

        def areas(gx, gy):
            cx = [0]
            for v in gx:
                cx.append(cx[-1] + v)
            cy = [0]
            for v in gy:
                cy.append(cy[-1] + v)
            out = []
            for pl in spans:
                out.append(sum((cx[b] - cx[a]) * (cy[d2] - cy[c])
                               for a, b, c, d2 in pl))
            return out

        a0 = areas(gx, gy)
        dev0 = [abs(a - t) / t for a, t in zip(a0, targets)]

        gx0, gy0 = list(gx), list(gy)
        t0 = time.perf_counter()
        res, status = warp_model(spans, len(gx), len(gy), targets, W, H, weights,
                                 min_side, join_x, join_y, tlim,
                                 aspect=not no_aspect, seed=(gx0, gy0))
        times.append(time.perf_counter() - t0)
        solved += 1
        statuses[status] += 1
        if res is None:
            # The target Envelope cannot host this arrangement at the ergonomic
            # floor. Retrieval declines this candidate -- ADR 0005.
            infeasible_axis += 1
            declined.append(len(types))
            continue
        gx, gy, was_optimal = res
        if was_optimal:
            optimal += 1

        # 5.1's extractor, on both warps, scored against the source tiling.
        # The claim under test: a strictly increasing per-axis map cannot produce
        # a confident-wrong relation, for any dwelling and any target.
        def boxes(gx, gy):
            cx, cy = [0], [0]
            for v in gx:
                cx.append(cx[-1] + v)
            for v in gy:
                cy.append(cy[-1] + v)
            return [Rect(cx[a], cy[c], cx[b], cy[d2])
                    for pl in spans for a, b, c, d2 in pl]

        src_boxes = [Rect(p[0], p[1], p[2], p[3]) for pl in parts for p in pl]
        for tag, bx in (("affine", boxes(gx0, gy0)), ("fitted", boxes(gx, gy))):
            chosen, _ab, _cy = select_relations(rank_relations(bx), 4, len(bx))
            cw = sev = rev = 0
            for axis, a, b in chosen:
                c = (src_boxes[a].x2 - src_boxes[b].x1) if axis == "x" \
                    else (src_boxes[a].y2 - src_boxes[b].y1)
                if c > 0:
                    cw += 1
                    sev += c
                    other = (src_boxes[b].x2 - src_boxes[a].x1) if axis == "x" \
                        else (src_boxes[b].y2 - src_boxes[a].y1)
                    if other <= 0:
                        rev += 1
            if tag == "affine":
                cw_affine += cw
                sev_affine += sev
            else:
                cw_fitted += cw
                sev_fitted += sev
                rev_fitted += rev
                asserted_total += len(chosen)

        a1 = areas(gx, gy)
        dev1 = [abs(a - t) / t for a, t in zip(a1, targets)]
        aff_dev += dev0
        fit_dev += dev1
        aff_worst.append(max(dev0))
        fit_worst.append(max(dev1))
        st_dev += [d for d, s in zip(dev1, stated) if s]
        inv_dev += [d for d, s in zip(dev1, stated) if not s]

    def pct(v, q):
        v = sorted(v)
        return v[min(len(v) - 1, int(q * len(v)))]

    print(f"warped {solved} dwellings ({skipped} skipped on programme mismatch, "
          f"{gated_out} had no gate-admitted envelope)")
    print(f"warp time: median {st.median(times)*1000:.0f} ms  "
          f"p90 {pct(times,0.9)*1000:.0f} ms  ({iters} alternations, {tlim}s cap)\n")
    print(f"{'':22}{'p50':>9}{'p90':>9}{'p99':>9}")
    print(f"{'per-room |dev| affine':22}{st.median(aff_dev):>9.3f}"
          f"{pct(aff_dev,0.9):>9.3f}{pct(aff_dev,0.99):>9.3f}")
    print(f"{'per-room |dev| fitted':22}{st.median(fit_dev):>9.3f}"
          f"{pct(fit_dev,0.9):>9.3f}{pct(fit_dev,0.99):>9.3f}")
    print(f"{'worst-room affine':22}{st.median(aff_worst):>9.3f}"
          f"{pct(aff_worst,0.9):>9.3f}{pct(aff_worst,0.99):>9.3f}")
    print(f"{'worst-room fitted':22}{st.median(fit_worst):>9.3f}"
          f"{pct(fit_worst,0.9):>9.3f}{pct(fit_worst,0.99):>9.3f}")
    print(f"\nrelations, against the source tiling, tau = 4 "
          f"({asserted_total:,} asserted over {solved} warps)")
    print(f"  affine warp: confident-wrong {cw_affine}, severity {sev_affine} units")
    print(f"  fitted warp: confident-wrong {cw_fitted}, severity {sev_fitted} units, "
          f"reversals {rev_fitted}")
    print("")
    print(f"warp declined -- target Envelope cannot host the arrangement at the"
          f" ergonomic floor: {infeasible_axis}/{solved}"
          f" ({100*infeasible_axis/max(solved,1):.1f}%)")
    if declined:
        from collections import Counter as _C
        print(f"  by room count: {sorted(_C(declined).items())}")
    print(f"  proven OPTIMAL inside the {tlim}s cap: {optimal}/{solved-infeasible_axis}")
    print(f"  CP-SAT status: {dict(statuses)}")
    if st_dev and inv_dev:
        print(f"\nstated target (weight {W_STATED}) vs invented "
              f"(weight {W_INVENTED}), probe share {STATED_SHARE:.0%}")
        print(f"  stated   |dev| p50 {st.median(st_dev):.3f}  p90 {pct(st_dev,0.9):.3f}"
              f"   n={len(st_dev):,}")
        print(f"  invented |dev| p50 {st.median(inv_dev):.3f}  p90 {pct(inv_dev,0.9):.3f}"
              f"   n={len(inv_dev):,}")

    OUT.mkdir(exist_ok=True)
    json.dump({"n": solved, "iters": iters, "time_cap_s": tlim,
               "warp_ms_p50": st.median(times) * 1000,
               "warp_ms_p90": pct(times, 0.9) * 1000,
               "affine": {"p50": st.median(aff_dev), "p90": pct(aff_dev, 0.9),
                          "worst_p50": st.median(aff_worst)},
               "fitted": {"p50": st.median(fit_dev), "p90": pct(fit_dev, 0.9),
                          "worst_p50": st.median(fit_worst)}},
              open(OUT / "fit_warp.json", "w"), indent=1)
    print(f"\nwrote {OUT/'fit_warp.json'}")


if __name__ == "__main__":
    main()
