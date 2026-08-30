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
| `gate_sites.py [n]` | which branch of the **pre-60** `gate_pool` fired and what it admitted — the two divergences that are not about depth. No warp, no solve | seconds |
| `gate_effect.py [n]` | **does the gate buy fidelity?** Splits one Brief's own bucket into gate-admitted and gate-refused and warps K from each, so the comparison is paired within a Brief rather than between two Brief populations | ~7 s a paired Brief at `--k=3` |
| `best_of_m.py [n]` | **the best-of-m curve**: starvation against pool depth, nested and paired | ~7 min a pool at `n=200 --m=64` |
| `best_of_m_fit.py` | fits and extrapolates that curve to production depth, with a bootstrap | ~2 min |
| `constrained_warp.py [n]` | what ADR 0020's notch invariant and ADR 0028's void charge cost when **posted in the solve** rather than arrived at | ~6 min at `n=200` |
| `stretch_terms.py` | **what the two dimensional gate terms are a proxy for**, computed directly and joined to `gate_effect.py`'s warps. No new warps | seconds |
| `floor_warp.py [n]` | **what `dim.statutory_min_area` costs when the WARP posts it**, not the solve. Four paired arms; `--pool=m` runs the Brief-level arm instead, `--lenient` swaps the `PRIVATE` limb to `bedroom_single`, `--raw` drops the `market_default` raise | ~8 min at `n=400`, ~25 min at `--pool=8 n=200` |

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

⚠️ **And this trap was written down, and then the rig walked back into it twice.**
Ticket 60. `absolute_area.gate_pool` returned the whole multiset **bucket** the
moment it was non-empty and scanned by area and aspect only in its by-room-count
fallback — so **82.4 %** of what it handed the warp is floor the gate refuses, and
its blank rate is **0.5 %** against the gate's ~13.4 %. Worse, that fallback drops
the multiset term itself, serving retrieval on **3.0 %** of Briefs (**4.0 %** at
7–10 rooms) where §2.2.1 says *hand the Brief to source B*. `fit_warp.py`'s own
pairing kept a same-multiset Envelope without checking area or aspect at all, and
kept an **off-multiset** one whenever area and aspect happened to pass: **22.5 %**
of its retained pairs were ones the gate refuses. Both are repaired. `gate_pool`
is now **two named functions** — `admissible_pool` (the gate, the default
everywhere) and `bucket_pool` (what the rig used to do, kept only as the depth
proxy `best_of_m.py` needs) — and `fit_warp.py` takes `--pairing=gate|pre60` so
the published percentiles can be reproduced before they are re-based.

⚠️ **The bucket is a depth stand-in and never a membership one, and the price is
measured.** `gate_effect.py`, paired within one Brief over 987 candidates an arm:
a gate-**refused** donor is declined **36.2 %** of the time against an admitted
donor's **27.6 %** and carries a worst-room deviation 68 % larger at p50, sign
test **p = 0.0001**, with a monotone dose on both terms. At **Brief** level the
same comparison is a wash (p = 0.74) because declines are correlated within a
pool. So: a per-candidate statistic must come off `admissible_pool`, and a curve
that needs production depth may come off `bucket_pool` **provided it says so** —
its members are worse, so such a curve under-states what real depth buys.

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

## What ticket 59 added: the warp reaches the projection solve

`project_join.py` is the first thing on this map to put a **warped Proposal
through `project()`**. Until it, `fit_warp.py` imported `experiments/solver-toy/`
for `rank_relations` / `select_relations` and nothing else, and every starvation
figure this directory publishes — 54's 30,7 %, 56's 25,5 %, 57's best-of-*m*
curve, 60's 4,4 % — was measured on the warped rectangles, before any projection.

