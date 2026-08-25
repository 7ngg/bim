---
id: 44
title: The partition footprint has a mean and no spread
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
blocked_by: []
writes:
  - experiments/thickness-fidelity/
  - docs/research/single-internal-thickness.md
---

# The partition footprint has a mean and no spread

## Question

**One number now carries a hard refusal, and only its centre has been measured.**

`brief.md` §9.4 bound 6 refuses a Brief whose programme cannot fill a **given**
Envelope. A stated `overall_dimension` is a *clear* dimension (ADR 0010), so the
area it fixes is the **interior**, gross of partitions, while Σ Space area is the
interior minus them — and the partition footprint is only known after the solve.
The bound is therefore stated as a pair:

```
refuse when   Σ upper_band  <  interior / (1 + f_hi)
warn   when   Σ upper_band  <  interior / (1 + f_lo)
```

Taking the **high** end for the refusal is what restores ADR 0015's one-way
implication — *every* Plan from this Brief fails, not *some might* — so the
refusal never catches a Brief a thin-walled layout could have rescued.

**`f_hi` and `f_lo` do not exist.** `docs/research/single-internal-thickness.md`
§6.4 publishes the footprint as a share of Σ Space area over 14,063 dwellings and
reports **mean 5.7 %, p50 5.7 %** at the shipped `t_int` of 150 — and nothing
else. So today `f_hi = f_lo = 0.057`, the refusal and the warning coincide, and a
hard refusal rests on a point estimate. `brief.md` §13 says so; that is a
disclosure, not a fix.

## What to do

1. **Report p5 and p95** of the per-dwelling partition footprint at `t_int` 150,
   from the harness that already produced the mean —
   `experiments/thickness-fidelity/`, over the same 14,063 dwellings. This is a
   percentile on a distribution already computed, not a new measurement.
2. **Report it against room count**, because bound 6 bites at **four rooms and
   only there** (`room-area-bands.md` §5.1) and partitions scale with the number
   of rooms. A whole-corpus percentile pooled across 2–24 rooms may be the wrong
   statistic for the one regime the bound fires in. If the split is material, the
   spec should read `f(n)` rather than a constant, and this ticket says so.
3. **State which tail is which.** Bound 6 needs the tail where partitions are
   *large*, because that is the case where Σ Space is smallest and the programme
   is likeliest to fill it — getting the sign wrong inverts a hard refusal.

## Boundaries

- **Does not write `brief.md`.** §9.4 bound 6 already names `f_hi` and `f_lo` and
  reads them; this ticket supplies the values and the caveat, and hands them back.
- **Does not re-derive the estimator.** §3.4 already swept the closing radius and
  found it moves the implied thickness by 8 mm — the estimator is not the free
  parameter, and re-litigating it is not this.
- **Not a `t_int` question.** 150 is settled and measured-vindicated at 4 mm from
  the corpus-optimal 146. This is the spread at the thickness that ships.

## Why it is not just a number

`area.invented_envelope_hard` gates at **5 %** and the footprint is **5.7 %** —
*wider than the gate*, which is the correction *One internal thickness* already
filed against ADR 0010. A quantity that sits on the wrong side of a gate by 0.7
points is one whose spread decides how often that gate misfires, and nobody has
looked. `brief.md` §5 rung 1 now also derives an Envelope from a stated
`target_area` as `interior = target_area × (1 + f)`, so this constant is
**load-bearing twice**: once in a refusal and once in the geometry a Brief
produces.

---

## Handed in by *What the engine says when the Envelope is bigger than the programme* (2026-08-24)

The obligation was written into `brief.md` §12 pointing at *"whoever next runs
`experiments/thickness-fidelity/`"*, and there was no such person: *One wall
weight where a real plan draws three* is about how many weights a **drawing**
prints, not about the footprint's distribution. Ticketed rather than left as an
address nobody lives at.

---

## Resolution (2026-08-25)

**The spread exists, the centre reproduced, and the answer is a table rather than
two constants.**

### The numbers

Measured over **13,967** in-band dwellings at `t_int` 150, share of Σ Space area:

```
p1=2.60  p5=3.53  p10=4.07  p25=4.96  p50=5.75  p75=6.50  p90=7.18  p95=7.71  p99=8.87
mean 5.71   sd 1.27   min 0.59   max 13.34   skew -0.01
```

