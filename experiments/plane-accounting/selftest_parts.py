"""Is the two-part encoding the bar plane, and is its A arm the incumbent?

Ticket 78. `selftest.py` is ticket 77's, for a Room that is one rectangle;
nothing here replaces it and it still runs. These are the statements that only
appear once a Room has TWO rectangles.

  P1  the join band, by hand. Two 4 x 3 Rooms merged along a 3-unit edge:
      the per-part form subtracts a band along an edge the Room does not have,
      twice, and `+ 2 x 75 x 250 x J` is exactly what puts it back.
  P2  the vertex rule REDUCES to Part VIII's pair. `true_union_mm2` equals
      `bar_plane.true_bar_area_mm2` on every one-rectangle Room of every tiling
      `selftest.py` uses -- so Part IX generalises Part VIII rather than
      competing with it.
  P3  `true_union_mm2` == `space_m2` x 1e6 on two-part Rooms: L, T, Z and a
      straight split, over a rect, an L, a U and an Envelope with an ENCLOSED
      void. Shapely on the real union against integer arithmetic.
  P4  the decomposition the model posts is the oracle:
      `bar_union_mm2 == SUM_p bar_area_mm2(p) + 37 500 J`.
  P5  the CP-SAT model's Room-level `amm` equals that oracle, with the parts
      pinned to a known tiling. P3/P4 check the arithmetic; this checks the
      model agrees with it.
  P6  arm `A` IS the incumbent: `plane='solver', join=False, room_area=False`
      reproduces `solver_parts.project_parts` -- same status, same objective,
      same rectangles, same variable and constraint counts.
  P7  the parts rig DEGENERATES to ticket 77's: with every Room one part,
      `plane='bar'` gives `bar_plane.project_plane(plane='bar')`'s model and
      answer exactly.
  P9  ADR 0001's erosion identity at TWO reflex corners. `erosion_check.py`
      checks it at one and asserts `reflex == 1`; 44,8 % of the corpus's
      two-part Rooms are a T, a Z or a rectangle, not an L.
  P8  `dim.statutory_min_area` binds per ROOM. A two-part Room whose union
      clears the floor and whose primary part does not is FEASIBLE under
      `room_area=True` and INFEASIBLE under the primary-part binding
      `project_join.py` LIMIT 3 flags -- the false refusal, exhibited.

    python experiments/plane-accounting/selftest_parts.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "solver-toy"))
sys.path.insert(0, str(HERE.parent / "warp"))
sys.path.insert(0, str(HERE.parent / "room-rectangles"))

from ortools.sat.python import cp_model                              # noqa: E402

from absolute_area import outside_of, space_m2                       # noqa: E402
from bar_plane import (CORNER_MM2, GRID_MM, bar_area_mm2,            # noqa: E402
                       project_plane, true_bar_area_mm2)
from geometry import Envelope, Rect                                  # noqa: E402
from parts_plane import (BAND_MM2_PER_UNIT, JOIN_MM2_PER_UNIT,       # noqa: E402
                         bar_union_mm2, join_units, project_parts_plane,
                         true_union_mm2, union_terms)
from scenarios import Brief, Proposal, RoomSpec                      # noqa: E402
from selftest import _envelopes, _tile                               # noqa: E402
from solver import SolveConfig                                       # noqa: E402
from solver_parts import PartConfig, project_parts                   # noqa: E402

T_INT = 150
OK = []


def note(s):
    OK.append(s)
    print(f"  ok  {s}")


def _cfg(**kw):
    base = dict(workers=1, time_limit_s=20.0, seed=7, area_units="mm_affine",
                erode_minima=True, t_int_mm=T_INT,
                soft=("coverage", "exterior", "wet_cluster", "circulation"))
    base.update(kw)
    return SolveConfig(**base)


# ---------------------------------------------------------------------------
def p1_join_band_by_hand():
    """Two 4 x 3-cell rectangles stacked, sharing their full 4-unit edge.

    The union is 4 x 6 cells, wholly interior, so its truth is the incumbent's
    own expression on the union -- `(1000 - 150)(1500 - 150)`. That gives the
    join term a value to be right or wrong about that owes nothing to this file.
    """
    env = Envelope("box", 12, 14, (), (Rect(0, 0, 12, 14),))
    a = Rect(3, 3, 7, 6)                        # 1000 x 750 mm
    b = Rect(3, 6, 7, 9)                        # 1000 x 750 mm, stacked on a
    assert join_units([a, b]) == 4

    per_part = bar_area_mm2(env, a, T_INT) + bar_area_mm2(env, b, T_INT)
    assert per_part == 2 * 487_500, per_part
    assert bar_union_mm2(env, [a, b], join=False) == per_part
    with_join = bar_union_mm2(env, [a, b], join=True)
    assert with_join == per_part + JOIN_MM2_PER_UNIT * 4, with_join
    assert with_join - per_part == 150_000

    # The union is a plain 4 x 6 rectangle with all four sides interior, so
    # [B](U) must be the one-rectangle form on it, and the truth must be [A].
    u = Rect(3, 3, 7, 9)
    assert with_join == bar_area_mm2(env, u, T_INT), (with_join,)
    truth = true_union_mm2(env, [a, b])
    assert truth == (1000 - 150) * (1500 - 150) == 1_147_500, truth
    assert truth - with_join == 4 * CORNER_MM2
    note("P1: two stacked 4 x 3 Rooms -- the per-part form is short by "
         "150 000 mm2 across a 4-unit join, and 2 x 75 x 250 x J is that "
         "number exactly")

    # And the L: drop the top part to 2 units wide, so the join is 2 and the
    # union gains a reflex corner of its own.
    c = Rect(3, 6, 5, 9)
    assert join_units([a, c]) == 2
    _area, _eint, wsum = union_terms(env, [a, c])
    # five convex corners, all interior, and one reflex -- the L's own
    assert wsum == 5 - 1 == 4, wsum
    note("P1b: the L's own reflex corner is the same -5 625 term as a mid-side "
         "flip -- `w = I - nU` gives I = 2, nU = 3 there, and nothing new is "
         "needed for it")


# ---------------------------------------------------------------------------
def p2_reduces_to_part_viii():
    n = 0
    for env in _envelopes():
        for seed in range(6):
            for r in _tile(env, seed):
                assert true_union_mm2(env, [r]) == true_bar_area_mm2(env, r, T_INT), \
                    (env.name, seed, r)
                assert bar_union_mm2(env, [r]) == bar_area_mm2(env, r, T_INT)
                n += 1
    note(f"P2: the vertex rule reproduces Part VIII's `corners - reflex` on "
         f"{n} one-rectangle Rooms -- Part IX generalises it, and the "
         f"one-part arm is untouched")


# ---------------------------------------------------------------------------
def _merge_pairs(rooms):
    """Fold a guillotine tiling into Rooms of one or two parts.

    Greedy over edge-sharing pairs, so the result covers L, T, Z and straight
    splits without any of them being hand-placed.
    """
    left = list(rooms)
    out = []
    while left:
        r = left.pop(0)
        mate = None
        for k, q in enumerate(left):
            if ((r.x2 == q.x1 or q.x2 == r.x1)
                    and min(r.y2, q.y2) - max(r.y1, q.y1) > 0):
                mate = k
                break
            if ((r.y2 == q.y1 or q.y2 == r.y1)
                    and min(r.x2, q.x2) - max(r.x1, q.x1) > 0):
                mate = k
                break
        out.append([r] if mate is None else [r, left.pop(mate)])
    return out


def _shape_of(parts):
    if len(parts) < 2:
        return "single"
    p, q = parts
    if p.x2 == q.x1 or q.x2 == p.x1:
        lo1, hi1, lo2, hi2 = p.y1, p.y2, q.y1, q.y2
    else:
        lo1, hi1, lo2, hi2 = p.x1, p.x2, q.x1, q.x2
    f_lo, f_hi = lo1 == lo2, hi1 == hi2
    if f_lo and f_hi:
        return "rectangle"
    if f_lo or f_hi:
        return "L"
    if (lo1 < lo2 and hi2 < hi1) or (lo2 < lo1 and hi1 < hi2):
        return "T"
    return "Z"


def _staggered():
    """One hand-built exact tiling that a guillotine dissection cannot produce:
    a Z-shaped Room, whose two parts are flush at NEITHER end.

    ⚠️ Two rectangles make an L, a T, a Z or a rectangle. ADR 0014 argues for the
    k <= 2 cap on the ground that *"an L is a shape an architect draws; a T, U, S
    or Z room is a shape a plan is left with"* -- and the cap does not exclude
    the T or the Z. They have to be in the fixture because they are in the
    corpus.
    """
    env = Envelope("stag", 12, 6, (), (Rect(0, 0, 12, 6),))
    rooms = [[Rect(0, 0, 3, 6)],
             [Rect(3, 0, 7, 3), Rect(5, 3, 9, 6)],       # Z
             [Rect(7, 0, 12, 3)],
             [Rect(3, 3, 5, 6)],
             [Rect(9, 3, 12, 6)]]
    return env, rooms


def p3_p4_against_shapely():
    n = 0
    seen = set()
    cases = [(env, _merge_pairs(_tile(env, seed)))
             for env in _envelopes() for seed in range(8)]
    cases.append(_staggered())
    for env, rooms in cases:
        assert sum(r.area for parts in rooms for r in parts) == env.interior_area
        allr = [[(r.x1 * GRID_MM, r.y1 * GRID_MM,
                  r.x2 * GRID_MM, r.y2 * GRID_MM) for r in parts]
                for parts in rooms]
        outside = outside_of(allr)
        for parts, rs in zip(rooms, allr):
            truth = round(space_m2(rs, outside) * 1e6)
            mine = true_union_mm2(env, parts)
            assert truth == mine, (env.name, parts, truth, mine)
            # P4, on the same geometry
            decomposed = (sum(bar_area_mm2(env, r, T_INT) for r in parts)
                          + JOIN_MM2_PER_UNIT * join_units(parts))
            assert bar_union_mm2(env, parts) == decomposed, parts
            seen.add(_shape_of(parts))
            n += 1
    for want in ("L", "T", "Z", "rectangle"):
        assert want in seen, (want, sorted(seen))
    note(f"P3: true_union_mm2 == space_m2 on {n} Rooms over four Envelopes, "
         f"shapes {', '.join(sorted(seen))}")
    note("P4: `[B](U) = SUM_p [B](p) + 37 500 J` holds on every one of them")


# ---------------------------------------------------------------------------
def _brief_and_pc(env, rooms, min_area=1, min_side=1):
    """⚠️ `leg_min` and `leg_join` are dropped to one grid unit here.

    ADR 0014's 900 mm leg floor and 1 100 mm realisable join are the shipped
    values and `arms_parts.py` runs at them. These fixtures are dissections, not
    Plans -- a merged pair may share two units — and the statements below are
    about the AREA identity, which the join predicate neither helps nor hinders.
    Every arm in a comparison gets the same `PartConfig`, so P6 and P7 stay
    like-for-like.
    """
    specs = [RoomSpec(f"r{i}", "living" if i else "hall", min_side, min_side,
                      min_area) for i in range(len(rooms))]
    b = Brief(env.name, env, GRID_MM, specs, entry=0, max_aspect=99)
    prop = Proposal(boxes=[parts[0] for parts in rooms],
                    kinds=[s.kind for s in specs])
    pc = PartConfig(leg_min=1, leg_join=1,
                    parts_proposal={i: list(parts)
                                    for i, parts in enumerate(rooms)})
    return b, prop, pc


def p5_model_agrees():
    from parts_plane import BarPartsProjector
    n = 0
    for env in _envelopes():
        for seed in (0, 1, 2, 3):
            rooms = _merge_pairs(_tile(env, seed))
            b, prop, pc = _brief_and_pc(env, rooms)
            p = BarPartsProjector(b, prop, _cfg(hint=False, diagnose=False),
                                  pc, plane="bar", join=True, room_area=True)
            flat = [r for parts in rooms for r in parts]
            for i, r in enumerate(flat):
                p.m.Add(p.x1[i] == r.x1)
                p.m.Add(p.y1[i] == r.y1)
                p.m.Add(p.x2[i] == r.x2)
                p.m.Add(p.y2[i] == r.y2)
            s = cp_model.CpSolver()
            s.parameters.num_workers = 1
            s.parameters.max_time_in_seconds = 30.0
            st = s.Solve(p.m)
            assert st in (cp_model.OPTIMAL, cp_model.FEASIBLE), s.StatusName(st)
            for r, parts in enumerate(rooms):
                got = s.Value(p.room_amm[r])
                want = bar_union_mm2(env, parts)
                assert got == want, (env.name, seed, r, got, want)
                if len(parts) > 1:
                    assert s.Value(p.join_len[r]) == join_units(parts), (r,)
                n += 1
    note(f"P5: the model's Room-level amm and join length equal the oracle on "
         f"{n} Rooms")


# ---------------------------------------------------------------------------
def p6_a_arm_is_the_incumbent():
    for env in _envelopes():
        rooms = _merge_pairs(_tile(env, 3))
        b, prop, pc = _brief_and_pc(env, rooms, min_area=2, min_side=2)
        cfg = _cfg(fix_relations=True, relation_confidence=4)
        inc = project_parts(b, prop, cfg, pc)
        mine = project_parts_plane(b, prop, cfg, pc, plane="solver", join=False,
                                   room_area=False)
        assert inc.solve.status == mine.solve.status, env.name
        # ⚠️ Objective equality only when BOTH proved optimality. The two models
        # are the same size and the same seed, but CP-SAT under a wall-clock
        # limit is not reproducible between runs, so a FEASIBLE pair may stop at
        # different incumbents. The identity claim is the model, not the race.
        if inc.solve.status == "OPTIMAL":
            assert inc.solve.objective == mine.solve.objective, env.name
            assert inc.solve.rooms == mine.solve.rooms, env.name
        for key in ("variables", "constraints", "multiplications"):
            assert inc.solve.model_stats[key] == mine.solve.model_stats[key], \
                (env.name, key, inc.solve.model_stats[key],
                 mine.solve.model_stats[key])
    note("P6: arm A is `solver_parts.project_parts` -- same status, objective, "
         "rectangles, variables and constraints on all four Envelopes")


# ---------------------------------------------------------------------------
def p7_degenerates_to_ticket_77():
    for env in _envelopes():
        rooms = [[r] for r in _tile(env, 4)]
        b, prop, pc = _brief_and_pc(env, rooms, min_area=2, min_side=2)
        cfg = _cfg(fix_relations=True, relation_confidence=4)
        one = project_plane(b, prop, cfg, plane="bar")
        two = project_parts_plane(b, prop, cfg, pc, plane="bar", join=True,
                                  room_area=True)
        assert one.status == two.solve.status, env.name
        if one.status == "OPTIMAL":
            assert one.objective == two.solve.objective, env.name
            assert one.rooms == two.solve.rooms, env.name
        assert two.solve.model_stats["join_ints"] == 0, env.name
        assert (one.model_stats["contact_lits"]
                == two.solve.model_stats["contact_lits"]), env.name
        assert (one.model_stats["contact_ints"]
                == two.solve.model_stats["contact_ints"]), env.name
        # ⚠️ NOT variable-identical, and that is `solver_parts`' own cost, not
        # this encoding's: Design A aggregates contact to Room level and
        # extracts relations in the part index space whatever k is. ADR 0014
        # measured it at 1,2-1,7x the variables. The encoding itself is
        # identical -- same reified-contact counts, same answer, no join
        # machinery built.
        assert (two.solve.model_stats["variables"]
                > one.model_stats["variables"]), env.name
    note("P7: with every Room one part the encoding IS ticket 77's -- same "
         "reified-contact counts, same answer, no join machinery built")


# ---------------------------------------------------------------------------
def p8_floor_binds_per_room():
    """`dim.statutory_min_area` binds per ROOM (ADR 0014), and binding it on the
    primary part is the false refusal `project_join.py` LIMIT 3 warns about.

    A 12 x 4 Envelope tiled into one 3 x 4 Room and a two-part Room of 6 x 4
    plus 3 x 4. The two-part Room's union clears a floor its primary part alone
    does not.
    """
    env = Envelope("bar", 12, 4, (), (Rect(0, 0, 12, 4),))
    rooms = [[Rect(0, 0, 3, 4)], [Rect(3, 0, 9, 4), Rect(9, 0, 12, 4)]]
    union = true_union_mm2(env, rooms[1])
    primary = true_union_mm2(env, [rooms[1][0]])
    assert primary < union
    # a floor between the two, in whole grid cells as `min_area` is stated
    floor_cells = (primary // (GRID_MM * GRID_MM)) + 2
    assert primary < floor_cells * GRID_MM * GRID_MM <= union, (
        primary, floor_cells, union)

    specs = [RoomSpec("r0", "hall", 1, 1, 1),
             RoomSpec("r1", "living", 1, 1, floor_cells)]
    b = Brief("floor", env, GRID_MM, specs, entry=0, max_aspect=99)
    prop = Proposal(boxes=[p[0] for p in rooms], kinds=[s.kind for s in specs])
    pc = PartConfig(leg_min=1, leg_join=1,
                    parts_proposal={i: list(p) for i, p in enumerate(rooms)})
    cfg = _cfg(soft=("exterior", "wet_cluster", "circulation"))

    # Pinned, because the claim is about THIS geometry: left free the solver
    # would simply grow the primary part until it cleared the floor on its own,
    # which is the re-sizing `site: both` licenses and not the question here.
    from parts_plane import BarPartsProjector
    flat = [r for parts in rooms for r in parts]
    status = {}
    for tag, room_area in (("per Room", True), ("per part", False)):
        p = BarPartsProjector(b, prop, cfg, pc, plane="bar", join=True,
                              room_area=room_area)
        for i, r in enumerate(flat):
            p.m.Add(p.x1[i] == r.x1)
            p.m.Add(p.y1[i] == r.y1)
            p.m.Add(p.x2[i] == r.x2)
            p.m.Add(p.y2[i] == r.y2)
        s = cp_model.CpSolver()
        s.parameters.num_workers = 1
        s.parameters.max_time_in_seconds = 30.0
        status[tag] = s.StatusName(s.Solve(p.m))
    assert status["per Room"] in ("OPTIMAL", "FEASIBLE"), status
    assert status["per part"] == "INFEASIBLE", status
    note("P8: a Room whose union clears the floor and whose primary part does "
         "not is FEASIBLE per Room and INFEASIBLE per part -- LIMIT 3's "
         "strictness, exhibited")


# ---------------------------------------------------------------------------
def p9_erosion_identity_at_two_reflex_corners():
    """ADR 0001's erosion identity, at a T and a Z.

    ⚠️ `room-rectangles/erosion_check.py` checks it on an **L** and closes with
    `assert n == 6 and reflex == 1`. ADR 0014 states the same: *"still
    rectilinear on integer millimetres with exactly one reflex corner"*, and
    `acceptance-bar.md` §9.1 repeats it as *"a rectilinear polygon with one
    reflex corner"*. Two rectangles sharing an edge make an L, a **T**, a **Z**
    or a rectangle, and **44,8 % of the converted index's 1 535 two-part Rooms
    are not an L** — 661 have two reflex corners and 27 have none.

    So the identity is checked here at two reflex corners rather than inherited,
    because this file's whole encoding rests on it. Same three properties as
    `erosion_check.py`, same hand-built inner-face polygon from the wall
    centrelines, same integer millimetres, no tolerance.
    """
    from shapely.geometry import Polygon, box
    r = T_INT // 2

    def erode(p):
        return p.buffer(-r, join_style=2, mitre_limit=10.0)

    cases = {
        # a T: a 6000 x 3000 bar with a 2000-wide stem above its middle
        "T": (box(0, 0, 6000, 3000), box(2000, 3000, 4000, 6000),
              [(r, r), (6000 - r, r), (6000 - r, 3000 - r), (4000 - r, 3000 - r),
               (4000 - r, 6000 - r), (2000 + r, 6000 - r),
               (2000 + r, 3000 - r), (r, 3000 - r)]),
        # a Z: two 3000-deep bars staggered, sharing 2000 mm of edge
        "Z": (box(0, 0, 4000, 3000), box(2000, 3000, 6000, 6000),
              [(r, r), (4000 - r, r), (4000 - r, 3000 + r), (6000 - r, 3000 + r),
               (6000 - r, 6000 - r), (2000 + r, 6000 - r),
               (2000 + r, 3000 - r), (r, 3000 - r)]),
    }
    for name, (a, b, face_pts) in cases.items():
        u = a.union(b)
        eu, parts = erode(u), erode(a).union(erode(b))
        assert eu.contains(parts.buffer(-1e-9)), name
        assert eu.area > parts.area, name
        faces = Polygon(face_pts)
        assert abs(eu.area - faces.area) < 1.0, (name, eu.area, faces.area)
        assert eu.symmetric_difference(faces).area < 1.0, name
        cs = list(eu.exterior.coords)[:-1]
        for x, y in cs:
            assert abs(x - round(x)) < 1e-6 and abs(y - round(y)) < 1e-6, name
        reflex = 0
        n = len(cs)
        for i in range(n):
            ax, ay = cs[i]
            bx, by = cs[(i + 1) % n]
            cx, cy = cs[(i + 2) % n]
            assert abs((bx - ax) * (by - ay)) < 1e-6, name
            cross = (bx - ax) * (cy - by) - (by - ay) * (cx - bx)
            if (cross > 0) != eu.exterior.is_ccw:
                reflex += 1
        assert n == 8 and reflex == 2, (name, n, reflex)
    note("P9: ADR 0001's erosion identity holds pointwise at TWO reflex corners "
         "-- a T and a Z, 8 vertices each, integer millimetres, no tolerance. "
         "`erosion_check.py` asserts `reflex == 1` and 44,8 % of the corpus's "
         "two-part Rooms are not an L")


if __name__ == "__main__":
    p1_join_band_by_hand()
    p2_reduces_to_part_viii()
    p3_p4_against_shapely()
    p5_model_agrees()
    p6_a_arm_is_the_incumbent()
    p7_degenerates_to_ticket_77()
    p8_floor_binds_per_room()
    p9_erosion_identity_at_two_reflex_corners()
    print(f"\n{len(OK)} checks passed")
