---
id: 59
title: Can a starved candidate be refused before the solve
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - docs/spec/proposer.md
  - docs/spec/acceptance-bar.md
  - experiments/warp/
---

# Can a starved candidate be refused before the solve

## Question

**Every starvation figure on this map is measured on the Proposal, and the rule
that produces it binds on the Plan.** `dim.statutory_min_area` is `site: both` —
the solver *posts* it and the validator *evaluates* it — but *What best-of-pool is
worth at production pool depth* measured 3,6 % and its whole best-of-*m* curve on
the **warped rectangles**, before any projection solve. **No warped Proposal on
this map has ever been put through the solver**: `fit_warp.py` imports
`experiments/solver-toy/` for its relation extractor and nothing else, and
`solver-toy`'s own Envelopes are real dwellings, never warped candidates.

The solver has freedom the warp does not — exact tiling is soft (C10), so it can
move floor between Rooms the warp sized — so Plan-level starvation could fall
either side of the Proposal-level number.

**This is also the whole of what deepening costs**, which is why the two questions
are one ticket. 57 measured the parts:

| | cost per extra pool member |
|---|---|
| warp | **0.79 s** (bucket) / **1.66 s** (gated fixed point) |
| projection solve, real boundary | p50 **10,11 s**, p90 at the 15 s cap |

79 extra members is ~60–130 s of warp and **13–20 minutes** of solve, and it falls
entirely on the starving Brief. So `acceptance-bar.md` §11.1 step 1 is affordable
if and only if a candidate can be refused on its **Proposal**, and unaffordable
otherwise — at any depth, not just at 87.

**What has to be decided:**

1. **Whether a Proposal-level check is sound.** A cheap screen that refuses
   candidates the solver would have rescued is throwing away yield to save time,
   and one that passes candidates the solver then fails has bought nothing. Which
   error is acceptable, and at what rate.
2. **Whether the screen is the same predicate.** `dim.statutory_min_area` is
   already `both`, so the solver posts it — the question is whether the *warp*
   should post it too, making it a third site, or whether a separate cheaper
   Proposal check is the right object.
3. **What §11.1 step 1 is then allowed to claim.** 57 showed it buys ~1 point,
   flat by m = 12, and cannot go below **π = 2,8 %** — so the step is a config
   value (a pool-depth constant), not a re-shape of the proposer service. That
   constant cannot be chosen without (1) and (2).

**Graduated from *What deepening a starved Brief's pool costs the runtime***,
whose own stated branch condition — *"if the curve is flat by m = 12, this is a
config value"* — 57 satisfied.

## Deliverable

Either a specified Proposal-level screen with its two error rates and the pool
depth constant it makes affordable, or a finding that the check must wait for the
solve, in which case §11.1 step 1's claim shrinks to whatever fits one 15 s budget
and steps 2 and 3 carry the rest.

## Resolution

**No Proposal-level screen. `dim.statutory_min_area` stays at two sites — and the
question was mis-posed in a way the measurement, not the argument, had to
correct.** `experiments/warp/project_join.py`, `proposer.md` **§2.2.9**,
`acceptance-bar.md` **§11.1**.

### The join

The ticket's premise was right: nothing on this map had put a warped Proposal
through `project()`. It does now. One warped candidate becomes one solver-toy
`Brief` plus one `Proposal`; the Envelope is the ADR 0020 box the warp solved
into, with every uncovered frame cell posted as a notch, so **the candidate is its
own witness** — the guarantee Parts I–III have and 58's real arm could not get.
`--selftest` asserts `warp_geom == absolute_area.run_one` per-room exactly, so
this cannot drift into a second warp. Shipped config, `t_int` **150** rather than
100, because the warp measures Space at 150 and a join solving at 100 compares
two planes.

**291 candidates, 273 reaching the solve, 61 Briefs**, `ringmarket` semantics
(targets on `dim.market_default_area`, the ring held) — §3.2's own population.
Plus a 34-candidate k ≤ 2 check arm through `room-rectangles/solver_parts.py`.

### 1. A returned Plan is never starved, so the ticket's two error modes are not the ones it named

`dim.statutory_min_area` is `site: both`: the projection **posts** it. A Plan that
comes back has already met every floor — `served_but_starved` is **0** on every
run, which is the rig's own assertion that the rule reaches the model. Plan-level
starvation appears only as INFEASIBLE. So decision 1's "which error is
acceptable" is not a choice between two kinds of starvation; it is **yield loss
against one solve slot**, and the solve slot turned out to be the cheap thing.

### 2. The screen is unsound at 82 %, and the mechanism is already on the map

| | |
|---|---:|
| starved on the warped rectangles | 18,3 % |
| **of those, served by the projection** | **82,0 %** — 41 of 50, 95 % CI [71,4–92,6] |
| the same, 4–6 rooms · 7–10 rooms | 91,7 % · 73,1 % |
| the same, k ≤ 2 arm | **88,9 %** — 8 of 9 |
| Proposal-clear then refused | 2,2 % — 5 of 223 |
| INFEASIBLE, all · 4–6 · 7–10 | 5,1 % · 2,0 % · **8,8 %** |
| INFEASIBLE re-solved with the statutory limb dropped | **14 of 14 feasible** |
| Σ Space, Plan against Proposal | p50 **0,0000** |

**The solve does not create floor, it moves it.** §2.2.2 minimises worst-room
*relative* deviation and prices every Room symmetrically; the projection posts the
floors hard and minimises corner displacement, so it shrinks a Room comfortably
above its floor to feed the one below — and the median starved candidate has
exactly **one** Room under its floor. `acceptance-bar.md` §3.2 argued from this
exact shape when it set bound 9 to `warn`; this is that sentence measured.

