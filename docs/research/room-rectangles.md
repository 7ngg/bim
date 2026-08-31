# Rooms that are not rectangles

Findings for *Whether a Room may be more than one rectangle* (ticket 28).
Decision: ADR
[0014](../adr/0014-a-room-is-one-or-two-rectangles-and-the-proposal-decides.md).
Harness: `experiments/room-rectangles/`.

Every stage of this system placed one rectangle per Room and no ticket ever
weighed it. This is what weighing it cost and what it found.

---

## 1. The question the ticket's headline number does not answer

Ticket 28 leads with *"v1 can exactly represent 2.7 % of real dwellings"*. That
is a true statement about the **corpus**, and corpus representability is
instrumental — it buys retrieval pool and training data. No Homeowner asks
whether a particular Swiss flat converts.

So the case has to be made on three grounds, kept separate because they do not
point the same way:

| | what it is | what it argues for |
|---|---|---|
| **output naturalism** | every-room-a-rectangle reads as a spreadsheet, not a flat | L-shapes in the **output** |
| **tiling slack** | `model.no_unassigned_area` forces every mm² into a Room, so with one rectangle each the only absorber is bloating a room — and *What a room's area is allowed to be* measured `dim.market_default_area` **actively rewarding** that bloat | a second rectangle as a **geometric** absorber |
| **corpus yield** | the 31 % conversion drop, taken disproportionately from the interlocked population | L-shapes in the **conversion** |

ADR 0014 goes ahead on the first two. The third is a consequence, and it is
re-owed as a measurement by *Re-measure the conversion at two rectangles per
Room* rather than claimed here.

**What the market does, for calibration.** `floorplan-generation-stack.md` finds
that essentially every published generator emits either arbitrary room polygons
(HouseGAN++, FMLM, floor-plan-rlvr, Raster2Seq, HypergraphFormer) or axis-aligned
boxes (DiffPlanner, the RPLAN/Graph2Plan line). **Rectangles-only is the
restrictive end of the field**, and it is the restriction that buys this engine
walls with thickness and exact integer geometry, which none of them have. One or
two rectangles is a deliberate middle: strictly more expressive than the box
models, still far short of the polygon models' tractability cost.

---

## 2. Two, not three

`experiments/rectangularise/rectilinear_k.py`, 1,200 Swiss dwellings, 8,293
rooms, at the 250 mm solve grid in the dwelling's own frame. Smallest *k* such
that the room is exactly a union of *k* axis-aligned rectangles (guillotine
decomposition, so an upper bound):

| k | rooms | cumulative | every room in the dwelling within k |
|---:|---:|---:|---:|
| 1 — today | 0.5286 | 0.5286 | **0.0267** |
| 2 — an L | 0.2497 | **0.7784** | 0.2392 |
| 3 — T, U, S, Z | 0.0976 | 0.8759 | 0.5467 |
| 4 | 0.0473 | 0.9232 | 0.7200 |
| >4 | 0.0768 | 1.0000 | — |

**Exactness is the wrong question for a drawing**, so
`experiments/room-rectangles/k_tolerance.py` re-asks it with a stated tolerance:
the smallest *k* whose best inscribed rectangles cover **98 %** of the room. Same
1,200 dwellings, same 8,293 rooms.

| type | n | k_tol = 1 | ≤ 2 | ≤ 3 | exact k = 1 | after a real 500 mm clean-up |
|---|---:|---:|---:|---:|---:|---:|
| ROOM | 2,129 | 0.6942 | 0.8971 | 0.9408 | 0.6740 | 0.6801 |
| BATHROOM | 1,804 | 0.6181 | 0.8952 | 0.9529 | 0.6181 | 0.6231 |
| CORRIDOR | 1,394 | **0.3034** | 0.5976 | 0.7970 | 0.2984 | 0.3142 |
| KITCHEN | 1,163 | 0.4402 | 0.7971 | 0.9200 | 0.4342 | 0.4445 |
| LIVING_DINING | 619 | **0.2633** | 0.6042 | 0.7884 | 0.2391 | 0.2439 |
| BEDROOM | 587 | **0.7206** | 0.9097 | 0.9574 | 0.7053 | 0.7087 |
| STOREROOM | 311 | 0.7203 | 0.9389 | 0.9582 | 0.7203 | 0.7331 |
| LIVING_ROOM | 245 | 0.4980 | 0.7796 | 0.8939 | 0.4449 | 0.4490 |
| **ALL** | 8,293 | 0.5400 | **0.8083** | 0.9045 | 0.5286 | 0.5367 |

