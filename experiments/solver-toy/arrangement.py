"""The arrangement metric of `docs/spec/proposer.md` 5, and the machinery to
inject known doses of it into a Proposal the solver is known to accept.

Ticket 24. The metric is a **proxy** — it claims that a Proposal scoring badly
on per-pair separation-direction agreement is a Proposal the solver will fail to
project. Nothing has tested that claim, and this map has already been bitten by
one unvalidated proxy (overlap, refuted by *Proposer architecture survey*).

Everything here runs the solver's own extractor — `solver.rank_relations` and
`solver.select_relations` — rather than a copy of it, which is what 5.1 means by
"the metric cannot drift from the thing it predicts".

Two definitions of *confident-wrong* are computed, and they are not the same
number:

* **argmin-wrong** — the asserted direction is not the truth's `argmin`. This is
  5.1 read literally.
* **violated** — the asserted separation is *false of the truth geometry*, i.e.
  its cost against the truth boxes is positive.

They differ because two boxes can be separated on both axes at once — a diagonal
pair in a tiling satisfies (say) both "i left of j" and "i below j". Asserting
the non-argmin one of those is not wrong in any sense the solver can feel: the
truth still satisfies the constraint. Which of the two predicts is the question.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from geometry import Rect
from ortools.sat.python import cp_model

from solver import (
    LayoutProjector,
    SolveConfig,
    SolveResult,
    _reaches,
    rank_relations,
    select_relations,
    separation_options,
)

Relation = Tuple[str, int, int]          # (axis, a, b): a is left of / below b


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------


def sep_cost(boxes: Sequence[Rect], axis: str, a: int, b: int) -> int:
    """Cost of the separation `a <axis-before> b` against `boxes`.

    <= 0 means these boxes already satisfy it, > 0 is the overlap it would have
    to close. This is the same arithmetic `rank_relations` minimises over.
    """
    if axis == "x":
        return boxes[a].x2 - boxes[b].x1
    return boxes[a].y2 - boxes[b].y1


def argmin_directions(boxes: Sequence[Rect]) -> Dict[frozenset, Relation]:
    """Per pair, the truth's own `argmin` separation. The metric's ground truth."""
    return {frozenset((a, b)): (axis, a, b)
            for _cost, _margin, axis, a, b in rank_relations(boxes)}


def all_four(a: int, b: int) -> List[Relation]:
    i, j = (a, b) if a < b else (b, a)
    return [("x", i, j), ("x", j, i), ("y", i, j), ("y", j, i)]


# ---------------------------------------------------------------------------
# The metric itself — 5.2's three numbers, plus the cycle rate
# ---------------------------------------------------------------------------


@dataclass
class Arrangement:
    n: int
    tau: int
    pairs: int                      # n(n-1)/2, the denominator
    asserted: int                   # what the solver would actually post
    abstained: int                  # margin < tau
    cyclic: int                     # dropped by the acyclicity guard
    agree: int                      # asserted and == truth argmin
    argmin_wrong: int               # asserted and != truth argmin
    violated: int                   # asserted and FALSE of the truth geometry
    wrong_margins: List[int] = field(default_factory=list)

    @property
    def abstain_rate(self) -> float:
        return self.abstained / self.pairs if self.pairs else 0.0

    @property
    def agreement(self) -> float:
        return self.agree / self.pairs if self.pairs else 0.0

    @property
    def argmin_wrong_rate(self) -> float:
        return self.argmin_wrong / self.pairs if self.pairs else 0.0

    @property
    def violated_rate(self) -> float:
        """The strict reading of confident-wrong. The headline candidate."""
        return self.violated / self.pairs if self.pairs else 0.0

    def as_row(self) -> dict:
        return {
            "pairs": self.pairs, "asserted": self.asserted,
            "abstained": self.abstained, "cyclic": self.cyclic,
            "agree": self.agree, "argmin_wrong": self.argmin_wrong,
            "violated": self.violated,
            "abstain_rate": round(self.abstain_rate, 5),
            "agreement": round(self.agreement, 5),
            "argmin_wrong_rate": round(self.argmin_wrong_rate, 5),
            "violated_rate": round(self.violated_rate, 5),
        }


def measure(proposal_boxes: Sequence[Rect], truth_boxes: Sequence[Rect],
            tau: int) -> Arrangement:
    """Score a Proposal against a truth. 5.1 and 5.2, both readings."""
    n = len(proposal_boxes)
    ranked = rank_relations(proposal_boxes)
    chosen, abstained, cyclic = select_relations(ranked, tau, n)
    truth_dir = argmin_directions(truth_boxes)

    agree = argmin_wrong = violated = 0
    margins = {(axis, a, b): margin
               for _c, margin, axis, a, b in ranked}
    wrong_margins: List[int] = []
    for rel in chosen:
        axis, a, b = rel
        if truth_dir[frozenset((a, b))] == rel:
            agree += 1
        else:
            argmin_wrong += 1
        if sep_cost(truth_boxes, axis, a, b) > 0:
            violated += 1
            wrong_margins.append(margins.get(rel, 0))
    return Arrangement(
        n=n, tau=tau, pairs=n * (n - 1) // 2, asserted=len(chosen),
        abstained=len(abstained), cyclic=len(cyclic),
        agree=agree, argmin_wrong=argmin_wrong, violated=violated,
        wrong_margins=wrong_margins,
    )


# ---------------------------------------------------------------------------
# Injection — the controlled dose
# ---------------------------------------------------------------------------


def flip(rel: Relation, rng: random.Random) -> Relation:
    """Replace a relation with one of the three directions it is not.

    Uniform over the three, because 5.2's definition of confident-wrong does not
    distinguish "reversed on the same axis" from "asserted on the other axis".
    Whether it should is one of the things this ticket measures.
    """
    axis, a, b = rel
    return rng.choice([d for d in all_four(a, b) if d != rel])


def flip_reverse(rel: Relation) -> Relation:
    """The same-axis reversal only: a left of b becomes b left of a."""
    axis, a, b = rel
    return (axis, b, a)


def flip_axis(rel: Relation, rng: random.Random) -> Relation:
    """The other-axis flip only, direction chosen at random."""
    axis, a, b = rel
    other = "y" if axis == "x" else "x"
    return rng.choice([d for d in all_four(a, b) if d[0] == other])


def guard(relations: Sequence[Relation], n: int) -> Tuple[List[Relation], int]:
    """Re-run the solver's per-axis acyclicity guard over a relation list.

    Same greedy order in, so this is exactly what `select_relations` would have
    kept had the Proposal's geometry produced this list.
    """
    succ = {"x": {i: set() for i in range(n)},
            "y": {i: set() for i in range(n)}}
    kept: List[Relation] = []
    dropped = 0
    for axis, a, b in relations:
        g = succ[axis]
        if _reaches(g, b, a):
            dropped += 1
            continue
        g[a].add(b)
        kept.append((axis, a, b))
    return kept, dropped


def inject_wrong(base: Sequence[Relation], k: int, rng: random.Random, n: int,
                 mode: str = "any", guarded: bool = True
                 ) -> Tuple[List[Relation], int, List[Relation]]:
    """Flip `k` of `base` to a wrong direction.

    Returns `(posted, cycle_drops, flipped)`. With `guarded=False` the posted set
    can contain a directed cycle, which the shipping solver can never produce —
    that arm exists to price the guard, not to model anything real.
    """
    idx = set(rng.sample(range(len(base)), min(k, len(base))))
    out: List[Relation] = []
    flipped: List[Relation] = []
    for t, rel in enumerate(base):
        if t in idx:
            if mode == "reverse":
                new = flip_reverse(rel)
            elif mode == "axis":
                new = flip_axis(rel, rng)
            else:
                new = flip(rel, rng)
            flipped.append(new)
            out.append(new)
        else:
            out.append(rel)
    if not guarded:
        return out, 0, flipped
    kept, dropped = guard(out, n)
    return kept, dropped, flipped


def inject_abstain(base: Sequence[Relation], k: int, rng: random.Random
                   ) -> List[Relation]:
    """Drop `k` relations. An abstained pair is one the solver is left free on,
    so dropping *is* abstaining — there is no third thing it could do."""
    idx = set(rng.sample(range(len(base)), min(k, len(base))))
    return [rel for t, rel in enumerate(base) if t not in idx]


def make_cycle(base: Sequence[Relation], length: int, rng: random.Random,
               n: int) -> Optional[List[Relation]]:
    """Force a directed cycle of `length` rooms onto the x axis, unguarded.

    Every relation in the cycle is individually satisfiable; the set is not.
    This is what 5.2's cycle rate is about, and it is only reachable by
    bypassing the guard.
    """
    if n < length:
        return None
    ring = rng.sample(range(n), length)
    cyc = {("x", ring[t], ring[(t + 1) % length]) for t in range(length)}
    touched = {frozenset((a, b)) for _ax, a, b in cyc}
    rest = [r for r in base if frozenset((r[1], r[2])) not in touched]
    return rest + sorted(cyc)


# ---------------------------------------------------------------------------
# Solving with a relation set chosen by us rather than by the extractor
# ---------------------------------------------------------------------------


def project_with(brief, proposal, relations: Sequence[Relation],
                 cfg: SolveConfig) -> SolveResult:
    """Solve with `relations` posted hard, bypassing the extractor.

    `cfg.fix_relations` must be False — the point is that we choose the set. The
    Proposal still supplies the objective and the hint, so the *only* channel
    under test is the relation set.
    """
    assert not cfg.fix_relations, "project_with owns the relation set"
    lp = LayoutProjector(brief, proposal, cfg)
    for axis, a, b in relations:
        lp.post_relation(axis, a, b)
    return lp.solve()


def blame(brief, proposal, relations: Sequence[Relation],
          cfg: SolveConfig) -> Optional[dict]:
    """Which posted relations are *sufficient* for the infeasibility?

    Every relation goes in behind its own assumption literal, so CP-SAT can be
    asked directly which subset of them cannot be satisfied together with the
    Brief. This is the causal test the metric needs: if the core is made of the
    relations we flipped, confident-wrong is not merely correlated with failure,
    it is the cause of it.

    `solver._core` cannot answer this — it rebuilds from `cfg`, and under
    `fix_relations=False` the rebuilt model has no relations in it at all.

    Returns None if the model is not infeasible.
    """
    lp = LayoutProjector(brief, proposal, cfg)
    lits = []
    for idx, (axis, a, b) in enumerate(relations):
        v = lp.m.NewBoolVar(f"rel_{idx}")
        if axis == "x":
            lp.m.Add(lp.x2[a] <= lp.x1[b]).OnlyEnforceIf(v)
        else:
            lp.m.Add(lp.y2[a] <= lp.y1[b]).OnlyEnforceIf(v)
        lits.append(v)
    at_index = {v.Index(): i for i, v in enumerate(lits)}
    lp.m.ClearAssumptions()
    lp.m.AddAssumptions(lits)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = cfg.time_limit_s
    s.parameters.num_workers = cfg.workers
    st = s.Solve(lp.m)
    if st != cp_model.INFEASIBLE:
        return {"status": s.StatusName(st), "core": None}
    core = sorted({at_index[i] for i in s.SufficientAssumptionsForInfeasibility()
                   if i in at_index})
    return {"status": "INFEASIBLE", "core": core}


def blame_families(brief, proposal, relations: Sequence[Relation],
                   cfg: SolveConfig) -> dict:
    """With the relations held HARD, which Brief family is the one that breaks?

    `solver._core` cannot answer this either: it rebuilds from `cfg`, which under
    `fix_relations=False` drops the relations entirely and then reports that the
    relaxed model is fine. Here every softenable family goes behind an assumption
    literal while the relation set stays hard, so CP-SAT names the families whose
    satisfaction is incompatible with the arrangement being asserted.

    An empty core with an INFEASIBLE status means no combination of Brief
    families is to blame — the relation set cannot be packed into the Envelope at
    all, whatever the Brief asks for.
    """
    from copy import deepcopy
    from solver import SOFTABLE

    cfg2 = deepcopy(cfg)
    cfg2.soft = SOFTABLE
    cfg2.diagnose = False
    lp = LayoutProjector(brief, proposal, cfg2)
    for axis, a, b in relations:
        lp.post_relation(axis, a, b)
    groups = {
        "required_adj": lp.req_lits,
        "exterior": lp.ext_viol,
        "wet_cluster": lp.wet_viol,
        "circulation": lp.circ_viol,
        "coverage": [lp.cov_slack] if lp.cov_slack is not None else [],
    }
    assumptions, labels = [], {}
    for gname, vars_ in groups.items():
        if not vars_:
            continue
        a_ = lp.m.NewBoolVar(f"assume_{gname}")
        for v in vars_:
            lp.m.Add(v == 0).OnlyEnforceIf(a_)
        assumptions.append(a_)
        labels[a_.Index()] = gname
    lp.m.ClearAssumptions()
    lp.m.AddAssumptions(assumptions)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = cfg.time_limit_s
    s.parameters.num_workers = cfg.workers
    st = s.Solve(lp.m)
    return {
        "status": s.StatusName(st),
        "core": (sorted({labels[i] for i in
                         s.SufficientAssumptionsForInfeasibility()
                         if i in labels})
                 if st == cp_model.INFEASIBLE else None),
    }
