---
id: 58
title: Every Envelope the solver has seen is invented
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: []
writes:
  - experiments/rectangularise/
  - docs/research/rectangularisation.md
  - experiments/solver-toy/
  - docs/research/solver-formulation.md
---

# Every Envelope the solver has seen is invented

## Question

**No Envelope on this map is a real dwelling's boundary, and the whole published
field conditions on one.** Both fixtures in `experiments/solver-toy/` are
parametric: a bounding box minus at most two notch rectangles, sized from a
formula. *The toy Envelope is more compact than a real dwelling* fitted the
second one to real dwellings on **area, perimeter and bounding-box occupancy** —
ADR 0029, within 0,7 % at every count from 5 to 11 — but a fitted summary is not
a boundary. What is still untested is whether the *shape* matters once those
three moments are matched.

This is the one place the map departs from every product it is measured against.
`docs/research/floorplan-generation-stack.md` reads about twenty published
generators; **HouseGAN++, HouseDiffusion, Graph2Plan and WallPlan all condition
on a boundary drawn from their dataset**, and none fits a parametric envelope
generator. ADR 0029 declined it for a stated reason — the conversion directory
was claimed — and charted it here rather than doing it blind.

## Why it is worth its own ticket rather than a caveat

Three shipped numbers are measured on invented Envelopes and nothing else:

1. **The 15 s job budget and τ = 4** (Part II, ADR 0019). C6 discards a candidate
   whose best objective is ≥ `soft_weight`, so the budget *is* the survivor rate,
   and the survivor rate is measured on a boundary family with a known structural
   property no real dwelling has.
2. **ADR 0019's slicing independence.** Its 483 solves ran on Envelopes with at
   most two notches and, until ADR 0029, boundaries exactly equal to their own
   bounding box perimeter.
3. **ADR 0014's two-rectangle cap.** Measured on the same family.

ADR 0029 already found that the family's structure was doing hidden work: every
notch it cut was a **corner** notch, which removes floor and adds *no perimeter*,
so no notch share and no notch count could give it a real dwelling's
articulation. That defect survived four closed decisions unnoticed. A second
structural property of the same kind is exactly what a real-boundary arm would
catch.

## What has to be settled

1. **Whether a real boundary is representable at all.** ADR 0003 is a rectilinear
   ring of typed edges with **at most two notches**, and *The two-notch cap is now
   evidenced* measured the refusal: two notches describe **61,8 %** of real
   dwellings exactly, and **4,17 %** are still above 0.10 envelope loss at four
   notches. So a faithful real-boundary arm and the shipped Envelope object
   **disagree by construction on about a third of the corpus**. Decide what the
   arm does with those: rectangularise onto the cap and measure the loss, or
   carry the true outline and accept that the arm is testing something the
   shipped object cannot express.
2. **Where the boundary comes from.** `experiments/rectangularise/out/swiss_dw.pkl`
   holds 46 800 dwellings as room polygons; welding them and typing the boundary
   is `envelope-exposure/fit_presets.py`'s procedure, already written. The
   rectilinear conversion onto the 250 mm grid is `rectangularise/`'s competence
   and is why this ticket claims that directory.
3. **What the arm measures.** The honest minimum is `fixture_delta.py`'s design
   with a third arm: matched `(n, exposure, seed)`, shipped config, survivor rate
   and time-to-VALID. If the real arm agrees with the corpus-fitted one, ADR 0029
   is discharged and the parametric family is vindicated for good; if it does
   not, the 15 s budget is measured on the wrong population.
4. **Whether exposure stays a preset.** A real boundary carries its own edge
   typing, so `EXPOSURE_PRESETS` becomes a *property of the sampled dwelling*
   rather than a knob. `dwelling_sides.json.gz` already holds per-side exterior
   run for 2 238 dwellings. That may retire the preset family, which
   `fit_presets.py` already measured as naming only **10,6 %** of real ring
   shapes across its three flat presets.

## What this does NOT decide

- **The published fixture's status.** Frozen by ADR 0029 and not reopened: it is
  the substrate of four closed decisions and it stays bit-exact.
- **`EXPOSURE_PRESETS` becoming `n`-dependent.** Refused by ADR 0029 on the
  grounds that it would hide an Envelope defect inside a preset. Item 4 above is
  a different question — retiring the preset, not reshaping it.
- **The two-notch cap.** Evidenced and closed by *The two-notch cap is now
  evidenced*, ADR 0003's amendment. Item 1 decides what the arm does *within* the
  cap, not whether the cap moves.

## Concurrency

⚠️ It shares `experiments/rectangularise/` and `docs/research/rectangularisation.md`
with **[The dwelling that is built on two angles](46-the-dwelling-that-is-built-on-two-angles.md)**,
and `experiments/solver-toy/` and `docs/research/solver-formulation.md` with
**[What an ordered entry sequence costs the solver](43-what-an-ordered-entry-sequence-costs-the-solver.md)**
and **[The toy Envelope is more compact than a real dwelling](52-the-toy-envelope-is-more-compact-than-a-real-dwelling.md)**.
Four artifacts, three other tickets: **this is the widest write-set on the map**
and the concurrency rule binds hard. 46 in particular is close in subject — it
decides what the conversion does with a dwelling built on two angles, and a
two-angle dwelling is exactly one whose boundary this ticket cannot use.
Take it when the frontier is quiet, as *The plan has no vertical dimension* and
*Whether a Room may be more than one rectangle* were taken.

## Raised by

*The toy Envelope is more compact than a real dwelling* (2026-08-28), ADR 0029,
which took the parametric route deliberately and recorded this as the option not
taken.
