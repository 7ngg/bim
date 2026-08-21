---
id: 31
title: Two room vocabularies in one file, and nothing maps between them
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
---

# Two room vocabularies in one file, and nothing maps between them

## Question

`data/standards/room-constraints.json` now contains **two independently-authored
room taxonomies with no mapping between them**, because two tickets populated it
in parallel and neither could see the other's keys.

The **ergonomic layer** (*Ergonomic minima and the constraint table's missing
half*) keys the region-free hard floor by room type:

```
living, dining, living_dining, kitchen, kitchen_dining, living_dining_kitchen,
bedroom_principal, bedroom_double, bedroom_single, study, bathroom,
shower_room, wc, utility, hall, entrance_lobby, corridor, storage
```

The **AZ profile** (*The Azerbaijani region profile*) keys its tiered areas by a
different scheme, one that encodes dwelling size into the room name:

```
living_room_1room_flat, living_room_2plus, ...
```

Nothing contradicts. AZ's `living` statutory floor of 15.0 m² sits far above the
ergonomic 3.7 m², which is the ordering C14 requires — a profile may change which
Plans are *preferred*, never which are *rejected*. The defect is not a conflict of
values. It is that **a Plan cannot resolve one key from the other**, so
`dim.market_default_area` cannot find the soft target for a Space whose hard floor
it just read.

Settle:

- **Which vocabulary is canonical**, and whether the other becomes a view over it
  or is rewritten. The ergonomic keys are consumed by three hard registry rules
  and by the Brief; the AZ keys are consumed by one soft rule. That asymmetry
  suggests a direction but does not settle it.
- **`living_room_1room_flat` versus `living_room_2plus` is not a room type — it is
  a room type conditioned on the dwelling.** AzDTN states the minimum living-room
  area as a function of how many rooms the flat has. The ergonomic layer has no
  such axis and the Brief may not either. Decide whether the profile schema grows
  an occupancy or room-count dimension, or whether the dependency is resolved at
  Brief-parse time and the profile only ever sees a resolved key. *Dimensional
  standards corpus* already found one of these — AD M's LKD area is `25 + 2 ×
  (bedspaces − 2)` — so this is the second, and the schema has answered neither.
- **What happens to a room type one side has and the other does not.** The
  ergonomic layer publishes `shower_room`, `utility`, `entrance_lobby` and
  `study`; a profile that is silent on them is the normal case, not an error, and
  the resolution rule has to say so out loud rather than leaving a `KeyError`.
- **Whether the ergonomic layer's key set is itself right**, given it was derived
  from fixture programmes rather than from the Brief. `bedroom_principal` /
  `bedroom_double` / `bedroom_single` is a *furniture* distinction; `CONTEXT.md`
  collapses bedroom, study and nursery into one **Private room** class and the
  Proposer collapses `{ROOM, BEDROOM, STUDIO}` to `PRIVATE`. Three vocabularies,
  then, not two — and the Brief's is the one a Homeowner actually speaks.

The cross-file check that must pass at the end: **for every room type the Brief
can name, both a hard floor and a soft target are resolvable**, and a conformance
test asserts it — the same shape of test *Acceptance validator spec* used to kill
drift across the 14 `both` rules.

Note this is a **schema and vocabulary** question, not a numbers question. Neither
set of numbers is in doubt and neither should be re-derived here.
