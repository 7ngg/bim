---
id: 21
title: The room-count envelope v1 promises
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: [8]
writes:
  - CONTEXT.md
  - docs/adr/0013-the-room-count-promise-is-two-numbers-in-two-units.md (new, on resolution)
  - experiments/room-count-envelope/ (new)
---

# The room-count envelope v1 promises

## Question

**How many rooms does v1 claim to handle, and what happens at the edges of that
claim?**

*Acquire the datasets* measured the corpora and the result reframes a number this
map has treated as settled. Across **63,800 real dwellings** in both committed
corpora, counting the rooms a Brief actually names:

| rooms | 4–10 | ≥12 | ≥14 | ≥16 | ≥20 | ≥24 |
|---|---:|---:|---:|---:|---:|---:|
| dwellings | ~60,600 | 916 | 178 | 66 | 11 | 1 |

The **24-room case that the solver formulation was validated against — and that
every timing on this map quotes — describes exactly one dwelling in 63,800.**
Meanwhile ~95% of the corpus sits between 4 and 10 rooms, and the mean is 6.8.

C5 already commits the product to stating its limits honestly: single storey, and
house layouts from apartment priors. This asks whether there is a **third stated
limit** and where it sits.

**What has to be decided:**

1. **Is 24 rooms a v1 requirement at all**, or an artefact of a stress test that
   became a spec figure? The solver clears it in 6.25 s — at 100% exterior
   exposure, which *Acquire the datasets* showed no real flat has — so the
   capability is real but it may be answering a question nobody asks.
2. **Where the supported band starts and stops.** A floor as well as a ceiling: a
   1-room Brief is 948 dwellings in the corpus and probably not a product.
3. **What the system does past the ceiling.** Refuse, warn, or attempt and let the
   Acceptance bar reject? *Acceptance validator spec* settled that a failing Plan
   is never shown and a zero-survivor case is diagnosed arithmetically — this is
   the same shape of decision one level earlier, at Brief-parse time, and *Brief
   schema and parsing contract* already owns a feasibility pre-check that could
   carry it.
4. **What the product copy says**, in the same breath as the other two limits.

**Why this waits on *What the model proposes, and how it is trained*.** If that
ticket takes retrieval-and-warp, the ceiling is not a choice — it is whatever the
corpus holds, and the numbers above *are* the answer. If it trains with a
synthetic generator, the ceiling becomes a design parameter and this question is
about what to aim the generator at. The route determines whether this is a
statement of fact or a decision.

**What this is not.** Not a re-litigation of C5 or of the solver formulation. The
solver's capability is measured and stands; this is about what v1 *promises*,
which is a different thing from what the engine *can do*.

---

## Resolution

**The gate and the promise are two numbers in two units, and the unit was the
whole problem.** ADR 0013. Gate: hard refusal outside **3–10 engine rooms**.
Promise: **1–4 otaq**. Between them, a zone the engine serves and the copy
declines to claim.

