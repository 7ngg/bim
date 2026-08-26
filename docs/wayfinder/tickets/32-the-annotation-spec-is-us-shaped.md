---
id: 32
title: The annotation spec is US-shaped and the drawing is now Azerbaijani
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - docs/spec/annotation.md
  - data/standards/room-constraints.json
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
