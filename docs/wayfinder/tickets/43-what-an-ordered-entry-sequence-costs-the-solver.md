---
id: 43
title: What an ordered entry sequence costs the solver
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
blocked_by: []
writes:
  - experiments/solver-toy/                # held, never written -- no solve was run
  - docs/research/solver-formulation.md
  - docs/research/zoning.md                # declared on resolution, unclaimed
  - experiments/zoning/                    # declared on resolution, unclaimed
---

# What an ordered entry sequence costs the solver

## Question

*The Proposal cannot express zoning* named four properties a pairwise contract
cannot carry, and found three of them already reachable: sleeping-group
clustering is the shipped flow routine on a third node set, facade allocation is
a soft term over the Envelope's typed edge ring, and the front door opening onto
circulation is one predicate about one Space.

**The fourth is not, and it is the one this ticket prices.** *Entry → hall →
living* is an **order** on the circulation graph, and the single-commodity flow
encoding does not produce one. Flow gives **reachability**: room *r* receives its
unit, therefore you can get there. It says nothing about *how far along* the walk
*r* sits, so no constraint written over it can distinguish a plan whose front
door opens into a hall that opens into a living room from one whose front door
opens into a living room with a hall behind it.

The natural encoding is a **per-Room hop-count integer** — `d_entry = 0`, and for
every other Room `d_r = min over neighbours(d_v + 1)` posted as a disjunction over
the door literals `door_ij` the flow already reifies. That is a new integer per
Room and a new disjunction per pair, on a formulation whose H8 note specifically
records that it needs **"no auxiliary integers"**.

**Nothing on this map has ever measured what that costs**, and there are three
reasons to think the cost is not small:

1. Every solver number on the map was fitted **without** these variables, at
   15 s and τ = 4 — and *Solver timing variance sweep* found v1 **sits on the
   edge of the feasibility cliff, not below it**. A formulation that adds
   variables to a model already at its limit is not obviously affordable.
2. *Ergonomic minima* and *Whether a Room may be more than one rectangle*
   between them establish that **no solver measurement on this map covers the
   bottom half of C13's own 3–10 band** — so the regime where this would be added
   is also the regime nobody has measured.
3. ADR 0014 has just taken the variable count to **1.2–1.7×** the k = 1 control
   for the Rooms the Proposal names as two-part. Hop counts land on top of that,
   not instead of it.

**What has to be decided:**

1. **What the ordering property actually is**, stated precisely enough to post.
   "Entry → hall → living" is a slogan; candidates include *the entry Space's
   hop-1 neighbourhood contains no habitable Room*, *every habitable Room is at
   hop ≥ 2*, and a genuine total order over a named sequence. They cost
   differently and only the last needs hop counts at all — the first two may
   collapse back into predicates over the existing graph, which would settle this
   ticket without touching the solver.
2. **What it costs**, if hop counts really are needed: variables, solve time to
   first VALID, and the feasibility rate — measured the way ticket 15 measured
   the rest, across room counts and at **corpus-median** exposure, not the
   100 %-exterior detached case that confounded the earlier sweeps.
3. **Whether the corpus supports the rule you would post.** `experiments/zoning/`
   already has hop distance from the entrance per Room class over 2 500
   dwellings — social 1.21, private 1.66, circulation 0.32 — and the day/night
   gradient there proved **directional but not assertable** (private is *nearer*
   the door than social in 16.1 % of real homes). Check the ordering candidate
   against the same data before pricing it: a rule real dwellings break one time
   in six is not worth new integers.
4. **Whether it is worth it at all**, against the alternative that the three
   cheap properties already shipped capture most of what "the plan reads as
   designed" means. That is a judgement, and it should be made *after* 1–3, not
   before.

**Blocked by *The solver has only ever seen guillotine layouts*.** Both tickets
write `experiments/solver-toy/`, and 29 changes the ground truth every timing on
this map was measured against. Pricing a new encoding on a rig that is about to
be re-based measures the rig. Settle the ground truth first — the same argument
that blocked *The Proposal cannot express zoning* on ADR 0014.

**Deliverable.** Either a precise statement of the ordering property and its
measured cost, or — the outcome to be genuinely open to — a finding that the
property collapses into predicates the existing graph already supports, and no
new solver machinery is owed.

## Unblocked by *The solver has only ever seen guillotine layouts* (ADR 0019)

**The rig is not moving, so pricing an encoding against it now measures the
encoding.** That was the whole reason for the block: 29 was expected to re-base
the ground truth every timing on this map was measured against. It re-based
nothing — 4 discordant slots each way, McNemar p = 1.00, and zero discordant at
8–16 rooms — so **15 s, τ = 4 and Part II's percentiles all stand at their
published values** and are the correct baseline to price a per-Room hop-count
integer against.

Three things 29 leaves you that change how to run this:

1. **`experiments/solver-toy/` is yours alone now.** 29 is closed. It added
   `pinwheel.py`, `sweep_ng.py`, `report_ng.py`, `relation_margins.py`,
   `t_int_arithmetic.py`, `pinwheel_area_premium.py` and `corpus_guillotine.py`,
   and deliberately left `_guillotine` the **default** — do not re-base it.
   `sweep_ng.py`'s paired-arm shape is reusable as-is if you want to price the
   encoding on both cut structures rather than one.
2. **A hop-count integer should be priced on the non-guillotine arm too**, and
   cheaply — it is one extra value of `truth` in the same suite. 29's own result
   makes that worth doing rather than optional: the arms agree on *survivor rate*
   but the pinwheel arm reaches INFEASIBLE **significantly less often** (17
   against 2, p = 0.0007), so a new hard integer's effect on infeasibility is
   exactly the axis where the two arms are known to differ.
3. ⚠️ **A fixture defect you will hit at small `n`.** `AREA_PER_ROOM_M2` = 9.65 is
   below what the placeholder table needs at 7 and 8 rooms in **either** arm —
   both need 11.58. Below 7 rooms this Envelope family has no non-guillotine
   tiling at all. If you sweep low room counts, that is the harness talking, not
   your encoding.

---

## Resolution

**No new solver machinery is owed, and the property collapses a *third* way — not
the way item 1 predicted.** `docs/research/zoning.md` §6 and **D10**;
`solver-formulation.md` **Part VI**; three probes in `experiments/zoning/`, all
reading the existing `zoning.json` / `zoning2.json`, **no corpus pass and no
solve**.

Item 3 was taken first, as the ticket directed, and it made item 2 moot: the
rules were refuted before the encoding was reached, so **no cost figure exists
and none should be quoted**.

### 1. What the ordering property actually is (item 1)

