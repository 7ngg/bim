"""Independent checker for a returned Plan.

Deliberately shares no code with `solver.py` beyond raw geometry. A solver that
reports OPTIMAL against a mis-stated model is worse than one that fails, so
every result in the timing table is re-checked here from the coordinates alone.

This is a stand-in for the real Acceptance bar (ticket 07). The two must be one
definition in the product; here they are two, on purpose, so they can disagree.
"""

from __future__ import annotations

from typing import Dict, List, Sequence

from geometry import (
    Rect,
    adjacency_matrix,
    connected,
    reachable_without_private,
    tiling_defects,
    touches_exterior,
)
from scenarios import HABITABLE, PRIVATE, WET, Brief


def check(brief: Brief, rooms: Sequence[Rect], window_min: int = 4) -> Dict[str, object]:
    b, env = brief, brief.env
    fails: List[str] = []

    for i, r in enumerate(rooms):
        if not env.contains(r):
            fails.append(f"H1 room {i} ({b.rooms[i].name}) leaves the Envelope")

    d = tiling_defects(rooms, env)
    if d["pairwise_overlap_area"] > 0:
        fails.append(f"H2 overlap area {d['pairwise_overlap_area']} grid cells")
    if d["uncovered_cells"] > 0:
        fails.append(f"H3 {d['uncovered_cells']} interior cells unassigned")
    if d["cells_outside_envelope"] > 0:
        fails.append(f"H1 {d['cells_outside_envelope']} cells outside the Envelope")

    for i, (r, spec) in enumerate(zip(rooms, b.rooms)):
        if r.w < spec.min_w or r.h < spec.min_h:
            fails.append(f"H4 room {i} ({spec.name}) {r.w}x{r.h} under min "
                         f"{spec.min_w}x{spec.min_h}")
        if r.area < spec.min_area:
            fails.append(f"H4 room {i} ({spec.name}) area {r.area} < {spec.min_area}")
        if r.w > b.max_aspect * r.h or r.h > b.max_aspect * r.w:
            fails.append(f"H5 room {i} ({spec.name}) aspect {r.w}:{r.h}")

    adj_door = adjacency_matrix(rooms, b.door_min)
    adj_any = adjacency_matrix(rooms, 1)

    for i, j in b.required_adj:
        if not adj_door[i][j]:
            fails.append(f"H6 required adjacency {b.rooms[i].name}-{b.rooms[j].name} missing")
    for i, j in b.forbidden_adj:
        if adj_any[i][j]:
            fails.append(f"H7 forbidden adjacency {b.rooms[i].name}-{b.rooms[j].name} present")

    for i, spec in enumerate(b.rooms):
        if spec.kind in HABITABLE and not touches_exterior(rooms[i], env, window_min):
            fails.append(f"H8 {spec.name} has no exterior wall run of {window_min}")

    wet = b.indices(sorted(WET))
    if len(wet) > 1 and not connected(adj_any, wet):
        fails.append("H9 wet rooms are not one plumbing cluster")

    private = [i for i, r in enumerate(b.rooms) if r.kind in PRIVATE and i != b.entry]
    ok, unreached = reachable_without_private(adj_door, b.entry, private)
    if not ok:
        names = ", ".join(b.rooms[i].name for i in unreached)
        fails.append(f"H10 unreachable without traversing a private room: {names}")

    return {"ok": not fails, "failures": fails, "defects": d}


def summarise(brief: Brief, rooms: Sequence[Rect]) -> str:
    r = check(brief, rooms)
    if r["ok"]:
        return "VALID"
    return f"INVALID ({len(r['failures'])}): " + "; ".join(r["failures"][:4])
