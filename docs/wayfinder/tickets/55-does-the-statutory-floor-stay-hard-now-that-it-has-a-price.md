---
id: 55
title: The statutory floor now has a price, and it is not the one it was posted at
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - data/acceptance/rules.json
  - docs/spec/acceptance-bar.md
---

# The statutory floor now has a price, and it is not the one it was posted at

## Question

**`dim.statutory_min_area` is hard, and the argument it was posted on is refuted.**
*A statutory floor, posted soft, in the one region v1 ships* made it hard — living
16 m², `bedroom_double` 10, kitchen 8 — reasoning that `market_default` sits at or
above `statutory_floor` in every reachable AZ cell, so **a Plan that reaches its
soft target clears the rule by construction**.

*The warp has never been measured against a stated target area* measured it. The
premise is true; the conclusion is false, because the warp does not reach the soft
target — it reaches a *proportion* of it. On Briefs whose every target sits at or
above `market_default`:

⚠️ **Every number this ticket was opened with is superseded. Use the right-hand
column.** *The sizing rung under-delivers by four per cent* found two defects in
the rig's Envelope — it eroded a 75 mm ring that ADR 0001 does not lose, and it
let the warp resize the notch, which ADR 0020's guarantee assumes it cannot — and
neither was `f`. Same sample, same seed, both fixed:

| | as opened | **corrected** |
|---|---:|---:|
| candidates losing a Room below its floor | 31,1 % | **25,5 %** |
| Briefs with no clearing candidate in a pool of 8 | 6,7 % | **3,6 %** |
| kitchens delivered below 8,0 m² when asked for 9,0 | 21,8 % | **17,4 %** |
| lower quartile margin of the kitchens that pass | +0,085 m² | **+0,518 m²** |

For scale, ADR 0018 measured **6,9 %** Brief-level loss from *every* dimensional
decline combined. This one predicate costs about **half** that again — not about
as much again, which is what this ticket was opened believing.

⚠️ **Do not take the halving as the whole change.** The kitchen's lower quartile
now clears by 518 litres rather than 85, so *"passing by luck"* no longer
describes it. But **17,4 % of kitchens asked for 9,0 m² are still delivered under
8,0**, and no sizing constant reaches that: it is the warp's own per-room
distribution, which survives a perfect level intact.

⚠️ **And do not reach for 18,8 %.** That was `calib`, which scales the box until
Σ Space hits `target_area` and so hands the rooms margin the Brief does not
entitle them to. A correctly-sized Envelope over-delivers by **0,4 %**, not by the
2,2 % of slack `calib` was buying.

Ticket 50 accepted this risk explicitly and named the trigger:

> A hard rule that is too strict is **discovered** — at build time, on the first
> Proposer run, and rolled back by one field. A soft rule that is too lax
> **ships**.

**The trigger has fired, early and on purpose.** What it does not do is make the
decision: 50's asymmetry argument is still standing and still good, and a rule
that costs 3,6 % of Briefs may well be worth it. That is the question.

## Settle

- **Does it stay hard?** The asymmetry that justified hard is unchanged. What has
  changed is that the cost is no longer hypothetical — and it is **3,6 %**, not
  6,7 %. Weigh them.
- **If it stays hard, what does a starved Brief see?** 3,6 % of Briefs get nothing
  from source A. `acceptance-bar.md` §11 requires the parse-time and no-candidate
  sentences to agree, and there is no bound whose edit resolves this one — the
  Brief was compliant. This may be source B's answer (ADR 0005) rather than a
  message, and if so the map is promising something it has not measured.
- **Is `max(ergonomic, statutory)` the right shape at the Plan site at all?**
  `dim.min_area` rejects 0,19 % of real dwellings and adds 0,00 % to the hard
  union; the statutory half carries the entire cost. A rule whose two halves are
  that unlike may want splitting rather than tuning.
- **Does the Brief owe a per-room pre-image?** ADR 0015 says a parse-time bound
  inherits the severity of the rule it is the pre-image of, and `brief.md` §9.4
  bound 1 bounds only the **sum**. A Homeowner asking for a 6 m² kitchen is
  currently told nothing at parse time and loses every candidate at the validator.
  ⚠️ This is a **new** bound, not an amendment — do not assume it is bound 1's job.

## What this ticket does NOT decide

- **The sizing rung**, which was [56](56-the-sizing-rung-under-delivers-on-the-warp-path.md)
  and no longer blocks this one. ✅ **Closed, and the premise it blocked on was
  wrong in the useful direction**: not *"two fifths of the 30,7 % is one
  constant"* — **none** of it was, `f = 0.0575` stands untouched, and what moved
  was two defects in how the Envelope had been measured. The number to judge is
  the corrected one above.
- **Whether retrieval-and-warp survives as source A.** That is the Proposer row's,
  and `proposer-architecture.md` §7.5 explicitly declines to draw it.

## Raised by

*The warp has never been measured against a stated target area, and a hard rule
now rests on it* (2026-08-27), which supplied the number and did not touch the
severity.
