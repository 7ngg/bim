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

**One Brief has one Envelope *area* and many Envelope *boxes*.** Where the shape
is invented, each candidate carries its own [[Notch]] geometry from the dwelling
it was retrieved from, so the ring's edge count and the bounding box both differ
across a pool while the floor they enclose does not — ADR 0020.
_Avoid_: "the Envelope, which every candidate for one Brief shares", which is ADR
0018 consequence 3 and is **false**; and any reading in which an Envelope is one
object per job.

**Notch** — a rectangular bite out of an Envelope's bounding box, at most two, and
what makes a rectilinear outline an L, U or T rather than a box. Its **position is
never stated** — a Homeowner who can place a notch can draw — so it comes from the
retrieved dwelling and is therefore a real home's.

A notch is **material** when it takes at least 5 % of the bounding box: ~4 m² on a
90 m² dwelling, a bite a person would call a shape. Below that it is a niche, and
counting it as shape is what made the shipped gate report 90 % of real flats as
U/T-shaped. Read materially, half of them are L.
_Avoid_: treating a notch as small. It is a median **12.55 %** of the bounding box
and runs to 23 % at p90 — the reason a pool agrees on floor area rather than on a
box.
_Avoid_: reading a notch and a [[Void]] as one quantity. Both are floor no Room
covers, and `uncovered` in a fit record **sums them** — which is why neither was
noticed. They are held in **opposite directions**: the notch is pinned at the
share the box was derived from, the void is charged to a Room and pushed down.
_Avoid_: **splitting them at the frame's border.** That was the shipped test and
it is wrong on a quarter of the index. The Envelope is the bounding box minus
**at most two** notch rectangles, so a third boundary-touching component is
inside the ring — **27.2 %** of donors carry one, p50 1.25 m², 89.7 % perfectly
rectangular, seated at a corner or edge distinct from the first two. The line is
the **notch spans**, not the border. ADR 0020's second amendment.
_Avoid_: reading `s` off the parts complement. It runs **+0.0191** mean above
the Envelope's own share — more than two points high on 38.2 % of donors, about
**1.9 m² of invented notch** on a 90 m² dwelling, in a ring edge that is typed,
drawn, dimensioned and exported.

**Void** — floor **inside the Envelope** that no Room covers: every complement
component of a candidate's frame other than the [[Notch]] spans. **p50 2.47 %**
of the Envelope, mean 2.93 %; about 40 % of the index carries at least one.
_Avoid_: the old name *enclosed void* and the enclosure test behind it. Touching
the bounding box border does not put floor outside the building — the Envelope
spent its two notches elsewhere. The **enclosed** slice alone is 15.49 % of the
index, p50 0.00 m², p90 0.25, max 4.56, and that is the population every
published measurement of ownership purity and warp amplification was made on.

It is **our residue, not the building's**: only 2.0 % of it is a dropped duct or
riser, and the rest is what ADR 0014's two-rectangle cap could not cover — 22.2 %
of real rooms need three. It cannot become a Room's second part, because a leg is
900 mm clear on both axes and 96 % of voids are smaller: below that it is a niche,
and this system does not model niches.

A void has a **known owner** — the real dwelling says whose floor it was, at p50
purity 1.00 — and that owner is **not derivable** from the boxes, which is why the
[[Proposal]] carries it. ADR 0028.
_Avoid_: calling it unassigned floor and stopping there. It is unassigned in the
donor and it is **charged to a Room** in the warp, because the solver is required
to close it and every bordering Room's repair costs the same — so "the objective
decides" means nothing decides.

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

**Derived from the [[Envelope]], per candidate, never equal to it.** Since the
Envelope's bounding box is per-candidate the domain is too, and the two are
different rectangles: `t_int` apart on each axis.
_Avoid_: tiling the Envelope's own box and then eroding every Room at its
boundary. That charges the dwelling for an external wall that is not there —
**3,7 % of the interior at p50** on the shipped `t_int` — and it reads as a
sizing error in `brief.md` §5 rung 1, which is where it was nearly fixed.
"No special case for perimeter rooms" is a statement about the **rule**; the
arithmetic still has to be given the right region to apply it to.

**Proposal** — what the learned model emits. Not a plan: a suggestion of topology
and proportion, used as the solver's objective. It is never the output.

It carries what **only it can know**: which Rooms are two rectangles (ADR 0014),
and which Room a [[Void]] belongs to (ADR 0028). That is the whole
membership test — a property enters the contract when the solver cannot derive it
from the `ResolvedBrief` and cannot infer it from the boxes. Zoning fails that
test and is refused; a Room's L-ness and a void's owner pass it.
_Avoid_: "the solver can work it out from the boxes" without checking. The
objective is L1 corner displacement, so for a void **every bordering Room's repair
costs the same** — the cheapest-looking derivable rule agrees with the truth
28.4 % of the time and is ambiguous on another 28.4 %.

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
_Avoid_: the [[Bucket]] as a stand-in for it. **82,4 %** of a bucket is dwellings
the size and proportion terms refuse, and refusing them buys real fidelity even
though neither quantity survives into the [[Warp]]'s own arithmetic: a refused
donor is declined **36,2 %** of the time against an admitted donor's **27,6 %**,
and carries a worst-room area deviation **68 %** larger at p50 — measured paired
*within one Brief*, so it is the donor and not the Brief. The confusion is not
hypothetical; every warp-fidelity figure this project published before ticket 60
was measured on a bucket.

**Bucket** — every converted dwelling sharing one Brief's room programme, before
size and proportion are checked. The **first** term of admissibility and only the
first: a bucket becomes a [[Retrieval pool]] when the other two terms have
scanned it. It is worth naming because it is roughly ten times deeper, which is
the only way a sample far smaller than the index can reach production pool depth
at all — but it stands in for **depth** and never for **membership**, and a
statistic that reads one candidate at a time may not be taken off it. At pool
level the distinction washes out, because declines are correlated within a pool
and the pool absorbs a weaker member.

