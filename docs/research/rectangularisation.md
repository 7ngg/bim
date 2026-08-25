# Rectangularising real rooms

Findings for *Rectangularising real rooms*
(`docs/wayfinder/tickets/22-rectangularising-real-rooms.md`).

Everything here was measured on this machine against the corpora on disk, per
C11. Harness in `experiments/rectangularise/`:

| file | what it does |
|---|---|
| `probe_swiss.py` | geometry census — do rooms touch, what axis are they on |
| `measure_swiss.py` | the three per-room conversions over all of Swiss Dwellings |
| `measure_resplan.py` | the same, over ResPlan |
| `analyse_swiss.py` | every per-room table below |
| `fit_rects.py` | the conversion that ships: one CP-SAT fit per dwelling |
| `analyse_fit.py` | what the joint fit costs |
| `ablate.py` | which constraint the reject rule is rejecting for |
| `survivorship.py` | whether the surviving corpus is the same corpus |
| `rectilinear_k.py` | how many rectangles a real room actually needs (§9) |
| `fit_rects.py --k2` | the same fit at one or two rectangles per Room (§11) |
| `analyse_k2.py` | the two arms paired on the dwelling key (§11) |
| `validate_k2.py` | an independent check on the emitted geometry (§11.3) |
| `name_rate.py` | how wide the k ≤ 2 lower bound is (§11.1) |
| `coverage_thinning.py` | the pool multiplier ticket 23 needs (§11) |

---

## 0. The headline

**The conversion is not per room.** Every candidate the ticket named converts one
room in ignorance of its neighbours, and all three fail — two by deleting real
adjacencies, the third by making 86 % of dwellings geometrically impossible. The
conversion that ships is **one CP-SAT fit per dwelling** over the same 250 mm
grid the engine solves on, with adjacency hard and coverage soft exactly as C10's
amendment has the shipping solver post them.

Its reject rule is not a percentile. It is **representability**: a dwelling that
cannot be expressed as a rectangular tiling comes back INFEASIBLE, and that is
the drop.

> ⚠️ **Every conversion figure in §§1–10 is at ONE rectangle per room, and the
> headline number has since moved.** ADR 0014 gives a Room a second rectangle and
> **§11** re-measures the whole conversion with it: the Swiss drop falls
> **30.70 % → 9.74 %** and ResPlan's **40.10 % → 6.40 %**, with zero dwellings
> lost and every guarantee below intact. Read §§1–10 as the construction and the
> reasoning, which are unchanged, and §11 for any number about *yield*.

**Two things in the ticket's premise are wrong**, and both were inherited from
the papers rather than measured:

1. **"Roughly 40 % of real rooms are not rectangles" has no meaning without an
   axis.** In the corpus's own coordinates **0.0 %** of Swiss Dwellings rooms are
   rectangles — the corpus is geo-referenced, so an axis-aligned bounding box
   measures the *site's north angle*. Rectangularisation is two decisions, and
   the first one is which axis.
2. **ResPlan's "43.2 % exactly rectangular" is a vertex count, not a shape
   measure.** 43.18 % of its room polygons have exactly four vertices; **53.9 %
   have an area equal to their bounding box**, which is what being a rectangle
   means. The 10.7-point gap is rectangles stored with redundant collinear
   vertices. Every downstream use of 43.2 % has been pessimistic.

---

## 1. What the corpora actually hold

### 1.1 Rooms are Spaces, and no two of them ever touch

`probe_swiss.py`, 300 dwellings, nearest-neighbour distance from each room
polygon to the closest other room in the same dwelling:

| | gap, m |
|---|---:|
| p5 | 0.0120 |
| p25 | 0.0141 |
| **median** | **0.0993** |
| p75 | 0.2025 |
| p95 | 0.2182 |
| **share touching (distance 0)** | **0.000** |
| share within 1 mm | 0.000 |

Swiss Dwellings stores the **clear** polygon — inner faces, wall body in the gap
— which is exactly `CONTEXT.md`'s **Space**. So the ticket's question 2, "the
fraction of dwellings where rectangularised rooms no longer tile", is malformed
as asked: **they never tiled.** Any adjacency test over this corpus must carry a
wall-width tolerance; `touches()` returns nothing, forever.

### 1.2 Rectangularity is a property of the axis you pick

Fill ratio (polygon area ÷ its own bounding-box area, which for a polygon inside
its bbox *is* the IoU), measured three ways over the same 1,919 rooms:

| axis | rect @1 % | rect @2 % | rect @5 % | median fill |
|---|---:|---:|---:|---:|
| raw, as stored (geo-referenced) | 0.000 | 0.000 | 0.000 | 0.582 |
| dwelling's minimum rotated rectangle | **0.433** | **0.489** | 0.573 | 0.977 |
| length-weighted edge-direction histogram | 0.426 | 0.482 | 0.574 | 0.976 |

The two real candidates agree to a **median 0.05°, p95 0.22°, with 0.3 % of
dwellings differing by more than 2°**, so the cheaper one wins and the axis
question is closed: **the axis is the minimum rotated rectangle of the union of
the dwelling's rooms.** ResPlan needs no rotation — it is canvas-aligned, median
axis 0.000°, 4.9 % off by more than 1°.

**Swiss Dwellings is 48.9 % rectangular at ResPlan's own 2 % tolerance**, against
ResPlan's 62.1 %. First time this corpus has been measured. Real surveyed
dwellings are less rectangular than vector-traced ones, which is the direction
you would guess and nobody had checked.

---

## 2. The three per-room conversions, and why all three lose

Full Swiss Dwellings: **42,986 dwellings, 296,653 rooms**, 4–10 rooms per C13.
ResPlan: **16,617 plans, 110,802 rooms**. `apr` is the area-preserving rectangle
— bounding-box proportion scaled to the true area, centroid-anchored — which the
ticket did not list and which is the obvious fix for bbox's area inflation.

### 2.1 Per-room loss

Swiss Dwellings:

| conversion | IoU p5 | median | IoU ≥.98 | IoU ≥.90 | area err median | mean | p95 |
|---|---:|---:|---:|---:|---:|---:|---:|
| bbox | 0.6329 | 0.9869 | 0.539 | 0.744 | +1.3 % | **+11.1 %** | +58.0 % |
| largest inscribed | 0.6042 | 0.9717 | 0.434 | 0.681 | −2.0 % | −9.0 % | (p5 −39.2 %) |
| area-preserving | 0.6160 | 0.9831 | 0.513 | 0.687 | 0.0 % | 0.0 % | 0.0 % |

ResPlan:

| conversion | IoU p5 | median | IoU ≥.98 | area err mean |
|---|---:|---:|---:|---:|
| bbox | 0.5052 | 0.9973 | 0.554 | **+17.2 %** |
| largest inscribed | 0.6104 | 0.9807 | 0.510 | −7.7 % |
| area-preserving | 0.5815 | 0.9945 | 0.544 | 0.0 % |

On IoU and area the area-preserving rectangle looks like the winner. It is not.

### 2.2 Adjacency — where two of the three die

