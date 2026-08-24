---
id: 31
title: Two room vocabularies in one file, and nothing maps between them
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - data/standards/room-constraints.json
  - CONTEXT.md
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

---

## Handed here by *What a room's area is allowed to be* (2026-08-22)

**Two corpus measurements this ticket should consume rather than re-derive**, and
one vocabulary gap it is the right owner for. Source:
`docs/research/room-area-bands.md`.

1. **`ergonomic.corpus_label_split` records medians and no upper tail, and the
   tail is where it matters.** Re-measured from Swiss Dwellings' **fixture**
   ground truth — toilet present, no bath or shower, 13,436 in-band rooms — a
   real WC runs p50 **1.85** / p95 **3.71** / p99 **5.29** / p99.5 **6.20** /
   max **18.23 m²**; a real bathroom p50 **4.10** / p99 **8.23** / max **24.52**.
   The p50s reconcile exactly with what the key already records.
   ⚠️ **The 2.4 m² splitter cannot see the tail**: **19.3 % of real WCs sit at or
   above it**. Anything read *through* the splitter is truncated at 2.4 by
   construction — a cap fitted that way came back as 2.40 at p95, p99, p99.5
   *and* p99.9 before the circularity was caught.

2. **The silent-profile medians for `brief.md` §9.2's ladder rung 2.** `wc` =
   **1.85 m²** (fixture). `kitchen_niche` and `wardrobe_1room_entry` have **no
   corpus type at all**, so rung 2 is empty and they fall through to absent, as
   §9.2 already specifies.

3. ⚠️ **`hall` is the vocabulary gap and it is yours.** The ergonomic layer
   carries `hall`, `entrance_lobby` **and** `corridor` as three distinct types.
   Swiss Dwellings carries **one** label, `CORRIDOR`; ResPlan carries **none**.
   The 7.58 m² median measured is all three merged, and is offered as a
   measurement with its limit attached, **not** as a default for `hall`. Whether
   the three collapse, and if so to what, is a vocabulary decision — which is
   this ticket.

---

## Handed in by *The room-count envelope v1 promises* (ADR 0013)

**`room-constraints.json` needs a `habitable` flag per ergonomic key.** Same
shape as the `brief_nameable` flag `brief.md` §3 already asks you for, and for a
related reason: otaq — the unit v1's supported band is *stated* in — is the count
of habitable Rooms only (bedrooms and living rooms; never kitchen, bathroom,
corridor or store), and nothing in the file can currently compute it from a Brief.

Note it lands on the **ergonomic** layer, not on `profiles.AZ`, even though the
convention is Azerbaijani: what counts as a habitable room is not a construction
system or a drawing convention, so C14 keeps it out of the profile.

Corroboration for the three-into-one gap you already hold: Swiss Dwellings has
**no `HALL` or `LOBBY` subtype at all** — 53,295 `CORRIDOR` rooms absorb every
one of them. So the corpus cannot distinguish the three either, and any mapping
that needs to must come from the profile side.

---

## Handed in by *Homeowner product surface*

**An Azerbaijani room-name table, and it exists nowhere in this repo.**

The surface is Azerbaijani (`docs/spec/homeowner-surface.md` §2). The room tag,
the Brief document and the room schedule all print a **name**, and
`room-constraints.json` carries no display name for any ergonomic key in any
language. `profiles.AZ.drawing.abbreviations_published` covers seven drawing
abbreviations from AZS 21101-2010 Əlavə D and **zero room words** — that annex
is explicit that abbreviating outside its list is forbidden, so the gap cannot be
closed by abbreviating.

**One name per ergonomic key, eighteen of them**, display-only in the sense
`brief.md` §3 already establishes for `label` — the type stays the load-bearing
thing.

**It makes this ticket's own three-into-one gap worse, not better.** In English
`hall` / `entrance_lobby` / `corridor` collapse plausibly. In Azerbaijani they do
not: **`hol` and `dəhliz` are different rooms to a Baku buyer** — one is where you
take your shoes off, the other is what you walk down — and `giriş holu` is a third
thing again. So the mapping you build has to survive being *printed on a drawing
in front of the person who asked for the room*, which is a stiffer test than
keying a minimum off it.

⚠️ The prototype's names are **unsourced placeholders** and are marked as such in
`experiments/homeowner-surface/README.md`, on branch `prototype/homeowner-surface`. Do not lift them: the C8 discipline
that caught *The Azerbaijani region profile* applies — a plausible name set
published without a source is exactly the failure mode that ticket exists to
warn about.
