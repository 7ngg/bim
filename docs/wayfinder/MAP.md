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
| Plan geometry model — Wall, WallSegment, Room/Space, integer mm, hosted Openings, wall **layer sets** | settled | ✅ its *one box per Room* premise is **weighed and reversed**: a Space is **one or two rectangles** and the Proposal decides which — ADR 0014. ⚠️ ADR 0001's erosion is untouched and is now **asserted** rather than inherited, but `acceptance-bar.md` §9's sliver *argument* is dead and replaced |
| Envelope — inner-face ring of typed edges, rect/L/U/T | settled | ⚠️ *H8 and the single-aspect flat*, **now handed a measured table and a correction**: Brief feasibility over exposure × room count is **non-monotonic** — single-aspect fails at 6, 7, 8, mostly at 9 and **succeeds at 10**, where `envelope_for` switches L → U — so *"dead from 7 rooms"* is measuring the envelope n selects, not n. ⚠️ And **n = 6 fails at corpus-median exposure too**, which is the case the toy's own comment calls typical, so H8 is not only a single-aspect problem — `experiments/envelope-exposure/`. How an **invented** Envelope is derived is still fog, under *Variant generation and ranking* |
| Corpus conversion — how a real dwelling becomes retrieval and training data | settled | ✅ **the 31 % drop is paid, and it was mostly a price for a deleted constraint** — ADR 0016 takes Swiss **30.70 % → 9.74 %** and ResPlan **40.10 % → 6.40 %**, paired, zero dwellings lost, every ADR 0008 guarantee re-asserted. **The slope moved more than the level**: the 83 %-at-4-rooms against 46 %-at-10 spread goes 35 points → 12, so the conversion has stopped preferring small dwellings. The `swiss_fit.json` labelling defect is **fixed at source**. ⚠️ Still true: **no converted plan has ever been looked at** — *Look at the converted corpus*, now owed against **two-rectangle** shapes and a changed record schema. ⚠️ **`why_k.clean()` does not do what it says** and its 58.3 % / 31.03 % figures remain an artefact. ⚠️ ADR 0008's *"decidable, not a timeout"* **is dead**: 1.27 % of Swiss and 16.5 % of ResPlan return UNKNOWN at 10 s, and ResPlan needs 30 s to decide at all |
| Solver projection — CP-SAT, 250 mm grid, 15 s, τ = 4 | settled | ⚠️ every timing and the whole feasibility cliff rest on guillotine ground truth — *The solver has only ever seen guillotine layouts*. ⚠️ And it is now asked whether it can afford a **per-Room hop-count integer** — *What an ordered entry sequence costs the solver*, blocked on the first, because pricing a new encoding on a rig about to be re-based measures the rig |
| Proposer source B — trained transformer: architecture, corpus prep, metric, stopping rule | settled | ✅ **its evaluation has three plan-quality terms for the first time** — sleeping-group count, longest-run allocation, social transit, all computable on a corpus dwelling and a generated Plan by the same code, which corner displacement is not. `proposer.md` §6.1. ⚠️ They are **evaluation only, not stop conditions**, and none has been measured on a generated Plan because no Proposer has been run |
| Runtime and process split — engine / proposer service / BFF, job model, threads, JSON | settled | ⚠️ the honest end state (queue + result store) is fog, under *Persistence, accounts, hosting* |
| DXF export | settled | — |
| Proposal contract — what a source emits and the solver consumes | settled | ✅ **it carries no zoning, and that is the decision** — the node set is derivable from Room type, so ADR 0014's *only the Proposal knows* argument does not transfer. §1 records the refusal with its reasoning. ⚠️ The premise it was challenged on was **half false**: `wet.plumbing_group_count` is a set-versus-set predicate shipping today, so the Proposal is pairwise and the *system* is not |
| Proposer source A — retrieval-and-warp, which ships first | partial | gate and coverage decided, **mechanism not** — *The retrieval index and warp procedure*, which is now **unblocked and re-supplied**: the conversion it warps has settled at two rectangles per Room, and ADR 0016 hands it the per-multiset **pool multiplier** (median 1.219, up to **3.53** on the multisets that thinned hardest) to restate `proposer.md` §2.2 with. ⚠️ It also inherits two staleness items in its own file — §4.4's yield and the **ladder now reduced to two rungs** — and one new check: a warp that scales a two-part Room down can break ADR 0014's **hard 900 mm join** |
| Acceptance bar — 38 predicates (**39 once `dim.leg_join` lands**), enforcement sites, conformance test | partial | **19 of 38 thresholds are `ENGINE_CHOICE`** — *Fit the ENGINE_CHOICE acceptance thresholds to the corpora*, which now also holds the **three area rules** *What a room's area is allowed to be* measured. Opening rules need *Opening placement rules*. ⚠️ **And the bar has no rule of the shape *this dwelling owes a room at all*** — every predicate is per-Room, per-Wall or per-Opening, so **a flat with a bath and no toilet passes all 38 and exports** — *A dwelling with no toilet passes every check*, which arrives with a **mandatory, first-hand source** (AzDTN cl. 5.2) and no home for the rule family it implies. ✅ **the 40 m² WC is answered**: `dim.max_area` hard at `both`, and **free in the solver** — H4's `a = w·h` already exists. ⚠️ **And five more rules are owed, from *Where a set-versus-set property lives***, specified ready to transcribe at `zoning.md` §5b — one hard (`zone.sleeping_group_count`, at most two sleeping groups, 97.5 % of real dwellings) and four soft or warn, of which **`zone.no_social_transit` is the one nobody had written**: `circ.no_private_transit` blocks routing through a bedroom and *nothing* blocks routing through the living room, which 18.2 % of real dwellings do. ⚠️ Every dimensional rule now has to declare **which part it binds** — ADR 0014 binds minima and aspect per part, area per Room — and one new soft rule, `dim.prefer_single_part`, is owed to `rules.json`'s holder — as is a **locale dimension on every Homeowner-facing message**, since §11 requires a plain-language message per rule, all 38 are English, and the surface is now Azerbaijani: a schema change, not a translation pass |
| Standards table — region-invariant ergonomic floor + the `AZ` profile | settled | ✅ **all four owed items paid** — the mapping exists (`profiles.AZ.rooms.mapping`, 18 rows, 162 gates), the room names turned out to be **in AzDTN 2.7-2's own text in this repo** (14 of 18 `verified`), the three-into-one gap resolved by **keeping three** (the norm carries `hol` and `dəhliz`; `giriş holu` is ours and labelled), and the corpus medians are recorded with their tail warning — *Two room vocabularies in one file*. ✅ its thickness is measured-vindicated: 150 lands **4 mm from the corpus-optimal 146**. ⚠️ **The merged 7,58 m² hall/lobby/corridor median can default nothing** now the three stay apart — rung 2 is empty for all three. ⚠️ One resolution step — `(type, otaq_count) → target, width, name` — is **named in no spec**; handed to `brief.md`'s holder |
| Drawing — graphics, chains, schedules, tags, sheet, Drawing check | partial | its US NCS / AIA defaults contradict an Azerbaijani drawing, **and ADR 0004's one centreline number is now dead** — both owed by *The annotation spec is US-shaped and the drawing is now Azerbaijani*, which now also holds a defect the audience split creates: **the room tag's fallback is a room number plus a `practitioner` schedule**, so on the Homeowner preview it points at a document that presentation filters out — reproduced at a 1,85 m bedroom. ⚠️ **a uniform partition draws two wall weights where 76.1% of real dwellings draw three** — *One wall weight where a real plan draws three*. ✅ the room tag and room schedule are **settled for a concave Space** (ADR 0014) and the Drawing check needed **no new predicate** — chains measure wall faces, not rooms |
| **Brief and parsing contract** — the object a prompt becomes, and per C4 the real interface | settled | `docs/spec/brief.md`. ✅ its **band** now has numbers, and ✅ **§9.4's upper half is closed**: six bounds, one function, and **no severity chosen** — ADR 0015 makes a parse-time bound inherit the severity and threshold of the validator rule it is the pre-image of. The Envelope-bigger-than-programme case is a **hard refusal naming two edits**, and the stated-Brief contradiction is caught net-versus-net at the 5 % `area.invented_envelope_hard` already ships. ✅ `resolve` invents **exactly one `hall`**, sourced from AzDTN cl. 5.2. ✅ **Bound 6 no longer rests on a point estimate** — *The partition footprint has a mean and no spread* measured the spread and **wrote it in rather than handing it on again**, because `brief.md` had no claimant and a second handoff would have recreated the defect that created that ticket. It came back **wider and differently shaped than asked for**: `f_hi`/`f_lo` are an **eight-row table over engine room count**, not two constants — ρ = +0.379, median 4.30 % at four rooms against 6.37 % at ten, so pooling excuses a four-room Brief with eight-room partition density — and `f_hi` ships at **p99, not p95**, because a too-low `f_hi` refuses a buildable Brief while a too-high one only sends a doomed Brief to a solve that explains it correctly. ✅ And the **5.7 % reproduced at 5.71 % on a disjoint, unconditioned sample**. ⚠️ What replaces the limit is smaller: `f_hi` restores ADR 0015's implication **empirically, not provably** — it is a p99 of *corpus* dwellings, and the engine's own reachable maximum has never been measured because no Proposer has been run. ⚠️ **Two of eighteen room types are now dead paths** the data still presents as live — `corridor` and `entrance_lobby` need `reachable_in_v1: false`, and this ticket could not write that file |
| Area measurement convention — what a m² means everywhere it travels | settled | — |
| **IFC export** — the Destination's second named output | settled | `docs/spec/ifc-export.md`, ADR 0011. ⚠️ **Reference View, because Design Transfer View never became an official MVD and zero software is certified for it** — so C2's Revit round-trip is still priced at zero, and the section that was to price it was never written. ⚠️ ADR 0010's `IfcWallStandardCase` naming is **dead**; the layer-set reasoning it carries is not. ✅ **The whole Space question is closed** by *What geometry an IfcSpace actually gets*: §6 and §12 no longer contradict each other, RV **does** accept an `IfcArbitraryClosedProfileDef` (template quoted first-hand, ADR 0014's open question discharged), a Space is **one** extrusion concave or not, and the quantity set goes **4 → 10 written** with the gate **11 → 16**. ⚠️ **The `IfcIndexedPolyCurve` Revit risk turns out to be a wall risk** — `ifcopenshell` builds an arbitrary profile for a plain rectangular wall, so every wall already carries it and the concave Space added nothing. ⚠️ **`NetPerimeter` had been specified wrong** and nine of thirteen space quantities were in neither list; both fixed, and a **vertical convention set** now publishes ADR 0012's understatement inside the file. What is left on this row is the round-trip, which is fog, not a ticket |
| **Vertical dimensions** — the height the model has never had | settled | `docs/research/vertical-dimensions.md`, ADR 0012, gates 33 → **67**. **One datum, `h_clear`;** `h_storey` **deleted** — AzDTN 2.7-2 publishes none, and its only two consumers were empty. ⚠️ the ticket's premise was **half false**: two of the four inputs were already shipped and `verified`. ⚠️ **the `Fall barrier` trigger is refused, not chosen** — it turns on the drop below the window, and v1 has one Storey at elevation 0 with no site, so the model cannot evaluate it at all. ✅ **its two IFC consequences are landed** by *What geometry an IfcSpace actually gets*, and one was bigger than the ADR declared: IFC4 defines `Qto…Height` from the **base slab**, so the declared understatement had to be **published in the file** rather than only in the ADR — `BimEngine_VerticalConvention` on `IfcBuilding` |
| **Homeowner product surface** — the whole of C2's user | settled | `docs/spec/homeowner-surface.md`, prototype on branch `prototype/homeowner-surface`. **A living document in Azerbaijani**, `both` set **plus a fixture render**. ⚠️ **The surface language had never been decided by anyone** — `profiles.AZ.drawing.language`'s own note scoped itself to the builder — and deciding it owed an **Azerbaijani room-name table** — ✅ **now delivered and sourced** by *Two room vocabularies in one file*, so the prototype's placeholder names can be replaced and its README warning discharged — and a **locale dimension on all 38 rule messages**, still owed. ⚠️ It found two defects in settled documents, and ✅ **both are now owned**: the **stated Brief that contradicts itself and survives parse** is **closed** by *What the engine says when the Envelope is bigger than the programme*, and **`Room.target_area` and `Space` area render identically** — a request and a result in one typeface — goes to [A request and a result in one typeface](tickets/45-a-request-and-a-result-in-one-typeface.md), which arrives with the **Practitioner half already paid**: `NetPlannedArea` beside `NetFloorArea` in the IFC, two properties apart on one entity. The shape of an answer exists; the open question is whether a Homeowner should be shown a delta at all |
| **Room-count promise** — the band v1 claims, and what it refuses | settled | ADR 0013, `experiments/room-count-envelope/`. **Gate 3–10 engine rooms, promise 1–4 otaq** — two numbers in two units, on purpose. ⚠️ **C13's "Brief-named" was false**: no Brief names a corridor, and 93.5 % of real dwellings have one. A Homeowner naming 10 rooms is out of band **99.8 %** of the time. ⚠️ The band's *edges* were also wrong — per-`n` coverage puts **n = 2 as the worst regime below 11**, worse than the n = 10 the old band included, and **n = 1 retrieves better than n = 4**. ✅ **No longer unowned**: all three of ADR 0013's handoffs are placed — the one-rectangle premise is settled by ADR 0014, §9.4's third and fourth bounds and the circulation-count rule sit on *What the engine says when the Envelope is bigger than the programme*, and the `habitable` flag on *Two room vocabularies in one file* — ✅ **resolved, and renamed**: `is_habitable` already existed, so the flag shipped as `counts_as_otaq`, sourced from AzDTN cl. 5.5 rather than chosen, and it **diverges from habitability on `kitchen_dining`**. What is left on this row is a **correction to the record**, not work |

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
| `CONTEXT.md` | **no claimant** — 31, 38 and 44 closed. 44 declared it on resolution: **Partition footprint** is a new term, and it exists because the quantity has *two* denominators — a share of Σ Space area, never of the interior — and no quote of the 5.7 % anywhere said which. 38 declared it on resolution: **Pre-image bound** and **Invented circulation** are new terms, **Acceptance bar** now reads *one declaration, three consumers* |
| `data/standards/room-constraints.json` | 16, 32 — **31 closed.** **38 hands it `reachable_in_v1: false` on `corridor` and `entrance_lobby`**, which nothing in v1 now reaches. It added `profiles.AZ.rooms.mapping`, `counts_as_otaq`, `brief_nameable` and `ergonomic.corpus_medians`; a new room type or profile cell must now come with a mapping row or `gate_check.py` fails |
| `data/acceptance/rules.json` | 16, 20, 26, **42** — and whichever of them moves first inherits the **message locale** schema change, which **38 has now merged with a second requirement**: `brief.md` §9.4 returns a *set of findings* rather than a verdict, each with a severity, a Brief field and an Azerbaijani message — one schema change, not two, and now **two rules 31 handed over** (cl. 5.2's mandatory room composition, and `kitchen_dining`'s zone-not-room target) and **five 30 handed over**, written out in full at `docs/research/zoning.md` §5b |
| `data/standards/room-constraints.json` (second entry) | **30 hands it one flag**, `is_sleeping` — and it **may not be folded into `is_private`**, which is true on the wet types too |
| `docs/spec/acceptance-bar.md` | 26, **42** — 42 is new and 28 is closed |
| `docs/spec/proposer.md` | 23 — **sole claimant now**, 30 closed |
| `docs/spec/annotation.md` | 32 — **sole claimant now**, 28 closed. ✅ **31 has handed it the eighteen Azerbaijani room names**, sourced and cited |
| `docs/spec/openings.md` | 16 — **sole claimant now.** 39 closed without creating it: the catalogue-versus-instance line is in `CONTEXT.md`'s **Opening** and **Head datum** terms and in the profile data, so 16 inherits it |
| `docs/spec/brief.md` | **no claimant — 38 and 44 closed.** 44 wrote §9.4 bound 6's `f_hi`/`f_lo` table, §5 rung 1's `f`, §12 and §13 into it rather than handing them on.
  It raises one new obligation: the eight-row table is inline prose and belongs in data beside `room-area-bands.md` §6.1's `k`, for `rules.json`'s holder. It rewrote §9.4 and added §3.1, so a ticket touching either is amending a settled shape rather than filling a gap. **31's two are still open**: whether a nineteenth type (`taxça-mətbəx`) is owed, and where the `(type, otaq_count) → target, width, name` resolution step lives |
