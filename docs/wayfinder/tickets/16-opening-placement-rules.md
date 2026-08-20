---
id: 16
title: Opening placement rules
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: [7, 14]
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
