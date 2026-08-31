# IFC export

What the engine writes into the `.ifc` file the Destination calls "valid IFC", and
what it deliberately does not.

Owed by *What IFC the engine actually emits*. Tooling was proved by *BIM and CAD
export stack* (`ifcopenshell` 0.8.5, LGPL core); this document specifies
**content**. Units, the wall reference line and the storey concept were already
fixed by ADR 0001 and `CONTEXT.md` and are carried here, not re-decided.

---

## 1. Who this file is for, and what is promised

The **recipient is a Practitioner** — an architect or designer the Homeowner
engages, who opens the file in Revit, ArchiCAD or a viewer and continues the work.
This is C2's pattern applied to an output: the Homeowner buys, the Practitioner
sets the standard the file is held to. A Homeowner cannot open an IFC file, so
they are not the audience for it; the Homeowner's outputs are the SVG preview and
the PDF.

The exchange is **one-way**. Nothing in v1 re-imports IFC, and nothing here claims
a round-trip. C2 promises only that the engine will not *preclude* a Revit
round-trip; §11 records what that promise costs and where it is paid.

**What the product may claim:** an IFC4 file that opens in any BIM tool, with real
walls carrying a real material build-up, spaces carrying **ten exact quantities** —
areas, perimeters, wall areas and volume — under a **named area convention and a
named vertical datum**, and typed doors and windows. A starting point for take-off
and for continued design.

**What it may not claim:** a permit set (C8), a thermal or energy model (§11), a
certified round-trip, or LOD above 200–250.

Market position, for calibration. Of eleven products surveyed
(`docs/research/competitive-landscape.md`), IFC output is rare and where it exists
it is conceptual: **ARCHITEChTURES** is the only credit-card-purchasable IFC-for-architects
product, sells its file as *"a starting point to generate take offs and estimates"*
at LOD 200+; **Autodesk Forma** ships IFC 4.3 in beta and calls its content *"the
conceptual BIM model"*; **Finch** has no IFC at all and its RVT export supplies
*"generic wall types"* with a documented manual-swap workflow; Snaptrude's,
Synaps's and Digital Blue Foam's IFC claims are absent from their own
documentation. The gap we can actually occupy is not fidelity of geometry — it is
that **our walls are not generic and our quantities are not estimates**: every layer
thickness traces to an Azerbaijani document with a `conf` flag, every space quantity
is exact because the model is integer millimetres, and both conventions those
numbers measure to are declared inside the file. §7 and §8 are where that shows up.

Note what the benchmark's own words concede — *"a starting point to generate take
offs and estimates"*. **Estimates** is the word §8 is aimed at.

## 2. Schema, model view, and the header

| | Decision |
|---|---|
| Schema | **IFC4 ADD2 TC1**, `FILE_SCHEMA(('IFC4'))` |
| Model view | **IFC4 Reference View V1.2**, held to strictly |
| Header | `ViewDefinition [ReferenceView_V1.2]` — **set explicitly** |
| Serialisation | SPF (`.ifc`), ISO 10303-21 |

### Why Reference View, and why the alternative does not exist

The ticket framed this as Reference View versus Design Transfer View. **Design
Transfer View is not a real option**, on three independent grounds:

- buildingSMART's own position, on their forum: *"Design Transfer View never
  materialised into an official MVD."* IFC4.3 publishes exactly two — Reference
  View and Alignment Based Reference View.
- The number of software products certified for Design Transfer View export is
  **zero**. Revit's IFC4 certification is **Reference View 1.2, export only**;
  IFC4 *import* certification exists for two products in the industry (Tekla,
  BridgeBIM). Declaring DTV would be declaring conformance to a view nothing is
  built to consume.
- The DTV documentation describes a *"higher fidelity one-way transfer of data and
  responsibility"* — not the round-trip it is usually invoked to buy.

So Reference View is not the cautious half of a fork; it is the only view with an
ecosystem. What matters is what it costs, and that is §2.1.

### 2.1 What Reference View actually restricts

RV is less restrictive than its reputation, and the three restrictions that do
bite reach back into the exporter. From the RV scope definition:

- **Swept solids are allowed.** `Body SweptSolid Geometry` — *"using extruded
  solid geometry or revolved solid geometry"* — is in scope, alongside
  tessellation. We are not forced to triangulate.
- **And the swept profile may be arbitrary.** RV1.2 carries four swept-solid
  templates — `PolyCurve`, `ParameterizedProfile`, `CompositeCurve`, `Composite` —
  and the first names `SweptArea = IfcArbitraryClosedProfileDef,
  IfcArbitraryProfileDefWithVoids` with `OuterCurve = IfcIndexedPolyCurve`. A
  concave profile is in scope, and this is quoted rather than assumed. → §6.1.
  Note which entity the view **prescribes** for the curve: §11's one named Revit
  risk is not avoidable inside RV.
- **No Booleans.** *"all other geometric models are out of scope of the IFC4
  Reference View, in particular Boolean operations required for Constructive Solid
  Geometry CSG."* → §5.
- **Openings are pre-subtracted.** *"within the scope of the IFC4 Reference View
  this relationship is a logical relationship, **the void is already part of the
  geometry**."* → §5.
- **Material layer sets are allowed, as data not as geometry.** Material
  dimensions are carried *"exclusively as alphanumeric information, and not as
  part of a dimension driven parametric shape representation."* → §7.
- **Not in RV at all:** space boundaries, and element-to-element connectivity.
  RV's *Object Connectivity* group covers Spatial Structure, Port Connectivity,
  Building Service Connectivity and Element Filling — and nothing else. → §11.

Everything the file needs is in scope: Property Sets, Quantity Sets, Material
Association, Object Typing, Spatial Decomposition, Element Voiding, Element
Filling, Body SweptSolid, FootPrint Geometry, Project Global Positioning, and the
`Name` / `Description` / `LongName` / `Tag` identity attributes.

### 2.2 The header is a claim, and it defaults to a false one

`ifcopenshell` writes `ViewDefinition [CoordinationView]` by default —
`CoordinationView` is the **IFC2x3** view name, and emitting it in an IFC4 file is
a declaration that is both wrong and silent. The exporter sets the string
explicitly and the check in §10 asserts it.

### 2.3 `IfcWallStandardCase` is never written

IFC4 still permits it and `ifcopenshell` still instantiates it, but IFC4.3 states:
*"The entity `IfcWallStandardCase` has been deprecated, `IfcWall` with
`IfcMaterialLayerSetUsage` is used instead."*

We write **`IfcWall` + `IfcMaterialLayerSetUsage`**, which is legal in IFC4 today
and is the 4.3 spelling of the same thing. It costs nothing now and removes a
schema migration later.

