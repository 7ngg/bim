---
id: 61
title: The notch is two components and a quarter of donors have more
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - docs/adr/0020-one-brief-one-envelope-area-many-envelope-boxes.md
  - docs/spec/proposer.md
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
