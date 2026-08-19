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

**Sharpened by *Building scope and envelope handling*, now closed. This adds an
axis, and it is not optional.**

Every timing on this map was measured with **100% exterior exposure**.
`Envelope.exterior_faces()` (`experiments/solver-toy/geometry.py:103`) returns all
four bbox faces plus all four faces of every notch, unfiltered, so H8 — *every
habitable room touches an exterior wall over a window's width*
(`experiments/solver-toy/solver.py:392`) — was posted against the largest face set
the geometry can offer. **The quoted 0.35 / 1.35 / 6.25 s therefore describes a
detached bungalow, and nothing else.**

The Envelope is now an ordered ring of edges, each `exterior` or `party`, and only
`exterior` edges may hold a window. So:

6. **Exposure.** Sweep the dwelling-type presets, not just room counts —
   `detached` (4 exterior), `terrace_mid` (2), `flat_corner` (2 adjacent),
   `flat_single_aspect` (1). The last quarters the face set with the same rooms
   competing for it, and flats are the v1 buyer's likelier case. Report separately;
   a single blended figure hides exactly the case that matters. The change is one
   filter on `exterior_faces()`.

Expect H8 to become the binding constraint at low exposure, where today it is
nearly free. If `flat_single_aspect` at 24 rooms does not solve, that is a product
finding, not a tuning problem — say so plainly.

## Third axis, from *Dimensioning and annotation rules*

The solved plans this sweep produces are the only ones that exist, so record three
drawing measurements off the same runs — no extra solving, and the whole sheet
ladder is currently unmeasured above **five** rooms.

1. **Unique witness count per side.** A tier-2 chain dimensions the partitions
   that *reach* that side. Nobody knows how many that is at 24 rooms, and it sets
   how crowded the chain gets.
2. **How often the narrow-tick rule fires**, and whether consecutive
   text-outside labels ever collide badly enough to need the above/below
   alternation. On the five-room worked example it fires four times.
3. **The sheet and scale chosen.** Scale is held at 1:50 and the sheet grows, so
   the honest question is how many rooms it takes to reach A1 — and whether
   `(A1, 1:100)`, the last entry in the ladder, is ever reached. If a 24-room plan
   falls off the end of the sheet ladder, that is the same class of finding as
   `flat_single_aspect` not solving: a product finding, not a tuning problem.

## The exposure axis now has measured numbers, from *Acquire the datasets*

Axis 6 above named four presets but had no evidence for what real flats look
like. Swiss Dwellings supplies it. Measured over 569 dwellings on 150 sampled
floors — `experiments/corpus-smoke/exposure_swiss_dwellings.py`, method and
caveats in `docs/research/dataset-inventory.md` §1.5 — the fraction of a
dwelling's Envelope perimeter that faces neither a neighbour nor a communal area:

| p5 | p25 | median | p75 | p95 | ≥0.99 |
|---:|---:|---:|---:|---:|---:|
| 0.16 | 0.23 | **0.37** | 0.47 | 0.59 | **0 of 569 (0.0%)** |

**Not one real dwelling in the sample sits near the 100% exposure every timing on
this map was measured at.** So sweep the presets as *fitted* values rather than
guesses: `flat_single_aspect` at a quarter is close to the measured **p25 of
0.23**, `terrace_mid` at a half is close to the **p75 of 0.47**, and the
**median case is 0.37** — which is the figure a spec should quote as typical,
not 1.0.

Two riders. The sample is 569 of 46,800 dwellings and the 0.45 m party threshold
is a judgement rather than a fitted value, so treat the quantiles as sound to two
decimals and no further. And nine sampled dwellings scored ~0.00 exterior —
genuinely windowless units that would fail H8 outright; worth a look before they
are dismissed as noise, because if they are real then H8 is rejecting homes that
exist.
