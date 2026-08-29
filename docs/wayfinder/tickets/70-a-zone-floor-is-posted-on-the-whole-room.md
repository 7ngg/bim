---
id: 70
title: A zone floor is posted on the whole room
parent: map
labels: [wayfinder:grilling]
status: open
assignee: tng
blocked_by: []
writes:
  - docs/adr/0033-the-warp-posts-the-statutory-floor-and-pays-adr-0027s-debt.md
  - data/standards/room-constraints.json
  - CONTEXT.md
---

# A zone floor is posted on the whole room

## Question

**AzDTN 2.7-2 cl. 5.7's 6 m² floors the kitchen *zone inside* a
mətbəx-yemək otağı, and `absolute_area.STAT_FLOOR["KITCHEN_DINING"]` carries it
as a whole-Room floor that ADR 0033 posts HARD.** The clause reads *«mətbəx-yemək
otağında **mətbəx zonası** — 6 m²-dən»*. `floors_for` returns 6,0 for the type
and `constrained_warp.py:157` posts it as `area >= area_floor_cells[r]` on the
Room.

**The profile already records the defect, verbatim, and nothing read it.**
`profiles.AZ.rooms.mapping.rooms.kitchen_dining.bridge`:

> THE AZ CELL CONSTRAINS A ZONE, NOT THE ROOM. cl. 5.7's 6 m² is the `mətbəx
> zonası` INSIDE the mətbəx-yemək otağı, not the whole room, while the ergonomic
> 4.6 m² floor is the whole room. So the AZ number is a **soft target** for a
> PART of what the ergonomic key measures, and reading it as a room target
> under-targets the room. Flagged rather than fixed: correcting it means either a
> zone concept the geometry model does not have, or a re-derivation, and ticket
> 31 is a vocabulary ticket. Handed to `rules.json`'s holder.

**Two independent drifts ride on one value.** The **referent** moved — a zone
read as a room — and the **force** moved: the profile calls it a *soft target*
and ADR 0033 posts it in the hard set. Either alone would be a defect; together
they mean the engine hard-refuses candidates against a floor no regulator wrote,
which is the C8 failure ADR 0027 says the hard set exists to prevent, in the
lenient direction rather than the strict one.

**The direction is under-constraint, and its size is unknown.** The law wants the
zone at 6,0, so the room it sits in is necessarily larger than 6,0 by whatever
the dining part takes — a quantity AzDTN leaves **unstated**. The posted 6,0 does
bind above the ergonomic whole-room 4,6, so the engine is stricter than
ergonomics and more lenient than the law, and no number on this map says by how
much.

⚠️ **This is not the SNiP folklore number surviving in a second slot.** The
hypothesis was tested and contradicted, not merely unproven: three instruments
carry the zone rule and SNiP 2.08.01-89\* has **no zone rule at all** —
`docs/research/az-statutory-floor-transcription.md`.

⚠️ **Reading the JSON does not fix this, so ticket 69's binding does not close
it.** The correct cell is being read; all six statutory values transcribe their
clause exactly. What drifted is the qualifier the cell is stated under, and it
lives in a prose `bridge` field no assertion will ever reach. This is the
**referent** failure mode, and a guard that reads `statutory_floor.v` and stops
is aimed at the one that did not occur.

⚠️ **It has been unowned since *Two room vocabularies in one file* closed.**
The bridge hands it to `rules.json`'s holder; nothing on this map recorded the
handoff, and the phrase appears **nowhere** on it. That is the state the
component table's done-test exists to catch, and it was caught by an audit rather
than by the table.

**Three candidate resolutions, and they are not equivalent:**

1. **Post no statutory floor for `KITCHEN_DINING`.** The type falls back to the
   ergonomic 4,6, `az_area` is honestly emptied, and the engine stops claiming a
   statutory floor it cannot state. Cheapest and the most honest about what is
   known — and it discards a floor the law genuinely does state, which is a real
   loss on the one region where `statutory_floor` has a live consumer.
2. **Derive a whole-room floor** as the zone plus a dining allowance, from the
   corpus or from the ergonomic dining minimum. Keeps a statutory claim and
   quantifies what the law left open — ⚠️ **and quantifying it is an engine
   choice about a legal minimum**, which ADR 0023 refuses in the opposite
   direction. Whatever comes out is ours, not AzDTN's, and must be labelled so.
3. **Give the model a zone.** A sub-region of one Room, constrained
   independently. ADR 0014 caps a Room at two rectangles and the vocabulary has
   no term below Room, so this is the deep option the bridge means by *"a zone
   concept the geometry model does not have"*. It also reaches `counts_as_otaq`,
   which is `false` for this type while both its parts are habitable.

⚠️ **ADR 0027 binds the choice.** A statutory floor is a product position and is
not tradeable for yield, so none of the three may be chosen for the INFEASIBLE it
buys — the yield each costs is a consequence to record, never the argument.

⚠️ **Do not touch `experiments/warp/`.** Four tickets already claim it (62, 65,
67, 69) and this one is deliberately kept off it. If the decision moves
`STAT_FLOOR["KITCHEN_DINING"]`, the constant is **handed** to whichever ticket
re-measures the floor arms, with the new value and its derivation stated here.

## Raised by

*az-statutory-floor-transcription* (2026-08-29), finding 1 —
`docs/research/az-statutory-floor-transcription.md`.
