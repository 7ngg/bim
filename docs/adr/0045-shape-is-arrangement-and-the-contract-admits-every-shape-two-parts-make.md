# ADR 0045 — Shape is arrangement, and the contract admits every shape two Parts make

- **Status**: accepted
- **Date**: 2026-08-31
- **Ticket**: [A two-part Room is a T or a Z as often as it is an L](../wayfinder/tickets/79-a-two-part-room-is-a-t-or-a-z-as-often-as-it-is-an-l.md)
- **Amends**: ADR 0014 — its *"Two, not three"* shape argument is struck and its
  `k ≤ 2` refusal re-based on the two legs that survive. See ADR 0014's
  `## Amendment`.
- **Supersedes nothing**
- **Asset**: `docs/research/room-shape-market-check.md`, branch
  `research/room-shape-market-check` (`5d10bf9`)

## Context

ADR 0014 caps a Room at two rectangles and defends the cap on shape: *"An L is a
shape an architect draws; a T, U, S or Z room is a shape a plan is left with."*
**The cap does not deliver the shape.** Two rectangles sharing an edge make an L,
a **T**, a **Z** or a plain rectangle, and over the converted index:

| shape | rooms | share | vertices | reflex |
|---|---:|---:|---:|---:|
| L | 851 | 55,2 % | 6 | 1 |
| T | 334 | 21,6 % | 8 | 2 |
| Z | 331 | 21,5 % | 8 | 2 |
| rectangle | 27 | 1,8 % | 4 | 0 |

**44,8 % do not have exactly one reflex corner**, and six artifacts said they did
— `CONTEXT.md`, ADR 0014, `acceptance-bar.md` §9.1, `ifc-export.md` §6.1,
`ifc-export.md` check row 14, and `erosion_check.py`, which asserted it in code.

### T and Z are a circulation-and-social phenomenon, and the warp reproduces it

Shape by room type, over the converted index:

| type | rooms | 2-part | L | T | Z | rect | not-L |
|---|---:|---:|---:|---:|---:|---:|---:|
| CORRIDOR | 2 675 | 650 | 323 | 195 | 130 | 2 | **50,3 %** |
| LIVING_DINING | 1 221 | 573 | 301 | 99 | 171 | 2 | **47,5 %** |
| LIVING_ROOM | 447 | 83 | 54 | 7 | 18 | 4 | 34,9 % |
| ROOM (generic) | 4 081 | 132 | 93 | 25 | 7 | 7 | 29,5 % |
| KITCHEN | 2 249 | 59 | 45 | 3 | 2 | 9 | 23,7 % |
| BEDROOM | 1 069 | 26 | 21 | 3 | 2 | 0 | **19,2 %** |
| BATHROOM | 3 379 | 13 | 8 | 2 | 0 | 3 | 38,5 % |

Corridor and social carry **89,5 %** of all T and Z. **26,9 %** of dwellings hold
a T or a Z; only **1,9 %** put one on a private room. **The U-shaped bedroom ADR
0014 refuses to defend is 5 rooms in 1 069.**

The warp emits the same distribution, which is the number that matters because it
is what ships: **94,1 %** of emitted T/Z is corridor or living_dining, **1,8 %**
of Proposals put one on a private room, and the warp **preserves donor part count
on 284/284 Proposals**. ADR 0014's own account already licenses these two types —
*"a corridor is an L because the flat is"*, *"corridors and open-plan living
26–30 %"* rectangular. A T corridor reaches two wings; the account extends
without strain.

### The cost of restricting, and the honesty about it

Restricting to L costs a Room on **46,5 %** of Proposals — the warp emits two-part
Rooms at 1,21 per Proposal against the corpus's 0,67 per dwelling. Falling back to
the larger part loses a median **29,4 %** (T) and **33,8 %** (Z) of the Room's
area.

⚠️ **That figure is an upper bound and was not the reason.** A converter
*constrained* to L would find a different, better L, not the larger part of the T.
No arm measures it — `swiss_fit_k1.json` refuses the second part entirely, which
is a different question — and the L-only arm was deliberately not built, because
the decision does not rest on it.

### What the market does

`docs/research/room-shape-market-check.md`. **No shipping BIM tool or commercial
generative product imposes a room-shape restriction narrower than "rectilinear
polygon."**

- **IFC imposes nothing, read from the schema.** `IfcArbitraryClosedProfileDef`
  (IFC4 ADD2 TC1) carries two informal propositions — the OuterCurve is closed,
  the OuterCurve does not self-intersect — and three where-rules (dim = 2; not
  `IfcLine`; not `IfcOffsetCurve2D`). No convexity, no reflex count, no vertex
  cap. `IfcSpace` footprints permit holes. RV1.2's own concept template, already
  quoted verbatim in `ifc-export.md` §6.1, constrains entity *types* only.
