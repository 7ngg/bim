---
id: 46
title: The dwelling that is built on two angles
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - experiments/rectangularise/
  - docs/research/rectangularisation.md
---

# The dwelling that is built on two angles

## Question

**The conversion silently emits a different flat, and scores it as a middling
one.** *Look at the converted corpus* found it by rendering, and it is the whole
p5 tail — ADR
[0017](../../adr/0017-three-of-the-conversions-fidelity-headlines-are-constraints-restated.md),
failure mode 1.

`measure_swiss.dwelling_frame` rotates a dwelling onto **one** angle, taken from
the minimum rotated rectangle of the whole room union. A dwelling built on two —
a bedroom wing splayed off a living spine, which real housing does — has every
room in the second wing sheared into the first wing's frame. The output is a
plausible home. It is not the home that was converted.

| room off frame by | dwellings | cell agreement | worst-room IoU |
|---|---:|---:|---:|
| 0–2° | 90.2 % | 0.941 | 0.768 |
| 2–5° | 3.5 % | 0.844 | 0.699 |
| 5–10° | 3.5 % | 0.876 | 0.745 |
| **10–20°** | **1.5 %** | **0.705** | **0.167** |
| 20°+ | 1.2 % | 0.676 | 0.429 |

Measured over 400 dwellings by `experiments/rectangularise/void_census.py`.
Rendered examples: `render_sheet.py --pick=worstroom`, sheets at
`out/sheets/SHEET.html`.

**What has to be decided: what the conversion does with a dwelling whose rooms
are not all on one angle.** Three candidates, and none is obviously right:

1. **Refuse it.** Add an off-frame gate to the reject rule — cheapest, and it
   thins the corpus by roughly 3 % on top of the 9.5 % already refused. But it
   removes exactly the splayed-wing plans, and the splayed wing is an
   arrangement a Homeowner will ask for.
2. **Re-frame per wing.** Segment the dwelling into angle-coherent components,
   fit each in its own frame, then reconcile. Expensive, and the reconciliation
   is a new problem: two frames meeting at an angle is not something the
   Envelope (ADR 0003, a rectilinear ring) can express, so a re-framed dwelling
   may be unrepresentable anyway.
3. **Accept and label.** Keep the sheared output and carry a per-dwelling
   `frame_residual`, so retrieval (ticket 23) can down-weight or exclude them
   without the corpus losing them. The Proposer then learns from a sample it
   knows is distorted rather than one it believes is faithful.

**What this ticket must settle beyond the choice:** whether `frame_residual` is
published on every converted record regardless — it costs nothing and it is the
only reason anyone would ever notice this again.

**Do not re-litigate** ADR 0008's conversion, the reject rule's existence, or
rectangles over polygons. This ticket decides what happens to one population.

**One thing the reading already establishes.** Nothing published faces this
problem: every generator in `docs/research/floorplan-generation-stack.md` fits
axis-aligned rectangles, and every corpus the field trains on — RPLAN, LIFULL —
is already orthogonal, so the second angle never arrives. Swiss Dwellings is
surveyed geometry. **There is no prior art to shop for**, which is a finding and
not a gap in the reading.

## Resolution

**Keep them, label them, and add no cut — because the rank the map already ships
was demoting them all along, and the gate was already refusing 40 % of them.**
[ADR 0031](../../adr/0031-a-two-angle-dwelling-is-kept-labelled-and-demoted-by-a-rank-that-already-exists.md),
`docs/research/rectangularisation.md` §15.

### The ticket's premise was half wrong in both directions

**The population is bigger than stated and the residue is smaller.** 4,79 % of
the converted index has a room ≥ 10° off frame, not the ~3 % the ticket assumed —
but `proposer.md` §2.2.4's `worst_room_iou ≥ 0,30` gate is **already refusing
39,6 % of it**, and **28,6 % of everything that gate removes is off-frame**. The
map has been discarding two-angle dwellings since the gate landed, unlabelled,
and nobody knew. The residue this ticket actually decides on is **67 dwellings,
2,89 % of the index**. The probe reproduces the spec's own 6,65 % index cost
exactly, which is what makes the join trustworthy.

### The four decisions

**1. Accept and label** — the ticket's candidate 3. Refusing discards a usable
*arrangement* to punish a *shape* defect: adjacency and separation are posted
hard in the conversion and survive the shear intact, and arrangement is what a
donor hands over. Accepting silently is not available, because the harm is real
and currently invisible — see 2.

**2. `frame_residual` is published on every record regardless**, which is what the
ticket asked to settle, and it is defined here because the ticket named it without
defining it: **the area-weighted mean deviation of a dwelling's Rooms from its
dwelling axis, in degrees**. Continuous, whole-dwelling, **no threshold inside
it**. `off_frame_max` is a one-room statistic on a whole-dwelling defect; an area
*share* buries a 5° cut in a raw field.

It earns its place because it is **not derivable from what the record holds**. At
every stratum of `worst_room_iou`, an off-frame dwelling scores 5–11
cell-agreement points lower at the same IoU (−0,110 / −0,074 / −0,088 / −0,054).
A per-room minimum cannot be a sufficient statistic for a whole-dwelling shear.

**3. No gate, no partition, no ranking term — and this is the surprising half.**
On §2.2.4's own stated rule `frame_residual` is *eligible* for a hard gate: it is
a pure donor fact, like `worst_room_iou` and unlike `frontage_reach`. It gets none.

