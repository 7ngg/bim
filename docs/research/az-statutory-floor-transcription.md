# AZ statutory floor — is the hand copy true?

Findings for **ticket 69, *The law is a hand copy and it now shapes rooms***.

Three artefacts claim to carry the same six numbers:

| | artefact | what it is |
|---|---|---|
| **(a)** | **AzDTN 2.7-2 cl. 5.7** | the law |
| **(b)** | `data/standards/room-constraints.json`, `profiles.AZ.rooms` | the published profile |
| **(c)** | `experiments/warp/absolute_area.py` `STAT_FLOOR` | six floats hand-typed into Python |

Nothing in the repo binds (a) to (b), and until ADR 0033 nothing bound (b) to (c)
either. ADR 0033 made (c) **constrain geometry** — `floor_warp.py` posts
`sum(part areas) >= floor` as a hard CP-SAT constraint and returns `INFEASIBLE`
rather than emitting a candidate that misses it. A drift in (c) no longer
produces a wrong figure in a report; it produces a plan built to a floor no
regulator wrote.

**C8 applies to every number below.** These are dimensional standards with a
citation, not a compliance claim. §3 states exactly what legal force each source
has. Nothing here is *claimed* to a Homeowner and no surface text names a law.

**This note does not edit any of the three artefacts.** A value edit belongs to
`room-constraints.json` under C14's monotone-raise rule; the binding belongs to
ticket 69; `experiments/warp/` has four open claimants (62, 65, 67, 69) and is
not written here.

---

## 0. TL;DR

| # | Finding |
|---|---|
| **1** | **All six values are correct, and this is now a first-hand verification rather than an inherited one.** AzDTN 2.7-2 was **downloaded live from the issuing authority during this session** and its cl. 5.7 read directly. The served PDF is byte-identical (md5 `4b5da47dd11808cd0aef37a75b01b4e9`) to the repo's cached copy at `experiments/finish-layer/src/azdtn_2_7_2.pdf`. §1, §2. |
| **2** | **`KITCHEN_DINING` 6.0 is the right number attached to the wrong thing, and this is the one substantive defect.** cl. 5.7 floors *«mətbəx-yemək otağında **mətbəx zonası** - 6 m²-dən»* — the **kitchen zone inside** the kitchen-diner, not the kitchen-diner. `floors_for` returns 6.0 as a **whole-Room** floor and ADR 0033 posts it as one. The law's whole-room floor for a `mətbəx-yemək otağı` is **unquantified**, and it is necessarily **more** than 6.0. The profile already says this, twice, in fields the Python never reads. §5.1. |
| **3** | **It is NOT the SNiP folklore number.** minima.md finding 8 established that "kitchen 6 m²" is not in SNiP 2.08.01-89\*. The 6.0 here is a different provision, verified verbatim in **two** live Azerbaijani instruments (AzDTN 2.7-2 cl. 5.7 and AzDTN 2.7-3 cl. 5.1) and corroborated in a third (SP 54.13330 cl. 5.11, per minima.md §11.5). The number's provenance is sound; only its referent is mis-transcribed. §5.1. |
| **4** | **`PRIVATE` 10.0 is genuinely the double and 8.0 genuinely the single.** cl. 5.7: *«yataq otağı - 8 m² (iki adama - 10 m²-dən)»* — 8 m², and 10 for two persons. The corpus collapse `{ROOM, BEDROOM, STUDIO} → PRIVATE` is real and the two-limb report is the honest response to it. §5.2. |
| **5** | **The law does condition the living-room floor on room count, and 15/16 with the threshold at 1-vs-2+ is exactly right.** cl. 5.7 splits *birotaqlı mənzildə* (15) from *iki və daha çox otaqlı mənzillərdə* (16). 15/16 is **AzDTN's own pair**, not a blend: SNiP 2.08.01-89\* and the Russian SP line both say **14**/16; Azerbaijan raised the one-room limb by 1.0 m². §5.3. |
| **6** | **No tier bleed. The two 16.0s and the two 6.0s are real coincidences, verified in two different documents.** `market_default` living 16.0 is AzDTN **2.7-3** cl. 5.1 (detached houses, recommended); `statutory_floor` living 16.0 is AzDTN **2.7-2** cl. 5.7 (apartments, mandatory). Different instrument, different building type, same figure. Same for the two 6.0s. §5.4. |
| **7** | ⚠️ **A seventh hand-copied value exists, it is wrong, and no ticket names it.** `absolute_area.HABITABLE` — the input to the otaq guard — omits `DINING`, which the profile's `counts_as_otaq` marks **true**. Where it bites the guard picks `LIVING_1OTAQ` 15.0 in a dwelling the profile calls 2+ otaq: **a living room floored 1.0 m² below the law**. Measured on the converted corpus: 85 of 46,794 dwellings flip, 59 of them carrying a living room. §6. |
| **8** | ⚠️ **The `LIVING` limb has ZERO headroom between the soft target and the hard floor, in 65.1 % of the corpus.** `market_default` living = 16.0 and `statutory_floor` living (2+ otaq) = 16.0. ADR 0033's *"the floor never fights a target … living 16,0 against 15/16"* is an **at**, not an **above**. Against consequence 3's own seed-shape estimate error (p50 0.038 m²) that margin is not a margin. `KITCHEN_DINING` is the same at 6.0/6.0. §7. |
| **9** | **The Python's prose inventory is wrong in three independent ways.** "Only three corpus labels reach a floor … the other six map to a null az_area … their ergonomic minima (0.5-1.7 m2)". It is **five** and **five**; two of the five reach a **non-null** `az_area` pointing at a cell whose `statutory_floor` is null (a *second, different* null the accessor must handle); and the quoted ergonomic range omits `dining` 1.9 m². None of it changes a posted number today — `floors_for` reads the dict, not the prose — but each is a place a reader is misled. §4.3, §8.2. |
| **10** | **`floor_warp._check_floor_transcription` is narrower than its own docstring implies.** It reads `areas_m2.<key>.statutory_floor.v` **raw**, bypassing `mapping` — which ticket 69 item 1 names as the contract. It cannot see a re-pointed guard, a changed `when_otaq_count`, a `MARKET` drift, or the `HABITABLE` defect above; it silently no-ops when `data/` is absent; it is a bare `assert` (stripped under `python -O`); and it fires only on import of the one file that already knew to worry. §8. |
| **11** | **The join a real accessor needs does not exist as data anywhere.** Three vocabularies are live — corpus labels (`PRIVATE`, `LIVING_DINING`, …), ergonomic keys (`bedroom_double`, `living_dining`, …), AZ cells (`living_room_2plus`, …). The profile publishes the second→third bridge (`mapping`). The **first→second** bridge is hand-written in Python in at least three places and is nowhere in `data/`. §9.1. |
| **12** | **A correction to minima.md §1.** Its stated extraction limitation — *"the two AzDTN norm PDFs embed fonts without a ToUnicode map, so text extraction silently drops Azerbaijani diacritics … and Cyrillic entirely"* — **does not hold for a `pypdf` extraction**. Diacritics and the Cyrillic «СНиП 2.08.01-89\*» on the cover page both survive intact. Every Azerbaijani quotation in this note is machine-extracted, not re-diacriticised by hand. §1.2. |

---

## 0.1 The six-value verdict, one line each

Verdicts are `law ↔ JSON ↔ Python`. "**match**" means all three agree on the
number *and* on what the number is a floor on.

