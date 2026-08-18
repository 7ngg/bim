---
id: 1
title: Canonical geometry model
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
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

## Resolution

**Walls with thickness survive the solver. The largest open risk on the
architecture is retired in structure, and reduced to one term that needs
re-measuring.**

The reconciliation is a **dilated solve domain**: the solver tiles the interior
clear region *dilated outward by `t_int/2`*, which makes every tiling edge a wall
centreline and makes `clear rect = erode(solved rect, t_int/2)` true uniformly,
with no special case for perimeter rooms and for any `t_ext`. Same variables, same
`AddNoOverlap2D`, same soft-coverage amendment — **only constants move**. Full
derivation in [ADR 0001](../../adr/0001-centreline-walls-over-a-dilated-solve-domain.md).

Item by item:

1. **Walls** — centreline + thickness, never solid polygons; a polygon leaves the
   exporter reverse-engineering an axis and openings with nothing to be parametric
   on. Two layers: a **`Wall`** is the maximal straight run of same-thickness,
   same-class material and does not stop where the rooms behind it change; a
   **`WallSegment`** is the stretch separating one specific pair, `{room, room}` or
   `{room, EXTERIOR}`. Segments carry identity, runs carry geometry and annotation.
   A segment *is*, unchanged, a 1st-level space boundary — which matters because
   space boundaries are the least-supported corner of the ifcopenshell API.
   Two classes only: **External** (from the Envelope) and **Partition** (from room
   contacts). `load_bearing` is **`None`, not `False`** — asserting false on every
   wall is a structural claim we cannot back and is actively wrong for a flat's
   party walls. Thicknesses come from the region profile, not hardcoded.
2. **Openings** — hosted and parametric, and **typed from a regional catalogue
   rather than dimensioned freely**. Leaf widths are discrete and regional (DE
   860 × 1985 commonest; UK 762 or 838 × 1981), so an invented width is the
   clearest tell that a plan was generated. Three widths kept distinct —
   *structural opening*, *leaf*, *clear* — with the ≈51 mm UK leaf→clear conversion
   in the region profile. Kind is an enum including **cased opening (no leaf)**,
   which is the single biggest realism lever in the model. Swing is structural, not
   decorative: corridor width depends on it. Windows carry `sill_height` **plus a
   separate optional `fall_barrier`**, adopted verbatim from *Dimensional standards
   corpus* — fall protection pushes the sill ≥800 mm and accessibility pushes it
   ≤600 mm, and collapsing them makes the German case unsolvable. Many openings per
   segment.
3. **Spaces** — derived by definition (the polygon bounded by surrounding wall
   inner faces), materialised for speed as `erode(rect, t_int/2)`, and **the
   validator asserts the two agree**. Vocabulary split that falls out and matters:
   **Room** is program (Brief-anchored id, no geometry), **Space** is geometry.
   Using "room" for both is how a clear dimension gets confused with a centreline
   one.
4. **Units and coordinates** — **integer millimetres**, right-handed, +Z up, origin
   at the Envelope bbox min corner, Z=0 at storey finished floor level. Zero
   tolerance in the model; junctions close by integer equality. The 250 mm grid is
   a **solver parameter, not model state**. DXF at 1 unit = 1 mm with
   `DIMLFAC = 1.0`; IFC declared in **metres**, which also dodges the
   `add_door_representation` negative-extrusion bug. Two exports, two declared
   units, one model.
5. **Levels** — `Storey` exists, exactly one in v1, and the Acceptance bar says so.
   IFC's spatial hierarchy makes us author one regardless; refusing it in the model
   would be a lie about what we emit.
6. **Annotation** — **not part of the Plan.** A `Drawing` is derived from Plan +
   sheet; only an `AnnotationOverride` is persisted. See
   [ADR 0002](../../adr/0002-annotation-is-derived-not-stored.md). This reverses
   the glossary as it stood. Requires stable identity, which is why identity is
   Brief-anchored and references to derived geometry are **relation-keyed**.
7. **⚠️ The risk** — retired, as above. **Junctions** resolve by *thicker wall runs
   through* (External beats Partition), ties broken **geometrically** — longest
   run, then coordinate order — never by entity id, because ids are not stable
   across a regenerate. Junctions are derived, materialised and validated, same
   shape as Spaces; a T-junction does **not** split the through wall, it records
   `ATPATH`.

### What this hands to other tickets

- **Solver timing variance sweep** — one specific term to re-measure: the **area
  product on eroded dimensions in millimetres** (operands ~10⁴, products ~10⁸),
  against a constraint family already flagged as the weak spot. Also: the contact
  threshold is `structural opening width + t_int`.
- **Acceptance validator spec** — integer millimetres **deletes** rather than
  answers its tolerance questions ("what counts as a closed junction, a coincident
  wall, a zero-area sliver"): they are integer equalities. It also inherits two
  new predicates — `len(storeys) == 1`, and *Space polygon equals the eroded
  centreline rect*. And C6 item 2's "no sub-1m corridors" placeholder resolves to
  **900 mm** minimum hall/landing (AD M M4(2) ¶2.22a) with a 750 mm pinch for
  ≤2 m.
- **Dimensioning and annotation rules** — its rule 3 ("measured to centrelines,
  faces or grid") now has its input: the model stores centrelines, the human-facing
  quantity is the **clear** dimension, and the two must never be conflated.
- **Which region profiles ship in v1** — the region profile now carries wall
  thicknesses, the door/window catalogue, leaf→clear conversion, and corridor
  constants. Plus a finding: DIN 18101 and DIN 4172 share a **125 mm** octametric
  module, the UK uses 100 mm or nothing, and our 250 mm solve grid is 2 × 125 — it
  courses German masonry and does not divide 100.

### Surfaced, and ticketed rather than buried

A **circular dependency**: AD M Table 1.1 makes corridor clear width a function of
the door widths opening onto it and the approach direction, and Neufert makes it a
function of swing direction — but the solver sizes the corridor and openings are
placed *after* the solve. Resolved by **pre-sizing corridors conservatively from
the region profile's worst-case door arrangement**, which keeps openings post-solve
and leaves the measured formulation untouched. Alternatives — iterating
solve↔placement, or rejecting in the validator — either reopen the 6.25 s or throw
away good plans for a fixable reason. The placement rule itself is now
*Opening placement rules*.

