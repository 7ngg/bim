# Ergonomic minima — the hard floor, derived and then falsified

**Ticket:** *Ergonomic minima and the constraint table's missing half*
**Canonical data:** `data/standards/room-constraints.json`, key `ergonomic`
**Generator:** `experiments/region-profile/build_ergonomic_layer.py`
**Harnesses:** `experiments/region-profile/`, `experiments/solver-toy/ergonomic_minima_tiling.py`

*Acceptance validator spec* made this layer the **entire hard dimensional reject
set** of the acceptance bar: region-free, because bodies are, and the only thing
standing between a Plan and rejection in every region, including ones never
surveyed. It was missing. This authored it.

---

## 1. TL;DR

1. **A derived floor is not self-justifying, and the first honest derivation was
   wrong.** Composed from the published clearances the sources actually state, the
   bathroom floor lands at 4.0 m² — which **rejects 36 % of real, built, QA'd
   Swiss bathrooms**. The error was using **AD M's 750 mm**, which is a
   *wheelchair transfer space*, as though it were a body clearance. Private
   dwellings are not built to accessibility figures.
2. **The corpus low tail is real, not annotation debris.** Checked against the
   corpus's own fixture entities: **0 %** of `wc` rooms fail to hold a WC pan and
   **0.8 %** of `bathroom` rooms fail to hold a 1700 mm bath. There is no
   fragments escape hatch — those small rooms are homes.
3. **One free parameter, fitted and then found to be cited.** The whole table is
   fixture footprints plus `u`, the body zone that cannot be shared with another
   fixture's zone. Fitted so no room type rejects more than ~5 % of
   fixture-consistent real rooms, `u` lands on **300 mm** — which is also
   Neufert's stated minimum clearance from a WC pan's free side to a wall.
4. **ADR 0007 does not apply to this layer, and applying it costs ~10 points of
   corpus on the WC alone.** Rounding a published minimum *down* onto the grid
   lattice is sound for a **quoted** number and unsound for a **derived** one: a
   derived 1700 mm *is* the bath, and 1650 deletes 50 mm of bathtub.
5. **§8's directional/orientation-free distinction dissolves.** The rules are
   stated over the *shorter* and *longer* clear dimension, not over x and y, so no
   room type needs an axis binding — and once fixtures drive the rectangle, most
   types are non-square, not two.
6. **The `BATHROOM` corpus split does *not* fall out of the minima**, which is
   what the ticket assumed. Two floors are both floors. Fitted against fixture
   ground truth instead: **2.4 m²**, 5.9 % total misclassification against the
   3.6 m² the derivation suggested, which scores 23.3 %.

---

## 2. Method — derive, do not quote

Findings §7.6 item 12 requires re-derivation over transcription, and it is also
the strongest copyright posture available: the row set, the room programmes and
the arithmetic are ours, and no surveyed work's table is reproduced. §7.6 item 3
separately permits reproducing **AD M Volume 1 Appendix D** — a furniture and
fixture schedule published under the Open Government Licence — which is where
almost every footprint here comes from.

Every published value is

```
minimum  =  Σ fixture footprints  +  k · u
```

where `k` counts the body zones on that axis that **cannot be shared**. Sharing is
the load-bearing modelling rule: two fixtures used one at a time may share one
activity zone, but no fixture's zone may overlap another fixture's *footprint*.
The first derivation summed zones as though they were disjoint, and that is most
of why it came out too big.

### 2.1 Why `u` is not 750 mm

| Source | Figure | What it actually is |
|---|---|---|
| AD M M4(1) | 750 mm in front of the WC | **wheelchair transfer space** |
| AD M M4(2) ¶2.25 | 750 mm bed surround | Category 2 *accessible and adaptable* dwellings |
| AD M M4(3) ¶3.35 | 1000 mm, plus a 1200 × 1200 manoeuvring square | wheelchair dwellings |
| DIN 18040-2 | 1200 mm baseline / 1500 mm R | accessible building standard |
| Neufert (DIN 18025) | **≥300 mm** pan free side to wall | the one non-accessible side clearance stated anywhere |

