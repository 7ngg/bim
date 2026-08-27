# A candidate pool shares a floor area, not a box

ADR 0018 gave the Envelope's notch geometry to the retrieved dwelling, so the
notch position is a real home's rather than an invented constant. That was right
and it stands. But it made the Envelope **per-candidate**, and the ADR that made
it per-candidate also asserts, four paragraphs later, that the Envelope is what
**every candidate for one Brief shares**:

> **The Envelope therefore becomes per-candidate in its `invented` fields only** —
> ADR 0018, *The decision*
>
> Declines … are driven by the Envelope, **which every candidate for one Brief
> shares**. — ADR 0018, consequence 3

Both cannot be true, and nothing on this map had noticed. Everything downstream —
the acceptance bar's hard area gate, `brief.md` §5's sizing rung, ADR 0003's
"entrance edge is fixed before the solve" — was written against the second
reading, while ADR 0018 shipped the first.

## The notch is not a rounding error

Re-measured over the 2,317 converted Swiss dwellings in
`experiments/rectangularise/out/swiss_fit_k2.json` — the share of a converted
dwelling's bounding box taken by its two largest boundary-touching complement
components, which is what the index records as its notches:

| notch share of bbox | p10 | p25 | **p50** | p75 | p90 | p95 |
|---|---:|---:|---:|---:|---:|---:|
| | 0.0313 | 0.0783 | **0.1255** | 0.1794 | 0.2330 | 0.2692 |

**A twenty-point swing between two candidates for the same Brief**, against a
`area.invented_envelope_hard` of ±5 %.

So the two readings are not a wording slip with a wording fix. If the **box** is
what the pool shares and it is sized at the median notch, the floor each candidate
delivers moves with whichever donor was drawn, and **56.15 % of the index fails
the hard area gate on donor geometry alone** — before the warp deviates a single
room, before the solver places a single partition. At the 2 % soft preference,
81.61 % fail.

**And that price has never appeared in a measurement, because the harness removes
it.** `experiments/warp/fit_warp.py:373-384` scales the Brief's room targets onto
the donor's *covered* area rather than its bounding box, with the reason in the
comment:

> Asking the fit for `W*H` would demand 13 % more floor than the arrangement
> holds, which reads as deviation and refusal that belong to the rig.

Correct for what that harness was measuring, and it means ADR 0018's headline —
best-of-8 worst-room deviation p50 **0.056** — is a statement about **proportion**
with absolute area normalised away. The warp has never been measured against a
stated `target_area`. The quantity `area.invented_envelope_hard` binds is the one
the rig divides out.

## The decision

**What a candidate pool holds constant is the Envelope's floor area. The bounding
box is derived per candidate and may differ across the pool.**

`resolve` fixes the invariant, once, per `brief.md` §5 rung 1:

```
interior = target_area × (1 + f)                 f = 0.0575, the p50 partition footprint
```

Each candidate then derives its own box from its own recorded notch share `s`,
holding the Brief's aspect ratio:

```
W × H = interior / (1 − s)                       aspect fixed, scale moves
```

Every candidate delivers `interior` of floor **by construction**, so the pool's
area agreement is 1.0000 rather than 0.4385, and it is not a tolerance that was
widened to get there.

**The bounding box may only flex where `overall_dimension` is `invented`.** Where
a Homeowner stated a dimension, the box is a fact about their home and the floor
absorbs the notch instead — which is already the right rule, because the
applicable gate there is `area.given_envelope_warn` (warn), not
`area.invented_envelope_hard` (hard). One rule, two provenance branches, no new
threshold and no new severity. ADR 0006's per-field provenance is what makes that
compose.

### What this costs and what it does not

`ResolvedBrief.envelope` **loses** `overall_dimension` on the invented path and
carries floor area plus aspect instead; the Proposal **gains** the realised
Envelope. A field crosses a contract boundary. **No new dependency, no new
technology** — the derivation is one division per candidate, and the warp solve
already takes `W, H` as inputs.