Whole dwellings, every room within *k*: **0.0292 / 0.3008 / 0.6367** at tolerance,
against 0.0267 / 0.2392 / 0.5467 exact.

**The type split is the architectural intuition, measured.** Bedrooms, stores and
generic rooms are 69–72 % rectangular; corridors and open-plan living are 26–30 %.
A bedroom is a rectangle because a bed and a wardrobe want one; a corridor is an
L because the flat is.

**Capping at two costs the median room nothing.** Its best two inscribed
rectangles cover it exactly — median 1.0000, p25 1.0000 — and 87.2 % of all rooms
are at least 95 % covered. Even the rooms that genuinely need three or more keep
a median **0.9268** of their area under a two-rectangle cover. Both figures are
lower bounds: the cover is greedy raced against guillotine cuts, not optimal.

**And what is left at three is mostly not a room shape at all.** Share of rooms
whose perimeter is more than 10 % off the dwelling axis:

| | n | off-axis > 10 % |
|---|---:|---:|
| k_tol = 1 | 4,478 | 0.0063 |
| k_tol = 2 | 2,225 | 0.0445 |
| **k_tol ≥ 3** | 1,590 | **0.3503** |

A wall two degrees off axis becomes a **staircase** at 250 mm and needs one
rectangle per step. **No value of *k* fixes that** — it is the *Angled walls*
problem, which is genuinely v2 — and it is the second reason not to chase *k*
upward. ~~The first is that an L is a shape an architect draws and a T, U, S or Z
room is a shape a plan is left with.~~ — **struck by ADR 0045; see §8.** The
off-axis measurement above is now the *whole* of the k ≤ 2 defence together with
the box-count trade, and neither mentions shape.

---

## 3. What the freedom costs, and what the solver does with it

`experiments/room-rectangles/sweep_k2.py`, 240 solves, 10 seeds × 4 room counts ×
6 arms. Rig matches the shipped decision — 15 s, τ = 4, `mm_affine`, eroded minima
at `t_int` 150 (ADR 0010), corpus-median exposure, σ = 0.5 m, four workers, exact
tiling soft.

> ⚠️ **`corpus_median` has moved since every sweep in this document ran, and the
> arms are unaffected.** *The exposure presets were fitted to a measurement of
> one room* (2026-08-26) re-fitted the preset from the corpus **p3–p10** to
> **p51**, after `dataset-inventory.md` §1.5 was corrected. Every sweep here
> predates it. The design is **paired within exposure** — `k1` against
> `free_scoped` against `free_all` on the same Envelope, room count and seed —
> so exposure is a nuisance factor held constant and every *ratio* below stands.
> What must not be read off them is an absolute rate "at corpus-median
> exposure": the condition was harsher than a real flat's, so the L counts and
> survivor rates are **conservative**. Not re-run — 3.5 h of machine time to
> re-measure a comparison under an easier nuisance factor. See ADR 0029.
>
> One phrase in this document and its README **is** retired: results quoted as
> holding "at both `detached` and `corpus_median` exposure" were reporting
> agreement between the corpus p100 and the corpus p3–p10 — genuinely far apart,
> so the agreement was real and is now *stronger* than claimed, since the two
> conditions are today p100 and p51. The phrase over-claims coverage of the low
> end, not of the comparison.

**Ground truth is guillotine**, so no room is an L and no second rectangle is ever
*needed*. This measures the **cost** of the freedom and never its benefit — which
is the right half to measure here, and it is what makes the L counts readable:
every L below is gratuitous by construction.

Arms differ only in which Rooms may take a second rectangle: `k1` nobody (the
control), `free_scoped` circulation and open-plan types, `free_all` every Room,
`free_pen_*` every Room at an objective cost of 200 or 2 000, `forced2` two Rooms
compelled to be Ls.

