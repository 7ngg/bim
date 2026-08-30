# ADR 0040 — The bar-plane encoding is measured, it fits, and the cap is posted on it

- **Status**: accepted
- **Date**: 2026-08-30
- **Ticket**: [The bar plane is derived and the solver has never run it](../wayfinder/tickets/77-the-bar-plane-is-derived-and-the-solver-has-never-run-it.md)
- **Amends**: ADR 0039 (decision 2's face set, decision 5's residual claim; confirms the rest and declines its fallback)
- **Supersedes nothing**

## Context

ADR 0039 decided that `solver.py` should read the **bar plane** by subtracting
the erosion band per *side* rather than on all four. It wrote no code and took no
measurement, and said so: *"build time, solve time and the INFEASIBLE delta are
not [measured]. That is a task ticket, and until it closes `solver.py` still
reads the solver plane and §11.1's rewritten paragraphs describe a decision
rather than a shipped state."*

The encoding is now built — `experiments/plane-accounting/`, a `LayoutProjector`
subclass overriding **one** method — and run at the shipped configuration over
340 (Brief, candidate) pairs with ADR 0033's floor posted in the warp. Full
measurement at `docs/research/solver-formulation.md` **Part VIII**.

**The incumbent could not be quoted and had to be re-run, for two reasons rather
than the one the ticket carried.** ADR 0033 shipped the warp's floor *after*
`project_join`'s run, so **14 of 273** was measured on a warp that posted nothing.
And the candidate population moved underneath it: `project_join`'s LIMIT 3 records
1 076 one-part donors of 2 317, and `load()` now returns **1 057 of 2 292**,
because ADR 0037 changed what `COLLAPSE` and the minima tables resolve to.

## Decision

**1. ADR 0039's encoding ships. Its decision 6 fallback is not selected.**

The cost is **measurable**, unlike II.1's arithmetic finding, and it fits.
`B` against the incumbent `A`, paired over 307 candidates: **2,36×** the
variables, **1,85×** the constraints, build p50 24,1 → 46,5 ms, wall p50
0,193 → 0,447 s, **284 slower against 23 faster**. Over six CP-SAT seeds only
**6 of 35** candidates have a difference inside their own seed spread, so this
is not seed noise and must not be reported as free.

It fits because none of it lands where the budget is. Time to first Plan goes
0,110 s → 0,284 s against a **15 s** cap; the number of candidates that exhaust
the cap goes **down**, 17 → 16; no candidate is pushed to `UNKNOWN`. τ = 4, 15 s
and ADR 0007 stand at their published values.

**ADR 0039 decision 3 is true and was the wrong reassurance.** There is no second
`AddMultiplicationEquality` and the multiplication was never the cost. Auxiliary
integers and reified literals are, and they cost **16,4 %** of total solve time.

**2. The face set is the boundary MINUS enclosed voids, not `Envelope.all_faces()`.**

Decision 2 names `all_faces()`, which walks the boundary of the *interior* — and
an **enclosed void** bounds the interior exactly as the outside does.
`absolute_area.outside_of` deliberately excludes enclosed components, because a
void is walled on every side and its edges erode like any partition. Crediting a
void face as boundary contact would read that Room **larger** than the bar plane,
which is the one direction `dim.max_area` cannot afford.

The correct set is `bar_plane.no_erode_faces()`: boundary unit edges whose other
side is the exterior or a **boundary-touching** notch, 4-connected, merged into
maximal runs. It equals `all_faces()` on a rectangle, an L and a U, and drops
exactly the hole's perimeter on an Envelope with a void.

**3. `dim.max_area` is posted by the solver, on the bar plane.** ADR 0039
decision 1 already said every `site: both` dimensional rule posts against `amm`.
This makes it a measurement rather than an entailment, because no arm on this map
had ever posted the cap at all.

It **binds**: **10 Rooms of 1 993** sit above their band uncapped, across 9
candidates, **every one a `BATHROOM`**, worst **10,2 m² over** — `brief.md` §9.3's
40 m² WC through a third door, made compulsory by `model.no_unassigned_area`.

It is **nearly free**: +6 constraints per candidate, no new variables, wall delta
p50 −0,002 s, **0** new INFEASIBLE.

And the plane decides whether it works: posted on the bar plane it leaves **0**
Rooms above the cap; posted on the solver's smaller plane it leaves **2**.
**ADR 0039 decision 4's biconditional contact literals are therefore bought for
something**, and the ticket's own doubt — *"if it turns out never to bind, decision
4's requirement is bought for nothing"* — is answered.

