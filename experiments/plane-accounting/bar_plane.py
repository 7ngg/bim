"""ADR 0039's encoding, built as a subclass so `solver-toy/` is imported and
never edited.

Ticket 77. ADR 0039 decision 1 says the solver reads the **bar plane** -- the
Space area ADR 0001 publishes, `erode(U parts, t_int/2)` with an edge on the
Envelope NOT eroded. `solver.py::_add_dimensions` binds `mm_affine`:

    amm_i = (250 w_i - t)(250 h_i - t)                                    [A]

which erodes all four sides of every Room. Decision 2 replaces it with a band
subtracted per side, over the sides that face another Room:

    amm_i = 62 500 a_i  -  75 * SUM_{s in 4 sides} interior_len_mm(i, s)  [B]
    interior_len(i, s)  = side_len(i, s) - boundary_contact_len(i, s)

`a_i = w_i h_i` is H4's existing product and stays the only one. Every length is
an integer number of grid units, so [B] is

    amm_i = 62 500 a_i - 18 750 * (2 w_i + 2 h_i - SUM_s contact_units(i, s))

WHY [B] IS NOT [A] EVEN WITH NO BOUNDARY CONTACT.  Expand [A] at t = 150:
`62 500 wh - 37 500 (w + h) + 22 500`. Set every contact to zero in [B]:
`62 500 wh - 37 500 (w + h)`. The missing 22 500 mm2 is ADR 0039 decision 5's
corner residual -- 4 x 5 625, one per interior-interior corner. **[A] is
corner-exact and boundary-wrong; [B] is boundary-exact and corner-short** by at
most 0,0225 m2 per Room. That trade is the whole of what this directory
measures, and it is why `corners=True` exists below: the residual IS
recoverable, at a price, and ticket 77 item 4 asks for the price and the
realised distribution rather than the bound.

WHAT THE CLEAR DIMENSIONS DO.  Decision 2's `clear_w_i = 250 w_i - 75 * (number
of interior x-sides)` is posted here too, and it RELAXES the width floor by one
grid unit for a Room with BOTH x-sides on the Envelope: the bound becomes
`250 w >= 250 (min_w - 1)`. That is correct -- such a Room spans the Envelope
and loses no partition on either side -- and it is a feasible-set change, not
only an area one. `project_join.py`'s LIMIT 2 identity survives at one and two
interior sides and is re-asserted for all three cases in `selftest.py`.

The area term uses the exact interior *length* per side; the clear width uses a
*binary* per side. That asymmetry is ADR 0039's and it is right: an area is a
sum over the boundary, a clear width is one scalar for the whole Room, so a
partly-contacted side must be charged the full band. Conservative in the floor
direction on every Room where they disagree.

DIRECTION.  The contact literals are **biconditional** (ADR 0039 decision 4).
`_add_exterior`'s are forward-only, which is right for a floor and wrong for a
cap: leaving every literal false is free and understates the area, so a cap
posted on an understated area does not bind. `_add_exterior` is untouched; this
builds its own literal set.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "solver-toy"))

from solver import LayoutProjector, SolveConfig                      # noqa: E402
from geometry import Envelope, Rect                                  # noqa: E402
from scenarios import Brief, Proposal                                # noqa: E402

GRID_MM = 250
CELL_MM2 = GRID_MM * GRID_MM            # 62 500
CORNER_MM2 = 75 * 75                    # 5 625, at t_int 150


# ---------------------------------------------------------------------------
# The four sides of a Room, as (name, face axis, which Room coordinate must be
# flush with the face, which axis the face spans).
#
# 'v' faces are vertical, at x == coord, spanning y. A Room's WEST side lies on
# one iff x1 == coord, and its length is h. Symmetrically for the rest.
# ---------------------------------------------------------------------------
SIDES = (("W", "v", "x1", "y"),
         ("E", "v", "x2", "y"),
         ("S", "h", "y1", "x"),
         ("N", "h", "y2", "x"))

# The unit edge of each side adjoining each corner. `(side, high_end)`: the
# corner square at (x1,y1) is eroded on the x axis iff the W side's LOW unit
# edge is interior, and on the y axis iff the S side's LOW unit edge is.
CORNERS = (("SW", "W", False, "S", False),
           ("SE", "E", False, "S", True),
           ("NW", "W", True, "N", False),
           ("NE", "E", True, "N", True))


def _interior_mask(env: Envelope):
    inside = [[True] * env.H for _ in range(env.W)]
    for n in env.notches:
        for x in range(max(0, n.x1), min(env.W, n.x2)):
            for y in range(max(0, n.y1), min(env.H, n.y2)):
                inside[x][y] = False
    return inside


def _outside_reachable(env: Envelope, inside):
    """Complement cells 4-connected to the bbox edge.

    ADR 0028's ENCLOSED void is deliberately excluded, which is the same line
    `absolute_area.outside_of` draws and states: *"a void is bounded by wall on
    every side, so its edges cost erosion exactly as an interior edge does; the
    notch and the exterior do not, because the erosion there lands on the
    external wall's inner face."* A Room's edge on an enclosed void therefore
    erodes and must not be credited as boundary contact.
    """
    W, H = env.W, env.H
    seen = [[False] * H for _ in range(W)]
    stack = []

    def push(x, y):
        if 0 <= x < W and 0 <= y < H and not inside[x][y] and not seen[x][y]:
            seen[x][y] = True
            stack.append((x, y))

    for x in range(W):
        push(x, 0)
        push(x, H - 1)
    for y in range(H):
        push(0, y)
        push(W - 1, y)
    while stack:
        x, y = stack.pop()
        push(x + 1, y)
        push(x - 1, y)
        push(x, y + 1)
        push(x, y - 1)
    return seen


def no_erode_faces(env: Envelope):
    """Every boundary unit edge whose OTHER side is the exterior or a
    boundary-touching notch, merged into maximal runs.

    ⚠️ ADR 0039 decision 2 names `Envelope.all_faces()` as the source, and
    `all_faces()` is one notch-class too wide: it returns the faces of an
    ENCLOSED void too, because it walks the boundary of the interior and an
    enclosed void bounds the interior exactly as the outside does. On the
    measurement plane they are not the same -- `space_m2` fills the outside and
    leaves the void open, so a Room's edge on a void erodes. Crediting it as
    boundary would make the solver's area LARGER than the bar's, which is the
    one direction `dim.max_area` cannot afford.

    Rare in this corpus -- 8 of 273 warped candidates hold any enclosed void at
    all, max share 0,5 % -- and not rare in the shipped contract, where ADR 0028
    puts `voids` on the Proposal as a first-class field.
    """
    W, H = env.W, env.H
    inside = _interior_mask(env)
    out = _outside_reachable(env, inside)

    def cell(x, y):
        return 0 <= x < W and 0 <= y < H and inside[x][y]

    def free(x, y):
        """Non-interior AND connected to the exterior: beyond the bbox counts."""
        if not (0 <= x < W and 0 <= y < H):
            return True
        return (not inside[x][y]) and out[x][y]

    edges: dict = {}
    for x in range(W + 1):
        for y in range(H):
            a, b = cell(x - 1, y), cell(x, y)
            if a == b:
                continue
            if free(x - 1, y) if b else free(x, y):
                edges.setdefault(("v", x), []).append(y)
    for y in range(H + 1):
        for x in range(W):
            a, b = cell(x, y - 1), cell(x, y)
            if a == b:
                continue
            if free(x, y - 1) if b else free(x, y):
                edges.setdefault(("h", y), []).append(x)

    faces: dict = {}
    for key, us in edges.items():
        us.sort()
        runs = []
        lo = prev = us[0]
        for u in us[1:]:
            if u == prev + 1:
                prev = u
                continue
            runs.append((lo, prev + 1))
            lo = prev = u
        runs.append((lo, prev + 1))
        faces[key] = runs
    return faces


def faces_by_coord(env: Envelope):
    """{('v'|'h', coord): [(lo, hi), ...]} -- the runs a Room's side may be
    flush with and NOT be eroded against.

    Grouping is what keeps the literal count down: one flush literal per Room
    per side per *coordinate*, not per run. Runs at one coordinate are disjoint
    by construction, so their overlaps with a Room's side sum without double
    counting.
    """
    return no_erode_faces(env)


# ---------------------------------------------------------------------------
# The oracle: [A], [B] and the corner term evaluated on a PLACED rectangle.
# `selftest.py` asserts the CP-SAT encoding reproduces these exactly.
# ---------------------------------------------------------------------------
def contact_units(env: Envelope, r: Rect) -> dict:
    """Per-side boundary contact of a placed Rect, in grid units."""
    by = faces_by_coord(env)
    got = {}
    for (name, kind, flush, span) in SIDES:
        c = {"x1": r.x1, "x2": r.x2, "y1": r.y1, "y2": r.y2}[flush]
        lo_r, hi_r = (r.y1, r.y2) if span == "y" else (r.x1, r.x2)
        tot = 0
        for (lo, hi) in by.get((kind, c), ()):
            tot += max(0, min(hi_r, hi) - max(lo_r, lo))
        got[name] = tot
    return got


def bar_area_mm2(env: Envelope, r: Rect, t_int_mm: int = 150) -> int:
    """[B] on a placed Rect. The formula, not the truth: short by `CORNER_MM2`
    per interior-interior corner."""
    band = t_int_mm // 2
    con = contact_units(env, r)
    interior = ((r.h - con["W"]) + (r.h - con["E"])
                + (r.w - con["S"]) + (r.w - con["N"]))
    return CELL_MM2 * r.w * r.h - band * GRID_MM * interior


def solver_area_mm2(r: Rect, t_int_mm: int = 150) -> int:
    """[A] on a placed Rect -- the incumbent's plane."""
    return (GRID_MM * r.w - t_int_mm) * (GRID_MM * r.h - t_int_mm)