Every clearance in the corpus of sources is an *accessibility* clearance, because
those are the numbers regulators write down. The ordinary private bathroom has no
regulator, and so no published clearance — which is precisely why §5.1 concluded
that the engine's room dimensions *have to be our own choices*.

So `u` is calibrated, not quoted, and the calibration target is the corpus.

---

## 3. The falsification test

*Rectangularising real rooms* settled the principle this rests on: every corpus
dwelling is a real, built, QA'd home, so **a hard rule that rejects them measures
what our model cannot express**, not what is wrong with the data. *Acceptance
validator spec* had already loosened two rules on exactly that reasoning.

`experiments/region-profile/ergonomic_floor_probe.py` measures, over 317,341
Swiss Dwellings residential rooms, the **minimum rotated rectangle** of each — the
axis-free analogue of the `(short, long)` pair we publish, and necessary because
*Rectangularising real rooms* found **0.0 %** of corpus rooms are rectangles in
the corpus's own geo-referenced coordinates, so a bounding box is not usable.

`BATHROOM` is split by **fixture**, not by area, so the classes are ground truth:

| room type | n | short p1 | short p5 | short p50 | long p1 | area p1 | area p50 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `bathroom` (has BATHTUB) | 40,747 | 1330 | 1481 | 1722 | 1717 | 2.56 | 4.17 |
| `shower_room` (SHOWER, no bath) | 10,850 | 835 | 1090 | 1671 | 1469 | 1.14 | 3.68 |
| `wc` (TOILET only) | 14,789 | 744 | 806 | 1099 | 1164 | 1.01 | 1.85 |
| `private` (ROOM/BEDROOM) | 105,437 | 2236 | 2421 | 3289 | 3316 | 8.65 | 14.28 |
| `kitchen` | 43,997 | 1266 | 1587 | 2387 | 2042 | 2.92 | 8.04 |
| `living` | 8,454 | 2969 | 3302 | 4014 | 3892 | 11.72 | 20.64 |
| `corridor` | 53,295 | 916 | 1111 | 2106 | 1279 | 1.22 | 7.52 |
| `storage` | 14,294 | 358 | 537 | 1201 | 658 | 0.26 | 2.17 |

Note **`long p1` for `bathroom` is 1717 mm**. That is the bath. The corpus
independently confirms AD M Appendix D's 1700 mm figure without being asked to.

### 3.1 The low tail is real

A room the corpus labels a bathroom *contains a bathtub entity*. If its rectangle
cannot hold the fixture, the polygon is debris — the finding *Solver timing
variance sweep* reached about three sub-0.02-exposure units. Measured:

| room type | must hold | cannot | share |
|---|---:|---:|---:|
| `bathroom` | 1700 (bath) | 340 | **0.8 %** |
| `shower_room` | 900 (tray) | 3 | 0.0 % |
| `wc` | 700 (pan) | 0 | **0.0 %** |
| `private` | 1900 (bed) | 0 | 0.0 % |
| `kitchen` | 1500 (sink + hob) | 42 | 0.1 % |

**There is no debris to discount.** Every subsequent figure is measured on the
fixture-consistent subset anyway.

### 3.2 Calibrating `u`

`experiments/region-profile/floor_calibration.py`, reject rate of the raw derived
floor against the fixture-consistent corpus:

| `u` | bathroom | dining | kitchen | living | private | shower_room | storage | **wc** |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 250 | 0.0 % | 0.6 % | 1.2 % | 0.0 % | 0.0 % | 2.8 % | 7.2 % | **1.3 %** |
| **300** | **0.0 %** | **0.6 %** | **1.2 %** | **0.0 %** | **0.0 %** | **3.7 %** | **7.8 %** | **4.6 %** |
| 400 | 0.1 % | 0.6 % | 1.2 % | 0.0 % | 0.0 % | 5.2 % | 9.2 % | 14.3 % |
| 600 | 0.7 % | 1.1 % | 1.6 % | 0.0 % | 0.1 % | 14.4 % | 14.8 % | 51.8 % |
| 750 *(AD M)* | ~2.4 % | ~1.5 % | ~2.1 % | 0.0 % | 0.2 % | ~20 % | ~20 % | **~66 %** |

