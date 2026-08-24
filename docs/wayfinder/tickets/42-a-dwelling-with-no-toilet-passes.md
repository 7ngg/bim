---
id: 42
title: A dwelling with no toilet passes every check
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - data/acceptance/rules.json
  - docs/spec/acceptance-bar.md
---

# A dwelling with no toilet passes every check

## Question

**Nothing in this system requires a dwelling to contain any particular room.**
Every dimensional rule is of the form *if a Room of type T exists, it is at least
this big*. Not one asks whether T exists at all. So a Brief naming a living room,
a bedroom, a kitchen and a bathroom resolves, solves, passes all 38 predicates,
and exports a valid IFC of a flat **with no toilet**.

"A bathroom implies a WC" is not available as a defence. The ergonomic floor for
`bathroom` is **1000 × 1700 mm** — a bath and nothing beside it — and
`CONTEXT.md` treats `wc` as a separate Room type that a Brief names separately.
Found while building the room vocabulary mapping (*Two room vocabularies in one
file*), which is where the absence became visible: the mapping is total over room
*types*, and total over types says nothing about which types a **dwelling** owes.

### The source is already read, and it is mandatory

AzDTN 2.7-2 **cl. 5.2**, in the file at
`experiments/finish-layer/out/azdtn_2_7_2.txt`:

> «Mənzillərdə yaşayış otaqları və yardımçı sahələr: mətbəx (və ya taxça-mətbəx),
> holl, vanna otağı (və ya duş) və tualet (və ya birləşdirilmiş sanitar qovşağı),
> yığnaq otağı (və ya divar təsərrüfat şkafı) nəzərdə tutulmalıdır.»

Register `nəzərdə tutulmalıdır` = **məcburi**, mandatory, per the file's own
`source_force_vocabulary`. Every flat shall have: a kitchen **or** kitchen-niche;
a hall; a bath **or** shower; a **WC or combined sanitary unit**; a storage room
**or** a built-in utility cupboard.

This is a **composition** requirement — a shape of rule the acceptance bar does
not currently have. All 38 predicates are per-Room, per-Wall, per-Opening or
per-Plan-geometry. None is *per-programme*.

Settle:

- **Does the rule bind the Brief, the Plan, or both?** It reads like a §9
  parse-time check — cheaper to tell a Homeowner "this needs a toilet" before a
  generate cycle than after. But `resolve` invents circulation, so a `hall` can be
  satisfied by invention while a `wc` cannot, and the two halves may not enforce
  in the same place. Note `site: both` is the shape *Acceptance validator spec*
  uses when a rule must hold in the solver and the validator; this may want a
  third site the registry has no word for.
- **Hard or soft, and does that differ per room.** A missing WC is a defect
  nobody would ship. A missing `yığnaq otağı` is a storage cupboard, and the norm
  offers `divar təsərrüfat şkafı` — a *built-in wardrobe* — as an alternative,
  which is furniture this engine does not model. One clause, and its five limbs
  do not obviously carry the same severity.
- **Whether `resolve` should add the missing room rather than reject.** C4 says
  gaps are filled from standards and every assumption surfaced, and `resolve`
  already invents circulation. Inventing a WC is the same move. But it changes the
  Engine room count, which C13's band gates on, and a Brief at 10 rooms that gains
  an eleventh is refused *because we added it*.
- ⚠️ **The alternatives are disjunctions the model may not be able to express.**
  `mətbəx (və ya taxça-mətbəx)` — the Brief has no `kitchen_niche` type at all
  (*Two room vocabularies* recorded that narrowing). `tualet (və ya birləşdirilmiş
  sanitar qovşağı)` — no ergonomic key can say the WC sits inside the bathroom, so
  the second limb is **inexpressible**, and a rule that demands a `wc` Room would
  reject the combined-unit layout the norm permits. Deciding this rule may require
  deciding whether the room vocabulary grows.
- **What C8 permits us to say about it.** The source is statutory and the register
  is mandatory, so `statutory_floor_binding: warn` is the established posture for
  *dimensional* AZ numbers. A composition rule that only warns produces a flat with
  no toilet and a warning. If it is hard, it is the **first hard rule sourced to a
  region document**, and C14 says a profile may never change which Plans are
  rejected — so it would have to live on the region-invariant layer, and the
  justification cannot be "Azerbaijani law says so".

The closing check: **a Brief that names no `wc` and no combined unit cannot reach
export**, and a conformance test asserts the composition rule at whichever site
the answer puts it.

### Concurrency

`data/acceptance/rules.json` is also claimed by 16, 20 and 26;
`docs/spec/acceptance-bar.md` by 26. Per the map's Notes this is a merge hazard,
not a dependency — do not run this at the same time as any of them.
