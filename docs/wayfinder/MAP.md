---
id: map
title: bim-engine — prompt to dimensioned floor plan
labels: [wayfinder:map]
status: open
tracker: local-markdown
---

# bim-engine — prompt to dimensioned floor plan

## Destination

A written spec plus locked architecture decisions for **bim-engine v1**: a system
that takes a natural-language brief from a Homeowner and produces a **single-storey
flat or house plan** with real walls, hosted openings, dimension chains and room
tags — passing an acceptance validator, exported as **dimensioned DXF and valid
IFC**. Built clean, from scratch.

The map is done when someone could staff the build from it. It produces
decisions, not code.

## Notes

**Skills every session should consult:** `grilling` and `domain-modeling` by
default. `research` for `wayfinder:research` tickets. `prototype` for
`wayfinder:prototype` tickets.

**Domain vocabulary** (see `CONTEXT.md` — which now also carries the geometry
terms and, critically, the **clear versus centreline** distinction that every
dimension in this system has to declare):

- **Homeowner** — describes needs in prose, cannot draw a boundary, cannot read a
  dimension string. Judges by "would I live here". Tolerates 90%-right. **The v1
  buyer.**
- **Practitioner** — architect/designer. Judges by "does this open in Revit and
  stay workable". 90%-right is worse than blank. **Not the v1 buyer, but the
  standard the engine is held to.**

**Standing constraints, settled while charting** — every session inherits these:

| # | Constraint |
|---|---|
| C1 | Destination is a **spec + decisions**, not a prototype and not a build. |
| C2 | **Homeowner is the v1 user**; the internal geometry model is built to Practitioner grade from day one. Homeowner just never sees that layer. |
| C3 | Hard output floor: **dimensioned 2D vector plan** — walls with thickness, doors, windows, room tags, dimension strings — to DXF/PDF. IFC/BIM is the stated export path. |
| C4 | Input is **prompt → LLM-parsed structured brief**, with gaps filled from standards and every assumption surfaced to the user. The brief stays editable; it is the real interface. |
| C5 | **Single-dwelling residential, single storey.** Flats and houses — *confirmed, and both ship through one code path*: dwelling type is a preset over the Envelope's edge ring, not a branch. Product copy states two limits, not one: **single storey only**, and **house layouts come from apartment priors** because every corpus is flats. See *Building scope and envelope handling*. |
| C6 | Acceptance bar (7 items) is a **hard filter**: generate many, reject most, show survivors. See *Acceptance validator spec*. **On solver expiry**, a candidate whose best objective is ≥ `soft_weight` has unassigned floor and is **not a survivor** — discard it, never show it (*Solver timing variance sweep*). |
| C7 | Post-generation, v1 is **edit-the-brief-and-regenerate**. Direct wall manipulation with re-solve is designed-for but deferred. |
| C15 | **The standards table carries two arithmetic constraints.** ADR 0004: every wall thickness even. ADR 0007: every published minimum satisfies `min + t_int ≡ 0 (mod grid)`, because ADR 0001's clear reading otherwise costs a whole grid unit per room per axis and **provably deletes 4-, 5- and 6-room dwellings**. Both are ship gates on a region profile. |
| C8 | **Neufert-grade dimensional standards. No legal code-compliance claim, ever.** Say so in the product copy. *Neufert now names the grade, not the source* — *Which region profiles ship in v1* found that building a profile out of it is the one copyright move the research forbids, and the shipping profile draws on freely-published regulatory text instead. |
| C9 | **Non-commercial project.** Research-only datasets and weights are available. Licence is not a gate; data quality and regional convention are. |
| C10 | **Model proposes, solver projects** — *amended, and the amendment is load-bearing.* The Proposal must carry **relative arrangement, not just boxes** (pairwise separations promoted to hard linear constraints), and exact tiling must be posted **soft, not hard**. The loose form — hand the solver boxes and let it project them — is **refuted by measurement**: it finds nothing at 24 rooms in 30 s. Amended, 6.25 s. A **two-phase fallback for infeasible Proposals is mandatory** — and *Solver timing variance sweep* moved this from prudence to operational necessity: `fix_relations` posts the Proposal's relations as **hard constraints**, so a merely **noisy** Proposal goes INFEASIBLE (5 of 5 seeds at 24 rooms at σ = 1.0 m, against σ = 0.5 m in every published run). The formulation doc's boxed claim that the Proposal *cannot* make the model infeasible is **false as written**. Shipped parameters: **time limit 15 s, τ = 4**. See *Solver formulation for layout projection*. **And "the model" is two things**: v1's Proposer has two sources — retrieval-and-warp and a trained transformer — behind one Proposal contract, with the Acceptance bar arbitrating. The split it names is proposal-versus-projection, not one generator versus another. See *What the model proposes, and how it is trained* and ADR 0005. |
| C11 | **Clean successor to `../plan-generator-3000-pro-max`.** No code inherited. Its findings may be reused only after independent verification. |
| C12 | Not tied to any region. Combine corpora where it can be made to work. *Amended: that was freedom, not a requirement to serve everywhere.* v1 ships **exactly one** region profile and it is **`AZ`**; `UK` is retained as a test fixture and is never selectable. See C14. |
| C13 | **v1's Proposer serves 4–10 Brief-named rooms.** 92% of the corpus. Set by *What the model proposes*, which measured retrieval dying at 11+ (67.7% blank). What the *product* promises is *The room-count envelope v1 promises*; this is what the Proposer covers. |
| C14 | **A region profile is a construction system plus a drawing convention, and it never rejects a Plan.** It owns the thickness catalogue, decimal separator, room-name abbreviations, opening catalogue keys, two soft area targets and one soft window fraction; every hard dimensional floor is the region-invariant ergonomic minimum. **`RegionProfile` and `CorpusProvenance` are two fields**, holding `AZ` and `CH`, and their disagreement is the normal case — v1 draws **Swiss-shaped layouts to Azerbaijani conventions, permanently**, and says so. See *Which region profiles ship in v1* and ADR 0006. |