| n | arm | vars | cons | VALID | t_first p50 | t_first p95 |
|---:|---|---:|---:|---:|---:|---:|
| 7 | k1 | 834 | 1,756 | 1.00 | **0.10** | 0.12 |
| 7 | free_scoped | 1,757 | 3,841 | 1.00 | 0.41 | 0.58 |
| 7 | free_all | 3,272 | 7,265 | 1.00 | **1.18** | 1.23 |
| 7 | free_pen_2k | 3,272 | 7,265 | 1.00 | 1.15 | 1.23 |
| 8 | k1 | 1,091 | 2,293 | 1.00 | 0.15 | 0.17 |
| 8 | free_all | 4,259 | 9,451 | 1.00 | 1.66 | 2.04 |
| 10 | k1 | 1,737 | 3,715 | 1.00 | 0.26 | 0.46 |
| 10 | free_all | 6,685 | 14,992 | 1.00 | 2.81 | 3.30 |
| 12 | k1 | 2,504 | 5,313 | 0.90 | 0.41 | 0.55 |
| 12 | free_all | 9,584 | 21,415 | 0.90 | 4.90 | 6.33 |

**The freedom costs no validity.** Every arm reaches a valid Plan at exactly the
control's rate — 1.00 in band, 0.90 at twelve rooms — which is the expected
consequence of an optional part being a strict relaxation. Whatever this design
costs, it is not feasibility.

**It costs search, and it costs it whether or not it is spent.** Time to a first
Plan is **11–12× the control at every room count** — 0.10 → 1.18, 0.15 → 1.66,
0.26 → 2.81, 0.41 → 4.90 — and the penalised arms, which produce **zero** Ls
below twelve rooms, pay ~11× as well (1.15, 1.57, 2.69, 6.17). The variable count
is 3.8–3.9× and the constraint count 4.0×. Scoping the freedom to circulation and
open-plan types halves the model and still costs ~4× the time to first Plan.

### What the solver does when it may choose

Share of *eligible* Rooms it made into an L, against a truth needing none:

| n | free_scoped | free_all | free_pen_200 | free_pen_2k | forced2 |
|---:|---:|---:|---:|---:|---:|
| 7 | 0.16 | **0.20** | 0.00 | 0.00 | 0.39 |
| 8 | 0.21 | **0.20** | 0.00 | 0.00 | 0.36 |
| 10 | 0.26 | **0.29** | 0.00 | 0.00 | 0.39 |
| 12 | 0.23 | **0.32** | **0.04** | **0.01** | 0.42 |

Runs with at least one gratuitous L: 0.60, 0.80, 0.80, 0.89 for `free_all`.

Three readings, and the third is the one that decides ADR 0014's second half:

1. **The rate rises with room count** — 20 % at seven Rooms, 32 % at twelve. It
   gets worse where the plans get harder.
2. **`forced2` takes more than it is forced.** Compelled to make two Ls, it makes
   2.7 to 5.0. Once the parts exist the objective spends them.
3. **The penalty is not a dependable off-switch.** It holds at 7, 8 and 10 rooms
   and **leaks at 12** — 0.04 of eligible Rooms at a penalty of 200, and still
   0.01 at **2 000**, which is an order of magnitude above the scale of a
   corner-displacement unit. A knob that works in the easy cases and slips in the
   hard ones is the wrong instrument for a decision about room shape.

### And it puts them on exactly the wrong rooms

`experiments/room-rectangles/kind_rates.py` regenerates all 40 Briefs the sweep
solved, takes each one's **actual** kind multiset, and joins it to the L counts.
The denominator matters: `scenarios.composition(n)` is *not* the multiset —
`assign_kinds` draws from a filler list within `comp_bounds` — and an earlier
reading of these results used it, got the rates wrong, and withdrew the claim.
This is the repaired version.

`free_all`, 39 valid runs. Corpus rectangularity is the k_tol = 1 share from §2,
so both sides are measured:

| kind | Ls | chances | solver L-rate | corpus type | corpus k_tol = 1 |
|---|---:|---:|---:|---|---:|
| utility | 27 | 80 | **0.338** | STOREROOM | 0.7203 |
| living | 12 | 39 | 0.308 | LIVING_ROOM | 0.4980 |
| bedroom | 23 | 78 | **0.295** | BEDROOM | 0.7206 |
| wc | 4 | 14 | 0.286 | BATHROOM* | 0.6181 |
| bathroom | 11 | 39 | 0.282 | BATHROOM | 0.6181 |
| kitchen | 7 | 39 | 0.179 | KITCHEN | 0.4402 |
| hall | 6 | 39 | 0.154 | CORRIDOR | 0.3034 |
| corridor | 3 | 30 | **0.100** | CORRIDOR | 0.3034 |

**Spearman between the solver's L-rate and the corpus's rectangularity: +0.795.**
The correlation is *positive*, and positive is the wrong sign. The types real
dwellings keep most rectangular — stores at 0.720 and bedrooms at 0.721 — are the
ones the solver reaches for hardest, at 0.338 and 0.295. The type real dwellings
make an L **70 % of the time** is the one it touches least, at 0.100.

