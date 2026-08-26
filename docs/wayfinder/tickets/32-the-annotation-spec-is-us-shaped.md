---
id: 32
title: The annotation spec is US-shaped and the drawing is now Azerbaijani
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - docs/spec/annotation.md
  - data/standards/room-constraints.json
declared_on_resolution:
  - docs/adr/0024-the-sheet-conforms-to-spds-and-the-layers-do-not.md
  - docs/spec/openings.md
  - data/acceptance/rules.json
  - experiments/region-profile/build_ergonomic_layer.py
  - experiments/region-profile/ergonomic_check.py
  - CONTEXT.md
---

# The annotation spec is US-shaped and the drawing is now Azerbaijani

## Question

*Dimensioning and annotation rules* fixed the sheet set, the title block, the
three drawn schedules and the layer names **before any region profile existed**,
and reached for the conventions nearest to hand — US NCS sheet numbers, AIA layer
names, `FFL`, `D1`/`W2` opening marks. *The Azerbaijani region profile* then fixed
the drawing's language as **Azerbaijani**, and read the Azerbaijani drafting
standards first-hand. Several of those defaults are now demonstrably not what an
Azerbaijani builder reads.

None of this is a bug in either ticket. It is the seam between them, and nobody
owns it.

**What is already established, so it does not need re-researching:**

- **`AZS ГОСТ 21.101-2010` and `21.501-2010` exist, are Azerbaijani-language, and
  are free from the issuing committee.** Read first-hand. This is a *published*
  convention, not an invented one, which is why it can be adopted at all.
- **Əlavə A marks architectural working drawings `MH`** (*Memarlıq həlli*) **or
  `MT`**, where `annotation.md` §9/§10 numbers sheets `A-101` on NCS.
- **Əlavə D gives seven abbreviations the spec actually consumes** — including
  **`t.d.s.`** (*təmiz döşəmə səviyyəsi*) where the spec says `FFL`, `M` for scale,
  `əd.` for a schedule quantity column, `sh.` for an area column. Marked *tövsiyə
  olunan*: permitted, not mandated.
- **Opening marks are two-level**, where the spec models one: a plan mark
  (windows `ОК<n>`; doors a **bare number in a Ø5 mm circle** in the Azerbaijani
  edition) plus a product designation (`ДГ 21-9`) carried in the schedule. The
  spec's `D1`/`W2` matches **no** published convention.
- **The decimal separator is a comma and there is no thousands grouping**, and
  `DIMDSEP` **is inert as the spec is written** — §4 sets `dimdec = 0`, so there is
  no decimal for it to separate. The profile field has to be plumbed to the strings
  we format ourselves — areas, levels, schedule cells — or it silently never fires.
- **The room-tag abbreviation ladder's step 2 is deleted.** No published room-name
  abbreviation set exists in *any* candidate language; SPDS and ISO 4157-2
  independently prescribe **room number + room schedule**, which §6 already ships
  with a `Ref` column and a totality assertion.

## What has to be decided

1. **Sheet numbering.** `MH-101` / `MT-101` against `A-101`. The builder reads
   this. The counter-argument the profile already records: **layer names are a
   machine-facing interchange convention** with their own justification in §11 — *a
   Practitioner recognises the real ones on import* — so `A-WALL` may well stay
   while the sheet number moves. Decide both, and say why they differ if they do.
2. **How much of the drawing is region-parameterised at all.** Today the profile
   owns "decimal separator, abbreviations, opening keys". This ticket may be
   evidence that it should own a **drawing convention object** — sheet marks, level
   annotation, mark scheme, schedule column headings — or evidence that it should
   not, and that v1 hard-codes one convention and says so. **Do not answer this by
   adding fields one at a time**; that is how the US-shaped default got in.
3. **The opening mark scheme**, given it is two-level and the schedule already
   exists. Which level appears on the plan, which in the schedule, and what the
   `Ref` column joins on.
4. **Whether the opening catalogue is `verified` at all.** ГОСТ 6629-88 is
   **superseded**, and its live successors explicitly refuse to fix an opening grid
   — ГОСТ 23166-99 cl. 4.9 makes it a project decision. If that holds, the
   catalogue is `engine_choice` bounded by the old series, and the profile's `conf`
   labels are wrong and must be restated.

## Already handled, do not redo

