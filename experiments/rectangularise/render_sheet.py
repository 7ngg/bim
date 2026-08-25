"""PROTOTYPE (ticket 27) -- draw a converted dwelling beside the real one.

Throwaway. It exists to answer one question no number on this map can answer:
*does a converted dwelling read as a home?* Nothing here ships; the renderer the
engine needs is `docs/spec/annotation.md`'s job, not this file's.

Three panels per dwelling, and the middle one is the point:

  ORIGINAL    the corpus room polygons, as drawn, filled by room type.
  CONVERTED   the fitted rectangles drawn as a PLAN -- 150 mm walls straddling
              every rectangle edge -- because an outline drawing of the same
              rectangles reads as a diagram and flatters the conversion. What a
              person judges is a plan.
  OVERLAY     the corpus outline over the converted fill, so what moved is
              visible rather than inferred.

TWO PLANES, AND THE DRAWING SAYS SO. The fitted rectangles are on the
watershed / CENTRELINE plane; the corpus polygons are on the corpus's own
(clear-ish) plane. Ticket 37 measured the ratio at 1.243 dwelling-wide but
1.17x for `living_dining` and 1.58x for `wc`, so a naive overlay makes the
conversion look like it inflated the wet rooms. It did not. Drawing the walls
is exactly what reconciles the two: the converted room's CLEAR extent is the
rectangle inset by t_int/2 a side, and that is the surface the corpus polygon
should be compared against. `--plane=clear` insets, `--plane=centreline` does
not, and the caption always says which.

Run:
  python experiments/rectangularise/render_sheet.py            # the standard sheet
  python experiments/rectangularise/render_sheet.py --pick=k2  # two-rectangle rooms
  python experiments/rectangularise/render_sheet.py --key=362|3468|c9b5...

Writes PNGs plus an index.html to out/sheets/.
"""
import html
import json
import math
import sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPoly, Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from shapely.affinity import rotate

from fit_rects import (GRID, T_INT_MM, envelope_approx, keep_largest_component,
                       load_swiss_geoms, swiss_keys, watershed)

OUT = Path(__file__).resolve().parent / "out"
SHEETS = OUT / "sheets"
SHEETS.mkdir(parents=True, exist_ok=True)

T_INT = T_INT_MM / 1000.0

# Muted, distinguishable, and deliberately NOT a heat scale -- a colour that
# encodes quality would tell the eye what to think, which is the one thing this
# ticket must not do.
COLOUR = {
    "ROOM": "#c8d8e8", "BEDROOM": "#bcd0e6", "LIVING_ROOM": "#d8e2c8",
    "LIVING_DINING": "#cfe0bd", "DINING": "#dde5c4", "KITCHEN": "#f0dcc0",
    "KITCHEN_DINING": "#efd9b6", "BATHROOM": "#cfe4e4", "STOREROOM": "#dedede",
    "CORRIDOR": "#eeeae0", "STUDIO": "#dcd2e6", "<NA>": "#e8e8e8",
}
SHORT = {
    "ROOM": "Room", "BEDROOM": "Bed", "LIVING_ROOM": "Living",
    "LIVING_DINING": "Liv/Din", "DINING": "Dining", "KITCHEN": "Kitchen",
    "KITCHEN_DINING": "Kit/Din", "BATHROOM": "Bath", "STOREROOM": "Store",
    "CORRIDOR": "Corr", "STUDIO": "Studio", "<NA>": "?",
}


def colour(t):
    return COLOUR.get(t, "#e8e8e8")


# ------------------------------------------------------------------- geometry

def frame(geoms):
    """Re-derive the fit's own cell frame. The record does not store it."""
    lab, x0, y0 = watershed(geoms)
    if lab is None:
        return None
    lab = keep_largest_component(lab)
    env, notches, info, (oy, ox) = envelope_approx(lab >= 0)
    dom = (lab >= 0)[oy:oy + env.shape[0], ox:ox + env.shape[1]]
    return {"x0": x0 + ox * GRID, "y0": y0 + oy * GRID, "env": env,
            "dom": dom, "notches": notches, "info": info}


