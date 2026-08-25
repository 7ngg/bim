---
id: 23
title: The retrieval index and warp procedure
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - docs/spec/proposer.md
---

# The retrieval index and warp procedure

## Question

*What the model proposes, and how it is trained* made **retrieval-and-warp one of
the Proposer's two sources**, and it is the one that ships first. It fixed the
admissibility gate and the coverage it buys. **It did not specify the mechanism.**

Settled already, and not to be re-litigated: retrieval is a **hard gate, not a
ranking term** (exact room-multiset match in the Brief vocabulary, area ±10 %,
envelope aspect ±15 %); outside the gate retrieval **declines** and source B
carries the Brief; the corpus is **Swiss Dwellings only** — ResPlan is not
reliably metric; and each match yields up to **8 orientation variants** (4
rotations × mirror), which multiplies diversity inside a matched pool without
raising coverage at all.

**What has to be decided:**

1. **The index.** What is keyed, and what a lookup costs. Graph2Plan measures 99 ms
   retrieval and <0.4 s end to end; that is a target, not a given, and 46,800
   dwellings is a different corpus from theirs.
2. **The warp.** Given a matched dwelling and a target Envelope, how do rooms
   move? Graph2Plan repositions nodes on a 5×5 grid relative to the boundary.
   Anisotropic scaling is the obvious alternative and the obvious way to ruin a
   proportion. State it precisely enough that the output is reproducible, and say
   what happens when the Envelope has a notch the source dwelling does not.
3. **Ranking inside the pool.** The gate admits a median of 66–92 dwellings in the
   common band. C6 wants many candidates, but not 92 near-identical ones — state
   how the pool is ordered and how many are taken, and whether diversity is a
   ranking term or a post-hoc filter.
4. **Per-room confidence.** `docs/spec/proposer.md` §1 promoted confidence from
   optional to **required**, and named "how far each room had to move under the
   warp" as retrieval's source for it. Turn that into a number.
5. **Where warp fidelity actually breaks.** ±10 % / ±15 % is **stated, not
   fitted** — it is simply the budget coverage was measured at. Loosening it
   raises coverage and lowers fidelity, and nobody has measured the trade. This is
   the sub-question with the most product value on this ticket: every point of
   coverage bought here is a Brief that does not fall through to an untrained
   model.
6. **The `entrance_side` anchor.** Graph2Plan anchors its turning function at the
   front door. ADR 0003 gives the Envelope an orthogonal `entrance_side` flag, and
   *Acquire the datasets* measured the real exposure distribution (median 0.37
   exterior, **0 of 569** dwellings above 0.99). State how a retrieved dwelling's
   exposure ring is matched against the Brief's — or whether it is matched at all,
   which would be a finding.

**Why this waits on *Rectangularising real rooms*.** The warp emits a Proposal,
and a Proposal is boxes. Corpus rooms are polygons. Until the conversion is
stated, the thing being warped is undefined.

**Deliverable.** A spec section under `docs/spec/proposer.md` §2.2, with the warp
reproducible from it, plus a measured coverage-versus-fidelity curve for the
budget in item 5.

## The admissibility gate is stated in the wrong units, from *Solver timing variance sweep*

`docs/spec/proposer.md` gates a warp at +-10% area and +-15% aspect. The sweep
measured the solver's actual tolerance in a different quantity entirely —
**per-corner Gaussian noise** — and found a cliff between **sigma 0.5 m and
1.0 m**, at which the recommended configuration goes INFEASIBLE rather than
merely inaccurate: 5 of 5 seeds at 24 rooms, 3 of 5 at 8.

Nothing connects the two. A warp inside the area and aspect budget may or may not
land inside the corner-noise budget, because a uniform stretch moves every corner
coherently while the noise model moves them independently — and it is the
*incoherent* displacement that breaks the relations `fix_relations` extracts.

