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

### Done-test

"Someone could staff the build" means **every component below is `settled`**. This
is the only thing that orders the frontier: the tickets are nearly all unblocked,
so pick by which gap is widest and which sits furthest upstream, not by which is
easiest to take. A ⚠️ on a `settled` row is a live challenge to something already
decided — it does not un-settle the row, but it is why that row can still move.

Every open ticket appears here exactly once. A row with no ticket is **unowned**,
and that is the failure this table exists to catch.

| Component | | Owed by |
|---|---|---|
| Plan geometry model — Wall, WallSegment, Room/Space, integer mm, hosted Openings, wall **layer sets** | settled | ⚠️ its *one box per Room* premise was never weighed — *Whether a Room may be more than one rectangle* |
| Envelope — inner-face ring of typed edges, rect/L/U/T | settled | ⚠️ *H8 and the single-aspect flat*. How an **invented** Envelope is derived is still fog, under *Variant generation and ranking* |
| Corpus conversion — how a real dwelling becomes retrieval and training data | settled | ⚠️ no converted plan has ever been looked at — *Look at the converted corpus* |
| Solver projection — CP-SAT, 250 mm grid, 15 s, τ = 4 | settled | ⚠️ every timing and the whole feasibility cliff rest on guillotine ground truth — *The solver has only ever seen guillotine layouts* |
| Proposer source B — trained transformer: architecture, corpus prep, metric, stopping rule | settled | — |
| Runtime and process split — engine / proposer service / BFF, job model, threads, JSON | settled | ⚠️ the honest end state (queue + result store) is fog, under *Persistence, accounts, hosting* |
| DXF export | settled | — |
| Proposal contract — what a source emits and the solver consumes | partial | *The Proposal cannot express zoning* — whether the contract can carry what plans are actually judged by |
| Proposer source A — retrieval-and-warp, which ships first | partial | gate and coverage decided, **mechanism not** — *The retrieval index and warp procedure* |
| Acceptance bar — 38 predicates, enforcement sites, conformance test | partial | **19 of 38 thresholds are `ENGINE_CHOICE`** — *Fit the ENGINE_CHOICE acceptance thresholds to the corpora*. Opening rules need *Opening placement rules* |
| Standards table — region-invariant ergonomic floor + the `AZ` profile | partial | **the file holds two unmapped room taxonomies** — *Two room vocabularies in one file, and nothing maps between them*. ✅ its thickness is now measured-vindicated: 150 lands **4 mm from the corpus-optimal 146** |
| Drawing — graphics, chains, schedules, tags, sheet, Drawing check | partial | its US NCS / AIA defaults contradict an Azerbaijani drawing, **and ADR 0004's one centreline number is now dead** — both owed by *The annotation spec is US-shaped and the drawing is now Azerbaijani*. ⚠️ **a uniform partition draws two wall weights where 76.1% of real dwellings draw three** — *One wall weight where a real plan draws three* |
| **Brief and parsing contract** — the object a prompt becomes, and per C4 the real interface | **open** | nothing written, but **unblocked** and now handed its two area fields — *Brief schema and parsing contract* |
| Area measurement convention — what a m² means everywhere it travels | settled | — |
| **IFC export** — the Destination's second named output | **open** | ⚠️ **was unowned until the done-test ran.** `IFC` appears in no spec file; *BIM and CAD export stack* proved the tooling, never the content — *What IFC the engine actually emits*, now **unblocked** and handed its quantity and its wall layers |
| **Homeowner product surface** — the whole of C2's user | **open** | nothing written — *Homeowner product surface*, waiting on the Brief |
| **Room-count promise** — what the product says it covers, against C13's 4–10 | **open** | *The room-count envelope v1 promises* |

## Notes

**This map is an index.** Every decision below lives in full on its ticket, under
`## Resolution`. The line here exists only to tell you whether to open it — do not
restate a resolution here, link it. A ⚠️ marks a claim not to take at face value.

**Check `writes:` before you claim.** Every open ticket declares in its frontmatter
which artifacts it authors. **Do not start a ticket that shares a `writes:` entry
with one already claimed** — take another from the frontier instead, or finish the
first. This is a *concurrency* rule, not a dependency: the tickets can be worked in
either order, just not at once.

It exists because two of them already went wrong that way. *Two room vocabularies in
one file* and *The annotation spec is US-shaped and the drawing is now Azerbaijani*
are both pure rework, created by parallel sessions writing the same file blind to
each other — "two tickets populated it in parallel and neither could see the other's
keys". The graph is nearly flat, so almost anything can be claimed at once, and
nothing but this rule stops it happening again.

Six artifacts have more than one claimant. Read this as a **conflict map, not an
order** — the done-test decides order:

