# Cross-dataset unification — can the corpora be combined?

**Ticket:** `docs/wayfinder/tickets/06-cross-dataset-unification.md`
**Date:** 2026-08-17
**Frame:** C9 (licence is not a gate; data quality and regional convention are),
C12 (not tied to any region; combine where it can be made to work), C5
(single-dwelling, single-storey), C10 (model proposes, solver projects).

> ### Evidence status — read this before trusting any number
>
> Ticket 12 (*Acquire the datasets*) has not run, so **most of this document is
> read from papers, schema pages and source code rather than from the corpora.**
> The exception is ResPlan: during this pass its 258 MB pickle was downloaded
> and inspected directly, and the results **contradict both its own paper and
> the previous research pass** on two material points (§8.2). Every claim
> carries one of five tags:
>
> | Tag | Meaning |
> |---|---|
> | `[DATA]` | **Verified against the actual dataset files.** ResPlan only. |
> | `[SRC]` | Read out of primary **source code or a schema file**. |
> | `[DOC]` | Stated in a **paper, README or dataset record** by the people who made the thing. |
> | `[EXEC]` | **Verified by running code** in the sibling project. Per C11 a strong prior that still needs re-verification here. |
> | `[INF]` | **My inference** from the above. Argued, not sourced. |
>
> A claim with no tag is a framing sentence, not a fact. Where a fact could not
> be established it says **NOT ESTABLISHED** rather than guessing.
>
> The ResPlan result is a warning about the rest: **the one corpus we actually
> opened turned out to disagree with its own documentation.** Treat every
> `[DOC]` claim below as provisional until ticket 12 checks it.

---

## Verdict

**Do not pool the five corpora. Combine two of them, use two as a separate
pre-training stage, and use one not at all.**

The request was "combine them if possible". The honest answer is that "combine"
is the right verb for exactly one pair, and applying it to all five would
produce the mediocre-everywhere model the ticket warns about.

| Corpus | Role | Merged into the target mix? |
|---|---|---|
| **Swiss Dwellings** | Primary. Geometry, walls, openings, 2.5D, fixtures, envelope-for-flats. | **Yes** — this is the backbone |
| **ResPlan** | Secondary. Second region, typed access graph, clean single-dwelling records. | **Yes** — merged under a conditioning tag |
| **RPLAN** | Demoted. Optional pre-training only, and it must earn its place on an ablation. | **No** |
| **MSD** | Not training data. A strict subset of Swiss Dwellings, filtered *away* from C5. | **No** |
| **ProcTHOR-10k** | Take the *generator* idea, not the dataset. Second choice to a purpose-built one. | **No** |

**Region must be an explicit conditioning variable — and region alone is not
enough.** Condition on the triple `(region, corpus, annotation_provenance)`.
Reasoning in §6.

The two load-bearing findings, both from primary sources found during this pass:

1. **The one role everyone assigns RPLAN — "pre-training scale" — is the one
   role with direct published evidence against it.** ResPlan's authors tested
   exactly that: *"RPLAN pre-training plus fine-tuning helps only at 1% training
   data (+0.4 pp) and vanishes at ≥5%, confirming the gap is structural."* `[DOC]`
2. **Deliberately *unrealistic* synthetic pre-training beats every real
   cross-corpus transfer**, and on one target beats in-domain training outright.
   Ospici et al. 2026 `[DOC]`. What transfers between regions is *spatial
   assembly rules*; what does not transfer is *architectural style*.

Finding 2 is the one that should change the plan, because of how it interacts
with C10. Under *model proposes, solver projects*, the assembly rules are the
**solver's** job — they are hard constraints. The only thing the model
contributes is regional plausibility, which is precisely the part that does not
transfer. **Pooling averages away the single thing we are asking the model
for.** That is the core argument of this document.

---

## 1. Corrections to the previous pass

`docs/research/floorplan-generation-stack.md` §2, §3 and §3.2 are the starting
point. They hold up on facts. Two things need correcting, and both are
consequences of C9 rather than errors of research.

### 1.1 The RPLAN verdict was a licence verdict, and C9 voids it

The prior doc concludes *"RPLAN cannot be used in a commercial product… this
also taints every model trained on it."* Under **C9 this is no longer the
question.** The project is non-commercial and research-only datasets are
available, so RPLAN's clause 1/clause 7 problem lapses.

RPLAN must therefore be re-judged **entirely on data grounds** — which this
document does. It still loses. But it loses for completely different reasons
(no metric scale, no windows, a regionally idiosyncratic taxonomy, and failed
transfer), and it is important that the next session understands the argument
has been rebuilt rather than inherited. Similarly, the prior doc's
"ResPlan vs RPLAN: for a commercial product that trade is not close" is a
commercial framing that C9 retires; the conclusion happens to survive, the
reasoning does not.

The same applies to MSD's CC BY-SA "are weights an adaptation?" question and to
CubiCasa5K / LIFULL / Structured3D being non-commercial. Under C9 those are all
moot. **CubiCasa5K and Structured3D should be reconsidered on data merit in
ticket 12** — this pass did not evaluate them because they were not in the
ticket's candidate list, and that is a gap, noted in §11.

### 1.2 The 0.592 number does not mean what the ticket implies

This matters, so it gets its own section: §2.1.

---

## 2. What the evidence actually says about domain shift

### 2.1 The ResPlan number is a room-*classifier*, not a generator

The ticket's warning sign — 0.909 on RPLAN, 0.592 on ResPlan — is real but is
being read as stronger than it is.

From the ResPlan paper (v2) `[DOC]`:

- The task is **semantic room labeling**: classifying room *nodes* into five
  categories — bedroom, bathroom, kitchen, living, balcony.
- The model is **GraphSAGE over 8 hand-crafted features** shared across
  datasets: room area, total degree, neighbour area statistics, area ratio,
  centroid position.
- "Accuracy" is node-classification accuracy.

So the finding is: *given a room's size, degree and position, what that room is
called differs by region.* That is a genuine and relevant result — our system
has to assign room types — but it is **not** a measurement of a layout
generator degrading.

Also note the arXiv v2 numbers are **0.582** (RPLAN→ResPlan) and **0.649**
(ResPlan→RPLAN), not the 0.592/0.664 in the ticket and the prior doc `[DOC]`.
The prior doc appears to have quoted v1. The difference is immaterial to the
conclusion but the next session should cite v2.

### 2.2 The generator evidence is stronger, and it is worse

Found this pass, and it is the most useful single source on the ticket's
question: **Ospici, Gueze, Bourrat & Bernhardt, *Mitigating Domain Shift in
Conditioned Floor Plan Generation: Synthetic Pre-training for Data-Efficient
Adaptation*, arXiv 2607.06483 (July 2026)** `[DOC]`.

They train genuine layout generators (DPFM, a flow-matching arrangement model;
and a vertex-level constraint diffusion model) and measure cross-domain
transfer on **RPLAN, MagicPlan and Swiss Dwellings**. Metrics: **MPE** (mean
Euclidean distance between predicted and ground-truth room vertices in a
256×256 frame, after optimal rigid alignment) and **NGED** (normalised graph
edit distance on the connectivity graph).

