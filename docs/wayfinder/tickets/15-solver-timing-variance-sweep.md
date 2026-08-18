---
id: 15
title: Solver timing variance sweep
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: [1]
---

# Solver timing variance sweep

## Question

Nothing to decide — but the destination is a **specification**, and the solver
numbers are not yet quotable in one.

*Solver formulation for layout projection* measured 0.35 s / 1.35 s / 6.25 s at
8 / 12 / 24 rooms and closed with the caveat in plain words: **single seed, no
variance estimate.** A spec that states "24 rooms in 6.25 s" on one sample of one
seed on one four-core machine is a spec making a promise it has not tested. Every
run terminated FEASIBLE rather than OPTIMAL, which means the time limit is a
product parameter — and a product parameter needs a distribution, not a point.

Run the existing harness in `experiments/solver-toy/` across:

1. **Many seeds** — enough for a median and a tail, not a mean. The tail is what
   a user experiences.
2. **Proposal quality** — the measured run started from a Proposal carrying 21.6%
   unassigned floor and 8.3% overlap. Sweep degradation from near-perfect to
   badly degenerate, and find where solve time turns over.
3. **Room counts** across the range, not only 8/12/24, so the growth curve is
   visible rather than three points.
4. **The two failure modes already identified** — degenerate Proposals (valid at
   8 and 12, nothing at 24) and shuffled Proposals (genuinely INFEASIBLE in
   <0.1 s). Establish how often each occurs and how reliably detection fires.
5. **Hardware** — the measurement machine was a 4-core Ivy Bridge. Report at least
   one modern-CPU figure so the spec is not quoting a floor as a typical.

Then set, with evidence: **the shipped time limit**, and what the system does when
it expires.

**Sharpened by *Canonical geometry model*, now closed.** Walls with thickness do
**not** change the formulation's structure — the dilated solve domain keeps the
same variables, the same `AddNoOverlap2D` and the same soft-coverage amendment.
Only constants move, with **one exception that this sweep must measure**:

- **Area constraints are now posted on eroded dimensions, in millimetres** —
  `AddMultiplicationEquality(area_mm2, [w·grid − t_int, h·grid − t_int])`. Operands
  move from ~10² to ~10⁴ and products to ~10⁸, against **H4, already flagged as the
  formulation's weak spot**. Whether the measured times survive this is the single
  most important thing the sweep now answers, and it should be measured *against*
  the original grid-unit form so the cost is attributable.
- **The contact threshold rose** to `structural opening width + t_int` — not leaf
  width. Adjacency machinery is sensitive to this constant, so use the real one.
- **The grid stays at 250 mm.** Ticket 01 retired the worry that real wall
  thicknesses might force 100 mm: wall faces sit off-grid at `± t_int/2`, which is
  fine because the model is millimetres and the grid only constrains the solve. The
  resolution sweep is therefore optional curiosity here, not a prerequisite.

Deliverable: the timing distributions appended to
`docs/research/solver-formulation.md`, and a recommended time-limit value with the
percentile it corresponds to.