| script | what it does | runtime |
|---|---|---|
| `project_join.py [n]` | one warped candidate → one solver-toy `Brief` + `Proposal` → `project()` at the shipped config. `--parts=1` uses `solver-toy/solver.py`, `--parts=2` uses `room-rectangles/solver_parts.py`'s Design A. `--report` re-summarises a finished run from its rows; `--planes` adds the two-plane diagnostic; `--selftest` asserts `warp_geom == absolute_area.run_one` | ~2 candidates/min |

It imports `solver-toy/` and `room-rectangles/` **read-only** and writes to
neither — the arrangement `envelope-exposure/`, `h8-frontage/` and `fit_warp.py`
itself already use.

**Five things that will bite whoever runs this next.**

⚠️ **`prop_starved × plan_starved` is not the confusion matrix, and building it
that way silently returns zeros.** `dim.statutory_min_area` is `site: both`, so
the projection **posts** the floor: a Plan that comes back has already met it and
Plan-level starvation cannot appear as an under-floor Room. It appears as
INFEASIBLE. `summarise()` asserts this the only way that means anything — it
reports `served_but_starved`, which is **0** on every run so far. If that number
is ever non-zero the floor is not reaching the model and nothing else in the file
is worth reading.

⚠️ **A refusal must be attributed, never assumed.** `infeasibility_core` only
covers the SOFTABLE families, so it cannot say the floor refused a candidate.
`one()` re-solves each INFEASIBLE with the statutory limb dropped and the
ergonomic floor kept — `fit_warp.py --no-min`'s shape one level up. 14 of 14
came back feasible; if that ratio ever falls, the arm is measuring H1/H2/H5/H7 or
the fixed relations and the false-pass rate is not the floor's.

⚠️ **The two rigs measure area on different planes and the gap is 3,9 % per
Room.** `absolute_area.space_m2` is ADR 0001's — a Room's Envelope-boundary edge
costs no floor, because the tiling edge there already sits at
exterior-inner-face + `t_int/2`. `solver.py`'s `amm = (250w − t)(250h − t)`
erodes all four sides of every Room, and it cannot do otherwise: ADR 0001 tiles
the box **dilated** by `t_int/2` and 75 mm is below the 250 mm grid's own
quantisation (`brief.md` §5.3 — the solve domain is a THIRD quantity). Ticket 56
removed exactly this defect from *this* directory and measured it at 3,7 % of
`interior` at p50; `--planes` re-finds it at p50 **0,0392** per Room inside
`solver.py`, where it cannot be removed. Read every false pass against it.

⚠️ **The toy's H8 / H9 / H10 are posted SOFT here, on purpose, and a run that
leaves them hard measures the toy.** H9 demands one plumbing cluster where
`wet.plumbing_group_count` has been 3 since ADR 0023; H10 routes around a
`PRIVATE` set that includes the wet types where `circ.no_private_transit` is
about sleeping rooms; H8 binds off an exposure preset a warped candidate does not
carry. What they would have cost is on the record anyway and for free, in
`witness_fails` — whether the warped candidate itself satisfies each is computed
with no solve at all. This is 58's finding from the other side: the toy's
placeholders may not be quoted as `room-constraints.json`'s cost.

⚠️ **`--parts=1` is 46,4 % of the converted index and it is not a random half.**
`solver-toy/solver.py` gives a Room one rectangle; ADR 0014 gives it one or two.
The k = 1 restriction skews small — 59,3 % of donors at n = 6 against 31,4 % at
n = 9 — and it lowers the Proposal-level starvation base rate from `ringmarket`'s
**25,5 %** to **18,3 %**, so the two are not interchangeable. `--parts=2` covers
the rest through `solver_parts.py`, which binds the Room's `min_area` on the
**primary part** where ADR 0014 binds it per Room: strictly stricter, so a false
refusal it finds is real and a false refusal it misses may be hidden.