| Train → Test | MPE ↓ | NGED ↓ |
|---|---|---|
| RPLAN → RPLAN | **6.31** | 0.46 |
| RPLAN → MagicPlan | 49.33 | 0.90 |
| RPLAN → **Swiss Dwellings** | **52.33** | 0.73 |
| MagicPlan → RPLAN | 57.16 | 0.80 |
| MagicPlan → MagicPlan | **29.10** | 0.33 |
| MagicPlan → Swiss Dwellings | 59.19 | 0.88 |
| **Synthetic → RPLAN** | 38.20 | **0.40** |
| **Synthetic → MagicPlan** | **23.32** | 0.42 |
| **Synthetic → Swiss Dwellings** | **49.41** | **0.63** |

Read the first and third rows together: **a model trained on RPLAN is roughly
eight times worse on Swiss Dwellings than on RPLAN.** That is far more severe
than the ticket's 0.909/0.592, it is measured on the actual task, and one of
the two domains is the corpus we intend to build on.

Three things follow.

**(a) The gap is structural and replicates.** It is not a ResPlan quirk, not a
single model family, and not a single dataset pair. Two independent groups,
three different tasks, four corpora, same direction.

**(b) Synthetic pre-training dominates real cross-domain pre-training.** Every
`Synthetic →` row beats the corresponding real cross-domain row. On MagicPlan,
synthetic pre-training (23.32) **beats in-domain training** (29.10). At 1k
fine-tuning samples on RPLAN, synthetic initialisation reaches 17.9 MPE against
30.8 for real-world initialisation — a **41.7% error reduction** `[DOC]`.

**(c) The authors' explanation is the design principle we should adopt.**
Verbatim: *"generalization requires decoupling the learning of spatial assembly
rules from statistical regularities of any particular architectural style"*, and
their generator *"enforces physical constraints while sacrificing architectural
realism"*. Models trained on real corpora *"overfit to the specific spatial
regularities of their training domain rather than learning the fundamental rules
of layout assembly."*

### 2.3 Why (c) is decisive *for this architecture specifically*

C10 already splits the problem in half:

- **Solver** — hard constraints: non-overlap, containment, connectivity,
  minimum dimensions. These are the "spatial assembly rules".
- **Model** — soft objective: plausibility. This is the "architectural style".

Ospici et al. show that the transferable half is the assembly rules. **In our
architecture we are not asking the model to learn that half — the solver
enforces it exactly.** So the transferable component is already handled by
construction, and the model's entire remaining job is the non-transferable
component.

That has a sharp consequence. Pooling corpora is a bet that averaging across
conventions produces a useful prior. But the thing being averaged is the *only*
thing the model contributes. A pooled, unconditioned model's notion of "a
plausible kitchen–living relationship" would be a blend of Swiss, South Asian
and Chinese practice — a convention that exists in no market. Under C6 the
acceptance bar is a hard filter and we *generate many, reject most*; a
mediocre-everywhere proposer does not produce visibly broken output, it
produces a lower survival rate and blander survivors. That is a silent cost,
which makes it the dangerous kind.

**This is the answer to the ticket's headline question.** Combining is possible;
naive pooling is actively contraindicated; conditioned combination of the
corpora that share a representation is the right move.

> **Honesty note.** No one has published a pooled-corpus floor-plan result.
> Ospici et al. explicitly *"[do] not discuss merging or pooling the three real
> datasets"* `[DOC]`. So "naive pooling hurts" is `[INF]` — a strong inference
> from measured domain gaps plus the C10 argument above, not a measured
> pooling result. The cheap way to settle it is stated in §11.

---

## 3. Do the corpora even agree on what a plan is? (ticket item 4)

No. They disagree at the most basic level, and the disagreement is not cosmetic.

| Corpus | What one record is | Dwelling extraction needed? |
|---|---|---|
| Swiss Dwellings | **a floor of a building**, containing several apartments | **Yes** — group by `apartment_id` |
| MSD | **a floor of a building complex**, ≥15 areas by construction | Yes, and it was curated to make this harder |
| ResPlan | **one dwelling** | No |
| RPLAN | **one dwelling** | No |
| ProcTHOR-10k | **one house** | No |

### 3.1 Swiss Dwellings: `plan_id` is not a dwelling

The join hierarchy is `site_id → building_id → floor_id → plan_id →
apartment_id → unit_id → area_id`, and **`apartment_id` is unique per site
only** `[DOC]`. There is a `unit_usage` field with values
`RESIDENTIAL / COMMERCIAL / PUBLIC / JANITOR` `[DOC]` — so the corpus contains
non-residential units that must be filtered out.

45,176 apartments sit across roughly 13,900 plans `[INF, from MSD's stated
input size]` — about 3.2 dwellings per plan. **The 45,176 figure is the
dwelling count; the plan count is an order of magnitude smaller.** Any
reasoning that treats Swiss Dwellings as "45,176 floor plans" is wrong.

Extracting a dwelling from a floor plate is a real operation with real losses,
and it is where our **Envelope** concept enters. Per `CONTEXT.md`, a flat's
envelope is *given*; the cut boundary of an apartment out of its floor plate
**is** that given envelope. That is a genuinely good fit — Swiss Dwellings is
the only corpus that can teach what a real flat envelope looks like, including
its party walls.

What extraction destroys, and the mitigation:

- **Party-wall ambiguity.** A wall between two apartments is shared. After the
  cut it looks like an exterior wall but behaves like an interior one
  (no windows, different acoustic and structural role). *Mitigation: keep a
  per-segment `boundary_role ∈ {exterior, party, corridor_facing}` derived
  before the cut.* This must happen at extraction time; it is unrecoverable
  afterwards.
- **The circulation core disappears.** Stairs, lifts and the common corridor
  are outside the apartment, but the front door opens onto them. Cutting them
  away leaves a front door onto nothing. *Mitigation: retain the front-door
  segment and a `faces` label, not the corridor geometry.*
- **Neighbour context is lost**, which is fine for C5 and is exactly why MSD
  exists as a separate dataset.

### 3.2 MSD is a subset of Swiss Dwellings, filtered away from us

MSD's own curation, verbatim counts `[DOC]`, starting from ~13,900 SD plans:

| Step | Removed |
|---|---|
| non-residential details | 2,305 (16.6%) |
| near-duplicate `plan_id`s | 4,395 (31.6%) |
| **<15 areas, or fewer than two "Zone 2" areas** | 1,541 (11.1%) |
| further cleaning | 388 (2.8%) |
| **remaining** | **5,372** |

The third step is the one that matters: **MSD deliberately removed the small
plans.** Its purpose is multi-apartment complexes; C5 scopes us to single
dwellings. MSD is curated in precisely the opposite direction from our need.

And because MSD ⊂ SD, **its 18,943 apartments are a subset of SD's 45,176 —
they are not additional data.** MSD contributes **zero net dwellings.**

That is not the same as MSD being useless. Its genuine contributions are:

- **`graphs.py` — the graph-extraction algorithm**, i.e. how to turn SD
  geometry into a typed access graph. This is the part worth reusing (the code
  is unlicensed, but C9 means we care about the *method*, and we are
  reimplementing per C11 anyway).
- **The structural-wall heuristic**, verbatim: *"The base wall thickness for
  each floor plan is the 60% quantile of the full set of existing walls'
  thickness given a floor plan. Any wall with a thickness larger than the base
  thickness value is then regarded as a load-bearing wall."* `[DOC]` No corpus
  ships a load-bearing flag; this is the published way to derive one.
- **An out-of-scope stress test.** MSD is what "the model degrades outside its
  regime" looks like for us, and it is the natural held-out set for proving we
  have not accidentally built a multi-unit massing model.

**Recommendation: take MSD's methods, not MSD's data.** Rebuild the equivalent
directly from Swiss Dwellings, which also sidesteps the near-duplicate removal
being tuned for a different objective than ours.

### 3.3 Survival under C5 filtering

| Corpus | Nominal | Survives C5 (single dwelling, single storey) | Confidence |
|---|---|---|---|
| Swiss Dwellings | 45,176 apartments | **NOT ESTABLISHED.** Filters are specifiable now (§9.1); the counts need the data. | — |
| ResPlan | 17,000 | **~15,800** after removing the 1,170 self-reported near-duplicates (6.9%) | `[DOC]` + `[INF]` |
| RPLAN | 80,788 | 80,788 structurally — but 0 in the metric schema (§5) | `[SRC]` |
| MSD | 5,372 plans / 18,943 apts | **0 net** — subset of SD | `[DOC]` + `[INF]` |
| ProcTHOR-10k | 10,000 | 10,000 structurally; 0 as *architectural* records (§7.5) | `[DOC]` |

The one independent data point on Swiss Dwellings' survival rate is
Ospici et al., who preprocessed SD by *"filtering multi-floor buildings,
deduplication, retaining Manhattan samples, and extracting missing door
segments"* and were left with **"approximately 5k floor plans"** `[DOC]`.
Against ~13,900 input plans that is roughly **36% survival at the plan level**.

Do not read that as 36% of *apartments*. Their filter was plan-level and
whole-plan-rejecting (one non-orthogonal wall anywhere kills the floor); a
dwelling-level filter should survive better, because a maisonette or a skewed
unit only removes itself. But the "retain Manhattan only" cut is a genuine
warning: **if v1 assumes orthogonal walls** — and MAP lists non-orthogonal
geometry as not-yet-specified — **a large fraction of Swiss Dwellings is
excluded, and it is excluded non-randomly** (older and architecturally
distinctive buildings first). That is a bias worth measuring, not just noting.

### 3.4 The gap nobody has flagged: these are apartment corpora

C5 says *"Flats and houses"*. Per `CONTEXT.md`, that is two different problems —
a flat's Envelope is **given**, a house's Envelope is **invented**.

- Swiss Dwellings: apartments in multi-unit buildings. Envelope given.
- MSD: same, more so.
- RPLAN: residential apartments. Envelope given (the boundary is a model input).
- ResPlan: mostly flats, though `garden`, `parking` and `pool` keys imply some
  detached houses `[DOC, key list]`. Proportion **NOT ESTABLISHED**.
- ProcTHOR: houses, but the envelope comes from *"iterative boundary
  cutting"* `[DOC]` — a procedural shape, not a real footprint.

**No corpus in the candidate list teaches footprint invention for a detached
house.** Every one of them hands the model a boundary. This is a real hole in
the plan and it belongs to ticket 9 (*Building scope and envelope handling*),
which should be told: **the house half of C5 has no training data.** The
options are to scope v1 to flats, to treat house footprints as a solver/rule
problem rather than a learned one, or to find a house corpus — but that
decision cannot be made inside this ticket.

---

## 4. The common schema (ticket item 1)

### 4.1 There is a common schema, but only if it is stratified

A single flat schema across all five corpora exists and is nearly worthless:
room polygons normalised to a unit box, four room types, and door edges. That
is the greatest common denominator, and §4.3 shows why it collapses that far.

The useful move is to notice that **the boundary between what the corpora share
and what they do not falls exactly on a line `CONTEXT.md` already draws**:

> **Proposal** — what the learned model emits. Not a plan: a suggestion of
> topology and proportion, used as the solver's objective.
>
> **Plan** — the canonical geometry: walls with thickness, openings hosted on
> walls, spaces, and the annotation over them.

**Topology and proportion** is what every corpus can express, RPLAN included.
**Walls with thickness and hosted openings** is what only Swiss Dwellings and
ResPlan can express. So the schema should be two levels, and the level boundary
is the Proposal/Plan boundary. This is not a coincidence — it is the same
distinction seen from the data side.

### 4.2 Proposed schema — the Unified Dwelling Record (UDR)

Two levels. Every record has Level 0 and Level A; only metric corpora have
Level B.

#### Level 0 — provenance (mandatory, every record)

```
record_id                 "{corpus}:{native_id}"
corpus                    {swiss_dwellings | resplan | rplan | msd |
                           procthor | synthetic}
region                    {europe_ch | south_asia | china | none}
annotation_provenance     {cad_records | cv_traced_render |
                           manual_platform | procedural}
fidelity                  {metric_plan | scale_free_proposal}
native_record             <opaque blob: the untouched source record>
```

Two rules that are load-bearing:

- **`native_record` is never dropped.** Every lossy decision below is a *view*,
  not a replacement. Any of them can be revisited without re-downloading or
  re-deriving. This is the single cheapest insurance policy in the whole
  pipeline and it costs disk, which is free.
- **`corpus` and `region` are separate fields even though they nearly
  co-vary.** They are different confounds. See §6.2.

#### Level A — Proposal record (all corpora)

```
envelope_norm       polygon, normalised so the envelope bbox maps to the unit
                    square; aspect ratio NOT baked in
envelope_aspect     float, w/h — preserved separately so it stays learnable
rooms[]
  room_id
  type              canonical class (§4.3)
  native_label      verbatim source label — never discarded
  polygon_norm      polygon in envelope-normalised coordinates
  area_frac         fraction of envelope area          <- expressible by all
  centroid_norm
access_graph
  edges[]           {u, v, kind ∈ {door, open, adjacent_no_access}}
entry               room_id or edge the front door serves
orientation
  known             bool
  north_angle       radians, null if unknown
```

`area_frac` rather than `area_m2` is the whole point of Level A: **fractions are
expressible by every corpus, absolute areas are not.** §5.2 explains why that
distinction is fatal for RPLAN.

The three edge kinds match what the predecessor project settled on
(`EdgeKind.DOOR / OPEN / ADJACENT_NO_ACCESS`, read from
`../plan-generator-3000-pro-max/schema/room_types.py`) `[SRC]`. That is
independent convergence on the same GCD, which is mild evidence it is the right
cut.

#### Level B — Plan record (Swiss Dwellings, ResPlan; MSD partially)

