# Classification Association in IFC4 Reference View V1.2 — is it in scope?

**Research date:** 2026-09-01
**Question:** is `IfcRelAssociatesClassification` → `IfcClassificationReference`, applied to
`IfcSpace`, within the scope of the IFC4 Reference View 1.2 (IFC4 ADD2 TC1 / RV1_2) Model
View Definition? This gates a spec decision: `docs/spec/ifc-export.md` §2.2 writes
`ViewDefinition [ReferenceView_V1.2]` into the header and §10 check #2 asserts it. If
classification is out of scope, writing one makes that header claim false.

**Method:** primary sources only, and *first-hand*. The answer is read out of
**buildingSMART's own published RV1.2 documentation** and out of **the RV1.2 mvdXML
file itself**, and the two were cross-checked against each other. Nothing below is taken
from a forum post, a vendor blog, or a summary of the MVD. Where a claim is reasoning
over the sources rather than something a source states, it is tagged **[INFERENCE]**.
Reproduction transcript in §7.

---

## VERDICT: **IN SCOPE.**

Classification Association applies to `IfcSpace` in IFC4 Reference View V1.2. It is
**not** an extension, not a tolerated-but-undocumented addition, and not inherited by
accident — buildingSMART's published RV1.2 documentation for `IfcSpace` lists it
explicitly, by name, in the Reference View column, on a page that demonstrably *does*
mark suppressed concepts as suppressed and does not mark this one.

Writing `IfcRelAssociatesClassification` on an `IfcSpace` **does not falsify** the
`ViewDefinition [ReferenceView_V1.2]` header claim.

---

## 1. The decisive quote

buildingSMART's RV1.2 documentation page for `IfcSpace` carries a table headed
**"Concept inheritance"** with the columns `# | Concept | Template | Model View`. Rendered
from the page's own HTML, the table reads:

```
IfcRoot
    Identity                             | Software Identity                   | Reference View
    Revision Control                     | Revision Control                    | Reference View
IfcObjectDefinition
    Classification                       | Classification                      | Reference View
IfcObject
    Object User Identity (suppressed)    | Object User Identity                | Reference View
    Object Predefined Type (suppressed)  | Object Predefined Type              | Reference View
    Property Sets for Objects            | Property Sets with Override         | Reference View
IfcSpatialElement
    Spatial Element Type Predefined Type | Spatial Element Type Predefined Type| Reference View
IfcSpace
    Space Attributes                     | Space Attributes                    | Reference View
    Object Typing                        | Object Typing                       | Reference View
    Property Sets for Objects            | Property Sets for Objects           | Reference View
    Quantity Sets                        | Quantity Sets                       | Reference View
    Spatial Decomposition                | Spatial Decomposition               | Reference View
    Spatial Container                    | Spatial Container                   | Reference View
    Product Local Placement              | Product Local Placement             | Reference View
    FootPrint GeomSet Geometry           | FootPrint GeomSet Geometry          | Reference View
    Body SweptSolid PolyCurve Geometry   | Body SweptSolid PolyCurve Geometry  | Reference View
```

Source:
`https://standards.buildingsmart.org/MVD/RELEASE/IFC4/ADD2_TC1/RV1_2/HTML/schema/ifcproductextension/lexical/ifcspace.htm`
(HTTP 200, 63,086 bytes; retrieved 2026-09-01).

Verbatim, the row that settles it, as the raw HTML has it:

```html
<tr><td colspan="3"><a href="../../ifckernel/lexical/ifcobjectdefinition.htm">IfcObjectDefinition</a></td></tr>
<tr><td> </td>
    <td><a href="../../ifckernel/lexical/ifcobjectdefinition.htm#classification">Classification</a></td>
    <td><a href="../../templates/classification.htm">Classification</a></td>
    <td>Reference View</td></tr>
```

**Why the "(suppressed)" markers matter.** This is the negative control, and it is the
reason this table is proof rather than suggestion. The same table, on the same page, in
the same rendering pass, marks two concepts `<del>Object User Identity</del> (suppressed)`
and `<del>Object Predefined Type</del> (suppressed)` — because `IfcSpace` overrides them
with its own versions. So the RV1.2 documentation **has a mechanism for saying "inherited
but not applicable here", it uses that mechanism on this very page, and it does not use it
on Classification.** The absence of a suppression marker is therefore meaningful, not
merely uninformative.

Corroborating, the RV1.2 page for the supertype states it in prose. Under the heading
**"Definitions applying to Reference View" → "Concept usage"**:

