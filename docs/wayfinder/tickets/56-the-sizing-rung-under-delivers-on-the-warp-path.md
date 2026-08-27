---
id: 56
title: The sizing rung under-delivers by four per cent, and f is not where to fix it
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
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
