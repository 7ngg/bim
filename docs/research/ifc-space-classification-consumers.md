# Does anything actually *read* a classification on an `IfcSpace`?

**Research date:** 2026-09-01
**Question:** the engine is deciding whether to emit `IfcRelAssociatesClassification` →
`IfcClassificationReference` (Uniclass 2015 table SL) on every exported `IfcSpace`.
`IfcSpace.Name` (private key, `bedroom_double`) and `IfcSpace.LongName` (AZ display
label) already ship. **Is a third, shared identifier read by any real consumer, or is
it write-only metadata?**

**Method.** Three kinds of evidence, in descending trust:

1. **Executable, first-hand** — a classification round-trip built and queried against
   this repo's own pinned `ifcopenshell 0.8.5`, and a corpus of **six published IFC
   models downloaded and parsed locally**. Transcript in §8. These claims are not
   quoted from anyone; they were run.
2. **First-party vendor documentation and vendor source code** — `help.graphisoft.com`,
   `help.drofus.com`, the buildingSMART bSDD/IFC mapping doc, the `Autodesk/revit-ifc`
   and `IfcOpenShell` repositories.
3. **Secondary** — labelled as such, and never load-bearing alone.

Where a source does not answer, this note says **COULD NOT CONFIRM** and says what was
tried. The brief explicitly asked for that, and §7 collects every instance.

Two existing notes are **cited, not re-derived**: `docs/research/room-classification-standards.md`
(the schema has no room-use vocabulary; Uniclass `SL_45_10` is the candidate) and
`docs/research/competitive-landscape.md` / `docs/research/floorplan-generation-stack.md`
(the competitor set).

---

## 0. Headline

**The doubt is right, but not for the reason it assumes. It is not dropped — it is
ignored.**

Every major consumer *retains* a classification on an `IfcSpace`. Revit turns it into a
real shared parameter; Archicad keeps it and lets you schedule on it; IfcOpenShell indexes
it as a first-class query facet. The plumbing is genuinely there, and this note proves it
from vendor source code rather than asserting it.

**And essentially nobody uses the plumbing.**

| the three tests the brief set | answer |
|---|---|
| **Does an importer surface it?** | **Yes.** Confirmed for **Revit** (`ClassificationCode` shared parameter), **Archicad** (IFC Manager) and **Bonsai** (panel + selector), plus **Allplan**, **ACCA PriMus IFC** and **That Open Engine**. **Navisworks: partial** — the value is handed over, the surface is closed source. **Solibri: could not confirm.** |
| **Does a checker query it?** | **Only through IDS.** The IDS Classification facet exists, defaults to `required`, applies to `IfcObjectDefinition`, and has a runnable implementation in this repo's own dependency tree (`ifctester`). **Every native space rule examined keys on something else** — Solibri's rule 183 enumerates eight permitted properties and IFC classification is not one of them. |
| **Does a downstream workflow key off it?** | **No shipped one.** Of ten QTO/cost tools, only Solibri and dRofus tie classification to spaces at all, and in both cases it is their **own** classification concept, not `IfcRelAssociatesClassification`. |

**The finding that should settle it is empirical, not documentary.** Six published IFC
models were downloaded and parsed: **431 `IfcSpace` entities, from four authoring tools,
2011–2024, including buildingSMART's own current certification dataset. Zero carry a
classification.** The same corpus classifies **3,345 non-space objects**. Archicad ships a
switch built for precisely this — *"ArchiCAD Zone Categories as IFC Space classification
data"* — and on a real delivered Dutch housing project it was **Off** while element
classification was on. buildingSMART's own single-family-house certification model
classifies the **building** and leaves both its rooms bare, putting the room use in
`ObjectType` instead.

**So: space classification is, in current practice, write-only metadata.** Not because it
is unreadable, but because the industry does not write it, and so nothing was ever built
to consume it.

**Two arguments survive that verdict, and only two.**

1. **The vacuous-pass hazard, and it is the strongest thing in this note.**
   buildingSMART's own published IDS sample selects rooms by *applicability*
   `IfcSpace + classification = SL_45_10_09` — **Bedrooms, the exact code this engine would
   emit**. Run that check against an export with no classification and it matches zero
   elements and **passes green**. A silent false negative is worse than a red one. If a
   client ever hands over an IDS shaped like the standards body's own sample, silence
   costs more than noise.
2. **COBie 2.4 / BS 1192-4 handover**, where `Space.Category` is a Required field
   populated from Uniclass 2015 Table SL. ⚠️ Vendor-attested (§4.3), not read from BSI.

**Three things that should temper it.**

- **COBie V3 moved the classification off `IfcSpace` and onto `IfcSpaceType`**, reached via
  `IfcRelDefinesByType`. The plan on the table matches the *older* model. For a residential
  generator emitting many occurrences of twelve room types, the type-level route is also
  the better-normalised one. **"On the occurrence or on the type" is a bigger question than
  "ship it or not", and the ticket does not currently ask it.**
- **The Dutch national IDS deliberately excludes `IFCSPACE`** from its classification
  requirement — a national body wrote the entity list out and left spaces off it.
- **No residential handover standard anywhere names space classification.** If the case is
  "housing handover needs it", that case is not supported by anything published this pass
  could find. And no competitor emits it (§5).

**What it costs, measured:** +26 STEP instances on a 19-space plan, three new entity types
on the spec surface, a Uniclass version pin *and* a second schema-version pin (the
dictionary-URI attribute is `Location` in IFC4 and **`Specification`** in IFC4.3). Revit
discards the `Location` URI and the `Edition` on import anyway, and mangles the code into
`[Uniclass 2015]SL_45_10_09:Bedrooms`.

**If it ships, one design note earns its place regardless of the above:** write the code
into a **property** as well as into the classification. A Pset property is the only channel
Archicad's import translator can route into an Archicad Property (and therefore into
Graphic Overrides), and it is the only channel Solibri's filters, rules, ITO and native
Classification builder are first-party documented to consume. **The classification is the
standards-conforming carrier; a property is the one that anything acts on.**

---

## 1. The carrier works, and it is queryable — proved, not asserted

Built against the repo's own pinned `ifcopenshell 0.8.5`: two `IfcSpace`s, one carrying
a Uniclass reference exactly as the engine would write it, one bare.

```
#2=IFCSPACE('2L7P1PsVDDvgxnoMO_U4h9',$,'bedroom_double',$,$,$,$,'Ikiotaqli yataq otagi',$,$,$);
#4=IFCCLASSIFICATION('NBS','v1.36',$,'Uniclass 2015',$,$,$);
#6=IFCCLASSIFICATIONREFERENCE($,'SL_45_10_09','Bedrooms',#4,$,$);
#7=IFCRELASSOCIATESCLASSIFICATION('2lEGgLyUj2ch9kVrhV_QHT',$,$,$,(#2),#6);
```

`ifcopenshell.util.selector` — the query engine behind Bonsai's search, IfcCSV and
IfcPatch — resolves it as a **first-class facet**, not a property lookup. The grammar at
`selector.py:46` lists `classification` beside `entity`, `attribute`, `material`,
`property`, `location`, `group`, `parent`:

```
facet: instance | entity | attribute | type | material | query | classification | location | property | group | parent
classification: "classification" comparison value
```

Every one of these ran and returned the right space:

| query | result |
|---|---|
| `IfcSpace, classification="SL_45_10_09"` | `['bedroom_double']` |
| `IfcSpace, classification="Bedrooms"` | `['bedroom_double']` |
| `IfcSpace, classification=/SL_45_10.*/` | `['bedroom_double']` (regex) |
| **`IfcSpace, classification=NULL`** | **`['kitchen']`** |

That last row is the one that matters. **"Find every space that is *not* classified" is
a one-line query.** That is the shape of an audit rule, and it works today.

And the value is *extractable*, not merely *matchable* — which is the difference between
colouring a view and filling a schedule column:

```
get_element_value(s1, 'classification.Identification')  ->  ['SL_45_10_09']
get_element_value(s1, 'classification.Name')            ->  ['Bedrooms']
```

`selector.py:1037` shows why both the code and the title match: the facet compares
against `reference.Name` **and** against `Identification` (falling back to `ItemReference`
on IFC2X3). So a downstream query keyed on either spelling hits.

**Conclusion for §1:** the carrier is not inert in the open-source stack. It is indexed,
filterable, regex-matchable, null-testable, and readable into a spreadsheet cell.

---

## 2. But nobody in the wild puts one on a space — 431 spaces, zero classified

This is the finding that should decide the question, and it is entirely first-hand:
six published IFC models were **downloaded and parsed locally**, not read about.

| model | schema | authoring tool | `IfcSpace` | **spaces classified** | `IfcRelAssociatesClassification` | objects classified |
|---|---|---|---|---|---|---|
| Duplex Apartment (architectural) | IFC2X3 CV | Autodesk Revit Architecture 2011 | 21 | **0** | 0 | 0 |
| Duplex Apartment (MEP, "ROOMS_AND_SPACES") | IFC2X3 | Autodesk Revit MEP 2011 | 37 | **0** | 0 | 0 |
| Medical-Dental Clinic (architectural) | IFC2X3 | Revit Architecture 2011 + Solibri IFC Optimizer | 269 | **0** | 0 | 0 |
| **Schependomlaan** (Dutch housing project) | IFC2X3 CV2.0 | **Graphisoft ArchiCAD 18** | 100 | **0** | 56 | **3,343** |
| buildingSMART PCERT sample scene | **IFC4 ReferenceView_V1.2** | IFC-manager for SketchUp 5.3.3 (2024) | 2 | **0** | 1 | 1 |
| buildingSMART PCERT sample scene | **IFC4X3_ADD2 ReferenceView** | IFC-manager for SketchUp 5.3.3 (2024) | 2 | **0** | 1 | 1 |
| **total** | | **4 authoring tools, 2011–2024** | **431** | **0** | **58** | **3,345** |

Three of these deserve to be read closely, because each kills a different defence of the
"ship it" position.

### 2.1 Schependomlaan: the tool classified 3,343 objects and skipped every space

Schependomlaan is a real Dutch residential project, and it is *not* an unclassified
model. Its Archicad export classifies walls, slabs, coverings, beams, windows, doors,
stairs, railings and columns with **NL/SfB** codes:

```
#399=IfcClassificationReference($,'21.12','SPOUWWANDEN',#397);      -- cavity walls
#5812=IfcClassificationReference($,'13.22','VLOEREN ALS GEBOUWONDERDEEL',#5811);
```

`{'IfcWall': 652, 'IfcCovering': 1262, 'IfcSlab': 279, 'IfcWallStandardCase': 282, 'IfcWindow': 259, 'IfcDoor': 205, …}`
— **and `IfcSpace: 0`.** All 100 spaces carry room use the ordinary way instead:
`Name='3.07'`, `LongName='slaapkamer 2'`. Number in `Name`, human label in `LongName`.

The reason is recorded **inside the file's own header**, in Archicad's serialised
translator settings:

> `Option [ArchiCAD Zone Categories as IFC Space classification data: **Off**]`

So this is not a tool that *can't*. Graphisoft ships a dedicated switch for exactly this
— see §3.1 — and on a real delivered project it was left off while element
classification was left on. **Classification is an element practice, not a space
practice.**

### 2.2 buildingSMART's own certification sample: a house that classifies the *building*, not the rooms

The PCERT sample scene is buildingSMART's certification dataset, refreshed 2024-11-14,
published in both **IFC4 Reference View** and **IFC4X3_ADD2 Reference View** — the same
view family ADR 0011 pins. It is a **single-family house**: residential, exactly the
repo's context. It contains one classification, and it is on the `IfcBuilding`:

```
#34=IFCCLASSIFICATION('Molio','1.0','2023-01-23','CCI Construction',$,
      'https://identifier.buildingsmart.org/uri/molio/cciconstruction/1.0',$);
#35=IFCCLASSIFICATIONREFERENCE('…/class/E-AAA','E-AAA','Single-family house',#34,$,$);
#36=IFCRELASSOCIATESCLASSIFICATION(…,(#30),#35);      -- #30 is the IfcBuilding
```

Its two spaces get nothing. What they get instead is worth noting, because it is a
**third carrier this repo has not considered**:

```
#89=IFCSPACE(…,'living room','A cozy space…','living area',…,'living room',.ELEMENT.,$,0.);
                 ^Name          ^Description   ^ObjectType         ^LongName
```

