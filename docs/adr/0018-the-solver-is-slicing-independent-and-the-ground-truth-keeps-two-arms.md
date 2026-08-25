# The solver is slicing-independent, and the ground truth keeps two arms

**Status:** accepted
**Date:** 2026-08-25
**Ticket:** *The solver has only ever seen guillotine layouts*
**Confirms:** [ADR 0007](0007-published-minima-must-erode-onto-the-solve-grid.md) —
unchanged, and its residue class corrected from the record rather than re-fitted
**Corrects:** [ADR 0010](0010-a-space-is-bounded-by-finished-faces.md)
consequence 3 — no experiment on this map was ever run at `t_int` = 120
**Related:** [ADR 0016](0016-the-conversion-names-its-own-ls.md) — its second
rectangle is what makes a real dwelling non-guillotine,
[ADR 0001](0001-centreline-walls-over-a-dilated-solve-domain.md),
[ADR 0009](0009-a-derived-minimum-is-not-rounded-onto-the-solve-grid.md),
[ADR 0013](0013-the-room-count-promise-is-two-numbers-in-two-units.md),
[ADR 0014](0014-a-room-is-one-or-two-rectangles-and-the-proposal-decides.md)

## Decision

**The projection model is not restricted to guillotine layouts, and this is now
measured rather than assumed. `scenarios.py` keeps the guillotine dissection as
its default and gains a non-guillotine generator beside it as a controlled second
arm — never as a replacement.**

Three shipped figures are re-affirmed unchanged at their published values: the
**15 s** time limit, **τ = 4**, and ADR 0007's congruence rule. Nothing in C10
moves.

Findings: `docs/research/solver-formulation.md` **Part III**. Harness
`experiments/solver-toy/sweep_ng.py`, generator `pinwheel.py`. **483 solves** over
568 scenario slots, on the same 4-core machine as Parts I and II.

## Why this needed deciding at all

The formulation always admitted any rectangular tiling — `AddNoOverlap2D` has no
slicing structure in it. But `scenarios.ground_truth` dissects every Envelope by
recursive guillotine cuts, so all 965 solves behind Part II had a target some
sequence of full-width cuts takes apart. **A pinwheel — four rooms circling a
central one, the canonical real apartment plan — had never been solved here
once.** The strength was real and untested, and an untested strength is a claim.

The exposure was not small, and it was **larger than the ticket knew**. Its
motivating table — 6.27 % of real dwellings non-guillotine — was measured on the
**k = 1** conversion ADR 0016 superseded. Re-measured paired on the shipped k ≤ 2
conversion, 419 dwellings, only `k_of` differing: **5.49 % → 13.60 %**, 40 moving
to non-guillotine against 6 back, exact McNemar **p = 3.1 × 10⁻⁷**. ADR 0014's
second rectangle is precisely the piece that blocks a cut. **The untested class
was about one real dwelling in seven, not one in sixteen** — which makes the null
result stronger, not weaker.

## What was measured

Paired across arms — same Envelope, room count, exposure, seed, Proposal noise
and config, with **only the cut structure of the target moving**. The treatment is
not marginal: `guillotine_residue` puts **21 of 24 rooms** in one block no
sequence of cuts decomposes, where the baseline arm is 1 by construction. Every
pinwheel ground truth was re-checked with the independent validator first, so it
remains a witness and a failure to solve stays a fact about the projection
problem.

| | result |
|---|---|
| survivors, whole main grid | 37 both, 10 neither, **4 only-guillotine, 4 only-pinwheel**, McNemar **p = 1.00** |
| survivors, 8–16 rooms | **zero discordant** over 35 slots |
| time to VALID, p90 | 10.41 s guillotine, **9.56 s** pinwheel |
| 15 s budget | 76.9 % against 74.5 % |
| τ, share of pairs fixed at 4 | 0.8683 against 0.8730 — ratio **1.005** |
| INFEASIBLE, paired over every suite | 12 both, **17 only-guillotine, 2 only-pinwheel**, McNemar **p = 0.0007** |

## Consequences

1. **C10 is de-risked, not qualified.** *Model proposes, solver projects* holds
   over a target class it had never been shown. The 15 s limit and τ = 4 stand at
   their Part II values, and Part II's percentiles do not need re-deriving.