def draw_voids(ax, f, parts_cells):
    """Envelope floor no Room claims, and that WAS dwelling.

    `fit_rects` posts exact tiling soft (C10), so this is legal and the
    objective merely charges for it -- but on a drawing it is floor with walls
    round it and no name, and until this sheet nobody had seen one. Cells the
    Envelope over-reached into are NOT marked: the notch approximation
    under-cuts on purpose and leaving those empty is correct.
    """
    env, dom = f["env"], f["dom"]
    covered = np.zeros(env.shape, dtype=bool)
    for ps in parts_cells:
        for (x1, y1, x2, y2) in ps:
            covered[y1:y2, x1:x2] = True
    void = env & dom & ~covered
    ys, xs = np.nonzero(void)
    for cy, cx in zip(ys, xs):
        ax.add_patch(Rectangle((f["x0"] + cx * GRID, f["y0"] + cy * GRID),
                               GRID, GRID, facecolor="#ffffff",
                               edgecolor="#c02020", linewidth=0.25,
                               hatch="///", zorder=3))
    return int(void.sum())


def to_world(r, f):
    """A fit-frame cell rectangle (x1,y1,x2,y2) -> metres in the rotated frame."""
    return (f["x0"] + r[0] * GRID, f["y0"] + r[1] * GRID,
            f["x0"] + r[2] * GRID, f["y0"] + r[3] * GRID)


def inset(b, d):
    """Shrink a world rectangle by d on every side; None if it vanishes."""
    x1, y1, x2, y2 = b[0] + d, b[1] + d, b[2] - d, b[3] - d
    if x2 <= x1 or y2 <= y1:
        return None
    return (x1, y1, x2, y2)


def join_band(a, b):
    """The stretch of shared edge between a Room's two parts, as a rectangle.

    Inset along the join by t_int/2 at each end so the band stops flush with the
    walls that continue past the corner, rather than eating them.
    """
    e = T_INT / 2
    if abs(a[2] - b[0]) < 1e-9 or abs(b[2] - a[0]) < 1e-9:
        x = a[2] if abs(a[2] - b[0]) < 1e-9 else b[2]
        lo, hi = max(a[1], b[1]) + e, min(a[3], b[3]) - e
        return None if hi <= lo else (x - e, lo, x + e, hi)
    if abs(a[3] - b[1]) < 1e-9 or abs(b[3] - a[1]) < 1e-9:
        y = a[3] if abs(a[3] - b[1]) < 1e-9 else b[3]
        lo, hi = max(a[0], b[0]) + e, min(a[2], b[2]) - e
        return None if hi <= lo else (lo, y - e, hi, y + e)
    return None


def rot_geoms(items):
    """The polygons in the same rotated frame `load_swiss_geoms` produced."""
    types = []
    geoms = load_swiss_geoms(items, types)
    return geoms, types


# --------------------------------------------------------------------- drawing

def draw_polys(ax, geoms, types, alpha=1.0, label=True):
    for i, (g, t) in enumerate(zip(geoms, types)):
        polys = [g] if g.geom_type == "Polygon" else list(g.geoms)
        for p in polys:
            ax.add_patch(MplPoly(np.asarray(p.exterior.coords), closed=True,
                                 facecolor=colour(t), edgecolor="#333333",
                                 linewidth=0.7, alpha=alpha, zorder=2))
        if label:
            # Indexed, because two ROOMs side by side are indistinguishable and
            # the whole point is matching a room across the three panels.
            c = g.representative_point()
            ax.text(c.x, c.y, f"{SHORT.get(t, t[:5])}{i}", ha="center",
                    va="center", fontsize=5.5, color="#222222", zorder=6)


