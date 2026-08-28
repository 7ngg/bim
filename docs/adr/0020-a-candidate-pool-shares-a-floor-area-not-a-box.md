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

---

## Second amendment: `s` is the **Envelope's** notch share, and it never was

Added by *The notch is two components and a quarter of donors have more*
(ticket 61), which set out to decide whether a third boundary-touching
complement component belongs in `s` and found that the question is the smaller
of two, and that answering it the obvious way makes the larger one worse.

### The third component is not a third notch, and cannot be

`fit_rects.envelope_approx(domain, max_notches=2)` builds the Envelope as **the
bounding box minus at most two inscribed notch rectangles**. Measured over the
2,317 converted donors:

| | |
|---|---|
| `notches_used` | **2 on 90.16 %**, 1 on 8.72 %, 0 on 1.12 % — and **never more** |
| `notches_needed` (complement components ≥ 0.25 m²) | **3 or more on 37.6 %** |
| `envelope_loss` — real notch area left *inside* the Envelope by the cap | p50 **1.78 %** of the domain, p90 **9.92 %**, mean **3.72 %** |

So a donor's third boundary-touching complement component is **floor inside the
Envelope that no part covers**. It is not the building's shape: the building's
shape is the ≤ 2 notch rectangles, and everything the cap refuses to model is
deliberately inside the ring. Its character says the same thing — p50 **1.25 m²**,
p90 4.12, **89.7 % perfectly rectangular** against 62 % for the first component,
**99.7 %** seated at a corner or edge distinct from the first two, and 46.4 % one
250 mm cell thin. It is the same object ADR 0028 already names, distinguished
from it only by a test — *enclosed by parts* — that fails at the frame border.

**The two-notch cap is not challenged and does not move.** At this ADR's own
materiality bar (consequence 3, at least 5 % of the bounding box) **0.30 %** of
donors carry three or more components. ADR 0003's cap is evidenced at a measured
ceiling and *The two-notch cap is now evidenced* stands unamended.

### The larger error: `s` is measured on the wrong rectangle

`s` is read off the **parts** complement, so it is the notch **plus** whatever
`envelope_loss` and fit residue happen to adjoin it. The Envelope's own share is
`1 - bbox_fill x (1 + envelope_loss)`, already derivable from every fit record.
On the **88.8 %** of donors whose parts frame and dwelling bounding box are the
same rectangle (p50 gap 0.0000; elsewhere the parts frame is *smaller*):