| # | Python symbol | value | verdict |
|---|---|---|---|
| 1 | `STAT_FLOOR["KITCHEN"]` | 8.0 | **MATCH.** cl. 5.7 *«mətbəx - 8 m²-dən»* = `areas_m2.kitchen.statutory_floor.v` 8.0 = code 8.0. |
| 2 | `STAT_FLOOR["KITCHEN_DINING"]` | 6.0 | **MISMATCH — semantic, not numeric. The Python is wrong.** The number transcribes correctly; the *referent* does not. Law floors the **kitchen zone within** the room; the Python floors **the room**. Under-strict by an amount the law does not state. §5.1. |
| 3 | `STAT_FLOOR["PRIVATE"]` | 10.0 | **MATCH.** cl. 5.7 *«iki adama - 10 m²-dən»* = `areas_m2.bedroom_double.statutory_floor.v` 10.0 = code 10.0. Genuinely the double. |
| 4 | `STAT_FLOOR_LENIENT["PRIVATE"]` | 8.0 | **MATCH.** cl. 5.7 *«yataq otağı - 8 m²»* = `areas_m2.bedroom_single.statutory_floor.v` 8.0 = code 8.0. |
| 5 | `LIVING_1OTAQ` | 15.0 | **MATCH.** cl. 5.7 *«birotaqlı mənzildə ümumi otaq - 15 m²-dən»* = `areas_m2.living_room_1room_flat.statutory_floor.v` 15.0 = code 15.0. ⚠️ The **guard's input** is defective — see §6. |
| 6 | `LIVING_2PLUS` | 16.0 | **MATCH.** cl. 5.7 *«iki və daha çox otaqlı mənzillərdə ümumi otaq - 16 m²-dən»* = `areas_m2.living_room_2plus.statutory_floor.v` 16.0 = code 16.0. ⚠️ Same guard defect; and zero headroom against the soft target — §7. |

**Five of six are clean transcriptions of a correctly-read law. One is a number
copied without its referent. Two are correct values reached through a defective
guard.**

---

## 1. What was read first-hand, and what was not

`conf: verified` means read in the primary document named, in this session.

### 1.1 Obtained

| Document | Obtained | How |
|---|---|---|
| **AzDTN 2.7-2** «Yaşayış binaları. Layihələndirmə normaları», Bakı 2021, 28 pp. | **yes, live** | Downloaded during this session from the State Committee's own register, `https://arxkom.gov.az/qanunvericilik/normativler/binalarin-muhendis-sistemleri/zhilye-zdaniya`. **md5 `4b5da47dd11808cd0aef37a75b01b4e9`, byte-identical to the repo's cached `experiments/finish-layer/src/azdtn_2_7_2.pdf`.** cl. 5.1, 5.2, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10 and the front matter read. |
| **AzDTN 2.7-3** «Fərdi yaşayış evləri. Layihələndirmə normaları», Bakı 2023, 12 pp. | **yes** | Repo cache `experiments/finish-layer/src/azdtn_2_7_3.pdf`. cl. 5.1 and 5.2 read. |
| `data/standards/room-constraints.json` | yes | Read in full; every AZ cell, mapping row and guard resolved programmatically. |
| `experiments/warp/absolute_area.py`, `floor_warp.py`, `fit_warp.py`, `project_join.py` | yes | Read in full. |
| `experiments/warp/out/dwelling_rooms.json` (46,794 converted dwellings) | yes | Used to measure the exposure of §6 and §7. |
| `docs/research/az-region-profile/minima.md` | yes | Read in full; §2, §4, §7, §7A, §9, §11 relied on. |

### 1.2 The extraction is machine-verifiable, contrary to minima.md §1

minima.md §1 records that *"the two AzDTN norm PDFs embed fonts without a
ToUnicode map, so text extraction silently drops Azerbaijani diacritics (ə, ş, ç,
ğ, ı, ö, ü) and Cyrillic entirely"*, and that every Azerbaijani quotation there
was **re-diacriticised by hand**.

**That is a property of the extractor, not of the PDF.** Three independent
extractions of cl. 5.7 were taken here and cross-checked:

1. the repo's cached text, `experiments/finish-layer/out/azdtn_2_7_2.txt` — diacritics intact;
2. `pdftotext -layout` on the **live-downloaded** PDF — diacritics stripped (this reproduces minima.md's symptom);
3. `pypdf.PdfReader(...).extract_text()` on the **live-downloaded** PDF — diacritics intact.

All three agree on every numeral and on the word `zonası`. The cover page's
Cyrillic «СНиП 2.08.01-89\*» also survives (1) and (3), so **§4.4's repeal
sentence no longer needs reconstruction from the SİYAHI** — it can be read.
This is a strict improvement on minima.md's stated confidence and should be
carried back to it.

### 1.3 NOT obtained — stated plainly

- **The SİYAHI (the Art. 14.2 in-force list) could not be re-read in this
  session.** `experiments/finish-layer/src/az_siyahi_2025.pdf` is **not a PDF** —
  it is a 1,893-byte HTML error page. `az_siyahi_cand.pdf` is a real PDF but is a
  *different document* (a Cabinet of Ministers decision on the composition of
  urban-planning documents); it returns **zero** hits for "2.7-2". So the claim
  *AzDTN 2.7-2 is currently in force and SNiP 2.08.01-89\* is not* rests on
  **minima.md §1 and §4.4's authority, not mine** — with one corroboration I can
  add: the issuing authority is serving this exact edition of the norm today,
  from its own register, and the file has not changed. See §10.
- **No amendment (`dəyişiklik`) search succeeded.** A web search for a post-2021
  amendment to AzDTN 2.7-2 returned the committee's index and sibling norms only.
  Absence of evidence; §10.
- **Nothing here re-verifies minima.md's other tiers** — the `accessible` tier
  (ВСН 62-91\*), the clear widths, the heights. They are out of ticket 69's scope
  and are cited, not re-read.

---

## 2. What the law actually says

### 2.1 AzDTN 2.7-2, clause 5.7 — verbatim

Read first-hand, from the live download. The lead-in and all six bullets:

> **5.7.** Normaların 5.2-ci bəndində göstərilmiş mənzillərdə otaqların sahəsi
> aşağıdakılardan **az olmamalıdır**:
>
> - birotaqlı mənzildə ümumi otaq — **15 m²**-dən;
> - birotaqlı mənzillərin girişində qarderob — **2,5 m²**-dən;
> - iki və daha çox otaqlı mənzillərdə ümumi otaq — **16 m²**-dən;
> - yataq otağı — **8 m²** (iki adama — **10 m²**-dən);
> - mətbəx — **8 m²**-dən;
> - **mətbəx-yemək otağında mətbəx zonası** — **6 m²**-dən.
>
> Birotaqlı mənzillərdə sahəsi **5 m²**-dən az olmayan taxça-mətbəxin
> layihələndirilməsinə **yol verilir**.
>
> Mansarda mərtəbəsində (və ya maili xarici divarı olan mərtəbədə) yataq otağı və
> mətbəxin sahəsinin **7 m²**-dən az olmamaqla qəbul edilməsinə yol verilir, bu
> halda ümumi yaşayış otağının sahəsi **16 m²**-dən az olmamalıdır.

*"In the apartments identified in cl. 5.2 of these Norms the area of rooms
**shall not be less than** the following: in a one-room apartment the common room
— 15 m²; at the entrance of one-room apartments a wardrobe — 2.5 m²; in
apartments of two or more rooms the common room — 16 m²; bedroom — 8 m² (for two
persons — 10 m²); kitchen — 8 m²; **the kitchen zone in a kitchen-dining room —
6 m²**. In one-room apartments the design of a kitchen-niche of not less than
5 m² is permitted. In a mansard storey (or a storey with a sloping external wall)
a bedroom and a kitchen may be taken at not less than 7 m², provided the general
habitable room is not less than 16 m²."*

### 2.2 The six values the ticket asks about

| room | AzDTN 2.7-2 cl. 5.7 | Azerbaijani | conf | force |
|---|---|---|---|---|
| **kitchen** | **8.0 m²** | *mətbəx* | verified | statutory |
| **kitchen zone in a kitchen-diner** | **6.0 m²** — ⚠️ **the ZONE, not the room** | *mətbəx-yemək otağında mətbəx zonası* | verified | statutory |
| **bedroom, single** | **8.0 m²** | *yataq otağı* | verified | statutory |
| **bedroom, double** | **10.0 m²** | *yataq otağı … iki adama* | verified | statutory |
| **living room, 1-otaq flat** | **15.0 m²** | *birotaqlı mənzildə ümumi otaq* | verified | statutory |
| **living room, 2+ otaq** | **16.0 m²** | *iki və daha çox otaqlı mənzillərdə ümumi otaq* | verified | statutory |

Three points on the reading, each checked against the text:

**"ümumi otaq" is the living room.** cl. 5.5 enumerates habitable rooms as
*«yaşayış otaqlarının (otaq, qonaq otağı və yataq otağı)»* — room, guest room,
bedroom — while cl. 5.7's area list calls the same room *ümumi otaq*, common
room. The profile records this two-word problem at
`mapping.rooms.living.name_az.note` and publishes `qonaq otağı`; that is a
naming decision, not a values one, and it does not affect any figure here.

**The otaq condition is in the law, not invented by the engine.** cl. 5.7 splits
*birotaqlı mənzildə* from *iki və daha çox otaqlı mənzillərdə* explicitly. The
threshold is 1 versus 2-or-more. There is no third limb.

**The bedroom split is on OCCUPANCY, not on bed size.** *«yataq otağı - 8 m²
(iki adama - 10 m²-dən)»* — 10 m² is owed to a room *for two people*. The
profile's `mapping.rooms.bedroom_double.bridge` states this and notes the
ergonomic key splits on *bed capacity* instead, with the two axes coinciding by
meaning rather than by definition. That bridge is correct and is not restated
here.

### 2.3 The register — this is mandatory, and the rule is the norm's own

`az olmamalıdır` = *məcburi* (mandatory), per minima.md §4.2's rule taken from
the AzDTN system's governing document («Əsas müddəalar (Konsepsiya)», Bakı 1994,
§§3.1, 3.2, 3.4, 3.6). The rule and its check both hold on the text I read:

- **cl. 5.7** — `az olmamalıdır`. **Mandatory.**
- **cl. 5.1** in the same section — read first-hand: *«…cədvəl 1 əsasında … qəbul
  edilməsi **tövsiyə olunur**»*. **Recommended.** The two clauses sit five
  paragraphs apart and land on opposite sides of the register test, which is
  minima.md §4.2's own evidence that the rule is real and not post-hoc. I
  confirm it independently.
- **cl. 5.6** — *«Mənzilin yaşayış otaqlarının və digər sahələrinin ölçüləri
  erqonomikanın tələblərinə uyğun … müəyyənləşdirilir»*. The delegation of plan
  dimensions to ergonomics, confirmed verbatim.
- **cl. 5.9** — *«Mənzillərdə yataq otaqları digər otağa keçid kimi
  layihələndirilməməlidir»*. **Mandatory**, and it is `is_private` stated as law.
- **cl. 5.8** — habitable rooms and kitchen `2,7 m-dən az olmamalıdır`;
  intra-apartment corridors, halls, antresols `2,1 m-dən az olmamalıdır`.
  **Mandatory.** Both confirmed.

### 2.4 The market tier's source, also read first-hand

AzDTN 2.7-3 cl. 5.1, the recommended list, verbatim:

> Layihələndirilən və yenidən qurulan fərdi evlərin yerləşgələrinin sahələri
> aşağıdakılardan az olmamaqla qəbul edilməsi **tövsiyə edilir**:
> - ümumi otaqlar (və ya qonaq otağı) — 16 m²;
> - yataq otağı — 9 m² (iki nəfərə 12 m², mansardda yerləşdirdikdə — 8 m²);
> - təkərli oturacaq təyin edilmiş əlilliyi olan şəxslərin: yataq otağı — 9 m²;
> - mətbəx — 9 m²;
> - **mətbəx-yemək otağında mətbəx zonası — 6 m²**;
> - hamam otağı — 3,2 m²;
> - birləşdirilmiş sanitar qovşağı — 3,8 m².

`tövsiyə edilir` — **recommended**. And note the width list immediately after it
uses `qəbul edilməlidir` — **mandatory** — inside the same clause. minima.md §9's
`force_note` for `az_azdtn_2_7_3` records exactly this split; confirmed.

**⚠️ Building type.** AzDTN 2.7-3 binds *fərdi yaşayış evləri* — detached houses,
at most 3 storeys and 12 m. It is **not** the building type this engine draws.
Every `market_default` figure below inherits that transfer caveat, which the JSON
already carries in each cell's `note` and `conf: derived`.

---

## 3. Legal force of each source

Explicit, per the house rule. Force is assigned from the **clause's verb**, never
from the tier's name.

| src_key | document | force | why |
|---|---|---|---|
| `az_azdtn_2_7_2` | AzDTN 2.7-2, Bakı 2021 | **`statutory`** | Technical normative legal act (Urban Planning and Construction Code, Law 392-IVQ of 2012-06-29, Art. 3.0.26); compliance obligatory under **Art. 14.3**; registered in the State Register of Legal Acts at **No. 15202111300003** — read first-hand on the norm's own front matter, together with Collegium decision **No. 03 of 30.11.2021**, entry into force **30.11.2021**, *İlk dəfə qəbul edilir*, code `AzDŞAK-TN/Q № 0030-2021`. **cl. 5.7 is in the mandatory register.** |
| `az_azdtn_2_7_3` | AzDTN 2.7-3, Bakı 2023 | `statutory` **for detached houses**; **never** statutory for an apartment | Same legal basis, **different building type**. Its cl. 5.1 *area* list is `tövsiyə edilir` (recommended) even for houses. Transferred to the apartment case it is at most a `market_default` proxy and `conf` degrades to `derived`. |
| `az_sehersalma_mecellesi_2012` | Urban Planning and Construction Code | `statutory` | The instrument that gives every AzDTN its force. **Not re-read here** — minima.md §4.1's authority. |
| `az_azdtn_system_1994` | «Əsas müddəaları (Konsepsiya)» | `statutory_guidance` | The source of the `məcburi`/`tövsiyə` rule. **Not re-read here** — minima.md §4.2's authority. |
| `az_siyahi_2026` / `az_register_2026` | SİYAHI, the Art. 14.2 in-force list | `statutory_guidance` | ⚠️ **Not obtainable in this session** (§1.3). The in-force claim inherits minima.md §1 and §4.4's authority, **not mine**. |
| `su_snip_2_08_01_89` | СНиП 2.08.01-89\* | **`superseded` in AZ** | AzDTN 2.7-2's cover page, read first-hand: *"Bu texniki normativ hüquqi akt qüvvəyə mindiyi tarixdən **СНиП 2.08.01-89\*** «Жилые здания» normativ sənədin Azərbaycan Respublikası ərazisində hüquqi qüvvəsi dayandırılır."* May be cited for lineage. **May not be cited as a live AZ minimum.** |
| `ru_sp_54_13330` | СП 54.13330 | `foreign_not_applicable` | Russian, never AZ law. Used below **only** as a corroborating comparator for the shape of the 6 m² kitchen-zone rule. **No value from it reaches any AZ figure.** |

**What the JSON asserts, and where.** `tier_model.validator_binding` publishes
`hard_reject_below: ["ergonomic", "statutory_floor"]` and
`statutory_floor_binding: "hard"`; `data/acceptance/rules.json`'s `tier_binding`
holds the same list. So the statutory floor is hard in the shipped data, which is
what makes a drift in (c) a geometry defect rather than a reporting one.