- **No vendor publishes a room-shape rule.** The advertised constraint vocabulary
  across the surveyed products is areas, adjacencies, unit mix, daylight and code
  — never shape class.
- **The one system that restricts narrower restricts to *rectangles*.** GPLAN's
  rectangular-floorplan line; and *A Theory of L-shaped Floor-plans* (arXiv
  2205.14434) defines L as *"boundary with only one concave corner"* — **about the
  plan boundary, not rooms** — chosen because it is the minimal case admitting
  necessary-and-sufficient existence conditions and an O(n²) construction. Adopting
  L-only would import a constraint for the sake of somebody else's proof.
- **Academically the travel is the other way.** HouseDiffusion is polygonal and
  advertises *"controlling the exact number of corners per room"* and
  *"non-Manhattan structures"*. The only system that dials corners, dials them up.

⚠️ Not established by that check: vendor output images were not inspected, Revit
and ArchiCAD are absence-of-restriction rather than affirmative permission, and
primary docs for several vendors were not reached.

### There is no tractability case either

At fixed part count a T and a Z are the same two boxes, the same
`AddNoOverlap2D`, the same join contact — shape is only which coordinates
coincide. **An L-only contract would *add* a disjunctive equality constraint, so
restricting makes the model strictly larger.**

## Decision