**Warp budget** — how far a real dwelling may be stretched before it stops being
worth retrieving. A limit, not a preference; a dwelling outside it is not
retrieved at all.
_Avoid_: "before its arrangement stops being a real home's" — that was the
original reading and it is **false**. The [[Warp]] moves cut lines, and a
monotone move preserves every [[Separation direction]] exactly, so no budget
protects the arrangement and none needs to. What a budget bounds is *dimensional*
plausibility, and the quantity that actually degrades is per-**Room** area.

**Warp** — turning a retrieved dwelling into a Proposal for a different
[[Envelope]]. Not a stretch: the retrieved tiling's **cut lines** are re-chosen
by a solve, so the arrangement survives untouched while every [[Room]] is sized
to the Brief's target area. What retrieval claims is therefore *a real home's
arrangement, sized to your Brief*, never *a real home, stretched*.
Its refusals are real: a target Envelope that cannot host that arrangement above
the [[Ergonomic minimum]] is declined, and the next pool member is tried.

**Relation provenance** — whether a [[Separation direction]] in a converted
corpus dwelling was **asserted by the real dwelling** or **invented by the
conversion**, because squaring a room resolved an overlap the truth abstained on.
It is what a retrieved Proposal's per-pair confidence is made of, displacement
being uninformative under a [[Warp]]. Roughly one axis-pair in eight is invented.
_Avoid_: reading it as *bad* — an invented pick reads as what a person would
draw. It is not evidence, and a hard constraint wants evidence.

**Frontage budget** — the run of `exterior`-condition [[Envelope]] edge one
[[Space]] must hold before its window can be seated: the window's structural
width plus twice the jamb return. Posted **hard by the solver**, not left to the
[[Opening]] layer to discover, because a candidate that cannot seat its window is
cheaper to refuse than to solve and throw away.

**Frontage reach** — the same quantity read off a **corpus** dwelling, as a
ratio: the tightest, over a dwelling's window-needing [[Room]]s, of the boundary
run that Room holds to the [[Frontage budget]] posted for it. Below 1.0 the
dwelling holds a Room that cannot seat its window on its own boundary. It is the
*only* daylight property a [[Retrieval pool]] member hands over — a donor's own
windows are overwritten, because the [[Opening]] layer draws them after the
solve.
_Avoid_: treating it as sufficient. It measures **boundary contact**, and the
conversion cannot tell an exterior edge from a party one, so a Room with reach
may still take no window in the target [[Envelope]]. It ranks; it does not gate.

**Borrowed daylight** — a room lit through another room rather than through its
own window. In `AZ` the only sanctioned form is the `taxça-mətbəx`, a kitchen
**niche**: a recess open to the room it sits in, which cl. 5.7 floors at 5 m².
_Avoid_: reading **adjacency** as borrowed daylight. A separate kitchen with a
*door* onto a windowed living room is not a niche — it is a windowless kitchen,
which cl. 9.12 forbids outright. A geometric adjacency test cannot tell the two
apart, and two documents on this map have already read one for the other.

**Private room** — a Room you do not walk *through*: the sleeping rooms and the
wet rooms together, and the class `circ.no_private_transit` is written over. It
is the `is_private` flag in `room-constraints.json`, true on `bathroom`,
`bathroom_combined`, `shower_room` and `wc` as well as the four sleeping types —
**four** wet types, not three. `zoning.md` §5b names three because it was written
before ADR 0022 added `bathroom_combined` as the nineteenth type.

⚠️ **This entry used to describe the narrower sleeping set** — "a Brief's
bedroom, study or nursery, as one class" — which is a *retrieval-matching* class
and never was what the flag holds. Two sets wore one word; the flag was right for
its rule and the glossary was describing something else. The sleeping set is now
**[[Sleeping room]]**, and the reason the split matters is that a rule reaching
for "the bedrooms" and finding `is_private` silently acquires the bathrooms.

**Sleeping room** — a bedroom or a study, as one class: `is_sleeping` in
`room-constraints.json`, **which now exists** — ADR 0044. It exists twice over. For **retrieval**, because the
corpora cannot tell a bedroom from a study — the commonest label in Swiss
Dwellings is an unlabelled room with a bedroom's proportions, so the Brief keeps
the finer word for the Homeowner and for conditioning while retrieval matches only
the class. For **[[Sleeping group]]**, because it is the node set that grouping is
computed over, and it must exclude the wet rooms a [[Private room]] includes.

⚠️ **The flag is a definition and the conjunction is a coincidence.** `is_sleeping`
is today exactly `is_habitable ∧ is_private` across all nineteen types, and
`gate_check.py` asserts that **agreement** rather than deriving from it. The
conjunction is a property of the current type set, not the meaning of the word: a
habitable private room that is not for sleeping — a library, a home office that is
not a study — breaks it, and the gate is where that gets decided rather than
silently rezoning every Plan. Read the flag; never re-derive it.

⚠️ **What a corpus can and cannot tell you about one.** The commonest Swiss label
is `ROOM`, the unlabelled bedroom-proportioned room, and it is **79,5 %** of the
corpus sleeping set against `BEDROOM`'s 20,5 %. A `study` is therefore not
*absent* from the measurement, it is **indistinguishable inside it** — a weaker
and different claim from `bedroom_principal`, which has no corpus label at all.
Area cannot separate them either: the corpus sleeping set's p5 is 9,97 m² against
`study`'s ergonomic minimum of 0,8 m², so **no threshold identifies a study**.
Every corpus rate quoted for a sleeping-set term counts studies as bedrooms.

**Circulation room** — a Room whose purpose is movement between other Rooms:
`hall`, `entrance_lobby`, `corridor`. It is the `is_circulation` flag in
`room-constraints.json`, and it is the one class distinction the other flags
cannot supply: `hall` and `storage` carry **identical** vectors over all six of
them and belong in different classes. That collision is why the zoning rig
carried a private corpus-label table until ADR 0044, and it is why the fix was a
new bit rather than a cleverer rule.

_Avoid_: reading it as *"not habitable and not wet"* — `storage` satisfies that
and is not circulation. Also distinct from `circ.fraction_hard`, which bounds
circulation **area**; this flag names the **types**. They agree today and are two
statements.

