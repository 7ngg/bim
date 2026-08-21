# AZ minima — minimum room areas and minimum clear dimensions

Partial findings for **ticket 25, *The Azerbaijani region profile*, item 2**.
Owns the `statutory_floor` / `market_default` / `accessible` tiers for `AZ` in
`data/standards/room-constraints.json`. **This note does not edit that file.**

Sibling partials under `docs/research/_az-partials/` cover the other items
(thickness catalogue, window ratio, decimal separator, abbreviations, opening
catalogue). The region-invariant ergonomic layer belongs to ticket 19 and is
**not** touched here; where an AZ source hands a number to ergonomics, that is
recorded as a cross-reference, not as a value.

**C8 applies to every number below.** These are dimensional standards with a
citation, not a compliance claim. §4 states exactly what legal force each source
has, and it is the field the acceptance validator must read.

---

## 0. TL;DR

| # | Finding |
|---|---|
| **1** | **The ticket's premise was right, but its source was wrong.** Azerbaijan has its own multi-apartment residential norm — **AzDTN 2.7-2 "Yaşayış binaları. Layihələndirmə normaları"** (Baku, 2021). It is not a SNiP, not an SP, and not folklore. It was read first-hand. |
| **2** | **SNiP 2.08.01-89\* is dead in Azerbaijan, and AzDTN 2.7-2 is the instrument that killed it.** The norm's own cover page states that from its entry into force the legal force of СНиП 2.08.01-89* on Azerbaijani territory is terminated. Read first-hand. So the "Soviet ancestor" the ticket told us to fall back on is *superseded in this region specifically* — it must not be cited as live AZ law. |
| **3** | **`statutory_floor` is honestly non-null for AZ, at `force: statutory`.** AzDTN 2.7-2 cl. 5.7 states minimum room areas in the mandatory register (*az olmamalıdır*, "shall not be less than"), the norm is a registered technical normative legal act, and Art. 14.3 of the Urban Planning and Construction Code makes compliance with normative-document requirements obligatory. This is a genuine legal floor, unlike the UK NDSS. **AZ is therefore the first region on this map with a real consumer for the tier.** |
| **4** | **The floor is areas only. AzDTN 2.7-2 publishes NO intra-apartment clear plan dimensions at all** — and it says why: cl. 5.6 hands room dimensions to *erqonomika*, to the furniture and equipment that must fit. The current Russian norm SP 54.13330.2022 cl. 5.11 makes the identical delegation in near-identical words, so this is the whole family's settled position, not an omission. **The Azerbaijani norm makes ticket 19's ergonomic layer load-bearing by name.** Every plan-dimension minimum in this note therefore comes from a *different* document than the areas do, and §3 says which. |
| **5** | **A second, weaker AZ instrument does publish clear widths** — AzDTN 2.7-3 (individual houses, 2023), also read first-hand, cl. 5.1: habitable room 3.0 m, kitchen 2.6 m, hall 1.4 m, bathroom 1.5 m, WC 0.8 m / 1.2 m. But it binds *fərdi yaşayış evləri* (detached houses), which is **not** the building type this engine draws. Adopting it for apartments is an engine choice, not an inheritance. |
| **6** | **AZ's accessible tier is ВСН 62-91\*, not SNiP 35-01-2001 and not SP 59.13330** — the Russian accessibility corpus the ticket named returns **zero hits** across all 211 pages of Azerbaijan's official in-force list. ВСН 62-91\* was obtained and read first-hand: kitchen **9.0 m² / 2200 mm wide**, WC **1200 × 1600 mm**, full wheelchair turn **1500 mm** (not 1400). **`force: recommended`, never `statutory`** — Azerbaijan invokes it only as a recommendation. §5. |
| **7** | **ADR 0007 arithmetic: the residue classes for the six candidate `t_int` are all distinct, so no single published clear dimension satisfies the rule for two thicknesses.** Six thicknesses ⇒ six different published values per raw source figure. §6 tabulates them. One happy accident: AZ's 1400 mm corridor is *already* admissible at `t_int = 100` (1400 + 100 = 6 × 250). |
| **8** | **The ticket's "classic SNiP numbers" are folklore and three of the six are wrong.** SNiP 2.08.01-89\* was read first-hand: the living room is **14/16 m², not 12**; the kitchen is **8 m², not 6** (the string "6 m²" for a kitchen is not in the document); and **1.4 m is the *передняя*, not the corridor** — the corridor is **0.85 m**. §11.1. The rule that catches this is the ticket's own. |
| **9** | **Most cells are legitimately empty, and that is the finding.** Nine of thirteen area cells and *all six* width cells at `statutory_floor` are `null` — Azerbaijani law fixes habitable-room and kitchen areas and nothing else about a room's plan. **§7A is the consolidated three-tier table**; read the blanks as load-bearing. |
| **10** | **Following the ticket's fallback would have produced two false AZ claims.** We would have published a 2500 mm clear height (AZ requires **2700 mm** nationally) and an 850 mm statutory corridor minimum (AZ **repealed** intra-apartment width minima outright). The second is a legal claim about a rule that no longer exists — the exact C8 violation the tier model warns of. §11.3. |

---

## 0.1 The four questions the merge depends on, answered

**1. Is `statutory_floor` honestly non-null for AZ, and under what `force`?**
**Yes. `force: statutory`, and it is a genuine legal floor.** The chain, every
link read first-hand: AzDTN 2.7-2 cl. 5.7 states the minima in the mandatory
register (*az olmamalıdır*, "shall not be less than");
the norm is a technical normative legal act registered at No. 15202111300003;
Art. 3.0.26 of the Urban Planning and Construction Code (Law 392-IVQ, 2012)
defines such documents as legal acts; **Art. 14.3 makes compliance obligatory**;
and Art. 14.2's annually published SİYAHI lists the norm as in force. §4.
This is materially unlike the UK NDSS (`planning_policy_optional`) — a plan below
these figures does break a rule that exists. **AZ is the first region on this map
where the `statutory_floor` warn has a real consumer.**

**And the force is derived from the clause, not the tier name.** §4.2 gives an
objective rule taken from the AzDTN system's own governing document, which
*requires* mandatory and recommended norms to be textually separated: `az
olmamalıdır` / `edilməlidir` ⇒ `statutory`; `tövsiyə olunur` ⇒ `recommended`.
Every `force` in this note was assigned by reading the verb. Two clauses in the
*same section* of AzDTN 2.7-2 land on opposite sides of it (cl. 5.7 mandatory,
cl. 5.1 recommended), which is the check that the rule is real and not
post-hoc.

**2. Per-tier values, extractable.** §2 (statutory floor), §3 (clear dimensions),
§5 (accessible), §7 (market default), each as
`{room_type, tier, field, value, unit, src_key, ref, conf, force, note}`.
**§7A is the consolidated three-tier table.** Headline figures:

| tier | headline |
|---|---|
| `statutory_floor` | living room **15 m²** (1-room flat) / **16 m²** (2+); bedroom **8 m²**, **10 m²** for two; kitchen **8 m²**; kitchen-niche **5 m²**; clear height **2700 mm**. `force: statutory`. |
| `market_default` | living room 16, bedroom 9 (12 for two), kitchen 9, bathroom 3.2, combined WC/bath 3.8 m²; widths 3000 / 2600 / 1400 / 1500 / 800 mm. `force: recommended`, and **detached-house provenance** — `conf` must degrade on transfer. |
| `accessible` | kitchen **9.0 m² and 2200 mm wide**; WC **1200 × 1600 mm**; wheelchair turn **1500 mm**; door clear **900 mm**. `force: recommended`, **never statutory**. |

**3. Linear minima with grid-aligned values per `t_int`.** §6.2, for
`t_int ∈ {100, 120, 140, 160, 200, 250}` at a 250 mm grid. **Areas in m² are
exempt and are marked so** (§6.3 item 4); **storey heights are exempt too**
(item 5, and this needs an explicit carve-out in ADR 0007); **door clear widths
and wheelchair turning squares are exempt** for the reasons given under the §6.2
table. The residue classes for the six `t_int` are **all distinct**, so no single
published value serves two thicknesses.

**4. What could not be obtained.** §8, stated plainly. The two live gaps are
**Baku market practice / MIDA space standards** (item 2) and the **two
Azerbaijani accessibility instructions of 2001–02** (item 3), which appear to be
unpublished online. Item 10 records a paywalled aggregator **fabricating clause
text**; no value here comes from one.

---

## 1. What was read first-hand, and what was not

`conf: verified` below means read in the primary document named in `src`, in this
session. Nothing else gets that label.

| Document | Obtained | How |
|---|---|---|
| **AzDTN 2.7-2** "Yaşayış binaları. Layihələndirmə normaları", Baku 2021, 28 pp. | **yes** | PDF served directly by the State Committee's own norms register, `arxkom.gov.az`. Text-extracted. |
| **AzDTN 2.7-3** "Fərdi yaşayış evləri. Layihələndirmə normaları", Baku 2023, 12 pp. | **yes** | Same register. Text-extracted. |
| **Şəhərsalma və Tikinti Məcəlləsi** (Law 392-IVQ of 2012-06-29) | **yes** | Official PDF, `fhn.gov.az`. Arts. 3.0.26, 14, 15 read. |
| **SİYAHI** — *"Azərbaycan Respublikasında qüvvədə olan şəhərsalma və tikintiyə dair normativ sənədlərin SİYAHISI (01.01.2026-cı il tarixinə olan vəziyyət), RƏSMİ NƏŞR"*, Ministry of Emergency Situations + State Committee on Urban Planning and Architecture, Bakı 2026, 211 pp. | **yes** | PDF linked from `arxkom.gov.az/qanunvericilik/normativler`. Used to establish what *is* and *is not* in force. |
| **"Əsas müddəalar (Konsepsiya)"** — governing document of the AzDTN system, Azərdövləttikintikom, Baku 1994 | **yes** | Same register. §§3.1–3.6 read; this is where *məcburi* vs *tövsiyə* is defined. |
| **SNiP 2.08.01-89\*** «Жилые здания», Gosstroy printed edition, Moscow 2000 (Изм. 1–4) | **yes** | Scan of the official edition, `files.stroyinf.ru`, corroborated against ГАРАНТ and three independent digitizations. **Superseded in AZ** — read to establish the lineage and to check the ticket's REPORTED figures. §11. |
| **SNiP 31-01-2003** (Gosstroy 2004 print) and **SP 54.13330** editions **2011, 2016, 2022** | **yes** | `meganorm.ru` + two independent full copies of the 2022 text, cross-checked verbatim. Russian, never AZ law. §11.5. |
| **SP 55.13330.2016** «Дома жилые одноквартирные» | **yes** | `meganorm.ru`. Read to locate where the SNiP-family clear widths actually live. §11.5. |
| **ВСН 62-91\*** — Goskomarkhitektura order No. 134 of 1991-10-04, in force 1992-01-01 | **yes** | Full text at `files.stroyinf.ru`. **Azerbaijan's accessibility instrument**, per the SİYAHI. §5. |
| SNiP 35-01-2001, SP 59.13330, SP 137.13330 | see §5, §8 | Russian, never applied in AZ; absent from the SİYAHI. |

**A note on the extraction.** The two AzDTN norm PDFs embed fonts without a
ToUnicode map, so text extraction silently drops Azerbaijani diacritics (ə, ş, ç,
ğ, ı, ö, ü) and Cyrillic entirely. Every Azerbaijani quotation from those two
documents has been re-diacriticised by hand from the stripped extraction. The
**numerals and the grammatical endings that carry the mandatory/recommended
distinction survived extraction intact** and are what the labelling rests on.

The **SİYAHI extracted cleanly**, with both diacritics and Cyrillic intact, which
is what allowed the two critical strings to be read rather than reconstructed:

> «AzDTN 2.7-2 — Yaşayış binaları. Layihələndirmə normaları — **СНиП 2.08.01-89\*
> əvəzinə** — Dövlət Şəhərsalma və Arxitektura Komitəsi Kollegiyasının
> 30.11.2021-ci il tarixli, 03 №-li qərarı ilə təsdiq edilib»  (§2.8, p. 24)

*"in place of СНиП 2.08.01-89\*"*. **СНиП 2.08.01-89\* appears exactly once in the
entire 211-page list — here, as the thing AzDTN 2.7-2 replaced.** It is nowhere
listed as in force. That is an independent, machine-checkable corroboration of the
repeal on AzDTN 2.7-2's own cover page, whose Cyrillic was destroyed by the norm
PDF's font encoding.

---

## 2. `statutory_floor` — AzDTN 2.7-2, clause 5.7

The operative sentence, clause 5.7:

> "Normaların 5.2-ci bəndində göstərilmiş mənzillərdə otaqların sahəsi
> aşağıdakılardan **az olmamalıdır**:"
>
> *"In the apartments identified in cl. 5.2 of these Norms the area of rooms
> **shall not be less than** the following:"*

