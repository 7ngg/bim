# Validating the arrangement metric

Ticket 24, *Validate the arrangement metric against the solver*.

`docs/spec/proposer.md` §5 defines the number the Proposer is to be scored on:
per-pair separation-direction agreement, reported as agreement / abstain /
**confident-wrong**, plus a cycle rate. It is a **proxy** — nothing had ever
shown that a Proposal scoring badly on it is a Proposal the solver fails to
project — and this map had already been bitten once by an unvalidated proxy
(overlap, refuted by *Proposer architecture survey* §7.1).

Harness: `experiments/solver-toy/`. New files `arrangement.py` (the metric and
the injection machinery), `probe6.py` (ten suites, 724 recorded runs), `report6.py`,
`severity6.py`, `mechanism6.py`. `solver.py`'s relation extractor was lifted to
module level unchanged — see §1.1 — and nothing else in the toy was touched.
Raw rows in `results/P6.jsonl`, an independent replication of the headline
suite in `results/P6_verify.jsonl` (§12), tables in `results/report_P6.txt`.

---

## 0. The headline

**The metric is real, causal, and defined wrong in three separate places.**

Injecting relations the truth contradicts, with every other channel held at
ground truth, destroys the solve: **zero violated relations gives a survivor in
100 % of runs at 8, 12 and 24 rooms; one gives 0–20 %; two or more gives 0 %,
and 85–100 % of those are proved INFEASIBLE.** Deleting only the injected
relations restores OPTIMAL in **43 of 45** cases. So the proxy is not merely
correlated with failure — it causes it.

Three things about the published definition do not survive.

1. **The cycle rate is identically zero and cannot be otherwise.** The
   extractor adds relations greedily and skips any that would close a per-axis
   cycle, so its asserted set is acyclic *by construction*. On real noisy
   Proposals the guard never even fires — 0 drops at every σ up to 1.5 m. And
   removing the guard changes nothing measurable: unguarded sets do contain
   cycles, and go INFEASIBLE at the same rate the guarded ones already did. The
   cycle rate is a number that is always 0, measuring a failure the solver is
   already immune to, protected by a guard worth nothing. **Delete all three.**

2. **§5.1 read literally over-counts confident-wrong by 2–3×.** "Not the truth's
   `argmin`" is not the same as "false of the truth". A pair separated on *both*
   axes — any diagonal pair in a tiling — satisfies two directions, so asserting
   the non-`argmin` one is not wrong in any way the solver can feel. At 24 rooms
   and σ = 1.0 m the two readings give **6.30 %** and **1.74 %**. The literal
   reading is also the worse predictor in v1's band: 61.4 % accuracy against
   78.6 %.

3. **Counting is the wrong unit; the count's *severity* is what predicts.** A
   relation the truth violates by one grid unit and one it violates by ten are
   one number in §5.2 and are not the same defect. Summing the violation, in
   grid units, beats the count: in v1's 4–10-room band, **severity sum < 8 grid
   units (2 m) implied a survivor in 80 runs out of 80**, and the threshold
   scores 87.9 % against the count's 78.6 %.

Two further results matter more than the redefinition.

- **Not all wrongness is equal, and the noise model produces only the harmless
  kind.** A *same-axis reversal* — the truth puts the two rooms the other way
  round — is INFEASIBLE at **100 %** of doses tested. A *cross-axis swap* at the
  same dose is 0–33 % at one relation. Gaussian corner noise, the corruption
  every published run on this map uses, produces **essentially no reversals**
  (0.00 per Proposal at 24 rooms up to σ = 1.5 m). So the injected dose-response
  is harsher than reality, and the difference is a kind, not a quantity.

- **The metric predicts INFEASIBILITY, not survival, and the two part company at
  24 rooms.** At 24 rooms with the shipped 15 s limit, 40 % of Proposals with
  **zero** violated relations still fail — they simply do not reach a survivor
  in time. In the 4–10-room band C13 actually promises, `violated == 0` implied
  a survivor in **67 runs out of 67**. State the scope; do not widen the claim.

