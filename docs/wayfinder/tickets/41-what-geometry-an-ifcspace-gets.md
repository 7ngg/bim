---
id: 41
title: What geometry an IfcSpace actually gets
parent: map
labels: [wayfinder:grilling]
status: open
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
