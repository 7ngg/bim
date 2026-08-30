# Room classification — does a standard already name what `zone_class` would name

**Research date:** 2026-08-31
**Question:** we are about to invent a private `zone_class` over 19 residential room
types with values ≈ `{sleeping, social, kitchen, wet, circulation, service}`, plus a
boolean `is_sleeping`. Does an established standard already publish this, and should
we align to it instead?
**Method:** primary sources where reachable. The IFC answers are read **out of the
EXPRESS schema itself**, as shipped in the project's own `ifcopenshell 0.8.5` — not
from a website about the schema. The SP 54.13330.2022 and OmniClass answers are read
out of the **published PDFs**, extracted locally with the project's own `pymupdf`.
Where a source was paywalled, 403, or served an expired certificate, that is said in
place and the claim is marked **COULD NOT CONFIRM** rather than guessed. Reproduction
transcript in §7.

**Budgeted pass.** 24 tool calls, no sub-agents. Three question areas came back thin
and are flagged as such rather than padded: OmniClass entry-level codes, SIA 416, and
the non-RPLAN datasets.

---

## 0. Headline

**The suspicion in the brief is correct, and it is worse than suspected.**
`IfcSpaceTypeEnum` in IFC4 is exactly `SPACE, PARKING, GFA, INTERNAL, EXTERNAL,
USERDEFINED, NOTDEFINED`; IFC4.3 adds one value and it is `BERTH` (a mooring). There
is **no room-use semantics anywhere in the entity, and none in `Pset_SpaceCommon`**.
The one property that comes close, `Pset_SpaceOccupancyRequirements.OccupancyType`, is
an `IfcLabel` — a free string — whose own definition defers to "the presiding national
building code". IFC ships a **socket, not a vocabulary**: `IfcRelAssociatesClassification`.

But the question conflates two different objects, and they have different answers:

| object | is there a standard? | verdict |
|---|---|---|
| the **19 leaf room types** (bedroom, living, kitchen, …) | **yes** — Uniclass SL_45_10 publishes 21 residential entries at exactly this granularity | do not adopt as our internal key; **map onto it for export** |
| the **grouping** into classes (`sleeping/social/wet/…`) | **yes, and it is statutory for our region** — SP 54.13330 partitions a dwelling into *жилые комнаты* vs *помещения вспомогательного использования*, and its own arithmetic depends on the partition | **do not invent a rival partition**; carry this one |

The single strongest alternative to inventing our own leaf vocabulary is **Uniclass
2015 table SL, group `SL_45_10` "Living spaces"**. The single strongest constraint on
the grouping is **SP 54.13330's two-class split**, which is not optional for us
because rules we already cite are written over it.

---

## 1. IFC — confirmed: `IfcSpaceTypeEnum` carries no room-use semantics

### 1.1 The enumeration, read from the schema

Read with `ifcopenshell.ifcopenshell_wrapper.schema_by_name(<s>).declaration_by_name("IfcSpaceTypeEnum").enumeration_items()`,
`ifcopenshell 0.8.5`:

| schema | `IfcSpaceTypeEnum` values, in schema order |
|---|---|
| **IFC2X3** | `USERDEFINED, NOTDEFINED` |
| **IFC4** | `SPACE, PARKING, GFA, INTERNAL, EXTERNAL, USERDEFINED, NOTDEFINED` |
| **IFC4X3** | `BERTH, EXTERNAL, GFA, INTERNAL, PARKING, SPACE, USERDEFINED, NOTDEFINED` |
| **IFC4X3_ADD2** | identical to IFC4X3 |

**The brief's guess was exactly right.** IFC4 has five real values and two escapes.
Reading them for what they are: `SPACE` is "a space, unspecified"; `PARKING` is a car
park; `GFA` is a *measurement* construct (gross floor area), not a room at all;
`INTERNAL`/`EXTERNAL` is inside-vs-outside. The **only** value IFC4.3 adds in a decade
of revisions is `BERTH` — a ship mooring, arriving with the infrastructure extension.
Nothing in the enumeration has ever distinguished a bedroom from a bathroom, and
nobody has proposed that it should.

> ⚠️ Note this cuts the other way too: `PredefinedType='SPACE'` is not a
> deficiency in our exporter, it is the **only correct value** for every habitable room
> we will ever emit. `bim-cad-export-stack.md` §… already writes
> `IfcSpace (PredefinedType='SPACE', LongName='Living Room')`, and that is the
> conforming shape.

