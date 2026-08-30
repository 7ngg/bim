---
id: 77
title: The bar plane is derived and the solver has never run it
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
blocked_by: []
writes:
  - experiments/plane-accounting/
  - docs/research/solver-formulation.md
---

# The bar plane is derived and the solver has never run it

## Question

**ADR 0039 is an identity and two hand-checks.** It says `solver.py` should
subtract the erosion band per *side* rather than on all four, so `amm_i` becomes
the area ADR 0001 publishes:

```
amm_i = 62 500 · a_i  −  75 · Σ_{s ∈ 4 sides} interior_len_mm(i, s)
```

The arithmetic is exact and it spends no second `AddMultiplicationEquality`. What
it does spend is **auxiliary integers and reified literals, bounded by
rooms × 4 sides × faces**, and not one of them has ever been built. The 15 s cap,
τ = 4 and every timing on this map were fitted against a model without them.

⚠️ **Until this closes, `acceptance-bar.md` §11.1 and `CONTEXT.md`'s Space plane
both describe a decision as though it were a shipped state.** That is deliberate
and it is the debt this ticket pays.

**What has to be measured:**

1. **Build time and solve time**, against the incumbent, at the shipped
   configuration verbatim — `mm_affine`, eroded minima, τ = 4, σ = 0,5 m, 15 s,
   4 workers. Part II's rig is the comparator and its seed-to-seed spread is the
   bar the cost has to clear. ⚠️ A finding that this does not fit is a finding,
   and ADR 0039 decision 6 already carries the fallback: floors only, forward-only
   literals, `dim.max_area` left to the validator.
2. **The INFEASIBLE delta on the floor.** The incumbent's number is **14 of 273**
   with all fourteen attributed to `dim.statutory_min_area` by ablation. Re-run
   the same arm with the corrected plane; the difference is what the plane defect
   was actually costing, and it is the number `acceptance-bar.md` §11.1 should
   carry in place of the 5,1 % upper bound it carries now. ⚠️ That figure is
   **pre-ADR 0033** — the warp did not post the floor when it was measured — so
   the incumbent arm has to be re-run too, not quoted.
3. **The cap side, which no arm on this map has ever exercised.** `dim.max_area`
   is hard and `site: both` and the toy solver **does not post it at all** — H4
   posts `min_w`, `min_h`, `min_area` and aspect, and nothing else. So the false
   pass ADR 0039 describes is a property of the *spec*, not of anything measured.
   Post the cap under both readings and find out whether it binds, and on which
   Rooms. ⚠️ If it turns out never to bind at production geometry, ADR 0039
   decision 4's biconditional requirement is the expensive half of the change and
   is bought for nothing.
4. **Whether the corner residual is worth recovering after all.** ADR 0039 drops
   it at ≤ 0,0225 m² per Room, conservative on floors and *lenient* on the cap.
   Exact recovery needs contact at a point rather than over a length. Measure the
   realised distribution before accepting the bound as decorative.

**What this is not.** Not a re-opening of ADR 0039's decision — a measurement that
the encoding is unaffordable selects its own stated fallback, it does not restore
the two planes. Not a change to any threshold: ADR 0027, ADR 0033 and
`acceptance-bar.md` §3.2 settle `dim.statutory_min_area` three times over. Not a
change to `_add_exterior`, which keeps its forward-only literals by decision 4.

**Where it goes.** `experiments/plane-accounting/`, **new**, importing
`solver-toy/` and `warp/project_join.py` read-only and editing neither — the
idiom `envelope-exposure/` and `h8-frontage/` already use, and the right one here
because an A/B needs both arms live. `experiments/solver-toy/` is claimed by
*What an ordered entry sequence costs the solver* and `experiments/warp/` by
three tickets; this takes neither.

## Raised by

*The projection discards a fifth of the guarantees the warp now buys*
(2026-08-30), ADR 0039 consequence 5.

## Resolution

**The encoding is built, it is exact, and it fits. ADR 0039's fallback is not
selected — and three of its supporting claims were wrong.** ADR 0040;
`docs/research/solver-formulation.md` **Part VIII**;
`experiments/plane-accounting/`, new.

All four items answered, plus a correctness defect the ticket did not carry.

### Before any timing: the encoding is exact, and ADR 0039 named the wrong set

