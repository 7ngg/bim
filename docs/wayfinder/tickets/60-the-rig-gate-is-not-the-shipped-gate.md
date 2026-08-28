---
id: 60
title: The rig gate is not the shipped gate
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
blocked_by: []
writes:
  - experiments/warp/
  - docs/spec/proposer.md
---

# The rig gate is not the shipped gate

## Question

**`absolute_area.gate_pool` does not implement `proposer.md` §2.2.1, and every
warp-fidelity number this map publishes was measured through it.**

§2.2.1 is explicit that the gate is a three-term conjunction: *"the gate's first
term is an exact match, so the bucket is the pool and the other two terms are a
scan of it."* `gate_pool` returns the **whole multiset bucket** the moment it is
non-empty, and applies the area and aspect terms **only** in its by-room-count
fallback. `coverage_restated.py`, on the same corpus, applies all three — which is
why the two disagree about what a pool even is.

*What best-of-pool is worth at production pool depth* measured both, over the same
200-Brief sample:

| pool definition | p50 4–6 | p50 7–10 | max | empty | ≥ 64 |
|---|---:|---:|---:|---:|---:|
| §2.2.1 as written | **9** | **5** | 51 | 14.5 % | **0 %** |
| `gate_pool` as it stands | **81** | **37** | 146 | 0.5 % | 43.5 % |
| production, full 46,794 index | 86.6 | 58.7 | — | — | — |

**The direction is measured and it is not one-sided.** Gate-admitted donors warp
**better** — first-candidate decline **29.8 %** gated against **35.2 %** on the
bucket — so the published per-candidate declines are *pessimistic*. But the bucket
is ~10× deeper, so any statistic that spends depth is *optimistic*. The two effects
land on different published numbers and do not cancel.

**What has to be decided:**

1. **Whether the rig is repaired.** It re-bases ADR 0018's fidelity table, §2.2.7's
   decline rates and §7.5's arm table — all measured through the wrong gate. That
   is a real cost and the answer may be to publish the discrepancy instead.
2. **Whether §2.2.7's second limit survives as written.** *"A pool of 87 in
   production is a pool of 8 here"* is **true of the shipped gate** (9 and 5
   against 86.6 and 58.7) and **false of the rig that produced the number it
   annotates**. At minimum that sentence needs to say which pool it is about.
3. **Whether the ADR 0020 sizing makes the area and aspect terms inert anyway.**
   `run_one` sizes the box from the **Brief's** `target_area` and aspect and takes
   only the donor's cut-line frame and notch share, so a donor's own area and
   aspect are scaled away before the warp sees them. If they are genuinely inert
   *for fidelity*, the rig's shortcut is harmless there and matters only for
   **which donors are in the pool at all** — and that distinction should be
   written down rather than rediscovered.

## Raised by

*What best-of-pool is worth at production pool depth* (2026-08-28), which needed
the pool definition to state its curve and found the two disagreed by a factor of
nine. `experiments/warp/pool_depth.py` is the probe and it is cheap — no warp, no
solve.

## Resolution

**The rig is repaired, the discrepancy is published as well, and the gate's two
dimensional terms turn out to be doing real work through a mechanism nobody had
written down.** The two biases this ticket predicted are both confirmed and they
land on different statistics, so they do not cancel: **per-candidate fidelity was
under-stated by nine points and retrieval's reach was over-stated by a factor of
three.**

Write-ups: `proposer.md` **§2.2.1** (all three terms bind, and why they are not
inert) and **§2.2.7** (the second limit, rewritten as three);
`proposer-architecture.md` **§7.5** (the arm table, re-based) and **§7.6** (the
paired test, and why the bucket is kept). Rig: `experiments/warp/gate_effect.py`
and `gate_sites.py`, new; `absolute_area.py`, `fit_warp.py`, `best_of_m.py`,
`pool_depth.py`, `constrained_warp.py` and `coverage_restated.py` amended;
findings and traps in that directory's README.

### 1. `gate_pool` diverged three ways, not one

`experiments/warp/gate_sites.py`, 2,000 Briefs.

| divergence | measured |
|---|---|
| primary branch skips terms 2 and 3 | **82.4 %** of the pool it handed the warp (108,142 of 131,212) is floor the gate refuses. The median refused donor sits **1.33×** the area tolerance and **1.83×** the aspect tolerance outside — 13 % off in area, 27 % off in aspect. **57.9 %** fail one term only |
| fallback branch skips term **1** | fires on **3.0 %** of Briefs (1.9 % at 4–6, **4.0 %** at 7–10), inventing a pool of p50 14 from a **different room programme**, where §2.2 says *hand the Brief to source B* |
| net effect on blanks | rig blank rate **0.5 %** against the gate's **~13.4 %** |

**Both are repaired.** `gate_pool` is gone, split into **`admissible_pool`** — the
three-term gate, the default everywhere — and **`bucket_pool`**, the pre-60
behaviour, kept and named because the best-of-*m* curve has nowhere else to reach
production depth. `absolute_area.py` takes `--pooldef=gate|bucket` and
`fit_warp.py` takes `--pairing=gate|pre60`, so the published numbers stay
reproducible rather than merely superseded.

### 2. The area and aspect terms are NOT inert, and the mechanism is the frame

Item 3 asked whether ADR 0020's sizing makes them inert. **In the arithmetic,
yes**: `run_one` reads only `brief["aspect"]` and the Brief's targets, and a donor
contributes its parts, types, cut-line frame and notch share — its own area and
aspect never enter. **In fidelity, no**, and it is not close.

`gate_effect.py` splits one Brief's *own* bucket into the members the gate admits
and the members it refuses and warps K = 3 from each — paired within a Brief, so
composition is controlled. 987 candidates an arm over 329 Briefs:

| the donor is one the gate | declined | worst-room deviation p50 | p90 |
|---|---:|---:|---:|
| **admits** | **27.6 %** | **0.097** | 0.491 |
| **refuses** | **36.2 %** | **0.163** | 0.725 |

Sign test on per-Brief decline counts: refused worse on **129** Briefs, admitted
worse on 74, tied 126 — **p = 0.0001**. A **dose, not a threshold**: decline runs
28.3 → 30.1 → 40.2 → **55.2 %** as the donor moves from inside the aspect
tolerance to four times outside it, and 29.9 → 37.4 → 31.6 → **53.3 %** on area.

**The mechanism.** ADR 0020 scales the donor's area and aspect away and then
stretches its **cut-line frame** into the Brief's box. A donor far from the Brief
stretches further, and the ergonomic floor and `dim.aspect_ratio_hard` the warp
already posts are what refuse the result. The terms are a cheap proxy for *how
hard the frame will have to stretch* — which is what they were buying all along,
and not what §2.2 said they were for.

⚠️ **At Brief level the pool absorbs it — p = 0.74** (19 Briefs served only by the
admitted arm, 16 only by the refused, 290 by both, 4 by neither). ADR 0018
consequence 3 again. **Member quality is a per-candidate property**, which is
exactly why the rig's error shows on some published numbers and not others.

### 3. What moved, and what did not

`absolute_area.py` at n = 600, seed 20260819. Pre-60 rows read off ticket 56's own
log — same n, same seed, same statistic — rather than re-run.

| | pool | plans | misses | Σ Space vs target | Rooms under a floor | plans losing one |
|---|---|---:|---:|---:|---:|---:|
| `cross` | bucket | 499 | 27 | −2.2 % | 12.7 % | **30.5 %** |
| `cross` | **gate** | 446 | 88 | **−1.7 %** | **8.5 %** | **21.1 %** |
| `ring` | bucket | 499 | — | +0.4 % | 10.1 % | **24.9 %** |
| **`ring`** | **gate** | **457** | **88** | **+0.5 %** | **6.2 %** | **17.1 %** |

- **`ring` is the row the map says to read, and it improves by 7.8 points.**
  `acceptance-bar.md` §11.1's escalation was priced against an inflated rate.
- **Σ Space does not move** (+0.4 → +0.5 %), so **ticket 56's level result stands
  exactly as written.** This is a distribution correction, which is where §7.5
  finding 2 already said all the remaining damage lives.
- **Starvation goes the other way: `ringpool` 3,6 % → 4,4 %** (22 of 495), because
  the gated pool is ~10× shallower and at Brief level depth is what buys survival.
- **The largest movement is neither**: `briefs_with_no_usable_candidate` is **105
  of 600**. About **one Brief in six** reaches source B rather than a warp, against
  a rig that put it nearer one in twenty.
- **ADR 0018 survives.** `fit_warp.py` carried a **third** pairing defect nobody
  had looked at — a same-multiset Envelope kept without checking area or aspect,
  an off-multiset one kept whenever those two happened to pass, **22.5 %** of
  retained pairs. Repaired and re-run: worst-room **p50 0.111 → 0.095, p90
  unchanged** at 0.471, decline flat 15.8 → 16.4 %. It is robust because that rig
  sizes the box from the donor Envelope *itself*, so even an ungated donor is
  self-consistent. The relation theorem is unmoved under either pairing —
  confident-wrong **0**, severity **0**, reversals **0** — as monotonicity says it
  must be.

### 4. §2.2.7's second limit, rewritten

*"A pool of 87 in production is a pool of 8 here"* is **true of the gate** (9 and 5
against 86.6 and 58.7, and no Brief in the sample holds 64) and **false of the
rig** (81 and 37, at production depth already, 43.5 % of Briefs holding 64+). It
now names its pool in both directions. ~~*"and the full index can only do
better"*~~ is **struck** — §7.6 has the curve flat by m ≈ 12 under a floor no depth
reaches, so the extra depth is worth about one point.

### 5. The cause was duplication, and that is fixed too

Six scripts each carried a private copy of the gate and **three differed from
§2.2.1, in three different ways**. There is now one definition, imported
everywhere. ⚠️ **Four are deliberately NOT unified** — `coverage_restated.py`,
`gate_curve.py`, `room_area_spread.py` and `pool_fidelity.py` gate against a
random same-room-count donor standing in for the Brief, a pre-ADR-0020 convention.
Changing it re-bases **86.6 and 58.7**, the production pool depths quoted across
the whole map, so it is a decision with its own blast radius rather than a
tidy-up. Recorded at the site in `coverage_restated.py` with a *do not fix this*
note.

### Handoff this ticket could not take

⚠️ **ADR 0020's `covered ÷ interior` = 0.9833 is a bucket number.** Gated it is
**0.9853**, so the notch guarantee is worth ~**1,3 %** of `interior` rather than
**1,5 %**. The argument is unchanged. That ADR is *The notch is two components and
a quarter of donors have more*'s file, which already holds it for `s` — take it in
that pass.

### Declared on resolution

`docs/research/proposer-architecture.md` (§7.5, §7.6 — unclaimed) and `CONTEXT.md`
(unclaimed), which gains **Bucket** and an `_Avoid_` on **Retrieval pool**: the
bucket is a *depth* stand-in and never a *membership* one.

### Raised

*The gate measures stretch with two blunt scalars* — the two terms work as a proxy
for frame stretch and are a coarse one: the effect is a dose rather than a step,
**57.9 %** of refusals fail one term only, and neither term *is* the stretch. Pool
depth is the scarce resource at 7–10 rooms, so a better-targeted gate is the lever
that more depth is not.
