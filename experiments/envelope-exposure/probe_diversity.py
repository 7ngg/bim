"""How different are the survivors of ONE Brief, by exposure?

The map's *Variant generation and ranking* patch carries a "deliberately
unpatched asymmetry": a stated Envelope gets no diversity axis, so flats get
less variety than bungalows. This measures the gap on one Brief.

Metric: rasterise each solved layout on the 250 mm grid, label every interior
cell with its room KIND, and take the mean pairwise fraction of cells whose kind
differs. 0 = identical layouts, 1 = nothing in common.

The envelope GEOMETRY is held identical across the comparison -- same
`envelope_for(n)`, same shape, same size, same seeds. Only the edge ring's
typing changes. The gap appears anyway, which is what makes it an **H8** effect
rather than a consequence of the aspect-ratio axis that patch proposes: H8 pins
habitable rooms to the exterior run, so fewer exterior edges means fewer
distinguishable arrangements.

REPEATS, AND WHY: `solver.SolveConfig` defaults to `workers = 8` and stops on
**wall-clock**, and multi-worker CP-SAT is not reproducible under a wall-clock
deadline even with a fixed `random_seed`. Two runs of an earlier single-pass
version of this probe returned 0.283 and 0.263 for the same cell. So each cell
is measured R times and reported as **mean and range**, and only the ratio
between exposures should be quoted -- never a single 3-decimal figure. The
direction and the rough factor are stable; the third digit is not.

`experiments/solver-toy` is claimed by *The solver has only ever seen guillotine
layouts*, so this probe lives in its own directory and imports rather than
edits.

Run:  ../../venv/Scripts/python.exe probe_diversity.py    (~3 min)
"""
from __future__ import annotations

import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "solver-toy"))

from scenarios import scenario            # noqa: E402
from solver import SolveConfig, project   # noqa: E402

SEEDS = (20260817, 991, 4242, 77, 1234, 5150)
REPEATS = 3
TIME_LIMIT_S = 6.0
ROOM_COUNTS = (5, 7)
EXPOSURES = ("detached", "corpus_median")


def label_grid(rooms, kinds):
    """Every interior grid cell -> the kind of the room covering it."""
    g = {}
    for r, k in zip(rooms, kinds):
        for x in range(r.x1, r.x2):
            for y in range(r.y1, r.y2):
                g[(x, y)] = k
    return g


def one_pass(n, exposure):
    grids = []
    for seed in SEEDS:
        try:
            brief, _truth, prop = scenario(n, seed=seed, exposure=exposure)
        except RuntimeError:
            continue                      # no feasible Brief at this exposure
        res = project(brief, prop, SolveConfig(time_limit_s=TIME_LIMIT_S))
        if not res.rooms:
            continue
        grids.append(label_grid(res.rooms, [s.kind for s in brief.rooms]))
    if len(grids) < 2:
        return None, len(grids)
    ds = []
    for a, b in itertools.combinations(grids, 2):
        keys = set(a) | set(b)
        ds.append(sum(1 for k in keys if a.get(k) != b.get(k)) / len(keys))
    return sum(ds) / len(ds), len(grids)


def main() -> int:
    print(f"mean pairwise room-kind difference over {len(SEEDS)} survivors of one "
          f"Brief, {REPEATS} repeats, {TIME_LIMIT_S:g}s limit\n")
    print(f"{'n':>3} {'exposure':>16} {'survivors':>10} {'mean':>7} {'range':>16} {'ratio':>7}")
    for n in ROOM_COUNTS:
        means = {}
        for e in EXPOSURES:
            vals, k = [], 0
            for _ in range(REPEATS):
                d, k = one_pass(n, e)
                if d is not None:
                    vals.append(d)
            if not vals:
                print(f"{n:>3} {e:>16} {k:>10} {'n/a':>7}")
                continue
            m = sum(vals) / len(vals)
            means[e] = m
            rng = f"{min(vals):.3f}-{max(vals):.3f}"
            ratio = ""
            if e != EXPOSURES[0] and EXPOSURES[0] in means:
                ratio = f"{m / means[EXPOSURES[0]]:.2f}x"
            print(f"{n:>3} {e:>16} {k:>10} {m:>7.3f} {rng:>16} {ratio:>7}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
