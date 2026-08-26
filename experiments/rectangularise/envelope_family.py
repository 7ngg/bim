"""What the residual Envelope loss actually is, for ticket 47.

ADR 0017 failure mode 4 measured that raising ADR 0003's notch cap does not
rescue the dwellings the cap looks responsible for.  It did not say *why*, and
"their outlines are not bounding-box-minus-notches at any count" was written as
a characterisation rather than as a measurement.

This probe separates the two families the characterisation conflates:

  * **rectilinear, but not bbox-minus-rectangles** -- a staircase, a stepped
    outline, a re-entrant whose complement component is L-shaped.  A general
    rectilinear ring with a *vertex* budget would express these; more *notches*
    would not, because a notch is one rectangle.
  * **not rectilinear at all** -- a chamfer, a curve, an angled wing.  No
    rectilinear family of any budget expresses these.

The distinction decides ticket 47's option 3: widening the shape family is
worth its cost only if the population it would rescue is the first kind.

Sections 5 and 6 then ask the question the first four make unavoidable.  If the
Envelope's shape family is not what is wrong with the tail, what *is* -- and is
envelope loss even the quantity to act on?  ADR 0017 calls envelope loss the
best **predictor** of conversion quality; the predicted quantity, worst-room
IoU, is in the same record.  Section 5 prices a gate on each.  Section 6 checks
whether the off-axis population section 1 finds is already caught by the better
one.

Reads `out/swiss_fit_k2.json` and the cached `out/swiss_dw.pkl`; writes
`out/envelope_family.log`.  Costs seconds -- no re-fit, no corpus parse.
"""
import json
import pickle
import statistics as st
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from shapely import from_wkt
from shapely.affinity import rotate
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fit_rects import BAND, MIN_ROOM_AREA, _poly, dwelling_frame  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"

# A segment counts as on-axis if it lies within this many degrees of 0 or 90.
# 2 deg is deliberately generous: Swiss polygons carry survey noise, and the
# question here is architecture, not floating point.
AXIS_TOL_DEG = 2.0
# Segments shorter than this are ignored entirely -- a 30 mm crumb between two
# long orthogonal runs is digitisation, and counting it inflates every share.
MIN_SEG_M = 0.10


def frame_geoms(items):
    """Rotate one dwelling's rooms into its own frame, as the fit did."""
    geoms = []
    for _st, wkt in items:
        g = _poly(from_wkt(wkt))
        if g is not None and g.area >= MIN_ROOM_AREA:
            geoms.append(g)
    if not (BAND[0] <= len(geoms) <= BAND[1]):
        return None
    ang, cen = dwelling_frame(geoms)
    if ang is None:
        return None
    return [rotate(g, -ang, origin=cen) for g in geoms]


def off_axis_share(poly):
    """Share of the outline's length that is neither horizontal nor vertical."""
    rings = [poly.exterior] if poly.geom_type == "Polygon" else [
        p.exterior for p in poly.geoms]
    on = off = 0.0
    for ring in rings:
        xy = np.asarray(ring.coords)
        d = np.diff(xy, axis=0)
        length = np.hypot(d[:, 0], d[:, 1])
        ang = np.degrees(np.arctan2(np.abs(d[:, 1]), np.abs(d[:, 0])))
        axis = np.minimum(ang, 90.0 - ang)
        keep = length >= MIN_SEG_M
        on += float(length[keep & (axis <= AXIS_TOL_DEG)].sum())
        off += float(length[keep & (axis > AXIS_TOL_DEG)].sum())
    return off / (on + off) if (on + off) else 0.0


def worst_room_iou(r):
    """The record's per-room IoU is a list; the dwelling is as good as its worst.

    Worst-room rather than mean, for the reason ADR 0017 consequence 1 gives:
    a mean hides the one room a person would look at and call wrong.
    """
    v = r.get("iou")
    return min(v) if isinstance(v, list) and v else None


