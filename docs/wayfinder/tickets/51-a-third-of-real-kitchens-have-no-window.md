---
id: 51
title: A third of real kitchens have no window and the engine may not draw one
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - docs/spec/proposer.md
  - experiments/corpus-smoke/
---

# A third of real kitchens have no window and the engine may not draw one

## Question

**`win.habitable_has_window` rejects 43.3 % of real Swiss dwellings, and 23.0
points of that is the kitchen alone.** The corpus is the retrieval pool and the
training set. Decide what the engine does about a population it is learning from
and may not reproduce.

Measured by *H8 and the single-aspect flat* — first per-room evaluation of this
rule against real dwellings. 561 dwellings, 2 169 window-needing rooms, 150 floors,
same seed as the exposure run:

| | no window on its own boundary |
|---|---|
| BEDROOM | 5.9 % |
| ROOM | 6.9 % |
| LIVING_DINING | 9.0 % |
| LIVING_ROOM | 20.0 % |
| **KITCHEN** | **31.0 %** |

Per dwelling: **23.0 % fail on the kitchen alone**, 20.3 % on a non-kitchen room.

**The number is not an artefact.** Attribution audit found **zero orphan windows**
— every window on a dwelling boundary is attributed to at least one room — and
1 031 of 3 179 attributed to more than one, which biases *toward* finding a
window. The windowless kitchens are not niches: median **6.8 m²**, and **84.7 %
adjoin a windowed habitable room**. That is borrowed daylight — the `taxca-metbex`
arrangement AzDTN names and `profiles.AZ.windows.kitchen_niche_windowless`
deliberately holds `false`, on the reasoning that every instrument granting the
exception conditions it on electric hob plus mechanical extract plus an apartment
class the Brief does not carry.

**The rule is not the thing to change.** AzDTN 2.7-2 cl. 9.12 is `verified` and
mandatory, corroborated for houses at 2.7-3 cl. 8.14, and a Baku flat with a
windowless kitchen is not sellable. *H8 and the single-aspect flat* refused to
weaken it and refused to relax H8 by type to buy the coverage back.

## What is actually undecided

*What a room's area is allowed to be* set its cap at p99.5 rather than p95 on the
argument that *"the corpus is the retrieval and training population, so a rejection
there is coverage lost"* — at **26.6 %**. This is **43.3 %**, and unlike a
percentile it carries **no threshold to move**. So the question is not where to put
a number, it is which of these the engine does:

1. **Filter the retrieval and training population** to dwellings that satisfy the
   shipped hard bar. Honest, and it is a second drop on top of ADR 0016's, which
   fought Swiss 30.70 % → 9.74 % and ResPlan 40.10 % → 6.40 %. Nobody has measured
   whether the two drops overlap or compound.
2. **Keep the donors and repair on warp.** ADR 0018 makes the warp a solve; adding
   a kitchen window is a *topological* change, not a dimensional one, so it is not
   obviously something a warp can do. This needs the retrieval side to say whether
   its repair reaches it.
3. **Keep the donors and let the bar reject.** Retrieval returns donors that cannot
   survive; the measured rate says roughly two in five. That is a yield question
   and it feeds *The Proposal-quality floor, and how often the fallback fires*.
4. **Model the borrowed-daylight kitchen**, which is what 84.7 % of the real cases
   are — an open kitchen zone of a windowed living space. `kitchen_dining` and
   `living_dining_kitchen` already exist in the table as habitable types with their
   own windows; this would be a *third* reading where the kitchen is a Room with no
   window of its own. ⚠️ It reopens `kitchen_niche_windowless`, which was held
   `false` with reasons, so it must beat those reasons rather than ignore them.

⚠️ **Check the label before acting on the split.** `ROOM` is 914 of the 2 169 and
is the corpus's generic habitable label; `LIVING_ROOM`'s 20.0 % is measured on only
105 rooms and may be a labelling effect rather than a real arrangement. The kitchen
figure rests on 549.

⚠️ **This bites the training corpus and the retrieval pool differently.** A
retrieval donor that fails the bar wastes one candidate. A **trained** Proposer that
learned windowless kitchens from 31 % of its data will propose them everywhere, and
`proposer.md` §6.1's three plan-quality terms do not measure daylight.

## Deliverable

A decision recorded in `docs/spec/proposer.md` covering both sources, with the
overlap against ADR 0016's existing drop measured rather than assumed.
