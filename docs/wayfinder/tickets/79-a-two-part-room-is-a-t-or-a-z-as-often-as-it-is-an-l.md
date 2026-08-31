---
id: 79
title: A two-part Room is a T or a Z as often as it is an L
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - docs/adr/
  - docs/spec/acceptance-bar.md
  - docs/research/room-rectangles.md
  # declared on resolution, all unclaimed at the time:
  - CONTEXT.md
  - experiments/room-rectangles/erosion_check.py
  - docs/spec/ifc-export.md
---

# A two-part Room is a T or a Z as often as it is an L

## Question

**ADR 0014 caps a Room at two rectangles and argues the cap on shape** — *"An L
is a shape an architect draws; a T, U, S or Z room is a shape a plan is left
with"* — and that argument is what refuses k = 3. **The cap does not deliver the
shape.** Two rectangles sharing an edge make an L, a **T**, a **Z** or a plain
rectangle, and over the **1 535** two-part Rooms of the converted index:

| shape | rooms | share | vertices | reflex corners |
|---|---:|---:|---:|---:|
| L | 847 | **55,2 %** | 6 | 1 |
| T | 332 | 21,6 % | 8 | 2 |
| Z | 329 | 21,4 % | 8 | 2 |
| rectangle | 27 | 1,8 % | 4 | 0 |

**44,8 % do not have exactly one reflex corner.** On the warped Proposals ADR
0041 solved, the split is the same: 206 L, 73 Z, 63 T, 3 rectangle of 345 —
40,3 % not an L. So the shape ADR 0014 says a plan is *left with* is a fifth of
what the contract emits, twice over.

**Three artifacts state the opposite, and one of them asserts it in code.**

- `experiments/room-rectangles/erosion_check.py` closes with
  `assert n == 6 and reflex == 1`.
- ADR 0014: the erosion result is *"still rectilinear on integer millimetres with
  exactly one reflex corner"*.
- `acceptance-bar.md` §9.1: *"the Space is a rectilinear polygon with one reflex
  corner, not a rectangle"*.

✅ **The geometry is not the problem, and that is already checked.**
`experiments/plane-accounting/selftest_parts.py` P9 re-runs all three of
`erosion_check.py`'s properties at **two** reflex corners, on a T and on a Z:
`erode(A ∪ B, t/2)` strictly contains `erode(A) ∪ erode(B)`; the result equals the
hand-built inner-face polygon **pointwise**; and it is rectilinear on integer
millimetres with 8 vertices and 2 reflex corners. ADR 0001 is untouched and ADR
0041's area encoding is verified on all four shapes against `space_m2`.

**So this is a contract question, not a geometry one. What has to be settled:**

1. **Does the Proposal contract restrict a Room to an L?** `proposer.md` §1 says
   *"one or two boxes per Room, four integers each, the two sharing an edge"* — a
   count and an adjacency, no shape. Restricting means adding a predicate: the two
   parts are flush at one end. That is one comparison and it is cheap to state.
2. **What restricting costs, and it is not free.** A T or a Z that cannot be
   emitted falls back to its larger part or drops the dwelling, which is the same
   conversion-yield trade ADR 0014 refused k = 3 to protect. The numbers to weigh
   it are already in `experiments/rectangularise/` and in the coverage table ADR
   0014 quotes (87,2 % of rooms ≥ 95 % covered at k = 2).
3. **What the retrieval-and-warp path can actually honour.** ADR 0014's own
   evidence is that a corridor is an L *because the flat is*; a warped donor
   reproduces whatever shape the donor had. If the contract refuses a T, the warp
   has to do something with the 21,6 % that are one, and that something is not
   specified anywhere.
4. **If the answer is "admit all four", three artifacts need correcting** and
   `erosion_check.py`'s assertion needs widening to `reflex ∈ {0, 1, 2}` — with the
   T and Z cases P9 already carries. If the answer is "restrict to L", ADR 0014's
   §"Two, not three" argument gains a predicate it currently lacks.

**What this is not.** Not a re-opening of the k ≤ 2 cap — the count is settled and
the corpus evidence for it is unchallenged. Not a geometry defect: the erosion
identity, the area encoding, the room tag at the larger part's centroid,
`dim.leg_join` and the IFC profile are all shape-agnostic or already verified at
two reflex corners. Not a threshold change.

## Raised by

*What the bar plane owes a two-part Room* (2026-08-30), ADR 0041 consequence 4,
`solver-formulation.md` IX.7.

## Resolution

**Shape is arrangement, not buildability, so the contract admits all four shapes
and says nothing about which.** ADR 0045; ADR 0014 `## Amendment`;
`acceptance-bar.md` §9.1; `room-rectangles.md` §8; and — declared on resolution,
all three unclaimed at the time — `CONTEXT.md`, `erosion_check.py`,
`ifc-export.md`.

Asset: `docs/research/room-shape-market-check.md`, branch
`research/room-shape-market-check` (`5d10bf9`).

All four items answered, plus an unsound shipped conformance assertion the ticket
did not carry, a soft rule withdrawn, and a reproducibility defect under 41 % of
the evidence.