**Sleeping group** — a maximal set of [[Sleeping room]] Spaces that touch, or
share a circulation neighbour. Bedrooms rarely touch, so "off the same hall" is
what grouping means here and adjacency is not required.

Named to sit beside [[Plumbing group]], because it is the same object: one
clustering routine, a different node set. Like it, the constraint is a bound on
the **number** of groups and not a demand for one — 69.8 % of real dwellings hold
their sleeping rooms in a single group and 27.7 % in two, so demanding one rejects
almost a third of real homes.

⚠️ **Never "zone", and never "zoning".** Across the whole surveyed market that
word means land-use control — floor-area ratio, setbacks, shadow law — and this
system makes no land-use claim at all. `docs/research/zoning.md` is the only place
it appears, and it appears there to say this.

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

**Singular by convention and not by fact.** **4,79 %** of the converted index has
a room more than 10° off the axis it was given — a wing splayed off a spine, which
real housing does. The conversion rotates onto **one** angle regardless, so those
dwellings are sheared onto it and emerge as a plausible home that is not the home
that was converted. The axis is a choice the conversion makes, and
[[Frame residual]] is how far that choice was from free.
_Avoid_: reading "the dwelling axis" as a property the dwelling has. It is a
property the conversion **assigns**, and a second one exists in one dwelling in
twenty.

**Frame residual** — the area-weighted mean deviation of a dwelling's Rooms from
the [[Dwelling axis]] it was assigned, in degrees. Published on every converted
record. Deliberately carries **no threshold**: a maximum is a one-room statistic
about a whole-dwelling defect, and an area *share* would bury a cut inside a raw
field.
_Avoid_: treating it as a duplicate of worst-room IoU. At a fixed IoU an
off-frame dwelling still scores 5–11 cell-agreement points lower, so a per-room
minimum is not a sufficient statistic for a shear.
_Avoid_: expecting it to gate anything. It gates and ranks nothing — the
retrieval pre-rank already puts a 4–8° donor at the tenth percentile — except in
the trained source's **evaluation baseline**, the one place excluding costs
nothing (ADR 0031).

**Representable** — whether a real dwelling can be expressed in this system's
model at all: at most **two** rectangles per Room, tiling an Envelope of a
bounding box minus at most two notches. The property that decides whether a corpus dwelling is used
or dropped. Stated as representability rather than as a similarity threshold
because the question is what v1 *can say*, and a percentile cannot answer that.

**It has two halves and only the Room half was ever measured.** The Envelope half
now is: a real dwelling's interior needs a minimum of **six rectangles** at the
median (p90 twelve), where the [[Notch]] family yields between one and four, and
**12,4 %** of the converted index comes in at three or fewer. Representability is
therefore mostly an *outline* property, not a room-shape one.
_Avoid_: reading a corpus-**fitted** Envelope as a real boundary. ADR 0029's
family matches the corpus on area, perimeter and bounding-box occupancy — three
moments — and a dwelling that agrees on all three can still need six rectangles
where the fixture needs three. Matching moments is not matching a [[Real
boundary]].

**Real boundary** — a converted dwelling's own outline on the 250 mm solve grid:
`keep_largest_component(watershed(rooms)) >= 0`, the cell mask the conversion
already measures its notch loss against. Distinguished from the [[Envelope]]
because the two are not the same object and the map has only ever solved on the
second.
_Avoid_: treating it as a drop-in fixture. Nothing in the harness can *pose* a
Brief on one — the ground-truth generator gives every Envelope part a room and
**96 %** of real dwellings have a part no room fits, so the blocker sits upstream
of the solver rather than in it.
_Avoid_: using a converted dwelling's recorded rectangles as its own boundary's
ground truth. They are fitted to the bounding-box-minus-two-notches
approximation, which is a **superset** of the real boundary, so against the real
one they both leave the Envelope and leave floor unassigned. A re-fit on the true
mask is a different, and materially harder, solve.

**Plan** — the canonical geometry: walls with thickness, openings hosted on walls,
and spaces. The single representation every layer reads or writes. Annotation is
**not** part of it — see **Drawing**.

**Room** — a room as *program*: a name, a type, a target area, and an identity
that comes from the Brief. Has no geometry of its own. Survives a regenerate.

Its **type**, its **name** and its **label** are three different things and only
the type is load-bearing. The type is a [[Room type]]; the name is what that type
is called in the drawing's language — see [[Room name]]; the label is the
Homeowner's own word, printed on the tag and nowhere else. "Nursery" and "guest
room" are labels on a typed Room, which is how a real drawing schedule already
works, and it is what lets a Homeowner's vocabulary be kept without any of it
becoming a number.
_Avoid_: treating the name as a translation of the label — the label is never
translated, and the name is never a Homeowner's word.

A **target area is a band, not a floor.** Stating only a minimum is what lets a
plan pass every check with a room several times the size anyone would build it:
the interior must be tiled exactly, so surplus is compulsory and lands wherever
the solver finds it cheapest.

**Engine room count** — the number of Rooms in a `ResolvedBrief`, including the
[[Invented circulation]]. The count the solver, retrieval and the supported band
are all measured in, and the only one that binds anything. A Homeowner has never
said it out loud: circulation is invented in 93.5% of real dwellings.
_Avoid_: "Brief-named rooms", which it is not — no Brief names a corridor.

**Invented circulation** — the circulation Room `resolve` adds when the Brief names
none. **Exactly one, and it is a `hall`.** One because the count has to be fixed
before any geometry exists and a wrong guess is not recoverable, and a `hall`
because AzDTN 2.7-2 cl. 5.2 lists `holl` among the [[Auxiliary space]]s a dwelling
must have — so it is transcribed, not chosen. It is the type a Homeowner may name,
which is how a dwelling gets a second circulation space: by the Brief saying so.
Safe at one only because a [[Space]] may be two [[Part]]s, so the hall can be an L
that reaches a wing.
_Avoid_: "invented rooms" plural, and "the corridor" — `corridor` and
`entrance_lobby` exist in the type set and nothing in v1 reaches them.

