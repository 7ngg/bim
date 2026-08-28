# The Proposer — spec

Ticket 08, *What the model proposes, and how it is trained*.
Contract it must satisfy: `docs/research/solver-formulation.md`
§"What this formulation requires the Proposal to look like".
Architecture it takes: `docs/research/proposer-architecture.md` §7.1.
ADR: [0005](../adr/0005-the-proposer-has-two-sources.md).

Units are integer millimetres and Envelope grid units throughout, per ADR 0001.

---

## 1. What is proposed

**One or two axis-aligned boxes per Brief Room** — four integers each, in
Envelope grid units. A Room's two boxes must share an edge of at least the leg
floor (`acceptance-bar.md` §9.1). No validity guarantee; no adjacency graph; no
wall geometry.

A box is a **part**. Everything downstream that used to say *room i* and mean a
rectangle now says *part*, and a Room is the union of its parts.

> Until ADR [0014](../adr/0014-a-room-is-one-or-two-rectangles-and-the-proposal-decides.md)
> this read *"exactly n axis-aligned boxes, one per Brief Room"* and called
> itself unchanged from the solver contract. It was never weighed: it entered
> through CP-SAT `AddNoOverlap2D` over n boxes and everything inherited it.
> **52.9 % of real rooms are one rectangle and 77.8 % are at most two.**

**The Proposal decides which Rooms are two boxes, and the solver may not.** That
is why this is a contract change rather than a solver option, and it is measured
rather than argued. Given a truth that says which Room really is an L, a Proposal
that carries it places **25 of 25, none spurious**. A solver left to find them
places **10 of 18 and invents 35 more**; penalised until the invented ones stop,
it places **none of 16**. It is also the wrong way round by type — Spearman
**+0.795** between its L-rate and how *rectangular* real dwellings keep that type,
so it reaches hardest for bedrooms and stores and least for corridors. And it is
the expensive way round: a second box for every Room costs 3.9× the variables and
about 10× the time to a first Plan even when it produces nothing, where one for
the Rooms the Proposal names costs 1.2–1.7× and 1.1–2.8× — and lifts the survivor
rate on a concave-truth Brief to **0.50** against **0.36** for the solver-decides
design and 0.33 for the k = 1 control. ADR 0014;
`docs/research/room-rectangles.md` §3–§4.

**Both sources emit it.** Retrieval-and-warp warps each part of a converted
dwelling's room; the trained model emits a fixed two-part slot per Room with a
presence token, so the sequence length stays fixed and only the token varies.

**The Proposal also carries its own holes, and each one names the Room it belongs
to.** A retrieved tiling can enclose floor no part covers — 15.49 % of the index
does — and the solver is required to close it (`model.no_unassigned_area`, hard).
A second field, `voids: [(span, receiving_room)]`, says whose that floor is.
Empty on source B and on 84.5 % of source A candidates. ADR
[0028](../adr/0028-the-enclosed-void-is-charged-to-a-room-and-bounded.md); the
mechanism is §2.2.8.

This passes the test ADR 0014 set and fails the one that refused zoning above.
**Only the Proposal knows it**: the receiving Room is not derivable from the
boxes — largest shared edge agrees with the donor 28.4 % of the time and is
ambiguous on 28.4 % of components, largest bordering Room 38.1 %. And the solver
cannot infer it, because `solver-formulation.md`'s objective is L1 displacement of
all four corners and H3 posts exact tiling soft at 100 000, so **every bordering
Room's repair costs the same** and which one receives 0.3–2.8 m² is a tie broken
by nothing the Brief said.

**No type is barred from being two parts.** Which Rooms are Ls is inherited from
the corpus distribution — already type-shaped and measured — rather than
legislated by a whitelist we would have had to invent. A soft preference for the
simpler Room belongs in `rules.json`, not here.

**One change, and it is a tightening.** Contract item 5 made per-pair confidence
optional, with the solver's own best-versus-second-best margin as a fallback
proxy. Confidence is now **required**.

Two reasons, and the second is the binding one:

1. Both v1 sources can emit a genuine confidence — retrieval from **whether the
   corpus asserted that separation or the conversion invented it**, the model
   from its own logits — and either is strictly better than a geometric proxy
   computed after the fact.

   > ⚠️ This read *"retrieval from how far each room had to move under the warp"*
   > until §2.2.5. Displacement is **uninformative**: §2.2.2's warp cannot
   > destroy a separation direction at any displacement, so severity is 0
   > whether a room moved 30 mm or 3 m. What varies is provenance, and ADR 0016
   > measures it at **12.62 %** of axis-pairs invented.

   **Confidence is per pair.** The contract's `{id: float}` per-box alternative
   is dead for retrieval, which has nothing per-Room to say.
2. With two sources feeding one filter, the solver needs a **source-independent**
   statement of which relations to trust. A proxy derived from box geometry gives
   a retrieved plan and a sampled plan the same confidence for different reasons.

**`source` is deliberately *not* a Proposal field.** The solver must not be able
to treat one source preferentially — that would make the two-source design a
ranking policy instead of a filter. The **job record** carries the source, so the
ablation stays measurable without the contract knowing about it.

**Zoning is deliberately *not* a Proposal field either, and this is a decision
rather than an omission.** *The Proposal cannot express zoning* opened on the
observation that the contract transmits only pairwise separation directions,
while day/night grouping is a property of a set against a set. The observation is
correct and the conclusion does not follow: the **system** already carries
set-shaped properties — `wet.plumbing_group_count` is hard and `site: both`, and
`solver-formulation.md` records that *"reachable and clustered are the same
constraint with different node sets"*. A **[[Sleeping group]]** is that routine on
a third node set.

The node set is derivable **from the Brief**. This is where ADR 0014's precedent
stops: a Room's *shape* had to enter the contract because L-ness is a property of
the truth being copied and only the Proposal knows it — told which Room is an L
the solver places 25 of 25, left to find them it places 10 of 18 and invents 35.
A sleeping group is a property of **Room type**, which the `ResolvedBrief`
already carries, so the solver derives the node set without being told and there
is nothing the Proposal could add. Zoning lives in the solver and the Acceptance
bar; `docs/research/zoning.md` §5.

What it *does* change here is **evaluation** — §6.1.

---

## 2. The two sources

### 2.1 Why two

Measured, not assumed — `experiments/retrieval-coverage/`, over all 46,800 Swiss
Dwellings dwellings, in the Brief's own room vocabulary (§4.1). Each Brief takes
one dwelling's programme and a *different* dwelling's envelope, because a
Homeowner's flat shape did not come paired with the rooms they want:

| Brief rooms | briefs | retrieval pool = 0 | median pool | pool ≥ 20 |
|---|---:|---:|---:|---:|
| 4–6 | 18,143 | **9.5 %** | 92 | 12,785 |
| 7–10 | 24,785 | **12.4 %** | 66 | 16,619 |
| 11–15 | 1,416 | **67.7 %** | 0 | 78 |
| 16+ | 66 | **71.2 %** | 0 | 0 |

Neither source is production-ready alone:

- **Retrieval alone refuses roughly one common-band Brief in nine**, and two in
  three above ten rooms. A system that blanks that often is not "ready to use".
- **A trained model alone fails quietly.** It always emits something, so nothing
  tells you it went wrong, and it discards 46,800 arrangements that are correct
  by construction wherever they apply.

C6 already generates many candidates and rejects most. Nothing ever said they
come from one source. Both sources emit the same Proposal, both go through the
same solver, and the Acceptance bar arbitrates.

### 2.2 Source A — retrieval-and-warp

Graph2Plan's retrieval step over Swiss Dwellings, no learned generator. Ships
first: no training, no GPU, and its arrangements are a real home's by
construction.

**Admissibility is a hard gate, not a ranking term.** A corpus dwelling is a
candidate only if all four hold — three since ADR 0018, and the fourth added by
ADR 0032 on the ground that it is **sound** and so costs no coverage at all:

| Gate | Value |
|---|---|
| room multiset | exact match in the Brief vocabulary (§4.1) |
| total floor area | within **±10 %** of the Brief's |
| envelope aspect ratio | within **±15 %** of the Brief's |
| **frame requirement** | **`req = max(W_req/W, H_req/H) ≤ 1`** — ADR 0032. The smallest box extent the donor's cut-line frame admits at the ergonomic floor, against ADR 0020's box. **Sound**: `req > 1` is a violated necessary condition of the warp's own model, so the term refuses only candidates the warp would have declined — **103 of 103**, measured |

Outside the gate, **do not retrieve** — hand the Brief to source B. The entire
claim of retrieval is that the arrangement is a real home's. Stretch a plan 40 %
in proportion and that claim is false, and what comes out is the 90 %-right
artefact C2 says is worse than a blank sheet. The budget is what makes the claim
true, so it is a gate.

⚠️ **The budget is not where fidelity lives, and the gate was measuring the wrong
quantity.** ±10 % and ±15 % are the values the coverage table above was measured
at, and the standing worry was that stretching a plan past them makes *"this is a
real home's arrangement"* false. It does not — §2.2.2 shows a warp of the shape
this spec now adopts cannot destroy a separation direction at any budget, for any
dwelling and any target. What the gate leaves unconstrained is **per-room area**,
which it never measured: it bounds the *total*. ADR
[0018](../adr/0018-the-warp-is-a-solve-and-it-fits-the-brief.md); everything
below is that decision written out.

**Orientation.** Each retrieved dwelling yields up to **8 variants**: 4 rotations
in 90° steps × mirrored or not. Mirroring is benign here — v1 is single storey,
so there is no stair handedness to preserve. Note precisely what this buys:
aspect ratio is orientation-invariant, so **this does not raise coverage at all**;
it multiplies arrangement diversity *inside* an already-matched pool by up to 8,
which is what C6 wants.

Swiss Dwellings polygons sit in **arbitrary global orientation** — the corpus is
geo-referenced, so a raw axis-aligned bounding box measures the site's north
angle rather than the flat. Every shape figure in this spec comes from the
**minimum-area rotated rectangle** of the union of a dwelling's rooms.

#### 2.2.1 The index

**A hash map on the collapsed room multiset, and nothing cleverer.** The gate's
first term is an *exact* match, so the bucket is the pool and the other two terms
are a scan of it. Over the 46,794-dwelling index there are **916 distinct
multisets** in the Brief's own vocabulary (§4.1), and a bucket is the median 66–92
of the coverage table.

⚠️ **The bucket is not the pool, and the sentence above has been read as though it
were.** *"The bucket is the pool"* means the bucket is the **set the other two
terms scan** — it is the pool's *domain*, not the pool. Every warp-fidelity number
this spec published before ticket 60 was measured through a rig that stopped at
the bucket: **82.4 %** of what it handed the warp is floor the gate refuses
(`experiments/warp/gate_sites.py`, 2,000 Briefs), the median refused donor sitting
**1.33×** the area tolerance and **1.83×** the aspect tolerance outside. Read this
paragraph as three terms, all binding, and an empty result as §2.2's *"outside the
gate, do not retrieve"*.

**The fourth term is sound, and that is why a hard gate may have four.** ADR
0032. `warp_model` posts `Σ gx = W`, `gx_i ≥ 1` and, per part,
`Σ gx[a:b] ≥ MIN_SIDE[room]`, so for **any** set of parts with pairwise-disjoint
x-spans `Σ MIN_SIDE ≤ W`. Maximising that over disjoint sets is an interval DP
over the record's own index spans — microseconds, no solve, no new dependency —
and gives `W_req`; likewise `H_req`. The cut sits at **1.0** because that is
where the warp's hard constraint sits, which is the same licence §2.2.4 gives
`frontage_reach` and denies `frame_residual`. Every other term on this page
trades coverage for quality; this one trades nothing, because everything it
refuses was already refused downstream. It takes per-candidate decline
**27.6 % → 22.9 %** and leaves best-of-pool p50, p90 and the Brief-level served
rate untouched.

⚠️ **It is necessary and not sufficient, so it does not replace the two scalars
and the measurement says so in the direction that matters.** 98 candidates with
`req ≤ 1` were refused anyway — the 2-D coupling `wv ≤ 3·hv` and the area
objective are outside the bound. Dropping the pair and keeping only `req` moves
best-of-pool **p90 0.2303 → 0.2543** at the bucket's real composition and equal
depth. The pair buys **proportion**; the bound buys **feasibility**. They are
orthogonal.

