---
id: 34
title: What IFC the engine actually emits
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - docs/spec/ifc-export.md (new)
  - docs/adr/0011-ifc-is-a-reference-view-file-that-asserts-only-what-is-known.md (new)
  - CONTEXT.md  # one term: IFC check
---

# What IFC the engine actually emits

## Question

**The Destination names "valid IFC" as a hard output, and no document on this map
says what that file contains.** Surfaced by the map's done-test: the string `IFC`
appears in `docs/research/`, in ADR 0001 in passing, and in five ticket bodies —
and in **zero** files under `docs/spec/`. DXF has a spec section
(`annotation.md` §11: R2007 floor, `DIMLFAC`, layer names, text style). IFC has
nothing.

*BIM and CAD export stack* proved the **tooling** — `ifcopenshell` authors clean
IFC4, `ObjectPlacement` is mandatory — and was never asked to specify the
**content**. That is this ticket.

This is not a build task dressed as a decision. Each item below is a fork with
consequences that reach back into the model, and picking one by whichever
`ifcopenshell` example is nearest to hand is precisely the C2 failure — a file
that opens, and that a Practitioner throws away.

**Decide:**

1. **Which IFC4 model view.** Reference View is the lightweight, widely-imported
   one; Design Transfer View is the one that carries editable parametric geometry.
   C2 promises the engine will not *preclude* a Revit round-trip, and the choice
   between these is most of what that promise costs. Name the view, and say what
   it forecloses.

2. **How a `Wall` becomes IFC.** ADR 0001 makes a Wall a **centreline plus a
   thickness** — which is exactly `IfcWallStandardCase`'s own axis-plus-thickness
   model, so the mapping looks free. Confirm that it is, and settle what happens at
   junctions: whether `IfcRelConnectsPathElements` is authored, and with what
   `RelatingConnectionType`, or whether walls ship as unconnected swept solids and
   the receiving application re-derives the joins.

3. **How a `Space` becomes IFC**, and whether space boundaries are authored.
   `IfcSpace` is easy; `IfcRelSpaceBoundary` (1st or 2nd level) is where the real
   decision is, because it is what makes the model useful downstream and what
   nothing in the current geometry model materialises. *Canonical geometry model*
   derives Spaces and junctions already — does that derivation reach far enough?

4. **Whether annotation crosses into IFC at all.** It largely cannot: IFC has
   `IfcAnnotation` but **no dimension-chain concept**, so the chains that
   `annotation.md` spends fourteen sections on have no IFC counterpart. Decide
   whether the IFC export is deliberately annotation-free — geometry and quantities
   only, with the drawing living in DXF/PDF — or whether room tags travel as
   `IfcAnnotation`. ADR 0002 already made annotation derived rather than stored,
   which points at the first answer; say so explicitly rather than by omission.

5. **Which property and quantity sets are written**, and what they claim.
   `Pset_SpaceCommon`, `Qto_SpaceBaseQuantities`, `Pset_WallCommon`. Two traps
   here. A wall's `LoadBearing` is **unknown, not false** (*Canonical geometry
   model* left the hook deliberately) and `Pset_WallCommon.LoadBearing` is a
   boolean — so either the property is omitted or the file asserts something this
   system does not know. And `IsExternal` must agree with ADR 0003's edge ring.

6. **Units, georeferencing, and the north angle.** The model is **integer
   millimetres** (ADR 0001); IFC's length unit is declared per file. State the
   declaration. *Building scope and envelope handling* stores a north angle used
   only for the drawing's north arrow — decide whether it reaches
   `IfcGeometricRepresentationContext.TrueNorth`, given that the site is
   out of scope and the export must not imply a siting it does not have.

7. **What "valid" means as an acceptance criterion.** The Destination says *valid*
   IFC. Name the check — buildingSMART validation service, `ifcopenshell`'s own
   schema validation, or a bundled subset — and decide whether it gates the export
   the way *Dimensioning and annotation rules*' **Drawing check** gates whether a
   DXF file is written. If it does, note explicitly that this is a **third**
   check alongside `rules.json` and the Drawing check, and justify it against the
   reasoning that kept the Drawing check out of `rules.json`.

