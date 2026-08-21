---
id: 33
title: One internal thickness, against a corpus that has no module at all
parent: map
labels: [wayfinder:research]
status: open
assignee:
blocked_by: []
writes:
  - docs/research/ (new findings doc) — read-only on the profile
---

# One internal thickness, against a corpus that has no module at all

## Question

Graduated from the map's fog patch *Whether a discrete thickness catalogue
reproduces real dwelling geometry*, which said it would sharpen "once *The
Azerbaijani region profile* names actual values to test". It named them, and the
question sharpened much further than expected — because the profile does not ship
a catalogue of eight values. **It ships one.**

**`t_int = 120 mm`, everywhere, in every dwelling the engine draws.**

Set against what *Which region profiles ship in v1* measured over 199,210 Swiss
Dwellings `WALL` separators:

| | |
|---|---|
| real internal walls | **no module at all** — 59.1% within ±2 mm of a multiple of 10 against 50% for uniform noise; modal snapped value holds 5.60% |
| distribution | near-continuous **50–600 mm**; p25 **109**, p50 **169**, p75 **267**, p95 **440** |
| an 8-entry catalogue | matches 58.5% of real walls at ±10 mm; a 12-entry one, 70.9% |
| what v1 ships | **one value, 120 mm** — below the corpus median, near the p25 |

The single-thickness decision was **forced arithmetic, not preference**: at a
250 mm grid no two plausible AZ thicknesses share a residue class mod 250, so a
second `t_int` needs a second copy of every dimensional minimum. It is defensible.
What nobody has measured is what it *costs the drawing*.

## What has to be measured

1. **Does a dwelling drawn with one internal thickness read as real?** Not "does
   120 mm match a real wall" — the corpus has no module, so nothing matches. The
   question is whether the *dwelling* does: whether a plan where every partition is
   identical reads as generated before a number is checked. That is the same
   failure mode *Dimensioning and annotation rules* added the aspect-ratio rule
   for, and it is the one C2 calls worse than blank.
2. **Does area drift systematically?** ADR 0001 re-derives every clear rect as
   `erode(solved, t_int/2)`. A `t_int` at the corpus p25 makes our rooms
   systematically *larger* than the same solved rect would give at the corpus
   median. Measure the drift against the converted corpus, per room and per
   dwelling, and say whether it biases the areas the Homeowner is shown.
3. **What a second thickness would actually buy**, priced against what it costs.
   The profile has `t_int_bearing = 250` **verified** and sitting unused, and real
   dwellings plainly mix a partition with a heavier internal wall. The cost is
   known: per-thickness minima in the region profile, plus a Plan carrying its
   construction type for life, extending `profile_carried_for_life`. **ADR 0009
   makes this markedly cheaper than it looked** — it exempts the ergonomic layer
   from ADR 0007's congruence rule entirely, so a second `t_int` no longer
   duplicates the *hard* minima, only whatever linear values a profile publishes
   itself, **which for AZ is currently none**. Re-price it on that basis. Note also
   that ADR 0009 held the grid at 250 mm, so that variable is fixed for v1.
4. **Sanity-check the shipped value.** 120 mm sits at the corpus p25 while
   *Rectangularising real rooms* found the corpus skews small anyway (median
   dropped dwelling 8 rooms / 89.9 m² against 6 rooms / 71.7 m²). Check the two
   biases do not compound.

## What this is not

**Not a re-derivation of the catalogue from the corpus.** That was measured and
came back negative — there is no module in Swiss Dwellings, the catalogue is
`ENGINE_CHOICE` unavoidably, and corpus thickness never reaches a produced Plan
because ADR 0001 re-derives geometry from our own `t_int`. The corpus is the
**sanity check**, not the source.

**Not *Fit the ENGINE_CHOICE acceptance thresholds to the corpora***, which fits
acceptance thresholds. This is about whether the geometry itself is plausible.

**Not the region choice.** `AZ` is settled and does not depend on this.

## Inherited from *Area measurement convention* — the number you are investigating moved

ADR 0010 changed what `t_int` **means** before this ticket got to say what it
should **be**. It is now a **layer set total**: `t_int` = 150 = `t_int_structural`
120 (half-brick, `verified`) + 2 × `t_finish` 15 (`engine_choice`).

Three things follow for this ticket:

1. **The corpus question is unchanged and is still the point.** Swiss Dwellings'
   near-continuous 50–600 mm distribution has no module, and that finding does not
   care which plane our own thickness is measured to. Do not re-open it.
2. **But the comparison does.** If corpus wall thicknesses are **structural** and
   ours is now a **total**, then every corpus-versus-profile comparison this ticket
   makes is off by 2 × `t_finish`. Which of the two the corpus records is
   **unknown** and is exactly the check *Look at the converted corpus* has just
   been handed. Coordinate rather than duplicating it: the arithmetic is the same
   — a wall's recorded thickness against the gap between the two space polygons it
   separates.
3. **The single-`t_int` argument is unaffected.** It rests on residue classes mod
   250 over 19 sourced candidates, and adding a uniform finish to all of them
   translates the whole set without changing which pairs share a class. The
   residue itself moved 130 → 100; the *conclusion* did not.

The finish constant itself is **not** this ticket's to settle — *What an
Azerbaijani finish layer actually is* owns it, and it is a sibling, not a blocker.
