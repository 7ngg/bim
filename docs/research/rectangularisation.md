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
[0016](../adr/0016-the-conversion-names-its-own-ls.md).

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

So the ladder is reduced to **two rungs, A and D** — see ADR 0016. Retrieval's
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

---

## 12. ⚠️ Three of §11's fidelity headlines are constraints restated

*Look at the converted corpus* (ADR
[0017](../adr/0017-three-of-the-conversions-fidelity-headlines-are-constraints-restated.md))
rendered 67 converted dwellings beside their originals. The verdict is that a
converted dwelling **reads as a home** — but the looking also found that three of
the numbers this document quotes as fidelity results are the *constraint set*
restated, and they must stop being cited as evidence.

Each is posted **hard** in `fit_rects`, so a dwelling that would violate it is
**refused** rather than converted, and the resulting zero measures the constraint:

| quoted here as | what it actually is |
|---|---|
| §11.3 *"adjacencies destroyed, 0 of 17,367"* | contact is a hard constraint. **"Zero adjacencies destroyed" and "9.5 % refused" are one fact stated twice.** |
| §11.3 / §11.4 *"0 weakened, 0 flipped"* | the true relations are posted hard. §3 already says this — *"with them, flipped and weakened are both exactly zero **by construction**"* — but the summary tables at §11.3 and §11.4 repeat the zeros without it. |
| §11.3 per-room area error inside ±10 % | the band **is** ±10 %, posted hard. p99 of \|aerr\| is 0.111. |

§11.3 does say these are *"guarantees of the formulation rather than of the
rectangle count"*. That is correct and is not enough: read from the summary
tables alone they look like measurements, and they have been quoted that way on
the map.

**What is genuinely free, and therefore quotable:** `cell_agreement`, the IoU
distribution, **the refusal rate**, and `boundary_lost`.

### 12.1 Cell agreement never travels alone

Checked against the eye, cell agreement is honest — it ranks dwellings the way
looking at them does (rank correlation **0.825** with worst-room IoU), and of the
69.6 % of conversions scoring ≥ 0.90 only **0.8 %** hide a room at IoU ≤ 0.30. But
it averages over cells and a person looks at the worst room, and at a fixed
agreement the worst room is wide:

| cell agreement | dwellings | worst-room IoU p10 | median | p90 | share ≤ 0.30 |
|---|---:|---:|---:|---:|---:|
| 0.95–1.00 | 922 | 0.74 | 0.90 | 0.96 | 0.1 % |
| 0.88–0.92 | 410 | 0.45 | 0.68 | 0.82 | 2.9 % |
| 0.78–0.84 | 180 | 0.23 | 0.47 | 0.67 | 17.2 % |
| < 0.78 | 156 | 0.00 | 0.25 | 0.47 | 58.3 % |

**Publish worst-room IoU beside every cell agreement.**

### 12.2 §11.4's spurious rate is the paired one, and there is a second

§11.4 gives Swiss k ≤ 2 as **0.1358**. That is over the **1,779 dwellings both
arms converted** — the right number for measuring what the second rectangle
bought, and the wrong one for describing the corpus. Over **all 2,317
conversions and 97,090 axis-pairs** the rate is **0.1262**.

The gap is not rounding. The 538 dwellings k ≤ 2 rescued and k = 1 refused carry
a *lower* spurious rate than the ones both arms managed, so rescuing them
improved the corpus twice over. **Ticket 23 should use 0.1262** — roughly one
axis-pair in eight, not one in seven.

⚠️ **And §11.4's explanation of what a spurious relation *is* is wrong.** It says
ADR 0008 *"adds a separation assertion on the axis-pairs the truth abstained on,
because one rectangle must pick a side when a room wraps another."* By
construction a `spurious` relation is a pair whose bounding boxes **overlapped**
on that axis and no longer do after squaring — the truth abstains because the
projections overlap, and squaring resolves the overlap. Wrapping is one cause of
overlap and not the only one. Rendered, the picks read as what a person would
draw; the caution ticket 23 is owed stands, but the reason is *overlap resolved*,
not *side picked*.