**Blocked by *Area measurement convention*.** Item 5 cannot be settled before it:
`Qto_SpaceBaseQuantities.NetFloorArea` has defined semantics, and writing a number
into it without knowing which convention that number is in is the silent
mismatch ticket 17 exists to prevent. That ticket's own item 4 already reaches
into this one — it owns the *area declaration* slice, this ticket owns everything
else, and neither should restate the other.

**Not in scope here:** the Revit *import* weakness the export research flagged and
never wrote up. That stays in the *Revit round-trip specifics* fog patch, which
currently rests on a section that was never written.

Deliverable: a spec section — `docs/spec/ifc-export.md`, or a new section in an
existing spec — naming the model view, the entity mapping per Plan concept, the
property and quantity sets with their sources, the unit and georeferencing
declaration, and the validity check.

## Inherited from *Area measurement convention* — blocker discharged, and item 3 gains a decided number

`blocked_by: [17]` is discharged. ADR 0010 settles the quantity; this ticket still
owns the encoding.

**The number is decided; how it is written is not.** The Plan's area convention is
`az_umumi_sahə` — Area Qaydalar cl. 3.8, measured per cl. 3.2 between **finished**
faces at floor level, skirtings excluded — and it is the **sum of Space areas**,
which does **not** count internal partitions.

- **Write `Qto_SpaceBaseQuantities.NetFloorArea`** from the Space polygon. Under
  ADR 0010 that polygon *is* the finished-face plane, so the mapping is exact and
  needs no adjustment on export.
- **Do not write `GrossFloorArea`.** It would require attributing half of each
  bounding partition to the space, which is a different convention from the one
  the drawing quotes and from the one the acceptance bar gates on. A file whose
  quantity disagrees with the room tag beside it is the defect item 4 of this
  ticket already worries about, arriving through the quantity set instead of
  through annotation.
- **Carry the convention as a property**, so the file self-describes rather than
  relying on a reader assuming IFC's own default reading. Where it goes —
  `Pset_SpaceCommon`, a custom `Pset`, or `IfcPropertySet` on the building — is
  this ticket's call.

**ADR 0010 also changes item 2, and in this ticket's favour.** A Wall's thickness
is now a **layer set**, not a scalar: `t_int` 150 = 120 mm structural leaf +
2 × 15 mm finish, and the structural twin is kept as data precisely so that
`IfcWallStandardCase` can carry `IfcMaterialLayerSetUsage` with real layers.
Emitting a homogeneous 150 mm wall where a real one has three layers is the file
that opens and gets thrown away — the C2 failure this ticket names in its own
preamble. The layers exist in the profile now; use them.

Shipping thicknesses, totals and leaves alike: `t_int` 150 / 120 structural,
`t_party` 280 / 250 structural, `t_ext_total` 500 (380 leaf + 100 insulation +
20 finish).

---

## Resolution

**Reference View, and the file asserts only what the engine knows.**
`docs/spec/ifc-export.md`, ADR 0011. Seven items decided, and the ticket's own
item 1 turned out to be a fork with one live branch.

### Design Transfer View is not an option, and the round-trip it was to buy is not for sale

The ticket asked which of the two IFC4 model views to pick, and said the choice
"is most of what that promise costs" — C2's undertaking not to preclude a Revit
round-trip. **There is no choice.** Three independent findings:

- buildingSMART's own position: *"Design Transfer View never materialised into an
  official MVD."* IFC4.3 publishes exactly two views — Reference View and
  Alignment Based Reference View.
- Software certified for Design Transfer View export: **zero**. Revit's IFC4
  certification is **Reference View 1.2, export only**; IFC4 *import*
  certification exists industry-wide for two products (Tekla, BridgeBIM).
- The DTV documentation itself describes a *"higher fidelity one-way transfer of
  data and responsibility"* — not a round-trip.

So **IFC4 ADD2 TC1, Reference View V1.2, held strictly**, and the file is built to
the top of what RV allows rather than to the bottom.

### What Reference View costs, and the one place it costs nothing because of ADR 0001

