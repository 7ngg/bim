# The Azerbaijani region profile

**Ticket:** *The Azerbaijani region profile*
(`docs/wayfinder/tickets/25-the-azerbaijani-region-profile.md`)
**Deliverable:** `data/standards/room-constraints.json` → `profiles.AZ`
**Gates:** `experiments/region-profile/gate_check.py` — 28 assertions, all passing
**Arithmetic:** `experiments/region-profile/congruence.py`
**Detail:** `docs/research/az-region-profile/{thickness,minima,daylight,drawing}.md`

This document is the synthesis and the decisions. The four partials hold the
per-value provenance and are the thing to read before re-litigating any number.

---

## 1. The headline: the ticket's central assumption was wrong, and wrong in our favour

The ticket instructed: *"Where an AzDTN document cannot be obtained, name the
SNiP/SP ancestor and label the value `REPORTED`, never `VERIFIED`."* It budgeted
for a profile built out of Soviet ancestors at arm's length.

**That fallback was never needed.** `arxkom.gov.az` serves Azerbaijan's normative
PDFs on a plain unauthenticated GET. Read first-hand across four independent
agents:

| document | what it settles |
|---|---|
| **AzDTN 2.7-2** *Yaşayış binaları. Layihələndirmə normaları* (Baku 2021, register no. 15202111300003) | minimum areas, clear heights, daylight ratio, kitchen window, party-wall acoustics |
| **AzDTN 2.7-3** *Fərdi yaşayış evləri* (2023) | `market_default`, and corroboration for houses |
| **AzDTN 2.17-1** (masonry, 2016) | the whole thickness catalogue |
| **AzDTN 2.16-1** (concrete/RC), **2.12-4\*** (thermal, 2022) | what is *absent* — no monolithic thickness is published |
| **AZS ГОСТ 21.101-2010 / 21.501-2010** | decimal separator, abbreviations, mark scheme, sheet marks |
| *Tikinti obyektlərinin sahəsinin … hesablanması qaydaları* (2012), Housing Code art. 12.5 | the area conventions |
| **ВСН 62-91\*** | the `accessible` tier |
| official **register of documents in force at 01.01.2026** | which edition of what applies |

Three agents independently converged on the same register numbers and dates —
genuine corroboration, not one source echoed three times.

**And the fallback would have been actively wrong.** *AzDTN 2.7-2 terminated the
legal force of СНиП 2.08.01-89\* in Azerbaijan on 2021-11-30*, stated on its own
cover and confirmed in the register's own wording (*«СНиП 2.08.01-89\* əvəzinə»*).
The ancestor's numbers are **superseded here, not merely aged**. Following the
ticket's instruction would have published a 2500 mm storey height where AZ
requires 2700, and an 850 mm *statutory* corridor floor for a rule Azerbaijan
repealed — the precise C8 violation the ticket was written to avoid.

Corollary for the map: **`REPORTED` off an ancestor is not a safe degradation.**
It is a different claim about a different document, and where the descendant
repealed the ancestor it is a false one.

---

## 2. The thickness catalogue, and why it is one construction type

### The decision

**Ship `brick` alone, with a single `t_int` of 120 mm.**

| field | mm | conf | source |
|---|---|---|---|
| `t_int` | **120** | verified | AzDTN 2.17-1 cl. 4.3; Table 29 n.2 |
| `t_int_bearing` | **250** | verified | AzDTN 2.17-1 cl. 6.9 |
| `t_ext` structural leaf | **380** | verified | AzDTN 2.17-1 cl. 5.2 n.3, 9.7 |
| `t_ext` total | **500** | engine_choice, **provisional** | blocked on Baku's `Dd` |
| `t_party` | **250** | derived | AzDTN 2.7-2 cl. 9.22 (≥ 50 dB), Table 3 |

Every value even. `model.thickness_in_catalogue` — the only hard acceptance rule
that reads a region profile — now has something to read.

### The arithmetic forced it; taste did not choose it

The ticket framed the single-thickness question as one of three options. It is
not a choice at 250 mm:

