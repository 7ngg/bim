# Solver formulation for layout projection — findings

Research note for **ticket 04**, testing standing constraint **C10** (*model
proposes, solver projects*). Deliverable is this document plus the runnable toy
at `experiments/solver-toy/`.

Method note, and please read it before trusting anything below. Every number in
this document was **measured on this machine, in this session, by running the
code in `experiments/solver-toy/`**. Nothing is estimated, extrapolated, or
carried over from the sibling project. Where a claim is *not* backed by a run or
by a direct inspection of the installed OR-Tools package, it is tagged
**[UNVERIFIED]** and must be checked before it is built on. The literature half
of this ticket is materially thinner than the empirical half — see
[What this note does not establish](#what-this-note-does-not-establish).

---

## Verdict on C10

**GO, with one mandatory change to the architecture: the Proposal must carry a
relative arrangement, not just boxes, and the exact-tiling requirement must be
posted as a weighted soft constraint rather than a hard equality.** With those
two changes a 24-room layout inside a non-rectangular Envelope projects to a
**fully valid Plan in 6.25 s**; without either of them the same problem returns
**nothing at all** after 30 s.

That is a qualified go, and the qualification is the finding. C10 as loosely
stated — "hand the solver some boxes and it will project them" — is **refuted**
by measurement. C10 as amended here holds.

One consequence of the amendment must be carried with it. Promoting the
Proposal's arrangement to a hard constraint means a Proposal that contradicts the
Brief can now make the model **infeasible** — measured, and it happens in under
0.1 s. A **two-phase fallback is therefore mandatory**: try with the arrangement
fixed; on infeasible, drop it and re-solve from the boxes alone, which cannot
fail. Detection is nearly free, so this costs almost nothing — but leaving it out
would reintroduce the failure mode C10 exists to prevent.

The 24-room case, the one that matters because it is where the sibling project's
diffusion approach collapsed to 35.8–66.8 % room overlap, comes back at **0 %
overlap, 0 unassigned cells, all seven constraint families satisfied**, verified
by a checker that shares no code with the solver.

---

## What was measured

| | |
|---|---|
| CPU | Intel64 Family 6 Model 58 Stepping 9 (Ivy Bridge), **4 logical cores** |
| OS | Windows 11 Pro 10.0.26200 |
| Python | 3.12.10 |
| Solver | **OR-Tools 9.15.6755**, CP-SAT, Apache 2.0 (`pip install ortools`) |
| Workers | `num_workers = 4` for every run below |

This is a **modest 4-core desktop**, and that cuts both ways: CP-SAT's portfolio
search scales with cores, so these times are close to a worst case for a
developer machine and pessimistic for a server. They are not pessimistic for a
laptop.

### Scenarios

All three Envelopes are non-rectangular. Grid unit = **250 mm**; all coordinates
are integers, so orthogonality and grid snapping are properties of the variable
domains rather than constraints that can be violated.

| Rooms | Envelope | Interior | Required adj. | Forbidden adj. |
|---|---|---|---|---|
| 8 | L, 10.0 × 8.0 m less a 2.5 × 2.0 m corner | 1200 cells = **75.0 m²** | 4 | 1 |
| 12 | U, 13.0 × 10.0 m, two notches | 1888 cells = **118.0 m²** | 6 | 4 |
| 24 | U, 18.0 × 14.0 m, two notches | 3724 cells = **232.8 m²** | 15 | 22 |

Each Brief is generated **from a known-feasible ground-truth tiling**, and the
room types on that tiling are assigned by a small separate CP-SAT model that is
itself required to satisfy the type-dependent rules. The ground truth is then
re-checked by the independent validator and passes at all three sizes. This
matters: it means a failure to solve is a fact about the *projection problem*,
not about a Brief that was accidentally impossible. Without that guarantee the
whole timing table would be uninterpretable.

Model correctness was confirmed separately by pinning every room to its
ground-truth rectangle and re-solving. All three sizes return `OPTIMAL`:

| Rooms | Time to confirm the ground truth is admitted |
|---|---|
| 8 | **0.02 s** |
| 12 | **0.04 s** |
| 24 | **0.20 s** |

So the constraint model is right. Everything difficult below is *search*, not
modelling.

### The Proposal, and how broken it is

The Proposal is the ground truth with **independent Gaussian noise on each of
the four corners of each box** (σ = 0.5 m), seeded and reproducible. Per-corner
rather than per-box noise is deliberate: it produces overlap *and* unassigned
floor simultaneously, which is what a learned generator actually emits.

Measured corruption of the Proposals the solver was asked to repair:

| Rooms | Overlap, % of proposed room area | Unassigned interior | Area proposed outside the Envelope |
|---|---|---|---|
| 8 | **2.2 %** | **26.8 %** | 0 cells |
| 12 | **7.8 %** | **25.8 %** | 84 cells |
| 24 | **8.3 %** | **21.6 %** | 47 cells |

These sit inside the band the sibling project measured for HouseDiffusion at 8
rooms (5.8–12.8 % overlap) and well below its 24-room band (35.8–66.8 %). So the
repair job posed here is **easier than the real one at 24 rooms** and comparable
at 8. Read the 24-room timings as a lower bound on the real difficulty, not an
upper bound.

---

## The two headline findings

### Finding 1 — the hard exact-tiling equality is a propagation disaster

"Rooms tile the Envelope with no unassigned slivers" has an elegant encoding.
Given that every room is inside the bounding box, clear of the notches, and
pairwise non-overlapping, an exact tiling is **equivalent** to

```
sum_i (w_i * h_i)  ==  interior_area
```

one linear equation over `n` products. It is correct — the ground-truth test
above passes with it in force. It is also, as a *hard* constraint, close to
useless for search: `AddMultiplicationEquality` gives CP-SAT weak bounds
propagation, and a single equality over 24 such products propagates almost
nothing until the coordinates are nearly fixed.

Posting the identical requirement as a **soft** constraint —

```
sum_i (w_i * h_i)  ==  interior_area - slack ,   slack >= 0
minimise ... + 100000 * slack
```

— changes the search completely, because CP-SAT can now reach a feasible region
early and let the objective close the gap. Measured, 12 rooms, 60 s limit:

| 12 rooms, hard vs soft coverage | Time to first feasible Plan |
|---|---|
| exact tiling as a **hard** equality | **42.79 s** |
| exact tiling as a **soft** penalised equality | **1.49 s** |

**a 29× speedup**, and the returned Plan still had `slack = 0` — a genuinely
exact tiling, confirmed by the independent validator. The penalty weight
(100 000, against an objective whose optimum is in the tens) makes any nonzero
slack lexicographically worse than any amount of displacement, so softening it
does not quietly trade tiling away for a prettier fit. It only changes how the
solver *gets there*.

This generalises: **anything in the Acceptance bar that is cheap to satisfy but
expensive to propagate should be posted soft with a dominating weight.** That is
an implementation technique, not a weakening of C6.

### Finding 2 — boxes alone are not enough; the Proposal must carry arrangement

With the Proposal supplying only boxes (used as an `AddHint` and as the
objective), CP-SAT finds **nothing** for 12 or 24 rooms:

| Rooms | 20 s, boxes only, hard coverage | Model size |
|---|---|---|
| 8 | `FEASIBLE`, first Plan at **0.53 s** | 694 vars / 1521 constraints |
| 12 | `UNKNOWN` — **no Plan found** | 1871 vars / 3997 constraints |
| 24 | `UNKNOWN` — **no Plan found** | 7601 vars / 15910 constraints |

The hint is doing real work even so — removing it makes 12 rooms find nothing in
**60 s** where the hinted run eventually found one at 42.79 s — but a hint is
only a starting point CP-SAT is free to abandon, and it abandons this one.

The fix is to use the Proposal for what it is actually good at. For each pair of
rooms, take the cheapest of the four ways to pull the Proposal's two boxes apart
(*i* left of *j*, *j* left of *i*, *i* below *j*, *j* below *i*) and **post that
relation as a hard linear constraint** — `x2_i <= x1_j` and so on. Relations are
added greedily in increasing separation cost, and only when they keep the
per-axis relation digraph acyclic; the pairs the Proposal is not confident about
are simply left to `AddNoOverlap2D`'s disjunction.

This is the ticket's *hybrid*, with the Proposal standing in where the ticket
imagined a rectangular dual: **topology is decided by the model, metrics by the
solver.** It converts the packing problem's `4·C(n,2)` disjunction — the source
of essentially all the combinatorial difficulty — into linear inequalities. At
24 rooms all 276 pairs were fixable without creating a cycle.

---

## Measured timings

`num_workers = 4`, 30 s limit, seed 20260817, hint from the Proposal in every
row. **`first Plan`** is wall-clock to the first feasible, fully valid Plan —
the number that decides whether this feels interactive. `obj` is the final
objective: summed L1 displacement of all four corners of all rooms, in grid
units of 250 mm.

⚠️ **Single seed, one machine, 100 % exterior exposure, areas in grid units.**
Part II re-measures every row across seeds, exposure and ADR 0001's clear
reading; the 24-room figure moves from 6.25 s to a median of 2.72 s once the
ground truth is held to the same reading the solver enforces.

| Rooms | Configuration | Status at 30 s | **First valid Plan** | obj | Relations fixed | Independent validator |
|---|---|---|---|---|---|---|
| 8 | boxes only, hard coverage | FEASIBLE | **0.53 s** (20 s run) | 78 | 0 | **VALID** |
| 8 | boxes only, soft coverage | FEASIBLE | **0.75 s** | 42 | 0 | **VALID** |
| 8 | +relations, hard coverage | FEASIBLE | **1.31 s** | 50 | 28 | **VALID** |
| 8 | **+relations, soft coverage** | FEASIBLE | **0.35 s** | 50 | 28 | **VALID** |
| 12 | boxes only, hard coverage | UNKNOWN | **none in 30 s** (42.79 s at 60 s limit) | — | 0 | — |
| 12 | boxes only, soft coverage | FEASIBLE | **0.99 s** | 123 | 0 | **VALID** |
| 12 | +relations, hard coverage | FEASIBLE | **12.82 s** | 68 | 66 | **VALID** |
| 12 | **+relations, soft coverage** | FEASIBLE | **1.35 s** | 68 | 66 | **VALID** |
| 24 | boxes only, hard coverage | UNKNOWN | **none in 30 s** | — | 0 | — |
| 24 | boxes only, soft coverage | FEASIBLE | 22.35 s | 14 102 001 | 0 | **INVALID** — 141 interior cells unassigned |
| 24 | +relations, hard coverage | UNKNOWN | **none in 30 s** | — | 276 | — |
| 24 | **+relations, soft coverage** | FEASIBLE | **6.25 s** | 166 | 276 | **VALID** |

Read the 24-room block carefully, because it contains the whole argument:

- boxes only, hard coverage → **nothing**.
- relations, hard coverage → **nothing**.
- boxes only, soft coverage → something, but the objective 14 102 001 decodes as
  141 units of coverage slack at weight 100 000 plus 2001 units of displacement.
  It is a **plan with 141 unassigned interior cells (8.8 m² of floor belonging to
  no room)**, and the independent validator correctly rejects it. This is the
  failure mode softening is supposed to risk, and it does occur — it is caught,
  not hidden.
- **both together → a valid Plan in 6.25 s** with slack driven to zero.

Neither half works alone at 24 rooms. Both together do.

### How far the solver had to move the Proposal

| Rooms | obj (grid units) | Total corner displacement | Mean per coordinate |
|---|---|---|---|
| 8 | 50 | 12.5 m over 32 coordinates | **0.39 m** |
| 12 | 68 | 17.0 m over 48 coordinates | **0.35 m** |
| 24 | 166 | 41.5 m over 96 coordinates | **0.43 m** |

Sub-half-metre mean corner movement, from Proposals carrying 21–27 % unassigned
floor. The projected Plan still reads as the layout the model proposed. That is
the property C10 is actually buying, and it survives to 24 rooms.

### An honest caveat on optimality

> **Part II sets the number this section leaves open: the shipped time limit is
> 15 s**, the p95 of time-to-VALID pooled over 159 solves, catching 96.5 % of
> every run that ever reaches a valid Plan. On expiry, a best solution whose
> objective is at or above `soft_weight` has unassigned floor and must be
> discarded, not shown.

**No run in this table reached `OPTIMAL` within its time limit.** Every one
terminated at `FEASIBLE`, meaning CP-SAT had a valid Plan and a proof that it
could not rule out something better. At 8 rooms / 20 s the best bound was 25.0
against an objective of 78, so the true optimum lies somewhere in between and the
returned Plan is within roughly 3× of it in the worst case.

This is fine, and it should be designed for rather than fought. The product does
not need the provably nearest Plan; it needs a valid Plan that still looks like
the Proposal, quickly. CP-SAT's anytime behaviour delivers exactly that — the
solution callback shows a steady improving stream (8 rooms: objective 302 at
0.53 s, 255 at 1.02 s, 201 at 2.95 s, 124 at 6.59 s). **Treat the time limit as a
product parameter and take the best Plan found.** Do not wait for `OPTIMAL`.

---

## The recommended formulation

**CP-SAT over integer grid coordinates, with the Proposal supplying the relative
arrangement, and connectivity encoded as single-commodity flow over a reified
contact graph.** Not MIP, not a rectangular dual, not pure box packing.

Per room *i*: integer variables `x1, x2, y1, y2, w, h` in grid units, plus an
interval variable per axis and an area variable `a = w·h`.

| # | Requirement | Encoding | Cost |
|---|---|---|---|
| H1 | Inside the Envelope | Variable domains give the bounding box; each notch enters `AddNoOverlap2D` as a **fixed** interval pair, so a non-rectangular boundary costs nothing extra | free |
| H2 | No room overlaps | `AddNoOverlap2D` over all room intervals *and* the notches | cheap, strong propagator |
| H3 | Exact tiling, no slivers | `sum(w_i·h_i) == interior_area - slack`, **soft**, weight 100 000 | see Finding 1 |
| H4 | Min width / height / area per type | linear bounds on `w`, `h`; `AddMultiplicationEquality` for area | area products are the weak spot |
| H5 | No unusable slivers | `w <= k·h` and `h <= k·w`, k = 4 | linear, free |
| H6 | Required adjacency | reified contact literal forced to 1 | ~15 booleans per pair |
| H7 | **Forbidden** adjacency | reified contact literal at threshold 1 forced to **0** | same machinery, opposite sign |
| H8 | Habitable rooms touch an exterior wall | disjunction over exterior faces, forward-implication only | no auxiliary integers |
| H9 | Wet rooms on shared plumbing walls | single-commodity flow over the wet subset | reuses H6 literals |
| H10 | Circulation without traversing a bedroom | single-commodity flow, private rooms forbidden to forward | reuses H6 literals |
| — | Orthogonal, grid-snapped | integer variables | free, cannot be violated |

Two encoding tricks are worth carrying into the real implementation because they
remove a large number of auxiliary integer variables:

**Overlap without `min`/`max` variables.** `min(hi_i,hi_j) − max(lo_i,lo_j) >= L`
is *exactly* the conjunction of four linear inequalities — `hi_i−lo_i >= L`,
`hi_j−lo_j >= L`, `hi_j−lo_i >= L`, `hi_i−lo_j >= L` (check all four min/max
cases). The first two are per-room size bounds, usually already implied by the
Brief's minimum dimensions, in which case they are dropped statically. No
`AddMinEquality`/`AddMaxEquality`, no integer auxiliaries, and the whole thing
reifies as a conjunction of four cheap linear literals.

**Exterior access needs only forward implication.** We force the disjunction, and
a true face literal entails a real flush contact; nothing in the model needs the
converse. Half the reification disappears.

### Why not MIP

Not tested here, so this is judgement rather than measurement. The disjunctive
no-overlap constraint in MIP is the classic big-M four-way disjunction with a
binary per pair per direction — the same `4·C(n,2)` combinatorial core, but with
big-M's notoriously weak LP relaxation instead of CP-SAT's dedicated
`NoOverlap2D` propagator. The hybrid's contribution is to *remove* that
disjunction; once removed, most of the remaining model is linear and a MIP would
be competitive. But the parts that are not linear — the area products, and above
all the reified contact literals feeding the flow constraints — are exactly what
CP-SAT does better than a branch-and-bound LP. **[UNVERIFIED]** — worth one
afternoon with HiGHS or SCIP before the decision is locked, but the burden of
proof is on MIP.

### Why not a rectangular dual

The ticket's intuition — that a rectangular-dual construction satisfies topology
by construction and uniquely supports forbidden adjacency — turns out to be
backwards on the second half, and that is worth stating plainly.

In this formulation a forbidden adjacency is *the same machinery as a required
one with the sign flipped*: `m.Add(contact_ij == 0)` against a threshold of one
grid unit. It cost nothing to add and the 24-room Brief carries 22 of them
without difficulty. There is no asymmetry to exploit.

Meanwhile a rectangular dual gives topology by construction only for adjacency
graphs that admit one at all, and the classical characterisation is restrictive —
the graph must be planar, internally triangulated, and free of separating
triangles. A learned model emitting an arbitrary adjacency graph will routinely
emit graphs outside that class, and there is no graceful degradation available
when it does: the construction either succeeds or does not exist. That is the
opposite of what C10 wants. **[UNVERIFIED]** — the theorem statement is from
memory (Kozminski & Kinnen; Bhasker & Sahni) and must be checked against the
primary sources before this reasoning is cited anywhere load-bearing.

The one thing the dual construction does buy — a guaranteed-consistent topology —
is bought here more cheaply by Finding 2's relation extraction, which gets a
consistent arrangement from the Proposal by a greedy acyclic construction and
degrades to "leave it to the disjunction" for pairs it cannot decide.

---

## "Nearest to the Proposal" as an objective

Implemented and measured: **L1 displacement of all four corners**, summed over
rooms, minimised.

```
min  sum_i ( |x1_i − px1_i| + |x2_i − px2_i| + |y1_i − py1_i| + |y2_i − py2_i| )
```

Each absolute value needs one auxiliary variable and two inequalities
(`d >= e`, `d >= −e`; the one-sided form suffices under minimisation, so
`AddAbsEquality` is not needed). Four per room, 96 at 24 rooms. Entirely linear,
and CP-SAT's objective handling is happiest with exactly this shape.

Why this and not the alternatives:

- **Centroid displacement** (implemented as an option, not benchmarked) uses two
  terms per room instead of four but is blind to size and proportion. A room can
  sit at the proposed centre at half the proposed area and score zero. Since the
  Proposal's whole contribution is plausibility of *proportion* as well as
  position, this discards half the signal.
- **IoU / Jaccard** is the metric one instinctively wants, and it is the wrong
  choice here. Intersection area is expressible (`min`/`max` per axis, then a
  product), but the union in the denominator makes IoU a **ratio**, requiring
  `AddDivisionEquality` per room inside the objective. That is a nonlinear
  constraint on a variable denominator, and it would land in the objective where
  it does the most damage to bounds propagation. Not attempted; the cost is
  obviously not worth it when L1 corners already keeps mean displacement under
  half a metre.
- **Relative-order preservation** — penalising each pair whose Proposal
  left-of/below relation is broken — is implemented as an optional additive term
  and was **not benchmarked**. It is now largely redundant: Finding 2 promotes
  exactly those relations from a soft penalty to a hard constraint, which is
  strictly stronger and much faster. The soft version's remaining use is as the
  fallback for the pairs the greedy acyclic construction declined to fix.

CP-SAT's objective is integer-only, which is not a limitation once coordinates
are in grid units — displacement is a count of grid steps and is naturally
integral. This is one more reason integer grid coordinates are the right base
representation rather than a compromise.

---

## Is reachability expressible as a constraint? Yes.

This was flagged in the ticket as possibly needing a post-filter. It does not.

**Every room reachable from the entry without passing through a bedroom or
bathroom** is expressible as a hard constraint, it stays linear, and it is in
force in every measured run above.

The encoding is **single-commodity flow over a variable graph**:

1. For each room pair, a reified boolean `door_ij` that is true exactly when the
   two rooms share a wall segment at least a door's width long. The graph is not
   given — it is a consequence of the geometry the solver is choosing.
2. A directed integer flow variable per arc, capped by its literal:
   `f_ij <= (n−1) · door_ij`. Flow can only travel through walls that actually
   exist in the solution.
3. The entry room supplies `n−1` units; every other room consumes exactly 1.
   Conservation is a linear equality per room.
4. **The circulation rule itself is one extra line**: for every bedroom,
   bathroom and WC, `sum(outgoing flow) == 0`. A private room may *receive* its
   unit — you can reach the bedroom — but may never forward one. It is a sink,
   never a corridor. That is precisely "you do not walk through a bedroom to
   reach the kitchen", and it is a linear constraint on integer variables.

The same routine, instantiated over the wet-room subset with no blocked nodes,
gives H9 wet-room clustering — one plumbing-connected cluster rather than
scattered bathrooms. Writing it once and calling it twice is not an
optimisation; it is the observation that "reachable" and "clustered" are the same
constraint with different node sets.

Two consequences worth carrying forward:

- **Circulation is not a filter, it is a shape.** Because it is a constraint,
  CP-SAT will *rearrange the geometry* to make circulation work, rather than
  generating plans and discarding the ones that fail. This is a large part of why
  the 24-room result is valid on the first Plan returned rather than the
  hundredth.
- **It softens cleanly.** Adding a per-room slack boolean to the conservation
  equality, and reducing the entry's supply by the number of slacks, yields
  "this room could not be reached" as a *scored, reportable* outcome instead of a
  failure. That is the exact shape of the message a Homeowner should see.

`AddCircuit` and `AddMultipleCircuit` both exist in the installed package
(verified by direct inspection of `ortools 9.15.6755`) and are the usual CP-SAT
route to connectivity via a Hamiltonian-circuit encoding with self-loops meaning
"node not visited". They were **not used and not benchmarked**; the flow
encoding was chosen because the "may enter but may not traverse" rule for private
rooms drops straight out of it as a single equality, and because it softens per
room. **[UNVERIFIED]** whether `AddCircuit` would be faster.

---

## What happens when the Proposal is infeasible

The structural answer is the important one, and it is a property of the
formulation rather than a recovery heuristic:

> **The Proposal appears only in the objective and in the solution hint. It never
> appears in a constraint. It therefore cannot make the model infeasible, however
> bad it is.**

> ⚠️ **Corrected by the ticket-15 sweep — see Part II.0.** This holds only with
> `fix_relations=False`. In the *recommended* configuration the extracted
> relations are hard constraints, and a merely **noisy** Proposal — not just the
> adversarial shuffled one below — goes INFEASIBLE: 3 of 5 seeds at 8 rooms and
> **5 of 5 at 24 rooms** at σ = 1.0 m of per-corner noise, against σ = 0.5 m in
> every run on this page. τ is the valve, and the two-phase fallback is
> mandatory rather than prudent.

There is no such thing as an "infeasible Proposal" in this design. A Proposal
that is nonsense simply makes the objective large; the feasible set is untouched,
and the solver returns the nearest feasible Plan to whatever nonsense it was
given. Graceful degradation is not a feature that had to be added — it is what
you get for free by refusing to let the Proposal be a constraint. **This is the
single most important design rule to carry out of this ticket.**

Measured, with two deliberately hostile Proposals, 30 s limit:

| Rooms | Hostile Proposal | Relations fixed? | Result | First valid Plan |
|---|---|---|---|---|
| 8 | **degenerate** — every room a 1×1 box at the origin | no | FEASIBLE | **0.17 s**, VALID |
| 12 | degenerate | no | FEASIBLE | **0.59 s**, VALID |
| 24 | degenerate | no | UNKNOWN | **none in 30 s** — *Part II: FEASIBLE 6/6, valid **0/6***. Returns a Plan with unassigned floor rather than timing out. |
| 8 | **shuffled** — correct boxes, wrong rooms | yes | **INFEASIBLE in 0.02 s** | — |
| 12 | shuffled | yes | **INFEASIBLE in 0.05 s** | — |
| 24 | shuffled | yes | **INFEASIBLE in 0.08 s** | — |

The degenerate rows confirm the structural claim exactly. A Proposal carrying
*zero* information — every room collapsed to a single grid cell in one corner —
still yields a fully valid Plan at 8 and 12 rooms, in well under a second. Note
what the solver does *not* do: it never reports `INFEASIBLE`. At 24 rooms it
returns `UNKNOWN`, i.e. "I ran out of time", not "this is impossible" — which is
the correct and honest failure. But it is still a failure: **a worthless Proposal
costs you the 24-room case entirely**, because with no arrangement to extract
there are no relations to fix and we are back in Finding 2's dead configuration.
The Proposal is not load-bearing for *correctness*; it is load-bearing for
*tractability at scale*.

The shuffled rows confirm the caveat I expected and make it a measured fact
rather than a worry. The *hybrid* of Finding 2 breaks the never-infeasible
guarantee, because it promotes Proposal-derived relations to hard constraints. A
Proposal whose arrangement contradicts the Brief makes the model genuinely
infeasible, and CP-SAT says so in under a tenth of a second at all three sizes.

Two mitigations are already implemented and neither is sufficient on its own: the
greedy acyclic construction refuses any relation that would close a cycle (so the
fixed set is internally consistent — it just may be inconsistent with the
*Brief*), and a `relation_confidence` threshold fixes only relations where the
best separation direction beats the second-best by a margin.

**The two-phase fallback is therefore mandatory, not prudent.** Attempt with
relations fixed; on `INFEASIBLE`, drop the relations and re-solve with boxes
only, which cannot be infeasible. The good news is that the failing branch costs
**under 0.1 s** to detect, so the fallback is nearly free. **[NOT MEASURED]** —
the two-phase controller itself was not implemented or timed; only its two halves
were, separately.

### An infeasible Brief

A different and real problem — the Homeowner asked for something impossible.
Measured at 12 rooms, with one room pair listed as **both required and forbidden**
adjacent:

| Configuration | Result | Diagnosis quality |
|---|---|---|
| all constraints hard | **INFEASIBLE in 0.04 s** | assumption core named **all five** families — useless |
| all five families soft | **FEASIBLE, first Plan at 1.27 s** | objective 100 072 decodes as **exactly one** required-adjacency violation; the independent validator named it: *"H6 required adjacency bedroom1–utility3 missing"* |

**Negative result worth recording: the assumption-core route did not work.**
CP-SAT's `AddAssumptions` / `SufficientAssumptionsForInfeasibility` are present
in 9.15.6755 and do return a sufficient set, but "sufficient" is not "minimal",
and here it returned every one of the five constraint families for every
infeasible case tested. That is technically correct and practically worthless —
it says "one of your requirements is wrong" when we already knew that.

**The soft-constraint route is the one to build on.** Posting every family soft
with a dominating weight and reading the violated literals off the returned
solution gave a precise, single-requirement diagnosis in 1.27 s, and it names the
exact room pair. It is also strictly more useful than a core, because it hands
back a *Plan* alongside the complaint — the nearest thing to what was asked for,
with the one broken requirement flagged. That is the right shape for the message
a Homeowner sees under C4.

Known remaining gap: minimum dimensions and areas are not in the softenable set,
so a Brief that is impossible purely because the rooms cannot fit in the Envelope
will still fail hard with no useful explanation. That family must be added before
this is usable in product.

---

## `kiwisolver` for the deferred interactive-drag case (C7)

**A second model, not this one. And it cannot replace this one.**

`kiwisolver` is an implementation of the Cassowary algorithm: an incremental
solver for systems of **linear equality and inequality constraints with
priorities/strengths**. The word doing the work is *linear*. Cassowary has no
representation for a **disjunction**, and non-overlap of two rectangles is
irreducibly a disjunction — *i* is left of *j* **or** right **or** above **or**
below. A linear constraint solver cannot express "at least one of these four
holds"; it can only be told which one holds.

That is not a defect, it is a division of labour, and it maps onto C7's two
halves exactly:

- **CP-SAT decides topology.** Which room is left of which, who touches whom, who
  reaches whom. Combinatorial, slow (seconds), runs on regenerate.
- **kiwisolver maintains metrics.** Once the topology is fixed — and after a
  CP-SAT solve it *is* fixed — every remaining requirement is linear: wall
  positions, minimum dimensions, alignment, "these two walls stay flush", "this
  room keeps its width". Cassowary re-solves that incrementally at frame rate
  while a Practitioner drags a wall, with strengths expressing which
  requirements bend first.

So: **the same constraints, expressed twice, at two different tiers.** The
formulations are not shared and should not be forced to share. What *must* be
shared is the Acceptance bar's predicate definitions (ticket 07), so the two
tiers cannot drift — which is what CONTEXT.md already demands of the Acceptance
bar for a different reason.

The handover rule falls out cleanly: **a drag that only changes metrics is
kiwisolver's; a drag that changes topology — a wall crossing another wall, a room
losing its last contact with the hall — invalidates the linear system and must
escalate to a CP-SAT re-solve.** Detecting that escalation is the design problem
C7 will actually have to solve.

**[UNVERIFIED]** — this section is reasoned from the algorithm's nature, not from
a run. `kiwisolver` was not installed or benchmarked in this session. Confirm
against `kiwisolver.readthedocs.io`, `github.com/nucleic/kiwi`, and the Cassowary
paper (Badros, Borning & Stuckey, ACM TOCHI 2001) before C7 is designed against
it. The licence claim (BSD) was not verified either.

---

## What this note does not establish

Listed plainly, because a research note that hides its gaps is worse than one
that has them.

**Not measured at all:**

- **Grid resolution sweep.** Everything ran at 250 mm. The effect of 100 mm
  (≈6× the domain size in cells) or 500 mm on solve time is unmeasured, and it is
  the most obvious remaining lever — 100 mm may be needed for real wall
  thicknesses under C3.
- **The two-phase controller** described above. Both of its halves were measured
  separately; the controller that switches between them was not built.
- **`arc_radius` pruning.** Implemented — restricting candidate adjacency pairs
  by Proposal distance to shrink the `O(n²)` contact machinery — never run.
- **A 24-room degenerate-Proposal recovery.** The one configuration that returned
  nothing. Whether soft-everything, a longer limit, or more workers rescues it is
  unknown, and it is the natural next experiment.
- **`AddCircuit` as an alternative to flow** for connectivity.
- **Multiple seeds.** Every timing is a **single run at seed 20260817**. There is
  no variance estimate. CP-SAT's portfolio search is stochastic across workers;
  these numbers could move materially on a re-run and must be repeated over
  ≥10 seeds before any of them is quoted as a specification.
- **MIP, and a rectangular-dual construction.** Neither was implemented. The
  arguments against them above are reasoning, not evidence.
- **Wall thickness.** The toy places *room rectangles* that tile exactly. Real
  walls have thickness and the rooms do not touch — they are separated by wall
  bodies. Whether the exact-tiling formulation survives the introduction of wall
  thickness is **unknown and is the largest open risk to this result**. It
  interacts directly with ticket 01.

**Literature half, largely not done.** The intended primary-source survey did not
complete. Everything in this note about MIP formulations, rectangular-dual
theory, the facility-layout literature, published runtimes for comparable
methods, and kiwisolver/Cassowary is tagged `[UNVERIFIED]` and rests on
recollection. The *empirical* half — every number in every table — is sound and
reproducible. Treat the two halves differently.

**Verified by direct inspection of the installed package** (`ortools 9.15.6755`):
`AddNoOverlap2D`, `AddMultiplicationEquality`, `AddAbsEquality`,
`AddMaxEquality`, `AddMinEquality`, `AddCircuit`, `AddMultipleCircuit`,
`AddElement`, `AddAssumption`/`AddAssumptions`,
`SufficientAssumptionsForInfeasibility`, `AddHint`, and the solver parameters
`max_time_in_seconds`, `num_workers`, `num_search_workers`,
`log_search_progress`, `random_seed`, `cp_model_presolve`, `relative_gap_limit`,
`symmetry_level` all exist. CP-SAT returns `FEASIBLE` with a best-so-far solution
on timeout rather than failing — observed in every timed-out run above.

---

## What this formulation requires the Proposal to look like

**This section is the input to ticket 08 (*What the model proposes*). It is
written to be consumed directly and stands alone.**

The Proposal is what the learned model emits and the solver's objective consumes.
It is never a constraint and never the output. Given the findings above, it must
carry the following, and nothing here is optional unless marked so.

### Required

1. **A fixed room set with types.** Exactly *n* rooms, each with a type drawn
   from the Brief's vocabulary. The solver does not invent, merge, split or drop
   rooms — room count and room identity are fixed before the solve. If the model
   wants to propose a different room count, that is a different Brief and a
   different solve.

2. **One axis-aligned box per room**, as four integers `(x1, y1, x2, y2)` in
   **grid units of the Envelope's grid**, not normalised floats, not pixels, not
   metres. The model may emit continuous values but the contract boundary is
   integer grid units, and rounding happens on the model's side of it so that the
   solver's objective is exactly the distance the model intended.

3. **Boxes may be arbitrarily bad.** They may overlap, leave gaps, exit the
   Envelope, violate minimum dimensions, and contradict the Brief's adjacencies.
   Measured tolerance in this study: 21–27 % of the interior unassigned, 2–8 %
   overlap, boxes outside the Envelope. **No validity guarantee whatsoever is
   required of the Proposal, and the model must not be trained to produce one at
   the cost of plausibility.** Producing a *valid* layout is the solver's job and
   the model will do it worse.

4. **A relative arrangement the boxes actually encode.** This is the finding that
   changes the contract, and it is the one that must not be lost. The solver
   extracts, for every pair of rooms, which of *left-of / right-of / above /
   below* the Proposal intends, from the four separation costs between the boxes.
   Therefore what the model is really being asked for is a **consistent relative
   arrangement**, with the boxes as its carrier. Two consequences for training
   and evaluation:
   - The model must be **scored on relative arrangement**, not only on box
     regression. A Proposal whose boxes are 30 cm off but whose left/right/above/
     below relations are all correct is *much* more useful to this solver than
     one with lower box error and scrambled relations. Evaluate accordingly.
   - Because the extraction takes the **cheapest** separation per pair, room
     boxes should be **separated in the direction the model means** even when
     they overlap. Overlap depth is the signal; a pair whose four separation
     costs are near-equal contributes nothing and will be discarded by the
     confidence threshold.

5. **Confidence, or something that stands in for it — optional but valuable.**
   The relation extraction takes a margin between best and second-best separation
   as a proxy for confidence. If the model can emit a genuine per-pair or per-box
   confidence, the solver will fix the confident relations and leave the rest
   free, which is strictly better than the geometric proxy. If it cannot, the
   proxy works; this is a *nice-to-have*, not a blocker.

### Explicitly not required

6. **No adjacency graph is needed** as a separate output. Required and forbidden
   adjacencies come from the **Brief**, not from the model — they are what the
   Homeowner asked for, and they are hard constraints. If the model also emits an
   adjacency graph it is redundant at best and, if treated as a constraint, is a
   direct violation of C10. A model-emitted graph may be used as an *additional
   soft objective term* if it measurably improves output, but it must never enter
   the constraint set.

7. **No wall geometry, no thicknesses, no openings, no door positions.** The
   Proposal is rooms only. Everything with a thickness is produced downstream from
   the projected Plan (tickets 01 and 11).

8. **No guarantee of tiling, connectivity, exterior access, or wet clustering.**
   All are constraints and all are the solver's responsibility.

9. **No ordering guarantee between Proposals.** Each is projected independently.

### Contract shape

```
Proposal := {
    rooms: [ { id: int,                 # stable, matches the Brief
               type: str,               # from the Brief's vocabulary
               box: (x1, y1, x2, y2) }  # integers, Envelope grid units
             ... ],                     # exactly n, one per Brief room
    confidence: optional[ {(i,j): float} or {id: float} ]
}
```

### What this costs the model

The important negative: **the model does not need to learn feasibility, and
should not be asked to.** It needs to learn *plausible relative arrangement and
proportion*. That is a considerably easier learning problem than the one the
sibling project's diffusion model was failing at, and it is a strong argument for
ticket 08's cheaper routes — an LLM emitting an arrangement, or retrieval from a
corpus — being genuinely sufficient for v1 rather than a stopgap. A retrieved
real floor plan, warped to the Envelope, is an excellent Proposal under this
contract: its relative arrangement is by construction that of a real home.

---

## Reproducing this

```
pip install ortools
cd experiments/solver-toy
python smoke.py          # scenarios, ground-truth validity, Proposal corruption
python probe1.py         # boxes only, hard coverage, 20 s   -> Finding 2
python probe2.py         # model admits the ground truth     -> correctness
python probe3.py         # 12-room ablation, 60 s            -> Finding 1
python probe4.py         # the recommended configuration     -> the timing table
python probe5.py         # infeasible Proposals and Briefs
```

See `experiments/solver-toy/README.md`. Seed 20260817 throughout; every run is
deterministic in its inputs, though CP-SAT's multi-worker search is not
bit-reproducible in its timings.

---

# Part II — the variance sweep (ticket 15)

Everything above this line was measured **once, at one seed, on one machine, at
100 % exterior exposure, with areas posted in grid units**. Ticket 15 re-measured
it across seeds, room counts, dwelling-type exposure, Proposal quality, the
confidence margin τ, worker count, and ADR 0001's eroded-millimetre area rule.

**965 solves**, all serial at `num_workers = 4`, 30 s limit, on the same 4-core
Ivy Bridge (`DESKTOP-25OJ4QH`) every number in Part I came from. Harness:
`experiments/solver-toy/sweep.py`, aggregation `report.py`, raw rows in
`experiments/solver-toy/results/*.jsonl`.

Two corrections to Part I are load-bearing and are stated before the tables,
because Part I's own wording is wrong in both places.

## II.0 Two corrections to Part I

### The Proposal *can* make the model infeasible, on ordinary noise

Part I boxes this claim and calls it "the single most important design rule to
carry out of this ticket":

> The Proposal appears only in the objective and in the solution hint. It never
> appears in a constraint. It therefore cannot make the model infeasible, however
> bad it is.

**This is false in the recommended configuration.** `fix_relations=True` reads the
Proposal's relative arrangement and posts it as hard linear separations, which is
a constraint by any definition. Part I knew this for the *adversarial* shuffled
Proposal and treated it as a caveat. It is not a caveat. Measured with plain
Gaussian per-corner noise — the pathology a real generator emits, not an attack:

| σ per corner | n = 8 | n = 12 | n = 24 |
|---|---|---|---|
| 0.00 m | 0/5 | 0/5 | 0/5 |
| 0.25 m | 0/5 | 0/5 | 0/5 |
| **0.50 m — what every Part I run used** | 0/5 | **3/5** | 1/5 |
| 1.00 m | 3/5 | 4/5 | **5/5** |
| 2.00 m | 4/5 | 5/5 | 5/5 |
| 4.00 m | 5/5 | 5/5 | 5/5 |

INFEASIBLE counts, τ = 0, 30 s. Below σ = 0.25 m nothing fails anywhere; from
σ = 0.5 m — **the value every Part I run used** — it is already failing 3 of 5
seeds at 12 rooms, and by σ = 1.0 m the 24-room case is gone entirely.
**v1 does not sit below the cliff. It sits on the edge of it.**

Solve *time* barely moves across that range — at 8 rooms the median time to first
Plan goes 0.091 s to 0.101 s from σ 0 to σ 2, and at 24 rooms 2.36 s to 2.40 s
from σ 0 to σ 0.5. So the ticket's question, "sweep
degradation and find where solve time turns over", has an answer it did not
anticipate: **it never turns over. Proposal quality does not cost seconds. Past a
threshold it costs feasibility outright.**

The correct statement of the design rule is:

> The Proposal reaches the constraint system through exactly one channel — the
> relations `fix_relations` extracts — and τ is the valve on that channel. With
> `fix_relations=False` the original claim holds exactly and is worth its billing.
> With it on, which is the recommended configuration, the Proposal is load-bearing
> for feasibility and a two-phase fallback is mandatory rather than prudent.

### Part I's degenerate-Proposal row is optimistic at 24 rooms

Part I reports 24-room degenerate as `UNKNOWN` — "I ran out of time". Re-measured
over 6 seeds it is `FEASIBLE` 6/6 and **valid 0/6**: the solver does return a
Plan, and the Plan has unassigned floor every time. The conclusion Part I drew is
unchanged and slightly strengthened — *a worthless Proposal costs you the 24-room
case entirely* — but the failure is a silently invalid Plan, not a timeout, and
that is the more dangerous shape.

## II.1 The formulation cost of ADR 0001 — and the one-line fix

ADR 0001 makes a room's published rect the **clear** rect, `erode(solved, t_int/2)`,
so H4 and H5 bind on eroded dimensions in integer millimetres. Ticket 15 flagged
this as the sweep's most important question, because the operands move from ~10^2
to ~10^4 and the products to ~10^8, against H4 already being the formulation's
weak spot.

**Three encodings were measured against each other:**

| rig | what it posts |
|---|---|
| `grid` | H4/H5 on grid units. Part I's rig. Products ~10^4. |
| `mm_direct` | a second `AddMultiplicationEquality` on eroded millimetres. Products ~10^8. The form the ticket feared. |
| `mm_affine` | the same value, expanded algebraically. |

The `mm_affine` identity is exact and worth stating, because it removes the
question rather than answering it:

```
(g*w - t)(g*h - t) = g^2*(w*h) - g*t*(w + h) + t^2        g = 250, t = t_int
```

The eroded area is **affine in the grid-unit product**, so ADR 0001 needs **no
second multiplication at all**. Verified exact over all `w, h` in `[1, 79]`.

Median time to first Plan, 6 seeds, detached:

| n | `grid` | `mm_affine` | `mm_direct` | multiplications, grid to mm_direct |
|---|---|---|---|---|
| 8 | 0.100 | 0.090 | 0.105 | 8 to 16 |
| 12 | 0.353 | 0.263 | 0.303 | 12 to 24 |
| 24 | 3.001 | 2.712 | 2.869 | 24 to 48 |

**H4 survives, and the worry was unfounded.** Doubling the multiplication count
and moving the products to 10^8 is not measurable against the seed-to-seed
spread. `mm_affine` should still be preferred — it is free — but nothing
depended on it.

### What *did* bite: the minima are one grid unit too tight, and that is arithmetic

The real cost of the clear reading is not numeric. It is that

```
clear_w = 250*w - t_int  >=  min_w
```

forces `w >= (min_w + t_int)/250`, and when `min_w` is itself a multiple of the
grid — which every value in the placeholder standards table is — that ceiling
lands **one whole grid unit above** `min_w/250`. Every room becomes 250 mm wider
and 250 mm taller to pay for a 100 mm wall.

Exact tiling at 9.65 m² of interior per room, 3 seeds, `valid/seeds`, `*` marking
seeds where no Brief could be constructed at all:

| reading | n=4 | n=5 | n=6 | n=7 | n=8 | n=10 | n=12 |
|---|---|---|---|---|---|---|---|
| published — minima on the solved rect | 3/3 | 3/3 | 2/3 | 2/3 | 3/3 | 2/3 | 3/3 |
| **ADR 0001 — minima on the clear rect** | 0/3\* | 0/3\* | 0/3\* | 2/3 | 3/3 | 2/3 | 3/3 |
| **ADR 0001 + grid-aligned minima** | 3/3 | 3/3 | 2/3 | 2/3 | 3/3 | 2/3 | 3/3 |

The middle row **deletes 4-, 5- and 6-room dwellings**, which is the bottom half
of the 4–10-room band C13 promises. More area does not fix it: swept from +0 % to
+40 % interior area per room, 4 rooms never recovers and the response is not even
monotone, because Envelope shape re-snaps to the 250 mm grid as area changes
(`erosion_cost.py`).

The third row is the fix, and it is one rule:

> **A published clear minimum must satisfy `min + t_int` congruent to 0 modulo the
> grid.** A 1750 mm kitchen is published as 1650 mm, and `clear = 250w - 100`
> meets it at exactly the `w` the old reading needed. The wall is paid for in the
> number rather than in the grid.

Recorded as ADR 0007. It is a sibling of ADR 0004's even-millimetre rule — a
second arithmetic constraint the standards table must satisfy — and it lands on
*Ergonomic minima and the constraint table's missing half* and *The Azerbaijani
region profile*, which own the numbers.

### A harness defect worth recording

Until this was found, the ground-truth generator enforced the published reading
while the solver enforced the clear one, so **the ground truth stopped being a
witness** and the harness's central guarantee — *a failure to solve is a fact
about the projection problem, not about an accidentally impossible Brief* —
silently stopped holding. At n=4 the truth's kitchen was 7 grid units wide where
the clear reading needs 8, and its hall 5 where it needs 6. Every validity number
measured in that state was reporting the defect.
`scenarios.fits_kind(r, kind, clear_t)` now takes the reading as a parameter and
`sweep.py` passes whatever the solver will enforce. **All tables in Part II are
post-fix.**

## II.2 Exposure — and it does not do what was expected

ADR 0003 makes the Envelope an ordered ring of typed edges, and only an
`exterior` edge may hold a window. Presets, with the exterior share of perimeter
each actually achieves on this harness's Envelopes, against the Swiss Dwellings
distribution (`dataset-inventory.md` §1.5: p5 0.16, p25 0.23, median 0.37,
p75 0.47, p95 0.59):

| preset | edges exterior | achieved fraction | vs corpus |
|---|---|---|---|
| `detached` | all four | 1.00 | **above p95 — no real dwelling** |
| `terrace_mid` | S, N | 0.64 – 0.71 | above p95 |
| `flat_corner` | S, E | 0.53 – 0.60 | ~p95 |
| `corpus_median` | S, plus 45 % of N | 0.32 – 0.41 | **straddles the median** |
| `flat_single_aspect` | S | 0.19 – 0.22 | ~p25 |

Two of the four presets ADR 0003 named sit **above the corpus p95**, so
`corpus_median` was added, fitted to 0.37 — a partial edge, which is also the
honest shape, since a real flat's front elevation is commonly part glazing and
part shared.

**Expected: H8 becomes binding at low exposure and solve time rises. It does
not.** Median time to first Plan, 8 seeds, `mm_affine`, clear reading, τ = 0:

| n | detached | terrace_mid | flat_corner | corpus_median | flat_single_aspect |
|---|---|---|---|---|---|
| 8 | 0.094 | 0.078 | 0.092 | 0.103 | — |
| 10 | 0.154 | 0.136 | 0.138 | 0.148 | — |
| 12 | 0.264 | 0.244 | 0.295 | 0.291 | — |
| 16 | 0.543 | 0.646 | 0.820 | 0.633 | — |
| 20 | 1.867 | 0.947 | 1.384 | 1.464 | — |
| 24 | 2.717 | 2.086 | 2.938 | 2.935 | — |

Every column is inside every other column's seed spread. **Exposure is not a
timing axis.** Quartering the exterior face set does not make the solve harder,
because H8 is a disjunction over faces and a smaller disjunction is a *smaller*
model, not a tighter search.

What exposure does instead is fail **earlier and harder**, at Brief construction
rather than at solve time — which is the more useful finding, because it is
cheap to detect and cannot be tuned away.

### `flat_single_aspect` is arithmetically dead from 7 rooms, and no solver is involved

Habitable rooms do not overlap, so the stretches of exterior wall they occupy are
disjoint, and each consumes at least its own shorter minimum dimension. That is a
**necessary condition with no search in it**:

```
sum over habitable rooms of min(min_w, min_h)   <=   total exterior run
```

| n | habitable | need | `flat_single_aspect` has | verdict |
|---:|---:|---:|---:|---|
| 6 | 4 | 8 500 | 9 000 | ok, 500 mm slack |
| **7** | 5 | 10 500 | 9 500 | **dead by 1 000 mm** |
| 8 | 5 | 10 500 | 10 000 | dead |
| 12 | 7 | 14 500 | 13 000 | dead |
| 24 | 14 | 28 250 | 18 000 | dead by 10 250 mm |

All millimetres, `frontage.py`. Single-aspect flats sit at the corpus **p25**, so
this is not an exotic case. **H8 as posted forbids the commonest
restricted-aspect dwelling above 6 rooms**, and no time limit, seed, τ or
Proposal changes it. The sweep short-circuits these cells rather than solving
them, which is why they read `H8_IMPOSSIBLE`. Handed on as its own decision — see
the ticket.

### The nine windowless dwellings: corpus noise, and H8 stands

`dataset-inventory.md` §1.5 flagged "nine dwellings scored ~0.00 exterior —
genuinely windowless units, which would fail acceptance rule H8 outright and are
worth inspecting before they are treated as noise". Inspected
(`experiments/corpus-smoke/windowless_swiss.py`, same seed and sample):

The "nine" is the histogram's 0.00 **bucket**, which catches everything below
0.125. At a literal `< 0.02` there are **three**. All three carry **zero WINDOW
openings** on their boundary band, against a control where 88.4 % of all 569
scored dwellings have at least one and the median is 2 in every other exposure
band — so the 0.45 m party-gap heuristic is not mis-classifying them.

But their areas settle it: **14.1 m², 14.2 m² and 10.3 m²**, holding 6, 6 and 4
annotated rooms. Two of them place a LIVING_ROOM, KITCHEN, BEDROOM, BATHROOM and
two CORRIDORs inside 14 m² — 2.4 m² per room. The third has six door openings, no
windows, and a STOREROOM. These are annotation fragments, not homes.

**H8 is not rejecting homes that exist.** The rider is closed and H8 stands as
posted — the single-aspect finding above is a separate and real problem.

## II.3 The shipped time limit

Pooled over the whole S2 grid — 8 room counts by 5 exposures by 8 seeds, 159
solves that produced a Plan. **`valid_at`** is wall-clock to the first Plan with
zero coverage slack, i.e. the first Plan the independent validator accepts. It is
the same quantity Part I's table calls "first valid Plan".

| metric | p50 | p90 | p95 | max |
|---|---|---|---|---|
| time to first Plan | 0.39 s | 2.83 s | 3.39 s | 6.18 s |
| **time to a VALID Plan** | **1.56 s** | **10.79 s** | **13.65 s** | **25.06 s** |
| time to within 5 % of best | 3.35 s | 18.36 s | 23.45 s | 27.71 s |

Because every row carries its full improving-solution trace, any budget below
30 s can be answered exactly rather than extrapolated:

| budget | any Plan | VALID Plan | within 5 % | share of *eventually-valid* runs caught |
|---|---|---|---|---|
| 3 s | 93.1 % | 57.2 % | 48.4 % | 63.6 % |
| 5 s | 98.7 % | 62.9 % | 56.0 % | 69.9 % |
| 7.5 s | 100.0 % | 73.0 % | 67.3 % | 81.1 % |
| 10 s | 100.0 % | 79.9 % | 73.6 % | 88.8 % |
| **15 s** | 100.0 % | **86.8 %** | 87.4 % | **96.5 %** |
| 20 s | 100.0 % | 88.7 % | 92.5 % | 98.6 % |
| 30 s | 100.0 % | 89.9 % | 100.0 % | 100.0 % |

The VALID column plateaus at 89.9 % because 33 of 192 attempted solves are
INFEASIBLE and never become valid at any budget.

> ### Recommendation: **the shipped time limit is 15 s.**
>
> It is the **p95 of time-to-VALID** (13.65 s, rounded up to a round number) and
> catches **96.5 %** of every run that ever reaches a valid Plan. Doubling it to
> 30 s buys 3.1 further percentage points. Halving it to 7.5 s costs 15.4.
>
> Every candidate has *some* Plan by 7.5 s, so a progress indicator has something
> real to show well before the limit.

### What the system does when it expires

The failure mode that matters is not "no Plan". It is **a Plan that pays coverage
slack** — one with unassigned interior floor, which the objective reveals exactly,
because one unit of slack costs `soft_weight` = 100 000 and the corner objective
is O(10^2 to 10^3).

> On expiry, if the best solution's objective is **at or above `soft_weight`**, the
> candidate **has no survivor**. Discard it; do not export it and do not show it.

This is arithmetic, not a re-validation pass, and it matches what *Acceptance
validator spec* already settled for the zero-survivor case: diagnose, never show a
failing Plan. Part I's own 24-room "boxes only, soft coverage" row — objective
14 102 001, decoding as 141 unassigned cells — is exactly this shape, and it is
why the rule is needed rather than assumed.

## II.4 τ — the confidence margin, fitted

τ (`SolveConfig.relation_confidence`) is the margin by which a Proposal's best
separation must beat its second-best before that relation is fixed hard. Part I
never fitted it; the toy used whatever was convenient.

Its direction is as the ticket predicted — high τ fixes fewer relations and is
slower — but the ticket's framing missed what τ is actually for. **τ is the valve
on the only channel by which the Proposal reaches the constraint system**, so it
is a *feasibility* knob first and a timing knob second.

INFEASIBLE counts out of 4, Proposal noise σ against τ (suite S8):

**n = 8**

| σ | τ=0 | τ=2 | τ=4 | τ=6 | τ=10 | τ=16 |
|---|---|---|---|---|---|---|
| 0.50 m | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| 1.00 m | 2/4 | 1/4 | **0/4** | 0/4 | 0/4 | 0/4 |
| 2.00 m | 3/4 | 2/4 | 2/4 | 2/4 | 2/4 | **0/4** |
| 4.00 m | 4/4 | 4/4 | 4/4 | 3/4 | 2/4 | 2/4 |
| *valid, pooled* | 6/16 | 8/16 | 9/16 | 10/16 | 12/16 | **14/16** |
| *median time to first* | 0.10 | 0.11 | 0.12 | 0.14 | 0.14 | 0.18 |

**n = 24**

| σ | τ=0 | τ=2 | τ=4 | τ=6 | τ=10 | τ=16 |
|---|---|---|---|---|---|---|
| 0.50 m | 1/4 | 1/4 | 1/4 | 0/4 | 0/4 | 0/4 |
| 1.00 m | 4/4 | 4/4 | 2/4 | 1/4 | 1/4 | **0/4** |
| 2.00 m | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 2/4 |
| *valid, pooled* | 3/16 | 3/16 | 3/16 | 3/16 | 4/16 | 7/16 |
| *median time to first* | 3.12 | 3.50 | 3.53 | 5.42 | 7.60 | 5.34 |
| *median time to VALID* | 10.36 | 16.16 | 14.70 | 17.87 | 21.86 | **23.98** |

**The exchange rate is room-count dependent, and that is the finding.** At 8
rooms, τ = 16 more than doubles the valid rate for **+0.08 s**. At 24 rooms the
same move costs **+13.6 s on time-to-VALID**, which is past the 15 s limit — so at
24 rooms high τ does not buy a survivor, it buys a timeout.

> ### Recommendation: **τ = 4**, with the room-count caveat stated.
>
> In the 4–10-room band C13 promises, τ = 4 costs 0.02 s and removes the σ = 1.0 m
> cliff completely (2/4 INFEASIBLE to 0/4). It is free insurance in the band the
> product actually sells.
>
> Above roughly 16 rooms τ stops being free and starts trading against the time
> limit. Anything beyond the promised band should treat τ and the limit as one
> joint parameter, not two.

### Distinct Plans per Proposal: not measured, and honestly so

The ticket asks for "VALID-plans-per-Proposal against τ". Holding the Proposal
fixed and moving only CP-SAT's own random seed (suite S7, 4 runs per cell) gives
distinct-Plan counts of 4, 2, 2, 3, 1, 4 at n = 8 across τ = 0 to 10 — consistent
with no trend at all, and 4 runs per cell cannot separate a trend from portfolio
noise. **No claim is published.** The hypothesis that high τ leaves more
arrangements alive is untested, not refuted; testing it needs solution
enumeration under a diversity constraint, which is a different experiment.

## II.5 Failure modes, and a detection feature that does not work

6 seeds per cell, corpus-median exposure.

| n | Proposal | result | time to detect | valid |
|---|---|---|---|---|
| 8 | shuffled | INFEASIBLE 6/6 | 0.009 s | — |
| 12 | shuffled | INFEASIBLE 6/6 | 0.030 s | — |
| 16 | shuffled | INFEASIBLE 6/6 | 0.077 s | — |
| 24 | shuffled | INFEASIBLE 6/6 | 0.125 s (max 0.172) | — |
| 8 | degenerate | FEASIBLE 6/6 | first Plan 0.243 s | **100 %** |
| 12 | degenerate | FEASIBLE 6/6 | 0.542 s | **100 %** |
| 16 | degenerate | FEASIBLE 6/6 | 1.266 s | **100 %** |
| 24 | degenerate | FEASIBLE 6/6 | 5.046 s | **0 %** |

Detection of a topologically hostile Proposal is **immediate and perfectly
reliable** — under 0.2 s at every size, 24/24 runs. A two-phase fallback triggered
on INFEASIBLE therefore costs nothing to arm.

**But the infeasibility core is useless.** Every INFEASIBLE run in the sweep, at
every size and from every cause, returned the identical full set:

```
('circulation', 'coverage', 'exterior', 'required_adj', 'wet_cluster')
```

`SolveConfig.diagnose` names every softenable family every time and therefore
discriminates nothing. It should either be fixed to return a minimal core or
dropped; as it stands it is a feature that looks like diagnosis and is not.

## II.6 Hardware — the axis this machine cannot answer, and what it can

**Item 5 of the ticket asks for at least one modern-CPU figure. There is no
modern CPU here.** `platform.processor()` reports `Intel64 Family 6 Model 58`,
which is Ivy Bridge — the same 4-core desktop every number in Part I came from.
**This axis is unresolved and no figure is extrapolated for it.**

What the machine can answer is how the portfolio uses cores, which turns out to
be the more useful half:

| n | workers | median time to first | median time to within 5 % | median objective | valid |
|---|---|---|---|---|---|
| 8 | 1 | 0.099 | 0.80 | 43 | 100 % |
| 8 | 2 | 0.102 | 0.32 | 43 | 100 % |
| 8 | 4 | 0.097 | 0.22 | 43 | 100 % |
| 24 | 1 | 2.395 | 21.02 | **17 000 136** | **0 %** |
| 24 | 2 | 2.386 | 16.68 | 124 | **100 %** |
| 24 | 4 | 2.384 | 15.08 | 131 | **100 %** |

**Time to the first Plan is flat — 2.395 / 2.386 / 2.384 s at 24 rooms.** Cores
buy nothing there. What they buy is *correctness*: one worker at 24 rooms returns
an objective of 17 000 136 — 170 units of coverage slack — and never reaches a
valid Plan inside 30 s, while two workers reach 124 and 100 % validity.

So the honest statement to put in a spec, in place of the number that could not be
measured:

> More cores do not make the first Plan arrive sooner. They make the Plan that
> arrives correct. A faster or wider CPU should be expected to raise the share of
> candidates that survive within a fixed time limit, not to lower the limit.

**Two workers is the floor.** A single-worker deployment is not a slower product,
it is a broken one at the top of the room range.

## II.7 Drawing measurements

Taken off the same solved Plans, no extra solving (`drawing_metrics.py`). The
module reproduces `annotation.md` §14's worked example exactly — all four tier-2
chains tick-for-tick, tier 2b empty, A3 at 1:50, annotated extent 226 by 186 mm —
which is what licenses these numbers above five rooms.

| n | plans | walls | tier 2b | witnesses/side p50 | max | narrow-tick fires p50 | max | outside-text collisions | chains close | sheet |
|---|---|---|---|---|---|---|---|---|---|---|
| 8 | 28 | 7 | 2 | 4 | 6 | 6 | 7 | **0** | 28/28 | A3 1:50 |
| 10 | 28 | 9 | 3 | 6 | 8 | 6 | 6 | **0** | 28/28 | A3 1:50 |
| 12 | 24 | 11 | 4 | 8 | 8 | 7 | 7 | **0** | 24/24 | A2 x17, A3 x7 |
| 16 | 31 | 14 | 5 | 10 | 10 | 10 | 10 | **0** | 31/31 | A2 1:50 |
| 20 | 22 | 18 | 8 | 10 | 10 | 11 | 12 | **0** | 22/22 | A2 1:50 |
| 24 | 26 | 21 | 10 | 8 | 10 | 12 | 13 | **0** | 26/26 | A2 1:50 |

**1. Witnesses per side top out at 10.** A tier-2 chain never carries more than 10
witness faces, i.e. 11 segments, anywhere up to 24 rooms. The chain does not get
crowded, and at 24 rooms the median actually *falls* to 8 — because by then most
partitions reach no Envelope edge at all and drop to tier 2b.

**2. Tier 2b is not a fallback — it is half the drawing.** The spec introduces
running dimensions from datum as the case for "a partition reaching no Envelope
edge", phrased as an exception. Measured: 2 walls of 7 at n=8, and **10 of 21 at
n=24**. Nearly half of every large plan's partitions dimension this way, which
means the 2b rung is occupied on most sides and tier 1 sits at 34 mm rather than
26 mm as the common case, not the rare one. `annotation.md` §4.3 should be
reworded and the sheet arithmetic should assume 34.

**3. The narrow-tick rule fires constantly and never collides.** 6 to 13 times per
plan, exactly as predicted — every `t_int` tick is 2 mm paper against ~7 mm of
text. But **zero consecutive outside-text collisions in 159 plans**. §5a's second
sentence — "when two consecutive outside texts would themselves overlap, alternate
them above and below the dimension line" — **never fires up to 24 rooms**. It is
dead code for v1 and should be marked as such rather than built.

**4. The sheet ladder's top two rungs are unreachable.** A3 up to 10 rooms, A2
from 12, and **A1 is never reached** — so `(A1, 1:50)` and `(A1, 1:100)` are
unused at every size v1 will ship. The honest answer to "how many rooms to reach
A1" is: more than 24, at 9.65 m² per room. `(A1, 1:100)` in particular exists for
a dwelling this system cannot currently generate.

**5. Every chain closed.** 159 of 159 plans, all four sides, sums exact. Integer
millimetres deliver what ADR 0001 promised.

### A defect in `annotation.md` §14

The worked example states the narrow-tick rule "fires four times — the four
`t_int` ticks". Its own four chains contain **five**: South one, North two, West
one, East one. The reproduction agrees with every other number in §14 and
disagrees here, so §14's count is off by one.

## II.8 What Part II does not establish

- **No modern-CPU figure.** Item 5 is unanswered; see II.6.
- **Grid resolution was still never swept.** Everything ran at 250 mm. Ticket 15
  called this optional and it stayed optional; ADR 0007's alignment rule is stated
  in terms of the grid, so a change of grid changes the standards table.
- **Distinct Plans per Proposal is unmeasured** (II.4).
- **Room counts below 7 are measured only through the aligned-minima fix.** Under
  the unaligned table no 4-, 5- or 6-room Brief could be built, so the growth
  curve in the main grid starts at 8.
- **Percentiles are nearest-rank on 8 seeds per cell**, so a per-cell p90 and p95
  coincide with that cell's maximum. Only the pooled figures in II.3 (n = 159)
  carry meaningful tail percentiles; the per-cell tables should be read as median
  plus worst-of-eight.
- **`arc_radius` is still never benchmarked**, as in Part I.

## Reproducing Part II

```
cd experiments/solver-toy
python frontage.py                  # the H8 frontage budget, no solver involved
python sweep.py all --limit 30      # 965 solves, serial, ~3 h on 4 cores
python report.py                    # every table above
python erosion_cost.py              # area does not fix the clear reading
python grid_aligned_minima.py       # what does fix it
python ../corpus-smoke/windowless_swiss.py
```

Rows land in `results/*.jsonl`, one JSON object per solve, carrying the full
improving-solution trace so any time limit below 30 s can be re-derived without
re-solving. The file is resumable: re-issuing the same command skips rows already
present. **Run nothing else on the machine while sweeping** — an early pass was
discarded because a watcher script started a second solver concurrently.

---

# Part III — the non-guillotine re-base (ticket 29)

Everything above this line was measured against a **guillotine** ground truth.
`scenarios.ground_truth` dissects each Envelope part with `_guillotine`, a
backtracking recursive dissection, so every one of Part II's 965 solves — every
timing, every percentile, the whole feasibility cliff — had a target that some
sequence of full-width cuts takes apart.

The solver never restricted itself to those. `AddNoOverlap2D` admits any
rectangular tiling and there is no slicing structure anywhere in the formulation.
But *nothing had ever checked*, because nothing had ever handed it a target that
was not guillotine. A **pinwheel** — four rooms circling a central one, the
canonical real apartment plan, and the smallest non-guillotine rectangle tiling —
had not appeared in a single experiment on this map.

**483 solves** over 568 scenario slots — 85 slots never reached the solver, 72
because the Envelope admits no non-guillotine tiling and 13 because no Brief could
be typed. All serial at `num_workers = 4`, on the same 4-core Ivy Bridge
(`DESKTOP-25OJ4QH`) every number in Parts I and II came from. Harness
`experiments/solver-toy/sweep_ng.py`, generator `pinwheel.py`, aggregation
`report_ng.py`, raw rows in `results/N9*.jsonl`.

> ### Headline: **the solver does not care, and C10 is de-risked rather than qualified.**
>
> Paired across arms on the same Envelope, room count, exposure, seed and
> Proposal noise, over the whole main grid: **37 slots where both arms produced a
> survivor, 10 where neither did, 4 where only the guillotine arm did and 4 where
> only the pinwheel arm did.** Exact McNemar **p = 1.00**. At 8–16 rooms — which
> covers the whole of C13's promised band that this Envelope family reaches — the
> discordant count is **zero**: 35 slots, and in every one the two arms agree.
>
> Part II's shipped 15 s and τ = 4 both survive. What does *not* survive is the
> ticket's stated reason for expecting movement, and one number it inherited.

## III.0 Two corrections before the tables

### The premise about τ is refuted by measurement, not by the sweep

The ticket argues that "a pinwheel has a denser relation graph than a slicing
layout, so there is a specific reason to expect movement" in τ. The first half is
true and the second does not follow, because **τ does not gate on adjacency**.

Door-contact density is genuinely higher in the pinwheel arm at every room count
— 0.521 against 0.461 at 8 rooms, 0.364 against 0.333 at 10, 0.324 against 0.298
at 12. But τ (`SolveConfig.relation_confidence`) gates on the **separation
margin**: per room pair, second-cheapest minus cheapest separation, computed by
`solver.rank_relations` over the *Proposal*. Measured over 7 355 guillotine pairs
and 7 110 pinwheel pairs (`relation_margins.py`):

| arm | p10 | p25 | p50 | p75 | p90 | mean | share below τ = 4 |
|---|---|---|---|---|---|---|---|
| guillotine | 3.0 | 7.0 | 14.0 | 24.0 | 34.0 | 16.55 | 12.5 % |
| pinwheel | 3.0 | 7.0 | 14.0 | 24.0 | 34.0 | 16.71 | 11.9 % |

Every percentile is identical to the grid unit. The share of pairs τ actually
fixes agrees to within half a percent at every τ from 0 to 10 — at the shipped
τ = 4, 0.8683 against 0.8730, a ratio of **1.005**.

**The mechanism is that τ never sees the cut structure.** It sees the Proposal's
corner noise, which is Gaussian and identical in both arms by construction. Two
rooms touching along a wall and two rooms a metre apart are the same question to
`rank_relations`; adjacency enters the model through the reified contact literals
instead, which carry no confidence margin at all. This is why suite B finds
nothing: there was never a channel for it to find something through.

### No experiment on this map has ever run at `t_int` = 120

The ticket's inherited section opens *"Every solver number on this map was fitted
at `t_int` = 120"*, and ADR 0010 consequence 3 says ticket 19's deletion analysis
*"was computed at `t_int` = 120"*. **Both are wrong, in the same direction.**

`sweep.py` line 59, `solver.SolveConfig.t_int_mm`, `ergonomic_minima_tiling.py`,
`grid_aligned_minima.py`, `erosion_cost.py` and `probe6.py` all carry
`t_int = 100`, inherited from `annotation.md` §14 — which ADR 0010 consequence 6
itself flags as stale, in the sentence *"100 was already wrong at 120"*. A grep
for any value of 120 on a solver path returns nothing. The 120 was the **AZ
profile's** value; it never reached the harness.

So the move actually made is **100 → 150**, a 50 mm step rather than 30 — two
thirds larger than the instruction assumed — and the ADR 0007 residue class moves
**150 → 100 (mod 250)**, not 130 → 100. The destination in both documents is
right; the origin is not. `t_int_arithmetic.py`.

## III.1 What a non-guillotine ground truth is here

`pinwheel.py` builds one. Five cells of a rectangle, cuts `a < b` in x and
`c < d` in y:

```
R4 R4 | R3 R3 R3       R1 = (x1, y1,  b,  c)     R2 = ( b, y1, x2,  d)
R4 R4 | R3 R3 R3       R3 = ( a,  d, x2, y2)     R4 = (x1,  c,  a, y2)
------+---------       C  = ( a,  c,  b,  d)
R4 R4 | C  | R2
------+----+----       x = a is spanned by R1, x = b by R3, y = c by R2,
R1 R1 R1 | R2 R2       y = d by R4. No full cut exists.
```

The Envelope part holding the most rooms is dissected this way; every cell then
takes the ordinary guillotine, so everything below one level reproduces the
baseline generator's shapes exactly. **Five is the floor** — every tiling of a
rectangle into four or fewer rectangles is guillotine — and the assembled tiling
is checked with `is_guillotine` and rejected if it comes out guillotine anyway.

Three things make this a treatment rather than a garnish.

**It knots most of the plan.** `guillotine_residue` peels every available cut and
reports the largest block that survives. The guillotine arm returns **1** at every
room count, by definition. The pinwheel arm returns **5, 6, 9, 11, 14, 18, 21** at
7, 8, 10, 12, 16, 20 and 24 rooms — at 24 rooms, 21 of 24 rooms sit in one block
no sequence of cuts decomposes. Nesting pinwheels (`depth`) adds nothing, because
depth 1 already saturates: it fires a second and third wheel only at 24 rooms and
the residue does not move.

**The witness guarantee holds.** Every pinwheel ground truth is re-checked with
`validate.check` before it is used, and every one passed. Without that a failure
to solve would be indistinguishable from an accidentally impossible Brief, and the
whole comparison would mean nothing.

**The Brief is genuinely different, and that is correct.** Required and forbidden
adjacencies are read off the truth, so the two arms cannot present the same Brief
and should not. What is held fixed is everything a solve time could otherwise be
blamed on: Envelope, room mix, seed, Proposal noise, config.

### Below 7 rooms this Envelope family has no pinwheel to offer

Not a fact about pinwheels — a fact about the harness. The L-shape's notch forces
the second Envelope part to hold two rooms, which leaves the main part four or
fewer, and four rectangles are always guillotine. At 7 and 8 rooms the constraint
is different and it is arithmetic: `AREA_PER_ROOM_M2` is **9.65**, fitted to Part
I's three published Envelopes, so an 8-room dwelling here is 77 m² and the
placeholder `living` wants 12 m² of it at 2.75 m clear both ways — about a third
of the plan, compact. A pinwheel spends its area on four interlocking arms and
cannot cut a compact cell that large.

`pinwheel_area_premium.py` prices it, by finding the smallest interior area per
room at which every seed builds *and types*:

| n | guillotine | pinwheel | premium |
|---:|---:|---:|---:|
| 7 | 10.13 m² | 11.58 m² | **+14 %** |
| 8 | 11.58 m² | 11.58 m² | 0 % |
| 10 | 9.65 m² | 10.13 m² | +5 % |
| 12 | 10.13 m² | 10.13 m² | 0 % |
| 16 | 9.65 m² | 9.65 m² | 0 % |
| 24 | 9.65 m² | 9.65 m² | 0 % |

**The non-guillotine premium is +14 % at 7 rooms, +5 % at 10, and zero from 12
up.** Most of the blind spot is the harness's own floor rather than the treatment:
at 8 rooms *both* arms need 11.58 m² per room, 20 % above the 9.65 the published
Envelopes were built at. That is a defect in the fixtures worth recording on its
own — Part II's small-*n* cells were run at an area per room its own placeholder
table cannot always satisfy.

## III.2 The headline — room count against cut structure

Suite A. 140 solves, 7 room counts × 2 exposures × 2 arms × 5 seeds, shipped
configuration (`mm_affine`, eroded minima, τ = 4, σ = 0.5 m, 15 s, 4 workers).

| n | guillotine valid | pinwheel valid | p50 G | p50 P | residue P |
|---:|---:|---:|---:|---:|---:|
| 7 | 4/5 | *no pinwheel exists* | 0.13 s | — | — |
| 8 | 10/10 | 5/5 | 0.27 s | 0.25 s | 6 |
| 10 | 10/10 | 10/10 | 0.44 s | 0.65 s | 9 |
| 12 | 10/10 | 10/10 | 1.43 s | 1.37 s | 11 |
| 16 | 10/10 | 10/10 | 5.11 s | 4.98 s | 14 |
| 20 | 4/10 | 6/10 | 11.74 s | 10.59 s | 18 |
| 24 | 2/10 | 0/10 | 10.53 s | — | 21 |

Pooled: guillotine **76.9 %** of solves reach a Plan the independent validator
accepts, pinwheel **74.5 %**. Time-to-VALID p90 is **10.41 s** guillotine against
**9.56 s** pinwheel, and the maximum **14.57 s** against **12.24 s** — the
pinwheel arm's tail is *shorter*, not longer.

Part II.3's budget curve, re-derived per arm from the traces:

| budget | guillotine | pinwheel |
|---|---|---|
| 3 s | 49.2 % | 41.8 % |
| 5 s | 58.5 % | 56.4 % |
| 7.5 s | 64.6 % | 63.6 % |
| 10 s | 67.7 % | 67.3 % |
| **15 s** | **76.9 %** | **74.5 %** |

The two curves are within 2.4 points at the shipped limit and within 0.4 at 10 s.
**15 s does not need to move.**

### The paired test, and the one cell that differs

Rates over 10 solves a cell mean very little. The paired count is what the design
buys — the same `(n, exposure, seed)` slot, one arm against the other:

| n | both survive | only guillotine | only pinwheel |
|---:|---:|---:|---:|
| 8 | 5 | 0 | 0 |
| 10 | 10 | 0 | 0 |
| 12 | 10 | 0 | 0 |
| 16 | 10 | 0 | 0 |
| 20 | 2 | 2 | **4** |
| 24 | 0 | **2** | 0 |
| **all** | **37** | **4** | **4** |

**4 against 4, exact McNemar p = 1.00.** Slots where one arm had no scenario to
solve are excluded — they are facts about the generator, not the solver, and
counting them was the one analysis bug this part had. At 20 rooms the ordering
*reverses* and the pinwheel arm wins 4–2.

The 24-room cell is the only one that goes the other way, and both arms fail there
the same way: **coverage slack, not infeasibility**. Every failing row in both arms
returns FEASIBLE with unassigned interior floor — the `objective ≥ soft_weight`
case C6 already discards — rather than INFEASIBLE or a validator rejection. Across
the whole grid the guillotine arm recorded 1 INFEASIBLE and the pinwheel arm 0.

Suite D re-runs 20 and 24 rooms at **30 s** to separate "slower" from "worse",
since suite A ran at the shipped 15 s while Part II ran at 30:

| n | guillotine valid | pinwheel valid |
|---:|---:|---:|
| 20 | 5/8 | **8/8** |
| 24 | 6/8 | 2/8 |

Paired: 7 both, 2 neither, 4 only-guillotine, 3 only-pinwheel, **p = 1.00**. Both
arms improve substantially with the extra 15 s, so the 24-room gap at 15 s is
largely a convergence-rate effect rather than a feasibility one. A residual
difference at 24 rooms cannot be ruled out on 8 solves a cell — and it matters
little: **C13 demotes 24 rooms to headroom evidence quotable as a ceiling by
nothing**, and the v1 gate is 3–10 engine rooms.

## III.3 τ — the shipped 4 survives, and suite B could not have found otherwise

Suite B, 108 solves, τ ∈ {0, 1, 2, 4, 6, 10} at 8, 12 and 24 rooms.

At 12 rooms both arms return **100 % valid at every τ** (one guillotine cell at
τ = 0 drops to 2/3 on a single INFEASIBLE). At 24 rooms both arms are at or near
zero at every τ. At 8 rooms the pinwheel arm has no scenarios.

So suite B is **badly powered, and says so**: with 8 rooms empty and 24 saturated,
its informative content is one room count at 3 seeds a cell. It detects no
movement in τ, but it could not have detected a small one either.

The answer rests on III.0's margin distributions instead, which are the quantity
τ gates on and are measured over 14 465 pairs rather than 108 solves. **They are
identical between arms.** τ = 4 does the same job on a pinwheel Proposal that it
does on a guillotine one, and there is a mechanism for why rather than only a null
result.

## III.4 `t_int` — the inherited sweep, and where its cost actually lands

The instruction was to re-run the solver numbers because ADR 0010 moved `t_int`.
Two of the three findings here are arithmetic and needed no solver at all; the
third is a sweep that came back weaker than the arithmetic.

### Half one: the linear minima cannot move, for a grid-aligned table

`250w − t ≥ 250·min` gives `w ≥ min + ⌈t/250⌉`, and **⌈t/250⌉ is 1 for every `t`
in (0, 250]**. So 100, 120 and 150 impose *identical* width and height bounds on
every room whose minimum is a whole number of grid units. Over the placeholder
table the harness runs, **zero of ten** room types move. This is why the sweep was
right to expect very little — and it is a stronger statement than "very little".
It is exactly nothing, and provably so.

### Half two: the eroded area moves, and it is the only solver channel

`amm = (250w − t)(250h − t)` shrinks with `t`, so the area floor bites harder:

| grid rect | m² at 100 | m² at 150 | loss | as % of the rect |
|---|---:|---:|---:|---:|
| 8 × 8 | 3.610 | 3.422 | 0.188 | 5.19 % |
| 11 × 11 | 7.022 | 6.760 | 0.263 | 3.74 % |
| 22 × 14 | 18.360 | 17.922 | 0.438 | 2.38 % |

Against the placeholder table, **7 of 10** room types need a bigger grid rect at
150 than at 100 — `wc` +20 %, `hall` +14.3 %, `bathroom` +12.5 %. Against the
*derived ergonomic* floor, **0 of 10** do: those minima sit far enough below their
linear bounds that the area constraint is slack and `t` cannot reach it.

### Half three: the shipped ergonomic layer, which is where it actually costs

ADR 0009 exempted the ergonomic layer from ADR 0007's congruence, and priced that
exemption once — at a `t_int` nothing now ships. **The price is a function of
`t_int`, and it moved when `t_int` did.** Those minima are millimetres, not grid
units, so `⌈(min + t)/250⌉` depends on where each sits inside its step:

| `t_int` | residue | congruent axes | wasted mm, summed over the table |
|---:|---:|---:|---:|
| 100 | 150 | **12 of 36** | 2 524 |
| 120 | 130 | 0 of 36 | 5 304 |
| **150** | **100** | **6 of 36** | **4 224** |

**14 of 36 shipped clear dimensions gain a whole grid unit — 250 mm on that axis —
going from 100 to 150.** The reason is an accident that has now been spent: at
`t_int` = 100 the residue class is 150 (mod 250), and 900, 1400, 1650, 1900 and
3150 mm are all congruent to it. A third of the table was exactly on the lattice
by coincidence. At 150 it is not.

The concrete cases, with what the room is actually handed:

| axis | published | at 100 | at 150 |
|---|---:|---:|---:|
| `hall.short`, `corridor.short/long`, `kitchen.short`, `utility.short`, `storage.long`, `entrance_lobby.short` | 900 mm | 900 mm clear | **1 100 mm clear** |
| `hall.long`, `entrance_lobby.long` | 1 138 mm | 1 150 | **1 350** |
| `bedroom_double.short` | 1 650 mm | 1 650 | **1 850** |
| `bedroom_double.long`, `bedroom_single.long` | 1 900 mm | 1 900 | **2 100** |
| `shower_room.long` | 1 400 mm | 1 400 | **1 600** |
| `living_dining.long` | 3 150 mm | 3 150 | **3 350** |

This is the answer to the inherited half of the ticket, and it is **not the answer
the instruction was looking for**. It asked for solve timings; the cost landed on
the standards table.

### The sweep half, which is directional and not significant

Suite T, 112 solves, `t_int` ∈ {100, 150} on both arms, the ground truth rebuilt
to satisfy whichever reading the solver will enforce so the witness holds at both.

Paired on the same Envelope, arm, exposure and seed — 41 slots solvable at both:

| | both survive | neither | lost at 150 | gained at 150 |
|---|---:|---:|---:|---:|
| guillotine | 14 | 5 | 4 | 1 |
| pinwheel | 12 | 4 | 1 | 0 |
| **pooled** | **26** | **9** | **5** | **1** |

Exact McNemar on the pooled discordants: **p = 0.219. Not significant.** Three
further pinwheel scenarios stopped being constructible at all at 150.

**Every loss is at 16 rooms or above.** At 8, 10 and 12 rooms — the whole of C13's
band this family reaches — the discordant count is **zero** in both arms: every
slot that survived at 100 survived at 150.

> **`t_int` = 150 costs nothing inside the promised band.** Above it there is a
> directional cost this sample cannot separate from noise, and it should be quoted
> as directional, never as a measured penalty.

## III.5 σ, and the two-phase fallback fires *less*

The ticket's fourth question: if non-guillotine targets are harder, the fallback
fires more on exactly the dwellings retrieval most wants to serve. **The sign is
the other way, and this is the strongest result in Part III.**

Suite C was designed to answer it and could not. It picked 8 and 24 rooms to match
Part II's own σ grid, and 8 admits no pinwheel on this Envelope family while 24
fails in both arms at every σ above 0.25. Its one usable result is the cliff
*location*: at 24 rooms both arms are 100 % valid at σ = 0, drop to 50 % and 25 %
at σ = 0.25, and are 0 % at σ = 0.5 and above. **The cliff is in the same place in
both arms.** Suite C is kept rather than replaced, because that is the only direct
comparison with Part II's own σ grid.

Suite E re-runs it at 10, 12 and 16 rooms, where a pinwheel exists and the solver
is not saturated. 96 solves.

| σ | guillotine valid | pinwheel valid | guillotine INFEASIBLE | pinwheel INFEASIBLE |
|---:|---:|---:|---:|---:|
| 0.25 | 12/12 | 11/12 | 0 | 0 |
| 0.5 | 11/12 | 11/12 | 1 | 0 |
| 1.0 | 6/12 | 7/12 | 5 | 3 |
| 2.0 | **0/12** | **3/12** | 11 | 7 |

Paired across arms: 26 both, 13 neither, 3 only-guillotine, 6 only-pinwheel,
McNemar **p = 0.51** — the survivor rate is a wash, as everywhere else.

The infeasibility count is not. **INFEASIBLE is precisely what triggers the
two-phase fallback** — C10's *"a merely noisy Proposal goes INFEASIBLE"* — so it,
not the survivor rate, is the quantity item 4 asks about. Pooled over **every**
suite in Part III, paired on the same slot:

| | count |
|---|---:|
| paired slots | 212 |
| both arms INFEASIBLE | 12 |
| **only the guillotine arm** | **17** |
| **only the pinwheel arm** | **2** |

Exact McNemar **p = 0.0007**. The effect is not concentrated in one corner: it
appears at the shipped σ = 0.5 (7 against 0 over 160 slots), at σ = 1.0 and 2.0
(5 against 1 each), and at 10, 12, 16 and 24 rooms.

> **A non-guillotine target reaches INFEASIBLE significantly less often than a
> guillotine one.** The expected firing rate of the two-phase fallback does not
> rise on the dwellings retrieval most wants to serve. It falls.

**The mechanism is not established, and the obvious candidates are ruled out.**
Separation-margin distributions are identical between arms (III.0), and so is the
share of pairs τ fixes, and so is the fraction of room pairs the truth separates
on exactly one axis (0.646 against 0.642). Whatever makes a pinwheel's extracted
relation set less often self-contradictory, it is not any of those three. This is
a real finding with an unexplained cause, and it is recorded that way rather than
given a story.

## III.6 The motivating number was measured on a superseded conversion

The ticket's own table — 6.27 % of real dwellings non-guillotine, ~15 % at 8–10
rooms — came from `guillotine_share.py` over `swiss_fit.json`, the **k = 1**
conversion. **ADR 0016 superseded that**: a Room is one or two rectangles, and the
shipped conversion writes `parts`, not `rects`. More rectangles per dwelling can
only make a tiling harder to cut apart, so the figure was stale in a *known*
direction.

Re-measured paired, same 600 dwellings in the same order, only `k_of` differing —
`fit_rects.py 600` against `fit_rects.py 600 --k2`, 419 converted by both arms:

| rooms | n | guillotine k = 1 | guillotine k ≤ 2 | G→non-G | non-G→G |
|---:|---:|---:|---:|---:|---:|
| 4 | 37 | 0.9459 | 0.9730 | 1 | 2 |
| 5 | 82 | 0.9878 | 0.8780 | 9 | 0 |
| 6 | 92 | 0.9783 | 0.8913 | 8 | 0 |
| 7 | 91 | 0.9451 | 0.8571 | 10 | 2 |
| 8 | 61 | 0.8689 | 0.8361 | 3 | 1 |
| 9 | 42 | 0.9524 | 0.7619 | 8 | 0 |
| 10 | 14 | 0.7857 | 0.7857 | 1 | 1 |
| **all** | **419** | **0.9451** | **0.8640** | **40** | **6** |

**The non-guillotine share goes 5.49 % → 13.60 %** — roughly **2.5×** — with 40
dwellings moving to non-guillotine against 6 moving back, exact McNemar
**p = 3.1 × 10⁻⁷**. Rectangles per dwelling rise 6.57 → 7.02, +6.8 %, which is the
mechanism: ADR 0014's second rectangle is exactly the piece that blocks a cut.

The k = 1 arm reproduces the ticket's figure closely — 0.9451 here against 0.9373
published — so the difference is the conversion, not the sample.

> **The untested class was about two and a half times larger than the ticket
> thought.** That makes the null result in III.2 more valuable, not less: the
> solver was shown to be indifferent to a class covering roughly one real dwelling
> in seven rather than one in sixteen.

⚠️ **This is 419 dwellings against the ticket's 1,787.** The full k ≤ 2 run is
~4 s a dwelling — five times the k = 1 arm — so it was stopped at its 600-dwelling
checkpoint rather than run to 2 600. The overall share is solid; the per-room-count
cells above 8 rooms are thin (14 dwellings at n = 10) and should not be quoted
individually. Re-run both arms at 2 600 before anyone builds on a per-*n* figure.

## III.7 Should `scenarios.py` generate these at all?

Yes — and `pinwheel.py` is the answer for the job it does, which is **not** the
job the ticket's second option describes.

The ticket offers extending the generator or seeding ground truth from real
converted dwellings, as alternatives. They are not alternatives; they answer
different questions, and only one of them could have produced Part III.

**A synthetic generator is the only thing that can support a paired comparison.**
The whole force of III.2 is that Envelope, room mix, seed, Proposal noise and
config are held fixed and *only* the cut structure moves. Real converted dwellings
bring their own Envelopes, their own areas and their own room mixes, so a sweep
over them measures the difference between the Swiss corpus and this harness's
fixtures — a real question, and not this one. The 4-against-4 discordant count
would not exist.

**A real tiling is still the stronger fixture for the question it does answer**,
which is whether the solver serves the corpus rather than whether it is sensitive
to slicing structure. That is worth doing and it is not this ticket: it needs the
converted Envelope to enter the harness as an Envelope, which `envelope_for` has
no path for today.

So: keep `_guillotine`, add `pinwheel_ground_truth` beside it, and treat the pair
as a controlled axis rather than a replacement. What the generator must *not* do
is quietly become the default — every published number in Parts I and II is a
guillotine number, and re-basing the default would invalidate the comparison this
part just established.

**One fixture defect is now on the record** and belongs to whoever next runs this
harness: `AREA_PER_ROOM_M2` = 9.65 is below what the placeholder table needs at 7
and 8 rooms in *either* arm (III.1). Part II's small-*n* cells are measuring a
generator that cannot always build the dwelling it is asked for, which is a
different failure from the one they are read as reporting.

## III.8 What Part III does not establish

- **No real dwelling was solved.** The treatment is a synthetic pinwheel, which is
  the canonical non-guillotine plan and not the only one. The converted corpus
  contains whatever shapes it contains; III.6 says why that is a separate run.
- **Below 7 rooms is unmeasured, and unmeasurable on this Envelope family.** The
  L-shape's notch leaves the main part with four rooms or fewer, and four
  rectangles are always guillotine. The bottom of C13's 3–10 band still has no
  non-guillotine measurement of any kind.
- **Only one non-guillotine shape was tested.** Depth-nested pinwheels were built
  and add nothing measurable, but a spiral, a nested-U or a genuinely irregular
  tiling was not tried.
- **The 24-room difference is not resolved.** At 15 s it is 2–0 to the guillotine
  arm and at 30 s 6/8 against 2/8, on 8 solves a cell. It could be a real
  convergence-rate penalty at the very top of the range or it could be noise; this
  sample cannot say. It sits well outside the v1 gate either way.
- **The infeasibility advantage has no mechanism** (III.5).
- **The corpus re-measurement is 419 dwellings, not 1 787** (III.6). The overall share is solid; per-room-count cells above 8 rooms are thin.
- **`t_int` above 16 rooms is directional only** (III.4), p = 0.219.
- **Suite B is underpowered by construction** (III.3) and the τ answer rests on
  the margin distributions rather than on it.
- **Everything ran at 250 mm.** The grid is still never swept — the same gap Part
  II.8 records, and III.4's half three makes it sharper rather than closing it.
- **Timings are this machine's.** Same 4-core Ivy Bridge as Parts I and II, so the
  arms are comparable with each other and with every published number, and none of
  them is a modern-CPU figure.

## Reproducing Part III

```
cd experiments/solver-toy
python pinwheel.py                  # the generator, and where a pinwheel exists
python t_int_arithmetic.py          # III.4 halves one to three, no solver
python pinwheel_area_premium.py     # III.1, the floor-area premium
python relation_margins.py          # III.0, what tau actually gates on
python sweep_ng.py A T B C D E      # 568 slots / 483 solves, serial, ~2 h
python report_ng.py                 # every table above
python corpus_guillotine.py         # III.6, needs both converted arms
```

Rows land in `results/N9*.jsonl`, resumable exactly like Part II's. **Run nothing
else on the machine while sweeping.** Suites A, B, C, E and T run at the shipped
15 s; suite D runs at 30 s, and only suite D's rows can answer a budget above 15.
