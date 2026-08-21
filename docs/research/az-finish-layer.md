# What an Azerbaijani finish layer actually is

**Ticket:** *What an Azerbaijani finish layer actually is*
(`docs/wayfinder/tickets/35-what-an-azerbaijani-finish-layer-is.md`)
**Reads:** `profiles.AZ.construction.catalogue.brick.t_finish` — **read-only on the
profile.** This document proposes a cell; it does not write one.
**Evidence:** `experiments/finish-layer/` — three scripts, and the extracted
source text under `experiments/finish-layer/out/`.
**Date:** 2026-08-21.

C8 applies to every number below. **No legal code-compliance claim is made or
implied**, in Azerbaijan or anywhere else. Where a norm *tabulates* a quantity
rather than *requiring* it, this document says so in the same breath as the
number, because the difference is the whole of items 2 and 3.

---

## 0. Verdict, up front

1. **An Azerbaijani statutory instrument publishes 15 mm as the thickness of
   plaster over brick masonry, and it was read first-hand.** **AzDTN 2.12-4\***
   *Binaların istilik mühafizəsi*, **Əlavə 8\*, Cədvəl 1, rows 27 and 28** —
   *plastering with cement-sand mortar over stone or brick masonry* and *…with
   lime mortar…* — both carry **`Layın qalınlığı, mm` = 15**. The shipped value
   does not move. **Its provenance moves from `engine_choice` to `verified`.**
2. **Nothing downstream re-opens.** `t_int` stays 150, the ADR 0007 residue class
   stays 100 mod 250, `t_party` stays 280, and the acoustic derivation that
   assumed *"brick 250 + 15 plaster both sides"* now rests on a number the AZ
   corpus actually publishes rather than on an engine's guess. Asserted, not
   claimed: `experiments/finish-layer/consequences.py`.
3. **This is the *opposite* of the trap that caught *The Azerbaijani region
   profile*, and the distinction is legal, not rhetorical.** There, СНиП
   2.08.01-89\* had been **terminated** in Azerbaijan by AzDTN 2.7-2, so its
   numbers were superseded. Here, **AzDTN 2.12-4\* is the instrument that
   terminated СНиП II-3-79\*** (2022-06-10) **and it carries the row forward into
   its own text.** I am quoting the live Azerbaijani instrument, not the dead
   ancestor. §1.4 discloses the genealogy in full anyway.
4. **Item 2's hypothesis is REFUTED, and refuting it is the most valuable thing
   here.** Azerbaijan's finishing-works norm *does* grade plaster into three
   quality classes — **but the classes publish flatness tolerances, not
   thicknesses.** A reader who took the ladder for a thickness ladder would have
   shipped `t_finish` = **1, 2 or 3 mm**. That is precisely the failure mode item
   3 exists to name, it is live in the real document, and §2 shows it.
5. **There is a second, competing Azerbaijani number — 10 mm — and it loses on
   product, not on authority.** AzDTN 2.17-1 cl. 8.24 note 1 says the published
   brick-*panel* thicknesses **include** the outer and inner mortar layers; the
   series 8.5 / 14 / 27 cm against quarter- / half- / one-brick gives **exactly
   10 mm per face, three times over.** It is a *factory* mortar face on a
   prefabricated panel. The AZ profile ships **hand-laid masonry**, not panels.
   §4.
6. **Azerbaijan has issued no AzDTN for finishing works at all.** The applicable
   instrument is the **retained СНиП 3.04.01-87**, in force by Cabinet of
   Ministers Decision No. 217 of 15.04.1992 and listed in the republic's own
   register under *Qrup 04. Qoruyucu, izolyasiya və üzlük örtükləri*. That is a
   negative result and it is reported as one. §2.1.
7. **Both corpora are negative, and cleanly so.** Swiss Dwellings stores
   `separator` as exactly **WALL / RAILING / COLUMN** — 93 distinct
   `(entity_type, entity_subtype)` pairs over 3,255,905 rows and **not one names
   a finish, render, plaster or layer**. ResPlan carries **one scalar
   `wall_depth` per plan** (n = 17,000) and no material, no per-wall thickness and
   no layer decomposition. §5.

---

## 1. Item 1 — the normative thickness, read first-hand

### 1.1 The instrument and its standing