| `docs/spec/homeowner-surface.md` | **45 — sole claimant.** Created by 13, which declared it on resolution rather than taking it quietly; 45 is the first ticket to claim it, and it inherits the **message locale** schema change if it moves before `rules.json`'s holder |
| `experiments/envelope-exposure/` | **new, no claimant.** Also 13's, and deliberately *not* `experiments/solver-toy/`, which 29 claims: the two probes import that directory and never edit it. Their findings are quoted on the Envelope row and on 26 |
| `experiments/region-profile/gate_check.py` | **no claimant.** 31 declared it on resolution rather than taking it quietly — 162 vocabulary gates, the file now runs 229 |
| `docs/spec/ifc-export.md` | **no claimant — 41 closed.** It also declared `docs/adr/0012-…` and `docs/adr/0014-…` on resolution rather than taking them quietly: 0012's `§5` → `§6` slip and both its consequences marked landed, 0014's RV question marked cleared and its rectangle comparison recorded as false |
| `experiments/thickness-fidelity/`, `docs/research/single-internal-thickness.md` | **no claimant — 44 closed.** It also declared `docs/spec/brief.md` and `CONTEXT.md` on resolution: neither had a claimant, and handing two numbers to an unheld file is the defect that created 44. It leaves behind a **committed 479 KB series**, `series/footprint_150.csv.gz`, so the next percentile off this study costs seconds instead of a 46-minute re-measure against a 1.09 GB corpus — with the rule in the README: *if you add a statistic to this study, add its inputs to the series* |
| `experiments/solver-toy/` | 29, **43** — 43 is new and **blocked on 29**, deliberately: 29 re-bases the ground truth every timing on this map was measured against, so pricing a new encoding first would measure the rig |
| `experiments/rectangularise/`, `docs/research/rectangularisation.md` | 27 — **sole claimant now, 40 is closed.** The sequencing hold is lifted: the fit has been rewritten and settled, so there is a stable conversion to render. Render `out/swiss_fit_k2.json`, whose records carry **`parts`** and no `rects` |