### 1.2 Where the room name actually lives, per the schema

`IfcSpace` attributes (IFC4, from the schema):

```
GlobalId, OwnerHistory, Name (IfcLabel), Description (IfcText), ObjectType (IfcLabel),
ObjectPlacement, Representation, LongName (IfcLabel),
CompositionType (IfcElementCompositionEnum), PredefinedType (IfcSpaceTypeEnum),
ElevationWithFlooring
```

Every field that could carry "Bedroom" — `Name`, `Description`, `ObjectType`,
`LongName` — is an unconstrained string. There is no typed slot for room use.

### 1.3 The property sets, read from the shipped IFC4 Pset templates

`ifcopenshell.util.pset.PsetQto("IFC4")`:

**`Pset_SpaceCommon`** (ApplicableEntity `IfcSpace`) — six properties:
`Reference`, `IsExternal`, `GrossPlannedArea`, `NetPlannedArea`, `PubliclyAccessible`,
`HandicapAccessible`. **None is a room-use classification**, and the spec says so
outright in `Reference`'s own definition:

> "Reference ID for this specified type in this project (e.g. type 'A-1'). Used to
> store the **non-classification driven** internal project type."

i.e. the standard explicitly tells you that classification does *not* live in this Pset.

**`Pset_SpaceOccupancyRequirements`** (ApplicableEntity `IfcSpace, IfcSpatialZone,
IfcZone`) — `OccupancyType`, `OccupancyNumber`, `OccupancyNumberPeak`,
`OccupancyTimePerDay`, `AreaPerOccupant`, `MinimumHeadroom`, `IsOutlookDesirable`.
`OccupancyType` is the closest thing IFC has to our field, and it is:

> `OccupancyType | IfcLabel | "Occupancy type for this object. It is defined according
> to the presiding national building code."`

**A free-text label, with the vocabulary explicitly delegated to national code.** It is
not an enumeration and there is nothing to align to. (It is also an *occupancy*
concept in the fire/egress sense — "the presiding national building code" means
IBC-style occupancy groups, not "this is a bedroom".)

**`Pset_SpaceFireSafetyRequirements`** likewise carries `FireRiskFactor` (`IfcLabel`,
"according to local building regulations") — same pattern, same delegation.

### 1.4 The mechanism IFC *does* provide

`IfcRelAssociatesClassification`, from the schema:

```
IfcRelAssociatesClassification: GlobalId, OwnerHistory, Name, Description,
  RelatedObjects : SET[1:?] OF IfcDefinitionSelect,
  RelatingClassification : IfcClassificationSelect (IfcClassification | IfcClassificationReference)

IfcClassificationReference: Location (IfcURIReference), Identification (IfcIdentifier),
  Name (IfcLabel), ReferencedSource, Description, Sort
```

**This is the answer to "is there ANY standard IFC mechanism".** Yes: attach an
external classification reference. IFC deliberately holds no room-use vocabulary of
its own and expects you to name one (Uniclass, OmniClass, a national table) with a
code, a name and a URI. Our `zone_class` has a conforming export path the day we
decide what it maps to.

### 1.5 Zones are not room-use either

`IfcZone` has no `PredefinedType` at all (`GlobalId, OwnerHistory, Name, Description,
ObjectType, LongName`). `IfcSpatialZone.PredefinedType` is `IfcSpatialZoneTypeEnum`:
IFC4 `CONSTRUCTION, FIRESAFETY, LIGHTING, OCCUPANCY, SECURITY, THERMAL, TRANSPORT,
VENTILATION, USERDEFINED, NOTDEFINED`; IFC4.3 adds `INTERFERENCE, RESERVATION`. These
are **engineering-system zones** — a thermal zone, a fire compartment — not day/night
or served/servant groupings. `IfcOccupantTypeEnum` is about tenure
(`ASSIGNEE, ASSIGNOR, LESSEE, LESSOR, LETTINGAGENT, OWNER, TENANT, …`), not room use.

**Confirmed, not refuted: IFC has no room-use type system.**

