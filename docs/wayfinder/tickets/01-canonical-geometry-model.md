---
id: 1
title: Canonical geometry model
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: [3]
---

# Canonical geometry model

## Question

What **is** a plan, in this system? The foundational decision — every other layer
reads or writes this, and C2 requires it to be Practitioner-grade even though the
Homeowner never sees it.

Decide the representation, and justify it against every consumer that has to live
with it:

1. **Walls.** Centrelines with a thickness attribute, or solid polygons? How are
   junctions represented — implicit from the centreline graph, or explicit joins?
   How do internal partitions, internal load-bearing walls and external walls
   differ? *Note: no published generator emits walls with thickness at all, so
   this layer is entirely ours to invent.*
2. **Openings.** Doors and windows hosted on a wall with a parametric position,
   or free geometry? Swing direction, leaf width, sill and head heights. Hosting
   is what makes IFC export and later editing tractable — confirm against the
   export research before choosing free geometry.
3. **Spaces.** Are rooms authored polygons, or derived from the wall graph? These
   diverge the moment a wall moves, and the answer decides whether the solver
   writes rooms or writes walls.
4. **Units and coordinates.** Metres, right-handed, +Z up? Floating point or an
   integer grid? The solver may want integers; IFC and DXF want reals. Where does
   the conversion happen, and what tolerance is carried?
5. **Levels.** Multi-storey is out of scope, but a `Storey` in the model costs
   almost nothing now and a retrofit costs a lot. Include or not?
6. **Annotation.** Are dimension chains and room tags *part of* the model, or a
   view over it? C3 makes them a hard deliverable, so they need a home.
7. ⚠️ **Do walls with thickness survive the solver formulation?** *Solver
   formulation for layout projection* proved C10 works — but on rooms that **tile
   exactly**, with zero-width boundaries. Real walls occupy space. Its own
   conclusion names this the **largest open risk on the architecture**. Resolve it
   here, explicitly, before anything is built on either decision. The candidates:
   solve on room centrelines and thicken afterwards (walls eat room area, so the
   solved minimum dimensions become wrong); solve on inner faces and let wall
   bodies live in the gaps (changes the tiling constraint); or carry thickness in
   the solve (grows the model). Each has a different cost, and one of them may
   invalidate the measured 6.25 s at 24 rooms.

Every choice must be checked against five consumers:

- the **solver**, which projects a proposal onto this representation
- the **validator**, which must evaluate the acceptance bar over it
- **DXF export**, which needs dimensionable, annotatable geometry
- **IFC export**, which needs walls, hosted openings and bounded spaces
- **future interactive editing** (C7) — the model must not make wall-drag
  re-solve a rewrite

Consult the findings from *BIM and CAD export stack* first: that ticket's job is
to produce the list of constraints the export layer imposes here.

Deliverable: the model written up in `CONTEXT.md` as vocabulary, plus an ADR — this
is hard to reverse, surprising without context, and a genuine trade-off, so it
meets all three bars.