**1. The contract admits every shape two Parts make.** No shape predicate. The
Proposal contract constrains **buildability** — part count (ADR 0014's `k ≤ 2`)
and the leg floor (`dim.leg_join`) — and says nothing about which shape the parts
form.

**The line is the principle.** Count and leg floor are buildability: three legs is
solver cost, a pinch is not a room. **Shape at fixed part count is arrangement**,
and ADR 0014 already ruled that *"shape is an architectural claim, and it is made
where the arrangement is made"* — which is why the **solver** may not decide it. A
flush-at-one-end predicate makes the **contract** decide instead: the same move,
a different actor.

**2. Two Parts flush at both ends are one Part.** The union is a rectangle; the
two-part encoding is redundant. This is a clause on `proposer.md` §1's existing
constraint — *"must share an edge of at least the leg floor **and may not be flush
at both ends**"* — and a statement about what a Part is, recorded in `CONTEXT.md`.
**No normalisation step is created**; the spec had none and needs none.

**3. `ifc-export.md` check row 14 becomes "at most 8 vertices."** Reflex-corner
count was a proxy for part count and it is **unsound**: it rejects 43 % of
legitimate two-part Rooms, while a three-Part bug presenting one reflex corner
passes. Two axis-aligned rectangles sharing an edge produce exactly 4, 6 or 8
vertices, so the bound **never rejects valid output**; a three-Part staircase
reaches 10 and is caught. Verified on data, not argued: `erode(⋃ parts, t_int/2)`
over all 1 543 corpus two-part Rooms gives **4 ×27, 6 ×851, 8 ×665, max 8**, no
holes, no disconnection. Incomplete but sound, replacing sound-looking and unsound.

**4. §9.1's owed soft `dim.prefer_single_part` is withdrawn.** Its justification
was *"a Proposer can over-produce them"*. The over-production is real — **17,6 %
against the corpus's 9,8 %** — but it is **selection, not proposal**: the warp
preserves part count 284/284, and room-count stratification explains none of it
(matched expectation 9,6 %, so the full **+8,0 points** is the pool ranking, at
every room count). The bar runs downstream of `Gate → Pre-rank → Warp → re-rank →
take m`, so the rule cannot influence which donors are drawn — only demote the
survivors selection already chose, in a gallery §11 shows soft results in. A
shape-graded variant is worse: it would penalise **47,7 %** of emitted two-part
corridors and **40,3 %** of living_dinings, the corpus-normal shape, and it would
smuggle back through the objective the restriction decision 1 refuses.

§9.1 names this defect class one paragraph before proposing the rule — *"the same
shape of defect … `dim.market_default_area`: an objective that rewards something
nobody asked for."* **The rule count is unchanged**: 43, and 44 once
`dim.leg_join` lands. The owed rule was never in it.

**5. The decision is locked on Swiss evidence.** No Azerbaijani polygon corpus
exists or can be obtained — MİDA's 318 plan geometries are per-room *areas*, an
eksplikasiya schedule with no boundaries. This follows the map's disclosed
precedent rather than setting one: `brief.md` §5.1 already states *"Every shape
number in §5.1 is Swiss … and **no Azerbaijani dwelling is in it**."* Room shape is
the same class of fact as Envelope shape. Shape enters **none** of `proposer.md`
§6.1's five scored terms, so admitting T/Z does not propagate Swiss shape through
the objective. The asymmetry is the argument: **admitting a shape costs nothing
where it is unused, and only a restriction can be wrong in a country nobody has
measured.**

## Consequences

**1. The admitted shapes pass the bar they are held to.** Per-part aspect on clear
dimensions, corridor and storage exempt, hard reject above 3,0: **T 23,7 %, Z
21,5 %, L 27,2 %**. T and Z hard-fail *less often than L*. This decision ships
rooms that pass, not rooms the bar rejects anyway.

**2. Decision 2 is a correctness fix, not tidiness.** A degenerate pair measured
per part hard-fails aspect on **48,0 %** of the 25 non-exempt cases; measured
merged, **4,0 %**. **11 of 25 are false rejections created purely by the redundant
encoding** — the bar is currently rejecting good rectangles because they were
sliced. The degenerate class is also the *worst-fitting* shape in the corpus (IoU
p50 **0,809**, against L 0,944), so merging it loses no geometry: the union is
identical.

**3. Every figure here is quoted on a non-reproducible measurement, and the band
is stated rather than hidden.** Pooled: **1 543 two-part Rooms, 44,8 % not an L**.
Proved-optimal floor: **907 Rooms, 43,1 %**. Post-normalisation: **1 516** and
**43,9 %**, floor **898** and **42,5 %**. ADR 0041 published **1 535 / 44,8 %**
from an earlier run of the same rig and the 8-Room difference is not
reconcilable by any population filter. Cause: `fit_rects.py` runs CP-SAT at
`num_search_workers = 4` with **no `random_seed`**, and **16,0 % of dwellings
return `FEASIBLE`** under `TIME_LIMIT = 10.0`, contributing **41,2 %** of all
two-part Rooms. ~~Which mechanism dominates is unmeasured — ticket 85.~~ **No
conclusion here moves at the 43,1 % floor**, and consequence 3's vertex bound is a
topological fact about two rectangles, not a corpus statistic.

⚠️ **Amended by ADR 0046**, ticket 85, which measured it. Three corrections, and
**the consequence's conclusion survives all three**.

- **The mechanism is the race, and the seed was never one.** CP-SAT's own default
  `random_seed` is **1**, so "no `random_seed`" never meant unseeded — every
  process this rig ran was already at seed 1. Varying it to 7 produces
  disagreement indistinguishable from running seed 1 twice (cover 103 vs 95,
  shape 16 vs 17). What varies is which of four workers finishes first.
- **The 8-Room difference is reconciled, and needed no filter.** It is **0,5 %**
  against a measured run-to-run range of **2,9 %** over 400 paired dwellings —
  a smaller-than-typical draw, not a population difference.
- **~~Proved-optimal floor~~ — 43,1 % is not a floor.** It is the not-L rate of
  the dwellings easy enough to prove at 10 s. At a 30 s cap the dwellings newly
  proved carry **51,5 %** not-L against **41,8 %** for those already proved, so
  the proved-optimal plane *rises* (41,1 % → 45,0 %) as the pooled falls
  (47,7 % → 46,4 %) and the two converge on **~45–46 %**.

The convergent value is **at least as high as the published 44,8 %**, so this
consequence's own claim — *no conclusion here moves* — holds, and the decision it
supports is if anything better evidenced than when it was taken.

**4. The pool ranking prefers two-part-rich donors by +8,0 points and nobody
decided that it should.** Handed to *What each §6.1 term is scored for* (81),
which owns §6.1's terms and is the only open ticket that can judge whether the
gate should be selecting them. Not resolvable here: this ADR holds neither the
gate nor §6.1.

**5. `proposer.md` §1 is owed one clause and this ADR could not write it.** 67 and
81 both claim the file. The clause is *"and may not be flush at both ends"*.
It is additive, nothing is false while it waits, and both claimants are working
§2.2 and §6.1 content — the conditions under which a handoff has landed on this
map (71 took two, 68 took one) rather than rotted (ADR 0012's balcony datum,
`annotation.md`'s general note, both to files with **no** claimant).

**6. `annotation.md` needs nothing.** §480's *"carries every leg"* and §528's
larger-part centroid are shape-agnostic and stay correct at two reflex corners.
`solver-formulation.md` IX.7 and `selftest_parts.py` P9 quote ADR 0014's struck
sentence *as the thing being challenged*, and the amendment is the answer to it —
neither needs a pointer, and IX.7 already carries one in the direction that
matters, having raised this ticket.
