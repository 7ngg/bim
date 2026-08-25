"""What a change of `t_int` can and cannot move in this formulation.

Ticket 29 inherited an instruction to re-run the solver numbers because ADR 0010
took `t_int` from 120 to 150. Two things turned out to be wrong with that:

1. **No experiment on this map has ever run at 120.** `sweep.py` line 59,
   `solver.SolveConfig.t_int_mm`, `ergonomic_minima_tiling.py`,
   `grid_aligned_minima.py`, `erosion_cost.py` and `probe6.py` all carry
   `t_int = 100`, inherited from `annotation.md` §14 — which ADR 0010 §6 itself
   flags as stale ("100 was already wrong at 120"). The move actually made is
   **100 -> 150**, 50 mm, not the 30 mm the instruction assumed, and the ADR 0007
   residue class moves **150 -> 100 (mod 250)**, not 130 -> 100.

2. The two halves of the erosion behave completely differently, and only one of
   them can move at all. This prints both, so the sweep is aimed at the half
   that can.

No solver, no corpus, no timing. Pure arithmetic on the model in
`solver.py:_add_dimensions`.

Run: python experiments/solver-toy/t_int_arithmetic.py
"""

from __future__ import annotations

import math

GRID = 250
CANDIDATES = (100, 120, 150)

# The two tables the harness has ever run against, in grid units.
PLACEHOLDER = {
    "living": (11, 11, 192), "bedroom": (8, 8, 112), "kitchen": (7, 7, 80),
    "dining": (9, 9, 112), "study": (7, 7, 80), "bathroom": (6, 6, 56),
    "wc": (4, 4, 24), "utility": (5, 5, 40), "hall": (5, 5, 48),
    "corridor": (4, 4, 40),
}
DERIVED = {
    "living": (9, 8, 64), "bedroom": (8, 8, 54), "kitchen": (5, 9, 35),
    "dining": (6, 7, 38), "study": (5, 6, 29), "bathroom": (5, 7, 30),
    "wc": (4, 5, 16), "utility": (3, 5, 10), "hall": (4, 5, 16),
    "corridor": (4, 4, 13),
}


def linear_bound(min_units: int, t: int) -> int:
    """Smallest integer grid width w with `GRID*w - t >= GRID*min_units`."""
    return math.ceil((GRID * min_units + t) / GRID)


def eroded_area_mm2(w: int, h: int, t: int) -> int:
    """solver.py's `amm`: (GRID*w - t)(GRID*h - t), written affinely there."""
    return (GRID * w - t) * (GRID * h - t)


