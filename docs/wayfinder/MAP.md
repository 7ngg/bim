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

**Domain vocabulary** (see `CONTEXT.md`):

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
  floor, and mandatory `ObjectPlacement`. Revit's IFC *import* is the weak link.
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
  Largest open risk: rooms tile exactly, real walls have thickness.
- [Cross-dataset unification](tickets/06-cross-dataset-unification.md) — **do not
  pool.** Swiss Dwellings is the backbone, ResPlan merges under a conditioning
  tag, RPLAN is demoted to optional pre-training, MSD and ProcTHOR are out.
  Condition on `(region, corpus, annotation_provenance)`. **ResPlan's real data
  contradicts its own paper on two material points** — every `[DOC]` claim is
  provisional until the corpora are opened.

## Not yet specified

In scope, not yet sharp enough to ticket. Graduates as the frontier advances.

- **Interactive re-solve** (C7's deferred half) — what a Practitioner drags, what
  stays pinned, how fast the re-solve must feel. Needs the geometry model and the
  solver formulation first.
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
- **Frontend architecture and rendering** — canvas vs WebGL, how the plan is drawn
  and manipulated in the browser.
- **Persistence, accounts, hosting** — where projects live, what a session is.
- **Revit round-trip specifics** — C2 promises the engine won't preclude it. The
  export research found Revit's IFC *import* is the weak link rather than the
  authoring (`docs/research/bim-cad-export-stack.md` §4); what that costs us is
  still unspecified.
- **Measurement convention as a first-class attribute** — minimum areas are not
  comparable across regions even after unit conversion, because German
  Wohnfläche, UK GIA and the IPMS family count differently. An area value may need
  to carry its convention everywhere it travels, which touches the geometry model,
  the Brief and the validator at once. Too diffuse to ticket yet.
- **The unverified solver literature.** *Solver formulation for layout projection*
  settled the question empirically, but its survey of MIP, rectangular-dual theory
  and `kiwisolver` died with the session and is tagged `[UNVERIFIED]` throughout.
  Low value while CP-SAT holds; it sharpens if the wall-thickness question in
  *Canonical geometry model* breaks the current formulation, or when C7's
  interactive re-solve is picked up and `kiwisolver` actually matters.
- **Whether the proposer is worth training at all** — *Cross-dataset unification*
  demoted RPLAN to "must earn its place on an ablation". The same question applies
  one level up: does a trained proposer beat retrieval, measured on
  solver-projected validator-passing output? Sharpens once the solver result lands.

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