Contact graph: a pair sharing a wall run of at least 1.0 m, which is ADR 0001
consequence 3's door threshold (structural opening + `t_int`). Both polygons are
dilated by half a wall so the test works identically on clear polygons separated
by a wall and on rectangles that already touch.

Swiss Dwellings, true edges: mean 7.10 per dwelling.

| conversion | edges destroyed /dwelling | edges kept | ≥1 destroyed | edges invented /dwelling |
|---|---:|---:|---:|---:|
| bbox | **0.000** | **1.0000** | **0.02 %** | 1.259 |
| largest inscribed | 2.697 | 0.6203 | 89.6 % | 0.107 |
| area-preserving | 1.699 | 0.7608 | 81.5 % | 0.493 |

ResPlan is the same picture: bbox 0.000 destroyed, largest inscribed 2.782,
area-preserving 1.749.

**The largest inscribed rectangle deletes 38 % of every real adjacency in the
corpus. The area-preserving rectangle deletes 24 %.** The asymmetry is
structural, not empirical: a bounding box contains its room, so a real contact
cannot vanish; anything that shrinks a room deletes contacts. Any conversion that
holds area constant while the bbox inflates it by 11 % **must** shrink somewhere.

### 2.3 Separation directions — and a small theorem

`CONTEXT.md`'s **separation direction** is *asserted* when some line puts one room
entirely to one side of another, and *abstains* otherwise. That is a bounds test.
A bounding box preserves bounds. Therefore:

> **The bounding box preserves the separation relation exactly, on every pair, by
> construction.**

Which matters because separation direction is what the Proposal actually
transmits — *Proposer architecture survey* found per-pair separation agreement is
what predicts survival, and nothing published measures it. Measured:

Swiss Dwellings, **931,369 room pairs**, 88.0 % asserted on at least one axis:

| conversion | axis-relations preserved | weakened | spurious | flipped | pairs invented | pairs dropped |
|---|---:|---:|---:|---:|---:|---:|
| bbox | **1.0000** | 0.0000 | 0.0000 | 0.0000 | **0** | **0** |
| largest inscribed | 0.9172 | 0.0008 | 0.0820 | 0.0000 | 110,910 | 912 |
| area-preserving | 0.9715 | 0.0044 | 0.0240 | 0.0000 | 33,325 | 7,260 |

ResPlan, 325,899 pairs, 77.3 % asserted:

| conversion | preserved | weakened | spurious | pairs invented | pairs dropped |
|---|---:|---:|---:|---:|---:|
| bbox | **1.0000** | 0.0000 | 0.0000 | **0** | **0** |
| largest inscribed | 0.8602 | 0.0003 | **0.1395** | 72,574 | 24 |
| area-preserving | 0.9479 | 0.0052 | 0.0469 | 24,771 | 2,764 |

A spurious assertion is the **confident-wrong** pair `CONTEXT.md` says costs a
candidate outright — asserted, and not true of the real home. The largest
inscribed rectangle manufactures 110,910 of them on Swiss Dwellings alone.

### 2.4 What is actually wrong with the bounding box

It is the least bad of the three, and the case against it is narrower than it
first looks. It is **not** that bbox targets drive the solver INFEASIBLE — §2.3
is the proof they cannot, since the relations a bbox transmits are the truth's,
exactly. Two things are wrong with it, and both are about what it *withholds*.

**It hands over a target that is not a Plan.**

| conversion | dwellings whose rectangles collide | overlap, median | p95 | max |
|---|---:|---:|---:|---:|
| bbox, Swiss | **86.0 %** | 5.28 % of floor area | 22.70 % | 106.5 % |
| bbox, ResPlan | **99.3 %** | **23.97 %** | 52.62 % | 98.1 % |
| area-preserving, Swiss | 83.2 % | 1.80 % | 7.56 % | 22.2 % |
| largest inscribed, Swiss | 4.4 % | 0.00 % | 0.00 % | 0.38 % |

A pair of boxes that overlap on both axes **abstains** — it carries no relation
at all. So the arrangement arrives with exactly the pairs that overlap silently
dropped, and those are the interesting ones: the corridor that wraps three rooms,
the living-dining that wraps the kitchen. The solver is then free precisely where
the real home was most particular, and it invents that part of the plan. The
result is not the arrangement someone lived in, which is retrieval's entire
claim.

**It inflates area by a mean 11 % and a p95 58 %** (ResPlan: 17 % and 98 %), and
per-room target-area conditioning consumes whichever number the conversion
produces. Fixing that inside a per-room conversion is what the area-preserving
rectangle does, and §2.2 is the bill: holding area while the bbox inflates it
means shrinking, and shrinking deletes 24 % of the corpus's real adjacencies.

---

## 3. Graph2Plan's 93 % does not survive contact with either corpus

Graph2Plan reports "over 93 % of the rooms in RPLAN can be represented as the
intersection between their respective bounding boxes and the building boundary".
The ticket asked what the gap between that and 43.2 % is. The answer is that the
gap is **the corpus, not the method**:

| corpus | bbox ∩ envelope within 2 % | bbox alone within 2 % | share of the loss the envelope explains |
|---|---:|---:|---:|
| Swiss Dwellings | 0.5516 | 0.5390 | **2.75 %** |
| ResPlan | 0.5641 | 0.5538 | **2.29 %** |

Intersecting with the building boundary buys **1.3 points on Swiss Dwellings and
1.0 on ResPlan**. Real rooms are not concave because the building's outline cuts
them; they are concave because *another room* does. 93 % is a property of RPLAN.

So `bbox ∩ envelope` is a **diagnostic, never an output form** — and adopting it
would have cost the aspect-ratio predicate, room-tag-at-centroid, and ADR 0003's
notch cap in exchange for one point of fidelity.

---

## 4. Non-rectangularity is concentrated in two room types

Swiss Dwellings, bbox IoU by `entity_subtype`:

| type | n | IoU median | rect @2 % | median area |
|---|---:|---:|---:|---:|
| CORRIDOR | 49,697 | 0.839 | **0.262** | 7.58 m² |
| LIVING_DINING | 23,169 | 0.866 | **0.262** | 28.32 m² |
| KITCHEN | 41,661 | 0.977 | 0.474 | 8.04 m² |
| LIVING_ROOM | 7,932 | 0.980 | 0.499 | 20.51 m² |
| BATHROOM | 63,388 | 0.994 | 0.566 | 3.80 m² |
| ROOM | 76,052 | 0.998 | 0.726 | 14.38 m² |
| STOREROOM | 11,907 | 1.000 | 0.726 | 2.24 m² |
| BEDROOM | 21,717 | 0.9995 | **0.769** | 14.02 m² |

ResPlan, which has no corridor class at all — circulation is folded into `living`:

| type | n | IoU median | rect @2 % | median area |
|---|---:|---:|---:|---:|
| living | 16,820 | **0.5655** | **0.017** | 38.98 m² |
| kitchen | 16,495 | 0.967 | 0.371 | 9.92 m² |
| bedroom | 38,964 | 1.0000 | 0.571 | 18.19 m² |
| bathroom | 38,523 | 1.0000 | 0.849 | 4.69 m² |