```
residue (-t_int) mod 250 over 19 sourced candidates
  80:170  100:150  120:130  140:110  160:90  180:70
 200:50   250:0    300:200  380:120  400:100 510:240
pairs sharing a residue class:  NONE
```

Two thicknesses can share one minima table **only if they differ by an exact
multiple of 250**. The fired-brick series steps by 130 and the RC-panel series by
20 — the one series rich enough to offer a choice is the one whose module forbids
it. This is structural, not bad luck, and the ticket's `{100, 200}` example was
the general case rather than an unlucky one.

**Per-thickness minima was rejected**, not overlooked: it needs *N* copies of
every dimensional minimum *and* a Plan carrying its construction type for life —
extending `profile_carried_for_life`, which today pins only the region id — for a
fidelity gain v1 cannot show a Homeowner. The grid question is left open exactly
where ADR 0007 left it.

### What the even-millimetre rule caught this time

The rule that killed DE nearly killed AZ too, and at a place nobody was looking:

> **ГОСТ 21520-89 Table 1 gives cellular-concrete blocks two thickness series by
> laying method — mortar-laid 200 / 250 / 300 (even) and thin-bed-glue-laid
> 195 / 245 / 295 (all odd).**

Glue is the modern default for gazobeton, and a single-leaf gazobeton wall is one
block wide, so that width *is* `t_int`. **The `block` construction type is
excluded from v1.** Two further odd values are named rather than rounded away:
**85 mm** (AzDTN 2.17-1 cl. 8.24 quarter-brick panel — carried identically in the
AZ and RU texts, so not a translation artefact) and **375 mm** (commercial
gazobeton, from the abolished ГОСТ 11024-84 M/4 series).

### Against the ticket's stated expectations

- **120 / 250 / 380 confirmed. 510 refuted as AZ-attested** — AzDTN 2.17-1 speaks
  only in 12 / 25 / 38 / 40 cm; 51 cm appears nowhere in it. 510 stays shippable
  only as `derived` from ГОСТ 530-2012 Table 3.
- **80 / 140 / 160 "the panel series" conflates two products.** Brick panels are
  85 / 140 / 180 / 270 (AzDTN); RC panels are ГОСТ 12504-80 cl. 2.2 Table 1,
  60 … 300 step 20. All three ticket values are genuine members — and so are ten
  others. The values are normative; **the selection is a series-album choice and
  must never be presented as normative.**
- **The party wall is 50 dB in AZ, not Russia's 52** (AzDTN 2.7-2 cl. 9.22). A
  120 mm brick wall computes to 49 dB and fails, which is what forces `t_party`
  to 250.
- **No Azerbaijani document publishes a monolithic RC wall thickness in
  millimetres** — confirmed *absent* from AzDTN 2.16-1 first-hand. The 160 mm
  everyone quotes is СП 430.1325800.2018 §5.2.11, phrased *«рекомендуется»*, with
  no AZ counterpart.

### The one real cost

**Sawn limestone (`ağ daş`, ГОСТ 4001-84, widths 190 / 240, both even) is not
shipped**, and it is Azerbaijan's commonest low- and mid-rise wall material. The
single-`t_int` decision buys arithmetic safety and pays for it here. It is the
first thing a second construction type should be.

---

## 3. `statutory_floor` is real, and this is the first region where it is

AzDTN 2.7-2 cl. 5.7 is in the mandatory register (*az olmamalıdır*); the norm is a
technical normative legal act (Construction Code art. 3.0.26); **art. 14.3 makes
compliance obligatory**; art. 14.2's annual SİYAHI lists it as in force. Each link
read, not inferred.

| tier | headline | force |
|---|---|---|
| `statutory_floor` | living 15 (1-room) / 16 m²; bedroom 8 (10 for two); kitchen 8; niche 5; entry wardrobe 2.5 m²; clear height **2700** | **statutory** |
| `market_default` | living 16, bedroom 9 (12 for two), kitchen 9, bath 3.2, combined 3.8 m²; widths 3000 / 2600 / 1400 / 1500 / 800 | recommended |
| `accessible` | kitchen 9.0 m² / 2200; WC 1200 × 1600; turn 1500; door 900 | **recommended, never statutory** |

