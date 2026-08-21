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
| C15 | **The standards table carries two arithmetic constraints.** ADR 0004: every wall thickness even. ADR 0007: every published minimum satisfies `min + t_int ≡ 0 (mod grid)`, because ADR 0001's clear reading otherwise costs a whole grid unit per room per axis and **provably deletes 4-, 5- and 6-room dwellings**. Both are ship gates on a region profile, and both are now **asserted** rather than claimed -- `experiments/region-profile/gate_check.py`, 28 assertions. *Amended by **ADR 0009**, and the amendment matters*: the two constraints apply to **different layers**. Even-thickness is global. **Congruence binds region profiles only** -- the region-invariant ergonomic layer is exempt, because its numbers are derived from fixture footprints rather than quoted from a source, so there is no nominal-to-clear conversion to apply and rounding one down deletes the fixture that defines the room. The 4-/5-/6-room deletion tracked the minima's **magnitude**, not the congruence. |
| C8 | **Neufert-grade dimensional standards. No legal code-compliance claim, ever.** Say so in the product copy. *Neufert now names the grade, not the source* — *Which region profiles ship in v1* found that building a profile out of it is the one copyright move the research forbids, and the shipping profile draws on freely-published regulatory text instead. |
| C9 | **Non-commercial project.** Research-only datasets and weights are available. Licence is not a gate; data quality and regional convention are. |
| C10 | **Model proposes, solver projects** — *amended, and the amendment is load-bearing.* The Proposal must carry **relative arrangement, not just boxes** (pairwise separations promoted to hard linear constraints), and exact tiling must be posted **soft, not hard**. The loose form — hand the solver boxes and let it project them — is **refuted by measurement**: it finds nothing at 24 rooms in 30 s. Amended, 6.25 s. A **two-phase fallback for infeasible Proposals is mandatory** — and *Solver timing variance sweep* moved this from prudence to operational necessity: `fix_relations` posts the Proposal's relations as **hard constraints**, so a merely **noisy** Proposal goes INFEASIBLE (5 of 5 seeds at 24 rooms at σ = 1.0 m, against σ = 0.5 m in every published run). The formulation doc's boxed claim that the Proposal *cannot* make the model infeasible is **false as written**. Shipped parameters: **time limit 15 s, τ = 4**. See *Solver formulation for layout projection*. **And "the model" is two things**: v1's Proposer has two sources — retrieval-and-warp and a trained transformer — behind one Proposal contract, with the Acceptance bar arbitrating. The split it names is proposal-versus-projection, not one generator versus another. See *What the model proposes, and how it is trained* and ADR 0005. |
| C11 | **Clean successor to `../plan-generator-3000-pro-max`.** No code inherited. Its findings may be reused only after independent verification. |
| C12 | Not tied to any region. Combine corpora where it can be made to work. *Amended: that was freedom, not a requirement to serve everywhere.* v1 ships **exactly one** region profile and it is **`AZ`**; `UK` is retained as a test fixture and is never selectable. See C14. |
| C13 | **v1's Proposer serves 4–10 Brief-named rooms.** 92% of the corpus. Set by *What the model proposes*, which measured retrieval dying at 11+ (67.7% blank). What the *product* promises is *The room-count envelope v1 promises*; this is what the Proposer covers. |
| C14 | **A region profile is a construction system plus a drawing convention, and it never rejects a Plan.** It owns the thickness catalogue, decimal separator, room-name abbreviations, opening catalogue keys, two soft area targets and one soft window fraction; every hard dimensional floor is the region-invariant ergonomic minimum. **`RegionProfile` and `CorpusProvenance` are two fields**, holding `AZ` and `CH`, and their disagreement is the normal case — v1 draws **Swiss-shaped layouts to Azerbaijani conventions, permanently**, and says so. See *Which region profiles ship in v1* and ADR 0006. **Now populated** by *The Azerbaijani region profile*, and it ships **one construction type and one `t_int` (120 mm brick)** because at a 250 mm grid no two plausible thicknesses share an ADR 0007 residue class. `statutory_floor` is non-null for the first time, and the drawing is **in Azerbaijani**. |

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
  split*; the Revit half is not. ⚠️ **Its DXF version floor is also wrong, and *The
  Azerbaijani region profile* measured it.** R2000/R2004 are *code-page* formats,
  not Unicode ones — the doc's line that *"`²` survived — R2000+ is
  unicode-capable"* generalises one lucky probe. **No legacy code page anywhere
  encodes `ə`**, not even Turkish cp1254, so an Azerbaijani drawing is
  unrepresentable at R2000, and Russian is worse rather than better (cp1251 cannot
  encode `²`). **The floor is R2007.** Corrected in place; nothing shipped is
  broken, because *Dimensioning and annotation rules* §11 already writes R2010.
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
  nine refused is not a usable product — ⚠️ *those three figures are **superseded**:
  they were measured on the unconverted corpus, and* Rectangularising real rooms
  *removes 31% of the retrieval index, disproportionately from the top of the band
  (83% of 4-room dwellings convert, 46% of 10-room). The conclusion they support —
  neither source survives alone — is strengthened, not weakened; the numbers must
  be re-measured by* The retrieval index and warp procedure — while a trained model **fails quietly**
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

