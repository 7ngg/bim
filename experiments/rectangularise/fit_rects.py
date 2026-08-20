"""The joint fit: re-express a real dwelling as a rectangular tiling.

Every per-room conversion (bbox, largest inscribed rectangle, area-preserving)
converts each room in ignorance of its neighbours, so the result is not a tiling:
measured on Swiss Dwellings, bbox collides in 86% of dwellings and the two
shrinking conversions delete 24-38% of real adjacencies.

The bounding box is the least bad of the three and its failure is narrower than
it first looks. It preserves every separation direction exactly -- the relation
is a bounds test and a bbox preserves bounds -- so it transmits the true
arrangement. What it cannot do is hand the solver a target that is a Plan: its
rectangles overlap, and an overlapping pair ABSTAINS rather than asserting, so
the arrangement arrives with the pairs that overlap silently dropped. It also
inflates area by a mean 11% and a p95 58%, and that number is what per-room
target-area conditioning consumes.

So the conversion is not per room. It is one CP-SAT fit per dwelling, over the
same 250 mm grid the shipping solver uses, and it answers a sharper question
than any threshold could:

    is this real dwelling expressible as a rectangular tiling at all?

A dwelling that is, converts with its adjacency intact and its area preserved by
construction. A dwelling that is not comes back INFEASIBLE, and *that* is the
reject rule -- a representability test, not a percentile.

Two steps:

  1. WATERSHED. Rasterise the dwelling at 250 mm and give every cell to the room
     whose polygon contains it; cells in no room are wall, and go to the nearest
     room. That splits each wall at its centreline, which is ADR 0001's
     construction done discretely, and it produces a ground-truth tiling whose
     room areas sum to the domain exactly.

  2. FIT. One axis-aligned rectangle per room inside a v1-expressible Envelope
     (bbox minus at most two notches, per ADR 0003). No overlaps, area within
     tolerance of the watershed area, and every real adjacency HARD -- while
     exact tiling is SOFT, exactly as C10's amendment has the shipping solver
     post them. Minimise the number of 250 mm cells that end up in the wrong
     room, which is the loss this whole ticket is about.

     The shipped objective, L1 corner displacement, was tried first and is
     WRONG for fitting: among exact tilings it is nearly uncorrelated with how
     much of the dwelling lands in the right room (IoU median 0.14 against 0.82
     for the cell objective). Projection and fitting are not the same problem.

New adjacencies are NOT forbidden. A gained contact tells the solver a door
could go somewhere it could not, which the circulation constraint treats as a
lower bound; a lost contact deletes a door that exists. The two are not
symmetric and only the second is a lie.

Run: python experiments/rectangularise/fit_rects.py [n] [--resplan]
"""
import json
import math
import sys
import time
from collections import Counter, defaultdict, deque
from pathlib import Path

import numpy as np
from ortools.sat.python import cp_model
from shapely import contains_xy
from shapely.affinity import rotate
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from measure_swiss import (  # noqa: E402
    BAND, MIN_ROOM_AREA, _op, _poly, bbox_rect, dwelling_frame,
)

OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)

GRID_MM = 250            # ADR 0001 / ticket 15: the shipped solve grid
GRID = GRID_MM / 1000.0
WALL_REACH = 0.35        # a cell further than this from every room is outside
DOOR_CELLS = 4           # 1.0 m of contact: ~900 structural + t_int (ADR 0001 c3)
AREA_TOL = 0.10          # per-room area band, as a fraction of the watershed area
TIME_LIMIT = 10.0
SOFT_WEIGHT = 100_000   # solver.py soft_weight: coverage degrades, never fails
MAX_NOTCHES = 2         # ADR 0003: v1 Envelope is bbox minus at most two notches
MIN_NOTCH_CELLS = 4     # 0.25 m2: below this a 'notch' is a rasterisation sliver
WORKERS = 4              # ticket 15: two workers is a floor for correctness


# ------------------------------------------------------------------ watershed

