---
id: 64
title: Should the warp post the statutory floor
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - experiments/warp/
  - docs/spec/proposer.md
  - docs/spec/acceptance-bar.md
---

# Should the warp post the statutory floor

## Question

**`dim.statutory_min_area` is `site: both` and the warp is neither site.**
*Can a starved candidate be refused before the solve* refused a Proposal-level
**screen** — a filter between the warp and the solve — on three grounds that all
hold. It did **not** decide the different thing: posting the floor as a hard
**constraint inside the warp's own CP-SAT model**, which changes what the warp
*emits* rather than what survives it.

The two are not the same object and only one of the three grounds transfers.

| ground the screen was refused on | does it transfer to a constraint? |
|---|---|
| 82,0 % of what it refuses the solve serves | **no** — a constraint does not refuse, it re-sizes |
| the sound form (Σ floors vs the box) never fires | **no** — that bounds a *screen*, not the warp's gap variables |
| it sits after the expensive step | **no** — the warp *is* the expensive step |

**What it could buy, and the number is small but sits in the worst place.** The
projection refuses **5,1 %** of warped candidates and **every one of them is the
floor** — 14 of 14 re-solve feasible with the statutory limb dropped. By band
that is **2,0 %** at 4–6 rooms and **8,8 % at 7–10**, which is the band ADR 0013
already calls tight, where §7.6 measured that pool depth buys **nothing at all**,
and where the projection's rescue rate is weakest (73,1 % against 91,7 %). It is
the one place on this map where more search does not help and a better-sized
candidate might.

**What it would cost is unmeasured and the machinery exists.** `fit_warp.py`
posts `MIN_SIDE` — a clear **width** floor — hard, plus `dim.aspect_ratio_hard`;
area enters only as the weighted deviation objective. Adding a per-Room area
floor is the same class of move, and `constrained_warp.py` is the rig that prices
exactly this shape: 57 measured ADR 0020's notch invariant and ADR 0028's void
charge posted **in** the solve at **2,6 %** of candidates, rising to 8,8 % if the
invariant is held exactly.

**What has to be decided:**

1. **Whether the warp's own INFEASIBLE rate rises by more than the 5,1 % it
   removes.** The warp already declines candidates at the ergonomic floor
   (`fit_warp` returns INFEASIBLE and retrieval falls to source B, ADR 0005). A
   floor it cannot meet turns a *rescuable* candidate into a refused one, which
   is the screen's failure mode arriving by another door. Measured against
   `project_join.py`'s own arm, not argued.
2. **Whether it damages fidelity where it does not refuse.** The objective is
   worst-room relative deviation plus the weighted sum; a hard area floor
   competes with both. 57's precedent is the shape to expect — the notch
   constraint took worst-room deviation 0.139 → 0.226 when held exactly.
3. **Which floor, and on which plane.** `max(ergonomic, statutory)` is the Room's
   floor, and ADR 0014 binds **area per Room** while the warp's variables are
   per **part**. And ⚠️ the two rigs measure area on planes **3,9 %** apart —
   posting the bar's plane in a warp whose objective is measured on the solver's
   would fit the constraint to the wrong quantity.
4. **What the market does, per the standing instruction.** This is the direction
   the reviewed literature actually points: RLVR (`2605.14117`) puts a hard
   verifier in the training loop and DPLAN (`2606.21159`) constructs feasible so
   constraints hold by construction. Neither gates candidates downstream. That is
   a prior *for* this ticket and it is the half of the market reading that
   *Can a starved candidate be refused before the solve* recorded and did not act
   on.

## What this is not

Not a re-opening of the screen — that is refused with published error rates and
this ticket must not reintroduce it as a constraint's side effect. Not a severity
question: `dim.statutory_min_area` stays **hard**, decided twice (ADR 0027,
`acceptance-bar.md` §3.2). Not the Plan-level best-of-*m* curve, which is
`proposer.md` §2.2.9's owed measurement and is about depth rather than sizing.

## Raised by

*Can a starved candidate be refused before the solve* (2026-08-29), which refused
the filter and found that the only remaining candidate placement is the one step
it never measured.

## Resolution

**Yes — hard, per Room, on the bar plane, single pass. ADR 0033.** And the
question was less open than the ticket framed it: ADR 0027 had already decided
the *whether*. Its generalised position is *"the cost is a debt owed by whichever
stage produced the failure… the stage that misses it owns the miss"*, and its
**Where the cost goes instead** section names the stage — *"what remains is the
warp's per-room distribution"*. This ticket is that debt coming due, so what was
actually open was the **form**, and four parts of the form were live.

### The baseline was worse than any page on this map stated

