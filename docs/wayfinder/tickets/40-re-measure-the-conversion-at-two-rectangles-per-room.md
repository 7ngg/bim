---
id: 40
title: Re-measure the conversion at two rectangles per Room
parent: map
labels: [wayfinder:task]
status: open
assignee: tng
blocked_by: []
writes:
  - experiments/rectangularise/
  - docs/research/rectangularisation.md
---

# Re-measure the conversion at two rectangles per Room

## Question

**ADR 0008's conversion drops 31 % of Swiss Dwellings, and that price was paid
for a constraint ADR 0014 has since removed.** Re-measure it.

*Rectangularising real rooms* converts a corpus dwelling by solving it: one
CP-SAT fit per dwelling with the real dwelling's separation directions and
door-width adjacencies hard and exact tiling soft, **one rectangle per room**. A
dwelling with no such tiling is dropped, and 31 % of Swiss Dwellings and 40 % of
ResPlan are. ADR
[0014](../../adr/0014-a-room-is-one-or-two-rectangles-and-the-proposal-decides.md)
gives every Room a second rectangle. Nobody has re-run the fit with it.

This is ticket 28 item 6, deliberately **not** resolved there. Item 2's solver
cost was the required measurement and it was made; this one is a different
harness — the conversion fit, not the projection solver — and it was left owned
rather than asserted.

**Why it matters more than a percentage.** The dropped population is the
*interlocked* one: `STOREROOM` over-represented 1.71×, bbox overlap 2.9× higher.
Those are exactly the dwellings an L absorbs. And the drop is not uniform across
the band — **83 % of 4-room dwellings convert against 46 % of 10-room** — so
retrieval's pool shrinks most where `proposer.md` §2.1 already showed it thinnest.
Every coverage figure on the map downstream of the conversion inherits this.

## A falsifiable prediction, stated so it can be wrong

`experiments/rectangularise/ablate.py` (250 dwellings, `out/ablate.log`) already
says **which constraint family** the reject rule is rejecting for:

| arm | converted |
|---|---:|
| as shipped | 0.7360 |
| area band ±25 % | 0.9080 |
| area free | 0.9120 |
| up to 4 notches | 0.6680 |
| relations, neighbours only | 0.8200 |
| **no hard adjacency** | **0.9560** |
| no hard relations | 0.9375 |
| relations + adjacency off | 1.0000 |

**Hard adjacency is the dominant cause** — turning it off recovers 22 points, more
than any other single relaxation. And an L is precisely the shape that reaches an
adjacency a rectangle cannot: a corridor that wraps a wing touches rooms on two
sides of it.

So the prediction is that k ≤ 2 attacks the dominant reject cause **directly**,
and the drop should fall substantially. That is a prediction off an ablation, not
a measurement of the thing itself. Do not quote it as one.

## What has to be done

1. **Extend `fit_rects.fit()` to two rectangles per room.** The projection
   solver's version is already written and exercised —
   `experiments/room-rectangles/solver_parts.py` — including the part-level
   presence trick (a zero-area box, which `AddNoOverlap2D` ignores in the pinned
   ortools; `smoke_zero_box.py` asserts it), the leg floor, the join constraint,
   and room-level aggregation of adjacency and flow. The conversion fit differs
   in what it optimises, not in its structure.
2. **Re-run the drop on both corpora**, and split it by room count, because the
   4-versus-10-room asymmetry is what bites retrieval.
3. **Re-measure the fidelity ladder.** ADR 0008's tiers A–D and *"retrieval
   admits tier A only"* were set against a one-rectangle fit. Ask whether the
   tier-A population is now large enough that the ladder still earns its
   complexity.
4. **Check the dropped population is still the interlocked one.** If k ≤ 2
   absorbs the interlocked dwellings, whatever remains dropped is something else,
   and naming it is worth more than the percentage.
5. **Re-state `proposer.md` §2.2's coverage table**, which *Rectangularising real
   rooms* already invalidated once and which is owed by *The retrieval index and
   warp procedure*. Coordinate: that ticket must not re-measure coverage on a
   conversion this ticket is about to move.

## What NOT to re-open

ADR 0008's mechanism — *a corpus dwelling is converted by solving it* — is not in
question, and neither is representability as the reject rule. Zero adjacencies
destroyed and zero relations flipped are guarantees of the formulation, not of
the rectangle count, and they must still hold.

⚠️ **`why_k.clean()` is broken and nothing here may use it** — see the note added
to *Look at the converted corpus*, and `experiments/room-rectangles/morphology.py`
for a corrected implementation with a selftest.
