---
id: 25
title: The Azerbaijani region profile
parent: map
labels: [wayfinder:research]
status: closed
assignee: tng
blocked_by: []
---

# The Azerbaijani region profile

## Question

*Which region profiles ship in v1* chose `AZ` as the one selectable profile and
**deliberately shipped it empty** — inventing a thickness catalogue in a grilling
session would have produced the 90%-right artefact C2 calls worse than blank. This
ticket populates it, from freely-published primary sources, with every value
carrying the `src` / `ref` / `conf` labels
`data/standards/room-constraints.json` already requires.

Azerbaijan's building norms (**AzDTN**, *Azərbaycan Dövlət Tikinti Normaları*)
derive from the Soviet **SNiP** corpus and its Russian **SP** successors — most
relevantly the multi-apartment residential instrument (SNiP 31-01-2003 /
SP 54.13330) and the dwelling-design and daylight norms around it. Sources are
published rather than paywalled, which is why this profile is buildable where the
DE one was not. Where an AzDTN document cannot be obtained, **name the SNiP/SP
ancestor and label the value `REPORTED`, never `VERIFIED`** — the two are not the
same document and this map has already been bitten twice by a claim that outran
its source.

Deliver every field a profile owns. They were discovered piecemeal across four
closed tickets, so the full list is here:

1. **The wall-thickness catalogue** — `t_int`, `t_ext`, `t_party`, per
   construction type (fired brick, panel, block, monolithic). **This is the
   priority**, because `model.thickness_in_catalogue` is the *only hard acceptance
   rule that reads the region profile*.
2. **Minimum room areas and clear dimensions**, at all three tiers
   (`statutory_floor` / `market_default` / `accessible`). AZ is expected to be the
   **first region where `statutory_floor` is non-null** — SNiP-family norms
   prescribe minimum room areas where German law prescribes none — which gives the
   tier a real consumer for the first time. Record each source's `force` so the
   warn wording can be derived from it rather than from the tier's name; C8 forbids
   claiming a legal floor that is not one.
3. **The window area fraction** for `win.area_ratio` (soft). SNiP-family norms
   state a light-opening ratio against floor area. This also **re-sources
   `win.kitchen_windowless`**, which cites `de_baybo` — a key that has never
   existed in the stub and now points at a deleted region.
4. **Decimal separator** for `DIMDSEP` and every area and dimension string.
5. **Room-name abbreviation table** — the room tag substitutes a *published*
   abbreviation when a name does not fit, never a truncation.
6. **Opening catalogue keys** — user-visible strings; the type marks on the plan
   and the rows of the door and window schedules cite them.
7. **The area measurement convention pair** — *общая площадь* against *жилая
   площадь*. Hand it to *Area measurement convention*; do not decide it here.

## The hard filter, and it is the first thing to check

**Every thickness in the profile must be an even number of millimetres.** ADR 0001
needs `erode(rect, t_int/2)` in integer millimetres; ADR 0004's tier-1 overall
needs `t_party/2`. This is what killed DE: the DIN 4172 octametric series
115 / 365 / 490 is *systematically* odd.

ADR 0006 chose AZ partly on the expectation that the post-Soviet fired-brick series
(**120 / 250 / 380 / 510**, from a 250 × 120 × 65 unit plus a 10 mm joint) and panel
series (**80 / 140 / 160**) are entirely even. **That expectation is `REPORTED` and
unverified — check it before anything else.** If it fails, say so plainly; the
profile absorbs the cost the same way any profile would, and the decision to ship
one region does not depend on it.

## What language the drawing is in

Unasked by any closed ticket and the most product-visible thing here. The
abbreviation table and every room tag need a language: **Azerbaijani** (Latin script
since 1991), **Russian**, or **English**. The three give three different abbreviation
sets and three different sheet-note registers, and *Dimensioning and annotation
rules* already fixed the general notes, three drawn schedules and the title block
that all consume them. Recommend one and say why; note that the drawing is read by a
builder, not by the Homeowner, which is the constituency that should decide it.

