---
id: 6
title: Cross-dataset unification
parent: map
labels: [wayfinder:research]
status: open
assignee:
blocked_by: []
---

# Cross-dataset unification

## Question

C12 says combine the corpora. **Can they be combined without making the model
worse everywhere?**

The warning sign is already on the table: a model trained on RPLAN scores 0.909
on RPLAN and **0.592** on ResPlan. Layout convention is regional, and naive
pooling of corpora that encode different conventions plausibly yields a model that
is mediocre on all of them. C9 removes the licence obstacle, so the only question
left is whether combining actually helps.

The candidates and what they are:

| Corpus | Plans | Geometry | Graph | Region |
|---|---|---|---|---|
| Swiss Dwellings | 45,176 apartments | WKT in metres; walls, railings, columns, windows, doors, fixtures; `elevation`+`height` | derivable | European |
| ResPlan | ~17,000 | vector polygons, `wall_depth`, explicit openings, metric | typed, 4 edge classes | South Asian |
| RPLAN | 80,788 | raster only | must be derived | Chinese |
| MSD | 5,372 plans / 18,943 apartments | graph-primary | yes | European, multi-apartment |
| ProcTHOR-10k | 10,000 | synthetic | yes | none |

Establish:

1. **A common schema, or a demonstration that there isn't one.** Room-type
   taxonomies differ; geometry representations differ (WKT metres vs shapely vs
   raster). What is the greatest common denominator, and what is lost converting
   each corpus into it?
2. **Whether RPLAN's raster form can be vectorised** to the same fidelity as the
   others, or whether including it means the common schema drops to raster.
3. **Whether region should be an explicit conditioning variable** on the model
   rather than something pooled away. If yes, that changes what
   *What the model proposes* has to be designed to accept.
4. **Whether the corpora even agree on what a plan is** — Swiss Dwellings has a
   building hierarchy and 2.5D; ResPlan is single flats; MSD is multi-apartment
   complexes. C5 scopes us to single dwellings, so how much of each corpus
   survives filtering?
5. **What each corpus is actually good for**, stated separately: geometry and BIM
   shape, typed adjacency graphs, pre-training scale, synthetic augmentation. A
   split-role answer may beat a merged one.

Deliverable: findings doc plus a **concrete schema proposal** with per-corpus
conversion notes and an honest list of what each conversion destroys.
