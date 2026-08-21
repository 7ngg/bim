---
id: 24
title: Validate the arrangement metric against the solver
parent: map
labels: [wayfinder:task]
status: closed
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

---

## Resolution

**The metric predicts, and it was defined wrong in three places.** Of the
ticket's three anticipated outcomes it is the first — *it tracks* — but the
tracking is a **step, not a slope**, and getting to it required fixing the
definition rather than confirming it.

Findings `docs/research/arrangement-metric.md`, spec rewritten at
`docs/spec/proposer.md` §5.1–5.5, harness `experiments/solver-toy/`
(`arrangement.py`, `probe6.py`, `report6.py`, `severity6.py`, `mechanism6.py`),
724 recorded runs in `results/P6.jsonl`, tables in `results/report_P6.txt`.

**Replicated.** The headline suite was re-run and the dose-response holds on
fresh random flips — 0 violated → 100 % survivor, 2 → 0 %, ≥3 → 0 %. That re-run
also exposed a defect in this harness worth knowing about: the per-row RNG seed
was derived from a field list that changed mid-sweep, so the two files are
**independent samples rather than one run repeated**. Frozen now as `RNG_FIELDS`.
And it quantified how much CP-SAT moves underneath: on rows that drew the same
dose, the **survivor verdict agrees 96 %** and the **status only 87 %** — runs
slide between INFEASIBLE and a timeout without changing whether a candidate
appeared. Every headline here rests on the survivor verdict for that reason.

### The measurement the ticket asked for

Ground-truth Proposals — the truth used *as* the Proposal, so geometry,
objective and hint are all perfect and the relation set is the only corrupted
channel — with relations flipped to directions the truth does not hold:

| relations the truth contradicts | runs | INFEASIBLE | survivor |
|---|---|---|---|
| 0 | 18 | 0 % | **100 %** |
| 1 | 16 | 56 % | 6 % |
| 2 | 17 | 88 % | 0 % |
| ≥ 3 | 99 | 100 % | 0 % |

"How steeply" has no answer because there is no slope. **One** wrong relation is
most of the damage and **two** is all of it.

It is **causal**, not correlated: deleting only the injected relations restores
OPTIMAL in **43 of 45** cases. And the injected relations *alone* are infeasible
in only **10 %** — so a confident-wrong relation is not self-contradictory, it is
fatal **in company**. The corollary is uncomfortable and measured: the better the
rest of a Proposal, the more each individual error costs.

### Three defects in the definition

**1. The cycle rate is identically zero and cannot be otherwise.** The
extractor adds relations greedily in increasing separation cost and skips any
that would close a per-axis cycle, so its asserted set is acyclic **by
construction**. On real noisy Proposals the guard never fires at all — 0 drops
at every σ up to 1.5 m. A cycle posted around the guard *is* INFEASIBLE, in
0.01–0.18 s, so §5.2's mechanism is real and unreachable; and removing the guard
changes no outcome measurably, so the guard is not defending anything either.
The suspect the ticket named — *cycle rate, not pairwise rate, is what kills a
solve* — is **refuted, and by the strongest possible route**: the number cannot
be non-zero. **Deleted from the spec.**

A second error hides in the same sentence: a cycle is not the only unrealisable
relation set. An **acyclic chain** `a < b < c < d` demands an Envelope at least
as wide as those rooms' minimum widths summed, and nothing checked it. That
bound alone condemns **62 %** of infeasible sets — see *the free check* below.

**2. §5.1 read literally over-counts by up to 3.6×.** "Not the truth's `argmin`"
is not "false of the truth". Two disjoint boxes can be separated on *both* axes
— every diagonal neighbour in a tiling is such a pair — so an assertion can
differ from the `argmin` and still be one the truth satisfies, which the solver
cannot feel. At 24 rooms, σ = 1.0 m: **6.30 %** by the literal reading against
**1.74 %** actually violated. The literal reading is also the worse predictor in
band, 61.4 % against 78.6 %. `CONTEXT.md` had it right all along — "asserted, and
**backwards**" — so the spec had drifted from the domain model, not the reverse.

**3. Counting is the wrong unit; severity is what predicts.** A relation the
truth violates by one grid unit and one it violates by ten are one number in a
count. Summing the violation beats counting it: in the 4–10-room band,
**severity below 2 000 mm implied a survivor in 80 runs of 80**, at 87.9 %
accuracy against a count's 78.6 %. And a *rate* is the wrong shape entirely,
because it compounds over a quadratic number of pairs — 0.5 % confident-wrong
leaves a Proposal clean 88 % of the time at 8 rooms and **28 %** at 24. Report
per Proposal.

### Not all wrongness is equal, and the noise model emits only the mild kind

A **same-axis reversal** — the truth puts the two rooms the other way round — was
INFEASIBLE at **100 %** of every dose tested, at 12 and 24 rooms. A **cross-axis
swap** at the same dose is 0–33 % at one relation. Gaussian per-corner noise, the
corruption behind every published number on this map, produces **essentially no
reversals** (0.00 per Proposal at 24 rooms up to σ = 1.5 m; they first appear at
σ = 2.0). Jitter makes separations *ambiguous*, which the extractor then resolves
onto the wrong axis; it does not march one room past another.

