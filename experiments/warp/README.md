# The retrieval warp

Harness for *The retrieval index and warp procedure* (ticket 23). Findings live
in `docs/spec/proposer.md` §2.2; the decision is ADR 0018.

Reads two things and writes neither:

- `data/corpora/swiss-dwellings/` — the raw corpus, gitignored, acquired per
  `docs/research/dataset-inventory.md`.
- `experiments/rectangularise/out/swiss_fit_k2.json` — the converted corpus,
  produced by `fit_rects.py --k2`. **Copy it in, do not regenerate it here**;
  that directory belongs to other tickets and nothing in this one writes to it.
- `experiments/solver-toy/solver.py` — imported read-only for `rank_relations`
  and `select_relations`, so the relation check is the solver's own extractor
  and not a copy of it (`proposer.md` §5.1). Same pattern
  `experiments/envelope-exposure/` uses.

Outputs go to `out/`, gitignored. Seed 20260819 throughout, the same one
`experiments/retrieval-coverage/` used, so a Brief here is the same Brief there.

| script | what it does | runtime |
|---|---|---|
| `room_area_spread.py` | does an **affine** warp land a gate-admitted dwelling's rooms on the Brief's per-room targets? Builds the per-room area cache on first run | ~4 min, then seconds |
| `gate_curve.py` | prices the two obvious fixes — per-room area as a fourth **gate** term, and per-room area as a **ranking** term | ~2 min |
| `fit_warp.py [n]` | **the warp that ships**: one CP-SAT solve over the source tiling's cut lines. Also runs the arrangement metric on every warp | ~0.2 s/dwelling |
| `pool_fidelity.py [briefs]` | best-of-pool — what a *Brief* gets, once every pool member is fitted | ~1 s/brief at `--take=8` |
| `coverage_restated.py` | §2.2's coverage table joined to the conversion, per multiset | seconds |
| `absolute_area.py [n]` | does a Room that asks for 12 m² **get** 12 m²? The same warp against an **un-normalised** target and measured on the **Space**, not the part | ~15 min an arm at `n=600` |

Order: `room_area_spread.py` first (it builds `out/dwelling_rooms.json`, which
every other script reads).

```
python experiments/warp/room_area_spread.py
python experiments/warp/gate_curve.py
python experiments/warp/fit_warp.py 400 --time=3.0
python experiments/warp/pool_fidelity.py 150 --take=8
python experiments/warp/coverage_restated.py
python experiments/warp/absolute_area.py 600 --time=3.0
```

`absolute_area.py` flags: `--time=` the per-warp CP-SAT cap, `--arms=` any of
`self,cross,calib,market` (default all four) plus `pool`, and `--pool=` its size
(default 8). **`pool` is the arm that answers "what does a Homeowner get"** — it
is best-of-pool, C6's own semantics, and it costs `k` warps a Brief, so run it at
a smaller `n` (200 is ~40 min at `k=8`). It writes a summary to
`out/absolute_area.json` **and every row to `out/absolute_area_rows_<arm>.json`**,
so a new statistic off this study costs seconds rather than the 15 minutes an arm
takes to re-solve. The rule `experiments/acceptance-thresholds/` states applies
here too: **if you add a statistic, add its inputs to the row record.**

`fit_warp.py` flags: `--time=` the per-warp CP-SAT cap, `--no-aspect` drops
`dim.aspect_ratio_hard`, `--no-min` drops the ergonomic floor. The last two are
the ablation that says what the warp's refusals are actually made of.

## Four things that will bite whoever runs this next

**Warping into an ungated Envelope measures the absence of the gate.** The first
version of `fit_warp.py` drew a target Envelope from any dwelling of the same
room count and refused 23 % of warps. Applying the shipped three-term gate — the
thing that exists to stop exactly that — took it to 16 %. A retrieval experiment
that does not gate is measuring a system nobody proposed.

**Scale the programme onto the covered area, not the bbox.** A converted dwelling
leaves a median **13.1 %** of its bounding box as notch and void, and no choice
of cut lines hands that back. Targets summed to `W × H` demand 13 % more floor
than the arrangement holds, and it comes out as deviation and refusal that belong
to the harness.