### Item 1 — the contract does not restrict a Room to an L

**It admits L, T, Z and (before normalisation) the plain rectangle.** The ticket
framed this as a cost question. The cost figure exists — restricting takes a Room
off **46,5 %** of Proposals, at a median **29,4 %** (T) / **33,8 %** (Z) of that
Room's area — but ⚠️ **it is an upper bound and it is not the reason**: a
converter constrained to L would find a different, better L, and no arm measures
that. See *What was deliberately not done* on why one was not built.

**The reason is ADR 0014's own principle.** It rules that *"shape is an
architectural claim, and it is made where the arrangement is made"* — which is
why the **solver** may not decide it. A flush-at-one-end predicate makes the
**contract** decide instead: the same move, a different actor. The line that
survives is **count and leg floor are buildability** — three legs is solver cost,
a pinch is not a room — **shape at fixed count is arrangement**. A T corridor and
an L corridor have identical part count, leg floor and buildability.

Three independent supports, each measured rather than argued:

- **The types that make T and Z are the two ADR 0014 already licenses.** Corridor
  and social carry **89,5 %** of corpus T/Z and **94,1 %** of *emitted* T/Z; only
  **1,8 %** of Proposals put one on a private room. The U-shaped bedroom ADR 0014
  refuses to defend is **5 rooms in 1 069**.
- **The market refutes both external justifications.** No shipping BIM tool or
  commercial product restricts narrower than rectilinear; `IfcArbitraryClosedProfileDef`
  carries no reflex or vertex limit at all; the one system that restricts narrower
  restricts to *rectangles*, and its one-concave-corner rule is about the **plan
  boundary, not rooms**, chosen for proof tractability. HouseDiffusion dials
  corners **up**.
- **There is no tractability case.** At fixed part count a T and a Z are the same
  two boxes and the same join contact; an L-only contract would *add* a
  disjunctive equality, making the model **strictly larger**.

And the admitted shapes pass the bar they are held to: per-part aspect hard-fail
is **T 23,7 %, Z 21,5 %** against **L 27,2 %**.

### Item 2 — what restricting costs, and what it does not

Answered in item 1. The one number the ticket expected to be decisive —
conversion yield — is **not** what carried the decision, and the ticket's own
framing (*"falls back to its larger part or drops the dwelling"*) overstates it.
Recorded as an upper bound in ADR 0045 and `room-rectangles.md` §8.5 so nobody
quotes it as the cost.

### Item 3 — what the retrieval-and-warp path can honour

**Moot, and measured rather than assumed.** The warp **preserves donor part count
on 284/284 Proposals**, so a donor's shape is reproduced exactly and the contract
never asks it to do anything with a T. Had the contract refused one, this is the
21,6 % the warp would have owed a repair procedure that does not exist anywhere.

### Item 4 — the four shapes are admitted, so three artifacts are corrected

**Six, not three, and the two the ticket missed are worse in kind.**

| artifact | what it said | disposition |
|---|---|---|
| `erosion_check.py` | `assert n == 6 and reflex == 1` | widened to all four shapes; **declared** |
| ADR 0014 | *"exactly one reflex corner"* + the shape argument | `## Amendment`, struck in place |
| `acceptance-bar.md` §9.1 | *"one reflex corner, not a rectangle"* | corrected — held |
| **`CONTEXT.md`** | *"a rectangle or an L"* | corrected; **declared** |
| **`ifc-export.md` §6.1** | *"at most one reflex corner"* | corrected; **declared** |
| **`ifc-export.md` row 14** | a shipped conformance assertion | replaced; **declared** |

⚠️ **Row 14 is the one that mattered.** It asserted *at most one reflex corner*
as a file-checkable proxy for the two-Part cap, and it is **unsound** — it rejects
43 % of legitimate two-part Rooms while a three-Part bug presenting one reflex
corner passes. Widening it to two reflex corners does not fix it, because reflex
count is the wrong quantity and the file has no Part to count instead: §6.1 merges
the parts into one profile. **Replaced with "at most 8 vertices"** — sound, since
two rectangles sharing an edge produce exactly 4, 6 or 8, verified on data as
`erode(⋃ parts, t_int/2)` over all 1 543 giving 4 ×27, 6 ×851, 8 ×665, max 8, no
holes; incomplete, since three collinear flush Parts also give 4. **Incomplete and
sound beats sound-looking and unsound.**

⚠️ **The ticket's own premise was half wrong about the code.** `erosion_check.py`
runs on **one hand-built L fixture**, not a corpus scan, so it never crashed — it
was under-general, not failing. It now checks ADR 0001's erosion identity
**pointwise against hand-built inner-face polygons at two reflex corners** for the
T and the Z, in the file ADR 0001, ADR 0014 and `annotation.md` §528 cite by name.

### The degenerate pair, which the ticket did not raise

**Two Parts flush at both ends are one Part** (ADR 0045 decision 2) — a clause on
§1's existing constraint, **not a new normalisation step**; the spec has none and
needs none, and the statement of what a Part *is* is recorded in `CONTEXT.md`.

