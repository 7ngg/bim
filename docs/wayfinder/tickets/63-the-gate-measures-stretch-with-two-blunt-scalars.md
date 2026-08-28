---
id: 63
title: The gate measures stretch with two blunt scalars
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - experiments/warp/
  - docs/spec/proposer.md
---

# The gate measures stretch with two blunt scalars

## Question

**The gate's two dimensional terms buy real fidelity through a mechanism they do
not name, and the quantity they are a proxy for is measurable directly.**

*The rig gate is not the shipped gate* established that total area ±10 % and
envelope aspect ±15 % are worth **8.6 points of decline** — 27.6 % against
36.2 %, paired within one Brief, sign test p = 0.0001 — and a worst-room area
deviation 68 % smaller at p50. It also established **why**, and the why is the
opening. ADR 0020 sizes the box from the *Brief*, so a donor's own area and
aspect never enter the warp's arithmetic at all; what they bound is how hard the
donor's **cut-line frame** has to stretch to reach the Brief's box, and the
stretch is what the ergonomic floor and `dim.aspect_ratio_hard` refuse.

**So the terms are a proxy, and a coarse one.** Three signs, all measured:

1. **The effect is a dose, not a threshold.** Decline runs 28.3 → 30.1 → 40.2 →
   **55.2 %** as the donor moves from inside the aspect tolerance to more than
   four times outside it. A gate is a step function fitted to a ramp, and the
   step is at 1.0 for no reason anyone has measured.
2. **57.9 % of refusals fail one term only.** The conjunction throws away a
   donor that is close on the axis that matters because it is far on the axis
   that may not.
3. **Neither term is the stretch.** Area and aspect together fix a *box*; the
   stretch is a per-axis ratio between the donor's frame extent and that box, and
   two donors with identical area and aspect can carry frames that stretch very
   differently — that is the same distinction *A dwelling with two angles* drew
   between `worst_room_iou` and `frame_residual`.

**And pool depth is the scarce resource, which is what makes this worth asking.**
Under the gate the sample's median pool is **9** at 4–6 rooms and **5** at 7–10,
**14.5 %** of Briefs are blank, and the production index is only ~10× deeper.
*What best-of-pool is worth at production pool depth* showed depth buys about one
point and nothing at all at 7–10 rooms — so more depth is not the lever. **A
better-targeted gate is**: the same fidelity from a pool that refuses fewer
donors, or better fidelity at the same depth. Both land on the band ADR 0013
already calls tight.

**What has to be decided:**

1. **What the stretch quantity is**, stated precisely enough to compute off an
   index record. Candidates: the per-axis ratio of the donor's frame extent to
   the Brief's box extent; the max of the two; the log-ratio; the same measured
   after ADR 0020 fixes `s`. Only some are computable without a warp, and a gate
   term that needs a warp is not a gate term.
2. **Whether it dominates the scalar pair.** The test is a frontier, not a point:
   for each candidate term, the coverage it admits against the decline rate and
   worst-room deviation it delivers, plotted against the ±10 %/±15 % pair's own
   point. `gate_effect.py` already emits per-candidate `d_area`, `d_aspect`,
   decline and `worst_room_dev` per Brief, so the first pass costs no new warps.
3. **Whether it replaces the two terms or joins them.** A third term is more
   refusals, which is the wrong direction. Replacing is the interesting case and
   the one that has to beat the incumbent on both axes to be taken.
4. **What the market does, per the standing instruction.** Graph2Plan conditions
   retrieval on the **boundary itself** rather than on scalar proportions, and
   nothing in the reviewed generator literature gates on an area tolerance. That
   is a strong prior that the scalar pair is a stand-in for a shape distance, and
   a weak one about which shape distance.

## What this is not

Not a re-opening of whether the gate exists — ADR 0018 settled that admissibility
is a hard gate and not a ranking term, on an argument this ticket strengthens
rather than touches. Not the **coverage** question: how many Briefs retrieval
cannot serve at all is §2.2.7's and it is measured. Not `worst_room_iou` or
`frame_residual`, which are donor-**fidelity** fields ranked and gated by
§2.2.4's own reasoning; this is about the *Brief-to-donor* match, which is a
different pair of objects.

## Raised by

*The rig gate is not the shipped gate* (2026-08-28), which had to measure whether
the terms were inert before it could say what the rig's shortcut cost — and found
them decidedly not inert, with a mechanism nobody had written down.


## Resolution

**The stretch has a closed form, it was inside the warp's own model, and it
JOINS the gate rather than replacing the two scalars.** ADR
[0032](../../adr/0032-the-gate-gains-a-sound-third-term-and-keeps-the-two-blunt-ones.md);
`experiments/warp/stretch_terms.py`, joined to the 1,974 candidates
`gate_effect.py` had already warped, **no new warps**.

### 1. What the stretch quantity is

