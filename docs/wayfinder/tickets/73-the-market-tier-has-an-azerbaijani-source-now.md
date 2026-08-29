---
id: 73
title: The market tier has an Azerbaijani source now
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: []
writes:
  - data/standards/room-constraints.json
  - experiments/baku-market-areas/
  - docs/research/az-market-default-against-practice.md
---

# The market tier has an Azerbaijani source now

## Question

**`market_default` is the default tier, it is what the solver targets, every one
of its values is a recommendation transferred from a detached-house norm, and
Azerbaijani built-stock data now exists to check it against.**

MİDA publishes per-room areas. `mida.gov.az` is a React shell, so every earlier
attempt fetched the shell and concluded nothing was there; its bundle calls an
undocumented public JSON endpoint returning the full *eksplikasiya* per apartment
type. **318 distinct Baku plan geometries**, and the room areas sum to
`internal_size` **to the cent** — which pins the plane as **net internal**, what
ADR 0010 measures. `docs/research/az-market-default-against-practice.md`.

**One cell is already known to be wrong, in the direction the Swiss check could
not see.**

| cell | target | MİDA p50 | |
|---|---:|---:|---|
| `kitchen` | 9,0 | 9,06 (n=312) | lands on it |
| `bedroom_double` | 12,0 | 13,20 (n=287) | fine |
| `living_room_2plus` | 16,0 | 17,60 (n=312) | fine |
| **`bathroom_combined`** | **3,8** | **3,51** (n=318) | ⚠️ **above practice — 63,5 % of Baku main bathrooms are smaller** |

`bathroom_combined` was measured against Swiss rooms when it was added, found on
the median to two decimals, and called settled. **Two corpora, opposite
verdicts.** A soft target *above* what the region builds is not a rounding error
— it is the engine reliably preferring a bathroom Baku does not build.

**What has to be settled:**

1. **The whole tier re-read against the 318 plans**, cell by cell, with n and
   provenance per value. Nine area cells and six width cells.
2. **`bathroom_combined` 3,8**, the one known contradiction, which should not
   wait for the rest.
3. **Whether the MİDA harvest is committed.** It sits in gitignored
   `experiments/baku-market-areas/out/`. ⚠️ **The endpoint is undocumented and can
   vanish without notice**, and every measured number on this map is meant to be
   reproducible from pinned inputs — the posture `requirements.lock.txt` is held
   to. C9 puts licence outside the gate for research data. Against: third-party
   data of unstated terms, and `minima.md` §7.1's copyright posture forbids
   reproducing published tables wholesale.
4. **`what_could_not_be_obtained.market_practice` is false today.** It carries a
   pointer saying so; rewriting it properly is this ticket's.
5. **The tier's structural defect, which no re-read fixes by itself**: every
   value is a *recommended minimum* — `az olmamaqla … tövsiyə edilir` — while
   `tier_model` calls the tier *"what is actually built"*. Those are different
   quantities and the file says one while holding the other.
6. ⚠️ **C13's promise has Azerbaijani evidence for the first time.** The 2024
   household survey puts **93,7 %** of Baku occupied dwellings inside the 1–4
   otaq band. C13 was set on Swiss data; this belongs on the Room-count row, and
   ticket 70 deliberately did not write it.

## What this is not

Not a change to any `statutory_floor` — those are AzDTN's and settled three times
over. Not the referent question, which ADR 0034 closed. Not `kitchen_dining`'s or
`living_dining_kitchen`'s targets, which ADR 0034 set at rung 2 and which this
ticket may supersede **only with a room-level Azerbaijani measurement, never with
a proxy** — MİDA's `Mətbəx-studio` (n=5) is already recorded as the corroboration
for 18,8 and must not be promoted to the source.

## Raised by

*A zone floor is posted on the whole room* (2026-08-30), whose Baku market
research overturned the premise that no such source exists.
