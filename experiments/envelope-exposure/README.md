# What the Envelope's edge ring costs

Four probes over `experiments/solver-toy`. Two began as offcuts of the
*Homeowner product surface* prototype; two were added by *The exposure presets
were fitted to a measurement of one room*, which re-fitted `EXPOSURE_PRESETS` and
re-ran the other two against the new values.

They import `solver-toy` and never edit it — except for the `EXPOSURE_PRESETS`
block itself, which is that ticket's to write. The rest of that directory is
claimed by *What an ordered entry sequence costs the solver*.

```
../../venv/Scripts/python.exe fit_presets.py [n_floors]   # ~8 min, scans the corpus
../../venv/Scripts/python.exe fit_ladder.py               # seconds, off the series
../../venv/Scripts/python.exe true_fraction.py            # seconds
../../venv/Scripts/python.exe probe_exposure.py           # seconds
../../venv/Scripts/python.exe probe_diversity.py          # ~3 min
```

## ⚠️ Read this before quoting any older number from this directory

Three results this README used to publish **did not survive** the re-fit. They
were all measured at `corpus_median` or `flat_single_aspect`, which had been
fitted to a distribution that measured **one room per dwelling** rather than the
dwelling — `dataset-inventory.md` §1.5, corrected. Both presets were therefore
running at roughly half the real exposure.

| Result | Was | Now |
|---|---|---|
| H8 kills the Brief at six rooms, corpus-median exposure | 0/5 seeds | **5/5** — gone |
| `flat_single_aspect` "fails at 6, 7, 8, mostly at 9" | 0/5 at 7 and 8 | fails at **6** only, 3/5 at 8 |
| The flat-versus-house **diversity gap** | 0.54× at 5 rooms, 0.73× at 7 | **1.00× and 0.98×** — gone |

## `fit_presets.py` — the ring's shape, measured for the first time

`EXPOSURE_PRESETS` is a **four-vector**, a fraction of exterior run per bbox edge.
Every number ever fitted to it came from a **scalar** — §1.5's fraction of
perimeter facing outside. A scalar cannot fit a four-vector, so both fitted
presets were produced by choosing a ring shape by hand and tuning one number
until the scalar matched. Nobody had measured the shape.

600 floors, **2,238 dwellings**. Per dwelling: weld the rooms across their walls,
rotate onto the dominant wall direction, type each boundary segment exterior or
party by §1.5's rule, and assign it to W/E/S/N by its outward normal.

The scalar reproduces §1.5 on four times the sample — p5 0.34, p25 0.55, median
0.68, p75 0.80, p95 0.90, and 1.1 % at ≥ 0.99.

**The shape refutes the preset family.** Counting a side as an aspect when it
carries ≥ 15 % of its own bbox edge:

| ring | share | preset that names it |
|---|---:|---|
| four-sided | **63.3 %** | none — `detached` only at 100 % |
| three-sided | **26.0 %** | **none at all** |
| adjacent pair | 4.6 % | `flat_corner` |
| opposite pair | 3.8 % | `terrace_mid` |
| single | 2.2 % | `flat_single_aspect` |

The three flat presets name **10.6 %** of real dwellings between them, and the
89.3 % that are three- or four-sided had no preset of their shape. Threshold-
insensitive: three-plus-four stays above 80 % anywhere from a 0.05 to a 0.33 cut,
and is still 62.5 % at 0.50.

**The abstraction also leaks.** 59.9 % of dwellings have at least one side whose
exterior run **exceeds its own bbox edge** — concavity. A preset caps at 1.0 and
cannot express them. This is why the scalar and the shape disagree: the median
profile is 1.02 / 0.98 / 0.66 / 0.21 yet the scalar is 0.68, because a real
dwelling's perimeter is far longer than its bounding box's.

Writes `series/dwelling_sides.json`, one record per dwelling, so a later
percentile costs seconds rather than a re-scan of a 1.09 GB corpus. **If you add
a statistic to this study, add its inputs to the series** —
`experiments/thickness-fidelity/`'s rule, and the reason `fit_ladder.py` runs in
seconds.

## `fit_ladder.py` — the re-fit, on run per room

