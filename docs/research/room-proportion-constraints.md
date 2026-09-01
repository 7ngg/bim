# Room proportion (aspect ratio): who bounds it, at what value, and how (September 2026)

**Question.** Do floor-plan generation systems — commercial products or published research
generators — constrain or score **room proportion** (length : width aspect ratio)? Is a ~2:1 to
~3:1 bound standard practice, an outlier, or absent?

**Why it was asked.** `rules.json` ships `dim.aspect_ratio_hard` = **3.0** (hard reject) and
`dim.aspect_ratio_soft` = **2.2** (ranking preference), both fitted to Swiss Dwellings
(p99.5 and p95 respectively — `acceptance-thresholds.md` §2). The rule's own note opens
*"No surveyed source states an aspect rule."* `az-market-default-against-practice.md` §2.3 already
falsified that sentence from the **standards** side (AzDTN 2.7-3 cl. 5.1 recommends a habitable
room's length not exceed 2× its width). This document falsifies it from the **generation-systems**
side, and prices the difference.

**Method.** Primary sources: paper PDFs downloaded and read in full, source code read from the
repository, benchmark data files downloaded and parsed, vendor documentation. For every generator
claimed here to have *no* aspect term, the claim rests on a case-insensitive full-text regex over
the extracted PDF text for
`aspect ratio | elongat | slender | compactness | shape quality | proportion | squarene`, not on
skim-reading — so the negatives are reproducible and their hit counts are reported. Anything not
established from a primary source is marked **NOT ESTABLISHED** rather than guessed; every
derivation of mine is labelled as such. Retrieval date **2026-09-01**.

**Scope note.** The brief asked about commercial products and published *generators*. Two adjacent
literatures turned out to carry the answer and are included deliberately: **VLSI floorplanning**
(§4.4), which is where the numeric precedent lives, and **constraint-based architectural layout
optimisation** (§4.5), which is where the *rationale* lives. Excluding them would have produced a
false negative.

---

## TL;DR — the one-sentence answer

> **A hard per-room aspect-ratio bound is completely standard — but in *floorplanning*, not in
> *floor-plan generation*: the VLSI literature has enforced one for decades and its modal interval
> is exactly **[1/3, 3]**, with **[0.5, 2]** as the second convention hard-coded into the GSRC
> benchmark files themselves; the constraint-based architectural literature carries the same
> constraint *form* (Michalek's "Minimum Ratio Constraint Group", Medjdoub's CSP ratio primitive,
> Shekhawat's per-room AR range) but **publishes no numeric value at all**; the learned
> generators — House-GAN through the 2026 diffusion and LLM models — do not put aspect in a loss, a
> constraint, or an evaluation metric anywhere; and no commercial product exposes proportion as a
> knob — three expose a proportion *setter* or an unquantified slider, none a maximum — while the
> one shipping architectural tool that does hard-reject on proportion is open-source and does it at
> exactly **[1/2, 2]**.**

So the answer to "is ~2:1 to ~3:1 standard, an outlier, or absent?" is **all three at once,
depending on which literature you stand in** — and that is the finding:

| literature | aspect bound? | our 3.0 / 2.2 relative to it |
|---|---|---|
| **VLSI floorplanning** | hard, universal, numeric | **3.0 is the modal hard bound. 2.0 is the benchmark convention.** Dead centre. |
| **Constraint-based architectural layout** | hard, universal, **no numbers published** | our *form* is standard; our *numbers* have no precedent here |
| **Graph-theoretic RFP** | in the dimensioning stage only; deliberately deferred elsewhere | matches our ADR 0003 staging |
| **Learned generators (~20)** | **absent** | no precedent in either direction |
| **Commercial products** | **no bound anywhere**; 3 of 13 expose a proportion *setter or slider* | no competitor precedent for a maximum |
| **Open-source architectural generators** | **hard [1/2, 2]** in Magnetizing FPG | the one real precedent for **2.0** |
| **Building codes (IBC/IRC/NYC)** | **absent** | AzDTN's 2:1 is a post-Soviet-tradition outlier |

Four consequences for the decision:

1. **The sentence *"No surveyed source states an aspect rule"* is now false several times over** and
   should be struck from `rules.json`. Michalek et al. (2002) state it as an inequality *with our
   exact rationale*; Shekhawat's RFP dimensioning takes an AR range as a first-class hard input; the
   ETH RL line rejects on it in shipped code; and VLSI has treated it as routine since at least
   Adya & Markov (2003).
2. **3.0 is not an arbitrary number — it is the single most common hard aspect bound in the
   engineering literature on this exact problem.** That is a **second, independent** defence of the
   shipped value alongside "p99.5 of Swiss Dwellings", reached from a different direction.
3. **2.0 is NOT unprecedented — and this is the finding that cuts against the rest of the survey.**
   Magnetizing FloorPlanGenerator, a working architectural generator, **hard-rejects any room outside
   `[1/2, 2]` by default** (§2.4), and GSRC encodes the same interval (§4.4). What 2.0 lacks is any
   evidence of surviving a real corpus: that tool *invents* rooms at ratios ≤ 1.9 and validates
   against nothing, and it exempts no room type — its corridors are bound at 2.0 too, which our
   corpus (corridor p90 = 3.30) says is wrong. Our kitchens reach p99.5 = **3.63**.
4. **The shape of our rule — hard reject + soft preference + circulation exemption — is
   independently corroborated**, including the exemption, which Shekhawat arrives at for the same
   reason we did (§4.1).

---

## 1. The deliverable table — who bounds aspect, at what value, how

Ordered by how binding the mechanism is.

| # | Source | Kind | Aspect mechanism | Value | Hard / soft | Evidence |
|---|---|---|---|---|---|---|
| 1 | **PeF** (arXiv 2210.03293); **Per-RMAP**; **PARSAC** (Intel, arXiv 2405.05495) | VLSI floorplanning | per-module inequality `AR_l ≤ h/w ≤ AR_u`, under `s.t.` | **[1/3, 3]** — the modal value, three independent papers | **HARD** (feasibility; PARSAC *clamps*) | §4.4 |
| 2 | **GSRC soft-block benchmarks** (`n100-2.soft`, CompaSS/UMich) | VLSI benchmark **data format** | per-block `<area> <min-AR> <max-AR>` **in the input file** | **[0.5, 2]** for all 100 blocks | **HARD** (input spec) | §4.4 |
| 3 | **Adya & Markov**, IEEE TVLSI 11(6) 2003 | VLSI floorplanning | soft-block shape interval | **0.75 – 1.5** (top-level clustered blocks) | **HARD** | §4.4 |
| 3b | **Magnetizing FloorPlanGenerator** (Gavrilov, Schneider, Dennemark & Koenig; Bauhaus-Weimar) | architectural generator, **open source** | `ProportionThreshold` — candidate rejected unless both rooms lie in the interval | **[1/2, 2]**, default **2**, user-settable; plus `MaxRatio = 1.9` | **HARD reject** | §2.4 |
| 4 | **Michalek, Choudhary & Papalambros**, *Eng. Optimization* 34(5) 2002 | architectural optimisation | **"Minimum Ratio Constraint Group"**, Eq. 23 | `R_min` symbolic — **no numeric value published** | **HARD** (`g(x) ≤ 0`, penalty-enforced) | §4.5 |
| 5 | **Medjdoub & Yannou**, *CAD* 32(1) 2000 | architectural CSP | explicit L/W **ratio constraint primitive** | interval endpoints — **no numeric L/W value published** | **HARD** (arc-consistency propagated) | §4.5 |
| 6 | **Upasani, Shekhawat & Sachdeva**, *Autom. in Constr.* 113:103149 (2020) | graph-theoretic RFP, dimensioning | per-room `(AR_i,min, AR_i,max)`, iterated to feasibility | **user-defined; no default published** | **HARD** (feasibility) | arXiv 1910.00081, §4.1 |
| 7 | **SpaceLayoutGym** (Kakooee & Dillenburger, ETH) | RL generator, **open source** | `max_acceptable_aspect_ratio` → `rejected_by_proportion` | **10** (low-res) / **20** (high-res); deviation tolerance **6** | **HARD reject** + soft target | source code, §3.1 |
| 8 | **Chen & Chang**, ISPD '05 (B*-tree / fast SA) | VLSI | per-block AR range on moves; **outline** AR penalty | per-block: unnumbered. Outline AR tested **[1, 4]** | per-block **HARD**; **outline** AR **SOFT** | §4.4 |
| 9 | **Weber, Mueller & Reinhart** | hypergraph generator, Nature Comms | perimeter difference score Δp, cull threshold | **Δp ≤ 0.1** ⇒ **aspect ≈ 2.55** (derived, §5) | **HARD cull** | Nat Commun 15:8327, §5 |
| 10 | **Kakooee & Dillenburger**, JCDE 12(1):149 (2025) | RL generator | desired per-room proportion `P*`, misfit `ΔP` in reward | targets **[1, 1.5, 1.2, 1, 2, 4]**; range **1–6** | **SOFT** (reward shaping) | §3.1 |
| 11 | **Tell2Design** (ACL 2023) | dataset + generator | aspect ratio as a natural-language *instruction* per room | observed targets **3/1, 5/2, 7/4, 1/2, 4/5, 3/4, 7/8** | **conditioning only** — not scored | §3.2 |
| 12 | **Squarified treemaps** (Bruls et al. 2000) → **Marson & Musse** (2010) | classical packing | greedy minimax on aspect ratio | target **1**; **no bound** | **SOFT** (objective) | §4.2 |
| 13 | **HypergraphFormer** (2026) | LLM generator | compactness deviation δ as *evaluation metric* + post-hoc objective | no threshold | **metric only** | arXiv 2605.18932, §3.3 |
| 14 | **GPLAN** (Shekhawat et al., *Autom. in Constr.* 127:103718, 2021) | graph-theoretic RFP | width/height **box** only — `min(d_i) ≤ w(e_ji) ≤ max(d_i)` | — | **NOT a ratio bound** | §4.1 |
| 15 | **IBC / IRC / NYC codes** | building code | — | — | **ABSENT** | §6 |
| 16 | **House-GAN, House-GAN++, Graph2Plan, iPLAN, GSDiff, MaskPLAN, ChatHouseDiffusion, RLVR-LLM, boundary-diffusion, TLC-Plan, markup-vector** | learned generators | — | — | **ABSENT** (full-text scanned) | §3.4 |
| 17 | **HouseDiffusion** | learned generator | "room shape quality" discussed **only** in an ablation | — | **ABSENT** as loss/metric | §3.4 |
| 18 | **"Ergonomic Principles" apartment generator** (2026) | differentiable ergonomic loss | all four cost terms are **distances** | — | **ABSENT** | arXiv 2604.08411, §3.4 |
| 19 | **DPLAN** (2026) | graph-theoretic | explicitly **defers** proportion downstream | — | **ABSENT by design** | arXiv 2606.21159, §4.3 |
| 20 | **Snaptrude** | commercial | `Ratio` field (width / length) per space, editable | user-typed | **exact setter** — no min/max | §2.1 |
| 21 | **Finch3D** | commercial | **"Squareness"** design-priority slider; separately "Minimum Unit Width… Avoid long, narrow units" | **no number published** | **SOFT**, unquantified | §2.1–2.2 |
| 22 | **Hypar** | commercial (archived fn) | `Default Aspect Ratio` seeds `width = sqrt(area x ratio)` | **1.8** | **shape seed**, not a limit | §2.1 |
| 23 | **ARCHITEChTURES**, **TestFit**, **Forma**, **Maket**, **Digital Blue Foam**, **Planner5D**, **Cedreo**, **Coohom**, **Spacio**, **Delve** | commercial | min dimensions / inscribed-circle diameter / explicit width x depth only | — | **ABSENT** | §2.2–2.3 |

---

## 2. Commercial products

**Headline, and it is not the one this section originally expected: three products DO expose a room
proportion control — but not one of them is a *bound* or a *penalty*. Snaptrude lets you type an
exact ratio, Finch offers an unquantified "Squareness" slider, Hypar seeds shapes from a default
aspect of 1.8. Nobody sells a maximum. And no product in the sweep exposes a compactness or
shape-factor score at all.**

`competitive-landscape.md` established what each product's constraint vocabulary *is*; this section
only asks whether proportion is in it. Roughly 1,000 vendor pages were fetched and grepped across
the set (Finch 82, TestFit 274, Forma 27, Snaptrude 124, Digital Blue Foam 69, Maket 124,
Planner5D 60, Cedreo 160, Coohom 67, Laiout 108), plus four source repositories.

### 2.1 The three that have something

| Product | Mechanism | Value | Kind |
|---|---|---|---|
| **Snaptrude** | `Ratio` column in the Program Mode table, = width ÷ length, editable per space | user types it | **exact setter**, not a range |
| **Finch3D** | **"Squareness"** design-priority slider | **no formula, no number published** | **soft, qualitative** |
| **Hypar** | `Default Aspect Ratio` used to derive a shape: `width = sqrt(area x ratio)` | **1.8** | **shape seed**, not a limit |

**Snaptrude** — verbatim from
[help.snaptrude.com, About Program Mode](https://help.snaptrude.com/en/articles/11154579-about-program-mode):

> "**Ratio** This field calculates the ratio of width over length of the space specified from object
> properties. User input would be used to edit width length of associated space on canvas based on
> ratio"

and its AI flow assigns proportions internally, verbatim from
[AI-powered design workflows](https://help.snaptrude.com/en/articles/12555467-ai-powered-design-workflows):

> "Step 4: Assign Dimensions Each space is automatically assigned optimized width, depth, and
> **aspect ratios**."

This is the closest thing to a room-proportion feature in the market — and note what it is: a
**setter**, not a validator. You tell it the ratio and the room is reshaped. There is no minimum, no
maximum, and nothing that rejects a bad one.

**Finch3D** — the "Squareness" control is real but unquantified, verbatim from
[docs.finch3d.com](https://docs.finch3d.com/llms-full.txt):

> "**Squareness and Adjacencies: Improve interior logic and flow**"

*Correction recorded deliberately, because it is the kind of error this document exists to prevent:*
the Finch algorithm-theory page names a **"Ratio score"** and **"Ratio weight"** alongside unit-size
and daylight scores, which reads like a geometric proportion metric and is **not** one — Finch's
full docs resolve "ratio" to **unit-mix percentages** (*"Unit Mix: Enforce target mix percentages"*).
Anyone re-running this research will hit the same false positive.

**Hypar** — `Default Aspect Ratio` = **1.8**, used to generate a room's width from its area rather
than to constrain it. The function is archived.

### 2.2 What the market uses *instead* — and one vendor says so out loud

The dominant pattern is a **minimum dimension standing in for an aspect bound**, which §4.1 and
Michalek's Eq. 20–23 (§4.5) show cannot do the job. Finch states the substitution in its own words —
verbatim:

> "**Minimum Unit Width (e.g., 5 meters): Avoid long, narrow units in deep buildings**"

**That sentence is the whole finding of this document in one line.** A vendor names the exact
pathology `dim.aspect_ratio_hard` exists to catch — *long, narrow* — and reaches for a **minimum
width** to prevent it. Finch then *also* ships a separate Squareness weight, which is the clearest
available sign that a vendor found minimum width alone insufficient.

**ARCHITEChTURES** goes further in the same wrong direction: it gates room geometry on **the
diameter of the largest circle inscribed in the room**, and that override beats the user's area
target. An inscribed circle is a pure *width* measure — it is provably blind to elongation, since
stretching a room lengthwise does not change it at all.

**TestFit**'s only "aspect ratio" in 274 pages resolves to a **minimum courtyard width per building
height** — a daylighting rule, not a room rule. **Maket.ai** takes per-room **x and y target
dimensions** (*"click under the x and y columns"*) with adjacency-only generation rules, and pushes
dimensional compliance outside the product entirely: *"Egress requirements, minimum room sizes… A
licensed professional needs to verify compliance."*

### 2.3 The negatives, including two instructive false positives

| Product | Proportion control? | What was found instead |
|---|---|---|
| **Digital Blue Foam** | **no** | targets are massing-scale: *"Number of Subplots, Site Coverage, Gross Floor Area and Maximum Height"* |
| **Coohom** | **no** | "AI Smart Layout" furnishes *already-drawn* rooms; does not generate room geometry |
| **Planner5D** | **no — false positive** | its only "Aspect Ratio" is a **render camera** setting: *"Choose between portrait or landscape mode."* |
| **Cedreo** | **no — false positive** | both hits are UI zoom / furniture scaling: *"The **aspect ratio conservation** This button enlarges and reduces a project while maintaining its proportions."* |
| **Spacio** | **no** | "ratios" = unit-mix percentages |
| **Sidewalk Labs Delve** | **no** | its complete published scored-outcome taxonomy — *"Yield… Unit mix, Open space… Parcelization, Zoning, Massing strategies, Circulation strategies… Views, Daylight, Walkability, Sun hours… Construction cost, Capital value, Net profit"* — contains **no shape term** |
| **Laiout, Archistar, PlanFinder** | **not established** | no help centre / behind login / domains dead |

**Zero hits for `compactness`, `shape factor`, `elongat*` or `slender*` across the entire ~1,000-page
vendor corpus.** No product scores room shape.

### 2.4 The one hard numeric room-aspect bound in shipping tooling — and it is 2.0

It is not a commercial product. It is the open-source Grasshopper generator
`floorplan-generation-stack.md` §5.3 already names: **Magnetizing FloorPlanGenerator**
([hellguz/Magnetizing_FloorPlanGenerator](https://github.com/hellguz/Magnetizing_FloorPlanGenerator)),
the Gavrilov / Schneider / Dennemark / Koenig (Bauhaus-Universität Weimar) tool.

Verified first-hand by reading the source. `Magnetizing_FPG/SpringSystem_ES.cs`, verbatim:

```csharp
pManager.AddNumberParameter("ProportionThreshold", "ProportionThreshold",
                            "ProportionThreshold, >= 1", GH_ParamAccess.item, 2);
...
public static double proportionThreshold = 2f;
...
// If the proportions of both rooms are in [0.5; 2] -> ok
if (!(GetRoomXYProportion(roomCurves[i]) > 1 / proportionThreshold &&
      GetRoomXYProportion(roomCurves[i]) < proportionThreshold &&
      GetRoomXYProportion(roomCurves[j]) > 1 / proportionThreshold &&
      GetRoomXYProportion(roomCurves[j]) < proportionThreshold))
```

and `Magnetizing_FPG/MagnetizingRooms_ES.cs`, verbatim:

```csharp
// MaxRatio stated for maximum allowed proportions of every room.
const double MaxRatio = 1.9f;
```

**This is a genuine architectural precedent for exactly the number the project is considering, and
it must be reported as such even though it cuts against the rest of this survey.** It is:

- a **hard reject** — candidate moves failing the test are discarded, not penalised;
- **per room**, applied to both rooms in a pair;
- **user-settable**, exposed as a Grasshopper input with **default 2**;
- **symmetric**, `[1/2, 2]` — the same shape as the VLSI `[1/3, 3]` and GSRC `[0.5, 2]` intervals
  (§4.4), which is likely where the convention comes from;
- reinforced by a second constant, `MaxRatio = 1.9`, used when *inventing* a room's proportions.

So: **a working architectural floor-plan generator hard-rejects rooms outside [1/2, 2] by default.**
The 2:1 figure is not without precedent in a generator after all — the AzDTN recommendation and this
tool land on the same number independently. What this precedent does **not** supply is any evidence
that 2.0 survives contact with a real corpus: this is a research prototype whose rooms are
*invented* at ratios ≤ 1.9 and never validated against measured construction, and it carries **no
room-type exemptions at all** — its corridors are bound by the same 2.0 as its bedrooms, which our
own data (corridor p90 = 3.30) says is wrong.

## 3. Published learned generators

### 3.1 The one line that genuinely constrains aspect — ETH Zurich RL (Kakooee & Dillenburger)

This is the strongest positive finding in the learned-generator space, and it is **one research
group**, not the field.

**Paper 1 — "Illuminating Spaces: Deep Reinforcement Learning and Laser-Wall Partitioning for
Architectural Layout Generation"**, Reza Kakooee & Benjamin Dillenburger, arXiv
[2502.04407](https://arxiv.org/abs/2502.04407) (2025-02-06).

Verbatim, on the experimental setup:

> "We define six distinct design scenarios, varying in complexity from 4 to 9 rooms. Table 1
> outlines the properties of the desired layout for each scenario. **For all scenarios, the desired
> room aspect ratio ranges from 1 to 6.**"

Verbatim, on how binding it is:

> "The agent's ability to find a design solution indicates that the generated layouts closely match
> the geometric properties defined in the table, **including the aspect ratio requirements. This is
> because geometric properties are integral constraints of the optimization problem, and without
> satisfying these constraints, a solution cannot be achieved.**"

And on evaluation:

> "we evaluate the layouts generated by our RL agents based on their adherence to the desired
> geometric properties (**areas and aspect ratios**) and topological requirements (adjacencies)"
>
> "the achieved aspect ratios closely match the specified values (both less than 5%)"

Note the reward is shaped, not a hard gate, in the paper's own description:

> "Negative rewards for intermediate layouts that deviate significantly from desired properties."
> … "Non-negative reward for solutions that fall within a threshold of closeness to desired
> properties, scaled linearly or nonlinearly based on the closeness."

**Paper 2 — "Enhancing architectural space layout design by pretraining deep reinforcement learning
agents"**, same authors, *Journal of Computational Design and Engineering* **12(1):149–166 (2025)**,
DOI [10.1093/jcde/qwae109](https://doi.org/10.1093/jcde/qwae109). Aspect ratio is a per-room
**desired proportion `P*`**, with the misfit `ΔP` entering both instant and terminal reward
(weights `w_p_m`, `w_p_s`). Verbatim design requirement from the paper:

> "The aspect ratios of the rooms should be **[1, 1.5, 1.2, 1, 2, 4]**."

So the *targets* an architect-facing RL system asks for cluster at **1 to 2**, with 4 as the loosest
single room in the scenario.

**The code — the only literal hard aspect gate found anywhere in this survey.**
`SpaceLayoutGym`, [github.com/RezaKakooee/space_layout_gym](https://github.com/RezaKakooee/space_layout_gym).

`gym-floorplan/gym_floorplan/envs/fenv_config.py`, verbatim:

```python
self.desired_aspect_ratio = 1
self.aspect_ratios_tolerance = 6 if self.is_proportion_a_constraint else 20
self.min_acceptable_aspect_ratio = 1
self.max_acceptable_aspect_ratio = 10 if self.resolution == 'Low' else 20
```

`gym-floorplan/gym_floorplan/envs/observation/design_inspector.py`, verbatim:

```python
def _check_proportion_status(self, plan_data_dict, room_name):
    ...
    if prop > self.fenv_config['max_acceptable_aspect_ratio']:
        return False
    delta_aspect_ratio = plan_data_dict['rooms_dict'][room_name]['delta_aspect_ratio']
    return delta_aspect_ratio <= self.fenv_config['aspect_ratios_tolerance']
```

and the failure label is a first-class rejection status: `w_status = 'rejected_by_proportion'`.

**Read this carefully — it is the most decision-relevant number in the document.** The only
open-source generator that *hard-rejects* on aspect sets the gate at **10** (or 20). Its *desired*
aspect is **1**. There is nothing at 2, and nothing at 3. The hard gate is doing anti-degeneracy
work — killing a room one cell wide — which is exactly the job `dim.min_clear_width` already does
for us, and is **not** the job our 3.0 is doing.

### 3.2 Tell2Design — aspect ratio as a user *instruction*, never scored

**Tell2Design: A Dataset for Language-Guided Floor Plan Generation**, Leng, Zhou, Dupty, Lee, Joyce
& Lu, **ACL 2023**, [aclanthology.org/2023.acl-long.820](https://aclanthology.org/2023.acl-long.820.pdf).

Aspect ratio is one of the room attributes the dataset's natural-language instructions carry.
Verbatim, from a real collected instruction:

> "It would be great to have a balcony approx 50 sqft **with an aspect ratio of 3 over 1**. The
> balcony should be next to the master room."

and from the artificial-instruction templates (Figure 8), verbatim:

> `"Make the aspect ratio of {room.type} "` · `"The aspect ratio of {room.type} should be "` ·
> `"I would like to have the aspect ratio of {room.type} "` · `"Can you make the aspect ratio of
> {room.type} "` · `"Can we have the aspect ratio of {room.type} to be "`

Observed target values across the worked example: **3/1** (balcony), **5/2** (balcony), **7/4**
(kitchen), **7/8** (bathroom), **3/4** (common room), **4/5** (master room), **1/2** (living room).

**But the evaluation ignores it entirely.** Verbatim, §Evaluation Metrics:

> "For testing, we use macro and micro **Intersection over Union (IoU)** scores between the
> ground-truth (GT) and generated floor plans at pixel level as the evaluation metrics"

So aspect ratio is *conditioned on* and never *measured*. This is the field's characteristic
posture: proportion is something a user may ask for, not something the system is held to.

Worth noting for our purposes: Tell2Design's human annotators, describing **real** floor plans,
routinely produced aspect targets up to **3:1**. That is a (weak, secondary) corroboration that real
rooms reach 3 and that a 3.0 cap is near the top of the observed range — consistent with our own
p99.5 = 3.02.

### 3.3 HypergraphFormer — a shape metric, but an evaluation one

**HypergraphFormer: Learning Hypergraphs from LLMs for Editable Floor Plan Generation**, arXiv
[2605.18932](https://arxiv.org/abs/2605.18932) (Autodesk Research-affiliated). Verbatim:

> "We adopt the per-polygon **compactness deviation** δ(a, b) = 1 − L_Sa·L_b / (L_a·L_Sb) of [15],
> where L_a, L_b are the perimeters of polygons a, b and L_Sa, L_Sb the perimeters of squares with
> the same areas as a and b, respectively"

It is used two ways, and neither is a constraint:
- as an **evaluation metric** aggregated over matched room pairs;
- as a **post-hoc procedural objective**: "rotating or flipping the hypergraph to **maximize
  per-room compactness**".

The paper is candid that its representation *costs* it shape quality, verbatim:

> "the BSP tiling constraint gives up modest per-room **squareness** on δ in exchange for exact
> boundary tiling"

Its reference [15] is Weber, Mueller & Reinhart — see §5, which is where the number lives.

### 3.4 The negatives — and they are the bulk of the field

Each of the following was scanned in full text. Hit counts are for the whole regex, including
irrelevant senses of the word "proportion"/"aspect".

| Generator | Venue / id | Aspect in loss? | in metric? | Finding |
|---|---|---|---|---|
| **Graph2Plan** | [2004.13204](https://arxiv.org/pdf/2004.13204) | no | no | **0 regex hits in the entire paper.** Losses are cross-entropy + L1 box regression + geometric consistency |
| **House-GAN** | [2003.06988](https://arxiv.org/pdf/2003.06988) | no | no | 2 hits, both incidental prose |
| **House-GAN++** | [2103.02574](https://arxiv.org/pdf/2103.02574) | no | no | 2 hits, both incidental prose |
| **iPLAN** (CVPR 2022) | [openaccess](https://openaccess.thecvf.com/content/CVPR2022/papers/He_iPLAN_Interactive_and_Procedural_Layout_Planning_CVPR_2022_paper.pdf) | no | no | **0 regex hits** |
| **GSDiff** (AAAI 2025) | [2408.16258](https://arxiv.org/abs/2408.16258) | no | no | 2 hits, both the diffusion-schedule sense of "proportion" |
| **MaskPLAN** (CVPR 2024) | [openaccess](https://openaccess.thecvf.com/content/CVPR2024/papers/Zhang_MaskPLAN_Masked_Generative_Layout_Planning_from_Partial_Input_CVPR_2024_paper.pdf) | no | no | 1 hit, "masked proportion" (unrelated) |
| **ChatHouseDiffusion** | [2410.11908](https://arxiv.org/abs/2410.11908) | no | no | 1 hit, unrelated |
| **HouseDiffusion** | [2211.13287](https://arxiv.org/abs/2211.13287) | no | no | see below |
| **"Ergonomic Principles Guided Apartment Layout Generation"** | [2604.08411](https://arxiv.org/abs/2604.08411) | no | no | see below |
| **Generative Floor Plan Design with LLMs via RLVR** | [2605.14117](https://arxiv.org/abs/2605.14117) | no | no | see below |
| **Boundary-Constrained Diffusion** | [2602.01949](https://arxiv.org/abs/2602.01949) | no | no | 2 hits, neither relevant |
| **TLC-Plan** | [2602.07100](https://arxiv.org/abs/2602.07100) | no | no | proportion appears only as a *criticism of a baseline* (below) |
| **Unified Vector Floorplan Generation via Markup** | [2604.04859](https://arxiv.org/abs/2604.04859) | no | no | 3 hits, none relevant |
| **FloorPlan-DeepSeek (FPDS)** | [2506.21562](https://arxiv.org/abs/2506.21562) | no | no | proportion only as qualitative prose (below) |

Four of these deserve their exact wording, because they are the field *noticing* the problem and
still not measuring it:

**HouseDiffusion** discusses room shape only in an ablation, verbatim:

> "Component-wise Self Attention (CSA) focuses on individual rooms and reveals a significant impact
> on the **room shape quality** in Fig. 6, causing self-intersections and 'impossible' shapes
> without it."

Its actual metrics, verbatim: *"three metrics are used for evaluations: **Diversity, Compatibility,
and Realism**. Diversity is the Fréchet Inception Distance (FID). Compatibility is the modified
Graph Edit Distance between the input bubble diagram and the one reconstructed from the generated
floorplan. **Realism is based on user studies.**"* — This answers the brief's sub-question directly:
where realism is evaluated, it is evaluated by **asking humans**, never by a shape statistic.

**The "Ergonomic Principles" paper** is the single most likely place an aspect term could have
lived — it introduces a *differentiable ergonomic loss* — and it does not. Its complete set of cost
terms, each read verbatim from the paper, is **Entrance cost**, **Kitchen cost**, **Bathroom cost**,
**Balcony cost**, and every one of them is a **Euclidean distance** between room polygons. Room
shape is not ergonomically modelled at all.

**The RLVR LLM paper (2026)** is the newest and most constraint-conscious method in the set, and it
is explicit about its own scope, verbatim: *"The RLVR optimizes only a limited set of automatically
checkable objectives."* Those objectives are exactly two — a **connectivity reward** (graph edit
distance) and a **total area reward** — plus a hard feasibility condition on invalid JSON or
overlapping polygons. Aspect ratio is *not* among them, despite being trivially checkable. Its
system prompt does say *"Your algorithm considers each room's dimensions, **proportion**, and
desired adjacencies"* — but that is prompt text, not an operationalised constraint.

**TLC-Plan** criticises a competitor for exactly the failure our rule exists to catch, verbatim:
*"Although generally box-aligned, **Graph2Plan can generate unrealistic proportions**"* — and then
does not introduce a proportion metric of its own. **FPDS** likewise says rival models "fall short
in **spatial proportion control**" while measuring none of it.

**The 2025 field review confirms the gap.** *Computer-Aided Layout Generation for Building Design:
A Review*, arXiv [2504.09694](https://arxiv.org/abs/2504.09694), §3.5 "Evaluation metrics and
experimental comparison", lists the standard metric set as: **Realism** (user studies), **FID**,
**Precision and Recall for Distributions (PRD)**, **Intra-FID**, **Graph Edit Distance**,
**IoU**, and diversity/compatibility. **No shape, proportion, aspect or compactness metric appears
in the field's standard evaluation battery.**

**NOT ESTABLISHED:** the **RPLAN** source paper (Wu et al., *Data-driven Interior Plan Generation
for Residential Buildings*, SIGGRAPH Asia 2019) could not be obtained — four candidate PDF hosts
returned HTTP errors. It is scanned here only indirectly, via Graph2Plan (same dataset, overlapping
authors, 0 hits) and the 2025 review. Also not reached: **WallPlan** (SIGGRAPH 2022) — ACM-paywalled,
no open copy found.

---

## 4. Constraint / optimisation / graph-theoretic literature

This is where aspect ratio actually lives, and the contrast with §3 is stark.

### 4.1 Shekhawat's dimensioned RFP line — aspect range as a first-class hard input

**"Automated Generation of Dimensioned Rectangular Floorplans"**, Shekhawat et al., arXiv
[1910.00081](https://arxiv.org/abs/1910.00081) (*Automation in Construction*). This is the
dimensioning half of the GPLAN line already surveyed in `room-shape-market-check.md` §5.

Verbatim, from the abstract:

> "the existence of a RFP, while **dimensional constraints are given in terms of minimum width and
> aspect ratio range for each room**. A linear optimization model is then presented to obtain a
> feasible dimensioned RFP for user-defined constraints."

Verbatim, the algorithm's Step 1:

> "Dimensional constraints are taken as an input from the user in the form of minimum width
> (w_i,min) and **the permitted aspect ratio range (AR_i,min, AR_i,max) for each room i**."

It is genuinely **hard** — the algorithm iterates until every room is inside its range. Verbatim,
Steps 3–5:

> "Width of rooms (w_i) is multiplied by lower limit of the aspect ratio (AR_i,min) to get the
> minimum height (h_i,min) of each room." … "**Step 4: Check for aspect ratio bounds and update
> minimum width.** … The aspect ratio of some of the rooms however may exceed the permissible value
> (AR_i,max) … w_i,min is updated using the following equation: w_i,min(up) = h_i,min / AR_i,max"
> … "Once the minimum width is updated, **steps 1-4 are repeated till the aspect ratios of all the
> rooms lie in between the specified range**."

**Two things matter here, and the second one is a direct hit on our design.**

1. **No default value is published.** The range is per-room and user-supplied. So this line
   establishes the *mechanism* as standard practice in constraint-based layout, but supplies **no
   number** to benchmark 3.0 or 2.0 against. Figure 5 of the paper carries the worked example's
   constraints as an image; the numbers are not in the PDF text layer. **NOT ESTABLISHED:** the
   worked example's numeric AR ranges.

2. **The paper independently derives our circulation exemption.** Verbatim:

   > "the aspect ratios are extracted from the input image for defining an approximate range for
   > each room (**adhering to these aspect ratios has a significant meaning here, as certain
   > rectangular spaces, such as circulations, have a typically distinct aspect ratio which must not
   > be al[tered]**)"

   and:

   > "The adjacency relations, as well as **aspect ratios inferred from existing RFPs have
   > architectural significance and must be preserved**"

   That is `exempt_types: [corridor, hall, storage]`, arrived at from the other direction, by
   someone regenerating real plans. Our exemption list is corroborated by an independent primary
   source. `acceptance-thresholds.md` §2.1 vindicated it empirically (corridor p90 = 3.30); this
   vindicates it *architecturally*.

**Important correction to how this line is usually cited: GPLAN itself does not carry a ratio
bound.** The 2020 dimensioning paper above enforces a true aspect *ratio*; **GPLAN** (Shekhawat,
Upasani, Bisht & Jain, *Automation in Construction* 127:103718, 2021; preprint arXiv
[2008.01803](https://arxiv.org/abs/2008.01803)) drops it. GPLAN's optimisation is a width/height
**box** only — verbatim: *"min (d_i) ≤ w(e_ji) ≤ max (d_i) ∀ i ∈ V(G)"*, *"where d is the dimension
corresponding to flow network in consideration, i.e., width for VNF and height for HNF"* — and the
only occurrence of "aspect ratio" in the whole GPLAN paper is the related-work sentence about Marson
et al. quoted in §4.2.

**This box-versus-ratio distinction is the crux of the whole question and it is worth stating
plainly.** A minimum-width plus minimum-area box does **not** imply an aspect bound: a
2750 × 8250 room satisfies both and is aspect 3.0. Michalek et al. (§4.5) are the clearest on this,
carrying a "Bound Size Constraint Group" *and* a separate "Minimum Ratio Constraint Group" precisely
because the first does not subsume the second. Several commercial products expose min-dimension
controls (§2) and those are **not** proportion controls.

### 4.2 Squarified treemaps — the aspect-minimising classical route

The `floorplan-generation-stack.md` §5.3 recommendation ("the cheapest possible v0") is built on an
algorithm whose *entire purpose* is aspect-ratio control. **"Squarified Treemaps"**, Bruls, Huizing
& van Wijk, Eurographics 2000, [win.tue.nl/~vanwijk/stm.pdf](https://www.win.tue.nl/~vanwijk/stm.pdf).
Verbatim:

> "The standard treemap method often gives **thin, elongated rectangles**. As a result, rectangles
> are difficult to compare… We propose a new method to subdivide rectangular areas, such that the
> rectangles… **approach squares**."

The mechanism is a greedy minimax on aspect, verbatim:

> "The function **worst()** gives the **highest aspect ratio** of a list of rectangles, given the
> length of the side along which they are to be laid out."

There is **no bound** — the target is 1 and the algorithm simply drives toward it. Shekhawat's
related-work section describes the architectural application (Marson & Musse, *Automatic Real-Time
Generation of Floor Plans Based on Squarified Treemaps Algorithm*, IJCGT 2010) verbatim as:

> "an algorithm for the construction of sliceable RFP such that **the rooms are generated with an
> aspect ratio close to 1**, given their areas"

and GPLAN (arXiv [2008.01803](https://arxiv.org/abs/2008.01803)) says the same, verbatim: *"Marson
et al. restricted their work to sliceable floorplans and **generated layouts having aspect ratios
close to one**, without considering the adjacency constraints."*

**NOT ESTABLISHED first-hand:** the Marson & Musse paper itself — three candidate hosts (Wiley,
Hindawi, PUCRS) all returned HTTP errors. The two characterisations above are from *other* primary
papers describing it, which is second-hand for that specific claim.

### 4.3 DPLAN — the graph-theoretic line explicitly *defers* proportion

**DPLAN: Minimal Connectivity to Floorplan Generation**, Lohani & Shekhawat, arXiv
[2606.21159](https://arxiv.org/abs/2606.21159) (2026). This matters because it shows the split is
deliberate, not an oversight. Verbatim:

> "**Separation of topology and geometry:** The pipeline focuses only on constructing a valid
> floorplan graph. **Geometric aspects such as room areas, proportions, circulation, and regulatory
> constraints are handled separately by downstream optimization or geometric solvers.**"

So in the RFP tradition, proportion is a **dimensioning-stage** concern (§4.1), consciously
excluded from the topology stage. That is exactly our architecture: ADR 0003 types the ring before
the solve, and aspect binds at the dimensioned Space.

### 4.4 VLSI / EDA floorplanning — where the numbers actually are

This is the oldest and largest literature on "pack rectangles with constraints", and it is the only
place in this survey where a **numeric** per-module aspect bound is both universal and published.
The canonical formulation, verbatim from **Adya & Markov, "Fixed-outline floorplanning: Enabling
hierarchical design", IEEE TVLSI 11(6), 2003**
([PDF](https://web.eecs.umich.edu/~imarkov/pubs/jour/tvlsi03-fixed.pdf)):

> "In a floorplanning instance, **soft blocks have a fixed area but an aspect ratio which is
> variable between certain pre-determined limits.**"

and, for their clustered instances, verbatim: *"Each top-level clustered block is soft with **aspect
ratios allowed from 0.75 to 1.5**."*

**The modal value is [1/3, 3], and it recurs independently.** From **PeF, "Poisson's Equation Based
Large-Scale Fixed-Outline Floorplanning"**, arXiv [2210.03293](https://arxiv.org/abs/2210.03293),
the constraint is one of exactly three under `s.t.`, verbatim:

> Eq. (12b): "**AR_i^l ≤ A_i/w_i² ≤ AR_i^u,  ∀ v_i ∈ V_s**"
>
> "we set **1/3 = AR_i^l ≤ h_i/w_i ≤ AR_i^u = 3** for all soft modules."

The same interval is adopted by the follow-on **Per-RMAP** work (arXiv 2406.03165 —
*"we set the aspect ratio of all soft modules with lower bound 1/3 and upper bound 3 as PeF does"*)
and, independently, by **Intel's PARSAC**, arXiv
[2405.05495](https://arxiv.org/pdf/2405.05495), verbatim:

> "In the PARSAC(soft) results we only allow a block's aspect ratio to vary in the range
> **[1/3, 3]**."
>
> "Shape constraints limit the minimum and maximum aspect ratios of blocks. We support them by
> always **clamping** aspect ratios back to these limits if they are pushed beyond them in an SA
> step."

*(PeF and PARSAC both verified first-hand by full-text scan — 40 and 21 regex hits respectively.
Note in passing that PeF also sweeps the **floorplanning-area** aspect ratio "from 1:1 to 4:1",
which is the outline quantity, not the module one — the same distinction Chen & Chang make below.)*

**The second convention, [0.5, 2], is baked into the benchmark data itself.** The GSRC soft-block
benchmark file format stores a per-block aspect interval as literal columns —
`<area> <min-AR> <max-AR>`. From `n100-2.soft`
([vlsicad.eecs.umich.edu](http://vlsicad.eecs.umich.edu/BK/CompaSS/results/INPUTS/n100-2.soft)),
verbatim file content: `1419 0.5 2`, `2405 0.5 2`, `1802 0.5 2`, … and the CompaSS results page
states it in prose, verbatim: *"**Each block has aspect ratio between 0.5 and 2.**"*

*(Verified first-hand: the file was downloaded and parsed — 101 lines, a count header of `100`
followed by 100 block rows, and **every one of the 100 rows carries the pair `0.5 2`**. So the
aspect interval is not an experimental setting someone chose; it is shipped **inside the standard
benchmark data** the whole field reports against.)*

**One distinction that must not be blurred.** Where this literature uses a *soft* aspect penalty, it
is on the **chip outline**, not the block. **Chen & Chang, "Modern floorplanning based on fast
simulated annealing", ISPD '05**
([PDF](https://cc.ee.ntu.edu.tw/~ywchang/Papers/ispd05-floorplanning.pdf)) has both, and names them
separately — the per-block bound is hard and enforced through the move set, verbatim: *"Op4: **Change
the aspect ratio of block b_i to a random value in the range of the given soft aspect ratio
constraint.**"* — while the soft penalty is on the floorplan as a whole, verbatim: *"we add an
**aspect ratio penalty** to the cost function… R is the current **floorplan** aspect ratio, R\* is
desired **floorplan** aspect ratio"*. Reading the outline penalty as a per-room preference would be
a category error.

**Bearing on our numbers.** A hard per-room bound at **3.0** is not merely defensible — it is the
**modal hard value** in the literature that has studied this problem longest, arrived at here
independently from a Swiss corpus percentile. And **2.0** is the second convention, so a tightening
to 2.0 would not be unprecedented *as a hard bound in VLSI terms*; what makes it wrong for us is
architectural (§7), not formal.

*Caveat on transfer:* VLSI blocks are circuit macros, not rooms. Nothing about a bound being right
for a standard-cell block makes it right for a bedroom. The value of this section is that it shows
**the ~2:1–3:1 band is the engineering consensus for "a rectangle that is still a useful
rectangle"** — convergent evidence, not authority.

### 4.5 Architectural optimisation — the constraint form, with our exact rationale, from 2002

Two papers state a room L/W ratio constraint outright. Neither publishes a number, which is why
§4.4 is where the numeric precedent lives.

**Michalek, Choudhary & Papalambros, "Architectural layout design optimization", *Engineering
Optimization* 34(5):461–484 (2002)**
([PDF](https://www.cmu.edu/me/ddl/publications/2002-Michalek,Choudhary,Papalambros-EO-ArchLayout.pdf)).
This is the closest thing to a direct ancestor of `dim.aspect_ratio_hard` found anywhere. The paper
separates the two constraint types by name — a **"Bound Size Constraint Group"** (Eqs. 20–22:
minimum area, minimum length/width, maximum length/width — the box) **and** a **"Minimum Ratio
Constraint Group"** (Eq. 23 — the ratio). Verbatim on why the second exists:

> "The **Minimum Ratio Constraint Group** can be used to maintain a desired aesthetic scheme or
> **prevent long, narrow Rooms that may not be usable**."

with the inequality, verbatim:

> Eq. (23): "**R_min_i · l_i − w_i ≤ 0  and  R_min_i · w_i − l_i ≤ 0**"

*(Verified first-hand from the CMU PDF.)* The surrounding equations make the box/ratio split
explicit — the Bound Size group is Eqs. 20–22, verbatim: *"A_min_i − l_i·w_i ≤ 0 **minimum area**
(20); l_min_i − l_i ≤ 0 and l_min_i − w_i ≤ 0 **minimum length/width** (21); l_i − l_max_i ≤ 0 and
w_i − l_max_i ≤ 0 **maximum length/width** (22)"* — and only then does Eq. 23 add the ratio. A paper
that already has minimum area, minimum width **and maximum width** still needed a ratio constraint
on top. That is the cleanest possible refutation of "min dimensions are enough".

**That sentence is our rule's note, written 24 years earlier.** `rules.json` says the rule exists
because *"nothing in C6's seven items catches a room that meets its minimum area and its minimum
width by being long: 2750 x 8250 is a compliant, unliveable bedroom."* Michalek says a bound-size
group is insufficient and a ratio group is needed to *"prevent long, narrow Rooms that may not be
usable."* Same gap, same fix, independently. The rule's claim to be precedent-free is not just
false — the precedent states the *reasoning*, not only the mechanism.

`R_min` is symbolic; Table I of the demonstration problem lists min area and min/max l&w only. **NOT
ESTABLISHED: any numeric `R_min` value.**

**Medjdoub & Yannou, "Separating topology and geometry in space planning", *Computer-Aided Design*
32(1):39–61 (2000)** (preprint [arXiv:1303.4017](https://arxiv.org/abs/1303.4017)). §3.1.1.2
"Setting a ratio constraint", verbatim:

> "We developed a **ratio constraint** between two variables p1 and p2. Practically, it allows to set
> **aesthetic proportions between the dimensions L and W of a space**. … In all cases, this
> constraint must be considered as a **dimensional constraint**."

It is a hard CSP constraint, propagated by arc-consistency. **NOT ESTABLISHED: a numeric L/W value**
— the paper's only worked ratio example is an *area* ratio (0.4–0.5, toilets vs. shower).

---

## 5. The one number in peer-reviewed generation that converts to an aspect — and it lands at 2.55

**Weber, Mueller & Reinhart, "A hypergraph model shows the carbon reduction potential of effective
space use in housing", *Nature Communications* 15:8327 (2024)**,
DOI [10.1038/s41467-024-52506-z](https://doi.org/10.1038/s41467-024-52506-z), preprint
[arXiv:2405.01290](https://arxiv.org/abs/2405.01290). MIT Building Technology. This is a
peer-reviewed generator that filters its own output on room shape.

The prose claims an aspect rule, verbatim:

> "a series of heuristics filter and rank feasible results (see Methods: 4.7 Apartment Validity
> Heuristic). With this, we can generate architecturally feasible floor plans where **rooms have an
> aspect ratio and size that makes them usable for their specified use**"

The implementation is not a raw aspect ratio but a **perimeter difference score**, verbatim
(Equation 1 and its caption):

> Δp = | 1 − (L_SA · L_B) / (L_A · L_SB) |
>
> "Perimeter difference score Δp, where **L_A is the perimeter of polygon A, L_SA the perimeter of
> the square polygon with the same area as A**, L_B the perimeter of polygon B, and L_SB the
> perimeter of the square polygon with the same area as B."

And the threshold, verbatim from the supplementary notes:

> "To cull floor plans with infeasible interior layout subdivisions **the authors suggest a
> perimeter difference score of 0.1 and lower**."

Their failure cases include exactly our target pathology, verbatim: *"subdivision resulting in
**foyer spaces that are too thin to be passable**"*.

### The conversion — flagged as DERIVED, not stated by the paper

Weber's Δp compares a generated room **A** against a *reference* room **B**. If B is a square, the
score collapses to the absolute compactness deficit of A. For a rectangle of aspect r, the ratio
L_S/L = 2√r / (1 + r), so **Δp = |1 − 2√r/(1+r)|**. Solving Δp = 0.1:

| aspect r | L_S/L | Δp vs a square reference |
|---:|---:|---:|
| 1.0 | 1.0000 | 0.000 |
| 2.0 | 0.9428 | 0.057 |
| **2.2** (our soft) | 0.9270 | **0.073** |
| **2.545** | 0.9000 | **0.100** ← Weber's cull threshold |
| **3.0** (our hard) | 0.8660 | **0.134** |
| 4.0 | 0.8000 | 0.200 |
| 6.0 | 0.6999 | 0.300 |

**This is my derivation from their Equation 1, not a claim they make.** Two caveats that keep it
honest: (a) their reference B is a *real reference room*, not a square, so a real Δp = 0.1 admits
shapes on either side of 2.55 depending on how elongated the reference was; (b) Δp is a *perimeter*
statistic, so it also charges for reflex corners, which a bbox aspect ratio does not.

With that said, the finding is worth the caveats: **the only numeric shape-quality threshold in the
peer-reviewed floor-plan generation literature sits at an aspect equivalent of ~2.55 — between our
soft 2.2 and our hard 3.0, and nowhere near 2.0.** Our pair of thresholds brackets the one external
number the field has.

---

## 6. Building codes — the calibration check, and it is a negative

Mainstream Anglo-American codes constrain **minimum width**, **minimum area** and **minimum ceiling
height**, and do **not** constrain proportion. Checked: IBC 2021 §1208 (room area / minimum
dimensions), IRC, NYC Building Code §1208.1 (minimum room widths) and NYC Admin §27-751 / §27-2074.
No length-to-width ratio requirement was found in any of them.

This is the finding that positions AzDTN. A 2:1 room proportion rule is **not** a general feature of
building codes; it belongs to the post-Soviet norm tradition, and — per
`az-market-default-against-practice.md` §2.3 — even there it is `tövsiyə olunur` (recommended) and
detached-house scope, not mandatory apartment law.

*Caveat:* this is an argument from absence over the codes the search surfaced, not an exhaustive
audit of world building codes. `dimensional-standards.md` owns that territory and does not currently
record a proportion rule for any of the regimes it surveys.

---

## 7. What this means for the decision

**On striking the false sentence.** `rules.json` `dim.aspect_ratio_hard.note` opens *"No surveyed
source states an aspect rule."* That is now falsified from five independent directions: AzDTN
(standards, already recorded), **Michalek et al. 2002** — which states our exact rationale as well
as the inequality (§4.5) — Medjdoub & Yannou's CSP ratio primitive (§4.5), Shekhawat's RFP
dimensioning (§4.1), and SpaceLayoutGym's shipped code (§3.1), with the whole VLSI literature behind
them. **The rule is not precedent-free, and neither is its value.**

**On the shipped 3.0.** It is now considerably better supported than it was. `acceptance-thresholds.md`
§2 defends it as the Swiss p99.5 (3.02) at a 2.85 % cost. This survey adds that **3.0 is the modal
hard per-module aspect bound in the engineering literature** — PeF, Per-RMAP and Intel's PARSAC all
use exactly `[1/3, 3]` (§4.4), and the one peer-reviewed generation threshold that converts to an
aspect equivalent lands at **2.55**, between our soft and hard values (§5). Three independent
derivations — a Swiss percentile, an EDA convention, and an MIT culling heuristic — put the boundary
of "still a usable rectangle" in the same place. **That is the strongest form of evidence available
here, and it argues for leaving 3.0 alone.**

**On tightening 3.0 → 2.0.** The honest reading is that 2.0 is *not* unprecedented as a formal hard
bound — GSRC's benchmark files literally encode `[0.5, 2]` per block (§4.4) — but three things argue
against making it *our* hard bound:

- **It contradicts our own corpus badly.** `acceptance-thresholds.md` §2.1 prices it: 2.2 is already
  the **p95**, so a hard 2.0 sits *below* the p95 of real Swiss rooms and below the **p90 of
  kitchens (2.17)** and `living_dining` (2.11), against a kitchen p99.5 of **3.63**. It would reject
  construction that demonstrably exists, which is the failure mode `rules.json` itself warns about
  for this rule ("its failure mode is rejecting good plans").
- **Its source does not ask for a hard bound.** AzDTN 2.7-3 cl. 5.1 is `tövsiyə olunur` —
  *recommended* — and detached-house scope. Every architectural source in this survey that expresses
  a *preference* targets aspect **1**, not 2 (§4.2, §3.1). A recommendation maps onto
  `dim.aspect_ratio_soft`, not `dim.aspect_ratio_hard`.
- **No building code anywhere in §6 bounds proportion at all.** Promoting a recommended clause to a
  hard reject would encode one country's guidance as a universal law, which is exactly the reasoning
  `rules.json` already uses to hold `win.glazing_ratio`'s severity down.

**The defensible reading of the evidence** is that the field's actual practice is **layered**, and
that we already ship most of those layers:

| tier | what the field does | what we do |
|---|---|---|
| **hard feasibility bound** | VLSI modal **[1/3, 3]** (PeF, Per-RMAP, PARSAC); GSRC data **[0.5, 2]**; Adya & Markov **[0.75, 1.5]**; **Magnetizing FPG [1/2, 2]**; Weber Δp cull ⇒ **≈2.55** | `dim.aspect_ratio_hard` = **3.0** — inside the band, at its **loose end**. The band runs 1.5 → 3. |
| **anti-degeneracy guard** (a *different* job) | SpaceLayoutGym `max_acceptable_aspect_ratio` = **10/20** | `dim.min_clear_width` already does this for us — **not** what 3.0 is for |
| **quality preference toward square** | squarified treemaps target **1**; JCDE targets [1, 1.5, 1.2, 1, 2, 4]; HypergraphFormer maximises compactness | `dim.aspect_ratio_soft` = 2.2 |
| **per-room / per-type range** | Shekhawat `(AR_i,min, AR_i,max)`; Michalek per-Room `R_min_i`; Tell2Design NL instructions | **we have none** — our bound is global with a type exemption list |

**The gap that opens up.** Every system in this survey that takes aspect seriously *and validates
against real plans* makes it **per-room**, not global — Shekhawat's `(AR_i,min, AR_i,max)` is
per-room, Michalek's `R_min_i` is per-Room, Tell2Design's instructions are per-room, the VLSI bounds
are per-module. The one counter-example proves the point: **Magnetizing FPG applies a single global
2.0 with no exemptions**, which would bind its corridors at 2.0 against our measured corridor
p90 of 3.30. Shekhawat's justification is precisely ours (§4.1: circulations have
a distinct aspect that must not be altered), and we already carry `exempt_types`. But our own corpus
data shows the *binding* types differ from one another too — `acceptance-thresholds.md` §2.1 has
`room*` at p99.5 = **2.33** while `kitchen` reaches **3.63**. A single 3.0 is simultaneously too
loose for bedrooms and too tight for kitchens. **If the project wants to act on this survey, the
supported move is not tightening the global number to 2.0 — it is splitting the bound by room type,
which is what every serious system in the field does and what our own fitted percentiles already
argue for.**

That would also let AzDTN's 2:1 land where it actually applies (habitable rooms, and as a *soft*
preference matching its `tövsiyə olunur` status) without imposing it on kitchens, which real
construction puts at 3.6.

**And there is a convergence here worth putting in front of whoever decides.** AzDTN's 2:1 is scoped
to **habitable rooms**. Read `acceptance-thresholds.md` §2.1's own table at exactly that scope — the
`room*` class, 97,775 rooms:

| `room*` (habitable) | p50 | p75 | p90 | **p95** | p99 | p99.5 |
|---|---:|---:|---:|---:|---:|---:|
| bbox aspect | 1.37 | 1.59 | 1.79 | **1.94** | 2.24 | 2.33 |

**AzDTN's 2:1 is the p95 of real habitable rooms** (1.94), to within rounding — and p95 is precisely
the percentile the project already chose for `dim.aspect_ratio_soft`. The 2.2 we ship is the p95 of
*all binding rooms* (2.14); restricted to the rooms AzDTN actually governs, that same percentile is
**2.0**. Meanwhile the p99.5 for habitable rooms is **2.33**, against the 3.02 all-types figure that
`dim.aspect_ratio_hard` was read off.

So the Azerbaijani norm, the Swiss corpus and the field's habit of binding proportion *per room type*
all point the same way — and none of them point at a **global** 2.0, which every kitchen in the
corpus contradicts (kitchen p90 = 2.17, p99.5 = 3.63). **The 2:1 figure is not wrong; applying it
globally is what would make it wrong.** That is the distinction the ticket should turn on.

---

## 8. Explicitly NOT established

1. **RPLAN** (Wu et al., SIGGRAPH Asia 2019) — four PDF hosts returned HTTP errors. Covered only
   indirectly via Graph2Plan and the 2025 review.
2. **WallPlan** (SIGGRAPH 2022) — ACM-paywalled; no open copy located.
3. **Marson & Musse** (IJCGT 2010) first-hand — three hosts failed. Its aspect behaviour is
   established here only through Shekhawat's and GPLAN's descriptions of it.
4. **Shekhawat's worked-example numeric AR ranges** — they are in Figure 5 as an image, not in the
   PDF text layer.
5. Whether the **Δp = 0.1** threshold in Weber et al. was itself fitted to a corpus or chosen by
   judgement — the supplement says only "the authors suggest".
6. An exhaustive audit of **world building codes** for proportion rules (§6 is an argument from
   absence over IBC/IRC/NYC).
7. **Any numeric aspect value in the architectural literature.** This is the most important gap and
   it is a real one: Michalek's `R_min`, Medjdoub's L/W interval and Shekhawat's
   `(AR_i,min, AR_i,max)` are all stated **symbolically**, with the numbers either absent or living
   in figure images that are not text-extractable. **The constraint form has architectural
   precedent; the numbers 3.0 and 2.2 have VLSI precedent only.**
8. **Laignel et al.**, *"Floor plan generation through a mixed constraint programming-genetic
   optimization approach"*, Automation in Construction 123:103491 (2021) — paywalled, no preprint.
   ⚠️ **Methodological warning recorded deliberately:** an early web search returned a sentence
   attributing "minimum width and aspect ratio range for each room" to this paper. **That is
   contaminated text — the sentence is verbatim from the Shekhawat abstract, not from Laignel.** The
   genuine Laignel abstract does not mention aspect ratio. Anyone re-running this research will hit
   the same false positive.
9. **Stamos & Stamou**, *"Automated Floor Plan Design with Constraint Optimization Using Simulated
   Annealing"* (LNCE, 2025), DOI 10.1007/978-3-031-92754-6_8 — Springer paywall, no abstract in
   Crossref.
10. **Classic architectural sources not reached at all**: Kozminski & Kinnen, Baybars & Eastman,
    Roth & Hashimshony, Steadman's *Architectural Morphology*, March & Steadman, Liggett's
    *"Automated facilities layout"* review. No open full text located; **no claim is made about
    them**, and they are the likeliest remaining home of a published architectural aspect number.
11. **Original sequence-pair, O-tree, corner block list and TCG papers** were not opened
    individually; the B*-tree per-block bound is confirmed to exist (Chen & Chang Op4) but its
    numeric range is not stated there.
12. **No open-source VLSI floorplanner with a literal per-block aspect bound in code** was located —
    the GitHub B*-tree floorplanners found all penalise the *outline* aspect ratio instead.
13. **Autodesk Forma** — public help is 27 thin pages; layout parameters live in-product or behind
    login. **Not reached**, so "absent" is weaker for Forma than for Cedreo or Snaptrude.
14. **Archistar** (Zendesk 403, product behind login), **PlanFinder** (all candidate domains dead, no
    Wayback snapshot), **Laiout** and **Spacio** (marketing pages only, no help centre or API
    reference — so their negatives rest on thin corpora). **Planner5D**'s grep was partial: Intercom
    rate-limited 268 of 328 articles, though the key Design Generator article was recovered.
15. **Whether any vendor's internal (unpublished) scoring function contains a proportion term.**
    Unknowable from outside. Finch's "Squareness" is the one published proportion control in the
    market and **its formula and weight are not documented anywhere** — the single highest-value
    remaining question in the commercial half of this survey.
16. **Whether Magnetizing FPG's `[1/2, 2]` default was fitted, inherited from the VLSI convention,
    or simply chosen.** The source carries no comment explaining the number, and the Gavrilov et al.
    paper was not obtained.