One number now explains two knobs that were fitted separately. At 12 rooms,
σ = 0.5 m, the shipped rig: **τ = 0 gives severity 11.2 and 2 survivors in 5;
τ = 4 gives severity 0.8 and 5 in 5.** The first of those reproduces *Solver
timing variance sweep*'s "3 of 5 already fail at 12 rooms" exactly.

---

## 1. What was measured

### 1.1 The extractor is now shared, because §5.1 says it must be

§5.1 requires the metric to "run the solver's own extractor on both sides, so
the metric cannot drift from the thing it predicts". It could not: the
extraction was a private method inside `LayoutProjector._add_relations`, and any
metric would have been a copy of it.

It is now `solver.rank_relations` / `solver.select_relations` /
`solver.extract_relations` at module level, with `_add_relations` reduced to the
posting half. The refactor is **verified behaviour-identical**: the posted
relation set is compared element-for-element against an inline copy of the old
algorithm at 8/12/24 rooms × τ ∈ {0, 2, 4, 8} × {Proposal, truth}, 24
comparisons, **0 mismatches**.

### 1.2 The ten suites

Shipped configuration throughout: 15 s, τ = 4, `soft=("coverage",)`, 4 workers,
250 mm grid, seeds 20260817–20260821.

| | What it does | Why |
|---|---|---|
| **A** | Proposal = the ground truth *exactly*; flip k of the truth's own relations to a direction it does not hold | The dose-response. Geometry, objective and hint are all perfect, so the relation set is the only corrupted channel |
| **A2** | the same, acyclicity guard off | Prices the guard, and is the only way a cyclic set reaches the model |
| **A3** | same-axis reversal against cross-axis swap | Does the *kind* of wrongness matter |
| **B** | drop k relations instead of flipping them | Abstain. An abstained pair is exactly one left free |
| **B2** | B with the solution hint off | B alone is confounded — see §7 |
| **C** | no injection; Gaussian per-corner noise at σ ∈ {0 … 1.5} m | What a real Proposer emits |
| **C2** | C at *Solver timing variance sweep*'s own rig, τ ∈ {0, 4} | Ties the metric to that ticket's measured cliff |
| **D** | a directed cycle posted unguarded | The failure §5.2 names |
| **E** | counterfactuals: flips alone, and everything-but-the-flips | Cause, not correlation |
| **F** | wrong and abstaining at once | The interaction ticket 24 asks for |

A **survivor** is ticket 15's definition, kept so the numbers are comparable: a
solution whose objective is below one `soft_weight`, i.e. one that tiles the
Envelope and would pass the Acceptance bar.

---

## 2. Confident-wrong is causal, and the proof is a deletion

Suite A, Proposal held at ground truth, dose measured as the number of posted
relations the truth actually contradicts:

| violated relations | runs | INFEASIBLE | survivor |
|---|---|---|---|
| 0 | 18 | 0 % | **100 %** |
| 1 | 16 | 56 % | 6 % |
| 2 | 17 | 88 % | 0 % |
| ≥ 3 | 99 | 100 % | 0 % |

There is no slope to fit. The ticket asked "how steeply"; the answer is that it
is a step, and the step is at one.

Suite E turns the correlation into a cause. Of 52 runs posting at least one
violated relation, 45 are INFEASIBLE, and:

- **deleting only the flipped relations — which is exactly what abstaining on
  those pairs would have done — restores a survivor in 43 of 45 (96 %).**
- the flipped relations **on their own** are INFEASIBLE in only **3 of 31**
  (10 %) at 8 and 12 rooms.

So a confident-wrong relation is not self-contradictory. It is fatal *in
company*: the surrounding correct relations pin every other room, and the wrong
one then has nowhere to go. The corollary is uncomfortable and is measured in
§7 — a **better** Proposal makes each individual error **more** expensive.

CP-SAT's own assumption core says nothing: asked which posted relations suffice
for the infeasibility, it returns **the entire set in 45 of 54 runs**. That is
the same non-minimality *Solver timing variance sweep* found for
`solver._core`, reached by a second and independent construction. `_core` is
worse than useless on this path — it rebuilds the model from `cfg`, and under
`fix_relations=False` the rebuild contains no relations at all, so it reports
that the relaxed model is fine. Suite E and `mechanism6.blame` replace it.