So this ticket owes one measurement it did not know about: **what per-corner
displacement distribution a warped retrieval actually produces**, expressed so it
can be compared against the cliff. If warps come out coherent, the gate is fine
and the cliff never fires for retrieval — which would be a strong argument for
retrieval over the trained model, since the model has no such guarantee. If they
do not, the gate needs a third term.

tau is the mitigation and it is cheap in this band: at 8 rooms tau = 4 removes
the sigma = 1.0 m cliff completely for 0.02 s. That is why the shipped default is
tau = 4 rather than 0.

## What *Rectangularising real rooms* hands this ticket

**Unblocked.** A corpus dwelling is now a **rectangular tiling of a bbox-minus-≤2-notch
Envelope**, one centreline rectangle per room, produced by a CP-SAT fit
(ADR 0008, `docs/research/rectangularisation.md`). Item 2's "how do rooms move"
is therefore warping *a tiling*, not warping polygons, and a scaled tiling is
still a tiling — which is most of what made the mechanism hard to state.

**Three things change on this ticket, and one of them is a correction.**

**Item 3's pool sizes are wrong, and item 5 now has half its curve.** The median
pool of 66–92 was measured on the unconverted corpus. Conversion drops **31 % of
Swiss Dwellings**, and not uniformly: **83 % of 4-room dwellings convert against
46 % of 10-room**, so the index thins most in exactly the band *What the model
proposes* already found weakest (12.4 % blank, median pool 66). **Re-measure
coverage before quoting any figure from §2.2.** This is affordable only because
ADR 0005 gives a blanked Brief somewhere to go.

**Item 5 inherits a second budget in a different coordinate.** The conversion
posts a **±10 % per-room area band** — stricter than the ±10 % *total*-area warp
gate, chosen so the corpus is not looser than the gate it feeds. Relaxing it to
±25 % takes conversion from 73.6 % to 90.8 %, and unconstrained to 91.2 %. That is
**17.6 points of corpus for a per-room area tolerance**, measured, and it is the
same fidelity-versus-coverage trade as the ±10 %/±15 % gate. Both belong here.

**A new item.** *What happens to the conversion's spurious relations under a
warp.* The fit preserves every separation direction the real dwelling asserted —
zero flipped, zero weakened — but **adds** an assertion on **15.7 %** of axis-pairs
where the truth abstained, because a rectangle model must pick a side when one
room wraps another. Those are the pairs the warp is least entitled to trust, and
`fix_relations` will post them **hard** like any other. Item 4's per-room
confidence should mark them: a relation the corpus asserted and a relation the
conversion invented are not the same claim, and the Proposal contract has exactly
one field that can say so.

**One thing this does not hand over.** The fit does not know exterior from party,
so item 6's exposure-ring matching gets no help from it — what was measured is
boundary contact, not window frontage.

## Item 5 now has a unit, from *Validate the arrangement metric against the solver*

The section above says the admissibility gate is stated in the wrong units and
that nothing connects `±10 % / ±15 %` to the solver's actual tolerance. It now
does, and the connecting quantity is **not** per-corner noise. It is
**confident-wrong severity**:

> Σ `sep_cost(truth, relation)` over the asserted relations the source dwelling
> contradicts, in millimetres. `docs/spec/proposer.md` §5.2,
> `experiments/solver-toy/arrangement.py`.

That ticket validated the metric by injection and found the relation channel is
where a Proposal actually reaches the constraint set: **one** relation the truth
contradicts makes the model INFEASIBLE 56 % of the time and **two** takes the
survivor rate to zero, while dropping *every* relation still yields a Plan. In
the 4–10-room band, severity below **2 000 mm** implied a survivor in 80 runs of
80.

So **this patch of fog is closed and the question is now sharp**: the fidelity
axis for item 5 is not "how far did rooms move", it is "how much separation
direction did the warp destroy".

**What item 5 must measure.** Sweep the gate — area beyond ±10 %, aspect beyond
±15 % — and for each warped Proposal report severity, confident-wrong count,
**reversal count** and abstain rate against the source dwelling. Then state the
curve as *coverage bought per millimetre of severity admitted*, and put the gate
where it turns over. The corpus-side ±10 % per-room area band above is the same
trade in a second coordinate and gets the same treatment.

