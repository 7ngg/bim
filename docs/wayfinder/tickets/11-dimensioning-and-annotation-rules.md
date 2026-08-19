---
id: 11
title: Dimensioning and annotation rules
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: [1, 3]
---

# Dimensioning and annotation rules

## Question

What exactly gets dimensioned and annotated, and by what rule?

This is the differentiator. C3 makes dimension strings and room tags a hard floor,
and the competitive scan found **no surveyed product documents a dimensioning,
annotation, title-block or schedule system** — eleven vendors across four price
tiers. Every one of them hands the user to Revit or AutoCAD at exactly this point.
So there is no prior art to copy and the rules must be derived.

Decide:

1. **Which chains are generated.** Overall external chains on which sides? A
   per-room chain? An intermediate chain picking up wall faces and openings? The
   architectural convention is usually three tiers — confirm it and adopt it, or
   justify departing.
2. **Where dimension lines sit.** Offset from the building face, spacing between
   tiers, and what happens when they collide with each other or with the plan.
   Collision avoidance is the part that makes this hard, and it is why nobody
   ships it.
3. **What is measured to** — wall centrelines, wall faces, or structural grid?
   These give different numbers and architects have opinions. This choice couples
   directly to the wall representation chosen in *Canonical geometry model*.
4. **Room tags.** Name, area, both? Placement rule — centroid, or largest
   inscribed circle so the tag never lands outside a concave room? Behaviour when
   a room is too small for its own label.
5. **Openings.** Are doors and windows dimensioned and tagged, or scheduled, or
   both? A door schedule is a table, which is a different output entirely.
6. **Drawing furniture.** Scale, north point, title block, sheet size, layer names
   and lineweights. Which conventions — and does the layer naming follow a
   published standard so a Practitioner recognises it?
7. **Rounding and units.** Millimetres or metres, and what rounding. Dimension
   strings that do not sum to the overall are the classic embarrassment; whatever
   rule is chosen must guarantee they add up.

Both blockers are now closed. What they hand over:

- **Rule 3's input.** The model stores wall **centrelines**; the human-facing
  quantity is the **clear** dimension, between finished faces. The two are never
  interchangeable and every number that crosses a boundary says which it is. A
  chain measured to centrelines and labelled as clear is the failure mode here.
- **Annotation is derived, not stored** (ADR 0002). A `Drawing` is a Plan plus a
  sheet plus resolved annotation; only human corrections persist, as
  `AnnotationOverride`s keyed by **relation** — the wall segment between two named
  rooms — because derived geometry has no stable id across a regenerate. Rule 2's
  collision avoidance is therefore a *function* to be specified, with its output
  overridable, not a set of stored positions.
- **`ezdxf` authors genuine `DIMENSION` entities**, verified by execution — but
  **we render the geometry block, not the CAD app**, so appearance is entirely this
  ticket's responsibility. `DIMLFAC` is 100.0 on every shipped `EZ_*` dimstyle and
  must be set to 1.0 against the model's 1 unit = 1 mm, or a 4000 mm wall prints as
  "400000". R2000 is the hard floor.
- **Rule 7's rounding problem has a free answer**: the model is integer
  millimetres, so a chain sums exactly. The classic embarrassment is unavailable
  unless we introduce it by rounding for display.

Deliverable: the annotation rule set, precise enough to implement, plus a worked
example on one plan.

## Resolution

**The rule set is specified in full at
[`docs/spec/annotation.md`](../../spec/annotation.md), with a worked example
computed end to end on a one-bedroom flat. The convention decision and its
rejected alternative:
[ADR 0004](../../adr/0004-published-dimensions-measure-wall-faces.md).**

The standard adopted is **a Practitioner's own issued set** — not "legible", not
"good enough for a Homeowner". Several rules below are more work than the obvious
alternative and were taken anyway.

### What the blockers deleted before this ticket started

