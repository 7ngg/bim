---
id: 26
title: H8 and the single-aspect flat
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: [19]
writes:
  - data/acceptance/rules.json
  - docs/spec/acceptance-bar.md
---

# H8 and the single-aspect flat

## Question

**Acceptance rule H8 — every habitable room touches an exterior wall over a
window's width — forbids the single-aspect flat above six rooms, and no amount of
solver, seed, τ or time limit changes that.** Decide what v1 does about it.

*Solver timing variance sweep* proved it arithmetically rather than
observing it. Habitable rooms do not overlap, so the stretches of exterior wall
they occupy are disjoint, and each consumes at least its own shorter minimum
dimension. That gives a necessary condition with no search in it:

```
sum over habitable rooms of min(min_w, min_h)   <=   total exterior run
```

| rooms | habitable | need (mm) | one exterior edge gives | verdict |
|---:|---:|---:|---:|---|
| 6 | 4 | 8 500 | 9 000 | ok, 500 mm slack |
| **7** | 5 | 10 500 | 9 500 | **dead by 1 000 mm** |
| 8 | 5 | 10 500 | 10 000 | dead |
| 12 | 7 | 14 500 | 13 000 | dead |
| 24 | 14 | 28 250 | 18 000 | dead by 10 250 |

`experiments/solver-toy/frontage.py`. The numbers are from the placeholder
standards table, which is why this is blocked on *Ergonomic minima and the
constraint table's missing half* — the real minima move the threshold, but they
cannot move it far, because the arithmetic is dominated by *how many* habitable
rooms a Brief names, not by 100 mm here or there.

**This is not an exotic case.** *Acquire the datasets* measured the exposure
distribution over 569 real Swiss dwellings: p25 is **0.23**, which is what
`flat_single_aspect` models. Roughly a quarter of real flats have this little
frontage, and the median dwelling holds 6.8 rooms — so the failing region is
adjacent to the corpus centre, not out in a tail.

The decision is not obviously any of these, and that is why it is a ticket:

1. **Relax H8 by room type.** A kitchen or a study on an internal wall is common
   and legal in much of the world; a bedroom without a window generally is not.
   H8 currently treats all five habitable types identically. Which types actually
   require frontage, and does that come from the same source as the minima?
2. **Relax H8 by count rather than by type** — e.g. every *bedroom* plus the
   living room needs frontage, the rest may borrow. This is closer to how the
   regulations that do exist are written.
3. **Bound the promise instead.** State that single-aspect dwellings above N rooms
   are out of v1's envelope, the way *The room-count envelope v1 promises* bounds
   the count. Cheap and honest, but it declines the corpus p25.
4. **Let the Envelope absorb it.** A single-aspect flat with 7+ rooms in the real
   world usually has a re-entrant light well — which ADR 0003's notch model can
   already express, and which *does* add exterior run. Whether real single-aspect
   flats solve the problem this way is measurable in Swiss Dwellings and nobody
   has looked.

Note the interaction with *Acceptance validator spec*, which made the hard rule
set **region-free** on purpose: whatever is decided here changes what is
*rejected*, so it cannot be pushed into a region profile without reopening that.

Also note what this ticket is **not**. *Solver timing variance sweep* closed the
adjacent rider: the three Swiss dwellings measuring ~0.00 exterior are annotation
fragments (6 rooms in 14.1 m²), not windowless homes, so H8 is not rejecting homes
that exist. The problem is specifically the 7-plus-room single-aspect flat, which
is real and which H8 forbids.

Deliverable: a decision recorded against `data/acceptance/rules.json`'s H8 entry
and `docs/spec/acceptance-bar.md`, plus whatever the Envelope model owes if
option 4 wins.

## A gap left open by *Rectangularising real rooms*