**"40 % of rooms are not rectangles" is really "circulation and open-plan living
are not rectangles, and private rooms nearly all are."** ResPlan's `living` is
rectangular in **1.7 %** of plans — it is the circulation spine of a Chinese
apartment, wrapping every other room, which is also why bbox overlap on ResPlan
is five times Swiss Dwellings'.

This lands on the Brief: the rooms a Homeowner names most confidently — bedrooms —
are the ones rectangularisation costs least, and the ones the system invents on
their behalf — corridors — cost most.

---

## 5. The conversion that ships

For each dwelling:

**Step 1 — watershed.** Rasterise at **250 mm**, the shipped solve grid. Every
cell goes to the room whose polygon contains its centre; a cell in no room is
wall, and goes to the nearest room. That splits each wall at its centreline,
which is **ADR 0001's construction performed discretely**, and it yields a
ground-truth tiling whose room areas sum to the domain exactly. Interior holes —
shafts, lightwells, already excluded from the room set — are filled, because v1
has no such object.

**Step 2 — the Envelope.** Reduce the domain to something v1 can express: a bbox
minus at most two notches, per ADR 0003. A complement component touching the bbox
border is a notch; only components of at least 0.25 m² count, because a 250 mm
raster of a real outline manufactures slivers along every wall.

**Step 3 — the fit.** One axis-aligned rectangle per room, by CP-SAT:

| | |
|---|---|
| hard | **every separation direction the real dwelling asserts** — 88.0 % of pairs |
| hard | **every real adjacency survives** — flush faces overlapping by ≥ 1.0 m |
| hard | no two rectangles overlap (`AddNoOverlap2D`), notches as fixed obstacles |
| hard | per-room area within ±10 % of its watershed area |
| soft | exact tiling of the Envelope |
| objective | **the number of 250 mm cells that end up in the wrong room** |

Constraint *structure* is copied from the shipping solver deliberately: C10's
amendment posts relations hard and tiling soft, and a corpus prepared under
different rules from the solver that consumes it would be measuring a different
problem. Posting the true relations hard is `fix_relations` pointed at a real
dwelling instead of at a Proposal.

Relations the truth **abstains** on are left free. Those are the pairs where one
room wraps another, and a rectangle model has to pick a side — that choice is
forced by the model, not an error in it, and it is the one place the conversion
adds information rather than losing it.

**Three things were measured wrong first, and each is worth recording because
each looked obviously right:**

- **Posting exact tiling hard rejects almost every real dwelling** — 17 of 40
  INFEASIBLE, 22 timed out. It is also simply the wrong model, since the solver
  this corpus feeds does not post it hard either.
- **The shipped objective is the wrong objective here.** L1 corner displacement
  is what the solver minimises when *projecting* a Proposal. Used for *fitting*, it
  is nearly uncorrelated with how much of the dwelling lands in the right room:
  **IoU median 0.14**, against **0.82** for minimising misassigned cells, on the
  same dwellings with the same constraints. Projection and fitting are not the
  same problem, and sharing the machinery hides it.
- **Approximating a notch by the bounding box of the complement component
  over-cuts**, deleting a room outright in **15 %** of dwellings — an artefact of
  the approximation, not anything ADR 0003 says. The notch is the largest
  rectangle *inside* the component, which under-cuts: it leaves a little
  non-dwelling inside the Envelope, which shows up as envelope loss and costs a
  room nothing.

**And posting the relations hard is what makes it a conversion rather than an
approximation.** Without them the fit is feasible more often — 90 % against
77.5 % — and it **flips 2 % of pairs outright**: truth says the kitchen is left
of the hall and the tiling puts it right of it. It also weakens 3.6 %. With them,
flipped and weakened are both **exactly zero** by construction, IoU rises from
0.823 to 0.856, and the solve gets **seven times faster** because the relations
prune the search. The 12 points of feasibility are the price, and they are not a
loss: a dwelling that cannot be tiled without reordering its rooms is a dwelling
v1 cannot represent, which is what the reject rule is for.

---

## 6. What the joint fit costs

**2,600 Swiss Dwellings dwellings**, sampled by key hash so the sample is not one
site, 4–10 rooms. Every figure below is at a **10 s** limit and 4 workers.

### 6.1 What happens to a real dwelling

| outcome | n | share |
|---|---:|---:|
| **OPTIMAL** — a proven-best tiling | 1,787 | **0.6873** |
| **INFEASIBLE** — no tiling exists under the constraints | 805 | **0.3096** |
| a room vanished in the 250 mm raster | 8 | 0.0031 |
| timed out | **0** | **0.0000** |

**Nothing times out.** Every dwelling is decided — proven optimal or proven
infeasible — within 10 s, median **0.44 s**, p95 **1.50 s**. That matters more
than the rate: the reject rule is *decidable*, so a dropped dwelling is a fact
about the dwelling and not about the time limit. Ticket 15's headline worry —
that expiry hides an unassigned floor — cannot arise here.

### 6.2 What it preserves, and what it costs

| | |
|---|---|
| per-room IoU | p5 0.3495, p25 0.7200, **median 0.8950** |
| cell agreement | p5 0.6974, p25 0.8328, **median 0.9005** |
| per-room area error | median **−3.45 %**, mean −2.84 %, beyond ±10 %: 5.4 % |
| uncovered Envelope | median 3.10 %, p95 7.30 % |
| **adjacencies destroyed** | **0 of 17,367** |
| separation directions preserved | **0.8435 same, 0 weakened, 0 flipped**, 0.1565 spurious |

Set against the bounding box: area error goes from a mean **+11.1 %** to
**−2.8 %**, the target becomes a tiling instead of a pile of overlapping boxes,
and adjacency and relation fidelity are held by construction rather than by luck.
The 15.65 % spurious relations are the pairs the truth *abstained* on — one room
wrapping another — where a rectangle model must pick a side. They are the
conversion making a forced choice, not losing information.

### 6.3 The cost falls where the corpus can least afford it

| rooms | tried | converted | IoU median | cell agreement |
|---:|---:|---:|---:|---:|
| 4 | 194 | **0.8299** | 0.8979 | 0.8980 |
| 5 | 377 | 0.8700 | 0.9000 | 0.9098 |
| 6 | 527 | 0.8159 | 0.9169 | 0.9139 |
| 7 | 518 | 0.7046 | 0.8842 | 0.8909 |
| 8 | 507 | 0.5464 | 0.8802 | 0.8895 |
| 9 | 344 | 0.4884 | 0.8826 | 0.8865 |
| 10 | 125 | **0.4640** | 0.8629 | 0.8910 |

**Fidelity barely moves across the band — 0.86 to 0.92 — and the conversion rate
halves.** More rooms do not convert *worse*; they convert *less often*. That is
the honest shape of the cost, and it lands badly: *What the model proposes*
measured retrieval blanking on 12.4 % of 7–10-room Briefs against a median pool
of 66, and this multiplies that pool by roughly 0.5. **The conversion costs
retrieval most exactly where retrieval was already weakest.**