> ⚠️ **Source caveat.** `standards.buildingsmart.org` returned **HTTP 403** and
> `ifc43-docs.standards.buildingsmart.org` served an **expired TLS certificate** during
> this pass, so the human-readable spec pages were not read. Everything in §1 comes
> from the EXPRESS schema and Pset templates **shipped inside `ifcopenshell 0.8.5`**,
> which is the artefact our exporter actually consumes — arguably the better source, but
> it is a different one, and the prose definitions quoted above are the Pset template
> `Description` fields, not the website's narrative text.

---

## 2. Classification systems — Uniclass has it, at finer granularity than we want

### 2.1 ISO 12006-2 is a framework that *names the table*, not a vocabulary

NBIMS-US V3 §2.4.4.3 cites `ISO 12006-2:2001, Organization of Information about
Construction Works — Part 2: Framework for Classification of Information` as a
normative reference for OmniClass Table 13, and its bibliography item 7 is:

> "ISO 12006-2, **Table 4.5 Spaces (by function or user activity)**; Geneva: ISO, 2001"

So ISO 12006-2 publishes the *class* — "spaces, by function or user activity" — and
national systems populate it. That is the standard's whole design: it is the reason
Uniclass SL and OmniClass 13 exist and are parallel.

> **COULD NOT CONFIRM:** `iso.org/standard/61753.html` (the 2015 edition) returned
> **HTTP 403**. The table-4.5 title above is quoted from the NBIMS-US document citing
> ISO 12006-2:**2001**; whether the 2015 revision renumbers or renames it was not read.
> The standard is paywalled and was not purchased.

### 2.2 Uniclass — `SL_45_10 Living spaces`, and it is *finer* than our 19 types

Read from `uniclass.thenbs.com/taxon/sl_45_10`. Parent group: **`SL_45 Residential
spaces`**. Entries under `SL_45_10 Living spaces`, verbatim:

| code | title | | code | title |
|---|---|---|---|---|
| `SL_45_10_06` | Balconies | | `SL_45_10_45` | Kitchen-dining-living rooms |
| `SL_45_10_08` | Bedroom-studies | | `SL_45_10_49` | **Living rooms** |
| `SL_45_10_09` | **Bedrooms** | | `SL_45_10_57` | Nursing home bedrooms |
| `SL_45_10_12` | Caravan pitches | | `SL_45_10_60` | Panic rooms |
| `SL_45_10_14` | Communal living rooms | | `SL_45_10_78` | Single-occupancy bedrooms |
| `SL_45_10_16` | Concierge offices | | `SL_45_10_85` | Studies |
| `SL_45_10_18` | Conservatories | | `SL_45_10_88` | Tent pitches |
| `SL_45_10_22` | Domestic dining rooms | | `SL_45_10_93` | Utility rooms |
| `SL_45_10_23` | **Domestic kitchens** | | `SL_45_10_94` | Verandas |
| `SL_45_10_24` | Dormitories | | | |
| `SL_45_10_37` | Hotel rooms | | | |
| `SL_45_10_44` | **Kitchen-dining rooms** | | | |

**This answers the brief's question with a yes.** Uniclass publishes a residential
room-use vocabulary at bedroom / living / kitchen granularity, with stable codes, and
it even carries `Kitchen-dining rooms` and `Kitchen-dining-living rooms` as separate
entries — which is precisely the distinction `az-kitchen-diner-whole-room.md` spent a
document on. Bathrooms and WCs are **not** in `SL_45_10` (they live elsewhere in the SL
table, presumably under sanitary spaces); **that sub-tree was not read** — see §6.

> ⚠️ **Version.** The page states this is **"Spaces/locations v1.36, July 2026"**.
> "Uniclass 2015" is a **brand name on a rolling scheme**, not a frozen 2015 snapshot;
> codes are added and revised continuously. Anything we pin must record the version, or
> it will silently drift.

### 2.3 OmniClass Table 13 — confirmed to exist and to be the same class, entries not read

From the NBIMS-US V3 §2.4.4.3 PDF (National Institute of Building Sciences,
buildingSMART alliance, ©2015), which incorporates the table by reference:

> "**OmniClass™ Table 13 – Spaces by Function, May 2011.** … Table 13 – Spaces by
> function provides a **hierarchical taxonomy for classifying and identifying spaces by
> function**."
>
> "**spaces by function**: basic units of the built environment delineated by physical
> or abstract boundaries **characterized by function or primary use**"

