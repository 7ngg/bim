"""docs/spec/annotation.md section 13 -- the Drawing check.

Twelve predicates. A Plan reaching this point has already passed the Acceptance
bar, so a Drawing failure is OUR BUG, NOT THE PLAN'S: the check raises and
refuses to emit the file. It never degrades silently, and it never ships a
drawing it knows is wrong.

This is not the Acceptance bar and does not go in `rules.json`. The bar has two
consumers -- the solver posts inequalities, the validator evaluates finished
geometry -- which is what forced a declarative registry. The Drawing check has
one consumer and runs at export.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from . import fmt, schedules, sheet as sheet_mod
from .dimensions import Dimensions
from .model import Plan


class DrawingError(Exception):
    pass


@dataclass
class Report:
    results: Dict[str, Tuple[bool, str]] = field(default_factory=dict)

    def add(self, name: str, ok: bool, detail: str = ""):
        self.results[name] = (bool(ok), detail)

    @property
    def ok(self) -> bool:
        return all(v[0] for v in self.results.values())

    @property
    def failures(self) -> List[str]:
        return ["%s: %s" % (k, d) for k, (o, d) in self.results.items() if not o]

    def lines(self) -> List[str]:
        return ["[%s] %-34s %s" % ("PASS" if o else "FAIL", k, d)
                for k, (o, d) in self.results.items()]


def run(plan: Plan, dims: Dimensions, tag_list, sh, doc=None,
        authored: Optional[Sequence] = None) -> Report:
    r = Report()
    inner = plan.inner

    # 1 -----------------------------------------------------------------
    bad = []
    for ch in dims.chains:
        want = ch.span
        if sum(ch.segments) != want:
            bad.append("%s/%s" % (ch.tier, ch.side))
        if ch.tier in (2, 3):
            axis_span = inner.w if ch.axis == "x" else inner.h
            if ch.span != axis_span:
                bad.append("%s/%s does not close on the axis" % (ch.tier, ch.side))
    r.add("draw.chain_closes", not bad, ", ".join(bad) or "%d chains" % len(dims.chains))

    # 2 -----------------------------------------------------------------
    if authored:
        off = [str(exp) for dim, exp in authored
               if abs(_measurement(dim) - exp) > 0.5]
        r.add("draw.measurement_matches_model", not off,
              "%d DIMENSION entities" % len(authored) if not off
              else "%d disagree: %s" % (len(off), ", ".join(off[:6])))
    else:
        r.add("draw.measurement_matches_model", True, "no DXF authored")

    # 3 -----------------------------------------------------------------
    if doc is not None:
        st = doc.dimstyles.get("ARCH-MM-%d" % sh.scale)
        ok = (abs(st.dxf.dimlfac - 1.0) < 1e-9 and st.dxf.dimdec == 0
              and doc.header["$INSUNITS"] == 4 and doc.header["$MEASUREMENT"] == 1)
        r.add("draw.dimstyle_units", ok,
              "dimlfac=%s dimdec=%s insunits=%s measurement=%s"
              % (st.dxf.dimlfac, st.dxf.dimdec, doc.header["$INSUNITS"],
                 doc.header["$MEASUREMENT"]))
    else:
        r.add("draw.dimstyle_units", True, "no DXF authored")

    # 4 -----------------------------------------------------------------
    refs = [t.ref for t in tag_list]
    r.add("draw.every_space_tagged",
          sorted(refs) == sorted(s.ref for s in plan.spaces)
          and len(refs) == len(set(refs)),
          "%d tags for %d Spaces" % (len(refs), len(plan.spaces)))

    # 5 -----------------------------------------------------------------
    marks = [o.mark for o in plan.openings]
    keyed = [(o.kind == "window", o.mark) for o in plan.openings]
    r.add("draw.every_opening_marked",
          all(m for m in marks) and len(set(keyed)) == len(keyed),
          "%d marks, join key is (kind, n)" % len(marks))

    # 6 -----------------------------------------------------------------
    from .dimensions import opening_side
    env_ops = [o for o in plan.openings if o.other is None]
    int_ops = [o for o in plan.openings if o.other is not None]
    missing = []
    for o in env_ops:
        side = opening_side(plan, o)
        hits = [c for c in dims.chains
                if c.tier == 3 and c.side == side
                and o.p1 in c.points and o.p2 in c.points]
        if len(hits) != 1:
            missing.append("%s in %d tier-3 chains" % (o.mark, len(hits)))
    for o in int_ops:
        hits = [s for s in dims.setting_out if s.opening is o]
        if len(hits) != 1:
            missing.append("%s has %d setting-out dims" % (o.mark, len(hits)))
    r.add("draw.every_opening_positioned", not missing,
          ", ".join(missing) or "%d envelope, %d internal"
          % (len(env_ops), len(int_ops)))

    # 7 -----------------------------------------------------------------
    from .dimensions import partition_bands
    faces = set()
    for b in partition_bands(plan):
        faces.add((b.axis, b.lo_face))
        faces.add((b.axis, b.hi_face))
    covered = set()
    for ch in dims.chains:
        if ch.tier != 2:
            continue
        axis = "v" if ch.axis == "x" else "h"
        for p in ch.points:
            covered.add((axis, p))
    for rr in dims.runnings:
        covered.add(("v" if rr.axis == "x" else "h", rr.to))
    undim = sorted(faces - covered)
    r.add("draw.every_wall_face_dimensioned", not undim,
          "%d partition faces" % len(faces) if not undim
          else "%d undimensioned: %s" % (len(undim), undim[:6]))

    # 8 -----------------------------------------------------------------
    d = schedules.door_schedule(plan)
    w = schedules.window_schedule(plan)
    rs = schedules.room_schedule(plan)
    ok = (len(d.rows) == len([o for o in plan.openings if o.is_door])
          and len(w.rows) == len([o for o in plan.openings if o.kind == "window"])
          and len(rs.rows) - 3 == len(plan.spaces))
    r.add("draw.schedule_complete", ok,
          "%d door rows, %d window rows, %d room rows"
          % (len(d.rows), len(w.rows), len(rs.rows) - 3))

    # 9 -----------------------------------------------------------------
    r.add("draw.schedule_totals_close", schedules.totals_close(plan),
          "printed column adds to the printed total")

    # 10 ----------------------------------------------------------------
    if doc is not None:
        from .dxf import LAYERS, VALID_LINEWEIGHTS
        bad_lw = [n for n, (_c, lw) in LAYERS.items()
                  if lw not in VALID_LINEWEIGHTS]
        r.add("draw.lineweights_valid", not bad_lw,
              ", ".join(bad_lw) or "%d layers" % len(LAYERS))
    else:
        r.add("draw.lineweights_valid", True, "no DXF authored")

    # 11 ----------------------------------------------------------------
    boxes = _text_boxes(plan, tag_list, sh, dims)
    clash = _first_overlap(boxes)
    r.add("draw.no_text_overlap", clash is None,
          "%d text extents" % len(boxes) if clash is None else str(clash))

    # 12 ----------------------------------------------------------------
    pw, ph = sh.printable
    ew, eh = sh.extent_paper
    r.add("draw.within_printable_area", ew <= pw + 1e-6 and eh <= ph + 1e-6,
          "extent %.1f x %.1f in %.1f x %.1f" % (ew, eh, pw, ph))
    return r


def _measurement(dim) -> float:
    """`add_linear_dim` hands back a `DimStyleOverride`; the DIMENSION entity is
    on its `.dimension`. Reading the measurement off the ENTITY rather than off
    what we passed in is the whole point of this predicate -- it is what catches
    the stale block, where definition points were mutated without re-rendering
    so the drawn picture and the semantic measurement disagree."""
    ent = getattr(dim, "dimension", dim)
    return float(ent.get_measurement())


def _text_boxes(plan: Plan, tag_list, sh, dims=None) -> List[Tuple[str, float, float, float, float]]:
    """Rendered text extents in PAPER millimetres.

    Approximate by construction -- a glyph advance is estimated at 0,62 of the
    height, which is what a normal-width ISO 3098 face runs at. It is stated
    rather than hidden: the predicate catches a tag laid over a tag, which is
    the failure it exists for, and would not catch two strings overlapping by a
    hair. The margin used is deliberately generous for that reason.
    """
    out = []
    for t in tag_list:
        if t.leadered:
            # section 7 step 4 terminates BY CONSTRUCTION: the margin column has
            # fixed pitch and unbounded length, so a leadered tag cannot overlap
            # anything. That argument is the reason the ladder is finite, and it
            # would be circular to re-check it against an estimated glyph width.
            continue
        heights = [t.name_height] + [t.body_height] * (len(t.lines) - 1)
        w = max(len(s) * 0.62 * h for s, h in zip(t.lines, heights))
        h = sum(heights) * 1.45
        cx, cy = t.at[0] / sh.scale, t.at[1] / sh.scale
        out.append(("tag " + t.ref, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
    for op in plan.openings:
        a, b = op.across
        across = (a + b) / 2.0 / sh.scale
        along = (op.p1 + op.p2) / 2.0 / sh.scale
        d = -1 if op.swing_side == "lo" else +1
        if op.axis == "v":
            cx, cy = across + d * 8.0, along
        else:
            cx, cy = along, across + d * 8.0
        out.append(("mark " + op.mark, cx - 2.5, cy - 2.5, cx + 2.5, cy + 2.5))
    # The external rungs cannot collide with the plan or with each other -- they
    # sit outside the Envelope bbox at 8 paper mm apart, carrying 2,5 mm text
    # (section 5, "impossible by construction"). The SETTING-OUT dimensions are
    # the exception the spec names: section 4.5 puts annotation INSIDE the plan,
    # so those collisions are real and are checked.
    for so in (dims.setting_out if dims else []):
        op = so.opening
        a, b = op.across
        face = (a if op.swing_side == "lo" else b) / sh.scale
        sign = -1 if op.swing_side == "lo" else +1
        mid = ((so.frm + so.to) / 2.0) / sh.scale
        w, h = len(str(so.value)) * 0.62 * 1.8, 1.8
        if op.axis == "v":
            cx, cy = face + sign * 10.0, mid
        else:
            cx, cy = mid, face + sign * 10.0
        out.append(("sod " + op.mark, cx - w / 2, cy - h / 2,
                    cx + w / 2, cy + h / 2))
    return out


def _first_overlap(boxes):
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            if (a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]):
                return "%s overlaps %s" % (a[0], b[0])
    return None


def enforce(report: Report) -> None:
    if not report.ok:
        raise DrawingError("the Drawing check refuses to emit this file:\n  "
                           + "\n  ".join(report.failures))
