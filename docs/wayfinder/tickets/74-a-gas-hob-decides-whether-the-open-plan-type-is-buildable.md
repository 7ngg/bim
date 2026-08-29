---
id: 74
title: A gas hob decides whether the open-plan type is buildable in AZ
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - data/standards/room-constraints.json
  - docs/spec/brief.md
---

# A gas hob decides whether the open-plan type is buildable in AZ

## Question

**`living_dining_kitchen` is one of `brief.md` §3's nineteen Room types, the AZ
profile maps it, and a mandatory Azerbaijani norm says the room it describes
cannot hold the cooking appliance the region actually fits.**

AzDTN 2.13-1 *Qaz təchizatı. Layihələndirmə normaları* cl. 8.31, read first-hand
from the PDF arxkom serves, mandatory register (`nəzərdə tutulmalıdır`):

> Yaşayış evlərində qaz pilətələrinin qoyulması nəfəslikli pəncərəsi, sorucu
> ventilyasiya kanalı və təbii işıqlandırılması olan, hündürlüyü 2,2 m-dən az
> olmayan **mətbəx otaqlarında** nəzərdə tutulmalıdır.

A gas hob **must** sit in a `mətbəx otağı`. AzDTN 2.7-3 cl. 4.7 files a
`mətbəx-yemək otağı` **inside** the word kitchen — *«mətbəx (o cümlədən
mətbəx-yemək otağı)»* — so a **kitchen-diner is compliant**. Neither norm
classifies a kitchen opened into a living room as a `mətbəx otağı`, so a
**`living_dining_kitchen` is not**, and needs an electric hob.

**MİDA hands over its apartments with a gas hob fitted.** Azerbaijan does not
carry the Moscow-style blanket prohibition on open-plan gas — it mandates the
mitigation instead (amended cl. 8.40: a 10 %-LEL detector wired to a solenoid
cut-off at every apartment's gas entry) — but the category rule in cl. 8.31 is
untouched by that.

⚠️ **The binding constraint is the room's category, not its size.** At 2,7 m
clear height cl. 8.31's 15 m³ volume rule is only 5,6 m² of floor, so it never
binds a real open-plan room. Nothing the engine can do to the *geometry* fixes
this, which is what makes it a product question rather than a dimensional one.

**Found by *The market tier has an Azerbaijani source now* (§6.5 of
`az-market-default-against-practice.md`), which recorded it as owned by nothing.**
That note's own handoff table says so in as many words: *"not currently owned by
anything on the map"*. It is the C8 failure seen from the inside — the engine
emitting a plan that cannot be built as drawn in the one region v1 ships.

## What has to be decided

1. **Whether `living_dining_kitchen` remains offerable in the `AZ` profile at
   all.** C5 says flats and houses ship through one code path; nothing says every
   Room type ships in every profile, and the profile has never refused a *type*
   before — only sized one.
2. **If it ships, what the engine says.** An Assumption on the Brief naming the
   electric hob is the cheap answer and it is not obviously the right one: C2's
   Homeowner "cannot read a dimension string", and an appliance-compliance
   footnote is further from them than that. ⚠️ This is also the first time the
   profile would carry a **fixture** consequence rather than a dimensional one,
   and `what_belongs_in_this_block` (ADR 0024) is the membership test that
   decides whether it may live in `room-constraints.json` at all.
3. **Whether `living_dining_kitchen`'s `az_area` mapping is right either way.**
   It currently points at `living_room_2plus` with `referent: part` and
   `compose_with: [kitchen_zone_in_diner]`; the profile's own note already calls
   that mapping under-targeted, and ADR 0034 set the compound targets at rung 2.
4. **Whether `kitchen_dining` inherits anything from this.** It does **not** —
   cl. 4.7 puts it inside `mətbəx`, so it is gas-compliant. Stating that
   explicitly is half the value of the ticket, because the two types are one
   letter apart in every table on this map.

## What this is not

Not a code-compliance claim — C8 forbids one, and this ticket must not turn the
profile into a gas-safety authority. The finding is that a **stated norm** and a
**shipped type** disagree; disclosing that is inside C8, certifying it is not.

Not a change to any area value: `kitchen_zone_in_diner` is ADR 0034's and the
`market_default` tier is ADR 0035's.

⚠️ **`data/standards/room-constraints.json` would be this ticket's THIRD open
claimant** (with 71 and 72). The Notes' concurrency rule applies: do not start
this while either of those is claimed.

## Raised by

*The market tier has an Azerbaijani source now* (2026-08-30), whose §6.5 read the
gas norm first-hand and found the finding unowned.
