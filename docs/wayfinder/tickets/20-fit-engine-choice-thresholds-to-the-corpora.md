---
id: 20
title: Fit the ENGINE_CHOICE acceptance thresholds to the corpora
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
blocked_by: [12, 19]
writes:
  - data/acceptance/rules.json
  - docs/research/acceptance-thresholds.md
  - docs/adr/0023-a-measured-threshold-is-not-an-engine-choice.md
  - experiments/acceptance-thresholds/
  - docs/spec/brief.md            # declared on resolution: 5 rung 2 and two 12 rows
  - experiments/region-profile/build_ergonomic_layer.py   # declared: a regression repair
  - data/standards/room-constraints.json                  # one field, via the generator
---

# Fit the ENGINE_CHOICE acceptance thresholds to the corpora

## Question

*Acceptance validator spec* shipped 19 of 37 rules with `conf: engine_choice` —
no source dictates them, and for several **no source in the surveyed corpus
supplies a number at all**. They were set by judgement so that v1 could ship a
bar rather than wait for one. Now measure them.

The corpora make this cheap: Swiss Dwellings and ResPlan are real, built plans.
Every threshold below is a distribution question about plans that people actually
live in.

Fit, and report the distribution alongside the chosen value:

| Rule | Placeholder | Question |
|---|---|---|
| `circ.fraction_soft` | 8–18% of GIA | C6 item 7's "sane fraction". No surveyed source gives one. What is the real distribution of circulation share? |
| `circ.fraction_hard` | ≤30% | Where does the tail actually stop? |
| `dim.aspect_ratio_hard` | ≤3.0 | What is the worst aspect ratio a real habitable room has? A hard bound below the observed maximum rejects real homes. |
| `dim.aspect_ratio_soft` | ≤2.2 | Is the mode where we guessed? |
| `wet.plumbing_group_count` | ≤2 | How many disconnected wet clusters do real dwellings have? If the tail reaches 3, the hard bound is wrong. |
| `open.fits_segment` | 100 mm jamb return | No source gives a minimum return. Measurable from plans that carry wall and opening geometry. |
| `area.invented_envelope_hard` | 5% | Not corpus-measurable — it is a product tolerance. Decide it against the solver's observed GIA spread instead. |

Two rules that matter more than their numbers:

- **`dim.aspect_ratio_hard` is the one rule in the spec with no precedent
  anywhere.** It was added because nothing in C6 catches a room that satisfies its
  minimum area and minimum width by being long. If the corpus shows real rooms
  above 3.0, the rule is wrong in a way that rejects good plans — the ticket's own
  failure mode. Check it first.
- **Every hard `engine_choice` threshold is a candidate 99%-rejection bug.** Run
  the full registry against the corpora *as plans* and report the per-rule
  rejection rate. Any hard rule rejecting a large share of real, built dwellings is
  a bug in the rule, not a quality bar.

Blocked on *Acquire the datasets*, and on *Ergonomic minima and the constraint
table's missing half* — without the ergonomic layer, `dim.min_*` cannot be
evaluated and the rejection-rate measurement is incomplete.

Deliverable: measured distributions, revised values in
`data/acceptance/rules.json` with `conf` upgraded where the corpus supports it,
and the per-rule rejection rate against real dwellings.

---

## Added by *Building scope and envelope handling*, now closed

Two more constants land here, both shipping as `ENGINE_CHOICE` with no source:

- **`efficiency`** in `envelope_clear_area = sum(room target areas) / efficiency`,
  the factor absorbing circulation and internal wall footprint when a Homeowner
  states no area at all. Shipping at ~0.85. Swiss Dwellings has the geometry to fit
  it directly.
- **The default Envelope aspect ratio** applied to that area to get a rectangle.
  Shipping at ~1.35.

And one distribution worth fitting rather than guessing:

- **The exposure mix.** Swiss Dwellings is the one corpus with a building
  hierarchy, so which edges of an apartment abut a neighbour is **derivable from
  its own data**. That gives a real distribution over the dwelling-type presets
  (`flat_single_aspect`, `flat_corner`, `flat_dual_aspect`) instead of an invented
  one, and it tells *Solver timing variance sweep* which exposure case is typical
  rather than merely possible. Confirm the hierarchy survives extraction on
  *Acquire the datasets* first.

## Two obligations from *Rectangularising real rooms*

**Fit against the converted corpus, and erode before you compare.** A corpus
dwelling is now a rectangular tiling produced by a CP-SAT fit (ADR 0008), and its
rectangles are **centreline** rectangles: the conversion splits each wall at its
axis, so a converted room's area includes half of every wall around it. Per
ADR 0001 the clear rectangle is that eroded by `t_int/2`. **Every threshold here
is stated in clear dimensions** (*Acceptance validator spec*: the hard floor is
the ergonomic minimum, which is a clear number), so fitting against unroded
rectangles makes every fitted minimum generous by `t_int` per axis — and by
ADR 0007's arithmetic that is exactly the error that deletes 4-, 5- and 6-room
dwellings.

**The population you are fitting to is not the corpus.** The conversion drops
**31 % of Swiss Dwellings and 40 % of ResPlan**, and it drops them
non-uniformly — 83 % of 4-room dwellings convert against 46 % of 10-room. A
threshold fitted to the surviving population is fitted to a corpus that is
**biased toward the small and the simple**, because what fails to convert is
disproportionately the dwelling whose arrangement a rectangle model cannot hold.
Say which population each fitted number came from. Fitting against the *raw*
polygons is also available and is the right choice for any predicate that is
well-defined on a polygon (area, aspect via bbox); it is not available for
anything that needs a tiling.

Also relevant: *Acquire the datasets* §6 flagged that geometric validity was
unmeasured and this ticket would hit it first. Partly discharged — 46 invalid
polygons in 296,653 were repaired by `make_valid`, none dropped
(`experiments/rectangularise/measure_swiss.py`).

---

## Handed here by *What a room's area is allowed to be* (2026-08-22)

**A new rule, not a threshold fit — but it lands in this file and this ticket
holds it.** Full measurement and reasoning: `docs/research/room-area-bands.md`
§6. Harness: `experiments/room-area-bands/`. Do not re-derive any of it.

1. **`dim.max_area`** — new, **hard**, site **`both`**. Bound is
   `k[type] x Room.target_area`, falling back to `absolute_cap[type]` where the
   Room has no target at all. Table in §6.1. The solver side is **free**: H4
   already builds `a = w*h` via `AddMultiplicationEquality` for the minimum, and
   an upper bound on a product tightens propagation on `w` and `h` rather than
   weakening it.
2. **`dim.market_default_area` must become two-sided.** It is soft and prefers
   Spaces *at or above* market default, so the objective **actively rewards
   bloat** while `model.no_unassigned_area` makes the surplus compulsory. A
   maximum alone relocates the bloat to just under the cap. Replace the reward
   with `soft_w[type] x |area - target|`; `soft_w` is measured, §3.1.
3. **`dim.stated_target_implausible`** — new, **warn**, when a *stated* target
   exceeds `absolute_cap[type]`. Keeps the Homeowner sovereign; catches an LLM
   decimal slip.

**Two cautions that change the numbers, not just the confidence.**

- The caps are the corpus **p99.5** and the percentile is not free: p95 rejects
  **26.6 %** of real dwellings, p99 **6.0 %**, p99.5 **3.1 %**. This corpus is the
  retrieval and training population, so a rejection here is coverage lost.
  p99.5 is also the percentile at which the 4-room case stops being
  inexpressible (§5.1) — chosen twice, independently.
- **Every number is Swiss and the profile is `AZ`.** Third instance of C14's
  `RegionProfile` / `CorpusProvenance` mismatch, disclosed per value as
  `src: swiss_dwellings_p99_5`. A maximum is **not** region-free the way
  `dim.min_area` is: the ergonomic floor is region-free because a body is a body,
  and a maximum is a market fact with no such defence.