The **WC is the binding room** and it is not close: it is where the entire real
distribution fits inside a span narrower than one grid step, so every millimetre
of clearance costs several points of corpus. `u = 300` is the knee.

That the fitted value **coincides with Neufert's published ≥300 mm** is
corroboration, not derivation — but §7.6 item 10 asks for exactly that: a number
that appears in two independent places is a fact about bodies.

---

## 4. The published table

Clear dimensions in mm, areas in m². `(short, long)`, never `(x, y)`.

| room type | short | long | area | hab | wet | priv | win |
|---|---:|---:|---:|:-:|:-:|:-:|:-:|
| `living` | 1850 | 2000 | 3.7 | ✓ | | | ✓ |
| `dining` | 1300 | 1500 | 1.9 | ✓ | | | ✓ |
| `living_dining` | 1850 | 3150 | 6.1 | ✓ | | | ✓ |
| `kitchen` | 900 | 2100 | 1.8 | | ✓ | | |
| `kitchen_dining` | 1300 | 2200 | 4.6 | ✓ | ✓ | | ✓ |
| `living_dining_kitchen` | 1850 | 4050 | 8.5 | ✓ | ✓ | | ✓ |
| `bedroom_principal` | 2100 | 2300 | 4.8 | ✓ | | ✓ | ✓ |
| `bedroom_double` | 1650 | 1900 | 3.1 | ✓ | | ✓ | ✓ |
| `bedroom_single` | 1200 | 1900 | 2.2 | ✓ | | ✓ | ✓ |
| `study` | 800 | 1050 | 0.8 | ✓ | | ✓ | ✓ |
| `bathroom` | 1000 | 1700 | 1.7 | | ✓ | ✓ | |
| `shower_room` | 1000 | 1400 | 1.4 | | ✓ | ✓ | |
| `wc` | 800 | 1000 | 0.8 | | ✓ | ✓ | |
| `utility` | 900 | 1500 | 1.3 | | ✓ | | |
| `hall` | 900 | 1138 | 1.0 | | | | |
| `entrance_lobby` | 900 | 1138 | 1.0 | | | | |
| `corridor` | 900 | 900 | 0.8 | | | | |
| `storage` | 600 | 900 | 0.5 | | | | |

`min_area` is `short × long` rounded **down** to 0.1 m². Rounded up it would
reject the very rectangle it was derived from. It still binds independently,
because a room can clear both sides and be long and thin — `dim.aspect_ratio_hard`
catches that separately.

**These are floors, not targets.** They sit far below what anyone builds: the
`living` floor is 3.7 m² against a corpus median of 20.6. That is correct and
deliberate. The hard set exists to reject the unbuildable; `dim.market_default_area`
and the AZ profile's tiered areas carry liveability, and C14 already guarantees a
region can change which Plans are *preferred* and never which are *rejected*.

### 4.1 Composite rooms are a permissive envelope

`living_dining`, `kitchen_dining` and `living_dining_kitchen` must hold two or
three programmes disjointly, and there is more than one way to pack them. A
`(short, long)` pair **cannot express "contains packing A *or* packing B"**. So we
publish the smallest short, the smallest long and the smallest area over all
packings — which under-rejects and never over-rejects. For a hard floor that is
the correct error direction.

### 4.2 The four flags now exist as data

`is_habitable`, `is_wet`, `is_private` and `needs_window` were defined in
`flag_semantics` and tabulated only as **prose in findings §8**, while four
registry rules consume them. A flag the registry cannot read is a predicate that
silently does not fire — the same failure as a missing minimum. They are now
published per room type, and each consuming rule carries a `flag_source` pointer.

