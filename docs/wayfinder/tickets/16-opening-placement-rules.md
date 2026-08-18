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
