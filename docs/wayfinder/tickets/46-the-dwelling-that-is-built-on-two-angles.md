---
id: 46
title: The dwelling that is built on two angles
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - experiments/rectangularise/
  - docs/research/rectangularisation.md
---

# The dwelling that is built on two angles

## Question

**The conversion silently emits a different flat, and scores it as a middling
one.** *Look at the converted corpus* found it by rendering, and it is the whole
p5 tail — ADR
[0017](../../adr/0017-three-of-the-conversions-fidelity-headlines-are-constraints-restated.md),
failure mode 1.

`measure_swiss.dwelling_frame` rotates a dwelling onto **one** angle, taken from
the minimum rotated rectangle of the whole room union. A dwelling built on two —
a bedroom wing splayed off a living spine, which real housing does — has every
room in the second wing sheared into the first wing's frame. The output is a
plausible home. It is not the home that was converted.

| room off frame by | dwellings | cell agreement | worst-room IoU |
|---|---:|---:|---:|
| 0–2° | 90.2 % | 0.941 | 0.768 |
| 2–5° | 3.5 % | 0.844 | 0.699 |
| 5–10° | 3.5 % | 0.876 | 0.745 |
| **10–20°** | **1.5 %** | **0.705** | **0.167** |
| 20°+ | 1.2 % | 0.676 | 0.429 |

Measured over 400 dwellings by `experiments/rectangularise/void_census.py`.
Rendered examples: `render_sheet.py --pick=worstroom`, sheets at
`out/sheets/SHEET.html`.

**What has to be decided: what the conversion does with a dwelling whose rooms
are not all on one angle.** Three candidates, and none is obviously right:

1. **Refuse it.** Add an off-frame gate to the reject rule — cheapest, and it
   thins the corpus by roughly 3 % on top of the 9.5 % already refused. But it
   removes exactly the splayed-wing plans, and the splayed wing is an
   arrangement a Homeowner will ask for.
2. **Re-frame per wing.** Segment the dwelling into angle-coherent components,
   fit each in its own frame, then reconcile. Expensive, and the reconciliation
   is a new problem: two frames meeting at an angle is not something the
   Envelope (ADR 0003, a rectilinear ring) can express, so a re-framed dwelling
   may be unrepresentable anyway.
3. **Accept and label.** Keep the sheared output and carry a per-dwelling
   `frame_residual`, so retrieval (ticket 23) can down-weight or exclude them
   without the corpus losing them. The Proposer then learns from a sample it
   knows is distorted rather than one it believes is faithful.

**What this ticket must settle beyond the choice:** whether `frame_residual` is
published on every converted record regardless — it costs nothing and it is the
only reason anyone would ever notice this again.

**Do not re-litigate** ADR 0008's conversion, the reject rule's existence, or
rectangles over polygons. This ticket decides what happens to one population.

**One thing the reading already establishes.** Nothing published faces this
problem: every generator in `docs/research/floorplan-generation-stack.md` fits
axis-aligned rectangles, and every corpus the field trains on — RPLAN, LIFULL —
is already orthogonal, so the second angle never arrives. Swiss Dwellings is
surveyed geometry. **There is no prior art to shop for**, which is a finding and
not a gap in the reading.
