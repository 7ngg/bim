# Rooms that are not rectangles

Harness for *Whether a Room may be more than one rectangle* (ticket 28). Findings
live in `docs/research/room-rectangles.md`; the decision is ADR
[0014](../../docs/adr/0014-a-room-is-one-or-two-rectangles-and-the-proposal-decides.md).

Corpora come from `data/corpora/`, which is gitignored — see
`docs/research/dataset-inventory.md` to acquire them. Outputs go to `out/`, also
gitignored; regenerate by running the scripts. Run everything with the pinned
interpreter, `./venv/Scripts/python.exe`.

| script | what it does | runtime |
|---|---|---|
| `smoke_zero_box.py` | does `AddNoOverlap2D` ignore a zero-area box in the pinned OR-Tools? The whole absence mechanism rests on it | seconds |
| `morphology.py` | opening and closing that do what their names say, with a selftest. Replaces `why_k.clean()`, which does not | seconds |
| `erosion_check.py` | ADR 0001's erosion at a **reflex** corner, and the room-tag containment claim — assertions, not prose | seconds |
| `k_tolerance.py [n]` | how many rectangles a real room needs at a stated 98 % tolerance, by type; and what a *correct* 500 mm clean-up buys | ~50 min at 1200 |
| `solver_parts.py` | the projection solver with 1–2 parts per Room. Not a script — imported by the sweeps | — |
| `validate_parts.py` | independent checker for a Plan whose Rooms are 1–2 rectangles, sharing no code with the model | — |
| `l_truth.py` | a ground truth in which some Rooms genuinely **are** Ls, by merging adjacent pairs of a guillotine dissection | — |
| `l_truth_check.py [n]` | asserts those merges are real Ls that still tile exactly | ~1 min |
| `sweep_k2.py [seeds]` | what an optional second rectangle **costs**, against a truth that never needs one | ~2 h at 10 seeds |
| `sweep_designA.py [seeds]` | Design A against three controls, on a truth that **is** concave. The table the decision rests on | ~75 min at 6 seeds |
| `kind_rates.py` | per room *type*, how often a free solver reaches for a second rectangle — against the Brief's real kind multiset | ~2 min |

Order: `sweep_k2.py` before `kind_rates.py`, which reads its JSON.

## Four things that will bite whoever runs this next

**Do not run two sweeps at once.** This is a 4-core machine and every solve asks
for 4 workers. Two concurrent sweeps inflate every second in both. The arms
interleave row by row so ratios survive contention, but absolute p50 and p95 do
not — and item 2 of the ticket is about absolute cost. `k_tolerance.py` is
single-threaded numpy and contends too, though only its own runtime suffers.

**An absent part is pinned at the origin, so anything indexed by part must be
gated on presence.** The first version of `solver_parts._add_relations` posted
`x2[p] <= x1[q]` ungated; with `q` absent that reads `x2[p] <= 0` and forces a
present primary to zero width. It reported **36 % INFEASIBLE against a control at
0 %** and made an L look compulsory, which is a plausible-looking result and a
wrong one. Contacts (`_gated`), the join and H8 are all gated; relations now are
too. If you add a constraint over parts, gate it.

**`why_k.clean()` is broken — use `morphology.py`.** Its dilation is clipped to
the array it is given, which for `why_k.py` is the room's own tight bounding box,
so the composition reduces to eroding every room by 500 mm on all sides and
restoring nothing. A 500 mm strip is deleted outright and no notch is filled at
any size. `morphology.selftest()` asserts the properties the names promise,
including the one that bounds what any clean-up can claim: closing fills a bite in
the middle of an edge and **never** one at a corner.

**A count is not a rate.** `scenarios.composition(n)` is not the Brief's kind
multiset — `assign_kinds` draws from a filler list within `comp_bounds`, so kinds
appear that `composition` never names. `kind_rates.py` regenerates the Briefs
instead. Using `composition` as the denominator produced a per-type ordering that
was wrong and looked right.

## The rig, and where it differs from the published sweep

15 s, τ = 4, `mm_affine`, eroded minima, corpus-median exposure, σ = 0.5 m, four
workers, coverage soft — the shipped decision, with **`t_int` 150 per ADR 0010**
where `experiments/solver-toy/sweep.py` ran at 100. Absolute seconds here are
therefore not comparable with the published 13.65 s p95; the arms are comparable
with each other, which is what item 2 asked for.

Room counts are **7, 8, 10 and 12**. Not 4, 5 or 6: `scenarios.make_brief` finds
no feasible room-type assignment below 7 once minima are eroded — at `t_int` 100,
120 *and* 150, and at both `detached` and `corpus_median` exposure — where at
`clear_t = 0` all three build. **No solver measurement on this map covers the
bottom half of C13's 3–10 band**, and that is a finding rather than a limitation
of this harness.
