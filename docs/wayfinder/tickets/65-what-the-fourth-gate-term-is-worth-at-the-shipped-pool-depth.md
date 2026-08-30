---
id: 65
title: What the fourth gate term is worth at the shipped pool depth
parent: map
labels: [wayfinder:task]
status: closed
assignee: claude-65
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

## Resolution

**ADR 0032 is right at `m = 3`, does not transfer to the shipped `m = 8`, and the
probe it named to find that out could not have found it.** The pair is kept and
made **depth-conditional**. ADR 0032 amendment; `experiments/warp/gate_depth.py`,
new; `experiments/warp/README.md`, *What ticket 65 added*. Two seeds, 6 421 warps.

### Before any warp: the prescribed probe cannot answer the question

`gate_effect.strata` drops a Brief unless **both** strata hold `K`, so
`--k=8` keeps a Brief **iff the incumbent pool already holds 8**. Measured over
500 Briefs, and the split is exact rather than approximate:

| incumbent pool | Briefs | kept by `--k=8` |
|---|---:|---:|
| 0 (empty) | 73 (14.6 %) | **0** |
| 1–2 | 98 (19.6 %) | **0** |
| 3–7 | 100 (20.0 %) | **0** |
| 8–15 | 108 (21.6 %) | 108 |
| 16+ | 121 (24.2 %) | 121 |

229 of 500 kept; median admitted pool **17** among the kept against **2** among
the dropped. The ticket's own mechanism is that the gate binds *below* the depth
the engine asks for, so the probe removes **every Brief where the effect can
occur** — 54.2 % of them. On the population it retains, ADR 0032 is confirmed.
**The ~2 h run would have returned "confirmed" and been wrong at population
level.** This cost no solves.

### Item 1 — the answer is neither "confirm" nor "replace"

Each rule draws its own pool over the whole bucket, truncated at `m`, **without
replacement**; only the union is warped. 288 Briefs, seed 20260819:

| gate | served | 95 % CI | p90 |
|---|---:|---|---:|
| incumbent pair | 83.0 % | [78.8–87.2] | 0.1369 |
| ADR 0032's join | 83.0 % | [78.8–87.2] | 0.1285 |
| `req ≤ 1` alone | 97.9 % | [96.2–99.7] | 0.1196 |
| **depth-conditional** | **97.6 %** | [95.8–99.3] | 0.1234 |

The pair admits a median pool of **8** and fills `m` on 51.7 % of Briefs; the
bound admits **52** and fills it on 85.4 %. ⚠️ **ADR 0032's join is the shallowest
of the three** — a conjunction only removes members — and leaves an **empty** pool
on **12.5 %** of Briefs against the pair's 9.7 % and the bound's 0.0 %.

### Item 2 — the falsifiable prediction, confirmed, and it is the whole mechanism

| | pair | `req ≤ 1` | join | **conditional** |
|---|---:|---:|---:|---:|
| pair short of `m` (n = 139) | 64.7 % / 0.2124 | 95.7 % / 0.1820 | 64.7 % / 0.2124 | **95.0 % / 0.1554** |
| pair fills `m` (n = 149) | 100 % / **0.0673** | 100 % / 0.0744 | 100 % / **0.0671** | 100 % / **0.0673** |

**+31.0 points where the pair starves, CIs disjoint; nothing at all where it does
not**, and there the pair holds the best p90 — ADR 0032 reproduced. Repeated at
seed 20260830 (194 Briefs, 2 587 warps) every qualitative claim holds, and the
replacement buys **nothing** on that half's p90 there (0.1922, identical to the
pair) while the conditional arm reaches 0.1369.

### Item 3 — it was a third thing, and it costs nothing

**Apply the pair, count what it admits, top up from `req ≤ 1` only when it holds
fewer than `m`.** Better than the replacement on p90 in **each half on both
seeds**; level on served. It adds **zero warps** — every member it can draw is
already inside `req ≤ 1`'s own first-`m` draw, proved from the crc32 ordering and
then confirmed (`distinct warps needed` unchanged at 3 834).

⚠️ **And it needs nothing from `proposer.md` §2.2**, which replacement would have
stranded on the rank alone. §6.1 gained a fifth term and ADR 0042 under ticket 66
while this ran; neither is touched. The file is owed one prose edit only —
§2.2.4 step 1's pool-size test, amended consequence 6.

### What is NOT claimed

⚠️ **No pooled dominance over `req ≤ 1`.** The per-half p90 advantage is stable on
both seeds; the **pooled** p90 changes sign between them (seed 1: 0.1196 against
0.1234; seed 2: 0.1096 against 0.1179). Not resolvable at this sample size.
⚠️ **The 0.3-point served gap to the replacement is not real** — below the floor
below. ⚠️ Not a re-opening of `req ≤ 1`, not a threshold change, and `m` itself is
not re-decided.

### Three defects found in the rig, two fixed here

1. ⚠️ **CP-SAT at a time cap is not deterministic.** 1 489 pairs warped twice with
   identical inputs: status agreed always, **2.82 % disagreed on `served`**,
   **14.71 % on `dev`**. It surfaced as a bug — a `last wins` dedupe moved the
   same analysis between two reads of one file. **No figure in these rigs may be
   quoted to tenths without reproduction**, and several ADRs do. **Raised as
   ticket 82**, which is where it belongs; dedupe is first-wins and outputs are
   seed-keyed here as a start.
2. ⚠️ **`gate_effect.py`'s per-Brief draw was never reproducible** — seeded with
   `hash()`, salted per process, so ADR 0032 rests on a sample no rerun can
   reconstruct and whose variance can never now be measured. Fixed to `crc32`.
3. ⚠️ **`stretch_terms.incumbent` compares ROUNDED terms**, admitting donors
   `gated_pool` refuses: 1 in 7 827, 1 Brief in 115. Immaterial, recorded.

### Two corrections to this ticket's own earlier reporting

⚠️ **"Reproduces ADR 0032" means the ORDERING and can mean nothing more** — that
sample is unrecoverable. And the absolute gap is **not** evidence of ADR 0037:
re-scoring this data under §4e's **with-replacement** estimator, which makes its
`m = 3` a best-of-**2.11**, closes **77 % of the served gap and 69 % of the p90
gap** on its own, and the residual is **inconsistently signed** across the four
rules — three above, `req ≤ 1` 1.2 points below. A systematic target shift signs
its residuals alike; and 0037 *raised* a floor on 59 dwellings, which moves
`served` the opposite way to the gap observed.

⚠️ **The `market`-arm re-run is therefore NOT discharged and was wrongly reported
as such.** These figures are computed *on* the post-0037 rig, which makes them
current, but MAP.md's debt is a measurement of **what moved**, and no arm here ran
the pre-0037 literals — 0037 deleted them. **The debt passes to 62 and 67
unchanged.**
