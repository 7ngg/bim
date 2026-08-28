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
| `pool_depth.py [n]` | how deep a pool the sample can draw, under three pool definitions. No warp, no solve | seconds |
| `best_of_m.py [n]` | **the best-of-m curve**: starvation against pool depth, nested and paired | ~7 min a pool at `n=200 --m=64` |
| `best_of_m_fit.py` | fits and extrapolates that curve to production depth, with a bootstrap | ~2 min |
| `constrained_warp.py [n]` | what ADR 0020's notch invariant and ADR 0028's void charge cost when **posted in the solve** rather than arrived at | ~6 min at `n=200` |

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

## What ticket 56 changed, and why every number above moved

**The rig was eroding a wall that is not there.** ADR 0001 tiles the **solve
domain** — the Envelope dilated outward by `t_int/2` — so a tiling edge on the
domain boundary erodes back onto the external wall's inner face and costs no
floor. `absolute_area.py` tiled the **Envelope box** (ADR 0020's
`box = interior/(1 - s)`) and eroded every Room on all four sides, charging each
dwelling a 75 mm ring around its whole perimeter: **3,7 % of `interior` at p50**,
which is larger than the level error ticket 54 attributed to `brief.md` §5 rung 1.

Dilating a 250 mm cell frame by 75 mm is below its own quantisation, so the
construction is honoured on the measurement plane instead. `space_m2` erodes the
Room's parts **union the region outside the Envelope**, so a boundary edge is
interior to that union and survives while a shared edge does not — exactly equal
to ADR 0001 for area, with no quantisation. `outside_of` draws that region and
deliberately **excludes enclosed voids**: a void is bounded by wall on every side,
so its edges cost erosion exactly as an interior edge does. `notch_share` already
draws the same line, which is why it separates boundary-touching complement
components from enclosed ones.

**`part_targets_cells` had the same defect one level up, and it was
compensating.** It charged every part `150 * (w + h) - 22500` on all four sides,
so a perimeter Room was asked for more centreline area than it needed and
delivered more Space than the level implied. Both sites now measure with the same
rule, which is why the fix moves the **level** a long way and the **yield**
hardly at all.

**The warp resizes the notch, and ADR 0020's guarantee assumes it does not.**
*"Every candidate delivers `interior` of floor by construction"* holds only if the
**realised** notch share equals the recorded `s` the box was derived from, and
`proposer.md` §2.2.3 says the opposite in as many words — the notch *"warps along
with everything else, for free"*. It is the one region of the frame carrying no
target, so it is a free sink: correcting the target overhead released cells and
the warp put them there, taking `cov_over_int` to 0.9833.

**`ring` / `ringmarket` / `ringpool` hold the share and are the arms to read.**
They enforce it by fixed point on the box rather than by pinning the cut lines,
because pinning means editing `warp_model`, which lives in `fit_warp.py` and
carries ADR 0018's published numbers. This is a **finding about the shipping
design**, not only about this rig: the constraint is owed by `proposer.md` §2.2.

`ring` is **not** `calib`. `calib` scales until Σ Space hits `target_area`, which
hands the rooms margin the engine does not give them; `ring` enforces a constraint
the engine actually has and leaves the erosion where it falls. Reading `calib` as
"what a correct Envelope delivers" over-states the gain — that mistake is what put
2/5 of a hard rule's cost on one constant in `brief.md`.

### Same sample, `n=600`, `--time=3.0`, seed 20260819

| arm | `cov/int` | `space/cov` | Σ Space ÷ `target_area` mean | p50 | conditional rooms under floor | plans losing one |
|---|---:|---:|---:|---:|---:|---:|
| `self` before | 1.0215 | 0.9143 | −2,30 % | −1,18 % | 5,8 % | 14,8 % |
| `self` after | 0.9908 | 0.9504 | −0,75 % | −0,27 % | 4,9 % | 13,1 % |
| `cross` before | 1.0071 | 0.9124 | −4,27 % | −2,91 % | 13,4 % | **30,7 %** |
| `cross` after | 0.9833 | 0.9490 | −2,19 % | −1,03 % | 12,7 % | 30,5 % |
| **`ring`** | **0.9986** | 0.9504 | **+0,36 %** | **+0,40 %** | **10,1 %** | **24,9 %** |
| `calib` before | — | — | −0,16 % | −0,17 % | 7,5 % | 18,8 % |
| `calib` after | — | — | −0,05 % | −0,02 % | 8,2 % | 22,0 % |
| `market` before | 1.0108 | 0.9141 | −3,11 % | −2,12 % | 10,8 % | 31,1 % |
| `market` after | 0.9882 | 0.9503 | −1,22 % | −0,60 % | 10,3 % | 29,9 % |

The pre-56 rows are **committed**, at
`series/absolute_area_pre56_rows.json.gz` (263 KB, five arms keyed by name), on
ticket 44's rule: the paired comparison above is re-derivable in seconds rather
than by a re-run, and every arm's `summarise()` can be recomputed off it. The
pre-fix script itself is one `git show HEAD~:experiments/warp/absolute_area.py`
away and is not kept here.