def _unit_on_boundary(by, kind: str, coord: int, base: int) -> bool:
    """Is the unit edge at (`kind`, `coord`, [base, base+1]) on the Envelope?"""
    for (lo, hi) in by.get((kind, coord), ()):
        if lo <= base <= hi - 1:
            return True
    return False


def corner_edges(r: Rect):
    """The two unit edges adjoining each corner, as
    ((name, 'v', x, y_base), ('h', y, x_base))."""
    out = []
    for (cname, vs, v_hi, hs, h_hi) in CORNERS:
        x = r.x1 if vs == "W" else r.x2
        y = r.y1 if hs == "S" else r.y2
        ybase = (r.y2 - 1) if v_hi else r.y1
        xbase = (r.x2 - 1) if h_hi else r.x1
        out.append((cname, ("v", x, ybase), ("h", y, xbase)))
    return out


def interior_corners(env: Envelope, r: Rect) -> int:
    """How many of the Rect's four corners have BOTH adjoining unit edges
    interior -- the count [B] over-subtracts a corner square for, times
    `CORNER_MM2`.

    "Both sides wholly interior" (ADR 0039 decision 5's rejected approximation)
    is a strictly smaller predicate; this is the point contact the decision says
    exactness needs.
    """
    by = faces_by_coord(env)
    n = 0
    for (_c, (vk, vc, vb), (hk, hc, hb)) in corner_edges(r):
        if (not _unit_on_boundary(by, vk, vc, vb)
                and not _unit_on_boundary(by, hk, hc, hb)):
            n += 1
    return n


