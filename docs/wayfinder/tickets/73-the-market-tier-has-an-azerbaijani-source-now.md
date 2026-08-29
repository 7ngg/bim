---
id: 73
title: The market tier has an Azerbaijani source now
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
blocked_by: []
writes:
  - data/standards/room-constraints.json
  - experiments/baku-market-areas/
  - docs/research/az-market-default-against-practice.md
---

# The market tier has an Azerbaijani source now

## Question

**`market_default` is the default tier, it is what the solver targets, every one
of its values is a recommendation transferred from a detached-house norm, and
Azerbaijani built-stock data now exists to check it against.**

MİDA publishes per-room areas. `mida.gov.az` is a React shell, so every earlier
attempt fetched the shell and concluded nothing was there; its bundle calls an
undocumented public JSON endpoint returning the full *eksplikasiya* per apartment
type. **318 distinct Baku plan geometries**, and the room areas sum to
`internal_size` **to the cent** — which pins the plane as **net internal**, what
ADR 0010 measures. `docs/research/az-market-default-against-practice.md`.

**One cell is already known to be wrong, in the direction the Swiss check could
not see.**

| cell | target | MİDA p50 | |
|---|---:|---:|---|
| `kitchen` | 9,0 | 9,06 (n=312) | lands on it |
| `bedroom_double` | 12,0 | 13,20 (n=287) | fine |
| `living_room_2plus` | 16,0 | 17,60 (n=312) | fine |
| **`bathroom_combined`** | **3,8** | **3,51** (n=318) | ⚠️ **above practice — 63,5 % of Baku main bathrooms are smaller** |

`bathroom_combined` was measured against Swiss rooms when it was added, found on
the median to two decimals, and called settled. **Two corpora, opposite
verdicts.** A soft target *above* what the region builds is not a rounding error
— it is the engine reliably preferring a bathroom Baku does not build.

**What has to be settled:**

1. **The whole tier re-read against the 318 plans**, cell by cell, with n and
   provenance per value. Nine area cells and six width cells.
2. **`bathroom_combined` 3,8**, the one known contradiction, which should not
   wait for the rest.
3. **Whether the MİDA harvest is committed.** It sits in gitignored
   `experiments/baku-market-areas/out/`. ⚠️ **The endpoint is undocumented and can
   vanish without notice**, and every measured number on this map is meant to be
   reproducible from pinned inputs — the posture `requirements.lock.txt` is held
   to. C9 puts licence outside the gate for research data. Against: third-party
   data of unstated terms, and `minima.md` §7.1's copyright posture forbids
   reproducing published tables wholesale.
4. **`what_could_not_be_obtained.market_practice` is false today.** It carries a
   pointer saying so; rewriting it properly is this ticket's.
5. **The tier's structural defect, which no re-read fixes by itself**: every
   value is a *recommended minimum* — `az olmamaqla … tövsiyə edilir` — while
   `tier_model` calls the tier *"what is actually built"*. Those are different
   quantities and the file says one while holding the other.
6. ⚠️ **C13's promise has Azerbaijani evidence for the first time.** The 2024
   household survey puts **93,7 %** of Baku occupied dwellings inside the 1–4
   otaq band. C13 was set on Swiss data; this belongs on the Room-count row, and
   ticket 70 deliberately did not write it.

## What this is not

Not a change to any `statutory_floor` — those are AzDTN's and settled three times
over. Not the referent question, which ADR 0034 closed. Not `kitchen_dining`'s or
`living_dining_kitchen`'s targets, which ADR 0034 set at rung 2 and which this
ticket may supersede **only with a room-level Azerbaijani measurement, never with
a proxy** — MİDA's `Mətbəx-studio` (n=5) is already recorded as the corroboration
for 18,8 and must not be promoted to the source.

## Raised by

*A zone floor is posted on the whole room* (2026-08-30), whose Baku market
research overturned the premise that no such source exists.

## Resolution

**The tier is re-fitted to Baku, four cells move, and the one cell the ticket led
with is refused.** [ADR 0035](../../adr/0035-the-market-tier-is-re-fitted-to-baku-and-may-only-move-up.md).

### The finding the ticket did not have, and it is the one that decided this

**No per-cell gap was large and the dwelling was 11 % small.** Rank-matched
against MİDA, five of six cells sat within 10 % of practice — a cell-by-cell
review reads as *"mostly fine, one bathroom to argue about"*, which is how the
ticket was framed. Summed against MİDA's own net internal less its 13,2 %
circulation:

| otaq | Σ targets before | room budget MİDA builds | before | after |
|---|---:|---:|---:|---:|
| 2 | 40,8 | 45,5 | −10 % | **−4 %** |
| 3 | 51,6 | 58,3 | −11 % | **−2 %** |

