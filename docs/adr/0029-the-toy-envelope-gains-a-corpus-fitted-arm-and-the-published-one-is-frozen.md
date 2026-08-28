# The toy Envelope gains a corpus-fitted arm, and the published one is frozen

**Status:** accepted
**Date:** 2026-08-28
**Ticket:** *The toy Envelope is more compact than a real dwelling*
**Amends:** [ADR 0003](0003-the-envelope-is-an-ordered-ring-of-typed-edges.md) —
its rect/L/U/T family is unchanged and its two-notch cap is unchanged; what
changes is that the generator now emits **all four** members, having only ever
emitted three
**Confirms:** [ADR 0019](0019-the-solver-is-slicing-independent.md),
[ADR 0014](0014-a-room-is-one-or-two-rectangles-and-the-proposal-decides.md),
[ADR 0007](0007-published-minima-must-erode-onto-the-solve-grid.md) — all
re-affirmed at their published values, none re-run
**Related:** [ADR 0010](0010-a-space-is-bounded-by-finished-faces.md),
[ADR 0013](0013-the-room-count-promise-is-two-numbers-in-two-units.md)

## Decision

**`experiments/solver-toy/` keeps its published Envelope family, bit-exact and
default, and gains a second family fitted to real dwellings beside it. The move
between them is measured once, paired, at the shipped configuration. The
published family is never edited in place.**

Three things land with it:

1. **`geometry.Envelope.all_faces()` now walks the real boundary.** It used to
   emit every bbox edge in full *and* all four faces of every notch, double-
   counting the stretch a corner notch removed. Fixed, and cross-checked against
   the independent shapely implementation in
   `experiments/envelope-exposure/true_fraction.py` — 45 (count, preset) pairs,
   **0 mismatches**.
2. **`geometry.u_shape_true`** cuts a **mid-edge** notch: ADR 0003's **U**, the
   one member of its shape family the generator never emitted.
3. **`scenarios.CORPUS_ENVELOPES`** is the fitted family, `fixture="corpus"`,
   covering **5–11 rooms**. `FIXTURE` defaults to `"published"`.

`AREA_PER_ROOM_M2` stays at **9.65**. It is not a number to be corrected — it is
the published fixture's own constant, and the honest per-count figures live in
the corpus fixture.

**The default is frozen for reproducibility, not because the fixtures are equal.
They are not.** Measured, `fixture_delta.py`, 140 solves at the shipped
configuration: the corpus fixture **strictly dominates**. So:

> **Every new measurement is taken on `fixture="corpus"`.** `published` exists to
> reproduce Parts I–III, ADR 0014 and ADR 0019 at their published values, and for
> nothing else.

## What the move costs, measured

140 solves, matched `(n, exposure, seed)` slots, shipped config verbatim —
`mm_affine`, eroded minima, τ = 4, σ = 0.5 m, 15 s, 4 workers, `t_int` 100, five
seeds over 5–11 rooms × {`detached`, `corpus_median`}. The fixture is the only
thing that differs between the two rows of a pair.

| | survivors | time-to-VALID p50 | p90 | max | no Brief |
|---|---:|---:|---:|---:|---:|
| published | 48/70 — 68,6 % | 0,30 s | 1,26 s | 2,00 s | 20 |
| **corpus** | **60/70 — 85,7 %** | 0,27 s | 1,28 s | 2,43 s | **10** |

Paired over 70 slots: **both 48, only published 0, only corpus 12, neither 10.**
Exact McNemar **p = 0,0005**.

**There is not one slot in the grid where the published fixture produces a
survivor and the corpus fixture does not.** The gain is one-sided and it is
located, not diffuse:

| n | published | corpus | what changed |
|---:|---|---|---|
| 5 | no Brief, 10/10 | **10/10 survivors** | a whole room count gained |
| 6 | no Brief, 10/10 | no Brief, 10/10 | unchanged — see below |
| 7 | 8/10 | **10/10** | two coverage-slack failures fixed |
| 8–11 | 10/10 | 10/10 | tie |