> **Classification**
> The Classification concept applies to this entity. Any object occurrence or object type
> can have a reference to a specific classification reference, i.e. to a particular facet
> within a classification system.

Source:
`https://standards.buildingsmart.org/MVD/RELEASE/IFC4/ADD2_TC1/RV1_2/HTML/schema/ifckernel/lexical/ifcobjectdefinition.htm`
(HTTP 200; retrieved 2026-09-01).

---

## 2. The three independent legs the verdict stands on

The verdict does not rest on the one table. Three separate primary artefacts agree.

### Leg 1 — the RV1.2 narrative names the concept in its scope statement

The RV1.2 specification text, section **"Objective"**, listing what an RV1.2 model
typically includes:

> - physical elements with explicit geometry, properties, quantities, material, and classification
> - types of elements with associated physical elements to group common definitions (geometry, properties, material, and classification)
> - **spatial elements (spaces, zones) with explicit geometry, properties, quantities, and classification**

and section **"Object association"**:

> In addition to the Property sets and the Quantity sets, also a classification reference
> to an external classification system can be assigned […] The usage of the object
> association is defined within the following concept templates (see also Chapter 4
> "fundamental concepts and assumptions"):
> - "*Material Association*"; assigns a material (or material set - constituent, layer,
>   profile) to one or several model elements […]
> - **"*Classification Association*"; assignes a classification reference to one or several
>   model elements.**

