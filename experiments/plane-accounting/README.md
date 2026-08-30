# `plane-accounting/` — does ADR 0039's encoding fit, and what does it buy?

Ticket 77. ADR 0039 decided that `solver.py` should read the **bar plane** —
the Space area ADR 0001 publishes — by subtracting the erosion band per *side*
rather than on all four. Part VII of `solver-formulation.md` is *"a derivation
and two hand-checks"*: the encoding was never built, its cost against the 15 s
cap and τ = 4 was never measured, and `dim.max_area`'s cap side had never been
posted by any arm on this map. This directory pays that debt.

Nothing here edits `solver-toy/` or `warp/`. Both are imported read-only, the
idiom `envelope-exposure/` and `h8-frontage/` already use, and the right one
here because an A/B needs both arms live in one process.

## Files

| file | what it is |
|---|---|
| `bar_plane.py` | the encoding: `BarPlaneProjector`, a `LayoutProjector` subclass overriding **one** method. Plus the placed-rectangle oracle the CP-SAT form is checked against. |
| `selftest.py` | nine assertions, run before any timing. Part VII's two hand-checks, the oracle against `absolute_area.space_m2`, the model against the oracle, and `plane="solver"` against `solver.project`. |
| `arms.py` | the run. Five arms over the same warped candidates `project_join.py` joined, with the warp posting ADR 0033's floor. |
| `seeds.py` | six CP-SAT seeds per arm — the seed-to-seed spread II.1 states its own finding against, and the bar this cost has to clear. |
| `report.py` | the four measurements, read off a finished run so a new statistic costs seconds rather than an hour. |

## Reproducing

```
python experiments/plane-accounting/selftest.py
python experiments/plane-accounting/arms.py --selftest      # the warp swap is a no-op
python experiments/plane-accounting/arms.py --tag=main      # ~1 h, 340 pairs x 5 arms
python experiments/plane-accounting/seeds.py 36 --tag=seeds # ~20 min
python experiments/plane-accounting/report.py --tag=main
```

`out/` is gitignored, so the run is preserved under `series/` the way
`experiments/warp/series/` preserves its own — `arms_rows_main.json.gz` (2,2 MB
raw, 161 KB packed), `seeds_rows_seeds.json.gz`, and `report_main.json` verbatim
and uncompressed, because it is the file Part VIII quotes. To re-report without
re-solving, gunzip a rows file back into `out/` and run `report.py`.

Findings are written up as **Part VIII** of `docs/research/solver-formulation.md`
and decided in **ADR 0040**.
