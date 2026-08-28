---
id: 62
title: What a sheared donor costs a warped candidate
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: []
writes:
  - experiments/warp/
  - docs/adr/0031-a-two-angle-dwelling-is-kept-and-labelled.md
---

# What a sheared donor costs a warped candidate

## Question

**ADR 0031 keeps the off-frame population and demotes it with the rank, on
evidence measured entirely on the donor** — `frame_residual`, cell agreement,
worst-room IoU. Whether a sheared donor actually yields a worse **Plan** after the
warp and the projection is unmeasured. 46 could not reach into `experiments/warp/`
because *What best-of-pool is worth at production pool depth* held it, and fogged
this rather than ticketing it, with its size left for 57 to determine.

**57 has determined it, and the answer is that this is sharp inside a narrow
window rather than moot.** The fog entry's own reasoning was that a 4–8° donor
sits at the **10,6th percentile** of a 58–87 bucket drawing `m = 8`, so at shipped
depth nothing draws these donors. That is right, and it is right by a margin of
about one position: the tenth percentile of a ranked pool of ~87 is rank **≈ 9**,
and `m = 8` stops at 8.

57's curve then says the useful depth is **m ≈ 12–16** — that is where starvation
flattens, and 90 % of what depth can buy is bought by 12. **Every one of those
extra draws is below the point where off-frame donors enter**, so the exact window
57 recommends spending is the window that starts drawing sheared donors. The
question is not moot; it is live precisely where the pool is worth deepening.

**What has to be measured:**

1. **Whether an off-frame donor yields a worse Plan**, not a worse record. Paired
   against an on-frame donor at matched `worst_room_iou` — `rectangularisation.md`
   §15.2 shows the two facts are not the same, so the pairing has to hold IoU
   fixed or it measures IoU again.
2. **Whether it changes starvation.** 57's curve is a survival rate; if sheared
   donors decline at a higher rate, deepening past rank 9 buys less than the curve
   says, and the m ≈ 12–16 recommendation moves.
3. **Whether the rank weight is right.** ⚠️ ADR 0031 records that the rank is where
   this lands, **not the gate** — a contradiction here re-weights an order, it does
   not reopen a hard cut.

**Blocked by *Can a starved candidate be refused before the solve*.** Two reasons,
and both are real. That ticket sets the pool-depth constant, which decides whether
rank 9 is ever reached — if it stays at 8 this ticket closes unmeasured. And
"yields a worse **Plan**" needs the warp-to-projection join, which no experiment on
this map has ever made and which 59 owns.

## Graduated from

*What a sheared donor costs a warped candidate, as opposed to a record* — the fog
patch 46 left, on the branch condition it stated. `experiments/warp/` is now
unclaimed and the four probes 57 left there (`pool_depth.py`, `best_of_m.py`,
`best_of_m_fit.py`, `constrained_warp.py`) are the harness this would extend;
`frame_residual` is published on every record per ADR 0031, so the split costs no
re-fit.

## Unblocked by *Can a starved candidate be refused before the solve*

**The constant you were waiting on exists, and it lands inside the window that
starts drawing off-frame donors.** §11.1 step 1 is now
`POOL_DEPTH_ON_STARVATION = 16`, past 57's knee — and a 4–8° donor sits at the
**10,6th percentile**, rank ≈ 9 of a 58–87 bucket. `m = 8` stopped one short; 16
does not. So the branch condition this ticket was raised on is **satisfied**: the
pool is deepened past the rank where sheared donors enter, on the Briefs that
reach the step.

⚠️ **It only fires on the starved path.** 16 is the depth on *starvation*, not the
standing pool, so the population that draws a sheared donor is the ~3 % of Briefs
that get there — which bounds what this ticket can be worth and should be said in
its own answer rather than discovered at the end of it.

Three things 59 leaves you that change how to run this:

1. **`experiments/warp/` is shared with 63 and not with 59** — `project_join.py`
   is finished and imports `solver-toy/` and `room-rectangles/` read-only. If you
   want a **Plan-level** cost for a sheared donor rather than a warp-level one,
   `project_join.one()` is the whole join in one call.
2. ⚠️ **A per-candidate warp figure is no longer the end of the story.** 82,0 % of
   candidates that look starved on the warped rectangles are served once the
   projection sizes them. Whatever a sheared donor costs the *warp*, price it at
   the Plan before concluding it costs the product anything.
3. ⚠️ **The conversion is still frozen until `fit_rects.py`'s five-field pass
   runs**, and `frame_residual` — the quantity this ticket turns on — is one of
   the five. Nothing in 59 moved that.