⚠️ **`circ.fraction_hard`'s 30 % is now cross-checked from a second direction.**
Corridor share of Σ Space area measures p50 **0.11**, p95 **0.20**, p99 **0.26**
on 42,986 Swiss dwellings, so 30 % does sit past the tail as its note claims.
But corridor is also the **second-largest absorber** (+4.00 m² per 40 m² of
dwelling), so tightening it moves slack into the living room. Fit the two
together, not separately.

---

## Handed here by *Re-measure the conversion at two rectangles per Room* (2026-08-25)

**Your "the population you are fitting to is not the corpus" section is right in
principle and its numbers are now stale — in your favour.** ADR
[0016](../../adr/0016-the-conversion-names-its-own-ls.md),
`docs/research/rectangularisation.md` §11.

The conversion drop is **9.74 % of Swiss and 6.40 % of ResPlan**, not 31 % and
40 %. More to your point, **the non-uniformity you warn about is mostly gone**:
*"83 % of 4-room dwellings convert against 46 % of 10-room"* becomes **94.8 % and
82.6 %**, and the spread across C13's band goes from 35 points to 12. The
surviving population is far less **biased toward the small and the simple** than
when you were written — the dropped set's median size gap narrows from
6-versus-8 rooms to 7-versus-8.

⚠️ **The bias is narrower, not absent, and its composition changed.** What is
still dropped is **storeroom-heavy (1.57×) and bedroom-heavy (1.25×)** — but the
`LIVING_DINING` over-representation is **gone** (1.37× → 1.02×). So a threshold
fitted on survivors now under-represents *the flat with several small ancillary
rooms*, not *the flat with a wrapped open-plan living room*. If any predicate you
fit is sensitive to store or bedroom geometry, that is the direction of the
residual error.

**Your instruction stands unchanged, and it is the right one**: say which
population each fitted number came from, and prefer the raw polygons for any
predicate well-defined on a polygon. Use `out/swiss_fit_k2.json` —
⚠️ **its records carry `parts` (a list of rectangles per Room) and no `rects`
key**, so a per-Room rectangle no longer exists for 9.85 % of rooms. For a
predicate that binds **per constituent rectangle** (ADR 0014 binds minimum clear
dimensions and aspect that way, and area per Room), that distinction is not
cosmetic.

✅ **One thing you were owed is discharged**: the room-type labels in the fitted
files are correct now — `load_swiss_geoms` collects them from the filtered
polygon list, fixing the 1.23 % off-by-one that *Look at the converted corpus*
found. The original `out/swiss_fit.json` still has it; regenerate rather than
repair.

---

## Resolution (2026-08-26)

**Measured, all of it.** Full findings: `docs/research/acceptance-thresholds.md`.
Decision: [ADR 0023](../../adr/0023-a-measured-threshold-is-not-an-engine-choice.md).
Harness: `experiments/acceptance-thresholds/`, five scripts over **42,985** real
Swiss dwellings and **16,612** ResPlan plans. Do not re-derive any of it.

### Two thresholds move, seven guesses hold, and the vocabulary was the real blocker

| rule | was | is | cost | why |
|---|---|---|---:|---|
| `wet.plumbing_group_count` | 2 | **3** | 0.20 % | **this ticket's own prediction came true.** 3 groups = **14.14 %** of real dwellings, so the bound at 2 rejected one real home in seven |
| `area.invented_envelope_soft` | 2 % | **3 %** | 2.85 % | the **250 mm grid alone** misses a 2 % target in **13.71 %** of dwellings |
| `circ.fraction_soft` | [0.08, 0.18] | **[0.09, 0.15]** | — | the old band held 71.31 % and held it asymmetrically. A soft band exists to rank; fitted to the corpus IQR |
| `dim.aspect_ratio_hard` | 3.0 | **3.0** | 2.85 % | it **is** the p99.5, at 3.02 |
| `dim.aspect_ratio_soft` | 2.2 | **2.2** | — | it is the p95, at 2.14 |
| `circ.fraction_hard` | 0.30 | **0.30** | 0.69 % | p99 0.284, p99.5 0.322 — inside the tail exactly as its note claimed |
| `open.fits_segment` | 100 mm | **100 mm** | 0.92 % | below the p1 (114 mm) of real half-slack — and the same 100 mm, used by `openings.md` §3.2 to *place* the door, is the **p40** of real returns |
| `area.invented_envelope_hard` | 5 % | **5 %** | 0.10 % | 1.9x the p95 of the grid residual |
| `efficiency` | ~0.85 | **0.84** | — | p50 **0.8423**. The guess was 0.9 % high |
| default Envelope aspect | ~1.35 | **1.38** | — | p50 **1.376**. The guess was 1.9 % low |
| `AZ.openings.min_pier_mm` | 600 | **250**, recommended | — | 600 forbids what 42–56 % of real window pairs do. **Handed to 32**, not written |

