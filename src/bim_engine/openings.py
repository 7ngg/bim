"""docs/spec/openings.md -- which opening, where, hinged which way.

Never executed before this module existed. Every rule below cites the section it
implements, because the spec is the contract and a placement that cannot name
its clause is a placement someone invented.

THE ORDER IS THE ORDER YOU WALK IN (section 3.1). Realised circulation is a tree
rooted at the primary entrance, doors are placed breadth-first from that root,
and each door is pushed to the end of its shared run nearest the point the path
arrives at -- the door the approaching Space was itself entered through. No
search, no objective, no tie-break heuristic dressed up as a rule. The effect is
the one that matters: the door lands at a corner and the far wall of the
receiving room stays unbroken.
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from . import profile
from .model import Face, Opening, Plan, RectMM, Space

JAMB = profile.JAMB_RETURN_MM          # 100 -- open.fits_segment
NIB = profile.LEADING_EDGE_NIB_MM      # 300 -- open.leading_edge_nib
T_INT = profile.T_INT_MM


class PlacementError(Exception):
    """A Plan that reached here has passed the Acceptance bar, so a failure is a
    fact about the Proposal (section 4.2 step 3) or about us -- never something
    to route around by moving a door somewhere an architect would not put it."""


# ---------------------------------------------------------------------------
# Shared runs
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Run:
    """One clear wall run shared by two Spaces, or by a Space and the outside.

    `axis` is the WALL's axis: 'v' means a vertical wall, so the run is in y.
    `across` is the wall body's extent; `lo`/`hi` bound the CLEAR run, which is
    what section 3.2 measures and what section 8's reservation is stated in.
    """
    axis: str
    across: Tuple[int, int]
    lo: int
    hi: int
    a: str                      # Space ref on the low side across the wall
    b: Optional[str]            # Space ref on the high side, or None (outside)

    @property
    def length(self) -> int:
        return self.hi - self.lo

    def point_at(self, along: float) -> Tuple[float, float]:
        c = (self.across[0] + self.across[1]) / 2.0
        return (c, along) if self.axis == "v" else (along, c)


def _parts(space: Space):
    return space.parts


def shared_runs(plan: Plan) -> List[Run]:
    """Every internal wall run two Spaces share, on the clear plane.

    Two clear rectangles separated by exactly `t_int` on one axis and
    overlapping on the other share a run, and the overlap IS the clear run --
    both extents are already face to face, so nothing has to be corrected for
    the perpendicular walls at its ends.
    """
    out: List[Run] = []
    for i, sa in enumerate(plan.spaces):
        for sb in plan.spaces[i + 1:]:
            for ra in _parts(sa):
                for rb in _parts(sb):
                    out.extend(_pair_runs(ra, rb, sa.ref, sb.ref))
    return _merge(out)


def _pair_runs(ra: RectMM, rb: RectMM, ka: str, kb: str) -> List[Run]:
    out = []
    if ra.x2 + T_INT == rb.x1:
        lo, hi = max(ra.y1, rb.y1), min(ra.y2, rb.y2)
        if hi > lo:
            out.append(Run("v", (ra.x2, rb.x1), lo, hi, ka, kb))
    if rb.x2 + T_INT == ra.x1:
        lo, hi = max(ra.y1, rb.y1), min(ra.y2, rb.y2)
        if hi > lo:
            out.append(Run("v", (rb.x2, ra.x1), lo, hi, kb, ka))
    if ra.y2 + T_INT == rb.y1:
        lo, hi = max(ra.x1, rb.x1), min(ra.x2, rb.x2)
        if hi > lo:
            out.append(Run("h", (ra.y2, rb.y1), lo, hi, ka, kb))
    if rb.y2 + T_INT == ra.y1:
        lo, hi = max(ra.x1, rb.x1), min(ra.x2, rb.x2)
        if hi > lo:
            out.append(Run("h", (rb.y2, ra.y1), lo, hi, kb, ka))
    return out


def _merge(runs: List[Run]) -> List[Run]:
    """A two-part Room can meet a neighbour twice on one line; those are one run.

    Merging matters for section 3.2 rather than for tidiness: the jamb return is
    measured from the perpendicular wall at the end of the RUN, and two abutting
    halves of one run have no wall between them.
    """
    by_key: Dict[Tuple, List[Run]] = {}
    for r in runs:
        by_key.setdefault((r.axis, r.across, r.a, r.b), []).append(r)
    out = []
    for key, group in by_key.items():
        group.sort(key=lambda r: r.lo)
        cur = group[0]
        for nxt in group[1:]:
            if nxt.lo <= cur.hi:
                cur = Run(cur.axis, cur.across, cur.lo, max(cur.hi, nxt.hi),
                          cur.a, cur.b)
            else:
                out.append(cur)
                cur = nxt
        out.append(cur)
    return out


def envelope_runs(plan: Plan) -> List[Run]:
    """Every clear run a Space shares with the Envelope, typed by its face.

    A run is emitted per (Space, face) pair, so a Space on two elevations gets
    two, which is what section 6.1's *longest exterior run* has to choose over.
    """
    out: List[Run] = []
    for s in plan.spaces:
        for r in _parts(s):
            for f in plan.faces:
                if f.axis == "v":
                    if f.outward == -1 and r.x1 == f.coord:
                        lo, hi = max(r.y1, f.lo), min(r.y2, f.hi)
                        if hi > lo:
                            out.append(Run("v", (f.coord - f.thickness, f.coord),
                                           lo, hi, None, s.ref))
                    if f.outward == +1 and r.x2 == f.coord:
                        lo, hi = max(r.y1, f.lo), min(r.y2, f.hi)
                        if hi > lo:
                            out.append(Run("v", (f.coord, f.coord + f.thickness),
                                           lo, hi, s.ref, None))
                else:
                    if f.outward == -1 and r.y1 == f.coord:
                        lo, hi = max(r.x1, f.lo), min(r.x2, f.hi)
                        if hi > lo:
                            out.append(Run("h", (f.coord - f.thickness, f.coord),
                                           lo, hi, None, s.ref))
                    if f.outward == +1 and r.y2 == f.coord:
                        lo, hi = max(r.x1, f.lo), min(r.x2, f.hi)
                        if hi > lo:
                            out.append(Run("h", (f.coord, f.coord + f.thickness),
                                           lo, hi, s.ref, None))
    return _merge_env(out)


def _merge_env(runs: List[Run]) -> List[Run]:
    by_key: Dict[Tuple, List[Run]] = {}
    for r in runs:
        by_key.setdefault((r.axis, r.across, r.a, r.b), []).append(r)
    out = []
    for _, group in by_key.items():
        group.sort(key=lambda r: r.lo)
        cur = group[0]
        for nxt in group[1:]:
            if nxt.lo <= cur.hi:
                cur = Run(cur.axis, cur.across, cur.lo, max(cur.hi, nxt.hi),
                          cur.a, cur.b)
            else:
                out.append(cur)
                cur = nxt
        out.append(cur)
    return out


def face_for_run(plan: Plan, run: Run) -> Optional[Face]:
    for f in plan.faces:
        if f.axis != run.axis:
            continue
        coord = run.across[1] if f.outward == -1 else run.across[0]
        if f.coord == coord and min(f.hi, run.hi) - max(f.lo, run.lo) > 0:
            return f
    return None


# ---------------------------------------------------------------------------
# Catalogue choice -- section 2.1, keyed by the RECEIVING Room
# ---------------------------------------------------------------------------
def receiving(plan: Plan, a: str, b: str, depth: Dict[str, int]) -> Tuple[str, str]:
    """section 3.3, in its stated order. Returns (receiving_ref, other_ref)."""
    sa, sb = plan.by_ref(a), plan.by_ref(b)
    pa, pb = sa.is_private, sb.is_private
    if pa != pb:
        return (a, b) if pa else (b, a)
    wa, wb = sa.is_wet, sb.is_wet
    if wa != wb:
        return (a, b) if wa else (b, a)
    da, db = depth.get(a, 10 ** 6), depth.get(b, 10 ** 6)
    if da != db:
        return (a, b) if da > db else (b, a)
    if sa.area_m2 != sb.area_m2:
        return (a, b) if sa.area_m2 < sb.area_m2 else (b, a)
    return (a, b) if a > b else (b, a)


def catalogue_for(plan: Plan, receiving_ref: str) -> dict:
    key = plan.by_ref(receiving_ref).key
    return profile.catalogue(profile.door_entry_for(key))


def structural_width(plan: Plan, receiving_ref: str) -> int:
    return int(catalogue_for(plan, receiving_ref)["opening_w"])


def _width_or_none(plan: Plan, ref: str):
    """`hall`, `corridor` and `entrance_lobby` never appear in section 2.1's
    table because they are never the receiving Room. That is a fact about the
    map, not a gap in it, so this returns None rather than raising."""
    try:
        return structural_width(plan, ref)
    except KeyError:
        return None


def pair_width(plan: Plan, a: str, b: str):
    """The door width a run must reserve for, before the tree fixes which end
    receives. `None` when neither end can receive a door at all."""
    ws = [w for w in (_width_or_none(plan, a), _width_or_none(plan, b))
          if w is not None]
    return min(ws) if ws else None


# ---------------------------------------------------------------------------
# Circulation -- section 3.1's tree
# ---------------------------------------------------------------------------
def entrance_face(plan: Plan) -> Tuple[Run, Space]:
    """section 7 -- the primary entrance is on the segment between the invented
    `hall` and the exterior, on an `entrance_side` edge.

    A party edge may host it: a party wall is External, so a flat's front door
    onto a common corridor is already expressible. A party edge hosts no window
    and no entrance unless flagged, which is what `entrance_side` is.
    """
    halls = [s for s in plan.spaces if s.key == "hall"]
    if not halls:
        raise PlacementError("no hall: `entry.exists` should have refused this "
                             "candidate before placement (openings.md section 7)")
    hall = halls[0]
    cands = [r for r in envelope_runs(plan)
             if (r.a == hall.ref or r.b == hall.ref)
             and _side_of(plan, r) == plan.entrance_side]
    if not cands:
        cands = [r for r in envelope_runs(plan) if r.a == hall.ref or r.b == hall.ref]
    if not cands:
        raise PlacementError("the hall touches no Envelope edge; `entry.exists` "
                             "fails (openings.md section 7)")
    cands.sort(key=lambda r: (-r.length, r.lo, r.across))
    return cands[0], hall


def _side_of(plan: Plan, run: Run) -> Optional[str]:
    f = face_for_run(plan, run)
    return f.side if f else None


def circulation_tree(plan: Plan, runs: List[Run]) -> Tuple[Dict[str, int], List[Tuple[str, str, Run]]]:
    """Breadth-first from the entrance. A private Room is a leaf: circulation
    never passes through one, which is the solver's own H10 restated at
    placement time so the two cannot disagree."""
    hall = [s for s in plan.spaces if s.key == "hall"][0]
    adj: Dict[str, List[Tuple[str, Run]]] = {s.ref: [] for s in plan.spaces}
    for r in runs:
        w = pair_width(plan, r.a, r.b)
        if w is not None and r.length >= w + JAMB + NIB:
            adj[r.a].append((r.b, r))
            adj[r.b].append((r.a, r))

    depth = {hall.ref: 0}
    edges: List[Tuple[str, str, Run]] = []
    q = deque([hall.ref])
    while q:
        cur = q.popleft()
        nbrs = sorted(adj[cur], key=lambda nr: (nr[0]))
        for nxt, run in nbrs:
            if nxt in depth:
                continue
            w = structural_width(plan, receiving(plan, cur, nxt, depth)[0])
            if run.length < w + JAMB + NIB:
                continue
            depth[nxt] = depth[cur] + 1
            edges.append((cur, nxt, run))
            if not plan.by_ref(nxt).is_private:
                q.append(nxt)
    return depth, edges


# ---------------------------------------------------------------------------
# Placement -- section 3.2
# ---------------------------------------------------------------------------
def push_end(run: Run, arrive: Optional[Tuple[float, float]]) -> str:
    """Which end the door is pushed to: the one nearest the point the path
    arrives at. Ties break to the end with the smaller x, then smaller y --
    so a regenerate with an unchanged Plan produces an unchanged set."""
    p_lo, p_hi = run.point_at(run.lo), run.point_at(run.hi)
    if arrive is None:
        return "lo" if (p_lo[0], p_lo[1]) <= (p_hi[0], p_hi[1]) else "hi"
    d_lo = math.dist(p_lo, arrive)
    d_hi = math.dist(p_hi, arrive)
    if abs(d_lo - d_hi) < 1e-9:
        return "lo" if (p_lo[0], p_lo[1]) <= (p_hi[0], p_hi[1]) else "hi"
    return "lo" if d_lo < d_hi else "hi"


def _span(run: Run, w: int, end: str) -> Tuple[int, int, int]:
    """The structural opening and its setting-out datum, section 3.2.

        jamb return 100 | structural opening w | nib 300

    so the minimum clear run is `w + 400` at either end, and the surplus falls
    on the far side. The door does not centre in it and does not distribute.
    """
    if run.length < w + JAMB + NIB:
        raise PlacementError(
            "clear run %d < %d for a %d door (open.fits_segment / "
            "open.leading_edge_nib)" % (run.length, w + JAMB + NIB, w))
    if end == "lo":
        p1 = run.lo + JAMB
        return p1, p1 + w, run.lo
    p2 = run.hi - JAMB
    return p2 - w, p2, run.hi


# ---------------------------------------------------------------------------
# Swing -- section 4
# ---------------------------------------------------------------------------
def _swing_square(op: Opening, side: str) -> RectMM:
    """The conservative bounding square the model uses for clearance, built from
    the LEAF width (section 2.3) and never drawn (annotation.md section 2)."""
    lw = op.leaf_w or 0
    a, b = op.across
    if op.axis == "v":
        x = (a - lw, a) if side == "lo" else (b, b + lw)
        y = (op.p1, op.p1 + lw) if op.hinge_end == "lo" else (op.p2 - lw, op.p2)
    else:
        y = (a - lw, a) if side == "lo" else (b, b + lw)
        x = (op.p1, op.p1 + lw) if op.hinge_end == "lo" else (op.p2 - lw, op.p2)
    return RectMM(int(x[0]), int(y[0]), int(x[1]), int(y[1]))


def _side_of_space(plan: Plan, op: Opening, ref: str) -> str:
    """Which side of the wall a Space lies on, 'lo' or 'hi' across the wall."""
    s = plan.by_ref(ref)
    a, b = op.across
    for r in s.parts:
        if op.axis == "v" and r.x2 == a:
            return "lo"
        if op.axis == "v" and r.x1 == b:
            return "hi"
        if op.axis == "h" and r.y2 == a:
            return "lo"
        if op.axis == "h" and r.y1 == b:
            return "hi"
    raise PlacementError("Space %s does not bound this opening" % ref)


def _swing_fits(plan: Plan, op: Opening, side: str, ref: str, placed) -> bool:
    sq = _swing_square(op, side).as_poly()
    if not plan.by_ref(ref).as_poly().buffer(1e-6).contains(sq):
        return False                       # open.swing_within_space
    for other, oside, oref in placed:
        if _swing_square(other, oside).as_poly().intersection(sq).area > 1e-6:
            return False                   # open.swings_disjoint
    return True


# ---------------------------------------------------------------------------
# Windows -- section 6
# ---------------------------------------------------------------------------
def window_for(plan: Plan, space: Space, runs: List[Run]) -> Optional[Opening]:
    """One window per Space, height fixed by the Room, width from the series.

    section 6.1, in its stated order: TARGET FIRST (0.154), FLOOR SECOND
    (0.125, `win.area_ratio`, HARD), FAILURE THIRD. It is never quietly
    downgraded to the widest member that fits, which would ship an under-glazed
    room the validator then rejects for a reason this layer already knew.
    """
    ext = [r for r in runs
           if (r.a == space.ref or r.b == space.ref)
           and (face_for_run(plan, r) or Face("v", 0, 0, 0, 1, False)).is_exterior]
    if not ext:
        raise PlacementError(
            "%s (%s) needs a window and has no exterior run: `win."
            "habitable_has_window` fails" % (space.ref, space.key))
    run = max(ext, key=lambda r: (r.length, -r.lo))
    h = profile.window_height_mm(space.key)
    series = profile.width_series_mm()
    area_mm2 = space.area_m2 * 1e6
    for ratio in (profile.glazing_soft_target(), profile.glazing_hard_floor()):
        need = ratio * area_mm2 / h
        for s in series:
            if s >= need and s + 2 * JAMB <= run.length:
                return _centre_window(space, run, s, h)
    raise PlacementError(
        "%s (%s) cannot be glazed to cl. 9.13 on its %d mm run: hard failure of "
        "win.area_ratio" % (space.ref, space.key, run.length))


def _centre_window(space: Space, run: Run, w: int, h: int) -> Opening:
    """A single window centres on its clear run, which keeps it off the corners
    without a separate corner rule.

    THE POSITION IS NOT ROUNDED TO EVEN, AND SECTION 14 IS THE EVIDENCE. section
    6.1 says "centred on its clear run, rounded to even millimetres per ADR
    0004", but ADR 0004 binds the published DIMENSIONS -- thicknesses and
    opening widths -- and section 14's own tier-3 chain reads
    `1275 | 1800 | 2425 | 1350 | 1000`, whose first and third ticks are odd.
    Forcing an even jamb would move the window 1 mm off centre and put this
    package 1 mm away from the only fully computed example on the map. The
    opening WIDTH stays even, which is what the ADR actually asks for; where the
    surplus is odd the near jamb takes the floor, deterministically.
    """
    p1 = run.lo + (run.length - w) // 2
    return Opening(kind="window", catalogue="", mark="", axis=run.axis,
                   across=run.across, p1=p1, p2=p1 + w, height_mm=h,
                   host_space=space.ref, glazed=True)


def window_designation(w: int, h: int) -> str:
    """annotation.md section 6 -- height-then-width in decimetres, and the
    fractional decimetre group takes a comma, which the standard itself prints.

    Above `published_through` the cell carries the plain opening dimension
    string and NEVER a fabricated mark: inventing a standard designation for a
    size the standard does not publish is the same failure as an invented room
    abbreviation.
    """
    if w > profile.width_series_published_through():
        return "%d x %d" % (h, w)

    def dm(v):
        d = v / 100.0
        return ("%g" % d).replace(".", profile.decimal_separator())
    return "ОР %s-%s" % (dm(h), dm(w))


# ---------------------------------------------------------------------------
# The whole placement
# ---------------------------------------------------------------------------
def place(plan: Plan) -> Plan:
    """Fill `plan.openings`. Idempotent; raises rather than degrading."""
    plan.openings = []
    runs = shared_runs(plan)
    env = envelope_runs(plan)
    depth, edges = circulation_tree(plan, runs)

    unreached = [s.ref for s in plan.spaces if s.ref not in depth]
    if unreached:
        raise PlacementError(
            "no door run reaches %s: section 8's reservation was not honoured "
            "upstream" % ", ".join(unreached))

    # ---- the entrance, section 7 -----------------------------------------
    e_run, hall = entrance_face(plan)
    cat = profile.catalogue("door_flat_entrance")
    end = push_end(e_run, None)
    p1, p2, datum = _span(e_run, int(cat["opening_w"]), end)
    ent = Opening(kind="entrance_door", catalogue="door_flat_entrance", mark="1",
                  axis=e_run.axis, across=e_run.across, p1=p1, p2=p2,
                  height_mm=int(cat["opening_h"]), receiving=hall.ref, other=None,
                  hinge_end=end, swing_side=None, datum=datum,
                  glazed=bool(cat.get("glazed")))
    ent.swing_side = _side_of_space(plan, ent, hall.ref)
    placed = [(ent, ent.swing_side, hall.ref)]
    plan.openings.append(ent)

    arrive: Dict[str, Tuple[float, float]] = {
        hall.ref: e_run.point_at((p1 + p2) / 2.0)}

    # ---- internal doors, breadth-first from that root, section 3.1 --------
    n = 1
    for (parent, child, run) in edges:
        rec, other = receiving(plan, parent, child, depth)
        cased = _is_cased(plan, parent, child)
        cat = catalogue_for(plan, rec)
        w = int(cat["opening_w"])
        end = push_end(run, arrive.get(parent))
        p1, p2, datum = _span(run, w, end)
        n += 1
        op = Opening(kind="cased_opening" if cased else "door",
                     catalogue="" if cased else profile.door_entry_for(
                         plan.by_ref(rec).key),
                     mark=str(n), axis=run.axis, across=run.across,
                     p1=p1, p2=p2, height_mm=int(cat["opening_h"]),
                     receiving=rec, other=other,
                     hinge_end=None if cased else end, datum=datum,
                     glazed=bool(cat.get("glazed")) and not cased)
        if not cased:
            op.swing_side = _pick_swing(plan, op, rec, other, placed)
            placed.append((op, op.swing_side, rec))
        plan.openings.append(op)
        arrive[child] = run.point_at((p1 + p2) / 2.0)

    # ---- windows, section 6 ----------------------------------------------
    k = 0
    for s in plan.spaces:
        if not s.needs_window:
            continue
        win = window_for(plan, s, env)
        k += 1
        win.mark = "ОK%d" % k
        win.catalogue = window_designation(win.width, win.height_mm)
        plan.openings.append(win)
    return plan


def _is_cased(plan: Plan, a: str, b: str) -> bool:
    """section 5 -- every internal opening carries a leaf, EXCEPT between
    `living` and `dining`, which is cased. Not a privacy-and-wet predicate: the
    catalogue ships a purpose-made glazed living-room door, and AzDTN requires
    no kitchen door yet a gas hob is the Baku norm."""
    keys = {plan.by_ref(a).key, plan.by_ref(b).key}
    return keys == {"living", "dining"}


def _pick_swing(plan: Plan, op: Opening, rec: str, other: str, placed) -> str:
    """section 4.2's fallback, in order, and section 4.3's absolute rule: no
    internal door swings into a circulation Space. The entrance door does, into
    the hall, and it is the only one."""
    side_rec = _side_of_space(plan, op, rec)
    if _swing_fits(plan, op, side_rec, rec, placed):
        return side_rec
    if not plan.by_ref(other).is_circulation:
        side_other = _side_of_space(plan, op, other)
        if _swing_fits(plan, op, side_other, other, placed):
            return side_other
    raise PlacementError(
        "no admissible swing for the %s->%s door: the Plan is rejected and is "
        "not re-solved (openings.md section 4.2 step 3)" % (other, rec))


def sill_mm(op: Opening) -> int:
    """`sill = head_datum - catalogue H`, derived and never stored per instance
    (ADR 0012). 700 at H 1500, 1000 at H 1200 -- which clears a 900 mm counter,
    and is why the kitchen window is the short one."""
    return profile.HEAD_DATUM_MM - op.height_mm
