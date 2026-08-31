# Room shape: market & standards check — is anyone narrower than "rectilinear"? (August 2026)

**Question.** Our contract says a Room is the union of at most two axis-aligned rectangles
sharing an edge → four shapes: **L** (1 reflex corner), **T** (2), **Z** (2), plain **rectangle** (0).
Measured on 1,543 real two-part rooms: **55% L, 21.6% T, 21.4% Z, 1.8% rectangle**.
Decision on the table: admit all four, or restrict the contract to **L only**.

**Method.** Primary sources only (buildingSMART spec HTML, Autodesk/Graphisoft help, arXiv).
`standards.buildingsmart.org` now sits behind a Cloudflare interactive challenge, so the IFC4
pages were pulled with `curl` and the IFC4x3 mirror (`ifc43-docs.standards.buildingsmart.org`)
was used where the IFC4 MVD page was unreachable. Anything not established from a primary
source is marked **NOT ESTABLISHED** rather than guessed. Budget: ~30 tool calls, no sub-agents.

---

## TL;DR — the one-sentence answer

> **No shipping BIM or commercial generative product imposes a room-shape restriction narrower
> than "rectilinear polygon", and IFC accepts a T- or Z-shaped room as a single `IfcSpace` with
> no limit whatsoever on the number of reflex corners — the only place a narrower rule exists is
> the graph-theoretic *rectangular floorplan* research line (GPLAN), which restricts rooms to
> rectangles, and whose published extension to non-rectangular shapes stops at exactly
> one concave corner (an L) for reasons of graph-theoretic tractability, not architecture.**

Implication for us: **restricting to L-only cannot be justified by "the market does it" or "IFC
needs it".** It can only be justified by our own solver tractability — the same reason the
graph-theory line stops at one concave corner. And that argument costs us 43% of observed
two-part rooms.

---

## 1. IFC — verified, and it refutes the premise of any corner limit

### 1.1 `IfcArbitraryClosedProfileDef` places NO limit on reflex corners

Source: IFC4 ADD2 TC1, §8.15.3.1 —
<https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/schema/ifcprofileresource/lexical/ifcarbitraryclosedprofiledef.htm>
(retrieved 2026-08-31, HTTP 200 via curl).

Entity definition, verbatim:

> "The closed profile `IfcArbitraryClosedProfileDef` defines an arbitrary two-dimensional profile
> for the use within the swept surface geometry, the swept area solid or a sectioned spine. It is
> given by an outer boundary from which the surface or solid can be constructed."

The **complete** set of Informal Propositions, verbatim:

> "The `OuterCurve` has to be a closed curve."
>
> "The `OuterCurve` shall not intersect."

The **complete** set of Formal Propositions (where rules), verbatim:

> "WR1 The curve used for the outer curve definition shall have the dimensionality of 2."
>
> "WR2 The outer curve shall not be of type `IfcLine` as `IfcLine` is not a closed curve."
>
> "WR3 The outer curve shall not be of type `IfcOffsetCurve2D` as it should not be defined as an
> offset of another curve."

EXPRESS, verbatim:

```
ENTITY IfcArbitraryClosedProfileDef
 SUPERTYPE OF ( IfcArbitraryProfileDefWithVoids )
 SUBTYPE OF ( IfcProfileDef ) ;
  OuterCurve : IfcCurve ;
 WHERE
  WR1 : OuterCurve.Dim = 2;
  WR2 : NOT('IFCGEOMETRYRESOURCE.IfcLine' IN TYPEOF(OuterCurve));
  WR3 : NOT('IFCGEOMETRYRESOURCE.IfcOffsetCurve2D' IN TYPEOF(OuterCurve));
END_ENTITY;
```

**Conclusion (VERIFIED):** the word "arbitrary" is load-bearing. Closed, planar, non-self-
intersecting, not a line, not an offset curve. **There is no convexity rule, no reflex-corner
count, no vertex-count cap, no L/T/Z distinction anywhere in the entity.** Our belief that IFC
places no such limit is **confirmed**, not merely unrefuted.

### 1.2 The `…SweptSolid PolyCurve Geometry` concept template adds nothing

Source: IFC 4.3.2 §4.1.7.1.12.1.1 *Reference SweptSolid PolyCurve Geometry* —
<https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Product_Shape/Product_Geometric_Representation/Reference_Geometry/Reference_SweptSolid_Geometry/Reference_SweptSolid_PolyCurve_Geometry/content.html>

Verbatim:

> "…is the reference representation of the 3D shape of a product by swept solid models, only
> allowing for the basic extruded area solids and revolved area solids. Being a reference
> representation it is normally not displayed and it is not used in a voiding relationship."

