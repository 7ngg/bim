"""Ticket 33 — check the internal/boundary classifier by drawing it.

`measure.py` decides that a wall separates two rooms of one dwelling by
perpendicular probing, and every number in the findings rests on that decision
being right. The failure mode that would matter is a perimeter wall being called
internal at a corner, which would drag the internal thickness distribution
upward toward the exterior one.

So: draw it. Internal walls RED, boundary walls BLACK, rooms pale, and print the
per-wall table beside the picture. A wrong classification is visible at a glance
in a way no percentile is.

Run:  python experiments/thickness-fidelity/classify_check.py [n] [seed]
Writes out/classify.png and prints the table.
"""
from __future__ import annotations

import gzip
import pickle
import random
import sys
from pathlib import Path

import shapely
from shapely import from_wkt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from measure import _poly, mrr_axes, measure_dwelling      # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
SCALE = 30.0
PAD = 16


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    with gzip.open(OUT / "cache.pkl.gz", "rb") as fh:
        cache = pickle.load(fh)
    keys = sorted(cache["rooms"])
    random.Random(seed).shuffle(keys)

    from PIL import Image, ImageDraw
    panels = []
    for key in keys:
        if len(panels) >= n:
            break
        floor, _ = key.split("|", 1)
        rooms = [p for p in (_poly(from_wkt(w)) for _, w in cache["rooms"][key])
                 if p is not None and p.area >= 0.5]
        if not (4 <= len(rooms) <= 8):
            continue
        wall_polys = [p for p in (_poly(from_wkt(w))
                                  for w in cache["walls"].get(floor, []))
                      if p is not None]
        rec = measure_dwelling(cache["rooms"][key], wall_polys,
                               cache.get("other", {}).get(key, ()))
        if rec is None or len(rec["internal"]) < 3:
            continue

        def match(wp, bucket):
            ax = mrr_axes(wp)
            if ax is None:
                return None
            t, L = ax[0] * 1000, ax[1]
            for w in rec[bucket]:
                if abs(w["t_mrr"] - t) < 0.6 and abs(w["len"] - L) < 1e-3:
                    return w
            return None

        hull = shapely.buffer(shapely.union_all(rooms), 0.45)
        drawn = []
        for wp in wall_polys:
            if not shapely.intersects(hull, wp):
                continue
            c = shapely.intersection(wp, hull)
            if c.is_empty:
                continue
            wi = match(wp, "internal")
            wb = match(wp, "boundary")
            drawn.append((c, (200, 40, 40) if wi else
                          ((17, 17, 17) if wb else (150, 150, 210)), wi))
        panels.append((key, rooms, drawn, rec))

        print(f"\n=== {key}  rooms={rec['n_rooms']}  "
              f"sum_area={rec['sum_area']:.1f} m2")
        print(f"    {'class':<9}{'t_mrr':>7}{'gap':>7}{'len':>7}{'len_int':>9}"
              f"{'int/bnd/void':>14}")
        for w in sorted(rec["internal"], key=lambda w: -w["len_int"])[:12]:
            print(f"    {'INTERNAL':<9}{w['t_mrr']:>7.0f}{w['gap']:>7.0f}"
                  f"{w['len']:>7.2f}{w['len_int']:>9.2f}"
                  f"{w['n_int']:>6}/{w['n_bnd']}/{w['n_void']}")
        for w in sorted(rec["boundary"], key=lambda w: -w["len_bnd"])[:6]:
            print(f"    {'boundary':<9}{w['t_mrr']:>7.0f}{'-':>7}"
                  f"{w['len']:>7.2f}{w['len_bnd']:>9.2f}"
                  f"{w['n_int']:>6}/{w['n_bnd']}/{w['n_void']}")

    if not panels:
        print("no dwellings matched")
        return

    W = max(shapely.bounds(shapely.union_all([g for g, _, _ in d]))[2] -
            shapely.bounds(shapely.union_all([g for g, _, _ in d]))[0]
            for _, _, d, _ in panels) * SCALE + 2 * PAD
    H = 0.0
    boxes = []
    for key, rooms, drawn, rec in panels:
        x0, y0, x1, y1 = shapely.bounds(
            shapely.union_all([g for g, _, _ in drawn] + rooms))
        boxes.append((x0, y0, x1, y1))
        H += (y1 - y0) * SCALE + 2 * PAD + 16

    im = Image.new("RGB", (int(W) + 20, int(H) + 24), "white")
    d = ImageDraw.Draw(im)
    y = 12.0
    for (key, rooms, drawn, rec), (x0, y0, x1, y1) in zip(panels, boxes):
        d.text((PAD, y), f"{key[:18]}   RED = classified internal", fill=(120, 120, 120))
        for g, col in [(r, (242, 239, 233)) for r in rooms] + \
                      [(g, c) for g, c, _ in drawn]:
            for p in (g.geoms if g.geom_type.startswith("Multi") else [g]):
                if p.is_empty or p.geom_type != "Polygon":
                    continue
                pts = [(PAD + (x - x0) * SCALE, y + PAD + (y1 - yy) * SCALE)
                       for x, yy in p.exterior.coords]
                if len(pts) >= 3:
                    d.polygon(pts, fill=col)
        y += (y1 - y0) * SCALE + 2 * PAD + 16
    dst = OUT / "classify.png"
    im.save(dst)
    print(f"\nwrote {dst}")


if __name__ == "__main__":
    main()
