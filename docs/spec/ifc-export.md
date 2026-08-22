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
walls carrying a real material build-up, spaces with area quantities in a named
convention, and typed doors and windows — a starting point for take-off and for
continued design.

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
that **our walls are not generic**: every layer thickness traces to an
Azerbaijani document with a `conf` flag, and the quantity attached to every space
names its measurement convention. §7 and §8 are where that shows up in the file.

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

Opening geometry is owed by *Opening placement rules* for the plan dimensions and
by *The Plan has no vertical dimension* (§12) for the rest.

## 6. Spaces

| Attribute | Value |
|---|---|
| Entity | `IfcSpace`, `PredefinedType = SPACE` |
| `Name` | the **canonical ergonomic key** — `bedroom_double`, `wc` |
| `LongName` | the **`AZ` display label** — `yataq otağı`, `ayaqyolu` |
| `Description` | absent |
| `Body` | `SweptSolid`, the Space polygon extruded to storey height (§12) |
| `FootPrint` | the Space polygon |

The Space polygon is the one ADR 0010 defines: bounded by **finished** inner
faces. The `Body` and `FootPrint` are that polygon and nothing else, which is what
makes `NetFloorArea` exact rather than adjusted on export (§8.4).

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

| Set | Property | Value |
|---|---|---|
| `Pset_SpaceCommon` | `Reference` | canonical ergonomic key |
| | `IsExternal` | `FALSE` |
| `Qto_SpaceBaseQuantities` | `NetFloorArea` | Space polygon area, m² |
| | `NetPerimeter` | Space polygon perimeter |
| | `Height`, `NetVolume` | §12 |
| | `GrossFloorArea` | **not written** |

`GrossFloorArea` is omitted deliberately, per *Area measurement convention*: it
would require attributing half of each bounding partition to the space, which is a
different convention from the one the drawing quotes and the one the acceptance
bar gates on. A quantity that disagrees with the room tag beside it is the exact
defect ADR 0010 exists to prevent, arriving through the quantity set instead of
through annotation.

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
| `Qto_SpaceBaseQuantities.GrossFloorArea` | wrong convention — §8.2 |
| `IfcSite.RefLatitude` / `RefLongitude` / `RefElevation` | the site is out of scope — §9.3 |
| `IfcOwnerHistory` | optional in IFC4; nothing here has an authoring history to state |

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

**Engine layer.** Eleven assertions the schema check cannot make — with one
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
| 10 | `LoadBearing` and `HandicapAccessible` absent on every element | §8.1 asserted, not trusted |
| 11 | `IfcSpace` count = Plan Space count; every `IsExternal` agrees with ADR 0003's ring | silent element loss |

Assertions 6 and 10 are the two that would otherwise ship: both produce a file
that validates cleanly and says something untrue.

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

## 12. What this export needs that the Plan does not have

**The Plan has no vertical dimension, and IFC cannot be authored without one.**

Every wall body is an extrusion and needs a height. Every space needs one for
`Height` and `NetVolume`. Every window needs a sill height and every door a head
height. The model supplies **none** of these: walls have thickness and no height,
`CONTEXT.md`'s **Storey** is "the level a Plan's geometry sits on" and carries no
storey height, and no ceiling or room height appears anywhere in
`room-constraints.json`, `acceptance-bar.md` or `brief.md`.

This is not confined to IFC. `annotation.md` already ships a **door schedule with a
`Structural opening W × H` column** and a **window schedule with `Structural
opening W × H` and `Sill height`** — three columns that cannot be filled from the
model as it stands.

The vertical dimensions are owed by *The Plan has no vertical dimension, and three
artefacts already assume one*. Until it resolves, this document names the inputs
rather than inventing them:

| Input | Consumed by |
|---|---|
| `h_storey` — floor-to-floor | `IfcBuildingStorey` spacing; wall extrusion height |
| `h_clear` — floor to ceiling | `IfcSpace` `Body` height, `Qto…Height`, `NetVolume` |
| per-opening `H` and head height | `IfcDoor`/`IfcWindow` geometry; door schedule |
| per-window sill height | `IfcWindow` placement; window schedule |

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
| 8 | `NetFloorArea` yes, `GrossFloorArea` no; convention carried on `IfcBuilding` in a **non-`Pset_`** set |
| 9 | **Metres**, and integer-mm exactness is declared dead at this boundary |
| 10 | `TrueNorth` only when stated; **never defaulted to 0**; no georeferencing ever |
| 11 | **Third gate**, the IFC check — schema clean plus 11 engine assertions; not in `rules.json` |
| 12 | **No annotation, no space boundaries, no connectivity** — each with its re-entry condition |
| 13 | The Plan has **no Z**, three artefacts already assume one, and it is now ticketed |