---

## 3. Two readings of §5.1, and they are not the same number

§5.1 step 2 takes `direction = argmin`. §5.2 then calls an asserted pair
confident-wrong when it "contradicts truth". Those are different tests:

- **argmin-wrong** — the asserted direction is not the truth's `argmin`.
- **violated** — the asserted separation is *false of the truth geometry*, i.e.
  its cost against the truth boxes is positive.

They diverge because a disjoint pair can be separated on both axes at once. In
a tiling, every diagonal neighbour is such a pair. Asserting "i is below j" when
the truth's `argmin` was "i is left of j" is scored as a disagreement by the
first test and as no error at all by the second — and the truth satisfies the
constraint, so the solver cannot tell.

Measured over 5 Proposals per cell, τ = 4:

| rooms | σ (m) | argmin-wrong | violated |
|---|---|---|---|
| 8 | 1.0 | 6.43 % | 4.29 % |
| 12 | 1.0 | 8.18 % | 3.94 % |
| 24 | 0.5 | 1.30 % | 0.29 % |
| 24 | 1.0 | 6.30 % | 1.74 % |
| 24 | 1.5 | 10.65 % | 3.70 % |

The literal reading over-reports by 1.5× at 8 rooms and **3.6×** at 24. It is
also the weaker predictor where v1 lives (§6).

`CONTEXT.md` already had this right — it defines a confident-wrong pair as
"asserted, and **backwards**", which is the `violated` reading. The drift is in
the spec, not the vocabulary.

---

## 4. The cycle rate is zero by construction

§5.2 asks for "the fraction of Proposals whose asserted relation set is
unrealisable, because a directed cycle in the implied x- or y-ordering is
infeasible however correct each pair looks alone".

`select_relations` walks candidate relations in increasing separation cost and
**skips any relation that would close a directed cycle on its axis**. The
asserted set is therefore acyclic before it is ever returned. The cycle rate, as
defined, is 0 for every Proposal that has ever been or ever will be extracted by
this solver.

It is not even a near miss. Across 8/12/24 rooms and σ ∈ {0, 0.25, 0.5, 0.75,
1.0, 1.5} m, the guard **dropped zero relations** — the greedy order never so
much as encounters a cycle on a noisy Proposal.

Three measurements finish it off.

- **Suite D.** A directed cycle of 3, 4 or 5 rooms, posted around the guard, is
  INFEASIBLE in 100 % of runs, in 0.011 s at 8 rooms, 0.03 s at 12 and 0.15–
  0.18 s at 24. §5.2's mechanism is real. It is simply unreachable.
- **Suite A2.** Turn the guard off and inject the same flips. Unguarded sets
  genuinely do contain cycles. The INFEASIBLE rate is **unchanged** — 100 % at
  k ≥ 4 either way, and the k = 2 cells differ by one run in three in both
  directions. The cycle is never the *first* thing wrong with the set.
- The guard's own cost is likewise nil: it drops 0.15–15 relations under
  injection and none under noise.

**So: delete the cycle rate from §5.2, and note that the guard is load-bearing
for nothing.** Keeping the guard is still right — it is three lines and it makes
a class of failure impossible — but it must not be described as a defence.

A second, quieter error in the same sentence: a cycle is not the only
unrealisable relation set. An *acyclic* chain `a < b < c < d` on the x axis
demands an Envelope at least as wide as those rooms' minimum widths summed, and
nothing checks that. §10 measures it.

---

## 5. Reversal against swap: the kind matters more than the count

Suite A3 injects only one kind at a time.

| rooms | kind | k = 1 | k = 2 | k = 4 |
|---|---|---|---|---|
| 12 | reversal | **100 %** INFEASIBLE | 100 % | 100 % |
| 12 | swap | 0 % | 67 % | 100 % |
| 24 | reversal | **100 %** | 100 % | 100 % |
| 24 | swap | 33 % | 33 % | 100 % |

