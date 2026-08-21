"""Ticket 33 — the four items, off `out/walls.json.gz`.

  item 0  calibration: does Swiss Dwellings record a finish layer at all, and
          therefore which plane is `t_int` = 150 comparable to?
  item 1  does a dwelling drawn with ONE internal thickness read as real —
          i.e. how many internal thicknesses does a real dwelling carry?
  item 2  area drift: what our uniform `t_int` does to Sum(Space area), per
          room and per dwelling.
  item 3  what a second thickness buys, measured, against three ways of
          spending it.
  item 4  does the thin-`t_int` bias compound with the conversion's known bias
          toward small dwellings?

Run:  python experiments/thickness-fidelity/analyse.py > out/analysis.txt
"""
from __future__ import annotations

import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
FIT = HERE.parents[0] / "rectangularise" / "out" / "swiss_fit.json"

T_SHIPPED = 150        # AZ t_int TOTAL, ADR 0010
T_OLD = 120            # AZ t_int before ADR 0010 (bare half-brick)
T_BEARING = 280        # what a second t_int would be: 250 one-brick + 2 x 15
BAND = (4, 10)         # C13
MIN_L = 3.0            # m of internal wall below which a dwelling is not judged


def pct(a, qs=(5, 10, 25, 50, 75, 90, 95)):
    a = np.asarray(a, dtype=float)
    return "  ".join(f"p{q}={np.percentile(a, q):.0f}" for q in qs)


def lw_percentiles(vals, wts, qs=(5, 10, 25, 50, 75, 90, 95)):
    """Length-weighted percentiles."""
    v = np.asarray(vals, float)
    w = np.asarray(wts, float)
    o = np.argsort(v)
    v, w = v[o], w[o]
    c = np.cumsum(w) / w.sum()
    return {q: float(v[min(np.searchsorted(c, q / 100), len(v) - 1)]) for q in qs}


def load():
    with gzip.open(OUT / "walls.json.gz", "rt", encoding="utf-8") as fh:
        d = json.load(fh)
    dw = [r for r in d["dwellings"]
          if BAND[0] <= r["n_rooms"] <= BAND[1]
          and sum(w["len_int"] for w in r["internal"]) >= MIN_L
          and r["sum_area"] > 10]
    return d, dw


def classes(walls, tol):
    """Length-weighted distinct thickness classes, greedy by length.

    A class is seeded by the longest unassigned wall and absorbs every wall
    within `tol` mm of it. Classes holding under 5 % of the dwelling's internal
    wall length are folded away as construction noise, not as a design choice.
    """
    ws = sorted(walls, key=lambda w: -w["len_int"])
    total = sum(w["len_int"] for w in ws)
    out = []
    used = [False] * len(ws)
    for i, w in enumerate(ws):
        if used[i]:
            continue
        seed, L = w["t_mrr"], 0.0
        for j in range(i, len(ws)):
            if not used[j] and abs(ws[j]["t_mrr"] - seed) <= tol:
                used[j] = True
                L += ws[j]["len_int"]
        out.append((seed, L))
    return [c for c in out if c[1] >= 0.05 * total], total