**Read the empties as the finding.** Nine of thirteen area cells and **all six
width cells** at `statutory_floor` are `null`. Azerbaijani law fixes
habitable-room and kitchen areas and nothing else about a room's plan. A profile
that fills those cells asserts law that does not exist.

Three things that constrain how this may be printed:

1. **The width cells are null *by design*.** AzDTN 2.7-2 cl. 5.6 delegates
   intra-apartment clear dimensions to *erqonomika* **by name**, and
   СП 54.13330.2022 cl. 5.11 does the same. **Azerbaijani law points directly at
   the region-invariant ergonomic layer.**
2. **The `accessible` tier must never print "statutory."** AZ's instrument is
   **ВСН 62-91\***, not SNiP 35-01 / СП 59.13330 — those return *zero* hits in the
   SİYAHI. Its clauses read mandatorily, but that is the Soviet drafter's
   register; the only Azerbaijani act invoking it (AzDTN 2.7-3 cl. 4.17) says
   *tövsiyə edilir*. The tier's one genuine uplift is the kitchen's +1.0 m².
3. **`force` means force *in Azerbaijan*.** A Russian СП that is live law in the
   Russian Federation is `foreign_not_applicable` here. The file now carries a
   controlled vocabulary for this, because `superseded` is wrong for a document
   that is live law somewhere else and the validator must never derive an AZ
   disclosure from one.

**The weakest part of the profile is its default tier.** No Baku market or MIDA
space standard could be obtained, so `market_default` — which is both the Brief's
defaulting source and the solver's objective target — rests entirely on regulator
recommendation transferred from a *detached-house* norm. Every such value is
`conf: derived`, `force: recommended`, with the building-type transfer recorded.

---

## 4. ADR 0007 does not have a consumer in this profile

This is the finding the ticket did not anticipate, and it is the largest one here.

ADR 0007 binds *"every dimensional minimum published in a region profile"*. Two
things are wrong with that as written.

**First, the scope is too broad.** Only a linear minimum the solver posts on a
room's **clear rect** is eroded by `t_int`. Areas in m², storey heights, door
clear widths and wheelchair turning squares are not room clear plan dimensions and
must not be aligned. A literal reading corrupts them. *Amendment owed.*

**Second — and this is the structural problem — the values it governs are not in
region profiles.** `gate_check.py` asserts it:

```
hard tier is None; hard linear minima published by profile AZ: 0
```

The hard floor is the **region-invariant ergonomic minimum** (*Acceptance
validator spec*), a profile never rejects a Plan (C14), and AzDTN 2.7-2 cl. 5.6
explicitly delegates every intra-apartment width to ergonomics. So **every value
ADR 0007 constrains lives in the invariant layer — which by construction cannot
carry a per-profile `t_int` offset.**

And the escape ADR 0007 itself uses does not generalise. Its move is to publish
the largest admissible value *at or below* the source's figure, justified by
reading that figure as nominal or centreline-to-centreline (1750 → 1650). That
reading is legitimate for a **convention-derived** minimum. It is illegitimate for
a **body-derived** one: an ergonomic clearance is already clear by definition and
has no nominal reading to reinterpret. Rounding it down simply violates the floor;
rounding it up pays exactly the grid unit ADR 0007 measured as deleting 4-, 5- and
6-room dwellings.

**Settled concurrently, and not by this ticket.** *Ergonomic minima and the
constraint table's missing half* reached the same convention-derived /
body-derived distinction from the other side and wrote **ADR 0009**: the
congruence rule is a **region-profile ship gate only**, the ergonomic layer is
exempt, published minima stay millimetre-exact, the solver's ceiling absorbs the
remainder, and **the v1 grid stays at 250 mm**. A ticket drafted for it here was
retracted rather than filed.