Its bibliography also cites `Uniclass: … Table F, Spaces; RIBA Publications, 1997` —
i.e. OmniClass 13 and Uniclass SL are acknowledged siblings, both instantiating
ISO 12006-2 table 4.5.

> **COULD NOT CONFIRM:** the actual residential entry numbers. The NIBS file is a
> **2-page reference-standard wrapper** (4 321 characters); the table itself is a
> separate CSI-copyrighted document that was not retrieved in this pass. **No OmniClass
> code for "bedroom" is asserted here**, and none should be copied out of this document
> until the real table is read.

---

## 3. Area / room standards — and the one that actually binds us

### 3.1 SP 54.13330.2022 — the partition is real, named, and load-bearing

Read verbatim from the published PDF of **СП 54.13330.2022 «СНиП 31-01-2003 Здания
жилые многоквартирные»**. This is the standard `az-region-profile` already records as
AzDTN's ancestor, and it is already cited across `housing-quality-standards-as-bars.md`
and `az-region-profile/_sources_canon.json`.

**The two classes exist and they are named.** The definition clause (the one
immediately preceding `3.1.28 помещение встроенно-пристроенное`, therefore **3.1.27**)
enumerates the auxiliary class:

> «…коммуникационных, санитарных, технических и хозяйственно-бытовых нужд, **в том
> числе: кухня (или кухня-столовая), передняя, внутриквартирные холл и коридор, ванная
> комната или душевая, уборная, туалет или совмещенный санузел, кладовая, постирочная,
> помещение теплогенераторной и т.п.**»

The composition clause in §5 (its number was outside the extraction window; it cites
`5.5`, so it precedes it — by structure this is **cl. 5.3**) states the split as a
requirement:

> «…**общие** — в однокомнатных, **общие жилые комнаты (гостиные) и спальни** — в
> квартирах с числом комнат 2 и более, **а также вспомогательные помещения: кухню (или
> кухню-столовую), переднюю (прихожую), уборную (или туалет), ванную комнату и (или)
> душевую, или совмещенный санузел (согласно 5.5), кладовую (или встроенный шкаф).**
> Примечание — В однокомнатных квартирах вместо кухни допускается проектировать
> кухню-нишу.»

**Confirmed: the exact terms are «жилые комнаты» and «вспомогательные помещения» /
«помещения вспомогательного использования».** What falls in each:

| class | members, as the standard names them |
|---|---|
| **жилые комнаты** (habitable) | общая жилая комната (гостиная), спальня, детская комната |
| **вспомогательные помещения** (auxiliary) | кухня / кухня-столовая / кухня-ниша, передняя (прихожая), внутриквартирные холл и коридор, ванная комната или душевая, уборная / туалет / совмещенный санузел, кладовая, постирочная, встроенный шкаф, помещение теплогенераторной |

Table 7.1 (ventilation) gives the habitable sub-vocabulary independently, confirming
the three-way read of «жилые комнаты»:

> «Жилые комнаты (**спальня, общая жилая комната (или гостиная), детская комната**)» …
> «Кладовая, бельевая, гардеробная» … «Кухня (кухня-ниша, кухонная зона в
> кухне-столовой)…»

**And the partition is arithmetic, not vocabulary.** Annex A:

> «А.2.1 Площадь квартир определяют как сумму площадей всех отапливаемых помещений
> (**жилых комнат и вспомогательных помещений**, предназначенных для удовлетворения
> бытовых и иных нужд) и антресолей…»
>
> «А.2.3 Общая площадь квартиры — сумма площадей ее отапливаемых **жилых комнат и
> вспомогательных помещений**, встроенных шкафов, антресолей, а также неотапливаемых
> помещений (лоджий, веранд, холодных кладовых и тамбуров), балконов, террас…»

And cl. 5.2 / Table 5.1 keys the **minimum apartment area to the count of жилые
комнаты**: «Число жилых комнат 1/2/3 → Минимальная площадь квартир 28/44/56 м²».

> ⚠️ **This is the finding that decides the ticket.** The minimum-area check we must
> perform is a function of *how many rooms are in the habitable class*. A `zone_class`
> from which «число жилых комнат» is not recoverable **cannot evaluate cl. 5.2**. The
> partition is not a nicety we might align to; it is an input to a rule we already
> claim to check.