⚠️ **The k ≤ 2 arm matters more than its n suggests.** `solver_parts.py` binds the
Room's `min_area` on the **primary part** where ADR 0014 binds it per Room —
strictly stricter — so it can only *understate* the rescue rate. It returns a
*higher* one. The k = 1 restriction is not manufacturing the result.

### 3. The only sound screen never fires, and cannot

A screen may refuse only what the projection provably cannot serve. The
projection can move floor between Rooms, so the sole cheap relaxation is
arithmetic: Σ hard floors against **this candidate's own** derived box — which is
a per-candidate test the parse-time bounds cannot make, since ADR 0020 derives
the box per candidate. Measured over 273: p50 **0,566**, p90 0,688, **max 0,736**.
Zero firings, and it cannot fire: `box = target_area × (1 + f) / (1 − s)` and
every target sits at or above its floor under `market_default`.

### 4. Any screen sits on the wrong side of the expensive step

**The projection costs less than the warp that feeds it.** Wall p50 **0,145 s**
against a warp p50 of **0,674**; means 1,05 and 1,12; p90 0,98 and 2,71; 4,4 % of
solves reach the 15 s cap. A gate between the two skips the cheaper half. That
alone would settle decision 2 without (2) or (3).

Why it is that cheap: a warped candidate arrives as an **exact tiling** of its own
Envelope with τ = 4 relations fixed from it, so the projection is a repair rather
than a search. ⚠️ Not comparable with Part V's 10,11 s (a real boundary with a
generated truth) or with ADR 0029's timings (`t_int` 100).

### 5. Decision 3 — what §11.1 step 1 may claim

**`POOL_DEPTH_ON_STARVATION = 16`**, past 57's knee with margin, and the step is a
**config value** rather than a re-shape of the proposer service. It is
comfortably affordable and the ticket's own arithmetic was off by an order of
magnitude: one extra pool member costs a **mean 2,17 s** (warp 1,12 + projection
1,05), so eight more members on a starving Brief is ~17 s, on the ~3 % of Briefs
that reach the step — not the 13–20 minutes this ticket priced from 58's
**real-boundary** arm, which no candidate ever presents.

**But the ordering matters more than the constant.** §11.1 now declares
starvation **on the Plan, never on the Proposal**. Read at the Plan on the same
Briefs, Brief-level starvation is **3,28 % → 1,64 %** — worth more than deepening,
which 57 measured at one point. ⚠️ **That halving is 61 Briefs and 2 starved
cases**: a direction, not a number, and the Plan-level twin of §7.6's curve is
what this ticket hands on.

### 6. What the market does

Nothing in the reviewed literature screens candidates on an area tolerance. The
two answers that exist both move the constraint **into** generation — RLVR
(`2605.14117`) puts a hard verifier in the training loop, DPLAN (`2606.21159`)
constructs feasible so "constraints are satisfied by construction". That is a
prior *for* posting the floor in the warp and *against* a downstream gate, and it
agrees with the decision on the gate. Posting it in the warp as a third site is
left open and bounded: it could only buy the 5,1 % INFEASIBLE rate, it is a
`constrained_warp.py` job beside the two constraints 57 already priced at 2,6 %,
and it is not worth a ticket at that size.

### 7. Two findings that were not the question

⚠️ **The projection reads a perimeter Room 3,9 % smaller than the bar does.**
`solver.py` binds H4 on `(250w − t)(250h − t)`, eroding all four sides; ADR 0001
does not erode at the Envelope boundary, because the tiling edge there already
sits at exterior-inner-face + `t_int/2`. On a 250 mm grid the 75 mm ring is
unrepresentable — `brief.md` §5.3's third quantity — so it is **structural**: the
projection is strictly stricter than the rule it posts. Gap p50 **3,92 %** per
Room (p90 7,24); **27 of 1 786 Rooms (1,51 %)** clear their floor on the bar's
plane and fail on the solver's; **19 candidates** are starved on the solver's
plane alone, a superset of the 5 false passes — so **the false-pass column is the
plane, not the engine**. This is ticket 56's ring, re-found where it cannot be
removed. It costs yield and never admits a Plan that should have been refused.

⚠️ **`solver-toy/solver.py` has no ADR 0014.** `project()` gives a Room exactly
one rectangle; the k ≤ 2 projection lives in `experiments/room-rectangles/`, and
its Design A binds area per **part** where ADR 0014 binds it per **Room**. Two
shipped decisions and one rig, and the rig implements neither cleanly. Recorded
for whoever next opens either directory; nothing here edits them.

⚠️ **The toy's H8 / H9 / H10 could not be posted hard and the reason is 58's.**
H9 wants one plumbing cluster where `wet.plumbing_group_count` has been **3**
since ADR 0023; H10 routes around a `PRIVATE` set containing the wet types where
`circ.no_private_transit` is about sleeping rooms; H8 binds off an exposure preset
a warped candidate does not carry. Of 273 warped candidates only **54** satisfy the
toy's full hard set — H9 129 failures, H10 104, H8 75 — and **none of those three
counts is `room-constraints.json`'s cost.** Computed with no solve, from the
witness.

### Deliverable, against the ticket's own wording

*"Either a specified Proposal-level screen with its two error rates and the pool
depth constant it makes affordable, or a finding that the check must wait for the
solve."* — **The second, and the two error rates are published anyway** (82,0 %
false refusal, 2,2 % false pass, the latter entirely the plane gap), because they
are what refuses the screen. §11.1 step 1 keeps its full claim: it is affordable
at any depth the curve justifies, and it is affordable **because the solve is
cheap**, not because a screen made it so.