It is affordable only because of ADR 0005. Retrieval blanking hands the Brief to
the trained model, which always answers, so a smaller index shifts load between
sources rather than refusing Briefs. Whoever picks up *The retrieval index and
warp procedure* must re-measure coverage on the converted corpus — the 9.5 % and
12.4 % figures were measured before this conversion existed and no longer hold.

### 6.4 ADR 0003's two-notch cap, measured for the first time

The map's *Non-orthogonal geometry* fog patch records the ≤2-notch cap as
"unevidenced in both directions", and suspected it was too tight. Counting
complement components of at least 0.25 m² on 2,592 dwellings:

| notches needed | share | cumulative |
|---:|---:|---:|
| 0 | 0.0440 | 0.0440 |
| 1 | 0.2245 | 0.2685 |
| **2** | 0.3499 | **0.6184** |
| 3 | 0.2562 | 0.8746 |
| 4 | 0.0887 | 0.9633 |
| 5+ | 0.0367 | 1.0000 |

Median 2, p90 4. And what the cap actually costs, as envelope area the Envelope
misdescribes:

| k notches | median loss | p75 | p95 |
|---:|---:|---:|---:|
| 0 (plain rectangle) | 0.1646 | 0.2628 | 0.4655 |
| 1 | 0.0531 | 0.1111 | 0.2244 |
| **2 — ADR 0003** | **0.0185** | 0.0576 | 0.1419 |
| 3 | 0.0121 | 0.0402 | 0.1166 |
| 4 | 0.0103 | 0.0377 | 0.1102 |

**The cap is vindicated, which is the opposite of what the fog patch feared.**
Two notches describe 61.8 % of real dwellings exactly and cost the rest a median
1.85 % of envelope area; a third notch recovers 0.64 points of that and a fourth
0.18. The curve is flat past two. Note also that a *plain rectangle* — no notches
— misdescribes 16.5 % of envelope area at the median, so the L/U/T shapes are
doing real work and are not decoration.

And raising the cap makes things **worse**, not better — §6.5. A more articulated
Envelope is harder to tile with *n* rectangles, so the notch that describes the
outline more faithfully takes away the freedom the rooms needed.

### 6.5 ResPlan converts markedly worse, and it is the living room

Same conversion, same constraints, **1,000 ResPlan plans**:

| | Swiss Dwellings | ResPlan |
|---|---:|---:|
| converted | **0.6873** | **0.5990** |
| INFEASIBLE | 0.3096 | 0.3990 |
| per-room IoU median | 0.8950 | **0.6792** |
| cell agreement median | 0.9005 | 0.7617 |
| per-room area error median | −3.45 % | −6.25 % |
| envelope loss at 2 notches, median | 0.0185 | 0.0460 |
| adjacencies destroyed | 0 of 17,367 | **0 of 5,321** |
| relations flipped / weakened | 0 / 0 | **0 / 0** |
| relations spurious | 0.1565 | 0.2056 |

The fidelity guarantees hold on both corpora — zero destroyed adjacencies, zero
flips, on every plan. What differs is how much of the dwelling survives: **0.68
IoU against 0.90**.

The cause is §4. ResPlan has no corridor class; circulation is folded into
`living`, which is rectangular in **1.7 %** of plans and wraps every other room.
A room that wraps its neighbours is precisely the room a rectangle model must
distort, and ResPlan has one in every plan.

*Cross-dataset unification* excluded ResPlan from retrieval on metric grounds —
its geometry is not in metres. This is a second, independent reason, and it is
about shape rather than units: **ResPlan is a worse fit for a rectangle-based
engine than Swiss Dwellings is, and by a wide margin.** It stays a training
corpus under its conditioning tag, and the 40 % drop is affordable there —
Swiss ≈ 29,500 plus ResPlan ≈ 9,800 usable dwellings against *Proposer
architecture survey*'s ~4,000 training floor is still 10×.

### 6.6 Is the surviving corpus the same corpus, only smaller?

A conversion that drops 31 % is only safe if what it drops is not systematically
different. The obvious fear is self-confirming: a rectangle model drops the
dwellings rectangles cannot hold, trains on the remainder, learns boxy priors,
emits boxy plans — and every metric here would miss it, because all of them are
computed on survivors. `survivorship.py`, joining the fit against the pre-conversion
measurement on 2,600 dwellings:

**That fear is refuted.** Rooms that were already rectangles, as a share of the
training corpus:

| | share of rooms with bbox IoU ≥ 0.98 |
|---|---:|
| corpus before conversion | 0.5390 |
| dwellings that converted | **0.5372** |
| dwellings that dropped | 0.5336 |

Eighteen ten-thousandths. **The conversion does not select for rectangular
dwellings**, and the Proposer will not be trained on a corpus that is boxier than
the world.

**What it does select for is size and interlock:**

| median | converted | dropped |
|---|---:|---:|
| rooms | 6 | **8** |
| floor area | 71.7 m² | **89.9 m²** |
| worst room's bbox IoU | 0.7842 | **0.6175** |
| bbox overlap fraction | 0.0336 | **0.0974** |
| contact edges | 6 | 8 |

So a dwelling is not dropped for being non-rectangular *on average* — it is
dropped for having **one room that cannot be squared and neighbours interlocked
around it**. Overlap under bbox is 2.9× higher in the dropped set while mean
rectangularity is nearly identical: it is the *arrangement* that resists, not the
shapes.

Over-represented among the dropped, by ratio: `STOREROOM` **1.71×**,
`LIVING_DINING` 1.37×, `BEDROOM` 1.25×. Under-represented: `LIVING_ROOM` 0.43×,
`CORRIDOR` 0.84×. The storeroom result is the tell — a storeroom is the small
leftover space wedged into whatever corner remained, and a leftover is exactly
what a tiling of *n* rectangles has nowhere to put.

**The bias that is real is toward the small**, and it compounds with a thinness
the map already has: *Acquire the datasets* found the corpus falling away above
10 rooms, and conversion now removes more of what is left there (83 % of 4-room
dwellings convert against 46 % of 10-room). A Homeowner asking for a large flat
loses precedent twice over. That belongs to *The room-count envelope v1 promises*
as much as to retrieval.

### 6.7 What the reject rule is actually rejecting for

The drop is only a defensible rule if we can say what it is rejecting *for*.
`ablate.py`, relaxing one family at a time over the same dwellings:

| arm | n | converted |
|---|---:|---:|
| **as shipped** | 250 | **0.7360** |
| area band ±25 % instead of ±10 % | 250 | 0.9080 |
| area unconstrained | 250 | 0.9120 |
| Envelope may have up to 4 notches | 250 | **0.6680** |
| relations hard for neighbours only | 250 | 0.8200 |
| adjacency not required | 250 | 0.9560 |
| relations not required | 80 | 0.9375 |
| **relations and adjacency both free** | 80 | **1.0000** |

Three things fall out.