`experiments/warp/floor_warp.py`, 381 paired (Brief, donor) cases, 3 s cap, four
arms on one draw. Baseline is `both` — notch invariant plus charged void — per
item 6 of the round: that is the warp `proposer.md` §2.2.2 **specifies**, and
pricing against `constrained_warp.py`'s `free` control would have reported the
floor cheaper than production will ever see it.

| | `both`, as specified | floor posted |
|---|---:|---:|
| served candidates | 335 | 302 |
| **carrying a Room below a statutory floor** | **106 = 31,6 %** | **14 = 4,6 %** |
| shortfall depth p50 · max | **1,356 m² · 8,444 m²** | 0,038 m² · 0,438 m² |
| INFEASIBLE | 46 = 12,1 % | 79 = 20,7 % |
| net paired candidate cost | — | **33 = 8,66 %** |

Nearly a third of what the specified warp emits is below the law, and the median
miss is 1,4 m² with a tail to 8,4 — a bedroom at 1,6 m² against a floor of 10.
The 5,1 % projection-INFEASIBLE rate this ticket was raised on is the *visible*
part of that; the rest is repaired silently by the projection, which is why
nobody had seen it.

### Item 1 — the INFEASIBLE rate rises, and less than the number it removes

12,1 % → 20,7 %, net **8,66 %** paired. But the ticket asked the wrong comparison
and §11.1 says why in its own text: *a per-candidate rate is not this number*. At
Brief level, m = 8 over 199 Briefs:

| | `both` | floor posted |
|---|---:|---:|
| Briefs served at all | 96,48 % | 94,97 % |
| **Briefs served *cleanly*** | **90,95 %** | **94,97 %** |
| clean share of served | 94,27 % | **100 %** |
| pool depth p50 | 7 | 6 |

**The floor costs 1,51 points of service and buys 4,02 points of legal service —
net +2,51.** The pool absorbs the candidate cost, which is what pool depth is for
and what `POOL_DEPTH_ON_STARVATION = 16` was set past the knee to fund. Measured
at m = 8; production median pool is 86,6 at 4–6 and 58,7 at 7–10, so this is an
upper bound on the loss.

### Item 2 — it does not damage fidelity, and the obvious reading is survivorship

Paired on the 302 candidates both arms serve: worst-room relative deviation p50
**0,1318 → 0,1352**, paired delta p50 **+0,0000** — 231 of 302 unchanged, 59
worse, 12 better — p90 0,5359 → 0,6065 (+0,085). ⚠️ Read unpaired, the arms
appear to show fidelity *improving* (0,1710 → 0,1352); that is the floor refusing
high-deviation candidates and it must not be quoted. 57's precedent was the shape
to expect and the floor is far cheaper than it: the notch invariant took
worst-room deviation 0,139 → 0,226 held exactly.

**And the floor never fights a target.** `moved_rooms = 0` across every arm:
under `dim.market_default_area` every target already sits at or above its floor,
which is §11.1 ground 2's own condition. The constraint binds against what the
warp *achieves*, never against what the Brief *asks for* — so the conflict this
ticket feared between a hard floor and the deviation objective does not exist in
the shipped regime. ⚠️ It would exist for a Brief stating a target *below* a
statutory floor, which `brief.md` §9.4 bounds 1 and 3 still permit; that bound is
`brief.md`'s and unclaimed, and it is now fog on the map.

### Item 3 — the plane, and this is where the ticket's framing was inverted

Two of the ticket's three worries here were already discharged by the code:
`dim.statutory_min_area`'s own statement says it binds **per Room, not per part**,
and `fit_warp.warp_model` already builds `area = sum(areas)` as a Room-level
variable. The constraint is one `m.Add` on a variable that exists, and it is
**linear** — no `AddMultiplicationEquality` at all, where ADR 0020's notch
invariant costs one per notch cell. It is the cheapest constraint on this map and
it was the largest unposted one.

The third worry — *"the two rigs measure area on planes 3,9 % apart"* — was real,
and the ticket's own instinct about it was backwards. Mirroring `solver.py`'s
four-side erosion would make the warp agree with the projection **by copying a
defect §11.1 has already published**, so two components would be wrong together
and the defect would become unfindable. Refused. The floor is posted on the
**bar plane**, via `part_targets_cells` — the same converter the targets already
use, so the floor and the objective are stated on one plane by construction.
`CONTEXT.md` gains **Space plane** for the distinction, which had no name and has
already produced one shipped defect.

### Item 4 — the market, and it points harder than the ticket said

