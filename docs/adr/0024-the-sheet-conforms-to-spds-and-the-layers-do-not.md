# The sheet conforms to SPDS and the layers do not

**Status:** accepted
**Date:** 2026-08-27
**Ticket:** *The annotation spec is US-shaped and the drawing is now Azerbaijani*
**Amends:** [ADR 0004](0004-published-dimensions-measure-wall-faces.md) — corrects
its tier-1 rule at the exterior edge;
[ADR 0010](0010-a-space-is-bounded-by-finished-faces.md) — narrows the half of
its centreline argument that over-reached
**Related:** [ADR 0002](0002-annotation-is-derived-not-stored.md),
[ADR 0006](0006-one-shipping-profile-and-it-is-not-the-corpus-region.md),
[ADR 0012](0012-one-vertical-datum-and-it-is-the-clear-height.md),
[ADR 0021](0021-a-door-is-placed-by-walking-in-and-none-swings-into-circulation.md),
[ADR 0023](0023-a-measured-threshold-is-not-an-engine-choice.md)

`annotation.md` fixed the sheet set, the title block, the three drawn schedules
and the layer names **before any region profile existed**, and reached for the
conventions nearest to hand: US NCS sheet numbers, AIA layer names, `FFL`,
`D1`/`W2` opening marks. *The Azerbaijani region profile* then fixed the
drawing's language as **Azerbaijani** and read `AZS ГОСТ 21.101-2010` and
`21.501-2010` first-hand. Neither ticket was wrong. The seam between them was
unowned, and a drawing issued in Azerbaijani to an Azerbaijani builder with a US
sheet number is internally inconsistent in a way the builder notices before
reading a single dimension.

## The decision

**Everything a person reads on the sheet conforms to SPDS. The layer names do
not.** The dividing line is stated once and used everywhere:

> **A sheet mark is read on paper by a builder. A layer name is read on import by
> a program.**

Nine things move, and the tenth deliberately does not.

1. **Sheet marks.** The set is `MH` (*Memarlıq həlli*), Əlavə A, and sheets are
   numbered sequentially within it — `<job>-MH`, *Vərəq 1 / 2*. This is not a
   letter swap: SPDS carries the designation on the **set** where NCS puts a
   discipline letter and a series number on each **sheet**, so `A-101` does not
   become `MH-101`.
2. **Abbreviations.** Əlavə D's seven published values, for the seven the spec
   actually consumes: `t.d.s.` for `FFL`, `M` for scale, `əd.`, `sh.`, `mər.`,
   `y.s.`, `san. qov.` Marked *tövsiyə olunan* — permitted, not mandated —
   and adopted because a drawing that abbreviates in English while writing
   Azerbaijani is the incongruity this ADR exists to remove.
3. **The opening mark scheme becomes two-level.** A plan mark in a Ø 5 mm circle
   — windows `ОК<n>`, doors a bare number, two separate number spaces — joins
   the plan to the schedule on `(kind, n)`; the GOST product designation
   (`ДГ 21-8`) moves to the schedule's `Type` column. `D1` / `W2` matched no
   published convention in any family this profile draws on.
4. **The opening catalogue's `conf` is split.** Each entry's dimensions stay
   `verified` — they were read off the GOST size drawings and that reading is
   still true. The **selection** becomes `engine_choice`: `ГОСТ 6629-88` is
   superseded and its live successor `ГОСТ 23166-99` cl. 4.9 makes the opening
   grid a **project decision**, so no instrument fixes it.
5. **A window is sized, not picked.** `window_for_room` becomes
   `erg_key → (height, width series)`; height is fixed per room family and the
   width is the smallest series member reaching the glazing target. This is what
   makes a hard `win.area_ratio` satisfiable, and §"Why the series had to be
   extended" below is where the decision is genuinely uncomfortable.
6. **The hard tier binding becomes a list**, `["ergonomic", "statutory_floor"]`,
   and `statutory_floor_binding` moves `warn` → `hard`, both at the **authoring
   site** — `build_ergonomic_layer.py`, not the JSON.
7. **Tier 1 measures the outer face of an exterior edge and the inner face of a
   party edge.** See below; this corrects ADR 0004 and narrows ADR 0010.
8. **The decimal comma is plumbed to a formatter, not only to `DIMDSEP`**, which
   is inert at `dimdec = 0`.
9. **The room tag's degradation ladder loses its invented step and gains an
   audience split**, and the plan gains the dwelling area fraction
   `yaşayış sahəsi / faydalı sahə` that `AZS ГОСТ 21.501-2010` cl. 2.3.2
   prescribes for a residential plan.

