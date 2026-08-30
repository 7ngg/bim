---
id: 68
title: The projection discards a fifth of the guarantees the warp now buys
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - docs/spec/acceptance-bar.md
  - docs/research/solver-formulation.md
---

# The projection discards a fifth of the guarantees the warp now buys

## Question

**`solver.py` reads a Room on a different plane from the bar it enforces, and
ADR 0033 has just changed what that costs.** The two quantities now have a name —
`CONTEXT.md`'s **Space plane**: the **bar plane** does not erode an edge sitting
on the Envelope, because ADR 0001's tiling edge there already sits at
exterior-inner-face + `t_int/2`; the **solver plane** erodes all four sides of
every Room, because 75 mm is below the 250 mm grid's own quantisation. The
projection is therefore **strictly stricter than the rule it posts**, by a median
**3,9 %** of a Room's area.

`acceptance-bar.md` §11.1 recorded this and deferred it, and the deferral's
reasoning is sound as far as it goes: *"it costs yield and never admits a Plan
that should have been refused"*. **What changed is the cost basis, not the
argument.** That deferral was priced when no stage was paying to clear the floor.
ADR 0033 makes the warp pay — 8,66 % of candidates, to guarantee every Room
clears its statutory floor on the bar plane — and then **59 of 302** floor-clean
candidates, **19,5 %**, fail that same floor on the solver's plane.

⚠️ **19,5 % and §11.1's 1,51 % are two denominators, not a contradiction.**
1,51 % is per-Room over all 1 786 warped Rooms; 19,5 % is per-candidate over the
floor-bound population. Anyone quoting one at the other is comparing different
quantities, and this ticket must not manufacture a conflict out of that.

**This is not a re-opening of the deferral.** It is the question the deferral
could not have answered: *what is a false refusal worth once a stage upstream is
spending yield to prevent it?*

## What has to be decided

1. **Whether the floor `solver.py` posts can carry a boundary correction.**
   §11.1 says the plane *"cannot be fixed inside the model"*, and that is a claim
   about representing 75 mm on a 250 mm grid — it is **not** obviously a claim
   about the floor *constant*. `amm >= min_area · 250² − correction(Room)`, where
   the correction is computed from which of the Room's sides sit on the domain
   boundary, moves arithmetic rather than geometry. Check whether that is
   available before accepting that nothing is.
2. **Whether the bar should instead be restated on the solver's plane.** The
   opposite fix, and it is the one to argue against explicitly: it would make the
   engine agree with itself by moving a *legal* quantity onto a plane chosen by a
   quantisation accident. ⚠️ ADR 0033 refused exactly this move for the warp and
   the reasoning transfers.
3. **Whether it is worth fixing at all in v1.** The honest case for leaving it:
   it never admits a Plan that should have been refused, so it costs only yield,
   and yield is what pool depth is for. The case against is now stronger by one
   fact — the yield it costs is yield another stage has already bought.
4. **What C2's Homeowner is told**, if anything. Nothing here reaches the surface
   today; a refusal on this path lands in §11.1 step 3's no-defect sentence,
   which already covers it. Confirm rather than assume.

## What this is not

Not a change to `dim.statutory_min_area` — severity, value, site and limb set are
settled three times over (ADR 0027, ADR 0033, `acceptance-bar.md` §3.2). Not a
re-opening of ADR 0033. Not the warp-side encoding residual, which is
*The posted floor is a seed-shape estimate*.

## Raised by

*Should the warp post the statutory floor* (2026-08-29), ADR 0033 consequence 4.

## Handed on by *A zone floor is posted on the whole room* (2026-08-30)

**One sentence of `acceptance-bar.md` §11.1 is now narrower than it reads, and
this ticket is the only one that may touch that file.**

ADR 0034 reclassifies `dim.statutory_min_area`'s `KITCHEN_DINING` limb: the 6,0
is **entailed, not transcribed** — AzDTN cl. 5.7 floors the kitchen *zone* inside
the room and publishes no whole-room figure at all, established exhaustively in
`docs/research/az-kitchen-diner-whole-room.md`. The value does not move, and
neither does the severity, the site or the enforcement order.

What §11.1 should carry when you rewrite it:

- **The rule no longer has one kind of limb.** Four limbs are transcriptions of
  a whole-room figure; one is a sound lower bound entailed from a part. Both are
  hard and both are enforced identically, but a reader reasoning about *what a
  clearing Plan guarantees* now gets a weaker guarantee on one limb — the room
  clears the part's floor, not the room's, and the room's is unpublished.
