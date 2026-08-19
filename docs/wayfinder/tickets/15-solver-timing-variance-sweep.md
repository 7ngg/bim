---
id: 15
title: Solver timing variance sweep
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
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

## New axis from *What the model proposes, and how it is trained*: fit τ

`docs/spec/proposer.md` §5 defines the arrangement metric on a **confidence
margin τ** — the gap between the best and second-best separation for a room pair.
τ is not the metric's parameter; it is **the solver's**, and it is the same number
the solver already uses to decide which relations to fix hard.

That makes it a timing axis, which is why it lands here rather than on the
Proposer:

- **High τ** — few relations asserted, most pairs left free. The search is less
  constrained, so it is **slower** and finds more valid arrangements.
- **Low τ** — many relations asserted as hard constraints. **Faster**, and a
  wrong one makes the model INFEASIBLE in under 0.1 s.

So τ trades wall-clock against candidate loss, and neither end is obviously right.
The current toy uses whatever value was convenient; nothing has fitted it.

**Sweep it against the axes already on this ticket**, because the interaction is
the point — a τ that is right at 100 % exposure and 24 rooms is not obviously
right at the measured median 0.37 and 6.8 rooms, and 4–10 rooms is the band
`docs/spec/proposer.md` §3 fixed for v1.

Report the curve, not a single value: solve wall-clock, INFEASIBLE rate, and
VALID-plans-per-Proposal against τ. *Validate the arrangement metric against the
solver* hands this ticket whatever it learns about the trade at a fixed τ; this
ticket owns choosing it.

---

## Resolution

**The shipped time limit is 15 s and τ is 4.** Both are fitted, not chosen.
965 solves, serial at `workers=4`, 30 s budget, on the same 4-core Ivy Bridge
every published number came from. Findings appended to
`docs/research/solver-formulation.md` as **Part II**; ADR
[0007](../adr/0007-published-minima-must-erode-onto-the-solve-grid.md); harness in
`experiments/solver-toy/{sweep,report,frontage,drawing_metrics,erosion_cost,grid_aligned_minima}.py`,
raw rows in `experiments/solver-toy/results/*.jsonl`.

### The deliverables the ticket asked for

**Time limit — 15 s, the p95 of time-to-VALID.** Pooled over the whole grid
(8 room counts × 5 exposures × 8 seeds, 159 solves that produced a Plan):
time-to-first p50 0.39 s / p90 2.83 s; **time-to-VALID p50 1.56 s / p90 10.79 s /
p95 13.65 s / max 25.06 s**. Every row carries its improving-solution trace, so
any budget below 30 s is answered exactly rather than extrapolated: 15 s gives a
valid Plan on 86.8 % of solves and catches **96.5 % of every run that ever
reaches one**; 30 s buys 3.1 points more, 7.5 s costs 15.4. The column plateaus at
89.9 % because 33 of 192 solves are INFEASIBLE and never become valid at any
budget.

**On expiry** the dangerous case is not "no Plan" — it is a Plan paying coverage
slack. One unit of slack costs `soft_weight` = 100 000 against a corner objective
of O(10²–10³), so **objective ≥ soft_weight means no survivor: discard the
candidate, never show it.** Arithmetic, not a re-validation pass, and consistent
with what *Acceptance validator spec* settled for the zero-survivor case.

**τ = 4.** τ is not the timing knob the ticket described. It is the **valve on the
only channel by which the Proposal reaches the constraint system**, so it governs
feasibility first. At 8 rooms τ=4 costs 0.02 s and removes the σ=1.0 m
infeasibility cliff completely (2/4 → 0/4); at 24 rooms the same insurance costs
+13.6 s on time-to-VALID, past the limit. **The exchange rate is room-count
dependent** — free in the 4–10-room band C13 promises, and a joint parameter with
the time limit above ~16 rooms.

### Four findings that change other parts of the map

**1. The Proposal *can* make the model infeasible, on ordinary noise — the
formulation doc's boxed "single most important design rule" is false as
written.** `fix_relations=True` posts the Proposal's relations as hard
constraints. Part I knew this for the adversarial *shuffled* Proposal and filed it
as a caveat. Measured with plain Gaussian corner noise, τ=0:

| σ | n=8 | n=12 | n=24 |
|---|---|---|---|
| 0.25 m | 0/5 | 0/5 | 0/5 |
| **0.50 m — every published run** | 0/5 | **3/5** | 1/5 |
| 1.00 m | 3/5 | 4/5 | **5/5** |

INFEASIBLE counts. Nothing fails below σ = 0.25 m, so **v1 does not sit below the
cliff — it sits on the edge of it.** And solve *time* barely
moves across the range, so the ticket's "find where solve time turns over" has an
answer it did not anticipate: it never turns over — **Proposal quality does not
cost seconds, it costs feasibility outright.** Corrected in place in Part I and in
the toy's README. The two-phase fallback C10 mandates is now load-bearing for
ordinary operation, not just for hostile input.

**2. ADR 0001's clear reading deletes 4-, 5- and 6-room dwellings unless the
minima are grid-aligned.** The feared part was harmless: three encodings of the
eroded-millimetre area — grid units, a second `AddMultiplicationEquality` at 10⁸,
and an affine expansion — are **indistinguishable in time** (24 rooms: 3.00 /
2.87 / 2.71 s median), so **H4 survives**. The affine identity
`(gw−t)(gh−t) = g²wh − gt(w+h) + t²` means ADR 0001 needs no second
multiplication at all. What bit instead is arithmetic: `250w − t ≥ min_w` forces
`w ≥ min_w + 1` whenever `min_w` is a multiple of the grid, costing 250 mm per
room per axis to pay for a 100 mm wall. Exact tiling then becomes **provably**
impossible at 4–6 rooms, and **more area does not fix it** (swept to +40 %,
non-monotone, 4 rooms never recovers). Grid-aligned minima restore the
pre-ADR-0001 baseline exactly. **ADR 0007**, and it constrains *Ergonomic minima*
and *The Azerbaijani region profile*, which own the numbers.

