---
id: 84
title: An IfcSpace carries no room use, and IFC has no vocabulary to give it one
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - docs/spec/ifc-export.md
  - docs/adr/
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