- [Rectangularising real rooms](tickets/22-rectangularising-real-rooms.md) — **a
  corpus dwelling is converted by solving it**, and the ticket's premise was wrong
  twice before anything could be decided. Findings
  `docs/research/rectangularisation.md`, ADR
  [0008](../adr/0008-a-corpus-dwelling-is-converted-by-solving-it.md), harness
  `experiments/rectangularise/`. **"40% of rooms are not rectangles" has no
  meaning without an axis** — in the corpus's own geo-referenced coordinates
  **0.0%** of Swiss Dwellings rooms are rectangles, and on the dwelling's own axis
  **48.9%** are, the first measurement of this corpus; and **ResPlan's 43.2% is a
  vertex count**, not a shape measure — 53.9% of its rooms have an area equal to
  their bounding box, so every downstream use of 43.2% was pessimistic. Also:
  corpus rooms are **Spaces that never touch** (p50 gap 99 mm, share touching
  0.000), so "do they still tile" was malformed — they never tiled. All three
  per-room conversions fail because each converts a room in ignorance of its
  neighbours: the **largest inscribed rectangle destroys 38% of every real
  adjacency** and the area-preserving one 24%, both manufacturing confident-wrong
  assertions, because holding area while the bbox inflates it 11% *means*
  shrinking and shrinking deletes contacts. **The bounding box preserves the
  separation relation exactly, by construction** — a relation is a bounds test and
  a bbox preserves bounds, 1.0000 on 931,369 pairs — so its failure is *not*
  feasibility; it is that its rectangles collide in **86%** of dwellings and an
  overlapping pair **abstains**, handing the solver a target that is not a Plan
  with the interesting pairs silently dropped. So: one CP-SAT fit per dwelling on
  the 250 mm grid, relations and door-width adjacencies **hard**, tiling **soft** —
  the shipping solver's own structure pointed at a real home. **Zero adjacencies
  destroyed and zero relations flipped or weakened across both corpora**; IoU
  median 0.895 Swiss / 0.679 ResPlan; area error median −3.5% against bbox's
  +11.1%. The reject rule is **representability, and it is decidable** — every
  dwelling proven optimal or proven infeasible inside 10 s, zero UNKNOWN — and it
  holds exactly for **69% of Swiss Dwellings and 60% of ResPlan**. ⚠️ **Amended
  after the fact, because the first framing was wrong**: every corpus dwelling is
  a real, built, QA'd home, so a rule that "rejects" 31% of them measures **what
  our model cannot express**, not what is wrong with the data — and *Acceptance
  validator spec* had already set the opposite principle by loosening two rules
  "to survive real homes". Replaced by a **fidelity ladder**: tier A exact
  (0.7360), B neighbour-relations only (0.8200), C relations soft (0.9375), D
  adjacency soft (**1.0000**). **Retrieval admits tier A only** — its claim is
  that someone lived in *this* arrangement — while **training takes every
  dwelling** at its best tier, carried as a conditioning field, which also deletes
  the size bias below. Ablation's last row is the sentence: with relations and
  adjacency both free **100%** convert, so **nothing here is un-tileable — what
  fails is tiling a dwelling *as itself*.** Three things were measured wrong first,
  each of which looked obviously right: posting tiling **hard** rejects nearly
  every dwelling; the **shipped L1 corner objective is wrong for fitting** (IoU
  0.14 against 0.82 — projection and fitting are different problems); and a notch
  taken as the complement's **bounding box** over-cuts, deleting a room in 15% of
  dwellings. Beyond the ask: **Graph2Plan's 93% does not survive either corpus** —
  bbox ∩ envelope buys 1.3 points because the envelope explains only 2.3–2.8% of
  real non-rectangularity, so rooms are concave because another *room* is there,
  and the gap the ticket asked about is the corpus rather than the method;
  **ADR 0003's ≤2-notch cap is evidenced and vindicated** — 61.8% of dwellings
  need ≤2, a third notch recovers 0.64 points of area, and **raising the cap makes
  conversion worse** (66.8% at four against 73.6% at two); and non-rectangularity
  is **two room types** — CORRIDOR and LIVING_DINING at 26% rectangular against
  BEDROOM's 77%, while ResPlan folds circulation into `living`, rectangular in
  **1.7%** of plans, which is why it converts far worse and is a second reason it
  stays training-only. ⚠️ **Invalidates *What the model proposes*' coverage
  table**: the 9.5% and 12.4% blank rates were measured unconverted, and the
  conversion takes the index disproportionately from the top of the band (83% of
  4-room dwellings convert, 46% of 10-room), so retrieval thins most where it was
  already thinnest — affordable only because ADR 0005 gives a blanked Brief
  somewhere to go. What the 31% is **not** is a boxiness filter: rooms that were
  already rectangles are 53.90% of the corpus and **53.72%** of what survives, so
  the self-confirming spiral a rectangle model invites does not happen. What it
  selects for is **size and interlock** — median dropped dwelling 8 rooms and
  89.9 m² against 6 rooms and 71.7 m², bbox overlap 2.9× higher, `STOREROOM`
  over-represented 1.71× — so the corpus skews **small**, which compounds a
  thinness *Acquire the datasets* already found above 10 rooms and lands on
  *The room-count envelope v1 promises* as well as on retrieval.

