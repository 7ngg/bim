---
id: 84
title: An IfcSpace carries no room use, and IFC has no vocabulary to give it one
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - docs/spec/ifc-export.md
  - docs/adr/
declared_on_resolution:
  - docs/adr/0047-the-export-declines-a-room-use-vocabulary-and-prices-it.md
  - docs/research/ifc-reference-view-classification-scope.md
  - docs/research/ifc-space-classification-consumers.md
  - docs/research/az-habitable-room-partition.md
---

# An IfcSpace carries no room use, and IFC has no vocabulary to give it one

## Question

**The Destination names *valid IFC* as one of two outputs, and every `IfcSpace`
this engine emits will say nothing about what its room is for.**

Read out of the EXPRESS schema in this repo's own pinned `ifcopenshell 0.8.5`,
not off a website — `docs/research/room-classification-standards.md` §1:

- `IfcSpaceTypeEnum` in IFC4 is exactly `SPACE, PARKING, GFA, INTERNAL,
  EXTERNAL, USERDEFINED, NOTDEFINED`. **IFC4.3 adds one value in a decade and it
  is `BERTH`**, a mooring. There is no bedroom, no kitchen, no bathroom.
- `Pset_SpaceCommon` has six properties and none is a room use. Its `Reference`
  definition says outright *"Used to store the **non-classification driven**
  internal project type."*
- `Pset_SpaceOccupancyRequirements.OccupancyType` is an `IfcLabel` — a free
  string — *"defined according to the presiding national building code"*.
- `IfcZone` has no `PredefinedType` at all.

**IFC ships a socket, not a vocabulary**: `IfcRelAssociatesClassification` →
`IfcClassificationReference`. So a Practitioner opening our export today gets
nineteen anonymous spaces, and C2 holds the geometry model to Practitioner grade
where *"90 %-right is worse than blank"*.

**What has to be decided:**

1. **Whether a classification reference ships in v1 at all**, or whether the
   room name in `Name`/`LongName` is judged sufficient. ⚠️ Note what the
   alternative costs: a name is a string in one language, and this profile's
   drawing language is Azerbaijani (ADR 0024). A classification code is
   language-free and a name is not.

2. **Which scheme, if one ships.** The research names **Uniclass 2015 table SL,
   group `SL_45_10` "Living spaces"** as the strongest candidate — 21 residential
   entries read verbatim at exactly our granularity, including `SL_45_10_09
   Bedrooms`, `_49 Living rooms`, `_23 Domestic kitchens`, `_44 Kitchen-dining
   rooms`, `_45 Kitchen-dining-living rooms`. ⚠️ **Three cautions, all from the
   research's own §6**: it is a **rolling** scheme (read at v1.36, July 2026, so
   *"Uniclass 2015"* names a family and not a version); bathrooms and WCs are
   **not** in that group and the sub-tree holding them was not read; and it is a
   **British** scheme on an **Azerbaijani** product, which is a C12 question this
   map has answered one way for the `AZ` profile and has never been asked here.
   **OmniClass Table 13 entry codes could not be confirmed** — the NIBS file is a
   two-page wrapper — so it is not a like-for-like alternative yet.

3. **Whether the grouping travels too, and under whose authority.** ADR 0044
   lands `is_sleeping` and `is_circulation` as *our* classes. The research finds
   the partition is **statutory in our region and not ours to invent a rival
   for**: SP 54.13330 splits a dwelling into «жилые комнаты» (спальня, общая
   жилая комната, детская) and «помещения вспомогательного использования»
   (кухня, передняя, холл и коридор, ванная, уборная, кладовая, постирочная), and
   **cl. 5.2 / Table 5.1 keys minimum apartment area to «число жилых комнат»** —
   the partition is arithmetic, not vocabulary. ⚠️ **This engine may already carry
   it under another name**: `counts_as_otaq` is AzDTN cl. 5.5's unit and diverges
   from `is_habitable` on exactly `kitchen_dining` (gate V6). Whether those are
   the same partition, or two, is the first thing to settle — and if they are the
   same, the divergence is a finding about the two norms rather than about us.

4. **Where it lands if it ships** — a per-type field beside `corpus_label_map`
   and `area_band_classes` (ADR 0037 puts *every* vocabulary projection there),
   or in `ifc-export.md` alone as an export-time table. ⚠️ The first is the
   precedent; the second is defensible only if no other consumer will ever want
   it, which is the judgement that has now failed twice on this map.