The corpus conversion (ADR 0008) preserves every real adjacency and every
separation direction, and it says **nothing about H8**. The fit does not know
which Envelope edges are exterior and which are party, so what it measured is
**boundary contact** — did a room that touched the Envelope's edge still touch it —
not window frontage. A room can keep its boundary run and have kept the *party*
side of it.

So: **whether the converted corpus still satisfies H8 is unverified**, and this
ticket should not assume it does. That matters here specifically, because
`flat_single_aspect` is arithmetically dead from 7 rooms and the corpus p25 is
0.23 exterior — if the conversion quietly moves habitable rooms off the exterior
run, the corpus will look worse against H8 than the real dwellings are, and the
fix would be aimed at the wrong thing.

The exposure machinery to close this already exists:
`experiments/corpus-smoke/exposure_swiss_dwellings.py` recovers the per-dwelling
exterior/party ring from the building hierarchy (*Acquire the datasets* §1.5,
150 floors, 569 dwellings). Joining it to the converted tiling is the measurement.

---

## Handed here by *Whether a Room may be more than one rectangle* (2026-08-23)

**ADR [0014](../../adr/0014-a-room-is-one-or-two-rectangles-and-the-proposal-decides.md)
moves H8's arithmetic, and you should decide whether you want the relief.**

At one rectangle per Room, a habitable Room touching the facade occupies its
**full width** there, so a single-aspect flat's habitable count is bounded by the
facade length divided by the rooms' own widths. That is the mechanism behind
`flat_single_aspect` being arithmetically dead from 7 rooms.

At two, a Room can present a **leg** at the facade and be wide inland. The leg
floor is 900 mm (`acceptance-bar.md` §9.1) against a `window_min` of 1000 mm, so
the binding number becomes `window_min` per habitable Room rather than that
Room's width — and more habitable Rooms fit on one facade than the old
arithmetic allows.

**Do not take this as good news without deciding it is.** A habitable room whose
only daylight comes down a 1000 mm-wide leg is an alcove with a window, not a
room with an aspect, and H8 exists to catch exactly the plan that passes on
paper and fails on being lived in. Three options, and this ticket owns the
choice:

1. Let H8 bind per Room, as now. The relief is real and single-aspect flats
   become feasible further up the band.
2. Bind H8 on the **part that carries the window**, requiring that part to meet
   the Room's own minimum width — so an alcove cannot stand in for an aspect.
3. Bind H8 per Room but add a soft rule on the ratio of window-bearing width to
   Room width, so the alcove case is scored rather than rejected.

The measurement that would decide it is the same single-aspect arithmetic
already in this ticket, re-run with a leg allowed. Whatever is chosen, the H8
predicate's row in `rules.json` needs a line saying **which part it binds**,
because §9.1 now makes that a question every dimensional rule has to answer.

---

## Handed in by *Homeowner product surface*

**"Dead from 7 rooms" is confounded with the envelope that 7 rooms selects.**

Measured while re-solving the *Homeowner product surface* prototype's layouts at
corpus-median exposure. The probes outlived the prototype and are on `master` at
**`experiments/envelope-exposure/`** (the prototype itself stays on its branch);
they import `solver-toy` and never edit it, since that directory is yours.
Five seeds per cell; the cell counts how many
produced a **Brief** at all — `make_brief`'s CP-SAT type assignment, which must
satisfy H8 together with wet clustering and circulation. It is upstream of the
solve, so this is not a timing result.

| n | detached | terrace_mid | flat_corner | corpus_median | flat_single_aspect |
|---|---|---|---|---|---|
| 4 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| 5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| **6** | 5/5 | 3/5 | 3/5 | **0/5** | **0/5** |
| 7 | 5/5 | 5/5 | 5/5 | 5/5 | 0/5 |
| 8 | 5/5 | 5/5 | 5/5 | 5/5 | 0/5 |
| 9 | 5/5 | 5/5 | 5/5 | 5/5 | 1/5 |
| **10** | 5/5 | 5/5 | 5/5 | 5/5 | **5/5** |

