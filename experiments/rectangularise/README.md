# Rectangularising real rooms

Harness for *Rectangularising real rooms* (ticket 22). Findings live in
`docs/research/rectangularisation.md`; the decision is ADR 0008.

Corpora come from `data/corpora/`, which is gitignored — see
`docs/research/dataset-inventory.md` to acquire them. Outputs go to `out/`, also
gitignored; regenerate by running the scripts.

| script | what it does | runtime |
|---|---|---|
| `probe_swiss.py` | geometry census: do rooms touch, what axis are they on, how rectangular under each axis choice | ~1 min |
| `measure_swiss.py` | the three per-room conversions over all 42,986 in-band Swiss dwellings | ~35 min |
| `measure_resplan.py` | the same over 16,617 ResPlan plans | ~20 min |
| `analyse_swiss.py [file]` | every per-room table — loss, tiling, adjacency, relations, Graph2Plan, by room type, reject gates | seconds |
| `fit_rects.py [n] [--resplan]` | **the conversion that ships**: one CP-SAT fit per dwelling | ~0.8 s/dwelling |
| `analyse_fit.py [file]` | what the fit costs, and ADR 0003's notch cap | seconds |
| `ablate.py [n]` | which constraint family the reject rule is actually rejecting for | ~50 min |
| `survivorship.py` | is the corpus that survives conversion the same corpus, only smaller | seconds |
| `rectilinear_k.py [n]` | how many rectangles a real room actually needs — the evidence for ticket 28 | ~20 min |
| `why_k.py [n]` | what causes k>2: trivial notches, angled walls, or real shape | ~12 min |
| `guillotine_share.py` | how many real dwellings are non-guillotine — the evidence for ticket 29 | seconds |
| `analyse_k2.py [k1] [k2]` | **ticket 40**: what a second rectangle per Room buys, paired on the dwelling key | seconds |
| `name_rate.py [n]` | how wide the lower bound is — which rooms Design A's naming misses, and why | ~10 min at 400 |
| `coverage_thinning.py [k1] [k2]` | the pool thinning factor, for ticket 23 to redo `proposer.md` §2.2 with | seconds |
| `render_sheet.py [--pick=] [--n=]` | **ticket 27**: draw a converted dwelling beside the real one — the eyeball check no metric stands in for | ~4 s/dwelling |
| `void_census.py [n]` | ticket 27: how much floor no Room claims, and how many rooms the one dwelling frame shears | ~2 s/dwelling |
| `envelope_family.py` | **ticket 47**: what the residual Envelope loss *is* — stepped or off-axis — and what a donor gate costs on the proxy against the thing itself | seconds |
| `real_boundary.py [n]` | **ticket 58**: how many rectangles a real outline needs, exactly, and whether the parts could hold rooms | ~0.4 s/dwelling |
| `real_envelope.py [n]` | **ticket 58**: emits the `cap` and `real` Envelopes plus a truth re-fitted to the true mask, for `solver-toy/real_arm.py` | ~2 s/dwelling |

Order: `measure_*` before `analyse_swiss.py`, `fit_rects.py` before
`analyse_fit.py`. `envelope_family.py` reads `out/swiss_fit_k2.json` and the
`out/swiss_dw.pkl` cache, so it costs seconds and never re-fits — **if you add a
statistic about the Envelope's shape family or about donor fidelity, add it
there rather than re-deriving it from the corpus.**

## Two things that will bite whoever runs the ticket-58 pair

**A converted dwelling is not a witness for its own boundary, and the failure
reads as a coordinate bug.** `swiss_fit_k2.json`'s rectangles are fitted to the
**cap** Envelope, a superset of the true outline, so against the true outline
they fail H1 (a Room poking into ground the dwelling never occupied) *and* H3
(cells no rectangle reaches) — seven of the first eight slots. `real_envelope.
refit_to_true_mask` re-runs the conversion with the domain set to the true mask
by substituting `envelope_approx` **at the call boundary**; `fit_rects.py` is
deliberately not edited, because four closed decisions rest on it and this needed
a different domain, not a different conversion. If you need another domain, copy
that pattern rather than adding a flag.

**The true-mask re-fit is much slower than the cap fit and returns INFEASIBLE
where the shipped one decides.** Budget ~2 s/dwelling against the cap fit's 0.8,
and expect refusals: that is a fact about the domain and it is reported rather
than retried.

## Running the two arms (ticket 40)

