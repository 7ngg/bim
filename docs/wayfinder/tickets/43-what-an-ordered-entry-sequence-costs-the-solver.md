---
id: 43
title: What an ordered entry sequence costs the solver
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: []
writes:
  - experiments/solver-toy/
  - docs/research/solver-formulation.md
---

# What an ordered entry sequence costs the solver

## Question

*The Proposal cannot express zoning* named four properties a pairwise contract
cannot carry, and found three of them already reachable: sleeping-group
clustering is the shipped flow routine on a third node set, facade allocation is
a soft term over the Envelope's typed edge ring, and the front door opening onto
circulation is one predicate about one Space.

**The fourth is not, and it is the one this ticket prices.** *Entry → hall →
living* is an **order** on the circulation graph, and the single-commodity flow
encoding does not produce one. Flow gives **reachability**: room *r* receives its
unit, therefore you can get there. It says nothing about *how far along* the walk
*r* sits, so no constraint written over it can distinguish a plan whose front
door opens into a hall that opens into a living room from one whose front door
opens into a living room with a hall behind it.

The natural encoding is a **per-Room hop-count integer** — `d_entry = 0`, and for
every other Room `d_r = min over neighbours(d_v + 1)` posted as a disjunction over
the door literals `door_ij` the flow already reifies. That is a new integer per
Room and a new disjunction per pair, on a formulation whose H8 note specifically
records that it needs **"no auxiliary integers"**.

**Nothing on this map has ever measured what that costs**, and there are three
reasons to think the cost is not small:

1. Every solver number on the map was fitted **without** these variables, at
   15 s and τ = 4 — and *Solver timing variance sweep* found v1 **sits on the
   edge of the feasibility cliff, not below it**. A formulation that adds
   variables to a model already at its limit is not obviously affordable.
2. *Ergonomic minima* and *Whether a Room may be more than one rectangle*
   between them establish that **no solver measurement on this map covers the
   bottom half of C13's own 3–10 band** — so the regime where this would be added
   is also the regime nobody has measured.
3. ADR 0014 has just taken the variable count to **1.2–1.7×** the k = 1 control
   for the Rooms the Proposal names as two-part. Hop counts land on top of that,
   not instead of it.

**What has to be decided:**

1. **What the ordering property actually is**, stated precisely enough to post.
   "Entry → hall → living" is a slogan; candidates include *the entry Space's
   hop-1 neighbourhood contains no habitable Room*, *every habitable Room is at
   hop ≥ 2*, and a genuine total order over a named sequence. They cost
   differently and only the last needs hop counts at all — the first two may
   collapse back into predicates over the existing graph, which would settle this
   ticket without touching the solver.
2. **What it costs**, if hop counts really are needed: variables, solve time to
   first VALID, and the feasibility rate — measured the way ticket 15 measured
   the rest, across room counts and at **corpus-median** exposure, not the
   100 %-exterior detached case that confounded the earlier sweeps.
3. **Whether the corpus supports the rule you would post.** `experiments/zoning/`
   already has hop distance from the entrance per Room class over 2 500
   dwellings — social 1.21, private 1.66, circulation 0.32 — and the day/night
   gradient there proved **directional but not assertable** (private is *nearer*
   the door than social in 16.1 % of real homes). Check the ordering candidate
   against the same data before pricing it: a rule real dwellings break one time
   in six is not worth new integers.
4. **Whether it is worth it at all**, against the alternative that the three
   cheap properties already shipped capture most of what "the plan reads as
   designed" means. That is a judgement, and it should be made *after* 1–3, not
   before.

**Blocked by *The solver has only ever seen guillotine layouts*.** Both tickets
write `experiments/solver-toy/`, and 29 changes the ground truth every timing on
this map was measured against. Pricing a new encoding on a rig that is about to
be re-based measures the rig. Settle the ground truth first — the same argument
that blocked *The Proposal cannot express zoning* on ADR 0014.

**Deliverable.** Either a precise statement of the ordering property and its
measured cost, or — the outcome to be genuinely open to — a finding that the
property collapses into predicates the existing graph already supports, and no
new solver machinery is owed.

## Unblocked by *The solver has only ever seen guillotine layouts* (ADR 0018)

**The rig is not moving, so pricing an encoding against it now measures the
encoding.** That was the whole reason for the block: 29 was expected to re-base
the ground truth every timing on this map was measured against. It re-based
nothing — 4 discordant slots each way, McNemar p = 1.00, and zero discordant at
8–16 rooms — so **15 s, τ = 4 and Part II's percentiles all stand at their
published values** and are the correct baseline to price a per-Room hop-count
integer against.

Three things 29 leaves you that change how to run this:

1. **`experiments/solver-toy/` is yours alone now.** 29 is closed. It added
   `pinwheel.py`, `sweep_ng.py`, `report_ng.py`, `relation_margins.py`,
   `t_int_arithmetic.py`, `pinwheel_area_premium.py` and `corpus_guillotine.py`,
   and deliberately left `_guillotine` the **default** — do not re-base it.
   `sweep_ng.py`'s paired-arm shape is reusable as-is if you want to price the
   encoding on both cut structures rather than one.
2. **A hop-count integer should be priced on the non-guillotine arm too**, and
   cheaply — it is one extra value of `truth` in the same suite. 29's own result
   makes that worth doing rather than optional: the arms agree on *survivor rate*
   but the pinwheel arm reaches INFEASIBLE **significantly less often** (17
   against 2, p = 0.0007), so a new hard integer's effect on infeasibility is
   exactly the axis where the two arms are known to differ.
3. ⚠️ **A fixture defect you will hit at small `n`.** `AREA_PER_ROOM_M2` = 9.65 is
   below what the placeholder table needs at 7 and 8 rooms in **either** arm —
   both need 11.58. Below 7 rooms this Envelope family has no non-guillotine
   tiling at all. If you sweep low room counts, that is the harness talking, not
   your encoding.