⚠️ **This is a correctness fix, not tidiness.** Measured per part such a Room
hard-fails aspect on **48,0 %** of the 25 non-exempt corpus cases; measured merged,
**4,0 %**. **11 of 25 are false rejections created purely by the encoding** — the
bar rejects good rectangles because they were sliced. The class is also the
worst-fitting shape in the corpus (IoU p50 **0,809** against L's 0,944), and
merging loses no geometry: the union is identical.

### §9.1's owed soft rule is withdrawn

`dim.prefer_single_part` was justified as *"a Proposer can over-produce them"*.
The over-production is real — **17,6 %** emitted against **9,8 %** in the corpus —
but it is **selection, not proposal**: 284/284 part-count preservation, and
room-count stratification explains **none** of it (matched expectation 9,6 %), so
the whole **+8,0 points** is the pool ranking, at every room count. The bar runs
downstream of `Gate → Pre-rank → Warp → re-rank → take m`, so the rule could only
demote survivors selection had already chosen. *All else equal* never obtains
after best-of-*m*.

A **shape**-graded variant is worse: it penalises **47,7 %** of emitted two-part
corridors and **40,3 %** of living_dinings — the corpus-normal shape — and
reimposes through the objective the restriction item 1 refuses in the contract.
**Rule count unchanged at 43 / 44**; the withdrawn rule was never in it. **This
also dissolves a `writes:` conflict** — with no rule to author, `rules.json` needs
no edit and 72/76 are untouched.

### Locked on Swiss evidence, and why that is not 76's defect

No AZ polygon corpus exists or can be obtained — MİDA's 318 plan geometries are
per-room **areas**, an eksplikasiya schedule with no boundaries. 76 and 75 are
about *magnitudes*, where two countries publish different numbers in the same unit.
This is about which shapes the contract can **express**, and admitting a shape
costs nothing where it is unused: **only a restriction can be wrong in a country
nobody has measured.** Shape enters **none** of §6.1's five scored terms.
`brief.md` §5.1 already discloses the precedent — *"no Azerbaijani dwelling is in
it."*

### What this hands on

- **`docs/spec/proposer.md` §1** → **67 and 81**, both claimants. One additive
  clause: *"and may not be flush at both ends."* Nothing is false while it waits,
  and both claimants are working §2.2 / §6.1 content — the conditions under which
  a handoff has landed on this map (71 took two, 68 took one) rather than rotted
  (ADR 0012's balcony datum and `annotation.md`'s general note, both to files with
  **no** claimant, both still outstanding).
- **The +8,0-point ranking preference** → **81**, which owns §6.1's terms and is
  the only open ticket that can judge whether the gate should be selecting
  two-part-rich donors.
- **Ticket 85**, raised: the conversion is unseeded at four workers and 16 %
  cap-truncated.
- **`annotation.md` needs nothing.** §480 and §528 are shape-agnostic and stay
  correct at two reflex corners. `solver-formulation.md` IX.7 and
  `selftest_parts.py` P9 quote the struck sentence *as the challenge*, and the
  amendment answers it.

### What was deliberately not done

- **No L-only converter arm.** ~5 minutes at 0,78 s/dwelling, and declined: it
  measures the cost of a branch not taken, and a favourable number would still not
  license the contract to make an arrangement claim. ⚠️ Recorded as a decision
  against this map's measure-first habit, not an oversight.
- **`experiments/rectangularise/` untouched.** §8 reads existing output.
- **P9 left alone** — `experiments/plane-accounting/` is 83's, claimed as a
  directory. ⚠️ **And widening `erosion_check.py` made one clause of P9 false,
  which this ticket caused and could not fix.** P9's docstring reads
  *"`erosion_check.py` checks it at one and asserts `reflex == 1`"*; it now checks
  all four shapes, so *"checks it at one"* is wrong — the `reflex == 1` half
  survives as the L case. Its runtime note repeats it. **This is a falsehood, not
  staleness, and the earlier draft of this resolution called it staleness.** Owed
  to **83**, which is the next ticket to open that directory; two clauses, no
  value changes, and nothing else in P9 moves — all ten of its checks pass
  unchanged.

### The reproducibility defect this ticket walked into

ADR 0041 published **1 535** two-part Rooms where the current file yields
**1 543** — L 851, T 334, Z 331, rect 27 — and no population filter reconciles the
8. **`fit_rects.py` runs CP-SAT at `num_search_workers = 4` with no `random_seed`,
and 16,0 % of dwellings return `FEASIBLE` under `TIME_LIMIT = 10.0`, contributing
41,2 % of all two-part Rooms.** ADR 0043's finding, upstream in the conversion,
where 82 found it in the warp — and `salt_check.py` scans the whole repo and
cannot see it, because it looks for the `hash()` pattern and this is a different
one.

**No conclusion here moves.** Not-L is 44,8 % pooled and **43,1 %** over the 907
proved-optimal Rooms alone; cap-hit dwellings are T/Z-richer (47,3 %), so a longer
cap drifts the headline **down**, bounded at 43,1 %. Every figure is published on
both planes. Ticket **85** owns the defect.
