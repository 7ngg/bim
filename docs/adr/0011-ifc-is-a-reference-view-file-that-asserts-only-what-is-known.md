# IFC is a Reference View file that asserts only what the engine knows

The Destination names "valid IFC" as a hard output and C2 promises the engine will
not preclude a Revit round-trip, which reads as an argument for the **Design
Transfer View** — the model view that carries editable parametric geometry. It is
not, because that view does not meaningfully exist. We export **IFC4 ADD2 TC1,
Reference View V1.2, held to strictly**, and adopt a file-level rule that a
property present in the file is a claim and a property absent means unknown.

Spec: `docs/spec/ifc-export.md`.

## Why Design Transfer View is not the alternative it looks like

Three independent findings, any one sufficient:

- buildingSMART's own position: *"Design Transfer View never materialised into an
  official MVD."* IFC4.3 publishes exactly two — Reference View and Alignment
  Based Reference View.
- **Zero** software products are certified for Design Transfer View export. Revit's
  IFC4 certification is **Reference View 1.2, export only**; IFC4 *import*
  certification exists industry-wide for two products.
- The Design Transfer View documentation describes a *"higher fidelity one-way
  transfer of data and responsibility"* — not the round-trip it is usually invoked
  to buy.

So this is not a fidelity decision taken for cheapness. Reference View is the only
view with an ecosystem, and the file is built to the top of what it allows.

## What Reference View actually costs, and what it does not

It costs less than its reputation suggests. Swept solids are in scope, so nothing
is forced to triangulate; property sets, quantity sets, material layer sets,
object typing and the `Name`/`LongName` identity attributes are all in scope.

Two restrictions bite, and both are absorbed rather than worked around:

- **No Booleans, and openings must be pre-subtracted.** Absorbed exactly, because
  ADR 0001 made every wall axis-aligned and every structural opening a rectangle
  in it: a wall with *n* openings decomposes into a set of axis-aligned boxes with
  no approximation. The file contains no `IfcBooleanResult`.
- **No space boundaries and no element connectivity.** Not authored — and the
  reason is not the restriction. 2nd-level boundaries exist for energy, lighting
  and CFD analysis, and this engine holds no U-values, no glazing specification
  and a `t_ext_total` that is itself provisional; authoring them would assert a
  capability we do not have. 1st-level boundaries and `IfcRelConnectsPathElements`
  restate what exact integer-millimetre geometry already says.

Not precluded: `CONTEXT.md`'s **Wall segment** — the stretch of one Wall separating
one specific room pair — *is* a 2nd-level space boundary with its corresponding
twin across the wall. The relation is already materialised; only this decision
stands between it and the file.

## Why "absent means unknown" is a decision and not a disclaimer

`Pset_WallCommon.LoadBearing` is an `IfcBoolean` with no third state, and a Wall's
`load_bearing` is *unknown, not false* (ADR 0001). The same shape recurs at
`AcousticRating` — `t_party = 280` was **derived** from a 50 dB requirement, never
tested — and at `Pset_SpaceCommon.HandicapAccessible`, where *Brief schema and
parsing contract* refused accessibility outright, so `TRUE` breaches C8 and `FALSE`
is a claim about a plan nobody assessed.

`IsExternal` is what stops this being laziness: ADR 0003's edge ring **does** know
exterior from party, so it is written and checked. The rule is enforced rather than
stated — the export gate asserts the omissions, so the day someone helpfully fills
one in, the export fails.

## Consequences

1. **`IfcWallStandardCase` is never written.** IFC4.3: *"The entity
   `IfcWallStandardCase` has been deprecated, `IfcWall` with
   `IfcMaterialLayerSetUsage` is used instead."* We write `IfcWall`, legal in IFC4
   and already the 4.3 spelling. **This corrects ADR 0010's own justification**,
   which reads *"IFC wants it. `IfcWallStandardCase` carries
   `IfcMaterialLayerSetUsage`."* The reasoning stands; the entity it names does
   not.
2. **A third gate exists.** The IFC check joins `rules.json` and the Drawing check,
   and is deliberately outside `rules.json` for the Drawing check's own reason: it
   judges the *file*, not the *Plan*, and a Plan must never be rejected for an
   exporter defect. Schema-clean plus eleven engine assertions, two of which —
   the area cross-check and the asserted omissions — catch files that validate
   cleanly and say something untrue.
3. **Integer-millimetre exactness dies at this boundary.** ADR 0001's metres (§6)
   mean 150 mm becomes 0.15 m, which binary floating point cannot hold. No defect
   follows, but the division of labour is now explicit: **the DXF is the exact
   export and the IFC is the interoperable one.**
4. **The file self-describes its area convention**, in a property set on
   `IfcBuilding` that does **not** wear the reserved `Pset_` prefix. `ümumi sahə`
   sums room areas and excludes partitions, so a reader assuming GIA is wrong by
   the partition footprint — 5.7 % at the shipped `t_int`.
5. **`TrueNorth` is written only when the Brief states one, and never defaulted to
   zero.** A defaulted 0° asserts north = +Y, which is the engine inventing a fact.
   No georeferencing is ever written.
6. **The Plan has no vertical dimension, and this export is where that surfaced.**
   Walls have thickness and no height; `CONTEXT.md`'s Storey exists "because the
   model would otherwise have to invent it on export" and carries no height.
   `annotation.md` already ships three schedule columns that cannot be filled.
   Ticketed, not invented.