Fits the five preset vectors, and fits them on **exterior run per room** rather
than on a fraction of perimeter. A fraction only transfers between dwellings
whose perimeters match, and these do not: at eight rooms the toy Envelope carries
36.0 m of perimeter around 75.0 m² where the real median dwelling carries 47.6 m
around 94.1 m². **H8 reads run** — a room needs a window's width of façade and
cannot spend a percentage. Run is also the stabler target: it is flat in the
corpus (median 3.97–4.41 m from four rooms to twelve) where the fraction is not.

Corpus run per room: p5 **2.09 m**, p25 **3.28**, median **4.19**, p75 **5.09**,
p95 **6.94**. Anchored at n = 7 — the corpus median room count and the centre of
C13's 3–10 band.

| preset | fitted to | ring | at n = 7 |
|---|---|---|---|
| `detached` | ceiling, 100 % | four | 4.86 m — corpus p68 |
| `corpus_median` | **p50** | four-sided | 4.21 m — p51 |
| `flat_corner` | **p25** | adjacent pair | 3.29 m — p25 |
| `terrace_mid` | **p25** | opposite pair | 3.25 m — p24 |
| `flat_single_aspect` | **p5** | single | 2.07 m — p5 |

`flat_corner` and `terrace_mid` are deliberately a **matched pair** — the same
exposure on a different ring — so the two isolate ring shape at fixed run, which
is what `probe_diversity` needs. `corpus_median`'s name is accurate for the first
time; it previously ran at the corpus p3–p10, and `flat_single_aspect` ran off
the bottom of all 2,238 dwellings.

The keys are unchanged on purpose. They are named in `brief.md`,
`acceptance-bar.md`, `room-constraints.json`, `CONTEXT.md`, ADR 0003 and three
experiment directories that ticket did not write, so renaming them would have
been a wide blind edit. What changed is that **a key is now a quantile with a
ring shape, not a building form.**

### ⚠️ Every preset drifts across C13's band

`envelope_for(n)` scales area linearly in n and perimeter as its root, so a
constant four-vector delivers a *falling* run per room against a corpus that is
flat in n. `corpus_median` sits at the corpus **p85 at four rooms and p25 at
twelve** — a 60-percentile swing from one number. Above nine rooms the corpus
median is **unreachable at any preset**, `detached` included: it needs more
exterior run than the Envelope has perimeter.

The cause is not the presets. The toy Envelope is **more compact than a real
dwelling and gets more so with n** — perimeter/area 0.390 against the corpus
0.572 at twelve rooms — and `AREA_PER_ROOM_M2` is **9.65 against a corpus median
of 11.36 m²**, which is the fixture defect *The solver has only ever seen
guillotine layouts* left behind, now priced from the corpus side. Both live in
`solver-toy/` and are handed on as *The toy Envelope is more compact than a real
dwelling*.

✅ **Settled, and this section's own headline row was the noise cell.** ADR 0029.
Two corrections, both measured:

- **Quote n ≤ 11, never n = 12.** That corpus cell holds **17** dwellings and its
  boundary runs **34,6 %** longer than its own bounding box against 11,8 % at
  eleven. In the well-sampled band (5–9, N = 291–480) the toy's perimeter ratio
  against the corpus is **0,91–0,97**, not the 0,68 the twelve-room row implies.
  The compactness defect is real and about a third the size the headline claimed.
- **The lever was never the notch share.** `l_shape` and `u_shape` cut only
  **corner** notches, and a corner notch adds *no perimeter at all*:
  `envelope_for(n)`'s true boundary is exactly `2 (W + H)` at every count.
  Matching the corpus with corner notches alone needs a notch share of **27–36 %**
  against a corpus **16–21 %**. The fix is `geometry.u_shape_true` — a **mid-edge**
  notch, ADR 0003's U, which the generator had never emitted and which adds
  `2 × depth` at zero area cost. `solver-toy/` now carries both fixtures and the
  default is unchanged.

## `true_fraction.py` — `exterior_fraction` double-counts

