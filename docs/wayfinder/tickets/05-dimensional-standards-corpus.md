---
id: 5
title: Dimensional standards corpus
parent: map
labels: [wayfinder:research]
status: closed
assignee: wayfinder-research-agent
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

## Resolution

**A `region` parameter is required — but only on half the table — and region alone
is not enough: every cell also needs a tier.**

Deliverable shipped at `data/standards/room-constraints.json` (canonical; the
prose table in the findings doc is a copy).

Findings that bind other tickets:

- **Split the table in two.** Body-derived clearances are invariant across
  regions; convention-derived numbers are not. Ergonomic layer shared, regional
  profiles ~30 numbers each.
- **Tiers are mandatory.** England alone yields *five* different minimum bedroom
  areas (7.5 / 8.5 / 11.5 / 12.5 / 13.5 m²) depending on the instrument invoked.
  Intra-national spread is as wide as international. Every cell carries
  `statutory_floor` / `market_default` / `accessible`.
- **Neufert issues no prescriptive minimum room areas at all**, and neither does
  German building law. Our default areas are *our* choices derived from
  clearances, not quoted minima — they must be marked as such.
- **C6 item 4 ("gets a window") is a method conflict, not a number conflict.**
  England has no daylight requirement; Germany uses a 1/8 area fraction; Japan a
  site-geometry factor; the Metric Handbook a daylight-factor formula. Not
  interconvertible. **The rule must be defined by us as topology.**
- **Minimum areas are not comparable across regions even after unit conversion** —
  measurement conventions differ (German Wohnfläche counts 1.00–2.00 m headroom at
  50%, balconies at 25–50%; UK GIA is binary). A minimum-area value without its
  measurement convention is meaningless.
- **The kitchen work triangle is not Neufert.** Metric Handbook / US origin.
- **Door widths propagate into masonry** — DIN 18040-2's 800 mm clear forces an
  860 mm leaf; the R level's 900 mm forces 985 mm, which moves the structural
  opening onto the 125 mm octametric grid. Doors are a layout constraint, not a
  schedule.
- **Copyright:** numbers are safe, tables and diagrams are not, and the
  incorporated-into-law safe harbour does not reach Neufert or the Metric
  Handbook. Prefer freely-published regulatory sources; re-derive, never transcribe.
- **The verification-grade corpus is free.** UK Approved Documents and the NDSS
  are OGL v3.0. Japanese law is on e-Gov; Bavarian and Saxon law are
  machine-readable.

Full findings: `docs/research/dimensional-standards.md`. Every number carries a
VERIFIED / REPORTED / DERIVED / ENGINE_CHOICE label.