def draw_plan(ax, parts_w, types, plane="clear", walls=True, label=True,
              ious=None):
    """Draw fitted rectangles as a plan: fill, then walls straddling the edges.

    `plane="clear"` insets every rectangle by t_int/2, which is the surface a
    corpus polygon is comparable to. The wall band then occupies exactly the
    t_int the inset gave up, so nothing is invented -- the wall is drawn in the
    space the centreline plane already reserved for it.
    """
    d = T_INT / 2 if plane == "clear" else 0.0
    for i, (ps, t) in enumerate(zip(parts_w, types)):
        drawn = []
        for b in ps:
            q = inset(b, d)
            if q is None:
                continue
            drawn.append(q)
            ax.add_patch(Rectangle((q[0], q[1]), q[2] - q[0], q[3] - q[1],
                                   facecolor=colour(t), edgecolor="none",
                                   zorder=2))
        if walls:
            for b in ps:
                x1, y1, x2, y2 = b
                # Four bands of t_int centred on the rectangle's own edges.
                for bx1, by1, bx2, by2 in (
                        (x1 - T_INT / 2, y1 - T_INT / 2, x2 + T_INT / 2, y1 + T_INT / 2),
                        (x1 - T_INT / 2, y2 - T_INT / 2, x2 + T_INT / 2, y2 + T_INT / 2),
                        (x1 - T_INT / 2, y1 - T_INT / 2, x1 + T_INT / 2, y2 + T_INT / 2),
                        (x2 - T_INT / 2, y1 - T_INT / 2, x2 + T_INT / 2, y2 + T_INT / 2)):
                    ax.add_patch(Rectangle((bx1, by1), bx2 - bx1, by2 - by1,
                                           facecolor="#3a3a3a", edgecolor="none",
                                           zorder=4))
            # A Room's two parts are ONE Space -- ADR 0014 -- so the join
            # between them is not a wall. Drawing per-rectangle puts a band
            # there; paint it back out, above the walls, or every L reads as
            # two rooms and the thing this sheet exists to judge is prejudged.
            if len(ps) == 2:
                j = join_band(ps[0], ps[1])
                if j is not None:
                    ax.add_patch(Rectangle((j[0], j[1]), j[2] - j[0], j[3] - j[1],
                                           facecolor=colour(t), edgecolor="none",
                                           zorder=5))
        if label and drawn:
            # ADR 0014: the tag goes at the centroid of the LARGEST constituent
            # rectangle, not the Room's own centroid -- an L's centroid can land
            # outside its own Space. Whether that READS as deliberate is one of
            # the things this sheet is here to be looked at for.
            big = max(drawn, key=lambda q: (q[2] - q[0]) * (q[3] - q[1]))
            mx, my = (big[0] + big[2]) / 2, (big[1] + big[3]) / 2
            ax.text(mx, my, f"{SHORT.get(t, t[:5])}{i}", ha="center",
                    va="center", fontsize=5.5, color="#111111", zorder=6)
            if ious and i < len(ious):
                # The number beside the picture, so a disagreement between the
                # two is visible rather than remembered -- ticket 27 item 4.
                ax.text(mx, my, f"\n\n{ious[i]:.2f}", ha="center", va="center",
                        fontsize=4.5, color="#8a0f2a", zorder=6)


def draw_overlay(ax, geoms, parts_w, types, plane="clear"):
    d = T_INT / 2 if plane == "clear" else 0.0
    for ps, t in zip(parts_w, types):
        for b in ps:
            q = inset(b, d)
            if q is None:
                continue
            ax.add_patch(Rectangle((q[0], q[1]), q[2] - q[0], q[3] - q[1],
                                   facecolor=colour(t), edgecolor="none",
                                   alpha=0.85, zorder=2))
    for g in geoms:
        polys = [g] if g.geom_type == "Polygon" else list(g.geoms)
        for p in polys:
            ax.add_patch(MplPoly(np.asarray(p.exterior.coords), closed=True,
                                 facecolor="none", edgecolor="#b00020",
                                 linewidth=0.9, zorder=5))