def main() -> None:
    meta, dw = load()
    print(f"# ticket 33 — one internal thickness against the corpus")
    print(f"\nSwiss Dwellings v3.0.0, 1-in-{meta['stride']} floor sample.")
    print(f"dwellings measured in C13 band {BAND} with >= {MIN_L} m internal wall: "
          f"{len(dw):,}")
    print(f"geometry repairs: {meta['repairs']}    probe stations per wall: "
          f"{meta['stations']}")

    iw = [w for r in dw for w in r["internal"]]
    bw = [w for r in dw for w in r["boundary"]]
    Li = sum(w["len_int"] for w in iw)
    Lb = sum(w["len_bnd"] for w in bw)
    print(f"\ninternal wall runs: {len(iw):,}  ({Li/1000:.1f} km)"
          f"   boundary runs: {len(bw):,}  ({Lb/1000:.1f} km)")
    si = sum(w["n_int"] for w in iw + bw)
    sb = sum(w["n_bnd"] for w in iw + bw)
    sv = sum(w["n_void"] for w in iw + bw)
    st = si + sb + sv
    print(f"probe stations: internal {100*si/st:.1f}%   boundary {100*sb/st:.1f}%"
          f"   neither side found a room {100*sv/st:.1f}%   (n={st:,})")
    print("   a `void` station is a wall whose rooms sit further than D_MAX=600 mm "
          "from its\n   centreline, or off perpendicular; it biases the internal "
          "population toward the\n   thinner walls and is reported rather than "
          "corrected.")

    # ---------------------------------------------------------------- item 0
    print("\n" + "=" * 72)
    print("ITEM 0 — which plane does the corpus record?")
    print("=" * 72)
    ex = np.array([e for w in iw for e in w["excess"]])
    print(f"\n(gap between the two Space polygons) - (wall polygon thickness), "
          f"n={len(ex):,} stations")
    bins = [(-1e9, -5), (-5, 5), (5, 12), (12, 20), (20, 26), (26, 36),
            (36, 60), (60, 1e9)]
    for lo, hi in bins:
        s = 100 * np.mean((ex >= lo) & (ex < hi))
        print(f"   [{lo if lo > -1e8 else '-inf':>5} , {hi if hi < 1e8 else 'inf':>4} )  "
              f"{s:5.2f}%")
    print(f"   median {np.median(ex):.1f} mm   modal bucket "
          f"{Counter((np.round(ex)).astype(int)).most_common(4)}")

    # ---------------------------------------------------------------- item 1
    print("\n" + "=" * 72)
    print("ITEM 1 — how many internal thicknesses does a real dwelling carry?")
    print("=" * 72)
    lw = lw_percentiles([w["t_mrr"] for w in iw], [w["len_int"] for w in iw])
    print("\nlength-weighted INTERNAL wall thickness (t_mrr), mm:")
    print("   " + "  ".join(f"p{q}={v:.0f}" for q, v in lw.items()))
    lwb = lw_percentiles([w["t_mrr"] for w in bw], [w["len_bnd"] for w in bw])
    print("length-weighted BOUNDARY wall thickness (exterior + party), mm:")
    print("   " + "  ".join(f"p{q}={v:.0f}" for q, v in lwb.items()))

    for tol in (5, 10, 20, 40):
        n = Counter()
        for r in dw:
            cs, _ = classes(r["internal"], tol)
            n[min(len(cs), 6)] += 1
        tot = sum(n.values())
        row = "  ".join(f"{k}:{100*n[k]/tot:5.1f}%" for k in sorted(n))
        print(f"\ndistinct internal thickness classes per dwelling, tol +/-{tol:2d} mm")
        print(f"   {row}")
        print(f"   >= 2 classes: {100*(tot-n[1])/tot:.1f}%")

    ratios, spreads = [], []
    for r in dw:
        cs, _ = classes(r["internal"], 10)
        ts = [c[0] for c in cs]
        ratios.append(max(ts) / min(ts))
        spreads.append(max(ts) - min(ts))
    ratios = np.array(ratios)
    print(f"\nheaviest / lightest internal class in one dwelling (tol +/-10 mm):")
    print("   " + "  ".join(f"p{q}={np.percentile(ratios, q):.2f}"
                            for q in (10, 25, 50, 75, 90, 95)))
    for k in (1.25, 1.5, 2.0, 2.5):
        print(f"   dwellings whose heaviest internal wall is >= {k:.2f}x its "
              f"lightest: {100*np.mean(ratios >= k):.1f}%")
    spreads = np.array(spreads)
    print("   absolute spread (mm): " + "  ".join(
        f"p{q}={np.percentile(spreads, q):.0f}" for q in (25, 50, 75, 90)))
    print(f"   dwellings whose internal spread is >= 50 mm -- 1 mm of paper at "
          f"1:50, the\n   threshold at which two solid poche bands read as "
          f"different walls: {100*np.mean(spreads >= 50):.1f}%")
    print(f"   >= 100 mm (2 mm of paper): {100*np.mean(spreads >= 100):.1f}%")

    # The claim §2.3 makes about the drawing: a real plan carries THREE visible
    # wall weights and a uniform t_int collapses it to two. Count them.
    three = two = 0
    for r in dw:
        cs, _ = classes(r["internal"], 10)
        ts = [c[0] for c in cs]
        bnd = [w["t_mrr"] for w in r["boundary"] if w["len_bnd"] >= 1.0]
        if not bnd:
            continue
        heaviest_int = max(ts)
        lightest_int = min(ts)
        if max(bnd) - heaviest_int >= 50 and heaviest_int - lightest_int >= 50:
            three += 1
        elif max(bnd) - heaviest_int >= 50:
            two += 1
    n3 = three + two
    if n3:
        print(f"\nvisible wall-weight hierarchy at 1:50 (>= 50 mm = 1 mm of paper "
              f"between bands):")
        print(f"   dwellings showing THREE weights -- envelope, internal bearing, "
              f"partition: {100*three/n3:.1f}%")
        print(f"   dwellings showing only two:                                    "
              f"      {100*two/n3:.1f}%")
        print(f"   a uniform t_int always draws exactly TWO.")

    heavy = sum(w["len_int"] for w in iw if w["t_mrr"] >= 200)
    vheavy = sum(w["len_int"] for w in iw if w["t_mrr"] >= 300)
    print(f"\ninternal wall LENGTH at >= 200 mm (a plausible internal bearing "
          f"wall): {100*heavy/Li:.1f}%")
    print(f"internal wall LENGTH at >= 300 mm (implausible as a partition -- the "
          f"classifier's\n   own error bar): {100*vheavy/Li:.1f}%")
    hd = np.mean([any(w["t_mrr"] >= 200 and w["len_int"] >= 1.0
                      for w in r["internal"]) for r in dw])
    print(f"dwellings holding at least 1 m of internal wall >= 200 mm: "
          f"{100*hd:.1f}%")

    # ---------------------------------------------------------------- item 2
    print("\n" + "=" * 72)
    print("ITEM 2 — area drift")
    print("=" * 72)

    # Three estimators of the same quantity, deliberately not one. They fail in
    # different directions, so agreement is evidence and disagreement is a flag.
    #   `wall`  Sum over internal walls of (Space-to-Space gap - t) * length.
    #   `area`  the morphological closing's own partition footprint - t * L_int,
    #           which counts junction material the per-wall sum misses.
    #   `body`  the same as `wall` but using the wall polygon's own thickness
    #           instead of the probed gap, so it is immune to a probe that
    #           reaches past the wall into a duct or a second leaf.
    def drift_rows(t):
        rows = []
        for r in dw:
            L = sum(w["len_int"] for w in r["internal"])
            wall = sum((w["gap"] - t) / 1000.0 * w["len_int"] for w in r["internal"])
            body = sum((w["t_mrr"] + 2 - t) / 1000.0 * w["len_int"]
                       for w in r["internal"])
            fill = r.get("fill_area")
            if fill is None or not np.isfinite(fill) or fill < 0:
                area = None
            else:
                area = fill - t / 1000.0 * L
            rows.append((r, L, wall, area, body))
        return rows

    for t in (T_OLD, T_SHIPPED, T_BEARING):
        rows = drift_rows(t)
        rel = np.array([100 * w / r["sum_area"] for r, _, w, _, _ in rows])
        relA = np.array([100 * a / r["sum_area"] for r, _, _, a, _ in rows
                         if a is not None])
        relB = np.array([100 * b / r["sum_area"] for r, _, _, _, b in rows])
        absd = np.array([w for _, _, w, _, _ in rows])
        tag = {T_OLD: "pre-ADR-0010", T_SHIPPED: "SHIPPED",
               T_BEARING: "t_bearing+finish"}[t]
        print(f"\nt_int = {t} mm  ({tag})")
        print(f"   drift per dwelling, % of Sum(Space area)   "
              f"[+ = our rooms bigger than the corpus's]")
        for nm, v in (("wall (gap)", rel), ("area (closing)", relA),
                      ("body (t_mrr)", relB)):
            print(f"      {nm:<16}" + "  ".join(f"p{q}={np.percentile(v, q):+.1f}"
                                                for q in (5, 25, 50, 75, 95))
                  + f"   mean {v.mean():+.2f}%")
        print(f"      dwellings drifting POSITIVE: {100*np.mean(rel > 0):.1f}% "
              f"(wall)   {100*np.mean(relB > 0):.1f}% (body)")
        print(f"   absolute, m^2 per dwelling: "
              + "  ".join(f"p{q}={np.percentile(absd, q):+.2f}"
                          for q in (5, 25, 50, 75, 95))
              + f"   mean {absd.mean():+.3f}")

    # ADR 0010 consequence 4 asserts the partition footprint is "roughly 4-5 %"
    # of a 90 m^2 dwelling. Nothing on the map measured it. Check it.
    print("\nADR 0010 consequence 4 says the partition footprint is 'roughly 4-5 %' "
          "of a 90 m^2\ndwelling. Measured here, as a share of Sum(Space area):")
    for t in (T_OLD, T_SHIPPED, T_BEARING):
        f = np.array([100 * t / 1000.0 * sum(w["len_int"] for w in r["internal"])
                      / r["sum_area"] for r in dw])
        print(f"   our own footprint at t_int = {t:3d}: "
              + "  ".join(f"p{q}={np.percentile(f, q):.1f}%"
                          for q in (25, 50, 75))
              + f"   mean {f.mean():.1f}%")
    fr = np.array([100 * r["fill_area"] / r["sum_area"] for r in dw
                   if r.get("fill_area") is not None
                   and np.isfinite(r["fill_area"]) and r["fill_area"] >= 0])
    print(f"   the corpus's OWN partition footprint:  "
          + "  ".join(f"p{q}={np.percentile(fr, q):.1f}%" for q in (25, 50, 75))
          + f"   mean {fr.mean():.1f}%")

    # What the drift is worth against the gates that consume Sum(Space area).
    print("\nwhat the drift at t_int = 150 is worth against the rules that read "
          "Sum(Space area):")
    rows = drift_rows(T_SHIPPED)
    for nm, idx in (("wall (gap)", 2), ("area (closing)", 3), ("body (t_mrr)", 4)):
        v = np.array([100 * r[idx] / r[0]["sum_area"] for r in rows
                      if r[idx] is not None])
        m = abs(v.mean())
        print(f"   {nm:<16} mean |drift| {m:.2f}%  =  {100*m/5:.0f}% of the 5% hard "
              f"gate (area.invented_envelope_hard),\n{'':21}{100*m/2:.0f}% of the 2% "
              f"soft one, and {m/1.2:.1f}x the corpus's own median area deviation "
              f"of 1.2%")

    # per room
    print("\nper-room drift at the shipped t_int = 150 mm")
    per_type = defaultdict(list)
    allroom = []
    for r in dw:
        acc = defaultdict(float)
        for w in r["internal"]:
            if not w["pairs"]:
                continue
            share = (w["gap"] - T_SHIPPED) / 1000.0 * w["len_int"] / len(w["pairs"])
            for a, b in w["pairs"]:
                acc[a] += share / 2
                acc[b] += share / 2
        for i, d in acc.items():
            if i < len(r["room_area"]) and r["room_area"][i] > 1.0:
                v = 100 * d / r["room_area"][i]
                allroom.append(v)
                per_type[r["types"][i]].append(v)
    allroom = np.array(allroom)
    print(f"   n rooms = {len(allroom):,}   "
          + "  ".join(f"p{q}={np.percentile(allroom, q):+.1f}"
                      for q in (5, 25, 50, 75, 95))
          + f"   mean {allroom.mean():+.2f}%")
    print("   by room type (mean %, n):")
    for k, v in sorted(per_type.items(), key=lambda kv: -len(kv[1]))[:12]:
        print(f"      {k:<15} {np.mean(v):+6.2f}%   n={len(v):,}")

    # ---------------------------------------------------------------- item 3
    print("\n" + "=" * 72)
    print("ITEM 3 — what a second thickness would buy")
    print("=" * 72)

    def cost(assign):
        """Sum over internal walls of |gap - t| * len, m^2 of misplaced material."""
        return sum(abs(w["gap"] - assign(r, w)) / 1000.0 * w["len_int"]
                   for r in dw for w in r["internal"])

    base = sum(w["gap"] / 1000.0 * w["len_int"] for r in dw for w in r["internal"])
    c1 = cost(lambda r, w: T_SHIPPED)
    print(f"\nreal internal partition material in the sample: {base:,.0f} m^2")
    print(f"   A. one t_int = 150 everywhere (SHIPPED)             "
          f"misplaced {c1:,.0f} m^2   {100*c1/base:5.1f}%")

    # option A: one t_int per PLAN, best of {150, 280}
    def per_plan(r):
        L = sum(w["len_int"] for w in r["internal"])
        best, bt = None, None
        for t in (T_SHIPPED, T_BEARING):
            c = sum(abs(w["gap"] - t) / 1000.0 * w["len_int"] for w in r["internal"])
            if best is None or c < best:
                best, bt = c, t
        return bt
    chosen = {r["k"]: per_plan(r) for r in dw}
    cA = cost(lambda r, w: chosen[r["k"]])
    n280 = sum(1 for r in dw if chosen[r["k"]] == T_BEARING)
    print(f"   B. one t_int per PLAN, better of {{150, 280}}         "
          f"misplaced {cA:,.0f} m^2   {100*cA/base:5.1f}%"
          f"    (plans picking 280: {100*n280/len(dw):.1f}%)")

    cB = cost(lambda r, w: min((T_SHIPPED, T_BEARING),
                               key=lambda t: abs(w["gap"] - t)))
    print(f"   C. two t_int WITHIN a plan, {{150, 280}} per wall     "
          f"misplaced {cB:,.0f} m^2   {100*cB/base:5.1f}%")

    # Best possible 1- and 2-value catalogues, length-weighted L1. Done on a
    # 2 mm weighted histogram of the gap, which is exact to within a bin.
    g = np.array([w["gap"] for r in dw for w in r["internal"]])
    L = np.array([w["len_int"] for r in dw for w in r["internal"]])
    edges = np.arange(0, 1002, 2.0)
    cen = (edges[:-1] + edges[1:]) / 2
    wgt, _ = np.histogram(np.clip(g, 0, 999), bins=edges, weights=L)
    grid = np.arange(60, 601, 2.0)
    D = np.abs(grid[:, None] - cen[None, :])           # (n_grid, n_bins)
    c1s = (D * wgt).sum(axis=1) / 1000.0
    t1 = int(grid[int(np.argmin(c1s))])
    print(f"\n   best single value, length-weighted L1: t = {t1} mm   "
          f"misplaced {c1s.min():,.0f} m^2   {100*c1s.min()/base:5.1f}%")
    M = np.minimum(D[:, None, :], D[None, :, :])       # (n_grid, n_grid, n_bins)
    C = (M * wgt).sum(axis=2) / 1000.0
    ia, ib = np.unravel_index(int(np.argmin(C)), C.shape)
    best2 = float(C[ia, ib])
    pair = (int(grid[min(ia, ib)]), int(grid[max(ia, ib)]))
    print(f"   best PAIR, per wall:  t = {pair}         "
          f"misplaced {best2:,.0f} m^2   {100*best2/base:5.1f}%")
    print(f"   ceiling: a perfect per-wall thickness would misplace 0 m^2.")

    # The decomposition that decides item 3: with the SAME best pair available,
    # how much does choosing it per PLAN buy, and how much only per WALL? The
    # difference is exactly the part of the variation that lives INSIDE a
    # dwelling, which is the only part a second construction type cannot reach.
    def per_plan_best(r, opts):
        return min(opts, key=lambda t: sum(abs(w["gap"] - t) / 1000.0 * w["len_int"]
                                           for w in r["internal"]))
    chosen2 = {r["k"]: per_plan_best(r, pair) for r in dw}
    cBstar = cost(lambda r, w: chosen2[r["k"]])
    cCstar = cost(lambda r, w: min(pair, key=lambda t: abs(w["gap"] - t)))
    n_hi = sum(1 for r in dw if chosen2[r["k"]] == pair[1])
    print(f"\n   with the SAME best pair {pair} available:")
    print(f"      chosen once per PLAN : misplaced {cBstar:,.0f} m^2  "
          f"{100*cBstar/base:5.1f}%   (plans picking the heavier: "
          f"{100*n_hi/len(dw):.1f}%)")
    print(f"      chosen per WALL      : misplaced {cCstar:,.0f} m^2  "
          f"{100*cCstar/base:5.1f}%")
    span = c1s.min() - cCstar
    if span > 0:
        print(f"      of the {100*span/base:.1f} points a second thickness can win, "
              f"per-plan selection\n      reaches "
              f"{100*(c1s.min()-cBstar)/span:.0f}% and the remaining "
              f"{100*(cBstar-cCstar)/span:.0f}% lives INSIDE a dwelling.")

    print("\n   drift at each option (mean % of Sum(Space area) per dwelling):")
    for name, fn in (("A one t_int = 150", lambda r, w: T_SHIPPED),
                     ("B one per plan {150,280}", lambda r, w: chosen[r["k"]]),
                     ("C two per wall {150,280}",
                      lambda r, w: min((T_SHIPPED, T_BEARING),
                                       key=lambda t: abs(w["gap"] - t))),
                     (f"D two per wall {pair}",
                      lambda r, w: min(pair, key=lambda t: abs(w["gap"] - t)))):
        rel = np.array([100 * sum((w["gap"] - fn(r, w)) / 1000.0 * w["len_int"]
                                  for w in r["internal"]) / r["sum_area"] for r in dw])
        print(f"      {name:<26} mean {rel.mean():+.2f}%   "
              f"p50 {np.percentile(rel, 50):+.2f}%   "
              f"|drift| p90 {np.percentile(np.abs(rel), 90):.2f}%")

    # ---------------------------------------------------------------- item 4
    print("\n" + "=" * 72)
    print("ITEM 4 — do the two biases compound?")
    print("=" * 72)
    sizes = np.array([r["sum_area"] for r in dw])
    rooms_n = np.array([r["n_rooms"] for r in dw])
    rel = np.array([100 * sum((w["gap"] - T_SHIPPED) / 1000.0 * w["len_int"]
                              for w in r["internal"]) / r["sum_area"] for r in dw])
    relb = np.array([100 * sum((w["t_mrr"] + 2 - T_SHIPPED) / 1000.0 * w["len_int"]
                               for w in r["internal"]) / r["sum_area"] for r in dw])
    teff = np.array([lw_percentiles([w["t_mrr"] for w in r["internal"]],
                                    [w["len_int"] for w in r["internal"]])[50]
                     for r in dw])
    print(f"\nSum(Space area) in the sample, m^2: {pct(sizes)}")
    print(f"rooms per dwelling:                 {pct(rooms_n)}")
    print(f"\ndrift vs dwelling size, by Sum(Space area) quintile:")
    qs = np.percentile(sizes, [20, 40, 60, 80])
    b = np.digitize(sizes, qs)
    for i in range(5):
        m = b == i
        print(f"   Q{i+1}  area p50 {np.median(sizes[m]):6.1f} m^2  n={m.sum():5d}  "
              f"median internal t {np.median(teff[m]):5.0f} mm  "
              f"drift mean {rel[m].mean():+.2f}% (wall)  "
              f"{relb[m].mean():+.2f}% (body)")
    print(f"\ndrift vs room count:")
    for k in range(BAND[0], BAND[1] + 1):
        m = rooms_n == k
        if m.sum() < 20:
            continue
        print(f"   {k:2d} rooms  n={m.sum():5d}  median internal t "
              f"{np.median(teff[m]):5.0f} mm   drift mean {rel[m].mean():+.2f}% (wall)"
              f"  {relb[m].mean():+.2f}% (body)")

    if FIT.exists():
        fit = json.loads(FIT.read_text(encoding="utf-8"))
        st = {r["k"].split("|")[1] + "|" + r["k"].split("|")[2]: r["status"]
              for r in fit}
        conv, drop = [], []
        for i, r in enumerate(dw):
            s = st.get(r["k"])
            if s == "OPTIMAL":
                conv.append(i)
            elif s == "INFEASIBLE":
                drop.append(i)
        print(f"\njoined to ADR 0008 conversion status "
              f"(experiments/rectangularise/out/swiss_fit.json):")
        print(f"   converted n={len(conv)}   dropped n={len(drop)}")
        for nm, ix in (("converted", conv), ("dropped", drop)):
            if not ix:
                continue
            ix = np.array(ix)
            print(f"   {nm:<10} median area {np.median(sizes[ix]):6.1f} m^2   "
                  f"median rooms {np.median(rooms_n[ix]):.0f}   "
                  f"median internal t {np.median(teff[ix]):5.0f} mm   "
                  f"drift mean {rel[ix].mean():+.2f}% (wall)  "
                  f"{relb[ix].mean():+.2f}% (body)")

    # closing-radius sensitivity
    print("\nclosing-radius sensitivity on the area-based partition footprint:")
    for rr in ("0.25", "0.35", "0.5"):
        v = [r["fill_by_r"][rr] / max(1e-9, sum(w["len_int"] for w in r["internal"]))
             * 1000 for r in dw
             if r.get("fill_by_r", {}).get(rr) is not None
             and np.isfinite(r["fill_by_r"][rr]) and r["fill_by_r"][rr] >= 0]
        if v:
            print(f"   r={rr} m   t_eff median {np.median(v):.0f} mm   "
                  f"p25 {np.percentile(v, 25):.0f}  p75 {np.percentile(v, 75):.0f}")


if __name__ == "__main__":
    main()
