# Context

Glossary for `bim-engine`. Terms only — no implementation detail, no spec.

## Actors

**Homeowner** — a person describing the home they want, in prose. Cannot draw a
boundary, cannot read a dimension string, cannot judge a plan on technical merit.
Judges by "would I live here". Tolerates a plan that is 90% right. The v1 user.

**Practitioner** — an architect or designer. Judges by "does this open in my
authoring tool and stay workable". A plan that is 90% right costs them more time
than a blank sheet. Not the v1 user; the standard the engine is held to.

## Artifacts

**Brief** — the structured object a Homeowner's prose is parsed into: rooms,
areas, envelope, adjacencies, occupancy. Editable, and the real interface to the
system. The prompt is the front door; the Brief is what everything downstream
consumes.

**Assumption** — a Brief value the system invented rather than read from the
prose. Always surfaced to the Homeowner. An invented *room* and an invented
*area* are assumptions of different kinds.

**Envelope** — the outer boundary a plan is laid out inside. **Given** for a flat,
which sits in a building that already exists; **invented** for a house, where the
footprint is being proposed.

**Solve domain** — the region the solver actually tiles: the interior clear region
**dilated outward by half an internal wall thickness**. Not the Envelope, and not
the interior. Chosen so that every edge of the tiling is a wall centreline —
interior edges shared between two rooms, boundary edges shared with the exterior
wall — which makes one erosion rule recover the real rooms with no special case
for perimeter rooms.

**Proposal** — what the learned model emits. Not a plan: a suggestion of topology
and proportion, used as the solver's objective. It is never the output.

**Proposer** — the component that emits the Proposal. Named separately from the
Proposal because it is replaceable: what it is built from is a separate question
from what it must emit, and the Proposal is the contract between them.

**Corpus** — a dataset of real floor plans used to train and evaluate the
Proposer. Plural **corpora**. They are not interchangeable: each encodes a
regional layout convention, which is why a Proposal is conditioned on which
corpus it came from rather than trained on all of them pooled.

**Plan** — the canonical geometry: walls with thickness, openings hosted on walls,
and spaces. The single representation every layer reads or writes. Annotation is
**not** part of it — see **Drawing**.

**Room** — a room as *program*: a name, a type, a target area, and an identity
that comes from the Brief. Has no geometry of its own. Survives a regenerate.

**Dependent room** — a Room the Brief says is entered *through* another Room
rather than from circulation: an ensuite, a walk-in wardrobe, a utility off the
kitchen. It names its host. Access-through is **program**, not geometry, so it is
declared and never inferred — without the declaration, "every room is reachable
without passing through a bedroom" rejects every plan with an ensuite; with it,
an ensuite that opens onto the hall correctly fails.

**Space** — a room as *geometry*: the polygon bounded by the inner faces of the
walls around it. Derived, never authored. **Room** and **Space** are not
interchangeable, and a sentence that uses "room" for both is the usual way a
clear dimension gets confused with a centreline one.

**Wall** — a centreline and a thickness. The body straddles the centreline; the
winding records which side is which. A Wall is the **maximal straight run** of
same-thickness, same-class material — it does not stop where the rooms behind it
change, and an opening does not divide it. Two classes: **External**, which comes
from the Envelope, and **Partition**, which comes from two rooms meeting.
Load-bearing is *unknown*, not false — v1 makes no structural claim.

**Wall segment** — the stretch of one Wall that separates one specific pair —
two Rooms, or a Room and the outside. Derived from the Room tiling. This is the
thing anything else refers to when it needs to name a piece of wall, because its
identity is the pair, and the pair is Brief-anchored. It is also, unchanged, a
space boundary.