⚠️ **The per-axis frame-extent ratio is the same quantity as the two scalars and
must not be proposed as a third candidate.** ADR 0020's box is
`interior/(1 − s)` at the *Brief's* aspect and the donor's bbox is
`area_d/(1 − s_d)` at its own, so `(1 − s)` cancels and the ratios are
`√(area ratio × aspect ratio)` and `√(area ratio ÷ aspect ratio)` — a bijection
with the pair up to the donor's *void* share, agreeing with the incumbent
conjunction on **89.4 %** of candidates.

⚠️ **The two dimensional terms are not made inert by ADR 0020, and the obvious
argument that they are is wrong.** Under ADR 0020 the box is sized
`interior = target_area × (1 + f)` and `box = interior/(1 − s)` from the **Brief's**
own area and aspect; a donor contributes its parts, its types, its cut-line frame
and its notch share, and its own area and aspect never enter the warp's
arithmetic at all. They are nevertheless worth **8.6 points of decline**. Measured
paired *within one Brief* — same targets, same ring, K = 3 drawn from each stratum
of that Brief's own bucket, 987 candidates an arm over 329 Briefs,
`experiments/warp/gate_effect.py`:

| the donor is one the gate | declined | worst-room area deviation p50 | p90 |
|---|---:|---:|---:|
| **admits** | **27.6 %** | **0.097** | 0.491 |
| **refuses** | **36.2 %** | **0.163** | 0.725 |

Sign test on the per-Brief decline counts: the refused arm is worse on 129 Briefs,
the admitted arm on 74, tied on 126 — **p = 0.0001**. And it is a **dose, not a
threshold**: decline rises 28.3 → 30.1 → 40.2 → **55.2 %** as the donor moves from
inside the aspect tolerance to more than four times outside it, and 29.9 → 37.4 →
31.6 → **53.3 %** on area.

**The mechanism is the frame, not the arithmetic.** ADR 0020 scales the donor's
area and aspect away and then stretches the donor's *cut-line frame* into the
Brief's box. A donor far from the Brief stretches further, and what refuses the
stretch is the ergonomic floor and `dim.aspect_ratio_hard` the warp already posts
(§2.2.2). So the two terms are a **cheap proxy for how hard the frame will have to
stretch**, which is what they were buying all along — the *"stretch a plan 40 % in
proportion and the claim is false"* reading in §2.2 was aimed at the arrangement,
which the monotone theorem shows is never at risk, and it happens to land on a
real quantity anyway.

⚠️ **At Brief level the pool absorbs it, and that is ADR 0018 consequence 3 again.**
Best of 3 from each stratum: 19 Briefs served only by the admitted arm, 16 served
only by the refused arm, 290 by both, 4 by neither — **p = 0.74**. Member quality
is a **per-candidate** property. Never take a per-candidate figure off an ungated
pool, and do not expect a Brief-level one to move when you stop doing so.

> Graph2Plan's 99 ms retrieval is **not a target and not a floor** — it is the
> cost of a *similarity*, a graph kernel evaluated against every candidate.
> Nothing here is a similarity. A lookup is one dict hit plus a linear scan of
> its bucket, and it is microseconds. The retrieval step is not where this
> system spends time; the warp is (§2.2.2), and even that is two orders of
> magnitude under the projection solve.

**What an index record carries.** Built offline, once, from the converted corpus
(§4.4) — never from the raw polygons at serving time:

| field | why |
|---|---|
| `parts[]` — one or two rectangles per Room, integer grid units | ADR 0014; the thing that is warped |
| `types[]` in the collapsed vocabulary | the gate's first term |
| the **cut-line frame**: the sorted distinct x and y coordinates, and each part's index span into them | §2.2.2 warps this, not the rectangles |
| `notches_used`, and **each notch's index span** | the Envelope shape the candidate carries (§2.2.3) — and, since ADR 0020's second amendment, the cells `s` is read off and the line that defines a void. ⚠️ **The spans have never been emitted.** `envelope_approx`'s `env_at` computes the notch rectangles and discards them; this is the **sixth** field owed on the frozen pass, and it is one statistic off the same records |
| **per-pair relation provenance** — for every axis-pair, whether the *corpus* asserted that separation or the *conversion* invented it | §2.2.5; ADR 0016 measures the invented share at **12.62 %** of axis-pairs and only the conversion can tell them apart |
| the entrance-adjacent Room, if the corpus identifies one | §2.2.6 |
| **`frontage_reach`** — the minimum, over the dwelling's `needs_window` Rooms, of the boundary run that Room holds ÷ the frontage budget the solver posts for it | §4.5; below 1.0 the donor holds a Room that cannot seat its window on its own boundary |
| **`W_req`, `H_req`** — the smallest box extent, per axis, this donor's cut-line frame admits at the ergonomic floor | §2.2's fourth gate term, ADR 0032. **Derived, not owed**: an interval DP over the frame's own index spans and the room types, both already in this record, so the frozen `fit_rects.py` pass does not grow a field. Precomputed into the index because it is Brief-free; only the division by the box is per-candidate |
| **`worst_room_iou`** — the minimum, over the dwelling's Rooms, of the fitted rectangles' IoU against the real room polygon | §2.2.4; the only donor-**fidelity** quantity in this record. `fit_rects.py` already emits per-room `iou`, so it is a `min` and no re-fit |
| **`voids`** — the complement components of the parts frame **other than the notch spans**, as index spans, each with the **donor Room that owned that floor** | §2.2.8; ADR 0028 and its amendment. ⚠️ **Widened from *enclosed* to *inside the Envelope*** by ticket 61 — the enclosure test misses the 27.2 % of donors carrying a third boundary-touching component. Watershed ownership purity is p50 1.00 and ≥ 0.80 on 72.7 % of components, **measured on the enclosed population only** |
| **`frame_residual`** — the area-weighted mean deviation of the donor's Rooms from its dwelling axis, in degrees | §4.4; ADR 0031. A dwelling built on two angles is sheared onto one by the conversion, and this records how far. Published on every record regardless of value, and **carrying no threshold inside it** |
| `RegionProfile`/`CorpusProvenance` = `AZ`/`CH` | C14 |

⚠️ **`frame_residual` is not derivable from `worst_room_iou` and the two are not
the same fact.** At every stratum of `worst_room_iou` an off-frame donor scores
5–11 cell-agreement points lower than an on-frame one at the same IoU
(`rectangularisation.md` §15.2): a per-room minimum cannot be a sufficient
statistic for a whole-dwelling shear. It is nevertheless **neither gated nor
ranked on** — §2.2.4 records why, and that paragraph is load-bearing.

**Five of these are new obligations on the conversion**, which today emits
`rel: {same, spurious}` as counts rather than per pair, and emits neither
`frontage_reach`, the void components nor `frame_residual`. That is a change to
`experiments/rectangularise/fit_rects.py`, handed to its holder — this spec
specifies the fields, not the emitter. **Take them in one pass**: they are five
statistics off the same records, and five passes is four wasted re-fits.

⚠️ **That pass also carries a change to `dwelling_frame` itself**, and it is the
reason the pass may not be split. ADR 0031 replaces the union minimum-rotated-
rectangle angle with the **area-weighted modal room angle**, which re-bases
`swiss_fit_k2.json` — the record every corpus figure on this map derives from.
Standalone that is a whole re-reading bought for a tail improvement; riding this
pass it is one function. **Until the pass runs, the conversion is frozen and every
figure quoted here is on the union-mrr frame.**

⚠️ **`worst_room_iou` is a fidelity fact and `frontage_reach` is not, and they are
gated differently on purpose** — §2.2.4.

**Size.** 46,794 records at ~1 KB is under 50 MB resident: an in-process dict
built at boot, not a service and not a database. It is rebuilt only when the
corpus or the conversion changes, and it is versioned with them.

#### 2.2.2 The warp

**A converted dwelling is a rectangular tiling, and a tiling is its cut lines.**
Write the distinct x-coordinates of every part edge as an increasing vector and
the gaps between them as `gx`; likewise `gy`. Every part's width is a contiguous
sum of `gx`, every part's height a contiguous sum of `gy`, and **the tiling's
combinatorics live entirely in the index spans** — which parts sit left of which,
which share an edge, which are adjacent — independent of the gap *values*, so
long as every gap stays positive.

**Two consequences, and the first is a theorem.**

> **Any strictly increasing per-axis map preserves the sign of every separation
> cost.** So for every pair the truth satisfied, the warped Proposal still
> satisfies it; `select_relations` asserts only relations of non-positive cost
> (§5.1); therefore a warp of this shape has **zero confident-wrong relations,
> zero reversals and severity identically 0 against the source dwelling — for
> every dwelling and every target**.

That is retrieval's strongest claim over source B, which has no such guarantee,
and it is why the ±10 %/±15 % budget was never protecting what it was thought to
protect. Asserted, not argued: **21,074 asserted relations over 993 warps at
τ = 4, across every configuration measured — affine and fitted, gated and
ungated — zero confident-wrong, zero severity, zero reversals**
(`experiments/warp/fit_warp.py`).

The second consequence is that the gaps are therefore **free to be chosen**, and
what they should be chosen for is the Brief.

**So the warp is a solve, and it fits the Brief's per-room target areas.** One
CP-SAT programme per candidate, over `len(gx) + len(gy)` integers — the same
toolchain as the conversion (ADR 0008) and the projection, and **no new
dependency**:

```
minimise   (1000 · n) · worst  +  Σ_r  w_r · dev_r  +  w_void · Σ_v  area_v
subject to Σ gx = W,  Σ gy = H,  every gap ≥ 1               (grid units)
           area_r = Σ (parts of r)  +  Σ (voids receiving into r)   § 2.2.8
           dev_r · target_r ≥ 1000 · |area_r − target_r|      (per-mille)
           worst = max_r dev_r
           every part's span ≥ its Room's realisable minimum, both axes
           every part within dim.aspect_ratio_hard
           every two-part Room's shared edge ≥ ADR 0014's join
```

Six things about that programme are decisions, not incidentals:

1. **The objective is minimax on the *relative* deviation**, with the weighted
   sum as a tie-break. An absolute objective spends every gap on the living room,
   because 5 % of 30 m² is a bigger number than 40 % of a WC — and both the
   acceptance bar and the Homeowner read the **worst** room.
2. **`w_r` ranks a stated target above an invented one.** `brief.md` §6.1 makes a
   stated target sovereign and an invented one ours to flex, so the objective
   says so. Measured at an 8:1 weight: stated rooms land at p50 **0.029** against
   invented at 0.039, p90 0.238 against 0.260.
3. **Both axes are solved at once.** A Room's area is bilinear in the two gap
   vectors and CP-SAT takes that through `AddMultiplicationEquality`.
   Alternating linearises it and looks cheaper, but `dim.aspect_ratio_hard`
   couples the axes, so freezing one manufactures infeasibility the joint model
   does not have.
4. **ADR 0014's join is a constraint, not a check.** A warp that scales a
   1 100 mm shared edge down by 15 % emits a Proposal the bar rejects. The join
   is one index span per two-part Room; constraining it costs one linear
   inequality and removes the failure entirely.
5. **The result is `INFEASIBLE`, never `UNKNOWN`.** 329 OPTIMAL, 1 FEASIBLE, 63
   INFEASIBLE, **0 UNKNOWN** over 393 warps at a 3 s cap. ADR 0008 asks the
   conversion to be *decidable rather than timed out*; this inherits that
   property rather than claiming it.
6. **A void is a term in this programme and not a free region.** Its
   area is bilinear in the same two gap vectors, it is added to its receiving
   Room's `area_r`, and it carries a penalty of its own — ADR 0028, §2.2.8. Left
   out, as it was, it is the objective's only unpriced region and the warp
   **amplifies the donor's void 2.2×**. It costs one
   `AddMultiplicationEquality` per component, p50 one component, on 15.5 % of
   candidates, and it moves `INFEASIBLE` not at all.

**Cost: median 72 ms, p90 534 ms.** Two orders of magnitude under the 15 s
projection, so the warp is free at the granularity a job actually works in.

**Rounding is not a separate step.** The gaps are integers in grid units by
construction, so the warped tiling is on the shipped 250 mm grid with no rounding
pass to get wrong — and no rounding pass means no chance of the incoherent
per-coordinate rounding that would break the theorem above.

#### 2.2.3 What happens when the Envelope has a notch the source does not

**The Brief fixes the notch *count* and never the positions** — `brief.md` §5
step 2, because a Homeowner who can place a notch can draw, and C2 says they
cannot. Nothing had said where an invented notch goes.

**The retrieved dwelling supplies it.** The notch is already in the cut-line
frame, so it warps along with everything else. Its position and proportion are
then a **real dwelling's**, measured, rather than the invented constant the
alternative needs.

