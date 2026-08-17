---
id: 4
title: Solver formulation for layout projection
parent: map
labels: [wayfinder:research]
status: closed
assignee: wayfinder-research-agent
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

## Resolution

**GO on C10, qualified. C10 as loosely stated — "hand the solver boxes and it
projects them" — is refuted by measurement. C10 with two amendments holds at 24
rooms in 6.25 s.**

Recommended formulation: **CP-SAT (OR-Tools, Apache 2.0) over integer grid
coordinates at 250 mm**, with two mandatory amendments:

1. **The Proposal must carry relative arrangement, not just boxes.** For each room
   pair, the cheapest of the four separations implied by the Proposal is promoted
   to a hard linear constraint, added greedily in cost order, only while the
   per-axis relation digraph stays acyclic. This converts the packing disjunction —
   the entire source of combinatorial difficulty — into linear inequalities.
2. **Exact tiling is posted soft, not hard** — `sum(w·h) == interior_area − slack`
   with a dominating penalty. Identical semantics, **29× faster search**.

### Measured (4-core Ivy Bridge, `num_workers=4`, seed 20260817, real runs)

| Rooms | Boxes only, hard coverage | Boxes only, soft coverage | +relations, soft coverage |
|---|---|---|---|
| 8 | 0.53 s VALID | 0.75 s VALID | **0.35 s VALID** |
| 12 | none in 30 s | 0.99 s VALID | **1.35 s VALID** |
| 24 | **none in 30 s** | 22.35 s **INVALID** (141 cells unassigned) | **6.25 s VALID** |

The 24-room row is the argument: neither amendment works alone, both together do.
Mean corner displacement 0.43 m at 24 rooms, from a Proposal carrying 21.6%
unassigned floor and 8.3% overlap. Result has 0% overlap and 0 unassigned,
confirmed by a validator sharing no code with the solver. Every run terminated
FEASIBLE, none OPTIMAL — **treat the time limit as a product parameter.**

### Findings that bind other tickets

- **Circulation is expressible as a constraint, not a post-filter.**
  Single-commodity flow over a reified contact graph; "no path through a bedroom"
  is one line — private rooms may receive flow but never forward it. The same
  routine over the wet-room subset gives plumbing clustering.
- **Forbidden adjacency is required-adjacency with the sign flipped**, which
  removes this ticket's main argument for a rectangular dual.
- Objective is **L1 displacement of all four corners**. IoU rejected — its union
  denominator forces a division into the objective.
- **A two-phase fallback is mandatory, not prudent.** A degenerate Proposal still
  yields a valid Plan at 8 and 12 rooms (never-infeasible is structural) but
  returns nothing at 24. A *shuffled* Proposal makes the model genuinely INFEASIBLE
  in <0.1 s, because amendment 1 promotes it to a constraint. Detection is nearly
  free.
- **Negative result worth keeping:** CP-SAT's assumption core returned all five
  constraint families for every infeasible case — useless for diagnosis. The
  soft-constraint route identified the exact broken room pair in 1.27 s *and*
  returns a Plan alongside the complaint. Build on that.

### Honest limits

- **The literature half is largely not done.** The primary-source survey died with
  the session; every claim about MIP, rectangular-dual theory and `kiwisolver` is
  tagged `[UNVERIFIED]` and rests on recollection. The empirical half is sound.
- **Single seed, no variance estimate — not yet quotable in a specification.**
  See *Solver timing variance sweep*.
- **Rooms tile exactly; real walls have thickness.** Whether the formulation
  survives wall bodies is unknown and is the **largest open risk** on this
  architecture. Carried into *Canonical geometry model*.

Full findings: `docs/research/solver-formulation.md`, ending with the nine-item
"what this formulation requires the Proposal to look like" contract that
*What the model proposes* consumes. Its headline: the model must be scored on
**relative arrangement, not box regression**, and must not be trained toward
validity at the cost of plausibility — which makes that ticket's cheap routes
(LLM or retrieval) genuinely sufficient for v1 rather than a stopgap.

Code: `experiments/solver-toy/`.