| | p50 | p90 | mean | > 2 points |
|---|---:|---:|---:|---:|
| `s` (shipped) | 0.1291 | — | 0.1373 | — |
| `s_env` (the Envelope's) | 0.1100 | — | 0.1182 | — |
| **`s` − `s_env`** | **+0.0153** | +0.0427 | **+0.0191** | **38.2 %** |
| `s_all` − `s_env` | +0.0201 | +0.0489 | +0.0237 | 50.1 % |

**Widening `s` to cover every touching component moves it further from the
object it names, not nearer.** That is the ticket's own question answered in the
negative, and it is why the answer is not "count the third component".

**What the error costs is not floor — it is the drawn ring.** The shipped box is
`interior/(1 − s)`, so the Envelope inside it is `interior × (1 − s_env)/(1 − s)`
= **+2.2 % mean**. The emitted Envelope's notch is therefore about **1.9 points
of the bounding box larger than any real dwelling's** — on a 90 m² dwelling,
roughly **1.9 m² of notch no donor had**. A notch is not bookkeeping: ADR 0003
makes it a **typed ring edge**, drawn, dimensioned, named to a Homeowner as *a
garden in one case and a neighbour in the other*, and exported as an IFC entity.
Inventing 1.9 m² of it is a fidelity defect in the one part of the Envelope this
map went to the corpus to avoid inventing.

### The decision

**`s` is the share of the candidate's bounding box taken by the Envelope's own
notch rectangles — `notches_used` of them, at most two — and nothing else.**

`box = interior / (1 − s)` is unchanged in form. `interior` is unchanged, on the
plane the first amendment fixed. What changes is which cells `s` counts, and the
box shrinks by p50 **1.7 %**, mean **2.2 %**.

**The two changes ship together or neither ships.** Under the shipped `s` the
over-sized box has been silently paying for the uncovered floor inside the ring:
`covered ÷ interior` is mean **0.9942**, and ticket 56 measured Σ Space at
**+0,4 %** of `target_area` with the ring held. Re-basing `s` alone removes the
compensation without removing the cause and takes Σ Space to about **−1,9 %** —
inside `area.invented_envelope_hard`'s ±5 % but spending a third of it on a
correction that was supposed to be exact. The cause is uncovered floor inside
the Envelope, **p50 2.47 % of it, mean 2.93 %**, and ADR 0028's amendment is
what removes it. Sequencing this wrong is the one way to make the plan worse.

**The guarantee is restated and is now true of the object it names.** *Every
candidate delivers `interior` of **Envelope** by construction* — exactly, since
`box × (1 − s) = interior` with `s` the Envelope's own share. Σ Space reaches
`interior` because the solve tiles the Envelope exactly (`model.no_unassigned_area`,
hard), and the floor it hands out is accounted for rather than absorbed at
random once ADR 0028 charges it.

### What it costs, and whether anything is owed

**No new technology, no new dependency, no refactor.** `env_at` already computes
the notch rectangles and discards them; §2.2's index-record table already
promises *"`notches_used`, and each notch's index span"* and `fit_rects.py` has
never emitted the spans. This is that **already-specified field**, taken on the
pass the conversion is already frozen for — the sixth alongside the cut-line
frame, per-pair relation provenance, `frontage_reach`, the void components with
their donor owner, and `frame_residual`. One statistic off the same records.

Until that pass runs, `s_env = 1 − bbox_fill × (1 + envelope_loss)` reproduces it
from fields every record already carries, on the 88.8 % where the frames agree.
That is enough to measure with and not enough to ship on, because a notch span
snapped to the cut-line frame is what the warp constrains and a scalar is not.

### Considered and rejected

- **Widen `s` to every boundary-touching component (`s_all`).** The ticket's own
  proposal, and the arithmetically exact one for the guarantee as previously
  worded: `covered ÷ interior` goes to ~0.999. Rejected because it is exact
  about the wrong object — it budgets the box for floor the ring **encloses**,
  moves `s` a further 0.5 points from the Envelope's share, and would have the
  emitted ring's notch bigger still. It buys a mean **0.51 %** of floor
  (p90 1.97 %, max 7.31 %) at the cost of making the notch a number that
  describes no geometry at all.
- **Keep `s` as shipped and charge only the third component.** Cheapest, and it
  closes the gap the ticket named. Rejected: it leaves `s` 1.9 points above the
  Envelope's share on 38.2 % of donors and leaves the invented notch in the
  drawing, which is the part a Homeowner sees.
- **Raise the notch cap so a third component can be a third notch.** Refused by
  ADR 0003's second amendment on a measured ceiling — a vertex budget rescues
  **4.17 %** of the corpus, 46.3 % of which still fails at four notches, and
  half the tail is chamfered or curved, which no rectilinear budget reaches.
  Nothing here reopens it.

### What the market does

Retrieval-conditioned generators do not form this scalar at all. **Graph2Plan
conditions on the boundary raster itself**, so there is no notch share to get
wrong and no compression to lose the object in; `s` exists here only because
ADR 0020 derives a *box* per candidate rather than carrying a boundary. That is
a prior for keeping `s` tied to a geometric object we can point at — the notch
rectangles — rather than to a residual computed from whatever the fit missed.
And the reason nobody else reports this defect is the one ADR 0028 already
recorded: `floorplan-generation-stack.md` finds **zero of ~20 published
generators emit walls with thickness**, and `competitive-landscape.md` finds
eleven products that all stop at schematic design. **A plan that stops at
schematic has no obligation to tile**, so no vendor ever has to say whether an
uncovered pocket is outside the building or inside it.

### Consequences

1. **Consequence 3's material-notch table owes a re-measure, and only in part.**
   Its `L` (52.96 %) and `U`/`T` (25.42 %) rows reproduce on the parts complement
   within 0.5 points and its `rectangular` row does not (15.67 % against 21.6 %),
   and the 5.95 % it leaves at three-or-more material components cannot exist
   against an Envelope that has at most two. The **headline is safe** — `L` is
   the common case and the material reading is the 6x gain — and the two end rows
   are on the contaminated object. Re-measure once the notch spans are published;
   do not restate the table meanwhile.
2. **The fork *What best-of-pool is worth at production pool depth* hit is
   collapsed.** It found that constraining *all* uncovered-minus-void holds a
   strictly larger region than this ADR names, with notch drift stalling at 0.04,
   where constraining the cells `s` is read off tracked the tolerance. With `s`
   defined on the notch spans, the region to constrain is **the notch spans**,
   and there is no longer a choice to get wrong. The tolerance table — 2,6 % of
   candidates at ±0.02, 8,8 % held exactly — is measured against a different
   region and is a **guide to the shape of the cost, not the cost**.
3. **`rules.json` sees no change.** Third time.
