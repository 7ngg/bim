---
id: 28
title: Whether a Room may be more than one rectangle
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
---

# Whether a Room may be more than one rectangle

## Question

**Every stage of this system places one rectangle per Room, and that premise has
never been examined. It should be, because v1 can exactly represent 2.7 % of real
dwellings.**

The premise entered through the solver formulation — CP-SAT `AddNoOverlap2D` over
*n* boxes — and everything downstream inherited it: ADR 0001's tiling, the
Proposal contract's "exactly *n* axis-aligned boxes, one per Brief Room", the
Acceptance bar's aspect-ratio predicate, room-tag-at-centroid. No ticket ever
weighed one rectangle against two. It was never a decision; it was a default.

**Why nobody looked: a category error in the map.** "A room that is not a
rectangle" was filed in the *Non-orthogonal geometry* fog patch, next to angled
walls, so it inherited that patch's deferral. But **an L-shaped room is
orthogonal.** It is a union of two axis-aligned rectangles, and CP-SAT places two
rectangles as happily as one. Angled walls break the coordinate model; an L does
not. The map's own text shows the seam — ADR 0003 lets the **Envelope** have two
notches (L, U, T) while a **room** may not have one, and a real flat's corridor is
L-shaped precisely *because* the flat is.

**What is measured** (`experiments/rectangularise/rectilinear_k.py`, 1,200 Swiss
Dwellings dwellings, 8,293 rooms, at the 250 mm solve grid in the dwelling's own
frame). Smallest *k* such that the room is a union of *k* axis-aligned rectangles:

| k | rooms | cumulative | | all rooms in the dwelling within k |
|---:|---:|---:|---|---:|
| 1 — today | 0.5286 | 0.5286 | | **0.0267** |
| 2 — an L | 0.2497 | **0.7784** | | 0.2392 |
| 3 — T, U, S, Z | 0.0976 | 0.8759 | | 0.5467 |
| 4 | 0.0473 | 0.9232 | | 0.7200 |
| >4 | 0.0768 | 1.0000 | | — |

By room type, `k=1 / ≤2 / ≤3`:

| type | n | k=1 | ≤2 | ≤3 |
|---|---:|---:|---:|---:|
| CORRIDOR | 1,394 | **0.2984** | 0.5739 | 0.7654 |
| LIVING_DINING | 619 | **0.2391** | 0.4927 | 0.6543 |
| KITCHEN | 1,163 | 0.4342 | 0.7704 | 0.8899 |
| BATHROOM | 1,804 | 0.6181 | 0.8908 | 0.9507 |
| ROOM | 2,129 | 0.6740 | 0.8643 | 0.9239 |
| BEDROOM | 587 | 0.7053 | 0.8790 | 0.9353 |

Both counts are **upper bounds** and pessimistic in two ways: the decomposition is
guillotine-only, and a 250 mm raster turns a slightly-angled real wall into a
staircase that needs many rectangles. The true rectilinear complexity is lower.

**What has to be decided:**

1. **Whether a Room may be more than one rectangle at all**, and if so how many.
   The recommendation on the evidence is **one or two, not three**: k ≤ 2 takes
   per-room exact representation from 52.9 % to 77.8 % and corridors from 30 % to
   57 % for a single new degree of freedom, while k = 3 buys 9.8 more points per
   room and triples the box count. Note what it does *not* buy: at k ≤ 2 only
   **24 %** of dwellings are exactly representable, so *Rectangularising real
   rooms*' joint fit does not go away — it gets far less work to do.
2. **The solver cost, measured rather than assumed.** 1–2 boxes per Room is 8–20
   boxes at C13's 4–10 rooms, against the 24 boxes *Solver timing variance sweep*
   solved in 6.25 s — so it should be affordable, but the new constraint family
   (the two boxes of one Room must share a positive-length edge, and the Room must
   be connected) has never been posted. Re-run the sweep.
3. **What the Acceptance bar means for an L.** `dim.max_aspect` ≤3.0 and the
   minimum clear dimensions are undefined on a concave room. The clean answer is
   to apply them **per constituent rectangle** and area **per Room** — which is
   also what an architect means: each leg of an L must be usable. State it.
4. **Room tag placement.** *Dimensioning and annotation rules* deferred this
   explicitly: the centroid is the pole of inaccessibility only because every
   Space is a rectangle. For a two-rectangle Room the answer is likely the
   centroid of the **larger** rectangle, not a largest-inscribed-circle solver.
   Confirm against a drawn example.
