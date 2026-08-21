# AZ wall-thickness catalogue — research partial

**Ticket:** `docs/wayfinder/tickets/25-the-azerbaijani-region-profile.md`, item 1
(the priority item, because `model.thickness_in_catalogue` is the only hard
acceptance rule that reads the region profile).
**Scope:** the wall-thickness catalogue only — `t_int`, `t_int_bearing`, `t_ext`,
`t_party`, per construction type. Nothing else in ticket 25 is decided here.
**Status:** partial, owned by this session. **Do not edit
`data/standards/room-constraints.json` from this file** — another session owns the
merge.
**Date:** 2026-08-20.

C8 applies to every number below: Neufert-grade dimensional data. **No legal
code-compliance claim is made or implied**, in Azerbaijan or anywhere else, by any
value here.

---

## 0. Verdict, up front

1. **AzDTN is obtainable, free, and was read first-hand.** The ticket assumed it
   would not be and instructed us to fall back on SNiP/SP ancestors labelled
   `reported`. That fallback turned out to be unnecessary for the load-bearing
   parts of this slice. `arxkom.gov.az` serves the actual normative PDFs on a
   plain unauthenticated GET. Four Azerbaijani instruments were downloaded and
   read in full: **AzDTN 2.17-1** (masonry), **AzDTN 2.7-2** (multi-apartment
   residential), **AzDTN 2.16-1** (concrete and reinforced concrete),
   **AzDTN 2.12-4\*** (thermal protection), plus the **official register** of
   documents in force in Azerbaijan at 01.01.2026.
2. **The ticket's fired-brick expectation is CONFIRMED for 120 / 250 / 380 and
   REFUTED for 510.** The 12 / 25 / 38 cm series appears in AzDTN 2.17-1 in
   Azerbaijani. **51 cm does not appear anywhere in that document** — I grepped
   the extracted text. 510 mm is real, but it is `derived` from the module, and
   corroborated by GOST 530-2012's own working-width list, not by AzDTN.
3. **The panel expectation 80 / 140 / 160 is half right, and the half that is
   wrong matters.** Two different products get conflated. AzDTN 2.17-1 §8.24's
   *brick*-panel series is **85 / 140 / 180 / 270 mm**, and **85 mm is ODD** —
   80 and 160 are not in it. *Reinforced-concrete* panels are governed by
   ГОСТ 12504-80, the edition Azerbaijan's register lists, whose cl. 2.2 Table 1
   runs **60 … 300 in steps of 20**; 80, 140 and 160 are all genuine members, but
   so are ten others. The values are normative; **the selection is a series-album
   choice and must not be presented as "the panel series".** See §3.
4. **The Azerbaijani party-wall requirement is 50 dB, not the 52 dB of the Russian
   corpus.** AzDTN 2.7-2 §9.22, read first-hand. This is a genuine AZ/RU
   divergence and it changes which thicknesses pass.
5. **No Azerbaijani document publishes a wall thickness in millimetres for
   monolithic reinforced concrete.** AzDTN 2.16-1 gives cover and reinforcement
   spacing only. The 160 mm figure everyone quotes is Russian SP 430.1325800.2018
   §5.2.11 and it is phrased *"рекомендуется"*. Monolithic values are
   `engine_choice`, and must say so.
6. **Even-millimetre verdict: PASS for the catalogue we would actually ship —
   but three odd series exist and are named rather than rounded.** See §8. The
   dangerous one is **195 / 245 / 295 mm**: ГОСТ 21520-89 Table 1 gives cellular
   blocks *two* thickness series by laying method, and the **thin-bed-glue series
   — which is the modern default for gazobeton — is entirely odd.** A single-leaf
   gazobeton wall is one block wide, so that block width *is* `t_int`. This is
   structurally the same defect that killed DE. The others are **85 mm**
   (AzDTN 2.17-1 §8.24) and **375 mm** (commercial gazobeton, traceable to the
   abolished ГОСТ 11024-84 М/4 = 25 mm series). **Recommendation: do not ship the
   aerated-block construction type in v1** (§4.3).
7. **ADR 0007 is hostile and the ticket's fear is exactly right.** Computed over
   all **19** sourced candidate `t_int` values, the set of pairs sharing a residue
   class mod 250 is **empty** — and structurally so: the brick series steps by 130
   (`gcd(130,250) = 10`) and the RC-panel series steps by 20, which 250 does not
   divide. So **the AZ profile genuinely needs exactly one `t_int`** if it is to
   have a single minima table. Recommended: **`t_int` = 120 mm**, residue **130
   mod 250**, minima 1630 / 1880 / 2130 / 2380 / 2630 / 2880 … See §9. This
   partial reports the arithmetic; it does not make the call.
8. **One thing the ticket did not ask for and the profile should have: sawn
   limestone block** (*ağ daş*, ГОСТ 4001-84 / AZS 476-2011, widths 190 / 240 mm,
   all even). It is Azerbaijan's commonest low- and mid-rise wall material.
   Leaving it out would be a larger fidelity error than any rounding here. See §6.

---

## 1. Jurisdiction — what Azerbaijan actually applies, read first-hand

**`az_register_2026`** — *"Azərbaycan Respublikasında qüvvədə olan şəhərsalma və
tikintiyə dair normativ sənədlərin SİYAHISI (01.01.2026-cı il tarixinə olan
vəziyyət)"*, joint official publication of the **Ministry of Emergency Situations**
and the **State Committee on Urban Planning and Architecture**, Baku 2026,
register code DŞAK-K № 0009-2026. Read first-hand.

Its preamble states, in its own words, that under **Cabinet of Ministers Decision
No. 217 of 15 April 1992** *"all normative, methodological and guidance documents
existing in the construction field of the former USSR have been retained in force
on the territory of the Republic of Azerbaijan and are currently applied in the
republic's construction complex."* So the SNiP/GOST inheritance the ticket assumed
is not an analogy — it is an explicit legal act, and the register is its live index.

Three consequences that decide every label in this document:

- **An AzDTN, where one exists, supersedes its SNiP ancestor explicitly.** Each
  AzDTN cover page carries a sentence of the form *"from the date this technical
  normative legal act enters into force, the legal force of СНиП … on the
  territory of the Republic of Azerbaijan is suspended."* AzDTN 2.17-1 says it of
  СНиП II-22-81\*; AzDTN 2.12-4\* says it of СНиП II-3-79\*.
- **Interstate GOSTs are in force in Azerbaijan by a dated domestic act**, listed
  individually in the register with the approving order. That is a much better
  provenance than "Azerbaijan inherits GOSTs", and it is checkable per standard.
- **Russian SP documents are NOT Azerbaijani authority.** No SP appears in the
  register. Where this document cites an SP it is flagged as such and the value is
  never presented as an Azerbaijani requirement.

### Standards confirmed in force in Azerbaijan by the register

Each of these was found in the register's own entries, first-hand:

| Standard | Register note (paraphrased, not transcribed) |
|---|---|
| ГОСТ 530-2012 *Кирпич и камень керамические* | listed in force, §5.2.2 wall materials |
| **AZS 481–2011 (ГОСТ 530-2007)** *Keramik kərpic və daşlar* | MES order No. 088 (2011); registered by order No. 204 of 30.12.2011, in force in AZ from 30.12.2011; replaces ГОСТ 530-95 and ГОСТ 7484-78 |
| ГОСТ 4001-84 *Камни стеновые из горных пород* | listed in force |
| **AZS 476–2011 (ГОСТ 4001-84)** *Dağ süxurlarından divar daşları* | MES order No. 088 (2011) |
| ГОСТ 379-2015 *силикатные кирпич, камни, блоки, плиты перегородочные* | in force, replacing ГОСТ 379-95 |
| ГОСТ 6133-99 *Камни бетонные стеновые* | in force from 30.12.2011 |
| ГОСТ 21520-89 *Блоки из ячеистых бетонов стеновые мелкие* | Committee decision No. 01 of 13.03.2013, in force from 10.05.2013 |
| ГОСТ 31360-2007 *Изделия стеновые неармированные из ячеистого бетона автоклавного твердения* | in force, replacing the autoclaved part of ГОСТ 21520-89 |
| ГОСТ 25485-89 / ГОСТ 31359-2007 *Бетоны ячеистые* | Committee decision No. 02 of 17.10.2013, in force from 15.11.2013 |
| **ГОСТ 11024-2012** *Панели стеновые наружные бетонные и железобетонные* | Committee decision No. 01 of 13.03.2013 |
| **ГОСТ 12504-80** *Панели стеновые внутренние бетонные и железобетонные* | in force — **note the 1980 edition, not the 2015 one** |
| ГОСТ 11118-2009 *Панели из автоклавных ячеистых бетонов для наружных стен* | Committee order No. 59 of 20.05.2010 |
| ГОСТ 6428-83 *Плиты гипсовые для перегородок* | Committee order No. 09 of 01.02.2010 |

**Copyright note on the register itself.** Its own front matter forbids reproducing
it, in whole or in part, as an official publication without the permission of the
two issuing bodies. The table above is therefore a set of individual facts in our
own ordering, chosen by our schema — not a reproduction of its selection or
arrangement. §7.6 items 5 and 7 apply and are being observed.

### The one document we wanted and could not get

