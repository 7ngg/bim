"""Is ADR 0039's encoding the bar plane? Asserted three ways before any timing.

Ticket 77. Part VII is *"a derivation and two hand-checks"* and everything this
directory reports rests on the encoding actually computing the area
`absolute_area.space_m2` computes. Three independent statements, each an assert:

  T1  the two hand-checks in Part VII / ADR 0039 decision 5 reproduce exactly.
  T2  `true_bar_area_mm2` == `space_m2` x 1e6, per Room, over tilings of a
      rectangle, an L, a U and an Envelope with an ENCLOSED void -- shapely
      against integer arithmetic, on ADR 0001's construction.
  T3  the CP-SAT model's `amm_i`, read out with the Rooms pinned to a known
      tiling, equals the same integer. This is the one that matters: T2 checks
      the oracle, T3 checks that the model agrees with the oracle.

  T4  `plane="solver"` reproduces `solver.py` -- same status, same objective, on
      the same Brief. The A arm has to BE the incumbent, not a rebuild of it.
  T5  `project_join.py` LIMIT 2's min-side identity, restated at 0, 1 and 2
      interior sides, because the bar plane relaxes the width floor by one grid
      unit for a Room spanning the Envelope and that has to be deliberate.

    python experiments/plane-accounting/selftest.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "solver-toy"))
sys.path.insert(0, str(HERE.parent / "warp"))

from ortools.sat.python import cp_model                              # noqa: E402

from bar_plane import (CORNER_MM2, GRID_MM, BarPlaneProjector,       # noqa: E402
                       bar_area_mm2, faces_by_coord, interior_corners,
                       no_erode_faces, reflex_on_sides, solver_area_mm2,
                       true_bar_area_mm2)
from geometry import Envelope, Rect                                  # noqa: E402
from scenarios import Brief, Proposal, RoomSpec                      # noqa: E402
from solver import SolveConfig, project                              # noqa: E402
from absolute_area import outside_of, space_m2                       # noqa: E402

T_INT = 150
OK = []


def note(s):
    OK.append(s)
    print(f"  ok  {s}")


# ---------------------------------------------------------------------------
def t1_hand_checks():
    """Part VII table: a 4 x 3-cell Room, all sides interior and then with its
    left side on the boundary."""
    # An Envelope big enough that the Room is interior on all four sides.
    env = Envelope("box", 10, 10, (), (Rect(0, 0, 10, 10),))
    r = Rect(3, 3, 7, 6)                       # 4 x 3 cells = 1000 x 750 mm
    assert r.w == 4 and r.h == 3
    b = bar_area_mm2(env, r, T_INT)
    t = true_bar_area_mm2(env, r, T_INT)
    assert b == 487_500, b
    assert t == 510_000, t
    assert t - b == 4 * CORNER_MM2
    assert solver_area_mm2(r, T_INT) == (1000 - 150) * (750 - 150) == 510_000
    note("VII.3 row 1: all four sides interior -> 487 500 against 510 000, "
         "four corners")

    # Same Room with its left side on the Envelope.
    r2 = Rect(0, 3, 4, 6)
    b2 = bar_area_mm2(env, r2, T_INT)
    t2 = true_bar_area_mm2(env, r2, T_INT)
    assert b2 == 543_750, b2
    assert t2 == 555_000, t2
    assert t2 - b2 == 2 * CORNER_MM2
    assert (1000 - 75) * (750 - 150) == 555_000
    note("VII.3 row 2: left side on the boundary -> 543 750 against 555 000, "
         "two corners")

    # The identity the whole ADR turns on: with NO boundary contact [B] is [A]
    # minus exactly the four corners, so the incumbent is corner-exact and
    # boundary-wrong and the replacement is the other way round.
    assert solver_area_mm2(r, T_INT) - bar_area_mm2(env, r, T_INT) == 4 * CORNER_MM2
    note("[A] - [B] = 22 500 mm2 with no boundary contact: the incumbent is "
         "corner-exact, the replacement is boundary-exact")


# ---------------------------------------------------------------------------
def _tile(env: Envelope, seed: int):
    """A guillotine tiling of an Envelope's parts into Rooms, on the grid.

    Not a solve -- just a deterministic dissection that gives T2/T3 a real
    multi-Room geometry with interior joins, boundary runs and (for the void
    case) an edge on an enclosed hole.
    """
    rng = random.Random(seed)
    out = []
    todo = [Rect(p.x1, p.y1, p.x2, p.y2) for p in env.parts]
    while todo:
        r = todo.pop()
        if r.w <= 3 or r.h <= 3 or (len(out) + len(todo)) >= 7:
            out.append(r)
            continue
        if (r.w >= r.h) if rng.random() < 0.7 else (r.w > r.h):
            c = rng.randint(2, r.w - 2)
            todo += [Rect(r.x1, r.y1, r.x1 + c, r.y2), Rect(r.x1 + c, r.y1, r.x2, r.y2)]
        else:
            c = rng.randint(2, r.h - 2)
            todo += [Rect(r.x1, r.y1, r.x2, r.y1 + c), Rect(r.x1, r.y1 + c, r.x2, r.y2)]
    return out


def _envelopes():
    """A rectangle, an L, a U, and one with an ENCLOSED void."""
    box = Envelope("rect", 16, 12, (), (Rect(0, 0, 16, 12),))
    ln = Rect(11, 8, 16, 12)
    ell = Envelope("L", 16, 12, (ln,),
                   (Rect(0, 0, 11, 12), Rect(11, 0, 16, 8)))
    u1, u2 = Rect(5, 8, 8, 12), Rect(12, 8, 15, 12)
    u = Envelope("U", 16, 12, (u1, u2),
                 (Rect(0, 0, 16, 8), Rect(0, 8, 5, 12), Rect(8, 8, 12, 12),
                  Rect(15, 8, 16, 12)))
    vd = Rect(6, 5, 9, 7)
    void = Envelope("void", 16, 12, (vd,),
                    (Rect(0, 0, 16, 5), Rect(0, 5, 6, 7), Rect(9, 5, 16, 7),
                     Rect(0, 7, 16, 12)))
    return [box, ell, u, void]


def t2_against_shapely():
    n = 0
    for env in _envelopes():
        for seed in range(6):
            rooms = _tile(env, seed)
            assert sum(r.area for r in rooms) == env.interior_area, env.name
            rects = [[(r.x1 * GRID_MM, r.y1 * GRID_MM,
                       r.x2 * GRID_MM, r.y2 * GRID_MM)] for r in rooms]
            outside = outside_of(rects)
            for r, rs in zip(rooms, rects):
                truth = round(space_m2(rs, outside) * 1e6)
                mine = true_bar_area_mm2(env, r, T_INT)
                assert abs(truth - mine) <= 1, (env.name, seed, r, truth, mine)
                n += 1
    note(f"T2: true_bar_area == space_m2 on {n} Rooms over a rect, an L, a U "
         f"and an enclosed void")


def t2b_void_erodes():
    """The correctness point ADR 0039's `all_faces()` would have got wrong: a
    Room's edge on an ENCLOSED void must erode."""
    void = [e for e in _envelopes() if e.name == "void"][0]
    # The Room directly under the void: its north side runs along the hole.
    r = Rect(6, 0, 9, 5)
    fac = faces_by_coord(void)
    assert not any(lo <= 6 and hi >= 9 for (lo, hi) in fac.get(("h", 5), ())), \
        "an enclosed void's face must not be credited as boundary contact"
    allf = {(k, c) for (k, c, _lo, _hi, _e) in void.all_faces()}
    assert ("h", 5) in allf, "all_faces() does return the void's face"
    rects = [[(r.x1 * GRID_MM, r.y1 * GRID_MM, r.x2 * GRID_MM, r.y2 * GRID_MM)]]
    # measured inside the full tiling, so `outside_of` sees the hole
    full = _tile(void, 0)
    allr = [[(q.x1 * GRID_MM, q.y1 * GRID_MM, q.x2 * GRID_MM, q.y2 * GRID_MM)]
            for q in full]
    outside = outside_of(allr)
    truth = round(space_m2(rects[0], outside) * 1e6)
    assert true_bar_area_mm2(void, r, T_INT) == truth, (truth,)
    note("T2b: `all_faces()` carries the enclosed void's face and the encoding "
         "must not -- checked on the Room under the hole")


