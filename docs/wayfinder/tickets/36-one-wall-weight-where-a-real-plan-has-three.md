---
id: 36
title: One wall weight where a real plan draws three
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - docs/adr/ (new ADR)
  - the consequences route to the owners of annotation.md, acceptance-bar.md
    and the Homeowner surface — see "What this ticket does NOT write"
---

# One wall weight where a real plan draws three

## Question

Surfaced by *One internal thickness, against a corpus that has no module at all*,
which was sent to ask whether one `t_int` is defensible. **It is** — the shipped
150 mm lands **4 mm** from the corpus-optimal single value of 146, area drift
straddles zero, and the single-`t_int` conclusion survives. So this is not that
question. It is the one that measurement left behind:

> **A uniform internal thickness draws two wall weights. 76.1% of real dwellings
> draw three** — envelope, internal bearing wall, partition.

The failure mode is **not** the one the map has been guarding against. A plan with
one partition weight does not read as *generated*. It reads as **drawn by someone
who does not distinguish a partition from a bearing wall** — which is worse,
because it is a competence signal rather than a novelty signal, it is invisible to
the Homeowner it is sold to, and it is the first thing the Practitioner in C2 sees.

Measured, `docs/research/single-internal-thickness.md` §2:

| | |
|---|---|
| dwellings with ≥2 internal thickness classes (±10 mm) | **93.0%** |
| dwellings showing three weights — envelope / bearing / partition | **76.1%** |
| dwellings with a *single* internal thickness | **7.0%** |
| heaviest ÷ lightest internal class, median | **2.00×** |
| dwellings whose internal spread ≥ 50 mm — 1 mm of paper at 1:50 | **77.0%** |
| dwellings holding ≥1 m of internal wall ≥ 200 mm | 35.6% |

`out/compare.png` draws it three ways — as surveyed, uniform at the dwelling's
*own* median, uniform at 150 — which separates **uniformity** from **thickness**.
Look at it before deciding: the thickness is fine and the uniformity is the loss.

## Decide

The research priced three shapes. Pick one, or refuse all three and say what the
product says instead.

**A — Accept it.** One weight, and the product copy says the engine does not
distinguish load-bearing from partition, alongside the C5 and C8 statements it
already makes. Costs nothing to build. The honest version of this is not silence:
`Wall.load_bearing` is already *unknown, not false*, and this would make that
admission visible on the drawing rather than only in the model.

**B — Solve thick, draw thin.** Dilate the solve domain by `t_max/2` uniformly so
every tiling edge is still a centreline and the tiling still closes, then draw
selected partitions at 150 against a bearing wall at 280. ADR 0001's uniformity
survives exactly where it is load-bearing — the solve — and the drawing gets two
internal weights. Priced, and not free:

- **19 of 36 ergonomic room-axes need one more 250 mm solve cell** at 280 than at
  150 (253 → 272 cells; +132 mm per room-axis). ADR 0009 already found 250 mm
  charging the **5-room case**, the bottom of C13's band and the corpus's
  commonest size. This makes that worse in exactly that band. **Whether it makes
  it fatal is unmeasured** and needs a solver run.
- **A second bill, in area.** The delivered Σ Space area would exceed what the
  solve computed, by the thickness difference over every internal wall. So
  `area.invented_envelope_hard` stops reading the number the solve produced. That
  is a **hard rule to re-derive**, not a tolerance to widen.

**C — Two `t_int` in one Plan.** What actually buys the fidelity: measured,
**per-plan selection captures 1% of the available gain; 99% lives inside a single
dwelling.** It breaks **ADR 0001 consequence 5** and the **hard** validator rule
`model.space_matches_erosion`, and — this is the part the map had wrong — **ADR
0009 does not make it cheaper.** ADR 0009 cheapens the *per-Plan* purchase, whose
cost for `AZ` was already zero rows. Shape C's cost is a hard geometric invariant,
untouched.

## What is already settled and must not be re-litigated

- **The single `t_int` is not in question, and 150 is not in question.** Both were
  measured and both hold. This ticket is about how many weights are *drawn*, which
  is a separate axis from how many are *solved*.
- **`t_int_bearing` = 250 is `verified` and sitting unused** in the profile. It is
  the second weight shape B or C would draw. It exists already; nothing needs
  sourcing.
