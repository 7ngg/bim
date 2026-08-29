# ADR 0034 — A profile cell declares what it measures, and a part may floor but never target

Status: **accepted** · 2026-08-30 ·
[A zone floor is posted on the whole room](../wayfinder/tickets/70-a-zone-floor-is-posted-on-the-whole-room.md)

## Context

`absolute_area.STAT_FLOOR["KITCHEN_DINING"] = 6.0` and `MARKET["KITCHEN_DINING"]
= 6.0` both resolve, through `profiles.AZ.rooms.mapping`, to a cell named
`kitchen_zone_in_diner`. AzDTN 2.7-2 cl. 5.7 reads *«mətbəx-yemək otağında
**mətbəx zonası** — 6 m²-dən»*: the floor is on the **zone inside** the room.
ADR 0033 then posts that number as a hard per-Room constraint in the warp.

**The profile already recorded the defect, verbatim, in two prose fields, and
nothing read them.** `az-statutory-floor-transcription.md` §11 is the finding
that matters here: *"No automated check will ever read those."* The number was
copied past its qualifier, and the qualifier had nowhere to live but English.

Two drifts rode on one value. The **referent** moved — a zone read as a room —
and the **force** moved: the profile called it a *soft target* and ADR 0033 put
it in the hard set.

### The ticket's framing was half right, and the correction matters

The ticket said the engine *"hard-refuses candidates against a floor no
regulator wrote"*. That is not what happens. Every legal `mətbəx-yemək otağı`
contains a kitchen zone of at least 6 m², so `area(Room) ≥ area(zone) ≥ 6.0`:
the posted floor refuses a **strict subset** of what the law refuses. **There
are no false refusals.** The defect is not that the constraint is wrong; it is
that it is **loose**, and that the same number leaks into the soft tier where it
is roughly four times low.

That inverts the ticket's option 1. Emptying the limb does not make the engine
honest — it discards a bound the law entails and drops the room to the
**ergonomic 4,6 m²**, which is *below* even the zone figure.

### And the norm's ladder makes the looseness worse than "unquantified"

AzDTN 2.7-2's definitions clause distinguishes three kitchen forms by **where
food is eaten**, not by size:

| type | eating | floor |
|---|---|---|
| `taxça-mətbəx` | **no** eating area | 5 m² |
| `mətbəx` — *«kulinariya və qida qəbulu üçün nəzərdə tutulmuş otaq»* | eating, **unzoned** | 8 m² |
| `mətbəx-yemək otağı` — *«…**ayrıca zonaları** olan otaq»* | eating, in its **own zone** | **kitchen zone** 6 m² |

Read down that ladder the 6 stops being puzzling: a `mətbəx` must hold both jobs
in one undifferentiated room, so the norm floors it at 8; a `mətbəx-yemək otağı`
has pulled eating into a zone of its own, so the norm lets the **cooking zone**
fall to 6 *because it no longer has to hold the table*. **The kitchen-diner is
the larger room with the smaller kitchen part.**

So posting 6,0 on the whole Room does not merely under-constrain by an unknown
margin — it **inverts the norm's own ordering**, flooring the zoned room
**2,0 m² below its unzoned equivalent**.

### What Azerbaijan publishes, established exhaustively

`az-kitchen-diner-whole-room.md`: **no instrument with force in Azerbaijan
publishes a whole-room area for this type.** The term occurs twice in AzDTN
2.7-2 and twice in 2.7-3, never with a room figure; all nine other norms in the
2.7 family through 2.7-11 were swept and return zero; the two mixed-use norms
that could have restated a dwelling schedule defer back to 2.7-2. **There is no
dining-zone figure either**, which kills the tidiest derivation. AzDTN 2.7-2 is
unamended, proved by byte-identity with the served PDF and by the asterisk
convention its own siblings apply to amended norms.

