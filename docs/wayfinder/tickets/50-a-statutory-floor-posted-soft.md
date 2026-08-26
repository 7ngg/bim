---
id: 50
title: A statutory floor, posted soft, in the one region v1 ships
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - data/acceptance/rules.json
  - docs/spec/acceptance-bar.md
  - CONTEXT.md
---

# A statutory floor, posted soft, in the one region v1 ships

## Question

**C14 says a region profile never rejects a Plan. AzDTN 2.7-2 fixes habitable-room
and kitchen areas by law. Both cannot be honoured, and today the law loses.**
Decide which one moves, or decide deliberately that neither does.

The hard bar binds against the **region-invariant ergonomic layer**, which is
fixture-derived. The region profile carries *soft* targets. So in the only region
v1 ships:

| | AzDTN, `verified`, statutory | hard floor actually enforced |
|---|---|---|
| living room, 2+ rooms | **16.0 m²** (cl. 5.7) | 3.7 m² |
| `bedroom_double` | **10.0 m²** (cl. 5.7) | **3.1 m²** |
| `bedroom_single` | 8.0 m² | 2.2 m² |
| kitchen | 8.0 m² | 1.8 m² |
| glazing ratio | **1:8** (cl. 9.13), mandatory | `win.area_ratio`, **soft** |

`win.area_ratio` is **the only statutory minimum on the map posted soft**.
*Opening placement rules* §10 flagged it and declined to move it; *H8 and the
single-aspect flat* held it soft for the same reason and ticketed it here: C14
names it explicitly — *"two soft area targets and one soft window fraction"* — so
changing it is amending a standing constraint, and neither of those tickets was
the right door.

## Why this is not merely tidy

The engine can emit a `bedroom_double` of **1.85 × 1.68 m = 3.1 m²**, clear every
hard rule, and be shown to a Homeowner as a survivor. `min_clear_short` 1650 is
derived as *double bed 1350 × 1900 + body zone 300 to one side* — a **fits** floor,
not a **habitable** floor. AZ's own market default for a habitable room's clear
width is **3 000 mm**; 19.3 % of real Swiss rooms sit below it.

C6 makes the bar a hard filter and the objective a ranking, so the defence is *the
soft objective pulls rooms to `target_area`*. That defence has two holes worth
pricing:

1. **A survivor is shown.** C6's contract is generate-many-reject-most-show-
   survivors, and `homeowner_surface.no_survivors` insists a failing Plan is never
   shown precisely because a Homeowner cannot judge a defective plan. A 3.1 m²
   bedroom is not annotated as defective — it *passed*.
2. **The pull is weakest exactly where it is needed.** `area.invented_envelope_hard`
   pins total floor only where the Envelope is *invented*. Where a Homeowner states
   a small Envelope, the hard minima are the whole story.

## The three ways out, and none is free

1. **Amend C14 to "a region profile may raise a floor, never lower one."** The
   reject set becomes region-dependent, which C14 was written to prevent — but the
   argument it was written on is *"a region we have never surveyed still gets a
   defensible hard bar"*, and C12 ships exactly one profile. Cost: reopens
   *Which region profiles ship in v1*, and `UK` as a test fixture stops being a
   free choice.
2. **Raise the region-invariant ergonomic floor.** Region-clean, but it asserts a
   habitability number the fixture derivation does not support and C8 forbids
   sourcing from Neufert. Cost: a number nobody can cite.
3. **Leave the floor and fix it in the objective**, e.g. a `warn` at the statutory
   figure so the Homeowner sees it. Cheapest, and it declines to reject a plan that
   is illegal in the region it is drawn for.

⚠️ Read together with *What a room's area is allowed to be*, which set the
**maximum** side of this and chose `target_area` as the anchor; and with the
`is_habitable`/`needs_window` invariant, which is what the retired
`win.habitable_touches_exterior` was mistaken for.

