# What the Envelope's edge ring costs

Two probes over `experiments/solver-toy`, produced while re-solving the
*Homeowner product surface* prototype's plans at corpus-median exposure. They
outlived the prototype, so they live on `master`; the prototype itself stays on
branch `prototype/homeowner-surface`.

They import `solver-toy` and never edit it — that directory is claimed by *The
solver has only ever seen guillotine layouts*.

```
../../venv/Scripts/python.exe probe_exposure.py     # seconds
../../venv/Scripts/python.exe probe_diversity.py    # ~3 min
```

## `probe_exposure.py` — Brief feasibility is not monotone in room count

Counts, per (exposure, room count), how many of five seeds produce a **Brief at
all**: `make_brief`'s CP-SAT room-type assignment, which must satisfy H8 with
wet clustering and circulation. Upstream of the solve, so nothing here is a
timing result.

| n | detached | terrace_mid | flat_corner | corpus_median | flat_single_aspect |
|---|---|---|---|---|---|
| 4 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| 5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| **6** | 5/5 | 3/5 | 3/5 | **0/5** | **0/5** |
| 7 | 5/5 | 5/5 | 5/5 | 5/5 | 0/5 |
| 8 | 5/5 | 5/5 | 5/5 | 5/5 | 0/5 |
| 9 | 5/5 | 5/5 | 5/5 | 5/5 | 1/5 |
| **10** | 5/5 | 5/5 | 5/5 | 5/5 | **5/5** |

`flat_single_aspect` fails at 6, 7 and 8, mostly fails at 9, and **succeeds at
10** — where `envelope_for` switches from an L to a U and the second notch adds
exterior run on the one live edge. The binding quantity is *how much exterior
run the envelope offers*, and `envelope_for(n)` varies that non-monotonically.
So a claim of the form **"dead from n rooms" is measuring the envelope n
selects, not n.**

⚠️ **n = 6 also fails at corpus median**, which `geometry.py`'s own comment
calls the case a spec should quote as typical. H8 is not only a single-aspect
problem.

⚠️ This is the toy's generator and the toy's minima, **not** the shipped
ergonomic layer — the same caveat *Whether a Room may be more than one
rectangle* attached to its own sub-7-room finding. It corroborates a direction
and settles no number.

## `probe_diversity.py` — the flat/house diversity gap is H8, not the missing axis

Mean pairwise fraction of floor cells whose room **kind** differs, across six
survivors of one Brief. Envelope *geometry* is held identical — same
`envelope_for(n)`, same shape, same size, same seeds — and only the edge ring's
typing changes.

| n | detached | corpus_median | ratio |
|---|---|---|---|
| 5 | 0.522 (0.512–0.531) | 0.282 (0.267–0.293) | **0.54×** |
| 7 | 0.749 (0.731–0.782) | 0.549 (0.542–0.558) | **0.73×** |

**Quote the ratio, never a single figure.** `SolveConfig` defaults to
`workers = 8` and stops on **wall-clock**, and multi-worker CP-SAT is not
reproducible under a wall-clock deadline even with a fixed `random_seed`: two
runs of a single-pass version of this probe returned **0.283 and 0.263** for the
same cell. Hence three repeats and a reported range. The ranges for the two
exposures do not overlap at either room count, so the gap is solid; the third
decimal is not.

**Why it matters to *Variant generation and ranking*.** That patch attributes
the flat-versus-house diversity gap to a diversity axis handed to invented
Envelopes and withheld from stated ones. This holds the Envelope fixed and the
gap still appears, so **H8 is a second and independent cause** — habitable rooms
are pinned to the exterior run, and a flat has less of it. Giving stated
Envelopes an aspect-ratio axis does not touch this half, and this half is the
one that applies to every flat.
