# ADR 0041 — A Room of two rectangles is accounted on the Room, and the join is paid

- **Status**: accepted
- **Date**: 2026-08-30
- **Ticket**: [What the bar plane owes a two-part Room](../wayfinder/tickets/78-what-the-bar-plane-owes-a-two-part-room.md)
- **Amends**: ADR 0039 (generalises decisions 1–2 to a Room of two parts; decision 5's residual identity is superseded by the vertex rule below), ADR 0040 (decision 4's identity is the one-rectangle case of it)
- **Supersedes nothing**

## Context

ADR 0040 consequence 3 raised the debt in its own words: *"the encoding is derived
for a Room that is ONE rectangle. ADR 0014 gives a Room one or two, and
`erode(A ∪ B, t/2)` exceeds `erode(A) ∪ erode(B)` by exactly the shared-edge band
— a term the per-side form does not carry, since it subtracts a band along an edge
the union does not have."*

**1 235 of 2 292 converted dwellings — 53,9 % — hold at least one two-part Room.**
It is the majority case, not the tail.

The encoding is now built for a Room of one or two parts —
`experiments/plane-accounting/parts_plane.py`, `room-rectangles/solver_parts.py`'s
Design A with **one** method replaced and `bar_plane.py`'s reified-contact helpers
bound in unmodified — and run at the shipped configuration over **332** (Brief,
candidate) pairs. Full measurement at `docs/research/solver-formulation.md`
**Part IX**; `acceptance-bar.md` §11.1 carries the Homeowner-facing half.

**Five arms, each one change from the last**, so every delta attributes: `A` the
incumbent (`solver_parts.project_parts`, asserted rather than rebuilt), `Ar` the
same plane with the area floor moved to the Room, `Bn` the bar plane applied
per part and summed, `B` that plus the join band, `Bcap` that plus `dim.max_area`.

## Decision

**1. The two-part encoding ships. ADR 0039 generalises by one term.**

```
amm_Room = 62 500 · Σ_p a_p  −  18 750 · ( Σ_p int_units(p)  −  2 J )
```

`int_units(p)` is ADR 0039 decision 2's per-part quantity, unchanged. `J` is the
shared-edge length in grid units. **There are no contact literals between a Room's
own parts.** `AddNoOverlap2D` already covers every part pair including a Room's
own, and two interior-disjoint rectangles meet in at most **one** maximal segment,
so the whole term is one length: **exactly 13 variables per two-part Room** —
p10, p50, p99 and max all 13 over 284 candidates — where the boundary term is
O(sides × faces). No second `AddMultiplicationEquality`; the form stays affine in
`a_p`.

**It fits.** `B` against `A`, paired over 284: **1,82×** the variables, **1,51×**
the constraints, wall p50 1,390 → 2,424 s, **13,2 %** more total solve time, 227
slower against 57 faster. Time to first Plan **0,257 → 0,623 s** against the
**15 s** cap; no candidate is pushed to `UNKNOWN`. **The join term itself is 1,5
points of that 13,2 %** and +0,0084 s at p50, 184 slower against 99 faster.
τ = 4, 15 s and ADR 0007 stand at their published values, and **ADR 0039 decision
6's fallback is not selected.**

**And the join term is free at the bar ADR 0040 set.** Six CP-SAT seeds per arm over
19 stratified candidates: `B − A` lies **outside** the candidate's own seed spread on
**15 of 19** (median +0,336 s, p = 0,00073), so the plane's cost is measurable, as it
was at one rectangle. **`B − Bn` lies inside it on 18 of 19 (94,7 %)**, median
+0,0046 s, **p = 0,167**. The join term is a systematic +8,4 ms across 284 paired
candidates and undetectable on any one of them.

⚠️ **The margin is thinner than at `--parts=1` and the reason is not this
encoding.** Under the *incumbent*, **90 of 284 candidates (31,7 %) already exhaust
the 15 s cap** at `--parts=2`, against 17 of 307 (5,5 %) at `--parts=1`. That is
Design A's search space, which ADR 0014 measured at 1,2–1,7× the variables. The
encoding takes it to 102 of 284 — so unlike Part VIII, where the count fell 17 →
16, here it **rises**, and Part VIII's *"none of it lands where the budget is"*
must not be quoted at two parts.

