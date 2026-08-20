"""Read out/swiss_fit.json and print what the joint fit costs.

Run: python experiments/rectangularise/analyse_fit.py [swiss_fit.json]
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent / "out"


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "swiss_fit.json"
    recs = json.load(open(OUT / src))
    n = len(recs)
    st = Counter(r["status"] for r in recs)
    print(f"dwellings attempted: {n}")
    print("\n" + "=" * 78)
    print("1. WHAT HAPPENS TO A REAL DWELLING")
    print("=" * 78)
    for k, v in st.most_common():
        print(f"  {k:<24} {v:>6}  {v / n:.4f}")
    ok = [r for r in recs if "rects" in r]
    print(f"\n  converted: {len(ok)} / {n} = {len(ok) / n:.4f}")

    # ------------------------------------------------------------ notches
    print("\n" + "=" * 78)
    print("2. ADR 0003's TWO-NOTCH CAP, MEASURED FOR THE FIRST TIME")
    print("=" * 78)
    nn = np.array([r["notches_needed"] for r in recs if "notches_needed" in r])
    na = np.array([r["notches_all"] for r in recs if "notches_all" in r])
    if len(nn):
        print(f"notches a real dwelling needs (components >= 0.25 m2), n={len(nn)}")
        h = Counter(int(x) for x in nn)
        for k in sorted(h):
            print(f"   {k:>2} notches: {h[k]:>6}  {h[k] / len(nn):.4f}"
                  f"   cumulative {sum(h[j] for j in sorted(h) if j <= k) / len(nn):.4f}")
        print(f"   median {np.median(nn):.1f}   p90 {np.percentile(nn, 90):.1f}"
              f"   share <= 2: {np.mean(nn <= 2):.4f}")
        print(f"   (counting every complement component, including raster slivers: "
              f"median {np.median(na):.1f})")
    lad = defaultdict(list)
    for r in recs:
        for k, v in (r.get("envelope_loss_by_k") or {}).items():
            lad[int(k)].append(v)
    if lad:
        print("\nenvelope area misdescribed by a bbox-minus-k-notches Envelope:")
        print(f"   {'k':>2} {'median':>9} {'p75':>9} {'p95':>9}")
        for k in sorted(lad):
            v = np.array(lad[k])
            print(f"   {k:>2} {np.median(v):>9.4f} {np.percentile(v, 75):>9.4f} "
                  f"{np.percentile(v, 95):>9.4f}")

    if not ok:
        return

    # ------------------------------------------------------------ loss
    print("\n" + "=" * 78)
    print("3. WHAT THE CONVERSION COSTS")
    print("=" * 78)
    iou = np.array([x for r in ok for x in r["iou"]])
    ag = np.array([r["cell_agreement"] for r in ok])
    unc = np.array([r["uncovered"] / max(r["cells"], 1) for r in ok])
    aer = np.array([x for r in ok for x in r["aerr"]])
    print(f"per-room IoU        p5 {np.percentile(iou, 5):.4f}  p25 {np.percentile(iou, 25):.4f}"
          f"  median {np.median(iou):.4f}  >=0.90 {np.mean(iou >= .90):.4f}")
    print(f"cell agreement      p5 {np.percentile(ag, 5):.4f}  p25 {np.percentile(ag, 25):.4f}"
          f"  median {np.median(ag):.4f}  >=0.90 {np.mean(ag >= .90):.4f}")
    print(f"uncovered fraction  median {np.median(unc):.5f}  p95 {np.percentile(unc, 95):.5f}")
    print(f"per-room area error median {np.median(aer):+.4f}  mean {aer.mean():+.4f}"
          f"  |err|>10% {np.mean(np.abs(aer) > .10):.4f}")
    lost = sum(r["edges_lost"] for r in ok)
    tot_e = sum(r["edges_true"] for r in ok)
    print(f"adjacencies destroyed: {lost} of {tot_e}  ({lost / max(tot_e, 1):.6f})"
          f"   <- hard-constrained; non-zero means the model is wrong")

    rel = Counter()
    for r in ok:
        rel.update(r.get("rel", {}))
    tot_ax = sum(rel[k] for k in ("same", "weakened", "spurious", "flipped"))
    if tot_ax:
        print("\nseparation directions, fit vs the real dwelling "
              "(bbox preserves all of these for free):")
        for k in ("same", "weakened", "spurious", "flipped"):
            print(f"   {k:<10} {rel[k]:>8}  {rel[k] / tot_ax:.4f}")

    sec = np.array([r["seconds"] for r in recs if "seconds" in r])
    print(f"\nsolve seconds: median {np.median(sec):.2f}  p95 {np.percentile(sec, 95):.2f}"
          f"  mean {sec.mean():.2f}")

    # ------------------------------------------------------------ by n
    print("\n" + "=" * 78)
    print("4. BY ROOM COUNT")
    print("=" * 78)
    print(f"{'rooms':>6} {'tried':>7} {'converted':>10} {'IoU med':>9} {'agree med':>10}")
    for k in range(4, 11):
        sub = [r for r in recs if r.get("n") == k]
        good = [r for r in sub if "rects" in r]
        if not sub:
            continue
        i = [x for r in good for x in r["iou"]]
        a = [r["cell_agreement"] for r in good]
        print(f"{k:>6} {len(sub):>7} {len(good) / len(sub):>10.4f} "
              f"{(np.median(i) if i else float('nan')):>9.4f} "
              f"{(np.median(a) if a else float('nan')):>10.4f}")

    # ------------------------------------------------------------ gate
    print("\n" + "=" * 78)
    print("5. THE REJECT RULE, AND WHAT IT COSTS")
    print("=" * 78)
    print(f"hard gate -- the fit returns a tiling at all: kept {len(ok) / n:.4f} "
          f"({n - len(ok)} dropped of {n})")
    for th in (.70, .75, .80, .85, .90):
        k = np.mean(ag >= th) * len(ok) / n
        print(f"   plus cell agreement >= {th:.2f}: kept {k:.4f} "
              f"({n - int(round(k * n))} dropped)")


if __name__ == "__main__":
    main()
