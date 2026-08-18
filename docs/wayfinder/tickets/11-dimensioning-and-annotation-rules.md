---
id: 11
title: Dimensioning and annotation rules
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: [1, 3]
---

# Dimensioning and annotation rules

## Question

What exactly gets dimensioned and annotated, and by what rule?

This is the differentiator. C3 makes dimension strings and room tags a hard floor,
and the competitive scan found **no surveyed product documents a dimensioning,
annotation, title-block or schedule system** — eleven vendors across four price
tiers. Every one of them hands the user to Revit or AutoCAD at exactly this point.
So there is no prior art to copy and the rules must be derived.

Decide:

1. **Which chains are generated.** Overall external chains on which sides? A
   per-room chain? An intermediate chain picking up wall faces and openings? The
   architectural convention is usually three tiers — confirm it and adopt it, or
   justify departing.
2. **Where dimension lines sit.** Offset from the building face, spacing between
   tiers, and what happens when they collide with each other or with the plan.
   Collision avoidance is the part that makes this hard, and it is why nobody
   ships it.
3. **What is measured to** — wall centrelines, wall faces, or structural grid?
   These give different numbers and architects have opinions. This choice couples
   directly to the wall representation chosen in *Canonical geometry model*.
4. **Room tags.** Name, area, both? Placement rule — centroid, or largest
   inscribed circle so the tag never lands outside a concave room? Behaviour when
   a room is too small for its own label.
5. **Openings.** Are doors and windows dimensioned and tagged, or scheduled, or
   both? A door schedule is a table, which is a different output entirely.
6. **Drawing furniture.** Scale, north point, title block, sheet size, layer names
   and lineweights. Which conventions — and does the layer naming follow a
   published standard so a Practitioner recognises it?
7. **Rounding and units.** Millimetres or metres, and what rounding. Dimension
   strings that do not sum to the overall are the classic embarrassment; whatever
   rule is chosen must guarantee they add up.

Both blockers are now closed. What they hand over:

- **Rule 3's input.** The model stores wall **centrelines**; the human-facing
  quantity is the **clear** dimension, between finished faces. The two are never
  interchangeable and every number that crosses a boundary says which it is. A
  chain measured to centrelines and labelled as clear is the failure mode here.
- **Annotation is derived, not stored** (ADR 0002). A `Drawing` is a Plan plus a
  sheet plus resolved annotation; only human corrections persist, as
  `AnnotationOverride`s keyed by **relation** — the wall segment between two named
  rooms — because derived geometry has no stable id across a regenerate. Rule 2's
  collision avoidance is therefore a *function* to be specified, with its output
  overridable, not a set of stored positions.
- **`ezdxf` authors genuine `DIMENSION` entities**, verified by execution — but
  **we render the geometry block, not the CAD app**, so appearance is entirely this
  ticket's responsibility. `DIMLFAC` is 100.0 on every shipped `EZ_*` dimstyle and
  must be set to 1.0 against the model's 1 unit = 1 mm, or a 4000 mm wall prints as
  "400000". R2000 is the hard floor.
- **Rule 7's rounding problem has a free answer**: the model is integer
  millimetres, so a chain sums exactly. The classic embarrassment is unavailable
  unless we introduce it by rounding for display.

Deliverable: the annotation rule set, precise enough to implement, plus a worked
example on one plan.