(spelling "assignes" is the source's). Both passages are in the RV1.2 mvdXML's own
embedded documentation — see §7 for the file and line numbers.

Note that the *first* of these bullets settles the `IfcSpace` question on its own terms:
RV1.2's own objective statement says spatial elements carry classification.

### Leg 2 — the machine-readable mvdXML says so structurally

The RV1.2 mvdXML contains a `ConceptRoot` for `IfcObjectDefinition` whose sole concept is
Classification:

```xml
<ConceptRoot uuid="ee2a5066-804f-4b60-89db-18e6a1659063" name="IfcObjectDefinition"
             status="sample" applicableRootEntity="IfcObjectDefinition">
  <Applicability uuid="00000000-0000-0000-0000-000000000000" status="sample">
    <Template ref="2f5ac9dc-eeb4-46f8-bfe5-25a335e5f7ad" />
    <TemplateRules operator="and" />
  </Applicability>
  <Concepts>
    <Concept uuid="5b55bf60-cc1b-409c-8856-7981c54d29b0" name="Classification"
             status="sample" override="false">
      <Template ref="4a224609-6578-4c75-afcf-8affa86e5ef2" />
    </Concept>
  </Concepts>
</ConceptRoot>
```

This is inside `<ModelView … code="ReferenceView_V1-2" version="1.2" owner="bSI"
copyright="© 1996-2018 buildingSMART International Ltd." applicableSchema="IFC4">`.

That a root on `IfcObjectDefinition` reaches `IfcSpace` is not an assumption. buildingSMART's
own mvdXML XSD documents the attribute:

> Identifies the class or data type of instance being described or validated, i.e. the IFC
> entity (deriving from IfcRoot) for which the concepts apply. **The concepts apply to this
> IFC entity or its subtypes** (respectively instances of those classes in case of
> validation).

— `xs:documentation` on `@applicableRootEntity`, line 373 of
`https://raw.githubusercontent.com/buildingSMART/mvdXML/master/mvdXML1.2/xsd/mvdXML_V1.2.xsd`

And `IfcSpace` is such a subtype, verified against the project's own pinned schema rather
than from memory (`ifcopenshell 0.8.5`, `schema_by_name('IFC4')`):

```
IfcSpace                    instantiable
IfcSpatialStructureElement  ABSTRACT
IfcSpatialElement           ABSTRACT
IfcProduct                  ABSTRACT
IfcObject                   ABSTRACT
IfcObjectDefinition         ABSTRACT
IfcRoot                     ABSTRACT
```

**`IfcObjectDefinition` is ABSTRACT.** No instance in any IFC file is ever literally an
`IfcObjectDefinition`. **[INFERENCE]** — a `ConceptRoot` on an abstract entity would be
dead weight under any reading *other* than subtype inheritance, so the file's own structure
only coheres if the XSD rule is applied. RV1.2 uses this deliberately and repeatedly:
`IfcRoot`, `IfcObject`, `IfcObjectDefinition`, `IfcElement`, `IfcSpatialElement`,
`IfcSpatialStructureElement`, `IfcProduct` and `IfcTypeProduct` all carry ConceptRoots and
all are abstract.

### Leg 3 — RV1.2's own concept index lists it, as a peer of Material Association

This is the cleanest single artefact in the whole investigation. `schema/toc-4.htm` is the
table of contents for **Chapter 4, "Fundamental concepts and assumptions"** — the chapter
that enumerates the concept templates in scope for the view. Its section 4.4, verbatim:

```
4.4       Association
4.4.1     Classification
4.4.1.1   Classification for Objects
4.4.1.1.1 Classification for Objects with Override
4.4.2     Material Association
4.4.2.1   Material Single
4.4.2.1.1 Material Single for Objects with Override
4.4.2.2   Material Constituent Set
4.4.2.2.1 Material Constituent Set with Override
```

Source: `https://standards.buildingsmart.org/MVD/RELEASE/IFC4/ADD2_TC1/RV1_2/HTML/schema/toc-4.htm`
(HTTP 200; retrieved 2026-09-01).

**Classification (4.4.1) and Material Association (4.4.2) are siblings under the same
heading of the same chapter of the same specification.** `docs/spec/ifc-export.md` §2.1
already lists Material Association as an established RV1.2 permission. There is no basis on
which to admit 4.4.2 and exclude 4.4.1 — they are peers, and RV1.2's own narrative (Leg 1)
introduces them together in one bulleted pair.

The template page itself, `schema/templates/classification.htm`, renders correspondingly:

> **4.4.1 Classification**
> Objects, type objects, properties, and some resource schema entities can be further
> described by associating references to external sources of information. […]
> **Reference View**
> Entity: `IfcObjectDefinition`

The full chapter-4 top level, for context on how narrow the view is: 4.1 Project Context,
4.2 Object Definition, 4.3 Object Attributes, **4.4 Association**, 4.5 Object Composition,
4.6 Object Assignment, 4.7 Object Connectivity, 4.8 Product Shape, 4.9 Partial Templates.

### The documentation is the [Official] release

The RV1.2 documentation frame carries the banner:

> **IFC4 RV - 1.2 [Official]**  © 1996-2020 buildingSMART International Ltd.

Source: `https://standards.buildingsmart.org/MVD/RELEASE/IFC4/ADD2_TC1/RV1_2/HTML/content.htm`
(HTTP 200; retrieved 2026-09-01).

This matters for how much weight the HTML carries relative to the mvdXML: the published
documentation is marked **[Official]**, whereas the mvdXML's elements all carry
`status="sample"` (see §8). Where the two agree — and here they agree exactly — the
[Official] HTML is the citation to lead with.

### The concept is actively maintained in RV1.2, per the release's own changelog

RV1.2's Annex F carries six changelog sections; four are empty stubs, two are populated.
**F.5.3 Model Views**, under the `REFERENCE VIEW` heading, `IFCELEMENT` block:

```
IFCELEMENT
  Material Single for Objects with Override   | ADDED
  Material Constituent Set with Override      | ADDED
  Classification for Objects with Override    | ADDED
  Material Single                             | DELETED
```

Source: `https://standards.buildingsmart.org/MVD/RELEASE/IFC4/ADD2_TC1/RV1_2/HTML/annex/annex-f/4022/modelviews.htm`
(HTTP 200; retrieved 2026-09-01). Section intro, verbatim:

> F.5 4.0.2.2 - The Technical Corrigendum to IFC4 RV1.2 includes fixes and improvements to
> documentation, property sets, and fundamental concepts based on implementer feedback.
> There is one fix of a Where Rule (IfcShapeModel), but no more changes to the schema.

**Read this precisely.** The row is under `IFCELEMENT`, and it concerns the
*Classification for Objects with Override* **subtemplate** - not `IfcSpace`, and not the
base *Classification* template that `IfcSpace` inherits. So it is **not** direct evidence
for the verdict. What it does establish is that classification concepts were being actively
added to and curated within Reference View as recently as the ADD2 TC1 corrigendum - which
is the opposite of a concept quietly falling out of scope. Treat it as context, not proof;
the proof is §1.

---

## 3. Provenance: the local mvdXML is the genuine bSI artefact

The RV1.2 mvdXML used above ships inside the project's own pinned dependency, at

```
venv/Lib/site-packages/ifcopenshell/mvd/mvd_examples/officials/ReferenceView_V1-2.mvdxml
792,777 bytes
sha256 0b6eab1e6d878874000c51a1deba1ec711b81152e1023059060f339ab41e4fb5
md5    b68e91babebdce3a21b5ffd8e9758b57
```

A file sitting in a `site-packages` directory is not by itself authority, so it was
**checked against buildingSMART's live publication**. Each RV1.2 HTML page embeds, under a
collapsed `<summary>mvdXML Specification</summary>` block, the exact mvdXML fragment it
documents. Comparing those embedded fragments to the local file:

| Artefact | uuid | Live bSI page | Local file | Match |
|---|---|---|---|---|
| `ConceptTemplate` "Classification" | `4a224609-6578-4c75-afcf-8affa86e5ef2` | `templates/classification.htm` | line 2424 | **identical** — same rules, same order, same nested `RuleID`s |
| `ConceptRoot` "IfcObjectDefinition" | `ee2a5066-804f-4b60-89db-18e6a1659063` | `ifckernel/lexical/ifcobjectdefinition.htm` | line 11774 | **identical** |
| `Concept` "Classification" | `5b55bf60-cc1b-409c-8856-7981c54d29b0` | same page | line 11780 | **identical** |
| `ConceptRoot` "IfcSpace" | `75217ae0-a1fb-43ad-b52d-a6b5d75e53fb` | `ifcproductextension/lexical/ifcspace.htm` | line 12812 | **identical** |

The vendored copy and the live specification agree on content and on uuids.

**Then the question was closed completely: buildingSMART publishes the mvdXML itself, and
the vendored file is that file.** The loose original is served at

`https://standards.buildingsmart.org/MVD/RELEASE/IFC4/ADD2_TC1/RV1_2/HTML/annex/annex-a/reference-view/ReferenceView_V1-2.mvdxml`

(HTTP 200, `Content-Length: 805551`, `last-modified: Wed, 11 Dec 2019 17:00:03 GMT`). It is
**not** byte-identical to the vendored copy — it is 12,774 bytes larger — and the entire
difference is line endings and three non-breaking spaces:

```
bSI published    805,551 bytes  sha256 c0b41798bea9af26d2745f1c6f664c0a0279326007a41ebe12b9ec7eeade34f6
vendored         792,777 bytes  sha256 0b6eab1e6d878874000c51a1deba1ec711b81152e1023059060f339ab41e4fb5

bsi.replace(b'\r\n', b'\n').replace(b'\xc2\xa0', b' ')
  ->             792,777 bytes  sha256 0b6eab1e6d878874000c51a1deba1ec711b81152e1023059060f339ab41e4fb5
  NORMALIZED == VENDORED : True
```

The byte accounting closes exactly: **12,771 CRLF + 3 U+00A0 = 12,774 = 805,551 - 792,777.**
Nothing else differs. **The file in `site-packages` is buildingSMART's published RV1.2
mvdXML, with LF line endings.** There is no semantic delta at all, so every line number and
every quotation in this note applies equally to bSI's own copy.

For completeness on how it got there: the vendored copy did **not** originate with
IfcOpenShell. `ifcopenshell/mvd` is a git submodule of `opensourceBIM/python-mvdxml`; the
blob was added there in commit `49f68e0c0cfccebf88df40e989b84fbaa475b1ae`, message verbatim
`Add ReferenceView`, by `johltn <j.luttun@laposte.net>`, 2021-03-03, direct push with no PR
and no issue, and has never been modified since. **No commit message or doc anywhere records
where the file was obtained** - that gap is real, and it is also now moot, because the
publisher's own bytes have been recovered and match.

Independent corroboration of the ModelView uuid, from a different repository and a different
file format: buildingSMART's `Design Transfer View` IfcDoc model-view definition cites RV as
its base view -

```xml
<DocModelView Name="Design Transfer View" Code="DesignTransferView_V1-1" Version="1.1"
  Status="Proposal" Owner="bSI" Copyright="&copy; 1996-2016 buildingSMART International Ltd."
  BaseView="86aa67de-829b-467b-9cd8-dd364beabe79" ...>
```

- `raw.githubusercontent.com/buildingSMART/IFC/master/ModelViews/Design%20Transfer%20View/DocModelView.xml`.
That is the RV1.2 `ModelView` uuid, appearing in `buildingSMART/IFC` (not the MVD release,
not python-mvdxml), in IfcDoc `DocModelView.xml` format rather than mvdXML, under a
1996-2016 copyright predating RV1.2's December 2018 release. DTV documents itself as *"derived
from the Reference View"*, so citing RV's uuid as `BaseView` is exactly right.

---

## 4. What the concept template permits — the attribute answer

This answers deliverable #3. The full rule tree of ConceptTemplate
`4a224609-6578-4c75-afcf-8affa86e5ef2`, verbatim in structure:

```
IfcObjectDefinition
└── HasAssociations → IfcRelAssociatesClassification
    ├── Name                          → IfcLabel                [RuleID "Name"]
    └── RelatingClassification → IfcClassificationReference     [RuleID "Value"]
        ├── Identification            → IfcIdentifier           [RuleID "Identification", Description="*"]
        ├── Name                      → IfcLabel                [RuleID "Name"]
        ├── Description               → IfcText
        ├── ReferencedSource → IfcClassification
        │   ├── Source                → IfcLabel                [RuleID "ClassificationSource"]
        │   ├── Name                  → IfcLabel                [RuleID "ClassificationName"]
        │   ├── ReferenceTokens       → IfcIdentifier           [RuleID "ClassificationTokens"]
        │   ├── Edition               → IfcLabel
        │   ├── Description           → IfcText
        │   ├── Location              → IfcURIReference
        │   └── EditionDate           → IfcDate
        ├── Sort                      → IfcIdentifier
        └── Location                  → IfcURIReference
```

Reading that against the three sub-questions:

**Are `IfcClassification.Edition` / `EditionDate` permitted?** **Yes, both, explicitly.**
`Edition → IfcLabel` and `EditionDate → IfcDate` are named `AttributeRule`s inside the
template.

In fact the template constrains **nothing away at all** on either entity. Checked against
the pinned schema (`ifcopenshell 0.8.5`, IFC4):

| Entity | Attributes in IFC4 | Covered by template `4a224609…` |
|---|---|---|
| `IfcClassification` | `Source`, `Edition`, `EditionDate`, `Name`, `Description`, `Location`, `ReferenceTokens` | **all 7** |
| `IfcClassificationReference` | `Location`, `Identification`, `Name`, `ReferencedSource`, `Description`, `Sort` | **all 6** |

So the answer to "does the concept template constrain *which* attributes may be written" is:
**no — every attribute of both entities is in scope.** There is no need to omit edition
metadata, `Sort`, `Location` or anything else for RV1.2 conformance.

**Is `ReferencedSource` required? Is `Identification` required?** **Neither is made
mandatory by the template.** An mvdXML `AttributeRule` declares that an attribute is *within
the concept's scope* and constrains its type; it does not by itself impose presence. Presence
is expressed by `<Requirements><Requirement applicability="export" requirement="…"/></Requirements>`
elements, and:

- The Classification `Concept` at the `IfcObjectDefinition` root carries **no `<Requirements>`
  element at all** (verified: zero `Requirement` elements in the concept block).
- Across the whole RV1.2 mvdXML there are only two `requirement="mandatory"` flags and 302
  `requirement="recommended"` ones — none of them on a Classification concept.

The RV1.2 exchange-requirement legend, verbatim from the specification:

> | Flag | Name | Description |
> |---|---|---|
> | R | Required | The attributes must be set as indicated. |
> | O | Optional | The attributes may be set as indicated or may be omitted. |
> | X | Excluded | The attributes must be omitted. |

and, importantly for how to read all of this:

> The listing of an entity below does not mean that instances of such entity must
> necessarily exist within a file, only that if any instances do exist, then they must
> conform to the indicated requirements.

**[INFERENCE]** — so the correct reading is permissive-but-constrained: RV1.2 does not
oblige a file to classify anything, but a file that *does* classify must stay inside the
template's shape. Practically, `Identification` and `ReferencedSource` should still be
written, on IFC4 schema grounds rather than MVD grounds: a bare `IfcClassificationReference`
with no `ReferencedSource` and no `Identification` names nothing a receiver can resolve.

**The one real restriction found — and it is on a *type*, not on an attribute.** In the
object-level Classification template, `ReferencedSource` is typed to **`IfcClassification`
only**:

```xml
<AttributeRule AttributeName="ReferencedSource">
  <EntityRules>
    <EntityRule EntityName="IfcClassification">
```

The IFC4 schema type is `IfcClassificationReferenceSelect = IfcClassification |
IfcClassificationReference`, i.e. the schema permits a *chain* of nested references. **The
RV1.2 object-level template does not include that nesting** — no `HasReferences` rule
appears anywhere in template `4a224609…`. **[INFERENCE]** — a conforming file should
therefore point `ReferencedSource` straight at a single `IfcClassification` and not build a
multi-level reference hierarchy hanging off the space's own reference.

(For contrast: the *project-level* template does permit nesting — see §5.)

---

## 5. The companion concept the export will also want: Project Classification Information

RV1.2 carries a second, separate classification concept, at the project rather than the
object: ConceptTemplate `818ca5a3-4574-49b1-9951-ae7bad5c3341`, **"Project Classification
Information"**, `applicableEntity="IfcContext"`. It is wired into the RV1.2
`IfcProject` ConceptRoot as concept `1f3d17a8-cfd2-4b20-ab7f-ec4414926c83`, alongside
Project Units, Project Representation Context 3D, Project Global Positioning, Project Type
Definitions and Spatial Decomposition.

Its documentation:

> Projects may define classification structures, which may be used to classify objects
> contained within the same project, or other referencing projects (incorporating the
> current project as *IfcProjectLibrary*).
>
> The classification information can either be provided as an external classification
> reference, only refering to an *IfcClassification*, that holds the classification name,
> edition and a resource location, or to an *IfcClassification* containing the
> *IfcClassificationReference*'s as the classification notations, and thereby allowing to
> include the classification system structure within the exchange structure.

Its rule tree differs from the object-level one in two ways worth knowing:

- `RelatingClassification` is typed to **`IfcClassification`** (not
  `IfcClassificationReference`) — it declares the *system*, not a facet.
- It **does** permit nesting: `IfcClassification.HasReferences → IfcClassificationReference
  → HasReferences → IfcClassificationReference`, so the classification tree itself can be
  carried in the file.
- It covers only `Source`, `Name`, `ReferenceTokens` and `HasReferences` on the
  `IfcClassification` — it does **not** carry `Edition`, `EditionDate`, `Location` or
  `Description` at this level, whereas the object-level template does.

**[INFERENCE]** — the shape RV1.2 appears to intend is: declare the classification system
once on `IfcProject` via Project Classification Information, then have each `IfcSpace`'s
`IfcClassificationReference.ReferencedSource` point at that same `IfcClassification`
instance. That gives one system declaration and N facet references, which is also what
keeps the file small.

---

## 6. Corrections to the premises this question arrived with

Two things in the framing were wrong and should not be carried forward.

**The URL `…/RV1_2/HTML/schema/templates/classification-association.htm` does not exist.**
It returns **HTTP 404** (1,293 bytes), not 403. The 403 previously seen was Cloudflare
answering before routing, and it masked the 404. The real page is
**`…/RV1_2/HTML/schema/templates/classification.htm`** (HTTP 200, 66,553 bytes). "Classification
Association" is the name used in the RV1.2 *narrative* prose (§"Object association", quoted
in §2 above); "Classification" is the name of the *concept template*, of its documentation
page, and of its Chapter 4 index entry (4.4.1). Same concept, two names, one live URL.

