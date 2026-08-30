# demo-sheet — a Baku Brief, drawn

The first drawing this map has ever produced. Everything upstream of it existed
already and had been measured; nothing had asked the result for a sheet.

```
Brief (MIDA)  ->  retrieval gate  ->  warp  ->  projection  ->  Plan  ->  sheets
briefs_az.py      admissible_pool    warp_geom  solver.project  src/bim_engine
```

The drawing layer lives in **`src/bim_engine/`** — the first shipping code in
this repo — because `openings.md`, `annotation.md` and the Drawing check are
specifications the engine will use verbatim, not throwaway measurement rigs.
This directory is the throwaway half: the Brief construction, the run loop and
the reporting.

## Run

```
./venv/Scripts/python.exe experiments/demo-sheet/run.py                # 5 Briefs
./venv/Scripts/python.exe experiments/demo-sheet/run.py 10 --k=8       # 10, pool 8
./venv/Scripts/python.exe experiments/demo-sheet/run.py 10 --otaq=2    # 2-otaq only
./venv/Scripts/python.exe experiments/demo-sheet/run.py 10 --soft      # ticket 59's arm
./venv/Scripts/python.exe experiments/demo-sheet/run.py 10 --door-min=rig --no-draw
./venv/Scripts/python.exe experiments/demo-sheet/_s14.py               # the spec's own example
cd src && ../venv/Scripts/python.exe -m bim_engine.selftest            # annotation.md §14
```

`--time=` is the per-warp CP-SAT cap, `--limit=` the projection cap,
`--door-min=` one of `max` (default) / `min` / `rig` — see the fourth note
below — and `--no-draw` serves without drawing, for a threshold arm where only
the survivor counts matter. Seed `20260830` throughout.

Writes four files per served Brief, all gitignored:

| file | audience | what is on it |
|---|---|---|
| `<brief>-sheet1.png` | `practitioner` | general arrangement: poché, swings, glazing, tags, the four dimension tiers, opening marks, title block, notes, area fraction |
| `<brief>-sheet2.png` | `practitioner` | door, window and room schedules |
| `<brief>-preview.png` | `both` | the eager preview — the SAME derivation with the `practitioner` elements filtered out |
| `<brief>.dxf` | — | both sheets as paper-space layouts over one model space |

plus `out/run.json` and `out/run_<arm>.json`. The preview is not a second
renderer: `annotation.md` §1 tags each annotation element `both` or
`practitioner` and a render target draws the elements tagged for it, so both
images come off one `dimensions.derive` and one `openings.place`.

| file | what it is |
|---|---|
| `briefs_az.py` | MIDA's 318 published Baku room schedules -> Briefs in the warp's own shape |
| `run.py` | the pipeline, best-of-pool, and the reporting |
| `_s14.py` | `annotation.md` §14's worked example, drawn — the oracle |
| `_dump.py` | one Brief's dimension ladder, printed. Debug only |
| `_determinism.py` | is the pipeline reproducible at a fixed seed? F13's own check |

## The oracle, and why it comes first

`src/bim_engine/selftest.py` reproduces **`annotation.md` §14 number by number**:
five clear rectangles, five areas including the two that only round correctly
half-up, the Envelope inner, `yaşayış sahəsi`, five doors with their catalogue
widths / leaves / setting-out datums, two windows with their series widths,
positions, GOST designations and sills, four tier-2 chains, an empty tier 2b,
two tier-3 chains and four setting-out dimensions.

That example was written by hand before any of this code existed, which makes it
a real oracle rather than a restatement of the implementation. **Every number
agrees.** Two things did not, and both are recorded rather than smoothed over:

- **`t_ext`.** §14 states its exterior edges at 300 mm; the shipped profile's
  `t_ext_total` is **500** (`engine_choice`, provisional, blocked on Baku's
  degree-day figure). Tier 1 therefore reads 8350 / 6350 here against the spec's
  8150 / 6150. The profile is the authority and the spec example is stale.
- **Even window positions.** §6.1 says a window is *"centred on its clear run,
  rounded to even millimetres per ADR 0004"*, but §14's own tier-3 chain reads
  `1275 | 1800 | 2425 | 1350 | 1000` — two odd ticks. ADR 0004 binds published
  *dimensions*, and the opening width stays even either way. The position is not
  rounded; §14 is the evidence.

## What the run reports

`out/run.json` carries one record per Brief and every candidate inside it, per
`experiments/acceptance-thresholds/`'s standing rule — a new statistic off this
study costs seconds rather than a re-solve.

Per Brief: the pool depth the gate admitted, how many donors were warped, how
many the warp refused, how many the projection refused, how many produced an
invalid Plan, and which candidate was drawn. Per drawing: the sheet size and
scale from §9's ladder, door and window counts, chain counts, which rung of §7's
tag degradation ladder fired, and **all twelve Drawing-check predicates**.

## Five things that will bite whoever runs this next

**The projection is posted HARD here, and ticket 59's arm was not.** That arm
softened `coverage`, `exterior`, `wet_cluster` and `circulation` because it was
measuring starvation, and 191 of its 273 candidates then failed the validator on
exactly those four. A Plan that reaches a drawing has to have passed the bar, so
those refusals are taken as INFEASIBLE instead and the cost shows up as a
shallower survivor rate rather than as an invalid sheet. `--soft` restores 59's
configuration for comparison; it is not the demo default.

**A Brief's envelope aspect is not in an eksplikasiya.** MIDA publishes areas and
no geometry, and the gate's third term is an aspect ratio. It is defaulted to the
median aspect of the donors sharing the Brief's exact room multiset — a measured
default over the population the donor comes from — and it is declared in
`run.json` as an Assumption. A different default is a different retrieval.

**`eyvan` is inside the published total and is excluded here.** Checked, not
assumed: on record 0 the five rooms sum to 34,97 = `internal`, one of them a
3,91 m² eyvan. The median Brief loses **6,6 %** of its listed area to it. That
is `area_convention.brief_semantics` in numbers, and it means a Baku listing's
headline and this engine's target area are not the same quantity.

**The door contact threshold is a `--door-min=` arm, and the default is not the
map's.** `real_arm.DOOR_MIN_ADR` is a single `mm(1.0)`; ADR 0021 says the
threshold is `structural opening width + t_int + 400`, which is 1250 to 1450 mm.
Paired over ten Briefs and 72 donors: at the rig's 1000 mm, **16,7 %** of
candidates produce a Plan that passes the acceptance bar and that no door can be
placed in; at 1250 that halves; at the Brief's widest door it is **zero**, and
Brief-level service is 7/10 on all three arms because best-of-pool absorbs the
difference. `run.py` defaults to `--door-min=max` for that reason.
`docs/research/drawing-layer-first-run.md` F4 carries the table.

**`bathroom_combined` has no row in `door_for_room`.** MIDA's commonest wet room
is *Sanitar qovşağı*, which is `bathroom_combined` in the AZ name table and in
the ergonomic layer — and `profiles.AZ.openings.door_for_room.map` carries
`wc`, `bathroom`, `shower_room` and `storage` and not that. `openings.md` §9 is
explicit that a room type arrives with a mapping row or the gate fails, so this
is a real hole in the profile rather than a hole in this rig. It is mapped to
the corpus `BATHROOM` label here, which resolves to `bathroom`, and the hole is
reported rather than patched — inventing the row would be exactly the
`engine_choice`-without-a-label failure the profile exists to prevent.
