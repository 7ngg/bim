---
id: 72
title: A regulator states an aspect rule and the engine says none does
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
blocked_by: []
writes:
  - data/acceptance/rules.json
  - data/standards/room-constraints.json
  - docs/research/room-area-bands.md
declared_on_resolution:
  - docs/adr/0048-the-aspect-rule-is-a-gradient-and-the-regulators-2-to-1-is-a-daylight-rule.md
  - docs/spec/acceptance-bar.md
  - docs/research/acceptance-thresholds.md
  - docs/research/room-proportion-standards.md
  - docs/research/room-proportion-constraints.md
  - experiments/acceptance-thresholds/resplan_aspect.py
  - experiments/region-profile/gate_check.py
  - CONTEXT.md
---

# A regulator states an aspect rule and the engine says none does

## Question

**AzDTN 2.7-3 cl. 5.1 closes with a proportion rule, it is in no artefact, and
`dim.aspect_ratio_hard`'s own note asserts that no surveyed source states one.**

> «Yaşayış otağının uzunluğunun eninə nisbətən **2 dəfədən çox olmayaraq** qəbul
> edilməsi **tövsiyə olunur**.»
>
> *"It is **recommended** that a living room's length be adopted as **not more
> than 2 times** its width."*

Read first-hand from the PDF arxkom serves — `az-kitchen-diner-whole-room.md`
§12.2, corroborated independently by `az-market-default-against-practice.md`.

The shipped rule is `dim.aspect_ratio_hard` at **3,0**, `conf: fitted`, Swiss
p99.5, corpus cost 2,85 % (ADR 0023). The **soft** threshold fitted beside it is
**2,2** — close to the norm's 2, and nobody noticed, because the norm's rule was
never in the repo to compare against.

**Two defects, and they are different sizes.**

1. **A false sentence in a shipped note.** The rule asserts no surveyed source
   states an aspect rule. One does. Cheap half; a correction, not a decision.
2. **A region profile has a shape rule and the profile has no field for one.**
   `room-constraints.json` carries areas, widths and heights. Aspect is the one
   dimensional axis a profile cannot express, in an engine whose whole business
   is shape.

**What has to be settled:**

1. **Whether 2:1 enters the profile at all, and at what force.** It is
   `tövsiyə olunur` — **recommended**, not `məcburi` — and it is from the
   **detached-house** norm, so it degrades to `conf: derived` / force
   `recommended` exactly as the six `clear_widths_mm` cells do.
2. **What it would cost.** Unmeasured, and it must be measured before anyone
   touches 3,0. ⚠️ C14 permits a profile to **raise** a hard floor; whether an
   aspect cap is a floor in C14's sense is itself a question this ticket must
   answer rather than assume — the profile has never reached a non-area
   predicate before.
3. **Whether it belongs to the soft side instead.** The fitted soft threshold is
   already 2,2. A regulator recommending 2 against a corpus statistic of 2,2 may
   be evidence the soft term is right, not that the hard one is wrong — and that
   reading costs nothing and claims nothing.

## What this is not

Not a change to `dim.aspect_ratio_hard`'s value on the strength of the norm
alone — ADR 0023 fixes how a threshold is placed and requires a published cost.
Not a re-opening of ADR 0007 or of grid erosion.

## Raised by

*A zone floor is posted on the whole room* (2026-08-30), via both of its research
tickets, which found the clause while reading cl. 5.1 for a different reason.

## Resolution (2026-09-01)

**The 2:1 does not enter, and the reason is not the one this ticket expected: it
is a *daylight* rule and the engine measures *proportion*. What did move is the
engine's own soft term, which was mis-formed rather than mis-valued.** ADR 0048.

The ticket asked *whether 2:1 enters the profile and at what force*. Both halves
of its framing turned out wrong. Item 1's premise — that the norm's rule and
`dim.aspect_ratio_hard` are the same predicate — is false. And item 3's guess —
that a regulator at 2.0 against a fitted 2.2 *"may be evidence the soft term is
right"* — inverts: the soft term is nearly inert on the exact population the norm
scopes to.

### The false sentence is four sentences, and one of them is a rig's reason to exist

*"No surveyed source states an aspect rule"* appears in `rules.json`,
`acceptance-bar.md` §10, `acceptance-thresholds.md` §2 and
`resplan_aspect.py`'s docstring. **All four struck.** Two carried a second stale
claim: §10 also said *"Both `ENGINE_CHOICE`"*, which ADR 0023 made `fitted`.
`resplan_aspect.py` cites the belief as *why that rig exists* — its reason is
restated and it survives, because a second corpus is still what keeps a fitted
threshold off a single population.

### The finding: 2:1 is a daylight rule, and two traditions prove it from opposite sides

