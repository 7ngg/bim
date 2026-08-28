---
id: 57
title: What best-of-pool is worth at production pool depth
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
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

## Added by *A donor's enclosed void becomes area nobody asked for* (2026-08-28)

Two obligations land on `experiments/warp/`, which this ticket holds. Neither
changes what 57 has to settle; both are cheap and both are in the way of doing it
honestly.

1. **`absolute_area.py` has no output for realised unassigned area at all.** That
   is why ADR 0028's measurements had to be made from outside the rig, in
   `experiments/void/`. Σ Space and per-room deviation are reported; the hole
   between the parts is not. Add it on `acceptance-thresholds/`'s standing rule —
   *if you add a statistic, add its inputs to the record* — before the best-of-*m*
   sweep, so the curve is re-readable against it later.

2. **`fit_warp.warp_model` owes two constraints and their INFEASIBLE cost is ONE
   unmeasured number.** ADR 0020's amendment holds the **notch** share at the `s`
   the box was derived from, and ADR 0028 charges the **enclosed void** to its
   receiving Room and weights it. Both constrain the same warp solve. ⚠️ The
   `ring` / `ringmarket` / `ringpool` arms reach the notch invariant by *re-sizing
   the box*, not by constraining the solve, so **no arm on this map has ever run
   the genuinely constrained model**. Measure it once, for both — not twice.

⚠️ **One caution for the best-of-*m* curve itself.** ADR 0028 measured that the
shipped warp objective under-states a receiving Room's deviation on voided
candidates — p50 **0.0652** measured on its parts against **0.0959** measured on
what it will hold after the solver closes the hole. **15.49 %** of the index is
voided, and the population is room-count-skewed (0.55 % at four rooms, 15.79 % at
ten), so a deep pool at 7–10 rooms draws proportionally more of it than a shallow
one. If the curve is fitted on the free objective it is fitted on a number that is
optimistic in exactly the regime the extrapolation cares about.

## Resolution

**Deepening the pool is worth about one point, and §11.1 step 1 is not the
answer it was posted as.** On the published statistic's own convention, an
**eightfold** deepening moves starvation **4,1 % → 3,1 %**; at 7–10 rooms it moves
nothing at all. Below that sits a floor no depth reaches: **π = 2,8 %**
[0,3 – 5,6] overall, **5,3 %** [0,0 – 11,2] at 7–10 rooms.

Full write-up: `docs/research/proposer-architecture.md` **§7.6** (the curve, the
extrapolation, the pool-depth decomposition, the cost) and **§7.7** (the two owed
constraints). Rig: `experiments/warp/{pool_depth,best_of_m,best_of_m_fit,constrained_warp}.py`,
findings and traps in that directory's README.

### The best-of-m curve

200 Briefs, `ringpool` semantics, seed 20260819, nested draw so every point is
paired. `run_pool`'s own convention in bold — it is what 3,6 % was measured on.

| m | 1 | 2 | 4 | **8** | 12 | 16 | 32 | **64** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| every Brief with a pool | 35.2 | 18.6 | 10.1 | **6.5** | 6.0 | 6.0 | 5.5 | **5.5** |
| **`run_pool` convention** | 33.5 | 16.5 | 7.7 | **4.1** | 3.6 | 3.6 | 3.1 | **3.1** |
| 4–6 rooms | 32.6 | 18.5 | 10.9 | 4.3 | 3.3 | 3.3 | 2.2 | **2.2** |
| 7–10 rooms | 37.4 | 18.7 | 9.3 | 8.4 | 8.4 | 8.4 | 8.4 | **8.4** |

**8 is already on the flat part**; ~90 % of what depth can buy is bought by m ≈ 12.
The published **3,6 %** reappears at m = 12–16 against 4,1 % at m = 8 — one Brief
on a different draw permutation, which is the reconciliation.

### Where 87 comes from, and why the sample cannot hold it

`pool_depth.py`, same sample:

| pool definition | p50 4–6 | p50 7–10 | max | empty | ≥ 64 |
|---|---:|---:|---:|---:|---:|
| shipped gate (§2.2.1's bucket, scanned by area+aspect) | **9** | **5** | 51 | 14.5 % | **0 %** |
| what `absolute_area.gate_pool` returns | **81** | **37** | 146 | 0.5 % | 43.5 % |
| production, full 46,794 index | 86.6 | 58.7 | — | — | — |

**§2.2.7's second limit is right about the gate and wrong about the rig.**
`gate_pool`'s primary branch returns the whole multiset bucket and applies the
area and aspect terms only in its by-room-count fallback, so the 3,6 % was drawn
at production *depth* from members the gate would not admit. Both differences were
measured and they pull opposite ways: gated donors are **better** (first-candidate
decline **29.8 %** gated against **35.2 %** bucket) but the gated sample bottoms
out at depth ~10.

**Route 1 — enlarge the converted sample — is not merely expensive, it is
blocked.** `proposer.md` §2.2.1: the conversion is **frozen** until `fit_rects.py`
takes ADR 0031 plus five new fields in one pass, because that re-bases
`swiss_fit_k2.json`. So route 2, fit and extrapolate and label it, was the only
one available.

### The extrapolation, and the model it forced

⚠️ **A plain Beta mixture is wrong in the dangerous direction and was rejected.**
Every `Beta(a,b)` sends `E[p^m]` to zero, so it predicts enough depth serves every
Brief; fitted here it returns **0,45 %** at m = 8 against a measured **8,2 %** —
contradicted by the column beside it, and it would have said *deepen the pool* is
free. The curve has a floor, so the model must be able to express one:

    starvation(m) = π + (1 − π) · B(a + m, b) / B(a, b)

Maximum likelihood over censored observations — a Brief whose pool holds 3 members
is **not** one that survived best-of-32 — with a 200-sample bootstrap:

| | π (the floor) | m = 8 | at production depth |
|---|---:|---:|---:|
| all Briefs | **2,8 %** [0,3 – 5,6] | 4,9 % | **2,8 %** [0,5 – 5,6] at 87 |
| 4–6 rooms | 1,1 % [0,0 – 4,7] | 5,0 % | **1,3 %** [0,0 – 4,8] at 87 |
| 7–10 rooms | **5,3 %** [0,0 – 11,2] | 5,4 % | **5,3 %** [0,0 – 11,2] at 59 |

⚠️ **The intervals are the finding, not decoration.** π is identified by the
*depth* of the censored observations, so a shallow pool cannot pin it: the gated
arm's own fit returns π = 0 with a **zero-width** interval, an artefact of the same
family as the plain Beta. Only the deep bucket can see an asymptote, which is why
the table is fitted on it.

### Is the residual still correlated? — yes, and strongly

*P(candidate j+1 declines | j prior declines)*, flat under independence:

| position | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| decline rate | 35.2 % | 50.7 % | 73.5 % | 66.7 % | 81.2 % | 81.8 % | 88.9 % | 87.5 % |

Ticket 56 removed the shared **level** error and the correlation did **not**
collapse. What remains — the warp's per-room **distribution** — has not thinned
across a pool. So §11.1's steps 2 and 3 are load-bearing and **source B's
unmeasured per-room area fidelity is now the urgent gap**, exactly as this ticket
anticipated.

### What deepening costs

A pool member is a warp **plus** a projection solve. Warp measured here at
**0.79 s** (bucket) / **1.66 s** (gated). Projection solve on a real boundary:
p50 **10,11 s**, p90 at the 15 s cap (`solver-formulation.md` Part V). So 79 extra
members is ~60–130 s of warp but **13–20 minutes of solve**, and it falls entirely
on the starving Brief — the worst possible distribution.

⚠️ **Depth is affordable only if starvation is screenable on the Proposal**, and
whether it is has not been established. `dim.statutory_min_area` is `site: both` —
the solver posts it, the validator evaluates it — and every number here is measured
on the **warped rectangles**, i.e. the Proposal. **No warped Proposal on this map
has ever been put through the projection solve**: `fit_warp.py` imports
`experiments/solver-toy/` for its relation extractor only. So 3,6 % and this whole
curve are *Proposal-level* starvation and the Plan-level figure could fall either
side. Ticketed.

### Obligation 1 — realised unassigned area

`absolute_area.py` reported Σ Space and per-room deviation and never the hole
between the parts, which is why ADR 0028 had to be measured from outside the rig.
`bbox` now decomposes on the record as **Σ Space + erosion + notch + enclosed
void**: every row carries `void_m2`, `notch_m2`, `erosion_m2`, `s_realised`,
`void_realised`, `bbox_m2`, and `summarise()` gained an `unassigned` block with the
donor-to-realised amplification.

⚠️ **Read realised shares off the frame, never the millimetre geometry.**
`notch_share` flood-fills one cell per square millimetre — fine on donor parts,
~80 million cells per plan on solved geometry, and the run never finishes. New
`frame_components` / `realised_frame_areas` do it exactly in O(cells): the
complement's components are fixed by `spans`, since the warp moves gap sizes and
never index spans.

### Obligation 2 — what the two owed constraints cost

194 paired (Brief, donor) cases. **The void half is free; the joint cost is the
notch's cost.**

| arm | INFEASIBLE | lost vs `free` | notch drift p90 | void p90 | worst-dev p50 |
|---|---:|---:|---:|---:|---:|
| `free` — what ships | 10.8 % | — | 0.0910 | 0.375 | 0.1391 |
| `void` — ADR 0028 | 10.8 % | **0** | 0.0923 | **0.250** | 0.1478 |
| `notch` — ADR 0020 | 13.4 % | 5 | **0.0197** | 0.375 | 0.1621 |
| **`both`** | **13.4 %** | **5 — 2,6 %** | **0.0195** | **0.250** | 0.1662 |

ADR 0028 costing zero reproduces `experiments/void/`'s 9/90-on-every-arm. The
notch cost is a function of how hard it is held:

| tolerance | ±0.04 | ±0.02 | ±0.01 | ±0.005 | exact |
|---|---:|---:|---:|---:|---:|
| lost vs `free` | 1,5 % | **2,6 %** | 3,6 % | 3,6 % | **8,8 %** |
| worst-dev p50 | 0.1645 | 0.1662 | 0.1797 | 0.1846 | **0.2256** |

⚠️ **ADR 0020's `s` does not cover all of the notch.** It is the **two largest**
boundary-touching complement components and **27,5 %** of donors have three or
more, so boundary-touching floor exists that is neither notch nor void by the
ADR's own definitions. The cheap encoding (`W*H − Σ parts − void`) holds a strictly
larger region than the ADR names; the table constrains the cells `s` is read off,
which is why its drift tracks the tolerance where the loose one stalled at 0.04.

### Corrections made to `proposer-architecture.md` §7.5

The file was carrying **pre-ticket-56** numbers throughout and it is this ticket's
to hold. The arm table is re-measured (`cross` mean **−2.2 %**, not −4.3 %) and
gains the `ring` row, which is the only arm that enforces ADR 0020's invariant and
the only one to read as what the engine delivers. **Finding 2's headline is dead**:
*"roughly two fifths of the damage is one fixable constant"* was measuring the two
rig defects 56 found — with the ring held, Σ Space lands at **+0,4 %** and no sizing
correction is owed anywhere. Finding 3's pool figure moves 6,7 % → **5,7 %** / 3,6 %.

### The fog patch 46 left this ticket to size

*What a sheared donor costs a warped candidate* was fogged rather than ticketed
because its size was 57's to determine. **It graduates**, as ticket 62, blocked on
59. The fog entry reasoned that a 4-8 deg donor sits at the **10,6th percentile**
of a 58-87 bucket drawing `m = 8`, so nothing draws these donors at shipped depth.
That is right, and right by about one position -- the tenth percentile of a ranked
pool of ~87 is rank ~9 and `m = 8` stops at 8. But the curve above puts the useful
depth at **m ~ 12-16**, and every draw in that range sits below rank 9. The window
worth deepening is exactly the window that starts drawing sheared donors, so the
question is live rather than moot. It waits on 59 for two independent reasons: 59
sets the depth constant, and "yields a worse **Plan**" needs the warp-to-projection
join that 59 owns.

### What this did not decide

- **`dim.statutory_min_area`'s severity** — settled hard by ticket 55 on an
  argument independent of this number. A smaller figure relaxes the escalation; it
  does not reopen the rule.
- **Source B's per-room absolute area fidelity** — §11.1 step 2 depends on it and
  `proposer.md` §6.1 has no term for it. Now the urgent gap.
- **Whether `gate_pool` should be repaired to match §2.2.1.** It is a rig defect
  with a measured direction, and repairing it re-bases published numbers. Ticketed.
