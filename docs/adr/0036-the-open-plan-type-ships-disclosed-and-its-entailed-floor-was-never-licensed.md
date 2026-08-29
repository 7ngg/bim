# ADR 0036 — The open-plan type ships, disclosed rather than enforced, and its entailed floor was never licensed

**Status:** accepted. Amends [ADR 0034](0034-an-az-cell-declares-what-it-measures-and-a-part-may-only-floor.md)
decision 4 and consequence 2. ADR 0034's other decisions stand.

## Context

`living_dining_kitchen` is one of `brief.md` §3's nineteen Room types — the type a
Homeowner reaches by asking for a kitchen open to the living room, and per
`openings.md` §5 the *only* way to express that, because open plan is a merged
Room and never a deleted door leaf.

**A mandatory Azerbaijani norm bears on it.** AzDTN 2.13-1 cl. 8.31, read
first-hand from the PDF `arxkom.gov.az` serves, register `nəzərdə tutulmalıdır`:

> Yaşayış evlərində qaz pilətələrinin qoyulması nəfəslikli pəncərəsi, sorucu
> ventilyasiya kanalı və təbii işıqlandırılması olan, hündürlüyü 2,2 m-dən az
> olmayan **mətbəx otaqlarında** nəzərdə tutulmalıdır.

A gas hob must stand in a `mətbəx otağı`. AzDTN 2.7-3 cl. 4.7 files a
`mətbəx-yemək otağı` **inside** that word — *«mətbəx (o cümlədən mətbəx-yemək
otağı)»* — so `kitchen_dining` is gas-compliant and `living_dining_kitchen` is
not. MİDA hands its apartments over with a gas hob fitted. **The binding
constraint is the room's category, not its size**: at 2,7 m clear height cl.
8.31's 15 m³ rule is 5,6 m² of floor and never binds a real open-plan room, so
nothing the engine does to the geometry touches it.

### The evidence was misread, and the correction cuts both ways

`az-market-default-against-practice.md` §6.4 recorded *"In multi-room apartments?
**Never. 0 of 318**"*, and ADR 0034 consequence 3 repeated it as *"publishes zero
multi-room open-plan plans"*. Re-read against
`experiments/baku-market-areas/mida_plans_318.json` — in this repo when the
sentence was written:

| | |
|---|---|
| `Mətbəx-studio` plans | **5 of 318** (1,57 %) |
| …carrying a separate `Yataq otağı` | **5 of 5** |
| room schedule | `Dəhliz`, `Mətbəx-studio`, `Yataq otağı`, `Sanitar qovşağı`, `Eyvan` |
| internal area | 34,97 / 34,97 / 35,57 / 40,10 / 40,10 m² |
| the open-plan room | 15,14 / 15,14 / 17,37 / 17,70 / 17,74 m², **p50 17,37** |

