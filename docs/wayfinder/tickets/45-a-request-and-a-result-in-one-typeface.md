---
id: 45
title: A request and a result in one typeface
parent: map
labels: [wayfinder:prototype]
status: open
assignee:
blocked_by: []
writes:
  - docs/spec/homeowner-surface.md
---

# A request and a result in one typeface

## Question

**The Homeowner is shown `Room.target_area` and the delivered `Space` area in the
same typeface, and nothing on the surface says which is which.** *The whole of C2's
user* found this and left it as a ⚠️ with no ticket — the one state the map's
done-test exists to catch.

It is not drift and it is not rare. `brief.md` §9.3 makes a target a **two-sided
band**, so a delivered area landing off its target is the **normal** case, not an
error. The Homeowner reads their own request back as though it were a promise, and
then reads a different number on the plan.

⚠️ **Observed, not measured.** The prototype's plans are not solves of its own
Briefs, so nobody has yet seen the two numbers disagree on a real generate cycle.
Whoever takes this should decide early whether the prototype needs a real solve
behind it before the question can be answered honestly, or whether a fixture with a
deliberately off-target area is enough.

## The Practitioner half is already paid, and it is the shape of the answer

*What geometry an `IfcSpace` actually gets* closed this for the Practitioner:
`Pset_SpaceCommon.NetPlannedArea` carries the resolved target and
`Qto_SpaceBaseQuantities.NetFloorArea` carries the delivery, two properties apart
on one entity, and a Practitioner reads the delta unprompted (`ifc-export.md`
§8.2a). IFC had a first-class place for the distinction. **The Homeowner surface
does not, and that is the whole of this ticket.**

Note the asymmetry that makes it hard rather than a labelling job: a Practitioner
*wants* the delta and knows what to do with it. C2's Homeowner "cannot read a
dimension string" and judges by *would I live here*. Showing them two numbers and a
difference may be worse than showing them one — and which one is then a real
decision, not a default.

## What this has to settle

1. **Whether both numbers appear at all**, or the target is retired from the result
   view once a plan exists and survives only in the editable Brief — which C4 makes
   the real interface, so it is not hidden, only moved.
2. **If both: what distinguishes them** — position, typeface, label, or an explicit
   delta. All four are cheap; they are not equally honest.
3. **What the surface says when the delta is large but legal.** §9.3's band is
   two-sided and `dim.max_area` is hard at `both`, so a plan can sit far from a
   target and still be a survivor. There is a message here and nobody has written
   it.
4. **The locale dimension.** Whatever text this adds is Azerbaijani, and it lands in
   the same schema hole as the 38 rule messages — see the Acceptance-bar row.

## What this is not

Not a re-opening of `homeowner-surface.md`'s settled decisions: Azerbaijani, the
`both` set, the living-document framing and the fixture render all stand. Not the
**room tag's** Homeowner-audience fallback, which is *The annotation spec is
US-shaped and the drawing is now Azerbaijani*. Not the **stated-Brief-contradicts-
itself** parse defect, which *What the engine says when the Envelope is bigger than
the programme* has already **closed** — read its resolution and ADR 0015 before
choosing a severity here, because that ticket settled how a parse-time bound
inherits the severity of the rule it is the pre-image of, and any message this
ticket adds sits in the same family.