**What this is not.** Not a change to the nineteen internal Room types — the
research is explicit that the leaf key stays ours and Uniclass is a **mapping
target**, not a replacement. Not a re-opening of ADR 0011's Reference View
decision. Not a claim that the export is currently invalid: it is valid and it is
silent, which is a different defect.

## Raised by

*Land the sleeping flag and retire the private corpus-label copies* (2026-08-31),
whose market check — fired to test whether a private `zone_class` should be
invented — answered that question **no** and surfaced this one instead.
`docs/research/room-classification-standards.md`.

## Resolution (2026-09-01)

**Nothing ships. The export names rooms in two strings and classifies none — and
that is now a decision with a measured price rather than a silence.** ADR 0047;
`ifc-export.md` §8.5 (two new rows), §11 (*Room use*), summary decision 16.

**The decision was taken one way, then reversed by measurement.** The session
first settled on shipping a Uniclass reference, on coverage evidence. Two research
findings reversed it. Both are recorded because a reversal that leaves no trace
invites the next reader to redo it.

### The ticket's own premise was half false, and it moved the question

Item 1 rests on *"a name is a string in one language and a classification code is
not."* §6 already writes **two** strings: `Name` is the canonical ergonomic key
(`bedroom_double`) — stable and language-free — and `LongName` is the `AZ` label.
The gap is not English-versus-Azerbaijani. It is that `bedroom_double` is a
**private** identifier: language-free but a vocabulary of one. That reframing is
what makes the decision turn on *who reads a shared code*, and nothing else.

### 1. Coverage was better than the research thought, and the metric was wrong

The unread sub-trees were read. `SL_45 Residential spaces` has exactly **one**
child group, so a full map draws from four SL branches — our wet rooms land under
*Medical, health, welfare and sanitary spaces*. **18 of 19 types have a
verbatim-read target, in 15 codes.** The full table is in `ifc-export.md` §11.

But type count is the wrong weighting. The one hole is **`living_dining` — 24 122
corpus rooms, the second-largest class, 71,2 % of all social rooms** (against
`living` 8 453 and `dining` 1 315). Weighted by what the retrieval actually draws,
"18 of 19" flattered it badly.

### 2. Nothing reads it — 431 spaces, zero classifications

Six published IFC models parsed first-hand, four authoring tools, 2011–2024,
including buildingSMART's own certification dataset: **431 `IfcSpace` entities,
zero classified**, while the same files classify **3 345 non-space objects**.

- **Schependomlaan** — real Dutch housing, Archicad 18 — classifies 3 343 walls,
  slabs and doors with NL/SfB and skips all 100 spaces. Its header names the
  choice: `Option [ArchiCAD Zone Categories as IFC Space classification data:
  Off]`. A purpose-built switch, off on a delivered project.
- **buildingSMART's own single-family-house certification model** (IFC4 RV and
  IFC4X3 RV, 2024) classifies the `IfcBuilding`, leaves both rooms bare, and puts
  room use in `ObjectType` — the reference implementation of the MVD our header
  claims.
