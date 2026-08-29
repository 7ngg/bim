# ADR 0038 — A Room type takes the area-band class whose population contains it

- **Status**: accepted
- **Date**: 2026-08-30
- **Ticket**: [Nineteen room types and nine area-band classes](../wayfinder/tickets/71-nineteen-room-types-and-nine-area-band-classes.md)
- **Amends**: ADR 0037 (scope), ADR 0023 (adds two classes, moves no fitted value)
- **Supersedes nothing**

## Context

`dim.max_area` is **hard**, site `both`, and binds `k[type] × Room.target_area`,
falling back to `absolute_cap[type]`. The table it reads —
`rules.json` `area_bands.classes` — is keyed by **class**, and the classes are
**corpus labels**. `brief.md` §3 fixes **nineteen** Room types. Nothing in the
repository published the correspondence.

Measured, that meant **nine of the nineteen types resolved to no class at all**,
and the rule silently did not fire on them: `hall`, `bedroom_principal`, `study`,
`shower_room`, `utility`, `bathroom_combined`, `kitchen_dining`,
`living_dining_kitchen`, `entrance_lobby`. Eight are reachable in v1 and all
eight are Brief-nameable.

`hall` is the one that decides the severity. `brief.md` §3.1 invents a `hall`
wherever the Brief names none, so **100 % of Plans carried a Room with no upper
bound**, ceilinged only by `circ.fraction_hard` at 30 % of Σ Space — **27 m² of
hall on a 90 m² dwelling passes every rule in the file**. That is the 40 m² WC
`brief.md` §9.3 was written to close, reached through a different door, and
shipping in every plan rather than in a worked example. `hall` also has no target
at either rung of §9.2's ladder, so `dim.market_default_area` had nothing to pull
against either: a 1.0 m² floor, no ceiling, and no preference between them.

`soft_w[type]` reads the same nine classes, so the same gap left
`bedroom_principal`, `bathroom_combined` and `living_dining_kitchen` with a
target and no soft term.

## Decision

**1. A type takes the class whose measured population contains it, and every row
declares how it got there.** Four rungs — `contains(label)`,
`contains(fixture)`, `composed`, `analogy` — published as data at
`room-constraints.json#/ergonomic/area_band_classes`, beside `corpus_label_map`
because it is a vocabulary projection and ADR 0037 put every projection there.
`rules.json` carries a pointer, not a copy.

**Containment is not borrowing.** A **target** must be type-specific — it says
*a hall should be about this big* — and a merged population cannot supply one,
which is exactly why `corpus_medians.hall_entrance_lobby_corridor` is explicitly
null. A **band** is a dispersion statistic over a population, and the population
`corridor` was fitted on **is** `hall ∪ entrance_lobby ∪ corridor`, merged by the
corpus and already declared as such. Assigning all three to it names the class's
real membership rather than lending them a neighbour's number.

**2. Totality is gated.** All nineteen resolve or `gate_check.py` fails. A type
with no class is worse than a wrong bound: a wrong bound reports itself.

**3. A compound type earns its class by the composition that already earned its
target.** `kitchen_dining` and `living_dining_kitchen` have no usable label — one
disqualified by ADR 0034 c1, one nonexistent — but both targets are per-dwelling
sums of clean donor classes, so the band is measured the same way. Two classes
added; **nine ADR 0023 values unchanged**.

| class | n | p50 | `absolute_cap` | `k` | `soft_w` |
|---|---:|---:|---:|---:|---:|
| `kitchen_dining` | 1,308 | 18.82 | 49.77 | 2.64 | 0.63 |
| `living_dining_kitchen` | 24,046 | 37.11 | 69.00 | 1.86 | 1.00 |

**4. `utility` is the one analogy, and it takes `bathroom`.** No population
contains it and none can be composed: Swiss Dwellings has no laundry label, and
MIDA's Baku schedules carry an eight-name vocabulary with no utility room and no
storeroom in it. Containment onto `STOREROOM` is wrong on the mechanism —
`STOREROOM` is dry residual space (CV 1.04, `k` 8.15) while a utility is
`is_wet: true`, a plumbed appliance room sized by a machine plus a body zone,
which is how the ergonomic layer derives both (`utility` 900 × 1500 as `bathroom`
is 1000 × 1700). Recorded `conf: derived`, flagged as the table's only
non-containment row, retired by any corpus with a laundry label.

**5. `dim.max_area` has two limbs and C14's guarantee attaches to one.**
`k × target_area` is a proportionality band around a **requested** size and moves
with the request by design, whether the request came from a Homeowner (C4) or
from the profile's measured practice (ADR 0035). `absolute_cap` is the
region-free outer bound and no profile touches it; that is where C14's *no
profile may weaken a predicate* lives. C14 is **not amended**. The safety is a
build-time gate: `market_default ≤ absolute_cap` of the resolved class, owed to
`gate_check.py`. Run over the 11 profile cells: **all pass**, tightest `kitchen` at 9.0 / 20.59 = **2.29×**.

**6. `dim.stated_target_implausible` widens from a *stated* target to any
resolved one.** The check is about the number, not its provenance. Severity
`warn`, scope `brief`, `rule_count` stays **43**.

## Consequences

1. `dim.max_area` and `dim.market_default_area` are evaluable on all nineteen
   types for the first time. `hall` gains a **24.84 m²** cap.
2. Borrowing was measured and refused: it is biased **lenient** by −3 % to +39 %
   with an unguessable sign, because a compound's `k` is always below its
   donors' (summing partly decorrelates).
3. **ADR 0037 was under-scoped.** Two further private copies of the projection
   sit in `experiments/acceptance-thresholds/` (`reject.py`, `census.py`) and
   their class keys disagree with the shipped table.
4. ⚠️ **`dim.max_area`'s `corpus_cost: 0.0311` was measured with
   `kitchen_dining` silently exempt** — 40 rooms, 0.093 % of the census, so the
   number survives and its provenance does not. Do not re-quote it as the
   eleven-class figure.
5. ⚠️ **`k × target` is a cross-provenance product** — CH ratio, AZ target — and
   it runs 62 %–114 % of the class's own cap, inverting at
   `living` (41.4 m²) against `living_dining` (35.6 m²). Neither limb was this
   ticket's to move; ticketed.
6. A second corpus needs a second block, exactly as `corpus_label_map` says.