- **There is no knee.** Cell agreement declines smoothly — 0,944 / 0,914 / 0,891 /
  0,854 / 0,802 / 0,778 — with no elbow. A partition would be a fitted constant
  chosen for the look of the table, the thing §2.2.4 exists to refuse.
  `frontage_reach` partitions at 1,0 only because a hard constraint sits there.
- **The existing pre-rank has already done it.** Off-frame donors carry low IoU,
  so ordering on `worst_room_iou` descending sorts them down unprompted: a donor
  at 4–8° residual sits at the **10,6th percentile** of the surviving pool. Against
  a bucket of 58–87 with `m = 8` drawn from its head, it is not taken.

**A gate is for a candidate that is wrong; a rank is for one that is worse.**

**4. The frame itself changes, and only inside the pass `fit_rects.py` already
owes.** The union mrr is fitted to *both* wings, so on a two-angle dwelling it
returns an angle that can be neither. The **area-weighted modal room angle** sits
on the dominant wing by construction. Counted it is a coin flip — 377 better, 357
worse — and **weighed it is not close**: gains mean 0,923° and sum 347,8°,
regressions mean 0,057° and sum 20,4°. Net **+327,4°**, dominating the shipped
frame at every quantile, rescuing ~30 dwellings across any line while pushing 1.

⚠️ **It may never be a re-run of its own.** A frame change re-bases
`swiss_fit_k2.json` and every corpus figure on this map with it. Riding the pass
§2.2.1 mandates for the five index fields, the marginal cost is one function.
`frame_of` in `frame_choice.py` is the reference implementation, drop-in for
`dwelling_frame`; **the conversion is frozen until that pass runs.**

### Three consumers, two answers

| consumer | answer |
|---|---|
| retrieval pool | keep, demoted by the rank that exists |
| source B training set | keep, unfiltered — §4.5's thinness argument |
| source B **evaluation baseline** (§6.1) | **exclude, hard** |

The third is the asymmetry. §6.1's four plan-quality terms are computed *on corpus
dwellings* as the target a generated Plan is scored against, so a sheared dwelling
scores the model against **our own conversion error**. Everywhere else a cut costs
index depth; in a baseline it costs nothing, because a baseline must be **true**
and not maximal. ⚠️ §4.5's reasoning does **not** transfer: it kept windowless
kitchens because *"a landlocked room is not a defect in the donor, it is a fact
about real housing"* — the **splay** is such a fact, the **shear** is ours.

### Candidate 2 is refused on scope, and deliberately not priced

Re-framing per wing produces a dwelling ADR 0003's rectilinear ring cannot
express, and ADR 0030 has just measured that object at a median of **6**
rectangles against a family yielding 1–4. It would buy a new reconciliation
problem to produce a donor for a Brief v1 cannot serve, in a shape family §13.3
already refused to widen. ⚠️ This is the one refusal here with no number under it.

### ⚠️ Two corrections this ticket owed to shipped text

**ADR 0017's 0,167 is a six-dwelling median.** Its failure-mode-1 table is on 400
dwellings and its last two bands hold 6 and 5 of them; the IoU reversal between
them (0,167 then 0,429) should have been read as a sample size. Over the full
index they are **0,397** and **0,353**, monotone, and the population is 4,79 %
not 2,7 %. The figure was quoted in three places — this ticket, `§12.3` and the
ADR — and all three are struck. Nothing rested on it.

**`CONTEXT.md`'s *Dwelling axis* presumed a dwelling has one.** One in twenty does
not. The term is amended to say the axis is **assigned by the conversion**, not
held by the dwelling, and *Frame residual* is added beside it with two `_Avoid_`s.

### What this does not settle, and it is named on the ADR

**What an off-frame donor costs a warped candidate.** Everything measured is on
the donor *record*. Whether a sheared donor yields a worse **Plan** is unmeasured,
because `experiments/warp/` is held by *What best-of-pool is worth at production
pool depth* and this ticket may not reach into it. If that measurement ever
contradicts decision 3, **the rank is where it lands, not the gate**.

### Artifacts

- `docs/adr/0031-…` — the decision.
- `docs/research/rectangularisation.md` **§15** — eight subsections, all on the
  full 2,317-dwelling index.
- `experiments/rectangularise/off_frame_gate.py` — the join to the shipped gate,
  which reproduces its 6,65 %.
- `experiments/rectangularise/frame_choice.py` — the two frames, plus `frame_of`
  and `frame_residual_of` as the reference implementations.
- `experiments/rectangularise/frame_residual.py` — the published quantity, the
  knee that is not there, and the cut that was refused.
- `experiments/rectangularise/README.md` — three traps, the first being the one
  that produced the 0,167.

### Declared on resolution

`docs/spec/proposer.md` (§2.2.1 field and the five-obligation pass, §2.2.4's
no-cut paragraph, §6.1's baseline exclusion), `CONTEXT.md`, `docs/adr/0017-…`.
All three were unclaimed — the open tickets at the time were 43
(`solver-toy`, `solver-formulation.md`), 45 (`homeowner-surface.md`) and 57
(`warp`, `proposer-architecture.md`) — so the `writes:` rule held. Recorded here
rather than taken quietly, per the map's Notes.