**No single family is the binding one.** Relaxing area alone recovers 17.6
points, adjacency alone 22.0, relations alone 20.2 — each nearly as much as the
others, on a drop of 26.4. They are not additive because they are not
independent: a dwelling can satisfy any two and fail the third.

**With relations and adjacency both free, every dwelling converts.** Nothing in
this corpus is un-tileable. What fails is tiling it **as itself** — the reject
rule rejects a dwelling for not being expressible as *its own* arrangement, never
for being unrepresentable in general. That is the sentence the rule should be
quoted by.

**The ±10 % per-room area band is stricter than anything the map states**, and it
costs 17.6 points. The stated warp budget is ±10 % on a dwelling's *total* floor
area (`docs/spec/proposer.md` §2.2), which per room is looser. ±10 % is kept for
v1 because a corpus looser than the gate it feeds cannot be checked against it,
but the value is an ENGINE_CHOICE and the curve above is the trade. It is the
same fidelity-versus-coverage trade the map already parks under *Where warp
fidelity actually breaks*, in different coordinates, and it belongs to *The
retrieval index and warp procedure* to fit — not here.

---

## 7. Corrections this note owes other documents

**`docs/research/dataset-inventory.md` §2.3 — the ResPlan rectangularity row.**
The 2 % figure reproduces exactly: **62.1 %** over all 17,000 plans and 62.5 %
over the first 2,000 the probe actually ran, against the reported 62.3 %. The
*exact* figure does not. Under every area-based definition tried the share is
**51.3 %** (float equality), **53.9 %** (1e-9), **55.2 %** (1e-3) — never 42.1 %.
What does land on the paper's number is the **vertex count: 43.18 % of room
polygons have exactly four vertices**, against the paper's 43.2 %. So the paper's
"exactly rectangular" is a statement about *storage*, and the row should read
53.9 % by area with the vertex figure noted separately.

**`docs/spec/proposer.md` §4.4** — "ResPlan reports 43.2 % exactly rectangular,
62.3 % at 2 % tolerance" inherits the conflation above, and its "how is unowned"
is now answered. §4.4 is rewritten by this note.

**The ticket's own premise.** "Those measure different things and are not in
conflict; the gap between them is this ticket." Half right. The Graph2Plan gap is
not a measurement mismatch, it is **the corpus** — bbox ∩ envelope buys 1.3
points on Swiss Dwellings and 1.0 on ResPlan, against the ~50 points 93 % implies.
And "roughly 40 % of real rooms are not rectangles" needed an axis before it
meant anything at all.

**ADR 0003's ≤2-notch cap** was recorded as "unevidenced in both directions". It
is now evidenced — see §6 — and the map's *Non-orthogonal geometry* fog patch can
strike its line that "how many real dwellings fit inside the cap is unmeasured".

**A term the map needs.** The conversion emits **centreline** rectangles: the
watershed splits each wall at its axis, so a converted room's area includes half
of every wall around it. That is what the solve domain is made of (ADR 0001) and
what the solver consumes. The **clear** area — the one a Homeowner reads and the
one the Acceptance bar is stated in — is the eroded rectangle. *Fit the
ENGINE_CHOICE acceptance thresholds to the corpora* fits clear-dimension
predicates and must erode before comparing, or every threshold it fits will be
generous by `t_int` per axis.

---

## 8. What this note does not establish

- **The fit is measured on a sample, not the whole corpus.** The three per-room
  conversions are full-corpus (42,986 Swiss dwellings, 16,617 ResPlan plans); the
  joint fit is not, because it costs about a second per dwelling against 14 ms.
  Sample sizes are stated in §6.
- **Which Envelope edges are exterior is not known to the fit**, so what §6
  reports is **boundary contact**, not window frontage. A room that kept its
  boundary run may still have kept the *party* side of it. Acceptance rule H8 is
  therefore not verified by this note, and *H8 and the single-aspect flat* should
  not assume it is.
- **Nothing has been rendered.** Inherited from *Acquire the datasets* and still
  true: no converted dwelling has been drawn and looked at by a person. Every
  number here is areas, cells and graph edges. A conversion that scores well and
  looks wrong would not have been caught.
- **The 250 mm raster rounds every room dimension to the solve grid** before any
  fitting happens, so a share of the measured loss is the grid rather than the
  rectangle. The map already carries *Whether the solve grid should be finer than
  250 mm* as fog; this note gives it a second reason to exist and does not
  separate the two costs.
- **Rooms with interior rings are flattened.** 0.6 % of Swiss Dwellings rooms
  wrap a hole — a shaft or a column. The watershed fills it, because v1 has no
  such object, and the filled area is charged to the room.
- **The conversion has not been run end-to-end into a Proposal.** That it
  produces a valid tiling is asserted by construction and checked per dwelling;
  that a *warped* one still solves belongs to *The retrieval index and warp
  procedure*.
- **OR-Tools aborted the ResPlan run after 1,000 plans** with an internal
  `CHECK` failure — `Infeasible solution! source: 'default_lp'`, a C++ abort that
  Python cannot catch. The checkpoint held and the figures above are that
  1,000; the plan that triggered it was not isolated. Anyone running this at
  corpus scale needs the driver to survive a worker abort, which means a
  subprocess per dwelling or a restart-from-checkpoint loop, not a `try`.
- **The Swiss figures are 2,600 dwellings and the ResPlan figures 1,000**, both
  sampled by key hash. Rates were stable to within a point from n≈1,200 onward,
  but no percentile here is a corpus-wide figure.

---

## 9. The premise this note never questioned, and should have

Everything above takes *one rectangle per Room* as given, because ticket 22's
scope says so. Asked afterwards whether that premise is right, the answer is
uncomfortable. `rectilinear_k.py`, 1,200 dwellings, 8,293 rooms, smallest *k* such
that a room is a union of *k* axis-aligned rectangles, at the 250 mm solve grid:

| k | rooms | cumulative | dwellings with **every** room within k |
|---:|---:|---:|---:|
| 1 — today's model | 0.5286 | 0.5286 | **0.0267** |
| 2 — an L | 0.2497 | **0.7784** | 0.2392 |
| 3 — T, U, S, Z | 0.0976 | 0.8759 | 0.5467 |
| 4 | 0.0473 | 0.9232 | 0.7200 |
| >4 | 0.0768 | 1.0000 | — |

**v1 can exactly represent 2.7 % of real dwellings.** The 53 % figure everything
above is built on is per *room*; per dwelling one bad room is enough, and the
median dwelling has six or seven chances. That is the real reason this ticket
existed, and it was never stated that way.

| type | n | k=1 | ≤2 | ≤3 |
|---|---:|---:|---:|---:|
| CORRIDOR | 1,394 | **0.2984** | 0.5739 | 0.7654 |
| LIVING_DINING | 619 | **0.2391** | 0.4927 | 0.6543 |
| KITCHEN | 1,163 | 0.4342 | 0.7704 | 0.8899 |
| BATHROOM | 1,804 | 0.6181 | 0.8908 | 0.9507 |
| ROOM | 2,129 | 0.6740 | 0.8643 | 0.9239 |
| BEDROOM | 587 | 0.7053 | 0.8790 | 0.9353 |