✅ **39 and 28 are closed and their collisions are gone.** 39 had the widest
write-set on the map and 28 had the widest after it; both were taken when the
frontier was quiet, exactly as this note directs. 28 **declared** `CONTEXT.md`,
`docs/research/` and a new `experiments/` directory on resolution rather than
taking them quietly — nothing else was claimed at the time, so the rule held, and
the entries are on its ticket for the next reader. Four artifacts now have a
single claimant that had two.

Only one of these became a blocking edge, and deliberately: sharing a file is a
merge hazard, sharing a *decision* is a dependency. 28 changes the Proposal
contract's shape rather than adding to it, so 30 would otherwise be amending a
contract about to move.

**The environment is pinned, and the pins are load-bearing.** `requirements.txt`
carries the direct dependencies with the *reason* for each pin;
`requirements.lock.txt` carries the resolved set including transitives. Install
from the lock file, never from PyPI latest:

```
python -m venv venv
./venv/Scripts/python.exe -m pip install -r requirements.lock.txt
./venv/Scripts/python.exe experiments/environment/env_check.py     # 28 gates
```

Exact pins rather than ranges, because **every measured number on this map was
produced by a specific version** — the solver timings by `ortools` 9.15.6755, the
thickness census and rectangularisation by that `shapely` and `numpy`, and the
whole IFC surface by `ifcopenshell` **0.8.5 specifically**, whose documented API
(`feature` not `void`, the near-empty `drawing` module, the missing
`boundary.add_boundary`) a bump invalidates rather than merely ages. `pytest` is
a **runtime** dependency, not a test one: `ifcopenshell.validate(express_rules=True)`
imports `_pytest.assertion` and the IFC check cannot run without it.

`env_check.py` is `gate_check.py` one layer down — it asserts the *toolchain*
still supports the decisions taken against it. **28 gates, all pass.** Two of them
re-measured claims this map rests on: the `add_door_representation` metre-only bug
**reproduces** (so ADR 0001 §6 is verified, not inherited), and the missing-`ObjectPlacement`
WR1 trap **is** caught by the express rules, which demoted one IFC-check assertion
from load-bearing to belt-and-braces. A failure here means a document on this map
now says something untrue.

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
| C3 | Hard output floor: **dimensioned 2D vector plan** — walls with thickness, doors, windows, room tags, dimension strings — to DXF/PDF. IFC/BIM is the stated export path. Now specified and **split by job**: the IFC is **IFC4 Reference View, one-way, annotation-free**, and **the DXF is the exact export while the IFC is the interoperable one** — integer-millimetre exactness does not survive the metre declaration. ADR 0011. |
| C4 | Input is **prompt → LLM-parsed structured brief**, gaps filled from standards, every assumption surfaced. The brief stays editable; it is the real interface. |
| C5 | **Single-dwelling residential, single storey.** Flats and houses ship through **one code path** — dwelling type is a preset over the Envelope's edge ring, not a branch. Product copy states two limits: single storey only, and **house layouts come from apartment priors**, because every corpus is flats. |
| C6 | Acceptance bar is a **hard filter**: generate many, reject most, show survivors. On solver expiry, a candidate whose best objective is ≥ `soft_weight` has unassigned floor and is **not a survivor** — discard it, never show it. |
| C7 | Post-generation, v1 is **edit-the-brief-and-regenerate**. Direct wall manipulation with re-solve is designed-for but deferred. |
| C8 | **Neufert-*grade* dimensional standards. No legal code-compliance claim, ever** — say so in the product copy. Neufert names the grade, not the source: building a profile out of it is the one copyright move the research forbids. |
| C9 | **Non-commercial project.** Research-only datasets and weights are available. Licence is not a gate; data quality and regional convention are. |
| C10 | **Model proposes, solver projects** — amended twice, and both amendments are load-bearing. The Proposal carries **relative arrangement, not just boxes** (pairwise separations promoted to hard linear constraints) and exact tiling is posted **soft**. It also carries **shape**: one or two boxes per Room, ADR 0014, because a solver left to choose takes a second rectangle on a fifth to a third of the rooms it is offered against a truth needing none, and a penalty stops being a dependable switch by twelve rooms. *Model proposes* now includes what shape a room is. The loose form is refuted by measurement. A **two-phase fallback is mandatory**: a merely *noisy* Proposal goes INFEASIBLE. Shipped: **15 s, τ = 4**. And "the model" is **two sources** behind one Proposal contract — ADR 0005. |
| C11 | **Clean successor to `../plan-generator-3000-pro-max`.** No code inherited. Its findings may be reused only after independent verification. |
| C12 | Not tied to any region — but that was freedom, not an obligation to serve everywhere. v1 ships **exactly one** profile and it is **`AZ`**; `UK` survives as a test fixture and is never selectable. |
| C13 | **The gate and the promise are two numbers in two units.** The engine hard-refuses outside **3–10 engine rooms** — every Space including the circulation `resolve` invents — and the product promises **1–4 otaq**, habitable rooms, the unit AzDTN and the Baku market count in. Between them is a zone the engine serves and the copy declines to claim: 89.9 % promised, 4.3 % served-unpromised, 5.9 % refused. *"Brief-named rooms" is struck* — no Brief names a corridor. Retrieval dies at 11+ (58.0 % blank) and the 24-room case is **demoted to headroom evidence, quotable as a ceiling by nothing**. ADR 0013. |
| C14 | **A region profile is a construction system plus a drawing convention, and it never rejects a Plan.** It owns the thickness catalogue, decimal separator, room-name abbreviations, opening catalogue keys, two soft area targets and one soft window fraction; every hard dimensional floor is the region-invariant ergonomic minimum. **`RegionProfile` and `CorpusProvenance` are two fields**, `AZ` and `CH`, and their disagreement is the normal case — v1 draws **Swiss-shaped layouts to Azerbaijani conventions, permanently**, and says so. Now populated: **one construction type, brick, `t_int` 150 mm — a layer set, 120 structural + 2 × 15 finish, every term `verified`**, drawing in Azerbaijani. It also owns the **area convention**, and every published number measures to that finish plane. ADR 0006, ADR 0010. |
| C15 | **Two arithmetic ship gates, and they bind different layers.** ADR 0004 — every wall thickness **even** — is global. ADR 0007 — `min + t_int ≡ 0 (mod grid)` — binds **region profiles only**; ADR 0009 exempts the region-invariant ergonomic layer, whose minima are *derived* rather than quoted and so have no nominal-to-clear conversion to apply. Asserted, not claimed: `experiments/region-profile/gate_check.py` — **67 gates, all pass** (33 before ADR 0012 added the vertical section) after ADR 0010 moved the residue class from 130 to 100 mod 250 and sharpened ADR 0004 to bind on **totals, not layer components**. |

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
  dwellings have every room a rectangle. ⚠️ **Its 69% / 60% yield and its whole
  fidelity ladder are superseded** — see *Re-measure the conversion at two
  rectangles per Room* below.