- **SNiP II-L.1-62 cl. 1.19 / II-L.1-71\* cl. 3.4** — habitable-room **depth**
  ≤ 6 m **and** ≤ 2× width, **mandatory**; the 1971 revision *added*
  «при одностороннем освещении», **single-sided lighting only**.
- **Portugal, RGEU art. 69.º n.º1 d)** — same 2:1, mandatory law, **waived** where
  openings are in the two most distant opposite walls.

The USSR *restricts* its 2:1 to single-aspect rooms; Portugal *waives* its 2:1 for
dual-aspect rooms. Same ratio, same class, same condition from opposite
directions, no contact between the traditions.

**A 6 × 3 m room glazed on its long wall is 2:1 to this engine and *ideal* to all
three norms.** The predicates are different and 2.0 may not be transferred.
**AzDTN 2.7-3 kept one of the clause's four elements** — dropping the 6 m cap, the
lighting condition and the mandatory force, and degrading *глубина* (depth) to
*uzunluq* (length), which loses the window anchor that is the entire mechanism.
It is the most degraded rendering of the rule in existence. And **AzDTN 2.7-2 —
the apartment norm that governs this product — has no proportion rule at all**,
which the repo's own three prior reads corroborate: every citation is to 2.7-3.

The rule also **died in its own parent tradition**: absent from SNiP 2.08.01-89,
SP 55.13330.2016, SP 31-107-2004 and SP 54.13330.2022, whose cl. 5.11 delegates
room dimensions to «требований **эргономики**» by name — the same delegation
`clear_widths_mm.comment` already records as why every AZ `statutory_floor` is
null *"BY DESIGN, not by omission"*.

### The ticket's structural claim is right, and there is evidence it never had

*"A region profile has a shape rule and the profile has no field for one"* is not
hypothetical. `az-region-profile/minima.md:257` drafted **seven** cells from
AzDTN 2.7-3 cl. 5.1 — six `clear_widths_mm` and
`habitable_room / max_aspect_ratio / 2.0`, *"a proportion rule, and a good soft
objective for the solver"* — all gated behind *"(see note) must be resolved before
these enter the JSON"*. **The six shipped. The seventh did not**, and no artefact
said why, leaving a deliberate-looking omission indistinguishable from the silent
revert that hit `kitchen.needs_window`. **The omission was right; the reason was
never written.** It is written now, as an explicitly-null `max_aspect_ratio` block
carrying its three reasons.

⚠️ **Declined on evidence, not on authority.** C14 would have *permitted* a
profile to tighten a predicate that already binds. The next region with a
mandatory proportion rule may legitimately do it.

### What cost the hard cap its 2:1, in numbers

⚠️ **Derived, not measured** — `data/corpora/` is gitignored and not on disk, so
`census.py` cannot run. The room→dwelling amplification is recovered from
`room-area-bands.md` §5's measured table (`n_eff` 6.32 / 6.37 / 6.41 at three
points) and reproduces the one aspect figure that *was* measured — 3.1 % predicted
against 2.85 % actual.

| aspect cap | rooms above | dwellings rejected |
|---:|---:|---:|
| 3.0 — shipped | 0.50 % | 3.1 % *(measured 2.85 %)* |
| **2.0 — AzDTN** | 8.00 % | **41.0 %** |
| 2.0, habitable-only scope | 6.02 % | **18.3 %** |

Against ADR 0023's ~3 % tolerance, and against §5's own verdict that a 26.63 % cap
is *"unusable"*. ⚠️ Independence is the weak limb; perfect correlation floors the
estimate at **8.0 %**, still 2.7× the tolerance. **The decision holds across the
whole plausible range**, which is why re-acquiring the corpus was not made a
blocker — stated so the next reader does not re-litigate it.

### The soft term was mis-formed, and item 3 inverts

At 2.2 — the p95 — the step fired on **1.5 %** of bedrooms and **9.5 %** of
kitchens. Least on the population an aspect rule is *for*; most on the one AzDTN's
own scope excludes (`yaşayış otağı` is habitable, a kitchen is `yardımçı sahə`).
**Moving the number could not fix it**: at 1.6 (p75) a step is still inert on 75 %.

It was the only **monotone-preference** soft rule in the file encoded as a
**step**. `dim.market_default_area` is `soft_w[type] × |area − target_area|`;
`wet.shared_wall_length` is the same shape. This rule was the odd one out, and
**ADR 0023 decision 5 already contains the argument** — *"a band that holds most
of the population is inert on most of the population, and a soft rule exists to
rank"* — stated for bands, never applied to the one-sided cap the same ADR's §2.1
approved at p95 four sections earlier.

It is now `soft_w[class] × max(0, aspect − target[class])`, `aspect_bands`
mirroring `area_bands`. **`rule_count` stays 43.** Targets are the corpus p50 —
`room*` 1.37, `bathroom` 1.39, `living_dining` 1.37, `kitchen` 1.45 — and
deliberately **not 1.0**, because a galley kitchen at 2.5 is a good kitchen.
Weights 1.00 / 0.94 / 0.83 / 0.82.