### 12.3 Two things the rendering found that no number here reports

**Floor no Room claims.** Exact tiling is soft, so an Envelope cell no Room takes
is legal. Measured over 400 dwellings by `void_census.py`, splitting the
Envelope's deliberate notch under-cut (correctly empty) from real floor: median
**1.19 m²** of real dwelling floor unclaimed, and **10.0 % of dwellings carry an
*enclosed* void ≥ 0.5 m²** — a room-shaped hole with walls round it and no name.
Invisible here because `uncovered` sums the correct case and the incorrect one.
Handed to the acceptance bar.

**Off-frame wings.** `dwelling_frame` rotates a dwelling onto one angle. A
dwelling built on two is sheared into a *different flat* — ~~1.5 % of dwellings~~
have a room off frame by 10–20°, scoring cell agreement 0.705 with worst-room IoU
~~0.167~~, and they come back **OPTIMAL** while doing it. Ticketed as *The
dwelling that is built on two angles*.

⚠️ **Both struck figures are 400-dwelling artefacts; §15 re-measures on all 2,317.**
The population is **4.79 %** at ≥ 10° and the 10–20° band's worst-room IoU is
**0.397**. §15.1 also finds that the shipped `worst_room_iou` gate was already
refusing 39.6 % of it.

Harness: `render_sheet.py`, `void_census.py`. Sheets at `out/sheets/SHEET.html`.

---

## 13. The Envelope loss tail is two populations, and neither is a notch budget

Ticket 47 held ADR 0003's two-notch cap. §6.4 and ADR 0017 failure mode 4 had
already vindicated the *number* — two notches is the knee of its own ladder and
raising the cap makes the conversion worse — and had characterised what is left
as outlines that *"are not bounding-box-minus-notches at any count"*. That
sentence was a characterisation, not a measurement. `envelope_family.py` measures
it, off the cached fit in seconds, and the characterisation is right for the
wrong reason.

### 13.1 The residual is a non-rectangular complement, not an un-budgeted notch

283 of 2,592 fitted dwellings (**10.92 %**) lose more than 0.10 of envelope area
at k = 2. Split them by how many notches their complement would need at all —
`notches_all`, components ≥ 0.25 m², the same count §6.4 laddered:

| tail class | n | median loss k = 2 | k = 3 | k = 4 | still > 0.05 at k = 4 |
|---|---:|---:|---:|---:|---:|
| already within the cap (`notches_all` ≤ 2) | 16 | 0.1303 | 0.1193 | 0.1193 | **100 %** |
| would need 3–4 | 180 | 0.1313 | 0.1018 | 0.1014 | 86.7 % |
| would need 5+ | 87 | 0.1562 | 0.1192 | 0.1106 | 91.9 % |

**Sixteen dwellings are inside ADR 0003's cap already and still lose more than a
tenth of their envelope**, and at `notches_all` = 1 the loss is *identical at
every k* — 0.1025 at k = 1, 2, 3 and 4. A notch is one **rectangle**; a
complement *component* need not be one. Where the component is L-shaped, stepped
or chamfered, the budget is not what binds, and no value of k ever was.

This is the mechanism §6.4's flat curve only showed the shape of.

### 13.2 Half the tail is not rectilinear at all

Share of the dwelling outline's length lying more than 2° off both axes, measured
in the dwelling's own frame — the same frame the fit uses, so this is off-axis
*after* `dwelling_frame` has done its best. Segments under 0.10 m are ignored as
digitisation.

| | n | median off-axis | share > 10 % off-axis |
|---|---:|---:|---:|
| tail (loss > 0.10) | 283 | **0.0939** | **49.5 %** |
| rest | 2,309 | 0.0000 | 3.8 % |

The corpus splits three ways, and envelope loss tracks the split almost perfectly:

| outline class | n | share of corpus | median loss k = 2 | > 0.10 at k = 2 | share of the tail it holds |
|---|---:|---:|---:|---:|---:|
| rectilinear (≤ 2 % off-axis) | 2,102 | 81.10 % | 0.0131 | 5.1 % | 38.2 % |
| mixed (2–10 %) | 263 | 10.15 % | 0.0376 | 13.3 % | 12.4 % |
| off-axis (> 10 %) | 227 | 8.76 % | 0.1223 | **61.7 %** | **49.5 %** |

**8.76 % of the corpus holds half the tail.** These are the chamfered, angled and
curved outlines, and they are the same failure §9.1 found one level down at room
scale — an angled wall becomes a staircase at 250 mm and no k fixes it.

### 13.3 What a wider shape family could buy, priced

Ticket 47's option 3 splits in two, and only one half is even coherent:

- **A general rectilinear ring with a vertex budget** — not more notches, but
  arbitrary rectilinear vertices — would express the *rectilinear* tail. That
  population is **108 dwellings, 4.17 % of the corpus**: rectilinear outline,
  loss > 0.10 at k = 2, and **46.3 % of them still above 0.10 at k = 4**. Their
  `notches_all` is 3 or 4 in 71 % of cases, so they are ordinary L/T/U dwellings
  whose complement happens not to decompose into two rectangles.
- **Chamfered or angled edges** would be needed for the other half, and break
  axis alignment for the 250 mm grid, `AddNoOverlap2D` and every dimension chain.

**4.17 % is the whole ceiling of the rectilinear widening**, and it is bought at
the cost of ADR 0003's typed edges. The decision is ADR 0003's amendment: refused.

### 13.4 Envelope loss is a predictor, and it is a poor gate

ADR 0017 calls envelope loss the best predictor of conversion quality measured.
It is — and the predicted quantity, **worst-room IoU**, is in the same fit
record, so there is no reason to act on the predictor. Over the 2,317 **converted**
dwellings, which is what the retrieval index actually holds:

| gate | keeps | median worst-room IoU kept | dropped |
|---|---:|---:|---:|
| envelope loss ≤ 0.20 | 98.06 % | 0.763 | 0.293 |
| envelope loss ≤ 0.10 | 90.07 % | 0.779 | 0.452 |
| envelope loss ≤ 0.06 | 77.43 % | 0.807 | 0.594 |
| worst-room IoU ≥ 0.30 | 93.35 % | — | — |
| worst-room IoU ≥ 0.50 | 82.82 % | — | — |

**The proxy errs in both directions.** 42.2 % of the envelope-loss tail has a
worst-room IoU at or above 0.50 — faithful conversions of unfaithful outlines —
and 12.70 % of everything *outside* the tail is below 0.50. An IoU < 0.50 cut
removes **10.09 %** of the most faithful envelope band (loss < 0.01): dwellings
whose outline the Envelope describes exactly and whose rooms the fit still got
wrong. No envelope-loss threshold can see them.

The population that matters is its own:

| | n | share of index |
|---|---:|---:|
| worst-room IoU < 0.30 | 154 | **6.65 %** |
| — of those, envelope loss > 0.10 | 55 | 35.7 % |
| — of those, outline > 10 % off-axis | 51 | 33.1 % |

Two thirds of it is invisible to either proxy.

And the better gate subsumes the off-axis finding rather than competing with it:
off-axis dwellings carry a median worst-room IoU of **0.522** against the
rectilinear 0.777, with 26.0 % below 0.30 against 4.5 %. §12.3's sheared
dwellings — cell agreement 0.705, worst-room IoU 0.167, returning OPTIMAL — are
in that 26.0 %.

### 13.5 What this section does not establish

- **Every number is Swiss.** ResPlan is fitted (`resplan_fit_k2.json`) but was
  not measured here; §6.5 already shows it converts markedly worse, so the tail
  shares are a lower bound for the ResPlan arm rather than a transfer.
- **Off-axis is measured on the *outline*, not per room.** §12.3's 1.5 % counts a
  room off frame by 10–20°; the 8.76 % here counts perimeter length off both
  axes at the dwelling scale. They are different populations and the larger one
  is handed to *The dwelling that is built on two angles*.