`area.invented_envelope_hard` is **not edited**. It binds Σ Space area against
`target_area` exactly as shipped, and this decision is what makes that honest: the
only quantity left that can move Σ Space area is the **partition footprint**,
which is what ADR 0010 rewrote the rule to catch and what `f` only predicts.
`rules.json` sees no change, which is the opposite of what the ticket that raised
this expected.

## Considered and rejected

- **Keep the shared box and re-fit `area.invented_envelope_hard` upward.** The
  threshold is `ENGINE_CHOICE` and *Fit the ENGINE_CHOICE acceptance thresholds to
  the corpora* holds it, so this was available and cheap. Rejected: admitting the
  measured spread needs roughly ±13 %, which is not a product tolerance anyone
  would defend on its own merits — it is a modelling defect laundered into a
  looser gate, and it would then be inherited by every later reader as evidence
  that ±13 % is what a Homeowner should expect.
- **Keep `overall_dimension` dense on the `ResolvedBrief` as the median-notch box
  and let candidates override it.** Nothing upstream moves. Rejected because it
  re-creates the exact defect this ADR closes: a dense field holding a number no
  candidate builds, which is how "one Envelope for all candidates" came to be
  asserted in the first place.
- **Invent the notch position in `resolve` and hold the whole Envelope fixed.**
  Already rejected by ADR 0018 on its own grounds and still rejected on those
  grounds — it is the invented constant this map keeps refusing, and it breaks the
  monotone warp's guarantee by putting the donor's notch in conflict with an
  arbitrary one.
- **Fill the notch: let the target Envelope's outline differ from the donor's and
  assign the leftover cells to whichever Room borders them.** The most interesting
  option here. A one-part Room bordering the notch becomes an L, which ADR 0014
  already permits, and any donor could then serve any shape — the stated-shape
  coverage cliff below would disappear entirely. **Not rejected on merit and not
  taken:** it breaks the cut-line frame that carries ADR 0018's monotone-warp
  theorem (zero confident-wrong over 21,074 asserted relations), so it would have
  to be re-proved, and it is a `proposer.md` change this ticket does not hold.
  Recorded for that file's next holder rather than decided here.

## Consequences

1. **`shape` leaves the `ResolvedBrief`.** §1 makes that object dense, so ADR
   0018 consequence 5's *"absence means unknown"* had no representation. `shape`
   is a **retrieval gate term on the `StatedBrief`**, not a build field: nothing
   downstream of the Proposal reads it, because by then the notch geometry is
   concrete and per-candidate.
2. **The per-candidate notch is not an Assumption, and that is derived rather than
   chosen.** `brief.md` §1 computes the Assumption set as
   `ResolvedBrief \ StatedBrief`. A field absent from `ResolvedBrief` yields no
   Assumption — correctly, because an Assumption is something we filled in on the
   **request** and the notch is a property of the **result**. §6 gains no fourth
   kind. The presentation problem moves to the gallery, where it joins *A request
   and a result in one typeface*.
3. **A stated `shape` gates on notch *area share*, not notch count — and the count
   gate was mis-labelling the entire index, not merely starving rectangles.** A
   *material* notch is one taking ≥ 5 % of the bounding box; on a 90 m² dwelling
   that is ~4 m², a real bite out of the plan, where 2 % is 1,8 m² and *Whether a
   Room may be more than one rectangle* already measured that class as real
   architecture rather than pipe boxings.

   | stated shape | shipped count gate | material-notch gate |
   |---|---:|---:|
   | `rectangular` | 1.12 % | **15.67 %** |
   | `L` | 8.72 % | **52.96 %** |
   | `U`/`T` | 90.16 % | **25.42 %** |

   Raw count says 90 % of real flats are U/T-shaped and 8.7 % are L, which is not
   a description anyone would recognise. The material reading says half are L, a
   quarter U/T and a sixth read as rectangles. The largest gain is the **common**
   case, `L`, at **6×**. Owed by `proposer.md` §2.2.3's holder.
4. **A stated `shape` still costs most of the index, and that is a warning with no
   pre-image.** 84 % of the pool goes the moment a shape is stated. When the pool
   empties, the Brief falls through to **source B** — ADR 0005 exists so neither
   source has to survive alone, and source B conditions on the Brief with no index
   to starve. **Never a refusal**: refusing here would decline a request the engine
   can serve. Per ADR 0015 this is the third case — no validator rule governs
   retrieval coverage, so there is no severity to inherit and the bound says so,
   as ADR 0013's scope gate already does.