⚠️ **C8 cuts both ways here and the ticket should say which.** C8 forbids claiming
code compliance. It does not forbid *being* compliant, and shipping a 3.1 m²
bedroom into a market whose law says 10 is the failure C8 exists to prevent in the
other direction.

## Deliverable

A decision recorded against C14 on the map, `win.area_ratio`'s severity in
`rules.json`, and — if the reject set moves — a line in `acceptance-bar.md` §3,
whose whole argument is that the hard set carries no region.

## Resolution

**C14 is amended, monotonically: a Region profile may raise a hard floor and may
never lower one.** Both halves of the ticket are taken hard — the statutory area
floors and the glazing ratio — and the second needed a third decision to be safe.
Nothing on the map's three offered routes was chosen unmodified: option 1 was
right about *which* thing moves and wrong about what it costs, and neither option
2 nor 3 survived the measurement.

### 1. The ergonomic floor is inert, and that is why the ticket is real

`dim.min_area` rejects **0.19 %** of 42,985 real Swiss dwellings and adds
**0.00 %** to the hard union — the only rule in the registry that changes no
outcome — while being the sole predicate between a Homeowner and the ticket's
1,85 × 1,68 m = 3,1 m² bedroom. `min_clear_short` 1650 is a *fits* floor (bed 1350
+ body zone 300 one side); AzDTN 2.7-2 cl. 5.7 publishes the *habitable* one,
`verified`, in the only region v1 ships. The ticket's "not merely tidy" section
understated it: the defence is not weak, it is **absent**.

### 2. Which reason of §3 died, and which two did not

`acceptance-bar.md` §3 gives three reasons the hard floor is ergonomic. Reasons 1
(defensible where no law exists) and 2 (region-invariant because bodies are) are
untouched and keep the **base** region-free. Reason 3 — *lets v1 ship without
settling the region list* — is **spent**: C12 settled it at exactly one profile.
It was the only one of the three arguing the hard set must carry **no** region
rather than a **defensible** one, and it was insuring against a case v1 does not
have.

The amendment costs nothing that reason 3 was protecting, because **raising is
monotone**: an unsurveyed region still gets the full ergonomic bar, and no profile
may add a predicate, remove one, or weaken one. Option 1's stated cost —
*"reopens Which region profiles ship in v1, and `UK` as a test fixture stops being
a free choice"* — **does not materialise** for the same reason. `UK` publishes no
statutory area floors, so under a monotone amendment it raises nothing and remains
exactly the free test fixture C12 made it.

### 3. The corpus number is not this rule's rejection rate

Measured on the cached census: AZ statutory floors as hard reject **54,51 %** of
real Swiss dwellings, **+19,98 points** marginal over the fitted/real-pier union —
which would be **51,5 % of the surviving pool**, and would have killed the
decision if it were a pool statistic. It is not:

1. **The bar does not gate the retrieval index.** Admission is conversion fidelity
   (`proposer.md` §2.2.1, plus worst-room IoU from *The two-notch cap is now
   evidenced*), not the bar. Had the bar gated the index, the index would already
   be 15,59 % of the corpus and this map would say so. A donor below the floor
   stays in the pool, so `room-area-bands.md` §6.1's coverage argument — the one
   that refused a p95 cap at 26,6 % — **does not transfer**.
2. **`market_default` is at or above `statutory_floor` in every reachable AZ
   cell**: living 16/16, `bedroom_double` 12 > 10, `bedroom_single` 9 > 8,
   kitchen 9 > 8, `kitchen_zone_in_diner` 6/6. So the new hard rule is **strictly
   weaker than the soft target the solver already aims at**. It fires only where
   the solve failed to reach that target — precisely the case it exists for.

**Per limb**, marginal over the fitted/real-pier union, so a later ticket amends a
limb and not the rule:

| limb | cl. 5.7 | Swiss p50 | share below | marginal |
|---|---|---|---|---|
| kitchen | 8,0 m² | **8,04 m²** | 49,57 % | **16,88 %** |
| `room*` as `bedroom_double` | 10,0 m² | 14,29 m² | 5,44 % | 5,73 % |
| living / `living_dining` | 15/16 m² | 26,59 m² | 4,33 % | 1,03 % |
| `room*` as `bedroom_single` | 8,0 m² | — | 0,37 % | 0,30 % |
| `kitchen_zone_in_diner` | 6,0 m² | 23,67 m² | 0 % | 0 % |

⚠️ **The kitchen limb lands on the corpus median** and is 16,88 of the 19,98
points; drop it and the whole decision costs **3,10 %**. It is taken anyway, on
`acceptance-bar.md` §7.5's own precedent — `win.habitable_has_window`'s 45,19 %
was *"handed to the retrieval and conversion side, not paid for by weakening a
statutory rule"* — and this is the same object seen from the same side.

### 4. What is unmeasured, and the asymmetry that decides it

The rule's true cost is on **engine output**, and no Proposer has been run. ADR
0018's warp fidelity is a *proportion* result — `fit_warp.py:373-384` normalises
absolute area away — so the warp has **never** been measured against a stated
`target_area`; that measurement is `experiments/warp/`'s, from *What shape an
Envelope is when the Brief does not say*. If the warp systematically undershoots
per-room area, this rule collapses yield and `homeowner_surface.no_survivors`
fires.

That risk is accepted, and the reason is an asymmetry, not optimism. **A hard rule
that is too strict is discovered** — at build time, on the first Proposer run,
and rolled back by one field. **A soft rule that is too lax ships**: a 6,6 m²
kitchen reaches a Baku Homeowner as a *survivor*, unannotated, indistinguishable
from a good one, because C6 shows survivors and nothing marks it defective. C2's
*"would I live here"* cannot catch it, which is the whole reason the bar exists.

### 5. `win.area_ratio`: hard, rescoped, and the window is sized rather than picked

Three changes; the third is what makes the first safe, and it is why option 3
(*fix it in the objective*) was refused.

**Scope, and it is a precondition rather than a tidy-up.** The shipped statement
bound **every Space**. cl. 9.13 binds **living rooms and kitchens only** and
`room-constraints.json` says so verbatim. Soft, the over-reach cost a wrong
objective term; **hard, it would have rejected a windowless WC for its glazing
ratio.**

**The measurement that changed the answer.** Against the shipped three-entry
catalogue (`window_living` 1500 × 1500 = 2,25 m², `window_kitchen` 900 × 1200 =
1,08 m²), 1:8 demands **2+ windows on 72,7 % of living rooms, 93,6 % of
`living_dining`, 40,7 % of kitchens**; required run p50 **3,80 m** against
available window-run p50 **3,84 m** — the rule sits exactly on the feasibility
cliff, failing **33,68 %** of dwellings at `min_pier` 600 and **21,20 %** at 250.
Size the *opening* to the room and the same test costs **5,39 %** (living 6,95 %,
`living_dining` 7,73 %, kitchen 1,98 %). **Three quarters of the cost was a
catalogue artefact, not a layout fact.** Rejecting on it would have been rejecting
a room an architect keeps for a window they would widen — the same failure ADR
0021 named when a threshold *specified* the room instead of permitting it.

**The window is selected, not mapped.** `window_for_room` stops being a fixed
`key → key` map and becomes the **smallest member of the profile's width series
for that room family which satisfies cl. 9.13**, at the family's catalogue height,
even per ADR 0004, fitting the run the Space has. A **series**, not a free
derivation: the catalogue's own comment is *"a facade with two different windows
in one room is a tell"*, and free per-room widths put six widths on one elevation
— the generated look `dim.aspect_ratio_hard` exists to prevent. Splitting into two
openings buys **nothing** — total glazing width is fixed and the pier is pure loss
— so this rule never asks for a second window.