They are **one-bedroom flats with an open-plan kitchen-living room**, not one-room
studios; `nrooms: 0` is MİDA's sales label. The original claim survives only under
the reading *"zero plans holding an open-plan room **and** a separate `Qonaq
otağı`"*, which is true and is the narrower fact.

So Baku practice **agrees** with cl. 8.31 in multi-otaq stock and **departs** from
it in exactly five one-bedroom flats. Both directions are real, which is why
neither a refusal nor an enforcement fits.

### And the hard floor this type carries was refusing all five

ADR 0034 decision 4 grants an entailed sum for *"cells whose disjointness **the
norm's own type definition** establishes"*, naming AzDTN 2.7-2's `ayrıca zonaları`
as the licence. It then applied that licence to `living_dining_kitchen` — whose
own `name_az` note in the same file says *"A compound with no norm equivalent —
AzDTN has no open-plan type"* — giving **15,0 + 6,0 = 21,0** at one otaq and
**16,0 + 6,0 = 22,0** at two or more. **The ADR states the rule and breaks it in
the same decision.** Neither the sum nor the underlying `part` read is licensed:
nothing in the norm entails that a room it has no word for contains a `qonaq otağı`
meeting cl. 5.7.

ADR 0034's own soundness rule for `part` is *"never rejects a room the law
admits"*. **All five MİDA open-plan rooms sit below both values**, by 3,3–5,9 m².
Consequence 1 quotes 17,37; consequence 2 posts 21,0 four paragraphs later.

The floor was also never reaching the warp. `experiments/warp/absolute_area.py`
has `LIVING_FAMILY = ("LIVING_ROOM", "LIVING_DINING")` and no open-plan limb, so
`floors_for` returns `None` for this type while `dim.statutory_min_area` demands
22,0 at site `both` — **ADR 0033's invariant has a hole on exactly this type**, and
no gate could see it because ADR 0034's four owed referent gates are still unwritten
(handed to ticket 69).

## Decision

1. **`living_dining_kitchen` ships in `AZ`.** The profile refuses no Room type.
   Refusing it would refuse the one open-plan dwelling the Baku state housing fund
   actually builds, and enforcing a fuel rule is the C8 breach outright.

2. **The consequence is disclosed in two channels, to two readers.**
   `brief.md` **§7.1** carries the Homeowner's half and names **both** ways out —
   an electric hob, or a `kitchen_dining` instead — because an architect asked
   this in Baku gives two answers. `annotation.md` **general note 9** carries the
   builder's half, emitted only where the Plan holds a Room of this type. This is
   ADR 0024's `what_belongs_in_this_block` distinction: two readers, two channels.

3. **It is not an Assumption, and no fourth kind is opened.** The Assumption set
   is `ResolvedBrief \ StatedBrief`, computed (`brief.md` §1). A **stated** type
   invents nothing and reinterprets no value of theirs, so none of §6's three
   kinds reaches it, and §6 closes the taxonomy at three. What this is, is a
   **consequence of what they asked for** — a different axis, and §7 already
   houses prose the engine must say and cannot model.

4. **`living_dining_kitchen`'s `az_area` becomes `null`.** Both `part` limbs and
   their `compose_with` are withdrawn as unlicensed. The hard floor falls to the
   ergonomic `min_area` **8,5 m²**, which all five MİDA rooms clear with margin.
   `null` is a state already defined and already occupied: `rules.json`
   `dim.statutory_min_area`'s `value_source` says *"A null `az_area` means NO
   STATUTORY FLOOR, not an error; ten of nineteen keys are silent in AZ"*. This
   row is the eleventh.

5. **`kitchen_dining` keeps its 6,0 limb, and gets its own `gas_note` saying it is
   compliant.** cl. 4.7 plus the definitions clause's `ayrıca zonaları` is exactly
   the norm-side type definition decision 4 requires, so the licence holds there.
   ADR 0034's refusal of "empty the limb" turned on *"information the law
   entails"* — for `kitchen_dining` the law entails it, for this type the law
   entails nothing. **Same licence, opposite results, and the difference is whether
   the norm has a word for the room.** The note exists because the absence of a
   note is unreadable when two types are one letter apart.

### Considered and refused

- **Refuse the type in `AZ`** — a Brief-scope refusal in §7's accessibility voice.
  Refused: it refuses five real Baku dwellings, and C14 says no profile may add a
  predicate.
- **`reachable_in_v1: false`** at the ergonomic layer, dropping it from v1
  entirely. Refused for the same reason plus a worse one: the flag is
  region-invariant, so a fact about Azerbaijani gas supply would remove a type
  everywhere.
- **Keep 21,0 / 22,0 and record the conflict.** Refused: a hard rule that rejects
  every real example of the type it governs is the defect ticket 71 describes for
  `kitchen_dining` — *"every real kitchen-diner rejected from above"* — which this
  map has already had to defuse once.
- **Open a fourth Assumption kind, `consequence`.** Refused: reopens a taxonomy
  §6 closed deliberately, and mislabels the thing — an Assumption is something
  *we* filled in.
- **Re-license the sum on physical disjointness** (a cooking zone and a living
  zone are obviously disjoint), stated as `engine_choice`. Refused: this is
  precisely the move ADR 0034 wrote the licence to forbid — an invented
  composition wearing a statutory cell's `conf: verified`, spending the property
  ADR 0027's market argument depends on.

## Consequences

1. **C14 is not weakened, and the argument matters more than the edit.** C14
   forbids a profile *lowering* a hard floor below the region-free base; the base
   is the ergonomic minimum and this returns to it. A raise posted on a read the
   licence does not grant was never a valid exercise of C14, so withdrawing it is
   a correction, not a weakening. ⚠️ **This is the first withdrawal of a profile
   raise on this map**, and the reasoning — not the precedent — is what a future
   ticket should reuse.

2. **The soft side does not move.** ADR 0034 already forbade a `part` read from
   feeding the soft tier, so the target was already `brief.md` §9.2 rung 2 and
   still is. The change is one-directional and touches only the hard floor.

3. **`gate_check.py` 238 → 235**, and the three are exactly V2's two
   key-exists gates plus one fallthrough gate on the removed guard entries. V4
   still passes because it accepts *"a soft target **or an explicit null**"*, and
   V5 because both living cells stay reachable through the `living` row and
   `kitchen_zone_in_diner` through `kitchen_dining`. No gate was silently lost.

4. **`compose_with` now licenses nothing on this file, and that is the correct
   state.** The two withdrawn limbs were the only non-empty ones. ADR 0034
   decision 4 stands as a rule; its only qualifying type has a single AZ-floored
   zone, so it is a no-op there by construction.

5. **Rung 2 for this type is Swiss and runs 2,1× the only AZ measurement of it.**
   36,5 m² composed against MİDA's p50 **17,37**. Recorded on the cell, **not
   fixed**: rung 2 is a corpus median and CH provenance is by construction (C14),
   while replacing it is a market-tier act owed to ADR 0035, which requires a
   published cost and may only move a cell up. n = 5 is thin. Owed by the next
   holder of the tier.

6. **Two hand-offs, and one is a hole in a shipped invariant.** `floors_for`
   posts no floor for this type while the bar demands one — ADR 0033's guarantee
   does not cover it, and after this ADR the two agree at *no AZ floor*, which is
   correct but coincidental and should be made deliberate. And ADR 0034's owed
   referent gates need a **fifth**: every `compose_with` traceable to a named norm
   type definition, which is the gate that would have caught this. Both to ticket
   69, which holds `experiments/region-profile/` and `experiments/warp/`.

7. **One sentence in `rules.json` is now false and this ADR may not fix it.**
   `dim.statutory_min_area`'s `value_source` reads *"Two AZ reads are `part`
   (kitchen_dining, living_dining_kitchen)"* — now one. `rules.json` is claimed by
   tickets 71 and 72, so per the map's concurrency rule the correction is handed
   on as prose rather than taken.

## Reversal trigger

Not a yield number and not market pressure. This ADR is refuted if **either**:

- **Azerbaijan publishes an area for an open-plan room** — an amendment to cl.
  5.7, or a norm naming the type. Then decision 4 is replaced by a transcription
  and the floor returns as a licensed raise. Decisions 1–3 survive, because they
  are about what the engine *says*, not what it *floors*.
- **cl. 8.31 is amended to admit a kitchen opened into a living room**, at which
  point decisions 2 and 5 are spent and note 9 is deleted. Decision 4 survives
  independently: the licence failed for a reason about the norm's vocabulary, not
  about gas.