**Otaq** — habitable rooms only: bedrooms and living rooms, never a kitchen,
bathroom, corridor or store. The AzDTN 2.7-2 counting convention, how a flat is
advertised in Baku, and the unit the product's supported band is **stated** in.
`AZ` already keys two statutory floors on it. One otaq is a median of four engine
Rooms — see [[Engine room count]], and never convert by assuming a constant.

The set is **enumerated by the norm, not chosen by us**: AzDTN 2.7-2 cl. 5.5 lists
yaşayış otaqları as `otaq, qonaq otağı və yataq otağı` — room, living room and
bedroom — and cl. 5.2 puts kitchen, hall, bath-or-shower, WC and storage in
[[Auxiliary space]]. So an otaq is countable from a [[Room type]] alone, and the
count is a *sourced* fact rather than a product opinion.

It is **not the same as habitable**, and the two are separate flags on purpose. A
kitchen-diner is habitable — it is sustained-occupation space and takes a window —
and it is **not** an otaq, because AzDTN treats it as a kitchen variant and a Baku
listing never counts a mətbəx. Reading the habitable flag for this number
advertises a one-bedroom flat with a kitchen-diner as two otaq.
_Avoid_: "habitable room count", "room count" unqualified, and using habitability
as a proxy for either.

**Room type** — the closed set of nineteen kinds a [[Room]] may be, and the only
room vocabulary anything load-bearing reads. The Brief speaks it verbatim, the
hard dimensional floors are keyed by it, and it is region-invariant: the same
nineteen types under every region profile, because they are derived from bodies
and furniture rather than from any country's convention.

The set grows only when a rule cannot be stated without the new type. It went
from eighteen to nineteen exactly once, for `bathroom_combined`, because
[[Programme rule]] `prog.wc_exists` rejected 48.32% of real dwellings over
eighteen and 43.13 of those points were homes that **had** a toilet the
vocabulary could not name.
_Avoid_: adding a type to express a *preference*. A type is how a Room is
measured, so a type nothing measures differently is a [[Room name]] or a label.

Everything else that names a room is a **projection of it, never a peer**. A
region profile keys its own soft targets differently and is reached through a
mapping; retrieval collapses several types into one class; a
[[Corpus label]] is a third scheme again. All three are lossy and one-way. Two of
them were once written into the same file as if they were alternatives, which is
the defect this term exists to prevent.
**Every projection is now a published object, and the last one was not.** A
projection that lives only in the comments of whoever last wrote it is a
projection no check can read, and each of the four tables that carried the corpus
one privately was free to disagree with the profile and with the others. ADR 0037.
_Avoid_: "room category", "room kind" — and any sentence where a profile key or a
corpus label stands where a type belongs.

**Area-band class** — the population a [[Room type]]'s **upper** area band was
fitted on, and the fourth projection of the type. Carries `k`, `absolute_cap` and
the soft weight; it is what `dim.max_area` and `dim.market_default_area` key on.

It resolves by **containment, not identity**, and that is the whole of the term.
A [[Corpus label]] map says what a label **is**; this one says which population
**contains** a type. The two differ, and treating them as one relation is why
nine of nineteen types resolved to nothing and a hard rule silently did not fire
on them — `hall` among them, which `resolve` invents in every dwelling. The
merged circulation label cannot default a hall's *target*, and it is exactly the
right *band*, because a band is a dispersion statistic over a population and that
population is the merge.

Every row declares the rung it resolved on — `contains(label)`,
`contains(fixture)`, `composed`, `analogy` — so the weak links are visible rather
than uniform-looking, and **totality is gated**: a type with no class is worse
than a wrong bound, because a wrong bound reports itself. ADR 0038.
_Avoid_: calling one a [[Corpus label]] even where the two share a spelling, and
reading a class as evidence about a *target*. It bounds; it never anchors.

**Corpus label** — the room vocabulary a [[Corpus]] annotates in, and the third
scheme after the [[Room type]] and the region profile's own keys. Belongs to
whoever built the dataset, so it is neither region-invariant nor ours, and it
reaches the engine only through a published one-way map onto the type.

It is **lossy in whichever direction the dataset was careless**, and where it is,
that is a fact about the corpus and never a licence to invent. One label may
collapse several types — Swiss Dwellings distinguishes none of `ROOM` /
`BEDROOM` / `STUDIO` from a single bedroom versus a double, so the read declares
which limb it takes rather than guessing. One label may straddle two types and
need a fitted splitter. And one may be **disqualified as a measurement while
staying valid as an identity**: a corpus room labelled a kitchen-diner is still
that type for the purpose of resolving its floor, even where its area
*distribution* is refused because 39 of its 41 rooms sit in dwellings that also
carry a separate kitchen.
_Avoid_: reading a label as evidence about the type it maps to without asking
what the annotator meant by it. And do not let a [[Room type]] with no label —
`bedroom_principal` has none — read as a type retrieval can produce.

**Room name** — what a [[Room type]] is *called*, in the language the drawing is
issued in. One name per type, printed by the room tag, the room schedule and the
Brief document. Display-only in exactly the sense a label is: the type stays the
thing that carries meaning.

A name is **sourced or it is marked**. Where the region's own norm names the room,
that word is published and cited; where it does not, the name says so rather than
passing as sourced. A plausible room name in a language the reader speaks and the
author does not is indistinguishable from a real one, which is why the
distinction is carried in the data and not in someone's memory.

**Programme rule** — a predicate whose subject is the dwelling's **whole
programme** — the multiset of [[Room type]]s in a `ResolvedBrief` — rather than
any one Space, Wall or Opening. Four of them, `prog.*_exists`, and they are the
only rules in the [[Acceptance bar]] of that shape.

They bind the **Brief and nothing else**, and there is no plan-side twin. The Room
set is frozen when `resolve` returns — nothing auto-repairs, every Brief Room is
required, the warp maps onto a fixed multiset, and no floor may go unassigned — so
a plan-side composition predicate could never fail on a Plan whose Brief passed.
_Avoid_: calling one a [[Pre-image bound]]. A pre-image bound is the parse-time
shadow of a rule that also binds a Plan; a programme rule *is* the rule, and its
severity is chosen against the corpus rather than inherited.

