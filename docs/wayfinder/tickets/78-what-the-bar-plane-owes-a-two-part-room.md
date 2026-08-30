---
id: 78
title: What the bar plane owes a two-part Room
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
blocked_by: []
writes:
  - experiments/plane-accounting/
  - docs/research/solver-formulation.md
  # declared on resolution, unclaimed at the time:
  - docs/spec/acceptance-bar.md
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

## Resolution

**The join is one length and thirteen variables, it fits, and the false refusals
turned out to be the binding site rather than the plane.** ADR 0041;
`docs/research/solver-formulation.md` **Part IX**;
`experiments/plane-accounting/parts_plane.py`, `selftest_parts.py`,
`arms_parts.py`, `seeds_parts.py`, `report_parts.py`, new.

All three items answered, plus a false refusal the ticket did not carry and a
shape claim three artifacts make that the corpus contradicts.

### Item 1 — the encoding, and it is cheaper than the boundary term

```
amm_Room = 62 500 · Σ_p a_p  −  18 750 · ( Σ_p int_units(p)  −  2 J )
```

**A two-part Room needs no contact literals against its own parts.**
`AddNoOverlap2D` already covers a Room's own part pair, and two interior-disjoint
rectangles meet in **at most one** maximal segment — so the whole term is one
length: four flush literals, two direction literals, three integers per axis for
`max(0, min(hi) − max(lo))`, and the length itself. Measured, **exactly 13
variables per two-part Room**: p10, p50, p99 and max all 13 over 284 candidates,
against the boundary term's O(sides × faces). No second
`AddMultiplicationEquality` — the form stays affine in `a_p`.

`int_units(p)` is ADR 0039's per-part quantity unchanged, and the code is ticket
77's: `BarPartsProjector` is `solver_parts.PartProjector` with `_add_dimensions`
replaced and `bar_plane.py`'s four reified-contact helpers bound in. The arm that
is the incumbent **is** `solver_parts.project_parts` — same status, objective,
rectangles, variables and constraints, asserted on four Envelopes (P6).

### Item 2 — the cost at the shipped configuration

332 pairs, **47 refused by the warp (14,16 %)**, **284 reaching the projection**,
1 961 Rooms of which **345 (17,6 %) are two-part**. Five arms, each one change
from the last.

| arm | vars p50 | cons p50 | wall p50 | at the 15 s cap | first Plan p50 | INFEASIBLE |
|---|---:|---:|---:|---:|---:|---:|
| `A` incumbent | 1 153 | 2 555 | 1,390 s | **90** | 0,257 s | **5** |
| `Ar` floor on the Room | 1 155 | 2 555 | 1,660 s | 100 | 0,266 s | 0 |
| `Bn` bar, no join | 2 042 | 3 786 | 2,155 s | 99 | 0,591 s | 0 |
| `B` bar + join | 2 055 | 3 809 | 2,424 s | **102** | 0,623 s | 0 |
| `Bcap` + `dim.max_area` | 2 055 | 3 816 | 2,336 s | 104 | 0,629 s | 0 |

Paired: `B − A` is **1,82×** the variables, **1,51×** the constraints, **+13,2 %**
total solve time, 227 slower against 57 faster. **The join term is 1,5 points of
that** — `B − Bn` +0,0084 s at p50, 184 slower against 99 faster, p < 10⁻⁶. The
binding-site move is **+2 variables**. `Bcap − B` is the one delta a sign test
cannot separate from zero: p50 −0,0003 s, 139 against 143, **p = 0,86**.

**And the seed sweep separates the two costs.** Six seeds per arm over 19 stratified
candidates: `B − A` is **outside** the candidate's own spread on **15 of 19** (median
+0,336 s, p = 0,00073) — the plane is measurable, as at one rectangle. **`B − Bn` is
inside it on 18 of 19 (94,7 %)**, median +0,0046 s, **p = 0,167**. The join term is a
systematic +8,4 ms over 284 paired candidates and undetectable on any single one.

**It fits**, and ADR 0039 decision 6's fallback is not selected. ⚠️ **But the
margin is thinner than at `--parts=1`, and not because of this encoding**: the
*incumbent* already exhausts the 15 s cap on **90 of 284 (31,7 %)** at two parts,
against 17 of 307 (5,5 %) at one. That is Design A's search space. The count rises
102 where Part VIII saw it fall to 16, so Part VIII's *"none of it lands where the
budget is"* must not be quoted here.

### Item 3 — the terms do not compose; they are replaced, and the replacement contains them

```
truth(U) = 62 500 |U| − 18 750 E_int(U) + 5 625 · Σ_v w(v)      w(v) = I(v) − nU(v)·[nO(v) ≥ 1]
```

