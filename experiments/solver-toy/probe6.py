"""Ticket 24 — does confident-wrong actually predict solve failure?

The arrangement metric (`docs/spec/proposer.md` 5) is a proxy for "will the
solver project this Proposal". It has never been tested. This probe tests it the
only way a proxy can be tested: take Proposals the solver is *known* to project,
inject the defect at known doses, and see whether failure follows the dose.

Six suites, and each one answers a different half of the question.

  A   dose-response. Proposal = the ground truth exactly, so the geometry, the
      objective and the hint are all perfect and the ONLY corrupted channel is
      the relation set. Flip k of the truth's own relations to a direction the
      truth does not hold. Guarded, i.e. the shipping solver's acyclicity guard
      still runs.
  A2  the same, unguarded. Prices the guard: the difference between A and A2 is
      everything the cycle half of the metric could possibly be worth.
  A3  does the KIND of wrongness matter — a same-axis reversal against a
      cross-axis flip?
  B   abstain. Drop k relations instead of flipping them, because an abstained
      pair is exactly one the solver is left free on. 5.2 claims abstain is the
      cheap failure and confident-wrong the expensive one; f = 1.0 drops every
      relation, which is the unamended C10 form ticket 4 refuted.
  C   realistic noise. No injection at all: the shipped configuration on
      Proposals corrupted the way `make_proposal` corrupts them, over the sigma
      range ticket 15 swept. Ties the injected dose-response back to the thing
      a real Proposer emits, and re-derives ticket 15's INFEASIBLE cliff in the
      metric's own units.
  D   forced cycles. A directed cycle posted unguarded. The only way to see one,
      since the extractor cannot produce one.

Rows land in `results/P6.jsonl`, resumable: a row whose key is already on disk
is skipped, so the file can be topped up after an interrupt.

    python probe6.py                 # everything, in answer-first order
    python probe6.py --suite A C     # a subset
    python probe6.py --seeds 3       # cheaper
"""

from __future__ import annotations

import argparse
import json
import pathlib
import random
import sys
import time
import zlib
from typing import Dict, Iterator, List, Tuple

import arrangement as A
import scenarios
from scenarios import (
    DEFAULT_SEED,
    Proposal,
    envelope_for,
    make_brief,
    make_proposal,
    mm,
)
from solver import SolveConfig, extract_relations, project
from validate import check

RESULTS = pathlib.Path(__file__).parent / "results"

# ---------------------------------------------------------------------------
# The shipped configuration, per ticket 15: 15 s, tau = 4, coverage soft.
# Everything here is measured at it, because the ticket validates the metric's
# SHAPE at whatever tau the toy already uses. Fitting tau is ticket 15's job.
# ---------------------------------------------------------------------------
TAU = 4
LIMIT = 15.0
WORKERS = 4
SOFT = ("coverage",)
SOFT_WEIGHT = 100_000
EXPOSURE = "detached"          # what every published timing used
ROOM_COUNTS = (8, 12, 24)

KEY_FIELDS = ("suite", "n", "seed", "k", "mode", "guarded", "sigma", "cyclen",
              "drop", "tau")

# The per-row RNG seed is derived from these and these MUST NOT CHANGE — every
# recorded row's injected flips depend on them. They were `KEY_FIELDS` once,
# which was a mistake: adding `tau` for suite C2 silently re-drew every suite-A
# flip, so `results/P6.jsonl` (taken before) and `results/P6_verify.jsonl`
# (after) are two *independent samples* rather than one repeated run. Frozen
# here as a literal so a re-run reproduces `P6_verify.jsonl` exactly. Add a new
# suite dimension by extending KEY_FIELDS only.
RNG_FIELDS = ("suite", "n", "seed", "k", "mode", "guarded", "sigma", "cyclen",
              "drop", "tau")


