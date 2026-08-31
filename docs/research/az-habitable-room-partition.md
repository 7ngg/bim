# The AZ habitable/auxiliary partition — does AzDTN 2.7-2 actually say what `counts_as_otaq` claims?

**Research date:** 2026-09-01
**Questions:**
**Q-A** — does AzDTN 2.7-2's own text reproduce SP 54's жилая/вспомогательная partition,
and in what words? The engine's `counts_as_otaq` flag is asserted to instantiate that
partition; the claim had never been checked against the AzDTN text directly.
**Q-B** — does AzDTN 2.7-2 (or SP 54 as parent) key a **minimum dwelling area** to the
count of yaşayış otaqları / жилых комнат, and if so is the engine missing a mandatory
whole-dwelling check?

**Method.** Both norms read first-hand this session, from the publishers' own PDFs.
**AzDTN 2.7-2 was re-downloaded live from the issuing committee** (`arxkom.gov.az`)
and is **md5 `4b5da47dd11808cd0aef37a75b01b4e9` — byte-identical** to the copy
`az-statutory-floor-transcription.md` §1.1 read. Every clause number quoted below was
**read directly off the page**, never inferred by position; §7 lists the two that prior
research inferred and that this pass now confirms. Extraction was cross-checked with two
independent engines (`pypdf 6.16.1` and `pymupdf 1.28.2`), and Table 1's cell-to-column
assignment was verified against **glyph x-coordinates**, not against reading order.

---

## 0. Headline

**Q-A — DIFFERENT PARTITION.** AzDTN carries SP 54's *auxiliary-side* definition almost
verbatim and then diverges on three things that matter to this engine. And **neither of
the two clauses `room-constraints.json` cites does what the file says it does**:

- **cl. 5.5 is not an enumeration clause. It is a basement prohibition.** The list of
  habitable rooms lives in a parenthetical gloss inside a rule about which storeys they
  may not be placed on. It is nonetheless the *only* enumeration of yaşayış otaqları in
  the whole norm — verified by exhaustive sweep.
- **cl. 5.2 is not the auxiliary enumeration either. It is a required-composition
  clause.** The real enumeration is the **section 3 definition of `yardımçı sahələr`**,
  which has seven members to cl. 5.2's five, and which is the near-verbatim translation
  of SP 54 **3.1.27**. The engine cites cl. 5.2 for eight types and section 3 for one;
  it has that backwards.
- **⚠️ The decisive divergence — and it is exactly the asymmetry the brief asked about.**
  SP 54 **3.1.18** defines `кухня-столовая` as «**Вспомогательное помещение**» and
  **3.1.27** lists «кухня (или **кухня-столовая**)» inside the auxiliary class.
  **AzDTN deleted the kitchen-diner from that list and put the kitchen-*niche* in its
  place**, and then defined `mətbəx-yemək otağı` in section 3 as an «**otaq**». So
  `kitchen_dining: counts_as_otaq = false` is **right under SP 54 and unsupported —
  arguably contradicted — by the AzDTN text the JSON cites for it.**

**Q-B — THE RULE EXISTS IN BOTH, AND IN AzDTN IT IS RECOMMENDED, NOT MANDATORY.**
**AzDTN 2.7-2 cl. 5.1 / Cədvəl 1 keys a whole-dwelling area band to
«Yaşayış otaqlarının sayı» — the count of habitable rooms** — and its urban lower bounds
are **28 / 44 / 56 / 70 / 84 / 103 m²**, which is **SP 54 Table 5.1's minimum column,
digit for digit, in all six places**. But AzDTN made three changes, all loosening:

1. register **`tövsiyə olunur`** — *recommended*, against SP 54's «Минимальная площадь»
   (and against `az olmamalıdır`, *mandatory*, five paragraphs later in cl. 5.7);
2. scope narrowed to the **state and municipal housing fund**;
3. the closing sentence hands the **private fund** to the client outright.

**So the engine is NOT missing a mandatory whole-dwelling check — AzDTN does not impose
one.** But a real gap exists and it is a different one; §6.

---

## 1. What was read first-hand, and what was not

### 1.1 Obtained

| Document | How |
|---|---|
| **AzDTN 2.7-2** «Yaşayış binaları. Layihələndirmə normaları», Bakı 2021, 30 pp. PDF | **Live download this session** from the issuing committee's own register, `https://arxkom.gov.az/qanunvericilik/normativler/binalarin-muhendis-sistemleri/zhilye-zdaniya` (the URL serves the PDF directly, HTTP 200, 1 188 378 bytes). **md5 `4b5da47dd11808cd0aef37a75b01b4e9`.** Sections 1, 3, 5 (cl. 5.1–5.10), 9 (cl. 9.2, 9.11–9.13), Cədvəl 1, Cədvəl 6, Əlavə 1 and the contents page read. |
| **СП 54.13330.2022** «СНиП 31-01-2003 Здания жилые многоквартирные», 39 pp. PDF | Fetched this session, `https://rkc56.ru/attach/orenburg/docs/Gosstandart_RF/SP-54.13330.2022-Mnogokvartirnie.pdf`, 675 101 bytes. Cl. 3.1.12–3.1.19, 3.1.27–3.1.28, 5.1–5.3, 5.10–5.12, Таблица 5.1, Таблица 7.1 read. |
| `data/standards/room-constraints.json` | Read in full — `flag_semantics`, `ergonomic.counts_as_otaq_sourcing`, all 19 types' flags, `sources`, `source_force_vocabulary`. |
| `data/acceptance/rules.json` | Read in full — all **43** rules enumerated and searched. |
| `docs/research/room-classification-standards.md`, `az-region-profile.md`, `az-statutory-floor-transcription.md`, `az-kitchen-diner-whole-room.md` §12.2, `az-region-profile/daylight.md` | Read as directed. |

### 1.2 The diacritics survive, and that is now twice confirmed

`az-region-profile/minima.md` §1 records that AzDTN's embedded fonts lack a ToUnicode
map and that extraction silently drops `ə ş ç ğ ı ö ü`. `az-statutory-floor-transcription.md`
§1.2 showed that to be a property of the *extractor*. **Confirmed again, independently:**
both `pypdf 6.16.1` and `pymupdf 1.28.2` return every diacritic intact from the
live-downloaded file, including the `²` superscripts in Cədvəl 1. `PYTHONIOENCODING=utf-8`
is still required — the default `cp1252` console codec raises `UnicodeEncodeError` and
truncates. No hand re-diacriticisation was needed anywhere in this document.

### 1.3 NOT obtained — stated plainly

- **No amendment search.** Whether AzDTN 2.7-2 has been amended since 2021-11-30 was not
  re-checked; this pass inherits `az-statutory-floor-transcription.md` §1.3's open
  caveat. The one corroboration available is the same one: the issuing committee is
  serving this exact byte-identical edition today.
- **The Azerbaijani Housing Code (Mənzil Məcəlləsi) was not read this pass.** AzDTN's
  section 3 definition of `otaq` reads like a lift from housing law (§3.1 explains why
  that matters), but it was **not verified against the Code**. The repo's
  `sources.az_housing_code` record cites Art. 12.5 for *total area* only.
