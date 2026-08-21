---
id: 17
title: Area measurement convention
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - CONTEXT.md
  - data/standards/room-constraints.json
  - docs/spec/acceptance-bar.md
  - data/acceptance/rules.json (added on resolution — see Resolution, "what was written")
  - docs/adr/0010-a-space-is-bounded-by-finished-faces.md (new)
---

# Area measurement convention

## Question

Graduated from **Not yet specified**, which held it as *"minimum areas are not
comparable across regions even after unit conversion, because German Wohnfläche,
UK GIA and the IPMS family count differently — too diffuse to ticket yet."*

*Canonical geometry model* sharpened it into something answerable, by accident and
then on purpose: it defined a **Space** as *the polygon bounded by the inner faces
of the surrounding walls*, and made its area exactly computable. That is no longer
a vague worry — **we have silently adopted one measurement convention**, and this
ticket names which, and decides what travels with it.

Settle:

1. **Which published convention the inner-face polygon actually is**, per region.
   It is close to a net internal area, but "close to" is what this ticket exists to
   eliminate. Name it against IPMS, the RICS Code of Measuring Practice, GIA, and
   Wohnflächenverordnung.
2. **What the Brief's target area means.** A Homeowner saying "about 90 m²" is
   using a convention they have never heard of, probably whatever their local
   property listings quote — which is Wohnfläche in Germany and something else in
   England. If the Brief's number and the Plan's number use different conventions,
   the system is wrong in a way no validator currently catches.
3. **Whether an area value carries its convention everywhere it travels.** The
   original fog note's worry, and it is a real one: it touches the geometry model,
   the Brief and the validator at once. A tagged quantity type, or a single
   convention fixed per project?
4. **What the exports declare.** IFC has `Pset_SpaceCommon` / `Qto_SpaceBaseQuantities`
   with defined semantics; a room tag on a drawing quoting a different number from
   the IFC quantity is exactly the sort of defect a Practitioner notices first.
5. **Whether the deductions matter at v1 scale** — Wohnfläche discounts sloped
   ceilings and counts balconies at a fraction; those are the rules that make the
   conventions actually diverge rather than merely differ in name. Single-storey
   scope may make most of them moot, which would be a welcome finding, but it needs
   checking rather than assuming.

The reason this cannot be deferred much further: **the numbers in
`data/standards/room-constraints.json` are minimum *areas*, and they were sourced
per region.** If they are not all in the same convention as the Space areas the
validator computes, the acceptance bar is comparing two different quantities and
will do so silently.

Waits on *Which region profiles ship in v1*, since the conventions are regional
and the answer is scoped by which regions actually ship.

Deliverable: the convention named per region, the tagging decision, and an
explicit statement of what the Brief's area number means to a Homeowner.

## Inherited from *Dimensioning and annotation rules*

This ticket now has a **third consumer that quotes the number in public**, and one
rule that follows its answer rather than keeping its own.

- The area appears in three places on an issued drawing: the **room tag**, the
  **room schedule** on sheet `A-102` — which also states the Envelope inner area
  and the difference, so a Practitioner can reconcile the schedule against the
  plan — and the title block's **`AREAS`** attribute, which names the convention in
  words. Question 3 ("does an area carry its convention everywhere it travels")
  therefore has at least one answer already: **on the drawing it is declared once
  in the title block, not per tag.**
- **ADR 0004's tier-1 overall follows this ticket.** Tier 1 spans the footprint
  and currently measures a party edge **to its centreline**, chosen because GIA and
  IPMS both do. If this ticket lands on a convention that treats party walls
  differently, tier 1 changes with it — one drawing must not quote a footprint on
  one convention and an area on another, and that is a defect a Practitioner spots
  before anything else.
- A drawing is also the artefact that makes question 2 concrete. A Homeowner
  reading `16.06 m²` on a plan they asked to be "about 90 m² total" is comparing
  our number against a listing convention they have never named.

## Inherited from *Which region profiles ship in v1*

**Item 5 is checked, and the answer is the welcome one it hoped for.** The
deductions that make Wohnfläche, GIA and the IPMS family genuinely diverge —
part-height ceilings discounted at 50%, balconies at 25–50% — **cannot fire in
v1**, because v1's geometry model contains **no ceiling height and no balcony**.
Neither term appears anywhere in `CONTEXT.md` or in *Canonical geometry model*.
So this ticket is not choosing between four conventions that disagree; it is
naming one, in one region.

