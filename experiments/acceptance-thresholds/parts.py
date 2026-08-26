"""The same predicates, on the CONVERTED corpus, per constituent rectangle.

Ticket 20. `census.py` measures the raw polygons, which is the right population
for anything well-defined on a polygon. This is the other arm, and it exists
because ADR 0014 binds minimum clear dimensions and aspect **per part**, not per
Room -- so the quantity the shipped rule actually reads is a rectangle's, and
9.85 % of Rooms have two of them.

Two corrections the raw arm does not need and this one does:

  - `parts` are CENTRELINE rectangles on a 250 mm grid (ADR 0008). A part w
    cells wide is 250w mm centreline and 250w - t_int mm clear (ADR 0001).
    Every threshold in `rules.json` is stated clear, so the erosion is applied
    here and only here.
  - the population is the 9.74 % thinner converted corpus, and it under-
    represents the store-heavy and bedroom-heavy dwelling (ADR 0016). Reported,
    never pooled with the raw arm.

Reads experiments/rectangularise/out/swiss_fit_k2.json (2,600 dwellings).

Run: python experiments/acceptance-thresholds/parts.py
"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
FIT = ROOT / "experiments" / "rectangularise" / "out" / "swiss_fit_k2.json"
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)

GRID_MM = 250      # ADR 0008 / ticket 15
T_INT_MM = 150     # ADR 0010, the shipped internal layer set total
BATH_SPLIT_M2 = 2.4

COLLAPSE = {
    "ROOM": "room*", "BEDROOM": "room*", "STUDIO": "room*",
    "LIVING_ROOM": "living", "LIVING_DINING": "living_dining",
    "DINING": "dining", "KITCHEN": "kitchen",
    "KITCHEN_DINING": "kitchen_dining", "CORRIDOR": "corridor",
    "STOREROOM": "storage",
}
EXEMPT = {"corridor", "hall", "storage"}
PCTS = [50, 75, 90, 95, 99, 99.5, 99.9]


def classify(t, area_m2):
    if t == "BATHROOM":
        return "wc" if area_m2 < BATH_SPLIT_M2 else "bathroom"
    return COLLAPSE.get(t, t.lower())


def main():
    recs = json.load(open(FIT))
    ok = [r for r in recs if r.get("status") in ("OPTIMAL", "FEASIBLE")
          and r.get("parts") and r.get("types")]
    print(f"records {len(recs)}, usable {len(ok)}")

    by_cls_aspect = defaultdict(list)
    by_cls_short = defaultdict(list)
    two_part = tot_rooms = 0
    for r in ok:
        parts, types = r["parts"], r["types"]
        if len(parts) != len(types):
            continue
        for p, t in zip(parts, types):
            tot_rooms += 1
            if len(p) > 1:
                two_part += 1
            # Room area from its parts, centreline, to pick the bathroom split
            a_m2 = sum((x1 - x0) * (y1 - y0) for x0, y0, x1, y1 in p) \
                * (GRID_MM / 1000.0) ** 2
            c = classify(t, a_m2)
            for x0, y0, x1, y1 in p:
                w = (x1 - x0) * GRID_MM - T_INT_MM
                h = (y1 - y0) * GRID_MM - T_INT_MM
                if w <= 0 or h <= 0:
                    continue
                lo, hi = min(w, h), max(w, h)
                by_cls_aspect[c].append(hi / lo)
                by_cls_short[c].append(lo)

    lines = []

    def emit(s=""):
        print(s)
        lines.append(s)

    emit(f"converted corpus, {len(ok)} dwellings, {tot_rooms} Rooms, "
         f"{two_part} of them two-part ({two_part / max(tot_rooms, 1):.2%})")
    emit("clear per-part aspect ratio (longer / shorter), CENTRELINE ERODED by "
         f"t_int = {T_INT_MM} mm")
    emit()
    hdr = f"{'class':16}{'n':>8}" + "".join(f"{f'p{p}':>9}" for p in PCTS) + f"{'max':>9}"
    emit(hdr)
    emit("-" * len(hdr))
    binding = [c for c in by_cls_aspect if c not in EXEMPT]
    for c in sorted(by_cls_aspect, key=lambda k: -len(by_cls_aspect[k])):
        v = np.asarray(by_cls_aspect[c])
        tag = c + ("" if c not in EXEMPT else " *exempt")
        emit(f"{tag:16}{len(v):>8}"
             + "".join(f"{np.percentile(v, p):>9.2f}" for p in PCTS)
             + f"{v.max():>9.2f}")
    allb = np.concatenate([by_cls_aspect[c] for c in binding]) if binding else np.array([])
    emit("-" * len(hdr))
    emit(f"{'BINDING (all)':16}{len(allb):>8}"
         + "".join(f"{np.percentile(allb, p):>9.2f}" for p in PCTS)
         + f"{allb.max():>9.2f}")
    emit()
    for thr in (2.2, 2.5, 3.0, 3.5, 4.0):
        emit(f"  parts above {thr:>4}: {(allb > thr).mean():>7.2%} of binding parts")
    emit()
    emit("clear per-part SHORT side, mm")
    emit(f"{'class':16}{'n':>8}{'p1':>9}{'p5':>9}{'p25':>9}{'p50':>9}")
    for c in sorted(by_cls_short, key=lambda k: -len(by_cls_short[k])):
        v = np.asarray(by_cls_short[c])
        emit(f"{c:16}{len(v):>8}"
             + "".join(f"{np.percentile(v, p):>9.0f}" for p in (1, 5, 25, 50)))

    (OUT / "parts.txt").write_text("\n".join(lines), encoding="utf-8")
    json.dump({c: {"n": len(v),
                   "pct": {str(p): float(np.percentile(v, p)) for p in PCTS},
                   "max": float(np.max(v))}
               for c, v in ((c, np.asarray(x)) for c, x in by_cls_aspect.items())},
              open(OUT / "parts_aspect.json", "w"), indent=1)
    print(f"wrote {OUT / 'parts.txt'}")


if __name__ == "__main__":
    main()