**`conf` had nowhere to put a measured number, and that was the actual gap.**
`verified` means read from a document, `derived` means computed from one,
`engine_choice` means *the engine picked it*. Fitting a threshold to 42,985 real
dwellings left it marked identically to a guess — so the map's own headline
metric could never move however much measurement was done. **ADR 0023 adds
`fitted`**, and `engine_choice` narrows from *unsourced* to **unmeasured**.

**`data/acceptance/rules.json`: 40 → 42 rules, ENGINE_CHOICE 18 → 9.**

- **Nine rules move to `conf: fitted`**, each carrying `src` (the statistic, e.g.
  `swiss_dwellings_p99_5`), `corpus_cost` (the share of real dwellings it
  rejects) and `fitted_by`.
- **Two rules added, both transcribed from *What a room's area is allowed to be*
  and neither re-derived**: `dim.max_area` (hard, site `both`) and
  `dim.stated_target_implausible` (warn, scope `brief`).
- **`dim.market_default_area` made two-sided** — it rewarded bloat while
  `model.no_unassigned_area` made the surplus compulsory.
- New blocks: `area_bands` (the `k` / `absolute_cap` / `soft_w` table),
  `envelope_constants` (`efficiency`, default aspect, the exposure mix as
  discharged, and a partition-footprint cross-check),
  `rule_format.conf_meanings`, `rule_count`, `conformance.subset_size`, and an
  **`owed`** block.
- ⚠️ **The `site: both` conformance subset moves 14 → 15**, because
  `dim.max_area` is `both` and its solver side is free. *A dwelling with no
  toilet passes every check* said the subset *"cannot grow here"*; that bound its
  own programme rules, which are `scope: brief` and have no plan-side twin. It
  was not a bar on the subset ever growing.

### ⚠️ The map says nineteen ENGINE_CHOICE; the file said eighteen

*H8 and the single-aspect flat* retired two rules after the count was written.
The count to quote is **eighteen before this ticket and nine after**, and the
nine are not a measurement gap: four `model.*` integrity rules,
`circ.dependent_room_host`, `entry.exists`, `entry.single_primary`,
`dim.market_default_area`'s penalty *shape*, and `wet.shared_wall_length` — every
one a predicate about shape or program rather than a magnitude. **There is
nothing left here to measure.**

### ⚠️ A regression, found in passing and repaired at its authoring site

`ergonomic.rooms.kitchen.needs_window` was **`false`** in the shipped standards
file. *Opening placement rules* set it `true` deliberately (`6019015`) — AzDTN
2.7-2 cl. 9.12 is `verified` and mandatory for living rooms *and* kitchens — and
*A dwelling with no toilet passes every check* (`e8ce199`) **reverted it
silently**, by re-running `build_ergonomic_layer.py`.

**Cause:** `needs_window` is in the generator's `AUTHORED_ROOM` set, so it is
re-authored from a `FLAGS` table that still said `False`, with a comment citing
BayBO — a source the same file elsewhere records as uncited. 42 taught the
generator to carry forward what it does **not** author; it cannot carry forward a
field the generator **does** author, so the fix that closed the drift for five
fields could not close it for this one.

