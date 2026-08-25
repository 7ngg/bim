---
id: 40
title: Re-measure the conversion at two rectangles per Room
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
blocked_by: []
writes:
  - experiments/rectangularise/
  - docs/research/rectangularisation.md
---

# Re-measure the conversion at two rectangles per Room

## Question

**ADR 0008's conversion drops 31 % of Swiss Dwellings, and that price was paid
for a constraint ADR 0014 has since removed.** Re-measure it.

*Rectangularising real rooms* converts a corpus dwelling by solving it: one
CP-SAT fit per dwelling with the real dwelling's separation directions and
door-width adjacencies hard and exact tiling soft, **one rectangle per room**. A
dwelling with no such tiling is dropped, and 31 % of Swiss Dwellings and 40 % of
ResPlan are. ADR
[0014](../../adr/0014-a-room-is-one-or-two-rectangles-and-the-proposal-decides.md)
gives every Room a second rectangle. Nobody has re-run the fit with it.

This is ticket 28 item 6, deliberately **not** resolved there. Item 2's solver
cost was the required measurement and it was made; this one is a different
harness — the conversion fit, not the projection solver — and it was left owned
rather than asserted.

**Why it matters more than a percentage.** The dropped population is the
*interlocked* one: `STOREROOM` over-represented 1.71×, bbox overlap 2.9× higher.
Those are exactly the dwellings an L absorbs. And the drop is not uniform across
the band — **83 % of 4-room dwellings convert against 46 % of 10-room** — so
retrieval's pool shrinks most where `proposer.md` §2.1 already showed it thinnest.
Every coverage figure on the map downstream of the conversion inherits this.

## A falsifiable prediction, stated so it can be wrong

`experiments/rectangularise/ablate.py` (250 dwellings, `out/ablate.log`) already
says **which constraint family** the reject rule is rejecting for:

| arm | converted |
|---|---:|
| as shipped | 0.7360 |
| area band ±25 % | 0.9080 |
| area free | 0.9120 |
| up to 4 notches | 0.6680 |
| relations, neighbours only | 0.8200 |
| **no hard adjacency** | **0.9560** |
| no hard relations | 0.9375 |
| relations + adjacency off | 1.0000 |

**Hard adjacency is the dominant cause** — turning it off recovers 22 points, more
than any other single relaxation. And an L is precisely the shape that reaches an
adjacency a rectangle cannot: a corridor that wraps a wing touches rooms on two
sides of it.

So the prediction is that k ≤ 2 attacks the dominant reject cause **directly**,
and the drop should fall substantially. That is a prediction off an ablation, not
a measurement of the thing itself. Do not quote it as one.

## What has to be done

1. **Extend `fit_rects.fit()` to two rectangles per room.** The projection
   solver's version is already written and exercised —
   `experiments/room-rectangles/solver_parts.py` — including the part-level
   presence trick (a zero-area box, which `AddNoOverlap2D` ignores in the pinned
   ortools; `smoke_zero_box.py` asserts it), the leg floor, the join constraint,
   and room-level aggregation of adjacency and flow. The conversion fit differs
   in what it optimises, not in its structure.
2. **Re-run the drop on both corpora**, and split it by room count, because the
   4-versus-10-room asymmetry is what bites retrieval.
3. **Re-measure the fidelity ladder.** ADR 0008's tiers A–D and *"retrieval
   admits tier A only"* were set against a one-rectangle fit. Ask whether the
   tier-A population is now large enough that the ladder still earns its
   complexity.
4. **Check the dropped population is still the interlocked one.** If k ≤ 2
   absorbs the interlocked dwellings, whatever remains dropped is something else,
   and naming it is worth more than the percentage.
5. **Re-state `proposer.md` §2.2's coverage table**, which *Rectangularising real
   rooms* already invalidated once and which is owed by *The retrieval index and
   warp procedure*. Coordinate: that ticket must not re-measure coverage on a
   conversion this ticket is about to move.

## What NOT to re-open

ADR 0008's mechanism — *a corpus dwelling is converted by solving it* — is not in
question, and neither is representability as the reject rule. Zero adjacencies
destroyed and zero relations flipped are guarantees of the formulation, not of
the rectangle count, and they must still hold.

⚠️ **`why_k.clean()` is broken and nothing here may use it** — see the note added
to *Look at the converted corpus*, and `experiments/room-rectangles/morphology.py`
for a corrected implementation with a selftest.

---

## Resolution

