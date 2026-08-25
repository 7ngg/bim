"""Ticket 29 — the non-guillotine sweep, and the t_int re-base that rides along.

Every one of the 965 solves behind `docs/research/solver-formulation.md` Part II
had a **guillotine** ground truth, because `scenarios.ground_truth` is a
recursive guillotine dissection. 6.27 % of real converted dwellings are not
guillotine, rising to ~15 % at 8-10 rooms, and none of that class has ever been
solved here.

This runs the published harness twice over the same Envelopes, same room mixes,
same seeds and the same Proposal noise, changing **only the cut structure of the
target**, and reports the pinwheel arm against the guillotine baseline.

    python sweep_ng.py A B C T          # or `all`
    python sweep_ng.py A --seeds 3

    A  the main grid: room count x exposure x truth, at the shipped tau = 4
    B  tau: does 4 survive a denser relation graph?
    C  sigma: does the feasibility cliff move?
    T  t_int: the inherited second sweep, 100 against the shipped 150

Rows land in `results/N9<suite>.jsonl`, resumable exactly like `sweep.py`.
Solves run strictly serially at `workers = 4`, matching every published number.

**The pairing is the point.** A guillotine and a pinwheel tiling of one Envelope
are different Briefs — the required and forbidden adjacencies are read off the
truth — so the arms cannot be identical and should not be. What is held fixed is
everything a solve time could otherwise be blamed on: Envelope, room mix, seed,
noise, config. Every row carries the structural covariates
(`pinwheel.tiling_structure`) so a difference can be attributed rather than only
observed.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import platform
import sys
import time
import traceback
from typing import Dict, Iterator, List, Tuple

import pinwheel
import scenarios
from geometry import Envelope
from scenarios import GRID_MM, envelope_for, make_brief, make_proposal, mm
from solver import SolveConfig, project
from validate import check

RESULTS = pathlib.Path(__file__).parent / "results"
RESULTS.mkdir(exist_ok=True)

scenarios.ASSIGN_TIME_LIMIT_S = 10.0
scenarios.ASSIGN_WORKERS = 4
scenarios.BRIEF_ATTEMPTS = 12

WORKERS = 4
BASE_SEED = 20260817
DOOR_MIN_ADR = mm(1.0)

# What every published solver number was actually fitted at. `sweep.py` line 59
# and `solver.SolveConfig.t_int_mm` both say 100 -- NOT the 120 that was the AZ
# profile's value at the time. ADR 0010 ships 150. Suite T measures the move
# that was really made: 100 -> 150.
T_INT_PUBLISHED = 100
T_INT_SHIPPED = 150

# The shipped configuration, C10: 15 s, tau = 4.
SHIPPED_LIMIT = 15.0
SHIPPED_TAU = 4

# Below 7 rooms this Envelope family has no non-guillotine tiling to offer: the
# L's notch forces the second part to hold two rooms, leaving the main part four
# or fewer, and every tiling of a rectangle into four rectangles is guillotine.
# Measured, not assumed -- `python pinwheel.py`.
COUNTS = (7, 8, 10, 12, 16, 20, 24)


# ---------------------------------------------------------------------------
# Scenario cache, keyed on the truth arm as well
# ---------------------------------------------------------------------------

_CACHE: Dict[tuple, tuple] = {}


def get_scenario(n: int, seed: int, exposure: str, truth_kind: str,
                 door_min: int, sigma_m: float, clear_t: int):
    """(status, brief, truth, proposal, gen_s, structure).

    A generation failure is a result, not an error. `no_pinwheel` is its own
    status because "this Envelope admits no non-guillotine tiling" is a
    different fact from "no Brief could be typed over one".
    """
    key = (n, seed, exposure, truth_kind, door_min, sigma_m, clear_t)
    if key in _CACHE:
        return _CACHE[key]
    t0 = time.perf_counter()
    try:
        env = envelope_for(n, exposure)
        if truth_kind == "pinwheel":
            brief, truth, kinds = pinwheel.make_brief_pinwheel(
                f"{n}-room-pin", env, n, seed, door_min, scenarios.WINDOW_MIN,
                clear_t=clear_t)
        else:
            brief, truth, kinds = make_brief(
                f"{n}-room", env, n, seed, door_min, scenarios.WINDOW_MIN,
                clear_t=clear_t)
        proposal = make_proposal(truth, kinds, seed, sigma=mm(sigma_m))
        st = pinwheel.tiling_structure(truth, door_min)
        st["is_guillotine"] = pinwheel.is_guillotine(truth)
        # The harness's central guarantee: the truth is a witness. If it is not,
        # a failure to solve stops being a fact about the projection problem.
        wit = check(brief, list(truth))
        st["truth_valid"] = bool(wit["ok"])
        st["truth_failures"] = None if wit["ok"] else wit["failures"][:3]
        val = ("ok", brief, truth, proposal, time.perf_counter() - t0, st)
    except Exception as e:                    # noqa: BLE001 - a result, not a bug
        msg = str(e)[:200]
        status = "no_pinwheel" if "non-guillotine" in msg else "fail"
        val = (status, msg, None, None, time.perf_counter() - t0, None)
    _CACHE[key] = val
    return val


KEY_FIELDS = ("suite", "n", "seed", "exposure", "truth", "tau", "sigma",
              "limit", "t_int", "workers")


def base_row(**kw) -> dict:
    r = {k: None for k in KEY_FIELDS}
    r["workers"] = WORKERS
    r["exposure"] = "corpus_median"
    r["sigma"] = 0.5
    r["limit"] = SHIPPED_LIMIT
    r["tau"] = SHIPPED_TAU
    r["t_int"] = T_INT_PUBLISHED
    r.update(kw)
    return r


def row_key(r: dict) -> tuple:
    return tuple(r.get(k) for k in KEY_FIELDS)


# ---------------------------------------------------------------------------
# Suites
# ---------------------------------------------------------------------------

TRUTHS = ("guillotine", "pinwheel")


def suite_A(seeds: int) -> Iterator[dict]:
    """The main grid. Room count x exposure x truth, shipped config.

    Two exposures rather than five: `detached` is what every published timing
    was measured at and `corpus_median` is what a real flat is. The other three
    add rows without adding a question this ticket asks.
    """
    for n in COUNTS:
        for exposure in ("detached", "corpus_median"):
            for truth in TRUTHS:
                for s in range(seeds):
                    yield base_row(suite="A", n=n, seed=BASE_SEED + s,
                                   exposure=exposure, truth=truth)


def suite_B(seeds: int) -> Iterator[dict]:
    """tau. A pinwheel's relation graph is denser, so tau -- the valve on
    relation-hardness -- is where movement is specifically expected."""
    for n in (8, 12, 24):
        for truth in TRUTHS:
            for tau in (0, 1, 2, 4, 6, 10):
                for s in range(seeds):
                    yield base_row(suite="B", n=n, seed=BASE_SEED + s,
                                   truth=truth, tau=tau)


def suite_C(seeds: int) -> Iterator[dict]:
    """sigma. Part II found the shipped 0.5 m sits one notch below a
    feasibility cliff. Does a non-guillotine target move the edge?"""
    for n in (8, 24):
        for truth in TRUTHS:
            for sigma in (0.0, 0.25, 0.5, 1.0, 2.0):
                for s in range(seeds):
                    yield base_row(suite="C", n=n, seed=BASE_SEED + s,
                                   truth=truth, sigma=sigma)


def suite_T(seeds: int) -> Iterator[dict]:
    """t_int, the inherited sweep. 100 (what was published) against 150 (what
    ADR 0010 ships), on both truth arms so the two changes cannot confound."""
    for n in COUNTS:
        for t_int in (T_INT_PUBLISHED, T_INT_SHIPPED):
            for truth in TRUTHS:
                for s in range(seeds):
                    yield base_row(suite="T", n=n, seed=BASE_SEED + s,
                                   truth=truth, t_int=t_int)


def suite_D(seeds: int) -> Iterator[dict]:
    """The top of the range at 30 s, because that is where the arms differ.

    Suite A runs at the shipped 15 s. Part II ran at 30 s and derived 15 from
    the traces, so A's rows cannot answer "would it have got there with longer".
    At 20 and 24 rooms both arms mostly fail on coverage slack rather than
    infeasibility, and the residual slack is small — a few cells of unassigned
    floor — so whether the pinwheel arm is slower or simply worse is exactly the
    question 30 s settles.
    """
    for n in (20, 24):
        for exposure in ("detached", "corpus_median"):
            for truth in TRUTHS:
                for s in range(seeds):
                    yield base_row(suite="D", n=n, seed=BASE_SEED + s,
                                   exposure=exposure, truth=truth, limit=30.0)


def suite_E(seeds: int) -> Iterator[dict]:
    """sigma again, in the band where the question can actually be answered.

    Suite C picked n = 8 and 24 to match Part II's own sigma grid, and both are
    useless here: 8 admits no pinwheel on this Envelope family, and 24 fails in
    both arms at every sigma above 0.25, so the treatment has nowhere to show.
    C is kept rather than deleted -- its n = 24 rows do locate the cliff between
    0.25 and 0.5 in *both* arms -- and this is the suite that carries the
    finding.
    """
    for n in (10, 12, 16):
        for truth in TRUTHS:
            for sigma in (0.25, 0.5, 1.0, 2.0):
                for s in range(seeds):
                    yield base_row(suite="E", n=n, seed=BASE_SEED + s,
                                   truth=truth, sigma=sigma)


SUITES = {"A": suite_A, "B": suite_B, "C": suite_C, "T": suite_T,
          "D": suite_D, "E": suite_E}
SEED_DEFAULTS = {"A": 5, "B": 3, "C": 4, "T": 4, "D": 4, "E": 4}


# ---------------------------------------------------------------------------


def execute(row: dict) -> dict:
    t_int = row["t_int"]
    sc = get_scenario(row["n"], row["seed"], row["exposure"], row["truth"],
                      DOOR_MIN_ADR, row["sigma"], t_int)
    row["gen_s"] = round(sc[4], 3)
    if sc[0] != "ok":
        row["status"] = ("NO_PINWHEEL" if sc[0] == "no_pinwheel"
                         else "NO_BRIEF")
        row["gen_error"] = sc[1]
        return row
    _, brief, truth, proposal, _, st = sc
    row["structure"] = st

    cfg = SolveConfig(
        workers=row["workers"], time_limit_s=row["limit"], seed=row["seed"],
        fix_relations=True, relation_confidence=row["tau"],
        soft=("coverage",), area_units="mm_affine", erode_minima=True,
        t_int_mm=t_int,
    )
    res = project(brief, proposal, cfg)
    row["status"] = res.status
    row["wall"] = round(res.wall_time_s, 4)
    row["build"] = round(res.build_time_s, 4)
    row["first"] = None if res.time_to_first is None else round(res.time_to_first, 4)
    row["valid_at"] = next((round(t, 4) for t, o in res.trace
                            if o < cfg.soft_weight), None)
    row["slack"] = res.model_stats.get("cov_slack")
    row["objective"] = res.objective
    row["vars"] = res.model_stats.get("variables")
    row["cons"] = res.model_stats.get("constraints")
    row["fixed_relations"] = res.model_stats.get("fixed_relations")
    row["candidate_relations"] = res.model_stats.get("candidate_relations")
    row["core"] = res.infeasibility_core or None
    if res.rooms:
        v = check(brief, res.rooms)
        row["valid"] = bool(v["ok"])
        row["failures"] = v["failures"][:3] if not v["ok"] else None
    else:
        row["valid"] = None
        row["failures"] = None
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("suites", nargs="+")
    ap.add_argument("--seeds", type=int, default=0)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()

    names = list(SUITES) if a.suites == ["all"] else a.suites
    host = {"cpu": platform.processor(), "cores": os.cpu_count(),
            "python": sys.version.split()[0], "workers": WORKERS,
            "machine": platform.node()}

    for name in names:
        out = RESULTS / f"N9{name}{a.tag}.jsonl"
        done = set()
        if out.exists():
            for line in out.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    try:
                        done.add(row_key(json.loads(line)))
                    except Exception:          # noqa: BLE001
                        pass
        seeds = a.seeds or SEED_DEFAULTS.get(name, 4)
        rows = list(SUITES[name](seeds))
        todo = [r for r in rows if row_key(r) not in done]
        print(f"[N9{name}] {len(rows)} rows, {len(rows)-len(todo)} done, "
              f"{len(todo)} to run -> {out}", flush=True)
        t0 = time.perf_counter()
        with out.open("a", encoding="utf-8") as fh:
            for i, row in enumerate(todo, 1):
                row["host"] = host
                row["t_start"] = round(time.time(), 2)
                try:
                    row = execute(row)
                except Exception:              # noqa: BLE001
                    row["status"] = "HARNESS_ERROR"
                    row["gen_error"] = traceback.format_exc()[-400:]
                fh.write(json.dumps(row) + "\n")
                fh.flush()
                el = time.perf_counter() - t0
                print(f"  [N9{name} {i}/{len(todo)}] n={row['n']} "
                      f"{row['exposure']} {row['truth']} tau={row['tau']} "
                      f"sig={row['sigma']} t={row['t_int']} "
                      f"-> {row['status']} first={row.get('first')} "
                      f"valid_at={row.get('valid_at')} "
                      f"valid={row.get('valid')} | {el/60:.1f} min", flush=True)
        print(f"[N9{name}] done in {(time.perf_counter()-t0)/60:.1f} min",
              flush=True)


if __name__ == "__main__":
    main()
