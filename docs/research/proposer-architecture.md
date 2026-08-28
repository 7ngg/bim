# Proposer architecture survey — findings

**Ticket:** `docs/wayfinder/tickets/18-proposer-architecture-survey.md`
**Date:** 2026-08-18
**Frame:** C10 (model proposes, solver projects — *as amended*), C9 (non-commercial;
research-only weights acceptable), C11 (clean successor; the predecessor's findings
need independent verification before reuse), C5 (single dwelling, single storey),
C12 (not tied to a region).

The spec this is measured against is the nine-item contract closing
`docs/research/solver-formulation.md`. The corpora are settled by
`docs/research/dataset-unification.md` and are taken as given.

> ### Evidence status — read this before trusting anything below
>
> | Tag | Meaning |
> |---|---|
> | `[CODE]` | Read out of the primary **source code** of the repository named, this pass. The strongest tag here. |
> | `[PAPER]` | Quoted from the **paper itself** (arXiv abstract page, ar5iv/arXiv HTML full text), this pass. |
> | `[API]` | Read from a machine API — GitHub API, arXiv API, Zenodo record. |
> | `[PRIOR]` | Carried from `docs/research/floorplan-generation-stack.md` or `dataset-unification.md` and **not re-verified this pass**. |
> | `[SIBLING]` | Measured by `../plan-generator-3000-pro-max`. Per C11 a strong prior that this pass could **not** re-run — no checkpoint and no GPU environment survives in that repo (verified: no `.venv-hd`, no `vendor/house_diffusion`, no `weights/`). |
> | `[DERIVED]` | Arithmetic I did here, from numbers tagged above. The arithmetic is shown so it can be checked. |
> | `[EST]` | An engineering estimate. Argued, not measured. |
>
> Anything that could not be established against a primary source says
> **COULD NOT CONFIRM** rather than guessing.
>
> **Quotation caveat, and it applies to every quoted sentence below.** Remote pages
> were retrieved through a fetch-and-summarise tool, not read as raw PDF. Quoted
> sentences are as that tool reported them; short quotes from `LICENSE` files and
> from source code are the most reliable, prose quotes from paper bodies the least.
> **Before any of these quotes is used in something load-bearing — a paper, a
> pitch, a contract — spot-check it against the PDF.** The numbers were
> cross-checked against a second source wherever one existed, which is why the
> room-count claims in §3 are each supported more than once.
>
> **Provenance caveat.** Most `[PAPER]`/`[CODE]`/`[API]` items were fetched by me
> directly. The graphic-layout block (§3.6, and the LayoutDM/LayoutFlow/DLT/BLT/
> LayoutFormer++/LayoutDiffusion/LayoutNUWA/LayoutPrompter rows in §4.2, §5.2 and
> §6) was gathered by a **delegated primary-source sweep inside this session**,
> which quoted a URL for every number; those URLs are in the Sources list. It is one
> hop further from the source than the rest of this document, and a reader who is
> about to spend money on the recommendation should re-read LayoutDM's configs
> personally.
>
> **Method:** where a repo's code and its README could disagree, the code was read.
> That mattered three times — HouseDiffusion's conditioning channels, MaskPLAN's
> room-count ceiling, and House-GAN++'s missing boundary input are all facts
> established from source, and two of them are not stated plainly in the papers.
> `WebSearch` quota for this session was exhausted early (200/200, mostly by
> parallel sub-agents), so discovery after that point used the **arXiv API**,
> **GitHub API** and **Zenodo** directly, which are primary sources anyway.

---

## Verdict

**Do not train HouseDiffusion, and do not train a HouseDiffusion successor in its
published form. Train a room-set transformer that emits one box per Brief room.**

The reason is not that HouseDiffusion is bad — it is the strongest thing in its
own lineage. The reason is that the contract in *Solver formulation* asks for an
input it cannot take, and pays a heavy price for an output property it then
discards:

- It cannot be conditioned on an **Envelope**. Its conditioning vector is 89
  channels wide and is `25 room-type + 32 corner-index + 32 room-index` — there is
  no boundary input anywhere in the model `[CODE]`. Our Brief always carries an
  Envelope, and for a flat that Envelope is *given* and non-rectangular.
- Its headline contribution — exact corner incidence and non-Manhattan polygon
  loops — is **thrown away** by our pipeline. The solver re-derives every
  coordinate on a 250 mm integer grid and only reads the boxes' implied pairwise
  ordering. We are paying a 1000-step sampler for geometric precision that the
  next stage overwrites.
- Independent published evidence says the polygon representation is actively
  *worse* at our room counts: the one published attempt to run this architecture
  on Swiss-Dwellings-derived plans found that **"a data processing procedure that
  simplifies all room polygons to rectangles leads to better performance"**, and had
  to discard ~1,000 training samples "for having too many rooms, to lower GPU
  memory needed" `[PAPER]` (Kuhn, arXiv 2312.03938). And on the one published
  benchmark that sits at our room count — MSD, 15–50 areas, peak ~25 — a
  **Modified HouseDiffusion scores 11.5–21.8 mean MIoU against a plain raster
  U-Net's 40.6–42.4** `[PAPER]`. (Those two are one line of work, not two: Kuhn
  co-authored MSD. See the counting caveat in §3.3.)

What replaces it is smaller, cheaper and better-fitted, and the survey below
shows the field itself has largely moved there.

**But the finding that should change the plan is not about architecture at all:**

> **The 24-room case is out of distribution for every corpus, not just for every
> model.** Swiss Dwellings as actually used in published work is **~5k plans with a
> mean of 6.20 rooms** `[PAPER]`; ResPlan averages **8.1 functional rooms**
> `[PAPER]`; RPLAN's maximum is **8** `[PAPER]`; the synthetic corpus that transfers
> best generates **2–10 rooms, mean 4.42** `[PAPER]`. No architecture choice fixes
> that. Only data does.

---

## 1. The candidate set — what actually shipped, 2020–2026

### 1.1 Three lineages, and where each one ends

The prior pass (`floorplan-generation-stack.md` §4.3) read the trend as three
replacements for raster generation: native vector diffusion, LLMs over a
structured representation, and explicit wall/junction graphs. That reading holds
up against an arXiv API sweep run this pass (40 newest hits for
`abs:"floorplan generation" OR abs:"floor plan generation"`, `[API]`) — every
paper it lists exists, with the ids and dates it gives. What the prior pass does
not do, because it was written for a different question, is separate the
candidates by **what they let you ask for**. That is the axis that decides this
ticket, and it cuts the field in half (§2).

| Lineage | Members | Where it ends for us |
|---|---|---|
| **Graph-conditioned generators** (bubble diagram in, per-room geometry out) | House-GAN (ECCV 2020), House-GAN++ (CVPR 2021), HouseDiffusion (CVPR 2023), ChatHouseDiffusion (2024), MaskPLAN (CVPR 2024) | The right *shape* — one output per requested room, identity preserved. This is the lineage to take. All of them except MaskPLAN refuse an Envelope. |
| **Boundary-conditioned generators** (footprint in, rooms invented) | WallPlan (2022), GSDiff (AAAI 2025), DiffPlanner (TVCG 2025), TLC-Plan, Alpha-to-Omega, Boundary-Constrained Diffusion, GFLAN, FloorplanMAE, Unit Region Encoding | **Disqualified as-is.** They invent the room programme; our Brief fixes it. Retrofitting a programme input is a redesign, not a config change. |
| **Autoregressive sequence models over a symbolic representation** | FloorGenT (2022, "vector floorplans as token sequences" `[API]`), Tell2Design (ACL 2023), DStruct2Design (2024), HouseTune (2024), **FloorPlan-DeepSeek** (2025, "next room prediction", reported "competitive … in comparison to diffusion models and Tell2Design" `[PAPER]`), floor-plan RLVR (ACL 2026), HypergraphFormer (2026) | The *representation* is right — rooms as tokens — and the graphic-layout branch of this same family (LayoutTransformer, LayoutFormer++) is where §3.6 leads. The **LLM-sized** members are live as a v1 baseline and as the Brief parser we already have (C4), but are weak on metric proportion and too large to train or serve here (§4.2). |
| **Non-learned** | rectangular duals / DPLAN, squarified treemaps, MIQP layout | Now the *solver's* job, not the proposer's. C10 already bought this. |

### 1.2 What the current state of the art actually is

Two 2026 works are the honest answer to "what is the state of the art", and
neither is a diffusion model over polygons:

- **Ospici, Gueze, Bourrat & Bernhardt**, *Mitigating Domain Shift in Conditioned
  Floor Plan Generation* (arXiv 2607.06483, July 2026). Trains **DPFM**, an
  arrangement model that "predicts rigid transformations of input polygons",
  treating layout generation as "a set of rigid transformations predicting the
  translation and rotation of input polygons", with **flow matching**; and a
  vertex-level constraint diffusion model that "operates at the vertex level,
  diffusing all polygon points simultaneously while reconciling local shapes with
  global graph constraints via cross-attention" `[PAPER]`. Trained on **NVIDIA H100
  GPUs**, "fine-tune for a fixed 50k steps across all setups" `[PAPER]`.
- **HypergraphFormer** (arXiv 2605.18932, Autodesk Research), "a novel and
  efficient approach to floor plan generation based on learning hypergraph
  representations with a large language model (LLM)" `[PAPER]`, conditioned on
  user-specified boundaries and constraints for irregular footprints, trained on
  RPLAN plus an out-of-distribution set the authors release. Model name/size,
  room counts and costs: **COULD NOT CONFIRM** — not stated on the abstract page,
  and no code URL is published `[PRIOR]`.

The first of those is the more useful result for us and is discussed throughout;
the second is a signal about where a well-resourced incumbent landed, not a
usable artifact.

### 1.3 Corrections to `docs/research/floorplan-generation-stack.md`

That document is accurate on the facts I re-checked. Three things need saying
anyway, and one is a correction rather than a reframing.

1. **Its decisive axis no longer applies.** It is explicitly *"Research note for a
   **commercial** product. The decisive axis throughout is licence / commercial-use
   terms"*. Under **C9** that axis is retired — the same retirement
   `dataset-unification.md` §1.1 already applied to the datasets now applies to the
   models. Every ❌ in its model table that reads "research only" or "non-commercial"
   is **no longer a blocker**. What survives is C11: we reimplement rather than
   inherit, so *code* licences matter mainly for how freely we may read.
