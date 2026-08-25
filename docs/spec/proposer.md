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
candidate only if all three hold:

| Gate | Value |
|---|---|
| room multiset | exact match in the Brief vocabulary (§4.1) |
| total floor area | within **±10 %** of the Brief's |
| envelope aspect ratio | within **±15 %** of the Brief's |

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
| `notches_used`, and each notch's index span | the Envelope shape the candidate carries (§2.2.3) |
| **per-pair relation provenance** — for every axis-pair, whether the *corpus* asserted that separation or the *conversion* invented it | §2.2.5; ADR 0016 measures the invented share at **12.62 %** of axis-pairs and only the conversion can tell them apart |
| the entrance-adjacent Room, if the corpus identifies one | §2.2.6 |
| `RegionProfile`/`CorpusProvenance` = `AZ`/`CH` | C14 |

The last two are **new obligations on the conversion**, which today emits
`rel: {same, spurious}` as counts rather than per pair. That is a change to
`experiments/rectangularise/fit_rects.py`, handed to its holder — this ticket
specifies the field, not the emitter.

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
minimise   (1000 · n) · worst  +  Σ_r  w_r · dev_r
subject to Σ gx = W,  Σ gy = H,  every gap ≥ 1               (grid units)
           dev_r · target_r ≥ 1000 · |area_r − target_r|      (per-mille)
           worst = max_r dev_r
           every part's span ≥ its Room's realisable minimum, both axes
           every part within dim.aspect_ratio_hard
           every two-part Room's shared edge ≥ ADR 0014's join
```

Five things about that programme are decisions, not incidentals:

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
frame — it is the part of the bbox no part covers — so it warps along with
everything else, for free. Its position and proportion are then a **real
dwelling's**, measured, rather than the invented constant the alternative needs.

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

1. **Gate** — dict hit, then scan the bucket on total area and aspect. Free.
2. **Pre-rank** — order the bucket by the affine warp's worst-room deviation,
   which needs no solve. A proxy, and only for choosing whom to warp.
3. **Warp** the head of that order, then **re-rank on the real post-warp
   number**. A warp that declines (§2.2.2) drops out here.
4. **Take `m`**, never two orientation variants of the same source dwelling
   unless the pool is exhausted.

**Diversity is a post-hoc filter, not a ranking term.** As a term it needs a
weight against area fidelity that nobody can fit; as a filter it is a rule with
no free parameter.

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

⚠️ **Two limits on the fidelity figures.** The pool here is drawn from the 2,317
converted dwellings of the ADR 0016 sample, not the full index, so a pool of 87
in production is a pool of 8 here — best-of-8 is what was measured and the full
index can only do better. And the stated-versus-invented weighting was probed at
a **30 % stated share**, which is a probe parameter and not a measurement of what
Homeowners state.

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

#### Three plan-quality terms that are available now

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

⚠️ These are **evaluation** terms and are not stop conditions. §6.2 stays as it
is: a source that zones well and reaches no valid Plan has not earned its place,
and none of the three has been measured on a generated Plan by anyone, because no
Proposer has been run.

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
- From ***The Proposal cannot express zoning***, to the holders of the files this
  ticket does not write. Four rules to `rules.json`, one flag to
  `room-constraints.json`, and one soft term to whoever next opens the objective —
  all specified in `docs/research/zoning.md` §5, none written here, because
  `rules.json` has four claimants and this ticket has none of them.

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
- No plan produced by a **warp** has been rendered or eyeballed. *Look at the
  converted corpus* rendered the conversion; nothing has yet drawn what comes out
  the far side of §2.2.2, and ADR 0017 is the standing reminder that a metric is
  not a look.
