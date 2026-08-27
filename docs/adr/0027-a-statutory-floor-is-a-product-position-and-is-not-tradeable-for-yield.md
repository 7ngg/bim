# ADR 0027 — A statutory floor is a product position, and it is not tradeable for yield

Status: **accepted** · 2026-08-28 ·
[The statutory floor now has a price, and it is not the one it was posted at](../wayfinder/tickets/55-does-the-statutory-floor-stay-hard-now-that-it-has-a-price.md)

## Context

ADR 0015 fixed how a rule's *severity* is read where the rule has a parse-time
pre-image. It says nothing about what happens when a hard rule turns out to cost
something, because until now none of them had a measured price on engine output.

`dim.statutory_min_area` does. *A statutory floor, posted soft, in the one region
v1 ships* made it hard and accepted an explicitly unmeasured risk, naming its own
revisit condition:

> If the first Proposer run shows the warp systematically undershooting per-room
> area, this rule collapses yield.

*The warp has never been measured against a stated target area* fired that
condition inside a week, and *The sizing rung under-delivers* corrected the
figure. Same sample, same seed, both rig defects fixed:

| | |
|---|---:|
| candidates losing a Room below its hard floor | **25,5 %** |
| Briefs with **no** clearing candidate, pool of 8 | **3,6 %** |
| kitchens delivered under 8,0 m² when asked for 9,0 | **17,4 %** |
| for scale — ADR 0018's Brief-level loss from *every* dimensional decline | 6,9 % |

So the question arrived in the shape every product eventually meets it in: **a
correctness rule with a yield price, and a one-field edit that buys the yield
back.**

## Decision

**A statutory floor is not priced against yield, and `dim.statutory_min_area`
stays hard at all five limbs.** More generally, and this is the part that
generalises past this rule:

> **Where a hard rule is the thing that distinguishes this engine from what the
> market ships, its cost is a debt owed by whichever stage produced the failure —
> never a reason to weaken the rule.** The rule names the standard; the stage that
> misses it owns the miss.

Ticket 50's asymmetry argument is the *mechanism* of that position, not a
competing one: hard-too-strict is discovered and rolled back, soft-too-lax ships.
This ADR records the reason the rollback lever exists and is still not pulled.

## What the market does, which is the whole argument

`competitive-landscape.md` §5.2, its own heading: **code compliance is claimed by
six vendors and implemented by approximately zero.** Eleven products surveyed,
$0–$20k/yr. The mechanisms, verbatim from the vendors:

| product | claim | mechanism |
|---|---|---|
| Snaptrude | *"generates compliant massing"* | **an LLM reads a PDF the user uploaded.** Never touches the geometry |
| Maket | a "zoning regulations" feature | **LLM document Q&A.** ToS: output *"cannot be used for construction, permitting, or regulatory approval"* |
| Finch | *"per firm standards and local codes"* | **user-authored graph rules** |
| ARCHITEChTURES | *"regulatory confidence"* | **the user enters the regulations. There is no code database** — and *"the designer is responsible for compliance with regulations"* |
| Synaps | — | ToS: *"the Services are not tailored to comply with industry-specific regulations… you may not use the Services"* |
| Forma | no compliance claim | sells environmental analysis |

Read as a set, the pattern is not that compliance is hard. It is that **nobody
has curated a code and bound it to geometry**, so every vendor either pushes the
authoring onto the user or disclaims in the terms. A fast-growing adjacent
segment — Kestrel Labs and others — sells compliance *checking* as a separate
product **inside Revit**, which is the market conceding the same gap from the
other side.

This engine's `dim.statutory_min_area` is the opposite of all of it: **transcribed
first-hand from AzDTN 2.7-2 cl. 5.7, `conf: verified`, and enforced on the
polygon** — at site `both`, so the solver posts it and the validator checks it.
It is a small rule and it is the only instance of the thing the market has not
built.

**That is why 3,6 % does not buy it.** Trading it for yield does not make the
product 3,6 % better; it moves the product into the category every competitor
already occupies, and the category is defined by not doing this.

## Why this is not a compliance claim, which C8 forbids

C8 forbids *claiming* code compliance and says nothing about *being* compliant.
The two are separated by where the text appears, not by what the geometry does:

- The rule is `hard`, so a failing Plan is **discarded and never shown**. There is
  no annotation, no badge, no "AzDTN-compliant" mark anywhere in the surface.
- No Homeowner-facing message on this rule names a law. Everything the Homeowner
  reads is arithmetic about areas — *your Envelope cannot hold n otaq* — including
  `brief.md` bound 9's new parse-time sentence.