**`az_azdtn_2_12_4`** — *"Binaların istilik mühafizəsi. Layihələndirmə
normaları"* (Thermal protection of buildings. Design norms), **new redaction,
Baku 2025, 64 pp.** Downloaded from `arxkom.gov.az` on a plain unauthenticated
GET and read first-hand. Its own front matter, transcribed:

- Approved by **Collegium decision MİHO/2.1-3.2-2022-4 of 10 June 2022**;
- **Qüvvəyə minib: 2022-ci il 10 iyun tarixdən** (in force from 2022-06-10);
- **State Register of Legal Acts no. 15202206100224**;
- *"Bu texniki normativ hüquqi akt qüvvəyə mindiyi tarixdən **СНиП II-3-79\***
  «Строительная теплотехника» normativ sənədin Azərbaycan Respublikası ərazisində
  hüquqi qüvvəsi **dayandırılır**."* — from the date this act enters into force,
  the legal force of СНиП II-3-79\* **on the territory of the Republic of
  Azerbaijan is suspended**;
- amended by **Collegium Decision 3-35/3-2-4/2025 of 05.06.2025**, and
  *"dəyişikliklər və əlavələr edilmiş müddəalar (cədvəllər) «\*» işarəsi ilə
  verilmişdir"* — **amended provisions (tables) are marked with an asterisk**.

This is already the profile's source for the thermal `R_req` line, and it is
already in `sources` as `az_azdtn_2_12_4`. **No new source key is needed.**

Note the asterisk on **Əlavə 8\***. By the document's own convention that marks
the appendix as one of the provisions carried through the **June 2025 amendment**
— so the table was passed over by the amending body, not merely inherited
unexamined. It does not tell us which rows changed, and §1.4 shows at least two
values elsewhere in the same table *were* revised against the ancestor.

### 1.2 The table

**Əlavə 8\* — *"Konstruksiya laylarının havanüfuzetmə müqaviməti"*** (Air-permeation
resistance of construction layers), **Cədvəl 1**. Columns, transcribed from the
header:

| `Konstruksiya və materiallar` | `Layın qalınlığı, mm` | `Havanüfuzetmə müqaviməti R, (m²·st·Pa)/kq` |
|---|---|---|

The three plaster rows, transcribed verbatim:

| # | Azerbaijani | English | `Layın qalınlığı, mm` | `R` |
|---|---|---|---|---|
| 27 | *Daş və ya kərpic hörgü üzrə **sement-qum məhlulu** ilə suvaqlanma* | plastering with **cement-sand mortar** over stone or brick masonry | **15** | 373 |
| 28 | *Daş və ya kərpic hörgü üzrə **əhəng məhlulu** ilə suvaqlanma* | plastering with **lime mortar** over stone or brick masonry | **15** | 142 |
| 29 | *Taxta üzrə əhəng-gips məhlulu ilə suvaqlanma* | plastering with lime-gypsum mortar over **timber** | 20 | 17 |

These are the **only** three plaster rows in the document. `suva*` matches at
exactly three points in the extracted text of all 67 pages, plus one unrelated
hit (`Fasad suvağı` in the solar-absorptivity appendix, which gives colours and
no thickness).

### 1.3 Why the column assignment is trustworthy

`pdftotext -layout` **scrambled the top of this table** — rows 3 to 20 come out
with their numbers desynchronised from their labels, because multi-line row
captions break the column reconstruction. Reading 15 mm out of that extraction
would have been exactly the kind of evidence this ticket exists to refuse.

So the column assignment was verified from **glyph coordinates**, not from the
text dump — `experiments/finish-layer/verify_appendix8_columns.py`, which walks
pypdf's text-showing operators and reports each token's x position on PDF page 66.

The thickness column is anchored by its neighbours:

```
23. Ruberoid                     [1,5]@x=339      [Havakeçirməzdir]@x=448
24. Tol                          [1,5]@x=339      [490]@x=482
25. Yapışdırılmış faner          [3]@x=339 [-] [4]@x=349   [2900]@x=479
26. Bütöv şlak-beton (tikişsiz)  [100]@x=337      [14]@x=486
27. Daş və ya kərpic hörgü üzrə   [15]@x=341      [373]@x=482   <==
28. Daş və ya kərpic hörgü üzrə   [15]@x=341      [142]@x=482   <==
29. Taxta üzrə əhəng-gips məhlulu [20]@x=341      [17]@x=486
30. Sıxlığı 1000 kq/m3 …    [250]@x=325 [-] [400]@x=349  [53]@x=477 [-] [80]@x=494
```

