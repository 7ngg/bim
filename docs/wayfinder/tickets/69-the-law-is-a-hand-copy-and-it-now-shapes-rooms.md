---
id: 69
title: The law is a hand copy and it now shapes rooms
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: []
writes:
  - experiments/warp/
  - experiments/region-profile/
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