2. **"Zero of ~20 published generators emit walls with thickness" is true and is
   now irrelevant to this ticket.** *Canonical geometry model* moved wall thickness
   into the solve domain, and the Proposal contract's item 7 explicitly says the
   Proposal carries **no wall geometry**. The prior doc's framing — "you are
   shopping for a room-topology proposer" — was right, and this ticket is the
   consequence of it.
3. **Correction: it names HouseDiffusion "the strongest architecture on the list".**
   Against *this* contract it is not, and the reasons are specific and verifiable
   (§2.2, §3.3). I believe the correction rather than the original because the
   original was ranking on vector-output fidelity, which the solver overwrites,
   and because it did not check the conditioning channels in the code.

---

## 2. Which of them can be conditioned on a Brief

### 2.1 What the Brief actually asks the model to accept

From `CONTEXT.md` and the closed tickets, the conditioning surface is:

| Field | Source | Mandatory? |
|---|---|---|
| **Room set with types and identities** | Brief | Yes — contract item 1 fixes it |
| **Target area per room** | Brief (or an Assumption) | Yes — it is most of what "proportion" means |
| **Envelope polygon** | Given for a flat, invented for a house | Yes for flats; the hard case is non-rectangular |
| **Entry / front door** | Brief | Yes — the solver's circulation flow starts there |
| **Required adjacencies** | Brief | As *soft* conditioning only |
| **Forbidden adjacencies** | Brief | **No** — contract item 6 forbids it entering the Proposal |
| **`(region, corpus, annotation_provenance)`** | `dataset-unification.md` §6.3 | Yes — this is the model's whole job |
| **Orientation** | Brief, often an Assumption | Desirable; Swiss Dwellings can teach it (`+y` is north `[API]`), RPLAN cannot |
| **Partially fixed rooms** | C7's deferred re-solve, and pinning | Desirable, not v1-blocking |

Two of these lines are worth pausing on, because they invert the usual reading of
the literature.

**Forbidden adjacency is not a gap.** Graph2Plan's own limitations section lists
the absence of forbidden constraints as a known weakness `[PRIOR]`, and the prior
research pass treats that as a mark against the learned route. Under C10 as
amended it is not: forbidden adjacency is a **hard solver constraint**
(`contact_ij == 0`, measured, 22 of them at 24 rooms with no difficulty) and the
Proposal contract explicitly says a model-emitted graph "must never enter the
constraint set". **The one thing the whole learned field cannot express is the one
thing we must not ask it for.**

**Target area is the gap nobody covers.** Of everything surveyed, exactly one
published system takes per-room target areas as a first-class conditioning input
(MaskPLAN, `area_mask` `[CODE]`), and one takes areas but no boundary
(FloorplanGAN `[PRIOR]`). Yet a Homeowner's Brief is *mostly* areas, and
proportion is half of what the Proposal contributes. Any architecture we adopt has
to add this input, and none of the published training recipes tells us how well it
is learned.

### 2.2 The conditioning interface of each candidate

Read from source where the source exists; from the paper where it does not.

| Model | Envelope | Room set fixed by the caller | Types | Target areas | Adjacency | Entry | Partial layout | Evidence |
|---|---|---|---|---|---|---|---|---|
| **House-GAN** (ECCV 2020) | ❌ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | `[PAPER]` — input is "a bubble diagram … nodes encode rooms with their room types and edges encode their spatial adjacency" |
| **House-GAN++** (CVPR 2021) | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ (door nodes) | ✅ (previous layout) | `[CODE]` — `test.py` builds only `z, given_masks_in, given_nds, given_eds`; **no boundary tensor exists** |
| **HouseDiffusion** (CVPR 2023) | ❌ | ✅ | ✅ (10 types) | ❌ | ✅ | ✅ (door loops) | ❌ | `[PAPER]` + `[CODE]` — `condition_channels=89` = 25 type + 32 corner-index + 32 room-index; no boundary channel |
| **Graph2Plan** (SIGGRAPH 2020) | ✅ raster + front door | ✅ (via retrieval + edit) | ✅ | ❌ | ✅ | ✅ | ❌ | `[PAPER]` |
| **MaskPLAN** (CVPR 2024) | ✅ (`bound_input`) | ✅ | ✅ | ✅ (`area_mask`) | ✅ (`ada_mask`) | ✅ (`door_input`) | ✅ **any subset** | `[CODE]` — the encoder takes `type_mask, loc_mask, ada_mask, area_mask, room_mask, bound_input, door_input` |
| **WallPlan** (SIGGRAPH 2022) | ✅ | optional | optional | ❌ | optional | ✅ | ❌ | `[PRIOR]` |
| **GFLAN** (2025/26) | ✅ | ❌ **invents the programme** | ❌ | ❌ | ❌ | ✅ | ❌ | `[PAPER]` — "single exterior building boundary" + front-door location |
| **GSDiff / DiffPlanner / TLC-Plan / Alpha-to-Omega / Boundary-Constrained Diffusion** | ✅ | ❌ **invent the programme** | ❌ | ❌ | ❌ | varies | ❌ | `[PAPER]`/`[PRIOR]` |
| **Tell2Design** (ACL 2023) | ✅ (enclosing box) | via text | via text | via text | via text | ✅ | ❌ | `[PRIOR]` |
| **DStruct2Design / floor-plan RLVR** | ✅ (numeric) | ✅ | ✅ | ✅ (numeric constraints) | ✅ | ✅ | ✅ | `[PRIOR]` |
| **Ospici DPFM** (2026) | **COULD NOT CONFIRM** | ✅ (it transforms *given* polygons) | ✅ | implicit in the given polygon | ✅ (graph constraints) | ✅ | ✅ | `[PAPER]` |

**The intersection that satisfies the Brief — accepts an Envelope *and* a
caller-fixed room programme — has exactly four members: Graph2Plan, MaskPLAN,
WallPlan and the LLM/structured line.** Two of those four are retrieval-or-raster
pipelines from 2020–22, one is capped at 8 rooms in its released form (§3), and
one is an LLM.

That is the survey's core negative result, and it is not a licensing result or a
quality result: **the published field mostly does not accept the input we have.**
The models that best match our *output* contract (House-GAN++, HouseDiffusion)
are exactly the ones that cannot take an Envelope, and the models that take an
Envelope mostly refuse to take a programme.

### 2.3 What that implies

