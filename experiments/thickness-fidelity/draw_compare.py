"""Ticket 33 item 1 — draw it, because the question is a looking question.

Item 1 asks whether a dwelling every one of whose partitions is identical *reads
as generated before a number is checked*. That is not answerable from a
percentile table, so this renders the comparison: each dwelling twice, left as
the corpus drew it and right with every internal wall replaced by a band of
`t_int` centred on the same centreline. The Envelope and every boundary wall are
untouched in both, because ADR 0001 leaves them untouched.

The poché is solid black at 1:50, which is the convention *Dimensioning and
annotation rules* settled on, so what is on the page is what the engine would
put on the page.

This is NOT *Look at the converted corpus* (ticket 27). That looks at the ADR
0008 rectangularisation; this changes nothing but wall thickness.

Run:  python experiments/thickness-fidelity/draw_compare.py [n] [seed]
Writes out/compare.svg
"""
from __future__ import annotations

import gzip
import math
import pickle
import random
import sys
from pathlib import Path

import shapely
from shapely import from_wkt, make_valid
from shapely.geometry import Polygon

sys.path.insert(0, str(Path(__file__).resolve().parent))
from measure import _poly, mrr_axes, measure_dwelling      # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
T_INT = 150          # mm, the shipped AZ t_int total (ADR 0010)
SCALE = 26.0         # px per metre on the sheet
PAD = 14


def band(cx, cy, u, length, t_mm):
    """Rectangle of width `t_mm` centred on a centreline, in metres."""
    h = t_mm / 2000.0
    n = (-u[1], u[0])
    L = length / 2.0
    pts = []
    for su, sn in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        pts.append((cx + u[0] * L * su + n[0] * h * sn,
                    cy + u[1] * L * su + n[1] * h * sn))
    return Polygon(pts)


def path_of(g, ox, oy, sc, flip_y):
    out = []
    geoms = g.geoms if g.geom_type.startswith("Multi") else [g]
    for p in geoms:
        if p.is_empty or p.geom_type != "Polygon":
            continue
        for ring in [p.exterior, *p.interiors]:
            cs = list(ring.coords)
            d = " ".join(
                f"{'M' if i == 0 else 'L'}{(x - ox) * sc:.1f},"
                f"{(flip_y - y) * sc:.1f}"
                for i, (x, y) in enumerate(cs))
            out.append(d + " Z")
    return " ".join(out)


