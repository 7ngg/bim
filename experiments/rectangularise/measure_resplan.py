"""Rectangularising real rooms - the same measurement, on ResPlan 17k.

The corpus ticket 22 quotes: 43.2% exactly rectangular, 62.3% at 2%. Both are
re-derived here rather than taken from the paper (C11), and the same conversions,
the same contact graph and the same relation comparison are run over it, so the
two corpora are directly comparable.

Two ResPlan-specific hazards, both from docs/research/dataset-inventory.md 2.4:
  - geometry is NOT in metres. A ~256-unit canvas whose scale varies per plan;
    recover it as sqrt(area / polygon_area).
  - ids 5981-5985 carry a square-feet bug in `area`, and 5227 has net_area 0.
    Filtered, along with every plan under 30 m^2.

Run: python experiments/rectangularise/measure_resplan.py
"""
import io
import json
import math
import pickle
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from shapely.affinity import rotate, scale
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from measure_swiss import (  # noqa: E402
    BAND, CONVERSIONS, MIN_ROOM_AREA, REPAIRS, TAU, _op, _poly, _area,
    bbox_rect, compare_relations, contact_graph, dwelling_frame, relations,
)

ROOT = Path(__file__).resolve().parents[2]
PKL = ROOT / "data" / "corpora" / "resplan" / "ResPlan.pkl"
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)

# The five functional classes reconcile to the paper's 137,131 polygons; a Brief
# never names the outdoor ones, so they are excluded exactly as the Swiss
# NOT_A_ROOM set excludes BALCONY and GARDEN.
ROOM_KEYS = ["living", "kitchen", "bedroom", "bathroom"]
NOT_A_ROOM_KEYS = ["balcony", "garden", "parking", "pool"]
BROKEN_IDS = {5981, 5982, 5983, 5984, 5985, 5227}
MIN_PLAN_AREA = 30.0  # m^2

ALLOWED = {
    ("shapely.io", "from_wkb"),
    ("numpy.core.multiarray", "_reconstruct"),
    ("numpy._core.multiarray", "_reconstruct"),
    ("numpy", "ndarray"),
    ("numpy", "dtype"),
    ("numpy.core.multiarray", "scalar"),
    ("numpy._core.multiarray", "scalar"),
}


class Restricted(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) not in ALLOWED:
            raise pickle.UnpicklingError(f"blocked global: {module}.{name}")
        return super().find_class(module, name)


def parts(v):
    """A class key holds a MultiPolygon when the plan has several rooms of it."""
    if v is None:
        return []
    if isinstance(v, (list, tuple)):
        out = []
        for x in v:
            out.extend(parts(x))
        return out
    if hasattr(v, "geoms"):
        return list(v.geoms)
    return [v] if hasattr(v, "area") else []