- **The lineage of AzDTN's Cədvəl 6 was not verified.** §3.4 observes that its rows match
  the `ГОСТ 30494` / `СНиП 31-01-2003` App. И family in *structure*; neither of those
  texts was read, so that is an observation, **not a sourced claim**.
- **No Azerbaijani legal commentary or expert-review practice** was consulted on whether
  a `kabinet` is treated as a yaşayış otağı. §3.5's finding is from the norm text alone.
- **SP 54's own bracketed references [4] and [21]** (RF Housing Code art. 50 and a
  supplementary source, both cited inside cl. 5.2) were **not followed**.

---

## 2. Q-A — the two clauses, verbatim

### 2.1 AzDTN 2.7-2 cl. 5.5 — and it is a basement rule

Read directly off page 12; the clause number is at the head of its own paragraph.

> **5.5.** Yaşayış binalarında yaşayış otaqlarının (**otaq, qonaq otağı və yataq otağı**)
> kürsülük və zirzəmi mərtəbələrində yerləşdirilməsi yolverilməzdir.

*"In residential buildings the placement of **habitable rooms (room, guest room and
bedroom)** on plinth and basement storeys is impermissible."*

**This is the whole clause.** It is a storey-placement prohibition. The three-member list
is a parenthetical gloss, not a taxonomy. `counts_as_otaq_sourcing` describes it as
"cl. 5.5 enumerates habitable rooms **statutorily**" — the parenthetical is real and the
words are quoted correctly, but the clause's *function* is misdescribed, and eight of the
engine's nineteen types are pinned to it.

⚠️ **It is nonetheless the only such list in the norm.** A sweep of all 30 pages for
`yaşayış otağ*` / `yaşayış otaq*` returns 16 occurrences; cl. 5.5 is the **only** one that
says what the class contains. Every other occurrence uses the term as already-understood
(cl. 5.6, 5.8, 9.12, 9.13, 9.17, 9.20, 9.22 …). So the engine had nowhere better to go —
the defect is the confidence, not the choice.

⚠️ **SP 54's corresponding clause carries no such list.** SP 54 **cl. 5.10** is the same
basement prohibition — «Размещение квартир и жилых комнат в подвальных и цокольных этажах
многоэтажных жилых зданий не допускается» — with **no parenthetical**. AzDTN *added* the
gloss. Its members are therefore AzDTN's own editorial choice, not inherited text.

### 2.2 AzDTN 2.7-2 cl. 5.2 — a composition requirement, not an enumeration

Read directly off page 12.

> **5.2.** Mənzillərdə yaşayış otaqları və yardımçı sahələr: mətbəx (və ya taxça-mətbəx),
> holl, vanna otağı (və ya duş) və tualet (və ya birləşdirilmiş sanitar qovşağı), yığnaq
> otağı (və ya divar təsərrüfat şkafı) **nəzərdə tutulmalıdır**.

*"In apartments, habitable rooms and auxiliary spaces shall be provided: kitchen (or
kitchen-niche), hall, bathroom (or shower) and toilet (or combined sanitary unit),
storage room (or built-in household cupboard)."*

Register `nəzərdə tutulmalıdır` = **məcburi / mandatory**. `rules.json`'s
`programme_rules.source` already cites this clause for the programme minimum and quotes
it correctly (in transliteration); **that citation is verified and stands.**

But note what the clause *is*: everything after the colon is the **auxiliary** list, and
it is a list of what a dwelling must *contain*. It says nothing about the habitable side
beyond naming the class. **It is not an enumeration of `yardımçı sahələr` — it is a
five-item composition minimum drawn from one.**

### 2.3 The enumeration the engine should have cited — section 3

Read directly off page 7, from «3. Əsas anlayışlar» («Basic concepts»):

> **yardımçı sahələr** - sakinlərin məişət və digər ehtiyaclarının ödənilməsi üçün, o
> cümlədən **mətbəx və ya taxça-mətbəx, holl, vanna otağı və ya duş, tualet və ya
> birləşdirilmiş sanitar qovşağı, yığnaq otağı və ya divar təsərrüfat şkafı, paltaryuma
> otağı, istilik generatorı üçün yerləşgələr**;

*"**auxiliary spaces** — for meeting residents' domestic and other needs, **including**:
kitchen or kitchen-niche, hall, bathroom or shower, toilet or combined sanitary unit,
storage room or built-in household cupboard, **laundry room**, premises for the heat
generator."*

Set beside SP 54 **3.1.27**, read directly off its own page (clause number visible; §7):

> **3.1.27 помещение вспомогательное:** Помещение квартиры для обеспечения
> коммуникационных, санитарных, технических и хозяйственно-бытовых нужд, **в том числе:
> кухня (или кухня-столовая), передняя, внутриквартирные холл и коридор, ванная комната
> или душевая, уборная, туалет или совмещенный санузел, кладовая, постирочная, помещение
> теплогенераторной** и т.п.

**The frame is the same and the ending is the same** — both are open lists («o cümlədən»
= «в том числе» = *including*), both close on the laundry and the heat-generator room.
**Three members differ, and each difference costs the engine something:**

| SP 54 3.1.27 | AzDTN sec. 3 | consequence |
|---|---|---|
| кухня (или **кухня-столовая**) | mətbəx və ya **taxça-mətbəx** | **the kitchen-diner leaves the auxiliary class and the kitchen-niche takes its place.** §3.3 |
| **передняя**, внутриквартирные **холл** и **коридор** | **holl** only | AZ collapses three circulation words into one; `entrance_lobby` and `corridor` have no AzDTN word of their own. §3.6 |
| кладовая | yığnaq otağı və ya divar təsərrüfat şkafı | matches SP 54 cl. 5.3's «кладовую (или встроенный шкаф)». No consequence. |

### 2.4 The definitions that decide the hard cases

Also section 3, page 7, read verbatim:

> **otaq** - mənzilin və ya yaşayış evinin **bilavasitə yaşamaq üçün** nəzərdə tutulmuş
> ayrıca hissəsi;
> **mətbəx** - kulinariya və qida qəbulu üçün nəzərdə tutulmuş **otaq**;
> **taxça-mətbəx** - elektrik pilətəsi və mexaniki sorucu-vurucu ventilyasiya ilə təchiz
> edilmiş, yemək hazırlamaq üçün nəzərdə tutulmuş, lakin yemək qəbulu ərazisi olmayan
> **sahə**;
> **mətbəx - yemək otağı** - mənzildə yeməyin hazırlanması və qəbulu üçün ayrıca zonaları
> olan **otaq**;
> **holl** - binaların və mənzillərin **giriş hissəsində** istirahət üçün, gözləmə yeri
> kimi və sairə məqsədlərlə istifadə olunan **sahə**;

*"**otaq** — a separate part of an apartment or dwelling house intended for **direct
habitation**; **kitchen** — an **otaq** intended for cookery and the taking of food;
**kitchen-niche** — a **space** equipped with an electric hob and mechanical supply-exhaust
ventilation, intended for preparing food but **having no area for taking it**;
**kitchen-dining room** — an **otaq** in a dwelling having separate zones for the
preparation and the taking of food; **hall** — a **space** at the **entrance part** of
buildings and apartments used for rest, as a waiting place and for other purposes."*

