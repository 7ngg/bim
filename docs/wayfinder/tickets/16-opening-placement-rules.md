---
id: 16
title: Opening placement rules
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: [7, 14]
writes:
  - docs/spec/openings.md (new)
  - data/standards/room-constraints.json
  - data/acceptance/rules.json
declared_on_resolution:
  - docs/adr/0021-a-door-is-placed-by-walking-in-and-none-swings-into-circulation.md
  - CONTEXT.md
---

# Opening placement rules

## Question

*Canonical geometry model* settled what an Opening **is** — hosted, typed from a
regional catalogue, three distinct widths, swing structural rather than
decorative. It deliberately did not settle **where each one goes**, because that
is a rule, not a representation. This ticket is that rule.

It exists as its own ticket rather than as a footnote because closing ticket 01
surfaced a **circular dependency** that has to be designed around:

> AD M Volume 1 Table 1.1 makes corridor clear width a function of the door widths
> opening onto it *and the approach direction* — a 750 mm doorway needs 1200 mm off
> head-on, an 800 mm doorway needs only 900 mm. Neufert goes further and makes it a
> function of **swing direction**: doors one side opening *into rooms* → 900 mm;
> opening *into the corridor* → 1400 mm. But the solver sizes the corridor, and
> openings are placed **after** the solve.

Ticket 01's provisional answer — **pre-size corridors conservatively from the
region profile's worst-case door arrangement** — keeps openings post-solve and
leaves the measured 6.25 s untouched. Confirm it or replace it, and if confirming,
produce the actual constants.

Decide:

1. **Position along the segment.** Centred, offset to a corner with a nib, or
   chosen to suit circulation? AD M gives a **300 mm nib** to the leading edge
   maintained back 1200 mm; that is a component of the rule, not the rule.
2. **Hinge side and swing direction.** What picks them. Known hard constraints:
   the entrance-level WC door must open **outwards** with the opening overlapping
   the pan by 250 mm; doors in lobbies 1500 mm apart with 1500 mm between swings.
   Both from AD M.
3. **Which openings get a leaf at all.** Cased openings are what make a plan read
   as a home rather than an institution, so this is a quality lever, not a detail.
   What rule decides kitchen→living is cased and hall→bedroom is not?
4. **Which catalogue entry.** Room type presumably picks the leaf size — Neufert's
   rule of thumb is room doors ≈800 mm clear, **bath/WC ≈700 mm**, flat entrance
   ≥900 mm. Confirm against the region profile and note that the 700 mm collides
   with accessibility minimums (conflict C4 in the standards findings).
5. **Windows.** How many per room and how wide. One 1200 mm window centred on each
   exterior wall is the spreadsheet look; the representation already allows many
   per segment, so the rule has to earn the realism. The glazing-area ratio is a
   soft objective already sitting in the region profile.
6. **The corridor pre-sizing constants** the solver needs, per region, and what
   worst case they assume.

