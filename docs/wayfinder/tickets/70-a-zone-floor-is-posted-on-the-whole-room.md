---
id: 70
title: A zone floor is posted on the whole room
parent: map
labels: [wayfinder:grilling]
status: closed
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

## Resolution

**Kept at 6,0 and reclassified. The referent is now typed data, a part may floor
but never target, and the norm's ordering is carried by the target.**
[ADR 0034](../../adr/0034-an-az-cell-declares-what-it-measures-and-a-part-may-only-floor.md).

### The ticket's own framing was half wrong, and correcting it inverted option 1

This ticket said the engine *"hard-refuses candidates against a floor no
regulator wrote"*. It does not. Every legal `mətbəx-yemək otağı` holds a kitchen
zone of at least 6 m², so `area(Room) ≥ area(zone) ≥ 6,0` and the posted floor
refuses a **strict subset** of what the law refuses. **Zero false refusals.** The
defect is that the bound is **loose**, and that the same number leaks into the
soft tier where it is ~4× low.

So **option 1 is refused as strictly worse than the status quo**: emptying the
limb discards a bound the law entails and drops the room to the ergonomic
**4,6 m²**, *below* even the zone figure.

### Two research tickets were fired and both changed the answer

**[The kitchen-diner's whole-room floor](../../research/az-kitchen-diner-whole-room.md).**
No instrument with force in Azerbaijan publishes a whole-room area for this
type — swept AzDTN 2.7-1 … 2.7-11; the two mixed-use norms defer back to 2.7-2;
**no dining-zone figure exists either**, which kills the tidiest derivation.
2.7-2 is unamended, proved by byte-identity and by the asterisk convention.

It also **sharpened the defect past this ticket's statement**. AzDTN's ladder is
about *eating*: `taxça-mətbəx` no eating area → 5, `mətbəx` eating unzoned → 8,
`mətbəx-yemək otağı` eating in its own zone → **zone** 6. The 6 is a relaxation
of the *cooking part*, granted because the table moved out of it. **The
kitchen-diner is the larger room with the smaller kitchen part**, so posting 6,0
on the room **inverts the norm's own ordering** — flooring the zoned room 2,0 m²
below its unzoned equivalent. Three candidate whole-room numbers exist and do
not converge — **8,0** taxonomic, **7,9** zone-plus-ergonomic, **12,0** Kazakh —
and *none is a transcription; none may be labelled statutory.*

**[market_default against Baku practice](../../research/az-market-default-against-practice.md).**
**MİDA does publish per-room areas** — the site is a React shell, so every prior
attempt fetched the shell; its bundle calls an undocumented JSON endpoint
returning the full *eksplikasiya*. 318 Baku plan geometries, room areas summing
to `internal_size` to the cent, so the plane is net internal (ADR 0010).

### What was decided

| | |
|---|---|
| `kitchen_dining` hard floor | **6,0 unchanged**, now `referent: part` — entailed by containment, the only deductively sound value in the band |
| the ordering inversion | **left in the hard set and recorded**, carried by the target instead |
| `kitchen_dining` target | 6,0 → **18,8** at rung 2 |
| `living_dining_kitchen` hard floor | 16,0 → **21,0 / 22,0** (`15,0 or 16,0 + 6,0`, disjoint by «ayrıca zonaları») |
| `living_dining_kitchen` target | 16,0 → **36,5** composed |
| `living_dining` | `referent: undetermined`, **behaviour unchanged** |
| a zone in the geometry model | **refused** |

**Why 6,0 and not 8,0**, since 8,0 removes the inversion and costs no yield: the
statutory tier is 13 cells for 13 `conf: verified`, and that integrity *is*
ADR 0027's market argument. 8,0 needs a premise the norm never states, so it is
`engine_choice`, and putting one into a hard set whose whole defence is
transcription spends the property the argument depends on. A floor is not what a
room is sized to — `CONTEXT.md` says so — and the target lands at 18,8, above all
three candidates. **8,0 was not refused for costing yield; it costs none.**

⚠️ **Residual, stated not buried.** A Homeowner who *states* 6,5 m² clears
`brief.md` §9.4 bound 1. That is *a stated target is sovereign* working as
designed, and it is the price of holding the tier to transcription.

### A figure this map nearly shipped is disqualified

The direct Swiss `KITCHEN_DINING` median **23,67 must not be used**: **39 of its
41 rooms sit in dwellings that also carry a separate `KITCHEN`**, so the label is
a **dining room**. It is also **21 layouts, not 41 rooms** — one site is 4
layouts × 6 floors and the per-unit key hashes differ, so a key-based dedup
cannot see it. Both verified here against `out/dwelling_rooms.json`.

**18,8** is `KITCHEN + DINING` per dwelling over 1 308 dwellings, trusted because
**MİDA's `Mətbəx-studio` is 17,37** over 5 Baku plans. Neither is literally a
`mətbəx-yemək otağı`; **the agreement at ≈18 is the evidence, not either alone.**
⚠️ The *"composition under-predicts by 22 %"* correction is **void** — calibrated
against the disqualified 23,67.

`LIVING_DINING` was checked the same way and is **clean**: 0,1 % also carry a
`LIVING_ROOM`, 0,7 % a `DINING`.

### A mandatory gas rule explains the empty corpus

AzDTN 2.13-1 cl. 8.31 requires a gas hob to stand in a `mətbəx otağı`, and 2.7-3
cl. 4.7 files the kitchen-diner *inside* the word kitchen — so a
kitchen-**diner** is gas-compliant and a kitchen-**living** room is not. MİDA
fits gas hobs and publishes **zero** multi-room open-plan plans in 318
geometries. **Recorded, not enforced** — C8, and the same refusal this map
already made for cl. 5.10 at `bathroom_combined`.

### Written

- `data/standards/room-constraints.json` — `mapping.referent_model`; `referent`
  + `compose_with` on all **15** `az_area` guard entries across 12 rows (**10 room,
  3 part, 2 undetermined** — an otaq-guarded row has two limbs and each is a
  separate read); rung-2 medians for both compound types; the `kitchen_dining`
  bridge rewritten; the LDK `gas_note`; **six** `clear_widths_mm` cells corrected
  from `cl. 5.4` to `cl. 5.1` (values unchanged — cl. 5.4 is foundations).
- `CONTEXT.md` — **Statutory floor** gains the part-referent clause and two
  `_Avoid_`s. **Hard area floor stays two limbs.**
- `data/acceptance/rules.json` — declared on resolution, **prose only**:
  `dim.statutory_min_area.value_source` and `dim.market_default_area.note`.
  `area_bands` deliberately untouched.
- ADR 0034 new; ADR 0033 amended.
- 238 `gate_check` and 233 `ergonomic_check` gates pass.

### Handed on

- **68** — `acceptance-bar.md` §11.1's text, which this does not hold.
- **69** — the gate family: every guard entry carries a `referent`; every
  `compose_with` key exists and is `verified`; no `part` read is reachable from a
  soft-tier resolution; and **every `part` read has a target**, which is the
  load-bearing one, because ADR 0034 leaves the ordering to the target. Plus
  `MARKET["KITCHEN_DINING"]` 6,0 → **18,8**, and an **eighth hand copy**:
  `fit_warp.MIN_SIDE` has no `KITCHEN_DINING` and falls to `MIN_SIDE_DEFAULT = 5`
  where the ergonomic 1300 mm gives 6.
- **71** the `area_bands` class mapping, **72** the AzDTN 2:1 aspect cap,
  **73** the MİDA re-read of the whole `market_default` tier.

### Not done, deliberately

`STAT_FLOOR` does not move, so `experiments/warp/` is untouched and its four
tickets are undisturbed. The `market_default` tier was not re-read against MİDA
— that is 73, and one cell is already known to contradict it
(`bathroom_combined` 3,8 against 63,5 % of Baku bathrooms being smaller).

⚠️ **Process note.** Both research agents shared one working tree and the first
one's commit landed on the second's branch. Nothing was lost and no history was
rewritten, but two parallel `research/*` agents need separate worktrees, not
separate branch names.
