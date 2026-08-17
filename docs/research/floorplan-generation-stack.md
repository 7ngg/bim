# Open floor-plan generation model & dataset stack — state of play (August 2026)

Research note for a **commercial** product. The decisive axis throughout is
**licence / commercial-use terms**, not benchmark scores.

Every claim below is tied to a primary source (arXiv abstract page, GitHub API,
raw `LICENSE` file, project page, Zenodo/4TU record). Where a fact could not be
confirmed from a primary source it is marked **UNCONFIRMED** rather than guessed.

Method note: GitHub facts were read from `api.github.com` and
`raw.githubusercontent.com` (not from README prose). `ResPlan.pkl` was downloaded
and inspected directly.

---

## TL;DR — the decisive facts

| Thing | Commercially usable? | Why |
|---|---|---|
| **RPLAN dataset** | **No** | ToU clause 1 *"non-commercial research and educational purposes"*, clause 2 no redistribution, **clause 7 binds your for-profit employer too** |
| **Graph2Plan code** | **No** | **No `LICENSE` file at all** → all rights reserved by default |
| **Graph2Plan weights** | n/a | **No pretrained weights released**; and any weights you train are RPLAN-derived → tainted by RPLAN's non-commercial clause |
| **ResPlan dataset** | **Yes** | Data CC BY 4.0, code MIT (verified in repo `LICENSE`) |
| **Swiss Dwellings** | **Yes** | CC BY 4.0 on Zenodo; 45,176 apartments with real walls/doors/windows |
| **MSD (Modified Swiss Dwellings)** | **Yes, with a copyleft caveat** | Two releases: 4TU 2023 challenge set = **CC BY 4.0**; Kaggle ECCV-2024 set = **CC BY-SA 4.0** (copyleft). Repo *code* is unlicensed. |
| **ProcTHOR-10k** | **Yes** | Apache 2.0; 10k *synthetic* houses — zero provenance risk |
| **CubiCasa5K** | **No** | CC BY-**NC** 4.0 (verified in repo `LICENSE`) |
| **Structured3D** | **No** | Non-commercial research/education only; binds for-profit employers |
| **LIFULL HOME'S** | **No** | *"Applications from those belonging to a private company, etc. will not be accepted"* — **a company cannot even apply** |

And on the model side:

| Model | Code licence | Commercial? |
|---|---|---|
| HouseGAN / House-GAN++ | GPL-3.0 + `THIS CODE CAN ONLY BE USED FOR RESEARCH PURPOSES` header | **No** |
| **HouseDiffusion** | *"code and the model weights … not allowed for commercial usage"* | **No — explicit** |
| WallPlan | **no LICENSE file** | **No** |
| Tell2Design | **no LICENSE file exists** (README claims Apache 2.0 but the link 404s), **data CC BY-NC** | **No** |
| **MaskPLAN** (CVPR 2024) | **MIT** | **Code yes** — weights are RPLAN-derived |
| **FloorplanGAN** | **MIT** | **Code yes** |
| **LayoutBridge** (2026) | **MIT** | **Code yes** |
| **Raster2Seq** (SIGGRAPH 2026) | **MIT** | **Code yes** — weights trained on CC BY-NC data |
| GSDiff (AAAI 2025) | GPL-3.0 | copyleft — poisons a closed product |
| OR-Tools CP-SAT / kiwisolver / HiGHS / SCIP / Z3 | Apache 2.0 / BSD / MIT | **Yes, all of them** |

**Practical conclusion:** the Graph2Plan + RPLAN pairing that most blog posts
recommend is a **licensing dead end for a commercial product**. The
commercially-clean substrate as of 2026 is:

- **Data — Swiss Dwellings (CC BY 4.0)** for a BIM engine specifically. It is the
  only corpus with a real building hierarchy (`site → building → floor → plan →
  apartment → unit → area`), **WKT geometry in metres**, explicit
  walls/railings/columns/windows/doors/fixtures, **and 2.5D `elevation`+`height`**.
  45,176 apartments, named corporate rights-holder (Archilyse AG), clean provenance.
  Add **ResPlan (CC BY 4.0)** for its typed room-connectivity graphs and
  ML-readiness, and **ProcTHOR-10k (Apache 2.0)** for unlimited synthetic pre-training.
- **Model — an MIT-licensed architecture retrained from scratch**, or better, a
  clean-room reimplementation from the paper. **Never a downloaded checkpoint.**
- **Constraints — OR-Tools CP-SAT (Apache 2.0)** for the guarantees, kiwisolver
  (BSD) for interactive editing.

And note you can ship a genuinely useful v0 (§5.6) with **no third-party data at
all**.

Five things worth internalising before reading further:

1. **Not one published model emits walls with thickness.** Zero, across ~20
   generators from 2020 to 2026. Exactly **one** emits windows (GFLAN, which has
   no code). You are not shopping for a floorplan engine — you are shopping for a
   *room-topology proposer* to sit in front of your own parametric layer. See the top of §4.
2. **The data licence gate closes more often than the code licence gate.** An MIT
   repo trained on RPLAN gives you usable *code* and unusable *weights*.
   And **RPLAN's terms bind your employer, not just the individual** (clause 7).
3. **Automated licence scanning gives false clears here.** GitHub renders
   HouseDiffusion as "GPL-3.0" while its actual `LICENSE` bans commercial use.
   Three of the most-starred repos in this field would pass an SBOM check. See the top of §4.
4. **Nothing here emits BIM.** ResPlan is the only dataset in the list that even
   *contains* wall thickness and door/window polygons as first-class fields.
