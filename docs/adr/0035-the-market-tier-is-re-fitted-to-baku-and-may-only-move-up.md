# ADR 0035 — The market tier is re-fitted to Baku, and measurement may only move it up

Status: **accepted** · 2026-08-30 ·
[The market tier has an Azerbaijani source now](../wayfinder/tickets/73-the-market-tier-has-an-azerbaijani-source-now.md)

## Context

`tier_model` defines `market_default` as *"what is actually built and what a
Homeowner expects"*. It is `default_tier`, it is `soft_objective_target`, and
`brief.md` §9.2 sizes every silent Room to it. It is the number the engine aims
at.

Every one of its nine cells was `az_azdtn_2_7_3`, `ref: cl. 5.1` — one clause of
a **detached-house** norm, in the register *«az olmamaqla … tövsiyə edilir»*: a
**recommended minimum**. Nine for nine on the number, zero for nine on what kind
of number it is. The tier's definition and its contents were different
quantities, and all nine notes closed with the same sentence — *"no Baku market
or MİDA space standard could be obtained"*.

**That sentence became false.** MİDA's React shell hides an undocumented public
JSON endpoint returning the full *eksplikasiya* per apartment type: **318
distinct Baku plan geometries**, room areas summing to each apartment's own
`internal_size` to the cent, which pins the plane as net internal — what ADR 0010
measures. `docs/research/az-market-default-against-practice.md`.

### The defect is at dwelling level, and per-cell inspection hides it

Rank-matched against MİDA, no cell is badly wrong — five of six sit within 10 %.
The tier looked far better against Baku than the Swiss comparison had made it
look, because it is an Azerbaijani number finally being asked an Azerbaijani
question.

**The sum is where it fails.** ADR 0023 made `dim.market_default_area`
**two-sided** — `soft_w[type] × |area − target|` — so a recommended *minimum* is
being used as a *centre*, and the objective actively penalises a room for
reaching the size Baku builds. Summed over a dwelling, against MİDA's own net
internal excluding balconies less its 13,2 % circulation:

| otaq | Σ tier targets, before | room budget MİDA builds | gap |
|---|---:|---:|---:|
| 2 | 40,8 | 45,5 | **−10 %** |
| 3 | 51,6 | 58,3 | **−11 %** |

Six cells each within 10 %, and a dwelling 11 % small. That is what a per-cell
review cannot see and is the whole reason this is an ADR rather than four edits.

### The sample is biased, and the bias has a direction

MİDA is the **state housing fund** — subsidised *güzəştli mənzil* at
administered prices, the regulated-affordable end of Baku. It is not Port Baku
or Sea Breeze, and §6.6 of the findings states that where the private market
differs it differs **upward**. Two further cautions travel with it: it is design
intent rather than compliance (84,0 % of its own kitchens meet AzDTN's mandatory
8,0 m²; one in six does not), and its vocabulary is **eight room names**, so it
is simply silent on several profile cells.

## Decision

**1. `market_default` is re-fitted to measured Baku practice where MİDA reaches
it, and the AzDTN recommendation is retained on the cell as the value it
superseded.**

| cell | from | to | matched class | n |
|---|---:|---:|---|---:|
| `living_room_2plus` | 16,0 | **17,6** | `Qonaq otağı`, largest per plan | 312 |
| `bedroom_double` | 12,0 | **13,2** | `Yataq otağı`, largest per plan | 287 |
| `bedroom_single` | 9,0 | **11,5** | `Yataq otağı`, smallest, 2+-bed plans | 159 |
| `wc` | *silent* | **2,1** | `Sanitar qovşağı`, 2nd-largest per plan | 172 |

`bedroom_single` is the widest gap in the tier: only **6,9 %** of MİDA secondary
bedrooms were below the old 9,0, so the solver's *preferred* single bedroom sat
at the 7th percentile of what the cheap end of Baku builds.

`wc` was silent, so `brief.md` §9.2 rung 2 supplied the **Swiss** median 1,85 m².
An Azerbaijani inference beats a Swiss measurement for the region this profile is
for — and it retires one of the disclosed `CorpusProvenance` ≠ `RegionProfile`
instances.

**2. The monotone-upward rule.** *MİDA may raise a `market_default` cell and may
never lower one.*

The bias makes the evidence asymmetric, and this is the load-bearing reasoning of
the ADR:

- MİDA **above** a target → the bias runs **against** the finding. Even the cheap
  end builds bigger. **Strong** evidence the target is low.
- MİDA **below** a target → the bias **explains** the finding. **Weak** evidence
  the target is high.

It is C14's shape applied to a soft target, for an entirely different reason:
C14's monotone raise is about legal force, this one is about sample bias.

