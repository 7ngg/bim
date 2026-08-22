"""Fit the band, price it, and check it cannot make a real dwelling infeasible.

Ticket 37, third pass. `bands.py` picked the anchor; this fixes the numbers and
answers the question that decides whether a maximum can ship at all:

  `model.no_unassigned_area` is hard. If every Room carries a maximum, and the
  maxima sum to less than the Envelope interior minus partitions, there is
  nowhere for the surplus to go and the Plan is INFEASIBLE rather than merely
  ugly. A cap per room is only safe if some Space is allowed to absorb.

So three things are measured together: what each cap costs in real rooms
rejected, whether the caps leave a real dwelling room to exist, and which class
carries the surplus in dwellings that have one.

Run: python experiments/room-area-bands/recommend.py
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
CANDIDATES = [95, 99, 99.5, 99.9]


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


def per_room_slope(dwellings):
    """d(one room's area)/d(dwelling total) -- does a room of this type GROW,
    or do bigger dwellings just have MORE of them? bands.py (B) cannot tell
    those apart, because it regresses the type's TOTAL in the dwelling."""
    pts = defaultdict(list)
    for d in dwellings:
        for c, a in d["rooms"]:
            pts[c].append((d["total"], a))
    out = {}
    for c, v in pts.items():
        if len(v) < 500:
            continue
        x = np.array([p for p, _ in v]); y = np.array([q for _, q in v])
        b, a0 = np.polyfit(x, y, 1)
        pred = b * x + a0
        r2 = 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()
        # what a 40 m2 rise in dwelling size buys this room, in m2
        out[c] = (b, a0, r2, 40 * b)
    return out


def report(tag, dwellings, fh):
    def w(s=""):
        print(s)
        fh.write(s + "\n")

    by_type = defaultdict(list)
    for d in dwellings:
        for c, a in d["rooms"]:
            by_type[c].append(a)
    classes = sorted(by_type, key=lambda c: -len(by_type[c]))
    fitted = [c for c in classes if len(by_type[c]) >= 500]

    w()
    w("=" * 104)
    w(f"{tag}   {len(dwellings)} dwellings")
    w("=" * 104)
    w()
    w("(E) DOES ONE ROOM OF THIS TYPE GROW WITH THE DWELLING?")
    w("     slope = d(room area)/d(dwelling total). +40 m2 col = what 40 m2 more dwelling buys THIS room.")
    w("  %-12s %8s %8s %7s %10s" % ("class", "slope", "intercept", "r2", "+40 m2 ->"))
    sl = per_room_slope(dwellings)
    for c in fitted:
        b, a0, r2, d40 = sl[c]
        w("  %-12s %8.4f %8.2f %7.3f %8.2f m2" % (c, b, a0, r2, d40))
    w()
    w("(F) CANDIDATE HARD CAPS -- percentile of real rooms, and what each rejects")
    w("  %-12s %7s | %s" % ("class", "n", " | ".join("p%-5s rej%%" % p for p in CANDIDATES)))
    caps = {}
    for c in fitted:
        a = np.asarray(by_type[c])
        cells = []
        for p in CANDIDATES:
            v = np.percentile(a, p)
            cells.append("%6.1f %5.2f" % (v, 100 * (a > v).mean()))
        caps[c] = {p: float(np.percentile(a, p)) for p in CANDIDATES}
        w("  %-12s %7d | %s" % (c, len(a), " | ".join(cells)))
    w()
    w("(G) HEADROOM -- sum of caps against the dwelling that must fit inside them")
    w("     ratio = sum(cap for each room present) / actual dwelling total.")
    w("     ratio <= 1 means the caps CANNOT accommodate this real dwelling: INFEASIBLE, not ugly.")
    w("  %-8s | %8s %8s %8s %8s | %s" % ("cap", "p1", "p5", "p50", "min", "dwellings with ratio<=1"))
    for p in CANDIDATES:
        rs, bad = [], 0
        for d in dwellings:
            s = sum(caps[c][p] for c, _ in d["rooms"] if c in caps)
            cov = sum(a for c, a in d["rooms"] if c in caps)
            if cov <= 0:
                continue
            r = s / cov
            rs.append(r)
            if r <= 1.0:
                bad += 1
        rs = np.asarray(rs)
        w("  p%-7s | %8.2f %8.2f %8.2f %8.2f | %d  (%.2f%%)"
          % (p, np.percentile(rs, 1), np.percentile(rs, 5), np.percentile(rs, 50),
             rs.min(), bad, 100 * bad / len(rs)))
    w()
    w("(H) THE 40 m2 WC, against each candidate cap")
    if "wc" in caps:
        for p in CANDIDATES:
            w("     p%-6s wc cap = %.2f m2 -> a 40 m2 WC is %.0fx the cap. REJECTED."
              % (p, caps["wc"][p], 40 / caps["wc"][p]))
    w()
    w("(I) MEDIANS FOR THE SILENT `AZ` TYPES  (brief.md 9.2 ladder, rung 2)")
    for c in ("wc", "corridor", "storeroom", "kitchen"):
        if c in by_type:
            a = np.asarray(by_type[c])
            w("  %-12s n=%-7d p25=%.2f  MEDIAN=%.2f  p75=%.2f  p95=%.2f"
              % (c, len(a), *np.percentile(a, [25, 50, 75, 95])))
    return caps, by_type


def main():
    res = {}
    with open(OUT / "recommend.txt", "w", encoding="utf-8") as fh:
        for tag, p in [("SWISS DWELLINGS", RECT_OUT / "swiss_rects.json"),
                       ("RESPLAN", RECT_OUT / "resplan_rects.json")]:
            caps, _ = report(tag, load(p), fh)
            res[tag] = caps
    json.dump(res, open(OUT / "caps.json", "w"), indent=1)
    print(f"\nwrote {OUT/'recommend.txt'}")


if __name__ == "__main__":
    main()
