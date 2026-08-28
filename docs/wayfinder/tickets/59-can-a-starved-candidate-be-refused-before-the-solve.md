---
id: 59
title: Can a starved candidate be refused before the solve
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - docs/spec/proposer.md
  - docs/spec/acceptance-bar.md
---

# Can a starved candidate be refused before the solve

## Question

**Every starvation figure on this map is measured on the Proposal, and the rule
that produces it binds on the Plan.** `dim.statutory_min_area` is `site: both` —
the solver *posts* it and the validator *evaluates* it — but *What best-of-pool is
worth at production pool depth* measured 3,6 % and its whole best-of-*m* curve on
the **warped rectangles**, before any projection solve. **No warped Proposal on
this map has ever been put through the solver**: `fit_warp.py` imports
`experiments/solver-toy/` for its relation extractor and nothing else, and
`solver-toy`'s own Envelopes are real dwellings, never warped candidates.

The solver has freedom the warp does not — exact tiling is soft (C10), so it can
move floor between Rooms the warp sized — so Plan-level starvation could fall
either side of the Proposal-level number.

**This is also the whole of what deepening costs**, which is why the two questions
are one ticket. 57 measured the parts:

| | cost per extra pool member |
|---|---|
| warp | **0.79 s** (bucket) / **1.66 s** (gated fixed point) |
| projection solve, real boundary | p50 **10,11 s**, p90 at the 15 s cap |

79 extra members is ~60–130 s of warp and **13–20 minutes** of solve, and it falls
entirely on the starving Brief. So `acceptance-bar.md` §11.1 step 1 is affordable
if and only if a candidate can be refused on its **Proposal**, and unaffordable
otherwise — at any depth, not just at 87.

**What has to be decided:**

1. **Whether a Proposal-level check is sound.** A cheap screen that refuses
   candidates the solver would have rescued is throwing away yield to save time,
   and one that passes candidates the solver then fails has bought nothing. Which
   error is acceptable, and at what rate.
2. **Whether the screen is the same predicate.** `dim.statutory_min_area` is
   already `both`, so the solver posts it — the question is whether the *warp*
   should post it too, making it a third site, or whether a separate cheaper
   Proposal check is the right object.
3. **What §11.1 step 1 is then allowed to claim.** 57 showed it buys ~1 point,
   flat by m = 12, and cannot go below **π = 2,8 %** — so the step is a config
   value (a pool-depth constant), not a re-shape of the proposer service. That
   constant cannot be chosen without (1) and (2).

**Graduated from *What deepening a starved Brief's pool costs the runtime***,
whose own stated branch condition — *"if the curve is flat by m = 12, this is a
config value"* — 57 satisfied.

## Deliverable

Either a specified Proposal-level screen with its two error rates and the pool
depth constant it makes affordable, or a finding that the check must wait for the
solve, in which case §11.1 step 1's claim shrinks to whatever fits one 15 s budget
and steps 2 and 3 carry the rest.
