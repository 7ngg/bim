# BIM and CAD export stack: what can author a dimensioned DXF and a valid IFC4

**Research date:** 2026-08-17
**Ticket:** `docs/wayfinder/tickets/03-bim-and-cad-export-stack.md` (C3 makes this mandatory)
**Method:** primary sources only — library documentation, library **source code**, the buildingSMART IFC specification, and Autodesk's own docs. Where the docs were thin or ambiguous, the claim was settled by **running the library** and inspecting the bytes it produced. Every executed experiment is reproducible from the transcript in §9. Anything that could not be established against a primary source is marked **COULD NOT CONFIRM** rather than guessed.

---

## 0. Headline

**Yes. Real, editable DXF `DIMENSION` entities are authorable from Python, today, with a permissive licence.** `ezdxf` (MIT) emits genuine `DIMENSION` records carrying the `AcDbDimension` / `AcDbAlignedDimension` / `AcDbRotatedDimension` subclass markers, a `DIMSTYLE` reference, definition points on the `Defpoints` layer, and a rendered geometry block — the same structure AutoCAD itself writes. This was **verified by execution**, not inferred from the API surface.

The competitive scan found no surveyed vendor documenting a dimensioning or annotation system. That gap is a **product choice across the industry, not a tooling limitation.** The tooling exists, it is free, and it is mature. C3 is buildable.

The honest caveats, all of which shape the geometry model:

| Finding | Consequence |
|---|---|
| DXF dimensions are **rendered by ezdxf, not by the CAD app** — the geometry block is authored by us | Our renderer's output *is* the drawing. Dimension appearance is our responsibility, and a stale block will not self-heal in every viewer. |
| `DIMLFAC` on every shipped `EZ_*` dimstyle is **100.0** | A 4000 mm wall dimensions as **"400000"** out of the box. Unit convention must be fixed globally and the dimstyle built to match. This is the single easiest way to ship a wrong drawing. |
| DXF **R2000 (AC1015) is the hard floor** | R12 rejects `MTEXT`, `LWPOLYLINE` and `HATCH` outright. |
| IFC4 authoring works and validates clean — but only after `ObjectPlacement` is set | An IfcProduct with a representation and no placement **fails** the IFC4 WR1 rule. |
| Revit's IFC import is the weak link, not the authoring | See §4. |
| ezdxf's PDF backend **vectorises all text** | No selectable or searchable text in the PDF. |

---

## 1. Environment used for the experiments

Everything below was installed from PyPI into a clean venv on the project's own machine (Windows 11, Python 3.12.10). No source builds, no conda, no manual wheels.

```
ezdxf         1.4.4     MIT
ifcopenshell  0.8.5     LGPL-3.0-or-later
shapely       2.1.2     BSD-3-Clause
pymupdf       1.28.2    AGPL-3.0 OR Artifex Commercial   <-- see §6
matplotlib    (BSD-style/PSF)
```

Licence strings above are read from each installed package's own metadata (`importlib.metadata`), i.e. from the distribution the project would actually consume — not from a website.

Both `ezdxf` and `ifcopenshell` install as prebuilt Windows wheels for CPython 3.12 with a plain `pip install`. `ifcopenshell` ships as `ifcopenshell-0.8.5-py312-none-win_amd64.whl` (24.5 MB) — **this is a real, current PyPI release**, which removes the historical friction of having to fetch project-built wheels by hand.

---

## 2. `ezdxf` — dimensioning and annotation

### 2.1 The decisive question: are these real DIMENSION entities?

Yes. A test drawing was authored with linear, aligned, continued-chain and angular dimensions, then written to disk, re-read, and the **raw DXF text inspected**.

Re-reading the file yields, in modelspace: `DIMENSION: 6`, `HATCH: 2`, `LWPOLYLINE: 2`, `MTEXT: 1`.

The raw record for the first dimension:

```
DIMENSION
  5
92
330
17
100
AcDbEntity
  8
A-DIMS
100
AcDbDimension
280
0
  2
*D1
  3
EZDXF
 10
0.0
 20
-800.0
...
 70
32
...
100
AcDbAlignedDimension
 13
0.0
 23
0.0
 33
0.0
 14
4000.0
 24
0.0
 34
0.0
 50
0.0
100
AcDbRotatedDimension
```

This is a structurally complete AutoCAD dimension:

- **`100 / AcDbDimension` → `AcDbAlignedDimension` → `AcDbRotatedDimension`** — the correct subclass marker chain for a rotated linear dimension. An entity faking a dimension with lines and text would have none of this.
- **Group code 2 = `*D1`** — the anonymous block holding the rendered geometry.
- **Group code 3 = `EZDXF`** — the `DIMSTYLE` table reference. The dimension is style-driven, so changing the style restyles the dimension.
- **Group codes 13/14** — the two **definition points**, i.e. the measured extension-line origins. These are what make the dimension *measure something* rather than merely display a string.
- **Group code 70 = 32** — dimension type. Low bits `0` = rotated/linear; bit `32` flags that the referenced block belongs to this dimension alone.

`ezdxf` also computes the measurement itself: `get_measurement()` returned `4000.0`, `1200.0`, `1400.0`, `1400.0` for the respective spans, and `90.0` for the angular dimension — i.e. the value is derived from the definition points, not authored as a literal. Dimension text was left as `<>`, the AutoCAD token meaning "use the measured value".

**Audit result: 0 errors, 0 fixes** from `ezdxf.recover.readfile`, ezdxf's own structural validator.

### 2.2 The factory methods that exist

