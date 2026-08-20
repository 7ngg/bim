---
id: 27
title: Look at the converted corpus
parent: map
labels: [wayfinder:prototype]
status: open
assignee:
blocked_by: []
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