**`min_pier_mm` is therefore not load-bearing here.** At one opening per room
there is no pier between windows, so this decision does **not** rest on the
600 → 250 move ticket 20 handed to *The annotation spec is US-shaped*. The
33,68/21,20 pair is retained only as the cost of the catalogue reading.

**The residual 5,39 % is real and it is frontage** — same object as
`win.habitable_has_window`'s cost, sent the same way as §7.5 sent that one.

### 6. Two shipped files disagreed, and both were wrong

`room-constraints.json` bound `statutory_floor_binding: "warn"` (from *Which
region profiles ship in v1*, with a `force`-derived disclosure note);
`rules.json` listed `statutory_floor` under `unread_in_v1`. The tier was
simultaneously bound as a warn and not read at all — and **neither statement had a
rule behind it**: no rule of severity `warn` sourced from a region profile has
ever existed in the registry. That absence is the finding. C14's *"a region
profile never rejects a Plan"* had been implemented as *"a region profile never
**appears** in the hard set"*, which is a stronger claim C14 never made, and it is
how a `verified` statutory number sat in a shipped data file for three tickets
without ever binding anything.

The ticket's premise — *"today the law loses"* — is therefore true of
`rules.json` and **false** of `room-constraints.json`. Both bindings are
superseded: `statutory_floor` is **read** and it is **hard**.

### 7. C8 cuts both ways, and this records which way

C8 forbids **claiming** code compliance. It does not forbid **being** compliant,
and shipping a 3,1 m² bedroom into a market whose law says 10 is the failure C8
exists to prevent from the other side. No Homeowner-facing message on this rule
names a law: it is `hard`, so a failing Plan is discarded and never shown (C6,
`homeowner_surface.no_survivors`), and the only text a Homeowner ever sees is the
Brief-side arithmetic — *your Envelope cannot hold n otaq* — which is a statement
about addition. Ticket 14's disclosure-wording trap is thereby avoided rather than
solved: this rule has no disclosure to word.

### 8. Brief-side pre-image, per ADR 0015

Σ hard minima rises. A one-otaq dwelling goes from **9,0 m²** (living 3,7 +
kitchen 1,8 + `bathroom_combined` 2,5 + hall 1,0) to **26,5**; two-otaq **37,5**,
three **47,5**, four **57,5**, before the partition footprint. Those are ordinary
Baku flat sizes and **nothing leaves C13's 3–10 band**. The 9,0 m² one-otaq flat
the old floor admitted **is** the defect, restated at parse time. `brief.md` §9.4
bounds 1 and 3 must read the raised floor — owed, and `brief.md` has no claimant.

### What was written

| file | what |
|---|---|
| `data/acceptance/rules.json` | `dim.statutory_min_area` added, **hard**, site `both`, `conf: verified`, `corpus_cost` 0.5451 with its denominator written out. `win.area_ratio` → **hard**, site `both`, `binds_room_types` added, `corpus_cost` 0.0539. `tier_binding.hard_reject_below` scalar → list `["ergonomic", "statutory_floor"]`, `unread_in_v1` → `["accessible"]`, new `contradiction_resolved`. `region_binding.hard_set_is_region_free` → **false** with the monotone wording. `rule_count` 42 → **43**, conformance subset 15 → **17**. Three new **blocking** `owed` items. |
| `docs/spec/acceptance-bar.md` | §3 retitled and reason 3 struck; new **§3.1** carrying the amendment, the per-limb table, the two reasons the corpus number is not a rejection rate, the yield trigger and the file contradiction. §7.4 rewritten — title, the three changes, the owed series. §7 heading → *two hard rules*. §2's tier sentence gains `statutory_floor`. **The stale counts are fixed at all four sites**: 40 → 43, subset 14 → 17, hard 31 → 34, locale 40 → 43. |
| `CONTEXT.md` | **Statutory floor** is a new term — transcribed never derived, habitable not fits, silence is not an error, and the monotone rule. **Ergonomic minimum** gains *base of the floor* and an `_Avoid_` on its old absolute reading. **Region profile** gains the statutory floors and an `_Avoid_` on *"never which are rejected"*. The **Region is a convention** relation is rewritten and its old sentence marked false. |

