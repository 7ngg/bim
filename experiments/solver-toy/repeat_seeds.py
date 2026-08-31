"""The variance estimate `solver-formulation.md` has owed since Part I, and the
price of the one flag that buys parallel determinism.

Ticket 83, items 3 and 4.

WHAT WAS OWED, AND WHY THE EIGHT SEEDS ALREADY RUN DO NOT DISCHARGE IT
---------------------------------------------------------------------
`solver-formulation.md` "What this note does not establish" says:

    Multiple seeds. Every timing is a single run at seed 20260817. There is no
    variance estimate. CP-SAT's portfolio search is stochastic across workers;
    these numbers could move materially on a re-run and must be repeated over
    >= 10 seeds before any of them is quoted as a specification.

Part II answers a *different* question and it is easy to mistake it for this
one. Its S2 grid is "8 room counts by 5 exposures by 8 seeds", but `sweep.py`
feeds `BASE_SEED + s` to BOTH the scenario builder and `SolveConfig.seed` -- one
knob, moving the Envelope, the Brief, the ground truth, the Proposal noise AND
CP-SAT's `random_seed` together. Its spread is therefore a spread over
*instances*, and it cannot separate "this dwelling is harder" from "the
portfolio went the other way this time". `sweep.py`'s own `KEY_FIELDS` comment
concedes the point: `solver_seed` is "None means 'use the scenario seed', which
is what every suite" does -- every suite but S7, which holds the scenario fixed
and moves `solver_seed` alone, and which ran at **4** seeds per cell purely to
count distinct Plans against tau.

The clause quoted above is about **portfolio** stochasticity. Discharging it
needs S7's design at S2's scale: one instance, >= 10 solver seeds, and the
spread reported on the quantities the note publishes. That is arm `base` here.

WHY THE SAME RUNS PRICE `interleave_search`
-------------------------------------------
ADR 0043 decision 5: no timing from a non-interleaved parallel run may become a
threshold, and "a gate that must be stable needs `interleave_search=true` +
`max_deterministic_time` + pinned `random_seed` and `num_workers`". That flag is
the only predicate `LaunchSubsolvers` (`cp_model_solver.cc:823-836`) branches on,
upstream marks it "Experimental.", it defaults false, and **what it costs on this
repo's models is unmeasured** -- so it cannot be made a default. Pricing it is
the same grid with the flag flipped, so it is one rig and not two.

THE THIRD ARM IS THE CLAIM ADR 0043 ASSERTS AND NOBODY HAS RUN
--------------------------------------------------------------
Decision 5 prescribes a configuration for a stable gate; no experiment on this
map has ever run it. Arm `det` is that configuration -- `interleave_search=true`
under `max_deterministic_time` with NO wall cap -- and every cell is solved
TWICE so the prescription is tested rather than trusted. Two runs of one cell
agree iff their Plan fingerprint and objective are identical.

Every cell in every arm is run twice, so this rig reports, from one grid:

  * arm `base`  the seed spread the note owes, on the SHIPPED configuration
  * `base` x2   whether a non-interleaved 4-worker run repeats itself at all
  * arm `il`    what `interleave_search` costs in quality at a fixed wall budget
  * arm `det`   whether decision 5's prescription is actually reproducible

PROVENANCE (ADR 0043 decision 6)
--------------------------------
1. `ortools` version           -- recorded in the meta block, asserted at 9.15.6755
2. workers / interleave / seed -- `num_workers` 4 pinned, per-arm interleave,
                                  `random_seed` = the cell's solver seed
3. the cap BY TYPE AND VALUE   -- `base`/`il`: max_time_in_seconds = 15.0
                                  (machine-local); `det`: max_deterministic_time
                                  (publishable), wall cap dropped
4. N runs x which seeds        -- 12 seeds, 1000..1011, x 2 replicates, reported
                                  as a distribution
5. the machine                 -- `platform.processor()` in the meta block
6. the tolerance               -- exact equality on status, objective and Plan
                                  fingerprint; seconds are reported as a spread
                                  and asserted at nothing

Everything not named above is `sweep.py`'s, by import: the scenario cache, the
Envelope family, `run_one`, the validator, `T_INT`, `DOOR_MIN_ADR`, WORKERS,
`soft=("coverage",)` and the `mm_affine` / `erode=True` shipped rig. This file
adds the arm dimension and nothing else.

    python experiments/solver-toy/repeat_seeds.py [--seeds=12] [--limit=15.0]
                                                  [--rooms=8,12,24] [--tag=main]
                                                  [--arms=base,il,det]
    python experiments/solver-toy/repeat_seeds.py --selftest
"""

