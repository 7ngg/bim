---
id: 32
title: The annotation spec is US-shaped and the drawing is now Azerbaijani
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
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
