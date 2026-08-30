---
id: 79
title: A two-part Room is a T or a Z as often as it is an L
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - docs/adr/
  - docs/spec/acceptance-bar.md
  - docs/research/room-rectangles.md
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