| Artifact | Claimed by |
|---|---|
| `CONTEXT.md` | 10, 21, 31 |
| `data/standards/room-constraints.json` | 16, 31, 32 |
| `data/acceptance/rules.json` | 16, 20, 26 |
| `docs/spec/acceptance-bar.md` | 26, 28 |
| `docs/spec/proposer.md` | 23, 28, 30 — 28 and 30 both amend §1, so **30 is blocked by 28** |
| `docs/spec/annotation.md` | 28, 32 |

Only one of these became a blocking edge, and deliberately: sharing a file is a
merge hazard, sharing a *decision* is a dependency. 28 changes the Proposal
contract's shape rather than adding to it, so 30 would otherwise be amending a
contract about to move.

**Skills every session should consult:** `grilling` and `domain-modeling` by
default. `research` for `wayfinder:research` tickets. `prototype` for
`wayfinder:prototype` tickets.

**Domain vocabulary** — `CONTEXT.md`, which carries the geometry terms and the
**clear versus centreline** distinction every dimension in this system declares.

- **Homeowner** — describes needs in prose, cannot draw a boundary, cannot read a
  dimension string. Judges by "would I live here". Tolerates 90%-right. **The v1 buyer.**
- **Practitioner** — architect/designer. Judges by "does this open in Revit and stay
  workable". 90%-right is worse than blank. **Not the v1 buyer, but the standard the
  engine is held to.**

**Standing constraints** — every session inherits these:

| # | Constraint |
|---|---|
| C1 | Destination is a **spec + decisions**, not a prototype and not a build. |
| C2 | **Homeowner is the v1 user**; the internal geometry model is built to Practitioner grade from day one. The Homeowner never sees that layer. |
| C3 | Hard output floor: **dimensioned 2D vector plan** — walls with thickness, doors, windows, room tags, dimension strings — to DXF/PDF. IFC/BIM is the stated export path. |
| C4 | Input is **prompt → LLM-parsed structured brief**, gaps filled from standards, every assumption surfaced. The brief stays editable; it is the real interface. |
| C5 | **Single-dwelling residential, single storey.** Flats and houses ship through **one code path** — dwelling type is a preset over the Envelope's edge ring, not a branch. Product copy states two limits: single storey only, and **house layouts come from apartment priors**, because every corpus is flats. |
| C6 | Acceptance bar is a **hard filter**: generate many, reject most, show survivors. On solver expiry, a candidate whose best objective is ≥ `soft_weight` has unassigned floor and is **not a survivor** — discard it, never show it. |
| C7 | Post-generation, v1 is **edit-the-brief-and-regenerate**. Direct wall manipulation with re-solve is designed-for but deferred. |
| C8 | **Neufert-*grade* dimensional standards. No legal code-compliance claim, ever** — say so in the product copy. Neufert names the grade, not the source: building a profile out of it is the one copyright move the research forbids. |
| C9 | **Non-commercial project.** Research-only datasets and weights are available. Licence is not a gate; data quality and regional convention are. |
| C10 | **Model proposes, solver projects** — amended, and the amendment is load-bearing. The Proposal carries **relative arrangement, not just boxes** (pairwise separations promoted to hard linear constraints) and exact tiling is posted **soft**. The loose form is refuted by measurement. A **two-phase fallback is mandatory**: a merely *noisy* Proposal goes INFEASIBLE. Shipped: **15 s, τ = 4**. And "the model" is **two sources** behind one Proposal contract — ADR 0005. |
| C11 | **Clean successor to `../plan-generator-3000-pro-max`.** No code inherited. Its findings may be reused only after independent verification. |
| C12 | Not tied to any region — but that was freedom, not an obligation to serve everywhere. v1 ships **exactly one** profile and it is **`AZ`**; `UK` survives as a test fixture and is never selectable. |
| C13 | **v1's Proposer serves 4–10 Brief-named rooms**, 92% of the corpus; retrieval dies at 11+. What the *product* promises is *The room-count envelope v1 promises*. |
| C14 | **A region profile is a construction system plus a drawing convention, and it never rejects a Plan.** It owns the thickness catalogue, decimal separator, room-name abbreviations, opening catalogue keys, two soft area targets and one soft window fraction; every hard dimensional floor is the region-invariant ergonomic minimum. **`RegionProfile` and `CorpusProvenance` are two fields**, `AZ` and `CH`, and their disagreement is the normal case — v1 draws **Swiss-shaped layouts to Azerbaijani conventions, permanently**, and says so. Now populated: **one construction type, brick, `t_int` 150 mm — a layer set, 120 structural + 2 × 15 finish, every term `verified`**, drawing in Azerbaijani. It also owns the **area convention**, and every published number measures to that finish plane. ADR 0006, ADR 0010. |
| C15 | **Two arithmetic ship gates, and they bind different layers.** ADR 0004 — every wall thickness **even** — is global. ADR 0007 — `min + t_int ≡ 0 (mod grid)` — binds **region profiles only**; ADR 0009 exempts the region-invariant ergonomic layer, whose minima are *derived* rather than quoted and so have no nominal-to-clear conversion to apply. Asserted, not claimed: `experiments/region-profile/gate_check.py` — **33 gates, all pass** after ADR 0010 moved the residue class from 130 to 100 mod 250 and sharpened ADR 0004 to bind on **totals, not layer components**. |

