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

# ADR 0014: a Room is one or two axis-aligned rectangles. A rectangle beyond the
# first carries a universal leg floor of 900 mm CLEAR, and the two must share at
# least 900 mm of edge. This fit works on the watershed / CENTRELINE plane, so a
# part w cells wide is 250w mm centreline and 250w - t_int clear. The realisable
# value of a 900 mm clear floor at the shipped grid and t_int 150 is 1 100 mm
# (ADR 0009, CONTEXT.md's *Realisable minimum*), which is 5 cells: 4 cells give
# 1 000 - 150 = 850 mm clear and miss it.
T_INT_MM = 150          # ADR 0010
LEG_CLEAR_MM = 900      # ADR 0014: hall/corridor minimum, no new provenance
LEG_CELLS = int(math.ceil((LEG_CLEAR_MM + T_INT_MM) / GRID_MM))   # 5
JOIN_CELLS = LEG_CELLS  # ADR 0014's join predicate is the same 900 mm clear


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


def contact_opts(m, a, b, L, X1, X2, Y1, Y2, nx, ny, pres, tag):
    """Literals whose truth implies parts a and b share a flush edge of >= L cells.

    One-directional -- `lit => contact` -- so a caller asserts AddBoolOr over the
    returned list. Choosing an option that involves an absent part also forces
    that part present, which is `solver_parts._gated`'s lesson posted the other
    way round: an absent part sits at the origin with zero size, and every face
    it appears to offer has zero overlap, so absence is already self-killing
    here. The implication is belt and braces, and it is what lets the join and
    the adjacency OR mean what they say.
    """
    opts = []
    for (u, v) in ((a, b), (b, a)):
        for axis in (0, 1):
            lit = m.NewBoolVar(f"{tag}{len(opts)}_{a}_{b}")
            if axis == 0:
                m.Add(X2[u] == X1[v]).OnlyEnforceIf(lit)
                lo = m.NewIntVar(0, ny, f"lo{tag}{len(opts)}_{a}_{b}")
                hi = m.NewIntVar(0, ny, f"hi{tag}{len(opts)}_{a}_{b}")
                m.AddMaxEquality(lo, [Y1[u], Y1[v]])
                m.AddMinEquality(hi, [Y2[u], Y2[v]])
                m.Add(hi - lo >= L).OnlyEnforceIf(lit)
            else:
                m.Add(Y2[u] == Y1[v]).OnlyEnforceIf(lit)
                lo = m.NewIntVar(0, nx, f"lo{tag}{len(opts)}_{a}_{b}")
                hi = m.NewIntVar(0, nx, f"hi{tag}{len(opts)}_{a}_{b}")
                m.AddMaxEquality(lo, [X1[u], X1[v]])
                m.AddMinEquality(hi, [X2[u], X2[v]])
                m.Add(hi - lo >= L).OnlyEnforceIf(lit)
            for k in (a, b):
                if k in pres:
                    m.AddImplication(lit, pres[k])
            opts.append(lit)
    return opts


