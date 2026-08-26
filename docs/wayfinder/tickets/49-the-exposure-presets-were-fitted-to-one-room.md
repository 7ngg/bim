---
id: 49
title: The exposure presets were fitted to a measurement of one room
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: []
writes:
  - experiments/solver-toy/geometry.py (EXPOSURE_PRESETS)
  - experiments/envelope-exposure/
  - docs/adr/0003-the-envelope-is-an-inner-face-ring-of-typed-edges.md
---

# The exposure presets were fitted to a measurement of one room

## Question

**`EXPOSURE_PRESETS` was fitted to a distribution that described the largest room
in each dwelling, not the dwelling.** Re-fit it, and decide which of the numbers
measured at the old presets have to be re-run.

`experiments/corpus-smoke/exposure_swiss_dwellings.py` unioned each dwelling's
`area` polygons. They are **disjoint** — the wall sits between them — so the union
is always a `MultiPolygon`, and `max(geoms, key=area)` took the largest part. Most
of a single room's perimeter faces other rooms of the same dwelling, which the
script scores as *party*, so the published distribution was biased low by roughly
a factor of two. Corrected by *H8 and the single-aspect flat*; the script and
`dataset-inventory.md` §1.5 are already fixed, and the correction reproduces the
old numbers exactly when the bridge step is removed, so this is not in doubt.

| | published | corrected |
|---|---|---|
| p5 / p25 | 0.16 / 0.23 | **0.33 / 0.51** |
| median | **0.37** | **0.67** |
| p75 / p95 | 0.47 / 0.59 | **0.78 / 0.89** |
| ≥0.99 | 0 of 569 | 5 of 569 |
| median area of the thing measured | 23.9 m² | 75.3 m² |
| median exterior run | 8.1 m | 27.5 m |

Two presets were fitted to the wrong column, and `dataset-inventory.md` §1.5 said
so in as many words — *"the dwelling-type presets are well-chosen but should now
be fitted rather than guessed"*:

- **`flat_single_aspect`** at 0.25, fitted to a p25 of 0.23. Real p25 is **0.51**.
- **`corpus_median`** at 0.37 (`S` full plus `N` 0.45), and `geometry.py`'s own
  comment calls it *"the case a spec should quote as typical"*. Real median is
  **0.67** — two full edges, which is a **dual-aspect** flat, not a one-and-a-bit.

So the preset the map has been quoting as typical models a flat roughly half as
exposed as the typical real one, and the preset named *single aspect* now sits
below the real p5 of 0.33 — which may be right, since a genuine single-aspect flat
is a tail case and the corrected p5 is where it should be anchored. **That is a
judgement this ticket owns**: whether the presets are quantiles of the corrected
distribution or named dwelling types that happen to be checked against it.

## What was measured at the old presets

This is the part that decides how big the ticket is. Everything below ran at
`corpus_median` or `flat_single_aspect` and therefore at roughly half the real
exposure:

- **`experiments/envelope-exposure/probe_exposure.py`** — the Brief-generation
  table (`flat_single_aspect` fails at 6, 7, 8; `corpus_median` **0/5 at n = 6**).
  The n = 6 corpus-median failure is quoted on the map as *worse than the map's
  framing*, and it is the single most likely thing to evaporate.
- **`experiments/envelope-exposure/probe_diversity.py`** — the flat-versus-house
  diversity ratios, **0.54× at 5 rooms and 0.73× at 7**, which the *Variant
  generation and ranking* fog patch carries as a second, independent cause of the
  diversity asymmetry. Both arms move if `corpus_median` moves.
- **ADR 0003**'s evidence for the ≤2-notch cap, and *The two-notch cap is now
  evidenced*, which is open and reads the same distribution.
- Anything in `experiments/room-rectangles/` and `docs/research/solver-formulation.md`
  that names a preset.

⚠️ **What does not move.** The headline that no real flat resembles the
fully-exposed geometry the 6.25 s-at-24-rooms timing assumed **survives** — 0.9 %
at ≥0.99 rather than 0.0 %. Timings measured at `detached` are unaffected, and so
is anything measured at 100 % exposure, which is most of the solver sweep.

⚠️ **The concurrency rule binds here.** `experiments/solver-toy/` is claimed by
*What an ordered entry sequence costs the solver*; the presets live in its
`geometry.py`. Do not take this ticket while that one is claimed.

## Deliverable

Re-fitted `EXPOSURE_PRESETS` with the fit recorded, the re-runs above either done
or explicitly declined with a reason, and a line on ADR 0003 saying which of its
evidence was re-measured.
