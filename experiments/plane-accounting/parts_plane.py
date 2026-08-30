"""ADR 0039's encoding for a Room that ADR 0014 gives ONE OR TWO rectangles.

Ticket 78. `bar_plane.py` derives and measures the encoding for a Room that is
one rectangle. ADR 0040 consequence 3 states the debt this file pays:

    `erode(A U B, t/2)` exceeds `erode(A) U erode(B)` by exactly the shared-edge
    band -- a term the per-side form does not carry, since it subtracts a band
    along an edge the union does not have.

THE TWO STATEMENTS THIS FILE MAKES

**1. The model form.** Sum the per-part band form over the parts and add the
join band back, twice, because both parts subtracted it:

    [B](U) = SUM_p [B](p)  +  2 * 75 * 250 * J        J = join length, grid units
           = 62 500 * SUM_p a_p  -  18 750 * ( SUM_p int_units(p)  -  2 J )

`int_units(p)` is `bar_plane`'s per-part quantity unchanged, so the boundary
half of the encoding is ticket 77's and is re-used method for method. `J` is
one new length per two-part Room -- seven auxiliary integers and seven literals,
O(1) in the Room rather than O(sides x faces) -- because the two parts are
interior-disjoint under `AddNoOverlap2D` and two interior-disjoint rectangles
meet in at most ONE maximal segment. There are no contact literals between a
Room's own parts beyond the flush pair, and item 1 of the ticket is answered by
that sentence.

**2. The truth.** One vertex rule covers one part and two, and it REPLACES
Part VIII's `corners - reflex` pair rather than extending it:

    truth(U) = 62 500 |U|  -  18 750 E_int(U)  +  5 625 * SUM_v w(v)

    w(v) = I(v)  -  nU(v) * [ nO(v) >= 1 ]

At a lattice vertex `v`, label each of the four cells round it `U` (this Room),
`F` (free: the exterior or a boundary-touching notch) or `O` (any other
interior: another Room, an enclosed void, an unassigned cell). `I(v)` counts the
four half-edges at `v` with one side `U` and the other `O` -- the eroding ones.
`nU`, `nO` count the quadrants.

WHY THAT IS THE WHOLE RULE.  Near `v` the eroded set is
`erode(S, d) INTERSECT U` for `S` = the union of the `U` and `F` quadrants, and
`S` is a cone. Unless `S` is the whole plane, `erode(S, d)` misses the `d`-box at
`v` entirely -- a quadrant, a half-plane, a bowtie and a three-quadrant cone all
retreat past it -- so the Room loses `nU * d^2` there. The per-side band form
subtracts `d^2` once per (U quadrant, eroding half-edge) incidence, which is
`I`. The correction is the difference, and when no quadrant is `O` nothing
erodes and `I` is already 0.

Part VIII's two named terms fall out as the one-rectangle case: at a corner with
both edges interior `I = 2, nU = 1`, giving `+1`; at a mid-side flip
`I = 1, nU = 2`, giving `-1`. The rule also reaches three places the pair could
not: an L's own reflex corner (`I = 2, nU = 3`, `-1`), a flush join end
(`I = 2, nU = 2`, `0` -- where naive per-part counting reports **two** interior
corners), and a Room touching an enclosed void at a point diagonally
(`I = 0, nU = 1, nO = 1`, `-1`).

⚠️ **`0,0225 m2` is not a bound and it was never one.** ADR 0040 already withdrew
the derivation; here `nU` reaches 3 and the reflex places multiply, so the
residual is stated as a measured distribution and nothing else.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "solver-toy"))
sys.path.insert(0, str(HERE.parent / "room-rectangles"))

from bar_plane import (CELL_MM2, CORNER_MM2, GRID_MM, SIDES,          # noqa: E402
                       BarPlaneProjector, _interior_mask,
                       _outside_reachable, faces_by_coord)
from geometry import Envelope, Rect                                   # noqa: E402
from solver_parts import PartConfig, PartProjector, PartResult         # noqa: E402

BAND_MM2_PER_UNIT = 75 * GRID_MM        # 18 750, at t_int 150
JOIN_MM2_PER_UNIT = 2 * BAND_MM2_PER_UNIT   # 37 500 -- both parts subtracted it


# ---------------------------------------------------------------------------
# The oracle, on placed rectangles.
# ---------------------------------------------------------------------------
def cell_labels(env: Envelope, rects):
    """`(label, cells)` where `label(x, y)` is `'U'`, `'F'` or `'O'`.

    `F` is `bar_plane.no_erode_faces`' own line, cell-wise rather than
    edge-wise: outside the bbox, or a notch component 4-connected to it. An
    ENCLOSED void is `O`, because `absolute_area.outside_of` excludes it and a
    Room's edge on one erodes.
    """
    inside = _interior_mask(env)
    out = _outside_reachable(env, inside)
    W, H = env.W, env.H
    cells = set()
    for r in rects:
        for x in range(r.x1, r.x2):
            for y in range(r.y1, r.y2):
                cells.add((x, y))

    def label(x: int, y: int) -> str:
        if (x, y) in cells:
            return "U"
        if not (0 <= x < W and 0 <= y < H):
            return "F"
        if (not inside[x][y]) and out[x][y]:
            return "F"
        return "O"

    return label, cells


def _span(rects):
    xs = [r.x1 for r in rects] + [r.x2 for r in rects]
    ys = [r.y1 for r in rects] + [r.y2 for r in rects]
    return min(xs) - 1, max(xs) + 1, min(ys) - 1, max(ys) + 1


def union_terms(env: Envelope, rects):
    """`(area_cells, eroding_unit_edges, vertex_sum)` for the union of `rects`."""
    label, cells = cell_labels(env, rects)
    x0, x1, y0, y1 = _span(rects)

    eint = 0
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            if {label(x - 1, y), label(x, y)} == {"U", "O"}:
                eint += 1                       # vertical edge at x over [y, y+1]
            if {label(x, y - 1), label(x, y)} == {"U", "O"}:
                eint += 1                       # horizontal edge at y over [x, x+1]

    wsum = 0
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            ne, nw = label(x, y), label(x - 1, y)
            sw, se = label(x - 1, y - 1), label(x, y - 1)
            quad = (ne, nw, sw, se)
            n_u = quad.count("U")
            if not n_u:
                continue
            n_o = quad.count("O")
            inc = sum(1 for a, b in ((nw, ne), (sw, se), (nw, sw), (se, ne))
                      if {a, b} == {"U", "O"})
            wsum += inc - (n_u if n_o else 0)
    return len(cells), eint, wsum


def true_union_mm2(env: Envelope, rects) -> int:
    """The bar plane over a Room's parts, exactly.

    Equal to `absolute_area.space_m2(rects, outside_of(env.parts)) * 1e6` to the
    millimetre squared -- asserted by `selftest_parts.py` over four Envelope
    families and by `arms_parts.py` over every solved Room.
    """
    a, eint, wsum = union_terms(env, rects)
    return CELL_MM2 * a - BAND_MM2_PER_UNIT * eint + CORNER_MM2 * wsum


def join_units(rects) -> int:
    """Length of the shared edge between two interior-disjoint parts, in grid
    units. Zero for a one-part Room, and for parts that meet at a point."""
    if len(rects) < 2:
        return 0
    p, q = rects[0], rects[1]
    if p.x2 == q.x1 or q.x2 == p.x1:
        return max(0, min(p.y2, q.y2) - max(p.y1, q.y1))
    if p.y2 == q.y1 or q.y2 == p.y1:
        return max(0, min(p.x2, q.x2) - max(p.x1, q.x1))
    return 0


def part_interior_units(env: Envelope, r: Rect) -> int:
    """`2w + 2h` minus the part's boundary contact -- `bar_plane`'s per-side
    quantity, summed, with the shared edge counted as interior because it is."""
    by = faces_by_coord(env)
    tot = 0
    for (_name, kind, flush, span) in SIDES:
        c = {"x1": r.x1, "x2": r.x2, "y1": r.y1, "y2": r.y2}[flush]
        lo_r, hi_r = (r.y1, r.y2) if span == "y" else (r.x1, r.x2)
        con = 0
        for (lo, hi) in by.get((kind, c), ()):
            con += max(0, min(hi_r, hi) - max(lo_r, lo))
        tot += ((r.h if span == "y" else r.w) - con)
    return tot


def bar_union_mm2(env: Envelope, rects, join: bool = True) -> int:
    """`[B]` over a Room's parts -- the quantity the model posts.

    `join=False` is the naive generalisation: the per-part form summed, which
    subtracts the join band twice along an edge the Room does not have.
    """
    a = sum(r.w * r.h for r in rects)
    ui = sum(part_interior_units(env, r) for r in rects)
    out = CELL_MM2 * a - BAND_MM2_PER_UNIT * ui
    if join:
        out += JOIN_MM2_PER_UNIT * join_units(rects)
    return out


def solver_union_mm2(rects, t_int_mm: int = 150) -> int:
    """`[A]` summed over the parts -- the incumbent plane, read at Room level."""
    return sum((GRID_MM * r.w - t_int_mm) * (GRID_MM * r.h - t_int_mm)
               for r in rects)


# ---------------------------------------------------------------------------
# The model.
# ---------------------------------------------------------------------------
class BarPartsProjector(PartProjector):
    """`room-rectangles/solver_parts.py`'s Design A with ONE method replaced.

    Everything the parts rig decides -- presence fixed by the Proposal, the join
    predicate, H6/H8 as an OR over parts, H9/H10 at Room level, relations in the
    part index space -- is `PartProjector`'s and is not touched here. The four
    reified-contact helpers are `BarPlaneProjector`'s, bound in unmodified, so
    the boundary half of this encoding is ticket 77's code and not a second copy
    of it.

    Knobs:

      plane      "solver" = `(250w - t)(250h - t)` per part, the incumbent.
                 "bar"    = ADR 0039's band form, per part.
      join       add the shared-edge band back. Only meaningful on "bar";
                 `join=False` prices the term this ticket exists to add.
      room_area  bind the area floor on the ROOM, per ADR 0014 and
                 `dim.statutory_min_area`'s own statement. `False` binds it on
                 the PRIMARY part, which is what `solver_parts` does today and
                 what `project_join.py` LIMIT 3 flags as strictly stricter.
      caps       per-ROOM `dim.max_area` in mm2, or None.
    """

    _flush_lit = BarPlaneProjector._flush_lit
    _contact_side = BarPlaneProjector._contact_side
    _interior_side_count = BarPlaneProjector._interior_side_count

    def __init__(self, brief, proposal, cfg, pc: PartConfig,
                 plane: str = "bar", join: bool = True,
                 room_area: bool = True, caps=None):
        if plane not in ("solver", "bar"):
            raise ValueError(f"unknown plane {plane!r}")
        self.plane = plane
        self.join = join
        self.room_area = room_area
        self.caps = caps
        self.contact_lits = 0
        self.contact_ints = 0
        self.join_ints = 0
        self.caps_posted = 0
        self.two_part_rooms = 0
        super().__init__(brief, proposal, cfg, pc)

    # -- the join length, in grid units ------------------------------------
    def _join_len(self, p: int, q: int, tag: str):
        """`J` for two interior-disjoint parts.

        `AddNoOverlap2D` covers every part pair including a Room's own, so the
        two meet in at most one maximal segment and one length is the whole
        term. The flush pair is rebuilt here rather than taken from
        `_add_join`'s `_contact`, because `_add_dimensions` runs first in
        `_build` -- seven integers and seven literals, and this file changes one
        method.
        """
        m = self.m
        W, H = self.env.W, self.env.H
        lits = []
        for (a, b, name) in ((self.x2[p], self.x1[q], "E"),
                             (self.x2[q], self.x1[p], "W"),
                             (self.y2[p], self.y1[q], "N"),
                             (self.y2[q], self.y1[p], "S")):
            lits.append(self._flush_lit(a, b, f"jf{name}_{tag}"))
        tE, tW, tN, tS = lits
        vx = m.NewBoolVar(f"jvx_{tag}")
        m.AddBoolOr([tE, tW]).OnlyEnforceIf(vx)
        m.AddImplication(tE, vx)
        m.AddImplication(tW, vx)
        hy = m.NewBoolVar(f"jhy_{tag}")
        m.AddBoolOr([tN, tS]).OnlyEnforceIf(hy)
        m.AddImplication(tN, hy)
        m.AddImplication(tS, hy)
        self.contact_lits += 2

        def overlap(lo1, hi1, lo2, hi2, cap, nm):
            lo = m.NewIntVar(0, cap, f"jlo{nm}_{tag}")
            hi = m.NewIntVar(0, cap, f"jhi{nm}_{tag}")
            m.AddMaxEquality(lo, [lo1, lo2])
            m.AddMinEquality(hi, [hi1, hi2])
            ov = m.NewIntVar(0, cap, f"jov{nm}_{tag}")
            m.AddMaxEquality(ov, [hi - lo, 0])
            self.join_ints += 3
            return ov

        oy = overlap(self.y1[p], self.y2[p], self.y1[q], self.y2[q], H, "y")
        ox = overlap(self.x1[p], self.x2[p], self.x1[q], self.x2[q], W, "x")
        j = m.NewIntVar(0, max(W, H), f"jlen_{tag}")
        m.Add(j == oy).OnlyEnforceIf(vx)
        m.Add(j == ox).OnlyEnforceIf(hy)
        m.Add(j == 0).OnlyEnforceIf([vx.Not(), hy.Not()])
        self.join_ints += 1
        return j

    # -- H4 / H5: per part, on the chosen plane; area at Room level ---------
    def _add_dimensions(self):
        m, b = self.m, self.brief
        W, H = self.env.W, self.env.H
        g, t = GRID_MM, self.cfg.t_int_mm
        band = t // 2
        if self.cfg.area_units != "mm_affine":
            raise ValueError("parts-plane runs the shipped rig only "
                             f"(mm_affine); got {self.cfg.area_units!r}")
        if not self.cfg.erode_minima or self.cfg.minima_are_clear_grid:
            raise ValueError("parts-plane runs the shipped rig only "
                             "(erode_minima on, minima_are_clear_grid off)")
        if t % 2:
            raise ValueError(f"t_int_mm {t} is odd; the band is t/2")
        if self.pc.parts_proposal is None:
            raise ValueError("parts-plane runs Design A only: presence is fixed "
                             "by the Proposal, per ADR 0014")

        self.faces = faces_by_coord(self.env)
        self._coords = {"v": sorted(k for k in self.faces if k[0] == "v"),
                        "h": sorted(k for k in self.faces if k[0] == "h")}
        self.area, self.area_mm2, self.mults = [], [], 0
        self.room_amm = {}
        self.join_len = {}
        k = b.max_aspect

        # Per part: the product H4 already builds, the clear dimensions, and the
        # part's own mm2 on the chosen plane.
        per_part = []
        for i, spec in enumerate(b.rooms):
            a = m.NewIntVar(0, W * H, f"a_{i}")
            m.AddMultiplicationEquality(a, [self.w[i], self.h[i]])
            self.mults += 1
            self.area.append(a)

            cw = m.NewIntVar(1, W * g, f"cw_{i}")
            ch = m.NewIntVar(1, H * g, f"ch_{i}")
            amm = m.NewIntVar(0, W * g * H * g, f"amm_{i}")

            if self.plane == "solver":
                m.Add(cw == self.w[i] * g - t)
                m.Add(ch == self.h[i] * g - t)
                m.Add(amm == g * g * a - g * t * (self.w[i] + self.h[i]) + t * t)
            else:
                cons = {nm: self._contact_side(i, nm, kd, fl, sp)
                        for (nm, kd, fl, sp) in SIDES}
                tot = 0
                for nm in ("W", "E", "S", "N"):
                    if cons[nm] is not None:
                        tot = tot + cons[nm]
                int_units = (2 * self.h[i] + 2 * self.w[i]) - tot
                m.Add(amm == g * g * a - band * g * int_units)
                nx = self._interior_side_count(i, ("W", "E"), cons)
                ny = self._interior_side_count(i, ("S", "N"), cons)
                m.Add(cw == self.w[i] * g - band * nx)
                m.Add(ch == self.h[i] * g - band * ny)

            self.area_mm2.append(amm)
            per_part.append(amm)

            # ADR 0014: clear dimensions and aspect bind PER CONSTITUENT
            # rectangle -- "each leg of an L must be usable" -- and the primary
            # carries the Room's minima while a secondary carries the universal
            # leg floor. That split is `build_part_brief`'s and is unchanged.
            on = self.pres.get(i)

            def add(c, on=on):
                m.Add(c) if on is None else m.Add(c).OnlyEnforceIf(on)

            add(cw >= spec.min_w * g)
            add(ch >= spec.min_h * g)
            add(cw <= k * ch)
            add(ch <= k * cw)
            if not self.room_area:
                # What `solver_parts` does today: the area floor on the PART,
                # which for a two-part Room means the PRIMARY, because
                # `build_part_brief` gives a secondary `min_area = 0`. Posted in
                # this loop and with this gating so arm A is that rig constraint
                # for constraint.
                add(amm >= spec.min_area * g * g)

        # Per Room: the union's mm2, and the area rules on it. The Room variable
        # is built only where a rule reads it, so `plane="solver",
        # room_area=False, caps=None` is `solver_parts` variable for variable.
        for r, ps in sorted(self.parts_of.items()):
            spec = self.room_brief.rooms[r]
            needs_room = self.room_area or (
                self.caps is not None and self.caps[r] is not None)
            if len(ps) > 1:
                self.two_part_rooms += 1

            amm_r = None
            if len(ps) == 1:
                amm_r = per_part[ps[0]]
            elif needs_room:
                p, q = ps[0], ps[1]
                expr = per_part[p] + per_part[q]
                if self.plane == "bar" and self.join:
                    j = self._join_len(p, q, f"{r}")
                    self.join_len[r] = j
                    expr = expr + JOIN_MM2_PER_UNIT * j
                amm_r = m.NewIntVar(0, 2 * W * g * H * g, f"ammR_{r}")
                m.Add(amm_r == expr)
            self.room_amm[r] = amm_r

            if self.room_area:
                m.Add(amm_r >= spec.min_area * g * g)

            if self.caps is not None and self.caps[r] is not None:
                m.Add(amm_r <= int(self.caps[r]))
                self.caps_posted += 1


def project_parts_plane(brief, proposal, cfg, pc: PartConfig, plane="bar",
                        join=True, room_area=True, caps=None) -> PartResult:
    """`solver_parts.project_parts`' signature plus the plane knobs."""
    p = BarPartsProjector(brief, proposal, cfg, pc, plane=plane, join=join,
                          room_area=room_area, caps=caps)
    out = p.solve()
    out.solve.model_stats["contact_lits"] = p.contact_lits
    out.solve.model_stats["contact_ints"] = p.contact_ints
    out.solve.model_stats["join_ints"] = p.join_ints
    out.solve.model_stats["caps_posted"] = p.caps_posted
    out.solve.model_stats["two_part_rooms"] = p.two_part_rooms
    out.solve.model_stats["build_ms"] = round(p.build_time * 1000, 2)
    return out
