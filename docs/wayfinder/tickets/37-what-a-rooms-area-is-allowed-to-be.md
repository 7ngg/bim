---
id: 37
title: What a room's area is allowed to be
parent: map
labels: [wayfinder:research]
status: closed
assignee: tng
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

---

## Resolution

**A maximum is enforceable, it is free in the solver, and the anchor is the
Room's own `target_area` — which is the same rule as an absolute per-type band,
by identity, for every Room a Homeowner does not size by hand.** Findings:
`docs/research/room-area-bands.md`. Harness: `experiments/room-area-bands/`.
Nothing in `rules.json`, `room-constraints.json` or `docs/spec/` was edited; the
ticket declared itself read-only on those and is.

### The three decisions asked for

**Anchor — `target_area`, and the fraction anchor is refuted.** `brief.md` §9.2
sets a silent Room's target from `market_default` → corpus median → absent, all
per-type constants, so anchoring to the target and anchoring to the type
absolutely coincide except where the Homeowner states a number — and there the
statement must win. A **fraction of the dwelling** is the *loosest* anchor tested,
on 7 of 9 Swiss classes and 4 of 5 ResPlan classes, because a room's share must
fall as the room count rises and a fractional band is fitted across a trend it
cannot see. A fourth anchor was added and beaten on a non-numeric ground: a band
of `k × total/n` is tighter still, but it makes every room's maximum a function of
how many *other* rooms there are, so adding a study silently shrinks the maximum
living room.

**Severity and site — hard, `both`, and the solver side costs nothing.** H4
already builds `a = w·h` through `AddMultiplicationEquality` to post the
*minimum*. A maximum is a domain bound on a variable that already exists, and an
upper bound on a product *tightens* propagation on `w` and `h` rather than
weakening it. There is no reason to make this validator-only. Threshold at the
corpus **p99.5**: p95 rejects **26.6 %** of real dwellings, p99 **6.0 %**, p99.5
**3.1 %** — and the corpus is the retrieval and training population, so a
rejection there is coverage lost.

**Where slack is directed — measured, and it needs no Brief field.** A Swiss
bedroom **does not grow with the dwelling at all**: per-room slope 0.0020,
r² **0.000**, so 40 m² more dwelling buys it **0.08 m²**. Nor does a WC (0.08), a
bathroom (0.43) or a storeroom (0.55). The absorbers are the **living room**
(+7.99 m² per 40 m²) and then **circulation** (+4.00). Rank the classes by area
dispersion and the ordering *is* the absorber ordering, so the direction falls out
as a **soft weight per type** taken from the corpus rather than from a nominated
absorber the Homeowner would have to choose.

### The recommendation handed to `rules.json`'s holder

1. **`dim.max_area`**, hard, site `both`: `k[type] × target_area`, falling back to
   `absolute_cap[type]` where no target exists. `k` runs **2.02–8.15** and is
   **not one constant** — the habitable types `AZ` sizes cluster at 2.0–2.6 and
   every outlier is a type `AZ` ships as `market_default: None`.
2. **`dim.market_default_area` becomes two-sided.** It is soft and prefers Spaces
   *at or above* market default, so the objective **actively rewards bloat**. A
   maximum alone leaves the incentive in place and relocates the bloat to just
   under the cap. Replace the reward with `soft_w[type] × |area − target|`.
3. **`dim.stated_target_implausible`**, warn, when a *stated* target exceeds the
   absolute cap — Homeowner stays sovereign, an LLM decimal slip still gets caught.
4. **`brief.md` §9.4's pre-check gains its upper bound.** It is "two bounds, two
   severities, one function" and both are currently lower.

### Three things that bite, and one is a defect in a committed artifact