**Layer names stay `A-WALL`, `A-ANNO-DIMS`, US NCS / AIA.** Their consumer is
AutoCAD, Revit and ArchiCAD, every one of which ships NCS/AIA templates and none
of which resolves a transliterated Azerbaijani taxonomy. `annotation.md` §11
already carried this justification — *a Practitioner recognises the real ones on
import* — and Azerbaijani-language output does not weaken it.

Two limits on that reasoning, so it is not read as a general licence. It is a
claim about **interchange**, not about correctness, so a profile shipping to a
market whose tools expect otherwise re-opens it. And it is **not** evidence that
other US defaults may stay: sheet marks, abbreviations, the mark scheme and the
separator all moved. An exception used twice stops being one.

## Why there is no `drawing` convention object, and the profile grew fields anyway

The ticket warned: *do not answer this by adding fields one at a time; that is
how the US-shaped default got in.* The answer is that the profile **already has**
a `drawing` block, and what was missing was not a container but a **rule for what
belongs in it**. That rule is the dividing line above, and it is now written into
the block itself. A field is region-parameterised **iff a person reads it**.

Under that rule the block is complete rather than growing: sheet marks, level
abbreviation, decimal separator, thousands separator, mark scheme, room-name
vocabulary and tag fallback are all human-facing and all in it; layers,
lineweights, text heights, ISO 3098 sizes and the DXF version floor are all
machine-facing or physical and all stay in the spec. The next person adding a
field has a test to apply rather than a precedent to follow.

## Why the series had to be extended past what GOST publishes

This is the weakest part of the decision and it is stated plainly rather than
buried.

`win.area_ratio` is now **hard**. Against the three-entry catalogue it fails
**21,20 %** of real dwellings; against a width series, **5,39 %**. *A statutory
floor, posted soft, in the one region v1 ships* wrote that a published series
would be *"engine_choice bounded by `gost_11214_86`, and more defensible than
three fixed entries"*.

**It cannot be bounded by `gost_11214_86`, because the published widths run out
at 21 dm and the same ticket's measured reach requirement is p90 3,23 m for
`living_dining`** — 1 130 mm above anything GOST prints. So members through 2100
sit on the published grid and 2400 / 2700 / 3000 / 3300 are an engine extension
of it. `published_through` marks the boundary in the data, and above it the
schedule prints a plain dimension string rather than a fabricated `ОР 15-27`,
because inventing a standard designation is the same failure as an invented room
abbreviation.

Three alternatives were weighed:

- **Raise the height instead.** cl. 9.13 is an area ratio, so a taller window
  needs less width — but at H 1800 `living_dining` still needs 2 692 mm, outside
  the published series, so it does not even solve the problem. It also is not
  free: `sill = head_datum_mm − H`, so H 1800 puts the sill at 400 mm and
  re-opens a guarding question `fall_barrier_when_required` **refuses** to
  evaluate, v1 having one Storey at elevation 0 and no site.
- **Keep the published top and allow a second window.** Never invents a size,
  and it is the one option that stays entirely inside a published document.
  Refused: a Baku *zal* is glazed as one unit; real AZ construction is ungridded
  PVC, which is exactly what cl. 4.9 anticipates; and it makes `min_pier_mm`
  load-bearing after ticket 50 established it was not.
- **Leave `win.area_ratio` soft.** Not available — that severity is a settled
  decision with a published corpus cost.

**One correction to ticket 50 falls out of this.** It wrote that splitting into
two openings *"buys nothing — total glazing width is fixed and the pier is pure
loss"*. That is true when the **wall run** binds and false when the **catalogue
top** binds, where a second opening is the only way past it. The two cases had
not been distinguished. The extension removes the second case, which is what
lets one-window-per-Space stand.

## Why tier 1 is asymmetric

ADR 0004 kept one centreline number: tier 1 measured a party edge to its
centreline, *"because GIA and IPMS both do"*. ADR 0010 killed it, correctly —
`ümumi sahə` stops at the finished inner face and does not do what GIA does, and
**a party wall's centreline cannot be taped from inside the flat**, which ADR
0004's own thesis forbids.

ADR 0010 then wrote that tier 1 *"now measures the Envelope's inner ring on every
edge, exterior and party alike"*, and that half over-reached. Two consequences it
did not price:

1. **Tier 1 would restate a number already on the sheet.** `annotation.md` §4.2
   requires each tier-2 chain to close on the Envelope inner dimension for its
   axis. If tier 1 is that same dimension, the overall is the same number drawn
   again on its own rung — the arithmetic debris §4.2 exists to prevent.
2. **The sheet would carry no external footprint at all**, and v1 ships houses as
   well as flats. A house is set out from its footprint.

