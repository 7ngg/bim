"""PROBE (ticket 46) -- is the frame `dwelling_frame` picks the best available one?

`dwelling_frame` takes the angle of the minimum rotated rectangle of the WHOLE
room union. On a two-angle dwelling that mrr is fitted to the union of both
wings, so the angle it returns can be neither wing's -- every room is then off
frame, rather than only the minority wing's rooms.

The ticket lists three candidates (refuse / re-frame per wing / accept and label)
and none of them is "keep one frame and choose it better". This measures that
fourth option: the AREA-WEIGHTED room angle, which puts the frame on the dominant
wing by construction, against the shipped union-mrr angle.

Reported as off-frame MASS -- the area share of rooms more than 5 deg off the
frame -- because a count treats a 2 m2 store like a 30 m2 living room.

Run: python experiments/rectangularise/frame_choice.py [n]
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shapely import from_wkt
from shapely.ops import unary_union

from fit_rects import swiss_keys
from measure_swiss import MIN_ROOM_AREA, _op, _poly, dwelling_frame
from void_census import angle_of, off_by, q

OUT = Path(__file__).resolve().parent / "out"
OFF_FRAME_DEG = 5.0


def weighted_modal_angle(geoms, angs, bin_deg=2.0):
    """The area-weighted mode of the per-room angles, refined to the mean of its bin.

    Mod-90 is circular, so the bin is walked on a doubled-and-wrapped axis and
    the winning bin's members are averaged with a circular mean at 4x frequency.
    """
    nb = int(round(90.0 / bin_deg))
    w = np.zeros(nb)
    for g, a in zip(geoms, angs):
        if a is None:
            continue
        w[int(a / bin_deg) % nb] += g.area
    if w.sum() <= 0:
        return None
    # widen each bin by its neighbours so a mode straddling a boundary is not split
    ww = w + np.roll(w, 1) + np.roll(w, -1)
    b = int(np.argmax(ww))
    sel = [(g, a) for g, a in zip(geoms, angs)
           if a is not None and (int(a / bin_deg) % nb) in ((b - 1) % nb, b, (b + 1) % nb)]
    if not sel:
        return None
    s = sum(g.area * math.sin(math.radians(4 * a)) for g, a in sel)
    c = sum(g.area * math.cos(math.radians(4 * a)) for g, a in sel)
    return (math.degrees(math.atan2(s, c)) / 4.0) % 90.0


def frame_of(geoms):
    """REFERENCE IMPLEMENTATION of ADR 0031's frame. Drop-in for `dwelling_frame`.

    Same signature and same contract -- (angle in degrees mod 90, origin) -- so a
    caller swaps one name for the other and nothing else moves. NOT applied:
    `measure_swiss.dwelling_frame` still returns the union-mrr angle, because the
    swap re-bases `swiss_fit_k2.json` and must ride the single re-run
    `fit_rects.py` already owes for proposer.md 2.2.1's five index fields.

    The origin stays the union centroid -- only the ANGLE changes, and a rotation
    origin does not affect any angle measured mod 90.
    """
    u = _op(unary_union, geoms)
    if u is None or u.is_empty:
        return None, None
    angs = [angle_of(g) for g in geoms]
    a = weighted_modal_angle(geoms, angs)
    if a is None:
        return None, None
    return a, u.centroid


def frame_residual_of(geoms, frame):
    """ADR 0031's published field: area-weighted mean |deviation|, in degrees."""
    tot = sum(g.area for g in geoms)
    if tot <= 0:
        return 0.0
    return sum(g.area * off_by(a, frame)
               for g, a in ((g, angle_of(g)) for g in geoms) if a is not None) / tot


def off_mass(geoms, angs, frame):
    tot = sum(g.area for g in geoms)
    off = sum(g.area for g, a in zip(geoms, angs)
              if a is not None and off_by(a, frame) > OFF_FRAME_DEG)
    return off / tot if tot > 0 else 0.0


