"""What best-of-pool is worth as the pool deepens.

Ticket 57. `acceptance-bar.md` §11.1 keeps `dim.statutory_min_area` hard on a
measured **3,6 % of Briefs with no clearing candidate**, and step 1 of its own
escalation is *deepen the pool*. That figure is `absolute_area.py`'s `ringpool`
arm at `--pool=8`: one point, no curve, and a mechanism with no number attached.

**The curve costs almost nothing more than the point, and that is the trick.**
`served_at_m` is a prefix-any over a fixed draw order -- if candidate 3 serves,
every m >= 3 serves -- so the whole curve is determined by the **index of the
first serving candidate**, and the early break in `run_pool` is still sound.
Going from m = 8 to m = 64 costs extra warps only on the Briefs that were
starving at 8, which is the ~6 % `run_pool` already found. The curve is
**nested**, so every point is paired against every other by construction and no
two points differ by a re-draw.

Two pool definitions, because they are not the same pool and §2.2.7's second
limit is stated about one of them:

  `rig`    -- `absolute_area.bucket_pool` -- what `gate_pool` returned before ticket 60
              the WHOLE multiset bucket and applies the area and aspect terms
              only in the by-room-count fallback.
  `gated`  -- §2.2.1 as written: *"the gate's first term is an exact match, so
              the bucket is the pool and the other two terms are a scan of it"*.

`pool_depth.py` measures the two at p50 50 and p50 7 over the same sample, so
which one `--pool=8` was drawn from decides whether 8 is a tenth of production
depth or most of it.

Run: python experiments/warp/best_of_m.py [n] [--m=32] [--time=3.0]
                                          [--pools=rig,gated] [--no-ring]
"""

from __future__ import annotations

import json
import random
import sys
import time
import zlib
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fit_warp import COLLAPSE, SEED, AREA_TOL, ASPECT_TOL          # noqa: E402
from absolute_area import (FIT, ROOMS, OUT, MARKET, bucket_pool,   # noqa: E402
                           admissible_pool,
                           pair_targets, run_one, floors_for, pct)

BANDS = {"4-6": range(4, 7), "7-10": range(7, 11)}
PROD_MEDIAN = {"4-6": 86.6, "7-10": 58.7}
CURVE_M = (1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64)


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


# Ticket 60: one definition of the gate, in `absolute_area`, imported
# everywhere. Four scripts each carried their own copy and three of them
# differed from 2.2.1 -- that duplication IS the defect this ticket found.
gated_pool = admissible_pool


def walk_pool(brief, order, tlim, hold_ring, max_m):
    """Warp candidates in draw order until one SERVES. Returns the per-candidate
    outcome list; its length is the number of warps actually spent.

    A candidate that fails to warp at all (INFEASIBLE, NOTCH, DEGENERATE) or that
    cannot be paired is a **decline that consumes a pool slot** -- ADR 0005 falls
    the Brief to the next member either way. `run_pool` counts those separately
    and excludes a Brief whose every candidate failed to warp; both conventions
    are reported rather than one being chosen here."""
    outcomes = []
    for cand in order[:max_m]:
        ct = [COLLAPSE.get(t, t) for t in cand["types"]]
        targets = pair_targets(ct, cand["parts"], brief["rooms"])
        if targets is None:
            outcomes.append({"status": "NOPAIR", "served": False})
            continue
        targets = [max(a, MARKET.get(t, 0.0)) for a, t in zip(targets, ct)]
        t0 = time.perf_counter()
        r = run_one(cand, brief["aspect"], targets, tlim,
                    key=brief["k"] + cand["k"], hold_ring=hold_ring)
        dt = time.perf_counter() - t0
        if r["status"] != "OK":
            outcomes.append({"status": r["status"], "served": False,
                             "secs": round(dt, 3)})
            continue
        floors = floors_for(r["types"])
        margin = [g - fl for g, fl in zip(r["got"], floors) if fl is not None]
        ok = all(m >= 0 for m in margin)
        outcomes.append({"status": "OK", "served": ok, "secs": round(dt, 3),
                         "worst_margin_m2": round(min(margin), 4) if margin else None,
                         "void_m2": r["void_m2"], "notch_m2": r["notch_m2"],
                         "space_m2_total": r["space_m2_total"],
                         "target_area": round(r["target_area"], 3),
                         "cov_over_int": round(r["cov_over_int"], 4)})
        if ok:
            break
    return outcomes


