"""What does ADR 0001's clear-dimension reading cost in Envelope area?

S1/S2 turned up a result nothing on the map predicted: with the standards table's
minima read as **clear** dimensions — which is what ADR 0001 means, since a
published minimum is a number a person can tape between two wall faces — exact
tiling becomes *provably* infeasible on the Envelopes this harness has always
used. CP-SAT returns OPTIMAL while paying coverage slack, so it is not a time
limit and not a search failure: no exact tiling of that Envelope satisfies those
minima.

The reason is not area. It is that every room's solved rect must now be one
whole grid unit wider and taller than before (250w - 100 >= min_w forces
w >= min_w + 1 whenever min_w * 250 is the published value), and an exact tiling
has no slack to give.

This sweeps interior area per room until exact tiling returns, so the finding
comes with a number rather than only a complaint.

Run: python experiments/solver-toy/erosion_cost.py
"""

from __future__ import annotations

import sys

import scenarios
from scenarios import mm, scenario
from solver import SolveConfig, project
from validate import check

scenarios.ASSIGN_TIME_LIMIT_S = 10.0
scenarios.ASSIGN_WORKERS = 4
scenarios.BRIEF_ATTEMPTS = 12
# Otherwise 8 and 12 would return the published Envelopes and ignore the sweep.
scenarios.USE_PUBLISHED_ENVELOPES = False

BASE = scenarios.AREA_PER_ROOM_M2          # 9.65, fitted to the published three
COUNTS = (4, 5, 6, 7, 8, 10, 12)
UPLIFTS = (1.00, 1.05, 1.10, 1.15, 1.20, 1.30, 1.40)
SEEDS = (20260817, 20260818, 20260819)


def run(n: int, seed: int, erode: bool) -> dict:
    b, t, p = scenario(n, seed, door_min=mm(1.0), clear_t=100 if erode else 0)
    r = project(b, p, SolveConfig(workers=4, time_limit_s=20, seed=seed,
                                  fix_relations=True, soft=("coverage",),
                                  area_units="mm_affine", erode_minima=erode))
    v = check(b, r.rooms) if r.rooms else None
    return {"status": r.status, "slack": r.model_stats.get("cov_slack"),
            "valid": bool(v and v["ok"]), "obj": r.objective,
            "interior": b.env.interior_area}


def main() -> None:
    print("Exact tiling under the clear reading, as interior area per room rises.")
    print(f"Baseline is {BASE} m2 per room, the value fitted to the three")
    print("published Envelopes. A cell is `valid/tried`; `.` means every run")
    print("paid coverage slack, so no exact tiling exists.\n")
    print(f"{'per room':>9} " + " ".join(f"{('n=%d' % n):>7}" for n in COUNTS))

    first_clean = {}
    for up in UPLIFTS:
        scenarios.AREA_PER_ROOM_M2 = round(BASE * up, 3)
        cells = []
        for n in COUNTS:
            ok = tried = nobrief = 0
            for s in SEEDS:
                try:
                    r = run(n, s, True)
                except Exception:                       # noqa: BLE001
                    nobrief += 1
                    continue
                tried += 1
                ok += r["valid"]
            cells.append(f"{ok}/{len(SEEDS)}" + ("*" if nobrief else ""))
            if tried == len(SEEDS) and ok == tried and n not in first_clean:
                first_clean[n] = scenarios.AREA_PER_ROOM_M2
        print(f"{scenarios.AREA_PER_ROOM_M2:>9.2f} "
              + " ".join(f"{c:>7}" for c in cells), flush=True)

    scenarios.AREA_PER_ROOM_M2 = BASE
    print("\nControl — the same Briefs under the published (grid) reading:")
    cells = []
    for n in COUNTS:
        ok = nobrief = 0
        for s in SEEDS:
            try:
                r = run(n, s, False)
            except Exception:                           # noqa: BLE001
                nobrief += 1
                continue
            ok += r["valid"]
        cells.append(f"{ok}/{len(SEEDS)}" + ("*" if nobrief else ""))
    print(f"{BASE:>9.2f} " + " ".join(f"{c:>7}" for c in cells))

    print("\nsmallest area per room at which every seed tiled exactly:")
    for n in COUNTS:
        print(f"  n={n:<3} {first_clean.get(n, 'not reached')}")


if __name__ == "__main__":
    main()
