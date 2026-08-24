"""Can the solver project a Proposal that already contains L-shaped Rooms?

`sweep_k2.py` measures what the extra freedom costs against a truth that never
needs it. This measures the other half, and it is the one Design A rests on: the
Proposal carries 1..2 boxes per Room, presence is FIXED by the Proposal rather
than searched, and the solver has to land it.

Ground truth comes from `l_truth.py` -- a guillotine dissection of n + j
rectangles with j adjacent pairs merged, so j Rooms genuinely are Ls and the
tiling is still exact.

Two arms on the SAME Brief and the SAME truth:

  designA   Proposal = one box per part, presence fixed. The honest thing.
  k1_bbox   Proposal = one box per Room, and that box is the L's BOUNDING BOX.
            The pessimal k = 1 reading, and the one where the interlocked pair
            has a positive separation cost on every axis.
  freeB0    Design B: the same primary-rectangle Proposal as k1_prim, but the
  freeB200  SOLVER may grow a second rectangle wherever it likes, unpenalised
            and penalised.
            The arm that decides A against B, because the truth here says which
            Room is really an L -- so "did the solver put the L on the right
            Room" is answerable rather than a matter of taste.
  k1_prim   Proposal = one box per Room, and that box is the L's LARGER PART.
            The fair k = 1 reading: it isolates "the extra rectangle" from "the
            better Proposal", because this box is a real rectangle of the real
            dwelling and separates cleanly from its neighbours. Without this arm
            designA's survivor rate is flattered by a worse control.

Note what ADR 0008 actually does with such a dwelling today: it DROPS it, because
representability is the reject rule. So neither k = 1 arm is the shipped system's
behaviour -- both are more generous than it.

Rig matches the shipped decision: 15 s, tau = 4, mm_affine, eroded minima at
t_int 150 (ADR 0010), corpus-median exposure, sigma 0.5 m, 4 workers.

Run: python experiments/room-rectangles/sweep_designA.py [seeds] [--counts=8,10]
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
from geometry import Rect  # noqa: E402
from scenarios import envelope_for, mm  # noqa: E402
from solver import SolveConfig  # noqa: E402
from l_truth import l_scenario  # noqa: E402
from solver_parts import ALL_KINDS_ALLOWED, PartConfig, PartProjector  # noqa: E402
from validate_parts import check  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)

scenarios.ASSIGN_WORKERS = 4

WORKERS = 4
BASE_SEED = 20260817
T_INT = 150
DOOR_MIN = mm(1.0)
LIMIT = 15.0
TAU = 4
SIGMA = mm(0.5)
LEG_MIN = 4
LEG_JOIN = 4
# Two penalties, because a penalty can only trade recall for precision -- it
# makes Ls rarer, it cannot make them better targeted. Running both makes that
# trade visible instead of asserted, and freeB0 is the ceiling on what any
# Design B can do: if the objective cannot locate the true L unpenalised, no
# penalty setting rescues it.
L_PENALTY = {"freeB0": 0, "freeB200": 200}
ARMS = ("designA", "k1_bbox", "k1_prim", "freeB0", "freeB200")


def bbox(parts):
    return Rect(min(b.x1 for b in parts), min(b.y1 for b in parts),
                max(b.x2 for b in parts), max(b.y2 for b in parts))


def cfg():
    return SolveConfig(
        objective="corners", time_limit_s=LIMIT, workers=WORKERS, seed=0,
        hint=True, soft=("coverage",), area_units="mm_affine",
        erode_minima=True, t_int_mm=T_INT, window_min=scenarios.WINDOW_MIN,
        fix_relations=True, relation_confidence=TAU, diagnose=False,
    )


_CACHE = {}


def scenario(n, j, seed):
    key = (n, j, seed)
    if key not in _CACHE:
        env = envelope_for(n + j, "corpus_median")
        _CACHE[key] = l_scenario(env, n, j, seed, DOOR_MIN, scenarios.WINDOW_MIN,
                                 T_INT, LEG_JOIN, LEG_MIN, SIGMA)
    return _CACHE[key]


def run(n, j, seed, arm):
    sc = scenario(n, j, seed)
    if sc is None:
        return {"n": n, "j": j, "seed": seed, "arm": arm, "status": "NO_SCENARIO"}
    brief, truth_parts, pp, flat = sc
    if arm == "designA":
        pc = PartConfig(leg_min=LEG_MIN, leg_join=LEG_JOIN, parts_proposal=pp)
        proposal = flat
    elif arm == "k1_bbox":
        pc = PartConfig(allow=frozenset(), leg_min=LEG_MIN, leg_join=LEG_JOIN)
        proposal = type(flat)([bbox(truth_parts[r]) for r in sorted(truth_parts)],
                              list(flat.kinds))
    elif arm == "k1_prim":
        pc = PartConfig(allow=frozenset(), leg_min=LEG_MIN, leg_join=LEG_JOIN)
        proposal = type(flat)(
            [max(pp[r], key=lambda b: b.area) for r in sorted(pp)],
            list(flat.kinds))
    else:                                    # freeB* -- Design B, on the same truth
        pc = PartConfig(allow=ALL_KINDS_ALLOWED, leg_min=LEG_MIN,
                        leg_join=LEG_JOIN, l_penalty=L_PENALTY[arm])
        proposal = type(flat)(
            [max(pp[r], key=lambda b: b.area) for r in sorted(pp)],
            list(flat.kinds))
    t0 = time.perf_counter()
    res = PartProjector(brief, proposal, cfg(), pc).solve()
    wall = time.perf_counter() - t0
    r = res.solve
    row = {
        "n": n, "j": j, "seed": seed, "arm": arm, "status": r.status,
        "wall_s": round(wall, 3),
        "t_first": None if r.time_to_first is None else round(r.time_to_first, 3),
        "variables": r.model_stats["variables"],
        "constraints": r.model_stats["constraints"],
        "parts": r.model_stats["parts"],
        "fixed_relations": r.model_stats["fixed_relations"],
        "objective": r.objective, "valid": False, "failures": [], "l_used": 0,
        "l_true": sorted(r_ for r_, ps in truth_parts.items() if len(ps) > 1),
        "l_hit": 0, "l_miss": 0, "l_spurious": 0,
    }
    if r.rooms:
        rp = {rm: [r.rooms[p] for p in ps] for rm, ps in res.parts_of.items()}
        chk = check(brief, rp, leg_min=LEG_MIN, leg_join=LEG_JOIN,
                    window_min=scenarios.WINDOW_MIN)
        row["valid"] = bool(chk["ok"])
        row["failures"] = chk["failures"][:3]
        row["l_used"] = len(chk["l_rooms"])
        got, want = set(chk["l_rooms"]), set(row["l_true"])
        row["l_hit"] = len(got & want)
        row["l_miss"] = len(want - got)
        row["l_spurious"] = len(got - want)
    return row


def main():
    seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    counts, js = (8, 10, 12), (1, 2)
    for a in sys.argv[2:]:
        if a.startswith("--counts"):
            counts = tuple(int(x) for x in a.split("=", 1)[1].split(","))
        if a.startswith("--j"):
            js = tuple(int(x) for x in a.split("=", 1)[1].split(","))
    rows = []
    for n in counts:
        for j in js:
            for s in range(seeds):
                for arm in ARMS:
                    row = run(n, j, BASE_SEED + s, arm)
                    rows.append(row)
                    print(f"  n={n:>2} j={j} s={s:>2} {arm:<9} "
                          f"{row['status']:<11}"
                          f"{'VALID' if row.get('valid') else '-':<6} "
                          f"wall={row.get('wall_s')} L={row.get('l_used')} "
                          f"rel={row.get('fixed_relations')}", flush=True)
                (OUT / "sweep_designA.json").write_text(json.dumps(rows))
    report(rows)


def report(rows):
    ok = [r for r in rows if r["status"] != "NO_SCENARIO"]
    miss = len(rows) - len(ok)
    print(f"\nscenarios that could not be generated: {miss // len(ARMS)} of "
          f"{len(rows) // len(ARMS)}\n")
    print("=" * 88)
    print("1. PROJECTING A PROPOSAL THAT CONTAINS Ls")
    print("=" * 88)
    print(f"{'n':>3}{'j':>3} {'arm':<9}{'runs':>5}{'vars':>7}{'cons':>8}"
          f"{'rel':>5}{'VALID':>7}{'t_first p50':>12}{'t_first p95':>12}"
          f"{'wall p50':>10}{'L/run':>7}")
    for n in sorted({r["n"] for r in ok}):
        for j in sorted({r["j"] for r in ok if r["n"] == n}):
            for arm in ARMS:
                rs = [r for r in ok if r["n"] == n and r["j"] == j
                      and r["arm"] == arm]
                if not rs:
                    continue
                tf = sorted(r["t_first"] for r in rs if r["t_first"] is not None)
                p = lambda q, v=tf: (v[max(0, min(len(v) - 1, int(q * len(v))))]
                                     if v else float("nan"))  # noqa: E731
                print(f"{n:>3}{j:>3} {arm:<9}{len(rs):>5}"
                      f"{int(st.mean(r['variables'] for r in rs)):>7}"
                      f"{int(st.mean(r['constraints'] for r in rs)):>8}"
                      f"{int(st.mean(r['fixed_relations'] for r in rs)):>5}"
                      f"{sum(r['valid'] for r in rs) / len(rs):>7.2f}"
                      f"{p(0.50):>12.2f}{p(0.95):>12.2f}"
                      f"{st.median(r['wall_s'] for r in rs):>10.2f}"
                      f"{st.mean(r['l_used'] for r in rs):>7.2f}")

    print()
    print("=" * 88)
    print("2. DID THE L LAND ON THE RIGHT ROOM?  (VALID runs only)")
    print("=" * 88)
    print("   The truth says which Room is an L. designA is told; freeB has to")
    print("   find it; the k1 arms cannot express one at all.")
    print(f"   {'arm':<10}{'runs':>6}{'L wanted':>10}{'hit':>7}{'missed':>8}"
          f"{'spurious':>10}{'recall':>9}{'precision':>11}")
    for arm in ARMS:
        rs = [r for r in ok if r["arm"] == arm and r["valid"]]
        if not rs:
            continue
        want = sum(len(r["l_true"]) for r in rs)
        hit = sum(r["l_hit"] for r in rs)
        miss = sum(r["l_miss"] for r in rs)
        spur = sum(r["l_spurious"] for r in rs)
        rec = hit / want if want else float("nan")
        prec = hit / (hit + spur) if (hit + spur) else float("nan")
        print(f"   {arm:<10}{len(rs):>6}{want:>10}{hit:>7}{miss:>8}{spur:>10}"
              f"{rec:>9.2f}{prec:>11.2f}")

    print()
    print("=" * 88)
    print("3. STATUS AND WHY THE CHECKER SAID NO")
    print("=" * 88)
    for arm in ARMS:
        rs = [r for r in ok if r["arm"] == arm]
        c = defaultdict(int)
        for r in rs:
            c[r["status"]] += 1
        print(f"   {arm:<10}" + "  ".join(f"{k}={v}" for k, v in sorted(c.items())))
        f = defaultdict(int)
        for r in rs:
            for x in r["failures"]:
                f[x.split()[0]] += 1
        if f:
            print("              checker: "
                  + ", ".join(f"{k}={v}" for k, v in sorted(f.items())))


if __name__ == "__main__":
    main()