def watershed(geoms):
    """Label every 250 mm cell of the dwelling with the room that owns it.

    Returns (labels, x0, y0) where labels is (ny, nx) int8, -1 outside.
    """
    u = _op(unary_union, geoms)
    if u is None or u.is_empty:
        return None, 0, 0
    x0, y0, x1, y1 = u.bounds
    x0 -= WALL_REACH
    y0 -= WALL_REACH
    nx = int(math.ceil((x1 + WALL_REACH - x0) / GRID))
    ny = int(math.ceil((y1 + WALL_REACH - y0) / GRID))
    if nx * ny > 60_000 or nx < 2 or ny < 2:
        return None, 0, 0
    cx = x0 + (np.arange(nx) + 0.5) * GRID
    cy = y0 + (np.arange(ny) + 0.5) * GRID
    gx, gy = np.meshgrid(cx, cy)
    px, py = gx.ravel(), gy.ravel()

    lab = np.full(px.shape, -1, dtype=np.int16)
    for i, g in enumerate(geoms):
        hit = contains_xy(g, px, py) & (lab < 0)
        lab[hit] = i
    # Wall cells: to the nearest room, which cuts each wall at its centreline.
    from shapely.geometry import Point
    idx = np.flatnonzero(lab < 0)
    for k in idx:
        p = Point(px[k], py[k])
        d = [(g.distance(p), i) for i, g in enumerate(geoms)]
        dm, im = min(d)
        if dm <= WALL_REACH:
            lab[k] = im
    return lab.reshape(ny, nx), x0, y0


def keep_largest_component(lab):
    """A dwelling must be one connected region; strip rasterisation islands."""
    ny, nx = lab.shape
    seen = np.zeros_like(lab, dtype=bool)
    best, best_n = None, 0
    for sy in range(ny):
        for sx in range(nx):
            if lab[sy, sx] < 0 or seen[sy, sx]:
                continue
            q, cells = deque([(sy, sx)]), []
            seen[sy, sx] = True
            while q:
                y, x = q.popleft()
                cells.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < ny and 0 <= xx < nx and lab[yy, xx] >= 0 and not seen[yy, xx]:
                        seen[yy, xx] = True
                        q.append((yy, xx))
            if len(cells) > best_n:
                best, best_n = cells, len(cells)
    out = np.full_like(lab, -1)
    for y, x in best or []:
        out[y, x] = lab[y, x]
    return out