def fit(env, n, areas, boxes, edges, truth=None, rel_true=None,
        time_limit=TIME_LIMIT, area_tol=AREA_TOL, k_max=1,
        leg_cells=LEG_CELLS, join_cells=JOIN_CELLS, hint_parts=None,
        k_of=None, force_second=False):
    """Fit n Rooms of 1..k_max rectangles each into a v1-expressible Envelope.

    Constraint structure copies the shipped formulation exactly (C10, amended):
    adjacency and no-overlap are HARD, exact tiling is SOFT. Posting coverage
    hard is what made the first version of this reject almost every real
    dwelling -- and it would also have been the wrong model, since the solver
    this corpus feeds does not post it hard either.

    At k_max = 1 this is the shipped fit, structurally unchanged. At k_max = 2 a
    Room becomes 1..2 PARTS, per ADR 0014, and the units move with it:

      area        binds per ROOM, over the sum of its parts -- a room area is a
                  room area whatever its shape.
      leg floor   binds per PART, and only on a secondary. The primary is left
                  unbound exactly as at k = 1, so the arms differ in freedom and
                  not in what the truth is asked to satisfy.
      join        the two parts of a Room share an edge of at least `join_cells`.
      adjacency   binds per ROOM: any part of i flush with any part of j. Per
                  part would demand every leg touch, which is not what a door is.
      relations   bind per PART PAIR, which is what "Room a is left of Room b"
                  means once a is two boxes -- and is equivalent to posting it
                  over the two Rooms' bounding boxes, without the aux variables.

    The conversion is entitled to choose k where the solver is not (ADR 0014).
    The reason is the objective: the solver's is corner displacement, which knows
    nothing about what a room is for, while this one is misassigned cells against
    the real room. Here the ground truth IS the taste, so `solver decides` and
    `the Proposal decides` are the same decision made by the same evidence.
    """
    ny, nx = env.shape
    obstacles = obstacle_rects(~env)
    total = int(env.sum())

    m = cp_model.CpModel()
    parts_of, room_of = {}, {}
    X1, X2, Y1, Y2, XI, YI, AREA = [], [], [], [], [], [], []
    W_, H_ = [], []
    pres = {}
    if k_of is None:
        k_of = [k_max] * n
    for i in range(n):
        parts_of[i] = []
        for s in range(k_of[i]):
            p = len(X1)
            parts_of[i].append(p)
            room_of[p] = i
            second = s > 0
            x1 = m.NewIntVar(0, nx, f"x1_{p}")
            x2 = m.NewIntVar(0, nx, f"x2_{p}")
            y1 = m.NewIntVar(0, ny, f"y1_{p}")
            y2 = m.NewIntVar(0, ny, f"y2_{p}")
            w = m.NewIntVar(0 if second else 1, nx, f"w_{p}")
            h = m.NewIntVar(0 if second else 1, ny, f"h_{p}")
            m.Add(x2 == x1 + w)
            m.Add(y2 == y1 + h)
            ar = m.NewIntVar(0 if second else 1, nx * ny, f"a_{p}")
            m.AddMultiplicationEquality(ar, [w, h])
            if second:
                # Absent by zero size, not by an optional interval: measured in
                # `room-rectangles/smoke_zero_box.py`, AddNoOverlap2D in the
                # pinned ortools ignores a zero-area box. Pinned to the origin
                # when absent so its coordinates stop being free variables.
                pr = m.NewBoolVar(f"pres_{p}")
                pres[p] = pr
                m.Add(w == 0).OnlyEnforceIf(pr.Not())
                m.Add(h == 0).OnlyEnforceIf(pr.Not())
                m.Add(x1 == 0).OnlyEnforceIf(pr.Not())
                m.Add(y1 == 0).OnlyEnforceIf(pr.Not())
                m.Add(w >= leg_cells).OnlyEnforceIf(pr)
                m.Add(h >= leg_cells).OnlyEnforceIf(pr)
                # The leg floor binds the PRIMARY too, once this Room is two
                # rectangles. ADR 0014 writes it as "any rectangle beyond the
                # first", but it also binds minima "per constituent rectangle"
                # so that "each leg of an L must be usable", and a 250 mm
                # primary beside a 1 250 mm secondary is not an L -- it is a
                # rectangle with a wart. Gated, so a Room that stays one
                # rectangle keeps exactly the freedom it has at k = 1.
                #
                # It also buys the symmetry break below: with both parts
                # carrying the same floor, which one is `primary` is arbitrary,
                # so the pair can be ordered without deleting a solution. Order
                # lexicographically on (x1, y1), which is a strict total order
                # because two non-overlapping rectangles cannot share both.
                q = parts_of[i][0]
                m.Add(W_[q] >= leg_cells).OnlyEnforceIf(pr)
                m.Add(H_[q] >= leg_cells).OnlyEnforceIf(pr)
                m.Add(X1[q] * (ny + 1) + Y1[q]
                      <= x1 * (ny + 1) + y1).OnlyEnforceIf(pr)
                # Design A, ADR 0014: presence FIXED by what named this Room two
                # rectangles, not searched. The presence booleans are what cost
                # Design B its 3.9x variables; fixing them removes the search
                # without removing the shape.
                if force_second:
                    m.Add(pr == 1)
            AREA.append(ar)
            W_.append(w); H_.append(h)
            X1.append(x1); X2.append(x2); Y1.append(y1); Y2.append(y2)
            XI.append(m.NewIntervalVar(x1, w, x2, f"xi_{p}"))
            YI.append(m.NewIntervalVar(y1, h, y2, f"yi_{p}"))

    np_ = len(X1)
    for (ox1, oy1, ox2, oy2) in obstacles:
        XI.append(m.NewIntervalVar(ox1, ox2 - ox1, ox2, f"ox{len(XI)}"))
        YI.append(m.NewIntervalVar(oy1, oy2 - oy1, oy2, f"oy{len(YI)}"))
    m.AddNoOverlap2D(XI, YI)

    # Area binds per ROOM, over the sum of its parts.
    for i in range(n):
        lo = max(1, int(math.floor(areas[i] * (1 - area_tol))))
        hi = max(lo, int(math.ceil(areas[i] * (1 + area_tol))))
        tot_i = sum(AREA[p] for p in parts_of[i])
        m.Add(tot_i >= lo)
        m.Add(tot_i <= hi)

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
    #
    # A Room relation binds every PART of it. Gated on presence: with q absent,
    # `x2[p] <= x1[q]` reads `x2[p] <= 0` and forces a present part to zero
    # width -- the defect `room-rectangles/README.md` records as reporting 36%
    # INFEASIBLE against a control at 0% and making an L look compulsory.
    if rel_true is not None:
        for (i, j), (rx, ry) in rel_true.items():
            if rx is None and ry is None:
                continue
            for p in parts_of[i]:
                for q in parts_of[j]:
                    gate = [pres[k] for k in (p, q) if k in pres]

                    def post(c, gate=gate):
                        if gate:
                            m.Add(c).OnlyEnforceIf(gate)
                        else:
                            m.Add(c)

                    if rx == "L":
                        post(X2[p] <= X1[q])
                    elif rx == "R":
                        post(X2[q] <= X1[p])
                    if ry == "B":
                        post(Y2[p] <= Y1[q])
                    elif ry == "A":
                        post(Y2[q] <= Y1[p])

    # Every real adjacency must survive: flush faces, overlapping by a door run.
    # At room level -- any part of i against any part of j.
    for (i, j) in edges:
        opts = []
        for p in parts_of[i]:
            for q in parts_of[j]:
                opts += contact_opts(m, p, q, DOOR_CELLS, X1, X2, Y1, Y2,
                                     nx, ny, pres, f"adj{i}x{j}n")
        m.AddBoolOr(opts)

    # The two parts of a Room share an edge. Anything shorter is a pinch, not an
    # L -- ADR 0014's join predicate, at the same 900 mm clear as the leg floor.
    for i in range(n):
        ps = parts_of[i]
        if len(ps) < 2:
            continue
        for a, b in zip(ps, ps[1:]):
            opts = contact_opts(m, a, b, join_cells, X1, X2, Y1, Y2,
                                nx, ny, {}, f"jn{i}n")
            m.AddBoolOr(opts).OnlyEnforceIf(pres[b])

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
    #
    # An absent part contributes nothing without being gated: its rows are never
    # active, because `Y1 <= y` and `Y2 >= y + 1` cannot both hold at zero height.
    agree = []
    if truth is not None:
        rowpre_of = {}
        for i in range(n):
            mask = (truth == i)
            rows = []
            for y in range(ny):
                row = np.concatenate([[0], np.cumsum(mask[y].astype(np.int32))])
                rows.append([int(v) for v in row])
            rowpre_of[i] = rows
        for p in range(np_):
            agree += agreement_terms(m, p, X1, X2, Y1, Y2,
                                     rowpre_of[room_of[p]], nx, ny)
        for i in range(n):
            hp = (hint_parts or {}).get(i)
            ps = parts_of[i]
            if hp is None:
                hp = [boxes[i]]
            hp = list(hp) + [(0, 0, 0, 0)] * (len(ps) - len(hp))
            for p, box in zip(ps, hp):
                for var, tgt in ((X1[p], box[0]), (Y1[p], box[1]),
                                 (X2[p], box[2]), (Y2[p], box[3])):
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
    out = {"status": name, "seconds": dt, "obstacles": len(obstacles),
           "k_max": k_max, "n_parts": np_, "k_offered": list(k_of)}
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return out
    parts = []
    for i in range(n):
        got = []
        for p in parts_of[i]:
            r = (s.Value(X1[p]), s.Value(Y1[p]), s.Value(X2[p]), s.Value(Y2[p]))
            if r[2] > r[0] and r[3] > r[1]:
                got.append(r)
        parts.append(got)
    out.update({"objective": s.ObjectiveValue(), "uncovered": s.Value(uncovered),
                "agreement": s.Value(agreement), "parts": parts,
                "k_used": [len(g) for g in parts], "domain_cells": total})
    if max(k_of) == 1:
        out["rects"] = [g[0] for g in parts]
    return out