The solver is not making bad Ls at random. It is making them in an order that is
close to the reverse of the one a real corpus would produce, because its objective
knows about corner displacement and nothing about what a room is for.

⚠️ **`free_scoped`'s correlation is −0.316, and that is not a defence of a
whitelist.** Its four types are `kitchen`, `hall`, `corridor`, `living` — the ones
*we* whitelisted. The ordering improves because we supplied the taste by hand,
which is exactly what ADR 0014 declines to do: a whitelist is a rule we invent,
and the corpus distribution is one we measure.

---

## 4. Design A against the alternatives, on a truth that is genuinely concave

`experiments/room-rectangles/sweep_designA.py`, 180 solves, 6 seeds × 3 room
counts × 2 L-counts × 5 arms. Same rig as §3, run alone so the seconds are not
contended.

Ground truth comes from `l_truth.py`: a guillotine dissection of *n* + *j*
rectangles with *j* adjacent pairs **merged**, so *j* Rooms genuinely are Ls, the
union of a merged pair is never itself a rectangle, and the tiling is still exact.
`l_truth_check.py` asserts all of that per scenario. The merges land where real
dwellings put them — `living 3.0 × 6.0 + 3.5 × 3.0`, `hall`, `kitchen`.

Five arms on the **same Brief and the same truth**:

| arm | what the Proposal carries | may the solver add a part? |
|---|---|---|
| `designA` | one box per **part**, presence fixed | no — the Proposal decided |
| `k1_bbox` | one box per Room: the L's **bounding box** | no |
| `k1_prim` | one box per Room: the L's **larger part** | no |
| `freeB0` | the larger part | yes, unpenalised |
| `freeB200` | the larger part | yes, at a penalty of 200 |

`k1_prim` is the fair control: its box is a real rectangle of a real dwelling and
separates cleanly from its neighbours, so it isolates *the extra rectangle* from
*the better Proposal*. Note also that ADR 0008 today would **drop** such a
dwelling outright — representability is the reject rule — so both k = 1 arms are
more generous than the shipped system.

### Did the L land on the right Room?

The truth names which Room is an L, so this is answerable rather than a matter of
taste. Over VALID runs only:

| arm | runs | Ls wanted | hit | missed | spurious | recall | precision |
|---|---:|---:|---:|---:|---:|---:|---:|
| **designA** | 18 | 25 | **25** | 0 | 0 | **1.00** | **1.00** |
| `k1_bbox` | 15 | 21 | 0 | 21 | 0 | 0.00 | — |
| `k1_prim` | 12 | 16 | 0 | 16 | 0 | 0.00 | — |
| `freeB0` | 13 | 18 | 10 | 8 | **35** | 0.56 | **0.22** |
| `freeB200` | 12 | 16 | **0** | 16 | 0 | **0.00** | — |

**This is the measurement the design rests on.** Told which Rooms are Ls, the
solver honours it exactly — 25 of 25, none spurious. Left to find them, it finds
a little over half and invents **thirty-five** that nothing asked for, nearly four
wrong for every right one. And the penalty that suppresses the wrong ones
suppresses the **right** ones with them: at 200 it places **zero** of sixteen.

So the knob has no good setting. At zero it is 22 % precise; at 200 it is silent.
A penalty makes Ls rarer, and rarity is not the axis the problem lives on.

### What it costs

| n | j | arm | vars | rel | VALID | t_first p50 | t_first p95 |
|---:|---:|---|---:|---:|---:|---:|---:|
| 7 | 1 | designA | 1,094 | 22 | 0.50 | 0.18 | 0.21 |
| 7 | 1 | k1_prim | 836 | 17 | 0.50 | 0.12 | 0.16 |
| 7 | 1 | freeB0 | 3,272 | 17 | 0.50 | 1.30 | 1.45 |
| 8 | 1 | designA | 1,384 | 28 | 0.67 | 0.20 | 0.31 |
| 8 | 1 | k1_prim | 1,094 | 22 | 0.67 | 0.17 | 0.19 |
| 8 | 1 | freeB0 | 4,261 | 22 | 0.67 | 1.68 | 1.92 |
| 10 | 1 | designA | 2,095 | 48 | **0.67** | 0.32 | 0.36 |
| 10 | 1 | k1_prim | 1,735 | 40 | **0.17** | 0.18 | 0.18 |
| 10 | 1 | freeB0 | 6,683 | 40 | 0.17 | 3.02 | 3.02 |
| 10 | 2 | designA | 2,491 | 52 | 0.17 | 0.51 | 0.53 |
| 10 | 2 | k1_prim | 1,741 | 37 | 0.00 | 0.23 | 0.23 |
| 10 | 2 | freeB0 | 6,689 | 37 | 0.00 | 3.30 | 3.30 |