### One check is left failing, deliberately

`experiments/region-profile/ergonomic_check.py` now reports **229 pass, 1 fail**:

```
FAIL  both files name the same hard tier  -- ['ergonomic', 'statutory_floor'] vs 'ergonomic'
```

That is the conformance test catching a real drift, which is what it is for.
`room-constraints.json` is claimed by *The annotation spec is US-shaped and the
drawing is now Azerbaijani*, so its half was **handed over rather than written** --
the concurrency rule, and the same posture `acceptance-bar.md` takes on
`dim.leg_join`. The check's message now names the ticket, the two lines to change
and the file to change them in, and carries an explicit *do not relax this
comparison*.

⚠️ **The edit must be made at the AUTHORING site.** `build_ergonomic_layer.py:267`
re-writes `hard_reject_below` on every run, so editing the JSON alone is reverted
by the next regeneration -- exactly the trap that silently reverted
`kitchen.needs_window` and falsified three published numbers.

`gate_check.py` **passes at 238** after a two-line fix in the same family: it read
`hard_reject_below` as a scalar and crashed on the list (`TypeError: unhashable
type: 'list'`). It now iterates the tiers, so a profile that ever publishes a
statutory *clear width* is gated on ADR 0007's congruence rather than skipped. `AZ`
publishes none today, so no gate changed value. `env_check.py` **28/28**.
`experiments/region-profile/` had no claimant, so both files are **declared on
resolution** rather than taken quietly.

### Handed on, not written

`data/standards/room-constraints.json` is claimed by *The annotation spec is
US-shaped and the drawing is now Azerbaijani* — sole claimant — so three edits are
handed there rather than written from here, which is the parallel-write hazard the
map's Notes exist to prevent. All three are in `rules.json`'s own `owed` block so
they cannot be lost the way *The partition footprint has a mean and no spread* was
created:

1. **BLOCKING — the window width series.** `win.area_ratio` is hard and its
   satisfiability rests on it. Measured reach requirement, ready to transcribe:
   **p90 2,47 m living, 3,23 m `living_dining`, 1,34 m kitchen**. Cover for
   publishing one: `catalogue_may_be_dead` records that `gost_23166_99` cl. 4.9
   makes the opening grid a **project decision**, so a series is `engine_choice`
   bounded by `gost_11214_86` and is *more* defensible than three fixed entries.
   Writing the rule hard now is writing the **decision** — C1 means no validator
   exists to be inconsistent with — but the series is owed before any build.
2. **The tier binding must follow.** `validator_binding.hard_reject_below` scalar
   `"ergonomic"` → list `["ergonomic", "statutory_floor"]`, and
   `statutory_floor_binding` `"warn"` → `"hard"`. The conformance test asserting
   the two files carry the same *string* must assert the same **list**. This is
   the one genuine schema change the decision costs.
3. **`window_for_room` becomes a selection, not a map** — `erg_key → (height,
   width series)`. The derived Type mark rides with it (the GOST mark reads
   **height-then-width**) and is `annotation.md`'s, same holder.

And one to `brief.md`, which has **no claimant**: §9.4 bounds 1 and 3 must read
`max(ergonomic, statutory)` rather than the ergonomic minimum alone.

### What this ticket did NOT decide

- **Whether the warp delivers a stated `target_area`.** Unmeasured, and it is the
  trigger that would reverse §3.1. `experiments/warp/`'s, unclaimed.
- **`win.area_ratio`'s upper bound.** There is none — AzDTN states no cap and
  `area_ratio_upper_bound` is explicitly `null`. Unchanged.
- **The soft glazing target 0.154.** Still `engine_choice`, still above the
  statutory floor, untouched.
- **Anything in `room-constraints.json`.** Claimed elsewhere; see above.