**2. Every area rule binds on the ROOM in the solver, and that — not the plane —
is where the false refusals were.**

`acceptance-bar.md` §9.1 already says it: clear width, depth and aspect bind **per
part**, *"area, and every area rule (§8) — per Room, over the union"*.
`solver_parts.py` binds `min_area` on the **primary part**, which
`project_join.py` LIMIT 3 flags as *"strictly stricter"*. This ADR does not decide
the site; it prices the deviation and closes it.

**5 of 284 candidates (1,76 %) are INFEASIBLE under `A`, all five attributed to the
statutory floor by ablation, and all five are rescued by `Ar` alone** — the binding
site, with the plane unchanged. `Bn` and `B` rescue nothing further because nothing
is left to rescue. The cost is **+2 variables**, one Room-level integer per two-part
Room.

⚠️ **So the plane's own Plan-level contribution at `--parts=2` is zero**, where
Part VIII measured 4 of 307 rescued at `--parts=1`. That is not a contradiction: a
strictly stricter binding site sat in front of it and spent the refusals first.
What the plane buys here is coverage — mean unassigned cells **7,4 → 2,6** — and
the objective, better on **140 of the 279** candidates both arms served, against 4
worse.

**3. `dim.max_area` is posted on the Room, on the bar plane, and it binds at two
parts too.** On the uncapped bar-plane arm, **10 Rooms of 1 961 (0,51 %)** sit
above their band across 9 candidates, worst **8,19 m² over**: 7 `BATHROOM`, and —
new against Part VIII, where all ten were bathrooms — 1 `KITCHEN`, 1 `CORRIDOR`,
1 `STOREROOM`. **One of the ten is a two-part Room**, a `Z`.

Posting it leaves **0** Rooms above the cap, costs **+7 constraints** at p50 and
**no new variables**, and its wall delta is the one difference in this run a sign
test cannot separate from zero (p50 −0,0003 s, 139 slower against 143 faster,
**p = 0,86**). Posted on the solver plane summed over the parts it leaves **2**.

**4. ADR 0040 decision 4's residual identity is replaced by one vertex rule, and
that identity is its one-rectangle case.**

```
truth(U) = 62 500 |U|  −  18 750 E_int(U)  +  5 625 · Σ_v w(v)

w(v) = I(v)  −  nU(v) · [ nO(v) ≥ 1 ]
```

At a lattice vertex, label the four cells round it `U` (this Room), `F` (exterior
or a boundary-touching notch) or `O` (any other interior). `I` counts the four
half-edges with one side `U` and the other `O`. Verified against
`absolute_area.space_m2` over **11 740 Rooms at a worst disagreement of
0,0 mm²**, in shapes L, T, Z and rectangle.

`corners − reflex` does not extend to a union — it is stated on a rectangle's four
corners and its sides' interiors, and a union of two rectangles has neither. The
rule above reproduces it exactly at one part (`I=2, nU=1` → +1; `I=1, nU=2` → −1)
and reaches three places it could not: an **L's own reflex corner** (`I=2, nU=3` →
−1, the same sign and size as a mid-side flip, so **the ticket's "third sign" is
not a third sign**), a **flush join end** (`I=2, nU=2` → 0, where naive per-part
counting would report two interior corners and be wrong by +11 250 mm²), and a Room
meeting an **enclosed void diagonally at a point**.

**ADR 0039 decision 5's drop stands.** With the join term the residual is p50
+0,00562 m², range −0,0225 … +0,0225, every value a multiple of 5 625, **all 1 961
Rooms inside ADR 0039's figure** — which remains an observed range and not a bound,
because `nU` reaches 3. **0 floor verdicts and 0 cap verdicts move.**

**5. The join term is bought for the posted quantity, not for yield — and that is
enough at 13 variables.**

Omitting it reads a two-part Room short by **p50 0,300 m²**, p90 0,600, **max
1,013 m²** — the corpus's join is p50 **8 grid units**, not ADR 0014's floor of 4 —
which is **53×** the p50 corner residual ADR 0039 dropped and **7,9×** the grid dust
*The posted floor is a seed-shape estimate* is deciding about. Whatever argument
retires the corner term does not reach this one.

