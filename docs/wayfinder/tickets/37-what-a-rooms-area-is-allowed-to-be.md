---
id: 37
title: What a room's area is allowed to be
parent: map
labels: [wayfinder:research]
status: open
assignee:
blocked_by: []
writes:
  - docs/research/ (new findings doc)
  - experiments/room-area-bands/ (new)
---

# What a room's area is allowed to be

## Question

**A 40 m² WC passes all 38 acceptance rules, and the surplus that creates it is
compulsory.**

Every area predicate in `data/acceptance/rules.json` is a lower bound or a total:

| rule | direction |
|---|---|
| `dim.min_area` | hard **floor**, per room |
| `dim.market_default_area` | soft, "prefer at or **above**" — rewards bigger |
| `circ.fraction_hard` ≤ 30 % | the only per-class **upper** bound, circulation only |
| `area.invented_envelope_hard` ±5 % | the **total**, not any room |

No non-circulation Space has a maximum area. And `model.no_unassigned_area`
requires the union of Spaces and Wall bodies to equal the Envelope interior
*exactly*, so when Σ Room target areas falls short of the interior minus
partitions the difference **must** be assigned to some Space. The solver
objective — L1 corner displacement plus soft exact tiling — expresses no
preference about which, so it lands wherever displacement is cheapest.

Worked: a **5.8 × 6.9 m WC** clears `dim.min_area` (≥ 0.8 m²), clears
`dim.aspect_ratio_hard` (1.19 ≤ 3.0), and cannot trip `dim.market_default_area`
at all because `profiles.AZ.rooms.areas_m2.wc.market_default` is `None`. It
passes the bar and would be shown to a Homeowner.

Reported from production experience on the predecessor: *"some rooms got too
small, others too big — sometimes the WC got to 40 m²."* This is that defect,
still present, in the successor's spec.

## What to measure

Both corpora are on disk and hash-verified; loaders are in
`experiments/corpus-smoke/`, and *Rectangularising real rooms* has already
converted dwellings to typed rectangles. Everything below is a read over data
that exists.

1. **Per-room-type area distribution** — p5 / p25 / p50 / p75 / p95 and CV, per
   type, per corpus, on the **converted** (rectangularised) geometry, not the raw
   polygons. Report Swiss Dwellings and ResPlan separately; do not pool
   (*Cross-dataset unification*).
2. **Area as a fraction of dwelling total**, same breakdown. A band anchored to an
   absolute number cannot serve both a 45 m² flat and a 200 m² house; a band
   anchored to a fraction, or to the Brief's own target, can. Decide which
   anchor the data supports.
3. **Which room types carry the variance.** Rank types by within-dwelling area
   dispersion after controlling for dwelling size. This is the question that
   decides the *absorber*: if real dwellings put their slack in circulation, then
   `circ.fraction_hard`'s 30 % already is the mechanism and the fix is to direct
   slack there deliberately. If real dwellings put it in living rooms, the
   absorber is a habitable Room and the design is different.
4. **The silent-profile fallback.** `AZ` ships `market_default: None` for `wc`,
   `hall`, `kitchen_niche` and `wardrobe_1room_entry`. *Brief schema and parsing
   contract* specifies the ladder as `market_default` → **corpus median** → absent;
   this supplies the medians. `ergonomic.corpus_label_split` already carries two of
   them (wc 1.85 m², bathroom 4.17 m²) — reconcile with, do not re-derive.

## What to decide from it

- **The band's form and anchor**: `[lo, hi]` against the Room's own Brief target,
  against the room type absolutely, or against a fraction of the dwelling. State
  which the data supports and why the other two do not.
- **The band's severity and enforcement site.** A hard `dim.max_area` rejects
  candidates late; the solver can post an upper bound cheaply, so `both` is
  available in a way it is not for the Opening rules. Price both.
- **Where slack is directed** when Σ target < available interior, and whether that
  needs a Brief field (a nominated absorber) or is a pure engine choice.

## Boundaries

- **Does not write `rules.json`.** The predicate and thresholds are handed to
  whoever holds that file — currently claimed by *Opening placement rules*, *Fit
  the ENGINE_CHOICE acceptance thresholds to the corpora* and *H8 and the
  single-aspect flat*. This ticket produces the measurement and the recommended
  rule text.
- **Does not re-derive the ergonomic floor.** *Ergonomic minima and the constraint
  table's missing half* owns the lower bound and it is settled. This is about the
  upper one, which nothing owns.
- **Not the envelope-sizing question.** How an *invented* Envelope is sized against
  `target_area` given a ~5.7 % partition footprint (*One internal thickness*) is the
  map's **Variant generation and ranking** fog patch. This ticket bounds the rooms;
  that one bounds the box. Both are needed and they are separate.

## Why this is research and not a grilling

Nothing here is a preference. The question is what real dwellings do, the data to
answer it is committed, and inventing a band by judgement is exactly the move
CLAUDE.md forbids and the move that produced the 40 m² WC in the first place.
