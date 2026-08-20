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

**Envelope** — the boundary a plan is laid out inside, taken at the **inner face**
of the external wall. It *is* the interior clear region, so a Homeowner's tape
measurement of their flat is the Envelope with nothing added or removed. Not the
footprint and not a centreline — those are derived from it. Rectilinear in v1.

An Envelope is an **ordered ring of edges**, and the order matters: a flat with
windows on two adjacent sides and one with windows on two opposite sides carry the
same counts and are not the same home.

**Boundary condition** — what lies on the far side of one Envelope edge, as far as
this dwelling is concerned. **Exterior**, which may hold a window, or **party**,
which is shared, blind, and makes no claim about who is behind it. Separate from
**entrance side**, a flag marking where the primary door may go — a house's front
door sits in an exterior wall, a flat's in a party wall onto a common corridor, so
the two cannot be one value.

**Dwelling type** — a named ring of boundary conditions: detached, semi-detached,
end and mid terrace, single-aspect, corner and dual-aspect flat. What separates a
flat from a house is **which edges can hold a window**, and nothing else, so
dwelling type is data about an Envelope rather than a kind of Plan. The ring is
region-invariant; only its name is regional.

**Footprint** — the gross outer boundary, derived by growing each Envelope edge
outward by its own wall's thickness. Never authored, never solved against, and the
reason the Envelope is not defined here instead: the thicknesses differ per edge.

**Provenance** — whether a value was **stated** by the user or **invented** by the
system. Held per field, not per object: someone who says "a corner flat, about 9 m
wide" has stated an exposure and one dimension and invented the rest. An invented
value is an **Assumption**.

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
from what it must emit, and the Proposal is the contract between them. It is
**not one thing** — v1 has two sources behind that contract, a retrieval over real
dwellings and a trained model, because one blanks where the corpus is thin and the
other fails without saying so. Which source a Proposal came from is recorded on
the **job**, never on the Proposal, so nothing downstream can prefer a source.

**Retrieval pool** — the real dwellings admissible as a Proposal for one Brief:
those whose room programme matches it and whose size and proportion are close
enough to warp without inventing. Its size is the candidate count, so an empty
pool is a Brief with no real precedent rather than an error.

**Warp budget** — how far a real dwelling may be stretched before its arrangement
stops being a real home's. A limit, not a preference: retrieval's entire claim is
that a person once lived in this arrangement, and past some distortion that
sentence is false. A dwelling outside the budget is not retrieved at all.

**Private room** — a Brief's bedroom, study or nursery, as one class. It exists
because the corpora cannot tell them apart: the most common label in Swiss
Dwellings is an unlabelled room with a bedroom's proportions. The Brief keeps the
finer word for the Homeowner and for conditioning; retrieval only ever matches the
class.

**Corpus** — a dataset of real floor plans used to train and evaluate the
Proposer. Plural **corpora**. They are not interchangeable: each encodes a
regional layout convention, which is why a Proposal is conditioned on which
corpus it came from rather than trained on all of them pooled.

A corpus stores **Spaces**, not Rooms — polygons bounded by wall inner faces,
with the wall body in the gap between them. No two of them touch. So a corpus
room is geometry with a label, never a Brief's programme, and adjacency in a
corpus is a question about distance rather than about contact.

**Rectangularisation** — turning a corpus **Space**, which is whatever shape a
person built, into the one rectangle every stage of this system places. Two
decisions, not one: which **axis**, and then which rectangle. It is not
preprocessing — it decides what arrangement the Proposer can ever learn.

**Dwelling axis** — the frame a dwelling is square to, which is its own and not
its site's. Corpora are geo-referenced, so a dwelling's rooms are square to a
building that is square to a street; measured against the world's axes not one
room in the corpus is a rectangle. Every shape statement about a corpus dwelling
names the axis it was measured on, or it means nothing.

**Representable** — whether a real dwelling can be expressed in this system's
model at all: one rectangle per Room, tiling an Envelope of a bounding box minus
at most two notches. The property that decides whether a corpus dwelling is used
or dropped. Stated as representability rather than as a similarity threshold
because the question is what v1 *can say*, and a percentile cannot answer that.

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
A party wall is External — its **boundary condition** selects its thickness, which
is why two classes are still enough. Load-bearing is *unknown*, not false — v1
makes no structural claim, on a party wall least of all.

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

**Drawing** — a Plan, a **Sheet set**, and the annotation resolved over them:
plan graphics, dimension chains, room tags, schedules, title block. **Derived**
from the Plan rather than stored in it, because annotation is a function of
geometry and goes stale the moment a wall moves. What *is* stored is the
**Annotation override** — a human's correction to a derived *placement*. An
override moves things; it can never change a measured number, a room name or a
schedule value, because that would let a human make the drawing lie about the
model.

