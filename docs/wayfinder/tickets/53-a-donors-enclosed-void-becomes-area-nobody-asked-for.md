---
id: 53
title: A donor's enclosed void becomes area nobody asked for
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - docs/spec/proposer.md
---

# A donor's enclosed void becomes area nobody asked for

## Question

**10.0 % of converted dwellings carry an enclosed void ≥ 0.5 m²**, and every one
of them is admissible to the retrieval index. `void_census.py`, over 400 converted
dwellings, separating the Envelope's deliberate notch under-cut from real dwelling
floor: enclosed-by-Spaces unclaimed floor is p50 0.00 m², p90 **0.44 m²**, max
3.69 m² — **15.0 % of dwellings ≥ 0.25 m², 10.0 % ≥ 0.5 m², 4.8 % ≥ 1 m².**

⚠️ **Do not reach for `uncovered` in a fit record.** It sums the correct case
(Envelope over-reach) and the incorrect one together, which is exactly why nobody
had noticed. `void_census.py` splits them.

**This is not the acceptance bar's, and that was checked rather than assumed.**
*A dwelling with no toilet passes every check* was handed this as *"nothing in the
bar forbids floor that belongs to nothing"* and found the premise **false**:
`model.no_unassigned_area` is **hard**, `site: both`, `scope: plan` — *"The union
of all Space polygons and all Wall bodies equals the Envelope interior exactly"* —
and its own note says exact tiling is posted soft in the solver *for search speed*
and checked hard at the validator, *"the place where a 29× faster search is
prevented from shipping a hole."* An OPTIMAL candidate with a 1 m² unnamed hole
cannot be shown. No rule is owed.

**What survives is the proposer's.** The 10.0 % measured the *conversion*, so the
donor carries the void into the index; the warp has no term for it; and the solve
is then **required** to tile exactly. The void does not vanish — it is absorbed
into whichever bordering Room the objective finds cheapest, as floor the Brief did
not ask for and no Assumption surfaces.

Settle:

- **Does an enclosed void disqualify a donor from the index, or is it warped?**
  A threshold picked by eye is worse than none; the distribution above is the
  input. Note the interaction with `proposer.md` §2.2's exact-multiset gate —
  thinning the index at 0.5 m² costs coverage that ADR 0013 already measures as
  tight above nine rooms.
- **Which Room absorbs it, and is that a ranking term or a constraint?** Today it
  is neither: it falls out of the objective. A 3.69 m² void landing on a `wc` is a
  different plan from one landing on a `living`.
- **Does it reach the fidelity numbers?** ADR 0018's worst-room deviation is a
  **proportion** result — `fit_warp.py:373-384` normalises absolute area away — so
  a donor whose void is redistributed may score well on a metric that cannot see
  it. That measurement is `experiments/warp/`'s and the two should be read
  together.
- **Is a void ever *real*?** A duct, a chimney, a party recess. The conversion
  drops `SHAFT` and `VOID` as `NOT_A_ROOM` before fitting, so what remains is
  residue — but nobody has looked at one rendered. `render_sheet.py` exists.

The closing check: **a stated `target_area` and the Σ Space area of a plan built
from a voided donor agree for a reason**, not by the 5 % gate absorbing it.

## Concurrency

`docs/spec/proposer.md` is also claimed by *A third of real kitchens have no
window and the engine may not draw one*. Per the map's Notes this is a merge
hazard, not a dependency — do not run the two at once.

## Raised by

*Look at the converted corpus* measured it; *A dwelling with no toilet passes
every check* (2026-08-26) established it is not the bar's and re-homed it here.
