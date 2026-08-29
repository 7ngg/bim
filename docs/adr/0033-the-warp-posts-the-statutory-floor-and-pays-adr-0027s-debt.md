# ADR 0033 — The warp posts the statutory floor, and that is ADR 0027's debt being paid

Status: **accepted** · 2026-08-29 ·
[Should the warp post the statutory floor](../wayfinder/tickets/64-should-the-warp-post-the-statutory-floor.md)

## Context

ADR 0027 kept `dim.statutory_min_area` hard against a measured yield price and
said where the price goes:

> **Where a hard rule is the thing that distinguishes this engine from what the
> market ships, its cost is a debt owed by whichever stage produced the failure —
> never a reason to weaken the rule.** The rule names the standard; the stage
> that misses it owns the miss.

It then named the stage: *"To the stage that produced it… what remains is the
warp's per-room **distribution**, which a perfect level leaves intact."*

This ADR is that debt coming due. It decides nothing about the rule's severity,
its value or its site — all three were settled twice (ADR 0027,
`acceptance-bar.md` §3.2). It decides one thing the map had left open: whether
the warp, which is a CP-SAT solve, **posts** the floor it is known to miss.

`acceptance-bar.md` §11.1 refused a Proposal-level **screen** — a filter between
the warp and the solve — on three grounds, and explicitly did not decide this:

> ⚠️ That is a refusal of a filter, not of a third site. Posting this floor as a
> **constraint inside the warp solve** changes what the warp *emits* rather than
> what survives it, and this section does not decide it.

None of the three grounds transfers. A constraint does not refuse, it re-sizes;
the sound arithmetic form bounds a *screen* and not the warp's gap variables;
and the warp **is** the expensive step, so there is no cheaper half to skip.

## What was measured

`experiments/warp/floor_warp.py`, 381 paired (Brief, donor) cases at a 3 s cap,
four arms on one draw. The baseline is `both` — notch invariant (ADR 0020) plus
charged void (ADR 0028) — because that is the warp `proposer.md` §2.2.2 already
specifies, not `constrained_warp.py`'s `free` control.

**The baseline is worse than anyone had stated.**

| | `both`, as specified | floor posted hard |
|---|---:|---:|
| candidates served | 335 | 302 |
| **served candidates carrying a Room below a statutory floor** | **106 = 31,6 %** | **14 = 4,6 %** |
| shortfall depth, p50 · max | **1,356 m² · 8,444 m²** | 0,038 m² · 0,438 m² |
| INFEASIBLE | 46 = 12,1 % | 79 = 20,7 % |
| net candidate cost, paired | — | **33 = 8,66 %** |

Nearly **a third** of what the specified warp emits contains a Room below the
law, and the median miss is 1,4 m² with a tail to 8,4 — a bedroom delivered at
1,6 m² against a 10 m² floor. That is not a rounding population.

**Fidelity is unchanged at the median.** Paired on the 302 candidates both arms
serve: worst-room relative deviation p50 **0,1318 → 0,1352** (delta p50
**+0,0000**; 231 of 302 unchanged, 59 worse, 12 better), p90 0,5359 → 0,6065.
⚠️ The unpaired arms appear to show fidelity *improving*; that is survivorship —
the floor refuses high-deviation candidates — and the paired figure is the honest
one.

**The floor never fights a target.** `moved_rooms = 0` across every arm: under
`dim.market_default_area` every target already sits at or above its floor
(kitchen 9,0 against 8,0; PRIVATE 12,0 against 10,0; living 16,0 against 15/16),
which is §11.1 ground 2's own stated condition. The floor binds against what the
warp *achieves*, never against what the Brief *asks for*.

**And the decisive number is at the Brief, not the candidate.** §11.1's own
warning is that a per-candidate rate is not this quantity. At m = 8 over 199
Briefs:

| | `both` | floor posted hard |
|---|---:|---:|
| Briefs served at all | 96,48 % | 94,97 % |
| **Briefs served *cleanly*** — ≥ 1 candidate meeting every floor | **90,95 %** | **94,97 %** |
| clean share of those served | 94,27 % | **100 %** |
| pool depth p50 | 7 | 6 |

The floor costs **1,51 points** of service and buys **4,02 points** of *legal*
service. **Net +2,51 points**, and `clean_share_of_served` reaches **1.00** — at
Brief level the invariant is not merely likely, it holds.

Robust to the one ambiguity in the floor value: the corpus collapses
`{ROOM, BEDROOM, STUDIO}` and cannot say single from double, so both were run.
At `bedroom_single` 8,0 the baseline violates 25,1 % against 3,6 % constrained,
net cost 7,61 %. The decision does not turn on which limb is right.

## Decision

**The warp posts `dim.statutory_min_area` as a hard per-Room constraint, on the
bar plane, in a single pass. `INFEASIBLE` stays a refusal.**

Four parts, each of which was a live alternative:

1. **Hard, inside `warp_model`.** Not a screen, which §11.1 refused with
   published error rates and which this must not reintroduce by another door.
   `sum(part areas) >= floor` is **linear** on variables the model already
   builds — it adds no `AddMultiplicationEquality` at all, where ADR 0020's
   notch invariant costs one per notch cell. It is the cheapest constraint on
   this map and it was the largest unposted one.

2. **Per Room, never per part.** `dim.statutory_min_area`'s own statement says
   so and ADR 0014 binds it there. `area = sum(areas)` already exists; the
   ticket's worry that the warp's variables are per part was already discharged
   by the code.

3. **On the bar plane** — [[Space plane]], `CONTEXT.md`. The floor is a Space
   area and the objective runs on centreline parts; `part_targets_cells` already
   converts one to the other with `space_m2`'s own erosion, so the same call
   converts the floor and it lands on the plane the rule is stated on.
   **Deliberately not `solver.py`'s plane.** Mirroring the projection's
   four-side erosion would have made the warp agree with the projection by
   copying a defect `acceptance-bar.md` §11.1 has already published, so that two
   components are wrong together. A floor is a legal quantity; it is posted on
   the plane the law is measured on, and the projection's disagreement stays
   visible where it can be priced.

4. **Single pass. No unconstrained fallback.** A two-pass shape — post the
   floor, re-warp without it on INFEASIBLE — was measured and **refused**. It
   recovers every lost candidate and takes violations 31,6 % → 14,0 % with zero
   candidates lost, which looks strictly dominant and is not: **every pass-2
   candidate violates by construction**, because it is precisely the one the
   floor refused. Two-pass buys a *rate* and buys **no invariant** — downstream
   still cannot say "a Proposal meets its statutory floors", so §2.2.9 and §11.1
   must still reason about starved Proposals and nothing simplifies. Single pass
   buys the invariant, and at Brief level it is **net positive** anyway. The
   candidates it declines are declined the way the warp already declines at the
   ergonomic floor (ADR 0005) — retrieval draws the next pool member, which is
   what pool depth is for and what `POOL_DEPTH_ON_STARVATION = 16` was set past
   the knee to fund.

## Why this is ADR 0027 applied and not a new position

ADR 0027 refused three ways of paying the price — soft, drop the kitchen limb,
lower the value — and sent the cost to the producing stage. Read against it:

- The **warp** is that stage, named in the ADR's own text.
- The payment is not a weakening: the rule's severity, value, site and limb set
  are all untouched.
- The market argument is unchanged and is the reason it is worth paying.
  `competitive-landscape.md` §5.2: **code compliance is claimed by six vendors
  and implemented by approximately zero** — every one either pushes authoring
  onto the user or disclaims in the terms. And `floorplan-generation-stack.md`'s
  own recommended architecture, step 3, is *"CP-SAT pass that enforces minimum
  dimensions… the RLVR paper's verifiable-reward idea moved to inference time"*.
  The warp is a CP-SAT pass and it was the one stage not doing it. RLVR
  (`2605.14117`) puts a hard verifier in the training loop; DPLAN
  (`2606.21159`) constructs feasible so constraints hold by construction.
  Neither gates candidates downstream, and neither did this.

