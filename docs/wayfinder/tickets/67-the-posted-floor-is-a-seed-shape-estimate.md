---
id: 67
title: The posted floor is a seed-shape estimate
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: []
writes:
  - experiments/warp/
  - docs/spec/proposer.md
---

# The posted floor is a seed-shape estimate

## Question

**ADR 0033 posts `dim.statutory_min_area` in grid cells, and the conversion from
a Space area to cells is read at the affine seed rather than at the shape the
warp solves to.** `part_targets_cells` adds back each Room's own erosion
overhead off `seed_rects`; the shape then moves under the warp, so the posted
constant is an estimate of the floor and not the floor.

The residual is small and it is not zero: **14 of 302** floor-posted candidates
(**4,6 %**) still land a Room under its floor on the bar plane. The depths are
grid dust — p50 **0,038 m²**, max **0,438** — against a baseline whose misses run
p50 1,356 and reach 8,444, and at m = 8 the residual vanishes at Brief level
(`clean_share_of_served` = 1.00). So this is second-order, and it is the whole
distance between *"the warp meets its floors"* and *"the warp usually meets its
floors"*.

⚠️ **`proposer.md` §2.2.2 decision 7 currently states the invariant without the
asterisk.** Either the residual is removed or that sentence is qualified; it may
not stand as written while 4,6 % of candidates falsify it.

**Three candidate fixes, and they are not equivalent:**

1. **Inflate the posted floor by the estimate error.** One constant, no extra
   solve. Costs INFEASIBLE in proportion to how much slack it buys, and the p90
   of the error is the number to fit it to. Cheapest, and it trades a false
   negative for a false positive rather than removing either.
2. **Re-post at the solved shape and re-solve.** Exact where it converges,
   doubles the warp on the candidates that need it. The warp is p50 0,674 s
   against a 15 s projection, so a second solve on a minority is affordable —
   but this is a fixed-point iteration and nothing on this map has shown it
   converges.
3. **Post the erosion exactly rather than as an overhead.** For a one-part Room
   with fixed boundary flags the eroded area is `(250w − t·a)(250h − t·b)` with
   `a, b` constant, which is one `AddMultiplicationEquality` on shifted
   variables — the same class ADR 0028's void already pays. Two-part Rooms need
   the shared-edge strip added back, which is linear in the join span. Exact, and
   the only option that makes the constraint *true* rather than *nearly true*.

**What has to be measured:** the estimate error's distribution (signed, not
absolute — a floor over-estimated costs INFEASIBLE and one under-estimated costs
the invariant), then whichever of the three the distribution argues for.

⚠️ **Do not re-price the floor decision here.** ADR 0033 is decided on evidence
that already includes this residual; this ticket removes a defect in the
constraint's *encoding*, and a finding that the residual is larger than reported
is a correction to ADR 0033's numbers, not a reopening of its decision.

## Raised by

*Should the warp post the statutory floor* (2026-08-29), ADR 0033 consequence 3.

## Handed on by *The projection discards a fifth of the guarantees the warp now buys* (2026-08-30)

**You now own grid dust at two sites, not one, and they should be decided
together because the three fixes above map onto both.**

ADR 0039 makes `solver.py` read the bar plane by subtracting the erosion band
**per side** rather than on all four. That form double-subtracts the 75 × 75 mm
square wherever two *interior* sides meet, so it understates a Room by
`5 625 mm²` per interior-interior corner — at most **0,0225 m²**. Hand-verified:
a 4 × 3-cell Room with all four sides interior computes 487 500 mm² against a true
510 000 (four corners); with its left side on the boundary, 543 750 against
555 000 (two).

**It is the same size and the same class as your 4,6 % residual.** Yours is p50
**0,038 m²**, max 0,438, and it is an *estimate* error — the erosion overhead read
at the affine seed, on a shape that then moves. This one is an *exactness* error —
a correct band subtraction with a known missing corner term. Both are dust; both
are the distance between a constraint being true and being nearly true.

**Three things this changes for your ticket:**

1. **Your option 3 — "post the erosion exactly rather than as an overhead" — now
   has a second consumer.** ADR 0039's decision 2 is the projection-side twin of
   it, and it stopped one term short for exactly the reason your option 3 names as
   its own cost: exactness needs contact at a **point** rather than over a length.
   If you take option 3, price the corner term for both sites at once.

2. ⚠️ **The two residuals do not compose in one direction.** Dropping a corner is
   conservative on every **floor** and *lenient* on `dim.max_area`, which ADR 0039
   found is the one rule of seven where the solver's plane is already the lenient
   one. So a corner term that is decorative for your floor question may not be for
   the cap. It is not yours to decide, but it is why the bound is recorded rather
   than waved.

3. **Nothing under you moved.** ADR 0039 wrote no code and touched neither
   `experiments/warp/` nor `docs/spec/proposer.md`, so §2.2.2 decision 7's
   unasterisked invariant is still exactly the sentence your ticket is about, and
   `experiments/warp/` still stands at three claimants — 62, 65 and you.