def reflex_on_sides(env: Envelope, r: Rect) -> int:
    """Reflex vertices of the Envelope interior lying STRICTLY INSIDE one of the
    Rect's sides -- the term ADR 0039 does not have, and the one that makes the
    residual two-signed.

    Along one side of a Room, each unit edge is either on the Envelope (does not
    erode) or faces a partition (does). Where the state flips, the interior's
    boundary turns away from the Room's side: three of the four cells around
    that vertex are interior, which is a 270 degree corner of the interior. The
    erosion wraps around it and takes a further 75 x 75 square out of the Room,
    under `space_m2`'s mitre join.

    [B] cannot see it: it subtracts a band per side, over a length, and this is
    a loss at a POINT that lies on no side's end. It is the exact mirror of the
    corner term and it carries the opposite sign, so a Room with more reflex
    vertices on its sides than interior corners is one [B] reads too LARGE.
    """
    by = faces_by_coord(env)
    n = 0
    for (coord, lo_r, hi_r, kind) in ((r.x1, r.y1, r.y2, "v"),
                                      (r.x2, r.y1, r.y2, "v"),
                                      (r.y1, r.x1, r.x2, "h"),
                                      (r.y2, r.x1, r.x2, "h")):
        st = [_unit_on_boundary(by, kind, coord, u) for u in range(lo_r, hi_r)]
        n += sum(1 for a, b in zip(st, st[1:]) if a != b)
    return n


