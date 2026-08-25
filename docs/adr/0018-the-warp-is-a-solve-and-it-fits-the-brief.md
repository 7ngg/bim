# The warp is a solve, and it fits the Brief

Retrieval-and-warp ships first (ADR 0005). *What the model proposes* fixed its
admissibility gate — exact room multiset, total floor area ±10 %, envelope
aspect ±15 % — and left the mechanism open. The standing assumption was that the
budget is what keeps retrieval's claim true: *a real person lived in this
arrangement*, and past some distortion that sentence is false.

**The budget was guarding the wrong thing, and the thing it left unguarded is the
one a Homeowner reads.**

## What the measurement found

**A warp cannot destroy an arrangement.** A converted dwelling (ADR 0008/0016) is
a rectangular tiling; a tiling is its cut lines; and any strictly increasing
per-axis map on those cut lines preserves the sign of every separation cost. So
every relation the source satisfied, the warp still satisfies — **zero
confident-wrong, zero reversals, severity identically 0, for every dwelling and
every target**. Verified over **21,074 asserted relations across 993 warps** at
τ = 4, affine and fitted, gated and ungated: zero, every configuration.

**What the gate does not bound is per-room area.** It bounds the *total*. Inside
it, a uniform scale misses the Brief's per-room targets by a median **21 %**;
**8.7 %/11.0 %** of admitted candidates breach `dim.max_area`, which is hard, and
**54.9 %/65.9 %** carry a room below 0.70 × what was asked. The median admitted
candidate's worst room is **0.67 ×/0.61 ×** the requested area.

**Nothing downstream fixes it.** The projection's objective is L1 corner distance
to the Proposal; `dim.min_area` is an ergonomic floor, not a target; `dim.max_area`
is a 2.02–8.15 × ceiling. **The Proposal is the only place a Brief's room sizes
can enter the geometry**, and it was not carrying them.

**Neither obvious fix works.** As a fourth *gate* term, holding every room within
±30 % of target takes coverage from 90.3 % to **40.9 %** at 4–6 rooms and 87.2 %
to **30.2 %** at 7–10; within ±10 % it is single digits. As a *ranking* term it is
free and useless — the pool's **best** member still misses its worst room by more
than 30 % for **54.8 %/65.3 %** of Briefs. The pool does not contain a
well-proportioned match, so no ordering finds one and no threshold admits one.

## The decision

**The warp is a CP-SAT solve over the source tiling's cut-line gaps, and its
objective is the Brief's per-room target areas.**

```
minimise   (1000 · n) · worst  +  Σ_r  w_r · dev_r
subject to Σ gx = W,  Σ gy = H,  every gap ≥ 1
           dev_r · target_r ≥ 1000 · |area_r − target_r|
           worst = max_r dev_r
           every part's span ≥ its Room's realisable minimum, both axes
           every part within dim.aspect_ratio_hard
           every two-part Room's shared edge ≥ ADR 0014's join
```

- **Minimax on the *relative* deviation**, weighted sum as tie-break. An absolute
  objective spends every gap on the living room, because 5 % of 30 m² outweighs
  40 % of a WC — and the bar and the Homeowner both read the worst room.
- **`w_r` ranks a stated target above an invented one**, because `brief.md` §6.1
  already says a stated target is sovereign.
- **Both axes at once.** Area is bilinear and CP-SAT takes it directly;
  alternating linearises it but `dim.aspect_ratio_hard` couples the axes, so a
  frozen axis manufactures infeasibility the joint model does not have.
- **Decidable.** 329 OPTIMAL, 1 FEASIBLE, 63 INFEASIBLE, **0 UNKNOWN** at a 3 s
  cap over 393 warps — ADR 0008's property, inherited rather than claimed.

**Retrieval's claim changes with it**: from *this is a real home, stretched* to
**this is a real home's arrangement, sized to your Brief**. The arrangement is
what no generator gets right and only the corpus supplies. The proportions are
what the Brief specifies, and the corpus has no standing to override them.

**And the Envelope's notch geometry comes from the retrieved dwelling.**
`brief.md` §5 fixes the notch *count* and never the positions. The notch is
already in the cut-line frame, so it warps for free and its position is a real
dwelling's rather than an invented constant. The Envelope therefore becomes
**per-candidate in its `invented` fields only**; where `shape` is `stated`, the
source's notch count must match and the gate gains a fourth term.

