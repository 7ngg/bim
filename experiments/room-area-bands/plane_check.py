"""Does the band survive the conversion, and on which plane is it measured?

Ticket 37 asks for distributions on the CONVERTED geometry, not raw polygons.
Two things have to be true for the full-corpus numbers in distributions.py to
count as converted:

  1. the conversion must not move the per-type area distribution, and
  2. the plane must be named, because ADR 0010 makes every published area a
     FINISHED-face area.

The shipped conversion (ADR 0008, `fit_rects.py`) rasterises at 250 mm by
WATERSHED: every wall cell goes to the nearest room, which splits each wall at
its centreline. So a fitted rectangle is a CENTRELINE-plane area and a corpus
polygon is the corpus's own (single, unrecorded) plane. They are not the same
quantity and the difference is about half a wall all round.

This measures that difference on the 2,600-dwelling fit sample, so the
full-corpus distribution can be stated on a named plane with a known offset.

It also checks an alignment defect found while reading `fit_rects.py`:
`load_swiss_geoms` drops polygons below MIN_ROOM_AREA, but line 727 labels the
result with `[t for t, _ in dw[k]][:n]` -- the UNFILTERED head. Where a dropped
polygon is not last, every label after it is off by one.

Run: python experiments/room-area-bands/plane_check.py
"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RECT_OUT = ROOT / "experiments" / "rectangularise" / "out"
OUT = Path(__file__).resolve().parent / "out"

CELL_M2 = 0.25 * 0.25
BATH_SPLIT_M2 = 2.4
COLLAPSE = {"ROOM": "room*", "BEDROOM": "room*", "STUDIO": "room*"}


def classify(t, area):
    if t == "BATHROOM":
        return "wc" if area < BATH_SPLIT_M2 else "bathroom"
    return COLLAPSE.get(t, t.lower())


def main():
    rects = {r["k"]: r for r in json.load(open(RECT_OUT / "swiss_rects.json"))["recs"]}
    fit = json.load(open(RECT_OUT / "swiss_fit.json"))
    lines = []

    def w(s=""):
        print(s)
        lines.append(s)

    ok = [f for f in fit if f.get("status") == "OPTIMAL" and f.get("rects")]
    w()
    w("PLANE AND CONVERSION CHECK")
    w(f"  fit records: {len(fit)}; OPTIMAL with rects: {len(ok)}")

    # --- the labelling defect -----------------------------------------------
    mism = same = missing = 0
    for f in ok:
        r = rects.get(f["k"])
        if r is None:
            missing += 1
            continue
        if list(r["types"]) == list(f.get("types", [])):
            same += 1
        else:
            mism += 1
    w()
    w("  (a) fit_rects.py line 727 label alignment, against measure_swiss's filtered list")
    w(f"      identical : {same}")
    w(f"      MISMATCHED: {mism}  ({100*mism/max(1,same+mism):.2f}% of fitted dwellings)")
    w(f"      unjoinable: {missing}")
    w("      Where these differ, any per-type reading off swiss_fit.json is mislabelled.")
    w("      Everything below relabels from measure_swiss's list, which filters correctly.")

    # --- the plane ----------------------------------------------------------
    per_type = defaultdict(list)      # (clear m2, watershed m2)
    dw_ratio = []
    for f in ok:
        r = rects.get(f["k"])
        if r is None or len(r["types"]) != len(f["rects"]):
            continue
        fitted = [(x1 - x0) * (y1 - y0) * CELL_M2 for x0, y0, x1, y1 in f["rects"]]
        clear = r["area"]
        dw_ratio.append(sum(fitted) / sum(clear))
        for t, c, v in zip(r["types"], clear, fitted):
            per_type[classify(t, c)].append((c, v))

    w()
    w("  (b) fitted (watershed / centreline) vs corpus polygon (clear), per type")
    w("      ratio > 1 is expected: the watershed hands each room half of every wall around it.")
    w("  %-12s %7s | %8s %8s | %8s %8s %8s"
      % ("class", "n", "clear p50", "fit p50", "ratio p25", "ratio p50", "ratio p75"))
    for c in sorted(per_type, key=lambda k: -len(per_type[k])):
        v = per_type[c]
        if len(v) < 100:
            continue
        cl = np.array([a for a, _ in v]); ft = np.array([b for _, b in v])
        rr = ft / cl
        w("  %-12s %7d | %8.2f %8.2f | %8.3f %8.3f %8.3f"
          % (c, len(v), np.median(cl), np.median(ft), *np.percentile(rr, [25, 50, 75])))
    dr = np.asarray(dw_ratio)
    w()
    w("  (c) dwelling-level sum(fitted)/sum(clear): p5 %.3f  p50 %.3f  p95 %.3f  (n=%d)"
      % (*np.percentile(dr, [5, 50, 95]), len(dr)))
    w()
    w("  (d) does the conversion move the DISTRIBUTION, once both are on the clear plane?")
    w("      fitted areas deflated by the dwelling's own (c) ratio, then compared to clear.")
    w("  %-12s | %8s %8s %8s | %8s %8s %8s"
      % ("class", "clear p50", "p95", "p99", "conv p50", "p95", "p99"))
    for c in sorted(per_type, key=lambda k: -len(per_type[k])):
        v = per_type[c]
        if len(v) < 100:
            continue
        cl = np.array([a for a, _ in v]); ft = np.array([b for _, b in v])
        conv = ft / np.median(dr)
        w("  %-12s | %8.2f %8.2f %8.2f | %8.2f %8.2f %8.2f"
          % (c, *np.percentile(cl, [50, 95, 99]), *np.percentile(conv, [50, 95, 99])))

    (OUT / "plane_check.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"\nwrote {OUT/'plane_check.txt'}")


if __name__ == "__main__":
    main()
