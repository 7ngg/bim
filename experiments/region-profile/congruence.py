"""ADR 0007 arithmetic explorer.

Given a grid and a set of candidate internal wall thicknesses, report which
published linear minima are admissible, i.e. satisfy

    minimum_mm + t_int  ==  0  (mod grid)

for EVERY t_int the profile offers.  Two thicknesses can coexist under one
shared minima table iff they are congruent modulo the grid.
"""
from itertools import combinations

GRID = 250

CANDIDATES = [80, 100, 120, 140, 160, 180, 200, 250, 300, 380, 400, 510]


def residue(t, grid=GRID):
    """The residue class an admissible minimum must fall in for this t_int."""
    return (-t) % grid


def admissible(t, lo, hi, grid=GRID):
    r = residue(t, grid)
    return [m for m in range(lo, hi + 1) if m % grid == r]


def main():
    print(f"grid = {GRID} mm\n")
    print("t_int  (-t) mod grid   first admissible minima >= 1000")
    for t in CANDIDATES:
        r = residue(t)
        first = [m for m in range(1000, 3200) if m % GRID == r][:6]
        print(f"{t:5d}  {r:12d}   {first}")

    print("\ncompatible pairs (same residue class -> one shared minima table):")
    any_pair = False
    for a, b in combinations(CANDIDATES, 2):
        if residue(a) == residue(b):
            print(f"  {a:4d} & {b:4d}   both need minima == {residue(a)} (mod {GRID})"
                  f"   [differ by {b - a} = {(b - a) // GRID} x grid]")
            any_pair = True
    if not any_pair:
        print("  none")

    print("\nresidue classes, grouped:")
    groups = {}
    for t in CANDIDATES:
        groups.setdefault(residue(t), []).append(t)
    for r in sorted(groups):
        print(f"  {r:3d}: {groups[r]}")


if __name__ == "__main__":
    main()