**4. ⚠️ Decision 5's residual is two-signed, and the sign claim is withdrawn.**

The residual has a second term ADR 0039 does not have. Exactly, and verified to
the millimetre squared against `space_m2` over **11 892 Rooms at a worst
disagreement of 0,0 mm²**:

```
truth = [B] + 5 625 × (interior corners − reflex vertices on the Room's sides)
```

Where a Room's side crosses from Envelope to partition, three of the four cells
round that vertex are interior — a 270° corner. The erosion wraps around it and
takes a further 75 × 75 square at a **point** that lies on no side's end, which a
band subtracted over a **length** cannot see.

Decision 5's *"conservative on every floor"* is **false**: `[B]` reads **109 of
1 993 Rooms (5,47 %)** larger than the bar plane. Its `0,0225 m²` is an **observed
maximum, not a derived bound** — nothing bounds the reflex count except the Room's
own perimeter, and it reached 3 here.

**The drop stands, and it changes no verdict**: 0 floor verdicts and 0 cap
verdicts move on 1 993 Rooms, against a plane gap of p50 **3,91 %** of a Room's
area. What is withdrawn is the *reason*.

**5. ⚠️ The corner term may not be added on its own.** `[B] + 5 625 × corners`
over-states by exactly `5 625 × reflex`, so it is **never** conservative: it reads
**726 of 1 993 Rooms (36,43 %)** larger than the bar plane, against `[B]`'s 5,47 %
— **6,7× more often**, for 0 verdict changes. ADR 0039's objection to the
approximation was that it under-counts. The real objection is that half the
correction is missing and adding the other half alone inverts the sign on a third
of Rooms. Exact recovery needs **both** point terms, at O(perimeter) reified
literals per Room against the corner term's O(4).

**6. §11.1's Plan-level cost is `1,30 %`, and the plane is all of it.** With ADR
0033's floor upstream, 33 of 340 candidates (9,71 %) are refused before the solve
and 307 reach it. The incumbent refuses **4 of 307 = 1,30 %**, all four attributed
to the floor by ablation; the bar plane refuses **0**. **5,1 %** is retired.

## Why this is not a re-opening of ADR 0039

Every decision it took is confirmed on measurement. Two of its supporting claims
are corrected — one names a set that is a class too wide, one asserts a sign that
does not hold — and neither changes what the encoding does. No threshold moves:
`dim.statutory_min_area`'s value, severity, site and limbs are settled three times
over by ADR 0027, ADR 0033 and `acceptance-bar.md` §3.2, and `dim.max_area`'s
value is `rules.json`'s and out of scope here.

## Consequences

1. **`acceptance-bar.md` §11.1 loses 5,1 % and gains 1,30 %**, and its ⚠️ changes
   from *"describes a decision as though it were a shipped state"* to a plain
   statement that the encoding is measured and the shipped engine has yet to be
   built. The escalation, the refused screen and the three steps are untouched.

2. ⚠️ **`rules.json` carries a sentence ADR 0039 could not fix and this ADR can
   now price.** `dim.max_area`'s note claims *"The solver side is FREE: H4 already
   builds a = w*h … an upper bound on a product tightens propagation."* The cost
   claim is very nearly right — **+6 constraints, no new variables, wall delta p50
   −0,002 s** — and the propagation claim was false as written, because the bound
   was posted on a quantity smaller than the one the rule bounds. Both halves are
   measured now. The file still has two claimants — *A regulator states an aspect
   rule and the engine says none does* and *A cap fitted in one country and a
   target set in another* — so this is handed on as prose, per the map's
   concurrency rule.

3. ⚠️ **The encoding is derived for a Room that is ONE rectangle.** ADR 0014 gives
   a Room one or two, and `erode(A ∪ B, t/2)` exceeds `erode(A) ∪ erode(B)` by
   exactly the shared-edge band — a term the per-side form does not carry, since
   it subtracts a band along an edge the union does not have. `--parts=1` is 46 %
   of the converted index. Raised as *What the bar plane owes a two-part Room*.

4. **`solver-formulation.md` gains Part VIII**, beside Part VII's derivation,
   because it is that derivation measured.

5. **`CONTEXT.md`'s Space plane needs no edit.** Its boundary rule says *"an edge
   on the Envelope is not eroded"*, and an enclosed void is not the Envelope, so
   decision 2 above sharpens the implementation without moving the term.

6. **No shipped code changes here.** This map produces decisions, not code; the
   evidence lives in `experiments/plane-accounting/` and the obligation on the
   build is ADR 0039 decision 1–4 as amended above.