**Three things that change how item 5 should be run.**

1. **Report reversals separately, and expect a warp to be safe from them.** A
   *same-axis reversal* — the source dwelling puts the two rooms the other way
   round — was INFEASIBLE at **100 %** of every dose tested. A cross-axis swap at
   the same dose is 0–33 %. A coherent anisotropic stretch should produce **no**
   reversals at all, which if true is the strongest possible argument for a
   generous area budget: the warp's errors would be structurally of the mild
   kind. That is a prediction this ticket can falsify cheaply, and it is the
   crux of whether the gate can be loosened.
2. **The conversion's 15.7 % invented assertions are the obvious severity
   source.** The section above already flags them as the pairs the warp is least
   entitled to trust. They are now measurable in the same units as everything
   else, so item 4's per-room confidence can be *calibrated* rather than asserted.
3. **Never publish the rate.** A per-pair rate compounds over a quadratic number
   of pairs: 0.5 % confident-wrong leaves a Proposal clean 88 % of the time at 8
   rooms and 28 % at 24. Report per Proposal.

**And the corner-noise framing above is superseded, not merely refined.** The
sweep's σ cliff is a symptom; severity is the cause. The same metric explains τ,
which the sweep fitted for unrelated reasons — at 12 rooms and σ = 0.5 m, τ = 0
gives severity 2 800 mm and 2 survivors in 5, τ = 4 gives 200 mm and 5 in 5. So a
warp does not need to be compared against a noise σ at all; it can be scored
directly.

**One caveat that lands squarely here.** The validation's own corruption model is
Gaussian corner noise, which produces **almost no reversals**. So the claim
"reversals are fatal" is measured by injection and the claim "real corruption
does not produce them" is measured only on noise. A warp is a third thing and has
never been looked at. Measuring it is this ticket's job, and it is the point at
which the metric stops being validated on a toy.

---

## Handed here by *Whether a Room may be more than one rectangle* (2026-08-23)

**Two things, and the first is a live defect in shipped code.**

⚠️ **`select_relations` never filters on a positive separation cost.** It abstains
on a small *margin* and on a cycle, and on nothing else. So a Proposal whose boxes
**overlap** — which a trained model emits routinely, and which `proposer.md`
§5.2's own per-corner Gaussian produces — has separations asserted for pairs the
Proposal never separated, and the solver posts them **hard**. That is a
manufactured confident-wrong relation, the failure *Validate the arrangement
metric against the solver* measured as fatal in company (1 → 6 % survivor,
2 → 0 %).

This predates ADR 0014 and is true at one rectangle per Room today. It surfaced
only because an L and the Room in its notch have a positive best cost on all four
options **by construction**, which made the missing filter impossible to miss. It
lands here because this ticket owns `docs/spec/proposer.md` §5 and has to score
real warped Proposals against the metric — it will hit this on the first noisy
Proposal it scores.

Whether the right rule is *abstain on positive cost* or *extract per part* is
open. ADR 0014 takes the second for the k ≤ 2 case, because an L's parts are
separable and abstaining throws away a real constraint; a merely-overlapping
noisy box has no parts to fall back to, so it probably wants the first.

**Second: §1's contract moved and §5's unit moved with it.** The Proposal is now
one or two boxes per Room, the extractor runs in the **part** index space
excluding same-Room pairs, and the pair count is quadratic in parts rather than
Rooms — up to **4×**. Every *count* threshold in §5 is therefore in a unit that
moves with a Proposal's shape; **severity, in millimetres, is not**. When this
ticket scores retrieval's Proposals, report severity and treat any count
threshold as needing a re-fit.

⚠️ Also note the coordination hazard: *Re-measure the conversion at two
rectangles per Room* is about to move the conversion this ticket's coverage
figures are measured on. Do not re-measure coverage against a conversion that is
being changed underneath you.