Adding Envelope conditioning to a graph-conditioned transformer is not research —
it is a cross-attention block, and the 2026 literature has already named it
(*Boundary-Constrained Diffusion Models*, arXiv 2602.01949: "a Boundary
Cross-Attention (BCA) module that enables conditioning on building boundaries"
`[PAPER]`; Kuhn's MSD adaptation added "cross-attention operation between each
room corner and all structural corners" `[PAPER]`). So the practical conclusion is
that **we are building a room-set transformer with envelope cross-attention
whichever paper we start from**, and the choice between papers is a choice of
generative head and tokenisation, not of conditioning.

---

## 3. Which of them hold up at 24 rooms

### 3.1 What the literature actually reports, by room count

This is the ticket's item 3, and the answer is blunter than expected.

| Work | Corpus | Room counts trained / evaluated | Evidence |
|---|---|---|---|
| **House-GAN** (2020) | LIFULL, 117,587 plans | **"We divide the samples into five groups based on the room counts (1-3, 4-6, 7-9, 10-12, and 13+)"** — the 13+ group holds 8,764 samples | `[PAPER]` |
| **House-GAN++** (2021) | RPLAN | "dividing the samples into four groups based on the number of rooms: (5, 6, 7, 8)" — **max 8** | `[PAPER]` |
| **HouseDiffusion** (2023) | RPLAN, 60,000 plans | four groups: **5, 6, 7, 8 rooms**; each group held out from training in turn | `[PAPER]` |
| **Graph2Plan** (2020) | RPLAN | "8" is "the maximal number of nodes (rooms)" | `[PAPER]` |
| **MaskPLAN** (2024) | RPLAN | adjacency array is `np.zeros((80788, 8, 8))`; sequences are padded to 10 = **8 rooms + BEGIN + END** | `[CODE]` |
| **Ospici et al.** (2026) | RPLAN / MagicPlan / **Swiss Dwellings** | means of **6.84 / 5.63 / 6.20 rooms**; SD reduced to "approximately 5k floor plans" by filtering | `[PAPER]` |
| **ResPlan** (2025/26) | ResPlan, 17,000 | **8.1 functional rooms** per plan on average, 9.2 graph nodes | `[PAPER]` |
| **Kuhn** (2023) | MSD (Swiss-Dwellings-derived) | MSD has "many more rooms per floor plan"; **~1,000 samples discarded "for having too many rooms, to lower GPU memory needed"**; 3,804 training samples | `[PAPER]` |
| **MSD benchmark** (ECCV 2024) | Swiss-Dwellings-derived **floor plates** | "MSD comprises mostly floor plans that have between 15 and 50 areas, **with a peak of around 25**" — and it runs generative baselines there (§3.5) | `[PAPER]` |
| **Synthetic pre-training corpus** (Ospici) | generated | "between 2 and 10 per scene", **mean 4.42 rooms**, 135k scenes | `[PAPER]` |

So: in the *dwelling* literature, **one published quantitative result exists above
12 rooms** — House-GAN's `13+` group on LIFULL, a 2020 GAN emitting 32×32 masks
that are then fitted with axis-aligned rectangles. Everything published since 2021
sits at **5–8 rooms**, and it sits there because RPLAN sits there. The one
benchmark that *does* sit at ~25 areas is MSD, and §3.5 is what it measured.

### 3.2 The ceiling is a dataset artefact, and it follows us home

House-GAN handled a `13+` bucket in 2020 with a much weaker architecture than
anything current. The field's ceiling then *dropped* to 8 when it standardised on
RPLAN, whose maximum is 8. That is worth stating plainly because it kills the
tempting inference "diffusion models cannot do 24 rooms": nobody has published the
experiment, on any architecture, on a residential dwelling corpus, because no such
corpus exists.

And the corpus problem is ours too. `dataset-unification.md` fixed the corpora
before this ticket ran, and those corpora are:

- **Swiss Dwellings** — 45,176 apartments / ~370,000 rooms / ~520,000 areas
  `[API]`, i.e. **≈8.2 rooms and ≈11.5 areas per apartment on average**
  `[DERIVED]`. The only independent measurement of what survives real filtering is
  Ospici's: ~5k plans, **mean 6.20 rooms** `[PAPER]`.
- **ResPlan** — mean 8.1 functional rooms `[PAPER]`.

The 24-room case in the solver study is a **232.8 m² interior with 24 rooms**.
Nothing in the plan's corpora is shaped like that in quantity. Whether Swiss
Dwellings' *tail* holds enough ≥16-area dwellings to train on is
**NOT ESTABLISHED** and cannot be established until ticket 12 opens the data. It
is the single highest-value query in that ticket, and it is one line:

```sql
-- per-dwelling area counts, residential only, single floor
SELECT n_areas, COUNT(*) FROM (
  SELECT site_id, apartment_id, COUNT(*) AS n_areas
  FROM geometries WHERE entity_type='area' AND unit_usage='RESIDENTIAL'
  GROUP BY site_id, apartment_id
) GROUP BY n_areas ORDER BY n_areas;
```

Until that histogram exists, **every claim in this document about 24-room
behaviour is a claim about extrapolation, not about training.**

### 3.3 The predecessor's 24-room result — what I could verify, and what I could not (C11)

The ticket flags the sibling project's numbers as a strong prior needing
independent verification. Here is the honest accounting.

**Could not re-run it.** `../plan-generator-3000-pro-max` no longer carries the
environment: no `.venv-hd`, no `vendor/house_diffusion`, no `weights/model.pt`
(verified on disk this pass). The overlap figures — 8 rooms 5.8–12.8 %, 12 rooms
21.0–27.7 %, 24 rooms **35.8–66.8 %**, and repair recovering 31 % / 7 % / 0 % —
therefore remain `[SIBLING]` and **unverified here**.

**Verified independently, from primary sources, the structural facts that make
those numbers plausible:**

| Sibling claim | Independent check |
|---|---|
| "The 100-corner budget is the real ceiling … at 4 corners per room the practical maximum is 25 rooms" | `max_num_points = 100` in `rplanhg_datasets.py`, and the padded layout shape is `(100, 94)` `[CODE]` |
| "24 rooms vs 5–8 trained" | The paper's own protocol is four groups of **5, 6, 7, 8 rooms** `[PAPER]` |
| "A 24-room villa costs exactly the same memory as an 8-room flat" | The conditioning tensor is fixed-size `(100, 94)` regardless of programme `[CODE]` — the sibling's constant 113–160 MiB is exactly what that predicts |
| RPLAN room-type vocabulary is tiny | The one-hot is 25-wide in the loader `[CODE]`; the sibling's "nine usable types" is a claim about which ids are *populated*, which I could not check without the data — **COULD NOT CONFIRM** |
| "31-room limit" | The room-index one-hot is 32-wide `[CODE]`, so 32 is the architectural cap on rooms in the conditioning |

**Independent corroboration from a different research group.** Kuhn (arXiv
2312.03938) took the same architecture to Swiss-Dwellings-derived floor plans and
reported, unprompted, the same failure direction:

- **"especially in cases of many smaller rooms, the rooms do not align together
  very well"** `[PAPER]`;
- discarding ~1,000 samples "for having too many rooms, to lower GPU memory
  needed" `[PAPER]`;
- and, decisively for us, that **"a data processing procedure that simplifies all
  room polygons to rectangles leads to better performance. This indicates that
  future work should explore better representations of variable-length polygons in
  diffusion models"** `[PAPER]`.

The MSD benchmark's own Modified HouseDiffusion baseline (§3.5) points the same
way — **11.5–21.8 MIoU** at ~25 areas against a raster U-Net's **40.6–42.4**
`[PAPER]`.

> **Do not count that as a third source.** Emanuel Kuhn is a **co-author of the MSD
> benchmark paper** (author list read from the arXiv API `[API]`), so the technical
> report and the MSD baseline are one line of work with two publications, not two
> independent replications. The honest count is **two independent bodies of
> evidence**: the sibling project's measurements, and the Kuhn/MSD line.

So the prior stands directionally, from two independent sources, and the mechanism
is now legible: a corner-sequence representation spends capacity on polygon shape,
and at high room counts that is capacity taken from arrangement.

**One correction to the prior, in fairness to it.** The sibling's 24-room fixture
is not a clean room-count experiment. Its own breakdown says the villa lost
**75 % vocabulary, 21 % conditioning, 4 % training regime**, and that the brief was
*two storeys flattened into one footprint* with a detached studio placed inside the
envelope `[SIBLING]`. Two storeys competing for one footprint **guarantees**
overlap independently of room count. So `35.8–66.8 %` is best read as "a
two-storey, out-of-vocabulary, out-of-distribution brief pushed through a
5–8-room RPLAN checkpoint", not as "HouseDiffusion at 24 rooms". Under C5 the
storey confound disappears, and with our own vocabulary the type confound
disappears. **The direction is well-evidenced; the magnitude is confounded and
should not be quoted as a room-count degradation curve.**

### 3.4 What the solver forgives, and what it does not

This is the part that changes what "holds up at 24 rooms" even means, and it must
be said explicitly because the predecessor's metric no longer applies.

**Forgiven — measured in `solver-formulation.md`:**

- **Overlap.** 2.2–8.3 % of proposed room area overlapping was repaired to a valid
  plan at all three sizes. The Proposal "appears only in the objective and in the
  solution hint. It never appears in a constraint."
- **Unassigned floor.** 21.6–26.8 % of the interior left unassigned by the
  Proposal — repaired.
- **Boxes outside the Envelope**, violated minimum dimensions, contradicted
  adjacencies, and "no validity guarantee whatsoever".
- **A totally uninformative Proposal**, at ≤12 rooms: every room collapsed to a
  1×1 box at the origin still returned a fully valid plan in 0.17 s / 0.59 s.

**Not forgiven:**

- **A wrong arrangement.** The "shuffled" Proposal — correct boxes, wrong rooms —
  makes the model **INFEASIBLE in 0.02–0.08 s** at all three sizes. The mandatory
  two-phase fallback then drops the relations, which at 24 rooms means falling back
  into the configuration that finds *nothing in 30 s*.
- **An uninformative Proposal at 24 rooms.** Degenerate Proposal, 24 rooms:
  `UNKNOWN`, no plan in 30 s. "A worthless Proposal costs you the 24-room case
  entirely."
- **Ambiguity.** The solver extracts a relation per pair from the *cheapest* of
  four separations, and discards pairs "whose four separation costs are near-equal".

Put those together and a specific pathology emerges that the overlap metric hides.
The sibling measured `worst_pair_overlap` at **100 % in 10 of 12 plans, including
three of four in-distribution 8-room plans** — i.e. at least one room drawn
*entirely inside* another `[SIBLING]`. A fully-nested pair has near-equal
separation costs in every direction, so it contributes **no relation at all**.
Nesting is therefore far more damaging under this contract than its contribution to
an aggregate overlap percentage suggests, while ordinary edge-crossing overlap is
nearly free.

> **Consequence for evaluation, and it is the whole ticket in one line:**
> **stop measuring overlap.** The quantity that predicts whether a Proposal
> survives is *per-pair separation-direction agreement with the ground truth,
> weighted by the confidence margin the solver uses to decide whether to fix the
> relation* — plus the fraction of pairs that can be fixed without closing a cycle.
> Overlap % is a proxy that was correct for the predecessor's rejection-based
> pipeline and is the wrong instrument for a projection-based one.

### 3.5 The one benchmark that measured at our room count — and what it found

MSD (van Engelenburg et al., ECCV 2024) is Swiss-Dwellings-derived and sits at
**15–50 areas, peak ~25** `[PAPER]`. It runs two generative baselines, and one of
them is **Modified HouseDiffusion**. The numbers, quoted from the paper `[PAPER]`:

| Baseline | Mean MIoU |
|---|---|
| Graph-informed U-Net | **40.6** |
| Graph-informed U-Net (preprocessed) | **42.4** |
| **Modified HouseDiffusion** | **11.5** |
| **Modified HouseDiffusion + wall cross-attention** | **21.8** |

alongside the paper's own *"the average MIoU ranges from 10.9 to 42.4"* and
*"the MIoU scores for larger floor plans are comparable across the three methods,
which suggests that the GCN struggles with larger graphs"* `[PAPER]`. Every number
in that band is low; the characterisation "weak across the board" is mine, not the
authors'.

Read that table next to §3.1. **The architecture that wins at 5–8 rooms is beaten
roughly two-to-one by a plain raster U-Net once the plan has ~25 areas.** That is a
group entirely independent *of the sibling project*, on a different corpus, with a
different metric and a different failure description — pointing the same way. It is
**not** independent of Kuhn's report (§3.3): same authors, one line of work.

Two honest caveats, so this is not over-read:

- MSD floor plans are **multi-apartment floor plates**, which C5 filters away. The
  room count is right; the object is not a dwelling.
- **MIoU is not our metric.** Under C10 a Proposal is not scored on pixel overlap
  with a ground-truth plan at all (§3.4). A low MIoU with the *arrangement* right
  would be perfectly acceptable to us, and nothing in that table separates the two.

So MSD does not prove a HouseDiffusion-class model fails at 24 rooms *for our
purpose*. What it does establish is that **the published evidence at our room
count, on our corpus family, is uniformly weak, and weakest for the architecture
the predecessor chose.**

### 3.6 The literature that *does* routinely do 24 elements is not the floorplan literature

The Proposal contract asks for exactly this task: **given a fixed set of typed
elements, produce one axis-aligned box each, inside a canvas.** That task has its
own literature — conditional *graphic layout* generation — where it is called
**C→S+P** ("category to size and position"), and it handles our element count as a
matter of routine.

| Model | Max elements | Params | Sampling | Licence | Evidence |
|---|---|---|---|---|---|
| **LayoutTransformer** (ICCV 2021) | **128** — "covers over 99.9% of the layouts" | ~12.7–19M | autoregressive | COULD NOT CONFIRM | `[PAPER]` |
| **BLT** (ECCV 2022) | **25** (RICO) / 22 (PubLayNet) | ~12.7M | non-autoregressive, ~T/3 ≈ 9–12 iterations | COULD NOT CONFIRM | `[PAPER]` |
| **LayoutDM** (CVPR 2023) | **25** | **12.4M** (4 layers, d=512, 8 heads) | discrete diffusion, T=100 | **Apache-2.0, weights released** | `[PAPER]` + `[CODE]` (`max_seq_length: 25`) |
| **LayoutFormer++** (CVPR 2023) | 20 | ≈59M `[DERIVED]` | autoregressive + constrained decoding | MIT, weights released | `[PAPER]` + `[CODE]` |
| **LayoutDiffusion** (ICCV 2023) | 20 | 86M | discrete diffusion, T=200/160 | MIT, weights released | `[PAPER]` |
| **LayoutFlow** (ECCV 2024) | 20 | 12.7–15M | flow matching, 50 steps | MIT, weights released | `[PAPER]` + `[CODE]` |
| **DLT** (ICCV 2023) | **10** | ~9.0M | 100 continuous + 10 discrete steps | Apache-2.0, no weights | `[PAPER]` + `[CODE]` |
| **LayoutNUWA** (ICLR 2024) | 25 | **7B** | autoregressive LLM | MIT, no fine-tuned weights | `[PAPER]` |
| **LayoutPrompter** (NeurIPS 2023) | ~20 (inherited splits) | **none — training-free** | 10 LLM samples + ranker | MIT | `[PAPER]` + `[CODE]` |

BLT states our task verbatim: *"Conditional on Category: only object categories are
given by users. The model needs to predict the size and position of each object"*
`[PAPER]`.

Two things follow, and they are the reason this section exists.

1. **24 boxes is not a hard problem for a transformer.** It is the *standard*
   problem size in an adjacent field, solved at **12M parameters** with
   **25-element** context, with released Apache-2.0 code and weights. The
   floorplan field's 8-room ceiling is not evidence that 24 is hard; it is
   evidence that RPLAN has 8 rooms.
2. **These caps are dataset filters, not architecture limits** — and the same
   filtering pathology we have. The median RICO layout has **36 elements**
   `[PAPER]`, yet the standard cap is 20–25, so *these models are also trained on
   the short tail of their own corpus*. LayoutDM's ≤25 filter takes RICO from 66k
   screens to 35,851 training layouts `[PAPER]`. The field we are borrowing from
   has the identical blind spot, for the identical reason, and knows it.

---

## 4. Training cost on Swiss Dwellings, on hardware this project plausibly has

### 4.1 The hardware envelope

Two machines are evidenced in this project's own history: a **4-core Ivy Bridge
desktop** (the solver measurements) and an **RTX 3060 Laptop, 6.0 GiB**
(`[SIBLING]`, the HouseDiffusion runs). Ticket 08 adds the free tiers: Kaggle
**~30 h/week of T4×2 or P100**. Everything below is sized against a **6 GB
consumer GPU** and a **16 GB T4**, because if a candidate does not fit those, it
is not a candidate.

### 4.2 What the reference implementations actually cost

Published training configurations, so the estimates below are anchored rather than
invented:

| Reference | Data | Schedule | Hardware | Wall-clock |
|---|---|---|---|---|
| **LayoutTransformer** | COCO, 118,280 layouts, 30 epochs | Adam, lr 1e-4 | **single GTX 1080** | **"about 6 hours"** `[PAPER]` |
| **LayoutDM** | RICO 35,851, 50 epochs (PubLayNet 315,757, 20 epochs) | batch 64, AdamW lr 5e-4 | single GPU (model unstated) | COULD NOT CONFIRM |
| **LayoutFlow** | RICO ~66k | batch 512, up to 1000 epochs | "a single GPU" | COULD NOT CONFIRM |
| **LayoutDiffusion** | RICO | 175,000 steps, batch 64, 2 GPUs | unstated | COULD NOT CONFIRM |
| **HouseDiffusion** | RPLAN 60k | **250,000 steps at batch 512**, lr 1e-3 ÷10 every 100k | **single NVIDIA RTX 6000** | COULD NOT CONFIRM `[PAPER]`+`[CODE]` |
| **Kuhn (HouseDiffusion → MSD)** | **3,804 samples** | ~340,000 steps at batch 32 | unstated | COULD NOT CONFIRM `[PAPER]` |
| **Ospici (2026 SOTA)** | 135k synthetic + ~5k SD | 50,000 fine-tune steps | **NVIDIA H100** | COULD NOT CONFIRM `[PAPER]` |
| **LayoutNUWA** (the LLM route) | RICO/PubLayNet | 10 epochs, LLaMA-2-7B | **64× V100 (8×8 nodes)** | COULD NOT CONFIRM `[PAPER]` |

The spread across that table *is* the finding. The same task — boxes from
categories — costs **6 GPU-hours on a 2016 gaming card** at one end and **64
V100s** at the other, and the quality difference on the shared benchmark is not
64×: LayoutPrompter (training-free, GPT-3.5 + retrieval) scores RICO Gen-T
mIoU **0.429** against LayoutFormer++'s **0.432** `[PAPER]`.

For reference, **HouseDiffusion is itself a small model** — the size gap is not
what separates it from the recommendation. From its code `[CODE]`: `num_channels =
512` for RPLAN, `self.num_layers = 4`, 4 heads, `FeedForward(d_model, d_model*2)`,
and **three** `MultiHeadAttention` blocks per layer (`self_attn`, `door_attn`,
`gen_attn`). That gives `4 × (3 × 4d² + 2 × 2d²) = 4 × 4.20M ≈ 16.8M`, plus
embeddings, time-embedding and output heads ≈ **19M parameters** `[DERIVED]`. Its
cost is entirely in the **1000 denoising steps** and the **250k × 512 training
schedule**, not in its width.

### 4.3 What our run would cost

Sizing a LayoutDM-class model for our task: **~24 room tokens + ~64–96 envelope
tokens ≈ 128 sequence positions**, `d = 512`, 4–8 layers → **12–25M parameters**
(anchored on LayoutDM's 12.4M at 4×512 and LayoutFormer++'s ≈59M at 16×512).

**Dataset volume.**

| Source | Records | Status |
|---|---|---|
| Swiss Dwellings, C5-filtered dwellings | **NOT ESTABLISHED** — nominal 45,176 apartments `[API]`; the only published filtering result is Ospici's ~5k *plans* `[PAPER]` | ticket 12 |
| ResPlan, deduplicated | ~15,800 `[PRIOR]` | ticket 12 |
| Synthetic pre-training, generated by us | 135k scenes is the published recipe's volume `[PAPER]` | free, no dependency |

**Compute, shown as arithmetic** `[DERIVED]`:

```
params            N  = 2.0e7
tokens/sample     T  = 128
train samples     S  = 2.0e4  (SD + ResPlan, mid estimate)
epochs            E  = 300    (a masked-token objective wants many passes)
presentations     P  = S*E                    = 6.0e6
training FLOPs    F  = 6*N*T*P = 6*2e7*128*6e6 = 9.2e16  (92 PFLOP)
T4 effective throughput, small model, fp16     ≈ 5e12 FLOP/s   [EST]
wall-clock                                      ≈ 5.1 hours
```

Cross-check against the one published wall-clock: LayoutTransformer did 3.5M
presentations of a ~13–19M model in **6 h on a GTX 1080**. Our 6.0M
presentations of a 20M model on a T4 (roughly 2–4× a GTX 1080 in mixed precision)
lands in the same **5–15 hour** band. Add synthetic pre-training (135k scenes ×
~50 epochs ≈ 6.8M presentations) and the whole recipe is **~10–25 GPU-hours**.

**That fits inside one week of Kaggle's free tier with a factor of ~2 to spare,
and it fits on the 6 GB laptop card.**

**VRAM floor** `[DERIVED]`:

```
optimizer state   20M params x (4 grad + 4 param + 8 Adam) B  = 320 MB
activations       B*T*d*layers*~20*4B, at B=64, T=128, d=512, L=8
                  = 64*128*512*8*20*4                        ≈ 2.7 GB  (fp32)
                  ≈ 1.3 GB in bf16, or 0.7 GB at batch 32
attention maps    B*heads*T^2*4B = 64*8*16384*4              ≈ 34 MB/layer
```

→ **VRAM floor ≈ 2 GB in fp32 at batch 64, under 1 GB in bf16 at batch 32.**
Fits the 6 GB RTX 3060 Laptop; fits a T4/P100 with the batch turned up.

**The trained fallback costs about 16× more.** A HouseDiffusion-class
corner-diffusion model at its published schedule is 250k steps × batch 512 =
**1.28e8 presentations** `[PAPER]` over 100-token sequences at ≈19M params:

```
6 * 1.9e7 * 100 * 1.28e8 = 1.46e18 FLOP  (1,460 PFLOP)  = 16x our budget
at 5e12-1e13 FLOP/s  ->  40-80 GPU-hours on a T4, call it 40-150 with slippage
```

`[DERIVED]` — **1.5–5 weeks of Kaggle's free tier, or under a day of rented
A100/H100 time.** Ospici's 2026 work uses H100s `[PAPER]`, which tells you what
that lineage now assumes. Note this is a cost you pay *before* you learn whether
it beat retrieval.

**The LLM route is out on training cost alone.** LayoutNUWA fine-tunes a 7B model
on **64 V100s** for the identical C→S+P task `[PAPER]`; floor-plan RLVR's released
weights are `Llama3.3-70B`-based `[PRIOR]`. Neither is trainable here, and §5
shows neither is servable here either.

---

## 5. Inference cost per Proposal

### 5.1 The budget

Per the ticket: one proposer call plus a **6.25 s solve** per candidate, times N
candidates. So the question is not "is the proposer fast" but "what fraction of
the plan budget does it eat".

### 5.2 Measured and published numbers

| Route | Latency per Proposal | Memory | Source |
|---|---|---|---|
| **LayoutFlow** (12.7M, 50 steps) | **1.75 ms** | — | `[PAPER]`, third-party benchmark table |
| **DLT** (9M) | **3.50 ms** | — | `[PAPER]`, same table |
| **LayoutDM** (12.4M, T=100) | **16.6 ms** | — | `[PAPER]`, same table |
| **LayoutDiffusion** (86M, T=200) | **1600 ms** | — | `[PAPER]`, same table |
| **Graph2Plan** (retrieval + refine) | **<0.4 s** — 99 ms retrieval + 11 ms transfer + 68 ms generation + 200 ms post-process | — | `[PAPER]` |
| **HouseDiffusion** (≈19M `[DERIVED]`, T=1000) | **24.1 s** at batch 1; **2.17 s/sample** at batch 20; 27.3 s/sample if called sequentially in a loop | **113–160 MiB** for batch 1→20 | `[SIBLING]`, RTX 3060 Laptop |
| **LLM route (7B–70B)** | seconds, plus 10 samples per layout for LayoutPrompter | 14–140 GB of weights | `[PAPER]` |

The HouseDiffusion memory figure is the one `[SIBLING]` number this pass can
*explain* rather than merely repeat: the conditioning tensor is a fixed
`(100, 94)` regardless of programme size `[CODE]`, so "a 24-room villa costs
exactly the same memory as an 8-room flat" is a property of the code, not a
measurement artefact.

### 5.3 What our model would cost

```
forward FLOPs   2*N*T = 2*2e7*128            = 5.1 GFLOP per sample per step
sampling steps  8-16 (parallel masked decoding, BLT does T/3 ~ 9-12)
per Proposal    ~40-80 GFLOP
RTX 3060 laptop, fp16, realistic             ~5e12 FLOP/s   [EST]
                                             ~8-16 ms per Proposal
batch of 20: 0.8-1.6 TFLOP, and batching
raises utilisation to ~1.5e13 FLOP/s [EST]   ~55-110 ms for all 20
```

Against a 6.25 s solve per candidate that is **under 1 % of the plan budget**, and
against HouseDiffusion's measured 43.3 s for 20 candidates `[SIBLING]` it is
roughly **400–800× cheaper** (43.3 s versus ~55–110 ms for the same 20).

**Memory per Proposal: well under 0.5 GB**, dominated by the weights (20M params =
40 MB in fp16) `[DERIVED]`, consistent with the 113–160 MiB the sibling measured
for a same-sized model.

**A consequence worth stating for the runtime split:** at 12–25M parameters and
8–16 sampling steps, the proposer service **does not need a GPU to serve**. A
4-core CPU should return a Proposal in a few hundred milliseconds `[EST]` — the
same order as Graph2Plan's measured 0.4 s retrieval pipeline. The GPU is needed
for *training*, not for serving. That materially simplifies the HTTP-service
deployment that *Language and runtime split* fixed, and it is a property the
1000-step diffusion route does not have.

---

## 6. Licence, per C9

C9 says licence is not a gate. It is still worth recording the terms, because C11
turns the licence question into a different one: **not "may we ship this?" but "may
we read it, and may we check our reimplementation against it?"**

| Artifact | Terms | Verified |
|---|---|---|
| **HouseDiffusion** code **and weights** | verbatim, the whole 311-byte `LICENSE`: *"The code and the model weights in this repository are not allowed for commercial usage. For research purposes, the terms follow the GPL v3, as in the separate file 'LICENSE_GPL'."* | `[CODE]` — read this pass from `raw.githubusercontent.com` |
| **House-GAN / House-GAN++** | GPL-3.0 text with a prepended banner: `********* THIS CODE CAN ONLY BE USED FOR RESEARCH PURPOSES *********` | `[CODE]` — read this pass |
| **MaskPLAN** | **MIT** (`spdx_id: "MIT"`); weights on Drive, RPLAN-derived; repo also ships RPLAN-derived `.npy`/`.npz` arrays | `[API]` + `[CODE]` |
| **LayoutDM** | **Apache-2.0**, "Copyright 2023 Naoto Inoue"; **weights released** (`layoutdm_starter.zip`); repo archived 2023-10-24 | `[API]` |
| **LayoutFormer++, LayoutDiffusion, LayoutPrompter** | **MIT** (Microsoft); weights released for the first two | `[API]` |
| **LayoutFlow** | **MIT**; weights on Hugging Face (re-trained after a refactor, not the paper's originals) | `[API]` |
| **DLT** | **Apache-2.0**; no weights | `[API]` |
| **LayoutNUWA** | **MIT**; no fine-tuned weights released | `[API]` |
| **Swiss Dwellings v3.0.0** | **CC BY 4.0**, Archilyse AG | `[API]` — Zenodo record 7788422, read this pass |
| **ResPlan** | data **CC BY 4.0**, code **MIT** | `[PRIOR]` |

**What actually binds us, once C9 has removed the commercial gate:**

1. **Attribution.** Swiss Dwellings and ResPlan are CC BY 4.0. The attribution
   strings belong in the product credits; ticket 12 already asks for them.
2. **C11, not licence, is what forbids inheriting the predecessor's code.** C11
   constrains `../plan-generator-3000-pro-max`; it says nothing about third-party
   code. Ticket 08 nonetheless states the intent to reimplement the architecture
   rather than download a checkpoint. **This deserves an explicit decision rather
   than drift:** the recommended architecture's reference implementation is
   **Apache-2.0 with released weights**, so "start from that code and retrain on our
   data" is legally clean and would save weeks. Reimplementing is a choice about
   understanding and about not depending on an archived upstream — not a licence
   requirement.
3. **A useful asymmetry:** the architectures whose code we may freely copy
   (LayoutDM, LayoutFlow, LayoutFormer++) are the ones this survey recommends; the
   ones we would have to clean-room (HouseDiffusion, House-GAN++) are the ones it
   rejects. Nothing has to be traded off.

---

## 7. Recommendation

### 7.1 The recommendation

> **Build the Proposer as a Brief-conditioned room-set transformer that emits one
> axis-aligned box per Brief room, trained from scratch. Take the architecture from
> the conditional graphic-layout line (LayoutDM / BLT class: ~12–25M parameters,
> `d = 512`, 4–8 layers, discrete coordinate bins, masked parallel decoding), not
> from HouseDiffusion.**

Six components, each of which already exists in a published system:

| # | Component | Taken from | Why |
|---|---|---|---|
| 1 | One token per room; box as 4 discretised coordinates; **128 uniform bins per axis** | LayoutFormer++ sets `discrete_x_grid`/`discrete_y_grid` to 128 in its training scripts `[CODE]`; LayoutDiffusion's vocab sizes imply the same 128 `[DERIVED]` | 128 bins × 250 mm = 32 m of envelope, so the solver's grid is representable exactly and the contract's "integers in Envelope grid units" is satisfied natively. LayoutDM's default of 32 KMeans bins is too coarse — but it is a config field, not an architectural constant. |
| 2 | **Envelope cross-attention** | Boundary-Constrained Diffusion's BCA `[PAPER]`; Kuhn's room-corner↔structural-corner cross-attention `[PAPER]` | The Brief always carries an Envelope. This is the one input HouseDiffusion cannot take. |
| 3 | **Per-room target-area conditioning** | MaskPLAN's `area_mask` `[CODE]` | A Homeowner's Brief is mostly areas, and proportion is half of what the Proposal contributes. |
| 4 | **Relational attention over the Brief's requested adjacency** | HouseDiffusion's `door_attn` / `self_attn` / `gen_attn` split `[CODE]` | Soft conditioning only — the Brief's adjacencies remain hard constraints in the solver (contract item 6). |
| 5 | **Masked training over any subset of room attributes** | MaskPLAN `[CODE]`; LayoutDM's six-tasks-one-checkpoint design `[PAPER]` | One checkpoint serves generation, completion and pinning. It is also the hook C7's interactive re-solve will want, at no extra cost now. |
| 6 | **`(region, corpus, annotation_provenance)` conditioning tokens** | `dataset-unification.md` §6.3 | Three categorical embeddings. This is the model's actual job. |

Trained in two stages, following the only 2026 result that measures transfer onto
Swiss Dwellings:

1. **Synthetic pre-training**, from a generator built in-house to Ospici et al.'s
   published recipe `[PAPER]` — but **extended past their 2–10 rooms to 12–32
   rooms**, because that is exactly the regime our corpora cannot supply, and their
   result is that what transfers is assembly rules rather than style.
2. **Fine-tune on Swiss Dwellings + ResPlan** under the conditioning triple, with
   **room polygons rectangularised** — which Kuhn found improves a
   HouseDiffusion-class model on this corpus family `[PAPER]`, and which our
   pipeline requires anyway because the solver places rectangles.

Scored on **relative arrangement first** (per-pair separation-direction agreement,
and the fraction of pairs fixable without closing a cycle), then on the only number
that ultimately matters: **solver-projected, validator-passed plans per Proposal**,
plus solve wall-clock. Not FID; not box IoU alone. The nearest published relatives
are House-GAN's *compatibility* — "a graph editing distance between the input
bubble diagram and the bubble diagram constructed from the output layout"
`[PAPER]` — and Ospici's **NGED** `[PAPER]`. Neither measures the four-way
separation direction the solver actually extracts, so **the primary metric is one
we have to define ourselves.** That is small, and it belongs to ticket 08.

### 7.2 Why not the obvious alternative

**HouseDiffusion, and a HouseDiffusion successor in its published form, is
rejected on four independent grounds**, any one of which would be sufficient:

1. **It cannot take an Envelope** (`condition_channels = 89` = 25 type + 32
   corner-index + 32 room-index `[CODE]`).
2. **Its distinguishing capability is discarded.** The solver re-derives every
   coordinate on a 250 mm grid, so exact corner incidence and non-Manhattan loops
   are paid for and then overwritten.
3. **It costs ~16× more to train and several hundred times more to serve** than the
   recommendation (§4.3, §5.3), for a task the cheaper model is designed for.
4. **Independent published evidence says its representation is the wrong one at our
   room counts** — rectangles beat polygons on Swiss-Dwellings-derived data, and
   training samples had to be dropped for having too many rooms `[PAPER]`.

### 7.3 The runner-up, and the condition under which it wins

> **Runner-up: retrieval-and-warp — Graph2Plan's retrieval step, reimplemented over
> Swiss Dwellings, with no learned generator at all.**

It is a serious candidate rather than a stopgap, and the contract says so:
*"A retrieved real floor plan, warped to the Envelope, is an excellent Proposal
under this contract: its relative arrangement is by construction that of a real
home."* The mechanism is published and cheap — filter the corpus by room types,
counts and adjacencies; rank by boundary similarity with a **turning function**
anchored at the front door; rotate in 90° steps to align entries; reposition nodes
on a 5×5 grid relative to the input boundary. Measured at **99 ms retrieval and
<0.4 s end to end** `[PAPER]`. Training cost zero; data requirement one corpus in
the target region.

**It wins outright if either of these holds:**

- **(a) The tail is empty.** Ticket 12's per-dwelling area histogram (§3.2) shows
  fewer than roughly **1,000** C5-surviving Swiss Dwellings dwellings with ≥16
  areas, **and** synthetic pre-training fails to close the relation-accuracy gap at
  16+ rooms on held-out data. Then there is nothing to learn in the regime that
  actually matters, and a *real* 20-room home warped onto the Envelope is a better
  arrangement prior than a model extrapolating from 6-room flats.
- **(b) It is not beaten on the metric that counts.** Measured on held-out
  dwellings, retrieval matches or beats the trained model on relation accuracy and
  on validator-passed plans per Proposal. This is the sibling's warning applied
  properly, and the adjacent literature says the outcome is live: **LayoutPrompter,
  training-free retrieval plus an LLM, scores RICO Gen-T mIoU 0.429 against
  LayoutFormer++'s 0.432** `[PAPER]`.

**Third place, and only inside the trained family:** if masked parallel decoding
produces insufficiently *diverse* candidates — which matters because C6 generates
many and rejects most, and which nobody has measured for floorplans — fall back to
**box-level discrete-continuous diffusion**: HouseDiffusion's objective with Kuhn's
rectangularisation, four corners per room, sampled in ≤100 steps rather than 1000.
Same conditioning, same tokenisation, ~16× the training cost. **Do not adopt it
before measuring diversity; do not rule it out either.**

### 7.4 What would falsify this recommendation

Stated so the next session can check rather than re-litigate:

1. **The ≥16-area tail in Swiss Dwellings** (ticket 12). Thick → the trained route
   strengthens and the synthetic stage may be unnecessary. Thin → §7.3(a) fires.
2. **Diversity of masked parallel decoding on floorplans.** Unmeasured anywhere.
3. **Whether target-area conditioning is actually learned.** Only MaskPLAN takes
   per-room areas, and publishes no ablation isolating them `[CODE]` — an unmeasured
   assumption sitting in the middle of the recommendation.
4. **Rectangle-only rooms.** The whole pipeline — solver included — places one
   rectangle per room. ResPlan reports only **43.2 %** of its room polygons are
   rectangular `[PRIOR]`, while Graph2Plan reports **"over 93% of the rooms in RPLAN
   can be represented as the intersection between their respective bounding boxes
   and the building boundary"** `[PAPER]`. Those measure different things and are
   not in conflict, but the gap between them is the L-shaped-room question. It
   belongs to tickets 01/04 — **flagged here because this recommendation quietly
   depends on it.**

### 7.5 Item 3's retrieval twin: target-area conditioning is not *delivered* either

§7.4 item 3 records that nobody has shown a trained model actually learns per-room
target areas. **The runner-up has the same hole and it is now measured.** ADR 0018's
headline — best-of-8 worst-room deviation p50 **0.056** — is a *proportion* result:
`fit_warp.py:373–384` scales the Brief's targets onto the donor's covered area
before comparing, so it says the warp preserves the **shares** a donor allocates
and says nothing about whether a Room asked for 12 m² gets 12 m².

`experiments/warp/absolute_area.py`, 600 sampled Briefs over the 2 292 converted
Swiss dwellings that join the room cache. Three changes from `fit_warp`: targets
enter in absolute m² and are never renormalised; the box is sized the way ADR 0020
writes it (`interior = target_area × 1.0575`, `box = interior/(1 − s)`); and the
quantity measured is the **Space**, `erode(⋃ parts, t_int/2)` per ADR 0001, which
is the plane `dim.min_area` and `dim.statutory_min_area` actually bind.

| arm | plans | per-Room abs dev p05 / p50 (m²) | Σ Space vs `target_area`, mean | Rooms pushed under a floor | plans losing one |
|---|---:|---:|---:|---:|---:|
| `self` — candidate is the Brief's own dwelling | 521 | −2.23 / −0.01 | **−0.8 %** | 4.9 % | **13.1 %** |
| `cross` — real gate-admitted retrieval | 499 | −4.91 / −0.02 | **−2.2 %** | 12.7 % | **30.5 %** |
| `calib` — `cross`, box scaled so Σ Space = `target_area` | 499 | −3.97 / +0.03 | −0.1 % | 8.2 % | **22.0 %** |
| `market` — every target raised onto `dim.market_default_area` | 508 | −4.05 / −0.04 | **−1.2 %** | 10.3 % | **29.9 %** |
| **`ring`** — `cross` with the Envelope's edge ring held before the solve | 499 | — | **+0.4 %** | 10.1 % | **24.9 %** |

⚠️ **This table was re-measured by ticket 56 and every row moved.** The rig had
been eroding a wall that is not there — it tiled the Envelope *box* and eroded
every Room on all four sides, where ADR 0001 tiles the solve domain and a boundary
edge costs no floor, a 75 mm ring worth **3.7 % of `interior` at p50**. **Read the
`ring` row and no other as what the engine delivers**: it is the only arm that
enforces ADR 0020's amendment, and it lands Σ Space at **+0.4 %** of the floor the
Brief asked for. `experiments/warp/README.md` carries the paired before/after
table and the committed pre-56 rows.

The last two columns count only Rooms whose **own stated target already clears the
floor**, so a Swiss dwelling entitled to a 6 m² kitchen is not counted against the
warp. That conditioning is necessary: `brief.md` §9.4 bound 1 is a bound on the
**sum**, not a per-room test, so nothing upstream raises an individual Room onto
its floor.

**Four findings.**

1. **The deviation is real and it is one-sided.** 57.7–59.0 % of Rooms come in
   under target across every arm, and the *plan total* is systematically short —
   `cross` delivers a mean **4.3 %** less floor than the Brief asked for, p05
   **−16.6 %**. Direction is what matters here: ticket 50 priced
   `dim.statutory_min_area` as hard partly because `dim.market_default_area` is
   two-sided and pulls from both sides. It does not pull from both sides.
2. **The level error and the distribution error are separable — and after ticket
   56 the level error is gone, so all of it is distribution.** Σ Space ÷
   `target_area` still decomposes at p50 into three terms with three different
   owners — the rung's inflation **1.0575**, what the box holds after `s` (`cross`
   **0.9833**), and the erosion (**0.9490**). ⚠️ **The earlier reading of this
   finding is dead.** It said calibrating the box needs **+4.2 %** and takes
   plan-level statutory loss 30.7 % → 18.8 %, so *"roughly two fifths of the damage
   is one fixable constant"*. Ticket 56 showed the +4.2 % **was** the two rig
   defects: with the ring held, Σ Space lands at **+0.4 %** of the stated floor and
   **there is no sizing correction owed anywhere**. Post-fix `calib` is *worse*
   than `ring` on plan-level loss (22.0 % against 24.9 % — `calib` buys margin the
   engine does not give). The whole of the damage survives a correct level, and
   **that is what §7.6 then prices against pool depth.**
3. **At the pool level it costs about as much again as every dimensional decline
   put together.** Per-candidate shares are not what a Homeowner meets: C6
   generates many and rejects most. Best-of-8, targets on `market_default`, 194
   Briefs — **5,7 % have no candidate that clears every floor**, and **3,6 %** on
   the `ringpool` arm, which is the one that holds ADR 0020's invariant and so is
   the one to quote. ⚠️ **Do not compound the per-candidate share to get here**:
   independence predicts 0,311⁸ ≈ **0,009 %**, a factor of **780** out. ADR 0018
   consequence 3 reproducing itself on a new statistic, with the same cause —
   every candidate for one Brief is sized from the same `interior`. §7.6 measures
   what that 3,6 % does as the pool deepens, and the answer is *very little*.
4. **The kitchen is the limb with no headroom, as predicted.** AZ floors it at
   8,0 m² against a Swiss p50 of 8,04. In `market` — where every kitchen was asked
   for **9,0 m²** or more — **21.8 %** are delivered below 8,0, and the lower
   quartile of those that pass clears the floor by **0,085 m²**. In `cross` the
   lower quartile is already **−0,128 m²**, i.e. under it.

**What this does not say.** It does not say retrieval-and-warp loses to the trained
route: §7.4 item 3 leaves the trained route's own area conditioning unmeasured, so
this moves one side of a comparison whose other side is still blank. And it does
not decide `dim.statutory_min_area`'s severity, which is `rules.json`'s.

⚠️ **Do not quote these past one decimal.** At `--time=3.0` CP-SAT is
wall-clock-dependent: two runs of `self` at the identical seed and inputs returned
5.96 % and 5.78 % on the same statistic.

### 7.6 What pool depth buys, and the floor it does not reach

`acceptance-bar.md` §11.1 keeps `dim.statutory_min_area` hard and offers a starved
Brief three steps, **the first of which is *deepen the pool*** — described there as
*"the step most likely to be the answer, since 3,6 % is a pool-of-8 number against
production pools 58.7–86.6 deep"*. That is a mechanism with no number attached.
This is the number, and **step 1 is not the answer.**

`experiments/warp/best_of_m.py`, 200 sampled Briefs, `ringpool` semantics (targets
on `market_default`, the Envelope ring held), seed 20260819.

**The curve is nested, which is why it costs almost nothing.** `served_at_m` is a
prefix-any over one fixed draw order — if candidate 3 serves, so does every
m ≥ 3 — so the whole curve is determined by the **index of the first serving
candidate** and the early break in `run_pool` stays sound. Going from m = 8 to
m = 64 spends extra warps only on the Briefs that were starving at 8. Every point
is paired against every other by construction.

| m | 1 | 2 | 4 | **8** | 12 | 16 | 32 | **64** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| starved, all Briefs with a pool | 35.2 % | 18.6 % | 10.1 % | **6.5 %** | 6.0 % | 6.0 % | 5.5 % | **5.5 %** |
| starved, `run_pool`'s own convention | 33.5 % | 16.5 % | 7.7 % | **4.1 %** | 3.6 % | 3.6 % | 3.1 % | **3.1 %** |
| 4–6 rooms | 32.6 % | 18.5 % | 10.9 % | 4.3 % | 3.3 % | 3.3 % | 2.2 % | **2.2 %** |
| 7–10 rooms | 37.4 % | 18.7 % | 9.3 % | 8.4 % | 8.4 % | 8.4 % | 8.4 % | **8.4 %** |

The second row is the published statistic's own convention — it excludes Briefs
whose every candidate failed to warp — and it reproduces §7.5's **3,6 %** at
m = 12–16 against **4,1 %** at m = 8, the difference being one Brief on a
different draw permutation.

**Three readings, and the third is the one §11.1 needs.**

1. **Eight is already on the flat part.** An **eightfold** deepening, 8 → 64, moves
   starvation **4,1 % → 3,1 %**: one point. Ninety per cent of what depth can buy
   is bought by m ≈ 12.
2. **At 7–10 rooms depth buys nothing at all** — 8.4 % from m = 6 to m = 64, flat.
   That is the band ADR 0013 already calls tight and where starvation is worst.
3. **Declines are still correlated, and the level fix did not touch it.** The
   conditional decline — *P(candidate j+1 declines | j prior declines)* — is flat
   under independence and rises here from **35.2 %** at the first candidate to
   50.7, 73.5, 81.2 and **88.9 %** by the seventh. A Brief that has been declined a
   few times is almost certain to be declined again: the residual is a property of
   the **Brief**, not of the draw. Ticket 56 removed the shared *level* error and
   what remains — the warp's per-room **distribution** — has not thinned across a
   pool.

**The extrapolation to production depth, and the model it required.** The sample
cannot hold m = 87 under the shipped gate (below), so the curve is fitted and
published as a fit. Independence is known wrong by a factor of 780, which says
mixture; the obvious mixture is `p ~ Beta(a,b)` with `E[p^m] = B(a+m,b)/B(a,b)`.

⚠️ **A plain Beta is also wrong, and it fails in the dangerous direction.** Every
Beta sends `E[p^m]` to zero, so it predicts that enough depth serves every Brief.
Fitted to this data it returns **0,45 %** at m = 8 against a measured **8,2 %** —
an answer contradicted by the column beside it, and one that would have said
*deepen the pool* is free. The fix is a **point mass at p = 1**, a share of Briefs
retrieval serves at no depth because the corpus simply does not hold an
arrangement clearing their floors:

    starvation(m)  =  π  +  (1 − π) · B(a + m, b) / B(a, b)

`π` is the asymptote, and it is exactly what step 1 cannot buy. Fitted by maximum
likelihood on the censored observations — a Brief whose pool holds 3 members is
**not** a Brief that survived best-of-32 — with a 200-sample bootstrap:

| | π (the floor) | at m = 8 | at production m | 
|---|---:|---:|---:|
| all Briefs | **2,8 %** [0,3 – 5,6] | 4,9 % | **2,8 %** [0,5 – 5,6] at 87 |
| 4–6 rooms | 1,1 % [0,0 – 4,7] | 5,0 % | **1,3 %** [0,0 – 4,8] at 87 |
| 7–10 rooms | **5,3 %** [0,0 – 11,2] | 5,4 % | **5,3 %** [0,0 – 11,2] at 59 |

So deepening from 8 to production depth buys roughly **two points**, and at 7–10
rooms it buys **one tenth of one point** — the curve is at its asymptote by m = 12.

⚠️ **The intervals are wide and they are the finding, not decoration.** `π` is
identified by the *depth* of the censored observations, so it is the one quantity
a shallow sample cannot pin down; the honest reading of 7–10's [0,0 – 11,2] is
that the sample bounds the floor loosely, not that it is small.

**What `--pool=8` was actually drawn from, which turns out not to be the shipped
gate.** §2.2.7's second limit says the sample is the converted 2,317, *"so a pool
of 87 in production is a pool of 8 here"*. Measured over the same sample
(`experiments/warp/pool_depth.py`):

| pool definition | p50, 4–6 | p50, 7–10 | max | empty | ≥ 64 |
|---|---:|---:|---:|---:|---:|
| shipped gate — §2.2.1's bucket, scanned by area and aspect | **9** | **5** | 51 | 14.5 % | **0 %** |
| what `absolute_area.gate_pool` returns | **81** | **37** | 146 | 0.5 % | 43.5 % |
| production, full 46,794 index | 86.6 | 58.7 | — | — | — |

**§2.2.7's sentence is right about the shipped gate and wrong about the rig.**
Against the gate as §2.2.1 writes it the sample is ~9.6× and ~11.7× short, so
"a pool of 87 is a pool of 8 here" is a fair ratio. But `gate_pool`'s primary
branch returns the **whole multiset bucket** and applies the area and aspect terms
only in its by-room-count fallback, so the pool the 3,6 % was drawn from is at
production *depth* with members the gate would not admit.

That cuts both ways and both were measured. Gate-admitted donors are **better**:
first-candidate decline is **29.8 %** on the gated pool against **35.2 %** on the
bucket, so the shipped system's members are ~5 points better than the ones priced.
But the gated sample bottoms out at depth ~10, and **its own fit returns π = 0
with a zero-width interval** — a shallow-censoring artefact, the same failure as
the plain Beta. The deep bucket is the only arm here that can see an asymptote at
all, which is why the table above is fitted on it.

**What deepening costs.** A pool member is a warp plus a projection solve. The warp
is measured here at **0.79 s** (bucket) and **1.66 s** (gated, whose fixed point
iterates more), against the projection solve on a real boundary at p50 **10,11 s**
with p90 at the 15 s cap (`solver-formulation.md` Part V). So depth is affordable
**only if starvation is screenable on the Proposal**, before the solve — 79 extra
warps is ~60–130 s, 79 extra solves is **13–20 minutes for one Brief**, and it
falls entirely on the starving Brief, which is the worst possible distribution.

⚠️ **Whether it is screenable is not established here, and the rig cannot settle
it.** `dim.statutory_min_area` is `site: both` — the solver *posts* it and the
validator *evaluates* it — and everything above is measured on the **warped
rectangles**, i.e. on the Proposal. No warped Proposal on this map has ever been
put through the projection solve: `fit_warp.py` imports `experiments/solver-toy/`
for its relation extractor only. **3,6 % and every number in this section are
Proposal-level starvation**, and the solver has freedom the warp does not, so the
Plan-level figure could fall either side.

**What §7.6 does not decide.** Not `dim.statutory_min_area`'s severity — settled
hard by ticket 55 on an argument that never depended on this number, and a smaller
figure here relaxes the escalation rather than reopening the rule. Not source B's
per-room absolute area fidelity, which §11.1 step 2 depends on and §6.1 has no term
for. What it does say is that **step 1 carries about two points and cannot go below
π**, so steps 2 and 3 are load-bearing and source B's unmeasured area fidelity is
now the urgent one.

### 7.7 What the warp's two owed constraints cost

`fit_warp.warp_model` posts neither constraint this map has since decided the warp
holds: ADR 0020's amendment (the notch share stays at the `s` the box was derived
from) and ADR 0028 (the enclosed void is charged to its receiving Room and
weighted). The `ring` arms reach the first by **re-sizing the box** rather than by
constraining the solve, so no arm had ever run the genuinely constrained model.
Both bind the same solve, so their cost is one number.
`experiments/warp/constrained_warp.py`, 194 paired (Brief, donor) cases.