**What it falsified while it stood:** `win.habitable_has_window`'s **43.3 %**
corpus cost and its *"23.0 points the kitchen alone"*; the **retirement of
`win.kitchen_windowless`** as unreachable, which becomes reachable the moment the
flag is `false`; and the Envelope row's *"one more room competing for frontage"*.

Repaired in `FLAGS`, with the AzDTN reason replacing the BayBO one and the
regression recorded in the comment so a re-run reproduces the fix. Regenerating
changes **exactly one field** and nothing else; **238/238** `gate_check.py` gates
and **28/28** `env_check.py` gates pass after it. This is a repair of a decision
already taken and published, which is why it was taken rather than handed on.

### The headline nobody had measured: the bar rejects 84.41 % of real dwellings

Full hard registry against 42,985 real, built Swiss dwellings. **15.59 %
survive** as shipped; **17.69 %** after this ticket's moves, the 2.1 points being
`wet.plumbing_group_count`.

⚠️ **21 of the remaining points are an artefact of one rule's reading, not the
bar.** `open.fits_segment` contributes 59.54 % across every run and **19.91 %**
on doors in an actual pier; the rest are full-width openings with no jamb by
construction. On that reading the bar rejects **61.23 %** and **38.77 %
survive** — and the engine emits cased openings as cased openings, so 38.77 % is
the number that describes engine output.

Leave-one-out says where to look:

| removing | that rule alone adds |
|---|---:|
| `open.fits_segment` (as written) | **26.53 %** |
| `win.habitable_has_window` | **15.97 %** |
| `wet.plumbing_group_count` | 2.12 % |
| **every other hard rule, together** | **< 0.4 %** |

**Eleven of thirteen hard rules cost less than a third of a point between them.
The bar is two rules and a rounding error** — and neither is a threshold this
ticket can move: one is a fit test whose 100 mm is right, one is a `verified`
topology rule with no number at all. **This is not a 99 %-rejection bug in any
single rule**, which is what the ticket was written to find; it is a statement
about the *conjunction*, and both rules that carry it are about the **opening
layer, placed after the solve** — the layer the Proposal does not carry.

`dim.max_area` reproduces *What a room's area is allowed to be* independently at
**3.11 %** against its 3.1 %; `win.habitable_has_window` reproduces *H8*'s 43.3 %
at **45.19 %**; `prog.storage_exists` reproduces ADR 0022's 73.35 % at
**74.52 %**.

### ✅ One constant, two documents, and both readings of it hold

`open.fits_segment` tests the **run's length** and binds no return — and it does
not need to, because **`openings.md` §3.2 fixes the return exactly, at the same
100 mm**. The split is deliberate: Openings are placed after the solve, so a
placement is not a postable predicate.

The corpus vindicates both halves. As a fit test, 100 mm is below the **p1**
(114 mm) of real half-slack. As a *placement* constant it sits at roughly the
**p40** of real door returns (p25 58 mm, p50 128 mm) — so an engine door is never
tighter to its corner than a median real one.

⚠️ **What does cost something is the composite.** §3.2 needs `w + 400` of clear
run whichever end the door is pushed to, and **12.32 %** of real doors sit on a
run shorter than that. That number belongs to `open.leading_edge_nib` and the
solver reservation, not to this threshold.

### ⚠️ The conversion manufactures elongation, and it is not the bar's to fix

Same threshold, two populations: **2.85 %** of real dwellings carry a room above
aspect 3.0, against **10.62 %** of converted ones. Split by role, the cause is
unambiguous — **19.55 %** of two-part *legs* exceed 3.0 against **2.45 %** of
single-part Rooms. A leg is a fitting artefact of representing one real polygon
as two boxes, not a room anybody built. The threshold is read off real rooms, as
ADR 0023 §2 now requires; the 10.6 % is **index coverage lost to the proposer**.

### Three claims in this ticket's own body, checked

- ✅ *"erode before you compare"* — **right, and it applies to the converted arm
  only.** Swiss room polygons are already **clear**; eroding them would take a
  clear number to a clear number minus a wall.