> **ADR 0010 needs a one-line correction.** Its justification for the layer set
> reads *"IFC wants it. `IfcWallStandardCase` carries `IfcMaterialLayerSetUsage`."*
> The reasoning is untouched — the entity that carries it is `IfcWall`.

## 3. Spatial structure

```
IfcProject
 └─ IfcSite                      (structural placeholder; no coordinates — §9.3)
     └─ IfcBuilding              (carries the area-convention property set — §8.4)
         └─ IfcBuildingStorey    (exactly one; Elevation = 0.0)
             ├─ IfcRelAggregates          → IfcSpace  (one per Space)
             └─ IfcRelContainedInSpatial… → IfcWall, IfcDoor, IfcWindow
```

The split on the last two lines is not cosmetic. `IfcSpace` is itself a spatial
structure element, so it **decomposes** the storey via `IfcRelAggregates`; physical
elements are **contained in** it via `IfcRelContainedInSpatialStructure`. Reversing
these is a classic malformed-IFC error and was verified the right way round during
the export research.

Exactly one `IfcBuildingStorey`, per `CONTEXT.md`'s **Storey** — which exists, in
its own words, "because the model would otherwise have to invent it on export".
This is that export.

## 4. Walls

| Aspect | Decision |
|---|---|
| Entity | `IfcWall`, `PredefinedType = STANDARD` |
| Type | `IfcWallType` per thickness class, `IfcRelDefinesByType` |
| Axis | `Axis` representation = the Wall centreline (ADR 0001) |
| Body | `Body` / `SweptSolid` — a **set** of axis-aligned `IfcExtrudedAreaSolid` (§5) |
| Placement | `IfcLocalPlacement` on every wall — **mandatory**, see §10 |

`PredefinedType = STANDARD` is chosen for what it does *not* say. It asserts a wall
extruded vertically at constant thickness along its path — which our model
guarantees. `PARTITIONING` would assert non-load-bearing, and a Wall's
`load_bearing` is *unknown, not false* (ADR 0001). §8.3 is the same decision
applied to the property.

**Three wall types ship**, one per entry in the region profile's thickness
catalogue, each carrying its own `IfcMaterialLayerSet` (§7):

| `IfcWallType.Name` | Total | Where it occurs |
|---|---|---|
| `AZ_brick_int_150` | 150 mm | interior tiling edges |
| `AZ_brick_party_280` | 280 mm | Envelope edges typed `party` (ADR 0003) |
| `AZ_brick_ext_500` | 500 mm | Envelope edges typed `exterior` |

The reference line is the **centreline**, with `OffsetFromReferenceLine = −t/2` on
the layer set usage, per ADR 0001 §7 — geometry and IFC semantics agreeing rather
than the file relying on an importer honouring the attribute.

**Winding is load-bearing for exterior walls and only for them.** The interior and
party layer sets are symmetric (15/120/15, 15/250/15), so their layer order cannot
be observed. The exterior set is **not** symmetric — 20 finish / 380 leaf /
100 insulation — so `DirectionSense` and the layer order together decide which
face the finish lands on. Exterior wall axes wind with the Envelope's edge ring
(ADR 0003), layers are listed **inside → outside**, and `DirectionSense` is set so
layer 1 lies on the interior side. §10 asserts it, because getting it backwards
produces a file that is valid, plausible, and has the plaster on the outside.

## 5. Openings, doors and windows

Reference View requires the void to be part of the geometry already and forbids
Booleans. Both are satisfied without compromise, and the reason is ADR 0001:
**every wall is axis-aligned and every structural opening is a rectangle in it**,
so a wall with *n* openings decomposes exactly into a small set of axis-aligned
boxes — the pieces beside, above and below each opening.

- The `Body` representation is `SweptSolid` with **one `IfcExtrudedAreaSolid` per
  piece**. No `IfcBooleanResult` appears anywhere in the file.
- The decomposition is **exact**, not approximate. Integer millimetres in, and the
  pieces' total volume equals `Qto_WallBaseQuantities.NetVolume` by construction —
  which §10 checks, so the day the decomposition is wrong the export fails rather
  than shipping a wall with a hole in the wrong place.
- `IfcOpeningElement` + `IfcRelVoidsElement` are still authored, as RV's *Element
  Voiding* intends: a logical record of where the opening is, **not** an
  instruction to subtract again.
- `IfcDoor` / `IfcWindow` fill the opening via `IfcRelFillsElement` (RV's *Element
  Filling*).
- `IfcDoorType` / `IfcWindowType` per **region-profile catalogue key**, so the
  file names the door it used rather than shipping a generic one. This is the
  single place the file is better than the market benchmark, which supplies
  "generic wall types" and "generic doors" with a documented manual-swap step.
- A **cased opening** (`CONTEXT.md`) is an `IfcOpeningElement` with no filling
  element — not an `IfcDoor` with a null leaf.

Opening geometry is owed by *Opening placement rules* for the plan dimensions.
The vertical half is **no longer owed** — catalogue `H`, the head datum and the
derived sill are all shipped profile data, and §12 says where each is read from.

## 6. Spaces

| Attribute | Value |
|---|---|
| Entity | `IfcSpace`, `PredefinedType = SPACE` |
| `Name` | the **canonical ergonomic key** — `bedroom_double`, `wc` |
| `LongName` | the **`AZ` display label** — `yataq otağı`, `ayaqyolu` |
| `Description` | absent |
| `Body` | `SweptSolid`, **one** `IfcExtrudedAreaSolid`, the Space polygon extruded `h_clear` (§12) |
| `FootPrint` | the Space polygon |

The Space polygon is the one ADR 0010 defines: bounded by **finished** inner
faces. The `Body` and `FootPrint` are that polygon and nothing else, which is what
makes `NetFloorArea` exact rather than adjusted on export (§8.4).

**`h_clear`, not storey height.** This sentence read *"extruded to storey height"*
until ADR 0012 **deleted `h_storey`**, at which point it named a quantity the model
no longer has — and named it for the one entity whose height is least ambiguous. A
room is floor to finished ceiling, which is `h_clear` and nothing else. Wall bodies
are `h_clear` too (ADR 0012), so Spaces and walls are **coplanar top and bottom**:
the file is one slab of rooms and walls at a single height, with no `IfcSlab` and no
`IfcRoof` above either.

### 6.1 A Space is one or two rectangles, and still one extrusion

