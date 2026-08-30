"""A rendered sheet you can look at, from the same derivation the DXF uses.

Not a second annotation engine. Everything drawn here comes from `openings`,
`dimensions`, `tags`, `schedules` and `sheet` -- this module owns pen widths and
nothing else. If the PNG and the DXF ever disagree, one of them is reading the
model wrong, and that is the point of having both.

The eager preview renders the `both` audience; the sheet renders everything
(annotation.md section 1).
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Arc, Circle, Polygon as MplPoly, Rectangle

from . import fmt, openings as op_mod, profile, schedules, sheet as sheet_mod, tags as tags_mod
from .dimensions import Chain, Dimensions, Running, SettingOut, opening_side
from .model import Opening, Plan

#: annotation.md section 2's hierarchy, in millimetres of pen.
LW = {"wall": 0.50, "frame": 0.25, "leaf": 0.18, "dim": 0.13, "text": 0.18,
      "ttlb": 0.18, "patt": 0.09}
PT = 2.834645          # points per millimetre


def _lw(key: str) -> float:
    return LW[key] * PT


class Pen:
    """Paper-space drawing. Model millimetres in, paper millimetres out."""

    def __init__(self, ax, scale: int, ox: float, oy: float):
        self.ax, self.scale, self.ox, self.oy = ax, scale, ox, oy

    def p(self, x: float, y: float) -> Tuple[float, float]:
        return (self.ox + x / self.scale, self.oy + y / self.scale)

    def poly(self, ring, holes=(), **kw):
        pts = [self.p(*c) for c in ring]
        self.ax.add_patch(MplPoly(pts, closed=True, **kw))
        for h in holes:
            self.ax.add_patch(MplPoly([self.p(*c) for c in h], closed=True,
                                      facecolor="white", edgecolor="none",
                                      zorder=kw.get("zorder", 1) + 0.1))

    def line(self, x1, y1, x2, y2, w="dim", **kw):
        a, b = self.p(x1, y1), self.p(x2, y2)
        self.ax.add_line(Line2D([a[0], b[0]], [a[1], b[1]],
                                linewidth=_lw(w), solid_capstyle="butt", **kw))

    def paper_line(self, x1, y1, x2, y2, w="dim", **kw):
        self.ax.add_line(Line2D([x1, x2], [y1, y2], linewidth=_lw(w),
                                solid_capstyle="butt", **kw))

    def text(self, x, y, s, h=2.5, **kw):
        px, py = self.p(x, y)
        self.ax.text(px, py, s, fontsize=h * 2.834645 * 0.75, **kw)

    def paper_text(self, x, y, s, h=2.5, **kw):
        self.ax.text(x, y, s, fontsize=h * 2.834645 * 0.75, **kw)


# ---------------------------------------------------------------------------
# Plan graphics -- section 2
# ---------------------------------------------------------------------------
def _draw_walls(pen: Pen, region):
    geoms = [region] if region.geom_type == "Polygon" else list(region.geoms)
    for g in geoms:
        pen.poly(list(g.exterior.coords), facecolor="#1a1a1a",
                 edgecolor="#000000", linewidth=_lw("wall"), zorder=3)
        for r in g.interiors:
            pen.poly(list(r.coords), facecolor="white", edgecolor="#000000",
                     linewidth=_lw("wall"), zorder=3.1)


def _door(pen: Pen, op: Opening):
    """Leaf at 90 degrees open, perpendicular to the wall, plus the quarter-
    circle swing arc from the hinge. A cased opening draws the void and the
    frame lines and NO leaf and NO arc -- which is what makes it legible as a
    cased opening rather than a missing door."""
    a, b = op.across
    # frame lines at both reveals
    if op.axis == "v":
        pen.line(a, op.p1, b, op.p1, "frame", color="k", zorder=4)
        pen.line(a, op.p2, b, op.p2, "frame", color="k", zorder=4)
    else:
        pen.line(op.p1, a, op.p1, b, "frame", color="k", zorder=4)
        pen.line(op.p2, a, op.p2, b, "frame", color="k", zorder=4)
    if op.kind == "cased_opening" or op.leaf_w is None:
        return
    lw_ = op.leaf_w
    hinge_along = op.p1 if op.hinge_end == "lo" else op.p2
    face = a if op.swing_side == "lo" else b
    sign_across = -1 if op.swing_side == "lo" else +1
    sign_along = +1 if op.hinge_end == "lo" else -1
    if op.axis == "v":
        hx, hy = face, hinge_along
        pen.line(hx, hy, hx + sign_across * lw_, hy, "leaf", color="k", zorder=5)
        th0, th1 = (0, 90) if (sign_across > 0 and sign_along > 0) else \
                   (270, 360) if (sign_across > 0) else \
                   (90, 180) if (sign_along > 0) else (180, 270)
    else:
        hx, hy = hinge_along, face
        pen.line(hx, hy, hx, hy + sign_across * lw_, "leaf", color="k", zorder=5)
        th0, th1 = (0, 90) if (sign_along > 0 and sign_across > 0) else \
                   (270, 360) if (sign_along > 0) else \
                   (90, 180) if (sign_across > 0) else (180, 270)
    c = pen.p(hx, hy)
    d = 2 * lw_ / pen.scale
    pen.ax.add_patch(Arc(c, d, d, theta1=th0, theta2=th1,
                         linewidth=_lw("leaf"), edgecolor="k", zorder=5))


def _window(pen: Pen, op: Opening):
    """Frame lines at both wall faces plus a single centred glazing line running
    the structural opening. Sill and head are not shown in plan."""
    a, b = op.across
    mid = (a + b) / 2.0
    if op.axis == "v":
        pen.line(a, op.p1, a, op.p2, "frame", color="k", zorder=4)
        pen.line(b, op.p1, b, op.p2, "frame", color="k", zorder=4)
        pen.line(mid, op.p1, mid, op.p2, "leaf", color="k", zorder=4)
        pen.line(a, op.p1, b, op.p1, "frame", color="k", zorder=4)
        pen.line(a, op.p2, b, op.p2, "frame", color="k", zorder=4)
    else:
        pen.line(op.p1, a, op.p2, a, "frame", color="k", zorder=4)
        pen.line(op.p1, b, op.p2, b, "frame", color="k", zorder=4)
        pen.line(op.p1, mid, op.p2, mid, "leaf", color="k", zorder=4)
        pen.line(op.p1, a, op.p1, b, "frame", color="k", zorder=4)
        pen.line(op.p2, a, op.p2, b, "frame", color="k", zorder=4)


def _mark(pen: Pen, op: Opening, outward: int = 1):
    """section 8 -- a Ø 5 mm paper circle. Doors are bare numbers, windows
    `ОК<n>`; the two number spaces are distinguished by circle diameter, not by
    the string."""
    a, b = op.across
    mid_across = (a + b) / 2.0
    mid_along = (op.p1 + op.p2) / 2.0
    x, y = (mid_across, mid_along) if op.axis == "v" else (mid_along, mid_across)
    off = 8.0        # paper mm, clear of the wall
    px, py = pen.p(x, y)
    # A mark sits on the side the opening is READ from: outside for an Envelope
    # opening, inside the receiving Space for an internal door. Offsetting the
    # same way for both puts a window mark in the room and a door mark in a wall.
    if op.other is None:
        d = +1 if outward > 0 else -1
    else:
        d = -1 if op.swing_side == "lo" else +1
    if op.axis == "v":
        px += d * off
    else:
        py += d * off
    pen.ax.add_patch(Circle((px, py), 2.5, fill=True, facecolor="white",
                            edgecolor="k", linewidth=_lw("text"), zorder=8))
    pen.paper_text(px, py, op.mark, 1.8, ha="center", va="center", zorder=9)


# ---------------------------------------------------------------------------
# Dimensions -- section 4
# ---------------------------------------------------------------------------
def _outward_of(plan: Plan, op: Opening) -> int:
    """Which way is out of the dwelling at this opening."""
    inner = plan.inner
    a, b = op.across
    if op.axis == "v":
        return -1 if b <= inner.x1 else +1
    return -1 if b <= inner.y1 else +1


def _rung_base(pen: Pen, plan: Plan, side: str, rung: float,
               foot) -> float:
    fx0, fy0, fx1, fy1 = foot.bounds
    if side == "S":
        return pen.p(0, fy0)[1] - rung
    if side == "N":
        return pen.p(0, fy1)[1] + rung
    if side == "W":
        return pen.p(fx0, 0)[0] - rung
    return pen.p(fx1, 0)[0] + rung


def _draw_chain(pen: Pen, plan: Plan, ch: Chain, foot):
    base = _rung_base(pen, plan, ch.side, ch.rung, foot)
    horizontal = ch.axis == "x"
    pts = [pen.p(v, 0)[0] if horizontal else pen.p(0, v)[1] for v in ch.points]
    if horizontal:
        pen.paper_line(pts[0], base, pts[-1], base, "dim", color="#333333")
    else:
        pen.paper_line(base, pts[0], base, pts[-1], "dim", color="#333333")
    for i, q in enumerate(pts):
        if horizontal:
            pen.paper_line(q, base - 1.25, q, base + 1.25, "dim", color="#333333")
        else:
            pen.paper_line(base - 1.25, q, base + 1.25, q, "dim", color="#333333")
    for (a, b), seg in zip(zip(pts, pts[1:]), ch.segments):
        m = (a + b) / 2.0
        span = abs(b - a)
        txt = str(seg)
        narrow = span < len(txt) * 1.8
        if horizontal:
            x, y = m, base + 0.9
            if narrow:
                x, y = m, base + 3.4
                pen.paper_line(m, base + 0.4, m, base + 3.1, "dim",
                               color="#777777")
            pen.paper_text(x, y, txt, 2.5 if not narrow else 1.8,
                           ha="center", va="bottom", color="#111111", zorder=7)
        else:
            x, y = base - 0.9, m
            if narrow:
                x = base - 3.4
                pen.paper_line(base - 0.4, m, base - 3.1, m, "dim",
                               color="#777777")
            pen.paper_text(x, y, txt, 2.5 if not narrow else 1.8, rotation=90,
                           ha="right", va="center", color="#111111", zorder=7)


def _draw_running(pen: Pen, plan: Plan, r: Running, foot):
    base = _rung_base(pen, plan, r.rung_side, r.rung, foot)
    horizontal = r.axis == "x"
    a = pen.p(r.frm, 0)[0] if horizontal else pen.p(0, r.frm)[1]
    b = pen.p(r.to, 0)[0] if horizontal else pen.p(0, r.to)[1]
    if horizontal:
        pen.paper_line(a, base, b, base, "dim", color="#333333")
        pen.paper_text((a + b) / 2, base + 0.9, str(r.value), 2.5,
                       ha="center", va="bottom", zorder=7)
    else:
        pen.paper_line(base, a, base, b, "dim", color="#333333")
        pen.paper_text(base - 0.9, (a + b) / 2, str(r.value), 2.5, rotation=90,
                       ha="right", va="center", zorder=7)


def _draw_setting_out(pen: Pen, so: SettingOut):
    """A short dimension drawn INSIDE the plan, offset 3 mm paper from the host
    wall face, from the perpendicular wall at the pushed-to end to the near jamb.

    The tick is 100 mm -- 2 mm of paper at 1:50 -- so section 5(a) fires on every
    one of them by construction: the text goes outside the extension lines with a
    leader, and it is set horizontally because a rotated two-digit number at
    1,8 mm is the one thing on this sheet a person would misread.
    """
    op = so.opening
    a, b = op.across
    face = a if op.swing_side == "lo" else b
    off = 3.0
    sign = -1 if op.swing_side == "lo" else +1
    if op.axis == "v":
        p1, p2 = pen.p(face, so.frm), pen.p(face, so.to)
        dx = sign * off
        pen.paper_line(p1[0] + dx, p1[1], p2[0] + dx, p2[1], "dim",
                       color="#333333", zorder=7)
        for q in (p1, p2):
            pen.paper_line(q[0], q[1], q[0] + dx * 1.4, q[1], "dim",
                           color="#333333", zorder=7)
        my = (p1[1] + p2[1]) / 2
        lead = 7.0 * sign
        pen.paper_line(p1[0] + dx, my, p1[0] + dx + lead, my, "dim",
                       color="#777777", zorder=7)
        pen.paper_text(p1[0] + dx + lead, my + 0.6, str(so.value), 1.8,
                       ha="left" if sign > 0 else "right", va="bottom", zorder=7)
    else:
        p1, p2 = pen.p(so.frm, face), pen.p(so.to, face)
        dy = sign * off
        pen.paper_line(p1[0], p1[1] + dy, p2[0], p2[1] + dy, "dim",
                       color="#333333", zorder=7)
        for q in (p1, p2):
            pen.paper_line(q[0], q[1], q[0], q[1] + dy * 1.4, "dim",
                           color="#333333", zorder=7)
        mx = (p1[0] + p2[0]) / 2
        lead = 7.0 * sign
        pen.paper_line(mx, p1[1] + dy, mx, p1[1] + dy + lead, "dim",
                       color="#777777", zorder=7)
        pen.paper_text(mx + 0.6, p1[1] + dy + lead, str(so.value), 1.8,
                       ha="left", va="bottom" if sign > 0 else "top", zorder=7)


# ---------------------------------------------------------------------------
# Sheet furniture -- section 10
# ---------------------------------------------------------------------------
def _furniture(ax, sh, attribs: Dict[str, str], notes: List[str],
               fraction=None):
    W, H, scale = sh.width, sh.height, sh.scale
    M = sheet_mod.MARGIN
    strip = sheet_mod.TITLE_STRIP
    ax.add_patch(Rectangle((M, M), W - 2 * M, H - 2 * M, fill=False,
                           linewidth=_lw("ttlb"), edgecolor="k"))
    x0 = W - M - strip
    ax.add_line(Line2D([x0, x0], [M, H - M], linewidth=_lw("ttlb"), color="k"))

    # title block, bottom of the strip
    tb_h = 58.0
    ax.add_patch(Rectangle((x0, M), strip, tb_h, fill=False,
                           linewidth=_lw("ttlb"), edgecolor="k"))
    rows = [("", attribs["PROJECT"], 3.5), ("", attribs["DRAWING"], 5.0),
            ("", attribs["SHEET"], 3.5), ("", attribs["SCALE"], 2.5),
            ("", attribs["SIZE"] + "   REV " + attribs["REV"], 2.5),
            ("", attribs["DATE"], 2.5),
            ("", "ÇƏKDİ " + attribs["DRAWN"], 2.5),
            ("", "YOXLADI " + attribs["CHECKED"], 2.5),
            ("", attribs["STATUS"], 2.5)]
    y = M + tb_h - 6
    for _, txt, h in rows:
        ax.text(x0 + 2, y, txt, fontsize=h * 2.834645 * 0.75, va="top", ha="left",
                wrap=True)
        y -= h + 2.4

    # revision block above it
    ax.add_patch(Rectangle((x0, M + tb_h + 3), strip, 16.0, fill=False,
                           linewidth=_lw("ttlb"), edgecolor="k"))
    ax.text(x0 + 2, M + tb_h + 16, "REV  TARİX  TƏSVİR  KİM",
            fontsize=1.8 * 2.834645 * 0.75, va="top")
    ax.text(x0 + 2, M + tb_h + 11.5, "%s  %s  ilk buraxılış  bim-engine"
            % (attribs["REV"], attribs["DATE"]),
            fontsize=1.8 * 2.834645 * 0.75, va="top")

    # north arrow and scale bar above that
    ny = M + tb_h + 34
    nx = x0 + strip / 2
    ax.add_line(Line2D([nx, nx], [ny - 7, ny + 7], linewidth=_lw("ttlb"), color="k"))
    ax.add_patch(MplPoly([(nx, ny + 9), (nx - 2.4, ny + 3), (nx + 2.4, ny + 3)],
                         closed=True, facecolor="k"))
    ax.text(nx, ny + 10.5, "Ş", fontsize=2.5 * 2.834645 * 0.75, ha="center")
    # The scale bar matters more than the `1:50` text -- it is what survives a
    # photocopy or a rescaled print, and its absence is noticed. One segment is
    # one metre AT THIS SCALE, so the bar is right on any rung of the ladder.
    seg = 1000.0 / scale
    n = max(2, min(4, int((strip - 8) // seg)))
    bx, by = x0 + 4, ny - 14
    for i in range(n):
        ax.add_patch(Rectangle((bx + i * seg, by), seg, 1.6,
                               facecolor="k" if i % 2 == 0 else "w",
                               edgecolor="k", linewidth=_lw("dim")))
    ax.text(bx, by - 4.5, "0", fontsize=1.8 * 2.834645 * 0.75, ha="center")
    ax.text(bx + n * seg, by - 4.5, "%d m" % n,
            fontsize=1.8 * 2.834645 * 0.75, ha="center")

    # general notes, left of the strip. Sheet 2 carries none, and a heading
    # with nothing under it is the tell of a template rather than a set.
    ny = H - M - 4
    if not notes:
        return
    ax.text(M + 3, ny, "QEYDLƏR", fontsize=3.5 * 2.834645 * 0.75, va="top")
    ny -= 6
    for n in notes:
        ax.text(M + 3, ny, _wrap(n, 78), fontsize=1.8 * 2.834645 * 0.75,
                va="top", linespacing=1.35)
        ny -= 3.4 * (1 + n.count("\n") + len(n) // 78)

    if fraction is not None:
        fx, fy = W - M - strip - 46, M + 16
        ax.text(fx, fy + 5, "%s  %s" % (fraction.numerator_label,
                                        fraction.numerator),
                fontsize=2.5 * 2.834645 * 0.75, va="bottom")
        ax.add_line(Line2D([fx, fx + 42], [fy + 4, fy + 4],
                           linewidth=_lw("text"), color="k"))
        ax.text(fx, fy - 1, "%s  %s" % (fraction.denominator_label,
                                        fraction.denominator),
                fontsize=2.5 * 2.834645 * 0.75, va="bottom")


def _wrap(s: str, n: int) -> str:
    out, line = [], ""
    for w in s.split():
        if len(line) + len(w) + 1 > n:
            out.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    out.append(line)
    return "\n".join(out)


# ---------------------------------------------------------------------------
# The sheets
# ---------------------------------------------------------------------------
def sheet1(plan: Plan, dims: Dimensions, tag_list, sh, wall_region, foot,
           attribs: Dict[str, str], notes: List[str], path: str,
           audience: str = "practitioner", dpi: int = 200) -> str:
    fig = plt.figure(figsize=(sh.width / 25.4, sh.height / 25.4), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, sh.width)
    ax.set_ylim(0, sh.height)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")

    fx0, fy0, fx1, fy1 = foot.bounds
    rung = sheet_mod.outermost_rung(dims) + sheet_mod.TEXT_ALLOWANCE
    px0, py0 = sheet_mod.MARGIN, sheet_mod.MARGIN
    pw, ph = sh.printable
    ew = (fx1 - fx0) / sh.scale + 2 * rung
    eh = (fy1 - fy0) / sh.scale + 2 * rung
    ox = px0 + max(0.0, (pw - ew) / 2) + rung - fx0 / sh.scale
    oy = py0 + max(0.0, (ph - eh) / 2) + rung - fy0 / sh.scale
    pen = Pen(ax, sh.scale, ox, oy)

    _draw_walls(pen, wall_region)
    for op in plan.openings:
        if op.kind == "window":
            _window(pen, op)
        else:
            _door(pen, op)

    if audience == "practitioner":
        for ch in dims.chains:
            _draw_chain(pen, plan, ch, foot)
        for r in dims.runnings:
            _draw_running(pen, plan, r, foot)
        for so in dims.setting_out:
            _draw_setting_out(pen, so)
        for op in plan.openings:
            _mark(pen, op, _outward_of(plan, op))

    # section 7 step 4: a leadered tag goes into a fixed column outside the
    # ladder, entries stacked at fixed pitch. That pitch is what makes
    # `draw.no_text_overlap` hard rather than best-effort -- the column has
    # unbounded length, so the ladder always terminates.
    col_x = pen.p(fx1, 0)[0] + sheet_mod.outermost_rung(dims) + 10.0
    col_y = pen.p(0, fy1)[1] - 4.0
    for t in tag_list:
        if t.leadered:
            col_y = _leadered_tag(pen, t, col_x, col_y)
        else:
            _tag(pen, t)

    # section 2 -- annotated once on the plan. Put it in the circulation Space,
    # which is the one room with no furniture and no contested area.
    halls = [s for s in plan.spaces if s.is_circulation] or plan.spaces
    lvl = halls[0].primary
    pen.text(lvl.centroid[0], lvl.y1 + 200, "t.d.s. " + fmt.level(0.0), 2.5,
             ha="center", va="bottom", zorder=9)

    if audience == "practitioner":
        _furniture(ax, sh, attribs, notes, tags_mod.area_fraction(plan))
    fig.savefig(path, dpi=dpi, facecolor="white")
    plt.close(fig)
    return path


def _leadered_tag(pen: Pen, t, col_x: float, col_y: float) -> float:
    ax, ay = pen.p(*t.at)
    pen.paper_line(ax, ay, col_x - 1.0, col_y - 2.0, "dim", color="#777777",
                   zorder=8)
    pen.ax.add_patch(Circle((ax, ay), 0.6, facecolor="k", edgecolor="none",
                            zorder=8))
    heights = [t.name_height] + [t.body_height] * (len(t.lines) - 1)
    y = col_y
    for i, (line, h) in enumerate(zip(t.lines, heights)):
        pen.paper_text(col_x, y, line, h, ha="left", va="top", zorder=9,
                       color="#111111")
        y -= h * 1.45
    return y - 3.0


def _tag(pen: Pen, t):
    x, y = t.at
    heights = [t.name_height] + [t.body_height] * (len(t.lines) - 1)
    total = sum(heights) * 1.45
    py = pen.p(x, y)[1] + total / 2
    px = pen.p(x, y)[0]
    for i, (line, h) in enumerate(zip(t.lines, heights)):
        pen.paper_text(px, py, line, h, ha="center", va="top", zorder=9,
                       color="#111111")
        if i in t.underline_lines:
            wgt = len(line) * 0.62 * h / 2
            pen.paper_line(px - wgt, py - h * 1.15, px + wgt, py - h * 1.15,
                           "text", color="#111111", zorder=9)
        py -= h * 1.45


def sheet2(plan: Plan, sh, attribs: Dict[str, str], path: str,
           dpi: int = 200) -> str:
    """Sheet 2 of 2 -- the three schedules. A single-sheet set with schedules
    crammed into the plan margin is what a generator produces; a set is what a
    practice issues."""
    fig = plt.figure(figsize=(sh.width / 25.4, sh.height / 25.4), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, sh.width)
    ax.set_ylim(0, sh.height)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")
    _furniture(ax, sh, attribs, [], None)

    y = sh.height - sheet_mod.MARGIN - 12
    x = sheet_mod.MARGIN + 6
    width = sh.width - 2 * sheet_mod.MARGIN - sheet_mod.TITLE_STRIP - 12
    for table in (schedules.door_schedule(plan), schedules.window_schedule(plan),
                  schedules.room_schedule(plan)):
        y = _table(ax, table, x, y, width)
        y -= 10
    fig.savefig(path, dpi=dpi, facecolor="white")
    plt.close(fig)
    return path


def _table(ax, table, x: float, y: float, width: float) -> float:
    ax.text(x, y, table.title, fontsize=3.5 * 2.834645 * 0.75, va="top")
    y -= 7
    n = len(table.headers)
    widths = _col_widths(table, width)
    ax.add_line(Line2D([x, x + width], [y, y], linewidth=_lw("frame"), color="k"))
    cx = x
    for h, w in zip(table.headers, widths):
        ax.text(cx + 1.5, y - 1.5, h, fontsize=2.5 * 2.834645 * 0.75, va="top")
        cx += w
    y -= 7
    ax.add_line(Line2D([x, x + width], [y, y], linewidth=_lw("frame"), color="k"))
    for row in table.rows:
        cx = x
        for cell, w in zip(row, widths):
            ax.text(cx + 1.5, y - 1.4, str(cell),
                    fontsize=2.5 * 2.834645 * 0.75, va="top")
            cx += w
        y -= 6
        ax.add_line(Line2D([x, x + width], [y, y], linewidth=_lw("dim"),
                           color="#888888"))
    for note in table.notes:
        y -= 5
        ax.text(x, y, _wrap(note, 110), fontsize=1.8 * 2.834645 * 0.75, va="top")
        y -= 3
    return y


def _col_widths(table, width: float) -> List[float]:
    cols = list(zip(*([table.headers] + table.rows))) if table.rows else \
        [(h,) for h in table.headers]
    raw = [max(len(str(c)) for c in col) for col in cols]
    total = sum(raw)
    return [max(14.0, width * r / total) for r in raw]
