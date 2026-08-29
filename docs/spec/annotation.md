# Drawing spec: graphics, dimensioning, annotation, schedules

How a `Drawing` is derived from a `Plan`. Resolves *Dimensioning and annotation
rules* and *The annotation spec is US-shaped and the drawing is now Azerbaijani*.
Companion to [ADR 0004](../adr/0004-published-dimensions-measure-wall-faces.md)
and [ADR 0024](../adr/0024-the-sheet-conforms-to-spds-and-the-layers-do-not.md).

> **This document was written before any region profile existed** and reached for
> the conventions nearest to hand — US NCS sheet numbers, AIA layer names, `FFL`,
> `D1`/`W2` opening marks. *The Azerbaijani region profile* then fixed the
> drawing's language as Azerbaijani and read the Azerbaijani drafting standards
> first-hand. ADR 0024 resolves the seam: **everything a person reads on the
> sheet conforms to `AZS ГОСТ 21.101-2010` / `21.501-2010`; the layer names do
> not, and §11 says why.** Sections 1, 3, 4.1, 4.5, 6, 7, 8, 9, 10, 11, 13 and 14
> all moved.

**The standard this is held to is a Practitioner's own output.** Not "readable",
not "close enough for a Homeowner" — a set an architect would issue. Where a rule
below is more work than an alternative, that is not a reason to prefer the
alternative. C2 makes the Homeowner the buyer and the Practitioner the standard,
and this document is where that standard is cashed.

Every number is in integer millimetres unless suffixed `paper` — a paper-space
millimetre, which becomes a model millimetre by multiplying by the plot
denominator.

---

## 1. One Drawing, two presentations, two sheets

A `Drawing` is a Plan, a **Sheet set**, and one resolved annotation set. Each
annotation element carries an **audience**: `both` or `practitioner`. A render
target draws the elements tagged for it and nothing else.

| Element | Audience |
|---|---|
| Plan graphics: poché, door swings, glazing (§2) | `both` |
| Room tag (name, area, clear dims) | `both` |
| Dwelling area fraction (§7.2) | `practitioner` |
| Dimension chains, tiers 1 / 2 / 2b / 3 (§4) | `practitioner` |
| Internal setting-out dimensions (§4.5) | `practitioner` |
| Opening plan marks (§8) | `practitioner` |
| Title block, revision block, general notes, north arrow, scale bar | `practitioner` |
| Schedules (§6) | `practitioner` |

The eager SVG preview renders `both`. The lazy DXF/PDF renders everything. One
derivation, one override key space, no second annotation engine to drift against
the first.

**The sheet set is two sheets, not one:**

| Sheet | Content |
|---|---|
| `MH` sheet 1 of 2 | General arrangement plan, dimensioned and annotated |
| `MH` sheet 2 of 2 | Door schedule, window schedule, room schedule |

A single-sheet set with schedules crammed into the plan margin is what a
generator produces. A set is what a practice issues.

**The set mark is `MH`, not `A`, and the sheets are numbered sequentially** —
`AZS ГОСТ 21.101-2010` Əlavə A, where architectural working drawings are `MH`
(*Memarlıq həlli*) or `MT` (*Memarlıq-tikinti həlləri*). This is **not a letter
swap**: SPDS carries the designation on the *set* and numbers sheets `1 … N`
within it, where NCS puts a discipline letter and a series number on each sheet.
So `A-101` and `A-102` do not become `MH-101` and `MH-102`; they become
`<job>-MH`, *Vərəq 1* and *Vərəq 2*. ADR 0024, and §10's title block carries both
halves in separate attributes.

Throughout this document a sheet is referred to by its number in that set. Where
an older ticket or ADR says `A-101` it means sheet 1 and `A-102` means sheet 2.

**Units differ by target, and that is safe only because of one invariant:**

> **A dimension rendered in any unit other than integer millimetres may not be
> part of a chain.**

The preview renders metres to 2 dp (`4,35 × 3,60 m`) and draws no chain. The
sheets render integer millimetres with no unit suffix (`4350`) and draw every
chain. Integer millimetres sum exactly, so a chain closes by construction; the
moment a number is rounded for display it is barred from a chain. The classic
embarrassment — a chain that does not add up — is unreachable rather than
guarded against.

Areas render as m² to 2 dp.

### 1.1 Every number goes through one formatter

The **decimal separator comes from the region profile** and is written to
`DIMDSEP`. For `AZ` it is a comma — `azs_21101_2010` cl. 5.12, corroborated by
CLDR's `az` locale — and there is **no thousands grouping**:
`profiles.AZ.drawing.thousands_separator` is `null` because CLDR gives `.` as the
`az` group separator, so a grouped `4.400` reads as a decimal to the person the
sheet is for. Never group, on the sheet or in the preview.

> **`DIMDSEP` is inert as this document is written, and setting it is not
> enough.** §11 sets `dimdec = 0`, so a rendered dimension is `4400` with no
> decimal for the separator to sit in — verified by rendering at both `DIMDEC = 0`
> and `DIMDEC = 2` through ezdxf and reading the text back out of the anonymous
> block. The separator's real consumers are the strings **we** format: the room
> tag's area, the level mark, the schedule cells, and the preview's metre
> dimensions.

So the profile field is plumbed to **one formatter**, and every rendered number in
this document and in `homeowner-surface.md` goes through it. `DIMDSEP` is set as
well — it is correct, and it matters the moment someone edits the file downstream
— but it is never the *only* place the profile is read, or the convention
silently never fires. Three call sites, one function:

| String | Example (`AZ`) |
|---|---|
| Area, 2 dp | `15,66 m²` |
| Level mark, 3 dp | `±0,000` |
| Preview metre dimension, 2 dp | `4,35 × 3,60 m` |

Integer millimetres contain no separator and are unaffected, which is why the
chain invariant above is independent of locale.

---

## 2. Plan graphics

Annotation sits on top of a drawing, and the drawing is judged first. A plan with
perfect dimensions and a flat single-weight linework reads as generated at a
glance, before a single number is checked.

### Lineweight hierarchy

The hierarchy expresses **what the cutting plane passes through**. This is the
oldest convention in architectural drawing and the fastest tell when it is
missing.

| Content | Layer | Lineweight |
|---|---|---|
| Cut: wall bodies, cut columns | `A-WALL` | 0.50 |
| Cut: door frames, window frames | `A-DOOR`, `A-GLAZ` | 0.25 |
| Uncut in elevation/projection: door leaves, swing arcs, glazing line | `A-DOOR`, `A-GLAZ` | 0.18 |
| Poché hatch | `A-WALL-PATT` | 0.09 |
| Dimension lines, extension lines, leaders | `A-ANNO-DIMS` | 0.13 |
| Text, tags, notes | `A-ANNO-TEXT` | 0.18 |
| Title block, north arrow, scale bar, schedule rules | `A-ANNO-TTLB` | 0.18 |

Lineweights are an enumerated DXF set in units of 1/100 mm. Every value above is
in it; an arbitrary 0.45 mm is not, and the pen table must snap. `$LWDISPLAY = 1`
or none of it displays.

### Poché

Cut walls are filled **solid** (`HATCH`, `SOLID`, external boundary path plus
inner island paths — the island support was verified). Material-differentiated
hatching (masonry, insulation, stud) belongs to 1:20 details and is out of v1
scope; solid poché is correct and standard at 1:50 and 1:100.

### Doors

Leaf drawn at **90° open**, perpendicular to the wall, plus the quarter-circle
swing arc from the hinge. Both on `A-DOOR` at 0.18; the frame at the reveal on
0.25. A **cased opening** draws the void and the frame lines and **no leaf and no
arc** — which is what makes it legible as a cased opening rather than a missing
door.