C8 is untouched: nothing here is *claimed*. A failing Plan is discarded and
never shown, no surface text names a law, and the differentiator stays real and
unadvertised.

## Consequences

1. **A Proposal from source A now carries an invariant it did not have**: every
   Room meets its [[Hard area floor]]'s statutory limb on the bar plane, or the
   warp returned INFEASIBLE. `proposer.md` §2.2.2 gains it as decision 7 and
   §2.2.9's starvation account is now about the residual, not the population.

2. **§11.1's three-step escalation is unchanged and its base rate moves.**
   Starvation is still declared on the Plan, the screen is still refused, and the
   steps still run in order. What changes is that step 1 now deepens a pool whose
   members are floor-clean, so what it is buying is different — and 18,3 %
   Proposal-level starvation is no longer the number to quote at it.

3. ⚠️ **A residual of 4,6 % survives at candidate level and it is an estimate
   error, not a modelling one.** The posted floor converts a Space area to cells
   using the erosion overhead read at the **affine seed**, and the shape moves
   under the warp. Residual shortfalls run p50 0,038 m², max 0,438 — grid dust
   against the baseline's 1,356 / 8,444 — and at m = 8 they vanish at Brief
   level. Owed: either inflate the posted floor by the p90 estimate error, or
   re-post at the solved shape and re-solve. It is a second-order fix and it is
   ticketed, not hidden.

4. ⚠️ **The projection discards about one in five of the guarantees the warp now
   pays for.** 59 of 302 floor-clean candidates (19,5 %) fail their floor on
   `solver.py`'s plane. §11.1 already recorded that gap and deferred it —
   *"costs yield and never admits a Plan that should have been refused"* — on a
   cost basis where no stage was paying to clear the floor. A stage now is. That
   does **not** re-open the deferral; it re-prices it, and the price is
   ticketed.

⚠️ **Amended 2026-08-30 by [ADR 0034](0034-an-az-cell-declares-what-it-measures-and-a-part-may-only-floor.md).**
The `KITCHEN_DINING` limb this ADR posts is **entailed, not transcribed**: AzDTN
cl. 5.7 floors the kitchen *zone* inside the room at 6 m² and publishes no
whole-room figure at all — searched exhaustively, `az-kitchen-diner-whole-room.md`.
6,0 stays, because the room contains the zone and the bound is sound. Two claims
above are narrowed by it. **"The floor never fights a target" held for this limb
only at equality** — floor 6,0 against target 6,0, zero headroom — and the target
is now 18,8, so it has real headroom for the first time. And `moved_rooms = 0`
was measured with `MARKET["KITCHEN_DINING"] = 6.0`; that constant is handed on,
which **raises** the margin and cannot invert the result. The decision, the
severity, the site and the other limbs are untouched.

5. **The floor table is a hand transcription and is now load-bearing.**
   `absolute_area.STAT_FLOOR` was copied from `room-constraints.json` with
   nothing binding the two. That was tolerable while it only measured; it
   constrains geometry now, and a drift would size rooms to a floor no regulator
   wrote — the C8 failure from the inside. `floor_warp._check_floor_transcription`
   asserts all six values on import. **That is a guard, not the fix**: the table
   should be *read* from the JSON, and the refactor is ticketed.

6. **This is the shape for the next constraint of its class.** Where a hard rule
   is `site: both` and a *proposing* stage is a solve, the question is not
   whether to gate its output but whether the stage can post the rule itself.
   Two have now been answered this way — ADR 0028's void charge and this — and
   both were linear or near-linear on variables that already existed.
