# A Room is one or two rectangles, and the Proposal decides which

Every stage of this system placed **one rectangle per Room**, and no ticket ever
weighed that. It entered through the solver formulation — CP-SAT `AddNoOverlap2D`
over *n* boxes — and ADR 0001's tiling, the Proposal contract, the Acceptance
bar's aspect predicate and room-tag-at-centroid all inherited it. It was never a
decision; it was a default, and it was invisible because *"a room that is not a
rectangle"* had been filed under the map's **Angled walls** fog. An L-shaped room
is orthogonal. CP-SAT places two rectangles as happily as one.

**A Room is a union of at most two axis-aligned rectangles, and which Rooms are
two is decided by the Proposal, not by the solver.**

Findings: `docs/research/room-rectangles.md`. Harness:
`experiments/room-rectangles/`.

## Two, not three

Exact rectilinear complexity over 8,293 real Swiss rooms
(`experiments/rectangularise/rectilinear_k.py`, at the 250 mm solve grid in the
dwelling's own frame): **52.9 %** of rooms are one rectangle, **77.8 %** are at
most two, 87.6 % at most three. Whole dwellings: 2.7 % / 23.9 % / 54.7 %.

Three would buy 9.8 more points per room and triple the box count, and that is
not why it is refused. **An L is a shape an architect draws; a T, U, S or Z room
is a shape a plan is left with.** The dining leg of an L sits by the kitchen and
the living leg faces the window; an L-shaped corridor is L-shaped to reach a
wing. There is no comparable account of a U-shaped bedroom, and admitting one
would mean defending every plan that contained it.

The measurement agrees from the other side. What survives at k ≥ 3 is **not room
shape**. Share of rooms whose perimeter runs more than 10 % off the dwelling
axis: **0.63 %** at k = 1, **4.45 %** at k = 2, **35.03 %** at k ≥ 3. An off-axis
wall becomes a staircase at 250 mm needing one rectangle per step — the genuine
*Angled walls* problem, which **no value of k fixes**, and the second reason not
to chase k upward.

Capping at two costs the median room **nothing**: its best two inscribed
rectangles cover it exactly, p25 likewise, and **87.2 %** of all rooms are at
least 95 % covered. Even the rooms that genuinely need three or more keep a
median **92.7 %** of their area under a two-rectangle cover.

The type split is the architectural intuition, measured: bedrooms, stores and
generic rooms are **69–72 %** rectangular, corridors and open-plan living
**26–30 %**. A bedroom is a rectangle because a bed and a wardrobe want one; a
corridor is an L because the flat is.

## The solver must not be the one to decide

The obvious cheap design — leave the contract alone and let the solver grow an
optional second rectangle wherever tiling wants one — is refused on measurement.

**1. It puts Ls on the wrong rooms, and the ordering is close to reversed.**
`sweep_k2.py` gives every Room an optional second rectangle against a
**guillotine** truth where none is needed, so every L is gratuitous by
construction. It makes them on **20–32 %** of eligible Rooms, rising with room
count. `kind_rates.py` then asks *which* rooms, against each Brief's real kind
multiset:

| kind | solver L-rate | corpus rooms that are one rectangle |
|---|---:|---:|
| store / utility | **0.338** | 0.720 |
| bedroom | **0.295** | 0.721 |
| bathroom | 0.282 | 0.618 |
| kitchen | 0.179 | 0.440 |
| corridor | **0.100** | 0.303 |

**Spearman +0.795**, and positive is the wrong sign: the types real dwellings keep
most rectangular are the ones it reaches for hardest, and the type real dwellings
make an L 70 % of the time is the one it touches least. Its objective knows about
corner displacement and nothing about what a room is for.

**2. Told to find the right L, it cannot; penalised, it finds none.**
`sweep_designA.py` puts genuine Ls in the ground truth, so *which* Room should be
an L has an answer. Over valid runs:

| | recall | precision | spurious Ls |
|---|---:|---:|---:|
| Proposal decides | **1.00** | **1.00** | 0 |
| solver decides, unpenalised | 0.56 | **0.22** | **35** |
| solver decides, penalty 200 | **0.00** | — | 0 |

Nearly four wrong for every right one at zero, and **silence** at 200 — the
penalty suppresses the correct Ls along with the invented ones. The knob has no
good setting, because rarity is not the axis the problem lives on.

**3. It is not free even when it is unused.** Against the k = 1 control, the
optional-part machinery costs **3.9×** the variables and **11–12×** the time to a
first Plan at every room count — and still ~11× in the arms whose penalty leaves
*zero* Ls. Search space is paid for whether or not it is spent. Design A, which
gives a second box only to the Rooms the Proposal names, costs **1.2–1.7×** the
variables and **1.1–2.8×** the time. **Design A pays for the parts it uses;
Design B pays for the parts it might use.**

And it converts what it pays for. On concave-truth Briefs the survivor rate is
**0.500** for Design A, **0.361** for a solver-decides design and **0.333** for
the k = 1 control it barely improves on — the same expressive power, almost none
of it realised, because nothing tells it which Room should use it.

**4. It does not fix the corpus yield**, which is one of the three grounds this
decision rests on. The 31 % conversion drop is a property of the *conversion*,
and a Proposal that cannot carry an L leaves the conversion nothing to emit, so
the interlocked dwellings stay dropped however clever the solver is.

What the freedom does *not* cost is validity: every arm reached a valid Plan at
the control's rate, as a strict relaxation should. The cost is search and it is
judgement.

So room shape is decided where taste exists. Under C10 that is the Proposer: a
retrieved dwelling's corridor is an L because a real one's was, and a trained
model's is because its corpus taught it. **The solver's presence variables are
fixed by the Proposal, not searched.** This is C10 made literal rather than
weakened — *model proposes* now includes shape.

It also means the engine needs **no type whitelist**. Scoping the freedom by hand
*does* improve the ordering — Spearman −0.316 — but only because we picked the
four types, which is us supplying the taste rather than measuring it. The corpus
distribution is already type-shaped (§2) and it is the one we did not invent.

## What this costs, measured

`experiments/room-rectangles/sweep_designA.py` projects Proposals that already
contain Ls — a guillotine dissection of *n* + *j* rectangles with *j* adjacent
pairs merged, so the truth genuinely is concave and still tiles exactly, asserted
per scenario by `l_truth_check.py`. Rig matches the shipped decision: 15 s, τ = 4,
`mm_affine`, eroded minima at `t_int` 150, corpus-median exposure, σ = 0.5 m, four
workers, run alone so the seconds are not contended.

**Survivor rate over 36 concave-truth scenarios: 0.50, against 0.33 for the fair
k = 1 control** — the same Brief handed the L's larger part, which is all a k = 1
Proposal can carry. Time to a first Plan stays under **0.55 s** at every room
count and L-count tested.

⚠️ **Design A uses more of the time budget**: it proved optimality 4 times where
the k = 1 bounding-box arm did 17, and ran to the 15 s limit in most cells. Time
to a *first* Plan is what C6's streaming job model consumes, so that is the number
that matters, but the gap to proven optimality is the honest cost of the extra
freedom. ⚠️ And a prediction of this session's was wrong: the bounding-box control
was expected to be the pessimal k = 1 reading and **beat** the larger-part one.
Recorded as unexplained in `docs/research/room-rectangles.md` §4 rather than
explained away.

## What follows, and what does not

**The Proposal contract** (`proposer.md` §1) becomes one or two boxes per Room,
four integers each, the two sharing an edge. No validity guarantee, no adjacency
graph, no wall geometry — unchanged.

**The arrangement metric** (`proposer.md` §5) extracts in the **part** index
space, excluding same-Room pairs. This is forced, not chosen. An L and the Room
sitting in its notch have a **positive** best separation cost on all four
options, and `select_relations` abstains only on a small *margin* — never on a
positive *cost*. At Room level it would therefore assert a separation the truth
contradicts, manufacturing exactly the confident-wrong relation ticket 24
measured as fatal in company. Their parts are separable, so extracting over parts
keeps the constraint that abstaining would have thrown away. When every Room is
one part this is bit-identical to the shipped extractor.

**The Acceptance bar** binds minimum clear dimensions and aspect ratio **per
constituent rectangle** and area **per Room**, which is also what an architect
means: each leg of an L must be usable. Any rectangle beyond the first carries a
universal leg floor of **900 mm clear** — the hall and corridor minimum already
in the bar, so no new number and no new provenance — because below that it is not
a leg of a room, it is a niche. One new hard predicate: the two rectangles must
**share at least 900 mm** of edge. Its realisable value at the shipped grid and
`t_int` 150 is **1 100 mm**, per ADR 0009 and `CONTEXT.md`'s *Realisable
minimum*.

**`acceptance-bar.md` §9's sliver argument is dead.** It rests on *"Spaces are
`erode(rect, t/2)` — rectangles"*, and `erode(A ∪ B, r)` is strictly larger than
`erode(A, r) ∪ erode(B, r)`: the band across the shared edge survives. Binding
H4/H5 per constituent **solved** rectangle is conservative — it under-states the
true clear leg — so no sliver can pass, but the reasoning has to be replaced
rather than kept. The same section's dropped corridor-pinch allowance was dropped
because *"a rectangular Space has no localised anything"*, which stops being
true; it returns as the join predicate, with the opposite sign.

**The room tag** goes at the centroid of the **larger** constituent rectangle,
not of the Room — a Room's centroid can fall in the notch, outside its own Space.
`annotation.md` §7's *"it becomes needed the day non-rectangular rooms do"* is
discharged: the largest-inscribed-circle machinery still is not needed, because
the larger rectangle is a rectangle.

**Not reopened, and the one claim about a closed ADR is asserted rather than
inherited.** `experiments/room-rectangles/erosion_check.py` checks that
`erode(L, t_int/2)` equals the polygon bounded by the surrounding wall inner
faces **at the reflex corner too** — pointwise, not merely in area — that the
result is still rectilinear on integer millimetres with exactly one reflex
corner, and that `erode(A ∪ B, r)` exceeds `erode(A, r) ∪ erode(B, r)` by
precisely the shared-edge band. All hold at `t_int` 150. ADR 0001's
uniform-`t_int` argument therefore holds unchanged.

ADR 0003's Envelope, the 250 mm grid, integer millimetres and the two-source
Proposer are untouched. **The dimension chains are untouched**, and that was
checked rather than assumed: `annotation.md` §4.2 chains the wall **faces**
reaching a side, not the rooms, and §4.3's tier-2b catches every face reaching
none, so a concave Room adds faces and no new machinery.

**The IFC introduces no Boolean**, which is the restriction ADR 0011 actually
carries: `ifc-export.md` §6 already makes `IfcSpace.Body` a `SweptSolid` of *the
Space polygon*, and an L polygon is one closed profile swept once. ⚠️ **Not
verified here**: whether Reference View accepts an `IfcArbitraryClosedProfileDef`
as that profile, as against the rectangles §5 currently relies on. One line, and
it belongs to `ifc-export.md`'s holder — do not read this paragraph as having
cleared it.

> ✅ **Cleared, and the comparison in it was wrong.** *What geometry an `IfcSpace`
> actually gets* verified RV1.2's `Body SweptSolid PolyCurve Geometry` template
> first-hand: `SweptArea = IfcArbitraryClosedProfileDef, IfcArbitraryProfileDefWithVoids`,
> `OuterCurve = IfcIndexedPolyCurve`. **And §5 relies on no rectangles** — the
> export research's entity census of the authored model is 12
> `IfcArbitraryClosedProfileDef` and **zero** `IfcRectangleProfileDef`, because
> `add_wall_representation` builds an arbitrary closed profile for a plain
> rectangular wall. An L costs no new entity type. `ifc-export.md` §6.1.

## The corpus clean-up this ticket expected is refused

Ticket 28 proposed erasing sub-500 mm features from corpus rooms before fitting
them, on the evidence that **58.3 %** of k ≥ 3 rooms fall to k ≤ 2 under a
morphological clean-up and **31.03 %** become plain rectangles.

**Those figures are an artefact.** `why_k.clean()` does not do what it is
documented to do — its dilation is clipped to the room's own bounding box, which
is the array it is given, so the composition reduces to **eroding every room by
500 mm on all sides and never restoring it**; a 500 mm strip is deleted outright,
making the true deletion threshold about 750 mm; and it fills **no** notch at any
size. Re-measured with a corrected opening and closing at a real 500 mm, the
share of rooms that are a single rectangle moves from **0.5286 to 0.5367** —
eight tenths of a percentage point. Whole dwellings all-rectangle: 0.0267 to
0.0275.

So the clean-up is refused because it **buys nothing**, not because it is wrong
in principle: on a 250 mm grid, nothing narrower than one cell is representable
whatever the operator returns.

**And the ticket's inflator story is wrong in its main term, not merely
mismeasured.** It attributed 58 % of k ≥ 3 to small hardware. Allowing a 2 % area
tolerance — which subsumes any small feature, morphology or not — moves per-room
k = 1 by **1.1 points**, from 0.5286 to 0.5400. Non-rectangularity in this corpus
is **real architecture**. What the inflator story got right is the *other* term:
the off-axis table above, where 35 % of k ≥ 3 rooms are not rectilinear at all.

## Amendment: shape is arrangement, and the T and the Z were always admitted

[A two-part Room is a T or a Z as often as it is an L](../wayfinder/tickets/79-a-two-part-room-is-a-t-or-a-z-as-often-as-it-is-an-l.md),
**ADR 0045**. The decision — `k ≤ 2`, and the Proposal decides which Rooms are two
— **stands unchanged**. What is struck is the sentence above that defends it on
shape:

> ~~**An L is a shape an architect draws; a T, U, S or Z room is a shape a plan is
> left with.**~~ — **struck.** The cap does not deliver the shape. Two rectangles
> sharing an edge make an L, a **T**, a **Z** or a plain rectangle, and over the
> converted index **44,8 % are not an L**: 851 L, 334 T, 331 Z, 27 rectangle. The
> ADR asserted a shape the contract never constrained.

The sentence is left in place rather than deleted, because four sites quote it —
`room-rectangles.md`, `solver-formulation.md` IX.7, `selftest_parts.py` P9 and
this ADR — and a deleted sentence makes every quotation dangle.

**The `k ≤ 2` refusal is re-based on the two legs that survive, and they were
always the stronger half.**

1. **The box-count trade.** `k = 3` buys **9,8 more points per room** — 77,8 % at
   k ≤ 2 against 87,6 % at k ≤ 3 — and triples the box count.
2. **The off-axis measurement.** Share of rooms whose perimeter runs more than
   10 % off the dwelling axis: **0,63 %** at k = 1, **4,45 %** at k = 2,
   **35,03 %** at k ≥ 3. What survives at k ≥ 3 is **not room shape** — it is the
   *Angled walls* problem, which no value of k fixes.

Neither leg mentions shape, and neither is disturbed. What the struck sentence
was doing was making an **arrangement** claim inside a **buildability** cap: part
count and the leg floor are what the contract constrains; which shape those parts
form is the Proposal's, by this ADR's own rule that *"shape is an architectural
claim, and it is made where the arrangement is made."*

⚠️ **The type split above reads the same way once T and Z are separated.** *"A
corridor is an L because the flat is"* is right and it under-counts: **50,3 %** of
two-part corridors are not an L, and a T corridor reaches two wings. Corridor and
open-plan living carry **89,5 %** of all T and Z; the U-shaped bedroom this
section refuses to defend is **5 rooms in 1 069**.

⚠️ **`erosion_check.py`'s result is restated.** *"Still rectilinear on integer
millimetres with exactly one reflex corner"* holds for an L and for nothing else.
The general statement is **at most two reflex corners and at most 8 vertices** —
measured over all 1 543 corpus two-part Rooms as 4 ×27, 6 ×851, 8 ×665, max 8.
ADR 0001's erosion identity itself is untouched and now checked on all four
shapes.
