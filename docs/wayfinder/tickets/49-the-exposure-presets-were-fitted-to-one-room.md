---
id: 49
title: The exposure presets were fitted to a measurement of one room
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
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

## Resolution

**The presets are quantiles of the corrected distribution, not named dwelling
types — and the judgement was settled by measurement rather than taken.** The
ticket framed the choice as open. It is not: the ring shape, measured here for
the first time, refutes the named-type family outright.

They are also no longer fitted on the quantity the ticket assumed. **Everything
that had been measured at `corpus_median` or `flat_single_aspect` was re-run, and
three published results did not survive** — including one the ticket did not
expect to lose.

### The fit is on exterior run per room, not on a fraction of perimeter

`EXPOSURE_PRESETS` is a **four-vector**. §1.5 publishes a **scalar**. A scalar
cannot fit a four-vector, which is why both presets had been produced by choosing
a ring shape by hand and tuning one number until the scalar matched — the step
that made them fragile in the first place.

A fraction also does not transfer between dwellings whose perimeters differ, and
these differ badly: at eight rooms the toy Envelope carries **36.0 m of perimeter
around 75.0 m²** where the real median dwelling carries **47.6 m around 94.1 m²**.
Matching the fraction therefore under-delivers the run, and **H8 reads run** — a
room needs a window's width of façade and cannot spend a percentage. Run is also
the stabler target: it is **flat in the corpus** (median 3.97–4.41 m from four
rooms to twelve) where the fraction is not.

Corpus run per room, 2,238 dwellings over 600 floors: p5 **2.09 m**, p25
**3.28**, median **4.19**, p75 **5.09**, p95 **6.94**. Anchored at **n = 7**, the
corpus median room count and the centre of C13's band.

| preset | fitted to | ring | at n = 7 | was |
|---|---|---|---|---|
| `detached` | ceiling, 100 % | four | 4.86 m — p68 | unchanged |
| `corpus_median` | **p50** | four-sided | 4.21 m — **p51** | p4–p10 |
| `flat_corner` | **p25** | adjacent pair | 3.29 m — p25 | p10–p25 |
| `terrace_mid` | **p25** | opposite pair | 3.25 m — p24 | p10–p25 |
| `flat_single_aspect` | **p5** | single | 2.07 m — p5 | **below p1** |

`corpus_median`'s name is accurate for the first time. `flat_single_aspect` was
running **off the bottom of all 2,238 dwellings** — the ticket's guess that p5 is
where it belongs is confirmed, and it is anchored there. `flat_corner` and
`terrace_mid` are now deliberately a **matched pair**: the same exposure on a
different ring, so the two isolate shape at fixed run, which is what
`probe_diversity` needs and what nothing previously provided.

### The ring shape refutes the named-type family

Nobody had ever measured the vector. Real dwellings, counting a side as an aspect
when it carries ≥ 15 % of its own bbox edge:

| ring | share | preset naming it |
|---|---:|---|
| four-sided | **63.3 %** | none |
| three-sided | **26.0 %** | **none at all** |
| adjacent pair | 4.6 % | `flat_corner` |
| opposite pair | 3.8 % | `terrace_mid` |
| single | 2.2 % | `flat_single_aspect` |

The three flat presets name **10.6 %** of the corpus between them, and the 89.3 %
that are three- or four-sided had no preset of their shape at all.
Threshold-insensitive: three-plus-four stays above 80 % from a 0.05 to a 0.33
cut, and is still 62.5 % at 0.50.

**The keys are kept anyway**, and that is a scope decision rather than a
preference. They are named in `brief.md`, `acceptance-bar.md`,
`room-constraints.json`, `CONTEXT.md`, ADR 0003 and three experiment directories
this ticket does not write — renaming would have been a wide blind edit into
claimed files. So a key is now a **quantile with a ring shape**, and every
existing caller silently gets the corrected exposure.

### Three results did not survive the re-run

| Result | Was | Now |
|---|---|---|
| H8 kills the Brief at six rooms, corpus-median exposure | 0/5 seeds | **5/5** — gone |
| `flat_single_aspect` "fails at 6, 7, 8, mostly at 9" | 0/5 at 7 and 8 | fails at **6** only, 3/5 at 8 |
| The flat-versus-house **diversity gap** | 0.54× at 5, 0.73× at 7 | **1.00× and 0.98×** — gone |

The first is what the ticket predicted would evaporate, and it did.

**The third is the one nobody expected, and it is the largest.**
`envelope-exposure/README.md` held the diversity gap as a **second and
independent cause** of the flat-versus-house diversity asymmetry, alongside the
diversity axis handed to invented Envelopes and withheld from stated ones — and
the *Variant generation and ranking* fog patch carries it as such. At corrected
exposure **there is no gap**: 0.514–0.524 against 0.515–0.525 at five rooms, the
ranges overlapping almost exactly. The probe's own caveat is what makes this
trustworthy as an *absence* rather than a small effect — it reports ranges
precisely because multi-worker CP-SAT under a wall-clock deadline is not
reproducible, and non-overlap was the old reading's whole claim. **The asymmetry
goes back to the diversity axis alone.**

### What survives

The headline that no real flat resembles the fully-exposed geometry the
6.25 s-at-24-rooms timing assumed **stands** — 1.1 % of dwellings at ≥ 0.99.
Every timing measured at `detached` is untouched, which is most of the solver
sweep.

