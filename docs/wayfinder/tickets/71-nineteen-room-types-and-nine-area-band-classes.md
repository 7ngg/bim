---
id: 71
title: Nineteen room types and nine area-band classes
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
blocked_by: []
writes:
  - data/acceptance/rules.json
  - docs/research/room-area-bands.md
---

# Nineteen room types and nine area-band classes

## Question

**`dim.max_area` binds `k[type] × Room.target_area`, and there is no published
type-to-class map.** `rules.json`'s `area_bands.classes` holds **nine** entries —
`room*`, `bathroom`, `wc`, `kitchen`, `living_dining`, `living_room`, `corridor`,
`dining`, `storeroom` — keyed by **corpus label**, while `brief.md` §3 fixes
**nineteen** Room types. Every class carries `"members": null`.

The rule's own statement says `k[type]`; the table is `k[class]`. Nothing in the
repo states which is which. `kitchen_dining`, `living_dining_kitchen`,
`bathroom_combined`, `entrance_lobby`, `hall`, `study` and `utility` all resolve
through a mapping that exists only in whoever last read it.

**Found, not caused, by *A zone floor is posted on the whole room* — and that
ticket defused the acute form rather than fixing it.** The old `kitchen_dining`
target of 6,0 put the cap at `k × 6,0` ≈ 13–15 m² against a corpus minimum of
20,9: every real kitchen-diner rejected from *above*, by a hard rule. The target
is now 18,8 and the cap lands ≈48–58 m², so nothing is visibly broken today. The
mapping is still unwritten, and the next type whose target moves will hit it
again.

**What has to be settled:**

1. **The nineteen-to-nine map, published as data** — `members` on each class, or
   a class key per room type. ⚠️ Two types have **no plausible class at all**:
   `living_dining_kitchen`, for which no corpus label exists, and
   `kitchen_dining`, whose label is **disqualified** (ADR 0034 consequence 1 —
   39 of its 41 rooms sit in dwellings that also carry a separate `KITCHEN`, so
   the label is a dining room). Deciding those two is deciding whether a compound
   type borrows a class or earns one.
2. **Whether `absolute_cap[type]` is reachable for every type.** It is the
   fallback where no target exists, so a type with no class has no cap either —
   which is the `40 m² WC` defect `brief.md` §9.3 was written to close, reopened
   through a different door.
3. **Whether `k` should be re-fitted for the compound types rather than
   borrowed.** `k` runs 2,02 to 8,15 and `room-area-bands.md` §6.1 says a single
   global `k` would be the invented number the rule exists to avoid — borrowing a
   neighbour's `k` is a smaller version of the same move.

## What this is not

Not a change to any fitted value: the nine `k` and `absolute_cap` figures are
ADR 0023's, `conf: fitted`, with published corpus costs. Not the referent
question — ADR 0034 settled that, and this is the tier below it.

## Raised by

*A zone floor is posted on the whole room* (2026-08-30), which needed a class for
`kitchen_dining`, found none, and declared `rules.json` for prose only rather
than author this inside a kitchen-diner ticket.

## Resolution

**ADR 0038.** The map is published, the class list is eleven, and the hole was
wider than the ticket knew.

### What the hole actually was

`dim.max_area` — **hard**, site `both` — could not be evaluated on **nine of the
nineteen** Room types, so it silently did not fire on them. Eight are reachable
in v1 and **all eight are Brief-nameable**.

| bound before this ticket | types |
|---|---|
| `k × target` | `living`, `living_dining`, `kitchen`, `bedroom_double`, `bedroom_single`, `bathroom`, `wc` |
| `absolute_cap` | `dining`, `corridor`, `storage` |
| **none** | `hall`, `bedroom_principal`, `study`, `shower_room`, `utility`, `bathroom_combined`, `kitchen_dining`, `living_dining_kitchen`, `entrance_lobby` |

**`hall` is the one that decides how bad this was.** `brief.md` §3.1 invents a
`hall` wherever the Brief names none, so **100 % of Plans carried a Room with no
upper bound**, ceilinged only by `circ.fraction_hard` at 30 % of Σ Space — **27 m²
of hall on a 90 m² dwelling passes every rule in the file**. That is §9.3's 40 m²
WC through a different door, shipping in every plan rather than in a worked
example. And `hall` has no target at either rung of §9.2's ladder, so
`dim.market_default_area` had nothing to pull against either: floor 1.0 m², no
ceiling, no preference between.