def draw_envelope(ax, f, b):
    """The Envelope alone -- what a refused dwelling was asked to tile."""
    env = f["env"]
    ny, nx = env.shape
    for y in range(ny):
        x = 0
        while x < nx:
            if not env[y, x]:
                x += 1
                continue
            x2 = x
            while x2 < nx and env[y, x2]:
                x2 += 1
            ax.add_patch(Rectangle((f["x0"] + x * GRID, f["y0"] + y * GRID),
                                   (x2 - x) * GRID, GRID, facecolor="#dfe6ee",
                                   edgecolor="none", zorder=2))
            x = x2
    ax.text((b[0] + b[2]) / 2, b[1] + 0.2,
            f"notches needed {f['info']['notches_needed']} · used "
            f"{f['info']['notches_used']} · loss {f['info']['envelope_loss']:.3f}",
            ha="center", va="bottom", fontsize=5.5, color="#444444", zorder=6)


def tidy(ax, title, bounds):
    ax.set_title(title, fontsize=7, pad=3)
    ax.set_aspect("equal")
    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_linewidth(0.4)
        s.set_color("#999999")


def bounds_of(geoms, parts_w, pad=0.5):
    xs = [c for g in geoms for c in (g.bounds[0], g.bounds[2])]
    ys = [c for g in geoms for c in (g.bounds[1], g.bounds[3])]
    for ps in parts_w:
        for b in ps:
            xs += [b[0], b[2]]
            ys += [b[1], b[3]]
    return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)


# ---------------------------------------------------------------------- record

def parts_of(rec):
    """k<=2 files carry `parts`; a k=1 file carries both. Prefer `parts`.

    None for a record that never produced geometry -- INFEASIBLE, UNKNOWN,
    ROOM_LOST_*. Those still want drawing: what was REFUSED is half of what the
    ticket asked to look at, and the original is all there is to show.
    """
    if rec.get("parts") is not None:
        return rec["parts"]
    if rec.get("rects") is not None:
        return [[r] for r in rec["rects"]]
    return None


def render(rec, dw, plane="clear", note=""):
    key = tuple(rec["k"].split("|"))
    geoms, types = rot_geoms(dw[key])
    if geoms is None:
        return None
    f = frame(geoms)
    if f is None:
        return None
    ps_raw = parts_of(rec)
    refused = ps_raw is None
    parts_w = [] if refused else [[to_world(r, f) for r in ps] for ps in ps_raw]
    # The record's own `types` is authoritative -- `load_swiss_geoms` collects
    # it from the FILTERED list now (the 1.23 % off-by-one is fixed at source),
    # so this is a consistency check rather than a repair.
    rt = rec.get("types") or types
    if rt != types:
        print(f"  ! label mismatch on {rec['k']}: record {rt} vs reload {types}")
    b = bounds_of(geoms, parts_w)

    if refused:
        fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.9), dpi=170)
        draw_polys(axes[0], geoms, types)
        tidy(axes[0], "ORIGINAL — corpus polygons (corpus plane)", b)
        draw_envelope(axes[1], f, b)
        tidy(axes[1], f"REFUSED — {rec['status']}: the Envelope it had to tile", b)
    else:
        fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.9), dpi=170)
        draw_polys(axes[0], geoms, types)
        tidy(axes[0], "ORIGINAL — corpus polygons (corpus plane)", b)
        draw_plan(axes[1], parts_w, rt, plane=plane, ious=rec.get("iou"))
        nv = draw_voids(axes[1], f, ps_raw)
        tidy(axes[1], f"CONVERTED — as a plan, walls {T_INT_MM} mm ({plane} plane)"
                      + (f"\nhatched: {nv * 0.0625:.2f} m² of floor no Room claims"
                         if nv else "\nevery cell of the dwelling is claimed"), b)
        draw_overlay(axes[2], geoms, parts_w, rt, plane=plane)
        tidy(axes[2], "OVERLAY — corpus outline (red) over converted fill", b)

    iou = rec.get("iou") or [0.0]
    k_used = rec.get("k_used") or [1] * len(rt)
    cap = (f"{rec['k']}   status={rec['status']}   n={rec['n']}   "
           f"cell_agreement={rec.get('cell_agreement', float('nan')):.3f}   "
           f"IoU min={min(iou):.2f} med={sorted(iou)[len(iou) // 2]:.2f}   "
           f"two-rect rooms={sum(1 for k in k_used if k == 2)}   "
           f"envelope_loss={rec.get('envelope_loss', 0):.3f}   "
           f"rel={rec.get('rel')}   edges_lost={rec.get('edges_lost')}")
    if note:
        cap = note + "\n" + cap
    fig.suptitle(cap, fontsize=6, y=0.995, family="monospace")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    name = rec["k"].replace("|", "_") + ".png"
    fig.savefig(SHEETS / name, facecolor="white")
    plt.close(fig)
    return name