---

## 4. The three-way comparison

### 4.1 How the JSON resolves — and it is a two-step lookup, not a key

`az_area` is **an ordered guard list, not a scalar**
(`mapping.row_format.az_area`: *"ordered guard list into
`profiles.AZ.rooms.areas_m2`, or null"*). `mapping.conditioning` fixes the
semantics: one axis, `when_otaq_count`; `when_otaq_count: 1` matches a one-otaq
dwelling; `null` is the unguarded fallthrough and **must be last**; **first match
wins**. `gate_check.vocabulary_gates` V2 asserts the well-formedness. Resolved
programmatically here, at both otaq = 1 and otaq = 3.

### 4.2 The table

Areas in m². `statutory_floor` unless marked. **Bold** = the six values ticket 69
names.

| corpus label | erg key | AZ cell (resolved) | **(a) law** cl. 5.7 | **(b) JSON** `statutory_floor` | **(c) Python** | verdict |
|---|---|---|---|---|---|---|
| `KITCHEN` | `kitchen` | `kitchen` | **8.0** *mətbəx* | **8.0** | **8.0** `STAT_FLOOR` | **match** |
| `KITCHEN_DINING` | `kitchen_dining` | `kitchen_zone_in_diner` | **6.0** — of the **zone inside** the room | **6.0** — cell name says `..._zone_in_diner`; `bridge` says "constrains a ZONE, not the ROOM" | **6.0** applied to **the Room** | **MISMATCH (semantic). (c) is wrong.** §5.1 |
| `PRIVATE` | `bedroom_double` | `bedroom_double` | **10.0** *iki adama* | **10.0** | **10.0** `STAT_FLOOR` | **match** |
| `PRIVATE` (lenient) | `bedroom_single` | `bedroom_single` | **8.0** *yataq otağı* | **8.0** | **8.0** `STAT_FLOOR_LENIENT` | **match** |
| `LIVING_ROOM` / `LIVING_DINING`, otaq = 1 | `living` / `living_dining` | `living_room_1room_flat` | **15.0** *birotaqlı* | **15.0** | **15.0** `LIVING_1OTAQ` | **match** (guard input defective — §6) |
| `LIVING_ROOM` / `LIVING_DINING`, otaq ≥ 2 | `living` / `living_dining` | `living_room_2plus` | **16.0** *iki və daha çox* | **16.0** | **16.0** `LIVING_2PLUS` | **match** (guard input defective — §6) |
| `DINING` | `dining` | — (`az_area: null`) | *silent* | **null** (no cell) | `floors_for` → `None` | **match** — correctly silent |
| `BATHROOM` | `bathroom` | `bathroom` | *silent* | **null** *(cell exists; `market_default` 3.2)* | `floors_for` → `None` | **match** on the value; ⚠️ reached through a **non-null** `az_area` — §4.3 |
| `CORRIDOR` | `corridor` | — (`az_area: null`) | *silent* | **null** (no cell) | `floors_for` → `None` | **match** |
| `STOREROOM` | `storage` | — (`az_area: null`) | *silent* | **null** (no cell) | `floors_for` → `None` | **match** |
| *(vocabulary only; absent from the corpus)* `WC` | `wc` | `wc` | *silent* | **null** *(cell exists, all tiers null)* | `floors_for` → `None` | match; same non-null `az_area` shape as `BATHROOM` |

And the market tier, `absolute_area.MARKET` against
`areas_m2.<cell>.market_default.v`:

| Python | value | JSON `market_default` | law (AzDTN 2.7-3 cl. 5.1) | verdict |
|---|---|---|---|---|
| `MARKET["KITCHEN"]` | 9.0 | `kitchen` 9.0 | *mətbəx — 9 m²* | **match** |
| `MARKET["KITCHEN_DINING"]` | 6.0 | `kitchen_zone_in_diner` 6.0 | *mətbəx zonası — 6 m²* | **match** numerically; inherits §5.1's zone/room defect |
| `MARKET["PRIVATE"]` | 12.0 | `bedroom_double` 12.0 | *iki nəfərə 12 m²* | **match** |
| `MARKET["LIVING_ROOM"]` / `["LIVING_DINING"]` | 16.0 | both living cells 16.0 | *ümumi otaqlar (və ya qonaq otağı) — 16 m²* | **match** |
| `MARKET["BATHROOM"]` | 3.2 | `bathroom` 3.2 | *hamam otağı — 3,2 m²* | **match** |
| *(absent)* `DINING` | — | `dining` has no cell | *silent* | **match** — correctly absent |
| *(absent)* `bathroom_combined` 3.8 | — | 3.8 published | *birləşdirilmiş sanitar qovşağı — 3,8 m²* | not a corpus label; unreachable from this rig. Not a defect. |

**All eleven Python numbers across both tiers transcribe their JSON cell exactly,
and every JSON cell transcribes its clause exactly.** The arithmetic is clean.
Everything below is about what the numbers *mean* and what carries them.

### 4.3 There are TWO nulls, and the Python's comment collapses them

`absolute_area.py:86-88` says the non-floored labels *"map to a null az_area,
which room-constraints.json says means NO STATUTORY FLOOR"*. Both halves need
correcting, and the correction is load-bearing for the accessor ticket 69 wants.

**Null one — `mapping.rooms.<k>.az_area is null`.** No cell is reachable at all.
True for `dining`, `corridor`, `storage` (and `study`, `shower_room`, `utility`,
`entrance_lobby`, `living_dining_kitchen`… among keys the corpus does not emit).

**Null two — a cell IS reached and its `statutory_floor` is null.** True for
`bathroom` (whose `market_default` is a live 3.2) and `wc` (all tiers null). An
accessor that only tests `az_area is None` will `KeyError` or mis-handle these.

**And the file does not say what the comment says it says.** `mapping.null_means`
is explicitly about the **soft** tier — *"NO SOFT TARGET, NOT AN ERROR.
`dim.market_default_area` skips a Space whose az_area resolves to null"* — and
goes on: *"The hard floor always resolves, because it is ergonomic and
region-invariant."* The key that actually licenses "no statutory floor here" is
`tier_model.validator_binding.statutory_floor_note`: *"the 'only where non-null'
half survives verbatim"*. The conclusion is right; the citation is not.

---

## 5. The four soft spots the ticket named

### 5.1 `KITCHEN_DINING` 6.0 — the number is right, the referent is not

**This is the one substantive defect in the six.**

**What the law says.** cl. 5.7, sixth bullet, read three ways in §1.2 and
identical in all three: *«mətbəx-yemək otağında **mətbəx zonası** - 6 m²-dən»*.
`mətbəx-yemək otağı` = kitchen-dining room. `mətbəx zonası` = **kitchen zone**.
`-da/-də` is the locative. The floor is on the **zone inside** the room.

**What the profile says.** The cell is named `kitchen_zone_in_diner` — the name
alone carries it. And the profile says it twice more, in prose:

- `mapping.rooms.kitchen_dining.bridge`: *"**THE AZ CELL CONSTRAINS A ZONE, NOT
  THE ROOM.** cl. 5.7's 6 m² is the `mətbəx zonası` INSIDE the mətbəx-yemək
  otağı, not the whole room, while the ergonomic 4.6 m² floor is the whole room.
  So the AZ number is a soft target for a PART of what the ergonomic key
  measures, and **reading it as a room target under-targets the room**. Flagged
  rather than fixed … Handed to rules.json's holder."*
- `ergonomic.counts_as_otaq_sourcing.per_key.kitchen_dining.note`: *"cl. 5.7
  names this `mətbəx-yemək otağı` and **constrains only its `mətbəx zonası`**"*.

**What the Python does.** `floors_for` returns `STAT_FLOOR["KITCHEN_DINING"]`
= 6.0 for a Room of that type, and `floor_warp.floors_m2` hands it to
`warp_model_constrained`, which posts `sum(part areas) >= 6.0` **on the whole
Room's Space area**. The transcription carried the number and dropped the
qualifier.

**Why it matters, precisely.** The defect is **under-strictness**, not
over-strictness:

- A compliant `mətbəx-yemək otağı` holds a kitchen zone of ≥ 6.0 m² **plus** a
  dining zone. The room is therefore necessarily **larger** than 6.0 m².
- AzDTN publishes **no** dining-zone area and **no** whole-room area for this
  type. So the correct whole-room statutory floor is **unquantified** — it is not
  6.0, and this note cannot say what it is.
- The posted 6.0 admits a 6.0 m² kitchen-diner. That room cannot hold a
  6 m² kitchen zone and a dining zone, so it is not a room cl. 5.7 permits.
- The ergonomic floor for `kitchen_dining` is 4.6 m² (whole room), which is below
  6.0 — so `max(ergonomic, statutory)` still returns 6.0 and the ergonomic layer
  does not rescue it.

**Exposure, measured.** `KITCHEN_DINING` occurs **41 times** across 46,794
converted dwellings (`out/dwelling_rooms.json`) — 0.013 % of 319,222 rooms. The
defect is real and its blast radius today is negligible. It becomes material the
moment a Brief can name `kitchen_dining` at volume, which `brief.md` §3 permits.

**Is 6.0 the SNiP folklore number in a second slot? No.** minima.md finding 8 and
§11.1 established that the string "6 m²" for a kitchen appears **nowhere** in
SNiP 2.08.01-89\*, and that the folklore 12/6 pair is unsourced and must not be
cited. The 6.0 here is a **different provision entirely** and is carried by three
instruments:

| instrument | clause | text | force for AZ |
|---|---|---|---|
| AzDTN 2.7-2 | cl. 5.7 | *mətbəx-yemək otağında mətbəx zonası — 6 m²-dən* | **statutory** — read first-hand |
| AzDTN 2.7-3 | cl. 5.1 | *mətbəx-yemək otağında mətbəx zonası — 6 m²* | recommended, detached houses — read first-hand |
| СП 54.13330 | cl. 5.11 | kitchen zone in a kitchen-diner, 6 m² | `foreign_not_applicable` — comparator only, per minima.md §11.5 |

Note further that SNiP 2.08.01-89\* has **no kitchen-zone rule at all** — minima.md
§11.5 records that the 6 m² zone rule and the 10 m²-for-two rule are exactly the
two provisions AzDTN carries from the **modern SP line** and not from the 1989
SNiP. So the folklore hypothesis is not merely unproven, it is **contradicted**:
the number could not have come from the document the folklore is attributed to.

**Verdict.** `KITCHEN_DINING` 6.0 is a correct transcription of a correct cell of
a correctly-read law, applied to the wrong quantity. **The Python is the wrong
one of the three.** The fix is not a value edit — `room-constraints.json` is
right — and it is not this note's to make. The two candidate shapes both cost
more than a value edit: a zone concept the geometry model does not have, or a
derived whole-room floor which would be an `engine_choice` and not a statutory
figure at all. The profile has already handed this to `rules.json`'s holder;
ticket 69 should note that ADR 0033 has now made it a **geometry** question and
not only a targeting one.

### 5.2 `PRIVATE` 10.0 / lenient 8.0 — both limbs confirmed

**The law.** cl. 5.7: *«yataq otağı - 8 m² (iki adama - 10 m²-dən)»*. Bedroom
8 m²; for two persons, 10 m². Read first-hand. Unambiguous, and **10.0 is
genuinely the double**.

**The corpus ambiguity is real and correctly handled.** `fit_warp.COLLAPSE`
maps `{ROOM, BEDROOM, STUDIO} → PRIVATE`; `out/dwelling_rooms.json` contains
105,425 `PRIVATE` rooms and no finer label. The corpus cannot say which are
one-occupant and which are two. Reporting both limbs — `STAT_FLOOR` at 10.0 as
primary, `STAT_FLOOR_LENIENT` at 8.0 — is the honest response, and ADR 0033
records that its decision does not turn on which limb is right (baseline
violations 31.6 % at `bedroom_double` against 25.1 % at `bedroom_single`).

**One thing the code comment gets slightly wrong.** It says *"`bedroom_double` 10
is the ticket's own naming and the primary"*. `bedroom_double` is not a ticket's
naming — it is a shipped **ergonomic key** with its own published `min_area` of
3.1 m², and it is one of the profile's two AZ bedroom cells. Cosmetic, but the
sentence reads as if the primary limb were a local choice when it is a data key.

**A three-to-two collapse sits underneath, and the profile documents it.**
Three ergonomic keys (`bedroom_principal`, `bedroom_double`, `bedroom_single`)
map onto two AZ cells; `bedroom_principal` and `bedroom_double` both resolve to
`bedroom_double` 10.0. `mapping.rooms.bedroom_principal.bridge` explains that the
ergonomic split is on **bed capacity** and cl. 5.7's on **occupancy**, and that
they coincide by meaning. That reasoning is sound against the clause text I read.

**Verdict: match, both limbs.**

### 5.3 `LIVING_1OTAQ` 15.0 / `LIVING_2PLUS` 16.0 — the pair and the threshold are AzDTN's own

**Does the law condition on room count at all?** **Yes, explicitly.** cl. 5.7
distinguishes *birotaqlı mənzildə* (in a one-room apartment) from *iki və daha
çox otaqlı mənzillərdə* (in apartments of two or more rooms), as two separate
bullets. There is no third limb and no other conditioning axis anywhere in the
clause. The profile's `mapping.conditioning` says the same — *"ONE AXIS, NAMED …
`when_otaq_count` … Three AZ area cells condition on the same thing — cl. 5.7's
`birotaqlı mənzil`"* — and it is right.

**Are the two limbs right?** Yes: 15.0 and 16.0, read first-hand.

**Is the threshold right?** Yes: `floors_for` uses `LIVING_1OTAQ if otaq == 1
else LIVING_2PLUS`, which is exactly the guard the mapping publishes
(`when_otaq_count: 1 → living_room_1room_flat`, `null → living_room_2plus`,
first match wins).

**Is 15/16 a blend of two instruments? No — it is AzDTN's own pair, and the
divergence runs the other way.** minima.md finding 8 warned that the dead SNiP's
living room is "14/16, not 12". Checked:

| instrument | 1-room flat | 2+ rooms |
|---|---|---|
| **AzDTN 2.7-2 cl. 5.7 (AZ, live, statutory)** | **15.0** | **16.0** |
| SNiP 2.08.01-89\* cl. 2.4\* (superseded in AZ) | 14.0 | 16.0 |
| СП 54.13330 cl. 5.11 (RU, not AZ law) | 14.0 | 16.0 |

Both comparators say **14**. Azerbaijan is the outlier at **15**, and minima.md
§11.3 and §11.4 flag it as one of AZ's three own divergences — plausibly
originating in the 2002–05 Azerbaijani amendment acts to SNiP 2.08.01-89\*, whose
text could not be obtained. So 15/16 is **not** a blend; if anything, the value a
careless transcription would have produced is 14/16, and it did not.

**Verdict: match, both limbs and the threshold.** ⚠️ But see §6 — the guard's
**input** does not match the profile, and §7 — the 16.0 limb has zero headroom.

### 5.4 Tier bleed — checked, and there is none

The concern: `LIVING` 16.0 appears in both `STAT_FLOOR` (via `LIVING_2PLUS`) and
`MARKET`, so one may have been copied into the other.

**It is a real coincidence and it is verified in two separate documents.**

| value | `statutory_floor` source | `market_default` source | same? |
|---|---|---|---|
| living 16.0 | **AzDTN 2.7-2** cl. 5.7, *iki və daha çox otaqlı mənzillərdə ümumi otaq* — apartments, **mandatory** | **AzDTN 2.7-3** cl. 5.1, *ümumi otaqlar (və ya qonaq otağı)* — detached houses, **recommended** | different instrument, different building type, different register — **same number** |
| kitchen zone 6.0 | **AzDTN 2.7-2** cl. 5.7 | **AzDTN 2.7-3** cl. 5.1 | same |

Both pairs were read verbatim in both documents in this session (§2.1, §2.4).
**Not a copy error.**

And the tiers are otherwise cleanly separated in the Python — every value in
`MARKET` is at or above its `STAT_FLOOR` counterpart, and each traces to the
2.7-3 clause rather than the 2.7-2 one:

| | statutory (2.7-2) | market (2.7-3) | separation |
|---|---|---|---|
| kitchen | 8.0 | 9.0 | +1.0 |
| bedroom (double) | 10.0 | 12.0 | +2.0 |
| living, 1 otaq | 15.0 | 16.0 | +1.0 |
| **living, 2+ otaq** | **16.0** | **16.0** | **0.0** ⚠️ §7 |
| **kitchen zone** | **6.0** | **6.0** | **0.0** ⚠️ §7 |
| bathroom | *null* | 3.2 | n/a |

**No value has bled between tiers.** Two pairs coincide, and the coincidence is
the law's, not the transcriber's. The consequence of the coincidence, however, is
a finding in its own right — §7.

---

## 6. A seventh hand-copied value, and this one is wrong

Ticket 69 counts six. There is a seventh, it is not in `STAT_FLOOR`, and it
selects which of the six limbs is applied.

```python
HABITABLE = ("PRIVATE", "LIVING_ROOM", "LIVING_DINING")  # ADR 0013: otaq
...
otaq = sum(1 for t in types if t in HABITABLE)
liv  = LIVING_1OTAQ if otaq == 1 else LIVING_2PLUS
```

`HABITABLE` is a hand copy of the profile's `counts_as_otaq` flag, and **it
omits `DINING`.**

**What the profile publishes.** `ergonomic.rooms.dining.counts_as_otaq` = `true`,
sourced at `counts_as_otaq_sourcing.per_key.dining`: *"Not named in cl. 5.5's list
by its own word; admitted through the list's first member `otaq`, which is the
unqualified catch-all. **DERIVED**, not verified — AzDTN never says this room is
or is not an otaq."* And `gate_check` V6 asserts that `is_habitable` and
`counts_as_otaq` diverge on **exactly** `kitchen_dining` — so `dining` counting
as an otaq is a gated, tested property of the shipped data.

**What the Python does with it.** `DINING` is not in `HABITABLE`, so it
contributes 0. Where a dwelling's only other habitable room is the living room
itself, the Python computes otaq = 1 and the profile computes otaq = 2.

**The direction of the error is the dangerous one.** The Python then selects
`LIVING_1OTAQ` = **15.0** where the profile's guard selects `living_room_2plus` =
**16.0**. Under ADR 0033 the warp posts 15.0 as a hard constraint and will accept
a living room at 15.0 m² in a dwelling AzDTN floors at 16.0 — **a room built
1.0 m² below the law**. That is precisely the C8-failure-from-the-inside ADR 0033
exists to prevent, arriving through a value nobody counted.

**Exposure, measured** over the 46,794 converted dwellings in
`experiments/warp/out/dwelling_rooms.json`:

| | count | share |
|---|---:|---:|
| dwellings containing a `DINING` room | 1,308 | 2.80 % |
| dwellings whose otaq count flips 1 → 2+ when `DINING` counts | **85** | **0.18 %** |
| …of which also carry a living-family room (floor moves 15.0 → 16.0) | **59** | **0.13 %** |

Small, and not zero, and it is a **silent** wrong answer rather than a refusal.

**Two caveats, stated so nobody over-reads this.** First, the profile marks
`dining.counts_as_otaq` as `conf: derived`, not `verified` — AzDTN never rules on
it. So this is a Python-versus-profile disagreement, and the profile's own
confidence in its side is one notch below verified. It is still the contract.
Second, `HABITABLE` correctly **excludes** `KITCHEN_DINING`, which is the one
type where `is_habitable` and `counts_as_otaq` diverge — so the hand copy got the
hard case right and the easy one wrong.

**Verdict: `HABITABLE` is a seventh unbound transcription and it does not match
the profile.** Any accessor ticket 69 writes must read `counts_as_otaq` from the
JSON alongside the floors, or the guard stays wrong while the six values it
guards are right.

---

## 7. The tier coincidence has a consequence: zero headroom on the biggest limb

Not a transcription defect — every number is right — but it falls straight out of
the three-way comparison and it revises a claim in ADR 0033.

**ADR 0033, "What was measured":**

> **The floor never fights a target.** `moved_rooms = 0` across every arm: under
> `dim.market_default_area` every target already sits **at or above** its floor
> (kitchen 9,0 against 8,0; PRIVATE 12,0 against 10,0; **living 16,0 against
> 15/16**), which is §11.1 ground 2's own stated condition.

For two limbs, "at or above" is **at**:

| limb | soft target (`market_default`) | hard floor (`statutory_floor`) | margin |
|---|---:|---:|---:|
| kitchen | 9.0 | 8.0 | +1.0 |
| PRIVATE (double) | 12.0 | 10.0 | +2.0 |
| living, **1 otaq** | 16.0 | 15.0 | +1.0 |
| **living, 2+ otaq** | 16.0 | **16.0** | **0.0** |
| **kitchen zone in diner** | 6.0 | **6.0** | **0.0** |

**And the zero-margin limb is the common case.** Measured over the same 46,794
dwellings:

| | dwellings | share |
|---|---:|---:|
| carrying a living-family room at otaq ≥ 2 → target 16.0, floor 16.0, **margin 0.0** | **30,450** | **65.1 %** |
| carrying a living-family room at otaq = 1 → target 16.0, floor 15.0, margin 1.0 | 2,059 | 4.4 % |
| carrying a `KITCHEN_DINING` room → target 6.0, floor 6.0, margin 0.0 | 41 | 0.09 % |

**Why this matters against ADR 0033's own consequence 3.** The posted floor is
converted from a Space area to grid cells using an erosion overhead read at the
**affine seed**, and the shape moves under the warp. Consequence 3 measures the
residual: shortfalls at p50 **0.038 m²**, max **0.438 m²**, and calls it "grid
dust". Against a +1.0 m² or +2.0 m² margin it is dust. Against a **0.0** margin
on 65 % of dwellings it is the entire safety factor, and the residual 4.6 % of
candidates that still carry a Room below its floor is exactly where one would
expect it to land.

**This is not an argument to change anything here.** It is an argument that
ticket 67 (*the posted floor is a seed-shape estimate*) is load-bearing for the
`LIVING` limb specifically, and that the "floor never fights a target" line
should not be quoted as though every limb had slack. `moved_rooms = 0` is a
boundary result on the majority limb, not a comfortable one.

---

## 8. What binds the JSON to the Python today

### 8.1 The one guard that exists

`experiments/warp/floor_warp.py:85-95` — `_check_floor_transcription()`, run at
module import. Its own docstring is honest about its status:

> ⚠️ This is an assertion, not a fix. The fix is for `STAT_FLOOR` to be READ from
> the JSON rather than copied beside it.

It passes today; verified by importing the module in this session.

**What it covers.** The six scalar values, each against
`profiles.AZ.rooms.areas_m2.<key>.statutory_floor.v`, for `kitchen`,
`kitchen_zone_in_diner`, `bedroom_double`, `bedroom_single`,
`living_room_1room_flat`, `living_room_2plus`. If any cell's number moves and the
Python's does not, an import of `floor_warp` raises.

### 8.2 What it does NOT cover — seven gaps

1. **It bypasses the mapping, which ticket 69 itself names as the contract.**
   The assertion reads `areas_m2.<key>` **raw**. `mapping.comment` is explicit:
   *"THE MAPPING IS THE VOCABULARY; THE TABLES ABOVE ARE JUST VALUES."* Re-point
   `mapping.rooms.kitchen_dining.az_area[0].key` from `kitchen_zone_in_diner` to
   any other cell and **the assertion still passes** while the profile's meaning
   has changed. `gate_check` V2 would still pass too — it checks only that the
   target cell exists.
2. **It does not check the guard's condition.** Change
   `mapping.rooms.living.az_area[0].when_otaq_count` from `1` to `2` and the
   assertion passes; `floors_for`'s `otaq == 1` test is now wrong.
3. **It does not check the guard's ORDER.** `mapping.conditioning` says first
   match wins and the `null` limb must be last; `floors_for` hard-codes the
   two-limb shape. A third limb added to the JSON would be silently ignored.
4. **It does not check `HABITABLE` against `counts_as_otaq`** — §6, which is
   already wrong.
5. **It does not check `MARKET` at all.** Six more hand-copied values, feeding
   `dim.market_default_area`, the default tier and the solver's target. Ticket 69
   item 4 names this; the guard does not implement it. `absolute_area.MARKET` is
   verified correct in §4.2 **by this note**, not by any test.
6. **It fails open.** `if not src.exists(): return` — the check silently no-ops
   without `data/`. That is ticket 69 item 2's dilemma made concrete: today the
   fallback is "no check", which is the drift risk itself.
7. **It is a bare `assert`, stripped under `python -O`**, and it fires **only** on
   import of `floor_warp.py`. Running `python experiments/warp/absolute_area.py`
   directly — the documented invocation in that file's own docstring — never
   triggers it. So does importing `floors_for` from `project_join.py`, which does
   exactly that.

### 8.3 A related hand copy in the same directory

`experiments/warp/project_join.py:164` — `ERG_AREA`, ten values copied from
`ergonomic.rooms[*].min_area.v`. Spot-checked against the JSON in this session:
**all ten correct.** Unlike `STAT_FLOOR` it does not constrain geometry (it is
used only where `floors_for` returns `None`). Note that `project_join.py` already
carries `_check_min_side_identity()` — an import-time assertion of the same shape
— so the pattern is established in the file; `ERG_AREA` simply does not have one.

Both `ERG_AREA`'s comment and `floors_for`'s docstring repeat the "three carry a
floor / six do not" count from `absolute_area.py`. It is wrong in all three
places: over `project_join.KIND`'s ten labels it is **five and five**
(`PRIVATE`, `LIVING_ROOM`, `LIVING_DINING`, `KITCHEN`, `KITCHEN_DINING` carry one;
`DINING`, `BATHROOM`, `WC`, `CORRIDOR`, `STOREROOM` do not). `KITCHEN_DINING` is
counted on the wrong side in the prose while sitting in `STAT_FLOOR` two lines
below. The parenthetical "(0.5-1.7 m2)" is the give-away: that range is exactly
`{storage 0.5, wc 0.8, corridor 0.8, bathroom 1.7}` — **four** labels — and it
omits `dining` at 1.9 m². The conclusion the docstrings draw is nonetheless
sound: the ergonomic floor never binds against a statutory one, including for the
two limbs the prose forgot (`LIVING_DINING` 6.1 against 15/16, `KITCHEN_DINING`
4.6 against 6.0).

---

## 9. How the link could be made checkable

**Described, not chosen.** Ticket 69 owns the decision and
`experiments/warp/` has four open claimants (62, 65, 67, 69).

### 9.1 The three facts a reader needs

**The key path.** For a floor, two hops, not one:

```
profiles.AZ.rooms.mapping.rooms.<erg_key>.az_area   →  ordered guard list
    [ {when_otaq_count: 1|null, key: <cell>}, … ]   →  first match wins, null last
profiles.AZ.rooms.areas_m2.<cell>.statutory_floor.v →  the number, or the cell is null
```
plus `ergonomic.rooms.<erg_key>.counts_as_otaq` for the guard's input (§6), and
`profiles.AZ.rooms.areas_m2.<cell>.market_default.v` for the soft tier.

**Is the JSON loadable at import time?** **Yes, and cheaply.** 207,724 bytes,
`json.load` measured at **2.4 ms** on this machine. `floor_warp` already does it
on import. There is no performance argument against a live read.

**Is the erg_key mapping 1:1?** **No — it is many-to-one in two places, and the
corpus→ergonomic hop is not published anywhere.**

- *ergonomic → AZ cell* (published, `mapping`, gated by `gate_check` V1–V5, total
  over all 19 ergonomic keys): `living`, `living_dining`, `living_dining_kitchen`
  all → the two living cells; `bedroom_principal` and `bedroom_double` both →
  `bedroom_double`. Many-to-one, declared, one-way.
- *corpus label → ergonomic key*: **not in `data/` at all.** `absolute_area`
  works in corpus labels (`PRIVATE`, `LIVING_DINING`, …); the profile works in
  ergonomic keys. There are **three** live vocabularies — corpus labels,
  `solver-toy` kinds, ergonomic keys — and the bridges between them are
  hand-written Python in at least three files:
  `acceptance-thresholds/reject.py`'s `ERG` (reporting class → ergonomic key, and
  the closest thing to the table an accessor needs — note it also already reads
  `room-constraints.json` live, so the shape ticket 69 item 1 wants has a
  precedent in the repo); `project_join.KIND` (corpus label → **solver-toy**
  kind, a different target); and `h8-frontage/frontage_shipped.py`'s `MAP`
  (solver-toy kind → ergonomic key). Any accessor must pick or publish one.
