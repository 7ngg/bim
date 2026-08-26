# ADR 0023 — A measured threshold is not an engine choice

Status: **accepted** · 2026-08-26 ·
[Fit the ENGINE_CHOICE acceptance thresholds to the corpora](../wayfinder/tickets/20-fit-engine-choice-thresholds-to-the-corpora.md)

## Context

The acceptance bar shipped eighteen rules carrying numbers no source dictates.
`rules.json` marks every one `conf: engine_choice`, whose stated meaning is *"no
source dictates this; the engine picks it, and `note` says why."* That was honest
when the numbers were guesses. It stops being honest the moment one of them is
fitted to 42,985 real dwellings, because the vocabulary has no way to say so:
`verified` means read from a primary document, `derived` means computed from a
verified value by a stated rule, and a corpus percentile is neither.

The consequence is not cosmetic. The map's done-test tracks *"19 of 40 thresholds
are `ENGINE_CHOICE`"* as the widest gap on the map. Under the shipped vocabulary
that count cannot move however much measurement is done, because a measured
number and an invented one carry the same mark. The gap would be closed in fact
and open on the map forever.

A second question had to be settled with it, and it is the one that decides the
values: **which population is a threshold read off, and what is a threshold
allowed to cost?** *What a room's area is allowed to be* had already answered the
second by example — it refused a p95 cap that rejected 26.6 % of real dwellings
and chose p99.5 at 3.1 % — but the reasoning lived in that ticket's prose and
bound nothing.

## Decision

**1. `fitted` is a fourth `conf` value.** *No source dictates this; its value is a
named statistic of a named corpus, and `src` says which.* It sits between
`derived` and `engine_choice`: weaker than a document, stronger than a judgement.
`src` carries the statistic, not just the corpus — `swiss_dwellings_p99_5`, the
form `room-area-bands.md` §6.5 already uses.

`engine_choice` keeps its meaning and its remaining nine rules. It now means
*unmeasured*, which is what the map should be counting.

**2. A threshold is read off the population the rule binds, in that population's
own plane, and both are declared per value.** For the acceptance bar that is real
rooms, which means the raw clear polygons — not the converted tiling, whose
rectangles are a fitting artefact of representing one real polygon as two boxes.
Where the two disagree, the disagreement is a cost on the artefact, not a
correction to the threshold.

**3. A hard threshold is placed at the percentile whose cost matches the standing
tolerance, and the cost is published with the value.** The tolerance is
**~3 % of real dwellings rejected**, set by *What a room's area is allowed to be*
and now applied twice more:

| rule | percentile | cost |
|---|---|---:|
| `dim.max_area` | p99.5 | 3.1 % |
| `dim.aspect_ratio_hard` | p99.5 | 2.85 % |
| `area.invented_envelope_soft` | grid p97 | 2.85 % |

A rule may sit tighter than the tolerance — `circ.fraction_hard` costs 0.69 % and
`open.fits_segment` 0.92 % — because a rule whose job is to catch the visibly
broken should not be spending the budget. A rule may not sit looser without
saying what it buys.

**4. Two thresholds move, and both move because the corpus refutes a sentence in
their own note.**

- **`wet.plumbing_group_count` 2 → 3.** Its note claims *"Two is the shape real
  dwellings take."* Two is the mode at 46.49 %, and the tail reaches three at
  **14.14 %**. The ticket said in advance that if the tail reached three the bound
  was wrong. It does, and it was. Three costs 0.20 %.
- **`area.invented_envelope_soft` 2 % → 3 %.** The 250 mm grid alone moves
  Σ Space area by more than 2 % in **13.71 %** of dwellings. A soft preference the
  engine cannot meet for reasons unconnected to design is a constant in the
  objective, not a gradient.

**5. A soft band is fitted to the interquartile range, not to coverage.**
`circ.fraction_soft` moves from `[0.08, 0.18]`, which holds 71.31 % of real
dwellings, to `[0.09, 0.15]`, the corpus p25–p75. A band that holds most of the
population is inert on most of the population, and a soft rule exists to rank.

## Consequences

1. **`rules.json` goes from eighteen unsourced numbers to nine.** The nine that
   remain `engine_choice` are the ones with nothing to measure: four
   `model.*` integrity rules, `circ.dependent_room_host`, `entry.exists`,
   `entry.single_primary`, `dim.market_default_area` and `wet.shared_wall_length`
   — every one of them a predicate about shape or program rather than a
   magnitude. **The remaining gap is not a measurement gap.**

2. **The map's headline count must be re-read.** It says nineteen; the file said
   eighteen before this ADR, because *H8 and the single-aspect flat* retired two
   rules after the count was written. Nine after.

3. **`data/standards/room-constraints.json` needs the same fourth value.**
   `ergonomic.corpus_label_split.threshold_m2` is fitted over 66,386 rooms and
   marked `engine_choice` today; `AZ.openings.min_pier_mm` is about to become
   fitted. That file has a claimant and this ADR does not write it.

4. **Seven guesses were right and that is now assertable.** `dim.aspect_ratio_hard`
   is the p99.5 to two decimal places (3.02), `circ.fraction_hard` sits between p99
   and p99.5, `open.fits_segment`'s 100 mm is below the p1 of real slack,
   `efficiency` was 0.9 % high and the default Envelope aspect 1.9 % low. A guess
   that survives measurement is worth more than a guess that was never tested, and
   the vocabulary now records the difference.

5. **The bar's real cost is elsewhere, and this ADR barely moves it.** The hard
   registry rejects **84.41 %** of real Swiss dwellings as shipped and **82.31 %**
   under these values — the 2.1 points are `wet.plumbing_group_count` and nothing
   else. Eleven of its thirteen hard rules cost less than a third of a point
   between them. The two that carry it — `open.fits_segment` and
   `win.habitable_has_window` — are a fit test whose number is right and a
   `verified` topology rule with no number at all, so **loosening a threshold
   cannot move it.** Read `open.fits_segment` on real piers rather than on
   full-width openings and the union is **61.23 %**; that spread is a modelling
   question about cased openings, not an uncertainty about any threshold.

6. **One constant, two documents, and both readings of it hold.**
   `open.fits_segment` tests the run's *length*; the return itself is fixed by
   `openings.md` §3.2, at the same 100 mm. The split is deliberate — Openings are
   placed after the solve, so a placement is not a postable predicate — and the
   corpus vindicates both halves: 100 mm is below the p1 of the slack real
   construction leaves on a real run, and it sits at roughly the **p40** of real
   door returns, so an engine door is never tighter to its corner than a median
   real one. What does cost something is the composite `w + 400` that §3.2 needs
   whichever end the door is pushed to: **12.32 %** of real doors sit on a run
   shorter than that, and that number belongs to the nib and the solver
   reservation, not to a threshold.

Measurement: `docs/research/acceptance-thresholds.md`.
Harness: `experiments/acceptance-thresholds/`.