Label the four cells round a lattice vertex `U` / `F` (free) / `O` (other
interior); `I` counts the half-edges with one side `U` and the other `O`.
`corners − reflex` cannot extend, because it is stated on a rectangle's four
corners and its sides' interiors and a union has neither. This rule reproduces it
exactly at one part and reaches three cases it could not:

- **an L's own reflex corner** — `I = 2, nU = 3` → **−1**. **So the ticket's
  "third sign" is not a third sign**: it is the same −5 625 a mid-side flip is.
  What two parts add is more *places* a reflex can sit, not a new term.
- **a flush join end** — `I = 2, nU = 2` → **0**, the case naive per-part counting
  gets **wrong** rather than misses: it reports two interior corners, +11 250 mm²,
  at a point where the union has no vertex.
- **a Room meeting an enclosed void diagonally, at a point** — `I = 0, nU = 1` → −1.

Exact against `absolute_area.space_m2` on **11 740 Rooms at a worst disagreement
of 0,0 mm²**, in shapes L, T, Z and rectangle. With the join term the residual is
p50 **+0,00562 m²**, every value a multiple of 5 625, and **all 1 961 Rooms inside
ADR 0039's 0,0225 m²** — still an observed range, not a bound, because `nU`
reaches 3. **0 floor and 0 cap verdicts move.** Without the join term it goes to
p90 **+0,236 m²**, max **+0,938 m²**.

### The false refusal the ticket did not carry

`acceptance-bar.md` §9.1 binds *"area, and every area rule — per Room, over the
union"*. `solver_parts.py` binds it on the **primary part**, which
`project_join.py` LIMIT 3 flags as *"strictly stricter"*.

**5 of 284 candidates (1,76 %) are INFEASIBLE under the incumbent, all five the
statutory floor's by ablation, and all five are rescued by `Ar` alone** — the
binding site, plane unchanged, +2 variables. `Bn` and `B` rescue nothing further,
because nothing is left. ⚠️ **So the plane's own Plan-level contribution at two
parts is zero**, where Part VIII measured 4 of 307 rescued at one part. Not a
contradiction: a stricter site sat in front of it and spent the refusals first.
What the plane buys here is coverage — mean unassigned cells **7,4 → 2,6** — and
the objective, better on 140 of 279 against 4 worse.

### What the join term is actually worth, stated plainly

⚠️ **One verdict in 1 961 Rooms.** The corpus joins at **p50 8 grid units**, not
ADR 0014's floor of 4, so the omitted band is p50 **0,300 m²** and max **1,013 m²**
— 53× the corner residual ADR 0039 dropped, and 7,9× the grid dust *The posted
floor is a seed-shape estimate* owns. It still converts to almost nothing, and the
reason is the rule's own site: `dim.statutory_min_area` is `site: both`, so a Room
read short is **re-sized, not refused**. A two-part Room's headroom over its own
floor is p50 **9,37 m²**, and **only 1 of 345 has less headroom than its own join
term** — a Room gets a second rectangle because it is large and awkward, not
because it is tight.

It is bought for the posted quantity being the quantity the rule is stated on, at
13 variables and 1,5 % of the solve. Not for yield.

### `dim.max_area`, posted on a Room that is two rectangles

**10 Rooms of 1 961 (0,51 %)** sit above their band uncapped, across 9 candidates,
worst **8,19 m² over**; **one of them is a two-part `Z`**. Part VIII's finding
survives and widens: 7 `BATHROOM` but also 1 `KITCHEN`, 1 `CORRIDOR`, 1
`STOREROOM`, where at one part all ten were bathrooms. Posting it leaves **0**
above the cap, at +7 constraints and no new variables; the solver plane summed
over the parts leaves **2**.

### ⚠️ Raised: two rectangles are an L only 55 % of the time

Over the **1 535** two-part Rooms of the converted index: **847 L, 332 T, 329 Z,
27 rectangle** — **44,8 % do not have exactly one reflex corner**, against
`erosion_check.py`'s `assert n == 6 and reflex == 1`, ADR 0014's *"exactly one
reflex corner"* and `acceptance-bar.md` §9.1's repetition of it.

✅ **The geometry survives and that is checked, not assumed**: P9 re-runs all three
of `erosion_check.py`'s properties at **two** reflex corners on a T and a Z —
strict containment, the inner-face polygon **pointwise**, and 8 vertices on integer
millimetres. ADR 0001 is untouched and this encoding is verified on all four
shapes. What is open is whether the *contract* should restrict to an L, and what
that costs conversion: *A two-part Room is a T or a Z as often as it is an L*.