ADR 0014 makes a Space `erode(⋃ parts, t_int/2)` — a rectilinear polygon with at
most **two** reflex corners and at most **8 vertices**, exact on integer
millimetres. The `Body` stays **one**
`IfcExtrudedAreaSolid` over **one** `IfcArbitraryClosedProfileDef`. An L is one
closed profile swept once; no Boolean appears, which is the restriction Reference
View actually carries (§2.1).

**Reference View permits this, and it is verified rather than assumed.** RV1.2's
`Body SweptSolid PolyCurve Geometry` concept template, verbatim:

```
Items                            = IfcExtrudedAreaSolid, IfcRevolvedAreaSolid
Items[1..n].SweptArea            = IfcArbitraryClosedProfileDef, IfcArbitraryProfileDefWithVoids
Items[1..n].SweptArea.OuterCurve = IfcIndexedPolyCurve
```

ADR 0014 refused to claim this and handed it here. It is now claimed, from the
primary source.

**The alternative — one extrusion per Part — is refused, and §5 is not a precedent
for it.** A wall with openings *cannot* be one profile without a Boolean, so its
decomposition into pieces is **forced**; a Space's is **free**. Two abutting solids
share a face, and viewers commonly draw a seam along it — a line through the middle
of a room that is not a wall, which is §11's part-pair failure arriving through
geometry instead of through boundaries. An `IfcSpace` is a spatial element and a
room is one volume; splitting it would publish the solver's decomposition, which is
an implementation artefact and no part of the design.

> **The rectangles this was weighed against do not exist.** ADR 0014 framed the
> arbitrary profile as a risk taken *against the rectangles §5 leans on*. §5 leans
> on no `IfcRectangleProfileDef`: the entity census of the authored model in the
> export research is **12 `IfcArbitraryClosedProfileDef`, 13 `IfcIndexedPolyCurve`,
> zero `IfcRectangleProfileDef`** — `add_wall_representation` builds an arbitrary
> closed profile for a plain rectangular wall. **An L profile introduces no new
> entity type**, and the unconfirmed `IfcIndexedPolyCurve`-versus-`IfcPolyline`
> Revit risk of §11 already sits on every wall in the file. The concave Space adds
> nothing to it, and RV's own template *mandates* `IfcIndexedPolyCurve`, so it is
> not avoidable inside this view in any case.

**Author it with `geometry.add_slab_representation`**, which the export research
verified producing `SweptSolid` / `IfcExtrudedAreaSolid` from an arbitrary polyline
with a correctly unit-converted profile. `add_wall_representation` must not be
abused for Spaces.

`FootPrint` is the same polygon, so it is concave too, and `NetFloorArea` stays
exact by construction because the polygon **is** the area.

**Two vocabularies, two fields, on purpose.** `Name` is machine-stable, region-free
and survives a profile change; `LongName` is what a human reads and matches the
room tag on the sheet. This consumes the mapping owed by *Two room vocabularies in
one file* — it does not decide it. If that ticket changes the mapping, this file
changes with it and nothing here is re-opened.

