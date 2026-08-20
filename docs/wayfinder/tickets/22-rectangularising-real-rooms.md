---
id: 22
title: Rectangularising real rooms
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
blocked_by: []
---

# Rectangularising real rooms

## Question

**Every stage of this system places one rectangle per room, and roughly 40 % of
real rooms are not rectangles. How does a real room become a rectangle, and what
does the conversion cost?**

Unowned until now. *Proposer architecture survey* §7.4 flagged it as "the
L-shaped-room question" and assigned it to *Canonical geometry model* and *Solver
formulation for layout projection* — **both closed without settling it**. It is
not a preprocessing detail: it sits under the Proposal contract (one box per
Room), under the solver's tiling, under both Proposer sources, and under *Fit the
ENGINE_CHOICE acceptance thresholds to the corpora*, which cannot fit a threshold
to a corpus it cannot read as rectangles.

**What is known.** ResPlan reports **43.2 % of room polygons exactly rectangular,
62.3 % at a 2 % tolerance** — verified in *Acquire the datasets*, not taken from
the paper. Graph2Plan reports **"over 93 % of the rooms in RPLAN can be
represented as the intersection between their respective bounding boxes and the
building boundary"**. Those measure different things and are not in conflict; the
gap between them is this ticket.

**What has to be decided:**

1. **The conversion itself.** Bounding box; largest inscribed axis-aligned
   rectangle; bounding box ∩ envelope, per Graph2Plan; or split a concave room
   into two rectangles and lose the one-box-per-Room contract. State which, and
   what happens to the room's *area* under it — a bounding box inflates area, an
   inscribed rectangle deflates it, and per-room target-area conditioning consumes
   whichever number this produces.
2. **Measure the loss on Swiss Dwellings**, which nobody has done — ResPlan's
   43.2 % is a different corpus. Per-room IoU, area error, and the fraction of
   dwellings where rectangularised rooms no longer tile.
3. **What it does to adjacency.** Two rooms that touch as polygons may not touch
   as rectangles, and the reverse. Adjacency is what the arrangement metric and
   the solver's contact graph are built on, so a conversion that scrambles it is
   worse than one that loses area.
4. **The reject rule.** Some dwellings will not survive at any tolerance. State
   the threshold above which a corpus dwelling is dropped from training and from
   the retrieval index, and how many that costs.

**Deliverable.** A stated conversion with measured loss on Swiss Dwellings and
ResPlan, checked into `experiments/`, plus the drop count each corpus pays. Feeds
*The retrieval index and warp procedure*, the training pipeline in
`docs/spec/proposer.md` §4, and *Fit the ENGINE_CHOICE acceptance thresholds*.

**Not this ticket.** Whether v1 ever *emits* a non-rectangular room. That is the
map's **Non-orthogonal geometry** fog and stays there.

---

## Resolution

**A corpus dwelling is converted by solving it.** Not by choosing a rectangle for
each room — one CP-SAT fit per dwelling on the shipped 250 mm grid, with the real
dwelling's separation directions and door-width adjacencies posted **hard** and
exact tiling **soft**, which is the shipping solver's own constraint structure
pointed at a real home. Findings `docs/research/rectangularisation.md`, ADR
[0008](../../adr/0008-a-corpus-dwelling-is-converted-by-solving-it.md), harness
`experiments/rectangularise/`. Measured over **42,986 Swiss Dwellings dwellings
and 16,617 ResPlan plans** for the per-room conversions, **2,600 and 1,000** for
the fit.

### The premise was wrong twice before anything could be decided

**"Roughly 40 % of real rooms are not rectangles" has no meaning without an
axis.** In the corpus's own coordinates **0.0 %** of Swiss Dwellings rooms are
rectangles — it is geo-referenced, so an axis-aligned bounding box measures the
site's north angle. On the **dwelling axis** it is 43.3 % at 1 % and **48.9 % at
2 %**, the first measurement of this corpus. The axis is the minimum rotated
rectangle of the union of the rooms; a length-weighted edge histogram agrees to a
median 0.05°, so that sub-question is closed cheaply.