def main() -> None:
    print("ADR 0007 residue class -- a published minimum must satisfy")
    print("    minimum_mm + t_int == 0 (mod 250)\n")
    print(f"{'t_int':>6} {'residue':>8}   what it means")
    for t in CANDIDATES:
        r = (-t) % GRID
        tag = ""
        if t == 100:
            tag = "  <- what EVERY experiment on this map actually ran at"
        if t == 120:
            tag = "  <- what ticket 29 and ADR 0010 s3 both say was run. Nothing was."
        if t == 150:
            tag = "  <- what ADR 0010 ships"
        print(f"{t:>6} {r:>8}{tag}")

    print("\n" + "=" * 78)
    print("HALF ONE -- the linear minima, for a GRID-ALIGNED table. Invariant.")
    print("=" * 78)
    print("`GRID*w - t >= GRID*min` gives `w >= min + ceil(t/GRID)`, and")
    print("ceil(t/250) is 1 for every t in (0, 250]. So 100, 120 and 150 impose")
    print("the SAME width and height bound -- but ONLY because every minimum in")
    print("this table is a whole number of grid units. See HALF THREE.\n")
    print(f"{'kind':>10} {'min_w':>6} " +
          " ".join(f"{('w@' + str(t)):>7}" for t in CANDIDATES) + "   moves?")
    moved = 0
    for k, (mw, _, _) in sorted(PLACEHOLDER.items()):
        bounds = [linear_bound(mw, t) for t in CANDIDATES]
        same = len(set(bounds)) == 1
        moved += not same
        print(f"{k:>10} {mw:>6} " + " ".join(f"{b:>7}" for b in bounds) +
              ("   no" if same else "   YES"))
    print(f"\n  room types whose linear bound moves between 100 and 150: {moved}")

    print("\n" + "=" * 78)
    print("HALF TWO -- the eroded AREA. Moves continuously, and is the only")
    print("channel through which t_int can reach a solve at all.")
    print("=" * 78)
    print("`amm = (250w - t)(250h - t)` shrinks with t, so the area floor bites")
    print("harder. This is what the sweep has to measure.\n")
    print(f"{'rect':>9} " + " ".join(f"{('m2@' + str(t)):>9}" for t in CANDIDATES)
          + f" {'loss 100->150':>14} {'as % of the rect':>17}")
    for w, h in ((8, 8), (9, 8), (11, 11), (12, 14), (13, 15), (18, 10), (22, 14)):
        areas = [eroded_area_mm2(w, h, t) / 1e6 for t in CANDIDATES]
        loss = areas[0] - areas[-1]
        print(f"{w:>4}x{h:<4} " + " ".join(f"{a:>9.3f}" for a in areas) +
              f" {loss:>14.3f} {100 * loss / areas[0]:>16.2f}%")

    print("\nWhich published minima the area move actually threatens:")
    print("a room at exactly its area floor at t = 100 that falls below it at 150.\n")
    for name, table in (("placeholder", PLACEHOLDER), ("derived ergonomic", DERIVED)):
        hits = []
        for k, (mw, mh, ma) in sorted(table.items()):
            floor = ma * GRID * GRID
            w, h = linear_bound(mw, 150), linear_bound(mh, 150)
            # Grow the square-ish rect until it clears the floor at each t.
            need = {}
            for t in (100, 150):
                ww, hh = w, h
                while eroded_area_mm2(ww, hh, t) < floor:
                    if ww <= hh:
                        ww += 1
                    else:
                        hh += 1
                need[t] = ww * hh
            if need[150] > need[100]:
                hits.append((k, need[100], need[150]))
        print(f"  {name}: {len(hits)} of {len(table)} room types need a bigger "
              f"grid rect at 150 than at 100")
        for k, a, b in hits:
            print(f"      {k:>10}  {a:>3} -> {b:>3} grid cells "
                  f"(+{100 * (b - a) / a:.1f}%)")

    print("\n" + "=" * 78)
    print("HALF THREE -- the SHIPPED ergonomic layer, whose minima are")
    print("millimetres and are NOT on the lattice (ADR 0009 exempts them).")
    print("=" * 78)
    print("Here the linear bound CAN move, because `ceil((min_mm + t)/250)`")
    print("depends on where `min_mm` sits inside its grid step. This is the")
    print("half that reaches the shipped system, and it is not what the")
    print("solver harness measures -- the harness still runs the placeholder.\n")
    ship = _shipped_ergonomic()
    if not ship:
        print("  (data/standards/room-constraints.json not readable from here)")
        return
    print(f"{'kind':>20} {'min_mm':>7} " +
          " ".join(f"{('w@' + str(t)):>7}" for t in CANDIDATES) + "   moves 100->150?")
    moved = []
    for k, mm_val in ship:
        bounds = [math.ceil((mm_val + t) / GRID) for t in CANDIDATES]
        if bounds[0] != bounds[-1]:
            moved.append((k, mm_val, bounds[0], bounds[-1]))
        print(f"{k:>20} {mm_val:>7} " + " ".join(f"{b:>7}" for b in bounds) +
              ("   no" if bounds[0] == bounds[-1] else "   YES"))
    print(f"\n  {len(moved)} of {len(ship)} shipped clear dimensions gain a whole")
    print(f"  grid unit -- 250 mm on that axis -- going from t_int 100 to 150.")
    for k, v, a, b in moved:
        print(f"      {k:>20} {v:>5} mm: w {a} -> {b} "
              f"({GRID * a - 150} -> {GRID * b - 150} mm clear delivered)")

    print("\n  WHY: ADR 0007 congruence over the layer ADR 0009 exempted from it.")
    print("  A minimum loses nothing to the grid exactly when it is congruent to")
    print("  the residue class -- and at t_int = 100 a third of this table was,")
    print("  by accident. 900, 1400, 1650, 1900 and 3150 are all 150 (mod 250).\n")
    print(f"  {'t_int':>6} {'residue':>8} {'congruent':>10} {'of':>4}  "
          f"{'wasted mm, summed over the table':>34}")
    for t in CANDIDATES:
        r = (-t) % GRID
        con = sum(1 for _, v in ship if v % GRID == r)
        waste = sum(GRID * math.ceil((v + t) / GRID) - t - v for _, v in ship)
        print(f"  {t:>6} {r:>8} {con:>10} {len(ship):>4}  {waste:>30} mm")
    print("\n  The exemption was priced once, at a t_int nothing now ships. Its")
    print("  cost is a function of t_int and moved when t_int did.")


def _shipped_ergonomic():
    """(key.axis, minimum in mm) for every clear dimension in the shipped layer."""
    import io
    import json
    import pathlib
    p = (pathlib.Path(__file__).resolve().parents[2]
         / "data" / "standards" / "room-constraints.json")
    if not p.exists():
        return []
    d = json.load(io.open(p, encoding="utf-8"))
    out = []
    for k, spec in sorted(d.get("ergonomic", {}).get("rooms", {}).items()):
        if not isinstance(spec, dict):
            continue
        for axis in ("min_clear_short", "min_clear_long"):
            cell = spec.get(axis)
            if isinstance(cell, dict) and isinstance(cell.get("v"), int):
                out.append((f"{k}.{axis.split('_')[-1]}", cell["v"]))
    return out


if __name__ == "__main__":
    main()