from __future__ import annotations

import argparse
import io
import json
import pathlib
import platform
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import sweep                                                     # noqa: E402
from solver import SolveConfig                                   # noqa: E402

RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)

# S7's design, at S2's scale. 1000 + k is S7's own numbering, kept so the two
# are comparable; the scenario seed stays at BASE_SEED in every cell.
SOLVER_SEED_BASE = 1000
N_SEEDS = 12                    # >= 10, the number the owed clause names
REPLICATES = 2                  # the determinism half: same cell, run twice
ROOMS = (8, 12, 24)             # the room counts Part I's headline table quotes
EXPOSURE = "corpus_median"      # the re-fitted p50 preset, project_join's own
TAU = 4                         # SHIPPED_TAU (C10), not S2's tau = 0
SIGMA = 0.5                     # every published run's Proposal noise

# `max_deterministic_time` is in OR-Tools' own units, not seconds, and the two
# are not convertible a priori. This budget is CALIBRATED, not guessed: arm
# `det` reads the deterministic time the `base` arm actually spent (recorded on
# every row as `dtime`) and takes its p90, so the deterministic arm is given a
# budget matched to what the wall-capped arm consumed rather than an invented
# one. `--dbudget` overrides it for a re-run without re-calibrating.
DET_BUDGET_PCT = 90

ARMS = {
    # name:  (interleave_search, uses max_deterministic_time)
    "base": (False, False),     # the configuration every published run used
    "il":   (True,  False),     # item 4: the flag priced at the same wall budget
    "det":  (True,  True),      # ADR 0043 decision 5's prescription, run at last
}


def cells(rooms, arms, seeds):
    for n in rooms:
        for arm in arms:
            for k in range(seeds):
                for rep in range(REPLICATES):
                    yield {"n": n, "arm": arm, "solver_seed": SOLVER_SEED_BASE + k,
                           "rep": rep}


def config_for(row, limit, dbudget):
    """The `SolveConfig` for one row. Split out so the selftest can compare it
    field-for-field against `sweep.execute`'s, which is a statement about the
    CONFIGURATION and is therefore deterministic -- comparing the two solves'
    output would not be, and that is the whole subject of this rig."""
    interleave, deterministic = ARMS[row["arm"]]
    return SolveConfig(
        workers=sweep.WORKERS, time_limit_s=limit, seed=row["solver_seed"],
        fix_relations=True, relation_confidence=row["tau"],
        soft=("coverage",), area_units=row["rig"], erode_minima=row["erode"],
        t_int_mm=sweep.T_INT,
        interleave_search=interleave,
        max_deterministic_time=dbudget if deterministic else None,
    )