def components(mask):
    """Connected components of a boolean mask, 4-connected. Returns list of cell lists."""
    ny, nx = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    out = []
    for sy in range(ny):
        for sx in range(nx):
            if not mask[sy, sx] or seen[sy, sx]:
                continue
            q, cells = deque([(sy, sx)]), []
            seen[sy, sx] = True
            while q:
                y, x = q.popleft()
                cells.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < ny and 0 <= xx < nx and mask[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        q.append((yy, xx))
            out.append(cells)
    return out


def max_rect_in_mask(mask):
    """Largest all-true axis-aligned rectangle, by max-rectangle-in-histogram."""
    ny, nx = mask.shape
    best = (0, 0, 0, 0, 0)
    heights = np.zeros(nx, dtype=np.int64)
    for i in range(ny):
        heights = np.where(mask[i], heights + 1, 0)
        stack = []
        for j in range(nx + 1):
            h = int(heights[j]) if j < nx else 0
            start = j
            while stack and stack[-1][1] >= h:
                s, sh = stack.pop()
                a = sh * (j - s)
                if a > best[0]:
                    best = (a, i - sh + 1, s, i, j - 1)
                start = s
            stack.append((start, h))
    if best[0] == 0:
        return None
    _, r0, c0, r1, c1 = best
    return (c0, r0, c1 + 1, r1 + 1)


def envelope_approx(domain, max_notches=2):
    """The v1-expressible Envelope for this dwelling: bbox minus <= k notches.

    ADR 0003 fixes v1's Envelope as rectilinear, bbox minus at most two notches
    (rect / L / U / T), and records that the cap is unevidenced in both
    directions. This is that measurement: how many notches a real dwelling
    actually needs, and what the cap costs the ones that need more.

    A complement component that touches the bbox border is a notch. One that
    does not is an interior hole -- a shaft or lightwell, already excluded from
    the room set -- and v1 has no such thing, so it is filled.
    """
    ny, nx = domain.shape
    ys, xs = np.nonzero(domain)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    sub = domain[y0:y1, x0:x1]
    comp = ~sub
    parts = components(comp)
    border, holes = [], []
    h, w = sub.shape
    for cells in parts:
        if any(y in (0, h - 1) or x in (0, w - 1) for y, x in cells):
            border.append(cells)
        else:
            holes.append(cells)
    border.sort(key=len, reverse=True)

    def env_at(k):
        # A notch is the largest rectangle INSIDE the complement component, not
        # the component's bounding box. The bbox over-cuts -- it removes dwelling
        # the notch never covered -- and measured that way it deleted a room
        # outright in 15% of dwellings, which is an artefact of the
        # approximation rather than anything ADR 0003 says. Under-cutting leaves
        # a little non-dwelling inside the Envelope, which shows up as envelope
        # loss and costs a room nothing.
        e = np.ones_like(sub, dtype=bool)
        rects = []
        for cells in border[:k]:
            m = np.zeros_like(sub, dtype=bool)
            for (cyy, cxx) in cells:
                m[cyy, cxx] = True
            r = max_rect_in_mask(m)
            if r is None:
                continue
            rects.append(r)
            e[r[1]:r[3], r[0]:r[2]] = False
        return e, rects

    # A 250 mm raster of a real outline manufactures slivers along every wall,
    # and counting those as notches would inflate the number ADR 0003 caps. Only
    # a complement component of at least MIN_NOTCH_CELLS is a notch; the rest is
    # rasterisation, and it shows up as envelope loss instead.
    real = [c for c in border if len(c) >= MIN_NOTCH_CELLS]
    ladder = {}
    for k in range(0, 5):
        e, _ = env_at(k)
        ladder[k] = round(float((e ^ sub).sum()) / max(int(sub.sum()), 1), 5)

    env, notches = env_at(max_notches)
    loss = float((env ^ sub).sum()) / max(int(sub.sum()), 1)
    return env, notches, {
        "notches_all": len(border),
        "notches_needed": len(real),
        "notches_used": len(notches),
        "holes_filled": sum(len(c) for c in holes),
        "envelope_loss": loss,
        "envelope_loss_by_k": ladder,
        "bbox_fill": float(sub.sum()) / (h * w),
    }, (y0, x0)


def obstacle_rects(mask):
    """Greedy maximal-rectangle cover of the cells OUTSIDE the domain.

    These become fixed boxes in AddNoOverlap2D, exactly as the solver treats an
    Envelope notch. Also the count that says how many notches this dwelling
    needs -- which ADR 0003 caps at two, and nobody had measured.
    """
    m = mask.copy()
    ny, nx = m.shape
    rects = []
    while True:
        ys, xs = np.nonzero(m)
        if len(ys) == 0:
            break
        y, x = ys[0], xs[0]
        w = 0
        while x + w < nx and m[y, x + w]:
            w += 1
        h = 1
        while y + h < ny and m[y + h, x:x + w].all():
            h += 1
        rects.append((x, y, x + w, y + h))
        m[y:y + h, x:x + w] = False
    return rects


def truth_from_labels(lab, n):
    """Per-room cell bbox, cell area, and the discrete contact graph."""
    areas, boxes = [], []
    for i in range(n):
        ys, xs = np.nonzero(lab == i)
        if len(ys) == 0:
            return None
        areas.append(int(len(ys)))
        boxes.append((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))
    run = Counter()
    a, b = lab[:, :-1], lab[:, 1:]
    for u, v in zip(a[(a >= 0) & (b >= 0) & (a != b)], b[(a >= 0) & (b >= 0) & (a != b)]):
        run[(min(u, v), max(u, v))] += 1
    a, b = lab[:-1, :], lab[1:, :]
    for u, v in zip(a[(a >= 0) & (b >= 0) & (a != b)], b[(a >= 0) & (b >= 0) & (a != b)]):
        run[(min(u, v), max(u, v))] += 1
    edges = {k for k, c in run.items() if c >= DOOR_CELLS}
    return areas, boxes, edges, run


# ------------------------------------------------------------------ the fit

def agreement_terms(m, i, X1, X2, Y1, Y2, rowpre, nx, ny):
    """Exact count of cells inside room i's rectangle that really belong to it.

    `rowpre[y][x]` is the number of label-i cells in row y left of column x, so
    one row contributes `rowpre[y][x2] - rowpre[y][x1]` when the row is inside
    the rectangle and nothing when it is not. Both lookups are AddElement over a
    constant array, which keeps this linear in rows rather than in cells.
    """
    out = []
    for y in range(ny):
        b1 = m.NewBoolVar(f"b1_{i}_{y}")
        m.Add(Y1[i] <= y).OnlyEnforceIf(b1)
        m.Add(Y1[i] >= y + 1).OnlyEnforceIf(b1.Not())
        b2 = m.NewBoolVar(f"b2_{i}_{y}")
        m.Add(Y2[i] >= y + 1).OnlyEnforceIf(b2)
        m.Add(Y2[i] <= y).OnlyEnforceIf(b2.Not())
        act = m.NewBoolVar(f"act_{i}_{y}")
        m.AddBoolAnd([b1, b2]).OnlyEnforceIf(act)
        m.AddBoolOr([b1.Not(), b2.Not()]).OnlyEnforceIf(act.Not())

        pre = rowpre[y]
        e1 = m.NewIntVar(0, nx, f"e1_{i}_{y}")
        e2 = m.NewIntVar(0, nx, f"e2_{i}_{y}")
        m.AddElement(X1[i], pre, e1)
        m.AddElement(X2[i], pre, e2)
        a = m.NewIntVar(0, nx, f"ag_{i}_{y}")
        m.Add(a == e2 - e1).OnlyEnforceIf(act)
        m.Add(a == 0).OnlyEnforceIf(act.Not())
        out.append(a)
    return out


def fit(env, n, areas, boxes, edges, truth=None, rel_true=None,
        time_limit=TIME_LIMIT, area_tol=AREA_TOL):
    """Fit n rectangles into a v1-expressible Envelope.

    Constraint structure copies the shipped formulation exactly (C10, amended):
    adjacency and no-overlap are HARD, exact tiling is SOFT. Posting coverage
    hard is what made the first version of this reject almost every real
    dwelling -- and it would also have been the wrong model, since the solver
    this corpus feeds does not post it hard either.
    """
    ny, nx = env.shape
    obstacles = obstacle_rects(~env)
    total = int(env.sum())

    m = cp_model.CpModel()
    X1, X2, Y1, Y2, XI, YI, AREA = [], [], [], [], [], [], []
    for i in range(n):
        x1 = m.NewIntVar(0, nx, f"x1_{i}")
        x2 = m.NewIntVar(0, nx, f"x2_{i}")
        y1 = m.NewIntVar(0, ny, f"y1_{i}")
        y2 = m.NewIntVar(0, ny, f"y2_{i}")
        w = m.NewIntVar(1, nx, f"w_{i}")
        h = m.NewIntVar(1, ny, f"h_{i}")
        m.Add(x2 == x1 + w)
        m.Add(y2 == y1 + h)
        ar = m.NewIntVar(1, nx * ny, f"a_{i}")
        m.AddMultiplicationEquality(ar, [w, h])
        lo = max(1, int(math.floor(areas[i] * (1 - area_tol))))
        hi = max(lo, int(math.ceil(areas[i] * (1 + area_tol))))
        m.Add(ar >= lo)
        m.Add(ar <= hi)
        AREA.append(ar)
        X1.append(x1); X2.append(x2); Y1.append(y1); Y2.append(y2)
        XI.append(m.NewIntervalVar(x1, w, x2, f"xi_{i}"))
        YI.append(m.NewIntervalVar(y1, h, y2, f"yi_{i}"))

    for (ox1, oy1, ox2, oy2) in obstacles:
        XI.append(m.NewIntervalVar(ox1, ox2 - ox1, ox2, f"ox{len(XI)}"))
        YI.append(m.NewIntervalVar(oy1, oy2 - oy1, oy2, f"oy{len(YI)}"))
    m.AddNoOverlap2D(XI, YI)

    # Exact tiling, SOFT: the shortfall is penalised, not forbidden.
    covered = m.NewIntVar(0, total, "covered")
    m.Add(covered == sum(AREA))
    uncovered = m.NewIntVar(0, total, "uncovered")
    m.Add(uncovered == total - covered)

    # Every separation direction the real dwelling ASSERTS is posted hard --
    # which is exactly what `fix_relations` does to a Proposal in the shipping
    # solver, and it is the whole point of fitting rather than approximating.
    # Without it the fit flips 2% of pairs outright: truth says the kitchen is
    # left of the hall and the tiling puts it right of it. A flipped pair is the
    # confident-wrong case, and no amount of cell agreement pays for one.
    #
    # Relations the truth ABSTAINS on are left free. They are where one room
    # wraps another, and a rectangle model has to pick a side; that choice is
    # forced by the model, not an error in it.
    if rel_true is not None:
        for (i, j), (rx, ry) in rel_true.items():
            if rx == "L":
                m.Add(X2[i] <= X1[j])
            elif rx == "R":
                m.Add(X2[j] <= X1[i])
            if ry == "B":
                m.Add(Y2[i] <= Y1[j])
            elif ry == "A":
                m.Add(Y2[j] <= Y1[i])

    # Every real adjacency must survive: flush faces, overlapping by a door run.
    for (i, j) in edges:
        opts = []
        for (a, b) in ((i, j), (j, i)):
            for axis in (0, 1):
                lit = m.NewBoolVar(f"adj_{i}_{j}_{a}_{axis}")
                if axis == 0:
                    m.Add(X2[a] == X1[b]).OnlyEnforceIf(lit)
                    lo = m.NewIntVar(0, ny, f"lo{len(opts)}_{i}_{j}")
                    hi = m.NewIntVar(0, ny, f"hi{len(opts)}_{i}_{j}")
                    m.AddMaxEquality(lo, [Y1[a], Y1[b]])
                    m.AddMinEquality(hi, [Y2[a], Y2[b]])
                    m.Add(hi - lo >= DOOR_CELLS).OnlyEnforceIf(lit)
                else:
                    m.Add(Y2[a] == Y1[b]).OnlyEnforceIf(lit)
                    lo = m.NewIntVar(0, nx, f"lo{len(opts)}_{i}_{j}")
                    hi = m.NewIntVar(0, nx, f"hi{len(opts)}_{i}_{j}")
                    m.AddMaxEquality(lo, [X1[a], X1[b]])
                    m.AddMinEquality(hi, [X2[a], X2[b]])
                    m.Add(hi - lo >= DOOR_CELLS).OnlyEnforceIf(lit)
                opts.append(lit)
        m.AddBoolOr(opts)

    # Objective: the number of 250 mm cells the rectangularisation gets wrong.
    #
    #   misassigned = covered by some room's rectangle, but not that room's cell
    #   uncovered   = a real cell no rectangle claims
    #
    # Both are in cells, so they add without a weight to invent, and the total is
    # directly the loss this conversion costs. L1 corner displacement -- the
    # SHIPPED objective -- is wrong here and was measured to be: it minimises how
    # far corners move, which among exact tilings is nearly uncorrelated with how
    # much of the dwelling ends up in the right room (IoU median 0.14).
    agree = []
    for i in range(n):
        if truth is None:
            break
        rowpre = []
        mask = (truth == i)
        for y in range(ny):
            row = np.concatenate([[0], np.cumsum(mask[y].astype(np.int32))])
            rowpre.append([int(v) for v in row])
        agree += agreement_terms(m, i, X1, X2, Y1, Y2, rowpre, nx, ny)
        for var, tgt in ((X1[i], boxes[i][0]), (Y1[i], boxes[i][1]),
                         (X2[i], boxes[i][2]), (Y2[i], boxes[i][3])):
            m.AddHint(var, tgt)
    agreement = m.NewIntVar(0, total, "agreement")
    m.Add(agreement == sum(agree))
    m.Minimize(uncovered + (covered - agreement))

    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = time_limit
    s.parameters.num_search_workers = WORKERS
    t = time.time()
    st = s.Solve(m)
    dt = time.time() - t
    name = s.StatusName(st)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"status": name, "seconds": dt, "obstacles": len(obstacles)}
    rects = [(s.Value(X1[i]), s.Value(Y1[i]), s.Value(X2[i]), s.Value(Y2[i]))
             for i in range(n)]
    return {"status": name, "seconds": dt, "obstacles": len(obstacles),
            "objective": s.ObjectiveValue(), "uncovered": s.Value(uncovered),
            "agreement": s.Value(agreement),
            "rects": rects, "domain_cells": total}


