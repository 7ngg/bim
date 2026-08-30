# `plane-accounting/` — does ADR 0039's encoding fit, and what does it buy?

Ticket 77. ADR 0039 decided that `solver.py` should read the **bar plane** —
the Space area ADR 0001 publishes — by subtracting the erosion band per *side*
rather than on all four. Part VII of `solver-formulation.md` is *"a derivation
and two hand-checks"*: the encoding was never built, its cost against the 15 s
cap and τ = 4 was never measured, and `dim.max_area`'s cap side had never been
posted by any arm on this map. This directory pays that debt.

Ticket 78 pays the next one. ADR 0040 consequence 3: the encoding is derived for
a Room that is **one** rectangle and ADR 0014 gives a Room **one or two**, so it
subtracts a band along the shared edge — twice — that the Room does not have.
The `_parts` files below are that half, and they run on the **53,9 %** of the
converted index the `--parts=1` arm excluded.

Nothing here edits `solver-toy/`, `warp/` or `room-rectangles/`. All three are
imported read-only, the idiom `envelope-exposure/` and `h8-frontage/` already
use, and the right one here because an A/B needs every arm live in one process.

## Files

| file | ticket | what it is |
|---|---|---|
| `bar_plane.py` | 77 | the encoding: `BarPlaneProjector`, a `LayoutProjector` subclass overriding **one** method. Plus the placed-rectangle oracle the CP-SAT form is checked against. |
| `selftest.py` | 77 | nine assertions, run before any timing. Part VII's two hand-checks, the oracle against `absolute_area.space_m2`, the model against the oracle, and `plane="solver"` against `solver.project`. |
| `arms.py` | 77 | the run. Five arms over the same warped candidates `project_join.py` joined, with the warp posting ADR 0033's floor. |
| `seeds.py` | 77 | six CP-SAT seeds per arm — the seed-to-seed spread II.1 states its own finding against, and the bar this cost has to clear. |
| `report.py` | 77 | the four measurements, read off a finished run so a new statistic costs seconds rather than an hour. |
| `parts_plane.py` | 78 | the same encoding for a Room of **one or two** parts: the join band the model posts, and one vertex rule for the truth that covers both. `BarPartsProjector` is `solver_parts.PartProjector` with `_add_dimensions` replaced and `bar_plane`'s contact helpers bound in. |
| `selftest_parts.py` | 78 | nine assertions, including the join band by hand, the reduction to Part VIII's `corners − reflex`, L / T / Z / rectangle against shapely, and arm `A` against `solver_parts.project_parts`. |
| `arms_parts.py` | 78 | the `--parts=2` run. Five arms, each one change from the last: binding site, plane, join term, cap. |
| `report_parts.py` | 78 | ticket 78's measurements off a finished `arms_parts.py` run. |

## Reproducing

```
python experiments/plane-accounting/selftest.py
python experiments/plane-accounting/arms.py --selftest      # the warp swap is a no-op
python experiments/plane-accounting/arms.py --tag=main      # ~1 h, 340 pairs x 5 arms
python experiments/plane-accounting/seeds.py 36 --tag=seeds # ~20 min
python experiments/plane-accounting/report.py --tag=main

python experiments/plane-accounting/selftest_parts.py            # 10 assertions
python experiments/plane-accounting/arms_parts.py --selftest
python experiments/plane-accounting/arms_parts.py --tag=parts    # ~2 h, 332 pairs x 5 arms
python experiments/plane-accounting/seeds_parts.py 24 --tag=seedsp   # 19 rows, ~29 min
python experiments/plane-accounting/report_parts.py --tag=parts
```

`out/` is gitignored, so each run is preserved under `series/` the way
`experiments/warp/series/` preserves its own — `arms_rows_main.json.gz`,
`seeds_rows_seeds.json.gz`, `armsp_rows_parts.jsonl.gz`,
`seedsp_rows_seedsp.jsonl.gz`, and `report_main.json` /
`report_parts.json` verbatim and uncompressed, because those are the files Parts
VIII and IX quote. To re-report without re-solving, gunzip a rows file back into
`out/` and run the matching reporter. `arms_parts.py` and `seeds_parts.py` **append** one
JSON object per line and take `--skip`, because a whole-list dump per pair loses
everything back to the last complete write if the process is killed mid-dump —
which cost the ticket 78 run 88 pairs before the log was changed.

Findings are written up as **Part VIII** (ticket 77) and **Part IX** (ticket 78)
of `docs/research/solver-formulation.md`, and decided in **ADR 0040** and
**ADR 0041**.
