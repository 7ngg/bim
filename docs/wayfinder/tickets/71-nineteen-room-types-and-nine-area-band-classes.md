---
id: 71
title: Nineteen room types and nine area-band classes
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: []
writes:
  - data/acceptance/rules.json
  - docs/research/room-area-bands.md
---

# Nineteen room types and nine area-band classes

## Question

**`dim.max_area` binds `k[type] × Room.target_area`, and there is no published
type-to-class map.** `rules.json`'s `area_bands.classes` holds **nine** entries —
`room*`, `bathroom`, `wc`, `kitchen`, `living_dining`, `living_room`, `corridor`,
`dining`, `storeroom` — keyed by **corpus label**, while `brief.md` §3 fixes
**nineteen** Room types. Every class carries `"members": null`.

The rule's own statement says `k[type]`; the table is `k[class]`. Nothing in the
repo states which is which. `kitchen_dining`, `living_dining_kitchen`,
`bathroom_combined`, `entrance_lobby`, `hall`, `study` and `utility` all resolve
through a mapping that exists only in whoever last read it.

**Found, not caused, by *A zone floor is posted on the whole room* — and that
ticket defused the acute form rather than fixing it.** The old `kitchen_dining`
target of 6,0 put the cap at `k × 6,0` ≈ 13–15 m² against a corpus minimum of
20,9: every real kitchen-diner rejected from *above*, by a hard rule. The target
is now 18,8 and the cap lands ≈48–58 m², so nothing is visibly broken today. The
mapping is still unwritten, and the next type whose target moves will hit it
again.

**What has to be settled:**

1. **The nineteen-to-nine map, published as data** — `members` on each class, or
   a class key per room type. ⚠️ Two types have **no plausible class at all**:
   `living_dining_kitchen`, for which no corpus label exists, and
   `kitchen_dining`, whose label is **disqualified** (ADR 0034 consequence 1 —
   39 of its 41 rooms sit in dwellings that also carry a separate `KITCHEN`, so
   the label is a dining room). Deciding those two is deciding whether a compound
   type borrows a class or earns one.
2. **Whether `absolute_cap[type]` is reachable for every type.** It is the
   fallback where no target exists, so a type with no class has no cap either —
   which is the `40 m² WC` defect `brief.md` §9.3 was written to close, reopened
   through a different door.
3. **Whether `k` should be re-fitted for the compound types rather than
   borrowed.** `k` runs 2,02 to 8,15 and `room-area-bands.md` §6.1 says a single
   global `k` would be the invented number the rule exists to avoid — borrowing a
   neighbour's `k` is a smaller version of the same move.

## What this is not

Not a change to any fitted value: the nine `k` and `absolute_cap` figures are
ADR 0023's, `conf: fitted`, with published corpus costs. Not the referent
question — ADR 0034 settled that, and this is the tier below it.

## Raised by

*A zone floor is posted on the whole room* (2026-08-30), which needed a class for
`kitchen_dining`, found none, and declared `rules.json` for prose only rather
than author this inside a kitchen-diner ticket.
