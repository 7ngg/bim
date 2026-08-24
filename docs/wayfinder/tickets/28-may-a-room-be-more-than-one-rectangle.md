---
id: 28
title: Whether a Room may be more than one rectangle
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - docs/adr/
  - docs/spec/proposer.md
  - docs/spec/acceptance-bar.md
  - docs/spec/annotation.md
  # Declared on resolution rather than taken quietly. Nothing else was claimed
  # at the time, so the map's concurrency rule was satisfied; the entries are
  # here so the next ticket to want them can see.
  - CONTEXT.md          # the Space term, plus Part and Leg floor
  - docs/research/room-rectangles.md (new)
  - experiments/room-rectangles/ (new)
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

---

## Handed in by *The room-count envelope v1 promises* (ADR 0013)

**A dependency nobody had drawn: `resolve` must choose how many circulation
Rooms to invent, before the solver runs — and whether it can safely fix that at
one is your question, not its.**

`brief.md` §3 has `resolve` invent `corridor` / `entrance_lobby` because
`model.no_unassigned_area` means circulation must be Brief Rooms or the Envelope
cannot be tiled. It does not say **how many**. Measured over 46,800 Swiss
dwellings (`experiments/room-count-envelope/circulation_split.py`):

```
k=0  6.55%    k=1 75.11%    k=2 16.69%    k>=3 1.65%
```

and the right k rises with the programme — at 6 named rooms k=1 is 77.7 % and
k=2 is 18.9 %; at 9 named rooms k=2 is 26.0 %.

If **a Room may be more than one rectangle**, `resolve` fixes k = 1 and an
L-shaped corridor reaches the wing a single rectangle cannot. If it may not,
`resolve` has to *guess* k from the programme before any geometry exists, and a
wrong guess is not recoverable: too few leaves the Envelope untileable, too many
fragments circulation the solver then has to justify against
`circ.fraction_hard`.

This also moves your own arithmetic. k is inside the **engine room count**, which
ADR 0013 hard-gates at 3–10 — so a `resolve` that over-invents circulation spends
the ceiling on corridors and refuses Briefs that would otherwise have fitted.

---

## Resolution

**A Room is a union of at most two axis-aligned rectangles, and which Rooms are
two is decided by the Proposal, not by the solver.** ADR
[0014](../../adr/0014-a-room-is-one-or-two-rectangles-and-the-proposal-decides.md).
Findings `docs/research/room-rectangles.md`. Harness
`experiments/room-rectangles/`.

### The ticket's own framing was refused first

The question opens on *"v1 can exactly represent 2.7 % of real dwellings"*. That
is a statement about the **corpus**, and corpus representability is instrumental
— it buys retrieval pool and training data. No Homeowner asks whether a
particular Swiss flat converts. The decision is taken on **output naturalism**
and on **tiling slack** — `model.no_unassigned_area` makes surplus area
compulsory, and *What a room's area is allowed to be* measured
`dim.market_default_area` actively rewarding the bloat that absorbs it — with
corpus yield as a consequence rather than a reason, and re-owed as a measurement
rather than claimed.

### Item 1 — how many, and for which Rooms

**Two.** Not three, and the reason is not the box count. **An L is a shape an
architect draws; a T, U, S or Z room is a shape a plan is left with**, and there
is no account of a U-shaped bedroom that would survive a Practitioner asking why.

The measurement agrees from the other side, and this is the part the ticket did
not have: what survives at k >= 3 is **mostly not a room shape**. Rooms whose
perimeter runs more than 10 % off the dwelling axis are **0.63 %** at k = 1,
**4.45 %** at k = 2 and **35.03 %** at k >= 3. An off-axis wall becomes a
staircase at 250 mm needing one rectangle per step — the *Angled walls* problem,
which **no value of k fixes.**

Capping at two costs the median room **nothing** (its best two inscribed
rectangles cover it exactly, p25 likewise); 87.2 % of all rooms are >= 95 %
covered, and even rooms genuinely needing three keep a median 92.7 %.