Enumerated by reflection on `ezdxf.graphicsfactory.CreatorInterface` (the mixin that supplies these to every layout), so this list is what the installed library actually offers:

| Method | Returns | Notes |
|---|---|---|
| `add_linear_dim(base, p1, p2, location=None, text='<>', angle=0, text_rotation=None, dimstyle='EZDXF', override=None, dxfattribs=None)` | `DimStyleOverride` | Rotated/horizontal/vertical linear. |
| `add_aligned_dim(p1, p2, distance, text='<>', dimstyle='EZDXF', ...)` | `DimStyleOverride` | Aligned to the measured direction. |
| `add_multi_point_linear_dim(base, points, angle=0, ucs=None, avoid_double_rendering=True, dimstyle='EZDXF', ...)` | **`None`** | **The dimension chain.** See below. |
| `add_angular_dim_2l` / `_3p` / `_arc` / `_cra` | `DimStyleOverride` | Angular, four construction forms. |
| `add_arc_dim_3p` / `_arc` / `_cra` | `DimStyleOverride` | Arc length. |
| `add_radius_dim`, `add_radius_dim_2p`, `add_radius_dim_cra` | `DimStyleOverride` | |
| `add_diameter_dim`, `add_diameter_dim_2p` | `DimStyleOverride` | |
| `add_ordinate_dim`, `add_ordinate_x_dim`, `add_ordinate_y_dim` | `DimStyleOverride` | |

**Dimension chains are covered.** `add_multi_point_linear_dim(base=(0,-1600), points=[(0,0),(1200,0),(2600,0),(4000,0)])` produced **three separate `DIMENSION` entities** (`*D3`, `*D4`, `*D5`) measuring 1200 / 1400 / 1400, all sharing one base line — i.e. a proper **continued (chained) dimension run**, which is exactly the overall-and-intermediate string an architectural plan needs. Note it returns `None`, not a handle, so if individual segments need post-hoc restyling they must be re-queried from the layout.

`avoid_double_rendering=True` is the default and matters: it suppresses the duplicated extension line where two adjacent segments meet.

### 2.3 `render()` and where the geometry actually comes from

This is the most important architectural fact about ezdxf dimensioning, and it is easy to miss.

`add_*_dim()` returns a `DimStyleOverride`, **not** the entity. The `DIMENSION` entity is at `.dimension`. Calling `.render()` is what generates the visible geometry into the anonymous block. Inspecting block `*D1` after render:

```
LINE   x3        (dimension line + two extension lines)
INSERT x2        -> block _ARCHTICK   (the arrowhead/tick at each end)
MTEXT  x1        (the dimension text)
POINT  x3        on layer 'Defpoints'  (the definition points)
```

So **ezdxf renders the dimension itself**. The DXF file ships both the semantic dimension (definition points + style reference) *and* a pre-drawn picture of it. Consequences:

- A viewer that does not itself render dimensions still shows a correct-looking dimension, because the block is there.
- AutoCAD, on the other hand, owns the dimension once opened: the header var **`$DIMASSOC` is written as `2`** (fully associative) by default, so AutoCAD treats the dimension as live and will regenerate the geometry when the dimension or its style is edited.
- The failure mode is a **stale block**: if the entity's definition points are mutated without re-rendering, the drawn geometry and the semantic measurement disagree. The pipeline must treat "author dimension" and "render dimension" as one atomic step.

`add_multi_point_linear_dim` renders internally (hence the `None` return and the `discard` parameter); the single-dimension factories do not — **you must call `.render()`**.

### 2.4 Dimension styles, and the units trap

`ezdxf.new(setup=True)` installs a set of ready-made styles:

```
Standard, EZDXF,
EZ_M_100_H25_CM, EZ_M_50_H25_CM, EZ_M_25_H25_CM, EZ_M_20_H25_CM,
EZ_M_10_H25_CM, EZ_M_5_H25_CM, EZ_M_1_H25_CM,
EZ_RADIUS, EZ_RADIUS_INSIDE, EZ_CURVED
```

The naming decodes as `EZ_M_<scale>_H<text mm>_<display unit>` — metric, drawing units in **metres**, text 2.5 mm on paper, dimension text displayed in **centimetres**.

**That last part is a trap.** Every shipped style carries `DIMLFAC = 100.0`:

| dimstyle | dimlfac | dimscale | dimtxt | dimasz | dimblk |
|---|---|---|---|---|---|
| `Standard` | 1.0 | 1.0 | 2.5 | 2.5 | |
| `EZDXF` | **100.0** | 1.0 | 0.25 | 0.175 | `_ARCHTICK` |
| `EZ_M_100_H25_CM` | **100.0** | 1.0 | 0.25 | 0.25 | |
| `EZ_M_50_H25_CM` | **100.0** | 1.0 | 0.125 | 0.125 | |
| `EZ_M_25_H25_CM` | **100.0** | 1.0 | 0.0625 | 0.0625 | |
| `EZ_RADIUS` | **100.0** | 1.0 | 0.25 | 0.25 | `_CLOSEDBLANK` |
| `EZ_CURVED` | **100.0** | 1.0 | 0.25 | 0.25 | |

`DIMLFAC` is a multiplier applied to the measured length before it is written as text. With drawing units in **millimetres** — the natural choice for a building model — and the stock `EZDXF` style, a 4000 mm wall renders its text as:

> **`400000`**

Confirmed by extracting the `MTEXT` from each rendered geometry block: `*D1 → '400000'`, `*D2 → '400000'`, `*D3 → '120000'`, `*D4 → '140000'`, `*D5 → '140000'`. The angular dimension rendered `'270°'` where 90° was measured — the reflex angle, a separate reminder that angular dimension direction is order-dependent.

