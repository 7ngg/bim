---
id: 41
title: What geometry an IfcSpace actually gets
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - docs/spec/ifc-export.md
---

# What geometry an IfcSpace actually gets

## Question

**Three unresolved things about `IfcSpace`'s body, in one file, and two of them
were on the map with no ticket at all.** They are bundled because they are the
same question — what solid does a Space become — and splitting them would send
two sessions at one section of one document.

### 1. §5 and §12 contradict each other on the Space's height, and a Space is not a storey

`ifc-export.md` §6 makes `IfcSpace.Body` *"the Space polygon extruded to **storey
height** (§12)"*. §12's own input table assigns `IfcSpace` `Body` height,
`Qto…Height` and `NetVolume` to **`h_clear`**, floor to ceiling, and gives
`h_storey` the wall extrusion instead.

ADR [0012](../../adr/0012-one-vertical-datum-and-it-is-the-clear-height.md)
settled it in §12's favour and went further: **`h_storey` is deleted, not
deferred** — AzDTN 2.7-2 prescribes no storey height, and a wall body is
floor-to-ceiling, declared. So §6's sentence names a quantity that **no longer
exists in the model**, and it names it for the one entity whose height is least
ambiguous: a room is floor to finished ceiling, which is exactly `h_clear`.

This is a one-word correction with nothing behind it *if* that is all it is —
and it should be checked that it is. `Qto_SpaceBaseQuantities` carries
`GrossHeight`, `NetHeight`, `GrossVolume`, `NetVolume` and `FinishCeilingHeight`,
and this file has to say which of them it asserts and which it omits under ADR
0011's *present is a claim, absent is unknown*. A `GrossHeight` implies a slab
this model does not have.

### 2. A Space is now up to two rectangles, so its profile is not a rectangle

ADR [0014](../../adr/0014-a-room-is-one-or-two-rectangles-and-the-proposal-decides.md).
A Space is `erode(⋃ parts, t_int/2)` — a rectilinear polygon with at most one
reflex corner, still exact on integer millimetres
(`experiments/room-rectangles/erosion_check.py` asserts it).

**No Boolean is introduced**, which is the restriction ADR 0011 actually carries:
an L is one closed profile swept once. What is **not verified** is whether
Reference View accepts an `IfcArbitraryClosedProfileDef` as the profile of an
`IfcExtrudedAreaSolid`, as against the rectangles §5 currently leans on. ADR 0014
says so explicitly and refuses to claim it. Verify against the buildingSMART RV
concept templates, first-hand, per C11 and §8.1.

Two follow-ons if it does not: the alternative is a set of extrusions per Space,
one per part, which is what §5 already does for walls — so the fallback exists
and the question is which is correct, not whether there is one.

And one that holds either way: **`FootPrint` is the Space polygon**, so it is
concave too, and `NetFloorArea` stays exact by construction because the polygon
is the area.

### 3. Space boundaries were refused for a reason ADR 0014 does not change — check that it does not

*What IFC the engine actually emits* refused 2nd-level `IfcRelSpaceBoundary`
because that level exists for energy, lighting and CFD and this engine holds no
U-values. It also observed that `CONTEXT.md`'s **Wall segment** *is* a 2nd-level
boundary with its twin across the wall, so the data is already materialised.

A two-part Room has an internal edge between its own legs. That edge is **not** a
Wall segment — nothing separates a Room from itself — but a naive derivation over
part boundaries would emit one, and it would be a wall in the file that is not a
wall in the Plan. Confirm the derivation is over **Room pairs**, not part pairs,
and say so where someone would otherwise get it wrong.

## What this is not

Not a re-opening of ADR 0011. Reference View, one-way, annotation-free, *present
is a claim and absent is unknown*, the refusal of 2nd-level boundaries and the
gate that asserts the omissions all stand. This ticket writes one section of one
document and adds gate rows.

⚠️ It does **not** own C2's Revit round-trip, which is priced at zero and sits in
the map's **Revit round-trip specifics** fog, nor the
`IfcIndexedPolyCurve`-versus-`IfcPolyline` import question named there — although
item 2 above is close enough to it that whoever takes this should read that patch
before starting.

## Resolution

**A Space is one extrusion over one arbitrary closed profile, `h_clear` tall, and
its quantity set goes from four written to ten.** `docs/spec/ifc-export.md` §6,
§6.1, §8.2, §8.2a, §8.2b, §8.4a, §8.5, §10, §11, §12. IFC check **11 → 16**
assertions.

Three findings changed what this ticket was. Two of them are corrections to its own
premises.

### The RV question is answered, and the comparison behind it was false

RV1.2's `Body SweptSolid PolyCurve Geometry` concept template, read first-hand per
C11:

```
Items                            = IfcExtrudedAreaSolid, IfcRevolvedAreaSolid
Items[1..n].SweptArea            = IfcArbitraryClosedProfileDef, IfcArbitraryProfileDefWithVoids
Items[1..n].SweptArea.OuterCurve = IfcIndexedPolyCurve
```

Siblings in the same RV group: `ParameterizedProfile`, `CompositeCurve`,
`Composite`. So **yes** — ADR 0014's refusal to claim it is discharged, and the
per-Part fallback is not needed for legality.

⚠️ **But "as against the rectangles §5 leans on" is false, and it was false before
ADR 0014 wrote it.** §5 leans on no `IfcRectangleProfileDef`. The export research's
entity census of the authored model is **12 `IfcArbitraryClosedProfileDef`, 13
`IfcIndexedPolyCurve`, zero `IfcRectangleProfileDef`** — `add_wall_representation`
builds an arbitrary closed profile for a plain rectangular wall. **An L introduces
no new entity type.** Two consequences:

- There was never a safe-rectangles baseline to trade against. The choice was one
  arbitrary profile versus two, not arbitrary versus parametric.
- The unconfirmed `IfcIndexedPolyCurve`-versus-`IfcPolyline` Revit risk of §11
  **already sits on every wall in the file**. The concave Space adds nothing to it,
  and RV's own template *mandates* `IfcIndexedPolyCurve`, so it is not dodgeable
  inside this view. The *Revit round-trip specifics* fog patch is unchanged in
  substance and its named pre-build test unchanged in priority — it just is not a
  Space question.

**Decision: one extrusion, concave or not.** §5 is no precedent for splitting: a
wall with openings *cannot* be one profile without a Boolean, so its decomposition
is **forced**; a Space's is **free**. Two abutting solids share a face and viewers
draw a seam along it — a line through the middle of a room that is not a wall,
which is item 3's failure arriving through geometry instead of through boundaries.
Authored with `geometry.add_slab_representation`, verified in the export research
for exactly this; `add_wall_representation` must not be abused for Spaces.

### The height correction was not one word

⚠️ **The ticket's quantity list is wrong.** `Qto_SpaceBaseQuantities` has **no
`GrossHeight` and no `NetHeight`.** It carries `Height`, `FinishCeilingHeight`,
`FinishFloorHeight`, `GrossVolume`, `NetVolume`, `GrossPerimeter`, `NetPerimeter`
and six areas. The `GrossHeight` argument the ticket built — *"a `GrossHeight`
implies a slab this model does not have"* — is about a property that does not exist.

The real defect is in `Height` itself. IFC4 defines it *"from base slab without
flooring to ceiling without suspended ceiling"*; `h_clear` is finished floor to
finished ceiling, cl. 5.8's own *döşəmədən tavanadək*. They differ by the floor
build-up ADR 0012 **refused to source**.

**Written anyway, and the reasoning is ADR 0012's own.** This model has no floor
build-up layer at all — no `IfcSlab`, no `IfcCovering`, no floor in any layer set —
so slab top and finished floor are one plane *in this file*, and the value is
exactly true of the model. More decisively, **the geometry already committed to
it**: Space bodies and wall bodies are both `h_clear` on elevation 0, so anyone
measuring the model gets this number. Omitting the quantity would hide in the
property set what the solid states plainly, and leave every take-off tool blank on
every room. ADR 0012 already declared this understatement for walls — *"it is an
understatement, and the export says so rather than padding it"*.

*Says so* is now discharged **in the file**, not only in the ADR:
`BimEngine_VerticalConvention` on `IfcBuilding`, §8.4a, beside §8.4's area
convention and non-`Pset_`-prefixed for the same reason. This is the half of ADR
0012 that had never been published anywhere a reader of the IFC could find it.

**`FinishFloorHeight` and `FinishCeilingHeight` are omitted, and that line is the
point.** They *are* the build-up. `0` asserts the building has no flooring and no
dropped ceiling — a claim about the world, not a description of the model — and a
length has no third state any more than `LoadBearing`'s boolean does. ADR 0012 keeps
cl. 5.8's corridor allowance **inert** precisely so a dropped ceiling stays a data
change; `FinishCeilingHeight = 0` today would have to be un-said.

### §8.2 had nine quantities in neither list, and a specified mis-claim

Thirteen quantities exist; four were named; **nine were in neither the written set
nor §8.5's register** — forgotten rather than declined, which is the one state the
register exists to make impossible. Settled by a rule rather than a list, §8.1 one
level down:

> Write a quantity when IFC4's definition names the same plane and the same
> exclusions our model computes to. Omit it when the definition names a plane or a
> convention we do not have — and register the omission.