- **The `PRIVATE` hop is genuinely 1-to-2** and no data can fix it: the corpus
  cannot say single from double, which is why both limbs exist (§5.2). The
  accessor has to keep the two-limb shape, not resolve it.

### 9.2 The options

| # | shape | what it fixes | what it costs |
|---|---|---|---|
| **A** | **Read at import through `mapping`.** `floors_for` resolves the guard list against the JSON instead of reading `STAT_FLOOR`. | Gaps 1–3 and 5 in §8.2 — a re-pointed guard, a changed condition, an added limb, `MARKET`. | Makes `data/` a hard dependency of `experiments/warp/` (ticket 69 item 2). 2.4 ms. Needs a published corpus→ergonomic table (§9.1). |
| **B** | **A gate in `gate_check.py`.** Assert the six values, `MARKET`, and `HABITABLE` against the profile, alongside the 238 gates already there. | Puts the check in the durable home ticket 69 item 3 names, and it runs whether or not any warp rig is imported. | Points `experiments/region-profile/` at `experiments/warp/`, which is a new dependency direction. Does not stop a rig **running** on a drifted table — it fails a gate afterwards. |
| **C** | **Widen the existing assertion** to resolve through `mapping`, cover `MARKET` and `HABITABLE`, and fail loudly rather than silently when `data/` is absent. | Gaps 1–6, cheaply, in the file that already has the guard. | Still ticket 69's *"a guard and not the fix"* — still import-scoped, still one consumer, still `assert`. |
| **D** | **Publish the corpus→ergonomic bridge as data** and let A, B and C all read it. | The missing hop (§9.1), and the three divergent hand-written copies of it. | A schema addition to a shipped file; C14 governs. Larger than ticket 69 as written. |