def two_rect_hint(mask, leg_cells):
    """A greedy 1..2 rectangle cover of one room's truth mask.

    Seeds the search at the shape the room actually is: the largest rectangle
    inside it, then the largest rectangle inside what is left. Only offered as a
    second part when that remainder clears the leg floor and touches the first,
    which is the same pair of conditions the model posts.
    """
    r1 = max_rect_in_mask(mask)
    if r1 is None:
        return None
    rest = mask.copy()
    rest[r1[1]:r1[3], r1[0]:r1[2]] = False
    if not rest.any():
        return [r1]
    best = None
    for cells in components(rest):
        m2 = np.zeros_like(mask)
        for (cy, cx) in cells:
            m2[cy, cx] = True
        r2 = max_rect_in_mask(m2)
        if r2 is None:
            continue
        if r2[2] - r2[0] < leg_cells or r2[3] - r2[1] < leg_cells:
            continue
        if best is None or (r2[2] - r2[0]) * (r2[3] - r2[1]) > (best[2] - best[0]) * (best[3] - best[1]):
            best = r2
    if best is None:
        return [r1]
    # The join: the two must share an edge of at least the leg floor, or the
    # hint is infeasible and CP-SAT throws it away for nothing. Same for the
    # primary's own floor and the (x1, y1) ordering the symmetry break posts --
    # a hint that breaks either is silently discarded, which is worse than no
    # hint because it looks like one was given.
    if r1[2] - r1[0] < leg_cells or r1[3] - r1[1] < leg_cells:
        return [r1]
    flush_x = (r1[2] == best[0] or best[2] == r1[0]) and \
        min(r1[3], best[3]) - max(r1[1], best[1]) >= leg_cells
    flush_y = (r1[3] == best[1] or best[3] == r1[1]) and \
        min(r1[2], best[2]) - max(r1[0], best[0]) >= leg_cells
    if not (flush_x or flush_y):
        return [r1]
    return sorted([r1, best], key=lambda r: (r[0], r[1]))


