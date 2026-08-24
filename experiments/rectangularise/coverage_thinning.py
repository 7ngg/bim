"""How much does the conversion thin a retrieval pool, at one rectangle and two?

Ticket 40 item 5 owes `proposer.md` 2.2's coverage table a correction, but that
file belongs to ticket 23 and this ticket may not write it. What it CAN hand
over is the quantity 23 needs to redo the table itself: the **thinning factor**,
the share of a pool that survives conversion, because retrieval's pool for a
Brief is the set of corpus dwellings sharing its room multiset and the
conversion removes some of them.

    coverage_after ~ coverage_before x thinning(pool)

This reads `experiments/retrieval-coverage/out/dwelling_records.json` READ-ONLY
-- the same pattern `experiments/envelope-exposure/` uses against
`solver-toy` -- and joins it to this ticket's two fits on the dwelling key,
which is identical in both (`site|floor|apartment`).

WHAT THIS IS NOT. The fit covers a hash-ordered sample of the corpus, not all
46,794 dwellings, so no absolute coverage figure can come out of it: a pool of
92 in the full index is a pool of 5 here. Every number below is a RATIO measured
on the sample and meant to be applied to the full-index figures, never quoted
beside them.

Run: python experiments/rectangularise/coverage_thinning.py [k1.json] [k2.json]
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
CACHE = HERE.parent / "retrieval-coverage" / "out" / "dwelling_records.json"

# collapsed_coverage.py: {ROOM, BEDROOM, STUDIO} are one class in the Brief's
# vocabulary, and that is the vocabulary retrieval gates in.
COLLAPSE = {"ROOM": "PRIVATE", "BEDROOM": "PRIVATE", "STUDIO": "PRIVATE"}
BANDS = {"4-6": range(4, 7), "7-10": range(7, 11), "11-15": range(11, 16)}


def converted(r):
    return r["status"] in ("OPTIMAL", "FEASIBLE")


def main():
    f1 = sys.argv[1] if len(sys.argv) > 1 else "swiss_fit_k1.json"
    f2 = sys.argv[2] if len(sys.argv) > 2 else "swiss_fit_k2.json"
    a = {r["k"]: r for r in json.load(open(OUT / f1))}
    b = {r["k"]: r for r in json.load(open(OUT / f2))}
    recs = {r["k"]: r for r in json.load(open(CACHE))}

    keys = [k for k in b if k in a and k in recs
            and a[k]["status"] != "UNKNOWN" and b[k]["status"] != "UNKNOWN"]
    print(f"joined {len(keys)} dwellings against the coverage cache "
          f"({len(recs):,} in the full index)\n")

    def ms_of(k):
        c = Counter()
        for t, n in recs[k]["ms"]:
            c[COLLAPSE.get(t, t)] += n
        return tuple(sorted(c.items()))

    print("=" * 74)
    print("THINNING BY ROOM COUNT")
    print("=" * 74)
    print("The share of a room-count stratum that survives conversion. Multiply")
    print("proposer.md 2.2's pool sizes by this, do not add to them.\n")
    byn = defaultdict(list)
    for k in keys:
        byn[recs[k]["n"]].append(k)
    print(f"{'n':>4} {'sampled':>9} {'k=1':>9} {'k<=2':>9} {'pool x':>9}")
    for n in sorted(byn):
        ks = byn[n]
        t1 = sum(converted(a[k]) for k in ks) / len(ks)
        t2 = sum(converted(b[k]) for k in ks) / len(ks)
        mult = (t2 / t1) if t1 else float("nan")
        print(f"{n:>4} {len(ks):>9} {t1:>9.4f} {t2:>9.4f} {mult:>9.3f}")

    print("\n" + "=" * 74)
    print("THINNING BY BAND")
    print("=" * 74)
    print(f"{'band':<8} {'sampled':>9} {'k=1':>9} {'k<=2':>9} {'pool x':>9}")
    for label, rng in BANDS.items():
        ks = [k for k in keys if recs[k]["n"] in rng]
        if not ks:
            continue
        t1 = sum(converted(a[k]) for k in ks) / len(ks)
        t2 = sum(converted(b[k]) for k in ks) / len(ks)
        mult = (t2 / t1) if t1 else float("nan")
        print(f"{label:<8} {len(ks):>9} {t1:>9.4f} {t2:>9.4f} {mult:>9.3f}")

    print("\n" + "=" * 74)
    print("THINNING PER MULTISET -- THE UNIT RETRIEVAL ACTUALLY GATES IN")
    print("=" * 74)
    print("A per-stratum rate assumes conversion is independent of the room")
    print("multiset. It is not: ADR 0008's dropped population is over-weighted")
    print("in STOREROOM. Measured per multiset, on the ones with enough sample")
    print("to say anything.\n")
    bym = defaultdict(list)
    for k in keys:
        bym[ms_of(k)].append(k)
    rows = []
    for ms, ks in bym.items():
        if len(ks) < 25:
            continue
        t1 = sum(converted(a[k]) for k in ks) / len(ks)
        t2 = sum(converted(b[k]) for k in ks) / len(ks)
        rows.append((len(ks), t1, t2, ms))
    rows.sort(reverse=True)
    print(f"{'sampled':>8} {'k=1':>8} {'k<=2':>8} {'pool x':>8}  multiset")
    for cnt, t1, t2, ms in rows[:18]:
        desc = " ".join(f"{t.lower()}x{n}" for t, n in ms)
        mult = (t2 / t1) if t1 else float("nan")
        print(f"{cnt:>8} {t1:>8.4f} {t2:>8.4f} {mult:>8.3f}  {desc}")
    if rows:
        m1 = np.array([r[1] for r in rows])
        m2 = np.array([r[2] for r in rows])
        print(f"\nover {len(rows)} multisets with >= 25 sampled dwellings:")
        print(f"  thinning k = 1   median {np.median(m1):.4f}  "
              f"min {m1.min():.4f}  max {m1.max():.4f}")
        print(f"  thinning k <= 2  median {np.median(m2):.4f}  "
              f"min {m2.min():.4f}  max {m2.max():.4f}")
        print(f"  pool multiplier  median {np.median(m2 / np.maximum(m1, 1e-9)):.3f}")
        print("\nThe spread is the point: a single corpus-wide thinning factor")
        print("would under-state the pools that thin hardest, which are the")
        print("ones a Brief in the weak band lands in.")


if __name__ == "__main__":
    main()
