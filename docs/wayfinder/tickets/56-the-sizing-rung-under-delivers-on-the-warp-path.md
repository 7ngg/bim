---
id: 56
title: The sizing rung under-delivers by four per cent, and f is not where to fix it
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - docs/spec/brief.md
  - experiments/warp/
---

# The sizing rung under-delivers by four per cent, and f is not where to fix it

## Question

**`brief.md` §5 rung 1 sizes the Envelope so that Σ Space lands on `target_area`,
and on the warp path it lands about 4 % short.** Measured by *The warp has never
been measured against a stated target area*, which factored Σ Space ÷
`target_area` at p50 into three terms with three different owners:

| term | owner | `cross` |
|---|---|---:|
| rung inflation `1 + f`, `f = 0,0575` | `brief.md` §5 rung 1 | 1,0575 |
| covered ÷ `interior` | ADR 0020's `s` | 1,0071 |
| Σ Space ÷ covered — the erosion | ADR 0001 | **0,9124** |
| product | | **0,9717** |

Calibrating the box until Σ Space = `target_area` exactly needs **+4,2 %**, and
doing so takes plan-level `dim.statutory_min_area` loss from **30,7 % to 18,8 %**.
So this is not bookkeeping: it is about two fifths of a hard rule's entire cost,
and it sits in one constant in one file.

⚠️ **The obvious fix is wrong.** `f = 0,0575` is the p50 partition footprint of
13 967 *real dwellings* at `t_int` 150 and it is correctly measured as such.
The warp's own tilings lose **8,6 %** to `erode(·, 75)` — about 2,8 points more.
Widening `f` to absorb that would make one number stand for two different
quantities and would silently mis-size the Envelope on the non-warp path too.

⚠️ **And there is a third quantity in play, undocumented.** `fit_rects.py`'s
watershed gives every wall cell to the nearest room within `WALL_REACH = 0.35 m`,
so a converted dwelling's parts cover the interior **plus a band of up to 350 mm
around the whole perimeter** — Σ part area runs **1,25 ×** Σ corpus room polygon
area. That is ADR 0001's centreline convention working correctly, and it is why
`covered ÷ interior` is not 1,0. Any fix that does not name which of the three
quantities it is adjusting will drift against the other two.

## Settle

- **Where does the correction live?** Candidates, none obviously right: a
  warp-path-only inflation term; a per-candidate calibration step after the warp
  (the `calib` arm proves it converges in ≤ 6 iterations); a second published
  constant beside `f` with its own name and its own measurement; or accepting the
  shortfall and letting `area.invented_envelope_hard` catch it — note that gate is
  ±5 % and the p05 plan total is **−16,6 %**, so it will not catch the tail.
- **Is `interior` in ADR 0020 the interior or the solve domain?** ADR 0020 writes
  `box = interior/(1 − s)`; ADR 0001 says the solve domain is the interior
  **dilated by `t_int/2`**. Those differ by ~0,075 × perimeter, ~3 % on a 90 m²
  dwelling — the same order as the whole discrepancy. The ADR does not say which
  it means and both readings are defensible from its text.
- **Does the correction belong to source B too?** A trained proposer emits boxes
  into the same Envelope. If the shortfall is the Envelope's, both sources inherit
  it; if it is the warp's, only one does. The decomposition above says *both* — the
  erosion term is geometry, not retrieval.

## What this ticket does NOT decide

- **`dim.statutory_min_area`'s severity**, which is
  [55](55-does-the-statutory-floor-stay-hard-now-that-it-has-a-price.md) and is
  blocked on this one, because ~3/5 of that rule's cost survives a perfect level
  and the severity should be judged against the number that remains.

## Raised by

*The warp has never been measured against a stated target area, and a hard rule
now rests on it* (2026-08-27).

## Resolution (2026-08-28)

**There is no correction to publish, `f` is vindicated, and the 4,2 % was two
defects in the rig's Envelope — neither of them in `brief.md`.** With the
measurement plane corrected and the candidate's notch share held to the one its
box was derived from, `interior = target_area × (1 + f)` at `f = 0.0575` delivers
Σ Space at **+0,4 %** of the floor the Brief asked for, mean and median.

