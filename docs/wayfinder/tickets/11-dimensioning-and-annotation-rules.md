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

Waits on *BIM and CAD export stack* because rule 1 is worthless if `ezdxf` cannot
author real dimension entities, and on *Canonical geometry model* because rule 3
needs to know what a wall is.

Deliverable: the annotation rule set, precise enough to implement, plus a worked
example on one plan.