**Time is unchanged.** p50 moves 0,30 → 0,27 s and p90 0,26 % the other way, on a
fixture carrying **+11,6 to +25,6 % more floor and +25 to +32 % more perimeter**.
A bigger, more articulated Envelope did not cost the solver anything measurable,
which is the same shape of result as ADR 0019's: the formulation is indifferent
to the property that was expected to bite.

### The bottom of C13's band moves from "below 7" to "6"

The map has carried a standing gap — *"no solver measurement on this map covers
the bottom half of C13's 3–10 band"*, because `make_brief` finds no typable
dissection below 7 rooms once minima are eroded. On the corpus fixture **n = 5
builds and solves at 10/10**. What remains is **exactly one count**: n = 6 fails
on both fixtures, deterministically, at both exposures, in `assign_kinds` rather
than in the solver. The gap is now a single named cell instead of a half-band.

## The finding this rests on: a corner notch buys no perimeter

`envelope_for` scales interior area linearly in `n` at a fixed aspect, so its
perimeter grows as the **root** of its area while a real dwelling stays
articulated. That was known. What was not known is **why no setting of the
existing knobs could fix it**:

> **Every notch this harness has ever cut is a corner notch, and a corner notch
> removes floor while adding exactly zero perimeter.** `l_shape` cuts one;
> `u_shape` cuts two, both corner-anchored — it builds a **T**, not a U. Measured:
> `envelope_for(n)`'s true boundary is exactly `2 * (W + H)` at every count in the
> band. A real dwelling's boundary runs **6–12 % longer than its own bounding
> box**, rising with room count.

So notch *share* was the wrong lever and notch *count* was the wrong lever.
Matching the corpus with corner notches alone needs a share of **27–36 %** against
the corpus's own bbox deficit of **16–21 %** — a shape that is two thin arms, not
a dwelling. A **mid-edge** notch adds exactly `2 × depth` at zero extra area cost,
which is precisely the missing quantity.

The two-notch budget is therefore split **by job**: the corner notch removes floor,
the mid-edge notch buys perimeter. Fitted that way against three targets — area,
perimeter and bounding-box occupancy — one rectilinear ring lands within **0,7 %**
of the corpus median at every count from 5 to 11, and the fitted mid-edge depth
rises 5 → 12 grid units across the band, tracking the corpus's own rising
articulation. `experiments/solver-toy/envelope_fit.py`.

### Fitting on two targets is not enough, and this is a trap worth recording

Fitted on area and perimeter alone, the search takes the over-notch route every
time: it buys the whole boundary from a large bbox, then carves the area back out
with a corner notch of 31–35 %. Every number lands, and the shape is wrong.
**Bounding-box occupancy is the third target that forces the perimeter onto the
mid-edge notch**, where real articulation actually lives.

## Why a second family and not a correction

**Because correcting `envelope_for` in place retroactively moves the substrate
under four closed decisions** — ADR 0014, ADR 0019, ticket 15's shipped 15 s and
τ = 4, and ticket 24's arrangement metric. One ticket does not silently invalidate
four. The map's own method for exactly this is a controlled second arm with the
delta measured once: ADR 0019 did it for cut structure, and *The exposure presets
were fitted to a measurement of one room* did it for presets with a committed
before/after series.

**And because the toy's job is a *controlled* harness.** `probe_diversity` holds
Envelope geometry identical and varies only the edge ring's typing; Part III's
McNemar pairing needs the same `(n, exposure, seed)` slot in both arms. A fixture
that changes underneath those designs destroys them.

### The option not taken, and it is what the market does

Every published generator — HouseGAN++, HouseDiffusion, Graph2Plan, WallPlan —
conditions on a **real boundary drawn from its dataset**. None fits a parametric
envelope generator. That is the honest external-validity arm and it is not
refused, only **not taken here**: building a corpus → rectilinear-Envelope
converter is `experiments/rectangularise/`'s subject matter, and that directory is
claimed by *The dwelling that is built on two angles*. Writing it from another
ticket is precisely the merge hazard that produced two pure-rework tickets on this
map already. It is charted as its own ticket instead.