The **DXF version floor** is settled and was measured, not argued: the Azerbaijani
alphabet is unrepresentable in R2000 — no legacy code page encodes `ə`, not even
Turkish cp1254 — and Russian is worse, since cp1251 cannot encode `²`. **R2007 is
the floor.** `bim-cad-export-stack.md` is corrected in two places and
`annotation.md` §11 already writes R2010, so nothing shipped is broken. Probes in
`experiments/az-drawing/`.

**Not this ticket:** the language choice itself, which is settled and which is what
created this seam.

Deliverable: amendments to `docs/spec/annotation.md`, and either a `drawing`
convention block in the region profile or a stated decision that there is not one.

## Inherited from *Area measurement convention* — four amendments to `annotation.md`

ADR 0010 lands squarely in this file, and this ticket owns it: `annotation.md` is
in this ticket's `writes:` and not in 17's.

1. **Delete the tier-1 centreline exception.** ADR 0004 measured a party edge to
   its centreline *"because GIA and IPMS both do"*, and its §4 committed the rule
   to follow *Area measurement convention*. That ticket landed on
   `az_umumi_sahə`, which stops at the **finished inner face** and does not do
   what GIA does. Tier 1 now measures the Envelope's inner ring on every edge,
   exterior and party alike. **The sheet then carries no centreline dimension
   anywhere**, which is what ADR 0004 wanted in the first place — and the
   exception was always in tension with its own thesis that *"every tick is a
   number a person can tape"*, because a party-wall centreline cannot be taped
   from inside the flat.
2. **`DIM-CONV` loses its second clause.** It currently reads *"Dimensions to
   finished wall faces. Overall to outer face of external walls and to centreline
   of party walls."* The second sentence is now false in both halves. General
   note 2 carries the same text and moves with it.
3. **`AREAS` and general note 5 get their filled-in value.** Note 5 is written as
   *"Areas are `<convention>`, measured to finished wall faces"* with the
   placeholder waiting on 17. The value is **`ümumi sahə`, Area Qaydalar cl. 3.8,
   measured per cl. 3.2 between finished faces at floor level, skirtings
   excluded** — rendered in Azerbaijani per this ticket's own language decision.
   The word "finished" is now true rather than aspirational: ADR 0010 moved the
   plane to match it.
4. **The A-102 room schedule's difference column changes meaning, and improves.**
   It states the Envelope inner area against the room total. That difference is
   now exactly the **internal partition footprint**, because `ümumi sahə` sums
   room areas and does not count partitions. It stops being a curiosity and
   becomes the reconciliation line a Practitioner checks first — say so in the
   schedule's own note.

**One number moves on the drawing and it makes this file's problem smaller**, not
larger: `t_int` is now **150 mm**, not 120. ADR 0004's collision complaint was a
2 mm paper tick at 1:50 against 2.5 mm of text; at 150 mm it is 3 mm. Fewer
leaders. Do not restate this as a justification for anything — ADR 0010 records
it as a side effect, and had the arithmetic pointed the other way the decision
would be unchanged.

---

## Handed in by *Homeowner product surface*

**The room tag has no Homeowner-audience fallback, and the fallback it does have
points at a document the Homeowner never sees.**

`annotation.md` §1 tags the room tag `both` and every schedule `practitioner`.
`profiles.AZ.drawing.room_tag_fallback` resolves a tag that will not fit to
**"room number + room schedule reference"** — a decision that is `verified`
against two independent standards families and is right for the sheet.

On the Homeowner's eager SVG preview it degrades to a bare number pointing at a
schedule that is filtered out of that presentation. **Reproduced**: in `experiments/homeowner-surface/`
on branch `prototype/homeowner-surface`, a 1,85 m-wide bedroom in a real solved layout
overflows its tag.

The audience split is what creates this — the fallback and its target are on
opposite sides of it — so the fix belongs with whoever owns that split. Options
the surface can live with, in order of how much they cost this spec: shorten to
the name alone and drop area and clear dims; scale the tag; leaf the tag outside
the Space with a leader; or promote a minimal room schedule to `both`.

**Related, and it is yours too:** the surface is now **Azerbaijani**
(`docs/spec/homeowner-surface.md` §2), which is the same direction this ticket is
already pulling `annotation.md`. The preview must use the decimal comma and
**must not group thousands** — `profiles.AZ.drawing.thousands_separator` is
`null` because CLDR gives `.` as the `az` group separator, so a grouped `4.400`
reads as a decimal.