| arm | INFEASIBLE | lost vs `free` | \|notch drift\| p90 | realised void p90 | worst-room dev p50 |
|---|---:|---:|---:|---:|---:|
| `free` — what ships | 10.8 % | — | 0.0910 | 0.375 | 0.1391 |
| `void` — ADR 0028 | 10.8 % | **0** | 0.0923 | **0.250** | 0.1478 |
| `notch` — ADR 0020 | 13.4 % | 5 | **0.0197** | 0.375 | 0.1621 |
| **`both`** | **13.4 %** | **5 — 2,6 %** | **0.0195** | **0.250** | 0.1662 |

**The void half is free and the notch half is not.** ADR 0028 costs **zero**
candidates, reproducing `experiments/void/`'s 9/90-on-every-arm; the joint cost
*is* the notch's cost. And it is a function of how hard the invariant is held:

| notch tolerance (share points) | ±0.04 | ±0.02 | ±0.01 | ±0.005 | exact |
|---|---:|---:|---:|---:|---:|
| candidates lost vs `free` | 1,5 % | **2,6 %** | 3,6 % | 3,6 % | **8,8 %** |
| worst-room dev p50 | 0.1645 | 0.1662 | 0.1797 | 0.1846 | **0.2256** |

Holding it exactly costs **8,8 %** of candidates and takes worst-room deviation
from 0.139 to **0.226** — a sixth of the pool and a fifth of the fidelity, for an
invariant the `ring` fixed point currently gets for free by moving the box instead.

