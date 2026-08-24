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

It is **two objects, not one**. A **Stated brief** is sparse — a field is present
only if the prose asserted it, and the parser is never asked for more than that. A
**Resolved brief** is dense, every field the pipeline needs filled by a pure
function of the stated one, the region profile and the standards. The split is
what makes the set of invented values *derivable* rather than a second list
somebody has to keep in step, and it is why editing and regenerating are the same
operation.

**Assumption** — a Brief value the Homeowner should check, always surfaced. Three
kinds, and the third is not a **Provenance** value: an invented *room*, an
invented *value*, and a **reading** — a value they *did* state, interpreted. A
listing's "90 m²" is stated and still a reading, because the published figure
counts an *eyvan* at full area and this system has no such element. Naming the
reading is how the engine says what it assumed without inventing a deduction the
user never made.

**Envelope** — the boundary a plan is laid out inside, taken at the **finished
inner face** of the external wall. It *is* the interior clear region, so a
Homeowner's tape measurement of their flat is the Envelope with nothing added or
removed — and a tape reads finish, which is why the plane is named. Not the
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

**Editing a value makes it stated; acknowledging one does not.** The distinction
is load-bearing rather than pedantic — whether the area-determining fields were
stated decides whether a plan missing its target area is rejected or merely
flagged, so "they looked at it" and "they chose it" cannot be the same value.

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
person built, into the **at most two** rectangles this system places. Two
decisions, not one: which **axis**, and then which rectangles. It is not
preprocessing — it decides what arrangement the Proposer can ever learn.

**Dwelling axis** — the frame a dwelling is square to, which is its own and not
its site's. Corpora are geo-referenced, so a dwelling's rooms are square to a
building that is square to a street; measured against the world's axes not one
room in the corpus is a rectangle. Every shape statement about a corpus dwelling
names the axis it was measured on, or it means nothing.

**Representable** — whether a real dwelling can be expressed in this system's
model at all: at most **two** rectangles per Room, tiling an Envelope of a
bounding box minus at most two notches. The property that decides whether a corpus dwelling is used
or dropped. Stated as representability rather than as a similarity threshold
because the question is what v1 *can say*, and a percentile cannot answer that.

**Plan** — the canonical geometry: walls with thickness, openings hosted on walls,
and spaces. The single representation every layer reads or writes. Annotation is
**not** part of it — see **Drawing**.

**Room** — a room as *program*: a name, a type, a target area, and an identity
that comes from the Brief. Has no geometry of its own. Survives a regenerate.

Its **type** and its **label** are different things and only the type is
load-bearing. The type is one of a closed set the minima, the schedule, the
retrieval key and the solver all read; the label is the Homeowner's own word,
printed on the tag and nowhere else. "Nursery" and "guest room" are labels on a
typed Room, which is how a real drawing schedule already works, and it is what
lets a Homeowner's vocabulary be kept without any of it becoming a number.

A **target area is a band, not a floor.** Stating only a minimum is what lets a
plan pass every check with a room several times the size anyone would build it:
the interior must be tiled exactly, so surplus is compulsory and lands wherever
the solver finds it cheapest.

**Engine room count** — the number of Rooms in a `ResolvedBrief`, including the
circulation `resolve` invents. The count the solver, retrieval and the supported
band are all measured in, and the only one that binds anything. A Homeowner has
never said it out loud: circulation is invented in 93.5% of real dwellings.
_Avoid_: "Brief-named rooms", which it is not — no Brief names a corridor.

**Otaq** — habitable rooms only: bedrooms and living rooms, never a kitchen,
bathroom, corridor or store. The AzDTN 2.7-2 counting convention, how a flat is
advertised in Baku, and the unit the product's supported band is **stated** in.
`AZ` already keys two statutory floors on it. One otaq is a median of four engine
Rooms — see [[Engine room count]], and never convert by assuming a constant.
_Avoid_: "habitable room count", "room count" unqualified.

**Supported band** — what v1 claims, and what it refuses, and they are not the
same edge. The **gate** is a hard refusal outside 3–10 [[Engine room count]],
taken at parse time and naming the count. The **promise** is 1–4 [[Otaq]], which
is narrower: between them lies a zone the engine serves and the copy declines to
claim, and a Brief landing there runs with a warning. ADR 0013.
_Avoid_: collapsing the two into one number — it can only over-refuse or
over-claim.

**Dependent room** — a Room the Brief says is entered *through* another Room
rather than from circulation: an ensuite, a walk-in wardrobe, a utility off the
kitchen. It names its host. Access-through is **program**, not geometry, so it is
declared and never inferred — without the declaration, "every room is reachable
without passing through a bedroom" rejects every plan with an ensuite; with it,
an ensuite that opens onto the hall correctly fails.

**Adjacency wish** and **Adjacency veto** — the two pairwise relations a
Homeowner may state about Rooms that are not host and dependent. They are not
symmetric and must not be one field: a wish is a *preference* and can never empty
the gallery, because "the kitchen near the dining" is said casually; a veto is
*hard*, because a prohibition the engine accepts and then ignores is worse than
offering none. Neither can express a set against a set — "the bedrooms, away from
the entrance" is a different shape of statement and is not expressible here.

