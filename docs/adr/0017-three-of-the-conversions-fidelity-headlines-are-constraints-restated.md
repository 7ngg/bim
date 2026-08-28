# Three of the conversion's fidelity headlines are constraints restated, and the corpus is accepted anyway

**Status:** accepted
**Date:** 2026-08-25
**Ticket:** *Look at the converted corpus*
**Amends:** [ADR 0008](0008-a-corpus-dwelling-is-converted-by-solving-it.md) —
what its fidelity figures are evidence *of*
**Evidences:** [ADR 0003](0003-the-envelope-is-an-inner-face-ring-of-typed-edges.md) —
its two-notch cap, recorded there as *"unevidenced in both directions"*
**Related:** [ADR 0014](0014-a-room-is-one-or-two-rectangles-and-the-proposal-decides.md),
[ADR 0016](0016-the-conversion-names-its-own-ls.md)

## Decision

**The converted corpus is accepted as the Proposer's arrangement source.** A
converted dwelling reads as a home. That was the one check no metric on this map
could stand in for, and it has now been made: 67 dwellings rendered beside their
originals, sampled across the cell-agreement range, across room counts, and
across every named sub-population — `experiments/rectangularise/render_sheet.py`,
sheets at `out/sheets/SHEET.html`.

Three things change with the acceptance.

**1. Three of the four fidelity headlines are demoted from evidence to
restatement.** Each is a hard constraint in `fit_rects`, so a dwelling that would
violate it is *refused* rather than converted, and the resulting zero measures
the constraint rather than the conversion:

| quoted as | what it actually is |
|---|---|
| *"zero adjacencies destroyed"* — `edges_lost = 0` on all 2,317 | contact is posted hard. **`edges_lost = 0` and "9.5 % refused" are one fact stated twice**, and only one of them was in the headline. |
| *"zero separation directions flipped"* | the true relations are posted hard. `flipped` and `weakened` are **0 by construction** over all 97,090 axis-pairs. |
| per-room area error inside ±10 % | the band **is** ±10 %, posted hard. p99 of \|aerr\| is 0.111. |

What is genuinely unconstrained, and therefore quotable: `cell_agreement`, the
IoU distribution, **the refusal rate**, and `boundary_lost`.

**2. Cell agreement stays the headline, and never travels alone.** It was chosen
because it is the fit's own objective, which makes it self-serving as an
evaluation — the ticket was right to ask. Checked against the eye it is
*honest*: it ranks dwellings the way looking at them does (rank correlation
**0.825** with worst-room IoU), and of the 69.6 % of conversions scoring ≥ 0.90,
only **0.8 %** hide a room at IoU ≤ 0.30. But it is an average over cells and a
person looks at the worst room, and at a fixed agreement the worst room is wide —
in the 0.88–0.92 band, p10 0.45 against p90 0.82. **Every published cell
agreement is accompanied by the worst-room IoU of the same population.**

**3. Four failure modes are named, and none of them is the rectangle model.**
ADR 0008's mechanism, ADR 0016's second rectangle and the choice of rectangles
over polygons are all untouched by this looking, and two of them are visibly
vindicated by it.

## What the sheets show

**The conversion is good, and the eye agrees with the number.** At p95 it is
effectively lossless — the converted plan is the original with its walls
straightened. At the median (cell agreement 0.935) it is a plausible flat that
keeps the original's arrangement, its circulation and its room sizes. ADR 0016's
L-shaped corridors — 22.0 % of corridors, 42.2 % of open-plan living/dining —
read as real circulation spines rather than as two rooms with the wall left out,
which is what the one-rectangle conversion was producing.

Two questions the ticket carried are answered by looking, and one of them was
asked the wrong way round.

**The relations the conversion adds are the right choices — but they are not
what the ticket thought they were.** They were described as *the pairs where one
room wraps another and a rectangle model must pick a side*. By construction a
`spurious` relation is a pair whose bounding boxes **overlapped** on that axis in
the corpus and no longer do after squaring: squaring necessarily turns an
ambiguous separation into a definite one, and that is the only free choice the
fit makes about relations at all. Rendered, those picks are what a person would
draw.

The ticket quotes 15.7 %. **Two rates are both correct and answer different
questions**, and `rectangularisation.md` §11.4 publishes only the first:

- **paired**, over the 1,779 dwellings both arms converted — 15.64 % → **13.58 %**.
  The like-for-like measure of what ADR 0016's second rectangle bought.
- **all conversions**, over the 2,317 dwellings and 97,090 axis-pairs k ≤ 2
  actually produced — **12.62 %**. What the corpus the Proposer sees contains, and
  the one to quote downstream.

The gap between them is not rounding: the 538 dwellings k ≤ 2 rescued and k = 1
refused carry a **lower** spurious rate than the ones both arms managed, so
rescuing them improved the corpus twice over.

**ADR 0014's tag placement reads as deliberate.** An L-shaped Space tagged at the
centroid of its **largest constituent rectangle** looks placed, not slid. Ticket
28 item 4 asked for a drawn example and there was no renderer on the map to give
one; `render_sheet.py` gives it, and the answer is yes.

## The four failure modes

**1. Off-frame wings — rare, and total.** `dwelling_frame` rotates a dwelling
onto **one** angle, taken from the minimum rotated rectangle of the whole union.
A dwelling built on two angles — a wing splayed off a spine — has every room in
the second wing sheared, and the conversion emits **a different flat**: still
plausible, still a home, not *this* home. It is the whole p5 tail, and it is not
a solver failure — those dwellings come back OPTIMAL.

| room off frame by | dwellings | cell agreement | worst-room IoU |
|---|---:|---:|---:|
| 0–2° | 90.2 % | 0.941 | 0.768 |
| 2–5° | 3.5 % | 0.844 | 0.699 |
| 5–10° | 3.5 % | 0.876 | 0.745 |
| **10–20°** | **1.5 %** | **0.705** | ~~0.167~~ |
| 20°+ | 1.2 % | 0.676 | ~~0.429~~ |

⚠️ **Corrected by ADR 0031 — this table is on 400 dwellings and its last two rows
hold six and five of them.** The IoU reversal between the two bands should have
been read as a sample size, and was not. Over the **full 2,317-dwelling converted
index** the bands are **0.397** and **0.353**, monotone, and the population is
**4.79 %** at ≥ 10° rather than the 2.7 % this table implies.
`rectangularisation.md` §15.1. No decision ever rested on the struck figures, but
they were quoted in three places.

**And the map was already refusing this population without saying so.**
`proposer.md` §2.2.4's `worst_room_iou ≥ 0.30` gate takes **39.6 %** of it, and
**28.6 %** of everything that gate removes is off-frame. The residue — 67
dwellings, 2.89 % of the index — is kept, labelled with `frame_residual`, and
demoted by the pre-rank that already exists (ADR 0031).

**Nothing published faces this, so there is nothing to copy.** Every generator in
`docs/research/floorplan-generation-stack.md` fits axis-aligned rectangles, and
every corpus the field trains on — RPLAN, LIFULL — is **already orthogonal**, so
the second angle never arrives. Swiss Dwellings is surveyed geometry and is not.
The absence of prior art is a finding, not a gap in the reading.

