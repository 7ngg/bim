---
id: 10
title: Brief schema and parsing contract
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: [5, 9, 17]
---

# Brief schema and parsing contract

## Question

What is the **structured brief** — the object a prompt is parsed into, and the
thing the rest of the system actually consumes?

C4 makes this the real interface: the prompt is the front door, the brief is the
product, and it stays editable. So its schema is a public contract, not an
implementation detail.

Decide:

1. **Fields.** Room list with types and target areas; total area; envelope (from
   *Building scope and envelope handling*); adjacency wishes; orientation and
   aspect preferences; occupancy ("a family of four"); style or lifestyle notes
   that have no geometric meaning — are those captured or discarded?
2. **How adjacency is expressed by a Homeowner.** "Kitchen open to living" is a
   prompt phrase; what does it become? Required adjacency, shared opening, or a
   merged space? Forbidden adjacencies matter too and nobody thinks to state them.
3. **Defaults.** Every unstated field is filled from the constraint table produced
   by *Dimensional standards corpus*. Which fields are defaultable and which make
   the brief invalid if absent?
4. **Assumption surfacing.** C4 requires that every invented value is visible.
   What does the user see — a marker per field, a summary block, both? An invented
   *room* and an invented *area* are different in kind; does the interface
   distinguish them?
5. **Validation and repair of the brief itself.** A brief can be internally
   impossible before any geometry exists — nine rooms in 45 m², a bedroom count
   that contradicts the occupancy. What is checked, and does the system correct,
   reject, or ask?
6. **Which LLM, and what contract.** Structured output, function calling, or
   constrained decoding? What happens on a malformed response — retry with the
   model's own output, or fail? What is the offline story so the pipeline is
   testable without credentials or tokens?

The sibling project built exactly this and has 235 offline tests behind it. Per
C11 nothing is inherited — but its `parser/` and `schema/` are worth reading as a
source of *questions already discovered*, then answering them independently.

Deliverable: the schema, the defaulting rules, and the parse contract, with the
vocabulary landed in `CONTEXT.md`.

---

## Inherited from *Acceptance validator spec*, now closed — do not re-derive

- **The Brief needs `access_via: RoomId` on a Room.** C6 item 1 rejects every plan
  with an ensuite without it: `is_private` is true on bedrooms *and* bathrooms, and
  an ensuite is reachable only through a bedroom. Access-through is **program, not
  geometry**, so it is declared here and never inferred from the plan. Not optional
  decoration — `circ.no_private_transit` and `circ.dependent_room_host` both read
  it, and the second requires a dependent Room to have exactly one passable
  Opening, to its declared host. Covers ensuites, walk-in wardrobes, and a utility
  off the kitchen. A new field neither this ticket nor the standards ticket asked
  for.
- **`area_convention` is a hard *Brief* error when absent**, not a warning. Two of
  the 37 acceptance rules are `scope: brief` — they reject the request, not the
  candidates — and this is one. The same building differs by 20–30% between
  Wohnfläche and GIA.
- **Defaults come from `market_default`, and the hard floor is `ergonomic_min`,
  not `statutory_floor`.** That tier is `null` in the default region and is
  **unread in v1**. Do not default any field from it.
- **The entry Room and the front-door position are Assumptions, not required
  fields.** The engine defaults and surfaces them; `entry.single_primary` requires
  exactly one primary entrance door but does not require the Brief to say where.
- **Item 5's "internally impossible brief" now has a cheap check.** The sum of
  ergonomic minima for the Brief's rooms plus a circulation allowance is a lower
  bound on feasible GIA — arithmetic, no search. It is also exactly the diagnosis
  the Homeowner sees when no candidate survives, so the two must produce the same
  sentence.