**Evidence that shaped the map** — read before re-litigating C10:

- `docs/research/floorplan-generation-stack.md` — model/dataset/licence survey.
  Headline: **zero of ~20 published generators (2020–2026) emit walls with
  thickness.** You are shopping for a room-topology proposer, not a floor-plan
  engine.
- `docs/research/competitive-landscape.md` — eleven products, $0–$20k/yr, all
  stop at schematic design; **none documents a dimensioning or annotation
  system.** That gap is C3.
- `../plan-generator-3000-pro-max/docs/phase2_findings.md` and
  `phase3_findings.md` — measured on this project's own hardware: HouseDiffusion
  degrades near-linearly outside its 5–8 room regime (8 rooms 5.8–12.8% overlap,
  24 rooms 35.8–66.8%), and repair recovers 31% / 7% / **0%** of it. *"Repair
  works, and it is not enough."* Treat as strong prior, re-verify per C11.

## Decisions so far

<!-- one line per closed ticket -->

- [BIM and CAD export stack](tickets/03-bim-and-cad-export-stack.md) — **C3 is
  buildable.** `ezdxf` authors genuine DXF `DIMENSION` entities (verified by
  execution) and `ifcopenshell` authors clean IFC4; the industry-wide annotation
  gap is a product choice, not a tooling limit. Watch `DIMLFAC=100.0`, the R2000
  floor, and mandatory `ObjectPlacement`. ⚠️ Its line that *Revit's IFC import is the
  weak link* cites a **§4 that was never written** — sections 4 (Revit import) and 5
  (`hypar-io/Elements`) are both absent from the findings doc. Treat as an open
  question, not a finding. The Elements half is closed by *Language and runtime
  split*; the Revit half is not.
- [Dimensional standards corpus](tickets/05-dimensional-standards-corpus.md) — a
  **`region` parameter is required on the convention-derived half of the table,
  and every cell also needs a tier**; England alone yields five different minimum
  bedroom areas. Neufert prescribes no minimum room areas at all, so our defaults
  are our own choices. ⚠️ Its line that the table is *shipped at*
  `data/standards/room-constraints.json` is **false** — that file is a 9 KB stub
  ending in a `PLACEHOLDER_NOTE`, carrying the region/tier/flag models and UK
  sources but **no ergonomic layer, no room table, and no DE or US sources**. The
  table exists only as prose in the findings doc §8, `DE`/`market_default` column
  only. Found by *Acceptance validator spec*, which then made the missing
  ergonomic layer its entire hard rule set. Ticketed. **Superseded in part:**
  *Which region profiles ship in v1* **deleted `DE` and `US`**, so the DE room
  table is no longer the thing owed — what is owed is the `AZ` profile plus the
  shared ergonomic layer, and this ticket's `must_match` and `default_region: DE`
  are struck. Its verification-region reasoning survives intact and is what the
  successor built on.
- [Solver formulation for layout projection](tickets/04-solver-formulation-for-layout-projection.md)
  — **GO on C10, amended.** CP-SAT over a 250 mm integer grid, with pairwise
  separations from the Proposal promoted to hard linear constraints and exact
  tiling posted soft. 24 rooms in **6.25 s VALID**; the unamended form finds
  nothing in 30 s. Circulation *is* a constraint (single-commodity flow; private
  rooms receive but never forward), forbidden adjacency is required with the sign
  flipped, objective is L1 corner displacement. Two-phase fallback mandatory.
  Its "largest open risk" — rooms tile exactly, real walls have thickness — is
  **retired** by *Canonical geometry model*, below.
- [Cross-dataset unification](tickets/06-cross-dataset-unification.md) — **do not
  pool.** Swiss Dwellings is the backbone, ResPlan merges under a conditioning
  tag, RPLAN is demoted to optional pre-training, MSD and ProcTHOR are out.
  Condition on `(region, corpus, annotation_provenance)`. **ResPlan's real data
  contradicts its own paper on two material points** — every `[DOC]` claim is
  provisional until the corpora are opened.