A single same-axis reversal is fatal every time. A single cross-axis swap is
usually survivable — at 12 rooms it left 67 % of runs with a survivor.

That is the whole explanation of why suite A looked so much harsher than suite C
at the same violated count: suite A's `any` mode draws uniformly from the three
wrong directions, so a third of its flips are reversals. **Real corner noise
produces almost none.** Per Proposal, mean reversals against the truth's
`argmin`:

| rooms | σ = 0.5 | σ = 1.0 | σ = 1.5 |
|---|---|---|---|
| 8 | 0.00 | 0.00 | 0.80 |
| 12 | 0.00 | 0.00 | 0.80 |
| 24 | 0.00 | 0.00 | 0.00 |

At σ = 2.0 m — four times the noise every published run on this map uses —
reversals finally appear, at 0.80 per Proposal at 8 rooms and 1.40 at 24.

Gaussian jitter on corners moves boxes; it does not often march one box all the
way past another. It converts confident separations into *ambiguous* ones, which
the extractor then resolves onto the wrong axis.

This is a real limit on the injection experiment and it cuts both ways. The
dose-response is measured on a defect the corpus noise model does not emit — but
a **learned generator** is not Gaussian corner noise, and a model that has
misplaced a room in the room-set entirely will emit exactly the reversal that
the noise model cannot. Neither source has been measured on real output yet;
that is *The retrieval index and warp procedure* and the trained model's first
eval.

---

## 6. Severity, not count

A violated relation carries a magnitude: `sep_cost` against the truth, the
overlap in grid units the assertion demands be closed. Summing it over a
Proposal's violated relations gives a single number, and it beats the count.

Confusion tables over 140 realistic Proposals at 8 and 12 rooms — v1's band —
each cell "predicted clean" against "produced a survivor":

| predictor | missed failures | false alarms | accuracy |
|---|---|---|---|
| argmin-wrong = 0 (§5.1 literal) | 0 / 43 | 54 / 97 | 61.4 % |
| violated = 0 | 0 / 67 | 30 / 97 | 78.6 % |
| severity sum < 4 | 0 / 72 | 25 / 97 | 82.1 % |
| **severity sum < 8** | **0 / 80** | 17 / 97 | **87.9 %** |
| severity sum < 16 | 6 / 92 | 5 / 97 | 92.1 % |

Every threshold up to 8 grid units is **sound** on this evidence: not one
Proposal below it failed to produce a survivor, across 140 runs. At 16 the
accuracy is higher and soundness is lost, which is the wrong trade for a gate.

**8 grid units is 2 m of demanded overlap, summed across the whole Proposal.**
Below it the solver absorbed every Proposal tested.

The τ evidence is the strongest single result in the ticket, because it explains
a knob that was fitted for other reasons. At *Solver timing variance sweep*'s own
rig, 12 rooms, σ = 0.5 m:

| τ | asserted | violated | severity sum | survivors |
|---|---|---|---|---|
| 0 | 66.0 | 2.40 | **11.2** | 2 / 5 |
| 4 | 55.2 | 0.20 | **0.8** | 5 / 5 |

The τ = 0 row reproduces that ticket's "3 of 5 already fail at 12 rooms at
σ = 0.5 m" exactly. τ does not make the solver cleverer; it **filters
confident-wrong relations out before they are posted**, and the severity sum is
what it filters. The same holds at 8 rooms, σ = 1.0 m (severity 22.2 → 5.2,
1 / 5 → 3 / 5 survivors).

### 6.1 Why a rate is the wrong shape to publish

A per-pair rate compounds over pairs, and the pair count is quadratic in rooms.
A Proposal is clean with probability `(1 − p)^m` over `m` asserted pairs:

| per-pair rate | 8 rooms (m ≈ 25) | 12 rooms (m ≈ 59) | 24 rooms (m ≈ 253) |
|---|---|---|---|
| 0.1 % | 97.6 % | 94.3 % | 77.6 % |
| 0.5 % | 88.4 % | 74.5 % | 28.1 % |
| 1 % | 78.1 % | 55.4 % | 7.8 % |
| 2 % | 60.8 % | 30.5 % | 0.6 % |

