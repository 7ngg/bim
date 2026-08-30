"""Does the gate's second and third term buy fidelity, holding the Brief fixed?

Ticket 60. `absolute_area.gate_pool` returned the whole multiset bucket the
moment it is non-empty and applies the area and aspect terms only in its
by-room-count fallback, so every warp-fidelity number this map publishes was
measured through a pool the shipped gate would not have handed it.

57 measured both definitions and found first-candidate decline **29.8 %** gated
against **35.2 %** on the bucket. That comparison is **between pools, not within
a Brief**: the gated arm serves 171 Briefs and the rig arm 199, so the two arms
answer different populations and the 5.4 points could be composition alone.

This is the paired version. For one Brief, split its own bucket into

  `admitted` -- the members 2.2.1's other two terms admit
  `refused`  -- the members they do not

warp K from each with the SAME Brief, the same targets, the same ring, and
compare. A Brief with fewer than K in either stratum is dropped rather than
counted at a different depth on the two arms.

It also records, per candidate, how far outside the tolerance the donor sits on
each term separately -- `d_area` and `d_aspect`, in units of the tolerance, so
1.0 is exactly at the bound. ADR 0020 sizes the box from the BRIEF's area and
aspect and takes only the donor's cut-line frame and notch share, so neither
quantity reaches the warp's arithmetic; if either predicts decline anyway it is
doing so through the frame it stretches, and the two terms can be priced apart.

Run: python experiments/warp/gate_effect.py [n] [--k=3] [--time=3.0] [--no-ring]
"""

from __future__ import annotations

import json
import random
import zlib
import sys
import time
from collections import defaultdict
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fit_warp import SEED, AREA_TOL, ASPECT_TOL                     # noqa: E402
from absolute_area import (OUT, MARKET, COLLAPSE, pair_targets,     # noqa: E402
                           run_one, floors_for, pct)
from best_of_m import load, gated_pool                              # noqa: E402


def strata(brief, by_ms):
    """The Brief's own bucket, split by the two terms the rig skips."""
    bucket = [p for p in by_ms.get(brief["ms"], []) if p["k"] != brief["k"]]
    adm = set(id(p) for p in gated_pool(brief, by_ms))
    admitted = [p for p in bucket if id(p) in adm]
    refused = [p for p in bucket if id(p) not in adm]
    return bucket, admitted, refused


def term_distances(brief, cand):
    """How far outside each term the donor sits, in units of that tolerance.
    <= 1.0 is admitted on that term; the gate is the conjunction of the two."""
    da = abs(brief["area"] - cand["area"]) / (AREA_TOL * cand["area"])
    dp = abs(brief["aspect"] - cand["aspect"]) / (ASPECT_TOL * cand["aspect"])
    return round(da, 4), round(dp, 4)


def warp_candidates(brief, cands, tlim, hold_ring):
    rows = []
    for cand in cands:
        ct = [COLLAPSE.get(t, t) for t in cand["types"]]
        targets = pair_targets(ct, cand["parts"], brief["rooms"])
        da, dp = term_distances(brief, cand)
        if targets is None:
            rows.append({"status": "NOPAIR", "served": False,
                         "d_area": da, "d_aspect": dp})
            continue
        targets = [max(a, MARKET.get(t, 0.0)) for a, t in zip(targets, ct)]
        t0 = time.perf_counter()
        r = run_one(cand, brief["aspect"], targets, tlim,
                    key=brief["k"] + cand["k"], hold_ring=hold_ring)
        dt = time.perf_counter() - t0
        row = {"status": r["status"], "served": False, "secs": round(dt, 3),
               "d_area": da, "d_aspect": dp, "donor": cand["k"]}
        if r["status"] == "OK":
            floors = floors_for(r["types"])
            margin = [g - fl for g, fl in zip(r["got"], floors) if fl is not None]
            row["served"] = all(m >= 0 for m in margin)
            row["worst_margin_m2"] = round(min(margin), 4) if margin else None
            # the fidelity quantity 2.2.7 publishes: worst-room area deviation
            dev = [abs(g - t) / t for g, t in zip(r["got"], r["targets"]) if t > 0]
            row["worst_room_dev"] = round(max(dev), 4) if dev else None
            row["space_m2_total"] = r["space_m2_total"]
        rows.append(row)
    return rows


