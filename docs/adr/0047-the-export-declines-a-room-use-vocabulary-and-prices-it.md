# ADR 0047 — The export declines a room-use vocabulary, and the decline is priced rather than silent

- **Status**: accepted
- **Date**: 2026-09-01
- **Ticket**: [An IfcSpace carries no room use, and IFC has no vocabulary to give it one](../wayfinder/tickets/84-an-ifcspace-carries-no-room-use.md)
- **Amends**: nothing. **Does not amend ADR 0011** (Reference View), whose header
  claim this ticket's research confirms — see consequence 5.
- **Supersedes nothing**

## Context

Every `IfcSpace` this engine emits is silent about what its room is for.
`IfcSpaceTypeEnum` in IFC4 is `SPACE, PARKING, GFA, INTERNAL, EXTERNAL,
USERDEFINED, NOTDEFINED`; IFC4.3 adds one value in a decade and it is `BERTH`, a
mooring. `Pset_SpaceCommon` has six properties and none is a room use. **IFC ships
a socket, not a vocabulary**: `IfcRelAssociatesClassification` →
`IfcClassificationReference`.

The ticket asked whether to fill that socket. It was opened on the premise that a
room name *"is a string in one language"* and a classification code is not. **That
premise is half false, and it changed the question.** §6 already writes two strings:
`Name` carries the canonical ergonomic key (`bedroom_double`), which is stable and
language-free, and `LongName` carries the `AZ` display label. The gap is not
English-versus-Azerbaijani. It is that `bedroom_double` is a **private** identifier
— language-free but a vocabulary of one — so a consumer still needs our dictionary.

Three findings then decided it, and the first two reversed a decision already taken
within the session that produced this ADR.

**1. The scheme covers us, and the coverage number that matters is not the type
count.** `SL_45 Residential spaces` has exactly one child group, so a full mapping
draws from four separate SL branches; our wet rooms classify under *Medical, health,
welfare and sanitary spaces*. 18 of 19 types have a verbatim-read target — but
weighted by the corpus the retrieval actually draws from, the one hole is
`living_dining` at **24 122 rooms, the second-largest class in the corpus**, which is
**71,2 % of all social rooms** (24 122 against `living` 8 453 and `dining` 1 315).
"18 of 19" flattered it.

**2. Nothing reads it.** Six published IFC models were downloaded and parsed —
four authoring tools, 2011–2024, including buildingSMART's own current
certification dataset: **431 `IfcSpace` entities, zero carry a classification**,
while the same files classify **3 345 non-space objects**. Two of the six are
decisive rather than circumstantial:

- **Schependomlaan**, a real Dutch housing project, classifies 3 343 walls, slabs
  and doors with NL/SfB and skips all 100 spaces. Its header records the choice:
  `Option [ArchiCAD Zone Categories as IFC Space classification data: Off]` — a
  purpose-built switch, left off on a delivered project.
- **buildingSMART's own single-family-house certification model** (IFC4 RV and
  IFC4X3 RV, 2024) classifies the `IfcBuilding`, leaves both rooms bare, and puts
  the room use in `ObjectType`. That is the reference implementation of the exact
  MVD our own header claims.

