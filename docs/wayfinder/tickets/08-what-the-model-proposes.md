---
id: 8
title: What the model proposes, and how it is trained
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: [4, 6, 12, 18]
---

# What the model proposes, and how it is trained

## Question

C10 says the model proposes and the solver projects. **Proposes what, exactly —
and how do we get a model that proposes it?**

The proposal is the solver's objective, so its shape is dictated by what the
solver can consume. That is why this waits on *Solver formulation for layout
projection*.

**What is proposed.** Candidates, not mutually exclusive:

- the room **adjacency graph** only — which rooms exist and what touches what
- the graph plus **relative arrangement** — an ordering or a rough partition tree
- the graph plus **rough boxes** — positions and proportions the solver then
  rectifies
- **proportions and area ratios** only, with arrangement left to the solver

Whichever is chosen, state precisely what the solver receives and how it becomes
an objective term.

**Where the proposal comes from.** Three routes, and they can be combined:

- **An LLM.** The adjacency graph is a small, discrete, structured object, and
  LLMs are genuinely good at those. Needs no training, no dataset, and ships
  immediately. It is also already the thing generating the brief (C4).
- **Retrieval** from the corpora — Graph2Plan's genuinely good idea: find the real
  plan closest to the brief and adapt it. No training either.
- **A trained model.** What the project wants. Retrained from scratch per C11;
  architecture reimplemented rather than checkpoint-downloaded.

Decide the v1 route and the eventual route, and be honest about whether the
trained model earns its place over retrieval on measured output — the sibling
project's numbers are a warning about assuming it does.

**If training:**

1. Architecture, reimplemented from which paper, and why that one.
2. Training data — the output of *Cross-dataset unification*. Does region become a
   conditioning variable?
3. Compute. Kaggle's free tier gives ~30h/week of T4×2 or P100; Colab free needs
   checkpointing to survive disconnects. For a graph model over ~17k–45k plans this
   is plausibly sufficient — confirm rather than assume, and state the fallback.
4. **Evaluation.** Not FID on rendered rasters. What number tells us the proposer
   improved the *final, solver-projected, validator-passed* plan? That is the only
   metric that matters, and it needs the validator to exist first.
5. What "done" looks like, so training does not become an open-ended sink.

## What *Acquire the datasets* changed here

The corpora are on disk and the blocking histogram has run. It lands against the
survey's recommendation, so read this before re-deriving the training plan.

**The ≥16-room tail is empty.** Counting rooms a Brief actually names — no
shafts, no cores, no outdoor areas — across both committed corpora:

| Corpus | dwellings | mean | ≥14 | **≥16** | ≥20 | ≥24 |
|---|---:|---:|---:|---:|---:|---:|
| Swiss Dwellings | 46,800 | 6.82 | 164 | **66** | 11 | 1 |
| ResPlan | 17,000 | 6.79 | 14 | **0** | 0 | 0 |

*Proposer architecture survey* §7.3(a) set the trigger at **~1,000**. The answer
is **66**. Its first half fires by a factor of fifteen, so this ticket owns the
second half: **does synthetic pre-training close the relation-accuracy gap at 16+
rooms on held-out data?** If not, the runner-up — retrieval-and-warp over Swiss
Dwellings — wins outright, and the beat-retrieval ablation this ticket already
carries becomes the deciding measurement rather than a sanity check.

**Two consequences the survey could not have stated:**

- **A synthetic generator is no longer the recommended first stage — it is the
  only possible source of ≥16-room training data.** RPLAN's maximum is 8 rooms and
  MSD is a subset of Swiss Dwellings, so no legally obtainable real corpus reaches
  the regime. If this ticket chooses to train, specifying that generator — what it
  emits, at what room counts, and what evidence would show it transfers to real
  dwellings — is part of the training recipe, not a later detail.
- **Per-room target-area conditioning has a data problem in ResPlan.** Its geometry
  is **not in metres** despite its README: polygons sit on a ~256-unit canvas whose
  scale varies per plan (median 0.0545 m/unit, range 0.0014–0.1667, only 3.6%
  within 1% of the median). Metres per unit must be recovered per plan as
  `sqrt(area / polygon_area)`, and seven plans carry a square-feet bug in `area`
  that would poison an area-conditioned loss. Swiss Dwellings is clean — WKT in
  metres. Details in `docs/research/dataset-inventory.md` §2.4.

Usable training volume, stated plainly: **46,800** Swiss Dwellings dwellings
(46,816 unique layouts — floors sharing a `plan_id` are not a duplication problem)
and **16,317** non-augmented ResPlan plans.
