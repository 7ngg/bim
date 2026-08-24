"""How much does Design A's naming heuristic leave on the table?

`fit_rects.run_dwelling` gives a Room a second rectangle only where
`two_rect_hint` -- greedy: largest inscribed rectangle, then the largest
rectangle in what is left -- finds one that clears the leg floor and joins the
first. Greedy is not exact, so a Room whose best 2-rectangle cover needs a
NON-maximal first rectangle is missed, and every such Room stayed one rectangle
in the measured arm. That is what makes ticket 40's conversion figure a lower
bound, and this is how wide the bound is.

The classifier here is EXACT, not another heuristic. A rectilinear mask is:

  a RECTANGLE      iff it equals its own bounding box;
  an L             iff (bbox minus mask) is exactly one rectangle anchored at a
                   corner of the bbox -- one reflex corner, which is ADR 0014's
                   shape;
  something else   otherwise: a T, U, S or Z, which ADR 0014 refuses, or a
                   staircase off an angled wall, which no k reaches.

For every L it then asks whether BOTH legs clear the leg floor, because a Room
whose short leg is a niche is one ADR 0014 says may not be an L at all -- so
refusing to name it is the rule working, not the heuristic failing. The two
causes are reported apart, which is the whole point: one is a decision and the
other is a defect.

Measured on the WATERSHED mask in the Envelope frame -- the thing the fit
actually sees -- not on the room polygon. ADR 0014's 52.9 % / 77.8 % were
measured by `rectilinear_k.py` on the polygon in the dwelling's own frame, so
these numbers are not comparable to those and the difference is the raster.

Run: python experiments/rectangularise/name_rate.py [n]
"""
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fit_rects as F  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"


def classify(mask):
    """'rect' | 'L' | 'other', plus the two leg sizes when it is an L."""
    ys, xs = np.nonzero(mask)
    if len(ys) == 0:
        return "empty", None
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    sub = mask[y0:y1, x0:x1]
    if sub.all():
        return "rect", (x1 - x0, y1 - y0)
    comp = ~sub
    parts = F.components(comp)
    if len(parts) != 1:
        return "other", None
    cells = parts[0]
    cy = [c[0] for c in cells]
    cx = [c[1] for c in cells]
    ny_, nx_ = sub.shape
    ry0, ry1, rx0, rx1 = min(cy), max(cy) + 1, min(cx), max(cx) + 1
    # the hole must BE a solid rectangle
    if (ry1 - ry0) * (rx1 - rx0) != len(cells):
        return "other", None
    # and it must be anchored at a corner of the bbox: one reflex corner only
    touch_y = ry0 == 0 or ry1 == ny_
    touch_x = rx0 == 0 or rx1 == nx_
    if not (touch_y and touch_x):
        return "other", None
    # The two legs of the L, as the greedy cut would make them.
    if rx0 == 0:
        leg_a = (nx_ - rx1, ry1 - ry0)      # the strip beside the notch
    else:
        leg_a = (rx0, ry1 - ry0)
    if ry0 == 0:
        leg_b = (nx_, ny_ - ry1)            # the full-width band below/above
    else:
        leg_b = (nx_, ry0)
    return "L", (leg_a, leg_b)


def main():
    n_target = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    leg = F.LEG_CELLS
    dw, keys = F.swiss_keys()
    print(f"leg floor {leg} cells = {leg * F.GRID_MM} mm centreline = "
          f"{leg * F.GRID_MM - F.T_INT_MM} mm clear\n", flush=True)

    shape = Counter()
    named = Counter()
    reason = Counter()
    done = 0
    for k in keys:
        if done >= n_target:
            break
        geoms = F.load_swiss_geoms(dw[k])
        if geoms is None:
            continue
        lab, _, _ = F.watershed(geoms)
        if lab is None:
            continue
        lab = F.keep_largest_component(lab)
        n = len(geoms)
        if any((lab == i).sum() == 0 for i in range(n)):
            continue
        env, _, _, (oy, ox) = F.envelope_approx(lab >= 0, F.MAX_NOTCHES)
        sub = np.full(env.shape, -1, dtype=lab.dtype)
        src = lab[oy:oy + env.shape[0], ox:ox + env.shape[1]]
        sub[env] = src[env]
        if any((sub == i).sum() == 0 for i in range(n)):
            continue
        for i in range(n):
            mask = (sub == i)
            cls, info = classify(mask)
            shape[cls] += 1
            h = F.two_rect_hint(mask, leg)
            got2 = h is not None and len(h) == 2
            named[(cls, got2)] += 1
            if cls == "L" and not got2:
                (aw, ah), (bw, bh) = info
                if min(aw, ah) < leg or min(bw, bh) < leg:
                    reason["L, a leg is below the floor (ADR 0014 refuses it)"] += 1
                else:
                    reason["L, both legs legal, GREEDY MISSED IT"] += 1
            elif cls == "other" and not got2:
                reason["not an L at all (T/U/S/Z or a staircase)"] += 1
        done += 1
        if done % 100 == 0:
            print(f"  {done} dwellings, {sum(shape.values())} rooms", flush=True)

    tot = sum(shape.values()) or 1
    print(f"\n{done} dwellings, {tot} rooms\n")
    print("=" * 70)
    print("WHAT SHAPE A REAL ROOM IS, ON THE WATERSHED PLANE")
    print("=" * 70)
    for c in ("rect", "L", "other"):
        print(f"  {c:<8} {shape[c]:>7}  {shape[c] / tot:.4f}")

    print("\n" + "=" * 70)
    print("WHAT DESIGN A OFFERS A SECOND RECTANGLE TO")
    print("=" * 70)
    off = sum(v for (c, g), v in named.items() if g)
    print(f"  offered            {off:>7}  {off / tot:.4f}")
    for c in ("rect", "L", "other"):
        d = shape[c] or 1
        print(f"    of the {c:<6} {named[(c, True)]:>7}  {named[(c, True)] / d:.4f}")

    print("\n" + "=" * 70)
    print("WHY A ROOM WAS NOT OFFERED ONE")
    print("=" * 70)
    print("The first line is the rule working. The second is the bound's width.")
    for r, v in reason.most_common():
        print(f"  {r:<48} {v:>7}  {v / tot:.4f}")


if __name__ == "__main__":
    main()