## What the corpus can and cannot tell you

Do not re-derive the catalogue from Swiss Dwellings. *Which region profiles ship in
v1* measured it — `experiments/corpus-smoke/wall_thickness_swiss.py`, 199,210 `WALL`
separators — and **there is no module in the corpus**: 59.1% of walls sit within
±2 mm of a multiple of 10 against 50% for uniform noise, and the modal snapped value
holds 5.60%. What the corpus *does* give you is the range a plausible catalogue must
span — p25 109, p50 169, p75 267, p95 440 mm — and that is a sanity check on the AZ
numbers, not a source for them.

## Copyright posture

Unchanged and binding: findings §7.6. Individual values with citations are free;
reproducing a source's own table, its selection and its ordering is not; and
*systematically extracting one work's tables into a data file* (§7.6 item 7) is the
specific failure this project walks into by accident. Prefer the freely-published
regulatory text, re-derive rather than transcribe, and never ship the source PDFs.

Deliverable: `data/standards/room-constraints.json` populated for `AZ` — replacing
the `PLACEHOLDER_NOTE` — with the findings written up under `docs/research/`.
Shares the file with *Ergonomic minima and the constraint table's missing half*,
which owns the region-invariant layer; coordinate rather than collide.

## Two ship gates on this profile, from *Solver timing variance sweep*

The catalogue this ticket fills is now constrained twice over, and both are
cheap to assert in a test:

1. **ADR 0004** — every wall thickness an even number of millimetres, so `t/2`
   stays integral. Already known; this is the rule that made the profile `AZ`
   rather than `DE`.
2. **ADR 0007** — every published dimensional minimum satisfies
   `minimum_mm + t_int` congruent to 0 modulo the grid, for **every** `t_int`
   the profile offers. Unaligned minima cost a whole grid unit per room per axis
   and provably delete 4-, 5- and 6-room dwellings.

Rule 2 has a consequence this ticket has to decide rather than inherit: at a
250 mm grid, `t_int = 100` wants minima congruent to 150 and `t_int = 200` wants
them congruent to 50, and there is **no common solution**. So the profile either
ships a **single internal thickness**, or carries **per-thickness minima**, or
forces the grid question open. The empty catalogue is the right place to settle
that, before any number is written down.

## Resolution

**The profile is populated, every load-bearing value is `verified` against an
Azerbaijani document read first-hand, and the ticket's central assumption was
wrong in our favour.** Deliverable `data/standards/room-constraints.json` →
`profiles.AZ` (the `PLACEHOLDER_NOTE` is gone). Findings
`docs/research/az-region-profile.md`, with four detail partials under
`docs/research/az-region-profile/`. Gates
`experiments/region-profile/gate_check.py` — **28 assertions, all passing**.
Arithmetic `experiments/region-profile/congruence.py`.

### The instruction this ticket gave was the wrong one, and following it would have breached C8

The ticket said: where AzDTN cannot be obtained, name the SNiP/SP ancestor and
label `REPORTED`. **AzDTN is obtainable** — `arxkom.gov.az` serves the normative
PDFs on an unauthenticated GET, and four agents independently read AzDTN 2.7-2
(residential, Baku 2021, register no. 15202111300003), 2.7-3, 2.17-1 (masonry),
2.16-1, 2.12-4\*, the AZS drafting standards, the 2012 area Qaydalar, ВСН 62-91\*
and the official register of documents in force at 01.01.2026. Three of them
converged on the same register numbers and dates independently.

**And the fallback would have been actively wrong.** *AzDTN 2.7-2 terminated the
legal force of СНиП 2.08.01-89\* in Azerbaijan on 2021-11-30* — on its own cover,
and in the register's own wording. The ancestor is **superseded here, not aged**.
The ticket's own "classic SNiP numbers" are folklore: living room is 14/16 not 12,
kitchen 8 not 6, and 1.4 m is the *передняя* — the corridor is 0.85 m. Publishing
them would have asserted a 2500 mm storey height where AZ requires 2700, and an
850 mm **statutory** corridor floor for a rule Azerbaijan repealed. That is
precisely the C8 violation this ticket was written to prevent, reached by
following this ticket's own instruction.

