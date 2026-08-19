# Published dimensions measure wall faces, never centrelines

Every dimension that reaches a human measures **wall faces** — the clear
quantity, between finished faces. The model stores centrelines and the solver
works in them, and neither number ever appears on a drawing. The single exception
is tier 1, which spans the footprint and measures **to the centreline of a party
wall**, because a party wall's outer face lies inside the neighbour's home.

## The trade-off, which is real and goes the other way

A face-based chain alternates: room clear width, wall thickness, room clear
width. It closes exactly on the Envelope inner dimension, and every tick is a
number a person can tape.

But the wall-thickness tick is `t_int` — 100 mm, which at 1:50 is **2 mm of paper
against 2.5 mm of text**. Every one of them collides. A five-room flat has four.

Centreline chains have no such tick: measuring axis to axis produces evenly-sized
segments and no collision at all. **That is why the convention exists**, and a
CAD-literate reader will reach for it first. We are rejecting the easier
formulation.

## Why faces win anyway

- **The Acceptance bar is stated in clear dimensions.** So is the ergonomic
  minimum, so is every minimum room dimension in the standards corpus, and so is
  a Homeowner's tape. A drawing dimensioned in centrelines cannot be checked
  against the bar that produced it without arithmetic on every number.
- **A centreline dimension labelled as a room size is wrong by `t_int`** — 100 mm
  on every room, every axis. The glossary already names this as *the* way a clear
  dimension gets confused with a centreline one, and putting centrelines on the
  sheet is the mechanism by which it would happen.
- **The collision has a deterministic fix.** If a segment's paper span is under
  the text width, the text goes outside with a leader; two consecutive outside
  texts alternate above and below. Arithmetic, computed before anything is drawn,
  no search. The cost is leader lines — ink, not correctness.

Trading correctness for ink is not a trade we get to make. C2 holds the engine to
a Practitioner's standard, and a Practitioner reads the ticks *because* they are
the room sizes.

## Consequences

1. **Every wall thickness in a region profile must be an even number of
   millimetres.** ADR 0001 needs `erode(rect, t_int/2)` in integer millimetres,
   and tier 1 needs `t_party/2`. 100 / 120 / 140 / 200 / 240 / 300 are fine;
   **115 mm (half-brick) and 125 mm (DIN 4172 octametric, and a common UK
   blockwork-plus-plaster build-up) are not** — they put every wall face on a
   half-millimetre and every clear dimension off-integer. This is a hard
   constraint on *Which region profiles ship in v1*, and it was found here rather
   than there.
2. **Leaders are a normal part of the output, not a failure.** Roughly one per
   internal wall per chained side. A reviewer seeing them should not "fix" them.
3. **The one centreline number is declared on the sheet.** The title block's
   `DIM-CONV` attribute states the convention in words, because a mixed-convention
   overall that does not say so is worse than either convention alone.
4. **Tier 1 couples to the area convention.** GIA and IPMS both measure party
   walls to centreline, which is why tier 1 does. If *Area measurement convention*
   lands somewhere else, tier 1 follows it rather than keeping its own rule — one
   drawing must not quote a footprint on one convention and an area on another.
