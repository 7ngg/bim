"""Fit EXPOSURE_PRESETS to the corrected corpus, on the quantity H8 binds on.

`fit_presets.py` measures the corpus. This turns that measurement into the five
preset vectors, and it fits on **exterior run per room**, not on the fraction of
perimeter that `dataset-inventory.md` §1.5 publishes.

Why not the fraction. A fraction only transfers between two dwellings whose
perimeters match, and they do not: at eight rooms the toy Envelope has 36.0 m of
perimeter around 75.0 m2, where the real median dwelling has 47.6 m around
94.1 m2. Matching the fraction therefore under-delivers the run, and run is what
H8 reads -- a room needs a window's width of facade, and cannot spend a
percentage. Run per room is also the stabler target: it is flat in the corpus
(median 3.97-4.41 m from n = 4 to 12) where the fraction is not.

Anchored at **n = 7** -- the corpus median room count, and the centre of C13's
3-10 engine-room gate.

Two limits this fit cannot remove, both structural and both in
`experiments/solver-toy/`, which this ticket may not write:

  1. `envelope_for(n)` is more compact than a real dwelling and gets more so
     with n -- perimeter/area 0.390 against the corpus 0.572 at twelve rooms --
     so a constant vector delivers a *falling* run per room against a corpus
     that is flat. Every preset therefore drifts across the band; the table this
     prints is the drift, and it is published rather than hidden.
  2. Above nine rooms the corpus median is unreachable at **any** preset,
     `detached` included, because it would need more exterior run than the
     Envelope has perimeter.

Run: ../../venv/Scripts/python.exe fit_ladder.py
"""

import bisect
import gzip
import itertools
import json
import math
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "solver-toy"))

import geometry                                          # noqa: E402
from scenarios import envelope_for                       # noqa: E402
from true_fraction import true_faces                     # noqa: E402

SIDES = ("W", "E", "S", "N")
GRID_M = 0.25
ANCHOR = 7

# Which corpus quantile of run-per-room each key is fitted to, and what ring
# shape it carries. The keys are unchanged: they are named in `brief.md`,
# `acceptance-bar.md`, `room-constraints.json`, ADR 0003, `CONTEXT.md` and three
# experiment directories, none of which this ticket writes. What changes is that
# a key is now a **quantile with a shape**, not a building form -- see this
# directory's README on why the form family did not survive measurement.
LADDER = [
    ("flat_single_aspect", 5,  "single"),
    ("flat_corner",        25, "adjacent"),
    ("terrace_mid",        25, "opposite"),
    ("corpus_median",      50, "four"),
]

# Fixed side assignments, so the ladder reads as a ladder rather than as four
# independent search results. The dominant side is S: the toy cuts its notches
# from the N edge (`u_shape`) or the NE corner (`l_shape`), so S is the one bbox
# edge that always runs whole.
SHAPES = {
    "single":   ("S", "W", "E", "N"),
    "adjacent": ("S", "E", "W", "N"),     # two sides meeting at the SE corner
    "opposite": ("S", "N", "W", "E"),     # two sides facing each other
    "four":     ("S", "W", "E", "N"),
}


def pct(xs, p):
    xs = sorted(xs)
    k = (len(xs) - 1) * p / 100.0
    lo, hi = math.floor(k), math.ceil(k)
    return xs[lo] if lo == hi else xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def run_per_room(vec, n):
    geometry.EXPOSURE_PRESETS["__fit"] = vec
    try:
        env = envelope_for(n, exposure="__fit")
        run = sum(hi - lo for (_, _, lo, hi, e) in true_faces(env) if e) * GRID_M
    finally:
        del geometry.EXPOSURE_PRESETS["__fit"]
    return run / n


def main() -> None:
    with gzip.open(HERE / "series" / "dwelling_sides.json.gz", "rt", encoding="utf-8") as fh:
        recs = json.load(fh)
    rr = sorted(r["ext_run"] / r["n_rooms"] for r in recs if r["n_rooms"])
    print(f"{len(rr):,} dwellings; run per room "
          f"p5 {pct(rr,5):.2f}  p25 {pct(rr,25):.2f}  median {statistics.median(rr):.2f}"
          f"  p75 {pct(rr,75):.2f}  p95 {pct(rr,95):.2f} m")
    print(f"anchored at n = {ANCHOR}\n")

    def crank(v):
        return 100.0 * bisect.bisect_left(rr, v) / len(rr)

    def profile_at(target):
        """The ring profile of the decile of dwellings nearest this run/room."""
        band = sorted((r for r in recs if r["n_rooms"]),
                      key=lambda r: abs(r["ext_run"] / r["n_rooms"] - target))
        band = band[:max(1, len(recs) // 10)]
        ranked = [sorted((min(1.0, r["frac"][k]) for k in SIDES), reverse=True)
                  for r in band]
        return [statistics.median(row[i] for row in ranked) for i in range(4)]

    fitted = {}
    for key, p, shape in LADDER:
        target = pct(rr, p)
        prof = profile_at(target)
        order = SHAPES[shape]
        if shape in ("adjacent", "opposite"):
            # A two-aspect ring: the two live sides take the profile's top two,
            # the other two take the bottom two. The profile is measured on the
            # dwellings at this run/room whatever their shape, so this imposes
            # the shape and keeps the measured magnitudes.
            prof = [prof[0], prof[1], prof[2] * 0.25, prof[3] * 0.25]
        lo, hi = 0.0, 4.0
        for _ in range(60):                        # scale to hit target at ANCHOR
            m = (lo + hi) / 2
            vec = {order[i]: min(1.0, prof[i] * m) for i in range(4)}
            if run_per_room(vec, ANCHOR) < target:
                lo = m
            else:
                hi = m
        vec = {order[i]: round(min(1.0, prof[i] * (lo + hi) / 2), 2) for i in range(4)}
        fitted[key] = vec
        got = run_per_room(vec, ANCHOR)
        print(f"{key:<20} p{p:<3} target {target:.2f}  ->  {got:.2f} m/room "
              f"(corpus p{crank(got):.0f})   shape {shape}")
        print(f"{'':<20} {{{', '.join(f'{chr(34)}{k}{chr(34)}: {vec[k]}' for k in SIDES)}}}")
    fitted["detached"] = {k: 1.0 for k in SIDES}

    print("\ndrift across C13's band -- run per room, and the corpus percentile it sits at:")
    keys = ["detached"] + [k for k, _, _ in LADDER]
    print(f"{'n':>3} " + " ".join(f"{k:>20}" for k in keys))
    for n in range(4, 13):
        cells = []
        for k in keys:
            v = run_per_room(fitted[k], n)
            cells.append(f"{v:.2f} (p{crank(v):.0f})")
        print(f"{n:>3} " + " ".join(f"{c:>20}" for c in cells))

    print("\nEXPOSURE_PRESETS, ready to transcribe:")
    for k in keys:
        print(f'    "{k}": {{'
              + ", ".join(f'"{s}": {fitted[k][s]}' for s in SIDES) + "},")


if __name__ == "__main__":
    main()
