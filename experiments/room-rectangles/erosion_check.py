"""ADR 0001's erosion, asserted rather than inherited, for a two-part Room.

ADR 0014 says ADR 0001 survives unchanged: `erode(polygon, t_int/2)` is still
exactly the region bounded by the finished inner faces of the surrounding walls,
reflex corner included. That is the single claim ADR 0014 makes about a closed
ADR, so it is checked here instead of asserted.

**All four shapes, since ADR 0045.** Two rectangles sharing an edge make an L, a
T, a Z or a plain rectangle, and 44,8 % of the converted index's two-part Rooms
are not an L. This file checked the L alone and closed `assert n == 6 and
reflex == 1`; three documents cite it by name -- ADR 0001, ADR 0014,
`annotation.md` 528 -- so a reader following the citation has to find the general
property here, not the special case.

Three properties, on integer millimetres, for EVERY shape:

  1. For a two-part Room, `erode(A U B, t/2)` is STRICTLY LARGER than
     `erode(A, t/2) U erode(B, t/2)` -- the band across the shared edge is
     interior to the union and survives. This is why `acceptance-bar.md` 9's
     old sliver argument is dead and why binding the minima per solved part is
     *conservative* rather than merely different.

     The degenerate rectangle is the one exception and it is instructive: two
     parts flush at BOTH ends erode to the same set as their union minus
     nothing, so the band is the whole shared edge and the gain is still
     positive -- but the union is a rectangle, which is why ADR 0045 decision 2
     normalises the encoding away rather than reasoning about it.

  2. `erode(shape, t/2)` equals the polygon bounded by the wall inner faces,
     where each wall is the centreline offset by t/2 -- INCLUDING at every
     reflex corner, which is the case ADR 0001 never had to consider. Checked
     pointwise, not merely in area, against a hand-built inner-face polygon per
     shape.

  3. The result is still a rectilinear polygon on integer millimetres with
     **at most two reflex corners and at most 8 vertices**. No rounding, no
     tolerance.

     ADR 0045 makes the vertex half of this a shipped conformance assertion:
     `ifc-export.md` check row 14 reads "at most 8 vertices", replacing an
     unsound "at most one reflex corner" that rejected 43 % of legitimate
     two-part Rooms. 4, 6 and 8 are the only counts two rectangles can produce;
     a third Part reaches 10.

Run: python experiments/room-rectangles/erosion_check.py
"""
from __future__ import annotations

from shapely.geometry import Polygon, box

T_INT = 150                      # ADR 0010
R = T_INT // 2                   # erosion radius; ADR 0004 keeps this integer


def erode(poly: Polygon, r: int) -> Polygon:
    """Erosion by a square of side 2r -- a mitred inward offset.

    `join_style=2` (mitre) is what keeps an axis-aligned polygon axis-aligned;
    the default round join would put an arc at every convex corner and the
    result would not be a rectilinear polygon at all.
    """
    return poly.buffer(-r, join_style=2, mitre_limit=10.0)


def l_room(w1, h1, w2, h2) -> tuple[Polygon, Polygon, Polygon]:
    """An L: a w1 x h1 leg with a w2 x h2 leg above its left end."""
    a = box(0, 0, w1, h1)
    b = box(0, h1, w2, h1 + h2)
    return a, b, a.union(b)


def close(x: float, y: float, tol: float = 1e-6) -> bool:
    return abs(x - y) <= tol


# --- the four shapes two Parts make ----------------------------------------
#
# Each entry is (parts, hand-built inner-face polygon, vertices, reflex). The
# inner-face polygon is written out by hand rather than derived, because
# deriving it from an offset would be assuming the identity property 2 exists
# to check. At a REFLEX corner the two inner faces meet at their intersection,
# which pushes the corner INTO the notch -- the case ADR 0001 never had to
# consider, and the reason this file exists.

def _shapes():
    # L -- flush at one end. 6 vertices, 1 reflex.
    la, lb = box(0, 0, 6000, 3000), box(0, 3000, 2500, 7000)
    l_faces = Polygon([
        (R, R), (6000 - R, R), (6000 - R, 3000 - R),
        (2500 - R, 3000 - R),                       # REFLEX
        (2500 - R, 7000 - R), (R, 7000 - R),
    ])

    # T -- one span strictly contains the other. 8 vertices, 2 reflex.
    ta, tb = box(0, 0, 6000, 3000), box(2000, 3000, 4000, 7000)
    t_faces = Polygon([
        (R, R), (6000 - R, R), (6000 - R, 3000 - R),
        (4000 - R, 3000 - R),                       # REFLEX
        (4000 - R, 7000 - R), (2000 + R, 7000 - R),
        (2000 + R, 3000 - R),                       # REFLEX
        (R, 3000 - R),
    ])

    # Z -- neither flush nor containing. 8 vertices, 2 reflex.
    za, zb = box(0, 0, 6000, 3000), box(3000, 3000, 9000, 7000)
    z_faces = Polygon([
        (R, R), (6000 - R, R),
        (6000 - R, 3000 + R),                       # REFLEX
        (9000 - R, 3000 + R), (9000 - R, 7000 - R),
        (3000 + R, 7000 - R),
        (3000 + R, 3000 - R),                       # REFLEX
        (R, 3000 - R),
    ])

    # rectangle -- flush at BOTH ends. 4 vertices, 0 reflex. ADR 0045 decision 2
    # normalises this away at the contract; it is checked because the corpus
    # contains 27 of them and the encoding was legal until that decision.
    ra, rb = box(0, 0, 6000, 3000), box(0, 3000, 6000, 7000)
    r_faces = Polygon([
        (R, R), (6000 - R, R), (6000 - R, 7000 - R), (R, 7000 - R),
    ])

    return [
        ("L",         (la, lb), l_faces, 6, 1),
        ("T",         (ta, tb), t_faces, 8, 2),
        ("Z",         (za, zb), z_faces, 8, 2),
        ("rectangle", (ra, rb), r_faces, 4, 0),
    ]