**Opening** — a door or a window. Always **hosted**: it voids a Wall rather than
sitting near one, and it is named by the Wall segment it pierces, so it is named
by the pair of rooms it connects. An Opening is **typed** from a regional
catalogue rather than dimensioned freely — door leaves come in a discrete set that
differs by country, and a door of an invented width is the clearest tell that a
plan was generated. A **cased opening** is an Opening with no leaf, which is how
most homes join a kitchen to a living room and which a model that only knows
hinged doors cannot say.

An Opening has **three widths and they are not the same number**: the *structural
opening* that voids the wall, the *leaf* that is manufactured, and the *clear*
width you can carry furniture through. Which one is meant is always stated.

**Fall barrier** — guarding at a window, held separately from the window's sill
height, because the height that protects against a fall and the height that lets a
seated person see out are in direct conflict and no single number satisfies both.

**Swing footprint** — the region a door leaf sweeps, taken as the leaf-side
square anchored at the hinge. Deliberately the bounding box of the swept
quarter-disc rather than the disc: conservative, integer, and checkable before
any fixture or furniture exists.

**Storey** — the level a Plan's geometry sits on. Exactly one in v1, and the
Acceptance bar says so. It exists because the model would otherwise have to
invent it on export.

**Drawing** — a Plan, a sheet, and the annotation resolved over them: dimension
chains, room tags, title block. **Derived** from the Plan rather than stored in
it, because annotation is a function of geometry and goes stale the moment a wall
moves. What *is* stored is the **Annotation override** — a human's correction to a
derived placement, which must survive a re-render.

**Acceptance bar** — the set of predicates a Plan must satisfy to be shown. One
**declaration**, two consumers: a hard filter on finished candidates, and the
constraint set the solver projects onto. Not one implementation — the solver
posts inequalities before geometry exists, the filter evaluates finished
geometry, and rules about Openings are unpostable because Openings are placed
after the solve. Each predicate therefore names its **enforcement site**, and
only those enforced at both can be asserted to agree.

**Potential circulation** — reachability over the **contact graph**: which Rooms
share enough wall for a door to be placed. What the solver constrains, because it
runs before any Opening exists.

**Realised circulation** — reachability over the **opening graph**: which Spaces
are joined by an Opening a person can walk through. What the Acceptance bar
checks. Named apart from potential circulation because a solve can satisfy the
first and still be handed no door, and a system that calls both "circulation"
cannot say so.

**Plumbing group** — a maximal set of wet Spaces connected by shared Wall
segments. Clustering is stated as a bound on the *number* of groups rather than
as a demand for one, because a kitchen at the front and a bathroom at the back is
a real home, not a defect.

## Measurement

**Clear dimension** — a distance between the *finished faces* of the walls that
bound a room. What a Homeowner would measure with a tape, what a minimum room
dimension means, and what the Acceptance bar is stated in.

**Centreline dimension** — the same distance measured between wall *axes*. Larger
than the clear dimension by half a wall on each side. What the solver works in.

The two are never interchangeable. Every number that crosses between the solver
and anything else says which one it is.

**Ergonomic minimum** — the smallest clear rectangle a room's required fixtures
and their body clearances occupy. Region-invariant, because bodies are. It is the
floor the Acceptance bar rejects below, standing in for a legal minimum: most
regions prescribe none, and the regions that do disagree with each other by
nearly a factor of two.

## Relations

- Model **proposes**; solver **projects** that Proposal onto the feasible set.
  Plausibility is a soft objective; correctness is a hard constraint.
- The **Acceptance bar** is not advisory. A Plan that fails it is not shown.
- **Identity is anchored in the Brief, not in geometry.** A room keeps its
  identity across a regenerate because the Brief says it exists. Geometry that is
  *derived* — walls, openings — does not, and anything that needs to refer to it
  later refers by relation ("the wall between kitchen and hall"), so that the
  reference dies honestly when the topology changes instead of silently
  reattaching to the wrong thing.
- **Neufert-grade** describes dimensional standards — ergonomic and dimensional
  design data. It is not a building code, and no legal code-compliance claim is
  made anywhere in this system.