⚠️ **The first WC cap was circular, and correcting it moved the number 2.2×.** The
cap came back as **2.40 m² at p95, p99, p99.5 *and* p99.9** — because the class
`wc` *is* `BATHROOM < 2.4`, so every percentile returns the splitter. Re-measured
against Swiss Dwellings' **fixture** ground truth (toilet, no bath or shower;
13,436 rooms), a real WC's p99 is **5.29 m²**, p99.5 **6.20**, and one is
**18.23 m²**. **19.3 % of real WCs sit at or above the splitter and are invisible
to it.** The fixture median, **1.85 m²**, reconciles exactly with
`ergonomic.corpus_label_split`. **ResPlan cannot be corrected** — no fixtures — so
every ResPlan `wc` figure here is reported unusable rather than quoted.

⚠️ **A hard maximum can make a Brief impossible, and it happens at four rooms.**
`model.no_unassigned_area` is exact and a given Envelope fixes Σ Space area before
the solve. At p99 caps the commonest 4-room mix sums to **77.9 m²** against a
corpus p99 of **79.7** — it cannot express the largest 1 % of real 4-room
dwellings. p99.5 clears it (85.7). Four rooms is the **bottom of C13's band**, and
*Ergonomic minima* already found the 250 mm grid charging the **5-room** case; the
small-dwelling end keeps taking hits from independent directions. The failure mode
is **not** solver INFEASIBLE — H3 is soft at weight 100,000, so it surfaces as
zero survivors, which is what §9.4's pre-check exists to explain.

⚠️ **`fit_rects.py` mislabels 1.23 % of fitted dwellings.** Line 727 takes
`[t for t, _ in dw[k]][:n]` — the *unfiltered* head — while `load_swiss_geoms`
has already dropped sub-`MIN_ROOM_AREA` polygons, so where a dropped polygon is
not last every later label is off by one. **22 of 1,787.** Any per-type reading
off `swiss_fit.json` inherits it. Handed to *Look at the converted corpus*.

### The ticket's own instruction, answered against it

It asked for distributions on the **converted** geometry rather than raw polygons.
For *area* that points the wrong way, and the reason is the plane: the shipped
conversion rasterises by **watershed**, so a fitted rectangle is a **centreline**
area while ADR 0010 makes every published area a **finished-face** one. The gap is
not a constant — **1.17× for `living_dining`, 1.58× for `wc`** — because a small
room's share of its surrounding walls is a larger share of its own floor, so **no
single scalar converts between the planes**. Deflating by the dwelling ratio shows
the rectangularisation *shape* change is negligible for the large classes
(`room*` p95 21.97 → 21.71). The band is measured on the corpus polygon and
stated as a finished-face area, carrying `dim.min_area`'s existing caution that
the corpus's own face convention is unrecorded and can never be recovered.

### Also delivered, because `brief.md` owed them here

**Corpus medians for the silent `AZ` types** — `wc` **1.85 m²** (fixture).
`kitchen_niche` and `wardrobe_1room_entry` have **no corpus type at all**, so
rung 2 of the ladder is empty and they fall through to absent. ⚠️ **`hall` is not
supplied**: the ergonomic layer carries `hall`, `entrance_lobby` and `corridor` as
three types, Swiss carries one label and ResPlan none, so the 7.58 m² measured is
all three merged and is offered with its limit attached rather than as a default.

**Bedroom count → total area**, the joint distribution `brief.md` §7 owes. Swiss
p50 by count: 1 → **56.3**, 2 → **76.5**, 3 → **90.8**, 4 → **94.7** m².
⚠️ ResPlan disagrees by ~40 % at three bedrooms (128.8) and the cause is
labelling, not market — it has four room types and no circulation at all.
⚠️ And `room*` is **not** "bedrooms": 78 % of the Swiss class is the generic
`ROOM` label.

### Boundaries held

Wrote no `rules.json`. Did not re-derive the ergonomic floor. Built no
corpus-to-ergonomic vocabulary mapping — that is *Two room vocabularies in one
file*'s, and only the two already-decided rules (`{ROOM, BEDROOM, STUDIO}`
collapse, the 2.4 m² bathroom split) were applied. Did not touch envelope sizing,
which is the map's **Variant generation and ranking** patch.