`experiments/warp/absolute_area.py`, same 600-dwelling sample, same seed, same
`--time=3.0` as ticket 54, so every row below is a paired comparison.

### 1. The rig was eroding a wall that is not there

ADR 0001 tiles the **solve domain** — the Envelope dilated outward by `t_int/2` —
so a tiling edge on the domain boundary erodes back onto the external wall's inner
face and costs no floor. The rig tiled the **Envelope box**, ADR 0020's
`box = interior/(1 − s)`, and then eroded every Room on all four sides. That
charges each dwelling a 75 mm ring around its whole perimeter: **3,7 % of
`interior` at p50**, which is larger than the entire level error this ticket was
raised to explain.

Two independent derivations agree. Geometrically, `0,075 × perimeter ÷ interior`
over the rig's own rows is p50 **0,0365 / 0,0368 / 0,0363** on `self` / `cross` /
`market` — a lower bound, since it ignores the notch's own perimeter. Measured,
the erosion term `Σ Space ÷ covered` moves **0.9124 → 0.9490** on `cross` when the
plane is fixed.

The code said so itself and nobody read it. `part_targets_cells` charged every
part `150 × (w + h) − 22500` of erosion overhead — four sides, perimeter parts
included — which is the same defect one level up, **and it was compensating**: a
perimeter Room was asked for more centreline area than it needed and delivered
more Space than the level implied. That is why fixing the plane alone moves the
*level* a long way and the *yield* barely at all.

Dilating a 250 mm cell frame by 75 mm is below its own quantisation, so the fix
honours the construction on the measurement plane instead: erode the Room's parts
**union the region outside the Envelope**, so a boundary edge is interior to that
union and survives while a shared edge does not. Exactly equal to ADR 0001 for
area, no quantisation, asserted on three hand-checked cases. Enclosed voids are
deliberately excluded — a void is bounded by wall on every side, so its edges cost
erosion exactly as an interior edge does, and `notch_share` already draws that
same line.

### 2. The second defect is not this rig's, and it is a finding about the design

ADR 0020's *"every candidate delivers `interior` of floor by construction"* holds
only if the **realised** notch share equals the recorded `s` the box was derived
from. **`proposer.md` §2.2.3 says the opposite in as many words** — the notch *"is
the part of the bbox no part covers — so it warps along with everything else, for
free"*. It is the one region of the frame carrying no target, so it is a free
sink: correcting §1's overhead released cells and the warp put them in the notch,
taking `covered ÷ interior` to **0.9833**.

This is **not** ADR 0003 consequence 7, which fixes the *entrance edge* — by side,
never by ring index — and says nothing about the notch's dimensions. The two
sentences are compatible and neither implies the other, which is why nothing had
caught it.

Held, the term returns to **0.9986** and the level lands. The `ring`, `ringmarket`
and `ringpool` arms hold it by fixed point on the box rather than by pinning the
cut lines, because pinning means editing `warp_model`, which lives in
`fit_warp.py` and carries ADR 0018's published numbers.

### 3. The measurement

| arm | `cov/int` | `space/cov` | Σ Space ÷ `target_area` mean | p50 | rooms under floor | plans losing one |
|---|---:|---:|---:|---:|---:|---:|
| `self` before | 1.0215 | 0.9143 | −2,30 % | −1,18 % | 5,8 % | 14,8 % |
| `self` after | 0.9908 | 0.9504 | −0,75 % | −0,27 % | 4,9 % | 13,1 % |
| `cross` before | 1.0071 | 0.9124 | −4,27 % | −2,91 % | 13,4 % | **30,7 %** |
| `cross` after | 0.9833 | 0.9490 | −2,19 % | −1,03 % | 12,7 % | 30,5 % |
| **`ring`** | **0.9986** | 0.9504 | **+0,36 %** | **+0,40 %** | **10,1 %** | **24,9 %** |
| `calib` before | — | — | −0,16 % | −0,17 % | 7,5 % | 18,8 % |
| `calib` after | — | — | −0,05 % | −0,02 % | 8,2 % | 22,0 % |
| `market` before | 1.0108 | 0.9141 | −3,11 % | −2,12 % | 10,8 % | 31,1 % |
| `market` after | 0.9882 | 0.9503 | −1,22 % | −0,60 % | 10,3 % | 29,9 % |
| **`ringmarket`** | **0.9986** | 0.9513 | **+0,31 %** | **+0,40 %** | **8,5 %** | **25,5 %** |

