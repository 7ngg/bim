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
