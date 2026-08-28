"""Rectilinear geometry helpers for the layout-projection toy.

Everything is in integer *grid units*. One grid unit = `GRID_MM` millimetres
(set per scenario). No floating point anywhere in the solver path — C6 item 6
wants orthogonal, grid-snapped walls, and integers give that for free.

A `Rect` is half-open: it covers x in [x1, x2) and y in [y1, y2).
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, List, Sequence, Tuple


@dataclass(frozen=True)
class Rect:
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def w(self) -> int:
        return self.x2 - self.x1

    @property
    def h(self) -> int:
        return self.y2 - self.y1

    @property
    def area(self) -> int:
        return self.w * self.h

    @property
    def cx2(self) -> int:
        """Centroid x, doubled (stays integral)."""
        return self.x1 + self.x2

    @property
    def cy2(self) -> int:
        return self.y1 + self.y2

    def intersect(self, other: "Rect") -> "Rect | None":
        x1 = max(self.x1, other.x1)
        y1 = max(self.y1, other.y1)
        x2 = min(self.x2, other.x2)
        y2 = min(self.y2, other.y2)
        if x1 >= x2 or y1 >= y2:
            return None
        return Rect(x1, y1, x2, y2)

    def overlap_area(self, other: "Rect") -> int:
        r = self.intersect(other)
        return 0 if r is None else r.area

    def shared_edge_length(self, other: "Rect") -> int:
        """Length of the common boundary segment (0 if not edge-adjacent).

        Two rectangles are *adjacent* when one's face is flush against the
        other's opposite face and the projections onto that face overlap in a
        segment of positive length. Corner-only touching gives 0.
        """
        if self.x2 == other.x1 or other.x2 == self.x1:
            lo = max(self.y1, other.y1)
            hi = min(self.y2, other.y2)
            return max(0, hi - lo)
        if self.y2 == other.y1 or other.y2 == self.y1:
            lo = max(self.x1, other.x1)
            hi = min(self.x2, other.x2)
            return max(0, hi - lo)
        return 0


# Ticket 15 axis 6: dwelling-type presets over the Envelope's edge ring.
# `detached` is what every timing before this ticket was measured at.
# A preset maps each bbox edge to the *fraction* of its run that is exterior,
# anchored at the edge's low end. A whole edge is 1.0, a party edge 0.0. The
# fractional case is not decoration: a real flat's front elevation is commonly
# part window wall and part shared, which is why the four whole-edge presets
# cannot reach the corpus median on their own (see the fitted entry below).
# Re-fitted by *The exposure presets were fitted to a measurement of one room*,
# 2026-08-26, over 2,238 Swiss dwellings — `experiments/envelope-exposure/`,
# `fit_ladder.py`, which prints this block. Three things changed at once.
#
# 1. The distribution they were fitted to measured ONE ROOM per dwelling.
#    `dataset-inventory.md` §1.5 was corrected from a median exterior fraction of
#    0.37 to 0.67. Every value below was tuned against the wrong column.
# 2. They are fitted on EXTERIOR RUN PER ROOM, not on a fraction of perimeter.
#    A fraction only transfers between dwellings whose perimeters match, and they
#    do not: at eight rooms this Envelope has 36.0 m of perimeter around 75.0 m²
#    where the real median dwelling has 47.6 m around 94.1 m². H8 reads run — a
#    room needs a window's width of façade and cannot spend a percentage.
# 3. A key is now a QUANTILE WITH A RING SHAPE, not a building form. Measured,
#    real dwellings are 63.3 % four-sided and 26.0 % three-sided; the forms these
#    keys name — one, adjacent pair, opposite pair — are 10.6 % between them, and
#    there was no three-sided preset at all. The keys survive only because they
#    are named in five documents and three experiment directories that ticket
#    could not write. `flat_corner` and `terrace_mid` are now a MATCHED PAIR:
#    same exposure, different ring, so the two isolate shape at fixed run.
#
# Anchored at n = 7 — the corpus median room count and the centre of C13's band.
# ⚠️ Each preset DRIFTS across that band, because `envelope_for(n)` is more
# compact than a real dwelling and gets more so with n (perimeter/area 0.390
# against the corpus 0.572 at twelve rooms). `corpus_median` sits at the corpus
# p85 at four rooms and p25 at twelve. Above nine rooms the corpus median is
# unreachable at ANY preset, `detached` included. Both are structural and belong
# to this directory's holder, not to the presets — see `envelope-exposure/README.md`.
EXPOSURE_PRESETS = {
    # 100 % exterior. Not a flat: the ceiling, and the house preset C5 needs.
    # Corpus p93 for run per room at four rooms, p39 at twelve.
    "detached": {"W": 1.0, "E": 1.0, "S": 1.0, "N": 1.0},
    # p5 of run per room (2.09 m). A genuine single-aspect flat is a tail case,
    # so it is anchored at the tail rather than at a quartile.
    "flat_single_aspect": {"W": 0.53, "E": 0.17, "S": 0.96, "N": 0.02},
    # p25 (3.28 m), two aspects meeting at the SE corner.
    "flat_corner": {"W": 0.32, "E": 1.0, "S": 1.0, "N": 0.1},
    # p25 (3.28 m) also, two aspects facing each other. Pairs with `flat_corner`.
    "terrace_mid": {"W": 0.18, "E": 0.06, "S": 1.0, "N": 1.0},
    # p50 (4.19 m), four-sided — the shape 63.3 % of real dwellings have. The
    # name is accurate for the first time; it previously ran at the corpus p3–p10.
    "corpus_median": {"W": 0.99, "E": 0.77, "S": 1.0, "N": 0.29},
}


@dataclass(frozen=True)
class Envelope:
    """A rectilinear Envelope: a bounding box minus a set of notch rectangles.

    `parts` is a disjoint rectangular decomposition of the *interior* — used by
    the ground-truth generator. `notches` is the complement inside the bbox,
    used by the solver as fixed obstacles in the no-overlap constraint.
    """

    name: str
    W: int
    H: int
    notches: Tuple[Rect, ...]
    parts: Tuple[Rect, ...]
    # Ticket 15 axis 6 / ADR 0003: the Envelope is an ordered ring of typed
    # edges and only an `exterior` edge may hold a window. The four bbox edges
    # are keyed W (x=0), E (x=W), S (y=0), N (y=H); a preset names the subset
    # that is exterior. Everything else is a party edge.
    exposure: str = "detached"

    @property
    def bbox(self) -> Rect:
        return Rect(0, 0, self.W, self.H)

    @property
    def interior_area(self) -> int:
        return self.W * self.H - sum(n.area for n in self.notches)

    def contains(self, r: Rect) -> bool:
        if r.x1 < 0 or r.y1 < 0 or r.x2 > self.W or r.y2 > self.H:
            return False
        return all(r.overlap_area(n) == 0 for n in self.notches)

    @property
    def exterior_sides(self) -> dict:
        """Per-bbox-edge exterior fraction for this preset."""
        try:
            return EXPOSURE_PRESETS[self.exposure]
        except KeyError:
            raise ValueError(f"unknown exposure preset {self.exposure!r}")

    def _bbox_runs(self) -> List[Tuple[str, int, int, int, bool]]:
        """The four bbox edges, split where a preset makes one partly party.

        A partial edge becomes an exterior head plus a party tail, anchored at
        the edge's low end, so every face is wholly one type and nothing
        downstream needs a fraction.
        """
        frac = self.exterior_sides
        base = [
            ("v", 0, 0, self.H, "W"),
            ("v", self.W, 0, self.H, "E"),
            ("h", 0, 0, self.W, "S"),
            ("h", self.H, 0, self.W, "N"),
        ]
        out: List[Tuple[str, int, int, int, bool]] = []
        for (k, c, lo, hi, side) in base:
            f = frac.get(side, 0.0)
            if f >= 1.0:
                out.append((k, c, lo, hi, True))
            elif f <= 0.0:
                out.append((k, c, lo, hi, False))
            else:
                cut = max(lo + 1, min(hi - 1, lo + int(round((hi - lo) * f))))
                out.append((k, c, lo, cut, True))
                out.append((k, c, cut, hi, False))
        return out

    def _notch_is_exterior(self, n: Rect) -> bool:
        """A notch sees daylight iff it opens onto an exterior run.

        Notches are cut from the boundary (see `l_shape` / `u_shape`), so a
        notch is flush with at least one bbox edge; it is a light well rather
        than a shaft exactly when the stretch of edge it replaces is exterior.
        """
        for (k, c, lo, hi, is_ext) in self._bbox_runs():
            if not is_ext:
                continue
            if k == "v" and c == n.x1 == 0 or k == "v" and c == n.x2 == self.W:
                if min(n.y2, hi) - max(n.y1, lo) > 0:
                    return True
            if k == "h" and c == n.y1 == 0 or k == "h" and c == n.y2 == self.H:
                if min(n.x2, hi) - max(n.x1, lo) > 0:
                    return True
        return False

    def all_faces(self) -> List[Tuple[str, int, int, int, bool]]:
        """Every boundary face of the *interior*, as ('v'|'h', coord, lo, hi, is_exterior).

        Built by walking the real boundary — the set of unit edges with interior
        on one side and not on the other, merged into maximal runs. A stretch of
        bbox edge a notch removed is simply absent, and a notch face that is not
        on a bbox line appears exactly once.

        Until *The toy Envelope is more compact than a real dwelling* this
        emitted every bbox edge **in full** plus all four faces of every notch,
        so a corner notch's removed stretch was counted twice — once as bbox
        edge, once as a phantom notch face laid over it. On `envelope_for(8)`
        that read 180 grid units of perimeter against a true 144. The phantom
        faces reached `exterior_faces()` too, and through it `frontage.py`'s H8
        budget, which is why the defect was not confined to a fraction.
        `experiments/envelope-exposure/true_fraction.py` is the shapely
        implementation this agrees with, kept there as an independent check.
        """
        return list(_faces_of(self))

    def exterior_faces(self) -> List[Tuple[str, int, int, int]]:
        """Every *exterior* wall face, as ('v'|'h', coord, lo, hi).

        'v' means a vertical face at x == coord spanning y in [lo, hi).
        A room touches the exterior if one of its faces is flush with one of
        these and overlaps it in a segment of positive length.

        Ticket 15: this used to return every boundary face unfiltered, which is
        why every timing on the map described a detached bungalow. It is now
        filtered by the `exposure` preset, and since *The toy Envelope is more
        compact than a real dwelling* it is also free of the phantom faces that
        inflated every frontage budget taken off it.
        """
        return [(k, c, lo, hi) for (k, c, lo, hi, e) in self.all_faces() if e]

    @property
    def exterior_fraction(self) -> float:
        """Exterior share of the Envelope perimeter, counted once per face.

        The corpus figures this used to quote (p25 0.23, median 0.37, p75 0.47)
        measured **one room per dwelling**, not the dwelling. Corrected values
        are p25 0.55, median 0.68, p75 0.80 — `dataset-inventory.md` §1.5.
        No preset is fitted on this scalar any more: `EXPOSURE_PRESETS` is fitted
        on exterior run per room, because a fraction does not transfer between
        dwellings whose perimeters differ.
        """
        total = ext = 0
        for (k, c, lo, hi, e) in self.all_faces():
            total += hi - lo
            if e:
                ext += hi - lo
        return ext / total if total else 0.0


@lru_cache(maxsize=4096)
def _faces_of(env: "Envelope") -> Tuple[Tuple[str, int, int, int, bool], ...]:
    """The real boundary of `env`, typed by its exposure preset.

    Walks unit edges rather than reasoning about notch positions, so it is
    correct for a notch anywhere on the boundary — including the mid-edge notch
    `u_shape_true` cuts, which is the one member of ADR 0003's rect/L/U/T family
    that adds perimeter. Cached: an Envelope is frozen and the solver asks for
    its faces once per model build.
    """
    W, H = env.W, env.H
    cell = [[env.contains(Rect(x, y, x + 1, y + 1)) for y in range(H)]
            for x in range(W)]

    def inside(x: int, y: int) -> bool:
        return 0 <= x < W and 0 <= y < H and cell[x][y]

    # Unit boundary edges, gathered per line and merged into maximal runs.
    runs: List[Tuple[str, int, int, int]] = []
    for x in range(W + 1):
        lo = None
        for y in range(H + 1):
            on = y < H and (inside(x - 1, y) != inside(x, y))
            if on and lo is None:
                lo = y
            elif not on and lo is not None:
                runs.append(("v", x, lo, y))
                lo = None
    for y in range(H + 1):
        lo = None
        for x in range(W + 1):
            on = x < W and (inside(x, y - 1) != inside(x, y))
            if on and lo is None:
                lo = x
            elif not on and lo is not None:
                runs.append(("h", y, lo, x))
                lo = None

    # Typing. A face on a bbox line takes the preset's exterior/party split for
    # that line; a face anywhere else is an internal notch face and takes the
    # typing of the notch it bounds. Both branches are `_bbox_runs`' and
    # `_notch_is_exterior`'s, unchanged — only the face set is new.
    ext_spans: dict = {}
    for (k, c, lo, hi, is_ext) in env._bbox_runs():
        ext_spans.setdefault((k, c), [])
        if is_ext:
            ext_spans[(k, c)].append((lo, hi))
    notch_ext = [(n, env._notch_is_exterior(n)) for n in env.notches]

    out: List[Tuple[str, int, int, int, bool]] = []
    for (k, c, lo, hi) in runs:
        if (k, c) in ext_spans:
            cuts = sorted({lo, hi}
                          | {max(lo, min(hi, a)) for (a, _) in ext_spans[(k, c)]}
                          | {max(lo, min(hi, b)) for (_, b) in ext_spans[(k, c)]})
            for a, b in zip(cuts, cuts[1:]):
                if b <= a:
                    continue
                e = any(a >= s and b <= t for (s, t) in ext_spans[(k, c)])
                out.append((k, c, a, b, e))
            continue
        e = False
        for n, is_ext in notch_ext:
            if not is_ext:
                continue
            on = (k == "v" and c in (n.x1, n.x2)) or (k == "h" and c in (n.y1, n.y2))
            if on:
                e = True
                break
        out.append((k, c, lo, hi, e))
    return tuple(out)


def l_shape(W: int, H: int, notch_w: int, notch_h: int) -> Tuple[Tuple[Rect, ...], Tuple[Rect, ...]]:
    """L-shaped Envelope: bbox minus the top-right corner."""
    notch = Rect(W - notch_w, H - notch_h, W, H)
    parts = (
        Rect(0, 0, W, H - notch_h),
        Rect(0, H - notch_h, W - notch_w, H),
    )
    return (notch,), parts


def u_shape(W: int, H: int, notch_w: int, notch_h: int, gap: int) -> Tuple[Tuple[Rect, ...], Tuple[Rect, ...]]:
    """Bbox minus two top **corner** notches separated by `gap` — a T, not a U.

    ⚠️ The name is inherited and the shape it builds is ADR 0003's **T**: both
    notches are anchored at a corner, so what is left is a wide base under a
    central tooth. Every notch here is a corner notch, and a corner notch
    removes area while adding **no perimeter at all** — this shape's boundary is
    exactly `2 * (W + H)`, its bounding box's. That is why `envelope_for` could
    not track a real dwelling's articulation at any notch share: see
    `u_shape_true` for the member of the family that can.
    """
    n1 = Rect(0, H - notch_h, notch_w, H)
    n2 = Rect(notch_w + gap, H - notch_h, W, H)
    parts = (
        Rect(0, 0, W, H - notch_h),
        Rect(notch_w, H - notch_h, notch_w + gap, H),
    )
    return (n1, n2), parts


def u_shape_true(W: int, H: int, notch_w: int, notch_h: int, offset: int) -> Tuple[Tuple[Rect, ...], Tuple[Rect, ...]]:
    """U-shaped Envelope: bbox minus **one mid-edge** notch on the N edge.

    ADR 0003 names rect, L, U and T. Until *The toy Envelope is more compact
    than a real dwelling* the generator emitted only rect, L and T — and the
    missing member is the only one that buys perimeter. A notch cut from the
    *middle* of an edge, rather than from a corner, leaves two re-entrant
    corners and lengthens the boundary by exactly `2 * notch_h` at zero extra
    area cost. That is the articulation a real dwelling has and a corner notch
    cannot express: measured over 2,238 Swiss dwellings, a real boundary runs
    6-12 % longer than its own bounding box and the excess rises with room
    count, while every corner-notched Envelope sits at exactly 0 %.

    `offset` is the notch's left edge; it must leave a tooth on both sides, so
    `0 < offset` and `offset + notch_w < W`.
    """
    if not (0 < offset and offset + notch_w < W):
        raise ValueError(
            f"u_shape_true needs a tooth each side: 0 < {offset} and "
            f"{offset + notch_w} < {W}")
    notch = Rect(offset, H - notch_h, offset + notch_w, H)
    parts = (
        Rect(0, 0, W, H - notch_h),
        Rect(0, H - notch_h, offset, H),
        Rect(offset + notch_w, H - notch_h, W, H),
    )
    return (notch,), parts


def tiling_defects(rooms: Sequence[Rect], env: Envelope) -> dict:
    """Independent check of a candidate Plan. Does not trust the solver.

    Rasterises at grid resolution and counts, per cell, how many rooms cover it.
    """
    counts = [[0] * env.H for _ in range(env.W)]
    for r in rooms:
        for x in range(max(0, r.x1), min(env.W, r.x2)):
            col = counts[x]
            for y in range(max(0, r.y1), min(env.H, r.y2)):
                col[y] += 1

    inside = 0
    uncovered = 0
    overlapped = 0
    outside_covered = 0
    for x in range(env.W):
        for y in range(env.H):
            c = counts[x][y]
            in_env = env.contains(Rect(x, y, x + 1, y + 1))
            if in_env:
                inside += 1
                if c == 0:
                    uncovered += 1
                elif c > 1:
                    overlapped += c - 1
            else:
                if c > 0:
                    outside_covered += c

    pairwise_overlap = 0
    for i in range(len(rooms)):
        for j in range(i + 1, len(rooms)):
            pairwise_overlap += rooms[i].overlap_area(rooms[j])

    total_room_area = sum(r.area for r in rooms)
    return {
        "interior_cells": inside,
        "uncovered_cells": uncovered,
        "double_covered_cells": overlapped,
        "cells_outside_envelope": outside_covered,
        "pairwise_overlap_area": pairwise_overlap,
        "overlap_pct_of_room_area": (
            100.0 * pairwise_overlap / total_room_area if total_room_area else 0.0
        ),
        "uncovered_pct_of_interior": 100.0 * uncovered / inside if inside else 0.0,
    }


def adjacency_matrix(rooms: Sequence[Rect], min_len: int) -> List[List[bool]]:
    n = len(rooms)
    m = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            adj = rooms[i].shared_edge_length(rooms[j]) >= min_len
            m[i][j] = m[j][i] = adj
    return m


def touches_exterior(r: Rect, env: Envelope, min_len: int) -> bool:
    for kind, coord, lo, hi in env.exterior_faces():
        if kind == "v":
            if r.x1 == coord or r.x2 == coord:
                seg = min(r.y2, hi) - max(r.y1, lo)
                if seg >= min_len:
                    return True
        else:
            if r.y1 == coord or r.y2 == coord:
                seg = min(r.x2, hi) - max(r.x1, lo)
                if seg >= min_len:
                    return True
    return False


def reachable_without_private(
    adj: Sequence[Sequence[bool]], entry: int, private: Iterable[int]
) -> Tuple[bool, List[int]]:
    """BFS from `entry`; a private room may be entered but never traversed."""
    priv = set(private)
    n = len(adj)
    seen = {entry}
    frontier = [entry]
    while frontier:
        nxt = []
        for u in frontier:
            if u in priv and u != entry:
                continue  # dead end: you do not walk through a bedroom
            for v in range(n):
                if adj[u][v] and v not in seen:
                    seen.add(v)
                    nxt.append(v)
        frontier = nxt
    return len(seen) == n, sorted(set(range(n)) - seen)


def connected(adj: Sequence[Sequence[bool]], nodes: Sequence[int]) -> bool:
    if not nodes:
        return True
    s = set(nodes)
    seen = {nodes[0]}
    frontier = [nodes[0]]
    while frontier:
        nxt = []
        for u in frontier:
            for v in s:
                if v not in seen and adj[u][v]:
                    seen.add(v)
                    nxt.append(v)
        frontier = nxt
    return len(seen) == len(s)