- [Re-measure the conversion at two rectangles per Room](tickets/40-re-measure-the-conversion-at-two-rectangles-per-room.md)
  — **two thirds of the Swiss drop and four fifths of the ResPlan drop were paying
  for a constraint ADR 0014 had already deleted.** ADR 0016,
  `docs/research/rectangularisation.md` §11, `experiments/rectangularise/`.
  Paired on the same 2,600 dwellings and 1,000 plans: **30.70% → 9.74%** Swiss and
  **40.10% → 6.40%** ResPlan, **zero lost**, p = 2.2e-162 and 7.1e-102. **The slope
  moved more than the level** — the gain is monotonic in room count (+0.119 at
  n = 4, **+0.351 at n = 9**) so the 4-versus-10-room spread goes 35 points → 12 and
  the conversion stops being a filter that prefers small dwellings. Fidelity
  *improves* — the **worst room** in a dwelling gains 0.157 IoU on Swiss and
  **0.341** on ResPlan — and zero adjacencies, flips or weakenings across 91,980
  axis-pairs, re-derived by `validate_k2.py` from the emitted geometry. **ADR
  0014's central claim is now measured from the other side**: the conversion's
  type ordering *inverts* the free solver's (living/dining 0.42 and corridor 0.22
  at the top, storeroom 0.005 and bathroom 0.003 at the bottom), so *the ground
  truth is the taste* stops being an argument. ⚠️ **The ticket's own item 1 pointed
  at Design B, which is unmeasurable**: every Room free returns **0 OPTIMAL and 0
  INFEASIBLE** in 10 s, so the reject rule stops existing — the conversion uses
  Design A and **every figure is a lower bound**, ~2 points of rooms wide
  (`name_rate.py`). ⚠️ **ADR 0008's "decidable, not a timeout" is dead.** ⚠️ **The
  fidelity ladder is cut to two rungs**: A→D spans 6.8 points where it spanned
  26.4, and **tier C sits below tier A** because dropping hard relations removes
  the pruning and the arm times out. ✅ Fixes *Look at the converted corpus*'
  labelling defect **at source**.
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
  **dead**, as ADR 0004 §4 pre-authorised. ⚠️ **ADR 0010's own IFC justification
  names a deprecated entity** — `IfcWallStandardCase` is superseded by `IfcWall`
  in IFC4.3, per *What IFC the engine actually emits*; the layer-set reasoning it
  supports is untouched. ✅ Its one `engine_choice` was
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
- [Brief schema and parsing contract](tickets/10-brief-schema-and-parsing-contract.md)
  — **the Brief is two objects, and the parser is the only untestable component.**
  `docs/spec/brief.md`, `CONTEXT.md`. `StatedBrief` (sparse, what the prose said)
  and `ResolvedBrief` (dense) joined by a pure `resolve`, so the Assumption set is
  **derived** rather than a second list, editing *is* re-resolution, and **the model
  is never asked to invent a number** — which is what deletes the retry loop
  entirely: structured outputs cannot fail schema, and a semantic problem is the
  Homeowner's to see. The Brief speaks the **ergonomic 18 verbatim** with a
  display-only `label`, so *Two room vocabularies* has one mapping to build, not
  three; open-plan is a **type**, not an adjacency. Relations are three — hard
  `access_via`, soft `adjacency_wish`, hard `adjacency_veto` — and **neither of the
  last two has a predicate today**. Defaults ladder `market_default` → **corpus
  median** → absent, because `AZ` is silent on `wc`/`hall` and 63,800 dwellings are
  on disk. ⚠️ **The finding that bites hardest is a defect in the bar, not in this
  ticket: a 40 m² WC passes all 38 rules** — every area predicate is a floor or a
  total, and `model.no_unassigned_area` makes the surplus *compulsory*, so it lands
  wherever the objective is cheapest. Re-owed by *What a room's area is allowed to
  be*. ⚠️ **The feasibility pre-check must sum realisable minima**, not published
  ones — ADR 0009's erosion still governs, so `bedroom_double` is 3.9 m², not 3.1,
  **25 % higher**; the circulation-allowance constant is deleted rather than fitted,
  and `acceptance-bar.md` §11's 58 m² is **not reproducible** from the shipped table.
  ⚠️ Its inherited *"`statutory_floor` is null in the default region"* is **stale** —
  `AZ`'s are populated and `verified`; the conclusion survives on C14 instead.
  Accessibility is **refused, not ignored**.