and by the header itself: `Layın qalınlığı, mm` @x=297, `Havanüfuzetmə
müqaviməti` @x=419. **x = 341 is inside the thickness column and nowhere near the
resistance column.** The reading is not an artefact.

### 1.4 The genealogy, disclosed

The table descends from **СНиП II-3-79\*, ПРИЛОЖЕНИЕ 9\*** *"Сопротивление
воздухопроницанию материалов и конструкций"*, which was read first-hand for this
check. Its rows 30–32:

> 30. Штукатурка цементно-песчаным раствором по каменной или кирпичной кладке — **15** — 373
> 31. Штукатурка известковая по каменной или кирпичной кладке — **15** — 142
> 32. Штукатурка известково-гипсовая по дереву (по драни) — **20** — 17

**Identical thicknesses and identical resistances.** AzDTN 2.12-4\*'s Əlavə 8\* is
that table carried forward, renumbered three places earlier.

It is **not a photocopy**: comparing the two tables row by row, at least two
values were re-edited in the Azerbaijani redaction — row 1 *Бетон сплошной* /
*Bütöv beton* goes **19 620 → 20 000**, and *Фанера клееная* / *Yapışdırılmış
faner* goes **2940 → 2900**. The plaster rows were carried unchanged.

**This disclosure does not weaken the label, and here is precisely why.** The
ticket's standing instruction is that a number from a Russian instrument may not
be transferred into the AZ profile *as if sourced*. That is not what is happening.
The 15 mm is being read **out of the Azerbaijani instrument's own text**, in an
instrument that is **in force**, that **suspended** the Russian ancestor rather
than being suspended by it, and that a Azerbaijani collegium amended in June 2025.
The ancestor's matching row is **genealogy, not authority**, and it is reported
here so that nobody mistakes the value for an independent Azerbaijani measurement.

**What must not be said, and is not said anywhere in this document:** that
Azerbaijan *requires* 15 mm of plaster. Əlavə 8\* is a **characteristics table** —
it states an air-permeation resistance *at* a stated layer thickness. The norm's
own choice of 15 mm as the representative plaster-on-masonry layer is strong,
first-hand, statutory evidence of what a plaster layer over brick **is** in
Azerbaijani practice. It is not a prescription, and the proposed cell's `note`
says so.

---

## 2. Item 2 — one number, or a class ladder?

### 2.1 Azerbaijan has issued no finishing-works norm. The negative result, stated.

The republic's own register of construction normative documents —
*"I. Tikinti üzrə normativ, metodiki və rəhbəredici sənədlər"* — carries a group
for exactly this subject:

> **Qrup 04. Qoruyucu, izolyasiya və üzlük örtükləri**
> (Group 04. Protective, insulating and facing coverings)
>
> **СНиП 3.04.01-87** — *Изоляционные и отделочные покрытия*
> **СНиП 3.04.03-85** — *Защита строительных конструкций и сооружений от коррозии*

**Two entries, both СНиП, no AzDTN, and no replacement note against either.**

That is the whole of the group. It was cross-checked against the live site:
`arxkom.gov.az`'s seven normative categories were enumerated and each relevant
one opened. **No document about finishing works, plastering, `üzləmə`, `suvaq` or
`bəzək işləri` appears anywhere on the site**, in *İnşaat konstruksiyaları*, in
*Rəhbəredici və metodiki sənədlər*, or in the buildings category.

The legal mechanism that keeps СНиП 3.04.01-87 alive is the same one *The
Azerbaijani region profile* established, and the register lists it in its own
Group 01:

> *"İnşaatda Tikinti norma və qaydalarının, dövlət standartlarının tətbiq
> edilməsi barədə Azərbaycan Respublikası **Nazirlər Kabinetinin 15.04.1992-ci il
> tarixli, 217 №-li Qərarı**"*

and **AzDTN 1.1-1**'s concept document §2.2(a), read first-hand, states the rule
in its own words: the former all-union documents (ГОСТ, СНиП, СН, ВСН, ВНТП…)
currently in force on the territory of the Republic **are considered temporary for
the transition period, with gradual revision and replacement envisaged**, and
§2.2(b) the AzDTN that will replace them **in stages**.

