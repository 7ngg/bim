"""What a second rectangle per Room buys the conversion.

Ticket 40. ADR 0008's conversion drops 31 % of Swiss Dwellings, and that price
was paid for a one-rectangle constraint ADR 0014 has since removed. This joins
the two arms on the dwelling key -- the SAME dwellings, in the same order, run
through the same code with only `k_of` changed -- so the delta is the rectangle
count and not the sample.

Three things it is careful about, because each one can turn a rig artefact into
a finding:

  UNDECIDED IS NOT DROPPED. The reject rule is representability: a dwelling is
  dropped when no rectangular tiling exists, which is INFEASIBLE. UNKNOWN is the
  solver running out of time and has no verdict at all. At k = 1 there are none;
  at k <= 2 there are, so they are counted apart and never folded into either
  column.

  FEASIBLE IS NOT OPTIMAL. At k = 1 every dwelling that converts converts
  OPTIMALLY, so every fidelity number is the best available. At k <= 2 some come
  back FEASIBLE, where the loss reported is an upper bound on the true loss.
  Fidelity comparisons are therefore also split by proof status.

  DESIGN A IS A LOWER BOUND. Which Rooms may take a second rectangle is named
  from the real room's own shape, not searched (ADR 0014's Design A, and
  `fit_rects.run_dwelling` records why Design B is unmeasurable at the shipped
  budget). A Room the naming heuristic misses is a Room that stayed one
  rectangle, so whatever this measures, the true k <= 2 conversion rate is at
  least it.

Run: python experiments/rectangularise/analyse_k2.py [k1.json] [k2.json]
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent / "out"

DECIDED_OK = ("OPTIMAL", "FEASIBLE")


def converted(r):
    return r["status"] in DECIDED_OK


def undecided(r):
    return r["status"] == "UNKNOWN"


def rule(title):
    print("\n" + "=" * 76)
    print(title)
    print("=" * 76)


def mcnemar(b, c):
    """Exact two-sided binomial p for the discordant pairs. No scipy dependency.

    b = converted at k=1 only, c = converted at k<=2 only. Under the null the
    discordant pairs split 50/50, so this is a sign test on b + c trials.
    """
    n = b + c
    if n == 0:
        return 1.0
    from math import comb
    k = min(b, c)
    tail = sum(comb(n, i) for i in range(0, k + 1))
    return min(1.0, 2.0 * tail / (2 ** n))


def main():
    f1 = sys.argv[1] if len(sys.argv) > 1 else "swiss_fit_k1.json"
    f2 = sys.argv[2] if len(sys.argv) > 2 else "swiss_fit_k2.json"
    a = {r["k"]: r for r in json.load(open(OUT / f1))}
    b = {r["k"]: r for r in json.load(open(OUT / f2))}
    keys = [k for k in b if k in a]
    print(f"k = 1   {f1}   {len(a)} records")
    print(f"k <= 2  {f2}   {len(b)} records")
    print(f"paired on {len(keys)} dwellings")

    A = [a[k] for k in keys]
    B = [b[k] for k in keys]

    # ---------------------------------------------------------------- status
    rule("STATUS, BOTH ARMS")
    print(f"{'status':<22} {'k = 1':>10} {'k <= 2':>10}")
    for st in sorted(set([r["status"] for r in A] + [r["status"] for r in B])):
        print(f"{st:<22} {sum(1 for r in A if r['status'] == st):>10} "
              f"{sum(1 for r in B if r['status'] == st):>10}")

    und = [k for k in keys if undecided(b[k]) or undecided(a[k])]
    print(f"\nundecided in either arm: {len(und)}  "
          f"({len(und) / max(len(keys), 1):.4f})")
    print("Excluded from every rate below: a timeout has no verdict, and")
    print("counting it as a drop would report the time limit as a finding.")

    dec = [k for k in keys if not (undecided(a[k]) or undecided(b[k]))]
    A_, B_ = [a[k] for k in dec], [b[k] for k in dec]

    # ------------------------------------------------------------- the number
    rule("THE CONVERSION RATE")
    c1 = sum(converted(r) for r in A_)
    c2 = sum(converted(r) for r in B_)
    n = len(dec)
    print(f"decided in both arms: {n}")
    print(f"  k = 1   converted {c1:>5} / {n}   {c1 / n:.4f}   "
          f"dropped {1 - c1 / n:.4f}")
    print(f"  k <= 2  converted {c2:>5} / {n}   {c2 / n:.4f}   "
          f"dropped {1 - c2 / n:.4f}")
    print(f"  the drop moves {1 - c1 / n:.4f} -> {1 - c2 / n:.4f}   "
          f"({(1 - c2 / n) - (1 - c1 / n):+.4f}, "
          f"{100 * (1 - (1 - c2 / n) / max(1 - c1 / n, 1e-9)):+.1f} % of it)")

    tab = Counter((converted(x), converted(y)) for x, y in zip(A_, B_))
    gain, lose = tab[(False, True)], tab[(True, False)]
    print(f"\npaired table")
    print(f"  both converted          {tab[(True, True)]:>5}")
    print(f"  k <= 2 gained           {gain:>5}")
    print(f"  k <= 2 lost             {lose:>5}   "
          f"(must be 0: Design A is a strict relaxation)")
    print(f"  both dropped            {tab[(False, False)]:>5}")
    print(f"  McNemar exact p = {mcnemar(lose, gain):.3g}")

    # ------------------------------------------------------------ by n rooms
    rule("BY ROOM COUNT -- WHERE THE INDEX WAS THINNEST")
    print("83 % at 4 rooms against 46 % at 10 is what thins retrieval exactly")
    print("where proposer.md 2.1 already showed it weakest.\n")
    print(f"{'n':>4} {'dwellings':>10} {'k=1':>9} {'k<=2':>9} {'delta':>9} "
          f"{'drop k=1':>10} {'drop k<=2':>10}")
    byn = defaultdict(list)
    for x, y in zip(A_, B_):
        if x.get("n"):
            byn[x["n"]].append((x, y))
    for nn in sorted(byn):
        rows = byn[nn]
        p1 = sum(converted(x) for x, _ in rows) / len(rows)
        p2 = sum(converted(y) for _, y in rows) / len(rows)
        print(f"{nn:>4} {len(rows):>10} {p1:>9.4f} {p2:>9.4f} {p2 - p1:>+9.4f} "
              f"{1 - p1:>10.4f} {1 - p2:>10.4f}")

    # ------------------------------------------------------- how many take it
    rule("HOW OFTEN A ROOM ACTUALLY BECOMES TWO RECTANGLES")
    # Both rates over the CONVERTED records only: `k_offered` is emitted for
    # every record and `k_used` only where there is geometry, so counting them
    # over different denominators silently compares different populations.
    off = Counter()
    used = Counter()
    for r in B_:
        if not converted(r):
            continue
        for k in r.get("k_offered", []):
            off[k] += 1
        for k in r.get("k_used", []):
            used[k] += 1
    no = sum(off.values()) or 1
    nu = sum(used.values()) or 1
    print(f"offered a second rectangle: {off[2]:>6} / {no}  {off[2] / no:.4f}")
    print(f"fitted as two rectangles:   {used[2]:>6} / {nu}  {used[2] / nu:.4f}")
    print("\nADR 0014 measured 52.9 % of real Swiss rooms as exactly one")
    print("rectangle, so 47 % need two or more at a 98 % tolerance. The gap")
    print("between that and the offered rate is the naming heuristic's")
    print("conservatism, and it is why this whole table is a LOWER bound.")

    rule("WHICH ROOM TYPES TAKE THE SECOND RECTANGLE")
    print("Labelled from the FILTERED polygon list -- ticket 27's off-by-one")
    print("defect is fixed at source in fit_rects.load_swiss_geoms.\n")
    t_off, t_used, t_all = Counter(), Counter(), Counter()
    for r in B_:
        ty = r.get("types") or []
        for t, ko in zip(ty, r.get("k_offered", [])):
            t_all[t] += 1
            if ko > 1:
                t_off[t] += 1
        for t, ku in zip(ty, r.get("k_used", [])):
            if ku > 1:
                t_used[t] += 1
    print(f"{'room type':<22} {'rooms':>8} {'offered':>9} {'fitted 2':>9}")
    for t, c in t_all.most_common():
        if c < 100:
            continue
        print(f"{t:<22} {c:>8} {t_off[t] / c:>9.4f} {t_used[t] / c:>9.4f}")

    # ------------------------------------------------------------- fidelity
    rule("FIDELITY, ON THE DWELLINGS BOTH ARMS CONVERT")
    both = [(x, y) for x, y in zip(A_, B_) if converted(x) and converted(y)]
    print(f"{len(both)} dwellings\n")

    def col(rows, pick, f):
        v = [f(r) for r in (x if pick == 0 else y for x, y in rows)]
        v = [q for q in v if q is not None and not np.isnan(q)]
        return np.array(v, dtype=float)

    metrics = [
        ("cell agreement", lambda r: r.get("cell_agreement")),
        ("median room IoU", lambda r: float(np.median(r["iou"])) if r.get("iou") else None),
        ("worst room IoU", lambda r: float(np.min(r["iou"])) if r.get("iou") else None),
        ("mean |area error|", lambda r: float(np.mean(np.abs(r["aerr"]))) if r.get("aerr") else None),
        ("adjacencies lost", lambda r: r.get("edges_lost")),
        ("relations flipped", lambda r: r.get("rel", {}).get("flipped", 0)),
        ("relations weakened", lambda r: r.get("rel", {}).get("weakened", 0)),
        ("relations spurious", lambda r: r.get("rel", {}).get("spurious", 0)),
        ("spurious share", lambda r: (r.get("rel", {}).get("spurious", 0) /
                                      max(sum(r.get("rel", {}).values()), 1))),
        ("boundary contacts lost", lambda r: r.get("boundary_lost")),
        ("solve seconds", lambda r: r.get("seconds")),
    ]
    print(f"{'quantity':<24} {'k=1 median':>12} {'k<=2 median':>12} {'delta':>10}")
    for label, f in metrics:
        u, v = col(both, 0, f), col(both, 1, f)
        if not len(u) or not len(v):
            continue
        mu, mv = float(np.median(u)), float(np.median(v))
        print(f"{label:<24} {mu:>12.4f} {mv:>12.4f} {mv - mu:>+10.4f}")

    print("\nmeans, for the counts where a median of 0 hides the movement")
    print(f"{'quantity':<24} {'k=1 mean':>12} {'k<=2 mean':>12} {'delta':>10}")
    for label, f in metrics:
        u, v = col(both, 0, f), col(both, 1, f)
        if not len(u) or not len(v):
            continue
        print(f"{label:<24} {u.mean():>12.4f} {v.mean():>12.4f} "
              f"{v.mean() - u.mean():>+10.4f}")

    rule("THE RELATIONS A RECTANGLE MODEL HAS TO INVENT")
    print("ADR 0008 kept every asserted separation and ADDED one on the pairs")
    print("the truth abstained on -- 15.7 % of axis-pairs -- because one")
    print("rectangle must pick a side when a room wraps another. An L does not")
    print("have to. Ticket 23 marks those pairs as the ones a warp is least")
    print("entitled to trust, so this is the number that moves for it.\n")
    for lbl, idx in (("k = 1", 0), ("k <= 2", 1)):
        tot = Counter()
        for x, y in both:
            tot.update((x if idx == 0 else y).get("rel", {}))
        s = sum(tot.values()) or 1
        print(f"{lbl:<8} same {tot['same'] / s:.4f}   spurious {tot['spurious'] / s:.4f} "
              f"  weakened {tot['weakened'] / s:.4f}   flipped {tot['flipped'] / s:.4f}"
              f"   ({s} axis-pairs)")

    rule("THE DWELLINGS ONLY k <= 2 CONVERTS")
    gained = [(x, y) for x, y in zip(A_, B_) if not converted(x) and converted(y)]
    print(f"{len(gained)} dwellings. If these convert markedly worse than the")
    print("ones that already converted, the gain is nominal.\n")
    if gained:
        print(f"{'quantity':<24} {'both-convert':>13} {'newly gained':>13}")
        for label, f in metrics:
            u = col(both, 1, f)
            v = col(gained, 1, f)
            if not len(u) or not len(v):
                continue
            print(f"{label:<24} {float(np.median(u)):>13.4f} "
                  f"{float(np.median(v)):>13.4f}")
        ku = Counter()
        for _, y in gained:
            for k in y.get("k_used", []):
                ku[k] += 1
        t = sum(ku.values()) or 1
        print(f"\nrooms fitted as two rectangles in the gained dwellings: "
              f"{ku[2] / t:.4f}  (against {used[2] / nu:.4f} overall)")

    rule("PROOF STATUS -- HOW MUCH OF THE FIDELITY IS AN UPPER BOUND")
    for lbl, rows in (("k = 1", A_), ("k <= 2", B_)):
        c = Counter(r["status"] for r in rows)
        ok = c["OPTIMAL"] + c["FEASIBLE"]
        print(f"{lbl:<8} of {ok} converted, {c['OPTIMAL']} proved optimal "
              f"({c['OPTIMAL'] / max(ok, 1):.4f}), {c['FEASIBLE']} feasible only")


if __name__ == "__main__":
    main()