**Where the name "Classification Association" as a page actually comes from: IFC4.3.**
The IFC4.3 concept tree publishes it under exactly that name —
`https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/content.html` links
`Object_Association/Classification_Association/content.html`. So the URL in the premise was
an IFC4.3 path pattern applied to the RV1_2 tree, which is why it 404'd. Worth remembering:
**IFC4.3 renamed these concepts**, and IFC4.3 paths do not transfer to the IFC4 ADD2 TC1
RV1_2 tree. Note also that the directory listing on the RV1_2 tree is enabled — the
`schema/templates/` directory holds 124 `.htm` files and can be enumerated directly, which
is the fastest way to find a concept's real page name rather than guessing at it.

**`…/RV1_2/HTML/schema/ifckernel/lexical/ifcrelassociatesclassification.htm` does exist** —
HTTP 200, 12,820 bytes, with the sections `IfcRelAssociatesClassification` / Semantic
definitions at the entity / Inherited definitions from supertypes / **Definitions applying to
Reference View** / Formal representations. Its entity definition:

> The objectified relationship IfcRelAssociatesClassification handles the assignment of a
> classification item (items of the select IfcClassificationSelect) to objects occurrences
> (subtypes of IfcObject) or object types (subtypes of IfcTypeObject).

**A reading trap on the lexical pages — the "R" column.** Every lexical page's attribute
table ends in a column headed `R`, with no legend anywhere on the page, and its cells
contain `X`. It is tempting to read that against the exchange-requirement legend quoted in
§4, where **X = "Excluded — the attributes must be omitted"**. **That reading is wrong.**
Checked directly: `IfcSpace` — indisputably in scope — shows the identical `X` on
`GlobalId`, `OwnerHistory` and `Name` as `IfcRelAssociatesClassification` does:

```
IfcSpace                        1 | GlobalId | IfcGloballyUniqueId |   | … | X
IfcRelAssociatesClassification  1 | GlobalId | IfcGloballyUniqueId |   | … | X
```

`GlobalId` is mandatory on every `IfcRoot` subtype and cannot be omitted, so `X` in this
column is a **tick meaning "this attribute is referenced by the model view"**, not the ER
exclusion flag. The R/O/X flags live in a different table (the per-entity exchange
requirement tables), not this one. Do not cite this column as evidence of anything.

**Cloudflare is not actually blocking this host.** `WebFetch` gets 403; `curl` with an
ordinary browser `User-Agent` gets 200. Every buildingSMART page in this note was retrieved
that way. This is worth recording for future IFC research in this repo — the standards site
is reachable, it just rejects the default agent string.

**And `docs/spec/ifc-export.md` §2.1's list is confirmed non-exhaustive**, exactly as this
question suspected. That list was written for what the file needed at the time. It should not
be read as a closed enumeration of RV1.2.

---

## 7. Reproduction transcript

Everything above is re-derivable from these commands.

**The vendored mvdXML** (`ifcopenshell 0.8.5`, pinned):

```
venv/Lib/site-packages/ifcopenshell/mvd/mvd_examples/officials/ReferenceView_V1-2.mvdxml
```