A 0.5 % confident-wrong rate reads as "99.5 % correct" and is also "loses seven
Proposals in ten at 24 rooms". Publishing the rate invites exactly that
misreading; publishing a per-Proposal figure does not.

---

## 7. Abstain is nearly free — and suite B had to be run twice to say so

§5.2 asserts that "an abstain leaves the solver free" while a confident-wrong
relation costs the candidate. Suite B drops relations from the truth's own set.

**Suite B as first run is confounded and its numbers should not be quoted.**
With the Proposal set to the ground truth, CP-SAT is *hinted with the answer*,
so dropping relations costs almost nothing for a reason that has nothing to do
with relations. Suite B2 repeats it with the hint off; the objective still pulls
toward the Proposal, because that is C10's design rather than a confound.

Dropping a fraction *f* of the truth's own relations, hint off, five seeds a
cell. **Not one run at any size and any f was INFEASIBLE.**

| rooms | f = 0 | 0.1 | 0.25 | 0.5 | 0.75 | 1.0 |
|---|---|---|---|---|---|---|
| 8 — survivors | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| 8 — time to survivor | 0.215 s | 0.271 | 0.307 | 0.328 | 0.281 | 0.202 |
| 12 — survivors | 5/5 | 5/5 | 5/5 | 5/5 | 4/5 | 5/5 |
| 12 — time to survivor | 0.523 s | 1.644 | 2.173 | **3.335** | 1.386 | 0.568 |
| 24 — survivors | 4/5 | 3/5 | 1/5 | **0/5** | **0/5** | 2/5 |
| 24 — time to survivor | 4.254 s | 11.653 | 4.454 | — | — | 3.222 |

At 8 and 12 rooms abstaining is very nearly free: it costs a factor of 6 in
time at worst and never a candidate. At 24 rooms it is expensive — half the
relations dropped loses every run — but the loss is always the **15 s limit**,
never infeasibility. That is §5.2's claim, now measured: an abstain costs
seconds, a confident-wrong relation costs the candidate.

Two things in that table are worth not smoothing over.

- **f = 1.0 is better than f = 0.5 at every size.** Dropping *all* relations
  beats dropping half. A partial relation set is the worst of both: it prunes
  the packing's symmetry without supplying a full ordering. Observed, not
  explained.
- **f = 1.0 here is not the unamended C10 form** *Solver formulation for layout
  projection* refuted. The Proposal is the ground truth, so the objective still
  points at the answer even with no relations posted. "No relations" is not "no
  information", and 2/5 survivors at 24 rooms is not a contradiction of that
  ticket's "finds nothing in 30 s" on a noisy Proposal.


The direction §5.2 predicts holds, and the asymmetry is enormous: dropping
**every** relation still produces a survivor, where flipping **one** does not.
Abstain and confident-wrong are not two ends of one scale. They are a slowdown
and a failure.

Suite F puts both defects in at once, and confirms §2's mechanism from the other
side. Flipping k relations *after* dropping a fraction f of the rest:

| rooms | drop f | k = 1 survivor | k = 2 survivor | suite A at same k |
|---|---|---|---|---|
| 12 | 0.25 | 33 % | 0 % | 40 % / 0 % |
| 12 | 0.50 | **67 %** | **67 %** | 40 % / 0 % |
| 24 | 0.25 | 33 % | 0 % | 20 % / 0 % |
| 24 | 0.50 | 33 % | 0 % | 20 % / 0 % |

At 12 rooms, abstaining on half the pairs takes two confident-wrong relations
from 0 % survivable to 67 %. This is §2's finding stated as a trade: **the
better the rest of the Proposal, the more each individual error costs.** A
Proposer that abstains freely buys tolerance for the assertions it does make.

---

## 8. What the metric does not predict

At 24 rooms the shipped 15 s limit, not feasibility, is what kills a candidate,
and the metric is silent about it.

| rooms | σ = 0.25 m | violated | survivor |
|---|---|---|---|
| 8 | | 0.00 | 100 % |
| 12 | | 0.00 | 100 % |
| 24 | | 0.00 | **60 %** |

