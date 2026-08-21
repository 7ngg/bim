---
id: 29
title: The solver has only ever seen guillotine layouts
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: []
writes:
  - docs/research/solver-formulation.md
  - experiments/solver-toy/
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
