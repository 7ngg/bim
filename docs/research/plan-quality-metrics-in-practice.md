# Plan-quality metrics in practice — what anybody else actually scores

Findings for the research question *is the **entry-depth inversion rate** the
right instrument for a fifth `proposer.md` §6.1 plan-quality term?*
The term is specified in `docs/research/zoning.md` **D10** and measured in its
§6.5: nearest private Room strictly nearer the entrance than the nearest social
Room, **31.6 % ordered / 51.0 % tied / 17.4 % inverted** over 2 500 Swiss
dwellings. D10 says *"scored against the corpus **rate** rather than a
threshold"* and leaves the scoring function unwritten. This note asks whether
anyone else scores anything this way, whether anyone else encodes this quantity,
and what the answer costs.

**Research date:** 2026-08-30.
**Method:** primary sources only — arXiv / CVF / ACM papers, space-syntax
proceedings and reprints, official standards and evaluation instruments, product
documentation, published methodology, source code, and the **committed output of
`experiments/zoning/`** already on disk. Marketing pages, blog roundups and
vendor comparison sites are excluded. Anything not read first-hand is marked
**UNCONFIRMED**; §9 lists every source that could not be reached and where it was
looked for.

**This note edits no shipped artefact and runs no corpus pass.** Nothing in
`docs/spec/`, `docs/research/zoning.md`, `experiments/`,
`data/acceptance/rules.json` or `data/standards/room-constraints.json` was
touched. §4, §5, §6 and §7 recompute numbers from
`experiments/zoning/out/zoning.json` **read-only** — the file `entry_order2.py`
already reads. §10 gives the one-liners.

---

## 0. TL;DR

**The instrument is real, it has a name-shaped hole, and it is not ready.** The
discipline that owns this quantity has never named it, has a better-behaved
alternative to the trichotomy, and has a size-normalisation test this term fails.
Five defects were found that each move the headline number or its meaning, and
every one is fixable inside this repo without new data. One finding is not a
defect at all — it *strengthens* the case.