Zero violated relations, zero INFEASIBLE, and 40 % of runs still fail — they
reach 15 s without an objective below `soft_weight`. Pooled over all 210
realistic Proposals the metric's accuracy is 77.1 %; restricted to 8 and 12
rooms it is 78.6 % with **no missed failures at all**, and every one of the 12
missed failures is at 24 rooms.

The same effect inverts τ at 24 rooms: on the shipped rig at σ = 0.25 m,
τ = 0 gives 3 survivors in 5 and τ = 4 gives 1 in 5, even though τ = 4 has the
lower severity. Higher τ fixes fewer relations, so the search is freer and
slower, and at 24 rooms slower means out of time. This is *Solver timing
variance sweep*'s "τ is free at 8 rooms and unaffordable at 24" appearing in a
second measurement.

**None of this is a problem for v1**, because C13 caps the Proposer at 10 rooms
and *The room-count envelope v1 promises* caps the product. It is a problem for
anyone who quotes the metric outside that band, so §5 must say so.

---

## 9. A check that needs no ground truth

The metric requires a truth to score against, so it is a training and evaluation
instrument only — at serving time, for a Brief nobody has a dwelling for, it
cannot be computed. One necessary condition can be:

A posted relation `x2[a] ≤ x1[b]` is an edge in a per-axis digraph. Along any
directed path the rooms sit strictly side by side, so the Envelope must be at
least the sum of their minimum widths. The heaviest path is a lower bound on the
Envelope, computable in O(pairs) with no solver and no truth:

```
need_x = max over directed paths P of sum(min_w[i] for i in P)      need_x ≤ W
need_y = max over directed paths P of sum(min_h[i] for i in P)      need_y ≤ H
```

The truth's own relation set always passes (26/40, 33/52, 47/72 at 8/12/24
rooms). Injected sets frequently do not, and when they do not the model is
infeasible by counting rather than by search: **98 of 157 INFEASIBLE runs
(62 %) are already dead on this bound alone.**

It is sufficient, not necessary, and it fails exactly where it would be most
useful — at doses of one or two relations it explains **0 %** at 12 and 24
rooms. So it is a cheap pre-filter a Proposer can run on its own output, not a
replacement for the solve. `experiments/solver-toy/mechanism6.py`.

For the low doses it cannot explain, softening each hard Brief family in turn
(coverage is already soft) does not isolate one either: the runs are killed by
the packing itself rather than by any single family.

---

## 10. The redefinition

§5 of `docs/spec/proposer.md` is rewritten to match. In summary:

1. **Confident-wrong** means *asserted, and false of the truth geometry* —
   `sep_cost(truth, relation) > 0`. Not "not the argmin".
2. **Report severity, not just count.** `severity = Σ sep_cost` over violated
   relations, in millimetres. Publish both; the gate is severity.
3. **Split by kind.** Reversals and cross-axis swaps are different defects with
   different costs, and a source that emits reversals is failing differently
   from one that emits swaps.
4. **Report per Proposal, never as a per-pair rate.** §6.1.
5. **Delete the cycle rate.**
6. **State the band.** The metric predicts *feasibility*. Inside 4–10 rooms
   feasibility and survival coincide; at 24 they do not.
7. **Abstain stays, and stays separate.** It is a slowdown, never a failure, and
   it buys tolerance for the assertions a source does make.

§6.2's stop condition 1 — "confident-wrong rate ≤ retrieval's" — is restated in
the new units.

---

## 11. Corrections this note owes other documents

- **`docs/spec/proposer.md` §5.2**, "A confident-wrong relation becomes a hard
  constraint and makes the model INFEASIBLE in under 0.1 s." Half right. It does
  become a hard constraint, and infeasibility is proved fast when it is proved —
  0.01 s at 8 rooms, 0.03 s at 12, 0.12–0.17 s at 24, so *under 0.1 s is wrong at
  24 rooms*. But a single violated relation is INFEASIBLE only 56 % of the time,
  and on realistic noise at 8 and 12 rooms a Proposal with one or two violated
  relations produced a survivor in every run measured.
