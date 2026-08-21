# A Space is bounded by finished faces, and a wall thickness is a layer set

**Status:** accepted
**Date:** 2026-08-21
**Ticket:** *Area measurement convention*
**Amends:** [ADR 0004](0004-published-dimensions-measure-wall-faces.md) — deletes
its one centreline exception
**Related:** [ADR 0001](0001-centreline-walls-over-a-dilated-solve-domain.md),
[ADR 0003](0003-the-envelope-is-an-inner-face-ring-of-typed-edges.md),
[ADR 0006](0006-one-shipping-profile-and-it-is-not-the-corpus-region.md),
[ADR 0007](0007-published-minima-must-erode-onto-the-solve-grid.md),
[ADR 0009](0009-a-derived-minimum-is-not-rounded-onto-the-solve-grid.md)

## Decision

A **Wall's thickness is a layer set**, not a scalar: an ordered list of
`(material, thickness)` summing to a **total**. The total is the only number the
solver, `erode` and every dimension consume. The structural leaf survives as data
and is consumed by nothing in v1.

The plane that bounds a **Space** is the **innermost finish face**. `clear =
erode(solved, t_int/2)` is unchanged in form; `t_int` now means the **total**.

For `AZ`, shipping:

| | was | now | note |
|---|---|---|---|
| `t_int` | 120 | **150** | 120 half-brick + 2 × 15 finish |
| `t_party` | 250 | **280** | 250 one-brick + 15 ours + 15 theirs |
| `t_ext_total` | 500 | **500** | unchanged — its 20 mm finish was always counted |

The measured area is `ümumi sahə` per **Area Qaydalar cl. 3.8**, measured per
**cl. 3.2** — *between the finished surfaces of walls and partitions, at floor
level, skirtings excluded*. It is the **sum of Space areas**, and it does not
count partitions.

## Why the model had to grow a layer, and could not just be relabelled

Four documents — `CONTEXT.md`, the ergonomic layer's own `reading`, ADR 0004, and
`annotation.md` general notes 2 and 5 — assert that every published dimension and
area measures **finished** faces. `annotation.md` §5 says in the same breath that
there is **no finishes model**. ADR 0001 eroded `t_int/2` from a centreline and
`t_int` was `120`, *"half-brick bare masonry"*. Every "finished" number in this
system was a structural number wearing the word.

Relabelling — publishing "structural clear" and correcting the prose — was the
cheap repair and it is refuted by arithmetic, not by taste:

- `bathroom.min_clear_long` is **1700**, derived as *"bath 1700 long"*. At 15 mm
  of finish per face the delivered clear is **1670**. **The bath does not fit
  inside its own minimum.**
- `wc.min_clear_short` is **800** = pan 500 + body **300**. Finished, it delivers
  270. The 300 mm body zone is the single calibrated constant behind the entire
  ergonomic layer (ADR 0009); a floor that quietly spends 10% of it is not a
  floor.

The ergonomic layer is composed from **physical fixture footprints**. A bath is
1700 mm of enamel. Checking it against a rectangle measured to bare masonry
compares the fixture against a room that will not exist. That is C2's failure
mode exactly — a plan that validates and cannot be built.

## Why a layer set rather than one fattened number

Folding the finish into a single `t_int = 150` gives the same geometry for less
structure, and it was rejected. Three things need the split:

- **The profile's own acoustics already assume it.** `t_party = 250` was derived
  from *"brick 250 + 15 plaster both sides = 52 dB"* against AzDTN 2.7-2's 50 dB;
  *"brick 120 + 15 both sides = 49 dB"* fails. The finish is already load-bearing
  in a shipped number. Erasing it makes that derivation unreadable.
- **IFC wants it.** `IfcWallStandardCase` carries `IfcMaterialLayerSetUsage`.
  Emitting a 150 mm homogeneous wall where a real one has three layers is the
  file that opens and gets thrown away — the thing C2 exists to prevent.
