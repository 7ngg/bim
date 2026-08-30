# ADR 0039 — The solver reads the bar plane, and a boundary is accounted once for every rule

- **Status**: accepted
- **Date**: 2026-08-30
- **Ticket**: [The projection discards a fifth of the guarantees the warp now buys](../wayfinder/tickets/68-the-projection-discards-a-fifth-of-the-guarantees-the-warp-now-buys.md)
- **Amends**: ADR 0001 (states its erosion rule as a solver obligation rather than a validator one), ADR 0033 (retires consequence 4's number, not its decision)
- **Supersedes nothing**

## Context

`CONTEXT.md`'s **Space plane** named two clear areas where the system needed one.
The **bar plane** — `erode(⋃ parts, t_int/2)` with an edge on the Envelope *not*
eroded, because ADR 0001's tiling edge there already sits at
exterior-inner-face + `t_int/2` — is the plane every predicate in `rules.json` is
stated on. The **solver plane** is `(250w − t_int)(250h − t_int)`, which erodes
all four sides of every Room. On a perimeter Room the two differ by a median
**3,9 %** of its area.

`acceptance-bar.md` §11.1 recorded that and deferred it, on the reasoning that it
*"costs yield and never admits a Plan that should have been refused"*. Three
things about the deferral turned out to be wrong or narrower than they read.

**The defect is arithmetic, not geometry, and there is no domain to dilate.**
`brief.md` §5.3 describes the solve frame as `dilate(Envelope, t_int/2)`, and
§11.1 read the gap as unfixable because 75 mm is below the 250 mm grid's own
quantisation. But `absolute_area.space_m2` implements the same construction by
eroding `parts ∪ outside`, under which *a boundary edge is interior to the union
and survives*. The domain boundary already **is** the exterior inner face. There
is no missing 75 mm ring to represent; there is a subtraction `solver.py` performs
and should not.

**It is not one predicate's.** Seven rules are `site: both` and read a clear
dimension: `dim.min_area`, `dim.statutory_min_area`, `dim.min_clear_width`,
`dim.min_clear_depth`, `dim.corridor_min_width`, `dim.aspect_ratio_hard`,
`dim.max_area`. A correction fitted to the statutory floor patches one of seven.

**It runs in both directions.** Five are floors, where the solver's plane refuses
what the bar admits — 75 mm of a 900 mm corridor is **8,3 %**. `dim.max_area` is a
**cap**, and there the solver's plane is the *lenient* one: it reads a perimeter
Room ~3,9 % smaller, so the cap fails to bind exactly where
`model.no_unassigned_area` sends surplus. Nothing unsafe reaches a Homeowner — the
validator re-checks on the bar plane and discards the Plan — but the rule's own
note justifies the solver post as *"FREE … an upper bound on a product tightens
propagation"*, and a cap that does not bind tightens nothing.

**And ADR 0033 consequence 4's 19,5 % is measured at the wrong site.**
`project_join.planes()` compares two planes on warped rectangles and says in its
own docstring that no solver runs. Because the rule is `site: both`, the
projection *posts* the floor: a Room short on the solver's plane is **re-sized**,
not refused, and a refusal can only surface as INFEASIBLE. Measured on the same
rig: 273 candidates reached the solve, **14 INFEASIBLE**, and ablation — drop the
statutory limb, keep the ergonomic floor — returns 10 OPTIMAL and 4 FEASIBLE, so
all fourteen are the floor's. **5,1 %**, an upper bound that also contains genuine
starvation. §11.1 had already caught itself making this exact error at 3,6 %.

## Decision

**1. The solver reads the bar plane. The Space plane stops being two quantities.**
`amm_i` is redefined as the Space area ADR 0001 publishes, and every `site: both`
dimensional rule posts against it. `CONTEXT.md`'s **Space plane** entry becomes a
record of a closed defect rather than a live distinction.

**2. The erosion is subtracted per side, over the sides that face another Room.**

```
amm_i = 62 500 · a_i  −  75 · Σ_{s ∈ 4 sides} interior_len_mm(i, s)

interior_len(i, s) = side_len(i, s) − boundary_contact_len(i, s)
```

`a_i = w_i · h_i` is the multiplication H4 already builds.
`boundary_contact_len` is the overlap between the Room's side and the runs
returned by `Envelope.all_faces()` — the boundary decomposition `_add_exterior`
already consumes for H8, and the one *The toy Envelope is more compact than a real
dwelling* removed the phantom faces from. Overlap per face is
`max(0, min(hi, p_hi) − max(lo, p_lo))` under a reified flush-contact literal:
`AddMaxEquality` / `AddMinEquality`, no products.

The clear dimensions take the same literals linearly:
`clear_w_i = 250·w_i − 75·(number of interior x-sides)`.

**3. No second `AddMultiplicationEquality`.** The form is affine in `a_i` and
linear in the segment lengths — the same identity that let ADR 0001's clear
reading ship free as `mm_affine`. II.1 measured that doubling the multiplication
count is not detectable against seed-to-seed spread; this does not even spend
that.

**4. The contact literals are biconditional, and H8's stay forward-only.**
Forward-only is correct for a floor: a Room must *prove* contact to claim the
correction, so an unclaimed correction leaves the solver conservative. It is wrong
for a cap, where leaving every literal false is free and keeps `dim.max_area`
loose. The area accounting therefore builds its own literal set, both directions;
`_add_exterior` is untouched.

**5. A corner residual of at most 0,0225 m² per Room is accepted, and it is
handed to the ticket that already owns dust of that size.** Subtracting a band per
side double-subtracts the 75 × 75 square where two interior sides meet. Adding it
back exactly requires contact at a *point* rather than over a length; approximating
it by "both sides wholly interior" under-counts. Dropped, bounded at `4 × 5625 mm²`,
conservative on every floor, and smaller than the **0,038 m²** *The posted floor is
a seed-shape estimate* is already deciding about. Verified by hand: 4 × 3 cells with
all sides interior gives 487 500 mm² against a true 510 000 — exactly four corners;
with the left side on the boundary, 543 750 against 555 000 — exactly two.

**6. The fallback, if the timing measurement refuses it.** This is a new per-Room
accounting layer in the solver's dimensional block and its cost against the 15 s
cap and τ = 4 is unmeasured. If it does not fit: **floors only, forward-only
literals, and `dim.max_area` left to the validator** — which recovers the whole
false-refusal side at a fraction of the model size, and leaves the cap exactly
where it is today rather than making it worse. It is a fallback, not the decision.

## Why this is not a re-opening of the deferral

§11.1's deferral is sound on its own terms and this does not dispute them. It was
priced when no stage was paying to clear the floor; ADR 0033 makes the warp pay
**8,66 %** of candidates for a guarantee the projection then reads on a different
plane. What changed is the cost basis, exactly as ADR 0033 consequence 4 said —
and then the measurement, which shows both the price and the mechanism were
misread.

Nor is it a change to `dim.statutory_min_area`. The value, severity, site and limb
set are settled three times over (ADR 0027, ADR 0033, `acceptance-bar.md` §3.2).
This ADR moves no threshold. It makes one component read the number the others
already read.

## Consequences

1. **`CONTEXT.md`'s Space plane is rewritten** from a live two-quantity
   distinction to a closed one, with the *avoid* note kept: the two planes were
   both clear areas and both correct on their own terms, and that is why the
   unnamed version shipped.

2. **`acceptance-bar.md` §11.1's plane paragraphs are rewritten**, and 19,5 % is
   retired from the file. The escalation, the refused screen and the three steps
   are untouched.

3. ⚠️ **`rules.json` carries one sentence that is now wrong and this ADR does not
   fix it.** `dim.max_area`'s note says *"The solver side is FREE: H4 already
   builds a = w*h … an upper bound on a product tightens propagation"*. It did not
   tighten propagation, because it was posted on a quantity smaller than the one
   the rule bounds. The file has two claimants — *A regulator states an aspect rule
   and the engine says none does* and *A cap fitted in one country and a target set
   in another* — so the correction is handed on as prose rather than written, per
   the map's concurrency rule.

4. **`docs/research/solver-formulation.md` gains the encoding**, beside II.1's
   `mm_affine` derivation, because it is the same identity applied one term
   further out.

5. ⚠️ **Nothing here is implemented or measured.** The encoding is derived and
   hand-verified on two cases; build time, solve time and the INFEASIBLE delta are
   not. That is a task ticket, and until it closes `solver.py` still reads the
   solver plane and §11.1's rewritten paragraphs describe a decision rather than a
   shipped state.

6. **This is the third constraint answered the way ADR 0033 consequence 6
   predicted** — after ADR 0028's void charge and ADR 0033's floor, a rule that
   looked like it needed a gate or a special case turned out to be linear on
   variables that already existed.