```
scale               metres — real coordinates, not normalised
rooms[].polygon_m
rooms[].area_m2
walls[]
  polygon_m         wall footprint
  centerline_m      derived
  thickness_m       derived from the footprint
  is_structural     bool | null      <- NOT SHIPPED BY ANY CORPUS
openings[]
  type              {door, window, front_door}
  geometry_m
  width_m
  host_wall_id      | null           <- NOT SHIPPED BY ANY CORPUS
  sill_m            | null           <- Swiss Dwellings only
  head_m            | null           <- Swiss Dwellings only
fixtures[]          {kind, point_m}  <- Swiss Dwellings only
storey
  floor_index
  elevation_m
  ceiling_height_m                   <- Swiss Dwellings only, often defaulted
boundary_roles[]    per envelope segment: {exterior | party | corridor_facing}
```

Three fields are deliberately **nullable because no corpus ships them**:
`is_structural`, `host_wall_id`, and the sill/head pair outside Swiss
Dwellings. They must be *derived*, the derivation is a versioned pipeline step,
and **its error rate must be measured rather than assumed.** A schema that
pretended these were data would launder a heuristic into a fact — and
`host_wall_id` in particular is what C3's "hosted openings" and the IFC export
depend on. Ticket 3 should know that opening-to-wall hosting is a derived
relation everywhere, not a read.

### 4.3 The canonical room taxonomy, and where it collapses

Room-type vocabularies are the sharpest disagreement between the corpora, and
the collapse is worse than it looks.

**RPLAN's taxonomy, read from Graph2Plan's own loader** (`room_label` in
`../Graph2plan/PostProcess/g2p/utils.py`) `[SRC]`:

| id | label | | id | label |
|---|---|---|---|---|
| 0 | LivingRoom | | 9 | Balcony |
| 1 | MasterRoom | | 10 | Entrance |
| 2 | Kitchen | | 11 | Storage |
| 3 | Bathroom | | 12 | Wall-in |
| 4 | DiningRoom | | 13 | External |
| 5 | ChildRoom | | 14 | ExteriorWall |
| 6 | StudyRoom | | 15 | FrontDoor |
| 7 | SecondRoom | | 16 | InteriorWall |
| 8 | GuestRoom | | 17 | InteriorDoor |

Two observations that no summary of RPLAN mentions:

**(a) RPLAN encodes a Chinese family-structure convention, not a geometric one.**
`MasterRoom`, `ChildRoom`, `SecondRoom`, `GuestRoom` are **four distinct
bedroom classes separated by social role**. ResPlan has one `bedroom`. Merging
forces 4→1 and destroys the distinction; the alternative — asking the other
corpora to invent it — is worse. Note that **Graph2Plan itself performs this
collapse**: `DataPreparation/4.data_train_eNum.py` maps ids 1, 5, 6, 7, 8 all
onto a single class `[SRC]`. RPLAN's own primary consumer does not trust the
fine-grained bedroom labels, which is good evidence that we should not either.

**(b) RPLAN has no corridor class at all.** There is `Entrance` but nothing for
hallways or circulation. Swiss Dwellings labels corridors explicitly. So
RPLAN's circulation space is absorbed into adjacent rooms — most likely
`LivingRoom`. That is not a taxonomy mismatch, it is a **different theory of
what a room is**, and it means "living room area" is not comparable between
RPLAN and Swiss Dwellings even after label alignment. Any pooled model would
learn a bimodal living-room-size distribution that reflects annotation
convention, not architecture.

**The intersection, corpus by corpus:**

| Canonical class | SD | ResPlan | RPLAN | MSD | ProcTHOR |
|---|---|---|---|---|---|
| living | ✅ | ✅ | ✅ | ✅ | ✅ |
| kitchen | ✅ | ✅ | ✅ | ✅ | ✅ |
| bedroom | ✅ | ✅ | ✅ (×4) | ✅ | ✅ |
| bathroom | ✅ | ✅ | ✅ | ✅ | ✅ |
| balcony | ✅ | ✅ | ✅ | ✅ | ❌ |
| storage | ✅ | ✅ | ✅ | ✅ | ❌ |
| dining | ✅ | ❌ | ✅ | ✅ | ❌ |
| entrance | ✅ | ❌ (opening only) | ✅ | ✅ | ❌ |
| circulation / corridor | ✅ | ~ (`stair`) | ❌ | ✅ | ❌ |
| utility / technical | ✅ | ❌ | ❌ | ✅ | ❌ |
| garden / pool / parking | ❌ | ✅ | ❌ | ❌ | ❌ |

> Swiss Dwellings' full `entity_subtype` enumeration is **NOT ESTABLISHED** from
> published documentation — the Archilyse page gives only examples (`WALL`,
> `LIVING_ROOM`) and does not publish the closed set. Its column marks above are
> `[INF]` from the dataset description's *"areas (rooms, bathrooms, kitchens,
> balconies)"* and the simulation feature list. **This is the single biggest
> documentation gap in this pass** and ticket 12 must resolve it by
> `SELECT DISTINCT entity_subtype` on the real file.

**Counting the intersection:**

- Across **all five**: 4 classes (living, kitchen, bedroom, bathroom).
- Across **SD + ResPlan + RPLAN + MSD**: ~6.
- Across **SD + ResPlan** only: ~8–10.

Independent corroboration: ResPlan's own cross-dataset experiment used exactly
**five** classes — bedroom, bathroom, kitchen, living, balcony `[DOC]`. Two
different analyses arriving at 4–5 as the workable intersection is a strong
signal that this is the real ceiling.

**So including RPLAN and ProcTHOR costs roughly half the room taxonomy.**
That is a concrete, quantified price for merging, and it is paid by every
record in the merged set, not just by the ones that came from RPLAN.

**Design rule:** the **Brief** taxonomy and the **corpus** taxonomy are
different objects. The predecessor's Brief vocabulary has 42 room types `[SRC]`
against a corpus GCD of 4. Do not force the Brief down to the corpus GCD — keep
the rich user-facing vocabulary, and make the Brief→corpus mapping an explicit,
versioned, many-to-one projection whose losses are recorded. The sibling project
already learned this the hard way and wrote it down as *"42 room types → 9
usable / heavy many-to-one mapping"* `[EXEC]`.

---

## 5. Can RPLAN be vectorised? (ticket item 2)

**Partly. It vectorises to topology and proportion. It does not vectorise to
geometry, and it never will, because the missing information was never
recorded.**

### 5.1 What is actually there

RPLAN ships **raster only**; there is no native vector release `[DOC]`. The
vectors that circulate — Graph2Plan's `boundary`, `rType`, `rBoundary`,
`gtBox`, `rEdge` — are a **derived product** distributed as a preprocessed
`data.mat`, not part of the RPLAN release `[SRC]`, confirmed against the local
Graph2Plan checkout's `DataPreparation/` pipeline.

The canvas is **256 × 256 pixels**, and the sibling project verified by running
the model that coordinates are mapped `pixels/256 - 0.5`, then ×2, into
`[-1, 1]` with origin at the image centre `[EXEC]`. Graph2Plan's own input
rendering is at **128 × 128** `[SRC]`, i.e. it throws away half the resolution
again before the model ever sees it.

### 5.2 What is irrecoverably lost

