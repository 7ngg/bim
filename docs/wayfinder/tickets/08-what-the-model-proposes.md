---
id: 8
title: What the model proposes, and how it is trained
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: [4, 6, 12]
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