**2. Floor no Room claims, drawn as a room-shaped hole with no name.** Exact
tiling is posted **soft** (C10's amendment), so an Envelope cell no Room takes is
legal and the objective merely charges for it. Nobody had seen one. Measured over
400 dwellings, splitting the Envelope's deliberate notch **under-cut** — which is
correctly left empty — from real dwelling floor:

| | median | p90 | max |
|---|---:|---:|---:|
| uncovered, total | 2.31 m² | 6.63 m² | 11.00 m² |
| — Envelope over-reach *(correct)* | 0.44 m² | 4.06 m² | 8.56 m² |
| — real dwelling floor | **1.19 m²** | 3.25 m² | 8.38 m² |
| — of that, **enclosed** by rooms | 0.00 m² | 0.44 m² | 3.69 m² |

Most of it opens onto the Envelope edge and reads as a re-entrant in the outline,
which is harmless. The enclosed remainder is not: **15.0 % of dwellings carry an
enclosed void ≥ 0.25 m², 10.0 % ≥ 0.5 m², 4.8 % ≥ 1 m²** — floor with walls round
it and no name, indistinguishable on a drawing from a room. It is invisible in
every number this map publishes because it is buried inside `uncovered`, which
counts the correct case and the incorrect one together.

The market has an answer to this one: DPLAN's rectangular-dual construction
(`floorplan-generation-stack.md` §5.2) **guarantees no overlapping rooms and no
empty space** by construction. It buys that guarantee with a graph-theoretic
formulation that cannot carry our dimensional constraints, so it is not a fix to
adopt — but it establishes that exact tiling is a *property a plan generator can
be expected to have*, which is the standard C2 holds the internal model to.

**3. Lost façade.** A room that faced the outside in the corpus and does not
after conversion: **4.1 %** of the 14,200 façade-facing rooms, and **22.5 %** of
dwellings lose at least one. This is the only fidelity number in the set that
nothing constrains, and it is the geometric half of H8 arriving from the corpus
side.

**4. Envelope loss is the dominant quality term — and ADR 0003's cap is not what
causes it.** Not the rectangle model, not the solver, not the room count: how far
the v1-expressible Envelope is from the dwelling's real outline predicts the
conversion's quality better than anything else measured.

| envelope loss at k = 2 | dwellings | worst-room IoU | share with a room ≤ 0.5 |
|---|---:|---:|---:|
| < 0.01 | 39.8 % | 0.844 | 10.5 % |
| 0.03–0.06 | 16.6 % | 0.738 | 15.3 % |
| 0.10–0.20 | 8.0 % | 0.483 | **53.5 %** |
| ≥ 0.20 | 1.9 % | 0.293 | **77.8 %** |

**The cap is at the knee of its own ladder, and raising it would not help the
dwellings it appears to hurt.** Corpus-wide median envelope loss by notch count
is 0.1610 / 0.0503 / **0.0178** / 0.0114 / 0.0096 at k = 0…4: a third notch buys
0.6 percentage points and a fourth buys 0.2. On the 230 dwellings above 0.10 loss
— the ones the cap looks responsible for — going to four notches moves the median
only 0.136 → 0.105, and **56 % are still above 0.10, 89 % still above 0.05**.
Their outlines are not bounding-box-minus-notches at any count. And the k ≤ 2
ablation's *"up to 4 notches"* arm converts **88.0 %** against the shipped
**93.2 %**: a tighter Envelope leaves the rectangles less slack inside it.

So ADR 0003's number is **vindicated** and its shape *family* is what the
evidence questions. The ADR recorded the cap as *"unevidenced in both
directions"*; that sentence is now false and must go either way.

## What the refusals look like

242 of 2,549 dwellings (**9.5 %**) come back INFEASIBLE. Rendered, they are
**ordinary flats** — nothing pathological, nothing a person would look at and
call unrepresentable. The ablation (`out/ablate_k2.log`) names the cause: the
hard **adjacency** constraint. Dropping it converts 99.2 % against the shipped
93.2 %, while relaxing the area band to ±25 % recovers only 5 of 13. Refused
dwellings are slightly larger (median 8 rooms against 7) and slightly thinner
(55.4 % against 42.6 % have a room below the 1.25 m centreline leg floor).

This ADR does not reopen the reject rule — the ticket forbade it and the rule is
ADR 0008's. It records that **the refusal rate is where the adjacency guarantee's
cost is actually paid**, and that the cost is not paid by unusual dwellings.

## Consequences

1. **`docs/research/rectangularisation.md` and every downstream quotation must
   stop citing `edges_lost = 0`, the zero flip count and the ±10 % area band as
   fidelity results.** They are the constraint set. Where fidelity is claimed,
   cite cell agreement **with worst-room IoU**, the refusal rate, and
   `boundary_lost`.
2. **Off-frame wings** (*The dwelling that is built on two angles*) and **the
   Envelope shape family** (*The two-notch cap is now evidenced, and more
   notches is not the fix*) are open questions on the map, not defects to
   absorb here.
3. **The enclosed void is handed to the acceptance bar**, not to the corpus. C6
   already discards an expired candidate with unassigned floor; it says nothing
   about an **OPTIMAL** candidate carrying a 1 m² unnamed hole, and after this
   ADR that gap is known rather than suspected.
4. **The lost façade is handed to H8.** 4.1 % of façade-facing rooms lose their
   frontage in conversion, so a Proposer trained on this corpus will sometimes
   propose an interior bedroom that the corpus did not contain.
5. **There is still no renderer on this map**, and `render_sheet.py` is a
   prototype that must not become one. It is the second time a ticket has needed
   to look at a plan and had to build the means first.
