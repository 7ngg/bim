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

Order: `measure_*` before `analyse_swiss.py`, `fit_rects.py` before
`analyse_fit.py`. `envelope_family.py` reads `out/swiss_fit_k2.json` and the
`out/swiss_dw.pkl` cache, so it costs seconds and never re-fits — **if you add a
statistic about the Envelope's shape family or about donor fidelity, add it
there rather than re-deriving it from the corpus.**

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
a key list, `--every=` the checkpoint interval.

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
