# A corpus dwelling is converted by solving it, not by boxing its rooms

Every stage of this system places one rectangle per Room, and 51 % of real rooms
are not rectangles. The corpus must therefore be converted before the Proposer
can read it. We convert a dwelling by **running our own solver on it** — one
CP-SAT fit per dwelling, over the shipped 250 mm grid, with the real dwelling's
adjacencies and separation directions posted **hard** — rather than by choosing a
rectangle for each room independently.

A dwelling for which no such tiling exists is **not dropped** — it is recorded at
a lower **fidelity tier**. See Consequences 1 and 1a: the first draft of this ADR
dropped it, which was wrong, because every corpus dwelling is a real home and a
rule that deletes 31% of them is measuring our model rather than their data.

## Why not the obvious three

Measured over 42,986 Swiss Dwellings dwellings and 16,617 ResPlan plans
(`docs/research/rectangularisation.md`):

| conversion | adjacencies destroyed | separation relations | area error, mean |
|---|---:|---:|---:|
| bounding box | 0.000 /dwelling | **exactly preserved** | +11.1 % |
| largest inscribed rectangle | 2.697 /dwelling — **38 % of all** | 110,910 invented | −9.0 % |
| area-preserving rectangle | 1.699 /dwelling — **24 % of all** | 33,325 invented, 7,260 dropped | 0.0 % |

The two that hold or shrink area delete real adjacencies, because a room that
shrinks loses contacts, and they manufacture **confident-wrong** separation
assertions — the failure `CONTEXT.md` says costs a candidate outright.

The bounding box makes neither mistake: it contains its room, so no contact can
vanish, and a separation direction is a bounds test, so a bbox preserves the
relation *exactly, by construction*. Its failure is different and it is not
feasibility — a bbox transmits the true relations, so it cannot mislead the
solver. It is that **it hands over a target that is not a Plan**: its rectangles
collide in 86 % of dwellings (median 5.3 % of floor area, 99.3 % and 24 % on
ResPlan), and a pair overlapping on both axes **abstains** rather than asserting.
So the arrangement arrives with exactly the interesting pairs — the corridor
wrapping three rooms — silently dropped, and the solver invents that part of the
plan. Plus an 11 % mean area inflation that per-room target-area conditioning
would consume as fact.

## The construction

1. **Watershed.** Rasterise at 250 mm; each cell to the room containing its
   centre, wall cells to the nearest room. This splits every wall at its
   centreline, which is ADR 0001 performed discretely, so the conversion emits
   **centreline** rectangles whose areas include half of every surrounding wall.
   The clear area is the eroded rectangle, as always.
2. **Envelope.** Reduce to a bounding box minus at most two notches (ADR 0003),
   each notch the largest rectangle *inside* its complement component.
3. **Fit.** Hard: every asserted separation direction, every door-width
   adjacency, no overlap, per-room area within ±10 %. Soft: exact tiling.
   Objective: the count of 250 mm cells that end up in the wrong room.

Constraint structure copies the shipping solver on purpose — C10's amendment
posts relations hard and tiling soft — so this is `fix_relations` aimed at a real
dwelling instead of at a Proposal.

## Considered options

- **Bounding box, with the true polygon area carried alongside.** Rejected. It
  fixes the area complaint by making the converted room carry two numbers that
  disagree, and it does nothing about the target not being a tiling.
- **`bbox ∩ envelope`, per Graph2Plan's 93 %.** Rejected on measurement: it buys
  **1.3 points** on Swiss Dwellings and 1.0 on ResPlan, because the envelope
  explains only 2.3–2.8 % of real non-rectangularity. Rooms are concave because
  another *room* is there, not because the building outline cuts them. Adopting
  it would also emit L-shaped Spaces, reopening room-tag-at-centroid, the
  aspect-ratio predicate and ADR 0003.
- **Splitting a concave room into two rectangles.** Held out of scope *by ticket
  22*, on the grounds that it breaks the one-box-per-Room contract. ⚠️ **That
  scoping is now itself under review** — an L-shaped room is *orthogonal*, so it
  never belonged in the *Non-orthogonal geometry* fog, and only **2.7 %** of real
  dwellings have every room a rectangle. See *Whether a Room may be more than one
  rectangle*. If it goes ahead, this ADR's construction survives — the fit places
  1–2 boxes per Room instead of 1 — but every figure in it is re-measured.
- **Minimising L1 corner displacement**, the shipped objective. Rejected on
  measurement, and this one is a trap worth naming: among exact tilings it is
  nearly uncorrelated with how much of the dwelling lands in the right room —
  **IoU median 0.14 against 0.82**. Projection and fitting are different
  problems and sharing the machinery hides it.
- **Posting the relations soft, or only between neighbours.** Rejected. Soft
  relations convert 90 % against 77.5 %, and **flip 2 % of pairs outright** —
  truth says the kitchen is left of the hall, the tiling puts it right of it.
  Neighbours-only converts 82 %. Fidelity is the reason this conversion exists.

## Consequences

1. **The model expresses 69 % of Swiss Dwellings and 60 % of ResPlan exactly**,
   and the shortfall is
   concentrated where it hurts: conversion falls from 83 % at 4 rooms to 46 % at
   10, while fidelity stays flat at 0.86–0.92. *What the model proposes*'
   retrieval coverage figures were measured before this conversion and **no
   longer hold**; they must be re-measured on the converted index.
1a. **A dwelling below tier A is kept, not deleted.** The ladder is A exact
   (0.7360) / B neighbour-relations only (0.8200) / C relations soft (0.9375) /
   D adjacency soft (1.0000). **Retrieval admits tier A only**, because its claim
   is that someone lived in *this* arrangement and a tier-B dwelling makes that
   claim falsely. **Training takes every dwelling** at its best tier, with the
   tier as a conditioning field — a model learns from an approximate example and
   cannot learn from a deleted one, and deleting them was silently teaching the
   Proposer that homes are smaller than they are (dropped dwellings ran 8 rooms
   and 89.9 m² against 6 and 71.7).
2. **This is affordable only because of ADR 0005.** A smaller retrieval index
   shifts Briefs to the trained model, which always answers, rather than refusing
   them. With one source it would be a coverage cut.
3. **What survives, survives exactly.** Zero adjacencies destroyed in 22,688
   edges across both corpora; zero flipped and zero weakened separation
   directions. The only relations the conversion adds are on pairs the truth
   abstained on, where a rectangle model must pick a side.
4. **The tier is decidable, not a timeout.** Every Swiss dwelling resolved to
   proven-optimal or proven-infeasible within 10 s — median 0.44 s, p95 1.50 s,
   **zero UNKNOWN**. A dwelling's tier is therefore a fact about the dwelling and
   our model, never an artefact of the time limit.
5. **Preparing the corpus costs about a second per dwelling** — ~17 CPU-hours for
   both corpora, once, offline, and parallel. It also needs a driver that
   survives an OR-Tools `CHECK` abort, which happened once in 1,000 ResPlan plans
   and cannot be caught in Python.
6. **±10 % per-room area is an ENGINE_CHOICE, and it is the loosest of the three
   hard families to justify.** Relaxing it recovers 17.6 points. It is kept
   because the stated warp budget is ±10 %, and a corpus looser than the gate it
   feeds cannot be checked against that gate — but the trade belongs to *The
   retrieval index and warp procedure*.
7. **Raising ADR 0003's notch cap makes conversion worse, not better** — 66.8 %
   at four notches against 73.6 % at two. A more articulated Envelope is harder
   to tile with *n* rectangles. The cap is now evidenced, and in the direction
   opposite to the one the map suspected.
