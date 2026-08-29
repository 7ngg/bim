---
id: 68
title: The projection discards a fifth of the guarantees the warp now buys
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - docs/spec/acceptance-bar.md
  - docs/spec/solver-formulation.md
---

# The projection discards a fifth of the guarantees the warp now buys

## Question

**`solver.py` reads a Room on a different plane from the bar it enforces, and
ADR 0033 has just changed what that costs.** The two quantities now have a name —
`CONTEXT.md`'s **Space plane**: the **bar plane** does not erode an edge sitting
on the Envelope, because ADR 0001's tiling edge there already sits at
exterior-inner-face + `t_int/2`; the **solver plane** erodes all four sides of
every Room, because 75 mm is below the 250 mm grid's own quantisation. The
projection is therefore **strictly stricter than the rule it posts**, by a median
**3,9 %** of a Room's area.

`acceptance-bar.md` §11.1 recorded this and deferred it, and the deferral's
reasoning is sound as far as it goes: *"it costs yield and never admits a Plan
that should have been refused"*. **What changed is the cost basis, not the
argument.** That deferral was priced when no stage was paying to clear the floor.
ADR 0033 makes the warp pay — 8,66 % of candidates, to guarantee every Room
clears its statutory floor on the bar plane — and then **59 of 302** floor-clean
candidates, **19,5 %**, fail that same floor on the solver's plane.

⚠️ **19,5 % and §11.1's 1,51 % are two denominators, not a contradiction.**
1,51 % is per-Room over all 1 786 warped Rooms; 19,5 % is per-candidate over the
floor-bound population. Anyone quoting one at the other is comparing different
quantities, and this ticket must not manufacture a conflict out of that.

**This is not a re-opening of the deferral.** It is the question the deferral
could not have answered: *what is a false refusal worth once a stage upstream is
spending yield to prevent it?*

## What has to be decided

1. **Whether the floor `solver.py` posts can carry a boundary correction.**
   §11.1 says the plane *"cannot be fixed inside the model"*, and that is a claim
   about representing 75 mm on a 250 mm grid — it is **not** obviously a claim
   about the floor *constant*. `amm >= min_area · 250² − correction(Room)`, where
   the correction is computed from which of the Room's sides sit on the domain
   boundary, moves arithmetic rather than geometry. Check whether that is
   available before accepting that nothing is.
2. **Whether the bar should instead be restated on the solver's plane.** The
   opposite fix, and it is the one to argue against explicitly: it would make the
   engine agree with itself by moving a *legal* quantity onto a plane chosen by a
   quantisation accident. ⚠️ ADR 0033 refused exactly this move for the warp and
   the reasoning transfers.
3. **Whether it is worth fixing at all in v1.** The honest case for leaving it:
   it never admits a Plan that should have been refused, so it costs only yield,
   and yield is what pool depth is for. The case against is now stronger by one
   fact — the yield it costs is yield another stage has already bought.
4. **What C2's Homeowner is told**, if anything. Nothing here reaches the surface
   today; a refusal on this path lands in §11.1 step 3's no-defect sentence,
   which already covers it. Confirm rather than assume.

## What this is not

Not a change to `dim.statutory_min_area` — severity, value, site and limb set are
settled three times over (ADR 0027, ADR 0033, `acceptance-bar.md` §3.2). Not a
re-opening of ADR 0033. Not the warp-side encoding residual, which is
*The posted floor is a seed-shape estimate*.

## Raised by

*Should the warp post the statutory floor* (2026-08-29), ADR 0033 consequence 4.