## Considered and rejected

- **Keep the affine warp and loosen the budget.** Rejected on its own premise:
  the budget cannot buy arrangement fidelity, because arrangement fidelity is
  free, and it cannot buy area fidelity, because it does not measure area per
  room. Loosening it changes nothing that was ever at risk.
- **Per-room area as a fourth gate term.** Measured; costs 49 points of coverage
  at ±30 % and all of it at ±10 %. Retrieval exists to serve the band where the
  corpus is dense; a gate that empties the band deletes the source.
- **Per-room area as a ranking term over an affine warp.** Measured; free and
  ineffective for the majority of Briefs.
- **Let the projection solve fix the areas.** It cannot: no area-target term
  exists in its objective, and adding one makes the solver trade the Proposal's
  arrangement against the Brief's areas — which is C10's *model proposes, solver
  projects* run backwards. The Proposal is the right place.
- **Invent the notch position in `resolve`.** Rejected. It is the invented
  constant this map keeps refusing, one Envelope for all candidates, and it puts
  the retrieved dwelling's own notch in conflict with an arbitrary one — which is
  precisely where the monotone warp's guarantee would break.
- **Fit the areas with a least-squares solver.** Rejected: it needs `scipy`,
  which is not a pinned dependency, and it does not respect the 250 mm grid, the
  ergonomic floor, the aspect cap or ADR 0014's join without a projection step
  that can violate all four. CP-SAT is already pinned and is integral by
  construction. **No new technology is required for this decision.**

## Consequences

1. **The Proposal now carries area intent, and only for retrieval.** Source B has
   per-room target-area conditioning (§2.3) and no such guarantee. The two
   sources reach the same contract by different routes, which is what ADR 0005
   bought.
2. **A warp can refuse, and refusing is correct.** **17.8 %** of candidates are
   declined because the target Envelope cannot host that arrangement at the
   ergonomic floor and inside `dim.aspect_ratio_hard`. Ablated: minima and aspect
   together 22.0 %, minima 16.9 %, aspect 11.9 %, **neither 0.0 %** — so every
   refusal is a real dimensional refusal. The pool absorbs it: **93.1 %** of
   Briefs are served by at least one of 8 candidates.
3. ⚠️ **Declines are correlated within a pool and must not be compounded.** They
   are driven by the Envelope, which every candidate for one Brief shares.
   Independence would predict a 10⁻⁶ Brief-level loss against a measured 6.9 %.
4. **Best-of-8 worst-room deviation: p50 0.056, p90 0.363.** Against the affine
   warp's best-of-whole-pool p50 of 0.325 — a 5.8 × improvement in the median
   Brief's worst room, at **zero** coverage cost and ~72 ms median per candidate.
5. **`shape` absent must not default to rectangular.** Only **1.12 %** of
   converted dwellings emit a notch-free tiling and only **6.5 %** leave under
   2 % of their bounding box unoccupied, so a stated rectangle admits single
   digits of the index. Absence means unknown. Owed by `brief.md`'s holder.
6. **The index owes two new per-record fields**, neither of which the conversion
   emits today: the **cut-line frame** with per-part index spans, and **per-pair
   relation provenance** (`spurious` or not — ADR 0016/0017 measure the invented
   share at 12.62 %). Owed by `experiments/rectangularise/fit_rects.py`'s holder.
7. **Confidence is provenance, not displacement.** §1 named "how far each room had
   to move under the warp"; the theorem above makes that uninformative, since
   severity is 0 at any displacement. Confidence is per pair and the contract's
   per-box alternative is dead for this source.
8. **`select_relations` must abstain on a positive best cost.** Not caused by this
   ADR — ADR 0014 handed it here — but the warp's guarantee is stated in terms of
   the rule holding. Retrieval is immune either way; source B is not. Owed by
   `experiments/solver-toy/solver.py`'s holder.
9. **The conversion's price is a pool-size effect, not a coverage effect.** Joined
   per multiset over the full index, ADR 0016's thinning costs **0.2 and 0.4
   points** of blank rate. `proposer.md` §4.4's warning that the pool shrinks
   most where it was thinnest is retired.