And the SP 54 definitions they answer to, all read with their numbers on the page:

> **3.1.15 комната жилая:** Часть квартиры, предназначенная для использования в качестве
> места **непосредственного проживания** граждан.
> **3.1.16 кухня: Вспомогательное помещение** с обеденной зоной, а также местом для
> размещения кухонного оборудования…
> **3.1.17 кухня-ниша: Зона**, предназначенная для приготовления пищи, расположенная
> **смежно с жилым или вспомогательным помещением квартиры**…
> **3.1.18 кухня-столовая: Вспомогательное помещение** с обеденной зоной для
> единовременного приема пищи всеми членами семьи…

---

## 3. Q-A — testing the partition against the engine's 19 types

### 3.1 First, the load-bearing correction: `otaq` is not a catch-all

`counts_as_otaq_sourcing` admits `dining`, `study`, `living_dining` and
`living_dining_kitchen` through *"the list's first member `otaq`, which is the
**unqualified catch-all**"*.

**`otaq` is not unqualified.** The norm defines it, in section 3, as «mənzilin və ya
yaşayış evinin **bilavasitə yaşamaq üçün** nəzərdə tutulmuş ayrıca hissəsi» — and that is
a near-word-for-word rendering of SP 54 **3.1.15 комната жилая**: «Часть квартиры,
предназначенная для использования в качестве места **непосредственного проживания**
граждан.» *Bilavasitə yaşamaq* ≡ *непосредственное проживание*.

**`otaq` is AzDTN's word for *habitable room*.** So the four derivations survive — and on
a **stronger** footing than the JSON gives them, not a weaker one. A dining room and a
study are places of direct habitation; the test is purposive, and they pass it. But the
recorded reason is wrong, and a wrong reason that happens to reach the right answer will
not survive the next room type someone adds.

⚠️ **And the same reading exposes a contradiction inside AzDTN that the engine leans on
without knowing.** If `otaq` is the defined habitable term, then section 3's own
definition of `mətbəx` — «kulinariya və qida qəbulu üçün nəzərdə tutulmuş **otaq**» —
makes the **kitchen a habitable room**, contradicting cl. 5.2 and the `yardımçı sahələr`
list in the very same section. **SP 54 has no such problem**, because Russian separates
`комната` (habitable room) from `помещение` (premises), and 3.1.16 calls the kitchen a
*помещение*. Azerbaijani AzDTN had `sahə` and `yerləşgə` available — it uses both,
including for `taxça-mətbəx` and `holl` in the adjacent definitions — and used `otaq` for
the kitchen anyway.

**`otaq` is used in two senses in AzDTN 2.7-2 and the norm never disambiguates them.**
Anyone deriving `counts_as_otaq` from the AzDTN text alone is reading an ambiguous
document. That is the single most important thing this pass found about Q-A.

### 3.2 The nineteen types

`cited` is what `ergonomic.counts_as_otaq_sourcing.per_key` records today.

| # | type | engine | cited | AzDTN 2.7-2, as read | SP 54, as read | verdict |
|---|---|---|---|---|---|---|
| 1 | `living` | **true** | 5.5 `verified` | `qonaq otağı` in cl. 5.5; `ümumi otaq` in cl. 5.7; `ümumi … otaqları` in Cədvəl 6 | «общая жилая комната (гостиная)», Табл. 7.1 | **holds** |
| 2 | `dining` | **true** | 5.5 `derived` | no standalone dining room exists anywhere in AzDTN | nor in SP 54 — only `кухня-столовая`, which is auxiliary | **holds** via the sec. 3 `otaq` definition; **reason in JSON is wrong** (§3.1) |
| 3 | `kitchen` | false | 5.2 `verified` | cl. 5.2 **and** sec. 3 both list `mətbəx` as auxiliary — but sec. 3 defines it **as an `otaq`** | **3.1.16 «Вспомогательное помещение»** — unambiguous | **holds**; AZ self-contradicts, SP 54 is the clean authority |
| 4–6 | `bedroom_principal` / `_double` / `_single` | **true** | 5.5 `verified` | `yataq otağı`, cl. 5.5; `Yataq … otaqları`, Cədvəl 6 | «спальня», Табл. 7.1 | **holds** |
| 7 | `study` | **true** | 5.5 `derived` | passes the `otaq` purposive test — **but Cədvəl 6 gives «Kitabxana, kabinet» its own row, outside the habitable row.** §3.5 | Табл. 7.1 has **no** study row; no SP 54 clause names `кабинет` as a dwelling room | **holds, weakest of the eight — flag it** |
| 8–11 | `bathroom` / `bathroom_combined` / `shower_room` / `wc` | false | 5.2 `verified` — **`bathroom_combined` has NO entry at all** | cl. 5.2 names all four: «vanna otağı (və ya duş) və tualet (və ya birləşdirilmiş sanitar qovşağı)» | 3.1.14, 3.1.35, 3.1.27 — all вспомогательное | **holds**; the missing `bathroom_combined` row is trivially fillable from cl. 5.2's own words |
| 12 | `utility` | false | **sec. 3** `verified` | `paltaryuma otağı`, sec. 3 — **correct, and the only type cited to the right clause** | «постирочная», 3.1.27 | **holds** |
| 13 | `hall` | false | 5.2 `verified` | `holl`, cl. 5.2 and sec. 3 | «внутриквартирные холл и коридор», 3.1.27 | **holds** |
| 14 | `entrance_lobby` | false | 5.2 `verified` | **no distinct word.** Only `holl`, whose sec. 3 definition covers the entrance («giriş hissəsində») | «**передняя**» is a separate 3.1.27 member | **holds, over-cited** — two engine types share one AzDTN word |
| 15 | `corridor` | false | **5.8** `verified` | `dəhliz` appears in **neither** auxiliary list; cl. 5.8 is a **height** clause | «внутриквартирные холл и **коридор**», 3.1.27 — explicit | **holds on SP 54, `derived` on AzDTN** — `verified` overstates |
| 16 | `storage` | false | 5.2 `verified` | «yığnaq otağı (və ya divar təsərrüfat şkafı)» | «кладовая», 3.1.27 | **holds** |
| 17 | `living_dining` | **true** | 5.5 `derived` | no AzDTN concept | no SP 54 concept | **holds** via the `otaq` definition |
| 18 | `kitchen_dining` | **false** | **5.7** `verified` | **sec. 3 defines `mətbəx-yemək otağı` as an `otaq`**, and it is **absent from both auxiliary lists** | **3.1.18 «Вспомогательное помещение»; 3.1.27 «кухня (или кухня-столовая)»** | ⚠️ **holds ONLY on SP 54. The AzDTN citation is wrong and the AzDTN text cuts the other way.** §3.3 |
| 19 | `living_dining_kitchen` | **true** | 5.5 `derived` | AzDTN's only kitchen-in-a-room concept is `taxça-mətbəx`, a **`sahə`**, and cl. 5.7 confines it to one-room flats | **3.1.17 `кухня-ниша`: a ZONE adjacent to a жилое or вспомогательное помещение** | **holds — and SP 54 supplies the justification the engine never wrote down.** §3.4 |