**Two thirds of the Swiss drop and four fifths of the ResPlan drop were paying
for a constraint ADR 0014 had already deleted.** ADR
[0016](../../adr/0016-the-conversion-names-its-own-ls.md). Findings
`docs/research/rectangularisation.md` §11. Harness
`experiments/rectangularise/` — `fit_rects.py --k2`, `analyse_k2.py`,
`validate_k2.py`, `name_rate.py`, `coverage_thinning.py`.

| | Swiss k = 1 | Swiss k ≤ 2 | ResPlan k = 1 | ResPlan k ≤ 2 |
|---|---:|---:|---:|---:|
| converted | 0.6930 | **0.9026** | 0.5990 | **0.9360** |
| dropped | **0.3070** | **0.0974** | **0.4010** | **0.0640** |
| gained / lost | — | 538 / **0** | — | 337 / **0** |

Paired: the same 2,600 dwellings and 1,000 plans, same order, same code, only
`k_of` changed. McNemar exact **p = 2.2 × 10⁻¹⁶²** and **7.1 × 10⁻¹⁰²**. Both
k = 1 arms reproduce the shipped files exactly — Swiss 1,787 / 805 / 8, ResPlan
597 / 399 / 2 / 2 — so the refactor moved nothing at one rectangle.

### The prediction was right, and it was right for the stated reason

The ticket predicted off `ablate.py` that **hard adjacency is the dominant reject
cause** and that k ≤ 2 attacks it directly, *"because an L is precisely the shape
that reaches an adjacency a rectangle cannot."* Re-run at k ≤ 2, adjacency's grip
falls from **+22.0 points to +6.0** and the area band's from **+17.2 to +4.4**.
Both dominant causes mostly vanish, and they turn out to have been **one cause in
two coats**: a room shape that could not reach.

### What the ticket did not anticipate, and it reframes the answer

**The slope moved more than the level.** ADR 0008's cost fell hardest where the
index was thinnest — 83 % at 4 rooms against 46 % at 10. The gain runs the other
way and is monotonic in room count: **+0.119 at n = 4, +0.351 at n = 9, +0.348 at
n = 10.** The spread across C13's band goes from **35 points to 12**. A 10-room
dwelling now converts about as well as a 4-room one used to, so **the conversion
has stopped being a filter that prefers small dwellings** — which was quietly
biasing the retrieval pool and the training corpus in the same direction. The
percentage was never the point.

### ⚠️ Three things the measurement forced that the ticket did not ask for

**1. Item 1's instruction pointed at Design B, and Design B is unmeasurable.**
The ticket says to port `solver_parts.py`'s machinery, which gives *every* Room an
optional second rectangle. Built that way, the shipped 10 s budget returns **0
OPTIMAL and 0 INFEASIBLE over 40 dwellings** — every solve burning the full
limit. `converted` degrades to *found something in 10 s* and the reject rule stops
existing. This is ADR 0014's own 11–12× against 1.2–1.7×, reproduced on a
different solver with a different objective. **The conversion uses Design A**:
the real room's shape names its Ls in a pre-pass. 2.9× faster and it decides.

**2. So every figure here is a lower bound — and the bound is ~2 points wide.**
`name_rate.py` classifies 2,734 rooms exactly. **2.05 %** are Ls with two legal
legs that the greedy naming missed; **23.2 %** are Ls whose short leg is under ADR
0014's 900 mm clear floor, which is **the rule working, not a defect**. The gap
between 9.85 % of rooms offered a second rectangle and ADR 0014's *"47 % need two
or more"* is the raster and the leg floor, not conservatism.

**3. ADR 0008 consequence 4 does not survive.** Its *"every Swiss dwelling
resolved to proven-optimal or proven-infeasible within 10 s, zero UNKNOWN"* held
at one rectangle only. At k ≤ 2, **1.27 % of Swiss and 16.5 % of ResPlan** return
UNKNOWN. Every rate above excludes them: a timeout has no verdict, and reading one
as a drop reports the time limit as a finding. ResPlan was re-run at 30 s and
**every plan resolved** — INFEASIBLE moving only 60 → 62, so the undecided were
overwhelmingly conversions, which is what makes excluding them correct rather than
convenient.

### Item 3 — the ladder does not still earn its complexity

ADR 0008's tiers **are** the ablation arms, so this is one run, not two.

| arm | tier | k = 1 | k ≤ 2 |
|---|---|---:|---:|
| as shipped | **A** | 0.7360 | **0.9320** |
| relations, neighbours only | **B** | 0.8200 | 0.9520 |
| no hard relations | **C** | 0.9375 | **0.9250** |
| relations + adjacency off | **D** | 1.0000 | 1.0000 |