⚠️ **Its realised yield at this geometry is one Room in 1 961**, and the reason is
stated rather than hidden: `dim.statutory_min_area` is `site: both`, so a Room read
short is **re-sized rather than refused**, and a two-part Room's headroom over its
own floor runs **p50 9,37 m²**. **Only 1 of 345 two-part Rooms has less headroom
than its own join term.** A Room gets a second rectangle because it is large and
awkward, not because it is tight.

## Why this is not a re-opening of ADR 0014, ADR 0039 or ADR 0040

A Room is one or two rectangles and the Proposal decides which — untouched.
ADR 0039's decisions 1–4 are confirmed and generalised by one term; its decision 5
drop stands and its identity is superseded, not contradicted. ADR 0040's
measurements are the one-rectangle case throughout and none of them moves. No
threshold moves: `dim.statutory_min_area`'s value, severity, site and limbs are
settled by ADR 0027, ADR 0033 and `acceptance-bar.md` §3.2, and `dim.max_area`'s
value is `rules.json`'s.

## Consequences

1. **`solver-formulation.md` gains Part IX**, beside Part VIII, because it is the
   same measurement one term further out.

2. **The obligation on the build is ADR 0039 decisions 1–4 as amended by ADR 0040,
   plus this ADR's decisions 1–3.** No shipped code changes here; this map produces
   decisions, and the evidence lives in `experiments/plane-accounting/`.

3. ⚠️ **`room-rectangles/solver_parts.py` binds `min_area` on the primary part and
   the shipped engine must not.** The rig is not edited — it is ticket 28's
   evidence and re-running it would invalidate ADR 0014's own numbers — so this is
   carried as an obligation on the build and as a correction to
   `project_join.py` LIMIT 3's caveat, which now has a price: **1,76 %**.

4. ⚠️ **Two rectangles are an L only 55,2 % of the time, and three artifacts say
   always.** Over the 1 535 two-part Rooms of the converted index: **847 L, 332 T,
   329 Z, 27 rectangle** — **44,8 % do not have exactly one reflex corner**.
   `room-rectangles/erosion_check.py` closes with `assert n == 6 and reflex == 1`;
   ADR 0014 says *"exactly one reflex corner"*; `acceptance-bar.md` §9.1 says *"a
   rectilinear polygon with one reflex corner"*. **The identity survives** —
   `selftest_parts.py` P9 re-runs all three of `erosion_check.py`'s properties at
   two reflex corners on a T and a Z, pointwise and on integer millimetres — so
   ADR 0001 is untouched and this encoding is sound on all four shapes. What is
   wrong is a shape claim, and it touches ADR 0014's *argument* for the k ≤ 2 cap.
   Raised as *A two-part Room is a T or a Z as often as it is an L*.

5. **`acceptance-bar.md` §11.1 gains the two-part half, written rather than handed
   on.** The file has **no claimant** — ticket 77 declared it on resolution and
   nothing has claimed it since — so the correction is made here. Four paragraphs:
   the encoding generalises by one term at 13 variables; the Plan-level refusals at
   two parts are the **binding site** and not the seam, 5 of 284 rescued by §9.1's
   own rule; the cap paragraph's *"10 Rooms of 1 993"* is a `--parts=1` population
   whose twin is 10 of 1 961 and **no longer all bathrooms**; and the 15 s headroom
   at two parts starts from 31,7 % of candidates already at the cap. The escalation,
   the refused screen and the three steps are untouched.

6. **`CONTEXT.md`'s Space plane needs no edit.** It already reads
   `erode(⋃ parts, t_int/2)` — the union, not a rectangle — so the term this ADR
   adds is one the domain model already described and the encoding did not carry.

7. ⚠️ **The 15 s cap has materially less headroom at `--parts=2`, and that is
   Design A's, not this encoding's.** Recorded in decision 1. Any future pricing of
   the projection at two parts must start from 31,7 % of candidates already at the
   cap, not from Part II's percentiles.