RV is less restrictive than its reputation. Swept solids are in scope — nothing is
forced to triangulate — as are property sets, quantity sets, material layer sets,
object typing and the `Name`/`LongName` identity attributes. Two restrictions bite:

**No Booleans, and openings must be pre-subtracted:** *"within the scope of the
IFC4 Reference View this relationship is a logical relationship, the void is
already part of the geometry."* This would be painful for a general geometry model
and is **free for ours**: ADR 0001 made every wall axis-aligned and every
structural opening a rectangle in it, so a wall with *n* openings decomposes
**exactly** into a set of axis-aligned boxes. The `Body` is a set of
`IfcExtrudedAreaSolid`, and no `IfcBooleanResult` appears anywhere in the file.

**No space boundaries and no element connectivity.** RV's *Object Connectivity*
group covers Spatial Structure, Port Connectivity, Building Service Connectivity
and Element Filling, and nothing else.

### Space boundaries are refused for a reason that is not the restriction

The ticket called `IfcRelSpaceBoundary` "where the real decision is, because it is
what makes the model useful downstream". Useful to **whom** is the answer:
2nd-level boundaries exist for *"energy analysis, lighting analysis, fluid
dynamics"*, and this engine holds no U-values, no glazing specification and a
`t_ext_total` that is `engine_choice` and provisional. Authoring them feeds an
analysis tool a model it will compute nothing true from — the file-structure form
of the omission failure this same ticket worried about at the property level.

1st-level is the architectural reading and is the genuinely arguable one. Refused
because nothing is lost: the geometry is exact integer millimetres and Space
polygons are finished-face, so adjacency is **derivable exactly** by any receiver.

**And it is precluded by nothing.** `CONTEXT.md`'s **Wall segment** — the stretch
of one Wall separating one specific room pair — *is* a 2nd-level space boundary,
with `CorrespondingBoundary` being the twin across the wall. The relation is
already materialised. If analysis-grade IFC enters scope, one spec section changes.

### The rule that decides most of the file

**A property present is a claim; a property absent means unknown.** Registered in
§8.5 and — the part that makes it real — **asserted by the export gate**, so the
day someone helpfully fills one in, the export fails.

Omitted: `LoadBearing` (`IfcBoolean`, no third state, and ADR 0001 left it
*unknown, not false*), `AcousticRating` (`t_party = 280` was **derived** from a
50 dB requirement, never tested — writing 52 dB is the C8 compliance claim),
`FireRating`, `ThermalTransmittance`, `PubliclyAccessible`, and
**`HandicapAccessible`**, where *Brief schema and parsing contract* refused
accessibility outright so `TRUE` breaches C8 and `FALSE` is a claim about a plan
nobody assessed. `IsExternal` is what stops this being laziness — ADR 0003's ring
knows it, so it is written and checked.

### Everything else

- **`IfcWall`, never `IfcWallStandardCase`.** IFC4.3: *"The entity
  `IfcWallStandardCase` has been deprecated, `IfcWall` with
  `IfcMaterialLayerSetUsage` is used instead."* Legal in IFC4 today, so it costs
  nothing and deletes a migration. ⚠️ **This corrects ADR 0010's own
  justification** — *"IFC wants it. `IfcWallStandardCase` carries
  `IfcMaterialLayerSetUsage`"* — whose reasoning stands and whose entity name does
  not.
- **Annotation-free, stated rather than implied**, on three independent grounds:
  ADR 0002 made annotation derived; IFC has no dimension-chain concept at all; and
  the only real IFC drawing system is **Bonsai's, which is GPL**. Nothing is lost —
  the tag's *content* travels as `IfcSpace.Name`, `LongName` and `NetFloorArea`.