- **`docs/spec/proposer.md` §5.2**, the cycle rate. Deleted, §4.
- **`docs/spec/proposer.md` §5.3**'s pointer to `probe5.py` as the existing
  harness. `probe5.py` runs *degenerate* and *shuffled* Proposals, neither of
  which is a dosed relation error; the work needed a new probe.
- **`docs/spec/proposer.md` §5.4** says τ "trades solve time against
  infeasibility … high τ fixes fewer relations, so the search is freer and
  slower; low τ fixes more, so it is faster and fails more." Confirmed, and now
  given its mechanism: what low τ admits is **violated relations**, and the
  severity sum is the quantity τ filters (§6).
- **`experiments/solver-toy/README.md`**'s "The Proposal appears only in the
  objective and the hint — never in a constraint", already flagged as true only
  with `fix_relations=False`. This note adds the size of the hole: with
  `fix_relations=True` one wrong relation is enough.
- **`CONTEXT.md`** is *correct* and the spec drifted from it. Its
  "asserted, and backwards" is the `violated` reading. Tightened only to name
  severity.

---

## 12. Two defects in this note's own measurements

**The per-row RNG seed was derived from a field list that changed mid-run.**
`probe6.execute` seeded each row's flips from `KEY_FIELDS`, and adding `tau` for
suite C2 — after the main run had launched — silently re-drew every subsequent
injection. So `results/P6.jsonl` and `results/P6_verify.jsonl` are **two
independent samples of suite A, not one run repeated.** The field list is now
frozen as `RNG_FIELDS`, a literal that must not change, and a re-run reproduces
`P6_verify.jsonl` exactly.

The accident is more useful than a bitwise repeat would have been, because it is
an **independent replication on fresh random flips** — and the dose-response
survives it unchanged:

| violated relations | original | replication |
|---|---|---|
| 0 | 100 % survivor (18 runs) | **100 % survivor** (15 runs) |
| 1 | 6 % (16) | 16 % (19) |
| 2 | 0 % (17) | **0 %** (16) |
| ≥ 3 | 0 % (99) | **0 %** (100) |

**CP-SAT's status is less stable than its verdict, and the difference is worth
knowing.** On the 69 rows where the two samples happened to draw the same dose,
the **survivor verdict agrees 66 times (96 %)** but the **status only 60 (87 %)**
— runs move between INFEASIBLE and a timeout without changing whether a
candidate was produced. That is `README.md`'s "the statuses are the stable part"
holding for *found / not found* and **not** for *proved infeasible / ran out of
time*. Every headline in this note is built on the survivor verdict for that
reason; the INFEASIBLE percentages are the softer numbers on the page.

**Second defect, smaller.** A family-blame diagnostic was run for about two
minutes alongside the main sweep on a 4-core machine, so a handful of suite-C
rows may have been solved under contention. The clean re-run above covers suite
A; suite C was not re-run, and its `valid_at` figures should be read as
indicative.

---

## 13. What this note does not establish

- **It is measured on the toy, not on a Proposer.** Ground truth here is a
  seeded guillotine tiling, not a rectangularised corpus dwelling, and the
  corruption is Gaussian corner noise, not a generative model's output. §5 is
  explicit that this understates reversals.
- **Five seeds per cell.** Enough to separate 0 % from 100 %; not enough to put
  a confidence interval on 60 %.
- **One grid, one time limit, one τ for the injection arms.** 250 mm, 15 s,
  τ = 4. C2 varies τ; nothing varies the grid.
- **The 8-grid-unit severity threshold is fitted on 140 runs of this toy** and
  is a starting value for a real eval, not a shipped constant. It has no
  corpus behind it.
- **A relation that contradicts the truth may still be satisfiable.** The truth
  is one feasible Plan, not the only one, so even the `violated` reading
  over-counts — which is visible as the 30 false alarms in §6. The only exact
  predictor of "will the solver project this" is the solve.
- **Neither Proposer source has been measured.** What retrieval-and-warp and the
  trained model actually score is *The retrieval index and warp procedure*'s and
  the training eval's work. This note validates the instrument, not the subject.