Bootstrap (2,000 resamples): p5 ∈ [3.48, 3.58], p95 ∈ [7.66, 7.77], p99 ∈ [8.80,
9.03]. Symmetric, not heavy-tailed — p99 is 1.54× the median. A **22 %
coefficient of variation** was hiding behind a point estimate.

### Item 1 — the percentiles, on a sample that had to move

The published 14,063 came from stride 10 **unioned with the floors
`experiments/rectangularise/out/swiss_fit.json` had fitted**. That file is
gitignored and ADR 0016 replaced the fit outright, so the original population is
unreproducible *in principle*, not merely missing. Re-ran at **stride 3,
unconditioned**: 14,966 measured, 13,967 in band — larger than the original and
free of a bias nobody had named, since the old union over-weighted floors that
happened to convert, and ADR 0016 has since shown that conversion preferring small
dwellings by 35 points of yield.

**The centre reproduced anyway**: mean **5.71 %**, p50 **5.75 %** against the
published 5.7 / 5.7; the corpus's own partitions at **4.87 %** against 4.8 %. Two
disjoint samples, one drawn under a conversion that no longer exists, agreeing to
two significant figures. That is a stronger verification than the re-run this
ticket asked for.

### Item 2 — the split is material, and it changes the spec's shape

ρ(n, f) = **+0.379**. Median climbs **4.30 % at four rooms → 6.37 % at ten**. At
n = 4 the bootstrapped p95 interval is [6.73, 6.99]; pooled it is [7.66, 7.77] —
**disjoint**, so not sampling noise.

The ticket asked whether the spec should read `f(n)` rather than a constant. It
should, and both single-constant options fail in opposite directions:

- **pooled** `f_hi` (8.87) is too permissive at n = 4 — it excuses a four-room
  Brief with eight-room partition density, so the refusal misses cases it exists
  to catch and the Homeowner pays the solve to reach a zero-survivor screen;
- **n = 4's own** `f_hi` (8.01) is too strict at n = 9, where the measured p99 is
  9.00 — and that is the expensive error, a refused Brief that was buildable.

Today the second is invisible only because `room-area-bands.md` §5.1 leaves
n = 6–10 fifty-odd m² of headroom. That is a coupling to how §6.1 happens to be
tuned, not a reason to ship a wrong number. So `brief.md` §9.4 now carries an
**eight-row measured table** over C13's 3–10 engine-room gate. No functional form
is fitted: eight rows is smaller than the nine-row `k` table §6.1 already ships,
and a fitted `f(n)` would be the invented number this line of work exists to
avoid. ⚠️ The `n = 3` row rests on 422 dwellings and its p99 on about four of
them; §5.1 finds no three-room mix whose caps bind, so nothing reads it today.

**A premise correction.** The ticket supposed the published 5.7 % was "pooled
across 2–24 rooms". It was not — `analyse.py`'s `load()` already filtered to
C13's 4–10 band and to dwellings holding ≥ 3 m of internal wall. Neither
`brief.md` §5 nor `acceptance-bar.md` §8 said so when quoting it. The restated
figures carry the same filter, stated.

### Item 3 — which tail is which, worked rather than asserted

`interior` is fixed, so Σ Space = `interior / (1 + f)`: a **larger** f means a
**smaller** area to fill, the case a programme is **most** able to fill, and so
the case where the refusal is hardest to earn. The threshold *falls* as f rises.
So `f_hi` is the **upper** tail — restoring ADR 0015's *every Plan from this Brief
fails* — and `f_lo` the lower, which puts the warn on a strict superset of the
refusal, the nesting the pair must have. It comes out right only with this
assignment. On a 95 m² interior: refuse below 88.20 at p95, 89.83 at p50, 91.76 at
p5.

### The one decision that was not a measurement

**`f_hi` ships at p99, not the p95 this ticket named.** The two failure directions
are not equally expensive: `f_hi` too low refuses a buildable Brief and is
unrecoverable, while `f_hi` too high lets a doomed Brief reach the solve, where
`acceptance-bar.md` §11 explains it **in terms of area** — the correct explanation
for this failure, not a wrong one. So the refusal buys the extra order of
magnitude for nothing; `f_lo` stays at p5 because it only moves a warn. Not the
maximum: 13.34 % is one dwelling in 15,000, and a hard refusal resting on the
single fattest record is weaker evidence than a percentile, not stronger.

