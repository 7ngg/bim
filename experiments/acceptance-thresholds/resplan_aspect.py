"""The aspect-ratio question on the second corpus.

Ticket 20. `dim.aspect_ratio_hard` was BELIEVED to be the one rule in the spec
with no precedent anywhere, so it is the one threshold that must not rest on a
single corpus.

CORRECTED by ticket 72 / ADR 0048: precedent exists -- [1/3, 3] is the modal hard
aspect bound in VLSI floorplanning, and regulators bound an ORIENTED depth ratio
which is a different predicate from the one measured here. The reason to run this
script is UNCHANGED and if anything stronger: the second corpus is still what keeps
a fitted threshold off a single population. Nothing measured here moves. This measures the same quantity -- bbox aspect in the plan's own frame,
clear plane -- over ResPlan.

Two limits, stated rather than worked around (`docs/research/rectangularisation.md`
3 and 6.5):

  - ResPlan has FOUR classes and no corridor at all: circulation is folded into
    `living`, which "wraps every other room". So ResPlan's `living` aspect is
    not the same quantity as Swiss `living` and is reported separately, never
    pooled.
  - the corpora are never pooled anyway (*Cross-dataset unification*).

Run: python experiments/acceptance-thresholds/resplan_aspect.py
"""
import io
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from shapely.affinity import rotate, scale

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "rectangularise"))
import measure_resplan as MR  # noqa: E402
from measure_swiss import BAND, MIN_ROOM_AREA, _poly, dwelling_frame  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)
PCTS = [50, 75, 90, 95, 99, 99.5, 99.9]
BINDING = {"bedroom", "kitchen", "bathroom"}   # living excluded: see docstring


def main():
    with io.open(MR.PKL, "rb") as f:
        plans = MR.Restricted(f).load()
    print(f"plans: {len(plans)}")

    asp = defaultdict(list)
    dwell = []
    kept = 0
    for pid, p in (plans.items() if isinstance(plans, dict) else enumerate(plans)):
        if isinstance(pid, int) and pid in MR.BROKEN_IDS:
            continue
        geoms, types = [], []
        for k in MR.ROOM_KEYS:
            for g in MR.parts(p.get(k)):
                g = _poly(g)
                if g is not None:
                    geoms.append(g)
                    types.append(k)
        if not geoms:
            continue
        canvas = sum(g.area for g in geoms)
        for k in MR.NOT_A_ROOM_KEYS:
            canvas += sum(g.area for g in MR.parts(p.get(k)) if hasattr(g, "area"))
        area = p.get("area")
        if not area or canvas <= 0 or float(area) < MR.MIN_PLAN_AREA:
            continue
        mpu = (float(area) / canvas) ** 0.5
        geoms = [scale(g, mpu, mpu, origin=(0, 0)) for g in geoms]
        keep = [(g, t) for g, t in zip(geoms, types) if g.area >= MIN_ROOM_AREA]
        if not keep:
            continue
        geoms, types = [g for g, _ in keep], [t for _, t in keep]
        if not (BAND[0] <= len(geoms) <= BAND[1]):
            continue
        ang, cen = dwelling_frame(geoms)
        if ang is None:
            continue
        geoms = [rotate(g, -ang, origin=cen) for g in geoms]
        kept += 1
        worst = 0.0
        for g, t in zip(geoms, types):
            x0, y0, x1, y1 = g.bounds
            lo, hi = min(x1 - x0, y1 - y0), max(x1 - x0, y1 - y0)
            if lo <= 0:
                continue
            a = hi / lo
            asp[t].append(a)
            if t in BINDING:
                worst = max(worst, a)
        dwell.append(worst)

    lines = []

    def emit(s=""):
        print(s)
        lines.append(s)

    emit(f"ResPlan, {kept} in-band plans, bbox aspect in the plan's own frame")
    hdr = f"{'class':16}{'n':>8}" + "".join(f"{f'p{p}':>9}" for p in PCTS) + f"{'max':>9}"
    emit(hdr)
    emit("-" * len(hdr))
    for t in sorted(asp, key=lambda k: -len(asp[k])):
        v = np.asarray(asp[t])
        tag = t + ("" if t in BINDING else "  (circulation folded in)")
        emit(f"{tag:16}{len(v):>8}"
             + "".join(f"{np.percentile(v, p):>9.2f}" for p in PCTS)
             + f"{v.max():>9.2f}")
    allb = np.concatenate([asp[t] for t in BINDING if asp[t]])
    emit("-" * len(hdr))
    emit(f"{'BINDING (3)':16}{len(allb):>8}"
         + "".join(f"{np.percentile(allb, p):>9.2f}" for p in PCTS)
         + f"{allb.max():>9.2f}")
    emit()
    emit(f"{'threshold':>10}{'rooms above':>14}{'plans rejected':>18}")
    cost = {}
    dw = np.asarray(dwell)
    for thr in (2.2, 2.5, 3.0, 3.2, 3.5, 4.0, 4.5, 5.0):
        cost[thr] = {"rooms": float((allb > thr).mean()),
                     "plans": float((dw > thr).mean())}
        emit(f"{thr:>10.1f}{(allb > thr).mean():>13.2%}{(dw > thr).mean():>17.2%}")

    (OUT / "resplan_aspect.txt").write_text("\n".join(lines), encoding="utf-8")
    json.dump({"n_plans": kept, "cost": cost,
               "by_class": {t: {"n": len(v),
                                **{f"p{p}": float(np.percentile(v, p))
                                   for p in PCTS}}
                            for t, v in ((t, np.asarray(x))
                                         for t, x in asp.items())},
               "src": "resplan_raw_polygon_bbox"},
              open(OUT / "resplan_aspect.json", "w"), indent=1)
    print(f"wrote {OUT / 'resplan_aspect.txt'}")


if __name__ == "__main__":
    main()