**(a) Metric scale — the fatal one.** *"There is no per-plan scaling: a plan's
real-world size is not represented"* `[EXEC]`. A pixel corresponds to no known
distance.

This cannot be repaired. You could *estimate* scale by assuming a typical
apartment area — but that means injecting a regional area prior, which is
exactly the regional convention we are trying to hold as a variable rather than
a hidden assumption. Worse, C3's hard floor is a **dimensioned** plan and C4's
Brief carries **requested room areas**. A corpus with no absolute scale
therefore cannot participate in area-conditioned training *at all*: there is no
target for "make the kitchen 9 m²". **RPLAN can only ever train unconditional
proportion.** Given that the Brief is the real interface (C4), a corpus that
cannot be conditioned on the Brief's most concrete field is contributing much
less than its 80,788 records suggest.

**(b) Wall thickness.** Walls exist as a raster band. At a plausible ~12 m plan
width on a 256 px canvas, one pixel is roughly **4–6 cm** `[INF]` — so a 10 cm
partition is ~2 px and a 25 cm structural wall is ~4–5 px. Thickness is
quantised at roughly the granularity of the distinction we need, and since the
scale is unknown you cannot express the result in centimetres anyway. For
comparison, ResPlan reports a median wall thickness of 21 cm with 99.3% between
10 and 40 cm `[DOC]` — the entire distribution we care about spans about 6
pixels.

**(c) Windows.** Not present. RPLAN's opening semantics are `FrontDoor` and
`InteriorDoor` `[SRC]`, and in the HouseDiffusion derivation doors appear as
*room-like boxes* in the sequence rather than as openings hosted on walls
`[EXEC]`. There is no window channel to recover.

**(d) Orientation.** RPLAN plans are re-oriented to be axis-aligned `[DOC, per
Ospici et al.]`. Compass orientation is destroyed, which matters for daylight —
one of the things Swiss Dwellings pre-computes and MSD explicitly preserves.

**(e) Non-door adjacency.** The only relation carried through is
door-connectivity; *"there is no representation of 'adjacent but no access'"*
`[EXEC]`. Note also that Graph2Plan's `rEdge` is not an access graph at all —
its relations are **spatial** (`left/right/above/below/surrounding/inside`),
computed from bounding boxes `[SRC]`. Two different things travel under the
name "the RPLAN graph" and they are easy to confuse.

### 5.3 The answer to the ticket's question

**Yes — including RPLAN in the shared schema forces it down to a scale-free,
wall-less, window-less, orientation-free box-and-door representation.** That is
a strong argument for excluding it from the metric schema, and the ticket's
framing anticipated this correctly.

But the right conclusion is not "throw RPLAN away", it is "**RPLAN is admissible
in the Proposal space and inadmissible in the Plan space**" — which is exactly
the Level A / Level B split of §4.2, and which is why that split is drawn where
it is.

Whether it should be used even in Level A is a separate question, answered in
§7.3: probably not, on measured evidence.

---

## 6. Should region be an explicit conditioning variable? (ticket item 3)

**Yes. And conditioning on region alone is a mistake — condition on
`(region, corpus, annotation_provenance)`.**

### 6.1 Why conditioning weakly dominates pooling

A conditioned model can always learn to ignore its conditioning token, which
recovers the pooled model exactly. So conditioning cannot be worse than pooling
in representational terms; it can only be worse through optimisation or
overfitting effects, which at 4 categorical values are negligible. Meanwhile
pooling *cannot* recover conditioning. **Pooling is a strict special case of
conditioning, chosen by the modeller rather than learned from data**, and there
is no reason to make that choice on the model's behalf. `[INF]`

The cost is one requirement: **at inference you must supply a value.** That is a
product decision, not a modelling one, and it is cheap here — see §6.3.

### 6.2 Why region alone is not enough

Region is a proxy for the thing that actually varies. At least three distinct
confounds travel together in these corpora:

| Confound | Swiss Dwellings | ResPlan | RPLAN |
|---|---|---|---|
| **Architectural convention** | Swiss/European | South Asian | Chinese |
| **Annotation pipeline** | digitised from building records, manual QA `[DOC]` | CV-traced from listing renderings `[DOC]` | manually annotated on a commercial platform `[DOC]` |
| **What counts as a room** | corridors labelled | no corridor class | circulation absorbed into living |

A single `region` token would force the model to absorb *"South Asian"* and
*"traced by computer vision from a marketing render"* into one embedding. Those
have different consequences: the first is a convention we may want to
reproduce; the second is an artefact we never want to reproduce.

Separating them buys a concrete capability. ResPlan's vectorisation artefacts
are documented — 0.52% of room polygons exceed 30 vertices, 0.02% exceed 100,
and **wall thickness is normalised per plan**, erasing within-plan variation
between structural walls and thin partitions `[DOC]`. If those artefacts are
attributed to `annotation_provenance = cv_traced_render`, then at inference you
set `annotation_provenance = cad_records` and the model generates in the clean
convention while still using ResPlan's 15,800 records for everything else.

This is the standard source-tagging / quality-tagging move from large-scale
pre-training: **train on the dirty data with the dirt labelled, generate with
the label set to clean.** `[INF]` — I could not verify a floor-plan-specific
instance of it, and the general-ML literature search for this pass was cut
short (§10), so treat it as a well-founded technique borrowed by analogy rather
than a demonstrated result in this domain.

### 6.3 What this does to *What the model proposes* (ticket 8)

The ticket correctly anticipates that this changes ticket 8's input contract.
The change is small and it fits C4's existing machinery:

- The Proposal conditioning gains **three categorical fields**, all with
  defaults.
- The Brief (C4) gains a **`convention` field** — and per C4 every invented
  value is surfaced as an **Assumption**. "Layout convention: European
  (assumed)" is precisely the kind of assumption C4 exists to expose, and it is
  one a Homeowner can meaningfully accept or change, unlike most of what is in
  there.
- **A default is now mandatory.** C12 says we are not tied to any region, but
  the model must pick *some* convention to generate in; "no region" is not a
  layout. **Recommend defaulting to `europe_ch` / `cad_records`** — the largest,
  cleanest, best-provenanced corpus, and the one whose openings carry real sill
  and head heights.
- **`fidelity` must also be conditioned on** if any scale-free corpus is ever
  mixed in, so that "no metric scale" is a labelled property of the training
  record rather than noise in the area distribution.

### 6.4 The honest counter-argument

The case against conditioning is that with only two corpora in the target mix
(§7), a `corpus` token has two values and is close to just training two models —
at which point you have not combined anything, you have interleaved.

That objection is fair and should be answered empirically, not rhetorically. It
is also *the* cheap experiment to run first (§11): train conditioned, then at
inference sweep the token and measure whether the outputs actually differ in the
ways the corpora differ (room counts, corridor prevalence, balcony frequency,
wet-room clustering). **If the token does nothing, the corpora were more alike
than the transfer numbers implied, and pooling was fine all along.** That is a
falsifiable prediction, and it is the right first thing to test.

---

## 7. What each corpus is actually for (ticket item 5), and merge vs split

