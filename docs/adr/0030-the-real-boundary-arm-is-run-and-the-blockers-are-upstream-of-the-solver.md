# The real-boundary arm is run, and every blocker is upstream of the solver

**Status:** accepted
**Date:** 2026-08-28
**Ticket:** *Every Envelope the solver has seen is invented*
**Discharges:** [ADR 0029](0029-the-toy-envelope-gains-a-corpus-fitted-arm-and-the-published-one-is-frozen.md)'s
*"the option not taken"* — the real-boundary arm exists, is run, and its result
is recorded here
**Confirms:** [ADR 0003](0003-the-envelope-is-an-ordered-ring-of-typed-edges.md),
[ADR 0014](0014-a-room-is-one-or-two-rectangles-and-the-proposal-decides.md),
[ADR 0019](0019-the-solver-is-slicing-independent.md) — none moves, none is re-run
**Related:** [ADR 0028](0028-the-enclosed-void-is-charged-to-a-room-and-bounded.md),
[ADR 0013](0013-the-room-count-promise-is-two-numbers-in-two-units.md)

## Decision

**v1's Envelope does not change, and the external-validity gap is now a *stated
limit with a mechanism* rather than an open question.**

Parts I–III measure the projection problem on a fixture the harness can pose a
Brief for. A real dwelling's boundary is largely not in that population, and the
three things that exclude it are all **upstream of `project()`**:

1. `ground_truth` cannot dissect a **per-dwelling** Envelope — even one inside
   ADR 0003's own shape family.
2. `assign_kinds` cannot type a real dwelling, because the toy's `COMPOSITION`
   demands more habitable Rooms than a real dwelling of that size supplies.
3. Exact tiling. A real dwelling's own Rooms do not tile its own boundary at
   ADR 0014's two-rectangle cap, and `model.no_unassigned_area` is hard.

None of these is the solver, and **none is repaired here.** Widening ADR 0003,
rebuilding `ground_truth` for general rectilinear regions, and re-fitting the
toy's programme model are three separate decisions with their own costs; this
ADR closes the *question* of whether the arm can be run and what it says, not
those.

## What the arm measured

`experiments/solver-toy/real_arm.py`, a three-rung ladder — `corpus` /
`cap` / `real` — 60 dwellings × 2 exposures × 1 seed × 3 arms = **360 solves**,
shipped config verbatim, paired on `(dwelling, exposure, seed)`.

| arm | slots | reached the solver | survivors | valid but for tiling | INFEASIBLE | `no_brief` | wall p50 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `corpus` | 120 | 106 | **106** (88,3 %) | 0 | 0 | 14 | 0,19 s |
| `cap` | 120 | 50 | 48 (40,0 %) | 2 | 0 | **70** | 3,30 s |
| `real` | 120 | 57 | **2** (1,7 %) | **53** | 2 | 63 | **10,11 s** |

Exact McNemar: `corpus` vs `cap` 62–4, `cap` vs `real` 46–0, `corpus` vs `real`
104–0, all at **p = 0,0000**.

> **Of the 57 real slots that reached the solver, 55 returned a candidate valid
> on every hard predicate other than exact tiling, and 2 went INFEASIBLE.** Of
> those 55, **2 tiled exactly and survived and 53 failed on left-over floor
> alone** — a median **1,06 m²**, ADR 0028's enclosed void at plan scale.

## The measurement that reframed the ticket

The ticket asked what a real boundary costs the solver. Before it could be asked,
`experiments/rectangularise/real_boundary.py` had to establish whether a real
boundary is an Envelope at all. It is not, and the margin is not close.

The **exact** minimum rectangle partition of a real dwelling's interior on the
250 mm grid — Lipski/Ohtsuki, verified against eight hand-checkable shapes:

| | `Envelope.parts` | min rectangles | reflex vertices |
|---|---:|---:|---:|
| published fixture | 2 | **2** | 1–2 |
| corpus fixture (ADR 0029), n ≥ 6 | 4 | **4** | 3 |
| **real dwelling** | — | **6** median, 12 at p90, 44 max | **6** median, 15 at p90 |

**12,4 % of the converted index comes in at three rectangles or fewer.** ADR
0029's fixture is a genuine improvement on this axis — 4 against 2 — and it still
sits at the corpus **p25**. Three matched moments do not carry the fourth.