⚠️ **ADR 0009 refutes the feared cost, too.** Rounding up does *not* trigger
ADR 0007's 4-, 5- and 6-room deletion: **that deletion tracked the minima's
magnitude, not the congruence.** It was measured against the *placeholder* table
(`living` 2750 mm, `bedroom` 2000 mm), and the derived floor is roughly half that.
The real cost of snapping is the **WC**, whose entire real width distribution — p1
744 to p50 1099 mm — spans **less than two grid steps**, so one snap moves the
floor across most of the population: **23.0% → 56.1% rejected**.

The **scope carve-out** above is still owed, and is narrower than ADR 0009: ADR
0007 still binds region *profiles*, and areas, storey heights, door clear widths
and turning squares are not room clear plan dimensions. Moot for AZ, which
publishes none.

For the record, the soft targets and what alignment would cost them:

| target | published | smallest achievable clear | cost |
|---|---|---|---|
| habitable room | 3000 | 3130 | +130 |
| kitchen | 2600 | 2630 | +30 |
| hall / corridor | 1400 | 1630 | +230 |
| bathroom | 1500 | 1630 | +130 |
| WC | 800 | 880 | +80 |
| WC with basin | 1200 | 1380 | +180 |

A soft target costs objective drift, never feasibility, so ADR 0007 does not bind
these. They are listed because the same arithmetic will bind their hard
counterparts once the invariant layer exists.

---

## 5. The drawing is in Azerbaijani, and it costs nothing

**Recommendation taken: Azerbaijani, Latin script.**

The expertise rules (2014 presidential decree) cl. 8.1 require the state language
for projects submitted to expertise — *"Ekspertizaya təqdim edilən tikinti
layihələri dövlət dilində tərtib olunmalıdır"*. That decree does not bind our
`PRELIMINARY` output, but it fixes the register the **builder** is trained on, and
the ticket named the builder as the constituency that should decide.

**The objection the ticket anticipated is not armed.** It feared that choosing
Azerbaijani would force us to invent an abbreviation set, which findings §7.6
forbids. In fact **no published room-name abbreviation set exists in any of the
three candidate languages** — ГОСТ 2.316-2008 cl. 4.4 actively *forbids*
abbreviating outside a list containing zero room words, the Azerbaijani and
Russian appendices each yield exactly one of our thirteen, and the English set is
paywalled and tells you to spell it out.

Two unrelated standards families — SPDS and ISO 4157-2 — prescribe the same
different fallback: **room number plus room schedule**, which `annotation.md` §6
already ships with a `Ref` column and a totality assertion. **That replaces ladder
step 2 and deletes the only step in the annotation spec that required invented
data.** The language choice made the spec smaller.

Other drawing decisions:

- **Decimal separator: comma**, `DIMDSEP = 44`, drafting standard and locale
  agreeing. **No thousands grouping** — CLDR gives `.` as the `az` group
  separator, so a grouped `4.400` reads as a decimal. `FFL ±0.000` → `±0,000`,
  and `FFL` itself becomes **`t.d.s.`**.
- **`DIMDSEP` is inert as specified.** `annotation.md` §4 sets `dimdec = 0`, so
  there is no decimal for it to separate. The field must be plumbed to the strings
  we format ourselves — areas, levels, schedule cells — or it silently never
  fires.
- **Opening marks are two-level**, where the spec models one: a plan mark
  (`ОК1` for windows; doors take a *bare number* in a Ø5 mm circle in the
  Azerbaijani edition) plus a product designation (`ДГ 21-9`) in the schedule.
  The spec's `D1`/`W2` matches no published convention.
- **Openings are even; blocks are not.** Every opening dimension in the series is
  even; every *block* height is odd (2071 / 2085 / 2175). `annotation.md` §4.4 and
  §4.5 already dimension to the structural opening, so the spec is on the right
  side of this — but `even_opening_required` now joins `even_thickness_required`
  as an asserted gate.