A hand-built millimetre-native style fixes it:

```python
my = doc.dimstyles.add("ARCH-MM-50")
my.dxf.dimlfac = 1.0     # drawing units ARE millimetres -> no scaling
my.dxf.dimscale = 50.0   # annotation scaled for a 1:50 plot
my.dxf.dimtxt  = 2.5     # 2.5 mm text on paper
my.dxf.dimasz  = 2.5
my.dxf.dimexe  = 1.25    # extension beyond dimension line
my.dxf.dimexo  = 0.625   # offset from measured feature
my.dxf.dimgap  = 0.625
my.dxf.dimdec  = 0       # whole millimetres
my.dxf.dimtad  = 1       # text above the line
my.dxf.dimblk  = "_ARCHTICK"
my.dxf.dimtxsty = "OpenSans"
my.dxf.dimdsep = ord(".")
```

Verified: this renders **`3625`** for a 3625 mm wall. Correct.

Note `setup_dimstyle(doc, name="ARCH-50", fmt="EZ_M_50_H25_CM")` copies the template's `DIMLFAC=100.0` too — the helper does not rescue you. The style must be built explicitly.

The two scale knobs are distinct and both matter:
- **`DIMSCALE`** scales the *annotation* (text height, arrow size, gaps) so it reads correctly at a given plot scale. For a 1:50 sheet with 2.5 mm text, `DIMSCALE = 50`.
- **`DIMLFAC`** scales the *number*. It should be `1.0` when drawing units equal the units you want printed.

### 2.5 DXF version: R2000 is the floor

Versions the installed library accepts for both `new()` and `save()`:

```
AC1009 (R12), AC1015 (R2000), AC1018 (R2004), AC1021 (R2007),
AC1024 (R2010), AC1027 (R2013), AC1032 (R2018)
```

R12 was tested directly by attempting to create each entity in an `R12` document:

| Entity | R12 |
|---|---|
| `LWPOLYLINE` | **REJECTED** — `DXFVersionError: LWPOLYLINE requires DXF R2000` |
| `MTEXT` | **REJECTED** — `DXFVersionError: MTEXT requires DXF R2000` |
| `HATCH` | **REJECTED** — `DXFVersionError: HATCH requires DXF R2000` |
| linear dimension | OK |
| `TEXT` | OK |
| `POLYLINE` | OK |

Downgrading a finished R2010 document to R12 emits two warnings from ezdxf itself —
`Downgrade from DXF R2010 to R12 may create an invalid DXF file.` and
`Drawing units ($INSUNITS) are not exported for DXF R12.` — and silently drops entities: the R12 re-read retained only the `DIMENSION`, losing everything else.

Everything from R2000 upward is lossless. The complete probe drawing was re-saved at each version and re-audited:

| Version | modelspace entities retained | layouts | audit |
|---|---|---|---|
| AC1015 (R2000) | LWPOLYLINE 2, HATCH 2, DIMENSION 6, MTEXT 1 | Model, Layout1, A3-PLAN | 0 err / 0 fix |
| AC1018 (R2004) | identical | identical | 0 err / 0 fix |
| AC1024 (R2010) | identical | identical | 0 err / 0 fix |
| AC1032 (R2018) | identical | identical | 0 err / 0 fix |

**Conclusion: R2000 (AC1015) is the minimum. R2010 (AC1024) is a safe default** — it covers everything used here (`MTEXT`, `LWPOLYLINE`, `HATCH` with solid and pattern fill, true colour, lineweight, paper-space layouts, `$INSUNITS`) while being old enough for broad reader support. R2018 buys nothing this project needs.

`$INSUNITS = 4` (millimetres) and `$MEASUREMENT = 1` (metric) were written and survived the round trip.

### 2.6 Layers, lineweights, linetypes, hatches

All verified present in the written file.

**Lineweights are an enumerated set**, not a free float. From `ezdxf.lldxf.const.VALID_DXF_LINEWEIGHTS`, in units of 1/100 mm:

```
0, 5, 9, 13, 15, 18, 20, 25, 30, 35, 40, 50, 53, 60, 70, 80, 90,
100, 106, 120, 140, 158, 200, 211
```

So 0.13, 0.18, 0.25, 0.35, 0.50, 0.70 mm — the ISO pen set — are all available, but an arbitrary 0.45 mm is not. A pen table must snap to this enum. `-3` means "by default", and `$LWDISPLAY = 1` must be set for lineweights to display.

Layers round-tripped with colour and lineweight intact:

```
A-WALL   color 7  lw 50   (0.50 mm)
A-DIMS   color 2  lw 13   (0.13 mm)
A-ANNO   color 3  lw 18   (0.18 mm)
A-HATCH  color 8  lw 9    (0.09 mm)
```

`setup=True` also installs the standard linetype table (`Continuous`, `CENTER`, `DASHED`, `PHANTOM`, `DASHDOT`, `DOT`, `DIVIDE`, and their `X2`/`2` scale variants) — enough for a plan without shipping custom `.lin` definitions.

**Hatches** work in both modes, confirmed on re-read:

```
HATCH solid_fill=1 pattern=SOLID  scale=1   angle=0  paths=2 assoc=0
HATCH solid_fill=0 pattern=ANSI31 scale=10  angle=45 paths=1 assoc=0
```

Two things to note. First, **island/hole support works**: the solid wall-poché hatch was built from an external boundary path plus an inner path, giving a filled wall band between two rectangles — which is exactly how wall poché is drawn. Second, **`associative = 0`**. ezdxf writes non-associative hatches: the boundary is stored as explicit geometry, and if the wall moves the hatch does not follow. For a generate-and-export pipeline that is harmless (we regenerate everything anyway), but a Practitioner editing the DXF will find hatches that do not track edits.