**No type whitelist.** The engine bars nothing. The type distribution comes from
the corpus, which is already type-shaped and now measured at tolerance —
bedrooms, stores and generic rooms **69–72 %** rectangular, corridors and
open-plan living **26–30 %**. A whitelist would be a rule we invented; the
corpus distribution is one we measured.

### Item 2 — the solver cost, and it is the item that moved the decision

Two sweeps, 420 solves, at the shipped rig — `sweep_k2.py` (240) against a
guillotine truth where no L is needed, and `sweep_designA.py` (180) against a
truth where *j* Rooms genuinely are Ls, so that "which Room should be an L" has
an answer to be right or wrong about.

**The freedom costs no validity.** Every arm reaches a valid Plan at the k = 1
control's rate — 1.00 in band, 0.90 at twelve rooms — which is what an optional
part being a strict relaxation predicts. **It costs search, and it costs it
whether or not it is spent**: 3.9x the variables and **11–12x the time to a first
Plan at every room count**, and still ~11x in the arms whose penalty leaves
*zero* Ls.

**And it costs judgement.** The decisive table, over valid runs on a concave
truth:

| | recall | precision | spurious Ls |
|---|---:|---:|---:|
| Proposal decides | **1.00** | **1.00** | 0 |
| solver decides, unpenalised | 0.56 | **0.22** | **35** |
| solver decides, penalty 200 | **0.00** | — | 0 |

Nearly four wrong for every right one at zero, and **silence** at 200: the
penalty suppresses the correct Ls with the invented ones. There is no setting at
which a solver-decides design places Ls well, because rarity is not the axis the
problem lives on.

**By type it is close to reversed.** Against each Brief's real kind multiset
(`kind_rates.py`), Spearman between the solver's L-rate and how *rectangular*
real dwellings keep that type is **+0.795** — store 0.338 and bedroom 0.295
against corpus rectangularity 0.720 and 0.721, corridor **0.100** against 0.303.
It reaches hardest for the types real homes keep rectangular and least for the
one real homes make an L 70 % of the time.

**Design A pays for the parts it uses; Design B pays for the parts it might
use.** Only the Rooms the Proposal names get a second box: **1.2–1.7x** the
variables and **1.1–2.8x** the time to first Plan, against a flat 3.9x and ~10x
for a solver-decides design. Time to a first Plan stays under **0.55 s**
throughout.

And Design A is the only arm that converts the extra rectangle into plans.
Survivor rate on concave-truth Briefs: **designA 0.500**, `k1_bbox` 0.417,
**solver-decides 0.361**, fair k = 1 control 0.333. Design B has the same
expressive power as Design A and realises almost none of it, because nothing
tells it which Room should use it.

⚠️ Design A **uses more of the time budget** — it proved optimality 4 times where
the bounding-box control did 17. Time to a *first* Plan is what C6's streaming
job model consumes, so that is the number that matters, but the gap is real.

That, with three structural arguments — retrieval already holds the L and would
be made to forget it; a penalty is an unfitted `ENGINE_CHOICE` constant governing
how often rooms are L-shaped, where the corpus supplies the distribution free;
and a solver-decides design **does not fix the corpus yield at all**, because a
Proposal that cannot carry an L leaves the conversion nothing to emit — is what
puts the second rectangle in the contract.

### Item 3 — the Acceptance bar on an L

`acceptance-bar.md` **§9.1**, new. Minimum clear dimensions and aspect ratio bind
**per part**; area binds **per Room**; circulation, wet cluster, entry and
windows bind per Room through *any* part; forbidden adjacency binds per part
pair. Every dimensional rule now has to declare which it binds, and that is a
column `rules.json`'s holder owes.

Any part beyond the first carries a **leg floor of 900 mm clear** — the hall and
corridor minimum already in the bar — because below that it is a niche, not a
leg. One new hard predicate, `dim.leg_join`: the two parts share at least 900 mm
of edge, or the "Room" is two rooms with no door between them.