Azerbaijani text is safe in SPF: ISO 10303-21 encodes non-ASCII as `\X2\…\X0\`
escapes and `ifcopenshell` writes them. This is the mirror of the DXF finding that
forced an R2007 floor because **no legacy code page encodes `ə`** — IFC has no
equivalent constraint, so the schema floor here is set by §2, not by the alphabet.

## 7. Materials and layer sets

The two-step, which is the correct IFC pattern and the one the export research
verified:

- `IfcMaterialLayerSet` → assigned to the **`IfcWallType`** (shared by all
  occurrences of that type).
- `IfcMaterialLayerSetUsage` → on each **`IfcWall`** occurrence, carrying
  `LayerSetDirection = AXIS2`, `DirectionSense` per §4, and
  `OffsetFromReferenceLine = −t/2`.

Layers are read from `profiles.AZ.construction.catalogue.brick` — never hard-coded
— so the file moves when the profile moves:

| Type | Layers, inside → outside | Total |
|---|---|---|
| `AZ_brick_int_150` | plaster 15 · brick 120 · plaster 15 | 150 |
| `AZ_brick_party_280` | plaster 15 · brick 250 · plaster 15 | 280 |
| `AZ_brick_ext_500` | plaster 20 · brick 380 · insulation 100 | 500 |

`IfcMaterial.Name` carries a stable technical key (`brick`,
`cement_sand_plaster`, `insulation`) with `Category` set to IFC's own vocabulary.
Material names are **not** translated — the profile publishes no Azerbaijani
material names and inventing them would be the C8-adjacent move ticket 25 was
built to avoid.

Under RV these thicknesses are **alphanumeric information**: the geometry in §5
carries the real total independently, and no importer is asked to derive the body
from the layer set.

> ⚠️ Two flags carried from the profile rather than smoothed here. **`t_ext_total`
> is `engine_choice` and PROVISIONAL** — blocked on Baku's degree-day figure, and
> its 20 mm finish share is *unsupported* by AzDTN 2.12-4\* Əlavə 8\*. And the
> external set as published leaves **insulation as the outermost layer with no
> external render over it**. The exporter encodes what the profile says; both are
> the profile's to fix, and the file inherits whatever it fixes them to.

## 8. Property sets and quantity sets

### 8.1 The rule the whole file obeys

**The engine writes only what it knows. A property that is absent means unknown; a
property that is present is a claim.**

This is not caution, it is the difference between a Practitioner trusting the rest
of the file and discarding all of it. `IsExternal` is the counter-example that
proves it is not laziness: ADR 0003's edge ring **does** know exterior from party,
so `IsExternal` is written on every wall and must agree with the ring.

§8.5 is the register of what is omitted and why, and §10 **asserts the omissions**
so the principle is a test rather than a comment.

### 8.2 Spaces

**The rule, which is §8.1 one level down.** `Qto_SpaceBaseQuantities` has thirteen
quantities and this file used to name four, leaving nine in neither the written set
nor the omission register — forgotten rather than declined, which is the one state
§8.5 exists to make impossible. The rule that decides all thirteen:

> **Write a quantity when IFC4's definition names the same plane and the same
> exclusions our model computes to. Omit it when the definition names a plane or a
> convention we do not have — and register the omission.**

It is applied per quantity below rather than per intuition, and it does not sort by
`Gross`/`Net`: `GrossPerimeter` is written and `GrossVolume` is not.

| Set | Property | Value |
|---|---|---|
| `Pset_SpaceCommon` | `IsExternal` | `FALSE` |
| | `NetPlannedArea` | the Room's `target_area`, m² — §8.2a |
| | `Reference` | **not written** — §8.5 |
| | `GrossPlannedArea`, `PubliclyAccessible`, `HandicapAccessible` | **not written** — §8.5 |
| `Qto_SpaceBaseQuantities` | `NetFloorArea` | Space polygon area, m² |
| | `GrossPerimeter` | Space polygon perimeter |
| | `NetPerimeter` | that perimeter **less every hosted opening's structural width** |
| | `Height` | `h_clear` — §8.2b |
| | `NetVolume` | `NetFloorArea` × `h_clear`, exact |
| | `GrossWallArea` | `GrossPerimeter` × `h_clear` |
| | `NetWallArea` | that, less Σ structural `W × H` of the Space's hosted openings |
| | `GrossCeilingArea`, `NetCeilingArea` | = `NetFloorArea`; flat ceiling, no interior elements |
| | `GrossFloorArea`, `GrossVolume` | **not written** — §8.5 |
| | `FinishFloorHeight`, `FinishCeilingHeight` | **not written** — §8.5 |

Ten written where there were four. Every one is **exact**, not estimated, for the
same reason §8.3 gives on walls: the model is integer millimetres. This is the part
of the file a take-off tool actually reads, and the market benchmark ships a thinner
set than this.

**`NetPerimeter` was specified wrong and is corrected here.** It read *"Space
polygon perimeter"*, but IFC4 defines `NetPerimeter` as excluding *"those parts of
the perimeter that are created by virtual boundaries and openings (like doors)"*.
The polygon perimeter is `GrossPerimeter` — *"at the outer contour"* — and a Space
has no thickness, so the outer contour is the polygon. Both are now written, with
the old number under its correct name. The subtraction is available exactly:
openings are hosted and named by the Wall segment they pierce, which is
Room-anchored (§11).

**A concave Space changes none of this.** Perimeter is perimeter, area is area, and
the reflex corner of an L adds faces rather than machinery — the same finding ADR
0014 recorded for the dimension chains.

#### 8.2a `NetPlannedArea` — the programme, beside the delivery

IFC4: *"Total planned net area of the object. Used for programming the object."*
That is `Room.target_area` exactly, and writing it is §8.1 permitted rather than
strained — a Room's target is a claim about the **programme**, which the Brief
states and `resolve` completes, not a claim about the building.

It also pays a debt from *The whole of C2's user*, which found that
`Room.target_area` and the delivered `Space` area **render identically** on the
Homeowner surface, so the Brief reads as promising an area the plan may not deliver.
IFC has a first-class place for the distinction the drawing does not: planned and
achieved sit two properties apart on the same entity, and a Practitioner reads the
delta without being told to. The Homeowner-facing half of that defect is still owed
by its own holder; this closes the Practitioner half.

**It is the *resolved* target, stated or defaulted.** `brief.md` makes
`StatedRoom.target_area` optional and fills the gap from the standards table, so
some of these numbers came from the Homeowner and some from `profiles.AZ`. The
distinction is real and it does **not** travel: the Brief's `Assumption` list is the
place it lives, and this file authors no annotation to carry it (§11). What is
written is the number the engine actually solved against, which is what a
Practitioner reading a delta needs. A reader who wants to know which targets the
client chose asks for the Brief, and the product hands it over — C4 makes it the
real interface.

`GrossPlannedArea` is omitted — gross planned area is the enclosure convention
`GrossFloorArea` is refused for, arriving through the programme instead.

#### 8.2b `Height` is written, and the understatement is declared not hidden

IFC4 defines `Qto_SpaceBaseQuantities.Height` as *"from base slab without flooring
to ceiling without suspended ceiling."* `h_clear` is **finished floor to finished
ceiling** — AzDTN 2.7-2 cl. 5.8's own quantity, *döşəmədən tavanadək*. In a real
building those differ by the floor build-up, and ADR 0012 **refused to source one**.

The number is written anyway, and the reasoning is ADR 0012's own, not a softening
of §8.1. This model has **no floor build-up layer at all** — no `IfcSlab`, no
`IfcCovering`, no floor in any layer set — so slab top and finished floor are the
same plane *in this file*, and `Height = h_clear` is exactly true of the model.
More decisively: **the geometry has already committed to it.** The Space body and
every wall body are `h_clear` tall standing on elevation 0, so anyone who measures
the model gets this number. Omitting the quantity would hide in the property set
what the solid states plainly, and leave a take-off tool blank on every room in the
file. ADR 0012 declared this exact understatement for wall bodies — *"it is an
understatement, and the export says so rather than padding it"* — and a Space is
the same solid decision seen from the other side.

*Says so* is discharged by **§8.4a**, which declares the vertical datum on
`IfcBuilding` the way §8.4 declares the area convention. A reader who needs slab to
ceiling learns from the file that they were not given it.

**`FinishFloorHeight` and `FinishCeilingHeight` are omitted, and the line between
them and `Height` is the point.** They *are* the build-up: flooring thickness and
suspended-ceiling depth. Writing `0` would assert the real building has no flooring
and no dropped ceiling, which is a claim about the world rather than a description
of the model, and a length has no third state any more than
`Pset_WallCommon.LoadBearing`'s boolean does (§8.5). ADR 0012 keeps cl. 5.8's
corridor allowance **inert** for precisely this reason: a dropped ceiling later is a
data change, and `FinishCeilingHeight = 0` today would have to be un-said.

**`GrossVolume` is omitted** on §8.2's oldest argument: it is `GrossFloorArea`'s
partner, and a reader handed `GrossVolume` divides by `Height` and believes they
have the gross floor area this file deliberately refuses. `GrossFloorArea` is
omitted per *Area measurement convention* — it would require attributing half of
each bounding partition to the space, a different convention from the one the
drawing quotes and the acceptance bar gates on. A quantity that disagrees with the
room tag beside it is the exact defect ADR 0010 exists to prevent, arriving through
the quantity set instead of through annotation. Shipping its volume twin would let
it in by the back door.

### 8.3 Walls

| Set | Property | Value |
|---|---|---|
| `Pset_WallCommon` | `IsExternal` | from ADR 0003's edge ring |
| | `Reference` | the `IfcWallType` name |
| | `LoadBearing` | **omitted** |
| | `FireRating`, `AcousticRating`, `ThermalTransmittance` | **omitted** |
| `Qto_WallBaseQuantities` | `Length`, `Height`, `Width` | `Width` = layer-set total |
| | `GrossFootprintArea`, `GrossSideArea`, `NetSideArea`, `NetVolume` | computed |

`AcousticRating` is the one worth explaining, because it looks knowable and is
not. `t_party = 280` was *derived from* AzDTN 2.7-2's 50 dB requirement — brick 250
plus 15 plaster each side computing to about 52 dB, where 120 fails at 49. That is
a **design derivation, not a tested rating**, and writing `52 dB` into a property
whose readers treat it as a laboratory figure is a compliance claim C8 forbids.
The derivation stays in the profile where its provenance is legible.

The `Qto` set is the part of this file the market benchmark actually sells — its
IFC is *"a starting point to generate take offs and estimates"* — and every number
in it is exact rather than estimated, because the model is integer millimetres.

### 8.4 The area convention travels with the file

A `NetFloorArea` read without its convention is the silent mismatch ADR 0010 was
written to kill. The file therefore self-describes, in a property set on
**`IfcBuilding`** — one declaration, whole-building scope:

```
BimEngine_AreaConvention                 (IfcPropertySet on IfcBuilding)
  Convention          = "az_umumi_sahə"
  Source              = "Area Qaydalar cl. 3.8, measured per cl. 3.2"
  MeasuredTo          = "finished inner faces, at floor level"
  ExcludesPartitions  = TRUE
  ExcludesSkirtings   = TRUE
  IsGIA               = FALSE
