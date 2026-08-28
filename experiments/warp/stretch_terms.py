"""What the gate's two dimensional terms are a proxy FOR, measured directly.

Ticket 63. `proposer.md` 2.2 gates on total area +-10 % and envelope aspect
+-15 %. Ticket 60 measured that the pair is worth **8.6 points of decline**
through a mechanism it named but did not compute: ADR 0020 sizes the box from
the BRIEF, so a donor's own area and aspect never enter the warp's arithmetic --
what they bound is how hard the donor's **cut-line frame** has to stretch to
reach that box, and the stretch is what the ergonomic floor refuses.

This computes the stretch, three ways, and joins all three to the 1,974
candidates `gate_effect.py` has already warped. **No new warps.**

  `req`   -- THE BOUND. `warp_model` posts `sum(gx) = W`, `gx_i >= 1`, and per
             part `sum(gx[a:b]) >= MIN_SIDE[room]`. So for ANY set of parts with
             pairwise-disjoint x-spans, `sum MIN_SIDE <= W`. Maximising that sum
             over disjoint sets -- an interval DP, microseconds, no solve -- gives
             `W_req`, the smallest box extent this donor's frame admits at the
             ergonomic floor. `stretch_req = max(W_req/W, H_req/H)`, and the cut
             sits at **1.0** because that is where the warp's own hard constraint
             sits. No fitted constant, the same licence 2.2.4 gives
             `frontage_reach`. It is a NECESSARY condition for the 1-D relaxation
             of each axis, so `> 1` implies INFEASIBLE and the term is SOUND: it
             can only refuse a candidate the warp would have declined anyway.
             (It is not sufficient -- it ignores the 2-D aspect coupling
             `wv <= 3*hv` and the area objective -- so it under-refuses.)

  `ext`   -- the ticket's own first candidate: the per-axis ratio of the donor's
             frame extent to the Brief's box extent. **Included as a control, to
             show it is not a new quantity.** Box `= interior/(1-s)` at the
             Brief's aspect and donor bbox `= area_d/(1-s_d)` at `aspect_d`, so
             `(1-s)` cancels and
                 Wb/Wd = sqrt(area_ratio * aspect_ratio)
                 Hb/Hd = sqrt(area_ratio / aspect_ratio)
             which is a bijection with the incumbent pair up to the donor's VOID
             share, the one thing `s` excludes. If `ext` tracks the incumbent it
             is because it IS the incumbent in polar coordinates.

  `logd`  -- the incumbent pair as a smooth radial distance,
             `sqrt(ln^2(area ratio) + ln^2(aspect ratio))`. Same information,
             better-shaped acceptance region. It is the honest version of the
             conjunction that ticket 60 found fails **one term only 57.9 %** of
             the time -- a box replaced by a circle.

Reports the frontier the ticket asks for: for each term at each cut, the share of
the candidate population it admits against the decline rate and worst-room
deviation it delivers, plotted against the incumbent's own point.

Run: python experiments/warp/stretch_terms.py [--json]
"""

from __future__ import annotations

import json
import math
import random
import sys
import zlib
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fit_warp import (COLLAPSE, MIN_SIDE, MIN_SIDE_DEFAULT, JOIN_UNITS,   # noqa: E402
                      GRID_MM, coord_frame)
from absolute_area import (OUT, MARKET, F_PARTITION, notch_share,         # noqa: E402
                           joins, pair_targets, pct)
from fit_warp import SEED  # noqa: E402
from best_of_m import load                                                # noqa: E402


# --------------------------------------------------------------------------
# The bound

def axis_requirement(nbands, intervals):
    """Smallest total extent an axis admits, given `gap_i >= 1` and, for each
    interval `(a, b, w)`, `sum(gap[a:b]) >= w`.

    Exact for the 1-D relaxation: f[j] is the requirement of bands [0, j), and a
    band is either covered by a chosen interval ending at j or costs its own 1.
    Choosing a set of pairwise-disjoint intervals is what the recurrence does,
    and the max over such sets is the tightest bound this relaxation gives."""
    by_end = defaultdict(list)
    for a, b, w in intervals:
        if b > a:
            by_end[b].append((a, max(w, b - a)))   # a span also needs its bands
    f = [0] * (nbands + 1)
    for j in range(1, nbands + 1):
        best = f[j - 1] + 1
        for a, w in by_end.get(j, ()):
            cand = f[a] + w
            if cand > best:
                best = cand
        f[j] = best
    return f[nbands]