```
python experiments/rectangularise/fit_rects.py 2600 --out=swiss_fit_k1.json
python experiments/rectangularise/fit_rects.py 2600 --k2 --out=swiss_fit_k2.json
python experiments/rectangularise/analyse_k2.py
```

Same dwellings, same order, same code — only `k_of` differs, so the delta is the
rectangle count and not the sample. `fit_rects.py` caches the parsed corpus to
`out/swiss_dw.pkl` on first run (the CSV parse is ~90 s and this ticket runs it a
dozen times over); **delete that file if the corpus or the filters change.**

Flags: `--k2` raises the ceiling to two rectangles per Room, `--select=shape`
(default) names which Rooms may take one from the real room's own shape and
`--select=free` lets every Room have one, `--leg=` / `--join=` move ADR 0014's
leg floor and join, `--time=` the solver budget, `--only=keys.json` restricts to
a key list, `--every=` the checkpoint interval. Ticket 85 adds `--seed=`,
`--workers=` and `--dettime=` (> 0 swaps the wall cap for CP-SAT's deterministic
time and turns on `interleave_search`; measured and refused, see below).

## The configuration is a decision, and it was wrong twice (ticket 85)

**Defaults are now `WORKERS = 1`, `TIME_LIMIT = 30.0`, `SEED = 1` — ADR 0046.**
Do not change one without reading `rectangularisation.md` §16.

**`WORKERS = 4` cited a floor measured on another model.** Its comment said
*"ticket 15: two workers is a floor for correctness"*, and that floor is real —
`solver-formulation.md` II.6, on the **shipped projection at 24 rooms**. This
corpus is filtered to the 3–10 engine-room band and tops out at **10 rooms**, so
the justifying regime occurs in **0,000 %** of inputs. The citation is why nobody
re-checked it: it made the number look examined. Four racing workers under a wall
cap made the fit non-reproducible — 26,5 % of covers differed between two runs of
identical code — and one worker costs **nothing** (3,31 s/dwelling against
3,28–3,33) and is byte-identical at 30 s.

**`random_seed` was never the problem.** CP-SAT's own default is **1**, so the rig
was always seeded; varying it to 7 gives disagreement indistinguishable from
running seed 1 twice. It is now set explicitly only because ADR 0043 requires the
seed be *recorded*, and an implicit default becomes false the day the library
changes it.

**`interleave_search` + `max_deterministic_time` is refused, and it was measured
before it was refused.** At four workers it costs 1,85× the wall time, loses
proofs, has no wall bound at all, and *still* returns different covers — three of
them on records both runs proved OPTIMAL at an identical objective, which is
google/or-tools **#3948**. At one worker it is 2,6× at budget 10 and **8,4×** at
budget 30, with a 145 s tail. ADR 0043 adopted this combination for the warp,
where it was free; **it does not transfer**, because those models finish inside
the budget and these do not.

**Two runs, or it is not a measurement.** `repeat_check.py` asserts the published
plane — status, objective, part count, shape class — over two solves of one
input, and is proven in both directions. It deliberately does **not** assert the
cover: tied optima move and that is upstream. Run it after touching anything in
`fit()`:

```
./venv/Scripts/python.exe experiments/rectangularise/repeat_check.py
./venv/Scripts/python.exe experiments/rectangularise/determinism.py selftest
```

## Four things that will bite whoever runs this next

**At two rectangles per Room, `--select=free` decides nothing.** Giving every
Room an optional second rectangle — ADR 0014's Design B — makes the shipped 10 s
budget useless: over 40 dwellings it returned **0 OPTIMAL and 0 INFEASIBLE**, 26
FEASIBLE and 14 UNKNOWN, every one of them burning the full limit at 10.38
s/dwelling. `converted` then means *found something in 10 s*, not *is
representable*, and ADR 0008's "the tier is decidable, not a timeout" stops being
true. `--select=shape` — Design A, the Rooms named from the real room's own
shape — is **2.9× faster and decides 33 of 40**. The k = 1 arm decides all of
them at 0.85 s. This is ADR 0014's measured 11–12× versus 1.2–1.7×, reproduced on
the conversion fit.

**A `--select=shape` result is a LOWER bound and must be quoted as one.** The
naming is greedy — largest inscribed rectangle, then the largest rectangle in
what is left — so a Room whose best two-rectangle cover needs a *non-maximal*
first rectangle is missed and stays one rectangle. `name_rate.py` measures how
wide that is, and separates it from the Rooms the leg floor refuses on purpose.

## Two more things that will bite whoever runs this next

