---
id: 14
title: Which region profiles ship in v1
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
---

# Which region profiles ship in v1

## Question

Two closed research tickets independently concluded that **region cannot be
averaged away** — and neither was allowed to decide which region we actually ship.
That decision is this ticket.

What forced it:

- *Dimensional standards corpus* — the constraint table splits into a shared
  ergonomic layer and **regional profiles of ~30 numbers each**, and every cell
  additionally needs a tier (`statutory_floor` / `market_default` / `accessible`),
  because England alone yields five different minimum bedroom areas. It also found
  that minimum areas are **not comparable across regions even after unit
  conversion**, because measurement conventions differ.
- *Cross-dataset unification* — the model must be conditioned on the triple
  `(region, corpus, annotation_provenance)`, and the corpus mix is Swiss Dwellings
  (European) plus ResPlan (South Asian).

C12 says "not tied to any region". That was a statement of freedom, not a
requirement to serve everywhere at once — and both research passes say serving
everywhere at once produces something coherent nowhere.

Decide:

1. **Which profile or profiles ship in v1.** The candidates are not equal:
   - **UK** — the only profile checkable end to end, because Approved Documents
     and the NDSS are Open Government Licence v3.0 and freely republishable. The
     research recommends the test suite assert against it for that reason.
   - **Germany / DACH** — matches Swiss Dwellings, the primary corpus, and matches
     Neufert's origin. Best *data* alignment.
   - **South Asia** — matches ResPlan.
   - Note the tension: the best-verifiable standards profile and the
     best-aligned training corpus are **different regions**. Resolve it explicitly
     rather than letting it resolve itself.
2. **Whether the standards profile and the corpus conditioning tag must agree.**
   Can we ship UK standards over a Swiss-Dwellings-trained proposer? The proposer
   only supplies topology and proportion, and the solver enforces the numbers — so
   maybe yes. Argue it; do not assume it.
3. **Which tier is the default** the Homeowner gets when they say nothing.
   `market_default` is the obvious answer and the obvious answer may be wrong,
   because a plan that silently fails `statutory_floor` is worse than one that
   admits it.
4. **What "region" means in the Brief.** A field the Homeowner sets, inferred from
   locale, or fixed for v1? If it is a field, it changes the Brief schema.
5. **What a second region costs later** — is adding one a data file, or a retrain?
   The answer decides whether shipping one region is a narrowing or a trap.

Feeds *Acceptance validator spec*, *Brief schema and parsing contract*, and
*What the model proposes*. Worth resolving before any of them.
