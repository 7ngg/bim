# solver-toy — does C10 actually work?

A runnable test of standing constraint **C10** (*model proposes, solver
projects*): given a fixed non-rectangular **Envelope** and a **Proposal** from a
learned model, find the feasible **Plan** nearest the Proposal.

Findings, measured timings and the recommended formulation live in
[`docs/research/solver-formulation.md`](../../docs/research/solver-formulation.md).
This README only tells you how to run it.

## Install and run

```
pip install ortools            # Apache 2.0; developed against 9.15.6755
cd experiments/solver-toy

python smoke.py                # scenarios, ground-truth validity, Proposal corruption
python probe1.py               # boxes only, hard coverage, 20 s
python probe2.py               # does the model admit the known-good ground truth?
python probe3.py               # 12-room ablation, 60 s
python probe4.py               # the recommended configuration, all three sizes
python probe5.py               # hostile Proposals and an impossible Brief
python probe6.py               # ticket 24: does confident-wrong predict failure?
python report6.py              # its tables
python severity6.py            # which definition of confident-wrong predicts
python mechanism6.py           # *why* a wrong relation kills a solve
```

No other dependencies. `probe3` and `probe4` take a few minutes each; the rest
are quick. Seed is `20260817` everywhere.

**Timings are machine-specific.** The published numbers were taken on a 4-core
Ivy Bridge desktop with `num_workers = 4`. CP-SAT's portfolio search is
stochastic across workers, so wall-clock times will move on a re-run and move a
lot on different core counts. The *statuses* (found / not found / infeasible) are
the stable part.

## Files

| File | What it is |
|---|---|
| `geometry.py` | `Rect`, `Envelope`, and pure-geometry predicates. Integer grid units only, no floating point on the solver path. |
| `scenarios.py` | Seeded Briefs, Envelopes and Proposals for 8, 12 and 24 rooms. Two Envelope **fixtures** — see below. |
| `envelope_fit.py` | Fits the corpus Envelope family, per room count, against 2,238 real dwellings. Seconds; reads the committed series. |
| `fixture_delta.py` | What moving between the two fixtures costs the solver: paired `(n, exposure, seed)`, shipped config. `results/FIXTURE.jsonl`. ~15 min at 5 seeds. |
| `solver.py` | The CP-SAT projection model. `LayoutProjector` / `SolveConfig` / `project()`. |
| `validate.py` | Independent checker. **Shares no code with the solver** beyond raw geometry — deliberately, so the two can disagree. |
| `smoke.py`, `probe1..5.py` | The runs behind the findings doc. |
| `arrangement.py` | `docs/spec/proposer.md` §5's metric, and the machinery to inject a known dose of confident-wrong into a Proposal the solver accepts. Ticket 24. |
| `probe6.py` / `report6.py` | Ten suites and their tables. `results/P6.jsonl`, `results/report_P6.txt`. |
| `severity6.py` | Which reading of "confident-wrong" actually predicts survival. |
| `mechanism6.py` | The chain bound — a necessary condition on a relation set, checkable with no solver and no ground truth. |

## How a scenario is built, and why it matters

Every Brief is derived from a **known-feasible ground-truth tiling**:

1. Pick a room mix (`composition`) and per-room target areas.
2. Dissect the Envelope into exactly that many rectangles by a backtracking,
   area-targeted guillotine (`ground_truth`). This is a valid exact tiling.
3. Assign room types with a **separate small CP-SAT model** (`assign_kinds`) over
   that fixed geometry, itself required to satisfy the type-dependent rules —
   habitable rooms on exterior walls, wet rooms in one cluster, circulation that
   never passes through a bedroom.
4. Derive the Brief's required and forbidden adjacencies from the truth.
5. Re-check the truth with `validate.check`. It passes at all three sizes.

This guarantees each Brief is satisfiable, with the ground truth as witness. It
is the reason a failure to solve can be read as a fact about the projection
problem rather than about an accidentally impossible Brief — without it the
timing table would mean nothing. `probe2.py` re-confirms it by pinning every room
to its ground-truth rectangle and re-solving.

The **Proposal** is that ground truth with independent Gaussian noise on each of
the four corners of each box. Per-corner rather than per-box, because that is
what produces overlap *and* unassigned floor at the same time — the pathology a
learned generator actually emits. Measured corruption: 2–8 % overlap, 21–27 % of
the interior unassigned, some boxes outside the Envelope.

## The model in one paragraph

Integer `x1, x2, y1, y2` per room in grid units of 250 mm, so orthogonality and
grid snapping are properties of the variable domains rather than constraints.
`AddNoOverlap2D` over the rooms **and** the Envelope's notches handles both
non-overlap and the non-rectangular boundary. Exact tiling is
`sum(w·h) == interior_area`, posted **soft** with a dominating weight. Adjacency
is a reified contact literal per pair; required adjacency forces it to 1,
forbidden forces it to 0. Circulation and wet-room clustering are both
**single-commodity flow** over that variable contact graph — for circulation,
bedrooms and bathrooms are forbidden to forward flow, which is exactly "you do
not walk through a bedroom to reach the kitchen". The objective is L1
displacement of all four corners from the Proposal.

