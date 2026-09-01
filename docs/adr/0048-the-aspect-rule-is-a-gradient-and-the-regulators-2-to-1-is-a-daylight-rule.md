# ADR 0048 — The aspect rule is a gradient, and the regulator's 2:1 is a daylight rule the engine does not have

- **Status**: accepted
- **Date**: 2026-09-01
- **Ticket**: [A regulator states an aspect rule and the engine says none does](../wayfinder/tickets/72-a-regulator-states-an-aspect-rule-and-the-engine-says-none-does.md)
- **Amends**: **ADR 0023** — decision 5's principle is extended from soft *bands*
  to soft *one-sided caps*, and that ADR's own §2.1 approval of
  `dim.aspect_ratio_soft` at p95 is withdrawn. `dim.aspect_ratio_hard` is
  **unmoved** and its ADR 0023 fit stands.
- **Supersedes nothing**

## Context

`rules.json` `dim.aspect_ratio_hard` opened with *"No surveyed source states an
aspect rule."* A surveyed source states one: AzDTN 2.7-3 cl. 5.1 closes
«Yaşayış otağının uzunluğunun eninə nisbətən **2 dəfədən çox olmayaraq** qəbul
edilməsi tövsiyə olunur» — a habitable room's length recommended at not more than
twice its width. Two independent first-hand reads in this repo found it and
neither could take it.

The claim was false in **four** places, not one: `rules.json`'s note,
`acceptance-bar.md` §10, `acceptance-thresholds.md` §2, and
`resplan_aspect.py`'s docstring — the last of which cites the belief as the
*reason that rig exists*.

The ticket posed the question as *whether 2:1 enters the profile, and at what
force*. Three findings moved it somewhere else.

**The profile's own record shows the cell was already drafted and lost.**
`az-region-profile/minima.md:257` drafted **seven** cells from AzDTN 2.7-3 cl.
5.1: six `clear_widths_mm` values and `habitable_room / max_aspect_ratio / 2.0`,
all gated behind *"(see note) must be resolved before these enter the JSON"*. The
six shipped. The seventh did not, because `room-constraints.json` had no field
for a shape rule — and **no artefact recorded that**, leaving a deliberate-looking
omission indistinguishable from the silent revert that hit
`ergonomic.rooms.kitchen.needs_window`.

**The regulator's rule is not this engine's predicate.** Verified first-hand:
SNiP II-L.1-62 cl. 1.19 and SNiP II-L.1-71\* cl. 3.4 post habitable-room **depth**
≤ 6 m **and** ≤ 2× width, **mandatory**, and the 1971 revision *added*
«при одностороннем освещении» — **single-sided lighting only**. Portugal's RGEU
art. 69.º n.º1 d) posts the same 2:1 as mandatory law and **waives** it where
openings are made in the two most distant opposite walls. The USSR *restricts* its
2:1 to single-aspect rooms; Portugal *waives* its 2:1 for dual-aspect rooms — same
ratio, same room class, same condition from opposite directions, two traditions
with no contact. **It is a daylight rule.**

`dim.aspect_ratio_hard` measures **orientation-free bbox aspect**, so a 6 × 3 m
room with its window on the long wall is 2:1 here and *ideal* to all three norms.

**And the shipped soft term was mis-formed.** At 2.2 — the p95 — it fired on
**1.5 %** of bedrooms and **9.5 %** of kitchens: least on the population an aspect
rule is *for*, most on the one AzDTN's own scope excludes (`yaşayış otağı` is
habitable; a kitchen is `yardımçı sahə`).

## Decision

**1. `dim.aspect_ratio_hard` is unmoved at 3.0, and gains a second defence.**
`[1/3, 3]` is the **modal** hard aspect bound in VLSI floorplanning (PeF,
Per-RMAP, Intel PARSAC) — a literature with no contact with housing. The value
rested on one Swiss percentile; it now rests on two unconnected fields.

**2. A 2:1 hard cap is refused on measurement.** Derived from published
percentiles: **41.0 %** of real dwellings, **18.3 %** even at the norm's own
habitable-only scope, against ADR 0023 decision 3's ~3 % tolerance and against
`room-area-bands.md` §5's verdict that a 26.63 % cap is *"unusable"*. ⚠️ Derived,
not measured — `data/corpora/` is not on disk. The independence model is
calibrated on three measured points and reproduces the one aspect figure that was
measured (3.1 % predicted, 2.85 % actual); perfect correlation floors the estimate
at **8.0 %**, still 2.7× the tolerance. The decision holds across the whole range.

**3. `dim.aspect_ratio_soft` becomes a gradient and its threshold is retired.**
`soft_w[class] × max(0, aspect − target[class])` — `dim.market_default_area`'s
exact form. Targets are the corpus p50 (1.37–1.45, `fitted`); weights are
`derived`, `room*` 1.00 / `bathroom` 0.94 / `living_dining` 0.83 / `kitchen` 0.82.
Parameters live in `rules.json` `aspect_bands`, mirroring `area_bands`.
**`rule_count` stays 43** — nothing is added.