**AZS 481-2011** — Azerbaijan's own ceramic-brick standard, and the instrument
AzDTN 2.17-1 §2 actually references for brick dimensions. The register tells us it
is the AZ adoption of **ГОСТ 530-2007**. Its text is sold by the national
standards body, not published. **So the brick module below is cited to
ГОСТ 530-2012 — which the register separately confirms in force in Azerbaijan and
which I read in full — and not to AZS 481-2011.** They are not the same document,
and no value here claims otherwise.

---

## 2. Construction type A — fired-brick (and silicate) masonry

### 2.1 The module

| field | value_mm | src_key | ref | conf | note |
|---|---|---|---|---|---|
| brick, normal format (одинарный / 1НФ) | 250 × 120 × 65 | `gost_530_2012` | cl. 3.2 | verified | AZ's own AZS 481-2011 adopts GOST 530-2007, same unit; text not obtained. |
| brick, thickened (1,4 НФ) | 250 × 120 × 88 | `gost_530_2012` | Table 2 | verified | |
| ceramic *stone* (камень) | hollow, nominal thickness ≥ 140 | `gost_530_2012` | cl. 3.3 | verified | |
| **working width forms the wall thickness at one-stone thickness** | definitional | `gost_530_2012` | cl. 3.12 | verified | this is the hook that makes the next row a *wall* dimension and not a *unit* dimension. |
| working widths listed | 120, 250, 380, 510 | `gost_530_2012` | Table 3 | verified | all four, in the standard's own list. |
| bed (horizontal) joint | 12 | `sp_70_2012` | cl. 9.2.4 | verified | **RU source.** Not an AZ instrument. |
| vertical joint | 10 | `sp_70_2012` | cl. 9.2.4 | verified | **RU source.** |
| silicate brick / thickened / stone | 250 × 120 × 65 / 250 × 120 × 88 / 250 × 120 × 138 | `gost_379_2015` | cl. 3.1–3.3 | verified | same 250/120 module; AZ voted for adoption and the register confirms it in force. |
| silicate partition plate | header width **≤ 130** | `gost_379_2015` | cl. 3.5 | verified | an upper bound on a partition, not a value. |

**The derivation, stated as a rule so nothing is transcribed.** A wall `n`
half-bricks thick alternates 120 mm units with 10 mm vertical joints:

```
t(n) = 120·n + 10·(n − 1) = 130·n − 10
```

| n | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| t, mm | **120** | **250** | **380** | **510** | **640** |

`130n − 10` is even for every integer `n`. **The series is even by construction,
not by luck** — which is precisely the structural difference from DIN 4172, whose
`125n − 10` is odd for every odd `n`. That was the bet ADR 0006 made, and it holds.

### 2.2 What AzDTN 2.17-1 itself says, in Azerbaijani

Read first-hand from the PDF at `arxkom.gov.az`. Values, with clause:

| Provision | Value | ref | conf |
|---|---|---|---|
| Frost-resistance grades apply to the outer part of walls taken as 12 cm thick | **120 mm** | AzDTN 2.17-1 cl. 4.3 | verified |
| Rigid lateral supports: stone/concrete cross-walls; reinforced-concrete cross-walls | **≥ 120 mm** / **≥ 60 mm** | cl. 8.16 a) | verified |
| Design resistances of Table 3 apply to masonry ≥ 40 cm; non-load-bearing and self-supporting wall sections **25–38 cm** permitted with a 0.8 factor | 250 … 380 mm | cl. 5.2, note 3 | verified |
| Accidental-eccentricity rule for load-bearing and self-supporting walls of thickness **25 cm and less** | 250 mm | cl. 6.9 | verified |
| Correction factor bracket for **non-load-bearing walls and partitions >10 cm and <25 cm** | 100 … 250 mm | Table 29, note 2 | verified |
| Winter-work rule brackets walls and columns at **38 cm** | 380 mm | cl. 9.7 | verified |
| Rubble-concrete basement/foundation walls / rubble masonry walls | ≥ 350 / ≥ 500 mm | cl. 8.67 | verified |
| **510 mm** | **absent** | — | — |

So the Azerbaijani masonry code speaks in **12 / 25 / 38 / 40 cm**. It never writes
51 cm. That is the one part of the ticket's REPORTED expectation that does not
survive contact with the AZ document, and it is a soft failure: 510 remains
correct arithmetic and is independently listed in GOST 530-2012 Table 3 — it just
is not attested in AzDTN.

### 2.3 The catalogue, type A

| field | value_mm | src_key | ref | conf | note |
|---|---|---|---|---|---|
| `t_int` | **120** | `azdtn_2_17_1` | cl. 4.3 / Table 29 n.2 (bracket) + `gost_530_2012` Table 3 | verified | half-brick partition, bare masonry. **Recommended `t_int`.** |
| `t_int` alt (rendered) | **150** | — | — | engine_choice | 120 + 2 × 15 mm plaster. No source read here states a plaster thickness. If shipped, `note` must carry the rule. |
| `t_int_bearing` | **250** | `azdtn_2_17_1` | cl. 6.9 + `gost_530_2012` Table 3 | verified | one brick. |
| `t_int_bearing` heavy | **380** | `azdtn_2_17_1` | cl. 5.2 n.3, cl. 9.7 | verified | 1½ brick. |
| `t_ext` structural leaf | **380** | `azdtn_2_17_1` | cl. 5.2 n.3 | verified | the conventional AZ external brick leaf. |
| `t_ext` structural leaf, heavy | **510** | `gost_530_2012` | Table 3 | derived | `130n − 10` at n = 4; listed as a working width; **not attested in AzDTN**. |
| `t_ext` total, insulated | **500** | — | see §2.4 | engine_choice | 380 leaf + 100 insulation + 20 finish. Do not present as published. |
| `t_party` | **250** | see §7 | — | derived | one brick; 120 mm fails the AZ 50 dB requirement by calculation. |

### 2.4 The external wall is a build-up, and the total is an engine choice

**AzDTN 2.12-4\*** *"Binaların istilik mühafizəsi. Layihələndirmə normaları"* (new
redaction, Baku 2025; approved by Collegium decision MİHO/2.1-3.2-2022-4 of
10 June 2022, in force from 10.06.2022, State Register of Legal Acts no.
15202206100224; **suspends СНиП II-3-79\*** in Azerbaijan). Read first-hand.

Its **Table 4 with formula (1)** sets the normalised thermal resistance as a linear
function of heating degree-days:

```
R_req = a·Dd + b        [m²·°C/W]
```

For **residential** buildings, **walls**: `a = 0.00035`, `b = 1.4`; the table's
anchor rows give `R_req` = **2.1 / 2.8 / 3.5** at `Dd` = 2000 / 4000 / 6000 °C·day.
All verified, AzDTN 2.12-4\* Table 4 and note 1.

**Why this matters to the catalogue:** a 380 mm solid clay-brick leaf reaches
roughly `R ≈ 0.7` m²·°C/W including surface resistances — about a third of the
2.1 the norm asks for at the lowest tabulated `Dd`. **The structural leaf is
therefore never the finished external wall in Azerbaijan**, and a profile that
ships `t_ext = 380` as a total is wrong by a layer.

**GAP:** Baku's `Dd` is set by the construction-climatology norm
(AzDTN 2.1-1 family), which I did not obtain. Without it the required insulation
thickness cannot be computed to a citable number, only estimated. The 500 mm total
above is the engine's own rounding of a plausible build-up (380 + 100 + 20) and is
labelled `engine_choice` for that reason. **Close this before shipping a total.**

---

## 3. Construction type B — large-panel prefabricated

Two distinct families that are constantly conflated, and the AZ register puts
different documents in force for each.

### 3.1 Brick and ceramic panels — AZ-verified

| field | value_mm | src_key | ref | conf | note |
|---|---|---|---|---|---|
| internal wall / partition panel, quarter-brick | **85** | `azdtn_2_17_1` | cl. 8.24 | verified | **ODD.** Note 2 to the clause: quarter-brick panels are for **partitions only**. |
| internal wall / partition panel, half-brick | **140** | `azdtn_2_17_1` | cl. 8.24 | verified | |
| internal wall panel, one brick | **270** | `azdtn_2_17_1` | cl. 8.24 | verified | |
| internal, two-layer (two quarter-brick leaves) | **180** total | `azdtn_2_17_1` | cl. 8.24 | verified | |
| — note 1 to cl. 8.24 | thicknesses **include** the outer and inner mortar/render layers | `azdtn_2_17_1` | cl. 8.24 n.1 | verified | this is why 140 ≠ 120 and 270 ≠ 250. |
| external panel, two-layer | leaf **≥ half-brick** + rigid insulation boards **≥ 40 mm** + reinforced protective mortar layer (grade ≥ M50) | `azdtn_2_17_1` | cl. 8.23 | verified | no total stated. |
| external panel, three-layer | outer leaves quarter- or half-brick, core rigid/semi-rigid insulation | `azdtn_2_17_1` | cl. 8.23 | verified | |
| external single-layer panel of hollow ceramic stones | **1½ and 2 stones** thick | `azdtn_2_17_1` | cl. 8.22 | verified | ⇒ 380 and 510 by the §2.1 rule. |
| rib width carrying the reinforcement cage | ≤ 30 mm | `azdtn_2_17_1` | cl. 8.23 | verified | |