# ------------------------------------------------------------------ per dwelling

def run_dwelling(geoms, use_rel=True, use_adj=True, area_tol=AREA_TOL,
                 max_notches=MAX_NOTCHES, rel_scope="all"):
    lab, x0, y0 = watershed(geoms)
    if lab is None:
        return {"status": "NO_RASTER"}
    lab = keep_largest_component(lab)
    n = len(geoms)
    if any((lab == i).sum() == 0 for i in range(n)):
        return {"status": "ROOM_LOST_IN_RASTER"}
    t = truth_from_labels(lab, n)
    if t is None:
        return {"status": "ROOM_LOST_IN_RASTER"}
    areas, boxes, edges, run = t

    env, notches, envinfo, (oy, ox) = envelope_approx(lab >= 0, max_notches)
    # Ground truth re-expressed in the Envelope's own frame, so loss is measured
    # against what v1 could actually have drawn rather than against the raster.
    sub = np.full(env.shape, -1, dtype=lab.dtype)
    src = lab[oy:oy + env.shape[0], ox:ox + env.shape[1]]
    sub[env] = src[env]
    areas_e = [int((sub == i).sum()) for i in range(n)]
    if any(a == 0 for a in areas_e):
        return {"status": "ROOM_LOST_TO_ENVELOPE", **envinfo, "n": n}
    boxes_e = []
    for i in range(n):
        ys, xs = np.nonzero(sub == i)
        boxes_e.append((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))
    # Areas must be able to sum to the Envelope; rescale onto it.
    scale_a = env.sum() / max(sum(areas_e), 1)
    areas_e = [max(1, int(round(a * scale_a))) for a in areas_e]

    def rel_of(bs):
        out = {}
        for i in range(n):
            for j in range(i + 1, n):
                a, b = bs[i], bs[j]
                x = "L" if a[2] <= b[0] else "R" if b[2] <= a[0] else None
                y = "B" if a[3] <= b[1] else "A" if b[3] <= a[1] else None
                out[(i, j)] = (x, y)
        return out

    rt = rel_of(boxes_e)
    rt_post = rt if use_rel else None
    if rt_post is not None and rel_scope == "adjacent":
        # Only pairs that share a wall. A flip between two rooms at opposite ends
        # of the flat is a different kind of wrong from one between neighbours,
        # and it is worth knowing whether the cheap half buys most of the fidelity.
        rt_post = {k: v for k, v in rt.items() if k in edges}
    res = fit(env, n, areas_e, boxes_e, edges if use_adj else set(),
              truth=sub, rel_true=rt_post, area_tol=area_tol)
    res["truth_boxes"] = boxes_e
    res.update(envinfo)
    res["n"] = n
    res["edges_true"] = len(edges)
    res["cells"] = int(env.sum())
    if "rects" not in res:
        return res

    # Loss, measured back against the real rooms in the Envelope frame.
    ious, aerr, agree = [], [], 0
    for i, (rx1, ry1, rx2, ry2) in enumerate(res["rects"]):
        cell = np.zeros(env.shape, dtype=bool)
        cell[ry1:ry2, rx1:rx2] = True
        truth = sub == i
        inter = int((cell & truth).sum())
        union = int((cell | truth).sum())
        ious.append(inter / union if union else 0.0)
        aerr.append((int(cell.sum()) - areas_e[i]) / areas_e[i] if areas_e[i] else 0.0)
        agree += inter
    res["iou"] = ious
    res["aerr"] = aerr
    res["cell_agreement"] = agree / max(res["cells"], 1)

    # Did every real adjacency in fact survive? Hard-constrained, so this is an
    # assertion rather than a measurement -- it fires only if the model is wrong.
    kept = set()
    for (i, j) in edges:
        a, b = res["rects"][i], res["rects"][j]
        if a[2] == b[0] or b[2] == a[0]:
            if min(a[3], b[3]) - max(a[1], b[1]) >= DOOR_CELLS:
                kept.add((i, j))
        elif a[3] == b[1] or b[3] == a[1]:
            if min(a[2], b[2]) - max(a[0], b[0]) >= DOOR_CELLS:
                kept.add((i, j))
    res["edges_lost"] = len(edges - kept)

    # Does the fit KEEP the separation relations a bounding box preserves for
    # free? This is the one comparison that decides the conversion, because the
    # relation -- not the geometry -- is what the Proposal transmits.
    rf = rel_of(res["rects"])
    c = Counter()
    for k, t in rt.items():
        f = rf[k]
        for ax in (0, 1):
            if t[ax] == f[ax]:
                c["same"] += 1
            elif t[ax] is not None and f[ax] is None:
                c["weakened"] += 1
            elif t[ax] is None and f[ax] is not None:
                c["spurious"] += 1
            else:
                c["flipped"] += 1
    res["rel"] = dict(c)

    # Does a room that faced the outside still face it? This is the geometric
    # half of H8 -- the fit knows nothing about which Envelope edges are
    # exterior versus party, so it is boundary contact, not window frontage.
    def boundary_run(x1, y1, x2, y2):
        run = 0
        h, w = env.shape
        for x in range(x1, x2):
            if y1 == 0 or not env[y1 - 1, x]:
                run += 1
            if y2 == h or not env[y2, x]:
                run += 1
        for y in range(y1, y2):
            if x1 == 0 or not env[y, x1 - 1]:
                run += 1
            if x2 == w or not env[y, x2]:
                run += 1
        return run

    kept_b = lost_b = 0
    for i in range(n):
        t_run = boundary_run(*boxes_e[i])
        f_run = boundary_run(*res["rects"][i])
        if t_run >= DOOR_CELLS:
            if f_run >= DOOR_CELLS:
                kept_b += 1
            else:
                lost_b += 1
    res["boundary_kept"] = kept_b
    res["boundary_lost"] = lost_b
    return res