**Evidence that shaped the map** — read before re-litigating C10:

- `docs/research/floorplan-generation-stack.md` — **zero of ~20 published generators
  (2020–2026) emit walls with thickness.** You are shopping for a room-topology
  proposer, not a floor-plan engine.
- `docs/research/competitive-landscape.md` — eleven products, $0–$20k/yr, all stop at
  schematic design; **none documents a dimensioning or annotation system.** That gap
  is C3.
- `../plan-generator-3000-pro-max/docs/phase2_findings.md` and `phase3_findings.md` —
  HouseDiffusion degrades outside its 5–8 room regime and repair recovers 31% / 7% /
  **0%**. *"Repair works, and it is not enough."* Strong prior; re-verify per C11.
  ⚠️ Its 35.8–66.8% overlap figure is **magnitude-confounded** — see *Proposer
  architecture survey*.

## Decisions so far

<!-- INDEX ONLY. One entry per closed ticket: the headline, where the detail lives,
     and any warning that changes how far to trust it. Full reasoning is on the
     ticket, under ## Resolution. Do not restate it here. -->

- [BIM and CAD export stack](tickets/03-bim-and-cad-export-stack.md) — **C3 is
  buildable.** `ezdxf` authors genuine DXF `DIMENSION` entities and `ifcopenshell`
  clean IFC4; the industry-wide annotation gap is a product choice, not a tooling
  limit. `docs/research/bim-cad-export-stack.md`. ⚠️ Two claims corrected since: its
  §4/§5 (Revit import, `hypar-io/Elements`) **were never written** — Elements is
  closed by *Language and runtime split*, Revit is not — and its **R2000 version floor
  is wrong. The floor is R2007**: no legacy code page encodes `ə`.
- [Dimensional standards corpus](tickets/05-dimensional-standards-corpus.md) — the
  convention-derived half of the table needs a **`region` parameter and a tier per
  cell**; England alone yields five minimum bedroom areas, and Neufert prescribes no
  minimum areas at all, so the defaults are our own choices.
  `docs/research/dimensional-standards.md`. ⚠️ Its "shipped at `room-constraints.json`"
  was false (a stub), and its `must_match` / `default_region: DE` are **struck** by
  *Which region profiles ship in v1*. The verification-region reasoning survives and
  is what the successor built on.
- [Solver formulation for layout projection](tickets/04-solver-formulation-for-layout-projection.md)
  — **GO on C10, amended.** CP-SAT over a 250 mm integer grid, Proposal separations
  hard and exact tiling soft: 24 rooms in **6.25 s VALID**, where the unamended form
  finds nothing in 30 s. Circulation is a single-commodity flow constraint; objective
  is L1 corner displacement; two-phase fallback mandatory.
  `docs/research/solver-formulation.md`. ⚠️ Its boxed "the Proposal *cannot* make the
  model infeasible" is **false as written** (*Solver timing variance sweep*), and its
  MIP / rectangular-dual / `kiwisolver` survey is `[UNVERIFIED]` throughout.
- [Cross-dataset unification](tickets/06-cross-dataset-unification.md) — **do not
  pool.** Swiss Dwellings is the backbone, ResPlan merges under a conditioning tag,
  RPLAN is demoted to optional pre-training, MSD and ProcTHOR are out; condition on
  `(region, corpus, annotation_provenance)`. `docs/research/dataset-unification.md`.
  ⚠️ Every `[DOC]` claim is provisional — ResPlan's real data contradicts its own paper
  on two material points.
- [Canonical geometry model](tickets/01-canonical-geometry-model.md) — **walls with
  thickness survive the solver.** The solver tiles a **solve domain** — the clear
  region dilated by `t_int/2` — so every tiling edge is a wall centreline and
  `clear = erode(solved, t_int/2)` holds with no perimeter special case; only constants
  move. A `Wall` is a centreline + thickness; a `WallSegment` separates one room pair.
  **Room (program) and Space (geometry) are split.** Model is **integer millimetres**,
  which *deletes* the validator's tolerance questions rather than answering them.
  Openings are hosted and typed from a regional catalogue. Annotation leaves the Plan
  for a derived `Drawing`. ADR 0001, ADR 0002.
- [Proposer architecture survey](tickets/18-proposer-architecture-survey.md) — **not
  HouseDiffusion**, and the disqualifier is structural: it **cannot be conditioned on
  an Envelope**, which C4 requires. Train a **Brief-conditioned room-set transformer**
  (~12–25M params, LayoutDM/BLT class); retrieval-and-warp is the runner-up. Three
  findings bite harder than the choice: 24 rooms is out of distribution for every
  **corpus**, not just every model; **overlap is the wrong metric** — per-pair
  separation-direction agreement predicts survival, and nothing published measures it;
  and the GPU is needed for **training only**.
  `docs/research/proposer-architecture.md`. ⚠️ Its blocking SQL is **wrong three ways**
  (*Acquire the datasets*), and its retrieval-wins trigger counted a tail v1 no longer
  promises.
