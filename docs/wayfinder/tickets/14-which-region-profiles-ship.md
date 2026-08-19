---
id: 14
title: Which region profiles ship in v1
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
---

# Which region profiles ship in v1

## Question

Two closed research tickets independently concluded that **region cannot be
averaged away** — and neither was allowed to decide which region we actually ship.
That decision is this ticket.

What forced it:

- *Dimensional standards corpus* — the constraint table splits into a shared
  ergonomic layer and **regional profiles of ~30 numbers each**, and every cell
  additionally needs a tier (`statutory_floor` / `market_default` / `accessible`),
  because England alone yields five different minimum bedroom areas. It also found
  that minimum areas are **not comparable across regions even after unit
  conversion**, because measurement conventions differ.
- *Cross-dataset unification* — the model must be conditioned on the triple
  `(region, corpus, annotation_provenance)`, and the corpus mix is Swiss Dwellings
  (European) plus ResPlan (South Asian).

C12 says "not tied to any region". That was a statement of freedom, not a
requirement to serve everywhere at once — and both research passes say serving
everywhere at once produces something coherent nowhere.

Decide:

1. **Which profile or profiles ship in v1.** The candidates are not equal:
   - **UK** — the only profile checkable end to end, because Approved Documents
     and the NDSS are Open Government Licence v3.0 and freely republishable. The
     research recommends the test suite assert against it for that reason.
   - **Germany / DACH** — matches Swiss Dwellings, the primary corpus, and matches
     Neufert's origin. Best *data* alignment.
   - **South Asia** — matches ResPlan.
   - Note the tension: the best-verifiable standards profile and the
     best-aligned training corpus are **different regions**. Resolve it explicitly
     rather than letting it resolve itself.
2. **Whether the standards profile and the corpus conditioning tag must agree.**
   Can we ship UK standards over a Swiss-Dwellings-trained proposer? The proposer
   only supplies topology and proportion, and the solver enforces the numbers — so
   maybe yes. Argue it; do not assume it.
3. **Which tier is the default** the Homeowner gets when they say nothing.
   `market_default` is the obvious answer and the obvious answer may be wrong,
   because a plan that silently fails `statutory_floor` is worse than one that
   admits it.
4. **What "region" means in the Brief.** A field the Homeowner sets, inferred from
   locale, or fixed for v1? If it is a field, it changes the Brief schema.
5. **What a second region costs later** — is adding one a data file, or a retrain?
   The answer decides whether shipping one region is a narrowing or a trap.

Feeds *Acceptance validator spec*, *Brief schema and parsing contract*, and
*What the model proposes*. Worth resolving before any of them.

## Inherited from *Dimensioning and annotation rules*

**A hard constraint on the profile, and it eliminates real candidate values.**
Every wall thickness a profile declares must be an **even number of
millimetres** — ADR 0001 needs `erode(rect, t_int/2)` in integer millimetres, and
ADR 0004's tier-1 overall needs `t_party/2`. 100 / 120 / 140 / 200 / 240 / 300
pass. **115 mm (half-brick) and 125 mm fail**, and both are real: 125 mm is DIN
4172's octametric module — the same module *Canonical geometry model* noted our
250 mm solve grid courses — and is also a common UK blockwork-plus-plaster
build-up. An odd thickness puts every wall face on a half-millimetre and every
clear dimension off-integer, which breaks the integer-equality property the whole
validator rests on. This does not force a thickness; it forbids a set of them,
and the German case is where it bites.

Three further fields the profile now owns, all discovered by the drawing needing
them:

- **Decimal separator** (`.` UK, `,` DE) — written to the DXF `DIMDSEP` and used
  by every area and dimension string.
- **Room-name abbreviation table** (`WC`, `ST`, `UT`) — the room tag substitutes
  a *published* abbreviation when a name does not fit, never a truncation.
- **Opening catalogue keys** — the type marks on the plan and the rows of the door
  and window schedules cite them, so the keys are user-visible strings rather than
  internal ids.

## Resolution

**One profile ships, its region is `AZ`, and `UK` stays as a test fixture — because
the ticket's central tension assumed the shipped profile and the verification
profile must be the same profile, and they need not be.**

ADR [0006](../../adr/0006-one-shipping-profile-and-it-is-not-the-corpus-region.md).
Measurement: `experiments/corpus-smoke/wall_thickness_swiss.py`.

### The ticket said two regions were in tension. There are four, and no two agree.

| Layer | Region it actually is | Status |
|---|---|---|
| Retrieval — the Proposer that **ships first** | **CH only.** ResPlan is excluded from retrieval (`docs/spec/proposer.md` §4.3) | measured |
| Trained transformer — the fallback path | CH + IN, under `(region, corpus, annotation_provenance)` | designed |
| Standards sources **read first-hand** | **UK only** — all seven in the stub, all OGL | verified |
| Profile the stub declares default | **DE** — with *zero* DE sources | asserted, unsourced |

Three facts nobody had put next to each other:

- **The stub's DE rationale cites the corpus, and the corpus is Swiss.**
  `default_region_rationale` reads *"the primary geometry corpus (Swiss Dwellings)
  is DE/CH"*. CH is SIA, not DIN, and SIA is paywalled. `DE` was a label doing duty
  for Swiss data plus a Neufert posture.
- **Building the DE profile is the one copyright move findings §7.6 forbids.** Every
  DE number is `REPORTED`; §5.6 states plainly that *"DIN 1053 and DIN 4172 were not
  read"*. The only readable source is Neufert, and §7.6 item 7 names *"systematically
  extract one work's tables into a data file"* as the failure mode this project walks
  into by accident.
- **DE's canonical partition is illegal in this engine.** §5.6 gives 115 mm; ADR 0004
  requires every profile thickness even. The octametric series — 115 / 365 / 490 — is
  *systematically* odd. UK's 100 mm stud and ~300 mm cavity both pass. The
  even-millimetre rule is a quiet anti-DIN filter, and nobody had noticed it was one.

### The obvious move — derive the catalogue from the corpus — fails, and that is the ticket's most useful finding

Swiss Dwellings ships **1,519,546 `WALL` separator polygons** in WKT metres under
CC BY 4.0. Measuring them would have replaced an unreadable copyrighted book with a
`VERIFIED` fact, and it is exactly the method *Acquire the datasets* used for the
exposure distribution. Measured over a 200,000-wall sample (minor side of the
minimum rotated rectangle, restricted to genuine straight strips, 199,210 usable):

| | |
|---|---|
| percentiles (mm) | p1 42 · p5 61 · p25 109 · **p50 169** · p75 267 · p95 440 · p99 590 |
| within ±2 mm of a multiple of 10 | **59.1%** — uniform noise gives 50% |
| even millimetres | **59.2%** — uniform gives 50% |
| most common snapped value | 80 mm, at **5.60%** |
| top 20 snapped values, cumulative | **70.5%** |

**There is no module.** Not octametric, not brick, not anything — the distribution is
near-continuous from 50 to 600 mm and the modal value holds under 6%. An 8-entry
catalogue covers 58.5% of real walls at ±10 mm; a 12-entry one reaches 70.9%. These
are surveyed as-built polygons carrying finish layers, and the design intent is
smeared past recovery.

Two consequences, both load-bearing:

1. **The thickness catalogue is `ENGINE_CHOICE`, unavoidably.** `model.thickness_in_catalogue`
   is the *only hard acceptance rule that reads the region profile*, and no corpus and
   no readable standard hands us its contents. The corpus can bound the range it must
   plausibly span, and nothing more.
2. **Corpus thickness never reaches a produced Plan anyway.** Retrieval takes room
   *arrangement*; ADR 0001 re-derives geometry from our own `t_int` over the solve
   domain. So corpus alignment was never an argument for the construction half of the
   profile — which removes the last reason to prefer a European profile.

### The five decisions

**1. Exactly one selectable profile ships, and it is `AZ`.** The decision is a
**construction system**, and country is a poor proxy for it: DE and AZ are both
fired-brick masonry with *different modules*, while UK and US are both frame-and-cavity.
Reasons in full in ADR 0006 — in short, UK's stud-and-cavity build-up exists in neither
corpus nor deployment context; the SNiP-family residential norm is written for
**multi-apartment buildings**, which is the only building type any corpus on this map
contains; its brick (120 / 250 / 380 / 510) and panel (80 / 140 / 160) series are
expected to be entirely even where DIN's are odd; its sources are free; and it is the
actual place a plan would be built. **"Plans ready to use" means usable somewhere
specific.**

`DE` and `US` are **deleted** from the enum, as are the `IN` / `JP` / `AU` / `CN` stubs.

**2. The profile is unpopulated here, on purpose.** Every number is owed by a new
research ticket, *The Azerbaijani region profile*. The even-thickness expectation above
is the **first thing it checks** and is `REPORTED` until it does. Inventing a catalogue
in this session would have produced the 90%-right artefact C2 calls worse than blank —
a wall labelled 200 mm corresponding to no masonry unit anywhere.

**3. `UK` is retained as a test fixture, never selectable.** This is what dissolves item
1's tension. The standards research recommended UK explicitly as *"a testing decision,
not a claim that UK numbers are better"*, and a test fixture is what that sentence
describes. Its seven OGL sources stay in `room-constraints.json`; the suite asserts the
profile **mechanism** — schema, tier resolution, even-thickness rule, decimal separator,
abbreviation fallback — against the one profile that is free, complete and independently
checkable end to end. Verifiability is not lost; it moves off the shipping path.

**4. The standards region and the corpus tag need not agree, and `must_match` is struck.**
Item 2, argued rather than assumed. The stub's `must_match` — *"the region enum MUST be
the same enum as the training-data conditioning variable"* — would, read literally,
**forbid a UK profile forever**, because that enum's members are fixed by corpora we hold
and UK is not one. Its stated justification was that projecting a region-A proposal onto
region-B constraints is "strictly worse than either alone", and that reasoning predates
*Acceptance validator spec* removing every hard dimensional floor from the region layer.
What is left after the projection is printed strings, preferred areas and wall
thicknesses, all of which the solver enforces regardless of what proposed the arrangement.