Both counts are **upper bounds**, pessimistic twice over: the decomposition is
guillotine-only, and a 250 mm raster turns a slightly-angled real wall into a
staircase needing many rectangles. The true complexity is lower than shown.

**The reason nobody had looked is a category error in the map.** "A room that is
not a rectangle" sat in the *Non-orthogonal geometry* fog patch next to angled
walls, so it inherited that patch's deferral — but **an L-shaped room is
orthogonal**, and CP-SAT places two rectangles as happily as one. The seam is
visible in the map's own text: ADR 0003 lets the *Envelope* have two notches while
a *room* may not have one, and a flat's corridor is L-shaped precisely because the
flat is.

Ticketed as *Whether a Room may be more than one rectangle*, with a recommendation
of **k ≤ 2** — 52.9 % → 77.8 % per room, corridors 30 % → 57 %, for one new degree
of freedom — and the honest caveat that k ≤ 2 still leaves only 24 % of dwellings
exactly representable, so this conversion does not go away, it gets less work to
do. **It also means the 31 % drop measured in §6 is a figure about the current
premise, not about the corpus**: the dwellings that fail are the interlocked ones
(`STOREROOM` over-represented 1.71×, bbox overlap 2.9× higher), which are exactly
what an L absorbs. Re-measure the drop at k ≤ 2 before treating 31 % as the price.

### 9.1 What causes k > 2, and it is mostly not room shape

`why_k.py`, 700 dwellings, 4,822 rooms. 21.1 % need k >= 3, and that decomposes
into three causes of which only the third is architecture:

| cause | share of k >= 3 rooms |
|---|---:|
| **features narrower than 500 mm** — pipe boxing, chimney breast, nib, reveal | **0.5833**, and 0.3103 become plain rectangles |
| **the room is not rectilinear at all** — >10 % of perimeter off-axis | **0.3232**, against 0.0059 of k = 1 rooms |
| genuinely T, U, S or Z | the remainder: CORRIDOR 0.2303, LIVING_DINING 0.3258 after clean-up |

An angled wall becomes a **staircase** at 250 mm, needing one rectangle per step.
That is the genuine non-orthogonal problem and **no value of k fixes it** — a
second reason not to chase k upward.

**And the number that decides ticket 28**: coverage of a room by its best two
inscribed rectangles is a **median 1.0000** over all rooms, with **88.05 %** of
rooms at least 95 % covered; even among k >= 3 rooms it is a median 0.9412. Both
are lower bounds. Capping at two rectangles costs the median room nothing.

### 9.2 A layout class nothing here has ever solved

The solver does not restrict to guillotine — `AddNoOverlap2D` over free
rectangles admits any tiling, pinwheels included, and that is a strength the map
never states. But `experiments/solver-toy/scenarios.py` generates **every**
ground-truth layout by recursive guillotine dissection, so every timing, every
percentile and the whole feasibility cliff in *Solver timing variance sweep* —
965 solves — was measured on guillotine layouts only.

Measured against real converted dwellings (`guillotine_share.py`, n = 1,787):
**6.27 % are non-guillotine**, rising to **13.7 % at 8 rooms and 15.5 % at 10**,
and the test overstates the guillotine share because it lets a cut pass through a
notch. The untested class sits at the top of C13's band, where the sweep already
found the solver most fragile. Ticketed as *The solver has only ever seen
guillotine layouts*.

---

## 10. Two defects in this note's own measurements

**"Zero adjacencies destroyed" means zero DOOR-WIDTH adjacencies destroyed.**
The contact graph counts a pair only when it shares at least 1.0 m — ADR 0001
consequence 3's threshold. Measured over 400 dwellings and 4,412 contacting
pairs, **32.68 % of real room-to-room contacts fall below it** (median 0.72 m;
24.6 % lie in 0.5–1.0 m and 8.1 % below 0.5 m). Those contacts are invisible to
the graph, are never posted as constraints in the fit, and could therefore be
destroyed freely without appearing anywhere in §6.2. The guarantee stands for
adjacencies a door can use, which is what circulation needs — but it is a
narrower claim than "adjacency is preserved", and this note made the broader one.

**The conversion hands interior shafts to habitable rooms.** v1's Envelope model
has boundary notches and no interior obstacles at all, so a shaft, riser or
lightwell inside the dwelling has nowhere to go: the watershed gives its cells to
the nearest room within 0.35 m, and anything left becomes a hole that
`envelope_approx` fills. Counted: **2.66 %** of dwellings have a filled hole,
median 0.10 % of dwelling area, p95 0.76 %. Small in area — and larger than
counted, because a shaft narrower than 0.7 m is absorbed by the watershed before
the hole test can see it, which is unmeasured.

It is small and it is still the thing an architect notices first, because what it
draws is **a bedroom over a riser**. The map parks risers under *Structural and
services reality*; this note is where the corpus consequence shows up, and the
honest statement is that v1 cannot express an interior obstacle of any kind.

---

## 11. The same conversion at two rectangles per Room

*Re-measure the conversion at two rectangles per Room*
(`docs/wayfinder/tickets/40-re-measure-the-conversion-at-two-rectangles-per-room.md`),
decision ADR
[0015](../adr/0015-the-conversion-names-its-own-ls.md).

Everything above §11 was measured with **one rectangle per room**, because that
is what the model allowed. ADR
[0014](../adr/0014-a-room-is-one-or-two-rectangles-and-the-proposal-decides.md)
gives every Room a second one. **The 31 % drop was a price paid for a constraint
that no longer exists**, and §9 said so without moving the number.

Paired re-run: the **same 2,600 Swiss dwellings and 1,000 ResPlan plans** in the
same order through the same code, with only `k_of` changed. Harness
`fit_rects.py --k2`, analysis `analyse_k2.py`, independent geometric check
`validate_k2.py`.

### 11.0 The headline

**Two thirds of the Swiss drop and four fifths of the ResPlan drop were paying
for the deleted constraint**, and **not one dwelling is lost** — the assertion a
strict relaxation owes.

| | Swiss k = 1 | Swiss k ≤ 2 | ResPlan k = 1 | ResPlan k ≤ 2 |
|---|---:|---:|---:|---:|
| converted | 0.6930 | **0.9026** | 0.5990 | **0.9360** |
| dropped | **0.3070** | **0.0974** | **0.4010** | **0.0640** |
| gained | — | 538 | — | 337 |
| lost | — | **0** | — | **0** |

McNemar exact **p = 2.2 × 10⁻¹⁶²** and **7.1 × 10⁻¹⁰²**. Both k = 1 arms
reproduce the shipped files exactly — Swiss 1,787 / 805 / 8, ResPlan 597 / 399 /
2 / 2 — so the refactor changed nothing at one rectangle and the pairing is
sound.