**The soft term had the same hole.** `soft_w[type]` reads the same nine classes,
so `bedroom_principal`, `bathroom_combined` and `living_dining_kitchen` each
carried a target and no soft term to apply it with.

⚠️ **One correction to this ticket.** It says every class carries
`"members": null`. The field did not exist — **absent**, not null, which is the
weaker of the two, because a null at least declares the slot.

### 1. The map, published as data

`room-constraints.json#/ergonomic/area_band_classes`, beside `corpus_label_map`
rather than beside the table it feeds, because it is a **vocabulary projection**
and ADR 0037 put every projection there; `rules.json` carries a pointer, not a
copy. Four rungs, and every one of the nineteen rows declares which it used:
`contains(label)` ×11, `contains(fixture)` ×4, `composed` ×2, `analogy` ×1.

**The ticket's framing had a third option it did not name.** It offered *borrow a
neighbour's class* or *earn your own*, and warned correctly that borrowing is a
smaller version of inventing. The answer is **containment**, which is neither: a
**target** must be type-specific — *a hall should be about this big* — and a
merged population cannot supply one, which is precisely why
`corpus_medians.hall_entrance_lobby_corridor` is explicitly null. A **band** is a
dispersion statistic over a population, and the population `corridor` was fitted
on **is** `hall ∪ entrance_lobby ∪ corridor`, merged by the corpus and already
declared. Naming that membership borrows nothing. The same reading resolves
`bedroom_principal` and `study` onto `room*` (Swiss `ROOM` is generic — 76,052
against 21,717 `BEDROOM`, which §10 already said), and `bathroom_combined` and
`shower_room` onto `bathroom`, of which combined units are the majority.

**Totality is gated, not assumed** — all nineteen resolve or `gate_check.py`
fails. A type with no class is worse than a wrong bound, because a wrong bound
reports itself.

### 2. The two compound types are now the best-evidenced rows, not the worst

Both targets were already per-dwelling sums of clean donor classes, so **the same
composition yields the band**. Measured on ticket 70's own population
(`experiments/warp/out/dwelling_rooms.json`):

| class | n | p50 | `absolute_cap` | `k` | CV | `soft_w` |
|---|---:|---:|---:|---:|---:|---:|
| `kitchen_dining` | 1,308 | 18.82 | **49.77** | **2.64** | 0.37 | 0.63 |
| `living_dining_kitchen` | 24,046 | 37.11 | **69.00** | **1.86** | 0.23 | 1.00 |

`kitchen_dining`'s p50 reproduces the shipped `corpus_medians` 18.8 exactly,
which is the check that it is the same composition.

**Borrowing was measured and refused.** `kitchen` gives 48.1 (−3 %), `dining`
gives 69.0 (**+39 %**), `living_dining` gives 73.7 (+7 %) — and the bias has a
mechanism: **a compound's `k` is always below its donors'**, because summing
partly decorrelates, so borrowing is systematically **lenient** while looking
conservative.

⚠️ Site clustering checked, since one site is 12.2 % of `kitchen_dining`'s n:
`k` holds at **2.49** on site medians and **2.58** with the heaviest site
dropped, against 2.64 published. ⚠️ `soft_w` for `living_dining_kitchen` is
**1.00 not 1.01** — its CV ties the anchor within the spread back-solved from the
nine shipped cells, and re-normalising ADR 0023 on 0.8 % is a re-fit this ticket
does not do. **No shipped value moved.**

### 3. `utility` — the one analogy, flagged as one

No population contains it and none can be composed. Swiss Dwellings has **no
laundry label**, and neither does the shipping market: over MIDA's published Baku
schedules the room-name vocabulary is **eight names** — `Eyvan`, `Yataq otağı`,
`Sanitar qovşağı`, `Mətbəx`, `Dəhliz`, `Qonaq otağı`, `Qarderob`,
`Mətbəx-studio` — with **no utility room and no storeroom in Azerbaijani market
practice at all**. Refusing the type in v1 was rejected: AzDTN 2.7-2 puts
`camaşırxana` in the mandatory `yardımçı sahələr` list.