⚠️ **This killed §9's sliver argument**, which the ticket did not anticipate.
That argument rests on *"Spaces are `erode(rect, t/2)` — rectangles"*, and
`erode(A ∪ B, r)` is **strictly larger** than `erode(A, r) ∪ erode(B, r)` — the
band across the shared edge is interior and survives. Binding the minima per
solved part is *conservative*, so the conclusion holds and no predicate is added,
but the reasoning is replaced. ⚠️ Same section: its dropped corridor-pinch
allowance was dropped because *"a rectangular Space has no localised anything"*,
which stops being true — the question returns as `dim.leg_join`, with the
opposite sign.

### Item 4 — the room tag

**The centroid of the larger constituent rectangle**, and the ticket's guess was
right for a reason it did not state: a Room's own centroid can land **outside its
own Space**. Asserted, not feared — `erosion_check.py`, for a 6.0 x 1.2 m leg
with a 1.2 x 6.0 m return, the Space centroid is at (1 800, 2 400), in the notch,
which belongs to a different room. The largest-inscribed-circle machinery
`annotation.md` §7 deferred is **still not needed**.

The tag's dimensions line and the room schedule carry **both legs**,
`4400 x 3400 + 2100 x 1800`, never a bounding box — a bbox claims floor area the
Room does not have, beside an area figure that does not include it.

⚠️ **"Confirm against a drawn example" could not be done.** Nothing on this map
has rendered a plan; `experiments/az-drawing/` holds two DXF encoding probes and
no renderer. Containment is proved; legibility is owed by *Look at the converted
corpus*.

### Item 5 — the Proposal contract and the metric

`proposer.md` §1 becomes **one or two boxes per Room**, four integers each,
sharing an edge; §2.3 gives the trained model a **fixed two-part slot with a
presence token**, so the sequence length stays `2n` and it stays a set
transformer rather than a variable-length decoder.

§5's extractor moves to the **part** index space, excluding same-Room pairs, and
this is **forced rather than chosen**: an L and the Room in its notch have a
positive best separation cost on all four options, and `select_relations` abstains
only on a small *margin*, never on a positive *cost*. At Room level it would
assert a separation the truth contradicts — a manufactured confident-wrong
relation, which ticket 24 measured as fatal in company. Their parts are
separable. At one part per Room the extraction is bit-identical to what shipped.

⚠️ **A live defect fell out of this and it is not about parts.** Nothing filters
on positive cost *at all*, so an overlapping Proposal — which a trained model
emits routinely — already has separations asserted it never made. True at k = 1
today. Handed to *The retrieval index and warp procedure*.

⚠️ **Every count threshold in §5 is now in a moving unit.** The pair count is
quadratic in *parts*, up to 4x — severity in millimetres is not. Ticket 24 had
already reached "counting is the wrong unit"; this is the second, independent
reason.

### Item 6 — the reject rule: NOT resolved here, and owned

Ticketed as *Re-measure the conversion at two rectangles per Room*, with the
ablation evidence and a falsifiable prediction: hard adjacency is the dominant
reject cause (73.6 % converted as shipped, **95.6 %** with it off) and an L is
precisely what reaches an adjacency a rectangle cannot. That is a prediction off
an ablation, not a measurement of the thing, and it is not quoted as one. Item 2
was the required measurement and it was made; this is a different harness.

### The conversion clean-up is refused, and the ticket's evidence for it is an artefact

⚠️ **`why_k.clean()` does not do what it is documented to do.** Its dilation is
clipped to the room's own bounding box — which is the array `why_k.py` gives it —
so the composition reduces to **eroding every room by 500 mm on all sides and
never restoring it**; a 500 mm strip is deleted outright, making the real
threshold ~750 mm; and it fills **no** notch at any size. Measured against
synthetic masks in `experiments/room-rectangles/morphology.py`, which carries a
selftest and is a corrected drop-in.

Re-measured at a real 500 mm, single-rectangle rooms go **0.5286 → 0.5367**.
Eight tenths of a point, against the 58.3 % / 31.03 % this ticket proposed acting
on.

**And the inflator story is wrong in its main term, not merely mismeasured.** A
2 % *area tolerance* — which subsumes any small feature, morphology or not —
moves per-room k = 1 by 1.1 points. **Non-rectangularity in this corpus is real
architecture, not pipe boxings.** What the ticket got right is the other term:
the off-axis table under item 1.