**OR-Tools can abort the process.** The ResPlan fit died after 1,000 plans on an
internal `CHECK` failure — `Infeasible solution! source: 'default_lp'` — which is
a C++ abort that Python cannot catch. `fit_rects.py` checkpoints every 200
records for exactly this reason. A corpus-scale run needs a subprocess per
dwelling or a restart-from-checkpoint loop, not a `try`.

**Real corpus polygons are not all valid.** 46 of 296,653 Swiss rooms fail
`is_valid`. Every set operation goes through `_op()` in `measure_swiss.py`, which
repairs with `make_valid` and falls back to snapping to a 1 mm grid — the model's
own resolution per ADR 0001 — and counts each repair rather than swallowing it.

## Looking at it (ticket 27)

```
python experiments/rectangularise/render_sheet.py --pick=spread --n=8
```

then open `out/sheets/SHEET.html`. Picks: `spread` (across the agreement range
and across room counts), `median`, `p5`, `p95`, `worstroom`, `k2`, `corridor`,
`spurious`, `infeasible`, `feasible`. `--plane=centreline` turns off the
t_int/2 inset; the default `clear` is the one that compares like with like.

**Three of the conversion's fidelity headlines are constraints restated, not
measurements**, and quoting them as evidence overstates what was checked:

| quoted as | actually |
|---|---|
| "zero adjacencies destroyed" (`edges_lost = 0`) | contact is a HARD constraint; a dwelling that would lose one is refused instead. The number that carries the information is the refusal rate. |
| "zero separation directions flipped" | the true relations are posted hard (`use_rel`). `flipped` and `weakened` are 0 by construction, over all 97,090 axis-pairs. |
| per-room area error inside ±10 % | the area band IS ±10 %, posted hard. p99 of \|aerr\| is 0.111. |

What is genuinely free, and therefore worth quoting: `cell_agreement`, the IoU
distribution, the **refusal rate**, and `boundary_lost` — the one fidelity
number nothing constrains.

## Three approaches that were measured and rejected

Recorded because each looked obviously right and cost a run to disprove.

- **Posting exact tiling hard.** 17 of 40 INFEASIBLE, 22 timed out. Also simply
  the wrong model: C10's amendment posts tiling soft in the shipping solver, so a
  corpus prepared under stricter rules is measuring a different problem.
- **L1 corner displacement as the fitting objective** — the shipped one. Among
  exact tilings it is nearly uncorrelated with how much of the dwelling ends up in
  the right room: **IoU median 0.14** against **0.82** for minimising misassigned
  cells. Projection and fitting are different problems.
- **A notch as the bounding box of its complement component.** Over-cuts, and
  deleted a room outright in 15 % of dwellings. The notch is the largest rectangle
  *inside* the component (`max_rect_in_mask`), which under-cuts and costs a room
  nothing.

## The frame, and three traps in the ticket-46 probes

`off_frame_gate.py`, `frame_choice.py` and `frame_residual.py` measure what
`dwelling_frame` does to a dwelling built on two angles. ADR 0031 and
`docs/research/rectangularisation.md` §15. All three read the cached
`out/swiss_fit_k2.json` plus the raw geometry, run in about four minutes each,
and **write to no other directory**.

**1. Do not quote a `void_census.py` band beside a `§15` one.** They measure the
same defect on different populations — 400 dwellings against all 2,317 — and the
small one's last two bands hold six and five dwellings. That is where ADR 0017's
**0.167** came from; the index figure is **0.397**. Any table with fewer than ~30
dwellings in a band is a direction, not a rate.

**2. `off_frame_max` and `frame_residual` are different quantities and a cut on
one does not transfer.** The first is the largest per-room deviation (what
`void_census.py` reports); the second is the **area-weighted mean**, which is
what ADR 0031 publishes. A 10° line on the max is roughly a 2–4° line on the
residual, and neither is a threshold the design uses — the decision deliberately
places no cut at all.

**3. The modal frame looks like a coin flip and is not.** `frame_choice.py`
counts 377 dwellings improved against 357 regressed; the regressions mean
**0.057°** and the improvements mean **0.923°**. Count them and you will refuse a
change worth +327° net. Weigh them.

⚠️ **The frame change is specified and NOT applied.** `frame_of` in
`frame_choice.py` is the reference implementation; `dwelling_frame` in
`measure_swiss.py` still returns the union-mrr angle, and every number in this
directory is on that frame. ADR 0031 requires the swap to ride the single re-run
`fit_rects.py` already owes for `proposer.md` §2.2.1's five index fields —
changing it alone re-bases `swiss_fit_k2.json` and every corpus figure on the map
with it.