---

## Handed here by *H8 and the single-aspect flat* (2026-08-26)

**Your 1,85 m-wide bedroom is not a tag problem, and this ticket owns the file
that decides it.** You hold `data/standards/room-constraints.json`.

You reproduced *"a 1,85 m-wide bedroom in a real solved layout overflows its
tag"* and read it as an annotation defect created by the audience split. It is
also the **width the hard bar permits**, arrived at independently:
`ergonomic.rooms.bedroom_double.min_clear_short` is **1 650 mm**, whose realisable
value under ADR 0007/0009 at `t_int` 150 is exactly **1 850**. So the layout that
broke your tag was not unlucky — it was the solver sitting on the published floor.

The floor is derived as *double bed 1350 × 1900 + body zone 300 to one side*
(AD M M4(2) 2.25). That is a **fits** floor, not a **habitable** floor, and three
numbers now sit against it:

- `profiles.AZ.rooms.clear_widths_mm.habitable_room.market_default` = **3 000 mm**.
- AzDTN 2.7-2 cl. 5.7 fixes `bedroom_double` at **10.0 m²** statutory, against the
  ergonomic `min_area` of **3.1 m²**.
- **19.3 %** of real Swiss rooms have a facade run below 3 000 mm; only **3.1 %**
  fall below 1 850. Measured on 2 169 window-needing rooms in 561 dwellings.

This matters beyond the tag because the acceptance bar's frontage arithmetic now
*clears* on these minima: *H8 and the single-aspect flat* found the single-aspect
flat is feasible to 16 rooms rather than dead at 7, and part of the reason is that
each habitable room is allowed to present 1 850 mm at the facade. **H8 passes on
rooms an architect would not draw**, and the place to fix that is the room table,
not a window rule — which is why it is handed to you rather than fixed there.

The *severity* half — whether a statutory floor may reject at all, given C14 —
is ticketed separately as *A statutory floor, posted soft, in the one region v1
ships*. What is yours is the **region-invariant width**: whether 1 650 is the
right published minimum for a room someone sleeps in, or whether it is the
minimum for a room a bed fits in and the two were never the same number.

⚠️ If it moves, `ergonomic_check.py` and `gate_check.py` both re-derive from it,
and the erosion arithmetic means the *published* number and the *realisable* one
move in steps of 250 mm.

## Handed here by *A statutory floor, posted soft, in the one region v1 ships* (ticket 50)

Three items, because this ticket is `data/standards/room-constraints.json`'s **sole
claimant** and 50 would otherwise have written into a claimed file — the
parallel-write hazard that created this ticket in the first place.

**(a) BLOCKING — the window width series, per room family.** `win.area_ratio` is now
**hard** (soft -> hard, rescoped to living rooms and kitchens per AzDTN cl. 9.13),
and its satisfiability rests on `window_for_room` selecting the **smallest series
member that meets 1:8** instead of picking one of three fixed catalogue entries.

Measured, ready to transcribe rather than re-derive:

| | against the 3-entry catalogue | against a width series |
|---|---|---|
| living rooms needing 2+ windows | 72,7 % | — |
| `living_dining` needing 2+ | 93,6 % | — |
| kitchens needing 2+ | 40,7 % | — |
| dwellings the rule cannot fit | **21,20 %** (at `min_pier` 250; 33,68 % at 600) | **5,39 %** |

**Three quarters of that cost is a catalogue artefact, not a layout fact.** The
series must reach **p90 2,47 m living, 3,23 m `living_dining`, 1,34 m kitchen**; a
top member below those turns the residual back up. Cover for publishing one is
already in the file: `catalogue_may_be_dead` records that `gost_23166_99` cl. 4.9
makes the opening grid a **project decision**, so a published series is
`engine_choice` bounded by `gost_11214_86` and is *more* defensible than three fixed
entries, not less. Splitting into two openings buys **nothing** — total glazing width
is fixed and the pier is pure loss — so this never asks for a second window, and
`min_pier_mm` is **not** load-bearing for it.

**(b) The tier binding must follow `rules.json`'s, and `ergonomic_check.py` is
FAILING RIGHT NOW because of it** -- 229 pass, 1 fail, deliberately left that way:
`both files name the same hard tier -- ['ergonomic', 'statutory_floor'] vs
'ergonomic'`. The check is doing its job; do not relax it.

