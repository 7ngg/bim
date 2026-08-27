---
id: 55
title: The statutory floor now has a price, and it is not the one it was posted at
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - data/acceptance/rules.json
  - docs/spec/acceptance-bar.md
  - docs/spec/brief.md        # declared on resolution, no other claimant
  - CONTEXT.md                # declared on resolution, no other claimant
---

# The statutory floor now has a price, and it is not the one it was posted at

## Question

**`dim.statutory_min_area` is hard, and the argument it was posted on is refuted.**
*A statutory floor, posted soft, in the one region v1 ships* made it hard — living
16 m², `bedroom_double` 10, kitchen 8 — reasoning that `market_default` sits at or
above `statutory_floor` in every reachable AZ cell, so **a Plan that reaches its
soft target clears the rule by construction**.

*The warp has never been measured against a stated target area* measured it. The
premise is true; the conclusion is false, because the warp does not reach the soft
target — it reaches a *proportion* of it. On Briefs whose every target sits at or
above `market_default`:

⚠️ **Every number this ticket was opened with is superseded. Use the right-hand
column.** *The sizing rung under-delivers by four per cent* found two defects in
the rig's Envelope — it eroded a 75 mm ring that ADR 0001 does not lose, and it
let the warp resize the notch, which ADR 0020's guarantee assumes it cannot — and
neither was `f`. Same sample, same seed, both fixed:

| | as opened | **corrected** |
|---|---:|---:|
| candidates losing a Room below its floor | 31,1 % | **25,5 %** |
| Briefs with no clearing candidate in a pool of 8 | 6,7 % | **3,6 %** |
| kitchens delivered below 8,0 m² when asked for 9,0 | 21,8 % | **17,4 %** |
| lower quartile margin of the kitchens that pass | +0,085 m² | **+0,518 m²** |

For scale, ADR 0018 measured **6,9 %** Brief-level loss from *every* dimensional
decline combined. This one predicate costs about **half** that again — not about
as much again, which is what this ticket was opened believing.

⚠️ **Do not take the halving as the whole change.** The kitchen's lower quartile
now clears by 518 litres rather than 85, so *"passing by luck"* no longer
describes it. But **17,4 % of kitchens asked for 9,0 m² are still delivered under
8,0**, and no sizing constant reaches that: it is the warp's own per-room
distribution, which survives a perfect level intact.

⚠️ **And do not reach for 18,8 %.** That was `calib`, which scales the box until
Σ Space hits `target_area` and so hands the rooms margin the Brief does not
entitle them to. A correctly-sized Envelope over-delivers by **0,4 %**, not by the
2,2 % of slack `calib` was buying.

Ticket 50 accepted this risk explicitly and named the trigger:

> A hard rule that is too strict is **discovered** — at build time, on the first
> Proposer run, and rolled back by one field. A soft rule that is too lax
> **ships**.

**The trigger has fired, early and on purpose.** What it does not do is make the
decision: 50's asymmetry argument is still standing and still good, and a rule
that costs 3,6 % of Briefs may well be worth it. That is the question.

## Settle

- **Does it stay hard?** The asymmetry that justified hard is unchanged. What has
  changed is that the cost is no longer hypothetical — and it is **3,6 %**, not
  6,7 %. Weigh them.
- **If it stays hard, what does a starved Brief see?** 3,6 % of Briefs get nothing
  from source A. `acceptance-bar.md` §11 requires the parse-time and no-candidate
  sentences to agree, and there is no bound whose edit resolves this one — the
  Brief was compliant. This may be source B's answer (ADR 0005) rather than a
  message, and if so the map is promising something it has not measured.
- **Is `max(ergonomic, statutory)` the right shape at the Plan site at all?**
  `dim.min_area` rejects 0,19 % of real dwellings and adds 0,00 % to the hard
  union; the statutory half carries the entire cost. A rule whose two halves are
  that unlike may want splitting rather than tuning.
- **Does the Brief owe a per-room pre-image?** ADR 0015 says a parse-time bound
  inherits the severity of the rule it is the pre-image of, and `brief.md` §9.4
  bound 1 bounds only the **sum**. A Homeowner asking for a 6 m² kitchen is
  currently told nothing at parse time and loses every candidate at the validator.
  ⚠️ This is a **new** bound, not an amendment — do not assume it is bound 1's job.

