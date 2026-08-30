"""docs/spec/annotation.md section 11 -- the DXF.

THREE TRAPS, ALL NAMED IN THE SPEC AND ALL AVOIDED HERE.

1. `setup_dimstyle(fmt="EZ_M_50_H25_CM")` copies the template's `DIMLFAC = 100.0`
   and prints a 4000 mm wall as `400000`. The style is built explicitly instead.
2. `add_multi_point_linear_dim` renders internally and returns `None`, so there
   is no handle to place text on and none to key an override to. Every chain is
   authored segment by segment with `add_linear_dim(base=...)` sharing one base
   line, and `.render()` is called on each -- authoring and rendering are ONE
   atomic step, or the drawn block and the semantic measurement disagree.
   `avoid_double_rendering` is lost with the factory method and is reproduced
   exactly: every segment after the first sets `dimse1 = 1`.
3. R2000 cannot encode the Azerbaijani alphabet -- no legacy code page anywhere
   encodes `ə`, not even Turkish cp1254 -- so the document is R2010, and the
   text style names a TrueType font because every stock SHX font lacks the
   letters too. Those are two different problems and the second is not solved by
   the first.

Layers stay US NCS / AIA while the sheet does not. A sheet mark is read on paper
by a builder; a layer name is read on import by a program, and AutoCAD, Revit and
ArchiCAD all ship NCS/AIA templates. ADR 0024.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import ezdxf
from ezdxf import const

from . import check as check_mod
from . import fmt, profile, schedules, sheet as sheet_mod
from .dimensions import Chain, Dimensions, Running, SettingOut
from .model import Opening, Plan

#: section 2's hierarchy. DXF lineweights are an enumerated set in 1/100 mm and
#: every value here is in it -- an arbitrary 45 is not, and would be snapped.
LAYERS = {
    "A-WALL":       (7, 50),
    "A-WALL-PATT":  (8, 9),
    "A-DOOR":       (7, 25),
    "A-GLAZ":       (7, 25),
    "A-ANNO-DIMS":  (7, 13),
    "A-ANNO-TEXT":  (7, 18),
    "A-ANNO-TTLB":  (7, 18),
}
VALID_LINEWEIGHTS = {0, 5, 9, 13, 15, 18, 20, 25, 30, 35, 40, 50, 53, 60, 70,
                     80, 90, 100, 106, 120, 140, 158, 200, 211}

TEXT_STYLE = "ARCH-AZ"
FONT = "arial.ttf"          # a TrueType face; every stock SHX lacks `ə`


def _dimstyle_name(scale: int) -> str:
    return "ARCH-MM-%d" % scale


def new_document(scale: int):
    doc = ezdxf.new("R2010", setup=False)
    doc.header["$INSUNITS"] = 4          # millimetres
    doc.header["$MEASUREMENT"] = 1       # metric
    doc.header["$LWDISPLAY"] = 1         # or none of the hierarchy displays
    doc.header["$DIMASSOC"] = 2
    doc.header["$PSVPSCALE"] = 0

    doc.styles.add(TEXT_STYLE, font=FONT)
    for name, (color, lw) in LAYERS.items():
        doc.layers.add(name, color=color, lineweight=lw)

    s = doc.dimstyles.add(_dimstyle_name(scale))
    s.dxf.dimlfac = 1.0          # drawing units ARE millimetres
    s.dxf.dimscale = float(scale)
    s.dxf.dimtxt = 2.5
    s.dxf.dimasz = 2.5
    s.dxf.dimexe = 1.25
    s.dxf.dimexo = 0.625
    s.dxf.dimgap = 0.625
    s.dxf.dimdec = 0             # whole millimetres
    s.dxf.dimtad = 1             # text above the line
    s.dxf.dimblk = "ARCHTICK"
    s.dxf.dimatfit = 2           # move text out first; ticks stay put
    s.dxf.dimtmove = 1           # add a leader when text is moved
    s.dxf.dimtofl = 1
    s.dxf.dimtix = 0
    s.dxf.dimdsep = ord(profile.decimal_separator())
    s.dxf.dimtxsty = TEXT_STYLE
    return doc


# ---------------------------------------------------------------------------
# Model space
# ---------------------------------------------------------------------------
def _poche(msp, region):
    geoms = [region] if region.geom_type == "Polygon" else list(region.geoms)
    for g in geoms:
        hatch = msp.add_hatch(color=8, dxfattribs={"layer": "A-WALL-PATT"})
        hatch.set_solid_fill()
        hatch.paths.add_polyline_path(
            [(x, y) for x, y in g.exterior.coords], is_closed=True,
            flags=const.BOUNDARY_PATH_EXTERNAL)
        for r in g.interiors:
            hatch.paths.add_polyline_path(
                [(x, y) for x, y in r.coords], is_closed=True,
                flags=const.BOUNDARY_PATH_DEFAULT)
        msp.add_lwpolyline([(x, y) for x, y in g.exterior.coords], close=True,
                           dxfattribs={"layer": "A-WALL"})
        for r in g.interiors:
            msp.add_lwpolyline([(x, y) for x, y in r.coords], close=True,
                               dxfattribs={"layer": "A-WALL"})


def _door(msp, op: Opening):
    a, b = op.across
    lay = {"layer": "A-DOOR"}
    if op.axis == "v":
        msp.add_line((a, op.p1), (b, op.p1), dxfattribs=lay)
        msp.add_line((a, op.p2), (b, op.p2), dxfattribs=lay)
    else:
        msp.add_line((op.p1, a), (op.p1, b), dxfattribs=lay)
        msp.add_line((op.p2, a), (op.p2, b), dxfattribs=lay)
    if op.kind == "cased_opening" or op.leaf_w is None:
        return                     # no leaf and no arc: that is what makes it
                                   # legible as a cased opening
    lw = op.leaf_w
    hinge_along = op.p1 if op.hinge_end == "lo" else op.p2
    face = a if op.swing_side == "lo" else b
    s_across = -1 if op.swing_side == "lo" else +1
    s_along = +1 if op.hinge_end == "lo" else -1
    if op.axis == "v":
        hx, hy = face, hinge_along
        tip = (hx + s_across * lw, hy)
        start = 0.0 if s_across > 0 else 180.0
        end = 90.0 if s_along > 0 else 270.0
    else:
        hx, hy = hinge_along, face
        tip = (hx, hy + s_across * lw)
        start = 90.0 if s_across > 0 else 270.0
        end = 0.0 if s_along > 0 else 180.0
    msp.add_line((hx, hy), tip, dxfattribs=lay)
    t1, t2 = sorted((start, end))
    if t2 - t1 > 180:
        t1, t2 = t2, t1 + 360
    msp.add_arc(center=(hx, hy), radius=lw, start_angle=t1, end_angle=t2,
                dxfattribs=lay)


def _window(msp, op: Opening):
    a, b = op.across
    mid = (a + b) / 2.0
    lay = {"layer": "A-GLAZ"}
    if op.axis == "v":
        msp.add_lwpolyline([(a, op.p1), (b, op.p1), (b, op.p2), (a, op.p2)],
                           close=True, dxfattribs=lay)
        msp.add_line((mid, op.p1), (mid, op.p2), dxfattribs=lay)
    else:
        msp.add_lwpolyline([(op.p1, a), (op.p1, b), (op.p2, b), (op.p2, a)],
                           close=True, dxfattribs=lay)
        msp.add_line((op.p1, mid), (op.p2, mid), dxfattribs=lay)


def _mark(msp, op: Opening, plan: Plan, scale: int):
    """A Ø 5 mm paper circle -- `AZS ГОСТ 21.501-2010` cl. 2.3.2(4), which fixes
    5 where the RF 2018 edition widens it to 5-7. The Azerbaijani edition is the
    operative one."""
    a, b = op.across
    across = (a + b) / 2.0
    along = (op.p1 + op.p2) / 2.0
    off = 8.0 * scale
    inner = plan.inner
    if op.other is None:
        d = -1 if (b <= (inner.x1 if op.axis == "v" else inner.y1)) else +1
    else:
        d = -1 if op.swing_side == "lo" else +1
    if op.axis == "v":
        cx, cy = across + d * off, along
    else:
        cx, cy = along, across + d * off
    msp.add_circle((cx, cy), radius=2.5 * scale,
                   dxfattribs={"layer": "A-ANNO-TEXT"})
    msp.add_text(op.mark, height=1.8 * scale,
                 dxfattribs={"layer": "A-ANNO-TEXT", "style": TEXT_STYLE}
                 ).set_placement((cx, cy), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)


def _tag(msp, tag, scale: int, at=None):
    r"""One MTEXT, attachment point 5 (middle-centre), `\P` breaks."""
    text = r"\P".join(tag.lines)
    mt = msp.add_mtext(text, dxfattribs={"layer": "A-ANNO-TEXT",
                                         "style": TEXT_STYLE,
                                         "char_height": tag.body_height * scale})
    mt.set_location(at or tag.at, attachment_point=5)


def _leadered_tag(msp, tag, scale: int, at):
    """section 7 step 4. Drawn as a LINE plus the same MTEXT rather than as a
    MULTILEADER: a MULTILEADER carries its own style, arrowhead and landing, and
    a wrong one of those is a worse defect than a plain leader line. The
    geometry a builder reads is identical and nothing downstream keys off the
    entity type."""
    msp.add_line(tag.at, at, dxfattribs={"layer": "A-ANNO-DIMS"})
    _tag(msp, tag, scale, at=at)


def _chain(msp, plan: Plan, ch: Chain, foot_bounds, scale: int, dimstyle: str):
    """Authored segment by segment, one shared base line, `.render()` on each."""
    fx0, fy0, fx1, fy1 = foot_bounds
    inner = plan.inner
    off = ch.rung * scale
    horizontal = ch.axis == "x"
    if ch.side == "S":
        base, ref = (0, fy0 - off), inner.y1
    elif ch.side == "N":
        base, ref = (0, fy1 + off), inner.y2
    elif ch.side == "W":
        base, ref = (fx0 - off, 0), inner.x1
    else:
        base, ref = (fx1 + off, 0), inner.x2
    angle = 0.0 if horizontal else 90.0
    made = []
    for i, (a, b) in enumerate(zip(ch.points, ch.points[1:])):
        p1 = (a, ref) if horizontal else (ref, a)
        p2 = (b, ref) if horizontal else (ref, b)
        override = {"dimse1": 1} if i else {}
        dim = msp.add_linear_dim(base=base, p1=p1, p2=p2, angle=angle,
                                 dimstyle=dimstyle, override=override,
                                 dxfattribs={"layer": "A-ANNO-DIMS"})
        dim.render()
        made.append((dim, b - a))
    return made


def _running(msp, plan: Plan, r: Running, foot_bounds, scale: int, dimstyle: str):
    fx0, fy0, fx1, fy1 = foot_bounds
    inner = plan.inner
    off = r.rung * scale
    horizontal = r.axis == "x"
    if r.rung_side == "S":
        base, ref = (0, fy0 - off), inner.y1
    elif r.rung_side == "N":
        base, ref = (0, fy1 + off), inner.y2
    elif r.rung_side == "W":
        base, ref = (fx0 - off, 0), inner.x1
    else:
        base, ref = (fx1 + off, 0), inner.x2
    p1 = (r.frm, ref) if horizontal else (ref, r.frm)
    p2 = (r.to, ref) if horizontal else (ref, r.to)
    dim = msp.add_linear_dim(base=base, p1=p1, p2=p2,
                             angle=0.0 if horizontal else 90.0,
                             dimstyle=dimstyle,
                             dxfattribs={"layer": "A-ANNO-DIMS"})
    dim.render()
    return dim


def _setting_out(msp, so: SettingOut, scale: int, dimstyle: str):
    op = so.opening
    a, b = op.across
    face = a if op.swing_side == "lo" else b
    sign = -1 if op.swing_side == "lo" else +1
    off = 3.0 * scale
    if op.axis == "v":
        base = (face + sign * off, 0)
        p1, p2 = (face, so.frm), (face, so.to)
        angle = 90.0
    else:
        base = (0, face + sign * off)
        p1, p2 = (so.frm, face), (so.to, face)
        angle = 0.0
    dim = msp.add_linear_dim(base=base, p1=p1, p2=p2, angle=angle,
                             dimstyle=dimstyle,
                             dxfattribs={"layer": "A-ANNO-DIMS"})
    dim.render()
    return dim


# ---------------------------------------------------------------------------
# Paper space
# ---------------------------------------------------------------------------
def _title_block(doc):
    """A BLOCK with ATTDEFs, so sheet metadata stays editable downstream instead
    of being burned into geometry."""
    blk = doc.blocks.new(name="TITLEBLOCK")
    strip, h = sheet_mod.TITLE_STRIP, 58.0
    blk.add_lwpolyline([(0, 0), (strip, 0), (strip, h), (0, h)], close=True,
                       dxfattribs={"layer": "A-ANNO-TTLB"})
    rows = [("PROJECT", 3.5), ("DRAWING", 5.0), ("SHEET", 3.5), ("SCALE", 2.5),
            ("SIZE", 2.5), ("REV", 2.5), ("DATE", 2.5), ("DRAWN", 2.5),
            ("CHECKED", 2.5), ("STATUS", 2.5), ("CLIENT", 2.5),
            ("UNITS", 1.8), ("DIM-CONV", 1.8), ("AREAS", 1.8)]
    y = h - 5.0
    for tag, size in rows:
        blk.add_attdef(tag=tag, text=tag, height=size,
                       dxfattribs={"layer": "A-ANNO-TTLB", "style": TEXT_STYLE}
                       ).set_placement((2.0, y))
        y -= size + 1.6
    return blk


def _paper(doc, plan: Plan, sh, attribs: Dict[str, str], notes: List[str],
           foot_bounds, name: str, n: int):
    layout = doc.layouts.new(name) if name not in doc.layouts.names() \
        else doc.layout(name)
    layout.page_setup(size=(sh.width, sh.height), margins=(0, 0, 0, 0),
                      units="mm")
    M = sheet_mod.MARGIN
    layout.add_lwpolyline([(M, M), (sh.width - M, M),
                           (sh.width - M, sh.height - M), (M, sh.height - M)],
                          close=True, dxfattribs={"layer": "A-ANNO-TTLB"})
    x0 = sh.width - M - sheet_mod.TITLE_STRIP
    layout.add_line((x0, M), (x0, sh.height - M),
                    dxfattribs={"layer": "A-ANNO-TTLB"})
    ref = layout.add_blockref("TITLEBLOCK", insert=(x0, M),
                              dxfattribs={"layer": "A-ANNO-TTLB"})
    ref.add_auto_attribs(attribs)

    y = sh.height - M - 6
    if not notes:
        return layout                      # sheet 2 carries no general notes
    layout.add_text("QEYDLƏR", height=3.5,
                    dxfattribs={"layer": "A-ANNO-TEXT", "style": TEXT_STYLE}
                    ).set_placement((M + 3, y))
    y -= 6
    for note in notes:
        layout.add_mtext(note, dxfattribs={"layer": "A-ANNO-TEXT",
                                           "style": TEXT_STYLE,
                                           "char_height": 1.8,
                                           "width": 70.0}
                         ).set_location((M + 3, y), attachment_point=1)
        y -= 3.4 * (1 + len(note) // 70)
    return layout


def _viewport(layout, sh, foot_bounds):
    """Viewport scale is `view_height / viewport_height`, set explicitly -- there
    is no annotative-scale plumbing and `$PSVPSCALE` stays 0 (section 9)."""
    fx0, fy0, fx1, fy1 = foot_bounds
    M = sheet_mod.MARGIN
    pw, ph = sh.printable
    layout.add_viewport(
        center=(M + pw / 2, M + ph / 2),
        size=(pw, ph),
        view_center_point=((fx0 + fx1) / 2, (fy0 + fy1) / 2),
        view_height=ph * sh.scale)


# ---------------------------------------------------------------------------
# The whole file
# ---------------------------------------------------------------------------
def write(plan: Plan, dims: Dimensions, tag_list, sh, wall_region, foot,
          attribs1: Dict[str, str], attribs2: Dict[str, str],
          notes: List[str], path: str, enforce: bool = True):
    """Author the file, run the section 13 check on it, and only then save.

    The order is the whole point: the check runs against the ezdxf document that
    is about to be written, so `measurement_matches_model` is comparing the
    rendered block against the model rather than against the intention.
    """
    doc = new_document(sh.scale)
    ds = _dimstyle_name(sh.scale)
    msp = doc.modelspace()
    bounds = foot.bounds

    _poche(msp, wall_region)
    for op in plan.openings:
        (_window if op.kind == "window" else _door)(msp, op)
        _mark(msp, op, plan, sh.scale)
    col_x = bounds[2] + (sheet_mod.outermost_rung(dims) + 12.0) * sh.scale
    col_y = bounds[3]
    for t in tag_list:
        if t.leadered:
            _leadered_tag(msp, t, sh.scale, (col_x, col_y))
            col_y -= (len(t.lines) * t.body_height * 1.45 + 3.0) * sh.scale
        else:
            _tag(msp, t, sh.scale)
    authored = []
    for ch in dims.chains:
        authored.extend(_chain(msp, plan, ch, bounds, sh.scale, ds))
    for r in dims.runnings:
        authored.append((_running(msp, plan, r, bounds, sh.scale, ds), r.value))
    for so in dims.setting_out:
        authored.append((_setting_out(msp, so, sh.scale, ds), so.value))

    # section 7.2's fraction is a dwelling-level annotation and belongs OUTSIDE
    # the ladder, not over the plan: placing it on the inner ring put it in the
    # north party wall, which the DXF read-back showed immediately.
    frac_x = plan.inner.x1
    frac_y = bounds[1] - (sheet_mod.outermost_rung(dims) + 14.0) * sh.scale
    from . import tags as tags_mod
    fr = tags_mod.area_fraction(plan)
    msp.add_mtext("%s  %s\\P%s  %s" % (fr.numerator_label, fr.numerator,
                                       fr.denominator_label, fr.denominator),
                  dxfattribs={"layer": "A-ANNO-TEXT", "style": TEXT_STYLE,
                              "char_height": 2.5 * sh.scale}
                  ).set_location((frac_x, frac_y), attachment_point=1)

    _title_block(doc)
    l1 = _paper(doc, plan, sh, attribs1, notes, bounds, "Sheet 1", 1)
    _viewport(l1, sh, bounds)
    l2 = _paper(doc, plan, sh, attribs2, [], bounds, "Sheet 2", 2)
    _schedules(l2, plan, sh)

    # The set is TWO sheets (section 1). ezdxf seeds a `Layout1`, and an empty
    # third tab in a set an architect issues is the tell of an export rather
    # than a drawing.
    if "Layout1" in doc.layouts.names():
        doc.layouts.delete("Layout1")

    report = check_mod.run(plan, dims, tag_list, sh, doc=doc, authored=authored)
    if enforce:
        check_mod.enforce(report)
    doc.saveas(path)
    return path, report


def _schedules(layout, plan: Plan, sh):
    """ezdxf has no `ACAD_TABLE` entity, so a schedule is composed from
    `LWPOLYLINE` rules and `MTEXT` cells. That is a table layout component to
    build; it is not a reason to omit the schedules -- and it is the single
    thing the competitive scan found NO vendor documents at all."""
    M = sheet_mod.MARGIN
    x = M + 6
    width = sh.width - 2 * M - sheet_mod.TITLE_STRIP - 12
    y = sh.height - M - 12
    for table in (schedules.door_schedule(plan),
                  schedules.window_schedule(plan),
                  schedules.room_schedule(plan)):
        y = _table(layout, table, x, y, width)
        y -= 10


def _table(layout, table, x: float, y: float, width: float) -> float:
    layout.add_text(table.title, height=3.5,
                    dxfattribs={"layer": "A-ANNO-TTLB", "style": TEXT_STYLE}
                    ).set_placement((x, y))
    y -= 7
    cols = list(zip(*([table.headers] + table.rows))) if table.rows else \
        [(h,) for h in table.headers]
    raw = [max(len(str(c)) for c in col) for col in cols]
    total = sum(raw) or 1
    widths = [max(14.0, width * r / total) for r in raw]

    layout.add_lwpolyline([(x, y), (x + width, y)],
                          dxfattribs={"layer": "A-ANNO-TTLB",
                                      "const_width": 0.25})
    cx = x
    for h, w in zip(table.headers, widths):
        layout.add_text(str(h), height=2.5,
                        dxfattribs={"layer": "A-ANNO-TEXT", "style": TEXT_STYLE}
                        ).set_placement((cx + 1.5, y - 4.5))
        cx += w
    y -= 7
    layout.add_lwpolyline([(x, y), (x + width, y)],
                          dxfattribs={"layer": "A-ANNO-TTLB",
                                      "const_width": 0.25})
    for row in table.rows:
        cx = x
        for cell, w in zip(row, widths):
            layout.add_text(str(cell), height=2.5,
                            dxfattribs={"layer": "A-ANNO-TEXT",
                                        "style": TEXT_STYLE}
                            ).set_placement((cx + 1.5, y - 4.4))
            cx += w
        y -= 6
        layout.add_lwpolyline([(x, y), (x + width, y)],
                              dxfattribs={"layer": "A-ANNO-DIMS"})
    for note in table.notes:
        y -= 5
        layout.add_mtext(note, dxfattribs={"layer": "A-ANNO-TEXT",
                                           "style": TEXT_STYLE,
                                           "char_height": 1.8,
                                           "width": width}
                         ).set_location((x, y), attachment_point=1)
        y -= 4
    return y
