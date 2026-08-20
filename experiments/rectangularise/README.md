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

Order: `measure_*` before `analyse_swiss.py`, `fit_rects.py` before
`analyse_fit.py`.

## Two things that will bite whoever runs this next

**OR-Tools can abort the process.** The ResPlan fit died after 1,000 plans on an
internal `CHECK` failure — `Infeasible solution! source: 'default_lp'` — which is
a C++ abort that Python cannot catch. `fit_rects.py` checkpoints every 200
records for exactly this reason. A corpus-scale run needs a subprocess per
dwelling or a restart-from-checkpoint loop, not a `try`.

**Real corpus polygons are not all valid.** 46 of 296,653 Swiss rooms fail
`is_valid`. Every set operation goes through `_op()` in `measure_swiss.py`, which
repairs with `make_valid` and falls back to snapping to a 1 mm grid — the model's
own resolution per ADR 0001 — and counts each repair rather than swallowing it.

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