def execute(cell, limit, dbudget):
    """One cell. `sweep.get_scenario` + `sweep.run_one`, verbatim and by import."""
    row = dict(cell)
    row.update(suite="R1", seed=sweep.BASE_SEED, exposure=EXPOSURE,
               rig="mm_affine", erode=True, tau=TAU, sigma=SIGMA, limit=limit,
               proposal="noisy", door_min=sweep.DOOR_MIN_ADR,
               workers=sweep.WORKERS)

    sc = sweep.get_scenario(row["n"], row["seed"], row["exposure"],
                            row["door_min"], row["sigma"], sweep.T_INT)
    row["gen_s"] = round(sc[4], 3)
    if sc[0] == "h8_dead":
        row["status"] = "H8_IMPOSSIBLE"
        return row
    if sc[0] != "ok":
        row["status"] = "NO_BRIEF"
        row["gen_error"] = sc[1]
        return row
    _, brief, truth, proposal, _ = sc

    cfg = config_for(row, limit, dbudget)
    interleave, deterministic = ARMS[row["arm"]]
    row["interleave"] = interleave
    # `results/README.md`: rows carry a wall-clock start so that a run taken
    # under CPU contention is DETECTABLE rather than invisible. This repo has
    # discarded a whole pass for want of it, and ticket 65's two concurrent
    # sweeps are the same failure one layer up.
    row["t_start"] = round(time.time(), 2)
    row["cap_type"] = ("max_deterministic_time" if deterministic
                       else "max_time_in_seconds")
    row["cap_value"] = dbudget if deterministic else limit
    row = sweep.run_one(row, brief, truth, proposal, cfg)
    # `run_one` keeps a 40-entry trace per row; this grid is 3 arms x 12 seeds x
    # 2 replicates and the traces are not read by the report.
    row.pop("trace", None)
    row.pop("drawing", None)
    return row