def load_swiss_geoms(items):
    geoms = []
    for _, wkt in items:
        from shapely import from_wkt
        g = _poly(from_wkt(wkt))
        if g is not None and g.area >= MIN_ROOM_AREA:
            geoms.append(g)
    if not (BAND[0] <= len(geoms) <= BAND[1]):
        return None
    ang, cen = dwelling_frame(geoms)
    if ang is None:
        return None
    return [rotate(g, -ang, origin=cen) for g in geoms]


def main_resplan(n_target):
    """The same fit over ResPlan, whose scale must be recovered per plan."""
    import io
    import measure_resplan as R

    plans = R.Restricted(io.BufferedReader(open(R.PKL, "rb"))).load()
    print(f"plans: {len(plans)}; fitting {n_target}", flush=True)
    recs, status = [], Counter()
    t0 = time.time()
    for p in plans:
        if len(recs) >= n_target:
            break
        if int(p.get("id", -1)) in R.BROKEN_IDS:
            continue
        geoms = resplan_geoms(p, R)
        if geoms is None:
            continue
        r = run_dwelling(geoms)
        r["k"] = str(p.get("id"))
        status[r["status"]] += 1
        recs.append(r)
        if len(recs) % 200 == 0:
            el = time.time() - t0
            print(f"  {len(recs)}  {dict(status)}  {el:.0f}s  "
                  f"{el / len(recs):.2f}s/plan", flush=True)
            json.dump(recs, open(OUT / "resplan_fit.json", "w"))
    print(f"done: {dict(status)}", flush=True)
    json.dump(recs, open(OUT / "resplan_fit.json", "w"))
    print(f"wrote {OUT / 'resplan_fit.json'}", flush=True)