**Design A pays for the parts it uses; Design B pays for the parts it might
use.** Only the *j* Rooms the Proposal says are Ls get a second box, so per run
against the fair control the model is **1.2–1.7×** the variables (median 1.37)
and time to a first Plan **1.1–2.8×** (median 1.79). Design B gives every Room
one and pays a flat **3.9×** the variables and **6.1–16.9×** the time (median
10.2×) — for a placement that is 22 % precise.

**Survivor rate over all 36 scenarios:**

| arm | VALID | proved OPTIMAL |
|---|---:|---:|
| **designA** | **0.500** | 4 |
| `k1_bbox` | 0.417 | 17 |
| `freeB0` | 0.361 | 1 |
| `k1_prim` | 0.333 | 8 |
| `freeB200` | 0.333 | 4 |

**The extra rectangle only helps when the Proposal says where to put it.** Design
B's survivor rate is 0.361 against the control's 0.333 — it has the same
expressive power as Design A and converts almost none of it, because it cannot
tell which Room should use it. Design A converts the same power into 0.500.

Two honest notes on that comparison:

- ⚠️ **`k1_bbox` beat `k1_prim`, which is the opposite of what was predicted.**
  The bounding box was expected to be the pessimal k = 1 reading, because an L's
  bbox overlaps the Room in its notch and the extractor then asserts a separation
  the truth contradicts. It still did better. A plausible mechanism — untested —
  is that the bbox conserves *area* while the primary-only Proposal understates
  every L Room by its second leg, so the objective pulls every room too small and
  the tiling has to make the difference up somewhere. Recorded as unexplained
  rather than explained away.
- **Design A uses more of the time budget.** It reached OPTIMAL 4 times against
  `k1_bbox`'s 17, and ran to the 15 s limit in most cells. Time to a *first* Plan
  is what C6's streaming job model consumes, and that stays inside half a second —
  but the gap to proven optimality is real and is the honest cost of the extra
  freedom.


---

## 5. The clean-up the ticket expected, refuted

Ticket 28 proposed erasing sub-500 mm features from corpus rooms before fitting
them, on this evidence from `experiments/rectangularise/why_k.py`:

> 0.5833 of k ≥ 3 rooms are k ≤ 2 once features narrower than 500 mm are erased;
> **0.3103 become a plain rectangle**.

**Those figures are an artefact of the operator, not a property of the rooms.**
`why_k.clean()` is documented as *"opening then closing: drop protrusions and
fill notches narrower than r"*, with `CLEAN_CELLS = 2` labelled a 500 mm
structuring element. Measured against synthetic masks
(`experiments/room-rectangles/morphology.py`, which carries a selftest):

- `_shift_all` pads and then slices back to the **original array shape**, so a
  dilation cannot grow past the array bounds. `why_k.py` rasterises each room
  over its own **tight bounding box**, so every room fills its array to the edge
  and the dilation is a no-op on it.
- The composition therefore reduces to erosion. On a tight-bbox 3.0 × 4.0 m
  rectangle `clean()` returns **96 of 192 cells** — the room eroded by 500 mm on
  every side, never restored.
- A **500 mm strip is deleted outright**, so the real deletion threshold is about
  750 mm.
- On a padded mask it fills **no notch at any size** — 250, 500, 750 and 1000 mm
  corner notches all survive untouched.

So the claim being made was *"k of the room eroded by 500 mm all round"*, which is
a far larger operation than the one described.

**Re-measured with a corrected opening and closing at a real 500 mm** (the
`clean500` column in §2): rooms that are a single rectangle go from **0.5286 to
0.5367** — **eight tenths of a percentage point**. Whole dwellings all-rectangle
go from 0.0267 to 0.0275. The clean-up buys essentially nothing.

It is refused because it buys nothing, not because it is wrong in principle: **on
a 250 mm grid nothing narrower than one cell is representable whatever the
operator returns.** Two consequences worth carrying:

- **The ticket's inflator story is wrong in its main term.** It attributed 58 %
  of k ≥ 3 to small hardware. The tolerance reading agrees with the corrected
  morphology: allowing a 2 % area tolerance moves per-room k = 1 by only 1.1
  points (0.5286 → 0.5400). Non-rectangularity in this corpus is **real
  architecture**, not pipe boxings.
- What the inflator story got right survives on other evidence: the off-axis
  table above. It is the *angled-wall* term that is doing the work at k ≥ 3, not
  the small-feature term.

**One property bounds what any morphological clean-up could ever claim**, and it
is asserted in the selftest: closing fills a bite in the **middle of an edge**
and never one at a **corner**, because the structuring element reaches a corner
bite from the background. A corner bite is exactly the shape that turns a
rectangle into an L.

---

## 6. What is not measured, stated so nobody quotes it as if it were

- **The conversion drop at k ≤ 2.** Ticket 28 item 6 asked for it; it is a
  different harness — the conversion fit, not the projection solver — and it is
  owned by *Re-measure the conversion at two rectangles per Room* rather than
  asserted here. What exists is a **prediction off an ablation**: hard adjacency
  is the dominant reject cause (73.6 % converted as shipped, **95.6 %** with hard
  adjacency off), and an L is precisely the shape that reaches an adjacency a
  rectangle cannot.
- **Anything drawn.** No plan has been rendered on this map. §7's room-tag rule
  is decided on containment, which is proved; whether it *reads* well is owed by
  *Look at the converted corpus*.
- **Reference View's profile types.** An L-shaped `IfcSpace` introduces no
  Boolean, but whether RV accepts an `IfcArbitraryClosedProfileDef` as a swept
  profile is unverified. *What geometry an IfcSpace actually gets*.
- **The low end of C13's band.** `scenarios.make_brief` finds no feasible
  room-type assignment below **7 rooms** once minima are eroded, at every `t_int`
  tested including 100, at both `detached` and the then-`corpus_median` exposure —
  where at `clear_t = 0` all of 4, 5 and 6 build. So **no solver measurement on
  this map, this one included, covers the bottom half of the shipped 3–10 band.**
  ✅ **Superseded in part.** On the corpus Envelope fixture (ADR 0029)
  **n = 5 builds and solves at 10/10** at both exposures, so the uncovered region
  is now **exactly n = 6** rather than everything below 7 — `solver-formulation.md`
  Part IV.2. The failure is `assign_kinds`, not the solver, and its mechanism is
  named in IV.3.
  That is evidence for the map's *Whether the solve grid should be finer than
  250 mm* patch and it extends *Ergonomic minima*'s "{5, and 6 unknown}" deletion
  to 4 and 6 — in the toy's own minima, which are not the shipped ergonomic
  layer, so it corroborates a direction rather than settling a number.
  ⚠️ **Both arms were the corpus p100 and p3–p10**, so this covers the low end of
  *exposure* far better than it covers the middle, which had no arm at all until
  the 2026-08-26 re-fit. And the **fixture** is now known to be part of the
  cause: the corpus-fitted Envelope family refuses `n` = 4 outright — a 40,4 m²
  dwelling cannot carry an articulated boundary *and* a 2,75 m `living` at the
  same time — which is a sharper statement of the same bottom-of-band gap than
  "no measurement covers it". ADR 0029.
- **ResPlan.** Every figure here is Swiss Dwellings.

---

## 7. What this hands on

| To | What |
|---|---|
| *Re-measure the conversion at two rectangles per Room* (new) | item 6, with the ablation evidence and a falsifiable prediction |
| *What geometry an IfcSpace actually gets* (new) | the concave `IfcSpace` profile, plus the §5/§12 storey-height contradiction that had no ticket |
| *The retrieval index and warp procedure* | a **live defect**: `select_relations` never filters on a positive separation cost, so an overlapping Proposal has separations asserted it never made. True at k = 1 today |
| *H8 and the single-aspect flat* | a Room can now present a **leg** at the facade, which relaxes H8's arithmetic — and may not be relief worth taking |
| *What the engine says when the Envelope is bigger than the programme* | ADR 0013's circulation-count dependency, discharged: `resolve` invents one Room per circulation type and the L covers the multi-wing case |
| *Two room vocabularies in one file* | whether `hall` / `entrance_lobby` / `corridor` can be told apart, which is what would make the circulation-count rule measurable |
| *Look at the converted corpus* | the `why_k.clean()` defect, and the room-tag legibility check |
| `rules.json`'s holder | one new hard predicate `dim.leg_join`, ~~one soft `dim.prefer_single_part`~~ (**withdrawn by ADR 0045** — §8.3: the over-production is the pool ranking, not the Proposer), and a **which-part-does-this-bind** column on every dimensional rule |
| *What each §6.1 term is scored for* (81) | the pool ranking prefers two-part-rich donors by **+8,0 points** over a room-count-matched expectation, and nothing decided that it should — §8.3 |
| `proposer.md`'s holders (67, 81) | §1's constraint gains a clause: two Parts **may not be flush at both ends** — ADR 0045 decision 2, §8.4 |

