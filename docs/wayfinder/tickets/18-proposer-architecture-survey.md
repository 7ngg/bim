---
id: 18
title: Proposer architecture survey
parent: map
labels: [wayfinder:research]
status: closed
assignee: wayfinder-research-agent
blocked_by: []
---

# Proposer architecture survey

## Question

**What should the proposer actually be?** C10 says the model proposes and the
solver projects. *Solver formulation for layout projection* fixed what the solver
consumes; *Language and runtime split* fixed that the proposer is an
**out-of-process service with its own HTTP+JSON API**, trained by us, on its own
runtime. What remains is the architecture inside that service.

The decision that motivated this ticket: **train a model — but is HouseDiffusion
(or a successor) the thing to train, or is something else a better fit?**

This is an architecture survey against a **fixed contract**, which is why it does
not wait on *Acquire the datasets*. It feeds *What the model proposes, and how it
is trained*, which keeps the training-recipe and does-it-beat-retrieval decisions.

### What the answer is measured against

1. **The Proposal contract.** `docs/research/solver-formulation.md` ends with a
   nine-item "what this formulation requires the Proposal to look like" section.
   Read it first — it is the spec. Note the subtlety: the solver *derives* the
   pairwise separations from the proposed boxes, so the wire format is boxes; what
   the contract demands is that the **implied arrangement** be right. Its headline
   is that the model must be scored on **relative arrangement, not box
   regression**, and must not be trained toward validity at the cost of
   plausibility.
2. **The 24-room case.** This is the case that matters and the case that broke the
   predecessor. Measured on this project's own hardware, HouseDiffusion degrades
   near-linearly outside its 5–8 room regime: 8 rooms 5.8–12.8% overlap, 24 rooms
   **35.8–66.8%**; geometric repair recovers 31% / 7% / **0%**. See
   `../plan-generator-3000-pro-max/docs/phase2_findings.md` and
   `phase3_findings.md`. **C11: strong prior, independently verify before reuse.**
   Note the solver changes what "good enough" means — overlap is now the solver's
   problem, not a disqualifier. Say explicitly what the solver forgives and what it
   does not.
3. **The corpora, as already decided.** *Cross-dataset unification* settled it:
   Swiss Dwellings is the backbone, ResPlan merges under a conditioning tag, RPLAN
   is demoted to optional pre-training, MSD and ProcTHOR are out. Condition on
   `(region, corpus, annotation_provenance)`. Do **not** re-litigate this; take it
   as the training-data given and ask what architecture suits it. Its
   `[DOC]`-tagged claims are provisional until the corpora are opened.
4. **It has to be served.** The proposer is an HTTP service on our GPU. Inference
   latency and VRAM are selection criteria, not afterthoughts — the whole plan
   budget is one proposer call plus a 6.25 s solve per candidate, times N
   candidates.
5. **The cheap baselines are live options.** *Solver formulation* found that
   retrieval and LLM routes are "genuinely sufficient for v1 rather than a
   stopgap". Any trained architecture has to beat them on **relative arrangement**,
   not on a metric that flatters generative models.

### Answer, with evidence rather than a reading list

1. **The candidate set.** Survey what has actually shipped 2020–2026 —
   HouseDiffusion and its successors, HouseGAN/HouseGAN++, graph-conditioned
   transformers, autoregressive sequence models, and whatever the current state of
   the art is. `docs/research/floorplan-generation-stack.md` is the prior pass;
   treat its claims as a starting point, not settled, and correct it where wrong.
2. **Which of them can be conditioned on a Brief.** The Brief carries room
   program, adjacency wishes, and an Envelope. An architecture that only accepts a
   bubble diagram, or only a fixed room count, is a poorer fit however good its
   samples look. State the conditioning interface of each.
3. **Which of them hold up at 24 rooms** — and whether any published result even
   reports beyond ~8. If the literature stops where our hard case starts, say so
   plainly; that is a finding.
4. **Training cost on Swiss Dwellings**, on hardware this project plausibly has:
   parameter count, dataset size needed, wall-clock to converge, VRAM floor. An
   architecture we cannot afford to train is not a candidate.
5. **Inference cost per Proposal** — latency and memory, at the room counts that
   matter.
6. **Licence**, per C9: non-commercial is acceptable, but record the terms of
   weights and code for each candidate.
7. **A recommendation**, with the runner-up named and the condition under which
   the runner-up wins instead.

### Deliverable

A findings doc under `docs/research/`, ending with an explicit recommendation and
a **"what this commits the training runtime to"** section — the input *What the
model proposes, and how it is trained* consumes. Flag anything that contradicts
the existing research docs rather than silently overwriting it.

