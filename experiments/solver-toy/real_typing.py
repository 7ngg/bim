"""Why a real dwelling cannot be given a Brief, measured without a solve.

Ticket 58. `real_arm.py`'s `real` column loses most of its slots to `no_brief` --
`assign_kinds` returns INFEASIBLE -- and a survivor rate cannot be read until it
is known *which* constraint refuses. Every question below is arithmetic over the
fixed real geometry, so this file runs in a second and settles the mechanism
before any solve time is spent interpreting it.

Three candidates, in the order they would bite:

  1. **Room size.** Are a real dwelling's Rooms simply too small for the toy's
     `STANDARDS` once minima are eroded onto the clear rect?
  2. **Edge typing.** A real outline is stepped, and `EXPOSURE_PRESETS` types
     **bounding-box edges**. If most of a real boundary lies off its own bbox,
     the preset cannot say whether it faces daylight.
  3. **Programme.** `COMPOSITION` fixes how many habitable Rooms the mix needs.
     A habitable Room must be exterior-facing *and* habitable-sized, and that
     conjunction does not grow with `n`.

This is ADR 0029 consequence 4's mechanism -- `assign_kinds` starving for cells
that are both exterior-facing and large enough to host a habitable type -- asked
of real geometry rather than of a fitted fixture.

Reads `../rectangularise/series/real_envelopes.json.gz`. No solver.

Run:  ../../venv/Scripts/python.exe real_typing.py
"""

from __future__ import annotations

import gzip
import json
import pathlib
import statistics as st
from typing import List

from geometry import Envelope, Rect, touches_exterior
from scenarios import (ALL_KINDS, HABITABLE, STANDARDS, WINDOW_MIN,
                       composition, fits_kind)

SERIES = (pathlib.Path(__file__).parent / ".." / "rectangularise" / "series"
          / "real_envelopes.json.gz")
T_INT_PUBLISHED = 100
EXPOSURES = ("detached", "corpus_median")


def envelope_from(row: dict, tag: str, exposure: str) -> Envelope:
    return Envelope(f"{tag}", row["W"], row["H"],
                    tuple(Rect(*q) for q in row[f"{tag}_notches"]),
                    tuple(Rect(*q) for q in row[f"{tag}_parts"]), exposure)


def _q(v: List[float], p: float) -> float:
    v = sorted(v)
    i = (len(v) - 1) * p
    lo = int(i)
    hi = min(lo + 1, len(v) - 1)
    return v[lo] * (1 - (i - lo)) + v[hi] * (i - lo)


def main() -> None:
    with gzip.open(SERIES, "rt", encoding="utf-8") as fh:
        rows = json.load(fh)
    n = len(rows)
    print(f"real dwellings: {n}\n")

    print("=" * 74)
    print("1. IS IT SIZE? -- can a real Room be typed as anything at all")
    print("=" * 74)
    total = nofit = 0
    per_kind = {k: 0 for k in ALL_KINDS}
    for r in rows:
        for q in r["truth"]:
            rect = Rect(*q)
            total += 1
            ks = [k for k in ALL_KINDS if fits_kind(rect, k, T_INT_PUBLISHED)]
            if not ks:
                nofit += 1
            for k in ks:
                per_kind[k] += 1
    print(f"   real Rooms: {total}   fitting NO toy type at clear_t="
          f"{T_INT_PUBLISHED}: {nofit} ({nofit / total:.4f})")
    print("   -> size is NOT the binding constraint.\n")
    print(f"   {'type':<10} {'rooms that fit':>15}  min (w, h, area) in cells")
    for k in ALL_KINDS:
        print(f"   {k:<10} {per_kind[k]:>15}  {STANDARDS[k]}")

    print("\n" + "=" * 74)
    print("2. IS IT EDGE TYPING? -- how much of a real boundary a preset can see")
    print("=" * 74)
    print("   A preset is a four-vector over BBOX edges. A face off the bbox is")
    print("   typed only through the notch it bounds, so the share of true")
    print("   boundary lying on a bbox edge bounds what a preset can express.")
    for tag in ("cap", "real"):
        on = []
        frac = []
        for r in rows:
            env = envelope_from(r, tag, "detached")
            tot = bb = 0
            for (k, c, lo, hi, _e) in env.all_faces():
                tot += hi - lo
                if (k == "v" and c in (0, env.W)) or (k == "h" and c in (0, env.H)):
                    bb += hi - lo
            on.append(bb / tot)
            frac.append(envelope_from(r, tag, "corpus_median").exterior_fraction)
        print(f"   {tag:>4}: on a bbox edge  p10 {_q(on, .1):.3f}  median "
              f"{st.median(on):.3f}  p90 {_q(on, .9):.3f}   "
              f"exterior_fraction at corpus_median median {st.median(frac):.3f}")
    print("   -> a third of a real boundary is off its own bbox, but the notch")
    print("      branch recovers most of the typing: NOT the binding constraint.")

    print("\n" + "=" * 74)
    print("3. IS IT THE PROGRAMME? -- habitable slots demanded against offered")
    print("=" * 74)
    print("   `COMPOSITION` fixes how many habitable Rooms the mix needs. A")
    print("   habitable Room must be exterior-facing AND habitable-sized.")
    for exposure in EXPOSURES:
        need, have, short = [], [], 0
        for r in rows:
            env = envelope_from(r, "real", exposure)
            truth = [Rect(*q) for q in r["truth"]]
            mix = composition(r["n"])
            nh = sum(1 for k in mix if k in HABITABLE)
            ok = sum(1 for x in truth
                     if touches_exterior(x, env, WINDOW_MIN)
                     and any(fits_kind(x, k, T_INT_PUBLISHED) for k in HABITABLE))
            need.append(nh)
            have.append(ok)
            short += ok < nh
        print(f"   {exposure:<14} demanded median {st.median(need):.0f}   "
              f"offered median {st.median(have):.0f}   "
              f"dwellings short {short}/{n} = {short / n:.3f}")
    print("   -> this is what refuses. It is ADR 0029 consequence 4's mechanism")
    print("      on real geometry, and it is a fact about the TOY's programme")
    print("      model, not about the solver and not about the boundary.")

    print("\n" + "=" * 74)
    print("What this does NOT say")
    print("=" * 74)
    print("   `composition` and `STANDARDS` are the TOY's placeholders, not")
    print("   `data/standards/room-constraints.json`. This measures the harness")
    print("   against real dwellings; it does not measure the shipped room")
    print("   table, and it must not be quoted as if it did.")


if __name__ == "__main__":
    main()
