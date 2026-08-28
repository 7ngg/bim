"""PROBE (ticket 46) -- place the cut on the quantity that actually gets published.

`off_frame_gate.py` measured the population with `off_frame_max`, a one-room
statistic. The decision publishes `frame_residual` = the AREA-WEIGHTED MEAN
deviation of a dwelling's rooms from its dwelling axis, in degrees, which carries
no threshold inside it. A cut placed on the max does not transfer, so this places
it on the residual: the knee of cell agreement against the residual, over the
dwellings that survive the shipped `worst_room_iou >= 0.30` gate.

Also reports the 8 dwellings `frame_choice.py` found the modal frame makes WORSE,
because a strict-improvement claim owes its own tail.

Run: python experiments/rectangularise/frame_residual.py [n]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shapely import from_wkt

from fit_rects import swiss_keys
from frame_choice import weighted_modal_angle
from measure_swiss import MIN_ROOM_AREA, _poly, dwelling_frame
from void_census import angle_of, off_by, q

OUT = Path(__file__).resolve().parent / "out"
IOU_GATE = 0.30


def residual(geoms, angs, frame):
    """Area-weighted mean |deviation from frame|, in degrees. No threshold."""
    tot = sum(g.area for g in geoms)
    if tot <= 0:
        return 0.0
    return sum(g.area * off_by(a, frame)
               for g, a in zip(geoms, angs) if a is not None) / tot


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
        mrr, _ = dwelling_frame(geoms)
        if mrr is None:
            continue
        angs = [angle_of(g) for g in geoms]
        mod = weighted_modal_angle(geoms, angs)
        if mod is None:
            continue
        rows.append({
            "k": r["k"], "n": r["n"], "worst_iou": min(r["iou"]),
            "cell_agreement": r["cell_agreement"],
            "res_mrr": residual(geoms, angs, mrr),
            "res_mod": residual(geoms, angs, mod),
            "off_max": max((off_by(a, mrr) for a in angs if a is not None), default=0.0),
        })
        if len(rows) % 500 == 0:
            print(f"  {len(rows)}", flush=True)

    json.dump(rows, open(OUT / "frame_residual.json", "w"))
    N = len(rows)
    print(f"\n{N} converted dwellings\n")

    for tag, f in (("shipped union-mrr frame", "res_mrr"), ("area-weighted modal frame", "res_mod")):
        v = [x[f] for x in rows]
        print("frame_residual, %s (deg)" % tag)
        print("  p50 %.3f  p75 %.3f  p90 %.3f  p95 %.3f  p99 %.3f  max %.2f  mean %.3f"
              % (q(v, 50), q(v, 75), q(v, 90), q(v, 95), q(v, 99), max(v), sum(v) / N))

    surv = [x for x in rows if x["worst_iou"] >= IOU_GATE]
    print("\nWHERE THE KNEE IS -- cell agreement by frame_residual, gate survivors (n=%d)" % len(surv))
    print("  %-16s %6s %7s  %-16s %-10s" % ("residual (deg)", "n", "share", "cell_agr med/p10", "worst_iou"))
    for lo, hi in [(0, 0.5), (0.5, 1), (1, 2), (2, 4), (4, 8), (8, 16), (16, 90)]:
        s = [x for x in surv if lo <= x["res_mrr"] < hi]
        if not s:
            continue
        ca = [x["cell_agreement"] for x in s]
        wi = [x["worst_iou"] for x in s]
        print("  %5.1f - %-6.1f    %5d %6.1f%%  %.3f / %.3f     %.3f"
              % (lo, hi, len(s), 100 * len(s) / len(surv), q(ca, 50), q(ca, 10), q(wi, 50)))

    print("\nWHAT A PARTITION COSTS, by cut (share of the index DEMOTED, not removed)")
    for cut in (1.0, 2.0, 3.0, 4.0, 5.0, 8.0):
        d = sum(1 for x in rows if x["res_mrr"] > cut)
        ds = sum(1 for x in surv if x["res_mrr"] > cut)
        print("  residual > %4.1f deg :  index %5.2f %%   gate survivors %5.2f %%"
              % (cut, 100 * d / N, 100 * ds / len(surv)))

    print("\nTHE MODAL FRAME'S OWN TAIL -- dwellings it makes WORSE")
    worse = sorted([x for x in rows if x["res_mod"] > x["res_mrr"] + 1e-9],
                   key=lambda x: x["res_mrr"] - x["res_mod"])
    print("  n = %d (%.2f %% of index)" % (len(worse), 100 * len(worse) / N))
    for x in worse[:8]:
        print("    n=%2d  residual %6.3f -> %6.3f  (+%.3f)  cell_agr %.3f"
              % (x["n"], x["res_mrr"], x["res_mod"], x["res_mod"] - x["res_mrr"], x["cell_agreement"]))
    better = [x for x in rows if x["res_mod"] < x["res_mrr"] - 1e-9]
    print("  against %d better; median gain %.3f deg, p90 gain %.3f deg"
          % (len(better),
             q([x["res_mrr"] - x["res_mod"] for x in better], 50) if better else 0,
             q([x["res_mrr"] - x["res_mod"] for x in better], 90) if better else 0))
    if worse:
        print("  worst single regression: %.3f deg" % max(x["res_mod"] - x["res_mrr"] for x in worse))


if __name__ == "__main__":
    main()
