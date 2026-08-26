# Fitting the ENGINE_CHOICE acceptance thresholds

Ticket 20, *Fit the ENGINE_CHOICE acceptance thresholds to the corpora*.
Harness: `experiments/acceptance-thresholds/`. Decision: ADR 0023.

The acceptance bar shipped with eighteen rules whose numbers no source dictates.
They were set by judgement so v1 could ship a bar rather than wait for one, and
the ticket's own stated failure mode was that one of them turns out to reject
real, built homes. This measures every one of them against 42,985 real Swiss
dwellings and 16,612 ResPlan plans, and prices each rule in dwellings rejected.

---

## Headline

**Two thresholds move, seven are vindicated, and the vindications are the more
useful half** — a guess that survives measurement stops being a guess.

| what | result |
|---|---|
| `wet.plumbing_group_count` ≤ 2 | **WRONG, as the ticket predicted.** The tail reaches three: 14.14 % of real dwellings have three plumbing groups. **Moves to 3**, which costs 0.20 % |
| `area.invented_envelope_soft` = 2 % | **WRONG for a reason nothing had checked.** The 250 mm grid alone moves Σ Space area by more than 2 % in **13.71 %** of dwellings, so the soft target is unreachable for reasons that have nothing to do with design. **Moves to 3 %** |
| `dim.aspect_ratio_hard` = 3.0 | **RIGHT, and right to three decimal places.** The p99.5 of real room aspect is **3.02**. Chosen by judgement, landed on the percentile *What a room's area is allowed to be* chose independently, at the same 3 % cost |
| `circ.fraction_hard` = 0.30 | **RIGHT.** p99 is 0.284, p99.5 is 0.322. It sits inside the tail exactly where its own note claims, and costs 0.69 % |
| `open.fits_segment` = 100 mm | **RIGHT twice over.** As a fit test, 100 mm is below the p1 of the slack real construction leaves. And the same 100 mm, used by `openings.md` §3.2 to *place* the door, sits at roughly the **p40** of real door returns — so an engine door is never tighter to its corner than a median real one |
| `efficiency` ≈ 0.85 | **RIGHT.** Fitted p50 **0.8423**. Publishes at 0.84 |
| default Envelope aspect ≈ 1.35 | **RIGHT.** Fitted p50 **1.376**. Publishes at 1.38 |
| `AZ.openings.min_pier_mm` = 600 | **WRONG and not fixable from this corpus alone.** Real window-to-window piers sit at a median 621 mm *after* mullions are merged out, but 48.65 % are below 600. Recommended **250**, with the merge sensitivity stated |
| the bar as a conjunction | **84.41 % of real Swiss dwellings are rejected by the hard registry as shipped, 82.31 % after this ticket's moves — and 61.23 % once `open.fits_segment` is read on real piers rather than on full-width openings.** Two rules carry all of it: `open.fits_segment` and `win.habitable_has_window` (45.19 %) |

**And a regression was found in passing and repaired.**
`ergonomic.rooms.kitchen.needs_window` had been moved `false → true` by *Opening
placement rules* and **silently reverted to `false`** by the next run of
`build_ergonomic_layer.py`. Three published numbers rest on it. §10.

---

## 1. What was measured, on what, and in which plane

Two populations, never pooled, each chosen per predicate rather than once for
the whole study.

### 1.1 The raw arm — and the erosion the ticket warned about does not apply here

The ticket instructs: *"erode before you compare"*, because a converted room's
rectangles are centreline and every threshold in `rules.json` is stated clear.
That instruction is correct **and it applies only to the converted arm.**

`docs/research/rectangularisation.md` §1.1 settled the plane of the raw corpus:
Swiss Dwellings stores the **clear** polygon — inner faces, wall body in the gap,
p50 nearest-neighbour gap 99 mm, share touching 0.000. A Swiss room polygon *is*
`CONTEXT.md`'s Space. Eroding it by `t_int/2` would take a clear number to a
clear number minus a wall, which is the error the ticket is warning against, in
the opposite direction.

So: **the raw arm is fitted with no erosion, and the converted arm with the full
`t_int`.** Both are stated per number below.

| | raw arm | converted arm |
|---|---|---|
| source | `geometries.csv`, in-band residential apartments | `rectangularise/out/swiss_fit_k2.json` |
| dwellings | **42,985** | 2,317 usable of 2,600 |
| plane | clear, as stored | centreline, eroded by 150 mm |
| geometry | polygons | 1–2 rectangles per Room, 250 mm grid |
| used for | area, aspect, circulation share, wet grouping, jamb return, piers, envelope | `dim.min_clear_*`, per-part aspect |
| bias | none beyond the corpus's own | 9.74 % thinner, store- and bedroom-heavy under-represented (ADR 0016) |
| repairs | **0** invalid polygons encountered | — |

**The ticket's own population warning is stale in this ticket's favour, and it
was right to leave the instruction standing.** *Re-measure the conversion at two
rectangles per Room* took the conversion drop from 31 %/40 % to 9.74 %/6.40 %.
Every number below says which arm it came from anyway, because the instruction
outlives the number that motivated it.

### 1.2 The classification, which invents nothing