**Space** — a room as *geometry*: the polygon bounded by the **finished** inner
faces of the walls around it — see [[Finish layer]]. Derived, never authored.
**Room** and **Space** are not interchangeable, and a sentence that uses "room"
for both is the usual way a clear dimension gets confused with a centreline one.

A Space is **one or two rectangles**, never more — a rectangle or an L. Not a
rectangle, which is what every document here assumed until it was measured: half
of real rooms are not one. See [[Part]].

**Part** — one of the at most two axis-aligned rectangles a [[Space]] is the
union of. The **first** part carries the Room's own dimensional minima; any
further part carries the **leg floor**, and the two must share an edge of at
least that floor — below it the two legs are not one room, they are two rooms
with no door between them.

Which Rooms have two parts is decided by the **[[Proposal]]**, never by the
solver. A second rectangle *improves* the objective rather than relieving it — it
lets the first sit closer to where the Proposal put it — so left to choose, the
solver takes one on a fifth to a third of the rooms it is offered, and takes it
hardest on the types real dwellings keep **most** rectangular. Shape is an
architectural claim, and it is made where the arrangement is made.

**Leg floor** — the smallest clear dimension a [[Part]] beyond the first may
have, and the smallest edge two parts may share. Below it, the shape is a niche
or a pinch rather than a room. It is the circulation minimum, because a leg you
cannot walk down is not a leg.

**Wall** — a centreline and a thickness. The body straddles the centreline; the
winding records which side is which. A Wall is the **maximal straight run** of
same-thickness, same-class material — it does not stop where the rooms behind it
change, and an opening does not divide it. Two classes: **External**, which comes
from the Envelope, and **Partition**, which comes from two rooms meeting.
A party wall is External — its **boundary condition** selects its thickness, which
is why two classes are still enough. Load-bearing is *unknown*, not false — v1
makes no structural claim, on a party wall least of all.

Its thickness is a **[[Layer set]]**, never a scalar.

**Layer set** — a Wall's build-up as an ordered list of `(material, thickness)`,
innermost first. Its **total** is the only thickness the solver, the erosion and
every dimension consume; the structural leaf survives as data and v1 consumes it
nowhere. The split is not decoration: a party wall's thickness is *derived from
an acoustic requirement that already assumes plaster on both faces*, so a single
scalar makes that derivation unreadable, and `IfcWallStandardCase` carries the
layers whether or not we do.

**Finish layer** — the innermost layer of a [[Layer set]]: what the occupant
actually touches, and the plane every published number measures to. Small,
systematic, and in the wrong direction if ignored — a bath is 1700 mm of enamel,
and a 1700 mm room measured to bare masonry does not hold one.

**Wall segment** — the stretch of one Wall that separates one specific pair —
two Rooms, or a Room and the outside. Derived from the Room tiling. This is the
thing anything else refers to when it needs to name a piece of wall, because its
identity is the pair, and the pair is Brief-anchored. It is also, unchanged, a
space boundary.

Derived over **Room pairs, never [[Part]] pairs.** Where a Room's two parts meet
there is an edge in the tiling and **no wall**: nothing separates a Room from
itself. A derivation that walked part boundaries would put a wall inside a room —
in the geometry, in the drawing and in the IFC — and it would look like a
deliberate partition rather than a bug.

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

An Opening's **height is catalogue and its placement is not.** The catalogue mark
fixes height and width together — a GOST mark reads *height*-then-*width*, so `OR
15-12` is 1500 × 1200 and not the reverse — while where the opening sits
vertically is fixed by the [[Head datum]] and never stored per instance. The same
window sits at one height in a living room and another over a kitchen counter, so
the catalogue could not carry it and an invented per-instance sill would be the
same tell as an invented width.

**Head datum** — the single line every window hangs from, and the reason a sill is
derived rather than stored: `sill = head datum − opening height`. It is the
tallest opening in the region catalogue, because a balcony door and the window
beside it share a lintel. Doors sit below it at their own catalogue height. ADR
0012.

**Fall barrier** — guarding at a window, held separately from the window's sill
height, because the height that protects against a fall and the height that lets a
seated person see out are in direct conflict and no single number satisfies both.

Its **height is known and its trigger is refused**. The region profile publishes a
statutory guarding height, but *which* windows need one depends on the drop below
them — which storey, and what is outside. v1 has one Storey at elevation zero and
no site, so the model cannot tell a ground-floor window from an eighth-floor one
and does not pretend to. Every window's Fall barrier reads *unknown*, and the
schedule prints `—`. ADR 0012.

**Swing footprint** — the region a door leaf sweeps, taken as the leaf-side
square anchored at the hinge. Deliberately the bounding box of the swept
quarter-disc rather than the disc: conservative, integer, and checkable before
any fixture or furniture exists.

