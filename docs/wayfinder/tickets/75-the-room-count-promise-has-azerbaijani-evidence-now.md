---
id: 75
title: The room-count promise has Azerbaijani evidence now
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - docs/adr/0013-the-room-count-promise-is-two-numbers-in-two-units.md
  - docs/spec/homeowner-surface.md
---

# The room-count promise has Azerbaijani evidence now

## Question

**C13 promises 1–4 otaq, the number was set on Swiss data, and Azerbaijan has now
published a figure in the promise's own unit.**

The 2024 Azerbaijani household survey puts **93,7 %** of Baku occupied dwellings
inside the 1–4 otaq band — 5,4 + 27,4 + 44,4 + 16,5 %. MİDA's own build mix
agrees independently: over 318 distinct plan geometries the counts run 5 studio /
32 one / 122 two / 125 three / 33 four, which is **100 % inside the band**.

C13's shipped figures are **89,9 % promised, 4,3 % served-unpromised**, and both
are Swiss. The Room-count row of the done-test is `settled` and — until this
ticket — carried **no ticket at all**, so nothing on the map owned the fact that
its central number came from the wrong country.

**Raised, not taken, by *A zone floor is posted on the whole room* and then again
by *The market tier has an Azerbaijani source now*.** Both closed leaving it
explicitly undone: 73 does not write either artefact below, and smuggling a
product-promise change into a standards-table ticket is the `writes:` violation
the Notes exist to prevent.

## What has to be decided

1. **Whether 89,9 % is restated on Azerbaijani evidence or kept and annotated.**
   The two numbers are not the same quantity — 89,9 % is a Swiss corpus share and
   93,7 % is an Azerbaijani *occupancy* share — so replacing one with the other
   is a change of what the sentence means, not a better estimate of the same
   thing. ⚠️ Decide which quantity the promise should be stated in **before**
   deciding which number.
2. **What happens to the 4,3 % served-unpromised zone.** C13's whole shape is
   that the engine serves 3–10 engine rooms and the copy claims 1–4 otaq, with a
   deliberate gap between them. If the AZ occupancy distribution differs from the
   Swiss one, the gap moves, and the gap is the part a Homeowner can be
   disappointed by.
3. **Whether the studio case is inside the promise.** MİDA builds 5 of 318 as
   studios and its own `nrooms` calls them 0. C13 says 1–4 **otaq**; a studio is
   arguably 1. `brief.md`'s `living_room_1room_flat` cell exists for exactly this
   dwelling and AzDTN's `birotaqlı mənzil` conditioning axis names it — so the
   engine already models it and the copy may not claim it.
4. **Whether ADR 0013 is amended or merely annotated.** Its two-numbers-in-two-units
   structure is not in question; only the provenance of one of them.

## What this is not

Not a change to the engine's 3–10 hard refusal — that is an engine-room count and
this ticket is about the otaq promise. Not a re-opening of ADR 0013's
two-units shape, which nothing here disputes.

## Raised by

*The market tier has an Azerbaijani source now* (2026-08-30), item 6, which
declined to take it because it writes neither artefact.