## What this ticket does NOT decide

- **The sizing rung**, which was [56](56-the-sizing-rung-under-delivers-on-the-warp-path.md)
  and no longer blocks this one. ✅ **Closed, and the premise it blocked on was
  wrong in the useful direction**: not *"two fifths of the 30,7 % is one
  constant"* — **none** of it was, `f = 0.0575` stands untouched, and what moved
  was two defects in how the Envelope had been measured. The number to judge is
  the corrected one above.
- **Whether retrieval-and-warp survives as source A.** That is the Proposer row's,
  and `proposer-architecture.md` §7.5 explicitly declines to draw it.

## Raised by

*The warp has never been measured against a stated target area, and a hard rule
now rests on it* (2026-08-27), which supplied the number and did not touch the
severity.

## Resolution (2026-08-28)

**It stays hard, at all five limbs, and the thing that moved is the shape rather
than the severity.** The trigger ticket 50 named fired inside a week, exactly as
designed, and firing it is what vindicates the argument rather than what refutes
it. Four reasons, in the order they bind — and the fourth is the one that would
have decided it on its own.

### 1. The asymmetry was never conditional on the price

Ticket 50 posted the rule on *discovered versus shipped*: a hard rule too strict
is found at build time and rolled back by one field; a soft rule too lax **ships**
a 6,6 m² kitchen to a Baku Homeowner as an unannotated survivor, indistinguishable
under C6 from a good one and uncatchable by C2's *"would I live here"*.

Discovery is what just happened. **The argument did not say *"hard until it costs
something"*** — it said the cost of hard is *recoverable* and the cost of soft is
not. Weakening the rule on the first exercise of its own recovery path spends the
argument on the single event that proves it works.

### 2. The price halved, and what is left is an upper bound

**3,6 %** of Briefs starved, not 6,7 %, against ADR 0018's **6,9 %** for every
dimensional decline combined. And 3,6 % is measured at **pool-of-8**:
`proposer.md` §2.2.7 says the fidelity sample is the 2,317 converted dwellings of
the ADR 0016 sample, *"so a pool of 87 in production is a pool of 8 here"*, against
a production median pool of **86.6** (4–6 rooms) and **58.7** (7–10).

⚠️ **This is a caveat, not a rescue.** §5a's own finding is that declines are
**correlated within a pool** — independence predicted 0,009 % against a measured
6,7 %, a factor of 780 — because every candidate shares one Envelope. What makes
the caveat worth recording is that the shared component was the **level** error,
and ticket 56 removed it: Σ Space now lands at **+0,4 %**. The residual is the
warp's per-room *distribution*, which varies by donor and therefore ought to thin
across a pool. **Ought to.** Nobody has measured it, so it is a ticket
— *What best-of-pool is worth at production pool depth* — and the caveat is on
`rules.json` as `dim.statutory_min_area.engine_cost.caveat` so the 3,6 % cannot be
quoted as a shipped figure.

### 3. The 17,4 % is the warp's, not the rule's

No sizing constant reaches it. Ticket 56 vindicated `f = 0.0575` and landed the
level at +0,4 %, so what survives is the warp's **per-room distribution**, which a
perfect level leaves intact. A predicate is the wrong instrument against a
proposer defect, and this map already has the precedent: §7.5 handed
`win.habitable_has_window`'s **45,19 %** *"to the retrieval and conversion side,
not paid for by weakening a statutory rule"* — the same object, from the same
side, at twelve times the cost.

### 4. The market settles it, and this is the reason that would have sufficed

`competitive-landscape.md` §5.2, its own heading: **code compliance is claimed by
six vendors and implemented by approximately zero.** Snaptrude and Maket run an
LLM over a PDF the user uploaded and never touch the geometry; Finch and
ARCHITEChTURES make the user author the rules and then disclaim responsibility for
them (*"the designer is responsible for compliance with regulations"*); Synaps'
terms say *"the Services are not tailored to comply with industry-specific
regulations so if your interactions would be subjected to such laws, you may not
use the Services"*; Maket's say the output *"cannot be used for construction,
permitting, or regulatory approval."*

