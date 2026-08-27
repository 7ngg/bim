---
id: 54
title: The warp has never been measured against a stated target area, and a hard rule now rests on it
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
blocked_by: []
writes:
  - experiments/warp/
  - docs/research/proposer-architecture.md
---

# The warp has never been measured against a stated target area, and a hard rule now rests on it

## Question

**ADR 0018's headline warp fidelity is a *proportion* result, and the quantity
every downstream decision reads it as is an *absolute area* one.**
`fit_warp.py:373-384` scales the Brief's targets onto the donor's covered area
before comparing, which normalises absolute area away. So the p50 0.056 worst-room
deviation says the warp preserves the *shares* a donor allocates. It says nothing
about whether a Room asked for 12 m² gets 12 m².

*What shape an Envelope is when the Brief does not say* found this and left it as
an obligation on `experiments/warp/` with **no claimant**. It also made the
measurement newly possible: ADR 0020 fixes `interior` before the warp runs, so
there is now a stable denominator to measure against.

**What makes it a ticket rather than an obligation is that a hard rule now rests
on it.** *A statutory floor, posted soft, in the one region v1 ships* posted
`dim.statutory_min_area` **hard** — living 16 m², `bedroom_double` 10, kitchen 8 —
on the argument that `market_default` sits at or above `statutory_floor` in every
reachable AZ cell, so **a Plan that reaches its soft target clears the rule by
construction**. That argument is exactly as good as the warp's ability to deliver a
stated `target_area`, and nobody has measured it.

The same ticket accepted the risk explicitly, and named this as the trigger that
would reverse it:

> A hard rule that is too strict is **discovered** — at build time, on the first
> Proposer run, and rolled back by one field. A soft rule that is too lax
> **ships**.

This ticket is that discovery, brought forward so it happens before the build
rather than during it.

## What to measure

1. **Per-Room absolute area deviation** between a stated `target_area` and the
   Space the warp delivers, over the index — not the proportion `fit_warp.py`
   currently reports. Distribution, not a point estimate: the tail is the whole
   question.
2. **Direction.** A systematic *undershoot* is what kills the statutory rule; a
   symmetric spread does not, because `dim.market_default_area` is two-sided and
   pulls from both sides with fitted weights.
3. **Conditioned on the limb that matters.** The kitchen is where the rule is
   tightest against the corpus — AZ floors it at 8,0 m² and the Swiss p50 is
   8,04 — so the kitchen's deviation is worth reporting on its own.
4. **The yield number.** What share of warped candidates would fail
   `dim.statutory_min_area`, and how that compares to the 15,59 % the shipped bar
   already leaves.

⚠️ **Do not re-measure it as a proportion.** That is the defect, and reproducing
ADR 0018's number would look like confirmation.

⚠️ **`experiments/warp/` imports `solver-toy` read-only** and never edits it, the
arrangement `envelope-exposure/` and `h8-frontage/` already use. It reads
`rectangularise/out/swiss_fit_k2.json` as a **copied-in input**, not as a claim on
that directory.

## What this ticket does NOT decide

- **Whether `dim.statutory_min_area` stays hard.** It supplies the number; the
  severity is `rules.json`'s, and `acceptance-bar.md` §3.1 states what a bad
  result would mean.
- **The engine's own reachable maximum partition footprint**, which
  `brief.md` §13 records as validated against the corpus rather than the engine.
  That one is ruled **out of scope** — it needs the build — and this is not it:
  the warp runs today.

## Resolution (2026-08-27)

**Measured, and the argument does not hold.** `experiments/warp/absolute_area.py`,
600 sampled Briefs over the 2 292 converted Swiss dwellings that join the room
cache. On Briefs whose every target sits at or above `dim.market_default_area` —
the argument's own premise, stated literally — **31,1 % of warped candidates put
at least one Room below `dim.statutory_min_area`**, and **21,8 % of kitchens asked
for 9,0 m² are delivered below the 8,0 m² floor.**

The claim ticket 50 posted the rule on was:

> `market_default` sits at or above `statutory_floor` in every reachable AZ cell,
> so a Plan that reaches its soft target clears the rule by construction.

The premise is true and the conclusion does not follow, because **the warp does
not reach the soft target.** It reaches a *proportion* of it.

### 1. What the rig changes, and why each change was necessary

Three, and each one on its own would have flipped the answer:

1. **No renormalisation.** `fit_warp.py:373–384` scales the Brief's targets onto
   the donor's covered area before comparing. Reproducing ADR 0018's 0.056 would
   have looked like confirmation of a quantity nobody was asking about.
2. **The box is sized as ADR 0020 writes it** — `interior = target_area × 1.0575`,
   `box = interior/(1 − s)` — and **not** tuned until the level came out right.
   Resizing the box to make Σ Space land on `target_area` is the renormalisation
   defect one level up, and the level error turns out to be one of the two things
   this ticket found.
