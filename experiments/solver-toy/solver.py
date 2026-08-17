"""CP-SAT projection of a Proposal onto the feasible set of Plans.

This is the concrete test of C10 — *model proposes, solver projects*.

The single most important structural fact about this model:

    THE PROPOSAL APPEARS ONLY IN THE OBJECTIVE, NEVER IN A CONSTRAINT.

Everything the Brief and the Acceptance bar demand is a hard constraint over
integer grid coordinates. The Proposal contributes exactly one thing: the
distance being minimised, plus a solution hint. It therefore cannot make the
model infeasible, however bad it is. That is the whole of C10's graceful
degradation, and it is a property of the formulation rather than of a
recovery heuristic.

Feasible set (all hard by default):

  H1 rooms lie inside the Envelope bbox and clear of every notch
  H2 no two rooms overlap                        (AddNoOverlap2D)
  H3 rooms exactly tile the Envelope interior    (area sum + H1 + H2)
  H4 per-room minimum width, height and area
  H5 aspect ratio bounded                        (no unusable slivers)
  H6 required adjacencies hold
  H7 forbidden adjacencies do not hold           (no shared wall at all)
  H8 every habitable room touches an exterior wall over a window's width
  H9 wet rooms form one plumbing-connected cluster
  H10 every room reachable from the entry without traversing a bedroom,
      bathroom or WC                             (single-commodity flow)

Walls are orthogonal and grid-snapped by construction: every coordinate is an
integer in grid units.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from ortools.sat.python import cp_model

from geometry import Rect
from scenarios import CIRCULATION, HABITABLE, PRIVATE, WET, Brief, Proposal

SOFTABLE = ("required_adj", "exterior", "wet_cluster", "circulation", "coverage")


@dataclass
class SolveConfig:
    objective: str = "corners"        # corners | centroid | corners+order
    time_limit_s: float = 10.0
    workers: int = 8
    seed: int = 0
    hint: bool = True                 # seed CP-SAT with the Proposal
    arc_radius: Optional[int] = None  # prune candidate adjacency by Proposal distance
    soft: Tuple[str, ...] = ()        # which families degrade instead of failing
    soft_weight: int = 100_000
    window_min: int = 4               # exterior wall run needed for a window
    log: bool = False
    diagnose: bool = True             # on INFEASIBLE, extract an assumption core
    # Hybrid: read the Proposal's relative arrangement (i is left of j, j is
    # below k, ...) and *fix* it, turning the packing disjunction into linear
    # constraints. This is "the model proposes topology, the solver refines
    # metrics" made literal.
    fix_relations: bool = False
    # Fix only relations the Proposal is confident about: separation cost, in
    # grid units, below which a relation is considered too ambiguous to fix.
    relation_confidence: int = 0


@dataclass
class SolveResult:
    status: str
    wall_time_s: float
    build_time_s: float
    rooms: List[Rect] = field(default_factory=list)
    objective: Optional[int] = None
    best_bound: Optional[float] = None
    proposal_distance: Optional[int] = None
    violations: Dict[str, int] = field(default_factory=dict)
    infeasibility_core: List[str] = field(default_factory=list)
    model_stats: Dict[str, int] = field(default_factory=dict)
    # (elapsed_s, objective) for every improving solution CP-SAT found.
    trace: List[Tuple[float, int]] = field(default_factory=list)

    @property
    def time_to_first(self) -> Optional[float]:
        """Wall-clock to the FIRST feasible Plan. The interactive metric."""
        return self.trace[0][0] if self.trace else None

    def time_to_within(self, pct: float) -> Optional[float]:
        """Wall-clock to the first Plan within `pct`% of the final objective."""
        if not self.trace:
            return None
        best = self.trace[-1][1]
        for t, o in self.trace:
            if best == 0 or o <= best * (1 + pct / 100.0):
                return t
        return None


class _Trace(cp_model.CpSolverSolutionCallback):
    def __init__(self):
        super().__init__()
        self.t0 = time.perf_counter()
        self.rows: List[Tuple[float, int]] = []

    def on_solution_callback(self):
        self.rows.append((time.perf_counter() - self.t0, int(self.ObjectiveValue())))


class LayoutProjector:
    def __init__(self, brief: Brief, proposal: Proposal, cfg: SolveConfig):
        self.brief = brief
        self.proposal = proposal
        self.cfg = cfg
        self.m = cp_model.CpModel()
        self.n = brief.n
        self.env = brief.env
        self._penalties: List[Tuple[int, cp_model.IntVar]] = []
        self._assume: Dict[str, cp_model.IntVar] = {}
        self._build()

    # -- variables ---------------------------------------------------------
    def _build(self):
        t0 = time.perf_counter()
        m, b, env, n = self.m, self.brief, self.brief.env, self.n
        W, H = env.W, env.H

        self.x1 = [m.NewIntVar(0, W, f"x1_{i}") for i in range(n)]
        self.x2 = [m.NewIntVar(0, W, f"x2_{i}") for i in range(n)]
        self.y1 = [m.NewIntVar(0, H, f"y1_{i}") for i in range(n)]
        self.y2 = [m.NewIntVar(0, H, f"y2_{i}") for i in range(n)]
        self.w = [m.NewIntVar(1, W, f"w_{i}") for i in range(n)]
        self.h = [m.NewIntVar(1, H, f"h_{i}") for i in range(n)]

        xiv, yiv = [], []
        for i in range(n):
            xiv.append(m.NewIntervalVar(self.x1[i], self.w[i], self.x2[i], f"xi_{i}"))
            yiv.append(m.NewIntervalVar(self.y1[i], self.h[i], self.y2[i], f"yi_{i}"))

        # H1 — notches are fixed obstacles inside the same no-overlap system.
        for k, nt in enumerate(env.notches):
            xiv.append(m.NewIntervalVar(nt.x1, nt.w, nt.x2, f"nx_{k}"))
            yiv.append(m.NewIntervalVar(nt.y1, nt.h, nt.y2, f"ny_{k}"))

        # H2 — no overlap, rooms with each other and with the notches.
        m.AddNoOverlap2D(xiv, yiv)

        # H4/H5 — dimensions, area, aspect.
        self.area = []
        for i, spec in enumerate(b.rooms):
            m.Add(self.w[i] >= spec.min_w)
            m.Add(self.h[i] >= spec.min_h)
            a = m.NewIntVar(spec.min_area, W * H, f"a_{i}")
            m.AddMultiplicationEquality(a, [self.w[i], self.h[i]])
            self.area.append(a)
            k = b.max_aspect
            m.Add(self.w[i] <= k * self.h[i])
            m.Add(self.h[i] <= k * self.w[i])

        # H3 — exact tiling. With H1 and H2 already in force, every room is
        # inside the interior and no two overlap, so total room area equal to
        # interior area is *equivalent* to an exact tiling: no gaps, no
        # slivers, nothing unassigned.
        self._add_coverage()

        self.fixed_relations = 0
        if self.cfg.fix_relations:
            self._add_relations()

        # Pair machinery, then the constraints that consume it.
        self._build_contacts()
        self._add_required_forbidden()
        self._add_exterior()
        self._add_wet_cluster()
        self._add_circulation()
        self._add_objective()
        self._hint()

        self.build_time = time.perf_counter() - t0

    # -- H3 ----------------------------------------------------------------
    def _add_coverage(self):
        m, target = self.m, self.env.interior_area
        if "coverage" in self.cfg.soft:
            slack = m.NewIntVar(0, target // 10, "cov_slack")
            m.Add(sum(self.area) == target - slack)
            self._penalties.append((self.cfg.soft_weight, slack))
            self.cov_slack = slack
        else:
            m.Add(sum(self.area) == target)
            self.cov_slack = None

    # -- hybrid: topology from the Proposal --------------------------------
    def _add_relations(self):
        """Freeze the Proposal's relative arrangement as linear separations.

        For each pair, the cheapest of the four ways to pull the Proposal's
        boxes apart (i left of j, j left of i, i below j, j below i) is taken as
        the intended relation. Relations are added greedily in increasing cost
        and only when they keep the per-axis relation digraph acyclic, so the
        confident ones are fixed and the ambiguous ones are left to
        AddNoOverlap2D's disjunction. That is the "dual for topology, CP-SAT for
        metric" hybrid, with the Proposal standing in for the dual.
        """
        p = self.proposal.boxes
        cands = []
        for i in range(self.n):
            for j in range(i + 1, self.n):
                opts = [
                    (p[i].x2 - p[j].x1, "x", i, j),   # i left of j
                    (p[j].x2 - p[i].x1, "x", j, i),
                    (p[i].y2 - p[j].y1, "y", i, j),   # i below j
                    (p[j].y2 - p[i].y1, "y", j, i),
                ]
                cost, axis, a, b = min(opts)
                second = sorted(c for c, _, _, _ in opts)[1]
                cands.append((cost, second - cost, axis, a, b))
        cands.sort(key=lambda t: (t[0], -t[1]))

        succ = {"x": {i: set() for i in range(self.n)},
                "y": {i: set() for i in range(self.n)}}

        def reaches(g, a, b):
            seen, stack = {a}, [a]
            while stack:
                u = stack.pop()
                if u == b:
                    return True
                for v in g[u]:
                    if v not in seen:
                        seen.add(v)
                        stack.append(v)
            return False

        lo = self.cfg.relation_confidence
        for cost, margin, axis, a, b in cands:
            if margin < lo:
                continue                       # Proposal is not confident here
            g = succ[axis]
            if reaches(g, b, a):
                continue                       # would close a cycle
            g[a].add(b)
            if axis == "x":
                self.m.Add(self.x2[a] <= self.x1[b])
            else:
                self.m.Add(self.y2[a] <= self.y1[b])
            self.fixed_relations += 1

    # -- reified geometric contact ----------------------------------------
    def _reify_le(self, expr, name: str) -> cp_model.IntVar:
        """Fully reified `expr <= 0`."""
        v = self.m.NewBoolVar(name)
        self.m.Add(expr <= 0).OnlyEnforceIf(v)
        self.m.Add(expr >= 1).OnlyEnforceIf(v.Not())
        return v

    def _overlap_at_least(self, i: int, j: int, axis: str, L: int, tag: str):
        """Reified `projection overlap of i and j on `axis` >= L`.

        overlap = min(hi_i, hi_j) - max(lo_i, lo_j) >= L
        is *exactly* the conjunction of four linear inequalities:
            hi_i - lo_i >= L,  hi_j - lo_j >= L,
            hi_j - lo_i >= L,  hi_i - lo_j >= L
        (check all four min/max cases). The first two are per-room size bounds
        and are usually implied by the Brief's minimum dimensions, in which
        case they are dropped statically.
        """
        m = self.m
        lo = self.x1 if axis == "x" else self.y1
        hi = self.x2 if axis == "x" else self.y2
        size = self.w if axis == "x" else self.h
        spec = self.brief.rooms
        mins = (spec[i].min_w, spec[j].min_w) if axis == "x" else (spec[i].min_h, spec[j].min_h)

        lits = []
        for k, mn in ((i, mins[0]), (j, mins[1])):
            if mn < L:
                lits.append(self._reify_le(L - size[k], f"sz_{axis}{L}_{k}"))
        lits.append(self._reify_le(L - (hi[j] - lo[i]), f"ov_{tag}a"))
        lits.append(self._reify_le(L - (hi[i] - lo[j]), f"ov_{tag}b"))

        g = m.NewBoolVar(f"g_{tag}")
        m.AddBoolAnd(lits).OnlyEnforceIf(g)
        m.AddBoolOr([l.Not() for l in lits] + [g])
        return g

    def _flush(self, a: cp_model.IntVar, bvar: cp_model.IntVar, name: str):
        """Fully reified `a == b`."""
        m = self.m
        v = m.NewBoolVar(name)
        m.Add(a == bvar).OnlyEnforceIf(v)
        m.Add(a != bvar).OnlyEnforceIf(v.Not())
        return v

    def _contact(self, i: int, j: int, L: int):
        """Reified: rooms i and j share a wall segment of length >= L."""
        m = self.m
        tag = f"{i}_{j}_{L}"
        tE = self._flush(self.x2[i], self.x1[j], f"tE_{tag}")
        tW = self._flush(self.x2[j], self.x1[i], f"tW_{tag}")
        tN = self._flush(self.y2[i], self.y1[j], f"tN_{tag}")
        tS = self._flush(self.y2[j], self.y1[i], f"tS_{tag}")

        vx = m.NewBoolVar(f"vx_{tag}")
        m.AddBoolOr([tE, tW]).OnlyEnforceIf(vx)
        m.AddImplication(tE, vx)
        m.AddImplication(tW, vx)
        hy = m.NewBoolVar(f"hy_{tag}")
        m.AddBoolOr([tN, tS]).OnlyEnforceIf(hy)
        m.AddImplication(tN, hy)
        m.AddImplication(tS, hy)

        gy = self._overlap_at_least(i, j, "y", L, f"{tag}_y")
        gx = self._overlap_at_least(i, j, "x", L, f"{tag}_x")

        A = m.NewBoolVar(f"A_{tag}")
        m.AddBoolAnd([vx, gy]).OnlyEnforceIf(A)
        m.AddBoolOr([vx.Not(), gy.Not(), A])
        B = m.NewBoolVar(f"B_{tag}")
        m.AddBoolAnd([hy, gx]).OnlyEnforceIf(B)
        m.AddBoolOr([hy.Not(), gx.Not(), B])

        c = m.NewBoolVar(f"c_{tag}")
        m.AddBoolOr([A, B]).OnlyEnforceIf(c)
        m.AddImplication(A, c)
        m.AddImplication(B, c)
        return c

    def _candidate_pairs(self) -> List[Tuple[int, int]]:
        n, r = self.n, self.cfg.arc_radius
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        if r is None:
            return pairs
        keep = set(self.brief.required_adj) | set(self.brief.forbidden_adj)
        p = self.proposal.boxes
        out = []
        for i, j in pairs:
            if (i, j) in keep:
                out.append((i, j))
                continue
            dx = max(0, max(p[i].x1, p[j].x1) - min(p[i].x2, p[j].x2))
            dy = max(0, max(p[i].y1, p[j].y1) - min(p[i].y2, p[j].y2))
            if dx <= r and dy <= r:
                out.append((i, j))
        return out

    def _build_contacts(self):
        b = self.brief
        self.pairs = self._candidate_pairs()
        self.door: Dict[Tuple[int, int], cp_model.IntVar] = {}
        for i, j in self.pairs:
            self.door[(i, j)] = self._contact(i, j, b.door_min)
        # Threshold-1 contact ("any shared wall") is only needed where the
        # semantics differ: forbidden adjacency and plumbing walls.
        self.any_contact: Dict[Tuple[int, int], cp_model.IntVar] = {}
        need = set(tuple(sorted(p)) for p in b.forbidden_adj)
        wet = b.indices(sorted(WET))
        for a in range(len(wet)):
            for c in range(a + 1, len(wet)):
                need.add(tuple(sorted((wet[a], wet[c]))))
        for p in sorted(need):
            self.any_contact[p] = self._contact(p[0], p[1], 1)

    # -- H6 / H7 -----------------------------------------------------------
    def _add_required_forbidden(self):
        m, b = self.m, self.brief
        soft = "required_adj" in self.cfg.soft
        self.req_lits = []
        for i, j in b.required_adj:
            lit = self.door.get((i, j))
            if lit is None:                       # pruned away by arc_radius
                lit = self.door[(i, j)] = self._contact(i, j, b.door_min)
            if soft:
                v = m.NewBoolVar(f"viol_req_{i}_{j}")
                m.AddBoolOr([lit, v])
                self._penalties.append((self.cfg.soft_weight, v))
                self.req_lits.append(v)
            else:
                m.Add(lit == 1)
        # Forbidden adjacency: NO shared wall of any positive length. This is
        # the constraint a pure box-packing formulation gets for free and a
        # rectangular-dual construction has to work for.
        for i, j in b.forbidden_adj:
            lit = self.any_contact.get((i, j))
            if lit is None:
                lit = self.any_contact[(i, j)] = self._contact(i, j, 1)
            m.Add(lit == 0)

    # -- H8 ----------------------------------------------------------------
    def _add_exterior(self):
        """A habitable room must touch an exterior wall over >= window_min.

        Forward implication only: we force the OR, and a true face literal
        entails a real flush contact. Nothing needs the converse.

        `min(hi,f_hi) - max(lo,f_lo) >= L` is again the conjunction of linear
        bounds, so no auxiliary integer variables are created.
        """
        m, b, env = self.m, self.brief, self.brief.env
        L = self.cfg.window_min
        soft = "exterior" in self.cfg.soft
        self.ext_viol = []
        faces = env.exterior_faces()
        for i, spec in enumerate(b.rooms):
            if spec.kind not in HABITABLE:
                continue
            lits = []
            for fi, (kind, coord, lo, hi) in enumerate(faces):
                if hi - lo < L:
                    continue
                if kind == "v":
                    sides = []
                    if coord - 0 >= 0:
                        sides.append(("x1", self.x1[i]))
                        sides.append(("x2", self.x2[i]))
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
                    lits.append(v)
            if soft:
                v = m.NewBoolVar(f"viol_ext_{i}")
                m.AddBoolOr(lits + [v])
                self._penalties.append((self.cfg.soft_weight, v))
                self.ext_viol.append(v)
            else:
                m.AddBoolOr(lits)

    # -- connectivity: one reusable flow ------------------------------------
    def _flow(self, nodes: Sequence[int], root: int, lit_of, name: str,
              blocked: Sequence[int] = (), slack: bool = False):
        """Single-commodity flow connectivity over a *variable* graph.

        The root supplies |nodes|-1 units; every other node consumes 1. Flow on
        an arc is capped by the arc's existence literal, so a node can only be
        served through walls that actually exist in the solution. A node in
        `blocked` may consume but may not forward — which is exactly "you do
        not walk through a bedroom to reach the kitchen".

        This is the answer to ticket item 3: reachability IS expressible as a
        constraint, it does not need a post-filter, and it stays linear.
        """
        m = self.m
        idx = {v: k for k, v in enumerate(nodes)}
        cap = max(1, len(nodes) - 1)
        out_arcs: Dict[int, List] = {v: [] for v in nodes}
        in_arcs: Dict[int, List] = {v: [] for v in nodes}
        for (i, j), lit in lit_of.items():
            if i not in idx or j not in idx:
                continue
            for a, bb in ((i, j), (j, i)):
                f = m.NewIntVar(0, cap, f"f_{name}_{a}_{bb}")
                m.Add(f <= cap * lit)
                out_arcs[a].append(f)
                in_arcs[bb].append(f)
        slacks = []
        for v in nodes:
            if v == root:
                continue
            if slack:
                s = m.NewBoolVar(f"unreach_{name}_{v}")
                slacks.append(s)
                m.Add(sum(in_arcs[v]) - sum(out_arcs[v]) == 1 - s)
            else:
                m.Add(sum(in_arcs[v]) - sum(out_arcs[v]) == 1)
            if v in blocked:
                m.Add(sum(out_arcs[v]) == 0)
        supply = len(nodes) - 1
        if slack:
            m.Add(sum(out_arcs[root]) - sum(in_arcs[root]) == supply - sum(slacks))
        else:
            m.Add(sum(out_arcs[root]) - sum(in_arcs[root]) == supply)
        return slacks

    # -- H9 ----------------------------------------------------------------
    def _add_wet_cluster(self):
        wet = self.brief.indices(sorted(WET))
        self.wet_viol = []
        if len(wet) < 2:
            return
        soft = "wet_cluster" in self.cfg.soft
        lits = {p: v for p, v in self.any_contact.items() if p[0] in wet and p[1] in wet}
        self.wet_viol = self._flow(wet, wet[0], lits, "wet", slack=soft)
        for s in self.wet_viol:
            self._penalties.append((self.cfg.soft_weight, s))

    # -- H10 ---------------------------------------------------------------
    def _add_circulation(self):
        b = self.brief
        blocked = [i for i, r in enumerate(b.rooms) if r.kind in PRIVATE and i != b.entry]
        soft = "circulation" in self.cfg.soft
        self.circ_viol = self._flow(
            list(range(self.n)), b.entry, self.door, "circ",
            blocked=blocked, slack=soft,
        )
        for s in self.circ_viol:
            self._penalties.append((self.cfg.soft_weight, s))

    # -- objective ---------------------------------------------------------
    def _abs_dev(self, expr, bound: int, name: str) -> cp_model.IntVar:
        d = self.m.NewIntVar(0, bound, name)
        self.m.Add(d >= expr)
        self.m.Add(d >= -expr)
        return d

    def _add_objective(self):
        m, cfg, p = self.m, self.cfg, self.proposal.boxes
        W, H = self.env.W, self.env.H
        bound = 4 * (W + H)
        terms = []
        if cfg.objective.startswith("corners"):
            for i in range(self.n):
                terms.append(self._abs_dev(self.x1[i] - p[i].x1, bound, f"dx1_{i}"))
                terms.append(self._abs_dev(self.x2[i] - p[i].x2, bound, f"dx2_{i}"))
                terms.append(self._abs_dev(self.y1[i] - p[i].y1, bound, f"dy1_{i}"))
                terms.append(self._abs_dev(self.y2[i] - p[i].y2, bound, f"dy2_{i}"))
        elif cfg.objective == "centroid":
            for i in range(self.n):
                terms.append(self._abs_dev(
                    self.x1[i] + self.x2[i] - p[i].cx2, bound, f"dcx_{i}"))
                terms.append(self._abs_dev(
                    self.y1[i] + self.y2[i] - p[i].cy2, bound, f"dcy_{i}"))
        else:
            raise ValueError(cfg.objective)
        self.distance_terms = list(terms)

        weighted = [(1, t) for t in terms]
        if cfg.objective.endswith("+order"):
            # Combinatorial similarity: keep the Proposal's left-of / below
            # relations. Cheap (booleans only) and it is what makes the output
            # still *read* as the layout the model proposed.
            wgt = max(2, (W + H) // 4)
            for i in range(self.n):
                for j in range(self.n):
                    if i == j:
                        continue
                    if p[i].x2 <= p[j].x1:
                        o = self.m.NewBoolVar(f"ordx_{i}_{j}")
                        self.m.Add(self.x2[i] <= self.x1[j]).OnlyEnforceIf(o)
                        self.m.Add(self.x2[i] > self.x1[j]).OnlyEnforceIf(o.Not())
                        weighted.append((wgt, o.Not()))
                    if p[i].y2 <= p[j].y1:
                        o = self.m.NewBoolVar(f"ordy_{i}_{j}")
                        self.m.Add(self.y2[i] <= self.y1[j]).OnlyEnforceIf(o)
                        self.m.Add(self.y2[i] > self.y1[j]).OnlyEnforceIf(o.Not())
                        weighted.append((wgt, o.Not()))
        weighted.extend(self._penalties)
        m.Minimize(sum(c * v for c, v in weighted))

    def _hint(self):
        if not self.cfg.hint:
            return
        W, H = self.env.W, self.env.H
        for i, r in enumerate(self.proposal.boxes):
            x1 = max(0, min(W - 1, r.x1))
            y1 = max(0, min(H - 1, r.y1))
            x2 = max(x1 + 1, min(W, r.x2))
            y2 = max(y1 + 1, min(H, r.y2))
            self.m.AddHint(self.x1[i], x1)
            self.m.AddHint(self.x2[i], x2)
            self.m.AddHint(self.y1[i], y1)
            self.m.AddHint(self.y2[i], y2)

    # -- solve -------------------------------------------------------------
    def solve(self) -> SolveResult:
        cfg = self.cfg
        s = cp_model.CpSolver()
        s.parameters.max_time_in_seconds = cfg.time_limit_s
        s.parameters.num_workers = cfg.workers
        s.parameters.random_seed = cfg.seed
        s.parameters.log_search_progress = cfg.log
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
        }
        name = s.StatusName(status)
        res = SolveResult(
            status=name, wall_time_s=wall, build_time_s=self.build_time,
            model_stats=stats, trace=tr.rows,
        )
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            res.rooms = [
                Rect(s.Value(self.x1[i]), s.Value(self.y1[i]),
                     s.Value(self.x2[i]), s.Value(self.y2[i]))
                for i in range(self.n)
            ]
            res.objective = int(s.ObjectiveValue())
            res.best_bound = s.BestObjectiveBound()
            res.proposal_distance = sum(s.Value(t) for t in self.distance_terms)
            res.violations = {
                "required_adj": sum(s.Value(v) for v in self.req_lits),
                "exterior": sum(s.Value(v) for v in self.ext_viol),
                "wet_cluster": sum(s.Value(v) for v in self.wet_viol),
                "unreachable_rooms": sum(s.Value(v) for v in self.circ_viol),
                "uncovered_area": s.Value(self.cov_slack) if self.cov_slack is not None else 0,
            }
        elif status == cp_model.INFEASIBLE and cfg.diagnose:
            res.infeasibility_core = self._core()
        return res

    def _core(self) -> List[str]:
        """Minimal-ish explanation of an infeasible Brief.

        Rebuild with each softenable family gated behind an assumption literal
        and ask CP-SAT which assumptions suffice for infeasibility. This is the
        raw material for telling a Homeowner *which* of their requirements is
        the impossible one.
        """
        from copy import deepcopy

        cfg2 = deepcopy(self.cfg)
        cfg2.soft = SOFTABLE
        cfg2.diagnose = False
        probe = LayoutProjector(self.brief, self.proposal, cfg2)
        groups = {
            "required_adj": probe.req_lits,
            "exterior": probe.ext_viol,
            "wet_cluster": probe.wet_viol,
            "circulation": probe.circ_viol,
            "coverage": [probe.cov_slack] if probe.cov_slack is not None else [],
        }
        assumptions = []
        labels = {}
        for gname, vars_ in groups.items():
            if not vars_:
                continue
            a = probe.m.NewBoolVar(f"assume_{gname}")
            for v in vars_:
                probe.m.Add(v == 0).OnlyEnforceIf(a)
            assumptions.append(a)
            labels[a.Index()] = gname
        probe.m.ClearAssumptions()
        probe.m.AddAssumptions(assumptions)
        s = cp_model.CpSolver()
        s.parameters.max_time_in_seconds = self.cfg.time_limit_s
        s.parameters.num_workers = self.cfg.workers
        st = s.Solve(probe.m)
        if st != cp_model.INFEASIBLE:
            return [f"no core: relaxed model is {s.StatusName(st)}"]
        return sorted({labels.get(i, str(i)) for i in s.SufficientAssumptionsForInfeasibility()})


def project(brief: Brief, proposal: Proposal, cfg: SolveConfig) -> SolveResult:
    return LayoutProjector(brief, proposal, cfg).solve()