⚠️ **Make the edit at the AUTHORING site.** `build_ergonomic_layer.py:267` re-writes
`hard_reject_below` on every run, so editing the JSON alone is reverted the next time
anyone regenerates -- the same trap that silently reverted `kitchen.needs_window` and
falsified three published numbers.

`tier_model.validator_binding.hard_reject_below` scalar `"ergonomic"` -> list
`["ergonomic", "statutory_floor"]`, and `statutory_floor_binding` `"warn"` ->
`"hard"`. The two files contradicted each other — this one bound the tier as a warn,
`rules.json` listed it unread — and **neither binding had a rule behind it**. The
conformance test that asserts both files carry the same *string* must assert the same
**list**. This is the one genuine schema change the decision costs.

**(c) `window_for_room` becomes a selection, not a map** — `erg_key -> (height, width
series)`, even per ADR 0004, fitting the run the Space has. A **series** and not a
free derivation, deliberately: this file's own comment is *"a facade with two
different windows in one room is a tell"*. The **derived Type mark** rides with it —
the GOST mark reads **height-then-width**, so `OR 15-<w/100>` is mechanical — and
that half is `annotation.md`'s, which this ticket also holds.

All three are also written into `data/acceptance/rules.json`'s own `owed` block, so
they survive if this note is missed.

---

## Resolution

**[ADR 0024](../../adr/0024-the-sheet-conforms-to-spds-and-the-layers-do-not.md).**
One line decides the whole ticket, and the ticket's second question is what
demanded it:

> **A sheet mark is read on paper by a builder. A layer name is read on import by
> a program.**

Everything a person reads on the sheet conforms to `AZS ГОСТ 21.101-2010` /
`21.501-2010`. The layer names stay US NCS / AIA. They differ because their
readers differ, and that is the answer to "say why they differ if they do".

### The four questions

**1. Sheet numbering.** Set mark **`MH`** (*Memarlıq həlli*), Əlavə A, sheets
numbered sequentially inside it. **This is not a letter swap and the ticket's own
framing of it as `MH-101` against `A-101` was wrong**: SPDS carries the
designation on the **set** where NCS puts a discipline letter and a series number
on each **sheet**, so `A-101` has no counterpart of the same shape. The set is
`<job>-MH` and the sheets are *Vərəq 1 / 2*. Layer names do not move.

**2. How much is region-parameterised.** **No new object, and the ticket's
warning was aimed at the wrong thing.** The profile already has a `drawing`
block; what was missing was not a container but a **test for membership**. It is
now written into the block as `what_belongs_in_this_block`: *a field belongs here
iff a person reads it.* Under that test the block is complete rather than
growing — sheet marks, level abbreviation, separators, mark scheme, room
vocabulary, tag fallback and the area annotation are in it; layers, lineweights,
ISO 3098 sizes and the DXF floor stay in the spec. The next person has a test to
apply instead of a precedent to follow, which is what "do not add fields one at a
time" actually needed.

**3. The opening mark scheme.** **Two-level.** Plan carries a position mark in a
Ø 5 mm circle — windows `ОК<n>`, doors a **bare number**; schedule carries the
GOST product designation. ⚠️ **Doors and windows number in two separate spaces,
so the join key is `(kind, n)` and never `n`** — a join on the number alone
silently matches door 1 to window 1, and `draw.schedule_complete` asserted
totality on a key that could not distinguish them. ⚠️ **The window prefix is
downgraded to `conf: derived`**: `ОК` is read off `ГОСТ 21.501-2018`, an RF
standard this repo verified AZ is **not** a voting party to, and the operative AZ
edition is silent. Taken anyway — a Latin `P<n>` for *pəncərə* would be the
invented abbreviation that deleted the tag ladder's step 2 — but labelled
honestly.

**4. Is the catalogue `verified`?** **The label splits and only the outer half
moves.** Each entry's *dimensions* stay `verified` — read first-hand off the GOST
size drawings, and that reading is still true. The *selection* becomes
`engine_choice`: `ГОСТ 6629-88` is superseded and `ГОСТ 23166-99` cl. 4.9 makes
the opening grid a **project decision**. This is what makes the window series
publishable at all — extending a grid nobody mandates is a project decision;
extending a "verified" catalogue would be falsifying a citation.

