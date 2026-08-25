---
id: 29
title: The solver has only ever seen guillotine layouts
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
blocked_by: []
writes:
  - docs/research/solver-formulation.md
  - experiments/solver-toy/
  - docs/adr/0019-the-solver-is-slicing-independent-and-the-ground-truth-keeps-two-arms.md
---

# The solver has only ever seen guillotine layouts

## Question

**Every layout this project has ever solved was produced by recursive guillotine
dissection. Real dwellings are not all guillotine, and the ones that are not have
never been solved once.**

The solver itself is innocent: `experiments/solver-toy/solver.py` posts
`AddNoOverlap2D` over free rectangles and admits **any** rectangular tiling,
pinwheels included. There is no slicing structure in the formulation. That is a
real strength and the map never states it.

The **ground truth** is the problem. `experiments/solver-toy/scenarios.py`
generates every known-good tiling with `_guillotine`, a backtracking recursive
dissection. That ground truth is what *Solver formulation for layout projection*
validated against, what *Solver timing variance sweep* perturbed to make its
Proposals, and therefore what produced **every timing, every percentile and the
entire feasibility cliff** on this map — 965 solves, all guillotine.

A **pinwheel** — four or five rooms circling a central hall, which is the
canonical real apartment plan — is not reachable by any sequence of full-width
cuts. It has never appeared in a single experiment here.

**How much of reality that misses**, measured on the converted corpus from
*Rectangularising real rooms* (`guillotine_share.py`, 1,787 real dwellings
expressed as rectangles):

| rooms | dwellings | guillotine |
|---:|---:|---:|
| 4 | 161 | 0.9814 |
| 5 | 328 | 0.9726 |
| 6 | 430 | 0.9605 |
| 7 | 365 | 0.9589 |
| 8 | 277 | **0.8628** |
| 9 | 168 | 0.8750 |
| 10 | 58 | **0.8448** |
| **all** | **1,787** | **0.9373** |

**6.27 % overall and ~15 % at 8–10 rooms** — and that is an *overstatement* of the
guillotine share, because the test lets a cut pass through an Envelope notch. The
untested class is concentrated at the top of C13's band, which is exactly where
the sweep already found the solver most fragile.

**What has to be decided:**

1. **Does the solver actually handle non-guillotine targets as well?** Re-run the
   sweep with pinwheel ground truths. Time-to-VALID, feasibility, and the σ cliff
   are all suspect until it does. This is the whole ticket; everything else is
   consequence.
2. **Whether `scenarios.py` should generate them at all.** A backtracking
   guillotine dissection is a convenient generator, not a faithful one. Either
   extend it, or seed ground truth from **real converted dwellings** —
   `fit_rects.py` now produces exactly that, and a real tiling is a stronger
   fixture than a synthetic one.
3. **Whether ADR 0007 and the τ figure survive.** Both were fitted on guillotine
   layouts. τ is a valve on relation-hardness and a pinwheel has a denser
   relation graph than a slicing layout, so there is a specific reason to expect
   movement rather than a general one.
4. **Whether this changes the two-phase fallback's expected firing rate.** The map
   parks *The Proposal-quality floor, and how often the fallback fires* as fog; if
   non-guillotine targets are harder, the fallback fires more on exactly the
   dwellings retrieval most wants to serve.

**Not this ticket.** Whether the solver *should* restrict to guillotine. It should
not, it does not, and restricting it would delete 6 % of real homes for
implementation convenience — which is the trade *Rectangularising real rooms*'
amendment already refused once.

**Deliverable.** A sweep over non-guillotine ground truths, on the same machine
and the same harness, reported against the guillotine baseline in
`docs/research/solver-formulation.md` Part II. If nothing moves, that is a
one-paragraph finding and a real de-risking. If something moves, ADR 0007's
arithmetic and the shipped 15 s / τ = 4 are both in play.

## Inherited from *Area measurement convention* — a second sweep to ride along

ADR 0010 moved `t_int` from **120 to 150** — it is now a layer-set total, 120
structural + 2 × 15 finish. **Every solver number on this map was fitted at
`t_int` = 120**, alongside the 250 mm grid and the 100%-exterior-exposure caveat
this ticket already carries.

Most of it is expected to move very little: ADR 0001's erosion is a constant, and
*Solver timing variance sweep* found solve time is barely sensitive to Proposal
quality, let alone to a 30 mm constant. **One result is not safe to assume
unchanged**, and it should be recomputed while `experiments/solver-toy/` is
already open:

**Ticket 19's room-count deletion.** Its finding — the 4/5/6-room deletion
narrowing to *{5, and 6 unknown}*, so **250 mm is charging the 5-room case** —
falls straight out of `250w − t ≥ min_w` and therefore out of `t`. At 150 the ADR
0007 residue class is **100 mod 250**, not 130. Whether the deleted set grows,
shrinks or moves is **not obvious and is deliberately not guessed anywhere on this
map**. It feeds *Whether the solve grid should be finer than 250 mm*, which is the
one fog patch already flagged as load-bearing rather than curious.