- **The old justification is dead.** *"A second `t_int` needs N copies of every
  dimensional minimum"* is false by count — `profiles.AZ` publishes **zero** linear
  minima. Do not reach for it; the argument that survives is ADR 0001, not ADR 0007.

## What this ticket does NOT write

It writes an ADR and nothing else. Whichever shape wins routes its consequences to
the tickets that own the files: **A** to the Homeowner surface and the product
copy; **B** and **C** to *The annotation spec is US-shaped* for the poché weights
and to whoever holds `acceptance-bar.md` for the re-derived area rule. Do not edit
those files from here — that is the collision the map's `writes:` rule exists to
stop, and it has already happened twice.

Deliverable: the shape, an ADR recording why the other two lost, and a named
hand-off per consequence.

## Resolution (2026-08-28)

**All three shapes are refused as posed. The Plan draws two internal wall weights,
and it draws them because the third is a structural claim the engine cannot make** —
ADR [0026](../../adr/0026-two-wall-weights-because-the-third-is-a-structural-claim.md).
Shape A's geometry ships; A's *delivery* does not. The admission goes on the
**sheet**, not into product copy, and two shipped general notes that make the sheet
misleading are corrected with it.

`Wall.load_bearing` stays `None` for the life of v1, `Pset_WallCommon.LoadBearing`
stays omitted, and `t_int_bearing` = 250 stays `verified` and unconsumed where
`room-constraints.json` already calls it *"the deferred structural patch"*.

### 1. The 76.1 % is measured on the wrong artifact class

Swiss Dwellings is a corpus of **surveyed built dwellings** — buildings that exist,
whose walls were measured *after* a structural engineer decided which ones carry
load. Three weights is a **working-drawing** property, produced by an engineering
step this engine does not contain. The engine emits a concept-stage design with no
loads, no spans and no structural scheme, and an architect's concept plan for a
new-build dwelling has two weights for the same reason ours does.

The counter-case is renovation, where bearing walls are *given* — existing fabric
the designer inherits. Real, and not v1's: C5 ships a single dwelling whose Envelope
is stated or invented, with no existing fabric to inherit from. That case is this
decision's reversal trigger, written on the ADR.

### 2. Nothing in the pipeline could draw it, and that is three facts, not one gap

B and C both need a per-wall heavy/light flag. None exists, and each of the three
reasons is independent:

| | |
|---|---|
| ADR 0003 c3 | *"`load_bearing` stays `None`; v1 still makes no structural claim"* |
| `fit_rects.py:125` | the conversion rasterises at 250 mm and assigns each wall cell to the nearest room, *"which cuts each wall at its centreline"* — **thickness is destroyed at conversion**, so a donor hands over none |
| `proposer.md` §2.3 | two box slots and a presence token. No thickness token, exactly as there is no window token (ADR 0025) |

**The donor-inherited version was weighed and it is the strongest argument on the
other side.** `thickness-fidelity/classify_check.py` already classifies per-wall
thickness on the raw Swiss geometry, `fit_rects.py` reads the same source and is
already owed three per-record fields, and a fourth would be one pass — that is
*inheriting* structure, not inventing it. It still loses twice over: the warp
stretches a donor by a per-room area budget and the solve selects which separations
it posts, so a heavy flag surviving that is provenance wearing structure's clothes;
and it covers **source A only**, so the sheet's wall hierarchy would depend on which
proposer won — non-deterministic across two candidates for one Brief, and a worse
tell than uniformity.

### 3. Shape B is strictly dominated, and the ticket had it the other way round

The ticket credits B with preserving ADR 0001 c5 *"exactly where it is
load-bearing — the solve"*. True, and worth nothing: **no hard rule binds the solve
alone.** Both bind the model, after it.

Solve at 280, draw a partition at 150, and the body straddles ±75 of a centreline
whose Space boundary sits at 140. The 65 mm strip each side belongs to nothing, and
`model.no_unassigned_area` is **hard**, site `both` — *"the union of all Space
polygons and all Wall bodies equals the Envelope interior exactly."* Priced off
§3.3's own table, reserved footprint **10.6 %** of Σ Space at 280 against **5.7 %**
drawn at 150:

| | |
|---|---|
| Σ Space left unassigned, upper bound (every internal wall drawn thin) | **4.9 points** |
| at the corpus's own bearing share (88.6 % of internal length is < 200 mm) | **≈4.3 points** |
| `area.invented_envelope_hard`, for scale | 5 % |