| # | Finding |
|---|---|
| **1** | ⭐ **There is no established name for this quantity, and the obvious one is taken.** Space syntax names the ingredients — **step depth**, **depth from the carrier**, the **inequality genotype** — but not the nearest-private-vs-nearest-social comparison. ⚠️ **"Inverted genotype" is already a Hillier & Hanson term for something unrelated.** Do not reuse it. §3.1. |
| **2** | ⭐ **Space syntax already has the continuous measure this term is reaching for: Hillier's *difference factor*.** `H* = (H − ln2)/(ln3 − ln2)` over the integration values of three space categories, running 0 (strongly ordered) to 1 (no difference). It was invented for exactly the case where an ordering is weak, degrades gracefully, and **does not manufacture a 51 % tie bucket.** §2.6. |
| **3** | ⭐ **Nobody scores a plan against a corpus distribution of an *architectural* quantity.** The field's distribution term is **FID** in a learned feature space. The one paper that builds a real-corpus reference profile — SSPT, [arXiv 2602.22507](https://arxiv.org/abs/2602.22507) — scores it with **mean absolute deviation from a median**, not a divergence. §2.1, §2.2. |
| **4** | ⭐ **The only framework purpose-built to evaluate generated dwellings does not contain the word "entrance" once**, and lists *"the level of privacy between rooms"* in its **limitations** as future work. RFP-A, *Buildings* 15(10):1674, 2025. §2.3. |
| **4b** | ⭐ **Nine market products and the whole patent corpus: unanimously no distribution scoring.** Weighted sums, min/max filters, Pareto dominance, signed distance from a target, hand rules. **Autodesk's core scoring patent says "weighted sum" in the claim itself** (US11423191 cl. 18); Sidewalk Labs' says "weighted average … less than a predetermined threshold". `"floor plan" AND "earth mover"` → **0** across patent full text; **`"space syntax"` → 0**. §3.5, §3.6. |
| **4c** | ⭐ **Exactly one product publishes a public/private set, and it puts the KITCHEN in the PUBLIC one** — Maket: *"common areas like the living room and kitchen sit close to the front door"*; *"public spaces (living room, kitchen, dining) and private ones (bedrooms, bathrooms)."* ⚠️ It is a marketing blog, a hand-written rule, no measure. **And it names a home office as an input and then omits it from both lists** — the sharpest published statement of the §5 gap anywhere. §3.7. |
| **4d** | ⚠️ **Terminology trap for the spec: in the Autodesk patents "circulation" means traffic-crossing density, not depth from an entrance**, and the layout graph's nodes are *occupant positions*, not rooms. The word "entrance" appears **zero** times in the core patents. A reader will assume entry-depth prior art exists; it does not. §3.6. |
| **4e** | ⭐ **§6.2's fix is already the published protocol.** House-GAN++ **never reports a pooled FID** — *"dividing the samples into four groups based on the number of rooms: (5, 6, 7, 8)"*. SSPT states the prevalence-bias problem outright and weights for it. **Report per room-count bucket and cite House-GAN++.** §3.8. |
| **5** | ⭐ **Every symmetric divergence scores "too many inversions" and "too few" identically, and KL is undefined for the outcome you most want.** Computed on this exact distribution: a generator that never inverts and one that inverts twice as often both score **TV 0.174, EMD 0.348**; **KL(corpus‖generator) = ∞** whenever a bucket empties. χ² at N = 2 500 flags a **2 pp** deviation as significant. §2.5. |
| **6** | ⚠️ **§6.5 calls the − bucket a "violation" and D10 asks to *match* its rate. The spec cannot hold both.** Matching a defect rate rewards a generator for producing exactly as many bad plans as real housing. The four shipped terms are typological facts where matching is right; this one is asserted as a defect. §2.7. |
| **7** | ⭐ **Amorim's three-sector paradigm matches the engine's room classes exactly, and it is free, primary and citable.** *"The **Social** sector … living, receiving and dining areas. The **Private** sector … bedrooms and study room. The **Service** sector … kitchen, larder and servants' accommodation."* — [1st Space Syntax Symposium, 1997](http://www.spacesyntax.net/symposia-archive/SSS1/SpSx%201st%20Symposium%2097%20-2003%20pdf/1st%20Symposium%20Vol%20II%20pdf/2%20-%20Domestic%20space/18%20Amorim%20300.pdf). Social excludes the kitchen; Private includes the study. **The engine's two contested classification choices are both already published as one taxonomy.** §4.2. |
| **8** | ⚠️ **But Alexander puts the kitchen on the *public* side, in the same sentence that puts the study on the private side** — *"A bedroom or boudoir is most intimate; a back sitting room or study less so; **a common area or kitchen more public still**; a front porch or entrance room most public of all."* (Pattern 127). **The two traditions disagree and both are canonical.** §4.1. |
| **9** | ⭐ **The social-set definition moves the headline by up to 7.1 points, and the spec has not written it down.** Recomputed read-only: **17.4 %** with social = `LIVING_ROOM/LIVING_DINING/DINING`; **14.7 %** if the kitchen joins; **21.8 %** if the kitchen counts only where no social Room exists. And **29.8 % of the corpus has no social Room at all**, moving the denominator from 1 756 to 2 488. §4.3. |
| **10** | ⚠️ **The engine's stated intent and its own measurement disagree about `KITCHEN_DINING`** — `measure_zoning.py`'s `CLASS` map has no entry for it, so it fell to `"other"`. Three rooms today; a whole region tomorrow. §4.4. |
| **11** | ⭐ **The confound runs the *opposite* way to the one that was feared.** Ties do **not** inflate in small flats: **4.5 %** at n = 4 rising to **63.2 %** at n = 9. Inversion swings **4.5 % → 27.3 % (n = 6) → 7.1 % (n = 11)** — 6× inside the 4–10 band v1 promises. §6.1. |
| **12** | ⭐ **And this is Hillier's own test, failed.** Hillier, Yang & Turner 2012: *"the first two tests of a normalised measure must be: whether the means for the system correlate with the size of the system…"* RA exists at all because H&H applied *"a correcting factor to **eliminate the empirical effects of size**"*. **The proposed term has no such factor.** §6.2. |
| **13** | ⭐ **Without circulation the inversion rate is 2.2 %; with it, 17.8 %.** Inversion is a hall phenomenon, and `openings.md` §7 puts every generated Plan in the with-hall stratum. **17.8 % is the target, not 17.4 %.** §6.4. |
| **14** | ⭐ **49.1 % of applicable dwellings sit in one cell — private at hop 1, social at hop 1** — and 96.3 % of ties are that cell. The term is a near-binary question about one hop off the hall, and the engine builds that hall on every Plan. §7. |
| **15** | ⭐ **The corpus cannot see a study.** Swiss Dwellings' vocabulary here is ten labels and **`STUDY`/`STUDIO` is not among them**; **70.1 %** of the private set is unlabelled `ROOM`. `room-constraints.json` already ships the admission — *"study is the weakest number in the file: a one-desk programme with no corpus to check it against."* §5.1. |
| **16** | ⚠️ **The literature has seen this exact inversion signal and called it *richer*, not defective.** Hanson, *Decoding Homes and Houses* ch. 10, on Monteiro's Recife study: shallow private-coded rooms were *"explained by the existence of a separate library, office, or 'best' room at the front of the house"*, and the conclusion was *"a more flexible use of space and a more heterogeneous and rich disposition of space functions"*. Alexander's Pattern 157 says a home work room should *"be seen from the street"*. §5.2, §5.3. |
| **17** | ⭐ **That benign explanation was tested on this corpus and it does not hold.** The shallow private room in an inversion is a **terminal cell in only 4.9 %** of cases against **26.5 %** in ordered dwellings — the opposite of the front-office signature. **The corpus's 17.4 % is bedrooms off the hall, not studies off the hall.** This is the finding that argues *for* the term. §5.4. |
| **18** | ⚠️ **Entrance-rooted depth measures the visitor interface only.** Hillier's inhabitant/visitor distinction; Ostwald: *"the conventional JPG, with exterior as carrier, is drawn from the point of view of a … 'visitor'"*; Hanson holds that inhabitant–inhabitant relations may matter more. The term's scope statement should say this. §8. |
| **19** | ⭐ **The engine's sample is two orders of magnitude larger than anything in the space-syntax canon** — 2 500 dwellings against Hanson's eighteen and Hillier's seventeen. Whatever else is true, **this repo has the best-powered measurement of this quantity that exists.** §6.3. |

⚠️ **What this note does not say.** It does not say the term is worthless.
Findings 9–14 are repairs, every one computable on data already committed, and
finding 17 removes the strongest argument against. Finding 6 is the one that is
not a repair: it is a question about what the term is *for*, and §2.7 states it as
a choice rather than answering it.

---

## 1. What was read first-hand

| Source | What it is | Read |
|---|---|---|
| **Hillier, Hanson & Peponis (1984)**, *What do we mean by building function?* and **Hillier, Hanson & Graham (1987)**, *Ideas are in things* | The primary definitions of depth, the justified graph, RA and the inequality genotype | **Verbatim**, via the open-access reprint *Space Syntax: Selected papers by Bill Hillier*, eds. Vaughan, Peponis & Conroy Dalton, [UCL Press 2025, CC BY-NC-ND](https://discovery.ucl.ac.uk/10207360/1/Space-Syntax.pdf) |
| **Ostwald (2011)**, *The Mathematics of Spatial Configuration: Revisiting, Revising and Critiquing Justified Plan Graph Theory*, *Nexus Network Journal* 13(2) | The standing methodological critique of JPG measures | [Free PDF](https://link.springer.com/content/pdf/10.1007/s00004-011-0075-3.pdf), pp. 445–457 of 445–470 |
| **Amorim (1997)**, *The Sectors' Paradigm*, 1st Space Syntax Symposium, Vol. II | The three-sector room taxonomy and 140 measured Recife houses | [Free proceedings PDF](http://www.spacesyntax.net/symposia-archive/SSS1/SpSx%201st%20Symposium%2097%20-2003%20pdf/1st%20Symposium%20Vol%20II%20pdf/2%20-%20Domestic%20space/18%20Amorim%20300.pdf) |
| **Hillier, Yang & Turner (2012)**, *Normalising least angle choice in Depthmap*, *J. Space Syntax* 3(2) | Why the earlier size normalisations were insufficient; NAIN/NACH | [UCL Discovery PDF](https://discovery.ucl.ac.uk/id/eprint/1389938/1/Normalising%20least%20angle%20choice.pdf) |
| **Hanson (1998)**, *Decoding Homes and Houses*, CUP | The English house genotype; Monteiro's Recife finding | ⚠️ Scraped text, prose reliable, **pagination not** — cited by chapter. §9 |
| **Alexander, Ishikawa & Silverstein (1977)**, *A Pattern Language*, OUP | Patterns 127, 129, 139, 141, 142, 157 | ⚠️ Transcriptions at [iwritewordsgood.com/apl](https://www.iwritewordsgood.com/apl/patterns/apl127.htm), consistent across independent copies, **not checked against the printed book**. §9 |
| **WBS 2015** — *Wohnbauten planen, beurteilen und vergleichen*, Bundesamt für Wohnungswesen | Switzerland's official dwelling use-value instrument; 25 criteria, 100 points | **Full 43-page brochure + criteria table**, [bwo.admin.ch](https://www.bwo.admin.ch/de/wohnungs-bewertungs-system-wbs) ([Kriterientabelle](https://www.bwo.admin.ch/dam/de/sd-web/ZBH79VvRtmLn/wbs_kriterientabelle_de_web.pdf), [Broschüre](https://www.bwo.admin.ch/dam/de/sd-web/OylvhDAe-yQv/wbs_2015_broschuere_de.pdf)) |
| **RFP-A** — Zeng, Yin, Gao, Li, Jin & Lu, *Buildings* 15(10):1674, 2025 | The only purpose-built evaluation framework for generated dwellings | **Full PDF extracted locally** after every HTML route 403'd, [mdpi-res.com](https://mdpi-res.com/d_attachment/buildings/buildings-15-01674/article_deploy/buildings-15-01674.pdf) |
| **SSPT** — Jiang & Zhang, 2026-02 | RL post-training with a Hillier–Hanson integration oracle | Full text, [arXiv 2602.22507](https://arxiv.org/abs/2602.22507) |
| **iPLAN** — He, Huang & Wang, CVPR 2022 | `FID_area` / `FID_type` | [arXiv 2203.14412](https://arxiv.org/abs/2203.14412) |
| **Graph2Plan** — SIGGRAPH 2020 · **House-GAN++** — CVPR 2021 · **Architext** · **RLVR** — ACL 2026 · **Ergonomic-loss** — 2026-04 · **VTN** — CVPR 2021 · **Mostafavi et al.** — IJAC 2025 | The generative stack and its metrics | [2004.13204](https://arxiv.org/abs/2004.13204) · [2103.02574](https://arxiv.org/abs/2103.02574) · [2303.07519](https://arxiv.org/abs/2303.07519) · [2605.14117](https://arxiv.org/abs/2605.14117) · [2604.08411](https://arxiv.org/abs/2604.08411) · [2104.02416](https://arxiv.org/abs/2104.02416) · [doi 10.1177/14780771241290649](https://doi.org/10.1177/14780771241290649) |
| **Finch 3D documentation** | The only fully published market scoring function | **Complete corpus**, [`docs.finch3d.com/llms-full.txt`](https://docs.finch3d.com/llms-full.txt), 158 589 bytes, plus the ~90-page index |
| **TestFit knowledge base** | — | **All 274 URLs** from `support.testfit.io` sitemap |
| **Maket.ai**, **Archistar**, **Digital Blue Foam**, **Hypar**, **ARCHITEChTURES**, **Planner5D** | — | Full sitemaps enumerated (126 / 125 / ~66 / 50 URLs); Hypar's repos cloned and grepped; Archistar's Postman collection JSON (158 KB) |
| **Nagy et al.**, *Project Discover*, SimAUD 2017 · **Coorey & Coorey**, ASA 2018 · **Digital Blue Foam**, CAADRIA 2022 & 2023 · **Song et al.**, SUNCG, CVPR 2017 | The four vendor-authored peer-reviewed papers that exist | PDFs downloaded and text-extracted |
| **US11423191**, **US11748527**, **US11409920**, **US11263360** (Autodesk) · **US20220114296A1** (Sidewalk Labs) · **US11009388** (Archistar) | Assigned patents covering layout scoring | **Full claims and full detailed descriptions**, via FreePatentsOnline |
| **`experiments/zoning/out/zoning.json`** | 2 500 committed per-dwelling records: `types`, `classes`, `dist`, `deg`, `n` | Read-only, this machine, 2026-08-30 |

`docs/research/zoning.md`, `docs/spec/proposer.md` §6.1,
`docs/research/floorplan-generation-stack.md` §4.3,
`docs/research/proposer-architecture.md` §7.1,
`docs/research/competitive-landscape.md` and
`data/standards/room-constraints.json` were read as the local framing and are
cited where they already contain the answer.

---

## 2. Q1 — does anybody score against a corpus *distribution*?

### 2.1 The field's distribution term is FID, and it is a black box

Every generative floorplan paper that reports a distribution distance reports
**FID**, computed in a *learned feature space*:

- **House-GAN++** — *realism* is *"an average user rating"*; *diversity* is
  *"the Fréchet Inception Distance (FID)"*; *compatibility* is *"the graph edit
  distance (GED)"* between the input bubble diagram and the graph read back off
  the output. ([arXiv 2103.02574](https://arxiv.org/abs/2103.02574))
- **The RLVR paper** — FID *"compares the feature distributions of generated floor
  plan images and ground truth floor plan images"*. Its two **rewards** are
  connectivity agreement and total-area error; nothing else.
  ([arXiv 2605.14117](https://arxiv.org/abs/2605.14117))
- **Graphic-layout generation**, the literature `proposer-architecture.md` §7.1
  already borrows from, reports **Layout FID, Max IoU, Alignment, Overlap**. VTN
  adds the only genuinely distributional pair — *"the Wasserstein distance
  between real and generated data for two marginal distributions — the class
  distribution (discrete) and the bounding box distribution"* — and is candid
  that it is an approximation: *"A rigorous approach … would be computing the
  Wasserstein distance between the real and learned data distributions.
  Unfortunately this is infeasible."*
  ([arXiv 2104.02416](https://arxiv.org/abs/2104.02416))

⭐ **VTN's `W_class` is the closest published relative of what D10 proposes** — a
Wasserstein distance between generated and real distributions over a **discrete**
support. It is over room *types*, not over a derived relation, but the shape is
the same and the choice of measure is the citable part.

**iPLAN goes furthest toward an interpretable quantity**, reporting two Fréchet
distances over architectural vectors rather than pixels:

> **FID_area** — *"to evaluate the distributional differences of room areas. Each
> layout is represented by a 1×K vector `area_i`, with its k-th element
> `area_i,k` representing the average area of the k-th type of rooms."*
> **FID_type** — *"to calculate the distributional differences of room numbers
> against room types."* — [iPLAN, CVPR 2022](https://arxiv.org/abs/2203.14412)

That is the published precedent for *take a per-dwelling architectural vector,
fit a Gaussian on each side, take a Fréchet distance*. **None of the three
involves the entrance.**

**Architext** has the only optimal-transport term on a named architectural
quantity: *"Spatial diversity compares the total floor area of different types of
spaces within a generated floor plan from the average distribution of respective
types' total floor areas within the training data."*
([arXiv 2303.07519](https://arxiv.org/abs/2303.07519)) — again area, not order,
and the paper states it does not model entrances at all.

### 2.2 The one paper that scores against a real-corpus reference profile uses L1 on medians

**Space Syntax-guided Post-training** ([arXiv 2602.22507](https://arxiv.org/abs/2602.22507),
Jiang & Zhang, 2026-02) is the closest published work to D10's whole idea, and
its scoring function is the finding.

It builds a **Space Syntax Integration Oracle** on the Hillier–Hanson measures —
`MD_i = Σd(i,j)/(n−1)`, `RA_i = 2(MD_i − 1)/(n−2)`, `RRA_i = RA_i / D_n`,
integration `s_i = 1/RRA_i` — reduces each plan to a per-room-type relative
integration profile, and then, verbatim:

> *"To summarize profile alignment against a screened real-data reference
> (RPLAN in our experiments), we report a median profile distance:"*
> `d_profile = (1/|G_eval|) Σ_g |Y_g − Y_g^ref|`
> where `Y_g^ref` is *"the reference median relative profile."*

⭐ **No KL, no EMD, no χ², no Fréchet.** The reference is a **median per group**
and the distance is **mean absolute deviation from it**. If the question is *what
does the state of the art use to score a plan against a real corpus of plans*,
the honest answer is: *an L1 distance to a median, published once, six months ago,
by one group.*

⚠️ **And it does not root depth at the entrance.** SSPT's depth is all-pairs mean
depth *"within each connected component"*, with **no entrance-specific rooting**;
what it optimises is *"public-space dominance and functional hierarchy"*. So even
the paper that does space syntax on generated plans does not compute the quantity
D10 proposes. That is not an argument against D10; it is the reason there is no
scoring function to copy.

### 2.3 ⭐ The one framework purpose-built for this has no distribution term, no entrance, and lists privacy as future work

**RFP-A** — Zeng, Yin, Gao, Li, Jin & Lu, *Buildings* 15(10):1674, 2025 — states
outright that it is the first study to establish evaluation metrics specifically
tailored for generated residential designs. Read first-hand:

**Its four aspects** are *"Room numbers"*, *"spatial connectivity and proximity of
rooms (often shown as a graph, or 'bubble diagram')"*, *"Room locations and
orientations"*, and geometric features — computed as room-number compliance, a
refined GED, room locations in a rotated coordinate system, and geometric
features. **All rule- and graph-based against a paired ground-truth plan.**

Three word-counts over the full text settle the rest:

| term | occurrences in RFP-A |
|---|---:|
| `entrance` / `Entrance` | **0** |
| `zoning` | **0** |
| `Wasserstein`, `KL` | **0** |
| `privacy` | 4, **all in related work or in the limitations** |

⭐ **A paper whose stated purpose is comprehensive, dedicated metrics for
residential plans does not contain the word "entrance" once.** Its limitations
say why:

> *"we aim to expand the scope of requirements in future studies, such as **the
> level of privacy between rooms** and energy efficiency of the residence. … We
> only include **rule-based** methods in designing the current RFP-A, which is
> effective only for well-definable design considerations."*

Its Table 1 gives an independent, citable census of what the field reports —
**FID, GED, IoU, PSNR, SSIM, User Study**, across Graph2Plan, HouseDiffusion,
House-GAN, House-GAN++, Tell2Design, Building-GAN, FloorplanDiffusion, Wang et al.
and Wu et al. That is §2.1's finding, published by somebody else.

### 2.4 ⚠️ The closest prior art is a paper this note could not read

RFP-A's related work, verbatim:

> *"Park et al. evaluated residential floor plans from three perspectives: room
> size, **privacy level**, and room connectivity. They found significant
> differences between the designs of the current generative models and those of
> the human experts **through statistical tests**."*

That is **Park, Ergan & Feng**, *Quality assessment of residential layout designs
generated by relational GANs*, *Automation in Construction* **158** (2024) 105243,
[doi 10.1016/j.autcon.2023.105243](https://doi.org/10.1016/j.autcon.2023.105243)
— the only work found anywhere that scores *generated* plans against
*human-designed* plans on a privacy quantity. Its ScienceDirect abstract states
the two rules of thumb it operationalises: *"1) the shared nature of spaces is
proportional, and 2) **the level of privacy is determined by space allocation**"*,
and reports *"discrepancies in generated versus real floorplans that reveal the
algorithm's partial learning of real data rules."*

⚠️ **UNCONFIRMED — closed access**, and the secondary characterisation is not
trustworthy on its own: RFP-A's citation for *"privacy level"* points at Lu et al.,
*Effect of high-rise residential building layout on the spatial vertical wind
environment in Harbin, China*, *Buildings* 12:705 — a **wind** paper. The citation
trail is broken at the one link that matters.

⭐ **What can be taken regardless:** the statistical machinery RFP-A attributes to
Park et al. is **Mann-Whitney U, descriptive statistics and the χ² test of
independence** (its refs 48–50). Not a divergence. The only published precedent
for *compare a generated population to a real population on a plan property* uses
**hypothesis tests on the raw quantity** — which is what §2.5 prices, including
its over-power problem.

**Someone should buy this paper before the fifth term ships.**

### 2.5 What a three-bucket *ordered* distribution does to each candidate measure

D10 leaves the scoring function open. Computed on the exact corpus distribution
`p = (inv .174, tie .510, ok .316)` against six hypothetical generators, on the
ordered support `inv = −1, tie = 0, ok = +1`:

| generator | TV | EMD | KL(p‖q) | KL(q‖p) | χ², N = 2500 |
|---|---:|---:|---:|---:|---:|
| A — never inverts, always ordered | 0.684 | 0.858 | **∞** | 1.152 | 5411 |
| B — always ties (everything off one hall) | 0.490 | 0.490 | **∞** | 0.673 | 2402 |
| C — matches the corpus exactly | 0.000 | 0.000 | 0.000 | 0.000 | 0.0 |
| D — inverts **twice** as often | **0.174** | **0.348** | 0.132 | 0.128 | 675 |
| E — hall-dominated, few inversions | 0.340 | 0.340 | 0.320 | 0.257 | 1157 |
| F — **never** inverts, corpus tie mass | **0.174** | **0.348** | **∞** | 0.215 | 675 |

1. ⭐ **KL is unusable, and it fails on exactly the case you care about.**
   `KL(p‖q)` is infinite whenever the generator empties a bucket the corpus
   fills — and the bucket a good generator empties is the inverted one. Rows A
   and F. A term whose score is `∞` for *"never produced the defect"* cannot ship.
2. ⭐ **Every symmetric divergence gives rows D and F the same number.** A
   generator that inverts twice as often as real housing and one that never
   inverts score **identically** under TV *and* EMD. For a rate the spec elsewhere
   calls a **violation** that is the wrong behaviour, and no choice among the
   standard divergences fixes it — they are symmetric by construction. The fix is
   a **signed** or **one-sided** statistic, not a better divergence.
3. ⚠️ **χ² is over-powered at this N.** A **2 percentage point** shift already
   exceeds the df = 2, α = 0.05 critical value of 5.99 (χ² = 8.91). Used as a
   hypothesis test the term would report *"significantly different from real
   housing"* for a generator sitting within 2 pp of it. Any use of χ² here must
   quote an **effect size**, never a p-value — the trap `zoning.md` §6.6 avoided
   by reporting an odds ratio beside its χ².

**If a distribution distance is kept, EMD is the right one of the four** — the
only one that respects bucket *order*, so moving mass from `inverted` to `tied`
scores as less wrong than moving it to `ordered`, which is the architectural
truth. It is also what the neighbouring literature picked for a discrete support
(VTN's `W_class`, Architext's spatial diversity). ⚠️ **But it does not solve
defect 2**, and this note does not pretend it does.

### 2.6 ⭐ Space syntax already has the measure this term is reaching for

The trichotomy is not the only way to express *how strongly is the day/night
order expressed in this plan*. Hillier's own answer is the **difference factor**,
and it was invented for exactly the case where the ordering is weak.

Hillier, Hanson & Graham 1987 (UCL Press reprint, p. 292–293), verbatim:

> *"**This particular type of consistency in spatial patterning we call an
> inequality genotype. We believe it to be one of the most general means by which
> culture is built into spatial layout.** How strong or weak these inequalities
> are in a complex, or in a sample, is therefore also of importance. To measure
> this, we have developed an entropy-based measure called **difference factor** to
> quantify the degree of difference between the integration values of any three
> (or more…) spaces or functions."*

`H = −Σ (a_i/t)·ln(a_i/t)`, relativised as **`H* = (H − ln2)/(ln3 − ln2)`**,
running **0** for maximum difference to **1** for all values equal. Their own
worked examples: *"the difference factor for, for example, 0.4, 0.5 and 0.6 is
0.97 (that is, close to 1 or very weak), whereas that for 0.3, 0.5 and 0.7 is
0.84 … and that for 0.1, 0.5 and 0.9 is 0.39, or much stronger still."*

⭐ **Three properties make this the better instrument for §6.1:**

1. **It is continuous.** A plan whose social and private minima differ by a hop
   and a plan where they differ by three hops are different numbers, not the same
   bucket. The trichotomy throws that away by construction.
2. **It does not manufacture a tie bucket.** §7 shows 51.0 % of the corpus is a
   tie *because the quantity is integer-valued with an effective range of two*.
   `H*` over integration values has no such degeneracy — which is precisely the
   problem §6 and §7 identify.
3. **It is one number per dwelling**, so the corpus target is a *distribution of
   `H*`* and the natural comparison is a distribution distance over a continuous
   support — where FID/Fréchet and Wasserstein both behave, and where §2.5's KL
   catastrophe cannot happen.

⚠️ **It is not free.** `H*` is defined over **integration** (all-pairs RRA), not
entrance depth, so it measures a *different* property — the one SSPT already
optimises (§2.2) — and it needs RRA, which needs the D-value normalisation §6.2
discusses. **Adopting it would be a different fifth term, not a rescoring of this
one**, and the note records it as an option rather than a recommendation. But
`proposer.md` §6.1 should not adopt a trichotomy without recording that the
discipline that owns this quantity rejected trichotomies forty years ago.

### 2.7 ⚠️ Matching a *defect* rate is not the same decision as matching a typology

This is the finding that is not a repair.

`zoning.md` §6.5's table labels the − bucket **"violation"**. D10 then asks for
the rate to be **matched**: *"scored against the corpus rate rather than a
threshold"*. Those are two different objectives:

- **Match** is right for the four terms §6.1 already ships. Sleeping-group count
  (69.8 / 27.7 / 2.5) is a **typological fact** — a generator that produces one
  group every time is not better than real housing, it is narrower than real
  housing, and the distribution is the whole point.
- **Minimise** is what you want from a defect. If 17.4 % of Swiss dwellings put a
  bedroom nearer the door than the living room, a generator that does it 5 % of
  the time is **better**, and a matching score penalises it.

The generative-metrics literature has this critique in its own terms: a single
distribution distance conflates fidelity with coverage and cannot say *which way*
a model differs, which is why the field split it into precision and recall
(Kynkäänniemi, Karras, Laine, Lehtinen & Aila,
[arXiv 1904.06991](https://arxiv.org/abs/1904.06991), NeurIPS 2019; Naeem et al.,
[arXiv 2002.09797](https://arxiv.org/abs/2002.09797), ICML 2020).

**The spec has to pick one.** Either the inversion is a defect — the term is
**one-sided** with the corpus rate as a *ceiling*, and §6.5's word "violation"
stands — or it is a typological fact like the other four, and the word "violation"
has to come out of §6.5 and a generator that never inverts has to be marked down.
⚠️ **Do not ship the term with both readings in the file**, which is what a
straight transcription of D10 would do.

### 2.8 The market and the one official instrument: points against a table

The market half of this question is §3.5, with its search record. The finding
that belongs here is the **non-vendor** one, because it is the strongest evidence
available and it is about the same country as the corpus.

**WBS 2015** — Bundesamt für Wohnungswesen — is Switzerland's official instrument
for assessing dwellings, in continuous use since the 1974 WEG as the basis for
federal housing support. Its methodology, verbatim:

> *"Jedes Kriterium erhält aufgrund der Beurteilung von Quantität oder Potenzial,
> Qualität und Innovation zwischen **0 und maximal 4 Punkte**. Insgesamt können
> 100 Punkte erreicht werden."*
> *"Die Quantität wird anhand einer **Tabelle** beurteilt … Die Qualität wird
> anhand **präzise beschriebener Merkmale** beurteilt."*

⭐ **Points against a lookup table and a checklist of stated features. Not a
distribution, not a divergence, not a corpus.** The only official instrument that
scores the exact population Swiss Dwellings is drawn from does the thing D10
declines to do — and does it because a criterion has to be *explicable to an
applicant*, which is the property a Homeowner-facing engine also needs.

**So there is no precedent anywhere for corpus-distribution scoring of a named
plan property, in research or in practice.** §6.1's framing is genuinely novel,
and novel instruments need their scoring function written down rather than implied.

---

## 3. Q2, part one — is the quantity named, and does anyone encode it?

### 3.1 ⭐ Space syntax names every ingredient and not the compound — and the obvious name is taken

The primitives all exist and are all quotable:

- **Depth**, verbatim (Hillier, Hanson & Graham 1987, reprint p. 290–291):
  *"A space is at depth 1 from another if it is directly accessible to it, at
  depth 2 if it is necessary to pass through one intervening space … In the
  justified graphs, therefore, depth from one space to another will show as
  height when the first space is used as the root."*
- **The justified graph and its root**: *"a graph in which a particular space is
  selected as the 'root', and the spaces in the graph are then aligned above it in
  levels according to how many spaces one must pass through to arrive at each
  space from the root."*
- **The carrier** — Ostwald 2011, p. 449: *"The carrier node, **often the outside
  world**, is located on the lowest line on the chart (line 0)."* Amorim's method:
  *"the exterior (public space) taken as its root … **depth from the exterior**,
  expressing the topological distance which visitors and inhabitants face while
  approaching the system."*
- **Step depth** — Bartlett/UCL training platform: *"Step depth … follows the
  shortest path from the selected root line (or segment) to all other lines … and
  the path length is recorded on the line."*
  ([spacesyntax.online](https://www.spacesyntax.online/term/step-depth/))
- **The inequality genotype** — the *ordering* itself, §2.6, measured with `H*`.
- **The sectors' genotype** — Amorim writes it as `s = se < p`, §4.2.

⭐ **But there is no term for "nearest-private-versus-nearest-social depth from
the entrance."** The discipline that owns this quantity has never formed it. That
makes `entry-depth inversion` a new name, which is fine — with one warning:

⚠️ **"Inverted genotype" is already a Hillier & Hanson term and it means something
else entirely** ([spacesyntax.online](https://www.spacesyntax.online/term/inverted-genotype/)).
Do not write *"inverted genotype"* anywhere in `proposer.md` or `rules.json`.
`entry_depth_inversion` does not collide; `zone.inverted_genotype` would.

### 3.2 Nobody in the generative stack roots depth at the entrance, and the reason is structural

`zoning.md` §6.7 found this for *constraints* and predicted it would hold for
evaluation. It does, and the mechanism is sharper than "nobody thought of it":
**the entrance is an input in every pipeline that has one at all.**

- **Graph2Plan** takes the front door as part of the boundary encoding, following
  RPLAN: *"The input boundary is represented as a 128×128 image with three binary
  channels … These masks capture the pixels that are inside the boundary, on the
  boundary, and **on the entrance doors**."* Its limitations: *"the graphs do not
  model accessibility criteria or functionality considerations."*
- **House-GAN++** types a door to `"outside"` — *"not an actual room but used for
  defining front doors"* — as a **given** in the input graph.
- **SSPT** computes all-pairs mean depth with no entrance root (§2.2).
- **The ergonomic-loss paper** is the only one with an explicit entrance term, and
  it is a **distance**, not a depth: `L_entrance` is the distance from the
  entrance room polygon to the front door polygon. ⭐ **And its `L_kitchens` term
  pulls the kitchen *toward* the entrance** — *"average distance from kitchens to
  assigned **entrance** and dining rooms"*. Nothing is scored *away* from the door.

⭐ **So the entry-depth quantity is not a gap somebody forgot — it is a quantity
the field's problem formulation makes unavailable.** When the user hands you the
bubble diagram and the door, privacy depth is conditioning. This engine's Brief
does *not* carry an access graph, which is why the quantity exists here and not
there. **That is a real argument for D10 and it should be recorded as one.**

⚠️ **UNCONFIRMED:** the RPLAN paper itself (Wu, Fu, Tang, Wang, Qi & Liu,
*ACM TOG* 38(6), 2019) was **not read first-hand** — the USTC project page refused
connection and the ACM DL entry is paywalled. Its front-door input is asserted
here only through Graph2Plan's verbatim description of it.

### 3.3 ⭐ Alexander wrote the metric in prose in 1977

**Pattern 129, Common Areas at the Heart**, characteristic 2, verbatim:

> *"Most important of all, **it must be 'on the way' from the entrance to private
> rooms, so people always go by it on the way in and out of the building.** It is
> crucial that it not be a dead-end room which one would have to go out of one's
> way to get to."*

That is entry-depth ordering stated as a design requirement, twenty years before
space syntax formalised the measurement. **It is the design-theoretic warrant for
the term and `proposer.md` should cite it.**

⚠️ **With one qualification that cuts against a naive reading**, from the same
pattern: *"if the circulation path cuts too deeply through the common area, the
space will be too exposed … **The only balanced situation is the one where a
common path, which people use every day, runs tangent to the common areas and is
open to them in passing.**"* Alexander wants the social room **beside** the path,
not **on** it. `zone.no_social_transit` (term 3) already encodes the second half
of that; the entry-depth term encodes the first. ⭐ **Read together, Alexander is
saying the two terms are one requirement with two failure modes** — which is a
better account of `zoning.md` §6.6's finding that they are *negatively* associated
than "they are different properties" was.

### 3.4 ⭐ Space syntax's own dwelling result: private is deepest, and it is stated both as a measurement and as a rule

Amorim 1997 — *"a sample composed of **140 houses, built between 1950 and 1970**,
selected from a larger sample of 250 modern houses"* in Recife, Brazil — reports
the depth finding directly, §4.3, verbatim:

> *"**Social and service sectors are the shallowest functional sectors in every
> graph (depth 1 and 2). They are also at the same distance from the visitor's
> viewpoint**, with the exception of type 22 …"*
> *"**The private sector is the deepest one, always positioned at the top of the
> graph.** Access to bedrooms is highly controlled…"*
> *"Summing up, the sample shows a consistent depth pattern. **Access is allowed
> through social and service sectors, then movement is distributed and controlled
> by mediator spaces, and private sector is the deepest element of all.**"*

⭐ **That is the closest published corroboration that the gradient is real** — a
different continent, a different decade, a hand-drawn convex map rather than a
machine-derived contact graph.

And Amorim states it **normatively** too, as design rule 2 of his conclusion:

> *"**Private sector as occupational space. Private sectors must be the deepest
> sector in the house. Bedrooms, as spatial units for resting, sleeping or
> studying**, just to refer to some private activities, **must be the most secluded
> elements. They must be dead-end spaces (a-type space) or included in a ring
> (c-type space)**, allowing secluded access to the servants, when required."*

⭐ **`zoning.md` D10's term is Amorim's rule 2, measured.** That is the citation
`proposer.md` §6.1 needs and does not have — and note that the rule couples
*depth* with *space type*, which is what §5.4 tests.

⚠️ **Do not quote his genotype percentages as if they were entry-depth rates.**
His two genotypes — **`s = se < p`** in **57.85 %** of the sample and
**`s < se < p`** in **34.28 %**, with 3 phenotypes covering the remaining 7.85 % —
are **rank orders of RRA integration**, not of depth from the entrance: *"Table 5
shows the rank order of integration of all sectors, ordering the RRA values"*. The
depth finding above is separate, and it is qualitative (*"every graph"*,
*"always"*) rather than a rate. **Same direction as §6.5's, incomparable
denominators, different measure.**

### 3.5 ⭐ The market — nine products and the whole patent corpus, and the answer is unanimous

`docs/research/competitive-landscape.md` (2026-08-17) already establishes the
product-level facts from primary vendor documentation and is not re-derived here.
What follows is specific to **evaluation methodology**, and §9 carries the full
search record — every dead domain, every 404, every corpus read to the end.

**Nothing in the market scores a plan against a corpus distribution.** Every
published mechanism is a threshold, a signed difference from a target, a hand-set
weight, a codified regulation, a Pareto sort, or a human rubric.

| product | mechanism | character |
|---|---|---|
| **Finch 3D** | Weighted sum behind hard pre-filters | user-set slider weights + "non-negotiables" |
| **TestFit** | Min/max solve filters | thresholds only; **no published score** |
| **Autodesk Forma / Spacemaker** | Pareto dominance (MOGA) in the research; additive penalty sum in the open source; **"weighted sum" in the patent claim** | no corpus anywhere |
| **Digital Blue Foam** | Isochrone-bucketed category counts; Simpson's index | 5-/15-min threshold + hand weights |
| **Archistar** | Rule gate then user-chosen sort key | *"deterministic, rule-based logic"* |
| **Maket.ai** | Hand-authored adjacency rules + LLM + repair pass | *"a set of predefined architectural rules"* |
| **ARCHITEChTURES** | Signed difference from target | user-editable colour thresholds |
| **Planner5D** | Nothing published; API returns areas and counts | — |
| **Hypar** | Target-vs-actual deviation % | **no objective function at all** |

**Finch is the best-documented and its scoring function is published in full**,
including a worked example
([docs.finch3d.com, algorithm theory](https://docs.finch3d.com/docs/projects-and-variants/story-editor/algorithm-theory)):

> *"Each iteration is scored for how well it hits certain metrics after inputting
> 'non-negotiable' variables. Non-negotiables are requirements applied right out of
> the gate before the scoring takes affect, such as **circulation entrance
> access**, minimum width, and stairwell count. After hitting the non-negotiables,
> the user can then influence the direction that the algorithm iterates. **By
> changing the weights, the user can tell the algorithm what is important and what
> is less so.**"*

⚠️ **Note where the entrance appears: as a binary connectivity non-negotiable.**
Finch matches apartment entrances to corridor spaces and lets the user pick the
entrance wall. **Nothing measures depth from it.** And a grep of Finch's complete
public documentation corpus (`llms-full.txt`, 158 589 bytes) returns **zero
occurrences** of `study`, `home office`, `den`, `workspace` or `social`;
`privacy`/`private` occurs only in the data-protection sense.

**Autodesk's research is the one place a weight-free aggregation appears**, and it
still has no corpus. *Project Discover* (Nagy et al., SimAUD 2017) uses six
objectives — adjacency preference, work-style preference, buzz, productivity,
daylight, views — and states: *"**the user does not need to prioritize or weight
the individual metrics beforehand.** This is because the MOGA determines relative
performance based on the idea of **dominance** rather than the absolute difference
in metric values."* It is an office model. **Spacemaker's own open-source
objective function** (`spacemakerai/space-planning-calculator`,
`src/objectiveFunction.ts`) is an additive penalty sum whose land-utilisation term
is literally `-Math.abs(ratio - target)` — a signed distance from a user-set
number.

### 3.6 ⭐ The patents say "weighted sum" in the claim language, and contain no entry node

Full claim text was obtained for the relevant families. The results are blunt:

> **US11423191 (Autodesk), claim 18:** *"wherein the step of generating the fitness
> metric for the first candidate design comprises computing a **weighted sum** of a
> subset of metrics included in the first set of metrics."*
> **US20220114296A1 (Sidewalk Labs / Alphabet, "Delve"), claim 1:** the layout score
> *"combines a lighting sub-score … a view sub-score … and a distance sub-score"*
> into a *"**cumulative layout score**"*; the spec adds *"a **weighted average** of
> the sub-scores"* and converges when the change is *"**less than a predetermined
> threshold value**"*.

Divergence searches over patent full text: `"floor plan" AND "earth mover"` → **0**;
`"floor plan" AND "Kullback"` → 40, none about layout; `"building layout" AND
"divergence"` → 13, none relevant; **`"space syntax"` → 0 across US, EP and PCT.**

⚠️ **A terminology trap worth naming in the spec.** In the Autodesk family
**"circulation" means traffic-crossing density, not depth from an entrance**:
*"Work style evaluator 224 computes **the number of intersections between paths**
… then combines the number of intersections with the computed path lengths to
generate a circulation metric."* And the layout graph has no room nodes at all —
*"**Each node of the graph represents a location where a potential occupant may be
stationary** for some amount of time."* **A reader who sees "circulation metric" in
prior art will assume entry-depth prior art exists. It does not.** The word
*entrance* appears **zero** times in US11423191, US11263360 and US12204821.

⭐ **And the kitchen, in the patents, is an amenity ranked by individual
preference** — *"a desired proximity to different amenities, **such as a kitchen or
bathroom**"*; *"those fixtures may include **a kitchen, a lounge, a coffee bar, a
bathroom, a private office, a conference room, a workstation**"*. There is no
social set for it to belong to. `"floor plan" AND "private zone" AND "public zone"`
→ **0**.

⚠️ **One correction that touches this repo's own competitive note.** No patent is
findable under **Finch**, **Spacemaker AS**, **TestFit**, **Maket** or **Higharc**,
by assignee or by named inventor — yet Finch's press coverage (Dezeen 2019, AEC
Magazine) reports *"patented graph technology"*. `competitive-landscape.md` does
not repeat that claim and **should not start**. ⚠️ **UNCONFIRMED as a negative**:
the zeros are confirmed against FreePatentsOnline's index, not Google's
assignee-normalised one, and Google Patents was blocked throughout (§9).

### 3.7 ⭐ Exactly one product publishes a public/private set — and it puts the kitchen in the *public* one

**Maket.ai** is the only vendor in the survey that states an entry-depth rule at
all, and it states it twice, independently, on the same page — its **company blog**,
not its documentation, because Maket publishes no documentation
([maket.ai/blog/ai-floor-plan-generator-guide-2026](https://www.maket.ai/blog/ai-floor-plan-generator-guide-2026)):

> *"Room placement is not random. Maket applies **adjacency rules drawn from
> architectural standards: bedrooms are grouped together and kept away from the
> entrance, common areas like the living room and kitchen sit close to the front
> door**…"*
> *"compare how each layout handles traffic flow, natural light, and **the
> separation between public spaces (living room, kitchen, dining) and private ones
> (bedrooms, bathrooms)**."*

⭐ **That is a third position on the kitchen question, and it sides with
Alexander** (§4.1) against Amorim and SSPT. ⚠️ **And it is the weakest source in
this note** — a marketing blog post, a hand-written placement rule, no measure, no
step count, no graph, and the mechanism it describes is *"a set of predefined
architectural rules"* handed to a frontier LLM with *"a proprietary post-processing
layer"* to correct mistakes. It is quoted because it is the only vendor answer that
exists, **not because it is good evidence.**

⭐ **And Maket names the study and then drops it.** Its own input list includes
*"any specific rooms like **a home office** or mudroom"* — and the home office
appears in **neither** the public list nor the private list on the same page.
**That is the sharpest published statement of the §5 gap found anywhere**: the one
vendor that partitions rooms by privacy declines to place the study.

Everyone else does not partition at all. **ARCHITEChTURES** publishes exactly two
adjacency heuristics and both are ventilation, not depth — *"the ventilation of the
kitchen to the facade or the central position of the living room as an element
separating bedrooms"*, and *"the possibility of interior kitchen"* — with the
entrance appearing only as a regulatory minimum width. **Hypar** declares an
adjacency graph schema (`{From, To, Weight}`) and **no solver reads it**; its
`TravelDistanceAnalyzer`, the closest entry-depth analogue in the market, is a
**visualiser with `outputs: []`**. **TestFit** has no room-level model — units are
bedroom counts, the entrance is a *Left/Center/Right* wall parameter. **Planner5D**
has published no papers at all; its user designs became **SUNCG**, whose 24 room
types include `office`, `hall` and `entryway` as flat sibling labels with no
relationship encoded and a **binary human majority vote** as the quality gate.

⚠️ **One near-miss worth recording.** The one KL divergence in the Planner5D
lineage is Ritchie, Wang & Lin (CVPR 2019, [arXiv 1811.12463](https://arxiv.org/abs/1811.12463)),
which reports *"Kullback-Leibler divergence `D_KL(P_synth‖P_dataset)` between the
category distribution of synthesized scenes and that of the training set"* — but
that is **KL over furniture categories inside a room**, not over room positions or
entrance depth. It is the nearest thing in the whole survey to what D10 proposes,
and it is a different object.

### 3.8 ⭐ Nobody normalises for size — and the two who do are academic, and both are copyable

**Zero of nine products and zero patents acknowledge that a layout metric can be
confounded by size or room count.** The only normalisation in the entire patent
corpus divides by **path count**: *"normalizes the accumulated path lengths based
on the number of shortest paths"* (US11423191). Sidewalk Labs offers only
*"sub-scores can be normalized in any suitable manner."*

⭐ **The academic literature has already solved this two ways, and House-GAN++'s
way is the one §6.2 recommends — it is a published protocol, not an invention of
this note:**

> **House-GAN++ never reports a pooled FID.** *"we use the k-fold cross validation
> … **dividing the samples into four groups based on the number of rooms:
> (5, 6, 7, 8)**"*. The same stratification is used in the Mila RLVR paper.

> **SSPT states the prevalence-bias problem outright** and fixes it by weighting:
> *"Different functional room types do not appear with equal frequency;
> consequently, **a direct comparison based solely on average relative integration
> may be biased by rare room types with unstable statistics.**"* → Coverage-Weighted
> Relative Integration, `CWRI_r = mean(RI_r) × ω_r`.

**So §6.2's recommendation — report per room-count bucket — is exactly what the
strongest generative-floorplan benchmark in the field already does**, and citing
House-GAN++ for it costs nothing.

---

## 4. Q2, part two — where the kitchen goes, and what it costs

### 4.1 ⚠️ The two canonical traditions disagree, and both are canonical

**Alexander puts the kitchen on the public side.** Pattern 127, Intimacy
Gradient, the ordering sentence, verbatim:

> *"In any building — house, office, public building, summer cottage — people need
> a gradient of settings, which have different degrees of intimacy. **A bedroom or
> boudoir is most intimate; a back sitting room or study less so; a common area or
> kitchen more public still; a front porch or entrance room most public of all.**"*

and the explicit house sequence: *"**In a house: gate, outdoor porch, entrance,
sitting wall, common space and kitchen, private garden, bed alcoves.**"*

Pattern 129 requires it: *"It must have the right components in it — **usually a
kitchen and eating space, since eating is one of the most communal of
activities**."* Pattern 139, Farmhouse Kitchen, is an entire pattern arguing the
point, with the historical account: *"**The isolated kitchen, separate from the
family and considered as an efficient but unpleasant factory for food is a
hangover from the days of servants**; and from the more recent days when women
willingly took over the servants' role."*

**Space syntax puts the kitchen in a third category.** Amorim 1997, §1:

> *"lecturers and professors at Recife assumed the idea of a **three sector
> system, composed by the social, service and private zones**. **The Social sector
> groups the spaces that allow for continuous interaction among the inhabitants
> and, fundamentally, the inhabitants and visitors — living, receiving and dining
> areas. The Private sector assures the necessary seclusion of the family and its
> members — bedrooms and study room. The Service sector houses the activities
> related to the reproduction and maintenance of a dwelling's life — kitchen,
> larder and servants' accommodation.**"*

**SSPT** agrees with Amorim: *"Service/Wet (**Kitchen** + Bathroom + Laundry)"*,
and *"Service spaces — including kitchens, bathrooms, storage rooms … are even
more segregated."* **WBS** (§5.2) is more radical still and has no social/private
axis at all.

⭐ **The disagreement is smaller than it looks, and the part that survives is the
part that matters.** Both traditions predict the kitchen is **shallow** — Amorim
measures social and service *"at the same distance from the visitor's viewpoint"*.
They differ on **what a violation means**, not on where the kitchen sits. And on
the English house the two converge: Hillier, Hanson & Peponis 1984 report the
genotype *"the parlour (P) integrates least, the main living area (L) most, and
**the kitchen (K) lies in between**"* — the kitchen is intermediate, which is
neither tradition's pure reading.

⚠️ **This corrects a claim an earlier draft of this note made.** It is **not**
true that every primary source puts the kitchen on the service side. Alexander,
who is the source of the gradient itself, puts it on the public side in the same
sentence in which he defines the gradient.

**What the engine should do:** the engine's social set is
`LIVING_ROOM / LIVING_DINING / DINING` and its private set is bedrooms plus study.
⭐ **That is Amorim's `Social` and `Private` sectors verbatim, and Amorim is a free,
primary, citable Space Syntax Symposium source.** The choice is defensible, it is
published, and `proposer.md` should cite it rather than deriving it. But the spec
should say *which* tradition it follows, because Alexander's reading would move
the number by 2.7 points (§4.3).

### 4.2 ⭐ The one taxonomy that matches the engine exactly

To make the alignment explicit, since it settles both contested choices at once:

| engine class | Amorim 1997 sector | membership |
|---|---|---|
| `social` | **Social** | *"living, receiving and dining areas"* |
| `private` (`is_sleeping`) | **Private** | *"**bedrooms and study room**"* |
| `kitchen`, `wet` | **Service** | *"kitchen, larder and servants' accommodation"* |
| `circ` | **Mediator** | *"a metatransitional unit, called Mediator sector or space, is introduced"* |

⭐ **`is_sleeping` including `study` is Amorim's Private sector, exactly**, and his
rule set states it twice: *"**Bedrooms, as spatial units for resting, sleeping or
studying** … must be the most secluded elements."* ⚠️ **This is a strong
membership citation and it is not a placement citation** — §5 shows why the two
come apart for a study specifically.

### 4.3 ⭐ The social-set definition moves the headline by up to 7.1 points

Recomputed read-only over the same 2 500 committed records, varying only the
definition of the social set:

| social set | n | inverted | tied | ordered |
|---|---:|---:|---:|---:|
| **(a) `LIVING_ROOM`, `LIVING_DINING`, `DINING`** — what §6.5 measured; Amorim's Social | 1 756 | **17.4 %** | 51.0 % | 31.6 % |
| **(b) (a) ∪ `KITCHEN`** — Alexander's reading | **2 488** | **14.7 %** | 57.4 % | 27.9 % |
| **(c) `KITCHEN` counts only where no social Room exists** | **2 488** | **21.8 %** | 51.6 % | 26.6 % |

Two facts sit under that table and both matter more than the spread:

⭐ **29.8 % of the corpus (744 of 2 500) has no social Room at all**, and 732 of
those 744 have a kitchen. The term as measured is **undefined on nearly a third of
real Swiss dwellings**, and the choice of what to do about them moves the
denominator from 1 756 to 2 488 — a **42 % change in sample**. Reading (b) is not
a rounding difference from (a); it scores a different and much larger population.

**And the kitchen is not reliably on either side.** Over the 1 756 dwellings
holding both: the kitchen sits **further** from the entrance than the nearest
social Room in 47.0 %, **ties** in 38.0 %, and sits **nearer** in 15.0 %. Adding
it to the social set does not pull the social boundary systematically inward or
outward — it *dilutes* the contrast, which is why (b) drops the inversion rate and
raises the tie rate together.

⚠️ **Note what that measurement does to Amorim's rule 1**, which is the normative
half of §3.4: *"**Social and service sectors as movement generators. Social and
service sectors must be part of a movement generator system (d-system), globally
integrating the house, being equidistant from the street.**"* Amorim's model says
the kitchen and the living room should be **equidistant from the entrance**, and
his Recife measurement finds them so — *"at the same distance from the visitor's
viewpoint"*. **The Swiss corpus does not follow that rule**: only 38.0 % tie, and
the kitchen is further in 47.0 %. ⭐ **So the one place the two traditions agreed
is the one place the corpus disagrees with both**, which is a genuine regional
finding and not an artefact of the class map. It also means reading (b) is not a
neutral relabelling: it merges two sets the corpus keeps apart.

⚠️ **The headline 17.4 % is therefore not a property of the corpus. It is a
property of a room-classification decision the spec has not written down.**
Whichever reading ships, `proposer.md` §6.1 must name the social set in the same
sentence as the number, the way §6.1 already names the sleeping set for term 1.

### 4.4 ⚠️ The engine's stated intent and its own measurement disagree about `KITCHEN_DINING`

`measure_zoning.py`'s class map, read first-hand:

```
for _t in ("BEDROOM", "ROOM"):                              CLASS[_t] = "private"
for _t in ("LIVING_ROOM", "LIVING_DINING", "DINING"):        CLASS[_t] = "social"
for _t in ("KITCHEN",):                                      CLASS[_t] = "kitchen"
```

There is **no entry for `KITCHEN_DINING`**, so `cls()` returns its default and the
corpus's `KITCHEN_DINING` rooms are classed `"other"` — neither social nor
kitchen. The engine's intent is that open-plan kitchen-dining types **count as
social**.

**Numerically it does not matter here** — there are **3** `KITCHEN_DINING` rooms
in 2 500 dwellings (the ten labels present are `ROOM` 4 765, `BATHROOM` 3 715,
`CORRIDOR` 2 811, `KITCHEN` 2 488, `LIVING_DINING` 1 300, `BEDROOM` 1 225,
`STOREROOM` 574, `LIVING_ROOM` 441, `DINING` 71, `KITCHEN_DINING` 3).
**Structurally it matters a lot**, for two reasons:

1. The number 17.4 % is offered as the calibration target for a rule that would
   classify `kitchen_dining` differently from how the number was measured. The
   mismatch is 3 rooms wide today and a whole region wide tomorrow —
   `room-constraints.json` ships `kitchen_dining` as a first-class type with its
   own gas note, and `az-market-default-against-practice.md` §6.4 measures the
   Baku open-plan room at ≈18 m².
2. `STOREROOM` (574 rooms) also falls to `"other"`, which is correct, and
   silently. ⚠️ **A map that returns a default for anything it has not heard of
   will absorb the next corpus's vocabulary without a word. It should fail
   loudly**, the way `gate_check.py` already gates flag divergence.

⚠️ **And the open-plan / separate split is itself a 1.8× effect on the headline:**

| dwelling type | n | inverted | tied | ordered |
|---|---:|---:|---:|---:|
| `LIVING_DINING` only (open plan) | 1 299 | **14.4 %** | 53.0 % | 32.6 % |
| `LIVING_ROOM` / `DINING` only (separate rooms) | 439 | **25.7 %** | 45.3 % | 28.9 % |

A Brief asking for a separate living room and a separate dining room would be
scored against a 17.4 % target three-quarters made of open-plan dwellings. §6's
mixture argument in a second dimension.

---

## 5. Q3 — the study / home office

### 5.1 ⭐ The corpus cannot see a study, and the repo already knows it

The ten labels in the 2 500-dwelling sample (§4.4) contain **no `STUDY`, no
`OFFICE` and no `STUDIO`**. `measure_zoning.py`'s private class is
`{BEDROOM, ROOM}`, and of the private rooms **70.1 % are the unlabelled `ROOM`**
and 29.9 % are `BEDROOM`.

The direct test was run — is an inversion disproportionately caused by a generic
`ROOM` (which might be a study, den or office) rather than a labelled `BEDROOM`?
It comes back **negative**:

| outcome | n | share `ROOM` | share `BEDROOM` |
|---|---:|---:|---:|
| private-set base rate | 5 990 | 70.1 % | 29.9 % |
| **inverted** | 305 | 71.8 % | 28.2 % |
| tied | 896 | 69.1 % | 30.9 % |
| ordered | 555 | 69.2 % | 30.8 % |

⭐ **No signal, in either direction.** The three rows are the base rate. **The
study case is unmeasured on this corpus and cannot be measured on it**, because
the label that would separate the two does not exist.

⭐ **`room-constraints.json` already ships that admission**, in
`weakest_cells_note`:

> *"Swiss Dwellings carries no label for these, so they are derived and
> **UNFALSIFIED**. **study is the weakest number in the file**: a one-desk
> programme with no corpus to check it against and no source that states a study
> minimum."*

⚠️ **So `zoning.md` §5b's `is_sleeping` would put `study` in the private set, and
§6.5's 17.4 % was measured on a private set in which a study is invisible.** The
one Room type the rule newly captures is the one type the calibrating measurement
could not see.

### 5.2 ⭐ Alexander contradicts himself, and the contradiction is exactly this case

**Pattern 127** puts the study on the private side: *"A bedroom or boudoir is most
intimate; **a back sitting room or study less so**."* **Pattern 141, A Room of
One's Own**, is emphatic: *"**place these rooms at the far ends of the intimacy
gradient — far from the common rooms**"*, and it names the type: *"In older
houses, the man of the house usually had **a study or a workshop of his own**."*

**Pattern 157, Home Workshop**, says the opposite for the same room:

> *"**the home workshop becomes far more than a basement or a garage hobby shop.
> It becomes an integral part of every house … And we believe its most important
> characteristic is its relationship to the public street. For most of us, work
> life is relatively public.**"*
> *"**Make a place in the home, where substantial work can be done; not just a
> hobby, but a job. … and locate it so it can be seen from the street and the
> owner can hang out a shingle.**"*

And 141 cross-references 157 as a way of *providing* the room of one's own —
*"it may be … **a home workshop — Home Workshop (157)**"*.

⭐ **So the single most-cited authority on the privacy gradient places the same
room type at both ends of it, in two patterns that reference each other.** The
contradiction is in the source, not in the engine. Alexander's own five-band
operationalisation (**Pattern 142, Sequence of Sitting Spaces**) splits the
difference and puts a work room one band shallower than a bedroom:

1. outside the entrance · 2. inside the entrance · 3. **common rooms** (incl.
Farmhouse Kitchen 139) · 4. **half-private rooms** (incl. **Half-Private Office
152**) · 5. **private rooms** (incl. A Room of One's Own 141)

⚠️ **A binary private/social split cannot represent that**, and the engine's
proposed term is binary.

### 5.3 ⚠️ And the space-syntax literature has seen this signal and called it *richer*

Hanson, *Decoding Homes and Houses* (1998), ch. 10, reporting Monteiro's study of
middle-class Recife houses:

> *"in marked contrast to the previous cases, **some private needs also occur
> quite shallow in the home, a factor which was explained by the existence of a
> separate library, office, or 'best' room at the front of the house which combine
> the properties of being manifested to the exterior and quite shallow in the
> house with being relatively segregated.** Monteiro concluded that '**the pattern
> of domestic activity in this case shows a more flexible use of space and a more
> heterogeneous and rich disposition of space functions**'."*

⭐ **That is the entry-depth inversion signal, observed, and the verdict is
"flexible" and "rich" — not "defect."** The resolution Hanson offers is that the
front office is **shallow but segregated**: few onward connections, on no ring, so
it does not compromise the private zone even though it sits by the door.

**The historical precedent is the parlour**, and it comes with a warning the
engine should hear. Hanson, ch. 2, on the English terraced house:

> *"**The space which is invariably the most segregated is the parlour, in spite of
> this room's being next to the front door and at the front of the house.**"*
> *"in the untransformed home there is likely to be **one special room, the front
> room on the ground floor facing the street, which does not form part of the
> everyday living accommodation**."*

⚠️ **Geometric frontness is not topological shallowness.** The parlour is at the
street facade and is still the deepest room in the house. The engine's graph is
built from **contact**, not facade, so it gets this right — but any future term
that reaches for "which room is on the entrance elevation" would get it exactly
backwards, and the canon says so.

### 5.4 ⭐ The benign explanation was tested on this corpus, and it does not hold

Amorim's space-type vocabulary (after Hillier 1996) gives the discriminator:
*"**Space 7 is called a-type space. Its relative position does not allow through
movement and for that reason privileges functional occupation rather than
movement.**"* A shallow **terminal** private room is the Monteiro/Alexander-157
front-office pattern; a shallow private room **on a route** is the defect.

`zoning.json` records `deg` per room, so the test runs read-only. Degree of the
**nearest private room** in the contact graph:

| outcome | n | **deg 1 (terminal)** | deg 2 | deg 3 | deg 4+ |
|---|---:|---:|---:|---:|---:|
| **inverted** | 305 | **4.9 %** | 50.8 % | 43.3 % | 1.0 % |
| tied | 896 | 5.0 % | 46.9 % | 46.2 % | 1.9 % |
| **ordered** | 555 | **26.5 %** | 47.7 % | 24.7 % | 1.1 % |
| all private rooms | 3 869 | 17.9 % | 50.5 % | 30.7 % | 1.0 % |

Tightening to the full front-office signature — terminal **and** entered off
circulation only — gives **4.6 %** of inverted dwellings, **4.4 %** of tied and
**0.2 %** of ordered.

⭐ **The result is the opposite of the hypothesis, by a factor of five.** The
shallow private room in an inversion is a *well-connected* room — degree 2 or 3 in
94 % of cases — not a ringless terminal cell. Under 5 % of the corpus's inversions
have the front-office structure Monteiro described. **The 17.4 % is bedrooms off
the hall, not studies off the hall.**

⭐ **This is the finding that argues *for* the term.** It removes the strongest
available benign explanation for the corpus rate, on the corpus's own data. A note
that had only found reasons to doubt would be the less trustworthy note.

⚠️ **Two honest caveats.** Contact ⊇ realised doors, so contact degree
**over-counts** connections and **under-counts** terminals — the true terminal
share is higher on every row, and the test should be re-run on realised doors when
they exist. And there is a positional confound: a room at hop 1 is adjacent to the
hall, and hall-adjacent rooms have more contacts, so some of the deg-1 gap is
geometry rather than type. **The direction of the finding survives both** — a 5×
gap is not a measurement artefact — but the magnitude should not be quoted as
precise.

### 5.5 What that means for `is_sleeping`

- **`is_sleeping` including `study` is right for the rules it was written for**,
  and now has a citation: Amorim's Private sector is *"bedrooms and study room"*
  (§4.2). `zone.sleeping_group_count` and `zone.no_social_transit` are **routing
  and clustering** properties. Routing a visitor *through* a study is a defect
  whatever the study is for, and `study.is_private` is already `true` in
  `room-constraints.json` for exactly that reason — *"A room that must not lie on
  the circulation path to any other room."*
- **Extending the same set to a *depth* term is a different claim, and it is the
  one that is contested.** Being *on the path* is a defect independent of
  convention; being *near the door* is convention, and Alexander's 157 and
  Hanson's Monteiro finding both place a work room there deliberately.
- ⚠️ **§5.4 says the corpus does not need the exception** — under 5 % of its
  inversions look like front offices. But the corpus **has no studies** (§5.1), so
  that is evidence about bedrooms, not about studies. **A briefed `study` is the
  case the measurement is silent on.**

**Recommendation, and it is a small one:** ship the term with the private set as
`is_sleeping`, and record in `proposer.md` §6.1 that a dwelling whose only shallow
private Room is a **briefed `study` that is a terminal cell** is the one case the
corpus cannot adjudicate — with §5.2's two patterns and §5.3's quote as the
reason. ⚠️ **Do not carve `study` out on the strength of this note**: §5.4 tested
the carve-out's premise and it failed. Record the uncertainty; do not act on it.

---

## 6. The confound — and it runs the opposite way to the one that was feared

The question asked was whether the metric is confounded by dwelling size, on the
theory that *a small flat has fewer distinct depths, so ties inflate*. **The data
says the reverse.**

### 6.1 By room count

| n rooms | dwellings | inverted | **tied** | ordered |
|---:|---:|---:|---:|---:|
| 4 | 22 | 4.5 % | **4.5 %** | 90.9 % |
| 5 | 239 | 11.3 % | **32.2 %** | 56.5 % |
| 6 | 352 | **27.3 %** | 48.0 % | 24.7 % |
| 7 | 373 | 22.0 % | 44.8 % | 33.2 % |
| 8 | 409 | 14.9 % | **63.1 %** | 22.0 % |
| 9 | 250 | 10.8 % | **63.2 %** | 26.0 % |
| 10 | 80 | 11.2 % | 61.2 % | 27.5 % |
| 11 | 28 | 7.1 % | 53.6 % | 39.3 % |
| 12 | 3 | 0.0 % | 66.7 % | 33.3 % |
| **all** | **1 756** | **17.4 %** | **51.0 %** | **31.6 %** |

1. ⭐ **The tie mass is a *large*-dwelling artefact, not a small one** — 4.5 % at
   n = 4, 63.2 % at n = 9. The mechanism is the hall: a big flat has a big hall and
   *both* the nearest private and the nearest social Room open off it, so they tie
   at hop 1. §7 confirms this directly.
2. ⭐ **The inversion rate is strongly non-monotonic and swings 6× inside the band
   v1 promises** — 4.5 % (n = 4) → **27.3 %** (n = 6) → 7.1 % (n = 11).

The corpus's own room-count distribution is n = 6 at 21.1 %, n = 7 at 20.2 %,
n = 8 at 20.2 %, with 14.2 % at n = 5 and 12.4 % at n = 9. **The 17.4 % is a
mixture over that distribution.**

⚠️ **A generated set scored against 17.4 % is partly being scored on its Brief
mix.** An evaluation weighted toward 6-room Briefs would look inversion-heavy and
be marked down for serving 6-room Briefs; one weighted toward 8- and 9-room Briefs
would be flattered. Neither has anything to do with plan quality.

### 6.2 ⭐ This is Hillier's own test, and the term fails it

**RA exists because of this problem.** Hillier, Hanson & Peponis 1984 (UCL Press
reprint, p. 228), verbatim — the formula *and* its reason in one sentence:

> *"It is calculated first by the following formula where MD is the 'mean depth' …
> and k the total number of spaces in the system, and then **applying a correcting
> factor to eliminate the empirical effects of size** (see Hillier and Hanson for
> details) **and permit cross-comparisons of systems of different sizes.**
> **2(MD − 1) / (k − 2)**"*

RRA then divides RA by a diamond value `D_k` (Ostwald 2011, p. 454: *"**RRA =
RA / D_K**"*). And Hillier, Yang & Turner 2012 state the acceptance test:

> *"**The first two tests of a normalised measure must be: whether the means for
> the system correlate with the size of the system in terms of numbers of
> segments; and whether the values for the individual segment continue to predict
> movement.**"*
> *"we plot the mean angular depth of systems against size in numbers of segments.
> **We find a marked, though by no means strong, tendency for mean depth to
> increase as size increases with an r-square of .215.** However, if we substitute
> NAIN for mean depth … **the increase with size all but disappears.**"*

⭐ **§6.1 is that first test, run on this term, and the term fails it far harder
than angular depth did.** Hillier normalised for an r² of .215; the inversion rate
here swings from 4.5 % to 27.3 % across the band. **The proposed term carries no
correcting factor at all.**

⚠️ **And the discipline's own fix is contested at exactly this scale.** Ostwald
2011, p. 452–454:

> *"**the RA values of two houses, each with 9 rooms, may be directly compared. The
> RA values for two houses with, say, K values of 9 and 11 might also be compared,
> but the larger the differential between the two K values the less valid the
> comparison.**"*
> *"**as buildings grow in configurational complexity and scale, their RA values
> typically fall** … Despite this, **many contemporary scholars … ignore RRA in
> favour of RA because they are not convinced by the logic of Hillier's and
> Hanson's method**."*
> *"**The Periklaki and Peponis formula produces correct values for graphs with
> certain node numbers (K = 4, 10, 22, …) and extrapolates for 'in-between' K
> values.**"*

Dwellings live at K ≈ 5–12, which is almost entirely in the extrapolated region
between the exact points 4 and 10. **So the canonical normalisation is least
trustworthy at exactly this scale**, and Hillier's own later move (HYT 2012) was
to abandon the diamond for an **empirically fitted exponent** — `NAtd = ATD /
(NC + 2)^1.2`, where 1.2 is *"the mean 'b' of nearly all the segments of six
cities"*, not a theoretical constant.

**Recommendation, and it follows Hillier's method rather than his formula:** the
term should be reported and scored **per room-count bucket**, or the corpus target
**re-weighted to the Brief distribution** of whatever evaluation set it is run
against. Either is a few lines over `zoning.json`, which already carries `n` per
record. ⚠️ **Reporting a single pooled rate is the one option that should not
ship**, and the same caution applies to §6.1's other three rates measured on this
sample.

⭐ **And this recommendation needs no defending, because it is already the
published protocol.** §3.8: **House-GAN++ never reports a pooled FID** — *"we use
the k-fold cross validation … **dividing the samples into four groups based on the
number of rooms: (5, 6, 7, 8)**"*, and the Mila RLVR paper follows it. The
strongest generative-floorplan benchmark in the field stratifies by room count as
a matter of course. **Cite it and move on.**

⭐ **This is not a new practice for this repo — it is an existing one this term
skipped.** `experiments/zoning/out/report2.txt` already runs the check for term 3
under the heading *"by engine room count — does it concentrate in small flats?"*,
finding social transit rising from 0.0 % at n = 3–4 to 35.4 % at n = 10, and
publishes an *"area-normalised longest run (m per m²), **to kill the size
confound**"* for term 2. **Terms 2 and 3 were checked and term 5 was not.**

### 6.3 ⭐ What the repo has that the canon does not

Ostwald 2011 on sample sizes: *"what is certain is that **the larger the sample
size, the more interesting the results become.** For example, the studies of
seventeen vernacular farmhouses in Normandy [Hillier et al. 1987], seven Pueblo
'room-blocks' [Shapiro 1995] and **eighteen post-war suburban houses in London
[Hanson 1998]** are all informative because the body of data being analysed is
large enough…"*

**Seventeen. Seven. Eighteen.** Against this repo's **2 500**, and Amorim's 140 is
the largest in the canon that this note found. ⭐ **Whatever else is true, this
engine holds the best-powered measurement of an entrance-depth genotype that
exists**, and that is worth stating in `proposer.md` rather than leaving implicit —
it is the reason the numbers here can be trusted to two significant figures where
the literature's cannot.

⚠️ **And it is why §2.5's χ² over-power problem bites.** At N = 17 no test would
reject anything; at N = 2 500 every test rejects everything. **The repo's sample
size is a strength for estimation and a trap for testing.**

### 6.4 ⭐ The right target is 17.8 %, not 17.4 %

| stratum | n | inverted | tied | ordered |
|---|---:|---:|---:|---:|
| dwelling **has** circulation | 1 711 | **17.8 %** | 52.3 % | 29.9 % |
| dwelling has **no** circulation | 45 | **2.2 %** | 2.2 % | 95.6 % |

Inversion is almost entirely a **hall** phenomenon. `openings.md` §7 — quoted in
`zoning.md` §6.4 — makes the engine invent exactly one `hall` on every Plan and
host the primary entrance on it, and §6.4 states the engine's
entry-opens-onto-circulation rate is *"100 % by construction"*. **So every
generated Plan is in the top row and none is in the bottom row.** Scoring against
the marginal 17.4 % mixes in 45 dwellings the engine can never produce.

The correction is 0.4 pp, it is free, and it is the same class of correction §6.4
already made once for R3.

---

## 7. ⭐ How much information the term actually carries

The three-bucket distribution hides how concentrated the underlying joint is. Over
the 1 756 applicable dwellings, `(hop to nearest private, hop to nearest social)`:

| cell | dwellings | share |
|---|---:|---:|
| **private 1 / social 1** | **863** | **49.1 %** |
| private 2 / social 1 | 403 | 22.9 % |
| private 1 / social 2 | 256 | 14.6 % |
| private 1 / social 0 | 78 | 4.4 % |
| private 3 / social 2 | 39 | 2.2 % |
| private 2 / social 2 | 33 | 1.9 % |
| everything else (11 cells) | 84 | 4.8 % |

- **Three cells hold 86.6 % of the mass.** The nearest private Room is at hop 1 or
  2 in 95.8 % of dwellings; the nearest social Room in 92.2 %.
- **96.3 % of all ties are the single cell (1, 1)** — both open off the hall.

⚠️ **So the "gradient" is a near-binary question about one hop**: does a bedroom
open off the entrance hall or not. That is a legitimate thing to measure and it is
much less than the word *gradient* suggests. ⭐ **It is also precisely the
degeneracy §2.6's difference factor was invented to avoid** — an integer-valued
quantity with an effective range of two cannot express *how strongly* the order
holds, only whether it holds, and half the population lands on "neither".

⭐ **And the engine's own construction pushes it toward the dominant cell.**
`openings.md` §7 invents one hall and hosts the front door on it; every Room
touching that hall is at hop 1. A Plan whose hall touches both a bedroom and the
living room — the ordinary case for a hall that has to reach everything — lands in
cell (1, 1) and **ties**.

⚠️ **This is a structural prediction, not a measurement**: no Proposer has been
run, `proposer.md` §6.1 says so, and this note does not run one. But it is
checkable the moment one is, and if it holds, the term saturates at "tie" and
discriminates poorly among generated Plans — **which would be the strongest single
argument against taking it.**

**The cheap check that would settle it** is the tie rate on Plans the *solver*
already produces from retrieval Proposals, scored by the same code. That is inside
`proposer.md` §6.1's own definition of a qualifying term — *computable on a corpus
dwelling and on a generated Plan by the same code* — and it does not wait for
source B.

---

## 8. ⚠️ The scope statement the term needs

Entrance-rooted depth measures **one** of the two interfaces a dwelling makes.
Hillier, Hanson & Peponis 1984 (reprint, p. 230):

> *"All building 'types' define two fundamentally different categories of people:
> a set of **'inhabitants'** whose social identity as individuals is durably
> recorded in the building form by control of space…; and a set of **'visitors'**
> whose rights of presence in the building exist and distinguish them from the
> world of strangers, but not in a durable way… **buildings can be defined in
> these terms as devices for making two kinds of interface: one between inhabitants
> and visitors, and the other between different categories of inhabitant.**"*

Ostwald 2011, p. 455, on which of the two an entrance-rooted graph sees:

> *"the conventional JPG, with exterior as carrier, is drawn from the point of view
> of a logical explorer or **'visitor'** who is not familiar with the building
> interior… **Inhabitant-visitor relations can be reasonably well represented in a
> JPG with the exterior as carrier**, but inhabitant-inhabitant relations are more
> complex and require consideration of multiple additional JPGs."*

and reports Hanson's own view that *"this sequence is a record of
'inhabitant-visitor' relations and that it may be more important for a house to
just consider 'inhabitant-inhabitant' relations"*.

⚠️ **So a dwelling that scores badly on this term may be entirely fine for the
people who live in it.** That is the honest scope statement, it pre-empts the
obvious objection, and `proposer.md` §6.1 should carry it in one sentence beside
the number. It is also a second, independent reason why the term must be **soft
and evaluative** and never a rule — which D10 already gets right.

---

## 9. What could NOT be obtained, and where it was looked for

| Wanted | Where it was looked for | Outcome |
|---|---|---|
| **Hillier & Hanson (1984)**, *The Social Logic of Space*, **pp. 108–113** — the RA/RRA text and the D-value table | UCL Discovery eprint 3813 (403); archive.org `sociallogicofspa0000hill` (lending-restricted, `_djvu.txt` 403, search-inside API dead); a second archive.org upload (**partial — Introduction + ch. 1–2 only, no ch. 3**); ETH Xenotheka (401); Cambridge Core (paywalled) | ❌ **Never read directly.** The RA formula is quoted **verbatim from Hillier's own hand** in two reprinted papers (§6.2) and RRA/`D_K` verbatim from Ostwald quoting H&H 1984: 111–112. **The D-value table itself was never seen.** Page refs pp. 108–109 / 111–113 are from the Bartlett training platform and are ⚠️ secondary |
| **Park, Ergan & Feng**, *Automation in Construction* 158 (2024) 105243 | ScienceDirect (403), NYU Scholars (SSL handshake failure), Semantic Scholar Graph API (`abstract: null`, `openAccessPdf: CLOSED`), OUCI index (bibliography only), arXiv (no preprint) | ❌ **Closed access.** §2.4 marked UNCONFIRMED. **The single most on-point paper in the survey, and the one that should be bought** |
| ***A Pattern Language*** verbatim | patternlanguage.com samples (404); Christopher Alexander CES Archive (provenance only — an early pattern of 01/08/1969 by Alexander, Hirshen, Ishikawa, Coffin & Angel, revised May 1970, later #127 — no text) | ⚠️ Quotes are transcriptions from [iwritewordsgood.com/apl](https://www.iwritewordsgood.com/apl/patterns/apl127.htm) and [patternlanguage.cc](https://patternlanguage.cc/Patterns/Home-Workshop-(157)), consistent across independent copies but **not checked against the printed book.** Verify before quoting in a spec |
| **Hanson (1998)**, *Decoding Homes and Houses*, authoritative copy | CUP (paywalled); epdf.pub (ch. 1 only) | ⚠️ Near-complete scraped text obtained; **prose reliable, pagination not.** Cited by chapter throughout |
| **RPLAN paper** (Wu et al., *ACM TOG* 38(6), 2019) | `staff.ustc.edu.cn/~fuxm/projects/DeepLayout/` (**connection refused**), ACM DL `10.1145/3355089.3356556` (paywalled), Semantic Scholar | ❌ Its front-door input is asserted only via Graph2Plan's description. **UNCONFIRMED** |
| **Teklenburg, Timmermans & van Wagenberg (1993)**, the alternative size normalisation | SAGE (paywalled); TU/e research portal | ⚠️ Abstract only. It confirms the problem — *"**integration values are not independent of the size of urban areas** … implying a need for standardisation"* — and not the remedy |
| **Chermayeff & Alexander (1963)**, *Community and Privacy* — the other canonical public→private hierarchy | No open text found | ❌ The six-domain scheme is known only from secondary sources and is **not quoted here** |
| **Post-2020 home-office placement research** — *Buildings* 14(11):3590 (2024), *Buildings* 15(19):3532 (2025), *Nexus NJ* 2025 (Isparta), *Frontiers of Arch. Research* 2016 (Hamedan) | MDPI, Springer, ScienceDirect | ❌ **HTTP 403 / paywalled on every route.** ⚠️ From search snippets only and **explicitly unverified**: the 2024 paper is reported to recommend a home office *"distanced from the main private areas"* and *"sufficiently far from the living room"* — i.e. segregated from **both**, which is Monteiro's pattern again. **Do not cite without reading** |
| ***Journal of Space Syntax*** site | `joss.bartlett.ucl.ac.uk` — **ECONNREFUSED** | The one JOSS paper needed (HYT 2012) was obtained via UCL Discovery |
| **Sabsabi & Hatipoglu (2024)**, *Enhancing Architectural Plan Generation with ML and Space Syntax Analysis* | `link.springer.com/chapter/10.1007/978-3-031-59329-1_7` | ❌ Springer login wall (303 to IdP) |
| **Number of real plans behind SSPT's reference profile** | Full text of arXiv 2602.22507 | ❌ **NOT PRESENT.** Its reference is *"screened RPLAN"* with no stated N |
| **A paper reporting ties/room-count confounding of a depth metric in dwellings** | SSS proceedings archive (spacesyntax.net), *Journal of Space Syntax*, *Nexus Network Journal*, general search on "small systems" / "room count" / "number of spaces" / "ties" | ❌ **Not found.** The nearest existing statements are Ostwald's K-value caution and Hillier's own size-correction rationale. ⭐ **§6.1's finding appears to be new** — and it is the *reverse* of the mechanism that was hypothesised |
| **A space-syntax name for the quantity** | Same sources | ❌ **Does not exist.** §3.1 |
| **Autodesk Forma's product documentation** | `help.autodeskforma.com` — **every path, including `/robots.txt` and `/sitemap.xml`, redirects to `signin.autodesk.com`**; `help.autodesk.com/view/FORMA\|FRM/ENU/` 404; `autodesk.com/support/technical/product/forma` 403; `aps.autodesk.com/en/docs/forma/v1/` 406 | ❌ **Login-walled. None of Forma's product documentation was read.** Anything Forma publishes about unit-layout evaluation could sit behind that wall. §3.5's Forma row rests on the SimAUD paper, the open-source repo and the patents |
| **Vendor documentation that does not exist** | NXDOMAIN: `help./docs./learn./api./blog.testfit.io`, `developers.finch3d.com`, `help./support./kb.digitalbluefoam.com`, `help./support./learn.archistar.ai`, `docs./help./support./kb./developers.maket.ai`, `docs./help./support./academy./kb./api.architechtures.com`, `help./docs./research./api./blog.planner5d.com`, `docs./support.higharc.com`, `suncg.cs.princeton.edu`. 404: `testfit.io/{docs,help}`, `maket.ai/{docs,help,api}`, `digitalbluefoam.com/{support,docs,help,knowledge-base,resources,documentation}`, `architechtures.com/en/{help,docs,support,knowledge-base,academy,manual,faq,user-manual,resources,glossary}`, `docs.hypar.io/llms.txt`, `intercom.help/{spacemaker/en,maket}` | ⭐ **The absence is the finding.** Six of the nine products publish no documentation site at all. Maket's FAQ is a Framer accordion whose server HTML carries the 24 question headers and **zero answer text**; Higharc's help centre is password-protected; Finch's Medium post on Graph Rules is 403 behind Cloudflare |
| **Google Patents** and most patent mirrors | `patents.google.com` (503 all session; `/xhr/query` throttled after ~6 calls), Justia (403), patentimages (403), uspto.report (403), Espacenet (403), `developer.uspto.gov` (301/key). USPTO PDFs are CCITT-fax scans with no text layer | ✅ **FreePatentsOnline worked** with a browser UA and a Referer header, so §3.6's claims are **full claim text, not snippets**. ⚠️ The Finch/TestFit/Spacemaker/Maket/Higharc patent zeros are confirmed against **FPO's index, not Google's assignee-normalised one** — treat as UNCONFIRMED negatives |
| **Coorey & Jupp**, *Generative spatial performance design system*, *AI EDAM* 28(3), 2014 | Cambridge Core (paywalled); the UTS PhD thesis full text is withheld for third-party copyright | ❌ ⭐ **The single most likely place a distribution-based or depth-based method exists in the market's academic lineage** — its abstract describes precedent-corpus work (*"capture of precedent designs, extraction of spatial analytics … populations can be used to drive the generation and optimization"*) **and cites Hillier & Hanson space syntax.** Archistar's founder. **Worth chasing** |
| **3 of 4 Digital Blue Foam whitepapers** | HubSpot lead-capture forms | ⚠️ Including *"Real-time Urban Insights: Neighbourhood Scoring System"* — its content is substantially the CAADRIA 2022 paper, which **was** read in full |
| ***RFP-A***, MDPI *Buildings* 15(10):1674 | `mdpi.com/.../1674`, `/htm`, `doi.org/10.3390/buildings15101674`, Scilit — **all HTTP 403** | ✅ **Obtained** on the fourth route, the `mdpi-res.com` asset host, and extracted locally. §2.3 is first-hand. Recorded because the obvious routes all fail and the next reader will hit the same wall |
| **The `AZ` inversion rate** | — | ❌ Not measured, like every other corpus rate on this map. `zoning.md` §6.8 already discloses it (C5) and this note adds nothing |

---

## 10. Reproducing §4, §5, §6 and §7

All of it reads `experiments/zoning/out/zoning.json`, the file `entry_order2.py`
already reads. **No corpus pass, no writes, seconds each.** Nothing was added to
`experiments/`; these are one-liners run from the repo root.

```
# room-count breakdown of the three buckets (6.1)
./venv/Scripts/python.exe -c "import json,collections; \
recs=json.load(open('experiments/zoning/out/zoning.json'))['recs']; \
md=lambda r,ks:min([d for d,k in zip(r['dist'],r['classes']) if k in ks],default=None); \
rows=collections.defaultdict(collections.Counter); \
[rows[r['n']].update([('inv' if md(r,{'private'})-md(r,{'social'})<0 else 'tie' if md(r,{'private'})==md(r,{'social'}) else 'ok')]) \
 for r in recs if md(r,{'private'}) is not None and md(r,{'social'}) is not None]; \
print({n:dict(c) for n,c in sorted(rows.items())})"

# social-set sensitivity (4.3)  -- swap {'social'} for {'social','kitchen'}
# open-plan split (4.4)         -- split on 'LIVING_DINING' in r['types']
# circulation stratum (6.4)     -- split on ('circ' in r['classes'])
# joint cell table (7)          -- Counter((md(r,{'private'}), md(r,{'social'})))
# nearest-private type (5.1)    -- argmin over dist, read r['types'] at that index
# terminal-cell test (5.4)      -- argmin over dist, read r['deg'] at that index
# corpus label census (4.4)     -- Counter over r['types']
```

The divergence table in §2.5 needs nothing but the three corpus shares; it is
arithmetic and is reproduced in full in the numbers given.

⚠️ **These recomputations inherit every caveat `zoning.md` §6.8 and §7 record** —
the 1 206 disconnected dwellings dropped, the Swiss-only corpus, the contact-graph
rather than realised-door edges. In particular the disconnection skip biases toward
well-connected dwellings, which §7 notes biases term 1 in a known direction; **its
effect on the tie mass is still unmeasured**, and §6.1's finding that ties rise
with room count makes that gap more interesting than it was, not less. §5.4's
terminal-cell test inherits the contact-vs-door caveat most sharply and says so.

---

## 11. What this hands on

**To whoever writes the fifth term into `proposer.md` §6.1** — seven things, in
decreasing order of how much they move the number:

1. **Name the social set in the same sentence as the rate**, and cite Amorim 1997
   for it. 17.4 % / 14.7 % / 21.8 % are three different terms (§4.3), and 29.8 % of
   the corpus is unscoreable under the reading that produced 17.4 %.
2. **Report per room-count bucket, or re-weight to the Brief mix.** A 6× swing
   across the 4–10 band (§6.1) makes a pooled rate a measurement of the Brief
   distribution, and Hillier's own acceptance test says so (§6.2). Terms 2 and 3
   already have this check in `report2.txt`; term 5 does not. ⭐ **Cite House-GAN++
   for the protocol** — it never reports a pooled FID and stratifies into
   (5, 6, 7, 8) rooms as a matter of course (§3.8). This is not a novel demand.
3. **Quote 17.8 %, not 17.4 %.** The engine is 100 % in the has-circulation
   stratum by construction (§6.4).
4. **Decide whether it is a defect or a typology, and make §6.5 and §6.1 agree.**
   §2.7. If defect: one-sided, corpus rate as ceiling. If typology: delete the word
   "violation" from §6.5.
5. **Do not use KL** — it is `∞` for the generator that never inverts (§2.5). If a
   divergence is kept, **EMD** on the ordered support is the one the neighbouring
   literature picked and the only one that respects bucket order; it does not by
   itself deliver item 4.
6. **Record that the discipline rejects trichotomies**, and that Hillier's
   difference factor `H*` is the continuous alternative (§2.6) — as a noted option,
   not as a substitution, because it measures integration rather than entrance
   depth and would be a different term.
7. **Carry two one-line scope statements**: that the term sees the
   *inhabitant–visitor* interface only (§8), and that a briefed `study` is the one
   membership the corpus cannot adjudicate (§5.5). ⚠️ **And do not name anything
   `inverted_genotype`** — the term is taken (§3.1).

**To whoever next opens `experiments/zoning/`** — one bug and two measurements:

- ⚠️ **`measure_zoning.py`'s `CLASS` map has no `KITCHEN_DINING` entry** and
  `cls()` silently returns `"other"` for anything unknown (§4.4). Three rooms
  today, a whole region tomorrow. **Make the unknown label raise.**
- **Run the tie rate on Plans the solver already produces from retrieval
  Proposals.** §7 predicts the engine's hall construction saturates the term at
  "tie"; that prediction is the strongest argument against taking the term and it
  is cheap to check.
- **Re-run §5.4's terminal-cell test on realised doors** rather than contact, when
  a door graph exists. The finding is robust in direction and its magnitude is not.

**To whoever reads a paper next** — three, and all are cheap:

- ⭐ **Park, Ergan & Feng**, *Automation in Construction* **158** (2024) 105243
  (§2.4). The **only** prior art that has done what D10 proposes — scored generated
  plans against human-designed plans on a privacy quantity — closed access, about
  €35. Everything this note says about it is second-hand through RFP-A, whose
  citation trail for *"privacy level"* is demonstrably broken.
- ⭐ **Coorey & Jupp**, *AI EDAM* 28(3), 2014 (§9). Archistar's founder, and the
  one paper in the market's academic lineage whose abstract describes both a
  **precedent corpus** and **space syntax**. If a distribution-based or
  depth-based method exists anywhere in the commercial world, that is where.
- ***A Pattern Language*** Patterns 127, 129, 141, 142 and 157 in print. §5.2 is
  load-bearing and rests on transcriptions.

**To `docs/research/competitive-landscape.md`'s next revision** — three things §3.5
to §3.8 produce that belong there rather than here:

- **A *published evaluation methodology* row** beside the existing *Technique*
  rows. That note records what each product **does**; nothing on this map recorded
  how any of them decides a layout is **good** until now.
- ⚠️ **The Finch patent discrepancy.** Dezeen (2019) and AEC Magazine both report
  Finch's *"patented graph technology"*, and **no patent is findable under the
  company or the inventor**. `competitive-landscape.md` does not currently repeat
  the claim and should not start; if it ever does, it needs this caveat attached.
  Same for **Spacemaker AS**, which appears to have shipped on trade secret alone.
- **Six of nine products publish no documentation site at all** (§9). That is a
  competitive fact in its own right and it is not in the landscape note.
