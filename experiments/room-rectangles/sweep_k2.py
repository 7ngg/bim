"""What does a second rectangle per Room cost the solver?

Ticket 28 item 2, and the ticket calls it required rather than optional: the
argument for k <= 2 rests on it.

Four arms over the same scenarios, differing ONLY in which Rooms may take a
second rectangle:

  k1          nobody              -- the control. Same feasible set as the
                                     shipped solver, run through the same class
                                     so the comparison has no second variable.
  k2_scoped   circulation + open  -- corridor, hall, living, dining, kitchen
  k2_all      every Room
  k2_all_pen  every Room, but each L costs `L_PENALTY` in the objective

The last arm is not a cost measurement. It answers a design question the ticket
does not ask: with the truth guillotine and an L never *needed*, does the solver
make one anyway? Every L here is gratuitous by construction, so the count is a
direct reading of whether the objective has taste.

Rig matches the shipped decision -- 15 s, tau = 4, mm_affine, eroded minima,
corpus-median exposure, sigma 0.5 m, 4 workers, coverage soft -- with one
deliberate difference: t_int is 150, per ADR 0010, where the published sweep ran
at 100. Absolute seconds here are therefore NOT the published 13.65 s p95. Only
the arms are comparable to each other, which is what item 2 asks for.

Run: python experiments/room-rectangles/sweep_k2.py [seeds] [--counts 4,6,8,10]
"""
from __future__ import annotations

import json
import statistics as st
import sys
import time
from collections import defaultdict
from pathlib import Path

TOY = Path(__file__).resolve().parents[1] / "solver-toy"
sys.path.insert(0, str(TOY))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import scenarios  # noqa: E402
from scenarios import envelope_for, make_brief, make_proposal, mm  # noqa: E402
from solver import SolveConfig  # noqa: E402
from solver_parts import (  # noqa: E402
    ALL_KINDS_ALLOWED, CIRCULATION_AND_OPEN, PartConfig, PartProjector,
)
from validate_parts import check  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)

scenarios.ASSIGN_WORKERS = 4

WORKERS = 4
BASE_SEED = 20260817
T_INT = 150                     # ADR 0010. The published sweep ran at 120/100.
DOOR_MIN = mm(1.0)              # ADR: 1000 mm = 4 grid units
LIMIT = 15.0                    # ADR 0007
TAU = 4                         # ADR 0007
SIGMA_M = 0.5
LEG_MIN = 4     # With eroded minima this binds the CLEAR leg at 4 x 250 = 1000 mm
                # (`cw >= min_w * g` in `_add_dimensions`). acceptance-bar.md 9.1
                # publishes 900 mm, and the two are the SAME grid bound: clear =
                # 250w - 150, so both 900 and 1000 need w >= 5 and realise at
                # 1100 mm. Per CONTEXT.md's *Realisable minimum*, that 1100 is
                # what actually binds either way.
LEG_JOIN = 4    # ditto for the shared edge
L_PENALTY = 40                  # ~ one grid unit on ten corner terms

# (name, kinds allowed a 2nd rectangle, objective cost of using one, how many
#  Rooms are FORCED to be two rectangles).
#
#   k1            the control -- same feasible set as the shipped solver.
#   free_scoped   Design B under a type whitelist: solver picks, circulation and
#                 open-plan only.
#   free_all      Design B unscoped: solver picks, any Room.
#   free_pen_*    the same, with an L costing something. Can a penalty buy taste?
#   forced2       Design A: the PROPOSAL says two Rooms are Ls and the solver
#                 must honour it. Against a guillotine truth that is strictly
#                 harder than the truth needs, so the cost is pessimistic.
ARMS = (
    ("k1",           frozenset(),           0,     0),
    ("free_scoped",  CIRCULATION_AND_OPEN,  0,     0),
    ("free_all",     ALL_KINDS_ALLOWED,     0,     0),
    ("free_pen_200", ALL_KINDS_ALLOWED,     200,   0),
    ("free_pen_2k",  ALL_KINDS_ALLOWED,     2000,  0),
    ("forced2",      ALL_KINDS_ALLOWED,     0,     2),
)

_CACHE = {}


def scenario(n: int, seed: int):
    key = (n, seed)
    if key in _CACHE:
        return _CACHE[key]
    try:
        env = envelope_for(n, "corpus_median")
        brief, truth, kinds = make_brief(f"{n}-room", env, n, seed, DOOR_MIN,
                                         scenarios.WINDOW_MIN, clear_t=T_INT)
        proposal = make_proposal(truth, kinds, seed, sigma=mm(SIGMA_M))
        val = (brief, truth, proposal)
    except Exception as e:                      # noqa: BLE001 - a result
        val = None
        print(f"    scenario n={n} seed={seed} failed: {str(e)[:120]}", flush=True)
    _CACHE[key] = val
    return val


