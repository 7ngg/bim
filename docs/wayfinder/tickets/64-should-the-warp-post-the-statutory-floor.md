---
id: 64
title: Should the warp post the statutory floor
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - experiments/warp/
  - docs/spec/proposer.md
  - docs/spec/acceptance-bar.md
---

# Should the warp post the statutory floor

## Question

**`dim.statutory_min_area` is `site: both` and the warp is neither site.**
*Can a starved candidate be refused before the solve* refused a Proposal-level
**screen** — a filter between the warp and the solve — on three grounds that all
hold. It did **not** decide the different thing: posting the floor as a hard
**constraint inside the warp's own CP-SAT model**, which changes what the warp
*emits* rather than what survives it.

The two are not the same object and only one of the three grounds transfers.

| ground the screen was refused on | does it transfer to a constraint? |
|---|---|
| 82,0 % of what it refuses the solve serves | **no** — a constraint does not refuse, it re-sizes |
| the sound form (Σ floors vs the box) never fires | **no** — that bounds a *screen*, not the warp's gap variables |
| it sits after the expensive step | **no** — the warp *is* the expensive step |

**What it could buy, and the number is small but sits in the worst place.** The
projection refuses **5,1 %** of warped candidates and **every one of them is the
floor** — 14 of 14 re-solve feasible with the statutory limb dropped. By band
that is **2,0 %** at 4–6 rooms and **8,8 % at 7–10**, which is the band ADR 0013
already calls tight, where §7.6 measured that pool depth buys **nothing at all**,
and where the projection's rescue rate is weakest (73,1 % against 91,7 %). It is
the one place on this map where more search does not help and a better-sized
candidate might.

**What it would cost is unmeasured and the machinery exists.** `fit_warp.py`
posts `MIN_SIDE` — a clear **width** floor — hard, plus `dim.aspect_ratio_hard`;
area enters only as the weighted deviation objective. Adding a per-Room area
floor is the same class of move, and `constrained_warp.py` is the rig that prices
exactly this shape: 57 measured ADR 0020's notch invariant and ADR 0028's void
charge posted **in** the solve at **2,6 %** of candidates, rising to 8,8 % if the
invariant is held exactly.

**What has to be decided:**

1. **Whether the warp's own INFEASIBLE rate rises by more than the 5,1 % it
   removes.** The warp already declines candidates at the ergonomic floor
   (`fit_warp` returns INFEASIBLE and retrieval falls to source B, ADR 0005). A
   floor it cannot meet turns a *rescuable* candidate into a refused one, which
   is the screen's failure mode arriving by another door. Measured against
   `project_join.py`'s own arm, not argued.
2. **Whether it damages fidelity where it does not refuse.** The objective is
   worst-room relative deviation plus the weighted sum; a hard area floor
   competes with both. 57's precedent is the shape to expect — the notch
   constraint took worst-room deviation 0.139 → 0.226 when held exactly.
3. **Which floor, and on which plane.** `max(ergonomic, statutory)` is the Room's
   floor, and ADR 0014 binds **area per Room** while the warp's variables are
   per **part**. And ⚠️ the two rigs measure area on planes **3,9 %** apart —
   posting the bar's plane in a warp whose objective is measured on the solver's
   would fit the constraint to the wrong quantity.
4. **What the market does, per the standing instruction.** This is the direction
   the reviewed literature actually points: RLVR (`2605.14117`) puts a hard
   verifier in the training loop and DPLAN (`2606.21159`) constructs feasible so
   constraints hold by construction. Neither gates candidates downstream. That is
   a prior *for* this ticket and it is the half of the market reading that
   *Can a starved candidate be refused before the solve* recorded and did not act
   on.

## What this is not

Not a re-opening of the screen — that is refused with published error rates and
this ticket must not reintroduce it as a constraint's side effect. Not a severity
question: `dim.statutory_min_area` stays **hard**, decided twice (ADR 0027,
`acceptance-bar.md` §3.2). Not the Plan-level best-of-*m* curve, which is
`proposer.md` §2.2.9's owed measurement and is about depth rather than sizing.

## Raised by

*Can a starved candidate be refused before the solve* (2026-08-29), which refused
the filter and found that the only remaining candidate placement is the one step
it never measured.