Cross-check inside the repo: `housing-quality-standards-as-bars.md` line 55 already
quotes cl. 5.6 — «…в 2-, 3- и 4-комнатных квартирах спальни и общие жилые комнаты
(гостиные) проектируют **непроходными**» — and that rule is stated over the *habitable
class as a whole*, spanning both what we would call `sleeping` and what we would call
`social`. A six-valued `zone_class` that splits those two apart **has no name for the
set the rule is written over.**

### 3.2 DIN 277 — a seven-group usage classification, NUF 1 is residential

DIN 277-1 defines seven usage groups (Nutzungsgruppen) of the Nutzungsfläche:
**NUF 1 "Wohnen und Aufenthalt"**, NUF 2 Büroarbeit, NUF 3 Produktion/Forschung,
NUF 4 Lagern/Verteilen/Verkaufen, NUF 5 Bildung/Unterricht/Kultur, NUF 6
Heilen und Pflegen, NUF 7 Sonstige Nutzungen; NUF 1 covers living rooms, bedrooms,
kitchens in dwellings and recreational areas.

> ⚠️ **SECONDARY SOURCE, and it matters.** This is from German trade summaries
> (`weka.de`, `gripsware.de`, `phase0.com`, `wohnflaechen-akademie.de`), **not from the
> DIN text**, which is paywalled and was not purchased. Treat the group titles as
> indicative. Note also what the structure implies: DIN 277 puts *the entire dwelling*
> — living, sleeping and kitchen alike — into **one** group. It classifies buildings by
> use, not rooms within a home. **It does not give us the partition we need.**

### 3.3 SIA 416 — **COULD NOT CONFIRM**

The search returned nothing usable on SIA 416's own category vocabulary
(HNF/NNF/VF/FF and their subdivisions). **No claim is made here.** If this matters,
it needs a dedicated pass against the SIA text.

---

## 4. What tools and generators actually do — no convergence at the leaf

### 4.1 Revit — free text

A Revit Room carries `Occupancy` and `Department` under Identity Data, alongside
`Base Finish / Ceiling Finish / Wall Finish / Floor Finish`. **The built-in `Occupancy`
parameter is a text parameter** — not an enumeration, not a picklist bound to any
standard. Practitioners routinely add shared text parameters to the Room category for
whatever taxonomy their office uses.

> ⚠️ **SECONDARY SOURCE.** The Autodesk help deep-link fetched returned a *Page Not
> Found*. This is from the Autodesk Community forum, `revitforum.org`, and the
> O'Reilly *Revit 2024 for Architecture* ch. 14. The **direction** of the finding
> (free text, no enumeration) is consistent across all of them, but no first-party
> Autodesk page was read end-to-end in this pass.

### 4.2 Archicad — a user-defined attribute list

**Zone Category is an Archicad *attribute*** — the same kind of object as a layer or a
fill. A category definition holds "the Category name, code, colour and zone stamp, and
a set of parameters", edited at `Options > Element Attributes > Zone Categories`, and
the zone stamp is a GDL object "whose look, contents and behavior can be fitted to
**local architectural practice**."

That is the whole answer: Archicad ships a *mechanism for you to define your own list*,
plus a template's worth of defaults, and explicitly frames the list as local. It is
structurally the same choice as our `zone_class` — which is mild evidence that inventing
one is *normal*, and no evidence at all that inventing one is *right*.

> ⚠️ **SECONDARY.** Read from search result summaries of
> `helpcenter.graphisoft.com/user-guide/128148/` and
> `help.graphisoft.com/AC/28/INT/_AC28_Help/040_ElementsVB/040_ElementsVB-139.htm`;
> the pages themselves were not fetched. **The actual default category list shipped in
> Archicad's residential template was not read** — so "does Archicad's out-of-the-box
> list happen to match ours" is unanswered.

### 4.3 Floor-plan generation research — everyone invents their own

**RPLAN** (Wu, Fu, Tang, Wang, Qi, Liu, *Data-driven Interior Plan Generation for
Residential Buildings*, ACM TOG 38(6):234, SIGGRAPH Asia 2019) — 80 788 plans, and
**8 room types: common room, bathroom, balcony, living room, master room, kitchen,
storage, dining room**, with the finer labels `MasterRoom / SecondRoom / …` used for
constraints.