**So the two cases are structurally different, and the difference is the whole
ticket-25 lesson:**

| | ticket 25's trap | this ticket |
|---|---|---|
| ancestor | СНиП 2.08.01-89\* | СНиП 3.04.01-87 / СНиП II-3-79\* |
| did an AzDTN replace it? | **yes** — AzDTN 2.7-2, 2021-11-30 | **3.04.01-87: no.** II-3-79\*: yes, by 2.12-4\* — **and 2.12-4\* is what we quote** |
| status of the ancestor's numbers in AZ | **superseded** — publishing them is a C8 breach | **retained in force** by CoM 217/1992 |

**Reading СНиП 3.04.01-87 for Azerbaijan is therefore legitimate**, and it is
read below for **shape** regardless — because what it turns out to say makes the
shape question answerable without leaning on the numbers at all.

### 2.2 There are three classes, and they are NOT thicknesses

**СНиП 3.04.01-87, Table 9** (cl. 3.14), read first-hand. Its column heading is
**`Предельные отклонения`** — *limiting deviations*. Every row is a tolerance:

| quantity | простая | улучшенная | высококачественная |
|---|---|---|---|
| deviation from vertical, mm per 1 m | **3** | **2** | **1** |
| …and over the full room height | ≤ 15 mm | ≤ 10 mm | ≤ 5 mm |
| surface irregularities per 4 m² | ≤3, up to 5 mm deep | ≤2, up to 3 mm | ≤2, up to 2 mm |
| deviation from horizontal, mm per 1 m | 3 | 2 | 1 |
| reveals / pilasters / corners, mm per 1 m | 4 | 2 | 1 |
| curved-surface radius, whole element | 10 | 7 | 5 |
| reveal width vs design | 5 | 3 | 2 |

**There is no thickness anywhere in Table 9.** Choosing *улучшенная штукатурка*
buys you 2 mm per metre of flatness. It does not buy you a millimetre of build-up.

**So item 2's hypothesis is refuted.** `t_finish` is **not** a choice among
published class values, because the classes do not publish thicknesses. The
profile cannot say "we ship improved plaster, hence *n* mm" — that sentence does
not correspond to anything in the document. What the profile *can* say is which
class it assumes for **tolerance** purposes, and that is a drawing/specification
question, not a geometry one; at 1–3 mm per metre it is below the model's
integer-millimetre resolution over any room dimension v1 emits, and it changes no
number in the layer set.

### 2.3 What the norm *does* publish about thickness — and it is a ceiling, not a value

**СНиП 3.04.01-87, Table 10** (cl. 3.21), read first-hand:

> **Допускаемая толщина однослойной штукатурки, мм:** при применении всех видов
> растворов, кроме гипсового — **до 20**, из гипсовых растворов — **до 15**
>
> **Допускаемая толщина каждого слоя при устройстве многослойных штукатурок без
> полимерных добавок, мм:**
> обрызга по каменным, кирпичным, бетонным поверхностям — **до 5**;
> обрызга по деревянным поверхностям (включая толщину драни) — до 9;
> грунта из цементных растворов — **до 5**;
> грунта из известковых, известково-гипсовых растворов — **до 7**;
> накрывочного слоя штукатурного покрытия — **до 2**;
> накрывочного слоя декоративной отделки — до 7

Every one of these is a **maximum** (`до` — "up to"), and the multi-layer figures
are **per coat**, not a cap on the total: cl. 3.18 requires each coat to be
applied after the previous one has set, and places no limit on how many `грунт`
coats there are. So Table 10 **bounds** a plaster build-up without **specifying**
one.

**15 mm sits comfortably inside that envelope, two ways:**

- as a **single-layer** cement-sand application it is within the ≤ 20 mm cap for
  all non-gypsum mortars — which is exactly what AzDTN 2.12-4\* row 27
  (*sement-qum məhlulu*) describes;
- as a **multi-coat** build-up: обрызг 5 + грунт 5 + грунт 3 + накрывка 2 = 15.

Two independent instruments, one retained and one in force, agree that 15 mm of
cement-sand plaster over brick is an ordinary thing. Neither *requires* it.