---

## 8. Two rectangles make four shapes, and the cap never chose between them

Ticket 79, ADR 0045. Harness: `arms_parts.shape_of`, over
`experiments/rectangularise/out/swiss_fit_k2.json`.

Two axis-aligned rectangles sharing an edge make an **L** (flush at one end), a
**T** (one span strictly contains the other), a **Z** (neither), or a plain
**rectangle** (flush at both). ADR 0014 capped the count and argued the cap on
shape; it never constrained the shape.

| shape | rooms | share | vertices | reflex | IoU p50 |
|---|---:|---:|---:|---:|---:|
| L | 851 | 55,2 % | 6 | 1 | 0,944 |
| T | 334 | 21,6 % | 8 | 2 | 0,873 |
| Z | 331 | 21,5 % | 8 | 2 | 0,900 |
| rectangle | 27 | 1,8 % | 4 | 0 | 0,809 |

**44,8 % do not have exactly one reflex corner.**

### 8.1 It is a circulation-and-social phenomenon

| type | rooms | 2-part | L | T | Z | rect | not-L |
|---|---:|---:|---:|---:|---:|---:|---:|
| CORRIDOR | 2 675 | 650 | 323 | 195 | 130 | 2 | **50,3 %** |
| LIVING_DINING | 1 221 | 573 | 301 | 99 | 171 | 2 | **47,5 %** |
| LIVING_ROOM | 447 | 83 | 54 | 7 | 18 | 4 | 34,9 % |
| ROOM (generic) | 4 081 | 132 | 93 | 25 | 7 | 7 | 29,5 % |
| KITCHEN | 2 249 | 59 | 45 | 3 | 2 | 9 | 23,7 % |
| BEDROOM | 1 069 | 26 | 21 | 3 | 2 | 0 | **19,2 %** |
| BATHROOM | 3 379 | 13 | 8 | 2 | 0 | 3 | 38,5 % |
| STOREROOM | 561 | 3 | 2 | 0 | 1 | 0 | 33,3 % |

Corridor and social carry **89,5 %** of all T and Z. At dwelling level: **26,9 %**
hold a T or a Z, **12,4 %** in the corridor alone, **12,6 %** in corridor and
social only, and **1,9 %** touching a private room. §2's *"a corridor is an L
because the flat is"* is right and under-counts — a T corridor reaches two wings.

### 8.2 The warp reproduces it, which is what makes it a shipping fact

Over 284 warped Proposals (`experiments/plane-accounting/out/armsp_rows_parts.jsonl`):
345 two-part Rooms — 206 L, 63 T, 73 Z, 3 rectangle, **40,3 % not an L**.
**94,1 %** of emitted T/Z is corridor or living_dining; **1,8 %** of Proposals put
one on a private room, against the corpus's 1,9 % of dwellings. The warp
**preserves donor part count on 284/284**.

**46,5 % of Proposals carry at least one T or Z Room**, higher than the corpus's
26,9 % of dwellings, because the warp emits two-part Rooms at **1,21 per Proposal**
against **0,67 per dwelling**.

### 8.3 The over-production is selection, not proposal

| rooms | corpus 2-part | selected 2-part |
|---:|---:|---:|
| 4 | 12,6 % | 25,0 % |
| 5 | 9,1 % | 22,2 % |
| 6 | 7,7 % | 18,1 % |
| 7 | 10,6 % | 20,5 % |
| 8 | 10,7 % | 15,4 % |
| 9 | 9,9 % | 14,4 % |
| 10 | 9,2 % | 14,0 % |

Pooled: **17,6 %** emitted against **9,8 %** in the corpus. Room-count-matched
expectation is **9,6 %**, so stratification explains **none** of it: the full
**+8,0 points** is the pool ranking, and it holds at every room count. Combined
with 284/284 part-count preservation, the Proposer creates nothing — best-of-*m*
draws two-part-rich donors. This is why ADR 0045 withdrew
`dim.prefer_single_part`, and it is handed to ticket 81.

