"""Coverage versus fidelity, in the coordinate the gate is missing.

Ticket 23, item 5. `room_area_spread.py` shows the shipped gate -- exact room
multiset, total area +-10 %, envelope aspect +-15 % -- leaves per-room area
unconstrained, and that an affine warp therefore misses a Brief's per-room
targets by a median 21 % and by more than 30 % on the worst room of the median
admitted candidate.

This prices the two ways out, on the same cross-paired Briefs, same seed:

  A. a **fourth gate term**: every room's warped area within +-t of its target.
     Costs coverage; buys fidelity outright.
  B. **rank on it instead of gating**: keep the three-term gate, order the pool
     by worst-room area ratio, and take the best m. Costs no coverage at all
     while a pool is non-empty; buys whatever the pool's best member happens to
     carry.

Reported for each: share of Briefs with a non-empty pool, median pool size, and
the fidelity of what survives.

    python experiments/warp/gate_curve.py
"""

from __future__ import annotations

import json
import random
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parent / "out"
CACHE = OUT / "dwelling_rooms.json"
AREA_TOL, ASPECT_TOL, SEED = 0.10, 0.15, 20260819

K = {"PRIVATE": 2.18, "BATHROOM": 2.23, "WC": 3.36, "KITCHEN": 2.56,
     "LIVING_DINING": 2.02, "LIVING_ROOM": 2.35, "CORRIDOR": 3.28,
     "DINING": 3.67, "STOREROOM": 8.15}
K_DEFAULT = 2.5
TOLS = [None, 0.60, 0.50, 0.40, 0.30, 0.25, 0.20, 0.15, 0.10]
TAKE = 8            # candidates a job actually solves, for arm B


def ms_of(rec):
    return tuple(sorted(Counter(t for t, _ in rec["rooms"]).items()))


def pair_by_type(target_rooms, pool_rooms):
    a, b = defaultdict(list), defaultdict(list)
    for t, ar in target_rooms:
        a[t].append(ar)
    for t, ar in pool_rooms:
        b[t].append(ar)
    for t in a:
        for tgt, src in zip(sorted(a[t], reverse=True), sorted(b[t], reverse=True)):
            yield t, tgt, src


def ratios_of(r, p, env_area):
    s = env_area / p["area"]
    return [(t, (src * s) / tgt) for t, tgt, src in pair_by_type(r["rooms"], p["rooms"])]


def worst_dev(rs):
    return max(abs(x - 1) for _, x in rs)


def breaches_max_area(rs):
    return any(x > K.get(t, K_DEFAULT) for t, x in rs)


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else float("nan")


def main():
    recs = json.load(open(CACHE))
    for r in recs:
        r["ms"] = ms_of(r)
    by_ms, by_n = defaultdict(list), defaultdict(list)
    for r in recs:
        by_ms[r["ms"]].append(r)
        by_n[r["n"]].append(r)
    print(f"dwellings: {len(recs):,}\n")

    bands = {"4-6": range(4, 7), "7-10": range(7, 11)}
    MAXPOOL = 40
    result = {}

    for band, rr in bands.items():
        rng = random.Random(SEED)
        sel = [r for r in recs if r["n"] in rr]
        # one pass: build each Brief's raw pool with its per-room ratios
        briefs = []
        for r in sel:
            d = rng.choice(by_n[r["n"]])
            pool = [p for p in by_ms[r["ms"]]
                    if p["k"] != r["k"]
                    and abs(p["area"] - d["area"]) <= AREA_TOL * d["area"]
                    and abs(p["aspect"] - d["aspect"]) <= ASPECT_TOL * d["aspect"]]
            if len(pool) > MAXPOOL:
                pool = rng.sample(pool, MAXPOOL)
            scored = [(worst_dev(rs), breaches_max_area(rs), rs)
                      for rs in (ratios_of(r, p, d["area"]) for p in pool)]
            briefs.append(scored)
        nb = len(briefs)

        print("=" * 78)
        print(f"band {band}  --  {nb:,} Briefs, pool capped at {MAXPOOL}")
        print("=" * 78)
        print("\nARM A: per-room area as a FOURTH GATE TERM")
        print(f"{'tol':>6} {'pool>0':>9} {'blank':>8} {'median':>8} {'worst-room dev':>16}"
              f" {'max_area breach':>16}")
        rows_a = {}
        for tol in TOLS:
            sizes, devs, breach = [], [], 0
            kept_total = 0
            for scored in briefs:
                keep = [s for s in scored if tol is None or s[0] <= tol]
                sizes.append(len(keep))
                for wd, br, _ in keep:
                    devs.append(wd)
                    breach += br
                kept_total += len(keep)
            nz = sum(1 for s in sizes if s > 0)
            label = "none" if tol is None else f"{tol:.2f}"
            bp = 100 * breach / kept_total if kept_total else 0.0
            print(f"{label:>6} {100*nz/nb:>8.1f}% {100*(nb-nz)/nb:>7.1f}%"
                  f" {pct(sizes,0.5):>8} {st.median(devs) if devs else float('nan'):>16.3f}"
                  f" {bp:>15.1f}%")
            rows_a[label] = {"coverage_pct": round(100 * nz / nb, 2),
                             "median_pool": pct(sizes, 0.5),
                             "worst_room_dev_p50": round(st.median(devs), 4) if devs else None,
                             "max_area_breach_pct": round(bp, 2)}

        print(f"\nARM B: three-term gate, pool ORDERED by worst-room ratio, top {TAKE}")
        sizes = [len(s) for s in briefs]
        nz = sum(1 for s in sizes if s > 0)
        best_devs, topk_devs, breach_top, top_total = [], [], 0, 0
        for scored in briefs:
            if not scored:
                continue
            ordered = sorted(scored, key=lambda s: s[0])
            best_devs.append(ordered[0][0])
            for wd, br, _ in ordered[:TAKE]:
                topk_devs.append(wd)
                breach_top += br
                top_total += 1
        print(f"  coverage {100*nz/nb:.1f}%   (unchanged -- ranking never empties a pool)")
        print(f"  best candidate's worst-room dev: p50 {st.median(best_devs):.3f}"
              f"  p90 {pct(best_devs,0.90):.3f}  p99 {pct(best_devs,0.99):.3f}")
        print(f"  top-{TAKE} worst-room dev:            p50 {st.median(topk_devs):.3f}"
              f"  p90 {pct(topk_devs,0.90):.3f}")
        print(f"  top-{TAKE} breaching dim.max_area:    {100*breach_top/top_total:.1f}%")
        print(f"  share of Briefs whose BEST candidate is still worse than 0.30:"
              f" {100*sum(1 for x in best_devs if x > 0.30)/len(best_devs):.1f}%")

        result[band] = {"briefs": nb, "arm_a": rows_a,
                        "arm_b": {"coverage_pct": round(100 * nz / nb, 2),
                                  "best_dev_p50": round(st.median(best_devs), 4),
                                  "best_dev_p90": round(pct(best_devs, 0.90), 4),
                                  "best_worse_than_030_pct":
                                      round(100 * sum(1 for x in best_devs if x > 0.30)
                                            / len(best_devs), 2),
                                  "topk_breach_pct": round(100 * breach_top / top_total, 2)}}
        print()

    json.dump(result, open(OUT / "gate_curve.json", "w"), indent=1)
    print(f"wrote {OUT/'gate_curve.json'}")


if __name__ == "__main__":
    main()