**The ticket's `80 / 140 / 160` panel expectation does not match this.** 140 is
right; 80 and 160 are not in AzDTN 2.17-1. The nearest real neighbours are 85
(odd) and 180.

### 3.2 Reinforced-concrete wall panels — GOST-verified, in the editions Azerbaijan lists

There is **no AzDTN for large-panel residential design.** The register puts
**ГОСТ 11024-2012** (external) and **ГОСТ 12504-80** (internal) in force in
Azerbaijan by dated Committee acts. Both editions were read first-hand — and note
that Azerbaijan lists **older editions than Russia currently applies**, which in
this case works in our favour (see the odd-value rupture below).

**Internal panels — ГОСТ 12504-80 cl. 2.2, Table 1.** Coordination thickness on
module **М/5 = 20 mm**:

```
60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300
```

| field | value_mm | src_key | ref | conf | note |
|---|---|---|---|---|---|
| internal panel thickness series | 60 … 300 step 20 | `gost_12504_80` | cl. 2.2 Table 1 | verified | 13 members; the module is М/5 = 20 mm, so **every member is even by construction**. |
| nominal = coordination thickness | — | `gost_12504_80` | cl. 2.3 | verified | М/2 = 50 mm permitted for cellular-concrete panels partly forming an external wall. |
| **minimum, load-bearing** | **100** | `gost_12504_80` | cl. 2.4 | verified | |
| **minimum, non-load-bearing** | **60** | `gost_12504_80` | cl. 2.4 | verified | the standard's scope covers internal load-bearing walls *and* partitions, with no separate partition table, so 60 is the partition floor. |
| socket-box separating diaphragm in an **inter-apartment** panel | ≥ **40** | `gost_12504_2015` | cl. 6.8.2 | verified | the only dimensional rule about a party wall found in any product standard. |

**External panels — ГОСТ 11024-2012 cl. 6.1.1:** thickness is a **rule, not a
series** — *"recommended to be multiples of 10, 20 or 50 mm"*, referred to the
modular-coordination standard ГОСТ 28984. Every multiple of 10 is even, so **the
rule itself guarantees the even property.** cl. 6.2.1 sets the minimum nominal
thickness of the load-bearing layer of a two-layer bearing panel at **80 mm**
(heavy concrete) / **100 mm** (lightweight). Marking encodes thickness in whole
centimetres (cl. 5.1.2), which reinforces it.

**The historical rupture, and why it matters.** The predecessor **ГОСТ 11024-84
Table 1** gave external-panel coordination thicknesses on **two** modules: М/2
(200, 250, 300, 350, 400) and **М/4 = 25 mm** — 200, **225**, 250, **275**, 300,
**325**, 350, **375**, 400, with a note preferring the М/4 series for layered
panels. **That is where 375 mm comes from, and it is systematically odd on the
odd multiples of 25.** ГОСТ 11024-2012 **abolished** the М/4 series in favour of
"multiples of 10, 20 or 50". Since Azerbaijan's register lists the **2012**
edition, the odd М/4 series is *not* the one in force there. This is a genuine
piece of luck and it should be recorded, because a reader who reaches for the 1984
table will reintroduce exactly the DIN-4172-shaped defect that killed DE.

**On the ticket's `80 / 140 / 160`.** All three are real members of ГОСТ 12504-80
Table 1 — so the values are normative. But the standard offers **13** permitted
thicknesses and never says that large-panel housing uses these three. **The
selection is a series-album (типовой проект) decision, not a GOST decision**, and
series albums are not published norms. So: values `verified`, selection
`reported`. Do not present "80 / 140 / 160" as *the* panel series.

**Gypsum-concrete partition panels — ГОСТ 9574** (1990 and 2018 editions both
read): **the widely quoted 80 mm is NOT normative.** cl. 1.2.2 (1990) / cl. 4.2.2
(2018) say only that *"the shape and dimensions of panels shall correspond to those
given in the working drawings."* There is no dimension table. 80 mm appears solely
inside a **marking example**. Recorded so nobody cites it as a standard value.

---

## 4. Construction type C — aerated concrete and blocks

The register puts **ГОСТ 21520-89** (small cellular-concrete wall blocks),
**ГОСТ 31360-2007** (unreinforced autoclaved cellular-concrete wall products),
**ГОСТ 25485-89 / ГОСТ 31359-2007** (cellular concretes) and **ГОСТ 6133-99**
(concrete wall stones) in force in Azerbaijan, each by a dated act. **AzDTN 2.17-1
§2 normatively references ГОСТ 25485-89 and ГОСТ 6133-99**, which links them to
the AZ masonry code directly.

### 4.1 Cellular-concrete small blocks — ГОСТ 21520-89, and this is the bad one

**ГОСТ 21520-89 Table 1** does not give one thickness series. It gives **two**, and
they differ by which mortar you lay in:

| Laying method | Block thickness series, mm | Even? |
|---|---|---|
| ordinary **mortar** joints | **200 / 250 / 300** | **YES** |
| **thin-bed glue** joints | **195 / 245 / 295** | **NO — every member is ODD** |

`verified`, ГОСТ 21520-89 Table 1. The glue series is the mortar series minus 5 mm,
because the thin-bed joint is ~2 mm instead of ~10 and the coordination size is
preserved by shrinking the unit. Note 1 to the table additionally permits other
dimensions by agreement between manufacturer and customer, which is how the market
widths arise.

**This is a DIN-4172-shaped defect and it must not be glossed.** Thin-bed glue
laying is the modern default for autoclaved aerated concrete — it is what a Baku
contractor actually does — and **in that mode the normative wall thickness series
is systematically odd.** A single-leaf gazobeton wall is one block wide, so the
block width *is* `t_int`. 195 / 245 / 295 all fail ADR 0004 outright.

### 4.2 The rest of the block family

| field | value_mm | src_key | ref | conf | note |
|---|---|---|---|---|---|
| autoclaved cellular wall products: nominal dimension provisions | **no series at all** | `gost_31360_2007` | cl. 4.2.2 / 4.2.4 | verified | gives **maxima and tolerances only**; actual dimensions are set by agreement. So the standard that replaced GOST 21520-89 for autoclaved products publishes **no** width to cite. |
| aerated external wall panels | **no thickness series** | `gost_11118_2009` | — | verified | thickness appears only inside marking examples (320, 400). Not normative values. |
| concrete wall stone, wall types | widths **288 / 190 / 138** | `gost_6133_99` | cl. 4.5 Table 1 | verified | e.g. 390 × 190 × 188; 288 × 138 × 138. All even. |
| concrete wall stone, **partition** types | width **90** | `gost_6133_99` | cl. 4.5 Table 1 | verified | 590 × 90 × 188, 390 × 90 × 188, 190 × 90 × 188. Even. |
| commercial gazobeton widths 100 / 150 / 200 / 250 / 300 / **375** / 400 | — | — | — | **reported** | manufacturer practice. **375 is ODD**, and §3.2 shows where it came from: the abolished ГОСТ 11024-84 М/4 = 25 mm series. |

### 4.3 Verdict for type C

**Do not ship the aerated-block construction type in v1.** Three independent
reasons, any one sufficient:

1. The standard actually in force for autoclaved products in Azerbaijan
   (ГОСТ 31360-2007) **publishes no width series**, so there is nothing to cite.
2. The standard that does publish one (ГОСТ 21520-89) publishes an **odd** series
   for the laying method the market actually uses.
3. The commercial widths are not normative and include an odd member (375).

If the type is shipped later it must carry an **explicitly enumerated even
subset** — 200 / 250 / 300, mortar-laid, ГОСТ 21520-89 Table 1 — with a `note`
recording that the glue-laid 195/245/295 series was excluded *because it is odd*,
or someone will "correct" it back in. The concrete-stone family (ГОСТ 6133-99,
widths 90 / 138 / 190 / 288) is entirely even and is the safer block family if one
is wanted.

---

## 5. Construction type D — monolithic reinforced concrete

**AzDTN 2.16-1** *"Beton və dəmir-beton konstruksiyalar. Layihələndirmə
normaları"* (approved by Collegium decision No. 02 of 15 April 2015; 2018 new
redaction; supersedes СНиП 2.03.01-84\*). Read first-hand, 126 pp.

**It states no minimum wall thickness.** I grepped the extracted text for every
form of *qalınlıq* (thickness) near *divar* (wall). What it gives is:

| field | value_mm | src_key | ref | conf | note |
|---|---|---|---|---|---|
| concrete cover, single-layer light/cellular concrete of class ≤ B7.5 | ≥ 20 | `azdtn_2_16_1` | cl. 10.3.2 area | verified | |
| concrete cover, external wall panels without a facing layer | ≥ 25 | `azdtn_2_16_1` | cl. 10.3.2 area | verified | **ODD**, but it is a cover, not a wall thickness. |
| vertical bar spacing in RC walls | ≤ 2t and ≤ 400, where t is the wall thickness | `azdtn_2_16_1` | cl. 10.3.8 | verified | thickness appears only as a *parameter*. |
| walls reinforced symmetrically at both faces with transverse ties | — | `azdtn_2_16_1` | cl. 10.4.3 | verified | this is what bounds thickness from below **indirectly**: two curtains at 20–25 mm cover cannot live in much under ~140–160 mm. |
| **minimum wall thickness** | **none published** | `azdtn_2_16_1` | — | — | stated as a negative finding, first-hand. |