def run(n: int, seed: int, arm: str, allow, pen: int, force: int = 0) -> dict:
    sc = scenario(n, seed)
    if sc is None:
        return {"n": n, "seed": seed, "arm": arm, "status": "NO_SCENARIO"}
    brief, truth, proposal = sc
    cfg = SolveConfig(
        objective="corners", time_limit_s=LIMIT, workers=WORKERS, seed=0,
        hint=True, soft=("coverage",), area_units="mm_affine",
        erode_minima=True, t_int_mm=T_INT, window_min=scenarios.WINDOW_MIN,
        fix_relations=True, relation_confidence=TAU, diagnose=False,
    )
    pc = PartConfig(allow=allow, leg_min=LEG_MIN, leg_join=LEG_JOIN,
                    l_penalty=pen, force=force)
    t0 = time.perf_counter()
    res = PartProjector(brief, proposal, cfg, pc).solve()
    wall = time.perf_counter() - t0
    r = res.solve
    row = {
        "n": n, "seed": seed, "arm": arm, "status": r.status,
        "wall_s": round(wall, 3), "build_s": round(r.build_time_s, 3),
        "t_first": None if r.time_to_first is None else round(r.time_to_first, 3),
        "variables": r.model_stats["variables"],
        "constraints": r.model_stats["constraints"],
        "parts": r.model_stats["parts"],
        "fixed_relations": r.model_stats["fixed_relations"],
        "eligible": res.eligible,
        "l_used": len(res.l_rooms),
        "objective": r.objective,
        "valid": False, "t_valid": None, "failures": [],
    }
    if r.rooms:
        rp = {rm: [r.rooms[p] for p in ps] for rm, ps in res.parts_of.items()}
        chk = check(brief, rp, leg_min=LEG_MIN, leg_join=LEG_JOIN,
                    window_min=scenarios.WINDOW_MIN)
        row["valid"] = bool(chk["ok"])
        row["failures"] = chk["failures"][:3]
        row["l_used"] = len(chk["l_rooms"])
        if chk["ok"]:
            row["t_valid"] = row["t_first"]
        row["l_kinds"] = sorted(brief.rooms[i].kind for i in chk["l_rooms"])
    return row


def main():
    seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    counts = (4, 6, 8, 10, 12)
    for a in sys.argv[2:]:
        if a.startswith("--counts"):
            counts = tuple(int(x) for x in a.split("=", 1)[1].split(","))

    rows = []
    for n in counts:
        for s in range(seeds):
            for arm, allow, pen, force in ARMS:
                row = run(n, BASE_SEED + s, arm, allow, pen, force)
                rows.append(row)
                print(f"  n={n:>2} s={s:>2} {arm:<11} {row['status']:<10} "
                      f"{'VALID' if row.get('valid') else '-':<6} "
                      f"wall={row.get('wall_s')} L={row.get('l_used')} "
                      f"vars={row.get('variables')}", flush=True)
            (OUT / "sweep_k2.json").write_text(json.dumps(rows))
    report(rows)


def report(rows):
    ok = [r for r in rows if r["status"] != "NO_SCENARIO"]
    print()
    print("=" * 84)
    print("1. THE COST: model size, time to a first Plan, share VALID")
    print("=" * 84)
    print(f"{'n':>3} {'arm':<11}{'runs':>5}{'vars':>8}{'cons':>8}{'rel':>5}"
          f"{'VALID':>7}{'t_first p50':>12}{'t_first p95':>12}{'wall p50':>10}")
    for n in sorted({r["n"] for r in ok}):
        for arm, *_ in ARMS:
            rs = [r for r in ok if r["n"] == n and r["arm"] == arm]
            if not rs:
                continue
            tf = sorted(r["t_first"] for r in rs if r["t_first"] is not None)
            v = sum(r["valid"] for r in rs) / len(rs)
            p = lambda q, v=tf: (v[max(0, min(len(v) - 1, int(q * len(v))))]
                                 if v else float("nan"))  # noqa: E731
            print(f"{n:>3} {arm:<11}{len(rs):>5}"
                  f"{int(st.mean(r['variables'] for r in rs)):>8}"
                  f"{int(st.mean(r['constraints'] for r in rs)):>8}"
                  f"{int(st.mean(r['fixed_relations'] for r in rs)):>5}"
                  f"{v:>7.2f}{p(0.50):>12.2f}{p(0.95):>12.2f}"
                  f"{st.median(r['wall_s'] for r in rs):>10.2f}")

    print()
    print("=" * 84)
    print("2. DOES THE SOLVER MAKE AN L WHEN IT DOES NOT HAVE TO?")
    print("=" * 84)
    print("   Ground truth is guillotine, so every L below is gratuitous.")
    print(f"{'n':>3} {'arm':<11}{'runs':>5}{'eligible/run':>14}"
          f"{'L/run':>8}{'runs with >=1 L':>18}")
    kinds = defaultdict(int)
    for n in sorted({r["n"] for r in ok}):
        for arm, *_ in ARMS:
            rs = [r for r in ok if r["n"] == n and r["arm"] == arm and r["valid"]]
            if not rs:
                continue
            share = sum(r["l_used"] > 0 for r in rs) / len(rs)
            print(f"{n:>3} {arm:<11}{len(rs):>5}"
                  f"{st.mean(r['eligible'] for r in rs):>14.1f}"
                  f"{st.mean(r['l_used'] for r in rs):>8.2f}{share:>18.2f}")
            for r in rs:
                for k in r.get("l_kinds", []):
                    kinds[(arm, k)] += 1
    print()
    print("   which kinds became Ls:")
    for (arm, k), c in sorted(kinds.items(), key=lambda kv: -kv[1]):
        print(f"     {arm:<12}{k:<12}{c:>5}")

    print()
    print("=" * 84)
    print("3. STATUS BREAKDOWN")
    print("=" * 84)
    for arm, *_ in ARMS:
        rs = [r for r in ok if r["arm"] == arm]
        c = defaultdict(int)
        for r in rs:
            c[r["status"]] += 1
        inv = sum(1 for r in rs if r["status"] in ("OPTIMAL", "FEASIBLE")
                  and not r["valid"])
        print(f"   {arm:<12}" + "  ".join(f"{k}={v}" for k, v in sorted(c.items()))
              + f"   solved-but-INVALID={inv}")

    fails = defaultdict(int)
    for r in ok:
        for f in r.get("failures", []):
            fails[f.split()[0]] += 1
    if fails:
        print("\n   independent-checker failure heads: "
              + ", ".join(f"{k}={v}" for k, v in sorted(fails.items())))


if __name__ == "__main__":
    main()