- **Rule 4's hard case does not exist.** The solver tiles rectangles and
  `erode(rect, t/2)` is a rectangle, so no v1 Space is concave and the centroid
  *is* the pole of inaccessibility. Largest-inscribed-circle placement is unneeded
  and unspecified until non-rectangular rooms exist.
- **Rule 7's problem does not exist, conditionally.** Integer millimetres sum
  exactly. The condition is the unit: print metres to 2 dp and the classic
  embarrassment returns immediately. It is held off by an invariant rather than by
  care — **a dimension rendered in any unit other than integer millimetres may not
  be part of a chain**. The sheet is millimetres and chains; the preview is metres
  and no chain; the two never meet.
- **Rule 2 is three local rules, not a solver.** Chains sit on a ladder outside
  the Envelope bbox, so chain-vs-plan and chain-vs-chain are impossible by
  construction; one tag per Space makes tag-vs-tag impossible. Worth saying loudly,
  because the competitive scan found nobody documents this layer and a reader will
  infer that means it is hard. **It is unglamorous, not hard** — and an annealer
  built for it would be built for a problem that has none.

### What the blockers broke

**Every wall thickness in a region profile must be an even number of
millimetres.** ADR 0001 needs `erode(rect, t_int/2)` in integer millimetres and
tier 1 needs `t_party/2`. 100/120/140/200/240/300 are fine; **115 mm (half-brick)
and 125 mm — DIN 4172's octametric module, and a common UK blockwork-plus-plaster
build-up — are not.** They put every wall face on a half-millimetre and every
clear dimension off-integer. Found here, handed to *Which region profiles ship in
v1*.

### The rules, by the ticket's own numbering

1. **Which chains.** Four tiers on a ladder: tier 1 overall footprint; **tier 2
   one chain per side, all four sides**, dimensioning only the partitions that
   *reach* that side; tier 2b running dimensions from datum for any partition
   reaching no side; tier 3 openings jamb-to-jamb per Envelope edge. Plus **in-plan
   setting-out dimensions for every internal opening**. The departure from the
   two-adjacent-sides convention is deliberate: projecting the whole plan onto two
   sides yields ticks matching no room and no wall on that elevation — arithmetic
   debris, and an immediate tell. Per-side restriction makes **every tick a real
   clear dimension of a real room**, and all four chains still close.
2. **Where lines sit.** Rungs at 10 / 18 / 26 (/34) mm paper. Collisions: text
   outside with a leader where a segment is narrower than its text, alternating
   above and below; the tag degradation ladder; crowded setting-out dimensions step
   out one increment. **The priority rule decides every case — information outranks
   labelling. A dimension never moves for a tag; the tag moves.**
3. **What is measured to. Faces, never centrelines**, with one declared exception:
   tier 1 measures a party edge to its centreline, per GIA and IPMS, because a
   party wall's outer face lies inside the neighbour's home. ADR 0004 records that
   this is the *harder* formulation — centreline chains have no narrow tick and no
   collision at all, which is exactly why the convention exists — and takes faces
   anyway, because the Acceptance bar, the ergonomic minima, the standards corpus
   and a Homeowner's tape are all clear dimensions, and a centreline number
   labelled as a room size is wrong by `t_int` on every room and every axis.
4. **Room tags.** Centroid. Name 3.5 mm, area / clear dims / ref at 2.5 mm.
   Degradation: text step down, then the region profile's **published
   abbreviation** (`WC`, `ST`) — never a truncation — then 1.8 mm, then leadered
   into a fixed-pitch margin column. **No line is ever dropped**, reversing an
   earlier draft of this rule: the small rooms are the ones whose area is
   contested, and a plan whose 4 m² store carries no area while its living room
   does is a plan someone queries.
5. **Openings. Dimensioned *and* tagged *and* scheduled.** Type marks join the
   plan to drawn door, window and room schedules on sheet `A-102`, composed from
   `LWPOLYLINE` rules and `MTEXT` cells because ezdxf has no `ACAD_TABLE`. No fire,
   thermal, acoustic or structural columns — excluded because C8 forbids the claim,
   and a `TBC` in a fire-rating column *is* a claim.