`ObjectType` = `'living area'`, `'hallway'`. buildingSMART's own reference file puts the
room-use string in **`ObjectType`**, not in a classification. (`ObjectType` is the
IFC-sanctioned partner of `PredefinedType = USERDEFINED`; it is a free `IfcLabel`, so it
is a *string in one language* and carries the same defect as `LongName` — but it is what
the standards body's own file does.)

### 2.3 Three Revit exports: not one classification entity in 327 spaces

The Duplex Apartment and the Medical-Dental Clinic are the two most-circulated IFC test
models in the industry. Between them, 327 `IfcSpace`s and **zero** `IfcClassification`,
`IfcClassificationReference` or `IfcRelAssociatesClassification` anywhere in the file.
Their spaces carry `Name='A101'` / `LongName='Foyer'` — again number-then-label.

**[INFERENCE]** Since these files are the corpus every importer has been tested against
for fifteen years, no importer's space-classification path has been meaningfully
exercised by the industry's own regression set. That is a claim about *test coverage*,
not about capability, and it is reasoning over the scan rather than something a source
states.

---

## 3. Per-consumer findings

### 3.0 The table

"Reads it" means the value survives import and is addressable. **"Useful" is the harder
test** — can a user filter, schedule, query or colour by it.

| Consumer | Reads it on import? | Where it lands | Filter / schedule / colour? | Prefers `Name`/`LongName`/Pset? | Primary source |
|---|---|---|---|---|---|
| **Revit** (Open/Link IFC) | ✅ **YES** | shared parameter **`ClassificationCode`**, group *IFC Parameters*, on a **Generic Model DirectShape** — **not a Room** | ✅ schedule/filter/colour **inside the imported RVT**; ⚠️ across a *link* needs the generated `.sharedparameters.txt` loaded into the host | ✅ yes — classification never touches naming | `revit-ifc` source (§3.1) |
| **Navisworks** | ⚠️ **PARTIAL** — value is handed to Navisworks by the Revit-based reader; the surface is closed source | property named `ClassificationCode`; **which tab: COULD NOT CONFIRM** | ✅ *if* it shows in Properties, Find Items → Search Set → Clash / Appearance Profiler follows mechanically | ✅ yes | `IFCNavisProcessor.cs` + Autodesk help (§3.2) |
| **Archicad** | ⚠️ **SPLIT** — retained as *IFC data*; **does not** populate the native Classification Manager | IFC Manager / IFC Project Manager, under *Classification References* | ✅ **Interactive Schedule + Find & Select**; ❌ **Graphic Overrides cannot see IFC data at all** | ✅ yes — Zone Name ↔ `LongName`, Zone Number ↔ `Name` | help.graphisoft.com AC29 (§3.3) |
| **Solibri** | ❓ **COULD NOT CONFIRM** — zero help-centre hits for the entity | not documented; no Classification tab in the Info view | ⚠️ **only via IDS rule #244**; the native space rules **cannot** — rule 183's key list is a closed enumeration of 8 properties and IFC classification is not one | ✅ yes — rules 36 and 183 key on Space Name / Number / Type + Psets | help.solibri.com (§3.4) |
| **Bonsai / IfcOpenShell** | ✅ **YES, fully** | *Classification References* panel — `poll()` accepts any `IfcObjectDefinition` | ✅ **best in the set**: selector facet, Bonsai search UI, IfcCSV group-and-sum, ifc5d cost query, ifctester IDS audit | ✅ available alongside, not instead | repo source + §1 executable proof (§3.6) |
| **dRofus** | ⚠️ **writes it; reading it back is not documented** | its own room-classification fields | ✅ **filters reports by classification** (its own, DB-side) | ✅ room Name / function number | help.drofus.com (§3.5) |
| **QTO / cost tools** | ⚠️ **mostly no** — only **Solibri** and **dRofus** tie classification to *spaces* in first-party docs | varies | ACCA PriMus IFC uses it to *select* entities for takeoff; Autodesk Takeoff uses uploaded CSVs instead | ✅ overwhelmingly name/property-driven | §3.7 |

### 3.1 Revit — reads it, and puts it on the wrong kind of object

**This is the best-evidenced row in the note, and it improves squarely on the repo's
existing complaint that Autodesk claims "rest on secondary or search-summary sources".**
It is read out of Autodesk's own open-source importer at
[`Autodesk/revit-ifc`](https://github.com/Autodesk/revit-ifc) master, commit
`e80e3d372f06d7fb704e250c7676e58e566b04e8`, cross-checked against branches
`Release_19.x.x` … `Release_27.x.x`.

**It is read.** `IFCObjectDefinition.cs:568-587` handles exactly **two** `IfcRelAssociates`
subtypes and logs everything else as unhandled — materials, and classification:

```csharp
else if (IFCAnyHandleUtil.IsSubTypeOf(hasAssociation, IFCEntityType.IfcRelAssociatesClassification))
   ProcessRelAssociatesClassification(hasAssociation);      // line 581
```

The handler's own doc-comment states the intent: *"Keep Classification assignment
information for creation of parameters later on"*. It reads `ReferencedSource.Name`,
`Name`, and — branching on schema version — `ItemReference` (IFC2X3) or `Identification`
(IFC4+), then composes:

```
[<ReferencedSource.Name>]<Identification>:<IfcClassificationReference.Name>
```

For this engine's output that would materialise as
**`[Uniclass 2015]SL_45_10_09:Bedrooms`**. Note what that means: **the bare code is never
stored on its own.** Anything downstream must parse the `[…]…:…` envelope itself.

It lands as a **genuine shared parameter**, not a pseudo-parameter:
`ParametersToSet.AddParameterBase` creates an `ExternalDefinition`, binds it as an
`InstanceBinding`, and inserts it under `GroupTypeId.Ifc` — the **"IFC Parameters"** group
in the properties palette — with the definition written to
`<yourfile>.ifc.sharedparameters.txt`. Both **Open IFC** and **Link IFC** take this path.
The logic is character-for-character identical back to `Release_19.x.x`, i.e. **Revit
2019**.

**But the object it lands on is not a Room.** `IFCCategoryUtil.cs:539`:

```csharp
m_EntityTypeToCategory[IFCEntityType.IfcSpace]     = BuiltInCategory.OST_GenericModel;
m_EntityTypeToCategory[IFCEntityType.IfcSpaceType] = BuiltInCategory.OST_GenericModel;
```

An imported `IfcSpace` becomes a **DirectShape in Generic Models**. Not a Revit Room, not
an MEP Space. It therefore carries **no room semantics at all**: no area or volume
computation, no room-bounding, no room tags, no key schedules. Autodesk's own issue
[**#15 "Link IFC does not create Room/Space from IfcSpace"**](https://github.com/Autodesk/revit-ifc/issues/15)
has been **open since 2018-08-08** with no maintainer resolution.

**So the classification is not moot — the DirectShape is real, selectable and
parameterised — but it decorates a generic solid, not a room.** Inside the resulting RVT
the parameter is schedulable, filterable and usable in a colour-override filter rule.
Across an IFC *link*, the host must first load the importer-generated
`.sharedparameters.txt` and add `ClassificationCode` as a project parameter — Autodesk
states *"All fields that are available for elements in the host project are available for
elements in linked models"*
([help](https://help.autodesk.com/cloudhelp/2026/ENU/Revit-Collaborate/files/GUID-0CD60F7E-D18F-4444-A20F-5408CA1163AF.htm)),
which implies but does not state the matching-GUID requirement; that last step rests on
**secondary** sources.

**What Revit throws away**, straight from the code:

- `IfcClassificationReference.Location` — **never read**. The bSDD URI that §6.3 goes to
  trouble over does not survive into Revit.
- A `RelatingClassification` that is a plain `IfcClassification` rather than a
  `…Reference` — dropped, **with no warning logged**.
- `IfcClassification.Edition` / `.Source` / `.EditionDate` — never read on import. **The
  Uniclass version the repo would carefully pin does not arrive.**
- `Description`, `Sort` — never read.

**And a round-trip bug worth knowing before anyone plans on one.** Import writes
`ClassificationCode`, `ClassificationCode(1)`, `(2)`…`(9)`. Export
(`ClassificationUtil.CreateClassification`) reads `ClassificationCode`,
`ClassificationCode(2)`…`(10)` — **never `(1)`**. On an IFC → Revit → IFC round trip an
element's *second* classification association is silently dropped and the rest are off by
one. Harmless for this engine (one code per space), but it is a fair measure of how much
attention this path gets.

**Naming is untouched by classification.** `IfcSpace.Name` → `Element.Name` plus a shared
parameter `IfcName`; `IfcSpace.LongName` → a shared parameter **`LongNameOverride`**;
`Description` → `IfcDescription`. Nothing maps to Room Name or Room Number, because no
Room exists.

**And the whole import path is undocumented by Autodesk.** A search of help.autodesk.com
and of the `revit-ifc` issue tracker found 20 issues with "classification" in the title —
**every one about export**, none about import. The behaviour exists only in the source.
Do not expect Autodesk support to acknowledge or defend it.

*(Export, kept separate: Revit's canonical carrier is a parameter also named
`ClassificationCode`, configured through the **Classification Settings** dialog which
collects Name / Edition / Source / Location. `ExporterUtil.ExportElementClassifications`
applies it to all products including Rooms, with the comment "No need to check the subtype
since Classification can be assigned to IfcRoot." So Autodesk agrees on the carrier — it
is the import surface that is thin.)*

### 3.2 Navisworks — the value is handed over; what happens next is closed source

Navisworks' "Modern"/v3 IFC readers are the same Revit-based codebase (the repo describes
itself as *"IFC for Revit (2019+) and Navisworks (2019-2024)"*). There is a dedicated
consumer, `IFCNavisProcessor.cs`, and `ParametersToSet.AddStringParameter` calls it
**before** any Revit-specific work:

```csharp
bool? processedParameter = Importer.TheProcessor.ProcessParameter(objDef.Id, parameterSetId, parameterName, parameterValue);
if (processedParameter.HasValue) return processedParameter.Value;   // short-circuits the Revit path
```

and `IFCNavisProcessor.ProcessParameter` forwards it unconditionally. **So the string
`[Uniclass 2015]SL_45_10_09:Bedrooms` does reach the Navisworks object model, under the
property name `ClassificationCode`.**

**Where it surfaces: COULD NOT CONFIRM.** The `IElement` implementation that decides the
Properties *tab* is stubbed in the open repo (`// NAVIS_TODO: This is inside Navis code.`)
and is not published. Autodesk's Properties Window help says only that the window *"has a
dedicated tab for each property category"* without enumerating IFC categories.

**If it is visible it is queryable** — Navisworks has no special classification concept; a
search statement is *"a property (a combination of category name and property name), a
condition operator, and a value"*, so anything in Properties is addressable in Find Items,
hence in a Search Set, hence in Clash Detective and the Appearance Profiler.

**Two risks specific to this consumer, both first-party:**

1. **The default reader in current Navisworks is `v4`, which is a different pipeline.**
   The [IFC file reader options page](https://help.autodesk.com/cloudhelp/2026/ENU/Navisworks/files/GUID-E1CD4663-D460-4EA5-ABEC-FD24885BA3A6.htm)
   describes v4 as *"the recommended Revit-based converter (default). This method adopts
   the **Autodesk Translation Framework**"*. The revit-ifc repo's scope stops at Navisworks
   2024. **Whether v4/ATF preserves `ClassificationCode` is COULD NOT CONFIRM.** The
   `Legacy` reader does not use this codebase at all.
2. **Spaces can be switched off wholesale.** Same page: *"Select this check box to bring
   through and visualize spaces. **When this check box is clear, the file reader ignores
   spaces.**"* If unticked, the `IfcSpace`s never arrive and the classification question
   never gets asked.

There is precedent for exactly this going wrong: an Autodesk troubleshooting article
titled *"IFC Uniformat Classification code missing when using Revit_IFC loader"* describes
the classification code going missing after IFC load in Navisworks, with **search sets
built on that property failing to find elements**. (Obtained via search summary only — the
page 403s to automated fetch. **Secondary-grade.**)

### 3.3 Archicad — schedulable, not colourable, and it never becomes a native Classification

The important correction here, and it is the opposite of what one would assume: **Archicad
does not derive its native Classification from an incoming classification association.**
Its import algorithm ([AC29 Help, *Import IFC Model*](https://help.graphisoft.com/AC/29/INT/_AC29_Help/121_IFC/121_IFC-5.htm))
is explicit at step 4:

> "**Which Classification should be assigned to the element? (This is based on the
> Translator's "Type Mapping for IFC Import" preset.)**"

and [*Type Mapping for IFC Import*](https://help.graphisoft.com/AC/29/INT/_AC29_Help/121_IFC/121_IFC-26.htm)
says what that preset consumes:

> "Use this chart to define how to classify imported IFC elements, **based on their IFC
> Type**. … **The IFC Type (far left column) is mapped to the Classification (far right
> column)**"

So an `IfcSpace` carrying `SL_45_10_09` gets whatever Archicad Classification `IfcSpace`
is mapped to. **The Uniclass code has no influence on it.** Options → Classification
Manager imports XML or project files only — there is no IFC path into it.

**It is retained, though, as IFC data.** [*Update with IFC Model*](https://help.graphisoft.com/AC/29/INT/_AC29_Help/121_IFC/121_IFC-9.htm):

> "**"IFC data" include IFC Attributes, IFC Properties and IFC Classification References**
> … **Merge new from IFC: IFC Attributes and IFC Classification References which do not
> yet exist in the host project will be added to elements in common.**"

**And it is schedulable.** [*Define Element Criteria using IFC Data*](https://help.graphisoft.com/AC/29/INT/_AC29_Help/121_IFC/121_IFC-22.htm):

> "Element criteria can include IFC data in the following functions: • Find & Select •
> Reserve Elements by Criteria (Teamwork) • **Interactive Schedule Schemes - list IFC data
> assigned to current project elements** … If you select an Attributes folder or a
> **Classification References folder, then all items contained in the folder are added to
> the criteria**"

**But it cannot be coloured by.** [*Property Mapping for IFC Import*](https://help.graphisoft.com/AC/29/INT/_AC29_Help/121_IFC/121_IFC-27.htm):

> "**Import as Archicad Properties** — This option can be useful if you wish to make
> certain IFC property data available for functions which use Archicad Properties (**but
> not IFC Properties**). These functions include: • **Graphic Overrides** • …"

Graphic Overrides consume Archicad Properties, never IFC data — and the only bridge, the
Property Mapping table, has exactly four columns (*"Property, Property Set, Value Type,
and Property Type"*) and **no Classification Reference column**. So there is no route from
an imported classification into a colour override. **[INFERENCE]** — that last step is
read off the column list, not stated by Graphisoft.

**Space identity is `Name`/`LongName`, and it is a fixed, non-configurable rule.** From
Archicad's [predefined mapping table](https://help.graphisoft.com/AC/29/INT/_AC29_Help/121_IFC/121_IFC-50.htm):
Zone **Name** ↔ `IfcSpace.LongName`; Zone **Number** ↔ `IfcSpace.Name`. **That is exactly
the split `docs/spec/ifc-export.md` §6 already ships** — machine key in `Name`, human
label in `LongName` — and it is corroborated independently by the Schependomlaan scan in
§2.1 (`Name='3.07'`, `LongName='slaapkamer 2'`). *(Documented for export; the import
direction is **COULD NOT CONFIRM**.)*

**What Archicad emits is the sharpest signal of all.** Archicad's own Classification does
**not** leave as `IfcClassificationReference` — it leaves as `ObjectType` /
`PredefinedType` / `ElementType`. `IfcClassificationReference` is a *separate, manually
authored channel*: [*Create New Classification Reference*](https://help.graphisoft.com/AC/29/INT/_AC29_Help/121_IFC/121_IFC-16.htm)
describes typing the fields in by hand or applying an XML rule. Combined with §2.1 — the
purpose-built *"ArchiCAD Zone Categories as IFC Space classification data"* switch found
**Off** on a real delivered housing project — the picture is consistent: **for Graphisoft,
space classification is an opt-in annotation, not part of the model.**

### 3.4 Solibri — the one consumer where "could not confirm" is the honest headline

Solibri is the tool most often *named* as the reason to emit classification — dRofus names
it explicitly (§3.5). It is also the one this pass could confirm least.

**Hard negative, and citable:** a search of the entire Solibri Desktop Help Center via its
Zendesk API returns **zero articles** for `IfcClassificationReference` and **zero** for
`IfcRelAssociatesClassification`. The nearest first-party statement is one unelaborated
line inside an article about Solibri's *own* feature
([*Understanding Classifications*](https://help.solibri.com/hc/en-us/articles/1500004070762-Understanding-Classifications)):

> "**Solibri supports ifcClassification.**"

It never says where it appears or how it is keyed. And the documented
[Info view](https://help.solibri.com/hc/en-us/articles/21701046739607-The-Info-View)
structure — *"BIM Data, IFC Header, IFC Standard Properties, IFC Standard Quantities,
Other Properties, and Custom"* — has **no Classification tab**.

⚠️ **Do not conflate two things that share a word.** A **"Solibri Classification"** is a
native `.classification` file — a component filter plus a rule table, editable in the
Classification view, colourable, and consumable by rules and ITOs. It ships with defaults
including *Space Usage*. **It is not `IfcRelAssociatesClassification`.** Solibri's docs use
"Classification" almost exclusively for the native feature.

**Secondary evidence (user posts on Solibri's community — not staff, not corroborated by
any first-party page)** suggests it *is* surfaced, partially: *"when selecting the
classification property from IFC, I can't select the reference and the name separately.
… only the reference is taken into consideration"*, and *"In Solibri i get all the
Uniformat Classifications separately… in the IFCRELASSOCIATESCLASSIFICATION the name is
written 'Uniformat EN_70'. That is why Solibri sees that as a unique Classification."*

**The route that *is* first-party documented is IDS.** Solibri's
[rule #244 IDS Validation](https://help.solibri.com/hc/en-us/articles/19053798036375-244-IDS-Validation)
executes an IDS file as a live ruleset and states it supports *"Official IDS v1.0"*; and
[*Creating an IDS File*](https://help.solibri.com/hc/en-us/articles/39702217779223-Creating-an-IDS-File)
enumerates the facets:

> "There are six different types of facets: … • **Classification: Facet parameters are
> System and Value.** You can also load a this facet and populate validated terms from
> bsDD. … **Applicability**: … This subset can be identified using available facets, such
> as **entity or classification**."

**So: an IDS saying "applicability = `IfcSpace`, requirement = Classification System
`Uniclass 2015`" can be dropped onto Solibri's Checking view and checked.** That is a
real, supported, rule-driven query. ⚠️ **The unstated link:** Solibri nowhere says its #244
implementation resolves the Classification facet against `IfcRelAssociatesClassification`.
The IDS 1.0 spec defines it that way and Solibri claims v1.0 support, so the inference is
strong — **but it is an inference from the standard, not a Solibri statement. Verify
empirically before relying on it.**

**ITO groups by the *native* classification, and that is the documented workflow.**
Solibri's own [space-takeoff tutorial](https://help.solibri.com/hc/en-us/articles/6265532828567-Tutorial-How-to-Takeoff-Space-Information)
uses the shipped `Spaces.ito`: *"usage defined by classification … **The classification
name for each space, based on the `Space usage.classification`**"* — a Solibri
`.classification`, not an IFC association. And the stated
[*IFC Model Requirements for Information Takeoff*](https://help.solibri.com/hc/en-us/articles/4901566051095-IFC-Model-Requirements-for-Information-Takeoff)
mention classification **not at all**: *"To distinguish different types of building
elements from similar component classes, **name, type and dimension data** is required."*

**And the rule closest to this repo's domain cannot key on it — this is a closed
enumeration, not an absence of evidence.** [Rule **183 Program Reconciliation**](https://help.solibri.com/hc/en-us/articles/29367732933143-183-Program-Reconciliation)
is Solibri's space-programme check — *"This rule checks the total areas of spaces by their
types"*, i.e. exactly the housing-schedule reconciliation a floor-plan generator's output
would be put through. Its keying parameter enumerates every property it will accept,
verbatim:

> "**Occupant Organization Classification**: Select the property which should be used as
> location in housing plan. The possible properties are: **Space Name · Space Number ·
> Occupant Organization Name · Occupant Organization Abbreviation · Occupant Organization
> Code · Occupant Sub-Organization Code · Occupant Organization ID · Space Group Name**"

Eight options. **An IFC classification reference is not among them.** Note also what *is*:
`Space Name`, `Space Number`, and a set of `Occupant Organization…` properties — i.e.
`IfcSpace.Name`/`LongName` and **property-set** values. The rule named "…Classification"
does not read IFC classification.

⚠️ **A third meaning of the word, to avoid a trap.** Solibri's
[*IFC Standards Supported by Solibri*](https://help.solibri.com/hc/en-us/articles/23779405208855-IFC-Standards-Supported-by-Solibri)
uses "classifications" to mean **IFC entity classes**: *"IFC 4.3 includes new
classifications for elements common in infrastructure, such as rails, sleepers, earth
layers…"*. So in Solibri's documentation "classification" means one of three unrelated
things depending on the page. Any search of their docs that does not disambiguate will
return a false positive.

**And Solibri's flagship space rule prefers names.** [Rule 36 *Space Requirements*](https://help.solibri.com/hc/en-us/articles/1500004611001-36-Space-Requirements)
identifies a space by **Space Classification** (Solibri's own, chosen from the
Classification View), **Space Type**, **Space Name**, **Space Number** — with the caveat
*"Depending on the source this is not always available. **You can use Space Name
instead.**"* IFC classification is not among the documented parameters.

### 3.5 dRofus — a writer, not a reader, and it names Solibri as the reason

dRofus is the space-programming tool most likely to care, and its documentation is the
clearest first-party evidence anywhere in this note that *someone* thinks this is worth
emitting. [*Export Room Groups as Classification*](https://help.drofus.com/en/English/Learning/groups-in-ifc):

> "Groups are typically exported as a zone object in the IFC model (IFCZone). However,
> groups can be specified to be exported as a **classification object
> (IFCClassificationReference)**. … This can be useful, for example, for **exporting to
> Solibri or other software that can read IFC Classifications.**"

Note the shape of that sentence: it is a *vendor asserting that Solibri reads them*, which
is exactly the claim §3.4 could not confirm from Solibri's own documentation. Treat it as
**second-party corroboration**, and note it concerns **groups**, exported as classification
in lieu of `IfcZone` — not per-space classification.

On the **import** side, dRofus documents nothing. Its
[*Room Classifications*](https://help.drofus.com/en/English/Learning/room-classifications)
page says classifications *"can be pre-loaded into the Project or even transferred from
another Project database"* — **no IFC source is named**. Its
[*Export IFC*](https://help.drofus.com/en/English/Learning/export-ifc) page says only *"The
rooms will be exported as IFCSpace"* with *"name, function number, and Room data"*. So
dRofus's own space identity is **name + function number**, not a classification.

One thing dRofus *does* prove about the reader side, though on its own data rather than
on IFC: classification is a working **report filter** there —
[*Room Classifications*](https://help.drofus.com/en/English/Learning/room-classifications):

> "Classifications can be applied as filters in Reporting. For example you might want to
> run a Room Data Report for all **OmniClass 13-25 11 11 - Primary Circulation Spaces**."

**Verdict: dRofus is evidence for the *writer* side of the market, and for the *shape* of
the workflow — but not for anyone reading a classification back out of an IFC file.**

### 3.6 Bonsai / IfcOpenShell — the one consumer where it is unambiguously useful

Confirmed from the `IfcOpenShell/IfcOpenShell` source and corroborated by the executable
proof in §1 against the repo's own pinned 0.8.5.

**It surfaces, for any object.** `src/bonsai/bonsai/bim/module/classification/ui.py`:

```python
class BIM_PT_classification_references(Panel, ReferenceUI):
    bl_label = "Classification References"
    @classmethod
    def poll(cls, context):
        return (... and element.is_a("IfcObjectDefinition"))
```

`IfcSpace → IfcSpatialStructureElement → IfcSpatialElement → IfcProduct → IfcObject →
IfcObjectDefinition`, so a selected space passes. **No whitelist, no spatial-element
exclusion.** The panel shows the system name, `Identification` (or `ItemReference` on
IFC2X3), `Name`, and an opener for the `Location` URI — the only consumer in this note
that surfaces `Location` at all. (The write API's docstring confirms the intended breadth:
*"References can be added to almost any object in IFC…"*.)

**Spaces are in the query universe by default.** `selector.py`'s `add_default_elements`
seeds `by_type("IfcProduct")` + `by_type("IfcTypeProduct")`. `IfcSpace` is an
`IfcProduct`, so a bare `classification=…` returns spaces without being asked to. The
official [selector syntax docs](https://docs.ifcopenshell.org/ifcopenshell-python/selector_syntax.html)
document `classification{{=}}{{value}}` and give the Uniclass example
`IfcElement, classification=/Pr_.*/`.

**It is in the GUI, not just the API.** `src/bonsai/bonsai/bim/module/search/prop.py`
lists `classification` as a search facet, and `operator.py:343`'s
`get_classification_suggestions()` autocompletes from every
`IfcClassificationReference` in the file.

**It reaches a spreadsheet with grouping and totals.** `IfcCsv` routes both row selection
and every column through the selector, so this is a shipped one-liner:

```
ifccsv --export -q "IfcSpace, classification=/SL_45.*/" \
       -a Name classification.Identification Qto_SpaceBaseQuantities.NetFloorArea
```

and `IfcCsv.export()` takes `groups=` / `summaries=` supporting `GROUP`, `CONCAT`, `SUM`,
`AVERAGE`, `MIN`, `MAX`. **Grouping spaces by Uniclass code and summing net floor area per
code is a supported operation with no custom code.** That is a real schedule, and it is
the workflow the whole question is about.

**And it reaches cost.** `src/ifc5d/ifc5d/csv2ifc.py:403,422` passes a BoQ row's `Query`
column straight to `filter_elements`, assigning matches to an `IfcCostItem` — so a cost
item can be priced against `IfcSpace, classification=SL_45_10_09` directly.

**Most importantly, it is machine-auditable.** `src/ifctester/ifctester/facet.py:394`
implements the IDS Classification facet, and its applicability filter is:

```python
def filter(self, ifc_file, elements):
    ...
    return ifc_file.by_type("IfcObjectDefinition")      # includes IfcSpace
```

It matches on both `value` (the `Identification`) and `system` (the `IfcClassification.Name`),
walks parent references so `SL_45_10_09` would satisfy an `SL_45` requirement, honours
`required`/`optional`/`prohibited`, and reports **`"The entity has no classification"`**.
The shipped `ids.xsd` allows `classification` under both `applicabilityType` and the
requirements block.

**So the IDS in §4.2 is not hypothetical — a runnable implementation of it exists in this
repo's own dependency tree.** That is the strongest single fact on the "read" side of the
ledger.

### 3.7 QTO / cost takeoff — classification is an *element* practice here too

Ten tools were examined. The pattern is consistent and it is not encouraging.

**Reads it, first-party confirmed:**

- **ACCA usBIM / PriMus IFC** — [accasoftware.com](https://www.accasoftware.com/en/5d-bim-software):
  *"PriMus IFC allows you to identify, within the IFC file, the classifications composition
  with which the project was formely made (**UniClass 2015, OmniClass, MasterFormat**, etc.)"*
  … *"it becomes easier to identify the entities to be accounted for in the quantity
  takeoff."* ⚠️ Documented as **entity selection** for takeoff, not a group-by cost
  dimension — and **nothing about `IfcSpace`**.
- **Allplan** — [help.allplan.com](https://help.allplan.com/Allplan/2026-1/1033/Allplan/95815.htm):
  *"IFC-format objects with classification attributes retain these attributes during IFC
  import."* Retention only; no grouping, pricing or space evidence.
- **That Open Engine** (web viewers) — reads it at the schema level, and the relation
  **survives IFC→Fragments conversion**
  (`ifc-relations-map.ts`: `IFCRELASSOCIATESCLASSIFICATION → { forRelating: "HasReferences", forRelated: "ClassificationRefForObjects" }`).
  ⚠️ Two traps if anyone builds on it: the object-side inverse is renamed
  **`ClassificationRefForObjects`**, not `HasAssociations`; and
  `IDSSpecifications/src/facets/Classification.ts` exists but `getEntities()` and `test()`
  are **entirely commented out**. `Classifier` ships `byCategory()`,
  `byIfcBuildingStorey()`, `byModel()` — **no `byClassification()`**.
- **BIMcollab Zoom** — [release notes](https://helpcenter.bimcollab.com/en/articles/326485-release-notes)
  build 9.4.7 (2025-05-06): *"Ability to check (IDS) whether any classification is set for
  a component and report which components are not compliant."* ⚠️ A **presence check**
  only. Its Smart Properties *derive* a classification from attributes rather than reading
  `IfcClassificationReference`. Group/filter by it: **could not confirm**.

**Does not:** **Autodesk Takeoff** — classification systems are **user-uploaded CSVs**
(*"click Import custom system to import and save the custom classification system to your
project"*), assigned manually to takeoff types. No documented path from
`IfcClassificationReference` into that field.

**Partial:** **Trimble Vico Office** — classification arrives only through the **live
Archicad publisher**, not generic IFC import (*"IFC Parameters (Available for Archicad
only) — In Archicad, you can also publish IFC attributes, IFC properties and IFC
Classifications into Vico Office"*). Plain `.ifc` import defaults to *"Default Takeoff
Items Grouping — IFC: Name"*. (Vico is EOL; sourced from archived vendor PDFs.)

**Could not confirm, several negative-leaning:** iTWO / Exactal **CostX** (its own IFC
chapter enumerates only Attributes, `Pset_` sets and Base Quantities; zero "classif" hits
in the 6.8 and 7.0 release notes; its UniFormat grouping arrives via **Revit→DWFx**, not
IFC), **Trimble Connect**, **Cubicost (Glodon)**, **Assemble Systems**, **Revizto** (help-centre
search API returns `"count": 0` for both `classification` and `IfcClassificationReference`
while control queries return hits), **Tekla Structures** (all classification pages are
export-direction).

**One assumption worth killing explicitly.** **Bexel Manager** was expected to be the
IFC-classification-native counter-example. It is not.
`help.bexelmanager.com/?s=IfcClassification` returns *"Sorry, but nothing matched your
search terms."* Its whole classification apparatus — Cost Classification, Custom Breakdown
Structure, the Data Enrichment Add-In — is **property-driven on its own schema**, with
codes injected from **Excel**: *"Custom Breakdown tool is used to classify elements based
on certain criteria, usually referring to specific **properties** of selected elements"*.
It is classification-*driven* and not classification-*reading*.

> **The summary line for this whole section: of ten QTO/cost tools, only Solibri and
> dRofus have first-party documentation tying classification to *spaces* at all — and
> §3.4 shows Solibri's is its own `.classification` resource, while §3.5 shows dRofus's is
> its own database field.**

⚠️ **A disagreement worth recording rather than smoothing over.** Two independent passes
over the same Solibri pages reached opposite conclusions — one read the shipped
`Spaces.ito` (*"usage defined by classification"*, *"based on the
`Space usage.classification`"*) as proof Solibri takes off spaces by IFC classification;
the other established that `Space usage` is a native Solibri `.classification` resource
built from **property sets**, per [*Creating a New Classification*](https://help.solibri.com/hc/en-us/articles/1500003953741-Creating-a-New-Classification)
(*"Select the property set … The list of available property sets depends on the IFC file
content"*). **The second reading is the correct one**, and the collision is itself the
finding: Solibri's documentation uses one word for three unrelated things (§3.4), and it
is very easy to come away believing this feature exists when what exists is a homonym.

---

## 4. Is it mandated anywhere?

Short answer: **once, in one place, and that place has since moved it off `IfcSpace`.**

### 4.1 IDS — the facet exists, the default is `required`, and it applies to spaces

buildingSMART's IDS 1.0 ships a **Classification facet**, and nothing restricts it by
entity. From the first-party user manual
([`Documentation/UserManual/classification-facet.md`](https://github.com/buildingSMART/IDS/blob/development/Documentation/UserManual/classification-facet.md)):

> "A **Classification System** is a defined hierarchy to categorise elements. Some
> popular classification systems include *Uniclass 2015*, *ETIM* and *CCI*. […]
> **Any object in IFC model can have a Classification Reference.**"

The XSD ([`Schema/ids.xsd`](https://raw.githubusercontent.com/buildingSMART/IDS/development/Schema/ids.xsd),
lines 151–165) gives `<ids:classification>` an optional `cardinality` attribute
`default="required"`. So an auditor **can** write "every `IfcSpace` must carry a Uniclass
SL code", and the check is one element of XML.

**So the checker leg of the doubt is answered: a standards-track checker language can
query this, and the query is trivial to write.**

### 4.2 …but no published IDS actually requires it. One first-party near-miss, and one deliberate exclusion

All 12 official sample IDS files were downloaded and grepped. Two contain both
`IFCSPACE` and `classification`, and neither *requires* it. The two results pull in
opposite directions and both matter.

**The near-miss — buildingSMART's own `IDS_SimpleBIM_examples.ids`:**

```xml
<ids:specification ifcVersion="IFC2X3 IFC4" name="Room requirement 1"
  description="the model must have rooms, every room must have a name from a list of
               allowed values, every room must have a (unique) room number">
  <ids:applicability maxOccurs="unbounded">
    <ids:entity><ids:name><ids:simpleValue>IFCSPACE</ids:simpleValue></ids:name></ids:entity>
    <ids:classification>
      <ids:value><ids:simpleValue>SL_45_10_09</ids:simpleValue></ids:value>
      <ids:system><ids:simpleValue>Uniclass</ids:simpleValue></ids:system>
    </ids:classification>
  </ids:applicability>
```

That is **applicability, not requirement** — it filters *to* rooms already classified.
But read what it presumes: buildingSMART's own published sample selects rooms by
**`SL_45_10_09`**, which is *Bedrooms* — the exact code, on the exact entity, in the
exact table this repo is considering.

**And that is the sharpest operational argument in this whole note.** An IDS written
this way, run against an export with no classification, **matches zero elements and
passes**. Not a failure — a *vacuous pass*. If a client ever hands over an IDS shaped
like buildingSMART's own sample, a silent export produces a green result that means
nothing. That is a worse failure mode than a red one, and it is the one argument here
that survives the "nobody reads it" verdict.

**The deliberate exclusion — `IDS_demo_BIM-basis-ILS.ids`**, the official demo of the
Dutch national ILS. Its classification spec is named `Classificatiesystematiek`
(*"Voorzie objecten altijd van een viercijferige NL-SfB code…"* — always give objects a
four-digit NL-SfB code) and it **enumerates its applicable entities explicitly**. The
enumeration runs `IFCSOLARDEVICE` → `IFCSPACEHEATER`, stepping straight over
`IFCSPACE`; the string `IFCSPACE` appears **nowhere in the file**. A national body wrote
out the list and left spaces off it.

Two further negatives worth recording: `IDS_oma_input.ids` has a dedicated `name="Space"`
specification containing **zero** classification facets; and `IDS_Aedes_example.ids` —
Aedes being the **Dutch housing-associations federation**, i.e. the residential body most
likely to want this — requires a classification on `IFCWINDOW` only.

### 4.3 COBie — the one real mandate, and COBie V3 moved it off `IfcSpace`

**COBie 2.4 / BS 1192-4:2014 — `Space.Category` is a Required field, populated from
Uniclass 2015 Table SL.** The clearest statement found is Graphisoft's
[*ARCHICAD 22 and COBie*](https://gsdownloads.graphisoft.com/cdn/ftp/techsupport/documentation/IFC/GRAPHISOFT%20ARCHICAD%2022%20and%20COBie.pdf)
guide (§3.4, p.34):

> "**COBie requires IfcSpace classification by the OmniClass table 13 called "Space by
> Function" (in the U.S.) or by the Uniclass 2015 system (in UK).**"

and its required-minimum list (§1.5, p.8):

> "The Lead Designer / Architect must provide the following **Required** data as a
> minimum to satisfy COBie: […] **Space — Name, CreatedBy, CreatedOn, Category and
> Description**"

⚠️ **This is the weakest link in the strongest finding.** It is a *software vendor's*
guide, not BSI. BS 1192-4:2014 is paywalled and its primary text was **not read**. Treat
"BS 1192-4 mandates it" as **vendor-attested**.

**COBie V3 (NBIMS-US, the current online text) moved the classification to
`IfcSpaceType`.** From [nibs.org/nbims/v3/cobie/4-3](https://nibs.org/nbims/v3/cobie/4-3/),
the SPACE table has **no `Category` field at all** — it has `SpaceType.Name`, a reference
into the SpaceType table. `Category` lives on SpaceType, marked *"If Specified"*:

> "**SpaceType.Category** … Typically, the values shown for this in the U.S. are those
> from **OmniClass Table 13**, while **Uniclass Table SL** is used in the U.K."

And the IFC binding, from [nibs.org/nbims/v3/cobie/6-2](https://nibs.org/nbims/v3/cobie/6-2/)
(IFC Table B) — note which rows do and do not appear:

> "**Category | IfcClassificationReference |** Company, Facility, Level, **SpaceType**,
> Zone, Type, System, Resource, Job, Event, Package, Document, Attribute, Coordinate, Risk"
>
> "**SpaceType.Name | IfcRelDefinedByType |** Space"

`Space` is **not** in the `Category → IfcClassificationReference` list. In COBie V3 the
Uniclass SL code belongs on an **`IfcSpaceType`**, reaching each occurrence through
`IfcRelDefinesByType`.

**This is the most architecturally consequential finding in the note, and it is not the
one the brief asked about.** The plan on the table — a reference on *every* `IfcSpace` —
matches COBie 2.4 and Archicad's exporter, and does **not** match the current spec's data
model. For a residential generator, where a plan contains many occurrences of the same
`bedroom_double`, the type-level route is also the better-normalised one: nineteen
occurrences of twelve types want twelve classified `IfcSpaceType`s, not nineteen
classified `IfcSpace`s. **If a classification ships, "on the occurrence or on the type"
should be decided deliberately, not inherited from the ticket's phrasing.**

### 4.4 National mandates — nothing requires it for spaces

| Source | Verdict |
|---|---|
| **NL — BIM basis ILS v2** | **MENTIONS BUT DOES NOT MANDATE** |
| **NO — Statsbygg BIM Manual 1.2.1** | **DOES NOT** |
| **UK — DfE / NHS / MoJ / Homes England** | **COULD NOT CONFIRM** |
| **FI — COBIM 2012 Series 3** | **COULD NOT CONFIRM** (paywalled) |
| **DE / DK / SG** | **COULD NOT CONFIRM** |

**Netherlands, BIM basis ILS v2** ([official EN infographic](https://www.digigo.nu/wp-content/uploads/2024/09/BIM-ILS_infographicA4_2024_EN.pdf))
has two relevant clauses, quoted complete:

> "**3.6 CLASSIFICATION SYSTEM** — Always assign objects a classification code, according
> to the latest published version used in the relevant country."
>
> "**4.1 SPACES** — Spaces are: volumes and areas, enclosed by real or theoretical
> boundaries, with a function in a construction. Create IfcSpace from spaces and name the
> function. To group spaces into zones, use IfcZone."

§3.6 says "objects" generically; **§4.1, the clause that actually governs spaces, requires
the entity, the function *name*, and zoning — and says nothing about classification.** The
ambiguity is settled by the national body's own machine-readable implementation, which
excludes `IFCSPACE` (§4.2). The Dutch page for §4.1 frames zone classification as strictly
optional: *"Indien je nog een stap verder wilt gaan, is het zelfs mogelijk om van de zones
een classificatie te maken."*

**Norway, Statsbygg BIM Manual 1.2.1** ([PDF](https://dok.statsbygg.no/wp-content/uploads/2020/06/statsbyggs-bim-manual-1-2-1_en_20131217.pdf)):
~20 `IfcSpace` requirement rows, all on `IfcSpace.Name` (space-function number),
`IfcSpace.LongName` (room name), `GrossFloorArea`, and `IfcZone`. **None require
`IfcRelAssociatesClassification`.** Where it says "classification" for spaces it means
naming conventions — *"the space names must accord with Statsbygg's permitted 'space
names'"* — and its Annex F is titled **"Classifications (Informative)"**, explicitly
non-normative. (2013 document, superseded by SIMBA, which was **not** verified.)

### 4.5 Residential handover — no such published requirement found

Searched and **not found**: any housing-association EIR, national housing programme, or
dwelling handover standard naming space classification. Aedes ILS 2.0 returned HTTP 403;
the UK Building Safety Act golden thread does not mandate BIM at all (secondary sources);
Homes England / NHBC surfaced nothing.

**If the case for shipping is "residential handover requires it", that case is not
supported by anything published that this pass could find.**

The one encouraging residential fact is about *fit*, not *obligation*: Uniclass
`SL_45_10` is well-populated for housing — Bedrooms, Domestic kitchens, Living rooms,
Kitchen-dining rooms, Kitchen-dining-living rooms, Utility rooms, Balconies (21 codes,
[uniclass.thenbs.com/taxon/sl_45_10](https://uniclass.thenbs.com/taxon/sl_45_10), v1.36,
July 2026 — as `docs/research/room-classification-standards.md` already established). The
vocabulary fits. That argues it is *correct*, not that it is *required*.

### 4.6 The MVD carries it, and does not ask for it

**IFC4 Reference View — MENTIONS BUT DOES NOT MANDATE.** From the
[RV1.2 schema view](https://standards.buildingsmart.org/MVD/RELEASE/IFC4/ADD2_TC1/RV1_2/HTML/schema/views/reference-view/index.htm):

> "typically include: physical elements with explicit geometry, properties, quantities,
> material, and classification […] **spatial elements (spaces, zones) with explicit
> geometry, properties**…"
>
> "**"Classification Association"; assignes a classification reference to one or several
> model elements.**"

`IfcSpace` is listed among RV spatial structure elements, and *Classification
Association* and *Project Classification Information* are both RV concepts. So an export
carrying this **will survive an RV round-trip** — ADR 0011's view choice does not block
it. But the RV is a capability scope, not a requirement, and it nowhere ties the two
together.

Independently confirmed from the pinned `ifcopenshell 0.8.5` schema: `IfcSpace` inherits
`HasAssociations` from `IfcObjectDefinition` in both IFC4 and IFC4X3_ADD2, so the
association is **schema-valid** in either target.

---

## 5. What competing floor-plan generators emit

Not re-derived — `docs/research/competitive-landscape.md` already establishes the set,
and this pass adds one query over it.

That note's §"IFC export" line gives the population: **ARCHITEChTURES ✅, Digital Blue
Foam ✅, Autodesk Forma ✅ (Beta 4.3)**, Snaptrude (claimed, undocumented), Planner 5D
(B2B API beta); **Finch ✗, Synaps ✗, TestFit ✗, Maket ✗, Cedreo ✗, RoomSketcher ✗.**
So at most five products in an eleven-product survey emit IFC at all.

**A grep across both research notes for `classif|uniclass|omniclass|cobie` returns one
hit, and it is not about spaces:** Qonic, listed as an adjacent platform doing "AI
auto-classification of IFC elements" — *elements*, and Qonic is recorded there as "Not a
generator". `docs/research/floorplan-generation-stack.md` (~20 generators) returns no
hits at all beyond two paper titles using "classification" in the graph-theory sense.

Even the most BIM-serious competitor is silent on it. ARCHITEChTURES — the only
credit-card-purchasable IFC-output product in the survey — describes its rooms as
objects "usually used as a starting point to generate take offs and estimates" and says
nothing about classifying them.

**Nobody in the competitive set documents classifying its exported spaces.** That is not
proof they don't; it is proof that none of them treats it as a feature worth naming, and
therefore that shipping it buys **no parity and no differentiation that a buyer is
already asking for**.

---

## 6. If it ships anyway, these are the mechanics — and they are not free

Three costs, each measured rather than estimated.

### 6.1 The attribute holding the code is **not stable across schema versions**

Read from the pinned `ifcopenshell 0.8.5` EXPRESS schemas:

| schema | `IfcClassificationReference` attributes | `IfcClassification` attributes |
|---|---|---|
| IFC2X3 | `Location`, **`ItemReference`**, `Name`, `ReferencedSource` | `Source`, `Edition`, `EditionDate`, `Name` — **no `Location`** |
| IFC4 | `Location`, **`Identification`**, `Name`, `ReferencedSource`, `Description`, `Sort` | … `Description`, **`Location`**, `ReferenceTokens` |
| IFC4X3_ADD2 | `Location`, **`Identification`**, `Name`, `ReferencedSource`, `Description`, `Sort` | … `Description`, **`Specification`**, `ReferenceTokens` |

Two renames on the path the engine would write: the code attribute is `ItemReference` in
IFC2X3 and `Identification` from IFC4; the dictionary URI attribute is `Location` in IFC4
and **`Specification`** in IFC4.3. buildingSMART's own bSDD→IFC mapping document
documents both forks explicitly, mapping the dictionary URI to
*"`IfcClassification.Specification` (IFC4x3_ADD2) or `IfcClassification.Location` (IFC4)"*
([bSDD-IFC documentation](https://github.com/buildingSMART/bSDD/blob/master/Documentation/bSDD-IFC%20documentation.md)).

This is a **second** version-pinning obligation on top of the Uniclass one the brief
already named, and it is the engine's own schema choice that triggers it.

### 6.2 The file cost, measured

19 spaces mapped onto 12 distinct Uniclass SL codes, built and written twice:

| | STEP instances | bytes |
|---|---|---|
| spaces only | 20 | 1,684 |
| **+ classification** | **46** | **3,624** |

**+26 instances: 1 `IfcClassification`, 12 `IfcClassificationReference`, 13
`IfcRelAssociatesClassification`.** (Thirteen, not twelve — `ifcopenshell.api.classification.add_classification`
also emits a rel binding the `IfcProject` to the classification system.) Three new entity
types on the spec surface and on gate 11's element-count checks.

### 6.3 The `Location` URI is real, resolvable — and marked `Preview`

Uniclass 2015 **is** published in the buildingSMART Data Dictionary, so the
`Location` attribute has a canonical value rather than an invented string. Queried
against `api.bsdd.buildingsmart.org`, every code the engine needs resolves:

| bSDD URI | code | name |
|---|---|---|
| `…/uri/nbs/uniclass2015/1/class/SL_45_10_09` | `SL_45_10_09` | Bedrooms |
| `…/uri/nbs/uniclass2015/1/class/SL_45_10_49` | `SL_45_10_49` | Living rooms |
| `…/uri/nbs/uniclass2015/1/class/SL_45_10_23` | `SL_45_10_23` | Domestic kitchens |

Full record for `SL_45_10_09`, verbatim from the API:

```
code: 'SL_45_10_09'   name: 'Bedrooms'   status: 'Preview'
hierarchy: SL Spaces/locations > SL_45 Residential spaces > SL_45_10 Living spaces
dictionaryUri: 'https://identifier.buildingsmart.org/uri/nbs/uniclass2015/1'
versionDateUtc: '0001-01-01T00:00:00Z'
```

Three cautions fall straight out of that record, and they sharpen the existing note's
warning that "Uniclass 2015" names a rolling family:

- **`status: 'Preview'`** — not `Active`. The bSDD publication is not a settled artefact.
- **`versionDateUtc` is epoch zero** and the dictionary version is the bare string
  `"1"`, not `v1.36`. So the bSDD URI **cannot express which Uniclass edition** is meant;
  the edition has to be carried separately in `IfcClassification.Edition`.
- **`relatedIfcEntityNames` is absent** — bSDD does not itself assert that `SL_45_10_09`
  applies to `IfcSpace`. The binding of a Uniclass space code to the `IfcSpace` entity is
  the engine's assertion, not the dictionary's.

**The shape to write, if it ships** (matching buildingSMART's own worked example):

```
#4=IFCCLASSIFICATION('NBS','<edition, e.g. v1.36>','<edition date>','Uniclass 2015',$,
     'https://identifier.buildingsmart.org/uri/nbs/uniclass2015/1',$);
#6=IFCCLASSIFICATIONREFERENCE(
     'https://identifier.buildingsmart.org/uri/nbs/uniclass2015/1/class/SL_45_10_09',
     'SL_45_10_09','Bedrooms',#4,$,$);
#7=IFCRELASSOCIATESCLASSIFICATION(<guid>,$,$,$,(<spaces>),#6);
```

One `IfcClassificationReference` **shared by every space with that code** — not one per
space. The scan in §2 is the argument for `Location` being populated: a bare code with no
URI is a string, and a string is what `Name` already is.

---

## 7. What could NOT be confirmed

The brief asked for this explicitly, and it is not a short list. Ranked by how much it
would change the verdict.

### 7.1 Would change the verdict if resolved

| # | Open question | What was tried |
|---|---|---|
| 1 | **Does Solibri actually read `IfcRelAssociatesClassification`, and where does it surface?** The single most-cited reason to emit this, and the least documented. | The whole Solibri Help Center via its Zendesk search API: **0 articles** for `IfcClassificationReference`, **0** for `IfcRelAssociatesClassification`. Read *The Info View*, *Info Settings*, *Adding a New Filter*, *Creating a New Classification*, *IFC Standards Supported by Solibri*, rules 36 / 183 / 203 / 231, the ITO tutorial and *IFC Model Requirements for Information Takeoff*. Only *"Solibri supports ifcClassification"*, unelaborated. Two user posts (**secondary**, no staff reply) say it appears but exposes only the Reference. **Needs an empirical test with a real file.** |
| 2 | **Does Solibri's rule #244 resolve the IDS Classification facet against `IfcRelAssociatesClassification`?** This is the whole "a checker queries it" leg for the commercial stack. | Solibri documents the facet (System + Value) and claims *"Official IDS v1.0"* support, but never names the IFC entity it resolves against. Inference from the IDS spec is strong but **is an inference**. |
| 3 | **Does the Navisworks 2025/2026 default `v4` (ATF) reader preserve `ClassificationCode`?** The `revit-ifc` codebase that provably carries it is scoped *"Navisworks (2019-2024)"*; v4 is documented as a different pipeline (Autodesk Translation Framework). | Read the first-party IFC file-reader options page; no statement either way. No ATF source is published. |
| 4 | **Which Navisworks Properties tab it lands on** — and therefore its `Category → Property` address in Find Items / Search Sets. | The `IElement` implementation is a stub in the open repo (`// NAVIS_TODO: This is inside Navis code.`). The Properties Window help does not enumerate IFC categories. |

### 7.2 Weakens a specific claim

| # | Open question | What was tried |
|---|---|---|
| 5 | **BS 1192-4:2014's own text** — the primary source for the *only* real mandate found (§4.3). | Paywalled at BSI. The requirement is **vendor-attested** via Graphisoft's COBie guide, which cites BS 1192-4 and the COBie Responsibility Matrix v17. **This is the weakest link in the strongest finding.** |
| 6 | **Whether Archicad applies the Zone Name/Number ↔ `LongName`/`Name` mapping on *import*.** | The predefined mapping table is titled *"Export to IFC"*. All AC29 IFC help pages 1–52 were fetched and grepped; the import pages (121_IFC-5/6/7/8/25) contain zero occurrences of "zone"/"space". AC28 and AC24 checked too. Symmetry is plausible but undocumented. |
| 7 | **Whether an incoming `IfcClassificationReference` survives plain Open / Merge / Hotlink** in Archicad, as opposed to *Update with IFC Model* where it is explicit. | 121_IFC-5/-6/-7/-8 read in full; none mentions classification. The criteria dialog's *"Classification References folder"* implies survival but does not state it. |
| 8 | **First-party confirmation that a linked model's shared parameter must exist in the host with a matching GUID** to be scheduled/filtered in Revit. | Closest first-party wording is *"All fields that are available for elements in the host project are available for elements in linked models"* — implies, does not state. The GUID rule rests on **secondary** sources (IMAGINiT blog, Autodesk Community). |
| 9 | **Two Autodesk support articles** — *"Rooms and space are imported as Generic Models linking IFC to Revit"* and *"IFC Uniformat Classification code missing when using Revit_IFC loader"*. | Both 403 to WebFetch and to curl with a browser UA (bot protection). Content came from search-engine summaries of first-party pages — **one notch below** the pages actually fetched. The DirectShape claim does not depend on them (it is proved from source); the Navisworks-regression claim does. |

### 7.3 Not reached

| # | Open question | What was tried |
|---|---|---|
| 10 | A **published IDS that *requires*** classification on `IfcSpace`. | All 12 official buildingSMART sample IDS files downloaded and grepped, plus web search for national IDS libraries. **None found.** The near-miss (§4.2) uses it as *applicability*. |
| 11 | **Finland COBIM 2012 Series 3**; **Statsbygg SIMBA** (which supersedes the 2013 manual); **BIM Deutschland**; **Danish ICT executive order / Molio**; **Singapore IFC-SG** Excel mapping file. | COBIM paywalled at Rakennustieto; SIMBA located at ucm.buildingsmart.org but not fetched; the others returned nothing concrete. |
| 12 | **UK DfE / NHS / MoJ EIRs and Homes England / NHBC** housing requirements. | Searched; only NBS publication-index stubs and unrelated university EIRs. **Aedes ILS 2.0** (Dutch housing associations) returned HTTP 403. |
| 13 | **bSI certification test cases** — whether any exercises classification. | `technical.buildingsmart.org/standards/ifc/mvd/mvd-database/` returned 403. Partially compensated by §2.2: the certification *dataset* was downloaded and does not classify its spaces. |
| 14 | **No behavioural/runtime verification of Revit, Navisworks, Archicad or Solibri.** No instance of any of the four was run. | Everything in §3.1–§3.4 is source reading plus vendor documentation. The executable evidence in this note (§1, §2, §6) is confined to `ifcopenshell` and to parsing real files. |
| 15 | **Seven QTO/cost tools** — iTWO/Exactal **CostX**, **Trimble Connect**, **Cubicost (Glodon)**, **Assemble Systems**, **Revizto**, **Tekla Structures**, **Bexel Manager**. | Each vendor's own docs searched; several are negative-leaning rather than silent (§3.7). Blockers: CostX and Cubicost documentation omits the topic entirely; Trimble Connect's Object Manager manuals sit behind a Google login; Assemble's docs 403 via Akamai; Revizto's help-centre search API returns `count: 0` while control queries return hits; Bexel's handbook PDF resisted text extraction. |
| 16 | **Whether BIMcollab Zoom can *group or filter* by a classification** (as opposed to IDS presence-checking it). | Read the release notes and the IDS article. Lists filters are documented as Element type + Property/Operator/Value; classification is not named. |

### 7.4 A limitation of the corpus, stated plainly

The six models in §2 span 2011–2024 and four authoring tools, and include buildingSMART's
own current certification set — but four of the six are IFC2X3 files from 2011. **A larger
and more modern corpus would make §2 stronger.** A search for additional published IFC4
models of real buildings with spaces did not turn up a better set than this one; the
buildingSMART IFC4 sample directory contains NURBS geometry tests, not buildings.
Treat §2 as strong evidence of a durable industry habit, not as a census.

---

## 8. Reproducing §1, §2 and §6

All of it runs against the repo's own `venv` (`ifcopenshell 0.8.5`) plus `curl`.

**§1 — the round-trip and the selector queries.**

```python
import ifcopenshell, ifcopenshell.api.root, ifcopenshell.api.classification
import ifcopenshell.util.selector as sel, ifcopenshell.util.classification as uc
f = ifcopenshell.file(schema="IFC4")
ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="P")
s1 = ifcopenshell.api.root.create_entity(f, ifc_class="IfcSpace", name="bedroom_double")
s2 = ifcopenshell.api.root.create_entity(f, ifc_class="IfcSpace", name="kitchen")
sys = ifcopenshell.api.classification.add_classification(f, classification="Uniclass 2015")
ifcopenshell.api.classification.add_reference(
    f, products=[s1], identification="SL_45_10_09", name="Bedrooms", classification=sys)
sel.filter_elements(f, 'IfcSpace, classification="SL_45_10_09"')   # -> {s1}
sel.filter_elements(f, 'IfcSpace, classification=NULL')            # -> {s2}
sel.get_element_value(s1, "classification.Identification")         # -> ['SL_45_10_09']
```

**§2 — the corpus.** The sample files are Git-LFS, so `raw.githubusercontent.com` returns
a 132-byte pointer; use the `media.` host.

```bash
B=https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main
curl -sL -o schep.ifc "$B/IFC%202.3.0.1%20(IFC%202x3)/Schependomlaan/Design%20model%20IFC/IFC%20Schependomlaan.ifc"
curl -sL -o duplex.ifc "$B/IFC%202.3.0.1%20(IFC%202x3)/Duplex%20Apartment/Duplex_A_20110907.ifc"
curl -sL -o clinic.ifc "$B/IFC%202.3.0.1%20(IFC%202x3)/Medical-Dental%20Clinic/Clinic_Architectural.ifc"
# the certification scenes are NOT LFS - plain raw host, different repo:
C=https://raw.githubusercontent.com/buildingSMART/Certification-datasets/main
curl -sL -o cert4.ifc   "$C/IFC%204.0.2.1%20(IFC%204)/PCERT-Sample-Scene/Building-Architecture.ifc"
curl -sL -o cert43.ifc  "$C/IFC%204.3.2.0%20(IFC4X3_ADD2)/PCERT-Sample-Scene/Building-Architecture.ifc"
```

```python
import ifcopenshell, ifcopenshell.util.classification as uc
f = ifcopenshell.open("schep.ifc")
sp = f.by_type("IfcSpace")
print(len(sp), len([s for s in sp if uc.get_references(s)]))     # -> 100 0
print(f.header.file_description.description)                     # the Archicad option list
```

**§6.3 — bSDD.**

```bash
curl -s "https://api.bsdd.buildingsmart.org/api/Dictionary/v1?SearchText=Uniclass"
curl -s "https://api.bsdd.buildingsmart.org/api/Class/v1?Uri=https%3A%2F%2Fidentifier.buildingsmart.org%2Furi%2Fnbs%2Funiclass2015%2F1%2Fclass%2FSL_45_10_09"
```

---

## 9. Sources

Graded. **Executable** = run or parsed locally in this pass. **First-party** = the vendor
or standards body that owns the behaviour. **Second-party** = another vendor describing a
competitor. **Secondary** = anything else.

### Executable / parsed locally

| # | Source | Used for |
|---|---|---|
| 1 | `ifcopenshell 0.8.5` in this repo's `venv` — `util/selector.py`, `util/classification.py`, `api/classification/`, and the IFC2X3 / IFC4 / IFC4X3_ADD2 EXPRESS schemas | §1, §6.1, §6.2, §4.6 |
| 2 | `Duplex_A_20110907.ifc`, `Duplex_M_20111024_ROOMS_AND_SPACES.ifc`, `Clinic_Architectural.ifc`, `IFC Schependomlaan.ifc` — [buildingsmart-community/Community-Sample-Test-Files](https://github.com/buildingsmart-community/Community-Sample-Test-Files) (Git-LFS; use the `media.` host) | §2 |
| 3 | `PCERT-Sample-Scene/Building-Architecture.ifc`, IFC4 and IFC4X3_ADD2 — [buildingSMART/Certification-datasets](https://github.com/buildingSMART/Certification-datasets) | §2.2 |
| 4 | `api.bsdd.buildingsmart.org` — `Dictionary/v1` and `Class/v1` | §6.3 |

### First-party — vendor source code

| # | Source | Used for |
|---|---|---|
| 5 | [Autodesk/revit-ifc](https://github.com/Autodesk/revit-ifc) @ `e80e3d372f06d7fb704e250c7676e58e566b04e8`, branches `Release_19.x.x`–`Release_27.x.x` — `IFCObjectDefinition.cs`, `ParametersToSet.cs`, `IFCCategoryUtil.cs`, `IFCImportCache.cs`, `IFCSpace.cs`, `IFCNavisProcessor.cs`, `ClassificationUtil.cs`, `IFCSharedParameters.cs` | §3.1, §3.2 |
| 6 | [Autodesk/revit-ifc issue #15](https://github.com/Autodesk/revit-ifc/issues/15) — "Link IFC does not create Room/Space from IfcSpace", open since 2018 | §3.1 |
| 7 | [IfcOpenShell/IfcOpenShell](https://github.com/IfcOpenShell/IfcOpenShell) — `bonsai/bim/module/classification/ui.py`, `bonsai/bim/module/search/{prop,operator}.py`, `ifccsv/ifccsv.py`, `ifc5d/csv2ifc.py`, `ifctester/facet.py:394`, `ifctester/ids.xsd` | §3.6 |
| 8 | [That Open Engine](https://github.com/ThatOpen) — `engine_web-ifc/src/ts/ifc-schema.ts`, `engine_fragment/.../ifc-relations-map.ts`, `engine_components/.../facets/Classification.ts` | §3.7 |

### First-party — vendor and standards-body documentation

| # | Source | Used for |
|---|---|---|
| 9 | Graphisoft AC29 Product Help, IFC chapter — [Import IFC Model](https://help.graphisoft.com/AC/29/INT/_AC29_Help/121_IFC/121_IFC-5.htm) · [Type Mapping for Import](https://help.graphisoft.com/AC/29/INT/_AC29_Help/121_IFC/121_IFC-26.htm) · [Update with IFC Model](https://help.graphisoft.com/AC/29/INT/_AC29_Help/121_IFC/121_IFC-9.htm) · [Element Criteria using IFC Data](https://help.graphisoft.com/AC/29/INT/_AC29_Help/121_IFC/121_IFC-22.htm) · [Property Mapping for Import](https://help.graphisoft.com/AC/29/INT/_AC29_Help/121_IFC/121_IFC-27.htm) · [Predefined Property Mapping](https://help.graphisoft.com/AC/29/INT/_AC29_Help/121_IFC/121_IFC-50.htm) · [Create New Classification Reference](https://help.graphisoft.com/AC/29/INT/_AC29_Help/121_IFC/121_IFC-16.htm) | §3.3 |
| 10 | Graphisoft AC24 Help, [Data Conversion for IFC Export](https://help.graphisoft.com/AC/24/INT/_AC24_Help/115_IFC/115_IFC-41.htm) — *"Export the Zone Categories data (Code and Name) of ARCHICAD Zones as IFC Space Classification Reference data (ItemReference and Name)"* | §2.1 |
| 11 | Solibri Help Center (fetched via its Zendesk API) — [Understanding Classifications](https://help.solibri.com/hc/en-us/articles/1500004070762-Understanding-Classifications) · [The Info View](https://help.solibri.com/hc/en-us/articles/21701046739607-The-Info-View) · [Creating a New Classification](https://help.solibri.com/hc/en-us/articles/1500003953741-Creating-a-New-Classification) · [244 IDS Validation](https://help.solibri.com/hc/en-us/articles/19053798036375-244-IDS-Validation) · [Creating an IDS File](https://help.solibri.com/hc/en-us/articles/39702217779223-Creating-an-IDS-File) · [36 Space Requirements](https://help.solibri.com/hc/en-us/articles/1500004611001-36-Space-Requirements) · [183 Program Reconciliation](https://help.solibri.com/hc/en-us/articles/29367732933143-183-Program-Reconciliation) · [IFC Standards Supported](https://help.solibri.com/hc/en-us/articles/23779405208855-IFC-Standards-Supported-by-Solibri) · [ITO model requirements](https://help.solibri.com/hc/en-us/articles/4901566051095-IFC-Model-Requirements-for-Information-Takeoff) | §3.4 |
| 12 | Autodesk Help — [Navisworks IFC file reader options](https://help.autodesk.com/cloudhelp/2026/ENU/Navisworks/files/GUID-E1CD4663-D460-4EA5-ABEC-FD24885BA3A6.htm) · [Properties Window](https://help.autodesk.com/cloudhelp/2026/ENU/Navisworks/files/GUID-DE27B147-B234-4AFE-8E2C-ACA82120A253.htm) · [Linked Models in Schedules](https://help.autodesk.com/cloudhelp/2026/ENU/Revit-Collaborate/files/GUID-0CD60F7E-D18F-4444-A20F-5408CA1163AF.htm) · [IFC Export Setup Options](https://help.autodesk.com/cloudhelp/2026/ENU/Revit-DocumentPresent/files/GUID-E029E3AD-1639-4446-A935-C9796BC34C95.htm) | §3.1, §3.2 |
| 13 | buildingSMART — [IDS Classification facet manual](https://github.com/buildingSMART/IDS/blob/development/Documentation/UserManual/classification-facet.md) · [`Schema/ids.xsd`](https://raw.githubusercontent.com/buildingSMART/IDS/development/Schema/ids.xsd) · the 12 official sample `.ids` files · [bSDD-IFC mapping](https://github.com/buildingSMART/bSDD/blob/master/Documentation/bSDD-IFC%20documentation.md) · [IFC4 RV1.2 schema view](https://standards.buildingsmart.org/MVD/RELEASE/IFC4/ADD2_TC1/RV1_2/HTML/schema/views/reference-view/index.htm) | §4.1, §4.2, §4.6, §6.1, §6.3 |
| 14 | NBIMS-US COBie V3 — [§4.3 Data Fields](https://nibs.org/nbims/v3/cobie/4-3/) · [§6.2 IFC mapping](https://nibs.org/nbims/v3/cobie/6-2/) | §4.3 |
| 15 | [BIM basis ILS v2, official EN infographic](https://www.digigo.nu/wp-content/uploads/2024/09/BIM-ILS_infographicA4_2024_EN.pdf) and [§4.1 Ruimten](https://www.digigo.nu/ilsen-en-richtlijnen/bim-basis-ils/4-1-ruimten/) | §4.4 |
| 16 | [Statsbygg BIM Manual 1.2.1](https://dok.statsbygg.no/wp-content/uploads/2020/06/statsbyggs-bim-manual-1-2-1_en_20131217.pdf) | §4.4 |
| 17 | [IfcOpenShell selector syntax docs](https://docs.ifcopenshell.org/ifcopenshell-python/selector_syntax.html) | §3.6 |
| 18 | [Uniclass 2015 SL_45_10](https://uniclass.thenbs.com/taxon/sl_45_10) (v1.36, July 2026) | §4.5 |
| 19 | Allplan [IFC import](https://help.allplan.com/Allplan/2026-1/1033/Allplan/95815.htm) · [ACCA 5D BIM](https://www.accasoftware.com/en/5d-bim-software) · [BIMcollab Zoom release notes](https://helpcenter.bimcollab.com/en/articles/326485-release-notes) · [Autodesk Takeoff settings](https://help.autodesk.com/cloudhelp/ENU/Takeoff-GS/files/Configure_Takeoff_Settings.html) | §3.7 |

### Second-party

| # | Source | Used for |
|---|---|---|
| 20 | dRofus Help — [Export Room Groups as Classification](https://help.drofus.com/en/English/Learning/groups-in-ifc) · [Room Classifications](https://help.drofus.com/en/English/Learning/room-classifications) · [Export IFC](https://help.drofus.com/en/English/Learning/export-ifc) · [Terminology](https://help.drofus.com/en/English/Learning/terminology) — dRofus asserting that **Solibri** reads IFC classifications | §3.5 |
| 21 | [Graphisoft, *ARCHICAD 22 and COBie*](https://gsdownloads.graphisoft.com/cdn/ftp/techsupport/documentation/IFC/GRAPHISOFT%20ARCHICAD%2022%20and%20COBie.pdf) — a vendor stating BS 1192-4's requirement. **The only evidence for the strongest mandate found, and BSI's own text was not read.** | §4.3 |

### Secondary — flagged in place, never load-bearing alone

| # | Source | Used for |
|---|---|---|
| 22 | Two Autodesk support articles reachable only via search summary (both 403 to automated fetch): *"Rooms and space are imported as Generic Models linking IFC to Revit"*; *"IFC Uniformat Classification code missing when using Revit_IFC loader"* | §3.1, §3.2 |
| 23 | `society.solibri.com` user threads [3226](https://society.solibri.com/topic/3226/classifcation-from-ifc) and [2057](https://society.solibri.com/topic/2057/ifc-classification-in-solibri) — users, not Solibri staff, no staff reply | §3.4 |
| 24 | IMAGINiT / Autodesk Community posts on shared-parameter GUID matching across links | §3.1 |

### Repo notes cited, not re-derived

- `docs/research/room-classification-standards.md` — IFC carries no room-use vocabulary;
  `IfcRelAssociatesClassification` is the socket; Uniclass `SL_45_10` is the candidate;
  "Uniclass 2015" names a rolling family.
- `docs/research/competitive-landscape.md` — the IFC-emitting competitor set (§5).
- `docs/research/floorplan-generation-stack.md` — the ~20-generator survey (§5).
- `docs/spec/ifc-export.md` §6 — the `Name` / `LongName` split this note repeatedly finds
  vendors independently expecting.
- `docs/wayfinder/tickets/84-an-ifcspace-carries-no-room-use.md` — the question this
  answers.
