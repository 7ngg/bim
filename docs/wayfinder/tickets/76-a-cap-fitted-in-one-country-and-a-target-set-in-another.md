---
id: 76
title: A cap fitted in one country and a target set in another
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - data/acceptance/rules.json
  - docs/research/room-area-bands.md
---

# A cap fitted in one country and a target set in another

## Question

**`dim.max_area`'s live limb is `k[type] × Room.target_area`, `k` is a ratio
fitted about a Swiss class median and `target_area` is an Azerbaijani number, and
nobody has ever checked what their product is.** It is the class's p99.5 only
where the two agree. They do not:

| type | bound | class `absolute_cap` | ratio |
|---|---:|---:|---:|
| `living_dining` | 2.02 × 17.6 = **35.6** | 57.12 | **62 %** |
| `bathroom` | 2.23 × 3.2 = 7.13 | 9.15 | 78 % |
| `bedroom_single` | 2.18 × 11.5 = 25.1 | 31.09 | 81 % |
| `living` | 2.35 × 17.6 = **41.4** | 48.12 | 86 % |
| `bedroom_double` | 2.18 × 13.2 = 28.8 | 31.09 | 93 % |
| `kitchen` | 2.56 × 9.0 = 23.0 | 20.59 | 112 % |
| `wc` | 3.36 × 2.1 = 7.06 | 6.20 | **114 %** |

**The visible symptom is an inversion.** `living` caps at **41.4 m²** and
`living_dining` at **35.6 m²**, so **the room that contains a dining area caps
smaller than the one that does not**. Both read the same AZ target — the
`az_area` guard for `living_dining` resolves to `living_room_2plus` with
`referent: undetermined` — while their `k` were fitted about Swiss medians of
20.51 and 28.32. Nothing is wrong with either number alone.

**This is not the sovereignty of a stated target, and the distinction matters.**
ADR 0038 settled that `k × target` *should* move with a request, from a Homeowner
or from the profile. That argument covers the target moving. It does not cover
`k` being a ratio about a **different distribution** from the one the target came
from, which is a defect in the multiplication rather than in either factor.

**What has to be settled:**

1. **Whether `k` is transferable across provenance at all.** It is dimensionless,
   which is the argument for; it is a dispersion ratio *about a specific median*,
   which is the argument against. A `k` fitted where p50 is 28.32 does not
   describe the tail of a distribution centred at 17.6.
2. **Which factor moves, if either.** The target belongs to ADR 0035's market
   tier — measured Baku practice, may only move up. `k` belongs to ADR 0023 —
   fitted, with a published corpus cost. Neither is free, and a third option is
   that the *rule* changes shape: `min(k × target, absolute_cap)` would remove
   the inversion without touching a fitted value, at the price of making the
   stated target no longer sovereign above the cap, which §6.1 argued for
   explicitly.
3. **Whether the AZ read for `living_dining` is the real cause.** Its guard
   resolves to `living_room_2plus` with `referent: undetermined` — a marker that
   ADR 0034 says changes no behaviour. It changes this one: it is why an open-plan
   room and a plain living room share a target.
4. **What it costs.** Unmeasured. The corpus is on disk and the seven rows above
   are the whole population.

## What this is not

Not a re-opening of ADR 0038's containment map — the type-to-class resolution is
settled and this is the tier below it. Not a re-fit of the nine ADR 0023 classes
on their own terms. Not the `absolute_cap` limb, which is region-free and which
no profile touches.

## Raised by

*Nineteen room types and nine area-band classes* (2026-08-30), §12.5, which
measured the product while bridging the type-to-class map and could move neither
factor from inside an area-band ticket.
