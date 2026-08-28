"""PROBE (ticket 46) -- does the shipped worst_room_iou gate already remove the
off-frame population?

`proposer.md` 2.2.4 gates the retrieval index at `worst_room_iou >= 0.30`, hard,
costing 6.65 % of the index. ADR 0017 failure mode 1 reports the 10-20 deg
off-frame band at worst-room IoU 0.167 -- BELOW that cut. If the gate already
removes them, option 1 (refuse) is largely paid for and `frame_residual` is a
label on a population retrieval has already dropped.

No void computation, no watershed, no envelope_approx -- this is `void_census`'s
off-frame half alone, joined to the fit record's own per-room IoU, so it runs
over the whole cached fit rather than 400 dwellings.

Run: python experiments/rectangularise/off_frame_gate.py [n]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shapely import from_wkt

from fit_rects import swiss_keys
from measure_swiss import MIN_ROOM_AREA, _poly, dwelling_frame
from void_census import angle_of, off_by, q

OUT = Path(__file__).resolve().parent / "out"
IOU_GATE = 0.30          # proposer.md 2.2.4, hard
OFF_FRAME_DEG = 5.0      # void_census's own threshold


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
        raw = []
        for _st, wkt in items:
            g = _poly(from_wkt(wkt))
            if g is not None and g.area >= MIN_ROOM_AREA:
                raw.append(g)
        if not raw:
            continue
        ang, _cen = dwelling_frame(raw)
        if ang is None:
            continue
        offs = [off_by(a, ang) for a in (angle_of(g) for g in raw) if a is not None]
        if not offs:
            continue
        rows.append({
            "k": r["k"], "n": r["n"],
            "worst_iou": min(r["iou"]),
            "cell_agreement": r["cell_agreement"],
            "off_max": max(offs),
            "off_rooms": sum(1 for d in offs if d > OFF_FRAME_DEG),
            "rooms": len(offs),
        })
        if len(rows) % 250 == 0:
            print(f"  {len(rows)}", flush=True)

    json.dump(rows, open(OUT / "off_frame_gate.json", "w"))
    N = len(rows)
    print(f"\n{N} converted dwellings\n")

    print("OFF-FRAME BANDS, and what the shipped IoU gate does to each")
    print("  %-12s %6s %7s   %-24s %-24s" % ("off_max", "n", "share",
                                             "worst_iou med/p10", "gated out at 0.30"))
    bands = [(0, 2), (2, 5), (5, 10), (10, 20), (20, 90)]
    for lo, hi in bands:
        s = [x for x in rows if lo <= x["off_max"] < hi]
        if not s:
            continue
        w = [x["worst_iou"] for x in s]
        cut = sum(1 for x in s if x["worst_iou"] < IOU_GATE)
        print("  %2d-%2d deg    %6d %6.1f%%   %6.3f / %.3f            %5d  %5.1f%%"
              % (lo, hi, len(s), 100 * len(s) / N, q(w, 50), q(w, 10),
                 cut, 100 * cut / len(s)))

    print("\nTHE JOIN -- 2x2 on (off frame > 10 deg) x (below the IoU gate)")
    a = sum(1 for x in rows if x["off_max"] >= 10 and x["worst_iou"] < IOU_GATE)
    b = sum(1 for x in rows if x["off_max"] >= 10 and x["worst_iou"] >= IOU_GATE)
    c = sum(1 for x in rows if x["off_max"] < 10 and x["worst_iou"] < IOU_GATE)
    d = sum(1 for x in rows if x["off_max"] < 10 and x["worst_iou"] >= IOU_GATE)
    print("                      below gate   at/above gate")
    print("  off frame >=10 deg  %8d      %8d" % (a, b))
    print("  off frame  <10 deg  %8d      %8d" % (c, d))
    print("\n  off-frame >=10 deg      : %5.2f %% of the index" % (100 * (a + b) / N))
    print("  of those, already gated : %5.1f %%" % (100 * a / max(a + b, 1)))
    print("  SURVIVES the gate       : %5.2f %% of the index" % (100 * b / N))
    print("  total gated by IoU      : %5.2f %% of the index (spec says 6.65)"
          % (100 * (a + c) / N))
    print("  of the gated, off-frame : %5.1f %%" % (100 * a / max(a + c, 1)))


if __name__ == "__main__":
    main()
