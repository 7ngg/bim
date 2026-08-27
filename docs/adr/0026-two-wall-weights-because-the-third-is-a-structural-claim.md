# ADR 0026 — Two wall weights, because the third one is a structural claim

Status: **accepted** · 2026-08-28 ·
[One wall weight where a real plan draws three](../wayfinder/tickets/36-one-wall-weight-where-a-real-plan-has-three.md)

## Context

*One internal thickness, against a corpus that has no module at all* was sent to
ask whether a single `t_int` is defensible. It is: the shipped 150 mm lands 4 mm
from the corpus-optimal single value of 146, and area drift straddles zero. What
the measurement left behind is a different question, and it is not about
thickness at all:

| | |
|---|---|
| real dwellings showing **three** wall weights at 1:50 — envelope, internal bearing, partition | **76.1 %** |
| real dwellings showing only two | 23.9 % |
| what a uniform `t_int` draws, always | **two** |
| dwellings with a *single* internal thickness | 7.0 % |
| heaviest ÷ lightest internal class, median | 2.00× |

`single-internal-thickness.md` §2.3 named the failure mode precisely, and its
framing is what made this a ticket rather than a note: a plan with one partition
weight does not read as *generated*, it reads as **drawn by someone who does not
distinguish a partition from a bearing wall**. That is a competence signal rather
than a novelty signal, invisible to C2's Homeowner and the first thing C2's
Practitioner sees.

The ticket priced three shapes — **A** accept it and say so in the product copy,
**B** solve at the thicker value and draw the thinner one, **C** two `t_int`
inside one Plan — and invited a fourth answer.

## Decision

**The Plan draws two internal wall weights. It draws them because the third
weight is a structural claim, and the engine computes no structure.** The
admission is a **general note on the sheet**, not a line in the product copy, and
the two shipped notes that currently make the sheet misleading are corrected with
it.

`Wall.load_bearing` stays `None` permanently in v1 — *unknown*, never *false* —
and `Pset_WallCommon.LoadBearing` stays omitted from the IFC, which ADR
[0011](0011-ifc-is-a-reference-view-file-that-asserts-only-what-is-known.md)
already does. The model, the sheet and the IFC now say one thing instead of the
model and the IFC saying *unknown* while the sheet says nothing at all.

`t_int_bearing` = 250 stays in the profile, `verified` and unconsumed, where
`room-constraints.json` already calls it *"the deferred structural patch"*.
Nothing about this decision spends it.

## Why the third weight is not ours to draw

**The 76.1 % is measured on the wrong artifact class, and that is the whole of
it.** Swiss Dwellings is a corpus of *surveyed built dwellings* — buildings that
exist, whose walls were measured after a structural engineer decided which ones
carry load. Of course they carry a visible hierarchy. The engine emits a design
that has never been engineered: no loads, no spans, no structural scheme, one
storey at elevation 0 with no site. The three-weight hierarchy is a
**working-drawing** property produced by an engineering step this engine does not
contain and does not claim to contain.

An architect's concept plan for a new-build dwelling has two weights for the same
reason ours does. The three-weight plan appears at *işçi sənədləşmə* stage, after
the structural design exists. Drawing a fabricated hierarchy onto a concept
drawing is not more architect-like; it is a working-drawing feature forged onto a
concept drawing, and it is read as a forgery by exactly the audience that would
notice the hierarchy was missing.

The counter-case is renovation, where the bearing walls are *given* — existing
structure the designer inherits and works around. That is a real case and it is
not v1's: C5 ships a single dwelling whose Envelope is stated or invented, with
no existing fabric to inherit from.

## Why nothing in the pipeline could draw it even if we wanted to

Both B and C need a per-wall heavy/light label. **Three independent parts of the
system establish that no such label exists**, and none of them is an oversight to
be filled in later:

1. ADR [0003](0003-the-envelope-is-an-inner-face-ring-of-typed-edges.md)
   consequence 3 — *"`load_bearing` stays `None` on party walls; v1 still makes no
   structural claim."*
2. **The conversion destroys per-wall thickness at the source.**
   `experiments/rectangularise/fit_rects.py:125` rasterises at 250 mm and assigns
   each wall cell to the nearest room, *"which cuts each wall at its centreline"*.
   A donor hands over an arrangement and no thickness whatever.
3. `proposer.md` §2.3's model emits two box slots and a presence token. There is
   no thickness token, exactly as there is no window token (ADR
   [0025](0025-glazing-is-not-a-property-a-donor-hands-over.md)).

So B and C are not expensive shapes; they are shapes **blocked on a classifier
that does not exist**. Building one means the engine deciding load paths, and a
builder reads a 280 mm poché as *this wall carries load, do not remove it*. C8
forbids reading a regulatory document as a compliance target for far less than
this.

