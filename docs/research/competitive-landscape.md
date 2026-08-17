# Competitive landscape: AI / generative floor-plan and building-layout products

**Research date:** 2026-08-17
**Method:** primary sources only — vendor product sites, pricing pages, help centres/docs, terms of service, changelogs, and named-publication founder interviews. Secondary write-ups and SEO listicles are excluded or explicitly marked LOW-TRUST. Anything that could not be verified against a primary source is marked **UNCONFIRMED** rather than guessed.
**Location:** this repo had no `docs/` tree before; `docs/research/` was created for this note.

---

## 0. Naming: "Finch3D" and "Synaps" — both real, and Synaps is *not* Snaptrude

Three distinct companies with confusable names:

| Name | Real? | What it is |
|---|---|---|
| **Finch** (finch3d.com) | Yes | Swedish generative layout engine for architecture firms. Founded 2019, Malmö. |
| **Snaptrude** (snaptrude.com) | Yes | Browser-based AI-native BIM workspace. Founded 2017 by Altaf Ganihar. |
| **Synaps** (synaps.app) | **Yes — a separate, newer company** | Vienna-based "AI canvas for architects." Beta Nov 2025, v1.5 public release June 2026. |

Synaps is a genuinely distinct product, not a mangling of Snaptrude. It raised a **€3.06M / $3.6M pre-seed in April 2026** from Plug and Play and Fil Rouge, founded by Brendon Ahmeti (CEO), Agron Bajraktari and Kevin Cobaj ([TNW](https://thenextweb.com/news/synaps-3-6m-pre-seed-ai-architecture-exclusive), [EU-Startups](https://www.eu-startups.com/2026/05/if-figma-and-lovable-had-a-child-that-became-an-architect-synaps-raises-e3-06-million-to-rival-autocad/)). Both Finch and Synaps are covered in full below.

---

## 1. At a glance

| Product | Buyer | Entry price | Primary input | Output fidelity | Exports | Permit-ready? |
|---|---|---|---|---|---|---|
| **Finch** | Architecture firms (KPF, SOM, ShoP) | €79/mo solo; **€14,500/yr** enterprise floor | Massing from Rhino/Revit/Forma + firm plan library + rule weights | BIM with **generic** walls/doors needing manual swap | RVT, Rhino 2D/3D, GH stream, PDF, PNG, CSV. **No IFC, no DXF** | No — "until schematic design" |
| **Snaptrude** | Architecture firms | $60–100/seat/mo | Text prompt + RFP/code PDFs + Excel program + Revit/Rhino models | **Native Revit families** (walls, floors, columns, doors, windows, parametric stairs) | RVT, IFC 2x3/4*, DWG*, PDF, SKP, .trude→ArchiCAD, Rhino, CSV | **No — explicitly disclaimed.** LOD 250/300 |
| **Synaps** | Architects, drafters, students | Free / €59 / €119 per editor/mo | Text prompt, sketch/bubble diagram, DWG/DXF import | Editable **vector** geometry — explicitly *not* BIM | **DXF + PDF only** | No — "sketch through SD and DD", export to CD tooling |
| **Maket.ai** | **Homeowners, builders, RE pros** | Free / $20/mo | Text prompt, plan image/PDF upload | 2D plans + raster renders | PDF, DXF (contested) | **No — prohibited in ToS** |
| **ARCHITEChTURES** | Architects + developers | **$588/yr** / $3,528/yr | Plot DWG, OSM context, program table, planning coefficients | **Real IFC BIM**, LOD 200+ | **IFC, DXF, XLSX** | No — "BIM schematic design (LOD 200+)" |
| **TestFit** | **Developers**, GCs, brokers, architects | $195/mo (parking); **$15k/yr** Site Solver | Parcel/GIS boundary, zoning params, unit mix, pro forma | Parametric solved arrangement, editable "skeleton" | DXF, SVG, SKP, glTF, CSV, PDF, .tfrvt | No — but **never says so explicitly** |
| **Autodesk Forma** | Architects/planners in the design office | ~$1,445–1,500/yr (LOW-TRUST); free in AEC Collection | Site context, GIS, IFC/OBJ import, massing | "Conceptual BIM model" | **IFC 4.3 (Beta)**, OBJ, PNG, SVG, CSV | No — "conceptual", "not intended for high LOD" |
| **Digital Blue Foam** | **Cities, governments, asset owners** | Contact sales | GeoJSON/DXF/SHP site, program, FAR/setback rules | Ranked scenarios + BIM-ready massing | IFC, DXF, Revit, XLSX | No — early massing/feasibility |
| **Planner 5D** | Homeowner / DIY | Free / $59.99/yr | Draw walls, upload plan image | Renders + 2D vectors | DWG/DXF (**2D only**), IFC (**B2B API, beta**) | No — concedes CD category to CAD |
| **Cedreo** | **Home builders, contractors, remodelers** | Free / $468/yr | Draw walls, trace imported plan. **No AI at all** | Dimensioned, to-scale 2D + renders | JPG, **DXF**, PDF | No — ToU: output has **"no contract value"** |
| **RoomSketcher** | Real-estate agents, interior designers | Free / $144/yr | Draw, trace, AI Convert, LiDAR, human drafting | Scaled raster/PDF, **±2 in / 5 cm** tolerance | **JPG, PNG, PDF only** | No — explicit permit disclaimer |

\* Snaptrude's IFC and DWG export are claimed on marketing/comparison pages but are **absent from the help centre's Export collection** — treat as unverified.

---

## 2. Product profiles

### 2.1 Finch (finch3d.com)

**What it is.** "AI-native platform for building design", tagline "AI for how the world builds". Promises to "Deliver detailed floor plans, area calculations, and BIM geometry in hours, not weeks" ([finch3d.com](https://finch3d.com/)). Careers page gives the tightest definition: an "AI-powered design platform for architects" that combines "a firm's own design logic with AI to create compliant, buildable layouts in hours instead of days" ([finch3d.com/careers](https://finch3d.com/careers)).

**Buyer.** Licensed architects at large practices — "Built by architects, for the way AEC professionals actually design"; names KPF, SOM, ShoP; customers page names Dark Arkitekter and Nordic Office of Architecture ([customers](https://finch3d.com/customers)). Claims "more than 120,000 architects have joined our waitlist" ([careers](https://finch3d.com/careers)), up from "over 80,000" reported in 2023 ([AEC Magazine](https://aecmag.com/ai/finch3d-starts-to-sing/)).

**Pricing** ([finch3d.com/get-started](https://finch3d.com/get-started)): Free €0 · Basic **€79/mo** (14-day trial) · Enterprise **"from €14.500 billed annually (3 seats)"**. Everything that matters — AI floor-plan generation, firm plan library, **"Code and compliance check"**, custom BIM export, the Archie agent — is Enterprise-gated. (AEC Magazine's earlier "€49/month" figure is superseded.)

**Inputs.** Not a prompt tool. Massing volume uploaded from **Rhino via Grasshopper**, **Revit conceptual massing / walls / objects**, or **Autodesk Forma**; massing drawn natively; the firm's own "Adaptive Plan Library"; and constraint parameters ("Area Graph rules", "Passage and room width Graph rules", non-negotiables like "circulation entrance access, minimum width, and stairwell count") ([docs.finch3d.com](https://docs.finch3d.com/llms.txt)). Natural language exists only as **Archie**, an agent that operates on an *existing* model ([Archie](https://docs.finch3d.com/readme/news/ai-agent-archie.md)).

**Output — precise.** Real BIM objects, but **placeholder types**. The Revit download doc lists exactly what transfers: "Unit groups, Walls and doors, Area plans, Sheets, Furniture (2D), Room tags" — and is explicit that Finch supplies **"Generic wall types"** and **"Generic Finch doors"**, with a documented workflow requiring the user to swap in "studio standard walls" and "correct door families" ([download to Revit](https://docs.finch3d.com/courses/finch-101/finch-101-download-to-revit.md)). **Windows and levels are not listed as transferring.** Grasshopper receives *surfaces*, not solids, which the user extrudes themselves.
Documented exports: **RVT (via plugin), Rhino 2D/3D layers, Grasshopper stream, PDF, PNG, CSV**. **No IFC, no DWG, no DXF.** ArchiCAD only via Grasshopper; "MicroStation and SketchUp are not yet supported" ([FAQ](https://docs.finch3d.com/readme/faq.md)).

**Permit-ready?** No, and the vendor is equivocal rather than explicit. Co-founder Pamela Nunez Wallgren to AEC Magazine: Finch targets "early-stage design – from first sketch through design development until schematic design" ([AEC Magazine](https://aecmag.com/ai/finch3d-starts-to-sing/)). The one permit-adjacent claim — "from the first napkin sketches to the building permit" — is Jesper Wallgren in **ArchDaily, December 2019** ([ArchDaily](https://www.archdaily.com/929300/can-a-machine-perform-the-work-of-an-architect-a-chat-with-jesper-wallgren-founder-at-finch-3d)), predating the current product by ~7 years and not repeated since. Current marketing edges upward ("detailed floor plans", "buildable layouts", "compliant") without ever saying *permit* or *construction documents*. **There is no disclaimer anywhere on the site or docs.**

**Technique — well documented.** Origin is a Grasshopper "adaptive plan" script written by Jesper Wallgren at his own practice, Wallgren Arkitekter, in 2019 ([Dezeen](https://www.dezeen.com/2019/06/27/adaptive-floor-plans-wallgren-arkitekter-box-bygg-parametric-tool/)). Wallgren: **"Everything in our system is based on our Finch graph which is the logic of architecture"** — the graph "is generated automatically", the user does not build it ([AEC Magazine](https://aecmag.com/technology/finch-untethered/)). Two intelligences, "rule-based and AI" ([ArchDaily](https://www.archdaily.com/929300/can-a-machine-perform-the-work-of-an-architect-a-chat-with-jesper-wallgren-founder-at-finch-3d)). The floor-plate generator itself is **constraint satisfaction + weighted scoring, not ML**: "Each iteration is scored for how well it hits certain metrics after inputting 'non-negotiable' variables" ([algorithm theory](https://docs.finch3d.com/docs/projects-and-variants/story-editor/algorithm-theory.md)). Image generation is a bolt-on: Google's **Nano Banana**, Enterprise only.

> Correction to a common assumption: Finch is a **practice spin-out, not a research-lab spin-out**. No academic lineage found in any source.

**Code compliance & liability.** "Code and compliance check" is an Enterprise bullet; the homepage claims plans "per firm standards and local codes". But the mechanism is **user-authored graph rules** — AEC Magazine: "Users can specify requirements such as minimum square footage, daylight minimums, and spatial relationships." **No named standard (IBC, ADA, Eurocode, Swedish BBR) appears anywhere in Finch's public docs.** The [Terms](https://finch3d.com/terms) contain **no AI clause and no code/permit clause at all** — only generic "AS IS", disclaimer of "ACCURACY" and "FITNESS FOR A PARTICULAR PURPOSE", and "YOU ASSUME RESPONSIBILITY FOR SELECTING THE SERVICES AND SOFTWARE TO ACHIEVE YOUR INTENDED RESULTS".

**Funding.** €2.5M seed Nov 2022 (Inventure; angels include Peter Neubauer, co-founder of Neo4j — note the graph-database pedigree); ~€1M April 2025. Independent, no acquisition.

---

### 2.2 Snaptrude (snaptrude.com)

**What it is.** "The AI-Powered BIM software for Architects" / "The design OS for AEC" — "From brief to BIM, in one connected model" ([snaptrude.com](https://www.snaptrude.com/)). Its own sharpest self-definition: built "for the 90% of architectural work that happens **before Revit**: programming, concept design, client sign-off, and schematic development" ([blog](https://www.snaptrude.com/blog/the-90-problem-why-snaptrude-is-the-revit-alternative-architects-actually-need-in-early-stage-design)).

**Buyer.** Architecture firms, enterprise-sized. CEO Altaf Ganihar: "Our software is built to be enterprise-ready and capable of handling the proprietary intellectual property of large architectural firms such as Gensler and HOK" ([AEC Magazine, Oct 2025](https://aecmag.com/bim/snaptrude-on-ai/)). Named customers: VMDO, Studio+, Dekker Design, Clark Nexsen.

**Pricing** ([pricing](https://www.snaptrude.com/pricing)): Free $0 (3 projects, **Revit export included**) · Individual **$60/mo** · Organization **$100/mo** billed annually · Enterprise custom. Radically cheaper and more self-serve than Finch.

**Inputs — the broadest surface of any tool surveyed.** Natural-language prompt; **PDF upload of "RFP, Building Codes, Local Guidelines"** (30 MB/doc) ([AI Program Creator](https://help.snaptrude.com/en/articles/11176702-ai-program-creator-guide)); Excel/CSV program tables; site polygon drawn in-app; CAD import; **native Revit model upload** (Direct Revit Import shipped v3.51.0, Apr 2026); Revit RFA families; Rhino models.

**Output — the best object fidelity in the set.** "Walls, floors, slabs, columns, doors, windows, etc are imported as the respective families on Revit"; stairs arrive as "cast-in-place stair in Revit with editable parameters such as riser width, riser height, tread depth, base level, base offset"; floor labels convert to Revit room tags ([import to Revit](https://help.snaptrude.com/en/articles/9626028-import-snaptrude-model-to-revit)). Documented: **RVT (bidirectional round-trip), PDF, SKP, .trude→ArchiCAD, Rhino, CSV**. IFC 2x3/IFC4 and DWG are claimed on comparison pages but **absent from the help centre's export docs** — unverified.
Sheets exist but are presentation-grade: the entire Documentation collection is 5 articles, with **no articles on dimensioning, annotation systems, title blocks, or schedules** ([Documentation](https://help.snaptrude.com/en/collections/10596947-documentation)).

**Permit-ready?** **No, and Snaptrude says so in writing** — the cleanest disclaimer in the professional tier:

> "No. Snaptrude is designed for the early stages of architectural design: programming, concept, and schematic development. **When you're ready for construction documentation, Snaptrude exports cleanly to Revit.**"
> — [snaptrude.com/blog](https://www.snaptrude.com/blog/the-90-problem-why-snaptrude-is-the-revit-alternative-architects-actually-need-in-early-stage-design)

Reinforced on the Revit comparison page: "Most architecture teams use Snaptrude for early-stage design and Revit for construction documents" ([vs/revit](https://www.snaptrude.com/vs/revit)). Ceiling stated by the CEO as an **"LOD 250/300 'ish' model"** ([AEC Magazine](https://aecmag.com/bim/snaptrude-on-ai/)). The 70+ published workflows contain **no construction-document, permit-set, or detailing workflow** ([workflows](https://www.snaptrude.com/workflows)).

**Technique.** Ganihar directly: **"Some of them are LLM. Some of them are not LLM. Some of them we had to build, ones that use physics and climate-aware models… It's a combination of AI modules… They're all run by this master AI which figures out which one to use and when"** ([AEC Magazine](https://aecmag.com/bim/snaptrude-on-ai/)). Nine named agents in-product (Design, Research, Charts, Interpret, Site Analysis, Generate Program, Update Program, Assign Dimension, Assign Stories) ([AI agents](https://help.snaptrude.com/en/articles/14004374-ai-agents-in-snaptrude)); no underlying model vendor is named. Renders/video use Nano-Banana and Veo 3. A from-scratch browser BIM engine — **no Grasshopper or Rhino Compute dependency**; Rhino is an interop target.

**Code compliance & liability — the sharpest marketing/contract gap in the set.** Marketing: "AI reads RFPs, analyzes sites, and **generates compliant massing** in minutes" ([for-firms](https://www.snaptrude.com/for-firms)); "Auto-adjacencies from building codes" (homepage). CEO: the AI produces something that "looks at zoning codes, building codes, and takes into account the climate" and "complies with zoning/building codes" ([AEC Magazine](https://aecmag.com/bim/snaptrude-on-ai/)).
But the mechanism is **user-supplied PDFs fed to an LLM**, not a curated code database. The AI Adjacency and Smart Layouts docs make no compliance claim. **No named code (IBC, ADA, NFPA, local zoning) is documented as built-in.**
Meanwhile [Terms](https://www.snaptrude.com/terms) §10.4:

> "Any AI-powered features and tools that we offer are only designed to **assist** you. These features and tools **may not always provide accurate, complete, or current suggestions and information. You are solely responsible for verifying the accuracy and suitability of such features and tools before relying on them.**"

**Funding.** $6.6M seed + **$14M Series A** led by Foundamental with Accel participating ([press](https://www.snaptrude.com/press)). No Series B found; press page has no items after Jan 2023.

---

### 2.3 Synaps (synaps.app)

**What it is.** "Architectural practice without the compromise" — a browser-based, multiplayer AI drafting canvas explicitly positioned as **the gap between AutoCAD and BIM**, not as BIM. The company page states the philosophy outright: **"BIM thinking without the BIM tax"** ([company](https://www.synaps.app/company/)). Press framing: "If Figma and Lovable had a child that became an architect."

**Buyer.** Segmented on-site into Architecture Studio, Interior Designers, Freelancers & Homeowners, Real Estate Professionals, Students & Educators. Press framing targets "the estimated 200 million drafters worldwide" ([Trending Topics](https://www.trendingtopics.eu/viennas-synaps-raises-3-6m-pre-seed-to-build-ai-canvas-for-architects/)). Homepage claims "Trusted by 80,000 architects worldwide."

**Pricing** ([synaps.app/pricing](https://www.synaps.app/pricing/)): Freemium €0 (300 signup credits + 30/day, 3 models/pages/editors) · **Pro €59 per editor/mo** (4,500 credits/mo rolling, **DXF import and export**, watermark-free) · **Studio €119 per editor/mo** (unlimited credits, 50 editors, "Opt out of data training"). Billed per *active editor*, viewers free — a deliberate jab at Autodesk named-user licensing.

**Inputs.** Text brief ("site dimensions, required rooms, adjacencies"); **a sketched bubble diagram or rough massing** used as "a soft constraint… a directional prior, not a template"; DWG and DXF opened directly with "geometry, layers, and dimension styles preserved" ([FAQ](https://www.synaps.app/faq/)).

**Output — precise.** Vector geometry, and the vendor is emphatic it is not an image:

> "Describe the constraints, site dimensions, required rooms, adjacencies, and get **three to twelve plan options as real, editable geometry, not an image**. Treat it as the starting point a junior would have handed you."
> — [floor plan generation](https://www.synaps.app/solutions/floor-plan-generation/)

Exports: **DXF and PDF.** No IFC on the pricing feature matrix; "Revit projects are imported as **reference geometry** today; full RVT round-trip is on the roadmap" ([FAQ](https://www.synaps.app/faq/)). The June 2026 changelog mentions "DWG and IFC round-trip" for office libraries ([changelog](https://www.synaps.app/news/changelog/)), which conflicts with the pricing page listing only DXF — **treat IFC as UNCONFIRMED**.

**Permit-ready?** **No — and the FAQ answers are unusually candid about the boundary:**

> "Synaps is fastest from sketch through **SD and DD**; once geometry is locked, **you can export DXF/PDF into your CD tooling** or keep refining inside Synaps. We are extending issue-set support release by release."
> — [architecture studio](https://synaps.app/solutions/architecture-studio/)

> "Does the generator handle structural feasibility or just spatial fit? It reasons about spatial fit, adjacencies, light, and circulation. **It does not size beams or check spans** — assume it gives you a viable layout to study with a structural engineer, **not a structurally vetted plan.**"
> — [floor plan generation](https://www.synaps.app/solutions/floor-plan-generation/)

**Technique.** A proprietary named model, **Vecy-1**: "our proprietary SOTA floor plan generation model achieves best-in-class benchmark performance in geometric validity, coherence, and spatial reasoning." No benchmark, dataset, or architecture is published — **UNCONFIRMED** whether this is diffusion, autoregressive, graph-based, or a hybrid. The company also claims "trained on architects' behavioural patterns" cutting commands by 80%.

**Code compliance & liability.** No code-checking feature is claimed anywhere. The [Terms](https://www.synaps.app/terms/) contain a striking clause:

> "**The Services are not tailored to comply with industry-specific regulations so if your interactions would be subjected to such laws, you may not use the Services.**"

Plus standard "AS IS", full indemnification of Synaps by the user, and no professional-liability carve-out.

**Maturity flags worth noting.** The footer "Documentation" link points to `docs.synaps.com`, which **does not resolve**; `docs.synaps.app` returns an empty GitBook shell. The FAQ quotes **€35/€75** per editor while the pricing page says **€59/€119**. The FAQ says "We do not train models on customer drawings" while the pricing page sells "Opt out of data training" as a Studio-tier feature. These are stale-marketing inconsistencies, not product claims, but they indicate a very young product behind a polished site.

---

### 2.4 Maket.ai

**What it is.** ToS gives the most precise self-description: "an AI-powered platform that helps you generate and visualize architectural ideas, including floorplans, layouts, and 3D renderings… **designed to support creativity, exploration, and early-stage planning**" ([terms](https://www.maket.ai/legal/terms-and-conditions)). Note: Maket has **repositioned** from a professional generative-design tool to a consumer-first "AI home design app".

**Buyer.** "**Homeowners, builders, and real estate professionals**"; "Anyone can design a home" ([maket.ai](https://www.maket.ai/)). Explicit non-replacement stance: "AI floor plan tools are designed to work alongside professionals, not replace them" ([floor plan generator](https://www.maket.ai/ai-floor-plan-generator)).

**Pricing** ([pricing](https://www.maket.ai/pricing)): Free $0 (50 credits/mo) · Plus **$20/mo** (300 credits, up to 4 floors) · top-ups from $10/150 credits. **20 credits per floor plan, 10 per render** — so free tier is ~2 plans/month.

**Inputs.** Text prompt; upload of an existing plan (image or PDF); manual drawing; templates; style references; conversational edits. No site polygon, GIS, or structured program table found.

**Output.** Editable 2D floor plans + raster 3D renders. **No BIM, no IFC.** Export is contested: `/ai-floor-plan-generator` lists PDF and DXF; `/features` says DWG/DXF export is **"coming soon"** — **UNCONFIRMED**.

**Permit-ready? No — the hardest prohibition in the entire survey, and it is in the binding contract:**

> "**All AI Outputs are provided for conceptual purposes only. They do not constitute technical drawings and cannot be used for construction, permitting, or regulatory approval.**"
> "Maket is not an architect, engineer, contractor, or construction professional."
> "Maket does not verify… measurements, dimensions, or scale; site conditions or land constraints; structural integrity or load-bearing requirements; electrical, plumbing, HVAC, or mechanical systems; material specifications or engineering requirements; **building code compliance; zoning restrictions; permit requirements**; or construction feasibility or safety standards."
> "**You must not rely on Maket outputs for construction, permitting, regulatory approval, engineering, or safety decisions unless they have been reviewed and approved by a licensed professional in your jurisdiction.**"
> — [terms](https://www.maket.ai/legal/terms-and-conditions), §2

Note the internal collision: marketing promises "realistic, **to-scale** layouts" and "accurate dimensions"; the ToS says Maket does not verify "measurements, dimensions, or scale."

**The zoning feature is an LLM document Q&A, not a geometric check.** The user uploads a zoning document (JSON, HTML, TXT, PDF, ZIP) and then asks questions about it; the system answers "based on your specific document" ([blog](https://www.maket.ai/post/makets-zoning-regulations-simplifying-zoning-compliance)). **It never touches the generated geometry.** The feature is absent from the current `/features` page — possibly legacy. Liability capped at 12 months of fees, i.e. ~$240 max.

---

### 2.5 ARCHITEChTURES (Smartscapes Studio)

**What it is.** "A generative AI-powered building design platform to help design optimal residential developments in minutes, rather than months"; "generates in real-time a BIM model with the geometry resulting from the AI-aided design process" ([architechtures.com](https://architechtures.com/en)). Scope limit: **multi-family residential only** (plus hotels, in-building commercial, subway parking garages) ([what is](https://architechtures.com/en/blog/posts/t1-what-is-architechtures)).

**Buyer.** "Used by **architects and real estate developers** to optimize the feasibility analysis process with regulatory confidence" (homepage).

**Pricing** ([pricing](https://architechtures.com/en/pricing)): Pro **$588/yr** ($49/mo billed yearly, annual only) · Business **$3,528/yr** ($294/mo) · Enterprise custom. **Exports (XLSX, DXF, IFC) are included at the entry tier** — no export paywall. This is the only credit-card-purchasable IFC-output product for architects in the survey.

**Inputs — the richest structured input set.** Plot geometry via **DWG upload** or manual drawing; OpenStreetMap site context and topography; urban-planning coefficients (buildability, building coverage, GFA deduction) typed in by the user; a full program table (net areas and minimum dimensions per room per typology, housing mix, room heights, core configuration); manual massing; cost presets. **No text prompt** — this is a structured-parameter tool.

**Output — genuinely BIM.** "A .IFC file importable into any BIM editor or viewer", with construction-element thicknesses matching user inputs, "construction families", and rooms generated as objects "usually used as a starting point to generate take offs and estimates". Plus a **DXF per floor** (each building, each basement, plus a ground-floor general plan) and an XLSX with area schedules, housing mix, per-dwelling metrics and a full construction cost estimate ([downloads](https://architechtures.com/en/blog/posts/9-downloads-automated-bim-and-cad-without-revit-autocad)). **No DWG export (import only), no RVT.** Whether the DXF carries dimension annotations is **UNCONFIRMED**.

**Permit-ready?** No — and it names a precise level, which is more honest than most: "feasibility studies and **BIM schematic design (LOD 200+), i.e. basic project**", after which users "download the BIM model and IFC standard to continue developing the project by adding furniture, MEPS, and construction details" ([what is](https://architechtures.com/en/blog/posts/t1-what-is-architechtures)).

**What "regulatory confidence" actually means — a user-parameterised violation tracker.** From the vendor's own explanation ([regulation compliance](https://architechtures.com/en/blog/posts/regulation-compliance-in-architechtures)):
1. **The user enters the regulations.** There is no code database.
2. "For each iteration, the AI offers a building that complies with all the data provided."
3. On manual edits, "the data panel allows to track the **violations** that may have been committed" — a tracker, not an enforcer.
4. No jurisdiction library; **no specific code (IBC, CTE, Eurocode) is named anywhere.**
5. And explicitly: **"ARCHITEChTURES is not a substitute for the designer… The design is decided by the user and the designer is responsible for compliance with regulations."**

This is real *geometric* constraint satisfaction against numbers the user typed — materially stronger than Maket's LLM Q&A, materially weaker than "code checking".

**Technique.** Founder Juan Bordallo: "The platform uses GenAI to generate in real-time the geometry that best fits the design objectives… based on a proprietary training process called **self-generative learning**, whereby the system can autonomously learn to design endless building typologies variations" ([World Architecture, Jun 2024](https://worldarchitecture.org/architecture-news/fhzpv/ai-can-amplify-human-creativity-and-capabilities-argue-ai-experts.html)). The vendor positions itself explicitly **against** evolutionary/generative search: "Generative solutions suffer more and more as complexity increases until they become so cumbersome that they are no longer viable" ([blog](https://architechtures.com/en/blog/posts/parametric-design-generative-design-and-ai-aided-design)).

**Liability.** Thin. The [Terms](https://architechtures.com/en/terms-and-conditions) say only that SMARTSCAPES "cannot be held responsible for issues related to the content of documentation and/or designs generated or modified by Architechtures, as well as the final destination of the same." **No clause on code compliance, permitting, or professional liability.** The responsibility statement lives in a blog post, not the contract.

---

### 2.6 TestFit

**What it is.** A "**Real Estate Feasibility Platform**" — "Automate Site Plans. Accelerate Decisions." Modules: Site Solver, Parking Solver, Site Intelligence, Pro Forma, MCP Connection ([testfit.io](https://www.testfit.io/)). Historically branded a "building configurator."

**Buyer.** Developers, architects, contractors, civil engineers, planners, brokers. The JTBD for architects is removing drudgery, not designing: "TestFit automates the tedious tasks like counting parking stalls, so you get to design, not count" ([roles/architects](https://www.testfit.io/roles/architects)). The deal-screening line: "From Parcel to Pro Forma in Minutes."

**Pricing** ([pricing](https://www.testfit.io/pricing)) — note the **per-seat model is gone**, replaced by module pricing with unlimited users: Parking Solver **$195/mo** · Site Solver **from $15,000/yr** · Site Solver Portfolio **from $20,000/yr**. Add-ons: Site Intelligence +$150/mo, Pro Forma +$170/mo, MCP Connection +$100/mo.

**Inputs.** Parcel boundary by address/GPS from public GIS, or drawn, or imported as **DXF/DWG/Shapefile/KML**; ArcGIS/FEMA/wetlands/SSURGO layers; zoning parameters from the **Zoneomics** integration or entered manually; unit mix and "kit of parts" importable from Revit; stairs/firewalls/elevators as parameters; land/hard/soft costs. **Text prompt: yes, via the MCP Connection add-on** — "Connect your AI assistant via MCP so you can prompt buildable outcomes that are directly editable inside TestFit."

**Output.** A parametric solved arrangement, editable via "Manual Mode… converting it into an editable skeleton" ([help](https://support.testfit.io/knowledge/getting-started/manipulating-buildings)). **Not native BIM.** Documented exports: **PDF, layered DXF, SVG, SKP, CSV, glTF, .tfrvt** (a proprietary handoff file for the Revit add-in), .rsd ([exporting data](https://support.testfit.io/knowledge/getting-started/exporting-data)). **No DWG out, no IFC, no Rhino/3DM, no Grasshopper plugin.** Ships a parking-configurator **extension inside Autodesk Forma** as a WebAssembly module.

**Permit-ready?** Concept-only in practice, but **TestFit never says so.** The strongest primary evidence is workflow framing:

> "Once the deal turns into a real project **after the real estate feasibility phase**, all the data and models can be exported into other platforms, such as AutoCAD, Revit, and Excel, **to continue design development**."
> — [blog](https://www.testfit.io/blog/real-estate-feasibility-workflow)

⚠️ Several SEO review sites circulate a polished line — "TestFit generates feasibility-level geometry, not construction documents" — that **could not be traced to any TestFit-authored page**. Do not cite it.

**Technique — confirmed *not* ML.** Clifton Harness to AEC Magazine:

> "**TestFit is commonly assumed to be based on AI. In fact, it's mostly not AI at all.**"
> "At its heart, TestFit is a **massive parametric solving engine**."
> "It's **purposely not referring to this as 'AI'**. Instead, it's a goals-based solver."
> — [AEC Magazine](https://aecmag.com/software/testfit-runs-free/)

Corroborated architecturally: the solver compiles to a **WebAssembly module running client-side** ([Autodesk APS](https://aps.autodesk.com/blog/use-open-forma-api-add-custom-extensions-and-contextual-data)). Architect Magazine ran a Q&A headlined "TestFit CEO Clifton Harness Has Some Reservations About His Successful Generative Design Tool" — which TestFit links from its own newsroom.
**But the positioning has since flipped:** current marketing says "an AI-generated plan you can edit", "Real-Time AI", "groundbreaking AI tool". The engine is very likely unchanged; the marketing rebranded.

**Code compliance & liability — the biggest risk/cover mismatch in the survey.** TestFit ingests permitted land uses, max FAR, max coverage, setbacks and building height, and provides **"a pass/fail score with each scheme to ensure compliance"** — a compliance verdict, on **third-party Zoneomics data**, with **no caveat and no advice to verify with the municipality** on that page ([zoning data](https://www.testfit.io/blog/zoning-data)).
Against that, the [Terms](https://www.testfit.io/legal/terms-of-service) offer only generic cover: §10.3 "AS IS" and no warranty that results "will meet Customer's… requirements… ACHIEVE ANY INTENDED RESULT… BE SECURE, ACCURATE, COMPLETE"; §9.5 pushes third-party-data risk entirely to the customer ("IT IS YOUR SOLE RESPONSIBILITY TO UNDERSTAND AND PROTECT YOURSELF AGAINST RISKS ASSOCIATED WITH USING THIRD-PARTY MATERIALS" — this is the clause carrying the Zoneomics zoning data); **§12.2 caps liability at the greater of US$5,000 or 12 months of fees.** There is **no professional-judgment clause**.

---

### 2.7 Autodesk Forma (formerly Spacemaker)

**Naming update, important:** "Forma" is no longer one product. There is **Forma Site Design** (the Spacemaker successor and the true TestFit competitor), **Forma Building Design** (launched Sept 2025, "a pioneering cloud-based solution for **schematic design**… bridging the gap between concept and BIM"), and **Forma Data Management** (the old BIM Collaborate line), plus Forma Board/Takeoff/Estimate/Build ([Autodesk blog](https://blogs.autodesk.com/forma/2025/09/16/introducing-forma-building-design/)). Comparing "Forma" to TestFit without saying which Forma compares the wrong things.

**Buyer.** Architects and planners in the design office, at conceptual design and site planning. Forma Building Design targets "project leaders, CAD, and BIM architects" plus "non-BIM contributors". Contrast the JTBD: Forma's outcome variable is design quality, environmental performance and carbon; TestFit's is yield, unit count, parking ratio and yield-on-cost. Different budgets — Forma sells to the design office, TestFit to acquisitions.

**Pricing.** ⚠️ **Could not be confirmed from primary source.** Autodesk renders prices client-side (the markup contains only `{{price.FORMBLDDES.1year}}`-style template variables) and `autodesk.com` 403s automated fetching. Confirmed from Autodesk: monthly / 1-year / 3-year terms, annual saving 33% over monthly, 30-day free trial. **LOW-TRUST third-party figures:** ~$185/mo, ~$1,445–1,500/yr; AEC Collection reported at $3,675/yr **with Forma Site Design included at no extra cost**. If accurate, Forma Site Design is an order of magnitude cheaper than TestFit Site Solver — TestFit is competing on the pro-forma/underwriting layer, not on geometry.

**Inputs.** Cloud-delivered site context (terrain, existing buildings); **ArcGIS for Autodesk Forma** (Esri partnership, June 2025); **IFC and OBJ import**; massing objects (3D sketch, basic/line buildings, houses, constraints, vegetation, roads, parking). **Zoning ordinances as a structured input are not documented — UNCONFIRMED that Forma ingests zoning at all.** Text prompt is emerging via **Neural CAD** and **Project Forma Sketch**.

**Output.** Documented exports: **OBJ, IFC (Beta), PNG, SVG, CSV**. IFC is **4.3**, exported per-proposal into Autodesk Docs, and Autodesk's own phrasing is *"the **conceptual** BIM model"*. **No glTF, no RVT file export.**
The Revit interop is the strong point and is genuinely deep — the Forma Add-in for Revit converts Line Buildings into **real Walls, Floors and Roofs**, terrain into **Toposolids**, parking into **Revit Parking Families**, with georeferencing preserved, and supports a reverse "Update Proposal" push ([Forma meets Revit](https://blogs.autodesk.com/forma/2023/11/07/forma-meets-revit/)). Documented limits: "you can only send a Forma proposal to Revit **once**"; Zones, Railroads, Generic Surfaces/Lines not supported; "Testfit parking is currently not supported".

**Permit-ready?** **No, and Autodesk documents the limit more explicitly than anyone else.** IFC export is of "the *conceptual* BIM model"; the blog frames the whole product as what you use "before it's time for BIM"; Autodesk guidance is that "Forma is not intended for high LOD models"; and **Building Layout Explorer — the generative floor-plan feature — is labelled "an experimental feature"** with the caveat "we recognize some outputs will be more useful than others as [it] continues to evolve" ([Autodesk newsroom](https://adsknews.autodesk.com/en/news/building-layout-explorer-in-autodesk-forma/)). Even Forma Building Design is scoped to *schematic design*.

**Technique — the only genuinely-ML-substantiated claim in the set.** Two tiers, ML surrogate for speed and real simulation for verification:
- **Rapid wind analysis** — "Using machine learning, this new easy-to-use tool complements our existing wind analysis… which gives exact results for verification." Autodesk calls the ML model a **"surrogate"** and **continuously retrains it** from usage of the detailed analysis ([Autodesk blog](https://blogs.autodesk.com/forma/2023/06/06/formas-rapid-wind-analysis-offers-instant-insights-into-wind-conditions/)).
- **Rapid noise analysis** — "Through machine learning, we use a dataset of **tens of thousands of noise simulations** to train a neural network to predict ground noise results"; rapid "makes an educated guess", standard "provides the accurate calculations" ([Autodesk blog](https://blogs.autodesk.com/forma/2023/07/03/game-changing-rapid-noise-analysis-comes-to-forma-2/)).
- **Building Layout Explorer** — "powered by generative AI models trained on aggregated 3D AEC data."
- **Neural CAD** — Mike Haley (SVP Research): "As the architect directly manipulates the shape, the neural CAD engine responds to these changes, auto generating floor plan layouts"; AEC Magazine's assessment: "it's still very early days for neural CAD" ([AEC Magazine](https://aecmag.com/features/autodesk-shows-its-ai-hand/)).

Whether sun-hours/daylight/solar and embodied carbon are simulation or surrogate is **UNCONFIRMED** (`help.autodesk.com` returned 503).

**Code compliance & liability.** Forma makes **no zoning or building-code compliance claim** that could be confirmed — it sells environmental analysis, not a compliance verdict. Its regulatory exposure is therefore materially lower than TestFit's. And its contract has a *purpose-built* professional-judgment clause that TestFit lacks:

> "The Offerings are tools and are intended **only to assist You** with Your design, analysis, simulation, estimation, testing and other activities and **are not a substitute for Your professional judgment** or Your own independent design, analysis, simulation, estimation, testing, or other activities, including, for example, those with respect to product stress, safety and utility."
> — [Autodesk General Terms](https://www.autodesk.com/company/terms-of-use/en/general-terms) (retrieved via search index + an Autodesk-authored PDF mirror; section number 11.1 is **UNVERIFIED**, the language is corroborated across two retrievals)

---

### 2.8 Digital Blue Foam — live, but pivoted out of this market

**Not shut down; repositioned.** DBF launched in 2022 as a SaaS building-design platform for "architects, planners, BIM managers, real estate developers, and construction managers" ([Architosh, Jan 2022](https://architosh.com/2022/01/digital-blue-foam-launches-for-soaring-ai-aec-market/)). Its 2026 headline is **"Your spatial reasoning layer for every asset decision"** — "AI city-planning software" turning "spatial data into ranked scenarios", sold to **cities, governments, large asset owners and facility operators** ([digitalbluefoam.com](https://www.digitalbluefoam.com/)). Named logos include Takenaka, Jacobs, Emaar, McKinsey, **Dubai Municipality**, EGIS, MODON.

**Pricing.** No public numbers. Academic/Pro is a **waitlist**; Enterprise/Gov is "Contact sales" with eligibility "Government & Organizations with 1,000+ ppl" ([pricing](https://www.digitalbluefoam.com/pricing)). DBF Mass reportedly offers a 14-day trial, but self-serve purchase is **UNCONFIRMED**.

**Inputs.** The only true GIS ingest in the survey: site boundaries as **GeoJSON, DXF, SHP**; footprints drawn on a map; 3D constraints as OBJ/FBX; IFC import; regulatory rules including FAR, setbacks, **shadow laws**, and clinical adjacency rules.

**Output.** **Ranked scenario sets with KPI scoring and "evidence chains" tracing each recommendation back to source rules/data** — a distinctive output no competitor offers. Plus 3D massing, real-time GFA/FAR/coverage metrics, and BIM: "100% IFC Compatible", "One-Click BIM Integrations", syncing to **Revit, ArchiCAD, Grasshopper**. Exports: IFC, DXF, Revit, Excel. IFC schema version, LOD, and object typing are all **UNCONFIRMED**.

**Permit-ready?** No — "early-stage decisions", "early massing studies". FAQ: "We recommend reviewing outputs with your team before final submissions." The **DBF Hikari** SKU carries the strongest regulatory claim in the whole survey — it "generates and ranks unit configurations against **hard constraints**" with "**an evidence chain back to each rule it satisfies**", with zoning compliance for specific regions **including Japan** (FAR, setbacks, 日影規制 shadow regulations). This is the only claim of *jurisdiction-specific encoded rules* found anywhere — but it is confined to one SKU in one country and is thinly documented.

**Liability.** The [Terms](https://www.digitalbluefoam.com/terms-and-conditions) contain **no clause at all** on code compliance, professional liability, output accuracy, or fitness for construction. A separate enterprise MSA almost certainly exists but is not public.

---

## 3. The consumer / SMB tier

All three of Planner 5D, Cedreo and RoomSketcher stop at exactly the same wall, and all three describe the wall the same way: *go hire an architect.*

**Planner 5D** — homeowner/DIY. Free / $59.99/yr Premium / $399.99/yr Professional. Concedes the category in its own words: **"Traditional CAD software is better for detailed technical drawings and construction documents"** ([architecture-design-software](https://planner5d.com/use/architecture-design-software)). CAD export (Pro tier) is **DWG/DXF 2D only** — "we currently do not have an option to export it in 3D". **IFC exists but only via the B2B API and is in beta** — the only IFC path anywhere in the consumer tier, and not self-serve. Its "AI Studio" is candidly a wrapper over third-party image models (Nano Banana 1/2, GPT Image 1.5/2, Seedream 5 Lite, Veo 3.1, Kling): pixels in, pixels out, no geometry. ToS mentions "building code" zero times; liability capped at the greater of $750 or 12 months of fees.

**Cedreo** — home builders, contractors, remodelers. Free / $59 per project / $468/yr Pro / $708/user/yr Enterprise. **Zero occurrences of "AI" on the homepage** — the only non-AI vendor surveyed, and notably the only one selling primarily to people who actually build houses. Output is genuinely dimensioned and to scale (multiple named scales, custom annotations, automatic surface-area tables), exporting **JPG, DXF, PDF**. Marketing claims "detailed **construction documents**"; the contract says otherwise:

> **Art. 3.1:** "CEDREO software is a **sales assistance tool** designed to render an internal and external representation of a home."
> **Art. 3.3:** "These visualizations **have no contract value**. CEDREO does not provide any guarantees with regard to the feasibility of the project. **The User is solely responsible for validating the technical details** of the visualization rendered."
> **Art. 16.2:** "**The User shall be solely liable for the use and interpretation of rendering, visuals or plans generated** and for the actions and advice that it derives from the same."
> — [cedreo.com/terms-of-use](https://cedreo.com/terms-of-use/)

That is the single most important sentence pair in this research set: the vendor marketing "construction documents" hardest is contractually a *sales tool whose output has no contract value*. (The Terms page is not in the site's sitemap; it is reachable only from the signup form.)

**RoomSketcher** — real-estate agents (RE/MAX, Keller Williams) and interior designers. Free / $144/yr Pro / $420/yr Team, plus à-la-carte credits ($20/level AI Convert, $20/level LiDAR, $38/level human-drawn plans). Its **AI Convert** (image/PDF → editable geometry, "trained on real floor plans") is the most substantive AI in the consumer tier precisely because its output is *geometry*, not pixels. But **exports are JPG, PNG, PDF only** — a help-centre search for "DWG DXF CAD AutoCAD" returns "No results". No vector, no IFC, no RVT.
It is the only vendor anywhere in this survey to name **measurement standards (GTA, GFA, GLA, GIA)** and to publish a **quantified accuracy tolerance**:

> "Measurement Accuracy — Floor plans are drawn as close to the provided measurements as possible, with a **margin of error of approximately +/- 2" (5 cm)**. Measurements are calculated from the center of each wall."
> — [delivery terms](https://help.roomsketcher.com/hc/en-us/articles/4410169574417-What-is-Included-in-My-Floor-Plan-Order-Here-are-our-Delivery-Terms-and-Conditions)

±2 inches is fine for a listing and disqualifying for construction. That is the honest quantification of the gap. Its permit disclaimer is the plainest anywhere:

> "**Can I use the floor plan for building permits?** While our floor plans are professional and detailed, **we can't guarantee they meet the requirements for building permits**, as these vary widely depending on local regulations. **We recommend consulting a licensed architect or building professional** to ensure your plans comply with the relevant codes and standards in your area."

**Structural observation:** AI marketing intensity in this tier is *inversely* proportional to how construction-serious the buyer is. Cedreo, selling to builders, mentions AI zero times. Planner 5D, selling to homeowners, leads with "AI-powered."

---

## 4. Notable 2025–2026 entrants

### The permit-ready claim is being made — but only by narrowing scope drastically

Two companies claim permit-ready output, and neither does it by claiming better models:

- **Genia** ([genia.design](https://www.genia.design/)) — "export **permit-ready structural drawings** in CAD or BIM formats with detailed calculation sheets and material take-offs"; layouts "validated through detailed structural calculations following the relevant building codes." **Structural discipline only**, consuming architectural input. $3M pre-seed, Feb 2025.
- **Higharc** ([higharc.com](https://www.higharc.com)) — "**permit-ready construction documents**", auto-regenerated per lot when the plan or a buyer selection changes. **Production homebuilding only.** **$95M Series C, 30 June 2026** — by far the largest raise in this scan.

### A fast-growing adjacent segment sells *compliance checking* rather than generation

- **Kestrel Labs** ([kestrellabs.com](https://kestrellabs.com)) — "the first compliance platform built natively inside the BIM workflow… putting **jurisdiction-specific code requirements inside Autodesk Revit**, before drawings reach plan review." $2.15M pre-seed, June 2026.
- **Permitify** (YC W2025, [permitify.com](https://permitify.com)) — pre-submittal AI plan review, **$297 flat per plan set**, "Every finding cited to the code & sheet."
- **Structured AI** (YC F2025) — QA/QC across drawing packages, PDF and native Revit.

### Others, one line each

| Company | What it does | Sells to | Output | Permit claim |
|---|---|---|---|---|
| **Swapp AI** ([swapp.ai](https://www.swapp.ai/)) | Automates Revit/ArchiCAD documentation; agentic ADA checking | BIM leads at deadline-driven firms | "Complete CD sets — dimensions, tags, views, sheets", native RVT | Strong CD claim; **never says "permit"** |
| **Motif** ([motif.io](https://www.motif.io)) | AI design workspace, 2D+3D review/markup. **$46M Jan 2025**; ex-Autodesk CEO + the Revit/AutoCAD team | Firms on Revit/Rhino | AI raster visuals; live model streaming | ❌ review layer only |
| **qbiq** ([qbiq.ai](https://qbiq.ai)) | AI test-fit / space planning. **$16M Series A (Insight), Jan 2025** | CRE — landlords, brokers, tenants | 2D plans, 3D tours, "Revit & CAD models — fully structured, editable", takeoffs | ❌ conceptual, architect in the loop |
| **Hypar** ([hypar.io](https://docs.hypar.io)) | Generative space planning on a custom geometry kernel | Architects/engineers doing test fits | PDF, images, Excel, native Revit, Rhino | ❌ positions as the *bridge* to CDs |
| **Arcol** ([arcol.io](https://arcol.io)) | Browser massing → plans → metrics → docs | Early-stage/feasibility teams | Revit export, sheet sets | ❌ **AI is roadmap**; a "Zoning Agent" is "up next" |
| **EvolveLAB** ([evolvelab.io](https://www.evolvelab.io)) | Revit plugins: Veras (AI render, raster only), Glyph (auto-documentation), Morphis (generative), Helix, Bento | Revit-centric firms | Raster (Veras); native Revit (rest) | ❌ none anywhere |
| **ArchiLabs** (YC F2024, [archilabs.ai](https://archilabs.ai)) | Browser-native "AI CAD for architects" | Production homebuilding, modular, MEP | Sheets, annotations, schedules, BOMs | ❌ no permit-set claim |
| **Augmenta** ([augmenta.ai](https://www.augmenta.ai/)) | **Spatial AI for MEP routing** — see §5 | Electrical contractors, VDC teams | Clash-free constructable models; **imports from and exports to Revit** | Claims "contractor-grade", "constructable", prefab-ready |
| **Qonic** ([qonic.com](https://qonic.com/)) | Cloud-native BIM platform; AI auto-classification of IFC elements | Designers, constructors, information managers, owners | BIM models, reports | Not a generator |
| **FORMAS.AI** ([formas.ai](https://www.formas.ai/)) | Orchestrates 60+ third-party models, sketch→viz. $3.98M pre-seed Apr 2026 | Architects, interior designers | **Visualization only**: JPG/PNG/WebP, GLB/OBJ/FBX/STL | ❌ no BIM |
| **Drafted** (drafted.ai) | Text prompt → floor plans + 3D home layouts. **$16M seed, May 2026** (Buckley, YC, Ben Silbermann). 120k users in month 1 | Consumer | **UNCONFIRMED** — site 403s | **UNCONFIRMED** |
| **PlanFinder** ([planfinder.xyz](https://www.planfinder.xyz/)) | Generative floor-plan automation for Rhino/Grasshopper/Revit | AEC | Reported DXF/SVG/PDF — LOW-TRUST | ❌ none found |

**Incumbent move worth noting:** **Revit 2027** (April 2026) shipped **Autodesk Assistant (Tech Preview)** — natural-language product help, model queries and task automation — plus an **MCP Public Server (Tech Preview)** letting external assistants (Claude, ChatGPT, Cursor, Copilot) connect to a live Revit model ([Autodesk](https://www.autodesk.com/blogs/aec/2026/04/07/whats-new-in-revit-2027/), [Revit 2027 Help](https://help.autodesk.com/view/RVT/2027/ENU/?guid=GUID-68D8FE6D-C5B0-4503-AE27-02C715BAC25B)). Note what this is: **a copilot inside the authoring tool, not a layout generator.** The incumbent is defending the documentation phase, not attacking the concept phase.

**Flagged:** **Vitruvius (ICON)** — announced 2024, prompt → 3 designs, trained on "building codes, building methods and structural engineering". `iconbuild.com/vitruvius` now returns **404** and no 2025/26 coverage was found. **Status UNCONFIRMED.**

---

## 5. The gap — observation with evidence

### 5.1 Every general-purpose generative layout tool stops at the same place, and it is not the expensive place

The convergence is total and it is stated by the vendors themselves, not inferred:

| Vendor | Where it stops, in its own words |
|---|---|
| Snaptrude | "designed for the early stages… When you're ready for construction documentation, Snaptrude exports cleanly to Revit"; LOD 250/300 |
| Synaps | "fastest from sketch through **SD and DD**; once geometry is locked, you can export DXF/PDF **into your CD tooling**" |
| Finch | "from first sketch through design development **until schematic design**" (co-founder) |
| ARCHITEChTURES | "BIM schematic design (**LOD 200+**), i.e. basic project" |
| Autodesk Forma | "conceptual BIM model"; "not intended for high LOD models"; layout generation is "an **experimental** feature" |
| TestFit | "**after** the real estate feasibility phase… export… **to continue design development**" |
| Maket | "cannot be used for construction, permitting, or regulatory approval" (ToS) |
| Cedreo | output "**has no contract value**" (ToU Art. 3.3) |
| RoomSketcher | "we **can't guarantee** they meet the requirements for building permits… consult a licensed architect" |
| Planner 5D | "Traditional CAD software is better for… construction documents" |

Eleven products, four price tiers from $0 to $20,000/yr, four different underlying techniques — and a single shared ceiling at schematic design. **Nothing in the surveyed market produces a dimensioned, annotated, coordinated permit set.** Every one of them terminates by handing the user to Revit, AutoCAD, or "a licensed architect."

That ceiling sits below the majority of the work — but **this document does not have a verified number for how much, and deliberately does not state one.** The canonical source would be AIA's allocation of basic-services fee across the five phases (SD, DD, CD, bidding, CA), in which construction documents is the largest single phase; **that allocation could not be confirmed against an AIA-published primary source in this pass** (see §6). The claim therefore rests on the vendor statements above alone, which are sufficient for its qualitative form: **every general-purpose generative tool terminates at or before design development and hands the user off to Revit, AutoCAD, or a licensed architect for everything after.** Quantifying the share of fee that represents is the single highest-value open item in this research.

### 5.2 "Code compliance" is claimed by six vendors and implemented by approximately zero

This is the sharpest finding. Sort the claims by what actually happens to the geometry:

| Vendor | Claim | What it actually is |
|---|---|---|
| **Maket** | "zoning regulations" feature | **LLM Q&A over a PDF the user uploaded.** Never touches the geometry. ToS separately says Maket does not verify "zoning restrictions" or "permit requirements". |
| **Snaptrude** | "generates **compliant** massing"; "auto-adjacencies from **building codes**" | **User-uploaded code PDFs fed to an LLM.** No named code library. ToS §10.4: "solely responsible for verifying." |
| **Finch** | "**Code and compliance check**" (Enterprise); "local codes" | **User-authored graph rules.** No named standard anywhere in the docs. |
| **ARCHITEChTURES** | "regulatory confidence" | **Real geometric constraint satisfaction + violation tracker — against coefficients the user typed in.** No code database, no jurisdiction awareness. Blog: "the designer is responsible for compliance with regulations." |
| **TestFit** | "a **pass/fail score** with each scheme **to ensure compliance**" | Rule evaluation against **third-party Zoneomics data**, with third-party-data risk contractually pushed to the customer. |
| **DBF Hikari** | "hard constraints" + "evidence chain back to each rule it satisfies", Japan-specific | **The only claim of jurisdiction-specific encoded rules found anywhere** — one SKU, one country, thinly documented. |
| **Autodesk Forma** | *(no code claim)* | Environmental analysis only. |
| **Cedreo, Planner 5D, RoomSketcher, Synaps** | *(no code claim)* | — |

Two patterns fall out:
1. **No general-purpose vendor ships a jurisdictional code library.** In every case the user supplies the rules — as typed coefficients, as hand-authored graph rules, or as a PDF pasted into an LLM. "Compliance" in this market means "satisfies the numbers you gave me."
2. **Regulatory claim strength is inversely correlated with contractual cover.** TestFit makes the strongest verdict-shaped claim ("pass/fail… to ensure compliance") and offers the weakest protection (generic AS IS, **$5,000 liability floor**, no professional-judgment clause). Autodesk claims the least and has the only purpose-built professional-judgment clause. Snaptrude's marketing says "compliant" while its §10.4 says the user is "solely responsible for verifying."

Meanwhile a whole segment (Kestrel Labs, Permitify, UpCodes-style tooling) has emerged in 2025–26 to sell code checking **as a separate product operating on already-finished drawings** — which is itself evidence that generation and compliance are not joined anywhere.

### 5.3 The output-format gap: nobody bridges "generated" and "authorable"

Cross-tabulate what the generators emit against what a permit set requires:

- **IFC export:** ARCHITEChTURES ✅, DBF ✅, Forma ✅ (Beta 4.3), Snaptrude (claimed, undocumented), Planner 5D (B2B API beta). **Finch ✗, Synaps ✗ (roadmap), TestFit ✗, Maket ✗, Cedreo ✗, RoomSketcher ✗.**
- **RVT:** only via plugins (Finch, Snaptrude, Forma, TestFit's `.tfrvt`). **No one exports an RVT file.**
- **Typed BIM objects:** Snaptrude (native families) and ARCHITEChTURES (construction families + room objects) are the only two with real object typing. **Finch ships "generic wall types" and "generic Finch doors" that the user must manually replace.**
- **Dimensioned/annotated output:** Cedreo and RoomSketcher produce scaled, annotated 2D — but as JPG/PDF/DXF, at ±2 in tolerance, for sales and listings. **None of the professional generators documents a dimensioning, annotation, title-block or schedule system.** Snaptrude's entire Documentation help collection is 5 articles with none on any of these.

So the market splits cleanly: tools that produce *real BIM objects but no drawings*, and tools that produce *real drawings but no BIM objects*. **Nothing produces both.**

### 5.4 Corroborating evidence from the research literature

The academic state of the art has the same problem in a purer form. Current graph- and diffusion-based floor-plan models are criticised precisely for outputs that are "scale-invariant and thus cannot be used directly in downstream tasks", and the newest work is explicitly motivated by it: *"existing generative models for floor plans are predominantly end-to-end generation that produce an entire pixel-based layout in a single pass. This paradigm is often incompatible with the incremental workflows observed in real-world architectural practice"* ([FloorPlan-DeepSeek, arXiv:2506.21562](https://arxiv.org/abs/2506.21562); see also [GSDiff](https://wutomwu.github.io/publications/2025-GSDiff/paper.pdf), [a 2025 survey](https://generativeaiandhci.github.io/papers/2025/genaichi2025_6.pdf)). Research is still working on getting *metrically valid vectors* out; the products are downstream of a problem the literature has not fully solved.

### 5.5 The counter-example that proves the gap is crossable

**Augmenta** ([augmenta.ai](https://www.augmenta.ai/)) is the one company in this scan producing construction-grade automated output — and it is instructive that it does so by *not* doing architectural layout. Its thesis line is the sharpest statement anyone in this industry has made:

> "**Building design is a geometry problem, not a language problem.** We're building the Foundation Model for Construction, starting with the hardest trade — electrical — now operating at datacenter scale."

Its workflow: **import from Revit** → user defines fly/no-fly zones and project specs (spacing, clearances, minimum raceway heights) → generate clash-free routes → **export conduit back to Revit**, where "our color-coded analysis tools for QC" and further modeling "get models construction-ready" ([electrical](https://www.augmenta.ai/electrical)). Claimed results: "clash-free, constructable 3D models in hours instead of weeks", "contractor-grade for any project size", 65% BIM-time reduction in a customer case study.

Note the shape of it: a **bounded geometry problem**, **hard constraints supplied as explicit parameters**, **round-tripped through the incumbent authoring tool**, **sold to the trade that carries the liability** (electrical contractors / VDC teams), and **still requiring human QC before it is construction-ready**. Similarly, the only two permit-ready claims in the whole market — Genia and Higharc — both got there by radically narrowing scope (structural discipline only; production homebuilding only).

### 5.6 The gap, stated

**There is no product that takes a generated or imported layout and carries it to a coordinated, dimensioned, code-checked permit set — and no product that treats jurisdictional building code as a first-class, encoded constraint on generation rather than as text the user pastes in.**

The evidence for each half:
- *No one crosses the SD/CD line* — eleven vendors, each stating the boundary in its own words (§5.1), and none documenting a dimensioning or annotation system (§5.3).
- *No one encodes code* — six compliance claims, all resolving to user-supplied rules (§5.2); the one exception (DBF Hikari) is one SKU in one country; and an entire separate segment sprang up in 2025–26 to sell code checking as a post-hoc check on finished drawings.

Three qualifications, because the gap is not free:
1. **It is a liability gap as much as a technology gap.** Every ToS surveyed disclaims fitness and accuracy; several cap liability at four figures. Permit drawings require a licensed professional's seal, and no vendor has offered to carry any part of that. Anyone closing this gap inherits the reason it is open. *(The regulatory specifics of sealing requirements were assigned to a research pass that did not complete — see §6.)*
2. **The vendors are not stupid; they are pricing risk.** Autodesk labels its layout generator "experimental" while shipping continuously-retrained ML surrogates elsewhere. TestFit's founder said publicly "it's mostly not AI at all… purposely not referring to this as 'AI'." The conservatism is deliberate.
3. **Scope narrowing is the demonstrated path through.** Augmenta (one trade), Genia (one discipline), Higharc (one building type) are the only three producing construction-grade output. **Nobody has done it for general architectural layout, and no one is publicly trying.**

---

## 6. Confidence and open items

**Could not be confirmed from a primary source:**
- **Autodesk Forma pricing.** `autodesk.com` 403s automated fetch and renders prices client-side. All figures are LOW-TRUST third-party and mutually inconsistent ($1,445 vs $1,500/yr).
- **Snaptrude's IFC 2x3/IFC4 and DWG export** — claimed on comparison pages, absent from the help centre. Needs product verification.
- **Synaps IFC** — the changelog claims IFC round-trip; the pricing feature matrix lists DXF only.
- **Maket's DXF export** — one page says supported, another says "coming soon".
- **Finch's Enterprise "Code and compliance check"** — both relevant doc pages are video-only with no text; which codes are checked is unknown.
- **DBF** — IFC version/LOD/object typing; the full jurisdiction list for Hikari's encoded rules; DBF Mass pricing; the full text of its regulatory-approval FAQ answer (truncated in the rendered source).
- **ARCHITEChTURES** — whether the DXF output is dimensioned; IFC schema version.
- **Drafted** (drafted.ai) — funding confirmed via aggregators only; the entire site 403s, so outputs and permit claims are unknown.
- **Vitruvius (ICON)** — product page now 404s; current status unknown.
- **Forma's sun-hours / daylight / embodied-carbon methods** — simulation vs ML surrogate; `help.autodesk.com` returned 503.
- **AIA phase-fee percentages** and **the regulatory specifics of professional sealing requirements for permit drawings** (NCARB / state board sources), plus the maturity of automated permit checking (Singapore CORENET X, Symbium, Archistar, CivCheck). **A dedicated research pass on this was launched and did not return before this document was written.** §5.1 and §5.6 flag the affected claims. This is the most valuable remaining gap to close.

**Explicitly LOW-TRUST — do not cite:**
- Cedreo pricing from FinancesOnline / Capterra / SaaSworthy / GetApp ($119, $129, $49/mo) — all contradict the live vendor page. Cedreo's own `/faq/3d-house-plan-cost` page ($129/mo) also appears stale.
- "TestFit generates feasibility-level geometry, not construction documents" — a convincing line circulated by several SEO review sites that **could not be attributed to any TestFit-authored page.**
- Tracxn/Crunchbase funding totals for Finch (~$4.19M) and Snaptrude (~$21.5M).

**Method notes.**
- Cedreo's pricing table, Planner 5D's pricing FAQ, and RoomSketcher's terms are JS-rendered and return empty content to plain HTTP fetches; they were read in a live browser and extracted from the DOM.
- `synaps.app`, `autodesk.com`, `help.roomsketcher.com`, `drafted.ai` and `docs.digitalbluefoam.com` all return 403 to standard automated fetching; Synaps was retrieved with a browser user-agent, the others worked around or flagged.
- The WebSearch quota was exhausted partway through; later work used direct fetches and browser reads only, which is the stricter standard.