## Resolution

**Do not train HouseDiffusion or a successor. Train a Brief-conditioned room-set
transformer that emits one box per Brief room** — the conditional graphic-layout
class (LayoutDM/BLT: ~12–25M params, d=512, 4–8 layers, discrete coordinate bins,
masked parallel decoding), with envelope cross-attention, per-room target-area
conditioning, and the `(region, corpus, annotation_provenance)` tokens *Cross-dataset
unification* requires. Synthetic pre-training first, then fine-tune on Swiss
Dwellings + ResPlan with rooms rectangularised.

**Runner-up: retrieval-and-warp** — Graph2Plan's retrieval reimplemented over Swiss
Dwellings, no learned generator at all. It wins outright if *Acquire the datasets*
finds fewer than ~1,000 C5-surviving dwellings with ≥16 areas and synthetic
pre-training does not close the gap, **or** if the trained model fails to beat it on
relation accuracy and validator-passing plans per Proposal.

**HouseDiffusion is disqualified on interface, before any quality argument.** It
**cannot be conditioned on an Envelope** — verified in its own code:
`condition_channels=89` decomposes as 25 room-type + 32 corner-index + 32 room-index,
with no boundary channel anywhere. C4 makes the Envelope part of the Brief, so this
is structural, not a tuning problem.

### Findings that bind other tickets

- **The 24-room case is out of distribution for every corpus, not just every model.**
  Swiss Dwellings as used in published work is ~5k plans at a **mean of 6.20 rooms**;
  ResPlan averages 8.1; RPLAN's maximum is 8; the synthetic corpus that transfers
  best spans 2–10, mean 4.42. **No architecture choice fixes this — only data does.**
  This is the single largest open risk on the proposer, and it displaces "which
  architecture" as the question that matters.
- **Stop measuring overlap. The solver changed the metric.** The solver forgives
  2–8% overlap and 21–27% unassigned floor, but a *scrambled* arrangement makes the
  model INFEASIBLE in <0.1 s, and a **fully-nested room pair contributes no relation
  at all** — the sibling project measured 100% worst-pair containment in 10 of 12
  plans, including in-distribution ones. The quantity that predicts survival is
  **per-pair separation-direction agreement**, and **no published metric measures
  it.** It has to be defined before any architecture can be scored.
- **The proposer is small, cheap, and needs no GPU to serve.** ~20M params, ~2 GB
  VRAM to train, **~10–25 GPU-hours on a free-tier T4**, and **8–16 ms per Proposal**
  (~55–110 ms for a batch of 20) — under 1% of the plan budget against a 6.25 s
  solve. Roughly 16× less training and several hundred times less inference than the
  HouseDiffusion route.

### What this hands to other tickets

- **Acquire the datasets** — gains a **blocking query**: the per-dwelling area
  histogram (SQL in §3.2 of the findings doc). That histogram, not this survey,
  decides between the recommendation and the runner-up. It also answers the map's
  open *"whether the proposer is worth training at all"*.
- **What the model proposes, and how it is trained** — must **define the
  separation-direction-agreement metric**, with *Acceptance validator spec*'s
  validator in the loop. Its training recipe and its beat-retrieval ablation are
  unchanged; its architecture question is now answered.
- **Language and runtime split** — the proposer service needs a **GPU for training
  only**. Inference is CPU-feasible at this size, so the separate service earns its
  place by keeping torch out of the engine image and making the model swappable, not
  because it needs an accelerator.

### C11 corrections to evidence already on the map

- **The predecessor's 35.8–66.8% overlap figure is directionally corroborated but
  magnitude-confounded.** Its villa brief flattened two storeys into one footprint,
  which guarantees overlap independently of room count. Treat the direction as sound
  and the magnitude as unusable.
- **Kuhn and MSD are one group across two papers — not two independent sources.**
  Anything resting on "independently corroborated" needs that weakening. What they
  do jointly establish: rectangles beat polygons on Swiss-Dwellings-derived data, and
  Modified HouseDiffusion scores 11.5–21.8 MIoU at ~25 areas where a plain raster
  U-Net scores 40.6–42.4.

### Honest limits

A second delegated sweep — GSDiff, DiffPlanner, floor-plan RLVR, HypergraphFormer,
FMLM, ChatHouseDiffusion — **failed twice on server errors**, so those remain
`[PRIOR]` and were re-checked only for existence. None is load-bearing: each is
either boundary-only conditioning (disqualified on the same interface test as
HouseDiffusion) or an LLM too large to train or serve here. The findings doc's own
"what this note does not establish" section is the authoritative gap list.

Full findings: `docs/research/proposer-architecture.md`.