- [Canonical geometry model](tickets/01-canonical-geometry-model.md) — **walls with
  thickness survive the solver.** The solver tiles a **solve domain** — the interior
  clear region dilated outward by `t_int/2` — so every tiling edge is a wall
  centreline and `clear rect = erode(solved rect, t_int/2)` holds uniformly, with no
  perimeter special case. Same variables, same constraints; **only constants move**,
  and only the area product needs re-measuring. A `Wall` is a centreline + thickness
  and a maximal straight run; a `WallSegment` separates one room pair and is what
  everything else refers to. **Room** (program) and **Space** (geometry) are split;
  Spaces and junctions are derived, materialised and validated. Model is **integer
  millimetres** — which deletes the validator's tolerance questions rather than
  answering them. Openings are hosted and **typed from a regional catalogue**, not
  dimensioned freely. Annotation leaves the Plan for a derived `Drawing`.
  ADRs [0001](../adr/0001-centreline-walls-over-a-dilated-solve-domain.md) and
  [0002](../adr/0002-annotation-is-derived-not-stored.md).
- [Proposer architecture survey](tickets/18-proposer-architecture-survey.md) — **not
  HouseDiffusion**, and the disqualifier is structural rather than a quality
  argument: it **cannot be conditioned on an Envelope** (`condition_channels=89` =
  25 type + 32 corner-idx + 32 room-idx, no boundary channel), which C4 requires.
  Train a **Brief-conditioned room-set transformer** (~12–25M params, LayoutDM/BLT
  class) with synthetic pre-training, then fine-tune on Swiss Dwellings + ResPlan
  with rooms rectangularised; **retrieval-and-warp** is the runner-up and wins
  outright if the corpora prove too thin at ≥16 areas. Three findings bite harder
  than the architecture choice: **24 rooms is out of distribution for every corpus,
  not just every model** (Swiss Dwellings mean 6.20 rooms, ResPlan 8.1, RPLAN max
  8) — only data fixes that; **overlap is the wrong metric** now the solver forgives
  2–8% of it, while a *nested* pair contributes no relation at all — per-pair
  **separation-direction agreement** predicts survival and nothing published
  measures it; and the proposer is **~20M params, 10–25 GPU-hours, 8–16 ms per
  Proposal**, so it needs a GPU for **training only**. Also corrects the map's own
  evidence: the predecessor's 35.8–66.8% figure is magnitude-confounded (its villa
  brief flattened two storeys into one footprint), and Kuhn and MSD are **one group
  across two papers**, not independent corroboration.
- [Language and runtime split](tickets/02-language-and-runtime-split.md) — **one
  engine language, Python.** `hypar-io/Elements` is rejected: its BREP/CSG kernel is
  precisely the value ADR 0001 deleted, and it makes no annotation claim — the
  research behind that question was never written, and does not need to be. Three
  processes online — **engine**, **proposer service** (HTTP+JSON; **gRPC ruled out**;
  GPU for training only), and **Next.js as the BFF**, the only thing the browser
  talks to — plus an **offline training runtime**. Generation is a **job, not a
  request**: candidates run concurrently on **threads** (measured here — CP-SAT's
  `Solve()` releases the GIL, 1.99× on two concurrent solves) and stream out as each
  passes the acceptance bar. **JSON at every boundary**, because ADR 0001's integer
  millimetres cross it with no float rounding. Export splits: **SVG preview eager**
  per survivor, **DXF/IFC/PDF lazy** on request.

- [Acceptance validator spec](tickets/07-acceptance-validator-spec.md) — **37
  predicates, 28 hard, and the hard set carries no region at all.** Canonical at
  `data/acceptance/rules.json`, prose at `docs/spec/acceptance-bar.md`. Four
  things bind harder than the rule list. **"Written once, consumed twice" is a
  *declaration*, not an implementation** — the solver posts inequalities before
  geometry exists, the validator evaluates finished geometry, and Opening rules are
  unpostable by construction, so each rule names an enforcement site and drift is
  killed by a conformance test over the 14 `both` rules. **The hard floor is the
  ergonomic minimum, not a legal one**, because the table's own
  `hard_reject_below: statutory_floor` is `null` in the default region and yields
  an *empty* hard set — which makes the reject set region-free, so a region can
  change which Plans are *preferred* but never which are *rejected*, and v1 ships
  without settling the region list. **C6 item 1 as written rejects every plan with
  an ensuite**, fixed in the Brief with `access_via` rather than in the predicate,
  because access-through is program, not geometry; circulation splits into named
  **potential** (solver, contact graph) and **realised** (validator, opening graph)
  halves. And **two rules were loosened to survive real homes** — wet clustering
  becomes ≤2 plumbing groups rather than one, and given-Envelope area agreement
  becomes warn-only, since rejecting there rejects 100% of candidates for a fault
  none caused. Adds one rule nothing asked for — **aspect ratio ≤3.0 hard** —
  because a 2750 × 8250 bedroom passes every other test. ADR 0001's integer
  millimetres **delete** three questions rather than answering them: slivers,
  the bbox-vs-polygon overlap re-measurement (discharged by construction, no C11
  work owed), and the corridor pinch allowance. Three rules are `conf: pending` on
  the stub above; 19 are `ENGINE_CHOICE` awaiting a corpus fit.