def measure_plan(p):
    geoms, types = [], []
    for k in ROOM_KEYS:
        for g in parts(p.get(k)):
            g = _poly(g)
            if g is not None:
                geoms.append(g)
                types.append(k)
    if not geoms:
        return None

    # metres per canvas unit, from the only metric anchor the corpus has
    canvas = sum(g.area for g in geoms)
    for k in NOT_A_ROOM_KEYS:
        canvas += sum(g.area for g in parts(p.get(k)) if hasattr(g, "area"))
    area = p.get("area")
    if not area or canvas <= 0 or area < MIN_PLAN_AREA:
        return None
    mpu = math.sqrt(float(area) / canvas)
    geoms = [scale(g, mpu, mpu, origin=(0, 0)) for g in geoms]

    keep = [(g, t) for g, t in zip(geoms, types) if g.area >= MIN_ROOM_AREA]
    if not keep:
        return None
    geoms, types = [g for g, _ in keep], [t for _, t in keep]
    n = len(geoms)
    if not (BAND[0] <= n <= BAND[1]):
        return None

    ang, cen = dwelling_frame(geoms)
    if ang is None:
        return None
    geoms = [rotate(g, -ang, origin=cen) for g in geoms]

    env = _op(unary_union, [_poly(g.buffer(TAU / 2, join_style=2, mitre_limit=2.0))
                            for g in geoms])
    if env is None or env.is_empty:
        return None

    rec = {"k": str(p.get("id")), "n": n, "types": types, "mpu": mpu,
           "axis": ang, "area": [g.area for g in geoms],
           "plan_area": float(area), "env_area": env.area}
    rec["g2p_ratio"] = [
        (_area(_op(lambda a, b: a.intersection(b), bbox_rect(g), env)) / g.area
         if g.area > 0 else 0.0) for g in geoms
    ]
    true_edges = contact_graph(geoms)
    true_rel = relations(geoms)
    rec["edges_true"] = len(true_edges)
    rec["pairs"] = len(true_rel)
    rec["pairs_asserted"] = sum(1 for v in true_rel.values() if v != (None, None))

    for name, fn in CONVERSIONS.items():
        rects, ok = [], True
        for g in geoms:
            r = fn(g)
            if r is None or r.is_empty:
                ok = False
                break
            rects.append(r)
        if not ok:
            rec[name] = None
            continue
        iou, aerr = [], []
        for g, r in zip(geoms, rects):
            inter = _area(_op(lambda a, b: a.intersection(b), g, r))
            union = _area(_op(lambda a, b: a.union(b), g, r))
            iou.append(inter / union if union > 0 else 0.0)
            aerr.append((r.area - g.area) / g.area if g.area > 0 else 0.0)
        ov = 0.0
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                if rects[i].intersects(rects[j]):
                    ov += _area(_op(lambda a, b: a.intersection(b), rects[i], rects[j]))
        cov = _op(unary_union, rects)
        out = _area(_op(lambda a, b: a.difference(b), cov, env)) if cov is not None else 0.0
        e2 = contact_graph(rects)
        rec[name] = {
            "rel": dict(compare_relations(true_rel, relations(rects))),
            "iou": iou, "aerr": aerr, "overlap": ov,
            "overlap_frac": ov / sum(g.area for g in geoms),
            "outside_env": out / cov.area if cov is not None and cov.area else 0.0,
            "edges": len(e2), "lost": len(true_edges - e2), "gained": len(e2 - true_edges),
        }
    return rec


def main():
    plans = Restricted(io.BufferedReader(open(PKL, "rb"))).load()
    print(f"plans loaded: {len(plans)}", flush=True)
    recs, skipped = [], Counter()
    for p in plans:
        if int(p.get("id", -1)) in BROKEN_IDS:
            skipped["broken_id"] += 1
            continue
        r = measure_plan(p)
        if r is None:
            skipped["out_of_band_or_degenerate"] += 1
            continue
        recs.append(r)
        if len(recs) % 2500 == 0:
            print(f"  measured {len(recs)}", flush=True)
    print(f"measured {len(recs)}, skipped {dict(skipped)}, repairs {dict(REPAIRS)}",
          flush=True)

    # The paper's own two numbers, re-derived on the dwelling's own axis.
    fill = np.array([x for r in recs if r.get("bbox") for x in r["bbox"]["iou"]])
    print(f"\nrectangular, exactly (IoU=1.000): {np.mean(fill >= 0.9999):.4f}")
    print(f"rectangular at 2% (IoU>=0.98):   {np.mean(fill >= 0.98):.4f}")
    ax = np.array([r["axis"] for r in recs])
    print(f"dwelling axis off the canvas axis, deg: median {np.median(ax):.3f}  "
          f"share >1deg {np.mean(np.minimum(ax, 90 - ax) > 1):.4f}")

    json.dump({"repairs": dict(REPAIRS), "n_plans_total": len(plans), "recs": recs},
              open(OUT / "resplan_rects.json", "w"))
    print(f"wrote {OUT / 'resplan_rects.json'}", flush=True)


if __name__ == "__main__":
    main()