**Audience** — who an annotation element is for: the Homeowner and the
Practitioner both, or the Practitioner alone. Held per element, so that one
derivation serves two presentations. There is no second annotation engine to
drift against the first.

**Sheet** — the paper an annotated plan is laid out on: size, plot scale,
margins, title block. Scale is held and the sheet grows, never the reverse —
halving the scale to fit smaller paper is a printing decision wearing a drawing
decision's clothes.

**Dimension chain** — a run of dimensions sharing one base line, whose segments
sum exactly to the span they cover. Closing is a property, not an aspiration:
the model is integer millimetres, so any chain that fails to close is a defect
rather than a rounding artefact.

**Witness** — the line a dimension measures to. Always a wall *face*, never a
centreline, with one declared exception at the footprint overall. Named because
a chain segment's identity is its pair of witnesses, and a witness is in turn
named by the Rooms either side of it — Brief-anchored, so it dies honestly when
the topology changes.

**Type mark** — the label tying an Opening on the plan to its row in a schedule
and its entry in the regional catalogue. The join between the drawing and the
schedule, asserted total in both directions.

**Drawing check** — the predicates a Drawing must satisfy before a file is
emitted. Distinct from the **Acceptance bar** in consumer and in timing: the bar
gates whether a Plan is *shown* and has two consumers, this gates whether a file
is *written* and has one. A failure here is our defect, not the Plan's — the Plan
already passed the bar — so it raises rather than degrading.

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
and anything else says which one it is. **Every number that reaches a human is
the clear one** — a centreline dimension on a drawing is wrong by a wall
thickness on every room and every axis, and putting one there is the mechanism by
which the confusion above actually happens.

**Separation direction** — which of left-of, right-of, above or below one Room is
meant to sit relative to another. What the solver actually reads out of a
Proposal's boxes, which is why a Proposal is judged on arrangement rather than on
how close its boxes landed.

**Asserted** and **abstained** — a Room pair whose separation direction is claimed
firmly enough to become a constraint, against one left open. The two are not
symmetric and must never be reported as one number: an abstention leaves the
solver free, and a **confident-wrong** pair — asserted, and backwards — is the
failure that costs a candidate outright.

**Ergonomic minimum** — the smallest clear rectangle a room's required fixtures
and their body clearances occupy. Region-invariant, because bodies are. It is the
floor the Acceptance bar rejects below, standing in for a legal minimum: most
regions prescribe none, and the regions that do disagree with each other by
nearly a factor of two.

**Region profile** — the set of *conventional* values a Plan is built and drawn
to: the thickness catalogue, the decimal separator, the room-name abbreviations,
the opening catalogue keys, the preferred room areas and the window fraction.
Underneath it is really a **construction system plus a drawing convention**;
country is only a proxy, and a poor one — Germany and Azerbaijan are both
fired-brick masonry with incompatible modules, while the UK and the US are both
frame-and-cavity. A profile can change which Plans are *preferred* and which
strings are *printed*, never which are *rejected*, because every hard dimensional
floor is an [[Ergonomic minimum]] and region-invariant. A Plan carries its profile
for its whole life. v1 ships exactly one, `AZ`.

**Corpus provenance** — which corpus a Proposal's arrangement came from, carried
as the `(region, corpus, annotation_provenance)` conditioning tag. **Not the
Region profile, and in v1 deliberately not equal to it:** retrieval reads Swiss
Dwellings only, so v1 draws Swiss-shaped layouts to Azerbaijani conventions. The
mismatch is a disclosed limit, not a defect — the third in the family that starts
"single storey" and "house layouts come from apartment priors".

**Thickness catalogue** — the discrete set of wall thicknesses a Region profile
permits, per wall class and construction type. Discrete rather than free, for the
same reason the Opening catalogue is: a chosen set beats free specification. Every
entry must be an **even number of millimetres**, because a clear dimension is
`erode(rect, t/2)` in integer millimetres and an odd thickness puts every wall face
on a half-millimetre. It is an engine choice, not a quoted standard — real
surveyed housing has no module to copy.

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
- **Region is a convention, not a standard of care.** The [[Region profile]] chooses what a Plan is drawn and built to; the [[Ergonomic minimum]] chooses what is rejected. Changing region never changes the second.
- **Neufert-grade** describes dimensional standards — ergonomic and dimensional
  design data. It is not a building code, and no legal code-compliance claim is
  made anywhere in this system.