`competitive-landscape.md` §5.2, its own heading: **code compliance is claimed by
six vendors and implemented by approximately zero** — every one either pushes the
authoring onto the user or disclaims it in the terms. And this repo's own
`floorplan-generation-stack.md` prescribes the answer at step 3: *"CP-SAT pass
that enforces minimum dimensions… the RLVR paper's verifiable-reward idea moved
to inference time"*. The warp **is** a CP-SAT pass and it was the one stage not
doing it. RLVR (`2605.14117`) verifies in the loop; DPLAN (`2606.21159`)
constructs feasible. The ticket called this *"a prior for"*; it is stronger — it
is the architecture this map's own research already recommended.

### The one thing the ticket did not name, and it was the real decision

**A two-pass warp** — post the floor, re-warp without it on INFEASIBLE — was
measured and **refused**, and refusing it was the hardest call here because it
looks strictly dominant:

| shape | served | violations | lost |
|---|---:|---:|---:|
| baseline `both` | 335 | 106 = 31,6 % | — |
| two-pass | 335 | 47 = 14,0 % | **0** |
| single pass | 302 | **14 = 4,6 %** | 33 = 9,9 % |

Zero candidates lost, violations more than halved. The refusal is that **every
pass-2 candidate violates by construction** — it is precisely the candidate the
floor refused — so two-pass buys a *rate* and buys **no invariant**. §2.2.9 and
§11.1 would still have to reason about starved Proposals; nothing downstream
could say *"a Proposal meets its statutory floors"*; and under ADR 0027 the 1,51
Brief-points it recovers are recovered by serving a plan below the law, which is
the exact trade ADR 0027 exists to refuse. A guarantee that holds except when it
doesn't is not a guarantee.

⚠️ **This reverses the recommendation the round opened with.** Q4 recommended
two-pass on a dominance argument made before the paired and Brief-level numbers
existed; the Brief-level arm is what killed it, because single pass turned out to
be net **positive** and the fallback's only remaining purchase was illegal plans.

### Pre-committed decision rule, and where it was mis-specified

Q5 fixed two thresholds in advance. Deviation: *take the floor if worst-room p50
rises by less than the notch constraint's +0,087* — paired rise is **+0,0000**,
passes with room. Second-pass rate: *under 5 %* — it fires at **9,85 %**, which
**fails**. That threshold was mis-specified: it was written as though firing were
a loss, and under the two-pass shape firing loses nothing. It is void because
two-pass is refused outright, not because the number came out inconvenient — and
the number is recorded here rather than quietly dropped.

### What this cost, beyond the decision

- ⚠️ **A 4,6 % residual, and it is an estimate error.** The posted floor converts
  a Space area to cells with the erosion overhead read at the **affine seed**,
  and the shape moves under the warp. Residuals are p50 **0,038 m²**, max
  **0,438** — grid dust against the baseline's 1,356 / 8,444 — and at m = 8 they
  vanish at Brief level (`clean_share_of_served` = 1.00). Ticketed.
- ⚠️ **The projection discards about one in five of the guarantees the warp now
  pays for**: 59 of 302 floor-clean candidates (19,5 %) fail on the solver plane.
  §11.1 deferred that gap when no stage was paying for the guarantee. Ticketed as
  a **re-pricing**, explicitly not a re-opening.
- **A transcription became load-bearing.** `absolute_area.STAT_FLOOR` is a hand
  copy of `room-constraints.json` with nothing binding the two — tolerable while
  it measured, not while it constrains geometry, because a drift sizes rooms to a
  floor no regulator wrote. `floor_warp._check_floor_transcription` asserts all
  six values on import. That is a guard, not the fix; the read-from-JSON refactor
  is ticketed.

### Robustness

Run at both limbs of the one genuine ambiguity — the corpus collapses
`{ROOM, BEDROOM, STUDIO}` and cannot say single from double. At `bedroom_single`
8,0: baseline 25,1 % violating against 3,6 % constrained, net cost 7,61 %. The
decision does not turn on which limb is right, so Q3's *"report both, headline
10,0"* stands and neither number is doing work the other could not.

### Assets

- `experiments/warp/floor_warp.py` — the four arms, the Brief-level pool arm, and
  the transcription gate.
- `experiments/warp/constrained_warp.py` — `warp_model_constrained` gains one
  optional `area_floor_cells` parameter, defaulting to `None`; with it unset the
  four published arms build a bit-identical model.
- `out/floor_warp.json`, `out/floor_warp_lenient.json`, `out/floor_warp_pool8.json`.
- `docs/adr/0033-the-warp-posts-the-statutory-floor-and-pays-adr-0027s-debt.md`.
- `CONTEXT.md` — **Space plane**, declared on resolution while unclaimed.
