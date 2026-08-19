# The Proposer — spec

Ticket 08, *What the model proposes, and how it is trained*.
Contract it must satisfy: `docs/research/solver-formulation.md`
§"What this formulation requires the Proposal to look like".
Architecture it takes: `docs/research/proposer-architecture.md` §7.1.
ADR: [0005](../adr/0005-the-proposer-has-two-sources.md).

Units are integer millimetres and Envelope grid units throughout, per ADR 0001.

---

## 1. What is proposed

**Unchanged from the solver contract**, which is already the spec: exactly *n*
axis-aligned boxes, one per Brief Room, as four integers in Envelope grid units;
no validity guarantee; no adjacency graph; no wall geometry. Nothing in this
ticket reopens it.

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

`docs/research/proposer-architecture.md` §7.1, unchanged: a Brief-conditioned
room-set transformer emitting one box per Brief Room. ~20M params, `d = 512`,
4–8 layers, 128 coordinate bins per axis, envelope cross-attention, per-room
target-area conditioning, `(region, corpus, annotation_provenance)` tokens.

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

### 4.4 Rectangularisation is unspecified and load-bearing

Every stage downstream places **one rectangle per room**, and real rooms are not
rectangles — ResPlan reports 43.2 % exactly rectangular, 62.3 % at 2 % tolerance.
Both sources need real polygons turned into rectangles, and how is unowned:
§7.4 of the survey flagged it as belonging to tickets 01/04, and both are closed
without settling it.

Ticketed as *Rectangularising real rooms*. Both sources block on it, so it is on
the critical path rather than a preprocessing detail.

---

## 5. The arrangement metric

Assigned to this ticket by *Proposer architecture survey* §7.1: no published
metric measures what the solver actually consumes.

### 5.1 Definition

Run the **solver's own extractor** on both sides, so the metric cannot drift from
the thing it predicts. For each unordered pair (i, j) of Brief Rooms:

1. compute the four separation costs — left-of, right-of, above, below
2. `direction = argmin`; `margin = second_best − best`
3. `margin < τ` → the pair **abstains**: the solver leaves it free
4. otherwise the pair is **asserted**

Ground truth is the same extractor over the held-out real dwelling's
rectangularised rooms.

### 5.2 What is reported — three numbers, never one

| | |
|---|---|
| **agreement** | asserted, and matches truth |
| **abstain rate** | pairs below τ |
| **confident-wrong** | asserted, and contradicts truth — **the headline** |

Collapsing these into a single accuracy figure hides the only failure that costs
a candidate. An abstain leaves the solver free. A **confident-wrong relation
becomes a hard constraint and makes the model INFEASIBLE in under 0.1 s.**

Plus **cycle rate** — the fraction of Proposals whose asserted relation set is
unrealisable, because a directed cycle in the implied x- or y-ordering is
infeasible however correct each pair looks alone.

### 5.3 The metric must be validated before it is trusted

It is a proxy, and this map has already been bitten once by an unvalidated one
(overlap). Before any architecture is scored on it: inject confident-wrong
relations at known rates into ground-truth Proposals and show solve failure rises
with the rate. **If it does not, the metric is wrong and gets redefined, not
excused.** `experiments/solver-toy/probe5.py` already runs infeasible Proposals,
so the harness exists.

### 5.4 τ belongs to the solver, not here

τ is the same margin the solver uses to decide which relations to fix hard, and
it trades solve time against infeasibility: high τ fixes fewer relations, so the
search is freer and slower; low τ fixes more, so it is faster and fails more.
That is a timing question. New obligation on *Solver timing variance sweep*.

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

### 6.2 Stop conditions for training

So it does not become an open-ended sink. All measured on held-out dwellings, in
the 4–10 band:

1. **Confident-wrong rate ≤ retrieval's**, on Briefs where retrieval has a pool.
2. **It does not collapse where it is needed** — confident-wrong on the ~11 % of
   Briefs retrieval blanks must not exceed its own in-pool rate by more than a
   fitted margin. A model that is only good where it is redundant has not earned
   its place.
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
- ***Solver timing variance sweep*** — must fit **τ** (§5.4).
- ***The room-count envelope v1 promises*** — unblocked, and the route makes its
  answer largely factual: retrieval covers 4–10, dies at 11+, and source B's
  reach past 10 is unmeasured until it is trained.
- ***Fit the ENGINE_CHOICE acceptance thresholds to the corpora*** — now also
  gates §6.1's terminal metric.
- New: ***The retrieval index and warp procedure***, ***Rectangularising real
  rooms***, ***Validate the arrangement metric against the solver***.

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