def summarise_pool(briefs, max_m, warps, secs):
    live = [b for b in briefs if not b["empty_pool"]]
    # `run_pool`'s convention: a Brief whose every evaluated candidate failed to
    # WARP is "no usable candidate", not a starvation.
    usable = [b for b in live if any(o["status"] == "OK" for o in b["outcomes"])]
    res = {"briefs_sampled": len(briefs),
           "briefs_with_empty_pool": sum(1 for b in briefs if b["empty_pool"]),
           "briefs_with_a_pool": len(live),
           "briefs_with_a_usable_candidate": len(usable),
           "warps_spent": warps, "in_warp_seconds": round(secs, 1),
           "seconds_per_warp": round(secs / max(1, warps), 3)}

    def curve(rowset, label):
        c = {}
        for m in CURVE_M:
            if m > max_m:
                continue
            n = len(rowset)
            starved = sum(1 for b in rowset
                          if not (b["first_serve"] is not None
                                  and b["first_serve"] < m))
            c[m] = {"briefs": n, "starved": starved,
                    "starved_share": round(starved / max(1, n), 4)}
        res[label] = c

    curve(live, "curve_strict")          # every Brief with a pool
    curve(usable, "curve_run_pool_convention")

    # Conditional decline: P(candidate j+1 does not serve | j prior declines).
    # Under independence this is FLAT in j. Rising means declines are correlated
    # within a pool, which is ADR 0018 consequence 3. A direct test: it needs no
    # independence prediction to compare against.
    cond = {}
    for j in range(0, min(max_m, 16)):
        at_risk = [b for b in live if len(b["outcomes"]) > j]
        if len(at_risk) < 8:
            break
        dec = sum(1 for b in at_risk if not b["outcomes"][j]["served"])
        cond[j + 1] = {"at_risk": len(at_risk), "declined": dec,
                       "decline_rate": round(dec / len(at_risk), 4)}
    res["conditional_decline_by_position"] = cond

    # depth actually available, and how often the curve is truncated by it
    depths = [b["depth"] for b in live]
    res["pool_depth"] = {"p25": pct(depths, .25), "p50": pct(depths, .50),
                         "p75": pct(depths, .75), "max": max(depths, default=0)}
    res["truncated_at_m"] = {
        m: sum(1 for b in live if b["depth"] < m and b["first_serve"] is None)
        for m in CURVE_M if m <= max_m}

    bands = {}
    for name, rr in BANDS.items():
        sel = [b for b in live if b["n"] in rr]
        if not sel:
            continue
        bands[name] = {m: round(sum(1 for b in sel
                                    if not (b["first_serve"] is not None
                                            and b["first_serve"] < m))
                                / len(sel), 4)
                       for m in CURVE_M if m <= max_m}
        bands[name]["briefs"] = len(sel)
        bands[name]["prod_median_pool"] = PROD_MEDIAN[name]
    res["curve_by_band"] = bands
    return res