# ---------------------------------------------------------------------------
def _brief_for(env: Envelope, rooms, min_area=1, min_side=1):
    specs = [RoomSpec(f"r{i}", "living" if i else "hall", min_side, min_side,
                      min_area) for i in range(len(rooms))]
    return Brief(env.name, env, GRID_MM, specs, entry=0, max_aspect=99)


def _read_amm(env, rooms, corners: bool):
    """Pin the Rooms to `rooms` and read `amm_i` straight out of the model."""
    b = _brief_for(env, rooms)
    prop = Proposal(boxes=list(rooms), kinds=[s.kind for s in b.rooms])
    cfg = SolveConfig(workers=1, time_limit_s=20.0, area_units="mm_affine",
                      erode_minima=True, t_int_mm=T_INT, hint=False,
                      soft=("coverage", "exterior", "wet_cluster", "circulation"),
                      diagnose=False)
    p = BarPlaneProjector(b, prop, cfg, plane="bar", corners=corners)
    for i, r in enumerate(rooms):
        p.m.Add(p.x1[i] == r.x1)
        p.m.Add(p.y1[i] == r.y1)
        p.m.Add(p.x2[i] == r.x2)
        p.m.Add(p.y2[i] == r.y2)
    s = cp_model.CpSolver()
    s.parameters.num_workers = 1
    s.parameters.max_time_in_seconds = 30.0
    st = s.Solve(p.m)
    assert st in (cp_model.OPTIMAL, cp_model.FEASIBLE), s.StatusName(st)
    return [s.Value(v) for v in p.area_mm2]