**One correction to §8:** it sets `study` `is_private: false`. `CONTEXT.md`
defines the Private room class as *"a Brief's bedroom, study or nursery, as one
class"*, and the Proposer spec collapses `{ROOM, BEDROOM, STUDIO}` to `PRIVATE` on
the same reasoning. A study that is a thoroughfare to another room is not a study.
Set **true**; §8 predates the glossary entry.

---

## 5. ADR 0007 does not bind on a derived minimum

ADR 0007 requires every published minimum to satisfy `minimum + t_int ≡ 0
(mod grid)`, and its worked example rounds **down**: *"a source specifying a
1750 mm kitchen is honoured by publishing 1650 mm clear."*

That reasoning is a **unit conversion**, and it is sound: the source's 1750 was a
nominal or centreline figure, so subtracting `t_int` recovers what an occupant can
tape. It is exactly ADR 0004's move.

**It has no counterpart for a derived minimum.** These numbers are clear by
construction — sums of footprints and clearances, all measured in clear space.
There is no centreline to subtract. A derived 1700 mm *is* the bath. Rounding it
down to 1650 does not honour a convention; it deletes 50 mm of bathtub and
publishes a bathroom floor that provably cannot hold the fixture that defines the
room.

So the ergonomic layer can only round **up** — and rounding up is arithmetically
*identical* to leaving the minimum unaligned, because
`grid·⌈(m+t)/grid⌉` is the same either way. That is the row ADR 0007 measured as
fatal.

### 5.1 What it costs, measured

Snapping this layer onto the 250 mm lattice (`t_int = 100`, so 650 / 900 / 1150 /
1400 / 1650 / 1900 …):

| room type | raw | reject | grid 250 | reject | grid 125 | reject | grid 50 | reject |
|---|---|---:|---|---:|---|---:|---|---:|
| `wc` | 950×1150 | 23.0 % | 1150×1150 | **56.1 %** | 1025×1150 | 38.1 % | 950×1150 | 23.0 % |
| `bathroom` | 1150×1700 | 0.1 % | 1150×1900 | 2.8 % | 1150×1775 | 0.6 % | 1150×1700 | 0.1 % |
| `kitchen` | 1050×2100 | 1.2 % | 1150×2150 | 1.6 % | 1150×2150 | 1.6 % | 1050×2100 | 1.2 % |

*(measured at `u = 450`, which exaggerates the WC's absolute rate; the relative
cost of the grid is the point, and at the shipped `u = 300` it is ≈ 10 points.)*

The WC's entire real width distribution — p1 744 to p50 1099 — **spans less than
two grid steps**, so one snap moves the floor across most of the population.

### 5.2 And the deletion ADR 0007 feared does not reproduce at this magnitude

ADR 0007 measured its 4-, 5- and 6-room deletion against the **placeholder** table
(`living` 2750 mm / 12.0 m², `bedroom` 2000 mm / 7.0 m²). The derived floor is
roughly half that. `experiments/solver-toy/ergonomic_minima_tiling.py`, 8 seeds,
exact tiling at 9.65 m² per room:

| reading | n=4 | n=5 | n=6 | n=7 | n=8 | n=10 | n=12 |
|---|---|---|---|---|---|---|---|
| placeholder, minima on solved rect | 8/8 | 7/8 | 7/8 | 6/8 | 7/8 | 7/8 | 6/8 |
| placeholder, clear rect, **unaligned** | **0/8\*** | **0/8\*** | **0/8\*** | 6/8 | 7/8 | 7/8 | 6/8 |
| derived floor, minima on solved rect | 8/8 | 8/8 | 0/8\* | 7/8 | 8/8 | 7/8 | 8/8 |
| derived floor, clear rect, **unaligned** | **8/8** | **0/8** | 0/8\* | 7/8 | 7/8 | 8/8 | 8/8 |

`*` marks seeds where no Brief could be built at all.

**Row 2 reproduces ADR 0007 cleanly and unambiguously.** The deletion is real.