The swing drawn is the *leaf* swing. The `Swing footprint` in the model is the
conservative bounding square used for clearance checks, and is never drawn.

### Windows

Frame lines at both wall faces (0.25) plus a single centred glazing line (0.18)
running the structural opening. Sill and head are not shown in plan.

### Levels and what is deliberately absent

`t.d.s. ±0,000` is annotated once on the plan, on `A-ANNO-TEXT` (§10 note 4,
`AZS ГОСТ 21.101-2010` Əlavə D). Ceiling height goes
in the general notes.

Not drawn, and each is a stated absence rather than an oversight: floor finishes
and thresholds (no finishes model), structural grid (a single dwelling does not
carry one), fixtures and furniture (not modelled — see the map's fog), and any
hatch pattern implying a material specification.

---

## 3. What is measured to

**Every published dimension measures a wall face. There is no centreline
dimension anywhere on the sheet.** Rationale and the rejected alternative:
ADR 0004, as amended by
[ADR 0010](../adr/0010-a-space-is-bounded-by-finished-faces.md) and
[ADR 0024](../adr/0024-the-sheet-conforms-to-spds-and-the-layers-do-not.md).

- A **witness** is a line a dimension is measured to. Every witness is a wall
  face, in clear coordinates.
- A tier-2 chain therefore alternates: room clear width, wall thickness, room
  clear width, … Every tick is a real quantity a person can tape.
- **Tier 1 spans the footprint, and its two ends are not symmetrical.** It
  measures to the **outer face of an exterior edge** and to the **inner face of a
  party edge**. A party wall's outer face lies inside the neighbour's home and
  cannot be taped from this dwelling; an external wall's outer face can be taped
  from the street, and for a house it is the number the building is set out from.

Tier 1 for a rectangular Envelope of inner width `W`, west edge exterior of
thickness `t_w`, east edge party of thickness `t_e`:

```
overall_x = W + t_w
```

### 3.1 Why tier 1 is not the inner ring on both edges

ADR 0004 kept exactly one centreline number — tier 1 measured a party edge to its
centreline, *"because GIA and IPMS both do"* — and committed the rule to follow
*Area measurement convention*. That ticket landed on `ümumi sahə`, which stops at
the finished inner face and does not do what GIA does, so **the authority for the
exception is gone and the exception is deleted.** The centreline was also always
in tension with ADR 0004's own thesis, that *every tick is a number a person can
tape*.

ADR 0010 then wrote that tier 1 *"now measures the Envelope's inner ring on every
edge, exterior and party alike"*, and **that half over-reached.** Two consequences
it did not price:

1. **Tier 1 would restate a number already on the sheet.** §4.2 requires each
   tier-2 chain to close on the Envelope inner dimension for its axis. If tier 1
   is also the inner dimension, the overall dimension is the same number drawn a
   second time on its own rung — the arithmetic debris §4.2 exists to prevent.
2. **The sheet would carry no external footprint at all.** v1 ships houses as
   well as flats (C13, the Destination). A house is set out from its footprint,
   and a general arrangement that omits it is not a set an architect would issue.

Killing the *centreline* does not require abandoning the *outer face*. The rule
above keeps every tick tapeable — the outer face of an external wall from
outside, the inner face of a party wall from inside — carries no centreline, and
degenerates correctly: where both edges on an axis are party, `overall = W`, and
tier 1 is then genuinely saying that this flat's footprint on that axis *is* its
inner dimension. That is a true statement about a mid-block flat, not a
duplicate.

ADR 0010 consequence 6 delegates this section to this ticket in terms, so the
authority to make the correction is here rather than owed back.

### 3.2 Every thickness is even, and it binds the totals

ADR 0001 needs `erode(rect, t/2)` in integer millimetres. **Every wall thickness
total in a region profile must be an even number of millimetres** — 100 / 120 /
140 / 150 / 200 / 240 / 280 / 300 are fine; 115 mm half-brick and 125 mm DIN 4172
octametric are not, because they put every wall face on a half-millimetre. ADR
0010 sharpens which number the rule binds: the **total**, which is what gets
halved, and never a layer component, which only ever enters a total doubled. A
15 mm finish is legal and a 15 mm wall is not.

Tier 1 no longer halves anything, so the rule now rests on `erode` alone.

---

## 4. Dimensions

Four external tiers on a **ladder** — rungs at fixed offsets outside the Envelope
bounding box — plus in-plan setting-out dimensions for internal openings. Rungs
are allocated outward in this order; a tier absent on a side consumes no rung.

| Tier | What | Rung |
|---|---|---|
| 3 | Openings on this Envelope edge | 10 mm `paper` |
| 2 | Partition faces on walls reaching this side | 18 mm `paper` |
| 2b | Running dimensions from datum, only if needed | 26 mm `paper` |
| 1 | Overall footprint | 26 or 34 mm `paper` |

### 4.1 Tier 1 — overall

One per side, all four sides. Footprint span, per §3 — **outer face on an
exterior edge, inner face on a party edge.** A side's tier-1 value is therefore
not generally equal to the span its tier-2 chain closes on, and where it is, that
side is party at both ends and the equality is the finding.

### 4.2 Tier 2 — one chain per side

A side's tier-2 chain dimensions **only the partition faces on walls that reach
that side**, and all four sides carry one.

This departs from the "chains on two adjacent sides" shortcut deliberately.
Projecting every partition in the plan onto two sides produces ticks that
correspond to no room and no wall present on that elevation — arithmetic debris,
and the sort of thing that tells a Practitioner immediately that no one drew
this. Restricting each side to the walls that touch it makes **every tick a real
clear dimension of a real room**, and each of the four chains still closes on the
Envelope inner dimension for its axis.

### 4.3 Tier 2b — running dimensions from datum

A partition reaching **no** Envelope edge appears on no tier-2 chain. Each such
face gets a **running dimension** from the Envelope inner face on the nearest
side — standard setting-out practice, on its own rung.

This is what makes `draw.every_wall_face_dimensioned` a hard predicate rather
than a hope: the fallback always applies and never collides.

**Measured, and it is not a fallback.** *Solver timing variance sweep* counted
tier-2b partitions over 159 solved Plans: **2 walls of 7 at 8 rooms, 4 of 11 at
12, and 10 of 21 at 24.** Nearly half of a large plan's partitions reach no
Envelope edge, so the 2b rung is occupied on most sides in the common case and
**tier 1 sits at 34 mm rather than 26 mm by default**. Size the sheet for 34
unless a plan is measured to need less; do not treat 26 as typical.

### 4.4 Tier 3 — openings on Envelope edges

One chain per Envelope edge holding an Opening — windows and the entrance door
alike — measured **jamb to jamb**, to the structural opening edges. Jambs chain
and sum; a centre mark cannot be chained unambiguously. The chain runs datum to
datum across the full Envelope inner dimension, so it closes like the others.

### 4.5 Internal openings — in-plan setting-out dimensions

**Every internal opening is dimensioned.** Not noted, not implied by a
convention: dimensioned, because a builder sets out from these and a
Practitioner checking the plan looks for them.

Rule: a short dimension drawn **inside the plan**, from the finished face of the
**perpendicular wall at the end the door is pushed to** to the **near jamb of the
structural opening**, offset 3 mm `paper` from the host wall face, text above the
line.

> **The datum was "the nearest perpendicular wall face, on the side with more
> clear space", and that rule is both ambiguous and dead.** `openings.md` §3.1
> pushes every internal door to one end of its run and §3.2 fixes a 100 mm jamb
> return at that end, so the nearest perpendicular face is *always* the pushed-to
> end and the two clauses can never disagree — but they can never be read
> together either, because "nearest" and "more clear space" name opposite ends
> whenever the run is longer than `w + 400`, which is every run that is not
> exactly minimal. Naming the pushed-to end directly is the same geometry with
> one reading.

**The value is 100 mm for every internal door in every plan**, by construction
from `openings.md` §3.2. It is dimensioned anyway, and this is a deliberate
choice rather than an oversight:

- It is what a builder sets out from, and a set-out dimension a builder can tape
  is the standard §0 holds this document to.
- Its constancy makes it a **closure check**: a setting-out dimension reading
  anything other than 100 means the placement and the drawing disagree, which is
  precisely the stale-block class of failure `draw.measurement_matches_model`
  exists for. A number that is always the same is still worth drawing when the
  drawing is the only place the disagreement would show.
- The general-note alternative — *"all internal openings set out 100 mm from the
  perpendicular face at the hinge end"* — cannot carry **which** end, and which
  end varies per door with `openings.md` §3.1's walk order. The note would be
  true and still leave the plan unable to say where a door is.

Consequence, taken deliberately: annotation now lives inside the plan, so
collisions inside the plan are real (§5).

### 4.6 The chain closes

Every chain's segments sum exactly to its axis span, in integer millimetres,
enforced by `draw.chain_closes`. There is no rounding step at which this can be
lost.

---

## 5. Collision

The ladder removes the collisions it can. Chains sit outside the Envelope bbox,
so chain-vs-plan and chain-vs-chain are impossible by construction, and one tag
per Space makes tag-vs-tag impossible. What remains is genuine and is handled by
rule, not by a global solver.

**Priority, and it decides every case: information outranks labelling. A
dimension never moves for a tag. The tag moves.**

### (a) A chain segment narrower than its own text

Frequent by construction: every tier-2 wall-thickness tick is `t_int`, which at
1:50 is 2 mm `paper` against 2.5 mm text.

> If a segment's span in `paper` mm is less than the rendered text width plus
> 2 × `DIMGAP`, place the text outside the extension lines with a leader. When
> two consecutive outside texts would themselves overlap, alternate them above
> and below the dimension line.

Arithmetic, not search. Both operands are known before anything is drawn.

**The first sentence fires constantly; the second never fires.** *Solver timing
variance sweep* measured 6 to 13 outside-text placements per plan from 8 to 24
rooms — every `t_int` tick, as expected — and **zero consecutive-outside-text
collisions in 159 plans**. The above/below alternation is unreachable at every
size v1 ships. Keep it in the spec as the rule it is, but **do not build it for
v1**; assert instead that the collision count is zero and revisit if that ever
trips.

**We compute the placement; the dimstyle only declares it.** ezdxf renders
dimension geometry into an anonymous block, and that block is what most viewers
show. Placement is passed explicitly via `add_linear_dim(location=…)`, and
`DIMATFIT` / `DIMTMOVE` are set to match so an app that regenerates
(`$DIMASSOC` is written as 2) reaches the same answer rather than a different
one.

### (b) A room tag against an in-plan dimension, a wall, or an opening

The §7 degradation ladder, applied to the tag.

### (c) An in-plan setting-out dimension against another

Two openings on perpendicular walls meeting at a corner can crowd. The
dimension on the **longer** wall keeps its offset; the other steps out one
further 3 mm `paper` increment. Deterministic, and it never drops a dimension.

### (d) Sheet furniture

Fixed paper-space positions. Title block bottom right, revision block above it,
north arrow and scale bar above that, general notes on the left of the strip.

---

## 6. Schedules

**v1 ships drawn schedules on sheet 2.** ezdxf has no `ACAD_TABLE` entity,
so a schedule is composed from `LWPOLYLINE` rules and `MTEXT` cells. That is a
table layout component to build; it is not a reason to omit the schedules. It is
also the single thing the competitive scan found **no vendor documents at all**,
across eleven products and four price tiers.

Header row 3.5 mm `paper` text on a 0.25 rule; body rows 2.5 mm on 0.13 rules;
column widths from the widest cell, rounded up to 5 mm `paper`.

**Our columns diverge from the published form, and the divergence is chosen.**
`AZS ГОСТ 21.501-2010` cl. 2.3.6(2) defers the opening schedule to `ГОСТ 21.101`
Annex 7, forms 7 or 8, whose columns are `Поз. | Обозн. | Наименование | Кол. |
Масса | Примеч.` with the opening size carried in the *notes* column and a mass
column we cannot populate. We put the size in its own column and carry no mass.
Stating this here rather than silently mismatching: the columns are ours, chosen
by our schema, which is also the correct copyright posture. Column headings are
Azerbaijani and use Əlavə D's published abbreviations where the spec consumes one
— `əd.` for a quantity, `sh.` for an area.

### Door schedule

| Mark | Type | Structural opening W × H | Leaf W × H | Handing | Swing | Notes |
|---|---|---|---|---|---|---|

`Mark` is the **plan mark** (§8) — a bare sequential number for a door — and it
is the join key. `Type` is the **product designation**, the region profile
catalogue entry's GOST string (`ДГ 21-8`), which is what tells a builder what to
buy. Handing and swing come from *Opening placement rules*. A **cased opening**
has no leaf and no handing; those cells read `—`, never blank, so a missing value
is distinguishable from an inapplicable one.

### Window schedule

| Mark | Type | Structural opening W × H | Sill height | Fall barrier | Notes |
|---|---|---|---|---|---|

`Mark` is `ОК<n>`; `Type` is the derived GOST designation, **height-then-width in
decimetres** — a 1500 × 1350 opening is `ОР 15-13,5`, and the fractional
decimetre group takes a comma, which the standard itself prints (`ОС 15-13,5`,
`БС 22-7,5`).

> **Above the published series the `Type` cell carries no designation.** A window
> width is now selected from `profiles.AZ.openings.width_series_mm` (§8), whose
> members above `published_through` = 2100 are an engine extension of the GOST
> grid rather than entries in it. For those the cell carries the plain opening
> dimension string — `1500 × 2700` — and **never** a fabricated mark like
> `ОР 15-27`. Inventing a standard designation for a size the standard does not
> publish is the same failure as an invented room abbreviation, and §7 deleted a
> whole ladder step over exactly that.

`Fall barrier` carries the guarding height where the model holds one, and `—`
where it does not — the two are separate model values precisely because one
number cannot serve both. In v1 it is `—` for every window:
`fall_barrier_when_required` refuses the trigger, because whether a window is a
place with a risk of falling depends on the drop below it and v1 has one Storey
at elevation 0 with no site.

### Room schedule

| Ref | Room | Clear dimensions | Area |
|---|---|---|---|

`Clear dimensions` carries **every leg**, `4400 × 3400 + 2100 × 1800` for a
two-rectangle Room (ADR
[0014](../adr/0014-a-room-is-one-or-two-rectangles-and-the-proposal-decides.md)),
in descending area order. `Area` is the Room's, over the union, so the two
columns are not multiplicands of each other for an L and are not meant to be.

Totals row: sum of Space areas, and the Envelope inner area, both stated. They
differ by the partition footprint, and showing both is how a Practitioner
reconciles the schedule against the plan.

**The difference column is now a named quantity, and it improves.** Under
ADR 0010 the measured area is `ümumi sahə`, which sums Space areas and does not
count partitions, so the gap between the two totals is **exactly the internal
partition footprint**. It stops being a curiosity and becomes the reconciliation
line a Practitioner checks first. The schedule's own note says so, and names it:
*daxili arakəsmələrin sahəsi*.

> **The totals row sums the printed cells, not the exact values, and this is not
> a rounding nicety.** Areas render to 2 dp, and a sum of rounded values is not
> the rounded sum: §14's five rooms are exactly 43,575 m², which renders as
> **43,58**, while the five printed cells add to **43,59**. A Practitioner adds
> that column. A totals row that disagrees with the column above it by 0,01 is
> the arithmetic-debris tell this document exists to avoid, and it is the same
> failure class as a chain that does not close — with the difference that a chain
> is in integer millimetres and cannot drift, while an area is not and can.
>
> So: **every printed total is computed from the printed cells.** The difference
> row is printed-minus-printed. `draw.schedule_totals_close` (§13) asserts it.
> The exact values are never shown, so nothing on the sheet contradicts anything
> else on the sheet.

**No fire, thermal, acoustic or structural columns.** Not omitted for effort —
excluded because C8 forbids the claim, and a `TBC` in a fire-rating column is a
claim that someone will fill it in.

---

## 7. Room tags

Placement is the centroid of the Space's **largest constituent rectangle**.
**The largest-inscribed-circle machinery is still not needed and is still not
specified** — the largest part is a rectangle and its centroid is exact and
inside it.

> That day arrived: ADR
> [0014](../adr/0014-a-room-is-one-or-two-rectangles-and-the-proposal-decides.md)
> makes a Space up to two rectangles, so this section's *"no v1 Space is concave
> and the centroid is exact"* is gone. Taking the **Room's** centroid would be
> the bug it warned about, and it is not hypothetical: for a 6.0 × 1.2 m leg
> with a 1.2 × 6.0 m return, the Space centroid lands at (1 800, 2 400) —
> **outside its own Space**, in the notch, which belongs to a different room, so
> the tag would name the neighbour. Asserted in
> `experiments/room-rectangles/erosion_check.py`; the larger part's centroid is
> inside by construction.

✅ **Now confirmed against a drawn example.** *Look at the converted corpus*
rendered 67 converted dwellings beside their originals
(`experiments/rectangularise/render_sheet.py`, which places the tag at the
largest constituent rectangle's centroid and cites ADR 0014 for it), so the
legibility question ticket 28 item 4 raised has been looked at rather than
reasoned about. Correctness was never in doubt — the containment is proved in
`experiments/room-rectangles/erosion_check.py`.

**The dimensions line carries both legs**, `4400 × 3400 + 2100 × 1800`. Never the
bounding box: a bbox claims floor area the Room does not have, next to an area
figure that does not include it, which is the kind of arithmetic a Practitioner
checks first. The degradation ladder below is unchanged and step 4 still
terminates.

One `MTEXT`, attachment point 5 (middle-centre), `\P` breaks. Name at 3.5 mm
`paper`, the rest at 2.5 mm. **The name and the reference are underlined**, per
`ISO 4157-2` cl. 4.3.2 and corroborated by `AZS ГОСТ 21.501-2010` cl. 2.3.2(6):

```
QONAQ-YEMƏK OTAĞI VƏ MƏTBƏX ZONASI
15,66 m²
4350 × 3600
[R01]
```

**Room names come from `profiles.AZ.rooms.mapping.rooms.<key>.name_az`**, the
eighteen-row table *Two room vocabularies in one file* sourced from AzDTN 2.7-2's
own text — fourteen of eighteen `verified`. They are not translated here and not
invented here; where a row is `engine_choice` it says so and says why, as this
one does: `living_dining_kitchen` is a compound AzDTN has no type for.

> **The standard's own tag placement is refused, and the refusal is narrow.**
> cl. 2.3.2(6) puts the area in the room's **lower-right corner, underlined**.
> The underline is adopted; the corner is not. That clause describes a tag that
> is a *name and an area*, which is what its own worked plans draw. Ours carries
> four lines including a clear-dimension pair, and §7's centroid placement is
> **proved** to sit inside a concave Space
> (`experiments/room-rectangles/erosion_check.py`) where a corner rule is not —
> a corner of a Space's bounding box can lie in the notch, which belongs to a
> different room. Adopting the corner would trade a proof for a convention. The
> divergence is chosen, and it is recorded here so it does not read as an
> oversight.

**Degradation ladder**, in this fixed order, until the tag fits its Space with a
1 × text-height margin clear of walls, openings and in-plan dimensions:

1. Name 3.5 → 2.5 mm `paper`.
2. Substitute the room's **schedule reference** (`R03`) for the room name, the
   full name being carried in the room schedule on sheet 2.
3. Name and body to 1.8 mm `paper`, the ISO 3098 legibility floor.
4. Leader the whole tag out with a `MULTILEADER` into the **margin column** — a
   fixed column outside the ladder, entries stacked at fixed pitch.

> **Step 2 used to substitute an abbreviation, and there is no abbreviation to
> substitute.** The rule required *a published abbreviation, never a truncation*,
> and the research asked in all three candidate languages and came back negative
> in all three: `AZS ГОСТ 21.101-2010` Əlavə D is the published Azerbaijani
> drawing-abbreviation table and contains **one** term from our room set;
> `ГОСТ 2.316-2008` cl. 4.4 actively *forbids* abbreviating outside an annex
> holding zero room words; the one English set is NCS UDS Module 5, paywalled,
> whose own §5.1.2 says *"when the meaning of an abbreviation is in doubt, spell
> it out"*. `WC`, `ST` and `UT` were plausible-looking inventions, and the rule
> forbade them.
>
> The replacement is **better sourced than the thing it replaces**, and it costs
> nothing to build. `AZS ГОСТ 21.501-2010` cl. 2.3.2(6) and `ISO 4157-2`
> cl. 4.3.1–4.3.2 — two standards families sharing no lineage — independently
> prescribe the same fallback: put the names in a schedule and carry **numbers**
> on the plan. §6's room schedule already ships with a `Ref` column, and
> `draw.schedule_complete` already asserts the join is total in both directions,
> which is exactly the property that makes the substitution safe. It removes the
> only step in this document that required inventing data.
>
> ISO 4157-2 adds a rung below this one — a *symbol* (a WC pan, a basin) may
> stand in for a small room's name. **Not built**: §2 states fixtures are not
> modelled.

**No line of the tag is ever dropped.** An earlier draft dropped the room number,
then the dimensions, then the area, as the room shrank. That is backwards: the
small rooms are the ones whose area is contested, and a plan whose 4 m² store
carries no area while its 16 m² living room does is a plan someone will query.
Leader it out instead.

Step 4 terminates: the margin column has fixed pitch and unbounded length, so it
cannot overlap. That is what makes `draw.no_text_overlap` hard rather than
best-effort.

### 7.1 The ladder is audience-split, because step 2 is not

Step 2 resolves a tag to a **room number pointing at the room schedule**, and the
room schedule is `practitioner` (§1). On the Homeowner's eager SVG preview the
tag therefore degrades to a bare number pointing at a document that presentation
filters out. Reproduced: a 1,85 m-wide bedroom in a real solved layout, in
`experiments/homeowner-surface/` on branch `prototype/homeowner-surface`.

The fallback and its target sit on opposite sides of the audience split, so the
fallback is split too:

| Audience | Step 2 resolves to |
|---|---|
| `practitioner` | Room number, name carried in the sheet-2 room schedule — unchanged, and sourced twice over |
| `both` (preview) | **Skip to step 4**: leader the whole tag out into a stacked list beside the plan |

The preview reuses **step 4's mechanism**, not a new one — a `MULTILEADER` into a
fixed-pitch stack — so there is one leadering rule in this document and not two,
and `draw.no_text_overlap`'s termination argument carries over unchanged. The
preview's list sits beside the plan rather than in a sheet margin column, because
the preview has no sheet.

**The three cheaper options were refused.** *Shorten to the name alone and drop
the area and clear dimensions* is refused by §7's own argument, which is not
weaker for a Homeowner: the small rooms are the ones whose area is contested, and
a preview whose 4 m² store carries no area while its 16 m² living room does is
the plan a Homeowner queries first. *Scale the tag* below 1,8 mm `paper` goes
under the ISO 3098 legibility floor. *Promote a minimal room schedule to `both`*
puts a table in front of a user `homeowner-surface.md` §1 says cannot read a
dimension string, to solve a problem that only occurs on the few smallest rooms.

### 7.2 The plan carries one dwelling-level area, and it is a fraction

`AZS ГОСТ 21.501-2010` cl. 2.3.2 states that on a **residential** plan the area
is annotated **as a fraction — living area over useful area**: *"sahəni kəsr
şəklində, surətdə yaşayış, məxrəcdə isə faydalı sahə göstərilir"*, read
first-hand. This is a dwelling-level annotation, not a room-level one: per room
it would divide a bedroom's area by itself. v1 draws exactly one dwelling, so the
plan carries exactly one.

```
yaşayış sahəsi ————————————  27,72
faydalı sahə   ————————————  43,59
```

Both quantities are computable from the model today, which is why this lands here
rather than being handed on a third time:

| Quantity | Definition | Source in the model |
|---|---|---|
| `yaşayış sahəsi` | Σ Space area over Rooms with `is_habitable` | `room-constraints.json` `ergonomic.rooms.*.is_habitable` |
| `faydalı sahə` | Σ all Space areas | the room schedule's own total |

> **`faydalı sahə` and `ümumi sahə` are numerically identical in v1 and are not
> the same quantity.** `ümumi sahə` (Area Qaydalar cl. 3.8, ADR 0010) counts
> balcony, loggia and eyvan area at a coefficient; `faydalı sahə` does not. v1
> models none of the three — `brief.md` and `acceptance-bar.md` both say so and
> the area convention excludes them — so the two coincide by accident of scope.
> **They diverge the day a balcony is modelled**, and a reader who has assumed
> they are one number will be wrong on that day. Stated here rather than
> discovered there.

Audience `practitioner`. A Homeowner shown `27,72 / 43,59` reads a fraction, not
two areas, and `homeowner-surface.md` §3 already gives them per-room areas and a
total in plain language.

**Provenance of this section.** The clause was surfaced by the region-profile
research, which flagged it as belonging to *Area measurement convention*; that
ticket closed on `ümumi sahə` as a single number and **the fraction was never
recorded anywhere in this repo.** It is landed here rather than re-handed
because both its inputs already exist and a third handoff is how a finding dies.

---

## 8. Opening marks are two-level

**The plan carries a position mark; the schedule carries the product
designation.** These are two different things and this document used to conflate
them into one string, `D1` / `W2`, which matches **no published convention** in
any of the families this profile draws on.

| Level | What it is | Where it appears |
|---|---|---|
| **Plan mark** | Short sequential label in a circle. Windows `ОК1`, `ОК2`, …; doors a **bare number**, no letter prefix | On the plan, and in the schedule's `Mark` column |
| **Product designation** | `ДГ 21-8`, `ОР 15-13,5` — encodes the opening size and names the standard | Schedule `Type` column only |

Both are needed and neither substitutes for the other: the mark is what fits
beside an opening at 2.5 mm `paper`; the designation is what tells a builder what
to buy. Marks are drawn in a **Ø 5 mm `paper` circle** — `AZS ГОСТ 21.501-2010`
cl. 2.3.2(4), which fixes 5 where the RF 2018 edition widens it to 5–7; the
Azerbaijani edition is the operative one. Marks that do not fit go on a
`MULTILEADER`.

**Doors and windows number in two separate spaces.** Doors are `1, 2, 3…` with no
prefix, so a door mark and a room number are both bare integers and are
distinguished by their circle diameter — Ø 5 mm for an opening, Ø 12–15 mm for a
room number. **The plan-to-schedule join key is `(kind, n)`, never `n`**, and
`draw.schedule_complete` asserts the join is total in both directions on that
key. A join on `n` alone would silently match door 1 to window 1.

> **The window prefix is `derived`, not `verified`, and the profile now says so.**
> `ОК<n>` is read off `ГОСТ 21.501-2018` cl. 5.4.2 — an RF standard whose preface
> this repo verified Azerbaijan is **not** a voting party to — and the operative
> `AZS ГОСТ 21.501-2010` is silent on it. The door mark and the circle diameter
> *are* verified in the Azerbaijani edition's own text; only the window prefix is
> borrowed. Taken anyway, and the alternative was refused: a Latin `P<n>` for
> *pəncərə* would be an unpublished abbreviation, which is exactly what deleted
> §7's ladder step 2. Emitted as the source writes it — Cyrillic, and **no
> hyphen**: the standard prints `ОК1`, not `ОК-1`.

---

## 9. Sheet, scale, text

### Scale and sheet size

**Scale is held; the sheet grows.** 1:50 is the residential GA scale, and
dropping to 1:100 to keep a plan on A3 is a printing decision masquerading as a
drawing decision. Take the first combination whose annotated extent fits the
printable area:

```
(A3, 1:50), (A2, 1:50), (A1, 1:50), (A1, 1:100)
```

1:100 appears once, at the largest sheet, for a dwelling that fits nothing else.

**The top two rungs are unreachable at v1 sizes.** Measured over 159 solved
Plans: A3 up to 10 rooms, A2 from 12, and **A1 never**, so `(A1, 1:50)` and
`(A1, 1:100)` are dead entries for every dwelling this engine can currently
generate. Implement the ladder as written — it is three lines — but expect only
the first two rungs to be exercised, and treat an A1 selection as a signal that
something upstream has produced a dwelling outside the promised envelope.

Annotated extent = footprint grown on each side by that side's outermost occupied
rung plus one text height, plus the margin column where the §7 ladder reached
step 4.

`DIMSCALE` is the plot denominator. Landscape, 10 mm margins, title-block strip
40 mm on the right edge. Viewport scale is `view_height / viewport_height`, set
explicitly — there is no annotative-scale plumbing and `$PSVPSCALE` stays 0.

### Text hierarchy

ISO 3098 sizes only — 1.8, 2.5, 3.5, 5, 7 mm `paper`. A drawing using arbitrary
text heights looks wrong before it is read.

| Use | Height |
|---|---|
| Drawing number | 7 |
| Project name, drawing title | 5 |
| Room name, notes heading, schedule header | 3.5 |
| Dimension text, tag body, opening marks, notes, schedule body | 2.5 |
| Room name, floor of the degradation ladder | 1.8 |

**The text style must name a TrueType font.** Every stock AutoCAD SHX font lacks
the Azerbaijani letters, so an SHX style renders `ə`, `ğ`, `ı`, `ö`, `ş`, `ü` as
missing glyphs. This is a separate problem from the encoding floor in §11 and is
not solved by it.

---

## 10. Sheet furniture

### Title block

A `BLOCK` with `ATTDEF`s, inserted into paper space and populated with
`add_auto_attribs`, so sheet metadata stays editable downstream instead of being
burned into geometry.

| Attribute | Source |
|---|---|
| `PROJECT`, `CLIENT`, `DATE` | job |
| `DRAWING` | set designation, `<job>-MH` (§1) |
| `SHEET` | `Vərəq n / N` — sequential within the set, not an NCS series number |
| `DRAWN`, `CHECKED` | job; `CHECKED` is `—` and stays `—` |
| `SCALE`, `SIZE`, `REV` | §9, revision block; scale is labelled `M` (*miqyas*), Əlavə D |
| `STATUS` | `İLKİN — TİKİNTİ ÜÇÜN DEYİL` |
| `UNITS` | `Bütün ölçülər millimetrlədir` |
| `DIM-CONV` | `Dimensions to finished wall faces. Overall to the outer face of external walls and to the inner face of party walls.` |
| `AREAS` | `ümumi sahə`, Area Qaydalar cl. 3.8, measured per cl. 3.2 between finished faces at floor level, skirtings excluded |

**`DIM-CONV`'s second sentence was false in both halves and is rewritten, not
deleted.** It read *"Overall to outer face of external walls and to centreline of
party walls."* The centreline half died with ADR 0010; the sentence still has
work to do, because §3's tier-1 rule is asymmetric and a Practitioner needs to be
told which end is which. General note 2 carries the same text and moves with it.

**`AREAS` was a placeholder waiting on *Area measurement convention*, and that
ticket has landed.** The word *finished* in it is now true rather than
aspirational: ADR 0010 moved the bounding plane to match it. Rendered in
Azerbaijani per §1.

`CHECKED` is deliberately present and deliberately empty. A generated drawing has
not been checked by anyone, and a title block that omits the field implies a
process that does not exist here.

### Revision block

Standard four-column block above the title block: `REV`, `DATE`, `DESCRIPTION`,
`BY`. We regenerate rather than revise, so each row is a generation: revision
letter, date, and the Brief change that caused it. This is the Brief being the
real interface, made visible on the sheet.

### General notes

Generated, not authored, on `A-ANNO-TEXT`:

1. All dimensions in millimetres. Do not scale from this drawing.
2. Dimensions are to finished wall faces unless noted. Overall dimensions are to
   the outer face of external walls and to the inner face of party walls.
3. All partitions `t_int` mm unless noted. External walls `t_ext` mm. Party walls
   `t_party` mm. *(region profile / Envelope edges)*
4. `t.d.s. ±0,000`. Clear ceiling height `h_clear` mm.
5. Areas are `ümumi sahə`, measured to finished wall faces at floor level,
   skirtings excluded (Area Qaydalar cl. 3.8, cl. 3.2).
6. All internal openings set out 100 mm from the finished face of the
   perpendicular wall at the hinge end, as dimensioned.
7. Fire, thermal, acoustic and structural performance are not specified.
8. Produced to Neufert-grade dimensional standards. **Not checked against any
   building code. Not for construction or permit submission.**
9. *(only where the Plan holds a `living_dining_kitchen`)* Bu mətbəx qonaq otağına
   açıqdır; **elektrik plitəsi** nəzərdə tutulmalıdır. — *This kitchen opens into
   the living room; an **electric** hob is to be provided.*

Note 9 is the **first conditional** note in this list, and the condition is a Room
type rather than a region or an Envelope edge. It is emitted only where the Plan
holds a Room of type `living_dining_kitchen`, and it is suppressed for
`kitchen_dining`, which AzDTN 2.7-3 cl. 4.7 files inside the word `mətbəx` and
which may therefore hold the gas hob. The two types are one letter apart, so the
condition is on the type and never on prose.

It is on the sheet for note 8's reason turned around. Note 8 says what the drawing
does **not** claim; note 9 says the one thing about this Plan a Baku builder cannot
read off the geometry — the constraint is the room's **category** under AzDTN 2.13-1
cl. 8.31, not its size, so no dimension on the sheet carries it. `brief.md` §7.1
carries the Homeowner's half in their own words and names the alternative; a builder
does not need the alternative, because the type is already decided by the time a
sheet exists. **It states a consequence and makes no compliance claim** — note 8
still governs, and C8 is unmoved. ADR 0036.

Note 4 uses **`t.d.s.`** (*təmiz döşəmə səviyyəsi*) where this document used to
say `FFL` — `AZS ГОСТ 21.101-2010` Əlavə D, Cədvəl D.1. Əlavə D is marked
*tövsiyə olunan*, permitted rather than mandated, and it is adopted because a
drawing issued in Azerbaijani that abbreviates in English is the incongruity ADR
0024 exists to remove. The level itself carries **three decimals and a comma**
per cl. 3.3.7. `h_clear` is ADR 0012's single vertical datum; `h_storey` was
deleted, so there is no second height to confuse it with.

Note 6 is new and it does **not** replace §4.5's dimensions — it states the
constant they all carry, so a builder reading one of them knows it is the rule
and not a one-off.

Note 8 is C8, and it belongs **on the drawing**, not only in the product copy. A
DXF outlives the session that produced it, gets emailed, and arrives somewhere
the product copy never reaches.

### North arrow and scale bar

Paper space, `A-ANNO-TTLB`. The arrow is rotated by the north angle stored on the
Envelope. The scale bar matters more than the `1:50` text — it is what survives a
photocopy or a rescaled print, and its absence is noticed.

---

## 11. DXF specifics

### Dimension style

One style per plot scale, built explicitly. `setup_dimstyle(fmt="EZ_M_50_H25_CM")`
does **not** rescue you — it copies the template's `DIMLFAC = 100.0`, which
prints a 4000 mm wall as `400000`, named by the export research as the single
easiest way to ship a wrong drawing.

```python
s = doc.dimstyles.add("ARCH-MM-50")
s.dxf.dimlfac  = 1.0      # drawing units ARE millimetres
s.dxf.dimscale = 50.0     # annotation scaled for a 1:50 plot
s.dxf.dimtxt   = 2.5      # 2.5 mm text on paper
s.dxf.dimasz   = 2.5
s.dxf.dimexe   = 1.25
s.dxf.dimexo   = 0.625
s.dxf.dimgap   = 0.625
s.dxf.dimdec   = 0        # whole millimetres
s.dxf.dimtad   = 1        # text above the line
s.dxf.dimblk   = "_ARCHTICK"
s.dxf.dimatfit = 2        # move text out first; ticks stay put
s.dxf.dimtmove = 1        # add a leader when text is moved
s.dxf.dimtofl  = 1        # dimension line drawn even when text is outside
s.dxf.dimtix   = 0
s.dxf.dimdsep  = ord(",") # region profile; INERT at dimdec 0 -- see §1.1
```

Document: **R2010 (AC1024)**, `$INSUNITS = 4`, `$MEASUREMENT = 1`,
`$LWDISPLAY = 1`.

> **The stated floor is R2007, not R2000, and it was measured rather than
> argued.** The Azerbaijani alphabet is unrepresentable in DXF R2000: no legacy
> code page anywhere encodes `ə`, not even Turkish cp1254, which carries every
> other Azerbaijani letter. Russian is *worse* at R2000, not better — cp1251
> cannot encode the superscript two in `m²`. Probes in `experiments/az-drawing/`.
> Nothing shipped is broken, because this section already writes R2010; what was
> wrong was the **stated** floor, here and in `bim-cad-export-stack.md`, both
> corrected. R2018 still buys nothing.

### Chains are authored segment by segment

**Do not use `add_multi_point_linear_dim`.** It renders internally and returns
`None`, so there is no handle to place text on and none to key an override to.
Author each segment with `add_linear_dim(base=…)` sharing one base line and call
`.render()` on each — authoring and rendering are **one atomic step**, or the
drawn block and the semantic measurement disagree.

`avoid_double_rendering` is lost with the factory method. Reproduce it exactly:
**every segment after the first in a chain sets `dimse1 = 1`**, suppressing the
duplicate extension line at the shared witness.

### Layers — and these stay US NCS / AIA while the sheet does not

US National CAD Standard / AIA. This **corrects** the ad-hoc names used in the
export research (`A-DIMS`, `A-ANNO`, `A-HATCH`), which are AIA-flavoured but not
conformant.

**This is the one place ADR 0024 does not follow the Azerbaijani convention, and
the split has a stated reason: a sheet mark is read on paper by a builder; a
layer name is read on import by a program.** The sheet number `MH` moved because
a person reads it and a US discipline letter on an Azerbaijani drawing is
incoherent to them. The layer names do not move because their consumer is
AutoCAD, Revit and ArchiCAD, every one of which ships NCS/AIA layer templates and
none of which will resolve a transliterated Azerbaijani layer taxonomy. A
Practitioner recognises `A-WALL` on import; that is the justification this
document already carried, and Azerbaijani-language output does not weaken it.

Two honest limits on that reasoning, so it is not mistaken for a general licence:

- **It is a claim about interchange, not about correctness.** If a later profile
  ships to a market whose tools expect a different taxonomy, this decision is
  re-opened for that profile — it is not region-invariant, it is
  region-*indifferent* only for as long as the tools are.
- **It is not evidence that other US defaults may stay.** Sheet marks,
  abbreviations, the mark scheme and the decimal separator all moved. Layers are
  the exception because of who reads them, and an exception that is used twice
  stops being one.

| Layer | Content |
|---|---|
| `A-WALL` | wall bodies |
| `A-WALL-PATT` | wall poché |
| `A-DOOR` | door frames, leaves, swing arcs |
| `A-GLAZ` | window frames, glazing lines |
| `A-ANNO-DIMS` | every `DIMENSION`, extension line, leader |
| `A-ANNO-TEXT` | room tags, opening marks, notes, level mark |
| `A-ANNO-TTLB` | title block, revision block, north arrow, scale bar, schedule rules |

### PDF

Plot from the DXF; do not author the PDF directly. **ezdxf's PDF backend
vectorises all text**, so nothing in the output is selectable or searchable.
Accepted: a floor plan is a drawing, not a document. `pymupdf` is AGPL-3.0 or
Artifex Commercial — fine under C9, and a licence trap the day C9 stops being
true.

---

## 12. Annotation overrides

ADR 0002 persists an `AnnotationOverride` keyed by **relation**, so it dies
honestly when the topology changes rather than reattaching to the wrong thing.

> **An override carries placement only. It can never change a measured number, a
> room name, or a schedule value.**

A name is Brief data — edit the Brief. A number is geometry — edit the plan.
Letting either through the override layer lets a human make the drawing lie about
the model, which is the failure this whole layer exists to prevent.

| Element | Key |
|---|---|
| Room tag | `("tag", room_id)` — Brief-anchored, stable |
| Chain segment | `("dim", tier, side, witness_a, witness_b)` |
| Setting-out dimension | `("sod", {room, room}, ordinal)` |
| Opening type mark | `("mark", {room, room}, ordinal)` — ordinal by coordinate order along the segment |
| Sheet furniture, schedules | fixed; not overridable |

A **witness** — the wall face a dimension measures to — is keyed by the rooms
immediately either side of it: `("wit", axis, {rooms left}, {rooms right})`,
Brief ids throughout. It survives a regenerate that keeps the topology and dies
when the topology changes, which is exactly ADR 0002's requirement.

Overrides are **additive**: shipping pure derivation first and adding the layer
later changes nothing in the model.

---

## 13. The Drawing check

**Twelve** predicates. A Plan reaching this point has already passed the Acceptance
bar, so a Drawing failure is **our bug, not the plan's**: the check raises and
refuses to emit the file. It never degrades silently, and it never ships a
drawing it knows is wrong.

| id | Predicate |
|---|---|
| `draw.chain_closes` | every chain's segments sum exactly to its axis span |
| `draw.measurement_matches_model` | every `DIMENSION`'s `get_measurement()` equals the model distance it was authored from |
| `draw.dimstyle_units` | `DIMLFAC == 1.0`, `DIMDEC == 0`, `$INSUNITS == 4`, `$MEASUREMENT == 1` |
| `draw.every_space_tagged` | every Space carries exactly one tag |
| `draw.every_opening_marked` | every Opening carries a type mark |
| `draw.every_opening_positioned` | every Envelope-edge Opening is in exactly one tier-3 chain; every internal Opening has exactly one setting-out dimension |
| `draw.every_wall_face_dimensioned` | every partition face is on a tier-2 or tier-2b chain |
| `draw.schedule_complete` | every Opening has exactly one schedule row and every row has exactly one Opening, joined on `(kind, mark)`; same for Spaces and the room schedule |
| `draw.schedule_totals_close` | every printed total equals the sum of the printed cells above it, and the difference row equals the printed difference |
| `draw.lineweights_valid` | every lineweight is in the DXF enumerated set |
| `draw.no_text_overlap` | no two rendered text extents intersect |
| `draw.within_printable_area` | all geometry inside the sheet margins |

**A two-rectangle Room adds no predicate here, and that is worth saying because
it looks as though it should.** `every_space_tagged` still wants exactly one tag
per Space — §7 places it, and a Space is still one Space. `every_wall_face_
dimensioned` counts **partition faces**, and the edge where a Room's two legs
meet is not one: nothing separates a Room from itself, so no Wall exists there
(`CONTEXT.md`, **Wall segment**). A derivation that walked part boundaries would
draw a partition inside a room, and it would read as deliberate rather than as a
bug — which is why the invariant is stated in the vocabulary and not only here.

**`schedule_totals_close` is new and it is the area analogue of
`chain_closes`.** A chain is in integer millimetres and closes by construction;
an area renders to 2 dp and does not, so a totals row computed from exact values
can differ from the column printed above it — 43,58 against 43,59 in §14. The
predicate makes the page self-consistent, and §6 makes it satisfiable by
computing every total from the printed cells. It is the only Drawing predicate
whose failure mode is invisible in the geometry and visible only to a person
adding a column.

`measurement_matches_model` earns its place: it catches the **stale block** —
definition points mutated without re-rendering, so the drawn picture and the
semantic measurement disagree. That failure is invisible in a viewer that shows
the block, and it is the specific hazard of ezdxf shipping both a semantic
dimension and a pre-drawn picture of it.

**This is not the Acceptance bar and does not go in `rules.json`.** The bar has
two consumers — the solver posts inequalities, the validator evaluates finished
geometry — which is what forced a declarative registry and a conformance test.
The Drawing check has one consumer and runs at export, after the bar has passed.
Giving it a registry would introduce a third consumer of a declaration built for
two, and reopen a question ticket 07 closed.

---

## 14. Worked example

A single-aspect one-bedroom flat, `AZ` profile. Every number is computed, not
illustrative.

> **Re-derived at `t_int` = 150.** This example was built at `t_int` = 100 and
> was stale from the day ADR 0010 shipped 150 — the profile's number, not the
> ADR's. It could not be patched, because the solve domain is the Envelope
> dilated by `t_int/2` and has to land on the 250 mm grid: at 75 mm of dilation
> the old 7900 × 5900 interior gives 8050 × 6050, which is not a whole number of
> cells. The Envelope moved to **7850 × 5850** so that it does. Everything below
> follows from that and from the shipped profile — tier 1 per §3, windows sized
> from the series per §8, doors placed per `openings.md` §3.1–3.3.

**Inputs.** Envelope inner region `[0, 7850] × [0, 5850]`, origin at bbox min,
+Y north. Edges: S exterior `t = 300`, W exterior `t = 300`, N party `t = 280`,
E party `t = 280`. Entrance side N. `t_int = 150`. Solve grid 250 mm.

**Solve domain** = Envelope dilated by `t_int/2 = 75` → `[-75, 7925] × [-75,
5925]` = 8000 × 6000 = 32 × 24 cells, exactly on grid.

**Solved rects → clear rects** (`erode(rect, 75)`). The hall is a spine touching
the N party edge, so the entrance reaches it and every room opens off it:

| Ref | Room | Solved | Clear | Area |
|---|---|---|---|---|
| R01 | QONAQ-YEMƏK OTAĞI VƏ MƏTBƏX ZONASI | `[-75,4425] × [-75,3675]` | `[0,4350] × [0,3600]` | 15,66 m² |
| R02 | YATAQ OTAĞI | `[4425,7925] × [-75,3675]` | `[4500,7850] × [0,3600]` | 12,06 m² |
| R03 | VANNA OTAĞI | `[-75,2425] × [3675,5925]` | `[0,2350] × [3750,5850]` | 4,94 m² |
| R04 | HOL | `[2425,5925] × [3675,5925]` | `[2500,5850] × [3750,5850]` | 7,04 m² |
| R05 | YIĞNAQ OTAĞI | `[5925,7925] × [3675,5925]` | `[6000,7850] × [3750,5850]` | 3,89 m² |

**Tier 1** (§3 — outer face on an exterior edge, inner face on a party edge).
W and S are exterior at 300; N and E are party:

```
overall_x = 7850 + 300 = 8150
overall_y = 5850 + 300 = 6150
```

Neither equals its axis's tier-2 span (7850, 5850), so tier 1 carries
information on both axes rather than restating the inner ring. Had this been a
mid-block flat with party walls east *and* west, `overall_x` would be 7850 and
would correctly say that the flat's footprint on that axis *is* its inner
dimension.

**Tier 2 — four chains, each closing on its axis:**

```
South  (verticals reaching S: x=4425)
  4350 | 150 | 3350                        = 7850  ✓
North  (verticals reaching N: x=2425, x=5925)
  2350 | 150 | 3350 | 150 | 1850           = 7850  ✓
West   (horizontals reaching W: y=3675)
  3600 | 150 | 2100                        = 5850  ✓
East   (horizontals reaching E: y=3675)
  3600 | 150 | 2100                        = 5850  ✓
```

Every tick is a room's clear dimension or a wall thickness. Every partition is
captured, so **tier 2b is empty and consumes no rung** — which makes this a
small-plan case, not the typical one: §4.3 measured nearly half a large plan's
partitions reaching no Envelope edge.

**Windows — sized from the series, not picked from a catalogue** (§8,
`profiles.AZ.openings.window_for_room`). Both Spaces take the 1500 mm habitable
height, so both sills are at `2200 − 1500 = 700`. Target is the profile's soft
0,154 where a member reaches it, floor is the hard 0,125:

| Space | Area | 0,154 needs | Member | Ratio delivered | Clear run | `w + 200` |
|---|---:|---:|---:|---:|---:|---:|
| R01 | 15,66 m² | 1608 mm | **1800** | 0,172 | 4350 | 2000 ✓ |
| R02 | 12,06 m² | 1238 mm | **1350** | 0,168 | 3350 | 1550 ✓ |

Both land just above target on one window each. The three-entry catalogue this
replaced would have given R01 a single 1500 (ratio 0,144 — under target, over the
floor) and then added a **second** 1500 to close the gap, reaching 0,287: nearly
twice the target, because the increment was a whole window rather than a width.

Marks and designations (§6, §8): `ОК1` is `ОР 15-18`; `ОК2` is **`ОР 15-13,5`** —
the fractional decimetre group, which the standard itself prints and which a
parser casting decimetres to `int` silently turns into 1300.

**Tier 3 — two Envelope edges hold openings.** Windows centre on their clear run
(`openings.md` §6.1, one window at ½ of the run); the entrance door is pushed to
an end per §3.2:

```
South  ОК1 SO 1800 (R01), ОК2 SO 1350 (R02)
  1275 | 1800 | 2425 | 1350 | 1000         = 7850  ✓
North  door 1 SO 900, entrance through the party wall into R04
  2600 | 900 | 4350                        = 7850  ✓
```

**Internal openings — four setting-out dimensions.** Placement order is
breadth-first from the entrance (`openings.md` §3.1); each door is pushed to the
end of its run nearest the door the approaching Space was entered through, which
here is the entrance door at `x` 2600–3500 on the north edge. Catalogue entry is
chosen by the **receiving** Space, the more private of the pair (§3.3):

| Mark | Between | Entry | SO | Contact run | Needs `w+400` | Datum face | Setting out |
|---|---|---|---:|---:|---:|---|---:|
| 2 | R04 → R01 | `door_living_glazed` | 900 | 1850 | 1300 ✓ | `x = 2500` | 100 |
| 3 | R04 → R02 | `door_kitchen` | 800 | 1350 | 1200 ✓ | `x = 4500` | 100 |
| 4 | R04 → R03 | `door_bathroom_wc` | 700 | 2100 | 1100 ✓ | `y = 5850` | 100 |
| 5 | R04 → R05 | `door_bathroom_wc` | 700 | 2100 | 1100 ✓ | `y = 5850` | 100 |

**All four read 100, and that is the rule rather than a coincidence** — §4.5.
Door 3 is the tight one: its contact run of 1350 mm is exactly `w + t_int + 400`
= 800 + 150 + 400 under ADR 0021's revised threshold, so this plan sits on the
solver reservation rather than clear of it. Under the *old* threshold — `w_struct`
of clear run and nothing else — the same contact would have looked 550 mm
oversized while admitting a door that `open.leading_edge_nib` then rejects.

Marks: doors are bare numbers `1 … 5` in Ø 5 mm circles, windows `ОК1`, `ОК2`.
Two number spaces, joined to the schedules on `(kind, n)` (§8).

**Areas, and the totals row does not simply add up** (§6):

```
              printed      exact
R01            15,66      15,660
R02            12,06      12,060
R03             4,94       4,935
R04             7,04       7,035
R05             3,89       3,885
              ------      ------
Σ Space        43,59      43,575   → rounds to 43,58, NOT 43,59
Envelope inner 45,92      45,9225
difference      2,33       2,3475  → rounds to 2,35, NOT 2,33
```

The printed column is what the schedule carries, because a Practitioner adds it.
The partition footprint is **2,33 / 43,59 = 5,35 %** of Σ Space area, against the
5,7 % measured over 14 063 dwellings at this `t_int` — one plan inside the
distribution, not a check of it.

**The dwelling area fraction** (§7.2). Habitable Spaces are R01 and R02:

```
yaşayış sahəsi   27,72
faydalı sahə     43,59
```

**Sheet.** Annotated extent = 8150 + 2 × (26 + 4) × 50 = 11 150 → 223 mm `paper`;
6150 + same = 9150 → 183 mm `paper`. A3 landscape printable area with the 40 mm
title strip is 360 × 277. It fits: **sheet 1 at A3, 1:50**, `DIMSCALE = 50`,
title block `<job>-MH`, `Vərəq 1 / 2`. Sheet 2 carries five door rows, two window
rows and five room rows.

**Preview, same plan.** Poché, swings, glazing, room tags, fixture render. No
chains, no marks, no sheet furniture, no area fraction:
`QONAQ-YEMƏK OTAĞI VƏ MƏTBƏX ZONASI` · `15,66 m²` · `4,35 × 3,60 m`. Decimal comma, no
thousands grouping, per §1.1.
