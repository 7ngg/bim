---
id: 7
title: Acceptance validator spec
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: [5]
---

# Acceptance validator spec

## Question

Turn C6's seven-item bar into **precise, machine-checkable predicates with real
numbers and real tolerances**.

This is the spec for the layer that makes output correct rather than merely
plausible, and it is used twice: as the hard filter on generated candidates, and
as the constraint set the solver is projecting onto. Those two uses must not
drift apart, so the predicates are written once and consumed by both.

The bar as agreed while charting:

1. Circulation is correct — every room reachable from the entry without passing
   through a bedroom or bathroom.
2. Minimum dimensions per room type met; no unusable slivers, no sub-1m corridors.
3. Every door physically fits its wall and its swing hits nothing.
4. Every habitable room touches an exterior wall and gets a window.
5. Wet rooms clustered so plumbing shares walls or stacks.
6. Walls orthogonal, thicknesses standard, junctions closed — no gaps, no overlaps.
7. Circulation area within a sane fraction of the total.

For each, settle:

- **The exact predicate.** "Reachable without passing through a bedroom" needs a
  defined graph: what are the nodes, what makes an edge, is a door required or
  does an opening count?
- **The number, and where it came from.** Comes from the constraint table produced
  by *Dimensional standards corpus*. "Sane fraction" and "sub-1m" are placeholders
  and must become values with a citation.
- **The tolerance.** Floating-point geometry never closes exactly. What
  counts as a closed junction, a coincident wall, a zero-area sliver?
- **Hard or soft.** Which failures reject a plan outright, and which are scored
  and surfaced as warnings? A rule that rejects 99% of candidates is a bug in the
  rule, not a quality bar.
- **What the Homeowner sees when a rule fires.** C4 established that assumptions
  are surfaced; failures deserve the same treatment.

Also settle two things the seven items do not cover:

- **Entry.** What defines the front door, and is exactly one required?
- **Total-area agreement.** The brief states a target area. How far may the
  produced plan drift before that is a failure?

**Inherited from *Canonical geometry model*, now closed** — do not re-derive:

- **The tolerance question is deleted, not answered.** The model is **integer
  millimetres**, so "closed junction", "coincident wall" and "zero-area sliver" are
  integer equalities, not tolerances. Tolerance exists only at import boundaries.
- **C6 item 2's "sub-1m corridors" placeholder resolves to 900 mm** — minimum clear
  width of every hall or landing, AD M M4(2) ¶2.22a, with a 750 mm pinch allowed
  for no more than 2 m (¶2.22b). VERIFIED, OGL-licensed.
- **Two new predicates** the geometry model asks for: `len(storeys) == 1`, and
  *Space polygon equals the centreline rect eroded by `t_int/2`* — the second is
  what keeps a cheap derivation honest, and it fails the day internal wall
  thickness stops being uniform.
- **Item 3's swing clearance has no finished predicate in the corpus** — only
  components: a 300 mm nib to the door's leading edge maintained back 1200 mm; 1500
  mm between lobby doors and between swings; the entrance-level WC door opening
  outwards overlapping the pan by 250 mm. Composing them is this ticket's job, and
  *Opening placement rules* consumes the result.
- **Areas are measured on the Space polygon** — but which measurement convention
  that is remains open, in *Area measurement convention*. Until it closes, do not
  assume the minimum areas in `data/standards/room-constraints.json` and the
  computed Space areas are the same quantity.

Deliverable: the predicate spec, with each number traced to its source. Note for
the session: the sibling project measured overlap by both bounding box and true
polygon intersection and found they agreed for a box-emitting backend — the
polygon metric is the one that survives a change of generator. Re-verify per C11
rather than inheriting the finding.