### 3.3 ⚠️ The asymmetry, answered: it is real, and AzDTN is the wrong authority for it

The brief asks whether the split — `kitchen_dining` not an otaq, `living_dining_kitchen`
an otaq, both containing a kitchen — is norm-backed or an engine invention.

**It is norm-backed. By SP 54, precisely and deliberately. Not by AzDTN.**

SP 54 draws exactly this line, twice, in adjacent definitions:

- **3.1.18 `кухня-столовая` is a *помещение*** — a room in its own right — and it is
  **вспомогательное**. A dwelling that gains one gains an auxiliary room. **0 otaq.**
- **3.1.17 `кухня-ниша` is a *зона*** — a zone, not a room — «расположенная **смежно с
  жилым или вспомогательным помещением** квартиры». It sits *inside* somebody else's
  room, and **the host room keeps its own class**. A living room with a kitchen niche is
  still a жилая комната. **1 otaq.**

That is `kitchen_dining` and `living_dining_kitchen`, and the discriminator is **room
versus zone**, not "does it contain a kitchen". The engine's two flag values are correct
and the asymmetry is not an invention.

**But the engine did not get there this way, and cannot get there from AzDTN.** Three
reasons the AzDTN citation fails:

1. **The cited clause is a floor-area clause.** `kitchen_dining` is sourced to cl. 5.7,
   whose text is a list of minimum areas. The JSON reasons that because cl. 5.7
   *"constrains only its `mətbəx zonası`, AzDTN treats it as a kitchen variant, never a
   yaşayış otağı"*. That is an **inference from a dimension rule about class membership**.
2. **AzDTN's own definition contradicts it.** «mətbəx - yemək otağı — … ayrıca zonaları
   olan **otaq**». The norm calls it an otaq.
3. **AzDTN deleted the very words that would have settled it.** SP 54 3.1.27 puts
   «кухня (или **кухня-столовая**)» in the auxiliary class in so many words. **AzDTN
   replaced that phrase with «mətbəx və ya **taxça-mətbəx**»** — and `mətbəx-yemək otağı`
   then appears in *no* auxiliary list in the document. The one sentence that would make
   the engine's flag `verified` under Azerbaijani law is the exact sentence AzDTN dropped.

**Net: the flag value survives; the citation does not.** `conf: verified` against
`az_azdtn_2_7_2` cl. 5.7 is not supportable. The honest record is SP 54 3.1.18 as the
source, with AzDTN noted as silent-to-contrary — and SP 54's `force` in the AZ profile is
`foreign_not_applicable`, so this becomes an **`engine_choice` with a foreign
corroboration**, which is a materially weaker claim than the file makes today.

### 3.4 The `living_dining_kitchen` limb has a second problem AzDTN cannot fix

Under SP 54 the LDK reads cleanly as *habitable room + кухня-ниша*. Under **AzDTN it does
not read at all**:

- `taxça-mətbəx` is defined as having **no eating area** («yemək qəbulu ərazisi olmayan
  sahə») — narrower than SP 54's `кухня-ниша`, which carries no such exclusion; and
- **cl. 5.7 confines it to one-room flats**: «Birotaqlı mənzillərdə sahəsi 5 m²-dən az
  olmayan taxça-mətbəxin layihələndirilməsinə **yol verilir**» — *permitted in one-room
  apartments*.

So an Azerbaijani three-otaq flat with an open-plan LDK has **no term in AzDTN 2.7-2 at
all**. The engine's `living_dining_kitchen` is outside the norm's vocabulary, not merely
underspecified in it. That is consistent with `az-kitchen-diner-whole-room.md`'s finding
that the whole regional family drafts kitchens zone-first, and it means the LDK type will
never become `verified` against AZ law. It should be recorded as `engine_choice`.

### 3.5 ⚠️ `study` — the norm names it exactly once, and not among the habitable rooms

The brief asks whether a `study` («kabinet») is really a yaşayış otağı. The purposive test
in §3.1 says yes. **The one place AzDTN actually writes the word says otherwise**, and the
engine has not recorded it.

**cl. 9.2** («Otaqların havadəyişmə həcmi cədvəl 6-ya uyğun olaraq qəbul edilməlidir»)
introduces **Cədvəl 6**, whose first four rows read, verbatim:

> Otaqlar və sahələr | Havadəyişmə misli və ya həcmi … Qeyri-iş rejimində / İş rejimində
> **Yataq, ümumi və uşaq otaqları** | - | **1,0**
> **Kitabxana, kabinet** | **0,2** | **0,5**
> **Köməkçi otaq, qarderob** | 0,2 | 0,2
> Trenajor zalı, bilyard otağı | 0,2 | 80 m³/saat

*"Rooms and spaces | air-change rate or volume … idle mode / working mode.
**Bedroom, common and children's rooms** — 1,0. **Library, study** — 0,2 / 0,5.
**Auxiliary room, wardrobe** — 0,2 / 0,2. Gym, billiard room — 0,2 / 80 m³/h."*

Three things follow, and they pull in different directions:

1. ⚠️ **`kabinet` is in a row of its own, separate from the habitable row and separate
   from the auxiliary row.** In the only sub-classification of room kinds AzDTN performs
   beyond cl. 5.5's parenthetical, the study is in **neither** class.
2. **The habitable row is SP 54's triple, not cl. 5.5's.** «Yataq, **ümumi** və **uşaq**
   otaqları» = «спальня, общая жилая комната, детская комната» — SP 54 Табл. 7.1 exactly,
   **including the children's room that cl. 5.5 omits**. So AzDTN carries the habitable
   list **twice, in two different wordings, and they disagree with each other**: cl. 5.5
   says *otaq / qonaq otağı / yataq otağı*, Cədvəl 6 says *yataq / ümumi / uşaq*.
3. **SP 54.13330.2022's Табл. 7.1 has no study row at all** — its rows are «Жилые комнаты
   (…)», «Кладовая, бельевая, гардеробная», and four kitchen variants. **AzDTN's Cədvəl 6
   is the richer table**, and the `Kitabxana, kabinet` row is AzDTN's, not inherited from
   the 2022 parent.

**How much weight this carries.** Cədvəl 6 is a **ventilation** table under section 9
(sanitary-epidemiological requirements), reached through `DÜİST 30494`. An air-change
classification is not the жилая/вспомогательная classification, and it cannot overturn
the section 3 definition. ⚠️ **But it is the only sentence in AzDTN 2.7-2 that contains
the word `kabinet` in a dwelling sense, and it does not put it with the habitable rooms.**
`study: counts_as_otaq = true` is the flag with the least support in the file, its
`conf: derived` is right, and the note attached to it should say *this*, not "unqualified
catch-all".

### 3.6 Two smaller citation defects, both real

- **`entrance_lobby` → cl. 5.2 `verified` is over-precise.** cl. 5.2 names `holl`, once.
  AzDTN has no word for SP 54's `передняя`; `holl`'s section 3 definition explicitly
  covers the entrance area, so **`hall` and `entrance_lobby` map to the same AzDTN term**.
  The flag value is right in both cases; the claim that the *clause distinguishes them* is
  not.