**The join's rows are committed**, `series/project_join_rows_k1.json.gz` (291
candidates) and `series/project_join_rows_k2.json.gz` (34, the k ≤ 2 arm), on 44's
standing rule: `out/` is gitignored, a re-run is hours, and every number in
`proposer.md` §2.2.9 is derivable from these. `--report --suffix=…` re-summarises
them in seconds and `--planes` re-derives the two-plane diagnostic; copy a series
file into `out/` first, since that is where `--report` reads.


## What ticket 63 added, and the three traps in it

`stretch_terms.py` computes the **frame requirement** — the smallest box extent a
donor's cut-line frame admits at the ergonomic floor — off the index record alone,
by an interval DP over the part spans. It reads `out/gate_effect_briefs.json` and
joins to the 1 974 candidates already warped there, so it costs seconds and no
solve. ADR 0032.

The bound is **sound**: `warp_model` posts `sum(gx) = W`, `gx_i >= 1` and per part
`sum(gx[a:b]) >= MIN_SIDE`, so for any set of parts with pairwise-disjoint x-spans
`sum MIN_SIDE <= W`. Maximising over disjoint sets is a lower bound on `W`, and
`req > 1` therefore implies INFEASIBLE. Measured: **103 of 103**, no exceptions.
It is not *sufficient* — it does not model the 2-D coupling `wv <= 3*hv` or the
area objective — so 98 candidates with `req <= 1` were still refused.

⚠️ **`gate_effect`'s population is 50/50 and a production bucket is 82,4 %
gate-refused.** Every §4b and §4c figure is on the 50/50 draw, and the bias runs
*toward* loosening the gate — precisely the direction this ticket was tempted in.
§4e repairs it with no new warps: each Brief record carries its own `n_admitted`
and `n_refused`, so weighting each row by its stratum size gives the urn the
bucket's real composition. **Quote §4e, not §4b.** Under the repair, replacing the
scalar pair stops winning: best-of-pool p90 goes **0,2303 → 0,2543**, the wrong way.

⚠️ **§4e's `m = 8` block is CONFOUNDED and is printed with that warning on it.**
The urn draws with replacement from at most six warped rows, three a stratum, so
each arm saturates at its own distinct count — the incumbent's three against a
loose rule's six. At `m = 8` that is a best-of-3 against a best-of-6 and it
flatters the loose rule by exactly the quantity under test. **`m = 3` is the
largest depth both arms fill with distinct warps and is the only quotable row.**
A real `m = 8` needs `gate_effect.py --k=8` — 16 warps a Brief, ~2 h.

⚠️ **`ext` is in the script as a control and is not a candidate.** ADR 0020's box
is `interior/(1-s)` at the *Brief's* aspect and the donor's bbox is
`area_d/(1-s_d)` at its own, so `(1-s)` cancels and the per-axis extent ratio is
`sqrt(area ratio x aspect ratio)` and `sqrt(area ratio / aspect ratio)` — a
bijection with the incumbent pair up to the donor's *void* share. It agrees with
the incumbent conjunction on **89,4 %** of candidates. It is the incumbent in
polar coordinates, and a frontier point quoted off it is the incumbent's own
point relabelled.

**`dim.max_area` is checked without a re-warp.** The rule is
`got <= k[type] x target` with `k` in 2,02–8,15 (`rules.json` `area_bands`), so a
breach needs a room at `got/target - 1 > 1,02`, and `worst_room_dev` is the max of
that over rooms — `dev > 1,02` is a *necessary* condition and the count is an
exact upper bound. 1,96 % under the incumbent, 2,08 % under `req <= 1` alone.

## What ticket 64 added, and the four traps in it

`floor_warp.py` prices posting `dim.statutory_min_area` **inside the warp's own
CP-SAT model**. ADR 0033. Four arms on one draw of 381 paired (Brief, donor)
cases, plus a Brief-level arm at `--pool=8`.

