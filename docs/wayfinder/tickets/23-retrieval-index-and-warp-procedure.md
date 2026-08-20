---
id: 23
title: The retrieval index and warp procedure
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
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
