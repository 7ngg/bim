# ADR 0042 — The entry-depth inversion is a fifth term, and its corpus rate is a ceiling

**Status:** accepted. Lands `docs/research/zoning.md` **D10**, which specified this
term and could not write it — raised by *What an ordered entry sequence costs the
solver*, on a file *The Proposal cannot express zoning* wrote without an ADR.
Amends `proposer.md` §6.1 and `zoning.md` D10, §6.7 and §6.8. Amends no ADR, no
threshold and no rule.

## Context

`proposer.md` §6.1 shipped four plan-quality terms, each *"scored against the
corpus distribution, never a threshold"*. `zoning.md` D10 proposed a fifth — the
**entry-depth inversion rate**, the fraction of dwellings whose nearest sleeping
Room sits strictly nearer the entrance than its nearest social Room, real
**17.4 %** — on the ground that the property is real, measured, and invisible to
all four. Term 3 (social transit) is the one that looks like it should cover it
and does not: the two are **negatively** associated, χ² = 34.55, p ≈ 4.2 × 10⁻⁹,
odds ratio 0.354, with **15.2 %** of dwellings inverting the gradient at no
transit defect at all. Transit is a *routing* property; inversion is a *distance*
one.

D10 specified the term ready to transcribe. Taking it surfaced that its scoring
rule, its node sets and its population were each wrong in a different way, and
that one of the three defects is **not this term's** — it is §6.1's.

## Decision

**1. The fifth term is taken.** The property is the only plan-quality property
this map has identified, measured, and left unowned. The benign reading — that a
shallow private Room is a deliberate front-office, which Alexander's Patterns 141
and 157 place at both ends of his own gradient — was tested and **fails**: the
shallow Room in an inversion is a terminal cell in **4.9 %** of cases against
**26.5 %** when ordered. The corpus's inversions are bedrooms off the hall.

**2. Its corpus rate is a CEILING, not a target.** 17.4 % is the "no worse than
real housing" line; lower scores better and 0 % scores best. D10 asked to *match*
the rate while `zoning.md` §6.5 calls the same bucket a **violation**, and those
cannot both stand — matching rewards producing as many bad plans as the housing
stock does.

**3. The social set is `is_habitable ∧ ¬is_sleeping`, and no new flag is added.**
That is the construction `zone.no_social_transit` and `zone.facade_to_living`
already use. Plain `kitchen` stays out, which `measure_zoning.py` already assumed:
`KITCHEN` is its own class there, in neither set.

**4. The term is stratified by habitable-room count and the pooled scalar is never
quoted alone** — 12.3 / 21.9 / 15.0 % at 3 / 4 / 5, pooling 6+.

**5. It ships `src: engine_choice`, `conf: derived`, and its lack of statutory
backing is stated in the spec rather than left to be discovered.**

**6. Term 5's *kind* is settled; terms 1–4's are not, and that is handed on
rather than guessed.** §6.1 conflates two kinds of quantity and this ADR does not
resolve the other four.

## Why the rate is a ceiling — the evidence, since this is the reversal

Nothing in either lineage supports scoring a defect rate against the corpus's own
rate.

- **ЖК РФ art. 50 §2**, reached through СП 54.13330.2022's Table 5.1 note
  (*«с учетом достигнутого уровня обеспеченности населения жилищем»*), is a real
  legal system indexing a threshold to observed stock — but as a **one-sided
  minimum on a quantity where more is better**, which *rises* as practice
  improves. Transplanted onto a defect rate it yields a ceiling, never a target.
- **WBS 2015 moved its bar *against* its own stock.** The 2015 revision added a
  **maximum** net floor area — *"neu nicht mehr nur eine minimale, sondern auch
  eine maximale Nettowohnfläche"* — because Swiss dwelling areas were rising. A
  distribution-matching instrument tracks its stock by construction and could not
  have done this.
