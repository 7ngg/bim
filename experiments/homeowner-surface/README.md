# PROTOTYPE — Homeowner product surface (ticket 13)

**Throwaway.** Lives on branch `prototype/homeowner-surface`, never merged to
`master`. The decisions it settled are on the ticket; this is the primary source
behind them.

## Run

Double-click `prototype.html`. No toolchain, no server.

Deep links for a specific branch: `prototype.html#happy/gallery`,
`#zero/zero`, `#rooms`, `#big`, `#access`, `#happy/export`, and a trailing
`/en` switches language (`#happy/gallery/en`).

## What is real and what is faked

**Exposure is `corpus_median`** — Swiss Dwellings' median 0.37, one full edge
plus 0.45 of the opposite one — not `detached`. The first cut of this prototype
used `detached` (100 % exterior, every edge can hold a window) and the plans read
as bungalows. Party edges draw at `t_party` 280 and exterior at `t_ext_total`
500, so the outer face steps, which is what a real flat plan does.

⚠️ **The 6-room case is unavailable at this exposure** and is absent for that
reason, not by choice: `make_brief` finds no valid room-type assignment at any of
five seeds. `probe_exposure.py` maps it — and the pattern is **non-monotonic**,
so it is an envelope-shape effect, not a room-count effect. `probe_diversity.py`
measures what the exposure costs in variety.

| Real | Faked |
|---|---|
| Every plan is a **solved, validated layout** from `experiments/solver-toy` (`make_fixtures.py`) | The `StatedBrief`/`ResolvedBrief` pairs are hand-built; `resolve()` is not run |
| `t_int` 150, `t_ext_total` 500 and the clear-region erosion (ADR 0001, ADR 0010) | Door positions — derived here by a spanning tree from the entry, not by *Opening placement rules* |
| Fixture footprints and the body zone, from `room-constraints.json` `ergonomic` | The fixture *packing* inside a room is the prototype's own and is crude |
| Opening widths from `profiles.AZ.openings.catalogue` | `engine_view` numbers are plausible constants, not computed |
| AZ decimal comma (`verified`) | **Azerbaijani room names are unsourced placeholders** — see the ticket's handoff |

## Rebuild

```
../../venv/Scripts/python.exe make_fixtures.py    # re-solve the layouts
../../venv/Scripts/python.exe make_standards.py   # re-pull the shipped constants
../../venv/Scripts/python.exe build.py            # inline both into prototype.html
node check.js                                     # headless: geometry + render
```

`check.js` asserts every room is reachable through a door from the entry, every
clear dimension clears its shipped ergonomic floor, and every plan renders.
