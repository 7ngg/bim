"""Is the pipeline reproducible at a fixed seed? (F13's own check.)

Two runs of `run.py` at seed 20260830 disagreed on which Briefs were served.
This solves the SAME candidates repeatedly in ONE process and compares, stage by
stage, so the answer is about the solvers and not about anything the run loop
does between them.

    ./venv/Scripts/python.exe experiments/demo-sheet/_determinism.py [reps]

Prints, per stage, how many repeats differ from the first.
"""
import pathlib
import random
import sys
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run as R                                                   # noqa: E402
import briefs_az                                                  # noqa: E402
from absolute_area import MARKET, admissible_pool, pair_targets   # noqa: E402
from project_join import COLLAPSE, warp_geom                      # noqa: E402


def key_of(w):
    """Everything the projection reads out of a warp."""
    if w["status"] != "OK":
        return ("status", w["status"])
    return (tuple(w["gx"]), tuple(w["gy"]),
            tuple(tuple(sorted(p)) for p in w["spans"]),
            tuple(round(g, 6) for g in w["got"]))


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    cands = R.load()
    by_ms = defaultdict(list)
    for c in cands:
        by_ms[c["ms"]].append(c)
    briefs = briefs_az.build(by_ms, otaq=[2, 3])
    rng = random.Random(R.SEED)
    rng.shuffle(briefs)

    pairs = []
    for b in briefs[:4]:
        pool = admissible_pool(b, by_ms)
        for cand in pool[:3]:
            pairs.append((b, cand))
    print("checking %d (Brief, donor) pairs x %d repeats" % (len(pairs), reps))

    warp_diff = solve_diff = 0
    for b, cand in pairs:
        ct = [COLLAPSE.get(t, t) for t in cand["types"]]
        tg = pair_targets(ct, cand["parts"], b["rooms"])
        if tg is None:
            continue
        tg = [max(a, MARKET.get(t, 0.0)) for a, t in zip(tg, ct)]
        keys, statuses = [], []
        for _ in range(reps):
            w = warp_geom(cand, b["aspect"], tg, 2.5,
                          key=b["k"] + cand["k"], hold_ring=True)
            keys.append(key_of(w))
            if w["status"] == "OK":
                got = R._one(b, cand, 2.5, 10.0, False, "max")
                statuses.append((got["row"]["status"],
                                 got["row"].get("valid"),
                                 got["row"].get("placed")))
        if len(set(keys)) > 1:
            warp_diff += 1
            print("  WARP DIFFERS  %s / %s : %d distinct results"
                  % (b["k"], cand["k"][:18], len(set(keys))))
        if len(set(statuses)) > 1:
            solve_diff += 1
            print("  SOLVE DIFFERS %s / %s : %s"
                  % (b["k"], cand["k"][:18], sorted(set(statuses))))
    print()
    print("warp non-deterministic on %d of %d pairs" % (warp_diff, len(pairs)))
    print("pipeline outcome non-deterministic on %d of %d pairs"
          % (solve_diff, len(pairs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