6. **Drawing furniture.** Scale held at 1:50 and the sheet grows —
   `(A3,1:50) → (A2,1:50) → (A1,1:50) → (A1,1:100)`. ISO 3098 text sizes only.
   **US National CAD Standard / AIA layers**, which corrects the export research's
   ad-hoc `A-DIMS` / `A-ANNO` / `A-HATCH` to `A-ANNO-DIMS` / `A-ANNO-TEXT` /
   `A-WALL-PATT`. Title block with `CHECKED` present and permanently `—`, revision
   block, north arrow, scale bar, generated general notes carrying C8 **on the
   drawing** — a DXF outlives the session that made it and arrives where the
   product copy never reaches.
7. **Rounding and units.** Integer millimetres on the sheet, no suffix,
   `DIMDEC 0`, `DIMLFAC 1.0`. Metres to 2 dp on the preview. Decimal separator from
   the region profile.

### Added, because the ticket asked for annotation and a drawing is judged first

**Plan graphics** were not in the ticket and had to be: a lineweight hierarchy
expressing what the cutting plane passes through, solid poché with island paths,
door leaves at 90° with swing arcs, cased openings drawn with no leaf and no arc,
windows as frame lines plus a centred glazing line, `FFL ±0.000`. A plan with
perfect dimensions and flat single-weight linework reads as generated before a
single number is checked.

### Three decisions reversed mid-session

Taken first on ease grounds, then reversed against the Practitioner standard:

| First answer | Final | Why |
|---|---|---|
| No drawn schedule — "a table layout engine is a different deliverable" | **Three schedules ship, drawn** | An ease argument. A real set has schedules, and the scan found **no vendor documents one** — that is the differentiator, not the cut |
| Internal doors positioned by a general note | **Every opening dimensioned**, internal ones in-plan | The note convention is real, but here it existed to keep annotation off the plan interior. A builder sets out from those numbers |
| Scale drops to 1:100 to stay on A3 | **Scale held, sheet grows** | An architect does not halve the scale to save paper |

### New machinery this introduces

- **The Drawing check** — eleven predicates gating whether a *file is written*.
  Explicitly **not** the Acceptance bar and **not** in `rules.json`: the bar has
  two consumers, which is what forced its registry and conformance test; this has
  one and runs at export after the bar has already passed, so a third consumer
  would reopen a question *Acceptance validator spec* closed. The predicate that
  earns its place is `draw.measurement_matches_model`, which catches the **stale
  block** — ezdxf ships both a semantic dimension and a pre-drawn picture of it,
  and a mutated definition point without a re-render makes the two disagree
  invisibly.
- **Witness** and **audience** as domain terms, and `AnnotationOverride` sharpened
  to **placement-only** — an override that could change a number would let a human
  make the drawing lie about the model, which is the failure this layer exists to
  prevent.

### Handed to other tickets

- *Which region profiles ship in v1* — **wall thicknesses must be even**; the
  profile also now owns the decimal separator, the room-name abbreviation table,
  and the opening catalogue keys the type marks cite.
- *Opening placement rules* — is the **single source** of the internal-door
  setting-out constant and of handing and swing, all three of which the drawing and
  the door schedule consume.
- *Area measurement convention* — the room schedule, the room tag and the title
  block's `AREAS` field all quote it, and **tier 1's party-wall-to-centreline rule
  follows it** rather than keeping its own, so one drawing cannot quote a footprint
  on one convention and an area on another.
- *Homeowner product surface* — inherits the audience-tag construction and the
  preview's exact content.
- *Solver timing variance sweep* — should also record annotated extent, unique
  witness count per side, and the sheet and scale chosen, at 8 / 12 / 24 rooms.
  The sheet ladder is unmeasured above five rooms.
