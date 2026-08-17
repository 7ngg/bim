---
id: 5
title: Dimensional standards corpus
parent: map
labels: [wayfinder:research]
status: open
assignee:
blocked_by: []
---

# Dimensional standards corpus

## Question

Which reference works give **machine-encodable dimensional standards** for
residential layout, and what numbers do we actually adopt?

C8 sets the posture: Neufert-grade dimensional standards, no legal
code-compliance claim. But Neufert is one book, it is European-leaning, and the
instruction is to *think and adopt*, not copy.

Survey and compare, at minimum:

- **Neufert, *Architects' Data*** — the baseline
- **Metric Handbook: Planning and Design Data** (Littlefield)
- **Time-Saver Standards for Building Types / Housing**
- **DIN 18040** (accessibility), and equivalent accessibility guidance
- **Ramsey/Sleeper, *Architectural Graphic Standards***
- Anything else that materially disagrees with the above

For each, establish what it actually provides and where the numbers conflict:

1. Minimum room areas and minimum clear dimensions, by room type.
2. Door leaf widths and required swing clearances; corridor and passage widths.
3. Furniture and circulation clearances — bed surrounds, kitchen work triangle and
   aisle widths, dining pull-out, bathroom fixture clearances.
4. Window-to-floor-area ratios for habitable rooms; sill and head heights.
5. Ceiling heights; wall thicknesses by construction type (internal partition,
   internal load-bearing, external).
6. Stair geometry — captured for the record even though multi-storey is out of
   scope, because a stair may still appear in a single-storey plan's entry.

Then decide, with reasoning:

- **Where the sources conflict, which number wins and why.** Note that these books
  encode different national conventions; a single blended table may be incoherent.
  Is a *region* parameter needed here as well as in the training data?
- **Copyright posture.** These are copyrighted works. Dimensional facts are facts,
  but tables and diagrams are expression. Establish what may be encoded as
  constraint values and what may not be reproduced.

Deliverable: findings doc, plus a **first-cut constraint table** — room type ×
{min area, min width, min depth, needs window, is wet, is habitable, is private} —
in a form the validator and the solver can both read. That table is the input to
*Acceptance validator spec* and to *Brief schema and parsing contract*.