- ✅ *"the population you are fitting to is not the corpus"* — the raw arm makes
  it moot for every predicate except `dim.min_clear_*`, which is the one place
  the converted arm is used, and it says so.
- ✅ *"geometric validity was unmeasured and this ticket would hit it first"* —
  **zero repairs** over all 42,985 dwellings on this pass.

### Not re-derived, deliberately

The **exposure mix** was paid in full by *The exposure presets were fitted to a
measurement of one room* — four-sided 63.3 %, three-sided 26.0 %, adjacent pair
4.6 %, opposite pair 3.8 %, single 2.2 %, with the three flat presets naming
10.6 % of the corpus between them. Recorded in
`envelope_constants.exposure_mix` so nobody measures it twice.

### The partition footprint corroborates ticket 44 rather than competing with it

Measured a second time and by a different method — geometrically, from the
corpus's own wall gaps — at **4.17 %** of Σ Space area against *The partition
footprint has a mean and no spread*'s **5.75 %**. The two agree once the plane is
named: the corpus's own p50 wall gap is **99 mm**, not the shipped 150, and
99/150 = 0.66 against 4.17/5.75 = 0.725. **`f = 0.0575` is the right number for a
plan built at 150 mm**, which is what `brief.md` §5 rung 1 sizes. Rung 1
unchanged.

### Declared on resolution rather than handed on

- **`docs/spec/brief.md`** — no claimant. §5 rung 2 gains the two fitted
  constants and the warning that a single `efficiency` is a point prediction with
  a ±10 % tail; two §12 rows struck as discharged.
- **`experiments/region-profile/build_ergonomic_layer.py`** and one field of
  **`data/standards/room-constraints.json`** — the regression above.

### What this hands on

| obligation | to |
|---|---|
| **`min_pier_mm` 600 → 250**, with the three-threshold mullion sensitivity, and `value_format.conf_meanings` gains `fitted` to hold it. `ergonomic.corpus_label_split.threshold_m2` is also fitted and marked `engine_choice` today | *The annotation spec is US-shaped* — holds `room-constraints.json` |
| **The rule count is 42 and the `both` subset is 15**, stale in four places in `acceptance-bar.md` and once in `brief.md`; §6 and §9.1 both publish `open.fits_segment` as a jamb-return rule and it is not one; `win.kitchen_windowless`'s retirement should cite the flag, not the ticket | *A statutory floor, posted soft* — holds `acceptance-bar.md` and `rules.json` |
| **The bar is two opening-layer rules and a rounding error** (84.41 %, of which 26.53 + 15.97 points), so a warped donor's prior of clearing the bar is set by a layer the Proposal does not carry | *A third of real kitchens have no window*, *A donor's enclosed void becomes area nobody asked for* — hold `proposer.md` |
| **The conversion manufactures elongation** — 19.55 % of legs against 2.45 % of single-part Rooms, 10.6 % of converted dwellings carrying a part the bar rejects | *The dwelling that is built on two angles*, *The two-notch cap is now evidenced* — hold `rectangularise/` |
| **One door in five sits on a run below ADR 0021's `w + t_int + 400` contact threshold**, and 12.32 % below the leading-edge nib's wall-length half | *What an ordered entry sequence costs the solver* — holds `solver-toy/`; ADR 0021's holder |
| **`openings.md` §3.2's 100 mm jamb return is measured and central** — p40 of real door returns, so nothing to change. Recorded so it is not re-litigated. What is not free is its composite `w + 400`: **12.32 %** of real doors sit on a shorter run | `docs/spec/openings.md` — **no claimant** |
| **2.66 % of real dwellings have no circulation Space at all**, and `resolve` invents one unconditionally | whoever next holds `brief.md` — **no claimant** |
| **Five zoning rules, `dim.prefer_single_part`, the message locale schema, and `f_hi`/`f_lo` into data** — all written into `rules.json`'s new **`owed`** block so the next holder does not reconstruct them from the map | whoever next holds `rules.json` |
