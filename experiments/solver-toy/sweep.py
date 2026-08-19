"""Ticket 15 — the solver timing variance sweep.

Every published solver number came from one seed, on one machine, at 100 %
exterior exposure, with areas posted in grid units. This runs the same harness
across the axes the ticket names and writes one JSON row per solve.

    python sweep.py S1 S2 S3 S4 S5          # or `all`
    python sweep.py S2 --limit 15 --seeds 8

Rows land in `results/<suite>.jsonl` and the file is **resumable**: a row whose
key is already present is skipped, so an interrupted run is restarted by
re-issuing the same command.

Solves run strictly serially at `workers=4`, matching the published
measurements. Running them concurrently would be faster and would make every
timing meaningless.
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
from typing import Dict, Iterator, List, Optional, Tuple

import scenarios
from drawing_metrics import measure as drawing_measure
from frontage import budget as frontage_budget
from geometry import EXPOSURE_PRESETS
from scenarios import (
    GRID_MM,
    degenerate_proposal,
    envelope_for,
    make_brief,
    make_proposal,
    mm,
    shuffled_proposal,
)
from solver import SolveConfig, project
from validate import check

RESULTS = pathlib.Path(__file__).parent / "results"
RESULTS.mkdir(exist_ok=True)

# Bound the cost of a hostile scenario: 12 attempts x 10 s rather than 40 x 30.
scenarios.ASSIGN_TIME_LIMIT_S = 10.0
scenarios.ASSIGN_WORKERS = 4
scenarios.BRIEF_ATTEMPTS = 12

WORKERS = 4
BASE_SEED = 20260817

# annotation.md 14: t_int = 100. ADR 0004 requires it even.
T_INT = 100
# Ticket 15: the contact threshold is `structural opening width + t_int`, not
# the leaf width. The widest internal SO in the worked example is 900.
DOOR_MIN_ADR = mm(1.0)          # 1000 mm = 4 grid units
DOOR_MIN_LEGACY = mm(0.75)      # 750 mm = 3, what every published run used


# ---------------------------------------------------------------------------
# Scenario cache — building a Brief runs its own CP-SAT model, so a scenario is
# built once and reused across every rig, tau and time limit that shares it.
# ---------------------------------------------------------------------------

_CACHE: Dict[tuple, object] = {}


def get_scenario(n: int, seed: int, exposure: str, door_min: int, sigma_m: float,
                 clear_t: int = 0):
    """(brief, truth, proposal) or an exception describing why there is none.

    A generation failure is a result, not an error: under a low-exposure preset
    there may be no way to type a ground-truth tiling at all — every habitable
    room needs a window and there are not enough exterior faces to go round.
    """
    key = (n, seed, exposure, door_min, sigma_m, clear_t)
    if key in _CACHE:
        return _CACHE[key]
    t0 = time.perf_counter()
    fb = frontage_budget(n, exposure)
    if not fb["possible"]:
        # No tiling of this Envelope can satisfy H8 — the habitable rooms'
        # minimum dimensions sum past the whole exterior run. Nothing to solve,
        # and no seed or Proposal can change it.
        val = ("h8_dead",
               f"H8 frontage budget: need {fb['need_mm']} mm over "
               f"{fb['habitable']} habitable rooms, have {fb['have_mm']} mm",
               None, None, time.perf_counter() - t0)
        _CACHE[key] = val
        return val
    try:
        env = envelope_for(n, exposure)
        brief, truth, kinds = make_brief(
            f"{n}-room", env, n, seed, door_min, scenarios.WINDOW_MIN,
            clear_t=clear_t
        )
        proposal = make_proposal(truth, kinds, seed, sigma=mm(sigma_m))
        val = ("ok", brief, truth, proposal, time.perf_counter() - t0)
    except Exception as e:                    # noqa: BLE001 - a result, not a bug
        val = ("fail", str(e)[:200], None, None, time.perf_counter() - t0)
    _CACHE[key] = val
    return val


def row_key(r: dict) -> tuple:
    return tuple(r.get(k) for k in KEY_FIELDS)


KEY_FIELDS = ("suite", "n", "seed", "exposure", "rig", "erode", "tau",
              "sigma", "limit", "proposal", "door_min", "workers",
              # None means "use the scenario seed", which is what every suite
              # but S7 does. Kept nullable so adding S7 did not invalidate the
              # rows already on disk.
              "solver_seed")


def base_row(**kw) -> dict:
    r = {k: None for k in KEY_FIELDS}
    r["workers"] = WORKERS
    r.update(kw)
    return r


def run_one(row: dict, brief, truth, proposal, cfg: SolveConfig) -> dict:
    res = project(brief, proposal, cfg)
    row["status"] = res.status
    row["wall"] = round(res.wall_time_s, 4)
    row["build"] = round(res.build_time_s, 4)
    row["first"] = None if res.time_to_first is None else round(res.time_to_first, 4)
    w5 = res.time_to_within(5.0)
    row["within5"] = None if w5 is None else round(w5, 4)
    # A solution paying coverage slack costs at least one soft_weight, and the
    # corner objective is O(10^2-10^3), so "objective below one soft_weight" is
    # exactly "tiles the Envelope, and would pass the validator". This is the
    # product metric: when does a *survivor* exist, not when does CP-SAT first
    # return something.
    row["valid_at"] = next((round(t, 4) for t, o in res.trace
                            if o < cfg.soft_weight), None)
    row["slack"] = res.model_stats.get("cov_slack")
    # Fingerprint the Plan so distinct arrangements off one Proposal can be
    # counted without keeping every rectangle.
    row["plan"] = ("|".join(f"{r.x1},{r.y1},{r.x2},{r.y2}" for r in res.rooms)
                   if res.rooms else None)
    row["trace"] = [[round(t, 4), o] for t, o in res.trace][:40]
    row["improvements"] = len(res.trace)
    row["objective"] = res.objective
    row["vars"] = res.model_stats.get("variables")
    row["cons"] = res.model_stats.get("constraints")
    row["mults"] = res.model_stats.get("multiplications")
    row["fixed_relations"] = res.model_stats.get("fixed_relations")
    row["candidate_relations"] = res.model_stats.get("candidate_relations")
    row["core"] = res.infeasibility_core or None
    if res.rooms:
        v = check(brief, res.rooms)
        row["valid"] = bool(v["ok"])
        row["failures"] = v["failures"][:3] if not v["ok"] else None
        try:
            row["drawing"] = drawing_measure(res.rooms, brief.env, T_INT)
        except Exception as e:                # noqa: BLE001
            row["drawing"] = {"error": str(e)[:120]}
    else:
        row["valid"] = None
        row["failures"] = None
        row["drawing"] = None
    return row


# ---------------------------------------------------------------------------
# Suites
# ---------------------------------------------------------------------------


def suite_S1(limit: float, seeds: int) -> Iterator[dict]:
    """Formulation cost: grid units against ADR 0001's eroded millimetres.

    `erode=True` is the real thing and is a *tighter* feasible set as well as a
    numerically bigger one; `erode=False` relaxes the minima by t_int so the
    feasible set matches the grid rig exactly and the numeric cost is
    attributable on its own.
    """
    rigs = [("grid", False), ("mm_direct", False), ("mm_affine", False),
            ("mm_direct", True), ("mm_affine", True)]
    for n in (8, 12, 24):
        for s in range(seeds):
            for rig, erode in rigs:
                yield base_row(suite="S1", n=n, seed=BASE_SEED + s,
                               exposure="detached", rig=rig, erode=erode,
                               tau=0, sigma=0.5, limit=limit, proposal="noisy",
                               door_min=DOOR_MIN_ADR)


def suite_S2(limit: float, seeds: int) -> Iterator[dict]:
    """The main grid: room count against dwelling-type exposure, many seeds."""
    for n in (4, 6, 8, 10, 12, 16, 20, 24):
        for exposure in ("detached", "terrace_mid", "flat_corner",
                         "corpus_median", "flat_single_aspect"):
            for s in range(seeds):
                yield base_row(suite="S2", n=n, seed=BASE_SEED + s,
                               exposure=exposure, rig="mm_affine", erode=True,
                               tau=0, sigma=0.5, limit=limit, proposal="noisy",
                               door_min=DOOR_MIN_ADR)


def suite_S3(limit: float, seeds: int) -> Iterator[dict]:
    """Proposal quality: where does solve time turn over as the model degrades."""
    for n in (8, 12, 24):
        for sigma in (0.0, 0.25, 0.5, 1.0, 2.0, 4.0):
            for s in range(seeds):
                yield base_row(suite="S3", n=n, seed=BASE_SEED + s,
                               exposure="corpus_median", rig="mm_affine",
                               erode=True, tau=0, sigma=sigma, limit=limit,
                               proposal="noisy", door_min=DOOR_MIN_ADR)


def suite_S4(limit: float, seeds: int) -> Iterator[dict]:
    """tau: the confidence margin above which a Proposal relation is fixed hard."""
    for n in (8, 24):
        for exposure in ("detached", "corpus_median"):
            for tau in (0, 1, 2, 4, 6, 10):
                for s in range(seeds):
                    yield base_row(suite="S4", n=n, seed=BASE_SEED + s,
                                   exposure=exposure, rig="mm_affine",
                                   erode=True, tau=tau, sigma=0.5,
                                   limit=limit, proposal="noisy",
                                   door_min=DOOR_MIN_ADR)


def suite_S5(limit: float, seeds: int) -> Iterator[dict]:
    """The two known failure modes, and how reliably detection fires."""
    for n in (6, 8, 12, 16, 24):
        for kind in ("degenerate", "shuffled"):
            for s in range(seeds):
                yield base_row(suite="S5", n=n, seed=BASE_SEED + s,
                               exposure="corpus_median", rig="mm_affine",
                               erode=True, tau=0, sigma=0.5, limit=limit,
                               proposal=kind, door_min=DOOR_MIN_ADR)


def suite_S6(limit: float, seeds: int) -> Iterator[dict]:
    """Worker scaling — the only half of the hardware axis this machine can answer.

    No modern CPU was available, so a "modern-CPU figure" cannot be reported
    honestly. What can be measured is how much of the win comes from cores, on
    the same 4-core Ivy Bridge every published number came from.
    """
    for n in (8, 12, 24):
        for w in (1, 2, 4):
            for s in range(seeds):
                yield base_row(suite="S6", n=n, seed=BASE_SEED + s,
                               exposure="corpus_median", rig="mm_affine",
                               erode=True, tau=0, sigma=0.5, limit=limit,
                               proposal="noisy", door_min=DOOR_MIN_ADR,
                               workers=w)


def suite_S7(limit: float, seeds: int) -> Iterator[dict]:
    """Valid Plans per *Proposal* against tau — the diversity half of the trade.

    S4 varies the scenario, so each of its rows is a different Proposal and it
    can only report a rate. Here the Proposal is held fixed and only CP-SAT's
    own random seed moves, so distinct Plans off one Proposal can be counted.
    That is what "high tau leaves more arrangements alive" has to mean if it is
    to be measured rather than asserted.
    """
    for n in (8, 24):
        for tau in (0, 1, 2, 4, 6, 10):
            for k in range(seeds):
                yield base_row(suite="S7", n=n, seed=BASE_SEED,
                               exposure="corpus_median", rig="mm_affine",
                               erode=True, tau=tau, sigma=0.5, limit=limit,
                               proposal="noisy", door_min=DOOR_MIN_ADR,
                               solver_seed=1000 + k)


def suite_S8(limit: float, seeds: int) -> Iterator[dict]:
    """Does tau rescue a noisy Proposal? The interaction S3 made urgent.

    S3 found the recommended configuration goes INFEASIBLE between sigma 0.5 and
    1.0 m of per-corner noise — and 0.5 m is what every published run used, so
    v1 sits one notch below a cliff. tau is the only knob that touches it:
    relations are the sole route by which the Proposal reaches a constraint, so
    fixing fewer of them should buy noise tolerance back. This measures the
    exchange rate.
    """
    for n in (8, 24):
        for sigma in (0.5, 1.0, 2.0, 4.0):
            for tau in (0, 2, 4, 6, 10, 16):
                for k in range(seeds):
                    yield base_row(suite="S8", n=n, seed=BASE_SEED + k,
                                   exposure="corpus_median", rig="mm_affine",
                                   erode=True, tau=tau, sigma=sigma,
                                   limit=limit, proposal="noisy",
                                   door_min=DOOR_MIN_ADR)


SUITES = {"S1": suite_S1, "S2": suite_S2, "S3": suite_S3,
          "S4": suite_S4, "S5": suite_S5, "S6": suite_S6, "S7": suite_S7,
          "S8": suite_S8}

# The main grid carries the percentile claims, so it gets the most seeds.
SEED_DEFAULTS = {"S1": 6, "S2": 8, "S3": 5, "S4": 5, "S5": 6, "S6": 5,
                 "S7": 4, "S8": 4}


# ---------------------------------------------------------------------------


def execute(row: dict) -> dict:
    # The ground truth has to satisfy whatever reading the solver will enforce,
    # or it stops being a witness and a NO_BRIEF is indistinguishable from a
    # solver failure.
    sc = get_scenario(row["n"], row["seed"], row["exposure"],
                      row["door_min"], row["sigma"],
                      T_INT if row["erode"] else 0)
    row["gen_s"] = round(sc[4], 3)
    if sc[0] == "h8_dead":
        row["status"] = "H8_IMPOSSIBLE"
        row["gen_error"] = sc[1]
        return row
    if sc[0] != "ok":
        row["status"] = "NO_BRIEF"
        row["gen_error"] = sc[1]
        return row
    _, brief, truth, proposal, _ = sc

    if row["proposal"] == "degenerate":
        proposal = degenerate_proposal(truth, proposal.kinds)
        fix = False
    elif row["proposal"] == "shuffled":
        proposal = shuffled_proposal(truth, proposal.kinds, row["seed"])
        fix = True
    else:
        fix = True

    cfg = SolveConfig(
        workers=row["workers"], time_limit_s=row["limit"],
        seed=row["seed"] if row.get("solver_seed") is None else row["solver_seed"],
        fix_relations=fix, relation_confidence=row["tau"],
        soft=("coverage",), area_units=row["rig"], erode_minima=row["erode"],
        t_int_mm=T_INT,
    )
    return run_one(row, brief, truth, proposal, cfg)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("suites", nargs="+")
    ap.add_argument("--limit", type=float, default=15.0)
    ap.add_argument("--seeds", type=int, default=0,
                    help="override the per-suite default seed count")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()

    names = list(SUITES) if a.suites == ["all"] else a.suites
    host = {"cpu": platform.processor(), "cores": os.cpu_count(),
            "python": sys.version.split()[0], "workers": WORKERS,
            "machine": platform.node()}

    for name in names:
        out = RESULTS / f"{name}{a.tag}.jsonl"
        done = set()
        if out.exists():
            for line in out.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    try:
                        done.add(row_key(json.loads(line)))
                    except Exception:      # noqa: BLE001
                        pass
        seeds = a.seeds or SEED_DEFAULTS.get(name, 6)
        rows = list(SUITES[name](a.limit, seeds))
        todo = [r for r in rows if row_key(r) not in done]
        print(f"[{name}] {len(rows)} rows, {len(rows)-len(todo)} done, "
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
                print(f"  [{name} {i}/{len(todo)}] n={row['n']} "
                      f"{row['exposure']} {row['rig']}/{row['erode']} "
                      f"tau={row['tau']} sig={row['sigma']} w={row['workers']} "
                      f"{row['proposal']} -> {row['status']} "
                      f"first={row.get('first')} valid_at={row.get('valid_at')} "
                      f"valid={row.get('valid')} | {el/60:.1f} min",
                      flush=True)
        print(f"[{name}] done in {(time.perf_counter()-t0)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
