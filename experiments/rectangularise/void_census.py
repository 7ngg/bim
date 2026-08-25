"""PROTOTYPE (ticket 27) -- put numbers on the two things the RENDERING found.

Throwaway, and downstream of `render_sheet.py`: the pictures named these two
failure modes and this file measures how common they are. Neither is visible in
`cell_agreement`, which is why the eyeballing was owed.

1. UNASSIGNED FLOOR. `fit_rects` posts exact tiling SOFT (C10's amendment), so
   an Envelope cell no Room claims is legal and the objective merely charges for
   it. On a drawing it is a room-shaped hole with walls round it and no name.
   But not every uncovered cell is a hole: the Envelope UNDER-cuts its notches on
   purpose, so some uncovered cells were never dwelling in the first place and
   leaving them empty is right. This splits the two, and separates the void that
   is ENCLOSED by rooms -- the one a Practitioner cannot explain -- from the one
   that opens onto the Envelope edge and merely reads as a re-entrant.

2. OFF-FRAME ROOMS. `dwelling_frame` rotates a dwelling onto ONE angle, taken
   from the minimum rotated rectangle of the whole union. A dwelling built on two
   angles -- a wing splayed off a spine, which is common enough -- has every room
   in the second wing sheared by the conversion. `cell_agreement` records that as
   a middling score; the drawing shows a different flat. This measures each
   room's own angle against the frame it was given.

Run: python experiments/rectangularise/void_census.py [n]
"""
import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shapely.affinity import rotate

from fit_rects import (components, envelope_approx, keep_largest_component,
                       load_swiss_geoms, swiss_keys, watershed)
from measure_swiss import dwelling_frame

OUT = Path(__file__).resolve().parent / "out"
CELL_M2 = 0.25 * 0.25
OFF_FRAME_DEG = 5.0   # below this a room is on the dwelling's own axis
MIN_VOID_CELLS = 4    # 0.25 m2; below this it is rasterisation, not a hole


def parts_of(rec):
    if rec.get("parts") is not None:
        return rec["parts"]
    return [[r] for r in rec["rects"]]


def angle_of(g):
    """The room's own axis, mod 90 -- the same construction as dwelling_frame."""
    mrr = g.minimum_rotated_rectangle
    if not hasattr(mrr, "exterior"):
        return None
    c = np.asarray(mrr.exterior.coords)
    e = c[1] - c[0]
    return math.degrees(math.atan2(e[1], e[0])) % 90.0


def off_by(a, b):
    """Separation of two mod-90 angles, in degrees: 0 at 0 and at 90."""
    d = abs(a - b) % 90.0
    return min(d, 90.0 - d)


def one(rec, items):
    geoms = load_swiss_geoms(items)
    if geoms is None:
        return None
    lab, x0, y0 = watershed(geoms)
    if lab is None:
        return None
    lab = keep_largest_component(lab)
    env, notches, info, (oy, ox) = envelope_approx(lab >= 0)
    dom = (lab >= 0)[oy:oy + env.shape[0], ox:ox + env.shape[1]]

    covered = np.zeros(env.shape, dtype=bool)
    for ps in parts_of(rec):
        for (x1, y1, x2, y2) in ps:
            covered[y1:y2, x1:x2] = True
    unc = env & ~covered

    # An uncovered cell that was never dwelling is the Envelope's own under-cut,
    # and leaving it empty is CORRECT. Only the ones inside the real dwelling
    # are floor the conversion failed to give to a room.
    over = unc & ~dom
    real = unc & dom

    # Enclosed versus open: a void that touches the Envelope edge reads as a
    # re-entrant in the outline; one that does not is a hole in the middle of a
    # flat, and nothing in a drawing explains it.
    edge = np.zeros(env.shape, dtype=bool)
    edge[0, :] = edge[-1, :] = True
    edge[:, 0] = edge[:, -1] = True
    outside = ~env
    pad = np.pad(outside | edge, 1, constant_values=True)
    touches_out = (pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:])

    enclosed = open_ = 0
    biggest_enclosed = 0
    for cells in components(real):
        if len(cells) < MIN_VOID_CELLS:
            continue
        m = np.zeros(env.shape, dtype=bool)
        for (cy, cx) in cells:
            m[cy, cx] = True
        if (m & touches_out).any():
            open_ += len(cells)
        else:
            enclosed += len(cells)
            biggest_enclosed = max(biggest_enclosed, len(cells))

    # --- off-frame rooms
    raw = []
    for st, wkt in items:
        from shapely import from_wkt
        from measure_swiss import MIN_ROOM_AREA, _poly
        g = _poly(from_wkt(wkt))
        if g is not None and g.area >= MIN_ROOM_AREA:
            raw.append(g)
    ang, cen = dwelling_frame(raw)
    offs = []
    for g in raw:
        a = angle_of(g)
        if a is not None:
            offs.append(off_by(a, ang))

    return {
        "k": rec["k"], "n": rec["n"], "status": rec["status"],
        "cell_agreement": rec["cell_agreement"],
        "worst_iou": min(rec["iou"]),
        "envelope_loss": rec["envelope_loss"],
        "unc_total": int(unc.sum()),
        "unc_overreach": int(over.sum()),
        "unc_real": int(real.sum()),
        "void_enclosed": enclosed,
        "void_open": open_,
        "void_biggest": biggest_enclosed,
        "off_frame_max": max(offs) if offs else 0.0,
        "off_frame_rooms": sum(1 for d in offs if d > OFF_FRAME_DEG),
        "rooms": len(offs),
    }