**Auxiliary space** — `yardımçı sahələr`, AzDTN 2.7-2's class for the rooms a
dwelling must have and that are not [[Otaq]]: kitchen or kitchen-niche, hall,
bath or shower, WC or combined sanitary unit, storage, laundry. Naming the class
matters because it is *mandatory* — the norm requires the rooms to exist, not
merely to be big enough if present — and because it is the complement that makes
the otaq count decidable.

What enforces it is four [[Programme rule]]s, one per limb — not one rule for the
clause, because the five limbs do not carry one severity. The `holl` limb has no
rule: `resolve` invents a hall when the Brief names none, so it holds by
construction.

**Combined sanitary unit** — `birləşdirilmiş sanitar qovşağı`, one room holding
both the washing fixture and the WC. Two [[Room type]]s are one: `shower_room`,
which has composed a pan since the layer was authored, and `bathroom_combined`.
A plain `bathroom` is **not** one — it is a bath and a body zone, and it holds no
pan.
_Avoid_: reading AzDTN cl. 5.10's restriction of the unit to one-otaq social
housing as a constraint on what v1 draws. C8 forbids reading a regulatory
document as a compliance target, and 67.24% of real dwellings combine, so the
clause does not describe practice either.

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

A Space is **one or two rectangles**, never more. Not a rectangle, which is what
every document here assumed until it was measured: half of real rooms are not one.
See [[Part]].

⚠️ **This read *"a rectangle or an L"* until ADR 0045, and the L was never the
whole of it.** Two rectangles sharing an edge make four shapes, and **44,8 %** of
real two-part Rooms are not an L. The glossary deliberately does **not** name
them: the contract constrains part count and the shared edge, and says nothing
about which shape the parts form, so naming the shapes here would imply a
distinction the system does not make.

**Part** — one of the at most two axis-aligned rectangles a [[Space]] is the
union of. The **first** part carries the Room's own dimensional minima; any
further part carries the **leg floor**, and the two must share an edge of at
least that floor — below it the two legs are not one room, they are two rooms
with no door between them.

**Two Parts flush at both ends are one Part** (ADR 0045). Their union is a
rectangle, so the two-part encoding says nothing the one-part encoding does not —
and it is not harmless: measured per part, such a Room hard-fails the aspect rule
on **48 %** of corpus cases against **4 %** measured merged, because the rule sees
two slivers where the room is one rectangle.

**Which shape the parts form is not a property of a Part.** The contract
constrains part count and the shared edge — *buildability* — and leaves shape to
the [[Proposal]], on the same ground that keeps the solver out of it: shape is an
architectural claim, made where the arrangement is made.

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
_Avoid_: inferring `load_bearing` from a wall's thickness, length or position.
Nothing in the pipeline carries it — the conversion cuts every wall at its
centreline and hands over no thickness, and the trained source has no thickness
token — so any value would be the engine's guess, and **a drawn wall weight is
read by the person holding the sheet as a structural instruction**. ADR 0026.

Its thickness is a **[[Layer set]]**, never a scalar.

**Wall weight** — how many distinct cut-[[Wall]] thicknesses a sheet draws, read
off the [[Layer set]] total. v1 draws **two**, envelope and internal, never three. Real *surveyed* dwellings show
three in **76.1 %** of cases — envelope, internal bearing, partition — because
they were engineered before they were measured; a concept plan for a dwelling
that has not been engineered has two. The gap is real and is **reclassified, not
closed**: the sheet says in a general note that load-bearing walls have not been
identified, which turns a competence signal into a scope one. ADR 0026.
_Avoid_: reading uniform `t_int` as the cause. The shipped 150 lands 4 mm from
the corpus-optimal single value; **the value is not the problem, the uniformity
is**, and the uniformity is downstream of having no structural model at all.

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
plan was generated. A **cased opening** is an Opening with no leaf, which a model
that only knows hinged doors cannot say.

**A window is typed differently from a door, and the asymmetry is deliberate.** A
door takes a whole catalogue entry chosen by its receiving Room. A window takes a
**fixed height** from its Room and a **width selected from a series** to meet the
Room's glazing requirement. The catalogue is discrete either way; what differs is
that a door's size answers *what goes through it* and a window's answers *how
much light the room owes*, and only the second is a function of the room's area.
ADR 0024.

_Avoid_: "which is how most homes join a kitchen to a living room". That is a
Western prior and the one profile v1 ships refutes it twice — the `AZ` catalogue
manufactures a **glazed living-room door**, and a gas hob is the Baku norm. In
`AZ` the only cased opening is between `living` and `dining`, and an open kitchen
is expressed by **merging Rooms** in the Brief rather than by deleting a leaf.
`openings.md` §5.

An Opening has **three widths and they are not the same number**: the *structural
opening* that voids the wall, the *leaf* that is manufactured, and the *clear*
width you can carry furniture through. Which one is meant is always stated —
which is not the same as all three being published. v1 publishes structural and
leaf and **refuses to publish clear**, the frame section being a joinery detail
no region profile carries and no shipped rule consuming it.

An Opening's **height is catalogue and its placement is not.** The catalogue mark
fixes height and width together — a GOST mark reads *height*-then-*width*, so `OR
15-12` is 1500 × 1200 and not the reverse — while where the opening sits
vertically is fixed by the [[Head datum]] and never stored per instance. The same
window sits at one height in a living room and another over a kitchen counter, so
the catalogue could not carry it and an invented per-instance sill would be the
same tell as an invented width.

**Head datum** — the single line every window hangs from, and the reason a sill is
derived rather than stored: `sill = head datum − opening height`. Doors sit below
it at their own catalogue height. ADR 0012.

_Avoid_: "because a balcony door and the window beside it share a lintel". The
number is right and that reason is **dead in v1**, which models no balcony, so
the entry the datum was read off can never be placed. What justifies 2200 is that
an AZ window head sits **above** the door head, which is what a real elevation
does and what keeps doors reading at their own 2100. `openings.md` §2.5.

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
any fixture or furniture exists. Its side is the **leaf** width, not the
structural opening — 100 mm smaller, which is 100 mm of relief in every wet room.

