"""CP-SAT projection where a Room is one OR TWO axis-aligned rectangles.

Ticket 28 item 2: *the solver cost, measured rather than assumed*. This is the
same formulation as `experiments/solver-toy/solver.py` with exactly one thing
changed -- a Room becomes a set of 1..2 *parts* -- so any timing difference is
attributable to that and nothing else.

WHAT CHANGES, AND WHY EACH ONE HAD TO

  variables    2 boxes per eligible Room instead of 1. The second is ABSENT by
               having zero size, not by being an optional interval: measured in
               `smoke_zero_box.py`, AddNoOverlap2D in ortools 9.15.6755 ignores
               a zero-area box, so absence needs no new machinery.
  H4/H5        bind PER PART. The primary carries the Room's own minima; the
               secondary carries a universal leg floor, and only when present.
               This is what stops a second rectangle being a 250 mm slot.
  join         the two parts of one Room must share an edge of at least the leg
               floor. Weaker than that is a pinched room, not an L.
  H6/H8        become an OR over parts -- any part of i touching any part of j,
               any part of a habitable Room reaching a window. Per-part would
               demand a window in every leg.
  H7/H9/H10    H7 stays per-part (no leg of i may touch any leg of j); H9/H10
               move to ROOM level, because an absent part cannot be asked to
               receive flow, and CONTEXT.md's circulation is between Rooms in
               any case.
  relations    a Room-level separation is posted over every part pair, which is
               what "Room a is left of Room b" means once a is two boxes.

WHAT IS NOT MEASURED HERE, STATED SO NOBODY QUOTES IT AS IF IT WERE

  The ground truth in `scenarios.py` is GUILLOTINE, so every truth room is a
  rectangle and the second part is never *needed*. This rig therefore measures
  the COST of the extra freedom, never its benefit. That is the right half to
  measure here -- the benefit is a corpus question (ticket 28 item 6). It also
  makes the "does the solver make an L when it does not have to" reading clean:
  every L this rig produces is gratuitous by construction.
"""
from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ortools.sat.python import cp_model

TOY = Path(__file__).resolve().parents[1] / "solver-toy"
sys.path.insert(0, str(TOY))

from geometry import Rect  # noqa: E402
from scenarios import (  # noqa: E402
    CIRCULATION, HABITABLE, PRIVATE, WET, Brief, Proposal, RoomSpec,
)
from solver import (  # noqa: E402
    LayoutProjector, SolveConfig, SolveResult, _Trace, rank_relations,
    select_relations,
)


# Which Room kinds may be an L. An empty frozenset is the k = 1 control arm.
ALL_KINDS_ALLOWED = None                       # sentinel: every Room may be an L
CIRCULATION_AND_OPEN = frozenset(CIRCULATION | {"living", "dining", "kitchen"})


@dataclass
class PartConfig:
    """Everything about the k <= 2 arm that is not already in SolveConfig."""
    allow: Optional[frozenset] = frozenset()   # kinds that may take a 2nd part
    leg_min: int = 4          # grid units; minimum side of ANY part
    leg_join: int = 4         # grid units; minimum shared edge between parts
    l_penalty: int = 0        # objective cost of using a second part
    force: int = 0            # how many Rooms MUST be two rectangles
    # Design A: the Proposal itself carries 1..2 boxes per Room. When present,
    # presence is FIXED by the Proposal rather than searched, and each part has
    # its own objective target. `force` and `allow` are ignored.
    parts_proposal: Optional[Dict[int, List[Rect]]] = None


@dataclass
class PartResult:
    solve: SolveResult
    parts_of: Dict[int, List[int]] = field(default_factory=dict)
    l_rooms: List[int] = field(default_factory=list)   # rooms that used 2 parts
    eligible: int = 0