**11 892 Rooms, worst `|integer identity − space_m2|` = 0,0 mm².** Shapely on real
solved geometry against the closed form. Part VII's two hand-checks reproduce to
the unit; the CP-SAT model's `amm_i`, read out with Rooms pinned, equals the
oracle on every Room tried; `plane="solver"` reproduces `solver.project` — same
status, same objective, same variable count.

⚠️ **`Envelope.all_faces()` is one notch-class too wide.** It walks the boundary of
the *interior*, and an **enclosed void** bounds the interior exactly as the outside
does. `absolute_area.outside_of` deliberately excludes enclosed components, so a
Room's edge on a void **erodes** — crediting it as boundary contact reads that Room
**larger** than the bar plane, the one direction `dim.max_area` cannot afford.
`bar_plane.no_erode_faces()` is the corrected set. 8 of 273 candidates carry a void
here; ADR 0028 makes `voids` a first-class Proposal field in the shipped contract.

### Item 1 — the cost is MEASURABLE, unlike II.1's, and it fits anyway

340 pairs, 307 reaching the solve, shipped configuration verbatim.

| | `A` incumbent | `B` bar plane | `Bc` + corner term |
|---|---:|---:|---:|
| variables / constraints, p50 | 454 / 1 035 | **1 114 / 1 980** | 2 376 / 4 687 |
| build p50 | 24,1 ms | 46,5 ms | 102,2 ms |
| wall p50 / p90 | 0,193 / 1,873 s | 0,447 / 3,015 s | 0,523 / 2,450 s |
| at the 15 s cap | 17 | **16** | 15 |
| total over 307 | 419,0 s | **487,7 s** (+16,4 %) | 501,0 s |

Paired `B − A`: p50 **+0,198 s**, **284 slower against 23 faster**. Over six CP-SAT
seeds on 35 candidates, only **6 of 35 (17,1 %)** differences sit inside the
candidate's own seed spread. **This is detectable where II.1's arithmetic was
not** — and that is the honest reading of ADR 0039 decision 3: no second
multiplication is true, and the multiplication was never the cost.

**It fits because none of it lands where the budget is.** Time to first Plan
0,110 → 0,284 s against a **15 s** cap; cap exhaustion goes **down** 17 → 16; no
candidate pushed to `UNKNOWN`. τ = 4, 15 s and ADR 0007 stand.

### Item 2 — **1,30 %**, and the plane is all of it

⚠️ **The incumbent could not be quoted, for two reasons rather than one.** ADR 0033
shipped the warp's floor after `project_join`'s run — the ticket's reason — and
*the candidate population moved too*: LIMIT 3 records 1 076 one-part donors of
2 317, `load()` now returns **1 057 of 2 292**, because ADR 0037 changed what
`COLLAPSE` and the minima tables resolve to. Both arms re-run.

With ADR 0033's floor upstream: **33 of 340** (9,71 %) refused before the solve,
**307** reach it. `A` refuses **4 of 307 = 1,30 %**, all four the floor's by
ablation (2 OPTIMAL, 2 FEASIBLE). `B` refuses **0 of 307** — all four rescued.
**5,1 %** is retired from `acceptance-bar.md` §11.1. The genuine-starvation
component of the Plan-level figure is zero on this sample; it moved upstream into
the 9,71 % the warp now pays, which is ADR 0033's cost and measured there.

### Item 3 — the cap binds, it is nearly free, and it is a bathroom

`dim.max_area` posted for the first time on this map, as `k[class] × target`, read
from `rules.json#/area_bands` and `room-constraints.json`, never transcribed.

**It binds**: **10 Rooms of 1 993** above their band uncapped, 9 candidates,
**every one a `BATHROOM`**, worst **10,2 m² over** — `brief.md` §9.3's 40 m² WC
through a third door, made compulsory by `model.no_unassigned_area`.
19 Rooms sit within 1 m² of the cap: 18 bathrooms, one corridor.

**It is nearly free**: +6 constraints, no new variables, wall delta p50 −0,002 s,
**0** new INFEASIBLE.

**And the plane decides whether it works**: posted on the bar plane it leaves **0**
Rooms above the cap; on the solver's smaller plane, **2**. So ADR 0039 decision 4's
biconditional literals are bought for something, and the ticket's own ⚠️ — *"if it
turns out never to bind, decision 4's requirement is bought for nothing"* — is
answered.