def show(r):
    d = r["pool_depth"]
    print("pool depth p25/p50/p75/max: %.0f/%.0f/%.0f/%.0f | empty pools %d | "
          "%.2fs per warp" % (d["p25"], d["p50"], d["p75"], d["max"],
                              r["briefs_with_empty_pool"], r["seconds_per_warp"]))
    print()
    print("   m  briefs  starved    share     4-6    7-10  trunc")
    for m, v in r["curve_strict"].items():
        b46 = r["curve_by_band"].get("4-6", {}).get(m)
        b710 = r["curve_by_band"].get("7-10", {}).get(m)
        print("%4s%8d%9d%8.1f%%%8s%8s%7d"
              % (m, v["briefs"], v["starved"], 100 * v["starved_share"],
                 ("%.1f%%" % (100 * b46)) if b46 is not None else "-",
                 ("%.1f%%" % (100 * b710)) if b710 is not None else "-",
                 r["truncated_at_m"][m]))
    print()
    print(" position  at risk  declined    rate   (flat = independent, "
          "rising = correlated)")
    for j, v in r["conditional_decline_by_position"].items():
        print("%9s%9d%10d%7.1f%%"
              % (j, v["at_risk"], v["declined"], 100 * v["decline_rate"]))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n_arg = int(args[0]) if args else 200
    tlim, max_m, hold_ring = 3.0, 32, True
    pools = ["rig", "gated"]
    for a in sys.argv[1:]:
        if a.startswith("--time="):
            tlim = float(a.split("=", 1)[1])
        if a.startswith("--m="):
            max_m = int(a.split("=", 1)[1])
        if a.startswith("--pools="):
            pools = a.split("=", 1)[1].split(",")
        if a == "--no-ring":
            hold_ring = False

    cands, by_ms, by_n = load()
    print("converted dwellings joined to the room cache: "
          + format(len(cands), ","))
    rng = random.Random(SEED)
    sample = rng.sample(cands, min(n_arg, len(cands)))
    print("sample %d Briefs | max m %d | time %.1fs | hold_ring %s | pools %s\n"
          % (len(sample), max_m, tlim, hold_ring, ",".join(pools)))

    out = {}
    for pname in pools:
        if pname == "rig":
            def pick(b):
                return bucket_pool(b, by_ms, by_n)
        else:
            def pick(b):
                return gated_pool(b, by_ms)
        briefs, warps, secs = [], 0, 0.0
        t_start = time.perf_counter()
        for i, brief in enumerate(sample):
            pool = pick(brief)
            if not pool:
                briefs.append({"k": brief["k"], "n": brief["n"], "depth": 0,
                               "first_serve": None, "outcomes": [],
                               "empty_pool": True})
                continue
            # A full permutation, seeded per Brief: its first m is a valid uniform
            # draw of size m for EVERY m, which is what makes the curve nested
            # rather than a series of independent draws.
            prng = random.Random(SEED ^ (zlib.crc32(brief["k"].encode()) & 0xFFFFFFFF))
            order = prng.sample(pool, len(pool))
            oc = walk_pool(brief, order, tlim, hold_ring, max_m)
            fs = next((j for j, o in enumerate(oc) if o["served"]), None)
            warps += len(oc)
            secs += sum(o.get("secs", 0.0) for o in oc)
            briefs.append({"k": brief["k"], "n": brief["n"], "depth": len(pool),
                           "first_serve": fs, "outcomes": oc,
                           "empty_pool": False, "warps_spent": len(oc)})
            if (i + 1) % 25 == 0:
                el = time.perf_counter() - t_start
                print("  [%s] %d/%d briefs, %d warps, %.0fs elapsed, "
                      "%.2fs/brief" % (pname, i + 1, len(sample), warps, el,
                                       el / (i + 1)))
        OUT.mkdir(exist_ok=True)
        json.dump(briefs, open(OUT / ("best_of_m_briefs_%s.json" % pname), "w"))
        out[pname] = summarise_pool(briefs, max_m, warps, secs)
        print("\n=== pool %s: %d warps, %.0fs in-warp ===" % (pname, warps, secs))
        show(out[pname])

    out["_meta"] = {"n_requested": n_arg, "max_m": max_m, "time_limit_s": tlim,
                    "hold_ring": hold_ring, "seed": SEED,
                    "targets": "market (dim.market_default_area), as ringpool"}
    json.dump(out, open(OUT / "best_of_m.json", "w"), indent=1)
    print("\nwrote %s" % (OUT / "best_of_m.json"))


if __name__ == "__main__":
    main()
