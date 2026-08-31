---
id: 88
title: The export has no IfcSpaceType and the exchange standard moved there
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - docs/spec/ifc-export.md
---

# The export has no IfcSpaceType and the exchange standard moved there

## Question

**Nineteen `IfcSpace` occurrences are emitted and no `IfcSpaceType` exists, and the
one exchange standard that asks anything of a space's semantics now asks it of the
type.** COBie 2.4 / BS 1192-4 required `Space.Category` from Uniclass SL on the
occurrence; **COBie V3 moved it onto `IfcSpaceType` via `IfcRelDefinesByType`.**

ADR 0047 declined a room-use vocabulary on the occurrence and was right to, on
measurement. But it declined the *older shape*. The question of whether this file
should carry a type layer at all was never asked — it is a spatial-structure
decision, not a classification one, and it survives the decline intact.

⚠️ **This is not a request to reverse ADR 0047.** If a type layer is refused, ADR
0047 stands unchanged and this ticket closes with a second register row. If a type
layer ships, the classification question returns *at the type*, where a scheme is
declared once for nineteen types rather than nineteen times — a different cost
structure from the one ADR 0047 priced.

## What has to be settled

1. **Whether `IfcSpaceType` ships at all.** Object Typing is in RV1.2 scope — it is
   named in §2.1's in-scope list. `IfcSpaceType` carries `PredefinedType`,
   `ElementType` and its own property sets, so it is the schema's own place for
   *"all bedrooms share these properties"*. Today every Space repeats them.
2. **What it would buy beyond tidiness.** ⚠️ The honest starting position is: with
   nineteen occurrences and no repetition worth deduplicating, possibly nothing. A
   type layer that exists only to hold a classification nobody reads is ADR 0047's
   finding one entity up.
3. **Whether COBie is a target for this product at all.** ⚠️ **Read the evidence
   before assuming.** COBie is a facilities-handover schema for asset owners; C2's
   v1 buyer is a **Homeowner** and the Practitioner is a standard, not a customer.
   The BS 1192-4 requirement is **vendor-attested only** — BSI's text is paywalled
   and was not read. If COBie is not a target, item 1 loses its main argument and
   should be decided on the property-set case alone.
4. **What §11's *Room use* section says afterwards.** It currently prices adding a
   classification on the occurrence. If the type layer is where a scheme would
   land, that section is describing the wrong insertion point.

## What this is not

Not a re-opening of ADR 0047's measurement — 431 published spaces carrying zero
classifications is a fact about spaces, and a type layer does not change it. Not a
re-opening of ADR 0011's Reference View decision. Not a change to §3's spatial
structure, which decomposes `IfcSite → IfcBuilding → IfcBuildingStorey → IfcSpace`
and is settled.

## Conflicts

None at creation. ⚠️ It claims `docs/spec/ifc-export.md`, which is why it could not
be raised until *An IfcSpace carries no room use* closed — the same file, and the
Notes rule forbids two live claimants.

## Raised by

*An IfcSpace carries no room use* (2026-09-01), whose consumer research found the
COBie V3 move while establishing that nothing reads classification on the
occurrence. `docs/research/ifc-space-classification-consumers.md`.
