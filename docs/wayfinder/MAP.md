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
| C5 | **Single-dwelling residential, single storey.** Flats and houses. |
| C6 | Acceptance bar (7 items) is a **hard filter**: generate many, reject most, show survivors. See *Acceptance validator spec*. |
| C7 | Post-generation, v1 is **edit-the-brief-and-regenerate**. Direct wall manipulation with re-solve is designed-for but deferred. |
| C8 | **Neufert-grade dimensional standards. No legal code-compliance claim, ever.** Say so in the product copy. |
| C9 | **Non-commercial project.** Research-only datasets and weights are available. Licence is not a gate; data quality and regional convention are. |
| C10 | **Model proposes, solver projects** — *amended, and the amendment is load-bearing.* The Proposal must carry **relative arrangement, not just boxes** (pairwise separations promoted to hard linear constraints), and exact tiling must be posted **soft, not hard**. The loose form — hand the solver boxes and let it project them — is **refuted by measurement**: it finds nothing at 24 rooms in 30 s. Amended, 6.25 s. A **two-phase fallback for infeasible Proposals is mandatory**. See *Solver formulation for layout projection*. |
| C11 | **Clean successor to `../plan-generator-3000-pro-max`.** No code inherited. Its findings may be reused only after independent verification. |
| C12 | Not tied to any region. Combine corpora where it can be made to work. |

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
  are our own choices. Table shipped at `data/standards/room-constraints.json`.
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

## Not yet specified

In scope, not yet sharp enough to ticket. Graduates as the frontier advances.

- **Interactive re-solve** (C7's deferred half) — what a Practitioner drags, what
  stays pinned, how fast the re-solve must feel. The geometry model is now settled
  and gives it a wall centreline to drag and a Brief-anchored identity to pin
  against; what remains vague is the interaction itself, so it stays fog.
- **Variant generation and ranking** — how many candidates are produced, how they
  are scored beyond pass/fail, how many are shown, how a Homeowner chooses.
- **Plan quality beyond the validator** — the validator gives pass/fail. What
  tells us a passing plan is *good*? Human eval protocol, perceptual metric, or
  held-out likelihood.
- **Fixtures and furniture** — Swiss Dwellings carries sinks, toilets, bathtubs.
  Do we place them, and does furniture-fit become a constraint or just a render?
- **Non-orthogonal geometry** — v1 presumably assumes orthogonal walls. When and
  how angled walls enter.
- **Structural and services reality** — load-bearing walls, plumbing stacks,
  risers. C6 item 5 gestures at wet-room clustering; the real version is larger.
  The geometry model left the hook deliberately: a wall's `load_bearing` is
  **unknown**, not false, so nothing has to be un-asserted when this is picked up.
- **Frontend rendering and manipulation** — narrowed by *Language and runtime
  split*: the stack is **Next.js/TypeScript**, it talks to the engine as a **BFF over
  JSON**, and every survivor arrives as an **eager SVG preview**, so *viewing* a plan
  is largely settled. What stays fog is **manipulation** — canvas, WebGL or
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
- ~~**Whether the proposer is worth training at all**~~ — graduated. *Proposer
  architecture survey* turned it into a decidable test in two places: *Acquire the
  datasets* now carries a blocking per-dwelling area histogram, and *What the model
  proposes* carries the beat-retrieval ablation. It is no longer fog.

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