def q(v, p):
    s = sorted(v)
    return s[max(0, min(len(s) - 1, int(round(p / 100 * (len(s) - 1)))))]


def main():
    n_target = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    recs = json.load(open(OUT / "swiss_fit_k2.json"))
    ok = [r for r in recs if r["status"] in ("OPTIMAL", "FEASIBLE")]
    dw, _ = swiss_keys()
    rows = []
    for r in ok:
        if len(rows) >= n_target:
            break
        row = one(r, dw[tuple(r["k"].split("|"))])
        if row:
            rows.append(row)
            if len(rows) % 50 == 0:
                print(f"  {len(rows)}", flush=True)
    json.dump(rows, open(OUT / "void_census.json", "w"))
    print(f"\n{len(rows)} dwellings\n")

    print("UNASSIGNED FLOOR (cells; 1 cell = 0.0625 m2)")
    for f in ("unc_total", "unc_overreach", "unc_real", "void_enclosed", "void_open"):
        v = [x[f] for x in rows]
        print("  %-14s med %5.1f  p75 %5.1f  p90 %6.1f  max %6.1f   "
              "med m2 %.2f" % (f, q(v, 50), q(v, 75), q(v, 90), max(v), q(v, 50) * CELL_M2))
    for c in (4, 8, 16, 32):
        e = sum(1 for x in rows if x["void_enclosed"] >= c)
        b = sum(1 for x in rows if x["void_biggest"] >= c)
        print("  enclosed void >= %2d cells (%.2f m2): %5.1f%% of dwellings; "
              "a SINGLE void that big: %5.1f%%"
              % (c, c * CELL_M2, 100 * e / len(rows), 100 * b / len(rows)))

    print("\nOFF-FRAME ROOMS (room axis vs the one frame it was rotated onto)")
    v = [x["off_frame_max"] for x in rows]
    print("  worst room per dwelling: med %.2f deg  p75 %.2f  p90 %.2f  p95 %.2f  max %.2f"
          % (q(v, 50), q(v, 75), q(v, 90), q(v, 95), max(v)))
    for d in (2, 5, 10, 20):
        n = sum(1 for x in rows if x["off_frame_max"] > d)
        print("  dwellings with a room off frame by > %2d deg: %5.1f%%"
              % (d, 100 * n / len(rows)))
    tot = sum(x["rooms"] for x in rows)
    off = sum(x["off_frame_rooms"] for x in rows)
    print("  rooms off frame by > %.0f deg: %d of %d (%.1f%%)"
          % (OFF_FRAME_DEG, off, tot, 100 * off / tot))

    print("\nOFF-FRAME vs THE HEADLINE NUMBER")
    for lo, hi in ((0, 2), (2, 5), (5, 10), (10, 20), (20, 90)):
        s = [x for x in rows if lo <= x["off_frame_max"] < hi]
        if not s:
            continue
        print("  off frame %2d-%2d deg  n=%4d  cell_agreement med %.3f  "
              "worst-room IoU med %.3f" % (lo, hi, len(s),
                                           q([x["cell_agreement"] for x in s], 50),
                                           q([x["worst_iou"] for x in s], 50)))
    print(f"\nwrote {OUT / 'void_census.json'}")


if __name__ == "__main__":
    main()