**The failure is not monotone in n, which is the finding.** `flat_single_aspect`
fails at 6, 7 and 8, mostly fails at 9, and then **succeeds at 10** — and n = 10
is where `envelope_for` switches from an **L to a U**, whose second notch adds
exterior run on the one live edge. So the quantity that binds is *how much
exterior run the envelope offers*, and `envelope_for(n)` varies that
non-monotonically. Any statement of the form "dead from n rooms" is measuring
the envelope n happens to select, not n.

**Two things this ticket should not take at face value from it:**

- ⚠️ **n = 6 fails at corpus median too**, not only at single aspect — and
  corpus median is *the case a spec should quote as typical*
  (`geometry.py`'s own comment). That is worse than the map's framing, which
  files H8 as a single-aspect problem.
- ⚠️ **This is the toy's generator, not the shipped ergonomic layer** — the same
  caveat *Whether a Room may be more than one rectangle* attached to its own
  sub-7-room finding. It corroborates a direction and settles no number.

**And it hands you a second-order consequence with a number on it.** Holding the
envelope *geometry* identical and varying only the edge ring's typing,
`probe_diversity.py` measures how different six survivors of **one** Brief are —
mean pairwise fraction of floor cells whose room kind differs:

| n | detached | corpus_median | ratio |
|---|---|---|---|
| 5 | 0.522 (0.512–0.531) | 0.282 (0.267–0.293) | **0.54×** |
| 7 | 0.749 (0.731–0.782) | 0.549 (0.542–0.558) | **0.73×** |

⚠️ **Quote the ratio, never a single figure.** `SolveConfig` defaults to
`workers = 8` and stops on wall-clock, and multi-worker CP-SAT is not
reproducible under a wall-clock deadline even with a fixed `random_seed` — two
runs of a single-pass version returned **0.283 and 0.263** for one cell. Three
repeats, range reported. The two exposures' ranges do not overlap at either room
count, so the gap is solid and the third decimal is not.

H8 pins habitable rooms to the exterior run, so the fewer exterior edges, the
fewer arrangements are distinguishable. See the *Variant generation and ranking*
patch — this is a **second, independent** cause of the flat-versus-house
diversity gap that patch records, and the aspect-ratio axis it proposes does not
touch it.

---

## Handed here by *Look at the converted corpus* (2026-08-25)

**H8's geometric half arrives from the corpus side, and it is not zero.** ADR
[0017](../../adr/0017-three-of-the-conversions-fidelity-headlines-are-constraints-restated.md),
failure mode 3.

A room that faced the outside in Swiss Dwellings and does **not** after
conversion: **579 of 14,200 façade-facing rooms (4.1 %)**, spread over **521 of
2,317 dwellings (22.5 %)** — 469 dwellings lose one room's frontage, 46 lose two,
6 lose three.

**This is the only fidelity number in the conversion that nothing constrains.**
Contact, separation relations and the area band are all posted *hard*, so their
zeros measure the constraint rather than the conversion; `boundary_lost` is
posted nowhere and is therefore a real measurement. It is also, per ADR 0017, one
of only four numbers on the conversion that can honestly be quoted as evidence.

**Why it lands on H8.** A Proposer trained on this corpus will sometimes propose
an arrangement in which a habitable room has no façade — an interior bedroom the
corpus did not contain, manufactured by squaring. If H8 is a hard rule, it will
fire on arrangements the corpus never actually contained, and the Proposer will
have been taught to produce them. That is a different problem from a
single-aspect flat and it needs to be told apart from one.

⚠️ **`boundary_lost` is contact with the Envelope boundary, not window
frontage.** `fit_rects` knows nothing about which Envelope edges are exterior and
which are party walls — ADR 0003 types them, the fit does not read the type. So
4.1 % is an **upper bound on lost daylight and a lower bound on nothing**: a room
that lost contact with a party edge lost no window. Whoever takes this must
decide whether the number needs re-measuring against typed edges before H8 can
lean on it.

---

## Resolution

**H8 is not relaxed, not typed, not counted and not bounded — because the crisis
it was opened for does not exist.** Both numbers that produced *"the single-aspect
flat is arithmetically dead from 7 rooms"* were wrong, in the same direction, and
correcting either one alone would have been enough. What the correction uncovered
instead is a different rule failing against real dwellings at 43.3 %, and a
measurement defect with a blast radius well outside this ticket.

Written: `docs/spec/acceptance-bar.md` §3 and §7 (rewritten),
`data/acceptance/rules.json` (38 → **36** rules). **Declared on resolution**
rather than taken quietly, none having a claimant:
`experiments/corpus-smoke/exposure_swiss_dwellings.py` (corrected),
`docs/research/dataset-inventory.md` §1.5 (corrected),
`experiments/region-profile/ergonomic_check.py` (one retired-rule gate removed;
219 checks still pass, `gate_check.py`'s 229 still pass, `env_check.py`'s 28 still
pass), `docs/spec/brief.md` (one stale rule count), and
**`experiments/h8-frontage/` (new)** — the three probes every number below comes
from, with a README recording what each one settles.

### 1. The frontage table was built on placeholders, and the real minima moved it nine rooms

`experiments/solver-toy/scenarios.py` says so in its own comment: *"Placeholders
pending ticket 05 … the point here is the shape of the constraint, not the
number."* Its bedroom is 2000 mm and its living room 2750; the shipped ergonomic
layer is `bedroom_double` **1650** (realisable 1850, ADR 0007/0009) and `living`
**1850**. Re-run against the shipped layer, with the kitchen's frontage included
as `openings.md` §6.2 asked:

| n | window-needing | need, placeholder | need, **shipped** | single-aspect has | verdict |
|---:|---:|---:|---:|---:|---|
| 6 | 4 | 8 500 | 6 650 | 9 000 | ok |
| **7** | 5 | 10 500 | **8 500** | 9 500 | **ok, +1 000** |
| 8 | 5 | 10 500 | 8 500 | 10 000 | ok |
| 12 | 7 | 14 500 | 10 700 | 13 000 | ok |
| 14 | 8 | 16 500 | 12 550 | 13 750 | ok |
| **16** | 10 | 20 250 | 15 250 | 14 750 | first DEAD |

The first arithmetically dead cell moves **7 → 16 rooms**, outside C13's 3–10
engine band. This ticket predicted the opposite — *"the real minima move the
threshold, but they cannot move it far … not 100 mm here or there"* — on the
reasoning that the sum is dominated by habitable **count**. The reasoning is sound
and the premise was wrong: the placeholders ran 20–48 % high per room, and across
five rooms that is 2 000 mm, which is exactly the deficit being explained.

### 2. `exposure_swiss_dwellings.py` never measured a dwelling

A dwelling's `area` polygons are **disjoint** — the wall sits between them — so
`unary_union(polys)` is always a `MultiPolygon`, and `max(geoms, key=area)`
reduced each dwelling to its **largest single room**. Most of that room's
perimeter faces other rooms *of the same dwelling*, which are in `occupied` and
therefore scored as party. Same sample, same seed, wall gap bridged before the
union:

| | published | **corrected** |
|---|---|---|
| p5 / p25 | 0.16 / 0.23 | **0.33 / 0.51** |
| **median** | **0.37** | **0.67** |
| p75 / p95 | 0.47 / 0.59 | **0.78 / 0.89** |
| ≥0.99 | 0 of 569 | 5 of 569 |
| median area of the thing measured | **23.9 m²** | 75.3 m² |
| median exterior run | 8.1 m | **27.5 m** |

The 23.9 m² median is the tell — that is a large room, not a Swiss flat. The
bridge distance is **not** load-bearing: p25/median/p75 are 0.51/0.67/0.78 at
0.12 m and move by at most 0.01 anywhere in 0.10–0.30 m; only 0.06 m, below a
wall's half thickness, fails to bridge and differs.

The script and `dataset-inventory.md` §1.5 are corrected here because both are
unclaimed and leaving a known-false measurement in the repo is not a thing to hand
on. **The consequences are not corrected here** and are ticketed as *The exposure
presets were fitted to a measurement of one room*: `flat_single_aspect` was fitted
to a p25 of 0.23 against a real **0.51**, and `corpus_median` — `geometry.py`'s own
*"the case a spec should quote as typical"* — to 0.37 against a real **0.67**,
which is two full edges, a **dual-aspect** flat. Everything measured at either
preset was measured at roughly half the real exposure, and the presets live in
`experiments/solver-toy/`, which *What an ordered entry sequence costs the solver*
holds.

✅ One published finding **survives**: no real flat resembles the fully-exposed
geometry the 6.25 s-at-24-rooms timing assumed — 0.9 % at ≥0.99.

### 3. Two rules retired, because neither could fire

`win.habitable_touches_exterior` keys on `is_habitable` and
`win.habitable_has_window` keys on `needs_window`. **No row of the 18-type table
carries the first without the second**, and `has_window` requires the window on a
segment whose Envelope edge **condition** is `exterior` — so touching the exterior
was strictly implied. Measured on 561 real dwellings it rejects 11.9 % against
`has_window`'s 43.3 %, and its rejections are a subset.

`win.kitchen_windowless` goes with it, on the handoff *Opening placement rules*
§10 left for *"whichever next holds `acceptance-bar.md`"* — that is this ticket.
Once `kitchen.needs_window` became `true` the warn was unreachable.

Both are moved to a `retired` block in `rules.json` with their statements and the
reasoning, not deleted. **36 rules, 37 with `dim.leg_join`; 28 hard, was 29.** The
`both` subset holds at 14 — see §4.

The invariant `touches_exterior` looked like it protected is a property of the
**table**, not of a Plan, and `ergonomic_check.py` already asserts it directly
(*"needs_window follows is_habitable"*). That gate is where it belongs: a rule can
only be exercised by a Plan that violates it, and no Plan can violate this one.

### 4. `win.habitable_has_window` takes the solver posting, and takes it stronger

Site moves `validator` → **`both`**. The retired rule posted mere exterior contact;
what the solver posts now is **the frontage budget itself** — each `needs_window`
Room holds a run of `exterior`-condition edge of at least its catalogue window's
structural width plus twice the 100 mm jamb return. 1 400 mm for a bedroom, 1 700
for a living room, 1 100 for a kitchen.

No new machinery: ADR 0003 types the edge ring before the solve and
`open.fits_segment` already carries the jamb constant. Posting anything weaker
generates candidates that cannot seat their windows, solves them, and throws them
away at validation — yield spent on a constraint the solver could already express.

### 5. The ADR 0014 alcove: option 2, and it is free today

Of the three readings *Whether a Room may be more than one rectangle* handed here,
**option 2**: the rule binds **per Room** for the requirement — a Room reaches its
window through any part — and **per part** for the part that carries the window,
which must meet that Room's own `min_clear_short`. At one rectangle per Room this
costs nothing; it is taken now because the alcove is cheap to prevent and
expensive to discover. `open.fits_segment` already forces a window-bearing leg to
1 400 mm for a bedroom; the Room's own published minimum is the number an
architect holds, and it invents no constant.

### 6. What the corpus actually says, and it is the kitchen

First per-room measurement of these rules against real dwellings — 561 dwellings,
2 169 window-needing rooms, corrected envelopes:

| | no window on own boundary | no exterior run |
|---|---|---|
| BEDROOM | **5.9 %** | 2.2 % |
| ROOM | 6.9 % | 1.5 % |
| LIVING_DINING | 9.0 % | 0.0 % |
| LIVING_ROOM | 20.0 % | 3.8 % |
| **KITCHEN** | **31.0 %** | 9.7 % |

**`win.habitable_has_window` rejects 43.3 % of real Swiss dwellings** — 23.0 % on
the kitchen **alone**, 20.3 % on a non-kitchen room. *What a room's area is allowed
to be* refused a p95 cap at 26.6 % on the argument that *"the corpus is the
retrieval and training population, so a rejection there is coverage lost"*. This is
worse, and unlike a percentile it **carries no threshold to move**.

The number is not an artefact. Attribution audit: **zero orphan windows** — every
boundary window attributed to at least one room — and 1 031 of 3 179 attributed to
more than one, which biases *toward* finding a window. The windowless kitchens are
not niches: median **6.8 m²**, and **84.7 % adjoin a windowed habitable room** —
borrowed daylight, the `taxca-metbex` arrangement AzDTN names and
`profiles.AZ.windows.kitchen_niche_windowless` deliberately holds `false`.

So the ticket's option 1 — *relax by type* — had an evidence base after all, and it
pointed at a type nobody named. **It is still refused**: AzDTN 2.7-2 cl. 9.12 is
`verified` and mandatory, corroborated at 2.7-3 cl. 8.14, and a Baku flat with a
windowless kitchen is not sellable. The cost is corpus coverage, and it is ticketed
as *A third of real kitchens have no window and the engine may not draw one* — a
retrieval and conversion question, not a licence to weaken a statutory rule.

### 7. What this ticket refused to fix from here

⚠️ **The hard bar admits a 1.85 × 1.68 m "double bedroom".** `bedroom_double`'s
`min_clear_short` is 1 650 (realisable 1 850) and its `min_area` 3.1 m², both
fixture-derived: *bed 1350 × 1900 + body 300 to one side*. That is a **fits** floor,
not a **habitable** floor, and it is why §1's arithmetic clears — H8 now passes on
rooms an architect would not draw. AzDTN's own statutory floor for that room is
**10 m²**, and 19.3 % of real Swiss rooms sit below AZ's 3 000 mm market habitable
width. Handed to `data/standards/room-constraints.json`'s claimant, *The annotation
spec is US-shaped and the drawing is now Azerbaijani*, and to the statutory-severity
ticket below. Not fixed here: the fix is a room-table number, and this ticket holds
neither that file nor a mandate to move a published minimum from a window rule.

⚠️ **`win.area_ratio` is the only statutory minimum on the map posted `soft`.**
AzDTN cl. 9.13's 1:8 is `verified` and mandatory. It stays soft because **C14 names
it** — *"one soft window fraction"* — and amending a standing constraint through a
window rule is the wrong door. Its statement *is* corrected: the run is now over
`exterior`-condition faces only, closing the *Opening placement rules* §6.1 handoff
that let a mid-block flat satisfy its glazing on a party wall.

### 8. What it hands on

| Handed | To |
|---|---|
| The exposure presets, and every number fitted or measured at one | *The exposure presets were fitted to a measurement of one room* (new) |
| `win.area_ratio`'s severity, and AzDTN's statutory **area** floors shipped soft against a 3.1 m² ergonomic bedroom | *A statutory floor, posted soft, in the one region v1 ships* (new) |
| 43.3 % corpus rejection, 23.0 points of it the kitchen alone | *A third of real kitchens have no window and the engine may not draw one* (new) |
| The 1 850 mm realisable habitable width against AZ's 3 000 mm market default | *The annotation spec is US-shaped …*, which holds `room-constraints.json` |
| `open.leading_edge_nib`'s `src`/`note` re-base (ADR 0021), still unclaimed on `rules.json` | *A dwelling with no toilet passes every check* or *Fit the ENGINE_CHOICE acceptance thresholds* |