**Swiss excludes 33 dwellings (1.27 %) as UNDECIDED**, because at k ≤ 2 some
solves return UNKNOWN at the 10 s budget. A timeout has no verdict: counting it
as a drop would report the time limit as a finding. ResPlan's undecided share was
**16.5 %** at 10 s, so it was re-run at 30 s and **every plan resolved** — and
they resolved overwhelmingly to conversions, INFEASIBLE moving only 60 → 62,
which is what makes excluding them the right treatment rather than a convenient
one.

### 11.1 The two-rectangle model is a lower bound, and this is how wide

⚠️ **Quote this section's numbers as a floor, never as the value.** Which Rooms
may take a second rectangle is **named from the real room's own shape** — ADR
0014's Design A — not searched. That was forced, not preferred; see §11.5.
`name_rate.py` classifies 2,734 real rooms exactly (a mask is an L iff its bbox
complement is one corner-anchored rectangle):

| shape, on the watershed plane | share of rooms |
|---|---:|
| a rectangle already | 0.2191 |
| an **L** | 0.2582 |
| something else — T, U, S, Z, or a staircase off an angled wall | 0.5227 |

and of the rooms that got **no** second rectangle:

| reason | share of rooms |
|---|---:|
| not an L at all | 0.4342 |
| **an L, but a leg is below ADR 0014's floor** | 0.2319 |
| **an L, both legs legal, the greedy naming missed it** | **0.0205** |

So the bound is **about two points of rooms wide, not thirty-seven**. The gap
between the 9.85 % of Swiss rooms offered a second rectangle here and ADR 0014's
*"47 % need two or more"* is almost entirely two things that are not
conservatism: the watershed raster is blockier than the room polygon, and
**23.2 % of rooms are Ls whose short leg is under 900 mm clear**, which ADR 0014
refuses on purpose — *below that it is not a leg of a room, it is a niche.* That
is the rule working.

⚠️ One residual is genuinely unmeasured: the naming is **room-local**, and a Room
whose best *global* fit wants a non-maximal first rectangle is invisible to it.
Only a Design B run could see that, and §11.5 is why there is none.

### 11.2 Where the gain lands — the 4-versus-10-room asymmetry collapses

This is the half that matters more than the headline. ADR 0008's cost fell
"where the corpus can least afford it" (§6.3): 83 % of 4-room dwellings converted
against 46 % of 10-room, thinning retrieval's index hardest in exactly the band
`proposer.md` §2.1 already showed weakest.

| rooms | dwellings | k = 1 | k ≤ 2 | delta |
|---:|---:|---:|---:|---:|
| 4 | 193 | 0.8290 | 0.9482 | +0.1192 |
| 5 | 377 | 0.8700 | 0.9576 | +0.0875 |
| 6 | 527 | 0.8159 | 0.9336 | +0.1176 |
| 7 | 515 | 0.7049 | 0.9126 | +0.2078 |
| 8 | 499 | 0.5551 | 0.8677 | +0.3126 |
| 9 | 333 | 0.4985 | 0.8498 | **+0.3514** |
| 10 | 115 | 0.4783 | 0.8261 | **+0.3478** |

**The gain rises monotonically with room count**, and the spread across the band
goes from **35 points** (0.829 → 0.478) to **12** (0.948 → 0.826). A 10-room
dwelling converted 46 % of the time and now converts 83 % — what a 4-room
dwelling managed before. ResPlan is flatter and moves the same way: every room
count lands between 0.90 and 1.00 where it ran 0.46–0.65.

The conversion has stopped being a filter that prefers small dwellings. **The
percentage was never the point; the slope was.**

### 11.3 Fidelity improves, and every ADR 0008 guarantee holds

Measured on the dwellings **both** arms convert, so the comparison is not
contaminated by the newly-gained ones.

| | Swiss k = 1 | Swiss k ≤ 2 | ResPlan k = 1 | ResPlan k ≤ 2 |
|---|---:|---:|---:|---:|
| cell agreement | 0.9008 | **0.9397** | 0.7617 | **0.8710** |
| median room IoU | 0.8900 | **0.9412** | 0.6773 | **0.8713** |
| **worst room IoU** | 0.6176 | **0.7742** | 0.2308 | **0.5714** |
| mean \|area error\| | 0.0513 | 0.0441 | 0.0663 | 0.0590 |
| **adjacencies lost** | **0** | **0** | **0** | **0** |
| **relations flipped** | **0** | **0** | **0** | **0** |
| **relations weakened** | **0** | **0** | **0** | **0** |
| solve seconds | 0.69 | 1.16 | 1.01 | 10.04 |

Nothing is traded. The number to look at is the **worst room in a dwelling**: it
gains 0.157 of IoU on Swiss and **0.341** on ResPlan. That is the room that used
to be squeezed into a box that did not fit it, and on ResPlan it was previously
getting less than a quarter of itself right.

**Zero adjacencies destroyed, zero separation directions flipped and zero
weakened, across 69,040 Swiss and 22,940 ResPlan axis-pairs.** These are
guarantees of the formulation rather than of the rectangle count, and ticket 40
was told they must still hold. `validate_k2.py` re-derives them and the ADR 0014
predicates — leg floor, join, non-overlap, the symmetry break — from the emitted
geometry, sharing no code with the model: **17,283 parts over 2,317 dwellings,
1,543 Rooms of two rectangles, zero failures.**

### 11.4 The relations the conversion has to invent, for ticket 23

ADR 0008 adds a separation assertion on the axis-pairs the truth **abstained**
on, because one rectangle must pick a side when a room wraps another. *The
retrieval index and warp procedure* flags those as the pairs a warp is least
entitled to trust. An L does not have to pick a side.

| | same | **spurious** | weakened | flipped |
|---|---:|---:|---:|---:|
| Swiss k = 1 | 0.8436 | **0.1564** | 0 | 0 |
| Swiss k ≤ 2 | 0.8642 | **0.1358** | 0 | 0 |
| ResPlan k = 1 | 0.7948 | **0.2052** | 0 | 0 |
| ResPlan k ≤ 2 | 0.8570 | **0.1430** | 0 | 0 |

Swiss falls 15.64 % → 13.58 %, ResPlan 20.52 % → 14.30 %. Real, and smaller than
the conversion-rate move: **the second rectangle rescues dwellings more than it
disambiguates pairs.** Ticket 23 should still expect roughly one axis-pair in
seven to be an assertion the corpus never made, and item 4's per-room confidence
still has to mark them.

### 11.5 ⚠️ Design B is not measurable at the shipped budget, and that is a finding

The obvious rig — give **every** Room an optional second rectangle and let the
fit decide — was built first and abandoned on measurement. Over 40 dwellings at
the shipped 10 s limit:

| arm | s/dwelling | OPTIMAL | FEASIBLE | INFEASIBLE | UNKNOWN |
|---|---:|---:|---:|---:|---:|
| **B** — every Room free | 10.38 (capped) | **0** | 26 | **0** | 14 |
| **A** — the real room names its Ls | 3.64 | 30 | 6 | 3 | 1 |
| k = 1 control | 0.85 | 31 | 0 | 9 | 0 |