def true_bar_area_mm2(env: Envelope, r: Rect, t_int_mm: int = 150) -> int:
    """The bar plane, exactly.

        truth = [B] + 5 625 * (interior corners - reflex vertices on the sides)

    For a single rectangle inside `env` this equals `absolute_area.space_m2` x
    1e6 to the millimetre squared -- `selftest.py` asserts it over four Envelope
    families, and `residual.py` over the corpus.
    """
    return bar_area_mm2(env, r, t_int_mm) + CORNER_MM2 * (
        interior_corners(env, r) - reflex_on_sides(env, r))


# ---------------------------------------------------------------------------
class BarPlaneProjector(LayoutProjector):
    """`LayoutProjector` with `_add_dimensions` on ADR 0039's plane.

    Everything else -- H1, H2, H3, relations, contacts, H8/H9/H10, objective,
    hint -- is the parent's, unmodified. Three knobs:

      plane    "solver" reproduces the incumbent's `mm_affine` line for line, so
               the A arm and the B arm differ in ONE method and share every
               other line of the build. "bar" is [B].
      corners  add the exact corner term back. ADR 0039 decision 5 drops it;
               this exists to price the drop rather than assert it.
      caps     per-Room upper bound in mm2 (`dim.max_area`), or None. `None` is
               what `solver.py` does today: it posts no cap at all.
    """

    def __init__(self, brief: Brief, proposal: Proposal, cfg: SolveConfig,
                 plane: str = "bar", corners: bool = False, caps=None):
        self.plane = plane
        self.corners = corners
        self.caps = caps
        self.contact_lits = 0
        self.contact_ints = 0
        self.caps_posted = 0
        super().__init__(brief, proposal, cfg)

    # -- reified per-side boundary contact ----------------------------------
    def _flush_lit(self, expr, coord: int, name: str):
        """Biconditional `expr == coord`."""
        m = self.m
        v = m.NewBoolVar(name)
        m.Add(expr == coord).OnlyEnforceIf(v)
        m.Add(expr != coord).OnlyEnforceIf(v.Not())
        self.contact_lits += 1
        return v

    def _contact_side(self, i: int, name: str, kind: str, flush: str, span: str):
        """`boundary_contact_len(i, s)` in grid units, as an IntVar or None.

        One flush literal per coordinate; under it the overlap is
        `max(0, min(hi_r, hi_f) - max(lo_r, lo_f))` summed over the disjoint
        runs at that coordinate -- `AddMaxEquality` / `AddMinEquality`, no
        products.
        """
        m = self.m
        fvar = {"x1": self.x1[i], "x2": self.x2[i],
                "y1": self.y1[i], "y2": self.y2[i]}[flush]
        lo_r, hi_r = ((self.y1[i], self.y2[i]) if span == "y"
                      else (self.x1[i], self.x2[i]))
        cap = self.env.H if span == "y" else self.env.W

        terms = []
        for (k, c) in self._coords[kind]:
            runs = self.faces[(k, c)]
            fl = self._flush_lit(fvar, c, f"fl_{i}{name}_{c}")
            for ri, (lo, hi) in enumerate(runs):
                lv = m.NewIntVar(0, cap, f"clo_{i}{name}_{c}_{ri}")
                hv = m.NewIntVar(0, cap, f"chi_{i}{name}_{c}_{ri}")
                m.AddMaxEquality(lv, [lo_r, lo])
                m.AddMinEquality(hv, [hi_r, hi])
                pos = m.NewIntVar(0, cap, f"cps_{i}{name}_{c}_{ri}")
                m.AddMaxEquality(pos, [hv - lv, 0])
                ov = m.NewIntVar(0, cap, f"cov_{i}{name}_{c}_{ri}")
                m.Add(ov == pos).OnlyEnforceIf(fl)
                m.Add(ov == 0).OnlyEnforceIf(fl.Not())
                self.contact_ints += 4
                terms.append(ov)
        if not terms:
            return None
        tot = m.NewIntVar(0, cap, f"con_{i}{name}")
        m.Add(tot == sum(terms))
        self.contact_ints += 1
        return tot

    # -- the exact corner term, built so it can be priced -------------------
    def _unit_on_face(self, i: int, kind: str, coordexpr, base, tag: str):
        """Reified: the unit edge at (`kind`, `coordexpr`, [base, base+1]) lies
        on a boundary face. Contact at a POINT rather than over a length --
        which is exactly why ADR 0039 decision 5 calls exact recovery expensive.
        """
        m = self.m
        parts = []
        for (k, c) in self._coords[kind]:
            fl = self._flush_lit(coordexpr, c, f"ufl_{i}{tag}_{c}")
            for ri, (lo, hi) in enumerate(self.faces[(k, c)]):
                inr = m.NewBoolVar(f"uin_{i}{tag}_{c}_{ri}")
                m.Add(base >= lo).OnlyEnforceIf(inr)
                m.Add(base <= hi - 1).OnlyEnforceIf(inr)
                blo = m.NewBoolVar(f"ulo_{i}{tag}_{c}_{ri}")
                bhi = m.NewBoolVar(f"uhi_{i}{tag}_{c}_{ri}")
                m.Add(base >= lo).OnlyEnforceIf(blo)
                m.Add(base <= lo - 1).OnlyEnforceIf(blo.Not())
                m.Add(base <= hi - 1).OnlyEnforceIf(bhi)
                m.Add(base >= hi).OnlyEnforceIf(bhi.Not())
                m.AddBoolOr([blo.Not(), bhi.Not(), inr])
                onp = m.NewBoolVar(f"uon_{i}{tag}_{c}_{ri}")
                m.AddBoolAnd([fl, inr]).OnlyEnforceIf(onp)
                m.AddBoolOr([fl.Not(), inr.Not(), onp])
                self.contact_ints += 4
                parts.append(onp)
        out = m.NewBoolVar(f"uany_{i}{tag}")
        if parts:
            m.AddBoolOr(parts).OnlyEnforceIf(out)
            m.AddBoolAnd([p.Not() for p in parts]).OnlyEnforceIf(out.Not())
        else:
            m.Add(out == 0)
        return out

    def _corner_count(self, i: int):
        """Number of corners of Room i whose two adjoining unit edges are both
        interior. `IntVar` in [0, 4]."""
        m = self.m
        lits = []
        for (cname, vs, v_hi, hs, h_hi) in CORNERS:
            xexpr = self.x1[i] if vs == "W" else self.x2[i]
            yexpr = self.y1[i] if hs == "S" else self.y2[i]
            ybase = (self.y2[i] - 1) if v_hi else self.y1[i]
            xbase = (self.x2[i] - 1) if h_hi else self.x1[i]
            vb = self._unit_on_face(i, "v", xexpr, ybase, f"{cname}v")
            hb = self._unit_on_face(i, "h", yexpr, xbase, f"{cname}h")
            both = m.NewBoolVar(f"cor_{i}_{cname}")
            m.AddBoolAnd([vb.Not(), hb.Not()]).OnlyEnforceIf(both)
            m.AddBoolOr([vb, hb, both])
            lits.append(both)
        tot = m.NewIntVar(0, 4, f"ncor_{i}")
        m.Add(tot == sum(lits))
        return tot

    def _interior_side_count(self, i: int, names, cons):
        """How many of these two opposite sides face another Room. A side is
        interior iff its boundary contact is strictly less than its full
        length."""
        m = self.m
        out = []
        for nm in names:
            size = self.h[i] if nm in ("W", "E") else self.w[i]
            c = cons[nm]
            v = m.NewBoolVar(f"is_{i}{nm}")
            if c is None:
                m.Add(v == 1)
            else:
                m.Add(c <= size - 1).OnlyEnforceIf(v)
                m.Add(c >= size).OnlyEnforceIf(v.Not())
            out.append(v)
        tot = m.NewIntVar(0, 2, f"nint_{i}_{names[0]}")
        m.Add(tot == sum(out))
        return tot

    # -- H4/H5 on the chosen plane ------------------------------------------
    def _add_dimensions(self):
        m, b = self.m, self.brief
        W, H = self.env.W, self.env.H
        g, t = GRID_MM, self.cfg.t_int_mm
        band = t // 2
        if self.cfg.area_units != "mm_affine":
            raise ValueError("plane-accounting runs the shipped rig only "
                             f"(mm_affine); got {self.cfg.area_units!r}")
        if not self.cfg.erode_minima or self.cfg.minima_are_clear_grid:
            raise ValueError("plane-accounting runs the shipped rig only "
                             "(erode_minima on, minima_are_clear_grid off)")
        if t % 2:
            raise ValueError(f"t_int_mm {t} is odd; the band is t/2")

        self.faces = faces_by_coord(self.env)
        self._coords = {"v": sorted(k for k in self.faces if k[0] == "v"),
                        "h": sorted(k for k in self.faces if k[0] == "h")}
        self.area, self.area_mm2, self.mults = [], [], 0

        for i, spec in enumerate(b.rooms):
            a = m.NewIntVar(0, W * H, f"a_{i}")
            m.AddMultiplicationEquality(a, [self.w[i], self.h[i]])
            self.mults += 1
            self.area.append(a)
            k = b.max_aspect

            cw = m.NewIntVar(1, W * g, f"cw_{i}")
            ch = m.NewIntVar(1, H * g, f"ch_{i}")
            amm = m.NewIntVar(0, W * g * H * g, f"amm_{i}")

            if self.plane == "solver":
                # [A], verbatim from `solver.py::_add_dimensions`.
                m.Add(cw == self.w[i] * g - t)
                m.Add(ch == self.h[i] * g - t)
                m.Add(amm == g * g * a - g * t * (self.w[i] + self.h[i]) + t * t)
            elif self.plane == "bar":
                cons = {nm: self._contact_side(i, nm, kd, fl, sp)
                        for (nm, kd, fl, sp) in SIDES}
                tot = 0
                for nm in ("W", "E", "S", "N"):
                    if cons[nm] is not None:
                        tot = tot + cons[nm]
                int_units = (2 * self.h[i] + 2 * self.w[i]) - tot
                expr = g * g * a - band * g * int_units
                if self.corners:
                    expr = expr + CORNER_MM2 * self._corner_count(i)
                m.Add(amm == expr)
                nx = self._interior_side_count(i, ("W", "E"), cons)
                ny = self._interior_side_count(i, ("S", "N"), cons)
                m.Add(cw == self.w[i] * g - band * nx)
                m.Add(ch == self.h[i] * g - band * ny)
            else:
                raise ValueError(f"unknown plane {self.plane!r}")

            self.area_mm2.append(amm)

            m.Add(cw >= spec.min_w * g)
            m.Add(ch >= spec.min_h * g)
            m.Add(amm >= spec.min_area * g * g)
            m.Add(cw <= k * ch)
            m.Add(ch <= k * cw)

            if self.caps is not None and self.caps[i] is not None:
                m.Add(amm <= int(self.caps[i]))
                self.caps_posted += 1


def project_plane(brief, proposal, cfg, plane="bar", corners=False, caps=None):
    """`solver.project`'s signature plus the plane knobs. Returns the same
    `SolveResult`, with the encoding's own size added to `model_stats`."""
    p = BarPlaneProjector(brief, proposal, cfg, plane=plane,
                          corners=corners, caps=caps)
    res = p.solve()
    res.model_stats["contact_lits"] = p.contact_lits
    res.model_stats["contact_ints"] = p.contact_ints
    res.model_stats["caps_posted"] = p.caps_posted
    res.model_stats["faces"] = len(p.env.all_faces())
    res.model_stats["build_ms"] = round(p.build_time * 1000, 2)
    return res