The best available source was weighed and refused on its merits.
`experiments/thickness-fidelity/classify_check.py` already classifies per-wall
thickness on the raw Swiss geometry, `fit_rects.py` reads the same source, and it
is already owed three per-record fields — a fourth would be one pass. **Inheriting
a heavy/light flag from the donor is not inventing structure, it is inheriting
it**, and that is the strongest argument on the other side. It still loses, for
two reasons that compound:

- The warp resizes a donor by a per-room area budget and the solve is free to
  select which separations it posts. A "heavy" flag surviving a 40 % stretch
  between two re-sized rooms is provenance wearing structure's clothes; it is no
  longer a statement about any load path that was ever engineered.
- **It covers source A only.** Source B has no thickness token and the invented
  Envelope has no donor. The sheet's wall hierarchy would silently depend on
  which proposer won — a worse tell than uniformity, because it is
  non-deterministic across two candidates for one Brief.

## Why B loses to C, which the ticket had the other way round

The ticket credits B with keeping ADR
[0001](0001-centreline-walls-over-a-dilated-solve-domain.md) consequence 5
*"exactly where it is load-bearing — the solve"*. That is true and it is not
worth anything, because **no hard rule binds the solve alone**. Both hard rules
bind the model, after it.

Solve at 280, draw selected partitions at 150, and the wall body straddles ±75 of
a centreline whose Space boundary sits at 140. The 65 mm strip on each side
belongs to nothing, and `model.no_unassigned_area` is **hard**, site `both`:
*"the union of all Space polygons and all Wall bodies equals the Envelope
interior exactly."* Priced off §3.3's own table — reserved footprint 10.6 % of
Σ Space at 280 against 5.7 % drawn at 150 — that is **up to 4.9 points of Σ Space
as void**, ≈4.3 at the corpus's own bearing share, since 88.6 % of internal wall
length measures under 200 mm. A whole `area.invented_envelope_hard` gate of
unassigned floor.

Redefine the Space as *bounded by real wall inner faces* so the void is absorbed,
and `model.space_matches_erosion` — hard, and whose own note says *"it fails the
day internal wall thickness stops being uniform, which is the point of keeping
it"* — dies instead.

**B breaks one of the two hard rules or the other. So does C.** B additionally
charges 19 of 36 ergonomic room-axes an extra 250 mm solve cell, in the five-room
band ADR [0009](0009-a-derived-minimum-is-not-rounded-onto-the-solve-grid.md)
already found the grid charging, which is the bottom of C13's band and the
corpus's commonest dwelling size. C costs one hard rule and no cells, and buys
10.3 of the 12.8 available fidelity points using values already in the profile.

**B is therefore strictly dominated and is recorded as refuted, not merely
unchosen.** Any future case for a second weight should be built on C.

## What the market does, which is the same thing

No authoring tool infers structural function, and the two that lead the market
ship an explicit third state rather than a default answer. ArchiCAD's wall
carries *Structural Function: Load-Bearing / Non-Load-Bearing / **Undefined***,
and Undefined is the default. Revit's `Structural` flag defaults off and is set
by a human. IFC has no third state at all — `Pset_WallCommon.LoadBearing` is an
`IfcBoolean` — and the idiom for unknown is to **omit the property**, which is
what ADR 0011 chose and is why that choice is now load-bearing twice.

On the generative side there is nothing to catch up to: `floorplan-generation-stack.md`
found **zero of ~20 published generators (2020–2026) emit walls with thickness at
all**. Inferring a bearing/partition split would not be catching up to the market.
It would be the one structurally novel move on this map, made in the one place
where being wrong is read as a safety instruction.

This is the same argument ADR 0010 used in the opposite direction — *"we are not
inventing a convention; we are catching up to the one the market shipped"* — and
here the shipped convention is `Undefined`.

## Why "accept it and put it in the product copy" is refused

Shape A's geometry is what ships. Shape A's *delivery* is not, and the file that
refuses it is `annotation.md`, which already made this exact argument for C8:

> Note 8 is C8, and it belongs **on the drawing**, not only in the product copy. A
> DXF outlives the session that produced it, gets emailed, and arrives somewhere
> the product copy never reaches.

A structural non-claim travels the same way and further, because the reader who
acts on it is a builder holding a printed sheet. Putting the admission in product
copy is the same silence with a receipt.

**And the sheet is currently worse than silent.** Two general notes are
individually true and jointly misleading:

- **Note 3** — *"All partitions `t_int` mm unless noted."* Nothing is ever noted.
  *Unless noted* promises an exception mechanism the engine does not have, and a
  Practitioner reads it as *the ones that differ are called out*.
- **Note 7** — *"Fire, thermal, acoustic and structural performance are not
  specified."* Performance is a calculation. **Identification is not
  performance.** A reader takes note 7 as "no structural calculations were run"
  and still assumes the wall the drawing renders heavy is the heavy one.