### Item 4 — the residual is decorative, and ADR 0039's reason for dropping it is wrong

**It has a second term the ADR does not have**, exact to the mm²:

```
truth = [B] + 5 625 × (interior corners − reflex vertices on the Room's sides)
```

Where a Room's side crosses from Envelope to partition, the interior has a 270°
corner; the erosion wraps round it and takes a further 75 × 75 square at a **point**
a band-over-a-length cannot see. Over 1 993 Rooms: p50 **+0,00562 m²**, range
**−0,01125 … +0,0225**, and **109 Rooms — 5,47 % — read LARGER than the bar plane**.

- ⚠️ Decision 5's *"conservative on every floor"* is **withdrawn**.
- ⚠️ `0,0225 m²` is an **observed maximum, not a derived bound** — nothing bounds
  the reflex count but the Room's own perimeter; it reached 3 here.
- ⚠️ **Adding the corner term alone makes it worse**: `[B] + 5 625 × corners`
  over-states by exactly `5 625 × reflex`, so it is *never* conservative —
  **36,43 %** of Rooms, **6,7× as often** as `[B]`.
- ✅ **0 floor verdicts and 0 cap verdicts move**, against a plane gap of p50
  **3,91 %** of a Room's area. It stays dust, and *The posted floor is a seed-shape
  estimate* owns the warp-side twin at p50 0,038 m² — **6,8×** the median here.

**So the drop stands and the reason changes.** The objection is not that "both
sides wholly interior" under-counts; it is that half the correction is missing and
adding the other half alone inverts the sign on a third of Rooms. Exact recovery
needs both point terms, at O(perimeter) reified literals per Room against the
corner term's O(4), and it buys nothing.

### One limit, stated rather than hidden

`project_join.SOFT` contains `coverage`, so H3 is soft here and **55 of 307**
returned Plans leave interior cells unassigned. Where they do, Plan-relative and
Envelope-relative Space diverge by up to 0,32 m². The solver cannot know where
slack lands, so the encoding is Envelope-relative by construction and the two
coincide exactly when H3 holds — the shipped state. It bites both arms identically,
and it is why the exactness check above is measured against the Envelope's own
outside.

### Raised

- **78 — *What the bar plane owes a two-part Room*.** `amm_i` is derived and now
  measured for ONE rectangle; ADR 0014 gives a Room one or two, and ADR 0014's own
  words are that *"the band across the shared edge survives"*. Applied per part the
  form subtracts a band along an edge the Room does not have: at the join floor of
  1 100 mm realisable that is **0,165 m²**, **29×** the corner residual this ticket
  just dismissed and **4,3×** the warp-side dust. **53,9 %** of the index holds a
  two-part Room, so it is the majority case.

### Handed on as prose, because the file has two claimants

`data/acceptance/rules.json`, `dim.max_area`'s note: *"The solver side is FREE: H4
already builds a = w*h … an upper bound on a product tightens propagation."* Both
halves now have a measurement. **The cost claim is very nearly right** — +6
constraints, no new variables, wall delta p50 −0,002 s. **The propagation claim was
false as written** and is true once the bound is posted on the plane the rule is
stated on. 72 and 76 both hold the file; ADR 0040 consequence 2 carries the wording.

### Artifacts

- `docs/adr/0040-the-bar-plane-encoding-is-measured-and-the-cap-is-posted-on-it.md`
  — new.
- `docs/research/solver-formulation.md` — **Part VIII**, beside Part VII because it
  is that derivation measured. **Sole claimant**, held.
- `experiments/plane-accounting/` — new: `bar_plane.py`, `selftest.py`, `arms.py`,
  `seeds.py`, `report.py`, `README.md`, rows and report under `out/`.
  **Sole claimant**, held.
- `docs/spec/acceptance-bar.md` §11.1 — 5,1 % retired, 1,30 % landed, the cap
  measurement added, the residual restated as two-signed. **Declared on
  resolution, no claimant.**
- **Not touched, deliberately**: `data/acceptance/rules.json` (72, 76),
  `experiments/warp/` (62, 65, 67), `experiments/solver-toy/` (43), `CONTEXT.md`
  (its Space plane boundary rule is already correct — an enclosed void is not the
  Envelope), and no shipped code anywhere.