`az olmamalıdır` is the mandatory register. Compare cl. 5.1 in the same section,
which uses `tövsiyə olunur` ("is recommended") — the norm distinguishes the two
deliberately and the system's governing document requires it to (§4.2).

**Scope: all apartments, not just social housing.** This matters and is easy to
get wrong. The clause binds *"5.2-ci bəndində göstərilmiş mənzillərdə"* — the
apartments identified in cl. 5.2 — and cl. 5.2 is the general room-composition
clause for apartments, with no housing-fund restriction. By contrast the
*recommended* cl. 5.1 **is** restricted, expressly, to *"Dövlət və bələdiyyə
mənzil fondunun yaşayış binalarında"* (state and municipal housing fund), and its
last paragraph hands private-fund apartment sizes to the client.

So Azerbaijan splits it the opposite way round from how one might guess: the
**mandatory** room-area floor applies to *every* apartment, while the
**recommended** total-area bands apply only to public housing. This is the same
position the Russian line reached only in 2022, when SP 54.13330 dropped the
social-fund restriction from its equivalent clause (§11.5) — AZ has had it since
2021.

### Values

Each is a **minimum floor area**, in m². `ref` is the clause. All read first-hand
in AzDTN 2.7-2.

| room_type | tier | field | value | unit | src_key | ref | conf | force | note |
|---|---|---|---|---|---|---|---|---|---|
| living_room | statutory_floor | min_area | 15.0 | m2 | `az_azdtn_2_7_2` | cl. 5.7 | verified | statutory | *ümumi otaq* in a **one-room** apartment (*birotaqlı mənzil*) |
| living_room | statutory_floor | min_area | 16.0 | m2 | `az_azdtn_2_7_2` | cl. 5.7 | verified | statutory | *ümumi otaq* in a **two-or-more-room** apartment |
| bedroom | statutory_floor | min_area | 8.0 | m2 | `az_azdtn_2_7_2` | cl. 5.7 | verified | statutory | *yataq otağı*, single occupancy |
| bedroom_double | statutory_floor | min_area | 10.0 | m2 | `az_azdtn_2_7_2` | cl. 5.7 | verified | statutory | *yataq otağı*, two persons (*iki adama*) |
| kitchen | statutory_floor | min_area | 8.0 | m2 | `az_azdtn_2_7_2` | cl. 5.7 | verified | statutory | *mətbəx* |
| kitchen_zone | statutory_floor | min_area | 6.0 | m2 | `az_azdtn_2_7_2` | cl. 5.7 | verified | statutory | the cooking zone within a *mətbəx-yemək otağı* (kitchen-dining room) |
| kitchen_niche | statutory_floor | min_area | 5.0 | m2 | `az_azdtn_2_7_2` | cl. 5.7 | verified | statutory | *taxça-mətbəx*; **permitted only in one-room apartments** ("yol verilir") |
| wardrobe_entry | statutory_floor | min_area | 2.5 | m2 | `az_azdtn_2_7_2` | cl. 5.7 | verified | statutory | *qarderob* at the entrance of a one-room apartment |
| bedroom | statutory_floor | min_area | 7.0 | m2 | `az_azdtn_2_7_2` | cl. 5.7 | verified | statutory | **mansard relaxation**: in a mansard storey, or a storey with a sloping external wall, bedroom *and* kitchen may drop to 7.0 m², **conditional** on the general living room being ≥ 16.0 m² |
| kitchen | statutory_floor | min_area | 7.0 | m2 | `az_azdtn_2_7_2` | cl. 5.7 | verified | statutory | same mansard relaxation, same condition |
| habitable_room | statutory_floor | min_clear_height | 2700 | mm | `az_azdtn_2_7_2` | cl. 5.8 | verified | statutory | *yaşayış otaqları*, floor to ceiling. Also the mansard high point. |
| kitchen | statutory_floor | min_clear_height | 2700 | mm | `az_azdtn_2_7_2` | cl. 5.8 | verified | statutory | *mətbəx* |
| corridor / hall / antresol | statutory_floor | min_clear_height | 2100 | mm | `az_azdtn_2_7_2` | cl. 5.8 | verified | statutory | *mənzildaxili dəhlizlər, hollar, antresollar* — intra-apartment |

### Composition and topology rules in the same section

Not dimensions, but they are hard constraints on a produced Plan and the
acceptance validator's C6 predicates already have slots for them.

| rule | ref | conf | force | note |
|---|---|---|---|---|
| An apartment **must** provide: kitchen (or kitchen-niche), hall, bathroom (or shower) and WC (or combined bathroom), and a store/built-in cupboard | cl. 5.2 | verified | statutory | *"nəzərdə tutulmalıdır"* — shall be provided. This is the required room set. |
| **A bedroom must not be designed as a through-route to another room** | cl. 5.9 | verified | statutory | *"yataq otaqları digər otağa keçid kimi layihələndirilməməlidir"*. This is exactly the `is_private` flag in `room-constraints.json`, stated as law. Direct consumer for the C6 item 1 reachability predicate. |
| **Habitable rooms may not be placed in a plinth or basement storey** | cl. 5.5 | verified | statutory | *yolverilməzdir* — not permitted. |
| A combined bathroom/WC is permitted in one-room apartments of the state and municipal social and special-purpose housing fund | cl. 5.10 | verified | statutory | permission, not requirement |
| Room dimensions are determined by the equipment and furniture that must fit, per **ergonomics** | cl. 5.6 | verified | statutory | *"Mənzilin yaşayış otaqlarının və digər sahələrinin ölçüləri erqonomikanın tələblərinə uyğun yerləşdirilən zəruri avadanlıq və mebelin yerləşdirilməsindən asılı olaraq müəyyənləşdirilir."* **The AZ norm delegates plan dimensions to ergonomics by name.** See §3.1. |
| Loggias and balconies **must** be designed, given Azerbaijan's climate, except under stated noise (≥75 dB at the façade) or dust (≥1.5 mg/m³ for ≥15 summer days) conditions | cl. 5.4 | verified | statutory | *zəruridir* — necessary. A regional convention with real force; worth carrying. |

### Scope of the norm

Clause 1: AzDTN 2.7-2 applies to newly built **multi-apartment residential
buildings not exceeding 75 m in height**, apartment-type dormitories, and
residential areas within multi-functional buildings — and compliance is owed by
"all legal and natural persons irrespective of organisational-legal form and form
of ownership". Above 75 m a project needs bespoke special technical conditions.
**This is the same building type the Swiss Dwellings corpus contains and the same
type ADR 0006 chose AZ for.** The fit is exact.

---

## 3. Clear plan dimensions

### 3.1 AzDTN 2.7-2 publishes none, on purpose

This is the single most consequential negative finding in this slice. Section 5
of AzDTN 2.7-2 — the section that governs apartments and their elements — sets
**areas and heights only**. It contains no minimum width, no minimum depth, no
minimum clear dimension for any room inside an apartment. The whole document was
scanned for `en` (width) and `ən azı` (at least); the only plan dimensions found
are building-circulation ones (§3.3) and plant-room ones (§3.4).

Clause 5.6 is why. It says room dimensions follow from placing the necessary
equipment and furniture *"erqonomikanın tələblərinə uyğun"* — in accordance with
the requirements of ergonomics — and the norm defines *erqonomika* in its own
terms section as the science of organising human activity to suit physiological
and psychological capability.

**This is not an Azerbaijani quirk.** The current Russian multi-apartment norm,
SP 54.13330.2022 cl. 5.11, makes the *same* delegation in near-identical words —
*"следует определять с учётом требований эргономики и размещения необходимого
набора внутриквартирного оборудования и предметов мебели"* — and likewise
publishes no intra-apartment clear width in any edition from 2003 to 2022. The
whole norm family moved these numbers out of the code and into ergonomics. §11.5.

**Consequence for the map.** Ticket 19's region-invariant ergonomic layer is not
merely compatible with the AZ profile; it is the thing AZ law points at for
exactly the values ticket 19 owns, and the Russian line independently corroborates
that this is deliberate rather than an omission. The AZ profile should carry
`min_clear_width` as **null at `statutory_floor`** and let the ergonomic layer
bind, with a provenance note citing cl. 5.6. Publishing a made-up width under an
AZ `src` key would be the 90%-right artefact C2 warns about.

### 3.2 AzDTN 2.7-3 does publish widths — for the wrong building type

AzDTN 2.7-3 (*Fərdi yaşayış evləri*, individual/detached dwelling houses), Baku
2023, cl. 5.1, second list:

> "Otaq və yerləşgələrin eni aşağıda qeyd olunan ölçülərdən az olmayaraq
> **qəbul edilməlidir**"
>
> *"The width of rooms and spaces **shall be taken** not less than the dimensions
> noted below"*

Mandatory register — and note it contrasts, within the *same clause*, with the
area list immediately above it, which says `tövsiyə edilir` ("is recommended").
The drafter separated force deliberately, sentence by sentence.

| room_type | tier | field | value | unit | src_key | ref | conf | force | note |
|---|---|---|---|---|---|---|---|---|---|
| habitable_room | (see note) | min_clear_width | 3000 | mm | `az_azdtn_2_7_3` | cl. 5.1 | verified | statutory | *yaşayış otaqları* |
| kitchen | (see note) | min_clear_width | 2600 | mm | `az_azdtn_2_7_3` | cl. 5.1 | verified | statutory | *mətbəx* |
| hall / corridor | (see note) | min_clear_width | 1400 | mm | `az_azdtn_2_7_3` | cl. 5.1 | verified | statutory | *dəhliz* |
| bathroom | (see note) | min_clear_width | 1500 | mm | `az_azdtn_2_7_3` | cl. 5.1 | verified | statutory | *hamam* |
| wc | (see note) | min_clear_width | 800 | mm | `az_azdtn_2_7_3` | cl. 5.1 | verified | statutory | *ayaqyolu*, without basin |
| wc_with_basin | (see note) | min_clear_width | 1200 | mm | `az_azdtn_2_7_3` | cl. 5.1 | verified | statutory | *ayaqyolu*, with washbasin (*əl-üz yuyanla*) |
| habitable_room | (see note) | max_aspect_ratio | 2.0 | — | `az_azdtn_2_7_3` | cl. 5.1 | verified | recommended | *"uzunluğunun eninə nisbətən 2 dəfədən çox olmayaraq"* — length:width **recommended** not to exceed 2:1. A proportion rule, and a good soft objective for the solver. |

**"(see note)" is deliberate and must be resolved before these enter the JSON.**
These values are `statutory` **for detached houses**. The engine draws
multi-apartment plans, so for the AZ profile they are:

- **not** `statutory_floor` — no Azerbaijani instrument imposes them on an
  apartment, and printing "below statutory minimum" against them would be the
  C8 violation the tier model explicitly warns about;
- a defensible **`market_default`** for the plan-dimension fields, because they
  are the same regulator's own published view of a liveable Azerbaijani room and
  they are internally consistent with the AzDTN 2.7-2 areas;
- if adopted there, they must carry `conf: derived` (or `engine_choice`) with a
  `note` recording the building-type transfer — **not** `verified`, because
  `verified` would assert the value at a tier the source does not support.

### 3.3 Building-circulation widths — AzDTN 2.7-2 cl. 7.2.2

Outside the apartment, so outside the solver's envelope in v1, but recorded
because the same profile will eventually need core geometry.

