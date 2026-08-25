# The conversion names its own Ls, and the corpus drop was a price for a deleted constraint

**Status:** accepted
**Date:** 2026-08-25
**Ticket:** *Re-measure the conversion at two rectangles per Room*
**Amends:** [ADR 0008](0008-a-corpus-dwelling-is-converted-by-solving-it.md) —
its rectangle count, its yield, its fidelity ladder, and its
*"decidable, not a timeout"*
**Related:** [ADR 0014](0014-a-room-is-one-or-two-rectangles-and-the-proposal-decides.md),
[ADR 0003](0003-the-envelope-is-an-inner-face-ring-of-typed-edges.md),
[ADR 0005](0005-the-proposer-has-two-sources.md),
[ADR 0009](0009-a-derived-minimum-is-not-rounded-onto-the-solve-grid.md)

## Decision

**The conversion fits one or two rectangles per Room, and which Rooms get two is
named from the real room's own shape before the solve.**

ADR 0008's mechanism is untouched: a corpus dwelling is still converted by
solving it, the reject rule is still representability, and every hard family
stays hard. What changes is the rectangle count and who chooses it.

Findings: `docs/research/rectangularisation.md` §11. Harness
`experiments/rectangularise/fit_rects.py --k2`.

## Why the number had to move

ADR 0008 dropped **31 %** of Swiss Dwellings and **40 %** of ResPlan, and that
price was paid for **one rectangle per room** — a constraint ADR 0014 removed and
no ticket had re-priced. ADR 0014 said so itself, in its consequence 4: *"it does
not fix the corpus yield … a Proposal that cannot carry an L leaves the
conversion nothing to emit."* That was true of the solver. It was never a claim
about the conversion.

Re-measured paired — the same 2 600 Swiss dwellings and 1 000 ResPlan plans, same
order, same code, only `k_of` changed:

| | k = 1 | k ≤ 2 |
|---|---:|---:|
| Swiss converted | 0.6930 | **0.9026** |
| ResPlan converted | 0.5990 | **0.9360** |
| dwellings lost | — | **0** |

McNemar exact p = 2.2 × 10⁻¹⁶² and 7.1 × 10⁻¹⁰². **Two thirds of the Swiss drop
and four fifths of the ResPlan drop were paying for the deleted constraint.**

**The slope mattered more than the level.** ADR 0008's cost fell hardest where
the retrieval index was already thinnest — 83 % of 4-room dwellings converting
against 46 % of 10-room. The gain runs the other way and cancels most of it:

| rooms | k = 1 | k ≤ 2 |
|---:|---:|---:|
| 4 | 0.8290 | 0.9482 |
| 7 | 0.7049 | 0.9126 |
| 10 | 0.4783 | 0.8261 |

The spread across C13's band goes from **35 points to 12**. A 10-room dwelling
now converts about as well as a 4-room one did. The conversion has stopped being
a filter that prefers small dwellings, which is the property that was quietly
biasing both the retrieval pool and the training corpus.

## Who names the Ls, and why it is not the solver

ADR 0014 refuses to let the **solver** grow its own second rectangle: given the
freedom it puts Ls on the wrong rooms, Spearman **+0.795** against the corpus —
positive being the wrong sign — because *"its objective knows about corner
displacement and nothing about what a room is for."*

**The conversion is the one place that argument does not apply**, and this is
where ADR 0014's reasoning gets tested rather than asserted. Its objective is
*misassigned cells against the real room*, so the ground truth is sitting in
front of it. Measured, the ordering inverts:

| room type | conversion fits 2 | ADR 0014's free solver |
|---|---:|---:|
| LIVING_DINING | **0.4219** | — |
| CORRIDOR | **0.2202** | 0.100 |
| LIVING_ROOM | 0.1718 | — |
| BEDROOM | 0.0213 | 0.295 |
| STOREROOM | 0.0046 | 0.338 |
| BATHROOM | 0.0034 | 0.282 |

The two types the conversion reaches for are the two `rectangularisation.md` §4
already named as the corpus's non-rectangular ones. *An L-shaped corridor is
L-shaped to reach a wing* — now measured being one 22 % of the time. **98.5 % of
offered second rectangles are used**, so the naming is not merely permissive.

So *the Proposal decides* is preserved exactly, not weakened: a retrieved
dwelling's corridor is an L because a real one's was. The conversion is how that
sentence becomes data.

## ⚠️ Design B is unmeasurable at the shipped budget, and that amends consequence 4

The alternative — give **every** Room an optional second rectangle and let the
fit choose — was built first and abandoned on measurement. Over 40 dwellings at
ADR 0008's 10 s limit:

| arm | s/dwelling | OPTIMAL | FEASIBLE | INFEASIBLE | UNKNOWN |
|---|---:|---:|---:|---:|---:|
| Design B | 10.38 (capped) | **0** | 26 | **0** | 14 |
| Design A | 3.64 | 30 | 6 | 3 | 1 |
| k = 1 | 0.85 | 31 | 0 | 9 | 0 |

