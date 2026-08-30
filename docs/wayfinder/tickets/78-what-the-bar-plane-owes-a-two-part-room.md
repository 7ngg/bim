---
id: 78
title: What the bar plane owes a two-part Room
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: []
writes:
  - experiments/plane-accounting/
  - docs/research/solver-formulation.md
---

# What the bar plane owes a two-part Room

## Question

**ADR 0039's `amm_i` is derived, and now measured, for a Room that is ONE
rectangle. ADR 0014 gives a Room one or two.**

```
amm_i = 62 500 · a_i  −  75 · Σ_{s ∈ 4 sides} interior_len_mm(i, s)
```

Every term in it is a property of a single rectangle: one product `w·h`, four
sides, four corners. A two-part Room has two products, eight sides, and a
**shared edge that is not a boundary of the Room at all** — and ADR 0014 states
the consequence in its own words:

> `erode(A ∪ B, r)` is strictly larger than `erode(A, r) ∪ erode(B, r)`: the band
> across the shared edge survives.

Applied per part, the form therefore subtracts a 75 mm band along an edge the
Room does not have, twice, plus the corner squares at its four ends. That is not
dust: at ADR 0014's join floor of **1 100 mm realisable**, a single shared edge
costs `2 × 75 × 1 100 = 165 000 mm² = 0,165 m²` before any corner term — **4,3×**
the p50 0,038 m² grid dust *The posted floor is a seed-shape estimate* is already
deciding about, and **29×** the p50 corner residual ADR 0040 measured and
dismissed.

⚠️ **`dim.statutory_min_area` binds per ROOM, not per part** — ADR 0014, and the
rule's own statement. `constrained_warp.warp_model_constrained` already posts it
that way in the warp. So the projection cannot sidestep this by binding each part
separately: that is H4/H5's reading, which ADR 0014 licenses precisely *because*
it is conservative, and a conservative area floor on a Room that is legally short
is the false-refusal side this whole thread has been closing.

**What has to be settled:**

1. **The encoding.** The join band is linear in the shared-edge span, which the
   Proposal already carries as `dim.leg_join`'s subject and which
   `room-rectangles/solver_parts.py` Design A already constrains. Whether it is
   as cheap as the boundary term — no second product — or whether a two-part Room
   needs contact literals between its own parts, which the one-part case did not.
2. **What it costs at the shipped configuration.** ADR 0040 measured the one-part
   encoding at 2,36× the variables and +16,4 % total solve time, fitting inside
   the 15 s cap with room. A two-part Room roughly doubles the per-Room term set
   before the join is added, and **1 235 of 2 292 converted dwellings — 53,9 % —
   hold at least one two-part Room** (`load()`, this map's current index). It is
   the majority case, not the tail.
3. **Whether the corner and reflex terms compose.** ADR 0040 found the residual
   is `5 625 × (corners − reflex)` and two-signed on 5,47 % of one-part Rooms. An
   L-shaped Room has a **reflex corner of its own**, which is a third sign, and
   nothing has been derived for it.

**What this is not.** Not a re-opening of ADR 0014 — a Room is one or two
rectangles and the Proposal decides. Not a re-opening of ADR 0039 or ADR 0040:
the one-part encoding is measured and stands, and this is the term it does not
carry. Not a threshold change of any kind.

**Where it goes.** `experiments/plane-accounting/`, extending the existing A/B to
`--parts=2` through `room-rectangles/solver_parts.py`'s Design A — the arm
`project_join.py` already carries as its `k2` limb, with that limb's own caveat:
that rig binds a Room's `min_area` on the PRIMARY part where ADR 0014 binds it on
the Room, so it is strictly stricter and a false refusal it *misses* may be hidden
by that strictness. Reading `docs/research/solver-formulation.md` Part VIII for
the one-part baseline and writing Part IX beside it.

## Raised by

*The bar plane is derived and the solver has never run it* (2026-08-30), ADR 0040
consequence 3.