def cfg_free() -> SolveConfig:
    """The shipped config with the extractor OFF — we post the relations."""
    return SolveConfig(time_limit_s=LIMIT, workers=WORKERS, soft=SOFT,
                       soft_weight=SOFT_WEIGHT, fix_relations=False,
                       relation_confidence=TAU, diagnose=False)


def cfg_shipped() -> SolveConfig:
    """The shipped config exactly, extractor ON. Suite C only."""
    return SolveConfig(time_limit_s=LIMIT, workers=WORKERS, soft=SOFT,
                       soft_weight=SOFT_WEIGHT, fix_relations=True,
                       relation_confidence=TAU, diagnose=False)


# ---------------------------------------------------------------------------
# Scenario cache. Building a Brief runs its own CP-SAT model.
# ---------------------------------------------------------------------------

_CACHE: Dict[tuple, object] = {}


def get(n: int, seed: int, exposure: str = EXPOSURE,
        door_min: int = None, clear_t: int = 0):
    door_min = scenarios.DOOR_MIN if door_min is None else door_min
    key = (n, seed, exposure, door_min, clear_t)
    if key not in _CACHE:
        env = envelope_for(n, exposure)
        brief, truth, kinds = make_brief(
            f"{n}-room", env, n, seed, door_min, scenarios.WINDOW_MIN,
            clear_t=clear_t)
        _CACHE[key] = (brief, truth, kinds)
    return _CACHE[key]


# ---------------------------------------------------------------------------
# Ticket 15's shipped rig, for suite C2 only. Everything else runs the rig the
# injection suites share, so that they stay comparable to each other; C2 exists
# to state the metric in the configuration that actually ships.
# ---------------------------------------------------------------------------
T_INT = 100
SHIPPED = dict(exposure="corpus_median", door_min=4, area_units="mm_affine",
               erode_minima=True, t_int_mm=T_INT)


def truth_proposal(truth, kinds, seed) -> Proposal:
    """A Proposal that IS the truth. sigma = 0 puts zero on every corner."""
    return make_proposal(truth, kinds, seed, sigma=0, label="truth")


# ---------------------------------------------------------------------------
# One run
# ---------------------------------------------------------------------------


def record(row: dict, res, brief, truth, posted, cfg) -> dict:
    row["status"] = res.status
    row["wall"] = round(res.wall_time_s, 4)
    row["build"] = round(res.build_time_s, 4)
    row["first"] = None if res.time_to_first is None else round(res.time_to_first, 4)
    # A Plan paying coverage slack costs at least one soft_weight and the corner
    # objective is O(10^2-10^3), so "objective below soft_weight" is exactly
    # "tiles the Envelope, and would survive the Acceptance bar". Ticket 15's
    # definition, kept so the numbers are comparable.
    row["valid_at"] = next((round(t, 4) for t, o in res.trace
                            if o < cfg.soft_weight), None)
    row["survivor"] = row["valid_at"] is not None
    row["objective"] = res.objective
    row["improvements"] = len(res.trace)
    row["core"] = res.infeasibility_core or None
    row["posted"] = len(posted)
    # The dose that actually reached the model, measured against the truth
    # geometry rather than assumed from k: a "wrong" direction can still be one
    # the truth happens to satisfy.
    row["violated_posted"] = sum(
        1 for axis, a, b in posted if A.sep_cost(truth, axis, a, b) > 0)
    if res.rooms:
        v = check(brief, res.rooms)
        row["valid"] = bool(v["ok"])
        row["failures"] = v["failures"][:3] if not v["ok"] else None
    else:
        row["valid"] = None
        row["failures"] = None
    return row


def base_row(**kw) -> dict:
    r = {k: None for k in KEY_FIELDS}
    r.update(kw)
    return r