### 8.4 The shapes pass the bar they are held to

Per-part aspect on clear dimensions, `corridor` and `storage` exempt, hard reject
above 3,0 (`acceptance-bar.md` §10):

| shape | rooms | hard fail | soft (> 2,2) |
|---|---:|---:|---:|
| L | 526 | 27,2 % | 46,8 % |
| T | 139 | **23,7 %** | 54,7 % |
| Z | 200 | **21,5 %** | 35,0 % |
| rectangle | 25 | **48,0 %** | 64,0 % |

**T and Z hard-fail less often than L.** The degenerate rectangle's 48,0 % is an
artefact of the encoding: measured **merged**, the same 25 rooms hard-fail at
**4,0 %**, so **11 of 25 are false rejections** created by slicing a rectangle in
two. ADR 0045 decision 2 normalises the encoding rather than exempting the rule.

### 8.5 Restricting to L, and the honest bound on its cost

Falling back to the larger part loses a median **29,4 %** of a T's area and
**33,8 %** of a Z's (p90 45,9 % and 46,7 %). ⚠️ **That is an upper bound and it is
not why the restriction was refused.** A converter constrained to L would find a
different, better L. **No arm measures it** — `swiss_fit_k1.json` refuses the
second part outright, a different question — and one was deliberately not built:
ADR 0045 rests on shape being *arrangement*, so a favourable cost number would
still not license the contract to make an arrangement claim.

The join is not the discriminator either: `fit_rects.py` enforces `JOIN_CELLS`, so
the minimum shared edge is **5 cells for all four shapes** and `dim.leg_join`
cannot tell them apart.

### 8.6 Every figure above is on a non-reproducible measurement

`fit_rects.py` runs CP-SAT at `num_search_workers = 4` with **no `random_seed`**,
and **16,0 %** of dwellings return `FEASIBLE` under `TIME_LIMIT = 10.0` —
contributing **41,2 %** of all two-part Rooms. ADR 0041 published **1 535** from an
earlier run of this rig where the current file yields **1 543**, a difference no
population filter reconciles.

**The distribution is stable where the records are not.** Not-L is **44,8 %**
pooled and **43,1 %** over the 907 proved-optimal Rooms alone; cap-hit dwellings
are T/Z-richer at 47,3 %, so a longer cap drifts the headline **down**, ~~bounded at
43,1 %~~. Every conclusion in §8 survives at that floor. Ticket 85 owns the defect.

⚠️ **Amended by ADR 0046** — [The conversion is a time-capped, unseeded
solve](../wayfinder/tickets/85-the-conversion-is-a-time-capped-unseeded-solve.md),
`rectangularisation.md` §16. The first sentence is **confirmed** and the bound is
**struck**.

*Confirmed*: the distribution is stable where the records are not, now measured
rather than inferred. Two runs of this rig over one 400-dwelling key list disagree
on **27 %** of covers and **7 %** of per-Room shape classes, while the pooled
not-L moves **0,4 points** and the two-part count is unchanged. The 1 535-vs-1 543
gap needs no population filter: it is **0,5 %** against a measured run-to-run range
of **2,9 %**, so it is a smaller-than-typical draw from noise this rig always had.

*Struck*: **43,1 % is not a floor.** "Proved optimal at 10 s" is not a fixed
population — it is the *easy* dwellings. Raising the cap to 30 s moves T/Z-rich
dwellings **into** it: the 41 dwellings that become OPTIMAL only at 30 s carry
**51,5 %** not-L against **41,8 %** for those already proved at 10 s. So the two
planes converge rather than the pooled figure falling to the optimal-only one —
pooled/optimal goes 47,7 / 41,1 % at 10 s to 46,4 / **45,0 %** at 30 s, a 6,6-point
gap closing to 1,4. The convergent value is **~45–46 %**, *above* the struck bound
and at least as high as the published 44,8 %, so §8's conclusions are unaffected
and mildly strengthened. (The 41,8-vs-51,5 contrast alone is ~1,3 sd at these n;
the convergence of the two planes is the robust part and does not rest on it.)

⚠️ **`experiments/rectangularise/` is not touched by this ticket** — §8 reads the
existing output and adds no probe. The shape classifier is `arms_parts.shape_of`,
in `experiments/plane-accounting/`, which ticket 83 claims.
