---
id: 31
title: Two room vocabularies in one file, and nothing maps between them
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - data/standards/room-constraints.json
  - CONTEXT.md
  - experiments/region-profile/gate_check.py (declared on resolution)
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

---

## Resolution (2026-08-24)

**The two vocabularies are now one canonical set and one declared projection, and the
projection is an object in the file rather than a hope that the key names match.**
`profiles.AZ.rooms.mapping` — eighteen rows, total by construction, asserted by 162 new
gates in `experiments/region-profile/gate_check.py` (`vocabulary_gates()`; the file now
runs **229 gates, all pass**, up from 67).

### What changed the shape of this ticket

**AzDTN 2.7-2's own text is in this repo** — `experiments/finish-layer/out/azdtn_2_7_2.txt`,
read first-hand by *What an Azerbaijani finish layer actually is* — and it contains a
room-vocabulary clause nobody had read. **cl. 5.2**, mandatory register:

> «Mənzillərdə yaşayış otaqları və yardımçı sahələr: mətbəx (və ya taxça-mətbəx), holl,
> vanna otağı (və ya duş) və tualet (və ya birləşdirilmiş sanitar qovşağı), yığnaq otağı
> (və ya divar təsərrüfat şkafı) nəzərdə tutulmalıdır.»

and **cl. 5.5**, which enumerates habitable rooms statutorily:

> «yaşayış otaqlarının (otaq, qonaq otağı və yataq otağı)»

So the "Azerbaijani room-name table that exists nowhere" was in a document this file
already cites fourteen times: the numbers were extracted from cl. 5.7 and the **words
were dropped**. Fourteen of eighteen names are now `verified` and cited. The C8
discipline is satisfied by *sourcing*, not by labelling — which was not the plan going
in, and is a better outcome than the plan.

### The decisions

**1. Canonical: the ergonomic key set, eighteen keys.** Not re-litigated — `brief.md` §3
settled it and said this ticket has one mapping to build. Confirmed and left alone.

**2. The mapping is the vocabulary; `areas_m2` and `clear_widths_mm` are just values.**
No AZ key was renamed. `areas_m2` is a faithful transcription of cl. 5.7's bullet list
and renaming its cells would break the only thing they are for. The defect was never the
names — it was that no object stated the **bridge** between them, so the mapping carries
a `bridge` field wherever the two sides key on different axes.

**3. Two silent collisions found, and neither is fixed by renaming.**

- `bedroom_single` / `bedroom_double` key on **bed capacity** ergonomically and on
  **occupancy** in cl. 5.7 — «yataq otağı - 8 m² (iki adama - 10 m²-dən)». They coincide
  (a bed for two is a room for two), so the mapping is sound and the coincidence is now
  written down. Three ergonomic types → two AZ cells; `bedroom_principal` is also a
  two-occupant room.
- `bathroom`: the `areas_m2` table conflates two axes and **the norm does not**. cl. 5.2
  keeps bath-or-shower and WC-or-combined-unit as two independent choices in one
  sentence. The ergonomic layer keys the first only and has no way to say the WC is
  inside — so `bathroom_combined` is reachable from nothing, deliberately.

**4. One conditioning axis, named, no expression language: `when_otaq_count`.** Three AZ
cells condition on cl. 5.7's `birotaqlı mənzil` and nothing conditions on anything else.
Resolved **in the mapping** — not in the key (that is what produced the defect:
`living_room_1room_flat` is not a room type) and not in the Brief parser (that buries a
profile fact in code, and C14 says a profile is data). A second axis is known to exist —
AD M's `25 + 2 × (bedspaces − 2)` — is not live in v1, and is recorded as a **schema**
change rather than a data one.

⚠️ **Honest limit: the guard buys almost nothing on the default tier yet.**
`living_room_1room_flat` and `living_room_2plus` differ at `statutory_floor` (15,0 / 16,0)
and are **identical at `market_default` (16,0)**, which is the default tier and the
solver's target — so for `living` the guard moves only the statutory *warn*. The other
two conditioned cells are unreachable. Built anyway, because encoding the condition in
the key is what broke this file once and the guard costs one field.

**5. Silence is explicit `null`, and it is the normal case.** Ten of eighteen keys have
no AZ area. `dim.market_default_area` skips such a Space; it does not raise and does not
fall back. C14 read literally: a profile with no preference is a legal profile.

**6. `hall` / `entrance_lobby` / `corridor` stay three types.** The norm carries two
words (`hol` cl. 5.8, `dəhliz` cl. 5.8) and `entrance_lobby` is ours — so `giriş holu` is
the **one `engine_choice` name in the table** and is labelled as such. `hall` and
`entrance_lobby` have byte-identical ergonomic floors (1.0 m², 900 × 1138); that is the
same fixture packing reaching the same rectangle, and it is now noted so nobody "fixes"
it. Retrieval collapsing all three to Swiss Dwellings' single `CORRIDOR` is a lossy
one-way projection and costs nothing.

**7. One name column, `name_az`, not two.** Reversed mid-ticket: the two-column design
(`name_az_norm` + `name_az_display`) rested on the market word being unsourceable, and
**cl. 5.5 supplies `qonaq otağı`** — the norm word and the Baku market word are the same
word. Two columns would have held one string twice. Note cl. 5.7's area table labels the
same room `ümumi otaq`; both are recorded, `qonaq otağı` is published.

