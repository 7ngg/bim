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
| Plan geometry model — Wall, WallSegment, Room/Space, integer mm, hosted Openings, wall **layer sets** | settled | ✅ its *one box per Room* premise is **weighed and reversed**: a Space is **one or two rectangles** and the Proposal decides which — ADR 0014. ⚠️ ADR 0001's erosion is untouched and is now **asserted** rather than inherited, but `acceptance-bar.md` §9's sliver *argument* is dead and replaced. ⚠️ **ADR 0001 consequence 3 is amended by ADR 0021**: its contact threshold reserved the structural opening and **nothing else** — the `+ t_int` in it is only the centreline-to-clear correction, so zero jamb and zero nib — which put it 400 mm *below* two hard rules binding the same segment. At a minimum-length contact it admitted exactly **one** door position, mid-wall, so the threshold was **specifying** the room an architect would redraw rather than merely permitting it. ✅ **The row's last open ticket is closed and ADR 0001 did not move** — [One wall weight where a real plan draws three](tickets/36-one-wall-weight-where-a-real-plan-has-three.md), ADR 0026. It had been open since *One internal thickness against a corpus with no module* closed and appeared nowhere in this table until 51 placed it, which is the UNOWNED state the table exists to catch. **All three priced shapes are refused and consequence 5 is untouched**: the 76,1 % is measured on *surveyed built* dwellings, whose three weights exist because an engineer decided the load paths first, so it is a **working-drawing** property and this engine emits a concept-stage design. **Nothing in the pipeline could draw it regardless** — ADR 0003 c3, `fit_rects.py:125` destroying per-wall thickness at conversion, and no thickness token in §2.3. The Plan draws **two** weights and says so in a general note on the sheet. ⚠️ **Shape B is REFUTED rather than unchosen, and the ticket had it backwards**: *"uniformity survives where it is load-bearing — the solve"* buys nothing, because **no hard rule binds the solve alone** — B leaves **up to 4,9 points of Σ Space** unassigned against a hard `model.no_unassigned_area`, or kills `model.space_matches_erosion` if that void is absorbed. Both hard rules stand today. ⚠️ **The gap is reclassified, not closed**, and what is left is `annotation.md`'s: two general notes individually true and jointly misleading, and a Drawing check going **12 → 13** |
| Envelope — inner-face ring of typed edges, rect/L/U/T | settled | ✅ **one Brief has one Envelope *area* and many Envelope *boxes*** — ADR 0020. **H8 and the notch cap are both paid, and the object is settled.** ✅ **The cap stands at two and the shape family is refused at a measured ceiling** — [The two-notch cap is now evidenced, and more notches is not the fix](tickets/47-the-two-notch-cap-is-now-evidenced.md), ADR 0003's second amendment. **The ticket was mis-posed and the measurement says so**: there is no ground truth on the generation side to be unfaithful to — `shape` left the `ResolvedBrief` and ADR 0020 derives each box from the *donor's* notch share — so the tail is a **donor-quality** fact, not an Envelope one. **Sixteen tail dwellings are inside the cap already** and still lose > 0.10; at `notches_all` = 1 the loss is identical at every k, because a notch is one *rectangle* and a complement component need not be one. The tail splits **38.2 % rectilinear / 49.5 % off-axis**, and a vertex-budget ring — the only coherent widening — tops out at **4.17 % of the corpus**, 46.3 % of which still fails at four notches. ✅ *H8 and the single-aspect flat* found the frontage crisis did not exist — the table ran on placeholder minima and the exposure distribution it was checked against **measured one room per dwelling**, not the dwelling. ⚠️ **That second defect is this row's problem, not H8's**: `flat_single_aspect` and `corpus_median` are both fitted to the wrong column — real p25 **0.51** against 0.23, real median **0.67** against 0.37 — so every Envelope number measured at either preset was measured at roughly half the real exposure. ~~including ADR 0003's notch evidence~~ — **that part was false**: the notch cap reads no exposure at all, and 49 checked rather than assumed it. ✅ **Paid** — [The exposure presets were fitted to a measurement of one room](tickets/49-the-exposure-presets-were-fitted-to-one-room.md), and it cost three published results rather than the one it expected. ADR 0018 asserted both readings four paragraphs apart, and the one everything downstream assumed costs **56.15 % of the index** to `area.invented_envelope_hard` on donor geometry alone, because the notch is a median **12.55 %** of the bbox (p10 3.13 %, p90 23.30 %). Floor is now the pool invariant and the box is derived per candidate; `rules.json` sees **no change**, which is the opposite of what the ticket expected. ✅ **`shape` leaves the `ResolvedBrief`** — a dense object had nowhere to put *unknown*, and both defaults are refused. ✅ **The stated-`shape` gate moves to notch *area share*, and the count gate was mis-labelling the whole index**: read materially (≥ 5 % of bbox) the corpus is 52.96 % `L`, not 8.72 % — the biggest win is the common case, at 6×. ⚠️ **ADR 0018's fidelity numbers are proportion, not area**: `fit_warp.py:373-384` normalises absolute area away, so **the warp has never been measured against a stated `target_area`** — now possible, and owed by `experiments/warp/`'s next holder. ✅ **ADR 0003 §7 is re-read as *one ring per candidate*, fixed before that candidate's solve** — written by *The two-notch cap is now evidenced* after two holders declined to write blind. What makes it safe is now stated: the entrance edge is identified **by side**, never by ring index. ⚠️ **"Fill the notch" is recorded and not taken** — it dissolves the stated-shape cliff and re-opens ADR 0018's monotone-warp theorem. ✅ ADR 0003's notch cap is now measured from the corpus side: 90.16 % of converted dwellings use both notches, 8.72 % one, 1.12 % none. ✅ **The non-monotonicity stands and both its numbers were wrong.** Re-run at the re-fitted presets: single-aspect fails at **6 only** (3/5 at 8), not "6, 7, 8, mostly at 9", and **n = 6 at corpus-median is 0/5 → 5/5 — that failure is gone**. *"Dead from n rooms" is still measuring the envelope n selects, not n*, and n = 6 is still the worst row across three presets because `envelope_for(6)` picks an L. ⚠️ **But six rooms is now unexplained**: at the re-fitted preset it has **5 250 mm of frontage slack**, so it is not the frontage arithmetic and nothing has identified what it is. ⚠️ `solver-formulation.md`'s *"`flat_single_aspect` is arithmetically dead from 7 rooms, and no solver is involved"* is **overturned outright** — alive by 4 000 mm at seven and by 14 500 at twelve — as is its whole `vs corpus` column, which compares against the uncorrected distribution. Both are ticket 52's to write. How an **invented** Envelope is derived is still fog, under *Variant generation and ranking*. ✅ **ADR 0003's two-notch cap is evidenced and the shape family survived the trial** — two is the knee (median envelope loss 0.161 / 0.050 / **0.018** / 0.011 / 0.010 at k = 0…4), a higher cap converts *worse* (88.0 % against 93.2 %), and the widening was refused on measurement rather than on cost. ⚠️ **What it hands on is not an Envelope question**: envelope loss is a *predictor* and a poor gate — 42.2 % of the loss tail converts faithfully anyway, 12.70 % outside it does not, and an IoU cut removes 10.09 % of the *most faithful* envelope band. The quantity is **worst-room IoU**, already in every fit record, and its population (**154 dwellings, 6.65 % of the index**) is two thirds invisible to either proxy. Owed by `proposer.md`'s next holder — index field, hard gate at 0.30, rank above it — written out in full on 47 so it is transcribed, not re-derived. ⚠️ H8 is also handed a corpus-side number: **4.1 % of façade-facing rooms lose their frontage in conversion**, 22.5 % of dwellings lose one — the only conversion fidelity figure nothing constrains. ⚠️ **And H8 now has one more room competing for frontage**: *Opening placement rules* moves `kitchen.needs_window` to **true** — three shipped places disagreed and AzDTN cl. 9.12 is `verified` and mandatory for living rooms *and* kitchens — so the kitchen is pulled onto the façade by `win.habitable_has_window`, which that ticket also had to re-key because **a party wall is `External` and the rule was satisfiable on one** |
| Corpus conversion — how a real dwelling becomes retrieval and training data | settled | ✅ **the 31 % drop is paid, and it was mostly a price for a deleted constraint** — ADR 0016 takes Swiss **30.70 % → 9.74 %** and ResPlan **40.10 % → 6.40 %**, paired, zero dwellings lost, every ADR 0008 guarantee re-asserted. **The slope moved more than the level**: the 83 %-at-4-rooms against 46 %-at-10 spread goes 35 points → 12, so the conversion has stopped preferring small dwellings. The `swiss_fit.json` labelling defect is **fixed at source**. ✅ **A converted dwelling has now been looked at, and it reads as a home** — 67 rendered beside their originals, ADR 0017. ⚠️ But **three of this row's own fidelity headlines are constraints restated, not measurements**: `edges_lost = 0`, zero flipped directions and the ±10 % area band are all posted hard, so *"zero adjacencies destroyed"* and *"9.5 % refused"* are one fact stated twice. Quote cell agreement **with worst-room IoU**, the refusal rate, and `boundary_lost`. ⚠️ Two failure modes left this row and became tickets — [The dwelling that is built on two angles](tickets/46-the-dwelling-that-is-built-on-two-angles.md), **still open and this row's**, and *The two-notch cap is now evidenced*, closed; two more were handed to the acceptance bar and to H8. ⚠️ **`why_k.clean()` does not do what it says** and its 58.3 % / 31.03 % figures remain an artefact. ⚠️ ADR 0008's *"decidable, not a timeout"* **is dead**: 1.27 % of Swiss and 16.5 % of ResPlan return UNKNOWN at 10 s, and ResPlan needs 30 s to decide at all |
| Solver projection — CP-SAT, 250 mm grid, 15 s, τ = 4 | settled | ✅ **the guillotine premise is discharged and nothing moved** — ADR 0019, 483 solves over 568 slots: 4 discordant each way, McNemar **p = 1.00**, and **zero** discordant at 8–16 rooms. 15 s, τ = 4 and ADR 0007 all stand at their published values. ✅ **Item 4 inverted**: a non-guillotine target reaches INFEASIBLE *less* often, **17 against 2, p = 0.0007** — the fallback fires less, not more, ⚠️ by an **unexplained** mechanism with the three obvious candidates excluded. ⚠️ **Two premises were false**: τ gates on separation margin, not adjacency, and those distributions are *identical* between arms; and **no experiment on this map ever ran at `t_int` = 120** — every one ran at **100**. ⚠️ The bottom of C13's band, below 7 rooms, still has **no non-guillotine measurement of any kind**. **[What an ordered entry sequence costs the solver](tickets/43-what-an-ordered-entry-sequence-costs-the-solver.md) is now unblocked** — ⚠️ and it now shares its whole directory with **[The toy Envelope is more compact than a real dwelling](tickets/52-the-toy-envelope-is-more-compact-than-a-real-dwelling.md)**, raised by 49 and holding three defects measured from the corpus side: the Envelope is **more compact than a real dwelling** and increasingly so with n (perimeter/area **0.390 against 0.572** at twelve rooms), **`AREA_PER_ROOM_M2` is 9.65 against a corpus median 11.36 m²** — 29's fixture defect, now with a number — and **`Envelope.exterior_fraction` double-counts**, 144 grid units of true perimeter counted as 180. It also holds `solver-formulation.md`'s exposure section, which is **wrong twice over** and whose *"arithmetically dead from 7 rooms"* table is **overturned outright**. Not at once with 43. — ⚠️ and it arrives holding a **second, unpriced job**: *Opening placement rules* took the contact threshold from `w_struct + t_int` to `w_struct + t_int + 400` (ADR 0021), because the old one reserved **zero jamb and zero nib** against two hard rules that require both. The arithmetic is exact and shipped on it; **the INFEASIBLE rate it costs has not been measured**, and `experiments/solver-toy/` is 43's |
| Proposer source B — trained transformer: architecture, corpus prep, metric, stopping rule | settled | ✅ **its evaluation has four plan-quality terms** — sleeping-group count, longest-run allocation, social transit and now **`frontage_reach`**, all computable on a corpus dwelling and a generated Plan by the same code, which corner displacement is not. `proposer.md` §6.1. ✅ **The daylight gap in that list is closed and the fear behind it was false** — [A third of real kitchens have no window](tickets/51-a-third-of-real-kitchens-have-no-window.md): *"a trained Proposer that learned windowless kitchens from 31 % of its data will propose them everywhere"* cannot happen, because **§2.3's model has no window token**. It emits two box slots and a presence token, so the only thing a windowless kitchen teaches it is an **interior** kitchen — a **5.88 %** prior, not 31 %. **No training filter**, on the reasoning that a landlocked room is a fact about real housing the solver already refuses hard, and trading 5.88 % of a corpus ADR 0013 calls thin to suppress a case the projection rejects anyway buys nothing. ⚠️ They are **evaluation only, not stop conditions**, and none of the four has been measured on a generated Plan because no Proposer has been run |
| Runtime and process split — engine / proposer service / BFF, job model, threads, JSON | settled | ⚠️ the honest end state (queue + result store) is fog, under *Persistence, accounts, hosting* |
| DXF export | settled | — |
| Proposal contract — what a source emits and the solver consumes | settled | ✅ **it carries no zoning, and that is the decision** — the node set is derivable from Room type, so ADR 0014's *only the Proposal knows* argument does not transfer. §1 records the refusal with its reasoning. ⚠️ The premise it was challenged on was **half false**: `wet.plumbing_group_count` is a set-versus-set predicate shipping today, so the Proposal is pairwise and the *system* is not |
| Proposer source A — retrieval-and-warp, which ships first | settled | ✅ **What the corpus is admitted on is settled, and glazing is not part of it** — [A third of real kitchens have no window](tickets/51-a-third-of-real-kitchens-have-no-window.md), ADR 0025, `proposer.md` §4.5. A donor's windows are **overwritten in every case** — §1 emits boxes with no openings, `openings.md` §6.1 glazes after the solve, the solver posts the frontage budget hard — so the index may not be selected on them. **The overlap ADR 0016 was owed is measured: the two drops COMPOUND**, lift **1.08×**, joint **44.91 %**, so filtering hands back four times what ADR 0016 bought. **The population is 6.39 %, not 43.3 %.** New index field **`frontage_reach`** and a **partition** at 1.0 in §2.2.4's pre-rank — no free parameter, because that is where the solver's own constraint sits. ⚠️ **It refuses ticket 47's gate-then-rank precedent on purpose**: worst-room IoU is a pure donor fact, `frontage_reach` is joint with the Brief's Envelope, because §2.2.6 records the conversion cannot tell `exterior` from `party` — so **6.39 % is a floor and not the residue's size**, and a gate would claim what it does not know. ⚠️ **`fit_rects.py` gains a third owed field**, alongside the cut-line frame and per-pair relation provenance. ⚠️ **Its fidelity headline is a PROPORTION and a hard rule now reads it as an absolute area** — [The warp has never been measured against a stated target area](tickets/54-the-warp-has-never-been-measured-against-a-stated-area.md), raised by *A statutory floor, posted soft, in the one region v1 ships*. `fit_warp.py:373-384` normalises absolute area away, so ADR 0018's p50 0.056 says the warp preserves a donor's *shares* and says nothing about whether a Room asked for 12 m² gets 12. 48 left it as an obligation on an unclaimed directory; the statutory floor made it a trigger. ✅ **the mechanism is specified and the warp is a solve** — `proposer.md` §2.2.1–§2.2.7, ADR 0018. Index, warp, ranking, confidence, entrance and the fidelity curve all landed, and both staleness items paid. ✅ **The gate's units were wrong a third time**: not corner noise, not severity — a monotone warp cannot destroy a separation direction at all (**21,074 asserted relations, zero confident-wrong**) — but **per-room area**, which the gate never measured. Fitting it costs no coverage and buys 5.8 × on the median Brief's worst room. ⚠️ **The Envelope is now per-candidate in its `invented` fields**, which is a contract change no consumer has been checked against, and **`shape` absent must not default to rectangular** — both owed by `brief.md`'s holder. ⚠️ Two index fields the conversion does not emit (cut-line frame, per-pair relation provenance) are owed by `fit_rects.py`'s holder, and `select_relations`'s positive-cost filter by `solver-toy`'s ⚠️ **The row's headline fidelity number was a proportion, and the absolute twin is now measured and bad** — [The warp has never been measured against a stated target area](tickets/54-the-warp-has-never-been-measured-against-a-stated-area.md), `proposer-architecture.md` §7.5. ADR 0018's p50 0.056 says the warp holds a donor's **shares**; asked for absolute area it delivers **mean −4,3 % of the floor the Brief asked for**, one-sided, and **6,7 % of Briefs have no candidate in a pool of eight** that keeps every Room above `dim.statutory_min_area` — about as much Brief-level loss again as ADR 0018's 6,9 % for every dimensional decline combined. **This does not un-settle the row**: source A still ships first, and the split is measured — ~2/5 of the damage is one constant in `brief.md` §5 rung 1, ~3/5 is the warp's own per-room distribution and survives a perfect level. The severity call is `rules.json`'s and it has no claimant. |
| Acceptance bar — **43** predicates (**44 once `dim.leg_join` lands**), enforcement sites, conformance test | settled | ✅ **The row's last decision is taken and it cost a standing constraint** — [A statutory floor, posted soft, in the one region v1 ships](tickets/50-a-statutory-floor-posted-soft.md). C14 is amended **monotonically**: a profile may RAISE a hard floor and never lower one, so `dim.statutory_min_area` is the **first hard rule on this map carrying a region** (42 → 43, subset 15 → 17), and `win.area_ratio` goes soft → hard rescoped to living rooms and kitchens. ⚠️ **This row's proudest rule was inert**: `dim.min_area` adds **0.00 %** to the hard union while being the only predicate between a Homeowner and the 3,1 m² bedroom §3 was written to forbid. ⚠️ **Do not quote the 54,51 %** — the bar does not gate the retrieval index and `market_default` is at or above `statutory_floor` in every reachable AZ cell, so the rule is strictly weaker than the target the solver already aims at. ⚠️ **The kitchen limb sits on the corpus median** (8,0 against p50 8,04), 16,88 of 19,98 marginal points; taken on §7.5's precedent. ⚠️ **The yield trigger is named and unmeasured**: the warp has never been checked against a stated `target_area`, and if it undershoots this rule collapses yield — a one-field build-time rollback, chosen over a soft rule that ships a 6,6 m² kitchen as a survivor. ⚠️ **`room-constraints.json` and `rules.json` disagreed about `statutory_floor` — warn against unread — and neither had a rule behind it.** ⚠️ **What the row still owes is transcription, not decision, and it lives in `rules.json`'s own `owed` block rather than here**: five zoning rules ready to transcribe at `zoning.md` §5b, `dim.prefer_single_part`, the message locale schema over 43 rules, `f_hi`/`f_lo` into data, `wet.shared_wall_length`'s missing gradient — and **one BLOCKING item that is 32's**, the window width series `win.area_ratio` needs to be satisfiable (reach p90 2,47 / 3,23 / 1,34 m). That is why this row is settled with no open ticket: staffable, with named owners. ✅ **the widest gap on the map is closed, and the vocabulary was the thing blocking it** — ADR 0023. **`ENGINE_CHOICE` 18 → 9**, and the nine that remain are predicates about shape or program with no magnitude to measure, so *the remaining gap is not a measurement gap*. `conf` gains a fourth value, **`fitted`**, because `verified`/`derived`/`engine_choice` marked a number fitted to 42,985 real dwellings identically to a guess — under the old vocabulary this count could never have moved however much measuring was done. **Two thresholds move and seven guesses hold**: `wet.plumbing_group_count` 2 → **3** (the ticket predicted it — the tail reaches three at **14.14 %** of real dwellings) and `area.invented_envelope_soft` 2 % → **3 %** (the 250 mm grid alone misses 2 % in **13.71 %**); `dim.aspect_ratio_hard` **is** the p99.5, at 3.02. **The three area rules landed**: `dim.max_area` and `dim.stated_target_implausible` added, `dim.market_default_area` made two-sided. ⚠️ **The `site: both` conformance subset moves 14 → 15** and the rule count 40 → **42**, both stale in `acceptance-bar.md`. ⚠️ **The number nobody had measured is the conjunction**: the hard registry rejects **84.41 %** of real Swiss dwellings as shipped and **82.31 %** under the fitted values, with **eleven of thirteen hard rules costing under a third of a point between them**. **The bar is two rules and a rounding error** — `open.fits_segment` and `win.habitable_has_window` — and neither has a threshold that could be loosened to move it; read `open.fits_segment` on real piers rather than on full-width openings and it is **61.23 %**. Both are **opening-layer** rules, placed after the solve, so a warped donor's prior of clearing the bar is set by a layer the Proposal does not carry.  ✅ **Every threshold is now fitted or declared unmeasurable, and what the row still owes is rules, not numbers** — five zoning rules, `dim.prefer_single_part`, the message locale schema and `f_hi`/`f_lo` into data, all now written into `rules.json`'s own **`owed`** block so the next holder does not reconstruct them from this map. ✅ **Opening rules are paid — and closing them found the bar contradicting the solver.** *Opening placement rules*: the contact threshold reserved `w_struct` of **clear** run and nothing else, while `open.fits_segment` and `open.leading_edge_nib` hard-require `w + 400` on that same segment, so **a solve could pass potential circulation and be hard-rejected the instant a door was placed on the run it had just certified** — ADR 0021 takes the threshold to `w + t_int + 400`. Six rule statements moved, **none added**, so the 38 count is untouched on purpose. ⚠️ Two of those moves are the bar's to publish and could not be written: **`win.habitable_has_window` was satisfiable on a party wall** (a party wall *is* `External`, so a mid-block bedroom took its daylight off the neighbour), and **`win.kitchen_windowless` can no longer fire** now `kitchen.needs_window` is true — retire-or-keep moves the count. ⚠️ And **`win.area_ratio` is the only statutory minimum on this map posted `soft`** — AzDTN cl. 9.13 is `verified` and mandatory — left alone because severity is the bar's. ✅ **The bar now has a rule of the shape *this dwelling owes a room at all*, and it cost a room type** — *A dwelling with no toilet passes every check*, ADR 0022. **Four `programme` rules, 36 → 40**, one per limb of AzDTN cl. 5.2, `scope: brief` with **no plan-side twin** — the Room set is frozen at `resolve`, so a plan-side composition predicate could never fire, and these are the first rules on this map with an **image and no pre-image**. Kitchen, washing and WC **hard** (5.99 / 7.33 / 5.19 % of real dwellings); storage **warn**, because hard it rejects **73.35 %** and the norm's own alternative is a built-in wardrobe v1 does not model. The `holl` limb gets **no rule**: `resolve` guarantees it, and a rule that cannot fire is what retired two rules above. ⚠️ **The WC limb was unshippable over eighteen Room types** — it rejected **48.32 %**, and only 5.19 of those points were toilet-less homes; the other **43.13** *have* a toilet in a room with a bath that the vocabulary could not name. Closed by a **nineteenth type**, `bathroom_combined` (1500 × 1700 = 2.5 m², rejecting 6.17 % of 35,821 real bath+WC rooms, with the corpus's own short-side p5 of **1477 mm** reproducing the derived 1500). ⚠️ **Two shipped sentences were false**: `bathroom`'s ergonomic note claimed a pan and basin that **cannot fit** (1.81 m² of fixture in a 1.70 m² room), and `shower_room` **has composed a WC pan since the layer was authored** while the AZ bridge asserted the layer *"carries no way to say the WC is inside"*. ⚠️ **cl. 5.10's restriction of the combined unit to one-otaq social stock is recorded and deliberately not enforced** — C8 forbids reading a regulatory document as a compliance target, and 67.24 % of 44,372 real dwellings combine, so it does not describe practice either. ⚠️ **Bound 8 now fights bounds 1/3/6**: adding the `wc` a refusal asks for raises Σ minima and the engine room count, so a nine-room Brief with no toilet is told to add a room *and* told it may not — nothing orders the two sentences, and it is `homeowner-surface.md`'s. ✅ **the 40 m² WC is answered**: `dim.max_area` hard at `both`, and **free in the solver** — H4's `a = w·h` already exists. ⚠️ **And five more rules are owed, from *Where a set-versus-set property lives***, specified ready to transcribe at `zoning.md` §5b — one hard (`zone.sleeping_group_count`, at most two sleeping groups, 97.5 % of real dwellings) and four soft or warn, of which **`zone.no_social_transit` is the one nobody had written**: `circ.no_private_transit` blocks routing through a bedroom and *nothing* blocks routing through the living room, which 18.2 % of real dwellings do. ⚠️ Every dimensional rule now has to declare **which part it binds** — ADR 0014 binds minima and aspect per part, area per Room — and one new soft rule, `dim.prefer_single_part`, is owed to `rules.json`'s holder — as is a **locale dimension on every Homeowner-facing message**, since §11 requires a plain-language message per rule, all **40** are English, and the surface is now Azerbaijani: a schema change, not a translation pass. ~~⚠️ **And nothing in the bar forbids floor that belongs to nothing**~~ — **that was false, and this row repeated it.** `model.no_unassigned_area` is **hard**, `site: both`: *"the union of all Space polygons and all Wall bodies equals the Envelope interior exactly."* Exact tiling is soft **in the solver** for a 29× faster search and hard **at the validator**, which its own note calls *"the place where that trade is prevented from shipping a hole"* — so an OPTIMAL candidate with a 1 m² unnamed hole **cannot be shown**. Checked rather than assumed by *A dwelling with no toilet passes every check*; **no rule added and none owed.** What survives is the **proposer's**: the 10.0 % measured the *conversion*, so a voided donor enters the index and the solve must absorb the hole into a bordering Room as area the Brief did not ask for — [A donor's enclosed void becomes area nobody asked for](tickets/53-a-donors-enclosed-void-becomes-area-nobody-asked-for.md) ✅ **Two rules retired by *H8 and the single-aspect flat*, 38 → 36**, because neither could fire: `win.habitable_touches_exterior` was strictly implied by `win.habitable_has_window`, and `win.kitchen_windowless` became unreachable when the kitchen took its window. Both kept in a `retired` block. `win.habitable_has_window` moves to site `both` and posts the frontage budget, so the conformance subset holds at 14. ⚠️ **The bar's corpus cost is measured for the first time and it is large**: that one rule rejects **43.3 %** of real Swiss dwellings, 23.0 points of it the kitchen alone — worse than the 26.6 % that made *What a room's area is allowed to be* refuse a p95 cap, and it carries **no threshold to move**. ⚠️ The bar also admits a **1.85 × 1.68 m double bedroom**; the room table owns that number, not a window rule. ⚠️ **`win.habitable_has_window` now carries THREE corpus costs answering three questions, and the file says which is which nowhere** — [A third of real kitchens have no window](tickets/51-a-third-of-real-kitchens-have-no-window.md): `rules.json`'s `corpus_cost` **0.4519** is the *raw* arm over 42,985 unconverted dwellings, **38.55 %** is the converted index at 46,565, and **15.97 points** is the same rule's leave-one-out contribution to the whole bar. None is wrong and none is the others; **none of them is the retrieval cost**, which is **6.39 %** and lives in `proposer.md` §4.5. One sentence, owed to this file's next holder — 51 deliberately did not write it or touch the number, because overwriting 0.4519 would destroy a measurement rather than improve one ⚠️ **`dim.statutory_min_area`'s severity is now a live question with a measured price** — [The warp has never been measured against a stated target area](tickets/54-the-warp-has-never-been-measured-against-a-stated-area.md). 50 posted it hard on the argument that a Plan reaching its soft target clears the floor by construction, and named its own reversal trigger: *a hard rule that is too strict is discovered at build time on the first Proposer run.* **That trigger has fired early.** ~~On Briefs whose every target sits on `market_default`, the rule alone costs **31,1 % of candidates** and **6,7 % of Briefs at pool-of-8**~~ — **both superseded, and the rule is about half as expensive as it was posted at**: [The sizing rung under-delivers by four per cent](tickets/56-the-sizing-rung-under-delivers-on-the-warp-path.md) found the *measurement* was carrying the difference, not the rule. Same sample, same seed, both Envelope defects fixed: **25,5 % of candidates** and **3,6 % of Briefs at pool-of-8**, with the passing kitchen's lower quartile clearing by **518 litres** rather than 85 — so *"passing by luck"* no longer describes it, though **17,4 %** of kitchens asked for 9,0 m² are still delivered under 8,0 and no sizing constant reaches that. The severity is [The statutory floor now has a price](tickets/55-does-the-statutory-floor-stay-hard-now-that-it-has-a-price.md), **now unblocked**, and its own ticket carries the corrected table. ⚠️ **Do not read it against the bar's 15,59 %** — one is a predicate's cost on generated candidates, the other the whole hard registry's survival rate on real dwellings. ⚠️ **And do not reach for the 18,8 %** — that was `calib`, which scales the box until Σ Space hits `target_area` and hands the rooms margin the Brief does not entitle them to; a correct Envelope over-delivers by **0,4 %**, not by `calib`'s 2,2 % of slack. |
| Standards table — region-invariant ergonomic floor + the `AZ` profile | settled | ✅ **the type set is nineteen, not eighteen** — `bathroom_combined`, added by *A dwelling with no toilet passes every check* because `prog.wc_exists` is unshippable without it. ⚠️ **Two of this table's own sentences were false**: `bathroom`'s note claimed a pan and a basin that **cannot fit** (1.81 m² of fixture in a 1.70 m² room) and `shower_room`'s programme **has composed a pan all along**, against an AZ bridge asserting the layer *"carries no way to say the WC is inside"*. Both corrected at source. ⚠️ **And `build_ergonomic_layer.py` was silently destructive** — it authors the arithmetic and four flags and nothing else, while three later tickets hand-edited the block it emits (`counts_as_otaq`, `brief_nameable`, `reachable_in_v1`, `counts_as_otaq_sourcing`, `corpus_medians`), so **every re-run deleted all of it without a word**, which is the exact drift its own docstring claims generation prevents. Found by tripping it; it now carries forward what it does not author and fails loudly. `gate_check.py` 229 → **238**. ✅ **all four owed items paid** — the mapping exists (`profiles.AZ.rooms.mapping`, 18 rows, 162 gates), the room names turned out to be **in AzDTN 2.7-2's own text in this repo** (14 of 18 `verified`), the three-into-one gap resolved by **keeping three** (the norm carries `hol` and `dəhliz`; `giriş holu` is ours and labelled), and the corpus medians are recorded with their tail warning — *Two room vocabularies in one file*. ✅ its thickness is measured-vindicated: 150 lands **4 mm from the corpus-optimal 146**. ⚠️ **The merged 7,58 m² hall/lobby/corridor median can default nothing** now the three stay apart — rung 2 is empty for all three. ⚠️ One resolution step — `(type, otaq_count) → target, width, name` — is **named in no spec**; handed to `brief.md`'s holder |
| Drawing — graphics, chains, schedules, tags, sheet, Drawing check | settled | ✅ **the seam is closed and it took one line to close it** — [The annotation spec is US-shaped and the drawing is now Azerbaijani](tickets/32-the-annotation-spec-is-us-shaped.md), ADR 0024: *a sheet mark is read on paper by a builder, a layer name is read on import by a program*. Sheet marks, abbreviations, the mark scheme and the separator all move to SPDS; **the layer names deliberately do not**, and the profile now carries a **test for membership** rather than a new object — *a field is region-parameterised iff a person reads it* — which is what the ticket's *do not add fields one at a time* actually needed. ✅ **ADR 0004's centreline number is dead and ADR 0010's replacement was narrowed**: tier 1 measures the **outer face of an exterior edge and the inner face of a party edge**, because *inner ring on every edge* would have made tier 1 restate the span every tier-2 chain already closes on **and left the sheet with no external footprint at all**, on a map that ships houses. ⚠️ **The BLOCKING window series exists and ticket 50's shape had to change**: it cannot be *bounded by `gost_11214_86`* because the published widths stop at 21 dm and 50's own p90 requirement is **3,23 m** — the top four members are an engine extension, marked by `published_through`, and above it the schedule prints a dimension string rather than a fabricated GOST mark. ⚠️ **And 50's *splitting buys nothing* is half false** — true when the wall run binds, false when the **catalogue top** binds, and the two were not distinguished. ⚠️ **`openings.md` §6.1 had to be rewritten by a ticket that does not hold it, and its own worked example is why: the shipped spec's example fails the shipped bar** — `living` at ratio **0,250**, nearly twice target because the increment was a whole window; `kitchen` at **0,120**, *below the now-hard floor*, described as surviving on a soft penalty; and `bedroom_single`'s window **omitted entirely**, which `win.habitable_has_window` rejects hard. ⚠️ **Two defects surfaced only because §14 was re-derived at the shipped `t_int` 150** — it had been computed at 100 and could not be patched, because the dilated domain must land on the 250 grid: **the schedule's totals row does not add up** (43,58 exact against 43,59 printed, so every total is now computed from the printed cells and the Drawing check gains a **twelfth** predicate), and **§4.5's setting-out datum names opposite ends on every non-minimal run**, with a value that is **100 mm for every internal door in every plan**. ✅ **A first-hand clause that had been dropped is landed rather than handed on a third time**: `AZS ГОСТ 21.501-2010` cl. 2.3.2 annotates a residential plan's area as a **fraction, living over useful** — 17 closed on `ümumi sahə` as a single number and the clause was recorded nowhere. ⚠️ **`faydalı sahə` and `ümumi sahə` are numerically identical in v1 and are not the same quantity**; they diverge the day a balcony is modelled. ✅ **The room tag's fallback splits by audience** and its invented-abbreviation ladder step is replaced by a schedule reference sourced twice over. ⚠️ **26's 1 650 mm bedroom was refused, and the defect it names is real**: the ergonomic layer is a *fits* floor by construction and raising it rejects 19,3 % of real rooms, but **a 1 850 × 5 400 bedroom passes every hard rule** and the number that would stop it — `market_default` 3 000 — **ships and is read by nobody**, because the only rule consuming that tier is an *area* term. `dim.prefer_wide_habitable` is owed to `rules.json` |
| **Brief and parsing contract** — the object a prompt becomes, and per C4 the real interface | settled | `docs/spec/brief.md`. ✅ **§9.4 is eight bounds and §3 is nineteen types** — *A dwelling with no toilet passes every check*, ADR 0022. Bound 8 is the mandatory-room check and it **inverts ADR 0015**: `acceptance-bar.md` §13's rules are brief-scope with no plan-side twin, so the bound *is* the rule and its severities are corpus-chosen, not inherited. §9.1 gains a fourth hard Brief error. ⚠️ **It also creates the map's first self-contradicting refusal**: adding the `wc` bound 8 asks for raises Σ minima, adds an engine room, and can push a Brief out of C13's 3–10 — a nine-room Brief with no toilet is told to add a room *and* told it may not, and nothing orders the two sentences. ✅ its **band** now has numbers, and ✅ **§9.4's upper half is closed**: six bounds, one function, and **no severity chosen** — ADR 0015 makes a parse-time bound inherit the severity and threshold of the validator rule it is the pre-image of. The Envelope-bigger-than-programme case is a **hard refusal naming two edits**, and the stated-Brief contradiction is caught net-versus-net at the 5 % `area.invented_envelope_hard` already ships. ✅ `resolve` invents **exactly one `hall`**, sourced from AzDTN cl. 5.2. ✅ **Bound 6 no longer rests on a point estimate** — *The partition footprint has a mean and no spread* measured the spread and **wrote it in rather than handing it on again**, because `brief.md` had no claimant and a second handoff would have recreated the defect that created that ticket. It came back **wider and differently shaped than asked for**: `f_hi`/`f_lo` are an **eight-row table over engine room count**, not two constants — ρ = +0.379, median 4.30 % at four rooms against 6.37 % at ten, so pooling excuses a four-room Brief with eight-room partition density — and `f_hi` ships at **p99, not p95**, because a too-low `f_hi` refuses a buildable Brief while a too-high one only sends a doomed Brief to a solve that explains it correctly. ✅ And the **5.7 % reproduced at 5.71 % on a disjoint, unconditioned sample**. ⚠️ What replaces the limit is smaller: `f_hi` restores ADR 0015's implication **empirically, not provably** — it is a p99 of *corpus* dwellings, and the engine's own reachable maximum has never been measured because no Proposer has been run. ⚠️ **Two of eighteen room types are now dead paths** the data still presents as live — `corridor` and `entrance_lobby` need `reachable_in_v1: false`, and this ticket could not write that file. ✅ **§5 is rewritten and §9.4 is now seven bounds** — *What shape an Envelope is when the Brief does not say*, ADR 0020: `shape` **leaves the `ResolvedBrief`** (a dense object had nowhere to put *unknown*, and both candidate defaults are refused), new §5.1 and §5.2 carry the gate term and the pool invariant, and bound 7 is the **only bound with no pre-image in either direction** — a stated shape warns and never refuses, falling through to source B when the pool empties, because refusing would decline a request the engine *can* serve. ⚠️ It leaves two limits: the derived box can differ **30 %** between two candidates that agree on floor to the millimetre, and **every shape number in §5.1 is Swiss and is the *conversion's* notch, not the building's** ✅ **§5 rung 1 does not under-deliver, and `f` is vindicated** — [The sizing rung under-delivers by four per cent, and `f` is not where to fix it](tickets/56-the-sizing-rung-under-delivers-on-the-warp-path.md). The ~4,2 % was **two defects in how the rig measured the Envelope** and neither was in this file: it eroded a 75 mm ring ADR 0001 does not lose (**3,7 % of `interior` at p50**), and it let the warp resize the notch, which ADR 0020's by-construction guarantee assumes it cannot (**1,5 %**). Corrected, Σ Space lands **+0,4 %** of `target_area` and `f = 0.0575` is untouched — the widening the ticket was raised to make would have oversized every Envelope on **both** proposer paths to compensate for an erosion the engine does not perform. ✅ **The `interior` reading is settled and was never a coin-flip**: the Envelope's own area at the finished inner face, because `CONTEXT.md` defines the solve domain as *"not the Envelope, and not the interior"* and `s` is a share of the **Envelope's** bbox. The domain is a **third** quantity, derived from the box, and new **§5.3** carries the three-plane table and the statement that it is source-independent. ⚠️ **What moved instead is `proposer.md` §2.2.3's, and 53 holds it**: *"the notch warps along with everything else, for free"* is what makes ADR 0020's guarantee false, worth **5,6 points** of plan-level `dim.statutory_min_area`. ⚠️ Rung 1's `f` had also been published with **no denominator** — *"the p50 of Σ Space area"*, which is not a quantity — now fixed at source. |
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
| `CONTEXT.md` | **no claimant** — 32, 31, 38, 23, 44, 48, 16, 42, 56 and 36 closed. **36 declared it**: **Wall weight** is a new term — *how many distinct cut-wall thicknesses a sheet draws; v1 draws two, envelope and internal, and never three* — carrying the fact that the 76,1 % three-weight figure is measured on **surveyed built** dwellings and is a working-drawing property, with an `_Avoid_` on blaming uniform `t_int` (the shipped 150 is 4 mm off the corpus-optimal single value; the uniformity is downstream of having no structural model at all). **Wall** gains an `_Avoid_` on **inferring `load_bearing` from thickness, length or position** — nothing in the pipeline carries it, and a drawn wall weight is read by the person holding the sheet as a structural instruction. **56 declared it**: **Solve domain** gains *derived from the [[Envelope]], per candidate, never equal to it* — `t_int` apart on each axis — with an `_Avoid_` on tiling the Envelope's own box and eroding at its boundary, which charges the dwelling for an external wall that is not there and reads as a sizing error in `brief.md`; *"no special case for perimeter rooms"* is a statement about the **rule**, and the arithmetic still has to be handed the right region. **Partition footprint** gains a second `_Avoid_`: it is the last term in the chain and the easiest to blame, and the two quantities in front of it are both larger and neither is a wall. **32 declared it**: **Plan mark**, **Product designation** and **Sheet set mark** are new and they **replace Type mark**, which conflated a position label with a manufacturing designation — and the plan-to-schedule join key is **(kind, number)**, never the number, because doors and windows number in separate spaces. **Living area / Useful area** is new and carries an `_Avoid_` naming the trap that **useful area and `ümumi sahə` are numerically identical in v1 and are not the same quantity**. **Opening** gains the door/window typing asymmetry: a door takes a catalogue entry, a window takes a fixed height and a **selected width**, because only the second is a function of the room's area. **42 declared it**: **Programme rule** and **Combined sanitary unit** are new terms, **Room type** moves to **nineteen** with an `_Avoid_` on growing the set for a *preference* rather than for a rule that cannot otherwise be stated, and **Auxiliary space** gains what enforces it — four rules for five limbs, the `holl` limb held by construction. **16 declared it**: **Nib**, **Receiving Space** and **Placement order** are new terms, **Swing footprint** gains the fact that its side is the **leaf** width and not the structural opening — 100 mm of relief in every wet room that had been silently spent — and two existing terms are marked `_Avoid_`, **Opening**'s cased-opening claim and **Head datum**'s balcony-lintel reason. **48 declared it too**: **Notch** is a new term carrying the material threshold (≥ 5 % of bbox) and the 12.55 % median, and **Envelope** gains *one area, many boxes* with an `_Avoid_` naming ADR 0018 consequence 3 — *"the Envelope, which every candidate for one Brief shares"* — as **false**. 38 declared it: **Pre-image bound** and **Invented circulation** are new terms, **Acceptance bar** reads *one declaration, three consumers*. **23 declared it too**: **Warp** and **Relation provenance** are new, and **Warp budget**'s old reading — *"before its arrangement stops being a real home's"* — is marked **false**, because a monotone warp cannot damage an arrangement at any budget. **44 declared it too**: **Partition footprint** is a new term, and it exists because the quantity has *two* denominators — a share of Σ Space area, never of the interior — and no quote of the 5.7 % anywhere said which. **51 declared it**: **Frontage budget**, **Frontage reach** and **Borrowed daylight** are new. The first two exist because the daylight property a donor hands over is not the one anybody had been quoting, and **Frontage reach** carries an `_Avoid_` on treating it as *sufficient* — it reads boundary contact, and the conversion cannot tell an exterior edge from a party one. **Borrowed daylight** carries the sharper one: *adjacency is not openness*, and **two documents on this map read one for the other** — a separate kitchen with a **door** onto a windowed living room is not a `taxça-mətbəx`, it is the windowless kitchen cl. 9.12 forbids |
| `data/standards/room-constraints.json` | **no claimant — 32 closed and discharged all three of 50's items.** ✅ **The BLOCKING window series is written** as `openings.width_series_mm`, `window_for_room` is a **selection** (`erg_key → (height, width series)`) with every derived sill unmoved, the tier binding was landed **at the authoring site** in `build_ergonomic_layer.py` rather than in the JSON, `min_pier_mm` is **250**, the catalogue's `conf` **splits** (dimensions stay `verified`, the *selection* becomes `engine_choice` off `gost_23166_99` cl. 4.9), and the `drawing` block gains `sheet_marks`, `area_annotation`, an audience-split `room_tag_fallback` and — the part that matters for whoever adds a field next — **`what_belongs_in_this_block`**, the membership test ADR 0024 turns on. ⚠️ **26's `bedroom_double.min_clear_short` 1650 was weighed and REFUSED**, and the reason is on 32: it is a fits floor by construction and raising it rejects 19,3 % of real rooms. The defect is a **missing soft rule** and it is `rules.json`'s. *(historical: 16, 31, 42, 50 and 32 all closed)* ⚠️ **50 hands it three items and one of them BLOCKS a rule already posted hard.** (a) **The window width series**, per room family: `win.area_ratio` is now hard and `window_for_room` must select the smallest member satisfying AzDTN cl. 9.13 rather than picking one of three fixed entries. Against the three entries the rule fails **21,20 %** of real dwellings; against a series, **5,39 %** — three quarters of the cost is a catalogue artefact. Measured reach requirement, ready to transcribe: **p90 2,47 m living, 3,23 m `living_dining`, 1,34 m kitchen**. Cover for publishing one is already in this file — `catalogue_may_be_dead` records that `gost_23166_99` cl. 4.9 makes the opening grid a **project decision**, so a series is `engine_choice` bounded by `gost_11214_86` and is *more* defensible than three entries. (b) **The tier binding must follow `rules.json`'s**: `validator_binding.hard_reject_below` scalar `\"ergonomic\"` → list `[\"ergonomic\", \"statutory_floor\"]`, and `statutory_floor_binding` **`\"warn\"` → `\"hard\"`** — the two files contradicted each other and neither binding had a rule behind it. The conformance test asserting both files carry the same *string* must assert the same **list**. (c) **`window_for_room` becomes `erg_key → (height, width series)`**, with the derived Type mark riding to `annotation.md` — same holder, and the mark reads **height-then-width**. All three are also in `rules.json`'s `owed` block so they cannot be lost. ⚠️ **42 declared it on resolution and moved the type set to nineteen**: `bathroom_combined` with an ergonomic row, an AZ mapping row and a reversed `reachable_in_v1`; `bathroom`'s impossible pan-and-basin note struck; `shower_room`'s programme now states that it composes the pan; three `bridge` notes corrected. ⚠️ **A new room type or profile cell must now also come with a `NEW_ROOM_FIELDS` entry in `build_ergonomic_layer.py`**, which used to delete `counts_as_otaq`, `brief_nameable`, `reachable_in_v1`, `counts_as_otaq_sourcing` and `corpus_medians` on every re-run and now refuses to. ⚠️ **26 hands it one number and could not take it**: `bedroom_double.min_clear_short` 1650 realises to **1850 mm**, which is the width 32 already reproduced from the other end as a tag overflowing in a real solved layout. It is a *fits* floor — bed 1350 + body 300 one side — against AZ's 3000 mm market default and a 10 m² statutory area, and it is why H8's arithmetic now clears. ✅ **38's `reachable_in_v1: false` handoff on `corridor` and `entrance_lobby` is discharged** by 16 rather than passed a third time. 16 also restructured `profiles.AZ.openings.catalogue` — every entry now carries `opening_w/h`, `block_w/h`, `leaf_w/h`, `kind`, `glazed` and `placeable_in_v1` rather than a GOST mark string with the sizes in prose — and added `door_for_room`, `window_for_room`, `dimension_derivation` and `min_pier_mm`. ⚠️ **It moved one flag that is not an opening fact**: `kitchen.needs_window` false → **true**, because three shipped places disagreed about the kitchen window and AzDTN cl. 9.12 is `verified` and mandatory. It added `profiles.AZ.rooms.mapping`, `counts_as_otaq`, `brief_nameable` and `ergonomic.corpus_medians`; a new room type or profile cell must now come with a mapping row or `gate_check.py` fails |
| `data/acceptance/rules.json` | **no claimant — 32, 50, 20, 42 and 26 all closed.** ✅ **32 discharged three `owed` items and added one.** The window series, the tier binding and `window_for_room` are done, each with what it cost written into a new `discharged` block rather than deleted — **50's series shape and its *splitting buys nothing* both had to be corrected**, and that correction is recorded where the next reader of the series will find it. Three stale `tier_binding` notes fixed: the two files carry the same **list**, not the same string. ⚠️ **One new item, and it is the map's cleanest unwired number**: `dim.prefer_wide_habitable`, soft — `clear_widths_mm.habitable_room.market_default` is **3 000** and `soft_objective_target` names `market_default`, but the only rule reading that tier is `dim.market_default_area`, an **area** term, so **there is no soft rule on clear width at all** and a 1 850 × 5 400 bedroom passes every hard rule on the file. ✅ **50 took it 42 → 43 and amended two bindings**: `dim.statutory_min_area` (hard, site `both`, `conf: verified`, `corpus_cost` 0.5451 with its denominator written out so nobody reads it as a rejection rate); `win.area_ratio` soft → **hard**, `validator` → **both**, `binds_room_types` added because cl. 9.13 binds living rooms and kitchens and the shipped statement bound every Space; `tier_binding.hard_reject_below` **scalar → list** `[\"ergonomic\", \"statutory_floor\"]`; `region_binding.hard_set_is_region_free` → **false**, monotone. Conformance subset 15 → **17**. A ticket touching a severity is now amending a decision with a published corpus cost. ⚠️ **The `owed` block gained three BLOCKING items, all `room-constraints.json`'s** — the window width series, the tier binding that must follow this file's, and `window_for_room` becoming a selection rather than a map. **50's `win.area_ratio` severity question is closed and it was the last unfitted severity on the file.** ✅ **20 took it from 40 to 42 rules and `ENGINE_CHOICE` from 18 to 9**, added `conf: fitted` (ADR 0023) with `src`/`corpus_cost`/`fitted_by` on every fitted rule, landed `dim.max_area` (hard, **site `both`**, which moves the conformance subset to 15) and `dim.stated_target_implausible`, made `dim.market_default_area` two-sided, and added four blocks: `area_bands`, `envelope_constants`, `rule_count` and **`owed`**. A ticket touching a threshold is now amending a fitted number with a published corpus cost rather than filling a gap. ⚠️ **50's `win.area_ratio` severity question is untouched and is the last unfitted severity on the file.** ✅ **42 added the first four rules whose subject is the programme rather than an entity**, 36 → **40**: a new `item: programme`, a `scope_meanings` block stating why they have no plan-side twin, and a `programme_rules` block carrying cl. 5.2, the four corpus costs and why `resolve` does not invent the missing room. The `both` conformance subset **stays at 14** and cannot grow here. ⚠️ **The locale schema change now spans 40 rules, not 36.** ✅ **26 retired two rules, 38 → 36**, the first retirement on this map: `win.habitable_touches_exterior` and `win.kitchen_windowless`, neither of which could fire. Both sit in a new `retired` block with their statements, so a ticket that expects 38 is reading a stale count. `win.habitable_has_window` is now site `both` and `win.area_ratio`'s statement gained its exterior-face clause. **50 is new and holds that rule's severity.** ⚠️ **16 amended six rules and added none**, on purpose, because `acceptance-bar.md` is claimed twice and adding one would move the 38 count: `circ.potential_reachability` (+400), `open.fits_segment` (face declared **clear**), `open.leading_edge_nib` (justification re-based off AD M accessibility), `win.habitable_has_window` (party-wall hole closed), `win.kitchen_windowless` (annotated unreachable) and `entry.exists` (`entrance_side` required). **Six rule statements now diverge from the prose that publishes them** — the next holder of `acceptance-bar.md` closes that, and it is a price of this rule rather than an oversight. And whichever of them moves first inherits the **message locale** schema change, which **38 has now merged with a second requirement**: `brief.md` §9.4 returns a *set of findings* rather than a verdict, each with a severity, a Brief field and an Azerbaijani message — one schema change, not two, and now **two rules 31 handed over** (cl. 5.2's mandatory room composition, and `kitchen_dining`'s zone-not-room target) and **five 30 handed over**, written out in full at `docs/research/zoning.md` §5b ⚠️ **`dim.statutory_min_area`'s severity is now a live question with a measured price** — [The warp has never been measured against a stated target area](tickets/54-the-warp-has-never-been-measured-against-a-stated-area.md). 50 posted it hard on the argument that a Plan reaching its soft target clears the floor by construction, and named its own reversal trigger: *a hard rule that is too strict is discovered at build time on the first Proposer run.* **That trigger has fired early.** ~~On Briefs whose every target sits on `market_default`, the rule alone costs **31,1 % of candidates** and **6,7 % of Briefs at pool-of-8**~~ — **both superseded, and the rule is about half as expensive as it was posted at**: [The sizing rung under-delivers by four per cent](tickets/56-the-sizing-rung-under-delivers-on-the-warp-path.md) found the *measurement* was carrying the difference, not the rule. Same sample, same seed, both Envelope defects fixed: **25,5 % of candidates** and **3,6 % of Briefs at pool-of-8**, with the passing kitchen's lower quartile clearing by **518 litres** rather than 85 — so *"passing by luck"* no longer describes it, though **17,4 %** of kitchens asked for 9,0 m² are still delivered under 8,0 and no sizing constant reaches that. The severity is [The statutory floor now has a price](tickets/55-does-the-statutory-floor-stay-hard-now-that-it-has-a-price.md), **now unblocked**, and its own ticket carries the corrected table. ⚠️ **Do not read it against the bar's 15,59 %** — one is a predicate's cost on generated candidates, the other the whole hard registry's survival rate on real dwellings. ⚠️ **And do not reach for the 18,8 %** — that was `calib`, which scales the box until Σ Space hits `target_area` and hands the rooms margin the Brief does not entitle them to; a correct Envelope over-delivers by **0,4 %**, not by `calib`'s 2,2 % of slack. |
| `data/standards/room-constraints.json` (second entry) | **30 hands it one flag**, `is_sleeping` — and it **may not be folded into `is_private`**, which is true on the wet types too |
| `docs/spec/acceptance-bar.md` | **no claimant — 50, 42 and 26 all closed.** ✅ **50 added §3.1**, retitled §3 and struck its reason 3, rewrote §7.4 whole and moved §7's heading to *two hard rules*; a ticket touching the region/hard-floor relationship, the glazing severity or the window selection is amending a settled shape rather than filling a gap. ✅ **The stale counts this file carried are fixed at all four sites** — 40 → **43**, conformance subset 14 → **17**, hard 31 → **34**, locale 40 → **43** — so the *stale in four places* warning 20 left here is discharged. 42 added **§13**, six subsections, and moved the count at four sites; a ticket touching composition, the WC satisfying set or cl. 5.10's non-enforcement is amending a settled shape rather than filling a gap. It rewrote §7 whole and amended §3, so a ticket touching windows is amending a settled shape rather than filling a gap; §7.3 also answers §9.1's which-part question for the window rule. **The rule count moved to 36 in three places in this file and once in `brief.md`** |
| `docs/spec/proposer.md` | **53 — sole claimant now; 51, 23, 47 and 56 closed.** ⚠️ **56 hands §2.2.3 a sentence that has to change and a measured price for leaving it**: *"the notch is the part of the bbox no part covers — so it **warps along with everything else, for free**"* is what makes ADR 0020's *"every candidate delivers `interior` of floor by construction"* **false**, because the guarantee holds only while the *realised* notch share equals the recorded `s` the box was derived from. The notch is the one region of the frame carrying no target, so it is a free sink: measured, `covered ÷ interior` is **0.9833** free and **0.9986** held — **1,5 % of `interior`**, and **5,6 points** of plan-level `dim.statutory_min_area` (30,5 % → 24,9 %). The constraint is one bilinear equality on the gap variables the room areas already use (realised uncovered area = `s × W × H`), or the fixed point on the box `ring` uses. ⚠️ **This is NOT ADR 0003 consequence 7**, which fixes the *entrance edge* by side and says nothing about the notch's dimensions — the two are compatible and neither implies the other, which is why nothing had caught it. ⚠️ **Nobody has priced the constrained model**: the `ring` arms reach the invariant by re-sizing the box, not by constraining the solve, so its INFEASIBLE cost is unmeasured. ✅ **51 added §4.5 and amended §2.2.1, §2.2.4, §6.1, §7 and §8** — a ticket touching what the corpus is admitted on, the index record, the pre-rank order or the plan-quality terms is now amending a settled shape rather than filling a gap. It **discharged the half of `acceptance-thresholds.md` §13's handoff addressed to it**; **the half addressed to 53 is untouched and still open**. ⚠️ **53 inherits one caution from it**: §4.5's residue is quoted as a **floor** and not a size, because `frontage_reach` reads boundary contact and §2.2.6 says the conversion cannot tell `exterior` from `party` — the same necessary-not-sufficient trap a void gate would sit in. ⚠️ **47 hands §2.2 the whole of its own open question and could not write it**: donor fidelity is in **neither** the index record (eleven fields, none of them fidelity) nor the ranking (§2.2.4 pre-ranks on the *warp's* deviation, a fact about the fit to this Brief and not about whether the donor converted faithfully). Owed in three parts, specified ready to transcribe on ticket 47 — add **worst-room IoU** to the index record (`fit_rects.py` already emits per-room `iou`, no re-fit), **gate hard below 0.30** at a published cost of **6.65 %** of the index and `conf: fitted` rather than `verified`, and **rank on it above the gate** rather than gating at 0.50, which would cost 17.2 % of an index C13 already calls thin. **53 is new**, raised by 42 after it checked and refuted the premise it was handed — `model.no_unassigned_area` is hard, so the enclosed void is a *donor* problem, not the bar's. ~~51 is new and holds the corpus cost of a shipped hard rule — 43.3 % of real dwellings rejected by `win.habitable_has_window`, 23.0 points the kitchen alone.~~ **Closed, and the corpus cost was never this file's to hold**: it is **38.55 %** at index scale, of which **86.04 %** is reglazed by the opening layer, leaving **6.39 %**. It rewrote §2.2 into seven subsections and corrected §1, §4.4 and §5.1, so a ticket touching those is amending a settled shape rather than filling a gap. **48 hands it three things**: §2.2.3's stated-`shape` gate moves from notch **count** to notch **area share** (a material notch is ≥ 5 % of bbox — the count gate reports 90 % of real flats as U/T and 8.7 % as L, where the material reading gives **52.96 % L**); §2.2.1's index record must carry the notch share `s`, and the per-candidate `W × H = interior / (1 − s)` needs a home; and **"fill the notch"** is recorded as a live candidate design that would dissolve the stated-shape coverage cliff at the cost of re-proving ADR 0018's monotone-warp theorem |
| `docs/spec/annotation.md` | **no claimant — 32 and 36 closed.** ⚠️ **36 hands it three items and could not take them, and two of them are corrections to shipped text rather than additions.** (a) **A new general note**, drafted on ADR 0026: *all internal walls are shown as partitions at one thickness; load-bearing walls have not been identified.* **`arakəsmə` is `verified`** — AzDTN's own word at `az-finish-layer.md` cl. 8.24, already used in §8 — but **`yükdaşıyan` is unsourced and must not ship as written**; source it from `azdtn_2_17_1`, which `thickness.md` read first-hand for `t_int_bearing` cl. 6.9. (b) **Strike *"unless noted"* from general note 3** — *"All partitions `t_int` mm unless noted"* promises an exception mechanism the engine does not have, and **nothing is ever noted**. (c) **Add `draw.structural_disclaimer_present`, Drawing check 12 → 13**, on `draw.schedule_totals_close`'s precedent. ⚠️ **Note 7 is the trap**: *"structural performance is not specified"* is a statement about a **calculation**, and the missing claim is **identification** — a reader takes note 7 as *no structural calculations were run* and still assumes the wall drawn heavy is the heavy one. ✅ **31 and 16 both handed it something and both are discharged**: the eighteen Azerbaijani room names are consumed through `profiles.AZ.rooms.mapping.rooms.<key>.name_az` rather than transcribed — §14 uses them and §7 says where they come from — and the door schedule now carries the two-level mark scheme with `Handing` and `Swing` filled from §4.1/§4.2. Twelve sections moved and §14 was **re-derived at `t_int` 150**; a ticket touching the sheet mark, the mark scheme, tier 1, the tag ladder, the schedule totals or the setting-out datum is amending a settled shape rather than filling a gap. ⚠️ **The Drawing check is twelve predicates, not eleven** — `draw.schedule_totals_close`, because a totals row computed from exact areas disagrees with the column printed above it. ⚠️ **`draw.schedule_complete` now joins on `(kind, mark)`**: doors and windows number in separate spaces and a join on the number alone matches door 1 to window 1. ✅ **31 has handed it the eighteen Azerbaijani room names**, sourced and cited. ✅ **16 has filled the door schedule's `Handing` and `Swing` columns** with a stated rule rather than a promise — handing is *derived* from the door's position, so the schedule cell and the plan's swing arc cannot disagree — and hands it one new graphic: `door_living_glazed` is a **glazed** leaf and draws a glazing line where a solid one does not |
| `docs/adr/0020-…` | **no claimant — 56 declared it on resolution.** ✅ Amendment: **`interior` is the Envelope's own area** at the finished inner face and the solve domain is a **third** quantity derived from the box — the ADR wrote `box = interior/(1 − s)` and never said which plane, and a shipped rig read it the other way. ⚠️ **And the ADR's own guarantee has a precondition it does not state**: *"every candidate delivers `interior` of floor by construction"* holds only while the *realised* notch share equals the recorded `s`, which `proposer.md` §2.2.3 explicitly denies. Worth **1,5 % of `interior`**. `rules.json` sees no change, which is the second time this ADR has ended there |
| `docs/adr/0012-…` | **no claimant.** ⚠️ **16 hands it one correction and could not make it**: `head_datum_mm` 2200 is justified as *"the balcony door's own catalogue head, because a balcony door and the window beside it share a lintel"*, and **v1 models no balcony**, so the entry the datum was read off can never be placed. The **number is right and the reason is dead** — an AZ window head sits above the door head, which is what keeps doors reading at their own 2100. Sills are unaffected and re-anchoring to 2100 is refused |
| `docs/spec/openings.md` | **no claimant — 16 created it, 32 amended it.** ⚠️ **§6.1 was rewritten by a ticket that does not hold it, and the alternative was shipping two contradictory window rules.** Its fixed-size / variable-count design contradicts a sized window, and **its own worked example fails the shipped bar** — `living` at 0,250, `kitchen` at 0,120 below the now-hard floor, and `bedroom_single`'s window omitted altogether. One window per Space, width from the series, target-first then floor then a hard failure reported as one. §11's window table and four §10 handoff rows updated with it. *(also: 16 closed and created it)* Eleven sections; a ticket touching position, hinge, swing, leaf-or-cased or window count is amending a settled shape rather than filling a gap. **It also declared `docs/adr/0021-…` and `CONTEXT.md` on resolution**: **Nib**, **Receiving Space** and **Placement order** are new terms, and two existing terms are marked `_Avoid_` — **Opening**'s *"a cased opening is how most homes join a kitchen to a living room"* is a Western prior the `AZ` catalogue refutes, and **Head datum**'s *"because a balcony door and the window beside it share a lintel"* is dead in a v1 that models no balcony |
| `docs/spec/brief.md` | **no claimant — 42, 48, 50 and 56 closed.** ⚠️ **50 hands it one bound and could not take it**: §9.4 bounds 1 and 3 must read `max(ergonomic minimum, region statutory floor)` rather than the ergonomic minimum alone, per ADR 0015. Σ hard minima for a one-otaq dwelling goes **9,0 m² → 26,5**, two-otaq 37,5, three 47,5, four 57,5 before the partition footprint — ordinary Baku flat sizes, and **nothing leaves C13's 3–10 band**. The 9,0 m² one-otaq flat the old floor admitted **is** the defect, restated at parse time. The message stays arithmetic — *your Envelope cannot hold n otaq* — never a compliance claim, which is how the rule stays inside C8. ⚠️ **42 declared it and wrote §9.4 bound 8, §3's nineteenth type and §9.1's fourth hard error rather than handing them on** — the same reason 44 refused a second handoff. It discharged §12's composition row and left three: which sentence leads when bound 8 contradicts bounds 1/3/6, a `taxça-mətbəx` type, and a Brief-nameable built-in wardrobe. 38 and 44 closed before it. 38 rewrote §9.4 and added §3.1, so a ticket touching either is amending a settled shape rather than filling a gap. **44 wrote §9.4 bound 6's `f_hi`/`f_lo` table, §5 rung 1's `f`, §12 and §13 into it** rather than handing them on, and it raises one new obligation: the eight-row table is inline prose and belongs in data beside `room-area-bands.md` §6.1's `k`, for `rules.json`'s holder. **31's two are still open**: whether a nineteenth type (`taxça-mətbəx`) is owed, and where the `(type, otaq_count) → target, width, name` resolution step lives. ~~**23's two became 48**~~ — **both discharged.** `shape` now leaves the `ResolvedBrief` entirely rather than getting a default, and the per-candidate Envelope is resolved by making **floor area the pool invariant and the box derived** (ADR 0020). 48 also rewrote §5 into §5/§5.1/§5.2, annotated §6, took §9.4 to **seven** bounds and added five §12 handoffs and two §13 limits, so a ticket touching any of those is amending a settled shape rather than filling a gap ✅ **§5 rung 1 does not under-deliver, and `f` is vindicated** — [The sizing rung under-delivers by four per cent, and `f` is not where to fix it](tickets/56-the-sizing-rung-under-delivers-on-the-warp-path.md). The ~4,2 % was **two defects in how the rig measured the Envelope** and neither was in this file: it eroded a 75 mm ring ADR 0001 does not lose (**3,7 % of `interior` at p50**), and it let the warp resize the notch, which ADR 0020's by-construction guarantee assumes it cannot (**1,5 %**). Corrected, Σ Space lands **+0,4 %** of `target_area` and `f = 0.0575` is untouched — the widening the ticket was raised to make would have oversized every Envelope on **both** proposer paths to compensate for an erosion the engine does not perform. ✅ **The `interior` reading is settled and was never a coin-flip**: the Envelope's own area at the finished inner face, because `CONTEXT.md` defines the solve domain as *"not the Envelope, and not the interior"* and `s` is a share of the **Envelope's** bbox. The domain is a **third** quantity, derived from the box, and new **§5.3** carries the three-plane table and the statement that it is source-independent. ⚠️ **What moved instead is `proposer.md` §2.2.3's, and 53 holds it**: *"the notch warps along with everything else, for free"* is what makes ADR 0020's guarantee false, worth **5,6 points** of plan-level `dim.statutory_min_area`. ⚠️ Rung 1's `f` had also been published with **no denominator** — *"the p50 of Σ Space area"*, which is not a quantity — now fixed at source. |
| `docs/spec/homeowner-surface.md` | **45 — sole claimant.** ⚠️ **32 leaves it two items and could not take them**: §187 offers *the full two-sheet set (`A-101` plan, `A-102` schedules)* and those sheet numbers no longer exist — the set is `<job>-MH`, *Vərəq 1 / 2* (ADR 0024), and `annotation.md` §1 carries the translation so nothing is ambiguous meanwhile. And §2's *numbers use the decimal comma everywhere* now has a **shared implementation** rather than a parallel one: `annotation.md` §1.1 puts every rendered number through one formatter, and the preview is one of its three named call sites. Created by 13, which declared it on resolution rather than taking it quietly; 45 is the first ticket to claim it, and it inherits the **message locale** schema change if it moves before `rules.json`'s holder |
| `experiments/warp/` | **no claimant — 54 and 56 both closed.** ✅ **56 found the rig had been measuring the wrong region and published the correction**: `absolute_area.py` tiled the *Envelope box* and eroded every Room on all four sides, where ADR 0001 tiles the Envelope **dilated by `t_int/2`** and a boundary edge costs no floor — a 75 mm ring, **3,7 % of `interior` at p50**, larger than the level error it was raised to explain. `part_targets_cells` carried the same defect one level up and was **compensating** for it, which is why the fix moves the level a long way and the yield hardly at all. New `outside_of`, `space_m2` and `part_targets_cells` re-based on ADR 0001's plane, and **`ring` / `ringmarket` / `ringpool`**, the arms that hold the notch share the box was derived from. ⚠️ **Read the `ring` row and no other as what the engine delivers** — `calib` scales until Σ Space hits `target_area` and buys the rooms margin the Brief does not entitle them to, and reading it as *what a correct Envelope gives* is what put 2/5 of a hard rule's cost on one constant in `brief.md`. ⚠️ **The pre-56 rows are committed** at `series/absolute_area_pre56_rows.json.gz` (263 KB, five arms), on 44's rule — `out/` is gitignored, so a snapshot in it would have been a local-only claim — and the paired before/after is re-derivable in seconds — and `cross before` reproduces 54's published 30,7 % and `calib before` its 18,8 % exactly, which is how the rig is known to be the same rig. *(historical: 54 closed and discharged both obligations.)* ✅ **The measurement exists and it refutes the argument it was asked about**: `absolute_area.py`, four per-candidate arms plus best-of-pool, un-normalised targets, measured on the **Space** (`erode(⋃ parts, 75)`) rather than the centreline part. **31,1 % of candidates and 6,7 % of Briefs at pool-of-8** lose a Room below `dim.statutory_min_area` even when every target sits on `market_default` — [The warp has never been measured against a stated target area](tickets/54-the-warp-has-never-been-measured-against-a-stated-area.md). ✅ **48's obligation is discharged**: ADR 0018's p50 0.056 is confirmed as a proportion result and the absolute twin is now published. ⚠️ **Three traps recorded in the README**: never quote a `fit_warp` deviation as an area, never compound a per-candidate share into a Brief-level one (780× wrong), and never quote past one decimal — CP-SAT under a wall-clock cap gave 5,96 % and 5,78 % on two identical runs. ⚠️ **It leaves two numbers with unheld files**: `rules.json` owns the severity, and `brief.md` §5 rung 1's `f` is short by ~4,2 % on this path — do **not** fix that inside `f`, which is a correctly measured partition footprint of a different quantity |
| `experiments/envelope-exposure/` | **new, no claimant.** Also 13's, and deliberately *not* `experiments/solver-toy/`, which 29 claimed: the two probes import that directory and never edit it. Their findings are quoted on the Envelope row and on 26 |
| `experiments/region-profile/gate_check.py`, `ergonomic_check.py` | **no claimant.** ✅ **The deliberate failure is discharged and both checks are green** — `ergonomic_check.py` reports **233 pass, 0 fail**. 50 declared both on resolution and left one FAILING ON PURPOSE (229 pass, 1 fail -- *both files name the same hard tier -- ['ergonomic', 'statutory_floor'] vs 'ergonomic'*) because `room-constraints.json` was 32's and its half was handed over rather than written; **32 wrote it, at the authoring site**, and both files now carry the list with `statutory_floor_binding: hard`. Verified rather than assumed, by 36 while checking the map's assertion layer after its own resolution. ⚠️ **Do not relax the comparison** if it ever fires again — it was catching a real drift, and its message names the ticket, the two lines and the authoring site. ⚠️ **`build_ergonomic_layer.py` re-authors that field every run**, so a JSON edit alone still reverts -- the same trap that reverted `kitchen.needs_window`. ✅ `gate_check.py` **passes at 238** after a two-line fix: it read `hard_reject_below` as a scalar and crashed on the list, and now iterates the tiers, so a profile that ever publishes a statutory *clear width* is gated on ADR 0007 rather than skipped -- `AZ` publishes none, so no gate changed value. 31 declared `gate_check.py` on resolution rather than taking it quietly — 162 vocabulary gates, the file now runs 229 |
| `docs/spec/ifc-export.md` | **no claimant — 41 closed.** It also declared `docs/adr/0012-…` and `docs/adr/0014-…` on resolution rather than taking them quietly: 0012's `§5` → `§6` slip and both its consequences marked landed, 0014's RV question marked cleared and its rectangle comparison recorded as false |
| `experiments/thickness-fidelity/`, `docs/research/single-internal-thickness.md` | **no claimant — 44 and 36 closed.** ⚠️ **36 leaves one correction it deliberately did not write** — the file was unclaimed but the ADR is the load-bearing record and a second edit would have restated it: **§4.4 prices shape B in solve cells and in area drift and never in hard-rule breakage**, which is the price that decides it. *"ADR 0001's uniformity survives where it is load-bearing (the solve)"* is true and misleading — no hard rule binds the solve alone, and the cheap version of C leaves **up to 4,9 points of Σ Space** unassigned against a hard `model.no_unassigned_area`. ⚠️ Its §2.1 headline is also **measured on surveyed built dwellings**, so the 76,1 % answers a question about working drawings, not about concept plans — ADR 0026. Created by 38 rather than left as a handoff to *whoever next runs* the harness, which named no one. 44 also declared `docs/spec/brief.md` and `CONTEXT.md` on resolution: neither had a claimant, and handing two numbers to an unheld file is the defect that created 44. One number here is load-bearing twice: a hard refusal in `brief.md` §9.4 bound 6, and the Envelope §5 rung 1 derives from a stated `target_area`. It leaves behind a **committed 479 KB series**, `series/footprint_150.csv.gz`, so the next percentile off this study costs seconds instead of a 46-minute re-measure against a 1.09 GB corpus — with the rule in the README: *if you add a statistic to this study, add its inputs to the series* |
| `experiments/solver-toy/` | **43 — sole claimant now, 29 is closed.** The re-base it was waiting for happened and **moved nothing**, so the rig 43 prices its encoding against is the published one. 29 added `pinwheel.py`, `sweep_ng.py`, `report_ng.py`, `relation_margins.py`, `t_int_arithmetic.py`, `pinwheel_area_premium.py`, `corpus_guillotine.py` and left `_guillotine` the **default** on purpose. ⚠️ It also leaves a fixture defect for whoever runs the harness next: `AREA_PER_ROOM_M2` = 9.65 is below what the placeholder table needs at 7 and 8 rooms in **either** arm |
| `docs/adr/0003-…` | **no claimant — 47 closed.** ✅ **48's §7 correction is written**, after two holders declined to write blind: consequence 7 now reads *one ring per candidate, fixed before that candidate's solve*, and states the reason it is safe — the entrance edge is identified **by side, never by ring index**. ✅ **A second amendment closes the notch cap**: the cap is evidenced, the shape family is refused at a measured ceiling of 4.17 % of the corpus, and the cap bullet points at it. A ticket touching the cap, the shape family or the entrance edge is amending a settled shape rather than filling a gap |
| `experiments/rectangularise/`, `docs/research/rectangularisation.md` | **46 — sole claimant now, 47, 27 and 40 all closed.** ✅ **47 added `envelope_family.py` and `rectangularisation.md` §13** and declared the research doc on resolution — 46 was unclaimed, so the rule held, and §13 is self-contained at the foot. ⚠️ **§13 hands 46 a population five times its own**: 46 scopes §12.3's 1.5 % (a room off frame by 10–20°); §13.2 measures **8.76 % of dwellings** with an outline more than 10 % off-axis *in their own frame*, holding **49.5 %** of the envelope-loss tail. Read it before deciding. ⚠️ `envelope_family.py` reads the cached fit and the `swiss_dw.pkl` cache and costs seconds — **add a statistic about the Envelope's shape family or about donor fidelity there rather than re-deriving it from the corpus**. ⚠️ **`fit_rects.py` is now owed THREE per-record fields the index needs and the fit does not emit.** 23 hands it the **cut-line frame** (sorted distinct coordinates plus each part's index span) and **per-pair relation provenance**, which today is only the `rel: {same, spurious}` counts; **51 adds `frontage_reach`** — one intersection per `needs_window` Room against the assembled envelope, both inputs already in hand, with `experiments/corpus-smoke/boundary_contact.py` as the reference implementation. Take them together: it is one pass over the same records. 27 added `render_sheet.py` and `void_census.py` and declared them on resolution; both new tickets read them rather than re-deriving. ✅ `rectangularisation.md` **§12 is the correction**, declared on 27's resolution rather than taken quietly: the three restated headlines, the worst-room-IoU pairing, and two fixes to §11.4 — its spurious rate is the **paired** one (0.1358) and the corpus-wide figure ticket 23 wants is **0.1262**, and its account of what a spurious relation *is* is wrong |
| `experiments/acceptance-thresholds/`, `docs/research/acceptance-thresholds.md` | **no claimant — 20 closed and created them.** Five scripts over 42,985 raw Swiss dwellings and 16,612 ResPlan plans; `census.py` is the only expensive step (~13 min) and everything else reads its record, so a new statistic off this study costs seconds — with the rule in the README: *if you add a statistic, add its inputs to `census.py`'s record.* ⚠️ **Two traps it documents**: do **not** erode the raw arm (Swiss polygons are already clear), and condition the converted arm on `dim.min_clear_short` before quoting aspect, or a 100 mm-wide part gives you a `max` of 56.00 |
| `data/standards/room-constraints.json` (third entry) | ⚠️ **20 declared it on resolution for a one-field regression repair**, and the repair is at the *authoring* site: `ergonomic.rooms.kitchen.needs_window` was set `true` by 16 and **silently reverted to `false`** by 42's re-run of `build_ergonomic_layer.py`, because `needs_window` is in `AUTHORED_ROOM` and 42's carry-forward fix cannot carry a field the generator itself authors. It falsified `win.habitable_has_window`'s 43.3 %, the retirement of `win.kitchen_windowless`, and the Envelope row's *one more room competing for frontage*. Regenerating changes exactly one field; 238/238 gates pass. **20 also hands this file `min_pier_mm` 600 → 250 and did not write it** — 32 holds it |
| `docs/spec/brief.md` (second entry) | ⚠️ **20 declared it too** — §5 rung 2 gains the two fitted Envelope constants (`efficiency` **0.84**, default aspect **1.38**, both corpus p50s, both shipped guesses inside 2 %) and the warning that a single `efficiency` is a point prediction with a ±10 % tail; two §12 rows struck as discharged. ✅ **Rung 1 is confirmed, not changed**: the partition footprint re-measured geometrically is 4.17 % against `f`'s 5.75 %, and the two agree once the plane is named — the corpus's own p50 wall gap is **99 mm**, not the shipped 150 |
| `experiments/h8-frontage/` | **no claimant — 26 closed and created it.** Three probes: the frontage budget against the *shipped* standards rather than `solver-toy`'s placeholders, and the first per-room evaluation of the window rules against real dwellings. It imports `solver-toy` and never edits it, the same arrangement `envelope-exposure` uses |
| `experiments/solver-toy/geometry.py` (`EXPOSURE_PRESETS`), `experiments/envelope-exposure/` | **no claimant — 49 closed.** It re-fitted the presets on **exterior run per room** rather than on a fraction of perimeter, because a fraction does not transfer between dwellings whose perimeters differ and **H8 reads run**. `envelope-exposure/` now holds four probes and a committed 371 KB series (2,238 dwellings), so a later percentile costs seconds. ⚠️ **It also declared `docs/adr/0003-…`**, which the row below lists as **47's** — a collision this table did not record. 47 was unclaimed at the time; the amendment is a self-contained section at the foot of the file and touches nothing in the notch-cap material 47 will write. 48's outstanding §7 correction was **deliberately left for 47** rather than written blind |
| `experiments/corpus-smoke/`, `docs/adr/0025-…` | **no claimant — 51 closed and created three probes plus the directory's first README.** `window_rule_overlap.py` (the paired 2×2 against ADR 0016), `boundary_contact.py` (the property the warp inherits, **no corpus stream** — it reads `rectangularise/out/swiss_dw.pkl` as a copied-in input) and `kitchen_niche_test.py`. It imports nothing and writes to no other directory. ⚠️ **Three traps in the README**: the method is `h8-frontage/window_rules_corpus.py`'s **verbatim** and changing any of its three constants breaks comparability with the figure it supersedes; **`win.habitable_has_window` has three corpus costs answering three questions** and none may overwrite another; and **stdout here is cp1252** — the schwa in `taxça-mətbəx` killed a nine-minute run *after* it had printed every number and *before* it wrote its JSON |
| `experiments/solver-toy/`, `docs/research/solver-formulation.md`, `experiments/room-rectangles/`, `docs/research/room-rectangles.md` | **52 — new, no claimant.** ⚠️ **51 hands it a named, unproven lead for the six-room mystery**: `probe_exposure` returns 0/5 at six rooms with 5 250 mm of frontage slack and nothing has identified why — and `kitchen.needs_window` went **`true` after** those presets were fitted, so the kitchen is a frontage claimant the arithmetic there may not carry. Not a claim; the one unexamined candidate. ⚠️ **51 also leaves both holders of this directory a question its own decision turns on**: what `select_relations`' positive-cost filter actually posts. A landlocked donor is only *provably* infeasible if the separations enclosing that Room survive selection — measure it and ADR 0025's refused gate becomes arguable. ⚠️ It shares **both** `solver-toy/` and `solver-formulation.md` with **43**, so the concurrency rule binds hard: not at once. Created by 49, which measured three structural defects it could not fix because the fixes change what the solver is *given*, not what it is measured against |

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
| C14 | **A region profile is a construction system plus a drawing convention, and it may RAISE a hard floor and never lower one.** ~~*never rejects a Plan*~~ — **amended, monotonically**, by [A statutory floor, posted soft, in the one region v1 ships](tickets/50-a-statutory-floor-posted-soft.md). The **base** of the hard set still carries no region: every predicate and its region-free floor is the same everywhere, and no profile may add a predicate, remove one or weaken one. What a profile may now do is raise a floor on a predicate that already binds — `dim.statutory_min_area`, hard, `verified`, AzDTN cl. 5.7 — and `win.area_ratio` is hard for the same reason. `acceptance-bar.md` §3's reasons 1 and 2 survive untouched; **reason 3 (*lets v1 ship without settling the region list*) is spent**, because C12 settled it at exactly one profile, and it was the only one of the three arguing the hard set must carry *no* region rather than a *defensible* one. The guarantee it protected survives because raising is monotone. `UK` raises nothing and stays the free test fixture. **The profile no longer owns *two soft area targets and one soft window fraction*** — that phrase is dead. It owns the thickness catalogue, decimal separator, room-name abbreviations, opening catalogue keys, two soft area targets, one **hard** window fraction and the **statutory area floors its law publishes** — ten of nineteen room types are silent in `AZ`, and silence is not an error. Every hard dimensional floor is now `max(ergonomic minimum, region statutory floor)`. **`RegionProfile` and `CorpusProvenance` are two fields**, `AZ` and `CH`, and their disagreement is the normal case — v1 draws **Swiss-shaped layouts to Azerbaijani conventions, permanently**, and says so. Now populated: **one construction type, brick, `t_int` 150 mm — a layer set, 120 structural + 2 × 15 finish, every term `verified`**, drawing in Azerbaijani. It also owns the **area convention**, and every published number measures to that finish plane. ADR 0006, ADR 0010. |
| C15 | **Two arithmetic ship gates, and they bind different layers.** ADR 0004 — every wall thickness **even** — is global. ADR 0007 — `min + t_int ≡ 0 (mod grid)` — binds **region profiles only**; ADR 0009 exempts the region-invariant ergonomic layer, whose minima are *derived* rather than quoted and so have no nominal-to-clear conversion to apply. Asserted, not claimed: `experiments/region-profile/gate_check.py` — **67 gates, all pass** (33 before ADR 0012 added the vertical section); `gate_check.py` as a whole is **238** after ADR 0022 added the nineteenth Room type after ADR 0010 moved the residue class from 130 to 100 mod 250 and sharpened ADR 0004 to bind on **totals, not layer components**. |

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
  hard** was added because a 2750 × 8250 bedroom passes every other test. ~~⚠️ 19 rules
  remain `ENGINE_CHOICE`~~ — **paid, and the count was never 19**: two were retired by *H8 and
  the single-aspect flat*, so it was **18**, and *Fit the ENGINE_CHOICE acceptance thresholds to
  the corpora* took it to **9** — fitting nine to the corpora and adding a `fitted` provenance
  level so a measured number stops being marked like a guess (ADR 0023). ✅ **This ticket's
  aspect-ratio guess is the most precisely vindicated number on the map**: 3.0 is the p99.5 of
  real room aspect, at **3.02**. ⚠️ **Its first loosening — wet clustering from one group to two — was the right
  rule and not far enough**: at 2 it still rejects **14.34 %** of real homes, and it is now 3.
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
  <!-- ⚠️ TWELVE since ADR 0024: `draw.schedule_totals_close` -->
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
  one class, so every coverage figure measured before that was pessimistic. ✅ Its
  coverage table — 9.5% / 12.4% / 67.7% blank — was measured on the **unconverted**
  corpus and is now **restated** by *The retrieval index and warp procedure*: joined
  per multiset over the full index, conversion costs **0.2 and 0.4 points** of blank
  rate, so the table was very nearly right and the fear that the pool would thin
  hardest where it was thinnest was wrong.
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
  with the opposite sign. ✅ It exposes a **live defect at k = 1**:
  `select_relations` never filters on a positive separation cost, so an
  overlapping Proposal already gets separations asserted it never made — **the rule
  is now decided** (assert only at best cost ≤ 0, `proposer.md` §5.1) and only the
  code change is outstanding, on `solver-toy`'s holder. ⚠️ Item 6, the 31 % conversion
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

- [Look at the converted corpus](tickets/27-look-at-the-converted-corpus.md)
  — **it reads as a home, and three of the numbers that said so were the constraints
  restated.** ADR 0017, 67 dwellings drawn beside their originals **as plans, with
  walls** — an outline drawing of the same rectangles flatters the conversion.
  `edges_lost = 0`, zero flipped directions and the ±10 % area band are all posted
  **hard**, so a violating dwelling is *refused*, not converted: **"zero adjacencies
  destroyed" and "9.5 % refused" are one fact stated twice.** Cell agreement survives
  as headline — it ranks dwellings the way looking does, ρ **0.825**, and of the
  69.6 % scoring ≥ 0.90 only **0.8 %** hide a room at IoU ≤ 0.30 — but it **never
  travels without worst-room IoU**, which at fixed agreement runs p10 0.45 to p90
  0.82. ✅ The added relations are right and the question was **inverted**: a
  `spurious` relation is a pair whose boxes *overlapped* and no longer do, not a wrap
  the fit picked a side on. **Two k ≤ 2 rates are both right**: 13.58 % paired
  (what §11.4 publishes) and **12.62 %** over all 2,317 conversions — the second is
  what the Proposer's corpus contains and the one to quote downstream. ✅ ADR 0014's tag in the fat leg **reads deliberate**, discharging
  ticket 28's owed drawing. ⚠️ Four failure modes named: **off-frame wings** (1.5 % of
  dwellings sheared into a *different* flat at worst-room IoU 0.167, and OPTIMAL while
  doing it) and **the Envelope shape family** became tickets; **enclosed voids**
  (10.0 % of dwellings carry a ≥ 0.5 m² unnamed hole) went to the acceptance bar and
  **lost façade** (4.1 % of façade rooms) to H8. ⚠️ Refusals render as **ordinary
  flats** — hard adjacency is what refuses them, not strangeness. ⚠️ **Still no
  renderer on this map**; this is the second ticket to build one to see anything.

- [The retrieval index and warp procedure](tickets/23-retrieval-index-and-warp-procedure.md) —
  **the warp is a solve, and it fits the Brief.** `docs/spec/proposer.md` §2.2 (seven
  subsections), ADR [0018](../adr/0018-the-warp-is-a-solve-and-it-fits-the-brief.md),
  `experiments/warp/`. ✅ **A warp cannot destroy an arrangement** — a monotone map on a
  tiling's cut lines preserves every separation direction, so severity is identically 0
  by construction; **21,074 asserted relations over 993 warps, zero confident-wrong**.
  So the gate's units were wrong in a third way nobody had guessed: not corner noise,
  not severity, but **per-room area**, which it never measured because it bounds the
  total. ⚠️ Inside the shipped gate an affine warp misses per-room targets by a median
  **21 %**, breaches the hard `dim.max_area` on 8.7 %/11.0 % of candidates and leaves a
  room under 0.70 × target on 54.9 %/65.9 %. **Gating it away costs 49 points of
  coverage; ranking it away does nothing** (the pool's best member still misses by >30 %
  for 54.8 %/65.3 % of Briefs). Fitting costs **nothing**: best-of-8 worst-room
  deviation p50 **0.056** against the affine best-of-pool's 0.325, at ~72 ms/candidate,
  INFEASIBLE never UNKNOWN. ✅ **The conversion's price is a pool-size effect, not a
  coverage effect** — joined per multiset over the full index, ADR 0016 costs **0.2 and
  0.4 points** of blank rate, retiring `proposer.md` §4.4's warning. ⚠️ **17.8 % of
  candidates are declined** and the ablation says every refusal is real (minima + aspect
  22.0 %, neither **0.0 %**); declines are **Envelope-correlated, so never compound
  them** — 6.9 % of Briefs lost, not 10⁻⁶. ⚠️ **`shape` absent must not default to
  rectangular**: only 1.12 % of converted dwellings emit a notch-free tiling.

- [The solver has only ever seen guillotine layouts](tickets/29-the-solver-has-only-ever-seen-guillotine-layouts.md)
  — **the solver does not care, and an untested strength is now a measured one.**
  ADR 0019, `docs/research/solver-formulation.md` Part III,
  `experiments/solver-toy/` (483 solves over 568 slots, same machine as Parts I and II). Paired on
  Envelope, room count, exposure, seed, noise and config with **only the cut
  structure moving**: 37 both, 10 neither, **4 discordant each way, exact McNemar
  p = 1.00**, and **zero** discordant at 8–16 rooms. **15 s, τ = 4 and ADR 0007 all
  stand unchanged** and Part II's percentiles need no re-derivation. The treatment
  was not marginal — 21 of 24 rooms in one block no sequence of cuts decomposes.
  ✅ **Item 4 inverted, and it is the strongest result**: INFEASIBLE — what triggers
  the two-phase fallback — fires on the guillotine arm alone **17 times against 2**,
  **p = 0.0007**. The fallback fires *less* on the class retrieval most wants to
  serve. ⚠️ **By an unexplained mechanism**: margin distributions, τ's fixed share
  and one-axis separation are all matched between arms. ⚠️ **Two premises were
  false.** τ gates on **separation margin, not adjacency** — the pinwheel's
  adjacency graph *is* denser and the margins are identical to the grid unit, so
  there was never a channel for τ to move through. And **no experiment on this map
  has ever run at `t_int` = 120**: every one ran at **100**, so the move is
  100 → 150 and the residue class 150 → 100 mod 250 — which corrects this ticket,
  ADR 0010 §3 and the grid fog patch alike. ✅ **`t_int` = 150 costs nothing inside
  C13's band** (zero discordant at 8/10/12); above 16 rooms it is directional only,
  p = 0.219. ⚠️ **The real cost of the `t_int` move is on the standards table, not
  the solver**: at 100, 12 of 36 shipped ergonomic dimensions were on the ADR 0007
  lattice *by accident*, at 150 only 6 are, and **14 of 36 gain a whole grid unit**
  — ADR 0009's exemption is 67 % dearer than when it was priced. ✅ **And the ticket's own motivating
  number was stale by 2.5×**: its 6.27 % came from the **k = 1** conversion ADR
  0016 superseded, and re-measured paired on the shipped k ≤ 2 arm the
  non-guillotine share is **5.49 % → 13.60 %** (40 across against 6 back,
  p = 3.1e-07) — the untested class was one real dwelling in **seven**, not one in
  sixteen, which makes the null result stronger. ⚠️ **The bottom of
  C13's band is still unmeasured and unmeasurable here** — below 7 rooms this
  Envelope family admits no non-guillotine tiling at all. ⚠️ And a fixture defect
  it did not cause: `AREA_PER_ROOM_M2` = 9.65 is below what the placeholder table
  needs at 7 and 8 rooms in **either** arm.

- [What shape an Envelope is when the Brief does not say](tickets/48-what-shape-an-envelope-is-when-the-brief-does-not-say.md)
  — **a candidate pool shares a floor area, not a box.** ADR
  [0020](../adr/0020-a-candidate-pool-shares-a-floor-area-not-a-box.md),
  `docs/spec/brief.md` §5/§5.1/§5.2/§6/§9.4/§12/§13, `CONTEXT.md`.
  ⚠️ **The defect was in an ADR, not a spec**: ADR 0018 asserts both readings four
  paragraphs apart — the Envelope is *"per-candidate in its `invented` fields"* and
  it is *"the Envelope, which every candidate for one Brief **shares**"* — and
  everything downstream was written against the second while the ADR shipped the
  first. **The notch is not a rounding error**: a median **12.55 %** of the bounding
  box, p10 3.13 % to p90 23.30 %, against a ±5 % hard gate — so one box for the pool
  puts **56.15 %** of the index outside `area.invented_envelope_hard` on donor
  geometry alone, and 81.61 % outside the 2 % soft preference. Fixing the **floor**
  instead and deriving `W × H = interior / (1 − s)` per candidate makes agreement
  1.0000 **by construction**, and the box may flex only where `overall_dimension` is
  invented — which is exactly where the hard rule applies, the stated path already
  being `area.given_envelope_warn`. ✅ **`rules.json` sees no change**, the opposite
  of what the ticket expected: with floor invariant the only thing left that moves
  Σ Space area is the partition footprint, which is what ADR 0010 rewrote the rule to
  catch. Re-fitting the gate to ~±13 % was available and is **refused as a modelling
  defect laundered into a tolerance**. ✅ **`shape` leaves the `ResolvedBrief`** —
  §1 makes it dense, so *"absence means unknown"* had nowhere to live; a
  `rectangular` default admits 1.12 % of the index and a corpus-mode default would
  surface a *donor's* notch as an Assumption inviting correction. ✅ **The per-candidate
  notch is therefore not an Assumption at all**, derived rather than chosen — the set
  is `ResolvedBrief \ StatedBrief`, and an Assumption is something filled in on the
  **request** where the notch is a property of the **result**. ⚠️ **The count gate was
  mis-labelling the whole index**, not merely starving rectangles: read as *material*
  notches (≥ 5 % of bbox) the corpus is **15.67 % rectangular / 52.96 % L / 25.42 %
  U-T** against the shipped count's 1.12 / 8.72 / 90.16 — raw count says 90 % of real
  flats are U/T-shaped, and **the biggest gain is the common case, `L`, at 6×**.
  ⚠️ **ADR 0018's fidelity headline is a proportion result**: `fit_warp.py:373-384`
  scales targets onto the donor's covered area, so p50 0.056 has absolute area
  normalised away and **the warp has never been measured against a stated
  `target_area`**. §9.4 goes **six bounds → seven**; bound 7 is the only one with **no
  pre-image in either direction** — a stated shape costs 84 % of the index, warns,
  and falls through to source B rather than refusing, because refusal would decline a
  request the engine can serve. ⚠️ **"Fill the notch" is recorded and not taken** — it
  dissolves the cliff and re-opens the monotone-warp theorem. ⚠️ ADR 0003 §7 is owed a
  re-reading it could not make, 47 holding that file. **Market**: ten of eleven
  surveyed products take the boundary as input and never invent one; the eleventh is
  **Maket**, C2's own buyer, which disclaims measurement in its terms — there was no
  precedent to copy.
- [Opening placement rules](tickets/16-opening-placement-rules.md) — **the solver was
  reserving zero jamb and zero nib, and a door placed on the run it had just certified
  could be hard-rejected.** `docs/spec/openings.md`, ADR 0021. `circ.potential_reachability`
  admitted a contact at `w_struct + t_int`, and ADR 0001 consequence 3 says that `+ t_int`
  is **only** the centreline-to-clear correction — so the clear run reserved was exactly
  `w_struct`, against `open.fits_segment` (100 mm/side) and `open.leading_edge_nib`
  (300 mm along the wall) binding the same segment. Threshold → `w + t_int + 400`.
  ⚠️ **The rate that costs is not measured** — handed to *What an ordered entry sequence
  costs the solver*, which holds the rig. **Doors are placed by walking in**: breadth-first
  from the entrance, each pushed to the end nearest where the path arrives, **hinge derived
  from position** and **swing into the private side, never into circulation** — which is
  why the corridor constant is **still 900** and now *derived* rather than pre-sized against
  an unknown arrangement, replacing ADR 0001's provisional answer. ✅ **Two premises the
  ticket carried were wrong.** Cased openings: the `AZ` catalogue manufactures a **glazed
  living-room door**, and AzDTN names `mətbəx` in nine clauses without once naming a door —
  so every internal opening carries a leaf except `living`↔`dining`, and the open kitchen is
  a **Brief** decision. And **800 is the interior door, not 900** — 900-everywhere would have
  cost 100 mm of reserved run per door for nothing. ⚠️ **Two live defects found in shipped
  data**: `win.habitable_has_window` was satisfiable on a **party wall** (a party wall *is*
  `External`), and three places disagreed about the kitchen window against a `verified`
  mandatory clause — `kitchen.needs_window` → true, cost handed to *H8 and the single-aspect
  flat*. ⚠️ **`balcony_door` can never be placed** and is the sole anchor of `head_datum_mm`:
  the number is right, ADR 0012's reason for it is dead. ⚠️ Six rule statements moved in
  `rules.json` with **no rule added** and no edit to `acceptance-bar.md`, which is claimed
  twice — a real, listed divergence, not an oversight. **Market**: of ~20 published
  generators **none emits a wall with thickness**, so none places a door; the commercial
  tools place openings by rule after the layout, which is why post-solve needed checking
  rather than accepting.

- [H8 and the single-aspect flat](tickets/26-h8-and-the-single-aspect-flat.md) —
  **there was no crisis, and both numbers that made one were wrong.** H8 is not
  relaxed by type, not relaxed by count and the room-count promise is not bounded:
  against the *shipped* ergonomic layer the first arithmetically dead cell moves
  from **7 rooms to 16**, outside C13's band. The old table ran on
  `scenarios.STANDARDS`, which says in its own comment that it is a placeholder.
  ⚠️ **And `exposure_swiss_dwellings.py` never measured a dwelling**: a dwelling's
  room polygons are disjoint, so the union is always a `MultiPolygon` and
  `max(geoms, key=area)` took the **largest single room** — every published
  exposure figure is one room's perimeter. Corrected **median 0.37 → 0.67**, p25
  **0.23 → 0.51**, median area of the thing measured **23.9 → 75.3 m²**. The script
  and `dataset-inventory.md` §1.5 are fixed; the presets fitted to the old column
  are ticketed. ✅ **Two rules retired because neither could fire** —
  `win.habitable_touches_exterior` was strictly implied by `win.habitable_has_window`
  (no table row is `is_habitable` without `needs_window`), and
  `win.kitchen_windowless` was unreachable once the kitchen took its window. **38 →
  36 rules**, both kept in a `retired` block, and the `both` subset holds at 14
  because `has_window` **takes the solver posting and takes it stronger** — the
  frontage budget itself, not mere contact. ⚠️ **The bar's real cost is measured for
  the first time and it is not frontage**: `win.habitable_has_window` rejects
  **43.3 %** of real Swiss dwellings, **23.0 points of it the kitchen alone**, and
  **31.0 % of real kitchens have no window** against 5.9 % of bedrooms — median
  6.8 m², **84.7 % adjoining a windowed room**, so it is borrowed daylight, not
  niches. Zero orphan windows in the attribution audit, so the number stands. The
  rule is right for Baku (cl. 9.12, mandatory) and the cost is corpus coverage.
  ⚠️ **The hard bar admits a 1.85 × 1.68 m "double bedroom"** — which *The
  annotation spec is US-shaped* had already reproduced from the other end, as a tag
  overflowing in a real solved layout. `acceptance-bar.md` §3 and §7,
  `rules.json`.
- [The exposure presets were fitted to a measurement of one room](tickets/49-the-exposure-presets-were-fitted-to-one-room.md)
  — **the presets are quantiles of the corrected distribution, and the named-type
  family is refuted by measurement.** Fitted on **exterior run per room**, not on a
  fraction of perimeter — a fraction only transfers between dwellings whose perimeters
  match and these do not (36.0 m around 75.0 m² against 47.6 m around 94.1 m² at eight
  rooms), and **H8 reads run**. Anchored at n = 7; corpus run per room p5 **2.09 m**,
  median **4.19**, p95 **6.94**. ⚠️ **Three published results did not survive**: H8's
  six-room corpus-median failure (0/5 → **5/5**), `flat_single_aspect`'s *"fails at 6,
  7, 8, mostly at 9"* (now **6 only**), and the **flat-versus-house diversity gap**,
  which is **gone** — 0.54×/0.73× → **1.00×/0.98×**. ⚠️ The **ring shape was never
  measured** and refutes the preset family: real dwellings are **63.3 % four-sided** and
  **26.0 % three-sided**, where the three flat presets name **10.6 %** between them and
  no preset was three-sided at all. Keys kept, because five documents and three
  experiment directories name them; a key is now a **quantile with a ring shape**.
  ⚠️ Three structural defects found and **not fixable here** — every preset **drifts 60
  percentiles** across C13's band, the Envelope is **more compact than a real dwelling**
  (perimeter/area 0.390 against 0.572 at twelve rooms, `AREA_PER_ROOM_M2` **9.65 against
  a corpus median 11.36**), and **`exterior_fraction` double-counts** (144 grid units
  counted as 180) — all owned by *The toy Envelope is more compact than a real
  dwelling*. ✅ **Two re-runs declined on a checked premise**: ticket 47 and ADR 0003's
  notch cap read **no exposure at all**, so this ticket's own claim that they read the
  same distribution is **false** and neither needs re-running.

- [A dwelling with no toilet passes every check](tickets/42-a-dwelling-with-no-toilet-passes.md) — four `programme` rules, one per limb of AzDTN cl. 5.2, binding the **Brief and nothing else**; three hard, storage **warn** at 73.35 % corpus cost. ADR 0022. The WC limb cost a **nineteenth Room type**: over eighteen it rejected **48.32 %** of real dwellings, 43.13 points of which *have* a toilet in a room with a bath and no way to say so.

- [Fit the ENGINE_CHOICE acceptance thresholds to the corpora](tickets/20-fit-engine-choice-thresholds-to-the-corpora.md) — **the widest gap on the map is closed, and `conf` was what was blocking it.** ADR 0023 adds a fourth provenance value, **`fitted`**, because a number measured against 42,985 real dwellings and a number invented carried the same mark; `ENGINE_CHOICE` **18 → 9**, and the nine left have no magnitude to measure. **Two thresholds move**: `wet.plumbing_group_count` 2 → **3** — the ticket predicted exactly this and the tail reaches three at **14.14 %** — and `area.invented_envelope_soft` 2 % → **3 %**, because the 250 mm grid alone misses 2 % in **13.71 %** of dwellings. **Seven guesses hold**, `dim.aspect_ratio_hard` most precisely: 3.0 **is** the p99.5, at 3.02. ⚠️ **The conjunction is the finding nobody had**: the bar rejects **84.41 %** of real Swiss dwellings as shipped, **82.31 %** fitted, and **eleven of thirteen hard rules cost under a third of a point between them** — it is two opening-layer rules and a rounding error, and no threshold move can touch it. ⚠️ **A regression was found and repaired**: `kitchen.needs_window` was reverted to `false` by 42's generator re-run, falsifying three published numbers.

- [The two-notch cap is now evidenced, and more notches is not the fix](tickets/47-the-two-notch-cap-is-now-evidenced.md) — **the cap stands at two, the shape family is refused, and the question was mis-posed.** ADR 0003, second amendment. There is no ground truth on the generation side to be unfaithful to — `shape` left the `ResolvedBrief` and ADR 0020 derives each box from the *donor's* notch share — so the tail is a **donor-quality** fact. ⚠️ **More notches was never the fix, and now the mechanism is known**: sixteen tail dwellings are inside the cap already, and at `notches_all` = 1 the loss is **identical at every k**, because a notch is one *rectangle* and a complement component need not be one. The tail is two populations — **38.2 % rectilinear, 49.5 % more than 10 % off-axis** — and a vertex-budget ring, the only coherent widening, tops out at **4.17 % of the corpus** with 46.3 % of that still failing at four notches. ⚠️ **Envelope loss is a predictor and a poor gate**: 42.2 % of the loss tail converts faithfully anyway, 12.70 % outside it does not, and an IoU cut removes **10.09 % of the most faithful envelope band**. The quantity is **worst-room IoU**, already in every fit record; its population is **154 dwellings, 6.65 % of the index**, two thirds of it invisible to either proxy. Owed by `proposer.md`'s next holder, specified ready to transcribe. ✅ **48's §7 correction is written** — one ring **per candidate**, safe because the entrance edge is identified by side and never by ring index. ⚠️ **Ticket 46 is handed 8.76 %** where it scopes 1.5 %.

- [A statutory floor, posted soft, in the one region v1 ships](tickets/50-a-statutory-floor-posted-soft.md)
  — **C14 is amended, monotonically: a Region profile may RAISE a hard floor and may
  never lower one.** Both halves taken hard. `dim.statutory_min_area` is new
  (**42 -> 43 rules**, conformance subset **15 -> 17**) and `win.area_ratio` moves
  soft -> hard, rescoped to living rooms and kitchens per cl. 9.13.
  `acceptance-bar.md` §3.1 and §7.4, `CONTEXT.md`. ⚠️ **The rule this map was
  proudest of does nothing**: `dim.min_area` rejects 0.19 % of real dwellings and adds
  **0.00 %** to the hard union — the only inert rule in the registry — while being the
  sole predicate between a Homeowner and the 3,1 m² bedroom §3 was written to forbid.
  ⚠️ **The 54,51 % corpus cost is NOT a rejection rate and the resolution says so
  twice**: the bar does not gate the retrieval index (admission is conversion fidelity),
  and `market_default` is at or above `statutory_floor` in **every** reachable AZ cell,
  so the new rule is strictly weaker than the target the solver already aims at and
  fires only where the solve failed to reach it. `room-area-bands.md` §6.1's coverage
  argument does **not** transfer. ⚠️ **The kitchen limb lands on the corpus median**
  (8,0 against a Swiss p50 of 8,04) and is 16,88 of the 19,98 marginal points; without
  it the decision costs **3,10 %**. Taken anyway on §7.5's own precedent. ⚠️ **The
  yield risk is real and named**: the warp has never been measured against a stated
  `target_area` (`fit_warp.py:373-384` normalises area away), so if it undershoots,
  this rule collapses yield — a one-field, build-time rollback, against a soft rule
  that ships a 6,6 m² kitchen to a Baku Homeowner as a survivor. **That asymmetry is
  the decision.** ⚠️ **Two shipped files disagreed and both were wrong**:
  `room-constraints.json` bound `statutory_floor` as a **warn** and `rules.json` listed
  it **unread**, and neither had a rule behind it — C14's *never rejects* had been
  implemented as *never appears in the hard set*, a stronger claim C14 never made.
  ✅ **The window is now sized, not picked, and that is what made the glazing rule
  safe**: against the three-entry catalogue 1:8 fails **21,20 %** of dwellings, against
  a width series **5,39 %** — three quarters of the cost was a catalogue artefact.
  `min_pier_mm` is therefore **not** load-bearing here. ⚠️ **One blocking handoff**:
  the width series values are `room-constraints.json`'s and that file is 32's — reach
  requirement p90 2,47 / 3,23 / 1,34 m, written into `rules.json`'s own `owed` block.

- [The annotation spec is US-shaped and the drawing is now Azerbaijani](tickets/32-the-annotation-spec-is-us-shaped.md)
  — **everything a person reads on the sheet conforms to SPDS; the layer names do not,
  and one line decides it: *a sheet mark is read on paper by a builder, a layer name is
  read on import by a program*.** ADR 0024. The set is `MH` with sheets numbered inside
  it — **not** `MH-101`, because SPDS carries the designation on the *set* where NCS puts
  it on each sheet, so `A-101` has no counterpart of the same shape. ✅ **No new profile
  object, and the ticket's warning pointed at the wrong thing**: the `drawing` block
  already existed and what was missing was a **membership test** — *a field is
  region-parameterised iff a person reads it* — which is now in the block, and under it
  the block is complete rather than growing. ✅ **The BLOCKING window series is written**,
  and ⚠️ **ticket 50's shape had to change twice**: it cannot be *bounded by
  `gost_11214_86`*, whose widths stop at 21 dm against 50's own p90 of **3,23 m**, so the
  top four members are an engine extension marked by `published_through` and above it the
  schedule prints a dimension string rather than a fabricated mark; and 50's *splitting
  buys nothing* is **true when the wall run binds and false when the catalogue top
  binds**, a distinction it had not drawn. ⚠️ **It forced an amendment to `openings.md`
  §6.1, a file the ticket does not hold, because the shipped spec's own worked example
  fails the shipped bar** — `living` at ratio **0,250**, nearly twice target because the
  increment was a whole window; `kitchen` at **0,120**, *below the now-hard floor*,
  described as surviving on a soft penalty; and **`bedroom_single`'s window omitted
  entirely**, which `win.habitable_has_window` rejects hard. ⚠️ **ADR 0010's tier-1
  replacement was narrowed**: *inner ring on every edge* would have made tier 1 restate
  the span every tier-2 chain already closes on **and left the sheet with no external
  footprint**, on a map that ships houses — so it is **outer face on an exterior edge,
  inner face on a party edge**, and no centreline survives either way. ⚠️ **Re-deriving
  §14 at the shipped `t_int` 150 found two defects nothing else would have**: the
  schedule's **totals row does not add up** (43,58 exact against 43,59 printed — every
  total is now computed from the *printed* cells, and the Drawing check gains a
  **twelfth** predicate), and **§4.5's setting-out datum names opposite ends** on every
  non-minimal run while its value is **100 mm for every internal door in every plan**.
  ✅ **A first-hand clause dropped by ticket 17 is landed rather than handed on a third
  time** — a residential plan annotates its area as a **fraction, living over useful**
  (cl. 2.3.2), both inputs already computable. ⚠️ **`faydalı sahə` and `ümumi sahə` are
  numerically identical in v1 and are not the same quantity.** ✅ `ergonomic_check.py`
  **229/1 → 233/0**, discharged at the **authoring site** because a JSON-only edit
  reverts. ⚠️ **26's 1 650 mm bedroom was weighed and refused** — the ergonomic layer is
  a *fits* floor by construction and raising it rejects 19,3 % of real rooms — but the
  defect it names is real and now has an owner: **a 1 850 × 5 400 bedroom passes every
  hard rule**, and `market_default` 3 000 **ships and is read by nobody** because the
  only rule consuming that tier is an area term.

- [A third of real kitchens have no window and the engine may not draw one](tickets/51-a-third-of-real-kitchens-have-no-window.md)
  — **the corpus is admitted unfiltered on glazing, because glazing is not a property a
  donor hands over.** ADR 0025, `proposer.md` §4.5. All four offered options are refused
  as posed: each treats the donor's windows as inherited, and **§1 emits boxes with no
  openings**, `openings.md` §6.1 glazes every Space **after** the solve, and the
  **solver** posts the frontage budget hard. ✅ **The overlap the ticket demanded is
  measured and it kills option 1**: paired on ADR 0016's own sample — whose 9.74 %
  reproduces at **9.75 %**, which is the join's check — the two drops **compound**, both
  refusing 4.13 % against 3.83 % under independence, **lift 1.08×**, joint **44.91 %**.
  A glazing filter hands back four times what ADR 0016 bought. ✅ **The population is
  6.39 %, not 43.3 %** — **86.04 %** of every dwelling the rule rejects holds its dark
  room **on the boundary**, where this engine reglazes it free, and **88.36 %** of 12,717
  windowless kitchens reach a wall. The failure mode is **INFEASIBLE at the solve**, not
  rejection at the bar. ⚠️ **Three published per-room figures move at 80× the sample, and
  one was the ticket's own warning coming true**: 43.3 → **38.55 %**, kitchen 31.0 →
  **28.90 %**, and `LIVING_ROOM` **20.0 → 10.09 %** — it *was* the 105-room labelling
  effect the ticket said to check. `DINING` at **19.54 %** is new. Restricted to h8's own
  population the headline is 38.77 %, so the gap is **sample size, not population**.
  ⚠️ **Do not overwrite `rules.json`'s 0.4519**: it is the *raw* arm over 42,985
  unconverted dwellings, and the same rule's leave-one-out contribution to the bar is
  **15.97 points** — three numbers, three questions, and `acceptance-bar.md`'s holder
  owes the sentence saying which is which. ✅ **What retrieval owes is a field and a rank,
  not a gate**: `frontage_reach`, a **partition** at 1.0 in the pre-rank with **no free
  parameter** because that is where the solver's own constraint sits. ⚠️ It deliberately
  **refuses ticket 47's gate-then-rank precedent** — worst-room IoU is a pure donor fact
  and this one is joint with the Brief's Envelope, since §2.2.6 records the conversion
  cannot tell `exterior` from `party`. **6.39 % is a floor, not the residue's size.**
  ⚠️ **Source B's warning is false as stated and is corrected on the record**: the model
  has **no window token**, so the only thing it learns from a windowless kitchen is an
  *interior* one, at **5.88 %** not 31 % — no training filter, and §6.1 gains a
  **fourth** plan-quality term, which is also the answer to *"the three terms do not
  measure daylight"*. ⚠️ **Option 4 was the largest lever and is still refused**: a niche
  exception retains **91.47 %** of the index against 61.45 %, thirty points — refused for
  having **no producer and no consumer**, not for being small. ⚠️ **And the evidence two
  documents rested it on is withdrawn**: *adjacency is not openness*, and of the 11,139
  windowless kitchens adjoining a lit room **5,227 (46.93 %) carry a DOOR on that shared
  boundary**, which a niche does not have; the rest is **undetermined**, not confirmed.
  ⚠️ It leaves a named, unproven lead for ticket 52's six-room mystery: `kitchen.needs_window`
  went `true` **after** those presets were fitted.

- [The warp has never been measured against a stated target area, and a hard rule now rests on it](tickets/54-the-warp-has-never-been-measured-against-a-stated-area.md)
  — **the argument `dim.statutory_min_area` was posted hard on is refuted, and the
  number is at the pool level.** `experiments/warp/absolute_area.py`,
  `proposer-architecture.md` §7.5. On Briefs whose every target sits at or above
  `market_default` — the argument's own premise — **31,1 % of candidates put a Room
  under its floor** and **6,7 % of Briefs have no candidate in a pool of eight that
  clears**, against ADR 0018's 6,9 % for every dimensional decline combined.
  **The shortfall is one-sided**: 57,7–59,0 % of Rooms come in under target, plan
  totals mean −4,3 %, which is exactly the case ticket 50 named as fatal and
  discounted because `dim.market_default_area` is two-sided.
  **Two defects, two owners, and the split is measured**: calibrating the box until
  Σ Space = `target_area` needs **+4,2 %** and takes plan loss 30,7 % → 18,8 %, so
  ~2/5 is one constant and ~3/5 survives a perfect level. The kitchen is the limb —
  **21,8 %** below 8,0 m² when asked for 9,0, lower quartile of the survivors
  **+0,085 m²**.
  ⚠️ **Do not compound a per-candidate share into a Brief-level one** — independence
  predicts 0,009 % against the measured 6,7 %, a factor of 780. ADR 0018 c.3, twice.
  ⚠️ **The numbers are good to one decimal and no further**: CP-SAT under a
  wall-clock cap is not reproducible, measured at 5,96 % vs 5,78 % on two identical
  runs.

- [The sizing rung under-delivers by four per cent, and `f` is not where to fix
  it](tickets/56-the-sizing-rung-under-delivers-on-the-warp-path.md) — **it does
  not, and `f` is vindicated.** The 4,2 % was **two defects in how the rig
  measured the Envelope**, neither in `brief.md`: it eroded a 75 mm ring ADR 0001
  does not lose (**3,7 % of `interior` at p50** — ADR 0001 tiles the Envelope
  *dilated* by `t_int/2`, so a boundary edge erodes back onto the external wall's
  face and costs nothing), and it let the warp resize the notch, which ADR 0020's
  by-construction guarantee assumes it cannot (**1,5 %**). Corrected, Σ Space lands
  **+0,4 %** of `target_area`. `brief.md` §5.3, ADR 0020 amended.
  ⚠️ **It corrects ticket 54's split at the root**: *"two fifths of the damage is
  one constant in one file"* is **false — none of it was**, and `calib`'s 18,8 %
  over-stated the gain by half because scaling until Σ Space hits `target_area`
  buys margin a correct Envelope does not give.
  ⚠️ **`dim.statutory_min_area` is about half as expensive as posted**: 31,1 % →
  **25,5 %** of candidates and 6,7 % → **3,6 %** of Briefs at pool-of-8, same
  sample and seed. 55 is **unblocked** and judges that.
  ⚠️ **The live defect it found is `proposer.md` §2.2.3's**, and 53 holds it: the
  notch may not *"warp along with everything else, for free"* — that sentence is
  what makes ADR 0020's guarantee false, at **5,6 points** of plan-level statutory
  loss. Not ADR 0003 c7, which fixes the entrance edge and not the notch.

- [One wall weight where a real plan draws
  three](tickets/36-one-wall-weight-where-a-real-plan-has-three.md) — **all three
  priced shapes refused; the Plan draws two weights because the third is a
  structural claim the engine cannot make** — ADR 0026. The **76,1 % is measured
  on the wrong artifact class**: Swiss Dwellings is *surveyed built* dwellings,
  whose weights exist because an engineer decided the load paths first. Three
  weights is a **working-drawing** property; this engine emits a concept-stage
  design and a concept plan has two. **Nothing in the pipeline could draw it
  anyway** — ADR 0003 c3, plus `fit_rects.py:125` destroying per-wall thickness at
  conversion, plus §2.3's model having no thickness token. **Shape A's geometry
  ships and A's *delivery* is refused**: the admission is a general note on the
  **sheet**, on `annotation.md` note 8's own precedent, because *"a DXF outlives
  the session that produced it."* `Wall.load_bearing` stays `None` for the life of
  v1; `t_int_bearing` = 250 stays `verified` and unspent.
  ⚠️ **Shape B was mis-priced by the ticket and is now REFUTED, not merely
  unchosen.** *"ADR 0001's uniformity survives where it is load-bearing — the
  solve"* is worth nothing, because **no hard rule binds the solve alone**: solve
  at 280 and draw at 150 and every thin partition leaves a 65 mm strip belonging
  to nothing, which is **up to 4,9 points of Σ Space** (≈4,3 at the corpus's
  bearing share) against a hard `model.no_unassigned_area` — a whole
  `area.invented_envelope_hard` gate of void. Absorb it and
  `model.space_matches_erosion` dies instead. **B breaks one of the two hard rules
  or the other, exactly as C does**, and pays 19 of 36 room-axes an extra solve
  cell on top. Any future second weight is built on C.
  ⚠️ **The gap is reclassified, not closed** — 76,1 % of real dwellings still
  carry a hierarchy this sheet does not. And **two shipped general notes are
  individually true and jointly misleading**: note 3's *"unless noted"* promises an
  exception mechanism that does not exist, and note 7 states *performance*, where
  the missing claim is **identification**. Both are `annotation.md`'s, with the
  Drawing check going **12 → 13**.

## Not yet specified

In scope, not yet sharp enough to ticket. Graduates as the frontier advances.

- **A Homeowner shown candidates whose outlines differ.** ADR 0018 makes the Envelope's
  notch geometry **per-candidate** wherever `shape` is `invented` — honest, because the
  position is genuinely undetermined by the Brief and the corpus knows real ones, but
  nobody has decided how the preview presents two plans with different outlines, or
  whether it should present them at all. It touches `homeowner-surface.md` and the
  DXF/IFC sheet, so it is not one ticket's question yet. Adjacent to the *stated one
  gets none* asymmetry already recorded under **Variant generation and ranking**, and
  probably resolves with it.
  ✅ **Narrowed twice by *What shape an Envelope is when the Brief does not say*, and
  the Brief half is off this patch.** The per-candidate outline generates **no
  Assumption** — the set is `ResolvedBrief \ StatedBrief` and `shape` is no longer a
  `ResolvedBrief` field, correctly, because an Assumption is something filled in on the
  **request** and an outline is a property of the **result** (ADR 0020). So this is
  purely a gallery question, and it is the same request-versus-result confusion *A
  request and a result in one typeface* is already open on — the two should be read
  together. ⚠️ **And it now has a magnitude**: two candidates that agree on floor to the
  millimetre can differ by up to **30 %** in bounding box at the p90 notch, so this is
  not a subtle difference a preview might get away with eliding.
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
  ~~⚠️ **And the asymmetry now has a number, and a second cause the proposed patch does
  not reach** — 0.54× at 5 rooms and 0.73× at 7, detached against corpus-median.~~
  ✅ **That second cause does not exist, and this patch should stop carrying it.**
  *The exposure presets were fitted to a measurement of one room* re-ran the probe at
  the re-fitted `corpus_median`, which had been running at the corpus **p4–p10** rather
  than the median it is named for: the ratios are **1.00× at 5 rooms and 0.98× at 7**,
  and the ranges now overlap almost exactly (0.514–0.524 against 0.515–0.525). The
  probe's own irreproducibility caveat is what makes this trustworthy as an *absence* —
  it reports ranges because multi-worker CP-SAT under a wall-clock deadline is not
  reproducible, and non-overlap was the old reading's entire claim. **The asymmetry goes
  back to the diversity axis alone**, which is where this patch already had it. ✅ **Sharpened a fourth time by *What shape an Envelope is when
  the Brief does not say*, and one half of the asymmetry has quietly closed.** ADR 0020
  derives each candidate's bounding box from its own donor's notch share, so an
  **invented** Envelope already varies its box across the pool — up to **30 %** at the
  p90 notch — without anyone handing out an aspect-ratio axis. The proposed axis was
  therefore going to be issued to the case that has one and withheld from the case that
  does not, which is the asymmetry *backwards again*. What a **stated** Envelope still
  has no diversity axis for is unchanged, and *which room absorbs* remains the only
  candidate that reaches it. The mechanism is
  **H8**: habitable rooms are pinned to the exterior run, so fewer exterior edges means
  fewer distinguishable arrangements. Adding an aspect-ratio axis to stated Envelopes
  therefore closes at most half of this, and the half it does not close is the half that
  applies to every flat. `experiments/envelope-exposure/`, which imports `solver-toy` rather than
  editing it.
  ⚠️ **Both ratios are now suspect, and the reason is not the solver's non-determinism.**
  *H8 and the single-aspect flat* found the exposure distribution the presets were fitted
  to had measured **one room per dwelling**: real p25 is 0.51 against 0.23 and the real
  median 0.67 against 0.37. `corpus_median` is therefore a **dual-aspect** flat, and the
  0.54×/0.73× gap was measured between `detached` and a preset roughly half as exposed as
  the case it is named for. The *direction* is unlikely to flip — fewer exterior edges is
  still fewer arrangements — but the magnitude is unmeasured until *The exposure presets
  were fitted to a measurement of one room* lands, and this patch should not quote it as
  a number before then.
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
  ✅ **The `deferred` WC rule stayed deferred through *Opening placement rules*, which
  is the check that mattered**: that ticket designed swing direction with no
  fixture model at all — into the private side, fallback to the other, then reject —
  so nothing now depends on a pan existing, and adopting the 250 mm overlap later
  stays a data change rather than a redesign.
- **The ordered entry sequence, and whether it is worth new integers** — ⚠️ **now a
  ticket, not fog**: *What an ordered entry sequence costs the solver*, ✅ **now
  unblocked** — the re-base it waited on happened and moved nothing, so the rig it
  prices against is the published one (ADR 0019). It is the **one** property of
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
  measured-vindicated (ADR 0003), and **it sizes this patch a second time, at the dwelling scale**: **8.76 % of dwellings** have an *outline* more than 10 % off-axis in their own frame, and they hold **49.5 %** of the envelope-loss tail — five times the 1.5 % *The dwelling that is built on two angles* currently scopes, and a different measure (outline perimeter, not a room off frame by 10–20°). `rectangularisation.md` §13.2. ✅ Its **deliberately unbuilt dependency** is
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
  is visible in the shipped artefact, not just in the model. **Charged a third time, and
  now in the one place a builder reads:** ADR 0026 puts the unknown on the **sheet** as a
  general note, so the model, the IFC and the drawing say one thing. ⚠️ Note the profile
  already publishes `t_int_bearing` = 250 as a `verified` catalogue value that **no wall
  type ships**, so the structural question has a number waiting as well as a field.
  ⚠️ **This patch now owns ADR 0026's reversal trigger, and it is narrow on purpose.**
  The second wall weight comes back **only when the engine is given structure rather than
  asked to infer it** — a Brief carrying existing fabric, where the bearing walls are
  stated, surveyed or read off an existing plan. Renovation, not new-build; C5 ships a
  dwelling with no fabric to inherit. It does **not** come back on a better classifier, a
  larger corpus, or a flag derived from donor thickness — those change how good the guess
  is, and the objection is that it is a guess presented as an instruction. If it does
  return, it returns as **shape C**: B is refuted, and C buys 10,3 of the 12,8 available
  fidelity points on values already in the profile, for one hard rule.
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
  ✅ **One half of this is now measured, and it went the opposite way to the fear.**
  ADR 0019 asked whether a non-guillotine target — the class retrieval most wants to
  serve — pushes more Proposals into the fallback. It pushes **fewer**: paired over
  212 slots, INFEASIBLE fires on the guillotine arm alone **17** times against the
  pinwheel arm's **2**, exact McNemar **p = 0.0007**, spread across σ and room count
  rather than concentrated. ⚠️ **The mechanism is unexplained** and the three obvious
  candidates — separation-margin distribution, the share of pairs τ fixes, and the
  fraction of pairs the truth separates on one axis — are all *matched* between arms,
  so this is an open question rather than a closed one. The **distribution** half is
  untouched and still needs a real Proposer.
  ⚠️ **One named contributor now has a corpus-side floor.** ADR 0025 routes the whole
  glazing residue here rather than to the bar: **6.39 %** of index dwellings hold a
  `needs_window` Room that cannot meet the frontage budget the solver posts, so they
  reach **INFEASIBLE** and trip the fallback rather than being rejected at validation.
  That is a floor and not a rate — `frontage_reach` reads boundary *contact* and the
  conversion cannot tell `exterior` from `party`, so the realised number depends on the
  Brief's Envelope and is only knowable once a Proposer runs. `proposer.md` §4.5 also
  demotes those donors in the pre-rank, so the share **reaching** a solve is lower again
  by an amount nothing has measured.
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
  on this map covers the bottom half of C13's own 3–10 band.** ⚠️ **The staleness note here was itself wrong, and ADR 0019 corrects it**: the deletion figure was computed at `t_int` **100**, not 120 — no experiment on this map has ever run at 120 — so the residue class moved **150 → 100 (mod 250)**, not 130 → 100, and the step made was 50 mm rather than 30. *One internal thickness* supplies a **partial** starting point and not a conclusion: the move cost **253 solve cells either way**, so no per-room ceiling changed — but the deletion also turns on the Envelope's own re-snapping, which that arithmetic does not touch.
  ⚠️ **This patch is now heavier, and for a reason nobody had computed.** ADR 0009 bought the grid by exempting the ergonomic layer, and **the price of that exemption is a function of `t_int`**: at 100 it was cheap by *accident* — 900, 1400, 1650, 1900 and 3150 mm are all congruent to 150 (mod 250), so **12 of 36 shipped clear dimensions sat exactly on the lattice**. At the 150 ADR 0010 ships only 6 do, **14 of 36 gain a whole grid unit** (a 900 mm minimum is now delivered at 1 100), and summed waste over the table goes **2 524 → 4 224 mm**. A finer grid is what makes the exemption cheap and the exemption just got **67 % dearer**. ✅ What is *no longer* owed here: `t_int` is measured to cost **nothing inside C13's band** — zero discordant slots at 8, 10 and 12 rooms, both arms — and the loss above 16 rooms is directional only (5 against 1, p = 0.219). ADR 0019, `experiments/solver-toy/t_int_arithmetic.py`.
  ⚠️ **And the grid now has an *area* price, which nothing here had computed.** *Fit the ENGINE_CHOICE acceptance thresholds to the corpora* re-expressed every real room with both dimensions rounded to 250 mm: Σ Space area moves by p50 **0.90 %**, p95 **2.64 %**, p99 **3.57 %**, and the residual alone exceeds a 2 % target in **13.71 %** of dwellings — which is why `area.invented_envelope_soft` had to move to 3 %. So the grid is not only deleting small dwellings, it is spending the tolerance the invented-Envelope gate has to live inside, and a finer grid buys that back too.

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