And **the non-monotonicity survives**, which was the finding worth keeping:
`flat_single_aspect` fails at six, passes at seven, drops to 3/5 at eight and
passes at nine and ten. n = 6 is still the worst row across three presets,
because `envelope_for(6)` picks an L. *"Dead from n rooms" is still measuring the
envelope n selects, not n.*

⚠️ **But the six-room failure is now unexplained.** It has **5 250 mm of frontage
slack** at the re-fitted preset, so it is not the frontage arithmetic, and
nothing has identified what it is. Handed on with the rest.

### Two re-runs declined, with reasons

- **ADR 0003's notch-cap evidence and *The two-notch cap is now evidenced*.** The
  ticket listed both as reading the same distribution. **That premise is false** —
  checked, not assumed: ticket 47 contains no reference to exposure of any kind,
  and its evidence comes from `experiments/rectangularise/`, which never reads a
  preset. The notch cap is corpus-conversion geometry. **Neither needs a re-run**,
  and 47 is unaffected.
- **`experiments/room-rectangles/` and `docs/research/solver-formulation.md`.**
  Both genuinely move and neither is this ticket's to write —
  `solver-formulation.md` belongs to *What an ordered entry sequence costs the
  solver*. Handed on **priced rather than merely named**, on ticket 52.

### What could not be fixed here, and is now owned

Three structural defects, all inside `experiments/solver-toy/`, which this ticket
may not write and whose fixes change what the solver is *given* rather than what
it is measured against. Raised as **The toy Envelope is more compact than a real
dwelling** rather than left on an ADR for nobody:

1. **Every preset drifts across C13's band.** `envelope_for(n)` scales area
   linearly and perimeter as its root, so a constant four-vector delivers a
   falling run per room against a corpus that is flat in n. `corpus_median` sits
   at the corpus **p85 at four rooms and p25 at twelve** — a 60-percentile swing
   from one number, and part of the non-monotonicity above is this artefact
   rather than the envelope family. **Published as a drift table, not hidden.**
   Above nine rooms the corpus median is **unreachable at any preset**,
   `detached` included.
2. **The Envelope is more compact than a real dwelling** — perimeter/area **0.390
   against the corpus 0.572** at twelve rooms — and **`AREA_PER_ROOM_M2` is 9.65
   against a corpus median of 11.36 m²**, which prices from the corpus side the
   fixture defect *The solver has only ever seen guillotine layouts* left with no
   number.
3. **`Envelope.exterior_fraction` double-counts.** `all_faces()` emits each bbox
   edge in full *and* all four faces of every notch, so a corner notch's removed
   stretch is counted twice — 144 grid units of true perimeter counted as **180**
   at eight rooms, a denominator 25 % too large. It is *the quantity every old
   preset was tuned to hit*. The phantom faces reach `exterior_faces()` too, but
   that half is harmless: `contains` forbids a room inside a notch, so no room
   can be flush with the removed stretch and claim its daylight. Corrected in
   `envelope-exposure/true_fraction.py`, which is what the new presets were
   fitted against.

### One limit this fit does not remove

⚠️ **The ring-shape distribution is Swiss building form.** 63.3 % four-sided
reflects Swiss point-blocks; Baku mass housing is slab blocks, where a mid-block
flat is dual-aspect at best. C14 already accepts Swiss-shaped layouts to
Azerbaijani conventions permanently — but the exposure ring is not a layout, it
is the **feasibility gate**, so an AZ dwelling could fail a Brief that this
lattice passes. Recorded on ADR 0003 and on ticket 52 rather than measured, since
no AZ corpus exists on this map.

### Artifacts

- `experiments/envelope-exposure/fit_presets.py` — the corpus measurement, and
  the first measurement of the ring's shape. Writes
  `series/dwelling_sides.json.gz`, 2,238 records, so a later percentile costs
  seconds rather than a re-scan of a 1.09 GB corpus.
- `experiments/envelope-exposure/fit_ladder.py` — the fit, which prints the
  transcribed block and the drift table.
- `experiments/envelope-exposure/true_fraction.py` — a correct
  `exterior_fraction`.
- `experiments/solver-toy/geometry.py` — the re-fitted `EXPOSURE_PRESETS`, and a
  ⚠️ on `exterior_fraction`'s docstring, which quoted the dead numbers.
- `docs/adr/0003-…` — amendment section. The ADR's **decision is untouched**;
  what moved is every number attached to a preset, plus two claims made in the
  ADR's own voice: consequence 5's *halves and quarters* (measured: **0.67× and
  0.43×**) and the construction bullet's whole-edge preset examples.

### Declared on resolution, not taken quietly

**`docs/research/dataset-inventory.md` §1.5** is unclaimed and its correction is
already in place, so nothing is owed there. But §1.5 says the presets *"should
now be fitted rather than guessed"* — they now are, and the section does not know
it. One line pointing at `experiments/envelope-exposure/` is owed by that file's
next holder.

⚠️ **`docs/adr/0003-…` is listed on the map as ticket 47's**, and this ticket's
own `writes:` claims it too — a collision the map's conflict table does not
record. 47 was **unclaimed** when this ran, so the concurrency rule held, and the
amendment is a self-contained section at the foot of the file that touches
nothing in the notch-cap material 47 will write. 48's outstanding §7 correction
was **deliberately left alone**: the map assigns it to 47, and writing it here
would have recreated the parallel-write defect that rule exists to prevent.
