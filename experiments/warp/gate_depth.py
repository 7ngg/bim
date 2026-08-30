"""What the gate is worth at the depth the gate can actually FILL.

Ticket 65. ADR 0032 is decided at `m = 3` and the shipped `m` is 8, and the
existing `m = 8` block is confounded: `stretch_terms.py` 4e draws WITH
replacement from at most three distinct warps a stratum, so the incumbent
saturates at best-of-3 while a rule admitting refused members saturates at
best-of-6. ADR 0032 consequence 5 records a real `m = 8` as owed and names the
probe: `gate_effect.py --k=8`.

**That probe cannot answer the question, and the reason is measurable without a
single solve.** `gate_effect.strata` drops a Brief unless BOTH strata hold K
members. At `K = 8` that keeps 229 of 500 Briefs -- and the 271 it drops are
exactly the Briefs whose admitted pool holds fewer than 8. The ticket's own
mechanism is that at `m = 8` the incumbent gate is *binding below the depth the
engine asks for*, so a looser rule wins by supplying draws the incumbent cannot.
Conditioning on `n_admitted >= 8` removes every Brief where that mechanism
operates. The run would cost ~2 h and return "confirmed" on the one population
that cannot exhibit the effect.

`pool_depth.py` publishes the distribution that makes this concrete. Under the
shipped `gated` definition the pool p50 is **6** (8 at 4-6 rooms, 6 at 7-10) and
only **46 %** of Briefs hold 8 or more. The engine asks for 8 and the median
Brief has 6. That is not a rig artefact to be scaled away -- 2.2.7's own ratio
puts sample depth at production depth for this quantity.

So this script measures the thing the equal-K design cannot: **each rule gets the
pool it actually supplies, truncated at m, drawn WITHOUT replacement.** Unequal
depth between arms is not a confound here. It is the effect under test.

Three readings come off one run:

  `m = 3`, equal-K subset   -- Briefs with >= 3 in both strata, first 3 of each.
                               Recovers ADR 0032's ORDERING on the post-ADR-0037
                               rig. Not its numbers, and not its sample: that
                               draw was salted by `hash()` and is unrecoverable.
                               This is NOT the `market`-arm re-run MAP.md owes --
                               that debt is a measurement of what MOVED, and no
                               arm here runs the pre-0037 literals. Still owed.
  `m = 8`, realised depth   -- the honest shipped-depth comparison.
  depth split               -- the falsifiable prediction: a replacement rule's
                               gain should concentrate in Briefs whose incumbent
                               pool holds fewer than m, and vanish elsewhere.

Four rules are `stretch_terms.py`'s combos verbatim, over the whole bucket:
`incumbent` is the two blunt scalars, `req <= 1` the sound frame bound, `both`
the ADR 0032 decision (join, do not replace), and `logd + req` the fourth. The
fifth arm, `DEPTH` below, is depth-conditional and is not a filter at all.

Every term a rule reads -- `d_area`, `d_aspect`, `req`, `logd` -- is computed off
the index record with no solve, so a rule's POOL is known before anything is
warped. Only the union of the four draws is warped, which is why this costs about
what `--k=8` would have cost while covering four rules instead of two arms.

Determinism: draws are ordered by `crc32(brief|donor)`, not `hash()`.
`gate_effect.py` seeded its per-Brief draw with `hash(brief["k"])`, and `hash` on
`str` is salted per process unless `PYTHONHASHSEED` is set, so **that draw was a
different sample on every run** and the README's "seed 20260819 throughout, so a
Brief here is the same Brief there" never held for it. The Brief *sample* was
always fine; the per-Brief *candidate* draw was not. Fixed here to `crc32`, the
same fix and the same reason as `experiments/solver-toy/probe6.py`. The
consequence for the record: `out/gate_effect_briefs.json` is one unreproducible
draw, ADR 0032 rests on it, and its run-to-run variance has never been measured.

Run: python -u experiments/warp/gate_depth.py [n] [--m=8] [--time=3.0] [--dry]
              [--cache=gate_depth_warps.jsonl]

Resumable: every warp is appended to `out/<cache>` and flushed as it lands, so
an interrupted sweep resumes by re-invoking with the same arguments.
"""

from __future__ import annotations

import json
import math
import random
import sys
import time
import zlib
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fit_warp import SEED, AREA_TOL, ASPECT_TOL, COLLAPSE          # noqa: E402
from absolute_area import (OUT, MARKET, pair_targets, run_one,     # noqa: E402
                           floors_for, pct)
