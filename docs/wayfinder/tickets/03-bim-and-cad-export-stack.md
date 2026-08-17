---
id: 3
title: BIM and CAD export stack
parent: map
labels: [wayfinder:research]
status: open
assignee:
blocked_by: []
---

# BIM and CAD export stack

## Question

What can actually author a **dimensioned, annotated DXF** and a **valid IFC4 with
walls, hosted openings and spaces** — and what does each library force onto the
geometry model upstream of it?

C3 makes dimension strings and room tags a hard floor, and the competitive scan
found that *no surveyed vendor documents a dimensioning or annotation system at
all*. So this is unmapped ground: confirm it is buildable before the geometry
model is locked around it.

Establish, from primary docs and by reading library source where docs are thin:

1. **`ezdxf`** — can it author linear/aligned/continued **dimension entities**
   (not lines that look like dimensions), MTEXT room tags, hatches, layers,
   lineweights, a title block, and paper-space layouts at scale? Which DXF version
   is needed? What breaks when AutoCAD/LibreCAD/Revit opens it?
2. **`IfcOpenShell`** — authoring (not just reading) `IfcWallStandardCase`,
   `IfcOpeningElement`, `IfcDoor`/`IfcWindow` hosted in openings, `IfcSpace` with
   boundaries, `IfcBuildingStorey`. What is the minimum valid IFC4 file that Revit
   imports without complaint? Note the licence split — core is LGPL, Bonsai and
   IfcSverchok are GPL.
3. **What Revit actually does on IFC import.** C2 promises the engine won't
   preclude a Practitioner path. Does Revit produce editable walls, or
   direct-shape blobs? What must the IFC contain for walls to arrive as walls?
   Note that Finch ships "generic wall types" its users must manually replace —
   find out whether that is a Finch choice or an IFC limitation.
4. **`hypar-io/Elements`** (MIT, C#) — BREP/CSG kernel exporting IFC, glTF, DXF,
   SVG. Does it do the dimensioning and annotation half, or only the model half?
   Worth a .NET boundary, or not?
5. **PDF** — plot from DXF, or author directly? What produces a scaled, printable
   sheet.

Deliverable: a findings doc under `docs/research/`, plus an explicit list of
**constraints this stack imposes on the canonical geometry model** — that list is
the input to *Canonical geometry model*.
