"""Can the clear reading be made free by choosing the minima better?

`erosion_cost.py` showed that ADR 0001's clear reading is not an *area* problem
— pouring more interior area at it does not reliably restore exact tiling, and
4 rooms never recovers even at +40 %. The mechanism is arithmetic, not spatial:

    clear_w = 250*w - t_int >= min_w        forces  w >= (min_w + t_int) / 250

and when `min_w` is itself a multiple of the grid — which every value in the
placeholder standards table is — that ceiling lands one whole grid unit above
`min_w / 250`. Every room gets 250 mm wider and 250 mm taller for a 100 mm wall.

So the fix is to publish minima that are already grid-aligned *after* erosion:

    min_w + t_int  ==  0  (mod grid)

A 1750 mm kitchen becomes 1650, and `w >= (1650 + 100)/250 = 7` exactly — the
same grid bound the published reading had, with no rounding loss at all. The
published number falls by 100 mm, which is precisely the wall that ADR 0001
introduced and the old reading silently ignored.

This tests whether that is true, by re-running the counts `erosion_cost.py`
could not fix.

Run: python experiments/solver-toy/grid_aligned_minima.py
"""

from __future__ import annotations

import scenarios
from scenarios import mm, scenario
from solver import SolveConfig, project
from validate import check

scenarios.ASSIGN_TIME_LIMIT_S = 10.0
scenarios.ASSIGN_WORKERS = 4
scenarios.BRIEF_ATTEMPTS = 12

T_INT = 100
COUNTS = (4, 5, 6, 7, 8, 10, 12)
SEEDS = (20260817, 20260818, 20260819)


def report(label: str, clear_t: int, align: bool) -> None:
    cells = []
    for n in COUNTS:
        ok = nobrief = 0
        for s in SEEDS:
            try:
                # The ground truth must satisfy whatever grid bound the solver
                # will enforce; under the aligned reading that is the published
                # one, so clear_t drops back to 0 here.
                b, t, p = scenario(n, s, door_min=mm(1.0),
                                   clear_t=0 if align else clear_t)
            except Exception:                            # noqa: BLE001
                nobrief += 1
                continue
            r = project(b, p, SolveConfig(
                workers=4, time_limit_s=20, seed=s, fix_relations=True,
                soft=("coverage",), area_units="mm_affine",
                erode_minima=bool(clear_t), t_int_mm=T_INT,
                minima_are_clear_grid=align))
            v = check(b, r.rooms) if r.rooms else None
            ok += bool(v and v["ok"])
        cells.append(f"{ok}/{len(SEEDS)}" + ("*" if nobrief else ""))
    print(f"{label:34s} " + " ".join(f"{c:>7}" for c in cells), flush=True)


def main() -> None:
    print("Exact tiling at 9.65 m2 per room, three readings of the same table.")
    print("`*` marks seeds where no Brief could be built at all.")
    print()
    print(f"{'reading':34s} " + " ".join(f"{('n=%d' % n):>7}" for n in COUNTS))
    report("published: minima on solved rect", 0, False)
    report("ADR 0001: minima on clear rect", T_INT, False)
    report("ADR 0001 + grid-aligned minima", T_INT, True)
    print()
    print("Row 3 publishes each minimum 100 mm lower — 1750 mm becomes 1650 —")
    print("so that clear = 250*w - 100 meets it at the same w the published")
    print("reading needed. The wall is paid for in the number, not in the grid.")


if __name__ == "__main__":
    main()