The template's permitted entity chain, as listed on the page: `IfcExtrudedAreaSolid` →
`IfcArbitraryClosedProfileDef` / `IfcArbitraryProfileDefWithVoids` → `OuterCurve` =
`IfcIndexedPolyCurve`. `RepresentationType = 'SweptSolid'`.

**Conclusion (VERIFIED for IFC4x3):** the template constrains *which entities* may be used, not
*what shape the profile may be*. The only profile-shape rules in force are §1.1's — closed and
non-self-intersecting. **A T- or Z-shaped room profile is a conformant `IfcIndexedPolyCurve`
outer curve.**

> **Caveat / NOT FULLY ESTABLISHED:** the brief named the **IFC4 Reference View 1.2 MVD** page
> `Body SweptSolid PolyCurve Geometry`. That exact MVD page
> (`…/MVD/RELEASE/IFC4/ADD2_TC1/RV1_2/HTML/link/body-sweptsolid-polycurve-geometry.htm`) returned
> HTTP 403 behind a Cloudflare JS challenge on every attempt, and the IFC4 spec has no
> `/templates/` mirror of it (404). I verified the **IFC4x3** sibling template instead. Given that
> the profile entity itself (§1.1, IFC4 ADD2 TC1, verified directly) carries no shape rule, an MVD
> template would have to *add* a corner limit to create one — no MVD in this family is known to add
> geometric shape predicates, but I could not read that specific page to prove it.

### 1.3 `IfcSpace` itself takes an arbitrary contour

Source: IFC 4.3.2 `IfcSpace` —
<https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcSpace.htm>

On the *FootPrint GeomSet Geometry* concept, verbatim:

> "An `IfcBoundedCurve` is required, using `IfcPolyline` for faceted space contours or
> `IfcCompositeCurve` for space contours with arc segments. For spaces with inner boundaries, a set
> of `IfcBoundedCurve`'s is used, that should be grouped into an `IfcGeometricCurveSet`."

On body geometry, verbatim:

> "The body or solid model geometric representation of an `IfcProduct` is typically defined using a
> Tessellation or Brep."

`IfcSpace` lists *Reference SweptSolid Geometry*, *Reference SweptSolid PolyCurve Geometry* and
*FootPrint GeomSet Geometry* among its representations.

**Conclusion (VERIFIED):** "faceted space contour" via `IfcPolyline` is exactly a rectilinear
polygon of any corner count. IFC not only permits a T or Z room as one `IfcSpace` — it permits a
space with *holes* (inner boundaries), which is strictly more permissive than anything we are
considering.

---

## 2. Revit and ArchiCAD — no restriction found; evidence is partial

### Revit

- *Room and Space Geometry* (Revit API help): "Revit uses the 2D outline of the room to form the
  bottom faces."
  <https://help.autodesk.com/cloudhelp/2016/ENU/Revit-API/files/GUID-E7B451BB-21DC-4D72-AD26-75F0C2E911E4.htm>
- *Create Area Boundaries* / *Calculate Areas in a Project*: boundaries must form a **closed loop**;
  Revit cannot automatically create area boundary lines in external walls that are not closed in a
  loop. <https://help.autodesk.com/view/RVT/2025/ENU/?guid=GUID-C3F4D1B7-83E0-4354-919A-101D6B86A220>
- *Change the Room Area Boundary Location*: the boundary can be wall finish, wall centre, core layer
  or core centre — a *location* rule, not a *shape* rule.
  <https://help.autodesk.com/view/RVTLT/2024/ENU/?guid=GUID-0BB62832-36DD-4E06-A9D4-EE98CE0FCF89>

**Finding:** the only stated requirement is **closure**. No Autodesk page found states any
convexity, corner-count or L/T/Z restriction. Structurally, `SpatialElement` boundaries are
*lists of loops of boundary segments*, which cannot express a corner limit.
**Confidence: medium.** This is an argument from absence across four Autodesk pages, not a
positive quote saying "any rectilinear shape is allowed". **NOT ESTABLISHED:** a single
affirmative Autodesk sentence admitting arbitrary reflex counts.

### ArchiCAD

- *Edit Zone Polygon* (Graphisoft Help, AC26): fetched and read; contains **no** statement
  restricting zone polygon shape — it describes pet-palette reshaping of the polygon.
  <https://help.graphisoft.com/AC/26/INT/_AC26_Help/040_ElementsVB/040_ElementsVB-138.htm>
- *Creating Zones* (AC24):
  <https://help.graphisoft.com/AC/24/INT/_AC24_Help/040_ElementsVB/040_ElementsVB-147.htm>