**Row 3 carries an anomaly, and row 4 must be read against row 3, not row 1.** The
derived table fails at n = 6 under the *baseline* reading, where the congruence
question does not arise at all — so that cell is a property of the harness's Brief
generator meeting much smaller minima (`scenarios.area_targets` sizes room targets
from the standards table and `assign_kinds` types the ground truth against it, and
both behave differently when nearly every kind fits nearly every rectangle). It is
**not** evidence about the grid, and n = 6 is simply not assessable here.

**Row 4 is a mixed result, and it does not say what an earlier draft of this
document expected it to say.**

| n | placeholder, unaligned | derived, baseline | derived, unaligned | reading |
|---|---|---|---|---|
| 4 | 0/8\* | 8/8 | **8/8** | **recovered outright** |
| 5 | 0/8\* | 8/8 | **0/8** | **still lost entirely** |
| 6 | 0/8\* | 0/8\* | 0/8\* | not assessable — baseline broken |
| 7–12 | 6–7/8 | 7–8/8 | 7–8/8 | no cost |

So the deletion is **narrowed, not removed**: from `{4, 5, 6}` down to `{5, and 6
unknown}`. At n = 5 the Briefs are constructible — no asterisk — and no valid
tiling is found. The magnitude hypothesis is therefore **half right**: halving the
minima buys back the 4-room case and does not buy back the 5-room case.

**This is a real cost of the exemption and it is reported as one.** ADR 0009 stands
on the argument that a derived minimum has no nominal-to-clear conversion to apply
— ADR 0007's remedy is simply unavailable to this layer, whatever the tiling counts
say, and the alternative is publishing a bathroom floor that cannot hold a bath.
But the corroboration this section was expected to supply is **mixed, not
supportive**, and the honest consequence is that *whether the solve grid should be
finer than 250 mm* gains a measured cost of staying: a 50 mm grid would make the
congruence vacuous, and the 5-room case is currently paying for the 250 mm one.
Note the affected band is the bottom of C13's promised 4–10 rooms and the commonest
dwelling size in the corpus.

**Decision, taken with the map's owner:** the ergonomic layer is **exempt from
ADR 0007** and publishes millimetre-precise derived minima; ADR 0007 continues to
bind on the **region profile**, whose numbers are quoted and therefore convertible.
The v1 solve grid stays at 250 mm, which preserves every timing *Solver timing
variance sweep* fitted there — the 15 s limit, τ = 4, the two-worker floor. The
alternatives considered were a 50 mm grid (makes the congruence vacuous and every
derived minimum exactly representable, at the cost of re-measuring every solver
number on the map) and a 125 mm grid (halves the loss, still leaves the 1700 mm
bath unrepresentable at 1775).

---

## 6. The `BATHROOM` split — the ticket's premise, refuted

*What the model proposes* handed this ticket the split with a stated rationale:
the threshold is *"the boundary between two rooms' minima"* and so *"falls out of
the table rather than being added to it"*.

**Measured, that is wrong, and it is wrong structurally.** Two floors are both
floors: `wc` is 0.8 m² and `shower_room` 1.4 m². The classes do not differ in
their minima — they differ in their **distributions**, `wc` at a median 1.85 m²
and `bathroom` at 4.17. A splitter cannot be recovered from the bottom of two
overlapping distributions.

It does not have to be invented either. Swiss Dwellings carries `BATHTUB`,
`SHOWER` and `TOILET` feature entities, so **which rooms really are bathrooms is
known**. Fitted over 66,386 fixture-labelled rooms
(`experiments/region-profile/bathroom_fixture_split.py`):

| threshold | bathrooms → wc | wcs → bathroom | total |
|---:|---:|---:|---:|
| 2.0 m² | 0.5 % | 8.7 % | 9.2 % |
| **2.4 m²** | **1.5 %** | **4.4 %** | **5.9 %** |
| 2.45 m² *(measured optimum)* | 1.8 % | 4.1 % | 5.8 % |
| 3.0 m² | 6.4 % | 2.2 % | 8.6 % |
| 3.6 m² *(derived candidate)* | 22.1 % | 1.2 % | **23.3 %** |
| 4.0 m² *(derived candidate)* | 36.0 % | 0.8 % | **36.9 %** |

