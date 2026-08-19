---
id: 8
title: What the model proposes, and how it is trained
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
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

## Resolution

**The Proposer has two sources, and the fork this ticket inherited was a false
one.** Spec at [`docs/spec/proposer.md`](../../spec/proposer.md), ADR
[0005](../../adr/0005-the-proposer-has-two-sources.md). Measurement in
`experiments/retrieval-coverage/`.

### What is proposed: unchanged, with one tightening

*Solver formulation for layout projection* already wrote this spec — exactly *n*
boxes, one per Brief Room, integer Envelope grid units, no validity guarantee, no
adjacency graph. Nothing here reopens it. The one change: **per-pair confidence
goes from optional to required**, because two sources feeding one filter need a
source-independent statement of which relations to trust, and the geometric
margin proxy gives a retrieved plan and a sampled plan the same number for
different reasons. **`source` is deliberately not a Proposal field** — the job
record carries it, so the solver cannot prefer one source and the ablation stays
measurable anyway.

### The route: both, and it is not a hedge

**Source A, retrieval-and-warp** over Swiss Dwellings — ships first, no training,
arrangements that are a real home's by construction. **Source B, the survey's
Brief-conditioned room-set transformer** — always answers. Same Proposal, same
solver, and the Acceptance bar picks survivors. C6 already generates many and
rejects most; nothing ever said they come from one source.

**The measurement that decides it.** Retrieval coverage over all 46,800 Swiss
Dwellings dwellings, in the Brief's own room vocabulary, each Brief taking one
dwelling's programme and a **different** dwelling's envelope — because a
Homeowner's flat shape did not come paired with the rooms they want:

| Brief rooms | briefs | pool = 0 | median pool | pool ≥ 20 |
|---|---:|---:|---:|---:|
| 4–6 | 18,143 | **9.5 %** | 92 | 12,785 |
| 7–10 | 24,785 | **12.4 %** | 66 | 16,619 |
| 11–15 | 1,416 | **67.7 %** | 0 | 78 |
| 16+ | 66 | **71.2 %** | 0 | 0 |

Neither source is production-ready alone. **Retrieval refuses roughly one
common-band Brief in nine** and two in three above ten rooms — not a product that
produces usable plans. **A trained model fails quietly**: it always emits
something, so nothing signals the failure, and it discards 46,800 arrangements
that are correct by construction wherever they apply.

Rejected explicitly, because it was the easiest answer available: **widening the
warp budget until retrieval covers everything.** Retrieval's whole claim is that
the arrangement is real; a plan stretched 40 % in proportion is not, and what
comes out is the 90 %-right artefact C2 calls worse than a blank sheet. ±10 %
area and ±15 % aspect is therefore a **hard admissibility gate, not a ranking
term** — and it is the budget every coverage figure above was measured at.

### Two things cut, and both follow from evidence

**The band v1's Proposer serves is 4–10 Brief-named rooms** — 92 % of the corpus,
where retrieval's median pool is 66–92. That reframes the survey's own trigger:
**§7.3(a) does not fire, because it counted the tail.** *Acquire the datasets*
measured 66 against ~1,000, but v1 no longer promises that band, and in the band
it does promise the corpora hold **~60,600 dwellings against the survey's own
~4,000-record floor — 15×**. What survives is **§7.3(b)**, that retrieval must be
*beaten* rather than assumed inferior — and two sources answer it continuously in
production rather than once in a report.

**Synthetic pre-training is cut from v1.** Its stated purpose was the 12–32 room
regime no real corpus reaches. That regime is out of the promise, so the generator
has nothing left to generate. Training drops from 10–25 GPU-hours to **5–15**. It
returns only if the ceiling is raised.

### Two corpus findings nothing on the map had

