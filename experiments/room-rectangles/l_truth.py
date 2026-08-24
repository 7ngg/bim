"""A ground truth in which some Rooms genuinely ARE two rectangles.

`scenarios.ground_truth` dissects the Envelope by guillotine cuts, so every
truth Room is a rectangle and no L is ever *needed*. That is the right control
for measuring what the extra freedom costs (`sweep_k2.py`), and useless for
measuring whether a Proposal that carries an L can be projected at all.

So: build the guillotine truth for `n + j` rectangles, then MERGE `j` adjacent
pairs into single Rooms. The result is `n` Rooms of which `j` are L-shaped, it
still exactly tiles the Envelope, and it is reachable by the same generator --
which matters, because a hand-drawn L would be a shape nobody had to satisfy the
Brief with.

A merge is only taken when the union is NOT itself a rectangle. Merging two
rectangles that happen to stack into a bigger one would produce a k = 1 Room
wearing two boxes, and every count off it would be a lie.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

TOY = Path(__file__).resolve().parents[1] / "solver-toy"
sys.path.insert(0, str(TOY))

from geometry import Rect, adjacency_matrix  # noqa: E402
from scenarios import (  # noqa: E402
    CIRCULATION, GRID_MM, MAX_ASPECT, STANDARDS, Brief, Proposal, RoomSpec,
    make_brief,
)

PREFERRED = frozenset(CIRCULATION | {"living", "dining", "kitchen"})


def _union_is_rect(a: Rect, b: Rect) -> bool:
    return (a.area + b.area) == ((max(a.x2, b.x2) - min(a.x1, b.x1)) *
                                 (max(a.y2, b.y2) - min(a.y1, b.y1)))


def merge_to_l(brief: Brief, truth: Sequence[Rect], kinds: Sequence[str],
               j: int, leg_join: int, leg_min: int, seed: int):
    """Fold `j` adjacent pairs into L-shaped Rooms. Returns None if it cannot.

    The surviving Room keeps the kind of its LARGER rectangle, which then serves
    as the primary and still meets that kind's minima -- it did before the
    merge and the merge does not shrink it.
    """
    rng = random.Random(seed * 31 + 7)
    n = len(truth)
    adj = adjacency_matrix(truth, leg_join)
    cand: List[Tuple[int, int]] = []
    for a in range(n):
        for b in range(a + 1, n):
            if not adj[a][b] or _union_is_rect(truth[a], truth[b]):
                continue
            big, small = (a, b) if truth[a].area >= truth[b].area else (b, a)
            if min(truth[small].w, truth[small].h) < leg_min:
                continue
            cand.append((big, small))
    # An L is most defensible where real dwellings have them: circulation and
    # open-plan living. Take those first, then anything.
    rng.shuffle(cand)
    cand.sort(key=lambda p: 0 if kinds[p[0]] in PREFERRED else 1)

    used, merges = set(), []
    for big, small in cand:
        if len(merges) >= j:
            break
        if big in used or small in used:
            continue
        used.update((big, small))
        merges.append((big, small))
    if len(merges) < j:
        return None

    absorbed = {s for _b, s in merges}
    old_to_new: Dict[int, int] = {}
    order = [i for i in range(n) if i not in absorbed]
    for new, old in enumerate(order):
        old_to_new[old] = new
    for big, small in merges:
        old_to_new[small] = old_to_new[big]

    parts: Dict[int, List[Rect]] = {old_to_new[o]: [truth[o]] for o in order}
    for big, small in merges:
        parts[old_to_new[big]].append(truth[small])

    rooms = [RoomSpec(f"{kinds[o]}{i}", kinds[o], *STANDARDS[kinds[o]])
             for i, o in enumerate(order)]

    def remap(pairs):
        out = set()
        for i, k in pairs:
            a, b = old_to_new[i], old_to_new[k]
            if a != b:
                out.add((min(a, b), max(a, b)))
        return sorted(out)

    nb = Brief(
        name=brief.name + "+L", env=brief.env, grid_mm=GRID_MM, rooms=rooms,
        entry=old_to_new[brief.entry],
        required_adj=remap(brief.required_adj),
        forbidden_adj=remap(brief.forbidden_adj),
        door_min=brief.door_min, max_aspect=MAX_ASPECT,
    )
    return nb, parts, [kinds[o] for o in order]


def l_scenario(env, n: int, j: int, seed: int, door_min: int, window_min: int,
               clear_t: int, leg_join: int, leg_min: int, sigma: float,
               attempts: int = 8):
    """A Brief of `n` Rooms, `j` of them L-shaped, plus a jittered Proposal.

    The Proposal carries one box per PART -- Design A's contract -- jittered with
    the same per-corner Gaussian the shipped sweep uses, so a part is noised
    exactly as a Room was.
    """
    for a in range(attempts):
        try:
            brief, truth, kinds = make_brief(
                f"{n}+{j}-room", env, n + j, seed + a * 1009, door_min,
                window_min, clear_t=clear_t)
        except Exception:                       # noqa: BLE001 - a result
            continue
        got = merge_to_l(brief, truth, kinds, j, leg_join, leg_min, seed + a)
        if got is None:
            continue
        nb, parts, nkinds = got
        rng = random.Random(seed * 7919 + 13)
        pp: Dict[int, List[Rect]] = {}
        for r, ps in parts.items():
            out = []
            for box in ps:
                x1 = box.x1 + round(rng.gauss(0, sigma))
                x2 = box.x2 + round(rng.gauss(0, sigma))
                y1 = box.y1 + round(rng.gauss(0, sigma))
                y2 = box.y2 + round(rng.gauss(0, sigma))
                if x2 <= x1:
                    x1, x2 = min(x1, x2), min(x1, x2) + 1
                if y2 <= y1:
                    y1, y2 = min(y1, y2), min(y1, y2) + 1
                out.append(Rect(x1, y1, x2, y2))
            pp[r] = out
        flat = Proposal([pp[r][0] for r in sorted(pp)], list(nkinds))
        return nb, parts, pp, flat
    return None
