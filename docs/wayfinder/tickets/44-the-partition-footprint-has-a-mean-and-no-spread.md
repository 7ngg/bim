---
id: 44
title: The partition footprint has a mean and no spread
parent: map
labels: [wayfinder:task]
status: open
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