- **The 0.30 threshold is fitted to a published cost, not derived.** 6.65 % of
  the index is what it removes; the corpus's own worst-room IoU p10 is 0.369 and
  p5 is 0.241. It is `conf: fitted` in ADR 0023's vocabulary, not `verified`.
- **Nothing here re-prices the ablation.** The *"up to 4 notches"* arm's 88.0 %
  against 93.2 % (§6.4, `out/ablate_k2.log`) is quoted, not re-run.

Harness: `envelope_family.py`, log at `out/envelope_family.log`.

## 14. A real outline is not an Envelope, and the gap is structural

Ticket 58. ADR 0003 fixes v1's Envelope as a rectilinear ring — a bounding box
minus at most two notch rectangles — and ADR 0029 fitted a second toy family to
real dwellings on **area, perimeter and bounding-box occupancy**. Three moments
matched is not a boundary matched, and nothing on this map had ever asked what a
real outline costs *as a shape*. §13 answered the neighbouring question — what
the loss tail is made of — and left this one.

The quantity here is the **minimum number of rectangles that partition a real
dwelling's interior**, computed exactly rather than greedily: reflex vertices
minus the maximum set of pairwise non-crossing chords minus holes, plus one
(Lipski/Ohtsuki), with the chord independence taken as |H| + |V| − maximum
bipartite matching. Verified against eight hand-checkable shapes before it was
quoted — and on two of them the *hand* expectation was the wrong one, which is
the reason to write the check down: a T is two rectangles, not three, and so is
a bbox with two opposite corner notches. The boundary is not re-derived: it is
`keep_largest_component(watershed(geoms)) >= 0`, the same 250 mm cell mask
`envelope_approx` measures §6.4's notch loss against, so every figure below is
comparable with `notches_all` and `envelope_loss_by_k` in the same record.

400 dwellings in fit order; **364 converted** (OPTIMAL or FEASIBLE), which is the
population that becomes a donor. **Every rate below is on the converted index**
unless a row says otherwise — that is the set a Proposal is ever drawn from. The
whole-400 figures move nothing by more than two points and the direction is
always the same, so nothing here turns on the choice.

### 14.1 The headline

> **A real dwelling's interior needs a median of 6 rectangles. ADR 0003's family
> produces between 1 and 4 parts. 12,4 % of the index comes in at 3 or fewer.**

| min rectangles | p25 | median | p75 | p90 | max |
|---|---:|---:|---:|---:|---:|
| all 400 | 4 | **6** | 9 | 12 | 44 |
| converted index (364) | 4 | **6** | 9 | 12 | 44 |

| cumulative share of the index | ≤ 1 | ≤ 2 | ≤ 3 | ≤ 4 | ≤ 6 | ≤ 8 | ≤ 12 |
|---|---:|---:|---:|---:|---:|---:|---:|
| | 1,4 % | 4,7 % | **12,4 %** | 26,9 % | 55,2 % | 72,5 % | 91,5 % |

Both shipped fixtures measure on the same scale, which is what makes the gap
readable rather than merely large:

| fixture | n | `Envelope.parts` | min rectangles | reflex vertices |
|---|---:|---:|---:|---:|
| published | 8 / 12 / 24 | 2 | **2** | 1–2 |
| corpus (ADR 0029) | 5 | 2 | **2** | 1 |
| corpus (ADR 0029) | 6–11 | 4 | **4** | 3 |
| **real dwelling** | 3–12 | — | **6** median, 12 at p90, 44 max | **6** median, 15 at p90 |

ADR 0029's fixture is a real improvement on this axis too — 4 against the
published 2 — and it is still at the corpus's **p25**. The three moments it was
fitted on do not carry the fourth.

The count rises monotonically with the notch count §6.4 laddered and with the
envelope loss §13 anatomised, which is the cross-check that it is measuring the
same thing from a different direction:

| `notches_all` | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---:|---:|---:|---:|---:|---:|
| n (index) | 5 | 28 | 95 | 114 | 75 | 31 |
| median min rectangles | 1 | 3 | 5 | 6 | 8 | 9 |
| median envelope loss at k = 2 (all 400) | 0,0000 | 0,0010 | 0,0066 | 0,0197 | 0,0380 | 0,0388 |

The envelope-loss tail (> 0,10, n = 29 in the index) needs a median of **14**.

### 14.2 Two gates the toy harness cannot pass on a real outline

`Envelope.parts` is a disjoint rectangular decomposition of the interior, and
`scenarios.ground_truth` gives **every part at least one room** before
dissecting it. Two consequences follow directly from §14.1 and neither is about
the solver.

**39,3 % of the index needs more rectangles than it has rooms**, so
`ground_truth` refuses them before any dissection is attempted. It eases only
slowly with size — the constraint is articulation, and articulation grows too:

| engine rooms | 3–5 | 6–7 | 8–9 | 10–12 |
|---|---:|---:|---:|---:|
| n | 90 | 147 | 117 | 10 |
| median min rectangles | 5 | 6 | 7 | 8 |
| share with min rectangles ≤ rooms | 54,4 % | 61,2 % | 63,3 % | 80,0 % |

The 10–12 cell holds ten dwellings and is quotable as a direction, not a rate.

**And the parts cannot hold rooms.** Two partition heuristics that fail in
opposite directions — greedy largest-inscribed-rectangle, which takes the fattest
piece first and leaves the residue thin, and the full-height slab partition
`envelope_fit.build` itself emits — agree, and both matched the theoretical
minimum count at the median:

| | every part clears `_leaf_ok` (1,0 m / 3,0 m² / aspect 4) | median share of parts failing it |
|---|---:|---:|
| greedy | 3,3 % | 66,7 % |
| slab | 3,9 % | 71,4 % |

Held to the floor a habitable room actually needs — `envelope_fit.MIN_COL`, the
2,75 m `living` column — **1,4 % of the index** has every part wide enough.

Neither heuristic proves a room-sized partition impossible; a minimum partition
is free to emit slivers and these two are not exhaustive. What they establish
jointly is that no obvious partition finds one, which is the fact the harness
needs, because the harness has no search for a good one either.

### 14.3 The outline is stepped, not holed, and it does not pinch

| | index (364) | all 400 |
|---|---|---|
| reflex vertices, median / p90 | 6 / 15 | 7 / 15 |
| dwellings with an enclosed hole | **2,2 %** | 2,0 % |
| dwellings whose boundary touches itself | 0,0 % | 0,0 % |

The 2,2 % sits beside ADR 0028's finding from the opposite side — ticket 53
measured **2,0 %** of enclosed-void *area* lying inside a dropped `SHAFT` /
`VOID` / `TECHNICAL_AREA`, and this counts the *dwellings* whose outline
topologically encloses one. The agreement is a coincidence of two small numbers
and must not be quoted as one figure confirming the other; what it does say is
that the articulation §14.1 measures is **stepped perimeter**, not perforation,
so a shape family with more notches was never the missing piece. §13.1 reached
the same conclusion from the loss side.

### 14.4 A converted dwelling is not a witness for its own boundary

This is the trap ticket 58 hit, and it is worth recording because it reads like
a coordinate bug and is not one. `swiss_fit_k2.json`'s rectangles are fitted to
the **cap** Envelope — bbox minus at most two notches — which is a *superset* of
the true outline. Handed to the validator against the true outline they fail two
hard predicates at once: **H1**, a Room poking into ground the dwelling never
occupied, and **H3**, cells no rectangle reaches. Seven of the first eight real
slots were invalid that way.

`real_envelope.refit_to_true_mask` re-runs the shipped conversion with the domain
set to the true mask instead. `fit_rects.py` is **not edited** — the substitution
is at the call boundary, because that file is the conversion four closed
decisions rest on and this needed a different domain, not a different conversion.
The result is inside the boundary by construction; the residue is ADR 0028's
enclosed void, and it is why the resulting witness is coverage-soft rather than
exact.

