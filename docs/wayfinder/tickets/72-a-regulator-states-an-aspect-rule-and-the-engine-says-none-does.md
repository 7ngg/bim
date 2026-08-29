---
id: 72
title: A regulator states an aspect rule and the engine says none does
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: []
writes:
  - data/acceptance/rules.json
  - data/standards/room-constraints.json
  - docs/research/room-area-bands.md
---

# A regulator states an aspect rule and the engine says none does

## Question

**AzDTN 2.7-3 cl. 5.1 closes with a proportion rule, it is in no artefact, and
`dim.aspect_ratio_hard`'s own note asserts that no surveyed source states one.**

> «Yaşayış otağının uzunluğunun eninə nisbətən **2 dəfədən çox olmayaraq** qəbul
> edilməsi **tövsiyə olunur**.»
>
> *"It is **recommended** that a living room's length be adopted as **not more
> than 2 times** its width."*

Read first-hand from the PDF arxkom serves — `az-kitchen-diner-whole-room.md`
§12.2, corroborated independently by `az-market-default-against-practice.md`.

The shipped rule is `dim.aspect_ratio_hard` at **3,0**, `conf: fitted`, Swiss
p99.5, corpus cost 2,85 % (ADR 0023). The **soft** threshold fitted beside it is
**2,2** — close to the norm's 2, and nobody noticed, because the norm's rule was
never in the repo to compare against.

**Two defects, and they are different sizes.**

1. **A false sentence in a shipped note.** The rule asserts no surveyed source
   states an aspect rule. One does. Cheap half; a correction, not a decision.
2. **A region profile has a shape rule and the profile has no field for one.**
   `room-constraints.json` carries areas, widths and heights. Aspect is the one
   dimensional axis a profile cannot express, in an engine whose whole business
   is shape.

**What has to be settled:**

1. **Whether 2:1 enters the profile at all, and at what force.** It is
   `tövsiyə olunur` — **recommended**, not `məcburi` — and it is from the
   **detached-house** norm, so it degrades to `conf: derived` / force
   `recommended` exactly as the six `clear_widths_mm` cells do.
2. **What it would cost.** Unmeasured, and it must be measured before anyone
   touches 3,0. ⚠️ C14 permits a profile to **raise** a hard floor; whether an
   aspect cap is a floor in C14's sense is itself a question this ticket must
   answer rather than assume — the profile has never reached a non-area
   predicate before.
3. **Whether it belongs to the soft side instead.** The fitted soft threshold is
   already 2,2. A regulator recommending 2 against a corpus statistic of 2,2 may
   be evidence the soft term is right, not that the hard one is wrong — and that
   reading costs nothing and claims nothing.

## What this is not

Not a change to `dim.aspect_ratio_hard`'s value on the strength of the norm
alone — ADR 0023 fixes how a threshold is placed and requires a published cost.
Not a re-opening of ADR 0007 or of grid erosion.

## Raised by

*A zone floor is posted on the whole room* (2026-08-30), via both of its research
tickets, which found the clause while reading cl. 5.1 for a different reason.