### What did not reopen, and one claim that was asserted rather than inherited

ADR 0001's erosion, ADR 0003's Envelope, the 250 mm grid, integer millimetres and
the two-source Proposer are untouched. The erosion is the one claim this ticket
makes about a closed ADR, so it is **checked**: `erosion_check.py` verifies that
`erode(L, t_int/2)` equals the polygon bounded by the surrounding wall inner
faces **at the reflex corner too**, pointwise and not merely in area, that the
result is still rectilinear on integer millimetres with exactly one reflex
corner, and that the union's erosion exceeds the union of erosions by precisely
the shared-edge band. All hold at `t_int` 150.

**The dimension chains are untouched, and that was checked rather than assumed**:
`annotation.md` §4.2 chains the wall **faces** reaching a side, not the rooms,
and §4.3's tier-2b catches every face reaching none — so a concave Room adds
faces and no machinery. The Drawing check needs **no new predicate**.

**The IFC introduces no Boolean**, so ADR 0011's real restriction is not engaged.
⚠️ Whether Reference View accepts an `IfcArbitraryClosedProfileDef` as the swept
profile of a now-concave `IfcSpace` is **not verified**, and is explicitly not
claimed — *What geometry an IfcSpace actually gets*, which also takes over the
§5/§12 storey-height contradiction that had no ticket at all.

### Things this session got wrong, recorded because the numbers caught them

1. **A first recommendation of the solver-decides design**, on the ground that it
   preserved every calibrated number. The solver work is *identical* either way;
   it was cheaper only in spec churn, and the destination of this map **is** the
   spec.
2. **A harness bug that manufactured the refutation of that design.** Absent
   parts are pinned at the origin, and separation relations were posted on them
   ungated: `x2[p] <= x1[q]` with `q` absent reads `x2[p] <= 0` and forces a
   present primary to zero width. It reported 36 % INFEASIBLE against a control
   at 0 % and made the L look compulsory. Fixed; the sweep was re-run from
   scratch and every number above is post-fix.
3. **A per-type "the solver picks the wrong rooms" claim**, computed against
   `scenarios.composition(n)` as the denominator. That is not the Brief's actual
   kind multiset — `assign_kinds` draws from a filler list within `comp_bounds` —
   so the rates were wrong, and the claim was withdrawn from all three documents
   rather than repaired with a bad denominator. ✅ **Later re-established
   properly**: `kind_rates.py` regenerates all 40 Briefs and takes their real
   multisets, and the claim survives at **Spearman +0.795**. Withdrawing it first
   was right; it was a coin-flip whether it would come back.
4. **A prediction that the bounding-box control would be the pessimal k = 1
   reading.** It beat the larger-part control. Recorded as unexplained.

### What this hands on

| To | What |
|---|---|
| *Re-measure the conversion at two rectangles per Room* (**new**) | item 6, with the ablation and a falsifiable prediction |
| *What geometry an IfcSpace actually gets* (**new**) | the concave `IfcSpace` profile, and the §5/§12 contradiction that was unowned |
| *The retrieval index and warp procedure* | the positive-cost extractor defect, live at k = 1; and §5's moving count unit |
| *H8 and the single-aspect flat* | a Room may now present a **leg** at the facade — a relief that may not be worth taking, with three options and the choice left there |
| *What the engine says when the Envelope is bigger than the programme* | ADR 0013's circulation-count dependency, discharged: one Room per circulation type, the L covers the multi-wing case |
| *Two room vocabularies in one file* | telling `hall` / `entrance_lobby` / `corridor` apart is what would make that rule measurable |
| *Look at the converted corpus* | the `why_k.clean()` defect, and the room-tag legibility check |
| *The Proposal cannot express zoning* | **unblocked** — §1 has moved and stopped moving |
| `rules.json`'s holder | `dim.leg_join` hard, `dim.prefer_single_part` soft, and a which-part-does-this-bind column on every dimensional rule |
