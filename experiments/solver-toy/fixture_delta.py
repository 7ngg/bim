"""What re-fitting the Envelope to the corpus costs the solver.

`envelope_fit.py` produces a second Envelope family, matched per room count
against 2,238 real dwellings on area, perimeter and bounding-box occupancy. Every
solver number on this map -- Parts I, II and III, ADR 0014, ADR 0019 -- was
measured on the *published* family, which is 15 % smaller per room and sits at
exactly 0 % boundary excess over its own bounding box where a real dwelling runs
6-12 % over.

This prices the move, at the shipped configuration and in the shape ADR 0019
used: matched `(n, exposure, seed)` slots, one arm each, so the fixture is the
only thing that differs between the two rows of a pair. It is **not** a re-run of
the published sweeps and it does not replace them. It answers one question -- does
the shipped 15 s budget and its survivor rate survive a fixture that looks like a
real dwelling -- and it is the only honest basis for either keeping the published
numbers or moving them.

Config is suite A's, verbatim: `mm_affine`, eroded minima, tau = 4, sigma = 0.5 m,
15 s, 4 workers, `t_int` 100 (what every published timing was fitted at, not
ADR 0010's shipped 150 -- see `sweep_ng.T_INT_PUBLISHED`).

Run:  ../../venv/Scripts/python.exe fixture_delta.py [seeds]
Writes results/FIXTURE.jsonl and prints the tables.
"""

from __future__ import annotations

import json
import pathlib
import statistics as st
import sys
import time
from typing import Dict, List, Optional

import scenarios
from scenarios import (CORPUS_ENVELOPES, GRID_MM, envelope_for, make_brief,
                       make_proposal, mm)
from solver import SolveConfig, project
from validate import check

RESULTS = pathlib.Path(__file__).parent / "results"
RESULTS.mkdir(exist_ok=True)
OUT = RESULTS / "FIXTURE.jsonl"

scenarios.ASSIGN_TIME_LIMIT_S = 10.0
scenarios.ASSIGN_WORKERS = 4
scenarios.BRIEF_ATTEMPTS = 12

WORKERS = 4
BASE_SEED = 20260817
DOOR_MIN_ADR = mm(1.0)
T_INT_PUBLISHED = 100
SHIPPED_LIMIT = 15.0
SHIPPED_TAU = 4

FIXTURES = ("published", "corpus")
EXPOSURES = ("detached", "corpus_median")
COUNTS = tuple(sorted(CORPUS_ENVELOPES))     # 5..11; see CORPUS_ENVELOPES


def one(n: int, seed: int, exposure: str, fixture: str) -> dict:
    row = {"n": n, "seed": seed, "exposure": exposure, "fixture": fixture,
           "limit": SHIPPED_LIMIT, "tau": SHIPPED_TAU, "workers": WORKERS,
           "t_int": T_INT_PUBLISHED}
    t0 = time.perf_counter()
    try:
        env = envelope_for(n, exposure, fixture=fixture)
        # `clear_t` MUST match the solver's `t_int_mm` whenever `erode_minima` is
        # on, exactly as suite A does it. The solver binds the minima on the
        # *clear* rect; a truth built at `clear_t = 0` satisfies them on the
        # *solved* rect and is then not a witness, so the model can be
        # provably unable to tile its own Envelope. Getting this wrong reads as
        # a fixture defect: the first run of this file returned OPTIMAL with 55
        # interior cells unassigned at every seed and both exposures on the
        # corpus arm, and it was this line. Part II.1, and `fits_kind`'s note.
        brief, truth, kinds = make_brief(
            f"{n}-room", env, n, seed, DOOR_MIN_ADR, scenarios.WINDOW_MIN,
            clear_t=T_INT_PUBLISHED)
        proposal = make_proposal(truth, kinds, seed, sigma=mm(0.5))
        wit = check(brief, list(truth))
        row["truth_valid"] = bool(wit["ok"])
        row["interior_m2"] = round(env.interior_area * (GRID_MM / 1000) ** 2, 2)
        row["perim_m"] = round(
            sum(hi - lo for (_, _, lo, hi, _) in env.all_faces()) * GRID_MM / 1000, 2)
        row["ext_run_mm"] = sum(
            hi - lo for (_, _, lo, hi, e) in env.all_faces() if e) * GRID_MM
    except Exception as e:                    # noqa: BLE001 - a result, not a bug
        row["status"] = "no_brief"
        row["error"] = str(e)[:160]
        row["gen_s"] = round(time.perf_counter() - t0, 3)
        return row
    row["gen_s"] = round(time.perf_counter() - t0, 3)

    cfg = SolveConfig(
        workers=WORKERS, time_limit_s=SHIPPED_LIMIT, seed=seed,
        fix_relations=True, relation_confidence=SHIPPED_TAU,
        soft=("coverage",), area_units="mm_affine", erode_minima=True,
        t_int_mm=T_INT_PUBLISHED,
    )
    res = project(brief, proposal, cfg)
    row["status"] = res.status
    row["wall"] = round(res.wall_time_s, 4)
    row["first"] = None if res.time_to_first is None else round(res.time_to_first, 4)
    row["valid_at"] = next((round(t, 4) for t, o in res.trace
                            if o < cfg.soft_weight), None)
    row["objective"] = res.objective
    # A survivor is C6's: a Plan the independent validator accepts, whose best
    # objective is below `soft_weight` -- above it there is unassigned floor.
    ok = False
    if res.rooms:
        v = check(brief, res.rooms)
        row["valid"] = bool(v["ok"])
        row["failures"] = v["failures"][:3] if not v["ok"] else None
        ok = bool(v["ok"]) and res.objective is not None and res.objective < cfg.soft_weight
    else:
        row["valid"] = None
        row["failures"] = None
    row["survivor"] = ok
    return row


