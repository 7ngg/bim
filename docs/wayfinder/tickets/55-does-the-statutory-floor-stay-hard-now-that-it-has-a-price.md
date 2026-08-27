---
id: 55
title: The statutory floor now has a price, and it is not the one it was posted at
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: [56]
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

| | |
|---|---:|
| candidates losing a Room below its floor | **31,1 %** |
| Briefs with no clearing candidate in a pool of 8 | **6,7 %** |
| kitchens delivered below 8,0 m² when asked for 9,0 | **21,8 %** |
| lower quartile margin of the kitchens that pass | **+0,085 m²** |

For scale, ADR 0018 measured **6,9 %** Brief-level loss from *every* dimensional
decline combined. This one predicate costs about as much again.

Ticket 50 accepted this risk explicitly and named the trigger:

> A hard rule that is too strict is **discovered** — at build time, on the first
> Proposer run, and rolled back by one field. A soft rule that is too lax
> **ships**.

**The trigger has fired, early and on purpose.** What it does not do is make the
decision: 50's asymmetry argument is still standing and still good, and a rule
that costs 6,7 % of Briefs may well be worth it. That is the question.

## Settle

- **Does it stay hard?** The asymmetry that justified hard is unchanged. What has
  changed is that the cost is no longer hypothetical. Weigh them.
- **If it stays hard, what does a starved Brief see?** 6,7 % of Briefs get nothing
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

- **The sizing rung**, which is [56](56-the-sizing-rung-under-delivers-on-the-warp-path.md)
  and blocks this one: about two fifths of the 30,7 % is one constant, and judging
  a severity against a number that is about to move is judging the wrong number.
- **Whether retrieval-and-warp survives as source A.** That is the Proposer row's,
  and `proposer-architecture.md` §7.5 explicitly declines to draw it.

## Raised by

*The warp has never been measured against a stated target area, and a hard rule
now rests on it* (2026-08-27), which supplied the number and did not touch the
severity.