The mechanism is item 5 of this ticket meeting ADR 0023: every value is a
*recommended minimum* and `dim.market_default_area` is **two-sided**, so a
minimum is being used as a **centre** and the objective actively penalises a room
for reaching the size Baku builds. Item 5 said the tier's definition and its
contents were different quantities; this is that mismatch priced in square metres
of dwelling.

### What moved

| cell | from | to | matched class | n |
|---|---:|---:|---|---:|
| `living_room_2plus` | 16,0 | **17,6** | `Qonaq otağı`, largest per plan | 312 |
| `bedroom_double` | 12,0 | **13,2** | `Yataq otağı`, largest per plan | 287 |
| `bedroom_single` | 9,0 | **11,5** | `Yataq otağı`, smallest, 2+-bed plans | 159 |
| `wc` | *silent* → Swiss 1,85 | **2,1** | `Sanitar qovşağı`, 2nd-largest per plan | 172 |

`bedroom_single` was the widest gap in the tier: only **6,9 %** of MİDA secondary
bedrooms were below 9,0, so the solver's *preferred* single bedroom sat at the
7th percentile of what the cheap end of Baku builds.

`wc` is **new**, and it retires a Swiss fallback: the cell was silent, so
`brief.md` §9.2 rung 2 supplied the Swiss median 1,85 m² — one of the disclosed
`CorpusProvenance` ≠ `RegionProfile` instances. It is `derived` by a rank rule
and the rule is the weak part, stated on the cell: MİDA has **one** sanitary
name, so *"the smaller of two is the WC"* is an inference from rank and size, not
a read.

Each moved cell keeps its AzDTN value under `superseded_by_measurement` — it is
still the regulator's number and a Practitioner will look for it.

### The rule that governs it — item 1's real answer

**The monotone-upward rule: MİDA may raise a `market_default` cell and may never
lower one.** MİDA is the subsidised state fund, so its sample is biased **low**
against Baku as a whole, and that makes the evidence asymmetric:

- MİDA **above** a target → the bias runs **against** the finding. Even the cheap
  end builds bigger. **Strong.**
- MİDA **below** a target → the bias **explains** it. **Weak.**

It is C14's shape applied to a soft target for an entirely different reason —
C14's monotone raise is about legal force, this one is about sample bias.

### Item 2: `bathroom_combined` 3,8 is REFUSED, deliberately