**8. `counts_as_otaq` — a new flag, `verified`, not the name ADR 0013 asked for.**
ADR 0013 requested a flag called `habitable`; `is_habitable` **already existed on all
eighteen keys**, and a field called `habitable` sitting beside `is_habitable` and meaning
something else is a defect, not a schema. The two are separate because they drive
different things — `is_habitable` drives windows and exterior walls (C6), `counts_as_otaq`
drives C13's product promise — and they **diverge on exactly one type**: `kitchen_dining`
is habitable and is not an otaq. A gate asserts the divergence set stays exactly
`{kitchen_dining}`, so it cannot grow silently. Sixteen of eighteen values come straight
out of cl. 5.5 / cl. 5.2; `dining` and `study` are `derived` through cl. 5.5's unqualified
`otaq` and say so.

**9. `brief_nameable` shipped**, as `brief.md` §3 asked. False for `corridor` and
`entrance_lobby` only.

**10. Four AZ cells are reachable from nothing and now say so** — `bedroom_mansard` (C5,
single storey), `kitchen_niche`, `wardrobe_1room_entry`, `bathroom_combined`. Kept as
data rather than deleted, the posture `clear_heights_mm.corridor_hall_antresol` already
takes; **not** the `h_storey` case, which ADR 0012 deleted because publishing it would
have been *wrong*.

### The closing check, and a reinterpretation of it

The ticket asked that "for every room type the Brief can name, both a hard floor and a
soft target are resolvable". **Resolvable means the lookup is total, not that a number
comes back.** Ten keys have no AZ area, and the stricter reading could only be satisfied
by inventing ten Azerbaijani numbers — the exact C8 failure this profile exists to warn
about. Gates assert: every hard floor non-null (always, it is ergonomic), every soft
target resolving to a cell or to an explicit null. Recorded in
`mapping.conformance.resolvable_means`.

### Artifacts taken beyond the declared `writes:`

Declared on resolution rather than taken quietly, per the map's Notes:

- `experiments/region-profile/gate_check.py` — `vocabulary_gates()`, 162 gates. Nothing
  else was claimed at the time.

### Handoffs

1. ⚠️ **`rules.json`'s holder — a mandatory room-composition rule with a verified
   statutory source, where the acceptance bar has nothing.** cl. 5.2 requires every flat
   to have a kitchen (or niche), a hall, a bath **or** shower, a **WC** (or combined
   unit) and a storage (or built-in cupboard) — register `nəzərdə tutulmalıdır` =
   məcburi. This closes a hole found while mapping: **nothing today stops a Brief
   producing a dwelling with a bath and no toilet.** The ergonomic `bathroom` floor is
   1000 × 1700 — a bath and no room for a pan — so "bathroom implies a WC" is not
   available as a defence.
2. ⚠️ **`rules.json`'s holder — `kitchen_dining`'s AZ cell constrains a zone, not the
   room.** cl. 5.7's 6 m² is the `mətbəx zonası` *inside* the kitchen-diner; the ergonomic
   4.6 m² is the whole room. Reading the AZ number as a room target under-targets the
   room. Same defect on `living_dining_kitchen`. Flagged not fixed: the correction needs
   a zone concept the geometry model does not have.
3. **`brief.md`'s holder — a nineteenth type, or a recorded narrowing.** cl. 5.2 allows
   `taxça-mətbəx` instead of a kitchen in a one-otaq flat, floored at 5 m² by cl. 5.7. A
   Baku studiya with a kitchen niche is an ordinary v1 case at the bottom of C13's
   promised band, and the Brief cannot say it — a niche is expressed as a `kitchen`
   (ergonomic floor 1,8 m²) and is **under-targeted, not rejected**.
4. **`annotation.md`'s holder (*The annotation spec is US-shaped*) — the names are
   ready.** `mapping.rooms.<key>.name_az`, one per type, fourteen `verified` with clause
   citations and four `engine_choice` carrying notes.
5. **`homeowner-surface.md`'s holder — the prototype's placeholder names can be replaced
   with sourced ones**, and `experiments/homeowner-surface/README.md`'s warning discharged.
6. **`is_private` corroboration, recorded not moved.** cl. 5.9 — «Mənzillərdə yataq
   otaqları digər otağa keçid kimi layihələndirilməməlidir» — makes the bedroom privacy
   flag statutory in AZ. Left on the region-invariant layer per C14; a profile may never
   move it.
7. ⚠️ **`bathroom_combined` carries a restriction the profile never recorded.** cl. 5.10
   permits the combined sanitary unit only in one-room flats of the state and municipal
   social and special-purpose housing stock. Now noted on the cell.

### Technology / refactor needed

**One resolution step now exists that no component owns.** Something must evaluate
`(ergonomic_key, otaq_count) → soft target, clear-width target, printed name`, and it sits
between `resolve` and both consumers (`dim.market_default_area` in the solver objective,
and the Drawing's tag and schedule). It is ~20 lines and pure, but it is **not** currently
named in any spec. It belongs where `resolve` lives. Naming it is a `brief.md` /
`proposer.md` boundary question rather than a decision this ticket should take alone.

**No new dependency, no refactor.** The mapping is data; the gates are stdlib.

### Market check (CLAUDE.md)

This is how production BIM tools already separate these concerns: Revit keys schedules on
a room's classification and prints a name from a separate parameter; ArchiCAD's Zone
Categories and Zone Stamps do the same. Neither conditions a *category* on the dwelling —
both would model `living_room_1room_flat` as a category plus a parameter, which is what
the guard now does.