## Consequences

1. **No published number moves, and none is re-run.** Parts I–III, ADR 0014 and
   ADR 0019 all stand at their published values on the published fixture.
2. **Two documents carry a stale-preset caveat rather than a re-run.**
   `solver-formulation.md` Part III ran half its grid at a `corpus_median` that
   has since moved from the corpus p3–p10 to p51 — ticket 29 closed 2026-08-25,
   the re-fit landed 2026-08-26. Exposure is held **fixed within each pair**, so it
   is a nuisance factor and the McNemar result is untouched; what moves is the
   population claim, and the pooled rates are **conservative**. The four
   `room-rectangles` sweeps are the same shape of case, at 3,5 h of machine time
   to re-measure a paired comparison under an easier nuisance factor.
3. **The frontage budget was inflated by up to 32 % and it cost nothing.**
   Phantom notch faces reached `exterior_faces()` and through it `frontage.py`.
   At twelve rooms `detached` read 68 000 mm of exterior run against a true
   46 000. **Zero cells change verdict** — H8's necessary condition was never
   close to binding.
4. **The six-room mystery is diagnosed and it was never frontage.**
   `probe_exposure`'s 0/5 at six rooms with 5 250 mm of slack is `assign_kinds`
   going INFEASIBLE for want of dissection cells that are *both* exterior-facing
   and large enough to host a habitable type — median **3** at
   `flat_single_aspect` against a requirement of **4**, which is fixed by
   `COMPOSITION` and does not grow with `n`. On the corpus fixture the six-room
   failure disappears and a seven-room one opens: **the hole moves, it does not
   close**, which is `probe_exposure`'s own headline confirmed on an
   independently-fitted family.
5. **The corpus fixture refuses n = 4, and that refusal is a finding.**
   `ground_truth` gives every Envelope part at least one room, so every part must
   be able to hold one — and a 40,4 m² dwelling cannot carry an articulated
   boundary *and* a 2,75 m `living` column at once. The published fixture serves
   n = 4 only because its single corner notch leaves two parts and buys no
   perimeter. This is a sharper statement of the map's standing *"no solver
   measurement covers the bottom half of C13's 3–10 band"*.
6. **`experiments/solver-toy/` is now shared by three concerns** — the published
   fixture, the corpus fixture, and whatever prices a new encoding against
   either. A ticket touching `envelope_for`, `CORPUS_ENVELOPES` or the face
   machinery is amending a settled shape rather than filling a gap.
7. **A trap that reads exactly like a fixture defect, and cost this ticket a
   whole sweep.** `clear_t` must equal the solver's `t_int_mm` whenever
   `erode_minima` is on — the solver binds minima on the *clear* rect, so a truth
   built at `clear_t = 0` satisfies them on the *solved* rect and stops being a
   witness. The first run of `fixture_delta.py` returned **OPTIMAL with 55
   interior cells unassigned at every seed and both exposures** on the corpus
   arm, which reads as *this Envelope cannot be tiled* and was one argument at
   one call site. It also **inverted the headline**: that run reported the two
   fixtures tied at McNemar p = 1,00, where the correct rig separates them at
   p = 0,0005. Part II.1 warns about it in prose; `sweep_ng.execute` threads
   `t_int` through and is the pattern to copy.

## What this does not decide

- **Whether the shipped 15 s and τ = 4 should be re-fitted on the corpus
  fixture.** `fixture_delta.py` prices the move; re-fitting the shipped
  configuration against it is a separate decision with C6 and the job budget in
  scope.
- **Sampling real Envelopes from the corpus.** Its own ticket, and it claims
  `experiments/rectangularise/`.
- **`EXPOSURE_PRESETS` becoming `n`-dependent.** Refused for now: the drift is
  caused by `envelope_for`, and making the presets `n`-dependent would hide an
  Envelope defect inside a preset. Measure on the corpus fixture first.