- [Validate the arrangement metric against the solver](tickets/24-validate-the-arrangement-metric.md)
  — **the metric predicts, and it was defined wrong in three places.** Findings
  `docs/research/arrangement-metric.md`, spec rewritten at
  `docs/spec/proposer.md` §5.1–5.5, harness `experiments/solver-toy/`
  (`arrangement.py`, `probe6.py`, 724 runs). With the Proposal held at ground
  truth so the relation set is the only corrupted channel: **0 relations the
  truth contradicts → 100% survivor; 1 → 6%; 2 → 0%**, 88% of those proved
  INFEASIBLE. The ticket asked how steeply failure rises with the rate and the
  answer is that **there is no slope** — one wrong relation is most of the damage
  and two is all of it. It is **causal**: deleting only the injected relations
  restores OPTIMAL in 43 of 45, while those relations *alone* are infeasible in
  just 10% — so a confident-wrong relation is fatal **in company**, and the
  better the rest of a Proposal the more each error costs. Three defects in the
  definition. **The cycle rate is identically zero and cannot be otherwise** —
  the extractor adds relations greedily and skips any that would close a per-axis
  cycle, so the asserted set is acyclic *by construction*, the guard never fires
  on real Proposals, and removing it changes nothing measurable; the ticket's own
  suspect — *cycles, not pairs, kill a solve* — is refuted by the strongest route
  available, the number cannot be non-zero. **§5.1 read literally over-counts by
  up to 3.6×**, because two boxes can be separated on *both* axes and asserting
  the non-`argmin` one is not wrong in any way the solver can feel — 6.30%
  against 1.74% at 24 rooms — and `CONTEXT.md`'s "asserted, and **backwards**"
  was right all along, so the **spec had drifted from the domain model**. And
  **counting is the wrong unit**: severity — the millimetres of overlap the
  assertion demands — beats it, with **severity below 2 000 mm implying a
  survivor in 80 runs of 80** in band; a *rate* is the wrong shape entirely,
  since it compounds over a quadratic pair count (0.5% leaves a Proposal clean
  88% of the time at 8 rooms and **28%** at 24). Beyond the ask: **the kind of
  wrongness matters more than the count** — a same-axis **reversal** is INFEASIBLE
  at 100% of every dose tested while a cross-axis swap is 0–33%, and **Gaussian
  corner noise, the corruption behind every published number on this map, emits
  essentially no reversals**, so every σ result understates a learned generator's
  real danger. The **abstain** interaction is confirmed with a far larger
  asymmetry than claimed — **not one abstain run at any size was INFEASIBLE**, and
  dropping *every* relation still yields a survivor at 8 and 12 rooms — but only
  after the first attempt was found **confounded by the solution hint** and
  re-run without it; abstain costs **seconds**, confident-wrong costs the
  **candidate**, and at 12 rooms abstaining on half the pairs takes two wrong
  relations from 0% survivable to 67%. **One number now explains two knobs**: at
  *Solver timing variance sweep*'s own rig, 12 rooms, σ = 0.5 m, τ = 0 gives
  severity 2 800 mm and 2 survivors of 5 — **reproducing that ticket's "3 of 5
  already fail" exactly** — and τ = 4 gives 200 mm and 5 of 5, so **what τ filters
  is confident-wrong severity**. ⚠️ **The metric predicts feasibility, not
  survival**: in C13's 4–10-room band zero confident-wrong implied a survivor 67
  times in 67, but at 24 rooms **40% of clean Proposals still fail on the 15 s
  limit** and τ inverts — every missed failure in the validation is at 24 rooms.
  It is therefore a **training and evaluation instrument only**; at serving time
  there is no ground truth. What can run without one is a **chain bound** —
  along any directed path rooms sit side by side, so the Envelope must exceed
  their summed minimum widths — which condemns **62%** of infeasible relation
  sets with no solver, though **0%** at the doses of one or two that matter.
  Housekeeping: the extractor is now **module level** so the metric runs the
  solver's own (verified behaviour-identical, 24 comparisons, 0 mismatches), and
  **`solver._core` cannot blame a relation** — it rebuilds from `cfg` and drops
  them — while CP-SAT's assumption core returns the entire set in 45 of 54 runs,
  the same non-minimality ticket 15 found, by a second construction. **Replicated
  on fresh draws**, which also exposed that the harness's RNG key changed
  mid-sweep — so the two result files are independent samples, not one run
  repeated — and that **CP-SAT's survivor verdict is stable (96%) while its
  status is not (87%)**: runs slide between INFEASIBLE and timeout without
  changing whether a candidate appeared, so every headline here rests on the
  survivor verdict.