**A → D spans 6.8 points where it spanned 26.4**, and A → B buys 2.0 where it
bought 8.4. ⚠️ **Tier C now sits *below* tier A**, because dropping the hard
relations removes the pruning that makes the search tractable and the arm times
out — 5 UNKNOWN of 80. **C is unmeasurable at k ≤ 2 for the same reason Design B
is, and a rung that cannot be measured cannot be a rung.**

Reduced to **A and D**. Retrieval's tier-A gate is untouched; what goes is a
four-valued training conditioning field that is now 93 % one value.

### Item 4 — the dropped population is no longer the one ADR 0008 named

| over-represented in dropped | k = 1 | k ≤ 2 |
|---|---:|---:|
| **LIVING_DINING** | **1.37×** | **1.02×** |
| STOREROOM | 1.71× | 1.57× |
| BEDROOM | 1.25× | 1.25× |
| bbox overlap, dropped ÷ converted | 2.90× | 2.07× |

The living/dining over-representation is **gone**, on exactly the type that takes
a second rectangle most (0.422). The L absorbs the interlocked open-plan
dwellings — predicted off the ablation, here measured directly. What remains is
**storeroom- and bedroom-heavy**, and a store is 72 % rectangular, so its cause is
**not its own shape**: it is a dwelling carrying several small ancillary rooms
with more pairs to satisfy at once. Naming that was worth more than the
percentage, as the ticket said.

### ADR 0014's central claim, measured from the other side

ADR 0014 refused solver-decided Ls on evidence the solver picks the wrong rooms —
Spearman **+0.795**, the wrong sign — and argued the conversion is different
because its objective is misassigned cells against the real room. That was an
argument. The conversion inverts the ordering:

| type | conversion fits 2 | ADR 0014's free solver |
|---|---:|---:|
| LIVING_DINING | **0.4219** | — |
| CORRIDOR | **0.2202** | 0.100 |
| BEDROOM | 0.0213 | 0.295 |
| STOREROOM | 0.0046 | 0.338 |
| BATHROOM | 0.0034 | 0.282 |

Its top two are the two types §4 already identified as the corpus's
non-rectangular ones. **98.5 % of offered second rectangles are used.** *The
Proposal decides* is preserved exactly, not weakened — the conversion is how that
sentence becomes data.

### What is preserved, asserted rather than assumed

Zero adjacencies destroyed, zero separation directions flipped, zero weakened,
across **69,040 Swiss and 22,940 ResPlan axis-pairs**. `validate_k2.py`
re-derives those and the ADR 0014 predicates — leg floor, join, non-overlap, the
symmetry break — from the emitted geometry sharing no code with the model:
**17,283 parts, 1,543 two-part Rooms, zero failures**, and it passes the k = 1
file too.

Fidelity **improves**: Swiss cell agreement 0.9008 → 0.9397, ResPlan 0.7617 →
0.8710, and the **worst room in a dwelling** gains 0.157 of IoU on Swiss and
**0.341** on ResPlan.

### Item 5 — handed over, not written

`docs/spec/proposer.md` is *The retrieval index and warp procedure*'s sole
claimant under the map's `writes:` rule, so this ticket produced the quantity
rather than the section: the per-multiset **pool multiplier**, median **1.219**
and up to **3.53** on the multisets that thinned hardest
(`coverage_thinning.py`). The spread is the point — a single corpus-wide factor
would under-state exactly the pools a Brief in the weak band lands in.

### Also fixed, and it was owed elsewhere

`load_swiss_geoms` now collects room types from the **filtered** polygon list, so
a dropped sub-minimum polygon no longer shifts every label after it. That is the
defect *Look at the converted corpus* measured at 1.23 % of fitted dwellings —
**fixed at source**, so its instruction to relabel from `swiss_rects.json` is
discharged.

### ⚠️ A process failure worth recording

The first ablation run reproduced the k = 1 ladder byte-for-byte because a patch
hunk wiring `k_max` into `run_dwelling` silently no-opped — it was the one hunk
in that edit without an assertion on the replacement. Two and a half hours of
machine time, and it was caught only because the numbers were *identical* to
`ablate.log` rather than merely similar. **A run whose output exactly reproduces a
prior run is evidence the new code did not execute**, and on this map that check
is cheap: every arm here was compared against its k = 1 counterpart before being
believed.