⚠️ **`soft_w` is `derived`, not `fitted`.** `area_bands` obeys
`soft_w = min(1, cv_min/cv)` — verified across **all eleven** area classes,
residuals ≤ 0.008, fully explained by 2-dp `cv`. The aspect census publishes no
`cv`, so `p95/p50` stands in. **Ordering is proxy-robust; spacing is not.** Refit
added to `owed`.

### Three external corroborations, and Palladio supplies the form

- **3.0 gains a second, independent defence**: `[1/3, 3]` is the **modal** hard
  aspect bound in VLSI floorplanning — a literature with no contact with housing.
- **Palladio I.XXI is cap-plus-gradient** — *"not to exceed two squares … the
  nearer they come to a square, the more commendable"* — and is the **only**
  source found whose predicate is orientation-free length:breadth, this engine's
  own quantity. The form was chosen before this research landed and it agrees.
- **Neufert and the Metric Handbook state no habitable-room ratio** — Neufert's
  1:1.5 is the **office** chapter, the Metric Handbook's is **broadcast studios**.
  Clean verified negatives, which is why the target is a corpus statistic: C8's
  Neufert-*grade* bar supplies no number here.
- **Michalek et al. (2002)** state this rule's rationale verbatim 24 years early,
  and pair it with min area, min width **and max width** — so ratio was never
  meant to carry this alone.

### Four defects fixed in passing, three of them nobody was looking for

1. **`circ.fraction_soft`'s statement** read *"between 8 and 18 percent"* while
   its value had been `[0.09, 0.15]` since ADR 0023 decision 5 — that decision
   moved the number and left the sentence, so the file stated the band it had just
   been shown was inert. Found while citing decision 5.
2. **`owed` item 5 is narrowed, not discharged.** Its worked example — a
   1850 × 5400 bedroom — is aspect **2.92** and always failed the soft term, so
   *"a missing soft **width** term is what stands between the engine and that
   room"* was never right. The genuine half survives: `market_default` 3000 is
   consumed by no rule, and Michalek corroborates the max-width limb externally.
   **No width rule created — outside this ticket's subject.**
3. **`GATE_FLOOR` lowered 446 → 445, and no gate went missing.** 446 was **never
   satisfiable**: at commit `8e2dd86`, the commit that *set* it, the runner
   already emitted 445, and `gate_check.py` is byte-identical from there to now.
   Verified by re-running against the data of six commits: 445 at every one. The
   ratchet has printed a phantom *"1 gate(s) have gone missing"* on every run
   through **five closures** and nobody looked — a ratchet failing as a false
   positive, which is the mode that gets ignored. Found only because this ticket
   ran the gates to check its own edits.
4. **`acceptance-thresholds.md` §2's heading** claimed the rule had no precedent
   anywhere; its §2.1 approval of the soft term at p95 is withdrawn.

### Verification

`gate_check.py` **445/445 (floor now 445)**, `ergonomic_check.py` **233 pass, 0
fail**, `env_check.py` **28/28**. Both edited JSON files parse. No value in
`room-constraints.json` moved. `build_ergonomic_layer.py` re-authors only
`ergonomic` and `tier_model.validator_binding` and reads the rest through, so the
new `profiles.AZ.rooms.max_aspect_ratio` block survives a regeneration — checked
before writing, because that generator is what silently reverted
`kitchen.needs_window`.

### Handed on

- **Ticket 89, *A daylight rule the engine has only a proxy for*** — the oriented
  rule, computable today because `win.habitable_has_window` already identifies
  each Room's exterior-condition run. Adds a predicate and needs a corpus cost, so
  it could not be taken here.
- **Per-class aspect at `area_bands` granularity** — fog, not a ticket. Five
  classes measured against eleven; the p75 spread is 11 % against 29 % at p95, so
  the split buys little at the body and is worth doing only if the corpus is
  re-acquired for another reason.
- **`soft_w` refit from `cv`** — in `rules.json`'s own `owed`, where a handoff
  cannot be lost.

⚠️ **Two reliability caveats travel with every figure sourced from the research.**
A sub-agent fabricated cited findings for six countries and retracted them; the
most dangerous was a claimed Galician *"P < 2.2 A"* — **2.2 being this engine's
own fitted threshold** — one quoting error from being published as an independent
regulator converging on our p95. **A fabrication that confirms the prior is the
hardest to catch.** Separately, a *"verified negative"* on Belarus was false
because that copy of СНБ 3.02.04-03 **silently omits cl. 4.11** (numbering runs
4.10 → 4.12) — the abridged-document failure this repo already records for SP 54,
recurring. Belarus ТКП 45-3.02-230-2010 is **reported, not read**; Spain, Ireland,
the Netherlands, France, Italy, Switzerland and Ukraine are unresearched.