def t3_model_agrees():
    n = 0
    for env in _envelopes():
        for seed in (0, 1, 2):
            rooms = _tile(env, seed)
            got = _read_amm(env, rooms, corners=False)
            want = [bar_area_mm2(env, r, T_INT) for r in rooms]
            assert got == want, (env.name, seed, got, want)
            gotc = _read_amm(env, rooms, corners=True)
            wantc = [bar_area_mm2(env, r, T_INT)
                     + CORNER_MM2 * interior_corners(env, r) for r in rooms]
            assert gotc == wantc, (env.name, seed, gotc, wantc)
            n += len(rooms)
    note(f"T3: the CP-SAT model's amm_i equals the oracle on {n} Rooms, with "
         f"and without the corner term")


# ---------------------------------------------------------------------------
def t4_solver_arm_is_the_incumbent():
    env = [e for e in _envelopes() if e.name == "L"][0]
    rooms = _tile(env, 3)
    b = _brief_for(env, rooms, min_area=2, min_side=2)
    prop = Proposal(boxes=list(rooms), kinds=[s.kind for s in b.rooms])
    cfg = SolveConfig(workers=1, time_limit_s=20.0, seed=7, area_units="mm_affine",
                      erode_minima=True, t_int_mm=T_INT, fix_relations=True,
                      relation_confidence=4,
                      soft=("coverage", "exterior", "wet_cluster", "circulation"))
    a = project(b, prop, cfg)
    from bar_plane import project_plane
    c = project_plane(b, prop, cfg, plane="solver")
    assert a.status == c.status, (a.status, c.status)
    assert a.objective == c.objective, (a.objective, c.objective)
    assert a.model_stats["variables"] == c.model_stats["variables"]
    assert a.model_stats["constraints"] == c.model_stats["constraints"]
    assert a.model_stats["multiplications"] == c.model_stats["multiplications"]
    note(f"T4: plane='solver' is the incumbent -- {a.status}, objective "
         f"{a.objective}, {a.model_stats['variables']} variables both ways")


def t5_min_side_identity():
    """LIMIT 2 at each interior-side count.

    The solver binds `clear_w >= min_w * 250`. On the incumbent plane
    `clear_w = 250w - 150` and `w >= min_w` follows for every integer min_w.
    On the bar plane `clear_w = 250w - 75 * n_interior`, so:

        n = 2   250w - 150 >= 250(min_w)      ...  w >= min_w + 0.6  -> min_w+1
        n = 1   250w -  75 >= 250(min_w)      ...  w >= min_w + 0.3  -> min_w+1
        n = 0   250w       >= 250(min_w)      ...  w >= min_w

    ⚠️ These bind on `min_w * 250`, NOT on `(min_w - 1) * 250` -- that shift is
    `project_join.py`'s, applied when it BUILDS the RoomSpec. Composed with it,
    the bar plane costs a Room the same grid unit at n = 1 and n = 2 and hands
    one back at n = 0.
    """
    for n_int, want in ((2, 0.6), (1, 0.3), (0, 0.0)):
        for min_w in range(1, 12):
            lo = math.ceil((250 * min_w + 75 * n_int) / 250)
            assert lo == min_w + math.ceil(want - 1e-9), (n_int, min_w, lo)
    # and the shifted form project_join actually posts
    for min_w in range(2, 12):
        lo2 = math.ceil((250 * (min_w - 1) + 150) / 250)
        assert lo2 == min_w
        lo1 = math.ceil((250 * (min_w - 1) + 75) / 250)
        assert lo1 == min_w
        lo0 = math.ceil((250 * (min_w - 1)) / 250)
        assert lo0 == min_w - 1
    note("T5: LIMIT 2 holds at 1 and 2 interior sides and RELAXES by one grid "
         "unit at 0 -- a Room spanning the Envelope loses no partition")


def t6_face_shapes():
    """The face set is the interior's real boundary, not the bbox."""
    for env in _envelopes():
        fac = no_erode_faces(env)
        total = sum(hi - lo for runs in fac.values() for (lo, hi) in runs)
        # every no-erode unit edge is a boundary edge of the interior
        allf = {}
        for (k, c, lo, hi, _e) in env.all_faces():
            allf.setdefault((k, c), []).append((lo, hi))
        atot = sum(hi - lo for runs in allf.values() for (lo, hi) in runs)
        assert total <= atot, env.name
        if env.name != "void":
            assert total == atot, (env.name, total, atot)
    v = [e for e in _envelopes() if e.name == "void"][0]
    tv = sum(hi - lo for runs in no_erode_faces(v).values() for (lo, hi) in runs)
    av = sum(hi - lo for (_k, _c, lo, hi, _e) in v.all_faces())
    assert av - tv == 2 * (3 + 2), (av, tv)   # the 3 x 2 hole's perimeter
    note(f"T6: no_erode_faces == all_faces on rect/L/U and drops exactly the "
         f"void's perimeter ({av - tv} units) on the void case")


if __name__ == "__main__":
    t1_hand_checks()
    t2_against_shapely()
    t2b_void_erodes()
    t6_face_shapes()
    t3_model_agrees()
    t4_solver_arm_is_the_incumbent()
    t5_min_side_identity()
    print(f"\n{len(OK)} checks passed")
