---
id: 21
title: The room-count envelope v1 promises
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: [8]
writes:
  - CONTEXT.md
---

# The room-count envelope v1 promises

## Question

**How many rooms does v1 claim to handle, and what happens at the edges of that
claim?**

*Acquire the datasets* measured the corpora and the result reframes a number this
map has treated as settled. Across **63,800 real dwellings** in both committed
corpora, counting the rooms a Brief actually names:

| rooms | 4–10 | ≥12 | ≥14 | ≥16 | ≥20 | ≥24 |
|---|---:|---:|---:|---:|---:|---:|
| dwellings | ~60,600 | 916 | 178 | 66 | 11 | 1 |

The **24-room case that the solver formulation was validated against — and that
every timing on this map quotes — describes exactly one dwelling in 63,800.**
Meanwhile ~95% of the corpus sits between 4 and 10 rooms, and the mean is 6.8.

C5 already commits the product to stating its limits honestly: single storey, and
house layouts from apartment priors. This asks whether there is a **third stated
limit** and where it sits.

**What has to be decided:**

1. **Is 24 rooms a v1 requirement at all**, or an artefact of a stress test that
   became a spec figure? The solver clears it in 6.25 s — at 100% exterior
   exposure, which *Acquire the datasets* showed no real flat has — so the
   capability is real but it may be answering a question nobody asks.
2. **Where the supported band starts and stops.** A floor as well as a ceiling: a
   1-room Brief is 948 dwellings in the corpus and probably not a product.
3. **What the system does past the ceiling.** Refuse, warn, or attempt and let the
   Acceptance bar reject? *Acceptance validator spec* settled that a failing Plan
   is never shown and a zero-survivor case is diagnosed arithmetically — this is
   the same shape of decision one level earlier, at Brief-parse time, and *Brief
   schema and parsing contract* already owns a feasibility pre-check that could
   carry it.
4. **What the product copy says**, in the same breath as the other two limits.

**Why this waits on *What the model proposes, and how it is trained*.** If that
ticket takes retrieval-and-warp, the ceiling is not a choice — it is whatever the
corpus holds, and the numbers above *are* the answer. If it trains with a
synthetic generator, the ceiling becomes a design parameter and this question is
about what to aim the generator at. The route determines whether this is a
statement of fact or a decision.

**What this is not.** Not a re-litigation of C5 or of the solver formulation. The
solver's capability is measured and stands; this is about what v1 *promises*,
which is a different thing from what the engine *can do*.
