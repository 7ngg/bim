---
id: 52
title: The toy Envelope is more compact than a real dwelling
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: []
writes:
  - experiments/solver-toy/
  - docs/research/solver-formulation.md
  - experiments/room-rectangles/
  - docs/research/room-rectangles.md
---

# The toy Envelope is more compact than a real dwelling

## Question

**`envelope_for(n)` generates dwellings that are too small per room and too
compact, and the gap widens with room count.** Measured from the corpus side by
*The exposure presets were fitted to a measurement of one room*, which could not
fix it: `experiments/solver-toy/` is claimed, and the fix changes what the solver
is given rather than only what it is measured against.

Three defects, one cause, and they are cheapest to take together because each
invalidates the same numbers.

### 1. The Envelope is more compact than a real dwelling

Perimeter against interior area, toy versus the corpus median at the same room
count — 2,238 Swiss dwellings, `experiments/envelope-exposure/series/`:

| n | corpus area | corpus perim | corpus per/area | toy area | toy perim | **toy per/area** |
|---:|---:|---:|---:|---:|---:|---:|
| 4 | 40.4 | 30.2 | 0.747 | 38.7 | 26.0 | **0.672** |
| 8 | 94.1 | 47.6 | 0.505 | 75.0 | 36.0 | **0.480** |
| 10 | 109.0 | 52.4 | 0.481 | 97.6 | 41.5 | **0.425** |
| 12 | 117.4 | 67.1 | 0.572 | 118.0 | 46.0 | **0.390** |

`envelope_for` scales interior area linearly in `n` at a fixed aspect and a fixed
notch share, so its perimeter grows as the *root* of its area. A real dwelling
stays articulated instead. The consequence is measurable: exterior run per room
is **flat in the corpus** — median 3.97–4.41 m from four rooms to twelve — and
**falls** in the toy at every preset.

### 2. `AREA_PER_ROOM_M2` is 9.65 against a corpus median of 11.36 m²

*The solver has only ever seen guillotine layouts* left this as a fixture defect
with no number — "below what the placeholder table needs at 7 and 8 rooms in
**either** arm". Here is the number from the corpus side: real dwellings run
**11.36 m² per room** at the median, so the toy's dwellings are **15 % smaller
per room** than the population every conclusion is generalised to.

### 3. `Envelope.exterior_fraction` double-counts

`all_faces()` emits each bbox edge **in full** *and* all four faces of every
notch, so the stretch a corner notch removed is counted twice — once as part of
the bbox edge that no longer runs there, once as a phantom notch face on the same
line. At eight rooms the true perimeter is **144** grid units and `all_faces()`
counts **180**: a denominator 25 % too large.

```
('v', 40,  0, 32)   E edge in full — but y 24..32 was cut away by the notch
('v', 40, 24, 32)   the same stretch again, as a notch face
('h', 32,  0, 40)   N edge in full — but x 30..40 was cut away
('h', 32, 30, 40)   the same stretch again
```

The phantom faces reach `exterior_faces()` too, which the solver reads for H8.
**That half is harmless** — `Envelope.contains` forbids a room inside a notch, so
no room can be flush with the removed stretch and claim its daylight — which is
why this is a measurement defect rather than a live solver bug. A correct
implementation exists and is tested against the presets:
`experiments/envelope-exposure/true_fraction.py`.

## What this ticket has to decide

**Whether to make the Envelope match the corpus, or to keep it compact and
declare it.** Both are defensible and the choice is not obvious:

- Matching means `envelope_for(n)` gains articulation with `n` — more notch, or a
  worse aspect, or a third notch above some count — which touches ADR 0003's
  **two-notch cap**, and *The two-notch cap is now evidenced* has just measured
  that cap at the knee of its own ladder. A third notch cannot be added casually.
- Keeping it compact means every solver conclusion is measured on dwellings 15 %
  smaller per room and less articulated than the ones v1 will meet, and the
  drift below has to be quoted with every number taken off this harness.

## What is already known to move

⚠️ **`docs/research/solver-formulation.md`'s exposure section is wrong twice
over**, and this ticket holds that file:

- Its `vs corpus` column compares realised fractions against the **uncorrected**
  distribution. Every row is wrong: `detached` 1.00 is the corpus **p99** and not
  "above p95 — no real dwelling"; `terrace_mid` is **p41–p57**, not above p95;
  `corpus_median` is **p4–p10**, not "straddles the median"; `flat_single_aspect`
  is **p1**, not ~p25.
- Its `achieved fraction` column is computed with the double-counting
  `exterior_fraction`, so the numbers themselves are wrong before the comparison
  is.
- ⚠️ **Its arithmetic-death table is overturned.** "`flat_single_aspect` is
  arithmetically dead from 7 rooms, and no solver is involved" is false at the
  re-fitted preset — re-run with the same necessary condition and the same
  minima:

  | n | need | old had | **new has** | verdict |
  |---:|---:|---:|---:|---|
  | 6 | 8 500 | 9 000 | **13 750** | alive by 5 250 mm |
  | **7** | 10 500 | 9 500 | **14 500** | **alive by 4 000 mm** |
  | 8 | 10 500 | 10 000 | **15 250** | alive by 4 750 mm |
  | 12 | 14 500 | 13 000 | **29 000** | alive by 14 500 mm |

  `probe_exposure` agrees independently: `flat_single_aspect` now returns 5/5 at
  seven, nine and ten rooms. ⚠️ **But it still returns 0/5 at six**, with 5 250 mm
  of frontage slack — so that failure is **not** the frontage arithmetic, and
  whatever it is has never been identified. That is the live question this table
  leaves behind.

⚠️ **`experiments/room-rectangles/` ran four sweeps at `corpus_median`** —
`kind_rates.py`, `l_truth_check.py`, `sweep_designA.py`, `sweep_k2.py` — and both
its README and `docs/research/room-rectangles.md` quote results as holding "at
both `detached` and `corpus_median` exposure". `corpus_median` has moved from the
corpus p4–p10 to p51, which is most of the way to `detached`, so the two arms are
now **much closer together** and that phrasing may be reporting agreement between
two nearly-identical conditions. Re-run or re-word; do not leave it as it stands.

⚠️ Its "no feasible room-type assignment below 7 rooms" claim was also measured
at the old `corpus_median`, and the six-room row is exactly where `probe_exposure`
moved most.

## What does NOT move

`detached` is unchanged at 100 %, so **every timing measured at `detached` stands**,
which is most of the solver sweep. The headline that no real flat resembles the
fully-exposed geometry the 6.25 s-at-24-rooms timing assumed also survives — 1.1 %
of real dwellings sit at ≥ 0.99 exterior.

## Deliverable

A decision on compact-versus-matched with its reasoning, the `exterior_fraction`
double-count fixed or explicitly declined, `AREA_PER_ROOM_M2` resolved, and the
two research documents above either re-run or re-worded so neither publishes a
number measured at a preset that no longer exists.
