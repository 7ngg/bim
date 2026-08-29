---
id: 69
title: The law is a hand copy and it now shapes rooms
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
blocked_by: []
writes:
  - experiments/warp/
  - experiments/region-profile/
  - data/standards/room-constraints.json
  - CONTEXT.md
  - docs/adr/0037-the-profile-is-read-not-copied-and-the-third-vocabulary-is-published.md
---

# The law is a hand copy and it now shapes rooms

## Question

**`absolute_area.STAT_FLOOR` is a hand transcription of
`room-constraints.json`, and nothing in the repo binds the two.** Six values —
`KITCHEN` 8,0, `KITCHEN_DINING` 6,0, `PRIVATE` 10,0, its lenient limb 8,0, and
the living family's 15,0 / 16,0 — are typed into a Python module beside the JSON
that publishes them, with a comment naming the source and no check.

That was tolerable while the table only **measured**. ADR 0033 makes it
**constrain geometry**: the warp now sizes rooms to these numbers and refuses
candidates that miss them. A drift no longer produces a wrong figure in a report,
it produces a plan built to a floor no regulator wrote — which is the C8 failure
seen from the inside, and the one failure ADR 0027 says the hard set exists to
prevent.

The values are correct **today**; that was verified when ADR 0033 landed, and
`floor_warp._check_floor_transcription` now asserts all six on import. ⚠️ **That
is a guard and not the fix.** It lives in the newest file in `experiments/warp/`,
it fires only when that file is imported, and it protects the one consumer that
already knew to worry.

## What has to be done

1. **Read the floors from `room-constraints.json`** rather than copying them.
   `floors_for` is the single accessor and already composes the otaq guard, so
   the change is contained — but note the JSON's shape is
   `profiles.AZ.rooms.areas_m2.<erg_key>.statutory_floor.v` reached **only**
   through `profiles.AZ.rooms.mapping` (ticket 31), so the mapping is the
   contract, not the raw key.
2. **Decide what happens where the JSON is absent.** The warp rigs import
   cleanly today without the repo's `data/` tree; a hard read makes `data/` a
   dependency of `experiments/warp/`. Either that is accepted and stated, or the
   accessor falls back and the fallback is exactly the drift risk again.
3. **Add it to `gate_check.py`.** 67 gates run there and every one of them is an
   arithmetic property of the profile; *the profile matches its own source* is
   the same class and is currently checked nowhere. This is the durable home for
   it, not a probe's import.
4. **Sweep for the same shape elsewhere.** `project_join.ERG_AREA` is a second
   hand copy — of the *ergonomic* layer this time — and `MARKET` in
   `absolute_area.py` is a third, of `dim.market_default_area`. Neither
   constrains geometry today. Say which, if any, join the gate.

## What this is not

Not a change to any floor's value — a value edit is `room-constraints.json`'s and
is governed by C14's monotone-raise rule. Not a change to ADR 0033. This ticket
removes a way for the map's own numbers to become quietly untrue.

## Raised by

*Should the warp post the statutory floor* (2026-08-29), ADR 0033 consequence 5.

## Handed on by *A zone floor is posted on the whole room* (2026-08-30)

**ADR 0034 landed the referent schema this ticket has to gate, and it made one
of the gates load-bearing rather than tidy.**

`data/standards/room-constraints.json` now carries `mapping.referent_model` and a
`referent` + `compose_with` pair on all **fifteen** `az_area` guard entries across twelve
rows — 10 `room`, 3 `part`, 2 `undetermined`. Four gates are owed, and `gate_check.py` is yours:

1. **Every `az_area` guard entry carries a `referent`**, and it is one of the
   three published values.
2. **Every `compose_with` key exists in `areas_m2`**, and its `statutory_floor`
   is non-null and `conf: verified`. An entailed bound may never sum a `derived`
   or `fitted` cell.
3. **No `part` read is reachable from a soft-tier resolution.** This is the rule
   ADR 0034 exists to enforce and it is currently enforced by prose.
4. ⚠️ **Every `part` read has a target** from some rung of `brief.md` §9.2's
   ladder. **This is the one that is easy to miss and it is the one that
   matters.** ADR 0034 deliberately leaves `kitchen_dining`'s hard floor at 6,0 —
   below the 8,0 a plain `mətbəx` gets — and has the *target* carry the norm's
   ordering. A `part` row with no target has nothing carrying it, and the ADR's
   reversal trigger names exactly this.