⚠️ **It is not free, and this sentence used to say it was.** *The sizing rung
under-delivers by four per cent* found that *"the notch is the part of the bbox no
part covers — so it warps along with everything else, **for free**"* is what makes
ADR 0020's *"every candidate delivers `interior` of floor by construction"*
**false**. The derivation `W × H = interior / (1 − s)` is sound only while the
**realised** notch share equals the recorded `s` the box was derived from, and
nothing was holding it: measured, `covered ÷ interior` is **0.9833** with the
notch free and **0.9986** with it held — **1,5 % of `interior`**, worth **5,6
points** of plan-level `dim.statutory_min_area` (30,5 % → 24,9 %).

**So the notch share is held, and it is one constraint.** A bilinear equality on
the gap variables the Room areas already use — realised uncovered area of the
notch components `= s × W × H` — or equivalently the fixed point on the box that
`experiments/warp/`'s `ring` arms reach. ⚠️ **Nobody has priced the constrained
model**: those arms reach the invariant by *re-sizing the box*, not by
constraining the solve, so its INFEASIBLE cost is unmeasured. That is the same
caveat ADR 0028 records for the void term, and the two are one measurement.

⚠️ **This is not ADR 0003 consequence 7.** That fixes the entrance *edge* by side
and says nothing about the notch's dimensions. The two are compatible and neither
implies the other, which is why nothing had caught it.

⚠️ **The notch is not the only uncovered region, and the two are held in opposite
directions.** The notch is held at `s`; everything else uncovered inside the ring
is **our own fit residue** and is charged and bounded — §2.2.8, ADR 0028. Reading
`uncovered` in a fit record as one quantity sums them, and is why neither was
noticed.

⚠️ **The line between them is the notch spans, and it used to be drawn at the
frame's border.** This section said *"the boundary-touching complement is the
**building** and is held at `s`; the enclosed complement is our own fit
residue"*, and both halves of that split were wrong on a quarter of the index.
**The Envelope is the bounding box minus at most two notch rectangles** —
`envelope_approx(domain, max_notches=2)`, and `notches_used` is 2 on 90.16 % of
donors and never more — while **37.6 %** of donors have three or more complement
components of ≥ 0.25 m². Everything past the second is *inside the ring*, so it
is residue that happens to reach an edge, not building. And the two largest are
contaminated the same way, by the `envelope_loss` and residue adjoining them:
measured against the Envelope's own share, `s` runs **+0.0153** at p50,
**+0.0191** mean, more than two points high on **38.2 %** of donors, which is
about **1.9 m² of invented notch** on a 90 m² dwelling — in a ring edge that is
typed, drawn, dimensioned and exported. **`s` is now the `notches_used` spans'
share of the box and nothing else** (ADR 0020, second amendment), and every
other uncovered component is §2.2.8's void (ADR 0028, amendment). Widening `s`
to cover them instead was measured and refused: it moves `s` a further half
point *away* from the Envelope's share.

This makes the Envelope **per-candidate in its `invented` fields only**, and that
is the price. Where `shape` is `stated`, the source's `notches_used` must equal
it and the gate gains a fourth term; where `shape` is `invented`, no gate applies
and each candidate carries its own notch geometry, surfaced as an
`invented_value` Assumption the Homeowner corrects by editing `shape` — C4's
Brief-as-interface, doing exactly the job it exists for.

⚠️ **A stated rectangle nearly kills retrieval, and this is a finding for
`brief.md`, not a knob here.** Of converted dwellings, **90.16 %** use two
notches, 8.72 % one and **1.12 % none**; measured as area, only **6.5 %** leave
under 2 % of their bounding box unoccupied and 15.0 % under 5 %. So
`shape = rectangular` as a *stated* gate term admits single-digit percentages of
the index. **`shape` absent must therefore not default to rectangular** — absence
means unknown, and a default of "rectangle" would silently delete retrieval for
most Briefs. Handed to `brief.md`'s holder.

#### 2.2.4 Ranking inside the pool

The gate admits a median 58–87 dwellings after conversion (§2.2.7). C6 wants many
candidates and not 87 near-identical ones.

1. **Gate** — dict hit, then scan the bucket on total area and aspect, then
   **`req ≤ 1`, hard** (ADR 0032), then **`worst_room_iou ≥ 0.30`, hard**. Free —
   `req` is two precomputed integers and two divisions, and it is ordered before
   the IoU cut only because it is cheaper, not because it is stronger.
2. **Pre-rank** — **partition on `frontage_reach ≥ 1.0`**, then order within each
   part by **`worst_room_iou` descending**, then by the affine warp's worst-room
   deviation, which needs no solve. A proxy, and only for choosing whom to warp.
3. **Warp** the head of that order, then **re-rank on the real post-warp
   number**. A warp that declines (§2.2.2) drops out here.
4. **Take `m`**, never two orientation variants of the same source dwelling
   unless the pool is exhausted.

**Diversity is a post-hoc filter, not a ranking term.** As a term it needs a
weight against area fidelity that nobody can fit; as a filter it is a rule with
no free parameter.

**`frontage_reach` is a partition for the same reason** — a weight against area
fidelity is unfittable, and a partition needs none: the cut sits at 1.0 because
that is where the solver's own hard constraint sits. It demotes and never
excludes; §4.5 records why a gate was refused, and 6.39 % of the index sits below
the cut.

**`worst_room_iou` is gated *and* ranked, and that asymmetry against
`frontage_reach` is deliberate.** *The two-notch cap is now evidenced* measured
donor fidelity and found this record had none: eleven fields, not one of them
about whether the donor converted faithfully, and §2.2.4 pre-ranking on the
*warp's* deviation — a fact about the fit to **this Brief**, not about the donor.
Envelope loss is the wrong proxy: 42.2 % of its tail converts faithfully anyway,
12.70 % outside it does not, and an IoU cut removes 10.09 % of the *most faithful*
envelope band. The quantity is worst-room IoU, its bad population is **154
dwellings, 6.65 % of the index**, and two thirds of that is invisible to either
proxy.

- **Hard at 0.30**, `conf: fitted` rather than `verified` — it is a corpus-fitted
  cut, not a published one. Cost **6.65 %** of the index.
- **Rank above the gate rather than gate at 0.50**, which would cost **17.2 %** of
  an index C13 already calls thin.
- Gated where `frontage_reach` is only partitioned, because **worst-room IoU is a
  pure donor fact** — it compares the fit to the polygon it was fitted to and the
  Brief is not involved — while `frontage_reach` is **joint with the Brief's
  Envelope** and §2.2.6 records that the conversion cannot tell `exterior` from
  `party`. A gate may not claim what it does not know; this one knows.

**`frame_residual` is a pure donor fact and is deliberately neither gated nor
ranked, which is the one asymmetry on this page that is not about what a quantity
knows.** ADR 0031. On the rule just stated it is eligible for a hard gate — it
compares a donor's Rooms to that donor's own axis and no Brief is involved — and
it gets none, because the rule is necessary and not sufficient.

- **There is no knee to cut on.** Cell agreement declines smoothly across the
  residual — 0.944 / 0.914 / 0.891 / 0.854 / 0.802 / 0.778 over
  `rectangularisation.md` §15.4's bands — with no elbow anywhere. A partition here
  would be a **fitted constant chosen for the look of the table**, which is what
  this section refuses everywhere else. `frontage_reach` may partition at 1.0 only
  because the solver's own hard constraint sits there. Nothing sits anywhere here.
- **The pre-rank above has already done it.** Off-frame donors carry low IoU, so
  ordering on `worst_room_iou` descending sorts them down unprompted: a donor at
  4–8° residual sits at the **10.6th percentile** of the surviving pool. Against a
  bucket of 58–87 and `m = 8` drawn from its head, that donor is not taken. A
  second cut on a correlated quantity demotes what is already at the floor and
  charges a fitted constant to do it.

**A gate is for a candidate that is wrong; a rank is for one that is worse.** An
off-frame donor is worse — the shear damages room shape, while adjacency and
separation are posted hard in the conversion and survive it intact, and
arrangement is what a donor hands over. `worst_room_iou < 0.30` is *wrong*: a Room
is essentially not that Room. That is the whole of the difference.

⚠️ **The gate above is already doing this job in part, and nobody knew.** 28.6 %
of everything `worst_room_iou ≥ 0.30` removes is off-frame, and it takes **39.6 %**
of the off-frame population — §15.1. The 6.65 % index cost quoted above is
unchanged; what changes is the reading of *what* it buys.

**`m` is an ENGINE_CHOICE and this spec does not fix it.** It is a cost dial as
well as a latency dial — each candidate is a warp plus a 15 s projection, and
*Language and runtime split* records that the measured 6.25 s does not hold under
candidate parallelism. What retrieval supplies is the pool; what a job spends is
owed by *Fit the ENGINE_CHOICE acceptance thresholds to the corpora*. Every
fidelity figure below is quoted at **m = 8** so it can be re-read at another.

#### 2.2.5 Per-room confidence

§1 promotes confidence from optional to required and named retrieval's source as
*"how far each room had to move under the warp"*. **That is now known to be
uninformative**: §2.2.2's theorem makes severity 0 whatever the displacement, so
a room that moved 3 m and a room that moved 30 mm are equally trustworthy on the
only axis the solver can feel.

**Retrieval's confidence is provenance, per pair.** ADR
[0016](../adr/0016-the-conversion-names-its-own-ls.md) and ADR
[0017](../adr/0017-three-of-the-conversions-fidelity-headlines-are-constraints-restated.md)
measure **12.62 %** of axis-pairs — one in eight, corpus-wide over 2,317
conversions and 97,090 pairs — as `spurious`: pairs whose bounding boxes
*overlapped* on that axis in the real dwelling and no longer do after squaring,
so the truth abstained and the conversion had to pick a side. The corpus asserted
the others.

| pair | confidence |
|---|---|
| the corpus dwelling's own polygons asserted this separation | **1.0** |
| the conversion invented it — `spurious` | **low**, and the solver drops it first |

⚠️ **The caution is about provenance, not about the picks being bad.** ADR 0017
renders them and they read as what a person would draw. What they are not is
*evidence*, and a hard constraint wants evidence.

This makes the contract's `{id: float}` per-box alternative dead for this source:
retrieval has nothing per-Room to say and everything per-pair. §1's wording is
corrected there.

#### 2.2.6 The entrance, and the exposure ring

**The exposure ring is not matched, and that is the finding.** ADR 0003 gives
every Envelope edge a `condition` and an `entrance_side` flag, and *Acquire the
datasets* measured the real distribution — median 0.37 exterior, **0 of 569**
dwellings above 0.99. But the conversion **does not know exterior from party**:
what it measured is boundary *contact*, not window frontage. Retrieval therefore
hands *H8 and the single-aspect flat* no help, and says so rather than implying a
match it cannot make.

**The entrance is matched, and it is free.** Graph2Plan anchors its turning
function at the front door; this system does not need a turning function, because
it already has 8 orientation variants and the entrance is a single edge. **Choose
the variant that puts the source's entrance-adjacent circulation on the Brief's
`entrance_side` edge.** Aspect is orientation-invariant, so this costs no
coverage at all — it spends diversity the pool already had on the one alignment
ADR 0003 says must be fixed before the solve.

#### 2.2.7 Coverage and fidelity, measured

**Coverage.** The table in §2.1 was measured on the *unconverted* corpus and
retrieval can only warp a dwelling the conversion could represent. Joined per
room multiset — the unit retrieval gates in, and the unit ADR 0016 warns against
averaging over — over the full 46,794-dwelling index:

| band | briefs | blank, unconverted | **blank, converted** | median pool | **median pool, converted** |
|---|---:|---:|---:|---:|---:|
| 4–6 | 18,143 | 9.5 % | **9.7 %** | 92 | **86.6** |
| 7–10 | 24,785 | 12.4 % | **12.8 %** | 66 | **58.7** |

**The conversion's price is a pool-size effect, not a coverage effect**, and
nobody had computed that. A 6–13 % thinning almost never empties a pool of 87.
§4.4's warning that *"retrieval's pool shrinks most where it was already
thinnest"* was written before ADR 0016 and is now **0.2 and 0.4 points of blank
rate**. 80.6 % and 71.8 % of Briefs land on a multiset the fit sampled at least
15 times; the rest carry their band's rate.
`experiments/warp/coverage_restated.py`.

**Fidelity, and why the budget could not have bought it.** An affine warp inside
the shipped gate misses the Brief's per-room targets by a median **21 %**;
**8.7 %/11.0 %** of admitted candidates breach `dim.max_area`, which is *hard*,
and **54.9 %/65.9 %** carry a room below 0.70 × what was asked. The two obvious
fixes were priced and both fail:

| | 4–6 rooms | 7–10 rooms |
|---|---:|---:|
| coverage, three-term gate | 90.3 % | 87.2 % |
| coverage if every room must land within ±30 % of target | **40.9 %** | **30.2 %** |
| …within ±10 % | 6.8 % | 8.7 % |
| ranking only: Briefs whose *best* candidate still misses by >30 % | **54.8 %** | **65.3 %** |

Gating cannot buy it — the coverage is not there. Ranking cannot buy it — the
pool does not contain a well-proportioned member, so no ordering finds one. Only
the warp can, and it does:

| worst-room area deviation | p50 | p90 | p99 |
|---|---:|---:|---:|
| affine warp, one candidate | 0.252 | 0.514 | 0.826 |
| **fitted warp, one candidate** | 0.111 | 0.471 | 1.286 |
| **fitted warp, best of m = 8** | **0.056** | **0.363** | 0.892 |

**93.1 %** of Briefs with a pool are served — at least one of 8 candidates
survives the warp. **17.8 %** of individual candidates are declined, and the
ablation says exactly what declines them:

| the warp holds | candidates declined |
|---|---:|
| ergonomic minima and `dim.aspect_ratio_hard` | **22.0 %** |
| minima only | 16.9 % |
| aspect only | 11.9 % |
| neither | **0.0 %** |

⚠️ **So every refusal is a real dimensional refusal, not a limit of the method** —
unconstrained the warp always succeeds and lands the worst room within 4.3 %. A
declined candidate is a target Envelope that cannot host that arrangement at the
ergonomic floor, and per ADR 0005 the Brief falls to the next pool member, then
to source B.

⚠️ **Declines are correlated within a pool, so do not compound them.** They are
driven by the *Envelope*, which every candidate for one Brief shares. Treating
17.8 % as independent across 8 candidates predicts a 10⁻⁶ Brief-level loss; the
measured loss is **6.9 %**. Quote the measured number.

⚠️ **Every decline figure in this section predates ADR 0032's fourth gate term
and is an upper bound once it lands.** The term removes **6.1 %** of the
candidates the three-term gate admits, all of them certain declines, taking the
paired per-candidate rate **27.6 % → 22.9 %**. It does not move best-of-*m*: the
removed members were never the best member, so the worst-room deviation table
above and the **93.1 %** served figure stand unchanged. What it changes is how
much of `m` is spent on corpses.

⚠️ **Three limits on the fidelity figures, and the first one has two answers —
which is the whole of ticket 60.** The sample is the 2,317 converted dwellings of
the ADR 0016 sample and not the full index. What that costs depends on which pool
the figure came off, and *"a pool of 87 in production is a pool of 8 here"* is
true of one and false of the other (`experiments/warp/pool_depth.py`, same
200-Brief sample):

| pool definition | p50 4–6 | p50 7–10 | max | empty | ≥ 64 |
|---|---:|---:|---:|---:|---:|
| §2.2.1 as written — the bucket, scanned by area and aspect | **9** | **5** | 51 | 14.5 % | **0 %** |
| the bucket alone — what the rig drew until ticket 60 | **81** | **37** | 146 | 0.5 % | 43.5 % |
| production, full 46,794-dwelling index | 86.6 | 58.7 | — | — | — |

- **Under the gate**, the sample really is ~9.6× and ~11.7× short and **no** Brief
  in it holds 64 members, so a best-of-8 measured here is a truncated production
  pool and the ratio is fair.
- **Under the bucket**, the sample is at production *depth* already, with 43.5 % of
  Briefs holding 64 or more — so a best-of-8 measured there is a genuine
  best-of-8, not a floor, and the shortfall is in **membership**, not depth.
- ~~*"and the full index can only do better"*~~ — **struck.** The curve is flat by
  m ≈ 12 under a floor no depth reaches (`proposer-architecture.md` §7.6), so the
  extra depth is worth about one point rather than an unbounded improvement.

**Which arm each figure on this page came off.** The coverage table, the
`gate_curve` fixes, the affine per-room miss and this section's decline and
best-of-*m* figures were all measured through the three-term gate and stand.
`proposer-architecture.md` §7.5's arm table and §11.1's starvation figure were
measured through the bucket and are re-based there; ADR 0018's fitted-warp
percentiles were measured through a **third** pairing of its own — `fit_warp.py`
kept a same-multiset Envelope without checking area or aspect and an off-multiset
one whenever those two happened to pass, **22.5 %** of its retained pairs — and
that is repaired and re-run at `--pairing=gate`. It barely moves: worst-room
deviation **p50 0.111 → 0.095**, **p90 unchanged** at 0.471, decline share flat at
15.8 → 16.4 %. **The median improves and the tail does not.** It is robust because
that rig sizes the box from the donor Envelope *itself*, so even an ungated donor
is self-consistent; §7.5's rig sizes the box from the **Brief**, which is where a
mismatched donor actually costs something — and there the same repair is worth
nine points. The relation theorem is unmoved under either pairing: confident-wrong
**0**, severity **0**, reversals **0**, as the monotonicity argument says it must
be.

And the stated-versus-invented weighting was probed at a **30 % stated share**,
which is a probe parameter and not a measurement of what Homeowners state.

#### 2.2.8 The void, and whose floor it is

ADR [0028](../adr/0028-the-enclosed-void-is-charged-to-a-room-and-bounded.md)
and its amendment. **A void is floor inside the Envelope that no Room covers**:
over a candidate's frame, every complement component *other than the
`notches_used` notch spans*. It is not the notch — the notch is the ring's own
geometry, at most two rectangles, held at `s` (§2.2.3). Everything else is inside
the ring, and `model.no_unassigned_area` is hard, so the solve is *required* to
close it.

⚠️ **The test used to be enclosure and it was a proxy that fails at the frame
border.** A component touching the bounding box border is not thereby outside the
building — the Envelope spent its two notches elsewhere. **27.2 %** of donors
carry a third boundary-touching component: p50 **1.25 m²**, p90 4.12, max 9.0,
**89.7 % perfectly rectangular**, **99.7 %** seated at a corner or edge distinct
from the first two. Same object, same cause as the enclosed population — the
k ≤ 2 fit's residue. Total uncovered floor inside the Envelope is **p50 2.47 %**
of it, mean **2.93 %**, against the enclosed slice's p50 0.00 / p90 0.25 m²
tabulated below. Donors carrying at least one void go **15.49 % → about 40 %**;
p50 is still one component, and the cost is still one
`AddMultiplicationEquality` each, the arm ticket 57 priced at **zero**.

⚠️ **This lands with ADR 0020's second amendment or not at all.** The shipped
over-sized `s` has been paying for the uncovered floor: Σ Space is **+0,4 %** of
`target_area` today, and re-basing `s` without widening the void takes it to
about **−1,9 %**.

The table below is the **enclosed** population, which is the measured one:

| | |
|---|---|
| index carrying any enclosed void | **15.49 %** — p50 **0.00 m²**, p90 0.25 |
| ≥ 0.5 m² · ≥ 1 m² · max | 6.73 % · 3.15 % · 4.56 m² |
| room-count gradient | 0.55 % at n = 4 → **15.79 %** at n = 10 |
| of it that is a dropped duct, riser or shaft | **2.0 % of the area** — the rest is our own fit residue |

⚠️ **Do not quote `void_census.py`'s 15.0 / 10.0 / 4.8 %.** Those measure
uncovered floor against the *real dwelling*, on the first 400 records in file
order, and the room-count gradient makes a file-order sample over-state by about
half. The engine never sees the real dwelling; the quantity above is the enclosed
complement of the **parts** frame. `experiments/void/`.

**It is the visible residue of ADR 0014's cap.** A Room is at most two
rectangles — 52.9 % of real rooms are one, 77.8 % at most two — and the void is
where the other 22.2 % shows up. It cannot become the Room's *third* part, and it
cannot become a second part either: `acceptance-bar.md` §9.1's leg floor is
900 mm clear on both axes, realisable 1 100, so a legal leg is ≥ 1.5625 m² and
only **16 of 389** components clear it. *Below 900 mm it is not a leg of a room,
it is a niche, and this system does not model niches.*

**So it is not gated, and the donor is not at fault.** A gate costs **11.74 %** of
the index after conversion-side absorption and **15.49 %** without, worst where
the index is thinnest — 16.2 % at eight rooms, 20.5 % at nine. §2.2.4 accepted a
6.65 % thinning and refused a 17.2 % one; this reaches the refused figure in the
band ADR 0013 already calls tight. And refusing a dwelling for a hole *our* cap
put there charges the corpus twice for a decision taken on solver cost.

**What is fixed is the warp, and it was one unpriced region.** The objective in
§2.2.2 minimised worst-room deviation and the weighted sum and nothing else, so
the void — the one region of the frame carrying no target — was where slack went
for free, and the warp **amplified the donor's void 2.2×**: p50 0.50 → 0.81 m²,
p90 1.31 → 3.19, growing in 62 % of cases.

| arm | realised void p50 / p90 / max | worst-room dev p50 / p90 | INFEASIBLE |
|---|---|---|---|
| free — what shipped | 0.688 / 3.500 / 13.125 | 0.0652 / 0.2849 | 9/90 |
| weighted only | 0.375 / 1.500 / 10.625 | 0.0686 / 0.2979 | 9/90 |
| charged only | 0.688 / 3.000 / 10.000 | 0.0999 / 0.3554 | 9/90 |
| **charged and weighted** | **0.375 / 1.500 / 8.125** | 0.0959 / 0.3293 | **9/90** |

⚠️ **The deviation column is not a regression and reading it as one is the trap.**
`free` measures a Room's parts and ignores the floor it is about to be handed;
`charged` measures the same warp against what the Room will actually hold. The
gap — p50 **0.0652 → 0.0959** — is the size of the understatement in every warp
fidelity figure quoted on a voided candidate.

**The receiving Room is the donor's own, recorded, and it is not derivable.** The
watershed knows whose floor it was — purity p50 **1.00**, ≥ 0.80 on 72.7 % of
components — and no rule computed from the boxes recovers it: largest shared edge
**28.4 %** and ambiguous on 28.4 % of components, largest bordering Room 38.1 %,
the part that can geometrically absorb it **24.1 %**. Where the record is missing
or impure, the fallback is the largest bordering Room, which does least relative
harm.

**Conversion-side absorption is available and deliberately not taken.** Growing a
bordering part closes 42.3 % of the void area and returns the floor to the wrong
Room three times in four, which corrupts the arrangement the index exists to
preserve. Now that the void is charged, it buys nothing worth a transform on the
donor record — ADR 0017 is the standing reminder about transforms whose fidelity
nobody looks at.

#### 2.2.9 What the projection does to a warped candidate

**Until this section, no warped Proposal had ever reached the projection solve.**
`fit_warp.py` imports `experiments/solver-toy/` for §5.1's relation extractor and
nothing else, and `solver-toy`'s own Envelopes are fixtures or real dwellings.
Every per-room area figure on this page — §2.2.7's decline rates, ADR 0028's void
arithmetic, `acceptance-bar.md` §3.2's 25,5 % and 3,6 % — is measured on the
**warped rectangles**, one stage before the object the rules bind on.
`experiments/warp/project_join.py` closes the join: one warped candidate becomes
one `Brief` plus one `Proposal`, `project()` runs at 15 s and τ = 4, and the same
function measures the delivered Space on both sides.

**291 candidates, 273 reaching the solve, 61 Briefs, `ringmarket` semantics.**

| | |
|---|---:|
| starved on the warped rectangles | **18,3 %** |
| of those, **served** by the projection | **82,0 %** — 41 of 50, [71,4–92,6] |
| Proposal-clear and then refused | 2,2 % — 5 of 223 |
| INFEASIBLE overall · 4–6 rooms · 7–10 rooms | 5,1 % · 2,0 % · **8,8 %** |
| every INFEASIBLE re-solved with the statutory limb dropped | **14 of 14 feasible** |
| Σ Space, Plan against Proposal | p50 **0,0000**, p10 −0,0113, p90 +0,0007 |

**The solve does not create floor, it moves it — and that is the whole mechanism.**
§2.2.2 minimises worst-room *relative* deviation and prices every Room
symmetrically; the projection posts the floors **hard** and minimises corner
displacement, so it will shrink a Room comfortably above its floor to feed the one
below. The median starved candidate has exactly **one** Room under its floor.
`acceptance-bar.md` §3.2 already argued from this shape when it set bound 9 to
`warn` — *"a kitchen stated at 6 m² can be delivered at 8 with another Room
absorbing the loss"* — and this is that sentence measured.