The ticket asked for this one first and it does not move. MİDA p50 3,51, 63,5 %
below target — but that is the direction the bias predicts, so the rule above
makes the evidence weak; three other populations agree with 3,8 and only MİDA
dissents (Swiss p50 3,78 over 68 434 rooms, this profile's own 4,25 m² over
35 821 bath+WC rooms, AzDTN's 3,8); and MİDA's p75 is 3,82, so a quarter of even
the cheap end exceeds it. **A ticket lowering this cell is overturning a decision
taken with the contradiction in hand, not filling a gap.**

⚠️ **And the ticket's own `bathroom` row was a mis-match.** §6.3 matched
`bathroom` 3,2 to the *largest* `Sanitar qovşağı`, which is a **combined** room.
MİDA's eight-name vocabulary has no separate `hamam otağı`, so there is **no MİDA
evidence for a bath-only room at all**. Corrected in the note at both sites.

### Item 3: the harvest is partly committed

`experiments/baku-market-areas/mida_plans_318.json` (172 KB) — the 318 distinct
plan geometries, the unit every statistic is computed over — plus the raw's md5
`6fe6d97ef72882ddb75c293a2a731cd8`, crawl stats and filter counts. The **raw**
5 954-row harvest stays gitignored: committing it would reproduce MİDA's tables
wholesale, which `minima.md` §7.1 forbids. ⚠️ **The cost is stated in the file:
the dedup is not re-auditable if the endpoint dies.** The md5 is the guard — a
re-crawl that differs means the population moved and the cells must be re-read,
not patched.

### Item 4: `what_could_not_be_obtained.market_practice` is narrowed, not deleted

Two facts, not one. The **private/premium** Baku market is still unobtained (14
portals checked; per-room areas exist there only as pixels inside plan images),
and it is where the numbers differ **upward** — so every cell here stays a
*lower*-biased estimate of Baku. What *is* obtained moves to a new positive
`profiles.AZ.market_evidence` block carrying n, plane, segment, the compliance
caution and the cells MİDA could not reach.

### Item 6: C13's 93,7 % is NOT taken here

It is the Room-count row's and this ticket writes none of its artefacts. Raised
as its own ticket rather than smuggled in.

### Circulation was refused a room cell

MİDA's `Dəhliz` p50 9,52 m² is a **whole-apartment** figure — 316 of 318 plans
carry exactly one — and the profile has three circulation types. Posting a whole
on one of three parts is ADR 0034's defect inverted. Handed to `rules.json` as a
dwelling-level comparator instead: **13,2 %** of net internal (p25 11,9 / p75
15,9) against `circ.fraction_hard`'s Swiss-fitted **30 %**, which Baku practice
does not approach.

### Verification

Every figure was recomputed before a constant moved (C11). `mida_room_schedules.py`
re-run and its pooled table reproduced; the **rank-matched** §6.3 table — the one
the decision rests on, which no committed script printed — recomputed by a probe
importing nothing from the harness. **All five rank-matched figures reproduced to
the cent.**

Three statistics the note never published turned out to be load-bearing and are
now in §11.2: the **second sanitary room** (p50 2,06, n=172 — the `wc` value),
**`Qonaq otağı` split by otaq count** (1 otaq **15,34**, *below* target, which is
why `living_room_1room_flat` and `living_room_2plus` needed opposite verdicts and
the pooled figure could not give them), and **circulation as a share** (13,2 %).

- `verify_shipped_cells.py` — **all 4 shipped MİDA cells reproduce from the
  committed schedule**, and it caught a real defect mid-flight: `bedroom_single`
  had been rounded *down* (11,45 → 11,4) while `wc` was rounded *up*. Fixed by
  publishing the rule rather than the value — nearest 0,1 m², enforced at ±0,05.
- `gate_check.py` **238 pass**, `ergonomic_check.py` **233 pass, 0 fail**.

### Writes

- `data/standards/room-constraints.json` — four `market_default` values and
  **all fifteen notes, nine area cells and six width cells**. The false
  *"no Baku market or MİDA space standard could be obtained"* sentence is
  asserted gone from every one of them. ⚠️ **The six width cells were nearly
  missed**: the first assertion covered only the areas, and a repo-wide re-scan
  after the edit found the same sentence live in all six widths. **No width
  moved** — MİDA's schedules carry areas only, so the 318-plan population is
  silent on every width, and that narrower gap is now what those cells state.
  Their `cl. 5.4` → `cl. 5.1` citation repair was **left alone: it is 72's**.
  Plus new `sources.az_mida_2026`, new `profiles.AZ.market_evidence`, narrowed
  `what_could_not_be_obtained.market_practice`.
- `experiments/baku-market-areas/` — `emit_derived_schedule.py`,
  `verify_shipped_cells.py`, committed `mida_plans_318.json`.
- `docs/research/az-market-default-against-practice.md` — new §11, plus pointers
  at the TL;DR, at finding 3 and at §6.3's `bathroom` row.
- `docs/adr/0035-…` — new.
- `CONTEXT.md` — **declared on resolution, unclaimed at the time.** New term
  **Target area**. The glossary used *"preferred area"* three times as though it
  were defined and it was defined nowhere, while the same concept is
  `market_default` in the profile, `soft_objective_target` in `tier_model` and
  `target_area` on the Brief — **one concept, four names, and the glossary's own
  name was the only one with no entry.** The term carries that it is a *band and
  not a floor*, the rung ladder, ADR 0035's *measured practice floored by
  regulator recommendation*, and the monotone-upward rule stated in domain terms
  rather than as a MİDA fact. Four uses relinked.

### Handed on

- **71** — ⚠️ **the sharpest thing this leaves.** `dim.max_area` binds
  `k[type] × target_area`, **hard**, so every cell raised here **loosens a hard
  rule**. C14 authorises a profile to raise a *floor* and is silent on raising a
  *cap*; the monotone-upward rule inherits that silence. The movement is small
  and no Plan that failed now passes for any other reason, but **the lever exists
  and is unowned**, and 71 holds `area_bands` and `k`.
- `brief.md`'s holder — **the Envelope grows for a silent Brief.** §5 rung 1
  sizes at Σ `target_area` × (1 + f), so a 3-otaq brief stating no area now
  derives an Envelope ≈10 % larger. Intended, but it changes what the engine
  emits for an unchanged prompt.
- `rules.json`'s holder — `circ.fraction_hard` has an AZ comparator now: 13,2 %
  against the Swiss-fitted 30 %.
- **New tickets raised**: the gas-hob viability of `living_dining_kitchen` (§6.5,
  owned by nothing until now) and C13's Azerbaijani evidence.

### Not done, deliberately

`data/acceptance/rules.json` is **untouched** — 71 and 72 both claim it and the
`circ.fraction_hard` comparator is handed to them as prose, not written. The
`clear_widths_mm` six-cell `cl. 5.4` → `cl. 5.1` citation repair is **72's**, and
was left alone even though this ticket had the file open: 72 claims it and the
concurrency rule holds. No `statutory_floor` moved.