2. **The two-phase fallback fires *less*, not more.** The ticket's worry was that
   non-guillotine targets would push the fallback onto exactly the dwellings
   retrieval most wants to serve. The sign is inverted and significant — 17
   against 2 discordant INFEASIBLE, p = 0.0007, spread across σ and room count
   rather than concentrated. This **sharpens the fog patch** *The Proposal-quality
   floor, and how often the fallback fires* rather than settling it: the
   distribution still needs a real Proposer.
   ⚠️ **The mechanism is unexplained and the obvious candidates are excluded** —
   separation-margin distributions, the share of pairs τ fixes, and the fraction
   of pairs the truth separates on one axis are all matched between arms.

3. **The ticket's own reason for expecting movement is refuted.** A pinwheel's
   *adjacency* graph is denser at every room count, but **τ does not gate on
   adjacency** — it gates on the separation margin over the Proposal, and those
   distributions are identical to the grid unit. Adjacency reaches the model
   through reified contact literals, which carry no confidence margin. There was
   never a channel for τ to move through.

4. **The generator keeps two arms and the default stays guillotine.** Re-basing
   the default would invalidate every published number's comparability, which is
   the thing this ADR exists to protect. Seeding ground truth from real converted
   dwellings — the ticket's other option — is **not** an alternative to this: it
   brings its own Envelopes, areas and room mixes, so it cannot hold anything
   fixed and could not have produced the paired result. It answers a different and
   also-worthwhile question, and needs a path for a converted Envelope to enter
   the harness that `envelope_for` does not have.

5. **ADR 0010 consequence 3 is corrected at its premise.** It says ticket 19's
   deletion analysis *"was computed at `t_int` = 120"*. It was computed at **100**,
   as is every other solver number on this map — `sweep.py` line 59,
   `SolveConfig.t_int_mm`, `ergonomic_minima_tiling.py`, `grid_aligned_minima.py`,
   `erosion_cost.py`, `probe6.py`. The 120 was the AZ profile's value and never
   reached the harness. So the move made is **100 → 150**, and the ADR 0007
   residue class moves **150 → 100 (mod 250)**, not 130 → 100. The instruction to
   recompute was right; its arithmetic was not.

6. **ADR 0009's exemption is more expensive than when it was priced, and nobody
   had noticed.** The linear minima are *provably* invariant across the whole
   range — `⌈t/250⌉ = 1` for every `t` in (0, 250], so 100, 120 and 150 impose
   identical grid bounds on any minimum that is a whole number of grid units. But
   the shipped ergonomic layer is millimetres and ADR 0009 exempted it from the
   congruence. At `t_int` = 100 **12 of its 36 clear dimensions were congruent by
   accident** — 900, 1400, 1650, 1900 and 3150 mm are all 150 (mod 250). At 150
   only 6 are, and **14 of 36 gain a whole grid unit**: a 900 mm minimum that was
   delivered at exactly 900 is now delivered at 1 100. Summed waste over the table
   goes **2 524 mm → 4 224 mm**.
   This does not reopen ADR 0009 — its argument was that a *derived* minimum has
   no nominal-to-clear conversion to apply, which is untouched by arithmetic. It
   re-prices it, and it lands on **the standards table, not the solver**, which is
   not where the instruction was looking. It also makes *Whether the solve grid
   should be finer than 250 mm* heavier: a finer grid is what makes the exemption
   cheap, and the exemption just got 67 % dearer.

7. **`t_int` = 150 costs nothing inside C13's band.** Paired at both values: 26
   both, 9 neither, 5 lost at 150, 1 gained, **p = 0.219 — not significant**, and
   **every loss is at 16 rooms or above**. At 8, 10 and 12 rooms the discordant
   count is zero in both arms. Above the band the cost is directional and must be
   quoted as directional, never as a measured penalty.

8. **A fixture defect is on the record.** `AREA_PER_ROOM_M2` = 9.65, fitted to
   Part I's three published Envelopes, is **below what the placeholder table needs
   at 7 and 8 rooms in either arm** — both need 11.58. Part II's small-*n* cells
   are partly measuring a generator that cannot always build the dwelling it is
   asked for. Separately, the genuine non-guillotine floor-area premium is
   **+14 % at 7 rooms, +5 % at 10, and zero from 12 up**.

9. **The bottom of the band is still unmeasured, and unmeasurable as the harness
   stands.** Below 7 rooms this Envelope family offers no non-guillotine tiling at
   all: the L-shape's notch leaves the main part four rooms or fewer, and four
   rectangles are always guillotine. C13's gate opens at 3.

## What this does not decide

Whether the solver *should* restrict to guillotine. It should not, it does not,
and restricting it would delete about 6 % of real homes for implementation
convenience — the trade ADR 0008's successor already refused once. Part III
removes the last reason anyone might have had to consider it: there is no
measured penalty to pay for the generality.