def rectilinear_stats(poly: Polygon) -> tuple[int, int]:
    """(vertices, reflex corners), asserting integer mm and axis-aligned edges."""
    cs = list(poly.exterior.coords)[:-1]
    for x, y in cs:
        assert close(x, round(x)) and close(y, round(y)), "integer millimetres"
    n = len(cs)
    reflex = 0
    for i in range(n):
        ax, ay = cs[i]
        bx, by = cs[(i + 1) % n]
        cx, cy = cs[(i + 2) % n]
        cross = (bx - ax) * (cy - by) - (by - ay) * (cx - bx)
        assert close((bx - ax) * (by - ay), 0.0), "axis-aligned edges only"
        if (cross > 0) != poly.exterior.is_ccw:
            reflex += 1
    return n, reflex


def main() -> None:
    print(f"ADR 0001's erosion at t_int = {T_INT}, on all four shapes two "
          f"Parts make (ADR 0045)\n")

    worst_n = 0
    for name, (a, b), faces, want_n, want_reflex in _shapes():
        u = a.union(b)

        # 1. the union's erosion keeps the band across the shared edge
        ea, eb, eu = erode(a, R), erode(b, R), erode(u, R)
        parts = ea.union(eb)
        assert eu.contains(parts.buffer(-1e-9)), \
            f"{name}: erode(A U B) must contain both"
        gain = eu.area - parts.area
        assert gain > 0, \
            f"{name}: the whole sliver argument turns on this being positive"

        # 2. against the inner-face polygon, built by hand from the centrelines
        assert close(eu.area, faces.area, 1.0), \
            f"{name}: ADR 0001's erosion identity"
        assert eu.symmetric_difference(faces).area < 1.0, \
            f"{name}: and pointwise, not just in area"

        # 3. still rectilinear, still integer, at most 2 reflex / 8 vertices
        n, reflex = rectilinear_stats(eu)
        assert (n, reflex) == (want_n, want_reflex), \
            f"{name}: expected {want_n} vertices / {want_reflex} reflex, " \
            f"got {n} / {reflex}"
        assert n <= 8 and reflex <= 2, \
            f"{name}: ifc-export.md row 14's bound is violated"
        worst_n = max(worst_n, n)

        print(f"{name:>9}: erode(A U B) - [erode(A) U erode(B)] = "
              f"{gain:>10,.0f} mm2 | identity holds pointwise | "
              f"{n} vertices, {reflex} reflex")

    print(f"\n   max vertices over all four shapes: {worst_n} "
          f"(ifc-export.md row 14 bounds at 8)")

    # 4. And the case that would break it: a leg thinner than the wall it is
    # made of erodes to nothing. The leg floor (900 mm clear) is what keeps this
    # unreachable, and it is why the floor is a hard predicate rather than
    # a preference.
    _, _, thin = l_room(6000, 3000, 100, 4000)
    et = erode(thin, R)
    print(f"\n4. a {100} mm leg erodes to area {et.area:,.0f} "
          f"(the L collapses to its main leg)")
    assert et.area < erode(box(0, 0, 6000, 3000), R).area + 1

    # 5. the room tag. `annotation.md` 7 placed it at the Space centroid on the
    #    stated grounds that no v1 Space is concave. For an L the Space centroid
    #    can land OUTSIDE the Space -- in the notch, which belongs to a
    #    different room -- so the tag would sit in the neighbour. The centroid of
    #    the LARGER part is inside by construction and needs no solver.
    deep = l_room(6000, 1200, 1200, 6000)[2]        # a thin, deep L
    c = deep.centroid
    inside = deep.contains(c)
    a2, b2, _ = l_room(6000, 1200, 1200, 6000)
    big = a2 if a2.area >= b2.area else b2
    print(f"5. L centroid ({c.x:,.0f}, {c.y:,.0f}) inside its own Space: {inside}")
    print(f"   larger part's centroid inside: {big.contains(big.centroid)}")
    assert not inside, "the case annotation.md 7 has to avoid"
    assert deep.contains(big.centroid), "and the rule that avoids it"

    # 6. the same rule at TWO reflex corners. Note what this does NOT show: a T
    #    at or above the leg floor keeps its centroid inside, because the union
    #    is y-connected over the bar's whole span. The escaping centroid is an
    #    L-shaped failure specifically. What is checked is that the larger-part
    #    rule is shape-agnostic -- it holds here too, so annotation.md 528 needs
    #    no shape case.
    ta, tb = box(0, 0, 6000, 1200), box(2400, 1200, 3600, 7200)
    t = ta.union(tb)
    tc = t.centroid
    tbig = ta if ta.area >= tb.area else tb
    print(f"6. T centroid ({tc.x:,.0f}, {tc.y:,.0f}) inside its own Space: "
          f"{t.contains(tc)}")
    print(f"   larger part's centroid inside: {t.contains(tbig.centroid)}")
    assert t.contains(tbig.centroid), "the larger-part rule is shape-agnostic"

    print("\nerosion_check: all assertions hold at t_int =", T_INT)


if __name__ == "__main__":
    main()