**Receiving Space** — of the two Spaces an Opening joins, the one the Opening
*belongs to* when you name it out loud: "the bathroom door". Resolved by a fixed
ladder — private, then wet, then further from the entrance, then smaller — and it
is the single answer three separate rules read: which catalogue entry the door
takes, which side the [[Nib]] is measured into, and which way the door swings.
`openings.md` §3.3.

_Avoid_: "the room the door opens into" as a synonym. A door swings into its
Receiving Space by default and may be flipped out of it when clearance fails, so
the two coincide in the normal case and come apart in exactly the case worth
naming.

**Nib** — the clear run of wall left at a door's **leading edge** — the handle
side, not the hinge side — maintained back into the [[Receiving Space]]. 300 mm
along the wall, 1200 mm deep. The along-the-wall half is ergonomic: architrave,
handle, elbow. The depth is accessibility, kept because it costs no wall run.

It is the reason a door needs more shared wall than its own width: jamb + opening
+ nib, the same total whichever end the door is hinged at, and the 400 mm the
solver's contact threshold had never reserved. ADR 0021.

**Placement order** — Openings are placed **breadth-first from the primary
entrance**, each pushed to the end of its shared run nearest where the path
arrives. Realised circulation is a tree rooted at the front door, so the order is
determined rather than searched. It is the rule an architect follows without
naming it — you place doors as you walk in — and it is what leaves the far wall of
a room unbroken. The **hinge** is then derived from the position rather than
chosen, so the schedule's handing column and the plan's swing arc cannot
disagree. ADR 0021.

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
_Avoid_: reading this term in a solver document. `experiments/solver-toy/` and
`docs/research/solver-formulation.md` use "witness" for something else entirely —
a **known-feasible ground truth**, the exact tiling that makes a failure to solve
a fact about the projection problem rather than about an impossible Brief. The
two senses share no referent. The drawing sense is this glossary's; the solver
sense is local to the harness and is always qualified there.

**Plan mark** — the short sequential label that ties an Opening on the plan to
its row in a schedule: windows `ОК1`, `ОК2`, …; doors a **bare number**, no
prefix; both drawn in a Ø 5 mm circle. The join between the drawing and the
schedule, asserted total in both directions — and the join key is **(kind,
number)**, never the number alone, because doors and windows number in two
separate spaces and a join on the number silently matches door 1 to window 1.

**Product designation** — what the Opening *is*, as the manufacturing standard
names it: `ДГ 21-8`, `ОР 15-13,5`. It encodes the opening size, **height then
width** in decimetres, with a comma where a group is fractional. It lives in a
schedule column and never on the plan. Distinct from the [[Plan mark]] because
they answer different questions — where is it, and what do I buy — and this
system carried one string doing both until ADR 0024.

_Avoid_: printing a designation for a size the standard does not publish. A
window width is now selected from a series whose upper members are the engine's
own extension of the GOST grid, and above that boundary the schedule carries a
plain dimension string. An invented designation is the same failure as an
invented room abbreviation.

**Sheet set mark** — the designation carried by the **set** of drawings, with
sheets numbered sequentially inside it: `<job>-MH`, *Vərəq 1 / 2*. Not a
per-sheet discipline code. The difference matters because the two conventions are
not translations of each other — a US sheet number and an SPDS set mark carry the
identifier at different levels, so `A-101` has no counterpart of the same shape.

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
**declaration**, three consumers: a hard filter on finished candidates, the
constraint set the solver projects onto, and the **parse-time** bounds computed
before any Plan exists — see [[Pre-image bound]]. Not one implementation — the
solver posts inequalities before geometry exists, the filter evaluates finished
geometry, and rules about Openings are unpostable because Openings are placed
after the solve. Each predicate therefore names its **enforcement site**, and only
those enforced at both can be asserted to agree.

**Pre-image bound** — a check on a **Brief** that is the arithmetic pre-image of a
predicate on a Plan: the set of Briefs from which *every* reachable Plan fails that
predicate. It is not a new rule and it has no severity of its own — it **inherits**
the severity and the threshold of the predicate it is the pre-image of, because
firing softer promises a Plan the validator will destroy and firing harder refuses
Briefs the validator would have passed. ADR 0015.

The implication has to run one way only: *every* Plan from this Brief fails, not
*some might*. A check that only makes failure likely is a heuristic, and shipping
one at `hard` refuses buildable Briefs.
_Avoid_: calling one a "validation" or an "early check" — both hide that its
severity is a read of another rule rather than a judgement. A bound with a
threshold of its own is a sign it is not a pre-image.

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

**Space plane** — the plane a Space's clear area is measured on. There is **one**,
the **bar plane**: `erode(∪ parts, t_int/2)` with a **boundary rule** — an edge on
the Envelope is *not* eroded, because ADR 0001's tiling edge there already sits at
exterior-inner-face + `t_int/2`. Every predicate in `rules.json` is stated on it
and [[Hard area floor]] is read against it.
_Avoid_: "the clear area", unqualified, and above all the **solver plane** — the
name this term carried for the second quantity `solver.py` read, which eroded all
four sides of every Room and so measured a perimeter Room a median **3,9 %**
smaller. It was a defect, not a distinction: ADR 0039 has the solver account the
boundary per side and read the bar plane, and the second name is retired with it.
Kept here because both were clear areas and both defensible on their own terms,
which is why the unnamed version shipped one component strictly stricter than the
rule it posted — and one, `dim.max_area`, strictly looser. A number stated on the
wrong plane constrains geometry to a figure no regulator wrote.

**Living area** / **Useful area** — the two quantities an Azerbaijani residential
plan annotates, as a **fraction**, living over useful. *Living area* is the sum
of Space area over Rooms carrying the habitable flag — the geometry flag, not
[[Otaq]], which is the narrower marketing count; *useful area* is the sum of all
Space areas. One fraction per dwelling, never per room — per room it would divide
a bedroom's area by itself.