**Generalise it:** `REPORTED` off an ancestor is not a safe degradation of
`VERIFIED`. It is a different claim about a different document, and where the
descendant repealed the ancestor it is a false one.

### 1. The catalogue — one construction type, and arithmetic chose it

`brick`: **`t_int` 120**, `t_int_bearing` 250, `t_ext` leaf 380 (total 500,
`engine_choice`, **provisional** — blocked on Baku's `Dd`), **`t_party` 250**,
derived from AzDTN 2.7-2 cl. 9.22's **50 dB** — an AZ/RU divergence, since Russia
asks 52 — where 120 mm computes to 49 and fails. All even, so
`model.thickness_in_catalogue` finally has something to read.

**The single-`t_int` question was not a choice.** Over 19 sourced candidates the
set of pairs sharing a residue class mod 250 is **empty**, and structurally so:
brick steps by 130, RC panels by 20, and 250 divides neither. Two thicknesses can
share a minima table only if they differ by an exact multiple of the grid. The
ticket's `{100, 200}` example was the general case, not bad luck. Per-thickness
minima was **rejected**: *N* copies of every minimum plus a Plan carrying its
construction type for life, extending `profile_carried_for_life`, for a fidelity
gain v1 cannot show a Homeowner.

**The even-millimetre rule nearly killed AZ too.** ГОСТ 21520-89 Table 1 gives
cellular blocks **two** series by laying method — mortar-laid 200/250/300 even,
**thin-bed-glue-laid 195/245/295 all odd** — and glue is the modern gazobeton
default, where a single-leaf wall is one block wide, so that width *is* `t_int`.
**The `block` type is excluded.** Also named rather than rounded away: **85 mm**
(AzDTN 2.17-1 cl. 8.24, identical in the AZ and RU texts, so not a translation
artefact) and **375 mm**.

Against expectations: **120/250/380 confirmed, 510 refuted as AZ-attested** — 51 cm
appears nowhere in AzDTN 2.17-1. **80/140/160 conflates two products** — brick
panels are 85/140/180/270, RC panels are ГОСТ 12504-80's 60…300 step 20, where all
three ticket values are members and so are ten others: the values are normative,
**the selection is a series-album choice**. **No Azerbaijani document publishes a
monolithic RC thickness at all**, confirmed absent from AzDTN 2.16-1 first-hand.

**The one real cost:** sawn limestone (`ağ daş`, 190/240, both even) is
Azerbaijan's commonest low/mid-rise material and is **not shipped**. Single-`t_int`
buys arithmetic safety and pays for it here. First candidate for a second type.

### 2. `statutory_floor` is real — the first region on this map where it is

Force chain read link by link: cl. 5.7 sits in the mandatory register
(*az olmamalıdır*) → technical normative legal act (Construction Code art. 3.0.26)
→ **art. 14.3 makes compliance obligatory** → art. 14.2's annual SİYAHI lists it in
force. Living 15/16 m², bedroom 8 (10 for two), kitchen 8, niche 5, wardrobe
2.5 m², clear height **2700** — all `statutory`.

**Read the empties as the finding.** Nine of thirteen area cells and **all six
width cells** at `statutory_floor` are `null`, because AzDTN 2.7-2 cl. 5.6
delegates intra-apartment clear dimensions to *erqonomika* **by name** (as does
СП 54.13330.2022 cl. 5.11). **Azerbaijani law points at the region-invariant
layer.** A profile that filled those cells would assert law that does not exist.

Two disclosure constraints: the **`accessible` tier must never print "statutory"**
— AZ's instrument is ВСН 62-91\*, not SNiP 35-01/СП 59 (zero SİYAHI hits), and the
only Azerbaijani act invoking it says *tövsiyə edilir*; its sole genuine uplift is
the kitchen's +1.0 m². And **`force` means force *in Azerbaijan*** — a live Russian
СП is `foreign_not_applicable`, for which the file now carries a controlled
vocabulary, because `superseded` is wrong for law that is live elsewhere.

**The weakest part is the default tier.** No Baku market or MIDA standard is
published, so `market_default` — the Brief's defaulting source *and* the solver's
objective target — rests entirely on regulator recommendation transferred from a
**detached-house** norm. Every such value is `conf: derived`, `force: recommended`,
with the transfer recorded.

### 3. ADR 0007 has no consumer inside a region profile — and that is a finding, not a detail

This ticket was told to settle the congruence question "before any number is
written down". Settled, and it went somewhere the ticket did not anticipate.
`gate_check.py` asserts it: **`hard linear minima published by profile AZ: 0`.**

Two things are wrong with ADR 0007 as written:

1. **Scope too broad.** It binds *"every dimensional minimum published in a region
   profile"*. Only a linear minimum the solver posts on a room's **clear rect** is
   eroded by `t_int`. Areas in m², storey heights, door clear widths and
   wheelchair turning squares are not, and a literal reading corrupts them.
   **Amendment owed to ADR 0007.**
2. **The values it governs are not in region profiles.** The hard floor is the
   region-invariant ergonomic minimum (*Acceptance validator spec*), a profile
   never rejects a Plan (C14), and AZ law delegates every width to ergonomics. So
   every value the rule constrains lives in the **invariant** layer — which by
   construction cannot carry a per-profile `t_int` offset.

**And ADR 0007's own escape does not generalise.** Its move is to publish the
largest admissible value *at or below* the source's figure, justified by reading
that figure as nominal or centreline-to-centreline (1750 → 1650) — which is a
**unit conversion**, and only available for a number quoted from a source. A
body-derived clearance is already clear by definition and has no nominal reading to
reinterpret.

**Measured once the `ergonomic` layer landed mid-session**, so this is not a
prediction: of the **36** hard linear minima that layer publishes, **36 miss the
residue class** — every one, up to **+242 mm per room per axis**, worst on
`corridor` and `hall`, which is what the solver's circulation model rests on.

> ✅ **Settled concurrently, and not by this ticket.** *Ergonomic minima and the
> constraint table's missing half* reached the same convention-derived /
> body-derived distinction from the other side and wrote
> [ADR 0009](../../adr/0009-a-derived-minimum-is-not-rounded-onto-the-solve-grid.md):
> **ADR 0007's congruence rule is a region-profile ship gate only**, the ergonomic
> layer is exempt, published minima stay millimetre-exact and the solver's ceiling
> absorbs the remainder. **The v1 grid stays at 250 mm.** This session had drafted a
> ticket for it; that ticket was **retracted rather than filed**, since the decision
> already exists. The gate check keeps printing the 36 rows to show the exemption is
> load-bearing rather than cosmetic.
>
> ⚠️ **And ADR 0009 refutes one thing stated above.** Rounding up does *not* cost
> "the grid unit ADR 0007 measured as deleting 4-, 5- and 6-room dwellings":
> **that deletion was a function of the minima's magnitude, not of the congruence.**
> ADR 0007 measured it against the *placeholder* table (`living` 2750 mm, `bedroom`
> 2000 mm); the derived ergonomic floor is roughly half that (`living` 1850 × 2000,
> `bedroom` 1650 × 1900) and does not reproduce it. The real cost of snapping is
> concentrated in the **WC**, whose entire real width distribution — p1 744 to p50
> 1099 mm — spans less than two grid steps, so one snap moves the floor across most
> of the population: **23.0 % → 56.1 % rejected**.

The **scope carve-out** this ticket identified is narrower than ADR 0009 but still
owed for any future profile that does publish a linear minimum: areas in m², storey
heights, door clear widths and wheelchair turning squares are not room clear plan
dimensions and must not be aligned. Moot for AZ, which publishes none.

### 4. The drawing is Azerbaijani, and choosing it made the spec smaller

Expertise rules cl. 8.1 (2014 decree) require the state language for submitted
projects. That does not bind our `PRELIMINARY` output, but it fixes the register
the **builder** is trained on — the constituency the ticket named.

**The trade the ticket feared is not armed.** It expected that choosing
Azerbaijani would force us to invent an abbreviation set, which findings §7.6
forbids. In fact **no published room-name abbreviation set exists in any of the
three candidate languages** — ГОСТ 2.316-2008 cl. 4.4 actively *forbids*
abbreviating outside a list with zero room words. Two unrelated families, SPDS and
ISO 4157-2, prescribe the same fallback: **room number + room schedule**, which
`annotation.md` §6 already ships with a `Ref` column. **That replaces ladder step 2
and deletes the annotation spec's only step requiring invented data.**

Also: **decimal separator comma** (`DIMDSEP = 44`), **no thousands grouping**
(CLDR groups `az` with `.`, so `4.400` misreads), `FFL` → **`t.d.s.`**; and
**`DIMDSEP` is inert as specified** — `dimdec = 0` leaves no decimal to separate,
so the field must be plumbed to the strings we format. **Opening marks are
two-level** (plan mark plus product designation), where the spec models one and its
`D1`/`W2` matches no published convention. **Openings are even, blocks are not**
(2071/2085/2175) — `even_opening_required` joins `even_thickness_required` as an
asserted gate. The opening GOSTs **may be dead**: ГОСТ 6629-88 is superseded and
ГОСТ 23166-99 cl. 4.9 explicitly refuses to fix an opening grid.

### 5. Handed on

- **`de_baybo` is closed.** Both consumers re-sourced in
  `data/acceptance/rules.json` to AzDTN 2.7-2 — `win.area_ratio` to cl. 9.13 (1:8
  lower bound, **no cap**; the 1:5.5 the ticket quoted is a *maximum*-glazing
  figure from the repealed SNiP; value unchanged at 0.125, now agreed by two
  independent traditions) and `win.kitchen_windowless` to cl. 9.12. **That second
  one inverted its premise** — the rule was a warn because Bayern *permitted* a
  windowless kitchen, and AZ *requires* the window. Held at warn because C14
  forbids a region changing the reject set; flipping the table's `needs_window`
  for kitchen is the region-invariant fix and is handed to *Ergonomic minima and
  the constraint table's missing half*.
- **Area measurement convention.** **There is no *жилая площадь* in Azerbaijan** —
  the modern instruments replaced the pair rather than extending it, so this
  ticket's framing of the handoff as a *pair* is itself wrong. AZ has **two
  in-force, mutually contradicting statutory definitions of *ümumi sahə***. Every
  divergent clause is inert in v1 except one: **cl. 3.2 measures to the *finished*
  face** while ADR 0001 erodes to the *structural* one, so our figure overstates
  area by 10–20 mm per face.
- **The DXF floor must rise to R2007**, measured: no legacy code page encodes `ə`,
  not even cp1254; Russian is worse, since cp1251 cannot encode `²`.
  `bim-cad-export-stack.md` corrected in two places. Nothing shipped is broken —
  `annotation.md` §11 already writes R2010.
- **Sheet marks** — `AZS ГОСТ 21.101-2010` Əlavə A says `MH`/`MT` where
  `annotation.md` §9 says `A-101`. Ticketed.

### What could not be obtained

**AZS 481-2011 / 476-2011** — Azerbaijan's own brick and limestone standards, sold
rather than published, so modules are cited to ГОСТ 530-2012 and 4001-84 instead;
**Baku's degree-day figure `Dd`**, which is what makes `t_ext_total` provisional
rather than derived; **МСН 2.04-05-95** full text, so KEO is `reported` off the
Russian twin and **not implemented**; **Baku market / MIDA standards**; the
**2001–02 accessibility instructions**. One process note: a paywalled aggregator
was observed returning **fabricated clause text** for СНиП 2.08.01-89\* rather than
an error. Every value here came from a retrieved full text.