- **The corpus's 17.4 % is what a stock produces when its own evaluation system
  never looks.** WBS 2015 scores zoning nowhere: `Zonierung`, `Durchgangszimmer`,
  `Tag/Nacht` and `Intimität` appear **zero** times across it, rooms are
  `nutzungsneutral`, and the entire bedroom-privacy provision is that the room be
  `abschliessbar`. A bedroom off the hall passes WBS completely. Matching that
  rate would import the silence.

`docs/research/housing-quality-standards-as-bars.md`,
`docs/research/plan-quality-metrics-in-practice.md`.

## Consequences

1. **The stratification is not optional.** Pooled, the term is a mixture over the
   corpus's size mix: the tie mass runs **30.8 → 67.3 %** monotone in habitable-room
   count, because a large dwelling is hall-centred and everything sits at equal
   depth. A generated population with a different Brief mix would score as
   deviating while being perfectly zoned. House-GAN++'s precedent — stratify FID,
   never pool it — transfers in shape, though not in statistical comfort: it runs
   on ~80 k dwellings and this runs on 2 500, so the 6+ stratum (n = 98) pools and
   the per-stratum n is published beside every rate.

2. ⚠️ **Four of the five terms are uncomputable today, and this ADR does not fix
   it.** Terms 1, 2, 3 and 5 all read `is_sleeping`.
   `data/standards/room-constraints.json` ships `is_private`, `is_wet` and
   `is_habitable` and no fourth flag. The flag is defined in `CONTEXT.md`,
   specified in `zoning.md` §5b, and depended on by `rules.json`'s own note. It
   has been handed over as prose twice and landed neither time, so it is raised as
   a ticket instead of handed a third time — *Land `is_sleeping` and retire the
   private corpus-label copies*.

3. ⚠️ **`experiments/zoning/measure_zoning.py` is a surviving private copy of the
   corpus-label projection ADR 0037 published.** Its `CLASS` dict names a
   `{ROOM, BEDROOM, STUDIO}` collapse in its comment and maps only `BEDROOM` and
   `ROOM`; it maps neither `OFFICE` (376 rooms, 86 apartments) nor `KITCHEN_DINING`
   (44 / 42). Harmless today only because `STUDIO` does not appear among the
   corpus's `area` entities at all. ADR 0037's sweep did not reach it because
   ticket 69's write scope was `experiments/warp/`.

4. ⚠️ **744 of 2 500 dwellings are outside the term's population, and it is a
   corpus-model mismatch rather than a corpus defect.** They hold no Room the
   conversion labels social, because Swiss practice is `nutzungsneutral` and the
   living room is often simply not designated — 70.1 % of the private set is the
   unlabelled `ROOM`. Their largest private Room runs a median **20.2 m²** against
   **15.3 m²** where a social Room is labelled, and under a kitchen-as-social
   reading they invert at **32.4 %** against **7.3 %**. Widening the social set to
   admit them imports the artefact, and a heuristic relabel is **refused**: it
   would impose a typology the source deliberately withholds. C5.

5. ⚠️ **§6.1 conflates two kinds of quantity and only term 5's is decided here.**
   Term 4 is **fidelity** by §4.5's explicit ruling — *"a landlocked room is not a
   defect in the donor, it is a fact about real housing"* — so matching is correct
   for it and minimising would be wrong. Term 3 is a defect rate. Term 2 is open:
   73.7 % give the longest exterior run to a living room, and the other 26.3 % is
   often a legitimate choice rather than a defect. Term 1 is a genuine
   distribution. *What each §6.1 term is scored for* owns the audit.

6. ⚠️ **A possible degeneracy in term 4, flagged not asserted.** §4.5 says the
   solver posts the frontage budget **hard**. If so, `frontage_reach < 1.0` on a
   generated Plan is 0 % by construction and the term reports constant deviation
   from 5.88 % while measuring nothing. Whether it is computed pre-solve on the
   Proposal or post-solve on the Plan is unconfirmed, and belongs to the §6.1
   audit.

7. **No rule, no threshold and no Proposal field moves.** A term scores a Plan; it
   never rejects one. The ordering constraint stays refused (`zoning.md` §6,
   `solver-formulation.md` Part VI) and this term does not reintroduce it as an
   evaluation term's side effect.
