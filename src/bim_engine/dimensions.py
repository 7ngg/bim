"""docs/spec/annotation.md section 4 -- the dimension ladder.

Four external tiers on rungs at fixed paper offsets outside the Envelope
bounding box, plus in-plan setting-out dimensions for internal openings. Rungs
are allocated outward in this order and a tier absent on a side consumes no rung:

    tier 3   10 mm paper   openings on this Envelope edge
    tier 2   18 mm paper   partition faces on walls reaching this side
    tier 2b  26 mm paper   running dimensions from datum, only if needed
    tier 1   26 or 34      overall footprint

EVERY TICK IS A REAL QUANTITY A PERSON CAN TAPE (ADR 0004, section 3). A tier-2
chain alternates room clear width, wall thickness, room clear width. There is no
centreline dimension anywhere on the sheet: ADR 0010 deleted ADR 0004's one
exception, and section 3.1 explains why tier 1 is nevertheless not the inner ring
on both edges.

EVERY CHAIN CLOSES. Segments sum exactly to the axis span, in integer
millimetres, and `check.chain_closes` asserts it. There is no rounding step at
which this can be lost.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from . import profile
from .model import Opening, Plan, RectMM
from .openings import shared_runs

RUNG_PAPER = {3: 10.0, 2: 18.0, "2b": 26.0, 1: 26.0}
RUNG_PAPER_TIER1_WITH_2B = 34.0

SIDES = ("S", "N", "W", "E")
#: which model axis a side's chain runs along
SIDE_AXIS = {"S": "x", "N": "x", "W": "y", "E": "y"}


@dataclass
class Chain:
    """One dimension chain. `points` are positions along `axis`, ascending."""
    tier: object
    side: str
    axis: str
    points: List[int]
    rung: float
    label: str = ""

    @property
    def segments(self) -> List[int]:
        return [b - a for a, b in zip(self.points, self.points[1:])]

    @property
    def span(self) -> int:
        return self.points[-1] - self.points[0]

    def closes(self, expected: int) -> bool:
        return sum(self.segments) == expected == self.span


@dataclass
class Running:
    """A tier-2b running dimension: from the Envelope inner face on the nearest
    side to one partition face that reaches no edge.

    TWO SIDES, AND CONFLATING THEM DRAWS NONSENSE. `datum_side` is the Envelope
    face the dimension is measured FROM -- W or E for an x-face, S or N for a
    y-face, whichever is nearer, which is what section 4.3 says. `rung_side` is
    where the dimension LINE is drawn, and a horizontal dimension can only go on
    a horizontal rung: x on S, y on W. The first version carried one field for
    both and drew an x-axis running on the E rung, which put a horizontal
    dimension line inside the plan at an x coordinate read as a y. Caught by
    eye on the first real dwelling, which is why the drawing exists.
    """
    datum_side: str
    axis: str
    frm: int
    to: int
    rung: float

    @property
    def rung_side(self) -> str:
        return "S" if self.axis == "x" else "W"

    @property
    def value(self) -> int:
        return abs(self.to - self.frm)


@dataclass
class SettingOut:
    """section 4.5 -- from the finished face of the perpendicular wall at the end
    the door is pushed to, to the near jamb of the structural opening.

    The value is 100 for every internal door in every plan, by construction from
    openings.md section 3.2, and it is dimensioned anyway: a reading of anything
    other than 100 means the placement and the drawing disagree, which is exactly
    the stale-block class of failure `draw.measurement_matches_model` exists for.
    """
    opening: Opening
    axis: str
    frm: int
    to: int
    offset_paper: float = 3.0

    @property
    def value(self) -> int:
        return abs(self.to - self.frm)


@dataclass
class Dimensions:
    chains: List[Chain] = field(default_factory=list)
    runnings: List[Running] = field(default_factory=list)
    setting_out: List[SettingOut] = field(default_factory=list)
    tier1_rung: float = RUNG_PAPER[1]


# ---------------------------------------------------------------------------
# Partition bands
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Band:
    axis: str                    # 'v' -> faces are x coordinates
    lo_face: int
    hi_face: int
    span: Tuple[int, int]        # extent along the wall


def partition_bands(plan: Plan) -> List[Band]:
    """Every internal wall body, merged per wall line.

    Built from the same shared runs the doors are placed on, so a partition the
    drawing dimensions and a partition a door sits in are the same object.
    """
    by_line: Dict[Tuple[str, Tuple[int, int]], List[Tuple[int, int]]] = {}
    for r in shared_runs(plan):
        by_line.setdefault((r.axis, r.across), []).append((r.lo, r.hi))
    out: List[Band] = []
    for (axis, across), spans in by_line.items():
        spans.sort()
        cur = list(spans[0])
        merged = []
        for lo, hi in spans[1:]:
            # Bridge a gap of exactly `t_int`: that gap is a PERPENDICULAR wall
            # crossing this one, and a wall crossed by another is still one
            # wall. Without this the long spine partition of annotation.md
            # section 14 arrives as four pieces, none of them reaching an
            # Envelope edge, and a plan whose tier 2b the spec computes as empty
            # gets four running dimensions it does not need.
            if lo <= cur[1] + profile.T_INT_MM:
                cur[1] = max(cur[1], hi)
            else:
                merged.append(tuple(cur))
                cur = [lo, hi]
        merged.append(tuple(cur))
        for span in merged:
            out.append(Band(axis, across[0], across[1], span))
    return out


def _slot_runnings(dims: "Dimensions", scale: int) -> None:
    """section 5(c), applied to tier 2b.

    Both faces of one un-reaching partition get their own running dimension
    (section 4.3), they are measured from the same datum, and they differ by
    `t_int` -- so their two texts land 75 mm apart in model space, which is 1,5
    paper millimetres at 1:50 and a guaranteed overlap. The spec's own rule for
    two in-plan dimensions crowding each other is that the second steps out one
    further increment, deterministically, and never drops. The same rule is
    applied here: each running takes the lowest sub-rung on which its text is
    clear, and tier 1 moves outboard of whatever that reaches.
    """
    by_side: Dict[str, List[Running]] = {}
    for r in dims.runnings:
        by_side.setdefault(r.rung_side, []).append(r)
    for rs in by_side.values():
        rs.sort(key=lambda r: (min(r.frm, r.to), r.to))
        slots: List[List[Tuple[float, float]]] = []
        for r in rs:
            mid = (r.frm + r.to) / 2.0 / scale
            half = len(str(r.value)) * 0.62 * 2.5 / 2.0 + 1.0
            iv = (mid - half, mid + half)
            for i, occ in enumerate(slots):
                if all(iv[1] <= o[0] or iv[0] >= o[1] for o in occ):
                    occ.append(iv)
                    r.rung = RUNG_PAPER["2b"] + i * 5.0
                    break
            else:
                slots.append([iv])
                r.rung = RUNG_PAPER["2b"] + (len(slots) - 1) * 5.0


# ---------------------------------------------------------------------------
# Tier 1 -- overall
# ---------------------------------------------------------------------------
def _side_is_exterior(plan: Plan, side: str) -> bool:
    """Whether the footprint on this side is measured to an outer face.

    section 3: to the OUTER face of an exterior edge and to the INNER face of a
    party edge -- a party wall's outer face lies inside the neighbour's home and
    cannot be taped from this dwelling. With a partial-exposure Envelope an edge
    can be part exterior and part party; the footprint is then still set out
    from the outermost wall face on that side, so any exterior run makes the
    side exterior. Stated because the spec's worked example has whole edges only.
    """
    return any(f.side == side and f.is_exterior for f in plan.faces)


def tier1(plan: Plan) -> Dict[str, int]:
    inner = plan.inner
    tw = profile.T_EXT_MM
    x = inner.w + (tw if _side_is_exterior(plan, "W") else 0) \
        + (tw if _side_is_exterior(plan, "E") else 0)
    y = inner.h + (tw if _side_is_exterior(plan, "S") else 0) \
        + (tw if _side_is_exterior(plan, "N") else 0)
    return {"S": x, "N": x, "W": y, "E": y}


# ---------------------------------------------------------------------------
# The whole ladder
# ---------------------------------------------------------------------------
def derive(plan: Plan, scale: int = 50) -> Dimensions:
    inner = plan.inner
    dims = Dimensions()
    bands = partition_bands(plan)

    reached: Dict[int, bool] = {}
    tier2: Dict[str, List[int]] = {s: [] for s in SIDES}
    for idx, b in enumerate(bands):
        touched = []
        if b.axis == "v":
            if b.span[0] == inner.y1:
                touched.append("S")
            if b.span[1] == inner.y2:
                touched.append("N")
        else:
            if b.span[0] == inner.x1:
                touched.append("W")
            if b.span[1] == inner.x2:
                touched.append("E")
        for side in touched:
            tier2[side].extend([b.lo_face, b.hi_face])
        reached[idx] = bool(touched)

    # --- tier 2, one chain per side, each closing on its axis ---------------
    for side in SIDES:
        axis = SIDE_AXIS[side]
        lo = inner.x1 if axis == "x" else inner.y1
        hi = inner.x2 if axis == "x" else inner.y2
        pts = sorted(set([lo, hi] + tier2[side]))
        dims.chains.append(Chain(2, side, axis, pts, RUNG_PAPER[2]))

    # --- tier 2b, everything that reaches no edge --------------------------
    for idx, b in enumerate(bands):
        if reached[idx]:
            continue
        axis = "x" if b.axis == "v" else "y"
        lo = inner.x1 if axis == "x" else inner.y1
        hi = inner.x2 if axis == "x" else inner.y2
        for face in (b.lo_face, b.hi_face):
            near_lo = (face - lo) <= (hi - face)
            side = ("W" if axis == "x" else "S") if near_lo else \
                   ("E" if axis == "x" else "N")
            dims.runnings.append(Running(side, axis, lo if near_lo else hi,
                                         face, RUNG_PAPER["2b"]))
    if dims.runnings:
        _slot_runnings(dims, scale)
        dims.tier1_rung = max(r.rung for r in dims.runnings) + 8.0

    # --- tier 3, openings on each Envelope edge ----------------------------
    for side in SIDES:
        axis = SIDE_AXIS[side]
        lo = inner.x1 if axis == "x" else inner.y1
        hi = inner.x2 if axis == "x" else inner.y2
        jambs: List[int] = []
        for op in plan.openings:
            if _opening_side(plan, op) != side:
                continue
            jambs.extend([op.p1, op.p2])
        if not jambs:
            continue
        pts = sorted(set([lo, hi] + jambs))
        dims.chains.append(Chain(3, side, axis, pts, RUNG_PAPER[3]))

    # --- tier 1, one per side, all four ------------------------------------
    t1 = tier1(plan)
    for side in SIDES:
        axis = SIDE_AXIS[side]
        lo = inner.x1 if axis == "x" else inner.y1
        dims.chains.append(Chain(1, side, axis, [lo, lo + t1[side]],
                                 dims.tier1_rung, label="overall"))

    # --- internal setting-out, section 4.5 ---------------------------------
    for op in plan.openings:
        if op.kind == "window" or op.other is None:
            continue
        axis = "y" if op.axis == "v" else "x"
        near = op.p1 if op.datum is not None and abs(op.p1 - op.datum) <= \
            abs(op.p2 - op.datum) else op.p2
        dims.setting_out.append(SettingOut(op, axis, op.datum, near))
    return dims


def _opening_side(plan: Plan, op: Opening) -> Optional[str]:
    """Which side an Envelope-hosted Opening faces. `None` for an internal one,
    which is dimensioned in plan instead (section 4.5).

    READ OFF THE HOSTING SPACE, NOT OFF THE BBOX. section 4.4 says one chain per
    Envelope edge, and its worked example has a rectangular Envelope where an
    edge and a bbox line are the same thing. A real dwelling is a bbox minus
    notches (ADR 0003), so a window can sit on a notch reveal that lies on no
    bbox line at all -- and a bbox test then silently drops it from every chain,
    which `draw.every_opening_positioned` catches and which is how this was
    found. The side is the direction the opening faces: the wall is west of its
    room, or east of it, and that is true on a notch reveal as much as on the
    perimeter.
    """
    if op.other is not None:
        return None
    ref = op.host_space or op.receiving
    if ref is None:
        return None
    a, b = op.across
    for r in plan.by_ref(ref).parts:
        if op.axis == "v":
            if r.x1 == b:
                return "W"
            if r.x2 == a:
                return "E"
        else:
            if r.y1 == b:
                return "S"
            if r.y2 == a:
                return "N"
    return None


def opening_side(plan: Plan, op: Opening) -> Optional[str]:
    return _opening_side(plan, op)
