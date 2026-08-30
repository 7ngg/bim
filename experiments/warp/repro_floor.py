"""How much of the "noise floor" is the time cap, and how much is a salted hash.

Ticket 82. Ticket 65 measured a floor by accident: two sweeps ran concurrently
and warped 1 489 identical `(brief, donor)` pairs -- same seed, same targets,
same `--time=3.0`, same code -- and disagreed on `served` 2.82 % of the time and
on `dev` 14.71 %. The stated mechanism was the wall-clock cap: CP-SAT returns
whatever incumbent it reached when the cap fired, and under different CPU load
that is a different one.

**That mechanism is real and it is not the only one, and the accident could not
tell them apart.** Two concurrent sweeps are two PROCESSES, and
`absolute_area.run_one` seeded its per-room objective weights with

    rng = random.Random(SEED ^ (hash(key) & 0xFFFF))

`hash` on a `str` is salted per process unless `PYTHONHASHSEED` is set. So the
two sweeps did not solve the same model twice under different load. They solved
**different objective functions** -- `W_STATED` 8 against `W_INVENTED` 1, drawn
per room at a 30 % coin flip, re-drawn in every process. Same key, three
processes, three weight vectors:

    h=38024  weights=[1, 8, 1, 1, 8, 8]
    h= 7292  weights=[1, 1, 8, 1, 1, 1]
    h=45387  weights=[8, 8, 8, 1, 8, 1]

This is the same defect ticket 65 fixed in `gate_effect.py`'s Brief draw and
`probe6.py`, and it survived in six live sites because those fixes were applied
to the SAMPLING and this one is in the OBJECTIVE.

So this script does deliberately what the accident did by chance, and separates
the two sources with a 2x2. Each `(brief, donor)` pair is solved `k` times under
each cell:

                       | wall-clock cap    | deterministic cap
    -------------------|-------------------|-------------------
    salt VARIED        | TOTAL  (= 65)     | salt alone
    salt FIXED         | time cap alone    | expect exactly 0

The bottom-right cell is the control: if it is not exactly zero, something else
is loose and neither of the other two readings can be trusted.

`--load` runs N busy processes alongside the sweep, because a time cap only
misbehaves under contention and an idle machine will under-report the floor.
That is the difference between this and the accident -- the accident WAS under
contention, and a quiet re-run is not a reproduction of it.

Sample: pairs are drawn from `out/gate_depth_warps.jsonl`, so the population is
exactly the one the published gate figures were computed on, not a fresh draw.

Run: python -u experiments/warp/repro_floor.py [n_pairs] [--k=5] [--time=3.0]
              [--dtime=6.0] [--load=3] [--tag=NAME]

Resumable: every solve is appended to `out/repro_floor_solves.jsonl` and flushed
as it lands, keyed by (pair, cell, repeat), so a re-run skips what it holds.
"""

from __future__ import annotations

import json
import os
import random
import subprocess
import sys
import time
import zlib
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fit_warp import SEED, COLLAPSE                                  # noqa: E402
from absolute_area import OUT, MARKET, pair_targets, run_one, floors_for  # noqa: E402
from best_of_m import load                                           # noqa: E402

CACHE = OUT / "gate_depth_warps.jsonl"

# The four cells. `salt` is the objective-weight draw, `cap` the stopping rule.
CELLS = [
    ("wall/varied", True, False),    # what ticket 65 measured
    ("wall/fixed", False, False),    # the time cap alone
    ("det/varied", True, True),      # the salt alone
    ("det/fixed", False, True),      # control: must be 0
]


def one_solve(brief, cand, tlim, dtime, wseed):
    """One warp, with the objective weight draw and the stopping rule both
    under explicit control. Mirrors `gate_depth.warp` so the outputs are the
    same three quantities the published figures are read off."""
    ct = [COLLAPSE.get(t, t) for t in cand["types"]]
    tg = pair_targets(ct, cand["parts"], brief["rooms"])
    if tg is None:
        return {"status": "NOPAIR", "served": False, "dev": None, "secs": 0.0}
    tg = [max(a, MARKET.get(t, 0.0)) for a, t in zip(tg, ct)]
    t0 = time.perf_counter()
    r = run_one(cand, brief["aspect"], tg, tlim,
                key=brief["k"] + cand["k"], hold_ring=True,
                wseed=wseed, dtime=dtime)
    row = {"status": r["status"], "served": False, "dev": None,
           "secs": round(time.perf_counter() - t0, 3)}
    if r["status"] == "OK":
        floors = floors_for(r["types"])
        margin = [g - fl for g, fl in zip(r["got"], floors) if fl is not None]
        row["served"] = all(m >= 0 for m in margin)
        dev = [abs(g - t) / t for g, t in zip(r["got"], r["targets"]) if t > 0]
        row["dev"] = round(max(dev), 4) if dev else None
        row["space"] = r["space_m2_total"]
        # Did the CAP bind? A solve proved optimal cannot vary with load, so
        # this is the denominator the time-cap floor is really measured over.
        row["opt"] = r.get("all_optimal")
    return row