| element | field | value | unit | src_key | ref | conf | force | note |
|---|---|---|---|---|---|---|---|---|
| common_corridor | min_clear_width | 1400 | mm | `az_azdtn_2_7_2` | cl. 7.2.2 | verified | statutory | corridor length up to 40 m between stairs, or stair to end wall |
| common_corridor | min_clear_width | 1600 | mm | `az_azdtn_2_7_2` | cl. 7.2.2 | verified | statutory | corridor length over 40 m |
| gallery | min_clear_width | 1200 | mm | `az_azdtn_2_7_2` | cl. 7.2.2 | verified | statutory | *qalereya* |
| stair_flight | min_clear_width | 1050 | mm | `az_azdtn_2_7_2` | cl. 8.2, Table 5 | verified | statutory | section-type buildings, 2 storeys and 3+ storeys alike; measured between handrails, or handrail to wall |
| stair_flight | min_clear_width | 1200 | mm | `az_azdtn_2_7_2` | cl. 8.2, Table 5 | verified | statutory | corridor- and gallery-type buildings |
| stair_flight_internal | min_clear_width | 900 | mm | `az_azdtn_2_7_2` | cl. 8.2, Table 5 | verified | statutory | flights to basement/plinth storeys, and **intra-apartment** stairs |
| winder_tread | min_width_at_centre | 180 | mm | `az_azdtn_2_7_2` | cl. 8.2 | verified | statutory | spiral / winder stairs are permitted as an intra-apartment stair in a two-level apartment |
| lift_lobby | min_clear_depth | 1600 | mm | `az_azdtn_2_7_2` | cl. 4.10 | verified | statutory | in front of a lift of ≤1000 kg with a 2100 mm-wide car; sized to admit a stretcher |
| lift_lobby | min_clear_depth | 2100 | mm | `az_azdtn_2_7_2` | cl. 4.10 | verified | statutory | lift of ≤1000 kg with 2100 mm car **depth** |
| lift_lobby | min_clear_depth | 1800 / 2500 | mm | `az_azdtn_2_7_2` | cl. 4.10 | verified | statutory | lifts facing each other in two rows: 1800 mm if car depth < 2100 mm, 2500 mm if ≥ 2100 mm |
| balustrade | min_height | 1200 | mm | `az_azdtn_2_7_2` | cl. 8.3 | verified | statutory | stairs, balconies, loggias, terraces, roofs and other fall risks. Cross-check against UK AD K. |
| stair_flight | min_risers | 3 | count | `az_azdtn_2_7_2` | cl. 8.2 | verified | statutory | fewer than 3 or more than 18 steps in a flight is not permitted; mixed riser heights/tread depths are forbidden outright |
| entrance_tambour | min_depth | 1500 | mm | `az_azdtn_2_7_2` | cl. 9.18 | verified | statutory | climatic region III (which covers Azerbaijan) |

### 3.4 Plant room — AzDTN 2.7-2, clause 7.3

Individual gas boilers (*istilik generatoru*) are ordinary in Azerbaijani
apartments, so this is a room the planner must actually place.

| room_type | field | value | unit | src_key | ref | conf | force | note |
|---|---|---|---|---|---|---|---|---|
| boiler_room | min_volume | 15.0 | m3 | `az_azdtn_2_7_2` | cl. 7.3 | verified | statutory | *"15 m³-dən az olmayaraq"*; sized for operation and installation access |
| boiler_room | min_clear_height | 2200 | mm | `az_azdtn_2_7_2` | cl. 7.3 | verified | statutory | *"ən azı 2,2 m"* |
| boiler_room | min_passage_width | 700 | mm | `az_azdtn_2_7_2` | cl. 7.3 | verified | statutory | passages around the appliance |
| boiler_room | glazing_ratio | 0.03 | m2/m3 | `az_azdtn_2_7_2` | cl. 7.3 | verified | statutory | 0.03 m² of glazing per 1 m³ of room volume, plus an opening light for air change. **Cross-reference for ticket 25 item 3 (`win.area_ratio`) — a plant-room ratio, not the habitable-room one.** Not decided here. |
| boiler_room | placement | — | — | `az_azdtn_2_7_2` | cl. 7.3 | verified | statutory | **not permitted in a basement** |

---

## 4. Force — and whether `statutory_floor` is honestly named for AZ

**Verdict: yes, and it is the first region on this map where it is.**
`force: statutory`. The chain is four links, each read first-hand.

### 4.1 The Code makes normative documents binding

**Şəhərsalma və Tikinti Məcəlləsi** (Urban Planning and Construction Code of the
Republic of Azerbaijan), approved by **Law No. 392-IVQ of 29 June 2012**.

- **Art. 3.0.26** defines *şəhərsalma və tikintiyə dair normativ sənədlər* as the
  rules, standards, conditions, technical norms and other **technical normative
  legal acts** regulating urban planning and construction. They are *legal acts*,
  by definition, not guidance.
- **Art. 14.3** — the operative one:

  > "Şəhərsalma və tikinti fəaliyyətinin həyata keçirilməsi zamanı şəhərsalma və
  > tikintiyə dair normativ sənədlərin tələblərinə **əməl edilməlidir**."
  >
  > *"In carrying out urban-planning and construction activity, the requirements
  > of the normative documents on urban planning and construction **must be
  > complied with**."*

- **Art. 14.2** requires the relevant executive authority to publish the **list**
  of those documents periodically each year. That list is the SİYAHI in §1.
- **Art. 15.1.5** places technical normative legal acts on the *design and
  construction* of construction objects inside the system. AzDTN 2.7-2 is one.
- **Art. 15.2**: the legal basis of the system is this Code and other normative
  legal acts.

### 4.2 The AzDTN system separates mandatory from recommended, in the text

From *"Azərbaycan Respublikası Dövlət tikinti normativ sənədləri sisteminin Əsas
müddəaları (Konsepsiya)"*, Azərdövləttikintikom, Baku 1994 — the governing
document of the AzDTN system itself:

- **§3.1** — every normative document in the system is composed of **mandatory
  norms and requirements** (*məcburi*), **recommended norms** (*tövsiyə*), and
  reference information.
- **§3.2** — norms that determine and regulate the final functional and
  operational properties of the living environment and of buildings, for the
  purpose of citizens' health and life safety, property protection, environmental
  protection, working conditions, reliability and durability, **are deemed
  mandatory**. Minimum habitable-room area is squarely inside that description.
- **§3.4** — in AzDTN documents, mandatory and recommended norms **must be
  separated from one another**.
- **§3.6** — mandatory norms are expressed **at the level of a minimum
  requirement or a maximum limit**. That is precisely the grammatical form of
  AzDTN 2.7-2 cl. 5.7.
- **§5.2** — legal enforcement runs through liability for **violation of the
  mandatory requirements** of normative documents, with sanctions applied by state
  supervisory bodies.

This gives an objective, source-based decision rule rather than a judgement call:

| Azerbaijani wording | register | `force` |
|---|---|---|
| `az olmamalıdır` / `olmamalıdır` / `edilməlidir` / `nəzərdə tutulmalıdır` / `zəruridir` | *məcburi* — mandatory | `statutory` |
| `tövsiyə olunur` / `tövsiyə edilir` | *tövsiyə* — recommended | `recommended` |
| `yol verilir` | permission, not obligation | (a relaxation; widens the feasible set) |

Every `force` in this note was assigned by that rule, from the verb in the clause
— not from the tier's name and not from the document's title. This is what the
`statutory_floor_note` in `room-constraints.json` demands.

### 4.3 The norm is a registered legal act

AzDTN 2.7-2's own front matter:

- **Approved** by decision **No. 03 of 30 November 2021** of the Collegium of the
  State Committee on Urban Planning and Architecture.
- **In force from** 30 November 2021.
- **State Register of Legal Acts registration number 15202111300003.**
- *İlk dəfə qəbul edilir* — adopted for the first time.
- Publication code `AzDAK-TN/Q № 0030-2021`.

AzDTN 2.7-3, for comparison: Collegium decision **No. 3-35/3-2-6/2023 of
21 November 2023**, in force from **6 December 2023**, register number
**15202311235326**, code `AzDAK-TN/Q № 0040-2023`. (The SİYAHI records its entry
into force as 23.11.2023; the norm's own cover page says 06.12.2023. Flagged; the
discrepancy affects nothing here.)

### 4.4 What is *not* in force — and this matters

AzDTN 2.7-2's cover page carries an express repeal (Cyrillic destroyed by the
font extraction, reconstructed from the surviving Latin frame and confirmed
against the SİYAHI entry, which records AzDTN 2.7-2 as *"СНиП 2.08.01-89\*
əvəzinə"* — "in place of СНиП 2.08.01-89\*"):

> "Bu texniki normativ hüquqi akt qüvvəyə mindiyi tarixdən **СНиП 2.08.01-89\***
> *«Жилые здания»* normativ sənədin **Azərbaycan Respublikası ərazisində hüquqi
> qüvvəsi dayandırılır**."
>
> *"From the date this technical normative legal act enters into force, the legal
> force of the normative document СНиП 2.08.01-89\* «Жилые здания» **on the
> territory of the Republic of Azerbaijan is terminated**."*

So:

- **SNiP 2.08.01-89\*** — *was* live Azerbaijani law until 2021-11-30, and is now
  **superseded in Azerbaijan by name**. `force: superseded`. It may be cited for
  lineage. It may **not** be cited as a live AZ minimum, and the ticket's
  instruction to fall back on it is now moot for the multi-apartment case: we got
  the successor.
- **SNiP 31-01-2003 / SP 54.13330** — the *Russian* successor line. These never
  applied in Azerbaijan; Azerbaijan branched to its own AzDTN instead. They do not
  appear in the SİYAHI. `force: foreign_not_applicable` for AZ. Useful only as a
  comparator (§11.5).
- **SNiP 35-01-2001 / SP 59.13330 / SP 137.13330** — likewise Russian, likewise
  absent from the SİYAHI. See §5.

**The honest framing for the profile's provenance field:** AZ's `statutory_floor`
is not "inherited Soviet practice". It is a 2021 Azerbaijani legal act that
replaced the Soviet document, in a state that legislated its own building code in
2012. The numbers happen to be close to the Soviet ones; the *authority* is not
Soviet at all.

---

## 5. `accessible` — and a correction to the ticket

The ticket expected SNiP 35-01-2001 / SP 59.13330 (or an AzDTN equivalent).
**Neither is Azerbaijan's instrument.** Searching the official SİYAHI and the
full arxkom norms register:

- **SNiP 35-01-2001, SP 59.13330 and SP 137.13330 do not appear** anywhere in the
  Azerbaijani list of normative documents in force. This is a **verified
  negative**, not a failure to find: the SİYAHI extracted cleanly with Cyrillic
  intact and was searched exhaustively — `35-01`, `59.13330` and `137.13330` each
  return **zero** occurrences across all 211 pages. (For completeness, so do
  `54.13330` and `31-01-2003`, the multi-apartment pair.) They are Russian
  Federation documents and Azerbaijan did not adopt any of them.
- There is **no AzDTN accessibility norm** in the register at all — no
  `AzDTN 2.x` covering *əlilliyi olan şəxslər*.

What Azerbaijan actually has in force, per the SİYAHI:

| # | Instrument | Issuer / date | force |
|---|---|---|---|
| 1 | **ВСН 62-91\*** — *Проектирование среды жизнедеятельности с учётом потребностей инвалидов и маломобильных групп населения* ("Design of the living environment taking account of the needs of persons with disabilities and low-mobility groups") | Listed in the SİYAHI, p. 66, verbatim: *"…SSRİ Dövlət Tikinti və Arxitektura Komitəsinin **29.11.91-ci il tarixli, 166 №-li əmri** ilə təsdiq olunmuş **dəyişikliyi** nəzərə almaqla"* — "taking into account the **amendment** approved by order No. 166 of 29.11.1991 of the USSR State Committee for Construction and Architecture". Note the order is cited as approving the *amendment*, which is what the trailing `*` in `62-91*` denotes. | departmental construction norms (*Ведомственные строительные нормы*; AZ designation *Sahə Tikinti Normaları*), carried as in force in AZ |
| 2 | *"Bina və qurğuların layihələndirilməsində əlillər üçün zəruri olan həyat və fəaliyyət şəraitinin yaradılması üzrə **Müvəqqəti Təlimat**"* (Temporary Instruction) | Azərdövləttikintikom, order **No. 42 of 14.03.2002** | instruction |
| 3 | *"…əlillərin reabilitasiyası üzrə texniki vasitələrdən və memarlıq-planlaşdırma həllərindən istifadə olunması üzrə **Metodiki göstərişlər**"* (Methodological guidelines) | Azərdövləttikintikom, order **No. 92 of 25.07.2001** | methodological guidance |

**AzDTN 2.7-3 cl. 4.17 points at the first of these by name**, using its
Azerbaijani designation *STN 62* (*Sahə Tikinti Normaları* 62 = ВСН 62):

> "Əlilliyi olan şəxslər (o cümlədən təkərli oturacaq təyin edilmiş) yaşayan
> fərdi evlərdə ВСН 62-yə uyğun münasib həyat və fəaliyyət şəraitinin təmin
> olunması **tövsiyə edilir**."
>
> *"In individual houses inhabited by persons with disabilities (including
> wheelchair users), it **is recommended** that suitable living and activity
> conditions be ensured in accordance with ВСН 62."*

`tövsiyə edilir` — **recommended**, not mandatory. So on the AZ side the
accessible tier is a recommendation even where it is invoked.

**AzDTN 2.7-2 (apartments) is weaker still.** Clause 4.3 requires that residential
buildings, stairs, stairwells, exits and entrances, corridors, open passages,
ramps, lifts and the entrance doors of apartments where persons with disabilities
live *"əlçatan uyğunlaşdırılmalıdır"* — shall be adapted for the comfortable and
safe movement of persons with disabilities — **but states no dimension for any of
it**, and cites no accessibility norm by number. It adds only:

| rule | ref | conf | force | note |
|---|---|---|---|---|
| Buildings intended for **older people** shall not exceed 9 storeys | cl. 4.3 | verified | statutory | *olmamalıdır* |
| Buildings intended for **families of persons with disabilities** shall not exceed 5 storeys | cl. 4.3 | verified | statutory | *olmamalıdır* |
| In other residential buildings, apartments for persons with disabilities are **recommended** to be placed on the first storey | cl. 4.3 | verified | recommended | *tövsiyə olunur* |

### The one accessible-tier AREA Azerbaijan does publish

AzDTN 2.7-3 cl. 5.1, in the recommended list:

| room_type | tier | field | value | unit | src_key | ref | conf | force | note |
|---|---|---|---|---|---|---|---|---|---|
| bedroom_wheelchair | accessible | min_area | 9.0 | m2 | `az_azdtn_2_7_3` | cl. 5.1 | verified | recommended | *"təkərli oturacaq təyin edilmiş əlilliyi olan şəxslərin: yataq otağı — 9 m²"*. Detached houses. Note it is the **same** 9 m² the same clause recommends for an ordinary bedroom — the norm gives the wheelchair user no uplift at all, which is itself the finding. |

### ВСН 62-91\* — obtained and read first-hand

**Everything else in the accessible tier comes from ВСН 62-91\*, and it was
obtained.** Full text read at
`https://files.stroyinf.ru/Data2/1/4294854/4294854753.htm`.

Front matter, verified: *«Утверждены приказом Государственного комитета по
архитектуре и градостроительству при Госстрое СССР от 4 октября 1991 г. № 134.
Срок введения в действие 1 января 1992 г.»* — approved by order **No. 134 of
4 October 1991** of the USSR State Committee for Architecture and Urban Planning
under Gosstroy, **in force from 1 January 1992**. Drafted by TsNIIEP im. B. S.
Mezentseva. The trailing `*` denotes the amendment approved by order **No. 166 of
29 November 1991** — which is precisely the order the Azerbaijani SİYAHI cites,
confirming that the version AZ carries is the amended `62-91*` and not the
original `62-91`.

**Force on the AZ side: `recommended`.** The only Azerbaijani instrument that
invokes it (AzDTN 2.7-3 cl. 4.17) does so with `tövsiyə edilir`. Inside the
document itself the clauses below are drafted in the Russian mandatory register
(*должна быть не менее*), but that register is the *Soviet drafter's*, not
Azerbaijan's, and Azerbaijan's own act downgrades it. **The warn wording for the
accessible tier in AZ must say "recommended", never "statutory".**

#### Dwelling values — apartments

| room_type | tier | field | value | unit | src_key | ref | conf | force | note |
|---|---|---|---|---|---|---|---|---|---|
| kitchen | accessible | min_area | 9.0 | m2 | `ru_vsn_62_91` | cl. 3.1.8 | verified | recommended | *«Площадь кухни в квартирах для инвалидов, пользующихся креслом-коляской, должна быть не менее 9 м²»*. Against the 8.0 m² statutory floor — a **+1.0 m² uplift**, and the only dwelling *area* uplift in the whole accessible tier. |
| kitchen | accessible | min_clear_width | 2200 | mm | `ru_vsn_62_91` | cl. 3.1.8 | verified | recommended | *«…а ее ширина не менее 2,2 м»*. Same sentence. |
| wc | accessible | min_clear_width | 1200 | mm | `ru_vsn_62_91` | cl. 2.8.8 | verified | recommended | *«Ширина помещения уборной в квартирах должна быть не менее 1,2 м, а ее глубина — не менее 1,6 м»* |
| wc | accessible | min_clear_depth | 1600 | mm | `ru_vsn_62_91` | cl. 2.8.8 | verified | recommended | same sentence |
| wheelchair_store | accessible | required | — | — | `ru_vsn_62_91` | cl. 3.1.9 | verified | recommended | a place or store for the wheelchair, in the *передняя* or immediately adjacent. **No dimension given** — another hand-off to ergonomics. |
| homework_store | accessible | min_area | 4.0 | m2 | `ru_vsn_62_91` | cl. 3.1.10 | verified | recommended | store for tools/materials where the occupant works at home |

#### Circulation and clearance — building-wide, and largely ergonomic

These are **body-derived, not convention-derived**, so by the ticket-5 split they
belong to ticket 19's invariant layer rather than to the AZ profile. Recorded
here as cross-references with their provenance intact, because ВСН 62 is where an
AZ-conditioned plan would be expected to get them.

| element | field | value | unit | ref | conf | note |
|---|---|---|---|---|---|---|
| wheelchair turn, 90° | min_clear_area | 1300 × 1300 | mm | cl. 2.1.4\* | verified | *«Размеры площадки для поворота кресла-коляски на 90° должны быть не менее 1,3 × 1,3 м»* |
| wheelchair turn, 180° | min_clear_area | 1300 × 1500 | mm | cl. 2.1.4\* | verified | |
| wheelchair turn, 360° | min_clear_area | **1500 × 1500** | mm | cl. 2.1.4\* | verified | **Answers the ticket's open question: the full turning figure is 1500 mm, not 1400 mm.** |
| approach to equipment/furniture | min_clear_width | 900 | mm | cl. 2.1.4\* | verified | 1200 mm where a 90° wheelchair turn is needed |
| knee space under furniture | min_width × min_height | 600 × 600 | mm | cl. 2.1.4\* | verified | measured across the furniture frontage, above floor level |
| door on a wheelchair route | min_clear_width | 900 | mm | cl. 2.6.3 | verified | *«должны иметь ширину в свету не менее 0,9 м»*. **Swing-hinge and revolving doors are forbidden outright on disabled circulation routes.** |
| wet-room door | swing | outward | — | cl. 2.8.7 | verified | *«Двери из санитарно-гигиенических кабин и помещений для инвалидов должны открываться наружу»*. Pairs with the WC-depth cross-reference in §10. |
| entrance landing | min_clear_area | 1000 × 2500 | mm | cl. 2.6.2 | verified | with drainage, and heating where the local climate requires it |
| apartment placement | storey | ground | — | cl. 3.1.6 | verified | apartments for wheelchair users to be on the first storey **as a rule** |
| ground-floor balcony exit to the plot | ramp or lift | — | — | cl. 3.1.7 | verified | |
| dead-end corridor | max_occupancy | 30 | persons | cl. 3.1.5\* | verified | a topology constraint on the core, not on a dwelling |
| specialised residential building | max_storeys | 3 | count | cl. 3.1.2\* | verified | **Conflicts with AzDTN 2.7-2 cl. 4.3, which sets 5 storeys for buildings for families of persons with disabilities.** See the conflict note below. |

#### Institutional — NOT apartments, do not merge into the profile

ВСН 62-91\* cl. 5.1.3 sets communal room areas for *дома-интернаты*
(residential institutions): bathroom 12 m², WC 4.5 m², shower cabin 3 m²,
sanitary room 16 m², utility room 12 m², plus a common room at 1.2 m² per
resident and a kitchen-buffet at 0.6 m² per resident. **These are institutional
shared facilities serving a whole living group, not rooms in a dwelling.** A
12 m² "bathroom" read as a dwelling minimum would be absurd. Recorded so nobody
later mines cl. 5.1.3 into the wet-room row.

#### A conflict, stated rather than resolved

ВСН 62-91\* cl. 3.1.2\* caps *specialised* residential buildings at **3 storeys**.
AzDTN 2.7-2 cl. 4.3 caps buildings for families of persons with disabilities at
**5 storeys** and buildings for older people at **9**. The two do not agree.

**AzDTN 2.7-2 wins**, and the reasoning is not "the newer document": it is that
AzDTN 2.7-2 is mandatory Azerbaijani law under Art. 14.3 of the Code, while
ВСН 62 reaches Azerbaijan only through AzDTN 2.7-3 cl. 4.17's *recommendation*
— and cl. 4.17 is in a norm about detached houses, which have at most 3 storeys
anyway. A recommendation cannot override a mandatory clause in the same legal
system. Flagged rather than silently dropped, because it is the only place these
two sources contradict each other.

Storey count does not reach a v1 Plan in any case; the engine draws one floor.

**Warn wording for `accessible` in AZ must not say "statutory".** The tier
binding is `unread` in v1 anyway, but the `force` field must be right before it
is ever read.

---

## 6. ADR 0007 — the grid arithmetic, reported not decided

ADR 0007 requires, at `grid_mm = 250`:

```
minimum_mm + t_int  ≡  0   (mod 250)
```

for **every** internal thickness the profile offers. Equivalently
`minimum_mm ≡ −t_int (mod 250)`.

### 6.1 Admissible residues

| `t_int` (mm) | 100 | 120 | 140 | 160 | 200 | 250 |
|---|---|---|---|---|---|---|
| required `minimum_mm mod 250` | **150** | **130** | **110** | **90** | **50** | **0** |

**All six residues are distinct.** That is the whole difficulty: no single
published clear dimension can satisfy the rule for two different `t_int`. The
ticket already anticipated this for `{100, 200}`; it holds for every pair in the
candidate set. A profile offering *n* internal thicknesses needs *n* sets of
published minima, or a single `t_int`, or a different grid.

### 6.2 Greatest admissible value at or below each raw source figure

`(−loss)` is how far the published figure falls below the source's number. Per
ADR 0007's consequence note, this drop is *correct* — the source's figure is
nominal, and the published figure is what the occupant can tape.

| raw (mm) | provision | `t_int`=100 | 120 | 140 | 160 | 200 | 250 |
|---|---|---|---|---|---|---|---|
| 3000 | habitable room width (AzDTN 2.7-3 cl. 5.1) | 2900 (−100) | 2880 (−120) | 2860 (−140) | 2840 (−160) | 2800 (−200) | **3000 (−0)** |
| 2600 | kitchen width (AzDTN 2.7-3 cl. 5.1) | 2400 (−200) | 2380 (−220) | 2360 (−240) | 2590 (−10) | 2550 (−50) | 2500 (−100) |
| 1400 | hall/corridor width (AzDTN 2.7-3 cl. 5.1) | **1400 (−0)** | 1380 (−20) | 1360 (−40) | 1340 (−60) | 1300 (−100) | 1250 (−150) |
| 1500 | bathroom width (AzDTN 2.7-3 cl. 5.1) | 1400 (−100) | 1380 (−120) | 1360 (−140) | 1340 (−160) | 1300 (−200) | **1500 (−0)** |
| 800 | WC width (AzDTN 2.7-3 cl. 5.1) | 650 (−150) | 630 (−170) | 610 (−190) | 590 (−210) | **800 (−0)** | 750 (−50) |
| 1200 | WC-with-basin width (AzDTN 2.7-3 cl. 5.1) | 1150 (−50) | 1130 (−70) | 1110 (−90) | 1090 (−110) | 1050 (−150) | 1000 (−200) |
| 1400 | common corridor ≤40 m (AzDTN 2.7-2 cl. 7.2.2) | **1400 (−0)** | 1380 (−20) | 1360 (−40) | 1340 (−60) | 1300 (−100) | 1250 (−150) |
| 1600 | common corridor >40 m (AzDTN 2.7-2 cl. 7.2.2) | 1400 (−200) | 1380 (−220) | 1360 (−240) | 1590 (−10) | 1550 (−50) | 1500 (−100) |
| 1200 | gallery (AzDTN 2.7-2 cl. 7.2.2) | 1150 (−50) | 1130 (−70) | 1110 (−90) | 1090 (−110) | 1050 (−150) | 1000 (−200) |
| 2200 | kitchen width, wheelchair (ВСН 62-91* cl. 3.1.8) | 2150 (−50) | 2130 (−70) | 2110 (−90) | 2090 (−110) | 2050 (−150) | 2000 (−200) |
| 1200 | WC width, wheelchair (ВСН 62-91* cl. 2.8.8) | 1150 (−50) | 1130 (−70) | 1110 (−90) | 1090 (−110) | 1050 (−150) | 1000 (−200) |
| 1600 | WC depth, wheelchair (ВСН 62-91* cl. 2.8.8) | 1400 (−200) | 1380 (−220) | 1360 (−240) | 1590 (−10) | 1550 (−50) | **1500 (−100)** |
| 1500 | wheelchair turn 360° (ВСН 62-91* cl. 2.1.4*) | 1400 (−100) | 1380 (−120) | 1360 (−140) | 1340 (−160) | 1300 (−200) | **1500 (−0)** |
| 1300 | wheelchair turn 90° (ВСН 62-91* cl. 2.1.4*) | 1150 (−150) | 1130 (−170) | 1110 (−190) | 1090 (−210) | **1300 (−0)** | 1250 (−50) |

