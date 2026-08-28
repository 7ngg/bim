---
id: 60
title: The rig gate is not the shipped gate
parent: map
labels: [wayfinder:task]
status: open
assignee:
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