**A and B are not alternatives.** A removes the copy; B checks that whatever
remains still agrees with its source. Ticket 69 asks for both (items 1 and 3),
and item 2's question — what happens where the JSON is absent — is the only one
that genuinely has to be *decided* rather than implemented.

**One thing any option should carry.** The `KITCHEN_DINING` zone/room defect
(§5.1) is **not** fixed by reading the JSON — the JSON's number is 6.0 and a
faithful read still posts 6.0 on the whole room. It needs the `bridge` field to be
read by a human, and it is a `rules.json` question. An accessor that silences the
transcription risk while leaving that defect in place would make it **harder** to
find, not easier.

---

## 10. What could NOT be verified, and why

Stated plainly.

1. **That AzDTN 2.7-2 is in force today.** The SİYAHI could not be re-read
   (§1.3): the repo's `az_siyahi_2025.pdf` is an HTML error page and
   `az_siyahi_cand.pdf` is a different document. **Every figure in §2 inherits
   minima.md §1 and §4.4's authority on the in-force question, not mine.** What I
   can add: the issuing authority is serving this exact edition today, from its
   own register, byte-identical to the copy minima.md read — which is
   corroboration of currency, not proof of it.
2. **That no amendment (`dəyişiklik`) has touched cl. 5.7 since 2021.** A web
   search returned the committee's index and sibling norms only. The served PDF
   carries no amendment marks and its front matter still reads *İlk dəfə qəbul
   edilir* (adopted for the first time). Absence of evidence.