def render(rooms, walls, ox, oy, flip_y, dx, title):
    s = [f'<g transform="translate({dx},0)">',
         f'<text x="4" y="-4" font-family="sans-serif" font-size="11" '
         f'fill="#888">{title}</text>']
    for r in rooms:
        s.append(f'<path d="{path_of(r, ox, oy, SCALE, flip_y)}" '
                 f'fill="#f2efe9" stroke="none"/>')
    for w in walls:
        s.append(f'<path d="{path_of(w, ox, oy, SCALE, flip_y)}" '
                 f'fill="#111" stroke="none" fill-rule="evenodd"/>')
    s.append("</g>")
    return "\n".join(s)


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    with gzip.open(OUT / "cache.pkl.gz", "rb") as fh:
        cache = pickle.load(fh)

    keys = sorted(cache["rooms"])
    random.Random(seed).shuffle(keys)

    panels, W, H = [], 0, 0
    picked = 0
    for key in keys:
        if picked >= n:
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

        # The dwelling's OWN length-weighted median internal thickness, so the
        # middle panel isolates UNIFORMITY from THICKNESS.
        ts = sorted((w["t_mrr"], w["len_int"]) for w in rec["internal"])
        tot = sum(L for _, L in ts)
        acc, t_own = 0.0, ts[0][0]
        for t_, L in ts:
            acc += L
            if acc >= tot / 2:
                t_own = t_
                break

        # Only walls touching this dwelling get drawn, at any thickness.
        hull = shapely.buffer(shapely.union_all(rooms), 0.45)
        real, own, new = [], [], []
        for wp in wall_polys:
            if not shapely.intersects(hull, wp):
                continue
            clipped = shapely.intersection(wp, hull)
            if clipped.is_empty:
                continue
            real.append(clipped)
            ax = mrr_axes(wp)
            if ax is None:
                own.append(clipped)
                new.append(clipped)
                continue
            thick, length, (cx, cy), u, nn = ax
            # internal iff the probe said so: match on centre + thickness
            is_int = any(abs(w["t_mrr"] - thick * 1000) < 0.6
                         and abs(w["len"] - length) < 1e-3
                         for w in rec["internal"])
            if is_int:
                for dst, tt in ((own, t_own), (new, T_INT)):
                    b = shapely.intersection(band(cx, cy, u, length, tt), hull)
                    dst.append(b if not b.is_empty else clipped)
            else:
                own.append(clipped)
                new.append(clipped)

        x0, y0, x1, y1 = shapely.bounds(shapely.union_all(real + rooms))
        w_px = (x1 - x0) * SCALE + 2 * PAD
        h_px = (y1 - y0) * SCALE + 2 * PAD + 16
        panels.append((rooms, real, own, new, x0, y0, y1, w_px, h_px, key,
                       round(t_own)))
        W = max(W, w_px)
        H += h_px + 10
        picked += 1

    if not panels:
        print("no dwellings matched")
        return

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{3*W+80:.0f}" '
             f'height="{H:.0f}" viewBox="0 0 {3*W+80:.0f} {H:.0f}">',
             '<rect width="100%" height="100%" fill="#fff"/>']
    y = 0.0
    for rooms, real, own, new, x0, y0, y1, w_px, h_px, key, t_own in panels:
        parts.append(f'<g transform="translate({PAD},{y + PAD + 14})">')
        parts.append(render(rooms, real, x0, y0, y1, 0,
                            f"{key[:22]}  —  as surveyed"))
        parts.append(render(rooms, own, x0, y0, y1, W + 20,
                            f"uniform at its OWN median, {t_own} mm"))
        parts.append(render(rooms, new, x0, y0, y1, 2 * W + 40,
                            f"uniform at t_int = {T_INT} mm"))
        parts.append("</g>")
        y += h_px + 10
    parts.append("</svg>")
    dest = OUT / "compare.svg"
    dest.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {dest}  ({picked} dwellings, seed {seed})")
    png(panels, W, H, seed)


def png(panels, W, H, seed):
    """The same thing as a raster, so it can actually be looked at."""
    from PIL import Image, ImageDraw

    im = Image.new("RGB", (int(3 * W + 80), int(H) + 24), "white")
    d = ImageDraw.Draw(im)
    y = 12.0
    for rooms, real, own, new, x0, y0, y1, w_px, h_px, key, t_own in panels:
        for dx, walls, title in ((PAD, real, f"{key[:16]}  as surveyed"),
                                 (PAD + W + 20, own,
                                  f"uniform at its own median {t_own} mm"),
                                 (PAD + 2 * W + 40, new,
                                  f"uniform at t_int = {T_INT} mm")):
            d.text((dx + 2, y - 10), title, fill=(130, 130, 130))
            for g, col in [(r, (242, 239, 233)) for r in rooms] + \
                          [(w, (17, 17, 17)) for w in walls]:
                for p in (g.geoms if g.geom_type.startswith("Multi") else [g]):
                    if p.is_empty or p.geom_type != "Polygon":
                        continue
                    pts = [(dx + (x - x0) * SCALE, y + PAD + (y1 - yy) * SCALE)
                           for x, yy in p.exterior.coords]
                    if len(pts) >= 3:
                        d.polygon(pts, fill=col)
        y += h_px + 10
    dst = OUT / "compare.png"
    im.save(dst)
    print(f"wrote {dst}")


if __name__ == "__main__":
    main()