def execute(row: dict) -> dict:
    n, seed = row["n"], row["seed"]
    brief, truth, kinds = get(n, seed)
    suite = row["suite"]
    # zlib.crc32, not hash(): PYTHONHASHSEED randomises str hashing per process,
    # which would make a resumed run disagree with the rows already on disk.
    rng = random.Random(zlib.crc32(
        "|".join(str(row.get(f)) for f in RNG_FIELDS).encode()))

    if suite == "C2":
        brief, truth, kinds = get(n, seed, SHIPPED["exposure"],
                                  SHIPPED["door_min"], T_INT)
        tau = row["tau"]
        prop = make_proposal(truth, kinds, seed, sigma=mm(row["sigma"]))
        cfg = SolveConfig(
            time_limit_s=LIMIT, workers=WORKERS, soft=SOFT,
            soft_weight=SOFT_WEIGHT, fix_relations=True, diagnose=False,
            relation_confidence=tau, area_units=SHIPPED["area_units"],
            erode_minima=SHIPPED["erode_minima"], t_int_mm=T_INT)
        row.update(A.measure(prop.boxes, truth, tau).as_row())
        posted, _ab, _cy = extract_relations(prop.boxes, tau)
        return record(row, project(brief, prop, cfg), brief, truth, posted, cfg)

    if suite == "C":
        prop = make_proposal(truth, kinds, seed, sigma=mm(row["sigma"]))
        cfg = cfg_shipped()
        m = A.measure(prop.boxes, truth, TAU)
        row.update(m.as_row())
        posted, _abst, _cyc = extract_relations(prop.boxes, TAU)
        res = project(brief, prop, cfg)
        return record(row, res, brief, truth, posted, cfg)

    prop = truth_proposal(truth, kinds, seed)
    base, _abst, _cyc = extract_relations(truth, TAU)
    row["base"] = len(base)
    cfg = cfg_free()

    if suite in ("A", "A2", "A3"):
        posted, drops, _flipped = A.inject_wrong(
            base, row["k"], rng, n, mode=row["mode"], guarded=row["guarded"])
        row["cycle_drops"] = drops
    elif suite in ("B", "B2"):
        posted = A.inject_abstain(base, row["k"], rng)
        row["cycle_drops"] = 0
        if suite == "B2":
            # Suite B measures abstain with the Proposal set to the truth, so
            # CP-SAT is *hinted with the answer* and dropping relations costs
            # almost nothing. That makes B's "abstain is free" partly an
            # artefact of the hint rather than a fact about relations. B2 turns
            # the hint off; the objective still pulls toward the Proposal,
            # because that is C10's design and not a confound.
            cfg.hint = False
    elif suite == "E":
        # Causation, not correlation. Two counterfactuals per dose:
        #   sufficient — post ONLY the flipped relations. If that alone is
        #                infeasible, nothing else is needed to explain the
        #                failure.
        #   necessary  — post the full set with the flipped ones DELETED, which
        #                is what abstaining on those pairs would have done. If
        #                that is feasible, the flips are what killed it.
        # CP-SAT's own assumption core is also recorded, and it is not minimal:
        # it comes back as the entire relation set at every size, which is why
        # it cannot answer this on its own.
        posted, drops, flipped = A.inject_wrong(
            base, row["k"], rng, n, mode="any", guarded=True)
        flipped_set = set(flipped)
        row["cycle_drops"] = drops
        row["posted"] = len(posted)
        row["flipped"] = len(flipped_set)
        row["violated_posted"] = sum(
            1 for axis, a, b2 in posted if A.sep_cost(truth, axis, a, b2) > 0)
        full = A.project_with(brief, prop, posted, cfg)
        row["status"] = full.status
        row["wall"] = round(full.wall_time_s, 4)
        row["valid_at"] = next((round(t, 4) for t, o in full.trace
                                if o < cfg.soft_weight), None)
        row["survivor"] = row["valid_at"] is not None
        only = [r for r in posted if r in flipped_set]
        without = [r for r in posted if r not in flipped_set]
        row["suff_status"] = (A.project_with(brief, prop, only, cfg).status
                              if n <= 12 else "SKIP")
        wres = A.project_with(brief, prop, without, cfg)
        row["nec_status"] = wres.status
        row["nec_valid_at"] = next((round(t, 4) for t, o in wres.trace
                                    if o < cfg.soft_weight), None)
        b = A.blame(brief, prop, posted, cfg)
        row["core_size"] = None if b["core"] is None else len(b["core"])
        return row
    elif suite == "F":
        kept = A.inject_abstain(base, row["drop"], rng)
        posted, drops, _flipped = A.inject_wrong(
            kept, row["k"], rng, n, mode="any", guarded=True)
        row["cycle_drops"] = drops
    elif suite == "D":
        posted = A.make_cycle(base, row["cyclen"], rng, n)
        row["cycle_drops"] = 0
        if posted is None:
            row["status"] = "SKIP"
            return row
    else:
        raise ValueError(suite)

    res = A.project_with(brief, prop, posted, cfg)
    return record(row, res, brief, truth, posted, cfg)


