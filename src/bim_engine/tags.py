"""docs/spec/annotation.md section 7 -- room tags, and section 7.2's fraction.

Placement is the centroid of the Space's LARGEST CONSTITUENT RECTANGLE, and the
distinction is not pedantry: ADR 0014 makes a Space up to two rectangles, and
for a 6,0 x 1,2 m leg with a 1,2 x 6,0 m return the Space centroid lands outside
its own Space, in the notch, which belongs to a different room -- so the tag
would name the neighbour. The larger part's centroid is inside by construction.

NO LINE OF THE TAG IS EVER DROPPED. The small rooms are the ones whose area is
contested, and a plan whose 4 m2 store carries no area while its 16 m2 living
room does is a plan someone will query. It is leadered out instead.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

from . import fmt, profile
from .model import Plan, Space

#: ISO 3098 sizes only. A drawing using arbitrary text heights looks wrong
#: before it is read. section 9.
TEXT_NAME = 3.5
TEXT_BODY = 2.5
TEXT_FLOOR = 1.8


@dataclass
class Tag:
    """One Space's tag. `lines` is what is drawn, top to bottom."""
    ref: str
    at: Tuple[float, float]
    lines: List[str]
    name_height: float = TEXT_NAME
    body_height: float = TEXT_BODY
    underline_lines: Tuple[int, ...] = (0,)
    leadered: bool = False
    step: int = 0                 # which rung of the degradation ladder fired


def tag_lines(space: Space, audience: str = "practitioner") -> List[str]:
    """Name, area, clear dimensions, reference -- and the dimensions line
    carries BOTH legs, never the bounding box: a bbox claims floor area the
    Room does not have, next to an area figure that does not include it."""
    return [space.name_az.upper(),
            fmt.area_m2(space.area_m2),
            fmt.legs([(p.w, p.h) for p in space.parts]),
            "[%s]" % space.ref]


def _text_extent(lines, name_h, body_h, scale) -> Tuple[float, float]:
    """Model-space extent of a tag block. Width is estimated at 0,62 of the
    glyph height a character, which is the ratio a normal-width ISO 3098 face
    runs at; it is used only to decide whether the tag FITS, and a tag that is
    judged too wide degrades rather than overlapping."""
    heights = [name_h] + [body_h] * (len(lines) - 1)
    w = max(len(t) * 0.62 * h for t, h in zip(lines, heights))
    h = sum(heights) * 1.45
    return w * scale, h * scale


def obstacles_for(plan: Plan, dims, scale: int) -> List[Tuple[float, float, float, float]]:
    """Everything inside the plan a tag has to stay clear of, in MODEL mm.

    section 7's ladder says "clear of walls, openings and in-plan dimensions",
    and the first version read only the walls -- it sized the tag against its
    Space and stopped. `draw.no_text_overlap` then failed on a real dwelling
    with `tag R03 overlaps mark 4`, which is the predicate doing its job and the
    ladder not doing its own.
    """
    out = []
    for op in plan.openings:
        a, b = op.across
        across = (a + b) / 2.0
        along = (op.p1 + op.p2) / 2.0
        d = -1 if op.swing_side == "lo" else +1
        rr = 2.5 * scale
        if op.axis == "v":
            cx, cy = across + d * 8.0 * scale, along
        else:
            cx, cy = along, across + d * 8.0 * scale
        out.append((cx - rr, cy - rr, cx + rr, cy + rr))
        # the leaf and its arc sweep real paper, and a tag over a swing reads as
        # a mistake even where it is legible
        lw = op.leaf_w
        if lw:
            hinge = op.p1 if op.hinge_end == "lo" else op.p2
            face = a if op.swing_side == "lo" else b
            lo_a, hi_a = sorted((hinge, hinge + (lw if op.hinge_end == "lo" else -lw)))
            lo_c, hi_c = sorted((face, face + (-lw if op.swing_side == "lo" else lw)))
            if op.axis == "v":
                out.append((lo_c, lo_a, hi_c, hi_a))
            else:
                out.append((lo_a, lo_c, hi_a, hi_c))
    for so in (dims.setting_out if dims else []):
        op = so.opening
        a, b = op.across
        face = a if op.swing_side == "lo" else b
        sign = -1 if op.swing_side == "lo" else +1
        mid = (so.frm + so.to) / 2.0
        w = len(str(so.value)) * 0.62 * 1.8 * scale
        h = 1.8 * scale
        if op.axis == "v":
            cx, cy = face + sign * 10.0 * scale, mid
        else:
            cx, cy = mid, face + sign * 10.0 * scale
        out.append((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
    return out


def _clear(box, obstacles) -> bool:
    x0, y0, x1, y1 = box
    for o in obstacles:
        if x0 < o[2] and o[0] < x1 and y0 < o[3] and o[1] < y1:
            return False
    return True


def place(plan: Plan, scale: int = 50, audience: str = "practitioner",
          obstacles: Optional[List] = None) -> List[Tag]:
    """The section 7 ladder, in its fixed order, until the tag fits its Space
    with a one-text-height margin clear of walls, openings and in-plan
    dimensions.

        1. name 3,5 -> 2,5
        2. substitute the schedule reference for the name  (practitioner)
           -- or, on the Homeowner preview, SKIP TO 4, because the room schedule
           is `practitioner` and a bare number would point at a document that
           presentation filters out (section 7.1)
        3. name and body to 1,8, the ISO 3098 legibility floor
        4. leader the whole tag into the margin column
    """
    obstacles = obstacles or []
    out: List[Tag] = []
    for s in plan.spaces:
        box = s.primary
        at = box.centroid
        lines = tag_lines(s, audience)
        rungs = [(TEXT_NAME, TEXT_BODY, lines, 0),
                 (TEXT_BODY, TEXT_BODY, lines, 1)]
        if audience == "practitioner":
            rungs.append((TEXT_BODY, TEXT_BODY,
                          ["[%s]" % s.ref] + lines[1:], 2))
        rungs.append((TEXT_FLOOR, TEXT_FLOOR, lines, 3))
        placed = None
        for name_h, body_h, ls, step in rungs:
            w, h = _text_extent(ls, name_h, body_h, scale)
            margin = name_h * scale
            extent = (at[0] - w / 2, at[1] - h / 2, at[0] + w / 2, at[1] + h / 2)
            if (w + margin <= box.w and h + margin <= box.h
                    and _clear(extent, obstacles)):
                placed = Tag(s.ref, at, ls, name_h, body_h, step=step)
                break
        if placed is None:
            placed = Tag(s.ref, at, lines, TEXT_BODY, TEXT_BODY,
                         leadered=True, step=4)
        out.append(placed)
    return out


@dataclass
class AreaFraction:
    """section 7.2 -- `AZS ГОСТ 21.501-2010` cl. 2.3.2 annotates a residential
    plan's area AS A FRACTION, living over useful. Dwelling level, one per plan,
    audience `practitioner`."""
    numerator: str
    denominator: str
    numerator_label: str = "yaşayış sahəsi"
    denominator_label: str = "faydalı sahə"


def area_fraction(plan: Plan) -> AreaFraction:
    """Both quantities come off the model, and the denominator is the room
    schedule's own printed total so the two cannot disagree on the sheet."""
    printed = sum(fmt.parse_back(fmt.area_cell(s.area_m2)) for s in plan.spaces)
    hab = sum(fmt.parse_back(fmt.area_cell(s.area_m2))
              for s in plan.spaces if s.is_habitable)
    return AreaFraction(fmt.area_cell(hab), fmt.area_cell(printed))
