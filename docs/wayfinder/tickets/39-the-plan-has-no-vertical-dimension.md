---
id: 39
title: The Plan has no vertical dimension, and three artefacts already assume one
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - CONTEXT.md
  - data/standards/room-constraints.json
  - docs/spec/openings.md
  - docs/research/vertical-dimensions.md (new)
---

# The Plan has no vertical dimension, and three artefacts already assume one

## Question

**The geometry model has no Z.** `CONTEXT.md` defines a Wall as *"a centreline and
a thickness"* and an Opening by **three widths**. Nothing in the model says how
tall anything is. Grep for a ceiling height, storey height, room height or opening
head height across `room-constraints.json`, `acceptance-bar.md`, `brief.md` and
`CONTEXT.md` and **nothing comes back**.

Surfaced by *What IFC the engine actually emits*. It is not an IFC problem — IFC
is just the first consumer that cannot proceed without one. **Three artefacts
already assume a vertical dimension that nothing supplies:**

1. **`annotation.md`'s door schedule** ships a `Structural opening W × H` column,
   and its **window schedule** ships `Structural opening W × H` *and* `Sill
   height`. Three columns that cannot be filled from the model as it stands.
2. **`CONTEXT.md`'s Storey** — *"the level a Plan's geometry sits on… It exists
   because the model would otherwise have to invent it on export."* It exists for
   export and carries no height, so export still has to invent one.
3. **`ifc-export.md` §12** — every wall body is an extrusion, every `IfcSpace`
   needs a `Height` and `NetVolume`, every window a sill and every door a head.
   The spec names the four inputs and **refuses to default them**.

A real unowned component, of exactly the class the map's done-test exists to
catch: *Opening placement rules* writes `openings.md` and its body does not
mention height at all; nothing else is near it.

**This is one ticket, not two, and that is deliberate.** Finding the numbers and
deciding where they live cannot be split, because *where* a number lives changes
*which* number you need — a height on the Region profile is one value for the
dwelling, a height on the Opening catalogue is a value per door type, and a height
on the Wall is a per-instance field that only a model with parapets or dropped
ceilings can justify. Answer the model question and the research question in the
same session, in that order.

⚠️ **`writes:` collision, read before claiming.** This ticket touches `CONTEXT.md`
(shared with 21, 31), `room-constraints.json` (shared with 16, 31, 32) and
`openings.md` (**16's sole artifact**). It is the widest write-set on the map. The
`openings.md` overlap with *Opening placement rules* is the sharp one — see item 2.

**Decide:**

1. **What the model gains, and where.** At minimum `h_storey` (floor to floor) and
   `h_clear` (floor to ceiling) — and whether the difference is *modelled* (a slab
   plus a build-up, which is a second layer set and a second ADR 0010 problem) or
   whether the two are simply two published numbers with the gap left unexplained.
   Then the harder half: does a **Wall** gain a height field, or is height a
   property of the **Storey** that every Wall reads? v1 is single-storey with no
   dropped ceilings, so a per-Wall height has no user today — but ADR 0001's
   `load_bearing` hook is the precedent for paying for a field before its consumer
   exists, and that precedent was recently vindicated. Decide which case this is.

2. **Whether opening heights are catalogue or instance**, and settle the boundary
   with *Opening placement rules*. `CONTEXT.md` already says an Opening is
   **typed** from a regional catalogue *"rather than dimensioned freely"* — *"a
   door of an invented width is the clearest tell that a plan was generated"*. If
   width is catalogue, height almost certainly is too, and then the door head is a
   catalogue column and not a placement rule. **Sill height is the one that
   probably is not** — it varies by room and by what is outside. Draw the line and
   write it into `openings.md` so 16 inherits it rather than colliding with it.

3. **What the Azerbaijani source says**, read first-hand. **AzDTN 2.7-2** is the
   live residential design norm and the ticket-25 trap applies with full force: a
   number off **СНиП 2.08.01-89\***, whose legal force in Azerbaijan terminated
   2021-11-30, is folklore *and* repealed, and publishing it would be the exact C8
   breach ticket 25 existed to prevent. Baku sits in a climate sub-region and this
   norm family has historically varied minimum room height by one, so check
   whether AzDTN 2.7-2 does. `conf` flag per value like every other cell.

4. **Whether any of it is `hard`.** A minimum room height is the first plausible
   *statutory* vertical floor on this map. If AzDTN 2.7-2 publishes one, decide
   whether it reaches `rules.json` as a predicate or stays a profile value the
   engine simply obeys — noting there is **nothing for it to constrain**, because
   the solver is 2D and could not violate it. That may well be the answer: **a
   published value with no predicate**. Record it as a deliberate outcome rather
   than inventing a rule to give the number a home.

5. **Whether the ergonomic layer owes a height too.** ADR 0009's floor is
   region-invariant and derived from fixture footprints, all of them in plan. A
   *height* is not a fixture footprint, and every clearance in that source corpus
   turned out to be an accessibility figure. If no region-free ergonomic height is
   derivable, **say so** — an empty answer recorded is worth more than a borrowed
   one, and this layer has already refused one number it was handed.

6. **Whether the Brief may state a height.** C4 makes the Brief the real
   interface and its defaults ladder is `market_default` → corpus median →
   absent. The corpus rung is **dead here** — Swiss Dwellings and ResPlan are both
   2D and neither carries a height — so the ladder has two rungs, not three, for
   this field. Decide whether a Homeowner can ask for a high ceiling at all, and
   what the `Assumption` reads when they do not.

**Explicitly not this ticket:** multi-storey, stair alignment, or anything that
follows from more than one `IfcBuildingStorey`. C5 and the map's Out of scope
section already rule those out. Exactly one storey; this ticket gives it a height.

Deliverable: the vertical values in `room-constraints.json` with `conf` flags and
sources; the model decision in `CONTEXT.md`; the catalogue-versus-instance
boundary in `openings.md`; findings in `docs/research/vertical-dimensions.md`; and
a one-line statement of which of `annotation.md`'s three schedule columns each
value fills.
