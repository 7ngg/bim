---
id: 58
title: Every Envelope the solver has seen is invented
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
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

## Resolution

**The arm is built and run. The solver is not what fails on a real boundary —
three things upstream of it are, and each is now isolated with a number.**
ADR 0030; `docs/research/solver-formulation.md` Part V;
`docs/research/rectangularisation.md` §14.

### The ticket's four items

**Item 2 — where the boundary comes from — was not a decision.** It is
`keep_largest_component(watershed(geoms)) >= 0`, the 250 mm cell mask
`envelope_approx` already measures ADR 0003's notch loss against. No new
convention, and every figure below is comparable with `notches_all` and
`envelope_loss_by_k` in the same fit record rather than merely similar to it.

**Item 1 — is a real boundary representable — is answered harder than the ticket
expected, and it reshaped the rest.** The quantity is the *exact* minimum
rectangle partition (Lipski/Ohtsuki, verified against eight hand-checkable
shapes; on two of them the hand expectation was the wrong one):

| | `Envelope.parts` | min rectangles | reflex vertices |
|---|---:|---:|---:|
| published fixture | 2 | **2** | 1–2 |
| corpus fixture (ADR 0029), n ≥ 6 | 4 | **4** | 3 |
| **real dwelling** | — | **6** median, 12 at p90, 44 max | **6** median, 15 at p90 |

**12,4 %** of the converted index is three rectangles or fewer. The ticket's
framing — *rectangularise onto the cap, or carry the true outline* — turned out
to be the wrong fork: both were run, as rungs of a ladder, and the informative
comparison was the one nobody had asked for (`corpus` → `cap`).

**Item 3 — what the arm measures.** `fixture_delta.py`'s design with a third arm,
as the ticket specified, but as a **ladder** so the two ways a real dwelling
differs from `CORPUS_ENVELOPES` are separated:

| arm | slots | reached the solver | survivors | valid but for tiling | INFEASIBLE | `no_brief` | wall p50 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `corpus` | 120 | 106 | **106** (88,3 %) | 0 | 0 | 14 | 0,19 s |
| `cap` | 120 | 50 | 48 (40,0 %) | 2 | 0 | **70** | 3,30 s |
| `real` | 120 | 57 | **2** (1,7 %) | **53** | 2 | 63 | **10,11 s** |

Exact McNemar: 62–4, 46–0, 104–0, all **p = 0,0000**.

**Item 4 — does exposure stay a preset. Yes, and the reason is measured rather
than assumed.** A third of a real boundary lies off its own bounding box, which
looked fatal for a four-vector over bbox edges. The notch branch of `_faces_of`
recovers it: `exterior_fraction` is **0,766** on a real outline against **0,786**
on its cap approximation. `EXPOSURE_PRESETS` is not retired.

### What actually refuses, in order

1. **`ground_truth` cannot dissect a per-dwelling Envelope.** Not a shape
   finding: the `cap` arm *is* ADR 0003's object, and it loses **70 of 120**
   slots where `corpus` loses 14. **Per-dwelling sampling alone, at a fixed shape
   family, costs more than half the survivors** — and every fixture on this map
   is a per-count median, which is dissectible in a way its own population is not.
2. **`assign_kinds` cannot type a real dwelling**, and `real_typing.py` settles
   which constraint it is without a solver: **not size** (2,0 % of real Rooms fit
   no toy type), **not edge typing** (above), but the **programme** —
   `COMPOSITION` demands a median 5 habitable Rooms against a median 4 cells that
   are both exterior-facing and habitable-sized. Short in 23,3 % of dwellings at
   `detached`, **50,0 %** at `corpus_median`. ⚠️ This is the **toy's**
   `composition` and `STANDARDS`, not `room-constraints.json`.
3. **Exact tiling.** Of the 57 solved slots, 55 are valid on every hard
   predicate other than tiling; **2 tile exactly and survive, and 53 fail on
   unassigned floor alone** —
   median **17 cells = 1,06 m²**, p90 60, max 92. The witness fails the same way
   (57 invalid, **50 tiling-only**), which is the tell that it is the conversion's
   residue and not the solver's error.

### The pre-registered rule fired, and it was the wrong rule

Written before the run: *paired McNemar at p < 0,01 with the real arm losing
survivors reopens the 15 s budget.* It fires at 104–0. **The conclusion does not
follow**: the rule assumed the arms differ only in the solve, and 63 of 120 real
slots never reach it while 55 of the 57 that do come back valid. Recorded rather
than reinterpreted — that is what pre-registration is for.

**The budget is not refuted and is closer to binding than it looked.** No
survivor waited more than 1,68 s to become valid; wall p50 goes
0,19 → 3,30 → **10,11 s** and p90 reaches the cap on both real-sampled arms.

### Two things found that were not looked for

- **The six-room hole belongs to `envelope_for(6)`, not to six rooms.** ADR 0029
  left n = 6 as the one uncovered cell in C13's band. On `cap`, **4 of 14** slots
  survive there against `corpus`'s **0 of 14**.
- **A converted dwelling is not a witness for its own boundary.** Its recorded
  rectangles are fitted to the cap Envelope, a superset, so against the true
  outline they fail H1 *and* H3 — seven of the first eight slots. It reads as a
  coordinate bug and is not one. `real_envelope.refit_to_true_mask` substitutes
  the domain at `fit_rects`' call boundary; **`fit_rects.py` is not edited**. The
  re-fit is materially harder: **11 of 71** in-band dwellings (15,5 %) cannot be
  re-fitted to their own boundary at the same 10 s budget.

### What this does NOT establish

- **That 15 s or τ = 4 is wrong.** Zero real slots failed for time, two went
  INFEASIBLE.
- **That a real boundary is infeasible for the solver.** The opposite: 55 of 57.
- **A clean shape effect.** `cap` → `real` moves boundary *and* ground-truth
  source together; the re-fit was forced.
- **Anything about the shipped room table**, or about ResPlan, or outside
  5–11 rooms, one seed, 60 dwellings.
- **That widening ADR 0003 would help.** Not priced. §13.3 refused it on separate
  evidence.

### Artifacts

- `experiments/rectangularise/real_boundary.py` — exact minimum partition and the
  two `_leaf_ok` heuristics; series `series/real_boundary.json.gz`.
- `experiments/rectangularise/real_envelope.py` — the `cap` and `real` Envelopes
  and the true-mask re-fit; series `series/real_envelopes.json.gz`.
- `experiments/solver-toy/real_typing.py` — which constraint refuses a Brief, no
  solver, one second.
- `experiments/solver-toy/real_arm.py` — the ladder; `results/REAL_ARM.jsonl`.
- `docs/research/rectangularisation.md` §14, `docs/research/solver-formulation.md`
  Part V, ADR 0030, and `CONTEXT.md` (declared on resolution — it had no
  claimant): **Real boundary** is a new term, **Representable** gains its Envelope
  half, and **Witness** gains an `_Avoid_` because the drawing sense and the
  solver-harness sense share no referent and both ship.