def run_dwelling(geoms, use_rel=True, use_adj=True, area_tol=AREA_TOL,
                 max_notches=MAX_NOTCHES, rel_scope="all", k_max=1,
                 leg_cells=LEG_CELLS, join_cells=JOIN_CELLS,
                 time_limit=TIME_LIMIT, hint="truth", k_select="shape",
                 force_second=False):
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

    # WHICH Rooms get a second rectangle, and where the hint starts.
    #
    # ADR 0014 refuses to let the SOLVER decide, and measured why: Design B --
    # every Room free to take a second box -- costs 3.9x the variables and
    # 11-12x the time to a first Plan, against 1.2-1.7x for Design A, which
    # gives a second box only to the Rooms something else named. Measured here
    # at k_select="free", the shipped 10 s budget then decides NOTHING: 0 of 40
    # dwellings proved either optimal or infeasible, so `converted` stopped
    # meaning representable and started meaning `found something in 10 s`.
    #
    # The conversion is the one place Design A is free, because the taste it
    # needs is sitting in front of it: the real room. `two_rect_hint` reads the
    # room's own mask and says whether a second rectangle clearing the leg floor
    # and joining the first is there to be had. That NAMES the Rooms, exactly as
    # a Proposal does at serving time -- which is also what the converted
    # dwelling has to become.
    hint_parts, k_of = None, [1] * n
    if k_max > 1:
        if k_select == "free":
            k_of = [k_max] * n
            if hint == "shape":
                hint_parts = {}
        elif k_select == "shape":
            hint_parts = {}
        else:
            raise ValueError(f"unknown k_select {k_select!r}")
        if hint_parts is not None:
            for i in range(n):
                h = two_rect_hint(sub == i, leg_cells)
                if h is not None:
                    hint_parts[i] = h
                    if k_select == "shape":
                        k_of[i] = len(h)
        if hint != "shape":
            hint_parts = None

    res = fit(env, n, areas_e, boxes_e, edges if use_adj else set(),
              truth=sub, rel_true=rt_post, area_tol=area_tol, k_max=k_max,
              leg_cells=leg_cells, join_cells=join_cells, time_limit=time_limit,
              hint_parts=hint_parts, k_of=k_of, force_second=force_second)
    res["truth_boxes"] = boxes_e
    res.update(envinfo)
    res["n"] = n
    res["edges_true"] = len(edges)
    res["cells"] = int(env.sum())
    res["hint"] = hint if k_max > 1 else "truth"
    res["k_select"] = k_select if k_max > 1 else "-"
    if "parts" not in res:
        return res

    # Everything below measures the fitted ROOM -- the union of its parts --
    # against the real room. At k = 1 a room is one rectangle and every number
    # here is the one the shipped fit reported.
    room_mask = []
    for i in range(n):
        cm = np.zeros(env.shape, dtype=bool)
        for (rx1, ry1, rx2, ry2) in res["parts"][i]:
            cm[ry1:ry2, rx1:rx2] = True
        room_mask.append(cm)

    ious, aerr, agree = [], [], 0
    for i in range(n):
        cell, truth_i = room_mask[i], (sub == i)
        inter = int((cell & truth_i).sum())
        union = int((cell | truth_i).sum())
        ious.append(inter / union if union else 0.0)
        aerr.append((int(cell.sum()) - areas_e[i]) / areas_e[i] if areas_e[i] else 0.0)
        agree += inter
    res["iou"] = ious
    res["aerr"] = aerr
    res["cell_agreement"] = agree / max(res["cells"], 1)

    # Did every real adjacency in fact survive? Hard-constrained, so this is an
    # assertion rather than a measurement -- it fires only if the model is wrong.
    # Counted as shared cell faces between the two room masks, which for flush
    # rectangles is the overlap run the constraint posted.
    def shared_faces(a, b):
        c = int((a[:, :-1] & b[:, 1:]).sum()) + int((a[:, 1:] & b[:, :-1]).sum())
        c += int((a[:-1, :] & b[1:, :]).sum()) + int((a[1:, :] & b[:-1, :]).sum())
        return c

    kept = {(i, j) for (i, j) in edges
            if shared_faces(room_mask[i], room_mask[j]) >= DOOR_CELLS}
    res["edges_lost"] = len(edges - kept)

    # Does the fit KEEP the separation relations a bounding box preserves for
    # free? This is the one comparison that decides the conversion, because the
    # relation -- not the geometry -- is what the Proposal transmits. Taken over
    # the fitted Room's bounding box, which is what a Room-level relation means.
    fit_boxes = []
    for i in range(n):
        ys, xs = np.nonzero(room_mask[i])
        fit_boxes.append((int(xs.min()), int(ys.min()),
                          int(xs.max()) + 1, int(ys.max()) + 1))
    rf = rel_of(fit_boxes)
    c = Counter()
    for k, tv in rt.items():
        f = rf[k]
        for ax in (0, 1):
            if tv[ax] == f[ax]:
                c["same"] += 1
            elif tv[ax] is not None and f[ax] is None:
                c["weakened"] += 1
            elif tv[ax] is None and f[ax] is not None:
                c["spurious"] += 1
            else:
                c["flipped"] += 1
    res["rel"] = dict(c)

    # Does a room that faced the outside still face it? This is the geometric
    # half of H8 -- the fit knows nothing about which Envelope edges are
    # exterior versus party, so it is boundary contact, not window frontage.
    outside = ~env

    def boundary_run_mask(cm):
        pad = np.pad(outside, 1, constant_values=True)
        c = int((cm & pad[:-2, 1:-1]).sum()) + int((cm & pad[2:, 1:-1]).sum())
        c += int((cm & pad[1:-1, :-2]).sum()) + int((cm & pad[1:-1, 2:]).sum())
        return c

    kept_b = lost_b = 0
    for i in range(n):
        tm = np.zeros(env.shape, dtype=bool)
        tm[boxes_e[i][1]:boxes_e[i][3], boxes_e[i][0]:boxes_e[i][2]] = True
        if boundary_run_mask(tm) >= DOOR_CELLS:
            if boundary_run_mask(room_mask[i]) >= DOOR_CELLS:
                kept_b += 1
            else:
                lost_b += 1
    res["boundary_kept"] = kept_b
    res["boundary_lost"] = lost_b
    return res