**Two of these must NOT be eroded, and the distinction matters.** A *room* clear
dimension is eroded because ADR 0001 makes the published rect `erode(solved,
t_int/2)`. A **door clear width** (ВСН 62 cl. 2.6.3, 900 mm) is a dimension of an
opening inside a wall, not of a room rect, so `t_int` never eats into it — it is
exempt for the same reason areas and storey heights are. A **turning square** is
a clearance that must *fit inside* the eroded room, so it is a lower bound on the
already-eroded clear rect, not itself a published minimum to be aligned. The two
turning rows above are shown for orientation only; publishing them as grid-aligned
minima would double-count the erosion.

### 6.3 Observations for whoever decides

1. **`t_int = 100` is the standout.** AZ's 1400 mm hall/corridor is *exactly*
   admissible at `t_int = 100` (1400 + 100 = 1500 = 6 × 250), at zero loss. The
   corridor is the tightest and most frequently binding dimension in a dwelling
   plan, and it is the one that costs nothing. That is a real argument for a
   single-`t_int` profile at 100 mm, and it arrives from the source rather than
   from convenience.
2. **Worst-case loss is 240 mm** (kitchen width at `t_int = 140`) — just under a
   full grid unit, which is the bound ADR 0007's argument predicts.
3. **Loss is not monotone in `t_int`.** The kitchen loses 240 mm at 140 mm but
   only 10 mm at 160 mm. Anyone eyeballing "thicker wall ⇒ bigger loss" will get
   this wrong; it must be computed per value.
4. **Area minima are exempt.** All of §2's m² values are unaffected by ADR 0007;
   the rule governs linear minima only. This should be asserted in the same test
   that asserts the congruence, so nobody later "fixes" 8.0 m² onto a grid.
5. **Heights are exempt too.** The 2700 mm and 2100 mm clear heights in cl. 5.8
   are vertical. ADR 0001 erodes the plan rect by `t_int/2` in plan only; nothing
   erodes a storey height by an internal partition thickness. The congruence must
   not be applied to them, and a naive "every dimensional minimum" reading of ADR
   0007 would apply it. **Worth an explicit carve-out in the ADR or in the test.**
6. **The 2:1 aspect recommendation (AzDTN 2.7-3 cl. 5.1) survives erosion badly
   at small rooms** and should be carried as a soft objective, never a gate.

**Not decided here**, per the ticket: whether the profile ships one `t_int`,
per-thickness minima, or reopens the grid. §6.1 is the input to that decision.

---

## 7. `market_default`

Two candidate sources, both weaker than the statutory floor, and they should be
reconciled by whoever writes the JSON.

### 7.1 AzDTN 2.7-2 cl. 5.1 — recommended apartment totals

Clause 5.1 recommends (`tövsiyə olunur`) minimum apartment sizes by room count
for the **state and municipal housing fund**, tabulated separately for
*şəhər* (town) and *kənd* (village), excluding balconies, terraces, verandas,
loggias, vestibules, unheated ancillary rooms and the apartment tambour. For the
private housing fund the clause says area, room count and composition are set by
the client.

Per the copyright posture (findings §7.6 items 5 and 7), the table is **not
reproduced**. Two anchor values, cited individually, to fix the order of
magnitude: a one-room town apartment sits in the **28–38 m²** band and a
three-room town apartment in the **56–65 m²** band. `src: az_azdtn_2_7_2`,
`ref: cl. 5.1 Table 1`, `conf: verified`, `force: recommended`.

Note the tier semantics fit: `room-constraints.json` says `market_default` is
"what is actually built and what a Homeowner expects", and this is the
*regulator's own* recommendation for publicly-funded housing — a floor on
ordinariness, not a target. It probably reads low against Baku private-sector
practice.

**A copyright observation that reinforces the decision not to reproduce it.**
AzDTN 2.7-2's Table 1 is **substantially SNiP 2.08.01-89\* Table 5 carried
forward** — same row structure (town/settlement over village), same column
structure (1 to 6 rooms), same exclusion list, and band figures that agree at
most cells and diverge at only three. That is the *selection and arrangement* of
someone else's table, which findings §7.6 item 5 names as the thin copyright that
survives Feist and item 7 names as the systematic-extraction failure. Citing two
anchor values individually is safe; transcribing the table is precisely the thing
the posture forbids, and the fact that it would be transcribing a *twice*-carried
table makes it worse, not better.

**Measurement convention: not decided here** (ticket 25 item 7 owns it). What was
observed: cl. 5.1 speaks of *ümumi sahə* (total area) with an explicit exclusion
list for balconies/loggias/terraces/verandas/tambour, so the AZ convention on the
*общая площадь* / *жилая площадь* question is closer to a binary GIA-style count
of enclosed heated space than to German Wohnfläche's fractional balcony weighting.
Handed on as an observation, not a decision.

### 7.2 AzDTN 2.7-3 cl. 5.1 — recommended areas for detached houses

Same document as §3.2, the *first* list in cl. 5.1, in the **recommended**
register (`qəbul edilməsi tövsiyə edilir`):

| room_type | tier | field | value | unit | src_key | ref | conf | force | note |
|---|---|---|---|---|---|---|---|---|---|
| living_room | market_default | min_area | 16.0 | m2 | `az_azdtn_2_7_3` | cl. 5.1 | verified | recommended | *ümumi otaq (və ya qonaq otağı)*. Detached houses. |
| bedroom | market_default | min_area | 9.0 | m2 | `az_azdtn_2_7_3` | cl. 5.1 | verified | recommended | single occupancy |
| bedroom_double | market_default | min_area | 12.0 | m2 | `az_azdtn_2_7_3` | cl. 5.1 | verified | recommended | two persons |
| bedroom | market_default | min_area | 8.0 | m2 | `az_azdtn_2_7_3` | cl. 5.1 | verified | recommended | in a mansard |
| kitchen | market_default | min_area | 9.0 | m2 | `az_azdtn_2_7_3` | cl. 5.1 | verified | recommended | *mətbəx* |
| kitchen_zone | market_default | min_area | 6.0 | m2 | `az_azdtn_2_7_3` | cl. 5.1 | verified | recommended | cooking zone in a kitchen-dining room |
| bathroom | market_default | min_area | 3.2 | m2 | `az_azdtn_2_7_3` | cl. 5.1 | verified | recommended | *hamam otağı* |
| bathroom_combined | market_default | min_area | 3.8 | m2 | `az_azdtn_2_7_3` | cl. 5.1 | verified | recommended | *birləşdirilmiş sanitar qovşağı* |
| habitable_room | market_default | min_clear_height | 2700 | mm | `az_azdtn_2_7_3` | cl. 5.2 | verified | statutory | same 2.7 m as apartments; `qəbul edilir` |
| corridor / antresol | market_default | min_clear_height | 2100 | mm | `az_azdtn_2_7_3` | cl. 5.2 | verified | statutory | same 2.1 m as apartments |

The **shape** of the market_default row is exactly right: every value is at or
above the corresponding statutory floor (bedroom 9 vs 8, kitchen 9 vs 8, living
room 16 vs 15/16), and it fills the two cells AzDTN 2.7-2 leaves empty —
bathroom 3.2 m² and combined WC/bath 3.8 m², for which **there is no Azerbaijani
statutory area minimum at all**. Same building-type caveat as §3.2 applies:
these are detached-house numbers, so `conf` must degrade on transfer.

### 7.3 The regulator's own occupancy and storey-height assumptions

AzDTN 2.7-2 **Əlavə 1** (Appendix 1) sizes passenger lifts against building
storey count. Its **Note 2** states the assumptions the table was built on, and
they are the only place in the norm where Azerbaijan puts a number on how densely
an apartment is expected to be occupied:

> "Cədvəl **adambaşına 18 m² ümumi mənzil sahəsi**, **mərtəbənin hündürlüyünün
> 2,8 m**, liftin hərəkət intervalının 81–100 s olması hesabı ilə tərtib
> edilmişdir."
>
> *"The table has been compiled on the basis of **18 m² of total apartment area
> per person**, a **storey height of 2.8 m**, and a lift interval of 81–100 s."*

| field | value | unit | src_key | ref | conf | force | note |
|---|---|---|---|---|---|---|---|
| area_per_person | 18.0 | m2 | `az_azdtn_2_7_2` | Əlavə 1, note 2 | verified | recommended | A **design assumption inside a lift-sizing table**, not a housing allocation norm. But it is the AZ regulator's own stated occupancy density and it is the best available bridge from a Brief's occupant count to a target dwelling area. |
| storey_height | 2800 | mm | `az_azdtn_2_7_2` | Əlavə 1, note 2 | verified | recommended | **Floor-to-floor**, against the 2700 mm floor-to-ceiling *clear* minimum of cl. 5.8. The 100 mm difference is thinner than any real slab, so 2.8 m is a lower bound on floor-to-floor in practice. **Cross-reference to ticket 25 item 1** — it bounds the slab thickness the catalogue can offer. |
| lift_car | 2100 × 1100 | mm | `az_azdtn_2_7_2` | Əlavə 1, note 1 | verified | statutory | *"kabinlərinin eni və uzunu ən azı 2100 … 1100 mm olmalıdır"* for 630 kg and 1000 kg lifts. The extraction lost the separator, so **which axis is which is not established** — cl. 4.10 refers to cars of 2100 mm *width* and cars of 2100 mm *depth* separately. Read the PDF before using this. |

**Sanity check.** 18 m²/person against cl. 5.1's recommended totals: a three-room
town apartment at 56–65 m² implies 3.1–3.6 occupants, and a two-room at 44–53 m²
implies 2.4–2.9. Both land where you would expect for the room count, so the two
clauses are mutually consistent rather than accidentally adjacent.

### 7.4 What is still missing for market_default

**Baku private-sector practice and any MIDA (Mənzil İnşaatı Dövlət Agentliyi)
social-housing space standard were NOT obtained** (§8 item 2). So `market_default`
rests entirely on two regulator-published sources — AzDTN 2.7-2 cl. 5.1 and
AzDTN 2.7-3 cl. 5.1 — with no independent check against what Baku developers
actually build.

**This is the weakest tier in the slice, and it is the tier that matters most.**
`market_default` is the profile's `default_tier` and the solver's
`soft_objective_target`: it is what an unstated brief field resolves to and what
the engine aims at. Both its sources are *regulator recommendations for public
housing or for detached houses*, which is a floor on ordinariness rather than a
picture of the market — and the tier model defines it as "what is actually built
and what a Homeowner expects". The two are not the same thing, and where they
diverge the current sources will read low.

The one internal cross-check available is AzDTN 2.7-2's own 18 m²-per-person
assumption (§7.3), which is consistent with cl. 5.1's bands. That is coherence,
not corroboration. **Worth closing before the profile ships.**

---

## 7A. Consolidated three-tier view

The same values, arranged the way `room-constraints.json` wants them, so the
ticket owner can see the shape of the AZ cell without reassembling it. **`null`
means no AZ source supplies it and the cell must stay empty** — not that a number
should be invented.

Areas, m²:

| room_type | `statutory_floor` | `market_default` | `accessible` |
|---|---|---|---|
| living_room (1-room flat) | **15.0** *(statutory)* | 16.0 † | null |
| living_room (2+ rooms) | **16.0** *(statutory)* | 16.0 † | null |
| bedroom, single | **8.0** *(statutory)* | 9.0 † | 9.0 † *(recommended)* |
| bedroom, double | **10.0** *(statutory)* | 12.0 † | null |
| bedroom, mansard | **7.0** *(statutory, conditional)* | 8.0 † | null |
| kitchen | **8.0** *(statutory)* | 9.0 † | **9.0** *(recommended)* |
| kitchen_zone (in kitchen-diner) | **6.0** *(statutory)* | 6.0 † | null |
| kitchen_niche | **5.0** *(statutory, 1-room flats only)* | null | null |
| bathroom | **null** | 3.2 † | null |
| bathroom_combined | **null** | 3.8 † | null |
| wc | **null** | null | null (area); **width 1200 / depth 1600 mm** — see linear table |
| hall / *передняя* | **null** | null | null |
| wardrobe (1-room flat entry) | **2.5** *(statutory)* | null | null |

Clear plan dimensions, mm — **before** ADR 0007 erosion (§6):

| room_type | `statutory_floor` | `market_default` | `accessible` |
|---|---|---|---|
| habitable_room width | **null** ‡ | 3000 † | null |
| kitchen width | **null** ‡ | 2600 † | **2200** *(recommended)* |
| hall / corridor width | **null** ‡ | 1400 † | null |
| bathroom width | **null** ‡ | 1500 † | null |
| wc width | **null** ‡ | 800 † | **1200** *(recommended)* |
| wc depth | **null** ‡ | null | **1600** *(recommended)* |
| wc_with_basin width | **null** ‡ | 1200 † | — |

Clear heights, mm — not subject to ADR 0007 (§6.3 item 5):

| element | `statutory_floor` | note |
|---|---|---|
| habitable room, kitchen | **2700** *(statutory)* | nationally, no climatic carve-out |
| intra-apartment corridor, hall, antresol | **2100** *(statutory)* | |