- [Building scope and envelope handling](tickets/09-building-scope-and-envelope-handling.md)
  — **v1 ships flats and single-storey houses through one code path**, because the
  flat/house difference was never provenance — it is **which edges can hold a
  window**. The Envelope becomes the **inner face** of the external wall (it *is*
  the interior clear region, so a Homeowner's tape number needs no conversion and
  ADR 0001's domain is `dilate(Envelope, t_int/2)` with no `t_ext` term at all) and
  an **ordered ring of edges**, each `exterior` or `party` with an orthogonal
  `entrance_side` flag — orthogonal because a flat's front door *does* pierce a
  party wall. Dwelling type is a **preset over that ring**, region-invariant in
  topology and regional only in label. Shape is rectilinear, bbox minus ≤2 notches
  (rect/L/U/T). **Provenance is per-field and decoupled from dwelling type**, which
  re-keys *Acceptance validator spec*'s area rule and fixes a case it got wrong.
  The finding that costs the most: **every solver timing on this map was measured
  at 100% exterior exposure** — `exterior_faces()` returns every boundary face
  unfiltered — so 6.25 s at 24 rooms describes a *detached bungalow*, and
  `flat_single_aspect` quarters the face set H8 competes for. New axis for *Solver
  timing variance sweep*. Also: **every corpus is flats**, so houses are generated
  from apartment priors and the corpus ranking is confirmed rather than changed;
  and Swiss Dwellings' building hierarchy can supply the real exposure
  distribution. ADR
  [0003](../adr/0003-the-envelope-is-an-inner-face-ring-of-typed-edges.md).

- [Dimensioning and annotation rules](tickets/11-dimensioning-and-annotation-rules.md)
  — **the differentiator is unglamorous, not hard**, and three of its rules were
  reversed mid-session for being easy rather than right. Spec at
  `docs/spec/annotation.md`, ADR
  [0004](../adr/0004-published-dimensions-measure-wall-faces.md). The blockers
  **deleted** most of the ticket before it began: rooms are rectangles so the
  centroid *is* the pole of inaccessibility (no largest-inscribed-circle
  machinery); integer millimetres make chains close by construction; and chains on
  a **ladder outside** the Envelope bbox make chain-vs-plan and chain-vs-chain
  collisions impossible, leaving three local rules and no global solver. What they
  **broke**: **every wall thickness in a region profile must be even** — ADR 0001
  needs `erode(rect, t_int/2)` in integer millimetres — which kills **115 mm and
  125 mm**, the latter being DIN 4172's own octametric module. Dimensions measure
  **faces, never centrelines** (one declared exception: tier 1 takes a party edge
  to centreline, per GIA/IPMS), and ADR 0004 records that this is the *harder*
  formulation — centreline chains have no narrow tick at all, which is why the
  convention exists — taken because a centreline number labelled as a room size is
  wrong by `t_int` everywhere. Held to a **Practitioner's issued set**, which
  reversed: no-schedule → **three drawn schedules** on their own sheet (the one
  thing eleven surveyed vendors document *nowhere*); internal doors by general note
  → **every opening dimensioned**; scale drops to fit A3 → **scale held, sheet
  grows**. Added what the ticket forgot to ask for — **plan graphics**, since flat
  single-weight linework reads as generated before a number is checked. New
  machinery: a **Drawing check** of eleven predicates that gates whether a *file is
  written*, deliberately **not** in `rules.json` — the Acceptance bar has two
  consumers and this has one, and a third would reopen what *Acceptance validator
  spec* closed.

- [Acquire the datasets](tickets/12-acquire-the-datasets.md) — **the >=16-room
  tail is empty, and that lands against the map's own proposer recommendation.**
  Two corpora on disk and verified (Swiss Dwellings md5 matches the publisher
  exactly; ResPlan reconciles to 137,131 room polygons *exactly*), inventory at
  `docs/research/dataset-inventory.md`, loaders in `experiments/corpus-smoke/`.
  Counting the rooms a Brief actually names, **63,800 real dwellings hold 66 with
  >=16 rooms and one with >=24** — against *Proposer architecture survey*'s
  ~1,000 trigger for retrieval-and-warp winning outright. Only the data half of
  that test is settled; the synthetic-pre-training half is now *What the model
  proposes*'s deciding measurement. The stronger form: **RPLAN's maximum is 8
  rooms and MSD is a subset of Swiss Dwellings, so no obtainable real corpus
  reaches the regime** — a synthetic generator is not a first stage any more, it
  is the only possible source. **Ticket 18's blocking SQL is wrong three ways**
  and returns 1,563 instead: it counts SHAFTs (72,255 of them — shafts outnumber
  bathrooms) as rooms, groups across floors despite saying "single floor" (1,672
  apartment_ids span more than one), and swallows `md5("")` as a real apartment
  key. The filtered mean of **6.82 corroborates Ospici's independent 6.20**; the
  unfiltered 9.44 does not. Also **measured the exposure distribution** ADR 0003
  needed — median **0.37** exterior, and **0 of 569 real dwellings above 0.99**,
  so every timing on this map describes a house nobody lives in. Corrections:
  ResPlan's geometry is **not in metres** despite its README (per-plan scale,
  median 0.0545 m/unit), three of its documented keys don't exist, seven plans
  carry a **square-feet bug** in `area`, and Swiss Dwellings ships **no licence
  file at all** — CC BY 4.0 lives only in Zenodo metadata. MSD and ProcTHOR
  deliberately not downloaded (already ruled out); **RPLAN left unsigned** — its
  8-room ceiling adds nothing to the tail that decides the question.