`RegionProfile` and `CorpusProvenance` become **two fields with two enums**, holding `AZ`
and `CH`, and their disagreement is the normal case. The one thing `must_match` was right
about survives in narrower form: **a Plan carries its profile id for its whole life**,
because a Plan solved under one thickness catalogue fails `model.thickness_in_catalogue`
under another. At inference the model is conditioned on `CH`/`swiss` — the tokens it was
trained with. An `AZ` token that never appeared in training is undefined behaviour, not
localisation.

**5. Tier: `market_default` is the target; `statutory_floor` becomes a `warn` driven by
`force`, not by its own name.** Item 3, mostly pre-settled by *Acceptance validator spec*
— hard floor is the ergonomic minimum, region-free. The residue was disclosure, and the
ticket was right that silence is worse than admission. Two refinements the AZ choice
forces:

- **`statutory_floor` becomes non-null for the first time.** SNiP-family norms prescribe
  minimum room areas; German law prescribes none, which is why the tier has sat unread.
  It now has a real consumer.
- **The disclosure wording derives from the source's `force` field, not from the tier
  name.** The stub already carries `force` per source (`statutory_guidance`,
  `planning_policy_optional`, …). Printing "below statutory minimum" for a plan that
  breaks no law is exactly the legal claim C8 forbids — under UK's NDSS it would be
  wrong more often than right, and under AZ it would be right. Same tier, different
  sentence, chosen by data.

`accessible` stays in the schema unread; it is the one tier with an obvious future
consumer.

### Item 4 — what `region` is in the Brief

A **Brief field with exactly one legal value in v1**, defaulted and surfaced as an
**Assumption** in the same mechanism *Building scope and envelope handling* uses for
dwelling type and notch edges — visible, editable in principle, editable to nothing else
today. Not inferred from locale: the browser's locale is where the Homeowner is sitting,
not where the building goes, and those differ exactly in the diaspora case a
non-commercial project is most likely to meet. Not hidden: ticket 10 needs the field to
exist so that adding the second profile stays the data task item 5 asked about.

### Item 5 — what a second region costs, and the trap inside the question

**Two different costs, orders of magnitude apart, and the product must not let one imply
the other.** A second *standards* profile is ~30 numbers in a data file, no code. A
second *layout* region is a corpus that does not exist — retrieval is Swiss-only and no
obtainable corpus is Azerbaijani, South-Asian retrieval having been ruled out on metric
grounds. So the engine will draw **Swiss-shaped layouts to Azerbaijani conventions,
permanently**.

That is disclosed, not hidden. It is the **third limit** in the family *Building scope and
envelope handling* started, and it is one sentence in the same paragraph: single storey;
house layouts come from apartment priors; **conventions are local, layouts are European**.
Rejected alternative: never naming the region to the Homeowner, so the mismatch cannot be
noticed. It buys nothing — the mismatch is structural and permanent, and this map's
standing pattern is to state limits rather than let a user discover them.

### What this hands the tickets it blocks

- ***Area measurement convention*** — its item 5 asks whether the deductions matter at v1
  scale, and says it needs checking rather than assuming. **Checked: they cannot fire.**
  `CONTEXT.md` and the geometry ticket model **no ceiling height and no balcony**, and
  those two deductions are exactly what make Wohnfläche, GIA and IPMS diverge rather than
  merely differ in name. What remains live is the AZ pair — *общая площадь* against
  *жилая площадь* — which is a genuine distinction and now the only one in scope. Also
  inherits: only one convention needs naming, not one per region.
- ***Opening placement rules*** — inherits the **opening catalogue keys** as
  user-visible strings in the AZ profile, and the fact that they are cited by the door and
  window schedules *Dimensioning and annotation rules* put on their own sheet.
- ***Brief schema and parsing contract*** — inherits the `region` field above, its
  Assumption surfacing, and `CorpusProvenance` as a separate field it does not own.

### Defects fixed in place

- `data/standards/room-constraints.json` — `region_model` rewritten: enum is `AZ`
  (shipping, unpopulated) and `UK` (test fixture); `default_region` is `AZ`;
  `must_match` struck and replaced by the profile-carried-for-life rule;
  `even_thickness_required` recorded, citing ADR 0004.
- `data/acceptance/rules.json` — `win.kitchen_windowless` cites `de_baybo`, **a source key
  that has never existed in the stub**. Flagged by *Acceptance validator spec* as dangling;
  now dangling *and* pointing at a deleted region. Re-sourcing it is the AZ profile
  ticket's, alongside `win.area_ratio`'s fraction.

### Landed in `CONTEXT.md`

**Region profile**, **Corpus provenance**, **Thickness catalogue**.