**A curated, first-hand, geometrically-enforced statutory floor is the one thing
this engine has that the entire surveyed market does not.** It is `verified`, read
from AzDTN 2.7-2 cl. 5.7 directly, and it binds the geometry rather than a
document. Trading it for 3,6 % of yield sells the differentiator to cover a debt
the **proposer** owes — and C8 stays intact throughout, because being compliant
was never the thing C8 forbids. Claiming it is.

### 5. All five limbs, and the kitchen is the one that needed arguing

The kitchen is **16,88 of the 19,98** marginal corpus points and the limb the warp
fails, so it is the only one worth dropping. **Dropping it does not lower the
kitchen floor — it removes it.** The ergonomic `kitchen.min_area` is **1,8 m²**
(900 × 2100 mm, a galley strip) against a statutory 8,0. A 3 m² kitchen would pass
`dim.min_area`, pass `dim.aspect_ratio_hard`, and be shown.

And the Swiss p50 of **8,04** against a floor of 8,0 is not evidence the floor is
too high. It is evidence the floor sits **exactly where people build**, which is
what a *habitable* minimum is supposed to be. A limb that lands on the corpus
median is doing its job; a limb far above it would be the defect.

### 6. What moved: the composition became a term

`max(ergonomic, statutory)` was asserted inside `dim.statutory_min_area`'s own
statement, which made a **limb** amendment read as a **rule** amendment — the
opposite of what the per-limb table was built for. It is now
**[[Hard area floor]]** in `CONTEXT.md`: `max(ergonomic minimum, statutory floor)`,
per Room and never per part, with the two halves' unlike costs (0,00 % and
19,98 % marginal) recorded on the term itself. Each rule states only its own half.
`acceptance-bar.md` §11 and `brief.md` §9.4 read the term.

⚠️ **Answering the ticket's third Settle bullet directly: they were already
split.** `dim.min_area` and `dim.statutory_min_area` are two rule objects in
`rules.json` with independent severities — the splitting the bullet asked for had
happened and only the *sentence* was composed. So there was nothing to split and
something to **name**.

### 7. The Brief gains bound 9, and it is the first bound ADR 0015 declines

A Homeowner asking for a 6 m² kitchen was told **nothing** at parse time and lost
every candidate at the validator; §9.4 bound 1 bounds only the **sum**.
`brief.md` §9.4 now carries **bound 9** — a *stated* per-room target below that
Room's hard area floor — at **`warn`**.

⚠️ **Its rule is hard and the bound is warn, and ADR 0015 does not decide that.**
The implication fails: `model.no_unassigned_area` fixes Σ Space at the interior
exactly and §9.3 targets are two-sided bands, so a kitchen stated at 6 **can** be
delivered at 8 with another Room absorbing the loss — and `cross` per-Room
deviation reaches **+3,30 m² at p95**, so that is a real outcome rather than a
theoretical one. ADR 0015 consequence 5 is explicit that shipping a
one-directional implication at `hard` refuses buildable Briefs; consequence 2 is
explicit that a bound needing a fitted slack threshold of its own is the tell it is
not a pre-image. So bound 9 argues its own severity, which is what ADR 0015
requires of a bound that is not a pre-image — **the ADR is followed by being
declined, not overridden.**

§9.5 forbids the tidy alternative independently: raising a stated 6 to an 8 in the
defaulting ladder is auto-repair, and the ladder fills only **absent** fields.

### 8. What a starved Brief sees — and §11's guarantee gets a stated hole

The 3,6 % Brief is **compliant**: every bound passes, every target at or above
`market_default`, and there is no field whose edit resolves it. §11 required the
parse-time sentence and the zero-survivor sentence to agree, and here **there is
no parse-time sentence**, because there is nothing wrong with the Brief.
`acceptance-bar.md` **§11.1** now says so rather than leaving it silent — a
guarantee with an unstated hole is worse than a stated exception.

**Three steps, and the hard set is not one of them** (`rules.json`
`homeowner_surface.no_survivors.escalation`):

1. **Deepen the pool** before declaring starvation. No failing Plan is shown and
   no predicate moves — this is spending more *search*, which §11 never forbade,
   and it is the step most likely to be the whole answer. Ticket 57 sizes it.