- [The Azerbaijani region profile](tickets/25-the-azerbaijani-region-profile.md) —
  **the profile is populated, every load-bearing value is `verified` against an
  Azerbaijani document read first-hand, and the ticket's own instruction was the
  wrong one.** `data/standards/room-constraints.json` → `profiles.AZ`, findings
  `docs/research/az-region-profile.md`, gates
  `experiments/region-profile/gate_check.py` (**28 assertions, all pass**). The
  ticket said to fall back on SNiP/SP ancestors labelled `REPORTED`; `arxkom.gov.az`
  serves the AzDTN PDFs on an unauthenticated GET, and **the fallback would have
  been actively wrong** — *AzDTN 2.7-2 terminated СНиП 2.08.01-89\*'s legal force in
  Azerbaijan on 2021-11-30*, so its "classic numbers" are folklore *and* repealed
  (living room 14/16 not 12, kitchen 8 not 6, 1.4 m is the *передняя* and the
  corridor is 0.85 m). Publishing them would have asserted a 2500 mm storey height
  where AZ requires 2700 and an 850 mm **statutory** corridor floor — the exact C8
  breach the ticket existed to prevent. **Generalise: `REPORTED` off an ancestor is
  not a safe degradation of `VERIFIED`**; where the descendant repealed the
  ancestor it is a false claim. Catalogue: **`brick` alone, `t_int` 120**, bearing
  250, `t_ext` leaf 380 (total 500 **provisional**, blocked on Baku's `Dd`),
  `t_party` **250** derived from AZ's **50 dB** (not Russia's 52), where 120 mm
  computes to 49 and fails. **One `t_int` is forced arithmetic, not preference** —
  over 19 candidates the set of pairs sharing a residue class mod 250 is **empty**,
  structurally, since brick steps by 130 and RC panels by 20; the ticket's
  `{100,200}` was the general case. The even rule nearly killed AZ too:
  **ГОСТ 21520-89 gives cellular blocks two series by laying method and the
  thin-bed-glue one — the modern default — is 195/245/295, all odd**, so the
  `block` type is excluded. **`statutory_floor` is non-null for the first time on
  this map** and the force chain was read link by link to art. 14.3; but **nine of
  thirteen area cells and all six width cells are `null` by design**, because
  AzDTN cl. 5.6 delegates every intra-apartment width to *erqonomika* **by name** —
  Azerbaijani law points at the invariant layer. ⚠️ **ADR 0007 turns out to have no
  consumer inside a region profile at all** (`hard linear minima published by
  profile AZ: 0`, asserted): its scope is too broad — areas, storey heights, door
  widths and turning squares must not be aligned — and every value it governs sits
  in the region-**invariant** layer, which cannot carry a per-profile `t_int`.
  Its escape does not generalise either: publishing below the source's figure is a
  *unit conversion*, available for a quoted number and not for a body-derived one.
  **Measured once the `ergonomic` layer landed mid-session: 36 of its 36 hard
  linear minima miss the residue class**, up to +242 mm per room per axis, worst on
  `corridor` and `hall`. ✅ **Settled concurrently by *Ergonomic minima and the
  constraint table's missing half***, which reached the same distinction from the
  other side and wrote **ADR 0009** — congruence is a *region-profile* ship gate
  only, the ergonomic layer is exempt, the grid stays 250 mm. A ticket drafted for
  it here was **retracted rather than filed**. ⚠️ ADR 0009 also **refutes** the
  scarier half of this: rounding up does *not* trigger ADR 0007's 4-/5-/6-room
  deletion, because **that deletion tracked the minima's magnitude, not the
  congruence** — it was measured against the placeholder table, and the derived
  floor is about half of it. The real cost is the **WC**, whose whole width
  distribution spans under two grid steps (23.0% → 56.1% rejected if snapped). Drawing is **Azerbaijani**, and choosing it made
  the spec *smaller* — **no published room-name abbreviation set exists in any
  candidate language**, so the ladder's step 2 is deleted in favour of the room
  number + schedule that SPDS and ISO 4157-2 independently prescribe and §6 already
  ships. Also: decimal **comma**, no thousands grouping, `DIMDSEP` **inert as
  specified**; opening marks are **two-level** where the spec models one; openings
  even but **blocks odd** (2071/2085/2175). Closes **`de_baybo`** — both consumers
  re-sourced to AzDTN 2.7-2, and `win.kitchen_windowless` **inverted its premise**
  (Bayern permitted a windowless kitchen; AZ requires the window). Hands *Area
  measurement convention* a reframed question: **there is no *жилая площадь* in
  Azerbaijan** — the pair was replaced, not extended — and what AZ has is **two
  in-force contradicting definitions of *ümumi sahə***, of which only the
  finished-versus-structural face binds v1.