**†** = AzDTN 2.7-3, a **detached-house** norm. On transfer to the apartment
case, `conf` must degrade from `verified` to `derived`/`engine_choice` with a
`note` recording the building-type transfer, and `force` must **not** be reported
as `statutory` for an apartment. §3.2.

**Accessible column provenance:** the kitchen 9.0 m² / 2200 mm and the WC
1200 × 1600 mm are **ВСН 62-91\*** (cl. 3.1.8, cl. 2.8.8), read first-hand. The
bedroom 9.0 m² carries **†** because it is AzDTN 2.7-3's, not ВСН 62's — and note
that AzDTN 2.7-3 recommends the *same* 9 m² for an ordinary bedroom, i.e. it gives
the wheelchair user no uplift at all. The kitchen is the opposite case and the
only genuine uplift in the tier: two independent sources agree on 9 m², and it
sits **+1.0 m² above** the 8.0 m² statutory floor.

**‡** = null **by design, not by omission** — AzDTN 2.7-2 cl. 5.6 delegates these
to ergonomics, and SP 54.13330.2022 cl. 5.11 does the same. Ticket 19's invariant
layer binds here. §3.1, §11.5.

The `accessible` column is now populated where ВСН 62-91\* speaks — kitchen
9.0 m² / 2200 mm, WC 1200 × 1600 mm — all `verified` against the document and all
`force: recommended`, never `statutory`, because Azerbaijan invokes ВСН 62 only
as a recommendation (§5). Everything ВСН 62 does not speak to stays `null`:
**it sets no accessible minimum for a living room, a bedroom, a bathroom or a
hall.** The one dwelling *area* uplift in the entire tier is the kitchen's
+1.0 m².

**Read the empties as the finding.** Nine of the thirteen area cells and all six
width cells at `statutory_floor` are `null`, and that is what an honest AZ profile
looks like: Azerbaijani law fixes habitable-room and kitchen areas and nothing
else about a room's plan. A profile that fills those cells is asserting law that
does not exist.

---

## 8. What could NOT be obtained

Stated plainly, per the ticket.

1. ~~ВСН 62-91\* full text~~ — **OBTAINED after all**, on a second attempt, and read
   first-hand. See §5. The `accessible` tier is no longer empty. Noted here only
   because `docs.cntd.ru` returned HTTP 000 throughout and would have been the
   obvious first stop; `files.stroyinf.ru` served the full text.

2. **Baku market practice and any MIDA (Mənzil İnşaatı Dövlət Agentliyi)
   social-housing space standard — NOT OBTAINED.** §7.4. The `market_default` tier
   therefore rests entirely on two regulator-published sources (AzDTN 2.7-2 cl. 5.1
   and AzDTN 2.7-3 cl. 5.1) with no independent check against what Baku developers
   actually build. Given that `market_default` is the **default tier** and the
   solver's objective target, this is worth closing before the profile ships.
3. **The two Azerbaijani accessibility instruments** (Azərdövləttikintikom orders
   No. 42/2002 and No. 92/2001) are named in the official SİYAHI but their texts
   are not published on arxkom.gov.az, e-qanun.az or huquqiaktlar.gov.az as far as
   this session could find. They are the only AZ-specific accessibility documents
   that exist, and they appear to be **effectively unobtainable online**. That is
   itself a finding: Azerbaijan's accessible tier cannot be built to `verified`
   from freely-published sources.
4. **The State Register entry for AzDTN 2.7-2** could not be opened.
   `huquqiaktlar.gov.az` serves a TLS certificate valid only for `e-qanun.az`, so
   the fetch fails on hostname mismatch; `e-qanun.az/framework/48625` is the
   registry entry but the site is a JavaScript SPA with no reachable document
   body or PDF endpoint. The registration number and approval details are taken
   from the norm's own front matter instead, which is a primary source for them —
   and the SİYAHI independently corroborates the approval decision and date.
   **Not a gap in the values, only in the second confirmation of the metadata.**

5. **The three Azerbaijani amendment acts to SNiP 2.08.01-89\*** (26.11.2002
   No. 2; Collegium 28.04.2004 No. 4; order 05.01.2005 No. 4) — named in an
   earlier AZ list of norms in force, texts not located. They are the likely
   origin of AZ's divergences from the Russian text (§11.4) and would settle
   whether the 15 m² living room and the national 2.7 m height date from 2002 or
   from 2021. Not needed for the profile; recorded as an open historical
   question.

6. **The pre-1999 original wording of SNiP 2.08.01-89 cl. 2.4** (before Изм. 3
   restarred it as 2.4\*) could not be obtained — ГАРАНТ paywalls its
   previous-edition links. This is the most likely home of the ticket's 12 m² and
   6 m² figures. **Until it is read, 12 m² and 6 m² are unsourced and must not be
   cited from any document.**
7. **Diacritics and Cyrillic** are destroyed by the arxkom PDFs' font encoding
   (§1). All numerals survived; Azerbaijani text was re-diacriticised by hand and
   the one Cyrillic string that matters (the СНиП 2.08.01-89\* repeal) was
   independently corroborated by the SİYAHI's *"СНиП 2.08.01-89\* əvəzinə"* entry.
8. **No Azerbaijani source gives a minimum WC or bathroom AREA for an
   apartment.** AzDTN 2.7-2 requires the rooms (cl. 5.2) and sets no area for
   them. The statutory floor for wet rooms in AZ apartments is genuinely empty and
   must be `null`, with the ergonomic layer binding.
9. **No Azerbaijani source gives an intra-apartment clear plan width.** See §3.1.
   This is by design, not by omission.
10. **A paywalled aggregator was observed FABRICATING clause text** for
   СНиП 2.08.01-89\* — inventing clause numbers and coefficients rather than
   returning an error or an empty result. **No value in this note comes from an
   aggregator.** Every number in §§2, 3, 5, 7 and 11 was taken from a retrieved
   full text: the two AzDTN PDFs from the issuing committee's own register, the
   СНиП from the Gosstroy printed edition scan, the SP line from `meganorm.ru`
   full texts, and ВСН 62-91\* from `files.stroyinf.ru`. Recorded because it is a
   live hazard for anyone re-checking this work, and because an aggregator that
   hallucinates instead of erroring defeats the `verified`/`reported` distinction
   entirely — it produces text that *looks* first-hand.

11. **Whether AzDTN 2.7-2 has been amended since 2021-11-30** — the SİYAHI of April
   2026 lists only the 30.11.2021 approval with no amendment, and the PDF served
   is unchanged since 2022-02-08, so no amendment is apparent. Not positively
   confirmed against a change register.

---

## 9. `sources` block

Shaped to match `data/standards/room-constraints.json`. **Do not paste this into
that file** — ticket 25's owner merges it, and `docs/research/_az-partials/` is
the staging area.