- ⚠️ **This does not touch your own question.** The plane defect is per-Room over
  all warped Rooms and is orthogonal to which limb a Room reads. The 19,5 % you
  are re-pricing is unaffected: `KITCHEN_DINING` is 41 rooms of 319 222, and
  `STAT_FLOOR` does not move, so no figure in your ticket changes.
- **`experiments/warp/` stayed untouched by ticket 70**, deliberately, so
  nothing you or 62/65/67 depend on has shifted underneath.

## Resolution

**ADR 0039.** The solver reads the bar plane. Three of this ticket's own premises
were wrong, and correcting them is most of the answer.

### 1. 19,5 % is measured at the wrong site, and this section had already caught itself doing that

`project_join.planes()` says it in its own docstring: *"No solver runs here."* It
compares two planes on warped rectangles. But `dim.statutory_min_area` is
`site: both` — the projection **posts** it — so a Room short on the solver's plane
is **re-sized**, not refused. A refusal can only surface as INFEASIBLE.

That is already measured on the same rig. `experiments/warp/out/project_join_k1.json`:
273 candidates reached the solve, **14 INFEASIBLE**, `infeasible_on_the_floor: 14`,
and the ablation arm — drop the statutory limb, keep the ergonomic floor — returns
**10 OPTIMAL and 4 FEASIBLE**. So all fourteen are the floor's, and the Plan-level
cost is **5,1 %**, an upper bound that also contains genuine starvation.

§11.1 demoted its own 3,6 % Proposal-starvation figure as *"an upper bound on a
quantity measured at the wrong site"* and then quoted 19,5 % four paragraphs
later — the same error, one stage further on. 19,5 % is retired from the file.

### 2. There is no domain to dilate — the defect is arithmetic, not geometry

`brief.md` §5.3 describes the solve frame as `dilate(Envelope, t_int/2)`, and
§11.1 concluded the gap *"cannot be fixed inside the model"* because 75 mm is
below the 250 mm grid's quantisation. Read together they invite a dilated domain,
or a shifted lattice on which `W_env + t_int ≡ 0 (mod 250)` — ADR 0007's *pay the
wall in the number* applied to the Envelope. **That solves a problem that does not
exist.**

`absolute_area.space_m2` erodes `parts ∪ outside`, under which *a boundary edge is
interior to the union and survives*. The domain boundary already **is** the
exterior inner face; §5.3's dilation and the union-with-outside are two
descriptions of one geometry. Nothing is missing. `solver.py` performs a
subtraction it should not.

So the answer to question 1 — can the posted floor carry a boundary correction —
is **yes, and not as a constant**. Question 2, restating the bar on the solver's
plane, needs no separate argument once this is seen: there is no solver plane to
restate onto, only an arithmetic error to remove.

### 3. It was never one predicate's, and it runs in both directions

Seven rules are `site: both` and read a clear dimension: `dim.min_area`,
`dim.statutory_min_area`, `dim.min_clear_width`, `dim.min_clear_depth`,
`dim.corridor_min_width`, `dim.aspect_ratio_hard`, `dim.max_area`.

Five are floors, where the solver is stricter — 75 mm of a 900 mm corridor is
**8,3 %**, and `_check_min_side_identity` in `project_join.py` asserts those bind
identically across *grid rounding* while saying nothing about the plane.
`dim.aspect_ratio_hard` reads a ratio of two clear dimensions and moves either way.

**`dim.max_area` is a cap, and there the solver's plane is the lenient one.** It
reads a perimeter Room ~3,9 % smaller, so the cap fails to bind exactly where
`model.no_unassigned_area` sends surplus. §11.1's *"never admits a Plan that
should have been refused"* survives only because the validator re-checks on the
bar plane and discards it — what is lost is yield, plus the propagation the rule's
own note claims the solver post buys. A ticket that closed on the statutory floor
alone would have left `acceptance-bar.md` asserting a one-directional safety
argument about a two-directional defect.

### The encoding

```
amm_i = 62 500 · a_i  −  75 · Σ_{s ∈ 4 sides} interior_len_mm(i, s)

interior_len(i, s) = side_len(i, s) − boundary_contact_len(i, s)
```