**ResPlan's 43.2 % is a vertex count, not a shape measure.** 43.18 % of its room
polygons have exactly four vertices; **53.9 %** have an area equal to their
bounding box. The 2 % figure reproduces (62.1 % against 62.3 %); the exact one
does not, under any area definition tried. `dataset-inventory.md` §2.3's "42.1 %
exact" is struck.

**And rooms in this corpus are Spaces that never touch** — p50 gap 99 mm, share
touching **0.000**. So item 2's "rectangularised rooms no longer tile" is
malformed: they never tiled. Adjacency needs a wall tolerance, never `touches()`.

### 1. The conversion

All three candidates convert a room in ignorance of its neighbours, and that is
what kills them. The **largest inscribed rectangle destroys 38 % of every real
adjacency** in the corpus and invents 110,910 separation assertions; the
**area-preserving rectangle** — the fourth option, bbox proportion scaled to true
area, which the ticket did not list — destroys 24 % and invents 33,325. Both are
**confident-wrong** manufacture, which `CONTEXT.md` says costs a candidate
outright. Shrinking is what does it: a room that shrinks loses contacts, and
holding area while the bbox inflates it by 11 % *means* shrinking.

**The bounding box makes neither mistake, and there is a small theorem under
that**: a separation direction is a bounds test and a bbox preserves bounds, so
**bbox preserves the separation relation exactly, on every pair, by
construction** — 1.0000 on 931,369 Swiss pairs and 325,899 ResPlan pairs. Its
failure is *not* feasibility. It is that its rectangles collide in **86 %** of
dwellings (99.3 % on ResPlan, median 24 % of floor area), and a pair overlapping
on both axes **abstains**, so the arrangement arrives with the interesting pairs
— the corridor wrapping three rooms — silently dropped and the solver free to
invent them. Plus **+11.1 % mean area**, which target-area conditioning would
consume as fact.

### 2. The measured loss

| | Swiss Dwellings | ResPlan |
|---|---:|---:|
| converted | **0.6873** | **0.5990** |
| per-room IoU median | 0.8950 | 0.6792 |
| cell agreement median | 0.9005 | 0.7617 |
| per-room area error median | −3.45 % | −6.25 % |
| **adjacencies destroyed** | **0 of 17,367** | **0 of 5,321** |
| **relations flipped / weakened** | **0 / 0** | **0 / 0** |
| relations spurious (forced choices) | 0.1565 | 0.2056 |

Against bbox: mean area error **+11.1 % → −2.8 %**, and the target becomes a
tiling. The spurious relations are pairs the truth *abstained* on — one room
wrapping another — where a rectangle model must pick a side. That is the
conversion making a forced choice, not losing information.

**ResPlan converts far worse and it is the living room**: no corridor class, so
circulation is folded into `living`, rectangular in **1.7 %** of plans and
wrapping everything. A second, independent reason it is training-only.

### 3. What it does to adjacency

Nothing, by construction — hard-constrained, and verified zero across 22,688
edges on both corpora. New adjacencies are **not** forbidden: a gained contact
tells the solver a door could go where it could not, which circulation reads as a
lower bound; a destroyed one deletes a door that exists. Only the second lies.

### 4. The reject rule

**Representability, not a percentile: the fit returns a tiling or it does not.**
It is *decidable* — every Swiss dwelling resolved to proven-optimal or
proven-infeasible within 10 s, median 0.44 s, **zero UNKNOWN** — so a dropped
dwelling is a fact about the dwelling and not about the time limit. Rejection is
per **dwelling**, never per room: dropping a room changes the multiset, and the
multiset is retrieval's exact-match key.

**Drop counts: 31.3 % of Swiss Dwellings (813 of 2,600) and 40.1 % of ResPlan
(401 of 1,000).** Roughly 29,500 and 9,800 usable dwellings — still 10× the
~4,000 training floor.

Ablation says what it rejects *for*, and the last row is the sentence to quote:

| arm | converted |
|---|---:|
| as shipped | 0.7360 |
| area band ±25 % | 0.9080 |
| area unconstrained | 0.9120 |
| up to 4 notches | **0.6680** |
| relations, neighbours only | 0.8200 |
| adjacency not required | 0.9560 |
| relations not required | 0.9375 |
| **relations and adjacency both free** | **1.0000** |

