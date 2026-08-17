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
| 24 | degenerate | no | UNKNOWN | **none in 30 s** |
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
