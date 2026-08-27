# ADR 0025 — Glazing is not a property a donor hands over

Status: **accepted** · 2026-08-27 ·
[A third of real kitchens have no window and the engine may not draw one](../wayfinder/tickets/51-a-third-of-real-kitchens-have-no-window.md)

## Context

`win.habitable_has_window` is hard, `verified`, and rejects a large share of the
corpus the engine both retrieves from and trains on. *H8 and the single-aspect
flat* measured it at **43.3 %** of real Swiss dwellings, 23.0 points of it the
kitchen alone, and refused to weaken it: AzDTN 2.7-2 cl. 9.12 is mandatory,
corroborated for houses at 2.7-3 cl. 8.14, and a Baku flat with a dark kitchen is
not sellable. It left the corpus cost as an open ticket, with four candidate
answers — filter the pool, repair on the warp, let the bar reject, or model the
borrowed-daylight kitchen — and one instruction: measure the overlap against
ADR [0016](0016-the-conversion-names-its-own-ls.md)'s existing 9.74 % conversion
drop rather than assume it.

*What a room's area is allowed to be* had already set the precedent the ticket
was read against: it refused a p95 cap costing **26.6 %** of the corpus on the
argument that *"the corpus is the retrieval and training population, so a
rejection there is coverage lost"*. This was worse, and unlike a percentile it
carries no threshold to move.

**All four candidates share a premise, and the premise is false.** Each treats a
donor's glazing as something retrieval inherits and the engine must therefore
either avoid, repair, or accept. It inherits nothing of the kind.

## Decision

**The corpus is admitted unfiltered on glazing, for both sources.** No index
filter, no training filter, no reweighting, and no niche exception. A donor's
windows are overwritten in every case, so they are not a property the index may
be selected on.

**What replaces the filter is one index field and one ranking partition**, on the
property the warp does inherit: `frontage_reach`, the minimum over a dwelling's
`needs_window` Rooms of the boundary run that Room holds divided by the frontage
budget the solver posts for it. Candidates at `frontage_reach ≥ 1.0` pre-rank
ahead of those below. `docs/spec/proposer.md` §4.5, §2.2.1, §2.2.4.

## Why the premise is false

Three shipped documents, and none of them was written for this question:

- **`proposer.md` §1** — a Proposal is boxes. *"No validity guarantee; no
  adjacency graph; no wall geometry."* No openings.
- **`openings.md` §6.1** — the opening layer places **one window per Space**, on
  its longest `exterior`-condition run, **after** the solve.
- **ADR 0021's ticket, *Opening placement rules*, and *H8 and the single-aspect
  flat* §4** — `win.habitable_has_window` sits at site `both`, so the **solver**
  posts the frontage budget hard: 1 100 mm kitchen, 1 400 bedroom, 1 700 living.

`acceptance-thresholds.md` §13 had already handed `proposer.md` the same
observation in one line — *"Both are opening-layer rules, placed after the solve,
so a candidate's prior of clearing the bar is set by a layer the Proposal does not
carry"* — and named this ticket as one of its two recipients. This ADR is that
handoff worked out rather than a new claim.

## What everyone else does, and why it corroborates rather than merely reassures

`docs/research/floorplan-generation-stack.md`: of roughly twenty published
generators between 2020 and 2026, **exactly one emits windows** — GFLAN, which has
no code. Graph2Plan states the position the field actually holds: doors and
windows are *"added afterwards"*, its own limitations section listing that they
*"aren't captured in the model"*. RPLAN carries no windows at all, and WinNet's are
raster masks the paper itself calls weak.

So **the entire field treats glazing as a post-hoc layer over a room topology** —
which is what makes the premise behind all four options an easy one to hold and a
wrong one. It is not that this engine happens to place windows late; it is that
nothing anyone trains on carries them in the first place, so *"the donor's
windows"* were never a thing a proposer could inherit.

`docs/research/competitive-landscape.md`: eleven commercial products, none
documenting a daylight or glazing rule at unit-plan scale. Autodesk Forma has
sun-hours and daylight, and it is a **site and massing** tool — a different
question one storey up. A hard per-Room frontage budget, posted at the solver, is
therefore not a constraint the market would recognise as ordinary; it is a
differentiator this ADR is protecting, and the reason to protect it is that
AzDTN 2.7-2 cl. 9.12 makes it mandatory in the one region v1 ships.

## The measurements

`experiments/corpus-smoke/`, 46,565 dwellings — the whole converted-corpus room
cache, against the 561 the rule had been measured on.

**1. The residue that is actually inherited is six times smaller.**

| | dwellings |
|---|---:|
| hold a dark `needs_window` Room — the shipped rule's corpus cost | **38.55 %** |
| …and hold that Room on the boundary, where this engine glazes it | 33.17 % |
| hold a `needs_window` Room reaching **no** boundary | **5.88 %** |
| …or reaching less than the frontage budget the solver posts | **6.39 %** |

**86.04 %** of every dwelling the rule rejects is reglazed for free. **88.36 %**
of the corpus's 12,717 windowless kitchens reach a wall.

**2. The two drops compound; they do not overlap.** Paired on ADR 0016's own
2,600-dwelling sample, whose conversion refusal reproduces at 9.75 % against the
published 9.74 %:

