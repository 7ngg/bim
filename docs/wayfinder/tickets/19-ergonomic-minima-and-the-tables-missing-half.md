---
id: 19
title: Ergonomic minima and the constraint table's missing half
parent: map
labels: [wayfinder:research]
status: open
assignee:
blocked_by: []
---

# Ergonomic minima and the constraint table's missing half

## Question

**`data/standards/room-constraints.json` is a stub, and *Acceptance validator
spec* has just made its missing half the entire hard rule set.**

*Dimensional standards corpus* records the table as shipped. It is not. The file
is 9 KB and ends:

```json
"PLACEHOLDER_NOTE": "DE and US sources, the ergonomic layer, and the room table are appended below in the completed file."
```

Present: UK sources, `region_model`, `tier_model`, `flag_semantics`,
`value_format`. **Absent: the ergonomic layer, the room table, and the DE and US
sources.** The room table exists only as prose in `docs/research/dimensional-standards.md`
§8, and only for the `DE` / `market_default` column.

This is not a transcription job. *Acceptance validator spec* changed what the
missing layer has to be:

- The validator's hard floor is no longer `statutory_floor` — that tier is `null`
  for the default region, so it yields an **empty hard set**. It is the
  **ergonomic minimum**: the smallest clear rectangle a room's required fixtures
  and their body clearances occupy.
- The hard rule set therefore **carries no region**. This layer is the only thing
  standing between a Plan and rejection, in every region, including ones never
  surveyed.
- Three registry rules — `dim.min_area`, `dim.min_clear_width`,
  `dim.min_clear_depth` — are `conf: pending` until it lands. Their structure is
  final. Only the values are missing.

Settle:

- **Derive, do not quote.** Per §7 of the findings, numbers are facts and tables
  are expression. Each ergonomic minimum must be *composed* from fixture
  footprints plus stated body clearances, with the arithmetic shown, so its
  provenance is a derivation rather than a transcription. §5.3 already carries
  much of the clearance material.
- **Width and depth are directional for `bathroom` and `wc` and not for the
  rest** (§8). Establish whether that survives derivation, or whether more room
  types turn out directional once fixtures drive the rectangle.
- **The ergonomic minimum for rooms with no fixtures** — `living`, `dining`,
  `study`, `hall`, `storage`. Furniture is not a fixture and is still fog on the
  map. Decide what the floor is for a room whose function is not a plumbed object,
  and mark it honestly.
- **`de_baybo` is a dangling source key** — `win.area_ratio` in
  `data/acceptance/rules.json` cites it, and the DE sources block does not exist.
- Complete the room table as data for all defined regions, and finish or
  explicitly re-stub the US profile (findings §10 gap 1: US light-frame wall
  thicknesses are the largest geometric divergence in the corpus and were never
  written up).

Cross-check every value against `data/acceptance/rules.json`: the registry is the
consumer, and any minimum it cannot read is a rule that silently does not fire.

Deliverable: the completed `data/standards/room-constraints.json` with an
`ergonomic` layer, each value carrying `v` / `src` / `ref` / `conf` / `note` per
the file's own `value_format`, and the three `pending` registry rules flipped to
real numbers.
