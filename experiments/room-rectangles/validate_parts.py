"""Independent checker for a Plan whose Rooms are 1..2 rectangles.

Same posture as `experiments/solver-toy/validate.py`: shares no code with the
model that produced the answer, beyond raw geometry. A solver reporting OPTIMAL
against a mis-stated model is worse than one that fails, and the k <= 2 model is
new, so every VALID in the sweep is re-derived here from coordinates alone.

The one thing this checks that `validate.py` cannot: the JOIN. Two parts of one
Room must share an edge of at least the leg floor, or the "Room" is two rooms
with no door between them -- the failure mode that makes a concave Space a
different thing from a partitioned one.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Sequence

TOY = Path(__file__).resolve().parents[1] / "solver-toy"
sys.path.insert(0, str(TOY))

from geometry import Rect, tiling_defects  # noqa: E402
from scenarios import HABITABLE, PRIVATE, WET, Brief  # noqa: E402


def _live(parts: Sequence[Rect]) -> List[Rect]:
    return [r for r in parts if r.w > 0 and r.h > 0]


def _room_rects(rooms_parts: Dict[int, List[Rect]]) -> Dict[int, List[Rect]]:
    return {r: _live(ps) for r, ps in rooms_parts.items()}


def _contact_len(a: Sequence[Rect], b: Sequence[Rect]) -> int:
    """Longest shared edge between any part of a and any part of b."""
    best = 0
    for p in a:
        for q in b:
            best = max(best, p.shared_edge_length(q))
    return best


def _touches_exterior(parts: Sequence[Rect], env, L: int) -> bool:
    from geometry import touches_exterior
    return any(touches_exterior(r, env, L) for r in parts)


def _reach(adj: Dict[int, set], root: int, blocked: Sequence[int], nodes):
    seen, stack = {root}, [root]
    while stack:
        u = stack.pop()
        if u != root and u in blocked:
            continue                     # may consume, may not forward
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return set(nodes) - seen


def check(brief: Brief, rooms_parts: Dict[int, List[Rect]], *,
          leg_min: int, leg_join: int, window_min: int = 4) -> Dict[str, object]:
    b, env = brief, brief.env
    fails: List[str] = []
    rp = _room_rects(rooms_parts)
    flat = [r for ps in rp.values() for r in ps]

    for r, ps in rp.items():
        if not ps:
            fails.append(f"H0 room {r} ({b.rooms[r].name}) has no rectangle")
        for q in ps:
            if not env.contains(q):
                fails.append(f"H1 room {r} ({b.rooms[r].name}) leaves the Envelope")

    d = tiling_defects(flat, env)
    if d["pairwise_overlap_area"] > 0:
        fails.append(f"H2 overlap area {d['pairwise_overlap_area']} grid cells")
    if d["uncovered_cells"] > 0:
        fails.append(f"H3 {d['uncovered_cells']} interior cells unassigned")
    if d["cells_outside_envelope"] > 0:
        fails.append(f"H1 {d['cells_outside_envelope']} cells outside the Envelope")

    # H4 / H5, PER PART. The primary carries the Room's minima; any further part
    # carries the universal leg floor. Area is per ROOM, over the union.
    for r, ps in rp.items():
        spec = b.rooms[r]
        for k, q in enumerate(ps):
            # NOTE the asymmetry, and it is the safe direction: the solver
            # binds a secondary part's floor on the ERODED clear rect
            # (`cw >= leg_min * 250`, so 1000 mm clear at leg_min 4) while this
            # checks the SOLVED rect (1000 mm solved, 850 mm clear). The checker
            # is therefore looser than the model it checks, so it can never
            # certify a leg the solver would have refused.
            mw, mh = (spec.min_w, spec.min_h) if k == 0 else (leg_min, leg_min)
            if q.w < mw or q.h < mh:
                fails.append(f"H4 room {r} ({spec.name}) part {k} {q.w}x{q.h} "
                             f"under min {mw}x{mh}")
            if q.w > b.max_aspect * q.h or q.h > b.max_aspect * q.w:
                fails.append(f"H5 room {r} ({spec.name}) part {k} aspect "
                             f"{q.w}:{q.h}")
        if sum(q.area for q in ps) < spec.min_area:
            fails.append(f"H4 room {r} ({spec.name}) area "
                         f"{sum(q.area for q in ps)} < {spec.min_area}")
        if len(ps) > 2:
            fails.append(f"K room {r} ({spec.name}) has {len(ps)} rectangles")
        if len(ps) == 2:
            j = ps[0].shared_edge_length(ps[1])
            if j < leg_join:
                fails.append(f"JOIN room {r} ({spec.name}) legs share {j} "
                             f"< {leg_join}")

    rooms = sorted(rp)
    door = {i: set() for i in rooms}
    anyc = {i: set() for i in rooms}
    for a in range(len(rooms)):
        for c in range(a + 1, len(rooms)):
            i, j = rooms[a], rooms[c]
            L = _contact_len(rp[i], rp[j])
            if L >= b.door_min:
                door[i].add(j)
                door[j].add(i)
            if L >= 1:
                anyc[i].add(j)
                anyc[j].add(i)

    for i, j in b.required_adj:
        if j not in door[i]:
            fails.append(f"H6 required adjacency {b.rooms[i].name}-"
                         f"{b.rooms[j].name} missing")
    for i, j in b.forbidden_adj:
        if j in anyc[i]:
            fails.append(f"H7 forbidden adjacency {b.rooms[i].name}-"
                         f"{b.rooms[j].name} present")

    for r, spec in enumerate(b.rooms):
        if spec.kind in HABITABLE and not _touches_exterior(rp[r], env, window_min):
            fails.append(f"H8 {spec.name} has no exterior wall run of {window_min}")

    wet = b.indices(sorted(WET))
    if len(wet) > 1:
        sub = {i: (anyc[i] & set(wet)) for i in wet}
        if _reach(sub, wet[0], (), wet):
            fails.append("H9 wet rooms are not one plumbing cluster")

    private = [i for i, r in enumerate(b.rooms) if r.kind in PRIVATE and i != b.entry]
    un = _reach(door, b.entry, private, rooms)
    if un:
        names = ", ".join(b.rooms[i].name for i in sorted(un))
        fails.append(f"H10 unreachable without traversing a private room: {names}")

    return {"ok": not fails, "failures": fails, "defects": d,
            "l_rooms": [r for r, ps in rp.items() if len(ps) > 1]}