from best_of_m import load                                          # noqa: E402
from gate_effect import strata                                      # noqa: E402
from stretch_terms import (F_PARTITION, MIN_SIDE, MIN_SIDE_DEFAULT,  # noqa: E402
                           coord_frame, notch_share, frame_requirement,
                           gate_box)

RULES = {
    "incumbent only": lambda t: t["d_area"] <= 1.0 and t["d_aspect"] <= 1.0,
    "req <= 1 only": lambda t: t["req"] is not None and t["req"] <= 1.0,
    "both (join)": lambda t: (t["d_area"] <= 1.0 and t["d_aspect"] <= 1.0
                              and t["req"] is not None and t["req"] <= 1.0),
    "logd <= 0.30 + req <= 1": lambda t: (t["logd"] is not None
                                          and t["logd"] <= 0.30
                                          and t["req"] is not None
                                          and t["req"] <= 1.0),
}

# The fifth arm is not a filter and cannot be one: it reads the SIZE of the pool
# the incumbent returns, which no per-candidate predicate can see. Take the
# incumbent's members; if they number fewer than `m`, top up from `req <= 1`
# until they do. Where the incumbent is deep this IS the incumbent, so the
# proportion argument the pair carries survives untouched wherever it is not
# starving; where it is thin the sound bound supplies the rest of the draw.
#
# It costs no new warps. Filling to `m` needs at most `m - j` members of
# `req <= 1` \ incumbent, and the (m-j)-th of those sits at position
# <= (m - j) + |incumbent n req<=1| <= m in `req <= 1`'s own crc32 order -- so
# every member it can ever draw is already inside that rule's first-`m` draw.
DEPTH = "incumbent, topped up to m by req <= 1"
ARMS = list(RULES) + [DEPTH]


def terms(brief, cand):
    """Every quantity a rule reads, off the index record. No solve.

    `req` and `logd` are None where the donor's frame is not computable -- a
    degenerate coord frame or a notch share past 0.60, the same two exclusions
    `stretch_terms.enrich` makes. A rule reading `req` does not admit those;
    they are counted separately rather than silently dropped, because they are
    pool members the engine would really be handed.
    """
    # Compared UNROUNDED. `gate_effect.term_distances` rounds to 4 dp before
    # storing, and `stretch_terms.incumbent` then compares the rounded value to
    # 1.0 -- so a donor at d_aspect = 1.0000164 passes `incumbent()` while
    # `gated_pool` refuses it. Measured contamination in the existing rig: 1
    # candidate in 7 827, 1 Brief in 115. Immaterial there, kept exact here.
    da = abs(brief["area"] - cand["area"]) / (AREA_TOL * cand["area"])
    dp = abs(brief["aspect"] - cand["aspect"]) / (ASPECT_TOL * cand["aspect"])
    out = {"d_area": da, "d_aspect": dp,
           "req": None, "logd": None, "ext": None, "donor": cand["k"],
           "ord": zlib.crc32((brief["k"] + "|" + cand["k"]).encode())}

    ct = [COLLAPSE.get(t, t) for t in cand["types"]]
    tg = pair_targets(ct, cand["parts"], brief["rooms"])
    out["nopair"] = tg is None
    if tg is None:
        return out
    tg = [max(a, MARKET.get(t, 0.0)) for a, t in zip(tg, ct)]
    xs, ys, spans = coord_frame(cand["parts"])
    if len(xs) < 2 or len(ys) < 2:
        return out
    s, _void = notch_share(cand["parts"])
    if s >= 0.60:
        return out
    mins = [MIN_SIDE.get(t, MIN_SIDE_DEFAULT) for t in ct]
    wq, hq = frame_requirement(spans, len(xs) - 1, len(ys) - 1, mins)
    W, H = gate_box(sum(tg), brief["aspect"], s)
    ar = brief["area"] * (1.0 + F_PARTITION) / cand["area"]
    pr = brief["aspect"] / cand["aspect"]
    out["req"] = max(wq / W, hq / H)
    out["logd"] = (math.log(ar) ** 2 + math.log(pr) ** 2) ** 0.5
    out["ext"] = round(max(abs(math.log((ar * pr) ** 0.5)),
                           abs(math.log((ar / pr) ** 0.5))), 5)
    return out