`a_i = w_i·h_i` is H4's existing product. `boundary_contact_len` is the overlap
between the Room's side and the maximal runs `Envelope.all_faces()` returns — the
decomposition `_add_exterior` already consumes for H8, and the one *The toy
Envelope is more compact than a real dwelling* de-phantomed. Per face,
`max(0, min(hi, p_hi) − max(lo, p_lo))` under a reified flush-contact literal:
`AddMaxEquality` / `AddMinEquality`, no products. Clear dimensions follow
linearly: `clear_w_i = 250·w_i − 75·(interior x-sides)`.

**Affine in `a_i`, linear in the segment lengths — no second
`AddMultiplicationEquality`.** The same identity II.1 used to make ADR 0001's clear
reading free. What it does spend is auxiliary integers and reified literals,
bounded by rooms × 4 sides × faces, and that is the cost to measure.

**The literals are biconditional and H8's stay forward-only.** Forward-only is
correct for a floor — a Room must prove contact to claim the correction, so an
unclaimed one leaves the solver conservative and no false pass is reachable. It is
wrong for a cap, where leaving every literal false is free and understates the
area. Separate literal set; `_add_exterior` untouched.

**Corner residual, accepted and handed on.** Subtracting a band per side
double-subtracts the 75 × 75 square where two interior sides meet: at most
**0,0225 m²** per Room. Hand-verified — 4 × 3 cells all-interior gives 487 500 mm²
against a true 510 000 (four corners); with the left side on the boundary, 543 750
against 555 000 (two). Exact recovery needs contact at a *point* rather than over a
length. Dropped: bounded, conservative on every floor, and smaller than the
0,038 m² *The posted floor is a seed-shape estimate* is already deciding about.
That ticket owns both.

### On the market, per the repo's standing instruction

Revit, ArchiCAD and Vectorworks compute a room's area from the bounding wall
faces. One area, no second plane — quantisation is our artifact and no
professional tool carries one. *"Costs only yield"* was a defensible v1 position
while nothing was paying for the guarantee. It is not an architecture, and a
Practitioner opening a plan whose tagged area differs from the area the engine
enforced finds it in minutes.

### Question 4 — what the Homeowner is told

**Nothing, and that is confirmed rather than assumed.** A refusal on this path
lands in §11.1 step 3's no-defect sentence, which already covers it and already
names no Brief field. Removing false refusals shrinks the population that reaches
step 3; it adds no message. The locale hole over the rule messages is unmoved.

### What this leaves

- ⚠️ **Nothing is implemented or measured.** The encoding is derived and
  hand-verified on two cases. Build time, solve time against the 15 s cap and
  τ = 4, and the INFEASIBLE delta are not. Raised as *The bar plane is derived and
  the solver has never run it*. Until it closes, `solver.py` still reads the solver
  plane and §11.1's rewritten paragraphs state a decision, not a shipped state.
- ⚠️ **One `rules.json` sentence is now false and this ticket did not write it.**
  `dim.max_area`'s note claims *"The solver side is FREE … an upper bound on a
  product tightens propagation"*. It did not tighten propagation, because it was
  posted on a quantity smaller than the one the rule bounds. The file has two
  claimants — *A regulator states an aspect rule and the engine says none does*
  and *A cap fitted in one country and a target set in another* — so it is handed
  on as prose, exactly as 73 and 74 did.
- **Ticket 70's handoff is discharged.** `acceptance-bar.md` §11.1 now carries the
  `KITCHEN_DINING` limb reclassification: four limbs transcribe a whole-room
  figure, one is a sound lower bound entailed from a part, and a clearing Plan
  guarantees less on that one. Orthogonal to the plane, as 70 said; no figure moved.
- **`writes:` corrected.** It named `docs/spec/solver-formulation.md`, which does
  not exist and which nothing on the map owes. The findings went to
  `docs/research/solver-formulation.md` Part VII.

### Artifacts

- `docs/adr/0039-the-solver-reads-the-bar-plane-and-a-boundary-is-accounted-once.md` — new.
- `docs/spec/acceptance-bar.md` §11.1 — the two plane paragraphs replaced; 19,5 %
  retired; ticket 70's limb note landed. **Sole claimant**, held.
- `docs/research/solver-formulation.md` — **Part VII**, beside II.1 because it is
  the same identity one term further out. Declared on resolution, no claimant.
- `CONTEXT.md` — **Space plane** rewritten from a live two-quantity distinction to
  a closed defect. Declared on resolution, no claimant at the time.
- **Not touched, deliberately**: `data/acceptance/rules.json` (two claimants),
  `experiments/warp/` (three), `experiments/solver-toy/` (claimed by 43), and no
  code anywhere — C1.