So the injected dose-response is harsher than corner noise, and the difference is
a **kind**, not a quantity — which is exactly the error a learned generator that
misplaces a room will make and a noise model cannot. Both Proposer sources must
report reversals separately.

### The abstain interaction the ticket asked for

Confirmed, with the asymmetry far larger than §5.2 claimed — but the first
attempt was **confounded and had to be re-run**. With the Proposal set to the
truth, CP-SAT is hinted with the answer, so dropping relations looked free for a
reason that had nothing to do with relations. Repeated with the hint off:

- **Not one abstain run at any size or any drop fraction was INFEASIBLE.**
- At 8 and 12 rooms, dropping **every** relation still produced a survivor 5
  times in 5, at worst 6× slower.
- At 24 rooms abstaining is genuinely expensive — half the relations dropped
  loses every run — but always to the **15 s limit**, never to infeasibility.

So the abstain half of the metric is not meaningless; it is a **different
currency**. An abstain costs seconds, a confident-wrong relation costs the
candidate, and collapsing them into one number hides the only failure that
matters. Putting both defects in at once confirms the mechanism from the other
side: at 12 rooms, abstaining on half the pairs takes two confident-wrong
relations from 0 % survivable to **67 %**.

Two oddities worth not smoothing over: dropping *all* relations beats dropping
half at every size, and this suite's `f = 1.0` is **not** the unamended C10 form
*Solver formulation* refuted — the objective still points at the answer, so "no
relations" is not "no information".

### One number explains two knobs

The result that most justifies trusting the metric is that it explains τ, which
*Solver timing variance sweep* fitted for unrelated reasons. At that ticket's own
rig, 12 rooms, σ = 0.5 m:

| τ | asserted | confident-wrong | severity | survivors |
|---|---|---|---|---|
| 0 | 66.0 | 2.40 | 2 800 mm | 2 / 5 |
| 4 | 55.2 | 0.20 | 200 mm | 5 / 5 |

The τ = 0 row **reproduces that ticket's "3 of 5 already fail at 12 rooms at
σ = 0.5 m" exactly**. τ does not make the solver cleverer: it drops ambiguous
pairs before they can be asserted wrongly, and ambiguity is where the errors are.
That is the missing mechanism behind §5.4's stated time-against-infeasibility
trade, and it is handed back to the sweep as the ticket promised.

### Where the metric stops, and it is a real boundary

**It predicts feasibility, not survival.** The two coincide only while the solve
sits comfortably inside the time limit.

- In the **4–10-room band C13 promises**: zero confident-wrong implied a survivor
  in **67 runs of 67**, and no severity threshold up to 2 000 mm ever missed a
  failure.
- At **24 rooms**: **40 %** of Proposals with **zero** confident-wrong relations
  still fail, by running out of time. Every missed failure in the whole
  validation is at 24 rooms — and so τ inverts there too, τ = 0 beating τ = 4
  despite the higher severity.

The scope is now stated in the spec. It is also a **training and evaluation**
instrument only: at serving time there is no ground truth to score against.

### The free check, for the thing the metric cannot do

A posted relation is an edge in a per-axis digraph; along any directed path the
rooms sit side by side, so the Envelope must be at least the sum of their minimum
widths. The heaviest path is a lower bound, O(pairs), **no solver and no ground
truth**:

```
need_x = max over directed paths of Σ min_w  ≤  Envelope width
need_y = max over directed paths of Σ min_h  ≤  Envelope height
```

The truth's own set always passes; injected sets frequently do not, and **98 of
157 INFEASIBLE runs (62 %) are already dead on this bound alone**. It is
sufficient and not necessary — it catches **0 %** at doses of one or two, which
is the realistic regime — so it is a free pre-filter a Proposer can run on its own
output, not a substitute for the solve.

### Housekeeping this ticket did

- **`solver.py`'s relation extractor is now module level** — `rank_relations`,
  `select_relations`, `extract_relations` — because §5.1 requires the metric to
  run *the solver's own* extractor and it previously could not. Verified
  behaviour-identical against an inline copy of the old algorithm across
  8/12/24 rooms × τ ∈ {0, 2, 4, 8} × {Proposal, truth}: **0 mismatches**.
- **`solver._core` is useless on this path and now has a replacement.** It
  rebuilds from `cfg`, so under `fix_relations=False` the rebuild contains no
  relations and it reports the relaxed model is fine. Independently, CP-SAT's
  assumption core over the relations themselves returns **the entire set in 45 of
  54 runs** — the same non-minimality *Solver timing variance sweep* found,
  reached by a second construction. Counterfactual deletion replaces it.
- §5.3's pointer to `probe5.py` as the existing harness was wrong: `probe5`
  runs *degenerate* and *shuffled* Proposals, neither of which is a dosed
  relation error.

### What this does not settle

The corruption is corner noise on a seeded guillotine tiling, not a corpus
dwelling and not a generator's output; five seeds a cell; one grid; the 2 000 mm
threshold is fitted on 140 runs of a toy and has no corpus behind it. And a
relation contradicting the truth may still be satisfiable, because the truth is
one feasible Plan and not the only one — visible as the 30 false alarms in band.
**Neither Proposer source has been scored.** This validates the instrument.