`warp_model` posts `Σ gx = W`, `gx_i ≥ 1` and, per part,
`Σ gx[a:b] ≥ MIN_SIDE[room]`. So for **any** set of parts with pairwise-disjoint
x-spans, `Σ MIN_SIDE ≤ W`. Maximising that sum over disjoint sets is an interval
DP over the record's own index spans — microseconds, pure Python, **no new
dependency** — and gives `W_req`, the smallest box extent this donor's frame
admits at the ergonomic floor. Likewise `H_req`.

```
req = max( W_req / W , H_req / H )      W, H = ADR 0020's box at scale 1.0
```

**It is sound.** `req > 1` is a violated necessary condition of the model the
warp solves, so it implies INFEASIBLE: **103 of 103** measured, no exceptions. It
is not sufficient — the 2-D coupling `wv ≤ 3·hv` and the area objective are
outside it, and 98 candidates with `req ≤ 1` were refused anyway.

**The cut is 1.0 and is not fitted** — it is where the warp's own hard constraint
sits, the licence §2.2.4 gives `frontage_reach` and denies `frame_residual`.

### 2. Whether it dominates the scalar pair — no, it is orthogonal to it

It is a much better *decline* predictor and monotone where `d_area` is not:
`req` runs **16.2 → 35.0 → 65.2 → 100 %** across its bands against `d_area`'s
29.9 → 37.4 → **31.6** → 53.3. But decline is not the axis. Best-of-pool
worst-room deviation per Brief, **at the bucket's real 82.4 %-refused
composition** and equal depth `m = 3`, 400 bootstrap draws:

| gate | Briefs served | best-of-pool p50 | p90 |
|---|---:|---:|---:|
| incumbent ±10 %/±15 % | 88.1 % | 0.0596 | 0.2303 |
| **incumbent + `req ≤ 1`** | **89.4 %** | **0.0591** | **0.2294** |
| `req ≤ 1` alone | 89.4 % | 0.0643 | **0.2543** |
| `logd ≤ 0.30` + `req ≤ 1` | 89.1 % | 0.0638 | 0.2333 |

Dropping the pair moves **p90 the wrong way**. The pair buys *proportion*; the
bound buys *feasibility*.

### 3. Replaces or joins — **joins**, and a third refuser is right exactly once

It removes 60 of the incumbent's 987 admitted candidates, **every one a certain
decline**, taking the paired per-candidate rate **27.6 % → 22.9 %** with
identical best-of-pool p50, p90 and served rate in both bands. It is better than
free: `m` is a warp budget and a dead candidate wastes a draw, so at equal `m`
and real composition it takes served Briefs **88.1 % → 89.4 %**. `dim.max_area`
is unmoved — exact upper bound on the breach rate (`dev > k_min − 1 = 1.02`) is
**1.96 %** either way.

**The ticket's own first candidate is pruned rather than measured.** The per-axis
frame-extent ratio is `√(area ratio × aspect ratio)` and
`√(area ratio ÷ aspect ratio)` — `(1 − s)` cancels — a bijection with the
incumbent pair up to the donor's *void* share, agreeing with the incumbent
conjunction on **89.4 %** of candidates. It is the incumbent in polar
coordinates.

### 4. What the market does

Graph2Plan filters on **room types, counts and adjacencies** and ranks by
**boundary similarity, a turning function anchored at the front door**
(`proposer-architecture.md` §770-779). Its shape match is a *rank*, not a gate —
which is a prior for loosening, and the measurement above refuses it. Adopting
the turning function itself needs the donor's boundary polygon, which the index
record does not carry and the frozen `fit_rects.py` pass does not owe. Out for
v1.

### What this cost, and what it did not

⚠️ **`gate_effect`'s population is 50/50 and a production bucket is 82.4 %
refused.** Every §4b/§4c figure in the probe is on the 50/50 draw and the bias
runs *toward* loosening the gate. §4e repairs it by weighting each row by its own
Brief's `n_admitted`/`n_refused` — no new warps. **The §4e rows are the load-
bearing ones and are the only ones quoted here.**

⚠️ **The `m = 8` block is confounded and is printed with that warning on it.**
The urn draws with replacement from at most six warped rows, so each arm
saturates at its own distinct count — the incumbent's three against a loose
rule's six, i.e. best-of-3 against best-of-6, flattering the loose rule by
exactly the quantity under test. **The shipped `m` is 8 and every figure here is
at 3.** A real `m = 8` needs `gate_effect.py --k=8`, ~2 h of warps. Raised as
*What the fourth gate term is worth at the shipped pool depth*.

⚠️ **`req ≤ 0.7` dominates the incumbent on four axes at once on the 50/50
population** — admit 54.0 % against 50.0 %, decline 16.2 % against 27.6 %, dev
p50 0.0845 and p90 0.4398 both better. It is refused: 0.7 is a fitted constant,
the term stops being sound below 1.0, and the population it wins on is the one
§4e exists to correct. **A ticket proposing a `req` cut below 1.0 is re-opening a
decision with all three of those on the record.**