**Do not alternate the two axes.** A Room's area is bilinear in the two gap
vectors and CP-SAT takes that directly through `AddMultiplicationEquality`.
Alternating — freeze `gy`, solve `gx` — makes the area term linear and looks
cheaper, but `dim.aspect_ratio_hard` couples the axes, so a frozen axis
manufactures infeasibility that the joint model does not have. The joint model is
also *decidable*: 329 OPTIMAL, 1 FEASIBLE, 63 INFEASIBLE, **0 UNKNOWN** at a 3 s
cap over 393 warps, which is the property ADR 0008 asks of the conversion and
gets here for free.

**Measure deviation in per-mille of the Room's own target, never in cells.** An
absolute objective spends every gap on the living room, because 5 % of 30 m² is a
bigger number than 40 % of a WC. Both the acceptance bar and the Homeowner read
the *worst* room, so the objective is minimax on the relative deviation with the
weighted sum as a tie-break.

## What was measured and rejected

- **Loosening the ±10 % / ±15 % gate.** The budget is not where fidelity lives:
  a monotone warp cannot destroy a separation direction at any budget, and the
  quantity that *is* damaged — per-room area — is not what the gate measures.
- **Per-room area as a fourth gate term.** Holding every room within ±30 % of its
  target takes coverage from 90.3 % to **40.9 %** at 4–6 rooms and 87.2 % to
  **30.2 %** at 7–10. Within ±10 % it is single digits. The gate cannot buy this.
- **Per-room area as a ranking term over an affine warp.** Free, and useless: the
  *best* member of the whole pool still misses its worst room by more than 30 %
  for **54.8 %** of Briefs at 4–6 rooms and **65.3 %** at 7–10. The pool does not
  contain a well-proportioned match, so no ordering finds one.

## Four more things that will bite, from `absolute_area.py`

**Every number in `fit_warp.py` is a proportion, and nothing here says so.** Lines
373–384 scale the Brief's targets onto the donor's covered area before comparing.
That was right for what `fit_warp` measures and it is the wrong quantity for
anything that reads an area in m². **Do not report a `fit_warp` deviation as
though a Room got its target.** `absolute_area.py` is the un-normalised twin.

**The plane matters and it is not the part.** ADR 0001: `Space = erode(⋃ parts,
t_int/2)`, and ADR 0010 makes that the finished face, which is the plane
`dim.min_area` and `dim.statutory_min_area` both bind. Erosion costs **8.6 %** of
the covered area at the shipped `t_int` of 150, systematically, so a rig that
measures the centreline part reports a dwelling 8.6 % richer than the one the
validator will see. Erode the **union**, not the parts: a two-part Room gets the
band across its join back, and eroding parts separately quietly under-measures it.

**The corpus tiling is not the interior.** `fit_rects.py`'s watershed gives every
wall cell to the nearest room within `WALL_REACH = 0.35 m`, so a converted
dwelling's parts cover the interior *plus* a band of up to 350 mm around the whole
perimeter. Σ part area runs **1.25 ×** Σ corpus room polygon area. Any arithmetic
that treats a converted tiling's covered area as `interior` is off by that band.

**Never compound a per-candidate share into a Brief-level one.** Declines are
correlated within a pool — every candidate for one Brief is sized from the same
`interior` — so independence is wildly wrong in the safe-looking direction.
Measured here: per-candidate 31,1 %, independence predicts 0,311⁸ ≈ 0,009 %,
**the pool arm measures 6,7 %**. A factor of 780. ADR 0018 consequence 3 says the
same thing about a different statistic; it is the same trap twice.

**CP-SAT under a wall-clock cap is not reproducible, so do not over-quote.** Two
runs of the `self` arm at the identical seed, n and inputs returned 102 and 99
conditional failures out of 1 712 — 5.96 % against 5.78 %. The seed fixes the
*sample*, not the *solution*: at `--time=3.0` the search is timing-dependent.
Quote these to one decimal and treat sub-half-point differences as noise.