- [What a room's area is allowed to be](tickets/37-what-a-rooms-area-is-allowed-to-be.md)
  — **a maximum is enforceable, it is free in the solver, and the anchor is the
  Room's own `target_area`.** `docs/research/room-area-bands.md`,
  `experiments/room-area-bands/`. The anchor is settled by an **identity**, not a
  measurement: §9.2 sets a silent Room's target from a per-type constant, so
  "against the target" and "against the type absolutely" are the same rule for
  every Room a Homeowner does not size by hand. A **fraction of the dwelling is
  refuted** — the loosest anchor tested, on 7 of 9 Swiss classes. Three rules
  handed to `rules.json`'s holder, and the second is the one nobody was looking
  for: **`dim.market_default_area` is a cause, not a bystander** — it prefers
  Spaces *at or above* market default, so the objective **actively rewards
  bloat** and a maximum alone just relocates it to under the cap. The absorber
  needs **no Brief field**: rank the classes by dispersion and the ordering *is*
  the absorber ordering. **A Swiss bedroom does not grow with the dwelling at
  all** — r² **0.000**, +0.08 m² per 40 m² — a bigger flat has *more* rooms, a
  bigger living room and more corridor. ⚠️ **The first WC cap was circular** and
  correcting it moved the number **2.2×**: the class `wc` *is* `BATHROOM < 2.4`,
  so every percentile returned the splitter; fixture ground truth puts a real
  WC's p99 at **5.29 m²** and **19.3 % of real WCs above the splitter**. ⚠️ **A
  hard maximum can make a Brief unsatisfiable**, at 4 rooms and only there — and
  it surfaces as zero survivors, not INFEASIBLE, because H3 is soft. ⚠️ **The
  ticket's own instruction points the wrong way**: the converted geometry is on
  the **centreline** plane and ADR 0010 wants the finished face, and the gap is
  **not a constant** — 1.17× for a living room, 1.58× for a WC. Also delivered:
  the silent-`AZ` medians and the bedroom-count → total-area joint distribution
  `brief.md` §7 owed, ⚠️ on which the two corpora **disagree by ~40 %** at three
  bedrooms, from labelling rather than market.

- [What IFC the engine actually emits](tickets/34-what-ifc-the-engine-emits.md) —
  **Reference View, and the file asserts only what the engine knows.**
  `docs/spec/ifc-export.md`, ADR 0011. The ticket's own item 1 has **one live
  branch**: buildingSMART say *"Design Transfer View never materialised into an
  official MVD"*, **zero** products are certified for it, and Revit's IFC4
  certification is **Reference View 1.2, export only** — so the view C2's
  round-trip promise was going to buy does not exist to be bought. RV costs less
  than its reputation (swept solids, Psets, Qtos, layer sets all in scope) and its
  two real restrictions are absorbed: **no Boolean appears in the file**, because
  ADR 0001's axis-aligned walls and rectangular openings decompose **exactly** into
  a set of extrusions. **Space boundaries are refused for a reason that is not the
  restriction** — 2nd level exists for energy/lighting/CFD and this engine holds no
  U-values, so authoring them asserts a capability we do not have; 1st level loses
  nothing, because exact integer geometry makes adjacency derivable. One rule
  decides most of the file — **present is a claim, absent is unknown** — and it is
  **asserted by the gate**, not merely stated, over `LoadBearing`,
  `AcousticRating` (derived from 50 dB, never tested) and `HandicapAccessible`
  (accessibility was *refused*, so both values are wrong). A **third gate** joins
  `rules.json` and the Drawing check, on the Drawing check's own reasoning: it
  judges the *file*, not the *Plan*. ⚠️ **Its hardest finding is not about IFC: the
  Plan has no vertical dimension at all**, and `annotation.md` was already shipping
  three unfillable schedule columns — re-owed by *The Plan has no vertical
  dimension*. ⚠️ **ADR 0010's `IfcWallStandardCase` is dead** — IFC4.3 deprecates
  it in favour of `IfcWall`; the layer-set reasoning stands. ⚠️ **Integer-mm
  exactness dies at this boundary** (ADR 0001's metres), so the DXF is the exact
  export. ⚠️ C2's Revit round-trip is **still priced at zero** — the research
  section that was to price it was never written, and one concrete untested risk is
  named instead (`IfcIndexedPolyCurve` vs `IfcPolyline` on Revit import).
- [The Plan has no vertical dimension, and three artefacts already assume one](tickets/39-the-plan-has-no-vertical-dimension.md)
  — **one vertical datum, and it is the clear height.** ADR 0012,
  `docs/research/vertical-dimensions.md`, `profiles.AZ`, gates 33 → **67, all pass**.
  ⚠️ **The ticket's premise was half false**: two of `ifc-export.md` §12's four
  inputs were already shipped and `verified` — ticket 25 landed `clear_heights_mm`,
  and the catalogue marks always carried head heights. The IFC session grepped for
  *names*, not values. **`h_storey` is deleted, not deferred**: AzDTN 2.7-2
  prescribes no storey height, its 2,8 m appears only as a **lift-traffic modelling
  assumption** the norm itself says to recompute, and both consumers §12 claimed are
  empty — one storey at `Elevation = 0.0`, and **no `IfcSlab` or `IfcRoof`
  anywhere**, so nothing rests on a wall. The cheap answer was **unavailable**: an
  extrusion cannot omit its depth, so ADR 0011's *absent is unknown* does not reach
  it, and the choice was forced between a statutory `verified` figure and an
  unsourced build-up. **A wall body is floor-to-ceiling, declared, not
  slab-to-slab**, and a Wall gains **no** height field. Sills are **derived** —
  `sill = head_datum − catalogue H`, the datum being the **balcony door's own
  catalogue head**, because it shares a lintel with the window beside it — giving
  700 / 700 / **1000**, the kitchen clearing a 900 mm counter. ⚠️ **The `Fall
  barrier` trigger is refused, and that is the finding**: cl. 8.3's 1,2 m is
  statutory, but *which* windows are "places with a risk of falling" turns on the
  **drop below them**, and v1 has one Storey at elevation 0 with no site — a
  ground-floor window and an eighth-floor one are **indistinguishable in this
  model** — so the column reads `—` and the refusal is **gated**. ⚠️ **The gate
  corrected the ticket twice**: a GOST mark is *height*-then-width, and a drafted
  1000 mm trigger guarded every window in the catalogue. ⚠️ Two reversals
  mid-session — the Brief **may** state a ceiling height (an architect never
  invents floor-to-ceiling), which is what makes one hard **Brief-sited** predicate
  possible; and `openings.md` was **deliberately not created**.

- [The room-count envelope v1 promises](tickets/21-the-room-count-envelope-v1-promises.md)
  — **the gate and the promise are two numbers in two units, and the unit was the
  whole problem.** ADR 0013, `CONTEXT.md`, `experiments/room-count-envelope/`.
  Gate: hard refusal outside **3–10 engine rooms**. Promise: **1–4 otaq**. Between
  them a zone the engine serves and the copy declines to claim — 89.9 % promised,
  4.3 % served-unpromised, 5.9 % refused. ⚠️ **C13's "Brief-named rooms" was
  false**, and it is the finding: `brief.md` §3 has `resolve` *invent* circulation
  and `dataset-inventory.md` §1.3 never excluded `CORRIDOR`, so every coverage
  figure on this map counts rooms **no Brief names** — k = 1 in 75.1 % of real
  dwellings, k = 2 in 16.7 %. Stated in a Homeowner's own units the old band was a
  false claim: **naming 10 rooms is out of band 99.8 % of the time**, naming 9,
  31.9 %. ⚠️ **The edges were wrong too.** `proposer.md` §2.1's three bands hid the
  shape; per room count, **n = 2 is the worst regime anywhere below 11** — worse
  than the n = 10 the old band included and worse than the n = 3 it excluded — and
  **n = 1 retrieves better than n = 4**, so excluding studios never was a coverage
  argument. The floor moved to **3 because the shipped profile forced it**:
  `living_room_1room_flat` and `wardrobe_1room_entry` are two `verified` AzDTN
  floors that exist *only* for the one-otaq case, and a floor of 4 makes them
  permanently unreachable — the dead-data defect ADR 0012 deleted `h_storey` for.
  **Refusal is hard because §11 cannot voice it**: the zero-survivor diagnosis is
  arithmetic over *areas*, so without an explicit check a Homeowner past the
  ceiling gets an explanation that is wrong rather than missing. **24 rooms is
  demoted** to headroom evidence — one dwelling in 63,800, measured at an exposure
  no real flat has — and nothing may quote it as the ceiling. ⚠️ **It also drew a
  dependency nobody had**: `resolve` must pick k *before* the solver runs, and
  fixing k = 1 is safe only if a Room may be more than one rectangle — handed to
  *Whether a Room may be more than one rectangle*, along with §9.4's third and
  fourth bounds to *What the engine says when the Envelope is bigger than the
  programme* and a `habitable` flag to *Two room vocabularies in one file*.
  ⚠️ Every number here is **Swiss**; the otaq convention is Azerbaijani — C14's
  two-tradition split showing up in the counting unit now, not just the thicknesses.


- [Whether a Room may be more than one rectangle](tickets/28-may-a-room-be-more-than-one-rectangle.md)
  — **a Room is one or two rectangles, and the Proposal decides which.** ADR 0014,
  `docs/research/room-rectangles.md`, `experiments/room-rectangles/`,
  `proposer.md` §1/§2.3/§5, `acceptance-bar.md` §9.1, `annotation.md` §6/§7/§13,
  `CONTEXT.md`. Cap **two**, and the reason is not the box count: an L is a shape
  an architect draws and a T/U/S/Z room is one a plan is left with — while what
  survives at k ≥ 3 is **mostly not a room shape at all**, being **35.0 %**
  off-axis against **0.63 %** at k = 1. No value of k fixes an angled wall.
  **No type whitelist**: the distribution comes from the corpus, which is already
  type-shaped — bedrooms 69–72 % rectangular, corridors and open-plan living
  26–30 %. ⚠️ **The ticket's own headline is refused**: "2.7 % of real dwellings"
  is a *corpus* statistic and corpus yield is instrumental; the decision rests on
  output naturalism and on tiling slack. ⚠️ **The clean-up it proposed is
  refused, and its evidence is an artefact** — `why_k.clean()`'s dilation is
  clipped to the room's own bbox, so it erodes every room by 500 mm all round and
  fills no notch at any size; corrected, single-rectangle rooms move
  **0.5286 → 0.5367**, and a 2 % area tolerance moves them 1.1 points, so
  **non-rectangularity here is real architecture, not pipe boxings.** ⚠️ It kills
  `acceptance-bar.md` §9's sliver *argument* (`erode(A ∪ B, r)` is strictly larger
  than the union of erosions) and revives the corridor-pinch question §9 dropped,
  with the opposite sign. ⚠️ It exposes a **live defect at k = 1**:
  `select_relations` never filters on a positive separation cost, so an
  overlapping Proposal already gets separations asserted it never made — re-owed
  by *The retrieval index and warp procedure*. ⚠️ Item 6, the 31 % conversion
  drop, is **ticketed rather than measured** — *Re-measure the conversion at two
  rectangles per Room*. ⚠️ Item 4's "confirm against a drawn example" **could not
  be done**: nothing on this map renders a plan. ✅ ADR 0001's erosion is
  **asserted rather than inherited** — `erosion_check.py` matches the inner-face
  polygon pointwise at the reflex corner. ✅ The dimension chains needed **no
  change** and the Drawing check **no new predicate** — chains measure wall faces,
  not rooms. ✅ **The decision rests on one table**: told which Room is an
  L, the solver places **25 of 25 with none spurious**; left to find them it
  places 10 of 18 and **invents 35**; penalised until the invented ones stop, it
  places **none of 16** — so a solver-decides design has no good setting. By type
  it is close to reversed, **Spearman +0.795** against corpus rectangularity. And it
  is the only arm that converts the extra rectangle into plans: **survivor rate
  0.500 against 0.361 for a solver-decides design and 0.333 for the k = 1
  control** — same expressive power, almost none of it realised — at 1.2–1.7× the
  control's variables where Design B costs a flat 3.9×.
  ⚠️ Four of this session's own claims were withdrawn after the measurements
  contradicted them — one caused by a bug in its own harness, one later
  re-established properly — and they are listed on the ticket rather than quietly
  dropped.

- [Homeowner product surface](tickets/13-homeowner-product-surface.md) — **a
  living document in Azerbaijani, and the two things that decided it were
  already in the repo.** `docs/spec/homeowner-surface.md`, prototype on branch
  `prototype/homeowner-surface` over **six real solved layouts** with a headless
  check on door-reachability and every clear dimension against its shipped
  ergonomic floor. The spine is a **document, not a wizard** — `brief.md` §1
  makes an edit *literally* a re-resolution, so a wizard would need step state
  `resolve` does not have. ⚠️ **The surface language had never been decided**:
  `profiles.AZ.drawing.language` is `az`/`verified` and its own note says *"the
  builder, not the Homeowner, reads the drawing"* — scoping itself to the sheet
  and leaving C2's user unaddressed. It is Azerbaijani, and that is the one
  decision here with real downstream cost. ✅ **The fixture decision reversed on
  the data**: `ergonomic.fixtures_mm` ships **fourteen footprints as `verified`**
  (AD M Appendix D, OGL) and **all eighteen** floors are derived from a *named
  packing* of them, so drawing furniture draws the arithmetic that already gates
  the room — it asserts nothing new and is the strongest legibility lever item 5
  was asking for. **No 3D**, though ADR 0012 has just made one possible. The
  **acknowledge control must not look or behave like the edit control**, because
  `brief.md` §6 makes one mutating and one not, and a uniform "OK" would swap
  `area.invented_envelope_hard` for a warning invisibly. ⚠️ **Two defects in
  settled documents, both found by putting two numbers on one screen**: §9.4
  compares realisable *ergonomic minima* against `target_area` and §9.2 fills
  silent rooms, but **nothing compares the Homeowner's own stated room areas
  against their own stated total** — 69,2 m² of stated rooms inside a stated
  45 m² clears every hard error and dies after a full generate cycle; and
  **`Room.target_area` and `Space` area render identically**, a request and a
  result in one typeface, which §9.3's two-sided band makes the *normal* case
  rather than drift. ⚠️ **The room tag has no Homeowner-audience fallback** —
  `room_tag_fallback` is a room number plus a **`practitioner`** schedule.
  ✅ ADR 0013's refusal-voice question is answered: **two forms**, otaq when the
  excess is otaq, **rooms the Homeowner listed** when it is not, never a
  converted number. ⚠️ The prototype's plans are **not solves of its own
  Briefs**, so the second defect is **observed, not measured** — it follows from
  `CONTEXT.md`'s Room/Space split regardless. ⚠️ Whether a Homeowner reads
  `4,40 × 3,40 m` was **rendered but never tested on a person**. ⚠️ **Its first cut
  ran at `detached` — 100 % exterior — and the plans read as bungalows**; re-solved at
  **corpus median** (the toy's own "typical") they read as flats, and the re-run
  produced two findings that outlive the prototype: H8's failure over exposure × room
  count is **non-monotonic** and therefore confounded with `envelope_for(n)`'s shape
  choice (handed to *H8 and the single-aspect flat*), and the flat-versus-house
  **diversity gap is caused by H8 directly** — 0.54× at 5 rooms with the envelope
  geometry held identical — which the aspect-ratio axis *Variant generation and
  ranking* proposes does not address. Both probes are on `master` at
  `experiments/envelope-exposure/`; the prototype stays on its branch.

- [Two room vocabularies in one file, and nothing maps between them](tickets/31-two-room-vocabularies-in-one-file.md)
  — the two taxonomies are now **one canonical set and one declared projection**:
  `profiles.AZ.rooms.mapping`, eighteen rows, total by construction, **162 new gates**
  (`gate_check.py` now runs **229, all pass**). Ergonomic stays canonical and **no AZ
  key was renamed** — the defect was never the names, it was that no object stated the
  **bridge**, so the mapping carries one wherever the sides key on different axes.
  ✅ **The Azerbaijani room names were never missing.** AzDTN 2.7-2's text is in this
  repo, and **cl. 5.2** — a mandatory room-composition clause nobody had read — names
  `mətbəx`, `holl`, `vanna otağı`, `duş`, `tualet`, `yığnaq otağı`, and **cl. 5.5**
  enumerates habitable rooms as `otaq, qonaq otağı və yataq otağı`. The numbers were
  extracted from cl. 5.7 and the *words were dropped*. **Fourteen of eighteen names are
  `verified` and cited**; `giriş holu` is the one `engine_choice` name and says so.
  ⚠️ **Two silent collisions on identically-named keys**, neither fixable by renaming:
  `bedroom_*` keys on **bed capacity** here and on **occupancy** in cl. 5.7
  («yataq otağı - 8 m² (iki adama - 10 m²-dən)») — they coincide, and that is a
  coincidence of meaning now written down; `bathroom`'s `areas_m2` cells conflate
  bath-vs-shower with wc-inside-or-not, which **the norm keeps apart in one sentence**.
  ⚠️ **ADR 0013 asked for a flag that already existed.** `is_habitable` was on all
  eighteen keys, so the new flag is **`counts_as_otaq`**, sourced from cl. 5.5 / cl. 5.2
  rather than chosen — and the two **diverge on exactly `kitchen_dining`**, which is
  habitable and is *not* an otaq. Read the wrong one and a one-bedroom flat with a
  kitchen-diner advertises as **2 otaq**, C13's headline number. A gate pins the
  divergence set. `brief_nameable` also shipped, as `brief.md` §3 asked.
  ⚠️ **The dwelling-conditioning axis is real, sourced, correctly placed, and buys
  almost nothing yet**: `when_otaq_count` lives in the mapping (not the key — that *is*
  the defect — and not the parser, which would bury a profile fact in code), but
  `living_room_1room_flat` and `living_room_2plus` are **identical at `market_default`**,
  so for `living` the guard moves only the statutory *warn*.
  ⚠️ **The closing check was reinterpreted, deliberately**: *resolvable* means the lookup
  is **total**, not that a number comes back — ten of eighteen keys have no AZ area, and
  the strict reading could only be met by inventing ten Azerbaijani numbers, the exact C8
  failure. Silence is explicit `null` and `dim.market_default_area` skips, never raises.

- [Where a set-versus-set property lives](tickets/30-the-proposal-cannot-express-zoning.md)
  — **zoning lives in the solver and the bar, the Proposal gains no field, and
  the ticket's premise was half wrong.** `docs/research/zoning.md`,
  `proposer.md` §1/§6.1/§7, `CONTEXT.md`, `experiments/zoning/` (2 500 Swiss
  dwellings). *"Everything this system optimises is pairwise"* is **false** —
  `wet.plumbing_group_count` is a hard set-versus-set predicate today, and
  `solver-formulation.md` already records that *"reachable and clustered are the
  same constraint with different node sets"*. So a **Sleeping group** is that
  routine on a third node set, and three of the ticket's four properties cost
  nothing new. **D8 is the answer and it turns on where ADR 0014 stops**: shape
  entered the contract because L-ness is a property of the truth being copied and
  only the Proposal has seen it; a sleeping group is a property of **Room type**,
  which the `ResolvedBrief` already carries, so there is nothing to tell the
  solver it does not know. **≤ 2 sleeping groups covers 97.5 %** of real
  dwellings — the same number `wet` clustering landed on, reached independently —
  and demanding *one* would reject 30 %. **Inferred, never a Brief field**: every
  surveyed product makes adjacency user-authored and every one of them sells to a
  practitioner who can draw a bubble diagram; C2's buyer cannot. ⚠️ **Four of
  this session's own claims were withdrawn**, and the sharpest is that a
  *withdrawal* was the error — the facade property was dropped on a per-m²
  normalisation, when "the living room gets the best elevation" is a claim about
  an **absolute scarce** resource: measured absolutely the social Room takes the
  longest exterior run **73.7 % to 26.3 %, no ties**, and is dual-aspect 2.4× as
  often, all of it topological and needing no site. ⚠️ **A candidate hard rule
  died as threshold-dominated** — "every bedroom touches circulation" reads
  52.9 % at the shipped 1.00 m contact run, 66.2 % at 0.80 and **78.4 % at
  0.60** — H8's *"dead from 7 rooms"* confound again. ⚠️ **`is_private` did not
  mean what `CONTEXT.md` said**: the flag is true on the wet types, the glossary
  described the sleeping set, and a zoning rule reaching for "the bedrooms" would
  have **silently acquired the bathrooms**. ⚠️ **29 % of real dwellings come out
  disconnected** on the contact graph at 1.00 m — flagged, not concluded, and
  handed to the two tickets that own the conversion. ⚠️ The hard bound's honest
  limit: 97.5 % of real dwellings already pass, so **the four soft rules carry the
  work** and the hard one is insurance against a generator nobody has run.
- [What geometry an IfcSpace actually gets](tickets/41-what-geometry-an-ifcspace-gets.md)
  — **one extrusion over one arbitrary closed profile, `h_clear` tall; the space
  quantity set goes from four written to ten; IFC check 11 → 16.**
  `ifc-export.md` §6.1, §8.2, §8.2a, §8.2b, §8.4a, §12. RV's own concept template
  is quoted first-hand and **permits `IfcArbitraryClosedProfileDef`**, so ADR
  0014's open question is closed. ⚠️ **Two of the ticket's premises were false.**
  The rectangles it weighed the L against **do not exist** — the entity census is
  12 `IfcArbitraryClosedProfileDef` and **zero** `IfcRectangleProfileDef`, because
  `ifcopenshell` builds an arbitrary profile for a plain rectangular wall — so an L
  costs no new entity type, and the `IfcIndexedPolyCurve` Revit risk was **always a
  wall question**, never a Space one. And `Qto_SpaceBaseQuantities` has **no
  `GrossHeight` and no `NetHeight`**; the argument built on them is about
  properties that do not exist. ⚠️ **The one-word height fix was not one word**:
  IFC4 defines `Height` from the **base slab**, not the finished floor, so ADR
  0012's declared understatement had to be *published in the file* —
  `BimEngine_VerticalConvention` on `IfcBuilding`, which is the half of ADR 0012 no
  reader of the IFC could previously find. ⚠️ **Nine of thirteen space quantities
  were in neither the written set nor the omission register** — forgotten, the one
  state that register exists to prevent — and `NetPerimeter` was **specified
  wrong**: IFC4 subtracts openings from it, so the old number was `GrossPerimeter`
  under the wrong name. ✅ **A debt from another ticket is half paid**:
  `NetPlannedArea` now carries the Brief's programme beside the delivered area, so
  the Practitioner sees the delta *The whole of C2's user* found invisible; the
  Homeowner-facing half is still owed. ✅ Item 3 needed **no decision** — ticket 28
  had already bound Room-pair derivation in `CONTEXT.md`; §11 gains a
  cross-reference plus the failure `CONTEXT.md` misses, that part pairs **split** a
  real wall segment as well as inventing a false one.

- [What the engine says when the Envelope is bigger than the programme](tickets/38-what-the-engine-says-when-the-envelope-is-bigger-than-the-programme.md)
  — **§9.4 is six bounds and one function, and not one severity was chosen.** ADR
  0015: a parse-time bound that is the arithmetic **pre-image** of a validator rule
  inherits that rule's severity *and* its threshold. Four of six are pre-images; the
  other two are ADR 0013's scope gate, which has none and says so. The upper bound is
  **hard** — two hard rules make the assignment illegal, so *warn and proceed* is a
  false promise — and it **proposes nothing**, naming two edits instead, because a
  60 m² living room is the 40 m² WC wearing a better name. ⚠️ **The ticket's premise
  for merging the two checks was false**: `target_area` is `ümumi sahə` and excludes
  partitions, so a stated Brief against itself is exact net-versus-net arithmetic
  with **no partition term at all** — the term is correct only where a *dimension* is
  stated, and that one term is what makes them two sentences. ✅ **ADR 0014's
  circulation rule turns out to be sourced, not chosen**: `resolve` invents **exactly
  one `hall`**, because AzDTN cl. 5.2 lists `holl` among the auxiliary spaces a
  dwelling must have — so `corridor` and `entrance_lobby` are **unreachable in v1**
  and the table's one unsourced Azerbaijani name is on no shipping path. ⚠️ **A third
  case nobody had ticketed**: §5 discarded a stated `target_area` entirely — *"95 m²,
  four rooms"* built a ~48 m² box and never mentioned the 95, so that case never
  reached a solve to fail at. ✅ Bound 6's **one inexact number is measured**:
  *The partition footprint has a mean and no spread* published the spread and wrote
  it into §9.4 directly — an **eight-row table over room count**, not the two
  constants that handoff asked for. It also corrected this row's own premise: the
  5.7 % was never pooled across all room counts, `analyse.py` had already filtered
  it to C13's 4–10 band and neither quote of it said so.

- [The partition footprint has a mean and no spread](tickets/44-the-partition-footprint-has-a-mean-and-no-spread.md)
  — **the spread exists, the centre held, and the answer is a table.** p5 **3.53 %**,
  p50 **5.75 %**, p99 **8.87 %** — a 22 % coefficient of variation behind what
  `brief.md` shipped as one number. `brief.md` §9.4 bound 6's `f_hi`/`f_lo` are now an
  **eight-row table over engine room count, not two constants**: ρ = +0.379 and the
  median climbs **4.30 % at four rooms to 6.37 % at ten**, so a pooled figure excuses a
  four-room Brief with eight-room partition density while the four-room figure alone
  over-refuses at nine. ✅ **The sign is derived, not chosen** — the refusal threshold
  *falls* as f rises, so `f_hi` is the upper tail and the warn lands on a strict
  superset. ✅ **`f_hi` ships at p99, not the p95 the ticket asked for**, because the
  two errors are not symmetric: too low refuses a buildable Brief, too high only sends
  a doomed one to a solve that explains it correctly. ✅ **5.7 % reproduced at 5.71 %
  on a disjoint, unconditioned sample** — the original population is unreproducible in
  principle, since ADR 0016 replaced the fit its floors came from. **What it decides,
  priced**: bound 6 refuses a four-room Brief above **92.53 m²** of stated interior, so
  the spread is worth ~2 m² of ordinary Baku four-otaq flats — and today's point
  estimate gives bound 6 **no warn band at all**, only a refusal. ⚠️ **The remaining
  limit is real**: `f_hi` restores ADR 0015's implication **empirically, not provably**
  — it is a p99 of *corpus* dwellings, and no Proposer has been run, so the engine's
  own reachable maximum is unmeasured. ⚠️ **The `n = 3` row rests on 422 dwellings.**
  ✅ It also left the harness a **committed 479 KB series** so the next percentile
  costs seconds, not 46 minutes — the reason 38 could only address *whoever next runs
  the harness*.

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
  before ADR 0010. ✅ **Half of that is now answered and is no longer fog**: `brief.md` §5
  rung 1 sizes a stated total as `interior = target_area × (1 + f)`, which also retires
  `efficiency` on that path — the quantity it stood in for is measured. What stays fog is
  the *aspect and diversity* half, and ⚠️ the constant `f` is a point estimate until *The
  partition footprint has a mean and no spread* lands. **Sharpened again by *What a room's area is allowed to be*:** the
  per-type growth curve is now measured, so an invented Envelope no longer has to guess
  how a bigger box distributes — 40 m² more dwelling buys the living room **+7.99 m²**,
  circulation **+4.00**, and a bedroom **+0.08**. And the diversity asymmetry gets a
  second reading: an aspect-ratio axis varies the *box*, while what actually varies
  between real dwellings of one size is **which room absorbs** — a diversity axis a
  **stated** Envelope can have too, which is exactly the case that currently gets none.
  ⚠️ **And the asymmetry now has a number, and a second cause the proposed patch does
  not reach.** Holding the envelope *geometry* identical and varying only the edge
  ring's typing, six survivors of one Brief differ by (mean pairwise fraction of floor
  cells whose room kind differs) **0.54× at 5 rooms and 0.73× at 7** going from
  detached to corpus-median — a flat's variants are roughly **half** as different as
  a house's at 5 rooms, *before any diversity axis is handed out*. ⚠️ **Quote the
  ratio, not the figure**: the solver stops on wall-clock at 8 workers and is not
  reproducible, and a single-pass version of the probe returned 0.283 and 0.263 for
  one cell; over three repeats the two exposures' ranges do not overlap, which is what
  makes the gap solid. The mechanism is
  **H8**: habitable rooms are pinned to the exterior run, so fewer exterior edges means
  fewer distinguishable arrangements. Adding an aspect-ratio axis to stated Envelopes
  therefore closes at most half of this, and the half it does not close is the half that
  applies to every flat. `experiments/envelope-exposure/`, which imports `solver-toy` rather than
  editing it.
  **Sharpened a third time by *Homeowner product surface*:** the wait screen is settled —
  survivors stream in and the **reject count is shown**, because C6's *generate many,
  reject most* is the product story and someone who has watched fourteen examined and
  four pass can understand a run that passes none. That fixes the *shape* of the answer
  and leaves the economics untouched. It also hands this patch a candidate for its "how
  does a Homeowner choose" half: the gallery's **difference line** — largest room,
  daylight side, what the front door opens onto — which is **computed and not scored**,
  deliberately, because a visible score makes people pick the number instead of the home.
- **What a corpus-shaped product looks like** — **two of its three parts have closed.**
  *Brief schema and parsing contract* answered whether the **Brief's defaults** come
  from the corpus: they do, as the ladder's second rung, where the region profile is
  silent. And the retrieval line is no longer a computation nobody owns — the
  `ResolvedBrief` carries `retrieval_pool_size` in its `engine_view`, so **what a
  Homeowner is told** is now purely a surface question for *Homeowner product surface*.
  Fog is what remains: whether generation is **biased toward corpus-typical shapes**.
  **Sharpened by *The room-count envelope v1 promises*, with a concrete instance:** the
  corpus's own room-count distribution is *not* the Brief distribution. 948 Swiss dwellings
  hold one interior room and 317 hold two, but a Brief that names a habitable room, a
  kitchen and a bathroom is at three before `resolve` adds anything — so that mass is
  `apartment_id` grouping, not a market. Any statistic taken off the corpus and shown to a
  Homeowner inherits that gap, and the band's floor is the first place it was noticed.
  **Sharpened again by *Re-measure the conversion at two rectangles per Room*, and this
  time a bias was removed rather than found.** The conversion itself was skewing the
  training corpus small — it converted 83 % of 4-room dwellings against 46 % of 10-room,
  so a model trained on survivors was learning that homes are smaller and simpler than
  they are. At two rectangles the spread is 35 points → 12 and the dropped set's median
  size gap narrows from 6-versus-8 rooms to 7-versus-8. What is left of this patch is
  the half no conversion can fix: the corpus's own room-count distribution is still not
  the Brief distribution, and **`STOREROOM`-heavy dwellings are still dropped at 1.57×**,
  so the surviving corpus under-represents the flat with a lot of small ancillary rooms.
- **Plan quality beyond the validator** — there now *is* a ranking signal (six soft
  rules, two warns, including the aspect-ratio term added because a plan can pass
  everything and still read as generated). Fog is whether it correlates with human
  judgement at all: the eval protocol, the perceptual metric, or held-out likelihood.
  **Sharpened by *Where a set-versus-set property lives*, and this is the first thing
  ever handed to it that is not a threshold:** three terms — sleeping-group count,
  longest-run allocation, social transit — are **computable on a corpus dwelling and
  on a generated Plan by the same code**, which is exactly what a held-out comparison
  needs and what corner displacement cannot be, a real dwelling having no Proposal to
  be displaced from. `proposer.md` §6.1 takes all three with the corpus distribution
  as the target rather than a threshold. What stays fog is the half that always was:
  **whether any of it tracks what a person would say**, which no corpus statistic can
  answer. ⚠️ And a caution the terms carry: all three were measured on *real*
  dwellings, so they describe the target, not the gap — **nobody has run a Proposer**,
  so the distance a generated Plan sits from that distribution is unmeasured.
- **Fixtures and furniture** — do we place them, and is furniture-fit a constraint or a
  render? Two hooks exist: the ergonomic minima are **derived from fixture footprints**,
  so fixtures are already implicit in the hard set; and
  `open.wc_door_outward_pan_overlap` sits `deferred` with its 250 mm, waiting only for a
  pan to exist. ✅ **The surface half is answered** by *Homeowner product surface*:
  the Homeowner's plan **renders fixtures**, labelled as scale and not design, toggleable,
  and absent from the Plan, the DXF and the IFC. It costs nothing to assert because
  `ergonomic.fixtures_mm` already ships **fourteen footprints as `verified`** (AD M
  Appendix D, OGL, `body_zone` 300) and **all eighteen** room floors are derived from a
  *named packing* of them. So the hook is now paying out on one side. What stays fog is
  the expensive half — whether furniture-fit becomes a **constraint** — and it is now
  sharper: a render that a Homeowner sees creates the expectation that the furniture
  drawn actually fits, which is a promise the solver does not currently make.
- **The ordered entry sequence, and whether it is worth new integers** — ⚠️ **now a
  ticket, not fog**: *What an ordered entry sequence costs the solver*, blocked on
  *The solver has only ever seen guillotine layouts*. It is the **one** property of
  the four *Where a set-versus-set property lives* examined that needs machinery this
  formulation does not have — flow gives reachability, not *how far along* a walk a
  Room sits — and the encoding wants a per-Room hop-count integer on a model whose
  H8 note specifically records needing **"no auxiliary integers"**, at 15 s, on the
  **edge** of the feasibility cliff. Left here is the judgement the ticket defers:
  whether the three cheap properties already shipped capture most of what *reads as
  designed* means.

- **Angled walls** — they genuinely break the coordinate model and are genuinely v2.
  ⚠️ **Renamed from "Non-orthogonal geometry", which was two questions wearing one name.**
  An L-shaped room is *orthogonal*, and filing it here made a cheap question inherit an
  expensive deferral, so every downstream ticket inherited *one box per Room* unweighed.
  Split out as *Whether a Room may be more than one rectangle*, **now closed** — ADR
  0014 gives a Room two rectangles and leaves this patch holding only the genuinely
  angled case. ✅ **And that case is now sized.** Rooms needing three rectangles or
  more are **35.0 %** off-axis by more than a tenth of their perimeter, against
  **4.45 %** at two and **0.63 %** at one — so a third of what looked like complex
  room shapes is a wall a couple of degrees off axis, rendered as a 250 mm
  staircase. **No value of k reaches it**, which is what makes this a separate
  problem rather than a harder version of the one just solved. Carries an estimate
  of its own size for the first time: fix this and the two-rectangle model covers
  most of what is left. The Envelope's ≤2-notch cap is settled and
  measured-vindicated (ADR 0003). ✅ Its **deliberately unbuilt dependency** is
  discharged: room-tag-at-centroid was exact only while every Space was a
  rectangle, and `annotation.md` §7 now tags the **larger part** — a Room's own
  centroid can land outside its own Space, which `erosion_check.py` asserts rather
  than fears.
- **Structural and services reality** — load-bearing walls, plumbing stacks, risers. The
  hook is deliberate: a wall's `load_bearing` is **unknown, not false**, and party walls
  now exist in the model still carrying `None`, so the hook is paying for something
  concrete rather than being merely prudent. **It has now been charged a second time and
  in public:** `Pset_WallCommon.LoadBearing` is an `IfcBoolean` with no third state, so
  every exported wall **omits** it, and the IFC gate asserts the omission — the unknown
  is visible in the shipped artefact, not just in the model. ⚠️ Note the profile already
  publishes `t_int_bearing` = 250 as a `verified` catalogue value that **no wall type
  ships**, so the structural question has a number waiting as well as a field.
- **Frontend rendering and manipulation** — *viewing* is largely settled: Next.js/TS over
  a JSON BFF, an eager SVG preview per survivor, one `Drawing` with two presentations and
  an audience per element, so the preview is a filter and not a second annotation engine.
  Fog is **manipulation** — canvas, WebGL or SVG-in-DOM — and how it couples to C7.
- **Persistence, accounts, hosting** — where projects live, what a session is. Known
  consequence: the honest end state for a job model is a **queue plus a result store**
  with the engine a pure worker and no HTTP surface at all, deferred because the broker
  and store *are* this patch. Expect the transport to move when it clears. ✅ **Narrowed
  by *Homeowner product surface*, which declines to grab it:** the v1 surface needs **no
  backend at all** — no accounts, and the `StatedBrief` serialised into the URL on every
  edit, so a refresh restores, history is undo and a bookmark is save. The link carries
  the **request, not the results**, because generation is not reproducible from a Brief
  alone. So this patch is not blocking the surface, and what it is actually for is
  narrower than it looked: sharing a *result*, and coming back to one.
- **Revit round-trip specifics** — C2 promises the engine won't preclude it. ⚠️ The
  research section that was supposed to price it **was never written**, so this patch
  currently rests on nothing. **Sharpened by *What IFC the engine actually emits*, and
  the news is bad:** the model view that would have carried a round-trip does not
  exist — buildingSMART say *"Design Transfer View never materialised into an official
  MVD"*, **zero** products are certified for it, and its own documentation calls it a
  *one-way* transfer. Revit is certified for **Reference View 1.2, export only**. So a
  round-trip is not something an MVD choice can buy, and whatever this patch turns out
  to be, it is not "pick the other view". One concrete pre-build test is now named
  rather than fog: whether Revit's importer handles `IfcIndexedPolyCurve` identically
  to `IfcPolyline`, which *"could not be confirmed"* from primary sources.
  **Sharpened again by *What geometry an IfcSpace actually gets*, and the test just
  got harder to avoid:** the risk is a **wall** risk, not a Space one —
  `add_wall_representation` builds an `IfcArbitraryClosedProfileDef` on an
  `IfcIndexedPolyCurve` for a plain **rectangular** wall, so **every wall in the file
  already carries it**, and the concave Space ADR 0014 introduced adds nothing. Nor
  can it be dodged by preferring `IfcPolyline`: RV1.2's own
  `Body SweptSolid PolyCurve Geometry` template **names `IfcIndexedPolyCurve` as the
  `OuterCurve`**, so the entity is prescribed by the view, not chosen by us. If Revit
  mishandles it, the answer is not a different curve — it is a different view, and
  §11 already records that there is no other view to move to.
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
  harder**. Only the solve-time side is still unmeasured. ⚠️ **A third measurement, from
  *Whether a Room may be more than one rectangle*, says the deletion is wider than
  {5, 6} and is not a t_int effect at all**: `scenarios.make_brief` finds **no
  feasible room-type assignment below 7 rooms** once minima are eroded — at
  `t_int` 100, 120 *and* 150, and at both `detached` and `corpus_median` exposure —
  where at `clear_t = 0` every one of 4, 5 and 6 builds. It is the toy's own
  minima rather than the shipped ergonomic layer, so it corroborates a direction
  rather than settling a number; what it settles is that **no solver measurement
  on this map covers the bottom half of C13's own 3–10 band.** ⚠️ **And the
  deletion figure itself is now stale** — it was computed at `t_int` 120, which ADR 0010 makes 150, moving the
  residue class from 130 to 100 mod 250. Recompute before quoting it again. *One internal thickness* supplies a **partial** starting point and not a conclusion: the 120 → 150 move cost **253 solve cells either way**, so no per-room ceiling changed — but the deletion also turns on the Envelope's own re-snapping, which that arithmetic does not touch.

## Out of scope

Ruled beyond this destination. Does not graduate; returns only as a fresh effort.

- **Permit-submittable output and legal code compliance.** C8. Liability and jurisdiction
  swamp; every surveyed vendor that claimed it was doing LLM-Q&A over a user-uploaded PDF.
- **Multi-storey buildings, stair alignment across floors.** C5. The next product.
- **Validating `f_hi` against the engine's own output rather than the corpus.** Named
  by *The partition footprint has a mean and no spread*. ADR 0015's implication needs
  `f_hi` to bound the partition footprint of *every* Plan the engine can reach; what
  ships is a p99 of **corpus** dwellings, a proxy. Closing that gap means running a
  Proposer and measuring the Plans it produces — which needs the build, so it is past
  this Destination by C1, not fog. Recorded here rather than left implicit, because the
  next reader of `brief.md` §13 will otherwise ticket it.
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
  *Building scope and envelope handling*. **Charged a second time by *The Plan has no
  vertical dimension*, and this time it costs a shipped column:** whether a window needs a fall
  barrier turns on the drop below it, so with no site and one Storey at elevation 0 the engine
  cannot evaluate AzDTN 2.7-2 cl. 8.3's trigger at all, and `annotation.md`'s `Fall barrier`
  column reads `—` for every window. The guarding *height* is statutory and shipped; only the
  *when* is unknowable, and it stays unknowable while this is out of scope. The Envelope is stated or derived from the
  programme and fixed before the solve; the Acceptance bar's window rules are
  topological, never solar. A **north angle is still stored**, used only for the north
  arrow and as a soft Brief preference.
- **An existing plan as input — image, PDF or DWG.** Ruled out by *Brief schema and
  parsing contract*, and it is the one place the market has clearly settled somewhere
  we have not: **every** Homeowner-facing product surveyed takes one — Maket (plan
  image or PDF), Snaptrude (RFP and code PDFs), Synaps (DWG/DXF with layers and
  dimension styles preserved). Out of scope rather than fog because it is a second
  *input modality*, not a step on the route to this Destination: understanding a
  raster plan is *Rectangularising real rooms* pointed at an image with none of the
  corpus's ground truth. Recorded so a redraw starts from the fact rather than
  rediscovering it.
- **Analysis-grade IFC — 2nd-level space boundaries, and any energy, lighting or CFD
  model.** Ruled out by *What IFC the engine actually emits*. `IfcRelSpaceBoundary` is
  outside Reference View, and the level worth having exists for *"energy analysis,
  lighting analysis, fluid dynamics"* — analyses this engine cannot supply inputs for:
  no U-values, no glazing specification, and a `t_ext_total` that is itself
  `engine_choice` and provisional. Authoring them would assert a capability we do not
  have. **Precluded by nothing**, and that is the point: `CONTEXT.md`'s **Wall segment**
  *is* a 2nd-level boundary with its corresponding twin across the wall, so the data is
  already materialised and one spec section is all that stands between it and the file.
- **A second region profile in v1, and any claim of regional *layouts*.** Ruled out by
  *Which region profiles ship in v1*. A second *standards* profile is ~30 numbers in a
  data file; a second *layout* region is a corpus that does not exist. Shipping one
  profile costs almost nothing — *implying* it brings regional layouts with it would be
  the lie. `DE`, `US` and the `IN`/`JP`/`AU`/`CN` stubs are deleted from the enum; `UK`
  survives only as a test fixture.
