---
id: 52
title: The toy Envelope is more compact than a real dwelling
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
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

## Resolution — the Envelope gains a corpus arm, the old one is frozen, and the correction is free (2026-08-28)

**ADR [0029](../../adr/0029-the-toy-envelope-gains-a-corpus-fitted-arm-and-the-published-one-is-frozen.md).**
Findings: `docs/research/solver-formulation.md` **Part IV**. Harness
`experiments/solver-toy/envelope_fit.py` and `fixture_delta.py`, rows in
`results/FIXTURE.jsonl`.

### Compact versus matched: **matched, as a second fixture, with the delta measured once**

Not a correction in place. Editing `envelope_for` retroactively moves the
substrate under **four closed decisions** — ADR 0014, ADR 0019, ticket 15's 15 s
and τ = 4, ticket 24's arrangement metric — and one ticket does not silently
invalidate four. `FIXTURE` defaults to `published`, bit-exact. The corpus family
is `fixture="corpus"`, and ADR 0029 makes it the one **every new measurement
uses**.

**It is not a tie, and the published fixture was handicapping the solver.**
140 solves, matched `(n, exposure, seed)`, shipped config verbatim:

| | survivors | p50 | p90 | no Brief |
|---|---:|---:|---:|---:|
| published | 48/70 — 68,6 % | 0,30 s | 1,26 s | 20 |
| **corpus** | 60/70 — **85,7 %** | 0,27 s | 1,28 s | 10 |

Paired: both 48, **only published 0**, only corpus 12, neither 10. Exact McNemar
**p = 0,0005**. **No slot** has the published fixture winning. **Time does not
move**, on an Envelope carrying +11,6 to +25,6 % floor and +25 to +32 % perimeter
— the same shape of result as ADR 0019's.

### The cause was never the notch share, and this ticket's headline row was the noise cell

⚠️ **Two corrections to this ticket's own evidence.**

1. **n = 12 must not be quoted.** That corpus cell holds **17** dwellings and its
   boundary runs **34,6 %** longer than its own bounding box against 11,8 % at
   eleven. In the well-sampled band (5–9, N = 291–480) the perimeter ratio is
   **0,91–0,97**, not the 0,68 the headline table implies. The defect is real and
   about a third the size claimed.
2. **Every notch this harness cuts is a corner notch, and a corner notch adds no
   perimeter at all.** `envelope_for(n)`'s true boundary is exactly `2 (W + H)` at
   every count. So no notch share and no notch *count* could ever have fixed it —
   matching the corpus with corner notches needs a share of **27–36 %** against a
   corpus **16–21 %**. `u_shape` builds ADR 0003's **T**, not its U.

**The fix is ADR 0003's missing shape.** A **mid-edge** notch adds exactly
`2 × depth` at zero area cost — `geometry.u_shape_true`. The two-notch budget is
split **by job**: corner notch removes floor, mid-edge notch buys perimeter.
Fitted on three targets — area, perimeter, bounding-box occupancy — one ring lands
within **0,7 %** of the corpus median at every count 5–11, with mid-edge depth
rising 5 → 12 grid units, tracking the corpus's own rising articulation.
⚠️ **Two targets are not enough**: on area and perimeter alone the fit buys the
boundary from a big bbox and carves the area back with a 31–35 % corner notch.
Every number lands and the shape is two thin arms.

### `AREA_PER_ROOM_M2`: **kept at 9.65**, and it was never a number to correct

It is the published fixture's own constant, and moving it moves every timing in
Parts I–III. The honest figures are per-count and live in the corpus fixture:
10,83–11,77 m² per room. This also prices 29's fixture defect — at n = 8 the
corpus gives **11,77**, which **clears** the 11,58 both cut structures need; at
n = 7 it gives 11,46, which does not. Part of "no pinwheel below 7 rooms" is the
fixture being too small and part is real.

### `exterior_fraction`: **fixed**, and the harmless half was not harmless