The ticket asks whether a split-role answer beats a merged one. Argued honestly,
**neither wins outright** — the answer is a merge for two corpora and a split for
the rest, and the split is *forced by the data* rather than preferred.

### 7.1 The case against split-role

Worth stating properly, because it is stronger than it first appears.

- **"Different corpus per component" just relocates the unification problem.**
  If ResPlan trains the graph proposer and Swiss Dwellings trains the geometry
  refiner, the two components still have to agree on a room taxonomy, a scale
  convention and an edge vocabulary at their interface. You have moved the
  merge from the data layer to the module boundary, where it is harder to test.
- **"ResPlan for typed adjacency graphs" is a weak role.** Swiss Dwellings can
  produce typed access graphs too — **MSD is the existence proof**, since its
  entire contribution is a graph-extraction algorithm run on SD geometry
  `[DOC]`. ResPlan's graph is convenient, not unique. Its real distinctive value
  is being a *second region* with clean single-dwelling records.
- **More components means more places to be mediocre.** For a v1 whose model is
  only a soft objective (C10), and where ticket 8 lists LLM and retrieval as
  live alternatives to training at all, a multi-corpus multi-component training
  architecture is a lot of machinery to justify.

### 7.2 Where split-role genuinely wins

Two of the splits are not preferences, they are consequences:

- **RPLAN cannot enter the metric schema** (§5). Its role is different because
  its representation is different. No amount of wanting a merge changes that.
- **Synthetic data must not enter the plausibility mix.** Ospici et al.'s
  generator works *because* it sacrifices architectural realism `[DOC]`. Putting
  such data in the fine-tuning set would teach the model that implausible
  layouts are plausible — the exact opposite of what the model is for. Its place
  is a separate earlier stage, by construction.

So the shape of the answer is three tiers, not five roles and not one pool.

### 7.3 Tier 1 — pre-training: synthetic, and RPLAN only on probation

The evidence here is unusually clean, and it inverts the ticket's assumption
that RPLAN's role is "pre-training scale":

| Pre-training source | Result | Source |
|---|---|---|
| **RPLAN → fine-tune on ResPlan** | **+0.4 pp at 1% data, nothing at ≥5%** | ResPlan authors `[DOC]` |
| **Unrealistic synthetic → fine-tune on RPLAN** | **41.7% error reduction at 1k samples** | Ospici et al. `[DOC]` |

The corpus with 80,788 plans fails as a pre-training source; procedurally
generated data explicitly designed to be architecturally implausible succeeds.
ResPlan's authors call the gap **structural**, and that word is doing real work:
more RPLAN data does not close it.

> **Caveat, stated plainly.** These are two different tasks (node classification
> vs layout generation), two model families, and two research groups. This is not
> a controlled comparison and I am not presenting it as one. What it is: two
> independent primary results pointing the same way, with a mechanism (§2.3) that
> explains both. That is enough to *demote* RPLAN from assumed-useful to
> must-prove-itself. It is not enough to forbid it.

**Recommendation: build a synthetic generator rather than download one.**
Ospici et al.'s recipe is published in enough detail to reimplement `[DOC]` —
polygon sampling, then aspect-ratio distortion in [0.8, 1.25], 1–3 rectangular
bumps per shape, random flips and {0°,90°,180°,270°} rotations, global scale in
[0.7, 1.6], edge-packing assembly of 2–10 rooms maximising shared boundaries
with no overlaps, and doors placed on shared wall segments at sampled fractions
of the shared boundary. They generated 135,000 scenes. Their ablation is
pointed: **removing the shape augmentations costs +23 average MPE** — the
irregularity is not incidental, it is the mechanism.

This also happens to be the cheapest item on the whole roadmap: it needs no
downloads, no licences, no application forms, and it can be built and tested
before ticket 12 finishes.

### 7.4 Tier 2 — the target mix: Swiss Dwellings + ResPlan, conditioned

**This is the merge, and it is the only one this document endorses.**

Both are metric vector corpora with wall geometry and explicit openings, so they
share Level B. Together they give ~15,800 ResPlan dwellings plus an
as-yet-unknown but probably larger number of Swiss Dwellings apartments, across
two genuinely different conventions, with the convention held as a labelled
variable rather than averaged away. That is a direct, honest reading of C12's
*"combine corpora where it can be made to work"* — combined where it works,
and not where it doesn't.

Division of labour inside the merge:

- **Swiss Dwellings** — the backbone. The only corpus with 2.5D
  (`elevation` + `height`), which makes it **the only source of window sill and
  head heights** anywhere in the candidate list. C3 requires hosted openings and
  the IFC export path needs sill heights, so this is not a nice-to-have. It also
  has ~315,000 fixtures (sinks, toilets, bathtubs) `[DOC]`, which is the data
  behind MAP's open question on furniture-fit, and it has real flat envelopes
  including party walls (§3.1). Caveat: heights *"may be defaulted rather than
  precisely measured"* `[DOC]` — so sill heights must be checked for a
  suspicious mode at the default value before being trusted.
- **ResPlan** — the second convention, and the cleanest single-dwelling records
  in the set (no extraction step, no multi-unit context). Its typed graph is a
  convenience that saves building the extraction first, not a unique asset.

### 7.5 Tier 3 — not training data

- **MSD**: subset of SD, curated away from C5, zero net dwellings (§3.2). Use
  its graph-extraction method and its structural-wall heuristic; use the dataset
  as an out-of-scope stress test.
- **ProcTHOR-10k**: this one deserves a specific warning. Its floor plans are
  produced by *"iterative boundary cutting"* followed by *"the recursive layout
  generation algorithm by Lopes et al."* `[DOC]` — reference [35] in the paper
  is *"A constrained growth method for procedural floor plan generation",
  Game-ON, 2010* `[SRC, from the paper's own bibliography]`. **ProcTHOR's layout
  prior is a 2010 video-game level-generation algorithm.** Pre-training a
  plausibility model on it teaches the model that algorithm, not architecture.
  Combined with only four room types (Bedroom, Bathroom, Kitchen, Living Room
  `[DOC]`) and no corridors, entrances, balconies or utility spaces, ProcTHOR
  is a weaker synthetic source than a purpose-built generator — it has neither
  the realism of a real corpus nor the deliberate constraint-focused
  irregularity that makes Ospici et al.'s synthetic data transfer. It occupies
  the worst of both positions.

  If synthetic data is wanted immediately and cheaply, ProcTHOR is a reasonable
  stopgap. It should not be the plan.

### 7.6 Retrieval changes the calculus, and ticket 8 should know

Ticket 8 lists **retrieval** (Graph2Plan's idea: find the closest real plan and
adapt it) as a live v1 route needing no training. If retrieval is chosen, this
entire analysis simplifies dramatically: **retrieval needs one corpus in the
target region with real geometry, and nothing else.** Pooling becomes
meaningless, pre-training becomes irrelevant, and the answer is simply "Swiss
Dwellings, plus ResPlan when the user wants South Asian conventions."

Given the sibling project's measured warning that a trained generator degraded
badly outside its regime and repair recovered *"31% / 7% / 0%"* of the damage,
retrieval deserves to be the baseline that training must beat. **Nothing in this
document should be read as an argument that the trained route has been
chosen** — it is an argument about what to train *on*, if training happens.

