---
id: 25
title: The Azerbaijani region profile
parent: map
labels: [wayfinder:research]
status: open
assignee:
blocked_by: []
---

# The Azerbaijani region profile

## Question

*Which region profiles ship in v1* chose `AZ` as the one selectable profile and
**deliberately shipped it empty** — inventing a thickness catalogue in a grilling
session would have produced the 90%-right artefact C2 calls worse than blank. This
ticket populates it, from freely-published primary sources, with every value
carrying the `src` / `ref` / `conf` labels
`data/standards/room-constraints.json` already requires.

Azerbaijan's building norms (**AzDTN**, *Azərbaycan Dövlət Tikinti Normaları*)
derive from the Soviet **SNiP** corpus and its Russian **SP** successors — most
relevantly the multi-apartment residential instrument (SNiP 31-01-2003 /
SP 54.13330) and the dwelling-design and daylight norms around it. Sources are
published rather than paywalled, which is why this profile is buildable where the
DE one was not. Where an AzDTN document cannot be obtained, **name the SNiP/SP
ancestor and label the value `REPORTED`, never `VERIFIED`** — the two are not the
same document and this map has already been bitten twice by a claim that outran
its source.

Deliver every field a profile owns. They were discovered piecemeal across four
closed tickets, so the full list is here:

1. **The wall-thickness catalogue** — `t_int`, `t_ext`, `t_party`, per
   construction type (fired brick, panel, block, monolithic). **This is the
   priority**, because `model.thickness_in_catalogue` is the *only hard acceptance
   rule that reads the region profile*.
2. **Minimum room areas and clear dimensions**, at all three tiers
   (`statutory_floor` / `market_default` / `accessible`). AZ is expected to be the
   **first region where `statutory_floor` is non-null** — SNiP-family norms
   prescribe minimum room areas where German law prescribes none — which gives the
   tier a real consumer for the first time. Record each source's `force` so the
   warn wording can be derived from it rather than from the tier's name; C8 forbids
   claiming a legal floor that is not one.
3. **The window area fraction** for `win.area_ratio` (soft). SNiP-family norms
   state a light-opening ratio against floor area. This also **re-sources
   `win.kitchen_windowless`**, which cites `de_baybo` — a key that has never
   existed in the stub and now points at a deleted region.
4. **Decimal separator** for `DIMDSEP` and every area and dimension string.
5. **Room-name abbreviation table** — the room tag substitutes a *published*
   abbreviation when a name does not fit, never a truncation.
6. **Opening catalogue keys** — user-visible strings; the type marks on the plan
   and the rows of the door and window schedules cite them.
7. **The area measurement convention pair** — *общая площадь* against *жилая
   площадь*. Hand it to *Area measurement convention*; do not decide it here.

## The hard filter, and it is the first thing to check

**Every thickness in the profile must be an even number of millimetres.** ADR 0001
needs `erode(rect, t_int/2)` in integer millimetres; ADR 0004's tier-1 overall
needs `t_party/2`. This is what killed DE: the DIN 4172 octametric series
115 / 365 / 490 is *systematically* odd.

ADR 0006 chose AZ partly on the expectation that the post-Soviet fired-brick series
(**120 / 250 / 380 / 510**, from a 250 × 120 × 65 unit plus a 10 mm joint) and panel
series (**80 / 140 / 160**) are entirely even. **That expectation is `REPORTED` and
unverified — check it before anything else.** If it fails, say so plainly; the
profile absorbs the cost the same way any profile would, and the decision to ship
one region does not depend on it.

## What language the drawing is in

Unasked by any closed ticket and the most product-visible thing here. The
abbreviation table and every room tag need a language: **Azerbaijani** (Latin script
since 1991), **Russian**, or **English**. The three give three different abbreviation
sets and three different sheet-note registers, and *Dimensioning and annotation
rules* already fixed the general notes, three drawn schedules and the title block
that all consume them. Recommend one and say why; note that the drawing is read by a
builder, not by the Homeowner, which is the constituency that should decide it.

## What the corpus can and cannot tell you

Do not re-derive the catalogue from Swiss Dwellings. *Which region profiles ship in
v1* measured it — `experiments/corpus-smoke/wall_thickness_swiss.py`, 199,210 `WALL`
separators — and **there is no module in the corpus**: 59.1% of walls sit within
±2 mm of a multiple of 10 against 50% for uniform noise, and the modal snapped value
holds 5.60%. What the corpus *does* give you is the range a plausible catalogue must
span — p25 109, p50 169, p75 267, p95 440 mm — and that is a sanity check on the AZ
numbers, not a source for them.

## Copyright posture

Unchanged and binding: findings §7.6. Individual values with citations are free;
reproducing a source's own table, its selection and its ordering is not; and
*systematically extracting one work's tables into a data file* (§7.6 item 7) is the
specific failure this project walks into by accident. Prefer the freely-published
regulatory text, re-derive rather than transcribe, and never ship the source PDFs.

Deliverable: `data/standards/room-constraints.json` populated for `AZ` — replacing
the `PLACEHOLDER_NOTE` — with the findings written up under `docs/research/`.
Shares the file with *Ergonomic minima and the constraint table's missing half*,
which owns the region-invariant layer; coordinate rather than collide.