2. **Fall through to source B**, per ADR 0005, already the declared behaviour
   where retrieval cannot answer. ⚠️ **Source B's per-room absolute area fidelity
   is unmeasured** — `proposer.md` §6.1's four plan-quality terms do not include
   delivered-versus-stated area. This is where the Brief **goes**; it is not
   something this map may claim will succeed, and §12 now owes that measurement.
3. **Then the no-survivor sentence, and it is a new kind.** Every other one names
   a Brief defect and the field that edits it. This one names none. It reports the
   *engine's* limit and offers the two edits that widen the search — raise
   `target_area`, or drop a Room — and must not imply the Homeowner asked for
   something wrong.

### 9. Two shipped sentences were dead and are now fixed

- **`brief.md` §9.2** read *"`statutory_floor` is **read by nothing in v1** — C14
  says a region profile never rejects a Plan, and every hard floor is the
  region-invariant ergonomic minimum."* Every clause of that died with ticket 50
  and nobody had struck it. Replaced, with what survives isolated: the ladder is
  about **defaulting a target**, and a statutory floor is never a target.
- **`acceptance-bar.md` §11's worked example** — *"three bedrooms, a bathroom and
  a kitchen need at least 58 m²"* — was reproducible from nothing (about 18 m²
  ergonomic, about 48 `market_default`), a defect `brief.md` §9.5 had recorded and
  handed to §12. It now quotes §3.1's published per-otaq series — **26,5 / 37,5 /
  47,5 / 57,5 m²** — which is measured rather than invented, and names the pair:
  market number as the recommendation, hard area floor as the line.

## What this resolution deliberately does not do

- **It does not touch `dim.min_area`.** The ergonomic half rejects 0,19 % and adds
  0,00 % to the hard union, and that inertness is the *reason* ticket 50 exists
  rather than a defect to fix here. Reasons 1 and 2 of §3 keep it as the
  region-free base.
- **It does not price the escalation's step 1.** Each extra pool member is a warp
  plus a solve against the shipped 15 s budget. Ticket 57 and the Runtime row.
- **It does not decide whether retrieval-and-warp survives as source A.**
  `proposer-architecture.md` §7.5 declines to draw it and this ticket has no
  standing to.

## Artifacts

- `data/acceptance/rules.json` — `dim.statutory_min_area` severity **unchanged at
  `hard`**, statement narrowed to its own half, new `engine_cost` block with the
  pool-of-8 caveat, four-reason note; `homeowner_surface.no_survivors` gains
  `escalation` and a corrected `diagnosis_source`.
- `docs/spec/acceptance-bar.md` — new **§3.2** (the trigger fired and the rule
  does not move), new **§11.1** (the starved Brief with no defect to name), §11
  worked example fixed, §12 rows.
- `docs/spec/brief.md` — **bound 9**, §9.4 preamble and table, §9.2's dead
  sentence struck, §9.5's worked-example item discharged.
- `CONTEXT.md` — new term **Hard area floor**; **Statutory floor** gains an
  `_Avoid_` on *"a Plan that reaches its target clears it by construction"*, which
  is measured and false.
- **ADR 0027 — *A statutory floor is a product position, and it is not tradeable
  for yield.*** The one reason above written nowhere else, generalised and
  **scoped to this rule alone**; its reversal trigger is the transcription or the
  market position, never a rising price.
- `data/acceptance/rules.json` — `engine_cost_note`, naming the three denominators
  this file has already seen misquoted for each other (0.5451 corpus, 0.036
  engine-Brief, 0.1559 whole-registry survival). ⚠️ `corpus_cost` was **not**
  renamed: the key is cited by name in `proposer.md`, `corpus-smoke/README.md` and
  two tickets, and a rename buys nothing the note does at the cost of a
  cross-document sweep through a file another ticket claims.
- `docs/wayfinder/MAP.md` — the Runtime row gains the escalation's unpriced
  step 1, and **Not yet specified** gains it as fog rather than a ticket, because
  its size is unknown until 57's curve lands.
- New ticket: *What best-of-pool is worth at production pool depth*.
