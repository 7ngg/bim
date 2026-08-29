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
