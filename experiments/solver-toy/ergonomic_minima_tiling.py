"""Does ADR 0007 still bind once the minima are the DERIVED ergonomic floor?

ADR 0007 measured that ADR 0001's clear reading, applied to minima that are not
congruent to `-t_int` modulo the grid, deletes 4-, 5- and 6-room dwellings
outright. It measured that against the PLACEHOLDER table in `scenarios.py` --
living 2750 mm / 12.0 m2, bedroom 2000 mm / 7.0 m2 -- which *Ergonomic minima and
the constraint table's missing half* has now replaced with a fixture-derived floor
that is very much smaller: living 2150 x 1850, bedroom 1800 x 1900.

That matters, because the ADR's fix -- round every published minimum DOWN onto the
lattice -- is sound for a CONVENTION-derived number and unsound for a
DERIVATION-derived one. A source quoting 1750 mm was quoting a nominal or
centreline figure, so publishing 1650 mm clear recovers what the occupant can
tape. A derived 1700 mm is the bath: rounding it down to 1650 deletes 50 mm of
bathtub. The ergonomic layer can only round UP, and rounding up is arithmetically
identical to leaving the minimum unaligned -- which is the row ADR 0007 measured
as fatal.

So: is it still fatal at the derived floor's magnitude? If the deletion does not
reproduce, ADR 0007 does not bind on the ergonomic layer and v1 keeps its
250 mm grid with honest, un-rounded minima.

The derived floors are rounded UP to whole grid units here, which makes this test
strictly HARDER than the real table. A pass is therefore conclusive; a fail is
not, and would need the mm-precise reading.

Run: python experiments/solver-toy/ergonomic_minima_tiling.py
"""

from __future__ import annotations

import scenarios
from scenarios import m2, mm, scenario
from solver import SolveConfig, project
from validate import check

scenarios.ASSIGN_TIME_LIMIT_S = 10.0
scenarios.ASSIGN_WORKERS = 4
scenarios.BRIEF_ATTEMPTS = 12

T_INT = 100
COUNTS = (4, 5, 6, 7, 8, 10, 12)
SEEDS = tuple(20260817 + i for i in range(8))

PLACEHOLDER = dict(scenarios.STANDARDS)

# The derived ergonomic floor, each dimension rounded UP to a whole grid unit.
# Raw values from experiments/region-profile/floor_calibration.py; see
# docs/research/ergonomic-minima.md for the fixture arithmetic behind each.
DERIVED = {
    #            min_w        min_h        min_area
    "living":   (mm(2.25),   mm(2.00),    m2(4.0)),
    "bedroom":  (mm(2.00),   mm(2.00),    m2(3.4)),
    "kitchen":  (mm(1.25),   mm(2.25),    m2(2.2)),
    "dining":   (mm(1.50),   mm(1.75),    m2(2.4)),
    "study":    (mm(1.25),   mm(1.50),    m2(1.8)),
    "bathroom": (mm(1.25),   mm(1.75),    m2(1.9)),
    "wc":       (mm(1.00),   mm(1.25),    m2(1.0)),
    "utility":  (mm(0.75),   mm(1.25),    m2(0.6)),
    "hall":     (mm(1.00),   mm(1.25),    m2(1.0)),
    "corridor": (mm(1.00),   mm(1.00),    m2(0.8)),
}


def report(label: str, table: dict, clear_t: int, align: bool) -> None:
    scenarios.STANDARDS.clear()
    scenarios.STANDARDS.update(table)
    cells = []
    for n in COUNTS:
        ok = nobrief = 0
        for s in SEEDS:
            try:
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
    print(f"{label:44s} " + " ".join(f"{c:>7}" for c in cells), flush=True)


def main() -> None:
    print("Exact tiling at 9.65 m2 per room. `*` marks seeds where no Brief")
    print("could be built at all -- the deletion ADR 0007 measured.")
    print()
    print(f"{'reading':44s} " + " ".join(f"{('n=%d' % n):>7}" for n in COUNTS))
    report("placeholder table, minima on solved rect", PLACEHOLDER, 0, False)
    report("placeholder table, clear rect, unaligned", PLACEHOLDER, T_INT, False)
    report("DERIVED floor,     minima on solved rect", DERIVED, 0, False)
    report("DERIVED floor,     clear rect, unaligned", DERIVED, T_INT, False)
    print()
    print("Row 4 is what shipping the derived ergonomic layer at the 250 mm grid")
    print("with honest, un-rounded-down minima actually costs.")


if __name__ == "__main__":
    main()