### The BLOCKING item, and ticket 50's shape had to change

✅ **`profiles.AZ.openings.width_series_mm` — 600, 750, 900, 1200, 1350, 1500,
1800, 2100, then 2400, 2700, 3000, 3300.** `window_for_room` is now
`erg_key → (height, width series)`: height fixed per family at the two the
retired entries already carried, so **every derived sill is unmoved** at
700/700/1000. Selection is target-first — smallest member reaching the soft
0,154 subject to `open.fits_segment`, else the hard 0,125, else a **hard failure
of `win.area_ratio` reported as one** rather than downgraded to whatever fits.

⚠️ **It cannot be "engine_choice bounded by `gost_11214_86`" as ticket 50 wrote
it.** The published nominal widths run out at **21 dm** and 50's own measured
reach requirement is p90 **3,23 m** for `living_dining` — 1 130 mm above anything
GOST prints. Members through 2100 sit on the published grid; the top four are an
**engine extension**, marked in the data by `published_through`, and above that
boundary the schedule prints a plain dimension string rather than a fabricated
`ОР 15-27`.

⚠️ **One correction to 50's reasoning.** It wrote that splitting into two
openings *"buys nothing — total glazing width is fixed and the pier is pure
loss"*. That is true when the **wall run** binds and **false when the catalogue
top binds**, where a second opening is the only way past it. The two cases were
not distinguished. The extension removes the second, which is what lets one
window per Space stand — and one window per Space is what keeps the profile's own
rule, *a façade with two different windows in one room is a tell*, true by
construction.

Raising the height instead was weighed and does not work: at H 1800
`living_dining` still needs 2 692 mm, and `sill = head_datum − H` puts the sill at
**400 mm**, re-opening a guarding question `fall_barrier_when_required` refuses
to evaluate.

### It forced an amendment to a file this ticket does not hold

⚠️ **`docs/spec/openings.md` §6.1 is rewritten**, and leaving it was not an
option: it fixed three sizes and varied the **count**, which contradicts a sized
window. **Its own worked example is the evidence, and the example fails the
shipped bar:**

- `living` 18,0 m² took a **second** 1500 window to close a 0,029 gap and landed
  at ratio **0,250** — nearly twice the target, because the increment was a whole
  window rather than a width.
- `kitchen` 9,0 m² landed at **0,120**, *below the floor*, and the example
  described it *"carrying a soft penalty and surviving, which is the correct
  outcome for a real kitchen"*. `win.area_ratio` is now **hard**. That candidate
  is a rejected Plan.
- ⚠️ It also **omitted `bedroom_single`'s window entirely** — four window rows
  counted as two for `living` plus one each for `bedroom_double` and `kitchen`,
  leaving a habitable Room with none, which `win.habitable_has_window` rejects
  hard.

Under the series the four rooms take one window each at 0,175 / 0,169 / 0,200 /
0,160. What is given up is stated: the old rule's even distribution produced a
real façade rhythm, and that argument is refused on measurement — the rhythm is
bought with glazing the room did not ask for, or with a rejection.

### Tier 1, where ADR 0010's handoff is narrowed

⚠️ **ADR 0010 over-reached and this ticket corrects it.** Killing ADR 0004's
party-wall centreline is right — `ümumi sahə` does not do what GIA does, and a
party centreline cannot be taped from inside the flat. But *"the inner ring on
every edge, exterior and party alike"* costs two things it did not price:

1. **Tier 1 would restate a number already on the sheet.** §4.2 requires every
   tier-2 chain to close on the Envelope inner dimension for its axis. Tier 1
   would be that same number on its own rung — the arithmetic debris §4.2 exists
   to prevent.
2. **The sheet would carry no external footprint at all**, and v1 ships houses.
   A house is set out from its footprint.

**Outer face on an exterior edge, inner face on a party edge.** No centreline
survives, every tick stays tapeable, and where both edges on an axis are party
the tier degenerates to `overall = W` — a true statement about a mid-block flat,
not a duplicate. ADR 0010 consequence 6 delegates this section here in terms.

### The four inherited ADR 0010 amendments, all landed

1. Tier-1 centreline exception **deleted**, and narrowed as above.
2. `DIM-CONV` **rewritten, not truncated** — the sentence still has work to do,
   because the tier-1 rule is asymmetric and a Practitioner must be told which
   end is which. General note 2 moves with it.