_Avoid_: treating **useful area** and the [[Area convention]]'s `ümumi sahə` as
one quantity. They are **numerically identical in v1 and are not the same
thing**: `ümumi sahə` counts balcony, loggia and eyvan at a coefficient and
useful area does not, and v1 models none of the three. They diverge the day a
balcony is modelled, and a reader who has assumed otherwise will be wrong on that
day.

**Partition footprint** — the plan area the internal walls of one dwelling
occupy, always stated as a **share of Σ Space area** and never as a share of the
interior. The two denominators are different numbers — a footprint of *f* against
Σ Space is *f*/(1+*f*) against the interior — and the interior it implies is
`Σ Space × (1 + f)`, so a reader who takes the published share for the other one
sizes a box wrong in the direction that matters. Per-dwelling, not a constant: it
is a property of how much partition a *layout* needs, which is why it is only
known after the solve and why anything reading it before then reads a quantile of
a measured distribution rather than a value.
_Avoid_: "wall ratio", "efficiency", "net-to-gross" — all three are quoted
against gross area elsewhere in the industry, which is the wrong denominator
here, and `efficiency` is separately a live `ENGINE_CHOICE` field.
_Avoid_ also: reading **any** shortfall in delivered Σ Space as a partition
footprint. It is the last term in the chain and the easiest to blame, and the two
quantities in front of it — which region the tiling covers ([[Solve domain]]) and
whether the Envelope's ring was held fixed while it was solved — are both larger
and neither is a wall. *The sizing rung under-delivers by four per cent* was
raised to widen `f` and closed without touching it.

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
**base** of the floor the Acceptance bar rejects below, and where a
[[Region profile]] publishes no [[Statutory floor]] it is the whole of it. It
stands in for a legal minimum where none exists: most regions prescribe none, and
the regions that do disagree with each other by nearly a factor of two.
_Avoid_: "it is the floor the Acceptance bar rejects below", full stop — a
[[Statutory floor]] may now raise it, and this term is only the base.
Stated as a **shorter side and a longer side**, never as
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

**Statutory floor** — the smallest area a [[Region profile]]'s own law permits a
room type, where that region's law says anything at all. Unlike an
[[Ergonomic minimum]] it is **transcribed, never derived** — it is a number a
regulator wrote down, and composing it would be inventing law. It is a *habitable*
floor where the ergonomic minimum is a *fits* floor, which is the whole difference
between them: 1650 mm of bedroom width is a bed plus room to walk past it, and
10 m² is a bedroom.

A profile publishes one only for the room types its law names — ten of nineteen
are silent in `AZ` — and **silence is not an error**: where there is no statutory
floor the ergonomic minimum stands alone. It always sits *below* the same
profile's [[Target area]], and it binds only where the solve failed to reach that
target.

**A law may floor a *part* of a room rather than the room, and then the profile
carries what that entails.** AzDTN floors the *kitchen zone* inside a
kitchen-diner, never the kitchen-diner. The room contains the zone, so the zone's
figure is a **sound lower bound** on the room — it refuses a strict subset of
what the law refuses, and there are no false refusals. Such a read is marked
`referent: part` and it **may floor, and may never target**: a bound that is
merely entailed is not what anyone builds, and reading it as a target
under-targets the room by the unmeasured remainder. An entailed bound may sum
cells whose disjointness the norm's *own type definition* establishes, and
nothing else. It stays **transcribed** in the sense that matters — every addend
is a number a regulator wrote — and this is the only way a figure enters this
term without being one. ADR 0034.
_Avoid_: reading an entailed bound as the smallest area the law permits that
room. It is the smallest area the law's *part* forces, and the true floor is
higher by an amount the norm may leave unstated. Where it does — and for the
kitchen-diner AzDTN does, exhaustively — the distance is the designer's
discretion and **the engine may not quantify it into this term**: every
candidate number is an `engine_choice` and belongs to the target, not here.
_Avoid_: “a Plan that reaches its target clears it by construction” — **measured
and false**. The premise holds and the conclusion does not, because a warp
delivers a *proportion* of a target rather than the target: 25,5 % of warped
candidates put some Room below its floor even when every stated target sits at or
above the profile's [[Target area]]. A statutory floor is a live constraint on
engine output, not a formality the objective satisfies on its way past.

**The licence runs out where the norm has no word for the room, and that governs
the `part` read itself and not only the sum.** A law entails a bound on a room by
naming a *kind* of room and constraining it; where a norm defines no such kind,
nothing about a room of that description is entailed at all — not the addend and
not the base cell either. `kitchen_dining` is licensed because AzDTN 2.7-3 cl. 4.7
files the `mətbəx-yemək otağı` inside the word `mətbəx` and the definitions clause
supplies its `«ayrıca zonaları»`. `living_dining_kitchen` is **not**, because
AzDTN defines no open-plan type: nothing in the norm entails that a room it has no
word for contains a `qonaq otağı` meeting cl. 5.7. **Same licence, opposite
results, and the difference is whether the norm names the room.** ADR 0036.
_Avoid_: treating a `part` read as the cautious option. An entailed bound is only
*sound* while it is *licensed*; an unlicensed one is an invention that inherits a
`conf: verified` cell's authority, and it can reject rooms the law admits — the
withdrawn 21,0 / 22,0 open-plan floor sat above **all five** real Baku rooms of
that kind. Where the licence fails the cell is `null`, and the
[[Ergonomic minimum]] stands alone in the ordinary way.

**The licence is carried by the read, as data, and the clause is named.** It was
prose in an ADR for one day, which is long enough: the rule was stated and broken
in the same decision, and no check could see it because no check reads prose. Now
every entailed read names the clause whose *type definition* grants it, and the
sum a read composes is gated separately — the sum was the narrower half all
along, and it is currently empty on every row. ADR 0037.
_Avoid_: reading the presence of a floor as evidence the read was granted. The
number and its licence are two facts, and the withdrawn one had the first.