**The constraint is one line and it is linear.** `sum(part areas) >= floor`, per
Room. The part areas are already `AddMultiplicationEquality` products and the
floor is a constant, so unlike ADR 0020's notch invariant — one product per notch
cell — this adds **no product at all**. `constrained_warp.warp_model_constrained`
gains one optional `area_floor_cells` parameter defaulting to `None`; with it
unset the four published arms build a bit-identical model, and no call site in
that file passes it.

| | `both`, as `proposer.md` §2.2.2 specifies it | floor posted |
|---|---:|---:|
| served candidates | 335 | 302 |
| **carrying a Room below a statutory floor** | **106 = 31,6 %** | **14 = 4,6 %** |
| shortfall depth p50 · max | **1,356 m² · 8,444 m²** | 0,038 m² · 0,438 m² |
| INFEASIBLE | 46 = 12,1 % | 79 = 20,7 % |
| net paired candidate cost | — | **33 = 8,66 %** |

⚠️ **TRAP 1 — the baseline is `both`, not `free`.** `proposer.md` §2.2.2 point 6
already puts the void in the programme and ADR 0020's notch invariant is decided,
so the *spec's* warp is `constrained_warp.py`'s `both` arm. Pricing the floor
against `free` reports it cheaper than production will ever see it. `free` and
`floor` are kept only as the historical pair.

⚠️ **TRAP 2 — `worst_dev` read across arms is survivorship, not fidelity.**
Unpaired, the arms appear to show fidelity *improving* under the floor
(0,1710 → 0,1352). That is the floor refusing high-deviation candidates. Paired
on the 302 candidates both arms serve, the honest figure is p50
**0,1318 → 0,1352** — delta p50 **+0,0000**, 231 of 302 unchanged, 59 worse, 12
better — and p90 0,5359 → 0,6065. Quote the paired one. `worst_dev_unbound` is
reported for the same reason and is inert here: see trap 3.

⚠️ **TRAP 3 — the floor never fights a target in this rig, and that is a
property of the regime, not of the constraint.** `moved_rooms = 0` on every arm,
because `absolute_area` raises every target onto `dim.market_default_area`
(kitchen 9,0 against a floor of 8,0; `PRIVATE` 12,0 against 10,0; living 16,0
against 15/16) — which is `acceptance-bar.md` §11.1 ground 2's own stated
condition. The constraint binds against what the warp *achieves*, never against
what the Brief *asks*. `--raw` drops the raise and is the arm to run for the case
`brief.md` §9.4 still permits, a stated target below its own statutory floor.

⚠️ **TRAP 4 — a per-candidate rate is not this number, and §11.1 says so in its
own text.** The candidate cost is 8,66 %; the pool absorbs it. At `--pool=8` over
199 Briefs:

| | `both` | floor posted |
|---|---:|---:|
| Briefs served at all | 96,48 % | 94,97 % |
| **Briefs served *cleanly*** | **90,95 %** | **94,97 %** |
| clean share of those served | 94,27 % | **100 %** |
| pool depth p50 | 7 | 6 |

The floor costs **1,51** points of service and buys **4,02** points of *legal*
service. Run at m = 8; the production median pool is 86,6 at 4–6 rooms and 58,7
at 7–10, so this is an **upper bound** on the loss.

**A two-pass warp was measured and refused.** Re-warping without the floor on
INFEASIBLE recovers every lost candidate and takes violations to 14,0 % with
nothing lost, which reads as strictly dominant. Every second-pass candidate
violates *by construction* — it is exactly the one the floor refused — so it buys
a rate and **no invariant**. The end states are in the ticket.

**The posted floor is a seed-shape estimate**, which is where the 4,6 % residual
comes from: `part_targets_cells` reads each Room's erosion overhead off
`seed_rects` and the shape moves under the warp. Residuals are grid dust (p50
0,038 m²) and vanish at Brief level, but the invariant is *nearly* true rather
than true until ticket 67 lands.

