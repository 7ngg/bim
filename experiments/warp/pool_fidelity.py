"""Best-of-pool: what a Brief actually gets, not what one candidate gets.

Ticket 23, items 3 and 5. `fit_warp.py` measures one (source, Envelope) pair.
Retrieval does not ship one pair -- it ships a **pool**, and C6 takes many
candidates and rejects most. Two things only a pool can answer:

  * the warp declines 22 % of candidates on the ergonomic floor or
    `dim.aspect_ratio_hard`. Is that a Brief-level coverage loss, or does the
    next pool member absorb it?
  * ranking on the affine warp was useless -- `gate_curve.py` arm B -- because
    no pool member was well proportioned. Once every member is *fitted*, what
    does taking the best of m buy?

Run: python experiments/warp/pool_fidelity.py [briefs] [--take=8] [--time=2.0]
"""

from __future__ import annotations

import json
import random
import statistics as st
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import fit_warp as F

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"


def main():
    nb = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 120
    take = 8
    tlim = 2.0
    for a in sys.argv[1:]:
        if a.startswith("--take="):
            take = int(a.split("=")[1])
        if a.startswith("--time="):
            tlim = float(a.split("=")[1])

    fits = {r["k"]: r for r in json.load(open(F.FIT))
            if r["status"] in ("OPTIMAL", "FEASIBLE")}
    recs = {r["k"]: r for r in json.load(open(F.ROOMS))}
    for r in recs.values():
        r["ms"] = tuple(sorted(Counter(F.COLLAPSE.get(t, t)
                                       for t, _ in r["rooms"]).items()))
    by_ms = defaultdict(list)
    for r in recs.values():
        by_ms[r["ms"]].append(r)
    # only dwellings that CONVERTED can be warped -- they are the index
    conv = [recs[k] for k in fits if k in recs]
    conv_ms = defaultdict(list)
    for r in conv:
        conv_ms[r["ms"]].append(r)
    print(f"index: {len(conv):,} converted dwellings over "
          f"{len(conv_ms):,} multisets")

    rng = random.Random(F.SEED)
    briefs = rng.sample(conv, min(nb, len(conv)))

    best_dev, pool_used, declines, served = [], [], 0, 0
    attempted = 0
    first_dev = []
    t_all = time.perf_counter()
    for src in briefs:
        # Envelope from a gate-admitted peer, as cross_coverage.py pairs them
        adm = [p for p in by_ms[src["ms"]]
               if p["k"] != src["k"]
               and abs(src["area"] - p["area"]) <= F.AREA_TOL * p["area"]
               and abs(src["aspect"] - p["aspect"]) <= F.ASPECT_TOL * p["aspect"]]
        if not adm:
            continue
        d = rng.choice(adm)
        # the pool retrieval would offer for that Brief: converted dwellings
        # sharing the multiset and inside the gate against this Envelope
        pool = [p for p in conv_ms[src["ms"]]
                if abs(p["area"] - d["area"]) <= F.AREA_TOL * d["area"]
                and abs(p["aspect"] - d["aspect"]) <= F.ASPECT_TOL * d["aspect"]]
        if not pool:
            continue
        rng.shuffle(pool)
        pool = pool[:take]

        devs = []
        for p in pool:
            attempted += 1
            r = F.warp_one(fits[p["k"]], src, d, tlim)
            if r is None:
                declines += 1
                continue
            devs.append(r)
        pool_used.append(len(pool))
        if devs:
            served += 1
            best_dev.append(min(devs))
            first_dev.append(devs[0])

    def pct(v, q):
        v = sorted(v)
        return v[min(len(v) - 1, int(q * len(v)))]

    print(f"briefs with a non-empty converted pool: {len(pool_used)}")
    print(f"pool offered (capped at {take}): median {st.median(pool_used):.0f}, "
          f"max {max(pool_used)}")
    print(f"candidates warped: {attempted:,}   declined: {declines:,} "
          f"({100*declines/max(attempted,1):.1f}%)")
    print(f"briefs served (>=1 candidate survived the warp): "
          f"{served}/{len(pool_used)} = {100*served/max(len(pool_used),1):.1f}%")
    print(f"\nworst-room deviation")
    print(f"  one candidate      p50 {st.median(first_dev):.3f}  "
          f"p90 {pct(first_dev,0.9):.3f}  p99 {pct(first_dev,0.99):.3f}")
    print(f"  best of the pool   p50 {st.median(best_dev):.3f}  "
          f"p90 {pct(best_dev,0.9):.3f}  p99 {pct(best_dev,0.99):.3f}")
    print(f"\nwall clock {time.perf_counter()-t_all:.0f} s")

    OUT.mkdir(exist_ok=True)
    json.dump({"briefs": len(pool_used), "take": take,
               "declined_pct": round(100 * declines / max(attempted, 1), 2),
               "served_pct": round(100 * served / max(len(pool_used), 1), 2),
               "one_p50": st.median(first_dev), "one_p90": pct(first_dev, 0.9),
               "best_p50": st.median(best_dev), "best_p90": pct(best_dev, 0.9),
               "best_p99": pct(best_dev, 0.99)},
              open(OUT / "pool_fidelity.json", "w"), indent=1)
    print(f"wrote {OUT/'pool_fidelity.json'}")


if __name__ == "__main__":
    main()
