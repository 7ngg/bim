"""Read out/swiss_rects.json and print every table ticket 22 owes.

Run: python experiments/rectangularise/analyse_swiss.py
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent / "out"
CONV = ["bbox", "lir", "apr"]


def q(v, *ps):
    v = np.asarray(v, dtype=float)
    return [float(np.percentile(v, p)) for p in ps]


def main():
    import sys
    src = sys.argv[1] if len(sys.argv) > 1 else "swiss_rects.json"
    blob = json.load(open(OUT / src))
    recs, repairs = blob["recs"], blob["repairs"]
    tot = blob.get("n_dwellings_total") or blob.get("n_plans_total")
    print(f"dwellings measured: {len(recs)}   (of {tot} in corpus, "
          f"4-10 rooms only)   repairs: {repairs}")
    n_rooms = sum(r["n"] for r in recs)
    print(f"rooms: {n_rooms}\n")

    # ---------------------------------------------------------------- 1. per-room loss
    print("=" * 78)
    print("1. PER-ROOM LOSS BY CONVERSION")
    print("=" * 78)
    print(f"{'conv':<6} {'IoU p5':>7} {'p25':>7} {'median':>7} {'p95':>7} "
          f"{'IoU>=.98':>9} {'IoU>=.95':>9} {'IoU>=.90':>9}")
    iou_all = {}
    for c in CONV:
        v = np.array([x for r in recs if r.get(c) for x in r[c]["iou"]])
        iou_all[c] = v
        a, b, m, p95 = q(v, 5, 25, 50, 95)
        print(f"{c:<6} {a:>7.4f} {b:>7.4f} {m:>7.4f} {p95:>7.4f} "
              f"{np.mean(v >= .98):>9.3f} {np.mean(v >= .95):>9.3f} {np.mean(v >= .90):>9.3f}")

    print(f"\n{'conv':<6} {'area err p5':>12} {'p25':>8} {'median':>8} {'p75':>8} "
          f"{'p95':>8} {'mean':>8} {'|err|>5%':>9}")
    for c in CONV:
        v = np.array([x for r in recs if r.get(c) for x in r[c]["aerr"]])
        a, b, m, d, e = q(v, 5, 25, 50, 75, 95)
        print(f"{c:<6} {a:>12.4f} {b:>8.4f} {m:>8.4f} {d:>8.4f} {e:>8.4f} "
              f"{v.mean():>8.4f} {np.mean(np.abs(v) > .05):>9.3f}")

    # ---------------------------------------------------------------- 2. tiling
    print("\n" + "=" * 78)
    print("2. DOES THE DWELLING STILL HOLD TOGETHER")
    print("=" * 78)
    print(f"{'conv':<6} {'overlap frac med':>17} {'p95':>8} {'max':>8} "
          f"{'dwell w/ overlap':>17} {'outside env med':>16} {'p95':>8}")
    for c in CONV:
        ov = np.array([r[c]["overlap_frac"] for r in recs if r.get(c)])
        oe = np.array([r[c]["outside_env"] for r in recs if r.get(c)])
        print(f"{c:<6} {np.median(ov):>17.5f} {np.percentile(ov, 95):>8.5f} "
              f"{ov.max():>8.4f} {np.mean(ov > 1e-6):>17.3f} "
              f"{np.median(oe):>16.5f} {np.percentile(oe, 95):>8.5f}")

    # ---------------------------------------------------------------- 3. adjacency
    print("\n" + "=" * 78)
    print("3. CONTACT GRAPH SURVIVAL   (run >= 1.0 m, wall tolerance 0.30 m)")
    print("=" * 78)
    et = np.array([r["edges_true"] for r in recs])
    print(f"true edges per dwelling: mean {et.mean():.2f}  median {np.median(et):.0f}")
    print(f"\n{'conv':<6} {'lost/dwell':>11} {'gained/dwell':>13} {'edges kept':>11} "
          f"{'exact graph':>12} {'>=1 lost':>9} {'>=1 gained':>11}")
    for c in CONV:
        lo = np.array([r[c]["lost"] for r in recs if r.get(c)])
        ga = np.array([r[c]["gained"] for r in recs if r.get(c)])
        tr = np.array([r["edges_true"] for r in recs if r.get(c)])
        print(f"{c:<6} {lo.mean():>11.3f} {ga.mean():>13.3f} "
              f"{1 - lo.sum() / max(tr.sum(), 1):>11.4f} "
              f"{np.mean((lo == 0) & (ga == 0)):>12.3f} "
              f"{np.mean(lo > 0):>9.3f} {np.mean(ga > 0):>11.3f}")

    # ---------------------------------------------------------------- 3b. relations
    if any(r.get("bbox", {}).get("rel") for r in recs if r.get("bbox")):
        print("\n" + "=" * 78)
        print("3b. SEPARATION-DIRECTION AGREEMENT   (what the Proposal actually transmits)")
        print("=" * 78)
        pa = sum(r["pairs_asserted"] for r in recs)
        pp = sum(r["pairs"] for r in recs)
        print(f"room pairs: {pp}   asserted on at least one axis: {pa} ({pa/pp:.3f})")
        print(f"\n{'conv':<6} {'axis-rel same':>14} {'weakened':>10} {'spurious':>10} "
              f"{'flipped':>9} {'pairs made up':>14} {'pairs dropped':>14}")
        for c in CONV:
            k = Counter()
            for r in recs:
                if r.get(c) and r[c].get("rel"):
                    k.update(r[c]["rel"])
            tot_ax = k["same"] + k["weakened"] + k["spurious"] + k["flipped"]
            if not tot_ax:
                continue
            print(f"{c:<6} {k['same']/tot_ax:>14.4f} {k['weakened']/tot_ax:>10.4f} "
                  f"{k['spurious']/tot_ax:>10.4f} {k['flipped']/tot_ax:>9.4f} "
                  f"{k['pair_spurious']:>14} {k['pair_weakened']:>14}")

    # ---------------------------------------------------------------- 4. graph2plan
    print("\n" + "=" * 78)
    print("4. GRAPH2PLAN'S CLAIM ON THIS CORPUS   (area of bbox n envelope / true area)")
    print("=" * 78)
    g = np.array([x for r in recs for x in r["g2p_ratio"]])
    print(f"rooms n={len(g)}   ratio 1.00 means the bbox adds nothing the envelope "
          f"does not already cut away")
    print(f"  <=1.02: {np.mean(g <= 1.02):.4f}   <=1.05: {np.mean(g <= 1.05):.4f}   "
          f"<=1.10: {np.mean(g <= 1.10):.4f}   median {np.median(g):.4f}")
    fill = iou_all["bbox"]
    print(f"  bbox alone (IoU) <=2% loss: {np.mean(fill >= .98):.4f}")
    print(f"  => share of non-rectangularity the ENVELOPE explains, at 2%: "
          f"{(np.mean(g <= 1.02) - np.mean(fill >= .98)) / max(1 - np.mean(fill >= .98), 1e-9):.4f}")

    # ---------------------------------------------------------------- 5. by room type
    print("\n" + "=" * 78)
    print("5. WHICH ROOMS ARE NOT RECTANGLES   (bbox IoU, types with n>=2000)")
    print("=" * 78)
    by = defaultdict(list)
    for r in recs:
        if not r.get("bbox"):
            continue
        for t, v, a in zip(r["types"], r["bbox"]["iou"], r["area"]):
            by[t].append((v, a))
    rows = [(t, len(v), float(np.median([x[0] for x in v])),
             float(np.mean([x[0] >= .98 for x in v])),
             float(np.median([x[1] for x in v])))
            for t, v in by.items() if len(v) >= 2000]
    rows.sort(key=lambda r: -r[1])
    print(f"{'type':<20} {'n':>7} {'IoU med':>8} {'rect@2%':>8} {'area med':>9}")
    for t, n, m, f, a in rows:
        print(f"{t:<20} {n:>7} {m:>8.4f} {f:>8.3f} {a:>9.2f}")

    # ---------------------------------------------------------------- 6. reject rule
    print("\n" + "=" * 78)
    print("6. THE REJECT RULE - WHAT EACH GATE COSTS")
    print("=" * 78)
    N = len(recs)
    print(f"population: {N} dwellings, 4-10 rooms\n")

    print("gate A - worst room IoU in the dwelling (bbox):")
    worst = np.array([min(r["bbox"]["iou"]) for r in recs if r.get("bbox")])
    for th in (.80, .85, .90, .92, .95, .98):
        print(f"   keep worst-IoU >= {th:.2f}:  kept {np.mean(worst >= th):.4f}   "
              f"dropped {int(np.sum(worst < th))}")

    print("\ngate B - contact graph exact (bbox):")
    for c in CONV:
        lo = np.array([r[c]["lost"] for r in recs if r.get(c)])
        ga = np.array([r[c]["gained"] for r in recs if r.get(c)])
        print(f"   {c}: keep lost==0 and gained==0 -> kept {np.mean((lo == 0) & (ga == 0)):.4f} "
              f"({int(np.sum((lo > 0) | (ga > 0)))} dropped)")
        print(f"   {c}: keep lost==0 only          -> kept {np.mean(lo == 0):.4f} "
              f"({int(np.sum(lo > 0))} dropped)")

    print("\ngate C - joint, on the recommended conversion:")
    for c in CONV:
        w = np.array([min(r[c]["iou"]) for r in recs if r.get(c)])
        lo = np.array([r[c]["lost"] for r in recs if r.get(c)])
        ga = np.array([r[c]["gained"] for r in recs if r.get(c)])
        for th in (.85, .90):
            k = (w >= th) & (lo == 0) & (ga == 0)
            print(f"   {c}: worst IoU>={th:.2f} AND graph exact -> kept {k.mean():.4f} "
                  f"({int((~k).sum())} dropped of {len(k)})")

    # ---------------------------------------------------------------- 7. band
    print("\n" + "=" * 78)
    print("7. WHAT SURVIVES, BY ROOM COUNT   (bbox, worst IoU >= 0.90 and graph exact)")
    print("=" * 78)
    print(f"{'rooms':>6} {'dwellings':>10} {'kept':>8} {'kept n':>8}")
    for n in range(4, 11):
        sub = [r for r in recs if r["n"] == n and r.get("bbox")]
        if not sub:
            continue
        k = [min(r["bbox"]["iou"]) >= .90 and r["bbox"]["lost"] == 0
             and r["bbox"]["gained"] == 0 for r in sub]
        print(f"{n:>6} {len(sub):>10} {np.mean(k):>8.4f} {int(np.sum(k)):>8}")


if __name__ == "__main__":
    main()