The number the industry quotes comes from a **Russian** code with no Azerbaijani
counterpart:

| field | value_mm | src_key | ref | conf | note |
|---|---|---|---|---|---|
| monolithic wall thickness, *recommended* | **160** | `sp_430_2018` | cl. 5.2.11 | verified (as an SP value) | phrased *"рекомендуется … не менее 0,16 м"* — a recommendation, not a prohibition; makes **no** internal/external distinction; **not an Azerbaijani instrument**. |
| 180 / 200 as "typical" | — | — | — | **refuted as normative** | neither value appears in SP 430. They are practice, and they are what §7's acoustic arithmetic actually forces. |

**Catalogue, type D:**

| field | value_mm | conf | note |
|---|---|---|---|
| `t_int` (non-load-bearing) | **160** | engine_choice | SP 430's recommended floor; no AZ source. |
| `t_int_bearing` | **200** | engine_choice | what the acoustic calculation demands with margin. |
| `t_ext` structural leaf | **200** | engine_choice | |
| `t_ext` total, insulated | **300** | engine_choice | 200 + 80 + 20; same `Dd` gap as §2.4. |
| `t_party` | **200** | derived | see §7 — 160 mm computes to exactly the requirement with zero margin and loses it to the flanking correction. |

All even. All `engine_choice` or `derived`. **None of these may be labelled
`verified`, and none may be presented as an Azerbaijani requirement.**

---

## 6. Construction type E — sawn natural stone. Not in the ticket, and it should be

Azerbaijan's commonest low- and mid-rise wall material is **sawn limestone block**
(*ağ daş*), not brick. The register puts **ГОСТ 4001-84** *and* its Azerbaijani
adoption **AZS 476–2011** in force. I read GOST 4001-84 first-hand; AZS 476-2011 is
sold, not published, and was not obtained.

| field | value_mm | src_key | ref | conf | note |
|---|---|---|---|---|---|
| stone type I | 390 × 190 × 188 | `gost_4001_84` | Table 1 | verified | |
| stone type II | 490 × 240 × 188 | `gost_4001_84` | Table 1 | verified | |
| stone type III | 390 × 190 × 288 | `gost_4001_84` | Table 1 | verified | |
| `t_int` | **190** | `gost_4001_84` | Table 1 (type I/III width) | derived | one stone on its bed. |
| `t_int_bearing` / `t_ext` leaf | **240** | `gost_4001_84` | Table 1 (type II width) | derived | |
| `t_ext` (stone laid on its length) | **390** | `gost_4001_84` | Table 1 | derived | |

All even. **Caveat:** GOST 4001-84 has been superseded in the Russian system by
GOST 4001-2013, whose text I could not obtain. The AZ register lists the **1984**
edition, which is the one read — so for Azerbaijan this is the right edition, and
that is a happy accident rather than a plan.

---

## 7. The party wall — `t_party`

### 7.1 The Azerbaijani requirement, verified

**Acoustic — AzDTN 2.7-2** *"Yaşayış binaları. Layihələndirmə normaları"*
(Baku 2021; Collegium decision No. 03 of 30.11.2021; State Register no.
15202111300003; supersedes СНиП 2.08.01-89\*; scope: multi-apartment residential
up to 75 m). Read first-hand.

- **cl. 9.22 — the airborne sound-insulation index of inter-apartment walls and
  partitions shall be not less than 50 dB.** `verified`.
  *The Russian SP 51.13330.2011 Table 2 row 7 says **52 dB** for the same wall.
  Azerbaijan's number is lower. Use 50.*
- cl. 9.25 — sanitary fixtures and pipework may not be fixed directly to
  inter-apartment walls, nor to walls and partitions separating habitable rooms.
  `verified`.

**Fire — AzDTN 2.7-2 cl. 7.1.6 and Table 3.** `verified`:

| Element | Fire-resistance limit / hazard class (buildings of fire-resistance degree I–III, class C0/C1) |
|---|---|
| inter-apartment **wall** (*mənzilarası divar*) | REI 30, K0 |
| inter-apartment **partition** (*mənzilarası arakəsmə*) | EI 30, K0 |
| inter-section wall / partition | REI 45, K0 / EI 45, K0 |
| wall / partition separating outside-apartment corridors from other spaces | REI 45, K0 / EI 45, K0 |

- cl. 7.1.6 also requires inter-section and inter-apartment walls and partitions to
  be **solid — no windows and no doors**.
- **cl. 7.1.7 — the fire-resistance limit of inter-room partitions is not
  normalised.** `verified`. So `t_int` inside a dwelling has no fire driver at all.

### 7.2 No code publishes a party-wall thickness. It is derived, and that must be said

Neither AzDTN 2.7-2 nor AzDTN 2.17-1 nor AzDTN 2.16-1 states a millimetre
thickness for the party wall. The requirement is a **performance** requirement
(50 dB, EI/REI 30, K0, solid), and the thickness is an engineering consequence.
The same negative result was confirmed across the Russian corpus (SP 51.13330.2011,
SP 275.1325800.2016, SP 23-103-2003): none contains an Rw-versus-thickness lookup
table; SP 275 gives a **calculation procedure** in which thickness is an input.

**Derived, by the SP 275.1325800.2016 §9.1 method** (mass law `R_B = 20·lg(m_э) − 12`,
critical frequency `f_B = 29000/h` for γ ≥ 1800 kg/m³, then the ISO 717 reference-curve
shift). The implementation was validated against SP 275's own worked example
(100 mm, γ = 2300 → the code states `f_B` = 315 Hz and `R_B` = 35, reproduced exactly).
**These are our numbers, not published ones — `conf: derived`:**