`cross before` reproduces ticket 54's published 13,4 % / 30,7 % exactly, and
`calib before` its 18,8 %, so the rig is the same rig and only the two defects
moved.

### 4. The correction to the record, and it is the reason this ticket existed

Ticket 54 §6 factored the level into three terms and concluded *"roughly two
fifths of the damage is one constant in one file, and three fifths survives a
perfect level."* **The first half is wrong and the second half understates.**

- **The `1 + f` term was never at fault.** The two terms beside it were both
  measured on a rig that had the wrong region and a free notch, and correcting
  them lands the level at +0,4 % with `f` untouched. Widening `f` by 4,2 % would
  have oversized every Envelope on **both** proposer paths to compensate for an
  erosion the engine does not perform.
- **`calib` is not "what a correct Envelope delivers".** It scales the box until
  Σ Space hits `target_area`, which hands the rooms margin the Brief does not
  entitle them to; a correct Envelope over-delivers by 0,4 %, not by the 2,2 % of
  slack `calib` was quietly buying. Read as the corrected number, its 18,8 %
  over-stated the gain by half.
- **The honest split is 5,8 points of Envelope defect and 24,9 points of warp.**
  `cross before` 30,7 % → `ring` 24,9 %. Everything that moved was the Envelope's
  and none of it was the rung's; what remains is the warp's own per-room
  distribution, which no sizing constant reaches.

### 5. The three questions the ticket posed

- **Where does the correction live?** **Nowhere.** No warp-path inflation term, no
  post-warp calibration, no second constant beside `f`. The candidates were all
  answers to a shortfall that a correctly-measured Envelope does not have.
- **Is ADR 0020's `interior` the interior or the solve domain?** The **Envelope's
  interior**, at the finished inner face, and it was never a choice between two
  defensible readings. `CONTEXT.md` defines the Envelope as the interior clear
  region and the solve domain as *"not the Envelope, and not the interior"*; `f`
  and `s` are both measured on the finished-face plane; and reading it as the
  domain would apply `s` — a share of the **Envelope's** bounding box — to the
  wrong rectangle. The domain is a **third** quantity, derived from the box by
  ADR 0001, one `t_int` larger on each axis. `brief.md` gains §5.3's three-plane
  table so no reader has to re-derive it.
- **Does it belong to source B too?** The question is moot for a correction that
  does not exist, and the **statement** is source-independent: the domain is a
  property of the Envelope, not of how the boxes inside it were proposed, so both
  ADR 0005 sources inherit it identically. Written into §5.3.

### 6. The number 55 was blocked for

C6 is best-of-pool, so a per-candidate share is not what a Homeowner meets. Run at
`--pool=8` over the **same 194 Briefs** ticket 54 used — same seed, same sample,
every target raised onto `dim.market_default_area`:

| pool arm | starved of 194 | Brief-level loss |
|---|---:|---:|
| ticket 54, as published | 13 | **6,7 %** |
| `pool`, plane fixed, notch free | 11 | 5,7 % |
| **`ringpool`, both fixed** | **7** | **3,6 %** |

**`dim.statutory_min_area` costs 3,6 % of Briefs at pool-of-8, not 6,7 %.** The
rule is roughly half as expensive as the number 55 was given, and the half that
vanished was measurement error in the Envelope, not a threshold anyone could move.

⚠️ **Quote one decimal and no further.** Seven against eleven starved Briefs is
four Briefs; the README's reproducibility limit applies — CP-SAT under a
wall-clock cap gave 5,96 % and 5,78 % on two identical runs of `self` — so treat
anything under a point as noise. The direction and the halving are solid; the
third digit is not there.