def disagreement(runs, field):
    """Share of pairs whose `k` repeats do NOT all agree on `field`.

    This is ticket 65's own statistic and it is deliberately the same one: a
    pair counts as disagreeing if any two of its repeats differ, so the numbers
    here are directly comparable to 2.82 % and 14.71 %."""
    n = bad = 0
    for vals in runs.values():
        if len(vals) < 2:
            continue
        n += 1
        if len({json.dumps(v.get(field)) for v in vals}) > 1:
            bad += 1
    return bad, n


def spread(runs, field):
    """Worst within-pair spread on a continuous field, and its distribution.

    A disagreement RATE says how often a figure moves; it does not say how far.
    `dev` is quoted to four decimals across this directory, so the size of the
    move is what decides whether a published tenth of a point is real."""
    rel = []
    for vals in runs.values():
        xs = [v[field] for v in vals if v.get(field) is not None]
        if len(xs) < 2:
            continue
        lo, hi = min(xs), max(xs)
        if lo > 0:
            rel.append((hi - lo) / lo)
    rel.sort()
    if not rel:
        return None
    return {"n": len(rel), "p50": rel[len(rel) // 2],
            "p90": rel[int(0.9 * len(rel))], "max": rel[-1],
            "nonzero": sum(1 for r in rel if r > 0) / len(rel)}


def busy(n):
    """N spinning processes, so the wall-clock cap is measured under the
    contention it actually misbehaves under. An idle machine under-reports."""
    if not n:
        return []
    code = "import time\nt=time.time()\nx=0\nwhile time.time()-t<3600: x=(x*x+1)%1000003"
    return [subprocess.Popen([sys.executable, "-c", code],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL) for _ in range(n)]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n_pairs = int(args[0]) if args else 60
    k, tlim, dtime, nload, tag, only = 5, 3.0, 6.0, 3, "", ""
    for a in sys.argv[1:]:
        if a.startswith("--k="):
            k = int(a.split("=", 1)[1])
        if a.startswith("--time="):
            tlim = float(a.split("=", 1)[1])
        if a.startswith("--dtime="):
            dtime = float(a.split("=", 1)[1])
        if a.startswith("--load="):
            nload = int(a.split("=", 1)[1])
        if a.startswith("--tag="):
            tag = a.split("=", 1)[1]
        if a.startswith("--only="):
            only = a.split("=", 1)[1]
    OUT.mkdir(exist_ok=True)
    suffix = ("_" + tag) if tag else ""
    solves_p = OUT / ("repro_floor_solves%s.jsonl" % suffix)

    print("PYTHONHASHSEED = %r  (unset means str hashing is salted per process)"
          % os.environ.get("PYTHONHASHSEED"))
    print("pairs %d | k %d | wall cap %.1fs | det cap %.1f | load %d\n"
          % (n_pairs, k, tlim, dtime, nload))

    # -- the sample: pairs the published figures were actually computed on.
    seen = []
    with open(CACHE) as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                seen.append((r["brief"], r["donor"]))
    uniq = sorted(set(seen))
    print("distinct (brief, donor) pairs in the gate cache: %s"
          % format(len(uniq), ","))

    if only == "disagree":
        # The DECISIVE population. 1 489 pairs were warped twice by the two
        # concurrent sweeps; 219 of them returned a different `dev` and 42 a
        # different `served`. A random sample of all 3 834 would carry that
        # signal at its base rate and need four times the solves to see it.
        # Restricting to the pairs that DID move asks the sharp question: with
        # the objective weight draw held fixed and only the wall clock free,
        # does the disagreement survive on the very pairs it was observed on?
        dup = defaultdict(list)
        with open(CACHE) as fh:
            for line in fh:
                if line.strip():
                    r = json.loads(line)
                    dup[(r["brief"], r["donor"])].append(r["warp"])
        uniq = sorted(kk for kk, vs in dup.items() if len(vs) > 1
                      and len({v.get("dev") for v in vs}) > 1)
        print("restricted to pairs whose duplicate warps DISAGREED on dev: %s"
              % format(len(uniq), ","))

    cands, _by_ms, _by_n = load()
    by_k = {c["k"]: c for c in cands}
    pool = [p for p in uniq if p[0] in by_k and p[1] in by_k]
    print("pairs resolvable against the room cache          : %s"
          % format(len(pool), ","))
    sample = random.Random(SEED).sample(pool, min(n_pairs, len(pool)))
    print("sampled                                          : %d\n" % len(sample))

    done = set()
    if solves_p.exists():
        with open(solves_p) as fh:
            for line in fh:
                if line.strip():
                    r = json.loads(line)
                    done.add((r["bk"], r["dk"], r["cell"], r["rep"]))
    if done:
        print("resuming: %d solves already on file\n" % len(done))

    procs = busy(nload)
    t_start = time.time()
    try:
        with open(solves_p, "a") as out:
            for i, (bk, dk) in enumerate(sample, 1):
                brief, cand = by_k[bk], by_k[dk]
                for cell, vary, det in CELLS:
                    for rep in range(k):
                        if (bk, dk, cell, rep) in done:
                            continue
                        # FIXED salt: one value for the pair, every repeat and
                        # every process. VARIED salt: a different value per
                        # repeat, which is what a fresh process gives you.
                        base = zlib.crc32((bk + "|" + dk).encode())
                        wseed = base ^ (rep * 0x9E3779B1) if vary else base
                        row = one_solve(brief, cand, tlim,
                                        dtime if det else None, wseed)
                        row.update(bk=bk, dk=dk, cell=cell, rep=rep)
                        out.write(json.dumps(row) + "\n")
                        out.flush()
                        os.fsync(out.fileno())
                if i % 10 == 0 or i == len(sample):
                    el = time.time() - t_start
                    print("  %3d/%d pairs   %5.1f min elapsed"
                          % (i, len(sample), el / 60), flush=True)
    finally:
        for p in procs:
            p.kill()

    # -- read the whole file back, so a resumed run analyses everything.
    per_cell = defaultdict(lambda: defaultdict(list))
    with open(solves_p) as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                per_cell[r["cell"]][(r["bk"], r["dk"])].append(r)

    print("\n%s" % ("=" * 78))
    print("DISAGREEMENT RATE -- share of pairs whose k repeats do not all agree")
    print("%s" % ("=" * 78))
    print("%-14s %10s %12s %12s %12s" % ("cell", "pairs", "status", "served", "dev"))
    summary = {}
    for cell, _v, _d in CELLS:
        runs = per_cell.get(cell)
        if not runs:
            continue
        row = {}
        cols = []
        for f in ("status", "served", "dev"):
            bad, n = disagreement(runs, f)
            row[f] = {"disagree": bad, "n": n,
                      "pct": (100.0 * bad / n) if n else None}
            cols.append("%d/%d %5.2f%%" % (bad, n, 100.0 * bad / n) if n else "-")
        print("%-14s %10d %12s %12s %12s"
              % (cell, len(runs), cols[0], cols[1], cols[2]))
        row["dev_spread"] = spread(runs, "dev")
        row["space_spread"] = spread(runs, "space")
        row["secs_p50"] = sorted(v["secs"] for vs in runs.values() for v in vs)[
            sum(len(v) for v in runs.values()) // 2]
        summary[cell] = row

    print("\n%s" % ("=" * 78))
    print("HOW FAR IT MOVES -- within-pair relative spread of `dev`")
    print("%s" % ("=" * 78))
    print("%-14s %8s %10s %10s %10s %10s"
          % ("cell", "pairs", "nonzero", "p50", "p90", "max"))
    for cell, _v, _d in CELLS:
        s = summary.get(cell, {}).get("dev_spread")
        if s:
            print("%-14s %8d %9.1f%% %9.4f %9.4f %9.4f"
                  % (cell, s["n"], 100 * s["nonzero"], s["p50"], s["p90"],
                     s["max"]))

    print("\n%s" % ("=" * 78))
    print("COST -- median seconds a solve")
    print("%s" % ("=" * 78))
    for cell, _v, _d in CELLS:
        if cell in summary:
            print("%-14s %8.3f s" % (cell, summary[cell]["secs_p50"]))

    print("" + chr(10) + "%s" % ("=" * 78))
    print("DID THE CAP BIND -- share of solves that did NOT prove optimal")
    print("%s" % ("=" * 78))
    for cell, _v, _d in CELLS:
        runs = per_cell.get(cell)
        if not runs:
            continue
        vs = [v for lst in runs.values() for v in lst if "opt" in v]
        if not vs:
            continue
        capped = sum(1 for v in vs if v["opt"] is False)
        # Restricted to pairs where the cap bound on at least one repeat: the
        # only pairs where a wall clock can change the answer at all.
        sub = {kk: lst for kk, lst in runs.items()
               if any(v.get("opt") is False for v in lst)}
        bad, n = disagreement(sub, "dev") if sub else (0, 0)
        print("%-14s capped %5.1f%% of solves (%d/%d) | on capped pairs, dev "
              "disagrees %s"
              % (cell, 100.0 * capped / len(vs), capped, len(vs),
                 ("%d/%d %.1f%%" % (bad, n, 100.0 * bad / n)) if n else "n/a"))
        summary.setdefault(cell, {})["capped_share"] = capped / len(vs)
        summary[cell]["capped_pairs"] = len(sub)
        summary[cell]["capped_pairs_dev_disagree"] = bad

    ctrl = summary.get("det/fixed", {}).get("served", {}).get("disagree")
    ctrl_d = summary.get("det/fixed", {}).get("dev", {}).get("disagree")
    print("\ncontrol cell det/fixed: served %s, dev %s -- both must be 0"
          % (ctrl, ctrl_d))

    res = {"n_pairs": len(sample), "k": k, "tlim": tlim, "dtime": dtime,
           "load": nload, "only": only, "cells": summary,
           "pythonhashseed": os.environ.get("PYTHONHASHSEED")}
    with open(OUT / ("repro_floor%s.json" % suffix), "w") as fh:
        json.dump(res, fh, indent=1)
    print("\nwrote out/repro_floor%s.json" % suffix)


if __name__ == "__main__":
    main()