A whole hard area gate of void floor. Absorb it by redefining the Space as *bounded
by real wall inner faces* and `model.space_matches_erosion` dies instead — the rule
whose own note says *"it fails the day internal wall thickness stops being uniform,
which is the point of keeping it."*

**So B breaks one of the two hard rules or the other, exactly as C does** — and
additionally charges 19 of 36 ergonomic room-axes an extra 250 mm solve cell, in the
five-room band ADR 0009 already found the grid charging. C costs one hard rule, no
cells, and buys 10.3 of the 12.8 available fidelity points on values already in the
profile. **B is recorded as refuted, not merely unchosen**; a future case for a
second weight is built on C.

### 4. The market does not infer structural function either

ArchiCAD's wall carries *Structural Function: Load-Bearing / Non-Load-Bearing /
**Undefined***, and Undefined is the default. Revit's `Structural` flag defaults off
and a human sets it. IFC has no third state — `Pset_WallCommon.LoadBearing` is an
`IfcBoolean` — and the idiom for unknown is to **omit the property**, which ADR 0011
already chose. On the generative side there is nothing to catch up to:
`floorplan-generation-stack.md` found **zero of ~20 published generators emit walls
with thickness at all**. Inferring a bearing split would be the one structurally
novel move on this map, made in the one place where being wrong reads as a safety
instruction. ADR 0010's *"we are not inventing a convention; we are catching up to
the one the market shipped"* applies here unchanged — the shipped convention is
`Undefined`.

### 5. The sheet is currently worse than silent, and that is why A's delivery is refused

`annotation.md` already made this argument, for C8, and it is quoted rather than
re-derived: *"Note 8 is C8, and it belongs on the drawing, not only in the product
copy. A DXF outlives the session that produced it, gets emailed, and arrives
somewhere the product copy never reaches."* A structural non-claim travels further,
because the reader who acts on it is a builder holding a printed sheet.

Two shipped general notes are individually true and jointly misleading:

- **Note 3** — *"All partitions `t_int` mm unless noted."* **Nothing is ever noted.**
  The phrase promises an exception mechanism the engine does not have.
- **Note 7** — *"Fire, thermal, acoustic and structural performance are not
  specified."* Performance is a calculation; **identification is not performance.**
  A reader takes it as *no structural calculations were run* and still assumes the
  wall drawn heavy is the heavy one.

Neither says the true thing: *every internal wall is drawn as a partition, and
load-bearing walls have not been identified.*

### What this cost, stated plainly

**Nothing in the acceptance bar, and no new technology.** No predicate added, none
deleted, rule count and conformance subset untouched; `model.space_matches_erosion`,
`model.no_unassigned_area` and ADR 0001 c5 all stand, which is the point. The build
cost is one general note, one struck phrase, one Drawing-check predicate and two
glossary terms — and that is what is *left after* the reason, not the reason.

**The fidelity gap is reclassified, not closed.** 76.1 % of real dwellings still
carry a hierarchy this sheet does not. The claim is that the hierarchy is not v1's
to draw, **not** that its absence is free.

### Hand-offs

**`docs/spec/annotation.md`** *(no claimant)* — (a) a new general note, drafted on
the ADR; **`arakəsmə` is `verified`**, AzDTN's own word at `az-finish-layer.md`
cl. 8.24 and already used in §8, while **`yükdaşıyan` is unsourced and must not ship
as written** — source it from `azdtn_2_17_1`, which `thickness.md` read first-hand
for `t_int_bearing` cl. 6.9 and which necessarily names the thing it sets a
thickness for. (b) **Strike *"unless noted"* from note 3.** (c) Add
`draw.structural_disclaimer_present`, Drawing check **12 → 13**, on the precedent of
`draw.schedule_totals_close`.

**`CONTEXT.md`** — declared on resolution and **written**, not handed on; it had no
claimant. New term **Wall weight**; **Wall** gains an `_Avoid_` on inferring
`load_bearing` from thickness, length or position.

**`docs/research/single-internal-thickness.md`** *(no claimant)* — one correction
when someone next holds it: §4.4 prices B in solve cells and in area drift and never
in hard-rule breakage, which is the price that decides it.

**Homeowner surface and product copy** — **nothing, deliberately.** That is shape
A's delivery mechanism and it is refused. `homeowner-surface.md` is claimed by *A
request and a result in one typeface*; this adds nothing to its queue.
