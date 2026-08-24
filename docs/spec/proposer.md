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

1. Both v1 sources can emit a genuine confidence — retrieval from how far each
   room had to move under the warp, the model from its own logits — and either is
   strictly better than a geometric proxy computed after the fact.
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

**The budget's exact values are an ENGINE_CHOICE and are not yet fitted.** ±10 %
and ±15 % are the values the coverage table above was measured at. Where warp
fidelity actually breaks is unmeasured — it belongs to *The retrieval index and
warp procedure*.

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

⚠️ **Superseded in its premise by ADR
[0014](../adr/0014-a-room-is-one-or-two-rectangles-and-the-proposal-decides.md),
not in its method.** Downstream now places **one or two** rectangles per Room
(§1), so the fit below has a second rectangle available per room and the reject
rule it produced is measured against a constraint that has moved. The conversion
is still one CP-SAT fit per dwelling and still drops what it cannot represent;
**what is re-owed is the 31 % price**, by *Re-measure the conversion at two
rectangles per Room*. Everything else in this section stands.

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

**This invalidates §2.2's coverage table.** The 9.5 % and 12.4 % blank rates were
measured on the unconverted corpus. Conversion removes 31 % of Swiss Dwellings and
takes it disproportionately from the top of the band — 83 % of 4-room dwellings
convert against 46 % of 10-room — so retrieval's pool shrinks most where it was
already thinnest. *The retrieval index and warp procedure* must re-measure before
any coverage figure here is quoted again. It is affordable at all because ADR 0005
gives a blanked Brief somewhere to go.

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

⚠️ **A defect this exposed, and it is live at k = 1 today.** Nothing in step 3
filters on a positive cost at all, so a Proposal whose boxes **overlap** — which
a trained model emits routinely, and which §5.2's own noise model produces — has
separations asserted for pairs the Proposal never separated. This predates parts
and is owed by *The retrieval index and warp procedure*.

For each unordered pair (i, j) of parts:

1. compute the four separation costs — left-of, right-of, above, below
2. `direction = argmin`; `margin = second_best − best`
3. `margin < τ` → the pair **abstains**: the solver leaves it free
4. otherwise the pair is **asserted**

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
- ***The retrieval index and warp procedure*** and the trained model's first
  eval — §5.4 validated the *instrument*; neither source has been scored on it.
  Both must report **severity, count, reversals and abstain rate** per Proposal,
  and a warped Proposal's severity is the natural fidelity axis the warp-budget
  question was missing. **They now also report §6.1's three plan-quality terms**,
  which is the first time either source can be scored on anything but feasibility.
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
- **±10 % / ±15 % is a stated budget, not a fitted one.** Where warp fidelity
  actually breaks is unmeasured.
- The envelope proxy is the **minimum-area rotated rectangle**. Median fill is
  **0.79** and p5 is **0.61**, so real dwellings are markedly non-rectangular —
  which ADR 0003 caps at "bbox minus ≤2 notches". **How many real dwellings fit
  inside that cap is unmeasured**, and it bounds retrieval from a direction this
  spec has not tested.
- No plan has been rendered or eyeballed, here or in *Acquire the datasets*.