- **Revit** reads it into a `ClassificationCode` parameter on a **Generic Model
  DirectShape, not a Room** (Autodesk issue #15, open since 2018), discarding
  `Location` and `Edition` and mangling the value. C2's *"90 %-right is worse than
  blank"* is not met by "attached to the wrong object".

No residential handover standard names space classification, no competitor emits
it, and the Dutch national IDS wrote out its entity list and **left `IFCSPACE`
off**. CLAUDE.md's market test now has a measured answer, not a surveyed one.

### 3. Item 3 answered: the grouping is AzDTN's, it differs from SP 54's, and it
must not travel

The ticket asked whether `counts_as_otaq` and SP 54's жилые/вспомогательные split
are one partition or two. **Two.** SP 54 3.1.27 lists «кухня (или кухня-столовая)»
as auxiliary; AzDTN replaced that with «mətbəx və ya taxça-mətbəx» and then defined
`mətbəx-yemək otağı` in sec. 3 as an «otaq». AzDTN carries the habitable list
**twice, inconsistently** — cl. 5.5's parenthetical against Cədvəl 6, which puts
`kabinet` outside the habitable group — and defines `mətbəx` itself as an `otaq`,
contradicting cl. 5.2.

**The `kitchen_dining` / `living_dining_kitchen` asymmetry the ticket flagged is
real and correct, and it is SP 54 that backs it, not AzDTN.** 3.1.18
`кухня-столовая` is an auxiliary **room** (0 otaq); 3.1.17 `кухня-ниша` is a
**zone** inside a habitable room, so the host keeps its class (1 otaq). Room versus
zone, not "contains a kitchen". **No flag value changes.**

So the grouping does not travel — a positive decision, not an absence. Exporting a
partition whose own source norm contradicts itself would launder a norm defect into
something a Practitioner reads as fact.

### What declining costs, stated so nobody discovers it by accident

buildingSMART's own published IDS sample selects rooms by applicability `IfcSpace`
+ classification `SL_45_10_09` — *Bedrooms*, the exact code. Against an export of
ours it matches zero elements and **passes green**: a silent false negative. That is
the single thing shipping would have bought, and it is now in §11 rather than
undiscovered.

### Declining is a choice, not a limitation

Classification Association **is** in RV1.2 scope. Established at byte level: the
mvdXML vendored in `ifcopenshell` is buildingSMART's published file, 805 551 bytes,
the 12 774-byte delta reproduced exactly as 12 771 CRLF plus 3 NBSP. We could have
conformed. We are not writing it because nothing reads it.

### Four things this ticket found and did not take

Three sit outside its `writes:` set and are raised rather than smuggled in, per the
Notes rule that produced two pure-rework tickets when it was broken.

1. **The otaq flag's sourcing is misdescribed in five places and silent in one** —
   `counts_as_otaq_sourcing.per_key` carries **18 rows for 19 types**
   (`bathroom_combined` absent); **cl. 5.5, cited 8×** as the habitable authority, is
   a *basement prohibition* whose list is a parenthetical AzDTN added; **cl. 5.2,
   cited 7×** as the auxiliary authority, is a *composition requirement* with five
   members while the real definition — sec. 3 `yardımçı sahələr`, seven members — is
   cited **once**. Ticket raised; `room-constraints.json` is 72's.
2. **The engine's dwelling floor sits below the only Azerbaijani otaq-indexed
   figure in existence.** AzDTN cl. 5.1 / Cədvəl 1's urban minima
   **28/44/56/70/84/103** are SP 54 Table 5.1's minimum column digit-for-digit;
   the engine's Σ of hard minima runs **26,5 / 37,5 / 47,5 / 57,5** — short by
   1,5 / 6,5 / 8,5 / 12,5, widening monotonically. AzDTN states it
   `tövsiyə olunur` and scopes it to the state and municipal fund, so **no mandatory
   check is missing and C8 is not at risk** — but every whole-dwelling bound in
   `rules.json` is against the Brief's `target_area`, a user input, and AzDTN 2.7-2
   cl. 5.1 is cited in no shipped artefact. Ticket raised.
3. **COBie V3 moved space classification onto `IfcSpaceType`.** This export has no
   `IfcSpaceType` layer, so the plan considered here implemented the superseded
   shape. It claims `ifc-export.md`, so it was only raisable once this closed.
   Ticket raised.
4. **`living_dining` is unnamed by three vocabularies** — AzDTN (`engine_choice`,
   *"the compound itself is not in the norm"*), its own `az_area` referent
   (`undetermined`), and now Uniclass, which ships both kitchen-dining compounds
   and no living-dining. Meanwhile `kitchen_dining` — 41 corpus rooms, a label
   `corpus_label_map` calls *"DISQUALIFIED as a measurement"* — has both. **Fog, not
   a ticket**: the question is not yet sharp enough to state.

### Two loose threads closed on the way past

- **ADR 0011's header string is right.** `code="ReferenceView_V1-2"` (hyphen) is the
  mvdXML's identifier attribute; the header convention is the dot, and bSI's own
  PCERT sample writes `IFC4 ReferenceView_V1.2`. §10 check #2 enforces the correct
  string. Also: `status="sample"` is in bSI's own copy, so it is an IfcDoc export
  artefact, not a signal about standing.
- **`room-classification-standards.md` §6's two inferred clause numbers are
  confirmed correct** — SP 54 **3.1.27** and **5.3**, both now read off the page.

### Handed on as prose

**AzDTN cl. 9.11** is a mandatory otaq-keyed insolation rule
(«1, 2 və 3 otaqlı mənzillərdə ən azı bir yaşayış otağında … təmin **edilməlidir**»)
and appears in no artefact. `docs/research/az-region-profile/daylight.md` §2.3
already defers KEO for v1 on sound reasoning and is not reopened — the clause number
belongs next to that deferral. Not taken here: the file is not this ticket's.
