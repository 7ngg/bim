"""Is the corpus that survives conversion the same corpus, only smaller?

The conversion drops 31% of Swiss Dwellings. If what it drops is a random 31%,
the surviving corpus is just smaller. If it drops the dwellings a rectangle model
finds hardest -- which is what it is built to do -- then the Proposer is trained
on a corpus biased toward the boxy, learns boxy priors, and emits boxy plans, and
the metrics would never say so because they are all computed on survivors.

Joins out/swiss_fit.json (converted or not) against out/swiss_rects.json (what
the dwelling was like before conversion) on the dwelling key.

Run: python experiments/rectangularise/survivorship.py [fit.json]
"""
import json
from collections import Counter
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent / "out"


def converted(r):
    """A record converted if the fit returned geometry, at either rectangle count."""
    return "parts" in r or "rects" in r


def main():
    import sys
    name = sys.argv[1] if len(sys.argv) > 1 else "swiss_fit.json"
    print(f"fit: {name}")
    print()
    fit = json.load(open(OUT / name))
    pre = {r["k"]: r for r in json.load(open(OUT / "swiss_rects.json"))["recs"]}

    kept, drop = [], []
    for r in fit:
        p = pre.get(r["k"])
        if p is None or not p.get("bbox"):
            continue
        (kept if converted(r) else drop).append((r, p))
    print(f"joined {len(kept) + len(drop)} dwellings: {len(kept)} converted, "
          f"{len(drop)} dropped\n")

    def stat(rows, f):
        return np.array([f(r, p) for r, p in rows], dtype=float)

    print("=" * 74)
    print("THE DROPPED DWELLINGS ARE NOT A RANDOM SAMPLE")
    print("=" * 74)
    rows = [
        ("rooms", lambda r, p: p["n"]),
        ("mean bbox IoU of its rooms", lambda r, p: float(np.mean(p["bbox"]["iou"]))),
        ("worst room bbox IoU", lambda r, p: float(np.min(p["bbox"]["iou"]))),
        ("floor area m2", lambda r, p: float(sum(p["area"]))),
        ("true contact edges", lambda r, p: p["edges_true"]),
        ("edges per room", lambda r, p: p["edges_true"] / max(p["n"], 1)),
        ("notches needed", lambda r, p: float(r.get("notches_needed", np.nan))),
        ("bbox overlap fraction", lambda r, p: p["bbox"]["overlap_frac"]),
    ]
    print(f"{'quantity':<28} {'converted':>12} {'dropped':>12} {'delta':>10}")
    for label, f in rows:
        a, b = stat(kept, f), stat(drop, f)
        a, b = a[~np.isnan(a)], b[~np.isnan(b)]
        if not len(a) or not len(b):
            continue
        ma, mb = float(np.median(a)), float(np.median(b))
        print(f"{label:<28} {ma:>12.4f} {mb:>12.4f} {mb - ma:>+10.4f}")

    print("\n" + "=" * 74)
    print("WHICH ROOMS ARE OVER-REPRESENTED IN THE DROPPED DWELLINGS")
    print("=" * 74)
    ck, cd = Counter(), Counter()
    for r, p in kept:
        ck.update(p["types"])
    for r, p in drop:
        cd.update(p["types"])
    nk, nd = sum(ck.values()), sum(cd.values())
    print(f"{'room type':<20} {'converted %':>12} {'dropped %':>11} {'ratio':>8}")
    for t, _ in Counter({**ck, **cd}).most_common():
        if ck[t] + cd[t] < 300:
            continue
        a, b = ck[t] / nk, cd[t] / nd
        print(f"{t:<20} {100 * a:>12.2f} {100 * b:>11.2f} {b / a if a else 0:>8.2f}")

    print("\n" + "=" * 74)
    print("THE HEADLINE: RECTANGULARITY OF THE SOURCE DWELLING")
    print("=" * 74)
    ak = np.concatenate([p["bbox"]["iou"] for _, p in kept])
    ad = np.concatenate([p["bbox"]["iou"] for _, p in drop])
    print(f"share of ROOMS that were already rectangles (bbox IoU >= 0.98)")
    print(f"   in dwellings that converted: {np.mean(ak >= .98):.4f}")
    print(f"   in dwellings that dropped:   {np.mean(ad >= .98):.4f}")
    print(f"\ncorpus-wide before conversion: 0.5390")
    print(f"corpus-wide after  conversion: {np.mean(ak >= .98):.4f}"
          f"   <- what the Proposer will be trained on")


if __name__ == "__main__":
    main()