**3. `bathroom_combined` stays at 3,8 — the one measured contradiction, refused
deliberately.** MİDA's largest sanitary room has p50 **3,51**, so **63,5 %** of
Baku state-fund main bathrooms are smaller than the engine's target. The Swiss
check had put this cell exactly on the median and called it settled; two corpora,
opposite verdicts. Held for three reasons in order: the monotone-upward rule
makes the evidence weak; three other populations agree with 3,8 and only MİDA
dissents (Swiss p50 3,78 over 68 434 rooms, this profile's own 4,25 m² over
35 821 real bath+WC rooms, AzDTN's 3,8); and MİDA's p75 is 3,82, so a quarter of
even the cheap end exceeds the target.

**4. Five cells are not reachable from this source, and each says so on itself.**
`bathroom` (MİDA has no separate `hamam otağı` — every sanitary room is a
`Sanitar qovşağı`, and the largest in a plan is a combined one),
`living_room_1room_flat` (MİDA p50 15,34, *below* — refused by rule 2),
`kitchen` (9,06 against 9,0, 0,7 % apart, moving it is spurious precision),
`bedroom_mansard` (no apartment evidence), `kitchen_zone_in_diner` (zero
`mətbəx-yemək otağı` across 5 954 records; ADR 0034 governs).

**5. Circulation is a dwelling-level quantity here and is not posted on a room
cell.** MİDA has one circulation name and 316 of 318 plans carry exactly one
`Dəhliz`, so its p50 **9,52 m²** is a *whole-apartment* figure. The profile has
three circulation types (`hall`, `corridor`, `entrance_lobby`), and posting a
whole on one of them is ADR 0034's defect inverted. It is handed to
`rules.json` instead as a comparator: MİDA circulation is p50 **13,2 %** of net
internal (p25 11,9 / p75 15,9) against `circ.fraction_hard`'s Swiss-fitted 30 %,
which Baku practice does not approach.

**6. The rounding rule is published and checked.** Every MİDA cell is the p50
rounded to the **nearest 0,1 m²**, the precision AzDTN's own list is published
at. `verify_shipped_cells.py` fails if a shipped cell sits more than 0,05 m²
from its measured p50 — the rounding cannot drift into a free hand.

**7. The derived schedule is committed; the raw harvest is not.**
`experiments/baku-market-areas/mida_plans_318.json` (172 KB) carries the 318
distinct plan geometries, the unit of analysis every statistic is computed over,
plus the raw harvest's md5 (`6fe6d97ef72882ddb75c293a2a731cd8`) and crawl stats.
One derivation step from MİDA's tables rather than a mirror of them, which is
what `minima.md` §7.1's posture asks; the endpoint is undocumented and can vanish,
and these are now shipped constants.

## Consequences

1. **The tier's definition and its contents finally agree.** `market_default` is
   measured practice floored by regulator recommendation, not a recommended
   minimum wearing a target's name. The structural defect — a minimum used as a
   two-sided centre — is resolved for the cells MİDA reaches and named on the
   cells it does not.

2. **The dwelling-level gap closes.** Σ targets at 3 otaq moves **51,6 → 57,2 m²**
   against a room budget of 58,3: **−11 % → −2 %**. At 2 otaq, 40,8 → 43,6
   against 45,5. This is the number the decision was taken on.

3. ⚠️ **Raising a target raises a hard cap, and nothing on this map governs
   that.** `dim.max_area` binds `k[type] × target_area`, hard — so every cell
   raised here **loosens** a hard rule. C14 authorises a profile to *raise a
   floor* and is silent on a profile *raising a cap*; the monotone-upward rule
   inherits that silence. No Plan that failed before passes now for any other
   reason, and the movement is small (`bedroom_single`'s cap moves 9,0·k → 11,5·k),
   but the **lever exists and is unowned**. Handed to
   [Nineteen room types and nine area-band classes](../wayfinder/tickets/71-nineteen-room-types-and-nine-area-band-classes.md),
   which owns `area_bands` and `k`.

4. **The Envelope grows for a silent Brief.** `brief.md` §5 rung 1 sizes the
   Envelope at Σ `target_area` × (1 + f), so a 3-otaq brief that stated no area
   now derives an Envelope about 10 % larger. That is the intended effect — it is
   the dwelling Baku builds — but it is a change to what the engine emits for an
   unchanged prompt, and `brief.md`'s holder should know it.

5. **Four cells now have `conf: derived` off a measurement rather than a
   document**, which is a first for this profile. `src` is `az_mida_2026`,
   `force: informative` — the only value in `source_force_vocabulary` that fits a
   builder's published schedule, and the validator must never derive an AZ
   disclosure from it.

6. **A ticket lowering `bathroom_combined` is overturning a decision taken with
   the contradiction already in hand**, not filling a gap. The same is true of
   `living_room_1room_flat`.

7. ⚠️ **The private Baku market is still unmeasured** and is where the numbers
   differ upward. Every cell here remains a *lower*-biased estimate of Baku as a
   whole. `what_could_not_be_obtained.market_practice` is narrowed to exactly
   that residual rather than deleted.
