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
| `scenarios.py` | Seeded Briefs, Envelopes and Proposals for 8, 12 and 24 rooms. |
| `solver.py` | The CP-SAT projection model. `LayoutProjector` / `SolveConfig` / `project()`. |
| `validate.py` | Independent checker. **Shares no code with the solver** beyond raw geometry — deliberately, so the two can disagree. |
| `smoke.py`, `probe1..5.py` | The runs behind the findings doc. |

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

## Knobs worth turning

`SolveConfig` in `solver.py`:

| Field | Effect |
|---|---|
| `fix_relations` | Extract the Proposal's relative arrangement and post it as hard linear separations. **The single biggest speedup**; also the only thing that can make the model infeasible. |
| `soft=("coverage", ...)` | Which constraint families degrade with a penalty instead of failing. `"coverage"` alone is the recommended default. |
| `objective` | `"corners"` (recommended), `"centroid"`, or `"corners+order"`. |
| `time_limit_s` | Treat as a product parameter. Runs terminate at `FEASIBLE`, not `OPTIMAL` — take the best Plan found. |
| `relation_confidence` | Fix only relations where the Proposal's best separation direction beats its second-best by this margin. |
| `arc_radius` | Prune candidate adjacency pairs by Proposal distance. Implemented, never benchmarked. |

## Known gaps

- ~~**Rooms tile exactly; real walls have thickness.**~~ **Closed.** ADR 0001's
  dilated solve domain keeps the formulation intact and the eroded-millimetre
  area rule costs nothing measurable (Part II.1) — but the *minima* must be
  grid-aligned or 4-, 5- and 6-room dwellings become infeasible. See ADR 0007.
- ~~Every timing is a **single run at one seed**. No variance estimate.~~
  **Closed** by ticket 15: `sweep.py` / `report.py`, ~1 000 solves, Part II.
- Grid resolution was never swept — everything ran at 250 mm. *Still true.*
- Minimum dimensions and areas are not in the softenable set, so a Brief that is
  impossible because the rooms cannot fit fails hard with no explanation.