- **Two vocabularies, two fields.** `Name` = the canonical ergonomic key,
  `LongName` = the `AZ` label. This **consumes** *Two room vocabularies in one
  file*'s mapping rather than deciding it. Azerbaijani is safe in SPF via
  `\X2\…\X0\` escapes — the mirror of the DXF finding that forced R2007 because no
  legacy code page encodes `ə`.
- **The area convention travels on `IfcBuilding`**, in a set that deliberately does
  **not** wear the reserved `Pset_` prefix, and states `IsGIA = FALSE` explicitly —
  a reader assuming GIA is wrong by the partition footprint, **5.7 %** at the
  shipped `t_int`.
- **`TrueNorth` only when the Brief states one; never defaulted to 0**, which would
  assert north = +Y. `IfcSite` is authored as a bare structural placeholder with no
  coordinates; `IfcMapConversion` never.
- **A third gate.** Schema-clean under `ifcopenshell.validate(express_rules=True)`
  plus **11 engine assertions**, and it gates whether a file is written exactly as
  the Drawing check gates DXF — kept out of `rules.json` for the Drawing check's
  own reason: it judges the *file*, not the *Plan*, and a Plan must never be
  rejected for an exporter defect. Two of the eleven are the ones that would
  otherwise ship a file that validates cleanly and says something untrue: **Σ
  `NetFloorArea` = the Plan's `ümumi sahə`**, and **the omissions asserted**. A
  third catches the one asymmetric layer set: the exterior wall is 20/380/100, so
  **winding decides which face the plaster lands on**, and getting it backwards
  produces a valid, plausible file with the render on the inside.

### ⚠️ The finding that bites hardest, and it is not about IFC

**The Plan has no vertical dimension.** A Wall is a centreline and a thickness; a
Space is a polygon. No ceiling height, storey height, room height, opening head
height or sill height exists anywhere in `room-constraints.json`,
`acceptance-bar.md`, `brief.md` or `CONTEXT.md`.

IFC is only the first consumer that cannot proceed without one. **Two artefacts
already assume it and predate this ticket:** `annotation.md` ships a door schedule
with `Structural opening W × H` and a window schedule with `Structural opening
W × H` and `Sill height` — three columns unfillable from the model — and
`CONTEXT.md`'s **Storey** exists, in its own words, *"because the model would
otherwise have to invent it on export"*, while carrying no height for export to
use.

Nothing owned it. *Opening placement rules* writes `openings.md` and its body does
not mention height at all. Now ticketed as *The Plan has no vertical dimension, and
three artefacts already assume one*. The spec names the four inputs and **refuses
to default any of them** — §8.1 binds the document as much as the file.

### ⚠️ Two costs recorded rather than smoothed

**Integer-millimetre exactness does not survive this boundary.** ADR 0001 §6's
metres mean 150 mm is 0.15 m, which binary floating point cannot hold. No defect
follows and every BIM tool tolerances it, but the division of labour is now
explicit: **the DXF is the exact export, the IFC is the interoperable one.**
Authored quantities are unaffected — `NetFloorArea` is computed in integer mm² and
written, never re-derived from exported geometry.

**C2's Revit round-trip is still priced at zero, because nobody has priced it.**
The export research's §4, which was to price it, **was never written**. This spec
does not pretend otherwise; it records the one concrete untested risk on file —
whether Revit's importer handles `IfcIndexedPolyCurve` identically to
`IfcPolyline`, which *"could not be confirmed"* — as a named pre-build test, and
leaves the rest in the *Revit round-trip specifics* fog patch.

### Market check

Of eleven products surveyed, IFC output is rare and conceptual where it exists.
**ARCHITEChTURES** is the only credit-card-purchasable IFC-for-architects product
and sells its file as *"a starting point to generate take offs and estimates"* at
LOD 200+ — which is why §8's quantity sets, not §5's geometry, are the part that
earns its keep. **Forma** ships IFC 4.3 beta and calls it *"the conceptual BIM
model"*. **Finch** has no IFC at all and its RVT export supplies *"generic wall
types"* and *"generic Finch doors"* with a documented manual-swap workflow.
Snaptrude's, Synaps's and Digital Blue Foam's IFC claims are absent from their own
documentation.

The gap that is actually occupiable is **not geometric fidelity** — it is that our
walls are not generic. Every layer thickness traces to an Azerbaijani document with
a `conf` flag, every door names a catalogue key, and every quantity names its
measurement convention. That is §7 and §8, and it is the only place in this file
where we are ahead of the benchmark rather than behind it.