Revit — the consumer that matters most — does read it, into a `ClassificationCode`
shared parameter, but lands it on a **Generic Model DirectShape rather than a
Room** (Autodesk issue #15, open since 2018), discards `Location` and `Edition`,
and mangles the value to `[Uniclass 2015]SL_45_10_09:Bedrooms`. C2 holds this model
to Practitioner grade, where *"90 %-right is worse than blank"*. Attached to the
wrong object and mangled is not 90 %-right.

**3. The statutory grouping is not ours to export, and it is not what the ticket
thought it was.** The ticket asked whether `counts_as_otaq` is SP 54.13330's
жилые/вспомогательные partition under another name. **It is not.** It instantiates
AzDTN 2.7-2's, which *differs*: SP 54 3.1.27 lists «кухня (или кухня-столовая)» as
auxiliary, AzDTN replaced that with «mətbəx və ya taxça-mətbəx», and then defined
`mətbəx-yemək otağı` in sec. 3 as an «otaq». AzDTN also carries the habitable list
**twice, inconsistently** — cl. 5.5's parenthetical against Cədvəl 6, which puts
`kabinet` outside the habitable group — and uses `otaq` in two irreconcilable senses,
defining `mətbəx` itself as one. Russian keeps комната and помещение apart;
Azerbaijani had `sahə` and `yerləşgə` available, and AzDTN used `otaq` anyway.

## Decision

**1. No classification association ships in v1.** No
`IfcRelAssociatesClassification`, no `IfcClassification`, no
`IfcClassificationReference`. **`IfcSpace.Name` and `LongName` remain the whole of
what the file says about a room's use.**

**2. The decline is registered, not omitted.** §8.5's register gains a row, because
this file's rule is that *"unknown is distinguishable from forgotten"* — and
classification was in neither the written set nor the register, the one state §8.5
exists to make impossible. Before this ADR, `ifc-export.md` contained **zero**
occurrences of the string "classif".

**3. The price is written down where a future reader will find it.** §11 —
*Deliberately absent, and what it would take to add* — carries the fifteen-code
mapping, the `living_dining` hole, and the one real cost of declining: **the
vacuous-pass hazard.** buildingSMART's own published IDS sample selects rooms by
applicability `IfcSpace` + classification `SL_45_10_09` (*Bedrooms*, the exact
code). Run against an unclassified export it matches zero elements and **passes
green** — a silent false negative, which is the failure mode this file's whole
omission discipline exists to prevent. Adding it later is a data change plus one
relationship, not a redesign.

**4. `ObjectType` is declined too, explicitly.** buildingSMART's certification model
uses it because that model has no meaningful `Name`. Ours would be a third copy of
`bedroom_double` — ADR 0002's duplicated state, and the same objection §8.5 already
sustained against `Pset_SpaceCommon.Reference`. `PredefinedType` stays `SPACE`.

**5. The habitable/auxiliary grouping does not travel into the file either, and
this is a positive decision rather than an absence.** The partition the engine
carries is self-contradictory *in its own source norm* (context, finding 3).
Exporting it under our authority would launder a norm defect into something a
Practitioner reads as fact. Room identity travels as `Name` and `LongName`; the
partition is the reader's jurisdiction to apply.

## Consequences

1. **A Practitioner opening our export gets nineteen rooms named in two strings and
   classified in none.** That is the state the ticket opened against, and it is now
   chosen rather than inherited. The engine's differentiator is C3 — a dimensioned
   2D vector plan no competitor documents — and a classification code moves nothing
   there.

2. **Declining is a choice, not a limitation, and that is established at byte
   level.** Classification Association **is in scope** for IFC4 Reference View 1.2.
   The mvdXML vendored in `ifcopenshell` was proved identical to buildingSMART's
   published file at
   `.../RV1_2/HTML/annex/annex-a/reference-view/ReferenceView_V1-2.mvdxml` —
   805 551 bytes, the 12 774-byte delta reproduced exactly as 12 771 CRLF plus
   3 NBSP. We could have written it and conformed. We are not writing it because
   nothing reads it.

3. **The `living_dining` naming gap is now three vocabularies deep**, and it is on
   the map as fog rather than resolved here. AzDTN has no word — the engine
   compounded `qonaq-yemək otağı` as `src: engine_choice`, *"the compound itself is
   not in the norm"*; its `az_area` guard resolves `referent: undetermined`; and
   Uniclass has no code, while shipping both `Kitchen-dining rooms` and
   `Kitchen-dining-living rooms`. Meanwhile `kitchen_dining` — **41 corpus rooms**,
   a label `corpus_label_map` itself calls *"DISQUALIFIED as a measurement of this
   type"* — has both an AzDTN clause and a Uniclass code. The type with 41 instances
   has two vocabularies; the type with 24 122 has none.

4. **Occurrence-versus-type is an open question this ADR does not answer.** COBie V3
   moved space classification off `IfcSpace` onto `IfcSpaceType` via
   `IfcRelDefinesByType`. This export has no `IfcSpaceType` layer at all, so the plan
   considered here implemented the *superseded* shape. That is a spatial-structure
   decision and it is ticketed.

5. **ADR 0011's header string is confirmed, and a suspected defect in it is
   dismissed.** The MVD's own identifier attribute is `code="ReferenceView_V1-2"`
   with a hyphen, against the dot in §2 and §10 check #2 — but those are different
   fields, and buildingSMART's own PCERT sample scene writes **`IFC4
   ReferenceView_V1.2`** in its header. §2.2 replaced `ifcopenshell`'s false
   `CoordinationView` default with the correct string. Also worth recording:
   `status="sample"` appears identically in bSI's own copy, so it is an IfcDoc export
   artefact and not a signal about the release's standing.

6. **Two inferred clause numbers in `room-classification-standards.md` §6 are now
   confirmed correct** and may be quoted: SP 54 **3.1.27** and **5.3**, both read
   directly off the page rather than inferred by position.

7. **This ADR writes no data file.** The five provenance defects the research found
   in `counts_as_otaq_sourcing`, and the Cədvəl 1 shortfall, are outside this
   ticket's `writes:` set and are raised as tickets rather than taken. See the map.