5. **The regional-convention gap is first-order.** ResPlan's own numbers: a model
   trained on RPLAN scores 0.909 on RPLAN and **0.592** on ResPlan. Pick the
   dataset that matches your target market's layout conventions, or you will ship
   plausible-looking plans that no local architect recognises.
   [arXiv 2607.06483](https://arxiv.org/abs/2607.06483) (2026) is the only paper
   measuring this properly — read it before committing engineering.

---

## 1. Graph2Plan (Hu et al., SIGGRAPH 2020)

### Identity

- **Title:** *Graph2Plan: Learning Floorplan Generation from Layout Graphs*
- **Authors:** Ruizhen Hu, Zeyu Huang, Yuhan Tang, Oliver van Kaick, Hao Zhang, Hui Huang
- **Venue:** ACM Transactions on Graphics 39(4) — SIGGRAPH 2020
- **arXiv:** [2004.13204](https://arxiv.org/abs/2004.13204) (submitted 27 Apr 2020),
  DOI `10.48550/arXiv.2004.13204`
- **Paper PDF (mirror):** <https://people.scs.carleton.ca/~olivervankaick/pubs/g2p.pdf>
- **Project page:** <https://vcc.tech/research/2020/Graph2Plan>
  (page fetched — it is a JS shell; the download links did not render as text. **UNCONFIRMED** whether it hosts weights)

### What it actually does

**Inputs:**

1. A **building boundary** (raster/polygon, with the front-door position marked).
2. A **layout graph** — nodes = rooms with a type, edges = adjacency with a
   relative-position label. Crucially the graph is *not* authored from scratch:
   the user gives room counts and coarse constraints, the system **retrieves**
   matching floor plans + their layout graphs from an RPLAN-derived database,
   and the user then edits the retrieved graph in a Django web UI.

**Outputs** (from the paper, via [ar5iv](https://ar5iv.labs.arxiv.org/html/2004.13204)):

1. A **128×128 raster floorplan image** with per-pixel room labels.
2. **Initial room bounding boxes**, then **refined bounding boxes** from a
   `BoxRefineNet`.
3. A **post-process** (MATLAB) that snaps box edges to nearby boundary edges and
   to adjacent room edges within a threshold, and resolves box overlaps by
   consulting the raster image for draw order.

So: **one axis-aligned box per room**, intersected with the building boundary.
The paper justifies this by noting *"over 93% of the rooms in RPLAN can be
represented as the intersection between their respective bounding boxes and the
building boundary."* Non-rectangular rooms exist only as the boundary clips a box.

**Walls:** no explicit wall geometry. Walls are the implicit interface between
adjacent room boxes. **No wall thickness anywhere in the model.**

**Doors and windows:** *not learned*. The paper states they are added afterwards
using *"the heuristics proposed by Wu et al., i.e., add doors between connected
rooms and windows along exterior wall segments."* The limitations section
explicitly lists that *doors and windows aren't captured in the model*.

**Runtime:** *"Generating a floorplan from an input boundary takes less than 0.4
seconds"* (99 ms retrieval + 11 ms transfer + 68 ms generation + 200 ms
post-processing).

**Training data:** ~80,000 layout graphs extracted from the ~120,000 RPLAN
floorplans, split 70/15/15.

### Stated limitations (from the paper)

- Layout graphs encode only room types, rough locations and adjacencies — **not**
  accessibility, circulation or functional requirements.
- The user cannot express **forbidden** adjacencies or exclusions.
- Doors/windows are outside the model.
- Room alignment is a post-process, not learned — misalignment is a known failure.
- Fails when the retrieved graph came from a boundary very different from the input.

### Code, weights, licence

- **Repo:** <https://github.com/HanHan55/Graph2plan>
- GitHub API (`/repos/HanHan55/Graph2plan`), read 2026-08-17:
  - `"license": null`
  - `/repos/HanHan55/Graph2plan/license` → **HTTP 404 "Not Found"**
  - `pushed_at: 2023-03-24` — **no code changes in ~3.5 years**
  - 344 stars, 83 forks, not archived
  - Root tree: `DataPreparation/`, `Interface/`, `Network/`, `PostProcess/`, `README.md` — **no LICENSE file**

> ### ⚠️ Licence verdict: Graph2Plan is NOT open source
>
> There is **no licence file and no licence statement** anywhere in the repo.
> Under the Berne Convention and GitHub's own Terms of Service, code published
> without a licence is **"All rights reserved"** — the public may view and fork it
> *within GitHub*, but has **no right to use, modify, or distribute it**.
> Using Graph2Plan source in a commercial product would be copyright infringement
> absent a written grant from Shenzhen University / the authors.

- **Pretrained weights: NOT released.** The only release asset is
  `https://github.com/HanHan55/Graph2plan/releases/download/data/Data.zip`
  (tag `data`, **245,536,030 bytes**, verified by HTTP HEAD). The README calls it
  *"pre-processed data … just for convenient to reproduce the result in our paper"*.
  Training instructions tell you to run `train.py` yourself, and the
  post-processing script says *"Change the `model_path` to the path of trained
  model"* — i.e. you supply your own checkpoint.
- **Note:** that `Data.zip` is RPLAN-derived data redistributed publicly, which
  appears to conflict with RPLAN's own no-redistribution clause (§2). Treat it as
  encumbered regardless of convenience.

### Practical build friction

- Requires **MATLAB** + the MATLAB Python Engine for the box-alignment
  post-process. This is a hard commercial dependency (paid MATLAB licence) and a
  major porting cost.
- Pinned to an ancient stack (originally PyTorch 1.3, Python 3.7; README patched
  to 3.9/CUDA 11.7).
- Depends on [`zzilch/RPLAN-Toolbox`](https://github.com/zzilch/RPLAN-Toolbox)
  for data prep — GitHub API: `"license": null`, last push **2021-04-13**.
  **Also unlicensed.**

### Forks and reimplementations

Queried the GitHub API for forks and for repos matching `graph2plan`:

| Repo | Stars | Last push | Licence | Note |
|---|---|---|---|---|
| `HanHan55/Graph2plan` | 344 | 2023-03-24 | **none** | canonical |
| `tahirrrhassan/Graph2Plan` | 4 | 2024-12-03 | GPL-3.0 | ⚠️ a GPL notice slapped on unlicensed upstream code is **legally ineffective** — the uploader had no right to relicense. Do not rely on it. |
| `zzilch/Graph2plan` | 2 | 2023-03-23 | none | by the RPLAN-Toolbox author |
| `WizardZZH/Floorplan-generation` | 14 | 2023-05-19 | GPL-3.0 | *Neural-Guided Room Layout Generation with Bubble Diagram Constraints* — different method, not a G2P fork |
| ~15 other forks | 0–1 | 2020–2026 | none | dormant mirrors |

**No maintained, cleanly-licensed reimplementation of Graph2Plan exists.**
Everything downstream inherits the unlicensed status.

**Bottom line on Graph2Plan:** architecturally it is a *retrieval-then-refine box
placer*, not a wall/BIM generator. Even if the licence were clean, its output
(axis-aligned room boxes, no walls, no openings) is roughly one third of what a
BIM engine needs. Its genuinely reusable idea is the **retrieval + graph-edit
interaction loop**, which you can reimplement from the paper without touching
their code (papers describe methods; methods are not copyrightable, only the
expression is).

---

## 2. RPLAN dataset

### Identity

- **Paper:** Wenming Wu, Xiao-Ming Fu, Rui Tang, Yuhan Wang, Yu-Hao Qi, Ligang Liu,
  *Data-driven Interior Plan Generation for Residential Buildings*,
  **ACM TOG (SIGGRAPH Asia) 38(6), 2019**.
  DOI: <https://dl.acm.org/doi/10.1145/3355089.3356556>
- **Affiliations:** USTC + **Kujiale** (a Chinese commercial interior-design platform).
- **Project page:** <http://staff.ustc.edu.cn/~fuxm/projects/DeepLayout/index.html>
  (⚠️ HTTPS is refused by that host — `ECONNREFUSED :443`. Plain HTTP works.)

### Size and content

- **80,788 floor plans** of real residential buildings, mostly **Asian**
  (China/Kujiale-sourced), manually collected and densely annotated.
  (Graph2Plan cites "~120K floorplans / 80K usable layout graphs" — the two
  numbers refer to raw vs. filtered.)
- **Representation: raster.** Each plan is a multi-channel PNG-style image
  (boundary channel, room-category channel, room-instance channel, wall channel).
  There is **no native vector/polygon release**. The ResPlan comparison table
  lists RPLAN as *"Raster only / Vector: No / Graph: No / Metric scale: No"*.
- Vectors/graphs must be recovered with third-party tooling:
  - [`zzilch/RPLAN-Toolbox`](https://github.com/zzilch/RPLAN-Toolbox) — **unlicensed**, last push 2021-04-13, 93 stars.
  - [`rplanpy` on PyPI](https://pypi.org/project/rplanpy/) v0.1.1 — PyPI metadata
    shows **`"license": ""` (empty)**; repo `unaisaralegui/rplanpy`. Effectively unlicensed.
- Per Graph2Plan's data spec, extracted items carry `boundary`, `rType`,
  `rBoundary` (room polygon points), `gtBox`, `rEdge` — i.e. the vectors are a
  *derived* product, not shipped.

### ⚠️ Licence / access — the decisive fact

Access is **not** a download link. It is gated behind a Google Form linked from
the project page:

<https://docs.google.com/forms/d/e/1FAIpQLSfwteilXzURRKDI5QopWCyOGkeb_CFFbRwtQ0SOPhEg0KGSfw/viewform>

The form (fetched directly, 2026-08-17) is titled **"RPLAN Dataset"**, collects
requester name, position (undergrad / postgrad / postdoc / professor / other),
**principal investigator's name**, and affiliation — i.e. it presumes an academic
requester — and requires agreement to terms including:

> **"The data will be used only for non-commercial research and academic purposes."**

> **"I will not redistribute the dataset in any way and in any format. Any new
> access will be established through this form and/or authors' official method of
> releasing the dataset."**

The full Terms document ([Google Drive](https://drive.google.com/file/d/1wEbccL5NAL_mzFt2hyxPqZppXDalbApW/view))
linked from the form reads, verbatim:

> **"1. Researcher shall use the Database only for non-commercial research and
> educational purposes.**
> **2. Researcher shall not redistribute the downloaded data**, in whole or in
> part, through other media…
> **7. If Researcher is employed by a for-profit, commercial entity, Researcher's
> employer shall also be bound by these terms and conditions**…
> 8. This Agreement shall be governed by the laws of P.R. China…"

> 🚨 **Clause 7 explicitly reaches your company.** It is not enough that an
> individual engineer downloaded it "for research" — the agreement binds the
> employer. This is the single most consequential sentence in this document.

There is **no SPDX licence, no CC licence, and no commercial tier**.

### ⚠️ Licence-laundering traps — do not fall for these

1. **[Zenodo record 18874946](https://zenodo.org/records/18874946)** is an
   **anonymous re-upload of RPLAN** (creator field: *"None"*) stamped **CC BY 4.0**.
   The uploader had no right to grant that licence. There is also a
   [Kaggle mirror](https://www.kaggle.com/datasets/lkerkarabulut/rplan-dataset2025).
   **A mirror is not a licence.** Downloading from these cures neither clause 1
   nor clause 7, and a CC BY badge applied by a stranger has no legal effect.
2. Several repos — **MaskPLAN**, **FloorplanGAN**, **Graph2Plan** — **ship
   preprocessed RPLAN arrays** in-repo or via Drive/Baidu. That appears to breach
   RPLAN clause 2, which likely means their own MIT grants cannot validly cover
   *those files* (though they do cover the authors' own code).

**Verdict: RPLAN cannot be used in a commercial product.** This is not a grey
area — the agreement text is explicit on both non-commercial use and
non-redistribution. Critically this also **taints every model trained on it**:
weights are a derivative use of the data, made for a commercial purpose, which
the agreement does not permit. Every RPLAN-trained checkpoint you find online
(HouseGAN, HouseDiffusion, Graph2Plan, WallPlan, …) carries this problem
regardless of the *code's* licence.

---

## 3. ResPlan

**Confirmed — it exists, and it is the single best-licensed option found.**

### Identity

- **Title:** *ResPlan: A Large-Scale Vector-Graph Dataset of 17,000 Residential Floor Plans*
- **Authors:** **Mohamed Abouagour, Eleftherios Garyfallidis** (2 authors)
- **arXiv:** [2508.14006](https://arxiv.org/abs/2508.14006) — **v1 submitted 19 Aug 2025**,
  **v2 last revised 4 Aug 2026**. Subjects cs.CV, cs.RO. DOI `10.48550/arXiv.2508.14006`
- **Repo:** <https://github.com/m-agour/ResPlan> — created 2025-08-26,
  last push **2026-07-28**, 13 stars, 2 forks (GitHub API, 2026-08-17)
- **Kaggle mirror:** <https://www.kaggle.com/datasets/resplan/resplan> (ships the same
  geometry with `plan["graph"]` pre-populated)
- **Peer-review status:** the repo README states *"Citation details are withheld
  while the accompanying paper is under peer review."* → **still a preprint as of
  Aug 2026.** Treat benchmark claims as un-refereed.

### Size and content (verified against the released files)

| Property | Value |
|---|---|
| Total plans | **17,000** |
| Splits | 13,053 train / 1,632 val / 1,632 test (+683 augmented, kept separate) |
| Avg functional rooms/plan | 8.1 |
| Avg graph nodes / edges | 9.2 / 12.9 |
| Median floor area | 110 m² |
| Room polygons | 137,131 (**only 43.2% rectangular**) |
| Edge types | `via_door` 54.2%, `adjacency` 35.2%, `direct` 7.6%, `via_window` 3.0% |
| Median wall thickness | 21 cm |

### Representation — verified by downloading and inspecting the data

`ResPlan.zip` (100,106,537 bytes) contains a single `ResPlan.pkl`
(258,453,658 bytes). Scanning the pickle opcode stream directly (`pickletools`,
no execution) shows it is a list of dicts of **`shapely.io.from_wkb`** geometries
— i.e. genuine vector polygons, not rasters — with these per-plan keys:

```
id, land, inner, wall, wall_depth, front_door, door, window,
living, kitchen, bedroom, bathroom, balcony, garden, parking, pool,
storage, stair, neighbor, area, net_area, area_change_sqft
```

This is materially richer than Graph2Plan's output space:

- **`wall` + `wall_depth`** → real walls with a thickness. Graph2Plan has neither.
- **`door`, `window`, `front_door`** → openings are *data*, not a post-hoc heuristic.
- **`neighbor`** → the connectivity graph.
- Room polygons per semantic class (`living`, `kitchen`, …) as Shapely polygons /
  multipolygons, in **metres** (metric scale) as well as pixels.
- Paper reports doors align to wall bands in **99.94%** of cases, windows **99.98%**.

Loading requires `shapely` (`pip install shapely`) — the pickle references
`shapely.io.from_wkb` and `numpy`.

### ⚠️ Licence — verified from the raw `LICENSE` file

Read from `https://raw.githubusercontent.com/m-agour/ResPlan/main/LICENSE`:

**Dual licence.**

- **DATA** (`ResPlan.pkl`, `split.json`, `croissant.json`):
  **Creative Commons Attribution 4.0 International (CC BY 4.0)** →
  **commercial use permitted with attribution.**
- **CODE** (`resplan_utils.py`, `ResPlan_demo.ipynb`, `baselines/`):
  **MIT License**, "Copyright (c) 2025 The ResPlan Authors".

Note GitHub's auto-detector reports `spdx_id: "NOASSERTION"` for the repo simply
because the file is a dual-licence composite; the file text itself is unambiguous.

The licence file is unusually candid about the *scope* of the grant:

> *"This licence is granted over the contributions the authors hold rights in:
> the annotations, the semantic taxonomy, the room-connectivity graph
> construction, the metric-scale conversion, the curation and filtering
> decisions, and the canonical splits."*
>
> *"The underlying spatial arrangement of a building is a matter of fact rather
> than creative expression, and facts are not subject to copyright. No licence is
> therefore asserted, required, or granted over the spatial arrangements
> themselves."*

There is also a `TAKEDOWN.md` policy: rights-holder requests acknowledged in
7 days, plan removed in the next release within 30 days, removed IDs tracked in
`REMOVED.md`.

### 🔶 Residual legal risk (be honest about this)

The provenance section states plans were **derived by computer vision from
publicly accessible real-estate listing renderings**, and that *"Source platform
identities are withheld to comply with those terms [of service]."* Implications:

1. The CC BY 4.0 grant covers *the authors' own contribution*, and the authors
   explicitly disclaim granting rights over the underlying arrangements. That is
   a defensible legal position (facts aren't copyrightable) but it is an
   *assertion*, not an adjudicated ruling.
2. **EU/UK `sui generis` database right** is a separate right from copyright and
   is not addressed by the licence text. **UNCONFIRMED** whether it bites here.
3. Scraping-ToS exposure sits with the dataset authors, not you — but the
   withheld platform identities mean you cannot independently diligence it.

For a commercial product this is **far better than RPLAN** (which is a flat "no")
but is not the same as a dataset with fully cleared provenance. If you need
bulletproof provenance, **Swiss Dwellings** (§3.2) has a named corporate
rights-holder.

### Known limitations (stated by the authors — read these before committing)

- **Regional scope:** *"All plans come from South Asian residential markets"* —
  layout conventions are **not** representative of Europe/North America. The
  authors' own cross-dataset transfer numbers quantify the gap brutally:

  | Train → test | Accuracy |
  |---|---|
  | ResPlan → ResPlan | 0.918 |
  | RPLAN → RPLAN | 0.909 |
  | RPLAN → ResPlan | **0.592** |
  | ResPlan → RPLAN | **0.664** |

  i.e. a model trained on one dataset loses ~30 points on the other. **Regional
  layout convention is a first-order product problem, not a detail.**
- Single floor, no furniture, no 3D.
- **Wall thickness is normalised per plan** — within-plan variation between
  structural walls and thin partitions is lost. 99.3% of plans fall in 10–40 cm.
- Vectorisation artefacts: 0.52% of room polygons exceed 30 vertices, 0.02%
  exceed 100 (jagged traced contours).
- **Near-duplicates:** 1,170 redundant plans (6.9%) in 931 clusters; 154 of 1,632
  test plans have a near-duplicate in train. (Author-reported effect on Task 1:
  0.15 accuracy points.)
- Semantic labels validated by a **500-plan manual audit**, not exhaustively.
- ⚠️ **Two graph definitions.** `plan_to_graph()` gives a *strict* graph
  (~8.7 edges/plan, 5 types); the paper/Kaggle/benchmarks use a *broader*
  adjacency obtained by additionally calling `add_adjacency_edges()`
  (12.9 edges/plan, 4 types). Mixing them silently invalidates comparisons.

### ResPlan vs RPLAN — head to head

| | RPLAN | ResPlan |
|---|---|---|
| Plans | 80,788 | 17,000 |
| Year | 2019 | 2025/2026 |
| Geometry | **Raster only** | **Vector (Shapely polygons)** |
| Graph | No (must be derived) | **Yes, 4 typed edge classes** |
| Metric scale | No | **Yes (metres)** |
| Walls | raster wall channel | **polygons + `wall_depth`** |
| Doors/windows | limited | **explicit polygons, incl. `front_door`** |
| Rooms/plan | ~6.7 (max 8) | 8.1 |
| Region | Asia (China) | South Asia |
| **Licence** | **Non-commercial research only, no redistribution** | **CC BY 4.0 (data) + MIT (code)** |
| Peer-reviewed | Yes (SIGGRAPH Asia 2019) | **No — preprint under review** |

**ResPlan trades ~4.7× fewer plans for a usable licence, real vectors, real
walls with thickness, real openings, metric scale, and a typed graph.** For a
commercial product that trade is not close.

### 3.2 Also worth knowing: Swiss Dwellings and MSD (both CC BY family)

These were not in the brief but are the strongest commercially-usable
alternatives found, and cover the **European** layout conventions that ResPlan
does not.

**Swiss Dwellings v3.0.0** — Archilyse AG
- Zenodo: <https://zenodo.org/records/7788422>, DOI `10.5281/zenodo.7788422`
- Authors: Matthias Standfest, Michael Franzen, Yvonne Schröder, Luis Gonzalez
  Medina, Yarilo Villanueva Hernandez, Jan Hendrik Buck, Yen-Ling Tan, Milena
  Niedzwiecka, Rachele Colmegna (all **Archilyse AG** — a named corporate
  rights-holder, i.e. clean provenance)
- v3.0.0 published 2022-09-20, updated 2023-03-31
- **Licence: Creative Commons Attribution 4.0 International (CC BY 4.0)** —
  commercial use permitted with attribution
- Scale: **45,176 apartments**, ~3,100 buildings, ~370,000 rooms,
  **~1.7M separators (walls, railings)**, **~715,000 openings (windows, doors)**,
  ~520,000 areas, ~315,000 features (sinks, toilets, bathtubs)
- Format: one 931.9 MB zip of CSVs (`geometries.csv` with 2D geometry,
  `simulations.csv` with daylight/noise/view/centrality sims, `locations.csv`,
  `location_ratings.csv`)
- **Schema — the most BIM-shaped data in this whole document**
  ([Archilyse research page](https://archilyse.standfest.science/swiss-dwellings)):
  - `geometries.csv` join keys: `site_id, building_id, floor_id, plan_id,
    apartment_id, unit_id, area_id` — a real building hierarchy, not flat plans.
  - Columns include `geometry, elevation, height` plus `entity_type` /
    `entity_subtype`.
  - **Geometry is WKT, in metres.** Local per-site coordinates,
    *"+y points northwards; +x points eastwards"*.
  - Entity taxonomy: **areas** (rooms, bathrooms, kitchens, balconies),
    **separators** (walls, railings, columns), **openings** (windows, doors),
    **fixed installations** (sinks, bathtubs, toilets).
  - ⭐ **`elevation` + `height` give you 2.5D**, though heights *"may be defaulted
    rather than precisely measured"*. No other dataset here has any Z at all.
- Bonus: the simulation columns (natural light, noise, viewshed, centrality) are
  exactly the "dashboard metrics" a generative design tool needs, pre-computed.
- ⚠️ **The data is CC BY 4.0 but Archilyse's *pipeline code* is AGPL** — a separate
  artifact. Take the data; do not vendor the pipeline into a closed product.

**MSD — Modified Swiss Dwellings** (van Engelenburg et al.)
- ECCV 2024 paper: [arXiv 2407.10121](https://arxiv.org/abs/2407.10121);
  ACM DOI <https://dl.acm.org/doi/10.1007/978-3-031-73636-0_4>
- Project page: <https://caspervanengelenburg.github.io/msd-eccv24-page/>
- Code: <https://github.com/caspervanengelenburg/msd> — GitHub API: **`license: null`**,
  129 stars, last push 2025-08-27. ⚠️ **The MSD *code* is unlicensed** (data is not).
- **5,372 floor plans / 18,943 distinct apartments** — the first large-scale
  dataset of **multi-apartment building complexes** (15–50 areas per plan, peak ~25),
  vs. the single-unit bias of RPLAN/ResPlan.
- Representation: the **graph is the primary container**
  (`networkx.Graph()` / `torch_geometric.data.Data()`), with room shapes and types
  as node attributes, connectivity types as edge attributes, and the full image as
  a graph attribute. Includes doors, windows, zone types, compass orientation.
- Distribution: [Kaggle](https://www.kaggle.com/datasets/caspervanengelenburg/modified-swiss-dwellings)
  and [4TU.ResearchData](https://data.4tu.nl/datasets/e1d89cb5-6872-48fc-be63-aadd687ee6f9)
  (DOI `10.4121/e1d89cb5-6872-48fc-be63-aadd687ee6f9.v2`, 5.54 GB uncompressed;
  train 4,167 plans in `graph_in`/`struct_in`/`full_out`/`graph_out` folders).
- ✅ **LICENCE CONFLICT RESOLVED** (via the Kaggle API,
  `api/v1/datasets/list?search=modified-swiss-dwellings`, 2026-08-17). They are
  **two different artifacts**, not a contradiction:

  | Release | What it is | Size | Licence |
  |---|---|---|---|
  | [4TU record `e1d89cb5…`](https://data.4tu.nl/datasets/e1d89cb5-6872-48fc-be63-aadd687ee6f9) v2, 2023-07-11 | the earlier **floor-plan auto-completion challenge** set, 4,167 train plans | 5.54 GB uncompressed | **CC BY 4.0** |
  | [Kaggle `caspervanengelenburg/modified-swiss-dwellings`](https://www.kaggle.com/datasets/caspervanengelenburg/modified-swiss-dwellings) v6 | the **ECCV 2024 MSD**, 5,372 plans / 18,943 apartments | 4,996,692,802 bytes, 2,471 downloads | **CC BY-SA 4.0** (owner = van Engelenburg himself, so authoritative) |

- ⚠️ **CC BY-SA is copyleft on the data.** Commercial use is permitted, but
  *adaptations* must be licensed ShareAlike. **Whether trained model weights count
  as an "adaptation" of the training data is legally unsettled** — this is the same
  open question as RPLAN-and-weights, and it needs counsel. If you want to avoid it
  entirely, use the **4TU CC BY 4.0** release, or derive your own MSD-equivalent
  directly from **Swiss Dwellings** (unambiguously CC BY 4.0).
- MSD's own generation code (Graph-informed U-Net, Modified HouseDiffusion) is
  marked *"will be released soon"* in the README and lives on unmerged branches
  (`yt`, `wip-house-diffusion-msd`). **UNCONFIRMED** whether it has landed.

**Neufert 4.0** (Bauhaus-Universität Weimar) — Zenodo <https://zenodo.org/records/14223942>
- Martin Bielik, Sven Schneider, Zhang Luyang, Milan Valasek; published 2024-11-26
- **Licence: CC BY 4.0**
- 20,419 residential apartments derived from Swiss dwelling plans; apartment
  outlines in **WKT** + per-apartment features (room counts, areas, sunlight klx,
  traffic noise dB(A)); 444.6 MB, 2 CSVs. All outlines human-audited.
- Filtered: no underground, ≤6th floor, 25–200 m², ≤5 rooms.
- Useful as a clean *outline + performance-metric* corpus; it is **not** a
  full wall/door/window vector set.

**ProcTHOR / ProcTHOR-10k** (Allen Institute for AI) — ✅ **Apache 2.0** (verified:
raw `LICENSE` at `allenai/procthor` and `allenai/procthor-10k`, both branches)
- 10,000 **procedurally generated** interactive house layouts. Not real-world
  architecture, and built for embodied-AI agents rather than construction — but
  it is **fully permissive, fully synthetic, and therefore has no provenance risk
  whatsoever.** Its generator is also open, so you can produce unlimited plans.
- Directly relevant twice over: DStruct2Design's benchmark is built from
  **RPLAN + ProcTHOR-10k**, so the **ProcTHOR half of that benchmark is clean**;
  and [arXiv 2607.06483](https://arxiv.org/abs/2607.06483) (2026) shows synthetic
  pre-training + small-real-data adaptation works — the standard escape hatch
  from a data-licensing problem.

**CubiCasa5K** — <https://github.com/CubiCasa/CubiCasa5k>
- ❌ Raw `LICENSE` file reads verbatim: *"CubiCasa5K is licensed under a Creative
  Commons Attribution-**NonCommercial** 4.0 International License."*
  **Not usable commercially.** (Widely mis-cited as CC BY-NC-SA; it is CC BY-NC.)
- 5,000 plans, SVG vector annotations. It is a floor-plan *parsing* dataset anyway.

**LIFULL HOME'S** — ~5M raster plans via Japan's NII IDR
([agreement page](https://www.nii.ac.jp/dsc/idr/en/lifull/)). ❌ **A commercial
entity cannot obtain it at all, under any terms.** Verbatim:

> *"**Only researchers belonging to a university or a public research institution
> can apply** to use the Data."*
> *"**Applications from those belonging to a private company, etc. will not be
> accepted.**"*
> *"THE DATA IS PROVIDED FOR **'NOT-FOR-PROFIT RESEARCH PURPOSES ONLY'**"*

This is why House-GAN (trained on LIFULL, 117,587 plans) is unreachable even
setting its code licence aside.

**Structured3D** — <https://structured3d-dataset.org/> — ❌ **Non-commercial
research/education only**, and the terms bind a for-profit employer, same pattern
as RPLAN. The *code* is MIT; the **data is not**. (**UNCONFIRMED in detail:** the
full ToU lives in a Google Drive document behind an agreement form and was not
read directly; the non-commercial restriction was confirmed from the dataset site.)
Relevant because Raster2Seq is trained on it.

**MagicPlan** (via PuzzleFusion) — ❌ non-commercial; see the Furukawa-lab note in §4.2.

---

## 4. Other current model options

### 🚨 First: the finding that outranks licensing

Across **~20 generators spanning 2020–2026**:

| Capability a BIM engine needs | How many published systems have it |
|---|---|
| **Walls as real geometry with thickness** | **0** |
| Windows emitted | **1** (GFLAN — which has no code) |
| Doors emitted as real entities | ~6 (House-GAN++, HouseDiffusion, FMLM, floor-plan-rlvr, HouseTune, TLC-Plan) |
| True vector **wall graph** output | **1** (GSDiff — GPL-3.0) |
| Everything else | axis-aligned boxes or raster masks |

Every model treats walls as zero-width centrelines or implicit polygon edges.
**Wall thickness, window generation and door hardware are yours to build
regardless of what you license.** That reframes the whole decision: you are not
shopping for a finished floorplan engine, you are shopping for a *room-topology
proposer* to sit in front of your own parametric constraints layer. Licensing
therefore only has to be clean for a comparatively small part of the system.

### 🚨 Second: automated licence scanning gives false clears here

**Do not trust the GitHub licence badge or an SBOM tool here.**

- [`aminshabani/house_diffusion`](https://github.com/aminshabani/house_diffusion)
  renders as **"GPL-3.0 license"** in GitHub's sidebar, because the detector reads
  the `LICENSE_GPL` file and ignores the 311-byte `LICENSE` that actually says
  *"not allowed for commercial usage."* The API's `NOASSERTION` is the honest signal.
- House-GAN and House-GAN++ have the same trap: 35 KB files that text-matchers
  report as GPL, or even Apache, while a four-line banner at the top restricts
  them to research.
- The House-GAN research-only banner was **added retroactively** in commit
  `1ad2b75` (2021-05-31). The repo was plain GPLv3 before that — so an old
  vendored copy or a cached scan result will disagree with reality.

**Three of the most-starred repos in this field would pass an automated licence
check and are actually research-only.** Every ✅/❌ in this document was taken from
the raw file, not the badge.

### The pattern that decides everything

Almost every published floor-plan generator is trained on **RPLAN**. The code
licence and the *data* licence are two separate gates, and **the data gate is the
one that usually closes**:

| Repo licence | Trained on RPLAN? | Can you ship it? |
|---|---|---|
| MIT / Apache | yes | **Code yes, released weights no.** Retrain on ResPlan/Swiss Dwellings. |
| GPL-3.0 | yes | Code is copyleft (poisons a closed product); weights still RPLAN-tainted. |
| "research only" | yes | **No.** |
| none | — | **No** (all rights reserved). |

So the realistic commercial path is: **take an MIT/Apache *architecture*, throw
away the released checkpoint, and retrain on CC BY data.**

### 4.1 Licence table — verified from raw `LICENSE` files

All read from `raw.githubusercontent.com` on 2026-08-17 unless noted.

| Model | Repo | Code licence (verbatim / SPDX) | Weights released? | Commercial? |
|---|---|---|---|---|
| **HouseGAN** (ECCV 2020) | [ennauata/housegan](https://github.com/ennauata/housegan) | Header: `********* THIS CODE CAN ONLY BE USED FOR RESEARCH PURPOSES *********` prepended to GPL-3.0 text | yes | ❌ **No** |
| **House-GAN++** (CVPR 2021) | [ennauata/houseganpp](https://github.com/ennauata/houseganpp) | Same research-only header + GPL-3.0 | yes | ❌ **No** |
| **HouseDiffusion** (CVPR 2023) | [aminshabani/house_diffusion](https://github.com/aminshabani/house_diffusion) | `LICENSE` reads verbatim: *"The code and the model weights in this repository are not allowed for commercial usage. For research purposes, the terms follow the GPL v3, as in the separate file LICENSE_GPL."* | yes | ❌ **No — explicit** |
| **MaskPLAN** (CVPR 2024) | [HangZhangZ/MaskPLAN](https://github.com/HangZhangZ/MaskPLAN) | **MIT** | yes (Google Drive, 4 variants) | ⚠️ **Code yes; weights RPLAN-derived** |
| **Tell2Design** (ACL 2023) | [LengSicong/Tell2Design](https://github.com/LengSicong/Tell2Design) | README: code Apache 2.0, **dataset CC BY-NC 4.0**. ⚠️ the linked `LICENSE` file **404s on both `main` and `master`** | no weights | ❌ **Dataset non-commercial** |
| **FloorplanGAN** | [luozn15/FloorplanGAN](https://github.com/luozn15/FloorplanGAN) | **MIT** (GitHub API) | **UNCONFIRMED** | ⚠️ Code yes; check data |
| **WallPlan** (SIGGRAPH 2022) | [cgjiahui/WallPlan](https://github.com/cgjiahui/WallPlan) | **`license: null`** (GitHub API); no LICENSE file; README is a PDF | **UNCONFIRMED** | ❌ **No (unlicensed)** |
| **GSDiff** (AAAI 2025) | [SizheHu/GSDiff](https://github.com/SizheHu/GSDiff) | **GPL-3.0** | yes (Google Drive, several variants) | ⚠️ **Copyleft** + RPLAN/LIFULL data |
| **Raster2Seq** (SIGGRAPH 2026) | [Cornell-VAILab/Raster2Seq](https://github.com/Cornell-VAILab/Raster2Seq) | **MIT** | yes (HuggingFace `haopt/Raster2Seq`) | ⚠️ Trained on **CubiCasa5K (NC)** + Structured3D |
| **LayoutBridge** (2026) | [lalalalaxxx/LayoutBridge](https://github.com/lalalalaxxx/LayoutBridge) | **MIT** | no (arch + training code only) | ⚠️ Code yes |
| **Residential Floorplan Diffusion** (Autom. in Constr. 2024/25) | [zengpengyu-student/…](https://github.com/zengpengyu-student/Residential_Floorplan_Diffusion) | **MIT** | yes (Google Drive, 2-stage) | ⚠️ Code yes; dataset undocumented |
| **MSD toolkit** (ECCV 2024) | [caspervanengelenburg/msd](https://github.com/caspervanengelenburg/msd) | **`license: null`** (GitHub API) | generation models "released soon" | ❌ code unlicensed (data is CC, see §3.2) |
| **Graph2Plan** | [HanHan55/Graph2plan](https://github.com/HanHan55/Graph2plan) | **none** | none | ❌ **No** |
| **RPLAN-Toolbox** | [zzilch/RPLAN-Toolbox](https://github.com/zzilch/RPLAN-Toolbox) | **none** | n/a | ❌ **No** |
| **rplanpy** | [PyPI](https://pypi.org/project/rplanpy/) | PyPI metadata `"license": ""` (empty) | n/a | ❌ effectively unlicensed |

### 4.2 Per-model detail

**House-GAN** (Nauata, Chang, Cheng, Mori, Furukawa — ECCV 2020)
- [arXiv 2003.06988](https://arxiv.org/abs/2003.06988) · DOI [10.1007/978-3-030-58452-8_10](https://doi.org/10.1007/978-3-030-58452-8_10)
- **In:** bubble diagram only. No boundary, no partial layout.
- **Out:** ❌ **axis-aligned bounding boxes** — 32×32 masks, thresholded, then
  *"we fit the tightest axis-aligned rectangle for each room."* No doors
  (*"An edge property (i.e. room adjacency) does not reflect the presence of
  doors"*), no windows, no walls.
- **Data: LIFULL HOME'S**, 117,587 plans → **unobtainable by a company at all** (§3.2).
- [ennauata/housegan](https://github.com/ennauata/housegan), 293★, last commit 2024-03-28.

**House-GAN++** (Nauata, Hosseini, Chang, Chu, Cheng, Furukawa — CVPR 2021)
- [arXiv 2103.02574](https://arxiv.org/abs/2103.02574) · DOI [10.1109/CVPR46437.2021.01342](https://doi.org/10.1109/CVPR46437.2021.01342).
  SFU + **Autodesk Research** (Chang, Chu, Cheng) — Autodesk funding is the likely
  reason the research-only banner exists.
- **In:** bubble diagram **+ partial/previous layout** (iterative refinement). Still
  no boundary constraint.
- **Out:** 64×64 raster masks → an **off-the-shelf vectoriser** →
  *"a room is represented by an axis-aligned closed-polygon, adjacent rooms share
  the walls with the common line segments, and a door is represented as a
  line-segment on a wall."*
  ✅ **doors are first-class nodes** (12-d one-hot = 10 room types + 2 door types).
  ❌ no windows. ❌ walls are zero-thickness shared polygon edges.
- **Data:** RPLAN (60k).
- [ennauata/houseganpp](https://github.com/ennauata/houseganpp), 254★, dormant since
  2021-11-18. **Weights are committed in-repo** (`checkpoints/pretrained.pth`) — so
  they are covered by the repo LICENCE with zero ambiguity. Its required data-prep
  dependency [sepidsh/Housegan-data-reader](https://github.com/sepidsh/Housegan-data-reader)
  carries the **same banner** — the pipeline is research-only at every layer.

The research-only header stapled onto GPL-3.0 is legally incoherent (GPL §7
forbids adding use restrictions), but the authors' intent is unambiguous.
Do not build on either.

**HouseDiffusion** (Shabani, Hosseini, Furukawa — CVPR 2023)
- [arXiv 2211.13287](https://arxiv.org/abs/2211.13287) · DOI [10.1109/CVPR52729.2023.00529](https://doi.org/10.1109/CVPR52729.2023.00529) ·
  [github.com/aminshabani/house_diffusion](https://github.com/aminshabani/house_diffusion)
  (235★; last commit 2026-03-21 but **README only — code untouched since Feb 2023**)
- **In:** bubble diagram + **explicit per-room corner-count control** (genuinely
  useful for a design tool).
- **Out:** ✅ **native vector polygon loops** — no raster stage, no post-hoc
  vectoriser. *"A floorplan is represented as a set of 1D polygonal loops one for
  each room/door."* Non-Manhattan capable. ✅ **doors are separate polygonal
  loops.** ❌ windows never mentioned. ❌ walls still implied — **but** the discrete
  denoising branch makes shared corners *exactly* coincident, which is the single
  most BIM-relevant property in the whole field (it is what makes downstream wall
  solidification tractable).
- **This is the strongest architecture on the list. Its `LICENSE` explicitly bans
  commercial use of both code and weights.** Verbatim, the whole 311-byte file:
  *"The code and the model weights in this repository are not allowed for
  commercial usage. For research purposes, the terms follow the GPL v3, as in the
  separate file 'LICENSE_GPL'."*
- Weights are on Google Drive and described by the authors as *"temporary"*.
- It vendors OpenAI's [guided-diffusion](https://github.com/openai/guided-diffusion),
  which is genuinely **MIT** — not itself a blocker.
- Emanuel Kuhn's [arXiv 2312.03938](https://arxiv.org/abs/2312.03938) adapts it
  to MSD with wall-line conditioning (input: structural wall masks) — but it
  inherits HouseDiffusion's licence.

> ### ⚠️ The Furukawa-lab escape hatch is closed
> HouseDiffusion's README recommends the **MagicPlan** dataset from
> [PuzzleFusion](https://github.com/sepidsh/PuzzleFussion) as an RPLAN
> alternative. PuzzleFusion's LICENSE carries the **identical non-commercial
> clause**, and its README states verbatim that the MagicPlan **"dataset follows
> same license as code."** The entire lineage — House-GAN, House-GAN++,
> HouseDiffusion, PuzzleFusion, the data-reader, and MagicPlan — is uniformly
> non-commercial. There is no clean entry point into it.

**MaskPLAN** (Hang Zhang, Anton Savov, Benjamin Dillenburger — **CVPR 2024**, ETH Zurich DBT)
- *"MaskPLAN: Masked Generative Layout Planning from Partial Input"*.
  ⚠️ You guessed KDD 2024 — the repo states **CVPR 2024**.
- [github.com/HangZhangZ/MaskPLAN](https://github.com/HangZhangZ/MaskPLAN), **MIT**, 15 stars, last push 2026-01-05.
- ⚠️ **No arXiv version exists** — arXiv full-text search for "MaskPLAN" returns 0
  results. Cite the CVF/IEEE version:
  [CVF PDF](https://openaccess.thecvf.com/content/CVPR2024/papers/Zhang_MaskPLAN_Masked_Generative_Layout_Planning_from_Partial_Input_CVPR_2024_paper.pdf),
  DOI `10.1109/CVPR52733.2024.00856`.
- **In:** **any subset** of {boundary raster, room types, centres, areas,
  adjacency, regions} — a masked generative autocomplete. This is the strongest
  *interactive design* story in the field: the user supplies whatever they have
  and the model fills the rest.
- **Out:** ❌ **axis-aligned bounding boxes**, not polygons. Supplementary,
  verbatim: *"each room region in pixel space is converted into a bounding box,
  represented by corners p ∈ {Xmin, Ymin, Xmax, Ymax}"*. Raster VQ-VAE region
  masks internally. **No doors, no windows, no walls.** Limitations state
  *"a limit to 8 rooms and orthogonal wall arrangements"*.
- **Data:** RPLAN (13 types consolidated to 8), preprocessed with **RPLAN-Toolbox
  and Graph2Plan's DataPreparation** — so the pipeline inherits two unlicensed
  dependencies and the released checkpoints are RPLAN-derived. The repo also
  **ships RPLAN-derived `.npy`/`.npz` arrays** (`RPLAN_B.npy`, `RPLAN_bound.npy`, …),
  which appears to breach RPLAN clause 2 and may mean the MIT grant is
  ineffective *as to those files* (though not as to the authors' own code).
  **The MIT code is the asset here; the weights and the bundled data are not.**

**Tell2Design** (**Sicong Leng** — not "Leo" — Zhou, Dupty, Lee, Joyce, Lu; NUS/SUTD)
- **ACL 2023**, pp. 14680–14697, **Area Chair Award + Best Paper nomination**.
  [ACL Anthology 2023.acl-long.820](https://aclanthology.org/2023.acl-long.820/) ·
  DOI `10.18653/v1/2023.acl-long.820` · [arXiv 2311.15941](https://arxiv.org/abs/2311.15941)
- **In:** natural language (~256 words) + boundary as an enclosing box + exterior boxes.
- **Out:** ❌ **axis-aligned bounding boxes emitted as text tokens** —
  `[ Balcony | x coordinate = 87 | y coordinate = 66 | height = 18 | width = 23 ]`,
  discretised to [0,255]. No doors, no windows, **no walls at all** — free-floating
  rectangles that can even **overlap**.
- **Data: T2D, built on RPLAN** — 5,051 human (MTurk) + 75,737 synthetic descriptions.
- [LengSicong/Tell2Design](https://github.com/LengSicong/Tell2Design), 86★,
  last commit 2025-03-14. No weights (it fine-tunes HF `t5-base`).
- ⚠️ **There is no LICENSE file at all** — 12 filename/branch variants probed, all
  404; API `license: null`; the README's `[Apache 2.0 license](LICENSE)` link is
  **broken**. The only grant that exists is a README sentence. The README says the
  dataset is **CC BY-NC 4.0**, and the paper's Ethics Statement says *"Our dataset
  should be only used for research purposes."* **Blocked twice over.**

**FloorplanGAN** (**Ziniu Luo & Weixin Huang**, Tsinghua School of Architecture)
- *Automation in Construction* **142**, art. 104470, Oct 2022 ·
  DOI [10.1016/j.autcon.2022.104470](https://doi.org/10.1016/j.autcon.2022.104470).
  ⚠️ **No arXiv preprint; paywalled** (ScienceDirect 403, no OA copy, empty
  abstracts in Crossref/OpenAlex/S2).
- **In:** room types + **areas** only. **No boundary constraint** (read from
  `models.py` / `config.yaml`, since the paper is inaccessible).
- **Out:** vector **axis-aligned rectangles**, `(xc, w, yc, h)` per room.
  Rasterisation is only a differentiable-rendering step feeding the discriminator.
  ❌ no doors, windows or walls.
- **Data:** RPLAN vectorised via Pyportace → 17,154 train / 2,000 test;
  redistributes preprocessed RPLAN via Baidu + Drive.
- [luozn15/FloorplanGAN](https://github.com/luozn15/FloorplanGAN), **MIT**
  (© 2021 luozn19), 73★, abandoned since 2023-08-11.
  **Weights: NO** — README says *"Coming soon…"*.

**WallPlan** (Jiahui Sun, Wenming Wu, Ligang Liu, Wenjie Min, Gaofeng Zhang, Liping Zheng)
- **ACM TOG 41(4), Article 92 (SIGGRAPH 2022)** ·
  DOI [10.1145/3528223.3530135](https://doi.org/10.1145/3528223.3530135) · no arXiv.
- **In:** building boundary polygon incl. front door, + optional bubble diagram
  and/or **load-bearing walls/columns**. All encoded as image channels.
- **Out:** ✅ **vector wall graph** — *"a node set V indicating wall junctions and
  an edge set E indicating wall segments"*, each node carrying a room-label list;
  rooms recovered as shortest cycles; edges constrained horizontal/vertical.
  This is semantically the closest thing in the literature to real BIM walls.
- ❌ **Centrelines only.** The only "thickness" anywhere is a training-time
  rasterisation constant: *"fixed wall thickness (3 pixels in our experiments)
  during training."* No per-wall thickness attribute in the output.
- ⚠️ **Windows are learned but weak** — WinNet emits raster square masks in only
  2 sizes (13×5 living room, 7×5 other), and the ground truth is **synthetic**:
  *"The original RPLAN dataset does not include windows… although windows are
  synthetic."* ❌ **Doors are not learned** — *"We use the rule-based algorithm in
  previous works: RPLAN and Graph2Plan"*, and figure captions say door/window
  drawing is *"only used for visualization."*
- [cgjiahui/WallPlan](https://github.com/cgjiahui/WallPlan): 23★, 7 commits, last
  push **2022-09-29**, README is a **PDF**. ⛔ **No LICENSE file** (404 across
  `main`/`master` × `LICENSE`/`.md`/`.txt`; API `license: null`) = all rights reserved.
  The README.pdf itself says: *"Due to copyright issues, we are unable to publish
  our dataset and trained models… If you want to use the whole dataset, a request
  should be made to www.Kujiale.com"*.

### 4.2b Name checks — three of the names in the brief do not exist

| Name | Verdict |
|---|---|
| **Chat2Plan** | ❌ **Does not exist** as a floorplan paper. arXiv title *and* full-text search: **0 results**. GitHub has only tiny student repos (`jhx19/Chat2Plan`, 0★, no licence; `bramyeon/Chat2Plan`, a KAIST course project). Nearest real things: **Chat2Layout** ([arXiv 2407.21333](https://arxiv.org/abs/2407.21333)) — *3D furniture* layout, not floorplans — and **ChatHouseDiffusion** ([arXiv 2410.11908](https://arxiv.org/abs/2410.11908), LLM + graphormer + diffusion, prompt-guided editing, **no code repo exists**, and built on HouseDiffusion so it inherits the NC bar). If a third party gave you the name "Chat2Plan", treat it as likely hallucinated. |
| **PlanGen** | ⚠️ Exists but is **not floorplans** — [arXiv 2503.10127](https://arxiv.org/abs/2503.10127), ICCV 2025, *"Unified Layout Planning and Image Generation in Auto-Regressive VLMs"*, i.e. object boxes in natural images. [360CVGroup/PlanGen](https://github.com/360CVGroup/PlanGen), Apache 2.0. Irrelevant. |
| **FloorPlanGPT** | ❌ Does not exist as a research artifact. Only commercial web toys use the name. |
| **DiffPlanner** | ✅ Real — see §4.3. |

### 4.3 2024–2026 successors — what is actually new

From an arXiv API sweep of `abs:"floorplan generation" OR abs:"floor plan generation"`,
newest first. **Code/licence is UNCONFIRMED for all of these unless noted** — most
are too recent to have released repos.

| Paper | arXiv | Date | In → Out |
|---|---|---|---|
| **HypergraphFormer: Learning Hypergraphs from LLMs for Editable Floor Plan Generation** — Klimenko, Salehipour, Eftekhar, **Khasahmadi**, **Weber** | [2605.18932](https://arxiv.org/abs/2605.18932) | 2026-05 | arbitrary irregular boundary → **editable hypergraph text representation**. Trained on RPLAN + a new OOD dataset they release. Claims to beat raster and vector SOTA and to be far more data-efficient under distribution shift. Authors are **Autodesk Research**-affiliated — this is the closest published thing to what Forma would ship. |
| **Generative Floor Plan Design with LLMs via RLVR** — Lara, Milios, Luo, Sharma, Luo, Beckham, **Golemo**, **Pal** (Mila/Polytechnique) | [2605.14117](https://arxiv.org/abs/2605.14117) | 2026-05, **Findings of ACL 2026** | connectivity + numerical constraints → floor plan. SFT on real plans then RL with *verifiable* rewards. Reports "at least 94% relative reduction in Compatibility" error. **The RLVR idea is the important one: it is a learned model with a hard constraint checker in the loop** — exactly the hybrid your rules engine needs. |
| **Unified Vector Floorplan Generation via Markup Representation** — Shiohara, Yamasaki (U. Tokyo) | [2604.04859](https://arxiv.org/abs/2604.04859) | 2026-04 | FML markup + transformer → high-fidelity vectors across multiple conditioning tasks |
| **Directly from Alpha to Omega: Controllable End-to-End Vector Floor Plan Generation** — Wang, Pajarola (U. Zurich) | [2602.20377](https://arxiv.org/abs/2602.20377) | 2026-02 | boundary → vector plan, topology+geometry-enhanced diffusion |
| **TLC-Plan: Two-Level Codebook Network for End-to-End Vector Floorplan Generation** — Xiong et al. | [2602.07100](https://arxiv.org/abs/2602.07100) | 2026-02 | boundary → topologically-valid vectors, hierarchical VQ-VAE + transformer |
| **Boundary-Constrained Diffusion Models for Floorplan Generation** — Stoppani, Bacciu, Mokarizadeh | [2602.01949](https://arxiv.org/abs/2602.01949) | 2026-02 | boundary → layouts, Boundary Cross-Attention |
| **Mitigating Domain Shift in Conditioned Floor Plan Generation: Synthetic Pre-training** — Ospici, Gueze, Bourrat, Bernhardt | [2607.06483](https://arxiv.org/abs/2607.06483) | 2026-07 | ⭐ **Directly relevant to your licence problem:** procedurally-generated *synthetic* pre-training data with constraint enforcement, then data-efficient adaptation. A route to a model with **zero third-party data licence exposure**. |
| **Space Syntax-guided Post-training** — Jiang, Zhang | [2602.22507](https://arxiv.org/abs/2602.22507) | 2026-02 | RL post-training with a space-syntax oracle |
| **Ergonomic Principles Guided Apartment Layout Generation** — Nieciecki, Płocharski, Musialski | [2604.08411](https://arxiv.org/abs/2604.08411) | 2026-04 | transformer + **differentiable ergonomic loss** |
| **GFLAN: Generative Functional Layouts** — **Abouagour & Garyfallidis** | [2512.16275](https://arxiv.org/abs/2512.16275) | v1 2025-12, v2 2026-07 | ⭐ **Same authors as ResPlan.** Two-stage: (A) CNN dual-encoder allocates room centroids via probability maps; (B) Transformer-augmented GNN jointly regresses room boundaries. **In:** exterior boundary + front-door location. **Out:** room centroids + boundaries. ⚠️ **No code repo found** — checked `github.com/m-agour?tab=repositories` on 2026-08-17: `ResPlan` is there, **`GFLAN` is not**. |
| **DiffPlanner: Eliminating Rasterization** — Wang, Pajarola | [2508.13738](https://arxiv.org/abs/2508.13738) | 2025-08, **accepted IEEE TVCG** | boundary → vectors, entirely in vector space with a designer-process alignment mechanism. Explicitly attacks the vector→raster→vector information loss that Graph2Plan/HouseGAN suffer. |
| **FloorPlan-DeepSeek (FPDS)** — Yin, Zeng, Zhong et al. | [2506.21562](https://arxiv.org/abs/2506.21562) | 2025-06 | text → vector plan by **autoregressive next-room prediction** (LLM-token analogy) |
| **FloorplanMAE** — Yin, Zhong, Zeng et al. | [2506.08363](https://arxiv.org/abs/2506.08363) | 2025-06 | partial sketch → completed layout, masked autoencoder + ViT |
| **Unit Region Encoding** — Zhang, Wang, Li et al. | [2501.11097](https://arxiv.org/abs/2501.11097) | 2025-01 | boundary-adaptive unit-region partition; a compact **representation** reusable across tasks |
| **HouseTune** — Zong, Chen, Zhan, Yu, Tan | [2411.12279](https://arxiv.org/abs/2411.12279) | 2024-11 (v4) | NL description → CoT LLM draft layout → diffusion refinement. Two-stage LLM+diffusion, i.e. the architecture the internal `GEMINI_THOUGHTS.md` note describes. |
| **DStruct2Design** — Luo, Lara, Luo, Golemo, Beckham, Pal | [2407.15723](https://arxiv.org/abs/2407.15723) | 2024-07 | ⚠️ LLM fine-tuning over an **intermediate data structure** (numeric room properties + constraints) rather than pixels. Data converted from **RPLAN + ProcTHOR-10k** → **RPLAN-derived, so encumbered**. (The "CC BY 4.0" on the arXiv page is the *paper* licence, not the data licence.) The **ProcTHOR-derived half is clean**: `allenai/procthor` and `allenai/procthor-10k` are both **Apache 2.0** (verified from raw `LICENSE`). So there is an LLM-constraint benchmark here with no RPLAN in it — you just have to drop the RPLAN half. **Repo: [plstory/DS2D](https://github.com/plstory/DS2D), [Apache 2.0](https://raw.githubusercontent.com/plstory/DS2D/master/LICENSE)** — you can ship the *converter*, not the converted RPLAN data. |
| **GSDiff** — Hu et al., **AAAI 2025** | [github](https://github.com/SizheHu/GSDiff) | 2025 | ⭐ Generates **wall-junction graphs** (structural graph: corners + edges) then rooms — semantically the closest to real walls. GPL-3.0, weights on Google Drive, trained on RPLAN (+ optional LIFULL). Copyleft + tainted weights, but the *method* is the right shape. |
| **Raster2Seq** — Phung & Averbuch-Elor (Cornell), **SIGGRAPH 2026** | [github](https://github.com/Cornell-VAILab/Raster2Seq) | 2026-07 | **Reconstruction, not generation**: RGB plan image → labelled polygon sequences, autoregressive. **MIT**, checkpoints on HuggingFace. Useful if you need to ingest customer PDFs/scans into vectors. Trained on Structured3D + **CubiCasa5K (CC BY-NC)** → retrain before shipping. |
| **PlanCraft** — Zeng, Dai, Yin et al. | [2607.23491](https://arxiv.org/abs/2607.23491) | 2026-07 | sketch → refined vector plan → furnished 3D |
| **HomeWorld** — Li, Ju, Qin, Fang, Li | [2606.06390](https://arxiv.org/abs/2606.06390) | 2026-06 | LLM floorplan → VLM furniture placement → interactive 3D home |
| **DPLAN: Minimal Connectivity to Floorplan Generation** — Lohani & **Shekhawat** | [2606.21159](https://arxiv.org/abs/2606.21159) | 2026-06 | ⭐ **Non-learned.** Graph-theoretic + triangulation: door-connectivity + adjacency constraints → **rectangular or orthogonal** floor plans. See §5. |
| **Algorithmic Design & Graph-Based Classification for Rectilinear-Shaped Modules** — Lohani, Suthar, Shekhawat | [2601.00539](https://arxiv.org/abs/2601.00539) | 2026-01 | ⭐ **Non-learned.** Adjacency requirements → **L- and T-shaped** module arrangements. See §5. |

### 4.4 The "solvable email" tier — working artifacts with NO licence file

These have released code and/or weights and their authors simply never attached a
licence. Legally that means **all rights reserved**, so they are unusable today —
but this is a solvable request, not a legal wall. Worth four emails.

| Work | Repo | State | Output |
|---|---|---|---|
| **DiffPlanner** — Wang & Pajarola, **IEEE TVCG 31(10):7906–7922, 2025**, DOI [10.1109/TVCG.2025.3559682](https://doi.org/10.1109/TVCG.2025.3559682) | [shidong-wang/DiffPlanner](https://github.com/shidong-wang/DiffPlanner), 7★, last push 2025-10-02, **weights via GitHub Releases** | **No LICENSE — verified 404** | ⚠️ **axis-aligned boxes**, not polygons, despite the "direct vector" framing. Doors/windows added by the **rule-based RPLAN/Graph2Plan post-process**, not learned. |
| **floor-plan-rlvr** — Lara, Milios, … Pal (Mila), **Findings of ACL 2026**, [arXiv 2605.14117](https://arxiv.org/abs/2605.14117) | [ludolara/floor-plan-rlvr](https://github.com/ludolara/floor-plan-rlvr), last commit 2026-07-30; weights on HF (`ludolara/fp5-rlvr-Llama3.3-70B`) | **No LICENSE — verified 404**, *and* the **Llama-3.3 Community License** applies on top (700M MAU cap, "Built with Llama" attribution) | ⭐ **The most attractive output format found: room polygons as ordered vertices in absolute metres, CAD-ready, with interior + entrance doors as entities.** Blocked twice over. |
| **HouseMind** — Qin, Weber, Lu (Tsinghua/Berkeley), **CVPR 2026**, [arXiv 2603.11640](https://arxiv.org/abs/2603.11640) | weights on Tsinghua Cloud; code "Soon" | **No licence anywhere** | 256×256 **raster** + JSON. Paper verbatim: *"Functional components like doors, windows, and furniture are not yet modeled."* |
| **FMLM / Floorplan Markup Language** — Shiohara & Yamasaki (U. Tokyo), **CVPR 2026 Highlight**, [arXiv 2604.04859](https://arxiv.org/abs/2604.04859) | [project page](https://mapooon.github.io/FMLPage) — every link checked, plus the author's 10 public repos: **no code exists yet** | n/a | ⭐ One model handles boundary / adjacency graph / room counts / **partial floorplan** conditioning via an HTML-like tagged sequence. Emits **room polygons + interior and front doors as line segments**. |
| **TLC-Plan** — [arXiv 2602.07100](https://arxiv.org/abs/2602.07100) | [rosolose/TLC-PLAN](https://github.com/rosolose/TLC-PLAN) — **a stub: 2 commits, README + assets, no code, no weights** | No LICENSE | boxes + room polygons; doors encoded implicitly by vertex rotation |
| **HypergraphFormer** — Autodesk Research, [arXiv 2605.18932](https://arxiv.org/abs/2605.18932) | Paper *claims* it releases code + a new architect-designed dataset **WMR24**, but **no URL appears anywhere in the paper** | n/a | editable hypergraph → polygons against **arbitrary footprints**. Given Autodesk authorship, expect restrictive or absent terms. |
| **CE2EPlan** (*Directly from Alpha to Omega*) — Wang & Pajarola, **TVCG 2026**, [arXiv 2602.20377](https://arxiv.org/abs/2602.20377) | no code | preprint is **CC BY-NC-ND** | boxes again; doors/windows via the same rule-based post-process |

Also paper-only, no locatable code: **HouseTune/HouseLLM**, **FloorPlan-DeepSeek**,
**FloorplanMAE**, **Unit Region Encoding**, **Boundary-Constrained Diffusion**
(ESANN 2026 — builds directly on HouseDiffusion, inherits the NC bar),
**GreenPlanner**, **PlanCraft**.

### 4.5 Hugging Face: nothing usable

A sweep of the HF model index for floorplan models found only hobby-grade raster
Stable Diffusion / DDPM fine-tunes (0–64 downloads, `creativeml-openrail-m` or
unlicensed). **No production-grade, commercially-licensed, vector floorplan model
exists on Hugging Face.**

### 4.6 Corrections to two entries above

- **GSDiff** full citation: Sizhe Hu, Wenming Wu, Yuntao Wang, Benzhu Xu, Liping
  Zheng, *Synthesizing Vector Floorplans via Geometry-enhanced Structural Graph
  Generation*, **AAAI 2025** — [arXiv 2408.16258](https://arxiv.org/abs/2408.16258).
  Its licence is **clean GPL-3.0** (no research-only rider; `spdx_id: GPL-3.0`),
  and weights are released for **both RPLAN and LIFULL** variants.
  **Architecturally it has the best output representation available under any
  licence**: nodes = wall junctions, edges = wall segments, rooms recovered as
  minimal cycles → true vector wall topology + semantic room polygons. Still
  ❌ doors, ❌ windows, ❌ thickness. GPL-3.0 will infect a shipped BIM product;
  viable only for never-distributed SaaS, or as a clean-room reimplementation target.
- **GFLAN** ⭐ — **the only system found that emits doors *and* windows** (auxiliary
  heatmap heads snapped to wall segments), and **the only one trained on a CC BY 4.0
  corpus** (ResPlan). No repo yet; given these authors' MIT/CC-BY track record a
  release is plausible. **Watch this one.**

**Reading of the trend (2024 → 2026):** the field has moved decisively away from
raster generation. Three things replaced it: (1) **native vector diffusion**
(HouseDiffusion → DiffPlanner → Alpha-to-Omega → TLC-Plan), (2) **LLMs over a
symbolic/structured representation** (DStruct2Design → HouseTune → FPDS →
HypergraphFormer → RLVR), and (3) **explicit wall/junction graphs** (WallPlan →
GSDiff). Graph2Plan's raster-then-boxes pipeline is two generations obsolete.

---

## 5. Non-learned / production-grade approaches

This is the section that matters most for a shippable product, because **every
constraint that must be *guaranteed* rather than *likely* has to be enforced by a
solver, not a network.** Minimum room dimensions, egress widths, no-overlap,
full-coverage of the boundary, wall alignment to a grid — a diffusion model gives
you these ~90% of the time, which is 0% of the time from a building-code
standpoint.

### 5.1 Solver tooling you can actually ship — licences verified

Read from PyPI JSON metadata / raw `LICENSE` files, 2026-08-17:

| Tool | Version checked | Licence | Commercial? | Fit |
|---|---|---|---|---|
| **Google OR-Tools / CP-SAT** | 9.15.6755 | **Apache 2.0** | ✅ yes | ⭐ **Best default.** CP-SAT is a world-class no-overlap/packing solver; it has native `AddNoOverlap2D` for exactly this problem. |
| **Z3** (`z3-solver`) | 5.1.0.0 | **MIT** | ✅ yes | SMT — good for symbolic/logical constraints, weaker at pure packing optimisation |
| **HiGHS** (`highspy`) | 1.15.1 | **MIT** (verified on repo) | ✅ yes | LP/QP/MIP, no third-party deps, easy to embed |
| **SCIP** | current | **Apache 2.0** (verified `scipopt/scip/LICENSE`) | ✅ yes | ⚠️ **Important history:** SCIP was under the restrictive *ZIB Academic License* until v8 (2022). Old advice saying "SCIP is academic-only" is out of date — but pin your version and check. |
| **PySCIPOpt** | 6.2.1 | MIT | ✅ yes | Python binding for SCIP |
| **python-mip** | 1.17.6 | **EPL-2.0** | ✅ yes (weak copyleft, file-level) | CBC/Gurobi wrapper |
| **PySAT** (`python-sat`) | 1.9.dev | MIT | ✅ yes | pure SAT, for feasibility of adjacency/topology |
| **kiwisolver** (Cassowary) | 1.5.0 | **BSD-3-Clause** | ✅ yes | ⭐ Incremental linear constraint solver — the right tool for the **interactive** case: user drags a wall, everything else re-satisfies in real time. This is how UI layout engines work; it maps directly onto dimension-driven plan editing. |
| **Shapely** | 2.1.2 | BSD-3-Clause | ✅ yes | geometry kernel (also what ResPlan ships in) |
| **NetworkX** | 3.6.1 | BSD-3-Clause (PyPI metadata empty; licence is BSD-3 in repo — **UNCONFIRMED** from raw file) | ✅ yes | adjacency graph manipulation |
| **Gurobi** | — | **Commercial, paid** | 💰 licence fee | fastest MIP; a real per-seat/per-core cost in a SaaS |

**Recommendation:** OR-Tools CP-SAT (Apache 2.0) for batch generation +
kiwisolver (BSD) for interactive editing. Both are permissive, both are
production-hardened, neither has a data-licence problem at all.

### 5.2 Graph-theoretic / rectangular-dual approaches (exact, guaranteed)

This literature is the strongest non-learned line and it is under-appreciated.
It comes from VLSI floorplanning: given an **adjacency graph**, construct a
**rectangular dual** — a partition of a rectangle into rectangles whose adjacency
structure is exactly the input graph. Where a solution exists it is *constructed*,
not sampled, so constraints are satisfied by construction.

**Krishnendra Shekhawat's group (BITS Pilani)** is the active line here. From an
arXiv API sweep:

| Paper | arXiv | Date | What it gives you |
|---|---|---|---|
| **DPLAN: Minimal Connectivity to Floorplan Generation** — Lohani & Shekhawat | [2606.21159](https://arxiv.org/abs/2606.21159) | 2026-06 | **In:** graph of rooms + required **door** connections + **non-adjacency** (forbidden) constraints. Adds edges if disconnected, builds a bi-connected plane triangulation, removes separating triangles, converts to a floor plan. **Out:** rectangular (RFP) *or* orthogonal (OFP) floor plans. **Guarantees no overlapping rooms and no empty space.** Implemented in Python with an interactive prototype — ⚠️ **no public repo URL given in the paper. UNCONFIRMED whether code is obtainable.** |
| **Algorithmic Design & Graph-Based Classification for Rectilinear-Shaped Modules** — Lohani, Suthar, Shekhawat | [2601.00539](https://arxiv.org/abs/2601.00539) | 2026-01 | Extends the above to **L- and T-shaped rooms** via prioritised canonical ordering |
| **A Theory of L-shaped Floor-plans** — Raveena & Shekhawat | [2205.14434](https://arxiv.org/abs/2205.14434) | 2022 | O(n²) algorithm; necessary *and sufficient* conditions for L-shaped plans from properly triangulated planar graphs |
| **Linear-time orthogonal floor plans with minimum bends** — Pinki & Shekhawat | [2006.14182](https://arxiv.org/abs/2006.14182) | 2020 | Linear-time rectilinear dual with provably minimal bend count |

> ⭐ **Note what DPLAN supports that Graph2Plan explicitly cannot:
> forbidden adjacencies.** Graph2Plan's own limitations section lists the absence
> of "forbidden" constraints as a known gap. A classical solver gets this for free.

⚠️ I could **not** confirm a public code release for any of the Shekhawat papers.
A `github.com/search?q=GPLAN floor plan Shekhawat` query returned **0
repositories**. If you want this line you will likely have to reimplement from
the papers (the algorithms are fully specified) or contact the authors.

### 5.3 Classical academic layout methods worth knowing

**Citations verified via the Crossref API** (authors, venue, year, DOI).
Availability of *code* for these is **UNCONFIRMED** — I did not locate public
implementations for any of them.

- **Merrell, Schkufza, Koltun — "Computer-Generated Residential Building Layouts"**,
  **ACM TOG / SIGGRAPH Asia 2010**, DOI [10.1145/1882261.1866203](https://doi.org/10.1145/1882261.1866203).
  Bayesian network learned from architectural programs, sampled with
  Metropolis-Hastings, then refined. The classic reference for *whole-building*
  residential layout; the precursor to everything in §4.
- **Bao, Yan, Mitra, Wonka — "Generating and Exploring Good Building Layouts"**,
  **ACM TOG 2013 (SIGGRAPH)**, DOI [10.1145/2461912.2461977](https://doi.org/10.1145/2461912.2461977).
  Characterises the *space of good layouts* rather than sampling one — directly
  relevant to a variant-exploration UI, which is what a generative-design product
  actually sells.
- **Peng, Yang, Wonka — "Computing Layouts with Deformable Templates"**,
  **ACM TOG 2014 (SIGGRAPH)**, DOI [10.1145/2601097.2601164](https://doi.org/10.1145/2601097.2601164).
  Tiles a domain with deformable templates via integer programming; handles
  non-rectangular boundaries better than box packing.
- **Wu, Fan, Liu, Wonka — "MIQP-based Layout Design for Building Interiors"**,
  **Computer Graphics Forum (Eurographics) 2018**, DOI [10.1111/cgf.13380](https://doi.org/10.1111/cgf.13380).
  Mixed-integer quadratic programming. ⚠️ Note the author list is
  **Wu, Fan, Liu, Wonka** — not "Wu, Xu, Wang, Chu" as sometimes miscited.
- ⭐ **Marson & Musse — "Automatic Real-Time Generation of Floor Plans Based on
  Squarified Treemaps Algorithm"**, *International Journal of Computer Games
  Technology*, **2010**, DOI [10.1155/2010/624817](https://doi.org/10.1155/2010/624817)
  — **open access**. Builds on **Bruls, Huizing & van Wijk, "Squarified Treemaps",
  Eurographics 2000**, DOI [10.1007/978-3-7091-6783-0_4](https://doi.org/10.1007/978-3-7091-6783-0_4).
  **This is the cheapest possible v0**: it packs rooms into a boundary by target
  area with reasonable aspect ratios, in **real time**, deterministically, with
  **zero data and zero licensing risk**. Squarified treemap is ~100 lines of code
  and there are permissive implementations in every language. If you need
  something generating plausible plans this week, start here.
- **Camozzato, Dihl, Silveira, Marson, Musse — "Procedural floor plan generation
  from building sketches"**, **ACM SIGGRAPH 2015 Posters**,
  DOI [10.1145/2787626.2787653](https://doi.org/10.1145/2787626.2787653).
  Constrained-growth room packing from a sketched outline.
- **Lopes, Tutenel, Smelik, de Kraker, Bidarra — "A Constrained Growth Method for
  Procedural Floor Plan Generation"** (TU Delft). ⚠️ **Not indexed in Crossref**
  — targeted queries returned only the group's other procedural-content papers.
  It is a **GAME-ON 2010 workshop paper**, which is why it has no DOI.
  **Citation UNCONFIRMED**; the TU Delft group's procedural-worlds line is real
  and adjacent (e.g. Tutenel et al., *"Generating Consistent Buildings"*, IEEE
  TCIAIG 2011, DOI [10.1109/tciaig.2011.2162842](https://doi.org/10.1109/tciaig.2011.2162842)),
  but treat the exact title/venue as unverified until you see the PDF.
- **VLSI floorplanning representations** — sequence pair, B*-tree, corner block
  list, O-tree. Decades of literature on exactly "pack rectangles with
  constraints". **UNCONFIRMED** which open-source implementations are currently
  maintained and permissively licensed.

**One working classical implementation you can actually look at:**
[hellguz/Magnetizing_FloorPlanGenerator](https://github.com/hellguz/Magnetizing_FloorPlanGenerator)
— a **Grasshopper plugin for Rhino 6+**, 71★/18 forks, 19 commits. Purely
classical: a *"quasi-evolutionary strategy"* with iterative room placement,
adjacency handling and corridor generation — no neural network anywhere.
**In:** boundary curve + room program (names, areas, connections) + cell size and
iteration parameters. **Out:** floor plan curves including circulation.
Paper: Gavrilov, Schneider, Dennemark, Koenig (2020), *"Computer-aided approach to
public buildings floor plan generation"*, 1st Int. Conf. on Optimization-Driven
Architectural Design (Bauhaus-Universität Weimar).
⚠️ **Licence not stated in the README — UNCONFIRMED** (a GitHub API check was
rate-limited). Useful as a reference implementation and a demonstration that the
classical route ships; verify the licence before reusing code.

### 5.4 Commercial products — what is actually documented

⚠️ **UNCONFIRMED across the board.** I did not complete a verified pass over
TestFit, Autodesk Forma/Spacemaker, Finch3D, Digital Blue Foam, Archistar,
Hypar, Snaptrude, maket.ai or ARCHITEChTURES. Their published material is
marketing copy; almost none publish algorithms. Treat any claim about their
internals as unverified unless traced to a patent or paper.

Two hard signals I *can* record:

- **Autodesk Research authorship appears directly in this literature.**
  House-GAN++ ([arXiv 2103.02574](https://arxiv.org/abs/2103.02574)) lists
  Kai-Hung Chang, Hang Chu and Chin-Yi Cheng of Autodesk Research;
  **HypergraphFormer** ([arXiv 2605.18932](https://arxiv.org/abs/2605.18932), 2026)
  lists Amir Khasahmadi and Ramon Elias Weber. The 2026 Autodesk-affiliated work
  is **LLM-over-hypergraph**, not GAN and not diffusion. That is the clearest
  available signal of where a well-resourced incumbent has actually landed.
- **RPLAN itself was co-produced with a commercial platform** (Kujiale, the
  second affiliation on the 2019 paper) — yet the public release is still
  non-commercial. Industrial players work from their own proprietary corpora.

For diligence on TestFit specifically, search USPTO/Google Patents rather than
their website. I attempted this and **could not complete it**:
`patents.google.com` returned **HTTP 503**, and the PatentsView API
(`api.patentsview.org`) now requires an API key and returned empty for assignee
queries on TestFit, Spacemaker, Finch3D and Hypar. **UNCONFIRMED whether relevant
patents exist** — this is an open diligence item, not a negative finding.

### 5.5 BIM output tooling — the part nobody else does for you

Since §4 established that **no learned model emits BIM**, the export layer is
entirely yours. Two permissive options, both verified:

- ⭐ **[hypar-io/Elements](https://github.com/hypar-io/Elements)** — **MIT**, 410★,
  80 forks, C#, ~5,579 commits, actively developed. *"A cross-platform library for
  creating building elements"* — a hybrid **BREP/CSG geometry kernel** (vectors,
  lines, arcs, polygons) with serialisation to **JSON, IFC, glTF, DXF and SVG**,
  explicitly designed so you can *"programmatically generate buildings without
  relying on proprietary geometry kernels or host applications like Revit or
  Rhino."* Unitless right-handed coordinates, +Z up; extend the base `Element`
  class for custom types.
  **This is the single most directly reusable artifact found in this entire
  research pass** for a BIM engine, and it is MIT. Note that Hypar is also one of
  the commercial products in §5.4 — they open-sourced their geometry core.
- **[IfcOpenShell](https://github.com/IfcOpenShell/IfcOpenShell)** — 2,700★, C++/Python,
  ~22,488 commits, very active. Parses IFC2x3 TC1 through IFC4x3 Add2, plus the
  `IfcConvert` tool. ⚠️ **Dual-licensed and you must be careful which part you
  touch:** the **core library is LGPL-3.0-or-later** (dynamic linking is fine for
  a closed product), but **Bonsai and IfcSverchok are GPL-3.0-or-later** (Blender
  add-ons — do not vendor these into a proprietary product).

Pairing Elements (MIT) for authoring with IfcOpenShell (LGPL core, dynamically
linked) for interoperability is a clean, fully commercial-safe BIM output stack.

### 5.6 The synthesis worth building

Nothing in §4 emits BIM. Every learned model stops at room polygons; walls with
thickness, openings with swing direction, and code compliance are all yours.
The defensible architecture is therefore:

1. **Topology** — propose the room adjacency graph. LLM or GNN, or just retrieval
   from ResPlan (Graph2Plan's genuinely good idea, reimplemented from the paper).
2. **Geometry** — realise the graph inside the boundary. Either a learned vector
   model retrained on CC BY data, or a **rectangular-dual / CP-SAT solve** — the
   solver route needs no training data at all and satisfies constraints by
   construction.
3. **Repair & compliance** — CP-SAT / kiwisolver pass that enforces minimum
   dimensions, grid snapping, egress, no-overlap. This is the RLVR paper's
   "verifiable reward" idea moved to inference time.
4. **BIM lift** — thicken walls, place openings, export IFC/DXF. Entirely
   deterministic, entirely yours, and the actual product moat.

Step 2 is the only step where the ML literature helps, and step 3 can substitute
for it entirely at the cost of some plausibility. **A solver-first v0 has zero
data-licensing exposure and ships now**; add the learned prior later, trained on
ResPlan + Swiss Dwellings, once the deterministic spine exists.

Concretely, in ascending order of cost:

| Stage | Approach | Data licence exposure | Effort |
|---|---|---|---|
| **v0, this week** | **Squarified treemap** (Marson & Musse 2010) inside the boundary | **none** | ~100 lines |
| **v1** | **CP-SAT** no-overlap + min-dimension + adjacency constraints (OR-Tools, Apache 2.0); **kiwisolver** for interactive drag | **none** | days |
| **v1.5** | **Rectangular-dual / DPLAN-style** construction from the adjacency graph — supports *forbidden* adjacencies, which no learned model does | **none** (reimplement from papers) | weeks |
| **v2** | Learned prior for room topology + proportions, **retrained from scratch** on ResPlan + Swiss Dwellings, architecture reimplemented from GSDiff / HouseDiffusion / MaskPLAN papers | **CC BY 4.0 attribution only** | months |
| **always** | Wall thickening, openings, IFC/DXF export, code compliance | **none — this is your product** | ongoing |

The important structural point: **steps v0–v1.5 have no third-party data in them
at all.** You can ship, sell, and demo the whole product before you ever touch a
dataset. That completely removes licensing from the critical path — which, given
everything above, is worth a great deal.

---

## 6. Corrections to the sibling repo `plan-generator-3000-pro-max/LICENSING.md`

A sibling project at `C:\Users\tng\g2p\plan-generator-3000-pro-max` already has a
Phase-2 licensing analysis. It is directionally correct and better than most, but
it contains three errors that this research corrects. **I did not edit that file —
it belongs to a different project.** Flagging for you to action.

1. **Dead ResPlan URL (line 52).** It cites
   `github.com/DeepLearningAndArchitecture/ResPlan`, which **404s**. The real repo
   is **<https://github.com/m-agour/ResPlan>** (verified HTTP 200).
2. **HouseDiffusion is understated (lines 32–33).** The doc implies the *weights*
   are the binding constraint and that *"the HouseDiffusion source code itself
   carries a permissive…"* licence. **The code is equally barred** — the LICENSE
   names both: *"The code **and the model weights**… are not allowed for commercial
   usage."* There is no scenario where the source is usable and only the weights
   get swapped out.
3. **Graph2Plan is unlicensed and is checked out locally** at
   `C:\Users\tng\g2p\Graph2plan`. It has **no LICENSE file** (confirmed both
   locally and via the GitHub contents API) = all rights reserved, and it
   hard-depends on **MATLAB**. If any of its code — or its released `Data.zip`,
   which is redistributed RPLAN — has informed that pipeline, it needs the same
   containment treatment the doc already applies to HouseDiffusion.
4. **Add a dataset-provenance column.** The doc tracks *component* licences but
   not *data* licences, which is where the actual blocker lives.
   **RPLAN clause 7 binds a for-profit employer** and belongs in that table in bold.

## Appendix: sources fetched

Primary sources read directly for this note (2026-08-17):

- `https://arxiv.org/abs/2004.13204`, `https://ar5iv.labs.arxiv.org/html/2004.13204`
- `https://arxiv.org/abs/2508.14006`, `https://arxiv.org/html/2508.14006v2`
- `https://api.github.com/repos/HanHan55/Graph2plan` (+ `/license`, `/contents`, `/releases`, `/forks`)
- `https://raw.githubusercontent.com/HanHan55/Graph2plan/master/README.md`
- `https://api.github.com/repos/m-agour/ResPlan` (+ `/contents`)
- `https://raw.githubusercontent.com/m-agour/ResPlan/main/{LICENSE,README.md,TAKEDOWN.md}`
- `https://raw.githubusercontent.com/m-agour/ResPlan/main/ResPlan.zip` (downloaded, 100 MB; pickle opcodes inspected)
- `http://staff.ustc.edu.cn/~fuxm/projects/DeepLayout/index.html` (HTTP only — HTTPS refused)
- `https://docs.google.com/forms/d/e/1FAIpQLSfwteilXzURRKDI5QopWCyOGkeb_CFFbRwtQ0SOPhEg0KGSfw/viewform`
- `https://raw.githubusercontent.com/CubiCasa/CubiCasa5k/master/LICENSE`
- `https://zenodo.org/records/7788422`, `https://zenodo.org/records/14223942`
- `https://data.4tu.nl/datasets/e1d89cb5-6872-48fc-be63-aadd687ee6f9`
- `https://caspervanengelenburg.github.io/msd-eccv24-page/`, `https://raw.githubusercontent.com/caspervanengelenburg/msd/main/README.md`
- `https://api.github.com/repos/{zzilch/RPLAN-Toolbox,caspervanengelenburg/msd,SizheHu/GSDiff,luozn15/FloorplanGAN}`
- `https://pypi.org/pypi/rplanpy/json`
- `https://raw.githubusercontent.com/{aminshabani/house_diffusion,ennauata/housegan,ennauata/houseganpp,LengSicong/Tell2Design,scipopt/scip}/{main,master}/LICENSE`
- `http://export.arxiv.org/api/query?...` — sweeps for `"floor plan generation"` (40 newest) and `Shekhawat AND "floor plan"`
- `https://arxiv.org/abs/{2512.16275,2605.18932,2605.14117,2508.13738,2407.15723,2606.21159,2504.09694}`
- `https://github.com/{SizheHu/GSDiff,Cornell-VAILab/Raster2Seq,lalalalaxxx/LayoutBridge,HangZhangZ/MaskPLAN,zengpengyu-student/Residential_Floorplan_Diffusion,cgjiahui/WallPlan,m-agour?tab=repositories}`
- `https://aclanthology.org/2023.acl-long.820/`
- `https://pypi.org/pypi/{ortools,z3-solver,highspy,PySCIPOpt,kiwisolver,mip,python-sat,shapely,networkx}/json`
- `https://raw.githubusercontent.com/{allenai/procthor,allenai/procthor-10k}/{main,master}/LICENSE`
- `https://www.kaggle.com/api/v1/datasets/list?search=modified-swiss-dwellings` (resolved the MSD licence question)
- `https://zenodo.org/records/18874946` (the unauthorised RPLAN mirror)
- `https://archilyse.standfest.science/swiss-dwellings` (Swiss Dwellings schema)
- `https://api.crossref.org/works?query.bibliographic=…` — verified Merrell 2010, Bao 2013, Peng 2014, Wu 2018, Marson & Musse 2010, Bruls 2000, Camozzato 2015
- `https://github.com/{hypar-io/Elements,IfcOpenShell/IfcOpenShell,hellguz/Magnetizing_FloorPlanGenerator}`
- RPLAN full Terms of Use: `https://drive.google.com/file/d/1wEbccL5NAL_mzFt2hyxPqZppXDalbApW/view`
- `https://www.nii.ac.jp/dsc/idr/en/lifull/` (LIFULL HOME'S agreement)

### Sources that could NOT be retrieved

- `http://staff.ustc.edu.cn/...` over **HTTPS** — `ECONNREFUSED :443`. Plain HTTP worked.
- `web.archive.org` — blocked by the fetch tool.
- The RPLAN **full terms & conditions** Google Drive document linked from the access form.
- The **Kaggle web pages** for MSD — but the **Kaggle public API** answered
  (`api/v1/datasets/list?search=…`), which is how the CC BY vs CC BY-SA question
  was resolved. Use that API, not the HTML, for Kaggle licence checks.
- `jcliu0428/awesome-building-layout-generation` — the README is a stub (one line).
- `scipopt.org` — HTTP 429. SCIP's licence was confirmed from the repo `LICENSE` instead.
- **FloorplanGAN's paper text** — paywalled (ScienceDirect 403, no OA copy, empty
  abstracts across Crossref/OpenAlex/Semantic Scholar). Its I/O representation was
  read from the **source code**, not the paper.
- **MaskPLAN's CVF PDF** — CVF returned 403 to automated fetch. Title/venue/DOI
  cross-verified via Crossref, IEEE Xplore (doc 10657009) and the repo; the
  verbatim output quotes came from the CVF supplementary.
- **Structured3D's full ToU document** (behind a Drive agreement form).
- **HypergraphFormer's promised code and WMR24 dataset** — announced in the paper,
  no URL published anywhere.
- **Live status of three Google Drive artifacts** (House-GAN weights,
  HouseDiffusion checkpoint, MaskPLAN checkpoints) — links not exercised. All are
  personal-Drive single points of failure regardless of licensing.

### 🔴 Open legal questions that need counsel, not a researcher

1. **Does RPLAN's ToU extend to trained model weights?** The agreement is
   **silent on weights**. This is the key open question for reusing *any*
   RPLAN-trained checkpoint. My working assumption above (weights are a
   derivative use and therefore encumbered) is the conservative read, not a
   settled one.
2. **Did the MaskPLAN / FloorplanGAN / Graph2Plan authors have the right to
   redistribute the RPLAN-derived arrays they ship?** On the face of clause 2 they
   did not — which may make their MIT grants ineffective *as to that data*.
3. **Is ResPlan's "spatial arrangements are facts, not expression" position
   sound?** It is reasonable but untested, and the existence of a takedown policy
   suggests the authors know it is not airtight. EU/UK **sui generis database
   right** is a separate question the licence does not address at all.
4. **Does CC BY-SA on the Kaggle MSD release reach model weights?** Same shape as
   question 1. If ShareAlike attaches to weights, MSD-trained weights would have to
   be released under CC BY-SA — fatal for a proprietary product. The 4TU CC BY 4.0
   release and Swiss Dwellings both avoid the question.

### Method caveats

- WebSearch quota for the session was exhausted partway through; later discovery
  used the **arXiv API**, **Crossref API**, **Kaggle API** and **GitHub API**
  directly, which are primary sources and arguably better. But it means the §5.4
  commercial-product survey and a few 2024–2026 stragglers are less complete than
  the rest.
- ⚠️ **§5.4 (commercial products) is the one genuinely thin section.** A dedicated
  research pass on TestFit / Forma / Finch3D / Archistar / maket.ai and on
  maintained VLSI-floorplanning implementations was launched but had not reported
  by the time this note was written. **Treat §5.4 as a stub, not a conclusion.**
  Everything else here is verified.
- GitHub's unauthenticated API rate limit (60 req/hr) was hit several times.
  A few small lookups (Hypar's org repo list, ResPlan's `baselines/` contents,
  the Magnetizing generator's licence) are marked UNCONFIRMED for that reason
  alone and would be trivial to complete with a token.
- Some entries were summarised by a fetch tool reading the page rather than by me
  reading raw text end-to-end. Every **licence** claim marked ✅/❌ above was taken
  from a raw `LICENSE` file, a PyPI/GitHub API field, or verbatim form text —
  not from prose summaries.