**Zero proved either way.** `converted` degrades to *found something in 10 s*, and
the reject rule stops existing. This is ADR 0014's measured 11–12× against
1.2–1.7×, reproduced on a different solver with a different objective, and it is
the reason the naming is a pre-pass rather than a search.

**ADR 0008 consequence 4 is amended.** Its *"every Swiss dwelling resolved to
proven-optimal or proven-infeasible within 10 s, zero UNKNOWN"* held at one
rectangle and does not survive the second: **1.27 % of Swiss and 16.5 % of
ResPlan** come back UNKNOWN at 10 s. A tier is therefore *mostly* a fact about
the dwelling, and an undecided dwelling now exists and must be reported apart
from a dropped one. Every rate in §11 excludes them for that reason.

## What is preserved, asserted rather than assumed

**Every ADR 0008 guarantee holds.** Zero adjacencies destroyed, zero separation
directions flipped, zero weakened, across **69 040 axis-pairs**. These are
properties of the formulation, not of the rectangle count, and
`experiments/rectangularise/validate_k2.py` re-derives them from the emitted
geometry sharing no code with the model — along with the leg floor, the join, and
non-overlap. It passes on both arms.

**Fidelity improves rather than trading.** On the 1 779 dwellings both arms
convert: cell agreement 0.9008 → 0.9397, median room IoU 0.8900 → 0.9412, and the
**worst** room in a dwelling gains 0.157 of IoU — that being the room previously
squeezed into a box that did not fit it.

**The relations the model has to invent fall**, 15.64 % → 13.58 % of axis-pairs.
An L does not have to pick a side where the truth abstained. Smaller than the
conversion-rate move: the second rectangle rescues dwellings more than it
disambiguates pairs, and *The retrieval index and warp procedure* should still
expect one axis-pair in seven to be an assertion the corpus never made.

## Consequences

1. **ADR 0008's 69 % / 60 % become 90.3 % / 93.6 %**, and every figure downstream
   of the conversion is re-owed — above all `proposer.md` §2.2's coverage table,
   which is *The retrieval index and warp procedure*'s to restate. The quantity
   it needs is handed over measured: the per-multiset **pool multiplier**, median
   **1.219** and up to **3.53** on the multisets that thinned hardest, from
   `experiments/rectangularise/coverage_thinning.py`.
2. **This is a lower bound, and the bound is about two points of rooms wide.**
   The naming is greedy and room-local, so a Room whose best global fit wants a
   non-maximal first rectangle is invisible to it. `name_rate.py` classifies
   2 734 real rooms exactly: **2.05 %** are Ls with two legal legs that greedy
   missed, against **23.2 %** that are Ls whose short leg is under ADR 0014's
   900 mm clear floor — which is the rule working, not a defect.
3. **What is still dropped is a different population.** `LIVING_DINING`'s
   over-representation among dropped dwellings goes **1.37× → 1.02×** — the L
   absorbs exactly the interlocked open-plan dwellings ADR 0008 was losing. What
   remains is **storeroom- and bedroom-heavy** (1.57× and 1.25×), and a store is
   72 % rectangular, so its cause is not its own shape: it is a dwelling carrying
   several small ancillary rooms with more pairs to satisfy at once.
4. **Conversion costs 4.3× more CPU** — 3.65 s/dwelling against 0.85 — so ADR
   0008 consequence 5's ~17 CPU-hours for both corpora becomes roughly **70**.
   Still once, offline and parallel, and still needing a driver that survives an
   OR-Tools `CHECK` abort; `fit_rects.py --resume` is now that driver.
5. **The fidelity ladder is reduced to two rungs, A and D.** ADR 0008's tiers
   *are* the ablation arms, and re-run at k <= 2 the ladder spans **6.8 points
   where it spanned 26.4**: A 0.9320, B 0.9520, C **0.9250**, D 1.0000. A -> B
   buys **2.0 points** against 8.4 before. ⚠️ **Tier C now sits below tier A**,
   because dropping the hard relations removes the pruning that makes the search
   tractable and the arm times out — 5 UNKNOWN of 80 — so **C is unmeasurable at
   k <= 2 for the same reason Design B is, and a rung that cannot be measured
   cannot be a rung.** What is deleted is a four-valued conditioning field that
   is now 93 % one value; **retrieval's tier-A gate is untouched**, and training
   still takes every dwelling at its best rung. The two dominant reject causes
   both collapse and they were one cause in two coats — a room shape that could
   not reach: hard adjacency's grip falls **+22.0 -> +6.0 points**, the area
   band's **+17.2 -> +4.4**.
6. **ADR 0003's two-notch cap and the ±10 % area band are untouched**, and
   consequence 7's finding that more notches make conversion *worse* is
   re-confirmed rather than merely surviving: **0.8800 at four notches against
   0.9320 at two**, measured again at k <= 2. A more articulated Envelope is
   harder to tile whatever the rectangle count.