def resplan_geoms(p, R):
    from shapely.affinity import scale as _scale
    geoms = []
    for k in R.ROOM_KEYS:
        for g in R.parts(p.get(k)):
            g = _poly(g)
            if g is not None:
                geoms.append(g)
    if not geoms:
        return None
    canvas = sum(g.area for g in geoms)
    for k in R.NOT_A_ROOM_KEYS:
        canvas += sum(g.area for g in R.parts(p.get(k)) if hasattr(g, "area"))
    area = p.get("area")
    if not area or canvas <= 0 or area < R.MIN_PLAN_AREA:
        return None
    mpu = math.sqrt(float(area) / canvas)
    geoms = [_scale(g, mpu, mpu, origin=(0, 0)) for g in geoms]
    geoms = [g for g in geoms if g.area >= MIN_ROOM_AREA]
    if not (BAND[0] <= len(geoms) <= BAND[1]):
        return None
    ang, cen = dwelling_frame(geoms)
    if ang is None:
        return None
    return [rotate(g, -ang, origin=cen) for g in geoms]


def main():
    import hashlib
    import pandas as pd
    from measure_swiss import COLS, GEOM, MD5_EMPTY, NOT_A_ROOM

    n_target = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    if "--resplan" in sys.argv:
        return main_resplan(n_target)
    dw = defaultdict(list)
    for chunk in pd.read_csv(GEOM, usecols=COLS, chunksize=500_000, dtype=str):
        a = chunk[(chunk["entity_type"] == "area") &
                  (chunk["unit_usage"] == "RESIDENTIAL") &
                  (chunk["apartment_id"] != MD5_EMPTY)]
        a = a[~a["entity_subtype"].isin(NOT_A_ROOM)]
        for s, f, ap, st, wkt in zip(a["site_id"], a["floor_id"], a["apartment_id"],
                                     a["entity_subtype"].fillna("<NA>"), a["geometry"]):
            dw[(s, f, ap)].append((st, wkt))
    keys = sorted(dw.keys())
    keys.sort(key=lambda k: hashlib.md5("|".join(k).encode()).hexdigest())
    print(f"dwellings: {len(dw)}; fitting {n_target}", flush=True)

    recs, status = [], Counter()
    t0 = time.time()
    for k in keys:
        if len(recs) >= n_target:
            break
        geoms = load_swiss_geoms(dw[k])
        if geoms is None:
            continue
        r = run_dwelling(geoms)
        r["k"] = "|".join(k)
        r["types"] = [t for t, _ in dw[k]][:r.get("n", 0)]
        status[r["status"]] += 1
        recs.append(r)
        if len(recs) % 200 == 0:
            el = time.time() - t0
            print(f"  {len(recs)}  {dict(status)}  {el:.0f}s  "
                  f"{el / len(recs):.2f}s/dwelling", flush=True)
            json.dump(recs, open(OUT / "swiss_fit.json", "w"))
    print(f"done: {dict(status)}", flush=True)
    json.dump(recs, open(OUT / "swiss_fit.json", "w"))
    print(f"wrote {OUT / 'swiss_fit.json'}", flush=True)


if __name__ == "__main__":
    main()
