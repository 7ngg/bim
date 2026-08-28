---
id: 63
title: The gate measures stretch with two blunt scalars
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - experiments/warp/
  - docs/spec/proposer.md
---

# The gate measures stretch with two blunt scalars

## Question

**The gate's two dimensional terms buy real fidelity through a mechanism they do
not name, and the quantity they are a proxy for is measurable directly.**

*The rig gate is not the shipped gate* established that total area ±10 % and
envelope aspect ±15 % are worth **8.6 points of decline** — 27.6 % against
36.2 %, paired within one Brief, sign test p = 0.0001 — and a worst-room area
deviation 68 % smaller at p50. It also established **why**, and the why is the
opening. ADR 0020 sizes the box from the *Brief*, so a donor's own area and
aspect never enter the warp's arithmetic at all; what they bound is how hard the
donor's **cut-line frame** has to stretch to reach the Brief's box, and the
stretch is what the ergonomic floor and `dim.aspect_ratio_hard` refuse.

**So the terms are a proxy, and a coarse one.** Three signs, all measured:

1. **The effect is a dose, not a threshold.** Decline runs 28.3 → 30.1 → 40.2 →
   **55.2 %** as the donor moves from inside the aspect tolerance to more than
   four times outside it. A gate is a step function fitted to a ramp, and the
   step is at 1.0 for no reason anyone has measured.
2. **57.9 % of refusals fail one term only.** The conjunction throws away a
   donor that is close on the axis that matters because it is far on the axis
   that may not.
3. **Neither term is the stretch.** Area and aspect together fix a *box*; the
   stretch is a per-axis ratio between the donor's frame extent and that box, and
   two donors with identical area and aspect can carry frames that stretch very
   differently — that is the same distinction *A dwelling with two angles* drew
   between `worst_room_iou` and `frame_residual`.

**And pool depth is the scarce resource, which is what makes this worth asking.**
Under the gate the sample's median pool is **9** at 4–6 rooms and **5** at 7–10,
**14.5 %** of Briefs are blank, and the production index is only ~10× deeper.
*What best-of-pool is worth at production pool depth* showed depth buys about one
point and nothing at all at 7–10 rooms — so more depth is not the lever. **A
better-targeted gate is**: the same fidelity from a pool that refuses fewer
donors, or better fidelity at the same depth. Both land on the band ADR 0013
already calls tight.

**What has to be decided:**

1. **What the stretch quantity is**, stated precisely enough to compute off an
   index record. Candidates: the per-axis ratio of the donor's frame extent to
   the Brief's box extent; the max of the two; the log-ratio; the same measured
   after ADR 0020 fixes `s`. Only some are computable without a warp, and a gate
   term that needs a warp is not a gate term.
2. **Whether it dominates the scalar pair.** The test is a frontier, not a point:
   for each candidate term, the coverage it admits against the decline rate and
   worst-room deviation it delivers, plotted against the ±10 %/±15 % pair's own
   point. `gate_effect.py` already emits per-candidate `d_area`, `d_aspect`,
   decline and `worst_room_dev` per Brief, so the first pass costs no new warps.
3. **Whether it replaces the two terms or joins them.** A third term is more
   refusals, which is the wrong direction. Replacing is the interesting case and
   the one that has to beat the incumbent on both axes to be taken.
4. **What the market does, per the standing instruction.** Graph2Plan conditions
   retrieval on the **boundary itself** rather than on scalar proportions, and
   nothing in the reviewed generator literature gates on an area tolerance. That
   is a strong prior that the scalar pair is a stand-in for a shape distance, and
   a weak one about which shape distance.

## What this is not

Not a re-opening of whether the gate exists — ADR 0018 settled that admissibility
is a hard gate and not a ranking term, on an argument this ticket strengthens
rather than touches. Not the **coverage** question: how many Briefs retrieval
cannot serve at all is §2.2.7's and it is measured. Not `worst_room_iou` or
`frame_residual`, which are donor-**fidelity** fields ranked and gated by
§2.2.4's own reasoning; this is about the *Brief-to-donor* match, which is a
different pair of objects.

## Raised by

*The rig gate is not the shipped gate* (2026-08-28), which had to measure whether
the terms were inert before it could say what the rig's shortcut cost — and found
them decidedly not inert, with a mechanism nobody had written down.