Experiments: `experiments/room-count-envelope/` — `circulation_split.py`,
`coverage_per_n.py`, `named_band.py`, `three_units.py`. All over the 46,800 Swiss
dwellings already on disk; `coverage_per_n.py` reuses
`experiments/retrieval-coverage/out/dwelling_records.json`, so the method is
`collapsed_coverage.py`'s exactly — cross-paired Brief, `{ROOM, BEDROOM, STUDIO}
→ PRIVATE`, ±10 % area / ±15 % aspect.

### 1. C13's "Brief-named" was false, and it is the finding

`brief.md` §3 makes `corridor` and `entrance_lobby` **invented by `resolve`**.
`dataset-inventory.md` §1.3 does not exclude `CORRIDOR`. So every coverage figure
and the 4–10 band itself are measured on a count **no Brief names**:

```
circulation rooms per dwelling (k):  k=0 6.55%   k=1 75.11%   k=2 16.69%   k>=3 1.65%
```

A Homeowner naming 10 rooms is outside the engine band **99.78 %** of the time;
naming 9, **31.93 %**. Stating the band in the Homeowner's units without
converting would have shipped a false claim, and nothing on the map would have
caught it — the number was right, the unit was missing.

### 2. Per-`n` coverage, which the three-band table hid

`proposer.md` §2.1 reports 4–6, 7–10, 11–15. Per room count:

| engine n | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| briefs | 948 | 317 | 1,119 | 2,972 | 6,343 | 8,828 | 8,575 | 8,175 | 5,844 | 2,191 | 774 | 374 |
| pool = 0 | 10.8 % | **42.6 %** | 24.2 % | 17.2 % | 8.3 % | 7.9 % | 9.3 % | 9.1 % | 15.7 % | 28.5 % | **58.0 %** | 76.2 % |
| median pool | 96 | 1 | 9 | 18 | 126 | 155 | 85 | 107 | 40 | 9 | 0 | 0 |

Two things the band table could not show. **n = 2 is the worst regime anywhere
below 11** — worse than n = 10, which the old band included, and worse than
n = 3, which it excluded. And **n = 1 retrieves better than n = 4** (10.8 % vs
17.2 %, median pool 96), so excluding studios was never a coverage argument and
could not have been defended as one.

### 3. The third unit, and it is the one the market speaks

`AZ` ships two `verified` statutory floors that exist **only for the one-room
flat** — `living_room_1room_flat` 15.0 m² and `wardrobe_1room_entry` 2.5 m², both
AzDTN 2.7-2 cl. 5.7. That norm counts **otaq**: habitable rooms, bedrooms and
living rooms only. It is how a Baku flat is advertised and it is a unit this map
did not have a word for.

| otaq | share | median engine | in engine 3–10 | E[retrieval blank] |
|---|---:|---:|---:|---:|
| 1 | 10.62 % | 4 | 78.2 % | 17.7 % |
| 2 | 19.19 % | 5 | 100.0 % | 9.1 % |
| 3 | 37.35 % | 7 | 99.9 % | 9.4 % |
| 4 | 26.06 % | 8 | 98.6 % | 15.0 % |
| 5 | 5.33 % | 10 | 79.1 % | 33.4 % |
| 6 | 0.74 % | 12 | 13.5 % | 67.2 % |

**1 otaq → median 4 engine rooms. 5 otaq → median 10.** Never convert by a
constant: the spread at each otaq is two to three engine rooms wide.

### 4. The five decisions

1. **Unit.** Three units exist, not two. The **gate binds on the engine count**
   post-`resolve` — the only count the solver and retrieval see. The **copy
   speaks otaq**. The named count is internal plumbing, never shown and never
   promised on. Three terms landed in `CONTEXT.md`.
2. **24 rooms: demoted, not deleted.** One dwelling in 63,800, and its 6.25 s
   VALID was measured at 100 % exterior exposure ADR 0003's census says no real
   flat has. It stands as headroom evidence for the formulation; **nothing may
   quote it as the supported ceiling.**
3. **Ceiling: engine 10.** Drawn at the last regime with a measured source. At 11
   retrieval is 58.0 % blank and only source B answers — unmeasured there, and
   `proposer.md` §2.1 says it **fails quietly**, with no serving-time ground
   truth (*Validate the arrangement metric*) to catch it.
4. **Floor: engine 3, not 4** — and this reverses the recommendation this session
   opened with. A floor of 4 makes `living_room_1room_flat` and
   `wardrobe_1room_entry` permanently unreachable: two `verified` numbers
   carrying a legal citation that no Brief could satisfy, which is the dead-data
   defect ADR 0012 deleted `h_storey` for. Floor 3 takes 1 otaq from 57.4 % to
   **78.2 %** in band and corpus coverage from 91.74 % to **94.13 %**. It is
   nearly non-binding by construction — a Brief naming one habitable room, a
   kitchen and a bathroom is already at 3 — and that is the intent: **the floor
   catches a malformed Brief, it does not exclude a market.** Refused below: a
   single Space has nothing to arrange, and n = 2 is the worst retrieval regime
   in range.
5. **Three zones, not two.**

   | zone | rule | share | behaviour |
   |---|---|---:|---|
   | promised | engine 3–10 **and** 1–4 otaq | 89.87 % | runs; copy claims it |
   | served, not promised | engine 3–10, outside 1–4 otaq | 4.26 % | runs, warns |
   | refused | outside engine 3–10 | 5.87 % | hard refusal, naming the count |

   Symmetric refusal was the opening recommendation and is wrong: it conflates
   *where the engine stops working* with *where we stop claiming it works well*.
   The middle zone is mostly 5 otaq, which the engine serves at a 33.4 % blank
   rate — real, and not something to promise.

   Refusal is hard rather than advisory because **`acceptance-bar.md` §11's
   zero-survivor diagnosis is arithmetic over areas and cannot voice a room-count
   failure.** Without an explicit check the Homeowner is handed an area sentence
   that is not the real reason — a wrong explanation, not a missing one.

### 5. Product copy, and what the market does

The third stated limit, beside C5's two:

> **We plan flats and houses of one to four rooms** — one storey, and house
> layouts come from apartment priors.

Checked against the market per CLAUDE.md: **no surveyed product states a
room-count limit at all.** The only published scope limits across the eleven in
`competitive-landscape.md` are building-type (ARCHITEChTURES: multi-family only)
and experimental-feature disclaimers (Autodesk Forma's Building Layout Explorer:
*"we recognize some outputs will be more useful than others"*). Nobody states a
band because nobody refuses. Stating one is the same shape of differentiator as
C3's annotation gap.

### 6. What this hands on

- **`brief.md` §9.4** grows from *two bounds, two severities* to **four bounds,
  three severities** — the two area bounds, plus the hard room-count refusal and
  the unpromised-band warning, in the same function so §11's same-sentence
  guarantee still holds by construction. → *What the engine says when the
  Envelope is bigger than the programme* (sole claimant of that file).
- **`room-constraints.json` needs a `habitable` flag** per ergonomic key so otaq
  is computable from a Brief — same shape as the existing `brief_nameable` flag.
  → *Two room vocabularies in one file*.
- **`resolve` must choose k before the solver runs.** k = 1 is right 75.1 % of
  the time, k = 2 16.7 %. Fixing k = 1 is safe **only if a Room may be more than
  one rectangle** — an L-shaped corridor reaching a wing one rectangle cannot.
  → *Whether a Room may be more than one rectangle*. This dependency had not been
  drawn anywhere.
- **`proposer.md` §3 and C13** both say "Brief-named rooms". C13 is corrected on
  the map by this ticket; §3 belongs to another file's claimants.
- ⚠️ **Everything here is Swiss.** ResPlan's 17,000 dwellings were not measured
  for circulation or otaq, and `proposer.md` §8 already flags that coverage is
  Swiss-only. The otaq convention is Azerbaijani and the corpus is Swiss —
  C14's permanent two-tradition split, showing up in the counting unit now as
  well as in the thicknesses.