- [What the model proposes, and how it is trained](tickets/08-what-the-model-proposes.md)
  — **the Proposer has two sources, and the fork the map inherited was a false
  one.** Spec `docs/spec/proposer.md`, ADR
  [0005](../adr/0005-the-proposer-has-two-sources.md), measurement in
  `experiments/retrieval-coverage/`. **Retrieval-and-warp** ships first and
  **the survey's room-set transformer** always answers; both emit the same
  Proposal, both go through the same solver, and the Acceptance bar arbitrates —
  C6 always generated many and rejected most, and nothing ever said they come from
  one source. Neither survives alone: measured over all 46,800 Swiss Dwellings
  dwellings with each Brief taking one dwelling's programme and a **different**
  dwelling's envelope, retrieval blanks on **9.5% of 4–6-room and 12.4% of
  7–10-room Briefs** (median pool 92 and 66) and **67.7% at 11–15** — one Brief in
  nine refused is not a usable product — while a trained model **fails quietly**
  and throws away 46,800 arrangements that are real by construction. Explicitly
  rejected because it was the easy answer: **widening the warp budget** until
  retrieval covers everything; ±10% area / ±15% aspect is a **hard gate**, since a
  plan stretched 40% in proportion is the 90%-right artefact C2 calls worse than
  blank. Two cuts follow from evidence: **v1's Proposer serves 4–10 rooms** — so
  **§7.3(a) does not fire, it counted the tail**, and in-band the corpora hold
  ~60,600 dwellings against a ~4,000 floor, 15× — and **synthetic pre-training is
  cut**, its only purpose having been the 12–32 room regime now out of the promise
  (training drops to 5–15 GPU-hours). Two corpus findings nothing on the map had:
  **`ROOM` is 26% of the corpus and is not a grab bag** — p5–p95 9.9–22.4 m²,
  CV 0.29 against `BEDROOM`'s 0.22 — so `{ROOM, BEDROOM, STUDIO}` collapse to one
  class and **every coverage figure measured before that was pessimistic**; and
  **`BATHROOM` spans a WC to a family bathroom under one label**, split ticketed to
  *Ergonomic minima* rather than invented here. Defines the arrangement metric the
  survey assigned it — **three numbers, never one, with confident-wrong as the
  headline** — and refuses to approximate the terminal one: **no partial
  `hard_pass_rate` is published**, because an upper bound with a plausible name is
  how a wrong figure gets quoted later. Training stops at **50 GPU-hours**; past
  it v1 ships retrieval-only with the room-count limit stated in product copy.

- [Which region profiles ship in v1](tickets/14-which-region-profiles-ship.md) —
  **one profile ships, it is `AZ`, and the ticket's own tension dissolved once the
  shipped profile stopped having to be the verification profile.** Spec in
  `data/standards/room-constraints.json` (`region_model` and `tier_model`
  rewritten), ADR
  [0006](../adr/0006-one-shipping-profile-and-it-is-not-the-corpus-region.md),
  measurement in `experiments/corpus-smoke/wall_thickness_swiss.py`. The map said
  two regions were in tension; there are **four and no two agree** — retrieval is
  **CH only**, the trained model is CH+IN, every standards source actually read is
  **UK**, and the stub's declared default was **DE with zero DE sources**. Three
  findings killed DE outright: its rationale cites a corpus that is *Swiss, not
  German*; building the profile means transcribing Neufert into a data file, which
  is the exact infringement findings §7.6 item 7 names; and its canonical 115 mm
  partition is **illegal under ADR 0004** — the octametric series 115/365/490 is
  systematically odd, so **the even-millimetre rule is a quiet anti-DIN filter**
  nobody had noticed. The measurement that mattered is a **negative result**:
  Swiss Dwellings' 1.5 M wall polygons were supposed to *supply* the thickness
  catalogue and **there is no module in the corpus at all** — 59.1% of walls within
  ±2 mm of a multiple of 10 against 50% for uniform noise, modal snapped value
  5.60%, near-continuous 50–600 mm — so the catalogue is `ENGINE_CHOICE`
  unavoidably, and corpus thickness never reaches a Plan anyway because ADR 0001
  re-derives geometry from our own `t_int`. `AZ` was chosen as a **construction
  system, not a country**: the SNiP-family norm is written for *multi-apartment
  buildings*, which is the only building type any corpus here holds; its brick and
  panel series are expected to be all-even where DIN's are odd; its sources are
  free; and it is where a plan would actually be built. **The profile ships
  empty on purpose** — inventing a catalogue is the 90%-right artefact C2 calls
  worse than blank — and is owed by *The Azerbaijani region profile*. Also: the
  stub's `must_match` is **struck** (read literally it forbids a UK profile
  forever), replaced by *a Plan carries its profile for life*; `statutory_floor`
  becomes a **warn worded from the source's `force` field**, not from the tier's
  name, and AZ is the first region where it is non-null at all; and *Area
  measurement convention*'s item 5 is **answered from the geometry model** — v1
  has no ceiling height and no balcony, so the deductions that make the
  conventions diverge cannot fire.