One further clause worth recording, because it is the only place the norm ties
thickness to a physical control: **cl. 3.16** — *improved and high-quality plaster
shall be executed to beads (маяки) whose thickness equals the thickness of the
plaster coating without the finishing coat.* The norm makes the bead **set** the
thickness and declines to say what the bead is. The thickness is a **project
decision** the norm bounds, which is exactly why no finishing-works norm on
either side of the border will ever hand us a design value.

---

## 3. Item 3 — thickness or tolerance? Both exist, and the trap is real

The ticket asked whether the published quantity is a build-up depth or a
deviation-from-plane tolerance. **The answer is that the finishing-works norm
publishes both, in adjacent tables, and they are twelve pages apart in meaning:**

| | Table 9 (cl. 3.14) | Table 10 (cl. 3.21) |
|---|---|---|
| quantity | **deviation from plane / vertical** | **layer thickness** |
| graded by quality class? | **yes** — 3 / 2 / 1 | **no** |
| kind of bound | limiting deviation | maximum |
| magnitude | 1–15 mm | 2–20 mm |
| **is it `t_finish`?** | **no, and it is the trap** | **a ceiling on it, not it** |

The magnitudes **overlap**, which is what makes the confusion survivable long
enough to ship. *"Улучшенная штукатурка — 2"* and *"накрывочного слоя — до 2"* are
both "2 mm" in a table about plaster, and one is a flatness tolerance while the
other is a coat depth. A profile that took the class ladder for a thickness ladder
would have shipped `t_finish` = 1, 2 or 3 mm, produced `t_int` = 122 / 124 / 126,
moved the ADR 0007 residue class to 128 / 126 / 124 mod 250, and been *internally
consistent the whole way down*. Nothing in the arithmetic would have caught it.

**Neither table is the source of the shipped number.** The source is a third
quantity in a fourth document — a layer thickness stated in a materials-and-layers
characteristics table in the thermal norm. That is the one place in the corpus
where an Azerbaijani instrument names a plaster thickness for brickwork instead of
bounding it.

---

## 4. The second Azerbaijani number — 10 mm — and why it does not win

**AzDTN 2.17-1 cl. 8.24**, read first-hand, in full:

> *"8.24. Daxili divarların və arakəsmələrin kərpic panellərini birqatlı —
> dörddəbir kərpic (**8,5 sm**), yarımkərpic (**14 sm**) və kərpic (**27 sm**)
> qalınlıqda, ikiqatlı — iki qatdan ibarət hər birinin qalınlığı dörddəbir kərpic
> (ümumi qalınlıq **18 sm**) layihələndirmək lazımdır."*
>
> *"**Qeyd: 1.** Panellərin qalınlığı **xarici və daxili məhlul qatı nəzərə
> alınmaqla** göstərilmişdir."* — the panel thicknesses are given **taking account
> of the outer and inner mortar layer**.
>
> *"2. Qalınlığı dörddəbir kərpic olan panelləri yalnız arakəsmələr üçün
> layihələndirmək lazımdır."*

Note 1 makes the arithmetic available, and it closes **three times with the same
value**:

| panel | brick core | published total | implied per face |
|---|---|---|---|
| quarter-brick (*dörddəbir kərpic*) | 65 | **85** | **10** |
| half-brick (*yarımkərpic*) | 120 | **140** | **10** |
| one brick (*kərpic*) | 250 | **270** | **10** |

A three-point exact fit on one constant is about as strong as a derivation gets,
and it is Azerbaijani, statutory and current. **It is nonetheless the wrong number
for this profile, for a reason of product rather than provenance:**

- cl. 8.24 governs **factory-made brick panels**. The `məhlul qatı` is a **mortar
  face cast in a mould against a flat pallet** — it takes up a manufacturing
  tolerance measured in a millimetre or two.
- AzDTN 2.12-4\* row 27 governs **suvaqlanma — plastering — over `hörgü`, laid
  masonry**. It has to absorb the dimensional deviation of brick laid by hand on
  10 mm mortar joints, which is what Table 9's 1–3 mm-per-metre flatness classes
  are grading in the first place.

**Thicker plaster over hand-laid work than over a moulded face is the physically
expected direction**, and the two documents disagree by exactly that. They are not
in conflict; they describe two products.