Three routes to a whole-room number exist and **they do not converge**: **8,0**
from the taxonomy above, **7,9** from zone-plus-ergonomic-dining, **12,0** from
СП РК 3.02-101-2012, the one regional norm that floors the dining zone too. The
first two share no inputs and land 0,1 apart; the third is a comfort judgement
on a more generous schedule throughout. **None is a transcription and none may
be labelled statutory.**

## Decision

**A profile cell declares what it measures relative to the ergonomic key that
reads it. Where it measures a proper part, its value is a sound lower bound: it
may floor, and it may never target.**

Five parts.

1. **`referent` on the `az_area` guard entry**, taking `room`, `part` or
   `undetermined`. **On the entry, not on the cell** — `living_room_2plus` is
   read by three rows with three different answers (`living` room,
   `living_dining` undetermined, `living_dining_kitchen` part), so the referent
   is a property of the *read*. It sits beside the `when_otaq_count` it is
   conditioned with, and each guard limb carries its own. At authoring: **15 guard entries
   across 12 rows — 10 `room`, 3 `part`, 2 `undetermined`.** Entries and rows differ
   because an otaq-guarded row has two limbs and each limb is a separate read.

2. **A `part` read may feed the hard tier and may never feed the soft tier.**
   Sound because the room contains the part; refused as a target because a
   bound that is merely entailed is not what anyone builds. This is the whole
   rule, and it is what turns two prose `bridge` fields into something a gate
   can check.

3. **`undetermined` changes nothing.** It is a marker. `living_dining` reads
   the `ümumi otaq` cell and AzDTN never defines `ümumi otaq` or says whether
   eating happens there — cl. 5.5 enumerates habitable rooms as *(otaq, qonaq
   otağı, yataq otağı)* and stops. Deliberately **fail-open**: the alternative
   moves a shipped target on a type with 24 122 corpus rooms as a side effect of
   a labelling change, which is the opposite of what a marker is for.

4. **An entailed bound may sum verified cells whose disjointness the norm's own
   type definition establishes**, and nothing else. `«ayrıca zonaları»` —
   separate zones — is what licenses a sum. It is a **no-op for
   `kitchen_dining`**, whose only AZ-floored zone is the kitchen, and it moves
   exactly one row: `living_dining_kitchen` to **15,0 + 6,0 = 21,0** at one otaq
   and **16,0 + 6,0 = 22,0** at two or more. Verified cells only; an entailed
   bound never sums a derived or fitted one.

