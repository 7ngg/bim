# ADR 0037 — The profile is read, not copied, and the third vocabulary is published

**Status:** accepted. Pays [ADR 0033](0033-the-warp-posts-the-statutory-floor-and-pays-adr-0027s-debt.md)
consequence 5, lands [ADR 0034](0034-an-az-cell-declares-what-it-measures-and-a-part-may-only-floor.md)'s
four owed gates and [ADR 0036](0036-the-open-plan-type-ships-disclosed-and-its-entailed-floor-was-never-licensed.md)'s
fifth. Amends neither.

## Context

`absolute_area.STAT_FLOOR` was a hand transcription of `room-constraints.json`
with nothing in the repo binding the two. That was tolerable while the table only
*measured*; ADR 0033 made it **constrain geometry**, and a drift stopped producing
a wrong figure in a report and started producing a plan built to a floor no
regulator wrote — the C8 failure seen from the inside.

**The ticket was raised on the risk. Three of the eight copies were already wrong
when it was taken.**

1. **`absolute_area.MARKET` sat four cells behind [ADR 0035](0035-the-market-tier-is-re-fitted-to-baku-and-may-only-move-up.md),
   which had landed the day before.** `PRIVATE` 12,0 against 13,2, both living
   limbs 16,0 against 17,6, and `wc` 2,1 absent entirely. One day.
2. **`HABITABLE` omitted `DINING`, whose `counts_as_otaq` is `true`.** So
   `floors_for` under-counted otaq, and a dwelling with a living room and a
   dining room took `living_room_1room_flat`'s **15,0** where the profile's own
   guard says `living_room_2plus`'s **16,0** — a hard floor 1 m² low, on the
   largest room in the plan.
3. **`fit_warp.MIN_SIDE` had no `KITCHEN_DINING` row**, so it fell to
   `MIN_SIDE_DEFAULT = 5` against the **6** its own stated formula gives.

`MARKET`'s cell for `KITCHEN_DINING` is the fourth and it is not drift at all: it
read **6,0** from `kitchen_zone_in_diner.market_default`, which is the read
ADR 0034 decision 2 forbids outright. That cell measures the `mətbəx zonası` —
`referent: part` — and is a sound floor and never a target. The ladder's rung 2
gives the room **18,8**.

### The fix could not be written as the ticket described it

Item 1 read as *replace six literals with a JSON lookup*. Two facts refuse that
shape.

**`floors_for` did not copy numbers; it reimplemented the resolution.** The
`when_otaq_count` match, the fallthrough order and the otaq set the condition
reads were all hand-written beside the guard list that publishes them. Swapping
the values would have bound the half that was right and left the half that was
wrong — defect 2 above is in the *guard*, not in any number.

**And the lookup had no key.** The copies are keyed by **corpus label**
(`PRIVATE`, `KITCHEN_DINING`, `LIVING_ROOM`); the profile is keyed by **ergonomic
key** and reached only through `mapping.rooms` (ticket 31). Nothing in the repo
published the map between them: it existed as end-of-line comments inside four
Python dicts. **This is ticket 31's own defect one vocabulary upstream** — *"no
object stated the bridge between them"* — and it is why every one of these copies
existed in the first place.

## Decision

1. **A third vocabulary is published as data: `ergonomic.corpus_label_map`.**
   Ten labels plus the three-way collapse, each landing on an ergonomic key, with
   `erg_lenient` carrying the one split the corpus cannot make (`PRIVATE` →
   `bedroom_double` / `bedroom_single`). It lives under `ergonomic` beside
   `corpus_label_split` and `corpus_medians`, **not** inside a region profile,
   because it is a *corpus* fact meeting the canonical vocabulary and carries no
   region at all: a second corpus needs a second block.

2. **One reader, `experiments/region-profile/profile_read.py`, and the rigs hold
   no tables.** `MIN_SIDE`, `MARKET`, `ERG_AREA`, `COLLAPSE`, `GRID_MM` and
   `T_INT_MM` are now that module's output, built at import. Every consumer keeps
   the name it imported, so no call site moved; what changed is that the dict is
   a **cache of a read** rather than a transcription. `floors_for` resolves the
   guard list instead of restating it.

3. **The data is a hard dependency: no file, no import.**
   `floor_warp._check_floor_transcription` returned *silently* when `data/` was
   absent — *"rigs may run without the repo data"* — and that escape hatch is what
   let a copy survive to be checked instead of read. There is deliberately no
   bundled fallback, because a fallback copy is the drift this removes.