3. **The correct whole-room statutory floor for a `mətbəx-yemək otağı`.** The
   norm does not publish one (§5.1). This note establishes that 6.0 is **not**
   it; it does not establish what is.
4. **Whether `dining` counts as an otaq under Azerbaijani law.** The profile says
   yes at `conf: derived`, admitted through cl. 5.5's unqualified `otaq`. AzDTN
   never rules on it. §6's finding is a Python-versus-profile disagreement; the
   underlying legal question is open and is minima.md's, not resolved here.
5. **The 2002–05 Azerbaijani amendment acts to SNiP 2.08.01-89\*** — minima.md
   §11.4's open item, the likely origin of the 15 m² one-room living room. Not
   attempted; not needed for any figure here.
6. **Nothing about `market_default` against actual Baku practice.** minima.md
   §7.4's gap is unchanged: both `market_default` sources are regulator
   recommendations, one of them for a different building type. §7's zero-margin
   finding is measured against that weak tier, and would move if the tier moved.

---

## 11. What evidence would have caught a drift

Ticket 69 asked for this explicitly, and it is the finding that survives the six
values checking out.

**What did catch things, here:**

1. **Resolving the guard list programmatically instead of reading the cell.**
   That is what surfaced §4.3's two-kinds-of-null and confirmed the otaq guard
   resolves to the right cells at both otaq = 1 and otaq = 3. A test that reads
   `areas_m2.<key>.statutory_floor.v` — which is what the current assertion does
   — cannot see any of it.