Killing the centreline does not require abandoning the outer face. **Outer face
on an exterior edge, inner face on a party edge**: every tick stays tapeable, no
centreline survives, and where both edges on an axis are party the tier
degenerates to `overall = W` — which is a true statement about a mid-block flat,
not a duplicate.

ADR 0010 consequence 6 delegates this section to this ticket in terms, so the
correction is made here rather than owed back.

## Consequences

1. **`annotation.md` moves in twelve sections** — 1, 1.1 (new), 3, 3.1–3.2 (new),
   4.1, 4.5, 6, 7, 7.1–7.2 (new), 8, 9, 10, 11, 13, 14. Its worked example is
   **re-derived at `t_int` = 150**, the shipped value; it had been computed at
   100 and could not be patched, because the solve domain is the Envelope dilated
   by `t_int/2` and must land on the 250 mm grid. The Envelope moved 7900 × 5900
   → **7850 × 5850** so that it does.
2. **The Drawing check gains a twelfth predicate**, `draw.schedule_totals_close`.
   Working the example found that a totals row computed from exact areas
   disagrees with the column printed above it — 43,58 against 43,59 — because
   areas render to 2 dp and a sum of rounded values is not the rounded sum. Every
   printed total is now computed from the printed cells. This is the area
   analogue of `chain_closes`, and it is the only Drawing predicate whose failure
   is invisible in the geometry and visible only to a person adding a column.
3. **`openings.md` §6.1 is rewritten by a ticket that does not hold it.** Its
   fixed-size, variable-count rule contradicts the sized window, and its own
   worked example is the evidence: `living` reached ratio **0,250** — nearly
   twice the target, because the increment was a whole window — and `kitchen`
   reached **0,120**, *below the now-hard floor*, described as surviving on a
   soft penalty. **The shipped spec's own example fails the shipped bar.** The
   example also omitted `bedroom_single`'s window entirely, which
   `win.habitable_has_window` rejects hard. Both corrected.
4. **`§4.5`'s setting-out datum was ambiguous and is now a constant.**
   `openings.md` §3.1–3.2 push every internal door to one end with a 100 mm jamb
   return, so *"the nearest perpendicular face, on the side with more clear
   space"* names opposite ends on every run longer than `w + 400`. The datum is
   now the pushed-to end, the value is **100 mm for every internal door in every
   plan**, and the dimension is kept as a closure check rather than deleted —
   a general note cannot carry *which* end, and which end varies per door.
5. **`ergonomic_check.py` goes 229/1 → 233/0.** The deliberate failure ticket 50
   left is discharged, and three checks are added: the hard tier compares as an
   ordered **list**, `statutory_floor_binding` must read `hard`, and the two
   files must agree on whether `statutory_floor` rejects. `gate_check.py` is
   unmoved at 238.
6. **`min_pier_mm` is 250, and it gates nothing.** Fitted by ADR 0023 and never
   written; written here. One window per Space means no shipped path places two
   openings on one run. It binds the day a balcony-door composition is modelled.
7. **The DXF version floor is stated as R2007**, correcting `annotation.md` §11
   and `bim-cad-export-stack.md`. Measured, not argued: no legacy code page
   encodes `ə`, not even cp1254, and cp1251 cannot encode `²`. Nothing shipped
   was broken — the spec already writes R2010 — but the **stated** floor was
   wrong. A TrueType text style is a separate requirement and is not solved by
   the version floor.
8. **The plan gains a dwelling-level area annotation and it had been dropped.**
   `AZS ГОСТ 21.501-2010` cl. 2.3.2 prescribes the area as a fraction, living
   over useful, on a residential plan. The region-profile research flagged it for
   *Area measurement convention*; that ticket closed on `ümumi sahə` as a single
   number and **the clause was recorded nowhere in this repo**. Landed here
   rather than handed on a third time, because both inputs already exist:
   `yaşayış sahəsi` is Σ Space area over `is_habitable` Rooms, `faydalı sahə` is
   Σ all Space areas. ⚠️ **`faydalı sahə` and `ümumi sahə` are numerically
   identical in v1 and are not the same quantity** — `ümumi sahə` counts balcony,
   loggia and eyvan at a coefficient and v1 models none of the three. They
   diverge the day a balcony is modelled.
9. **`win.area_ratio`'s Homeowner-visible failure mode changes shape.** A Space
   that cannot be glazed on its run now fails **hard at placement**, with the run
   and the smallest member both known. That is a better diagnosis than the old
   silent under-glazing, and `homeowner-surface.md` §7's zero-survivor path is
   where it surfaces.
