"""ADR 0001's erosion, asserted rather than inherited, for a two-part Room.

ADR 0014 says ADR 0001 survives unchanged: `erode(polygon, t_int/2)` is still
exactly the region bounded by the finished inner faces of the surrounding walls,
reflex corner included. That is the single claim ADR 0014 makes about a closed
ADR, so it is checked here instead of asserted.

Three properties, on integer millimetres:

  1. For a two-part Room, `erode(A U B, t/2)` is STRICTLY LARGER than
     `erode(A, t/2) U erode(B, t/2)` -- the band across the shared edge is
     interior to the union and survives. This is why `acceptance-bar.md` 9's
     old sliver argument is dead and why binding the minima per solved part is
     *conservative* rather than merely different.

  2. `erode(L, t/2)` equals the polygon bounded by the wall inner faces, where
     each wall is the centreline offset by t/2 -- INCLUDING at the reflex
     corner, which is the case ADR 0001 never had to consider.

  3. The result is still a rectilinear polygon on integer millimetres with
     exactly one reflex corner. No rounding, no tolerance.

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


def main() -> None:
    a, b, l = l_room(6000, 3000, 2500, 4000)
    assert close(l.area, 6000 * 3000 + 2500 * 4000)

    # 1. the union's erosion keeps the band across the shared edge
    ea, eb, el = erode(a, R), erode(b, R), erode(l, R)
    parts = ea.union(eb)
    assert el.contains(parts.buffer(-1e-9)), "erode(A U B) must contain both"
    gain = el.area - parts.area
    band = (min(a.bounds[2], b.bounds[2]) - max(a.bounds[0], b.bounds[0])
            - 2 * R) * (2 * R)
    print(f"1. erode(A U B) - [erode(A) U erode(B)] = {gain:,.0f} mm2")
    print(f"   the shared-edge band alone is       {band:,.0f} mm2")
    assert gain > 0, "the whole sliver argument turns on this being positive"

    # 2. against the inner-face polygon, built by hand from the wall centrelines
    #    The L's boundary is 6 edges; every wall inner face is its centreline
    #    offset by R into the room. At the REFLEX corner the two faces meet
    #    diagonally outward, which is the case ADR 0001 never had to consider.
    faces = Polygon([
        (R, R),                                   # convex
        (6000 - R, R),                            # convex
        (6000 - R, 3000 - R),                     # convex
        (2500 - R, 3000 - R),                     # REFLEX: pushed +x, -y
        (2500 - R, 3000 + 4000 - R),              # convex
        (R, 3000 + 4000 - R),                     # convex
    ])
    print(f"2. erode(L, t/2) area      {el.area:,.0f} mm2")
    print(f"   inner-face polygon area {faces.area:,.0f} mm2")
    assert close(el.area, faces.area, 1.0), "ADR 0001's erosion identity"
    assert el.symmetric_difference(faces).area < 1.0, "and pointwise, not just in area"

    # 3. still rectilinear, still integer, exactly one reflex corner
    cs = list(el.exterior.coords)[:-1]
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
        if (cross > 0) != el.exterior.is_ccw:
            reflex += 1
    print(f"3. vertices {n}, reflex corners {reflex}")
    assert n == 6 and reflex == 1

    # And the case that would break it: a leg thinner than the wall it is made
    # of erodes to nothing. The leg floor (900 mm clear) is what keeps this
    # unreachable, and it is why the floor is a hard predicate rather than
    # a preference.
    _, _, thin = l_room(6000, 3000, 100, 4000)
    et = erode(thin, R)
    print(f"4. a {100} mm leg erodes to area {et.area:,.0f} "
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

    print("\nerosion_check: all assertions hold at t_int =", T_INT)


if __name__ == "__main__":
    main()