- **`corridor` → cl. 5.8 `verified` overstates.** `dəhliz` is in **neither** auxiliary
  list — not cl. 5.2, not section 3. cl. 5.8 groups it with `hol` and `antresol` for a
  **reduced ceiling height** (2,1 m). Inferring class membership from a height allowance
  is the same move §3.3 criticises for `kitchen_dining`. **SP 54 3.1.27 names
  «внутриквартирные холл и коридор» outright**, so the value is safe — but the confidence
  belongs to the Russian text, not the Azerbaijani one.
- **`bathroom_combined` has no sourcing row at all** — 18 keys in
  `counts_as_otaq_sourcing.per_key`, 19 types in `ergonomic.rooms`. It is the only flag
  value in the set with no recorded provenance, and cl. 5.2 names
  «birləşdirilmiş sanitar qovşağı» explicitly, so this is a pure omission.

### 3.7 Q-A verdict

**DIFFERENT PARTITION — same skeleton, materially different flesh.**

AzDTN reproduces SP 54's **auxiliary-side definition** near-verbatim (sec. 3 ≈ SP 54
3.1.27), and reproduces SP 54's **habitable triple** in Cədvəl 6. It does **not** reproduce
the partition as a whole:

- it has **no clause corresponding to SP 54 cl. 5.3**, the clause that states the split as
  a composition requirement over both classes;
- it **enumerates the habitable class twice, inconsistently** (cl. 5.5 vs Cədvəl 6), and
  never in a clause whose job is to define it;
- it **drops `кухня-столовая` from the auxiliary list** and substitutes the kitchen-niche,
  removing the one sentence that decides the engine's hardest flag;
- it **drops `передняя` and `коридор`**, collapsing three circulation terms into `holl`;
- and it **uses `otaq` in two irreconcilable senses**, so that its own kitchen definition
  contradicts its own auxiliary list.

**Fourteen of the nineteen flag values are correctly sourced and stand as they are. Five
carry defects:** `kitchen_dining` (wrong authority, contradicting text), `study` (right
answer, wrong reason, unrecorded counter-evidence), `corridor` and `entrance_lobby`
(`verified` should be `derived`), `bathroom_combined` (no row). **No flag value needs to
change. Five provenance records do.**

---

## 4. Q-B — the dwelling-area rule, verbatim from both norms

### 4.1 SP 54.13330.2022 cl. 5.2 and Table 5.1

Read directly off the page; both numbers visible.

> **5.2** Площади квартир (без учета площадей балконов, лоджий, террас, холодных кладовых
> и приквартирных тамбуров) **в зависимости от числа их жилых комнат** приведены в
> таблице 5.1, дополнительные сведения - в [21].
>
> **Таблица 5.1**
>
> | **Число жилых комнат** | 1 | 2 | 3 | 4 | 5 | 6 |
> |---|---|---|---|---|---|---|
> | **Минимальная площадь квартир, м²** | **28** | **44** | **56** | **70** | **84** | **103** |
>
> Допускается **отклонение** от приведенных значений в таблице 5.1 к числу жилых комнат и
> площади квартир в соответствии с **[4, статья 50]** с учетом демографических требований,
> достигнутого уровня обеспеченности населения жилищем и ресурсообеспеченности жилищного
> строительства.

*"**5.2** The areas of apartments (not counting the areas of balconies, loggias, terraces,
cold storerooms and apartment vestibules), **as a function of their number of habitable
rooms**, are given in Table 5.1 … Table 5.1: Number of habitable rooms 1–6 → **Minimum
area of apartments, m²: 28 / 44 / 56 / 70 / 84 / 103**. Deviation from the values given
in Table 5.1 for the number of habitable rooms and the apartment area is permitted in
accordance with [4, article 50], taking account of demographic requirements, the achieved
level of housing provision and the resource-availability of housing construction."*

**Confirmed: SP 54 does key a minimum dwelling area to the habitable-room count**, exactly
as `room-classification-standards.md` §3.1 reports — and its 28/44/56 are now extended to
the full six-column row. Note the escape clause: SP 54's own minimum is deviable by
statute.

### 4.2 AzDTN 2.7-2 cl. 5.1 and Cədvəl 1 — the rule exists here too

Read directly off pages 11–12. **This is the finding of the pass on Q-B, and it appears
nowhere in the repo today** (§6.2).

> **5.1.** **Dövlət və bələdiyyə mənzil fondunun** yaşayış binalarında mənzillərin,
> **otaqların sayına və sahəsinə görə minimal ölçülərinin** cədvəl 1 əsasında
> (balkonların, terrasların, eyvanların, lociyaların, şüşəbəndlərin, isidilməyən köməkçi
> otaqların və mənzilin tamburunun sahələri nəzərə alınmamaq şərtilə) qəbul edilməsi
> **tövsiyə olunur**.
>
> **Cədvəl 1**
>
> | **Yaşayış otaqlarının sayı** | 1 | 2 | 3 | 4 | 5 | 6 |
> |---|---|---|---|---|---|---|
> | **Mənzillərin tövsiyə edilən ümumi sahəsi, m²** — şəhər, qəsəbə | **28-38** | **44-53** | **56-65** | **70-77** | **84-96** | **103-109** |
> | — kənd | 38-44 | 50-60 | 66-76 | 77-89 | 94-104 | 106-116 |
>
> **Özəl mənzil fonduna aid** yaşayış binalarındakı mənzillərin sahəsi, otaqların sayı və
> tərkibi **sifarişçi tərəfindən müəyyən edilir.**

*"**5.1.** In residential buildings **of the state and municipal housing fund** it is
**recommended** that the **minimum dimensions of apartments, by the number of rooms and by
area**, be adopted on the basis of Table 1 (excluding the areas of balconies, terraces,
eyvans, loggias, glazed enclosures, unheated auxiliary rooms and the apartment's tambour).
**Table 1: Number of habitable rooms 1–6 → Recommended total area of apartments, m²:
city/settlement 28-38 / 44-53 / 56-65 / 70-77 / 84-96 / 103-109; rural 38-44 / 50-60 /
66-76 / 77-89 / 94-104 / 106-116.** The area, number of rooms and composition of apartments
in residential buildings belonging to the **private housing fund is determined by the
client.**"*

**The table is keyed to «Yaşayış otaqlarının sayı» — literally "the number of habitable
rooms". That is `counts_as_otaq`'s referent, and it is the table's index column.**

### 4.3 The urban lower bound *is* SP 54's minimum — all six columns

| habitable rooms | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| SP 54 Табл. 5.1, «Минимальная площадь квартир» | 28 | 44 | 56 | 70 | 84 | 103 |
| AzDTN Cədvəl 1, şəhər/qəsəbə **lower** bound | **28** | **44** | **56** | **70** | **84** | **103** |
| AzDTN Cədvəl 1, şəhər/qəsəbə upper bound | 38 | 53 | 65 | 77 | 96 | 109 |
| AzDTN Cədvəl 1, kənd (rural) band | 38-44 | 50-60 | 66-76 | 77-89 | 94-104 | 106-116 |

**Six of six, exact.** AzDTN Cədvəl 1 is the transposition of SP 54 Table 5.1: Azerbaijan
kept the Russian minimum as the floor of an urban band, added a ceiling, and added a rural
band above it.

> **On the extraction, because the whole answer turns on it.** pypdf renders this table in
> column-major order, which is easy to mis-pair. The pairing above was verified against
> **glyph x-coordinates** in pymupdf: the header digits sit at x = 325,3 / 366,8 / 410,7 /
> 454,8 / 498,7 / 553,1 and the six value cells at x = 315,2 / 356,7 / 400,6 / 444,7 /
> 488,6 / 537,5 — a clean one-to-one ordering, with each cell block holding its column's
> `şəhər` value above its `kənd` value. The 28/44/56/70/84/103 coincidence with SP 54 is
> then an **independent** confirmation of the same reading.

### 4.4 What AzDTN changed, and why each change matters

**1. Register: mandatory → recommended.** The clause ends `tövsiyə olunur`. By the AzDTN
system's own governing rule (`Əsas müddəalar (Konsepsiya)`, Bakı 1994 §§3.1–3.6, as
`minima.md` §4.2 records and `az-statutory-floor-transcription.md` §2.3 re-confirms),
`-məlidir` / `az olmamalıdır` = **məcburi**, `tövsiyə olunur` = **recommended**. In the
repo's `source_force_vocabulary` this is `recommended`, not `statutory`.

