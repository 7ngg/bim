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

**Proposal** — what the learned model emits. Not a plan: a suggestion of topology
and proportion, used as the solver's objective. It is never the output.

**Plan** — the canonical geometry: walls with thickness, openings hosted on walls,
spaces, and the annotation over them. The single representation every layer reads
or writes.

**Acceptance bar** — the set of predicates a Plan must satisfy to be shown. Used
twice: as a hard filter on candidates, and as the constraint set the solver
projects onto. Deliberately one definition, so the two uses cannot drift.

## Relations

- Model **proposes**; solver **projects** that Proposal onto the feasible set.
  Plausibility is a soft objective; correctness is a hard constraint.
- The **Acceptance bar** is not advisory. A Plan that fails it is not shown.
- **Neufert-grade** describes dimensional standards — ergonomic and dimensional
  design data. It is not a building code, and no legal code-compliance claim is
  made anywhere in this system.