- [Language and runtime split](tickets/02-language-and-runtime-split.md) — **one
  engine language, Python.** `hypar-io/Elements` rejected: its BREP/CSG kernel is
  precisely the value ADR 0001 deleted. Three processes online — **engine**,
  **proposer service** (HTTP+JSON, gRPC ruled out), and **Next.js as the BFF**, the
  only thing the browser talks to — plus an offline training runtime. Generation is a
  **job, not a request**: candidates run on **threads** (CP-SAT releases the GIL,
  1.99× measured here) and stream out as each passes the bar. **JSON at every
  boundary.** SVG preview eager per survivor; DXF/IFC/PDF lazy.
- [Acceptance validator spec](tickets/07-acceptance-validator-spec.md) — **37
  predicates, 28 hard, and the hard set carries no region at all.**
  `data/acceptance/rules.json`, `docs/spec/acceptance-bar.md`. "Written once, consumed
  twice" is a **declaration, not an implementation** — each rule names an enforcement
  site and drift is killed by a conformance test over the 14 `both` rules. The hard
  floor is the **ergonomic minimum**, not a legal one, which is what makes the reject
  set region-free. Circulation splits into **potential** (solver) and **realised**
  (validator). Two rules were loosened to survive real homes; **aspect ratio ≤3.0
  hard** was added because a 2750 × 8250 bedroom passes every other test. ⚠️ 19 rules
  remain `ENGINE_CHOICE`, owed by *Fit the ENGINE_CHOICE acceptance thresholds to the corpora*.
- [Building scope and envelope handling](tickets/09-building-scope-and-envelope-handling.md)
  — **flats and single-storey houses through one code path**, because the difference
  was never provenance — it is **which edges can hold a window**. The Envelope is the
  **inner face** of the external wall and an **ordered ring of typed edges**
  (`exterior`/`party`, with an orthogonal `entrance_side` flag); dwelling type is a
  preset over that ring. Shape is rectilinear, bbox minus **≤2 notches** (rect/L/U/T).
  Provenance is per-field and decoupled from dwelling type. ADR 0003. ⚠️ The finding
  that costs the most: **every solver timing on this map was measured at 100% exterior
  exposure** — a detached bungalow — against a corpus median of 0.37.
- [Dimensioning and annotation rules](tickets/11-dimensioning-and-annotation-rules.md)
  — **the differentiator is unglamorous, not hard**, and three rules were reversed
  mid-session for being easy rather than right. `docs/spec/annotation.md`, ADR 0004.
  Dimensions measure **faces, never centrelines** (one declared exception: tier 1
  party edge to centreline). **Every wall thickness in a region profile must be even**,
  which kills 115 and 125 mm. Held to a Practitioner's issued set: **three drawn
  schedules**, every opening dimensioned, scale held and the sheet grows. Adds **plan
  graphics**, unasked. A **Drawing check** of eleven predicates gates whether a file is
  written — deliberately *not* in `rules.json`. ⚠️ Corrected in four places by *Solver
  timing variance sweep*; ⚠️ its US NCS / AIA defaults are contested by *The annotation
  spec is US-shaped*; ⚠️ **its one centreline number is dead** — ADR 0010 took tier 1
  to the finished inner face, so the sheet now carries no centreline dimension at all.
- [Acquire the datasets](tickets/12-acquire-the-datasets.md) — **the ≥16-room tail is
  empty.** Two corpora on disk and hash-verified; inventory
  `docs/research/dataset-inventory.md`, loaders `experiments/corpus-smoke/`. 63,800
  real dwellings hold **66 with ≥16 rooms and one with ≥24**, and RPLAN's ceiling is 8
  — so **no obtainable real corpus reaches that regime**. The filtered mean of **6.82**
  corroborates Ospici's independent 6.20. Also measured the exposure distribution ADR
  0003 needed: median **0.37**, and **0 of 569** dwellings above 0.99. ⚠️ Corrections
  that bite downstream: ResPlan is **not metric** despite its README, three documented
  keys don't exist, seven plans carry a square-feet bug, and Swiss Dwellings ships
  **no licence file at all**.
- [What the model proposes, and how it is trained](tickets/08-what-the-model-proposes.md)
  — **the Proposer has two sources, and the fork the map inherited was false.**
  `docs/spec/proposer.md`, ADR 0005, `experiments/retrieval-coverage/`.
  Retrieval-and-warp ships first and the room-set transformer always answers; one
  Proposal contract, one solver, the Acceptance bar arbitrates. Neither survives alone.
  The warp budget **±10% area / ±15% aspect is a hard gate** — widening it was rejected
  explicitly as the easy answer. Two cuts follow from evidence: **v1 serves 4–10 rooms**
  (C13), and **synthetic pre-training is cut**. `{ROOM, BEDROOM, STUDIO}` collapse to
  one class, so every coverage figure measured before that was pessimistic. ⚠️ Its
  coverage table — 9.5% / 12.4% / 67.7% blank — is **superseded**: measured on the
  unconverted corpus, and re-owed by *The retrieval index and warp procedure*.
