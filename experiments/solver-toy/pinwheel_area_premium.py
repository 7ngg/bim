"""What does a non-guillotine layout cost in floor area?

The first run of the ticket-29 sweep could build no pinwheel dwelling at 7 or 8
rooms, and it would have been easy to report that as a fact about pinwheels. It
is not. It is a fact about the harness: `scenarios.AREA_PER_ROOM_M2` is 9.65,
fitted to the three Envelopes Part I published, so an 8-room dwelling here is
77 m2 and its living room wants 12 of them — and a pinwheel spends its area on
four interlocking arms, none of which can be the compact third-of-the-plan that
demands.

This finds the smallest interior area per room at which a pinwheel dwelling can
be built *and typed*, against the guillotine control on the same Envelopes. The
gap between the two columns is the premium.

Deliberately the same shape as `erosion_cost.py`, which asked the same kind of
question about ADR 0001's erosion, so the two read together.

Run: python experiments/solver-toy/pinwheel_area_premium.py
"""

from __future__ import annotations

import sys

import random

import scenarios
from pinwheel import guillotine_residue, pinwheel_ground_truth
from scenarios import (
    DOOR_MIN,
    WINDOW_MIN,
    assign_kinds,
    comp_bounds,
    composition,
    envelope_for,
)

# The console here is cp1252 and these tables are read back as UTF-8; without
# this a single non-ASCII character lands in the saved output as a mojibake.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                      # noqa: BLE001
    pass

scenarios.ASSIGN_TIME_LIMIT_S = 10.0
scenarios.ASSIGN_WORKERS = 4
# Otherwise 8, 12 and 24 return the published Envelopes and ignore the sweep.
scenarios.USE_PUBLISHED_ENVELOPES = False

BASE = scenarios.AREA_PER_ROOM_M2          # 9.65
COUNTS = (7, 8, 10, 12, 16, 24)
UPLIFTS = (1.00, 1.05, 1.10, 1.15, 1.20, 1.30, 1.50)
SEEDS = tuple(20260817 + i for i in range(4))
ARMS = (("guillotine", scenarios.ground_truth),
        ("pinwheel", pinwheel_ground_truth))


def cell(fn, env, mix, n) -> str:
    gen = typed = 0
    for s in SEEDS:
        try:
            truth = fn(env, mix, random.Random(s))
        except Exception:                                # noqa: BLE001
            continue
        gen += 1
        if assign_kinds(truth, env, DOOR_MIN, WINDOW_MIN, s,
                        comp_bounds(mix), 100):
            typed += 1
    if not gen:
        return "  none"
    return f"{typed}/{len(SEEDS)}" + ("" if gen == len(SEEDS) else "*")


def main() -> None:
    print("Smallest interior area per room at which a dwelling can be built and")
    print("typed. `typed/seeds`; `*` marks uplifts where some seed produced no")
    print("tiling at all. The clear reading is on, t_int = 100.\n")

    first = {arm: {} for arm, _ in ARMS}
    for arm, fn in ARMS:
        print(f"{arm}:")
        print(f"{'per room':>9} " + " ".join(f"{('n=%d' % n):>7}" for n in COUNTS))
        for up in UPLIFTS:
            scenarios.AREA_PER_ROOM_M2 = round(BASE * up, 3)
            cells = []
            for n in COUNTS:
                env = envelope_for(n, "detached")
                mix = composition(n)
                c = cell(fn, env, mix, n)
                cells.append(c)
                if c.startswith(f"{len(SEEDS)}/") and n not in first[arm]:
                    first[arm][n] = scenarios.AREA_PER_ROOM_M2
            print(f"{scenarios.AREA_PER_ROOM_M2:>9.2f} "
                  + " ".join(f"{c:>7}" for c in cells), flush=True)
        print()

    scenarios.AREA_PER_ROOM_M2 = BASE
    print("Smallest area per room at which every seed typed:")
    print(f"{'n':>4} {'guillotine':>12} {'pinwheel':>10} {'premium':>9}")
    for n in COUNTS:
        g = first["guillotine"].get(n)
        p = first["pinwheel"].get(n)
        prem = ("-" if not g or not p else f"{100 * (p - g) / g:+.0f}%")
        print(f"{n:>4} {(g or '-'):>12} {(p or '-'):>10} {prem:>9}")

    print("\nAnd what the pinwheel is, where it exists - residue is the largest")
    print("block no sequence of cuts takes apart; 1 means guillotine.")
    scenarios.AREA_PER_ROOM_M2 = round(BASE * 1.20, 3)
    print(f"{'n':>4} {'residue(G)':>11} {'residue(P)':>11}")
    for n in COUNTS:
        env = envelope_for(n, "detached")
        mix = composition(n)
        out = []
        for _, fn in ARMS:
            try:
                out.append(guillotine_residue(fn(env, mix, random.Random(SEEDS[0]))))
            except Exception:                            # noqa: BLE001
                out.append(0)
        print(f"{n:>4} {out[0]:>11} {out[1]:>11}")


if __name__ == "__main__":
    main()