Neither note says the thing that is true: *every internal wall is drawn as a
partition and load-bearing walls have not been identified.*

## Consequences

1. **`Wall.load_bearing` is `None` for the life of v1**, and that is now a
   decision with a reason rather than a deferral. The field stays — ADR 0010
   bought it deliberately — but nothing in v1 writes it.
2. **The general notes gain the identification statement and note 3 loses
   *"unless noted"***, since no mechanism produces a noted exception. Wording is
   `annotation.md`'s, below.
3. **The Drawing check gains a thirteenth predicate** —
   `draw.structural_disclaimer_present` — on the precedent of the twelfth,
   `draw.schedule_totals_close`. A generated note that can be dropped by a
   regression is a note that will be. `annotation.md`'s to publish.
4. **No change to `rules.json`'s rule count, no change to the acceptance bar, no
   change to the conformance subset.** This decision deletes no predicate and
   adds none. `model.space_matches_erosion` and `model.no_unassigned_area` both
   stand, and ADR 0001 consequence 5 is untouched — which is the point.
5. **No change to the IFC.** ADR 0011 already omits the property; this ADR makes
   that omission a stated decision rather than a consequence of a nullable field.
   Asserted, not moved.
6. **No new technology and no refactor.** One note, one struck phrase, one check
   predicate, two glossary terms. That is the whole build cost, and it is not the
   reason for the decision — it is what is left after the reason.
7. **The fidelity gap is reclassified, not closed.** 76.1 % of real dwellings
   still carry a hierarchy this engine's sheet does not. The claim made here is
   that the hierarchy is not v1's to draw, **not** that its absence is free. A
   Practitioner comparing our sheet to a working drawing will still see two
   weights where they expect three; what changes is that the sheet tells them
   why.

## Hand-offs

Per the ticket, this writes an ADR and routes the rest by name.

**To `docs/spec/annotation.md`** *(no claimant)* — three items:

- **New general note.** Draft, for a holder who can source the term: *"Bütün daxili
  divarlar arakəsmə kimi, eyni qalınlıqda göstərilib. Yükdaşıyan divarlar müəyyən
  edilməyib."* — *all internal walls are shown as partitions at one thickness;
  load-bearing walls have not been identified.* **`arakəsmə` is `verified`** — it
  is AzDTN's own word, quoted at `az-finish-layer.md` cl. 8.24 (*"Daxili divarların
  və arakəsmələrin…"*), and `annotation.md` §8 already uses *daxili arakəsmələrin
  sahəsi*. **`yükdaşıyan` is unsourced and must not ship as written**: source it
  from `azdtn_2_17_1`, which `az-region-profile/thickness.md` already read
  first-hand for `t_int_bearing` cl. 6.9 and which necessarily names the thing it
  sets a thickness for.
- **Strike *"unless noted"* from note 3.** No mechanism produces a noted
  exception, and the phrase promises one.
- **Add `draw.structural_disclaimer_present`** to the Drawing check, 12 → 13.

**To `CONTEXT.md`** *(no claimant — declared on resolution, per the map's rule)* —
**Wall weight** is a new term: *how many distinct cut-wall thicknesses a sheet
draws; v1 draws two, envelope and internal, and never three.* **Wall** gains an
`_Avoid_` on `load_bearing`: it is *unknown, never false*, and **inferring it from
thickness, length or position is forbidden** — a drawn wall weight is read as a
structural instruction by the person holding the sheet.

**To the Homeowner surface and the product copy** — **nothing, deliberately.**
That is shape A's delivery mechanism and it is refused above. `homeowner-surface.md`
is claimed by *A request and a result in one typeface*; this ADR adds nothing to
its queue.

**To `docs/research/single-internal-thickness.md`** *(no claimant)* — one
correction, when someone next holds it: §4.4's *"ADR 0001's uniformity survives
where it is load-bearing (the solve)"* is true and misleading. Both hard rules
bind the model, so the cheap version of C breaks `model.no_unassigned_area` by up
to 4.9 points of Σ Space. The section prices B in solve cells and in area drift
and does not price it in hard-rule breakage, which is the price that decides it.

## Reversal trigger

Named, on the precedent of *A statutory floor, posted soft* — whose own trigger
fired early, which is why they are worth writing.

**This decision reverses when the engine is given structure rather than asked to
infer it.** Concretely: a Brief that carries existing fabric — a renovation or
refurbishment input where the bearing walls are stated by the user, surveyed, or
read off an existing plan. At that point the flag is *inherited*, the fabrication
objection dissolves, and shape C becomes arguable on its measured merits: 10.3 of
12.8 fidelity points at the cost of one hard rule, with `t_int_bearing` = 250
already `verified` and waiting.

**It does not reverse** on a better classifier, a larger corpus, or a bearing flag
derived from donor thickness. Those change how good the guess is; the objection is
that it is a guess presented as an instruction.