3. `AREAS` and general note 5 **filled in**: `ümumi sahə`, Area Qaydalar cl. 3.8,
   per cl. 3.2, between finished faces at floor level, skirtings excluded.
4. The room schedule's difference column **named**: it is exactly the internal
   partition footprint, *daxili arakəsmələrin sahəsi*, and the schedule's own
   note says so.

### The room tag, and a clause that had been dropped

✅ **Ladder step 2 loses its invented abbreviation** and takes the room's
**schedule reference**, sourced twice over — `AZS ГОСТ 21.501-2010` cl. 2.3.2(6)
and `ISO 4157-2` cl. 4.3.1–4.3.2, two families sharing no lineage prescribing the
same fallback. `WC` / `ST` / `UT` were plausible-looking inventions the rule's own
wording forbade.

✅ **`room_tag_fallback` splits by audience**, which is what the Homeowner-surface
handoff needed: `practitioner` keeps the room number, `homeowner` **skips to step
4** and leaders the tag into a stacked list beside the plan — reusing the ladder's
own mechanism, so there is one leadering rule and `draw.no_text_overlap`'s
termination argument carries over. The three cheaper options are refused on the
record.

✅ **The name and reference are underlined** (`ISO 4157-2` cl. 4.3.2). ⚠️ The
standard's **lower-right corner** placement is refused, narrowly: that clause
describes a *name and area* tag, ours carries four lines, and §7's centroid
placement is **proved** inside a concave Space where a corner rule is not.

⚠️ **A first-hand clause had been handed to *Area measurement convention* and
dropped.** `AZS ГОСТ 21.501-2010` cl. 2.3.2 annotates a residential plan's area
as a **fraction, living over useful** — *"sahəni kəsr şəklində, surətdə yaşayış,
məxrəcdə isə faydalı sahə göstərilir"*. Ticket 17 closed on `ümumi sahə` as a
single number and **the clause was recorded nowhere in this repo**. Landed here
rather than handed on a third time, because both inputs already exist:
`yaşayış sahəsi` = Σ Space area over habitable Rooms, `faydalı sahə` = Σ all
Space areas. ⚠️ **`faydalı sahə` and `ümumi sahə` are numerically identical in v1
and are not the same quantity** — `ümumi sahə` counts balcony, loggia and eyvan
at a coefficient and v1 models none of the three. **They diverge the day a
balcony is modelled.**

### What the worked example found by being re-derived

⚠️ **§14 was computed at `t_int` = 100 and the profile ships 150.** It could not
be patched: the solve domain is the Envelope dilated by `t_int/2` and must land
on the 250 mm grid, and at 75 mm the old 7900 × 5900 gives 8050 × 6050, which is
not a whole number of cells. The Envelope moved to **7850 × 5850**. Two defects
surfaced only because the numbers were actually run:

⚠️ **The schedule's totals row does not add up, and the Drawing check gains a
twelfth predicate.** Areas render to 2 dp, and a sum of rounded values is not the
rounded sum: the five rooms are exactly 43,575 m², which renders **43,58**, while
the five printed cells add to **43,59**. A Practitioner adds that column. Every
printed total is now computed from the **printed** cells and
`draw.schedule_totals_close` asserts it. It is the area analogue of
`chain_closes`, with the difference that a chain is in integer millimetres and
cannot drift.

⚠️ **§4.5's setting-out datum was ambiguous and its value is a constant.**
`openings.md` §3.1–3.2 push every internal door to one end with a 100 mm jamb
return, so *"the nearest perpendicular face, on the side with more clear space"*
names **opposite ends** on every run longer than `w + 400` — which is every run
that is not exactly minimal. The datum is now the pushed-to end, and the value is
**100 mm for every internal door in every plan**. Kept rather than replaced by a
general note: a note cannot carry *which* end, and which end varies per door with
the walk order. It functions as a **closure check** — a setting-out dimension
reading anything else means placement and drawing disagree.

The example also lands one plan exactly on ADR 0021's revised threshold: door 3's
contact run of 1350 mm **is** `w + t_int + 400`.

### The tier binding, and where the edit had to go