# ---------------------------------------------------------------------------
# Suites
# ---------------------------------------------------------------------------

DOSES = (0, 1, 2, 3, 4, 6, 8, 12, 16, 24)


def suite_A(seeds: int) -> Iterator[dict]:
    for n in ROOM_COUNTS:
        for s in range(seeds):
            for k in DOSES:
                yield base_row(suite="A", n=n, seed=DEFAULT_SEED + s, k=k,
                               mode="any", guarded=True)


def suite_C(seeds: int) -> Iterator[dict]:
    for n in ROOM_COUNTS:
        for s in range(seeds):
            for sigma in (0.0, 0.25, 0.5, 0.75, 1.0, 1.5):
                yield base_row(suite="C", n=n, seed=DEFAULT_SEED + s,
                               sigma=sigma)


def suite_C2(seeds: int) -> Iterator[dict]:
    """The metric against ticket 15's own cliff, at ticket 15's own rig.

    S3 measured 5 of 5 INFEASIBLE at 24 rooms at sigma 1.0 m and 3 of 5 at 12
    rooms at sigma 0.5 m — both at **tau = 0**, before tau was fitted. S8 then
    showed tau = 4 halves that. If the metric is real, one number should explain
    both knobs: raising tau and lowering sigma should buy survival through the
    same channel, the count of violated relations that reach the model.
    """
    for n in ROOM_COUNTS:
        for s in range(seeds):
            for sigma in (0.25, 0.5, 1.0, 2.0):
                for tau in (0, 4):
                    yield base_row(suite="C2", n=n, seed=DEFAULT_SEED + s,
                                   sigma=sigma, tau=tau)


def suite_B(seeds: int) -> Iterator[dict]:
    for n in ROOM_COUNTS:
        for s in range(seeds):
            base = len(extract_relations(get(n, DEFAULT_SEED + s)[1], TAU)[0])
            for f in (0.0, 0.1, 0.25, 0.5, 0.75, 1.0):
                yield base_row(suite="B", n=n, seed=DEFAULT_SEED + s,
                               k=round(f * base), mode=f"drop{f}", guarded=True)


def suite_B2(seeds: int) -> Iterator[dict]:
    """Suite B without the solution hint. See the note in `execute`."""
    for n in ROOM_COUNTS:
        for s in range(seeds):
            base = len(extract_relations(get(n, DEFAULT_SEED + s)[1], TAU)[0])
            for f in (0.0, 0.1, 0.25, 0.5, 0.75, 1.0):
                yield base_row(suite="B2", n=n, seed=DEFAULT_SEED + s,
                               k=round(f * base), mode=f"drop{f}", guarded=True)


def suite_A2(seeds: int) -> Iterator[dict]:
    for n in ROOM_COUNTS:
        for s in range(min(seeds, 3)):
            for k in (2, 4, 8, 16):
                yield base_row(suite="A2", n=n, seed=DEFAULT_SEED + s, k=k,
                               mode="any", guarded=False)