```json
{
  "az_azdtn_2_7_2": {
    "title": "AzDTN 2.7-2 — Yaşayış binaları. Layihələndirmə normaları (Residential buildings. Design norms)",
    "issuer": "Azərbaycan Respublikası Dövlət Şəhərsalma və Arxitektura Komitəsi (State Committee on Urban Planning and Architecture of the Republic of Azerbaijan)",
    "date": "approved 2021-11-30 by Collegium decision No. 03; in force from 2021-11-30; State Register of Legal Acts No. 15202111300003; publication code AzDAK-TN/Q No. 0030-2021; Baku 2021, 28 pp.",
    "url": "https://arxkom.gov.az/qanunvericilik/normativler/binalarin-muhendis-sistemleri/zhilye-zdaniya",
    "licence": "Azerbaijani state normative legal act, published free of charge by the issuing committee; no explicit open licence is asserted. Individual values cited per value; the source's own tables are NOT reproduced and the PDF is NOT redistributed (findings 7.6 items 5-8).",
    "force": "statutory",
    "force_note": "A technical normative legal act within the meaning of Art. 3.0.26 of the Urban Planning and Construction Code (Law 392-IVQ of 2012-06-29), listed in the annually published SİYAHI required by Art. 14.2, and made binding by Art. 14.3 ('normativ sənədlərin tələblərinə əməl edilməlidir'). WITHIN the norm, mandatory and recommended provisions are separated by grammatical register per the AzDTN system's governing document: 'az olmamalıdır' / 'edilməlidir' = məcburi (mandatory); 'tövsiyə olunur' = tövsiyə (recommended). Cl. 5.7 (minimum room areas) is mandatory. Cl. 5.1 (recommended apartment totals) is NOT. Applies to new multi-apartment residential buildings up to 75 m in height.",
    "supersedes": "СНиП 2.08.01-89* «Жилые здания» — expressly terminated on Azerbaijani territory by this norm's entry into force.",
    "reusable": false
  },
  "az_azdtn_2_7_3": {
    "title": "AzDTN 2.7-3 — Fərdi yaşayış evləri. Layihələndirmə normaları (Individual dwelling houses. Design norms)",
    "issuer": "Azərbaycan Respublikası Dövlət Şəhərsalma və Arxitektura Komitəsi",
    "date": "approved 2023-11-21 by Collegium decision No. 3-35/3-2-6/2023; in force from 2023-12-06 (SİYAHI records 2023-11-23); State Register of Legal Acts No. 15202311235326; publication code AzDAK-TN/Q No. 0040-2023; Baku 2023, 12 pp.",
    "url": "https://arxkom.gov.az/qanunvericilik/normativler/binalarin-muhendis-sistemleri/azdtn-27-3-ferdi-yasayis-evleri-layihelendirme-normalari",
    "licence": "As az_azdtn_2_7_2.",
    "force": "statutory",
    "force_note": "Same legal basis as az_azdtn_2_7_2. BUILDING TYPE IS DIFFERENT AND THIS IS LOAD-BEARING: it binds fərdi yaşayış evləri (detached/individual houses of at most 3 storeys and 12 m), NOT multi-apartment buildings. Its numbers are statutory for houses and are at most a market_default proxy for apartments; any value transferred to the apartment case must degrade conf to derived or engine_choice and must NOT be described as a statutory minimum for an apartment. Within cl. 5.1 the AREA list is recommended ('tövsiyə edilir') while the WIDTH list is mandatory ('qəbul edilməlidir').",
    "reusable": false
  },
  "az_sehersalma_mecellesi_2012": {
    "title": "Azərbaycan Respublikasının Şəhərsalma və Tikinti Məcəlləsi (Urban Planning and Construction Code of the Republic of Azerbaijan)",
    "issuer": "Milli Məclis of the Republic of Azerbaijan, approved by Law No. 392-IVQ",
    "date": "2012-06-29",
    "url": "https://fhn.gov.az/storage/pages/217/3922012.pdf",
    "licence": "Azerbaijani legislation, published by state bodies. Short clause quotation only.",
    "force": "statutory",
    "force_note": "The instrument that gives every AzDTN its binding force. Art. 3.0.26 defines normative documents as technical normative legal acts; Art. 14.3 requires compliance; Art. 14.2 requires annual publication of the list; Art. 15.1.5 places design norms inside the system. This is the source the acceptance validator's 'statutory' force wording ultimately rests on for AZ.",
    "reusable": false
  },
  "az_siyahi_2026": {
    "title": "Azərbaycan Respublikasında qüvvədə olan şəhərsalma və tikintiyə dair normativ sənədlərin SİYAHISI (List of normative documents on urban planning and construction in force in the Republic of Azerbaijan)",
    "issuer": "Azərbaycan Respublikası Dövlət Şəhərsalma və Arxitektura Komitəsi",
    "date": "April 2026 edition",
    "url": "https://arxkom.gov.az/qanunvericilik/normativler",
    "licence": "As above.",
    "force": "statutory_guidance",
    "force_note": "The list required by Art. 14.2 of the Code. Used here as the AUTHORITY ON WHAT IS AND IS NOT IN FORCE — it is how we established that AzDTN 2.7-2 replaced СНиП 2.08.01-89*, that ВСН 62-91* is carried, and that SNiP 35-01-2001, SP 59.13330 and SP 54.13330 are absent from Azerbaijani law. Not itself a source of dimensional values.",
    "reusable": false
  },
  "az_azdtn_system_1994": {
    "title": "Azərbaycan Respublikası Dövlət tikinti normativ sənədləri sisteminin Əsas müddəaları (Konsepsiya) — Basic provisions of the system of state construction normative documents",
    "issuer": "Azərbaycan Respublikası Dövlət Tikinti və Arxitektura Komitəsi (Azərdövləttikintikom)",
    "date": "Baku, 1994",
    "url": "https://arxkom.gov.az/qanunvericilik/normativler/rehberedici-ve-metodiki-senedler/tikinti-normativ-senedleri-sistemlerinin-esas-muddealari",
    "licence": "As above.",
    "force": "statutory_guidance",
    "force_note": "The AzDTN system's own governing document. Sections 3.1, 3.2, 3.4, 3.6 and 5.2 define the məcburi/tövsiyə (mandatory/recommended) split, require it to be textually separated within each norm, state that mandatory norms are expressed as a minimum requirement or maximum limit, and locate enforcement in liability for breach of mandatory requirements. This is the source of the force-classification rule in the findings section 4.2 — it is why 'force' here is derived from the clause's verb rather than from the tier's name. Self-described as a Konsepsiya (concept), so it is the system's methodology, not itself a dimensional norm.",
    "reusable": false
  },
  "su_snip_2_08_01_89": {
    "title": "СНиП 2.08.01-89* «Жилые здания» (Residential buildings)",
    "issuer": "USSR Gosstroy; edition read is the Gosstroy printed edition, Moscow 2000, incorporating Изм. 1 (30.04.1993 No. 18-12), Изм. 2 (11.10.1994 No. 18-21), Изм. 3 (Gosstroy Russia decree No. 42 of 03.06.1999) and Изм. 4 (No. 112 of 20.11.2000)",
    "date": "1989, as amended to 2000",
    "url": "https://files.stroyinf.ru/Data2/1/4294854/4294854790.pdf",
    "licence": "Former-USSR / Russian normative text, freely mirrored. Read to establish facts; PDF not redistributed.",
    "force": "superseded",
    "force_note": "SUPERSEDED IN AZERBAIJAN BY NAME. AzDTN 2.7-2's front matter expressly terminates its legal force on Azerbaijani territory from 2021-11-30, and the SİYAHI records AzDTN 2.7-2 as being 'СНиП 2.08.01-89* əvəzinə' (in place of it). It may be cited for lineage. It MUST NOT be cited as a live Azerbaijani minimum, and no value may be attributed to AZ through it. Separately: between roughly 2002 and 2021 the version in force in AZ was NOT this Russian text — it carried three Azerbaijani amendment acts (26.11.2002 No. 2; Collegium 28.04.2004 No. 4; order 05.01.2005 No. 4) whose content could not be obtained. In Russia its repeal is itself contested: Gosstroy decree No. 109 of 23.06.2003 declared it inoperative from 2003-10-01, but the Ministry of Justice refused that decree state registration (letter No. 07/3971-ЮД of 16.04.2004).",
    "reusable": false
  },
  "ru_sp_54_13330": {
    "title": "СП 54.13330 «СНиП 31-01-2003 Здания жилые многоквартирные» (Multi-apartment residential buildings)",
    "issuer": "Gosstroy Russia (SNiP 31-01-2003); Minstroy Russia (SP editions 2011, 2016, 2022)",
    "date": "SNiP 31-01-2003; SP editions 2011, 2016, 2022. Изм. No. 2 to the 2022 edition (Minstroy order No. 938/пр of 27.12.2024, in force 2025-08-22) does not touch cl. 5.11 or 5.12.",
    "url": "https://rkc56.ru/attach/orenburg/docs/Gosstandart_RF/SP-54.13330.2022-Mnogokvartirnie.pdf",
    "licence": "Russian normative text, freely published. Read to establish facts; not redistributed.",
    "force": "foreign_not_applicable",
    "force_note": "RUSSIAN, NEVER AZERBAIJANI LAW, and absent from the Azerbaijani SİYAHI. Carried here ONLY as the comparator that shows AzDTN 2.7-2 follows the modern SP line rather than the 1989 SNiP, and that the delegation of intra-apartment dimensions to ergonomics is family-wide. NO VALUE FROM THIS SOURCE MAY REACH THE AZ PROFILE, and the validator must never derive an AZ disclosure from it. Its own force in Russia is unsettled and must not be copied by analogy: section 5 was excluded from SNiP 31-01-2003's mandatory introduction; decree No. 815 of 28.05.2021 then listed cl. 5.7/5.8 of the 2016 edition as mandatory; No. 815 was repealed from 2024-09-01 by decree No. 589 of 06.05.2024; and Art. 6 of 384-ФЗ was rewritten by 653-ФЗ from the same date, abolishing the mandatory/voluntary list system in favour of a 'register of requirements'. Whether cl. 5.11 of the 2022 edition sits in that register was not confirmed.",
    "caution": "The widely-mirrored tiflocentre.ru copy of SP 54.13330.2022 is ABRIDGED — section 5 jumps from 5.2 to section 6 — and reading it yields the false conclusion that the 2022 edition dropped the room minima.",
    "reusable": false
  },
  "ru_sp_55_13330_2016": {
    "title": "СП 55.13330.2016 «Дома жилые одноквартирные» (Single-family dwelling houses)",
    "issuer": "Minstroy Russia",
    "date": "2016",
    "url": "https://meganorm.ru/Data2/1/4293748/4293748498.htm",
    "licence": "Russian normative text, freely published. Read to establish facts; not redistributed.",
    "force": "foreign_not_applicable",
    "force_note": "RUSSIAN, NEVER AZERBAIJANI LAW. Carried only to locate where the SNiP-family clear widths actually live: cl. 6.1, single-family houses, and even there only as a relaxation for RECONSTRUCTED houses. This is the exact structural parallel to AzDTN 2.7-3 carrying widths while AzDTN 2.7-2 does not, and it is why transferring house widths onto apartments must degrade conf.",
    "reusable": false
  },
  "ru_vsn_62_91": {
    "title": "ВСН 62-91* «Проектирование среды жизнедеятельности с учетом потребностей инвалидов и маломобильных групп населения» (Design of the living environment taking account of the needs of persons with disabilities and low-mobility groups)",
    "issuer": "USSR State Committee for Architecture and Urban Planning under Gosstroy USSR (Goskomarkhitektura); drafted by TsNIIEP im. B. S. Mezentseva",
    "date": "approved by order No. 134 of 1991-10-04; in force from 1992-01-01; the trailing asterisk denotes the amendment approved by order No. 166 of 1991-11-29 — the same order the Azerbaijani SİYAHI cites, which confirms AZ carries the amended 62-91* text",
    "url": "https://files.stroyinf.ru/Data2/1/4294854/4294854753.htm",
    "licence": "Former-USSR departmental norm, freely mirrored. Read to establish facts; not redistributed.",
    "force": "recommended",
    "force_note": "AZERBAIJAN'S ACCESSIBILITY INSTRUMENT, not SNiP 35-01-2001 and not SP 59.13330 — those are Russian and return ZERO hits across all 211 pages of the Azerbaijani SİYAHI. ВСН 62-91* IS carried in the SİYAHI (p. 66) as in force. CRITICAL FOR THE WARN WORDING: the clauses are drafted in the Russian mandatory register («должна быть не менее»), but that is the Soviet drafter's register, not Azerbaijan's — the only Azerbaijani instrument that invokes the document (AzDTN 2.7-3 cl. 4.17) does so with 'tövsiyə edilir' (recommended). So on the AZ side this is RECOMMENDED. The accessible tier's disclosure must never say 'statutory'. Note also that Ukraine repealed this norm in 2006 and Russia largely displaced it with SNiP 35-01-2001; Azerbaijan did neither.",
    "scope_warning": "cl. 5.1.3 sets communal room areas for дома-интернаты (residential institutions serving a whole living group), NOT rooms in a dwelling. Do not mine it into the wet-room row — a 12 m2 'bathroom' is a shared institutional facility.",
    "conflict": "cl. 3.1.2* caps specialised residential buildings at 3 storeys; AzDTN 2.7-2 cl. 4.3 sets 5 storeys for buildings for families of persons with disabilities and 9 for older people. AzDTN 2.7-2 wins — it is mandatory AZ law under Art. 14.3 of the Code, whereas ВСН 62 reaches AZ only through a recommendation in a detached-house norm.",
    "reusable": false
  }
}
```

### Force vocabulary used

`statutory` · `statutory_guidance` · `recommended` · `superseded` ·
`foreign_not_applicable`. The last is new and is needed: SNiP 31-01-2003,
SP 54.13330, SNiP 35-01-2001 and SP 59.13330 are all *live law somewhere*, which
makes `superseded` wrong for them, but they are not law in Azerbaijan, which
makes any of the others wrong too. If they are carried in `sources` at all they
need that value, and the validator must never produce a disclosure from them for
an AZ plan.

---

## 10. Cross-references handed to other tickets

Recorded, not decided.

| Observation | Belongs to |
|---|---|
| AzDTN 2.7-2 cl. 5.6 delegates all room plan dimensions to **ergonomics** by name. The AZ profile's plan-dimension floors are therefore *supposed* to be the invariant layer. | ticket 19, *Ergonomic minima and the constraint table's missing half* |
| AzDTN 2.7-2 cl. 7.3: boiler room glazing 0.03 m² per 1 m³ of volume, plus an opening light. A plant-room ratio; the habitable-room light ratio was not looked for in this slice. | ticket 25 item 3, `win.area_ratio` |
| Cl. 5.1 measures *ümumi sahə* with an explicit exclusion list (balconies, terraces, verandas, loggias, vestibules, unheated ancillary rooms, apartment tambour) — i.e. a binary count of enclosed space, not German-style fractional weighting. | ticket 25 item 7 / *Area measurement convention* |
| Cl. 5.9: a bedroom must not be a through-route. This is `is_private` as law and a direct consumer for the C6 reachability predicate. | ticket 07, *Acceptance validator spec* |
| Cl. 5.2: the required room set for an AZ apartment (kitchen or niche, hall, bath or shower, WC or combined, store). Direct consumer for brief defaulting. | ticket 10, *Brief schema and parsing contract* |
| Cl. 5.4: loggias/balconies are *required* in Azerbaijan absent stated noise/dust conditions. A regional convention with statutory force and no analogue in DE or UK. | ticket 25, profile scope |
| AzDTN 2.7-2 cl. 8.3: 1200 mm balustrade height — compare UK AD K. | ticket 19 / ticket 5 comparator table |
| AzDTN 2.7-2 Əlavə 1 note 2 assumes a **2.8 m floor-to-floor storey height** against the 2.7 m clear minimum. The 100 mm gap is thinner than any real slab, so it bounds what slab thickness the catalogue may offer. §7.3. | ticket 25 item 1, thickness catalogue |
| AzDTN 2.7-2 Əlavə 1 note 2 assumes **18 m² total apartment area per person** — the only occupancy density Azerbaijani norms state, and the bridge from a Brief's occupant count to a target area. §7.3. | ticket 10, brief defaulting |
| ADR 0007's "every dimensional minimum" should carve out **areas and storey heights** explicitly; only plan-linear minima are eroded by `t_int`. §6.3 item 5. | ADR 0007 |
| **WC clear depth is door-swing dependent** — SP 55.13330.2016 cl. 6.1 sets 1.2 m on the pan axis with the door opening outward but 1.5 m opening inward, and SNiP 2.08.01-89\* cl. 2.5 *required* WC/bath doors to open outward. No AZ instrument states either. A WC's real footprint depends on which way its door swings, which the engine controls. | ticket 19 (ergonomic layer) |
| SNiP 2.08.01-89\* cl. 2.6: a WC may not open directly off a kitchen or a habitable room, and wet rooms may not sit over habitable rooms or kitchens. Repealed in AZ, but it is the origin of wet-room clustering (C6 item 5) and a plausible `engine_choice`. | ticket 07 |
| The `sources` schema needs a **`force: foreign_not_applicable`** value. SNiP 31-01-2003, SP 54.13330, SP 55.13330, SNiP 35-01-2001 and SP 59.13330 are live law *somewhere*, so `superseded` is wrong, but they are not law in AZ, so nothing else fits. §9. | ticket 25 / schema |

---

## 11. The superseded ancestor — SNiP 2.08.01-89\*, read first-hand

**This is no longer Azerbaijani law** (§4.4). It is recorded because the ticket
asked for the lineage, because it *was* AZ law from independence until
2021-11-30, and because comparing it against AzDTN 2.7-2 shows exactly where the
Azerbaijani drafter diverged. Every value here is `force: superseded` for AZ and
**may not reach the AZ profile as a live minimum**.

The 2000 Gosstroy printed edition (incorporating Изм. 1–4: 30.04.1993 № 18-12;
11.10.1994 № 18-21; 03.06.1999 № 42; 20.11.2000 № 112) was read first-hand in a
scan of the official edition at
`https://files.stroyinf.ru/Data2/1/4294854/4294854790.pdf`, corroborated against
ГАРАНТ (`base.garant.ru/2306190/`) and three independent digitizations.

### 11.1 The ticket's "classic numbers" were folklore, and three of them are wrong

The ticket listed *общая жилая комната* 12 m², *кухня* 6 m², *коридор* 1.4 m as
REPORTED values to verify. Verified — and **they are not in the document**:

| ticket's expectation | what cl. 2.4\* / 2.7 actually say | verdict |
|---|---|---|
| living room 12 m² | **14 m²** (1-room flat) / **16 m²** (2+ rooms) | **wrong** |
| kitchen 6 m² | **8 m²**; relaxed to **5 m²** for a kitchen or kitchen-niche in type 1А and 2А city flats; **7 m²** in an added mansard storey. The string "6 m²" for a kitchen appears **nowhere** in the document. | **wrong** |
| corridor 1.4 m | **0.85 m** for the *внутриквартирный коридор*. 1.4 m is the ***передняя*** (entrance hall), a different room. | **wrong — confused two rooms** |
| передняя 1.4 m | **1.4 m** | correct |
| bedroom 8 m² | **8 m²**, but as a single floor for "other habitable rooms" with **no two-person uplift**. The 10 m²-for-two rule is *not* in this norm. | half right |

The 12 / 6 figures most likely belong to the **original 1989 wording** of cl. 2.4,
before Изм. 3 of 1999 restarred it as 2.4\*. That pre-1999 text could not be
obtained — ГАРАНТ paywalls its "previous edition" links — so **12 m² and 6 m²
remain unsourced and must not be cited**.

This is precisely the failure mode the ticket's "REPORTED, never VERIFIED" rule
exists to catch, and it caught it.

### 11.2 Values, all verified first-hand

| provision | ref | value | unit | force (for AZ) |
|---|---|---|---|---|
| living room, 1-room flat | cl. 2.4\* | 14.0 | m² | superseded |
| living room, 2+ rooms | cl. 2.4\* | 16.0 | m² | superseded |
| other habitable rooms **and kitchen** | cl. 2.4\* | 8.0 | m² | superseded |
| kitchen / kitchen-niche, type 1А and 2А city flats | cl. 2.4\* | 5.0 | m² | superseded |
| bedroom and kitchen in an added mansard storey (conditional on living room ≥ 16 m²) | cl. 2.4\* | 7.0 | m² | superseded |
| clear height, habitable rooms | cl. 1.1\* | 2500 (**2700** in climatic subregions IА, IБ, IГ, IД, IIА) | mm | superseded |
| clear height, intra-apartment corridors | cl. 1.1\* | 2100 | mm | superseded |
| **kitchen clear width** | **cl. 2.7** | **1700** | mm | superseded |
| ***передняя*** **(entrance hall) clear width** | **cl. 2.7** | **1400** | mm | superseded |
| **intra-apartment corridor clear width** | **cl. 2.7** | **850** | mm | superseded |
| **WC (*уборная*) clear width × min depth** | **cl. 2.7** | **800 × 1200** | mm | superseded |
| — *wheelchair-family flats* — kitchen width | cl. 2.7 | 2200 | mm | superseded |
| — *передняя* width (with wheelchair storage) | cl. 2.7 | 1600 | mm | superseded |
| — intra-apartment corridor width | cl. 2.7 | 1150 | mm | superseded |
| — bathroom or combined WC/bath, W × D | cl. 2.7 | 2200 × 2200 | mm | superseded |
| — WC with washbasin, W × D | cl. 2.7 | 1600 × 2200 | mm | superseded |
| — balcony/loggia depth (and a loggia or balcony is **obligatory**) | cl. 2.2\* | 1400 | mm | superseded |
| dormitory room, per resident (≤3 residents, room width ≥ 2200 mm, non-through) | cl. 2.9 | 6.0 | m² | superseded |
| daylight ratio, habitable rooms and kitchens (window : floor) | cl. 1.3\* | max 1:5.5, **min 1:8** (1:10 for mansard windows) | ratio | superseded — **cross-ref ticket 25 item 3** |

Composition rules, verified: cl. 2.2\* required room set (habitable rooms plus
kitchen, *передняя*, bath or shower, WC, store or built-in cupboards); cl. 2.5
combined WC/bath permitted only in 1-room flats and **WC/bath doors must open
outward**; cl. 2.6 a WC may not open directly off a kitchen or habitable room
(except in flats for families with disabilities) and wet rooms may not sit
directly over habitable rooms or kitchens.

Scope, verified: quartier houses including houses for the elderly and for
families with wheelchair users, plus dormitories, **up to 25 storeys**.

### 11.3 The divergence table — and why the fallback would have failed

| provision | **AZ, AzDTN 2.7-2 cl. 5.7/5.8 (statutory, 2021)** | SNiP 2.08.01-89\* (superseded) | diverged? |
|---|---|---|---|
| living room, 1-room flat | **15 m²** | 14 m² | **yes, +1** |
| living room, 2+ rooms | 16 m² | 16 m² | no |
| bedroom | **8 m², and 10 m² for two persons** | 8 m², no occupancy uplift | **yes, new rule** |
| kitchen | **8 m², as its own line** | 8 m², bundled with bedrooms | same number, restructured |
| kitchen-niche | **5 m², one-room flats generally** | 5 m², only flat types 1А / 2А | **yes, widened** |
| mansard relaxation | 7 m², conditional on living room ≥ 16 m² | 7 m², same condition | no |
| entry wardrobe, 1-room flat | **2.5 m²** | *not present* | **yes, new** |
| clear height | **2700 mm everywhere** | 2500 mm, 2700 only in cold subregions | **yes — AZ took the cold-climate figure nationally** |
| intra-apartment corridor height | 2100 mm | 2100 mm | no |
| kitchen / hall / corridor / WC **clear widths** | ***deleted — handed to ergonomics, cl. 5.6*** | 1700 / 1400 / 850 / 800×1200 mm | **yes — deliberately removed** |

**Two of these would have poisoned the profile** had we followed the ticket's
fallback and published the ancestor's numbers under an AZ label:

1. **Clear height.** We would have published 2500 mm. Azerbaijan requires
   **2700 mm**, everywhere, with no climatic carve-out. A 200 mm error on every
   storey of every plan.
2. **Clear widths.** We would have published 850 mm intra-apartment corridors as
   an AZ statutory minimum. Azerbaijan has **no such minimum** — it repealed the
   clause and replaced it with a delegation to ergonomics. Printing "below
   statutory minimum" against an 900 mm corridor in an AZ plan would have been a
   false legal claim about a rule that was repealed in 2021. **That is exactly the
   C8 violation the tier model's `statutory_floor_note` warns about**, and the
   only thing that prevented it was obtaining the actual document.

### 11.4 A wrinkle worth recording

Between roughly 2002 and 2021 the version of SNiP 2.08.01-89\* in force in
Azerbaijan was **not the Russian text**. An earlier Azerbaijani list of norms in
force carries it *"with the amendments approved by decision No. 2 of 26.11.2002,
the Collegium decision No. 4 of 28.04.2004, and order No. 4 of 05.01.2005 of the
State Committee on Urban Planning and Architecture"*. **Those three Azerbaijani
amendment acts could not be located**, so their content is unknown. They are the
most likely origin of AZ's divergences in §11.3 — the 15 m² living room, the
10 m² two-person bedroom and the national 2700 mm height look like an Azerbaijani
amendment carried forward into AzDTN 2.7-2 rather than a 2021 invention.

Recorded because it forecloses a tempting shortcut: **"AZ inherited SNiP
2.08.01-89\*, so the Russian text gives AZ's numbers" is false in both
directions** — false before 2021 because of the national amendments, and false
after 2021 because of the repeal.

### 11.5 The Russian successor line — and the convergence that matters

Not AZ law, never was, and absent from the SİYAHI. Read first-hand anyway
(SNiP 31-01-2003 Gosstroy 2004 print; SP 54.13330 editions 2011, 2016 and 2022;
SP 55.13330.2016) because it answers the question "did AZ invent cl. 5.6, or is
this how the whole family now works?"

**Areas** — clause 5.7 in 2003/2011/2016, renumbered **5.11** in
SP 54.13330.2022, values unchanged across all four editions, all in the mandatory
drafting register (*должна быть … не менее*):

| provision | RU, SP 54.13330 cl. 5.11 | **AZ, AzDTN 2.7-2 cl. 5.7** |
|---|---|---|
| living room, 1-room flat | 14 m² | **15 m²** |
| living room, 2+ rooms | 16 m² | 16 m² |
| bedroom | 8 m² (**10 m² for two**) | 8 m² (**10 m² for two**) |
| kitchen | 8 m² | 8 m² |
| kitchen zone in a kitchen-diner | 6 m² | 6 m² |
| kitchen / kitchen-niche, 1-room flats | 5 m² | 5 m² |
| bedroom & kitchen in a mansard (living room ≥16 m²) | 7 m² | 7 m² |
| entry wardrobe, 1-room flat | *not present* | **2.5 m²** |
| clear height | 2.7 m in subdistricts IА IБ IГ IД **IVА**, else **2.5 m** | **2.7 m, nationally** |
| corridor / hall / antresol clear height | 2.1 m | 2.1 m |

So the AZ norm is closest to the **modern Russian SP line**, not to the 1989
SNiP — it carries the 10 m²-for-two rule and the 6 m² kitchen-zone rule that
SNiP 2.08.01-89\* does **not** have. AZ then made three of its own changes: the
1-room living room up to 15 m², a 2.5 m² entry wardrobe with no Russian analogue,
and the 2.7 m height applied nationally rather than only in cold subdistricts.

**Widths — the convergence.** SP 54.13330 publishes **no intra-apartment clear
width in any edition**. Verified negative: all four editions were searched for
`ширина передней`, `Ширина подсобных`, `0,85`, `1,7 м`, `в чистоте`; the only
`ширина` clauses concern evacuation corridors, lift lobbies, stair treads and
light wells. And cl. 5.11 opens with the same delegation AzDTN 2.7-2 cl. 5.6
makes:

> *"…следует определять с учётом требований **эргономики** и размещения
> необходимого набора внутриквартирного оборудования и предметов мебели."*

**Both the Azerbaijani and the Russian multi-apartment norms hand intra-apartment
plan dimensions to ergonomics, in near-identical words.** §3.1 is therefore not
an Azerbaijani quirk — it is how this entire norm family now works, and it is
independent corroboration that ticket 19's invariant layer is the right place for
those numbers.

**And the widths the ticket was chasing live in the single-family-house norm.**
SP 55.13330.2016 «Дома жилые одноквартирные» cl. 6.1 gives kitchen 1.7 m,
*передняя* 1.4 m, intra-apartment corridor 0.85 m, bathroom 1.5 m, WC 0.8 m, WC
depth on the pan axis 1.2 m **with the door opening outward** / 1.5 m opening
inward — and even there only as a *relaxation for reconstructed houses*. The
structural parallel to AZ is exact: **AzDTN 2.7-2 (apartments) has no widths;
AzDTN 2.7-3 (houses) does** — the same split, in the same family, in the same
place. §3.2's caution about transferring house widths to apartments is the
correct reading of that split, not an over-scruple.

Note also the door-swing conditional on WC depth, which the AZ house norm does
not carry — worth a cross-reference to ticket 19, since door swing changes the
clear depth a WC actually needs.

**Force, in Russia, is now genuinely unsettled** and should not be copied as a
model. Section 5 was excluded from SNiP 31-01-2003's own mandatory introduction;
ПП РФ № 815 of 28.05.2021 then listed cl. 5.7 and 5.8 of the **2016** edition as
mandatory; № 815 was repealed with effect from 2024-09-01 by ПП РФ № 589 of
06.05.2024; and Art. 6 of 384-ФЗ was rewritten by 653-ФЗ from the same date so
that the mandatory/voluntary two-list system no longer exists at all — force now
depends on entry in the *реестр требований*. Whether SP 54.13330.2022 cl. 5.11
is in that register could not be confirmed. **`reported`, and irrelevant to AZ**,
where Art. 14.3 of the Code is clean and unambiguous. Recorded only so nobody
imports the Russian ambiguity into the AZ `force` field by analogy.

*(Warning for anyone re-checking this: the widely-mirrored `tiflocentre.ru` copy
of SP 54.13330.2022 is **abridged** — its section 5 jumps from 5.2 to section 6 —
and reading it produces the false conclusion that the 2022 edition dropped the
room minima. It did not; they are at 5.11 with **wider** scope than 2016, the
social-housing-fund restriction having been removed.)*

### 11.6 Status in Russia, for completeness

Постановление Госстроя РФ № 109 of 23.06.2003 brought in SNiP 31-01-2003 and
declared 2.08.01-89\* not in force in the RF from 2003-10-01 — but the Ministry of
Justice **refused state registration** of that order (письмо Минюста РФ
№ 07/3971-ЮД of 16.04.2004), which is why ГАРАНТ hedges with *«фактически
прекратил действие»* rather than a clean repeal. `reported` — read as ГАРАНТ's
editorial annotation, not as the text of order 109 itself.

None of this bears on Azerbaijan, where the repeal is clean, express and by name.