Line numbers into that 13,875-line file:

| What | Line |
|---|---|
| `<ModelView … code="ReferenceView_V1-2" version="1.2" owner="bSI">` | 7372 |
| "Objective" scope list — "spatial elements (spaces, zones) … and classification" | 7417 |
| "Object association" — "*Classification Association*" | 8513 |
| Exchange-requirement legend (R / O / X) | ~8754 |
| ConceptTemplate "Classification" `4a224609…` | 2424 |
| SubTemplate "Classification for Objects" `21359513…` | 2549 |
| SubTemplate "Classification for Objects with Override" `2a56ad37…` | 2642 |
| ConceptTemplate "Project Classification Information" `818ca5a3…` | 639 |
| ConceptRoot `IfcObjectDefinition` + its Classification concept | 11774 / 11780 |
| ConceptRoot `IfcSpace` | 12812 |
| ConceptRoot `IfcProject`, incl. Project Classification Information | 12040 / 12090 |

**Live pages** (all HTTP 200 on 2026-09-01, base
`https://standards.buildingsmart.org/MVD/RELEASE/IFC4/ADD2_TC1/RV1_2/HTML/`):

```sh
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
B="https://standards.buildingsmart.org/MVD/RELEASE/IFC4/ADD2_TC1/RV1_2/HTML"
curl -sL -A "$UA" "$B/content.htm"                                            # 200    - "IFC4 RV - 1.2 [Official]"
curl -sL -A "$UA" "$B/schema/toc-4.htm"                                       # 200    - Ch.4 index: 4.4.1 Classification
curl -sL -A "$UA" "$B/schema/ifcproductextension/lexical/ifcspace.htm"        # 63086  - the decisive table
curl -sL -A "$UA" "$B/schema/ifckernel/lexical/ifcobjectdefinition.htm"       # 200    - "Concept usage: Classification"
curl -sL -A "$UA" "$B/schema/templates/classification.htm"                    # 66553  - section 4.4.1
curl -sL -A "$UA" "$B/schema/templates/classification-for-objects.htm"        # 43598
curl -sL -A "$UA" "$B/schema/templates/classification-for-objects-with-override.htm"  # 24259
curl -sL -A "$UA" "$B/schema/ifckernel/lexical/ifcrelassociatesclassification.htm"    # 12820
curl -sL -A "$UA" "$B/schema/templates/"                                      # 200    - dir listing, 124 files
curl -sL -A "$UA" "$B/schema/templates/classification-association.htm"        # 404    - does not exist
curl -sL -A "$UA" "$B/annex/annex-f/4022/modelviews.htm"                      # 200    - changelog: "Classification for Objects with Override | ADDED"
curl -sL -A "$UA" -o bsi.mvdxml \
  "$B/annex/annex-a/reference-view/ReferenceView_V1-2.mvdxml"                 # 805551 - bSI's own mvdXML
```