def main():
    recs = [r for r in json.load(open(OUT / "swiss_fit_k2.json"))
            if r.get("envelope_loss_by_k")]
    dw, _keys = pickle.load(open(OUT / "swiss_dw.pkl", "rb"))

    rows = []
    for i, r in enumerate(recs):
        items = dw.get(tuple(r["k"].split("|")))
        if items is None:
            continue
        geoms = frame_geoms(items)
        if geoms is None:
            continue
        u = unary_union(geoms).buffer(0)
        rows.append({
            "loss2": r["envelope_loss_by_k"]["2"],
            "loss4": r["envelope_loss_by_k"]["4"],
            "notches_all": r["notches_all"],
            "off": off_axis_share(u),
            "iou": worst_room_iou(r),
            "status": r["status"],
        })
        if (i + 1) % 500 == 0:
            print(f"  {i + 1}", flush=True)

    print(f"\ndwellings measured: {len(rows)}")
    tail = [r for r in rows if r["loss2"] > 0.10]
    rest = [r for r in rows if r["loss2"] <= 0.10]

    def block(title, g):
        if not g:
            return
        o = [r["off"] for r in g]
        print(f"\n{title}  n={len(g)}")
        print(f"   off-axis share of outline: median {st.median(o):.4f}  "
              f"p75 {np.percentile(o, 75):.4f}  p90 {np.percentile(o, 90):.4f}")
        for cut in (0.02, 0.05, 0.10, 0.20):
            print(f"   share above {cut:.0%} off-axis: "
                  f"{sum(x > cut for x in o) / len(o):.4f}")

    print("=" * 70)
    print("1. IS THE TAIL OFF-AXIS, OR MERELY STEPPED?")
    print("=" * 70)
    block("tail  (envelope loss at k=2 > 0.10)", tail)
    block("rest  (envelope loss at k=2 <= 0.10)", rest)

    print("\n" + "=" * 70)
    print("2. THE TAIL SPLIT BY WHETHER MORE NOTCHES COULD EVEN HELP")
    print("=" * 70)
    for name, g in (
        ("within the cap already (notches_all <= 2)",
         [r for r in tail if r["notches_all"] <= 2]),
        ("would need 3-4 notches", [r for r in tail if 3 <= r["notches_all"] <= 4]),
        ("would need 5+ notches", [r for r in tail if r["notches_all"] >= 5]),
    ):
        if not g:
            continue
        o = [r["off"] for r in g]
        l4 = [r["loss4"] for r in g]
        print(f"\n{name}  n={len(g)}")
        print(f"   median loss at k=4: {st.median(l4):.4f}   "
              f"still > 0.05: {sum(x > 0.05 for x in l4) / len(l4):.4f}")
        print(f"   median off-axis: {st.median(o):.4f}   "
              f"share > 5% off-axis: {sum(x > 0.05 for x in o) / len(o):.4f}")

    print("\n" + "=" * 70)
    print("3. RESIDUAL LOSS AT k=4, BY WHETHER THE OUTLINE IS RECTILINEAR")
    print("=" * 70)
    for name, pred in (
        ("rectilinear  (<= 2% off-axis)", lambda r: r["off"] <= 0.02),
        ("mixed        (2-10% off-axis)", lambda r: 0.02 < r["off"] <= 0.10),
        ("off-axis     (> 10% off-axis)", lambda r: r["off"] > 0.10),
    ):
        g = [r for r in rows if pred(r)]
        if not g:
            continue
        print(f"\n{name}  n={len(g)}  ({len(g) / len(rows):.4f} of corpus)")
        for k in ("loss2", "loss4"):
            v = [r[k] for r in g]
            print(f"   {k}: median {st.median(v):.4f}  "
                  f"share > 0.10: {sum(x > 0.10 for x in v) / len(v):.4f}")
        print("   share of the whole tail this class holds: "
              f"{sum(1 for r in g if r['loss2'] > 0.10) / len(tail):.4f}")

    print("\n" + "=" * 70)
    print("4. HOW MANY VERTICES A RECTILINEAR RING WOULD NEED")
    print("=" * 70)
    print(Counter(r["notches_all"] for r in tail).most_common())

    # The index is the *converted* corpus -- an INFEASIBLE dwelling never
    # becomes a donor, so pricing a gate over the fitted set would flatter it.
    idx = [r for r in rows
           if r["status"] in ("OPTIMAL", "FEASIBLE") and r["iou"] is not None]

    print("\n" + "=" * 70)
    print("5. WHAT A DONOR GATE COSTS, ON THE PROXY AND ON THE THING ITSELF")
    print("=" * 70)
    w = [r["iou"] for r in idx]
    print(f"\nindex n={len(idx)}   worst-room IoU: "
          f"p5 {np.percentile(w, 5):.3f}  p10 {np.percentile(w, 10):.3f}  "
          f"p25 {np.percentile(w, 25):.3f}  median {st.median(w):.3f}")

    print("\ngate on worst-room IoU -- the quantity itself:")
    for t in (0.30, 0.40, 0.50, 0.60):
        keep = [r for r in idx if r["iou"] >= t]
        print(f"   >= {t:.2f}: keeps {len(keep) / len(idx):.4f} of the index")

    print("\ngate on envelope loss at k=2 -- the proxy:")
    for t in (0.20, 0.15, 0.10, 0.06):
        keep = [r for r in idx if r["loss2"] <= t]
        drop = [r for r in idx if r["loss2"] > t]
        print(f"   <= {t:.2f}: keeps {len(keep) / len(idx):.4f}   "
              f"median worst-room IoU kept {st.median([r['iou'] for r in keep]):.3f}"
              f"  dropped {st.median([r['iou'] for r in drop]):.3f}")

    print("\nthe proxy errs in both directions:")
    inside = [r for r in idx if r["loss2"] > 0.10]
    outside = [r for r in idx if r["loss2"] <= 0.10]
    for cut in (0.30, 0.50):
        print(f"   worst-room IoU < {cut:.2f}:  inside the loss tail "
              f"{sum(r['iou'] < cut for r in inside) / len(inside):.4f}   "
              f"outside it {sum(r['iou'] < cut for r in outside) / len(outside):.4f}")

    print("\nwhat an IoU < 0.50 cut removes, by envelope-loss band:")
    for lo, hi in ((0, .01), (.01, .03), (.03, .06), (.06, .10), (.10, .20), (.20, 9)):
        b = [r for r in idx if lo <= r["loss2"] < hi]
        if b:
            print(f"   loss {lo:.2f}-{hi:.2f}  n={len(b):>4}   "
                  f"removed {sum(r['iou'] < 0.50 for r in b) / len(b):.4f}")

    print("\n" + "=" * 70)
    print("6. DOES THE BETTER GATE ALREADY CATCH THE OFF-AXIS POPULATION?")
    print("=" * 70)
    for name, pred in (
        ("rectilinear (<= 2%)", lambda r: r["off"] <= 0.02),
        ("mixed       (2-10%)", lambda r: 0.02 < r["off"] <= 0.10),
        ("off-axis    (> 10%)", lambda r: r["off"] > 0.10),
    ):
        g = [r for r in idx if pred(r)]
        if not g:
            continue
        v = [r["iou"] for r in g]
        print(f"   {name}  n={len(g):>4}  median worst-room IoU {st.median(v):.3f}"
              f"  share < 0.50 {sum(x < 0.50 for x in v) / len(v):.4f}"
              f"  share < 0.30 {sum(x < 0.30 for x in v) / len(v):.4f}")

    hard = [r for r in idx if r["iou"] < 0.30]
    print(f"\n   the IoU < 0.30 population: n={len(hard)}  "
          f"{len(hard) / len(idx):.4f} of the index")
    print(f"   of them, envelope loss > 0.10:    "
          f"{sum(r['loss2'] > 0.10 for r in hard) / len(hard):.4f}")
    print(f"   of them, outline > 10% off-axis:  "
          f"{sum(r['off'] > 0.10 for r in hard) / len(hard):.4f}")
    print("   -> neither proxy finds it; it is its own population")


if __name__ == "__main__":
    main()