Corpus label → the class this system reasons in, using two already-decided rules
and no new mapping:

- `{ROOM, BEDROOM, STUDIO}` collapse to one class (*What the model proposes*).
- `BATHROOM` splits at `ergonomic.corpus_label_split.threshold_m2` = 2.4 m².

`room*` is scored against `bedroom_double`, the AZ market default; `bedroom_single`
is reported as the loosest sensitivity and moves nothing (§11.2).

---

## 2. `dim.aspect_ratio_hard` — the one rule with no precedent, and it survives

The ticket said to check this first, because it is the only rule in the spec with
no precedent anywhere and its failure mode is rejecting good plans.

### 2.1 It is exactly the p99.5 of a real room

Raw arm, 235,045 binding rooms (habitable and wet; `corridor`, `hall`, `storage`
exempt as the rule already says), bbox aspect in the dwelling's own frame:

| | p50 | p75 | p90 | p95 | p99 | **p99.5** | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| all binding rooms | 1.39 | 1.63 | 1.91 | 2.14 | 2.71 | **3.02** | 6.85 |
| `room*` (97,775) | 1.37 | 1.59 | 1.79 | 1.94 | 2.24 | 2.33 | — |
| `kitchen` (41,660) | 1.45 | 1.76 | 2.17 | 2.50 | 3.35 | 3.63 | — |
| `bathroom` (51,414) | 1.39 | 1.62 | 1.87 | 2.09 | 2.52 | 2.81 | — |
| `living_dining` (23,168) | 1.37 | 1.66 | 2.11 | 2.34 | 2.96 | 3.21 | — |
| *`corridor`, exempt* | 1.71 | 2.41 | 3.30 | 3.87 | 5.00 | 5.43 | — |

**3.0 is the p99.5.** And the cost lands where *What a room's area is allowed to
be* put its own: that ticket refused a p95 cap at 26.6 % rejection and chose
p99.5 at **3.1 %**. This threshold, chosen by judgement months earlier and for a
different reason, costs **2.85 %** of real dwellings. Two thresholds, two
tickets, one tolerance, arrived at independently.

`dim.aspect_ratio_soft` at 2.2 is the **p95** (2.14) of the same distribution —
also well placed, also unmoved.

The exemptions are vindicated too: `corridor` sits at p90 3.30, above the hard cap
it is exempt from, and `storage` reaches p99 3.89. Exempting them was not
generosity; without it the rule would reject the corridor in one dwelling in ten.

### 2.2 ResPlan agrees and is looser, which is the direction to expect

16,612 in-band plans. ResPlan has four classes and no corridor at all —
circulation is folded into `living`, which *"wraps every other room"* — so only
`bedroom`, `kitchen` and `bathroom` are the same quantity as the Swiss classes,
and `living` is reported apart and never pooled.

| | p50 | p90 | p95 | p99 | p99.5 | max |
|---|---:|---:|---:|---:|---:|---:|
| binding three (93,952) | 1.32 | 1.82 | 2.01 | 2.50 | 2.73 | 7.41 |
| *`living`, circulation folded in* | 1.28 | 1.88 | 2.14 | 2.72 | 2.96 | 9.99 |

At 3.0 ResPlan loses **1.05 %** of plans against Swiss's 2.85 %. Vector-traced
plans are more regular than surveyed ones — the same direction
`rectangularisation.md` §1.2 found for rectangularity (48.9 % against 62.1 %) —
so **Swiss is the conservative corpus and the one the threshold should be read
off.** It is.

### 2.3 The converted arm disagrees, and that is a conversion cost, not a bar defect

`acceptance-bar.md` §9.1 binds this rule **per part**, on the argument that *"a
bowling-alley leg is a bowling alley"* and a Room's bbox would exempt exactly the
shape the rule catches. On the converted arm, per part, eroded:

| | p50 | p90 | p95 | p99 | p99.5 | max |
|---|---:|---:|---:|---:|---:|---:|
| binding parts (13,394) | 1.44 | 2.28 | 2.76 | 4.41 | 5.26 | 56.00 |

**That `max` of 56.00 is the tell.** It is a part one cell wide — 250 − 150 = 100
mm clear — which `dim.min_clear_width` rejects long before aspect is consulted.
Measuring aspect on parts a prior hard rule has already killed double-counts the
same broken conversion. Conditioned on the dwelling first clearing
`dim.min_clear_short` (79.24 % do), the tail collapses from 56.00 to 7.36 and:

| threshold | rooms above | dwellings, governing rectangle | dwellings, any part |
|---:|---:|---:|---:|
| 2.2 | 8.14 % | 34.64 % | 36.17 % |
| **3.0** | **2.02 %** | **9.69 %** | **10.62 %** |
| 3.5 | 0.89 % | 4.41 % | 5.01 % |
| 4.0 | 0.50 % | 2.45 % | 2.56 % |

So the same threshold costs 2.85 % of real dwellings and **10.62 % of converted
ones**. The gap is not noise and it is not the bar's:

**The conversion manufactures elongation.** Split by role, unconditioned:

| part | n | p50 | p90 | p99 | above 3.0 |
|---|---:|---:|---:|---:|---:|
| single-part Room | 11,614 | 1.42 | 2.13 | 3.76 | **2.45 %** |
| main part of a two-part Room | 890 | 1.58 | 2.91 | 4.81 | 9.55 % |
| **leg of a two-part Room** | 890 | 1.68 | 3.73 | 6.38 | **19.55 %** |

A single-part Room's 2.45 % is the raw arm's 0.53 % seen through a 250 mm grid.
The elongation is in the *second* rectangle — the leg — and a leg is a fitting
artefact of representing one real polygon as two boxes, not a room anybody built.

**The decision follows from which population the rule binds.** The bar binds
engine output. The engine's Space *is* rectangles, so the per-part binding is
right and stays. But the number must be read off the population of **real
rooms**, which is the raw arm, and it is: 3.0 = p99.5 = 2.85 %.

What the converted arm measures instead is a **coverage cost on the proposer's
index**: a donor whose real room needs a 5:1 leg produces a candidate the bar
kills. That is 10.6 % of the converted corpus and it belongs to
`proposer.md`/`rectangularise/`, not here. §13 hands it over.

---

## 3. Circulation — the hard bound is right and the soft band is off-centre

Denominator per ADR 0010: the sum of **all** Space areas, circulation included —
`ümumi sahə` itself, not GIA, which v1 does not compute. Raw arm, 42,985
dwellings, circulation = `CORRIDOR` (the only circulation label the residential
subset carries; `CORRIDORS_AND_HALLS` and `LOBBY` appear zero times in it).

| | p5 | p10 | **p25** | **p50** | **p75** | p90 | p95 | p99 | p99.5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| circulation share | 0.045 | 0.067 | **0.092** | **0.122** | **0.151** | 0.188 | 0.218 | 0.284 | 0.322 |

### 3.1 `circ.fraction_hard` = 0.30 stands

| cap | 0.20 | 0.25 | 0.28 | **0.30** | 0.35 |
|---|---:|---:|---:|---:|---:|
| dwellings rejected | 7.57 % | 2.14 % | 1.10 % | **0.69 %** | 0.36 % |

Its note says it is *"an outer bound, not a quality bar… set where it only ever
catches Plans that are visibly broken."* Measured: it sits between p99 and p99.5
and costs 0.69 %. The note is now a measurement.

### 3.2 `circ.fraction_soft` moves to the corpus interquartile range

The shipped band is `[0.08, 0.18]`. It holds 71.31 % of real dwellings, but not
symmetrically — 16.55 % fall below and 12.14 % above, so the band is shifted low
against a distribution whose p50 is 0.122.

A soft band's job is to **rank**, not to hold. A band covering 71 % of the
population is close to inert on the 71 %. The interquartile range is the band
that discriminates:

**`circ.fraction_soft` → `[0.09, 0.15]`**, the corpus p25–p75, with p50 = 0.122
recorded beside it. By construction a quarter of real dwellings sit each side;
that is what makes it a gradient rather than a second bound.

### 3.3 One fact the engine cannot reproduce