**The AZ profile ships hand-laid masonry.** `t_int_structural = 120` is sourced to
AzDTN 2.17-1 **cl. 4.3 / Table 29 note 2** — the bare half-brick partition — and
the shipped `shipping_type` is `brick`, not a panel type. `thickness.md` §3.1
already records the panel series as construction type **B1**, separately, and §8
recommends against shipping it (85 mm is odd). **10 mm is the correct
`t_finish` for a construction type this profile does not ship**, and it should be
recorded against B1 if B1 ever ships. It is not the value for `brick`.

---

## 5. Item 4 — what the corpora say. Nothing, twice, and cleanly.

`experiments/finish-layer/probe_corpus_layers.py` and `probe_resplan_layers.py`.

### 5.1 Swiss Dwellings v3.0.0 — negative

Streamed all of `geometries.csv`: **3,255,905 rows, 93 distinct
`(entity_type, entity_subtype)` pairs.** The complete `separator` taxonomy is:

| entity_type | entity_subtype | rows |
|---|---|---|
| separator | **WALL** | 1,519,546 |
| separator | **RAILING** | 158,398 |
| separator | **COLUMN** | 22,869 |

**Three subtypes. That is all of them.** No `FINISH`, no `RENDER`, no `PLASTER`,
no `LAYER`, no `CORE`, no `SKIN` — not in `separator` and not anywhere in the
other 90 pairs, which are `opening` (DOOR / WINDOW / ENTRANCE_DOOR), `feature`
(fixtures) and `area` (room programme). **A wall is one polygon with one
`height`.** A finish layer is not merely unrecorded; the schema has no place to
put one.

### 5.2 ResPlan — negative

Loaded `ResPlan.pkl` (17,000 records). A record's geometry keys are `wall`,
`inner`, `door`, `window`, `front_door`, `land`, `balcony` and the room
programme; the only thickness field in the entire record is:

- **`wall_depth`** — one `float` per **plan**: n = 17,000, min 2.220, max 7.175,
  mean 4.187, median 4.137, 3,153 distinct values.

**One scalar for the whole dwelling.** No per-wall thickness, no material, no
layer decomposition, no finish entity. ResPlan cannot distinguish a structural
leaf from a finish even in principle.

*(Adjacent, and worth one line for whoever picks up the area work: ResPlan does
carry both `area` and `net_area` — 120.77 vs 95.66 on the sampled record — so it
has a gross/net distinction. That is a **measurement-plane** distinction, not a
layer one, and it is not evidence about finishes.)*

### 5.3 What the negative is worth

It is worth exactly what *Which region profiles ship in v1* got from the same kind
of answer. **No corpus on this map can ever corroborate or refute a finish
thickness**, so the question is closed against the corpora permanently rather than
left open as a thing someone might check later with better tooling. It also
confirms, independently, ADR 0010's premise: every published floor-plan dataset in
this project's reach measures to a single undifferentiated wall, which is why
"finished" has been a word rather than a number in this system until now.

---

## 6. What moves if the number is not 15 — nothing, because it is 15

`experiments/finish-layer/consequences.py`, run:

```
 t_finish  t_int  t_party  residue  t_int even  t_party even
        8    136      266      114        True          True
       10    140      270      110        True          True
       12    144      274      106        True          True
       15    150      280      100        True          True  <== shipped / proposed
       18    156      286       94        True          True
       20    160      290       90        True          True
       25    170      300       80        True          True
```

The three named consequences, each checked rather than asserted:

1. **`t_int` = 120 + 2 × 15 = 150.** Unchanged. Reproduces ADR 0010's shipped
   value. *(At 10 it would be 140; at 20, 160 — matching the ticket's own
   arithmetic.)*
2. **ADR 0007 residue class = −150 mod 250 = 100.** Unchanged. Reproduces ADR
   0010 consequence 1 exactly. *(10 → 110, 20 → 90 — again matching the ticket.)*
   Moot for `AZ` either way, which publishes no hard linear minimum, but owed
   before a second profile does.
3. **ADR 0004's even-thickness gate stays unbound on this layer, as ADR 0010
   consequence 2 sharpened it.** `120 + 2·t_finish` is even for **every** integer
   `t_finish` — verified over 1..59 in the script. A 15 mm finish is legal; a
   15 mm wall is not. **The ticket's instruction not to rule out an odd answer was
   correct, and the answer is odd.**