This is a second sweep in the same harness, not a redesign of this ticket. Its own
question — that every solve so far has been over guillotine-cuttable layouts — is
untouched by any of the above and stays the headline.

## Resolution

**The solver does not care, and the untested strength is now a measured one.**
ADR [0019](../../adr/0019-the-solver-is-slicing-independent-and-the-ground-truth-keeps-two-arms.md).
Findings `docs/research/solver-formulation.md` **Part III**. Harness
`experiments/solver-toy/` — `pinwheel.py`, `sweep_ng.py`, `report_ng.py`,
`relation_margins.py`, `t_int_arithmetic.py`, `pinwheel_area_premium.py`,
`corpus_guillotine.py`. **483 solves** over 568 scenario slots (85 never reached
the solver: 72 Envelopes admit no non-guillotine tiling, 13 could not be typed),
serial at 4 workers, on the same 4-core
Ivy Bridge (`DESKTOP-25OJ4QH`) every number in Parts I and II came from — the
"same machine and same harness" the deliverable asked for.

Paired across arms: same Envelope, room count, exposure, seed, Proposal noise and
config, with **only the cut structure of the target moving**.

| | guillotine | pinwheel |
|---|---:|---:|
| survivors, main grid | 76.9 % | 74.5 % |
| time to VALID p90 | 10.41 s | **9.56 s** |
| time to VALID max | 14.57 s | **12.24 s** |
| share caught by 15 s | 76.9 % | 74.5 % |
| pairs τ fixes at 4 | 0.8683 | 0.8730 |

Paired survivor count over the main grid: **37 both, 10 neither, 4 only-guillotine,
4 only-pinwheel — exact McNemar p = 1.00.** At 8–16 rooms the discordant count is
**zero** over 35 slots. **Nothing moves. ADR 0007, the 15 s limit and τ = 4 all
stand at their published values, and Part II's percentiles need no re-derivation.**

The treatment is not marginal: `guillotine_residue` puts **21 of 24 rooms** in one
block no sequence of cuts decomposes, against 1 for the baseline by construction.
Every pinwheel ground truth was re-checked with the independent validator before
use, so it stays a witness and a failure to solve stays a fact about the
projection problem.

### Item 4 inverts, and it is the strongest result here

The ticket's worry: *"if non-guillotine targets are harder, the fallback fires
more on exactly the dwellings retrieval most wants to serve."* **The sign is the
other way.** INFEASIBLE is what triggers the two-phase fallback, and pooled over
every suite, paired on the same slot:

| | count |
|---|---:|
| paired slots | 212 |
| both arms INFEASIBLE | 12 |
| **only the guillotine arm** | **17** |
| **only the pinwheel arm** | **2** |

Exact McNemar **p = 0.0007**, and it is spread across σ and room count rather than
concentrated — 7 against 0 at the shipped σ = 0.5 alone, over 160 slots.
⚠️ **The mechanism is unexplained and the three obvious candidates are excluded**:
separation-margin distributions, the share of pairs τ fixes, and the fraction of
pairs the truth separates on one axis are all matched between arms. Recorded as an
open mechanism rather than given a story.

### ⚠️ The ticket's own reason for expecting τ to move is refuted

*"A pinwheel has a denser relation graph"* is **true** — door-contact density is
higher at every room count, 0.521 against 0.461 at 8 rooms. The inference is
false, because **τ does not gate on adjacency.** It gates on the separation margin
over the Proposal, and measured over 14 465 pairs those distributions are
identical to the grid unit — p10 through p90 exactly 3 / 7 / 14 / 24 / 34 in both
arms, mean 16.55 against 16.71. Adjacency reaches the model through reified
contact literals, which carry no confidence margin at all. **There was never a
channel for τ to move through**, which is why suite B finds nothing and why that
null result is trustworthy despite suite B being underpowered.

### ⚠️ No experiment on this map has ever run at `t_int` = 120

This ticket's inherited section and **ADR 0010 consequence 3** both say the solver
numbers were fitted at 120. They were fitted at **100** — `sweep.py` line 59,
`SolveConfig.t_int_mm`, `ergonomic_minima_tiling.py`, `grid_aligned_minima.py`,
`erosion_cost.py`, `probe6.py`, all of them, inherited from `annotation.md` §14
which ADR 0010 §6 itself calls stale. A grep for 120 on any solver path returns
nothing; 120 was the AZ profile's value and never reached the harness.

So the move made is **100 → 150** — 50 mm, two thirds larger than the instruction
assumed — and the ADR 0007 residue class moves **150 → 100 (mod 250)**, not
130 → 100. Both documents name the right destination and the wrong origin.

### The inherited sweep: the cost is real, and it is not in the solver