| Construction | Rw (own), dB | vs AZ 50 dB |
|---|---|---|
| brick 120 + 15 plaster both sides | 49 | **fails** |
| brick 250 + 15 plaster both sides | 52 | passes |
| RC 140 bare | 51 | marginal |
| RC 160 bare | 52 | passes, no margin |
| RC 180 bare | 52 | passes |
| RC 200 bare | 52 | passes |
| RC panel 120 bare | 48 | **fails** |
| aerated concrete γ 500, 250 + 10 plaster both sides | 48 (SP 275's own worked example) | **fails** |

SP 275 further mandates a flanking-transmission correction, including a stated
**−1 dB for monolithic-concrete buildings**, which is what removes 160 mm's
zero margin.

**Conclusion, and it is an engine decision:** `t_party` = **250 mm** in brick and
**200 mm** in monolithic. A 120 mm half-brick party wall and a 120 mm RC panel
party wall both fail the Azerbaijani 50 dB requirement by calculation, and no
amount of "it is what gets built" changes that. This is precisely the
production-fidelity call CLAUDE.md asks for.

---

## 8. Even-millimetre verdict

**The rule (ADR 0004, ADR 0001):** every wall thickness must be an even number of
millimetres, so that `erode(rect, t_int/2)` and tier 1's `t_party/2` stay integral.

**Per construction type — is the sourced series entirely even?**

| Type | Sourced series | Entirely even? | Source of the answer |
|---|---|---|---|
| **A — fired brick masonry** | 120 / 250 / 380 / 510 (/640) | **YES**, and even *by construction*: `t(n) = 130n − 10` | `azdtn_2_17_1` cl. 4.3, 5.2 n.3, 6.9, 9.7; `gost_530_2012` Table 3 |
| **B1 — brick panels** | **85** / 140 / 180 / 270 | **NO — 85 mm is ODD** | `azdtn_2_17_1` cl. 8.24 |
| **B2 — RC internal panels** | 60 … 300 step **20** | **YES**, by construction: the module is М/5 = 20 mm | `gost_12504_80` cl. 2.2 Table 1 |
| **B3 — RC external panels** | "multiples of 10, 20 or 50 mm" | **YES**, by construction: every multiple of 10 is even | `gost_11024_2012` cl. 6.1.1 |
| **C1 — cellular block, mortar-laid** | 200 / 250 / 300 | **YES** | `gost_21520_89` Table 1 |
| **C2 — cellular block, glue-laid** | **195 / 245 / 295** | **NO — every member is ODD** | `gost_21520_89` Table 1 |
| **C3 — autoclaved cellular products** | *no series published* | **N/A — nothing to check** | `gost_31360_2007` cl. 4.2.2 / 4.2.4 |
| **C4 — concrete wall/partition stones** | widths 90 / 138 / 190 / 288 | **YES** | `gost_6133_99` cl. 4.5 Table 1 |
| **D — monolithic RC** | 160 / 200 | **YES**, but every value is `engine_choice` — we chose them even. That is not the same as finding an even published series. | `sp_430_2018` cl. 5.2.11 (RU, recommendation only) |
| **E — sawn natural stone** | widths 190 / 240 (length 390) | **YES** | `gost_4001_84` Table 1 |
| **— gypsum partition plates** | 80 / 100 | **YES** | `gost_6428_83` Table 1 |

### The odd values, named plainly, not rounded away

1. **85 mm — AzDTN 2.17-1 cl. 8.24, quarter-brick internal brick panel.** Real,
   current, Azerbaijani, odd. **Avoidable:** the same clause restricts it to
   partitions and offers 140 mm alongside. Exclude the member; do not round it to
   84 or 86, and do not drop it silently. The Russian SP 15.13330.2020 cl. 9.28
   carries the identical 8,5 / 14 / 18 / 27 cm series — both descend from
   СНиП II-22-81\* — so this is not a translation artefact.
2. **195 / 245 / 295 mm — ГОСТ 21520-89 Table 1, cellular blocks laid on thin-bed
   glue.** This is the serious one. Thin-bed glue is the *modern default* for
   autoclaved aerated concrete, a single-leaf gazobeton wall is one block wide, so
   the block width **is** `t_int` — and in that laying mode **the whole normative
   series is odd.** Structurally the same failure that killed the German profile,
   and the reason §4.3 recommends not shipping the block type.
3. **375 mm — commercial gazobeton width.** Odd. §3.2 traces its pedigree: the
   abolished ГОСТ 11024-84 М/4 = 25 mm coordination series, whose odd multiples
   were 225 / 275 / 325 / 375. ГОСТ 11024-2012 — the edition Azerbaijan lists —
   replaced it with "multiples of 10, 20 or 50". Exclude 375 and record why, or a
   later reader will reintroduce the whole М/4 series.
4. **219 / 229 mm — ГОСТ 530-2012 Table 3 ceramic-stone heights.** Odd, but they
   are **course heights, not wall thicknesses**, and never reach `t_int`. Recorded
   so nobody later mistakes them for wall dimensions.
5. **25 mm cover** (`azdtn_2_16_1`), **35 mm facing** (`azdtn_2_17_1` cl. 4.4),
   **367 / 195 mm** fractional stone *lengths* (`gost_4001_84` Table 1). Odd, and
   none of them is a wall thickness or an input to `t/2`.

### Verdict

**For the catalogue recommended in §13 — types A, D, E, plus the brick-panel and
RC-panel rows — every shipped thickness is an even number of millimetres. ADR 0004
holds.**

But it holds **only because two real, published, currently-applicable odd series
are deliberately excluded** (the 85 mm brick-panel member, and the entire glue-laid
cellular-block series). That exclusion is a decision, not a discovery, and it must
be recorded in the `note` field of the affected construction types in
`room-constraints.json`. If it is not recorded, it will be undone.

---

## 9. mod-250 residues (ADR 0007 raw material)

ADR 0007 requires `minimum_mm + t_int ≡ 0 (mod grid_mm)` for **every** internal
wall thickness the profile offers. At the v1 grid of 250 mm, admissible minima are
those `≡ (−t_int) mod 250`.

### Every sourced candidate `t_int`

| `t_int` | where it comes from | `(−t_int) mod 250` | first six admissible minima, mm |
|---|---|---|---|
| 60 | RC internal panel, non-load-bearing floor (`gost_12504_80` cl. 2.4) | **190** | 1690, 1940, 2190, 2440, 2690, 2940 |
| 80 | RC internal panel (`gost_12504_80` T1); gypsum plate (`gost_6428_83` T1) | **170** | 1670, 1920, 2170, 2420, 2670, 2920 |
| 90 | concrete partition stone (`gost_6133_99` T1) | **160** | 1660, 1910, 2160, 2410, 2660, 2910 |
| 100 | RC internal panel, load-bearing floor; gypsum plate | **150** | 1650, 1900, 2150, 2400, 2650, 2900 |
| **120** | **half-brick masonry partition — RECOMMENDED** | **130** | **1630, 1880, 2130, 2380, 2630, 2880** |
| 138 | concrete wall stone (`gost_6133_99` T1) | **112** | 1612, 1862, 2112, 2362, 2612, 2862 |
| 140 | brick panel, half-brick (`azdtn_2_17_1` 8.24); RC panel | **110** | 1610, 1860, 2110, 2360, 2610, 2860 |
| 160 | monolithic RC (`engine_choice`); RC panel | **90** | 1590, 1840, 2090, 2340, 2590, 2840 |
| 180 | brick panel, two-layer (`azdtn_2_17_1` 8.24); RC panel | **70** | 1570, 1820, 2070, 2320, 2570, 2820 |
| 190 | sawn stone, one stone (`gost_4001_84` T1); concrete stone | **60** | 1560, 1810, 2060, 2310, 2560, 2810 |
| 200 | monolithic RC; RC panel; cellular block mortar-laid | **50** | 1550, 1800, 2050, 2300, 2550, 2800 |
| 220 | RC panel (`gost_12504_80` T1) | **30** | 1530, 1780, 2030, 2280, 2530, 2780 |
| 240 | sawn stone type II (`gost_4001_84` T1); RC panel | **10** | 1510, 1760, 2010, 2260, 2510, 2760 |
| 250 | one-brick internal bearing; cellular block mortar-laid | **0** | 1500, 1750, 2000, 2250, 2500, 2750 |
| 260 | RC panel (`gost_12504_80` T1) | **240** | 1740, 1990, 2240, 2490, 2740, 2990 |
| 270 | brick panel, one brick (`azdtn_2_17_1` 8.24) | **230** | 1730, 1980, 2230, 2480, 2730, 2980 |
| 280 | RC panel (`gost_12504_80` T1) | **220** | 1720, 1970, 2220, 2470, 2720, 2970 |
| 288 | concrete wall stone (`gost_6133_99` T1) | **212** | 1712, 1962, 2212, 2462, 2712, 2962 |
| 300 | RC panel (`gost_12504_80` T1); cellular block mortar-laid | **200** | 1700, 1950, 2200, 2450, 2700, 2950 |

*(The odd candidates 85, 195, 245, 295 and 375 are excluded by ADR 0004 before this
arithmetic is reached, and are not listed.)*

### Which candidates can coexist in one minima table — none of them

Two `t_int` values share a residue class **iff they differ by an exact multiple of
250**. Computed over all 19 candidates above:

```
pairs sharing a residue class among sourced t_int candidates:  []
```

**Empty. This confirms the coordinator's independent result — against the actual
sourced series, not a generic candidate set.** Three structural reasons, worth
stating because they mean the answer will not change if more sources turn up:

- The **brick** series steps by **130** (`130n − 10`). `gcd(130, 250) = 10`, so two
  members return to a common residue only every 25 steps — a 3.3 m wall.
- The **RC internal panel** series steps by **20** (`gost_12504_80`, module М/5).
  250 is not a multiple of 20, so **no two members of that 13-value series can ever
  share a residue class.** The one series rich enough to offer a choice is exactly
  the one whose module forbids it.
- The **stone**, **concrete-stone** and **block** widths are isolated values rather
  than progressions, and none lands 250 mm from another.

For completeness, coincidences do exist between an internal and an *external*
thickness — (140, 390), (250, 500), (260, 510) — but `t_ext` and `t_party` never
enter the ADR 0007 congruence, so these are informational only.

### How many distinct `t_int` the AZ profile genuinely needs

**One, if the profile is to have a single dimensional-minima table.** That is the
direct consequence of the empty pair list: any second `t_int` lands in a different
residue class, and every published minimum would have to be restated for it.

Three coherent shapes exist. This partial does not choose between them:

1. **One `t_int` for the whole profile.** Recommended value **120 mm** (half-brick),
   fixing the minima residue class at **130 mod 250** — minima 1630, 1880, 2130,
   2380, 2630, 2880 … Simplest, and the type with the most AZ-verified values
   behind it.
2. **Minima keyed by construction type.** The profile ships `brick`, `monolithic`,
   `stone` … each with its own `t_int` *and its own minima table*. ADR 0007 is then
   satisfied per type. Cost: N copies of every dimensional minimum, and a Plan must
   carry its construction type for life as well as its region — an extension of
   `profile_carried_for_life`, which today pins only the region id.
3. **Change the grid.** ADR 0007 explicitly leaves this open and explicitly says its
   arithmetic changes with the grid. A 10 mm grid divides every difference in the
   table above; a 50 mm grid divides all but 138 and 288. Both are far finer than
   ADR 0001's 250 mm and the solve-time cost is unmeasured.

One observation to hand on: **`t_int = 250` is the only candidate with residue 0**,
i.e. the only one under which round multiples of 250 (2000, 2250, 2500) are
admissible minima. That is not an argument for it — a 250 mm internal partition is
a one-brick load-bearing wall, absurd as a bedroom partition — but it is exactly
why the placeholder table's round numbers looked natural and were wrong.

---

## 10. Sanity check against the Swiss corpus

Not a source. The corpus (`experiments/corpus-smoke/wall_thickness_swiss.py`,
199 210 WALL separators) has **no module**, so it cannot supply AZ values. What it
supplies is a plausibility band: p25 109, p50 169, p75 267, p95 440 mm,
near-continuous 50–600.

| AZ value | in 50–600? | position |
|---|---|---|
| 60, 80, 90, 100 | yes | below p25 (109) — thin, but real partition territory |
| 120 | yes | just above p25 — a very ordinary partition |
| 138, 140, 160 | yes | between p25 and p50 (169) |
| 180, 190, 200, 220, 240 | yes | between p50 and p75 (267) |
| 250, 260, 270, 280, 288, 300 | yes | around and just above p75 |
| 380, 390 | yes | between p75 and p95 (440) |
| 500 (`t_ext` total), 510 | yes | above p95 — plausible for an insulated or 2-brick external wall |
| **640** | **NO — exceeds 600** | **FLAGGED.** The `n = 5` member of the brick series lies outside the corpus range entirely. Arithmetically correct and normatively supportable, but nothing in the corpus looks like it. **Do not ship 640.** |

640 mm is the only flagged value. Everything else sits inside the range of real
surveyed walls, which is the only thing the corpus is entitled to tell us.

---

## 11. What could NOT be obtained

Stated plainly, because a claim must not outrun its source.

1. **AZS 481-2011** *Keramik kərpic və daşlar* — Azerbaijan's own ceramic-brick
   standard, and the instrument AzDTN 2.17-1 cl. 2 actually references for brick
   dimensions. Sold by the national standards body, not published. **The brick
   module is therefore cited to ГОСТ 530-2012** — read in full, and separately
   confirmed in force in Azerbaijan by the official register — **not to
   AZS 481-2011. They are not the same document.**
2. **AZS 476-2011** *Dağ süxurlarından divar daşları* — same situation. Stone
   dimensions cited to ГОСТ 4001-84 instead, which the register also lists.
3. **AZS 534-2011** *Divar materialları* — referenced by AzDTN 2.17-1 cl. 2; not
   obtained. Test methods, so nothing dimensional is believed lost.
4. **Baku's heating degree-days `Dd`** — needed to turn AzDTN 2.12-4\* Table 4's
   `R_req = 0.00035·Dd + 1.4` into a citable insulation thickness. The
   construction-climatology norm (AzDTN 2.1-1 family) was not obtained. **This is
   the single gap that blocks a defensible `t_ext` *total*.** The structural-leaf
   values are unaffected.
5. **ГОСТ 4001-2013** — the current Russian edition of the stone standard. Not
   obtained as free full text. Immaterial for Azerbaijan, whose register lists the
   **1984** edition, which is the one read.
6. **МСН 2.04-03-2005** *Защита от шума* and **МСП 2.04-102-2005** — in force in
   Azerbaijan as authentic translations (Committee order No. 59 of 2008-07-14,
   effective 2008-09-01). The PDFs are on `arxkom.gov.az`, but their embedded fonts
   carry no ToUnicode map, so **Cyrillic body text does not extract** and
   clause-level values would need OCR. Not needed in the end: **AzDTN 2.7-2
   cl. 9.22 supplies the 50 dB requirement directly, first-hand.**
7. **Cabinet of Ministers Decision No. 217 of 1992-04-15** itself. Its existence,
   date, number and effect are attested by the official register (read first-hand),
   but the decision's own text was not read.
8. **A mortar-joint thickness from an Azerbaijani source.** The 12 mm bed / 10 mm
   vertical figures are Russian (`sp_70_2012` cl. 9.2.4). They are used only to
   *re-derive* a series that ГОСТ 530-2012 Table 3 already lists independently, so
   nothing rests on them alone.
9. **An Rw-versus-thickness lookup table.** None exists in SP 51.13330.2011,
   SP 275.1325800.2016 or SP 23-103-2003 — checked. Party-wall thickness is
   therefore necessarily `derived`, never `verified`, in any region profile.
10. **A published minimum wall thickness for monolithic RC in Azerbaijan.**
    Confirmed absent from AzDTN 2.16-1 first-hand. This is a **negative finding,
    not a gap** — the document was read; it simply does not contain one.

### Provenance of the reading, so the labels can be audited

- **Read first-hand by the lead of this slice:** `azdtn_2_17_1`, `azdtn_2_7_2`,
  `azdtn_2_16_1`, `azdtn_2_12_4`, `az_register_2026`, `gost_530_2012`,
  `gost_379_2015`, `gost_4001_84`, `gost_6428_83`, `sp_15_2020`, `sp_70_2012`.
- **Read within this session by a delegated research agent, with clause text and
  URL returned:** `gost_12504_80`, `gost_12504_2015`, `gost_11024_2012`,
  `gost_11024_84`, `gost_21520_89`, `gost_31360_2007`, `gost_11118_2009`,
  `gost_6133_99`, `gost_9574`, `sp_430_2018`, `sp_275_2016`, `sp_51_2011`.
- **Not read by anyone:** everything in items 1–3 and 5–7 above.

---

## 12. `sources` block

Same shape as the `sources` object in `data/standards/room-constraints.json`.

```json
{
  "azdtn_2_17_1": {
    "title": "AzDTN 2.17-1 — Daş və armaturlanmış daş konstruksiyalar. Layihələndirmə normaları (Masonry and reinforced masonry structures. Design norms)",
    "issuer": "Azərbaycan Respublikasının Dövlət Şəhərsalma və Arxitektura Komitəsi (State Committee on Urban Planning and Architecture of the Republic of Azerbaijan)",
    "date": "Baku 2016, 63 pp.; approved by Collegium decision No. 05 of 2016-11-21; in force from 2016-12-13; State Register of Legal Acts no. 15201611210005; publication code AzDŞAK-TN/Q No. 0021-2016",
    "url": "https://arxkom.gov.az/qanunvericilik/normativler/insaat-konstruksiyalar-sistemi/das-ve-armaturlanmis-das-konstruksiyalar-layihelendirme-normalari",
    "licence": "Published free of charge by the issuing authority as a RƏSMİ NƏŞR (official publication). No open licence is granted; treat as read-only. Do not redistribute the PDF.",
    "force": "statutory",
    "force_note": "A technical normative legal act registered in Azerbaijan's State Register of Legal Acts. Its cover page states that from its entry into force the legal force of СНиП II-22-81* on the territory of the Republic of Azerbaijan is suspended. Adopted for the first time.",
    "reusable": false
  },
  "azdtn_2_7_2": {
    "title": "AzDTN 2.7-2 — Yaşayış binaları. Layihələndirmə normaları (Residential buildings. Design norms)",
    "issuer": "Azərbaycan Respublikasının Dövlət Şəhərsalma və Arxitektura Komitəsi",
    "date": "Baku 2021; State Register of Legal Acts no. 15202111300003; terminated the legal force of СНиП 2.08.01-89* in Azerbaijan on 2021-11-30",
    "url": "https://arxkom.gov.az/qanunvericilik/normativler/binalarin-muhendis-sistemleri/zhilye-zdaniya",
    "licence": "Free official publication; no open licence. Do not redistribute the PDF.",
    "force": "statutory",
    "force_note": "The AZ counterpart of SNiP 31-01-2003 / SP 54.13330. Scope: newly built multi-apartment residential buildings up to 75 m. Supplies the party-wall performance requirements (cl. 9.22 airborne sound insulation index >= 50 dB; Table 3 fire limits) but no thickness. Any value previously sourced from СНиП 2.08.01-89* is SUPERSEDED in Azerbaijan, not merely aged.",
    "reusable": false
  },
  "azdtn_2_16_1": {
    "title": "AzDTN 2.16-1 — Beton və dəmir-beton konstruksiyalar. Layihələndirmə normaları (Concrete and reinforced concrete structures. Design norms)",
    "issuer": "Azərbaycan Respublikasının Dövlət Şəhərsalma və Arxitektura Komitəsi",
    "date": "Approved by Collegium decision No. 02 of 2015-04-15; new redaction Baku 2018, 126 pp.; supersedes СНиП 2.03.01-84*",
    "url": "https://arxkom.gov.az/qanunvericilik/normativler/insaat-konstruksiyalar-sistemi/beton-ve-demir-beton-konstruksiyalar-layihelendirme-normalari",
    "licence": "Free official publication; no open licence. Do not redistribute the PDF.",
    "force": "statutory",
    "force_note": "Cited here mainly for a NEGATIVE finding, established first-hand: it publishes no minimum wall thickness for monolithic reinforced concrete, only cover (20 / 25 mm) and reinforcement-spacing rules (cl. 10.3.8: vertical bar spacing <= 2t and <= 400 mm).",
    "reusable": false
  },
  "azdtn_2_12_4": {
    "title": "AzDTN 2.12-4* — Binaların istilik mühafizəsi. Layihələndirmə normaları (Thermal protection of buildings. Design norms), new redaction",
    "issuer": "Azərbaycan Respublikasının Dövlət Şəhərsalma və Arxitektura Komitəsi",
    "date": "Approved by Collegium decision MİHO/2.1-3.2-2022-4 of 2022-06-10; in force from 2022-06-10; State Register of Legal Acts no. 15202206100224; new redaction Baku 2025, 64 pp.",
    "url": "https://arxkom.gov.az/qanunvericilik/normativler/muhendis-sistemleri/azdtn-212-4-binalarin-istilik-muhafizesi-layihelendirme-normalari",
    "licence": "Free official publication; no open licence. Do not redistribute the PDF.",
    "force": "statutory",
    "force_note": "Suspends the legal force of СНиП II-3-79* in Azerbaijan. Table 4 with formula (1) gives R_req = a*Dd + b; for residential walls a = 0.00035, b = 1.4, with tabulated anchors 2.1 / 2.8 / 3.5 m2*degC/W at Dd = 2000 / 4000 / 6000. It supplies no wall thickness, so any external-wall total derived from it is an engine choice.",
    "reusable": false
  },
  "az_register_2026": {
    "title": "Azərbaycan Respublikasında qüvvədə olan şəhərsalma və tikintiyə dair normativ sənədlərin SİYAHISI (List of urban-planning and construction normative documents in force in the Republic of Azerbaijan), status at 2026-01-01",
    "issuer": "Azərbaycan Respublikasının Fövqəladə Hallar Nazirliyi (Ministry of Emergency Situations) and Azərbaycan Respublikasının Dövlət Şəhərsalma və Arxitektura Komitəsi",
    "date": "Baku 2026, 209 pp.; publication code DŞAK-K No. 0009-2026",
    "url": "https://arxkom.gov.az/qanunvericilik/normativler",
    "licence": "Explicitly NOT reusable — its front matter forbids reproduction or distribution, in whole or in part, without the permission of both issuing bodies. Cite individual entries only; never reproduce its listing.",
    "force": "statutory_guidance",
    "force_note": "The official index of what is in force. Its preamble records Cabinet of Ministers Decision No. 217 of 1992-04-15, under which all former-USSR construction normative documents were retained in force in Azerbaijan. Used here to establish which GOSTs apply in Azerbaijan, in which EDITION, and by which dated act.",
    "reusable": false
  },
  "gost_530_2012": {
    "title": "ГОСТ 530-2012 — Кирпич и камень керамические. Общие технические условия (Ceramic brick and stone. General specifications)",
    "issuer": "Interstate Council MNTKS (protocol No. 40 of 2012-06-04); put into force in the Russian Federation by Rosstandart order No. 2148-st of 2012-12-27; supersedes GOST 530-2007",
    "date": "2012, in force 2013-07-01",
    "url": "https://meganorm.ru/Data2/1/4293782/4293782555.htm",
    "licence": "Interstate standard text, freely republished. Individual values cited; the standard's own tables are NOT reproduced.",
    "force": "voluntary_standard",
    "force_note": "Its preface records that Azerbaijan (country code AZ), through the State Committee on Urban Planning and Architecture, VOTED FOR ADOPTION, and Azerbaijan's own register separately lists it in force. Azerbaijan additionally has AZS 481-2011 (an adoption of GOST 530-2007) which could not be obtained. An adoption vote is not domestic enforceability and no such claim is made here.",
    "reusable": true
  },
  "gost_379_2015": {
    "title": "ГОСТ 379-2015 — Кирпич, камни, блоки и плиты перегородочные силикатные. Общие технические условия",
    "issuer": "Interstate Council (protocol No. 74-P of 2015-01-30); Rosstandart order No. 246-st of 2015-04-09",
    "date": "2015",
    "url": "https://base.garant.ru/71276714/",
    "licence": "Interstate standard text, freely republished (definitions accessible; the dimensional annex is paywalled on this host).",
    "force": "voluntary_standard",
    "force_note": "Preface records Azerbaijan (AZ, Azstandart) as voting for adoption; the AZ register lists it in force, replacing GOST 379-95. Corroborates the 250 x 120 module in a second unit family.",
    "reusable": true
  },
  "gost_4001_84": {
    "title": "ГОСТ 4001-84 — Камни стеновые из горных пород. Технические условия (Natural rock wall blocks. Specifications)",
    "issuer": "Gosstroy USSR, decree No. 74 of 1984-05-10, in force from 1985-07-01; reissued with Amendment 1 approved by Gosstroy of Russia decree No. 115 of 2000-12-04",
    "date": "1984, am. 2000",
    "url": "https://meganorm.ru/Data2/1/4294853/4294853180.htm",
    "licence": "Soviet-era interstate standard text, freely republished.",
    "force": "voluntary_standard",
    "force_note": "Listed in Azerbaijan's register as in force, alongside its Azerbaijani adoption AZS 476-2011 (not obtained). Superseded in the Russian system by GOST 4001-2013, which was not obtained; Azerbaijan lists the 1984 edition, which is the one read.",
    "reusable": true
  },
  "gost_6428_83": {
    "title": "ГОСТ 6428-83 — Плиты гипсовые для перегородок. Технические условия (Plaster slabs for partitions. Specifications)",
    "issuer": "Gosstroy USSR, decree No. 299 of 1983-11-02, in force from 1985-01-01; supersedes GOST 6428-74",
    "date": "1983",
    "url": "https://meganorm.ru/Data2/1/4294853/4294853235.htm",
    "licence": "Soviet-era standard text, freely republished.",
    "force": "voluntary_standard",
    "force_note": "Listed in Azerbaijan's register as in force by State Committee order No. 09 of 2010-02-01. Table 1 gives partition-plate thicknesses of 80 and 100 mm — both even.",
    "reusable": true
  },
  "gost_12504_80": {
    "title": "ГОСТ 12504-80 — Панели стеновые внутренние бетонные и железобетонные для жилых и общественных зданий. Общие технические условия",
    "issuer": "Gosstroy USSR",
    "date": "1980",
    "url": "https://meganorm.ru/Data2/1/4294816/4294816929.htm",
    "licence": "Soviet-era standard text, freely republished.",
    "force": "voluntary_standard",
    "force_note": "THIS is the edition Azerbaijan's register lists in force — not the Russian GOST 12504-2015. cl. 2.2 Table 1 sets coordination thickness on module M/5 = 20 mm: 60 to 300 in steps of 20, so every member is even by construction. cl. 2.4 sets the minimum at 100 mm load-bearing and 60 mm non-load-bearing.",
    "reusable": true
  },
  "gost_11024_2012": {
    "title": "ГОСТ 11024-2012 — Панели стеновые наружные бетонные и железобетонные для жилых и общественных зданий. Общие технические условия",
    "issuer": "Interstate standard; in force in Azerbaijan by State Committee decision No. 01 of 2013-03-13",
    "date": "2012",
    "url": "https://meganorm.ru/Data2/1/4293774/4293774660.htm",
    "licence": "Interstate standard text, freely republished.",
    "force": "voluntary_standard",
    "force_note": "cl. 6.1.1 states thickness as a RULE, not a series: recommended to be multiples of 10, 20 or 50 mm, referred to GOST 28984 modular coordination — so the even property is guaranteed by the rule itself. cl. 6.2.1 sets the minimum bearing-layer thickness of a two-layer bearing panel at 80 mm (heavy concrete) / 100 mm (lightweight). Its predecessor GOST 11024-84 carried an M/4 = 25 mm series containing the odd values 225 / 275 / 325 / 375, which this edition ABOLISHED.",
    "reusable": true
  },
  "gost_21520_89": {
    "title": "ГОСТ 21520-89 — Блоки из ячеистых бетонов стеновые мелкие. Технические условия",
    "issuer": "Interstate standard; in force in Azerbaijan by State Committee decision No. 01 of 2013-03-13, effective 2013-05-10",
    "date": "1989",
    "url": "https://meganorm.ru/Data2/1/4294821/4294821960.htm",
    "licence": "Soviet-era standard text, freely republished.",
    "force": "voluntary_standard",
    "force_note": "Table 1 gives TWO thickness series by laying method: mortar-laid 200 / 250 / 300 (even) and thin-bed-glue-laid 195 / 245 / 295 (ALL ODD). Note 1 permits other dimensions by agreement. The glue series fails ADR 0004 and is the reason the block construction type is not recommended for v1.",
    "reusable": true
  },
  "gost_31360_2007": {
    "title": "ГОСТ 31360-2007 — Изделия стеновые неармированные из ячеистого бетона автоклавного твердения. Технические условия",
    "issuer": "Interstate standard; in force in Azerbaijan (register entry), replacing the autoclaved part of GOST 21520-89",
    "date": "2007",
    "url": "https://meganorm.ru/Data2/1/4293833/4293833721.htm",
    "licence": "Interstate standard text, freely republished.",
    "force": "voluntary_standard",
    "force_note": "cl. 4.2.2 / 4.2.4 give MAXIMA and tolerances only; actual dimensions are set by agreement between manufacturer and customer. So the standard that replaced GOST 21520-89 for autoclaved products publishes NO width series to cite.",
    "reusable": true
  },
  "gost_6133_99": {
    "title": "ГОСТ 6133-99 — Камни бетонные стеновые. Технические условия",
    "issuer": "Interstate standard; in force in Azerbaijan from 2011-12-30 (register entry); normatively referenced by AzDTN 2.17-1 cl. 2",
    "date": "1999",
    "url": "https://meganorm.ru/Data2/1/4294819/4294819374.htm",
    "licence": "Interstate standard text, freely republished.",
    "force": "voluntary_standard",
    "force_note": "cl. 4.5 Table 1 gives wall-stone widths 288 / 190 / 138 and partition-stone width 90 — all even. The safest block family if a block construction type is ever wanted.",
    "reusable": true
  },
  "gost_11118_2009": {
    "title": "ГОСТ 11118-2009 — Панели из автоклавных ячеистых бетонов для наружных стен зданий. Технические требования",
    "issuer": "Interstate standard; in force in Azerbaijan by State Committee order No. 59 of 2010-05-20",
    "date": "2009",
    "url": "https://meganorm.ru/Data2/1/4293823/4293823725.htm",
    "licence": "Interstate standard text, freely republished.",
    "force": "voluntary_standard",
    "force_note": "Publishes no thickness series; thickness appears only inside marking examples (320, 400). Not normative values.",
    "reusable": true
  },
  "gost_9574": {
    "title": "ГОСТ 9574 — Панели гипсобетонные для перегородок. Технические условия (1990 and 2018 editions)",
    "issuer": "Gosstroy USSR / Interstate standard",
    "date": "1990; 2018",
    "url": "https://meganorm.ru/Data2/1/4294851/4294851970.htm",
    "licence": "Standard text, freely republished.",
    "force": "voluntary_standard",
    "force_note": "NEGATIVE finding: cl. 1.2.2 (1990) / cl. 4.2.2 (2018) say only that the shape and dimensions of panels shall correspond to the working drawings. There is NO dimension table. The widely quoted 80 mm appears solely inside a marking example and must not be cited as a standard value.",
    "reusable": true
  },
  "sp_70_2012": {
    "title": "СП 70.13330.2012 — Несущие и ограждающие конструкции. Актуализированная редакция СНиП 3.03.01-87",
    "issuer": "Ministry of Regional Development / Minstroy of the Russian Federation",
    "date": "2012, with amendments",
    "url": "https://meganorm.ru/Data2/1/4293782/4293782487.htm",
    "licence": "Russian code of practice, freely republished.",
    "force": "recommended",
    "force_note": "RUSSIAN, NOT AZERBAIJANI. Does not appear in Azerbaijan's register. Cited only for cl. 9.2.4 (bed joint 12 mm, vertical joint 10 mm), used to re-derive a series that GOST 530-2012 Table 3 lists independently.",
    "reusable": true
  },
  "sp_15_2020": {
    "title": "СП 15.13330.2020 — Каменные и армокаменные конструкции. СНиП II-22-81*",
    "issuer": "Minstroy of the Russian Federation, order No. 902/pr of 2020-12-30, in force from 2021-07-01",
    "date": "2020, am. 2024",
    "url": "https://meganorm.ru/mega_doc/norm/polozhenie_polozheniya/0/sp_15_13330_2020_svod_pravil_kamennye_i_armokamennye.html",
    "licence": "Russian code of practice, freely republished.",
    "force": "recommended",
    "force_note": "RUSSIAN, NOT AZERBAIJANI. Recorded only because its cl. 9.28 carries the identical 8,5 / 14 / 18 / 27 cm brick-panel series as AzDTN 2.17-1 cl. 8.24 — both descend from СНиП II-22-81* — which is what shows the odd 85 mm value is not a translation artefact.",
    "reusable": true
  },
  "sp_430_2018": {
    "title": "СП 430.1325800.2018 — Монолитные конструктивные системы. Правила проектирования",
    "issuer": "Minstroy of the Russian Federation; introduced for the first time",
    "date": "2018",
    "url": "https://files.stroyinf.ru/Data2/1/4293730/4293730490.htm",
    "licence": "Russian code of practice, freely republished.",
    "force": "recommended",
    "force_note": "RUSSIAN, NOT AZERBAIJANI, and there is NO Azerbaijani counterpart. cl. 5.2.11 RECOMMENDS a wall thickness of not less than 0.16 m, makes no internal/external distinction, and states no other thickness. 180 and 200 mm do not appear in it. Every monolithic value in this partial is therefore engine_choice.",
    "reusable": true
  },
  "sp_275_2016": {
    "title": "СП 275.1325800.2016 — Конструкции ограждающие жилых и общественных зданий. Правила проектирования звукоизоляции",
    "issuer": "Minstroy of the Russian Federation",
    "date": "2016",
    "url": "https://meganorm.ru/Data2/1/4293746/4293746919.htm",
    "licence": "Russian code of practice, freely republished.",
    "force": "recommended",
    "force_note": "RUSSIAN, NOT AZERBAIJANI. Cited only as the CALCULATION METHOD (cl. 9.1) by which the derived Rw figures in section 7 were computed; it publishes no Rw-versus-thickness lookup table. The requirement itself comes from AzDTN 2.7-2 cl. 9.22 (>= 50 dB).",
    "reusable": true
  },
  "azs_481_2011": {
    "title": "AZS 481-2011 (ГОСТ 530-2007) — Keramik kərpic və daşlar. Ümumi texniki şərtlər",
    "issuer": "Azərbaycan Respublikasının Fövqəladə Hallar Nazirliyi (order No. 088, 2011); registered by the State Committee for Standardization, Metrology and Patents, order No. 204 of 2011-12-30",
    "date": "2011, in force in Azerbaijan from 2011-12-30",
    "url": null,
    "licence": "Sold by the national standards body; not published free of charge.",
    "force": "voluntary_standard",
    "force_note": "GAP, and the most consequential one. This is the instrument AzDTN 2.17-1 cl. 2 actually references for ceramic brick dimensions. Its text was NOT obtained, so the brick module is cited to GOST 530-2012 instead. The two are not the same document and no value claims otherwise.",
    "reusable": false
  },
  "azs_476_2011": {
    "title": "AZS 476-2011 (ГОСТ 4001-84) — Dağ süxurlarından divar daşları. Texniki şərtlər",
    "issuer": "Azərbaycan Respublikasının Fövqəladə Hallar Nazirliyi (order No. 088, 2011)",
    "date": "2011",
    "url": null,
    "licence": "Sold by the national standards body; not published free of charge.",
    "force": "voluntary_standard",
    "force_note": "GAP. The Azerbaijani adoption of GOST 4001-84. Not obtained; stone dimensions are cited to GOST 4001-84 itself, which the AZ register also lists in force.",
    "reusable": false
  }
}
```

---

## 13. Recommended shipping catalogue

What to write into `data/standards/room-constraints.json` for `AZ`. Every row
carries `src` / `ref` / `conf`. **The merge is owned by another session; this is a
recommendation, not an edit.**

### 13.1 If ADR 0007 forces a single `t_int` — ship `brick` only

This is the recommendation. One construction type, one `t_int`, one minima table.

| field | value_mm | src | ref | conf | note |
|---|---|---|---|---|---|
| `construction_type` | `brick` | — | — | engine_choice | The only type with AZ-verified values for every field, even by construction, and the commonest multi-apartment wall system in Azerbaijan. |
| `t_int` | **120** | `azdtn_2_17_1` | cl. 4.3; Table 29 note 2 (100–250 bracket) | verified | half-brick, bare masonry. Corroborated by `gost_530_2012` Table 3 working width + cl. 3.12. **Fixes the ADR 0007 residue class at 130 mod 250.** |
| `t_int_bearing` | **250** | `azdtn_2_17_1` | cl. 6.9 | verified | one brick. Corroborated by `gost_530_2012` Table 3. |
| `t_ext` (structural leaf) | **380** | `azdtn_2_17_1` | cl. 5.2 note 3; cl. 9.7 | verified | 1.5 brick. |
| `t_ext_total` | **500** | — | — | engine_choice | 380 leaf + 100 insulation + 20 finish. Required because `azdtn_2_12_4` Table 4 asks R >= 2.1 and a 380 brick leaf gives about 0.7. **Blocked on the `Dd` gap (§11 item 4) — flag as provisional.** |
| `t_party` | **250** | `azdtn_2_7_2` | cl. 9.22 (>= 50 dB); Table 3 (REI 30 / EI 30, K0) | derived | one brick. 120 mm computes to 49 dB and fails. No code publishes a party-wall thickness — see §7.2. |

### 13.2 If minima are keyed by construction type — the additional rows

| construction_type | `t_int` | `t_int_bearing` | `t_ext` leaf | `t_ext` total | `t_party` | residue |
|---|---|---|---|---|---|---|
| `brick` | **120** verified | 250 verified | 380 verified | 500 engine_choice | 250 derived | 130 |
| `panel_brick` | **140** verified (`azdtn_2_17_1` 8.24) | 270 verified | 380 verified (8.22) | 500 engine_choice | 270 derived | 110 |
| `panel_rc` | **160** verified (`gost_12504_80` 2.2 T1) | 200 verified | 300 verified (`gost_11024_2012` 6.1.1 rule) | 400 engine_choice | 200 derived | 90 |
| `monolithic` | **160** engine_choice (`sp_430_2018` 5.2.11, RU recommendation) | 200 engine_choice | 200 engine_choice | 300 engine_choice | 200 derived | 90 |
| `stone` | **190** derived (`gost_4001_84` T1) | 240 derived | 240 derived | 400 engine_choice | 240 derived — **acoustics unchecked** | 60 |
| `block` | **DO NOT SHIP** — §4.3 | — | — | — | — | — |

Note that `panel_rc` and `monolithic` share residue 90, because both use
`t_int = 160`. That is the *only* coincidence available, and it comes from choosing
the same number twice rather than from the standards agreeing.

### 13.3 Values that must NOT be shipped

| value | why |
|---|---|
| **85 mm** | ODD. `azdtn_2_17_1` cl. 8.24 quarter-brick panel. Record the exclusion. |
| **195 / 245 / 295 mm** | ODD. `gost_21520_89` Table 1 glue-laid cellular blocks. Record the exclusion. |
| **375 mm** | ODD. Commercial gazobeton width, from the abolished `gost_11024_84` M/4 series. |
| **640 mm** | Even and defensible, but outside the corpus band (§10). |
| **80 / 140 / 160 as "the panel series"** | The values are real members of `gost_12504_80` Table 1, but the *selection* is a series-album choice, not a normative one. Ship the values, never the claim. |
| **510 mm** | Shippable, but label `derived` from `gost_530_2012` Table 3 — it is **absent from AzDTN 2.17-1**, which speaks only of 12 / 25 / 38 / 40 cm. |
