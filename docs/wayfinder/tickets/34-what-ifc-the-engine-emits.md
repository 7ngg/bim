---
id: 34
title: What IFC the engine actually emits
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: [17]
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
