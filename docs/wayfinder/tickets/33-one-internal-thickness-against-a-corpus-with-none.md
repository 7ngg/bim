---
id: 33
title: One internal thickness, against a corpus that has no module at all
parent: map
labels: [wayfinder:research]
status: closed
assignee: tng
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

## Findings pointer

Measured and written up in **`docs/research/single-internal-thickness.md`**.
Harness, runnable, in **`experiments/thickness-fidelity/`** (`README.md` there
carries the two things that will bite whoever runs it next).

Nothing in `data/standards/room-constraints.json` was edited — the `writes:`
declaration above is honoured literally. This section is a pointer only; the
`## Resolution` is the parent session's to write.

## Resolution

**One internal thickness is defensible, and 150 mm is nearly optimal. What it
costs is the drawing, not the areas** — and the cost is a different failure from
the one the map was guarding against. Findings:
`docs/research/single-internal-thickness.md`. Harness:
`experiments/thickness-fidelity/` (8 scripts, all runnable; the measurement pass
is ~48 min over 14,063 dwellings).

### The four items

1. **Does a dwelling drawn with one internal thickness read as real? No — and not
   for the expected reason.** 93.0% of real dwellings carry ≥2 internal thickness
   classes at ±10 mm; the modal dwelling has three; only **7.0%** have one.
   Heaviest ÷ lightest is a median **2.00×**, and 77.0% differ by ≥50 mm, which is
   1 mm of paper at 1:50. **76.1% show three weights** — envelope, internal
   bearing, partition. A uniform `t_int` draws two, always. So the plan does not
   read as *generated*; it reads as **drawn by someone who does not distinguish a
   partition from a bearing wall.** That is a competence signal, not a novelty
   signal, and it is the C2 failure. Drawn three ways in `out/compare.png` — as
   surveyed, uniform at the dwelling's own median, uniform at 150 — which
   separates *uniformity* from *thickness*.
2. **Does area drift? Not at 150, and ADR 0010 deleted the drift by accident.**
   Three independent estimators land at **−0.91% / −0.46% / +0.68%** of Σ Space
   area — they straddle zero. At the 120 mm ADR 0010 replaced they were
   **+0.22 / +0.68 / +1.81, all positive**. The drift was real and moving `t_int`
   for an unrelated reason removed it. Per *room* it is not zero — bathrooms
   +5.1%, flagged by the study itself as its least reliable figure.
3. **What a second thickness buys.** The re-pricing is right and re-prices a cost
   that was already nil. But **per-plan selection captures 1% of the available
   gain; 99% lives inside a single dwelling.** So the purchase that buys the
   fidelity is two `t_int` in **one** Plan, which breaks ADR 0001 consequence 5
   and the **hard** rule `model.space_matches_erosion` — neither touched by ADR
   0009. A cheap middle shape exists ("solve at 280, draw at 150") and costs
   **19 of 36 room-axes an extra 250 mm solve cell**, plus a re-derivation of the
   area gate.
4. **Sanity-check the value. It passes, and by a wide margin.** The corpus-optimal
   **single** internal thickness over 411 km of Swiss internal wall is **146 mm**;
   `AZ` ships **150**, reached from AzDTN 2.17-1's half-brick and AzDTN 2.12-4\*'s
   plaster **with no corpus involved**. Misplaced material 38.1% against 38.0% at
   the optimum. Two independent construction traditions, one number, 4 mm apart.
   The three biases *do* compound — bias 1's gradient runs −0.74% in the smallest
   area quintile to −0.03% in the largest, monotone, and the retained pool skews
   small — but each is ~1% and none justifies moving a `verified` number.

### What it contradicts, and one of them is mine from this morning

- **VERIFIED, not contradicted** — the prior's *"no module at all"* reproduces on
  an independent 467,690-wall sample, every cell within ~2 points. C11 satisfied.
- **CORRECTED, and it is ADR 0010's own figure.** *"The partition footprint is
  roughly 4–5% — the width of the 5% gate"* is verified for the corpus (4.8%) and
  for the 120 mm ADR 0010 **replaced** (4.5%), and stale for the **150 it
  shipped**: measured **5.7%**, *wider* than the gate. Fixed in ADR 0010
  consequence 4, `acceptance-bar.md` §8, `rules.json` and the profile's
  `area_convention.quantity`. It strengthens ADR 0010's argument rather than
  weakening it, which is exactly why it needed saying rather than quietly
  benefiting from it.
- **CONTRADICTED** — *"120 sits below the corpus median, near the p25"*, inherited
  from *Which region profiles ship in v1*, quotes the **all-walls** census, which
  mixes in exterior and party walls at 2–3× a partition. **Internal walls only:
  p25 = 100, p50 = 131, p75 = 169.** 150 sits at ≈ **p60**, *above* the internal
  median. Recorded in the profile's `ship_gates.ticket_33_sanity_check`.
- **QUALIFIED** — *"an 8-entry catalogue matches 58.5% of real walls"* is measured
  on all walls. On **internal** walls it is **74.7%**; 12 entries 84.1%; top-20
  snapped 91.5%. The conclusion survives; the evidence was understated by 16
  points on the population it is used to talk about.
- **SUPERSEDED** — *"a second `t_int` needs N copies of every dimensional
  minimum"*, in `az-region-profile.md` §2 and in the shipped ship-gate note, is
  **false by count**: `profiles.AZ` publishes **zero** linear minima. The
  single-`t_int` conclusion holds on a different argument — ADR 0001, not ADR
  0007. Ship-gate note corrected.
- **NARROWED** — ADR 0009 cheapens the *per-Plan* purchase, whose cost was already
  zero. It does not touch the one that buys the fidelity.

### A free gift to a re-owed item

**ADR 0010's 120 → 150 move cost the solver nothing** — 253 solve cells either
way, not one room-axis changed its ceiling. That is *partial* evidence toward
ticket 19's re-owed room-count deletion analysis: the per-room ceiling is unmoved.
It does **not** settle it, because the deletion also turns on the Envelope's own
re-snapping, which this arithmetic does not touch. A starting point, not a
conclusion.

### The finding that answers a question I handed elsewhere

**Swiss Dwellings records exactly one plane and no finish layer.** Space polygons
sit on the wall body's own faces to within 1 mm a side; `gap − t_mrr` has a mode
at exactly 2.0 mm. So *Look at the converted corpus* was handed the wrong
question: the corpus is not structural *or* finished — **the distinction does not
exist in the file.** That ticket's item is rewritten accordingly.

### What was surfaced rather than resolved

Item 1's measurement is a **fact**; what to do about it is a **decision**, and it
is not this ticket's. New ticket: *One wall weight where a real plan draws three*,
with the three shapes priced — accept and say so; solve thick and draw thin; two
`t_int` in one Plan.

### What could not be obtained

Any Azerbaijani dwelling geometry — **none exists**, so every figure here is Swiss
and inherits C14's standing disagreement · a third corpus (`rplan/`, `msd/`,
`procthor/` are empty directories) · a per-wall thickness in ResPlan (one scalar
per plan, 17,000 of 17,000 — it *assumes* uniformity and so cannot corroborate) ·
a load-bearing flag, so the ≥200 mm bearing proxy is `engine_choice` · solve
**time** at a second thickness, since `experiments/solver-toy/` belongs to other
tickets, so shape B's cost is stated in solve cells rather than seconds · a
Practitioner's judgement of a uniform plan, because **nobody has been shown one**
· **the sign of the drift at 150** — three estimators straddle zero, magnitude
bounded under 1%, direction unresolved · the magnitude of the bathroom per-room
drift, whose ordering is robust and whose number is not.