⚠️ **The register test is decided *inside this same section*, five paragraphs apart, and
the norm lands on opposite sides.** cl. 5.1 (dwelling area) is `tövsiyə olunur`. cl. 5.7
(room areas) is `az olmamalıdır`. **AzDTN mandates the room and recommends the dwelling.**
That is not an accident of drafting; it is the norm choosing.

**2. Scope: all apartments → state and municipal fund.** SP 54 cl. 5.2 carries **no** fund
restriction — it is a flat statement about «Площади квартир». SP 54 puts the
state/municipal restriction in a *different* clause, **cl. 5.3**, and that clause governs
**composition**, not area. **AzDTN merged the two and applied the restriction to the area
table.**

**3. The private fund is handed to the client, explicitly.** «Özəl mənzil fonduna aid …
sifarişçi tərəfindən müəyyən edilir.» SP 54 cl. 5.3 has the parallel sentence for
composition — «В квартирах частного жилищного фонда … состав помещений определяют в
задании на проектирование» — but SP 54 says it about *composition*, and adds *"с учетом
указанного выше необходимого состава"* (taking account of the required composition above).
**AzDTN's version has no such tether, and it governs area.**

**4. A floor became a band.** SP 54 gives one number per room count. AzDTN gives a range,
and thereby also an **upper** recommendation — 38 m² for a one-otaq urban flat, 109 for a
six. ⚠️ Note an internal tension: the clause says «**minimal** ölçülərinin … qəbul
edilməsi», *minimum* dimensions, while the table it points at is headed
«**tövsiyə edilən** ümumi sahəsi», *recommended* total area, and holds ranges. The clause
and its table do not use the same word for the same thing.

### 4.5 Nothing else in AzDTN bounds a whole dwelling

A sweep of all 30 pages for `az olmamalıdır` (shall not be less than) and `ümumi sahəsi`
(total area) returns every area floor in the norm. **None is a per-dwelling minimum:**

- **cl. 5.7** — per-**room** floors (15 / 16 / 8 / 10 / 8 / 6 / 5 / 2,5 / 7 m²). Mandatory.
  Already fully transcribed in `az-statutory-floor-transcription.md` §2.1.
- **cl. 7.2.5 / 7.2.6 / 7.2.9** — 500 m² caps on the **total apartment area per floor**,
  for fire-evacuation purposes. Per storey, not per dwelling, and a **ceiling**.
- **Əlavə 1, Note 2** — «Cədvəl adambaşına **18 m²** ümumi mənzil sahəsi … hesabı ilə
  tərtib edilmişdir» — 18 m² per person, stated as the **assumption the lift table was
  compiled on**. `room-constraints.json` already reads this note correctly for a different
  purpose (storey height) and its "PRESCRIBES NO …" framing applies identically here: this
  is an input to a lift calculation, **not a rule about dwellings**.

### 4.6 Q-B verdict

**RULE EXISTS — in both norms — but in Azerbaijan it is `recommended`, scope-limited to
the state and municipal housing fund, expressed as a band, and explicitly disclaimed for
the private fund.**

- **SP 54.13330.2022 cl. 5.2 / Табл. 5.1: yes, a minimum, 28/44/56/70/84/103 m².** Force
  in the AZ profile: `foreign_not_applicable`.
- **AzDTN 2.7-2 cl. 5.1 / Cədvəl 1: yes, keyed to the same index, same lower bounds —
  but `tövsiyə olunur`.** Force: **`recommended`**, not `statutory`.
- **No mandatory whole-dwelling area rule exists in AzDTN 2.7-2.**

---

## 5. ⚠️ One mandatory AzDTN rule *is* keyed to the otaq count, and it is not cl. 5.1

While sweeping for Q-B. **cl. 9.11**, second paragraph, read directly off page 24:

> **9.11.** … 1, 2 və 3 otaqlı mənzillərdə **ən azı bir yaşayış otağında**, 4 və daha çox
> otaqlı mənzillərdə isə **ən azı iki otaqda** normalaşdırılmış insolyasiya davamiyyəti
> təmin **edilməlidir**.

*"In 1-, 2- and 3-room apartments **in at least one habitable room**, and in apartments of
4 or more rooms **in at least two rooms**, the normalised insolation duration **shall be
ensured**."*

Register `təmin edilməlidir` = **məcburi / mandatory**.

**This is the counter-example to "there is no acceptance rule keyed to `counts_as_otaq`".**
It is mandatory; its threshold is the **otaq count** (1–3 vs 4+); and evaluating it needs
**both** the otaq count *and* the habitable class — precisely the pair
`room-classification-standards.md` §3.1 argued a `zone_class` must preserve.

**The repo already knows the shape of this rule but has never cited the clause.**
`az-region-profile/daylight.md` §2.3 records the identical one-room/two-room asymmetry
from СНиП 23-05-95* cl. 5.4* and СП 52.13330.2016 cl. 5.3, calls it *"the insolation rule
AzDTN inherits"*, and records a **deliberate decision not to implement KEO in v1** for
want of sky models, orientation and obstruction angles. **That decision is sound and this
finding does not reopen it** — insolation duration needs solar geometry the engine's plans
do not carry. But `9.11` is the clause number behind that inherited rule, it is
**mandatory in Azerbaijan**, and it appears in **no** artefact: `grep "9.11"` returns
nothing in `daylight.md` or `az-statutory-floor-transcription.md`. Worth recording where
the KEO decision is recorded, so that the deferral is against a named clause.

---

## 6. The gap in the engine — stated plainly

### 6.1 What `rules.json` bounds today

`data/acceptance/rules.json` carries **43 rules** (`rule_count: 43`, verified against the
array length). Every rule was read. On whole-dwelling area:

| rule | what it actually bounds |
|---|---|
| `area.invented_envelope_hard` | Σ Space area within **5 %** of **the Brief's `target_area`** |
| `area.invented_envelope_soft` | prefer within **2 %** of the same |
| `area.given_envelope_warn` | warn when Σ Space area differs from the same |
| `area.convention_declared` / `_agrees` | that the Brief's `target_area` carries and matches an `area_convention` |
| `dim.statutory_min_area` | **per-Space**, per Room type, via the region profile's `statutory_floor` |
| `dim.min_area`, `dim.max_area`, `dim.market_default_area` | per-Space |
| `circ.fraction_hard` / `_soft` | circulation area as a **fraction** of Σ Space area |

**Every whole-dwelling bound in the engine is against `target_area` — a Homeowner input —
and none is against any normative figure.** `dim.statutory_min_area` is the only rule that
touches a statutory number and it is per-Space, never aggregate. The otaq count enters the
engine in exactly one place, `when_otaq_count` in `room-constraints.json`, and all it does
is select the living-room floor (15 m² at one otaq, 16 at two or more).

**Confirmed by search:** `"Cədvəl"` occurs **0** times in `rules.json`; `"cl. 5.1"` occurs
**0** times in `rules.json` and **28** times in `room-constraints.json`, where **every one
of them refers to AzDTN 2.7-3** — the detached-house norm — not to AzDTN 2.7-2.
**AzDTN 2.7-2 cl. 5.1 and Cədvəl 1 are cited nowhere in the shipped data.**

### 6.2 Is a mandatory check missing? **No. And that is the answer to the brief's worry.**

The brief's hypothesis was: *"If the norm makes the otaq count drive a statutory minimum
dwelling area, the engine may be missing a mandatory whole-dwelling check."*

**The norm does not.** AzDTN cl. 5.1 is `tövsiyə olunur`, and its scope sentence excludes
the housing this engine draws — cl. 5.1's own closing line hands the **private fund** to
the client. **No mandatory whole-dwelling check is missing, and C8 is not at risk.**

### 6.3 But a real gap exists, and it is quantified

`dim.statutory_min_area`'s own note records the brief-side pre-image: the Σ of hard minima
over a resolved Brief, post-resolve. Set that against Cədvəl 1's urban recommendation for
the same otaq count:

| otaq | engine Σ hard minima (`dim.statutory_min_area` note) | AzDTN Cədvəl 1 urban recommended minimum | shortfall |
|---|---|---|---|
| 1 | 26,5 m² | **28** | **−1,5** |
| 2 | 37,5 m² | **44** | **−6,5** |
| 3 | 47,5 m² | **56** | **−8,5** |
| 4 | 57,5 m² | **70** | **−12,5** |

**The engine's floor sits below the norm's recommended minimum at every otaq count, and
the shortfall widens monotonically.** A Plan can satisfy all 43 acceptance rules and still
be a dwelling the Azerbaijani regulator would call undersized **for the otaq count the
engine's own copy prints**.

**Why this matters more than its `recommended` register suggests.**
`flag_semantics.is_habitable_versus_counts_as_otaq` states that `counts_as_otaq` is *"a
PRODUCT driver: it decides what number the copy prints and what C13's 1-4 band is measured
in"*. **Cədvəl 1 is the regulator's own opinion about what that same number should buy.**
It is the one published, Azerbaijani, otaq-indexed statement of dwelling size in existence,
and it disagrees with the engine by up to 12,5 m² at four otaq. The engine may decline to
adopt it — `recommended`, wrong fund, and a band rather than a floor are three good
reasons — but **today the omission is silent**: nothing in `rules.json` or
`room-constraints.json` mentions the clause or the table at all, so no reader can tell the
omission from an oversight.

### 6.4 What this suggests, without deciding it

Not decided here; these belong to the tickets that own the artefacts.

1. **Record cl. 5.1 / Cədvəl 1 somewhere, at `force: recommended`, even if nothing reads
   it.** The precedent is `room-constraints.json`'s own "EXPLICITLY NULL, AND THAT IS THE
   FINDING" pattern for storey height. A searched-for-and-found-recommended rule that the
   engine declines is a different artefact from a rule nobody looked for.
2. **If a whole-dwelling bound is ever wanted, Cədvəl 1's urban lower row is the only
   Azerbaijani number available**, it is `recommended` not `statutory`, and any rule
   reading it must be phrased as a **preference**, never as a compliance claim — the same
   line `dim.statutory_min_area`'s note already walks for the brief-side pre-image
   ("never a compliance claim, which is how this rule stays inside C8").
3. **⚠️ Copyright.** `az-region-profile.md` §8 states the posture: *"no source's table is
   reproduced with its own selection and ordering."* Cədvəl 1 is quoted **in full in this
   research document**, for analysis, with attribution — which is the citation of a state
   normative act, not redistribution. **§8 still binds any move of these figures into a
   shipped artefact**: carry the cells the engine actually reads, each cited, not the
   table.
4. **Five provenance repairs in `counts_as_otaq_sourcing`** (§3.7). No flag value changes.
5. **cl. 9.11 belongs next to `daylight.md` §2.3's KEO deferral** (§5), so the deferral
   names the mandatory clause it defers.

---

## 7. Clause numbers — every one read directly off the page

The brief warns that prior research was burned by inferring two clause numbers by
position. **Nothing in this document is inferred.** Each number below was read at the head
of its own paragraph or in its own table caption.

**AzDTN 2.7-2 (2021):** sec. 1, sec. 3, cl. 5.1, **Cədvəl 1**, cl. 5.2, 5.3, 5.5, 5.7,
5.8, 5.9, 5.10, 7.2.5, 7.2.6, 7.2.9, 9.2, **Cədvəl 6**, 9.11, 9.12, 9.13, Əlavə 1 Note 2.

**SP 54.13330.2022:** 3.1.12, 3.1.14, 3.1.15, 3.1.16, 3.1.17, 3.1.18, 3.1.27, 3.1.28,
5.1, 5.2, **Таблица 5.1**, 5.3, 5.10, 5.11, 5.12, **Таблица 7.1**.

### ✅ Two open items from `room-classification-standards.md` §6 are now closed

That document flagged: *"§3.1's definition clause is identified as **3.1.27 by position**
… and the composition clause as **5.3 by structure** … Neither number was read directly
off the page. **Verify before quoting a clause number into `rules.json` or an ADR.**"*

**Both inferences were correct, and both are now confirmed by direct reading:**

- **3.1.27** — the string `3.1.27` appears immediately before `помещение вспомогательное:`
  in the extracted text, with `3.1.26 подполье техническое` before it and `3.1.28
  помещение встроенно-пристроенное` after. **Confirmed.**
- **5.3** — `5.3 В многоквартирных жилых зданиях государственного и муниципального
  жилищных фондов…` reads with its number at the head of the paragraph, between 5.2 and
  5.4. **Confirmed.**

Both may now be quoted with their numbers. §2.3 above also supplies 3.1.27's full verbatim
text with its lead-in, which §3.1 of that document had only in part (its quote began
mid-sentence at «…коммуникационных»).

### Also corrected in the parent document

`room-classification-standards.md` §3.1 states the SP 54 minimum-area row as
*«Число жилых комнат 1/2/3 → Минимальная площадь квартир 28/44/56 м²»*. **Correct as far
as it goes; the row has six columns, 28/44/56/70/84/103.** §4.1 above carries it in full.

---

## 8. What this establishes and what it does not