**A Region profile may raise a hard floor and may never lower one.** That is the
one direction in which region reaches the reject set, and it is monotone by
design: a region nobody has surveyed still gets the full ergonomic bar, and no
profile can take a predicate away or weaken one.
_Withdrawing a raise that was never licensed is not lowering one._ The rule
forbids a profile going **below** the region-free base; the base is the
[[Ergonomic minimum]], and a cell returning to it because its read was never
granted is a correction rather than an exercise of the rule in reverse. Reuse the
reasoning and never the precedent: the test is whether the licence held, not
whether the number is inconvenient.

**Hard area floor** — the area a Space is actually rejected below:
`max(`[[Ergonomic minimum]]`, `[[Statutory floor]]`)` for its Room type, per Room
and never per part. Named because the two halves are **one number with two
sources and two costs**, and every consumer wants the composed number while every
amendment touches exactly one half. The ergonomic half is derived, region-free
and rejects 0,19 % of real dwellings; the statutory half is transcribed, carries a
region, and is the entire measured cost of the pair. Both are `hard`, and a
predicate states only its own half — the composition is this term, so that raising
one limb of one region's law is a value edit and not a rule edit.
_Avoid_: reading the composed floor as a single rule with a single severity, or
quoting either half's corpus cost as the pair's. And do not reach for it as the
number a room is *sized* to: it is a floor far below what anyone builds, and the
liveable number is the [[Target area]].

**Target area** — the area a Room is *sized to*: the two-sided band the solver's
soft objective is centred on, and the number a Homeowner reads back as their own
request. It is the liveable figure the [[Hard area floor]] sits far below.

**It is a band and not a floor**, and that is the distinction the whole term
exists to carry. A delivered Space landing off its target is the **normal** case,
not an error, so *"the plan is smaller than I asked for"* is a statement about a
band's lower side rather than a defect. A Room with no target has **no upper
bound either**, which is how a 40 m² WC once passed every rule.

**Where it comes from is a ladder, not a constant.** A [[Region profile]]'s
preferred value first; the corpus median where the profile is silent — which is a
disclosed [[Corpus provenance]] mismatch, a *number* rather than a layout; and
where neither answers, the field is absent and the Room is sized against its
ergonomic floor alone, surfaced as an assumption saying exactly that.

**A profile's preferred values are measured practice floored by regulator
recommendation — not a regulator's minimum wearing a target's name.** A
recommended minimum used as a *centre* under-sizes by the whole distance between
the minimum and the ordinary, and it does so invisibly: every cell can sit within
a tenth of practice while the *dwelling* their sum describes is a tenth too
small. ADR 0035.

**Measured evidence may raise a preferred value and may never lower one**, where
the evidence is a built population narrower than the region it stands for. The
asymmetry is the sampling: a population drawn from the affordable end sitting
*above* a target contradicts its own bias and is strong, while the same
population sitting *below* is only that bias restated. This is the
[[Region profile]]'s monotone rule in a second place and for a second reason —
that one is about legal force, this one about who was measured.
_Avoid_: treating a target as the smallest acceptable area. It is the middle of a
band, the floor is a different term with a different severity, and reading one as
the other is what makes a plan legal and unliveable.
_Avoid_: "preferred area", "market default", "soft objective target" and
"`target_area`" as if they were four things. They are this one, seen from the
profile, the tier table, the objective and the Brief.

**Region profile** — the set of *conventional* values a Plan is built and drawn
to: the thickness catalogue, the decimal separator, the room-name abbreviations,
the opening catalogue keys, the preferred room areas ([[Target area]]), the window fraction, and
the [[Statutory floor]]s its law publishes.
Underneath it is really a **construction system plus a drawing convention**;
country is only a proxy, and a poor one — Germany and Azerbaijan are both
fired-brick masonry with incompatible modules, while the UK and the US are both
frame-and-cavity. A profile changes which Plans are *preferred*, which strings are
*printed*, and — in **one direction only** — which are *rejected*: it may raise a
hard floor above the region-invariant [[Ergonomic minimum]] and may never lower
one, add a predicate, or remove one.
_Avoid_: "a profile can change which Plans are preferred and which strings are
printed, **never** which are rejected" — true only while every hard dimensional
floor was ergonomic, and a [[Statutory floor]] is now hard too.
A Plan carries its profile for its whole life. v1 ships exactly one, `AZ`.

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

**Room proportion** — the ratio of a Space's longer to its shorter clear
dimension, measured on its bounding box **in the dwelling's own frame** and
therefore **orientation-free**: it does not know which wall the window is on. It
is what `dim.aspect_ratio_hard` and `dim.aspect_ratio_soft` measure, and what
Palladio means by *"two squares"*. Bounded hard at 3.0 and ranked by a gradient
toward the class's typical proportion. _Avoid_ calling this "aspect ratio" when
the thing meant is [[Daylight depth]] — one word for the two of them is the
confusion ADR 0048 exists to end.

**Daylight depth** — how far a habitable room extends **away from its glazed
wall**. Oriented, unlike [[Room proportion]]: the same rectangle has two different
daylight depths depending on which side is glazed. This is the quantity every
regulator surveyed actually bounds — SNiP II-L.1-71\* cl. 3.4 at ≤ 6 m and
≤ 2× width **under single-sided lighting only**, Portugal's RGEU art. 69.º
n.º1 d) waiving its 2:1 for openings in opposite walls — and it is the reason a
deep room is bad, which proportion only proxies. **The engine does not have it
yet**; `win.habitable_has_window` already identifies the exterior-condition run
each Room holds, so it is computable rather than blocked. A 6 × 3 m room glazed
on its long wall has proportion 2.0 and daylight depth 3 m: elongated by one
measure, exemplary by the other.

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
- **Region is a convention, and in one direction a standard of care.** The [[Region profile]] chooses what a Plan is drawn and built to; the [[Ergonomic minimum]] is the region-free **base** of what is rejected, and a [[Statutory floor]] may raise it. Changing region can therefore change the reject set — **upward only**, on predicates that already bind. _Avoid_: "changing region never changes the second", which held only while every hard dimensional floor was ergonomic.
- **Neufert-grade** describes dimensional standards — ergonomic and dimensional
  design data. It is not a building code, and no legal code-compliance claim is
  made anywhere in this system.