Note what RPLAN's taxonomy *is*: it is a leaf vocabulary with `MasterRoom` vs
`SecondRoom` — a **rank inside the sleeping class**, which neither Uniclass nor SP 54
has, and which our 19 types presumably do not either. It also has no circulation type
at all. It is not a superset or a subset of anything else; it is its own thing.

> **COULD NOT CONFIRM:** Swiss Dwellings, LIFULL HOME'S and ResPlan taxonomies were
> **not read in this pass**. ResPlan is real (a 2025 vector-graph dataset of 17 000
> residential plans) but its label set was not retrieved. For Swiss Dwellings the repo
> already holds first-hand knowledge — `zoning.md` §2 records collapsing
> `{ROOM, BEDROOM, STUDIO}` into one private set and
> `LIVING_ROOM / LIVING_DINING / DINING` into social, which is itself evidence that
> **the corpus's own labels did not arrive grouped** and we had to group them.

### 4.4 The convergence question, answered

| system | residential leaf types | fixed? |
|---|---|---|
| Uniclass `SL_45_10` | 21 | yes, versioned |
| RPLAN | 8 | yes, dataset-fixed |
| SP 54.13330 | ~13 named terms in 2 classes | yes, statutory |
| Revit | 0 | free text |
| Archicad | 0 built-in standard | user attribute |
| **ours (proposed)** | 19 | — |

**There is no converged leaf taxonomy.** Four different counts, no shared codes, two
major tools shipping no vocabulary at all. Inventing a leaf list is the industry norm.

**But there IS convergence one level up**, and it is not the six-way split we proposed:
SP 54 splits 2 ways (habitable / auxiliary), DIN 277 groups the whole dwelling as one
usage group, and IFC's own `IsExternal` / `PubliclyAccessible` / `HandicapAccessible`
are *predicates over spaces*, not a partition. Nobody publishes
`{sleeping, social, kitchen, wet, circulation, service}` as a named enumeration.

---

## 5. Verdict

**Do not invent `zone_class` as specified. Invent less than that, and derive more.**

The proposal bundles three separable decisions, and they get three different answers.

**5.1 The 19 leaf types: keep them private. No standard is at our granularity, and
being at our granularity is the point.** Uniclass has 21 residential entries but they
include `Caravan pitches`, `Tent pitches` and `Hotel rooms` and exclude bathrooms; RPLAN
has 8 and no circulation. Adopting either as our primary key would mean carrying dead
values and missing live ones. **This is the one place "invent our own" survives contact
with the evidence.**

**5.2 Add a `uniclass_sl` code per leaf type, optional, for export only.** One column.
It is the only thing that makes our IFC readable to a consumer who is not us, it has a
conforming carrier already in the schema (`IfcRelAssociatesClassification` →
`IfcClassificationReference`, with `Location`, `Identification`, `Name`), and IFC
supplies no alternative because it supplies no vocabulary. **Record the Uniclass
version** (`SL v1.36, July 2026` as read) — the scheme rolls.

**5.3 Do not add a six-valued `zone_class`. Carry the statutory two-class partition
instead, and derive the rest.** Three reasons, in descending force:

1. **The statute's arithmetic needs the two-class partition and nothing else.**
   SP 54 cl. 5.2 / Table 5.1 keys minimum apartment area to «число жилых комнат»; A.2.1
   and A.2.3 both sum «жилых комнат **и** вспомогательных помещений». If our field
   cannot answer "is this a жилая комната", we cannot run the check.
2. **A six-way split loses the set the rules are written over.** Cl. 5.6's non-passage
   rule binds «спальни **и** общие жилые комнаты (гостиные)» — one rule, two of our
   proposed classes, no name for their union. We would immediately be writing
   `zone_class in {sleeping, social}` everywhere, which is `is_habitable` spelled badly.
3. **We already decided this, and `zone_class` would silently reverse it.**
   `docs/adr/0042-…` states: *"The social set is `is_habitable ∧ ¬is_sleeping`, and no
   new flag is added"*, and *"Terms 1, 2, 3 and 5 all read `is_sleeping`"*. A
   `zone_class` with a `social` value **re-adds the flag ADR 0042 refused**, and
   creates a second, independently-editable spelling of a set that is currently derived.
   The same argument retires `zone_class.wet`: `solver-formulation.md`'s wet subset and
   `rules.json`'s `wet.plumbing_group_count` already define the wet set by node
   membership, not by an enum value.