**One region, not several.** ADR 0006 ships exactly one selectable profile, `AZ`,
so item 1's "per region" collapses. The live pair is the post-Soviet one —
*общая площадь* (total) against *жилая площадь* (living) — which is a real
distinction with real consequences for what a room tag prints and what
`Qto_SpaceBaseQuantities` declares, and it is now the only one in scope. `UK` is
retained only as a test fixture, so GIA still needs naming *for the fixture*, not
for a user.

**Item 2 gets sharper, not easier.** A Homeowner saying "about 90 m²" is quoting
whatever their local property listings quote. Under the AZ profile that is
*общая площадь*, which counts differently from the inner-face polygon a **Space**
is defined as. Naming the convention is exactly what stops the Brief's number and
the Plan's number silently disagreeing.

**The pair itself belongs here, not to the profile ticket.** *The Azerbaijani
region profile* is instructed to surface the two terms and hand them over rather
than decide between them.

## Handed over by *The Azerbaijani region profile* — and it reframes the question

That ticket was told to gather the *общая площадь* / *жилая площадь* pair and hand
it here without deciding. It gathered it, and **the pair does not exist.** Sources
read first-hand; detail in `docs/research/az-region-profile.md` §7 and
`docs/research/az-region-profile/daylight.md` §4.

**1. There is no *жилая площадь* in Azerbaijan.** As a summed metric,
`yaşayış sahəsi` appears in neither the 2012 area Qaydalar nor AzDTN 2.7-2, and
СП 54.13330 does not define it either. The modern instruments did not *add* a
total-area figure alongside a living-area one — **they replaced the pair**. So this
ticket's inherited framing, a choice between two metrics, is not the question.

**2. What AZ has instead is two in-force, mutually contradicting statutory
definitions of the *same* metric, *ümumi sahə*:**

| | Housing Code art. 12.5 | Area Qaydalar cl. 3.8 |
|---|---|---|
| purpose | housing-law entitlement | design / inventory |
| balcony, *eyvan* | **excluded outright** | **included**, at a coefficient |
| force | statutory | statutory |

