"""Can a per-room maximum make a Brief impossible to satisfy?

This is the question that decides whether `dim.max_area` can be hard at all.

`model.no_unassigned_area` is hard and exact: the union of Spaces and Wall bodies
equals the Envelope interior. So for a GIVEN Envelope -- a flat, C5's majority
case -- the sum of Space areas is fixed before the solve. If every Room also
carries a maximum, and

    sum(max for each Room in the Brief)  <  interior - partitions

then no assignment exists. The Plan is INFEASIBLE, and the Homeowner gets nothing
rather than an ugly plan. A maximum is only safe if that cannot happen, or if
something is allowed to absorb.

Real dwellings cannot show this: they all fit, by construction. So the test is a
sweep over the corpus's own joint distribution of (room count, total area), using
the corpus's own commonest room MIXES, and asking at each room count how large a
dwelling the caps can still express.

Run: python experiments/room-area-bands/expressibility.py
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RECT_OUT = ROOT / "experiments" / "rectangularise" / "out"
OUT = Path(__file__).resolve().parent / "out"

BATH_SPLIT_M2 = 2.4
COLLAPSE = {"ROOM": "room*", "BEDROOM": "room*", "STUDIO": "room*"}

# Fixture ground truth replaces the threshold-split figures for the two wet
# classes -- see wc_fixture_truth.py. Everything else is the polygon percentile.
FIXTURE = json.load(open(OUT / "wc_fixture_truth.json"))


def classify(t, area):
    if t == "BATHROOM":
        return "wc" if area < BATH_SPLIT_M2 else "bathroom"
    return COLLAPSE.get(t, t.lower())


def load():
    d = json.load(open(RECT_OUT / "swiss_rects.json"))
    out = []
    for r in d["recs"]:
        rooms = [(classify(t, a), a) for t, a in zip(r["types"], r["area"])]
        out.append({"rooms": rooms, "total": sum(a for _, a in rooms),
                    "n": len(rooms)})
    return out


def main():
    dwellings = load()
    by_type = defaultdict(list)
    for d in dwellings:
        for c, a in d["rooms"]:
            by_type[c].append(a)

    lines = []

    def w(s=""):
        print(s)
        lines.append(s)

    # ---- caps, with the two wet classes taken from fixtures -----------------
    _cap_memo = {}

    def cap(c, p):
        # memoised: np.percentile over 97k rooms inside a 43k-dwelling loop is
        # what made the first run of this script time out.
        hit = _cap_memo.get((c, p))
        if hit is not None:
            return hit
        if c == "wc":
            v = FIXTURE["wc_pan_only"][f"p{p}"]
        elif c == "bathroom":
            v = FIXTURE["bathroom_fixture"][f"p{p}"]
        else:
            v = float(np.percentile(by_type[c], p))
        _cap_memo[(c, p)] = v
        return v

    _med_memo = {}

    def med(c):
        hit = _med_memo.get(c)
        if hit is not None:
            return hit
        if c == "wc":
            v = FIXTURE["wc_pan_only"]["p50"]
        elif c == "bathroom":
            v = FIXTURE["bathroom_fixture"]["p50"]
        else:
            v = float(np.median(by_type[c]))
        _med_memo[c] = v
        return v

    classes = [c for c in sorted(by_type, key=lambda k: -len(by_type[k]))
               if len(by_type[c]) >= 500]

    w()
    w("(J) THE BAND AS A MULTIPLE OF THE TYPE MEDIAN -- the form brief.md 9.3 already commits to")
    w("     A Room.target_area is two-sided, and 9.2 sets a silent target from the type median.")
    w("     So the band is k x target, and the corpus fixes k. wc/bathroom from fixtures.")
    w("  %-12s %8s | %6s %6s %6s %6s | %6s %6s %6s"
      % ("class", "median", "p95", "p99", "p99.5", "p99.9", "k95", "k99", "k99.9"))
    for c in classes:
        m = med(c)
        w("  %-12s %8.2f | %6.2f %6.2f %6.2f %6.2f | %6.2f %6.2f %6.2f"
          % (c, m, cap(c, 95), cap(c, 99), cap(c, 99.5), cap(c, 99.9),
             cap(c, 95) / m, cap(c, 99) / m, cap(c, 99.9) / m))
    ks = [cap(c, 99) / med(c) for c in classes]
    w()
    w("     k99 across types: min %.2f  median %.2f  max %.2f -- NOT one constant."
      % (min(ks), float(np.median(ks)), max(ks)))

    # ---- expressibility sweep ----------------------------------------------
    w()
    w("(K) EXPRESSIBILITY -- the largest dwelling the caps can express, per room count")
    w("     mix = the corpus's commonest room multiset at that room count.")
    w("     sum(cap) is what the Brief can hold; corpus p95/p99 is what dwellings that size ARE.")
    w("     A row where sum(cap) < corpus p99 has real dwellings the bar would call INFEASIBLE.")
    mixes = defaultdict(Counter)
    totals = defaultdict(list)
    for d in dwellings:
        key = tuple(sorted(c for c, _ in d["rooms"]))
        mixes[d["n"]][key] += 1
        totals[d["n"]].append(d["total"])
    for p in (99, 99.5, 99.9):
        w()
        w(f"     caps at p{p}")
        w("  %4s %7s | %-46s | %8s %8s %8s %s"
          % ("n", "dwell", "commonest mix", "sum(cap)", "corp p95", "corp p99", "verdict"))
        for n in range(4, 11):
            if n not in mixes:
                continue
            mix, cnt = mixes[n].most_common(1)[0]
            s = sum(cap(c, p) if c in by_type and len(by_type[c]) >= 500 else med(c)
                    for c in mix)
            t = np.asarray(totals[n])
            p95, p99 = np.percentile(t, [95, 99])
            verdict = "OK" if s >= p99 else ("tight" if s >= p95 else "CANNOT EXPRESS")
            w("  %4d %7d | %-46s | %8.1f %8.1f %8.1f %s"
              % (n, len(t), "+".join(mix)[:46], s, p95, p99, verdict))

    # ---- what a cap costs at the dwelling level ----------------------------
    w()
    w("(L) WHOLE-DWELLING REJECT RATE -- a real dwelling dies if ANY of its rooms is over")
    w("  %-8s | %10s %12s | %s" % ("caps", "rooms rej", "dwellings rej", "worst class"))
    for p in (95, 99, 99.5, 99.9):
        nr = nd = 0
        blame = Counter()
        for d in dwellings:
            bad = [c for c, a in d["rooms"]
                   if c in classes and a > cap(c, p)]
            nr += len(bad)
            if bad:
                nd += 1
                blame.update(bad)
        tot_rooms = sum(len(d["rooms"]) for d in dwellings)
        w("  p%-7s | %6.2f%%     %8.2f%%     | %s"
          % (p, 100 * nr / tot_rooms, 100 * nd / len(dwellings),
             ", ".join(f"{k} {v}" for k, v in blame.most_common(3))))

    (OUT / "expressibility.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"\nwrote {OUT/'expressibility.txt'}")


if __name__ == "__main__":
    main()