⚠️ **So a per-candidate starvation figure taken off this page is not a statement
about what a Homeowner gets.** It is the input to a solve that fixes four fifths
of it. Quote §2.2.7's decline rates as *warp* fidelity, which is what they are,
and never as plan yield.

**A Proposal-level *screen* is refused, on three independent grounds.** A screen
is a filter between the warp and the solve; posting the floor as a **constraint
inside the warp** is a different object, it is not refused here, and
`acceptance-bar.md` §11.1 says so.

1. **It is unsound at 82 %.** Refusing what the warp starves throws away four
   candidates in five that the projection would have served, off a pool whose
   median depth under §2.2.1's gate is **9** at 4–6 rooms and **5** at 7–10.
2. **Its only sound form never fires.** A screen may refuse only what the
   projection provably cannot serve, and the sole cheap relaxation is arithmetic:
   Σ hard floors against the candidate's own derived box. Measured, that ratio is
   p50 **0,566**, p90 0,688, **max 0,736** over 273 candidates — 0 firings, and it
   cannot fire, because `box = target_area × (1 + f) / (1 − s)` and every target
   sits at or above its floor under `dim.market_default_area`.
3. **It would sit on the wrong side of the expensive step.** The projection costs
   **less than the warp that feeds it** — wall p50 **0,145 s** against a warp p50
   of 0,674 (means 1,05 and 1,12; p90 0,98 and 2,71; 4,4 % of solves reach the
   15 s cap). A gate between the two skips the cheaper half.

**Why the solve is that cheap, stated so nobody quotes it against a different
object.** A warped candidate arrives as an exact tiling of its own Envelope with
τ = 4 relations fixed from it, so the projection is a **repair**, not a search.
⚠️ It is therefore **not comparable** with `solver-formulation.md` Part V's
10,11 s, which is a real dwelling's own boundary with a generated ground truth, or
with ADR 0029's fixture timings, which run at `t_int` 100 where this runs at 150.

**What the join cannot see, and one thing it found instead.**

⚠️ **The two rigs measure area on different planes, and the gap is the whole of
the false-pass column.** `solver.py` binds H4 on `(250w − t)(250h − t)`, eroding
all four sides; ADR 0001 does not erode at the Envelope boundary. The gap is p50
**3,92 %** of a Room's area (p90 7,24), **27 of 1 786 Rooms** cross a floor
between the planes, and **19 candidates are starved on the solver's plane alone**
— a superset of the 5 false passes. This is ticket 56's 75 mm ring, re-found
inside the solver where the 250 mm grid makes it unremovable, and it means the
projection is strictly stricter than the bar. `acceptance-bar.md` §11.1 carries it.

⚠️ **The arm runs on one-rectangle donors, 46,4 % of the converted index.**
`solver-toy/solver.py` gives a Room one rectangle where ADR 0014 gives it one or
two, and the restriction skews small — 59,3 % of donors at n = 6 against 31,4 % at
n = 9 — which is why the starvation base rate here is 18,3 % against
`ringmarket`'s **25,5 %** on the unrestricted set. The k ≤ 2 arm runs through
`room-rectangles/solver_parts.py`, whose Design A binds the Room's `min_area` on
the **primary part** where ADR 0014 binds it per Room; it is strictly stricter, so
it can confirm a false refusal and cannot rule one out.

⚠️ **H8, H9 and H10 are posted soft in the arm and their cost is not measured
here.** The toy's H9 wants one plumbing cluster where `wet.plumbing_group_count`
has been 3 since ADR 0023; its H10 routes around a `PRIVATE` set containing the
wet types; its H8 binds off an exposure preset a warped candidate does not carry,
because the ring is ADR 0003 §7's and `frontage_reach` is not on the Proposal.
Leaving them hard would have measured the toy — 58's finding from the other side.
What they would have cost is recorded without a solve: of 273 warped candidates,
only **54** satisfy the toy's full hard set, failing H9 129 times, H10 104 and H8
75. **None of those three counts is `room-constraints.json`'s cost** and none may
be quoted as one.

⚠️ **The void is carried as an Envelope obstacle, not as ADR 0028's charged
span**, because the toy `Proposal` has no `voids` field. That is what makes the
candidate its own witness and it makes the arm optimistic about H3 and nothing
else; §2.2.8 holds the void's real cost.

**What is owed.** The **Plan-level twin of §7.6's best-of-*m* curve**. §11.1 now
declares starvation on the Plan, and the one number it has for that — 3,28 % →
**1,64 %** at Brief level — rests on 61 Briefs and 2 starved cases. The curve, the
floor π and the 7–10 band all need re-measuring at the Plan, and `project_join.py`
plus `best_of_m.py` are the two halves of it.

---

### 2.3 Source B — the trained model

`docs/research/proposer-architecture.md` §7.1: a Brief-conditioned room-set
transformer. ~20M params, `d = 512`, 4–8 layers, 128 coordinate bins per axis,
envelope cross-attention, per-room target-area conditioning,
`(region, corpus, annotation_provenance)` tokens.

**Two box slots per Brief Room, the second gated by a presence token** (§1). The
sequence length stays fixed at `2n`, which is what keeps this a set-transformer
rather than a variable-length decoder: the model learns *whether* a Room is an L,
not *how many* rectangles to emit. Training targets come from the converted
corpus, so the L distribution it learns is the corpus's own — which is already
type-shaped, and is why §1 needs no whitelist.

**Synthetic pre-training is cut from v1.** The survey's stated purpose for it was
the 12–32 room regime, because no real corpus reaches it. v1 does not promise
that regime (§3), and in the band v1 *does* promise the corpora hold **~60,600
dwellings against the survey's own ~4,000-record floor — 15×**. It returns only
if the room-count ceiling is raised.

This drops the training bill from the survey's 10–25 GPU-hours to **5–15**.

### 2.4 Why §7.3(a) does not fire

The survey's trigger — retrieval wins outright below ~1,000 dwellings at ≥16
rooms — counted **the tail**. *Acquire the datasets* found 66. v1 no longer
promises that band, so the trigger is measuring a regime the product does not
sell. Its second conjunct ("and synthetic pre-training fails to close the gap")
is moot: in-band there is no gap to close.

What survives is **§7.3(b)** — retrieval must be *beaten*, not assumed inferior —
and the two-source design answers it continuously in production rather than once
in a report.

---

## 3. The band v1 serves

**4–10 Brief-named rooms.** 42,928 of 46,800 Swiss Dwellings dwellings — 92 % —
and where retrieval has a median pool of 66–92.

Above 10 rooms retrieval is dead (67.7 % blank) and only source B answers.
*The room-count envelope v1 promises* owns what the product **claims**; this spec
states only what the Proposer **covers**.

---

## 4. Corpus preparation

### 4.1 Room-type vocabulary

`ROOM` is Swiss Dwellings' most common label — 82,618 rooms, 26 % of the corpus,
more than `BEDROOM`'s 22,997. A Brief never says "room". Measured
(`experiments/retrieval-coverage/room_label_probe.py`, 3.26M rows, areas in m²):

| subtype | n | p5 | median | p95 | CV |
|---|---:|---:|---:|---:|---:|
| `ROOM` | 82,562 | 9.9 | **14.4** | 22.4 | **0.29** |
| `BEDROOM` | 22,875 | 10.0 | **14.0** | 18.6 | **0.22** |
| `CORRIDOR` | 53,295 | 2.2 | 7.5 | 17.7 | 0.60 |
| `STOREROOM` | 14,294 | 0.5 | 2.2 | 7.3 | 1.30 |

`ROOM` is **not a grab bag** — it is an *unlabelled private habitable room*, with
`BEDROOM`'s distribution and a tighter spread than `CORRIDOR` or `STOREROOM`. Its
wider upper tail absorbs some studies and larger living spaces.

**Collapse `{ROOM, BEDROOM, STUDIO}` → `PRIVATE`** for the retrieval key and the
training label. The Brief's finer type (bedroom, study, nursery) rides as *model
conditioning*, never as a retrieval key.

**Do not collapse `LIVING_ROOM` / `LIVING_DINING` / `DINING`.** Open-plan versus
separate is real programme a Homeowner states, not a labelling artefact.

Collapsing cuts distinct multisets from 1,190 to 916 and roughly doubles pool
sizes — every coverage figure measured *before* the collapse was pessimistic.

### 4.2 `BATHROOM` is ambiguous and the corpus cannot say

One label spans **p5 1.5 m² to p95 6.3 m²** — a WC at one end and a family
bathroom at the other. A Brief distinguishes them, and `dim.min_area` is a
different number for each.

Split by area. **The threshold is not set here**: *Ergonomic minima and the
constraint table's missing half* is deriving exactly these fixture footprints and
body clearances, and inventing a second number here would create a table to drift
against that one. New obligation on that ticket.

### 4.3 ResPlan

**Excluded from retrieval. Included in training.**

Retrieval's admissibility gate is metric — ±10 % of an area in m². ResPlan's
geometry is **not in metres** despite its README: a ~256-unit canvas whose scale
varies per plan, median 0.0545 m/unit, only 3.6 % within 1 % of the median. Scale
must be recovered per plan as `sqrt(area / polygon_area)` — from the same `area`
field that carries a **square-feet bug in seven plans**. A gate cannot rest on
that. Swiss Dwellings is WKT in metres, manually QA'd to ≤5 % area deviation by a
named corporate rights-holder.

For training it enters under the `(region, corpus, annotation_provenance)`
conditioning tag *Cross-dataset unification* requires, with per-plan scale
recovery applied and ids 5981–5985 filtered. **16,317** non-augmented plans.

### 4.4 Rectangularisation — settled, and it is a solve

⚠️ **The 31 % price is paid, and this section's own figures are the stale ones.**
ADR [0016](../adr/0016-the-conversion-names-its-own-ls.md) re-ran the fit at ADR
[0014](../adr/0014-a-room-is-one-or-two-rectangles-and-the-proposal-decides.md)'s
two rectangles per Room, paired on the dwelling key, zero dwellings lost:

| | was | **is** |
|---|---:|---:|
| Swiss Dwellings dropped | 30.70 % | **9.74 %** |
| ResPlan dropped | 40.10 % | **6.40 %** |
| yield | — | **90.3 % / 93.6 %** |
| 4-room against 10-room conversion | 83 % / 46 % | **94.8 % / 82.6 %** |
| spurious axis-pairs, corpus-wide | 15.64 % | **12.62 %** (ADR 0017 §12.2) |

⚠️ **And the tier ladder is two rungs, not four.** ADR 0016 consequence 5: A → B
now buys 2.0 points against 8.4, and tier C sits *below* tier A because dropping
the hard relations removes the pruning and the arm times out. **The tier
conditioning field ADR 0008 gave the training set is binary, not four-valued**;
§2.3's two-part slot needs no change, and retrieval's tier-A gate is unchanged.

The conversion is still one CP-SAT fit per dwelling and still drops what it
cannot represent. Everything else in this section stands.

Every stage downstream places **one rectangle per room**, and about half of real
rooms are not rectangles. Settled by *Rectangularising real rooms*:
`docs/research/rectangularisation.md`, ADR
[0008](../adr/0008-a-corpus-dwelling-is-converted-by-solving-it.md), harness in
`experiments/rectangularise/`.

**A corpus dwelling is converted by solving it.** One CP-SAT fit per dwelling on
the shipped 250 mm grid, with the real dwelling's separation directions and
door-width adjacencies posted **hard** and exact tiling **soft** — the shipping
solver's own constraint structure, pointed at a real home. A dwelling with no
such tiling is **dropped**; representability is the reject rule.

Three corrections to what this section used to say:

- **ResPlan's "43.2 % exactly rectangular" is a vertex count, not a shape
  measure.** 43.18 % of its room polygons have four vertices; **53.9 %** have an
  area equal to their bounding box. Every use of 43.2 % here was pessimistic.
- **Swiss Dwellings had never been measured.** It is **48.9 %** rectangular at
  the same 2 % tolerance — and **0 %** in the corpus's own coordinates, because
  it is geo-referenced. Every shape figure names the **dwelling axis** it was
  measured on, which is the minimum rotated rectangle of the union of its rooms.
- **Non-rectangularity is two room types.** CORRIDOR and LIVING_DINING are
  rectangular in 26 % of cases; BEDROOM in 77 %. ResPlan folds circulation into
  `living`, which is rectangular in **1.7 %** of plans.

**What the conversion guarantees, on both corpora:** zero real adjacencies
destroyed, zero separation directions flipped or weakened. **What it costs:** 31 %
of Swiss Dwellings and 40 % of ResPlan dropped, per-room IoU median 0.895 and
0.679, per-room area error median −3.5 % and −6.3 %.