**It takes `bathroom`, not `storeroom`.** Containment onto `STOREROOM` was the
tempting read and is **wrong on the mechanism**: `STOREROOM` is dry residual space
(CV 1.04, `k` 8.15, the loosest class in the table) while a utility is
`is_wet: true`, a **plumbed appliance room** sized by a machine plus a body zone —
which is exactly how the ergonomic layer derives both, `utility` at 900 × 1500
(washer + body) as `bathroom` is 1000 × 1700 (bath + body). It decides the number
too: `storeroom` would cap a laundry at **18.23 m²** against `bathroom`'s
**9.15 m²**, and 18 m² is not a bound an architect would recognise. `conf:
derived`, retired by any corpus carrying a laundry label.

### 4. The C14 lever handed here by `az-market-default-against-practice.md`

*Raising a profile `market_default` raises a hard cap; C14 authorises raising a
**floor** and is silent on loosening a **cap**.* Settled **without amending
C14**, because the rule has two limbs of different character. `k × target_area`
is a **proportionality band around a requested size** and moves with the request
by design, identically whether the request came from a Homeowner (C4, sovereign)
or from the profile's measured practice (ADR 0035, may only move up).
`absolute_cap` is the **region-free outer bound and no profile touches it** —
that is where C14's *no profile may weaken a predicate* lives. C14's guarantee
never attached to a band around a number the Brief itself supplies.

What makes that safe rather than merely stated is a **build-time gate**, owed to
`gate_check.py` and not written here: `market_default ≤ absolute_cap` of the
resolved class. **Run over the 11 profile cells and all pass** — tightest
`kitchen` 9.0 / 20.59 (**2.29×**), then `bedroom_principal` and `bedroom_double`
13.2 / 31.09 (2.36×) and `bathroom_combined` 3.8 / 9.15 (2.41×). `bedroom_principal`
is only checkable because the map resolves it.

`dim.stated_target_implausible` widens from *a **stated** target* to **any**
resolved target: the check is about the number, not its provenance, and the
narrow reading left uncovered the one provenance a Homeowner cannot correct.
`warn`, scope `brief`, **`rule_count` stays 43**.

### 5. What this exposed and did not fix

⚠️ **ADR 0037 was under-scoped.** Two more private copies of the projection sit
in `experiments/acceptance-thresholds/` — `reject.py`'s `ERG` / `ABS_CAP` /
`classify_parts` and `census.py`'s `COLLAPSE` — and their class keys **disagree
with the shipped table**: `living` and `storage` against `living_room` and
`storeroom`. `reject.py` also carries `EXEMPT_ASPECT = {corridor, hall, storage}`,
naming a `hall` the corpus cannot produce.

⚠️ **`dim.max_area`'s published `corpus_cost: 0.0311` was measured with
`kitchen_dining` silently exempt** — `ABS_CAP` has no entry and the guard is
`if cap is not None`, so the same silent pass this ticket is about ran inside the
rig that priced the rule. 40 rooms, 0.093 % of the census: **the number survives,
its provenance does not.** Do not re-quote it as the eleven-class figure.

⚠️ **`k × target` is a cross-provenance product** — a CH ratio times an AZ target
— running **62 %–114 %** of the class's own cap and **inverting**: `living` caps
at 2.35 × 17.6 = **41.4 m²** while `living_dining` caps at 2.02 × 17.6 =
**35.6 m²**, so the room containing a dining area caps *smaller*. Neither limb is
this ticket's — the target is ADR 0035's tier, `k` is ADR 0023's fitted set — so
it is measured, named and **ticketed as 76**.

### Artifacts

- `data/acceptance/rules.json` — two composed classes, `members` pointers,
  `corpus_label` per class, the TWO LIMBS note, the widened statement. **Held.**
- `docs/research/room-area-bands.md` §12 and §6.1's two rows. **Held.**
- `data/standards/room-constraints.json` — `ergonomic.area_band_classes`.
  **Declared on resolution**, unclaimed in assignment; **72 lists it**, so this
  was held strictly to its own subject: one new additive block, **124 insertions
  and 0 deletions**, no citation repair, no aspect field, no value edit.
- `CONTEXT.md` — new term **Area-band class**. Declared on resolution, unclaimed.
- `docs/adr/0038-a-type-takes-the-class-whose-population-contains-it.md`.
- **Raised: 76**, the cross-provenance inversion.

**Not touched, deliberately:** `experiments/acceptance-thresholds/` and
`experiments/region-profile/gate_check.py`. Both are handed on as prose with the
exact assertions written out, the discipline 69, 73 and 74 used.