**This is item 3 of your own question, arriving with a second instance.** You
already own *the profile matches its own source*; this is *a consumer matches the
profile*, same file, same class.

### Two constants, handed with their derivations

**`absolute_area.MARKET["KITCHEN_DINING"]` 6,0 → 18,8.** The 6,0 was the kitchen
**zone** figure read as a room target. 18,8 is `ergonomic.corpus_medians.kitchen_dining`
— Swiss `KITCHEN + DINING` summed per dwelling over 1 308 dwellings — corroborated
by MİDA's `Mətbəx-studio` p50 of 17,37 over 5 Baku plans.
⚠️ **Do not use the direct Swiss `KITCHEN_DINING` median of 23,67.** It is
disqualified: 39 of its 41 rooms sit in dwellings that *also* carry a separate
`KITCHEN`, so the label is a **dining room**. It is also 21 layouts, not 41 rooms
— one site is 4 layouts × 6 floors and the per-unit key hashes differ, so a
key-based dedup cannot see it.

**`STAT_FLOOR` does not move.** 6,0 stays, so nothing in `experiments/warp/`
re-measures on its account and tickets 62, 65 and 67 are undisturbed.

### An eighth hand copy, and this one is also wrong

Your own note counts six values, and the transcription research found a seventh
(`HABITABLE`, omitting `DINING`). There is an **eighth**:

`fit_warp.MIN_SIDE` has **no `KITCHEN_DINING` entry**, so it falls to
`MIN_SIDE_DEFAULT = 5` (1 250 mm centreline). The ergonomic
`kitchen_dining.min_clear_short` is **1 300 mm**, which by `MIN_SIDE`'s own stated
rule — `ceil((min_clear_short + 150) / 250)` — gives **6**. The warp under-posts
the minimum side for this type by one grid cell. Same class as the seventh: a
table copied beside the data that publishes it, with nothing binding the two.

## Handed on by *A gas hob decides whether the open-plan type is buildable in AZ* (2026-08-30)

**Two items, and the first is a hole in a shipped invariant rather than a drift
risk.**

1. **`floors_for` has no `living_dining_kitchen` limb, and the bar has one.**
   `absolute_area.py`'s `LIVING_FAMILY = ("LIVING_ROOM", "LIVING_DINING")` and
   `STAT_FLOOR` carries three keys, so `floors_for` returns **`None`** for an
   open-plan Room while `dim.statutory_min_area` binds at site **both**. Until
   ADR 0036 the bar demanded **22,0 m²** on a type the warp posted nothing for —
   **ADR 0033's invariant did not cover it**. ADR 0036 takes that cell's
   `az_area` to `null`, so the two now agree at *no AZ floor* — but they agree
   **coincidentally**, through two unrelated omissions. Item 1 of this ticket
   (read the floors from the JSON rather than copying them) makes the agreement
   deliberate, and it is the case that shows why the fix is not cosmetic: a hand
   copy can be wrong by **omission** as well as by drift, and
   `floor_warp._check_floor_transcription` asserts the six values that **are**
   copied, so it is structurally blind to a seventh that is missing.

2. **ADR 0034's owed gates need a FIFTH, and it is the one that would have caught
   ADR 0036's defect.** The four on this ticket check that a `referent` exists,
   that `compose_with` keys resolve to verified non-null cells, that no `part`
   read is soft-reachable, and that every `part` read has a target. **None of them
   checks the licence itself.** ADR 0034 decision 4 grants a sum only for *"cells
   whose disjointness the norm's own type definition establishes"*, and the
   defect was a `compose_with` on a type the norm **does not define** — every one
   of the four gates would have passed it. The fifth: **every `compose_with` names
   the clause whose type definition licenses it**, which means the licence has to
   become a field rather than prose in an ADR. That is ADR 0034 consequence 6's own
   lesson — *"a number copied away from the qualifier that gives it meaning"* —
   applied one level up, to the composition rather than the value.

⚠️ **`experiments/warp/` was at four claimants and this ticket is one of them.**
ADR 0036 wrote no code and claimed nothing there; both items above are stated so
they are transcribed rather than re-derived.


## Resolution (2026-08-30) — ADR 0037

**The profile is read rather than copied, the third vocabulary is published, and
the ticket's own premise was too generous: it was raised on the RISK of drift and
three of the eight copies were already wrong.**