**Provenance byte-proof** - bSI's published mvdXML vs the vendored copy:

```python
bsi  = open('bsi.mvdxml','rb').read()
vend = open('venv/Lib/site-packages/ifcopenshell/mvd/mvd_examples/'
            'officials/ReferenceView_V1-2.mvdxml','rb').read()
norm = bsi.replace(b'\r\n', b'\n').replace(b'\xc2\xa0', b' ')
assert norm == vend
# bsi  805551  c0b41798bea9af26d2745f1c6f664c0a0279326007a41ebe12b9ec7eeade34f6
# vend 792777  0b6eab1e6d878874000c51a1deba1ec711b81152e1023059060f339ab41e4fb5
# norm 792777  0b6eab1e6d878874000c51a1deba1ec711b81152e1023059060f339ab41e4fb5
# 12771 CRLF + 3 NBSP = 12774 = 805551 - 792777
```

**mvdXML XSD** (subtype-inheritance rule, line 373):

```sh
curl -sL https://raw.githubusercontent.com/buildingSMART/mvdXML/master/mvdXML1.2/xsd/mvdXML_V1.2.xsd
```

**Schema hierarchy** (pinned `ifcopenshell 0.8.5`):

```python
import ifcopenshell
s = ifcopenshell.ifcopenshell_wrapper.schema_by_name('IFC4')
d = s.declaration_by_name('IfcSpace')
while d: print(d.name(), d.is_abstract()); d = d.supertype()
```