- Community threads report the *automatic* (inner-edge detection) zone tool struggling with
  "unconventional" room shapes and users drawing the polygon manually instead — a **usability**
  limit of auto-detection, not a data-model limit. (Forum = secondary, flagged as such.)
  <https://community.graphisoft.com/t5/Modeling/Wall-Connections-amp-Zone-Boundaries/td-p/111679>

**Finding:** a Zone is a polygon; no shape restriction documented.
**Confidence: medium-low** — again absence-of-evidence. **NOT ESTABLISHED:** an affirmative
Graphisoft quote.

**Net for §2: neither authoring tool was found to restrict a space to one reflex corner, and
nothing suggests a T or Z room is anything other than one ordinary space in either.**

---

## 3. Commercial generative products — nobody publishes a room-shape rule

| Product | Room-shape statement found? | Evidence |
|---|---|---|
| **TestFit** | Supports non-rectangular "spaces" | Blog (marketing, labelled): "TestFit has built out tools for simple (rectangular) & complex shapes alike (called spaces)". Massing offers "Shape Style — either fill the site, create a custom shape, or offset a custom shape"; free shape → "draw outline or draw path offset". <https://www.testfit.io/blog/testfit-2-10-structured-spaces>, <https://support.testfit.io/knowledge/mass-based-buildings/getting-started> |
| **TestFit (units)** | **NOT ESTABLISHED** | `support.testfit.io/knowledge/unit-editor` describes depth, width, balconies, bays, entry — it never states whether a *unit* may be non-rectangular. "Corner units"/"inside corners" imply rectangles but do not say so. |
| **Maket.ai** | **NOT ESTABLISHED** | maket.ai front page carries no geometric statement at all; input is described as a footprint polygon + room types + areas + adjacencies. |
| **Finch3D** | **NOT ESTABLISHED** | Only secondary reviews found; they describe a "proprietary graph system" and a constraint set (unit mix, min/max area, daylight, code) — **no** room-shape claim. |
| **Archistar** | **NOT ESTABLISHED** | Positioned for feasibility/massing; no room-shape doc found. |
| **Autodesk Forma (ex-Spacemaker)**, **Digital Blue Foam**, **Snaptrude**, **Laiout**, **PlanFinder**, **Coohom/Planner5D** | **NOT ESTABLISHED** | Targeted search returned no primary vendor documentation stating any room-shape constraint. **Not reached within budget.** |

**Finding:** across the whole commercial set, **no vendor publishes a room-shape restriction of any
kind** — not "rectangles only", not "L only", not "rectilinear only". The constraint vocabulary they
advertise is *areas, adjacencies, unit mix, daylight, code* — never *shape class*. That is itself a
signal: shape class is not a knob anyone markets, which means restricting it is unlikely to read as
a feature and has no competitor precedent to point at.

**Also NOT ESTABLISHED:** whether any vendor's *published output images* visibly contain T- or
Z-shaped rooms. Verifying that requires visual inspection of gallery renders; not attempted within
budget. This is the single cheapest remaining check and I recommend it as follow-up.

---

## 4. Academic generators — representation, not shape rules

| System | Room representation | Source |
|---|---|---|
| **RPLAN** / **Graph2Plan** | **Rasterised**: rooms as segmentation masks; Graph2Plan "first predicts coarse **bounding boxes** of rooms and then refines them by simultaneously generated floorplan images", vectorised by post-processing | survey / related-work statements: <https://arxiv.org/html/2504.09694v1>, <https://arxiv.org/pdf/2207.13268> |
| **House-GAN / House-GAN++** | Raster masks per room, graph-constrained | <https://arxiv.org/pdf/2003.06988> |
| **HouseDiffusion** | **Polygon.** Verbatim: *"We represent a floorplan as 1D polygonal loops, each of which corresponds to a room or a door."* and *"capable of generating non-Manhattan structures and controlling the exact number of corners per room"* | <https://arxiv.org/abs/2211.13287> |

**Finding:** the raster/bbox generators impose no *shape* rule — they impose a *resolution* rule; a
T or Z room falls out of the mask freely, and the bbox stage is an intermediate, not the output
contract. HouseDiffusion is explicitly polygonal with a **tunable corner count per room** — i.e.
the one academic system that parameterises corners treats corner count as a *dial*, and advertises
going *beyond* rectilinear (non-Manhattan), not below it.

**Not re-derived here** (already in `docs/research/floorplan-generation-stack.md`): none of ~20
published generators emit walls with thickness.

---

## 5. The one genuine narrower-than-rectilinear precedent — and why it does not transfer

