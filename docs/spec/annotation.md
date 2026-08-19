# Drawing spec: graphics, dimensioning, annotation, schedules

How a `Drawing` is derived from a `Plan`. Resolves *Dimensioning and annotation
rules*. Companion to [ADR 0004](../adr/0004-published-dimensions-measure-wall-faces.md).

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
| Dimension chains, tiers 1 / 2 / 2b / 3 (§4) | `practitioner` |
| Internal setting-out dimensions (§4.5) | `practitioner` |
| Opening type marks | `practitioner` |
| Title block, revision block, general notes, north arrow, scale bar | `practitioner` |
| Schedules (§6) | `practitioner` |

The eager SVG preview renders `both`. The lazy DXF/PDF renders everything. One
derivation, one override key space, no second annotation engine to drift against
the first.

**The sheet set is two sheets, not one:**

| Sheet | Content |
|---|---|
| `A-101` | General arrangement plan, dimensioned and annotated |
| `A-102` | Door schedule, window schedule, room schedule |

A single-sheet set with schedules crammed into the plan margin is what a
generator produces. A set is what a practice issues.

**Units differ by target, and that is safe only because of one invariant:**

> **A dimension rendered in any unit other than integer millimetres may not be
> part of a chain.**

The preview renders metres to 2 dp (`4.40 × 3.40 m`) and draws no chain. The
sheets render integer millimetres with no unit suffix (`4400`) and draw every
chain. Integer millimetres sum exactly, so a chain closes by construction; the
moment a number is rounded for display it is barred from a chain. The classic
embarrassment — a chain that does not add up — is unreachable rather than
guarded against.

Areas render as m² to 2 dp. The **decimal separator comes from the region
profile** (`.` UK, `,` DE) and is written to `DIMDSEP`.

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

`FFL ±0.000` is annotated once on the plan, on `A-ANNO-TEXT`. Ceiling height goes
in the general notes.