def load_swiss_geoms(items, keep_types=None):
    """Rotate a dwelling's room polygons into its own frame.

    `keep_types` collects the entity_subtype of each polygon that SURVIVES the
    filter, in the order the geometry list ends up in. Labelling a fitted
    dwelling from the unfiltered source list instead is the defect ticket 27
    measured at 22 of 1,787 dwellings (1.23 %): where a polygon below
    MIN_ROOM_AREA is not last, every label after it is off by one.
    """
    geoms = []
    for st, wkt in items:
        from shapely import from_wkt
        g = _poly(from_wkt(wkt))
        if g is not None and g.area >= MIN_ROOM_AREA:
            geoms.append(g)
            if keep_types is not None:
                keep_types.append(st)
    if not (BAND[0] <= len(geoms) <= BAND[1]):
        return None
    ang, cen = dwelling_frame(geoms)
    if ang is None:
        return None
    return [rotate(g, -ang, origin=cen) for g in geoms]


def main_resplan(n_target, opts):
    """The same fit over ResPlan, whose scale must be recovered per plan."""
    import io
    import measure_resplan as R

    out_path = OUT / opts["out"]
    plans = R.Restricted(io.BufferedReader(open(R.PKL, "rb"))).load()
    print(f"plans: {len(plans)}; fitting {n_target}  k_max={opts['k_max']} "
          f"select={opts['k_select']}", flush=True)
    # OR-Tools can abort the PROCESS on an internal CHECK failure -- the ResPlan
    # fit died that way after 1,000 plans, and it is a C++ abort Python cannot
    # catch. `--resume` picks up from the last checkpoint so a corpus-scale run
    # is a restart loop rather than one long gamble.
    recs, status = [], Counter()
    done = set()
    if opts["resume"] and out_path.exists():
        recs = json.load(open(out_path))
        done = {r["k"] for r in recs}
        for r in recs:
            status[r["status"]] += 1
        print(f"resuming: {len(recs)} already done", flush=True)
    t0 = time.time()
    for p in plans:
        if len(recs) >= n_target:
            break
        if int(p.get("id", -1)) in R.BROKEN_IDS:
            continue
        if str(p.get("id")) in done:
            continue
        geoms = resplan_geoms(p, R)
        if geoms is None:
            continue
        r = run_dwelling(geoms, k_max=opts["k_max"], hint=opts["hint"],
                         leg_cells=opts["leg"], join_cells=opts["join"],
                         time_limit=opts["time_limit"],
                         k_select=opts["k_select"], force_second=opts["force"])
        r["k"] = str(p.get("id"))
        status[r["status"]] += 1
        recs.append(r)
        if len(recs) % opts["every"] == 0:
            el = time.time() - t0
            fresh = max(len(recs) - len(done), 1)
            print(f"  {len(recs)}  {dict(status)}  {el:.0f}s  "
                  f"{el / fresh:.2f}s/plan", flush=True)
            json.dump(recs, open(out_path, "w"))
    print(f"done: {dict(status)}", flush=True)
    json.dump(recs, open(out_path, "w"))
    print(f"wrote {out_path}", flush=True)


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


