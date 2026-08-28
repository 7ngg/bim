---
id: 61
title: The notch is two components and a quarter of donors have more
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - docs/adr/0020-one-brief-one-envelope-area-many-envelope-boxes.md
  - docs/spec/proposer.md
  - docs/adr/0028-the-enclosed-void-is-charged-to-a-room-and-bounded.md   # declared on resolution, unclaimed
  - docs/adr/0003-the-envelope-is-an-inner-face-ring-of-typed-edges.md    # declared on resolution, unclaimed
  - CONTEXT.md                                                            # declared on resolution, unclaimed
---

# The notch is two components and a quarter of donors have more

## Question

**ADR 0020's `s` is defined as the two largest boundary-touching complement
components, and 27,5 % of converted donors have three or more.** On those donors
there is floor that touches the Envelope boundary, is covered by no Room, and is
**neither notch nor enclosed void** by the map's own definitions — it falls
through the gap between them.

`notch_share` draws the line deliberately: components that touch the frame border
are the building's shape, components that touch nothing are ADR 0028's void, and
the *two largest* touching ones are `s`. The two-component choice is ADR 0003's
notch cap — *The two-notch cap is now evidenced* settled that an Envelope carries
at most two notches — so `s` is measuring the cap, not the geometry. The
geometry does not always agree.

Measured over 1,484 converted donors (`experiments/warp/constrained_warp.py --census`):

| boundary-touching complement components | share |
|---|---:|
| 0 | 1.9 % |
| 1 | 14.3 % |
| **2** | **56.3 %** |
| 3 | **24.9 %** |
| 4 | 2.5 % |
| 5 | 0.1 % |

**It is already load-bearing on one decision.** *What best-of-pool is worth at
production pool depth* posted ADR 0020's invariant as a solver constraint for the
first time, and the choice of region changed the answer: constraining *all*
uncovered-minus-void holds a strictly larger region than the ADR names, and its
notch drift stalled at 0.04 where constraining the cells `s` is read off tracked
the tolerance down to 0.0003. Anyone else who posts this invariant will hit the
same fork with no guidance in the ADR.

**What has to be decided:**

1. **What that third component is.** Corpus geometry the conversion should have
   absorbed, a genuine third notch the cap refuses, or fit residue of the same
   family as ADR 0028's void. The three have different owners.
2. **Whether `s` should count it.** `s` sizes the Envelope box
   (`box = interior/(1 − s)`), so floor excluded from `s` is floor the box does not
   budget for — it comes out as deviation somewhere. ADR 0020's guarantee is that
   *every candidate delivers `interior` of floor by construction*, and that
   guarantee is stated over a quantity that does not cover the whole complement.
3. **Whether it interacts with the two-notch cap.** If the third component is a
   real notch, the cap and `s` disagree about the same donor, and *The two-notch
   cap is now evidenced* priced the cap without this measurement in front of it.

## Raised by

*What best-of-pool is worth at production pool depth* (2026-08-28), while posting
ADR 0020's amendment in the warp solve for the first time. The census is one flag
on an existing probe.

## Resolution

**The third component is not a third notch, it cannot be one, and `s` should not
count it — because `s` is measured on the wrong rectangle and widening it makes
that worse.** ADR 0020 second amendment; ADR 0028 amendment; `proposer.md`
§2.2.1, §2.2.3, §2.2.8; ADR 0003 note; `CONTEXT.md`.

### Item 1 — what the third component is

**Floor inside the Envelope that no part covers.** `fit_rects.envelope_approx(domain,
max_notches=2)` builds the Envelope as *the bounding box minus at most two
inscribed notch rectangles*, so the Envelope has never had a third notch to have.

| | |
|---|---|
| `notches_used` | **2 on 90.16 %**, 1 on 8.72 %, 0 on 1.12 % — **never more** |
| `notches_needed` — complement components ≥ 0.25 m² | **3 or more on 37.6 %** |
| `envelope_loss` — real notch area left *inside* the ring by the cap | p50 **1.78 %** of domain, p90 **9.92 %**, mean **3.72 %** |