- [Ergonomic minima and the constraint table's missing half](tickets/19-ergonomic-minima-and-the-tables-missing-half.md)
  — **the hard floor is authored, and the ticket's own method had to be corrected
  twice before one number could be published.** Data
  `data/standards/room-constraints.json` key `ergonomic` (generated, not typed, by
  `experiments/region-profile/build_ergonomic_layer.py`, so the numbers and the
  arithmetic cannot drift apart), findings `docs/research/ergonomic-minima.md`,
  ADR [0009](../adr/0009-a-derived-minimum-is-not-rounded-onto-the-solve-grid.md),
  harnesses in `experiments/region-profile/`. **A derived floor is not
  self-justifying**: composed from the clearances the sources actually state, the
  `bathroom` floor lands at 4.0 m² and **rejects 36% of real Swiss bathrooms** —
  because **every clearance in the entire source corpus is an accessibility
  figure** (AD M's 750 mm is a *wheelchair transfer space*), regulators being the
  only people who write clearances down, and the ordinary private bathroom having
  no regulator. That is §5.1's "our own choices" arriving as a measurement. **And
  the low tail is real**, so there is no fragments escape hatch: checked against
  the corpus's own `BATHTUB`/`SHOWER`/`TOILET` entities, **0% of `wc` rooms fail to
  hold a pan and 0.8% of `bathroom` rooms fail to hold a 1700 mm bath** — and the
  corpus's `bathroom` long-side p1 of **1717 mm is the bath**, confirming AD M's
  footprint without being asked. So: **structure derived, one constant
  calibrated** — footprints plus `u`, the body zone that cannot be *shared* with
  another fixture's zone (zones may overlap each other, never another fixture's
  footprint, which is most of why the first derivation came out too big). Fitted
  to ~5% max rejection, `u` lands on **300 mm**, which is also **Neufert's stated
  minimum** from a pan's free side to a wall — fitted and cited agree. The corpus
  may **falsify** a number and never supply one. 18 room types, clear,
  `(shorter, longer)`: `wc` 800×1000/0.8 m², `bathroom` 1000×1700/1.7,
  `bedroom_double` 1650×1900/3.1, `living` 1850×2000/3.7. **Floors, not targets** —
  `living`'s 3.7 against a corpus median of 20.6 is correct, C14 having already
  put liveability in the profile. **§8's directional/orientation-free split
  dissolves**: the rules bind the *shorter* and *longer* dimension, not x and y, so
  no type needs an axis binding and most are non-square once fixtures drive the
  rectangle — only `corridor` is square, having no second dimension of its own.
  Composite rooms publish a **permissive envelope** over their packings, because a
  `(short, long)` pair cannot say "contains packing A *or* B" and under-rejecting
  is the correct error direction for a hard floor. **The four flags now exist as
  data** — `is_habitable`/`is_wet`/`is_private`/`needs_window` were prose in §8
  while four registry rules consumed them, and a flag the registry cannot read is
  a predicate that silently does not fire; `study` `is_private` flips to **true**,
  per `CONTEXT.md`'s Private room class. All three `pending` rules flipped by JSON
  pointer, so **`rules.json` now carries zero**, and `hard_reject_below` reads
  `ergonomic` in **both** files where they previously disagreed. The HITL decision:
  **ADR 0007 rounds *down*, and its justification is a unit conversion that a
  derived number has nothing to apply** — a derived 1700 *is* the bath — so this
  layer can only round **up**, which is arithmetically the row ADR 0007 measured as
  fatal. Obeying it costs the `wc` floor **23.0% → 56.1%** of real WCs, because
  **the whole real WC width distribution, p1 744 to p50 1099, spans less than two
  grid steps**. Exempted; grid held at 250 mm; see C15 and ADR 0009. ⚠️ **And the
  corroborating measurement came back mixed, which is reported rather than
  smoothed**: re-running ADR 0007's own counts at 8 seeds, the derived floor
  **recovers n = 4 outright** (0/8 → 8/8) and **still loses n = 5 entirely**
  (8/8 → 0/8), while n = 6 is **not assessable** because the derived table fails it
  under the baseline reading too. The deletion narrows from `{4,5,6}` to `{5, and 6
  unknown}` — it is **not removed**, and the magnitude hypothesis is half right. So
  *whether the solve grid should be finer than 250 mm* gains a **measured cost of
  staying**: the 5-room case, the bottom of C13's band and the corpus's commonest
  dwelling size, is what 250 mm is currently charging. ⚠️ **Refutes
  an obligation it was given**: *What the model proposes* handed it the `BATHROOM`
  split on the reasoning that the threshold "falls out of the table" as the
  boundary between two minima. **It cannot** — two floors are both floors (`wc`
  0.8, `shower_room` 1.4) and a threshold there misclassifies 19%; the classes
  differ in **distribution**, not minimum. Fitted to **fixture ground truth**
  instead over 66,386 labelled rooms: **2.4 m²**, 5.9% error, against 23.3% for the
  3.6 m² the derivation implied. Also: **`de_baybo` was closed better by *The
  Azerbaijani region profile***, concurrently — re-sourcing both consumers to AzDTN
  caught that **AZ requires the kitchen window where Bayern permitted its
  absence**, an inverted premise adding the missing block would have hidden; the
  block added here was withdrawn. Leaves `study` as **the weakest number in the
  file** (one-desk programme, no corpus label, no source), and hands
  *Two room vocabularies in one file* the collision the parallel sessions created.

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
- **Non-orthogonal geometry** — ⚠️ **this patch was two questions wearing one
  name, and the conflation cost the map a decision nobody examined.** An
  **L-shaped room is orthogonal.** It is a union of two axis-aligned rectangles,
  and CP-SAT places two rectangles as happily as one. Filing "a room that is not a
  rectangle" next to "walls at an angle" made the cheap question inherit the
  expensive one's deferral, and every downstream ticket then inherited *one box
  per Room* without anyone weighing it. The map's own text shows the seam: the
  **Envelope** may have two notches — L, U, T — while a **room** may not have one.
  Split out as *Whether a Room may be more than one rectangle*; what remains in
  this patch is **angled walls only**, which genuinely do break the coordinate
  model and are genuinely v2. ⚠️ **And the split is not cosmetic** — measured in
  *Rectangularising real rooms*' follow-on
  (`experiments/rectangularise/rectilinear_k.py`, 8,293 rooms): **only 2.67% of
  real dwellings have every room a rectangle**, against 23.9% if a Room may be an
  L and 54.7% at three rectangles. Per room it is 52.9% / 77.8% / 87.6%, and
  CORRIDOR — the room the whole circulation model rests on — is a rectangle just
  **29.8%** of the time. So *one box per Room* is not a modelling simplification
  with a small cost; it is the reason the corpus conversion has to approximate at
  all. Settle it before anything is built.

  No longer a presumption: *Building scope and
  envelope handling* fixed v1's Envelope as **rectilinear, bbox minus ≤2 notches**
  (rect/L/U/T), and ADR 0003 records why. **The ≤2 cap is no longer unevidenced, and it is vindicated** —
  *Rectangularising real rooms* measured it: **61.8%** of real dwellings need two
  notches or fewer, the rest lose a median **1.85%** of envelope area to the cap,
  a third notch recovers 0.64 points of that and a fourth 0.18, and a plain
  rectangle would lose 16.5% — so L/U/T earn their place and the curve is flat
  past two. **Raising the cap makes things worse**: conversion falls to 66.8% at
  four notches against 73.6% at two, because a more articulated Envelope is
  harder to tile with *n* rectangles. That closes the suspicion *What the model
  proposes* raised from the 0.79 median rotated-rectangle fill — real dwellings
  are indeed more notched than rect/L/U/T describes, and it costs almost nothing.
  The patch also carries a **deliberately unbuilt dependency**: room-tag
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


- **The Proposal-quality floor, and how often the fallback fires.** New, and it is
  the fog patch the sweep created. *Solver timing variance sweep* found the
  recommended configuration goes INFEASIBLE between **σ 0.5 and 1.0 m** of
  per-corner Proposal noise, and that τ buys the margin back cheaply at 8 rooms and
  not at 24. What stays fog is the number that matters commercially: **how often a
  real Proposer lands past the cliff**, which decides whether the two-phase
  fallback is a rare safety net or a routine second solve — and therefore how many
  candidates must be launched to get a survivor. Sharpens the moment *The retrieval
  index and warp procedure* produces real warped Proposals, and it feeds the
  economics question under *Variant generation and ranking* directly.
  **The unit problem is now solved, and the cliff is a symptom rather than the
  thing.** *Validate the arrangement metric against the solver* found that what a
  noisy Proposal actually loses is separation directions: one relation the truth
  contradicts makes the model INFEASIBLE 56% of the time, and **severity** — the
  millimetres of overlap the wrong assertions demand — is the quantity that
  predicts, explaining τ and σ with one number. So neither source has to be
  expressed in corner noise any more; both can be scored directly, and *The
  retrieval index and warp procedure* now says how. What stays fog is the
  **distribution** — nobody has run a real Proposer and counted how many of its
  Proposals land past the threshold. One caution the validation hands this patch:
  the reliably fatal error is a **same-axis reversal**, and Gaussian corner noise,
  the model behind every σ number on this map, emits almost none — so the cliff's
  shape may not survive contact with a generator that misplaces a room outright.

- **Whether the solve grid should be finer than 250 mm.** Long deferred as
  "optional curiosity"; ADR 0007 gives it a price. The clear-reading rounding loss
  is exactly `grid − t_int` per room per axis, so a 125 mm grid halves it and a
  50 mm grid removes it, and the standards table would then be free of the
  congruence rule. Nobody has measured what a finer grid costs the solve — the
  variance sweep ran entirely at 250 mm — so the trade is one measured cost against
  one unmeasured one. It also collides with a profile offering **two** internal
  thicknesses, which ADR 0007 shows has no common solution at 250 mm. ⚠️ **This is
  now load-bearing rather than curious, and it has an owner.** *The Azerbaijani
  region profile* found the two-thickness collision is not a corner case: over 19
  sourced candidates **no pair shares a residue class mod 250**, structurally,
  because the brick series steps by 130 and the RC-panel series by 20. And the
  alignment problem turned out not to live in region profiles at all — **36 of the
  36 hard linear minima in the region-invariant `ergonomic` layer miss the class**.
  **ADR 0009 then held the grid at 250 mm** and exempted that layer instead, on the
  ground that a derived minimum has no nominal-to-clear conversion to apply — and it
  priced the alternatives: a 50 mm grid makes the congruence vacuous and every
  derived minimum exactly representable, a 125 mm grid still cannot represent the
  1700 mm bath, and **every solver number on this map was fitted at 250 mm**. So the
  patch stays fog, with two inputs it did not have. Nothing published is snapped to
  250 mm, which makes a finer grid **strictly easier to adopt later, never harder**.
  And *Ergonomic minima* then measured what the exemption costs: the deletion
  narrows to `{5, and 6 unknown}` rather than clearing, so **250 mm is charging the
  5-room case** — the bottom of C13's promised band and the commonest dwelling size
  in the corpus. The trade is no longer one measured cost against one unmeasured
  one; both sides now have a number, and only the solve-time side is missing.

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