4. **`t_party`'s acoustic derivation holds, and is strictly better than it was.**
   `t_party` = 250 + 2 × 15 = **280**, and the derivation behind the 250 mm leaf —
   *"brick 250 + 15 plaster both sides = 52 dB"* passing AzDTN 2.7-2 §9.22's
   50 dB, against *"brick 120 + 15 both sides = 49 dB"* failing — assumed a 15 mm
   plaster that **now has an Azerbaijani source behind it.** Before this ticket the
   derivation rested on an `engine_choice`; it now rests on `az_azdtn_2_12_4`. **No
   part of `t_party` re-opens.**

**The ticket's stated worry — that changing `t_finish` re-opens `t_party` — does
not materialise.** The self-consistency it flagged as "not a source" turns out to
have been pointing at the right number the whole time; what was missing was the
document, and the document exists.

---

## 7. The cell this proposes

**Not written.** The ticket declares itself read-only on the profile and that is
honoured literally. This is the exact cell for
`profiles.AZ.construction.catalogue.brick.t_finish`, for whoever owns the merge:

```json
"t_finish": {
  "v": 15,
  "src": "az_azdtn_2_12_4",
  "ref": "App. 8*, Table 1, row 27",
  "conf": "verified",
  "note": "Cement-sand plaster (sement-qum mehlulu) over stone or brick masonry. Read first-hand from Elave 8* Cedvel 1, column 'Layin qalinligi, mm'; row 28 gives the same 15 mm for lime mortar. WAS engine_choice and is no longer. SCOPE, and it matters: App. 8* is a CHARACTERISTICS table -- it states an air-permeation resistance AT a stated layer thickness. The norm does not REQUIRE 15 mm and no code-compliance claim is made (C8). The retained finishing-works norm SNiP 3.04.01-87 Table 10 bounds rather than specifies: single-layer non-gypsum up to 20, and its quality classes (Table 9) are FLATNESS TOLERANCES of 1-3 mm/m, NOT thicknesses -- reading that ladder as thickness is the documented trap. AzDTN 2.17-1 cl. 8.24 n.1 implies 10 mm per face, but for FACTORY BRICK PANELS (construction type B1), not laid masonry; see docs/research/az-finish-layer.md section 4. Value unchanged, so t_int stays 150, residue stays 100 mod 250, and t_party's 52 dB derivation is unaffected."
}
```

**`src` needs no new source-register key** — `az_azdtn_2_12_4` is already in
`sources` and is already cited by `t_ext_total`.

### 7.1 One correction owed elsewhere in the register, not made here

`sources.az_azdtn_2_12_4.force_note` currently ends:

> *"It supplies **no wall thickness**, so any external-wall total derived from it
> is an engine choice."*

That was true of the thermal tables and is **now incomplete**: the same instrument
supplies a **finish-layer** thickness in Əlavə 8\*. The external-wall clause is
still correct — Əlavə 8\* gives no structural or insulation thickness, so
`t_ext_total` remains an `engine_choice` and remains blocked on Baku's `Dd`.
Suggested repair, for the owner of that file: *"It supplies no **structural**
thickness … but see App. 8\* Table 1 rows 27–28 for the plaster layer."*

### 7.2 Out of scope, and flagged rather than fixed

`t_ext_total` = 500 spends **20 mm** on external finish. **Əlavə 8\* does not
support that number** — its only 20 mm row is row 29, *lime-gypsum plaster over
**timber***, which is not an external render on brick. The document's external
plaster reference (`Fasad suvağı`) appears only in the solar-absorptivity appendix
and gives colours, not thicknesses. **The 20 mm external finish remains an
`engine_choice` and this ticket does not close it.** It was not in the ticket's
four items and is recorded here only so the next reader does not assume §1 settled
it.

---

## 8. What I could not obtain, and why