def warp(brief, cand, tlim):
    """One warp. Mirrors gate_effect.warp_candidates so the two are comparable."""
    ct = [COLLAPSE.get(t, t) for t in cand["types"]]
    tg = pair_targets(ct, cand["parts"], brief["rooms"])
    if tg is None:
        return {"status": "NOPAIR", "served": False, "dev": None}
    tg = [max(a, MARKET.get(t, 0.0)) for a, t in zip(tg, ct)]
    t0 = time.perf_counter()
    r = run_one(cand, brief["aspect"], tg, tlim,
                key=brief["k"] + cand["k"], hold_ring=True)
    row = {"status": r["status"], "served": False, "dev": None,
           "secs": round(time.perf_counter() - t0, 3)}
    if r["status"] == "OK":
        floors = floors_for(r["types"])
        margin = [g - fl for g, fl in zip(r["got"], floors) if fl is not None]
        row["served"] = all(m >= 0 for m in margin)
        dev = [abs(g - t) / t for g, t in zip(r["got"], r["targets"]) if t > 0]
        row["dev"] = round(max(dev), 4) if dev else None
    return row


def best_of(members, m):
    """Best served member of the first m, drawn WITHOUT replacement.

    Returns (served, best_dev, realised_depth). `realised_depth` is
    min(m, |pool|) -- the number of candidates the rule actually supplies, which
    is the quantity the equal-K design holds fixed and this one does not.
    """
    take = members[:m]
    good = [x["dev"] for x in take if x["served"] and x["dev"] is not None]
    return (bool(good), min(good) if good else None, len(take))