def parse_opts(argv):
    """Flags, so the two arms differ only in what is stated on the command line."""
    def flag(name, cast, default):
        for a in argv:
            if a.startswith(name + "="):
                return cast(a.split("=", 1)[1])
        return default

    k_max = 2 if "--k2" in argv else 1
    resplan = "--resplan" in argv
    default_out = ("resplan_fit" if resplan else "swiss_fit") + \
        ("_k2" if k_max > 1 else "") + ".json"
    return {
        "k_max": k_max,
        "resplan": resplan,
        "hint": flag("--hint", str, "shape" if k_max > 1 else "truth"),
        "leg": flag("--leg", int, LEG_CELLS),
        "join": flag("--join", int, JOIN_CELLS),
        "time_limit": flag("--time", float, TIME_LIMIT),
        "out": flag("--out", str, default_out),
        "only": flag("--only", str, ""),
        "every": flag("--every", int, 200),
        "k_select": flag("--select", str, "shape"),
        "force": "--force-second" in argv,
        "resume": "--resume" in argv,
    }


def swiss_keys():
    """The dwelling order every Swiss run uses, so two runs are PAIRED.

    Cached, because parsing the 2.4 GB geometry CSV costs ~90 s and this ticket
    runs it a dozen times over: two paired arms, eight ablation arms, and the
    re-runs. The cache is keyed on nothing -- delete `out/swiss_dw.pkl` if the
    corpus or the filters change.
    """
    import hashlib
    import pickle
    import pandas as pd
    from measure_swiss import COLS, GEOM, MD5_EMPTY, NOT_A_ROOM

    cache = OUT / "swiss_dw.pkl"
    if cache.exists():
        dw, keys = pickle.load(open(cache, "rb"))
        return dw, keys

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
    pickle.dump((dict(dw), keys), open(cache, "wb"), protocol=4)
    return dw, keys


