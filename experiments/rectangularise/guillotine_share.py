"""Are real dwellings guillotine layouts?

The solver does NOT restrict to guillotine -- AddNoOverlap2D admits any
rectangular tiling. But `experiments/solver-toy/scenarios.py` generates every
ground-truth layout by recursive guillotine dissection, so every timing and
every feasibility figure on this map was measured on guillotine layouts only. A
pinwheel -- rooms circling a central hall, the canonical real apartment plan --
has never been solved in any experiment here.

This measures how much of reality that leaves untested, using the converted
tilings from fit_rects.py: real dwellings, expressed as rectangles.

A tiling is guillotine if some full-width or full-height cut splits it without
cutting any rectangle, recursively. Cuts may pass through the Envelope's
notches, since a notch is not a room -- so this OVERSTATES the guillotine share.

Run: python experiments/rectangularise/guillotine_share.py
"""
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent / "out"


def is_guillotine(rects):
    if len(rects) <= 1:
        return True
    x0 = min(r[0] for r in rects); x1 = max(r[2] for r in rects)
    y0 = min(r[1] for r in rects); y1 = max(r[3] for r in rects)
    for c in sorted({r[0] for r in rects} | {r[2] for r in rects}):
        if not (x0 < c < x1):
            continue
        if any(r[0] < c < r[2] for r in rects):
            continue
        a = [r for r in rects if r[2] <= c]
        b = [r for r in rects if r[0] >= c]
        if a and b and len(a) + len(b) == len(rects):
            return is_guillotine(a) and is_guillotine(b)
    for c in sorted({r[1] for r in rects} | {r[3] for r in rects}):
        if not (y0 < c < y1):
            continue
        if any(r[1] < c < r[3] for r in rects):
            continue
        a = [r for r in rects if r[3] <= c]
        b = [r for r in rects if r[1] >= c]
        if a and b and len(a) + len(b) == len(rects):
            return is_guillotine(a) and is_guillotine(b)
    return False


def main():
    recs = [r for r in json.load(open(OUT / "swiss_fit.json")) if "rects" in r]
    by_n, tot = Counter(), Counter()
    g = 0
    for r in recs:
        ok = is_guillotine([tuple(x) for x in r["rects"]])
        g += ok
        tot[r["n"]] += 1
        by_n[r["n"]] += ok
    print(f"converted dwellings: {len(recs)}")
    print(f"guillotine: {g}  ({g / len(recs):.4f})")
    print(f"NOT guillotine: {len(recs) - g}  ({1 - g / len(recs):.4f})"
          f"   <- never tested by any experiment on this map\n")
    print(f"{'rooms':>6} {'n':>6} {'guillotine':>11}")
    for k in sorted(tot):
        print(f"{k:>6} {tot[k]:>6} {by_n[k] / tot[k]:>11.4f}")


if __name__ == "__main__":
    main()