### 2.7 MTEXT room tags

`add_mtext()` with `char_height`, a text `style`, and `set_location(..., attachment_point=5)` (middle-centre) works; `\P` is the MTEXT hard line break, so a two-line room tag (`"LIVING\\P18.2 m²"`) is a single entity. Non-ASCII (`²`) survived the round trip — R2000+ DXF is unicode-capable.

### 2.8 Paper space, viewports at scale, and title blocks

All three confirmed working in the written file.

```python
psp = doc.layouts.new("A3-PLAN")
psp.page_setup(size=(420, 297), margins=(10, 10, 10, 10), units="mm")
vp = psp.add_viewport(center=(210, 148.5), size=(380, 240),
                      view_center_point=(2000, 1500), view_height=240*50)
```

The scale relationship is **`view_height / viewport_height`**. Here `12000 / 240 = 50.0` — a true 1:50. Verified by reading back `vp.dxf.view_height == 12000.0`. This is simple, explicit arithmetic; there is no scale abstraction to fight.

A **title block** is exactly what you would hope: a `BLOCK` containing geometry plus `ATTDEF` definitions, inserted into paper space with `add_blockref` and populated via `add_auto_attribs`:

```python
tb = doc.blocks.new("TITLEBLOCK")
tb.add_lwpolyline([...], close=True)
tb.add_attdef("PROJECT", (5, 45), dxfattribs={"height": 5})
ref = psp.add_blockref("TITLEBLOCK", (230, 10))
ref.add_auto_attribs({"PROJECT": "Test House", "SCALE": "1:50", "SHEET": "A-101"})
```