# ---------------------------------------------------------------------- picking

def pct(vals, p):
    s = sorted(vals)
    return s[max(0, min(len(s) - 1, int(round(p / 100 * (len(s) - 1)))))]


def pick(recs, mode, n):
    ok = [r for r in recs if r["status"] in ("OPTIMAL", "FEASIBLE")]
    ok.sort(key=lambda r: r.get("cell_agreement", 0))
    if mode == "spread":
        # Across the agreement range AND across room counts: the two axes the
        # ticket names. Take a band at each decile, preferring an unseen n.
        out, seen_n = [], Counter()
        for q in range(0, 101, max(1, 100 // max(n - 1, 1))):
            i = max(0, min(len(ok) - 1, int(round(q / 100 * (len(ok) - 1)))))
            lo, hi = max(0, i - 40), min(len(ok), i + 40)
            band = sorted(ok[lo:hi], key=lambda r: seen_n[r["n"]])
            for r in band:
                if r not in out:
                    out.append(r)
                    seen_n[r["n"]] += 1
                    break
            if len(out) >= n:
                break
        return out[:n]
    if mode == "p5":
        return ok[:n]
    if mode == "p95":
        return ok[-n:]
    if mode == "median":
        i = len(ok) // 2
        return ok[max(0, i - n // 2):max(0, i - n // 2) + n]
    if mode == "infeasible":
        return [r for r in recs if r["status"] == "INFEASIBLE"][:n]
    if mode == "feasible":
        return [r for r in ok if r["status"] == "FEASIBLE"][:n]
    if mode == "k2":
        # The rooms the one-rectangle conversion was mangling: most two-part.
        two = [r for r in ok if sum(1 for k in r.get("k_used", []) if k == 2)]
        two.sort(key=lambda r: -sum(1 for k in r["k_used"] if k == 2))
        return two[:n]
    if mode == "corridor":
        out = []
        for r in ok:
            for t, k in zip(r.get("types", []), r.get("k_used", [])):
                if k == 2 and t == "CORRIDOR":
                    out.append(r)
                    break
            if len(out) >= n:
                break
        return out
    if mode == "spurious":
        # The 15.7 % of relations the conversion ADDS -- one room wrapping
        # another, and the fit picking a side.
        sp = [r for r in ok if r.get("rel", {}).get("spurious", 0)]
        sp.sort(key=lambda r: -r["rel"]["spurious"] / max(sum(r["rel"].values()), 1))
        return sp[:n]
    if mode == "lostedge":
        le = [r for r in ok if r.get("edges_lost", 0)]
        le.sort(key=lambda r: -r["edges_lost"])
        return le[:n]
    if mode == "worstroom":
        w = sorted(ok, key=lambda r: min(r.get("iou") or [1.0]))
        return w[:n]
    raise SystemExit(f"unknown --pick={mode}")


NOTE = {
    "spread": "SPREAD — across the cell-agreement range and across room counts",
    "p5": "P5 — the worst conversions that still converted",
    "p95": "P95 — the best conversions",
    "median": "MEDIAN — the typical conversion",
    "infeasible": "INFEASIBLE — rightly dropped? this is what was refused",
    "feasible": "FEASIBLE not OPTIMAL — a tiling was found but not proved best",
    "k2": "TWO-RECTANGLE ROOMS — what ADR 0016 bought",
    "corridor": "L-SHAPED CORRIDORS — the case k=1 was mangling",
    "spurious": "SPURIOUS RELATIONS — one room wrapped another and the fit picked a side",
    "lostedge": "LOST ADJACENCIES — a door that exists in the corpus and not in the conversion",
    "worstroom": "WORST ROOM — the room a person's eye lands on",
}


def main():
    args = [a for a in sys.argv[1:]]
    mode = "spread"
    n = 10
    plane = "clear"
    fitfile = "swiss_fit_k2.json"
    keys = []
    for a in args:
        if a.startswith("--pick="):
            mode = a.split("=", 1)[1]
        elif a.startswith("--n="):
            n = int(a.split("=", 1)[1])
        elif a.startswith("--plane="):
            plane = a.split("=", 1)[1]
        elif a.startswith("--fit="):
            fitfile = a.split("=", 1)[1]
        elif a.startswith("--key="):
            keys.append(a.split("=", 1)[1])
    recs = json.load(open(OUT / fitfile))
    dw, _ = swiss_keys()
    if keys:
        by = {r["k"]: r for r in recs}
        chosen = [by[k] for k in keys if k in by]
        note = "BY KEY"
    else:
        chosen = pick(recs, mode, n)
        note = NOTE.get(mode, mode)
    print(f"{fitfile}: {len(recs)} records; rendering {len(chosen)} "
          f"({mode}) on the {plane} plane", flush=True)
    made = []
    for r in chosen:
        name = render(r, dw, plane=plane, note=note)
        if name:
            made.append((name, r))
            print("  " + name, flush=True)
    write_index(mode, plane, fitfile, note, made)
    write_master()


def write_index(mode, plane, fitfile, note, made):
    idx = SHEETS / f"index_{mode}_{plane}.html"
    with open(idx, "w", encoding="utf-8") as fh:
        fh.write(f"<!doctype html><meta charset=utf-8><title>{mode}</title>"
                 "<style>body{font:12px system-ui;margin:24px;background:#fafafa}"
                 "img{width:100%;max-width:1500px;border:1px solid #ddd;"
                 "margin:6px 0 22px;background:#fff}</style>")
        fh.write(f"<h1>{html.escape(note)}</h1>")
        fh.write(f"<p>{fitfile} — {plane} plane — {len(made)} dwellings</p>")
        for name, r in made:
            fh.write(f"<div><img src='{name}'></div>")
    print(f"wrote {idx}", flush=True)


def write_master():
    """One page that opens every sheet made so far -- the ticket's deliverable."""
    rows = sorted(SHEETS.glob("index_*.html"))
    with open(SHEETS / "SHEET.html", "w", encoding="utf-8") as fh:
        fh.write("<!doctype html><meta charset=utf-8>"
                 "<title>ticket 27 — converted corpus, looked at</title>"
                 "<style>body{font:14px system-ui;margin:32px;max-width:900px;"
                 "background:#fafafa}li{margin:4px 0}code{background:#eee;"
                 "padding:1px 4px}</style>"
                 "<h1>Ticket 27 — the converted corpus, looked at</h1>"
                 "<p>Each sheet is three panels per dwelling: the corpus polygons, "
                 "the conversion drawn as a plan with 150&nbsp;mm walls, and the "
                 "two overlaid. The red outline is the corpus room.</p>"
                 "<p><b>Two planes.</b> The fitted rectangles are on the "
                 "watershed/centreline plane and the corpus polygons are on the "
                 "corpus's own. The <code>clear</code> sheets inset every "
                 "rectangle by t_int/2 so the two are comparable; the wall band "
                 "occupies exactly what the inset gave up.</p><ul>")
        for p in rows:
            label = p.stem.replace("index_", "").replace("_", " · ")
            fh.write(f"<li><a href='{p.name}'>{html.escape(label)}</a> — "
                     f"{NOTE.get(p.stem.split('_')[1], '')}</li>")
        fh.write("</ul>")
    print(f"wrote {SHEETS / 'SHEET.html'}", flush=True)


if __name__ == "__main__":
    main()