It does not sort by `Gross`/`Net`: `GrossPerimeter` is written, `GrossVolume` is
not. **Ten written, all exact**: `NetFloorArea`, `GrossPerimeter`, `NetPerimeter`,
`Height`, `NetVolume`, `GrossWallArea`, `NetWallArea`, `GrossCeilingArea`,
`NetCeilingArea`, and `Pset_SpaceCommon.NetPlannedArea`. **Four omitted and
registered**: `GrossFloorArea`, `GrossVolume`, `FinishFloorHeight`,
`FinishCeilingHeight`.

⚠️ **`NetPerimeter` was specified wrong.** §8.2 read *"Space polygon perimeter"*;
IFC4 excludes from `NetPerimeter` *"those parts of the perimeter created by virtual
boundaries and openings (like doors)"*. The polygon perimeter is **`GrossPerimeter`**
— *"at the outer contour"*, and a Space has no thickness. Both are now written, the
old number under its correct name, and the subtraction is exact because openings are
hosted and named by the Wall segment they pierce.

⚠️ **`Pset_SpaceCommon.Reference` is dropped.** It restated `IfcSpace.Name`, which
already carries the canonical ergonomic key — ADR 0002's duplicated state arriving
in a property set — and IFC4.3 **deprecates** the property. §2.3's move on a second
entity: write the spelling that survives the schema migration.

### One debt paid that was not on this ticket

`Pset_SpaceCommon.NetPlannedArea` — IFC4: *"Total planned net area of the object.
Used for programming the object."* That is `Room.target_area` exactly.

*The whole of C2's user* found that `Room.target_area` and the delivered `Space`
area **render identically** on the Homeowner surface, so the Brief reads as
promising an area the plan may not deliver. IFC has a first-class place for the
distinction the drawing does not: planned and achieved two properties apart on one
entity, and a Practitioner reads the delta unprompted. **This closes the
Practitioner half. The Homeowner-facing half is still owed by its own holder.**

Stated honestly in §8.2a: it is the *resolved* target, stated or defaulted, and the
provenance does not travel — the Brief's `Assumption` list is where that lives, and
this file authors no annotation (§11). C4 makes the Brief the real interface, so a
reader who needs provenance asks for it.

### Item 3 was already written, by ticket 28

`CONTEXT.md`'s **Wall segment** already binds it: *"Derived over Room pairs, never
Part pairs… would put a wall inside a room — in the geometry, in the drawing and in
the IFC."* Nothing to decide. §11 gets a **cross-reference, not a restatement** — it
is where someone would go looking for the derivation — plus the second failure
`CONTEXT.md` does not name: a wall along the outside of an L faces **both legs of
the same Room**, and since a Wall is the maximal straight run that is **one**
segment, a part-pair walk **splits** it as well as inventing one. The failure is
symmetric.

### Gate rows: 11 → 16

| # | Assertion |
|---|---|
| 10 *(widened)* | every row of §8.5's register absent on every element it names — the register is now the assertion's input, so a row added to §8.5 and not to the exporter fails here |
| 12 | per `IfcSpace`: `Body` holds exactly one `IfcExtrudedAreaSolid` over exactly one `IfcArbitraryClosedProfileDef` |
| 13 | every Space body depth **and** every wall extrusion depth = `h_clear` |
| 14 | every Space profile closed, rectilinear, integer mm, **at most one reflex corner** — ADR 0014's cap reaching the file |
| 15 | per Space: `NetVolume` = `NetFloorArea` × `h_clear`; `GrossPerimeter` − `NetPerimeter` = Σ opening structural widths; `GrossWallArea` − `NetWallArea` = Σ opening `W × H` |
| 16 | `NetPlannedArea` present and = the Room's `target_area`; both convention sets present on `IfcBuilding` |

13 is the row that would have caught this ticket's own bug. 14 catches a three-Part
Space, which is a Proposal defect that would otherwise ship as valid geometry.

### No technology and no refactor needed

Asked per `CLAUDE.md`. `ifcopenshell` 0.8.5 already does everything here —
`add_slab_representation` is verified for arbitrary-polygon bodies. Nothing new is
required in the model either: openings are already Wall-segment-anchored and
therefore Room-anchored, and `Room.target_area` already exists. **No ADR**: every
decision here is ADR 0011 or ADR 0012 applied, and the reasoning belongs next to the
property, which is where it now sits.

### Declared on resolution, not claimed quietly

Beyond `writes:` — nothing else was claimed on either at the time:

- `docs/adr/0012-…` — corrected `§5` → `§6` and marked both consequences landed.
- `docs/adr/0014-…` — marked the RV question cleared, and recorded that the
  rectangles it compared against do not exist.

### Left open

- The **Revit round-trip** stays priced at zero and its `IfcIndexedPolyCurve` test
  stays named — now known to be a **wall** question, not a Space one.
- The **Homeowner-facing** half of the planned-versus-delivered defect.
- `annotation.md`'s room tag at the larger Part's centroid (ADR 0014) is that file's
  holder's, untouched here.