5. **The Proposal contract.** §1's "exactly *n* axis-aligned boxes" becomes 1–2
   per Room. Decide what that does to the trained model, which must now emit a
   variable count, and to the arrangement metric, whose separation directions are
   currently a bounds test on one box per Room.
6. **Whether this changes the reject rule.** *Rectangularising real rooms* drops
   31 % of Swiss Dwellings, and the dropped population is the interlocked one —
   `STOREROOM` over-represented 1.71×, bbox overlap 2.9× higher. Those are exactly
   the dwellings an L would absorb. Re-measure the drop at k ≤ 2 before accepting
   the 31 % as the price.

**What does not break, and should not be re-litigated.** ADR 0001's erosion
survives unchanged — `erode(L, t_int/2)` is still exactly the region bounded by
the surrounding wall inner faces, reflex corner included, so the uniform-`t_int`
argument holds. ADR 0003's Envelope is untouched. Integer millimetres, the solve
grid, and the two-source Proposer are all untouched.

**Blast radius, stated honestly.** This reopens parts of four closed tickets —
*Canonical geometry model*, *Solver formulation for layout projection*,
*Dimensioning and annotation rules*, *Acceptance validator spec* — plus
`docs/spec/proposer.md` §1. That is the reason it is a ticket and not an
amendment. It is also the reason to settle it **before** anything is built:
every one of those tickets is cheaper to amend on paper than in code.

**Deliverable.** A decision, an ADR if it goes ahead, and the amendments to the
four tickets and the Proposal contract that follow. A measured solver cost for
item 2 is required, not optional — the argument for k ≤ 2 rests on it.

## What causes k > 2, measured — and it is mostly not room shape

`experiments/rectangularise/why_k.py`, 700 dwellings, 4,822 rooms. 21.1 % are
k ≥ 3, and that number decomposes into three causes of which only the third is
architecture:

| cause | share of k ≥ 3 rooms | evidence |
|---|---:|---|
| **features narrower than 500 mm** | **0.5833** | erasing them with a morphological open+close at 500 mm takes the room to k ≤ 2; **0.3103 become a plain rectangle** |
| **the room is not rectilinear at all** | **0.3232** | more than 10 % of perimeter off-axis, against **0.0059** of k = 1 rooms and 0.0346 of k = 2 |
| genuinely T, U, S or Z | the remainder | after clean-up, only CORRIDOR 0.2303 and LIVING_DINING 0.3258 |

A pipe boxing, a chimney breast, a structural nib and a door reveal each add a
reflex corner and therefore a rectangle, and none of them is a room shape. And a
splayed or angled wall becomes a **staircase** at 250 mm, needing one rectangle
per step — that is the genuine *Non-orthogonal geometry* problem, and **no value
of k fixes it**, which is a second reason not to chase k upward.

**The number that decides this ticket.** Coverage of the room by its best two
inscribed rectangles:

| population | median | p25 | p5 | share ≥ 0.95 |
|---|---:|---:|---:|---:|
| all rooms | **1.0000** | 1.0000 | 0.8812 | **0.8805** |
| k ≥ 3 rooms only | 0.9412 | 0.8841 | 0.7437 | 0.4325 |

**Capping at two rectangles costs the median room nothing**, and 88 % of rooms
are at least 95 % covered. Even the genuinely complex ones keep 94 % of their
area. Both figures are lower bounds — the two-rectangle cover is greedy raced
against guillotine cuts, not optimal.

By type, `k ≥ 3` before and after the 500 mm clean-up: ROOM 0.138 → 0.046,
KITCHEN 0.219 → 0.053, BEDROOM 0.096 → 0.035, BATHROOM 0.099 → **0.095**
(barely moves — bathroom niches are genuine), CORRIDOR 0.410 → 0.230,
LIVING_DINING 0.472 → 0.326.

**This strengthens k ≤ 2 and weakens k ≥ 3.** Most of what looked like complex
room shapes is small hardware and angled walls; what remains is circulation and
open-plan living, and two rectangles already hold 94 % of even those.

**One consequence for the conversion.** If sub-500 mm features are what force a
third of rooms past k = 2, the corpus conversion should consider **cleaning them
before fitting** rather than trying to honour them at a 250 mm grid it cannot
represent them on anyway. That is a change to *Rectangularising real rooms*'
pipeline and should be decided here, since it only matters if k > 1.