The three candidates, over the same 2 500 Swiss dwellings, on the same plane the
solver constrains — `dist` is BFS over `measure_swiss.contact_graph` (τ 0.30 m,
door run 1.00 m), which is exactly what `solver-formulation.md` reifies as
`door_ij` (*"true exactly when the two rooms share a wall segment at least a
door's width long"*):

| candidate | holds | needs `d_r`? |
|---|---:|---|
| **R1** no otaq at hop 1 | **9,6 %** | no — one existing literal |
| **R1h** no habitable Room at hop 1 | **1,8 %** | no |
| **R2** every otaq at hop ≥ 2 | **7,7 %** | no |
| **R2h** every habitable Room at hop ≥ 2 | **1,6 %** | no |
| **R5** every private Room at hop ≥ 2 | **25,1 %** | no |
| **R3** circulation nearer than any social Room | 96,8 %† | no |
| **R4** nearest private ≥ nearest social | **82,6 %**† | **yes** |
| **R6** strict entry < social < private | **26,9 %**† | **yes** |

† on the population holding both class sets (68–70 %).

**The ticket's own first two candidates are the negation of the slogan they were
written to encode.** The nearest social Room sits at hop **1** in **73,4 %** of
dwellings — the modal case by a factor of four. *Entry → hall → living* **means
the living room is at hop 1**; R1 and R2 forbid precisely that. Stated
positively, the slogan already holds on **72,9 %** of dwellings with a social
Room, with no rule posted by anyone. Nor is there a buffer to assert: what sits
at hop 1 is private **33,9 %**, wet **28,1 %**, kitchen **16,8 %**, social
**15,2 %**.

**R3 is a construction, not a predicate, and it is already shipped.**
`openings.md` §7 — *"The hall exists to be the room the front door opens into"* —
hosts the primary entrance on the invented `hall`, and a candidate whose hall
misses an `entrance_side` edge *"is already dead at `entry.exists`, before this
rule is consulted"*. The engine's rate is **100 % by construction** against the
corpus's 93,2 %. R3 carries no information beyond that.

### 2. What it costs (item 2) — deliberately not measured

**Moot, and the reason is worth keeping.** Every candidate that needed the
integers was refused on the corpus first, so pricing the encoding would have
measured the rig rather than the encoding. No solve was run and **no figure
exists** — do not infer one from ADR 0014's 1,2–1,7×, which is a *box-count*
multiplier for two-part Rooms and says nothing about auxiliary integers.

⚠️ One thing the ticket's unblocking note left, carried into **Part VI §VI.3**
rather than dying here: **`AREA_PER_ROOM_M2` = 9,65 is below what the placeholder
table needs at 7 and 8 rooms in either cut structure** (both need 11,58), and
below 7 rooms this Envelope family has no non-guillotine tiling at all. So the
bottom half of C13's 3–10 band is where the fixture is *least* trustworthy and
also the half no solver measurement covers. Any future pricing work fixes the
fixture first or measures 8+ only.

### 3. Whether the corpus supports the rule (item 3) — it does not, and the shape of the "no" is the finding

`d(nearest private) − d(nearest social)` over the 1 756 dwellings holding both:

| gap | share | |
|---|---:|---|
| − (private **nearer**) | **17,4 %** | violation, **1 in 5,8** |
| 0 | **51,0 %** | **tie** |
| + (private further) | **31,6 %** | strict order |

**Half of real dwellings say nothing at all.** The ticket's own bar was *"a rule
real dwellings break one time in six is not worth new integers"* — 17,4 % is
worse than that, and the tie mass is the fact nobody had computed.

⚠️ **This refines `zoning.md` §2.2's 16,1 % rather than repeating it.** That
figure is *mean* against *mean*; this is the **minimum** each side, which is what
a rule binds, because a rule binds the nearest offender. Quote 16,1 % for the
gradient's shape and **17,4 %** for a rule's cost.

### 4. Whether it is worth it at all (item 4) — no, and the alternative the ticket offered is false

The ticket asked this against *"the alternative that the three cheap properties
already shipped capture most of what the plan reads as designed means"* — which
is also the residue the fog patch left behind. **It is false, and now measured
false.** Entry-depth inversion against `proposer.md` §6.1 term 3 (**social
transit**), joined on key over the same 2 500 dwellings:

| | transit 0 | transit 1 | total |
|---|---:|---:|---:|
| **inversion 0** | 1 035 | 416 | 1 451 |
| **inversion 1** | **267** | **38** | 305 |

χ² = **34,55** (Yates 33,71), df 1, **p ≈ 4,2 × 10⁻⁹**, odds ratio **0,354**.
Expected in the both-cell under independence **78,9**, observed **38** — they are
**negatively** associated. **15,2 %** of all dwellings invert the gradient with
**no transit defect at all**, and term 3 is structurally blind to them: transit
is a *routing* property, inversion is a *distance* one, and a bedroom opening
straight off the entry hall is the second and not the first.

So the gradient is not merely unassertable — it is **unowned**, which is the
state the done-test exists to catch. It has a home and it is neither a constraint
nor nothing: a **fifth §6.1 plan-quality term**, scored against the corpus rate
in the shape the other four take. That is **D10**, and it is raised as
[What the entry-depth gradient is worth as a fifth evaluation term](66-what-the-entry-depth-gradient-is-worth-as-a-fifth-evaluation-term.md)
rather than written here, because `docs/spec/proposer.md` is claimed.

⚠️ The quantity is the **inversion rate** (real **17,4 %**), not the strict-order
rate: a model that ties everything and a model that reverses everything both
score 0 % strict, and the corpus is 51,0 % ties, so a strict rate cannot tell
them apart.

### 5. What the market does

Re-checked for this question, per the standing instruction. **Nothing in the
reviewed stack posts an ordering constraint, and the reason is structural**:
Graph2Plan and HouseDiffusion are *conditioned on a supplied access graph* — the
user hands them the bubble diagram, so privacy depth is an **input**, never
solved for and never scored. `zoning.md` §4's finding for adjacency holds
unchanged for order: user-authored, and soft. Nobody measures it, which supports
D10 and is not an argument against it.

### 6. Consequences

1. **The H-list closes at H10.** `solver-formulation.md`'s H-table now says so.
   A later proposal to add an ordering constraint is re-opening a decision with a
   published corpus cost, not filling a gap.
2. **`zoning.md` D7's verdict stands and its *reason* does not.** D7 said *out of
   v1* because *cost unmeasured*. The cost was never reached; the corpus decided
   it. D7 is amended in place so the stale reason is not quoted.
3. **§2.2 and §2.3 are amended in place** — 16,1 % gains its min-based twin and
   the tie mass, 93,2 % gains the note that the engine's rate is 100 % by
   construction.
4. **15 s, τ = 4 and Part II's percentiles are untouched.** Nothing in this
   ticket changes a solver constant, so 62, 64 and 65 may keep quoting them.
5. **`experiments/zoning/` gains its first README**, with six traps — the three
   social-transit denominators being the one that will bite.

### 7. What this ticket did not do

- **Did not write `docs/spec/proposer.md`** — 64's, sole claimant. D10 is
  specified in `zoning.md` and raised as ticket 66.
- **Did not touch `experiments/solver-toy/`**, though it held it. No solve was
  run, so there was nothing to write there.
- **Did not graduate the harness fog.** *Whether the harness needs a Brief
  generator that works on a real boundary* states its trigger as *a decision that
  needs one*; declining to measure creates no such trigger, so the patch stays
  fog, correctly owned.

### 8. Declared on resolution, unclaimed at the time

- `docs/research/zoning.md` — §6, D10, and amendments to §2.2, §2.3, D7.
- `experiments/zoning/` — `entry_order.py`, `entry_order2.py`,
  `entry_depth_vs_transit.py`, `README.md`.

Both were unclaimed by any open ticket when taken (43, 45, 62, 64, 65 declare
`experiments/solver-toy/`, `solver-formulation.md`, `homeowner-surface.md`,
`experiments/warp/`, ADR 0031, `proposer.md`, `acceptance-bar.md`, ADR 0032), so
the concurrency rule held.