**Storey** — the level a Plan's geometry sits on, and **the only thing in this
model that has a height**. Exactly one in v1, and the Acceptance bar says so. It
used to exist only so export would not have to invent it; it now carries the
[[Clear height]] every Wall and Space reads, so there is nothing left to invent.

**Clear height** — floor to finished ceiling, and **v1's single vertical datum**.
One number per Plan, stated in the Brief or assumed from the region profile. Every
other vertical quantity is expressed against it or refused: a Wall body is
extruded to it, a Space's volume is its area times it, and a window's sill is the
[[Head datum]] minus the opening's height. Named for the same reason [[Clear
dimension]] is — it measures **finished** faces, and the source says so in its own
words.

**Floor-to-floor** is deliberately **absent**, not merely unmeasured. Nothing in
v1 rests on a slab, so publishing a slab-to-slab height would assert a build-up
this model does not carry. A Wall body is therefore floor-to-ceiling, and that is
an understatement the export declares rather than pads. ADR 0012.

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

**IFC check** — the same shape as the **Drawing check**, one export along. The
predicates an authored IFC file must satisfy before it is written: schema
validity, plus the assertions a schema cannot make — that the header declares the
view it was built to, that no omitted property has quietly been filled in, and
that the areas in the file equal the areas on the sheet. Like the Drawing check it
judges the *file*, never the Plan, so it raises rather than degrading; and like the
Drawing check it is deliberately not in the Acceptance bar, because a Plan must
never be rejected for an exporter's defect. **Three gates exist and they ask three
different questions:** is this Plan good, is this sheet issuable, is this file
honest.

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
dimension means, and what the Acceptance bar is stated in. "Finished" is
load-bearing and was for a long time not true: the erosion subtracts half a
[[Layer set]]'s **total**, and it once subtracted half a bare structural leaf,
which is a different plane by two [[Finish layer]]s per axis. ADR 0010.

**Area convention** — the named rule by which an area is measured, without which
an area is not a quantity. Two different conventions on one building differ by
tens of percent, so a number that has lost its convention cannot be compared,
gated or printed. Held **once per Plan**, derived from the [[Region profile]] and
carried for life; the Brief holds its own, separately, because a Homeowner quotes
whatever their property listing quotes and the two are allowed to disagree — the
disagreement is a Brief error, and a silent agreement that was never checked is
the failure this term exists to prevent. v1 ships `az_umumi_sahe`: the sum of
Space areas, measured to finished faces at floor level, partitions **not**
counted.

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
solver free and costs **time**, while a **confident-wrong** pair — asserted, and
backwards — costs the **candidate**. Measured: dropping every relation still
yields a Plan; asserting one backwards makes the model infeasible over half the
time, and two ends it. "Backwards" means *the truth contradicts the assertion*,
not merely that the truth would have picked another direction — two rooms can be
separated on both axes at once, and asserting the other one costs nothing.

**Severity** — how far backwards a confident-wrong pair is: the overlap, in
millimetres, that the assertion demands be closed against the truth. Summed over
a Proposal it is what predicts whether the solver can project it, and it is the
quantity **τ** filters. A pair wrong by a hand's breadth and a pair wrong by a
room are one number in a count and are not the same defect.

**Ergonomic minimum** — the smallest clear rectangle a room's required fixtures
and their [[Body zone]]s occupy. Region-invariant, because bodies are. It is the
floor the Acceptance bar rejects below, standing in for a legal minimum: most
regions prescribe none, and the regions that do disagree with each other by
nearly a factor of two. Stated as a **shorter side and a longer side**, never as
a width and a depth — a room has no canonical orientation, so binding the pair to
axes would assert a direction no fixture implies. It is a **floor, not a target**:
it sits far below what anyone builds, and the liveable number is the [[Region
profile]]'s. A minimum is *derived* — composed from published footprints — and
never transcribed from a table; the corpus is allowed to falsify it and never to
supply it.

**Realisable minimum** — an [[Ergonomic minimum]] after the solve grid and the
wall have been paid for: the smallest clear dimension the solver can actually
produce at or above it. A published minimum and a realisable one are different
numbers because a room is solved in whole grid cells and then eroded by a wall,
so a floor of 1650 mm is delivered as 1850. Named because every arithmetic done
*before* a solve — above all the check that says whether a Brief is possible at
all — has to use the realisable number, and using the published one quietly
approves briefs the solver cannot build.

**Body zone** — the depth of body in front of a fixture that cannot be shared
with another fixture's zone. The one calibrated constant behind every [[Ergonomic
minimum]]; everything else in the composition is a published footprint. Two
fixtures used one at a time may *share* one zone, but no zone may overlap another
fixture's footprint — which is why an ergonomic minimum is smaller than the sum of
its parts. Deliberately **not** any published clearance: every clearance the
sources state is an *accessibility* figure, because those are the ones regulators
write down, and composing a private bathroom out of them yields a floor that
rejects a third of real homes.

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