`Envelope.exterior_fraction` is the quantity every **old** preset was tuned to
hit, and it is wrong. `all_faces()` emits each bbox edge in full *and* all four
faces of every notch, so the stretch a corner notch removed is counted twice —
once as bbox edge, once as a phantom notch face on the same line. At eight rooms
the true perimeter is 144 grid units and `all_faces()` counts **180**.

The phantom faces reach `exterior_faces()` too, which the solver reads for H8.
That half is harmless: `contains` forbids a room inside a notch, so no room can
be flush with the removed stretch and claim its daylight. The fraction is not
harmless, so this module recomputes it from the real boundary, and it is what the
new presets were fitted against.

✅ **Fixed in `geometry.py`** by *The toy Envelope is more compact than a real
dwelling* — `all_faces()` now walks the real boundary, and this module is kept as
the **independent shapely check** it agrees with: 45 (count, preset) pairs, **0
mismatches**. ⚠️ **The "harmless" half was not harmless in the one place nobody
looked**: the phantoms reached `frontage.py`'s H8 budget, which at twelve rooms
read 68 000 mm of exterior run against a true 46 000 — a numerator up to **32 %
too large**, and every arithmetic-death table on the map was computed through it.
Re-checked at every cell in the band: **zero verdicts change**, because H8's
necessary condition was never close to binding. ADR 0029.

## `probe_exposure.py` — Brief feasibility is still not monotone in n

Counts, per (exposure, room count), how many of five seeds produce a **Brief at
all**: `make_brief`'s CP-SAT room-type assignment, which must satisfy H8 with wet
clustering and circulation. Upstream of the solve, so nothing here is a timing
result.

| n | detached | terrace_mid | flat_corner | corpus_median | flat_single_aspect |
|---|---|---|---|---|---|
| 4 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| 5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| **6** | 5/5 | **3/5** | **3/5** | 5/5 | **0/5** |
| 7 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| **8** | 5/5 | 5/5 | 5/5 | 5/5 | **3/5** |
| 9 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| 10 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |

**The corpus-median failure at six rooms is gone** — 0/5 became 5/5, and it was
the single most likely result to evaporate, which is what the ticket predicted.
H8 is not a problem at typical real exposure at any count in the band.

**The non-monotonicity survives and is the real finding.**
`flat_single_aspect` fails at six, passes at seven, drops to 3/5 at eight and
passes at nine and ten. n = 6 is still the worst row across three presets,
because `envelope_for(6)` picks an L whose notch adds no run on a live edge. So a
claim of the form **"dead from n rooms" is still measuring the envelope n
selects, not n.**

⚠️ This is the toy's generator and the toy's minima, **not** the shipped
ergonomic layer. It corroborates a direction and settles no number.

## `probe_diversity.py` — there is no flat-versus-house diversity gap

Mean pairwise fraction of floor cells whose room **kind** differs, across six
survivors of one Brief. Envelope *geometry* is held identical — same
`envelope_for(n)`, same shape, same size, same seeds — and only the edge ring's
typing changes.

| n | detached | corpus_median | ratio |
|---|---|---|---|
| 5 | 0.520 (0.514–0.524) | 0.519 (0.515–0.525) | **1.00×** |
| 7 | 0.746 (0.745–0.747) | 0.727 (0.722–0.731) | **0.98×** |

**This inverts the result this file used to publish.** At the old presets the
ratios were 0.54× and 0.73×, with non-overlapping ranges at both room counts, and
that gap was carried by the *Variant generation and ranking* fog patch as a
**second and independent cause** of the flat-versus-house diversity asymmetry,
alongside the diversity axis handed to invented Envelopes and withheld from
stated ones. At corrected exposure the ranges overlap almost exactly and **the
gap is not there**. The asymmetry goes back to the diversity axis alone.

**Quote the ratio, never a single figure.** `SolveConfig` defaults to
`workers = 8` and stops on **wall-clock**, and multi-worker CP-SAT is not
reproducible under a wall-clock deadline even with a fixed `random_seed`: two
runs of a single-pass version of this probe returned **0.283 and 0.263** for the
same cell. Hence three repeats and a reported range. That caveat is why the new
reading is trustworthy as an *absence*: the ranges now overlap, which is the
signature of no effect rather than of a small one.