- **The deferred structural patch is paid for, not merely promised.** A Wall's
  `load_bearing` is already *unknown, not false*. Keeping the structural leaf
  costs one field and means the structural question has a number waiting for it.

Every competent BIM authoring tool models this as layers and computes room area
to a **named** plane — Revit's room boundary is selectable between wall finish,
wall centre, core layer and core centre, and it defaults to finish. We are not
inventing a convention; we are catching up to the one the market shipped.

## Why the centreline exception dies

ADR 0004 kept exactly one centreline number: tier 1 measures a party edge **to
its centreline**, *"because GIA and IPMS both do"*, and §4 committed it to follow
this ticket. `ümumi sahə` does not do what GIA does — it stops at the finished
inner face, and it excludes partitions where GIA includes them. The authority for
the exception is gone.

It was also always in tension with ADR 0004's own thesis, that *"every tick is a
number a person can tape"*. **A party wall's centreline cannot be taped from
inside the flat.** Tier 1 now measures the Envelope's inner ring on every edge,
exterior and party alike. The sheet carries **no centreline dimension anywhere**,
and `DIM-CONV` loses its second clause.

## Consequences

1. **`t_int` is 150, and the ADR 0007 residue class moves from 130 to 100
   `(mod 250)`.** Moot for `AZ`, which publishes no hard linear minimum — cl. 5.6
   delegates every intra-apartment clear dimension to the ergonomic layer, which
   ADR 0009 exempts. Owed before a second profile publishes one.
   `experiments/region-profile/gate_check.py` was re-run: **33 gates, all pass**
   (was 28).
2. **ADR 0004's even-thickness rule is sharpened, and it had to be.** It binds on
   the numbers that get **halved** — the totals, because `erode` needs `t_int/2`
   — and **not on a layer component**, which only ever enters a total *doubled*.
   `120 + 2 · 15 = 150` is even for any integer finish. **A 15 mm finish is legal
   and a 15 mm wall is not.** Without this the gate rejects its own data, and the
   rejection would be arithmetically meaningless. The gate now also asserts the
   layer sum closes: `t_int == t_int_structural + 2 · t_finish`.
3. **Ticket 19's room-count deletion analysis is re-owed.** Its finding — the
   4/5/6-room deletion narrows to *{5, and 6 unknown}*, so 250 mm charges the
   5-room case — was computed at `t_int = 120`. It must be recomputed at 150.
   Direction is not obvious and must not be guessed: this is filed as a
   correction, not a reassurance.
4. **The total-area gate changes quantity, not just width.** It gated on GIA,
   which counts partitions; `ümumi sahə` does not. On a 90 m² dwelling the
   partition footprint is roughly **4–5%** — the width of the 5% gate itself. See
   `acceptance-bar.md` §8.
5. **The finish constant is `engine_choice` and is the weakest number here.**
   15 mm is not read from any Azerbaijani document. It is corroborated only by
   being the value the shipped `t_party` derivation already assumes. Owed by
   *What an Azerbaijani finish layer actually is*.
6. **The drawing gets easier, and that is a side effect and never the reason.**
   ADR 0004's collision complaint was a `t_int` tick of 2 mm of paper at 1:50
   against 2.5 mm of text. At 150 mm the tick is 3 mm. Fewer leaders. Had the
   arithmetic pointed the other way the decision would be unchanged. ADR 0004
   still says `t_int` is 100 mm — it was written before any profile shipped one,
   and 100 was already wrong at 120. The shipped number is the profile's, not the
   ADR's; the prose there is not re-edited because *The annotation spec is
   US-shaped* is rewriting that section anyway.
7. **The Envelope's definition is sharpened, not moved.** `CONTEXT.md` already
   said *"a Homeowner's tape measurement of their flat is the Envelope with
   nothing added or removed."* A tape reads finish. The Envelope was always the
   finished inner face; only `t_int` disagreed.
