---
id: 30
title: The Proposal cannot express zoning
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
---

# The Proposal cannot express zoning

## Question

**Everything this system optimises is pairwise, and the property architects rank
plans by is not.**

The Proposal transmits **separation directions** — for each pair of Rooms,
whether one is left of, right of, above or below the other, or abstains
(`CONTEXT.md`). The solver promotes those to hard linear constraints. The
arrangement metric scores per-pair agreement, and *Proposer architecture survey*
found per-pair agreement is what predicts survival. So the whole chain, from
corpus conversion to Proposal to objective to metric, is pairwise.

**No pairwise relation can express any of these:**

- **Day/night zoning.** "The bedrooms are grouped, and they are away from the
  entrance." That is a property of a *set* against another *set*, and it is the
  first thing any architect checks on a residential plan.
- **Served and servant.** Bathroom next to bedrooms, utility next to kitchen —
  clustering by function, not by direction.
- **Sequence.** Entry → hall → living is an ordered path, not a set of
  left-of relations. Two plans with identical pairwise separations can have
  completely different entry sequences.
- **Facade allocation.** Which rooms get the good elevation. H8 asks only whether
  a habitable room touches *an* exterior run; it cannot say the living room
  should get the long one and the bathroom should not.

A plan can satisfy every pairwise relation in a real dwelling and still put the
WC off the living room and the master bedroom next to the front door. The map has
two partial hooks and neither is zoning: **forbidden adjacency** (a blunt
per-pair veto) and **circulation** (private rooms receive but never forward,
which is a weak day/night proxy that fires only through the contact graph).

**What has to be decided:**

1. **Whether zoning belongs in the Proposal, the Acceptance bar, or the ranking.**
   Three different answers with different costs. In the Proposal it must be
   expressible as constraints the solver can post — a set-versus-set separation is
   posted as "every room in A is left of every room in B", which is cheap and
   linear. In the bar it is a predicate. In the ranking it is a soft score and
   changes nothing about what is generated.
2. **Whether zones are Brief-stated or inferred.** A Homeowner says "I want the
   bedrooms away from the living room" in prose, and C4 says the Brief is the real
   interface — so this is probably a Brief field, which makes it *program* like
   `access_via` rather than geometry. If it is inferred from room type instead,
   say from what.
3. **Whether the corpus can even supply it.** Swiss Dwellings has room types and
   geometry; whether real dwellings show consistent zoning that a model could
   learn is unmeasured. It is measurable — the converted corpus from
   *Rectangularising real rooms* has typed rectangles and an entrance side.
4. **What it does to the arrangement metric.** *What the model proposes* defines
   three numbers, all pairwise. If zoning is the thing that matters, the metric
   is measuring the wrong property well. Feeds *Validate the arrangement metric
   against the solver*, which is currently validating it against **solver
   survival** rather than against **plan quality** — those are different tests
   and only the first is scheduled.

**Why this is not the existing fog patch.** *Plan quality beyond the validator*
asks whether the soft-rule score correlates with human judgement. That is an
**evaluation** question. This is a **representation** question: the Proposal
contract, as specified, has no vocabulary in which zoning can be stated, so no
amount of eval will surface it and no training run can learn it. A metric can be
fixed later; a contract that cannot express the property has to be reopened.

**Deliverable.** A decision on where zoning lives, and if it enters the Proposal,
the amendment to `docs/spec/proposer.md` §1 and the constraint form for the
solver. Plus the corpus measurement in item 3, which is cheap and tells us
whether there is a signal to learn at all.