4. **`_check_floor_transcription` is deleted rather than extended.** Its own
   docstring called it *"an assertion, not a fix"*, and it was blind in the two
   ways that mattered: it asserted the six values that **were** copied, so a
   seventh missing by **omission** passed it — which is exactly how `floors_for`
   came to return `None` on `living_dining_kitchen` while the bar bound that type
   at site `both` (ADR 0036) — and it fired only when one file was imported.

5. **ADR 0034's four owed gates land, plus ADR 0036's fifth, and the licence
   becomes a field.** `licence` sits on every `az_area` guard entry: an object
   naming the clause and the type definition where the read is `part`, and `null`
   elsewhere, where a cell's own `ref` is the whole of its authority. ADR 0034
   wrote the licence as a condition on `compose_with`; ADR 0036 found that too
   narrow, and `compose_with` is now empty on every row — **a gate written over
   it alone would pass vacuously forever.** The field is non-vacuous today.

6. **The forbidden `part` target is stopped at the read, and the cell keeps its
   value.** `kitchen_zone_in_diner.market_default` is a first-hand transcription
   of AzDTN 2.7-3 cl. 5.1 with real provenance, and its own note already says it
   *"measures a ZONE … and never a target"*. Nulling it would destroy a number a
   regulator wrote in order to make a *consumer* bug unrepresentable, and
   ADR 0035's monotone rule governs that tier. `market_default_m2` skips a `part`
   guard and falls to rung 2; gate P6 holds it.

### Considered and refused

**Null the `part` cell** (decision 6's alternative). Refused above: it moves a
datum to fix a read. ⚠️ Not the same shape as ADR 0036's withdrawal — that
withdrew an unlicensed *entailment*; this cell is licensed and correct about the
zone it names.

**A fallback copy when `data/` is absent** (decision 3's alternative). It restores
the defect with a longer fuse. A rig that cannot see the profile cannot size a
room to it.

**Classify consumers, hard-read only where geometry is constrained.** Sounds
prudent; requires classifying every consumer correctly forever, which is the
judgement that already failed twice.

**Gate the rigs by importing them.** Refused: it would couple a *profile* gate to
`ortools` and `shapely`, so this file would fail when the solver toolchain moved.
The rigs are bound by construction instead — they hold no literals to check.

## Consequences

1. **`gate_check.py` goes 235 → 384 gates, and every one of them can fail.**
   Fifteen mutations of the data file were run against the new families and
   **15/15 were caught**; a sixteenth re-introduced a literal `MIN_SIDE` into
   `fit_warp.py` and gate C1 caught that too. This map has retired two rules for
   being unable to fire, so the mutation run is the evidence, not the count.

2. **The ticket's *"`experiments/warp/` is undisturbed"* is false, and the third
   correction is large.** Measured on the converted index, 46 794 dwellings /
   319 222 rooms:

   | correction | population | size |
   |---|---:|---|
   | `HABITABLE` gains `DINING` | otaq moves on **1 308** dwellings (2,80 %); a living **floor** actually moves on **59** | **0,13 %**, 15,0 → 16,0 m² |
   | `MIN_SIDE` gains `KITCHEN_DINING` | **41** rooms | 0,013 % |
   | `MARKET` re-read | **138 041** rooms (**43,24 %**) on 99,48 % of dwellings | mean **+0,561 m²** |

   ⚠️ **Every published `market`-arm number on this map was measured at the old
   tier** — the arm that raises each Brief target onto `dim.market_default_area`.
   **The direction is provable and the magnitude is not**: every moved cell moved
   *up*, no floor moved, and ADR 0020 sizes the box from Σ target, so no room's
   statutory floor gets harder to clear. The starvation figures are therefore
   **conservative**, not wrong. A re-run is owed and is deliberately not taken
   here: it would move results three open tickets are built on, inside a ticket
   that holds none of their subjects.

3. **`bedroom_principal` is unreachable from the corpus and now says so.** It is
   a Brief-nameable ergonomic type with no corpus label, so a retrieval never
   produces one — recorded on the bridge rather than left to be rediscovered.

4. **The `hall` / `entrance_lobby` / `corridor` merge survives one more layer.**
   The bridge sends `CORRIDOR` to `corridor` because that is the type the label
   names; rung 2 stays empty for all three, exactly as
   `corpus_medians.hall_entrance_lobby_corridor` already records.

5. **Two more hand copies are named and NOT taken.** `gate_curve.K` and
   `room_area_spread.K` duplicate `rules.json`'s `area_bands` — same class, and
   they constrain no geometry. `rules.json` is claimed by tickets 71 and 72, so
   they are handed on rather than fixed here.

## Reversal trigger

A second corpus arrives and its labels do not fit one flat block — at which point
`corpus_label_map` needs a corpus dimension, the way `mapping.conditioning`
already records that a second conditioning axis is known to exist and is not
live. That is a schema change and this ADR's shape survives it.