5. ⚠️ **ADR 0003 §7 needs re-reading and this ADR may not edit it.** *"The
   entrance edge is fixed before the solve"* currently reads as *one ring for the
   job*; a per-candidate notch changes the ring's edge **count**, so it must be
   re-read as *one ring per candidate, fixed before that candidate's solve*. The
   ring's **rule** is per-Brief — `dwelling_type` fixes the exterior sides and the
   entrance side, notch edges inherit a `condition` by ADR 0003 §6's existing
   default, and the entrance edge is identified **by side, never by ring index**,
   which is what makes it survive a topology change. `docs/adr/0003-…` is in *The
   two-notch cap is now evidenced*'s `writes:`, so this is a handoff to that
   ticket and not an edit from here.
6. **Declines should decorrelate, and nobody has measured it.** ADR 0018
   consequence 3 prices the 6.9 % Brief-level loss on declines being driven by an
   Envelope every candidate shares. Under this ADR they no longer share one, so
   the loss should fall — direction only. Unmeasured, and it needs the harness to
   stop normalising area away first.
7. **ADR 0018's fidelity numbers are proportion, not area, and should be quoted
   that way.** p50 0.056 worst-room deviation is a real result about the warp's
   ability to hit *relative* room targets. It is not evidence that a candidate
   delivers a Homeowner's stated total, and until `fit_warp.py` is re-run against
   an absolute `target_area` nothing on this map is.

---

## Amendment: `interior` is the Envelope, and the ring has to be held

Added by *The sizing rung under-delivers by four per cent, and `f` is not where to
fix it* (ticket 56), which found both gaps live in a shipped measurement rig.

**This ADR writes `box = interior / (1 − s)` and never says which plane
`interior` is on, nor what the solver then tiles.** Two readings are available
from the text — the Envelope's interior, or ADR 0001's solve domain — and they
differ by `t_int/2 × perimeter`, **3,7 % of a 90 m² dwelling**, the same order as
the whole level discrepancy ticket 54 measured.

**It is the Envelope's own area, at the finished inner face, and that was never a
choice.** `CONTEXT.md` defines the Envelope as *the interior clear region* and the
solve domain as *"not the Envelope, and not the interior"*; `f` and `s` are both
measured on the finished-face plane; and a `ResolvedBrief` that meant the solve
domain would be applying `s` — a share of the **Envelope's** bounding box — to the
wrong rectangle. The solve domain is **derived** from the box by ADR 0001, one
`t_int` larger on each axis, and it is a third quantity rather than either of the
first two. `brief.md` §5.3 carries the three-plane table.

**And this ADR's own guarantee has a precondition it does not state — which the
shipping design then violates.** *"Every candidate delivers `interior` of floor by
construction"* holds only if the **realised** notch share equals the recorded `s`
the box was derived from. `proposer.md` §2.2.3 says the opposite in as many
words: the notch *"is the part of the bbox no part covers — so it warps along
with everything else, for free"*. A warp free to move the cut lines bounding the
notch will spend spare cells there, because the notch is the one region of the
frame carrying no target. Measured on `absolute_area.py`, `covered ÷ interior` is
**0.9833** with the notch free and **0.9986** with the share held, so the
guarantee is worth **1,5 % of `interior`** and is not self-evident.

This is not ADR 0003 consequence 7, which fixes the **entrance edge** — by side,
never by ring index — and says nothing about the notch's dimensions. The two
sentences are compatible and neither implies the other. **The constraint is owed
by `proposer.md` §2.2**, whose *"for free"* is what has to move; nothing in this
ADR changes.

**What this costs: nothing.** `f` is unchanged at 0.0575 and is vindicated — with
the plane corrected and the ring held, Σ Space lands **+0,4 %** of the
`target_area` the Brief asked for. The derivation is unchanged, and `rules.json`
sees no change, which is the second time this ADR has ended there.