- [Which region profiles ship in v1](tickets/14-which-region-profiles-ship.md) — **one
  profile ships and it is `AZ`.** ADR 0006,
  `experiments/corpus-smoke/wall_thickness_swiss.py`. DE was killed three ways,
  including that its canonical 115 mm partition is **illegal under ADR 0004** — the
  even-millimetre rule is a quiet anti-DIN filter nobody had noticed. The measurement
  that mattered is a **negative result**: the corpus was supposed to *supply* the
  thickness catalogue and **there is no module in it at all** (near-continuous
  50–600 mm), so the catalogue is `ENGINE_CHOICE` unavoidably. `AZ` was chosen as a
  **construction system, not a country**. The profile shipped **empty on purpose**, and
  is populated by *The Azerbaijani region profile*. ⚠️ **Its thickness census mixes
  internal and external walls**, so every "sits at the corpus p*N*" reading off it is
  comparing a partition against a population two to three times heavier — *One internal
  thickness* re-measures it internal-only and the shipped value moves from "near the p25"
  to **≈ p60, above the internal median**. ⚠️ Its "8 entries match 58.5% of real walls" is
  **74.7%** on internal walls.
- [Solver timing variance sweep](tickets/15-solver-timing-variance-sweep.md) — **15 s
  and τ = 4, both fitted**, from 965 serial solves. `docs/research/solver-formulation.md`
  Part II, ADR 0007, `experiments/solver-toy/`. The limit is the p95 of time-to-VALID
  (13.65 s), catching 96.5% of runs that ever reach a valid Plan. What bites hardest:
  **Proposal quality costs *feasibility*, not seconds** — solve time barely moves — and
  **v1 sits on the edge of the cliff, not below it**. **ADR 0001's cost was
  misidentified**: `250w − t ≥ min_w` costs a whole grid unit per room per axis and
  provably deletes 4-, 5- and 6-room dwellings; ADR 0007 makes the erosion free.
  **Exposure is not a timing axis at all**, but `flat_single_aspect` is arithmetically
  dead from 7 rooms → *H8 and the single-aspect flat*. **Two workers is a floor** — one
  is 0% valid, two are 100%.
- [Rectangularising real rooms](tickets/22-rectangularising-real-rooms.md) — **a corpus
  dwelling is converted by solving it.** `docs/research/rectangularisation.md`, ADR
  0008, `experiments/rectangularise/`. "40% of rooms are not rectangles" has no meaning
  without an axis — **0.0%** in the corpus's own coordinates, **48.9%** on the
  dwelling's. One CP-SAT fit per dwelling, relations and door-width adjacencies hard
  and tiling soft: **zero adjacencies destroyed, zero relations flipped**, IoU median
  0.895 Swiss. The reject rule is **representability, and it is decidable** — it holds
  for 69% Swiss / 60% ResPlan. Amended into a **fidelity ladder** (A exact → D adjacency
  soft): **retrieval admits tier A only**, training takes every dwelling. ⚠️
  **Invalidates *What the model proposes*' coverage table.** ⚠️ Its follow-on is what
  *Whether a Room may be more than one rectangle* rests on: only **2.67%** of real
  dwellings have every room a rectangle.
- [Validate the arrangement metric against the solver](tickets/24-validate-the-arrangement-metric.md)
  — **the metric predicts, and it was defined wrong in three places.**
  `docs/research/arrangement-metric.md`, `docs/spec/proposer.md` §5.1–5.5,
  `experiments/solver-toy/` (724 runs). **0 contradicted relations → 100% survivor;
  1 → 6%; 2 → 0%** — there is no slope, and it is causal: a confident-wrong relation is
  fatal **in company**. Three defects: the cycle rate is identically zero *by
  construction*; §5.1 read literally **over-counts by up to 3.6×**; and **counting is
  the wrong unit — severity is**, the millimetres of overlap the assertion demands,
  below 2 000 mm implying a survivor 80 times in 80. **One number now explains both τ
  and σ.** ⚠️ It predicts **feasibility, not survival** — at 24 rooms 40% of clean
  Proposals still fail on the 15 s limit — so it is a **training and evaluation
  instrument only**; at serving time there is no ground truth.