def frame_requirement(spans, nx, ny, min_side):
    """`(W_req, H_req)` in grid units, off the index record alone. No Brief."""
    ix, iy = [], []
    for r, parts in enumerate(spans):
        for (a, b, c, d) in parts:
            ix.append((a, b, min_side[r]))
            iy.append((c, d, min_side[r]))
    jx, jy = joins(spans)
    ix += [(a, b, JOIN_UNITS) for a, b in jx]
    iy += [(a, b, JOIN_UNITS) for a, b in jy]
    return axis_requirement(nx, ix), axis_requirement(ny, iy)


def gate_box(target_area, aspect, s):
    """ADR 0020's box at gate time -- scale 1.0, before any warp."""
    box_m2 = target_area * (1.0 + F_PARTITION) / (1.0 - s)
    Hm = (box_m2 * 1e6 / aspect) ** 0.5
    return max(4, round(aspect * Hm / GRID_MM)), max(4, round(Hm / GRID_MM))


# --------------------------------------------------------------------------

def enrich(briefs, recs):
    """Join every warped candidate to its donor's frame. Returns flat rows."""
    rows, misses = [], 0
    for b in briefs:
        brief = recs.get(b["k"])
        if brief is None:
            misses += 1
            continue
        for arm in ("admitted", "refused"):
            for o in b[arm]:
                cand = recs.get(o.get("donor"))
                if cand is None or o["status"] == "NOPAIR":
                    continue
                ct = [COLLAPSE.get(t, t) for t in cand["types"]]
                tg = pair_targets(ct, cand["parts"], brief["rooms"])
                if tg is None:
                    continue
                tg = [max(a, MARKET.get(t, 0.0)) for a, t in zip(tg, ct)]
                xs, ys, spans = coord_frame(cand["parts"])
                if len(xs) < 2 or len(ys) < 2:
                    continue
                s, _void = notch_share(cand["parts"])
                if s >= 0.60:
                    continue
                mins = [MIN_SIDE.get(t, MIN_SIDE_DEFAULT) for t in ct]
                wq, hq = frame_requirement(spans, len(xs) - 1, len(ys) - 1, mins)
                W, H = gate_box(sum(tg), brief["aspect"], s)

                ar = brief["area"] * (1.0 + F_PARTITION) / cand["area"]
                pr = brief["aspect"] / cand["aspect"]
                rows.append({
                    "brief": b["k"], "n": b["n"], "arm": arm,
                    "served": o["served"], "status": o["status"],
                    "dev": o.get("worst_room_dev"),
                    "d_area": o["d_area"], "d_aspect": o["d_aspect"],
                    "req": max(wq / W, hq / H),
                    "req_x": wq / W, "req_y": hq / H,
                    "ext": max(abs(math.log((ar * pr) ** 0.5)),
                               abs(math.log((ar / pr) ** 0.5))),
                    "logd": (math.log(ar) ** 2 + math.log(pr) ** 2) ** 0.5,
                    "donor": o["donor"],
                    "donor_ord": zlib.crc32((b["k"] + "|" + o["donor"]).encode()),
                })
    return rows, misses


def incumbent(r):
    return r["d_area"] <= 1.0 and r["d_aspect"] <= 1.0


def stats(rows):
    if not rows:
        return None
    dev = [r["dev"] for r in rows if r["dev"] is not None]
    dec = sum(1 for r in rows if not r["served"])
    return {"n": len(rows), "declined": dec,
            "decline_rate": round(dec / len(rows), 4),
            "dev_p50": round(pct(dev, 0.50), 4) if dev else None,
            "dev_p90": round(pct(dev, 0.90), 4) if dev else None}