Not drawn, and each is a stated absence rather than an oversight: floor finishes
and thresholds (no finishes model), structural grid (a single dwelling does not
carry one), fixtures and furniture (not modelled — see the map's fog), and any
hatch pattern implying a material specification.

---

## 3. What is measured to

**Every published dimension measures wall faces. No published dimension measures
a centreline, with exactly one exception.** Rationale and the rejected
alternative: ADR 0004.

- A **witness** is a line a dimension is measured to. Every witness is a wall
  face, in clear coordinates.
- A tier-2 chain therefore alternates: room clear width, wall thickness, room
  clear width, … Every tick is a real quantity a person can tape.
- **The exception**: tier 1 spans the footprint, and a party wall's outer face
  lies inside the neighbour's home. Tier 1 measures **to the outer face of an
  exterior edge and to the centreline of a party edge**, matching GIA and IPMS.
  It is the only centreline number on the sheet, and the title block names it.

Tier 1 for a rectangular Envelope of inner width `W`, west edge exterior of
thickness `t_w`, east edge party of thickness `t_e`:

```
overall_x = W + t_w + t_e/2
```

**Consequence, and it binds a different ticket.** ADR 0001 needs
`erode(rect, t/2)` in integer millimetres, and tier 1 needs `t_party/2` likewise.
So **every wall thickness in a region profile must be an even number of
millimetres.** 100 / 120 / 140 / 200 / 240 / 300 are fine. **115 mm (half-brick)
and 125 mm (DIN 4172 octametric, and a common UK blockwork-plus-plaster
build-up) are not** — they put every wall face on a half-millimetre and every
clear dimension off-integer. Handed to *Which region profiles ship in v1*.

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

One per side, all four sides. Footprint span, per §3.

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

Rule: a short dimension drawn **inside the plan**, from the **nearest
perpendicular wall face** to the **near jamb of the structural opening**, on the
side with more clear space, offset 3 mm `paper` from the host wall face, text
above the line.

Consequence, taken deliberately: annotation now lives inside the plan, so
collisions inside the plan are real (§5). The alternative — a general note
standing in for every internal door position — keeps the plan interior clean by
withholding information the drawing exists to carry.

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

**v1 ships drawn schedules on sheet `A-102`.** ezdxf has no `ACAD_TABLE` entity,
so a schedule is composed from `LWPOLYLINE` rules and `MTEXT` cells. That is a
table layout component to build; it is not a reason to omit the schedules. It is
also the single thing the competitive scan found **no vendor documents at all**,
across eleven products and four price tiers.

Header row 3.5 mm `paper` text on a 0.25 rule; body rows 2.5 mm on 0.13 rules;
column widths from the widest cell, rounded up to 5 mm `paper`.

### Door schedule

| Mark | Type | Structural opening W × H | Leaf W × H | Handing | Swing | Notes |
|---|---|---|---|---|---|---|

Handing and swing come from *Opening placement rules*. `Type` is the region
profile catalogue key. A **cased opening** has no leaf and no handing; those
cells read `—`, never blank, so a missing value is distinguishable from an
inapplicable one.

### Window schedule

| Mark | Type | Structural opening W × H | Sill height | Fall barrier | Notes |
|---|---|---|---|---|---|

`Fall barrier` carries the guarding height where the model holds one, and `—`
where it does not — the two are separate model values precisely because one
number cannot serve both.

### Room schedule

| Ref | Room | Clear dimensions | Area |
|---|---|---|---|

Totals row: sum of Space areas, and the Envelope inner area, both stated. They
differ by the partition footprint, and showing both is how a Practitioner
reconciles the schedule against the plan.

**No fire, thermal, acoustic or structural columns.** Not omitted for effort —
excluded because C8 forbids the claim, and a `TBC` in a fire-rating column is a
claim that someone will fill it in.

---

## 7. Room tags

Placement is the Space centroid. **The largest-inscribed-circle machinery is not
needed and is not specified**: the solver tiles rectangles and `erode(rect, t/2)`
is a rectangle, so no v1 Space is concave and the centroid is exact. It becomes
needed the day non-rectangular rooms do.

One `MTEXT`, attachment point 5 (middle-centre), `\P` breaks. Name at 3.5 mm
`paper`, the rest at 2.5 mm:

```
LIVING / KITCHEN
16.06 m²
4400 × 3400
[R01]
```

**Degradation ladder**, in this fixed order, until the tag fits its Space with a
1 × text-height margin clear of walls, openings and in-plan dimensions:

1. Name 3.5 → 2.5 mm `paper`.
2. Substitute the region profile's **standard abbreviation** for the room name
   (`WC`, `ST`, `UT`) — a published abbreviation, never a truncation. `BEDR…`
   reads as a bug and discredits the numbers beside it.
3. Name and body to 1.8 mm `paper`, the ISO 3098 legibility floor.
4. Leader the whole tag out with a `MULTILEADER` into the **margin column** — a
   fixed column outside the ladder, entries stacked at fixed pitch.

**No line of the tag is ever dropped.** An earlier draft dropped the room number,
then the dimensions, then the area, as the room shrank. That is backwards: the
small rooms are the ones whose area is contested, and a plan whose 4 m² store
carries no area while its 16 m² living room does is a plan someone will query.
Leader it out instead.

Step 4 terminates: the margin column has fixed pitch and unbounded length, so it
cannot overlap. That is what makes `draw.no_text_overlap` hard rather than
best-effort.

---

## 8. Opening type marks

Every Opening carries a **type mark** — `D1`, `W2` — keyed to the region profile
catalogue entry, at 2.5 mm `paper` beside the opening, or on a `MULTILEADER`
where it does not fit. The mark is the join between the plan and the §6
schedules, and `draw.schedule_complete` asserts the join is total in both
directions.

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
| Dimension text, tag body, type marks, notes, schedule body | 2.5 |
| Room name, floor of the degradation ladder | 1.8 |

---

## 10. Sheet furniture

### Title block

A `BLOCK` with `ATTDEF`s, inserted into paper space and populated with
`add_auto_attribs`, so sheet metadata stays editable downstream instead of being
burned into geometry.

| Attribute | Source |
|---|---|
| `PROJECT`, `CLIENT`, `DRAWING`, `SHEET`, `DATE` | job |
| `DRAWN`, `CHECKED` | job; `CHECKED` is `—` and stays `—` |
| `SCALE`, `SIZE`, `REV` | §9, revision block |
| `STATUS` | `PRELIMINARY — NOT FOR CONSTRUCTION` |
| `UNITS` | `All dimensions in millimetres` |
| `DIM-CONV` | `Dimensions to finished wall faces. Overall to outer face of external walls and to centreline of party walls.` |
| `AREAS` | area convention name — from *Area measurement convention* |

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
   the outer face of external walls and to the centreline of party walls.
3. All partitions `t_int` mm unless noted. External walls `t_ext` mm. Party walls
   `t_party` mm. *(region profile / Envelope edges)*
4. Finished floor level `±0.000`. Clear ceiling height `H` mm.
5. Areas are `<convention>`, measured to finished wall faces. *(from* Area
   measurement convention*)*
6. Fire, thermal, acoustic and structural performance are not specified.
7. Produced to Neufert-grade dimensional standards. **Not checked against any
   building code. Not for construction or permit submission.**

Note 7 is C8, and it belongs **on the drawing**, not only in the product copy. A
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
s.dxf.dimdsep  = ord(".") # region profile
```

Document: **R2010 (AC1024)**, `$INSUNITS = 4`, `$MEASUREMENT = 1`,
`$LWDISPLAY = 1`. R2000 is the hard floor; R2018 buys nothing.

### Chains are authored segment by segment

**Do not use `add_multi_point_linear_dim`.** It renders internally and returns
`None`, so there is no handle to place text on and none to key an override to.
Author each segment with `add_linear_dim(base=…)` sharing one base line and call
`.render()` on each — authoring and rendering are **one atomic step**, or the
drawn block and the semantic measurement disagree.

`avoid_double_rendering` is lost with the factory method. Reproduce it exactly:
**every segment after the first in a chain sets `dimse1 = 1`**, suppressing the
duplicate extension line at the shared witness.

### Layers

US National CAD Standard / AIA. This **corrects** the ad-hoc names used in the
export research (`A-DIMS`, `A-ANNO`, `A-HATCH`), which are AIA-flavoured but not
conformant. A Practitioner recognises the real ones, and layer names are the
first thing they look at on import.

| Layer | Content |
|---|---|
| `A-WALL` | wall bodies |
| `A-WALL-PATT` | wall poché |
| `A-DOOR` | door frames, leaves, swing arcs |
| `A-GLAZ` | window frames, glazing lines |
| `A-ANNO-DIMS` | every `DIMENSION`, extension line, leader |
| `A-ANNO-TEXT` | room tags, type marks, notes, FFL |
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

Eleven predicates. A Plan reaching this point has already passed the Acceptance
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
| `draw.schedule_complete` | every Opening has exactly one schedule row and every row has exactly one Opening; same for Spaces and the room schedule |
| `draw.lineweights_valid` | every lineweight is in the DXF enumerated set |
| `draw.no_text_overlap` | no two rendered text extents intersect |
| `draw.within_printable_area` | all geometry inside the sheet margins |

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

A single-aspect one-bedroom flat. Every number is computed, not illustrative.

**Inputs.** Envelope inner region `[0, 7900] × [0, 5900]`, origin at bbox min,
+Y north. Edges: S exterior `t = 300`, W exterior `t = 300`, N party `t = 200`,
E party `t = 200`. Entrance side N. `t_int = 100`. Solve grid 250 mm.

**Solve domain** = Envelope dilated by `t_int/2 = 50` → `[-50, 7950] × [-50,
5950]` = 8000 × 6000 = 32 × 24 cells, exactly on grid.

**Solved rects → clear rects** (`erode(rect, 50)`). The hall is a spine touching
the N party edge, so the entrance reaches it and every room opens off it:

| Ref | Room | Solved | Clear | Area |
|---|---|---|---|---|
| R01 | LIVING / KITCHEN | `[-50,4450] × [-50,3700]` | `[0,4400] × [0,3650]` | 16.06 m² |
| R02 | BEDROOM | `[4450,7950] × [-50,3700]` | `[4500,7900] × [0,3650]` | 12.41 m² |
| R03 | BATHROOM | `[-50,2450] × [3700,5950]` | `[0,2400] × [3750,5900]` | 5.16 m² |
| R04 | HALL | `[2450,5950] × [3700,5950]` | `[2500,5900] × [3750,5900]` | 7.31 m² |
| R05 | STORE | `[5950,7950] × [3700,5950]` | `[6000,7900] × [3750,5900]` | 4.09 m² |

Space total 45.03 m²; Envelope inner 46.61 m²; difference 1.58 m² is partition
footprint. Both go on the room schedule's totals row.

**Tier 1.** `overall_x = 7900 + 300 + 100 = 8300`.
`overall_y = 5900 + 300 + 100 = 6300`.

**Tier 2 — four chains, each closing on its axis:**

```
South  (verticals reaching S: x=4450)
  4400 | 100 | 3400                        = 7900  ✓
North  (verticals reaching N: x=2450, x=5950)
  2400 | 100 | 3400 | 100 | 1900           = 7900  ✓
West   (horizontals reaching W: y=3700)
  3650 | 100 | 2150                        = 5900  ✓
East   (horizontals reaching E: y=3700)
  3650 | 100 | 2150                        = 5900  ✓
```

Every tick is a room's clear dimension or a wall thickness. Every partition is
captured, so **tier 2b is empty and consumes no rung**.

**Tier 3 — two Envelope edges hold openings:**

```
South  W1 SO 1800 (R01), W2 SO 1200 (R02)
  1300 | 1800 | 2500 | 1200 | 1100         = 7900  ✓
North  D1 SO 1000, entrance through the party wall into R04
  3700 | 1000 | 3200                       = 7900  ✓
```

**Internal openings — four setting-out dimensions**, each from the nearest
perpendicular face to the near jamb:

| Mark | Between | SO | Datum face | Setting out |
|---|---|---|---|---|
| D2 | R04 → R01 | 900 | `x = 2500` | 200 |
| D3 | R04 → R02 | 900 | `x = 4500` | 200 |
| D4 | R04 → R03 | 800 | `y = 5900` | 400 |
| D5 | R04 → R05 | 700 | `y = 5900` | 200 |

Each contact clears the threshold: `SO + t_int` against a contact run of 2000
(D2), 1500 (D3) and 2250 (D4, D5).

**Narrow-tick rule fires five times** — the five `t_int` ticks (South one, North
two, West one, East one), 2 mm `paper` at 1:50 against ~7 mm of text, all five
text-outside with a leader. On the north chain the two outside texts are 3400
apart, 68 mm `paper`, so no alternation is needed.

*(Corrected from "four" by* Solver timing variance sweep*, whose reproduction in
`experiments/solver-toy/drawing_metrics.py` agrees with every other number in
this section. The four chains above contain five `t_int` ticks.)*

**Sheet.** Annotated extent = 8300 + 2 × (26 + 4) × 50 = 11 300 → 226 mm `paper`;
6300 + same = 9300 → 186 mm `paper`. A3 landscape printable area with the 40 mm
title strip is 360 × 277. It fits: **A-101 at A3, 1:50**, `DIMSCALE = 50`.
`A-102` carries five door rows, two window rows and five room rows.

**Preview, same plan.** Poché, swings, glazing, room tags. No chains, no marks,
no sheet furniture: `LIVING / KITCHEN` · `16.06 m²` · `4.40 × 3.40 m`.