def main():
    n_target = int(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else 2000
    opts = parse_opts(sys.argv)
    if opts["resplan"]:
        return main_resplan(n_target, opts)

    out_path = OUT / opts["out"]
    dw, keys = swiss_keys()
    only = None
    if opts["only"]:
        only = set(json.load(open(opts["only"])))
        print(f"restricted to {len(only)} keys from {opts['only']}", flush=True)
    print(f"dwellings: {len(dw)}; fitting {n_target}  k_max={opts['k_max']} "
          f"select={opts['k_select']} force={opts['force']} hint={opts['hint']} "
          f"leg={opts['leg']} join={opts['join']} "
          f"time={opts['time_limit']}", flush=True)

    recs, status = [], Counter()
    done = set()
    if opts["resume"] and out_path.exists():
        recs = json.load(open(out_path))
        done = {r["k"] for r in recs}
        for r in recs:
            status[r["status"]] += 1
        print(f"resuming: {len(recs)} already done", flush=True)
    t0 = time.time()
    for k in keys:
        if len(recs) >= n_target:
            break
        kk = "|".join(k)
        if only is not None and kk not in only:
            continue
        if kk in done:
            continue
        types = []
        geoms = load_swiss_geoms(dw[k], types)
        if geoms is None:
            continue
        r = run_dwelling(geoms, k_max=opts["k_max"], hint=opts["hint"],
                         leg_cells=opts["leg"], join_cells=opts["join"],
                         time_limit=opts["time_limit"],
                         k_select=opts["k_select"], force_second=opts["force"])
        r["k"] = kk
        r["types"] = types
        status[r["status"]] += 1
        recs.append(r)
        if len(recs) % opts["every"] == 0:
            el = time.time() - t0
            fresh = max(len(recs) - len(done), 1)
            print(f"  {len(recs)}  {dict(status)}  {el:.0f}s  "
                  f"{el / fresh:.2f}s/dwelling", flush=True)
            json.dump(recs, open(out_path, "w"))
    print(f"done: {dict(status)}", flush=True)
    json.dump(recs, open(out_path, "w"))
    print(f"wrote {out_path}", flush=True)


if __name__ == "__main__":
    main()