**The Proposal appears only in the objective and the hint — never in a
constraint.** That is what makes graceful degradation structural rather than a
recovery heuristic.

⚠️ **True only with `fix_relations=False`.** With it on — the recommended
configuration — the extracted relations *are* constraints, and the ticket-15
sweep measured a merely noisy Proposal going INFEASIBLE (5 of 5 seeds at 24
rooms at σ = 1.0 m). See `docs/research/solver-formulation.md` Part II.0.

Ticket 24 sized the hole: **one** relation the truth contradicts is enough to
make the model INFEASIBLE 56 % of the time, and two takes the survivor rate to
zero — while dropping *every* relation still yields a Plan. The Proposal's route
into the constraint set is narrow and it is sharp.
See `docs/research/arrangement-metric.md`.

## Knobs worth turning

`SolveConfig` in `solver.py`:

| Field | Effect |
|---|---|
| `fix_relations` | Extract the Proposal's relative arrangement and post it as hard linear separations. **The single biggest speedup**; also the only thing that can make the model infeasible. |
| `soft=("coverage", ...)` | Which constraint families degrade with a penalty instead of failing. `"coverage"` alone is the recommended default. |
| `objective` | `"corners"` (recommended), `"centroid"`, or `"corners+order"`. |
| `time_limit_s` | Treat as a product parameter. Runs terminate at `FEASIBLE`, not `OPTIMAL` — take the best Plan found. |
| `relation_confidence` | Fix only relations where the Proposal's best separation direction beats its second-best by this margin. This is τ; ticket 15 fitted it to 4 and ticket 24 found what it filters — confident-wrong severity. |
| `arc_radius` | Prune candidate adjacency pairs by Proposal distance. Implemented, never benchmarked. |

## Two Envelope fixtures, and why the default is the old one

`envelope_for(n, exposure, fixture=...)` serves two families. **`published`** is
the default and is every number in `docs/research/solver-formulation.md` Parts
I-III, in ADR 0014 and in ADR 0019. **`corpus`** is fitted per room count against
2,238 real Swiss dwellings on area, perimeter *and* bounding-box occupancy, to
within 0,7 % at every count from 5 to 11.

The published family is **15 % smaller per room** than the corpus median and sits
at exactly **0 %** boundary excess over its own bounding box, where a real
dwelling runs 6-12 % over and rises with room count. The cause is not the notch
share and not the notch count:

> **Every notch `l_shape` and `u_shape` cut is a corner notch, and a corner notch
> removes floor while adding no perimeter at all.** `u_shape` builds ADR 0003's
> **T**, not its U. `geometry.u_shape_true` cuts the missing member -- a mid-edge
> notch, which adds exactly `2 x depth` at zero area cost.

The default does **not** move. A closed decision does not change because a later
ticket fitted a better fixture beside it; the move is priced once by
`fixture_delta.py` instead. ADR 0029.

⚠️ **`clear_t` must equal the solver's `t_int_mm` whenever `erode_minima` is on.**
The solver binds minima on the *clear* rect; a truth built at `clear_t = 0`
satisfies them on the *solved* rect and stops being a witness, and the model can
then be **provably** unable to tile its own Envelope. The first run of
`fixture_delta.py` returned OPTIMAL with 55 interior cells unassigned at every
seed and both exposures and it was this one argument. It reads exactly like a
fixture defect. `sweep_ng.execute` passes `t_int` through; do the same.

## Known gaps

- ~~**Rooms tile exactly; real walls have thickness.**~~ **Closed.** ADR 0001's
  dilated solve domain keeps the formulation intact and the eroded-millimetre
  area rule costs nothing measurable (Part II.1) — but the *minima* must be
  grid-aligned or 4-, 5- and 6-room dwellings become infeasible. See ADR 0007.
- ~~Every timing is a **single run at one seed**. No variance estimate.~~
  **Closed** by ticket 15: `sweep.py` / `report.py`, ~1 000 solves, Part II.
- Grid resolution was never swept — everything ran at 250 mm. *Still true.*
- ~~**The Envelope was never checked against a real dwelling.**~~ **Closed** by
  *The toy Envelope is more compact than a real dwelling*: `envelope_fit.py`,
  `fixture_delta.py`, ADR 0029. Its residue is that **no Envelope here is a real
  boundary** — both families are parametric, where every published generator
  (HouseGAN++, HouseDiffusion, Graph2Plan, WallPlan) conditions on a boundary
  drawn from its dataset. That arm needs `experiments/rectangularise/` and has
  its own ticket.
- The corpus fixture covers **5-11 rooms**. `n` = 4 is *refused*, not missing: a
  40,4 m² dwelling cannot carry an articulated boundary and a 2,75 m `living`
  column at once, and `ground_truth` gives every Envelope part a room.
- ~~The Proposal's relation channel is untested.~~ **Closed** by ticket 24:
  `probe6.py`, `docs/research/arrangement-metric.md`. Its residue is that the
  corruption model is Gaussian corner noise, which produces almost no *same-axis
  reversals* — the one kind of error that is fatal every time. A learned
  generator will.
- Minimum dimensions and areas are not in the softenable set, so a Brief that is
  impossible because the rooms cannot fit fails hard with no explanation.
