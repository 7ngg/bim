---
id: 27
title: Look at the converted corpus
parent: map
labels: [wayfinder:prototype]
status: open
assignee:
blocked_by: []
writes:
  - experiments/rectangularise/ — no shared artifact
---

# Look at the converted corpus

## Question

**Does a converted dwelling read as a home? Nobody has looked.**

*Rectangularising real rooms* settled how a real dwelling becomes rectangles and
measured the conversion hard: zero adjacencies destroyed, zero separation
directions flipped, per-room IoU median 0.895 on Swiss Dwellings, cell agreement
0.90, area error −3.5 %. Every one of those is a number about cells and graph
edges. *Acquire the datasets* §6 recorded that **no plan from either corpus has
been rendered or eyeballed**, and that is still true — now of the converted
output too, which is worse, because the conversion is a transformation we
invented rather than data we received.

This is the one check the metrics cannot stand in for. A conversion can score
0.90 cell agreement and still put the bathroom door where a person would not walk,
or turn a hall into a room, or produce a plan whose proportions read as generated
at a glance. C2 holds the internal model to a Practitioner's standard, and a
Practitioner's judgement of a plan is visual before it is numeric.

**What has to be decided:**

1. **Whether the conversion is acceptable as it stands.** Render converted
   dwellings beside their originals and look. If the answer is no, this ticket
   says what specifically is wrong — that is the deliverable, not a score.
2. **What the failure modes are, named.** The measurement can rank dwellings by
   cell agreement but cannot say what a bad one looks like. Sample across the
   range — the median, the p5, and a few INFEASIBLE ones to see what was
   rightly dropped — and name the recurring kinds.
3. **Whether the 15.7 % of relations the conversion *adds* are the right
   choices.** Those are the pairs where one room wraps another and a rectangle
   model must pick a side. The fit picks whichever side costs fewer misassigned
   cells. Whether that matches what a person would draw is a visual question and
   has no metric.
4. **Whether cell agreement is the right headline number.** It was chosen because
   it is the objective; that makes it self-serving as an evaluation. If eyeballing
   disagrees with it, say which quantity tracked judgement better.

**Do not re-litigate.** The conversion itself (ADR 0008), the reject rule, or the
choice of rectangles over polygons. This ticket can find that the conversion is
wrong and say why; it cannot reopen whether v1 emits rectangles.

**Deliverable.** A rendered sheet — originals against conversions, sampled across
the agreement range and across room counts — plus a stated verdict and, if the
verdict is negative, the named failure modes. Renderer belongs in
`experiments/rectangularise/`.

**Why now.** It blocks nothing formally, and it is the cheapest possible check on
the most load-bearing transformation on the map. Everything the Proposer will ever
learn about arrangement comes through this conversion.

## Inherited from *Area measurement convention* — one thing to look at that nobody has

ADR 0010 moved the Space boundary to the **finished** face, and in doing so
exposed a gap in a number this map already treats as settled.

*Ergonomic minima and the constraint table's missing half* validated the hard
floor against Swiss Dwellings — *"the published floor rejects 0.0% of real living
rooms and bedrooms, 1.2% of kitchens, 4.6% of WCs and 7.8% of storerooms"*, and
the `BATHROOM` refutation that re-fitted the split at 2.4 m². **Every one of those
figures was measured against corpus polygons whose own face convention is
unrecorded.** Swiss Dwellings does not say, and nothing on this map has asked,
whether its space polygons are drawn to structural faces or to finished ones.

**It matters, and the direction is known even though the magnitude is not.** If
the corpus polygons are **structural**, every real room in the validation set was
roughly 30 mm larger per axis than the room a person actually occupies, so the
published ergonomic floor is **slightly lenient** — small, systematic, and in the
wrong direction, which is the same sentence ADR 0010 wrote about our own areas.
If they are **finished**, nothing moves and that is a clean result worth having.

Add to this ticket's looking: **for a handful of converted dwellings, check
whether the corpus's wall thicknesses and space polygons are mutually consistent
with a bare structural leaf or with a finished build-up.** The corpus records
both, so the question is answerable by arithmetic on data already on disk — the
wall thickness between two spaces against the gap between their polygons. A
negative result (the corpus does not distinguish, or is internally inconsistent)
is itself the finding.

This is a looking task, not a re-fit. If it shows the floor is lenient, the re-fit
is owed by whoever holds the ergonomic layer, not by this ticket.

## Amended by *One internal thickness* — the question above was the wrong one

The face-convention check handed to this ticket has been answered, and the answer
is that the question does not apply.

**Swiss Dwellings records exactly one plane, and no finish layer at all.** A
corpus Space polygon is not offset from its wall: the polygons sit on the wall
body's own faces to within 1 mm a side, and `gap − t_mrr` has a mode at **exactly
2.0 mm**. So the corpus is not "structural" and not "finished" — the distinction
that ADR 0010 introduced **does not exist in the file**.

Two consequences, and the second is the one worth looking at:

1. **The leniency worry is unresolvable from this corpus**, not merely unmeasured.
   *Ergonomic minima*' Swiss validation compared our rectangle against a corpus
   plane that is neither of ours. That is a **stated limit** on those figures now,
   not a pending measurement. Nothing further is owed here.
2. **What is still worth looking at is the shape, not the plane.** This ticket's
   own reason stands untouched — no converted plan has ever been looked at, and
   everything the Proposer will learn about arrangement comes through that
   conversion. Do the looking.

`experiments/thickness-fidelity/` did the arithmetic (see its README, *"A corpus
room polygon is not offset from its wall"*); do not repeat it.

---

## Handed here by *What a room's area is allowed to be* (2026-08-22)

⚠️ **A labelling defect in `swiss_fit.json`, found while reading it.**
`fit_rects.py` line 727 labels a fitted dwelling with
`[t for t, _ in dw[k]][:n]` — the **unfiltered** head of the source list — while
`load_swiss_geoms` (line 628) has already dropped polygons below
`MIN_ROOM_AREA`. Where a dropped polygon is not last, **every label after it is
off by one**.

Measured against `measure_swiss`'s correctly-filtered list
(`experiments/room-area-bands/plane_check.py`): **22 of 1,787 fitted dwellings,
1.23 %**. This ticket renders converted dwellings, so it will render
mislabelled rooms unless it relabels from `swiss_rects.json` — which is keyed
identically and filters correctly. Fix the source or work around it, but do not
read `swiss_fit.json`'s `types` as-is.

**Also relevant to what this ticket is looking for.** The fitted rectangles are
on the **watershed / centreline** plane and the corpus polygons are on the
corpus's own (clear-ish) plane. The ratio is **1.243** at dwelling level but runs
**1.17× for `living_dining` to 1.58× for `wc`** — a small room's share of the
walls around it is a much larger share of its own floor. A rendering that
overlays the two without saying which plane is which will look like the
conversion inflated the wet rooms. It did not; that is the plane.
