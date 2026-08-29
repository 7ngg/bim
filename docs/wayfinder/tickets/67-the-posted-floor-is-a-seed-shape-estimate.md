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