### What was found before anything was changed

1. **`absolute_area.MARKET` sat four cells behind ADR 0035** — which had landed
   the day before. `PRIVATE` 12,0 against **13,2**, both living limbs 16,0
   against **17,6**, `wc` 2,1 absent entirely. One day between an ADR landing and
   its consumer being wrong.
2. **`HABITABLE` omitted `DINING`, whose `counts_as_otaq` is `true`.** So
   `floors_for` under-counted otaq and a living-plus-dining dwelling took
   `living_room_1room_flat`'s **15,0** where the guard says `living_room_2plus`'s
   **16,0**. A hard floor 1 m² low, on the largest room in the plan — not a wrong
   report, a wrong constraint.
3. **`fit_warp.MIN_SIDE` had no `KITCHEN_DINING` row**, falling to
   `MIN_SIDE_DEFAULT = 5` against the **6** its own stated formula gives. The
   eighth copy, exactly as handed on by *A zone floor is posted on the whole room*.
4. **`MARKET["KITCHEN_DINING"] = 6,0` was not drift at all** — it is the read
   ADR 0034 decision 2 forbids outright. That cell measures the `mətbəx zonası`
   (`referent: part`), a sound floor and never a target; the ladder's rung 2 gives
   the room **18,8**. ADR 0034's owed gate (c) had a live violation in shipped code.

### The fix could not be item 1's shape, and the reason is the ticket's real finding

Item 1 read as *replace six literals with a JSON lookup*. Two facts refuse it.

**`floors_for` did not copy numbers; it reimplemented the resolution** — the
`when_otaq_count` match, the fallthrough order and the otaq set the condition
reads, all hand-written beside the guard list that publishes them. Swapping the
values would have bound the half that was right: defect 2 is in the *guard*.

**And the lookup had no key.** The copies are keyed by **corpus label**; the
profile by **ergonomic key**, reached only through `mapping.rooms`. Nothing in the
repo published the map between them — it lived as end-of-line comments inside four
Python dicts. **This is ticket 31's own defect one vocabulary upstream**, *"no
object stated the bridge between them"*, and it is why every one of these copies
existed at all. Item 1's *"the mapping is the contract"* named a contract whose
domain the callers could not reach.

### What was done

1. **`ergonomic.corpus_label_map`** — ten labels plus the three-way collapse, each
   landing on an ergonomic key, `erg_lenient` carrying the one split the corpus
   cannot make. Under `ergonomic`, beside `corpus_label_split` and
   `corpus_medians`, **not** in a region profile: it is a corpus fact and carries
   no region, so a second corpus needs a second block.
2. **`experiments/region-profile/profile_read.py`** — the single accessor.
   `MIN_SIDE`, `MARKET`, `ERG_AREA`, `COLLAPSE`, `GRID_MM` and `T_INT_MM` are now
   its output, built at import. Every consumer keeps the name it imported, so no
   call site moved; the dict is a **cache of a read**, not a transcription.
   `GRID_MM` and `T_INT_MM` were a ninth and tenth copy of the same class —
   `residue_class_mod_grid` publishes both.
3. **Item 2 answered: the data is a hard dependency.** No file, no import, no
   bundled fallback. `_check_floor_transcription`'s silent return when `data/` was
   absent is the escape hatch that let a copy survive to be *checked* instead of
   *read*.
4. **`_check_floor_transcription` is deleted, not extended.** Its own docstring
   called it *"an assertion, not a fix"*, and it was blind twice over: it asserted
   the six values that **were** copied, so a seventh missing by **omission** passed
   it — which is how `floors_for` returned `None` on `living_dining_kitchen` while
   the bar bound that type at site `both` — and it fired only on one import.
5. **Item 4 answered: all eight, in one pass, plus two more.** Three were wrong
   *now*; splitting would have re-derived the bridge twice. ⚠️ `MIN_SIDE` and
   `ERG_AREA` are **derived**, not transcribed, so what is bound is the *formula*
   `ceil((min_clear_short + t_int) / grid)` — gate P3 recomputes it.
6. **ADR 0034's four gates land, and ADR 0036's fifth makes the licence a field.**
   `licence` on every guard entry: an object naming the clause and the type
   definition where the read is `part`, `null` elsewhere. ⚠️ **A gate written over
   `compose_with` alone would pass vacuously forever** — ADR 0036 emptied it on
   every row. The field is non-vacuous today.