2. **Reading the JSON's prose fields, not only its numbers.** The
   `KITCHEN_DINING` defect (§5.1) is stated twice, in plain English, in
   `mapping.rooms.kitchen_dining.bridge` and in
   `counts_as_otaq_sourcing…kitchen_dining.note`. **No automated check will ever
   read those.** They were written by the person who found the problem and filed
   it forward; the transcription copied the number past them.
3. **Diffing the Python's prose inventory against the data.** The "three / six /
   0.5-1.7" miscount (§8.3) is checkable arithmetic and it is wrong in three
   files. Prose in a comment is not tested anywhere, and it is what the next
   reader will believe.
4. **Cross-checking the corpus label set against the profile's flag set.** That
   is the whole of §6, and it took one `set` comparison plus a count over
   `dwelling_rooms.json`.
5. **Comparing the two tiers side by side rather than one at a time.** §7's
   zero-margin finding is invisible from either tier alone.

**What would NOT have caught a drift, and is the honest answer to ticket 69:**

- **The current assertion.** It would catch a changed number in one of six cells.
  Of the three defects in this note — a mis-referenced number, a wrong otaq
  predicate, a zero-margin tier coincidence — it catches **none**, because none
  of them is a changed number.
- **`gate_check.py`'s 238 gates.** All pass. They assert the profile's internal
  consistency (mapping totality, guard well-formedness, orphan cells, flag
  presence) and nothing about any consumer of it. *The profile matches its own
  source* and *a consumer matches the profile* are both unchecked, which is
  exactly ticket 69 item 3's diagnosis.

**So the finding ticket 69 needs is this:** the six values are right, and the
mechanism that would keep them right is aimed at the one failure mode that did
not occur. The transcription risk is real but it has not fired; what **has**
fired is **referent drift** — a number copied away from the qualifier that gives
it meaning, and a predicate copied away from the flag that defines it. A binding
that reads `statutory_floor.v` and stops there will close the risk that did not
materialise and leave both that did.

---

## 12. Handoffs

Recorded, not decided.

| # | to | what |
|---|---|---|
| 1 | **ticket 69** | A seventh hand copy exists — `absolute_area.HABITABLE` versus `ergonomic.rooms[*].counts_as_otaq` — and unlike the six it is **wrong**. It selects which living-room limb is posted. §6. |
| 2 | **ticket 69** | `az_area` null and `statutory_floor` null are **two different nulls** and the accessor must handle both; `mapping.null_means` is about the soft tier and does not license the reading the Python's comment attributes to it. §4.3. |
| 3 | **ticket 69 / `rules.json`'s holder** | `KITCHEN_DINING` 6.0 is the kitchen **zone**, not the room, and ADR 0033 has promoted it from a targeting question to a **geometry** one. Reading the JSON does not fix it. §5.1. |
| 4 | **ticket 69 item 4** | `project_join.ERG_AREA`'s ten values are **all correct**, spot-checked. `absolute_area.MARKET`'s six are **all correct**, verified against both the JSON and AzDTN 2.7-3 cl. 5.1. Neither is bound by anything. §8.3, §4.2. |
| 5 | **ticket 67** | The `LIVING` 2+-otaq limb has **zero** margin between soft target and hard floor in 65.1 % of the corpus, so ADR 0033 consequence 3's seed-shape estimate error is the whole safety factor there. §7. |
| 6 | **minima.md** | §1's extraction limitation is an artefact of the extractor: `pypdf` recovers all diacritics **and** the cover page's Cyrillic. The AzDTN quotations can be machine-verified rather than re-diacriticised by hand. §1.2. |
| 7 | **whoever owns `experiments/finish-layer/src/`** | `az_siyahi_2025.pdf` is a 1,893-byte **HTML error page**, not a PDF. The SİYAHI is not actually cached in this repo. §1.3. |
| 8 | **`gate_check.py`** | Three prose inventories in two Python files repeat a "three carry a floor, six do not" count that is **five and five**, and an ergonomic range that omits `dining` 1.9 m². Comment text is untested everywhere. §8.3. |
| 9 | **`room-constraints.json`'s holder** | Same class, inside the shipped file: the ergonomic key set has **19** members, and the file's own prose still says "eighteen" five times (`mapping.comment` ×1, `mapping.null_means` ×1, `tier_model` and others ×3) while six newer notes correctly call `bathroom_combined` "a nineteenth type". `gate_check.vocabulary_gates`'s docstring repeats "Ten of eighteen". V1 asserts the two **sets** are equal, so nothing catches a stale **count** in prose. Cosmetic today; it is the same referent-drift shape as §5.1 and §8.3. |