**The re-fit is materially harder than the cap fit**, and this is the first
measurement of it: over 71 in-band converted dwellings, **11 (15,5 %) could not
be re-fitted to their own boundary** at the same 10 s budget — 9 INFEASIBLE and 2
UNKNOWN — where the cap fit had decided every one of them. Runtime roughly
doubles, 0,8 s/dwelling to ~2. That is a fact about the domain, not about the
solver.

The witness that survives covers a median **93,8 %** of the true interior (p10
84,3 %, p90 97,8 %) and spills outside it **not at all** at every decile, which
is the guarantee the re-fit buys and the recorded fit cannot give. **68,3 %** of
dwellings reach a witness that both covers ≥ 90 % and spills ≤ 5 %.

### 14.5 What this section does not establish

- **That the shipped Envelope is wrong.** ADR 0003's object is a *design*
  choice with its own evidence (§6.4, ADR 0003's second amendment). §14 measures
  the distance between it and a real outline; it does not price widening it, and
  §13.3 already refused the widening on separate evidence.
- **That no room-sized partition exists.** Two heuristics failed to find one.
  Neither is a proof, and no exhaustive search was run.
- **Anything outside 5–11 engine rooms.** The re-fit and the solver arm are both
  scoped to the band ADR 0029's corpus fixture serves.
- **Anything about ResPlan.** Swiss only, as §13.5.
- **That the minimum partition is the right partition.** It is the floor on part
  count. A partition that *also* satisfies `_leaf_ok` everywhere may need more
  rectangles than the minimum, which would make §14.2 worse, never better.

Harness: `real_boundary.py` (representability, series at
`series/real_boundary.json.gz`) and `real_envelope.py` (the two Envelopes and
the re-fit, series at `series/real_envelopes.json.gz`); logs in `out/`.

---

## 15. The dwelling built on two angles, and the gate that was already refusing it

Ticket 46. ADR 0017 failure mode 1: `dwelling_frame` rotates a dwelling onto
**one** angle — the minimum rotated rectangle of the whole room union — so a
dwelling built on two, a wing splayed off a spine, has every room in the second
wing sheared into the first wing's frame. The output is a plausible home and it
is not the home that was converted. It came back **OPTIMAL** while doing it.

Everything below is on the **full 2,317-dwelling converted index**. ADR 0017's
own table is on 400, and the difference matters in one place — §15.5.

### 15.1 The headline

> **The population is 4,79 % of the index, and the shipped `worst_room_iou`
> gate is already refusing 39,6 % of it. 28,6 % of everything that gate
> removes is off-frame — the map has been refusing two-angle dwellings since
> the gate landed, unlabelled, and nobody knew.**

`proposer.md` §2.2.4 gates the retrieval index at `worst_room_iou ≥ 0,30`,
hard, at a stated cost of 6,65 % of the index. `off_frame_gate.py` joins the
off-frame measurement to that gate's own quantity and **reproduces the 6,65 %
exactly**, which is what makes the join trustworthy rather than merely
plausible.

| off frame by | n | share | worst_iou med / p10 | already gated |
|---|---:|---:|---:|---:|
| 0–2° | 2 063 | 89,0 % | 0,778 / 0,421 | 4,4 % |
| 2–5° | 61 | 2,6 % | 0,699 / 0,262 | 14,8 % |
| 5–10° | 82 | 3,5 % | 0,618 / 0,197 | 13,4 % |
| **10–20°** | **61** | **2,6 %** | **0,397 / 0,070** | **39,3 %** |
| **20°+** | **50** | **2,2 %** | **0,353 / 0,087** | **40,0 %** |

|  | below the gate | at or above |
|---|---:|---:|
| off frame ≥ 10° | **44** | **67** |
| off frame < 10° | 110 | 2 096 |

**The residue is 67 dwellings — 2,89 % of the index** — that are ≥ 10° off frame
and pass every fidelity check the index has. That is the population this ticket
is actually about, and it is half the size the ticket assumed.

### 15.2 Off-frame is informative beyond `worst_room_iou`, and that is why it is published

The obvious objection to publishing anything is that the record already holds a
fidelity quantity and off-frame is merely a cause of it. It is not: at **every**
stratum of `worst_room_iou`, an off-frame dwelling scores materially lower cell
agreement than an on-frame one at the same IoU.

| `worst_iou` band | on frame (< 10°) | off frame (≥ 10°) | delta |
|---|---:|---:|---:|
| 0,30–0,45 | 0,841 (n = 152) | 0,731 (n = 24) | **−0,110** |
| 0,45–0,60 | 0,883 (n = 241) | 0,809 (n = 21) | −0,074 |
| 0,60–0,75 | 0,920 (n = 509) | 0,832 (n = 16) | −0,088 |
| 0,75–1,01 | 0,965 (n = 1 194) | 0,911 (n = 6) | −0,054 |

`worst_room_iou` is a **per-room minimum** and the shear is a **whole-dwelling**
defect, so the first cannot be a sufficient statistic for the second. The
quantity is not redundant and the record does not hold it.

### 15.3 `frame_residual` — the quantity, and why it is not the ticket's

The ticket names the field and does not define it. Three candidates were
measured and the difference decides where any cut would land:

- **`off_frame_max`** — the largest per-room deviation, which is what
  `void_census.py` and ADR 0017 report. A one-room statistic on a
  whole-dwelling defect.
- **off-frame area mass** — the area share of rooms more than 5° off. Stops a
  2 m² store counting like a 30 m² living room, and **buries a 5° threshold
  inside a field that is supposed to be raw**.
- **`frame_residual`** — the **area-weighted mean deviation of a dwelling's
  rooms from its dwelling axis, in degrees**. Continuous, whole-dwelling, and
  carrying no free parameter, which is the same ground §2.2.4 gave for
  partitioning `frontage_reach` at 1,0 rather than fitting a weight.

The third is what is published. Its distribution on the shipped frame:

| `frame_residual`, degrees | p50 | p75 | p90 | p95 | p99 | max | mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| shipped union-mrr frame | 0,000 | 0,057 | 0,834 | 2,845 | 9,822 | 23,75 | 0,489 |
| area-weighted modal frame | 0,000 | 0,021 | 0,507 | 2,043 | 7,410 | 21,37 | 0,347 |

**A cut placed on `off_frame_max` does not transfer to this quantity**, which is
why §15.4 places it here rather than inheriting ADR 0017's 10°.

### 15.4 There is no knee, and that is the finding

Cell agreement against the residual, over the 2 163 dwellings that survive the
IoU gate:

| residual | n | share | cell agr. med / p10 | `worst_iou` med | pool percentile |
|---|---:|---:|---:|---:|---:|
| 0,0–0,5° | 1 949 | 90,1 % | 0,944 / 0,857 | 0,787 | 52,4 |
| 0,5–1,0° | 62 | 2,9 % | 0,914 / 0,809 | 0,745 | 45,7 |
| 1,0–2,0° | 61 | 2,8 % | 0,891 / 0,767 | 0,732 | 41,1 |
| 2,0–4,0° | 42 | 1,9 % | 0,854 / 0,763 | 0,603 | 22,4 |
| 4,0–8,0° | 33 | 1,5 % | 0,802 / 0,706 | 0,489 | **10,6** |
| 8,0–16,0° | 13 | 0,6 % | 0,778 / 0,647 | 0,562 | 16,7 |
| 16°+ | 3 | 0,1 % | 0,696 / 0,638 | 0,450 | — |

The decline is **smooth**. There is no elbow to place a cut on, so any partition
would be a fitted constant chosen for the look of it — the thing §2.2.4 exists to
refuse.

**The last column is why none is needed.** *Pool percentile* is where the
dwelling's `worst_room_iou` sits in the distribution of everything that survives
the gate — that is, where §2.2.4's existing pre-rank already puts it. A donor at
4–8° residual sits at the **10,6th percentile**. With a bucket of 58–87 (§2.2.7)
and `m = 8` drawn from its head, a donor at the tenth percentile is not taken.
**The rank the map already ships demotes this population to the floor of the
pool without being told to.**

### 15.5 ⚠️ ADR 0017's 0,167 is a six-dwelling artefact

Its failure-mode-1 table reports the 10–20° band at worst-room IoU **0,167** and
the 20°+ band at **0,429** — a reversal that should have been read as a sample
size. It was: the bands hold 6 and 5 dwellings of 400. Over the full index they
are **0,397** and **0,353**, monotone as expected, and the population is nearly
twice the rate ADR 0017 quotes (4,79 % against 2,7 % at ≥ 10°).

Nothing downstream turns on it — the number was never load-bearing for a
decision — but the ticket, this note's §12.3 and ADR 0017 all carried it, and a
figure quoted three times is one somebody will eventually build on.

### 15.6 The frame the conversion picks is the wrong one, and a better one is a wash in the body and a real gain in the tail

The union mrr is fitted to **both** wings, so on a two-angle dwelling the angle
it returns can be neither wing's — every room is then off frame rather than only
the minority wing's. `frame_choice.py` measures the obvious alternative: the
**area-weighted modal room angle**, which sits on the dominant wing by
construction.

Counted per dwelling it looks like a coin flip — 377 better, 357 worse. Weighed,
it is not close:

| | n | mean | sum | p90 | max |
|---|---:|---:|---:|---:|---:|
| improved | 377 | 0,923° | **347,8°** | 2,225° | 22,400° |
| regressed | 357 | 0,057° | **20,4°** | 0,137° | 1,911° |

**The regressions are estimator noise and the gains are the defect.** Net
+327,4° over 2 317 dwellings, and the modal frame dominates the shipped one at
every published quantile (§15.3). Where it changes a reading rather than a
decimal:

| | shipped | modal |
|---|---:|---:|
| residual > 2° | 6,26 % | 5,05 % |
| residual > 4° | 3,63 % | 2,37 % |
| residual > 8° | 1,64 % | 0,91 % |

At a 2° line the modal frame **rescues 29 dwellings and pushes 1 across**; at 4°,
30 against 1.

**89,2 % of the population is irreducibly two-angle** — re-framed to the modal
angle, only 12 of the 111 dwellings ≥ 10° fall under 10°. A better single frame
is a better *measurement*, not a fix, and nothing here claims otherwise.

### 15.7 Why re-framing per wing was refused without being priced

The ticket's second candidate — segment into angle-coherent components, fit each
in its own frame, reconcile — is refused on representability rather than cost.

Two frames meeting at an angle is not something ADR 0003's Envelope can express,
and §14 has just measured how far that object already is from a real outline: a
median of **6** rectangles against a family that yields 1–4. A re-framed dwelling
would be a donor for a Brief v1 cannot serve, in a shape family §13.3 has
already refused to widen on separate evidence. The reconciliation is a new
problem bought to produce an unusable result.

⚠️ **This is a refusal on scope, not a measurement**, and it is the one line in
§15 with no number under it.

### 15.8 What this section does not establish

- **What an off-frame donor costs a warped candidate.** Everything here is
  measured on the donor. The warp is `experiments/warp/`, held by another open
  ticket, and the conversion may not reach into it — so *whether a sheared
  donor produces a worse Plan*, as opposed to a worse record, is unmeasured.
  It is the honest gap in this decision and it is named on ADR 0031.
- **That the modal frame is the best frame.** It is better than the shipped one
  on this corpus. Two estimators were compared, not searched.
- **Anything about ResPlan**, which is already orthogonal and cannot carry this
  defect at all.
- **That the 5° convention in `void_census.py` means anything.** It is a
  reporting threshold inherited from ticket 27; `frame_residual` deliberately
  has none.

Harness: `off_frame_gate.py` (the join to the shipped gate),
`frame_choice.py` (the two frames) and `frame_residual.py` (the published
quantity and the cut that was refused); records in `out/`.
