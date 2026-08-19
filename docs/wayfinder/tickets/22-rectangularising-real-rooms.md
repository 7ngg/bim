---
id: 22
title: Rectangularising real rooms
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: []
---

# Rectangularising real rooms

## Question

**Every stage of this system places one rectangle per room, and roughly 40 % of
real rooms are not rectangles. How does a real room become a rectangle, and what
does the conversion cost?**

Unowned until now. *Proposer architecture survey* §7.4 flagged it as "the
L-shaped-room question" and assigned it to *Canonical geometry model* and *Solver
formulation for layout projection* — **both closed without settling it**. It is
not a preprocessing detail: it sits under the Proposal contract (one box per
Room), under the solver's tiling, under both Proposer sources, and under *Fit the
ENGINE_CHOICE acceptance thresholds to the corpora*, which cannot fit a threshold
to a corpus it cannot read as rectangles.

**What is known.** ResPlan reports **43.2 % of room polygons exactly rectangular,
62.3 % at a 2 % tolerance** — verified in *Acquire the datasets*, not taken from
the paper. Graph2Plan reports **"over 93 % of the rooms in RPLAN can be
represented as the intersection between their respective bounding boxes and the
building boundary"**. Those measure different things and are not in conflict; the
gap between them is this ticket.

**What has to be decided:**

1. **The conversion itself.** Bounding box; largest inscribed axis-aligned
   rectangle; bounding box ∩ envelope, per Graph2Plan; or split a concave room
   into two rectangles and lose the one-box-per-Room contract. State which, and
   what happens to the room's *area* under it — a bounding box inflates area, an
   inscribed rectangle deflates it, and per-room target-area conditioning consumes
   whichever number this produces.
2. **Measure the loss on Swiss Dwellings**, which nobody has done — ResPlan's
   43.2 % is a different corpus. Per-room IoU, area error, and the fraction of
   dwellings where rectangularised rooms no longer tile.
3. **What it does to adjacency.** Two rooms that touch as polygons may not touch
   as rectangles, and the reverse. Adjacency is what the arrangement metric and
   the solver's contact graph are built on, so a conversion that scrambles it is
   worse than one that loses area.
4. **The reject rule.** Some dwellings will not survive at any tolerance. State
   the threshold above which a corpus dwelling is dropped from training and from
   the retrieval index, and how many that costs.

**Deliverable.** A stated conversion with measured loss on Swiss Dwellings and
ResPlan, checked into `experiments/`, plus the drop count each corpus pays. Feeds
*The retrieval index and warp procedure*, the training pipeline in
`docs/spec/proposer.md` §4, and *Fit the ENGINE_CHOICE acceptance thresholds*.

**Not this ticket.** Whether v1 ever *emits* a non-rectangular room. That is the
map's **Non-orthogonal geometry** fog and stays there.