---

## 8. Per-corpus conversion notes, and what each conversion destroys

### 8.1 Swiss Dwellings → UDR Level B

**Steps.** Filter `unit_usage = RESIDENTIAL`; group areas, separators, openings
and features by `(site_id, apartment_id)`; reject apartments spanning more than
one `floor_id` (maisonettes); parse WKT (already metres, local per-site,
+y north); derive wall centrelines and thickness from separator polygons; derive
`host_wall_id` by geometric containment of each opening in a separator; derive
`is_structural` via MSD's 60%-quantile rule; label envelope segments
`exterior / party / corridor_facing` **before** cutting the apartment out;
extract the access graph.

**Destroys:**

| Loss | Severity |
|---|---|
| Multi-unit context, corridor cores, stairwells | Intended (C5) but see §3.1 — the front door is left opening onto nothing |
| Party-wall identity, if not captured before the cut | **Unrecoverable.** Mitigate as above |
| Maisonettes and any non-orthogonal stock, if a Manhattan filter is applied | Non-random loss, biased against older and distinctive buildings (§3.3) |
| The 367 simulation columns (daylight, noise, view, centrality) | Dropped from UDR, but they are exactly MAP's "dashboard metrics" open question — **keep them joined by `area_id`, do not discard** |
| Real vs defaulted heights | `height` *"may be defaulted"* `[DOC]`; the 2.5D layer is partly synthetic and must be flagged, not trusted |

**Does not destroy:** geometry (already metric vector), openings, fixtures,
orientation, taxonomy (richest of the five).

### 8.2 ResPlan → UDR Level B

**Steps.** Load the pickle (needs `shapely`); map per-class polygon keys
(`living`, `kitchen`, `bedroom`, `bathroom`, `balcony`, `storage`, `stair`,
`garden`, `parking`, `pool`) to canonical types, preserving the key as
`native_label`; take `wall` + `wall_depth` as wall geometry; take `door`,
`window`, `front_door` as openings; use `neighbor` / the typed graph for
`access_graph`; drop the 1,170 near-duplicates.

**Destroys:**

| Loss | Severity |
|---|---|
| **Within-plan wall thickness variation** — `wall_depth` is normalised per plan `[DOC]` | **Serious.** Structural vs partition distinction is *already gone in the source*. MSD's 60%-quantile heuristic **cannot be applied to ResPlan** — there is no within-plan variation left to threshold |
| No dining / entrance / corridor classes | Systematic absence, not missing labels — see the RPLAN corridor point in §4.3; the same comparability problem applies |
| Traced-contour artefacts (0.52% of polygons >30 vertices) `[DOC]` | Manageable; simplify and record the simplification |
| `garden` / `pool` / `parking` have no counterpart elsewhere | Map to an outdoor class; keep `native_label` |
| Two incompatible graph definitions in the released tooling `[DOC]` | **A trap.** `plan_to_graph()` gives ~8.7 edges/plan over 5 types; the published benchmarks additionally call `add_adjacency_edges()` for 12.9 edges/plan over 4 types. Pick one, record which, never mix |

The wall-thickness row is the important one: **ResPlan cannot contribute
load-bearing-wall supervision at all.** Only Swiss Dwellings can.

### 8.3 RPLAN → UDR Level A only