⚠️ **ADR 0020's `s` does not cover all of the notch.** `notch_share` defines `s` as
the **two largest** boundary-touching complement components, and **27,5 %** of
converted donors have three or more. On those, boundary-touching floor exists that
is neither notch nor void by the ADR's own definitions — and an encoding that
holds "all uncovered minus the enclosed" is therefore holding a strictly larger
region than the ADR names. Both encodings were run; the table above constrains the
cells `s` is actually read off, which is why its drift tracks the tolerance
(0.0388 → 0.0195 → 0.0097 → 0.0051 → 0.0003) where the looser one stalled at 0.04.

---

## 8. What this commits the training runtime to

This is the section ticket 08 consumes. Every number carries its status; the
`[DERIVED]` ones show their arithmetic in §4.3 and §5.3.

| Commitment | Value | Status |
|---|---|---|
| **Parameter count** | **12–25M**, target ≈20M. `d = 512`, 4–8 layers, 8 heads, FFN 2048, 128 coordinate bins per axis | `[DERIVED]` from LayoutDM 12.4M @ 4×512 `[PAPER]` and LayoutFormer++ ≈59M @ 16×512 |
| **VRAM floor, training** | **≈2 GB** fp32 at batch 64 / **<1 GB** bf16 at batch 32. Fits the 6 GB RTX 3060 Laptop and a free-tier T4 or P100 | `[DERIVED]` |
| **VRAM, serving** | **<0.5 GB**, weights-dominated (20M params = 40 MB fp16). CPU serving is viable | `[DERIVED]`, corroborated by the sibling's measured 113–160 MiB for a same-sized model `[SIBLING]` |
| **Dataset volume — floor** | **~4,000 records** trains a model of this class on this corpus family (Kuhn: 3,804 samples `[PAPER]`; Ospici: 1k fine-tuning samples after synthetic pre-training `[PAPER]`) | `[PAPER]` |
| **Dataset volume — target** | Swiss Dwellings C5-filtered dwellings (**NOT ESTABLISHED**; nominal 45,176 apartments, one published filtering run yielded ~5k plans) **+ ~15,800 ResPlan** **+ ~135k synthetic scenes generated in-house** | `[API]`/`[PAPER]`/`[PRIOR]` |
| **The volume that actually binds** | dwellings with **≥16 areas**. Unknown until ticket 12. If it is under ~1,000, §7.3(a) fires and the runner-up wins | **NOT ESTABLISHED** |
| **Wall-clock to converge** | **5–15 GPU-hours** fine-tune + **~5–10 GPU-hours** synthetic pre-training = **~10–25 GPU-hours on a T4** → inside one week of Kaggle's free 30 h/week, with a factor of ~2 spare | `[DERIVED]`, anchored on LayoutTransformer's "about 6 hours on a single NVIDIA GTX1080" for 3.5M presentations `[PAPER]` |
| **Wall-clock, trained fallback** (box diffusion) | **~40–150 GPU-hours on a T4** — 1.5–5 weeks of free tier, or under a day of rented A100/H100. ≈16× the recommendation | `[DERIVED]` from HouseDiffusion's 250k × batch 512 `[PAPER]` |
| **Inference latency per Proposal** | **8–16 ms** on a consumer GPU at 8–16 sampling steps; **~55–110 ms for a batch of 20 candidates in one call**; a few hundred ms on 4 CPU cores | `[DERIVED]`, bracketed by published measurements of LayoutFlow 1.75 ms / DLT 3.5 ms / LayoutDM 16.6 ms `[PAPER]` |
| **Share of the plan budget** | **<1 %** against a 6.25 s solve per candidate. Compare HouseDiffusion's measured 43.3 s for 20 candidates | `[DERIVED]` / `[SIBLING]` |
| **Sampling call shape** | **Batched: N candidates in one call, never a loop.** The sibling measured 12.6× between batch-20 and sequential on the same model | `[SIBLING]` |
| **Serving hardware** | **No GPU required to serve.** GPU is a training dependency only | `[EST]` |