Character, over the 631 donors that carry one — and it is the character of
residue, not of a building outline: p50 **1.25 m²**, p90 4.12, max 9.0;
**89.7 %** perfectly rectangular against 62 % for the first component and 84 %
for the second; **99.7 %** seated at a corner or edge **distinct** from the first
two; 67.4 % at a corner, none spanning opposite sides; 46.4 % one 250 mm cell
thin, and those carry only 21.2 % of the area. 1,252 m² across the index,
0.54 m² per donor mean.

So it is ADR 0028's object, separated from it only by a test — *enclosed by
parts* — that fails at the frame border.

### Item 3 — the cap, taken first because it closes

**No interaction, and the cap does not move.** At ADR 0020 consequence 3's own
materiality bar (≥ 5 % of bbox) **0.30 %** of donors carry three or more
components. The cap and the geometry cannot disagree about a donor because the
cap already decided, upstream, at conversion: `notches_used` is 2 and the rest is
inside the ring by construction.

⚠️ **What the cap's own evidence never priced is now a note on ADR 0003.** 47
priced it as index thinning (6.65 %) and as a refused shape-family widening
(4.17 % ceiling). Neither is the price a Room pays: `envelope_approx`'s docstring
says under-cutting *"costs a room nothing"*, which is true of the conversion —
scored against the real dwelling — and false of the engine, which must tile the
ring exactly and hands that floor to whichever Room the objective finds cheapest.
Mean **3.72 %** of the domain. Note only; the cap's reasoning is untouched.

### Item 2 — the decision, and it is not the one the ticket proposed