**2.66 % of real dwellings have no circulation Space at all.** `resolve` invents
circulation unconditionally (C13: *"every Space including the circulation
`resolve` invents"*), so the engine can never emit one of these. Not a threshold;
handed to `brief.md`'s holder in §11.

---

## 4. `wet.plumbing_group_count` — the ticket predicted this one and it was right

> *"How many disconnected wet clusters do real dwellings have? If the tail
> reaches 3, the hard bound is wrong."*

Raw arm. A group is a maximal set of wet Spaces connected through a shared wall,
tested at the same 0.30 m wall-width tolerance `measure_swiss.contact_graph` uses,
because corpus rooms never touch.

| groups | dwellings | share | cumulative |
|---:|---:|---:|---:|
| 0 | 49 | 0.11 % | 0.11 % |
| 1 | 16,787 | 39.05 % | 39.17 % |
| **2** | **19,983** | **46.49 %** | **85.66 %** |
| **3** | **6,079** | **14.14 %** | 99.80 % |
| 4 | 87 | 0.20 % | 100.00 % |

| hard bound | ≤ 1 | **≤ 2** | **≤ 3** | ≤ 4 |
|---|---:|---:|---:|---:|
| rejects | 60.83 % | **14.34 %** | **0.20 %** | 0.00 % |

The rule's note claims *"Two is the shape real dwellings take — a front wet zone
and a rear one."* Half true: two is the **mode**, at 46.5 %. But the tail reaches
three at 14.14 %, and a hard rule that rejects one real home in seven is the bug
this ticket exists to find.

**`wet.plumbing_group_count` → 3.** It costs 0.20 %, and it still does the job the
rule was written for: it *"stays postable as a hard constraint"* and still refuses
the candidate with five isolated stacks that scoring it purely soft would admit.
The quality gradient inside the bound — `wet.shared_wall_length` — is what should
prefer two over three, and it is measured in §5.

**The measurement is conservative in the safe direction.** Contact at 0.30 m
merges groups that touch only at a corner, so the true group count is **at least**
what is reported. A tighter contact test moves 14.34 % up, never down.

---

## 5. `wet.shared_wall_length` — the soft gradient now has a distribution

Raw arm, total shared run between wet Spaces, metres:

| | p25 | p50 | p75 | p90 | p95 |
|---|---:|---:|---:|---:|---:|
| per adjacent wet pair (30,809) | 0.75 | **1.12** | 1.47 | 1.87 | 2.08 |
| per dwelling (42,985) | 0.00 | **0.57** | 1.41 | 2.07 | 2.50 |

The per-dwelling p25 of 0.00 is the 39.05 % of dwellings whose wet rooms form one
group with **no shared run at all** — they are connected through a corridor, not
a wall. So this soft term is scoring zero on nearly two dwellings in five, and
`wet.plumbing_group_count` at 3 is now the only wet-adjacency rule with teeth.
Recorded; the term keeps its shape and gains a scale.

---

## 6. `open.fits_segment` — the number is right twice, in two documents

### 6.1 What was measured

For every room's clear boundary edge and every Opening assigned to it — nearest
edge to the opening's centroid, never every edge within reach — the harness
records the opening's structural width along the run, the run's clear length, and
the gap from the opening to the nearer end. **693,976 opening incidences.**

A room's clear edge runs corner to corner, which is precisely the clear run a
WallSegment offers an Opening: the quantity `open.fits_segment` bounds, on the
face *Opening placement rules* declared (clear, not centreline).

### 6.2 The rule as written is a segment-length test, and 100 mm is safely below the tail

The statement is *"structural width plus twice the minimum jamb return does not
exceed the CLEAR length of the WallSegment."* So the fitted quantity is the
**half-slack**, `(run − width) / 2` — the largest symmetric return the placement
could have had:

| half-slack, mm | p1 | p5 | p10 | p25 | p50 |
|---|---:|---:|---:|---:|---:|
| all openings (693,976) | 11 | 65 | 121 | 371 | 763 |
| `DOOR` (467,631) | 13 | 71 | 130 | 385 | 831 |
| **`DOOR`, run ≥ 1.5 m (367,145)** | **114** | **383** | 452 | 667 | 1,071 |
| `WINDOW` (187,363) | 7 | 53 | 108 | 418 | 710 |

Unfiltered, 100 mm fails 8.27 % of openings. **75.1 % of those failures sit on a
run under 1.5 m**, where the opening is effectively the whole wall — a cased or
full-width opening, which `openings.md` models and which has no jamb by
construction. On doors sitting in an actual pier, 100 mm costs **0.92 %**, and
sits just under the p1 of 114 mm.

**`open.fits_segment` = 100 mm stands.** It is below the p1 of the slack real
construction leaves on a real run.

### 6.3 The rule does not bind the return — and it does not need to, because `openings.md` does

The predicate tests the **run's length** and says nothing about where on the run
the Opening sits. That looked like a rule named for a quantity it does not bind,
and it is not: **`docs/spec/openings.md` §3.2 fixes the return exactly**, at
100 mm at the pushed-to end, with a 300 mm nib at the leading end. The validator
guarantees the run can hold that arrangement; the placement spec puts the door
there. One quantity, two documents, and the division is deliberate — Openings are
placed after the solve, so a placement is not a postable predicate.

**So the corpus check that matters is on the placement constant, not the rule** —
and it passes:

| jamb return achieved, mm | p1 | p5 | p10 | p25 | **p50** | p90 |
|---|---:|---:|---:|---:|---:|---:|
| `DOOR` | 0 | 7 | 22 | 58 | **128** | 902 |
| `ENTRANCE_DOOR` | 0 | 10 | 27 | 64 | 114 | 490 |
| `WINDOW` | 0 | 0 | 15 | 70 | 255 | 930 |

**`openings.md` §3.2's 100 mm sits between the p25 (58 mm) and the p50 (128 mm)
of real door returns — at roughly the 40th percentile.** An engine door therefore
sits slightly tighter to its corner than a median real door and comfortably
inside the range real construction uses. The constant was invented and it is
central; that is the third Envelope-class guess in this study to survive contact
with the corpus.

41.72 % of real doors sit closer than 100 mm than the engine would place them,
and 94.19 % of real dwellings contain at least one. **None of that is a
rejection** — `open.fits_segment` is a fit test and passes every one. It is the
gap between *what real construction does* and *what the engine will do*, and it
is one-sided in the safe direction: the engine is never tighter than a real
median.

⚠️ **What does cost something is the composite.** §3.2's arrangement needs
`w + 400` of clear run whichever end the door is pushed to, and **12.32 % of real
doors sit on a run shorter than that** (§6.4). That is the number that says how
often a real dwelling's door arrangement is unreproducible, and it belongs to the
nib and the solver reservation, not to this threshold.

### 6.4 Two shipped run demands, priced on the same segments

| demand | source | real doors below it |
|---|---|---:|
| `open.leading_edge_nib`, 300 mm at the leading edge | `verified`, AD M M4(2) ¶2.22 | 12.32 % (proxy: run < w + 300) |
| `circ.potential_reachability`, run ≥ w + `t_int` + 400 | ADR 0021 | **20.49 %** |

Both are proxies measured along the run, and `open.leading_edge_nib`'s real
predicate is a clear *region* 1200 mm into the receiving Space, which a run length
cannot express — so 12.32 % is an under-count of the wall-length half and says
nothing about the depth half. Neither is this ticket's to move: the nib is
`verified` and the contact threshold is ADR 0021's. Both numbers are recorded
because **one dwelling in five has a door on a run below the contact threshold
that certifies it**, and nothing on the map had priced that.

---

## 7. `AZ.openings.min_pier_mm` = 600 — not supported, and the corpus cannot settle it alone

Handed here by *Opening placement rules* as *"the only unfitted constant
`openings.md` adds"*. Measured as the gap between consecutive openings assigned to
one run: **94,272 pairs**, of which 10,664 are window-to-window, the pair the
constant governs.

| window-to-window gap, mm | p5 | p10 | p25 | **p50** | p75 | below 600 |
|---|---:|---:|---:|---:|---:|---:|
| raw (10,664) | 0 | 26 | 93 | 242 | 807 | 65.88 % |
| mullions < 100 merged (7,644) | 112 | 128 | 202 | 489 | 1,072 | 56.29 % |
| **mullions < 150 merged (6,506)** | **164** | **192** | **286** | **621** | 1,121 | **48.65 %** |
| mullions < 200 merged (5,754) | 228 | 261 | 364 | 739 | 1,181 | 41.94 % |

**The corpus does not distinguish a mullion from a pier.** A 26 mm "pier" is a
window unit stored as two sashes. The histogram is bimodal — 4,158 of 10,664 gaps
sit under 150 mm, then a long spread from 150 to 1,200 — so the merge threshold
is a modelling choice and the fit is reported at three of them rather than as one
number.

At every merge threshold, **600 mm forbids the arrangement 42–56 % of real window
pairs use.** Recommended **250 mm**: above the mullion band at every threshold,
below the p25 of the merged distribution, and two courses of the AZ profile's own
120 mm structural leaf.

**This value lives in `data/standards/room-constraints.json`, which *The
annotation spec is US-shaped* holds.** Not written here; handed over in §13 with
the sensitivity, because a number whose value depends on a modelling choice must
arrive with the choice attached.

---

## 8. The Envelope constants — both guesses land

Handed here by *Building scope and envelope handling*. `brief.md` §5 rung 2:
`interior = Σ Room.target_area / efficiency`.

The numerator is the sum of the Brief's room targets, and **no Brief names a
corridor** (C13), so the fitted quantity is Σ(named-room areas) / interior, where
`interior` is the dwelling's floor at the inner face of the exterior wall —
recovered by a morphological closing at 150 mm, which fills every internal
partition up to 300 mm and restores the outer boundary.

| | p5 | p25 | **p50** | p75 | p95 |
|---|---:|---:|---:|---:|---:|
| **`efficiency`** (named rooms / interior) | 0.750 | 0.813 | **0.842** | 0.872 | 0.923 |
| all Spaces / interior | 0.943 | 0.953 | 0.960 | 0.968 | 0.978 |
| **default Envelope aspect** | 1.033 | 1.172 | **1.376** | 1.702 | 2.362 |
| interior / its own bbox | 0.635 | 0.755 | 0.826 | 0.897 | 0.984 |

**`efficiency` = 0.85 → 0.84.** The guess was 0.9 % high.
**Default Envelope aspect = 1.35 → 1.38.** The guess was 1.9 % low.

Neither moves anything downstream materially, and that is the finding: two
constants invented to let the Envelope be derived at all were within 2 % of the
corpus.

### 8.1 The third item on that handoff is already discharged

*"The exposure mix… derivable from Swiss Dwellings' own building hierarchy"* was
**paid in full by *The exposure presets were fitted to a measurement of one
room***, which measured the ring-shape vector nobody had ever measured:
four-sided 63.3 %, three-sided 26.0 %, adjacent pair 4.6 %, opposite pair 3.8 %,
single 2.2 % — and found that the three flat presets name **10.6 %** of the corpus
between them. Not re-derived here.

### 8.2 The partition footprint corroborates ticket 44 rather than contradicting it

This study measures the partition footprint **geometrically**, from the corpus's
own wall gaps: p50 **4.00 %** of interior, which is 4.17 % of Σ Space area.
*The partition footprint has a mean and no spread* computed **5.75 %** of Σ Space
area at the shipped `t_int` of 150.

The two agree once the plane is named. The corpus's own p50 wall gap is 99 mm
(`probe_swiss.py`), not 150. 99/150 = 0.66; 4.17/5.75 = 0.725. **`f = 0.0575` is
the right number for a plan built at 150 mm**, which is what `brief.md` §5 rung 1
sizes, and this measurement is an independent check of it from a different
direction, not a competing value. `brief.md` is unchanged on that rung.

---

## 9. `area.invented_envelope_*` — decided against the grid, because the solver spread does not exist

The ticket says this pair is *"not corpus-measurable — it is a product tolerance.
Decide it against the solver's observed GIA spread instead."* **There is no
published solver GIA spread**: `solver-formulation.md` reports timing and
objective spreads and never an area one.

There is a better denominator, and it is the one that dominates. `model.no_unassigned_area`
is **hard**: Σ Space + wall bodies = the Envelope interior, exactly. So on the
invented-Envelope path the drift of Σ Space from `target_area` is not the solver's
packing freedom — that is closed by construction — it is **what the 250 mm grid
does to an area when every room dimension must land on it.**

Measured: re-express every real room at its own proportions with both dimensions
rounded to 250 mm, and compare Σ area:

| |rel err| on Σ Space area | p50 | p75 | p90 | p95 | p99 |
|---|---:|---:|---:|---:|---:|
| 250 mm grid alone | 0.0090 | 0.0155 | 0.0221 | 0.0264 | 0.0357 |

| exceeds | 2 % | 3 % | 5 % |
|---|---:|---:|---:|
| share of dwellings | **13.71 %** | 2.85 % | **0.10 %** |

- **`area.invented_envelope_hard` = 5 % stands.** The grid alone crosses it in one
  dwelling in a thousand, so 5 % is a real tolerance with room left for the
  solver on top. It is 1.9× the p95 of the grid residual.
- **`area.invented_envelope_soft` = 2 % → 3 %.** At 2 % the grid alone misses the
  target in **13.71 %** of dwellings. A soft preference the engine cannot meet for
  reasons unconnected to design is a constant term in the objective, not a
  gradient. 3 % costs 2.85 % — the same tolerance every other fitted number in
  this study lands on.

---

## 10. A regression found in passing, and repaired at its authoring site

`ergonomic.rooms.kitchen.needs_window` is **`false`** in the shipped standards
file. It should be `true`, and the map, the Envelope row, `acceptance-bar.md` §7
and two open tickets all assume it is.

| commit | ticket | value |
|---|---|---|
| `db69376` | *Two room vocabularies in one file* | `false` |
| `6019015` | *Opening placement rules* | **`true`** — set deliberately: AzDTN 2.7-2 cl. 9.12 is `verified` and mandatory for living rooms *and* kitchens |
| `e8ce199` | *A dwelling with no toilet passes every check* | **`false`** — reverted, silently |

**Cause.** `needs_window` is in `build_ergonomic_layer.py`'s `AUTHORED_ROOM` set,
so the generator re-authors it from its own `FLAGS` table on every run — and that
table still said `False`, with a comment citing BayBO Art. 46(1), a source the
same file elsewhere records as *"nothing cites `de_baybo` now."* *A dwelling with
no toilet passes every check* taught the generator to carry forward what it does
not author; it cannot carry forward a field the generator **does** author. So the
fix that closed the drift for five fields could not close it for this one.

**What it falsifies while it stands `false`:**

- `win.habitable_has_window`'s **43.3 %** corpus cost, *"23.0 points of it the
  kitchen alone"* — measured with the kitchen inside the rule, against a file
  that puts it outside.
- The **retirement of `win.kitchen_windowless`** as unreachable. It was retired
  because *"the kitchen took its window"*; with the flag `false` it is reachable
  again, and a retired rule that can fire is a hole in the bar.
- The Envelope row's *"H8 now has one more room competing for frontage"*.

**Repaired here, at the authoring site**, so a re-run reproduces it:
`FLAGS["kitchen"]` → `needs_window: True`, with the AzDTN reason in place of the
BayBO one and the regression recorded in the comment. Regenerating changes
**exactly one field** in `room-constraints.json` and nothing else; all 238
`gate_check.py` gates and all 28 `env_check.py` gates pass after it.

This is a repair of a decision already taken and published, not a new decision,
which is why it was taken rather than handed on. §13 hands on what it changes.

---

## 11. The registry against real dwellings, and the conjunction

The ticket's second instruction. Raw arm, 42,985 dwellings; a dwelling is
rejected by a rule if **any** Space in it fails.

| rule | rejects | note |
|---|---:|---|
| `prog.storage_exists` *(warn)* | 74.52 % | reproduces ADR 0022's 73.35 %, which is why it ships `warn` |
| **`open.fits_segment`** (as written, 100 mm) | **59.54 %** | §6.2: 75 % of it is full-width openings on sub-1.5 m runs |
| **`win.habitable_has_window`** | **45.19 %** | reproduces *H8 and the single-aspect flat*'s 43.3 % independently |
| **`wet.plumbing_group_count`** ≤ 2 | **14.34 %** | §4 — moves to 3 |
| `entry.single_primary` (> 1 exterior door) | 12.76 % | §11.1 |
| `dim.max_area` (`absolute_cap`) | 3.11 % | reproduces *What a room's area is allowed to be*'s **3.1 %** |
| `prog.kitchen_exists` | 3.08 % | looser test than ADR 0022's 5.99 % — no `taxça-mətbəx` type here |
| `dim.min_clear_short` *(lower bound)* | 2.86 % | bbox short side over-states clear width, so this is a floor |
| **`dim.aspect_ratio_hard`** | **2.85 %** | §2 — stands |
| `entry.exists` | 2.83 % | dwellings with no `ENTRANCE_DOOR` polygon; a corpus gap, not homes without doors |
| `dim.corridor_min_width` | 0.76 % | `verified`, and cheap |
| **`circ.fraction_hard`** | **0.69 %** | §3.1 — stands |
| `prog.wc_exists` | 0.24 % | looser than ADR 0022's 5.19 % — `bathroom` OR `wc`, no combined-unit split |
| `dim.min_area` | 0.19 % | the ergonomic floor is genuinely a floor |

**The bar as shipped rejects 84.41 % of real, built Swiss dwellings. 15.59 %
survive.** Under this ticket's fitted values it rejects **82.31 %** — the 2.1
points are `wet.plumbing_group_count` moving to 3, and nothing else this ticket
touched moves it at all.

⚠️ **And 21 points of the remainder are a measurement artefact of the same rule,
not a property of the bar.** `open.fits_segment` contributes 59.54 % across every
run, but only **19.91 %** when restricted to doors sitting in an actual pier —
the rest are full-width openings whose "failure" is that they have no jamb by
construction (§6.2). On that reading the bar rejects **61.23 %** and **38.77 %
survive.** Both numbers are true of different questions: 82.31 % is what a
validator handed these polygons verbatim would do, and 61.23 % is what it would
do to a dwelling whose cased openings had been modelled as cased openings. The
engine emits the second kind.

Leave-one-out, which is the number that says where to look:

| removing | leaves the bar rejecting | that rule alone adds |
|---|---:|---:|
| `open.fits_segment` | 57.88 % | **26.53 %** |
| `win.habitable_has_window` | 68.44 % | **15.97 %** |
| `wet.plumbing_group_count` | 82.30 % | 2.12 % |
| `dim.max_area` | 84.09 % | 0.32 % |
| `dim.aspect_ratio_hard` | 84.25 % | 0.17 % |
| every other hard rule | ≥ 84.30 % | ≤ 0.11 % |

**Eleven of the thirteen hard rules cost less than a third of a point between
them.** The bar is two rules and a rounding error, and neither of the two is a
threshold this ticket can move: one is a fit test whose 100 mm is right (§6.2) and
one is a `verified` topology rule with **no threshold at all** (*H8*'s finding,
restated: `win.habitable_has_window` *"carries no threshold to move"*).

**What that means for C6.** *Generate many, reject most, show survivors* is sound;
this is not a 99 %-rejection bug in any single rule. But it does say that a
retrieval-and-warp candidate drawn from this corpus has somewhere between a
**one in six** and a **two in five** prior of clearing the bar before the solver
improves anything — the range is the cased-opening question above, not
uncertainty about the rules — and that the two rules setting that prior are both
about **openings and windows**, the layer placed *after* the solve. §13 hands
that to the proposer.

### 11.1 `entry.single_primary`

12.76 % of real dwellings carry more than one `ENTRANCE_DOOR` polygon (11.57 %
carry two). The rule's note already says *"one by default, more allowed"* for a
house and *exactly one* for a flat, on the reasoning that a second exterior door
in a flat's Brief is an error rather than a layout choice. The corpus does not
refute that — a Swiss `ENTRANCE_DOOR` may mark a service door onto the same common
corridor — so the rule does not move. Recorded because nothing had priced it.

### 11.2 Sensitivity

Reading `room*` as `bedroom_single` (the loosest bedroom floor, 2.2 m² against
3.1) instead of `bedroom_double` moves `dim.min_area` from 0.19 % to 0.19 %. The
ergonomic floor is far enough below real practice that which bedroom the corpus
room is does not matter.

---

## 12. What ships

| key | was | **is** | src | cost |
|---|---|---|---|---|
| `dim.aspect_ratio_hard` | 3.0 | **3.0** | `swiss_dwellings_p99_5` | 2.85 % |
| `dim.aspect_ratio_soft` | 2.2 | **2.2** | `swiss_dwellings_p95` | — |
| `circ.fraction_soft` | [0.08, 0.18] | **[0.09, 0.15]** | `swiss_dwellings_p25_p75` | — |
| `circ.fraction_hard` | 0.30 | **0.30** | `swiss_dwellings_p99_p99_5` | 0.69 % |
| `wet.plumbing_group_count` | 2 | **3** | `swiss_dwellings_p99_8` | 0.20 % |
| `open.fits_segment` | 100 mm | **100 mm** | `swiss_dwellings_half_slack_p1` | 0.92 % |
| `area.invented_envelope_hard` | 5 % | **5 %** | `grid_residual_250mm` | 0.10 % |
| `area.invented_envelope_soft` | 2 % | **3 %** | `grid_residual_250mm` | 2.85 % |
| `efficiency` (`brief.md` §5 rung 2) | ~0.85 | **0.84** | `swiss_dwellings_p50` | — |
| default Envelope aspect | ~1.35 | **1.38** | `swiss_dwellings_p50` | — |
| `AZ.openings.min_pier_mm` | 600 | **250**, recommended | `swiss_dwellings_p25_mullions_merged` | §7 |

Plus the three rules *What a room's area is allowed to be* measured and this
ticket transcribes without re-deriving: `dim.max_area` (new, hard, `both`),
`dim.stated_target_implausible` (new, warn), and `dim.market_default_area` made
two-sided with the measured `soft_w`.

### 12.1 `conf` needed a fourth value and now has one

The deliverable says *"`conf` upgraded where the corpus supports it"*, and the
vocabulary had nowhere to put it. `verified` means read from a primary document;
`derived` means computed from a verified value; `engine_choice` means **nobody
sourced it and the engine picked it.** A number fitted to 42,985 real dwellings is
none of those, and leaving it `engine_choice` conflates *invented* with
*measured* — which is precisely the distinction this ticket exists to create.

**`fitted` is added to `rules.json`'s `conf` vocabulary**: *no source dictates
this; its value is a named statistic of a named corpus, and `src` says which.*
Nine rules move `engine_choice → fitted`, taking `rules.json` from **eighteen**
unsourced numbers to **nine**.

> ⚠️ **The map says nineteen and the file says eighteen.** Two rules were retired
> by *H8 and the single-aspect flat* after this ticket was written. The count to
> quote is eighteen before this ticket and nine after.

`data/standards/room-constraints.json` needs the same fourth value when
`min_pier_mm` lands. Handed over in §13 rather than written, because that file has
a claimant.

---

## 13. What this hands to other tickets

| obligation | to |
|---|---|
| **`AZ.openings.min_pier_mm` 600 → 250**, with the three-threshold mullion sensitivity (§7), and `value_format.conf_meanings` gains `fitted` to hold it | *The annotation spec is US-shaped* — holds `room-constraints.json` |
| **`kitchen.needs_window` was reverted and is repaired** (§10). What still needs deciding: `win.kitchen_windowless` was retired as unreachable on the flag being `true` — that retirement is now correct again, but nothing tested it while the flag was `false`. The `retired` block's justification should cite the flag, not the ticket | *A statutory floor, posted soft* — holds `acceptance-bar.md` and `rules.json` |
| **The bar is two rules and a rounding error** (§11): 84.41 % rejection, of which `open.fits_segment` contributes 26.53 points and `win.habitable_has_window` 15.97. Both are opening-layer rules, placed after the solve, so a candidate's prior of clearing the bar is set by a layer the Proposal does not carry | *A third of real kitchens have no window* and *A donor's enclosed void becomes area nobody asked for* — both hold `proposer.md` |
| **The conversion manufactures elongation** (§2.3): 19.55 % of two-part legs exceed aspect 3.0 against 2.45 % of single-part Rooms, so 10.62 % of converted dwellings carry a part the bar rejects while only 2.85 % of real ones do. This is index coverage, not a bar defect | *The dwelling that is built on two angles* and *The two-notch cap is now evidenced* — hold `rectangularise/` |
| **`openings.md` §3.2's 100 mm jamb return is now measured and central** (§6.3) — it sits at roughly the p40 of real door returns (p25 58 mm, p50 128 mm), so an engine door is never tighter to its corner than a real median. Nothing to change; recorded so it is not re-litigated | `docs/spec/openings.md` — **no claimant** |
| **One door in five sits on a run below ADR 0021's contact threshold** (§6.4), and 12.32 % below the leading-edge nib's wall-length half. Neither number is this ticket's to act on | *What an ordered entry sequence costs the solver* — holds `solver-toy/`; and ADR 0021's holder |
| **2.66 % of real dwellings have no circulation Space at all** (§3.3), and `resolve` invents one unconditionally, so the engine cannot emit them | whoever next holds `brief.md` — no claimant |
| **`wet.shared_wall_length` scores zero on 39 % of dwellings** (§5): their wet rooms connect through a corridor, not a wall. With the group bound at 3, this soft term is the only thing preferring two zones over three, and it is silent on two dwellings in five | whoever next holds `rules.json` |
| **`prog.kitchen_exists` and `prog.wc_exists` reproduce at 3.08 % and 0.24 %** against ADR 0022's 5.99 % and 5.19 %. The gap is the vocabulary, not the corpus: this study has no `taxça-mətbəx` and no `bathroom_combined` split. Not a contradiction; a floor | *A statutory floor, posted soft* |

---

## 14. Harness

`experiments/acceptance-thresholds/`. Corpora come from `data/corpora/`, which is
gitignored; outputs go to `out/`, also gitignored. Regenerate by running the
scripts in this order.

| script | what it does | runtime |
|---|---|---|
| `census.py [n]` | one pass over all 42,985 in-band Swiss dwellings: per-room area and bbox, wet grouping, envelope closing, jamb returns, piers, entrance doors | ~13 min |
| `parts.py` | the same aspect question on the converted arm, per part, eroded | seconds |
| `resplan_aspect.py` | the aspect question on the second corpus | ~2 min |
| `fit.py` | every threshold's distribution and its cost curve | seconds |
| `reject.py` | the full hard registry against real dwellings, per rule and as a conjunction | seconds |

`census.py` is the only expensive step and everything else reads its output, so a
new statistic off this study costs seconds. **If you add one, add its inputs to
`census.py`'s record** — the same rule `thickness-fidelity/` carries.

### Two things that will bite whoever runs this next

**Do not erode the raw arm.** Swiss room polygons are already clear (§1.1).
`parts.py` is the only script here that erodes, and it must.

**An Opening belongs to one edge.** The first version assigned every opening to
every boundary edge within reach, which double-counts a door near a corner onto
the perpendicular wall and manufactures near-zero jamb returns. `jamb_returns`
assigns by nearest-centroid-to-segment and nothing else. The `min_pier_mm`
measurement inherits that assignment, so a change there moves §7.