**Nothing in this corpus is un-tileable.** What fails is tiling it *as itself* —
the rule rejects a dwelling for not being expressible as **its own** arrangement.
No single family binds: area alone recovers 17.6 points, adjacency 22.0,
relations 20.2, on a drop of 26.4. And **raising ADR 0003's notch cap makes it
worse** — a more articulated Envelope is harder to tile with *n* rectangles.

### Beyond what was asked

**Graph2Plan's 93 % does not survive either corpus.** `bbox ∩ envelope` lands
within 2 % for 55.2 % of Swiss rooms against bbox's 53.9 % — the envelope explains
**2.75 %** of the non-rectangularity, and **2.29 %** on ResPlan. The gap the
ticket asked about is **the corpus, not the method**: rooms are concave because
another *room* is there. So it is a diagnostic and never an output form, which
also keeps room-tag-at-centroid, the aspect-ratio predicate and ADR 0003 closed.

**ADR 0003's ≤2-notch cap is evidenced, and vindicated** — the *Non-orthogonal
geometry* fog patch suspected it was too tight. Two notches describe **61.8 %** of
real dwellings exactly and cost the rest a median **1.85 %** of envelope area; a
third recovers 0.64 points and a fourth 0.18. A plain rectangle misdescribes
16.5 %, so L/U/T are doing real work.

**Non-rectangularity is two room types.** CORRIDOR and LIVING_DINING are
rectangular in **26 %** of cases; BEDROOM in **77 %**, ROOM in 73 %. The rooms a
Homeowner names most confidently cost least; the ones the system invents for them
cost most.

**Three things were measured wrong first**, each of which looked obviously right:
posting exact tiling **hard** rejects almost every real dwelling and is the wrong
model anyway; the **shipped L1 corner-displacement objective is wrong for
fitting** (IoU median 0.14 against 0.82 — projection and fitting are different
problems and shared machinery hides it); and approximating a notch by the
complement's **bounding box** over-cuts, deleting a room outright in 15 % of
dwellings.

### What this hands to other tickets

- ***The retrieval index and warp procedure*** — unblocked, and carrying a
  correction: **§2.2's 9.5 % and 12.4 % blank rates no longer hold.** Conversion
  removes 31 % of the index and takes it disproportionately from the top of the
  band (83 % of 4-room dwellings convert, 46 % of 10-room), so the pool shrinks
  most where it was thinnest. It also owns the **±10 % per-room area band**,
  which is an ENGINE_CHOICE worth 17.6 points of corpus and is the same
  fidelity-versus-coverage trade as *Where warp fidelity actually breaks*.
- ***Fit the ENGINE_CHOICE acceptance thresholds to the corpora*** — the
  converted room is a **centreline** rectangle whose area includes half of every
  surrounding wall. Erode by `t_int/2` before comparing against any
  clear-dimension threshold, or every fitted number is generous by `t_int` per
  axis.
- ***H8 and the single-aspect flat*** — the fit does not know exterior from
  party, so what is measured is **boundary contact**, not window frontage. H8
  fidelity across the conversion is **unverified**.
- **The map's *Non-orthogonal geometry* fog** — strike "how many real dwellings
  fit inside the cap is unmeasured". Measured: 61.8 % at ≤2 notches, and raising
  the cap costs feasibility.

### What this ticket did not settle

- **Nothing has been rendered.** No converted dwelling has been drawn and looked
  at by a person. A conversion that scores well and reads wrong would not have
  been caught here.
- **Sample, not corpus.** The three per-room conversions are full-corpus; the fit
  is 2,600 Swiss and 1,000 ResPlan, stable to a point from n≈1,200.
- **OR-Tools aborted the ResPlan run** after 1,000 plans with an internal `CHECK`
  failure — a C++ abort Python cannot catch. Corpus-scale runs need a subprocess
  per dwelling or restart-from-checkpoint, not a `try`.
- **The 250 mm raster rounds every dimension before fitting**, so part of the
  measured loss is the grid rather than the rectangle, and the two are not
  separated. A second reason for the map's finer-grid fog patch.

### Addendum — what the 31 % is made of

Added after the resolution, because "the drop count each corpus pays" is not just
a count. `experiments/rectangularise/survivorship.py`, findings §6.6.