def build_part_brief(brief: Brief, proposal: Proposal, pc: PartConfig):
    """Expand a Room-indexed Brief into a part-indexed one.

    A secondary part inherits its parent's `kind` -- so WET / PRIVATE /
    CIRCULATION classification is unchanged -- but carries the universal leg
    floor as its minima rather than the Room's.
    """
    parts_of: Dict[int, List[int]] = {}
    specs: List[RoomSpec] = []
    boxes: List[Rect] = []
    kinds: List[str] = []
    for r, spec in enumerate(brief.rooms):
        parts_of[r] = [len(specs)]
        specs.append(spec)
        boxes.append(proposal.boxes[r])
        kinds.append(spec.kind)
        if pc.parts_proposal is not None:
            allowed = len(pc.parts_proposal.get(r, ())) > 1
        else:
            allowed = pc.allow is ALL_KINDS_ALLOWED or spec.kind in (pc.allow or ())
        if allowed:
            parts_of[r].append(len(specs))
            specs.append(RoomSpec(
                name=f"{spec.name}/2", kind=spec.kind,
                min_w=pc.leg_min, min_h=pc.leg_min, min_area=0,
            ))
            boxes.append(proposal.boxes[r])
            kinds.append(spec.kind)
    pb = Brief(
        name=brief.name + "+parts", env=brief.env, grid_mm=brief.grid_mm,
        rooms=specs, entry=parts_of[brief.entry][0],
        required_adj=[], forbidden_adj=[],
        door_min=brief.door_min, max_aspect=brief.max_aspect,
    )
    return pb, Proposal(boxes=boxes, kinds=kinds), parts_of