**`s` is the `notches_used` spans' share of the box, and nothing else.** Not the
two largest parts-complement components (shipped), and not all of them (the
ticket's implied fix).

`s` is read off the **parts** complement, so it is the notch plus whatever
`envelope_loss` and fit residue adjoin it. Against the Envelope's own share
`1 − bbox_fill × (1 + envelope_loss)`, on the **88.8 %** of donors whose parts
frame and dwelling bbox are the same rectangle (p50 gap **0.0000**; elsewhere the
parts frame is *smaller*):

| | p50 | p90 | mean | > 2 points |
|---|---:|---:|---:|---:|
| `s` (shipped) | 0.1291 | — | 0.1373 | — |
| `s_env` (the Envelope's) | 0.1100 | — | 0.1182 | — |
| **`s` − `s_env`** | **+0.0153** | +0.0427 | **+0.0191** | **38.2 %** |
| `s_all` − `s_env` | +0.0201 | +0.0489 | +0.0237 | 50.1 % |

**Widening `s` moves it further from the object it names.** That answers item 2
in the negative and is why "count the third component" is refused: it buys mean
**0.51 %** of floor (p90 1.97 %, max 7.31 %) by making the notch a number that
describes no geometry.

**What the shipped error costs is the drawn ring, not the floor.** The box is
`interior/(1 − s)`, so the Envelope inside it is `interior × (1 − s_env)/(1 − s)`
= **+2.2 % mean** — the emitted notch is about **1.9 points of the box larger
than any real dwelling's**, ~**1.9 m²** on a 90 m² dwelling. ADR 0003 makes a
notch a **typed ring edge**: drawn, dimensioned, named to a Homeowner as *a
garden in one case and a neighbour in the other*, exported as an IFC entity.
Inventing 1.9 m² of it defeats the reason ADR 0018 went to the corpus for notch
geometry in the first place.

### Where the floor goes — ADR 0028 widens

**A void is floor inside the Envelope that no Room covers**: every complement
component other than the notch spans. Enclosure is dropped as the test. Nothing
else in ADR 0028 changes — charged to the donor's own receiving Room, weighted
against growth, carried as `voids: [(span, receiving_room)]`, no donor refused.
Population **15.49 % → ~40 %** of donors, p50 still one component, cost still one
`AddMultiplicationEquality` each — the arm 57 priced at **zero** (INFEASIBLE
unchanged, 0 lost, void p90 0.375 → 0.250).

⚠️ **The two changes ship together or neither ships.** The over-sized `s` has
been silently paying for the uncovered floor: `covered ÷ interior` mean
**0.9942**, and 56 measured Σ Space at **+0,4 %** of `target_area`. Re-basing `s`
alone removes the compensation without the cause and takes Σ Space to about
**−1,9 %** — inside `area.invented_envelope_hard`'s ±5 %, and spending a third of
it on a correction meant to be exact. Total uncovered floor inside the Envelope
is p50 **2.47 %** of it, mean **2.93 %**.

### Technology and refactor: none

`env_at` already computes the notch rectangles and discards them, and §2.2's
index-record table has promised *"each notch's index span"* since it was written.
This is that **already-specified, never-emitted field** — the **sixth** on the
pass the conversion is already frozen for, beside the cut-line frame, per-pair
relation provenance, `frontage_reach`, the void components with their donor
owner, and `frame_residual`. The void's new definition is the *same* computation:
record the spans, and the void is the rest. No new dependency, no new variable
class, no re-fit.

Interim: `s_env = 1 − bbox_fill × (1 + envelope_loss)` reproduces it from fields
every record already carries. Enough to measure with, not enough to ship on — the
warp constrains a span snapped to the cut-line frame, not a scalar.

### What the market does

**Graph2Plan conditions retrieval on the boundary raster itself**, so it forms no
notch-share scalar and has no object to lose. `s` exists here only because ADR
0020 derives a *box* per candidate instead of carrying a boundary — a prior for
tying `s` to geometry we can point at. And the reason no vendor reports this:
`floorplan-generation-stack.md` finds **zero of ~20 published generators emit
walls with thickness**; `competitive-landscape.md` finds eleven products that all
stop at schematic design. **A plan that stops at schematic has no obligation to
tile**, so nobody else has to say whether an uncovered pocket is outside the
building or inside it.

### Corrections and handoffs

- ⚠️ **`proposer.md` §2.2.3's *"the boundary-touching complement is the building
  and is held at `s`"* was false** and is struck. Both halves failed: past the
  second component it is not the building, and the first two are contaminated.
- ⚠️ **ADR 0020 consequence 3's material-notch table owes a partial re-measure.**
  `L` **52.96 %** and `U`/`T` **25.42 %** reproduce on the parts complement within
  0.5 points; `rectangular` **15.67 %** does not (21.6 %), and the 5.95 % it
  leaves at three-or-more material components **cannot exist** against an Envelope
  with at most two. Headline safe, two end rows on the contaminated object.
  Re-measure when the spans land; **not restated meanwhile**.
- ✅ **57's fork is collapsed.** *Constrain the cells `s` is read off* versus
  *constrain all uncovered-minus-void* is no longer a choice — with `s` on the
  notch spans, the spans are the region. Its tolerance table (2,6 % at ±0.02,
  8,8 % exact) was measured against a different region and is now a guide to the
  **shape** of the cost, not the cost.
- ⚠️ **ADR 0028 §4's ownership purity (p50 1.00, ≥ 0.80 on 72.7 %) is measured on
  the enclosed population only.** The widened population is corner- and
  edge-seated and borders fewer Rooms, so the fallback should fire *less* — a
  direction, not a measurement. Check it on the emitting pass.
- ⚠️ **My own round-1 caveat was wrong and is withdrawn**: I reported a
  parts-frame/dwelling-bbox gap of p50 2.26 % / p90 10.1 %, having inflated the
  bbox by `(1 + envelope_loss)`. Corrected, the frames are **identical on 88.8 %**
  (p50 gap 0.0000) and the parts frame is smaller elsewhere. No reconciliation
  is owed and no field beyond the spans.

### Declared on resolution

`docs/adr/0028-…` and `docs/adr/0003-…`, both unclaimed at the time, and
`CONTEXT.md`, also unclaimed. `docs/adr/0020-…` and `docs/spec/proposer.md` are
this ticket's own `writes:`. `experiments/warp/` is **not** touched — it is held
by 62, 63 and 64, and every measurement here was run read-only from a scratch
probe over `experiments/rectangularise/out/swiss_fit_k2.json`.
