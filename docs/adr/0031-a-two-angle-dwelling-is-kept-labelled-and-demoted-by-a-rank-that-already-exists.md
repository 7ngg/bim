# A two-angle dwelling is kept, labelled, and demoted by a rank that already exists

**Status:** accepted
**Date:** 2026-08-28
**Ticket:** *The dwelling that is built on two angles*
**Amends:** [ADR 0008](0008-a-corpus-dwelling-is-converted-by-solving-it.md) — the
frame the conversion rotates onto
**Corrects:** [ADR 0017](0017-three-of-the-conversions-fidelity-headlines-are-constraints-restated.md) —
failure mode 1's rates and its 0,167
**Related:** [ADR 0016](0016-the-conversion-names-its-own-ls.md),
[ADR 0003](0003-the-envelope-is-an-inner-face-ring-of-typed-edges.md),
[ADR 0030](0030-the-real-boundary-arm-is-run-and-the-blockers-are-upstream-of-the-solver.md)

## Decision

**A dwelling whose rooms are not all on one angle is converted, kept, and
labelled. It gains no gate, no partition and no ranking term, because the rank
the map already ships demotes it to the floor of the pool without being told
to.** Four parts, and the third is the one that will surprise a reader.

### 1. `frame_residual` is a fifth obligation on the conversion, and a twelfth field on the index record

**`frame_residual` — the area-weighted mean deviation of a dwelling's rooms from
its dwelling axis, in degrees.** Published on every converted record regardless
of value, which is what the ticket asked to settle.

Continuous, whole-dwelling, and **carrying no threshold inside it**. That is the
whole reason it is this quantity and not one of the two obvious alternatives:
`off_frame_max` is a one-room statistic on a whole-dwelling defect, and off-frame
*area mass* buries a 5° cut inside a field whose job is to be raw.

It is published because it is **not derivable from what the record already
holds**. At every stratum of `worst_room_iou` an off-frame dwelling scores 5 to
11 cell-agreement points lower than an on-frame one — `rectangularisation.md`
§15.2. A per-room minimum cannot be a sufficient statistic for a whole-dwelling
shear, and it is not.

⚠️ **`proposer.md` §2.2.1 said four new obligations and it is now five.** Take
them in one pass, as that section already directs: they are five statistics off
the same records and five passes is four wasted re-fits.

### 2. The frame changes to the area-weighted modal angle — and only inside that pass

`dwelling_frame` takes the angle of the minimum rotated rectangle of the **whole
room union**, so on a two-angle dwelling the angle it returns is fitted to both
wings and can be neither. The **area-weighted modal room angle** sits on the
dominant wing by construction.

Counted per dwelling it is a coin flip — 377 better, 357 worse. **Weighed it is
not close**: the improvements mean 0,923° and sum 347,8°, the regressions mean
0,057° and sum 20,4°. The regressions are estimator noise at a tenth of a degree;
the gains are the defect. Net +327,4° over 2 317 dwellings, dominating the
shipped frame at every published quantile.

**It rides the re-run that `fit_rects.py` already owes and is never a re-run of
its own.** A frame change re-bases `swiss_fit_k2.json`, which every corpus figure
on this map derives from; standalone, that is a whole re-reading bought for a
tail improvement. Riding the pass part 1 mandates, the marginal cost is one
function.

⚠️ **The conversion is frozen until that pass runs.** Every number published
before it — this ADR's included — is on the union-mrr frame, and the two frames
are named wherever they differ.

### 3. No gate, no partition, no ranking term

The precedent invited one. §2.2.4 gates *and* ranks `worst_room_iou` because it
is a **pure donor fact**, and partitions `frontage_reach` without gating it
because that one is joint with the Brief's Envelope. `frame_residual` is a pure
donor fact — it compares a dwelling's rooms to that dwelling's own axis and no
Brief is involved — so on the stated rule it is eligible for a hard gate.

**It gets none, for two reasons that compound.**

**There is no knee.** Cell agreement declines smoothly across the residual —
0,944 / 0,914 / 0,891 / 0,854 / 0,802 / 0,778 over the bands of §15.4 — with no
elbow anywhere. A partition placed on it would be a fitted constant chosen for
the look of the table, which is the thing §2.2.4 exists to refuse. `frontage_reach`
could partition at 1,0 only because the solver's own hard constraint sits there.
Nothing sits anywhere here.