`all_faces()` now walks the real boundary; cross-checked against the independent
shapely implementation in `envelope-exposure/true_fraction.py` — 45 (count,
preset) pairs, **0 mismatches**. ⚠️ **The phantoms reached `frontage.py`'s H8
budget**, which every arithmetic-death table on this map was computed through: at
twelve rooms `detached` read **68 000 mm** of exterior run against a true
**46 000**, a numerator up to **32 %** too large. Re-checked at every cell:
**zero verdicts change.** H8's necessary condition was never close to binding.

### The two research documents: **re-worded, not re-run**, and the blast radius was wider than this ticket knew

⚠️ **ADR 0019 / Part III also ran half its grid at the stale `corpus_median`** —
29 closed 2026-08-25, the re-fit landed 2026-08-26. This ticket named only
`room-rectangles`. Exposure is held **fixed within each pair** in both studies, so
it is a nuisance factor and both McNemar results are untouched; what moves is the
*population claim*, and the pooled rates are **conservative**. The four
`room-rectangles` sweeps are the same case at 3,5 h of machine time. §II.2 is
rewritten whole — its preset table, its `vs corpus` column and its
arithmetic-death table were all wrong, and the death table is **overturned**: no
count in the band is arithmetically dead.

### The six-room mystery: diagnosed, and it was never frontage

`assign_kinds` goes INFEASIBLE for want of dissection cells that are **both**
exterior-facing and large enough to host a habitable type — median **3** at
`flat_single_aspect` against a requirement of **4**, which `COMPOSITION` fixes and
which **does not grow with `n`**. Upstream of any solve. Confirmed from the other
side: on the corpus fixture the six-room failure disappears and a seven-room one
opens. **The hole moves; it does not close** — `probe_exposure`'s own headline,
now on an independently-fitted family. 51's `kitchen.needs_window` lead is *not*
implicated: the binding count is composition, not the kitchen.

### The bottom of C13's band moves from "below 7" to "6"

On the corpus fixture **n = 5 builds and solves 10/10** at both exposures. The
map's standing *"no solver measurement covers the bottom half of the 3–10 band"*
is now **one named cell**, n = 6, failing in `assign_kinds` on both fixtures.
⚠️ **n = 4 is refused** by the corpus family, and the refusal is a finding: a
40,4 m² dwelling cannot carry an articulated boundary *and* a 2,75 m `living`
column at once, and `ground_truth` gives every part a room.

### The option not taken, and it is what the market does

Every published generator — HouseGAN++, HouseDiffusion, Graph2Plan, WallPlan —
conditions on a **real boundary from its dataset**; none fits a parametric
envelope generator. Refused here for one reason only: the conversion lives in
`experiments/rectangularise/`, which **46 holds**, and writing it blind is the
merge hazard that has already cost this map two pure-rework tickets. Charted as
[Every Envelope the solver has seen is invented](58-every-envelope-the-solver-has-seen-is-invented.md).

### ⚠️ A trap that cost this ticket a whole sweep and inverted its headline

`clear_t` **must** equal the solver's `t_int_mm` whenever `erode_minima` is on.
The solver binds minima on the *clear* rect; a truth built at `clear_t = 0`
satisfies them on the *solved* rect and stops being a witness, so the model can be
**provably** unable to tile its own Envelope. The first run of `fixture_delta.py`
returned **OPTIMAL with 55 interior cells unassigned at every seed and both
exposures**, which reads as a fixture defect, and reported the fixtures **tied at
p = 1,00** where the correct rig separates them at **p = 0,0005**. One argument at
one call site. Part II.1 warns in prose; `sweep_ng.execute` is the pattern.

### Declared on resolution

- `docs/adr/0029-…` — new.
- `docs/adr/0003-…` — **not edited**. Its shape family and two-notch cap are
  unchanged; what changed is that the generator now emits all four members.
- `experiments/envelope-exposure/README.md` — unclaimed; both handoffs it left
  are discharged in place rather than passed on again.
- `docs/research/solver-formulation.md` Part III — this ticket's file, so the
  stale-preset caveat belongs on it rather than on a new ticket.
