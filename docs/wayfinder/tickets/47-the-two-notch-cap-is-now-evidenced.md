---
id: 47
title: The two-notch cap is now evidenced, and more notches is not the fix
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - docs/adr/0003-the-envelope-is-an-inner-face-ring-of-typed-edges.md
  - experiments/rectangularise/
---

# The two-notch cap is now evidenced, and more notches is not the fix

## Question

**ADR 0003 caps the v1 Envelope at a bounding box minus at most two notches and
records the cap as *"unevidenced in both directions"*. It is now evidenced.** The
cap is defensible — it sits at the knee of its own ladder — and the population it
hurts is **not** hurt by the cap. ADR
[0017](../../adr/0017-three-of-the-conversions-fidelity-headlines-are-constraints-restated.md),
failure mode 4.

Envelope loss is the largest single quality term in the conversion, larger than
the rectangle count, the solver budget or the room count:

| envelope loss at k = 2 | dwellings | worst-room IoU | share with a room ≤ 0.5 |
|---|---:|---:|---:|
| < 0.01 | 39.8 % | 0.844 | 10.5 % |
| 0.03–0.06 | 16.6 % | 0.738 | 15.3 % |
| 0.10–0.20 | 8.0 % | 0.483 | **53.5 %** |
| ≥ 0.20 | 1.9 % | 0.293 | **77.8 %** |

**And the obvious response is wrong.** The corpus-wide ladder, median over 2,317
converted dwellings, with the marginal gain of each extra notch:

| notches | median loss | marginal |
|---:|---:|---:|
| 0 | 0.1610 | — |
| 1 | 0.0503 | −0.1107 |
| **2** | **0.0178** | **−0.0325** |
| 3 | 0.0114 | −0.0064 |
| 4 | 0.0096 | −0.0018 |

**Two is already the knee.** A third notch buys 0.6 percentage points of median
loss and a fourth buys 0.2. And on the 230 dwellings the cap supposedly hurts
most — those above 0.10 loss at k = 2 — raising the cap to four moves the median
only 0.136 → 0.105, and **56 % are still above 0.10 and 89 % still above 0.05**.
Their outlines are not bounding-box-minus-notches at *any* notch count: they are
chamfered, curved, or stepped more times than a rectilinear ring of typed edges
can express.

⚠️ **And a higher cap is measured to make the conversion worse.** The k ≤ 2
ablation (`out/ablate_k2.log`) has an *"up to 4 notches"* arm: it converts
**88.0 %** against the shipped **93.2 %**, 25 INFEASIBLE against 13. A tighter
Envelope leaves the rectangles less slack to satisfy the hard adjacency and area
constraints inside it. Raising the cap trades a fifth of the conversion yield for
moving 9 % of dwellings below 0.05 loss (26.6 % → 17.3 % above it).

**What has to be decided, then, is not the number.** It is what v1 does about the
dwellings whose *outline shape family* it cannot express — which is a different
question from how many notches it allows, and the one this evidence actually
raises:

1. **Nothing — the cap stands and the loss is the price.** Defensible on this
   evidence, and it is the cheapest answer, which is exactly why it needs
   arguing rather than assuming. It means roughly 10 % of the training corpus
   carries an Envelope that is visibly not the dwelling's own outline, and the
   Proposer learns from it.
2. **Refuse them.** An envelope-loss gate in the reject rule, thinning the corpus
   further on top of the 9.5 % already refused, and buying a corpus whose every
   Envelope is faithful.
3. **Widen the shape family rather than the count** — chamfered edges, or a
   general rectilinear ring with a vertex budget instead of a notch budget. This
   is the one that reaches production-plan territory and the one that costs
   most: ADR 0003's edges are **typed**, a notch is *"a garden in one case and a
   neighbour in the other"*, and any new edge kind has to be nameable to a
   Homeowner, drawable, dimensionable, and expressible in the IFC (ADR 0011).

**Whatever is decided, ADR 0003 must stop saying "unevidenced".** The ladder,
the ablation arm and the tail measurement above are the evidence; a reader who
takes the ADR at its word today will re-derive all three.

**Also owed:** ticket 15's solver timings were measured against a two-notch
Envelope, so any cap change re-prices them. That is a reason to decide before
the timings are quoted again, not a reason to leave the cap alone.