**Obligations this creates elsewhere:**

- **Ticket 12 gains a blocking query**, not just a download: the per-dwelling area
  histogram in §3.2. It decides between the recommendation and its runner-up.
- **Ticket 08 must define the arrangement metric** (§7.1). No published metric
  measures what the solver consumes.
- **The evaluation loop needs the validator (ticket 07) and the solver in it.**
  "Validator-passed plans per Proposal" cannot be computed before ticket 07 lands,
  so the interim proxy is relation accuracy plus solve wall-clock.
- **A default for the conditioning triple is mandatory at inference** —
  `dataset-unification.md` recommends `europe_ch` / `cad_records`, surfaced as a C4
  Assumption.
- **CC BY 4.0 attribution** for Swiss Dwellings and ResPlan in the product credits.
- **The synthetic generator is the earliest-startable item on this whole route.**
  It needs no downloads, no licences and no corpora — it can be built and tested
  before ticket 12 finishes, and it is the only lever that addresses the 24-room
  regime at all.

**What this explicitly does *not* commit us to:**

- No downloaded checkpoint, no GPL/research-only code in the tree, no MATLAB.
- No 1000-step sampler, and no GPU in the serving path.
- **No per-room-count models.** House-GAN++ and HouseDiffusion both cross-validate
  *by room-count group* — train with one group held out, evaluate on it — so a
  checkpoint is tied to the group it was cut for (`--target_set 8` in
  HouseDiffusion's own training command `[CODE]`). A permutation-equivariant
  room-set transformer with no room-index one-hot handles variable *n* in one
  checkpoint, which is what makes 24 rooms an extrapolation question rather than an
  architecture question.
- No commitment to beat retrieval on faith — §7.3 makes retrieval the measured
  baseline, and it ships first either way.

---

## What this note does not establish

Listed plainly, because a research note that hides its gaps is worse than one that
has them.

- **Nothing was trained or benchmarked.** Every cost figure here is derived from
  published configurations plus arithmetic, or is an estimate. There is no run.
- **The predecessor's degradation curve was not reproduced** (§3.3). The
  environment no longer exists in that repo. It is corroborated in *direction* by
  an independent group and by structural facts read out of the code, and it is
  *confounded* in magnitude by storey-flattening and vocabulary loss.
- **The Swiss Dwellings room-count distribution is unknown** — the single most
  important missing number in this document.
- **Diversity, and whether masked parallel decoding gives enough of it**, is
  unmeasured for this domain.
- **No pooled-corpus or conditioned-corpus floorplan result exists** to validate
  `dataset-unification.md`'s conditioning recommendation; that remains `[INF]`
  there and is inherited unverified here.
- **Several 2026 works could not be read past their abstract pages** —
  HypergraphFormer's model size, room counts and code URL; GFLAN's architecture
  details and room counts; FloorPlan-DeepSeek's base model and costs. All marked
  **COULD NOT CONFIRM** where cited.
- **`WebSearch` quota was exhausted** at 200/200 partway through this pass.
  Discovery afterwards used the arXiv, GitHub and Zenodo APIs directly. Coverage of
  very recent work with no arXiv listing is therefore weaker than the rest.
- **A second delegated sweep — on GSDiff, DiffPlanner, floor-plan RLVR,
  HypergraphFormer, FMLM and ChatHouseDiffusion — did not complete** (it failed
  twice on server errors). Those entries therefore remain `[PRIOR]` from
  `floorplan-generation-stack.md`, re-checked only for existence via the arXiv API.
  None of them is load-bearing for the recommendation: every one is either
  boundary-only conditioning (§2.2, disqualified on interface) or an LLM at a size
  we cannot train or serve (§4.2).

---

## Sources

**Read directly this pass** (2026-08-18):

*Source code and repository metadata*
- `https://api.github.com/repos/aminshabani/house_diffusion/git/trees/main?recursive=1`
- `https://raw.githubusercontent.com/aminshabani/house_diffusion/main/house_diffusion/{script_util.py, transformer.py, rplanhg_datasets.py}`
- `https://raw.githubusercontent.com/aminshabani/house_diffusion/main/scripts/script.sh`
- `https://raw.githubusercontent.com/aminshabani/house_diffusion/main/LICENSE`
- `https://raw.githubusercontent.com/ennauata/houseganpp/main/{test.py, LICENSE}`
- `https://api.github.com/repos/HangZhangZ/MaskPLAN` and `/git/trees/main?recursive=1`
- `https://raw.githubusercontent.com/HangZhangZ/MaskPLAN/main/{utils.py, Train/MaskPLAN_Train.py, MaskPLAN/MaskPLAN_BaseModel.py, Processed_data/FP_MaskPLAN_vec.py}`

*Papers*
- `https://arxiv.org/abs/2211.13287` and `https://ar5iv.labs.arxiv.org/html/2211.13287` — HouseDiffusion
- `https://ar5iv.labs.arxiv.org/html/2003.06988` — House-GAN
- `https://ar5iv.labs.arxiv.org/html/2103.02574` — House-GAN++
- `https://ar5iv.labs.arxiv.org/html/2004.13204` — Graph2Plan
- `https://arxiv.org/abs/2312.03938` and `https://ar5iv.labs.arxiv.org/html/2312.03938` — Kuhn, HouseDiffusion → MSD
- `https://arxiv.org/html/2407.10121v3` — MSD benchmark
- `https://arxiv.org/html/2607.06483v1` — Ospici et al., synthetic pre-training
- `https://arxiv.org/abs/2508.14006` — ResPlan
- `https://arxiv.org/abs/{2605.18932, 2602.01949, 2512.16275, 2506.21562}` — HypergraphFormer, Boundary-Constrained Diffusion, GFLAN, FloorPlan-DeepSeek (abstract pages only)

*Datasets and APIs*
- `https://zenodo.org/records/7788422` — Swiss Dwellings v3.0.0 record
- `https://archilyse.standfest.science/swiss-dwellings` — schema
- `http://export.arxiv.org/api/query?...` — two sweeps: `abs:"floorplan generation" OR abs:"floor plan generation"` (40 newest) and `all:"Swiss Dwellings"`

*Local, in-repo*
- `docs/research/{solver-formulation.md, floorplan-generation-stack.md, dataset-unification.md}`, `docs/wayfinder/MAP.md`, `CONTEXT.md`, tickets 06/07/08/12/18
- `../plan-generator-3000-pro-max/docs/{phase2_findings.md, phase3_findings.md}`, and a filesystem check confirming no `.venv-hd`, `vendor/house_diffusion` or `weights/` survive there

**Read by the delegated graphic-layout sweep this session** (URLs it quoted)
- `https://arxiv.org/abs/{2303.08137, 2311.06495, 2208.08037, 2303.03755, 2006.14615, 2112.05112, 2303.11589, 2403.18187, 2305.15393, 2309.09506}`
- `https://raw.githubusercontent.com/CyberAgentAILab/layout-dm/main/src/trainer/trainer/{hydra_configs.py, config/experiment/layoutdm.yaml, config/dataset/rico25.yaml, config/dataset/publaynet.yaml, config/backbone/medium.yaml}`
- `https://raw.githubusercontent.com/microsoft/LayoutGeneration/main/{LayoutPrompter/src/utils.py, LayoutPrompter/src/preprocess.py, LayoutPrompter/notebooks/constraint_explicit.ipynb, LayoutFormer++/src/model/layout_transformer/model.py, LayoutFormer++/src/scripts/rico_gen_t.sh, LayoutDiffusion/README.md, LICENSE}`
- `https://raw.githubusercontent.com/wix-incubator/DLT/master/dlt/configs/remote/dlt_rico_config.py`
- `https://raw.githubusercontent.com/JulianGuerreiro/LayoutFlow/main/conf/model/LayoutFlow.yaml`
- `https://api.github.com/repos/CyberAgentAILab/layout-dm`
- `http://interactionmining.org/rico`, `https://arxiv.org/abs/1908.07836` (PubLayNet)