Three things make this the form rather than a preference. ADR 0023 decision 5
already says *"a band that holds most of the population is inert on most of the
population, and a soft rule exists to rank"* — stated for bands, and never applied
to the one-sided cap the same ADR approved at p95 four sections earlier. Moving
the number could not fix it: at 1.6 (p75) a step is still inert on 75 %. And
**Palladio I.XXI is cap-plus-gradient** — *"I use not to exceed two squares … the
nearer they come to a square, the more commendable"* — the only source found whose
predicate is orientation-free length:breadth, this engine's own quantity.

**4. The target is the corpus p50 and deliberately not 1.0.** Neufert and the
Metric Handbook state **no** habitable-room ratio — Neufert's 1:1.5 is the
**office** chapter, the Metric Handbook's is **broadcast studios** — so C8's
Neufert-*grade* bar supplies no design-grade number here. A square room is not the
ideal for every class either: a galley kitchen at 2.5 is a good kitchen because
worktop runs are linear.

**5. `profiles.AZ` takes no aspect cell, and the decline is written down.**
`max_aspect_ratio` is added as an explicitly-null block carrying its three
reasons, in the pattern `clear_widths_mm.comment` already uses. The reasons are:
AzDTN **2.7-2**, the apartment norm that governs this product, carries no
proportion rule at all; the rule **died in its own parent tradition** (absent from
SP 54.13330.2022, whose cl. 5.11 delegates room dimensions to «требований
**эргономики**» — the same delegation this profile already honours); and AzDTN
2.7-3 kept **one of the original clause's four elements**, dropping the 6 m cap,
the lighting condition and the mandatory force, and degrading *глубина* (depth) to
*uzunluq* (length), which loses the window anchor that is the whole mechanism.

⚠️ **Declined on evidence, not on authority.** C14 would have *permitted* a
profile to tighten a predicate that already binds. The next region with a
mandatory proportion rule may legitimately do it.

**6. The oriented rule is ticketed, not adopted.** Depth from the glazed segment
≤ 6 m and ≤ 2× width, single-sided only. It is **computable today** —
`win.habitable_has_window` already identifies each `needs_window` Room's
exterior-condition run. It adds a predicate and needs a corpus cost, so it could
not be taken here.

## Consequences

1. **The four false sites are struck**, and two of them carried a second stale
   claim: `acceptance-bar.md` §10 also said *"Both `ENGINE_CHOICE`"*, which ADR
   0023 had already made `fitted`.
2. **`soft_w` is `derived`, not `fitted`, and the refit is `owed`.** `area_bands`
   obeys `soft_w = min(1, cv_min / cv)` — verified across all eleven area classes,
   residuals ≤ 0.008 — but the aspect census publishes percentiles and no `cv`, so
   `p95/p50` stands in as the dispersion proxy. **Ordering is proxy-robust;
   spacing is not.**
3. ⚠️ **Five classes, not eleven.** Unmatched `area_bands` classes take the pooled
   figures. Left as fog: the p75 spread across measured classes is 11 % against
   29 % at p95, so the split buys little at the body of the distribution.
4. **`circ.fraction_soft`'s statement was repaired in passing** — it read *"between
   8 and 18 percent"* while its value had been `[0.09, 0.15]` since ADR 0023
   decision 5. That decision moved the number and left the sentence, so the file
   stated the band it had just been shown was inert.
5. **`rules.json` `owed` item 5 is narrowed, not discharged.** Its worked example
   — a 1850 × 5400 bedroom — is aspect 2.92 and *always failed the soft term*, so
   the claim that a missing soft **width** term is what stands between the engine
   and that room was never right. What survives is genuine: `market_default` 3000
   is consumed by no rule, and Michalek et al. (2002) pair a ratio group with min
   area, min width **and max width**, so the width limb is externally corroborated
   and still unbuilt.
6. **`GATE_FLOOR` was lowered 446 → 445 and no gate went missing.** 446 was never
   satisfiable: at the commit that *set* it the runner already emitted 445, and
   `gate_check.py` is byte-identical from there to now. The ratchet has printed a
   phantom failure on every run through five closures. Found while checking this
   ticket's own edits did not break a gate — which is the ratchet working, one
   level up from where it was failing.
7. ⚠️ **Carry the research's reliability caveats.** A sub-agent fabricated cited
   findings for six countries; the most dangerous was a claimed Galician
   *"P < 2.2 A"* — **2.2 being this engine's own fitted threshold** — one quoting
   error from publication as an independent regulator converging on our p95. A
   fabrication that confirms the prior is the hardest to catch. Separately a
   "verified negative" on Belarus was false because that copy of СНБ 3.02.04-03
   **silently omits cl. 4.11** (numbering 4.10 → 4.12), the abridged-document
   failure this repo already records for SP 54. Belarus ТКП 45-3.02-230-2010 is
   **reported, not read**; Spain, Ireland, the Netherlands, France, Italy,
   Switzerland and Ukraine are unresearched.