---

## 8. Caveats — what was *not* established

Stated plainly, so nothing here is over-read.

- **The mvdXML carries `status="sample"` on every element**, including the `ModelView`
  itself, and the file's `name=""` is empty. This is now definitively an IfcDoc export
  artefact rather than anything about the content's standing: the byte-diff in §3 proves
  `status="sample"` is present **identically in buildingSMART's own published copy**. Note
  that bSI labels this release three different ways across three artefacts - the MVD
  database says `Final`, the documentation banner says `[Official]`, the mvdXML attributes
  say `sample`. §1 leads with the `[Official]` HTML for that reason, with the mvdXML as
  machine-readable corroboration - not the other way round.
- **No certification evidence was gathered.** Whether any RV1.2-certified exporter actually
  writes space classification, and whether bSI's certification test suite exercises it, was
  not investigated. In-scope per the MVD is not the same as exercised by certification.
- **No `IfcSpace`-level exchange-requirement flag (R/O/X) was located** for Classification.
  The concept carries no `<Requirements>` element, and the per-entity ER tables were not
  exhaustively read. The conclusion "not mandatory" rests on the absence of a requirement
  element plus the legend's own wording, not on a table that says "O" against this row.
- **The mvdXML was not XSD-validated.** No `lxml`/`xmllint` was available, and the schema
  host named in the file's own `xsi:schemaLocation`
  (`buildingsmart-tech.org/mvd/XML/1.1/mvdXML_V1.1_add1.xsd`) is dead with no archived copy.
  Immaterial to the verdict - the file's semantics were read directly, and the published
  HTML agrees - but the file has not been machine-checked against its declared schema.
- **`ReferenceView_V1-2` vs `ReferenceView_V1.2`.** The MVD's own identifier attribute is
  `code="ReferenceView_V1-2"` - a **hyphen**. `docs/spec/ifc-export.md` §2.2 writes
  `ViewDefinition [ReferenceView_V1.2]` - a **dot**. The RV1.2 specification requires that
  "for export, the schema identifier and model view identifier must be written to the file"
  but the exact header string bSI mandates was **NOT CONFIRMED** in this pass. This is
  orthogonal to the question asked and does not affect the verdict, but it is a loose thread
  worth pulling before §10 check #2 is treated as authoritative.

---

## 9. What this means for `docs/spec/ifc-export.md`

Not applied here — this note only reports. For whoever picks up the decision:

1. The **§2.1 permitted-concepts list can gain "Classification Association"** without
   qualification. It belongs there on the same footing as Material Association.
2. **§10 check #2 stays valid.** Writing classification on spaces does not conflict with the
   `ReferenceView_V1.2` header assertion.
3. If space classification is written, the file should probably **also** carry Project
   Classification Information on `IfcProject` (§5), so the classification system is declared
   once and the per-space references resolve against it.
4. `IfcClassification.Edition` and `EditionDate` **may** be written — useful, given this
   repo's habit of pinning every standard to a dated edition. That is exactly the metadata
   slot for "AzDTN 2.7-2, Baku 2021".
5. Do **not** nest `IfcClassificationReference` under a space's own reference — RV1.2's
   object-level template has no `HasReferences` rule (§4). Nesting belongs at the project
   level if it is needed at all.

**One warning for any future MVD-checking code.** RV1.2's `ConceptRoot` for `IfcSpace`
(`75217ae0-a1fb-43ad-b52d-a6b5d75e53fb`) does **not** itself declare a Classification
concept, and Classification is likewise absent from the `IfcSpace` page's own "Concept
usage" prose section. The applicability comes **purely from inheritance** at
`IfcObjectDefinition`. Any validator — ours or a third party's — that resolves concepts
per-entity out of the mvdXML **without walking the supertype chain will wrongly conclude
that Classification does not apply to `IfcSpace`.** If §10 ever grows an mvdXML-driven
check, this is the defect it will have. It is also, most likely, the reason §2.1's list
omitted classification in the first place.
