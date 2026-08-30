"""Solved grid rectangles -> a `Plan` on the clear plane, plus its wall bodies.

THE ONE CONVERSION, AND IT IS ADR 0001's EROSION READ FORWARDS.

A grid line `c` in the solve domain is a wall, and its two finished faces are

    low-side face   = GRID * c - t_int          (bounds the room below/left)
    high-side face  = GRID * c                  (bounds the room above/right)

so a solved rectangle `[u1, u2]` becomes a clear `[GRID*u1, GRID*u2 - t_int]`
and the Envelope's `W` cells become an inner `GRID*W - t_int`. At grid 250 and
t_int 150 that is annotation.md section 14's arithmetic exactly, which is the
check that this file is not inventing a plane of its own.

`src/` may not import `experiments/`, so this module takes plain tuples. The
harness that owns the solver is what unpacks its objects.
"""
from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Tuple

from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

from . import profile
from .model import Face, Plan, RectMM, Space

GRID = profile.GRID_MM
T_INT = profile.T_INT_MM


# ---------------------------------------------------------------------------
# The conversion
# ---------------------------------------------------------------------------
def clear_lo(u: int) -> int:
    """The finished face on the HIGH side of grid line `u`."""
    return GRID * u


def clear_hi(u: int) -> int:
    """The finished face on the LOW side of grid line `u`."""
    return GRID * u - T_INT


def clear_rect(g: Sequence[int]) -> RectMM:
    x1, y1, x2, y2 = g
    return RectMM(clear_lo(x1), clear_lo(y1), clear_hi(x2), clear_hi(y2))


def grid_line_of(c_mm: int) -> Tuple[int, str]:
    """Inverse: which grid line a clear face sits on, and which side of it."""
    if c_mm % GRID == 0:
        return c_mm // GRID, "high"
    if (c_mm + T_INT) % GRID == 0:
        return (c_mm + T_INT) // GRID, "low"
    raise ValueError("%s is not a finished face on the %s/%s plane"
                     % (c_mm, GRID, T_INT))


def grid_bound(c_mm: int) -> int:
    """The grid line a clear coordinate is bounded by, either side."""
    return grid_line_of(c_mm)[0]


def clear_notch(g: Sequence[int]) -> RectMM:
    """A notch is the complement of interior, so it sits on the other side of
    the same grid lines: it grows by t_int/2 a side where a room shrinks."""
    x1, y1, x2, y2 = g
    return RectMM(clear_hi(x1), clear_hi(y1), clear_lo(x2), clear_lo(y2))


# ---------------------------------------------------------------------------
# Plan assembly
# ---------------------------------------------------------------------------
def make_plan(name: str,
              W: int, H: int,
              notches: Iterable[Sequence[int]],
              grid_faces: Iterable[Tuple[str, int, int, int, bool]],
              room_parts: Sequence[Sequence[Sequence[int]]],
              corpus_labels: Sequence[str],
              erg_keys: Sequence[str],
              entrance_side: str,
              provenance: Optional[dict] = None) -> Plan:
    """Every argument is in GRID units except `entrance_side`.

    `grid_faces` is `Envelope.all_faces()` -- (axis, coord, lo, hi, is_exterior).
    `room_parts[i]` is that Room's one or two rectangles (ADR 0014).
    """
    spaces: List[Space] = []
    for i, (parts, lab, key) in enumerate(zip(room_parts, corpus_labels, erg_keys)):
        spaces.append(Space(ref="R%02d" % (i + 1), key=key, corpus_label=lab,
                            parts=[clear_rect(p) for p in parts]))

    inner = RectMM(clear_lo(0), clear_lo(0), clear_hi(W), clear_hi(H))
    plan = Plan(name=name, spaces=spaces, faces=[], inner=inner,
                entrance_side=entrance_side,
                notches=[clear_notch(n) for n in notches],
                provenance=provenance or {})
    plan.faces = _faces_to_mm(grid_faces, W, H, plan)
    return plan


def _faces_to_mm(grid_faces, W: int, H: int, plan: Plan) -> List[Face]:
    """Type each Envelope boundary face and put it on the clear plane.

    A face's `outward` -- which side the wall body lies on -- is read off the
    geometry rather than assumed: a notch face on a bbox line and one that is
    not are the same object to `all_faces()` and are not the same object here.
    """
    interior = plan.interior_poly()
    out: List[Face] = []
    for (axis, c, lo, hi, is_ext) in grid_faces:
        if axis == "v":
            side = "W" if c == 0 else ("E" if c == W else None)
        else:
            side = "S" if c == 0 else ("N" if c == H else None)

        if side in ("W", "S"):
            outward, coord = -1, clear_lo(c)
        elif side in ("E", "N"):
            outward, coord = +1, clear_hi(c)
        else:
            outward, coord = _notch_side(axis, c, lo, hi, interior)

        out.append(Face(axis=axis, coord=int(coord),
                        lo=clear_lo(lo), hi=clear_hi(hi),
                        outward=outward, is_exterior=bool(is_ext), side=side))
    return out


