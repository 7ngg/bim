---
id: 87
title: The dwelling floor sits below the only Azerbaijani otaq-indexed figure
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - data/acceptance/rules.json
  - docs/research/az-region-profile.md
---

# The dwelling floor sits below the only Azerbaijani otaq-indexed figure

## Question

**AzDTN 2.7-2 cl. 5.1 / Cədvəl 1 keys dwelling area to the otaq count, the engine's
own floor is below it at every count, and the clause is cited in no shipped
artefact.**

Cədvəl 1's six urban lower bounds are **28 / 44 / 56 / 70 / 84 / 103 m²** — and they
are SP 54 Table 5.1's minimum column **digit-for-digit**. (Cell-to-column pairing was
verified against glyph x-coordinates, not reading order: `pypdf` renders that table
column-major and it is easy to mis-pair.)

Against the engine's Σ of hard minima:

| otaq | engine | Cədvəl 1 urban min | shortfall |
|---:|---:|---:|---:|
| 1 | 26,5 | 28 | **−1,5** |
| 2 | 37,5 | 44 | **−6,5** |
| 3 | 47,5 | 56 | **−8,5** |
| 4 | 57,5 | 70 | **−12,5** |

Below at every count, **widening monotonically**.

## What is NOT wrong, and it matters

⚠️ **No mandatory check is missing, and C8 is not at risk.** AzDTN made three
loosening changes to the figure it inherited: the register is **`tövsiyə olunur`**
— *recommended* — against `az olmamalıdır`, mandatory, five paragraphs later in cl.
5.7; the scope is narrowed to the **state and municipal housing fund**; and a closing
sentence hands the **private fund** to the client. A floor became a band. An
exhaustive sweep of every `az olmamalıdır` and `ümumi sahəsi` across all 30 pages
confirms AzDTN imposes no mandatory whole-dwelling area rule.

So this ticket may not simply post Cədvəl 1 as a hard rule. **C14 permits a profile
to raise a hard floor; it does not oblige it to adopt a recommendation.**

## What is wrong

**Every whole-dwelling bound in `rules.json` is against the Brief's `target_area` —
a user input. None is against any normative figure.** `dim.statutory_min_area` is
per-Space only. `"Cədvəl"` appears **0 times** in `rules.json`, and all 28 `"cl. 5.1"`
hits in `room-constraints.json` refer to **AzDTN 2.7-3**, the *detached-house* norm —
a different document. AzDTN 2.7-2 cl. 5.1 is in no artefact at all.

Since `counts_as_otaq` is explicitly *"what number the copy prints"*, **Cədvəl 1 is
the regulator's own opinion about what that number should buy.** It is the only
Azerbaijani otaq-indexed dwelling-size statement in existence. The engine may decline
it — but today the omission is silent and indistinguishable from an oversight, which
is the state the acceptance bar's own discipline exists to prevent.

## What has to be settled

1. **Whether Cədvəl 1 enters at all, and at what force** — a `warn`, a `soft` term,
   or nothing plus a recorded decline. ⚠️ It is `tövsiyə olunur` and fund-scoped, so
   `hard` needs an argument this ticket does not start with.
2. **Which quantity it would bound.** Cədvəl 1 is a *dwelling* area against an otaq
   count; the engine's comparable figure is a Σ of per-Space minima. Those are not
   the same quantity, and the area convention has to be reconciled before the
   shortfall table above means anything as a rule.
3. **What it would cost.** Unmeasured. ⚠️ The −12,5 at four otaq is **arithmetic over
   two published figures, not a corpus measurement**;
   `experiments/warp/out/dwelling_rooms.json` could supply a real one.
4. **Whether the promise moves instead of the bar.** If the engine can legally emit a
   4-otaq dwelling 12,5 m² under what the regulator recommends, that may be a fact
   about the product copy rather than about the validator.

## What this is not

Not a change to `dim.statutory_min_area`, which is per-Space and settled by ADR 0027
and ADR 0033. Not a C8 breach in either direction — AzDTN's recommendation is not a
legal compliance claim and adopting it would not make one.

## Conflicts

⚠️ Shares `data/acceptance/rules.json` with *A regulator states an aspect rule and
the engine says none does* and *A cap fitted in one country and a target set in
another*. Concurrency only.

## Raised by

*An IfcSpace carries no room use* (2026-09-01). Its item-3 research asked whether the
otaq partition drives statutory arithmetic; SP 54 cl. 5.2 / Table 5.1 does, and the
question of whether AzDTN reproduces it surfaced this. Not taken there: `rules.json`
is outside that ticket's `writes:` set.
`docs/research/az-habitable-room-partition.md`.