**Half one — the linear minima provably cannot move.** `250w − t ≥ 250·min` gives
`w ≥ min + ⌈t/250⌉` and **⌈t/250⌉ = 1 for every `t` in (0, 250]**. For any minimum
that is a whole number of grid units, 100, 120 and 150 impose *identical* bounds.
Zero of ten placeholder room types move. Not "very little" — exactly nothing.

**Half two — the eroded area moves**, and it is the only channel by which `t_int`
reaches a solve. Against the placeholder table 7 of 10 room types need a bigger
grid rect at 150; against the derived ergonomic floor, 0 of 10.

**Half three — the shipped ergonomic layer, and this is where it lands.** ADR 0009
exempted that layer from ADR 0007's congruence and priced the exemption once, at a
`t_int` nothing now ships. **At 100 the residue class is 150 (mod 250), and 900,
1400, 1650, 1900 and 3150 mm are all congruent to it — 12 of 36 clear dimensions
were on the lattice by accident.** At 150 only 6 are, and **14 of 36 gain a whole
grid unit**: a 900 mm minimum delivered at exactly 900 is now delivered at 1 100.
Summed waste over the table **2 524 → 4 224 mm**. ADR 0009's *argument* is
untouched — a derived minimum has no nominal-to-clear conversion to apply — but
its *price* rose 67 % and nobody had recomputed it.

**The sweep half is directional and not significant.** Paired at both `t_int`
values: 26 both, 9 neither, **5 lost at 150, 1 gained, p = 0.219**. Three further
pinwheel scenarios stopped being constructible at all. **Every loss is at 16 rooms
or above**; at 8, 10 and 12 the discordant count is zero in both arms.
**`t_int` = 150 costs nothing inside C13's band**, and above it the cost must be
quoted as directional, never as a measured penalty.

### Item 2 — `scenarios.py` keeps both arms, and the default stays guillotine

The ticket frames "extend the generator" and "seed from real converted dwellings"
as alternatives. **They are not.** A synthetic generator is the only thing that can
hold Envelope, room mix, seed and noise fixed, which is the entire force of the
paired result; real dwellings bring their own Envelopes and areas, so a sweep over
them measures corpus-versus-fixtures, a different and also-worthwhile question that
needs a path for a converted Envelope into `envelope_for` which does not exist
today. Re-basing the default would invalidate the comparability of every published
number — the thing this ticket exists to protect.

### ⚠️ This ticket's own motivating table is stale, and understates by 2.5×

The 6.27 % headline was measured on the **k = 1** conversion, which ADR 0016
superseded. Re-measured paired — `fit_rects.py 600` against `fit_rects.py 600
--k2`, same dwellings, same order, only `k_of` differing, 419 converted by both:
**non-guillotine 5.49 % → 13.60 %**, 40 dwellings moving across against 6 back,
exact McNemar **p = 3.1 × 10⁻⁷**. Rectangles per dwelling 6.57 → 7.02, which is
the mechanism — ADR 0014's second rectangle is exactly what blocks a cut. The
k = 1 arm reproduces the published 0.9373 at 0.9451, so this is the conversion
moving and not the sample. **The untested class was one real dwelling in seven,
not one in sixteen**, which makes the null result above stronger rather than
weaker. ⚠️ 419 dwellings, not 1,787 — the k ≤ 2 fit is ~4 s a dwelling and was
stopped at its 600 checkpoint; per-*n* cells above 8 rooms are thin and should not
be quoted on their own.

### ⚠️ Two findings about the fixtures, not about pinwheels

**Below 7 rooms this Envelope family has no non-guillotine tiling at all.** The
L-shape's notch forces the second part to hold two rooms, leaving the main part
four or fewer, and four rectangles are always guillotine. **The bottom of C13's
3–10 band still has no non-guillotine measurement of any kind**, and cannot get one
without a different Envelope generator.

**`AREA_PER_ROOM_M2` = 9.65 is below what the placeholder table needs at 7 and 8
rooms in *either* arm** — both need 11.58. Part II's small-*n* cells are partly
measuring a generator that cannot always build the dwelling it is asked for. The
genuine non-guillotine premium on top of that is **+14 % at 7 rooms, +5 % at 10,
zero from 12 up**.

### What was not established

- No real dwelling was solved; the treatment is one synthetic shape family.
- The 24-room difference is unresolved — 2–0 to guillotine at 15 s, 6/8 against
  2/8 at 30 s, on 8 solves a cell. Both arms fail there on **coverage slack, not
  infeasibility**, which is C6's discard case. It sits well outside the v1 gate.
- Suite C was **mis-designed** and says so: it picked 8 and 24 rooms, where 8
  admits no pinwheel and 24 is saturated. Suite E replaces it at 10/12/16; C is
  kept because its n = 24 cliff location is the only direct comparison with Part
  II's own σ grid, and that cliff sits between σ = 0.25 and 0.5 **in both arms**.
- The grid is still never swept. Half three makes that fog patch heavier, not
  lighter: a finer grid is what makes ADR 0009's exemption cheap, and the
  exemption just got dearer.