**Read the `ring` row and no other as what the engine delivers.** `interior =
target_area × (1 + f)` with `f = 0.0575` lands Σ Space at **+0,4 %** of the floor
the Brief asked for. There is no sizing correction owed anywhere, and the 4,2 %
calibration ticket 54 computed was measuring the two rig defects above.

## What ticket 57 added, and the two traps in it

**The curve costs almost nothing more than the point.** `served_at_m` is a
prefix-any over one fixed draw order, so the whole curve is fixed by the **index
of the first serving candidate** and `run_pool`'s early break stays valid. Going
from m = 8 to m = 64 spends extra warps only on the Briefs starving at 8. Every
point is paired against every other; no two differ by a re-draw.

| m | 1 | 2 | 4 | 8 | 12 | 16 | 32 | 64 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| every Brief with a pool | 35.2 % | 18.6 % | 10.1 % | 6.5 % | 6.0 % | 6.0 % | 5.5 % | 5.5 % |
| `run_pool`'s convention | 33.5 % | 16.5 % | 7.7 % | **4.1 %** | 3.6 % | 3.6 % | 3.1 % | **3.1 %** |
| 7–10 rooms | 37.4 % | 18.7 % | 9.3 % | 8.4 % | 8.4 % | 8.4 % | 8.4 % | 8.4 % |

An eightfold deepening buys **one point**, and at 7–10 rooms it buys nothing.
`ringpool`'s published **3,6 %** reappears at m = 12–16 against 4,1 % at m = 8 —
one Brief on a different draw permutation.

**Trap 1 — `gate_pool` is not the shipped gate, and `--pool=8` is not a tenth of
production depth.** `proposer.md` §2.2.1 makes the multiset bucket the first term
and the area and aspect terms *a scan of it*. `gate_pool`'s primary branch returns
the **whole bucket** and applies the other two only in its by-room-count fallback.
Measured over the same sample: shipped gate p50 **9** (4–6) and **5** (7–10),
max 51, 14.5 % empty; `gate_pool` p50 **81** and **37**, max 146. So §2.2.7's
*"a pool of 87 in production is a pool of 8 here"* is right about the gate and
wrong about the rig. Gate-admitted donors are also **better** — first-candidate
decline 29.8 % gated against 35.2 % bucket — so the two differences pull opposite
ways and neither can be waved off.

**Trap 2 — do not fit a plain Beta to the curve.** Independence is wrong by 780×,
so the fit has to be a mixture; but every `Beta(a,b)` sends `E[p^m]` to zero and
therefore predicts that enough depth serves every Brief. Fitted here it returns
**0,45 %** at m = 8 against a measured **8,2 %**. The curve has a floor and the
model must be able to express it: a point mass at `p = 1`,
`starvation(m) = π + (1−π)·B(a+m,b)/B(a,b)`. `π` is **2,8 %** [0,3–5,6] overall
and **5,3 %** [0,0–11,2] at 7–10 rooms. `π` is identified by the **depth** of the
censored observations, so the shallow gated pool cannot see it at all — its own
fit returns π = 0 with a zero-width interval, which is an artefact and not a
result.

**`absolute_area.py` now reports the realised hole.** `bbox` decomposes exactly as
`Σ Space + erosion + notch + enclosed void` and only the first two were on the
record, which is why ADR 0028's measurements had to be made from `experiments/void/`.
Every row now carries `void_m2`, `notch_m2`, `erosion_m2`, `s_realised`,
`void_realised` and `bbox_m2`, and `summarise()` an `unassigned` block with the
donor-to-realised amplification.

⚠️ **Read realised shares off the FRAME, never off the millimetre geometry.**
`notch_share` flood-fills one boolean cell per square millimetre; on donor parts
that is small, on solved geometry it is ~80 million cells per plan and the run
never finishes. `frame_components` + `realised_frame_areas` do it exactly and in
O(cells) — the complement's components are fixed by `spans`, because the warp
moves gap sizes and never index spans.

**The two owed constraints cost 2,6 % of candidates, and it is all the notch.**
`constrained_warp.py`, 194 paired cases: ADR 0028's void charge costs **zero**,
ADR 0020's notch invariant costs 5 candidates, and `both` costs the same 5. The
cost is a function of how hard the invariant is held — ±0.04 loses 1,5 %, ±0.02
loses 2,6 %, holding it **exactly** loses **8,8 %** and takes worst-room deviation
0.139 → 0.226.

⚠️ **`s` does not cover all of the notch.** `notch_share` sums the **two largest**
boundary-touching components and **27,5 %** of donors have three or more. The
cheap encoding — `W*H − Σ part areas − void`, linear and free — therefore holds a
strictly larger region than ADR 0020 names. Constrain the cells `s` is read off
instead: it costs one product per notch cell (p50 6) and it is the difference
between drift that tracks the tolerance and drift that stalls at 0.04.