For scale, unchanged: ADR 0018 measured **6,9 %** Brief-level loss from every
dimensional decline combined. This one predicate now costs about **half** that
again rather than about as much again, and the two are still not the same Briefs.

### 7. What was written

- **`experiments/warp/absolute_area.py`** — `outside_of` (new), `space_m2` and
  `part_targets_cells` re-based onto ADR 0001's plane, and `hold_ring` with the
  `ring` / `ringmarket` / `ringpool` arms.
- **`experiments/warp/series/absolute_area_pre56_rows.json.gz`** — new, 263 KB,
  five pre-56 arms keyed by name, **committed** on ticket 44's rule: every row of
  the before column above is re-derivable in seconds instead of by a re-run, and
  `out/` is gitignored so a snapshot in it would have been a local-only claim.
- **`experiments/warp/README.md`** — what moved and why, the two defects, and the
  paired table. Plus the rule that matters for the next holder: **read the `ring`
  row and no other as what the engine delivers**, and `calib` is not that row.
- **`docs/spec/brief.md` §5.3** — new. The three planes, the table, why `interior`
  is the Envelope and not the domain, and the source-independence statement. §5
  rung 1's `f` gains its missing **denominator** — it was published as *"the p50
  of Σ Space area"*, which is not a quantity; against the interior the same
  footprint is 5,44 %, and the two differ by half a point of box.
- **`docs/adr/0020-…`** — declared on resolution; it had no claimant. Amendment:
  `interior` is the Envelope, the domain is derived from the box rather than equal
  to it, and the ADR's by-construction guarantee has a precondition that
  `proposer.md` §2.2.3 currently violates.
- **`CONTEXT.md`** — declared on resolution; it had no claimant. **Solve domain**
  gains *derived from the Envelope, per candidate, never equal to it* with an
  `_Avoid_` on tiling the Envelope's own box; **Partition footprint** gains an
  `_Avoid_` on reading any Σ Space shortfall as a wall, since it is the last term
  in the chain and the easiest to blame.

### 8. Handed on, not written

- **`docs/spec/proposer.md` §2.2.3 — the notch may not warp for free.** Its *"so
  it warps along with everything else, for free"* is what makes ADR 0020's
  guarantee false, and it costs **1,5 % of `interior`** and **5,6 points** of
  plan-level `dim.statutory_min_area`. The constraint is one bilinear equality on
  the same gap variables the room areas already use — the realised uncovered area
  equals `s × W × H` — or the fixed point on the box that `ring` uses. That file
  is **ticket 53's** and this ticket did not touch it.
- **`experiments/warp/fit_warp.py` — `warp_model` does not pin the notch.**
  Same finding, one layer down. Not edited here on purpose: it carries ADR 0018's
  published numbers and re-running them is not this ticket's scope.
- **`data/acceptance/rules.json` — the severity is still `rules.json`'s**, and
  the number it should be judged on is now **3,6 % of Briefs at pool-of-8**, not
  6,7 %. That file has no claimant; the severity is
  [55](55-does-the-statutory-floor-stay-hard-now-that-it-has-a-price.md), which
  this ticket unblocks.

### 9. What this ticket did NOT decide

- **Whether `dim.statutory_min_area` stays hard.** 55's, and the reason it was
  blocked on this one has held up exactly: the number it would have judged is
  nearly double the number it will judge.
- **Whether the notch constraint changes the warp's fidelity or its INFEASIBLE
  rate.** The `ring` arms reach the invariant by re-sizing the box, not by
  constraining the solve, so nothing here prices the constraint `proposer.md`
  actually needs. INFEASIBLE was 74/573 on `cross` and 76/573 on `ring` — no
  signal, and not a measurement of the constrained model.
- **Whether the engine's realised partition footprint matches `f` in a solved
  Plan.** The warp's tilings carry **5,37 %** against `f`'s 5,75 %, so on this
  path the rung is mildly conservative and lands +0,4 % over. That is the *warp's*
  tilings, not the solver's, and no Proposer has been run.