```

Not `Pset_`-prefixed: that prefix is reserved for buildingSMART-published sets, and
a custom set wearing it is a false claim of standardisation — the same class of
error as §2.2's header.

`IsGIA = FALSE` is stated rather than implied. `ümumi sahə` **sums room areas and
does not count partitions**, so a reader who assumes GIA reads every number in
this file wrong by roughly the partition footprint — measured at **5.7 %** for the
shipped `t_int` of 150.

### 8.4a The vertical datum travels with the file too

§8.4 exists because a `NetFloorArea` read without its convention is a silent
mismatch. `Height` and `NetVolume` have exactly the same exposure — §8.2b writes
`h_clear` into a quantity IFC4 defines from the **base slab** — so the same move is
made on the vertical axis, in a second set on `IfcBuilding`:

```
BimEngine_VerticalConvention             (IfcPropertySet on IfcBuilding)
  Datum               = "h_clear"
  Source              = "AzDTN 2.7-2 cl. 5.8, döşəmədən tavanadək"
  MeasuredTo          = "finished floor to finished ceiling"
  IncludesSlab        = FALSE
  IncludesFloorBuildUp = FALSE
  IncludesSuspendedCeiling = FALSE
```

Not `Pset_`-prefixed, for §8.4's reason. Two sets rather than rows added to
`BimEngine_AreaConvention`, because a vertical datum inside a set named
*AreaConvention* is the same misfiling this pair of sections exists to prevent.

`IncludesSlab = FALSE` is the sentence a reader needs and the one ADR 0012 wrote:
**a wall body is floor-to-ceiling, not slab-to-slab.** Every height in this file
understates the built dimension by a floor build-up that has no Azerbaijani source,
and the file says so rather than padding it. There is no `h_storey` here to look
for — ADR 0012 deleted it, and §12 records why.

### 8.5 Omission register

Written into the spec so that "unknown" is distinguishable from "forgotten", and
asserted by §10.

| Omitted | Because |
|---|---|
| `Pset_WallCommon.LoadBearing` | `IfcBoolean`, no third state. `load_bearing` is *unknown, not false* (ADR 0001); structural reality is deferred, not decided |
| `Pset_WallCommon.AcousticRating` | derived, not tested — §8.3 |
| `Pset_WallCommon.FireRating` | no source; a rating is a test result |
| `Pset_WallCommon.ThermalTransmittance` | `t_ext_total` is itself provisional and blocked on Baku's degree-day figure |
| `Pset_SpaceCommon.HandicapAccessible` | *Brief schema and parsing contract* **refused** accessibility. `TRUE` is a C8 breach; `FALSE` is a claim about a plan nobody assessed |
| `Pset_SpaceCommon.PubliclyAccessible` | single dwelling; the question is not modelled |
| `Pset_SpaceCommon.Reference` | it would restate `IfcSpace.Name`, which already carries the canonical ergonomic key — ADR 0002's duplicated state arriving in a property set. IFC4.3 **deprecates** the property, so this is §2.3's move on a second entity: write the spelling that survives the schema migration |
| `Pset_SpaceCommon.GrossPlannedArea` | the gross **enclosure** convention `GrossFloorArea` is refused for, arriving through the programme — §8.2a |
| `Qto_SpaceBaseQuantities.GrossFloorArea` | wrong convention — §8.2 |
| `Qto_SpaceBaseQuantities.GrossVolume` | `GrossFloorArea`'s partner: divided by `Height` it hands back the gross area this file refuses — §8.2b |
| `Qto_SpaceBaseQuantities.FinishFloorHeight` / `FinishCeilingHeight` | they **are** the floor build-up and the dropped ceiling, and `0` asserts the building has neither. A length has no third state, exactly as `LoadBearing`'s boolean has none. ADR 0012 keeps cl. 5.8's corridor allowance *inert* so a dropped ceiling stays a data change — §8.2b |
| `IfcSite.RefLatitude` / `RefLongitude` / `RefElevation` | the site is out of scope — §9.3 |
| `IfcOwnerHistory` | optional in IFC4; nothing here has an authoring history to state |
| `IfcRelAssociatesClassification` on `IfcSpace` | **declined, not unavailable** — it is in RV1.2 scope and we could conform. 431 `IfcSpace` entities across six published models classify **zero**; Revit lands the code on a DirectShape rather than a Room. ADR 0047, and §11 for the price |
| `IfcSpace.ObjectType` | it would restate `Name` a third time — ADR 0002's duplicated state, the same objection this register sustains against `Pset_SpaceCommon.Reference`. `PredefinedType` stays `SPACE` — ADR 0047 |

## 9. Units, precision, georeferencing, encoding

### 9.1 The declaration

| Unit | Declaration |
|---|---|
| `LENGTHUNIT` | `IfcSIUnit` **METRE**, no prefix |
| `AREAUNIT` | `SQUARE_METRE` |
| `VOLUMEUNIT` | `CUBIC_METRE` |
| `PLANEANGLEUNIT` | `RADIAN` |
| `Precision` on the 3D `IfcGeometricRepresentationContext` | `1e-6` (= 0.001 mm) |

Metres, per ADR 0001 §6. Two things support it and one thing costs.

Supporting: it is the unit under which `ifcopenshell`'s SI-native API path is
exercised, and the one under which `geometry.add_door_representation` does not
emit a schema-invalid negative extrusion depth. And quantity sets are in m²/m³
regardless, so a metre length unit makes the file one unit system instead of a
mixed one.

The door bug is **re-verified here rather than inherited** (C11):
`experiments/environment/env_check.py` calls the same helper under both unit
assignments on the pinned `ifcopenshell` 0.8.5 — **metres gives 8 solids with a
minimum depth of 0.005; millimetres gives a non-positive depth** and violates the
`IfcExtrudedAreaSolid` where-rule `Depth > 0`. ADR 0001 §6 stands on a measurement
taken twice, by two tickets, a year apart in map-time.

### 9.2 The cost, stated rather than hidden

**Integer-millimetre exactness does not survive the IFC boundary.** 150 mm is
0.15 m, which is not representable in binary floating point; a consumer
re-deriving thicknesses from our geometry gets 149.999… mm. Every BIM tool
tolerances this and no defect follows, but the consequence is worth naming
plainly:

> The **DXF is the exact export** and the **IFC is the interoperable one.** Where
> a number must be exact to the millimetre, the authority is the model, and the
> drawing that quotes it is the DXF.

Authored quantities do not inherit this. `NetFloorArea` is computed in the model in
integer mm² and written as a decimal — it is not re-derived from the exported
geometry.

### 9.3 North, and the silent Brief

`TrueNorth` on `IfcGeometricRepresentationContext` states a **direction inside the
model's own coordinate system** — "model +Y is *n* degrees off true north". It is
not a location and asserts no siting. What would assert a siting is
`IfcSite.RefLatitude`/`RefLongitude` or `IfcMapConversion`, and the site is out of
scope.

- Brief **states** a north angle → write `TrueNorth`. It is the Homeowner's own
  information and dropping it loses something real.
- Brief is **silent** → **omit the attribute entirely.** Never default it to 0°,
  which asserts north = +Y — a claim the engine invented. This is §8.1 applied to
  an attribute rather than a property.
- `IfcMapConversion`, `IfcProjectedCRS`, `IfcSite` coordinates → **never**, under
  any circumstances.

`IfcSite` is still authored as a structural placeholder so the spatial chain is
conventional, with no geometry and no coordinates. An `IfcSite` that says nothing
asserts nothing.

## 10. The IFC check — a third gate, and why it is not in `rules.json`

**No `.ifc` file is written unless the check passes.** This mirrors the **Drawing
check** that gates whether a DXF is written, and it is deliberately kept out of
`data/acceptance/rules.json` for the same reason:

> `rules.json` decides whether a **Plan** is a survivor — it is about the design.
> The IFC check decides whether a **file we authored** is well-formed — it is about
> the encoding. A Plan must never be rejected for something the exporter got
> wrong, and a survivor that fails IFC validation is an engine bug, not a bad
> plan. Same reasoning as the Drawing check, same conclusion.

So v1 has **three** checks, and they are about three different things: the
Acceptance bar (is this Plan good), the Drawing check (is this sheet issuable),
the IFC check (is this file honest).

**Schema layer.** `ifcopenshell.validate(f, express_rules=True)` must return **0
issues**. Note `pytest` is a *runtime* dependency of this call — it imports
`_pytest.assertion` and raises `ModuleNotFoundError` without it. Undocumented
upstream, found the hard way during the export research, and now pinned as a
direct dependency in `requirements.txt` with that reason attached.

**Engine layer.** Sixteen assertions the schema check cannot make — with one
exception, measured rather than assumed:

| # | Assertion | Catches |
|---|---|---|
| 1 | Every `IfcProduct` with a `Representation` has an `ObjectPlacement` | IFC4 WR1 — the single most likely defect in a generated file; `assign_representation` does not create one. ⚠️ **Redundant, and kept anyway:** `experiments/environment/env_check.py` builds exactly this defect and the express rules **do** catch it (1 issue). Kept because it is cheap, because it names the defect in our own vocabulary, and because it is the one assertion whose redundancy is *verified* rather than assumed |
| 2 | Header `ViewDefinition` is `ReferenceView_V1.2` | the `CoordinationView` default (§2.2) |
| 3 | Zero `IfcBooleanResult` / `IfcBooleanClippingResult` | RV conformance and §5 |
| 4 | Zero `IfcWallStandardCase` | §2.3 |
| 5 | Zero `IfcRelSpaceBoundary*`, zero `IfcRelConnectsPathElements` | RV conformance and §11 |
| 6 | Σ `Qto_SpaceBaseQuantities.NetFloorArea` = the Plan's `ümumi sahə`, ≤ 1e-4 m² | the file disagreeing with the sheet |
| 7 | Per wall: Σ piece volumes = `Qto_WallBaseQuantities.NetVolume` | a wrong opening decomposition (§5) |
| 8 | Per wall: `Qto…Width` = its `IfcMaterialLayerSet` total | geometry and layer set drifting apart |
| 9 | Exterior walls: layer 1 lies interior-side | plaster on the outside (§4) |
| 10 | Every row of §8.5's register is absent on every element it names — `LoadBearing`, `HandicapAccessible`, `PubliclyAccessible`, `Pset_SpaceCommon.Reference`, `GrossPlannedArea`, `GrossFloorArea`, `GrossVolume`, `FinishFloorHeight`, `FinishCeilingHeight`, the ratings, the `IfcSite` coordinates | §8.1 asserted, not trusted. The register is the assertion's input, so a row added to §8.5 and not to the exporter fails here |
| 11 | `IfcSpace` count = Plan Space count; every `IsExternal` agrees with ADR 0003's ring | silent element loss |
| 12 | Per `IfcSpace`: `Body` holds **exactly one** `IfcExtrudedAreaSolid`, over exactly one `IfcArbitraryClosedProfileDef` | §6.1's single-profile decision regressing to one extrusion per Part — which validates cleanly and draws a seam through the middle of a room |
| 13 | Every Space body depth **and** every wall extrusion depth = `h_clear` | §6 and §12 contradicting each other again, which is the defect this section of the file was written to close |
| 14 | Every Space profile is closed, rectilinear, on integer millimetres, with **at most 8 vertices** | ADR 0014's two-Part cap reaching the file. A third Part is a Proposal bug, and without this row it ships as valid geometry. ⚠️ **This read “at most one reflex corner” until ADR 0045 and it was UNSOUND** — reflex count was a proxy for Part count, and it rejects **43 %** of legitimate two-part Rooms (a T and a Z have two) while a three-Part bug presenting one reflex corner passes. Two rectangles sharing an edge produce exactly 4, 6 or 8 vertices — measured over all 1 543 corpus two-part Rooms as 4 ×27, 6 ×851, 8 ×665, max 8, no holes — so the bound never rejects valid output, and a three-Part staircase reaches 10 and is caught. Incomplete (three collinear flush Parts also give 4) but **sound**, which the predecessor was not |
| 15 | Per Space: `NetVolume` = `NetFloorArea` × `h_clear`; `GrossPerimeter` − `NetPerimeter` = Σ hosted opening structural widths; `GrossWallArea` − `NetWallArea` = Σ hosted opening structural `W × H` | the §8.2 quantity set drifting from the geometry it is computed from — assertion 7's argument applied to Spaces |
| 16 | `Pset_SpaceCommon.NetPlannedArea` present on every Space and equal to its Room's `target_area`; `BimEngine_AreaConvention` and `BimEngine_VerticalConvention` both present on `IfcBuilding` | a file whose numbers are exact and whose convention is missing — §8.4 and §8.4a are only worth writing if their absence fails |

Assertions 6 and 10 are the two that would otherwise ship: both produce a file
that validates cleanly and says something untrue. **12, 13 and 14 are the same
class**, added because ADR 0012 and ADR 0014 each moved a number this file had
already written down: 13 catches the exact contradiction §6 carried for as long as
it existed, and 14 catches a Space the Proposal should never have produced.

**buildingSMART's online validation service is not a gate.** It is a network
service and cannot sit in a per-candidate export path. It is the right instrument
for a **pre-release conformance run** — once per schema or MVD change, not once
per file.

## 11. Deliberately absent, and what it would take to add

### Annotation — none, and stated rather than implied

**No `IfcAnnotation`. No dimension chains. No sheets.** Three independent reasons,
any one sufficient:

- ADR 0002 made annotation **derived, not stored**. Writing it into IFC would
  persist exactly the duplicated state that ADR was written to delete.
- IFC has **no dimension-chain concept at all**, so the fourteen sections of
  `annotation.md` have no counterpart to map onto.
- The only real IFC drawing system is **Bonsai's, which is GPL** — the
  `ifcopenshell` LGPL core's `drawing` module has three functions and creates no
  sheets, viewports, dimensions or annotation.

Nothing is lost that a reader needs: the room tag's *content* travels as
`IfcSpace.Name`, `LongName` and `NetFloorArea`, and any viewer regenerates a tag
from those. **The drawing lives in DXF and PDF. The model lives in IFC.**

### Room use — the file names rooms and classifies none

**No `IfcRelAssociatesClassification`. No `IfcClassification`. No
`IfcClassificationReference`.** A room's use travels as `IfcSpace.Name` (the
canonical ergonomic key) and `LongName` (the `AZ` label), and as nothing else.
ADR 0047 decides this; the reasoning is there and only the price is here.

**This is a decline, not a limitation.** Classification Association **is** in
IFC4 RV1.2 scope — established by proving the mvdXML vendored in `ifcopenshell`
byte-identical to buildingSMART's published file (805 551 bytes; the 12 774-byte
delta is exactly 12 771 CRLF plus 3 NBSP). We could write it and stay conformant.

**What it would take to add.** The mapping below was read verbatim off
`uniclass.thenbs.com` at **Spaces/locations v1.36, July 2026** and covers 18 of
19 types in **15 codes across 4 SL branches**. It is a transcription with no
staleness detector — `env_check.py` can assert the toolchain, nothing can assert a
web-served rolling scheme offline — so treat it as read-once and dated, never as a
live reference.

| ergonomic key | code | Uniclass title |
|---|---|---|
| `living` | `SL_45_10_49` | Living rooms |
| `dining` | `SL_45_10_22` | Domestic dining rooms |
| `kitchen` | `SL_45_10_23` | Domestic kitchens |
| `bedroom_principal`, `bedroom_double`, `bedroom_single` | `SL_45_10_09` | Bedrooms — **3 → 1** |
| `study` | `SL_45_10_85` | Studies |
| `kitchen_dining` | `SL_45_10_44` | Kitchen-dining rooms |
| `living_dining_kitchen` | `SL_45_10_45` | Kitchen-dining-living rooms |
| `utility` | `SL_45_10_93` | Utility rooms |
| `bathroom`, `bathroom_combined` | `SL_35_80_08` | Bathrooms — **2 → 1** |
| `shower_room` | `SL_35_80_80` | Showers |
| `wc` | `SL_35_80_89` | Toilets |
| `hall` | `SL_90_10_36` | Hallways |
| `corridor` | `SL_90_10_15` | Corridors |
| `entrance_lobby` | `SL_90_10_27` | Entrance halls — against `_51 Lobbies`, `_94 Vestibules` |
| `storage` | `SL_90_50_35` | General storerooms |
| **`living_dining`** | **none** | **no entry exists** |

Adding it costs **+26 STEP instances** on a 19-space plan, three new entity types,
a Uniclass version pin, and a **second schema pin**: the dictionary-URI attribute
is `Location` in IFC4 and **`Specification`** in IFC4.3.

**The one real cost of declining, stated so it is not discovered by accident.**
buildingSMART's own published IDS sample selects rooms by applicability `IfcSpace`
+ classification `SL_45_10_09` — *Bedrooms*, the exact code. Run against an export
of ours it matches zero elements and **passes green**. That is a silent false
negative, and it is the one thing shipping the codes would buy. It is registered
here rather than in §8.5 because it is a property of the *consumer's* check, not of
our file.

**`living_dining` is the hole and it is not a tail case.** It is the corpus's
second-largest class at **24 122 rooms — 71,2 % of all social rooms** — and Uniclass
has no entry for it, while shipping both kitchen-dining compounds. AzDTN has no word
for it either. If this section is ever acted on, that gap is the first thing to
settle, not the last.

### Space boundaries — none in v1

`IfcRelSpaceBoundary` is not in Reference View, and the level that would be worth
having is worth *less* than it looks:

- **2nd level** boundaries exist for *"energy analysis, lighting analysis, fluid
  dynamics"* — analyses this engine cannot supply inputs for. It holds no U-values,
  no glazing specification, no thermal properties, and `t_ext_total` is itself
  provisional. Authoring boundaries for an energy tool that would then compute
  from nothing is §8.1's failure at the level of file structure: asserting a
  capability we do not have.
- **1st level** is the architectural reading, and it is the one thing here that is
  genuinely arguable. It is not authored because it is not in RV and because
  **nothing is lost**: the geometry is exact integer millimetres and Space
  polygons are finished-face, so a receiving app derives space-to-wall adjacency
  exactly rather than approximately.

**Not precluded.** `CONTEXT.md`'s **Wall segment** — *"the stretch of one Wall that
separates one specific pair"* — **is** a 2nd-level space boundary with its
`CorrespondingBoundary` being the twin segment across the wall. The model already
materialises the relation exactly. If analysis-grade IFC ever enters scope, the
data is there and this section is the only thing that changes.

**And it derives over Room pairs, never Part pairs.** `CONTEXT.md`'s **Wall
segment** already binds this and is the authority; it is repeated here because this
paragraph is where someone would go looking for the derivation, and a Space is now
one or two rectangles (§6.1). Two ways a part-pair walk goes wrong, and the second
is not in `CONTEXT.md`:

- Where a Room's two Parts meet there is an edge in the tiling and **no wall** —
  nothing separates a Room from itself. A part-pair derivation emits a boundary
  there, and it reads as a deliberate partition rather than a bug.
- A wall running along the outside of an L faces **both legs of the same Room**.
  That is **one** Wall segment — a Wall is the maximal straight run and does not
  stop where the rooms behind it change — and a part-pair walk splits it into two
  boundaries against one wall.

So the failure is symmetric: part pairs invent a boundary that is not a wall *and*
divide one that is.

### Element connectivity — none

`IfcRelConnectsPathElements` is not in RV, and no major importer uses it to rebuild
joins — Revit and ArchiCAD join walls by their own geometric rules. Our junction
resolution is already baked into the exported bodies, exactly and deterministically
(ADR 0002 ties junctions on geometry, never on entity id). The relation would
restate what the geometry already says.

### The Revit round-trip — priced at zero, because nobody has priced it

C2 promises the engine will not *preclude* a Revit round-trip. The section of the
export research that was to price it — §4 — **was never written**, so that promise
currently rests on nothing, and this document does not pretend otherwise. What can
be said honestly:

- Revit is certified for **IFC4 RV1.2 export**, so RV is the view its importer is
  best exercised against.
- One concrete untested risk is on record: `IfcIndexedPolyCurve` is an IFC4
  addition, and whether Revit's importer handles it identically to `IfcPolyline`
  **could not be confirmed** from primary sources. It is a named pre-build test.

Pricing the round-trip stays in the *Revit round-trip specifics* fog patch.

## 12. Where the vertical comes from

**The Plan still has no Z, and IFC cannot be authored without one.** This section
used to be a list of what the export was owed. ADR 0012 paid it, so it is now a
list of where each vertical number is read from — and the answer is **two values,
not four.**

| Value | Source | Consumed by |
|---|---|---|
| `h_clear` — finished floor to finished ceiling | **Brief-stated**, defaulted from the profile, hard-bounded ≥ 2700 by AzDTN 2.7-2 cl. 5.8 | every wall body's extrusion depth; `IfcSpace.Body` depth; `Qto…Height`, `NetVolume`, `GrossWallArea`, `NetWallArea` |
| per-opening structural `H` | the region profile's **opening catalogue**, `profiles.AZ.openings` | `IfcDoor` / `IfcWindow` geometry; both schedules in `annotation.md` |

Everything else that used to be listed here is **derived or deleted**:

- **`h_storey` is deleted, not deferred.** AzDTN 2.7-2 prescribes no storey height,
  and its two consumers were both empty: `IfcBuildingStorey` spacing is vacuous with
  exactly one storey pinned at `Elevation = 0.0`, and wall extrusion height is a
  *choice*, because this export authors **no `IfcSlab` and no `IfcRoof`** — nothing
  sits on top of a wall in this file. ADR 0012 carries the full argument, including
  why the lift table's 2,8 m is not a storey height.
- **Sill heights are derived, not tabulated.** One datum,
  `openings.head_datum_mm` = 2200, and `sill = head_datum − catalogue H`. The datum
  is the balcony door's own catalogue head, taken because a balcony door and the
  window beside it share a lintel. A sill is not a catalogue column: the same
  opening sits at one height in a living room and another over a kitchen counter.
- **The `Fall barrier` column is refused, not empty by accident.** The 1,2 m guarding
  height is statutory and `verified`; its *trigger* depends on the drop below the
  window, and v1 has one Storey at elevation 0 with `IfcSite` out of scope. Nothing
  in the model distinguishes a ground-floor window from the same window eight floors
  up, so the export evaluates it nowhere.

Because a wall body and a Space body are both `h_clear`, they are **coplanar top and
bottom**, and every height in the file understates the built dimension by a floor
build-up with no Azerbaijani source. **§8.4a declares that on `IfcBuilding`** rather
than leaving a reader to discover it.

No number here is invented, defaulted or borrowed from an example file. §8.1 binds
this document as much as it binds the file it describes.

---

## Summary of decisions

| # | Decision |
|---|---|
| 1 | Recipient is a **Practitioner**; exchange is **one-way**; claim is LOD 200–250, never a permit set or a round-trip |
| 2 | **IFC4 ADD2 TC1**, **Reference View V1.2** held strictly, header set explicitly |
| 3 | **`IfcWall`**, never `IfcWallStandardCase` — ADR 0010's naming corrected |
| 4 | Wall body is a **set of axis-aligned extrusions**; **no Boolean anywhere** |
| 5 | `IfcSpace.Name` = canonical key, `LongName` = `AZ` label — consumes the mapping, does not decide it |
| 6 | Layer sets from the profile; **exterior winding is checked** |
| 7 | **Write only what is known**; omissions registered in §8.5 and asserted in §10 |
| 8 | Ten of thirteen space quantities written, **all exact**, decided by one rule and not by `Gross`/`Net`; both conventions — area and vertical — carried on `IfcBuilding` in **non-`Pset_`** sets |
| 9 | **Metres**, and integer-mm exactness is declared dead at this boundary |
| 10 | `TrueNorth` only when stated; **never defaulted to 0**; no georeferencing ever |
| 11 | **Third gate**, the IFC check — schema clean plus **16** engine assertions; not in `rules.json` |
| 12 | **No annotation, no space boundaries, no connectivity** — each with its re-entry condition; boundaries derive over **Room pairs, never Part pairs** |
| 13 | The vertical is **two values, `h_clear` and catalogue `H`** — `h_storey` deleted, sills derived, the fall-barrier trigger refused |
| 14 | A Space is **one extrusion over one arbitrary closed profile**, concave or not — RV-verified, no Boolean, and **no new entity type**, because the walls already use one |
| 15 | `NetPlannedArea` carries the Brief's **programme** beside the delivered area, which is the one place in this system the two are distinguishable |
| 16 | **No room-use vocabulary** — no classification, no `ObjectType`, and the habitable/auxiliary partition does not travel. Declined on measurement, not on availability: RV1.2 permits it and 431 published spaces carry it zero times. §11 holds the mapping and the vacuous-pass price — ADR 0047 |