3. **The quantity is the Space, not the part.** ADR 0001: `Space = erode(⋃ parts,
   t_int/2)`; ADR 0010 makes that the finished face, which is the plane
   `dim.statutory_min_area` binds. Erosion costs **8,6 %** of covered area,
   systematically — measuring centreline parts would have biased the answer
   optimistic in exactly the direction that decides the rule.

### 2. Item 1 — per-Room absolute deviation

Distribution, not a point estimate. Per-Room `delivered − target`, in m²:

| arm | plans | p05 | p25 | p50 | p75 | p95 |
|---|---:|---:|---:|---:|---:|---:|
| `self` — candidate is the Brief's own dwelling | 521 | **−2,67** | −0,47 | −0,07 | +0,17 | +1,32 |
| `cross` — real gate-admitted retrieval | 499 | **−5,17** | −1,09 | −0,13 | +0,31 | +3,30 |
| `calib` — `cross`, box scaled so Σ Space = `target_area` | 501 | −3,89 | −0,45 | +0,02 | — | — |
| `market` — every target raised onto `market_default` | 508 | −4,41 | — | −0,10 | — | — |

**`self` is a floor, not an estimate.** Its candidate is the Brief's own dwelling,
so the arrangement already matches the programme exactly and the multiset matches
by construction. Real retrieval cannot do better than this, and `cross` shows it
does roughly twice as badly.

### 3. Item 2 — direction, and it is the bad one

**One-sided.** 57,7–59,0 % of Rooms come in under target in every arm, and the
plan total is systematically short: `cross` delivers a mean **4,3 %** less floor
than asked, p05 **−16,6 %**. This is the case ticket 50 named as fatal. Its
counter-argument — that `dim.market_default_area` is two-sided and "pulls from
both sides with fitted weights" — does not apply to a shortfall that is present at
every percentile below the median and in the plan total.

### 4. Item 3 — the kitchen, conditioned as the ticket asked

AZ floors the kitchen at 8,0 m² against a Swiss p50 of 8,04, so it is the limb
with no headroom, and the measurement agrees:

| arm | kitchens whose target clears 8,0 | delivered below | share | margin p25 (m²) |
|---|---:|---:|---:|---:|
| `self` | 266 | 24 | **9,0 %** | +0,61 |
| `cross` | 244 | 64 | **26,2 %** | **−0,13** |
| `calib` | 246 | 44 | 17,9 % | +0,16 |
| `market` | 499 | 109 | **21,8 %** | **+0,085** |

In `cross` the **lower quartile kitchen is already under the floor**. In `market`,
where every kitchen was asked for 9,0 m² or more, the lower quartile of the ones
that pass clears a hard statutory floor by **85 litres of floor**. A rule passing
by that margin is passing by luck.

### 5. Item 4 — the yield, and the comparison the ticket asked for

**The confound had to be removed first, and removing it is a finding of its own.**
A raw fail share counts Briefs that were below the floor before the warp touched
them — a Swiss dwelling is entitled to a 6 m² kitchen and AZ is not. **Nothing
upstream catches that**: `brief.md` §9.4 bound 1 bounds the **sum** of a Brief's
areas, not any individual Room, so no bound raises a single Room onto its floor.
Every number in §2–§4 above therefore counts only Rooms whose **own stated target
already clears the floor**.

Conditioned that way, per candidate: **13,4 %** of compliant Rooms are pushed
under a floor and **30,7 %** of plans lose at least one (`cross`); **10,8 %** and
**31,1 %** (`market`).

**Against the 15,59 %:** that figure is the share of real Swiss dwellings that
survive the *whole* hard registry. These are not the same quantity and must not be
subtracted — this is one predicate, measured on generated candidates rather than
on the corpus, and it is *additional* to whatever else the bar removes. The one
comparison that is fair is the corpus cost `rules.json` already records for this
rule, **0,5451**, which is what it costs against real Swiss dwellings; against
warped candidates built from compliant Briefs it costs 30,7 %.

### 5a. The number that actually decides it: best-of-pool

A per-candidate share is not what a Homeowner meets. C6 generates many and rejects
most, so the quantity that matters is **how often a whole pool is starved.** Run
with every target raised onto `market_default`, pool of 8, 194 Briefs:

**13 Briefs of 194 — 6,7 % — have no candidate in a pool of eight that puts every
Room at or above its floor.**

**Do not reach for the per-candidate number to get here.** Independence would
predict 0,311⁸ ≈ **0,009 %** against a measured **6,7 %**: a factor of **780**.
That is ADR 0018 consequence 3 reproducing itself on a new statistic — *"declines
are correlated within a pool and must not be compounded… independence would
predict a 10⁻⁶ Brief-level loss against a measured 6.9 %"* — and the correlation
has the same cause, because every candidate for one Brief is now sized from the
same `interior`.

For scale: ADR 0018 measured **6,9 %** Brief-level loss from dimensional declines.
This one predicate costs about as much again, and the two are not the same Briefs.

### 6. The level and the distribution are two defects, with two owners

Σ Space ÷ `target_area` factors at p50 into three terms:

| term | owner | `self` | `cross` | `market` |
|---|---|---:|---:|---:|
| rung inflation `1 + f` | `brief.md` §5 rung 1 | 1,0575 | 1,0575 | 1,0575 |
| covered ÷ `interior` | ADR 0020's `s` | 1,0215 | 1,0071 | 1,0109 |
| Σ Space ÷ covered — the erosion | ADR 0001 | 0,9143 | 0,9124 | 0,9141 |
| **product** | | **0,9877** | **0,9717** | **0,9772** |

which closes against the measured plan totals (−1,2 %, −2,9 %, −2,1 % at p50).
**The erosion term is the one nobody had priced**: `f = 0,0575` was fitted as the
partition footprint of real dwellings, and the warp's own tilings lose **8,6 %**
to `erode(·, 75)` — about 2,8 points more than the rung hands back.

**Calibrating the box until Σ Space = `target_area` needs +4,2 %**, and takes
plan-level statutory loss from 30,7 % to **18,8 %**. So roughly **two fifths of
the damage is one constant in one file, and three fifths survives a perfect
level.** These want different fixes and the severity decision needs both numbers,
which is why the `calib` arm exists.

### 7. Two implementation gates passed, and one precision limit declared

- **The notch-share code reproduces ADR 0020's published table exactly** — p10
  0,0312 / 0,0313, p25 0,0783, **p50 0,1255**, p75 0,1794, p90 0,2330. The sizing
  input is the ADR's own quantity, not a re-derivation of it.
- **`market`'s raw and conditional shares coincide at 0,3110**, as they must once
  every target is raised above its floor and every Room becomes eligible. The
  eligibility filter is doing what it claims.
- ⚠️ **CP-SAT under a wall-clock cap is not reproducible.** Two runs of `self` at
  the identical seed, n and inputs returned 102 and 99 conditional failures out of
  1 712 — 5,96 % against 5,78 %. The seed fixes the sample, not the solution.
  **Quote these to one decimal; treat sub-half-point differences as noise.**

### 8. A defect found on the way, in a file this ticket does not hold

`fit_rects.py`'s watershed gives every wall cell to the nearest room within
`WALL_REACH = 0.35 m`, so a converted dwelling's parts cover the interior **plus a
band of up to 350 mm around the whole perimeter**: Σ part area runs **1,25 ×** Σ
corpus room polygon area. Any arithmetic treating a converted tiling's covered
area as `interior` is off by that band. It is not wrong — it is ADR 0001's
centreline convention doing its job — but it is undocumented, and it is the reason
`covered ÷ interior` is not 1,0.

### What was written

- `experiments/warp/absolute_area.py` — new. Four per-candidate arms plus a
  best-of-pool arm. Writes `out/absolute_area.json` **and every row** to
  `out/absolute_area_rows_<arm>.json`, so a new statistic costs seconds rather
  than the ~15 minutes an arm takes to re-solve.
- `experiments/warp/README.md` — the script's row, its flags, and **four more
  things that will bite**: the proportion trap, the Space-versus-part plane, the
  `WALL_REACH` band, and the reproducibility limit.
- `docs/research/proposer-architecture.md` **§7.5** — new, sited deliberately next
  to §7.4 item 3 (*"whether target-area conditioning is actually learned"*),
  because this is that item's retrieval twin: the runner-up has the same hole and
  it is now the measured one.

### Handed on, not written

- **`data/acceptance/rules.json` — the severity of `dim.statutory_min_area`.**
  This ticket supplies the number and does not touch the severity; that file has
  no claimant. Ticket 50's own trigger has fired: *"a hard rule that is too strict
  is discovered — at build time, on the first Proposer run, and rolled back by one
  field."* It has been discovered before the build, which is what this ticket was
  brought forward to do.
- **`docs/spec/brief.md` §5 rung 1 — `f = 0,0575` is short by about 4,2 % of
  interior on this path.** Held by no one; do not fix it inside `f`, which is a
  measured partition footprint and correct as such. The gap is the erosion of the
  *warp's* tilings, which is a different quantity.
- **`docs/spec/proposer.md` §2.2** — its ⚠️ already says the gate *"bounds the
  total"* and leaves per-room area unconstrained. That worry is now quantified.
  The file is ticket 53's; this ticket did not touch it.
- **Ticket 53** gets its third bullet answered as a by-product: the enclosed void
  is **not** the dominant term in the shortfall — void share of bbox is p50
  **0,0000**, p90 **0,0024**. The level error is the erosion and the rung, not the
  void.

### What this ticket did NOT decide

- **Whether `dim.statutory_min_area` stays hard.** Supplying the number was the
  whole scope; the severity is `rules.json`'s.
- **Whether retrieval-and-warp loses to the trained route.** §7.4 item 3 leaves
  the trained route's own area conditioning unmeasured, so this moves one side of
  a comparison whose other side is still blank.
- **The engine's reachable maximum partition footprint** — ruled out of scope on
  this ticket at charting time, and it still needs the build.