The **graph-theoretic rectangular floorplan (RFP)** line *does* restrict shape, harder than we do.

**GPLAN** (released software with a GUI) — abstract, verbatim:

> "GPLAN takes user requirements as input in the following two forms: i. Adjacency graph: It allows
> user to draw an adjacency graph on a GUI … corresponding to which GPLAN produces a set of
> dimensioned floorplans with a **rectangular boundary**, where each floorplan is topologically
> distinct from others."

<https://arxiv.org/abs/2008.01803>

**"A Theory of L-shaped Floor-plans"** — abstract, verbatim:

> "Existing graph theoretic approaches are mainly restricted to floor-plans with rectangular
> boundary. In this paper, we introduce floor-plans with $L$-shaped boundary (**boundary with only
> one concave corner**). To ensure the L-shaped boundary, we introduce the concept of
> non-triviality of a floor-plan. A floor-plan with a rectilinear boundary with at least one concave
> corner is non-trivial if the number of concave corners **can not be reduced**, without affecting
> the modules adjacencies within it. Further, we present necessary and sufficient conditions for the
> existence of a non-trivial L-shaped floor-plan corresponding to a properly triangulated planar
> graph (PTPG) $G$. Also, we develop an $O(n^2)$ algorithm for its construction, if it exists."

<https://arxiv.org/abs/2205.14434>

**Read this carefully — three things matter:**

1. **It is about the floor-plan BOUNDARY, not individual rooms.** Inside an RFP the modules are
   *rectangles*. So the precedent for "narrower than rectilinear" is **rectangles-only rooms**,
   which is 1.8% of our measured population — obviously unusable for us.
2. **The "one concave corner" limit is a graph-theory artefact.** They extend to L because L is the
   minimal non-rectangular case for which they can state necessary and sufficient existence
   conditions and give an $O(n^2)$ construction. The paper's own framing — reduce concave corners
   until you *can't* — is a **minimisation** stance: concave corners are a cost to be driven down,
   admitted only when adjacency demands it. That is a solver-tractability argument, not a claim
   that architects don't draw T and Z rooms.
3. **Nothing in this line says T or Z rooms are architecturally invalid.** They are simply outside
   what the enumeration theory covers.

**So: the only precedent for an L-only rule is a research line that restricts rooms to rectangles,
and whose L extension is a boundary result driven by proof tractability.** If we adopt L-only, we
are copying a constraint from a system whose actual room contract is *stricter than any shape we
are considering*, for reasons about their proofs, not about buildings.

---

## 6. What this means for the decision

- **"IFC/Revit/ArchiCAD force us to L" — refuted.** IFC's profile entity has exactly two informal
  propositions and three where-rules, none about shape (§1.1, verified verbatim). A T or Z room
  exports as one `IfcSpace` with one `IfcPolyline` footprint. Downstream BIM fidelity is **not** an
  argument for L-only.
- **"The market restricts room shape" — not supported.** No vendor in the set publishes any
  room-shape rule; the one system that dials corners (HouseDiffusion) dials them *up*.
- **The only real argument for L-only is our own solver/contract tractability** — the same argument
  the RFP line makes. It must be paid for at **43.0% of observed two-part rooms (21.6% T + 21.4% Z)**,
  and those rooms don't vanish: an L-only contract forces each of them to be split into two Rooms or
  approximated, which is a fidelity loss an architect would see on the sheet.
- Note the asymmetry the data already shows: **T and Z each carry two reflex corners, and together
  they are 24× the rectangle case.** They are not a tail. The 1.8% rectangle is the tail.

**Recommendation for the grilling:** treat "restrict to L" as needing a *positive* tractability
proof with a measured cost, because the external-authority justification for it does not exist.

---

## 7. Explicitly NOT established (budget exhausted)

1. The **IFC4 RV1.2 MVD** page `Body SweptSolid PolyCurve Geometry` itself — Cloudflare 403 on every
   attempt. Verified the IFC4x3 sibling template instead (§1.2).
2. An **affirmative** Autodesk or Graphisoft sentence permitting arbitrary reflex counts. Both §2
   findings are absence-of-restriction across several pages, not a positive permission quote.
3. Whether any commercial vendor's **published output images** visibly contain T- or Z-shaped rooms.
   Not attempted — cheapest remaining check, recommended as follow-up.
4. Primary documentation for **Finch3D, Maket.ai, Archistar, Forma, Digital Blue Foam, Snaptrude,
   Laiout, PlanFinder, Coohom/Planner5D** on room shape. Searched; nothing primary surfaced. Several
   were not individually reached.
5. Whether **TestFit units** (as opposed to "spaces") may be non-rectangular.