- The differentiator is therefore **real and unadvertised**. It shows up as plans
  that are quietly buildable, not as a claim someone could rely on.

Shipping a 3,1 m² bedroom into a market whose law says 10 is the failure C8 exists
to prevent, seen from the other side.

## Why the price could not have been paid by moving the rule

Three candidates were priced and each fails for its own reason.

**Soft.** A soft rule too lax **ships**: a 6,6 m² kitchen reaches a Baku Homeowner
as a *survivor*, unannotated and — under C6, which shows survivors — indis­tin­guish­able
from a good one. C2's *"would I live here"* cannot catch a kitchen that is
plausibly drawn and 1,4 m² short. This is the failure with no detector.

**Drop the kitchen limb.** It is **16,88 of the 19,98** marginal corpus points and
the limb the warp actually fails, so it is the only one worth dropping — and
dropping it does not lower the kitchen floor, it **removes** it. The ergonomic
`kitchen.min_area` is **1,8 m²**, a 900 × 2100 mm galley strip. A 3 m² kitchen
would clear `dim.min_area`, clear `dim.aspect_ratio_hard`, and be shown.

The kitchen limb's own alarming statistic argues the other way once read
properly: a Swiss p50 of **8,04 m²** against a floor of **8,0** does not mean the
floor is too high, it means the floor sits **exactly where people build**. That is
what a *habitable* minimum is, as against the ergonomic *fits* minimum. A limb
landing on the corpus median is working.

**Lower the value.** Not available and not wanted: the value is transcribed, and
composing or discounting a number a regulator wrote down is inventing law —
`CONTEXT.md`, **Statutory floor**.

## Where the cost goes instead

To the stage that produced it. The 17,4 % is **not reachable by any sizing
constant**: *The sizing rung under-delivers* vindicated `f = 0.0575` and landed
Σ Space at **+0,4 %** of the stated floor, so what remains is the warp's per-room
**distribution**, which a perfect level leaves intact.

The precedent is already on this map and it is the same object seen from the same
side. `acceptance-bar.md` §7.5 handed `win.habitable_has_window`'s **45,19 %**
*"to the retrieval and conversion side, not paid for by weakening a statutory
rule"* — twelve times this cost, same disposal.

⚠️ **And the price is an upper bound.** 3,6 % is measured at **pool-of-8**;
`proposer.md` §2.2.7 states that the fidelity sample is the 2,317 converted
dwellings of the ADR 0016 sample, *"so a pool of 87 in production is a pool of 8
here"*, against a production median pool of **86.6** at 4–6 rooms and **58.7** at
7–10. The pool-level correlation that would have defended reading it straight was
driven by the shared *level* error, which is now gone and has not been re-read.

## Consequences

1. **A hard rule that is a differentiator is not a tuning knob.** The next time a
   measured price arrives against one, the question is *which stage owes this*,
   not *what does the rule cost*. The knob still exists — ticket 50's one-field
   rollback — and this ADR is the reason it stays unturned while a stage owes.
2. **A rule can be a product position, and this map now has a term for that
   class.** Nothing else in `rules.json` is one. `dim.min_area` is correctness with
   no market content; `dim.aspect_ratio_hard` is a look; `win.area_ratio` is a
   habitability rule with a statutory *source* but no market gap behind it. Do not
   generalise this ADR to those.
3. **The starved Brief becomes a product problem rather than a rule problem**, and
   it is answered by search and by source B — `acceptance-bar.md` §11.1's
   escalation — never by the reject set. ⚠️ The escalation's second step routes to
   a source whose per-room absolute area fidelity is **unmeasured**.
4. **The differentiator is only as good as the transcription.** It rests on one
   first-hand reading of AzDTN 2.7-2 cl. 5.7 in
   `experiments/finish-layer/out/azdtn_2_7_2.txt`. If that reading is wrong the
   argument in this ADR inverts completely, and C12's *exactly one profile* means
   there is no second region to catch it.
5. **It does not survive a second region for free.** `AZ` publishes floors; `UK`
   publishes none and so raises nothing. A third profile whose law is *lower* than
   the ergonomic base changes nothing (raising is monotone, C14), but a profile
   whose law is materially higher re-opens the yield arithmetic with a different
   corpus behind it.

## Reversal trigger

Not a yield number. This ADR is refuted if **either**:

- the transcription is wrong — cl. 5.7 does not say what
  `room-constraints.json` records, or the register is not `məcburi`; **or**
- the market position stops being true: a surveyed competitor ships a curated
  code bound to geometry rather than to an uploaded document. Re-read
  `competitive-landscape.md` §5.2 before quoting this ADR a year from now.

A rising price alone is not a trigger — it is a bill for whichever stage produced
it.
