---
id: 86
title: The otaq flag's sourcing is misdescribed in five places and silent in one
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: []
writes:
  - data/standards/room-constraints.json
---

# The otaq flag's sourcing is misdescribed in five places and silent in one

## Question

**`counts_as_otaq` is the unit C13's product promise is stated in, and every clause
number it cites for its own authority is wrong or misassigned.** No flag *value*
changes. The provenance does, in five places, and one type has no provenance at all.

Both norms were read first-hand for this: AzDTN 2.7-2 re-downloaded live from
arxkom (md5 `4b5da47dd11808cd0aef37a75b01b4e9`, byte-identical to the copy prior
research read), SP 54.13330.2022 fetched and extracted, and **every clause number
below read directly off the page rather than inferred by position** — the failure
that burned `room-classification-standards.md` §6.

| # | defect | status |
|---|---|---|
| 1 | `counts_as_otaq_sourcing.per_key` carries **18 rows for 19 types** — `bathroom_combined` has no sourcing row at all | confirmed by direct read |
| 2 | **cl. 5.5, cited 8×** as the habitable authority, is a **basement prohibition**. Its habitable list is a parenthetical gloss AzDTN added — SP 54's matching cl. 5.10 has none | first-hand |
| 3 | **cl. 5.2, cited 7×** as the auxiliary authority, is a **composition requirement** listing five members. The real enumeration is **sec. 3 `yardımçı sahələr`**, seven members, a near-verbatim rendering of SP 54 **3.1.27** — and it is cited **once** | first-hand |
| 4 | `study`'s recorded reason — that `otaq` is an unqualified catch-all — is **wrong**. Sec. 3 defines `otaq` purposively, «bilavasitə yaşamaq üçün», rendering SP 54 **3.1.15**. The purposive test *passes* the study, so the value survives on **stronger** footing than it is recorded with | first-hand |
| 5 | `corridor` and `entrance_lobby` are `conf: verified` and the evidence supports `derived` | first-hand |

**Item 2 and item 3 are the same defect in opposite directions**: the habitable half
is sourced to a storey rule and the auxiliary half to a composition rule, while the
one clause that actually defines the auxiliary set is used once. The flag is
right and its paperwork points at the wrong pages.

## What this ticket must NOT do

⚠️ **No flag value changes, and `kitchen_dining` in particular stays `false`.** The
asymmetry — `kitchen_dining` not an otaq, `living_dining_kitchen` an otaq — is real
and **norm-backed by SP 54**: 3.1.18 `кухня-столовая` is an auxiliary **room** (0
otaq) while 3.1.17 `кухня-ниша` is a **zone** inside a habitable room, so the host
keeps its class (1 otaq). The discriminator is **room versus zone**, not "contains a
kitchen". ⚠️ But **AzDTN deleted the deciding sentence** — SP 54 3.1.27 lists
«кухня (или кухня-столовая)» as auxiliary; AzDTN wrote «mətbəx və ya taxça-mətbəx»
instead, leaving `mətbəx-yemək otağı` in no auxiliary list and then defining it in
sec. 3 as an «otaq». So the shipped value is right under SP 54 and **contradicted by
the AzDTN clause cited for it**. That contradiction is the thing to record, not to
resolve by moving the flag.

## The harder question underneath

**AzDTN uses `otaq` in two irreconcilable senses**, and this ticket should decide
whether the file says so. Sec. 3 defines `mətbəx` as «…nəzərdə tutulmuş **otaq**»,
making the kitchen an `otaq` and contradicting cl. 5.2's auxiliary list. Russian
keeps `комната` and `помещение` apart; Azerbaijani had `sahə` and `yerləşgə`
available and AzDTN used `otaq` anyway. AzDTN also carries the habitable list
**twice, inconsistently** — cl. 5.5's parenthetical against **Cədvəl 6** (cl. 9.2),
which gives «Kitabxana, kabinet» its own ventilation row apart from «Yataq, ümumi və
uşaq otaqları». That is a ventilation classification and does not overturn item 4,
but it is unrecorded counter-evidence sitting against a flag the product promise
rests on.

## What this is not

Not a change to C13's 1–4 otaq promise or to ADR 0013 — that is *The room-count
promise has Azerbaijani evidence now*, which writes those artefacts and this one
does not. Not a change to `is_habitable`, whose divergence from this flag on
`kitchen_dining` is gated by V6 and is correct.

## Conflicts

⚠️ Shares `data/standards/room-constraints.json` with *A regulator states an aspect
rule and the engine says none does*. Concurrency only — either order is fine, not
both at once.

## Raised by

*An IfcSpace carries no room use* (2026-09-01), whose item-3 research read both
norms to test whether the engine's grouping is SP 54's. It is not, and this fell out
of establishing that. Not taken there: `room-constraints.json` is outside that
ticket's `writes:` set. `docs/research/az-habitable-room-partition.md`.