7. **The forbidden `part` target is stopped at the read and the cell keeps its
   value.** `kitchen_zone_in_diner.market_default` is a first-hand transcription of
   AzDTN 2.7-3 cl. 5.1 whose own note already says it *"measures a ZONE … and never
   a target"*. Nulling it destroys a number a regulator wrote to fix a *consumer*
   bug, and ADR 0035's monotone rule governs that tier. `market_default_m2` skips a
   `part` guard and falls to rung 2.

### Item 3: `gate_check.py` 235 → **384 gates**, and every family can fail

Fifteen mutations of the data file were run against the new gates and **15/15 were
caught** — referent removed, referent unpublished, `compose_with` on a non-verified
cell, a `part` read losing its ladder target, a target falling to its own entailed
floor, licence removed, licence naming no clause, a spurious licence on a `room`
read, a guard entry appearing without `counts_at_authoring` moving, a label
pointing at no ergonomic key, a collapse source doubling as a label, a second
lenient split, a corpus label the bridge misses, `t_int` drifting from the
catalogue, and `counts_as_otaq` flipped. A sixteenth re-introduced a literal
`MIN_SIDE` into `fit_warp.py` and **gate C1 caught that too** — it gates the
*shape* of the defect without importing the rigs, because coupling a profile gate
to `ortools` would make this file fail when the solver toolchain moved.

⚠️ **The mutation run is the evidence, not the count.** This map has retired two
rules for being unable to fire.

### ⚠️ *"`experiments/warp/` is undisturbed"* is FALSE, and the third correction is large

Measured on the converted index — 46 794 dwellings, 319 222 rooms:

| correction | population | size |
|---|---:|---|
| `HABITABLE` gains `DINING` | otaq moves on **1 308** dwellings (2,80 %); a living **floor** actually moves on **59** | **0,13 %**, 15,0 → 16,0 m² |
| `MIN_SIDE` gains `KITCHEN_DINING` | **41** rooms | 0,013 % |
| `MARKET` re-read | **138 041** rooms (**43,24 %**) on 99,48 % of dwellings | mean **+0,561 m²** |

**`STAT_FLOOR`'s values did not move — but the floor a dwelling gets did**, on 59
of them, because the guard resolved differently. The handoff's *"`STAT_FLOOR` does
not move, so tickets 62, 65 and 67 are undisturbed"* holds for the constant and not
for the constraint.

⚠️ **Every published `market`-arm number on this map was measured at the old
tier.** **The direction is provable and the magnitude is not**: every moved cell
moved *up*, no floor moved, and ADR 0020 sizes the box from Σ target — so no room's
statutory floor becomes harder to clear. The starvation figures are **conservative,
not wrong**. A re-run is owed to whoever holds `experiments/warp/` next and is
deliberately not taken here: it would move results three open tickets are built on,
inside a ticket holding none of their subjects.

### Handed on

- **A `market`-arm re-run at the ADR 0035 tier** — to `experiments/warp/`'s next
  holder (**62**, **65** or **67**). Cheap: no re-fit, the tables now resolve
  themselves — and it is **not a task anyone has to remember**, because `MARKET` is computed at import, so any re-run already uses the new tier. What is owed is **not quoting the published figures**.
- **A ninth hand copy, named and not taken.** `gate_curve.K` and
  `room_area_spread.K` duplicate `rules.json`'s `area_bands`. Same class; they
  constrain no geometry. `rules.json` is claimed by **71** and **72**, so this is
  prose, exactly as 73 and 74 handed theirs on.
- **`bedroom_principal` is unreachable from the corpus** — a Brief-nameable type
  with no corpus label, so retrieval never produces one. Recorded on the bridge.

### Declared on resolution

`data/standards/room-constraints.json` (unclaimed in assignment; **72** lists it,
and this touched only the bridge block and the `licence` field — none of 72's
subject, no citation repair, no value edit) and `CONTEXT.md` (unclaimed): new term
**Corpus label**, plus the licence-is-data clause on **Statutory floor** and the
every-projection-is-published clause on **Room type**.

### What this did not do

No floor's value changed — a value edit is `room-constraints.json`'s and governed
by C14's monotone rule. ADR 0033 is untouched. `data/acceptance/rules.json` was not
opened.