def run(seeds: int) -> List[dict]:
    rows: List[dict] = []
    with OUT.open("w", encoding="utf-8") as fh:
        for n in COUNTS:
            for exposure in EXPOSURES:
                for s in range(seeds):
                    for fixture in FIXTURES:
                        r = one(n, BASE_SEED + s, exposure, fixture)
                        rows.append(r)
                        fh.write(json.dumps(r) + "\n")
                        fh.flush()
                        print(f"  n={n:<3} {exposure:<14} seed{s} {fixture:<10} "
                              f"{r['status']:<12} "
                              f"{'survivor' if r.get('survivor') else '-':<9} "
                              f"{r.get('wall', 0):.2f}s", flush=True)
    return rows


def _p(v: List[float], q: float) -> Optional[float]:
    if not v:
        return None
    v = sorted(v)
    i = (len(v) - 1) * q
    lo = int(i)
    hi = min(lo + 1, len(v) - 1)
    return v[lo] * (1 - (i - lo)) + v[hi] * (i - lo)


def report(rows: List[dict]) -> None:
    print("\n" + "=" * 78)
    print("The fixture, per room count -- what the solver is actually handed")
    print(f"{'n':>3} | {'published m2':>12} {'perim':>7} {'m2/room':>8} |"
          f" {'corpus m2':>10} {'perim':>7} {'m2/room':>8} | {'dA':>6} {'dP':>6}")
    for n in COUNTS:
        a = {f: next((r for r in rows if r["n"] == n and r["fixture"] == f
                      and "interior_m2" in r), None) for f in FIXTURES}
        if not all(a.values()):
            continue
        p, c = a["published"], a["corpus"]
        print(f"{n:>3} | {p['interior_m2']:>12} {p['perim_m']:>7} "
              f"{p['interior_m2']/n:>8.2f} | {c['interior_m2']:>10} "
              f"{c['perim_m']:>7} {c['interior_m2']/n:>8.2f} | "
              f"{100*(c['interior_m2']/p['interior_m2']-1):>+5.1f}% "
              f"{100*(c['perim_m']/p['perim_m']-1):>+5.1f}%")

    print("\n" + "=" * 78)
    print("Survivor rate and time to VALID, by fixture")
    for exposure in EXPOSURES:
        print(f"\n  exposure = {exposure}")
        print(f"  {'n':>3} | {'pub valid':>10} {'p50':>7} {'p90':>7} |"
              f" {'cor valid':>10} {'p50':>7} {'p90':>7}")
        for n in COUNTS:
            cells = []
            for f in FIXTURES:
                g = [r for r in rows if r["n"] == n and r["exposure"] == exposure
                     and r["fixture"] == f]
                sv = [r for r in g if r.get("survivor")]
                t = [r["valid_at"] for r in sv if r.get("valid_at") is not None]
                cells.append((len(sv), len(g), _p(t, .5), _p(t, .9)))
            (a, an, a50, a90), (b, bn, b50, b90) = cells
            f2 = lambda x: "--" if x is None else f"{x:.2f}"
            print(f"  {n:>3} | {a:>4}/{an:<5} {f2(a50):>7} {f2(a90):>7} |"
                  f" {b:>4}/{bn:<5} {f2(b50):>7} {f2(b90):>7}")

    print("\n" + "=" * 78)
    print("Pooled, and the paired count -- the same (n, exposure, seed) slot")
    for f in FIXTURES:
        g = [r for r in rows if r["fixture"] == f]
        sv = [r for r in g if r.get("survivor")]
        t = [r["valid_at"] for r in sv if r.get("valid_at") is not None]
        nb = [r for r in g if r["status"] == "no_brief"]
        inf = [r for r in g if r["status"] == "INFEASIBLE"]
        print(f"  {f:<10} survivors {len(sv):>3}/{len(g):<3} "
              f"({100*len(sv)/len(g):.1f} %)  time-to-VALID p50 "
              f"{_p(t,.5):.2f} p90 {_p(t,.9):.2f} max {max(t) if t else 0:.2f}  "
              f"no_brief {len(nb)}  INFEASIBLE {len(inf)}")

    slots: Dict[tuple, Dict[str, bool]] = {}
    for r in rows:
        slots.setdefault((r["n"], r["exposure"], r["seed"]), {})[r["fixture"]] = \
            bool(r.get("survivor"))
    both = only_p = only_c = neither = 0
    for v in slots.values():
        if len(v) < 2:
            continue
        p, c = v["published"], v["corpus"]
        both += p and c
        only_p += p and not c
        only_c += c and not p
        neither += not p and not c
    print(f"\n  paired over {both+only_p+only_c+neither} slots: both {both}, "
          f"only published {only_p}, only corpus {only_c}, neither {neither}")
    b = only_p + only_c
    if b:
        # Exact two-sided McNemar on the discordant pairs, as ADR 0019 used.
        from math import comb
        k = min(only_p, only_c)
        pv = min(1.0, 2 * sum(comb(b, i) for i in range(k + 1)) / 2 ** b)
        print(f"  exact McNemar on {b} discordant pairs: p = {pv:.4f}")
    else:
        print("  no discordant pairs")


if __name__ == "__main__":
    seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    print(f"fixture delta: {len(COUNTS)} counts x {len(EXPOSURES)} exposures x "
          f"{seeds} seeds x {len(FIXTURES)} fixtures = "
          f"{len(COUNTS)*len(EXPOSURES)*seeds*len(FIXTURES)} solves, "
          f"{SHIPPED_LIMIT} s each at worst\n")
    report(run(seeds))