Two consequences follow without any solver: **39,3 %** of the index needs more
rectangles than it has rooms, so `ground_truth` refuses it outright; and under
two partition heuristics that fail in opposite directions, only **3–4 %** of
dwellings have every part clearing `_leaf_ok`, and **1,4 %** have every part wide
enough for a habitable room.

## Consequences

1. **No published number moves and nothing is re-run.** Parts I–III, ADR 0014 and
   ADR 0019 stand. What changes is the **scope sentence** attached to them: they
   measure the projection problem on a dissectible fixture.
2. **The pre-registered decision rule fired and was the wrong rule** — recorded,
   not reinterpreted. It said a paired McNemar loss at p < 0,01 reopens the 15 s
   budget. It fired at 104–0, and the loss is not in the solve. A rule written
   against one mechanism was fired by three others. Pre-registration is kept
   because it made that visible.
3. **The 15 s budget is not refuted, and it is closer to binding than it looked.**
   Zero real slots failed for time; no survivor waited more than 1,68 s to become
   valid. But wall p50 goes 0,19 → 3,30 → **10,11 s** across the ladder and p90
   reaches the cap on both real-sampled arms. Part II's headroom is a property of
   the published fixture.
4. **Per-dwelling sampling, at a fixed shape family, costs more than half the
   survivors** — `cap` loses 70 of 120 slots in `ground_truth` against `corpus`'s
   14. This is the finding with the widest reach here, because **every fixture on
   this map is a per-count median**, and a median is dissectible in a way its own
   population is not.
5. **The toy's programme model over-demands habitable rooms**, and it is now
   measured: `COMPOSITION` wants a median 5 where a real dwelling offers a median
   4 cells that are both exterior-facing and habitable-sized — short in 23,3 % of
   dwellings at `detached` and **50,0 %** at `corpus_median`. ⚠️ This is
   `scenarios.composition` and `scenarios.STANDARDS`, **not**
   `data/standards/room-constraints.json`, and it may not be quoted as the
   shipped table's cost.
6. **`EXPOSURE_PRESETS` is not retired, and the reason is measured rather than
   assumed.** A third of a real boundary lies off its own bounding box, which
   looked fatal for a four-vector over bbox edges; the notch branch of
   `_faces_of` recovers it, and `exterior_fraction` lands at 0,766 on a real
   outline against 0,786 on its cap approximation. The ticket's item 4 is
   answered *no*, on evidence.
7. **The six-room hole belongs to `envelope_for(6)`, not to six rooms.** ADR 0029
   left n = 6 as the one uncovered cell in C13's band. On the `cap` arm **4 of
   14** slots survive there against `corpus`'s **0 of 14**.
8. **A converted dwelling is not a witness for its own boundary**, and the
   failure reads as a coordinate bug. Recorded at `rectangularisation.md` §14.4:
   the recorded rectangles are fitted to the cap Envelope, a superset, so against
   the true outline they fail H1 and H3 together — seven of the first eight
   slots. `real_envelope.refit_to_true_mask` substitutes the domain at
   `fit_rects`' call boundary; **`fit_rects.py` is not edited**, because four
   closed decisions rest on it.
9. **The true-mask re-fit is materially harder than the cap fit**, first measured
   here: **11 of 71** in-band converted dwellings (15,5 %) could not be re-fitted
   to their own boundary at the same 10 s budget, where the cap fit decided every
   one. Runtime roughly doubles.
10. **`experiments/rectangularise/` and `experiments/solver-toy/` each gain two
    files and a committed series.** A ticket touching the real-boundary arm, the
    minimum-partition metric or the re-fit is amending a settled shape rather
    than filling a gap.

## What this does not decide

- **Whether ADR 0003's Envelope should be widened.** Not priced here.
  `rectangularisation.md` §13.3 refused it on separate evidence, and §14 measures
  the distance without costing the crossing.
- **Whether `ground_truth` should be replaced** by a dissector for general
  rectilinear regions. That is the single change that would make a real-boundary
  arm a clean measurement, and it is a build, not a decision this ticket owns.
- **Whether the toy's `composition` should be re-fitted to the corpus.** Named,
  measured, and handed on.
- **Anything about the shipped acceptance bar.** V.3's programme finding is about
  the harness. The bar's own corpus cost is ADR 0023's **84,41 %** and is a
  different measurement of a different object.
- **That no room-sized partition of a real outline exists.** Two heuristics
  failed to find one; neither is a proof.