- **The opening GOSTs may be dead.** ГОСТ 6629-88 is superseded and its live
  successors explicitly refuse to fix an opening grid (ГОСТ 23166-99 cl. 4.9 makes
  it a project decision). If that holds, the catalogue is `engine_choice` bounded
  by the old series rather than `verified`. Recorded as an open question.

---

## 6. Two things that land outside this ticket

### The DXF version floor must rise, and this is measured

**The Azerbaijani alphabet is unrepresentable in DXF R2000.** No legacy code page
anywhere encodes `ə` — not even Turkish cp1254, which carries every other
Azerbaijani letter. R2007+ is clean. Russian is **worse** at R2000, not better:
cp1251 cannot encode `²`.

Nothing shipped is broken — `annotation.md` §11 already writes R2010 — but
`bim-cad-export-stack.md`'s line that *"`²` survived — R2000+ is unicode-capable"*
is **false in general**, and the stated floor has to move from R2000 to R2007.
Probes in `experiments/az-drawing/`.

### The annotation spec is US-shaped and the drawing is now Azerbaijani

`AZS ГОСТ 21.101-2010` Əlavə A marks architectural drawings **`MH`** (*Memarlıq
həlli*) or **`MT`**, where `annotation.md` §9/§10 numbers sheets `A-101` on US NCS
and §11 layers them `A-WALL` on AIA. A drawing issued in Azerbaijani to an
Azerbaijani builder with a US sheet number is internally inconsistent. Layer names
are a machine-facing interchange convention with their own justification; the
**sheet number**, which the builder reads, is the one worth reconsidering.
Ticketed.

---

## 7. Handed on, not decided here

- **Area measurement convention.** The ticket asked for the *общая / жилая* pair.
  **There is no *жилая площадь* in Azerbaijan** — the modern instruments replaced
  the pair rather than extending it. What AZ has instead is **two in-force,
  mutually contradicting statutory definitions of *ümumi sahə***: the Housing Code
  (art. 12.5) excludes balconies outright, the 2012 Qaydalar (cl. 3.8) includes
  them at 0.3 / 0.5 / 1.0. Both statutory. That disagreement is the real question.
  Every divergent clause is **inert in v1** (no balcony, no ceiling height) except
  one: **cl. 3.2 measures to the *finished* face**, while ADR 0001 erodes `t_int/2`
  to the *structural* face. At 10–20 mm per face, publishing our figure as *ümumi
  sahə* systematically overstates area.
- **The ergonomic layer.** Every `null` width cell here is a value that ticket
  owns, and AZ law points at it by name.
- **KEO.** In force in AZ via МСН 2.04-05-95, whose text could not be obtained
  from any Azerbaijani source. Carried `reported` off the Russian twin and **not
  implemented** — it needs a sky model, orientation, obstruction angle and a
  light-climate coefficient our geometry does not carry.

---

## 8. Copyright posture

Findings §7.6, observed throughout. Every value is cited individually; no source's
table is reproduced with its own selection and ordering; the seven abbreviations
carried from `AZS ГОСТ 21.101-2010` Əlavə D are the subset *our* schema names, not
that table. **No source PDF is committed.** The residential opening subset is the
one place where the risk is real — a standard's size table is the standard's
expression — so the designation *scheme* is re-derived as a rule and only the ten
keys our schedules actually print are carried, each cited.

## 9. What could not be obtained

- **AZS 481-2011** and **AZS 476-2011** — Azerbaijan's own brick and limestone
  standards. Sold, not published; modules are cited to ГОСТ 530-2012 and
  ГОСТ 4001-84 instead, and the profile says so.
- **Baku's degree-day figure `Dd`** — the one gap blocking a defensible
  `t_ext_total`. That value is flagged provisional rather than guessed.
- **МСН 2.04-05-95** full text.
- **Baku market / MIDA space standards** — see §3.
- **The Azerbaijani accessibility instructions of 2001–02** — appear unpublished.

One process note worth recording: a paywalled aggregator was observed returning
**fabricated clause text** for СНиП 2.08.01-89\* — an invented clause number and
invented coefficients — rather than an error. Every value in this profile came
from a retrieved full text.
