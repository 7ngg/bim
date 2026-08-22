"""Which anchor a `dim.max_area` band should use, and where the slack goes.

Ticket 37. Four candidate anchors for the same band, scored the same way:

  A1  absolute m2, per room type
  A2  fraction of the dwelling's total Space area
  A3  the Room's own Brief target_area
  A4  multiple of this dwelling's mean room area (total / room count)

The score is the width of the narrowest interval admitting 90% of real rooms of
that type, expressed as hi/lo. A tighter interval is a band that says more, so
the anchor with the lowest ratio is the anchor the data supports.

A3 is not measurable directly -- corpus rooms have no Brief. It is measurable
*by identity*: *Brief schema and parsing contract* 9.2 sets a silent Room's
target from the ladder `market_default` -> corpus median -> absent, all of which
are per-TYPE constants, so for every Room the Homeowner does not size by hand,
A3 IS A1 with the median substituted for the profile value. It differs only for
a Homeowner-stated per-room area, and there the band must follow the statement.
So A3 is reported as A1's ratio, and the design note is the identity.

Run: python experiments/room-area-bands/bands.py
"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RECT_OUT = ROOT / "experiments" / "rectangularise" / "out"
OUT = Path(__file__).resolve().parent / "out"

BATH_SPLIT_M2 = 2.4
COLLAPSE = {"ROOM": "room*", "BEDROOM": "room*", "STUDIO": "room*",
            "bedroom": "room*"}
COVER = 0.90            # the band must admit this share of real rooms
MIN_N = 500             # below this a per-type band is not fitted


def classify(t, area):
    if t in ("BATHROOM", "bathroom"):
        return "wc" if area < BATH_SPLIT_M2 else "bathroom"
    return COLLAPSE.get(t, t.lower())


def load(path):
    d = json.load(open(path))
    out = []
    for r in d["recs"]:
        rooms = [(classify(t, a), a) for t, a in zip(r["types"], r["area"])]
        out.append({"rooms": rooms, "total": sum(a for _, a in rooms),
                    "n": len(rooms)})
    return out


def tightest(xs, cover=COVER):
    """Narrowest [lo, hi] by ratio admitting `cover` of xs. Returns lo, hi, ratio."""
    a = np.sort(np.asarray(xs, dtype=float))
    a = a[a > 0]
    m = len(a)
    k = int(np.ceil(cover * m))
    if k >= m:
        return a[0], a[-1], a[-1] / a[0]
    best = None
    for i in range(m - k + 1):
        lo, hi = a[i], a[i + k - 1]
        r = hi / lo
        if best is None or r < best[2]:
            best = (lo, hi, r)
    return best


def anchors(dwellings):
    """-> {class: {anchor: [values]}}"""
    out = defaultdict(lambda: defaultdict(list))
    for d in dwellings:
        tot, n = d["total"], d["n"]
        mean_room = tot / n if n else 0
        for c, a in d["rooms"]:
            out[c]["A1_abs"].append(a)
            if tot:
                out[c]["A2_frac"].append(a / tot)
            if mean_room:
                out[c]["A4_meanroom"].append(a / mean_room)
    return out


def slack_attribution(dwellings, medians):
    """Where does the area above the type median actually land?"""
    carried = defaultdict(float)
    total_excess = 0.0
    for d in dwellings:
        for c, a in d["rooms"]:
            e = a - medians.get(c, a)
            if e > 0:
                carried[c] += e
                total_excess += e
    return {c: v / total_excess for c, v in carried.items()}, total_excess


def marginal(dwellings, classes):
    """d(type total)/d(dwelling total), over ALL dwellings, absent type = 0.

    Subsetting to dwellings that HAVE the type inflates every slope -- the first
    cut of this measured 1.263 for what must sum to 1.
    """
    tot = np.array([d["total"] for d in dwellings])
    rows = {}
    for c in classes:
        y = np.array([sum(a for cc, a in d["rooms"] if cc == c) for d in dwellings])
        b, a0 = np.polyfit(tot, y, 1)
        pred = b * tot + a0
        r2 = 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()
        rows[c] = (b, a0, r2, (y > 0).mean())
    return rows


def bedroom_area_joint(dwellings, bedroom_class="room*"):
    """Bedroom count -> total area, the joint distribution brief.md 7 owes."""
    by_k = defaultdict(list)
    for d in dwellings:
        k = sum(1 for c, _ in d["rooms"] if c == bedroom_class)
        by_k[k].append(d["total"])
    return {k: np.asarray(v) for k, v in sorted(by_k.items())}


def report(tag, dwellings, fh):
    def w(s=""):
        print(s)
        fh.write(s + "\n")

    A = anchors(dwellings)
    classes = [c for c in sorted(A, key=lambda c: -len(A[c]["A1_abs"]))]
    fitted = [c for c in classes if len(A[c]["A1_abs"]) >= MIN_N]
    medians = {c: float(np.median(A[c]["A1_abs"])) for c in classes}

    w()
    w("=" * 100)
    w(f"{tag}   {len(dwellings)} dwellings")
    w("=" * 100)
    w()
    w(f"(A) WHICH ANCHOR IS TIGHTER -- narrowest interval admitting {COVER:.0%} of real rooms")
    w("     ratio = hi/lo. Lower is a band that says more. A3 == A1 by identity (see docstring).")
    w("  %-12s %6s | %-20s | %-20s | %-20s | %s"
      % ("class", "n", "A1 absolute m2", "A2 frac of dwelling",
         "A4 x mean room", "tightest"))
    winners = defaultdict(int)
    for c in fitted:
        cells, ratios = [], {}
        for key in ("A1_abs", "A2_frac", "A4_meanroom"):
            lo, hi, r = tightest(A[c][key])
            ratios[key] = r
            fmt = "%.2f-%.2f (x%.2f)" if key != "A2_frac" else "%.3f-%.3f (x%.2f)"
            cells.append(fmt % (lo, hi, r))
        best = min(ratios, key=ratios.get)
        winners[best] += 1
        w("  %-12s %6d | %-20s | %-20s | %-20s | %s"
          % (c, len(A[c]["A1_abs"]), cells[0], cells[1], cells[2], best))
    w()
    w("     anchor wins: " + ", ".join(f"{k}={v}" for k, v in
                                       sorted(winners.items(), key=lambda x: -x[1])))
    w()
    w("(B) MARGINAL ALLOCATION over ALL dwellings (absent type = 0 m2)")
    w("  %-12s %8s %9s %7s %9s" % ("class", "slope", "intercept", "r2", "present"))
    rows = marginal(dwellings, classes)
    for c in classes:
        b, a0, r2, pres = rows[c]
        w("  %-12s %8.3f %9.2f %7.3f %8.1f%%" % (c, b, a0, r2, 100 * pres))
    w("  %-12s %8.3f" % ("SUM", sum(r[0] for r in rows.values())))
    w()
    w("(C) SLACK ATTRIBUTION -- share of all above-median area carried by each class")
    share, tot_ex = slack_attribution(dwellings, medians)
    for c, v in sorted(share.items(), key=lambda x: -x[1]):
        w("  %-12s %6.1f%%   (median %.2f m2)" % (c, 100 * v, medians[c]))
    w()
    w("(D) BEDROOM COUNT -> TOTAL AREA  (brief.md 7; class '%s')" % "room*")
    w("  %5s %7s | %6s %6s %6s %6s %6s" % ("k", "n", "p5", "p25", "p50", "p75", "p95"))
    for k, v in bedroom_area_joint(dwellings).items():
        if len(v) < 30:
            continue
        q = np.percentile(v, [5, 25, 50, 75, 95])
        w("  %5d %7d | %6.1f %6.1f %6.1f %6.1f %6.1f" % (k, len(v), *q))
    return A, medians


def main():
    with open(OUT / "bands.txt", "w", encoding="utf-8") as fh:
        res = {}
        for tag, p in [("SWISS DWELLINGS", RECT_OUT / "swiss_rects.json"),
                       ("RESPLAN", RECT_OUT / "resplan_rects.json")]:
            res[tag] = report(tag, load(p), fh)
        json.dump({t: {"medians": m} for t, (_, m) in res.items()},
                  open(OUT / "medians.json", "w"), indent=1)
    print(f"\nwrote {OUT/'bands.txt'}")


if __name__ == "__main__":
    main()