**Steps.** Vectorise room regions by contour tracing (RPLAN-Toolbox, or
Graph2Plan's derived `rBoundary` / `gtBox`); normalise the boundary to the unit
square; collapse the four bedroom classes; derive door edges from the
`FrontDoor` / `InteriorDoor` semantics; set `region = china`,
`fidelity = scale_free_proposal`.

**Destroys:** absolute scale (§5.2a — and with it any possibility of
area-conditioned training), wall thickness (§5.2b), all windows (§5.2c),
compass orientation (§5.2d), non-door adjacency (§5.2e), and the bedroom
sub-taxonomy (§4.3a). Plus a subtler one: **RPLAN's rooms are frequently
handled as axis-aligned bounding boxes** (`gtBox`) rather than polygons in the
downstream ecosystem `[SRC]`, so shape fidelity depends on which derived
artefact you take.

**Net:** what survives is topology and proportion. That is a Proposal, and
nothing more.

### 8.4 MSD → not converted

Not ingested as training data. Convert only for held-out stress testing, in
which case it maps to Level B with room polygons in metres `[DOC]` but **no
wall or opening geometry as node attributes** — MSD's edges carry connectivity
types (`passage`, `door`, `front door` `[DOC]`) rather than opening geometry, so
Level B's `openings[]` would be empty. Its zone taxonomy is 4 classes: zone1
private, zone2 public, zone3 service, zone4 outside `[DOC]`.

### 8.5 ProcTHOR-10k → UDR Level A, flagged synthetic

**Destroys:** nothing, because there is nothing architectural to destroy. The
issue is the opposite — it *adds* a procedural prior. Convert with
`region = none`, `annotation_provenance = procedural`, four room types, and
never mix it into a fine-tuning set.

**NOT ESTABLISHED:** whether ProcTHOR walls carry a real thickness. AI2-THOR
walls are believed to be effectively planar, but I could not read
`procthor/generation/` this pass (GitHub raw was rate-limited throughout).
Assume Level A only until checked.

---

## 9. Concrete next actions

### 9.1 Queries to run the moment ticket 12 lands

These are the questions this pass could not answer without the data. Each is a
one-liner and each has a decision hanging on it.

1. `SELECT DISTINCT entity_type, entity_subtype FROM geometries` — the closed
   Swiss Dwellings taxonomy. **Blocks the canonical taxonomy mapping** (§4.3).
2. `SELECT COUNT(DISTINCT floor_id) per (site_id, apartment_id)` — how many
   apartments are maisonettes, i.e. the real single-storey survival rate (§3.3).
3. Count apartments by `unit_usage` — how much of the 45,176 is residential.
4. Fraction of apartments whose separator polygons are all axis-aligned — the
   cost of an orthogonal-only v1 (§3.3), and whether the Ospici ~36% plan-level
   figure translates to something better at dwelling level.
5. Distribution of `height` and opening `elevation` — how much of the 2.5D layer
   is a defaulted constant (§7.4).
6. Whether any opening polygon fails to sit inside exactly one separator
   polygon — the error rate of derived `host_wall_id`, which C3 and ticket 3
   depend on.
7. ResPlan: confirm the metres-vs-pixels conversion key, and which of the two
   graph definitions the shipped pickle carries (§8.2).
8. Overlap check: how many Swiss Dwellings apartments also appear in MSD,
   confirming the subset claim of §3.2 empirically.

### 9.2 The experiment that settles the merge question

Cheapest decisive test, and it does not need the full pipeline:

Train the same small model three ways on Swiss Dwellings + ResPlan —
**(a) pooled unconditioned, (b) conditioned on `(region, corpus)`, (c) two
separate per-corpus models** — and evaluate each on both corpora's held-out
sets. Then sweep the conditioning token in (b) and measure whether outputs shift
along the axes the corpora actually differ on: room count, corridor prevalence,
balcony frequency, wet-room clustering, area distribution.

- If (b) ≈ (c) on both test sets and the token sweep moves those statistics,
  **conditioned merging works** and this document's recommendation stands.
- If (a) ≈ (b) ≈ (c), the corpora were compatible and pooling was fine —
  cheerfully simplify.
- If (c) beats (b), conditioning is insufficient and the corpora should be kept
  apart entirely.

Note that (a) is the experiment nobody in the literature has run (§2.2), so this
is worth doing on its own merits.

### 9.3 Build before you download

The synthetic generator (§7.3) needs no data and no licences. It is the
highest-evidence, lowest-dependency item identified in this pass and it is not
blocked by ticket 12.

---

## 10. What is verified, and what is not

**Verified against real data: nothing.** The corpora are not downloaded. This is
the honest headline and it should govern how much the next session trusts the
numbers here.

**Verified against primary source code on disk:**

- RPLAN's 18-entry `room_label` taxonomy, and Graph2Plan's own collapse of the
  bedroom classes — `../Graph2plan/PostProcess/g2p/utils.py`,
  `DataPreparation/4.data_train_eNum.py`.
- Graph2Plan's `rEdge` being *spatial* relations, not access —
  `PostProcess/g2p/floorplan.py`.
- Graph2Plan's derived-vector pipeline and 128×128 input rendering.
- The predecessor's `EdgeKind` and 42-type room vocabulary —
  `../plan-generator-3000-pro-max/schema/room_types.py`.

**Verified by execution, in the sibling project, per C11 needing re-verification:**

- RPLAN's 256 px canvas, absence of per-plan scale, door-only adjacency, and the
  9-usable-room-type ceiling — `../plan-generator-3000-pro-max/docs/rplan_format.md`.
  Note this describes HouseDiffusion's *preprocessed* RPLAN, which is two
  derivations away from the raw release.

**From documentation only** — everything else, including all Swiss Dwellings
schema detail, all ResPlan schema detail, MSD's structure, ProcTHOR's
generation method, and every transfer number in §2.

**Not established, and it matters:**

- Swiss Dwellings' closed `entity_subtype` enumeration (§4.3). Biggest gap.
- Swiss Dwellings' single-storey and orthogonality survival rates (§3.3).
- Whether ProcTHOR walls have thickness (§8.5).
- ResPlan's flat-vs-house proportion (§3.4).
- MSD's per-node apartment identifier — the paper does not document one, so
  extracting individual apartments from MSD may not be straightforward `[DOC]`.
  Moot given §3.2, but it would matter if MSD were ever reconsidered.

**Method limits of this pass, stated so they are not mistaken for absence of
evidence:**

- The session's web-search budget was exhausted early, so §6.2's source-tagging
  argument and the general multi-domain-training literature rest on analogy
  rather than a systematic survey. **A literature pass on domain conditioning
  was not completed and is a legitimate follow-up.**
- `raw.githubusercontent.com` rate-limited throughout, so `resplan_utils.py`,
  MSD's `constants.py` and ProcTHOR's generation modules were not read directly.
  Several taxonomy details that could have been `[SRC]` are only `[DOC]`.
- CubiCasa5K and Structured3D were excluded by the ticket's candidate list but
  are newly eligible under C9 (§1.1) and were not evaluated.

---

## 11. Summary answers to the five items

1. **Common schema?** Yes, but stratified — Level A (topology + proportion,
   scale-free) and Level B (metric, walls with thickness, hosted openings). The
   boundary falls exactly on `CONTEXT.md`'s Proposal/Plan line. A single flat
   schema across all five collapses to four room types and no walls. §4.
2. **RPLAN vectorisable?** To topology and proportion, yes. To geometry, no —
   scale, thickness, windows and orientation were never recorded. Including it
   in the shared schema does force the common denominator down. §5.
3. **Region as a conditioning variable?** Yes, and condition on
   `(region, corpus, annotation_provenance)` rather than region alone. Costs
   ticket 8 three categorical fields and C4 one surfaced Assumption; requires
   picking a default, recommended `europe_ch`. §6.
4. **Do they agree on what a plan is?** No. Swiss Dwellings and MSD records are
   *floors*, not dwellings. MSD is a subset of Swiss Dwellings filtered in the
   opposite direction from C5 and contributes zero net dwellings. ResPlan
   survives nearly whole (~15,800). Swiss Dwellings' survival rate is the key
   unknown. And **no corpus teaches house-footprint invention** — the house half
   of C5 has no training data. §3.
5. **What each is good for, and merge vs split?** A merge for Swiss Dwellings +
   ResPlan under a conditioning tag; a forced split for the rest. RPLAN's
   assumed role — pre-training scale — is the one role with published evidence
   against it. Synthetic pre-training, built rather than downloaded, is the
   highest-evidence and lowest-dependency item on the list. §7.

---

## Sources

**Primary, fetched this pass**

- Ospici, Gueze, Bourrat & Bernhardt, *Mitigating Domain Shift in Conditioned
  Floor Plan Generation: Synthetic Pre-training for Data-Efficient Adaptation*,
  arXiv [2607.06483](https://arxiv.org/abs/2607.06483), July 2026 —
  transfer table, synthetic recipe, ablations, the "assembly rules vs style"
  argument.
- Abouagour & Garyfallidis, *ResPlan*, arXiv
  [2508.14006v2](https://arxiv.org/abs/2508.14006) — transfer experiment
  definition, the RPLAN-pre-training result, regional-scope statement.
- van Engelenburg et al., *MSD: A Benchmark Dataset for Floor Plan Generation of
  Building Complexes*, arXiv [2407.10121](https://arxiv.org/abs/2407.10121)
  and [github.com/caspervanengelenburg/msd](https://github.com/caspervanengelenburg/msd)
  — curation counts, zone taxonomy, structural-wall heuristic, metric
  coordinates.
- Deitke et al., *ProcTHOR*, NeurIPS 2022 —
  [proceedings.neurips.cc](https://proceedings.neurips.cc/paper_files/paper/2022/hash/27c546ab1e4f1d7d638e6a8dfbad9a07-Abstract-Conference.html)
  — generation pipeline, Lopes et al. reference, room types, 10k statistics.
- Swiss Dwellings v3.0.0 — Zenodo
  [record 7788422](https://zenodo.org/records/7788422) and the
  [Archilyse schema page](https://archilyse.standfest.science/swiss-dwellings)
  — join hierarchy, `unit_usage` values, WKT/metres, 2.5D caveat.

**Primary, read on disk**

- `../Graph2plan/PostProcess/g2p/utils.py`,
  `../Graph2plan/DataPreparation/4.data_train_eNum.py`,
  `../Graph2plan/PostProcess/g2p/floorplan.py`
- `../plan-generator-3000-pro-max/docs/rplan_format.md`,
  `../plan-generator-3000-pro-max/schema/room_types.py`

**In-repo**

- `docs/research/floorplan-generation-stack.md` §2, §3, §3.2 — built on, and
  corrected in §1.