- [The Azerbaijani region profile](tickets/25-the-azerbaijani-region-profile.md) — **the
  profile is populated, and every load-bearing value is `verified` against an
  Azerbaijani document read first-hand.** `profiles.AZ` in
  `data/standards/room-constraints.json`, findings `docs/research/az-region-profile.md`,
  gates `experiments/region-profile/gate_check.py` (28 assertions). ⚠️ **The ticket's
  own instruction was wrong, and the correction generalises**: `REPORTED` off a SNiP
  ancestor is *not* a safe degradation of `VERIFIED` — AzDTN 2.7-2 repealed
  СНиП 2.08.01-89\* in 2021, so its classic numbers are folklore *and* repealed, and
  publishing them would have been the exact C8 breach the ticket existed to prevent.
  Catalogue: **`brick` alone, `t_int` 120**, `t_party` 250 derived from AZ's 50 dB.
  **One `t_int` is forced arithmetic, not preference** — over 19 candidates, no pair
  shares a residue class mod 250. `statutory_floor` is non-null for the first time on
  this map. Drawing is **Azerbaijani**, decimal comma. ⚠️ **ADR 0007 turns out to have
  no consumer inside a region profile at all** — resolved by ADR 0009.
- [Ergonomic minima and the constraint table's missing half](tickets/19-ergonomic-minima-and-the-tables-missing-half.md)
  — **the region-free hard floor is authored**, generated rather than typed by
  `experiments/region-profile/build_ergonomic_layer.py` so the numbers and their
  arithmetic cannot drift apart. `room-constraints.json` key `ergonomic`, findings
  `docs/research/ergonomic-minima.md`, ADR 0009. **A derived floor is not
  self-justifying**: composed straight from the sources it rejects **36% of real Swiss
  bathrooms**, because **every clearance in the entire source corpus is an accessibility
  figure** and the ordinary private bathroom has no regulator. So: structure derived,
  one constant calibrated — `u` = **300 mm**, which is also Neufert's stated minimum.
  18 room types, bound on `(shorter, longer)` rather than x and y, so §8's axis split
  dissolves. **Floors, not targets.** The four flags now exist as data, and `rules.json`
  carries zero `pending`. ⚠️ **ADR 0009 exempts this layer from ADR 0007's congruence**
  — obeying it would take the `wc` floor from 23.0% to 56.1% of real WCs rejected.
  ⚠️ Corroboration came back **mixed and is reported rather than smoothed**: the
  4-/5-/6-room deletion narrows to **{5, and 6 unknown}**, so 250 mm is charging the
  5-room case. ⚠️ **Refutes the `BATHROOM` split it was handed** — fitted to fixture
  ground truth at **2.4 m²** instead. `study` is the weakest number in the file.
  ⚠️ **Its room-count deletion analysis is re-owed** — the *{5, and 6 unknown}*
  narrowing was computed at `t_int` 120, and ADR 0010 makes it 150.
- [Area measurement convention](tickets/17-area-measurement-convention.md) — **the
  convention was never the hard part; the plane was.** ADR 0010,
  `docs/spec/acceptance-bar.md` §8, `CONTEXT.md`, `rules.json` (37 → **38 rules**).
  Four documents claimed published numbers measured **finished** faces while ADR
  0001 eroded half a **bare** leaf — and `bathroom.min_clear_long` is 1700 *because
  a bath is 1700*, delivering 1670. So a **Wall's thickness is a layer set**, its
  **total** is the only number anything consumes, and `t_int` goes **120 → 150**.
  Relabelling was refuted by arithmetic, not taste. The metric is `ümumi sahə` per
  **Area Qaydalar cl. 3.8** — which **sums room areas and does not count
  partitions**, so it is *not* GIA, and the total-area gate changed **quantity**,
  not tolerance, by roughly the width of the gate itself. New hard rule
  `area.convention_agrees`: **presence of a convention was never agreement.**
  ⚠️ ADR 0004's one centreline number — tier 1 to a party-wall centreline — is
  **dead**, as ADR 0004 §4 pre-authorised. ✅ Its one `engine_choice` was
  discharged the same day — see below.
- [What an Azerbaijani finish layer actually is](tickets/35-what-an-azerbaijani-finish-layer-is.md)
  — **15 mm, and it is now `verified`.** `docs/research/az-finish-layer.md`,
  `experiments/finish-layer/`. **AzDTN 2.12-4\* Əlavə 8\*, Cədvəl 1, rows 27–28**,
  *plastering over stone or brick masonry* — the live instrument that suspended
  СНиП II-3-79\*, not a repealed ancestor, so not ticket 25's trap. The number did
  not move, so **nothing downstream re-opened**. `pdftotext` scrambles that table,
  so the column was verified from **glyph coordinates** and the check is committed
  and reproducible. What bites hardest is the **refutation**: the finishing-works
  ladder — simple / improved / high-quality — is **flatness tolerances, not
  thicknesses**, and reading it as thickness would have shipped `t_finish` =
  1/2/3 mm, `t_int` = 122/124/126, **internally consistent all the way down with no
  gate on this map catching it.** A competing AZ number, 10 mm, is real and loses
  on **product not authority** — it is a factory panel's cast face, not laid
  masonry. ⚠️ Both corpora are **permanently** unable to corroborate a finish
  thickness: Swiss Dwellings' separator taxonomy is `WALL/RAILING/COLUMN` and
  ResPlan carries one scalar per plan. ⚠️ Leaves `t_ext_total`'s 20 mm external
  finish **unsupported on a second axis** — Əlavə 8\*'s only 20 mm row is over
  *timber*.
- [One internal thickness, against a corpus that has no module at all](tickets/33-one-internal-thickness-against-a-corpus-with-none.md)
  — **one thickness is defensible and 150 mm is nearly optimal; what it costs is the
  drawing, not the areas.** `docs/research/single-internal-thickness.md`,
  `experiments/thickness-fidelity/` (14,063 dwellings, 411 km of internal wall). The
  corpus-optimal **single** internal thickness is **146 mm** and `AZ` ships **150**,
  reached from Azerbaijani sources with no corpus involved — two traditions, 4 mm
  apart. Area drift **straddles zero** at 150; it was real and positive at the 120 ADR
  0010 replaced, which **deleted it by accident**. What it leaves behind is not a
  number but a fact: **76.1% of real dwellings draw three wall weights and a uniform
  `t_int` draws two**, which reads not as *generated* but as *drawn by someone who
  cannot tell a partition from a bearing wall* — ticketed as *One wall weight where a
  real plan draws three*. ⚠️ **Corrects ADR 0010's own partition footprint**: 4–5% is
  right for the corpus and for the 120 it replaced, and the 150 it shipped is
  **5.7%**, *wider* than the 5% gate. ⚠️ Kills the recorded justification for one
  `t_int` — *"N copies of every dimensional minimum"* is **false by count**, zero rows
  — while leaving the conclusion standing on ADR 0001 instead. ⚠️ **Swiss Dwellings
  records one plane and no finish layer**, so the corpus can never say whether it is
  structural or finished.

## Not yet specified

In scope, not yet sharp enough to ticket. Graduates as the frontier advances.

- **Interactive re-solve** (C7's deferred half) — what a Practitioner drags, what stays
  pinned, how fast the re-solve must feel. The geometry model gives it a centreline to
  drag and a Brief-anchored identity to pin against; the *interaction* is what stays fog.
- **Variant generation and ranking** — scoring is answered (the six soft rules are the
  score; the zero-survivor case is settled — diagnose arithmetically, never show a
  failing Plan). Fog is the **economics**: how many candidates are produced, survive and
  are shown, and how a Homeowner chooses. Carries one **deliberately unpatched
  asymmetry** — an invented Envelope gets 2–3 aspect ratios as a diversity axis, a
  stated one gets none, so flats get *less* variety than bungalows, backwards from where
  the demand is. Envelope jitter was rejected as the patch; the fix belongs here. **Sharpened by
  *Area measurement convention*:** the total-area gate now measures Σ Space area, not
  GIA, so an invented Envelope can no longer be sized by setting its inner area to
  `target_area` — the partition footprint, ~4–5%, is only known after the solve. How
  the Envelope is sized against that target is part of this patch and did not exist
  before ADR 0010.
- **What a corpus-shaped product looks like** — the room-count half is now a ticket. Fog
  is the rest: whether the **Brief's defaults** come from the corpus rather than the
  standards table, whether generation is **biased toward corpus-typical shapes**, and
  **what a Homeowner is told when their Brief crosses the retrieval line**. That line is
  already knowable at Brief-parse time, since retrieval's gate is a lookup — nothing yet
  says whether it should be shown.
- **Plan quality beyond the validator** — there now *is* a ranking signal (six soft
  rules, two warns, including the aspect-ratio term added because a plan can pass
  everything and still read as generated). Fog is whether it correlates with human
  judgement at all: the eval protocol, the perceptual metric, or held-out likelihood.
- **Fixtures and furniture** — do we place them, and is furniture-fit a constraint or a
  render? Two hooks exist: the ergonomic minima are **derived from fixture footprints**,
  so fixtures are already implicit in the hard set; and
  `open.wc_door_outward_pan_overlap` sits `deferred` with its 250 mm, waiting only for a
  pan to exist.
- **Angled walls** — they genuinely break the coordinate model and are genuinely v2.
  ⚠️ **Renamed from "Non-orthogonal geometry", which was two questions wearing one name.**
  An L-shaped room is *orthogonal*, and filing it here made a cheap question inherit an
  expensive deferral, so every downstream ticket inherited *one box per Room* unweighed.
  Split out as *Whether a Room may be more than one rectangle*. The Envelope's ≤2-notch
  cap is settled and measured-vindicated (ADR 0003). Carries a **deliberately unbuilt
  dependency**: room-tag-at-centroid is exact only while every Space is a rectangle.
- **Structural and services reality** — load-bearing walls, plumbing stacks, risers. The
  hook is deliberate: a wall's `load_bearing` is **unknown, not false**, and party walls
  now exist in the model still carrying `None`, so the hook is paying for something
  concrete rather than being merely prudent.
- **Frontend rendering and manipulation** — *viewing* is largely settled: Next.js/TS over
  a JSON BFF, an eager SVG preview per survivor, one `Drawing` with two presentations and
  an audience per element, so the preview is a filter and not a second annotation engine.
  Fog is **manipulation** — canvas, WebGL or SVG-in-DOM — and how it couples to C7.
- **Persistence, accounts, hosting** — where projects live, what a session is. Known
  consequence: the honest end state for a job model is a **queue plus a result store**
  with the engine a pure worker and no HTTP surface at all, deferred because the broker
  and store *are* this patch. Expect the transport to move when it clears.
- **Revit round-trip specifics** — C2 promises the engine won't preclude it. ⚠️ The
  research section that was supposed to price it **was never written**, so this patch
  currently rests on nothing.
- **The unverified solver literature** — MIP, rectangular-dual theory and `kiwisolver`,
  all `[UNVERIFIED]`. Cold while CP-SAT holds; sharpens only when C7's interactive
  re-solve is picked up.
- ~~**Whether the proposer is worth training at all**~~ — **closed**, not fog. *What the
  model proposes*: yes, and also retrieval, and the question was never exclusive.
- **The Proposal-quality floor, and how often the fallback fires** — decides whether the
  two-phase fallback is a rare safety net or a routine second solve, and therefore how
  many candidates must launch per survivor; feeds the economics patch directly. **The
  unit problem is solved** — severity, not corner noise — so both sources can be scored
  directly. Fog is the **distribution**: nobody has run a real Proposer and counted how
  many of its Proposals land past the threshold. ⚠️ One caution: the reliably fatal error
  is a **same-axis reversal**, and Gaussian corner noise — the model behind every σ
  number on this map — emits almost none, so the cliff's shape may not survive a
  generator that misplaces a room outright.
- **Whether the solve grid should be finer than 250 mm** — ⚠️ **load-bearing now, not the
  optional curiosity it was filed as.** ADR 0009 held the grid and exempted the ergonomic
  layer instead, and priced the alternatives: a 50 mm grid makes the congruence vacuous,
  a 125 mm grid still cannot represent the 1700 mm bath, and **every solver number on
  this map was fitted at 250 mm**. *Ergonomic minima* then measured the cost of staying:
  the deletion narrows to {5, and 6 unknown}, so **250 mm is charging the 5-room case** —
  the bottom of C13's band and the corpus's commonest dwelling size. Nothing published is
  snapped to 250 mm, which makes a finer grid **strictly easier to adopt later, never
  harder**. Only the solve-time side is still unmeasured. ⚠️ **And the deletion figure itself is
  now stale** — it was computed at `t_int` 120, which ADR 0010 makes 150, moving the
  residue class from 130 to 100 mod 250. Recompute before quoting it again. *One internal thickness* supplies a **partial** starting point and not a conclusion: the 120 → 150 move cost **253 solve cells either way**, so no per-room ceiling changed — but the deletion also turns on the Envelope's own re-snapping, which that arithmetic does not touch.

## Out of scope

Ruled beyond this destination. Does not graduate; returns only as a fresh effort.

- **Permit-submittable output and legal code compliance.** C8. Liability and jurisdiction
  swamp; every surveyed vendor that claimed it was doing LLM-Q&A over a user-uploaded PDF.
- **Multi-storey buildings, stair alignment across floors.** C5. The next product.
- **Multi-family, commercial, and large buildings.** C5. Massing and packing is a
  different problem from room layout.
- **Practitioner-first workflow and native Revit round-trip as a v1 requirement.** C2 —
  the engine must not preclude it, but shipping it is not on this route.
- **Commercial productisation, pricing, licensing posture.** C9.
- **Detail drawings, and material-differentiated hatching.** Ruled out by *Dimensioning
  and annotation rules*: the scale ladder tops out at 1:50 where solid poché is the
  correct convention, and a detail asserts a construction build-up this system does not
  model and C8 forbids it claiming.
- **The site: plot boundaries, setbacks, and any solar or daylight model.** Ruled out by
  *Building scope and envelope handling*. The Envelope is stated or derived from the
  programme and fixed before the solve; the Acceptance bar's window rules are
  topological, never solar. A **north angle is still stored**, used only for the north
  arrow and as a soft Brief preference.
- **A second region profile in v1, and any claim of regional *layouts*.** Ruled out by
  *Which region profiles ship in v1*. A second *standards* profile is ~30 numbers in a
  data file; a second *layout* region is a corpus that does not exist. Shipping one
  profile costs almost nothing — *implying* it brings regional layouts with it would be
  the lie. `DE`, `US` and the `IN`/`JP`/`AU`/`CN` stubs are deleted from the enum; `UK`
  survives only as a test fixture.
