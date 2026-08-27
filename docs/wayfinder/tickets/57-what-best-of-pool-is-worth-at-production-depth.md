---
id: 57
title: What best-of-pool is worth at production pool depth
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: []
writes:
  - experiments/warp/
  - docs/research/proposer-architecture.md
---

# What best-of-pool is worth at production pool depth

## Question

**The number the acceptance bar's most expensive decision now rests on is
measured at a pool one tenth of production depth, and nobody has said what it
does as the pool grows.**

*The statutory floor now has a price* kept `dim.statutory_min_area` hard at a
measured **3,6 % of Briefs with no clearing candidate**. That figure is
`absolute_area.py` §5a: 194 Briefs, **pool of 8**. `proposer.md` §2.2.7 states
the limit in as many words:

> The pool here is drawn from the 2,317 converted dwellings of the ADR 0016
> sample, not the full index, so **a pool of 87 in production is a pool of 8
> here** — best-of-8 is what was measured and the full index can only do better.

Production median pool, joined per multiset over the full 46,794-dwelling index:
**86.6** at 4–6 rooms, **58.7** at 7–10. So 3,6 % is an **upper bound**, and the
whole of `acceptance-bar.md` §11.1's escalation — whose **step 1 is *deepen the
pool*** — is currently a mechanism with no number attached.

⚠️ **Do not assume it divides out.** `absolute_area.py` §5a's own finding is that
declines are **correlated within a pool**: independence would have predicted
0,009 % against a measured 6,7 %, a factor of **780**, because every candidate for
one Brief is sized from one Envelope. That is ADR 0018 consequence 3 reproducing
itself.

⚠️ **But the correlation's cause has since been removed, and nobody has re-read
it.** The shared component was the *level* error, and *The sizing rung
under-delivers* fixed exactly that — same sample, same seed, Σ Space now lands at
**+0,4 %** of the stated floor. What remains is the warp's per-room
**distribution**, which varies by donor and therefore *should* thin across a pool.
Whether it does is the question.

## Settle

- **The best-of-m curve.** Starvation share against pool depth m, over the sample
  the fidelity arm can actually hold. Where does it flatten, and is 8 already on
  the flat part or still on the slope?
- **How to reach 87 when the sample cannot hold it.** Two routes and they are not
  equivalent: enlarge the converted sample toward the full index, or fit and
  **extrapolate** the best-of-m curve and publish it as an extrapolation. The
  second is cheap and must be labelled as such — this map has a standing rule
  against quoting a modelled number as a measured one.
- **Is the residual still correlated?** Re-measure the pool-level correlation now
  that the level defect is gone. If it has collapsed, deepening the pool is the
  whole answer and §11.1 step 1 carries the case alone; if it has not, steps 2 and
  3 are load-bearing and source B's unmeasured area fidelity becomes urgent.
- **What deepening costs.** Each extra pool member is a warp plus a solve. §11.1
  step 1 spends solve time to buy yield and nobody has priced it against the
  shipped 15 s budget.

## What this ticket does NOT decide

- **The severity of `dim.statutory_min_area`.** Settled hard by
  [55](55-does-the-statutory-floor-stay-hard-now-that-it-has-a-price.md) on an
  argument that does not depend on this number — the asymmetry, §7.5's precedent,
  and the market position. A smaller figure here **relaxes the escalation**, it
  does not reopen the rule.
- **Source B's per-room absolute area fidelity**, which `acceptance-bar.md` §11.1
  step 2 depends on and `proposer.md` §6.1 has no term for. That is the Proposer
  source B row's.

## Raised by

*The statutory floor now has a price, and it is not the one it was posted at*
(2026-08-28), which took the decision without it and recorded the caveat on
`rules.json` as `dim.statutory_min_area.engine_cost.caveat`.
