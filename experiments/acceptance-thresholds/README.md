# Fitting the ENGINE_CHOICE acceptance thresholds

Harness for *Fit the ENGINE_CHOICE acceptance thresholds to the corpora*
(ticket 20). Findings live in `docs/research/acceptance-thresholds.md`; the
decision is ADR 0023.

Corpora come from `data/corpora/`, which is gitignored — see
`docs/research/dataset-inventory.md` to acquire them. Outputs go to `out/`, also
gitignored; regenerate by running the scripts.

| script | what it does | runtime |
|---|---|---|
| `census.py [n]` | **the only expensive step.** One pass over all 42,985 in-band Swiss dwellings: per-room class, area and bbox, wet grouping, envelope closing, jamb returns, inter-opening piers, entrance-door count | ~13 min |
| `parts.py` | the aspect question on the converted arm, per part, centreline eroded by `t_int` | seconds |
| `resplan_aspect.py` | the aspect question on the second corpus — the only rule with no precedent must not rest on one | ~2 min |
| `fit.py` | every threshold's distribution and its cost curve | seconds |
| `reject.py` | the full hard registry against real dwellings, per rule and as a conjunction | seconds |

Order: `census.py` before `fit.py` and `reject.py`. `parts.py` and
`resplan_aspect.py` are independent of it.

```
./venv/Scripts/python.exe experiments/acceptance-thresholds/census.py
./venv/Scripts/python.exe experiments/acceptance-thresholds/fit.py
./venv/Scripts/python.exe experiments/acceptance-thresholds/reject.py
```

`reject.py` honours `CENSUS_FILE` if you want to run it against an older census.

**Everything reads `census.py`'s record, so a new statistic off this study costs
seconds — if you add one, add its inputs to `census.py`'s record.** The same rule
`thickness-fidelity/` carries, and for the same reason.

## Four things that will bite whoever runs this next

**Do not erode the raw arm.** Swiss room polygons are already **clear** — inner
faces, wall body in the gap, p50 nearest-neighbour gap 99 mm, share touching
0.000 (`rectangularisation.md` §1.1). The ticket's instruction to *"erode before
you compare"* is correct and applies to the **converted** arm only, whose
rectangles are centreline. `parts.py` is the only script here that erodes, and it
must. Eroding the raw arm would take a clear number to a clear number minus a
wall.

**An Opening belongs to exactly one edge.** The first version of
`jamb_returns` assigned every opening to every boundary edge within reach, which
double-counts a door near a corner onto the perpendicular wall and manufactures
near-zero jamb returns. It now assigns by nearest-centroid-to-*segment* and
nothing else. The `min_pier_mm` measurement inherits that assignment, so a change
there moves §7 of the findings.

**Filter the sub-1.5 m runs before quoting `open.fits_segment`.** 75.1 % of the
openings that fail the rule as written sit on a run under 1.5 m, where the
opening is effectively the whole wall — a cased or full-width opening with no
jamb by construction. Quoting the unfiltered 7.56 % as the rule's cost overstates
it by 8×; the number is 0.92 %.

**Condition the converted arm on `dim.min_clear_short` before quoting aspect.**
Unconditioned, the per-part aspect distribution has a `max` of 56.00 — a part one
cell wide, 250 − 150 = 100 mm clear, which `dim.min_clear_width` kills long
before aspect is consulted. Measuring aspect on parts a prior hard rule has
already rejected double-counts the same broken conversion. Conditioned, the tail
is 7.36.

## Two approximations, stated because they bound the conclusions

**Wet groups are merged at corner contact.** `wet_groups` tests a buffered
intersection at τ = 0.30 m, the same tolerance `measure_swiss.contact_graph`
uses, so two wet rooms touching only at a corner count as one group. The true
group count is therefore **at least** what is reported, which moves
`wet.plumbing_group_count`'s 14.34 % up and never down — the safe direction for
the conclusion it supports.

**The Envelope interior is a morphological closing at 150 mm.**
`buffer(+r).buffer(−r)` fills every internal partition up to 300 mm and restores
the outer boundary, so the result is the floor at the inner face of the exterior
wall. Partitions thicker than 300 mm do not close, which would *reduce* the
measured interior; the corpus's own p50 wall gap is 99 mm, so this is rare.