**Concretely, the shape this research supports:**

- `room_type` — the private 19-value leaf enum. Keep.
- `is_habitable` — the SP 54 «жилая комната» predicate, derived from `room_type`.
  **This is the field to actually add**, and it should be named after the statute, not
  after `zone_class`.
- `is_sleeping` — already exists (ADR 0042). Keep. Do not duplicate as an enum value.
- `wet`, `circulation`, `service`, `social` — **derived predicates over `room_type`**,
  not stored values. One source of truth, no drift, no third spelling.
- `uniclass_sl` — optional export mapping, versioned.

**The single strongest alternative to inventing our own** is **Uniclass 2015 table SL
(`SL_45` Residential spaces / `SL_45_10` Living spaces)** — as a *mapping target*, not
as an internal key. For the grouping, the strongest alternative is not an alternative
at all: **SP 54.13330's жилые/вспомогательные partition is binding on us**, because
our own rules already cite the clauses that are written over it.

---

## 6. What this does and does not establish

**Establishes, from primary sources:**

- The complete `IfcSpaceTypeEnum` value sets for IFC2X3 / IFC4 / IFC4X3 / IFC4X3_ADD2,
  from the EXPRESS schema our own exporter loads. IFC carries no room-use semantics.
- The complete property lists of `Pset_SpaceCommon`, `Pset_SpaceOccupancyRequirements`
  and `Pset_SpaceFireSafetyRequirements` with their definition text, including
  `OccupancyType`'s delegation to national code and `Reference`'s explicit
  "non-classification driven" disclaimer.
- `IfcRelAssociatesClassification` / `IfcClassificationReference` as the standard
  mechanism, with their exact attribute lists.
- 21 verbatim Uniclass `SL_45_10` codes and titles at the requested granularity, with
  the table version.
- The SP 54.13330.2022 two-class partition, its member lists in both directions, and
  three independent places (cl. 5.2/Table 5.1, Table 7.1, Annex A.2.1/A.2.3) where the
  partition is load-bearing rather than descriptive.
- ISO 12006-2's table 4.5 title, as quoted by NBIMS-US V3.
- RPLAN's 8-type taxonomy and its citation.

**Does not establish:**

- **OmniClass Table 13 residential codes.** Only the 2-page NBIMS wrapper was read. No
  `13-…` number for any residential room appears in this document, deliberately.
- **ISO 12006-2:2015.** `iso.org` 403'd; the table title quoted is from the **2001**
  edition as cited by a third party. Paywalled, not purchased.
- **SIA 416.** Nothing was found. No claim made.
- **DIN 277 group titles from the DIN text.** Secondary German trade sources only.
- **Bathrooms and WCs in Uniclass.** They are not in `SL_45_10`; the sub-tree that holds
  them was not read, so our wet-room mapping has **no confirmed target yet**.
- **First-party Autodesk and Graphisoft pages.** Both §4.1 and §4.2 rest on secondary
  or search-summary sources; the direction is consistent but no page was read whole.
  Archicad's shipped default zone-category list was not inspected.
- **Swiss Dwellings, LIFULL HOME'S, ResPlan taxonomies.** Not read this pass.
- **The exact clause numbers for two SP 54 passages.** §3.1's definition clause is
  identified as **3.1.27 by position** (the next numbered clause read is 3.1.28) and the
  composition clause as **5.3 by structure** (it cites 5.5, so it precedes it). Neither
  number was read directly off the page. **Verify before quoting a clause number into
  `rules.json` or an ADR.**
- **Whether AzDTN reproduces SP 54's partition verbatim.** §3.1 is SP 54.13330.2022.
  `az-region-profile` records the derivation, but the AzDTN text's own wording of the
  жилая/вспомогательная split was **not re-read in this pass**, and the region profile
  is the authority for that, not this document.
- **Any measurement.** Nothing here was measured against a corpus. This is a standards
  reading, and §5 is an argument from it, not from data.

---

## 7. Reproducing this

The IFC facts are reproducible offline, in seconds, against the project's own venv:

```python
# IfcSpaceTypeEnum across schemas
import ifcopenshell.ifcopenshell_wrapper as W
for s in ("IFC2X3","IFC4","IFC4X3","IFC4X3_ADD2"):
    print(s, list(W.schema_by_name(s).declaration_by_name("IfcSpaceTypeEnum").enumeration_items()))

# IfcSpace attributes / the classification relationship
sch = W.schema_by_name("IFC4")
for e in ("IfcSpace","IfcZone","IfcSpatialZone","IfcClassificationReference",
          "IfcRelAssociatesClassification"):
    d = sch.declaration_by_name(e)
    print(e, [(a.name(), str(a.type_of_attribute())) for a in d.all_attributes()])

# Pset property lists with definition text
from ifcopenshell.util.pset import PsetQto
q = PsetQto("IFC4")
for n in ("Pset_SpaceCommon","Pset_SpaceOccupancyRequirements",
          "Pset_SpaceFireSafetyRequirements"):
    t = q.get_by_name(n)
    print(n, t.ApplicableEntity)
    for p in t.HasPropertyTemplates:
        print("  ", p.Name, p.PrimaryMeasureType, p.Description)
```

Run as `./venv/Scripts/python.exe`, `ifcopenshell 0.8.5`, Windows 11 / Python 3.12.

The SP 54 and OmniClass quotes were extracted from the published PDFs with the
project's own `pymupdf` (`pymupdf.open(path)`, `page.get_text()`), then searched for the
Russian keys `вспомогательные помещения`, `Жилые комнаты`, `Общая площадь квартиры`,
`передняя`. **Set `PYTHONIOENCODING=utf-8`** — the default `cp1252` console codec raises
`UnicodeEncodeError` on the Cyrillic and silently truncates the extraction.

### Sources

| # | source | how read | trust |
|---|---|---|---|
| 1 | IFC4 / IFC4X3 / IFC4X3_ADD2 EXPRESS schema + IFC4 Pset templates, as shipped in `ifcopenshell 0.8.5` | executed locally | **primary** |
| 2 | Uniclass 2015 SL, `SL_45_10 Living spaces` v1.36 (July 2026) — https://uniclass.thenbs.com/taxon/sl_45_10 | fetched | **primary** |
| 3 | NBIMS-US V3 §2.4.4.3, *OmniClass Table 13 – Spaces by Function* (NIBS/buildingSMART alliance, ©2015) — https://nibs.org/wp-content/uploads/2025/04/NBIMS-US_V3_2.4.4.3_Omniclass_Table_13_Spaces_by_Function.pdf | fetched, PDF text extracted | **primary** (wrapper only; table not included) |
| 4 | СП 54.13330.2022 «СНиП 31-01-2003 Здания жилые многоквартирные» — https://rkc56.ru/attach/orenburg/docs/Gosstandart_RF/SP-54.13330.2022-Mnogokvartirnie.pdf (39 pp.) | fetched, PDF text extracted | **primary** |
| 5 | Wu, Fu, Tang, Wang, Qi, Liu, *Data-driven Interior Plan Generation for Residential Buildings*, ACM TOG 38(6):234, SIGGRAPH Asia 2019 (RPLAN) — http://staff.ustc.edu.cn/~fuxm/projects/DeepLayout/index.html | search summaries citing the paper and derived datasets | secondary |
| 6 | Archicad Zone Categories — https://helpcenter.graphisoft.com/user-guide/128148/ , https://help.graphisoft.com/AC/28/INT/_AC28_Help/040_ElementsVB/040_ElementsVB-139.htm | search summaries only | secondary |
| 7 | Revit room Identity Data (`Occupancy` a text parameter) — Autodesk Community, revitforum.org, *Revit 2024 for Architecture* ch. 14 | search summaries only | secondary |
| 8 | DIN 277-1 usage groups NUF 1–7 — weka.de, gripsware.de, phase0.com, wohnflaechen-akademie.de | search summaries only | secondary; DIN text paywalled |
| 9 | `standards.buildingsmart.org` (IFC4 ADD2 TC1 HTML), `ifc43-docs.standards.buildingsmart.org`, `iso.org/standard/61753.html` | **403 / expired TLS certificate / 403** | **unreachable** |

Repo cross-references used in §5: `docs/adr/0042-the-entry-depth-inversion-is-a-fifth-term-and-its-corpus-rate-is-a-ceiling.md`,
`docs/research/housing-quality-standards-as-bars.md`, `docs/research/zoning.md`,
`docs/research/bim-cad-export-stack.md`, `docs/research/az-region-profile/_sources_canon.json`.