| | window PASS | window FAIL |
|---|---:|---:|
| conversion **converts** | 1,413 | 902 |
| conversion **refuses** | 144 | 106 |

Both refuse **4.13 %** against **3.83 %** under independence — lift **1.08×**.
Joint drop **44.91 %**. ADR 0016 fought the Swiss drop 30.70 % → 9.74 %; a glazing
filter would hand back four times what that bought.

**3. Three published per-room figures move**, and one of them was a warning coming
true. *H8 and the single-aspect flat* flagged its own `LIVING_ROOM` figure as
possibly *"a labelling effect"* on 105 rooms. It was.

| | 561 dwellings | **46,565** |
|---|---:|---:|
| dwellings rejected | 43.3 % | **38.55 %** |
| kitchen alone | 23.0 pts | **21.64 pts** |
| `KITCHEN` | 31.0 % | **28.90 %** |
| **`LIVING_ROOM`** | **20.0 %** | **10.09 %** |
| `DINING` | not reported | **19.54 %** |

Restricted to h8's own population — floors carrying two or more dwellings — the
headline is 38.77 %, so the gap is sample size and not population.

## Why a rank and not a gate

*The two-notch cap is now evidenced* set the nearby precedent: add worst-room IoU
to the index, **gate hard** at 0.30, rank above it. This deliberately does not
follow it.

Worst-room IoU is a pure **donor-fidelity** fact — it is true of the donor whoever
retrieves it. `frontage_reach` is not: `proposer.md` §2.2.6 records that the
conversion knows boundary **contact** and not `exterior`-versus-`party`, so a run
measured on the donor may be party edge in the target Envelope. The property is
**necessary and not sufficient**, and it is a joint fact about the donor *and* the
Brief's Envelope. A hard gate on it would claim what it does not know.

Two supporting reasons: the residue is small, and a gate would thin hardest
exactly where ADR [0013](0013-the-room-count-promise-is-two-numbers-in-two-units.md)
already calls the index tight — landlocked runs **0.73 %** at three rooms to
**10.91 %** at ten and **12.83 %** at twelve.

The partition introduces **no free parameter**: the cut is at 1.0 because that is
where the solver's own hard constraint sits. `proposer.md` §2.2.4 refuses weighted
ranking terms on the grounds that a weight against area fidelity cannot be fitted,
and a partition needs none.

## The niche is refused again, and not for being small

`profiles.AZ.windows.kitchen_niche_windowless` stays **`false`**. A
borrowed-daylight exception would retain **91.47 %** of the index against 61.45 %
under the rule as shipped — thirty points, the largest single lever this ticket
priced, so it is not refused on size.

It is refused because **v1 has no producer and no consumer for it**: the engine
glazes kitchens itself, so it never needs to emit one, and no Brief can ask for
one — there is no `taxça-mətbəx` Room type, which ADR
[0022](0022-a-dwelling-owes-rooms-and-the-brief-is-where-that-is-checked.md) §4
already records as a partly unsatisfiable limb. A rule with neither is a rule that
cannot fire, and *H8 and the single-aspect flat* retired two rules on that test.

⚠️ **And the evidence it rested on does not say what two documents read it as
saying.** Both this ticket and *H8 and the single-aspect flat* §6 read *"84.7 %
adjoin a windowed habitable room"* as *"the `taxça-mətbəx` arrangement"* — an open
kitchen zone of a windowed living space. **Adjacency is not openness.** cl. 5.7's
niche is a recess open to the room it sits in; a separate kitchen with a door onto
a windowed living room is a windowless kitchen, which cl. 9.12 forbids outright.
Swiss Dwellings ships the openings, so the two can be separated in one direction:
of the 11,139 windowless kitchens that adjoin a lit room, **5,227 — 46.93 % —
carry a DOOR on that shared boundary**, and a niche has no door. The remaining
53.07 % is **undetermined**, not confirmed: an absent door polygon is not evidence
of an open threshold. Nearly half of the population is positively not a niche and
nothing licenses reading the rest as one. The statistic is sound; the gloss on it
is withdrawn. `proposer.md` §4.5.

## Consequences

1. **`frontage_reach` is a new index record field** and a new obligation on
   `experiments/rectangularise/fit_rects.py`, which already holds both inputs. It
   joins the cut-line frame and per-pair relation provenance that file is already
   owed.
2. **The training set is not filtered, and §2.3's warning is corrected.** The
   trained model has no window token; the only thing it can learn from a windowless
   kitchen is an **interior** kitchen, and that prior is **5.88 %**, not 31 %.
   `proposer.md` §6.1 gains a **fourth** plan-quality term so the rate is measured
   against the corpus's own rather than assumed.
3. **`win.habitable_has_window` now carries three corpus costs answering three
   questions** — 0.4519 raw-arm in `rules.json`, 38.55 % converted-index here, and
   a 15.97-point leave-one-out contribution to the bar. None is wrong and none is
   the others. `acceptance-bar.md`'s holder should say which is which.
4. **The gate stays arguable, and what would settle it is named**: whether
   `select_relations`' positive-cost filter posts the separations that enclose a
   landlocked Room. Nothing on this map has measured it, and it is
   `experiments/solver-toy/`'s.
5. **C6 is unmoved.** *Generate many, reject most, show survivors* is what absorbs
   the residue; this ADR changes which candidates are tried first, not how many.