def brief_served(rows, keep):
    """Briefs with at least one served candidate among those `keep` admits, and
    the depth that leaves. Depth is why this is not the same question as decline."""
    by_b, depth = defaultdict(list), defaultdict(int)
    for r in rows:
        if keep(r):
            by_b[r["brief"]].append(r["served"])
            depth[r["brief"]] += 1
    all_b = {r["brief"] for r in rows}
    served = sum(1 for b in all_b if any(by_b.get(b, ())))
    empty = sum(1 for b in all_b if not by_b.get(b))
    d = sorted(depth.get(b, 0) for b in all_b)
    return {"briefs": len(all_b), "served": served,
            "served_rate": round(served / len(all_b), 4),
            "pool_empty": empty,
            "median_depth": d[len(d) // 2] if d else 0}


def best_of(rows, keep, m=None):
    """What a HOMEOWNER gets: per Brief, the worst-room deviation of the BEST
    candidate the rule admits. C6's own semantics, and the axis a per-candidate
    decline rate is not -- ticket 60 measured the two disagree (p = 0.74).

    `m` caps the draw so two rules are compared at equal depth; the order is by
    donor key, which is arbitrary and therefore fair -- 2.2.4's pre-rank needs
    `worst_room_iou` and `frontage_reach`, neither of which this rig carries."""
    by_b = defaultdict(list)
    for r in rows:
        if keep(r):
            by_b[r["brief"]].append(r)
    best, served = {}, 0
    for b, rs in by_b.items():
        rs = sorted(rs, key=lambda r: r["donor_ord"])
        if m is not None:
            rs = rs[:m]
        ok = [r["dev"] for r in rs if r["served"] and r["dev"] is not None]
        if ok:
            best[b] = min(ok)
            served += 1
    vals = sorted(best.values())
    all_b = {r["brief"] for r in rows}
    return {"briefs_with_a_candidate": len(by_b), "briefs_served": served,
            "served_rate": round(served / len(all_b), 4),
            "best_dev_p50": round(pct(vals, 0.50), 4) if vals else None,
            "best_dev_p90": round(pct(vals, 0.90), 4) if vals else None,
            "_per_brief": best}


def sign_test(a, b):
    """Paired sign test on the Briefs both rules serve. `a` better = lower dev."""
    shared = set(a) & set(b)
    aw = sum(1 for k in shared if a[k] < b[k] - 1e-9)
    bw = sum(1 for k in shared if b[k] < a[k] - 1e-9)
    n, kk = aw + bw, min(aw, bw)
    p = 1.0
    if n:
        p = min(1.0, 2 * sum(math.comb(n, i) for i in range(kk + 1)) / 2 ** n)
    return {"shared": len(shared), "a_better": aw, "b_better": bw,
            "tied": len(shared) - aw - bw, "p_exact": round(p, 5)}


def frontier(rows, term, cuts):
    out = []
    for c in cuts:
        keep = [r for r in rows if r[term] <= c]
        st = stats(keep)
        if not st:
            continue
        st["cut"] = c
        st["admit_share"] = round(len(keep) / len(rows), 4)
        st.update(brief_served(rows, lambda r, c=c: r[term] <= c))
        out.append(st)
    return out


def main():
    want_json = "--json" in sys.argv
    briefs = json.load(open(OUT / "gate_effect_briefs.json"))
    cands, _by_ms, _by_n = load()
    recs = {c["k"]: c for c in cands}
    rows, misses = enrich(briefs, recs)
    print("gate_effect Briefs %d | candidates joined %d | donor misses %d"
          % (len(briefs), len(rows), misses))

    # -- 1. is the bound sound?  req > 1 must imply the warp declined.
    over = [r for r in rows if r["req"] > 1.0]
    infeas = [r for r in over if r["status"] != "OK"]
    print("\n--- 1. soundness of the bound ---")
    print("candidates with req > 1 (the box cannot hold the frame): %d of %d "
          "(%.1f %%)" % (len(over), len(rows), 100 * len(over) / len(rows)))
    if over:
        print("  of those, the warp returned not-OK : %d (%.1f %%)"
              % (len(infeas), 100 * len(infeas) / len(over)))
        print("  of those, declined (not served)    : %d (%.1f %%)"
              % (sum(1 for r in over if not r["served"]),
                 100 * sum(1 for r in over if not r["served"]) / len(over)))
    under_bad = [r for r in rows if r["req"] <= 1.0 and r["status"] != "OK"]
    print("candidates with req <= 1 that the warp still refused: %d "
          "(the 2-D coupling the bound does not model)" % len(under_bad))

    # -- 2. dose on each term
    print("\n--- 2. decline against each term ---")
    edges = {"d_area": (1, 2, 4), "d_aspect": (1, 2, 4),
             "req": (0.7, 0.85, 1.0), "ext": (0.05, 0.12, 0.25),
             "logd": (0.10, 0.22, 0.45)}
    for term, es in edges.items():
        print(" %s" % term)
        bounds = [(-1e9, es[0]), (es[0], es[1]), (es[1], es[2]), (es[2], 1e9)]
        names = ["<= %g" % es[0], "%g-%g" % (es[0], es[1]),
                 "%g-%g" % (es[1], es[2]), "> %g" % es[2]]
        for (lo, hi), nm in zip(bounds, names):
            sel = [r for r in rows if lo < r[term] <= hi]
            st = stats(sel)
            if st:
                print("   %-12s%7d cands%9.1f%%   dev p50 %s"
                      % (nm, st["n"], 100 * st["decline_rate"], st["dev_p50"]))

    # -- 3. the frontier, against the incumbent's own point
    print("\n--- 3. frontier: admit share vs decline vs fidelity ---")
    inc = stats([r for r in rows if incumbent(r)])
    inc["admit_share"] = round(sum(1 for r in rows if incumbent(r)) / len(rows), 4)
    inc.update(brief_served(rows, incumbent))
    print("%-22s%9s%9s%10s%10s%10s%9s" % ("rule", "admit", "cands", "decline",
                                          "dev p50", "dev p90", "served"))
    print("%-22s%8.1f%%%9d%9.1f%%%10s%10s%8.1f%%"
          % ("INCUMBENT +-10/+-15", 100 * inc["admit_share"], inc["n"],
             100 * inc["decline_rate"], inc["dev_p50"], inc["dev_p90"],
             100 * inc["served_rate"]))
    grids = {"req": (0.70, 0.80, 0.90, 1.00, 1.10),
             "ext": (0.05, 0.10, 0.15, 0.25, 0.40),
             "logd": (0.10, 0.20, 0.30, 0.45, 0.70)}
    front = {}
    for term, cuts in grids.items():
        front[term] = frontier(rows, term, cuts)
        for st in front[term]:
            print("%-22s%8.1f%%%9d%9.1f%%%10s%10s%8.1f%%"
                  % ("%s <= %g" % (term, st["cut"]), 100 * st["admit_share"],
                     st["n"], 100 * st["decline_rate"], st["dev_p50"],
                     st["dev_p90"], 100 * st["served_rate"]))

    # -- 4. the sound gate as a REPLACEMENT and as an ADDITION
    print("\n--- 4. sound gate (req <= 1) against the incumbent ---")
    combos = {
        "incumbent only": incumbent,
        "req <= 1 only": lambda r: r["req"] <= 1.0,
        "both (a third refuser)": lambda r: incumbent(r) and r["req"] <= 1.0,
        "logd <= 0.30 + req <= 1": lambda r: r["logd"] <= 0.30 and r["req"] <= 1.0,
    }
    rowsout = {}
    for nm, keep in combos.items():
        sel = [r for r in rows if keep(r)]
        st = stats(sel)
        st["admit_share"] = round(len(sel) / len(rows), 4)
        st.update(brief_served(rows, keep))
        rowsout[nm] = st
        print("%-26s%8.1f%%%9d%9.1f%%%10s%10s%8.1f%%  depth p50 %d"
              % (nm, 100 * st["admit_share"], st["n"],
                 100 * st["decline_rate"], st["dev_p50"], st["dev_p90"],
                 100 * st["served_rate"], st["median_depth"]))

    # -- 4b. the Homeowner's own number: best of pool, per Brief
    print("\n--- 4b. best-of-pool worst-room deviation, per Brief ---")
    print("%-26s%9s%9s%11s%11s   %s" % ("rule", "served", "depth",
                                        "best p50", "best p90", "vs incumbent"))
    bo, bo_m3 = {}, {}
    for nm, keep in combos.items():
        bo[nm] = best_of(rows, keep)
        bo_m3[nm] = best_of(rows, keep, m=3)
    base = bo["incumbent only"]["_per_brief"]
    base3 = bo_m3["incumbent only"]["_per_brief"]
    tests = {}
    for nm in combos:
        v, v3 = bo[nm], bo_m3[nm]
        t = sign_test(v["_per_brief"], base)
        tests[nm] = {"uncapped": t, "at_m3": sign_test(v3["_per_brief"], base3)}
        print("%-26s%8.1f%%%9s%11s%11s   better %d / worse %d / p %.4f"
              % (nm, 100 * v["served_rate"], "all", v["best_dev_p50"],
                 v["best_dev_p90"], t["a_better"], t["b_better"], t["p_exact"]))
        print("%-26s%8.1f%%%9d%11s%11s   better %d / worse %d / p %.4f"
              % ("  at same depth", 100 * v3["served_rate"], 3,
                 v3["best_dev_p50"], v3["best_dev_p90"],
                 tests[nm]["at_m3"]["a_better"], tests[nm]["at_m3"]["b_better"],
                 tests[nm]["at_m3"]["p_exact"]))
    # by band -- 7-10 is the band ADR 0013 calls tight and where depth is scarce
    print()
    print("--- 4c. best-of-pool by band, at equal depth m = 3 ---")
    bands = {"4-6": range(4, 7), "7-10": range(7, 11)}
    by_band = {}
    for bn, rng in bands.items():
        sub = [r for r in rows if r["n"] in rng]
        if not sub:
            continue
        print(" %s rooms (%d Briefs)" % (bn, len({r["brief"] for r in sub})))
        ref = best_of(sub, incumbent, m=3)
        by_band[bn] = {}
        for nm, keep in combos.items():
            v = best_of(sub, keep, m=3)
            t = sign_test(v["_per_brief"], ref["_per_brief"])
            by_band[bn][nm] = {k: x for k, x in v.items() if k != "_per_brief"}
            by_band[bn][nm]["sign_vs_incumbent"] = t
            print("   %-24s%8.1f%%   p50 %-8s p90 %-8s better %d / worse %d / p %.4f"
                  % (nm, 100 * v["served_rate"], v["best_dev_p50"],
                     v["best_dev_p90"], t["a_better"], t["b_better"],
                     t["p_exact"]))
        ref.pop("_per_brief", None)

    for d in list(bo.values()) + list(bo_m3.values()):
        d.pop("_per_brief", None)

    # -- 4e. THE TRAP IN 4b/4c, and the repair.
    #
    # `gate_effect` drew K = 3 from each stratum, so this population is 50/50
    # admitted/refused. A PRODUCTION bucket is 82.4 % refused (`gate_sites.py`),
    # so any rule that admits refused members is being measured on a pool far
    # richer than the one it would really draw from -- the bias runs TOWARD
    # replacing the incumbent, which is the direction this ticket is tempted in.
    #
    # The repair costs no warps. Each Brief record carries its own `n_admitted`
    # and `n_refused`, so weight each admitted row by `n_admitted / K` and each
    # refused row by `n_refused / K` and the urn has the bucket's real
    # composition. Draw m with replacement, take the best served member, repeat.
    print()
    print("--- 4e. same, at the bucket's REAL composition (bootstrap) ---")
    nadm = {b["k"]: b["n_admitted"] for b in briefs}
    nref = {b["k"]: b["n_refused"] for b in briefs}
    by_brief = defaultdict(list)
    for r in rows:
        by_brief[r["brief"]].append(r)

    def weighted(rows_, keep, m, draws=400):
        urns = {}
        for b, rs in by_brief.items():
            sel = [r for r in rs if keep(r)]
            if not sel:
                continue
            w = [(nadm[b] if r["arm"] == "admitted" else nref[b]) for r in sel]
            if sum(w) <= 0:
                continue
            urns[b] = (sel, w)
        rng = random.Random(SEED)
        served_acc, dev_acc = [], []
        for _ in range(draws):
            ok, devs = 0, []
            for b in by_brief:
                if b not in urns:
                    continue
                sel, w = urns[b]
                drawn = rng.choices(sel, weights=w, k=m)
                good = [d["dev"] for d in drawn
                        if d["served"] and d["dev"] is not None]
                if good:
                    ok += 1
                    devs.append(min(good))
            served_acc.append(ok / len(by_brief))
            dev_acc.append((pct(sorted(devs), 0.50), pct(sorted(devs), 0.90)))
        served_acc.sort()
        p50s = sorted(d[0] for d in dev_acc)
        p90s = sorted(d[1] for d in dev_acc)
        return {"served_rate": round(served_acc[len(served_acc) // 2], 4),
                "served_ci": [round(served_acc[int(0.025 * draws)], 4),
                              round(served_acc[int(0.975 * draws)], 4)],
                "best_dev_p50": round(p50s[draws // 2], 4),
                "best_dev_p90": round(p90s[draws // 2], 4),
                "p90_ci": [round(p90s[int(0.025 * draws)], 4),
                           round(p90s[int(0.975 * draws)], 4)]}

    # !! m = 3 is the load-bearing row and m = 8 is NOT QUOTABLE. The urn draws
    # WITH replacement from at most 6 warped rows -- 3 admitted, 3 refused -- so
    # every arm saturates at its own DISTINCT count, and the incumbent's is 3
    # against a loose rule's 6. At m = 8 that is a best-of-3 against a
    # best-of-6, which flatters any rule that admits refused members by exactly
    # the amount this ticket is trying to measure. m = 3 is the largest depth
    # both arms can fill with distinct warps, so it is the honest comparison.
    # A real m = 8 needs `gate_effect.py --k=8`, which is 16 warps a Brief.
    weighted_out = {}
    for m in (3, 8):
        print(" m = %d%s" % (m, "" if m == 3 else
                             "   !! CONFOUNDED -- best-of-3 vs best-of-6, do not quote"))
        for nm, keep in combos.items():
            v = weighted(rows, keep, m)
            weighted_out["%s @ m=%d" % (nm, m)] = v
            print("   %-24s served %5.1f%% [%.1f-%.1f]   p50 %-8s p90 %-8s [%.3f-%.3f]"
                  % (nm, 100 * v["served_rate"], 100 * v["served_ci"][0],
                     100 * v["served_ci"][1], v["best_dev_p50"],
                     v["best_dev_p90"], v["p90_ci"][0], v["p90_ci"][1]))

    # -- 4d. dim.max_area, the hard CEILING `served` does not test
    #
    # `served` is the ergonomic FLOOR. `dim.max_area` is `got <= k[type] *
    # target` with k in 2.02-8.15 (`rules.json` area_bands), so a breach needs
    # some room at `got/target - 1 > 1.02`, and `worst_room_dev` is the max of
    # that over rooms. `dev > 1.02` is therefore a NECESSARY condition and this
    # is an exact upper bound on the breach rate -- no re-warp.
    K_MIN = 2.02
    print()
    print("--- 4d. dim.max_area breach ceiling (dev > %.2f) ---" % (K_MIN - 1))
    ceil_out = {}
    for nm, keep in combos.items():
        sel = [r for r in rows if keep(r) and r["served"] and r["dev"] is not None]
        over = [r for r in sel if r["dev"] > K_MIN - 1]
        ceil_out[nm] = {"served_candidates": len(sel), "may_breach": len(over),
                        "upper_bound": round(len(over) / max(1, len(sel)), 4)}
        print("%-26s%7d served cands, at most %d could breach (%.2f %%)"
              % (nm, len(sel), len(over), 100 * len(over) / max(1, len(sel))))

    # -- 5. is `ext` the incumbent in disguise?
    print("\n--- 5. is `ext` a new quantity? ---")
    agree = sum(1 for r in rows if incumbent(r) == (r["ext"] <= 0.1226))
    print("ext <= 0.1226 agrees with the incumbent conjunction on %.1f %% of "
          "candidates" % (100 * agree / len(rows)))
    print("(0.1226 = the ext value of a donor exactly at both tolerances)")

    if want_json:
        json.dump({"soundness": {"over": len(over), "rows": len(rows),
                                 "not_ok": len(infeas),
                                 "under_but_refused": len(under_bad)},
                   "incumbent": inc, "frontier": front, "combos": rowsout,
                   "best_of_pool": bo, "best_of_pool_m3": bo_m3,
                   "sign_tests": tests, "by_band_m3": by_band, "max_area_ceiling": ceil_out,
                   "production_composition": weighted_out},
                  open(OUT / "stretch_terms.json", "w"), indent=1)
        print("\nwrote %s" % (OUT / "stretch_terms.json"))


if __name__ == "__main__":
    main()