1. **The 2026 SİYAHI register, first-hand.** *The Azerbaijani region profile* read
   the official register at 01.01.2026 (DŞAK-K № 0009-2026). I could not re-locate
   that PDF on `arxkom.gov.az` in this session — the two candidate `storage/media`
   URLs surfaced by search resolved to an unrelated Cabinet decision and to a
   404-equivalent. **The register I read first-hand is the Azerbaijani
   State Committee's list published via `sukanal.az` (10,867 lines extracted),
   which carries no internal date and sits under a 2016 upload path.** So §2.1's
   claim — *no AzDTN for finishing works; СНиП 3.04.01-87 retained in Group 04* —
   is **verified against that register and corroborated against the live
   `arxkom.gov.az` category listings** (which show no finishing-works document
   today), but **not confirmed against the 01.01.2026 edition.** Treat the
   *absence of an AzDTN on finishing works* as strongly evidenced, not as
   certified current. **This does not touch §1**, whose instrument was downloaded
   from `arxkom.gov.az` today and carries its own in-force date.
2. **ГОСТ 28013-98** *Растворы строительные. Общие технические условия* — in force
   in Azerbaijan by a dated domestic act (Committee order No. 173 of 31.10.2003
   and Standardization Agency order No. 130 of 14.11.2003, in force from
   01.03.2004, replacing ГОСТ 28013-89; confirmed in the register). **The full
   text was not retrieved** — the meganorm URL tried returned a 404 page. Expected
   value is low: it governs mix properties (mobility, water retention), not layer
   geometry. **Not chased further**, and named here so the gap is visible rather
   than silent.
3. **ГОСТ 31377** (the ticket named it as a shape-source) **was not read.** Once
   Əlavə 8\* produced a first-hand Azerbaijani thickness and СНиП 3.04.01-87
   answered the shape question, a further Russian instrument could only have added
   numbers this ticket is forbidden to transfer.
4. **No page image.** No rasteriser (`pdftoppm`) is available in this environment,
   so §1.2 could not be confirmed against a rendered page. **The glyph-coordinate
   check in §1.3 is the substitute**, and it is stronger evidence than a screenshot
   would have been, because it is reproducible by running the script.
5. **Baku's heating degree-days `Dd`** — still not obtained, still blocking
   `t_ext_total`. Unchanged from `thickness.md` §2.4; not this ticket's item.

---

## 9. Sources actually read first-hand for this document

| key | document | what it settled here |
|---|---|---|
| `az_azdtn_2_12_4` | **AzDTN 2.12-4\*** *Binaların istilik mühafizəsi*, Baku 2025 (in force 2022-06-10, reg. 15202206100224) | **Əlavə 8\*, Cədvəl 1, rows 27–28 — `t_finish` = 15 mm.** Front matter: suspends СНиП II-3-79\* in AZ |
| `az_azdtn_2_17_1` | **AzDTN 2.17-1** *Daş və armaturlanmış daş konstruksiyalar*, Baku 2016 | **cl. 8.24 + note 1** — the panel series and the "includes the mortar layers" note ⇒ 10 mm/face for type B1. cl. 8.60's 3 cm cement plaster is **anchor protection**, not a wall finish |
| — | **СНиП 3.04.01-87** *Изоляционные и отделочные покрытия* (retained in AZ, register Group 04) | **Table 9** — the class ladder is **tolerances**. **Table 10** — thickness **maxima**. **cl. 3.16, 3.18** |
| — | **СНиП II-3-79\*** *Строительная теплотехника*, **Прил. 9\*** | the genealogy of Əlavə 8\*, rows 30–32 |
| — | **Azerbaijani register** *"Tikinti üzrə normativ, metodiki və rəhbəredici sənədlər"* | **Qrup 04 holds no AzDTN.** CoM Decision 217 of 15.04.1992 listed in Qrup 01. ГОСТ 28013-98 in force from 01.03.2004 |
| — | **AzDTN 1.1-1** concept document (Baku 1994) §2.2 | the retention-and-staged-replacement rule, in the system's own words |
| — | **AzDTN 2.7-2**, **AzDTN 2.7-3** | **negative** — zero occurrences of `suva*` in either. Neither residential design norm mentions plaster at all |
| — | `arxkom.gov.az` category listings (7 categories) | **negative** — no finishing-works document on the site |

Local extractions of all of the above are under `experiments/finish-layer/out/`;
the PDFs and one HTML are under `experiments/finish-layer/src/`. **Both are
gitignored and neither is redistributed** — they are free official publications
without an open licence, retained only as working copies for this check. The URLs
in this table and in the `sources` register re-fetch them; `arxkom.gov.az` serves
the AzDTN PDFs on a plain unauthenticated GET, as it did for *The Azerbaijani
region profile*.