**Published: 2.4 m².** The curve is flat at the optimum and the round number is
honest about the precision. Adding the long side as a second test buys nothing —
the best two-term rule collapses back onto the area term.

**Direction of error.** It prefers to over-assign to `bathroom`, about three to
one. That is the tolerable direction: an over-large `wc` wastes floor and breaks
nothing, while a `bathroom` that is really a WC arrives with too little room for a
bath — but it is still a real built Swiss room, still clears the 1.7 m² bathroom
floor, and so yields a small bathroom rather than an invalid Plan. Neither error
moves a published minimum, because **no minimum in this file is fitted to the
corpus** — the corpus only ever falsifies.

Note the ticket's own framing of the direction (*"too high and real WCs are
relabelled as undersized bathrooms"*) inverts the mapping; above the threshold is
`bathroom`, so a threshold set too high moves real **bathrooms** into the WC class.

---

## 7. Weakest cells, and what is still owed

- **`study` is the weakest number in the file.** A one-desk programme, no corpus
  label to falsify it against, and no surveyed source states a study minimum.
- **`utility`, `hall`, `entrance_lobby`** — likewise unfalsified; Swiss Dwellings'
  `WASH_AND_DRY_ROOM` and `CORRIDORS_AND_HALLS` are almost entirely non-residential.
- **`storage` rejects 7.8 %**, the worst rate published. Its low tail is genuinely
  tiny — p1 is 358 × 658 mm — and those are built-in cupboards, which the NDSS
  treats as built-in storage rather than as rooms. Left as is and flagged.
- **The AZ profile uses a different room-key vocabulary** (`living_room_1room_flat`,
  `living_room_2plus`) from the ergonomic layer's (`living`, `bedroom_double`, …).
  Both now live in the same document with no mapping between them. Ordering is
  consistent — AZ's `living` statutory floor of 15.0 m² sits far above the
  ergonomic 3.7 — so nothing contradicts, but a Plan cannot resolve one from the
  other. **Not fixed here**: it is *The Azerbaijani region profile*'s vocabulary.
- **The US profile bullet is discharged, not answered.** *Which region profiles
  ship in v1* deleted `US` outright, so §10 gap 1 no longer blocks anything.

---

## 8. Corrections to earlier documents

| Document | Correction |
|---|---|
| findings §8 | The `DE`/`market_default` table is superseded, not amended: `DE` is deleted and every hard floor now comes from the region-free ergonomic layer. |
| findings §8 | The directional/orientation-free split (`bathroom` and `wc` directional, the rest not) **does not survive**. The rules are stated over shorter/longer, so no type needs an axis binding, and most types are non-square. |
| findings §8 | `study` `is_private` is **true**, per `CONTEXT.md`'s Private room class. |
| findings §5.1 | *"We therefore set `min_width = min_depth` and mark the room `orientation_free: true`"* — withdrawn, same reason. |
| `rules.json` `dim.min_clear_depth` | Its note's directional claim is withdrawn in place. |
| `rules.json` `win.area_ratio` | `de_baybo`, the dangling source key this ticket was asked to close, was closed **concurrently and better** by *The Azerbaijani region profile*: it re-sourced both consumers to AzDTN 2.7-2 rather than adding the missing BayBO block. That also caught what adding the block would have hidden — **AZ requires the kitchen window where Bayern permitted its absence**, so the BayBO reading was inverted, not merely absent. Nothing cites `de_baybo` now and no block was added. |
| ADR 0007 | Scope narrowed: it binds on **quoted** region-profile minima, not on derived ones. |
| *What the model proposes* §4.2 | The split threshold does not fall out of the minima; it is fitted to fixture ground truth. |