The residual risk ticket 01 left here: **a door fitting at all is guaranteed by
construction**, since the solver's contact threshold is `structural opening width
+ t_int`. What is *not* guaranteed is **swing clearance**, which in v1 rejects the
plan rather than triggering a re-solve. Confirm that is acceptable, or design the
alternative.

Waits on *Acceptance validator spec*, because rules 1–2 must satisfy a
swing-clearance predicate that ticket composes (the corpus hands over components,
never a finished predicate), and on *Which region profiles ship in v1*, because
the catalogue and every constant here is regional.

Deliverable: the placement rule set, precise enough to implement, plus the
per-region constants and a worked example on one plan.

---

## Inherited from *Acceptance validator spec*, now closed — do not re-derive

- **The swing-clearance predicate is composed, and is now yours to satisfy.** A
  **swing footprint** is the leaf-side square of side `leaf_width` anchored at the
  hinge — the bounding box of the swept quarter-disc, chosen because it is
  conservative, integer, and evaluable with no fixture model. Three hard rules:
  footprint ⊆ the receiving Space; no two footprints overlap (this *generalises*
  AD M's 1500 mm lobby rule to every arrangement, so decision 2 needs no separate
  lobby case); and a 300 mm nib clear at the leading edge maintained 1200 mm back.
- **Decision 2's WC rule is `deferred` in the registry, not adopted.** The outward
  swing overlapping the pan by 250 mm needs a pan, and fixtures are still fog. Its
  source and number are carried so adopting it later is a data change — but do not
  design decision 2 around a predicate that cannot fire in v1.
- **Decision 6's corridor constant has a floor: 900 mm clear, hard, VERIFIED.**
  AD M's 750 mm pinch allowance for ≤2 m is **dropped** — a Space is a rectangle
  and has no localised narrowing, so the relief could never fire. Pre-size above
  900, never below.
- **The entrance door is an Assumption you own.** `entry.exists` and
  `entry.single_primary` require at least one `entrance_door` on an External
  segment with exactly one flagged primary — one by default, more allowed (a house
  may have a back door; a flat gets exactly one). **Which Room holds it and where
  on the segment it sits are defaulted from knowledge and surfaced**, and that
  defaulting rule is this ticket's.
- **Decision 5's windows now carry a hard fit rule.** `open.fits_segment` —
  structural width + 2 × 100 mm jamb return ≤ segment length — applies to windows
  as well as doors, and `win.habitable_has_window` is hard *topology*: every Space
  needing a window hosts one on an External segment of that Space. The glazing
  ratio stays soft at 1/8, so realism in decision 5 is bought by the placement
  rule, not by the validator.
- **The residual risk is confirmed as accepted**: swing clearance rejects the
  Plan; it does not trigger a re-solve.

---

## Inherited from *Building scope and envelope handling*, now closed — do not re-derive

- **The Envelope is an ordered ring of edges**, each `exterior` or `party`, with a
  separate `entrance_side` flag (ADR 0003). Two rules in this ticket read it and
  currently do not:
  - **A party edge hosts no window.** The window-ratio rule needs each Space's
    exterior run computed against **filtered** faces, not every boundary face. Today
    a mid-block flat's bedroom can satisfy it on a wall shared with a neighbour.
  - **A party edge hosts no primary entrance unless it is `entrance_side`.** A
    flat's front door *does* pierce a party wall — onto a common corridor — which is
    why the flag is orthogonal to the condition rather than a third value.
    `entry.single_primary` must place on an `entrance_side` edge.
- **The entrance edge is fixed before the solve**, because it is the source node of
  the circulation flow. Opening placement receives it; it does not choose it.
- The windowless-kitchen **warn** and the topological window rule are unaffected in
  form, only in which faces count.

## Inherited from *Dimensioning and annotation rules*

This ticket is now the **single source** of three values the drawing publishes,
which raises the bar on each from "a rule the engine follows" to "a number a
builder sets out from".

- **The internal-door setting-out constant.** The drawing dimensions every
  internal opening in-plan, from the nearest perpendicular wall face to the near
  jamb of the structural opening. That distance is this ticket's to decide; the
  drawing only measures it.
- **Handing and swing direction.** Both are drawn — the leaf at 90° plus its arc —
  and both are columns in the door schedule on sheet `A-102`. A cased opening draws
  no leaf and no arc, and its handing cell reads `—`, so the *kind* enum has to be
  legible from the placement rule's output.
- The `Swing footprint` in the model stays a clearance abstraction and is **never
  drawn**; what is drawn is the real leaf swing. Worth stating because the two
  differ deliberately — the footprint is the conservative bounding square — and a
  drawing that rendered the abstraction would look wrong to anyone who knows what a
  swing arc is.

## Inherited from *Which region profiles ship in v1*

**Opening catalogue keys are user-visible strings owned by the region profile**,
and v1 has exactly one profile, `AZ` (ADR 0006). They are not internal ids: the
type marks on the plan and the rows of the door and window schedules that
*Dimensioning and annotation rules* put on their own sheet both cite them, so a
key is read by a builder.

Two consequences for this ticket. The catalogue is **discrete by design** — the
same move ADR 0003 made for dwelling type, a chosen set beating free
specification — so opening placement is choosing from a list, never dimensioning
freely. And every dimension the placement rules produce lands in a profile whose
**thicknesses must be even millimetres**, which matters here because a structural
opening is a leaf width plus frame and tolerance, and *Dimensional standards
corpus* found door widths propagate into masonry rather than staying in a
schedule.

The catalogue's contents are owed by *The Azerbaijani region profile*, not by
this ticket. What this ticket owes is the placement rule set that consumes them.

## An ordering question this ticket inherits and may not own

**Doors are placed after the solve, and an architect places them with the room.**
*Acceptance validator spec* found Opening rules "unpostable by construction" —
Openings do not exist when the solver runs — so the pipeline is solve, then
place. ADR 0001 consequence 3 makes the solver reserve *enough* shared wall
(structural opening + `t_int`), which is why circulation is satisfiable. It does
not reserve **where**.

That gap is architectural, not procedural. A door's position decides whether a
room has an unbroken furniture wall, whether two doors eat the same corner, and
whether the swing lands in the circulation path rather than across it. A room
that is dimensionally fine and has its only door mid-wall is a room an architect
would redraw, and nothing in the current ordering can prevent it — the solve that
fixed the geometry had no opinion about doors beyond a minimum contact length.

Decide here whether that is acceptable for v1, or whether the solve needs a
door-position variable (which would make Openings partly postable and reopen
*Acceptance validator spec*'s enforcement-site table). Stating "acceptable, and
here is why" is a fine answer; leaving it unstated is not, because it is one of
the two or three things that most makes a generated plan read as generated.

---

## Resolution — 2026-08-26

**`docs/spec/openings.md`, [ADR 0021](../../adr/0021-a-door-is-placed-by-walking-in-and-none-swings-into-circulation.md).**
The six decisions are taken, the two risk confirmations are made, and the
ordering question is answered — but the finding that reorders the ticket is one
nobody had asked for.

### The three rules already shipped did not agree

`circ.potential_reachability` admits a contact edge at `w_struct + t_int`. ADR
0001 consequence 3 is explicit that `+ t_int` is *only* the centreline-to-clear
correction, so the reserved **clear** run was exactly `w_struct` — **zero jamb,
zero nib**. On that same segment `open.fits_segment` hard-requires 100 mm per
side and `open.leading_edge_nib` hard-requires 300 mm along the wall. Floor is
`w + 400`, and hinging at either end gives the same number.

**A solve could pass potential circulation and be hard-rejected the instant a
door was placed on the run it had just certified.** Two constants, two files, two
tickets, and the arithmetic between them had never been done.

Worse than a contradiction: at a minimum-length contact the old threshold admits
**exactly one** door position — mid-wall. So the threshold was not permitting the
room an architect would redraw, it was **specifying** it. The ticket's own
closing section calls that one of the two or three things that most makes a
generated plan read as generated.

### The answers

1. **Ordering — post-solve stays, and the threshold moves to `w + t_int + 400`.**
   A door-position variable was rejected: it makes Openings partly postable,
   reopens *Acceptance validator spec*'s enforcement-site table, and spends time
   on a solver the map already puts on the edge of the p95 cliff. It is also
   nobody's practice — of ~20 published generators **none emits a wall with
   thickness**, so none places a door, and the commercial tools place openings by
   rule after the layout. Post-solve is both the cheap path and the industry's
   path, which is the coincidence that needed checking rather than accepting. It
   survives, but only with the reservation corrected. **Ticket 01's provisional
   answer on corridors is replaced, not confirmed** — see 6.
2. **Position — breadth-first from the entrance, each door pushed to the end of
   its run nearest where the path arrives.** No objective, no heuristic; ties
   break on coordinate so a regenerate is stable. This is what preserves the
   unbroken furniture wall, and the threshold in 1 is what makes it feasible
   rather than lucky.
3. **Hinge and swing — both derived, neither chosen.** Hinge at the pushed-to
   end, so leading edge and nib fall inboard. Swing into the **Receiving Space**
   (private, then wet, then further from entrance, then smaller), fallback to the
   other side, then reject. **No internal door swings into circulation.**
4. **Leaf or cased — every internal opening carries a leaf except
   `living`↔`dining`.** This **reverses the ticket's premise**, and the reversal
   is sourced twice. The `AZ` catalogue manufactures a **glazed living-room
   door** (DO 21-9) — nobody makes a purpose-built glazed door for a doorway with
   no leaf. And **AzDTN 2.7-2 requires no kitchen door**, read first-hand: every
   clause naming `mətbəx` — 5.2, 5.7, 5.8, 9.12, 9.13, 9.14, 9.20, 7.3.7, 9.7 —
   is area, height, daylight or ventilation. A cased kitchen is *permitted* in AZ
   and is still not what is built. The tidy predicate over `is_private` /
   `is_wet` was written and **discarded**: it cases `hall`↔`living`, where the
   catalogue says a glazed door goes. The open kitchen is a **Brief** decision —
   `living_dining_kitchen` merges Rooms — not a placement one.
5. **Catalogue — 800 is the interior door, not 900.** DG 21-8 is the ordinary
   interior door of a post-Soviet flat; DG 21-9 is what you draw for a *zal*.
   Neufert's ≈800 lands on the same rung, which is the check that matters, and
   900-everywhere would have cost 100 mm of reserved run per door under 1 for
   nothing. `storage` takes 700 (a *kladovaya* door), `utility` 800 (a washing
   machine goes through it). **The 700 mm bathroom door stands** against conflict
   C4, with the refusal written down and pointed at `body_zone`'s identical
   refusal of AD M's 750.
6. **The corridor constant is derived, and it is still 900.** Decision 3's rule
   removes the worst case instead of pre-sizing for it: Neufert's 1400 mm arm is
   for doors opening *into* the corridor, and under 3 none does. The hall carries
   exactly **one** swing footprint — the entrance door's, an 800 mm square — which
   a 900 mm hall contains. Two independent readings now agree on 900: this
   derivation and the ergonomic floor's `hall.min_clear_short`.
7. **Windows — count is derived from the ratio, not fixed at one.** Longest
   `exterior` run first, one entry per Space repeated, 600 mm minimum pier,
   centres at `(2i−1)/2n`, second edge only when the first is full. Even
   distribution buys the facade rhythm *and* keeps windows off corners with no
   corner rule.
8. **Entrance — the invented `hall`'s segment on an `entrance_side` edge,
   swinging inward.** Nothing to search: the hall exists to be that room, and a
   candidate whose hall misses the edge is already dead at `entry.exists`. Inward
   because a common corridor is not in the model, so an outward swing is one this
   engine cannot check.
9. **Residual risk confirmed.** Swing clearance rejects the Plan; it does not
   re-solve. With 1 in place it should be rare, and when it fires the cause is a
   Proposal that put two doors in one corner — a quality signal worth surfacing.

### Three widths, and one is refused

Structural `verified` off the GOST mark; block `verified` at `opening − 30`
wide / `− 29` high; leaf **derived** by `leaf = opening − 100`, which on the
catalogue's five door openings reproduces GOST 6629-88's published leaf series
exactly (700→600, 800→700, 900→800, 1300→1200) — the check that promotes it from
a guess. **Clear is not published**: the frame section is joinery the profile
does not carry and no shipped rule consumes it. CONTEXT requires that which width
is meant is always stated, not that all three exist.

Leaf width is load-bearing past the schedule: `open.swing_within_space` builds
the footprint from it, so a bathroom door sweeps a **600** square, not 700 — 100 mm
of relief in every wet room that had been silently spent.

### Two defects found in shipped data

- **`win.habitable_has_window` was satisfiable on a party wall.** It said
  "External WallSegment", and CONTEXT's *Wall* term says **a party wall is
  External**. A mid-block flat's bedroom could take its daylight off the
  neighbour. Re-keyed to the Envelope edge's `condition`. This is exactly the
  handoff *Building scope and envelope handling* left here, and it was live.
- **Three shipped places disagreed about the kitchen window** —
  `kitchen.needs_window: false`, `AZ.windows.kitchen_windowless: false`,
  `win.kitchen_windowless` **warn** — against AzDTN cl. 9.12, `verified` and
  mandatory for living rooms *and* kitchens. `needs_window` moves to **true**. A
  Baku flat with a windowless kitchen is not buildable. `is_habitable` stays
  false: daylight and habitability are different questions AzDTN answers
  differently.

### `balcony_door` can never be placed, and something rests on it

v1 models no balcony, so BS 22-7,5 has no receiving Room and no rule that would
emit one. Flagged `placeable_in_v1: false` rather than deleted. But it is the
**sole anchor of `head_datum_mm`**, which ADR 0012 justifies as *the balcony
door's own catalogue head, because a balcony door and the window beside it share
a lintel* — a composition v1 cannot draw. **The number is right and the reason is
dead**: 2200 is right because an AZ window head sits above the door head. Sills
(700/700/1000) are unaffected; re-anchoring to 2100 would collapse the two head
lines and is refused.

### Written

| File | What |
|---|---|
| `docs/spec/openings.md` **(new)** | §1–§11: catalogue mapping, three widths, position, hinge and swing, leaf-or-cased, windows, the entrance, what the solver must reserve, the two dead room types, eight handoffs, and a worked 3-otaq example |
| `docs/adr/0021-…` **(declared)** | the four interlocking parts, the rejected door-position variable, the corridor constant's derivation, and the nib's re-basing |
| `data/standards/room-constraints.json` | catalogue entries gain `opening_w/h`, `block_w/h`, `leaf_w/h`, `kind`, `glazed`, `placeable_in_v1`; new `dimension_derivation`, `door_for_room`, `window_for_room`, `min_pier_mm`, `placement_spec`; `kitchen.needs_window` → true; `reachable_in_v1: false` on `corridor` and `entrance_lobby` |
| `data/acceptance/rules.json` | six rules **amended, none added** — the 38 count is untouched, deliberately, because `acceptance-bar.md` is claimed elsewhere |
| `CONTEXT.md` **(declared)** | **Nib**, **Receiving Space** and **Placement order** are new; **Opening**'s cased-opening sentence and **Head datum**'s balcony-lintel reason are both marked `_Avoid_` |

`gate_check.py` **229/229** and `env_check.py` **28/28** after the edits.

### Handed on

| Handed | To |
|---|---|
| The **INFEASIBLE rate** of the `+400` threshold. The arithmetic is exact; the cost is not measured | *What an ordered entry sequence costs the solver* — holds `experiments/solver-toy/` |
| The **exposure cost of forcing the kitchen to the facade** — one more Room competing for frontage | *H8 and the single-aspect flat* |
| **`win.kitchen_windowless` can no longer fire**; retire-or-keep moves the 38-rule count. Also: `win.area_ratio` is `soft` although AzDTN cl. 9.13 is a `verified` mandatory floor — the only statutory minimum on the map posted soft, left alone because severity is the bar's. Also: `open.leading_edge_nib`'s `src` should follow its re-based justification | whichever ticket next holds `acceptance-bar.md` — *A dwelling with no toilet passes every check* or *Fit the ENGINE_CHOICE acceptance thresholds* |
| **ADR 0012's head-datum justification is dead** while the number stands | ADR 0012's holder |
| A **glazed leaf draws a glazing line**; `Handing` and `Swing` schedule columns are now filled by a stated rule | *The annotation spec is US-shaped and the drawing is now Azerbaijani* |
| **`min_pier_mm` 600 is `engine_choice`** — the only unfitted constant this ticket adds | *Fit the ENGINE_CHOICE acceptance thresholds to the corpora* |

### What this ticket could not do

`docs/spec/acceptance-bar.md` is claimed by two open tickets, so six rule
**statements** moved in `rules.json` with no corresponding edit to the document
that publishes them. That is a real, temporary divergence between a rule and its
prose, and it is the price of the concurrency rule rather than an oversight —
listed above so the next holder of that file closes it rather than discovers it.
