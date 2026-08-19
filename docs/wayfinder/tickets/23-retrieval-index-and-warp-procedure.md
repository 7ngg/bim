---
id: 23
title: The retrieval index and warp procedure
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: [22]
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
