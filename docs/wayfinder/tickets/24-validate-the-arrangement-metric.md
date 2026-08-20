---
id: 24
title: Validate the arrangement metric against the solver
parent: map
labels: [wayfinder:task]
status: open
assignee: tng
blocked_by: []
---

# Validate the arrangement metric against the solver

## Question

*What the model proposes, and how it is trained* **defined** the arrangement
metric — per-pair separation-direction agreement, reported as agreement / abstain
/ **confident-wrong**, plus a cycle rate. `docs/spec/proposer.md` §5.

It is a **proxy**, and this map has already been bitten by an unvalidated one:
*Proposer architecture survey* found that overlap — the number the predecessor
project was optimising against — is the wrong metric once the solver forgives
2–8 % of it, and that a fully-nested room pair contributes no relation at all.

So: **does confident-wrong actually predict solve failure?**

**The measurement.** Take ground-truth Proposals — arrangements the solver is
known to project successfully — and inject confident-wrong relations at known
rates. Solve. Show failure rises with the rate, and say how steeply.

Three outcomes and all three are useful:

- **It tracks.** The metric is trusted and both Proposer sources are scored on it.
- **It tracks weakly, or only past a threshold.** Then the threshold is the real
  finding and the metric is reported against it.
- **It does not track.** The metric is **wrong and gets redefined**, not excused.
  Say what to replace it with — the obvious suspect is that the cycle rate, not
  the pairwise rate, is what actually kills a solve.

**What already exists.** `experiments/solver-toy/` — `smoke.py` corrupts
Proposals, `probe2.py` establishes the solver admits the ground truth, `probe5.py`
runs infeasible Proposals and Briefs. Seed 20260817. The harness is there; this is
a new probe against it, not a new experiment.

**Also measure the interaction with abstain.** An abstained pair leaves the solver
free, so a Proposal that abstains on half its pairs should solve *slower* and fail
*less*. If it does not, the abstain half of the metric is meaningless and only
confident-wrong survives.

**Not this ticket.** Fitting **τ**, the confidence margin. It trades solve time
against infeasibility, which is a timing question — it belongs to *Solver timing
variance sweep*. This ticket validates the metric's *shape* at whatever τ the toy
already uses, and hands the sweep whatever it learns about the trade.

**Deliverable.** A probe checked into `experiments/solver-toy/`, its numbers, and
either a confirmation or a redefinition written back into `docs/spec/proposer.md`
§5.