class PartProjector(LayoutProjector):
    def __init__(self, brief: Brief, proposal: Proposal, cfg: SolveConfig,
                 pc: PartConfig):
        self.room_brief = brief
        self.room_proposal = proposal
        self.pc = pc
        pb, pp, parts_of = build_part_brief(brief, proposal, pc)
        self.parts_of = parts_of
        self.room_of = {p: r for r, ps in parts_of.items() for p in ps}
        self.secondary = {p for ps in parts_of.values() for p in ps[1:]}
        super().__init__(pb, pp, cfg)

    # -- variables ---------------------------------------------------------
    def _build(self):
        t0 = time.perf_counter()
        m, env, n = self.m, self.brief.env, self.n
        W, H = env.W, env.H

        self.x1 = [m.NewIntVar(0, W, f"x1_{i}") for i in range(n)]
        self.x2 = [m.NewIntVar(0, W, f"x2_{i}") for i in range(n)]
        self.y1 = [m.NewIntVar(0, H, f"y1_{i}") for i in range(n)]
        self.y2 = [m.NewIntVar(0, H, f"y2_{i}") for i in range(n)]
        self.w = [m.NewIntVar(0 if i in self.secondary else 1, W, f"w_{i}")
                  for i in range(n)]
        self.h = [m.NewIntVar(0 if i in self.secondary else 1, H, f"h_{i}")
                  for i in range(n)]

        # Presence. A primary is always present; a secondary is present exactly
        # when it has positive size, and when absent it is pinned to the origin
        # so its coordinates stop being free variables the search has to chase.
        self.pres: Dict[int, cp_model.IntVar] = {}
        for i in range(n):
            if i not in self.secondary:
                continue
            p = m.NewBoolVar(f"pres_{i}")
            self.pres[i] = p
            m.Add(self.w[i] == 0).OnlyEnforceIf(p.Not())
            m.Add(self.h[i] == 0).OnlyEnforceIf(p.Not())
            m.Add(self.x1[i] == 0).OnlyEnforceIf(p.Not())
            m.Add(self.y1[i] == 0).OnlyEnforceIf(p.Not())
            m.Add(self.w[i] >= 1).OnlyEnforceIf(p)

        # Design A: the Proposal already said these Rooms are two rectangles, so
        # presence is FIXED rather than searched. Forcing them against a
        # guillotine truth -- which needs no L at all -- makes this the
        # pessimistic reading of Design A's cost, never the flattering one.
        self.forced = []
        if self.pc.parts_proposal is not None:
            for r, ps in self.parts_of.items():
                if len(ps) > 1:
                    m.Add(self.pres[ps[1]] == 1)
                    self.forced.append(r)
        elif self.pc.force:
            for r in sorted(self.parts_of):
                if len(self.forced) >= self.pc.force:
                    break
                ps = self.parts_of[r]
                if len(ps) > 1:
                    m.Add(self.pres[ps[1]] == 1)
                    self.forced.append(r)

        xiv, yiv = [], []
        for i in range(n):
            xiv.append(m.NewIntervalVar(self.x1[i], self.w[i], self.x2[i], f"xi_{i}"))
            yiv.append(m.NewIntervalVar(self.y1[i], self.h[i], self.y2[i], f"yi_{i}"))
        for k, nt in enumerate(env.notches):
            xiv.append(m.NewIntervalVar(nt.x1, nt.w, nt.x2, f"nx_{k}"))
            yiv.append(m.NewIntervalVar(nt.y1, nt.h, nt.y2, f"ny_{k}"))
        m.AddNoOverlap2D(xiv, yiv)

        self._add_dimensions()
        self._add_coverage()

        self.fixed_relations = 0
        nr = len(self.parts_of)
        self.candidate_relations = nr * (nr - 1) // 2
        if self.cfg.fix_relations:
            self._add_relations()

        self._build_contacts()
        self._add_join()
        self._add_required_forbidden()
        self._add_exterior()
        self._add_wet_cluster()
        self._add_circulation()
        self._add_objective()
        self._hint()
        self.build_time = time.perf_counter() - t0

    # -- H4 / H5, per part -------------------------------------------------
    def _add_dimensions(self):
        m, b = self.m, self.brief
        W, H = self.env.W, self.env.H
        g, t = 250, self.cfg.t_int_mm
        units = self.cfg.area_units
        self.area, self.area_mm2, self.mults = [], [], 0
        k = b.max_aspect

        for i, spec in enumerate(b.rooms):
            a = m.NewIntVar(0, W * H, f"a_{i}")
            m.AddMultiplicationEquality(a, [self.w[i], self.h[i]])
            self.mults += 1
            self.area.append(a)
            on = self.pres.get(i)          # None => unconditional

            def add(c, on=on):
                if on is None:
                    m.Add(c)
                else:
                    m.Add(c).OnlyEnforceIf(on)

            if units == "grid":
                add(self.w[i] >= spec.min_w)
                add(self.h[i] >= spec.min_h)
                add(a >= spec.min_area)
                add(self.w[i] <= k * self.h[i])
                add(self.h[i] <= k * self.w[i])
                continue

            # Clear dimensions, integer millimetres: clear = solved - t_int.
            # An absent part has w = 0, so cw = -t_int; the lower bound is
            # widened to admit that rather than making absence infeasible.
            cw = m.NewIntVar(-g, W * g, f"cw_{i}")
            ch = m.NewIntVar(-g, H * g, f"ch_{i}")
            m.Add(cw == self.w[i] * g - t)
            m.Add(ch == self.h[i] * g - t)
            amm = m.NewIntVar(-g * g, W * g * H * g, f"amm_{i}")
            if units == "mm_direct":
                m.AddMultiplicationEquality(amm, [cw, ch])
                self.mults += 1
            elif units == "mm_affine":
                m.Add(amm == g * g * a - g * t * (self.w[i] + self.h[i]) + t * t)
            else:
                raise ValueError(f"unknown area_units {units!r}")
            self.area_mm2.append(amm)

            if self.cfg.erode_minima and self.cfg.minima_are_clear_grid:
                add(cw >= spec.min_w * g - t)
                add(ch >= spec.min_h * g - t)
                add(a >= spec.min_area)
                add(cw <= k * ch)
                add(ch <= k * cw)
            elif self.cfg.erode_minima:
                add(cw >= spec.min_w * g)
                add(ch >= spec.min_h * g)
                add(amm >= spec.min_area * g * g)
                add(cw <= k * ch)
                add(ch <= k * cw)
            else:
                add(self.w[i] >= spec.min_w)
                add(self.h[i] >= spec.min_h)
                add(a >= spec.min_area)
                add(self.w[i] <= k * self.h[i])
                add(self.h[i] <= k * self.w[i])

    # -- contact, gated by presence ---------------------------------------
    def _build_contacts(self):
        b = self.brief
        self.pairs = [(i, j) for i in range(self.n) for j in range(i + 1, self.n)]
        self.door: Dict[Tuple[int, int], cp_model.IntVar] = {}
        self.any_contact: Dict[Tuple[int, int], cp_model.IntVar] = {}
        for i, j in self.pairs:
            self.door[(i, j)] = self._gated(i, j, b.door_min, "d")
            self.any_contact[(i, j)] = self._gated(i, j, 1, "a")
        # Room-level aggregation: any part of a touching any part of b.
        self.door_r = self._aggregate(self.door, "dr")
        self.any_r = self._aggregate(self.any_contact, "ar")

    def _gated(self, i: int, j: int, L: int, tag: str) -> cp_model.IntVar:
        """`_contact` ANDed with the presence of both parts.

        An absent part has zero size and sits at the origin, so its faces would
        otherwise report spurious flush contacts with whatever is there.
        """
        c = self._contact(i, j, L)
        gates = [self.pres[k] for k in (i, j) if k in self.pres]
        if not gates:
            return c
        m = self.m
        v = m.NewBoolVar(f"{tag}g_{i}_{j}_{L}")
        m.AddBoolAnd([c] + gates).OnlyEnforceIf(v)
        m.AddBoolOr([c.Not()] + [g.Not() for g in gates] + [v])
        return v

    def _aggregate(self, part_lits, tag: str):
        m = self.m
        out: Dict[Tuple[int, int], cp_model.IntVar] = {}
        rooms = sorted(self.parts_of)
        for a in range(len(rooms)):
            for c in range(a + 1, len(rooms)):
                ra, rc = rooms[a], rooms[c]
                lits = [part_lits[tuple(sorted((p, q)))]
                        for p in self.parts_of[ra] for q in self.parts_of[rc]]
                v = m.NewBoolVar(f"{tag}_{ra}_{rc}")
                m.AddBoolOr(lits).OnlyEnforceIf(v)
                for lit in lits:
                    m.AddImplication(lit, v)
                out[(ra, rc)] = v
        return out

    # -- the L is connected ------------------------------------------------
    def _add_join(self):
        """Two parts of one Room share an edge of at least the leg floor.

        Anything shorter is a pinch, not an L -- and `acceptance-bar.md` 9
        dropped the localised-narrowing rule on the grounds that "a rectangular
        Space has no localised anything", which stops being true here.
        """
        m = self.m
        for ps in self.parts_of.values():
            if len(ps) < 2:
                continue
            p, q = ps[0], ps[1]
            join = self._contact(p, q, self.pc.leg_join)
            m.Add(join == 1).OnlyEnforceIf(self.pres[q])

    # -- H6 / H7 at room level --------------------------------------------
    def _add_required_forbidden(self):
        m, b = self.m, self.room_brief
        soft = "required_adj" in self.cfg.soft
        self.req_lits = []
        for i, j in b.required_adj:
            lit = self.door_r[tuple(sorted((i, j)))]
            if soft:
                v = m.NewBoolVar(f"viol_req_{i}_{j}")
                m.AddBoolOr([lit, v])
                self._penalties.append((self.cfg.soft_weight, v))
                self.req_lits.append(v)
            else:
                m.Add(lit == 1)
        for i, j in b.forbidden_adj:
            m.Add(self.any_r[tuple(sorted((i, j)))] == 0)

    # -- H8: a window in ANY leg ------------------------------------------
    def _add_exterior(self):
        m, env = self.m, self.brief.env
        L = self.cfg.window_min
        soft = "exterior" in self.cfg.soft
        self.ext_viol = []
        faces = env.exterior_faces()
        for r, ps in self.parts_of.items():
            if self.room_brief.rooms[r].kind not in HABITABLE:
                continue
            lits = []
            for i in ps:
                for fi, (kind, coord, lo, hi) in enumerate(faces):
                    if hi - lo < L:
                        continue
                    if kind == "v":
                        sides = [("x1", self.x1[i]), ("x2", self.x2[i])]
                        plo, phi, psz = self.y1[i], self.y2[i], self.h[i]
                    else:
                        sides = [("y1", self.y1[i]), ("y2", self.y2[i])]
                        plo, phi, psz = self.x1[i], self.x2[i], self.w[i]
                    for sname, svar in sides:
                        v = m.NewBoolVar(f"ext_{i}_{fi}_{sname}")
                        m.Add(svar == coord).OnlyEnforceIf(v)
                        m.Add(psz >= L).OnlyEnforceIf(v)
                        m.Add(plo <= hi - L).OnlyEnforceIf(v)
                        m.Add(phi >= lo + L).OnlyEnforceIf(v)
                        if i in self.pres:
                            m.AddImplication(v, self.pres[i])
                        lits.append(v)
            if soft:
                v = m.NewBoolVar(f"viol_ext_{r}")
                m.AddBoolOr(lits + [v])
                self._penalties.append((self.cfg.soft_weight, v))
                self.ext_viol.append(v)
            else:
                m.AddBoolOr(lits)

    # -- H9 / H10 at room level -------------------------------------------
    def _add_wet_cluster(self):
        b = self.room_brief
        wet = b.indices(sorted(WET))
        self.wet_viol = []
        if len(wet) < 2:
            return
        soft = "wet_cluster" in self.cfg.soft
        lits = {p: v for p, v in self.any_r.items() if p[0] in wet and p[1] in wet}
        self.wet_viol = self._flow(wet, wet[0], lits, "wet", slack=soft)
        for s in self.wet_viol:
            self._penalties.append((self.cfg.soft_weight, s))

    def _add_circulation(self):
        b = self.room_brief
        blocked = [i for i, r in enumerate(b.rooms)
                   if r.kind in PRIVATE and i != b.entry]
        soft = "circulation" in self.cfg.soft
        self.circ_viol = self._flow(
            list(range(len(b.rooms))), b.entry, self.door_r, "circ",
            blocked=blocked, slack=soft,
        )
        for s in self.circ_viol:
            self._penalties.append((self.cfg.soft_weight, s))

    # -- relations: a Room relation binds every part -----------------------
    def _add_relations(self):
        """Separation relations, extracted in the PART index space.

        When every Room is one part this is bit-identical to the shipped
        extractor. When a Room is two, the generalisation is forced rather than
        chosen: an L and the Room sitting in its notch have a POSITIVE best
        separation cost on all four options -- no axis separates them -- and the
        shipped extractor abstains only on a small *margin*, never on a positive
        cost. It would therefore assert a separation the truth contradicts,
        which is the confident-wrong relation ticket 24 measured as fatal. Their
        PARTS are separable, so extracting over parts keeps the constraint that
        abstaining would have thrown away.

        Same-Room part pairs are excluded: they are joined, not separated.
        """
        pp = self.pc.parts_proposal
        if pp is None:
            chosen, _ab, _cy = select_relations(
                rank_relations(self.room_proposal.boxes),
                self.cfg.relation_confidence, len(self.parts_of),
            )
            for axis, a, b in chosen:
                for p in self.parts_of[a]:
                    for q in self.parts_of[b]:
                        # Gate on presence. An ABSENT part is pinned to the
                        # origin with zero size, so an ungated `x2[p] <= x1[q]`
                        # with q absent reads `x2[p] <= 0` and forces a present
                        # primary to zero width -- the model comes back
                        # INFEASIBLE for a reason that is nothing to do with the
                        # layout. Found by preview: the free arms were reporting
                        # 36 % INFEASIBLE where the control was 0 %.
                        gates = [self.pres[k] for k in (p, q) if k in self.pres]
                        c = (self.x2[p] <= self.x1[q] if axis == "x"
                             else self.y2[p] <= self.y1[q])
                        if gates:
                            self.m.Add(c).OnlyEnforceIf(gates)
                        else:
                            self.m.Add(c)
                self.fixed_relations += 1
            return

        boxes = [None] * self.n
        for r, ps in self.parts_of.items():
            for k, part in enumerate(ps):
                boxes[part] = pp[r][k]
        same = {(min(p, q), max(p, q))
                for ps in self.parts_of.values()
                for p in ps for q in ps if p != q}
        ranked = [row for row in rank_relations(boxes)
                  if (min(row[3], row[4]), max(row[3], row[4])) not in same]
        chosen, abstained, _cy = select_relations(
            ranked, self.cfg.relation_confidence, self.n)
        self.abstained = len(abstained)
        for axis, a, b in chosen:
            if axis == "x":
                self.m.Add(self.x2[a] <= self.x1[b])
            else:
                self.m.Add(self.y2[a] <= self.y1[b])
            self.fixed_relations += 1

    # -- objective: primaries chase the Proposal, secondaries are free -----
    def _add_objective(self):
        m, cfg, p = self.m, self.cfg, self.room_proposal.boxes
        W, H = self.env.W, self.env.H
        bound = 4 * (W + H)
        terms = []
        pp = self.pc.parts_proposal
        for r, ps in self.parts_of.items():
            i = ps[0]
            if pp is not None:
                for k, part in enumerate(ps):
                    tgt = pp[r][k]
                    terms.append(self._abs_dev(self.x1[part] - tgt.x1, bound, f"dx1_{r}_{k}"))
                    terms.append(self._abs_dev(self.x2[part] - tgt.x2, bound, f"dx2_{r}_{k}"))
                    terms.append(self._abs_dev(self.y1[part] - tgt.y1, bound, f"dy1_{r}_{k}"))
                    terms.append(self._abs_dev(self.y2[part] - tgt.y2, bound, f"dy2_{r}_{k}"))
                continue
            if cfg.objective.startswith("corners"):
                terms.append(self._abs_dev(self.x1[i] - p[r].x1, bound, f"dx1_{r}"))
                terms.append(self._abs_dev(self.x2[i] - p[r].x2, bound, f"dx2_{r}"))
                terms.append(self._abs_dev(self.y1[i] - p[r].y1, bound, f"dy1_{r}"))
                terms.append(self._abs_dev(self.y2[i] - p[r].y2, bound, f"dy2_{r}"))
            else:
                terms.append(self._abs_dev(
                    self.x1[i] + self.x2[i] - p[r].cx2, bound, f"dcx_{r}"))
                terms.append(self._abs_dev(
                    self.y1[i] + self.y2[i] - p[r].cy2, bound, f"dcy_{r}"))
        self.distance_terms = list(terms)
        weighted = [(1, t) for t in terms]
        if self.pc.l_penalty:
            for v in self.pres.values():
                weighted.append((self.pc.l_penalty, v))
        weighted.extend(self._penalties)
        m.Minimize(sum(c * v for c, v in weighted))

    def _hint(self):
        if not self.cfg.hint:
            return
        W, H = self.env.W, self.env.H
        pp = self.pc.parts_proposal
        for r, ps in self.parts_of.items():
            for k, part in enumerate(ps):
                box = pp[r][k] if pp is not None else self.room_proposal.boxes[r]
                if k and pp is None:
                    continue
                x1 = max(0, min(W - 1, box.x1))
                y1 = max(0, min(H - 1, box.y1))
                x2 = max(x1 + 1, min(W, box.x2))
                y2 = max(y1 + 1, min(H, box.y2))
                self.m.AddHint(self.x1[part], x1)
                self.m.AddHint(self.x2[part], x2)
                self.m.AddHint(self.y1[part], y1)
                self.m.AddHint(self.y2[part], y2)
            for q in ps[1:]:
                self.m.AddHint(self.pres[q], 1 if r in self.forced else 0)

    # -- solve, reporting which Rooms became Ls ----------------------------
    def solve(self) -> PartResult:
        cfg = self.cfg
        s = cp_model.CpSolver()
        s.parameters.max_time_in_seconds = cfg.time_limit_s
        s.parameters.num_workers = cfg.workers
        s.parameters.random_seed = cfg.seed
        tr = _Trace()
        t0 = time.perf_counter()
        status = s.Solve(self.m, tr)
        wall = time.perf_counter() - t0
        proto = self.m.Proto()
        stats = {
            "variables": len(proto.variables),
            "constraints": len(proto.constraints),
            "pairs": len(self.pairs),
            "fixed_relations": self.fixed_relations,
            "multiplications": self.mults,
            "candidate_relations": self.candidate_relations,
            "parts": self.n,
        }
        res = SolveResult(status=s.StatusName(status), wall_time_s=wall,
                          build_time_s=self.build_time, model_stats=stats,
                          trace=tr.rows)
        out = PartResult(solve=res, parts_of=self.parts_of,
                         eligible=len(self.pres))
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            res.rooms = [Rect(s.Value(self.x1[i]), s.Value(self.y1[i]),
                              s.Value(self.x2[i]), s.Value(self.y2[i]))
                         for i in range(self.n)]
            res.objective = int(s.ObjectiveValue())
            res.best_bound = s.BestObjectiveBound()
            res.proposal_distance = sum(s.Value(t) for t in self.distance_terms)
            res.violations = {
                "required_adj": sum(s.Value(v) for v in self.req_lits),
                "exterior": sum(s.Value(v) for v in self.ext_viol),
                "wet_cluster": sum(s.Value(v) for v in self.wet_viol),
                "unreachable_rooms": sum(s.Value(v) for v in self.circ_viol),
                "uncovered_area": (s.Value(self.cov_slack)
                                   if self.cov_slack is not None else 0),
            }
            out.l_rooms = [r for r, ps in self.parts_of.items()
                           if len(ps) > 1 and s.Value(self.pres[ps[1]])]
        return out


def project_parts(brief, proposal, cfg: SolveConfig, pc: PartConfig) -> PartResult:
    return PartProjector(brief, proposal, cfg, pc).solve()