Market check per the standing constraint: `competitive-landscape.md` records
eleven products and **none refuses anything at parse** — Maket disclaims
"measurements, dimensions, or scale", Cedreo that its output has "no contract
value". The refusal is a capability the market does not have, which is exactly why
a wrong one is the expensive failure.

### Why it was not just a number, priced

At §5.1's commonest four-room mix Σ upper_band is **85.67 m²**, so bound 6 refuses
a four-room Brief whose stated interior exceeds `Σ upper_band × (1 + f_hi)`:

| `f_hi` from | value | refused above |
|---|---:|---:|
| today's point estimate | 5.70 % | 90.55 m² |
| p95, n = 4 | 6.85 % | 91.54 m² |
| **p99, n = 4 — shipped** | **8.01 %** | **92.53 m²** |
| p99, pooled | 8.87 % | 93.27 m² |

The refusal line lands between 90.5 and 93.3 m², inside the ordinary Baku
four-otaq range, and `brief.md` §5's own worked example is a 95 m² flat. The
spread is worth about **2 m² of real flats** at the boundary between *refused* and
*generated*. The warn band it opens is 3.6–4.9 m² on a 95 m² interior against
**0,00 m² today** — under a point estimate bound 6 has no warning at all, only a
refusal.

### Boundary deliberately crossed

The ticket said *"Does not write `brief.md`"*. It does. `brief.md` has **no open
claimant** — 10 and 38 are closed and no open ticket lists it in `writes:` — so
handing `f_hi`/`f_lo` on would have recreated the exact defect that created this
ticket: an obligation addressed to nobody. §9.4's constants, §5 rung 1's `f`, §12's
row and §13's limit are all written here. The concurrency rule is respected: no
other claimant to collide with.

### Two consumers, two statistics

`brief.md` §5 rung 1 derives `interior = target_area × (1 + f)` from the **same**
quantity and needs the **p50**, because sizing a box is a point prediction of
geometry rather than a one-way refusal. A tail there draws the Envelope **1,86 m²
too big** on a stated 95 m². Rung 1 now says so explicitly, so the next reader
does not "fix" the apparent inconsistency.

### Written

- `docs/research/single-internal-thickness.md` — new **§3.5** (the spread, the
  per-`n` table, the sign, the asymmetry argument, the two denominators, the
  second-estimator cross-check); **§6.4** restated on the new sample with the old
  one marked superseded and its unstated filter disclosed; Headline, Reproducing
  and §7 provenance updated.
- `docs/spec/brief.md` — §9.4 bound 6's table and its p99/p5 argument; §5 rung 1
  at `f = 0.0575` with the two-statistics note; §12's row discharged and one new
  obligation raised; §13's limit closed and replaced with a smaller honest one.
- `experiments/thickness-fidelity/footprint_spread.py`, `README.md`.
- `CONTEXT.md` — new **Partition footprint** term. Declared on resolution rather
  than taken quietly; the map records no claimant.

### What is left, and it is smaller than what it replaces

**`f_hi` restores ADR 0015's implication empirically, not provably.** The
implication needs `f_hi` to bound the footprint of *every* Plan the engine can
reach; what is measured is a p99 of **corpus** dwellings, which is a proxy. The
engine's own reachable maximum has never been measured because no Proposer has
been run, and p99 leaves one dwelling in a hundred above the line by construction.
ADR 0015 consequence 5 already names this bound as the map's one near miss, and
that remains true at a hundredth rather than at a point.

### The reason this ticket cost 46 minutes, and the fix

The distribution had been computed once and published as two numbers, with nothing
persisted to read a third off — which is why 38 could only address *"whoever next
runs the harness"*. `experiments/thickness-fidelity/series/footprint_150.csv.gz`
is now **committed**: five columns per dwelling, 479 KB, and
`footprint_spread.py` falls back to it, so every future percentile is answerable
in a second by someone holding neither the 1.09 GB corpus nor a populated `out/`.
Verified by running it with `out/` moved aside — identical percentiles. The
README carries the rule: **if you add a statistic to this study, add its inputs to
the series.**

**No ADR.** 0019 was reserved for this ticket and is not used: the sign is derived
from ADR 0015's own implication rather than traded off, and the one judgement
here — p99 over p95 — is a threshold on a measured distribution, which ADR 0015
consequence 2 already governs. It is recorded in §7's provenance as
`engine_choice` with its argument, which is where a threshold belongs. 0019
returns to the pool.