**`ROOM` is Swiss Dwellings' most common label — 82,618 rooms, 26 %, more than
`BEDROOM` — and it is not a grab bag.** Measured: p5–p95 **9.9–22.4 m², CV 0.29**
against `BEDROOM`'s 10.0–18.6, CV 0.22, and far tighter than `CORRIDOR` (0.60) or
`STOREROOM` (1.30). It is an *unlabelled private habitable room*. Collapse
`{ROOM, BEDROOM, STUDIO}` → `PRIVATE` for the retrieval key and the training
label, with the Brief's finer type riding as model conditioning. Do **not** collapse
`LIVING_ROOM`/`LIVING_DINING`/`DINING` — open-plan versus separate is real
programme. The collapse cuts distinct multisets 1,190 → 916 and roughly doubles
pool sizes, so **every coverage figure measured before it was pessimistic**.

**`BATHROOM` is ambiguous and the corpus cannot say.** One label spans p5 1.5 m²
to p95 6.3 m² — a WC at one end, a family bathroom at the other — and `dim.min_area`
is a different number for each. Split by area; **the threshold is not set here**,
because *Ergonomic minima* is deriving exactly these fixture footprints and a
second number invented here would be a table to drift against that one.

### The arrangement metric, which *Proposer architecture survey* assigned here

Defined in §5 of the spec. **Per-pair separation-direction agreement**, computed
by the **solver's own extractor** on both sides so it cannot drift from the thing
it predicts. Reported as **three numbers, never one** — agreement, abstain rate,
and **confident-wrong as the headline** — plus a **cycle rate**. An abstain leaves
the solver free; a confident-wrong relation becomes a hard constraint and makes
the model INFEASIBLE in under 0.1 s, so collapsing them into one accuracy figure
hides the only failure that costs a candidate.

**And it must be validated before it is trusted.** This map has already been bitten
by an unvalidated proxy (overlap). Inject confident-wrong relations at known rates
and show solve failure tracks them; if it does not, the metric is wrong and gets
redefined rather than excused. τ is **not set here** — it is the same margin the
solver uses to fix relations hard, and it trades solve time against infeasibility,
so it is a timing question.

### Evaluation: the terminal metric is refused rather than approximated

`hard_pass_rate` needs `dim.min_area`, `dim.min_clear_width` and
`dim.min_clear_depth` — all **hard**, all `conf: pending`, and precisely the rules
a weak Proposal trips. **No partial pass rate is published.** A figure over the 25
fitted hard rules would be an upper bound, and an upper bound with a plausible
name is how a wrong number gets quoted six months later. The **route decision was
scoped so it never depends on it**: coverage and the arrangement metric decide it,
and the beat-retrieval ablation waits for *Ergonomic minima* and *Fit the
ENGINE_CHOICE acceptance thresholds*.

**Stop conditions** so training is not a sink: confident-wrong ≤ retrieval's on
Briefs retrieval covers; no collapse on the ~11 % it blanks; and, once the minima
land, `hard_pass_rate` ≥ retrieval's. **Wall-clock stop 50 GPU-hours** — past it,
v1 ships retrieval-only and states the room-count limit in the product copy
alongside the two limits C5 already commits to. Shippable, not a failure state.

### Honest limits

- Coverage is **Swiss Dwellings only**, and simulated Briefs are real dwellings.
  The cross-paired test is the honest version and still draws both halves from the
  corpus.
- **±10 % / ±15 % is stated, not fitted.** Where warp fidelity actually breaks is
  unmeasured.
- Envelope proxy is the **minimum-area rotated rectangle** — necessary because the
  corpus is geo-referenced, so an axis-aligned bbox measures the site's north
  angle. Median fill **0.79**, p5 **0.61**: real dwellings are markedly
  non-rectangular, and **how many fit ADR 0003's "bbox minus ≤2 notches" cap is
  unmeasured**. That bounds retrieval from a direction not tested here.
- **Rectangularisation is unowned and load-bearing** — every stage places one
  rectangle per room, ~40 % of real rooms are not rectangles, and §7.4 of the
  survey assigned it to tickets 01/04, both closed without settling it. Ticketed.
- No plan has been rendered or eyeballed.