**The self-confirming-boxiness fear is refuted.** A rectangle model that drops the
dwellings rectangles cannot hold, then trains on the remainder, would learn boxy
priors and no metric here would catch it. Measured: rooms that were already
rectangles are **53.90 %** of the corpus, **53.72 %** of what converts, **53.36 %**
of what drops. The conversion does not select on rectangularity at all.

**It selects on size and interlock.** Median dropped dwelling: **8 rooms and
89.9 m²** against **6 rooms and 71.7 m²** for converted; worst-room bbox IoU
0.6175 against 0.7842; bbox overlap fraction **2.9× higher**. A dwelling is
dropped for having *one* unsquarable room with neighbours interlocked around it,
not for being non-rectangular on average. `STOREROOM` is over-represented among
the dropped at **1.71×** — the leftover space wedged into whatever corner
remained is exactly what a tiling of *n* rectangles has nowhere to put.

**The bias toward the small is the one that matters**, and it compounds: the
corpus was already thinning above 10 rooms, and conversion removes more of what
is left there. Also relevant to *The room-count envelope v1 promises*, which is
not currently listed as a consumer of this ticket and should be.

---

## Amendment — the reject rule was the wrong shape

Raised after the resolution and it is right: **every dwelling in these corpora is
a real, built, inhabited home**, manually QA'd by Archilyse to ≤5 % area
deviation. Nothing here is bad data. So a rule that "rejects" 31 % of them is not
a data-quality gate — it is **a measurement of what our model cannot express**,
and reporting it as a drop rate put the fault on the corpus.

**Say it the other way round: the model expresses 69 % of real homes.** That is a
score for the model, and it invites fixing the model, which is what *Whether a
Room may be more than one rectangle* is for.

**The map already had this principle and this ticket broke it.** *Acceptance
validator spec* loosened two rules specifically **to survive real homes** — wet
clustering to ≤2 plumbing groups, and given-Envelope area agreement to warn-only,
"since rejecting there rejects 100 % of candidates for a fault none caused". The
reject rule as resolved above is the same mistake in a different place.

### What replaces it: a fidelity ladder, not a gate

The ablation already measured the rungs. Every corpus dwelling converts; what
varies is how much of its arrangement survives, and that is **recorded on the
dwelling** rather than used to delete it:

| tier | constraints held | share |
|---|---|---:|
| **A — exact** | all asserted relations, all door-width adjacencies, area ±10 % | 0.7360 |
| **B** | relations between neighbours only; adjacency and area held | 0.8200 |
| **C** | adjacency and area held; relations soft | 0.9375 |
| **D** | area held; relations and adjacency soft | **1.0000** |

**Retrieval admits tier A only.** Its claim is that a person lived in *this*
arrangement, and a tier-B dwelling makes that claim falsely — the gate is real
there and it stays.

**Training takes every dwelling**, at the best tier it reaches, with the tier as a
conditioning field alongside `(region, corpus, annotation_provenance)`. A model
learns from an approximate example; it cannot learn from a deleted one. This also
removes the size bias the addendum above measured — dropped dwellings ran 8 rooms
and 89.9 m² against 6 and 71.7 — which was silently teaching the Proposer that
homes are smaller than they are.

The 31 % therefore stops being a corpus loss and becomes what it always was: the
share of real homes v1's geometry cannot hold exactly. Ticket 28 is how that
number moves.

### Two corrections to this ticket's own claims

**"Zero adjacencies destroyed" is narrower than it reads.** The contact graph
only counts a pair sharing at least 1.0 m, and **32.68 % of real contacts are
below that** (median 0.72 m). Sub-door-width contacts are never constrained by
the fit and their loss is unmeasured. The guarantee holds for adjacencies a door
can use; it does not hold for "adjacency".

**The conversion gives interior shafts to habitable rooms.** v1's Envelope has
boundary notches and no interior obstacles, so a riser inside the dwelling is
absorbed — 2.66 % of dwellings by the hole-filling path, more by the watershed's
0.35 m nearest-room rule, which is unmeasured. Small in area, and it draws a
bedroom over a riser. Belongs to *Structural and services reality*.
