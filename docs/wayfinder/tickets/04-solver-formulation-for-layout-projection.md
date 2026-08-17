---
id: 4
title: Solver formulation for layout projection
parent: map
labels: [wayfinder:research]
status: open
assignee:
blocked_by: []
---

# Solver formulation for layout projection

## Question

Can C10 — *model proposes, solver projects* — actually be formulated and solved
in interactive time? This is the highest-risk decision on the map: if the answer
is no, the whole architecture changes.

The formulation to prove or refute: given a **fixed boundary polygon** (possibly
non-rectangular) and a **proposed layout** from a learned model, find the feasible
arrangement **nearest** to the proposal, where feasible means:

- no room overlaps, rooms tile the boundary with no unassigned slivers
- per-room minimum dimensions and areas by room type
- required adjacencies satisfied; **forbidden** adjacencies respected
- circulation correct — every room reachable from the entry without passing
  through a bedroom or bathroom
- every habitable room touches an exterior wall
- wet rooms clustered onto shared plumbing walls
- walls orthogonal, snapped to a grid

Answer, with worked evidence rather than a literature summary:

1. **Which formulation.** CP-SAT (OR-Tools, Apache 2.0) with integer grid
   coordinates? MIP? Rectangular-dual construction from the adjacency graph, which
   satisfies topology by construction and uniquely supports *forbidden*
   adjacencies? A hybrid — dual for topology, CP-SAT for metric refinement?
2. **How "nearest to the proposal" is expressed as an objective.** The model emits
   axis-aligned boxes. Minimise summed centroid displacement? IoU loss? Preserve
   relative ordering and proportion rather than absolute position? This choice
   decides whether the output still *looks like* what the model proposed.
3. **Whether the reachability constraint is expressible at all** in CP-SAT, or
   whether it must be a post-filter or a separate graph-construction step.
4. **Runtime.** Build a real toy: 8, 12 and 24 rooms in a non-rectangular
   boundary. Report solve times and whether they hold at interactive latency. The
   24-room case is where the sibling project's diffusion approach collapsed
   (35.8–66.8% overlap) — this is the case that matters.
5. **What happens when the proposal is infeasible.** Does the solver return the
   nearest feasible plan, or nothing? Graceful degradation is the entire value of
   C10.
6. **`kiwisolver` (BSD)** for the deferred interactive-drag case (C7) — same model,
   or a second one?

Deliverable: findings doc plus a **runnable toy solver** demonstrating the
formulation on the three room counts, with measured times.