def summarise(briefs, rule, m, only=None):
    served, devs, depths = 0, [], []
    n = 0
    for b in briefs:
        if only is not None and not only(b):
            continue
        mem = b["pools"].get(rule)
        if not mem:
            continue
        n += 1
        ok, dev, d = best_of(mem, m)
        depths.append(d)
        if ok:
            served += 1
            devs.append(dev)
    if not n:
        return None
    devs.sort()
    return {"briefs": n, "served": served,
            "served_rate": round(served / n, 4),
            "best_dev_p50": round(pct(devs, 0.50), 4) if devs else None,
            "best_dev_p90": round(pct(devs, 0.90), 4) if devs else None,
            "depth_p50": sorted(depths)[len(depths) // 2],
            "depth_mean": round(sum(depths) / len(depths), 2),
            "depth_full": round(sum(1 for d in depths if d >= m) / len(depths), 4)}


def boot_ci(briefs, rule, m, only=None, draws=400):
    """Brief-level bootstrap on the served rate and the dev percentiles.

    Resamples BRIEFS, not candidates: the arms share a Brief, so the Brief is
    the independent unit. This is the same resampling unit 4e uses and the CIs
    are therefore comparable to ADR 0032's.
    """
    pool = [b for b in briefs if (only is None or only(b)) and b["pools"].get(rule)]
    if not pool:
        return None
    rng = random.Random(SEED)
    sr, p50s, p90s = [], [], []
    for _ in range(draws):
        pick = [pool[rng.randrange(len(pool))] for _ in range(len(pool))]
        ok, devs = 0, []
        for b in pick:
            s, dev, _ = best_of(b["pools"][rule], m)
            if s:
                ok += 1
                devs.append(dev)
        sr.append(ok / len(pick))
        devs.sort()
        p50s.append(pct(devs, 0.50) if devs else 0.0)
        p90s.append(pct(devs, 0.90) if devs else 0.0)
    sr.sort(); p50s.sort(); p90s.sort()
    lo, hi = int(0.025 * draws), int(0.975 * draws)
    return {"served_ci": [round(sr[lo], 4), round(sr[hi], 4)],
            "p50_ci": [round(p50s[lo], 4), round(p50s[hi], 4)],
            "p90_ci": [round(p90s[lo], 4), round(p90s[hi], 4)]}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n_arg = int(args[0]) if args else 400
    tlim, M, dry, cache, seed = 3.0, 8, False, "gate_depth_warps.jsonl", SEED
    for a in sys.argv[1:]:
        if a.startswith("--time="):
            tlim = float(a.split("=", 1)[1])
        if a.startswith("--m="):
            M = int(a.split("=", 1)[1])
        if a.startswith("--cache="):
            cache = a.split("=", 1)[1]
        if a.startswith("--seed="):
            seed = int(a.split("=", 1)[1])
        if a == "--dry":
            dry = True
    OUT.mkdir(exist_ok=True)
    cache_p = OUT / cache

    cands, by_ms, _by_n = load()
    print("converted dwellings joined to the room cache: %s"
          % format(len(cands), ","))
    sample = random.Random(seed).sample(cands, min(n_arg, len(cands)))
    print("sample %d Briefs | m %d | time %.1fs | seed %d\n"
          % (len(sample), M, tlim, seed))

    # -- pass 1: every rule's pool, with no solve anywhere.
    plans, need = [], {}
    for brief in sample:
        bucket, admitted, refused = strata(brief, by_ms)
        if not bucket:
            continue
        tt = {c["k"]: terms(brief, c) for c in bucket}
        by_k = {c["k"]: c for c in bucket}
        pools = {}
        for nm, keep in RULES.items():
            sel = [t for t in tt.values() if keep(t)]
            sel.sort(key=lambda t: t["ord"])
            pools[nm] = [t["donor"] for t in sel[:M]]
            for dk in pools[nm]:
                need[(brief["k"], dk)] = (brief, by_k[dk])

        chosen = list(pools["incumbent only"])
        if len(chosen) < M:
            have = set(chosen)
            sound = sorted((t for t in tt.values() if RULES["req <= 1 only"](t)),
                           key=lambda t: t["ord"])
            for t in sound:
                if len(chosen) >= M:
                    break
                if t["donor"] not in have:
                    chosen.append(t["donor"])
                    have.add(t["donor"])
        pools[DEPTH] = chosen
        for dk in chosen:
            need[(brief["k"], dk)] = (brief, by_k[dk])

        sizes = {nm: sum(1 for t in tt.values() if RULES[nm](t)) for nm in RULES}
        sizes[DEPTH] = len(chosen)
        plans.append({"k": brief["k"], "n": brief["n"], "bucket": len(bucket),
                      "n_admitted": len(admitted), "n_refused": len(refused),
                      "pool_size": sizes, "pools": pools})

    print("Briefs with a non-empty bucket : %d" % len(plans))
    print("distinct warps needed          : %d" % len(need))
    print("estimated                      : %.0f min at 1.53 s a warp\n"
          % (len(need) * 1.53 / 60))
    for nm in ARMS:
        ps = [p["pool_size"][nm] for p in plans]
        ps.sort()
        print("  %-26s pool p50 %3d   >= %d on %5.1f%% of Briefs"
              % (nm, ps[len(ps) // 2], M,
                 100 * sum(1 for v in ps if v >= M) / len(ps)))
    if dry:
        return

    # -- pass 2: warp the union once, RESUMABLY.
    #
    # The first attempt at this run was killed at ~31 % after 58 minutes and
    # left NOTHING behind: results were held in memory and stdout was block
    # buffered, so the log was 0 bytes and not one warp survived. Both causes
    # are fixed here. Every warp is appended to a JSONL and flushed to the OS
    # as it completes, so an interruption costs one warp, not an hour; and a
    # re-run reads the file back and skips what it holds. Run with `python -u`.
    done = {}
    if cache_p.exists():
        with open(cache_p) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except ValueError:
                    continue            # a torn last line from a hard kill
                # FIRST occurrence wins, so a re-read of the same file is
                # stable. A key can appear twice when two sweeps run at once,
                # and the two results are NOT always equal: CP-SAT at a time cap
                # returns whatever it reached, so under different CPU load the
                # same warp can land on a different solution. Measured on the
                # 1 489 keys this file holds twice: identical `status` every
                # time, but **2.82 % disagree on `served`** and **14.71 % on
                # `dev`**. That is the noise floor for every timed figure in
                # this rig, and it is why a `last wins` dedupe made the same
                # analysis move between two reads of one file.
                done.setdefault((r["brief"], r["donor"]), r["warp"])
        print("resuming: %d warps already on disk" % len(done), flush=True)

    todo = [(k, v) for k, v in need.items() if k not in done]
    print("\nwarping %d (%d already done)..." % (len(todo), len(done)),
          flush=True)
    t0, n0 = time.perf_counter(), len(done)
    with open(cache_p, "a") as fh:
        for i, (key, (brief, cand)) in enumerate(todo):
            done[key] = warp(brief, cand, tlim)
            fh.write(json.dumps({"brief": key[0], "donor": key[1],
                                 "warp": done[key]}) + "\n")
            fh.flush()
            if (i + 1) % 25 == 0:
                el = time.perf_counter() - t0
                print("  %d/%d warps (%d total), %.0fs elapsed, %.0f min left"
                      % (i + 1, len(todo), n0 + i + 1, el,
                         (el / (i + 1) * (len(todo) - i - 1)) / 60), flush=True)

    # A Brief is analysable only if every draw it makes was warped. An
    # interrupted sweep leaves a completed prefix plus one partial Brief, so
    # drop the partial rather than KeyError -- the cached prefix stays usable.
    full = []
    for p in plans:
        if all((p["k"], dk) in done for ks in p["pools"].values() for dk in ks):
            p["pools"] = {nm: [dict(done[(p["k"], dk)], donor=dk) for dk in ks]
                          for nm, ks in p["pools"].items()}
            full.append(p)
    if len(full) < len(plans):
        print("\n%d of %d Briefs fully warped (%d partial, dropped)"
              % (len(full), len(plans), len(plans) - len(full)), flush=True)
    plans = full

    # -- reading 1: m = 3, equal-K subset. ADR 0032's row on the post-0037 rig.
    eq3 = lambda b: b["n_admitted"] >= 3 and b["n_refused"] >= 3   # noqa: E731
    print("\n--- 1. m = 3, equal-K subset (ADR 0032's row, re-measured) ---")
    print("%-26s%8s%9s%9s%9s%22s" % ("rule", "briefs", "served", "p50", "p90",
                                     "served 95% CI"))
    out = {"m3_equalK": {}, "m8_realised": {}, "depth_split": {}}
    for nm in ARMS:
        s = summarise(plans, nm, 3, only=eq3)
        c = boot_ci(plans, nm, 3, only=eq3)
        if not s:
            continue
        out["m3_equalK"][nm] = dict(s, **(c or {}))
        print("%-26s%8d%8.1f%%%9s%9s%12s"
              % (nm, s["briefs"], 100 * s["served_rate"], s["best_dev_p50"],
                 s["best_dev_p90"],
                 "[%.1f-%.1f]" % (100 * c["served_ci"][0], 100 * c["served_ci"][1])))

    # -- reading 2: m = 8, realised depth. The shipped configuration.
    print("\n--- 2. m = %d, REALISED depth (each rule gets the pool it fills) ---" % M)
    print("%-26s%8s%9s%9s%9s%10s%9s" % ("rule", "briefs", "served", "p50", "p90",
                                        "depth p50", "full"))
    for nm in ARMS:
        s = summarise(plans, nm, M)
        c = boot_ci(plans, nm, M)
        if not s:
            continue
        out["m8_realised"][nm] = dict(s, **(c or {}))
        print("%-26s%8d%8.1f%%%9s%9s%10d%8.1f%%"
              % (nm, s["briefs"], 100 * s["served_rate"], s["best_dev_p50"],
                 s["best_dev_p90"], s["depth_p50"], 100 * s["depth_full"]))
    for nm in ARMS:
        v = out["m8_realised"].get(nm)
        if v and v.get("served_ci"):
            print("   %-26s served CI [%.1f-%.1f]  p90 CI [%.3f-%.3f]"
                  % (nm, 100 * v["served_ci"][0], 100 * v["served_ci"][1],
                     v["p90_ci"][0], v["p90_ci"][1]))

    # -- reading 3: the falsifiable prediction.
    thin = lambda b: b["pool_size"]["incumbent only"] < M    # noqa: E731
    deep = lambda b: b["pool_size"]["incumbent only"] >= M   # noqa: E731
    print("\n--- 3. does the gain live in the THIN Briefs, as predicted? ---")
    for lab, sel in (("incumbent pool < %d" % M, thin),
                     ("incumbent pool >= %d" % M, deep)):
        print(" %s" % lab)
        blk = {}
        for nm in ARMS:
            s = summarise(plans, nm, M, only=sel)
            if not s:
                continue
            blk[nm] = s
            print("   %-26s%6d briefs%8.1f%%  p50 %-8s p90 %-8s depth p50 %d"
                  % (nm, s["briefs"], 100 * s["served_rate"], s["best_dev_p50"],
                     s["best_dev_p90"], s["depth_p50"]))
        out["depth_split"][lab] = blk

    out["_meta"] = {"n_requested": n_arg, "m": M, "time_limit_s": tlim,
                    "seed": seed, "briefs": len(plans), "warps": len(need),
                    "arms": ARMS}
    OUT.mkdir(exist_ok=True)
    # Seed-keyed: a second-seed run must not overwrite the first's rows, which
    # is exactly what happened once and cost a re-derivation of the seed-1 table.
    tag = "" if seed == SEED else "_s%d" % seed
    json.dump(out, open(OUT / ("gate_depth%s.json" % tag), "w"), indent=1)
    json.dump(plans, open(OUT / ("gate_depth_briefs%s.json" % tag), "w"))
    print("\nwrote %s" % (OUT / ("gate_depth%s.json" % tag)))


if __name__ == "__main__":
    main()