- [Solver timing variance sweep](tickets/15-solver-timing-variance-sweep.md) —
  **15 s and τ = 4, both fitted; and four of the map's own claims move.** 965
  serial solves on the machine every published number came from; findings are
  `docs/research/solver-formulation.md` **Part II**, ADR
  [0007](../adr/0007-published-minima-must-erode-onto-the-solve-grid.md),
  harness in `experiments/solver-toy/`. The limit is the **p95 of time-to-VALID**
  (13.65 s) and catches **96.5%** of runs that ever reach a valid Plan; 30 s buys
  3.1 points more. On expiry, **objective ≥ `soft_weight` means no survivor** —
  discard, never show, which is arithmetic rather than a re-validation pass. What
  bites hardest: **the Proposal *can* make the model infeasible on ordinary
  noise**, so *Solver formulation*'s boxed "single most important design rule" is
  **false as written** — `fix_relations` posts relations as hard constraints, and
  at **σ = 1.0 m of corner noise 5 of 5 seeds are INFEASIBLE at 24 rooms**, and at
  the σ = 0.5 m every published run used, 3 of 5 already fail at 12 rooms.
  **v1 sits on the edge of the cliff, not below it**, and
  Proposal quality costs *feasibility*, not seconds — solve time barely moves at
  all, so the ticket's "where does time turn over" never turns over. τ is the
  valve on that one channel, which is why it is a feasibility knob first, free at
  8 rooms and unaffordable at 24. **ADR 0001's cost was misidentified**: the
  feared 10⁸ products are harmless (three encodings indistinguishable; the eroded
  area is *affine* in the grid product, so no second multiplication is needed) but
  `250w − t ≥ min_w` costs one whole grid unit per room per axis and **provably
  deletes 4-, 5- and 6-room dwellings** — the bottom half of C13's band — with
  more area not fixing it. ADR 0007 makes the erosion free. **Exposure is not a
  timing axis at all** — the ticket's central expectation, refuted; every preset
  sits inside every other's seed spread — but `flat_single_aspect` is
  **arithmetically dead from 7 rooms**, and it is the corpus p25, ticketed as
  *H8 and the single-aspect flat*. Two of ADR 0003's four presets sit above the
  corpus p95, so a fitted `corpus_median` was added. **Cores buy correctness, not
  latency** (24 rooms: time-to-first flat at 2.39 s across 1/2/4 workers, but one
  worker is 0% valid and two are 100%) — **two workers is a floor**, offered in
  place of the modern-CPU figure that **could not be measured**, because this
  machine *is* the original Ivy Bridge. Drawing: chains never exceed **10
  witnesses a side**, the narrow-tick rule fires 6–13 times a plan with **zero
  collisions ever** (so §5a's alternation is do-not-build), **A1 is never
  reached**, all 159 chains closed — and **tier 2b is half the drawing, not a
  fallback** (10 of 21 walls at 24 rooms), so tier 1 sits at 34 mm by default.
  Corrects `annotation.md` in four places including §14's own narrow-tick count.
  Closes the windowless-dwelling rider: the three units below 0.02 exterior hold
  6 rooms in 14.1 m² and are annotation fragments, so **H8 is not rejecting homes
  that exist**. Also: **the infeasibility core discriminates nothing** — every
  INFEASIBLE run at every size returned the identical five-family set.

## Not yet specified

In scope, not yet sharp enough to ticket. Graduates as the frontier advances.

- **Interactive re-solve** (C7's deferred half) — what a Practitioner drags, what
  stays pinned, how fast the re-solve must feel. The geometry model is now settled
  and gives it a wall centreline to drag and a Brief-anchored identity to pin
  against; what remains vague is the interaction itself, so it stays fog.
- **Variant generation and ranking** — the *scoring* half is answered by
  *Acceptance validator spec*: the six soft rules are the score, and the
  zero-survivor case is settled (diagnose arithmetically, never show a failing
  Plan). What stays fog is the economics — how many candidates are produced, how
  many survive, how many are shown, and how a Homeowner chooses between them.
  *Building scope and envelope handling* hands this patch one **known asymmetry,
  deliberately unpatched**: an invented Envelope gets 2–3 aspect ratios as a real
  diversity axis, a stated one gets none and varies only by Proposal. So flats —
  the corpus-backed case and the likelier v1 purchase — get *less* variety than
  bungalows, which is backwards from where the demand is. Envelope jitter was
  rejected as a patch here; the fix belongs to whatever settles the economics.
- **What a corpus-shaped product looks like.** *Acquire the datasets* found ~95%
  of 63,800 real dwellings sit between 4 and 10 rooms, mean 6.8. The room-count
  half of that is now a ticket — *The room-count envelope v1 promises*. What stays
  fog is everything else the distribution implies: whether the **Brief's defaults**
  should be drawn from the corpus rather than from the standards table, whether
  candidate generation should be **biased toward corpus-typical shapes**, and
  whether a Brief far from the corpus centre should be flagged to the Homeowner
  before a solve rather than after. **Sharpened by the route, which is both.**
  Corpus-typicality is now *structural* for the ~89% of common-band Briefs
  retrieval covers and a *choice* for the rest — so the question is no longer
  which, but what a Homeowner is told when their Brief crosses that line. Note the
  line is already measurable at Brief-parse time: retrieval's gate is a lookup, so
  the system knows before it solves whether this Brief has real precedent. Nothing
  yet says whether that should be shown.

- **Plan quality beyond the validator** — narrowed by *Acceptance validator
  spec*: there now *is* a ranking signal, six soft rules and two warns, including
  the aspect-ratio term added specifically because a plan can pass everything and
  still read as generated. What stays fog is whether that score correlates with
  human judgement at all — the eval protocol, the perceptual metric, or held-out
  likelihood that would tell us.
- **Fixtures and furniture** — Swiss Dwellings carries sinks, toilets, bathtubs.
  Do we place them, and does furniture-fit become a constraint or just a render?
  Now carries two hooks. The **ergonomic minima are derived from fixture footprints
  plus body clearances**, so fixtures are already implicit in the hard rule set
  even though no fixture is modelled; and one acceptance rule
  (`open.wc_door_outward_pan_overlap`) sits `deferred` in the registry, with its
  source and its 250 mm, waiting only for a pan to exist.
- **Non-orthogonal geometry** — no longer a presumption: *Building scope and
  envelope handling* fixed v1's Envelope as **rectilinear, bbox minus ≤2 notches**
  (rect/L/U/T), and ADR 0003 records why. What stays fog is when and how angled
  walls enter, and the ≤2 cap is unevidenced in both directions — the toy ran one
  L and two U envelopes, which shows two notches are affordable and says nothing
  about three. *What the model proposes* added the first evidence that the cap may
  be **too tight rather than too loose**: real dwellings fill only **0.79** of
  their minimum-area rotated rectangle at the median and **0.61** at p5, so a
  meaningful share of Swiss Dwellings is more notched than rect/L/U/T can
  describe. **How many real dwellings fit inside the cap is unmeasured**, and it
  bounds retrieval from a direction nothing has tested — a corpus dwelling the
  Envelope model cannot express is a retrieval match that cannot be warped. It
  also carries a **deliberately unbuilt dependency**: room-tag
  placement is the Space *centroid*, exact only because every v1 Space is a
  rectangle. The day a room is concave, tags start landing outside their own rooms
  and largest-inscribed-circle placement has to be specified — *Dimensioning and
  annotation rules* left it out on purpose rather than building for a case that
  cannot occur.
- **Structural and services reality** — load-bearing walls, plumbing stacks,
  risers. C6 item 5 gestures at wet-room clustering; the real version is larger.
  The geometry model left the hook deliberately: a wall's `load_bearing` is
  **unknown**, not false, so nothing has to be un-asserted when this is picked up.
  *Building scope and envelope handling* sharpens the point: **party walls now
  exist in the model** and are the walls most obviously load-bearing in a real
  building, and they still carry `load_bearing: None`. The hook is now paying for
  something concrete rather than being merely prudent.
- **Frontend rendering and manipulation** — narrowed by *Language and runtime
  split*: the stack is **Next.js/TypeScript**, it talks to the engine as a **BFF over
  JSON**, and every survivor arrives as an **eager SVG preview**, so *viewing* a plan
  is largely settled. *Dimensioning and annotation rules* then fixed **what that
  preview contains**: one `Drawing`, two presentations, every element carrying an
  **audience**, so the preview is a filter — plan graphics and room tags — and not a
  second annotation engine. What stays fog is **manipulation** — canvas, WebGL or
  SVG-in-DOM once C7's interactive re-solve is picked up, and how that couples to the
  drag-and-pin question below.
- **Persistence, accounts, hosting** — where projects live, what a session is. Now
  carries a known consequence: *Language and runtime split* chose a **service** the
  BFF proxies and streams through, but the honest end state for a job model is a
  **queue plus a result store**, with the engine as a pure worker and no HTTP surface
  at all. That was deferred because a broker and a store *are* this fog patch —
  expect the transport to move when it clears.
- **Revit round-trip specifics** — C2 promises the engine won't preclude it. The
  export research found Revit's IFC *import* is the weak link rather than the
  authoring (`docs/research/bim-cad-export-stack.md` §4); what that costs us is
  still unspecified.
- **The unverified solver literature.** *Solver formulation for layout projection*
  settled the question empirically, but its survey of MIP, rectangular-dual theory
  and `kiwisolver` died with the session and is tagged `[UNVERIFIED]` throughout.
  Low value while CP-SAT holds; it sharpens if the wall-thickness question in
  *Canonical geometry model* breaks the current formulation, or when C7's
  interactive re-solve is picked up and `kiwisolver` actually matters. *Update:
  the wall-thickness question did not break the formulation — see* Canonical
  geometry model *— so this stays cold until C7 is picked up.*
- ~~**Whether the proposer is worth training at all**~~ — **closed.** *What the
  model proposes* answered it: **yes, and also retrieval, and the question was
  never exclusive.** The trigger that looked decisive counted the ≥16-room tail,
  which v1 no longer promises; in the band it does promise the corpora are 15× the
  training floor. Retrieval's measured **9.5–12.4% blank rate** in that band is why
  it cannot be the only source. Not fog — settled.

- **Where warp fidelity actually breaks.** New, and it is the fog patch with the
  most product value on the map: every point of retrieval coverage bought is a
  Brief that does not fall through to a model. *What the model proposes* stated
  ±10% area / ±15% aspect as the admissibility gate and was explicit that the
  numbers are **the budget coverage was measured at, not a fitted value**.
  Loosening raises coverage and lowers fidelity, and nobody has measured the
  trade. Sharp enough to be a sub-question of *The retrieval index and warp
  procedure* and not yet sharp enough to be its own ticket, because what "fidelity"
  means here needs the arrangement metric validated first.

- **Whether a discrete thickness catalogue reproduces real dwelling geometry.**
  New, and it is the residue of *Which region profiles ship in v1*'s negative
  result. Real surveyed walls have **no module** — near-continuous 50–600 mm, p25
  109 / p50 169 / p75 267 — while every Plan this engine emits will draw from a
  chosen catalogue of perhaps eight even values. An 8-entry catalogue matches 58.5%
  of real walls within ±10 mm and a 12-entry one 70.9%, but nothing says whether
  the *dwellings* built from a discretised catalogue read as real, or whether the
  areas they enclose drift systematically against the corpus. Adjacent to *Fit the
  ENGINE_CHOICE acceptance thresholds to the corpora* and not owned by it: that
  ticket fits acceptance thresholds, this is about whether the geometry itself is
  plausible. Sharpens once *The Azerbaijani region profile* names actual values to
  test.

- **The Proposal-quality floor, and how often the fallback fires.** New, and it is
  the fog patch the sweep created. *Solver timing variance sweep* found the
  recommended configuration goes INFEASIBLE between **σ 0.5 and 1.0 m** of
  per-corner Proposal noise, and that τ buys the margin back cheaply at 8 rooms and
  not at 24. What stays fog is the number that matters commercially: **how often a
  real Proposer lands past the cliff**, which decides whether the two-phase
  fallback is a rare safety net or a routine second solve — and therefore how many
  candidates must be launched to get a survivor. Neither source has been measured
  against the solver: retrieval-and-warp's admissibility gate is stated in area and
  aspect, not in the corner noise this cliff is measured in, and the trained model
  has no measured noise figure at all. Sharpens the moment *The retrieval index and
  warp procedure* produces real warped Proposals, and it feeds the economics
  question under *Variant generation and ranking* directly.

- **Whether the solve grid should be finer than 250 mm.** Long deferred as
  "optional curiosity"; ADR 0007 gives it a price. The clear-reading rounding loss
  is exactly `grid − t_int` per room per axis, so a 125 mm grid halves it and a
  50 mm grid removes it, and the standards table would then be free of the
  congruence rule. Nobody has measured what a finer grid costs the solve — the
  variance sweep ran entirely at 250 mm — so the trade is one measured cost against
  one unmeasured one. It also collides with a profile offering **two** internal
  thicknesses, which ADR 0007 shows has no common solution at 250 mm.

## Out of scope

Ruled beyond this destination. Does not graduate; returns only as a fresh effort.

- **Permit-submittable output and legal code compliance.** C8. Liability and
  jurisdiction swamp; every surveyed vendor that claimed it was doing LLM-Q&A over
  a user-uploaded PDF.
- **Multi-storey buildings, stair alignment across floors.** C5. The next product,
  not this one.
- **Multi-family, commercial, and large buildings.** C5. Massing and packing is a
  different problem from room layout.
- **Practitioner-first workflow and native Revit round-trip as a v1 requirement.**
  C2 — the engine must not preclude it, but shipping it is not on this route.
- **Commercial productisation, pricing, licensing posture.** C9.
- **Detail drawings, and material-differentiated hatching.** Ruled out by
  *Dimensioning and annotation rules*. v1's drawing scale ladder tops out at 1:50,
  where solid poché is the correct convention; material hatches (masonry,
  insulation, stud) belong to 1:20 details, and a detail asserts a construction
  build-up this system does not model and C8 forbids it claiming.
- **The site: plot boundaries, setbacks, and any solar or daylight model.** Ruled
  out by *Building scope and envelope handling*. v1 never generates a footprint
  *from* a plot — the Envelope is stated or derived from the programme, and it is
  fixed before the solve. Nothing downstream needs a sun: the Acceptance bar's
  window rules are topological (exterior wall run), never solar. A **north angle is
  still stored** on the Envelope, used only for the Drawing's north arrow and as a
  soft Brief preference, so the export does not have to lie about orientation.

- **A second region profile in v1, and any claim of regional *layouts*.** Ruled out
  by *Which region profiles ship in v1*. The two halves of "add a region" differ by
  orders of magnitude: a second *standards* profile is ~30 numbers in a data file,
  while a second *layout* region is a corpus that does not exist — retrieval reads
  Swiss Dwellings only and ResPlan was excluded from it on metric grounds. So the
  narrowing is real and the trap is the other way round from the one the ticket
  feared: shipping one profile costs almost nothing, and *implying* it brings
  regional layouts with it would be the lie. `DE`, `US` and the `IN`/`JP`/`AU`/`CN`
  stubs are deleted from the enum; `UK` survives only as a test fixture.