---

## Handed here by *Re-measure the conversion at two rectangles per Room* (2026-08-25)

**The coordination hazard is cleared: the conversion has moved, and you may now
measure coverage against it.** ADR
[0016](../../adr/0016-the-conversion-names-its-own-ls.md),
`docs/research/rectangularisation.md` §11.

**Item 3's pool sizes and item 5's corpus-side budget both move, in your favour.**
The conversion drop falls **30.70 % → 9.74 %** on Swiss and **40.10 % → 6.40 %**
on ResPlan, paired, with zero dwellings lost. Do not apply a single corpus-wide
factor — `experiments/rectangularise/coverage_thinning.py` measures the thinning
**per room multiset**, which is the unit retrieval actually gates in:

| | k = 1 | k ≤ 2 | pool × |
|---|---:|---:|---:|
| band 4–6 | 0.8344 | 0.9424 | 1.129 |
| band 7–10 | 0.5880 | 0.8736 | **1.486** |
| median over 25 multisets | 0.7638 | 0.9318 | 1.219 |
| worst-thinned multiset | 0.2206 | 0.7794 | **3.533** |

The spread is the finding. The multisets that thinned hardest — two bathrooms, a
storeroom, an open-plan living/dining and three private rooms — are exactly the
ones a Brief in the weak band lands in, and they gain most. **§2.2's coverage
table is still yours to restate; this is the quantity to restate it with.**

**The 4-versus-10-room asymmetry that made your item 3 hard is mostly gone.**
*"83 % of 4-room dwellings convert against 46 % of 10-room"* becomes 94.8 % and
82.6 %; the spread across the band goes from 35 points to 12. The index no longer
thins hardest where it was already thinnest.

**Item 4's per-room confidence: the invented assertions fall, and not by much.**
The conversion's spurious separations — pairs the truth abstained on where a
rectangle had to pick a side — go **15.64 % → 13.58 %** of axis-pairs on Swiss and
**20.52 % → 14.30 %** on ResPlan. Real, and smaller than the conversion-rate move:
**the second rectangle rescues dwellings more than it disambiguates pairs.** Still
expect roughly one axis-pair in seven to be an assertion the corpus never made,
and still mark them.

⚠️ **A retrieved dwelling is now one or two boxes per Room, so the warp warps a
two-part tiling.** An anisotropic scale is affine and preserves incidence, so the
join survives a uniform stretch — but that is an argument, not a measurement, and
ADR 0014's join predicate is a **hard** acceptance rule (two parts sharing at
least 900 mm of edge, realisable 1 100 mm). A warp that scales a 1 100 mm join
down by 15 % emits a Proposal the bar rejects. **Item 2 owes that check**, and it
is cheap: the join length is one number per two-part Room.

⚠️ **`select_relations`'s missing positive-cost filter is unchanged and still
yours.** ADR 0014 handed it here; nothing in this ticket touched
`docs/spec/proposer.md`, which remains your sole claim.

**Every figure above is a lower bound.** Which Rooms may take a second rectangle
is named room-locally from the real room's shape, and `name_rate.py` puts the
miss at **2.05 %** of rooms. Design B — letting the fit choose freely — is
unmeasurable at any affordable budget (§11.5).

⚠️ **`proposer.md` §4.4 is now stale in two places, and it is your file.** It
records the conversion as *"settled, and it is a solve"* with the k = 1 yield and
the four-rung ladder. Both moved: the yield is **90.3 % Swiss / 93.6 % ResPlan**,
and **the ladder is reduced to two rungs, A and D** (ADR 0016 consequence 5) —
A → B now buys 2.0 points against 8.4, and tier C sits *below* tier A because
dropping the hard relations removes the pruning and the arm times out. The
tier conditioning field ADR 0008 gave the training set is therefore **binary now,
not four-valued**; retrieval's tier-A gate is unchanged. §2.3's two-part slot with
a presence token needs no change — it already carries what the conversion emits.