**3. Exposure is not a timing axis — the ticket's central expectation is
refuted.** H8 was expected to become binding at low exposure. Every preset's
median time-to-first sits inside every other preset's seed spread at every room
count (24 rooms: detached 2.72, terrace_mid 2.09, flat_corner 2.94,
corpus_median 2.94 s). A smaller face set makes H8 a *smaller* disjunction, not a
tighter search. Two of ADR 0003's four presets also sit **above the corpus p95**,
so a fifth, `corpus_median`, was fitted to the measured 0.37.

What exposure does instead is fail earlier: **`flat_single_aspect` is
arithmetically dead from 7 rooms**, with no solver involved. Habitable rooms
occupy disjoint stretches of exterior wall, so `Σ min(min_w, min_h) ≤ exterior
run` is necessary; at 7 rooms it is 10 500 mm needed against 9 500 available, and
at 24 rooms it fails by 10 250 mm. Single-aspect flats are the corpus **p25**.
Ticketed as *H8 and the single-aspect flat*.

**4. More cores do not make the first Plan arrive sooner — they make the Plan
that arrives correct.** Time-to-first is flat across 1/2/4 workers (24 rooms:
2.395 / 2.386 / 2.384 s). One worker at 24 rooms returns objective 17 000 136 —
170 units of slack — and **0 % validity**; two workers reach 124 and **100 %**.
**Two workers is a floor, not a preference.** This is offered in place of item 5's
modern-CPU figure, which **could not be measured**: `platform.processor()` reports
`Intel64 Family 6 Model 58`, Ivy Bridge — this *is* the original machine. That
axis is unresolved and nothing was extrapolated for it.

### Drawing measurements, and three spec corrections

`drawing_metrics.py` reproduces `annotation.md` §14's worked example exactly —
four chains tick-for-tick, A3 1:50, extent 226 × 186 — which is what licenses
these numbers above five rooms.

- **Witnesses per side top out at 10** (11 segments) anywhere up to 24 rooms. The
  chain does not get crowded; at 24 rooms the median *falls* to 8, because most
  partitions no longer reach a side.
- **Tier 2b is not a fallback — it is half the drawing.** 2 walls of 7 at n=8,
  **10 of 21 at n=24**. So tier 1 sits at the 34 mm rung by default, not 26.
  `annotation.md` §4.3 corrected.
- **The narrow-tick rule fires 6–13 times per plan and never collides** — zero
  consecutive-outside-text collisions in 159 plans. §5a's above/below alternation
  is unreachable at v1 sizes; marked do-not-build.
- **The sheet ladder's top two rungs are unreachable.** A3 to 10 rooms, A2 from
  12, **A1 never**. `(A1, 1:100)` exists for a dwelling this engine cannot
  generate. §9 corrected.
- **Every chain closed, 159 of 159**, all four sides, sums exact.
- **§14 undercounts its own narrow-tick rule**: it says four, its four chains
  contain five. Corrected.

### Two riders closed

**The nine windowless Swiss dwellings are corpus noise, and H8 stands.** The
"nine" is the histogram's 0.00 bucket (everything below 0.125); at a literal
< 0.02 there are **three**. All three carry zero WINDOW openings against a control
where 88.4 % of 569 dwellings have ≥1 — so the party-gap heuristic is not
mis-classifying them — but their areas are **14.1, 14.2 and 10.3 m²** holding 6, 6
and 4 annotated rooms. A LIVING_ROOM, KITCHEN, BEDROOM, BATHROOM and two CORRIDORs
in 14 m² is an annotation fragment, not a home. **H8 is not rejecting homes that
exist**; the single-aspect finding above is the real problem and is separate.

**The infeasibility core does not work.** Every INFEASIBLE run in the sweep, at
every size and from every cause, returned the identical full set
`('circulation', 'coverage', 'exterior', 'required_adj', 'wet_cluster')`.
`SolveConfig.diagnose` discriminates nothing and should be fixed to return a
minimal core or dropped — as it stands it is a feature that looks like diagnosis.

### A harness defect that invalidated a first pass

The ground-truth generator enforced the published reading while the solver
enforced ADR 0001's clear one, so **the ground truth stopped being a witness** and
the harness's central guarantee — *a failure to solve is a fact about the
projection problem, not about an accidentally impossible Brief* — silently stopped
holding. At n=4 the truth's kitchen was 7 grid units wide where the clear reading
needs 8. `scenarios.fits_kind(rect, kind, clear_t)` now takes the reading as a
parameter. Every table published here is post-fix; the pre-fix pass was discarded,
as was an earlier one in which a watcher script started a second solver
concurrently and corrupted the timings. Rows now carry start timestamps so
contention is detectable rather than invisible.

### What this ticket did not settle

- **No modern-CPU figure** (item 5). Unresolved, not estimated.
- **Grid resolution still never swept.** ADR 0007's arithmetic is stated in terms
  of the grid, so changing it restates the standards table.
- **Distinct valid Plans per Proposal against τ is unmeasured.** 4 runs per cell
  cannot separate a trend from portfolio noise, so no claim is published; the
  hypothesis is untested rather than refuted.
- **Per-cell percentiles are nearest-rank on 8 seeds**, so a cell's p90/p95
  coincide with its maximum. Only the pooled figures carry real tails.