def selftest(limit=15.0):
    """Three statements before any timing.

    1. The flag reaches the solver. A `SolveConfig` carrying it produces a
       CpSolver whose `interleave_search` is set -- checked on the parameters
       object, because a typo'd protobuf field raises and a mis-plumbed one is
       silent.
    2. Both cap types are exclusive. Setting `max_deterministic_time` must leave
       `max_time_in_seconds` unset, or `DeterministicLoop` never runs.
    3. Arm `base` IS `sweep.execute`'s configuration at tau = 4, field for
       field on the `SolveConfig`. If this fails the rig is measuring something
       other than the shipped solver and nothing below repeats anything.

       ⚠️ It is asserted on the CONFIGURATION and deliberately not on the two
       solves' output. The first draft did assert the Plan and **it failed on
       its first run**: identical model, identical `random_seed` = 1000,
       identical 4 workers, same status and same objective -- and a different
       set of rectangles. That is not a defect in the rig, it is the
       measurement, arriving before the grid did. A selftest asserted on a
       stochastic output is a coin flip, so it asserts the inputs and REPORTS
       the output agreement as the first row of evidence.
    """
    from ortools.sat.python import cp_model
    for flag in (False, True):
        s = cp_model.CpSolver()
        s.parameters.interleave_search = flag
        assert s.parameters.interleave_search is flag
    print("  ok  interleave_search is a real parameter and round-trips")

    s = cp_model.CpSolver()
    s.parameters.max_deterministic_time = 1.0
    assert s.parameters.max_time_in_seconds == float("inf"), \
        "a wall cap left set alongside a deterministic budget destroys determinism"
    print("  ok  the two caps are exclusive on a fresh CpSolver")

    import dataclasses
    row = {"n": 8, "arm": "base", "solver_seed": SOLVER_SEED_BASE, "rep": 0,
           "tau": TAU, "rig": "mm_affine", "erode": True}
    mine = config_for(row, limit, None)
    theirs = SolveConfig(
        workers=sweep.WORKERS, time_limit_s=limit, seed=SOLVER_SEED_BASE,
        fix_relations=True, relation_confidence=TAU,
        soft=("coverage",), area_units="mm_affine", erode_minima=True,
        t_int_mm=sweep.T_INT,
    )
    diff = {f.name: (getattr(mine, f.name), getattr(theirs, f.name))
            for f in dataclasses.fields(SolveConfig)
            if getattr(mine, f.name) != getattr(theirs, f.name)}
    assert not diff, f"arm base is not sweep.execute's configuration: {diff}"
    print(f"  ok  arm base's SolveConfig == sweep.execute's, all "
          f"{len(dataclasses.fields(SolveConfig))} fields")

    a = execute(dict(row), limit, None)
    b = execute(dict(row, rep=1), limit, None)
    same = (a["status"] == b["status"], a["objective"] == b["objective"],
            a["plan"] == b["plan"])
    print(f"  --  two runs of ONE cell at seed {SOLVER_SEED_BASE}, 4 workers, "
          f"no interleave: status {'=' if same[0] else 'differs'}, "
          f"objective {'=' if same[1] else 'differs'}, "
          f"Plan {'=' if same[2] else 'DIFFERS'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=N_SEEDS)
    ap.add_argument("--limit", type=float, default=15.0)
    ap.add_argument("--rooms", default=",".join(str(n) for n in ROOMS))
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--dbudget", type=float, default=None)
    ap.add_argument("--tag", default="main")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(a.limit)
        return

    rooms = tuple(int(x) for x in a.rooms.split(","))
    arms = tuple(x for x in a.arms.split(","))
    for arm in arms:
        assert arm in ARMS, arm

    # `det` needs a budget in deterministic units, and it is read off `base`
    # rather than invented -- so `base` is always run first when both are asked
    # for. `--dbudget` short-circuits the calibration on a re-run.
    ordered = [x for x in ("base", "il", "det") if x in arms]
    out = RESULTS / f"repeat_seeds_{a.tag}.jsonl"
    # Rows are APPENDED and flushed, `arms_parts.py`'s lesson: a whole-list dump
    # per row loses everything back to the last complete write if the process
    # dies, and this grid is long enough for that to matter.
    jl = io.open(out, "a", encoding="utf-8")

    dbudget = a.dbudget
    rows, t0 = [], time.perf_counter()
    todo = list(cells(rooms, ordered, a.seeds))
    print(f"{len(todo)} cells: rooms {rooms}, arms {ordered}, "
          f"{a.seeds} solver seeds x {REPLICATES} replicates, "
          f"cap {a.limit} s wall", flush=True)

    for arm in ordered:
        if arm == "det" and dbudget is None:
            base_d = sorted(r["dtime"] for r in rows
                            if r["arm"] == "base" and r.get("dtime"))
            if not base_d:
                print("  skip det: no base rows to calibrate a budget from")
                continue
            dbudget = round(base_d[int(len(base_d) * DET_BUDGET_PCT / 100) - 1], 3)
            print(f"  det budget calibrated to base p{DET_BUDGET_PCT} "
                  f"deterministic time = {dbudget}", flush=True)
        for cell in [c for c in todo if c["arm"] == arm]:
            r = execute(cell, a.limit, dbudget)
            rows.append(r)
            el = time.perf_counter() - t0
            print(f"  {len(rows):>4}/{len(todo)} n={r['n']:<3} {r['arm']:<5} "
                  f"s={r['solver_seed']} r{r['rep']} {r['status']:<10} "
                  f"obj={r.get('objective')} {el:.0f}s", flush=True)
            jl.write(json.dumps(r) + "\n")
            jl.flush()
    jl.close()

    import ortools
    meta = {
        "ortools": getattr(ortools, "__version__", "unknown"),
        "machine": platform.processor(),
        "python": platform.python_version(),
        "workers": sweep.WORKERS, "seeds": a.seeds, "replicates": REPLICATES,
        "solver_seeds": [SOLVER_SEED_BASE + k for k in range(a.seeds)],
        "scenario_seed": sweep.BASE_SEED, "exposure": EXPOSURE, "tau": TAU,
        "sigma": SIGMA, "rooms": list(rooms), "arms": ordered,
        "wall_cap_s": a.limit, "det_budget": dbudget,
        "t_int_mm": sweep.T_INT, "rig": "mm_affine", "erode": True,
        "soft": ["coverage"], "rows": len(rows),
        "secs": round(time.perf_counter() - t0, 1),
    }
    json.dump(meta, io.open(RESULTS / f"repeat_seeds_meta_{a.tag}.json", "w",
                            encoding="utf-8"), indent=1)
    print(f"done: {len(rows)} rows in {meta['secs']:.0f}s -> {out.name}")


if __name__ == "__main__":
    main()
