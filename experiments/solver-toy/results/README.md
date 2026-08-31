# Raw sweep rows — which files may be quoted

One JSON object per solve. Every row carries its full improving-solution trace,
so any time limit below 30 s can be re-derived without re-solving.

## `*_v2.jsonl` — **quotable. These are the numbers in Part II.**

965 solves, serial, `workers=4`, 30 s, 4-core Ivy Bridge. Taken after the
ground-truth generator was fixed to honour whatever dimensional reading the
solver enforces (`scenarios.fits_kind(rect, kind, clear_t)`).

| file | suite |
|---|---|
| `S1_v2` | grid vs eroded-millimetre area encodings |
| `S2_v2` | the main grid — room count × exposure × 8 seeds |
| `S3_v2` | Proposal quality (σ) |
| `S4_v2` | τ |
| `S5_v2` | degenerate and shuffled Proposals |
| `S6_v2` | worker scaling |
| `S7_v2` | distinct Plans off one Proposal |
| `S8_v2` | τ × Proposal noise |

## `repeat_seeds_main.jsonl` — **quotable, on its own machine only. Part X.**

216 solves, ticket 83. **A DIFFERENT MACHINE from every other file in this
directory**: Tiger Lake-H `Model 141`, **12 logical cores**, against the 4-core
Ivy Bridge `Model 58` every `_v2` row came from. `num_workers = 4` is four of
twelve uncontended here and was the whole contended machine there, so **no wall
figure may be compared across the two**. Status, objective and validity may be.

One instance per room count (8, 12, 24) at the shipped configuration — `mm_affine`,
`erode`, `t_int` 100, **τ = 4**, `corpus_median`, σ 0,5, 15 s — with only CP-SAT's
`random_seed` moving, over **12 seeds × 2 replicates × 3 arms**. This is S7's design
at S2's scale, and it is what discharges Part I's owed ≥10-seed repeat; `S2_v2`
cannot, because `sweep.py` moves the scenario seed and the solver seed together.

Arms: `base` (shipped), `il` (`interleave_search` at the same wall cap), `det`
(`interleave_search` + `max_deterministic_time`, no wall cap — ADR 0043 decision
5's prescription). Provenance in `repeat_seeds_meta_main.json` per decision 6.

⚠️ **These rows predate this file's own `t_start` rule and do not carry it.**
The run was taken with nothing else running, but the rows cannot *prove* it —
which is exactly the gap `t_start` exists to close. `repeat_seeds.py` writes it
now; the fix is forward-only and this grid was not re-run for it.

⚠️ **The traces are dropped**, unlike every `_v2` file: three arms × 216 rows of
40-entry trace is bulk nothing here reads. Time-to-first-Plan and time-to-VALID
are kept as `first` and `valid_at`, so a budget below 15 s cannot be re-derived
from these rows without re-solving.

## `S[1-7].jsonl` (no suffix) — **superseded. Do not quote.**

The first pass, kept as an audit trail. In it the ground truth was built against
the *published* reading while the solver enforced ADR 0001's *clear* one, so the
ground truth was not a witness and every `erode=true` row's validity figure is
measuring that defect rather than solve quality. Symptom: `OPTIMAL` results
carrying non-zero `slack` and objectives above 100 000.

Where v1 and v2 disagree, v2 is right and the difference is the defect. The
sharpest case is S3 at 12 rooms, where v1 shows 2 of 5 seeds INFEASIBLE at
σ = 0.00 — noise-free Proposals failing — which is impossible and was the clue.

An earlier pass than either was discarded entirely and is not here: a watcher
script started a second solver concurrently, so its timings were taken under CPU
contention. Rows now carry `t_start` so that is detectable rather than invisible.

## Text outputs

`erosion_cost.txt`, `grid_aligned.txt`, `windowless.txt` and the `report_*.txt`
files are generated summaries, reproducible from the scripts named in
`docs/research/solver-formulation.md` Part II.