**And the existing rank has already done it.** §2.2.4 pre-ranks on
`worst_room_iou` descending. Off-frame dwellings carry low IoU, so the rank
already sorts them down — a donor at 4–8° residual sits at the **10,6th
percentile** of the surviving pool. With a bucket of 58–87 and `m = 8` drawn from
its head, that donor is not taken. A second cut on a correlated quantity would
demote what is already at the floor, and charge a fitted constant for it.

**A gate is for a candidate that is wrong; a rank is for one that is worse.** An
off-frame donor is worse. `worst_room_iou < 0,30` is wrong — a room is
essentially not that room — and that gate stays exactly where it is.

### 4. The evaluation baseline excludes them, and it is the only place a hard cut is right

Three consumers read the converted corpus and they do not get one answer.

| consumer | answer | why |
|---|---|---|
| **retrieval pool** | keep, demoted by the existing rank | the shear damages room *shape*; adjacency and separation are posted hard and survive it, and arrangement is what a donor hands over |
| **source B training set** | keep, unfiltered | §4.5's precedent — do not thin a corpus ADR 0013 already calls thin for a 2,89 % effect the model can be measured on |
| **source B evaluation baseline** (§6.1) | **exclude, hard** | a hard cut here costs nothing and buys truth |

The third is the asymmetry worth stating. §6.1's four plan-quality terms are
computed *on corpus dwellings* as the target a generated Plan is scored against.
A sheared dwelling is an artefact of our own conversion, so scoring against it
measures the model against our error. Everywhere else a cut costs index depth;
in a baseline it costs nothing, because a baseline needs to be **true** and not
maximal.

⚠️ **§4.5's reasoning does not transfer, and reading across from it is the trap.**
It kept windowless kitchens because *"a landlocked room is not a defect in the
donor, it is a fact about real housing"*. The **splay** is a fact about real
housing. The **shear** is not — it is ours. What survives from §4.5 is only the
thinness argument, and that one holds.

## What was refused, and on what ground

**Refusing the population outright** — the ticket's first candidate. It is the
one option the measurement made cheaper than expected, because the IoU gate is
already taking 39,6 % of it, and it is still refused: the residue is 67
dwellings, 2,89 % of an index ADR 0013 calls thin, and refusing them discards a
usable *arrangement* to punish a shape defect the warp re-sizes anyway.

**Re-framing per wing** — the second candidate, refused on **representability,
not cost, and without being priced**. Two frames meeting at an angle is not
expressible in ADR 0003's rectilinear ring, and ADR 0030 has just measured that
object at a median of **6** rectangles against a family yielding 1–4. A re-framed
dwelling would be a donor for a Brief v1 cannot serve, in a shape family §13.3
already refused to widen. ⚠️ This is the one refusal in this ADR with no number
under it.

## Consequences

1. **`fit_rects.py` owes five fields, not four**, and `dwelling_frame` changes in
   the same pass. `measure_swiss.py`, `void_census.py` and the ticket-46 probes
   all import that function; the frame becomes a stated input to the record
   rather than an angle discarded after rotation.
2. **`proposer.md` gains a field in §2.2.1, a paragraph in §2.2.4 recording why
   no cut was added, and an exclusion in §6.1.** The §2.2.4 paragraph matters
   more than it looks: without it the next reader sees a pure donor fact that is
   not gated and reads it as an oversight.
3. **ADR 0017's failure mode 1 is corrected.** Its 0,167 is a six-dwelling median
   and the true figure is 0,397; its 2,7 % is 4,79 %. Nothing downstream turned
   on either, and the figure was quoted in three places.
4. **`CONTEXT.md`'s *Dwelling axis* presumed a dwelling has one.** 4,79 % do not.
   The term is amended and *Frame residual* is added beside it.
5. ⚠️ **The open gap is on the warp, not here.** Everything measured is on the
   donor record. Whether a sheared donor yields a worse *Plan* — as opposed to a
   worse record — is unmeasured, because `experiments/warp/` is held by another
   open ticket and the conversion may not reach into it. If that measurement ever
   contradicts part 3, the rank is where it lands, not the gate.