**`_check_floor_transcription` runs on import** and asserts all six values of
`absolute_area.STAT_FLOOR` against `room-constraints.json`. The table is a hand
copy; it was tolerable while it only measured and is not now that it constrains
geometry. That is a guard, not the fix — ticket 69 owns the read-from-JSON
refactor.

## What ticket 65 added, and the four traps in it

`gate_depth.py` measures the gate at the depth the gate can actually **fill**.
ADR 0032 is decided at `m = 3`; the shipped `m` is 8. Ticket 65 was raised to run
the probe ADR 0032 consequence 5 names — `gate_effect.py --k=8` — and the first
finding is that **that probe cannot answer the question it was named for.**

⚠️ **`gate_effect.py --k=8` keeps a Brief if and only if its incumbent pool holds
8.** `strata` drops a Brief unless BOTH strata hold `K`, so at `K = 8` it keeps
**229 of 500** Briefs and the split is exact: every Brief with `n_admitted ≥ 8` is
kept, every Brief below it is dropped. Median admitted pool among the kept is
**17**; among the dropped, **2**. The ticket's own mechanism is that at `m = 8`
the incumbent gate binds *below the depth the engine asks for*, so conditioning on
`n_admitted ≥ 8` removes **every Brief where the effect can occur**. Measured
below: on exactly that retained population ADR 0032 is confirmed. The ~2 h run
would have returned "confirmed" and been wrong at population level.

**The pools are not the same size, and that is the whole finding.** Over 288
Briefs, pool p50 and the share of Briefs holding 8:

| rule | pool p50 | ≥ 8 on | empty pool |
|---|---:|---:|---:|
| incumbent ±10 %/±15 % | 8 | 51.7 % | 9.7 % |
| `req ≤ 1` alone | **52** | **85.4 %** | **0.0 %** |
| both (ADR 0032's join) | 8 | **50.0 %** | **12.5 %** |
| `logd ≤ 0.30` + `req ≤ 1` | 24 | 71.2 % | 4.2 % |

A conjunction can only remove members, so **the joined gate leaves the Homeowner
with no candidate at all more often than either term alone** — 12.5 % against
9.7 % and 0.0 %.

**3 834 warps, 288 Briefs, seed 20260819, `--time=3.0`, shipped configuration.**
Each rule draws its own pool over the whole bucket, truncated at `m`, **without
replacement**; only the union of the four draws is warped. No reweighting is
needed and none is done: 4e reweights a 50/50 draw to recover the bucket's
composition, and this design never makes a 50/50 draw.

**`m = 3`, equal-K subset — ADR 0032 reproduced on the post-ADR-0037 rig.**

| rule | Briefs served | p50 | p90 |
|---|---:|---:|---:|
| incumbent | 95.1 % | 0.0464 | **0.1515** |
| **both (join)** | **97.1 %** | 0.0465 | 0.1526 |
| `req ≤ 1` alone | 94.6 % | 0.0500 | **0.1998** ← worst |
| `logd` + `req` | 96.6 % | 0.0493 | 0.1846 |

⚠️ **"Reproduced" here means the ORDERING, and it cannot mean more than that.**
ADR 0032's sample is not recoverable — its per-Brief draw was salted by `hash()`
(below), so no rerun can reconstruct the rows it was computed on. What is
reproduced is the *ranking* of the four rules on both axes: the join is best on
served Briefs, and dropping the scalar pair moves the **p90 the wrong way**. The
absolute values differ substantially and are not comparable — 95.1 % against the
ADR's 88.1 % served, p90 0.1515 against 0.2303 — because the draw is
without-replacement, the sample differs, and `MARKET` has since been re-read.
Aggregates converged on the same ordering; nothing here matches row for row.

⚠️ **This is NOT the `market`-arm re-run MAP.md owes, and that debt is still
open.** These figures are *computed on* the post-ADR-0037 rig, which makes them
current, but MAP.md's debt is a re-run measuring **what moved** — and no arm here
was run under the pre-0037 literals, so no delta was measured. ADR 0037 deleted
those literals from the rig, so recovering the before-side is a real piece of
work and not a by-product of this ticket. **The debt passes to 62 and 67
unchanged.**

**`m = 8`, realised depth — the ordering inverts.** The incumbent falls to
**83.0 %** of Briefs served and `req ≤ 1` alone rises to **97.9 %**, with disjoint
CIs and a better p90; ADR 0032's join sits with the incumbent at 83.0 %. Full
five-arm table below, once the fifth arm is introduced.

⚠️ **Two denominators, and the conclusion survives both.** Above counts an empty
pool as not served. `pool_depth.py` calls an empty pool *"a Brief retrieval cannot
serve at all, which falls to source B and is **not** a starvation"* — so excluding
those Briefs instead gives incumbent **91.9 %** [88.8–95.4], `req ≤ 1` **97.9 %**
[96.2–99.3], join **94.8 %** [92.5–97.6]. The gap narrows from 14.9 points to 6.0
and **the served CIs stay disjoint either way**. Quote whichever, state which.

**The falsifiable prediction is confirmed, and it is the whole mechanism.**

| | incumbent | `req ≤ 1` | join | **depth-conditional** |
|---|---:|---:|---:|---:|
| **thin** (incumbent pool < 8), n = 139 | 64.7 % / p90 0.2124 | 95.7 % / 0.1820 | 64.7 % / 0.2124 | **95.0 % / 0.1554** |
| **deep** (incumbent pool ≥ 8), n = 149 | 100.0 % / 0.0673 | 100.0 % / 0.0758 | 100.0 % / **0.0657** | 100.0 % / 0.0673 |

In the deep half every rule serves every Brief and the incumbent and the join hold
the **best** p90 — ADR 0032, exactly. In the thin half the incumbent and the join
are **identical and both cost 31.0 points of served Briefs**, with disjoint CIs
([56.8–72.7] against [92.1–98.6]) and a worse p90 as well. The two scalars are not
buying proportion there; they are buying an empty pool.

**And the fifth arm is the answer: apply the incumbent, count what it admits, and
top up from `req ≤ 1` only when it holds fewer than `m`.** It costs no new warps
— every member it can draw is already inside `req ≤ 1`'s own first-`m` draw — and
it **dominates the replacement in both halves at once**:

| arm | served | 95 % CI | p90 | p90 95 % CI |
|---|---:|---|---:|---|
| incumbent | 83.0 % | [78.8–87.2] | 0.1369 | [0.0913–0.1727] |
| `req ≤ 1` alone | **97.9 %** | [96.2–99.7] | **0.1196** | [0.0974–0.1658] |
| both (join) | 83.0 % | [78.8–87.2] | 0.1285 | [0.0875–0.1727] |
| `logd` + `req` | 92.7 % | [89.9–95.5] | 0.1285 | [0.0932–0.1727] |
| **depth-conditional** | **97.6 %** | [95.8–99.3] | 0.1234 | **[0.0913–0.1412]** |

⚠️ **It wins in each half and does not win overall, and the difference is a mix
effect rather than a contradiction.** Per half it is better than the replacement
on p90 **twice** — 0.1554 against 0.1820 thin, 0.0673 against 0.0744 deep — and
level on served. Pooled, its p90 point estimate is marginally *worse* (0.1234
against 0.1196), because the two arms serve slightly different Brief sets and the
replacement's extra members land in the easy half. The per-half comparison is the
like-for-like one. Its p90 interval is also **materially tighter** (upper bound
0.1412 against 0.1658), which is the tail the acceptance bar reads.

⚠️ **The served gap between these two arms is BELOW this rig's noise floor.**
97.6 % against 97.9 % is 0.3 points, and re-warping the same candidate flips
`served` **2.82 %** of the time (below). Nothing here separates the two arms on
served, and no amendment should claim it does. What separates them is the per-half
p90 and what they cost the §2.2 argument.

⚠️ **What that buys is a decision that strands nothing.** In the deep half the
depth-conditional arm **is** the incumbent, member for member, so the proportion
argument the scalar pair carries in `proposer.md` §2.2 stands wherever the pool is
deep — and the pool is deep on 51.7 % of Briefs. Only where the incumbent would
otherwise hand back fewer than `m` candidates does the sound bound fill the draw.
The replacement wins the same served rate by discarding that argument everywhere.

⚠️ **Trap: `gate_effect.py`'s per-Brief draw was never reproducible.** It seeded
with `hash(brief["k"])`, and `hash` on `str` is salted per process unless
`PYTHONHASHSEED` is set, so every run drew a **different** sample and the
README's "seed 20260819 throughout" never held for it. The Brief *sample* was
always fine; the per-Brief *candidate* draw was not. Fixed to `zlib.crc32`, the
same fix and reason as `experiments/solver-toy/probe6.py`. **`out/gate_effect_briefs.json`
is one unreproducible draw and ADR 0032 rests on it**; its run-to-run variance has
never been measured.

⚠️ **Trap: the incumbent is evaluated on ROUNDED terms in the existing rig.**
`gate_effect.term_distances` rounds to 4 dp before storing and
`stretch_terms.incumbent` compares the rounded value to 1.0, so a donor at
`d_aspect = 1.0000164` passes `incumbent()` while `gated_pool` refuses it.
Contamination measured at **1 candidate in 7 827, 1 Brief in 115** — immaterial
there, and `gate_depth.py` compares unrounded.

⚠️ **Trap: this run is resumable and the sweep must be run with `python -u`.**
The first attempt was killed at ~31 % after 58 minutes and left **nothing** —
results were in memory and stdout was block buffered, so a 0-byte log. Every warp
is now appended to `out/gate_depth_warps.jsonl` and flushed as it lands; a re-run
skips what the file holds, and a Brief whose draws are not all present is dropped
from the analysis rather than crashing it. Do not pipe the sweep through `tail`:
the pipe re-buffers what `-u` unbuffered.

⚠️ **Trap: CP-SAT at a time cap is NOT deterministic, and this is the noise floor
for every timed figure in this directory.** Two sweeps ran concurrently by
accident and warped 1 489 of the same `(brief, donor)` pairs twice, with the same
seed, the same targets and the same `--time=3.0`. Status agreed every time, but
**2.82 % disagreed on `served`** and **14.71 % on `dev`** — the solver returns
whatever it reached when the cap fired, and under different CPU load that is a
different solution. Consequences: a `last wins` dedupe made the same analysis move
between two reads of one file (`req ≤ 1` p90 0.1196 → 0.1217), so
`gate_depth.py` now keeps the **first** occurrence per key; and **no difference of
a few tenths of a point on `served` is real** in any of these rigs unless it is
reproduced. The 14.9-point and 31.0-point gaps above are far outside it; the
0.3-point gap between the replacement and the depth-conditional arm is far inside.

### The second seed, and what it does and does not settle

ADR 0032 rests on a draw nobody can reproduce, which is precisely the reason not
to overturn it on one sample. Repeated at **seed 20260830**, `n = 200` (194
Briefs with a non-empty bucket, 2 587 warps), against seed 20260819's 288:

| | incumbent | `req ≤ 1` | join | **depth-conditional** |
|---|---:|---:|---:|---:|
| served, seed 1 | 83.0 % | 97.9 % | 83.0 % | 97.6 % |
| served, seed 2 | 79.9 % | 99.0 % | 79.9 % | 98.5 % |
| **thin** p90, seed 1 | 0.2124 | 0.1820 | 0.2124 | **0.1554** |
| **thin** p90, seed 2 | 0.1922 | 0.1922 | 0.1922 | **0.1369** |
| **deep** p90, seed 1 | 0.0673 | 0.0744 | 0.0671 | 0.0673 |
| **deep** p90, seed 2 | 0.0646 | 0.0797 | 0.0646 | 0.0646 |

**Every qualitative claim survives.** The incumbent and the join collapse together
at realised depth and are indistinguishable from each other on both seeds; the
replacement's gain is concentrated in the thin half and is ~1 point in the deep
half; in the deep half the incumbent keeps the better p90 (0.0646 against 0.0797);
and the depth-conditional arm holds the best thin-half p90 on both seeds while
being, by construction, exactly the incumbent in the deep half.

⚠️ **Seed 2 strengthens the fifth arm specifically.** In the thin half the
replacement buys **nothing** on p90 there — 0.1922, identical to the incumbent —
while the depth-conditional arm reaches **0.1369**. So the replacement's whole
thin-half advantage on seed 2 is served rate, not tail quality, and the fifth arm
takes both.

⚠️ **What the two seeds do NOT settle: the pooled p90 between the replacement and
the fifth arm, which changes sign.** Seed 1 has the replacement ahead
(0.1196 against 0.1234); seed 2 has the fifth arm ahead (0.1179 against 0.1096).
That comparison is a mix effect over differently-served Brief sets and it is not
resolvable at this sample size — do not quote it in either direction. The
per-half comparison is stable across both seeds and is the one to quote.

### Why ADR 0032's m = 3 absolutes are so far from these, and what it is NOT

The published m = 3 row is 88.1 % served / p90 0.2303; the same rule here is
95.1 % / 0.1515. Seven points and ~52 % is far too large to be the lost sample,
and the obvious suspect is ADR 0037 — it moved **43,24 % of rooms by a mean
+0,561 m²** and raised 59 dwellings' living floor, a systematic shift that would
move absolutes while preserving ordering. **It is not that.** Two things rule it
out.

**The draw semantics account for most of the gap on their own.** 4e draws `m`
**with replacement** from the warped rows, so at `m = 3` over 3 distinct rows it
is best-of-`3·(1−(2/3)³)` = **best-of-2.11**, not best-of-3. Re-scoring *this*
data under 4e's urn and changing nothing else:

| rule | best-of-3, no replacement | **best-of-3, WITH replacement** | ADR 0032 |
|---|---:|---:|---:|
| incumbent | 95.1 % / 0.1515 | **89.7 % / 0.2061** | 88.1 % / 0.2303 |
| both (join) | 97.1 % / 0.1526 | **92.2 % / 0.2061** | 89.4 % / 0.2294 |
| `req ≤ 1` alone | 94.6 % / 0.1998 | **88.2 % / 0.2414** | 89.4 % / 0.2543 |
| `logd` + `req` | 96.6 % / 0.1846 | **91.7 % / 0.2216** | 89.1 % / 0.2333 |

That is **77 % of the served gap and 69 % of the p90 gap** from the estimator
alone. ⚠️ **4e's `m` is not the engine's `m`** — a rig quoting best-of-*m* with
replacement is quoting a shallower draw than the name says, and the shortfall
grows with `m`. This is a second, independent reason the existing `m = 8` block
was never quotable.

**The residual is not consistently signed, which is what rules 0037 out.** After
the estimator is matched, three rules sit *above* ADR 0032 (+1.6, +2.8, +2.6
points) and `req ≤ 1` sits **1.2 points below** it. A systematic target shift
signs its residuals alike; sampling and the 2.82 % solver floor do not. And the
direction is wrong anyway: 0037 **raised** a floor on 59 dwellings, which makes
`served` harder, so its effect runs opposite to the observed gap.

⚠️ **So the market arm's "before" side is NOT visible here and the debt is not
even partly discharged.** The gap is an estimator artefact plus noise, and it
carries no usable information about what 0037 moved. **62 and 67 still owe it.**