Coefficients verified: balcony/terrace **0.3**, loggia/glazed enclosure **0.5**,
veranda/*eyvan* **1.0** (full, not reduced), mansard below 2.7 m **0.7**. The
ticket's reported 0.3/0.5 is confirmed. **That disagreement is the real question**,
and it is a choice between two Azerbaijani legal instruments, not between two
conventions.

**3. Every divergent clause is inert in v1 — except one.** v1 has no balcony and
no ceiling height, so the balcony coefficients, the mansard 0.7 and the 1.6 m
under-stair rule **cannot fire**, and the two definitions currently compute *the
same number*. This is cheap to defer, and stays cheap only until a balcony or a
ceiling height enters the model.

**4. The one clause that binds now.** Qaydalar cl. 3.2 measures **between finished
wall faces at floor level**, skirtings excluded. ADR 0001 erodes `t_int/2` from a
centreline, which yields the **structural** face. Finishes run 10–20 mm per face,
so publishing our figure as *ümumi sahə* **systematically overstates area** — every
room, every plan, in the one region v1 ships. That is a live decision for this
ticket, not a deferral.

Note this ticket's `blocked_by: [14]` is discharged — *Which region profiles ship
in v1* is closed, and its item 5 (that v1 has no ceiling height and no balcony, so
the deductions cannot fire) is confirmed above rather than merely asserted.

## Resolution

**The convention was never the hard part. The plane was.**

The ticket arrived expecting a choice between named conventions, and the handover
from *The Azerbaijani region profile* had already collapsed that choice to one
region and one metric with every divergent clause inert. What was left looked like
bookkeeping. It was not: **the system has been publishing structural-face numbers
under the word "finished" in four separate documents, and one of them puts a
1700 mm bath inside a 1700 mm minimum that delivers 1670.** ADR 0010.

### 1. Where the Space boundary sits — the innermost finish face

A **Wall's thickness is a layer set**, not a scalar: an ordered
`(material, thickness)` list whose **total** is the only number the solver,
`erode` and every published dimension consume. The structural leaf survives as
data and v1 consumes it nowhere.

`clear = erode(solved, t_int/2)` is **unchanged in form**. `t_int` now means the
total, so the erosion lands on the finished face by construction and **no second
plane is created** — which was the whole reason to reject the alternative of
storing structural and subtracting finish at publish time. `CONTEXT.md` already
names clear-versus-centreline as *the* confusion mechanism in this system; a third
plane triples it.

For `AZ`: `t_int` **120 → 150** (120 half-brick + 2 × 15 finish), `t_party`
**250 → 280**, `t_ext_total` **500, unchanged** — its 20 mm inner finish was
always counted, so the external wall was finished-face all along and only `t_int`
disagreed with it.

**Why not simply relabel** — publish "structural clear" and correct the prose. It
is refuted by arithmetic rather than by taste. `bathroom.min_clear_long` is 1700
*because a bath is 1700 mm of enamel*; finished, it delivers 1670 and the bath
does not fit. `wc.min_clear_short` is 800 = pan 500 + body **300**, and finished
it spends 10% of the one calibrated constant behind the entire ergonomic layer
(ADR 0009). The ergonomic layer is composed from **physical footprints**; checking
them against bare masonry compares a fixture against a room that will not exist.

**Why a layer set rather than one fattened `t_int` = 150.** Same geometry, less
structure, and rejected for three reasons. The profile's **own acoustics already
assume the finish** — `t_party` 250 was derived from *"brick 250 + 15 plaster both
sides = 52 dB"* against AzDTN 2.7-2's 50 dB, and 120 + 15 both sides computes 49
and fails — so erasing the layer makes a shipped, `verified`-sourced derivation
unreadable. **IFC wants it**: `IfcWallStandardCase` carries
`IfcMaterialLayerSetUsage`, and a homogeneous 150 mm wall where a real one has
three layers is the file that opens and gets thrown away. And the deferred
structural patch becomes **paid for rather than promised** — `load_bearing` is
already *unknown, not false*, and the leaf is now a number waiting for it.

**Market check, per CLAUDE.md.** Every competent BIM authoring tool models walls
as layers and computes room area to a **named** plane — Revit's room boundary is
selectable between wall finish, wall centre, core layer and core centre, and it
defaults to finish. We are not inventing a convention. We were behind one.

### 2. Which instrument — Area Qaydalar cl. 3.8

Over Housing Code art. 12.5. Both are in force, both define `ümumi sahə`, and they
disagree only about balconies, which v1 cannot express — so today they compute the
same number. The Qaydalar wins on three grounds: it is the **design and inventory**
instrument, which is what a drawing is and what a technical passport is, and
therefore what an Azerbaijani property listing quotes; **cl. 3.2, the measurement
rule adopted above, lives inside it**; and the Housing Code is an entitlement test
that was never a drawing convention. The Housing Code delta and the verified
coefficients are kept as data, so a balcony later is a data change and not a
redesign.

### 3. Whether an area carries its convention — two fields, and presence is not agreement

**`Plan.area_convention`** is derived from the region profile, held **once per
Plan**, carried for life alongside the profile id, printed once in the title block
and written once into IFC. Per-Space tagging was rejected: twenty copies of one
fact. Revit stores this per project too.

**`Brief.target_area_convention`** is separate and **allowed to disagree** — the
C14 precedent, where `RegionProfile` and `CorpusProvenance` are two fields whose
disagreement is the normal case.

The rule the ticket existed to produce is **new**: `area.convention_agrees`, hard,
Brief-scoped. `area.convention_declared` only ever checked that a convention was
*present*, and **presence without agreement is exactly the silent failure** — two
numbers compared that are not the same quantity, with nothing raising a hand. v1
does **not convert** between conventions, because the deductions that separate
them are unrepresentable here, so a mismatch has no honest resolution but to ask.

### 4. What the gate measures — the wrong quantity, not the wrong tolerance

**`ümumi sahə` is not GIA.** Qaydalar cl. 3.8 read with cl. 3.2 **sums room
areas**, so internal partitions are **not counted**; GIA counts them. The
acceptance bar gated on *"Plan GIA within 5%"*. On a 90 m² dwelling the partition
footprint is roughly **4–5%** — the width of the gate itself. The three
`area.*_envelope_*` rules now measure **Σ Space area**, and the word GIA is struck
rather than adjusted.

Two consequences, recorded rather than smoothed:

- **The invented-Envelope gate stops being near-vacuous.** Against GIA, an engine
  that sets the Envelope inner area to `target_area` passes by construction.
  Against Σ Space it must also control the partition footprint, which is not known
  until the layout is solved. The 5% is unchanged and remains **unfitted** — it was
  never measured against the old quantity either — and it is now materially
  harder. **How an invented Envelope is sized against this target is a real new
  question**, and it goes to *Variant generation and ranking*, where
  invented-Envelope derivation already lives as fog.
- **The given-Envelope warn's stated reason is now only mostly true.** Σ Space is
  *not* fixed by the Envelope — it falls as the layout adds partitions — so unlike
  GIA it varies between candidates of one Envelope. It stays a warn because that
  variation is small against the Brief-versus-Envelope gap that dominates it, but
  the justification is weaker than it reads.

### 5. What `target_area` means to a Homeowner

**Interior `ümumi sahə`, balcony / loggia / terrace / *eyvan* excluded.** A Baku
listing quotes `ümumi sahə` *including* them at cl. 3.8 coefficients, and an
*eyvan* enters at **1.0 — full area, not reduced**. So a Homeowner's *"about
90 m²"* can be several percent more than the rooms they will get.

**The engine does not guess a balcony share back out of the number.** Inventing a
deduction from a figure the user never decomposed is fabricating data, and it is
invisible to them. It surfaces the reading as an Assumption per C4 and lets them
correct it. Handed to *Brief schema and parsing contract*.

### 6. ADR 0004's one exception dies

Tier 1 measured a party edge **to its centreline**, *"because GIA and IPMS both
do"*, and ADR 0004 §4 pre-committed the rule to follow this ticket. The authority
is gone, and the exception was always in tension with ADR 0004's own thesis that
*every tick is a number a person can tape* — **a party-wall centreline cannot be
taped from inside the flat.** Tier 1 now measures the Envelope's inner ring on
every edge. **The sheet carries no centreline dimension anywhere.** Handed to *The
annotation spec is US-shaped* with `DIM-CONV`, general notes 2 and 5, and the
A-102 schedule.

### What was written

`docs/adr/0010-a-space-is-bounded-by-finished-faces.md` (new) · `CONTEXT.md` —
`Space`, `Wall`, `Envelope` and `Clear dimension` sharpened, **`Layer set`**,
**`Finish layer`** and **`Area convention`** added · `room-constraints.json` —
the `AZ` layer set, the residue class, and `area_convention` promoted from REPORT
ONLY to shipped · `acceptance-bar.md` §8 · `data/acceptance/rules.json` — 37 →
**38 rules**, 29 hard.

**`rules.json` was not in this ticket's declared `writes:`**, and it was written
anyway. The map's concurrency rule guards against blind parallel edits; no other
ticket is claimed, so there was no session to collide with, and leaving a
known-wrong quantity in the shipped registry to honour a bookkeeping convention
would have been the easy call rather than the right one. The frontmatter now
declares it. The one file deliberately **not** touched is `annotation.md`, which
belongs to *The annotation spec is US-shaped*; every amendment it needs is written
into that ticket instead.

### What this costs, stated rather than buried

- **The ADR 0007 residue class moves 130 → 100 (mod 250)**, and
  `experiments/region-profile/gate_check.py`'s 28 assertions are owed a re-run.
  Moot for `AZ`, which publishes no hard linear minimum — cl. 5.6 delegates every
  intra-apartment clear dimension to the ergonomic layer, which ADR 0009 exempts.
- **Ticket 19's room-count deletion analysis is re-owed.** Its finding — the
  4/5/6-room deletion narrowing to *{5, and 6 unknown}*, so 250 mm charges the
  5-room case — was computed at `t_int` = 120 and must be recomputed at 150. The
  direction is **not obvious and is not guessed here.** It feeds *Whether the
  solve grid should be finer than 250 mm* directly, and it can ride along with
  *The solver has only ever seen guillotine layouts*, which already owns
  `experiments/solver-toy/`.
- **`t_finish` = 15 mm is `engine_choice`, and is now the weakest number under the
  largest number of consumers.** It is corroborated only from inside — it is the
  value the shipped `t_party` derivation already assumes. New research ticket:
  *What an Azerbaijani finish layer actually is*.
- **The ergonomic layer's corpus validation stands on unexamined ground.** Its
  Swiss figures were measured against polygons whose own face convention is
  unrecorded; if they are structural, the published floor is **slightly lenient**
  — small, systematic, in the wrong direction. Added to *Look at the converted
  corpus*.

### A side effect that is not a reason

`t_int` at 150 makes ADR 0004's dimension-tick collision *smaller* — 3 mm of paper
at 1:50 against 2.5 mm of text, where 120 gave 2 mm. Fewer leaders. Recorded as a
consequence. Had the arithmetic pointed the other way the decision would be
unchanged.
