"""Ticket 33 — the second corpus's view of an internal wall thickness.

ResPlan 17k is the only other metric-recoverable corpus on disk (RPLAN, MSD and
ProcTHOR directories are empty — `docs/research/dataset-inventory.md` §3). It is
not metric as shipped: polygons sit on a ~256-unit canvas whose scale varies per
plan, so metres-per-unit is recovered per plan as `sqrt(area / polygon_area)`
exactly as the inventory prescribes.

Two things are asked of it, and the second is the more interesting:

  1. what is a ResPlan wall depth in millimetres?
  2. **how many wall depths does a ResPlan plan have?**  The schema answer is
     one — `wall_depth` is a per-plan SCALAR — so this corpus cannot corroborate
     or refute within-dwelling mixing. It assumes uniformity. That is worth
     recording rather than quietly using as agreement.

The `wall` geometry is measured independently of the scalar, so the scalar is
checked rather than trusted.

Run:  python experiments/thickness-fidelity/resplan_thickness.py [n]
"""
from __future__ import annotations

import math
import pickle
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from shapely.geometry.base import BaseMultipartGeometry

ROOT = Path(__file__).resolve().parents[2]
PKL = ROOT / "data" / "corpora" / "resplan" / "ResPlan.pkl"

# Same restricted unpickler as experiments/corpus-smoke/smoke_resplan.py: a
# third-party pickle does not get to execute arbitrary code on load.
ALLOWED = {("shapely.io", "from_wkb"), ("numpy", "dtype"),
           ("numpy._core.multiarray", "scalar"),
           ("numpy.core.multiarray", "scalar")}


class R(pickle.Unpickler):
    def find_class(self, m, n):
        if (m, n) not in ALLOWED:
            raise pickle.UnpicklingError(f"blocked {m}.{n}")
        return super().find_class(m, n)


def parts(g):
    if g is None:
        return []
    if isinstance(g, (list, tuple)):
        return [x for e in g for x in parts(e)]
    if isinstance(g, BaseMultipartGeometry):
        return [x for x in g.geoms if not x.is_empty]
    return [] if g.is_empty else [g]


def strip_width(p):
    """Minor side of the minimum rotated rectangle, if the part is a strip."""
    mrr = p.minimum_rotated_rectangle
    if mrr is None or mrr.is_empty or mrr.geom_type != "Polygon" or mrr.area <= 0:
        return None
    if p.area / mrr.area < 0.95:
        return None
    c = list(mrr.exterior.coords)[:4]
    a = math.dist(c[0], c[1])
    b = math.dist(c[1], c[2])
    if min(a, b) <= 0:
        return None
    return min(a, b), max(a, b)


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    plans = R(open(PKL, "rb")).load()
    if n:
        plans = plans[:n]
    print(f"plans: {len(plans):,}")

    depths_mm, scales = [], []
    widths_mm, widths_len = [], []
    per_plan_classes = Counter()
    scalar_keys = Counter()
    n_parts = [0]

    for p in plans:
        inner = parts(p.get("inner"))
        if not inner or not p.get("area"):
            continue
        px = sum(g.area for g in inner)
        if px <= 0:
            continue
        s = math.sqrt(float(p["area"]) / px)          # metres per canvas unit
        scales.append(s)
        wd = p.get("wall_depth")
        if wd:
            depths_mm.append(float(wd) * s * 1000.0)

        ws = []
        for g in parts(p.get("wall")):
            n_parts[0] += 1
            r = strip_width(g)
            if r is None:
                continue
            t, L = r
            t_mm = t * s * 1000.0
            if 20 <= t_mm <= 900 and L * s >= 0.30:
                ws.append((round(t_mm), L * s))
        widths_mm.extend(t for t, _ in ws)
        widths_len.extend(L for _, L in ws)
        if ws:
            # how many distinct widths does one plan's own wall geometry hold,
            # folding classes under 5 % of the plan's wall length
            tot = sum(L for _, L in ws)
            acc: dict[int, float] = {}
            for t, L in sorted(ws, key=lambda x: -x[1]):
                for k in list(acc):
                    if abs(k - t) <= 10:
                        acc[k] += L
                        break
                else:
                    acc[t] = L
            per_plan_classes[min(sum(1 for v in acc.values()
                                     if v >= 0.05 * tot), 6)] += 1

    for k in ("wall_depth",):
        scalar_keys[k] = sum(1 for p in plans if p.get(k) is not None)
    print(f"plans carrying a scalar `wall_depth`: {scalar_keys['wall_depth']:,}"
          f"   -- ONE value per plan, by schema")

    d = np.array(depths_mm)
    print(f"\nscalar `wall_depth` in mm (per-plan scale recovered): n={len(d):,}")
    print("   " + "  ".join(f"p{q}={np.percentile(d, q):.0f}"
                            for q in (5, 25, 50, 75, 95))
          + f"   mean {d.mean():.0f}")

    w = np.array(widths_mm, float)
    Lw = np.array(widths_len, float)
    o = np.argsort(w)
    c = np.cumsum(Lw[o]) / Lw.sum()
    print(f"\n`wall` geometry parts: {n_parts[0]:,}   of which straight strips "
          f"passing the same 0.95 gate: {len(w):,} "
          f"({100 * len(w) / max(1, n_parts[0]):.1f}%)")
    print(f"`wall` geometry strip width in mm, length-weighted: n={len(w):,}")
    print("   " + "  ".join(
        f"p{q}={w[o][min(np.searchsorted(c, q/100), len(w)-1)]:.0f}"
        for q in (5, 25, 50, 75, 95)))

    tot = sum(per_plan_classes.values())
    print(f"\ndistinct wall widths in one plan's own `wall` geometry "
          f"(+/-10 mm, >=5 % of length):")
    print("   " + "  ".join(f"{k}:{100*v/tot:5.1f}%"
                            for k, v in sorted(per_plan_classes.items())))
    print(f"   NOTE: ResPlan's `wall` polygons are the drawn wall band, exterior "
          f"and internal together;\n         the corpus records no internal/"
          f"external distinction and no room-pair for a wall.")


if __name__ == "__main__":
    main()