✅ **`ergonomic_check.py` 229/1 → 233/0.** The failure ticket 50 left deliberately
is discharged **at the authoring site** — `build_ergonomic_layer.py`, which
re-authors `hard_reject_below` on every run, so a JSON-only edit reverts. It now
also authors `statutory_floor_binding`, giving the whole `validator_binding` block
one authoring site. Three checks added: the hard tier compares as an **ordered
list**; `statutory_floor_binding` must read `hard`; and the two files must agree
on whether `statutory_floor` rejects. **No field was invented on the `rules.json`
side to make the comparison symmetrical** — membership of `hard_reject_below` *is*
that file's statement of the severity, and a second place to state it is the shape
of defect that produced the check. `gate_check.py` unmoved at 238.

### The 1 650 mm bedroom, handed here by *H8 and the single-aspect flat*

⚠️ **The published minimum is right and the defect is elsewhere. Not taken.**
`bedroom_double.min_clear_short` stays **1 650**. The ergonomic layer is defined
as fixture footprints plus body zone, so it **is** a fits floor by construction
and region-invariant because bodies are; inflating it smuggles a Baku market
judgement into the layer every future region inherits, and **19,3 %** of real
rooms present under 3 000 mm at the façade against **3,1 %** under 1 850.

What survives is **a 1 850 × 5 400 bedroom**: exactly 10,0 m² so
`dim.statutory_min_area` passes, aspect 2,92 against `dim.aspect_ratio_hard` 3,02
so that passes, ergonomic floor passes. **Every hard rule admits a room no
architect would draw**, because nothing between 1 850 and 3 000 costs the solver
anything — and the number that would fix it **already ships and is read by
nobody**: `clear_widths_mm.habitable_room.market_default` = 3 000, with
`soft_objective_target: market_default` naming it, while the only rule consuming
that tier is `dim.market_default_area`, an **area** term. There is no soft rule
on clear width at all. Written into `rules.json`'s `owed` as
**`dim.prefer_wide_habitable`**, soft, because that file is not this ticket's.

### Also landed

- ✅ **`min_pier_mm` 600 → 250**, fitted by ADR 0023 and never written. ⚠️ It now
  **gates nothing** — one window per Space means no shipped path places two
  openings on one run. It binds the day a balcony-door composition is modelled.
- ✅ **The DXF floor is stated as R2007**, correcting this file and
  `bim-cad-export-stack.md`. Nothing shipped was broken — §11 already writes
  R2010 — the **stated** floor was wrong. ⚠️ **A TrueType text style is a
  separate requirement**: every stock SHX font lacks the Azerbaijani letters, and
  the version floor does not fix that.
- ✅ **`DIMDSEP` is plumbed to a formatter**, not only to the dimstyle where it is
  inert at `dimdec = 0`. Three call sites, one function (§1.1).
- ✅ **Əlavə D's seven abbreviations adopted**, `t.d.s.` for `FFL`, and the level
  mark carries three decimals and a comma per cl. 3.3.7.
- ✅ **§7's "not yet confirmed against a drawn example" is discharged** — *Look at
  the converted corpus* rendered 67 dwellings and `render_sheet.py` places the tag
  at the largest constituent rectangle's centroid, citing ADR 0014.

### Declared on resolution

Beyond this ticket's `writes:`, all four unclaimed at the time:

| File | Why |
|---|---|
| `docs/adr/0024-…` | new |
| `docs/spec/openings.md` | §6.1 contradicts a sized window, and its example fails the bar |
| `data/acceptance/rules.json` | three `owed` items discharged, one added, three stale `tier_binding` notes corrected |
| `experiments/region-profile/build_ergonomic_layer.py`, `ergonomic_check.py` | the tier binding's authoring site, and the check ticket 50 left failing |
| `CONTEXT.md` | **Plan mark**, **Product designation**, **Sheet set mark**, **Living area / Useful area** are new; **Type mark** is replaced; **Opening** gains the door/window typing asymmetry |

### What this ticket does not close

- ⚠️ **The message locale schema** over 43 rules is untouched — it is
  `rules.json`'s and merges with `brief.md` §9.4's findings schema.
- ⚠️ **`ОК<n>` is Cyrillic on an otherwise Latin-script sheet.** Followed because
  it is the only published window mark in the family, and labelled `derived`. If
  a first-hand reading of the AZ edition ever turns up a mark, this is a
  one-field change.
- ⚠️ **The 1 850 mm bedroom is still admitted** until
  `dim.prefer_wide_habitable` lands.