def arm_stats(briefs, arm):
    rows = [o for b in briefs for o in b[arm]]
    warped = [o for o in rows if o["status"] == "OK"]
    dev = [o["worst_room_dev"] for o in warped if o.get("worst_room_dev") is not None]
    declined = sum(1 for o in rows if not o["served"])
    return {
        "candidates": len(rows),
        "warp_failed": sum(1 for o in rows if o["status"] != "OK"),
        "declined": declined,
        "decline_rate": round(declined / max(1, len(rows)), 4),
        "decline_rate_of_warped": round(
            sum(1 for o in warped if not o["served"]) / max(1, len(warped)), 4),
        "briefs_served": sum(1 for b in briefs if any(o["served"] for o in b[arm])),
        "worst_room_dev_p50": round(pct(dev, 0.50), 4) if dev else None,
        "worst_room_dev_p90": round(pct(dev, 0.90), 4) if dev else None,
        "secs_per_warp": round(
            sum(o.get("secs", 0.0) for o in rows) / max(1, len(warped)), 3),
    }


def exact_two_sided(a, b):
    n = a + b
    if n == 0:
        return 1.0
    k = min(a, b)
    tail = sum(comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def mcnemar(briefs, key="served"):
    """Brief-level: served by at least one of K admitted vs one of K refused."""
    a_only = r_only = both = neither = 0
    for b in briefs:
        a = any(o[key] for o in b["admitted"])
        r = any(o[key] for o in b["refused"])
        if a and r:
            both += 1
        elif a:
            a_only += 1
        elif r:
            r_only += 1
        else:
            neither += 1
    return {"admitted_only": a_only, "refused_only": r_only, "both": both,
            "neither": neither, "p_exact": round(exact_two_sided(a_only, r_only), 5)}


def paired_candidate_test(briefs):
    """The per-candidate arms are not independent samples -- they share a Brief.
    Sign test on the per-Brief difference in declines, K against K."""
    plus = minus = tie = 0
    for b in briefs:
        da = sum(1 for o in b["admitted"] if not o["served"])
        dr = sum(1 for o in b["refused"] if not o["served"])
        if dr > da:
            plus += 1          # refused arm declines more -- the gate helps
        elif da > dr:
            minus += 1
        else:
            tie += 1
    return {"refused_worse": plus, "admitted_worse": minus, "tied": tie,
            "p_exact": round(exact_two_sided(plus, minus), 5)}


def by_distance(briefs):
    """Decline rate against how far outside the tolerance the donor sits.
    Each term alone, so an inert term shows as a flat column."""
    rows = [o for b in briefs for arm in ("admitted", "refused") for o in b[arm]]

    def band(v):
        for hi, lab in ((1.0, "<=1 (admitted)"), (2.0, "1-2"), (4.0, "2-4")):
            if v <= hi:
                return lab
        return ">4"

    out = {}
    for key in ("d_area", "d_aspect"):
        acc = defaultdict(lambda: [0, 0])
        for o in rows:
            bd = band(o[key])
            acc[bd][1] += 1
            acc[bd][0] += (not o["served"])
        out[key] = {bd: {"candidates": v[1], "declined": v[0],
                         "decline_rate": round(v[0] / v[1], 4)}
                    for bd, v in acc.items()}
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n_arg = int(args[0]) if args else 200
    tlim, K, hold_ring = 3.0, 3, True
    for a in sys.argv[1:]:
        if a.startswith("--time="):
            tlim = float(a.split("=", 1)[1])
        if a.startswith("--k="):
            K = int(a.split("=", 1)[1])
        if a == "--no-ring":
            hold_ring = False

    cands, by_ms, by_n = load()
    print("converted dwellings joined to the room cache: %s" % format(len(cands), ","))
    rng = random.Random(SEED)
    sample = rng.sample(cands, min(n_arg, len(cands)))
    print("sample %d Briefs | K %d per stratum | time %.1fs | hold_ring %s\n"
          % (len(sample), K, tlim, hold_ring))

    briefs, dropped = [], defaultdict(int)
    t_start = time.perf_counter()
    for i, brief in enumerate(sample):
        bucket, admitted, refused = strata(brief, by_ms)
        if len(admitted) < K or len(refused) < K:
            dropped["thin_admitted" if len(admitted) < K else "thin_refused"] += 1
            continue
        # zlib.crc32, not hash(): PYTHONHASHSEED randomises str hashing per
        # process, so this draw was a DIFFERENT sample on every run and the
        # README's "seed 20260819 throughout" never held for it. Same fix, and
        # the same reason, as `experiments/solver-toy/probe6.py`. Ticket 65.
        # The pre-fix `out/gate_effect_briefs.json` is therefore one
        # unreproducible draw, and ADR 0032 rests on it.
        prng = random.Random(SEED ^ zlib.crc32(brief["k"].encode()))
        a_draw = prng.sample(admitted, K)
        r_draw = prng.sample(refused, K)
        rec = {"k": brief["k"], "n": brief["n"],
               "bucket": len(bucket), "n_admitted": len(admitted),
               "n_refused": len(refused),
               "admitted": warp_candidates(brief, a_draw, tlim, hold_ring),
               "refused": warp_candidates(brief, r_draw, tlim, hold_ring)}
        briefs.append(rec)
        if len(briefs) % 10 == 0:
            el = time.perf_counter() - t_start
            print("  %d paired Briefs (%d/%d scanned), %.0fs elapsed"
                  % (len(briefs), i + 1, len(sample), el))

    print("\npaired Briefs: %d of %d sampled" % (len(briefs), len(sample)))
    print("dropped: %s" % dict(dropped))
    if not briefs:
        return

    out = {"_meta": {"n_requested": n_arg, "K": K, "time_limit_s": tlim,
                     "hold_ring": hold_ring, "seed": SEED,
                     "paired_briefs": len(briefs), "dropped": dict(dropped)},
           "admitted": arm_stats(briefs, "admitted"),
           "refused": arm_stats(briefs, "refused"),
           "mcnemar_brief_level": mcnemar(briefs),
           "sign_test_per_brief_declines": paired_candidate_test(briefs),
           "decline_by_term_distance": by_distance(briefs)}

    print("\n--- per-candidate, paired within Brief ---")
    print("%-12s%11s%11s%14s%12s%12s" % ("arm", "cands", "declined", "rate",
                                         "dev p50", "dev p90"))
    for arm in ("admitted", "refused"):
        s = out[arm]
        print("%-12s%11d%11d%13.1f%%%12s%12s"
              % (arm, s["candidates"], s["declined"], 100 * s["decline_rate"],
                 s["worst_room_dev_p50"], s["worst_room_dev_p90"]))

    m = out["mcnemar_brief_level"]
    print("\n--- Brief-level, best of K ---")
    print("admitted only %d | refused only %d | both %d | neither %d | "
          "exact p %.4f" % (m["admitted_only"], m["refused_only"], m["both"],
                            m["neither"], m["p_exact"]))
    s = out["sign_test_per_brief_declines"]
    print("sign test on per-Brief decline counts: refused worse %d, "
          "admitted worse %d, tied %d, exact p %.4f"
          % (s["refused_worse"], s["admitted_worse"], s["tied"], s["p_exact"]))

    print("\n--- decline against distance outside each term ---")
    for key in ("d_area", "d_aspect"):
        print(" %s" % key)
        for bd in ("<=1 (admitted)", "1-2", "2-4", ">4"):
            v = out["decline_by_term_distance"][key].get(bd)
            if v:
                print("   %-16s%7d cands%9.1f%%"
                      % (bd, v["candidates"], 100 * v["decline_rate"]))

    OUT.mkdir(exist_ok=True)
    json.dump(briefs, open(OUT / "gate_effect_briefs.json", "w"))
    json.dump(out, open(OUT / "gate_effect.json", "w"), indent=1)
    print("\nwrote %s" % (OUT / "gate_effect.json"))


if __name__ == "__main__":
    main()