def _notch_side(axis: str, c: int, lo: int, hi: int, interior):
    """Which side of a notch face the dwelling is on, settled geometrically so
    that an L, a U and an enclosed void all resolve without a case each."""
    mid = (clear_lo(lo) + clear_hi(hi)) / 2.0
    for outward, coord in ((-1, clear_lo(c)), (+1, clear_hi(c))):
        inside = coord - outward * 1.0
        p = Point(inside, mid) if axis == "v" else Point(mid, inside)
        if interior.contains(p):
            return outward, coord
    return +1, clear_hi(c)


# ---------------------------------------------------------------------------
# Wall bodies
# ---------------------------------------------------------------------------
def interior_polygon(plan: Plan):
    """The Envelope's inner-face ring, as one polygon on the clear plane."""
    return plan.interior_poly()


def partition_region(plan: Plan):
    """Interior minus the Spaces. Every internal wall body, and nothing else.

    Note what is NOT here: the edge where a two-rectangle Room's legs meet.
    Nothing separates a Room from itself, so no Wall exists there (CONTEXT,
    *Wall segment*) -- and a derivation that walked part boundaries would draw a
    partition inside a room. annotation.md section 13 says the same thing from
    the other end.
    """
    return interior_polygon(plan).difference(
        unary_union([s.as_poly() for s in plan.spaces]))


def _orient_ccw(ring_coords):
    a = 0.0
    for (x1, y1), (x2, y2) in zip(ring_coords, ring_coords[1:]):
        a += x1 * y2 - x2 * y1
    return list(ring_coords) if a > 0 else list(ring_coords)[::-1]


def _thickness_at(plan: Plan, axis: str, coord: float, lo: float, hi: float) -> int:
    """Which Envelope face a ring edge belongs to, and how thick it is.

    Falls back to the PARTY thickness, not the exterior one: over-drawing a
    500 mm wall where the model holds a 280 mm one would put the sheet's
    footprint outside the model's, and `check.measurement_matches_model` would
    then be asserting a number nothing else believes.
    """
    mid = (lo + hi) / 2.0
    best = None
    for f in plan.faces:
        if f.axis != axis or abs(f.coord - coord) > 1e-6:
            continue
        if f.lo - 1e-6 <= mid <= f.hi + 1e-6:
            return f.thickness
        if best is None and min(f.hi, hi) - max(f.lo, lo) > 0:
            best = f.thickness
    return best if best is not None else profile.T_PARTY_MM


def _offset_ring(plan: Plan, coords, outward: bool):
    coords = _orient_ccw(coords)
    if not outward:
        coords = coords[::-1]
    n = len(coords) - 1
    lines = []
    for i in range(n):
        (x1, y1), (x2, y2) = coords[i], coords[i + 1]
        if abs(y1 - y2) < 1e-9:
            t = _thickness_at(plan, "h", y1, min(x1, x2), max(x1, x2))
            lines.append(("h", y1 + (-t if x2 > x1 else t)))
        else:
            t = _thickness_at(plan, "v", x1, min(y1, y2), max(y1, y2))
            lines.append(("v", x1 + (t if y2 > y1 else -t)))
    out = []
    for i in range(n):
        a, b = lines[i - 1], lines[i]
        x = b[1] if b[0] == "v" else a[1]
        y = b[1] if b[0] == "h" else a[1]
        out.append((x, y))
    out.append(out[0])
    return out


def envelope_ring(plan: Plan):
    """The Envelope's wall bodies, each edge offset by ITS OWN thickness.

    A uniform buffer cannot draw this: an exterior wall is 500 and a party wall
    280 in the shipped profile, and the corner between them is 500 x 280. So the
    ring is built by offsetting each rectilinear edge on its own and intersecting
    consecutive offsets -- variable offset, exact for an axis-aligned ring.
    """
    interior = interior_polygon(plan)
    geoms = [interior] if interior.geom_type == "Polygon" else list(interior.geoms)
    pieces = []
    for g in geoms:
        outer = _offset_ring(plan, list(g.exterior.coords), outward=True)
        holes = [_offset_ring(plan, list(r.coords), outward=False)
                 for r in g.interiors]
        pieces.append(Polygon(outer, holes))
    return unary_union(pieces).difference(interior)


def wall_region(plan: Plan):
    """Everything the cutting plane passes through, openings subtracted.

    Poche fills this and the 0.50 linework traces its boundary -- annotation.md
    section 2. Subtracting the openings here rather than drawing over them
    afterwards is what makes a reveal a real edge instead of a white rectangle
    laid on top.
    """
    solid = unary_union([partition_region(plan), envelope_ring(plan)])
    if plan.openings:
        voids = unary_union([o.rect().as_poly() for o in plan.openings])
        solid = solid.difference(voids)
    return solid


def footprint(plan: Plan):
    """Interior plus wall bodies -- what tier 1 measures on an exterior edge."""
    return unary_union([interior_polygon(plan), envelope_ring(plan)])
