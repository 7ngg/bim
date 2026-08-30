"""The floor on an AGGREGATE, which is the only floor a published figure has.

Ticket 82, and it is this script rather than `repro_floor.py` that decides
whether any published claim moves.

`repro_floor.py` measures a PER-PAIR disagreement rate: re-solve one
`(brief, donor)` pair and ask whether the answer changed. It came back at 36 %
on `dev` and 4 % on `served`. **Neither number is the floor under a published
figure**, because nothing on this map is published per pair. What is published is
a served RATE over a few hundred Briefs and a `dev` PERCENTILE over the same --
and an aggregate over `n` pairs is far more stable than its members, by exactly
the averaging that makes a mean tighter than a draw.

Quoting the per-pair rate as though it were the floor under ADR 0032's
**1,3-point** served margin is the error this script exists to prevent. It would
say a 1,3-point difference is drowned by a 4-point floor. That comparison is
between two different quantities and it is meaningless.

So: hold the stopping rule DETERMINISTIC -- `max_deterministic_time`, which
`repro_floor.py` measured at exactly 0,00 % disagreement -- and vary only the
objective-weight draw, `k` times over the SAME set of pairs. Each draw yields one
complete published-shape statistic. The spread of that statistic across the `k`
draws is the floor a published figure actually sits on.

Reported for each: served rate, dev p50, dev p90. Those are the three quantities
`gate_depth.summarise` publishes and ADR 0032 is decided on.

⚠️ This measures the salt's contribution ONLY. The wall clock adds nothing at
15 s (`repro_floor.py`: 0 of 69 solves reach the cap) and 4 points per pair at
3 s, and it is held out here deliberately so the aggregate spread is attributable.

Run: python -u experiments/warp/agg_floor.py [n_pairs] [--k=5] [--dtime=6.0]

Resumable: appends to `out/agg_floor_solves.jsonl`, keyed by (pair, draw).
"""

from __future__ import annotations

import json
import os
import sys
import random
import time
import zlib
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fit_warp import SEED                                            # noqa: E402
from absolute_area import OUT                                        # noqa: E402
from best_of_m import load                                           # noqa: E402
from repro_floor import CACHE, one_solve                             # noqa: E402


def pctile(xs, q):
    if not xs:
        return None
    xs = sorted(xs)
    i = min(len(xs) - 1, int(q * len(xs)))
    return xs[i]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n_pairs = int(args[0]) if args else 120
    k, dtime = 5, 6.0
    for a in sys.argv[1:]:
        if a.startswith("--k="):
            k = int(a.split("=", 1)[1])
        if a.startswith("--dtime="):
            dtime = float(a.split("=", 1)[1])
    OUT.mkdir(exist_ok=True)
    solves_p = OUT / "agg_floor_solves.jsonl"

    seen = set()
    with open(CACHE) as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                seen.add((r["brief"], r["donor"]))
    cands, _bm, _bn = load()
    by_k = {c["k"]: c for c in cands}
    pool = sorted(p for p in seen if p[0] in by_k and p[1] in by_k)
    sample = random.Random(SEED + 1).sample(pool, min(n_pairs, len(pool)))
    print("pairs %d | draws %d | deterministic cap %.1f\n"
          % (len(sample), k, dtime), flush=True)

    done = set()
    if solves_p.exists():
        with open(solves_p) as fh:
            for line in fh:
                if line.strip():
                    r = json.loads(line)
                    done.add((r["bk"], r["dk"], r["draw"]))

    t0 = time.time()
    with open(solves_p, "a") as out:
        for i, (bk, dk) in enumerate(sample, 1):
            for draw in range(k):
                if (bk, dk, draw) in done:
                    continue
                # draw 0 is the SHIPPED draw after ticket 82's fix -- crc32 of
                # the key, the value `run_one` now uses by default. Draws 1..k-1
                # are what a different process used to hand you.
                base = zlib.crc32((bk + dk).encode())
                wseed = base if draw == 0 else base ^ (draw * 0x9E3779B1)
                row = one_solve(by_k[bk], by_k[dk], 3.0, dtime, wseed)
                row.update(bk=bk, dk=dk, draw=draw)
                out.write(json.dumps(row) + "\n")
                out.flush()
                os.fsync(out.fileno())
            if i % 20 == 0 or i == len(sample):
                print("  %3d/%d pairs  %5.1f min"
                      % (i, len(sample), (time.time() - t0) / 60), flush=True)

    per_draw = defaultdict(list)
    with open(solves_p) as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                per_draw[r["draw"]].append(r)

    print("\n" + "=" * 72)
    print("ONE PUBLISHED-SHAPE STATISTIC PER OBJECTIVE-WEIGHT DRAW")
    print("=" * 72)
    print("%-8s %8s %12s %10s %10s" % ("draw", "pairs", "served", "dev p50",
                                       "dev p90"))
    stats = {}
    for d in sorted(per_draw):
        rows = per_draw[d]
        ok = [r for r in rows if r["status"] == "OK"]
        served = sum(1 for r in ok if r["served"]) / len(rows) if rows else 0
        devs = [r["dev"] for r in ok if r["dev"] is not None]
        stats[d] = (served, pctile(devs, 0.50), pctile(devs, 0.90))
        print("%-8s %8d %11.2f%% %10.4f %10.4f"
              % (("%d (shipped)" % d) if d == 0 else d, len(rows),
                 100 * served, stats[d][1] or 0, stats[d][2] or 0))

    print("\n" + "=" * 72)
    print("THE FLOOR UNDER A PUBLISHED FIGURE -- spread across the draws")
    print("=" * 72)
    names = ("served rate", "dev p50", "dev p90")
    floors = {}
    for j, nm in enumerate(names):
        vs = [s[j] for s in stats.values() if s[j] is not None]
        if len(vs) < 2:
            continue
        rng_ = max(vs) - min(vs)
        mean = sum(vs) / len(vs)
        sd = (sum((v - mean) ** 2 for v in vs) / (len(vs) - 1)) ** 0.5
        floors[nm] = {"min": min(vs), "max": max(vs), "range": rng_,
                      "mean": mean, "sd": sd}
        if j == 0:
            print("%-12s  min %6.2f%%  max %6.2f%%  RANGE %5.2f pts  sd %5.2f pts"
                  % (nm, 100 * min(vs), 100 * max(vs), 100 * rng_, 100 * sd))
        else:
            print("%-12s  min %6.4f  max %6.4f  RANGE %6.4f  sd %6.4f"
                  % (nm, min(vs), max(vs), rng_, sd))

    sv = floors.get("served rate")
    if sv:
        print("\nADR 0032's margin is 1,3 points of served. The aggregate floor "
              "measured here is %.2f points (range) / %.2f points (sd) at n = %d."
              % (100 * sv["range"], 100 * sv["sd"], len(sample)))
        print("A floor scales as 1/sqrt(n): ADR 0032's own n is ~288 Briefs "
              "against %d pairs here." % len(sample))

    with open(OUT / "agg_floor.json", "w") as fh:
        json.dump({"n_pairs": len(sample), "k": k, "dtime": dtime,
                   "per_draw": {str(d): stats[d] for d in stats},
                   "floors": floors}, fh, indent=1)
    print("\nwrote out/agg_floor.json")


if __name__ == "__main__":
    main()