**Design B proves nothing about any dwelling.** Zero optimal and zero infeasible
means the reject rule has stopped existing: `converted` degrades to *found
something in 10 s*, and ADR 0008 §4's **"the tier is decidable, not a timeout"**
is false in that arm. This is ADR 0014's *"Design A pays for the parts it uses;
Design B pays for the parts it might use"* — its 11–12× against 1.2–1.7× —
reproduced on a different solver with a different objective.

⚠️ So no measurement on this map has ever priced an unconstrained k ≤ 2
conversion, and none affordably can. §11.1 bounds what that costs at ~2 points of
rooms.

### 11.6 The conversion may choose k where the solver may not, and now the corpus says so

ADR 0014 refuses to let the **solver** grow its own second rectangle, on evidence
that it puts them on the wrong rooms — Spearman **+0.795** against the corpus,
positive being the wrong sign. The conversion is a different case and the ADR
says why: its objective is **misassigned cells against the real room**, so the
ground truth is the taste. That was an argument. This is the measurement.

| room type | rooms | conversion fits 2 | ADR 0014's free **solver** |
|---|---:|---:|---:|
| LIVING_DINING | 1,358 | **0.4219** | — |
| CORRIDOR | 2,952 | **0.2202** | 0.100 |
| LIVING_ROOM | 483 | 0.1718 | — |
| ROOM | 4,549 | 0.0290 | — |
| KITCHEN | 2,484 | 0.0238 | 0.179 |
| BEDROOM | 1,223 | 0.0213 | 0.295 |
| STOREROOM | 653 | 0.0046 | 0.338 |
| BATHROOM | 3,788 | 0.0034 | 0.282 |

**The ordering is inverted, which is the right answer.** The free solver reached
hardest for stores, bedrooms and bathrooms and least for corridors; the
conversion does the opposite, and its top two are the open-plan living/dining
room and the corridor — the two types §4 already identified as the corpus's
non-rectangular ones (26–30 % rectangular against 69–72 % for bedrooms and
stores). *An L-shaped corridor is L-shaped to reach a wing*, now measured being
one 22 % of the time.

**98.5 % of offered second rectangles are used** (1,543 of 1,551), so the naming
is not merely permissive: where it names an L, the fit wants one.

### 11.7 What is still dropped is a different population

`survivorship.py`, both arms, joined against `swiss_rects.json`.

| over-represented in the dropped set | k = 1 | k ≤ 2 |
|---|---:|---:|
| STOREROOM | 1.71× | 1.57× |
| BEDROOM | 1.25× | 1.25× |
| **LIVING_DINING** | **1.37×** | **1.02×** |
| bbox overlap fraction, dropped ÷ converted | 2.90× | 2.07× |
| median rooms, converted vs dropped | 6 vs 8 | 7 vs 8 |
| median m², converted vs dropped | 71.7 vs 89.9 | 76.4 vs 91.0 |

**The living/dining over-representation is gone** — 1.37× → 1.02×, on exactly the
type that takes a second rectangle most often (§11.6). The L absorbs the
interlocked open-plan dwellings ADR 0008 was losing, which ticket 40 predicted
off the ablation and is here measured directly rather than inferred.

What remains dropped is **storeroom- and bedroom-heavy**, and naming it is worth
more than the percentage: it is no longer *"the dwelling with a wrapped living
room"*, it is *"the dwelling with several small interlocked ancillary rooms"*. A
store is 72 % rectangular (§4) and is being dropped anyway, so its cause is **not
its own shape** — it is that a dwelling carrying several of them has more pairs
to satisfy at once. ADR 0008's size bias narrows without closing.

### 11.8 The fidelity ladder no longer earns its complexity

`ablate.py 250 --k2`. ADR 0008's tiers **are** these arms, so re-running the
ablation is how the ladder gets re-measured rather than a separate exercise.

| arm | tier | k = 1 | k ≤ 2 |
|---|---|---:|---:|
| **as shipped** | **A** | 0.7360 | **0.9320** |
| area band ±25 % | — | 0.9080 | 0.9760 |
| area free | — | 0.9120 | 0.9800 |
| up to 4 notches | — | 0.6680 | 0.8800 |
| **relations, neighbours only** | **B** | 0.8200 | **0.9520** |
| no hard adjacency | — | 0.9560 | 0.9920 |
| **no hard relations** | **C** | 0.9375 | **0.9250** |
| **relations + adjacency off** | **D** | 1.0000 | **1.0000** |

**The ladder spans 6.8 points where it spanned 26.4.** Tier A alone now reaches
0.9320, so B and C exist to rescue single-digit fractions of the corpus:
**A → B buys 2.0 points**, against 8.4 at one rectangle.

⚠️ **And tier C is now *below* tier A** — 0.9250 against 0.9320. That is not a
paradox and it is not noise: dropping the hard relations removes the pruning that
makes the search tractable, so the arm times out (**5 UNKNOWN of 80**, against 1
at k = 1). **Tier C is unmeasurable at k ≤ 2 for the same reason Design B is**,
and a rung that cannot be measured cannot be a rung.

So the ladder is reduced to **two rungs, A and D** — see ADR 0015. Retrieval's
gate is unchanged and untouched by this; what goes is a four-valued conditioning
field that is now 93 % one value and whose two middle rungs no longer separate
anything.

**The ticket's own prediction is confirmed, and it was the right prediction.**
It reasoned from the k = 1 ablation that *hard adjacency is the dominant reject
cause* and that k ≤ 2 would attack it directly, because *"an L is precisely the
shape that reaches an adjacency a rectangle cannot: a corridor that wraps a wing
touches rooms on two sides of it."* Adjacency's grip falls from **+22.0 points to
+6.0**, and the area band's from **+17.2 to +4.4**. Both dominant causes are
mostly gone, and they were the same cause wearing two coats: a room shape that
could not reach.

⚠️ **ADR 0008 consequence 7 survives unchanged**: four notches still converts
*worse* than two, 0.8800 against 0.9320. A more articulated Envelope is harder to
tile whatever the rectangle count, so the cap is evidenced twice now.

### 11.9 What this section does not establish

**Nobody has looked at a k ≤ 2 converted dwelling.** Every number here is a
statistic over 3,600 fits; *Look at the converted corpus* is still owed, and is
now owed against a conversion whose shapes are different from the ones it was
written for.

**371 of 2,317 Swiss and 594 of 936 ResPlan conversions are FEASIBLE rather than
OPTIMAL**, so their reported loss is an **upper** bound on the true loss — §11.3
understates k ≤ 2 rather than flattering it. At k = 1 essentially everything
proved optimal.

**Conversion now costs 4.3× the CPU** — 3.65 s/dwelling against 0.85 on Swiss,
and ResPlan needs 30 s to decide every plan where 10 s left 16.5 % open. ADR 0008
consequence 5's ~17 CPU-hours for both corpora becomes roughly **70**.

**The 250 mm watershed is unchanged**, so §10's two defects stand exactly as
written: door-width adjacency is still the only adjacency measured, and interior
shafts are still handed to habitable rooms. A second rectangle does not give the
Envelope an interior obstacle.
