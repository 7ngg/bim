---
id: 65
title: What the fourth gate term is worth at the shipped pool depth
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: []
writes:
  - experiments/warp/
  - docs/adr/0032-the-gate-gains-a-sound-third-term-and-keeps-the-two-blunt-ones.md
---

# What the fourth gate term is worth at the shipped pool depth

## Question

**ADR 0032 is decided at `m = 3` and the shipped `m` is 8.** Every figure in it —
the served-rate gain, both best-of-pool percentiles, the refusal of the
replacement — comes from a bootstrap over `gate_effect.py`'s warps, and that rig
holds **three** distinct candidates per stratum per Brief. Drawing with
replacement past three does not deepen a pool, it repeats it: at `m = 8` the
incumbent arm saturates at best-of-3 while any rule admitting refused members
saturates at best-of-6, and the gap between them is an artefact of the rig's own
`--k`, not of the gate. `stretch_terms.py` prints that block with the warning
attached and ADR 0032 consequence 5 records it as owed.

**It matters in the one direction the ADR could be wrong.** At the confounded
`m = 8` the replacement arm — `req ≤ 1` with the two scalars **dropped** — is the
best row on every axis: served **96.0 %** against 93.3 %, p50 0.0513 against
0.0528, and p90 **0.1626** against 0.1938, with the served CIs disjoint
([95.1–97.3] against [92.4–93.9]). At the honest `m = 3` it is the worst row on
p90. Those two facts have a common explanation and it is not a contradiction:
under the incumbent the production median pool is **9 at 4–6 and 5 at 7–10**
(§2.2.7), so at `m = 8` the gate is **binding below the depth the engine asks
for** in the tight band, and a looser gate is buying draws the incumbent cannot
supply. If that mechanism is real at true depth, ADR 0032's *join, do not
replace* is right at 3 and wrong at 8.

**What has to be measured:**

1. **`gate_effect.py --k=8`**, or a probe of that shape — 16 warps a Brief, ~2 h
   at the 3 s cap. Then re-run `stretch_terms.py`'s §4e at `m = 8` against eight
   distinct warps an arm, not three drawn with replacement.
2. **Whether the incumbent pool actually runs out at 7–10.** The prediction is
   specific: the replacement arm's gain should be concentrated in the Briefs
   whose gated pool holds fewer than `m` members, and near zero elsewhere.
   `pool_depth.py` already reports the depth distribution, so the split costs no
   warps once the warps exist.
3. **Whether the answer is a third thing** — that `m` should be spent differently
   rather than that the gate should move. ⚠️ *What best-of-pool is worth at
   production pool depth* found depth buys about one point and **nothing at all
   at 7–10 rooms**, on `bucket_pool` — a pool where depth was never scarce. That
   curve does not answer this question and must not be quoted at it.

**Deliverable.** Either ADR 0032 confirmed at the shipped depth, or an amendment
that drops the two scalars — which is a bigger change than it looks, because
`proposer.md` §2.2's *"stretch a plan 40 % in proportion and the claim is false"*
argument would then be carried by nothing but the rank.

## Raised by

*The gate measures stretch with two blunt scalars* (2026-08-29), which had to
choose between two rows of its own bootstrap and took the one whose depth both
arms could actually fill.