✅ **§2.2's coverage table is re-measured, and the fear was misplaced.** This
section used to warn that *"retrieval's pool shrinks most where it was already
thinnest"*. Joined per multiset over the full index, the conversion costs **0.2
and 0.4 points of blank rate** — 9.5 → 9.7 % and 12.4 → 12.8 % — and takes the
median pool from 92 to 86.6 and 66 to 58.7. A 6–13 % thinning almost never
empties a pool of 87, so the price is a **pool-size effect, not a coverage
effect**. §2.2.7.

**The converted room is a centreline rectangle**, not a clear one: the watershed
splits each wall at its axis, so a converted room's area includes half of every
wall around it. Per ADR 0001 the clear rectangle is that eroded by `t_int/2`, and
anything comparing against a clear-dimension threshold must erode first.

### 4.5 Glazing is not a property a donor hands over

**The corpus is admitted unfiltered on glazing, for both sources.** No index
filter, no training filter, no reweighting, and no niche exception. What replaces
the filter is one index field and one ranking partition, on the property the warp
actually inherits. *A third of real kitchens have no window and the engine may not
draw one*; ADR
[0025](../adr/0025-glazing-is-not-a-property-a-donor-hands-over.md).

The ticket asked what the engine does about a population it learns from and may
not reproduce. **The population was mis-identified.** A donor's windows are never
inherited:

- §1 emits **boxes** — *"no validity guarantee; no adjacency graph; no wall
  geometry"* — and no openings.
- `openings.md` §6.1 places **one window per Space**, on its longest
  `exterior`-condition run, **after** the solve.
- *H8 and the single-aspect flat* moved `win.habitable_has_window` to site
  `both`, so the **solver** posts the frontage budget hard — 1 100 mm for a
  kitchen, 1 400 for a bedroom, 1 700 for a living room.

A donor's glazing is overwritten in every case. What a donor hands over is its
**arrangement**, and through the arrangement one thing that binds: whether each
`needs_window` Room can reach a wall at all.

This **discharges an obligation already recorded here** rather than inventing an
argument. `docs/research/acceptance-thresholds.md` §13 left this page exactly
this, and named this ticket as one of its two recipients:
*"Both are opening-layer rules, placed after the solve, so a candidate's prior of
clearing the bar is set by a layer the Proposal does not carry."*

#### The number that is a retrieval cost, and it is not the ticket's

`experiments/corpus-smoke/`, over 46,565 dwellings — the whole converted-corpus
room cache, against the 561 the rule had been measured on:

| | dwellings |
|---|---:|
| hold a dark `needs_window` Room — the shipped rule's corpus cost | **38.55 %** |
| …and hold that Room **on the boundary**, where this engine glazes it | 33.17 % |
| **hold a `needs_window` Room that reaches no boundary at all** | **5.88 %** |
| **…or reaches less than the frontage budget the solver posts** | **6.39 %** |

**86.04 % of every dwelling the shipped rule rejects is reglazed for free.** Per
room the kitchen is **28.90 %** dark and **3.54 %** landlocked, and **88.36 %** of
the corpus's 12,717 windowless kitchens reach a wall. The population this section
is about is **6.39 %**, six times smaller than the number the ticket was raised
on, and its failure mode is **INFEASIBLE at the solve** — the frontage budget is a
hard solver constraint — not rejection at the bar.

⚠️ **Three published per-room figures move, and one of them was a warning coming
true.** *H8 and the single-aspect flat* flagged its own `LIVING_ROOM` figure as
*"measured on only 105 rooms and may be a labelling effect"*. It was:

| | 561 dwellings | **46,565** |
|---|---:|---:|
| dwellings rejected | 43.3 % | **38.55 %** |
| kitchen alone | 23.0 pts | **21.64 pts** |
| `KITCHEN` rooms | 31.0 % | **28.90 %** |
| **`LIVING_ROOM` rooms** | **20.0 %** | **10.09 %** |
| `DINING` rooms | not reported | **19.54 %** (n = 1,315) |

Restricting to h8's own population — floors carrying two or more dwellings —
moves the headline to 38.77 %, so the gap is **sample size and not population**.

⚠️ **`rules.json`'s `corpus_cost` 0.4519 is not contradicted and must not be
overwritten.** It is the *raw* arm of `experiments/acceptance-thresholds/`, 42,985
unconverted dwellings under a different envelope method, and its own leave-one-out
says the rule adds **15.97 points** to the bar rather than 45. Three numbers, three
questions; none of them is the retrieval cost, which is the row above.

#### Why the filter is refused, and it is the overlap the ticket asked for

Paired on ADR 0016's own 2,600-dwelling sample — the only dwellings whose
conversion verdict is known, so there is no sampling gap to argue about. The
conversion's refusal reproduces at **9.75 %** against ADR 0016's 9.74 %, which is
the join's own check:

| | window PASS | window FAIL | total |
|---|---:|---:|---:|
| conversion **converts** | 1,413 | 902 | 2,315 |
| conversion **refuses** | 144 | 106 | 250 |

**The two drops compound; they do not overlap.** Both refuse 4.13 % against
3.83 % under independence — **lift 1.08×**. Joint drop **44.91 %**; survive both
**55.09 %**; the window rule's marginal cost on dwellings the conversion keeps is
**38.96 %**. ADR 0016 fought Swiss 30.70 % → 9.74 %, and a glazing filter would
hand back four times what that bought — for a property the opening layer
overwrites.

✅ **No slope is restored.** ADR 0016's headline gain was flattening a conversion
that preferred small dwellings. Window-fail runs **42.9 % at four rooms to 36.0 %
at ten** — flat to *declining* — so nothing about this filter re-biases the index
by size.

#### What retrieval owes: a field and a rank, and deliberately not a gate

**`frontage_reach`, a new index record field** (§2.2.1): the minimum, over a
dwelling's `needs_window` Rooms, of the boundary run that Room holds divided by
the frontage budget the solver posts for it. Dimensionless; below **1.0** the
donor holds a Room that cannot seat its window on its own boundary.

**A partition in the pre-rank, not a weighted term** (§2.2.4): candidates with
`frontage_reach ≥ 1.0` are ordered ahead of those below it, and the existing
worst-room-deviation order holds inside each part. §2.2.4 already refuses weighted
terms — *"it needs a weight against area fidelity that nobody can fit"* — and this
needs none: the threshold is 1.0 because that is where the solver's own hard
constraint sits, so the rule introduces **no free parameter and no fitted
constant**.

⚠️ **It is a rank and not a gate, for three reasons, and the third is the one that
decides it.** The residue is small (6.39 %); a gate would thin hardest exactly
where ADR 0013 already calls the index tight — landlocked runs **0.73 % at three
rooms to 10.91 % at ten and 12.83 % at twelve**; and, decisively, §2.2.6 records
that **the conversion knows boundary contact and not exterior-versus-party**. So
`frontage_reach` is **necessary and not sufficient**: a run measured on the donor
may be party edge in the target Envelope and host no window. A hard gate on a
necessary-not-sufficient proxy claims what it does not know. This is why it does
**not** follow *The two-notch cap is now evidenced*'s worst-room-IoU precedent —
that quantity is a pure donor-fidelity fact, and this one is a joint fact about
the donor **and** the Brief's Envelope.

#### Source B, and the warning the ticket carried is false as stated

The ticket warned that *"a trained Proposer that learned windowless kitchens from
31 % of its data will propose them everywhere"*. **§2.3's model has no window
token.** It emits two box slots per Room with a presence token, so the only thing
it can learn from a windowless kitchen is an **interior kitchen** — and that
prior is **5.88 %**, not 31 %.

**The training set is therefore not filtered either**, and for a reason beyond the
arithmetic: a landlocked room is not a defect in the donor, it is a fact about
real housing that the solver already refuses hard. Trading 5.88 % of a corpus ADR
0013 calls thin, to suppress a case the projection rejects anyway, buys nothing.

What is added instead is **a fourth plan-quality term in §6.1** — `frontage_reach`
computed on a generated Plan by the same code that computes it on a corpus
dwelling, so the model's rate is **measured against the corpus's own 5.88 %**
rather than assumed. Evaluation, not a stop condition, exactly as the other three.

**ResPlan needs no separate decision.** It is training-only (§4.3) and its schema
carries a first-class `window` field, so the same measurement is available there —
but nothing above depends on the donor's windows, so there is nothing to measure
before admitting it.

#### The `taxça-mətbəx` is refused again, and on a stronger ground

`profiles.AZ.windows.kitchen_niche_windowless` holds **`false`**, and this section
does not move it. **The exception is not refused for being small**: a
borrowed-daylight exception would retain **91.47 %** of the index against 61.45 %
under the rule as shipped — thirty points, the largest single lever this ticket
priced. It is refused because **v1 has no producer and no consumer for it**. The
engine glazes kitchens itself, so it never needs to emit one; and no Brief can ask
for one — there is no `taxça-mətbəx` Room type, which ADR 0022 §4 already records
as a partly unsatisfiable limb. A rule with neither is a rule that cannot fire,
and *H8 and the single-aspect flat* retired two rules on exactly that test.

⚠️ **And the evidence it rested on does not say what two documents read it as
saying.** *H8 and the single-aspect flat* §6 and this ticket both glossed *"84.7 %
adjoin a windowed habitable room"* as *"the `taxça-mətbəx` arrangement"* — an open
kitchen zone of a windowed living space. **Adjacency is not openness.** cl. 5.7's
niche is a **recess open to the room it sits in**; a separate kitchen with a
**door** onto a windowed living room is a windowless kitchen, which cl. 9.12
forbids outright. Swiss Dwellings ships the openings, so the two can be told apart
in one direction — `experiments/corpus-smoke/kitchen_niche_test.py`, over the
11,139 windowless kitchens that adjoin a lit room:

| | kitchens | of adjoining |
|---|---:|---:|
| **DOOR polygon on the shared boundary — not a niche** | **5,227** | **46.93 %** |
| no door polygon — undetermined, see below | 5,912 | 53.07 % |
| *(of all 12,717 windowless kitchens: clear cl. 5.7's 5 m²)* | 9,277 | 72.95 % |
| *(…and have no lit neighbour at all — nothing to borrow from)* | 1,578 | — |

⚠️ **The test is one-sided and the remainder is not the other half.** A missing
door polygon is not evidence of an open threshold: the corpus may not model one,
or the two rooms may merely touch. So **nearly half of the population is
positively not a niche and the rest is undetermined** — nothing here licenses
reading any share of it *as* one. The 84.7 %/87.59 % figure is sound; the gloss on
it is withdrawn.

---

## 5. The arrangement metric

Assigned to this ticket by *Proposer architecture survey* §7.1: no published
metric measures what the solver actually consumes.

**Validated, and redefined in the process**, by *Validate the arrangement metric
against the solver*. Everything below is the post-validation definition;
`docs/research/arrangement-metric.md` holds the measurements, and
`experiments/solver-toy/arrangement.py` is the reference implementation.

### 5.1 Definition

Run the **solver's own extractor** on both sides, so the metric cannot drift
from the thing it predicts. This is now literal rather than aspirational:
`solver.rank_relations` and `solver.select_relations` are module-level functions
that `LayoutProjector._add_relations` and the metric both call.

**The unit is a pair of parts, not a pair of Rooms**, with same-Room part pairs
excluded — they are joined, not separated. When every Room is one part this is
bit-identical to what shipped, so nothing measured before §1 changed is invalid.

⚠️ **This is forced, not chosen, and the Room-level reading is unsafe.** An
L-shaped Room and the Room sitting in its notch have a **positive** best
separation cost on all four options — no axis separates them — and step 3 below
abstains on a small *margin*, never on a positive *cost*. Extracted at Room
level the pair would therefore be **asserted**, and the truth contradicts it: a
manufactured confident-wrong relation, which §5.3 measures as fatal in company.
Their parts *are* separable, so the part-level extraction keeps a real
constraint where abstaining would have thrown one away.

✅ **A defect this exposed, and it is now closed by rule.** Nothing in step 3
filtered on a positive cost at all, so a Proposal whose boxes **overlap** — which
a trained model emits routinely, and which §5.2's own noise model produces — had
separations asserted for pairs the Proposal never separated, posted **hard**.
§5.4 measures the cost of exactly that: 1 confident-wrong relation → **6 %**
survivor, 2 → **0 %**.

**The rule: assert only when the best separation cost is ≤ 0.** A positive best
cost means no axis separates these two boxes — the Proposal is asserting
*overlap*, which this contract cannot express, and the honest reading is that it
asserted nothing.

For each unordered pair (i, j) of parts:

1. compute the four separation costs — left-of, right-of, above, below
2. `direction = argmin`; `margin = second_best − best`
3. **`best > 0` → the pair abstains**: the Proposal separated them on no axis
4. `margin < τ` → the pair **abstains**: the solver leaves it free
5. otherwise the pair is **asserted**

Three notes on step 3, because *abstain* was not the only candidate rule:

- **It never fires on legitimate geometry.** ADR 0014's per-part extraction is
  what makes this safe: an L-shaped Room and the Room in its notch have a
  positive best cost at *Room* level, and their **parts** are separable, so the
  part-level best cost is ≤ 0. Extracting per part keeps the real constraint;
  the filter then only ever removes assertions about boxes that genuinely
  overlap.
- **Retrieval is immune either way.** §2.2.2's warped tiling is disjoint by
  construction, so every best cost is ≤ 0. This rule exists for source B, which
  is the source that needs it.
- **It is a spec rule here and a code change there.** `select_relations` lives in
  `experiments/solver-toy/solver.py`, claimed by *The solver has only ever seen
  guillotine layouts* and *What an ordered entry sequence costs the solver*.
  Handed to whichever moves first; nothing in this ticket touched that file.

An asserted relation is then scored against the ground-truth dwelling's
rectangularised rooms:

| | |
|---|---|
| **agreeing** | the truth **satisfies** the asserted separation — `sep_cost(truth, relation) ≤ 0` |
| **confident-wrong** | the truth **contradicts** it — `sep_cost(truth, relation) > 0` |

⚠️ **This is not "the asserted direction is the truth's `argmin`", and the
difference is not pedantic.** Two disjoint boxes can be separated on *both* axes
— every diagonal neighbour in a tiling is such a pair — so a relation can differ
from the truth's `argmin` and still be one the truth satisfies. The solver
cannot tell the difference, because the constraint holds either way. Scoring by
`argmin` over-reports confident-wrong by **1.5× at 8 rooms and 3.6× at 24**, and
predicts survival worse (61.4 % against 78.6 %). Earlier drafts of this section
said `argmin`; `CONTEXT.md` always said "backwards", and `CONTEXT.md` was right.

### 5.2 What is reported

Four numbers, per Proposal, never one and never as a per-pair rate.

| | |
|---|---|
| **severity** | Σ `sep_cost(truth, relation)` over confident-wrong relations, in millimetres — **the headline** |
| **confident-wrong count** | how many relations the truth contradicts |
| **reversal count** | of those, how many are *same-axis* reversals (see below) |
| **abstain rate** | pairs below τ |

**Severity, not count, is the gate.** A relation the truth violates by one grid
unit and one it violates by ten are the same number in a count and are not the
same defect. Measured over 140 realistic Proposals in the 4–10-room band,
**severity below 2 000 mm implied a survivor in 80 runs out of 80**, at 87.9 %
accuracy against a count's 78.6 %. Treat 2 000 mm as a starting threshold fitted
on a toy, not a shipped constant.

**Report per Proposal, never as a per-pair rate.** A rate compounds over pairs
and the pair count is quadratic in rooms: a 0.5 % confident-wrong rate leaves a
Proposal clean 88 % of the time at 8 rooms and **28 %** at 24. "99.5 % correct"
and "loses seven Proposals in ten" are the same number, and only one of them
gets quoted.

⚠️ **The pair count is quadratic in *parts*, not Rooms, since §1.** A Proposal
where every Room is two boxes has up to **four times** the pairs of the same
Proposal at one box each, so every *count* threshold on this page — the 1 → 6 %,
2 → 0 % survivor cliff of §5.3 above all — is stated in a unit that now moves
with the Proposal's shape. **Severity is not**: it is millimetres of contradicted
overlap and it does not care how the boxes were grouped. This is the second
independent reason severity is the gate, and *Validate the arrangement metric
against the solver* had already reached the first — counting is the wrong unit.
Re-fit any count threshold before quoting it on a Proposal with parts.

**Split reversals out.** A *same-axis reversal* — the truth puts the two rooms
the other way round — was INFEASIBLE at **100 %** of injected doses tested. A
*cross-axis swap* at the same dose is 0–33 % at one relation. They are different
defects, and a source that emits one is failing differently from a source that
emits the other.

**The asymmetry with abstain is why these are never one number.** An abstain
leaves the solver free and costs **time**: at 8 and 12 rooms, dropping *every*
relation still produced a survivor in 5 runs of 5, at worst 6× slower. A
confident-wrong relation costs the **candidate**: one is enough to make the
model INFEASIBLE 56 % of the time, and two takes the survivor rate to zero.
Never collapse a slowdown and a failure into one figure.

**No cycle rate.** The earlier definition asked for the fraction of Proposals
whose asserted set is unrealisable through a directed cycle. `select_relations`
adds relations greedily in increasing separation cost and **skips any that would
close a per-axis cycle**, so the asserted set is acyclic by construction and the
number is identically zero — on real noisy Proposals the guard never fires at
all. Posting a cycle around the guard is INFEASIBLE in 0.01–0.18 s, so the
mechanism is real and unreachable; removing the guard changes no outcome
measurably. Keep the guard, delete the number.

### 5.3 What it predicts, and where it stops

The metric predicts **feasibility**, not survival. Those coincide only while the
solve sits comfortably inside the time limit.

- In the **4–10-room band this Proposer serves** (§3, C13): zero confident-wrong
  relations implied a survivor in **67 runs of 67**, and no severity threshold
  up to 2 000 mm ever missed a failure.
- At **24 rooms**, out of band: **40 %** of Proposals with zero confident-wrong
  relations still fail, by reaching the 15 s limit without one. Every missed
  failure in the whole validation is at 24 rooms.

So the metric is a **training and evaluation** instrument, scoped to the band.
It is not a serving-time gate and cannot be — at serving time there is no ground
truth to score against.

One check *is* available without a truth, and belongs in the Proposer rather
than here. A posted relation is an edge in a per-axis digraph; along any directed
path the rooms sit side by side, so the Envelope must be at least the sum of
their minimum widths. The heaviest path is a lower bound, computable in
O(pairs):

```
need_x = max over directed paths of Σ min_w      need_x ≤ Envelope width
need_y = max over directed paths of Σ min_h      need_y ≤ Envelope height
```

It condemns **62 %** of infeasible relation sets with no solver and no truth. It
is sufficient and not necessary — it catches nothing at doses of one or two
relations — so it is a free pre-filter, not a substitute for the solve.
`experiments/solver-toy/mechanism6.py`.

### 5.4 Validation — what was done, and what it does not cover

The proxy was tested the only way a proxy can be: Proposals the solver is known
to project, corrupted at known doses on the relation channel alone, with
geometry, objective and hint all held at ground truth.

- **It tracks, and as a step rather than a slope.** 0 confident-wrong → 100 %
  survivor; 1 → 6 %; 2 → 0 %, with 88 % proved INFEASIBLE. The ticket asked how
  steeply failure rises with the rate; the answer is that it is not a slope.
- **It is causal.** Deleting only the injected relations restores OPTIMAL in
  **43 of 45** cases. The injected relations *alone* are infeasible in only
  10 %, so a confident-wrong relation is fatal **in company** — which means the
  better the rest of a Proposal, the more each individual error costs. A source
  that abstains freely buys tolerance for the assertions it does make: at 12
  rooms, abstaining on half the pairs takes two confident-wrong relations from
  0 % survivable to 67 %.

Two limits on that evidence, both material.

1. **The corruption is Gaussian corner noise**, which produces almost no
   reversals (0.00 per Proposal at 24 rooms up to σ = 1.5 m). A learned
   generator that misplaces a room entirely will emit exactly the reversal that
   noise cannot, so the realistic arm understates the danger and the injected
   arm overstates it.
2. **Neither source has been measured.** This validates the instrument, not
   retrieval-and-warp and not the trained model.

### 5.5 τ belongs to the solver, and here is what it does

τ is the same margin the solver uses to decide which relations to fix hard.
*Solver timing variance sweep* fitted it to **4** and found it a feasibility
knob rather than a timing one. This ticket supplies the mechanism: **what low τ
admits is confident-wrong relations, and severity is the quantity τ filters.**
At that ticket's own rig, 12 rooms, σ = 0.5 m:

| τ | asserted | confident-wrong | severity | survivors |
|---|---|---|---|---|
| 0 | 66.0 | 2.40 | **2 800 mm** | 2 / 5 |
| 4 | 55.2 | 0.20 | **200 mm** | 5 / 5 |

The τ = 0 row reproduces that ticket's "3 of 5 already fail at 12 rooms at
σ = 0.5 m" exactly. τ does not make the solver cleverer; it drops ambiguous
pairs before they can be asserted wrongly, and the ambiguous pairs are where
the errors are.

⚠️ **This inverts at 24 rooms**, where higher τ frees the search, slows it, and
loses candidates to the time limit: at σ = 0.25 m, τ = 0 gives 3 survivors of 5
and τ = 4 gives 1 of 5. Consistent with that ticket's "free at 8 rooms and
unaffordable at 24", and out of band either way.

---

## 6. Evaluation, and when training stops

### 6.1 The terminal metric is not available yet, and no partial stands in for it

`hard_pass_rate` — validator-passed plans per Proposal — needs `dim.min_area`,
`dim.min_clear_width` and `dim.min_clear_depth`, all **hard** and all
`conf: pending` on a stub table. Those are precisely the rules a weak Proposal
trips.

**No partial pass rate is published.** A number computed over the 25 fitted hard
rules would be an upper bound, and an upper bound with a plausible name is how a
wrong figure gets quoted six months later. The **route** decision was therefore
scoped so it never depends on this metric: coverage (§2.1) and the arrangement
metric (§5) decide it. The beat-retrieval ablation waits for *Ergonomic minima*
and *Fit the ENGINE_CHOICE acceptance thresholds*.

#### Four plan-quality terms that are available now

Everything above measures whether a Proposal reaches a **valid** Plan.
*Validate the arrangement metric against the solver* established that §5 predicts
**feasibility, not survival**, and is *"a training and evaluation instrument
only"*; nothing in this spec has ever measured whether a Plan is any **good**.

*The Proposal cannot express zoning* supplies three terms that do, and their one
qualifying property is that each is **computable on a corpus dwelling and on a
generated Plan by the same code** — which corner displacement is not, because a
real dwelling has no Proposal to be displaced from. Measured distributions over
2 500 Swiss dwellings are in `docs/research/zoning.md` §2; the held-out target is
the corpus distribution, not a threshold.

1. **Sleeping-group count** — components of the sleeping set, where two are one
   group if they touch or share a circulation neighbour. Real: **69.8 %** one
   group, 27.7 % two, 2.5 % three.
2. **Longest-run allocation** — whether the longest single exterior run goes to a
   habitable non-sleeping Room. Real: **73.7 %**.
3. **Social transit** — the fraction of sleeping Rooms reachable only through a
   social Space. Real: **11.1 %**.
4. **`frontage_reach` below 1.0** — a `needs_window` Room holding less boundary
   run than the frontage budget posted for it. Real: **5.88 %** of dwellings,
   3.54 % of kitchens (§4.5). Added by *A third of real kitchens have no window
   and the engine may not draw one*, and it qualifies on the same property: it is
   the same field the index already carries, computed by the same code on either
   side. It is the term that says whether a **trained** source has learned the
   interior kitchen the corpus is full of.

⚠️ These are **evaluation** terms and are not stop conditions. §6.2 stays as it
is: a source that zones well and reaches no valid Plan has not earned its place,
and none of the four has been measured on a generated Plan by anyone, because no
Proposer has been run.

**The corpus distributions above are held out on `frame_residual`, and this is
the only place on the map where an off-frame dwelling is excluded rather than
demoted.** ADR 0031. Each of the four terms is computed *on a corpus dwelling* as
the target a generated Plan is scored against, so a dwelling the conversion
sheared onto one angle — 2.89 % of the index survives every fidelity gate while
being ≥ 10° off frame — scores the model against **our own conversion error**
rather than against real housing.

⚠️ **Nothing else on this map takes that cut, and the reason is asymmetric cost.**
In the retrieval pool and in §2.3's training set, excluding thins an index ADR
0013 already calls thin, so §2.2.4 demotes and §4.5's precedent keeps. In a
**baseline** the exclusion costs nothing, because a baseline has to be *true* and
not maximal. Read across from §4.5 carefully: it kept windowless kitchens because
*"a landlocked room is not a defect in the donor, it is a fact about real
housing"* — the **splay** is such a fact, and the **shear** is not. Only §4.5's
thinness argument transfers.

⚠️ **The four rates above are quoted on the unfiltered corpus** — `zoning.md` §2's
2,500 dwellings and §4.5's 5.88 %, neither held out on a field that does not exist
yet. They move when the §2.2.1 pass lands and must be re-read then, not before.

### 6.2 Stop conditions for training

So it does not become an open-ended sink. All measured on held-out dwellings, in
the 4–10 band:

1. **Confident-wrong severity ≤ retrieval's**, on Briefs where retrieval has a
   pool. Restated in §5.2's units by *Validate the arrangement metric against
   the solver*: a *rate* compounds over a quadratic number of pairs, so a rate
   comparison flatters whichever source serves the smaller dwellings. Compare
   **per-Proposal severity distributions**, and compare the **reversal counts**
   separately — a source that emits reversals is failing differently from one
   that emits cross-axis swaps, and only the first is reliably fatal.
2. **It does not collapse where it is needed** — confident-wrong on the ~11 % of
   Briefs retrieval blanks must not exceed its own in-pool severity by more than
   a fitted margin. A model that is only good where it is redundant has not
   earned its place.
3. **After *Ergonomic minima* lands**: `hard_pass_rate` from model Proposals ≥
   retrieval's on the covered subset.

**Wall-clock stop: 50 GPU-hours total.** Past that, v1 ships retrieval-only and
states the room-count limit in the product copy, in the same breath as the other
two limits C5 already commits to. That is a shippable v1, not a failure state.

### 6.3 Serving

Per the survey: **8–16 ms per Proposal**, batched — N candidates in one call,
never a loop. **No GPU in the serving path**; GPU is a training dependency only.
Retrieval is a ranked index lookup, measured at 99 ms in Graph2Plan.

Conditioning defaults at inference are mandatory: **`europe_ch` / `cad_records`**,
surfaced to the Homeowner as a C4 Assumption.

---

## 7. What this hands to other tickets

- ***Ergonomic minima and the constraint table's missing half*** — must also
  settle the **WC-versus-bathroom area threshold** (§4.2). The corpus has one
  label for both and both routes need the split.
- ***Solver timing variance sweep*** — fitted **τ = 4**; §5.5 now carries the
  mechanism, which is that τ filters confident-wrong severity.
- ***The room-count envelope v1 promises*** — unblocked, and the route makes its
  answer largely factual: retrieval covers 4–10, dies at 11+, and source B's
  reach past 10 is unmeasured until it is trained.
- ***Fit the ENGINE_CHOICE acceptance thresholds to the corpora*** — now also
  gates §6.1's terminal metric.
- New: ***The retrieval index and warp procedure***, ***Rectangularising real
  rooms***, ***Validate the arrangement metric against the solver***.
- ✅ ***The retrieval index and warp procedure*** is **closed**, and it refuted
  the second half of this bullet. §5.4 validated the *instrument*; retrieval has
  now been scored on it and **the score is identically zero** — §2.2.2's warp
  cannot produce a confident-wrong relation, so *"a warped Proposal's severity is
  the natural fidelity axis the warp-budget question was missing"*, which this
  bullet used to say, is **false**. Severity is the fidelity axis for **source B**
  and for nothing else on this page. Retrieval's axis is per-room area.
  **The trained model's first eval still owes all four numbers** — severity,
  count, reversals, abstain rate, per Proposal — plus §6.1's three plan-quality
  terms, and it is still the case that neither source has been scored on those.
- ✅ ***Can a starved candidate be refused before the solve*** is **closed** and it
  refused the thing it was raised to specify. No Proposal-level screen: unsound at
  82 %, its only sound form never fires, and it would sit after the expensive step
  — the projection costs **less** than the warp that feeds it. What it hands on is
  a **measurement**, not a decision: the Plan-level twin of §7.6's best-of-*m*
  curve, since `acceptance-bar.md` §11.1 now declares starvation on the Plan and
  has one under-powered number for it.
- From ***The Proposal cannot express zoning***, to the holders of the files this
  ticket does not write. Four rules to `rules.json`, one flag to
  `room-constraints.json`, and one soft term to whoever next opens the objective —
  all specified in `docs/research/zoning.md` §5, none written here, because
  `rules.json` has four claimants and this ticket has none of them.
- ✅ From ***Fit the `ENGINE_CHOICE` acceptance thresholds to the corpora***, via
  `acceptance-thresholds.md` §13 — *"a candidate's prior of clearing the bar is
  set by a layer the Proposal does not carry"*. **Discharged** by §4.5, which
  turns it into the reason the corpus is admitted unfiltered on glazing. ✅ **The
  half addressed to *A donor's enclosed void becomes area nobody asked for* is
  discharged too** — §2.2.8 and ADR 0028. The Proposal *does* now carry part of
  the layer that sets a candidate's prior of clearing the bar: an enclosed void
  and the Room it belongs to, which is what stopped an arbitrary 1.5 m² landing on
  a small Room and breaching `dim.max_area`.
- From ***A donor's enclosed void becomes area nobody asked for***, to the holders
  of the files it does not write:
  - **`experiments/rectangularise/fit_rects.py`** — a **fourth** owed per-record
    field, the void components as frame spans each with its **donor
    owner**. ⚠️ **Ticket 61 changed what this field holds and added a sixth
    beside it**: a void is now every complement component *other than the
    `notches_used` notch spans*, and those spans are themselves the sixth owed
    field (ADR 0020's second amendment). The two are one computation — `env_at`
    already returns the notch rectangles and throws them away, and the void is
    defined as the rest. `notch_share` in `warp/absolute_area.py` splits
    enclosed from boundary-touching, which is **no longer the line**;
    `watershed` already labels every cell with the Room that owns it.
    `experiments/void/provenance.py` is the reference. **Take it with the other
    three** — cut-line frame, per-pair relation provenance, `frontage_reach` —
    they are four statistics off one pass.
  - **`experiments/warp/`** — `fit_warp.warp_model` gains the void variables, and
    every fidelity figure quoted on a voided candidate is superseded by the
    charged measurement (§2.2.8). ⚠️ **`absolute_area.py` has no output for
    realised unassigned area at all**, which is why this had to be measured from
    outside the rig; add it on `acceptance-thresholds/`'s rule. **Ticket 57 holds
    that directory** and is re-running best-of-*m*.
  - **`docs/research/solver-formulation.md`** — H3 closes the hole and the
    objective is L1 corner displacement, so the Proposal's `voids` field is the
    thing that turns an arbitrary repair into a directed one. Nothing in that file
    knows the field exists.
  - ⚠️ **The constrained notch and the charged void are one unmeasured cost.**
    §2.2.3's `s`-holding equality and §2.2.8's void term both constrain the warp
    solve, and `experiments/warp/`'s `ring` arms reach the notch invariant by
    re-sizing the box instead. The INFEASIBLE rate of the genuinely constrained
    model has never been measured, and it should be measured **once, for both**.
- From ***A third of real kitchens have no window and the engine may not draw
  one***, to the holders of the files it does not write:
  - **`experiments/rectangularise/fit_rects.py`** — `frontage_reach` is a new
    per-record field (§2.2.1) and the fit already holds both inputs: the room
    polygons and the assembled envelope. It is one intersection per
    `needs_window` Room. `experiments/corpus-smoke/boundary_contact.py` computes
    it today and is the reference. This joins the **cut-line frame** and
    **per-pair relation provenance** that §2.2.1 already owes the same file.
  - **`experiments/solver-toy/`** — nothing on this map has measured what
    `select_relations`' positive-cost filter actually posts, and §4.5's choice of
    a rank over a gate turns on it: a landlocked donor is only *provably*
    infeasible if the separations that enclose the Room survive selection. Measure
    it and the gate becomes arguable; leave it and the rank is the honest posting.
  - **`docs/spec/acceptance-bar.md`** — `win.habitable_has_window` now has three
    corpus costs answering three questions (§4.5). None is wrong; the file should
    say which is which rather than let a reader take 0.4519 for the retrieval
    cost.

## 8. Honest limits

- Coverage is measured on **Swiss Dwellings only**, and simulated Briefs are real
  dwellings. Real Homeowner Briefs are not corpus samples. The cross-paired test
  (§2.1) is the honest version — a Brief whose envelope did not come paired with
  its programme — but it still draws both from the corpus.
- **±10 % / ±15 % is still a stated budget, and it now matters less than it
  looked.** Where warp fidelity breaks is measured (§2.2.7) and it is not on
  either of those axes. What the two terms still do is keep the *pre-warp* pool
  honest and bound how far the fit has to reach; neither has been fitted, and a
  ticket that wants to move them should move them against §2.2.7's decline rate,
  not against severity.
- The envelope proxy is the **minimum-area rotated rectangle**. Median fill is
  **0.79** and p5 is **0.61**, so real dwellings are markedly non-rectangular —
  which ADR 0003 caps at "bbox minus ≤2 notches". ✅ **How many fit inside that
  cap is now measured**: 90.16 % of converted dwellings use both notches, 8.72 %
  one, 1.12 % none, and ADR 0016's own conversion rate — 90.3 % of Swiss — is the
  share that fits the cap at all. ⚠️ **The direction of the bound turned out to be
  the opposite of the worry.** The cap does not stop real dwellings entering the
  index; it stops a **rectangular Brief** leaving it, because a source with two
  notches cannot serve an Envelope with none (§2.2.3).
- **Fidelity is measured against the Brief, never against a Homeowner.** Every
  per-room "target" here is a real dwelling's real room area standing in for what
  a person would have asked for. That is the best proxy available and it is not
  the thing.
- ⚠️ **The best-of-8 figures are drawn from a 2,317-dwelling converted sample**,
  not the full index — a pool of 87 in production is a pool of 8 here — so they
  are a lower bound on what the shipped index can do.
- ✅ **A warped Proposal has now been through the projection solve** — §2.2.9,
  291 candidates. ⚠️ **Read every per-room area figure on this page as a *warp*
  result and never as plan yield**: 82,0 % of the candidates that look starved on
  the warped rectangles are served once the solve sizes them, because it posts
  the floors hard and moves floor between Rooms at Σ Space unchanged. ⚠️ And the
  arm is **one-rectangle donors only** (46,4 % of the index, skewed small), which
  is why its own base rate is 18,3 % against `ringmarket`'s 25,5 %.
- ⚠️ **The projection reads a perimeter Room 3,9 % smaller than the bar does.**
  `solver.py` erodes all four sides; ADR 0001 does not erode at the Envelope
  boundary. On a 250 mm grid the 75 mm ring is unrepresentable, so this is
  structural: the solve is strictly stricter than `dim.statutory_min_area`, and
  1,51 % of warped Rooms fall in the gap. Ticket 56's ring, where it cannot be
  removed.
- No plan produced by a **warp** has been rendered or eyeballed. *Look at the
  converted corpus* rendered the conversion; nothing has yet drawn what comes out
  the far side of §2.2.2, and ADR 0017 is the standing reminder that a metric is
  not a look. ⚠️ **§2.2.8's void was measured and not looked at either** —
  `render_sheet.py` exists and no voided candidate has been drawn after its warp.
- **v1 models no vertical service void.** There is no shaft, riser or duct object,
  no Room type for one, and an enclosed pocket could not be a Room in any case —
  `circ.potential_reachability` refuses it. **2.0 % of §2.2.8's void area really
  is a dropped `SHAFT`/`VOID`/`TECHNICAL_AREA`**, and it is charged to a bordering
  Room like the other 98 %. That is wrong, it is about 0.3 m² on one dwelling in
  fifty, and it is stated here rather than hidden inside the residue figure.
- ⚠️ **Source B has the same problem in a form nobody can measure.** Its boxes need
  not tile, so its slack is diffuse rather than in identified components: it emits
  an empty `voids` list not because it has none but because it cannot name them,
  and H3 closes its holes by the same L1 tie §2.2.8 removed for source A. The
  Proposer source B row owns that, alongside its unmeasured per-room absolute area
  fidelity.
- ⚠️ **`frontage_reach` is necessary and not sufficient, and it is quoted as a
  lower bound throughout §4.5.** It measures boundary **contact** on the donor,
  because §2.2.6 records that the conversion cannot tell `exterior` from `party`.
  A Room holding 4 m of donor boundary may hold 4 m of *party* edge in the target
  Envelope and take no window at all. So **6.39 % is the floor of the residue and
  not its size**, and the quantity that would bound it — the joint distribution of
  donor contact against target-Envelope exposure — needs the Brief's Envelope and
  has never been measured. Nothing in §4.5 rests on the upper end: the rank
  demotes, it does not exclude, so a proxy that under-counts costs ordering and
  never coverage.