**Establishes, from primary sources read this session:**

- AzDTN 2.7-2 cl. 5.5 and cl. 5.2 verbatim, with translations, and their true function —
  a basement prohibition and a composition requirement, neither an enumeration clause.
- AzDTN 2.7-2 section 3's definitions of `otaq`, `mətbəx`, `taxça-mətbəx`,
  `mətbəx-yemək otağı`, `holl` and `yardımçı sahələr`, verbatim.
- That AzDTN's `otaq` is the near-verbatim rendering of SP 54 3.1.15 `комната жилая`, and
  therefore **not a catch-all**; and that AzDTN nonetheless uses the word in a second,
  generic sense in its own kitchen definition.
- SP 54 3.1.16/3.1.17/3.1.18/3.1.27 verbatim, establishing that **SP 54 puts
  `кухня-столовая` in the auxiliary class explicitly and treats `кухня-ниша` as a zone** —
  which is the norm-side basis for the engine's `kitchen_dining` / `living_dining_kitchen`
  asymmetry, and which **AzDTN does not reproduce**.
- That AzDTN's Cədvəl 6 puts `Kitabxana, kabinet` outside the habitable group, and that
  its habitable row is SP 54's triple rather than cl. 5.5's.
- **AzDTN 2.7-2 cl. 5.1 and Cədvəl 1 in full**, with all twelve area bands, the
  `tövsiyə olunur` register, the state/municipal scope and the private-fund disclaimer;
  and the exact identity of its six urban lower bounds with SP 54 Табл. 5.1.
- That **no mandatory whole-dwelling area rule exists in AzDTN 2.7-2**, by exhaustive
  sweep of every `az olmamalıdır` and `ümumi sahəsi` occurrence in the document.
- AzDTN 2.7-2 cl. 9.11 verbatim — a **mandatory** rule keyed to the otaq count.
- That `rules.json`'s 43 rules contain **no** normative whole-dwelling area bound, and
  that AzDTN 2.7-2 cl. 5.1 / Cədvəl 1 is cited in **no** shipped artefact.
- Confirmation of `room-classification-standards.md` §6's two inferred clause numbers.

**Does NOT establish:**

- **Whether AzDTN 2.7-2 has been amended since 2021.** No amendment search this pass; the
  §1.3 caveat is inherited, not discharged.
- **The Azerbaijani Housing Code's own definition of `otaq`.** §3.1's argument stands on
  AzDTN's section 3 alone. If the Code defines it too, that is the higher authority and
  should be read before this is quoted into an ADR.
- **Cədvəl 6's lineage.** Its resemblance to the `ГОСТ 30494` / `СНиП 31-01-2003` App. И
  family is an observation from structure. Neither text was read.
- **Whether Azerbaijani expert review (ekspertiza) treats a `kabinet` as a yaşayış otağı.**
  No practice, commentary or case material was consulted. §3.5 is a text reading.
- **Any measurement.** Nothing here was tested against the corpus. In particular the
  §6.3 shortfall table is arithmetic over two published figures, **not** a measurement of
  how often generated plans fall in the gap. `experiments/warp/out/dwelling_rooms.json`
  (46 794 converted dwellings) could measure it and was not used.
- **Whether SP 54's [4, статья 50] deviation clause has an Azerbaijani analogue.** Not
  followed.

---

## 9. Reproducing this

```bash
# 1. The AzDTN norm, from the issuing committee. The URL serves the PDF directly.
curl -sSL -A "Mozilla/5.0" \
  "https://arxkom.gov.az/qanunvericilik/normativler/binalarin-muhendis-sistemleri/zhilye-zdaniya" \
  -o azdtn_2_7_2.pdf
md5sum azdtn_2_7_2.pdf   # 4b5da47dd11808cd0aef37a75b01b4e9

# 2. SP 54.13330.2022
curl -sSL "https://rkc56.ru/attach/orenburg/docs/Gosstandart_RF/SP-54.13330.2022-Mnogokvartirnie.pdf" \
  -o sp54.pdf
```

```python
# 3. Extract. PYTHONIOENCODING=utf-8 is REQUIRED - cp1252 raises UnicodeEncodeError
#    on the Azerbaijani diacritics and the Cyrillic, and truncates silently.
import pypdf, pymupdf
txt = "\n".join(p.extract_text() for p in pypdf.PdfReader("azdtn_2_7_2.pdf").pages)
# clauses land at the head of their own paragraph: grep for r"\n\s*5\.[125]\." etc.

# 4. Cədvəl 1 is column-major in reading order. Verify cell-to-column by x-coordinate,
#    NOT by reading order - this is where the answer to Q-B can be silently corrupted.
p = pymupdf.open("azdtn_2_7_2.pdf")[11]          # page 12, 0-indexed
[(w[0], w[4]) for w in p.get_text("words") if 100 < w[1] < 155]
#  header digits  x = 325.3 366.8 410.7 454.8 498.7 553.1
#  value cells    x = 315.2 356.7 400.6 444.7 488.6 537.5   -> one-to-one, left to right
```

Run against `./venv/Scripts/python.exe` — `pypdf 6.16.1`, `pymupdf 1.28.2`, Windows 11 /
Python 3.12. Both extractors agree on every numeral and every diacritic quoted above.

### Sources

| # | source | how read | trust |
|---|---|---|---|
| 1 | **AzDTN 2.7-2** «Yaşayış binaları. Layihələndirmə normaları», Bakı 2021 — State Committee on Urban Planning and Architecture; approved 2021-11-30, Collegium dec. No. 03, State Register No. 15202111300003 — https://arxkom.gov.az/qanunvericilik/normativler/binalarin-muhendis-sistemleri/zhilye-zdaniya | **downloaded live this session**, md5 `4b5da47dd11808cd0aef37a75b01b4e9`, text extracted twice and cross-checked | **primary** |
| 2 | **СП 54.13330.2022** «СНиП 31-01-2003 Здания жилые многоквартирные» — https://rkc56.ru/attach/orenburg/docs/Gosstandart_RF/SP-54.13330.2022-Mnogokvartirnie.pdf | fetched this session, text extracted | **primary** (mirror of the Minstroy text, not the Minstroy host) |
| 3 | `data/standards/room-constraints.json`, `data/acceptance/rules.json` | read in full, resolved programmatically | **primary** (repo) |
| 4 | `docs/research/room-classification-standards.md` §3.1, §6 | read | repo research |
| 5 | `docs/research/az-statutory-floor-transcription.md` §1.1–1.3, §2.1–2.4 | read; §1.1's md5 independently reproduced | repo research |
| 6 | `docs/research/az-region-profile.md` §8, `az-region-profile/daylight.md` §2.3 | read | repo research |
| 7 | `docs/research/az-kitchen-diner-whole-room.md` §12.2 | read (sourcing pattern) | repo research |

**Licence posture.** Both norms are state normative acts published free of charge by their
issuers. Neither PDF is committed. AzDTN Cədvəl 1 and Cədvəl 6 are quoted here **for
analysis, in a research document**; `az-region-profile.md` §8's rule — *no source's table
reproduced with its own selection and ordering* — governs any shipped artefact, and §6.4
item 3 says so at the point of use.