Re-reading the layout confirms `['VIEWPORT', 'VIEWPORT', 'INSERT']` — two viewports (the first is the mandatory "paper space viewport" #1 that every layout carries) and the title-block insert. Block attributes are the standard mechanism every CAD tool understands, so sheet metadata is editable downstream rather than burned into geometry.

**`$PSVPSCALE` was written as `0.0`.** Annotation-scale plumbing beyond the explicit viewport ratio was **not confirmed**; treat annotative-scaling as out of scope and set annotation sizes explicitly via `DIMSCALE`.

### 2.8a Leaders yes, schedules no

Tested directly on an R2010 document:

| Entity | Result |
|---|---|
| `LEADER` | OK |
| `MULTILEADER` (`add_multileader_mtext`, `add_multileader_block`) | OK — returns a builder |
| `MLINE` | OK |
| **`ACAD_TABLE`** | **`DXFTypeError: invalid entity ACAD_TABLE`** |

`MULTILEADER` covers annotation that needs a pointer — a door tag or a note leading to a specific wall. `MLINE` (multi-line) is in principle a wall-drawing primitive, though hand-built two-polyline walls give more control.

**There is no table entity.** A door/window/room **schedule** must be composed from `LWPOLYLINE` rules plus `MTEXT` cells, or built once as a block. That is a modest amount of layout code, not a blocker — but it *is* work that no library does for us, and it is the one item in C3's neighbourhood with no off-the-shelf answer. Note that AutoCAD's own `ACAD_TABLE` is a notoriously under-supported entity in third-party readers anyway, so hand-composed schedule geometry is arguably the *more* portable choice.

### 2.9 What degrades elsewhere

Detailed third-party behaviour (LibreCAD version coverage, Revit's DXF importer) is covered in §4 and §7 alongside the corroborating documentation.

---

## 3. `IfcOpenShell` — authoring IFC4

### 3.1 The API surface actually installed

`ifcopenshell.api` in 0.8.5 exposes these modules (enumerated with `pkgutil`, so this is the real installed surface):

```
aggregate, alignment, attribute, boundary, classification, cogo, constraint,
context, control, cost, document, drawing, feature, geometry, georeference,
grid, group, layer, library, material, nest, owner, profile, project, pset,
pset_template, resource, root, sequence, spatial, structural, style, system,
type, unit
```

Two naming notes that will otherwise waste time:

- **`void` no longer exists — it is `feature`.** The functions are `feature.add_feature`, `feature.add_filling`, `feature.remove_feature`, `feature.remove_filling`. Documentation and tutorials written against 0.7.x still say `void.add_opening`; that call fails on 0.8.5.
- The modern call form is a **direct module call**, `ifcopenshell.api.geometry.add_wall_representation(file, ...)`. The older `ifcopenshell.api.run("geometry.add_wall_representation", file, ...)` string-dispatch form still exists.

The relevant sub-APIs:

```
geometry  -> add_wall_representation, add_door_representation, add_window_representation,
             add_axis_representation, add_footprint_representation, add_profile_representation,
             add_slab_representation, add_mesh_representation, add_representation,
             assign_representation, edit_object_placement, connect_wall, connect_path,
             create_2pt_wall, regenerate_wall_representation, add_boolean, clip_solid, ...
feature   -> add_feature, add_filling, remove_feature, remove_filling
boundary  -> assign_connection_geometry, copy_boundary, edit_attributes, remove_boundary
drawing   -> assign_product, edit_text_literal, unassign_product
root      -> create_entity, copy_class, reassign_class, remove_product
```

**Note the `drawing` module is nearly empty** — three functions, none of which create sheets, viewports, dimensions or annotation. This is load-bearing for the licence question in §3.7: the real drawing system lives in Bonsai, not in the LGPL core.

### 3.2 A complete single-storey model was authored and validated

The following were created and written to a well-formed IFC4 SPF file:

- `IfcProject` with an `IfcUnitAssignment` (SI length with `MILLI` prefix, area, volume)
- Six representation contexts — `Model`, and subcontexts `Body` (MODEL_VIEW), `Axis` (GRAPH_VIEW), `FootPrint` (MODEL_VIEW); plus `Plan` and subcontext `Annotation` (PLAN_VIEW)
- `IfcSite` → `IfcBuilding` → `IfcBuildingStorey` (with `Elevation = 0.0`), chained with `IfcRelAggregates`
- `IfcWall` with a `Body` representation and an `Axis` representation
- `IfcWallType` carrying an `IfcMaterialLayerSet`, plus an `IfcMaterialLayerSetUsage` on the occurrence
- Two `IfcOpeningElement`s joined to the wall by `IfcRelVoidsElement`
- `IfcDoor` (`OverallHeight`, `OverallWidth`, `PredefinedType='DOOR'`, `OperationType='SINGLE_SWING_LEFT'`) and `IfcWindow`, each joined to its opening by `IfcRelFillsElement`
- `IfcSpace` (`PredefinedType='SPACE'`, `LongName='Living Room'`) aggregated into the storey
- `IfcRelSpaceBoundary` linking the space to the wall

Entity census of the written file:

```
IfcDirection 39, IfcCartesianPoint 14, IfcCartesianPointList2D 13,
IfcIndexedPolyCurve 13, IfcAxis2Placement3D 13, IfcArbitraryClosedProfileDef 12,
IfcExtrudedAreaSolid 12, IfcShapeRepresentation 6, IfcProductDefinitionShape 5,
IfcRelAggregates 4, IfcGeometricRepresentationSubContext 4, IfcSIUnit 3,
IfcRelFillsElement 2, IfcOpeningElement 2, IfcRelVoidsElement 2,
IfcGeometricRepresentationContext 2, IfcWindow 1, IfcSpace 1,
IfcRelSpaceBoundary 1, IfcProject 1, IfcUnitAssignment 1, IfcSite 1,
IfcBuilding 1, IfcBuildingStorey 1, IfcWall 1,
IfcRelContainedInSpatialStructure 1, IfcMaterial 1, IfcMaterialLayerSet 1,
IfcMaterialLayer 1
```

The whole model is **9.4 KB**. IFC4 is not a heavyweight format at this scale.

### 3.3 Wall geometry

`geometry.add_wall_representation(file, context=body, length=4.0, height=2.7, thickness=0.2)` returns an `IfcShapeRepresentation` with:

```
RepresentationIdentifier = "Body"
RepresentationType       = "SweptSolid"
Items                    = [IfcExtrudedAreaSolid]
```

This is the good case. `SweptSolid` extrusion — not a mesh, not a tessellation — is the representation form that downstream BIM tools can interpret as a parametric wall. The profile underneath is an `IfcArbitraryClosedProfileDef` built on an **`IfcIndexedPolyCurve`**.

> **Flag for §4:** `IfcIndexedPolyCurve` is an IFC4 addition. It does not exist in IFC2x3, and some importers historically expected `IfcPolyline` for profile and axis curves. Whether Revit's importer handles `IfcIndexedPolyCurve` identically to `IfcPolyline` **COULD NOT BE CONFIRMED** from primary sources and is a concrete pre-build test.

`geometry.add_axis_representation(file, context=axis, axis=[(0.,0.),(4.,0.)])` produced `RepresentationIdentifier="Axis"`, `RepresentationType="Curve2D"`, items `[IfcIndexedPolyCurve]`.

`geometry.add_door_representation(...)` produced a `SweptSolid` of **eight** `IfcExtrudedAreaSolid` items — a real panelled door body, not a placeholder box.

### 3.4 `IfcWallStandardCase` and the material layer set

`IfcWallStandardCase` **can still be instantiated in IFC4** — verified directly (`f.create_entity("IfcWallStandardCase")` succeeds and reports `is_a() == 'IfcWallStandardCase'`). It remains in the IFC4 schema. Its status in IFC4.3 and the question of whether to prefer plain `IfcWall` is addressed in §4.

What actually makes a wall a "standard case" is the **`IfcMaterialLayerSetUsage`**, and getting one requires a two-step that is easy to get wrong. Assigning an `IfcMaterialLayerSet` directly to the wall occurrence produces an `IfcRelAssociatesMaterial` but **no usage at all** — verified: `usage: []`.

The working sequence is: put the layer set on the **type**, then ask for the usage on the **occurrence**.

```python
wtype = root.create_entity(f, ifc_class="IfcWallType", name="WT-200")
mls   = material.add_material_set(f, name="WT-200", set_type="IfcMaterialLayerSet")
lay   = material.add_layer(f, layer_set=mls, material=mat)
material.edit_layer(f, layer=lay, attributes={"LayerThickness": 0.2})
material.assign_material(f, products=[wtype], type="IfcMaterialLayerSet", material=mls)

wall = root.create_entity(f, ifc_class="IfcWall", name="W1")
type.assign_type(f, related_objects=[wall], relating_type=wtype)
material.assign_material(f, products=[wall], type="IfcMaterialLayerSetUsage")
```

Result, verified:

```
IfcMaterialLayerSetUsage(#18, .AXIS2., .POSITIVE., 0., $)
  LayerSetDirection = AXIS2
  DirectionSense    = POSITIVE
  OffsetFromReferenceLine = 0.0
```

`OffsetFromReferenceLine` is the offset from the wall's **axis** to the start of the layer set. It is `0.0` here, meaning the axis sits on one face. For a centreline-modelled wall it must be `-thickness/2`. **This value directly couples the IFC export to the geometry model's choice of wall reference line** — see the constraints list.

### 3.4a The realistic recipe: walls from centrelines, and where the wall body lands

A second, more realistic model was authored — a 6 × 4 m flat, four walls built from a closed centreline loop, junctions connected, one hosted door, one space, four space boundaries. **11.4 KB.**

The plan-shaped API is `geometry.create_2pt_wall`:

```python
rep = geometry.create_2pt_wall(f, element=w, context=body,
                               p1=(0., 0.), p2=(6., 0.),
                               elevation=0.0, height=2.7, thickness=0.2,
                               is_si=True)
geometry.assign_representation(f, product=w, representation=rep)   # <-- required!
```

**Gotcha:** despite setting the `ObjectPlacement` for you, `create_2pt_wall` **returns** the representation without assigning it. Omit `assign_representation` and the wall silently ends up with `Representation = None`. Verified by hitting exactly that.

`is_si=True` means the arguments are in metres regardless of the project's declared unit; ifcopenshell converts. With a `MILLI` unit assignment, `height=2.7` correctly stored as `2700.0`.

**Wall junctions** are real: `geometry.connect_wall(f, wall1, wall2)` produced `IfcRelConnectsPathElements` with `RelatingConnectionType = ATEND`, `RelatedConnectionType = ATSTART`. So corner joins are expressible, not just implied by coincident geometry.

**The reference line is a face, not the centreline.** The generated wall profile is:

```
(0,0) -> (0,200) -> (4000,200) -> (4000,0)
```

i.e. the swept profile occupies `y ∈ [0, thickness]` in wall-local coordinates — entirely on **one side** of the line through `p1`/`p2`. Transforming each wall's profile into world space for the 6 × 4 m loop confirms it:

| Wall | centreline given | resulting body |
|---|---|---|
| W1 | (0,0) → (6,0) | x[0, 6000] **y[0, 200]** |
| W2 | (6,0) → (6,4) | **x[5800, 6000]** y[0, 4000] |
| W3 | (6,4) → (0,4) | x[0, 6000] **y[3800, 4000]** |
| W4 | (0,4) → (0,0) | **x[0, 200]** y[0, 4000] |

Had the body straddled the centreline, W1 would span `y[-100, +100]`. It does not. The body falls to the **left of the direction of travel**, so **winding order selects which side of the line the wall material occupies** — counter-clockwise puts it inside. This is consistent with `IfcMaterialLayerSetUsage.OffsetFromReferenceLine = 0.0` meaning "reference line on a face".

Consequence: a solver that emits **centrelines** must either offset them by `thickness/2` before export, or set `OffsetFromReferenceLine = -thickness/2`. Either way the geometry model must commit to one convention and record the winding. This is the sharpest single coupling between the solver's output and the IFC exporter.

`geometry.add_slab_representation(f, context=body, depth=2.7, polyline=[...])` is the right tool for an **arbitrary-polygon** `IfcSpace` body — verified producing `SweptSolid` / `IfcExtrudedAreaSolid` with `Depth = 2700.0` and a correctly unit-converted profile. `add_wall_representation` should not be abused for spaces.

### 3.4b A real bug: `add_door_representation` is unit-broken

`geometry.add_door_representation` produces a **schema-invalid negative extrusion depth** unless the project length unit is the metre. Verified across three unit assignments, same call (`overall_height=2.1, overall_width=0.9`):

| Length unit | 8 solid depths | Invalid |
|---|---|---|
| metre (no prefix) | `0.03, 0.03, 2.05, 0.02, 0.02, 0.03, 0.01, 0.01` | 0 |
| **MILLI** | `25.0, 25.0, **-47.9**, 20.0, 20.0, 25.0, 5.0, 5.0` | **1** |
| **CENTI** | `2.5, 2.5, **-2.9**, 2.0, 2.0, 2.5, 0.5, 0.5` | **1** |

The pattern gives the cause away: the door-leaf panel depth is computed as `overall_height − <panel inset>` where the inset is unit-converted but `overall_height` is not. `2.1 − 50 = −47.9` (mm); `2.1 − 5 = −2.9` (cm).

This trips the IFC4 `IfcExtrudedAreaSolid` where-rule `SELF\IfcExtrudedAreaSolid.Depth > 0`:

```
(SELF > 0.0)
Violated by: (-47.9 > 0.0)
On instance: #189=IfcExtrudedAreaSolid(#183,#187,#188,-47.899999999999999)
```

`add_window_representation` is **not** affected — 4 solids, all positive, at both metre and millimetre (`10.0, 40.0, 35.0, 10.0`). `add_wall_representation` and `add_slab_representation` are also clean.

Three options, and the choice belongs to the geometry model: **(a)** declare the IFC project in **metres**, **(b)** author door geometry ourselves rather than using the helper, or **(c)** carry a patch. Option (a) is the cheapest and is the recommendation — note it is a constraint on the *IFC file's* declared unit, which need not match the DXF's.

### 3.5 Spaces and boundaries

`IfcSpace` is attached to the storey with **`IfcRelAggregates`**, not `IfcRelContainedInSpatialStructure` — confirmed by inspecting the inverse relationships after `aggregate.assign_object`. This is correct: `IfcSpace` is itself a spatial structure element and so *decomposes* the storey rather than being *contained in* it. Physical elements (walls, doors, windows) use `IfcRelContainedInSpatialStructure` via `spatial.assign_container`. Getting these two backwards is a classic malformed-IFC error.

All three boundary classes are available in IFC4 and instantiable:

```
IfcRelSpaceBoundary          available
IfcRelSpaceBoundary1stLevel  available
IfcRelSpaceBoundary2ndLevel  available
```

But **there is no `boundary.add_boundary` API** — the `boundary` module only offers `assign_connection_geometry`, `copy_boundary`, `edit_attributes`, `remove_boundary`. Space boundaries must be created with `root.create_entity(f, ifc_class="IfcRelSpaceBoundary")` and their attributes (`RelatingSpace`, `RelatedBuildingElement`, `PhysicalOrVirtualBoundary`, `InternalOrExternalBoundary`) set by hand, then connection geometry attached separately. This worked, but it is manual: **the space-boundary half is the least-supported part of the authoring API.**

### 3.6 The minimum valid IFC4 file, and the one rule that bites

The absolute floor — `IfcProject` + `IfcUnitAssignment` + one `IfcGeometricRepresentationContext` — is **874 bytes** and passes `ifcopenshell.validate` with `express_rules=True` at **0 issues**. That is a valid but empty IFC4 file.

The realistic model initially reported **1 validation issue**, and it is worth quoting because it is the single most likely defect in a generated file:

```
(exists(representation) and exists(objectplacement)
 or (exists(representation) and sizeof([temp for temp in representation.Representations
     if 'ifc4.ifcshaperepresentation' in typeof(temp)]) == 0)
 or ...
```

This is the IFC4 `IfcProduct` WR1 rule: **an element that has a shape representation must also have an `ObjectPlacement`.** `assign_representation` does not create one.

Adding placements resolved it completely:

```python
for el in f.by_type("IfcProduct"):
    if el.Representation and not el.ObjectPlacement:
        geometry.edit_object_placement(f, product=el, matrix=np.eye(4))
```

→ **`after edit_object_placement: issues = 0`**, and the wall gained `IfcLocalPlacement`.

**`IfcOwnerHistory` is not created by default** — the authored file had zero instances and `wall.OwnerHistory` was `None`. This is *legal* in IFC4, where `OwnerHistory` is optional on `IfcRoot` (it was mandatory in IFC2x3), and the file validates without it. It can be supplied by wiring the owner settings:

```python
person = owner.add_person(f, identification="ME", family_name="Engine")
org    = owner.add_organisation(f, identification="bim-engine", name="bim-engine")
pao    = owner.add_person_and_organisation(f, person=person, organisation=org)
app    = owner.add_application(f, application_developer=org, version="0.1",
                               application_full_name="bim-engine",
                               application_identifier="bim-engine")
owner.settings.get_user = lambda ifc: pao
owner.settings.get_application = lambda ifc: app
```

after which newly created entities carry a populated `IfcOwnerHistory`. Recommended: some receiving applications are less tolerant than the schema.

**The header MVD string defaults to the wrong thing.** ifcopenshell writes:

```
FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');
FILE_SCHEMA(('IFC4'));
```

`CoordinationView` is the **IFC2x3** view-definition name. For IFC4 the correct strings are `ReferenceView_V1.2` or `DesignTransferView_V1.0`. It is settable:

```python
f.header.file_description.description = ("ViewDefinition [DesignTransferView_V1.0]",)
```

(In 0.8.5 this is `f.header`, not `f.wrapped_data.header`.) `DesignTransferView` is the semantically right choice for a model intended to be *edited* downstream rather than merely viewed — which is exactly C2's promise. Whether Revit's importer branches on this string is examined in §4.

### 3.7 Licence split

Confirmed from the installed distribution's own metadata:

```
ifcopenshell 0.8.5 -> License :: OSI Approved ::
                      GNU Lesser General Public License v3 or later (LGPLv3+)
```

The core Python package — including **all of `ifcopenshell.api`**, which is everything used above — is **LGPL-3.0-or-later**. Bonsai (formerly BlenderBIM) and IfcSverchok are **GPL**, because they link Blender. The practical rule:

> Everything needed to author walls, openings, doors, windows, spaces, boundaries and the spatial hierarchy is in the **LGPL** core. Nothing in the experiments above imported Bonsai.

The corollary is the one that costs us: as noted in §3.1, the core `drawing` module has three functions and no annotation system. **Bonsai's drawing/sheet system is on the GPL side.** So IFC cannot supply the annotation half of C3 without a GPL dependency — which is a second, independent reason (alongside the fact that IFC is a model format, not a drawing format) that **dimensions must come from the DXF/PDF path, not the IFC path.**

C9 states licence is not a gate for this non-commercial project, so GPL is not fatal; but taking a GPL dependency to get something the MIT-licensed `ezdxf` already does better would be a poor trade.

---

## 6. PDF — a scaled, printable sheet

### 6.1 Plot from DXF. Do not author the PDF directly.

The DXF is already the drawing: it holds the dimensions, the hatches, the layers with lineweights, the paper-space sheet and the title block. Authoring a PDF separately would mean re-implementing all of that and then keeping two renderers in agreement. **Plot from the DXF.**

`ezdxf` ships the plotter in-tree: `ezdxf.addons.drawing`. Backends present in 1.4.4:

```
backend, config, debug_backend, dxf, file_output, frontend, gfxproxy, hpgl2,
json, layout, matplotlib, mtext_complex, pipeline, properties, pymupdf, pyqt,
qtviewer, recorder, svg, text, text_renderer, type_hints, unified_text_renderer
```

The architecture is record-then-replay: a `Recorder` captures the frontend's primitives once, and its `Player` can be replayed into any number of backends. So one traversal feeds PDF, SVG and PNG.

### 6.2 True scale is real, and it was measured

```python
backend = Recorder()
Frontend(RenderContext(doc), backend).draw_layout(msp)

page     = layout.Page(420, 297, layout.Units.mm, margins=layout.Margins.all(10))
settings = layout.Settings(fit_page=False, scale=1/50)     # <-- 1:50

pmb = pymupdf.PyMuPdfBackend()
backend.player().replay(pmb)
open("plan_1to50.pdf", "wb").write(pmb.get_pdf_bytes(page, settings=settings))
```

`Settings(fit_page=False, scale=...)` is the whole trick — the default is `fit_page=True`, which scales to fill the sheet and gives you a drawing at no particular scale. That default is a quiet way to ship an unscaled "scaled drawing".

Verified by measuring the produced PDF:

| | |
|---|---|
| Page rectangle | 1190 × 841 pt = **419.81 × 296.69 mm** (A3) |
| Model bounding box | 5414.31 × 5400.76 mm |
| Predicted on paper at 1:50 | 108.29 × 108.02 mm |
| **Measured on the page** | **108.24 × 107.97 mm** |

Agreement to 0.05 mm — the residual is the stroke half-width included in the model bbox. **This is a genuine 1:50 plot.**

The `SVGBackend` takes the identical `Page`/`Settings` and emits `width="420mm" height="297mm" viewBox="0 0 1000000 707143"` — also true-scale.

`Frontend.draw_layout` accepts a **paper-space layout**, and viewport contents are resolved: replaying the `A3-PLAN` layout recorded 42 primitives spanning (141.7, 10.0)–(410.0, 194.5) in page millimetres, which includes both the title-block insert and the model geometry seen through the viewport. `Frontend.draw_viewport` skips viewports with `status < 1` and logs `"Cannot render non top-view viewports"` for anything that is not a plan view — irrelevant for a floor plan, but it means the sheet must be composed of top-view viewports only.

### 6.3 Two fidelity limits worth knowing

**Text is vectorised.** The produced PDF reports:

```
get_text() length : 0
fonts on page     : []
text blocks       : 0
```

Every glyph is converted to filled paths. The drawing looks right and prints right, but the PDF has **no selectable, searchable or copyable text**, and no embedded fonts. For a Homeowner-facing plan this is cosmetically fine; for anyone expecting to grep a room schedule out of the PDF it is not. If real text is required, that is an argument for the SVG path plus a converter that preserves text — **COULD NOT CONFIRM** that any ezdxf backend preserves live text.

**Dimensions render because their geometry block renders.** The plotter draws the anonymous `*D<n>` block contents (lines, `_ARCHTICK` inserts, MTEXT). This is why §2.3 matters: **an unrendered dimension is an invisible dimension in the PDF.** It would still be a valid dimension in AutoCAD, which regenerates it — so a missing `.render()` produces a defect that is invisible in CAD and glaring in the PDF.

### 6.4 The licence wrinkle

`pymupdf` is **AGPL-3.0 or Artifex Commercial** — confirmed from the installed distribution's own metadata (`Dual Licensed - GNU AFFERO GPL 3.0 or Artifex Commercial License`). It is an **optional** dependency: ezdxf itself is MIT and its `SVGBackend` is pure Python, so a fully permissive route exists as **DXF → SVG (MIT, true-scale) → PDF**. The `matplotlib` backend is *not* a substitute for precise work: `qsave()` exposes only `size_inches` and `dpi` — **there is no `scale` parameter**, so it cannot produce a guaranteed 1:50 sheet.

Given C9 ("licence is not a gate"), PyMuPDF is acceptable and is the shortest path. The SVG route is the fallback if that ever changes.

**The CLI cannot do this.** `ezdxf draw` offers `--backend {matplotlib,qt,mupdf,custom_svg}`, `-l/--layout`, `-o/--out`, `--dpi` — and **no scale option**. Scaled output is a Python-API-only capability. Plan the exporter as library code, not a shell-out.

### 6.5 An undocumented build requirement

`ifcopenshell.validate(..., express_rules=True)` imports `_pytest.assertion` and raises `ModuleNotFoundError: No module named '_pytest'` without it. **`pytest` is a runtime dependency of IFC validation**, not just a test dependency. Not documented anywhere found; discovered by hitting it.

---

## 9. Reproducing the experiments

The probes are self-contained. Environment:

```bash
python -m venv venv
./venv/Scripts/python.exe -m pip install ezdxf ifcopenshell pytest pillow pymupdf matplotlib
```

`pytest` is required by `ifcopenshell.validate(..., express_rules=True)` — it imports `_pytest.assertion` and raises `ModuleNotFoundError` without it. This is undocumented and worth knowing.

Probes written and run:

| Script | Establishes |
|---|---|
| `dxf_probe.py` | Dimension factory enumeration; authors linear/aligned/chained/angular dims, hatches, layers, MTEXT, paper space, title block; re-reads and dumps raw DXF; audits. |
| `dxf_probe2.py` | Header vars (`$DIMASSOC`), rendered geometry-block contents, full dimstyle attribute dumps. |
| `dxf_probe3.py` | Rendered dimension **text** (the `DIMLFAC` trap), a corrected mm-native dimstyle, R12 degradation matrix. |
| `ifc_probe.py` | Full IFC4 authoring: contexts, hierarchy, wall, axis, openings, door, window, space, boundary; header dump. |
| `ifc_probe2.py` | `IfcMaterialLayerSetUsage` two-step, owner history wiring, MVD header override, express-rule validation, minimal-file size. |
| `pdf_probe.py` | Scaled PDF and SVG output; measured scale verification; text-vectorisation check; CLI enumeration. |