def main():
    n_target = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
    recs = json.load(open(OUT / "swiss_fit_k2.json"))
    ok = [r for r in recs if r["status"] in ("OPTIMAL", "FEASIBLE")]
    dw, _ = swiss_keys()
    rows = []
    for r in ok:
        if len(rows) >= n_target:
            break
        items = dw.get(tuple(r["k"].split("|")))
        if items is None:
            continue
        geoms = []
        for _st, wkt in items:
            g = _poly(from_wkt(wkt))
            if g is not None and g.area >= MIN_ROOM_AREA:
                geoms.append(g)
        if not geoms:
            continue
        mrr_ang, _ = dwelling_frame(geoms)
        if mrr_ang is None:
            continue
        angs = [angle_of(g) for g in geoms]
        mod_ang = weighted_modal_angle(geoms, angs)
        if mod_ang is None:
            continue
        rows.append({
            "k": r["k"], "n": r["n"], "worst_iou": min(r["iou"]),
            "cell_agreement": r["cell_agreement"],
            "mrr_off_max": max((off_by(a, mrr_ang) for a in angs if a is not None), default=0.0),
            "mod_off_max": max((off_by(a, mod_ang) for a in angs if a is not None), default=0.0),
            "mrr_mass": off_mass(geoms, angs, mrr_ang),
            "mod_mass": off_mass(geoms, angs, mod_ang),
            "frame_shift": off_by(mrr_ang, mod_ang),
        })
        if len(rows) % 250 == 0:
            print(f"  {len(rows)}", flush=True)

    json.dump(rows, open(OUT / "frame_choice.json", "w"))
    N = len(rows)
    print(f"\n{N} converted dwellings\n")

    print("HOW FAR THE TWO FRAME CHOICES DISAGREE")
    fs = [x["frame_shift"] for x in rows]
    print("  |mrr - modal| deg   med %.2f  p90 %.2f  p99 %.2f  max %.2f"
          % (q(fs, 50), q(fs, 90), q(fs, 99), max(fs)))
    for d in (1, 2, 5, 10):
        print("    disagree by > %2d deg: %5.2f %%" % (d, 100 * sum(1 for v in fs if v > d) / N))

    print("\nOFF-FRAME MASS (area share of rooms > 5 deg off the frame)")
    for tag, f in (("union mrr  (shipped)", "mrr_mass"), ("area-weighted modal ", "mod_mass")):
        v = [x[f] for x in rows]
        print("  %s  med %.4f  p90 %.4f  p99 %.4f  mean %.4f   >10%% of area: %5.2f %%"
              % (tag, q(v, 50), q(v, 90), q(v, 99), sum(v) / N,
                 100 * sum(1 for x in v if x > 0.10) / N))

    print("\nWHO WINS, per dwelling (off-frame mass)")
    better = sum(1 for x in rows if x["mod_mass"] < x["mrr_mass"] - 1e-9)
    worse = sum(1 for x in rows if x["mod_mass"] > x["mrr_mass"] + 1e-9)
    print("  modal better %5d (%5.2f %%)   modal worse %5d (%5.2f %%)   tie %5d"
          % (better, 100 * better / N, worse, 100 * worse / N, N - better - worse))

    print("\nTHE POPULATION THIS TICKET IS ABOUT -- shipped off_max >= 10 deg")
    s = [x for x in rows if x["mrr_off_max"] >= 10]
    print("  n = %d (%.2f %% of index)" % (len(s), 100 * len(s) / N))
    if s:
        fixed = sum(1 for x in s if x["mod_off_max"] < 10)
        print("  re-framed to modal, now under 10 deg: %d (%.1f %%)" % (fixed, 100 * fixed / len(s)))
        for tag, f in (("mrr", "mrr_mass"), ("mod", "mod_mass")):
            v = [x[f] for x in s]
            print("    %s off-frame mass  med %.4f  p90 %.4f" % (tag, q(v, 50), q(v, 90)))
        print("  IRREDUCIBLE -- off frame >= 10 deg under BOTH choices: %d (%.2f %% of index)"
              % (sum(1 for x in s if x["mod_off_max"] >= 10),
                 100 * sum(1 for x in s if x["mod_off_max"] >= 10) / N))


if __name__ == "__main__":
    main()