def suite_A3(seeds: int) -> Iterator[dict]:
    for n in (12, 24):
        for s in range(min(seeds, 3)):
            for mode in ("reverse", "axis"):
                for k in (1, 2, 4):
                    yield base_row(suite="A3", n=n, seed=DEFAULT_SEED + s,
                                   k=k, mode=mode, guarded=True)


def suite_E(seeds: int) -> Iterator[dict]:
    """Blame: of the relations CP-SAT says are sufficient for infeasibility, how
    many are the ones we flipped? Correlation becomes causation here or not at
    all."""
    for n in ROOM_COUNTS:
        for s in range(min(seeds, 3)):
            for k in (1, 2, 3, 4, 6, 8):
                yield base_row(suite="E", n=n, seed=DEFAULT_SEED + s, k=k,
                               mode="any", guarded=True)


def suite_F(seeds: int) -> Iterator[dict]:
    """Wrong AND abstaining at once.

    Suite E finds that flipped relations are rarely infeasible on their own —
    they are fatal in company. So loosening the company should buy the same flip
    back. That is the interaction ticket 24 asks for, and it is the one place
    the abstain half of the metric could earn its keep.
    """
    for n in ROOM_COUNTS:
        for s in range(min(seeds, 3)):
            base = len(extract_relations(get(n, DEFAULT_SEED + s)[1], TAU)[0])
            for f in (0.25, 0.5):
                for k in (1, 2, 4):
                    r = base_row(suite="F", n=n, seed=DEFAULT_SEED + s, k=k,
                                 mode=f"drop{f}", guarded=True)
                    r["drop"] = round(f * base)
                    yield r


def suite_D(seeds: int) -> Iterator[dict]:
    for n in ROOM_COUNTS:
        for s in range(min(seeds, 2)):
            for cyclen in (3, 4, 5):
                yield base_row(suite="D", n=n, seed=DEFAULT_SEED + s, k=0,
                               mode="cycle", guarded=False, cyclen=cyclen)


SUITES = {"A": suite_A, "C": suite_C, "C2": suite_C2, "B": suite_B,
          "B2": suite_B2, "E": suite_E, "F": suite_F, "A2": suite_A2,
          "A3": suite_A3, "D": suite_D}
ORDER = ("A", "C", "C2", "B", "B2", "E", "F", "A2", "A3", "D")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", nargs="*", default=list(ORDER))
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--out", default="P6.jsonl")
    a = ap.parse_args()

    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / a.out
    done = set()
    if out.exists():
        with out.open(encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    r = json.loads(line)
                    done.add(tuple(r.get(k) for k in KEY_FIELDS))

    rows: List[dict] = []
    for name in a.suite:
        rows.extend(SUITES[name](a.seeds))
    todo = [r for r in rows if tuple(r.get(k) for k in KEY_FIELDS) not in done]
    print(f"{len(rows)} rows, {len(rows)-len(todo)} already on disk, "
          f"{len(todo)} to run", flush=True)

    t0 = time.perf_counter()
    with out.open("a", encoding="utf-8") as fh:
        for i, row in enumerate(todo, 1):
            r = execute(row)
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            print(f"[{i:>4}/{len(todo)}] {r['suite']:>2} n={r['n']:>2} "
                  f"seed={r['seed']} k={r['k']} mode={r['mode']} "
                  f"sig={r['sigma']} -> {r.get('status'):>10} "
                  f"viol={r.get('violated_posted')} "
                  f"survivor={r.get('survivor')} "
                  f"valid_at={r.get('valid_at')} wall={r.get('wall')} "
                  f"[{time.perf_counter()-t0:.0f}s]", flush=True)
    print(f"done in {time.perf_counter()-t0:.0f}s -> {out}")


if __name__ == "__main__":
    main()
