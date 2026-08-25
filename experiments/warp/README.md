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

Order: `room_area_spread.py` first (it builds `out/dwelling_rooms.json`, which
every other script reads).

```
python experiments/warp/room_area_spread.py
python experiments/warp/gate_curve.py
python experiments/warp/fit_warp.py 400 --time=3.0
python experiments/warp/pool_fidelity.py 150 --take=8
python experiments/warp/coverage_restated.py
```

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
