---
id: 89
title: A daylight rule the engine has only a proxy for
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - data/acceptance/rules.json
  - docs/spec/acceptance-bar.md
---

# A daylight rule the engine has only a proxy for

## Question

**Every regulator surveyed bounds a habitable room's *depth from its glazed wall*.
The engine bounds its *orientation-free proportion*. These are different
predicates, and the engine has only the second.**

Verified first-hand by ADR 0048's research:

| source | rule | force |
|---|---|---|
| SNiP II-L.1-62 cl. 1.19 | depth ≤ 6 m **and** ≤ 2× width | mandatory |
| SNiP II-L.1-71\* cl. 3.4 | same, **+ «при одностороннем освещении»** — single-sided lighting only | mandatory |
| Portugal, RGEU art. 69.º n.º1 d) | length ≤ 2× width for compartments ≥ 15 m², **waived** where openings are in the two most distant opposite walls | mandatory law |
| Belarus, ТКП 45-3.02-230-2010 cl. 5.5 | the rule in its faithful *depth* form, single-family houses | ⚠️ **reported, not read** |

**The USSR restricts its 2:1 to single-aspect rooms; Portugal waives its 2:1 for
dual-aspect rooms.** Same ratio, same room class, same condition from opposite
directions, two traditions with no contact between them. That convergence is what
identifies the quantity: **it is daylight, not proportion.**

**A 6 × 3 m room with its window on the long wall is 2:1 to this engine and
*ideal* to all three norms.** `dim.aspect_ratio_hard` cannot tell that room from
the same rectangle glazed on its short wall, which is the one an architect would
redraw.

## It is computable today, and that is why this is a ticket rather than fog

`win.habitable_has_window` already posts, at `site: both`, that each
`needs_window` Room holds a run of **EXTERIOR-condition** Envelope edge — ADR 0003
types the edge ring before the solve. So the glazed side is **already identified
per Room, pre-solve**. Depth is the Room's extent perpendicular to that run.
Nothing new has to be measured about the geometry; the quantity is one projection
off a datum the solver already has.

## What has to be settled

1. **Whether it ships at all**, and at what severity. ⚠️ It **adds a predicate**
   (`rule_count` 43 → 44), which C14 permits for the region-free base set and
   forbids to a profile. It is *mandatory* in three traditions, which is a
   stronger claim than anything `dim.aspect_ratio_hard` rests on — but AzDTN,
   the one region v1 ships, **dropped it**, so C14's *"a profile may raise a
   floor"* is not the lever and the region-free set is.
2. **Which limb.** The clause has two: **≤ 6 m absolute** and **≤ 2× width**. They
   are not the same rule and the corpus may support one and refuse the other.
   ⚠️ Kazakhstan reportedly caps apartment depth at 10 m, so the absolute limb's
   *value* is not settled by one tradition.
3. **The single-sided condition, which is the hard part.** Both traditions bind
   this rule *only* where daylight is single-sided. A dual-aspect Room is exempt
   in the USSR reading and waived in the Portuguese one. The engine would have to
   decide dual-aspect per Room — `win.habitable_has_window` finds *a* run, not
   *how many sides*, so this is the one genuinely new computation.
4. **What it costs.** ⚠️ **Unmeasured, and not measurable today**:
   `data/corpora/` is gitignored and not on disk, so `census.py` cannot run. See
   `room-area-bands.md` §13.1 for the derivation method that stood in for a
   measurement on the aspect question, and for its limits — it priced a
   *rejection rate* from published percentiles, and there is no published
   percentile for depth-from-glazing.
5. **Whether `dim.aspect_ratio_hard` narrows if this lands.** If the oriented rule
   catches the bowling alley, the orientation-free cap may be doing less work than
   ADR 0048 credits it with — or may be doing different work, since VLSI bounds it
   with no daylight in the picture at all.

## What this is not

Not a re-opening of ADR 0048. `dim.aspect_ratio_hard` at 3.0 and the
`dim.aspect_ratio_soft` gradient are settled and rest on their own evidence
(Swiss p99.5, the VLSI modal bound, Palladio's form). Not a change to
`win.area_ratio`, which is a glazing-area rule and settled by ADR 0024. Not an AZ
profile question — ADR 0048 decision 5 records why AZ takes no aspect cell, and
the same reasoning applies here: this is region-free or it is nothing.

## Conflicts

⚠️ Shares `data/acceptance/rules.json` with *A regulator states an aspect rule and
the engine says none does* (closed), *A cap fitted in one country and a target set
in another* and *The dwelling floor sits below the only Azerbaijani otaq-indexed
figure*. Concurrency only. `docs/spec/acceptance-bar.md` has no other claimant.

## Raised by

*A regulator states an aspect rule and the engine says none does* (2026-09-01),
ADR 0048 decision 6. Not taken there: it adds a predicate and needs a corpus cost,
neither of which fits a ticket whose subject was a false sentence about an
existing rule. `docs/research/room-proportion-standards.md`,
`docs/research/room-area-bands.md` §13.4.