5. **`kitchen_dining`'s hard floor stays 6,0, and the ordering is carried by the
   target, not by the reject set.** The inversion in §Context is left standing
   in the hard set, on purpose, and the reasoning is the point of this ADR:

   - 6,0 is the **only deductively sound value** in the band. 8,0 needs the
     premise that separating zones never reduces required area — very plausible,
     and a judgement the norm does not make.
   - The statutory tier is **13 cells for 13 `conf: verified`**. Its integrity
     *is* ADR 0027's market argument — *"transcribed first-hand, `conf:
     verified`, and enforced on the polygon"* is the thing eleven surveyed
     competitors do not have. Putting an `engine_choice` number into it spends
     exactly the property the argument depends on.
   - A hard floor is not what a room is sized to. `CONTEXT.md`'s **Hard area
     floor** says so outright: *"do not reach for it as the number a room is
     sized to… the liveable number is the Region profile's preferred area."*
     The inversion compares two backstops, and the target lands at **18,8** —
     above all three candidate floors.

   ⚠️ **This is not the ADR 0027 argument being smuggled back.** 8,0 was not
   refused for costing yield; it costs none — no corpus kitchen-diner is near
   any of these numbers. It was refused for what it would have to be *labelled*.

**Residual, stated rather than buried.** A Homeowner who *states* 6,5 m² for a
kitchen-diner clears `brief.md` §9.4 bound 1, because the bound reads
`max(ergonomic 4,6, statutory 6,0)`. That is the designed behaviour — *a stated
target is sovereign*, `room-area-bands.md` §6.1 — not a leak, and it is the
price of holding the statutory tier to transcription.

## Consequences

1. **Two targets change, and one of them corrects a figure this map nearly
   shipped.** `kitchen_dining` gets rung 2 at **18,8 m²**, and the direct Swiss
   `KITCHEN_DINING` median of **23,67 is disqualified**: 39 of its 41 rooms sit
   in dwellings that also carry a separate `KITCHEN`, so the label is a **dining
   room**. It is also 21 layouts rather than 41 rooms — one site is 4 layouts ×
   6 floors, and the per-unit key hashes differ so a key-based dedup cannot see
   it. 18,8 is `KITCHEN + DINING` summed per dwelling over 1 308 dwellings, and
   it is trusted because **MİDA's `Mətbəx-studio` p50 is 17,37** over 5 Baku
   plans on a net-internal plane. Neither is literally a `mətbəx-yemək otağı`;
   **the agreement at ≈18 is the evidence, not either alone.**
   ⚠️ **The "composition under-predicts by 22 %" correction is void** — it was
   calibrated against the disqualified 23,67 and must not be quoted.

2. **`living_dining_kitchen` gets 21,0 / 22,0 hard and 36,5 as a composed
   target**, on donor labels checked the way `KITCHEN_DINING`'s was not: 0,1 %
   of `LIVING_DINING` dwellings also carry a `LIVING_ROOM`. It binds only on
   Brief-named Rooms — Swiss has no LDK label, so one never arrives from
   retrieval.

3. **A mandatory gas rule explains the empty corpus, and is recorded rather than
   enforced.** AzDTN 2.13-1 cl. 8.31 requires a gas hob to stand in a `mətbəx
   otağı`, and AzDTN 2.7-3 cl. 4.7 files the kitchen-diner inside the word
   kitchen — so a kitchen-**diner** is gas-compliant and a kitchen-**living**
   room is not. MİDA fits gas hobs and publishes zero multi-room open-plan plans
   in 318 geometries. C8 forbids reading a regulatory restriction as a
   compliance target and this map already refused the same move for cl. 5.10 at
   `bathroom_combined`.

4. **`STAT_FLOOR` does not move, so `experiments/warp/` is undisturbed** and the
   four tickets holding it are unaffected. `MARKET["KITCHEN_DINING"]` 6,0 → 18,8
   **is** a change there, and it is handed, not made. ⚠️ ADR 0033's *"the floor
   never fights a target"* held for this limb only at **equality** — floor 6,0,
   target 6,0. Raising the target gives it real headroom for the first time.

5. **A gate is owed and it is the one that is easy to miss: every `part` read
   must have a target.** This ADR leaves the norm's ordering to be carried by
   the target, so a `part` row with no target has nothing carrying it. With
   `compose_with` key existence and soft-tier unreachability, it goes to ticket
   69, which holds `experiments/region-profile/`.

6. **This is the shape for the next cell whose meaning drifts from its number.**
   The failure was never a wrong value — all six statutory values transcribe
   their clause exactly. It was **referent drift**: a number copied away from
   the qualifier that gives it meaning. A guard that reads `statutory_floor.v`
   and stops is aimed at the failure that did not occur.

## Reversal trigger

Not a yield number, and not a tighter candidate for the floor. This ADR is
refuted if **either**:

- Azerbaijan publishes a whole-room area for `mətbəx-yemək otağı` — an amendment
  to cl. 5.7, or a norm the §Context sweep could not reach. Then the entailed
  bound is replaced by a transcription and part 5's reasoning is spent; **parts
  1–4 survive**, because they are about how a cell declares itself.
- The soft tier stops carrying the ordering — if `kitchen_dining`'s target is
  ever removed or falls below **8,0**, the inversion is no longer covered and
  the hard floor has to be revisited. That is what consequence 5's gate exists
  to catch.
