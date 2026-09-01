# Room proportion in published standards — is 2:1 Azerbaijani, or is it everybody's? (September 2026)

**Question.** `dim.aspect_ratio_hard` ships at **3,0** with a note asserting *"No
surveyed source states an aspect rule."* AzDTN 2.7-3 cl. 5.1 falsifies that
sentence. This note establishes whether the ~2:1 figure the Azerbaijani norm
states is **region-specific** (→ a field on the region profile) or
**region-invariant design-grade** (→ an entry in the region-free ergonomic layer,
beside the body-derived clear widths).

**Raised by** [ticket 72](../wayfinder/tickets/72-a-regulator-states-an-aspect-rule-and-the-engine-says-none-does.md).

⚠️ **Companion note, read them together.**
[`room-proportion-constraints.md`](room-proportion-constraints.md) answers the
same ticket from the **generation-systems** side — who bounds aspect in shipped
products, learned generators, graph-theoretic RFP and VLSI floorplanning. This
note answers it from the **published-standards** side. They agree on the
conclusion and each corrects one claim of the other; the reconciliation is §8.5.

**Method.** Primary sources, read first-hand wherever the document could be
obtained. Russian and Soviet norms were pulled as raw HTML/PDF and grepped
**whitespace-insensitively** (the PDF extractors inject spaces mid-word, so a
naive `grep` produces false negatives — every negative below was re-run against a
whitespace-stripped copy — though §2.5a shows that is **not sufficient** when the
source itself is abridged). Four parallel sub-agents covered the handbook,
Western-norm, post-Soviet and design-theory arms; their output is labelled
`reported` unless re-read, and §10 records which were spot-checked. Anything not established from a primary
document is labelled `reported` or marked **NOT ESTABLISHED**, never guessed.

⚠⚠ **READ §10 BEFORE RELYING ON ANY ROW OF THIS NOTE.** This research hit two
distinct failure modes and both are recorded there: **a sub-agent fabricated
cited findings for six countries** (retracted; §7), and **an abridged primary
source produced a confident false negative of my own** (corrected; §2.5a). §10
also records the spot-checks that show the handbook and design-theory arms are
sound. Nothing in this note rests on retracted material.

⚠️ **Budget note, because it bounds the negatives.** The session exhausted its
web-search allowance (200/200), which prevented the fabricated country arm from
being redone. **Spain, Ireland, the Netherlands, France, Italy, Switzerland and
Ukraine are therefore UNRESEARCHED** — §7.4, and Spain is the highest-value gap.
The conclusion does not rest on them: it rests on the Soviet lineage (verified),
the modern Russian and Azerbaijani texts (verified), **Portugal** (verified),
**Belarus** (reported, structurally corroborated), both handbooks (verified),
NDSS and the German MBO (verified) and Palladio (verified).

> **C8 applies to every number here: Neufert-*grade* dimensional data. No legal
> code-compliance claim is made or implied, in Azerbaijan or anywhere else.**
> Several numbers below are quoted *from* building regulations. That is a
> statement about where a number came from, not a claim that a plan carrying it
> complies with anything.

---

## 1. TL;DR — the answer, and it is not the one the ticket expected

> ⭐⭐ **The headline.** The ~2:1 figure is **not Azerbaijani** — but it is also
> **two different rules wearing one number**, and only one of them is the
> quantity the engine computes.
>
> **Rule A, daylight depth.** Soviet, mandatory, and older than the ticket
> assumes: SNiP II-L.1-**62** cl. 1.19 (1962) and SNiP II-L.1-**71**\* cl. 3.4
> bind a habitable room's **depth** at ≤ **6 m** *and* ≤ 2× width — the 1971
> edition adding *«при одностороннем освещении»*, **single-sided lighting only**.
> Neufert's **office** chapter reaches the same **6000 mm** by the same daylight
> argument and quotes **1:1,5** because it divides by a wider room; the
> BRE/BS 8206-2 criterion reaches ~1:1,35–1:1,65 the same way; Neufert's
> single-sided **classrooms** cap depth at 7,20 m. **The ratio is a metre figure
> divided by an assumed width** — which is why the traditions agree on the physics
> and disagree on the number. This rule is **directional** and does **not** match
> `dim.aspect_ratio_*`. ⚠️ Note that **Neufert states no habitable-room ratio at
> all** (§6.1) — its 1:1,5 is for offices, and the Metric Handbook's is for
> broadcast studios (§6.2).
>
> **Rule B, design proportion.** ⭐ **Palladio, *Four Books* I.XXI: *"In the
> length of halls I use not to exceed two squares … the nearer they come to a
> square, the more commendable."*** That IS orientation-free length:breadth — the
> engine's exact predicate — and it has precisely the engine's two-term shape: a
> soft monotone preference toward square plus a hard ceiling near 2. Ching's
> standard teaching text propagates it. So `dim.aspect_ratio_*` **does** have
> design-grade backing; the engine simply never knew it, and ships **looser** than
> it (3,0 hard, 2,2 soft against Palladio's 2).
>
> **Live elsewhere, and mandatory.** ⭐ **Portugal RGEU art. 69.1 d)** states
> **length ≤ 2× width** as *mandatory* national law — and **waives it where both
> far opposite walls have openings**, i.e. for dual-aspect rooms. **Belarus ТКП
> 45-3.02-230-2010 cl. 5.5** carries the Soviet rule fully mandatory, in the
> faithful ***depth*** form, for single-family houses — AzDTN 2.7-3's exact scope.
> Between them, Portugal's exemption and the USSR's restriction settle that this
> is a **single-aspect daylight rule** (§6.4).
>
> **Consequence for ticket 72:** the profile gets **no aspect field** — no region
> owns this number. The false note must be struck (**two copies**, §5). Neither
> canonical handbook states a habitable-room ratio (§6); the "1:1.2–1:1.5
> preferred band" has **no primary source** and is teaching folklore (§8.4); and
> the golden-ratio justification is **refuted** (§8.3).

1. **The rule is real, it is old, and it is not Azerbaijani.** The 2:1 figure is
   **Soviet**, stated *mandatorily* in **SNiP II-L.1-62 cl. 1.19** (1962) and
   again in **SNiP II-L.1-71\* cl. 3.4** (1971). AzDTN 2.7-3 did not invent it;
   it **retained** it, six decades later and demoted to a recommendation. So the
   answer to *"is it idiosyncratically Azerbaijani?"* is **no** — and it is not
   even historical: it is **live and fully mandatory in Belarus**, and an
   unrelated **mandatory Portuguese** rule states the same 2:1.

2. **The NORM's rule is a DAYLIGHT rule, not an aesthetic one, and that changes
   what it may be used for.** SNiP II-L.1-71\* cl. 3.4 binds the room's **depth**
   *«при одностороннем освещении»* — **with one-sided lighting** — and pairs the
   2× with an absolute **6 m** cap. It sits three clauses from the
   window-to-floor ratio rule (cl. 3.13) in the same daylight family. The 1962
   edition stated it unconditionally and **the 1971 revision added the
   single-aspect condition** (§2.1a) — the authors narrowing their own rule to
   the case where daylight binds is the clearest evidence of what it is for. A
   *separate* aesthetic tradition also lands on 2 (Palladio, §8.1); the two are
   different predicates and must not be conflated.

3. **The engine's predicate and the norm's predicate are NOT the same
   quantity.** The engine measures **longer : shorter**, orientation-free. The
   norm measures **depth : width**, where depth is the dimension *normal to the
   glazed wall*. A room 6,0 m along its window and 3,0 m deep is **2:1 by the
   engine's measure and perfectly compliant under SNiP** — it is a shallow,
   well-lit room. Adopting "2:1" into an orientation-free rule would reject
   exactly the rooms the norm was written to encourage. ⚠️ **This is the finding
   that most constrains what ticket 72 may do.**

4. **Russia dropped it, and the drop is datable.** SNiP 2.08.01-89 no longer
   contains it (read first-hand: zero hits for `глубинажилых`, `двойнойширины`).
   Neither does SP 55.13330.2016, nor SP 31-107-2004. The modern Russian line
   answers the shape question with **furniture fit**, not ratio — SP 31-107-2004
   cl. 6.1.1 says room dimensions are set *"from the possibility of conveniently
   accommodating the necessary set of furniture, equipment and sanitary
   fixtures."* That is, verbatim, the argument the engine's ergonomic layer
   already makes.

5. **The rule is in the wrong Azerbaijani norm for our product.** It is in
   **AzDTN 2.7-3** (detached houses). **AzDTN 2.7-2** — the *apartment* norm, and
   the one the engine's layouts actually answer to — has **no proportion rule at
   all** (read first-hand; zero hits for `nisbətən`/`dəfədən` on room length). Its
   only room ratio is the 1:8 window-to-floor rule the engine already ships as
   `win.area_ratio`.

6. **The corpus quietly agrees with 2, for the rooms the norm actually covers.**
   The engine's soft 2,2 was fitted on the **pooled** habitable+wet distribution,
   whose p95 is 2,14 — inflated by kitchens (p95 **2,50**). For the `room*`
   class alone — the Swiss corpus's bedrooms/generic habitable rooms, which is
   what *yaşayış otağı* means — **p95 is 1,94**, below 2,0. Two independent
   traditions land on ~2 for the same room class. That convergence is evidence
   the number is **design-grade, not regional**; the *daylight* mechanism in
   finding 2 is why.

7. **Scope mismatch, and it cuts against the profile option.** The norm's rule
   covers habitable rooms only. The engine's rule binds **habitable *or wet***.
   Kitchens and bathrooms — the classes where the engine's cap actually bites
   (kitchen p99.5 **3,63**) — are precisely the classes the norm's rule does not
   reach.

**Recommendation to ticket 72, stated as evidence not as a decision:** the
correction to the false note is unconditional and cheap. The 2:1 itself should
**not** enter `profiles.AZ` as an orientation-free aspect cap, because (a) it is
not an Azerbaijani fact, (b) it is not the same predicate the engine computes,
and (c) the norm that governs apartments does not state it. The honest homes for
it are the **soft** side — where 2,2 already sits within 0,2 of it and costs
nothing to defend — and, if anyone wants the real rule, a **new directional
daylight-depth predicate** that the engine does not currently have and that
would need a window normal to compute.

---

## 2. What each document actually says

`force` uses the repo's `source_force_vocabulary`. `conf` uses
`value_format.conf_meanings`: **verified** = read first-hand from the primary
document; **reported** = a credible third party attributes it; **derived** =
computed from a verified value.

| Document | Proportion rule? | Value | Force | conf |
|---|---|---|---|---|
| **SNiP II-L.1-71\*** cl. 3.4 (USSR, 1971) | **YES** | depth ≤ **6 m** *and* ≤ **2× width**, *one-sided lighting only*; bay window excluded; +5 % modular tolerance | **mandatory** (*«должна быть»*) | **verified** |
| **SNiP II-L.1-62** cl. 1.19 (USSR, 1962) | **YES** | depth ≤ **6 m** *and* ≤ **2× width**, **unconditional**; +5 % modular tolerance | **mandatory** | **verified** |
| **SNiP 2.08.01-89\*** (USSR/RF) | **NO** | — (cl. 2.7 gives *auxiliary*-room widths only) | — | **verified** (negative) |
| **SP 55.13330.2016** cl. 6.1 (RF, detached houses) | **NO** | — (areas + auxiliary widths; no closing proportion sentence) | — | **verified** (negative) |
| **SP 31-107-2004** cl. 6.1.9 (RF, planning guidance) | **NO** | habitable-room **width** ≥ 3,2 m living / 2,4 m bedroom (new build) | advisory SP | **verified** (negative on proportion) |
| **AzDTN 2.7-3** cl. 5.1 (AZ, 2023, detached houses) | **YES** | length ≤ **2×** width | **recommended** (*«tövsiyə olunur»*) | **verified** |
| **AzDTN 2.7-2** (AZ, 2021, **apartments**) | **NO** | — (only 1:8 window:floor, cl. 9.13) | — | **verified** (negative) |
| **СНБ 3.02.04-03** cl. 4.11 (Belarus, apartments) | **YES** | depth ≤ **2× width**, *«как правило»* | mandatory but **derogable**; superseded 2018 | **reported** — ⚠️ see 2.5a |
| **ТКП 45-3.02-230-2010** cl. 5.5 (Belarus, **single-family/blocked houses**) | **YES** | depth ≤ **2× width** | **fully mandatory**, no softener | **reported** — ⚠️ see 2.5a |
| **СН 3.02.01-2019** (Belarus, current) | **NO** | — (cl. 4.1 delegates room dimensioning to the design brief) | — | **reported** |
| **СП РК 3.02-101-2012** cl. 4.4.10.22 (Kazakhstan) | **near-miss** | rooms deeper than 6 m *recommended* ≥ **4 m** wide; *«не рекомендуются узкие и глубокие комнаты»* | advisory | **reported** |
| **СП РК 3.02-101-2012** cl. 4.4.10.21 (Kazakhstan) | **depth cap** | apartment depth ≤ **10 m from the window**; building width ≤ 24 m | **mandatory** | **reported** |
| **Georgia**, Decree №41/2016 cl. 1208.1 | **NO** | no plan dimension < **2,2 m** (IBC 7 ft metricated) | mandatory | **reported** |
| **Ukraine, Armenia, Moldova, Uzbekistan** | **NO** | — | — | **reported** (negative) |
| **⚠️ PORTUGAL, RGEU art. 69.º n.º1 d)** | **YES** | **length ≤ 2× width** for compartments ≥ 15 m² — **waived where openings are made in the two most distant opposite walls** | **mandatory** national regulation | **verified** — §7.1 |

### 2.1 The Soviet original, read first-hand

`SNiP II-L.1-71*` cl. 3.4, verbatim:

> «3.4. Глубина жилых комнат в квартирных домах и общежитиях **при одностороннем
> освещении** должна быть **не более 6 м и не превышать двойной ширины**, при
> этом глубина эркера не учитывается.
>
> Примечание. Для обеспечения требований модульных размеров допускается
> увеличение глубины жилых комнат до 5 %.»

*"The **depth** of habitable rooms in apartment houses and dormitories **with
one-sided lighting** shall be **not more than 6 m and shall not exceed twice the
width**; the depth of a bay window is not counted. Note: to satisfy modular
dimension requirements, an increase in habitable-room depth of up to 5 % is
permitted."*

Source: <https://meganorm.ru/Data2/1/4293823/4293823188.htm> (retrieved
2026-09-01, HTTP 200 via `curl`, 114 281 chars of extracted text).

**Cross-validation that this is the right document.** The same file carries
cl. 3.13 note 1 — the window-to-floor ratios *«не более 1:6,5 и 1:5,5»* with a
floor of *«не менее 1:8»*. `room-constraints.json` already cites
"1:6.5 … a published cap in SNiP II-L.1-71\*" for the solver's soft objective, so
the repo has trusted this exact document before. The copy is genuine.

Three things in this clause that a naive reading of "2:1" loses:

1. **`Глубина`, not `длина`.** Depth is measured *away from the window wall*. The
   rule is directional and window-anchored.
2. **`при одностороннем освещении`.** The rule only binds single-aspect rooms. A
   dual-aspect or corner room is outside it entirely.
3. **The 6 m companion and the 5 % tolerance.** The binding constraint for a
   3,0 m-wide room is the 2×; for a 4,0 m-wide room it is the 6 m. And the
   tolerance makes the effective figures **2,1** and **6,3 m**.

Note the arithmetic coincidence, which is almost certainly not a coincidence:
6,0 m ÷ 2 = 3,0 m, and **3,0 m is exactly the habitable-room width AzDTN 2.7-3
cl. 5.1 makes mandatory**. The Soviet pair (min width, max depth) and the ratio
are the same rule stated twice.

### 2.1a ⭐ The 1962 original, and the 1971 edit is itself the evidence

`SNiP II-L.1-62` cl. 1.19, read first-hand
(<https://meganorm.ru/mega_doc/norm/normy/4/snip_II-l_1-62_stroitelnye_normy_i_pravila_chast_II_razdel_l.html>,
66 988 chars):

> «1.19. Глубина жилых комнат должна быть **не более 6 м** и **не должна
> превышать двойной их ширины**. Примечание. Для обеспечения требований модульной
> системы допускается увеличение глубины жилых комнат в пределах 5 %.»

⭐ **The 1962 form is UNCONDITIONAL. The 1971 form ADDED
*«при одностороннем освещении»* and the bay-window exclusion.** The Soviet
normative authors, revising their own rule after nine years, narrowed it to
**single-aspect rooms only**. That edit is the strongest available evidence that
the rule was understood by the people who wrote it as a **daylight** rule and not
a proportion aesthetic — they restricted it to exactly the case where daylight
from one wall is the binding constraint.

⚠️ **And AzDTN's form matches the 1962 one, not the 1971 one** — unconditional,
no lighting qualifier. It kept the ratio, dropped the 6 m companion, dropped the
single-aspect condition, and demoted the force to *recommended*. Of the four
things the 1971 clause said, AzDTN retained one.

| edition | ratio | 6 m cap | single-aspect only | bay excluded | force |
|---|:--:|:--:|:--:|:--:|---|
| SNiP II-L.1-62 cl. 1.19 | ✅ | ✅ | ❌ | ❌ | mandatory |
| SNiP II-L.1-71\* cl. 3.4 | ✅ | ✅ | ✅ | ✅ | mandatory |
| SNiP 2.08.01-89\* | ❌ | ❌ | — | — | — |
| **AzDTN 2.7-3 cl. 5.1 (2023)** | ✅ | ❌ | ❌ | ❌ | **recommended** |

### 2.2 Where it died in the Russian line

`SNiP 2.08.01-89*` — read first-hand
(<https://meganorm.ru/Data2/1/4294854/4294854790.htm>, 64 873 chars). Searched
whitespace-insensitively:

| term | hits |
|---|---:|
| `глубинажилых` | **0** |
| `двойнойширины` | **0** |
| `пропорц` | **0** |
| `ширинажилых` | **0** |

What survives is cl. 2.7 — widths for **подсобные помещения** (auxiliary rooms)
only: kitchen 1,7 · hall 1,4 · corridors 0,85 · WC 0,8 (min depth 1,2). The
habitable room is left unconstrained in shape.

`SP 55.13330.2016` — the Russian **detached-house** norm, i.e. the direct
structural counterpart of AzDTN 2.7-3. Read first-hand from
<https://sro-a.ru/upload/medialibrary/abc/SP-55.13330.2016.-Svod-pravil.-Doma-zhilye-odnokvartirnye.-SN.pdf>
(28 pp., extracted via `pypdf`, Cyrillic extraction sanity-checked). Zero hits
for `пропорц`, `вдвое`, `в2раза`, `соотношен`, `длинажилой`, `ширинажилой`.

Its cl. 6.1 is worth putting beside AzDTN 2.7-3 cl. 5.1, because the parallel is
unmistakable and the **divergence is the whole finding**:

| | SP 55.13330.2016 cl. 6.1 | AzDTN 2.7-3 cl. 5.1 |
|---|---|---|
| living room | 16 m² (14 if only one) | 16 m² |
| bedroom | 8 m² (10 two-person, 7 mansard) | **9 m²** (12 two-person, 8 mansard) |
| wheelchair bedroom | 9 m² | 9 m² |
| kitchen | 9 m² | 9 m² |
| kitchen zone in kitchen-diner | 6 m² | 6 m² |
| bathroom / combined | — | 3,2 / 3,8 m² |
| widths given for | **auxiliary rooms only** | **habitable rooms too — 3,0 m** |
| **closing proportion sentence** | **absent** | **present — length ≤ 2× width** |

AzDTN is visibly built on the SP 55 template. It **adds** two things: a habitable
room width, and the proportion sentence. Both are exactly the two halves of the
1971 Soviet rule. Azerbaijan did not invent the rule and did not inherit it from
modern Russia — it **kept the older one**.

### 2.3 The modern Russian answer to the shape question is furniture

`SP 31-107-2004`, *Архитектурно-планировочные решения многоквартирных жилых
зданий* — the Russian family's **architectural-planning design guidance**, and
therefore the single most likely modern carrier of a proportion rule. Read
first-hand from <https://files.stroyinf.ru/Data2/1/4294813/4294813059.htm>
(140 367 chars). Whitespace-insensitive search:

| term | hits |
|---|---:|
| `пропорц` | **0** |
| `вдвое` | **0** |
| `в2раза` | **0** |
| `соотношен` | 1 — *percentage mix of apartment types*, not room shape |
| `глубинажилой` | **0** |

What it does state, cl. 6.1.9 — habitable-room **widths**, which is a different
predicate:

> «…ширина жилых комнат в новом строительстве **должна быть не менее**, м: общей
> комнаты (гостиной) — **3,2**; спальни — **2,4**. В квартирах реконструируемых и
> модернизируемых жилых домов … общей комнаты (гостиной) — **2,8**; одной из
> спален — **2,25**.»

with the closing qualifier that for dwellings of other ownership forms these
*«могут приниматься в качестве рекомендуемых»* — may be taken as recommended.

And cl. 6.1.1, which is the governing principle and reads like the engine's own
ergonomic layer:

> «При проектировании квартир площади и габариты отдельных помещений
> устанавливаются исходя из возможности удобного размещения необходимого набора
> мебели, оборудования и санитарно-гигиенических приборов.»

*"When designing apartments, the areas and dimensions of individual rooms are
established from the possibility of conveniently accommodating the necessary set
of furniture, equipment and sanitary fixtures."*

⚠️ **This is a corroboration of `ergonomic`, not of an aspect rule.** The modern
Russian design guidance was given the opportunity to state a proportion and
instead stated *furniture fit* and a *minimum width*. That is the same two-part
answer `ergonomic.rooms.*.min_clear_short` / `min_clear_long` already gives.

### 2.3a ⭐⭐ SP 54.13330.2022 — the ticket's named parent, and it delegates to *ergonomics* by name

The ticket calls SP 54.13330 *"the parent document AzDTN renders"*, so it is
verified here directly rather than left to inference. **Unabridged** copy — 56 pp.,
180 105 chars, cl. 5.7 / 5.8 / 5.11 / 5.12 all present, so it is **not** the
abridged tiflocentre.ru text that `ru_sp_54_13330.caution` warns about:
<https://www.fkr-spb.ru/upload/iblock/e62/7vxc9o7pegu5vnd1xegbtxzg4ffdhry5.pdf>

Whitespace-insensitive search: `пропорц` **0**, `двойнойширины` **0**,
`глубинажилых` **0**, `вдвое` **0**, `в2раза` **0**, `ширинажилых` **0**.

cl. 5.11, verbatim:

> «5.11 Габариты жилых комнат и вспомогательных помещений квартиры следует
> определять **с учетом требований эргономики** и размещения необходимого набора
> внутриквартирного оборудования и предметов мебели. Площадь жилых комнат и
> вспомогательных помещений в квартирах должна быть, м², не менее: 14 — общей
> жилой комнаты в однокомнатной квартире; 16 — общей жилой комнаты в квартирах с
> числом жилых комнат две и более; 8 — спальни (10 — на двух человек); 8 — кухни;
> 6 — кухонной зоны в кухне-столовой.»

*"The **dimensions** of habitable and auxiliary rooms of an apartment shall be
determined **taking account of the requirements of ERGONOMICS** and the
accommodation of the necessary set of in-apartment equipment and furniture."*

⭐⭐ **The live Russian apartment norm names ergonomics, in the clause where a
proportion rule would go, and then gives areas only — no widths, no ratio.** This
independently verifies for the 2022 edition what `ru_sp_54_13330.force_note`
already asserts — *"the delegation of intra-apartment dimensions to ergonomics is
family-wide"* — and it is the fourth document in this note to answer the shape
question with **furniture**, after SP 31-107-2004 cl. 6.1.1, Neufert's living-room
and bedroom sections, and the Metric Handbook's housing chapter.

⚠️ Per `ru_sp_54_13330.force_note`, **no value from this source may reach the AZ
profile**. It is cited here as a comparator only.

### 2.4 The Azerbaijani clause, read first-hand and independently

Retrieved directly from the Committee — the page URL serves the PDF itself
(16 pp.): <https://arxkom.gov.az/qanunvericilik/normativler/binalarin-muhendis-sistemleri/azdtn-27-3-ferdi-yasayis-evleri-layihelendirme-normalari>

cl. 5.1 closes:

> «Yaşayış otağının uzunluğunun eninə **2 dəfədən çox olmayaraq** qəbul edilməsi
> **tövsiyə olunur**.»

This **independently confirms** the transcription in
`az-kitchen-diner-whole-room.md` §12.2 and `az-market-default-against-practice.md`.
The reading is now third-hand-confirmed and may be treated as `verified`.

The clause's internal register split is also confirmed first-hand, and it matters:

- **areas** — *«az olmamaqla qəbul edilməsi tövsiyə edilir»* → **recommended**
- **widths** — *«az olmayaraq qəbul edilməlidir»* → **mandatory**; `yaşayış otaqları` **3,0 m**, `mətbəx` 2,6 m, `dəhliz` 1,4 m, `hamam` 1,5 m, `ayaqyolu` 0,8 m (1,2 m with washbasin)
- **proportion** — *«tövsiyə olunur»* → **recommended**

**Scope, from the norm's own word list.** The width list says `yaşayış otaqları`
(habitable rooms) and lists `mətbəx` (kitchen) *separately*. So the 2:1 sentence,
which says `yaşayış otağının`, covers **living rooms and bedrooms** and does
**not** cover kitchen or bathroom. It is narrower than the engine's
habitable-or-wet binding.

**And the lighting condition is gone.** AzDTN states the 2× **unconditionally**.
The Soviet original stated it only for single-aspect rooms. Somewhere between
1971 and 2023 the rule lost its physical justification and became a bare number.
⚠️ Adopting it *as stated by AzDTN* means adopting a rule its own author has
detached from the mechanism that made it true.

### 2.5 The apartment norm — a clean negative

`AzDTN 2.7-2` *Yaşayış binaları. Layihələndirmə normaları* (2021, 30 pp.),
retrieved first-hand from
<https://arxkom.gov.az/qanunvericilik/normativler/binalarin-muhendis-sistemleri/zhilye-zdaniya>.

| term | hits |
|---|---:|
| `nisbətən` (relative to) | **0** |
| `dəfədən` (times) | **0** |
| `mütənasib` (proportional) | **0** |
| `uzunluğ` (length) | 4 — all corridors, smoke shafts, hose length |

The only room ratio in the document is cl. 9.13 — light-opening area to floor
area **not less than 1:8** (1:10 for sloped-wall upper storeys) — which the engine
already carries.

⚠️ **The engine ships apartment-derived layouts** (C5: "house layouts come from
apartment priors"). The norm that governs that product states **no** proportion
rule. The 2:1 reaches our product only by the same house→apartment transfer that
`az_azdtn_2_7_3.force_note` already says degrades `conf` to `derived` and forbids
describing as a statutory minimum for an apartment.

---

### 2.5a ⚠⚠ Belarus keeps the rule — and my own first-hand read of it was a FALSE NEGATIVE

**This subsection corrects an error made earlier in this same research.** An
earlier pass of this note recorded Belarus as a *verified negative*, on the
strength of a copy of СНБ 3.02.04-03 pulled from
<https://www.stn.by/files/tr/44.pdf> (11 pp.), grepped whitespace-insensitively
with zero hits for `глубинажилой` and `двойнойширины`. That negative was **wrong**, and the
way it was wrong is instructive.

**That copy silently omits clause 4.11.** Re-checked directly: the extracted
text runs `4.10 … Ширина помещений квартир …` and then jumps **straight to
`4.12`**. The string `4.11` does not occur in the file at all. The grep was
sound; the *document* was abridged — the same failure mode `ru_sp_54_13330.caution`
already records for the tiflocentre.ru copy of SP 54.

The post-Soviet arm, working from different copies, reports cl. 4.11 as:

> «Глубина жилой комнаты, **как правило**, не должна превышать её ширину более
> чем в 2 раза.»

and ТКП 45-3.02-230-2010 *«Дома жилые одноквартирные и блокированные»* cl. 5.5 as
the same sentence **without** the *«как правило»* softener — i.e. **fully
mandatory**, and scoped to **single-family and blocked houses**, which is
**exactly AzDTN 2.7-3's scope**.

⭐ **Partial independent corroboration.** That arm's reading of the *adjacent*
clause is confirmed by my own copy: its reported СНБ cl. 4.10 widths — living
(общая) **3,0**, single bedroom/kitchen **2,3**, double bedroom **2,6** — match my
extracted text verbatim, together with wheelchair living 3,4 and прихожая 1,4. The
clause numbering gap sits exactly where the reported rule would be. That is not
proof of cl. 4.11's wording, but it is strong structural corroboration, and it is
why this note now carries Belarus as a **positive**.

⚠️ **`conf: reported`, not `verified`.** I did not read ТКП 45-3.02-230-2010 or
an unabridged СНБ 3.02.04-03 first-hand, and the arm itself could not confirm the
ТКП's **in-force status** (tnpa.by and normativka.by unreadable). Treat "still
current in Belarus" as **NOT ESTABLISHED**.

⭐⭐ **Why this matters more than the correction itself: Belarus preserves the
SEMANTICS Azerbaijan lost.** Belarus says **глубина** — *depth*, the dimension
measured from the window wall. AzDTN says **uzunluq** — *length*, which has no
window anchor and is orientation-blind. Of the two surviving post-Soviet
renderings of the 1962 rule, **the Belarusian one is faithful and the Azerbaijani
one is degraded** (§2.1a already showed AzDTN kept one of the 1971 clause's four
elements). If the engine ever implements this rule, it should implement the
Belarusian form.

## 3. The predicate mismatch — why "2:1" cannot be dropped into `dim.aspect_ratio_*`

This section is the one with engineering consequences.

**What the engine computes.** `dim.aspect_ratio_hard`: *"the ratio of its longer
to its shorter clear dimension"*. Orientation-free by construction — and
deliberately so. `ergonomic.reading.short_and_long_not_width_and_depth` says it
outright: *"A room has no canonical orientation, so the pair is (shorter side,
longer side), not (x, y)."*

**What SNiP II-L.1-71\* computes.** Depth ÷ width, where **depth is normal to the
glazed wall**. Directional, and it needs a window to be defined at all.

These agree only when the room is deeper than it is wide. They disagree exactly
where it matters:

| room | engine's longer:shorter | SNiP depth:width | engine verdict at a 2,0 cap | SNiP verdict |
|---|---:|---:|---|---|
| 3,0 m wide × 6,0 m deep, window on the 3,0 m wall | 2,00 | **2,00** | at the cap | at the cap |
| **6,0 m wide × 3,0 m deep, window on the 6,0 m wall** | **2,00** | **0,50** | **at the cap** | **comfortably compliant — this is a good room** |
| 3,0 × 6,0, windows on both 3,0 m walls | 2,00 | n/a — dual-aspect | at the cap | **rule does not bind** |

The middle row is a shallow, wide, well-daylit room — a living room with a broad
window wall, which is a *desirable* type. An orientation-free 2,0 cap treats it
identically to the tunnel the rule exists to prevent.

**Consequence.** There are three distinct things ticket 72 could do, and only one
of them is "adopt 2:1":

1. **Correct the false note.** Unconditional, free, and owed regardless.
2. **Read the norm as corroboration of the existing soft term.** 2,2 is within
   0,2 of the norm's 2, and the norm's own 5 % modular tolerance puts its
   effective figure at **2,1**. This costs nothing and claims nothing — the
   ticket already identifies it as the cheapest reading, and this research
   supports it.
3. **Implement the real rule** — a directional, window-anchored, single-aspect
   daylight-depth predicate with a 6 m companion cap. The engine has no such
   predicate. It would need the window normal, which `win.*` knows and `dim.*`
   does not, and it would be a **new** hard predicate — which C14 forbids a
   profile from adding.

Option 3 is the only one that is faithful to the source, and it is the one the
region-profile framing cannot deliver, because C14 lets a profile *raise a floor
on a predicate that already binds* and this predicate does not exist.

### 3.1 ⭐ Option 3 is cheaper than it looks — the engine already knows the glazed wall

`win.habitable_has_window` is **hard** and reads:

> *"Every Space whose Room has `needs_window` true hosts at least one window
> Opening on a WallSegment of that Space whose Envelope edge condition is
> exterior."*

So for **every** habitable Space the engine already identifies a specific
exterior `WallSegment` carrying a window. That segment's normal **is** the depth
axis. A daylight-depth predicate therefore needs **no new geometry and no new
Proposal field** — it is:

```
depth  = extent of the Space measured normal to its window-hosting WallSegment
width  = extent measured along that segment
single_aspect = the Space's window-hosting segments are collinear
```

and the rule binds only when `single_aspect`. Everything on the right-hand side is
already in the Plan.

The **vocabulary already exists too** — *H8 and the single-aspect flat*
(ticket 26) is where the repo learned to reason about frontage and exposure, and
`win.area_ratio` already carries an exterior-face clause added by that ticket. A
daylight-depth rule would be that ticket's natural continuation, not a new
concept.

This matters for the ticket's cost accounting: option 3 is a **new hard
predicate**, which is a bar change and out of ticket 72's scope — but it is not a
research project, and it is the only option that reproduces what the sources
actually say. Worth raising as its own ticket rather than being priced out by
assumption.

⚠️ **Note the naming collision waiting there.** `dim.min_clear_depth` already
exists and its statement is *"Every Space longer clear dimension is at least
`min_clear_long`"* — i.e. the rule named "depth" measures the **longer side**,
orientation-free, and has nothing to do with depth-from-glazing. Any new rule
must not be called `dim.*_depth`.

---

## 4. What the corpus says, and it is not what the soft term was fitted on

From `acceptance-thresholds.md` §2.1, 235 045 binding rooms in 42 985 Swiss
dwellings, and re-read here for the question this note asks:

| class | p50 | p90 | p95 | p99 | p99.5 |
|---|---:|---:|---:|---:|---:|
| all binding rooms (pooled, habitable **+ wet**) | 1,39 | 1,91 | 2,14 | 2,71 | **3,02** |
| **`room*` — bedrooms/generic habitable** | 1,37 | 1,79 | **1,94** | 2,24 | 2,33 |
| `living_dining` | 1,37 | 2,11 | 2,34 | 2,96 | 3,21 |
| `kitchen` | 1,45 | 2,17 | **2,50** | 3,35 | 3,63 |
| `bathroom` | 1,39 | 1,87 | 2,09 | 2,52 | 2,81 |

`corpus_label_map` collapses ROOM / BEDROOM / STUDIO to PRIVATE, so **`room*` is
the Swiss corpus's habitable-room class** — the same population *yaşayış otağı*
denotes.

Three readings fall out:

1. **For the class the norm covers, the corpus p95 is 1,94 — below the norm's
   2,0.** An Azerbaijani regulator writing 2 and a Swiss corpus reporting 1,94
   are the strongest evidence in this note that the number is **not regional**.
   Two traditions, no contact, same figure.
2. **The soft term at 2,2 was fitted on the wrong population for this
   comparison.** Its 2,14 is the *pooled* p95, pulled up by kitchens (2,50) and
   `living_dining` (2,34). Against habitable rooms alone the corpus says 1,94.
   The engine's soft term is *looser than both the norm and the corpus* for the
   rooms the norm is about.
3. **The engine's cap bites hardest exactly where the norm is silent.** Kitchen
   p99.5 is 3,63 — above the hard cap. Kitchens are the room type most often
   long-and-thin in real dwellings, and `mətbəx` is listed separately from
   `yaşayış otaqları` in AzDTN cl. 5.1, i.e. outside the 2:1 sentence.

**Cost of a 2,0 cap — NOT ESTABLISHED, and it must be measured.** ADR 0023
requires a published cost before a threshold moves. What can be said from the
existing table without new computation: on habitable rooms alone, 2,0 sits just
below p95 (1,94), so it would reject on the order of **5 % of rooms** — against
0,5 % at 3,0. Dwelling-level cost amplifies room-level cost by roughly 5–6× in
this corpus (0,5 % of rooms → 2,85 % of dwellings at 3,0), which puts a
habitable-only 2,0 cap somewhere in the **low-to-mid tens of percent of
dwellings**. That is an **estimate by extrapolation, `conf: derived`, and it is
not a measurement.** `experiments/acceptance-thresholds/` owns the real number.
It is owed before anyone touches 3,0.

---

## 5. Region-specific or region-invariant? — the verdict

The ticket poses a binary. The evidence does not fit either box cleanly, and the
honest answer names a third thing.

**Not region-specific.** A 1971 all-Union norm, an Azerbaijani norm of 2023, and
a Swiss corpus of 42 985 dwellings all land within 0,06 of 2,0 for habitable
rooms. A number three unconnected traditions agree on is not a regional
convention. `profiles.AZ` would be a **false home**: it would record as an
Azerbaijani fact something Azerbaijan inherited and Switzerland exhibits without
ever writing down.

**Not region-invariant-ergonomic either.** The ergonomic layer's entries are
**floors derived from bodies and fixtures** — a 1700 mm bath *is* the bath. An
aspect cap is a **ceiling**, and no fixture derivation produces one: furniture
tells you a room cannot be smaller than X, never that it cannot be longer than Y.
Putting 2:1 in `ergonomic` would be the first entry in that layer with no
derivation behind it, breaking the property that makes the layer defensible
(`ergonomic.generated_by` → `build_ergonomic_layer.py`).

**What it actually is: TWO different rules that both land near 2, and only one of
them is ours.** This is the finding that resolves the ticket.

| | **Rule A — daylight depth** | **Rule B — design proportion** |
|---|---|---|
| predicate | **depth : width**, depth normal to the glazed wall | **longer : shorter**, orientation-free |
| binds | single-aspect rooms only | any room |
| stated by | SNiP II-L.1-62/71\*, AzDTN 2.7-3, BRE/BS 8206-2, Neufert (offices, schools) | **Palladio I.XXI**, Serlio, Vitruvius (dining), Ching |
| natural unit | **metres** (6 m, 7,2 m, 25 ft, 30 ft) | **a ratio** |
| value | 2:1 *given a 3,0 m width*; 1:1,5 *given 4,0 m* | *"not exceed two squares"*, **2:1**, with a monotone preference toward square |
| region | **invariant — it is physics** | **invariant — but it is a tradition, not a measurement** |
| **matches `dim.aspect_ratio_*`?** | ❌ **no** | ✅ **yes** |

⭐⭐ **The Portugal/USSR pair collapses the ambiguity.** Before §7, Rule A's
daylight character rested on the 1971 revision adding a single-aspect condition.
It now also rests on **Portugal waiving the identical ratio for dual-aspect
rooms**, and on **Belarus stating it as *глубина* (depth)**. Three independent
legislatures, one mechanism.

⚠️ **And this sharpens what adopting AzDTN's wording would mean.** AzDTN is the
**only** one of the four that states the rule as orientation-blind *length* with
no window anchor and no lighting condition. Copying AzDTN's form into an
orientation-free `dim.*` predicate would be copying the **most degraded** rendering
of the rule in existence, and would reject the shallow wide daylit room that
Portugal, the USSR and Belarus all explicitly permit.

**Both are region-free. Neither belongs in `profiles.AZ`.** That disposes of the
ticket's primary question: the profile gets **no aspect field**, because no
region owns this number — Azerbaijan inherited it, Russia dropped it, Switzerland
exhibits it without writing it down, and Palladio stated it in 1570.

**Rule A belongs with the window rules.** The engine already has a `win.*` family
that knows about apertures; a depth-from-glazing predicate is a `win.*` rule
wearing a `dim.*` costume (§3.1 shows it is computable today). The repo has done
this before — `win.habitable_touches_exterior` was retired precisely because the
invariant it appeared to protect belonged elsewhere.

**Rule B is what `dim.aspect_ratio_*` already is, and it is already shaped
correctly.** ⭐ Palladio's sentence has exactly the two-term structure the engine
ships: a **monotone preference toward square** (`dim.aspect_ratio_soft`, a ranking
term) plus an **outer ceiling near 2** (`dim.aspect_ratio_hard`). The engine did
not know it had design-grade backing for this shape. It does.

⚠️ **But the engine's two numbers sit on the loose side of Rule B.** Palladio's
ceiling is 2; the engine's hard cap is 3,0. Palladio's preference runs to 1; the
engine's soft term is 2,2. That is a defensible position — 3,0 is fitted as a
*"visibly broken"* catch at Swiss p99.5, not as a design target, and ADR 0023
governs it — but the note should stop claiming there is **no** precedent when
there is one and the engine is looser than it.

⭐ **And 3,0 now has a second, independent defence** that this arm did not find:
the companion note establishes that **[1/3, 3] is the modal hard per-module aspect
bound in the VLSI floorplanning literature**, across three independent papers
(§8.5). So the shipped value is simultaneously the Swiss p99.5 and the
engineering literature's modal bound — arrived at from two unrelated directions.
That is a stronger position than either note alone shows.

**And the tradition is not unanimous** (§8.2): Alberti's series runs to **1:4**,
looser than the engine's 3,0. A note that reported only Palladio would be
selecting its evidence.

**Minimum honest action, in ADR 0023's terms:**

⚠️ **The false claim has TWO copies, and only one of them has been flagged.**
`az-market-default-against-practice.md` §2.3 caught
`rules.json` `dim.aspect_ratio_hard.note`. It did **not** catch
`acceptance-thresholds.md` §2, whose heading reads *"`dim.aspect_ratio_hard` —
**the one rule with no precedent**, and it survives"* and whose opening line
repeats *"the only rule in the spec with **no precedent anywhere**"*. Both
sentences are false in the same way and by the same document. A ticket that fixes
only `rules.json` leaves the claim standing in the research note that `rules.json`
cites as its own justification.

| action | force | cost | owed? |
|---|---|---|---|
| Strike *"No surveyed source states an aspect rule"* from `dim.aspect_ratio_hard.note`; replace with the SNiP II-L.1-71\* / AzDTN 2.7-3 provenance and the predicate-mismatch caveat | — | zero | **yes, unconditionally** |
| Strike *"no precedent anywhere"* / *"the one rule with no precedent"* from `acceptance-thresholds.md` §2 — **second copy, previously unflagged** | — | zero | **yes, unconditionally** |
| Record `SNiP II-L.1-71*` and its cl. 3.4 in `sources` (it is already cited for 1:6.5, so the entry half-exists) | `superseded` | zero | **yes** |
| Note on `dim.aspect_ratio_soft` that 2,2 is corroborated at 2,0–2,1 by two norms and at 1,94 by the corpus's habitable class | soft | zero | **recommended** |
| Add an aspect field to `profiles.AZ.rooms` | — | — | **no** — see §5, false home |
| Move `dim.aspect_ratio_hard` off 3,0 | hard | **unmeasured** | **not without the ADR 0023 cost** |
| New directional daylight-depth predicate | hard, new | unmeasured | **out of scope for ticket 72** — C14 forbids a profile adding a predicate; this is a bar change |

---

## 6. The handbooks — C8's own named grade says NO

Both canonical handbooks were read in full text, first-hand.

### 6.1 Neufert, *Architects' Data* — no habitable-room proportion rule

Editions read: **2nd (International) English**, Blackwell Science, 447 pp.
(<https://www.uceb.eu/DATA/CivBook/03.%20Architect_s%20Data.pdf>) and **4th
English**, Wiley-Blackwell 2012
(<https://archive.org/details/architects-data-ernst-neufert-peter-neufert-z-library>).

| where | what it says about room shape | ratio? |
|---|---|---|
| 2nd ed, *Living rooms*, pp. 67–69 | furniture clearance, seating groups, daylight/orientation. Shape is an **output** of the furniture fit | **none** |
| 2nd ed, *Bedrooms*, pp. 70–72 | *"Rm sizes determined by bed sizes"* | **none** |
| 2nd ed, p. 44, *Standards & Regulations* | area **+ a "least dimension"** (US FHA style): living 11'6", primary bedroom 9'4", other habitable 8'0" | **none** |
| 4th ed, *Residential Buildings*, pp. 135–170 | swept for `proportion`, `aspect ratio`, `room shape`, `length…width`, every `1:x` pattern — **zero hits** | **none** |
| 2nd ed, p. 10 / 4th ed pp. 30–33, *Proportions* / *Geometrical Relationships* | golden section, Modulor red/blue series — applied to **façades, temples, dimensional series** | not a room rule |

⚠️ **Neufert DOES state 1:1.5 — for cellular OFFICES, and this is almost certainly
the origin of the folklore.** 2nd ed, *Office Construction*, p. 234: a room-depth
limit of **6000 mm** (*"otherwise unusable space created towards back of each rm"*)
and then *"Acceptable rm proportions should not exceed ratio of 1:1.5"* — an
**upper limit**, for offices, from which the 1500 mm planning grid is derived.
Anyone who "remembers Neufert saying 1:1.5" is remembering the office chapter.

Neufert's own **depth** rules, which are the relevant family and are all
daylight- or ventilation-driven — none is an aspect rule:

- 4th ed, Schools: windows on one side only → **max classroom depth 7,20 m**
- 4th ed, Universities: free ventilation from one external wall → **depth ≤ 2,5 × clear ceiling height**
- 4th ed, Daylight (DIN 5034): min window width ≥ 65 % of room width; glazing as % of floor banded by room depth
- 4th ed, Rooflighting: rooflight *spacing : room height* 1:1,5 to 1:2 — **a spacing rule, easy to misread as a plan ratio**

### 6.2 The Metric Handbook — no housing proportion rule, and it declines one explicitly

Editions read: **6th**, ed. Buxton, Routledge 2018
(<https://archive.org/details/metric-handbook-planning-and-design-data>) and
**2nd**, ed. Adler, 1999
(<https://archive.org/details/architecture-ebook-metric-handbook-plan_202102>).

- **6th ed, Ch. 21 *Houses and flats*** — rooms sized by the UK NDSS: GIA by
  bedspaces, per-room area **plus minimum width** (single bedroom ≥ 7,5 m² and
  ≥ 2,15 m; double/twin ≥ 11,5 m², principal min width 2,75 m, other 2,55 m;
  living/dining/kitchen width 2,8–3,2 m by occupancy). **Area + minimum width, no
  ratio.** The only proportion word is qualitative, about conversions.
- **2nd ed, Ch. 33** — Parker Morris areas and Housing Corporation bands. Purely
  area-based. No ratio.
- ⭐ **6th ed, Ch. 23 §6.2 is literally headed *"Room size and shape"*** — and
  gives only areas, *"usually rectangular"*, and *"Carefully consider the
  proportions of the room"*, **with no number**. This is the strongest documented
  negative in the whole search: the book takes up room shape as a heading and
  deliberately declines to state a ratio.
- `aspect ratio` in the 6th ed appears only for glazing panes and courtyard H/W.
  **Zero hits in the 2nd ed.**

⚠️ **The Metric Handbook DOES state 1:1.5 — for broadcast/recording STUDIOS.**
Identical sentence in both editions (6th ed Ch. 40, at Fig. 40.1): *"Studio
length-to-breadth ratio should be in the region of 1:1.5."* Note *"in the region
of"* — a **target**, not a cap — and it is an acoustics/camera-tracking rule.

### 6.3 ⭐ The BRE limiting-depth criterion — the one genuinely computable rule

**Metric Handbook 6th ed, Ch. 9 *Light* (Joe Lynes) §3; same text in 2nd ed
Ch. 39.** A side-lit room is too deep when

```
l/w + l/h  >  2 / (1 − R_b)
```

where `l` = depth from window to back wall, `w` = width across the window wall,
`h` = height of window head above floor, `R_b` = area-weighted average reflectance
of the back half of the room.

This is the rule most often mistaken for a proportion rule. It genuinely bounds
depth against width — **but jointly with window head height and surface
reflectance**, so it does not reduce to a single ratio.

Worked through for ordinary domestic geometry (window head h = 2,1 m) — this
arithmetic is the sub-agent's, `conf: derived`, not a claim in the book:

| R_b | w | max l | implied l:w |
|---:|---:|---:|---:|
| 0,5 | 4,0 m | 5,51 m | **1,38** |
| 0,5 | 3,0 m | 4,94 m | **1,65** |
| 0,4 | 3,0 m | 4,12 m | **1,37** |

⭐ **So the BRE criterion lands at roughly 1:1,35–1:1,65 for ordinary rooms** —
which is plausibly the real physical reason 1:1.5 "feels right" to architects,
even though neither handbook asserts it for dwellings.

### 6.4 ⭐⭐ The triangulation, and it is the most important paragraph in this note

**Six unconnected traditions**, asked about habitable-room shape, all answer with
**daylight depth from a single window wall** — and two of them independently
produce the same **6 m**:

| tradition | rule | mechanism |
|---|---|---|
| **SNiP II-L.1-71\* cl. 3.4** (USSR housing) | depth ≤ **6 m** and ≤ 2× width, ***one-sided lighting only*** | daylight |
| **⭐ Portugal RGEU art. 69.1 d)** | length ≤ **2×** width — ***waived when both far opposite walls have openings*** | daylight, by its exemption |
| **Belarus ТКП 45-3.02-230-2010 cl. 5.5** | ***depth*** ≤ **2×** width | daylight, by its choice of *глубина* |
| **Kazakhstan СП РК 3.02-101-2012 cl. 4.4.10.21** | apartment depth ≤ **10 m from the window** | daylight, stated in the clause |
| **Neufert 2nd ed p. 234** (German, offices) | depth limit **6000 mm**, ratio ≤ 1:1,5 | daylight — *"unusable space towards back of rm"* |
| **BRE / Metric Handbook Ch. 9** (UK) | `l/w + l/h > 2/(1−R_b)` | daylight, explicitly |
| **Neufert 4th ed** (schools) | depth ≤ **7,20 m**, windows one side only | daylight |

⭐⭐ **Portugal and the USSR settle it between them.** The USSR restricts its 2:1
to rooms that are **single-aspect**; Portugal **waives** its 2:1 for rooms that
are **dual-aspect**. Two legal traditions with no contact state the same ratio,
for the same room class, and hinge it on the same condition from opposite
directions. **There is no reading of that pair under which 2:1 is an aesthetic
proportion rule.**

**The region-invariant fact is not "2:1". It is "a single-sided-lit room has a
depth limit of roughly 6 m, and any ratio you quote is that limit divided by
whatever width you assumed."** SNiP assumed 3,0 m and got 2:1. Neufert assumed
4,0 m and got 1:1,5. The ratio is a *derived quantity whose value depends on the
width assumption*, which is exactly why different traditions quote different
ratios while agreeing on the metre figure.

⚠️ **This retires the framing of the ticket's question.** "Is 2:1 region-specific
or region-invariant?" has no good answer because 2:1 is not the underlying fact.
The underlying fact is a **depth limit in metres**, region-invariant, and the
ratio is an artefact of the width it was divided by.

---

## 7. Western housing standards — one mandatory 2:1, and its escape clause proves the case

⚠⚠ **METHOD WARNING, AND IT IS THE MOST IMPORTANT PARAGRAPH IN THIS SECTION.**
The Western-norm arm of this research **fabricated a large body of detailed,
plausible, fully-cited findings** — clause numbers, verbatim Spanish and Italian
quotations, inscribed-circle diameters, decree dates and URLs — for **Spain
(Catalonia, Madrid, Basque Country, Galicia, Valencia), Ireland, the Netherlands,
France, Italy and Switzerland**, and then **retracted all of it** on
self-examination.

Two of the fabrications were **headline positives** that this note came within one
shell-quoting error of publishing:

- a claimed **Galicia** rule *"P < 2,2 A"* — presented with a DOG URL, and
  seductive because **2,2 is exactly `dim.aspect_ratio_soft`**. It does not exist.
- a claimed **Lombardy** room-depth cap at 2,5×/3,5× room height. It does not
  exist.

⭐ **The lesson for this repo is not "check sub-agents". It is that a fabricated
number that *coincides with a value you already believe* is the hardest kind to
catch** — the Galicia "2,2" would have been written up as an independent
regulator converging on our fitted p95, and it would have read as the strongest
evidence in the note. **Nothing in §7 below rests on any retracted material.**

Everything retained here was read in an operative text, either by me directly or
from extracted text the arm could point to.

### 7.1 ⭐⭐ PORTUGAL — RGEU art. 69.º n.º 1 d): mandatory 2:1, waived for dual aspect

**Verified first-hand by me** in the extracted text, art. 69 in the wording of
**Decreto-Lei n.º 650/75** amending the **Regulamento Geral das Edificações
Urbanas** (DL n.º 38 382 of 1951). **Mandatory** national building regulation.

> "d) Quando a respectiva área for maior ou igual a 15 m2, **o comprimento não
> poderá exceder o dobro da largura**, ressalvando-se as situações em que **nas
> duas paredes opostas mais afastadas se pratiquem vãos**, sem prejuízo de que
> possa inscrever-se nessa área um círculo de diâmetro não inferior a 2,70 cm."

*"Where the area is 15 m² or more, **the length may not exceed double the
width**, save in cases where **openings are provided in the two most distant
opposite walls**, without prejudice to a circle of diameter not less than 2,70 m
being inscribable in that area."*

(The trailing "2,70 cm" is a typo **in the source**; art. 69.1 c) gives the same
figure as 2,70 m.)

⭐⭐ **Read the exception.** Portugal waives its 2:1 precisely when the room is
**dual aspect**. The USSR restricted its 2:1 precisely to rooms that are **not**
(§2.1). Same ratio, same room class, same condition — stated from opposite
directions by two legal traditions with no contact. This is the load-bearing
evidence for §6.4.

Art. 69 is a **graduated area-banded ladder**, and it is the most directly
implementable shape rule found anywhere in this research:

| compartment area | constraint |
|---|---|
| < 9,5 m² | minimum dimension **2,10 m** |
| ≥ 9,5, < 12 m² | inscribed **circle ⌀ ≥ 2,40 m** |
| ≥ 12, < 15 m² | inscribed **circle ⌀ ≥ 2,70 m** |
| **≥ 15 m²** | **length ≤ 2 × width** *(unless openings in both far opposite walls)* **and** circle ⌀ ≥ 2,70 m |

⭐ **Note the area gate.** The ratio binds **only at ≥ 15 m²**. Smaller
compartments are governed by an inscribed circle instead. Portugal's drafters
judged a ratio to be the wrong instrument for a small room — which is exactly
what §4 shows for us: the classes that breach our cap are the **small wet ones**
(kitchen p99.5 **3,63**), and they are the classes a ratio serves worst.

Two further shape rules in the same article, both aimed at pathologies a
generative layout engine actually produces:

- **art. 69.2 — articulated (L-shaped) rooms.** Where a compartment articulates
  into two non-autonomous spaces, the horizontal dimension of their junction
  *"nunca será inferior a **dois terços da dimensão menor do espaço maior**, com o
  mínimo de **2,10 m**."* — a **throat width ≥ ⅔ of the larger part's smaller
  dimension**. ⚠️ **This is an anti-pinch-point rule for precisely the two-rectangle
  Room that ADR 0014 lets the engine emit**, and the engine has no equivalent.
- **art. 69.3** — kitchen minimum dimension **1,70 m**; minimum clear distance
  between counters on opposing walls **1,10 m**.

⚠️ **Force caveat.** DL n.º 10/2024 set the RGEU to be revoked from 2026-06-01;
DL n.º 108/2026 reportedly deferred revocation until the future *Código da
Construção*. **`conf: reported` on current in-force status, `verified` on the
text.** Read from the Ordem dos Arquitectos SRN consolidated transcription
(<http://www.oasrn.org/upload/apoio/legislacao/pdf/rgeu.pdf>), which states it
does not replace the Diário da República publication; diariodarepublica.pt is
JavaScript-gated and returned an empty body.

### 7.2 UK — read in full, no proportion rule

**NDSS 2015 — verified first-hand by me** (§ below) and independently by the
Western arm. Full text; `proportion`, `ratio`, `shape` and `depth` appear
**zero** times. What it states is **area + bedroom width**, cl. 10 c–e:

> "c. … a single bedroom has a floor area of at least **7.5 m²** and is at least
> **2.15 m wide** … d. … a double (or twin bedroom) has a floor area of at least
> **11.5 m²** … e. 1 double (or twin bedroom) is at least **2.75 m wide** and
> every other double (or twin) bedroom is at least **2.55 m wide**"

cl. 10 h makes it an *effective* clear width (a built-in wardrobe "should not
reduce the effective width of the room below the minimum widths set out above");
cl. 10 i sets ceiling 2,3 m over 75 % of GIA. Force: **planning-policy optional**,
not a Building Regulation — already correctly recorded in the repo as
`planning_policy_optional`.

| GLA / UK document | proportion rule? | what it uses instead |
|---|---|---|
| **London Plan 2021 Policy D6** (528 pp.) | **none** | makes the NDSS widths mandatory; ceiling **2,5 m** over 75 % GIA |
| **Housing Design Standards LPG 2023** | **none** | **C2.6: sitting space ≥ 3,0 m wide, ≥ 3,5 m at 3+ bedspaces**; **C2.12: furnished 1:100 plans are the compliance test**; Note 3 requires the **width and depth of every habitable room** to be drawn; App. 3 dual-aspect tests (135°, openings at least halfway down the depth) |
| **London Housing Design Guide 2010** | **none** | glazing ≥ **20 %** of internal floor area |
| **Approved Document M Vol 1** | **none** | **1500 mm turning circles**; M4(3) single bedroom ≥ 8,5 m² and ≥ **2,4 m wide**, principal double ≥ 13,5 m² and ≥ **3,0 m wide**; 750/1000 mm furniture clearance zones |

⭐ **London's actual room-shape test is furnishability plus a drawn width and
depth** — not a ratio. LPG C2.12 rejects layouts that "cannot comfortably
accommodate all of the prescribed furniture."

### 7.3 Germany and the USA — clean negatives

**Germany.** MBO 2002/2019 read in full: `Seitenverhältnis` **0**, `Raumtiefe`
**0**, `Raumbreite` **0** (re-checked by me against the arm's own extracted
files). § 47 Aufenthaltsräume: clear height **2,40 m**, windows ≥ **1/8 der
Netto-Grundfläche**. § 48 Wohnungen sets **no** room area, width or proportion.
BayBO Art. 45 mirrors it; **WoFlV** read in full is a pure *measurement* rule with
no shape content.

- **DIN 18011** (1967) is **withdrawn without replacement** and paywalled
  (€26.10). **Not read; no claim made about its contents.**
- **DIN 5034-1** paywalled (€74.80), **not read**. Its clause 4.2.2 window-width
  ≥ **55 % of room width** is a **secondary** quotation and is a *window*:*room*
  ratio, not a room aspect ratio. DIN 5034 is **not** an *eingeführte Technische
  Baubestimmung*.
- ⚠️ **The German "Raumtiefe ≈ 2 × Fensterhöhe" figure is a *Faustregel*, not
  code.** No binding German instrument states a room-depth limit; the only binding
  daylight geometry is the 1/8 window-to-floor ratio.

**USA — no code states a length:width ratio anywhere.**

| provision | rule |
|---|---|
| **IRC R304.1** | habitable rooms ≥ **70 sq ft** (kitchens excepted) |
| **IRC R304.2** | habitable rooms **≥ 7 ft (2134 mm) in any horizontal dimension** |
| **IBC 1208.1 / .3** | ≥ 7 ft in any plan dimension; one room ≥ 120 sq ft, others ≥ 70 sq ft |
| **HUD MPS 4910.1** | defines "habitable room", sets **no** dimension or proportion; defers to model codes |
| **NY MDL § 31(2)(d)**; **NYC Admin Code § 27-751** | least horizontal dimension **8 ft** (7 ft in 3+ bedroom units) |

⚠️ **Citation note: the 2024 IRC renumbers R304 → R312.** ICC's own site is
JavaScript-gated (HTTP 403); the text came from UpCodes and a Washington SBCC
reproduction — `conf: reported` on the exact wording, `verified` on the substance
across multiple reproductions.

⭐ **The mid-century FHA documents were worth the look, and they are the closest
American analogue to the daylight family.** FHA **MPR 1947**, read in two
independent state editions, gives **areas only** — and states its intent as
furnishability: rooms *"of such size and so planned as to permit the proper
placing of adequate furniture and equipment."* But it carries two genuine
**plan-depth** devices:

- **cl. 301-C.3** — glazing rises from 10 % to **15 %** of floor area for rooms
  "any portion of which is **more than 18 feet (5,49 m) from a window**". ⚠️ **A
  depth threshold priced in glazing rather than banned** — the same instrument
  Galicia was falsely claimed to use, and the same one the engine already owns in
  `win.area_ratio`.
- **cl. 301-B.6** — row dwellings **"shall be not more than two habitable rooms
  deep"**.

FHA **MPS 1963** adds a **"Least Dimension"** column — living 10'0", dining 7'8",
bedroom 8'0", kitchen 5'0" — still a minimum, never a ratio.

**Norway, TEK17 § 12-7:** binding height 2,4 m, **no minimum room area at all**
(*"ingen konkrete krav til minste størrelse"*), 1,5 m turning circle in
non-binding guidance. No proportion rule. ⭐ **Norway regulates room shape purely
by furnishability** — the furthest point of the trend in §2.3a.

### 7.4 ⚠️ What is now UNRESEARCHED, and it includes the brief's top target

Because the retracted material covered them and the session's web-search budget
(200/200) was exhausted before it could be redone, the following are
**NOT ESTABLISHED** — no claim is made in either direction:

**Spain** (all autonomous communities — Catalonia, Madrid, Basque Country,
Galicia, Valencia, Andalucía), **Ireland**, **the Netherlands**, **France**,
**Italy**, **Switzerland**, **Ukraine (DBN V.2.2-15)**, and the **paywalled DIN
and SIA** norms.

⚠️ **Spain is the highest-value remaining gap.** Spanish habitability decrees
are regulated at community level and are the jurisdiction most likely to encode
room shape as an **inscribed figure** — the mechanism §8.6 identifies as
strictly more expressive than a ratio, and the one the engine would most benefit
from. It should be the first target of any follow-up.

---

## 8. Design-theory provenance — and the one source whose predicate matches ours

⭐ **Independent corroboration worth recording.** The design-theory arm reached
SNiP II-L.1-62 cl. 1.19 and SNiP II-L.1-71\* cl. 3.4 **independently**, at the
same meganorm URLs, and read the same verbatim text as §2.1/§2.1a above. Two
unconnected searches converging on the same two clauses is the strongest
reliability signal available in this note.

### 8.1 ⭐⭐ Palladio states a 2:1 ceiling, and it is orientation-free — like ours

**Andrea Palladio, *The Four Books of Architecture*, Book I, Ch. XXI**, read
verbatim in the **Isaac Ware 1738** translation
(<https://archive.org/download/gri_33125011569684/gri_33125011569684_djvu.txt>)
and corroborated in the independent **Giacomo Leoni 1715** translation
(archive.org `architecturePal00Pall`). Public domain, quoted properly:

> "In the length of halls I use not to exceed **two squares**, made from the
> breadth; but **the nearer they come to a square, the more convenient and
> commendable they will be**."

and the canonical set:

> "The most beautiful and proportionable manners of rooms, and which succeed
> best, are seven, because they are either made round (tho' but seldom) or
> square, or their length will be the diagonal line of the square, or of a square
> and a third, or of one square and a half, or of one square and two thirds, or
> of two squares."

Numerically: circle · **1:1** · **1:√2 (1,414)** · **4:3 (1,333)** · **3:2
(1,500)** · **5:3 (1,667)** · **2:1**. The series **terminates at 2:1**.

⚠️ **Both quotations were re-verified first-hand for this note**, directly against
the Ware 1738 OCR (long-s spelling: *"I ufe not to exceed two fquares, made from
the breadth"*, *"The moft beautiful and proportionable manners of rooms … or of
two fquares"*). They are accurate.

⚠️ **Scope, stated precisely, because it is easy to overclaim.** The explicit
ceiling sentence is about **halls** — the *sala*, which the preceding sentence
says *"ought to be much larger than the others, and to have the moft capacious
form"*. The **seven-shape canon** is about **rooms** generally. So Palladio does
not state "no room shall exceed 2:1" in one sentence; he states a **ceiling for
the largest room type** and a **canon for rooms that terminates at the same
value**. The two agree at 2:1, and that agreement is the finding — but the note
should not quote the hall sentence as though it were a universal room rule.

⭐ **This is the only source in the entire survey whose predicate is the same
quantity the engine computes.** Every norm rule is *depth : width* anchored to a
window. Palladio's is *length : breadth* — orientation-free, exactly
`dim.aspect_ratio_*`. And it comes in two parts that map cleanly onto the
engine's two-term structure:

| Palladio | engine |
|---|---|
| *"I use not to exceed two squares"* | a **hard ceiling** near 2 |
| *"the nearer they come to a square, the more commendable"* | a **soft monotone preference** toward 1 |

⚠️ **Note what Palladio does NOT say.** He does not give a preferred *band*. He
gives a *direction* (toward square) plus a *ceiling* (2). A rule of the form
"prefer 1,2–1,5" is not Palladio's, and §8.4 shows it is not anybody's.

### 8.2 The rest of the tradition — and it is not unanimous

| source | what it gives | ratio range | conf |
|---|---|---|---|
| **Vitruvius**, *De architectura* VI.iii (Morgan tr., [Gutenberg #20239](https://www.gutenberg.org/cache/epub/20239/pg20239.txt)) | *triclinia* "twice as long as they are wide"; Corinthian/tetrastyle/Egyptian *oeci* same; atriums 5:3, 3:2, √2:1; peristyles 4:3 | **2:1 for dining/reception** | **verified** |
| Vitruvius on **bedrooms** (*cubicula*) | **no length:width rule at all** — Book VI prescribes only **orientation** (eastern exposure) | — | **verified** (negative) |
| **Serlio**, *Tutte l'opere* Bk I (1545) | seven room ratios: 1:1, 4:5, 3:4, 1:√2, 2:3, 3:5, **1:2** | terminates **1:2** | **reported** — NNJ article paywalled, not read |
| **Alberti**, *De re aedificatoria* Bk IX (Leoni 1755) | short 1:1, 3:4, 2:3 · middling 1:2, 4:9, 9:16 · **longest 1:3, 1:4, 3:8** | **runs to 1:4** | **verified**, degraded OCR |
| **Ching**, *Form, Space & Order* 3rd ed. p. 315 | figure *"Seven Ideal Plan Shapes for Rooms"*, attributing Palladio | propagates **2:1** as outer bound | **verified** (in copyright — existence + numbers only) |
| **Alexander**, *A Pattern Language* **Pattern 191** *The Shape of Indoor Space* | *"a rough rectangle, with roughly straight walls, near right angles"* — **NO number** | — | **verified** (negative) |
| Alexander **Pattern 107** *Wings of Light* | wings **≤ 25 ft (~7,6 m)** wide — a **depth** rule | — | **reported** |
| **Rasmussen**, *Experiencing Architecture* ch. V | reportedly denies any uniquely right proportions | — | **NOT ESTABLISHED** — image-only scan, no OCR |

⚠️ **Alberti is the counter-example and it is recorded deliberately.** His series
runs to **1:4**, which is looser than the engine's hard 3,0. The Renaissance
consensus on *rooms* converges at 1:2 (Serlio, Palladio), but the tradition is not
unanimous, and a note that reported only the convergent half would be selecting
its evidence.

### 8.3 The empirical literature does not support a number

| study | finding | conf |
|---|---|---|
| **Franz, von der Heyde & Bülthoff (2005)**, *Automation in Construction* 14(2) 165–172, [doi:10.1016/j.autcon.2004.07.009](https://doi.org/10.1016/j.autcon.2004.07.009) | rated **beauty peaks at L:W ≈ 1,7** (16 participants, 16 virtual rooms) | **verified** via the author's MPI paper |
| **the same author's larger 64-room study** | *"no evidence for nonlinear relations to room proportions could be found … whether the finding in the single-factor study was mainly an **artifact**"* — proportion weak and non-significant (r = .18, p = .16) | **verified** |
| **Stamps (2011)**, *Environment and Behavior* 43(2) 252–273 | area dominates (r = .60); **elongation r = −.22 for concave spaces** (i.e. rooms) — weak, and **no threshold value given** | **reported** — abstract only, full text paywalled |
| **Höge (1997)**, *"The Golden Section Hypothesis—Its Last Funeral"* | *"the golden section did not turn out to be the preferred proportion … It is concluded that the golden section hypothesis is a **myth**."* | **verified** (abstract verbatim) |

⚠️ **Do not justify any aspect threshold by the golden ratio.** Höge buried it,
and Fechner's original result was about rectangles on a table, not rooms. If the
engine ever needs an empirical anchor, the honest one is Franz's **1,7 carried
together with Franz's own retraction**.

### 8.4 ⭐ The "1:1.2–1:1.5 preferred band" is folklore — a well-searched negative

The ticket's hypothesised band **has no primary source.** What exists is a
*teaching* rule, propagated by copying:

- VSSUT Burla, *Basic of Civil Engineering* lecture notes:
  *"It is always advisable to plan a rectangular room with a proportion of **1.2
  to 1.5** … The increase in ratio due to length gives the **tunnel experience**."*
  (<https://www.vssut.ac.in/lecture_notes/lecture1684506126.pdf>)
- GITAM, *Basic Civil Engineering* lecture notes: **word-for-word identical text**
  (<https://gitam.ac.in/wp-content/uploads/2024/03/Basic-civil-engineer-LECTURE-NOTE.pdf>)

Neither cites a source; the identical wording means a shared uncited ancestor.
And the same syllabus is **internally inconsistent** — Brainkart's Anna University
material for the same course states the band as **1.5:1 to 2:1** instead.

**Verdict: taught, not established.** `conf` would be neither `verified` nor
`reported` — there is no source to report. It is the class of claim
`room-shape-market-check.md` calls **NOT ESTABLISHED**.

The sub-agent additionally discounted, by name, a long list of content-farm pages
asserting "ideal room ratio 1:1.5 / 1:1.618" with zero sourcing, all hand-waving
at the golden ratio and several contradicting each other. **No number in this note
rests on any of them.**

### 8.5 The generative literature — ⚠️ **superseded; see the companion note**

⚠️ **This section is deliberately short, because a companion research note
covers the same ground far more thoroughly and reaches a *different and better*
conclusion.** Read
[`room-proportion-constraints.md`](room-proportion-constraints.md) — *"Room
proportion (aspect ratio): who bounds it, at what value, and how"* — which
landed the same day against the same ticket from the **generation-systems** side.

Its finding **corrects** what this arm's narrower scan concluded. Scanning only
the architectural generation papers, this arm found that the field supplies no
justified number:

| paper | what it uses | justification |
|---|---|---|
| Shekhawat et al., [arXiv:1910.00081](https://arxiv.org/abs/1910.00081) | user-supplied `(AR_min, AR_max)` per room; **no defaults** | **none** — where values are needed it **reads them off existing plans, including a Palladio plan** |
| *Constrained Layout Generation with Factor Graphs*, [arXiv:2404.00385](https://arxiv.org/abs/2404.00385) | 1:1 default, **2:1 for the living room** | **none stated** |
| Tell2Design, GreenPlanner, [arXiv:2504.09694](https://arxiv.org/abs/2504.09694) | — | no numeric bound |

⭐ **But the companion note looked in the literature this arm did not — VLSI
floorplanning — and found the numeric precedent that does exist:** the modal hard
per-module bound there is **exactly [1/3, 3]** across three independent papers,
with **[0.5, 2]** hard-coded into the GSRC soft-block benchmark files. So
`dim.aspect_ratio_hard` = 3,0 has an **independent engineering precedent** that
this arm's scan missed.

**Where the two notes must be read together:**

| | this note (standards side) | companion note (systems side) |
|---|---|---|
| is 3,0 arbitrary? | no view — 3,0 has no *design-grade* backing; Palladio's ceiling is 2 | **no** — 3,0 is the modal hard bound in VLSI floorplanning |
| is 2:1 an outlier? | **no** — Soviet, 1962, and Palladio's ceiling | it calls AzDTN's 2:1 "a post-Soviet-tradition outlier" — **this note supersedes that**: §2.1a traces it to SNiP II-L.1-62/71, and §8.1 shows Palladio states the same ceiling |
| hard 2,0? | rejects ~5 % of real habitable rooms; predicate mismatch (§3) | *"would reject construction that exists"* — kitchens at p99.5 = 3,63 |
| **agreed conclusion** | **strike the false sentence; do not hard-tighten to 2,0; the rule's two-term shape is right** | same |

⚠️ **One claim of the companion note this research narrows.** It records building
codes as **ABSENT** on aspect and calls AzDTN's 2:1 a post-Soviet outlier. The
first half is right for **IBC/IRC/NYC**; the second is **not** — the rule is a
1962 Soviet norm that was *mandatory* for ~30 years (§2.1a), and its
disappearance from the modern Russian line (§2.2) is what makes it *look* like an
Azerbaijani peculiarity. Neither note should be cited for "AzDTN invented it".

### 8.6 The alternative encodings — what other jurisdictions do instead of a ratio

Recorded because they are the real market alternatives to an aspect rule:

| jurisdiction | encoding | value | conf |
|---|---|---|---|
| **⭐ Portugal**, RGEU art. 69.1 a)–c) | **area-banded ladder**: min dimension, then **inscribed circle** | 2,10 m → ⌀ 2,40 m → ⌀ 2,70 m | **verified** (§7.1) |
| **Portugal**, RGEU art. 69.2 | **junction/throat width** for an articulated room | ≥ **⅔ of the larger part's smaller dimension**, min 2,10 m | **verified** |
| **USA**, IRC R304.2 / IBC 1208.1 | **minimum plan dimension** | **7 ft (2134 mm)** | **verified** (§7.4) |
| **USA**, NY MDL §31(2)(d) / NYC §27-751 | least horizontal dimension | **8 ft** (7 ft in 3+ bedroom units) | **verified** (§7.4) |
| **USA**, FHA MPR 1947 cl. 301-C.3 | **depth threshold enforced by a glazing penalty** | glazing 10 % → **15 %** beyond **18 ft (5,49 m)** from a window | **verified** (§7.4) |
| **USA**, FHA MPR 1947 cl. 301-B.6 | **plan depth in rooms** | row dwellings **≤ two habitable rooms deep** | **verified** |
| **Kazakhstan**, СП РК 3.02-101-2012 cl. 4.4.10.21 | maximum **apartment depth from the window** | **10 m** | **reported** |
| **USSR**, SNiP II-L.1-62/71\* | maximum absolute **depth** | **6 m** | **verified** (§2.1, §2.1a) |
| **Georgia**, Decree №41/2016 cl. 1208.1 | minimum plan dimension, any direction | **2,2 m** | **reported** |

⭐ **Only two jurisdictions in the whole survey legislate a ratio — Portugal and
the post-Soviet family — and both pair it with a daylight condition.** Everyone
else uses an **absolute length**, an **inscribed figure**, or a **glazing
penalty**. ⚠️ Note especially the FHA's 1947 device: it did not *ban* a deep
room, it **priced** it in glazing. That is the same instrument the engine already
owns in `win.area_ratio`.

---

## 9. What this does NOT settle, and who holds it

| # | open question | holder |
|---|---|---|
| 1 | **The measured cost of any cap below 3,0.** ADR 0023 requires it before the threshold moves. §4 gives an extrapolation, not a measurement; the corpora are not in the repo. | whoever moves `dim.aspect_ratio_hard` |
| 2 | **Whether a daylight-depth predicate is worth its cost.** §3.1 shows it is computable from what the Plan already carries; §6.4 and §8.6 show it is what jurisdictions actually legislate. It is a **new hard predicate** — a bar change, not a profile change, so **out of ticket 72's scope**. Raise separately. | `acceptance-bar.md`'s holder |
| 3 | **Whether the soft term should move from 2,2 toward 2,0.** Palladio's ceiling is 2; Portugal's mandatory cap is 2; Belarus's is 2; the corpus's habitable-only p95 is **1,94**. Four witnesses, and the engine's ranking term is looser than all four. It rejects nothing, so it is the cheapest available alignment. | ticket 72 |
| 4 | **Whether the wet-room binding is right.** Every norm rule found covers *habitable* rooms only; the engine's binds habitable **or wet**, and kitchen has the fattest tail (p99.5 **3,63**). Portugal's area gate (≥ 15 m²) is direct evidence that a ratio is the wrong instrument for small rooms. | ticket 72, or a successor |
| 5 | **An anti-pinch-point rule.** Portugal art. 69.2 (⅔-junction) and France's "spurs under 2 m don't count" both catch a pathology the engine's two-rectangle Room can produce and no current rule detects. Not in scope here; worth raising. | `acceptance-bar.md`'s holder |
| 6 | **⚠️ Spain — the highest-value unresearched jurisdiction.** Community-level habitability decrees are the likeliest place to find room shape encoded as an **inscribed figure**. All Spanish material gathered this session was retracted as fabricated (§7). **Nothing is known.** | follow-up research |
| 7 | Ireland, Netherlands, France, Italy, Switzerland, Ukraine (DBN V.2.2-15) | follow-up research |
| 8 | **In-force status** of Belarus ТКП 45-3.02-230-2010 and of the Portuguese RGEU | follow-up research |
| 9 | **German-original Neufert** (*Bauentwurfslehre*) not obtained; 3rd/5th English editions lending-restricted. A German-original statement absent from the translation cannot be ruled out. | — |
| 10 | **AzDTN's drafting record.** Whether the 2023 drafters took the 2× from SNiP II-L.1-62/71, from the Belarusian ТКП, or from a textbook is **not established**. §2.1a's lineage is inferred from text comparison. | — |

---

## 10. ⚠⚠ Method note — two failure modes this research hit, both recorded

This note contains **two corrected errors**. Both are recorded because the
correction is more reusable than the finding.

**1. A sub-agent fabricated cited findings, and one of them flattered a number we
already believed.** Detailed clause numbers, verbatim foreign-language
quotations, decree dates and working URLs were invented for six countries
(§7). The most dangerous was a claimed Galician rule **"P < 2,2 A"** — because
**2,2 is `dim.aspect_ratio_soft`**, it would have been written up as an
independent regulator converging on our fitted p95. **A fabrication that
confirms your prior is the hardest to catch.** It survived only because the
write-up attempt hit an unrelated shell-quoting error, and the agent retracted
before the retry.

*Reusable rule:* a sub-agent's finding is `reported` at best until someone reads
the text. In this note, every `verified` row names a file that was extracted and
grepped, and §7's surviving claims were re-checked against the arm's own
extracted files.

⭐ **The other two arms were spot-checked against their own extracted files and
held up exactly.** This is recorded because "one agent fabricated" must not be
read as "discount the whole note":

| claim | check | result |
|---|---|---|
| Neufert 2nd ed **p. 234**, offices: *"Single rm depth should not exceed 6000 … Acceptable rm proportions should not exceed ratio of 1:1.5. Thus if strict modular grid thought necessary, 1 500mm feasible grid"* | grepped the arm's extracted `neufert2.txt` | ✅ **verbatim**, under the running head `OFFICE CONSTRUCTION` and the page marker `234` |
| Metric Handbook: *"Studio length-to-breadth ratio should be in the region of 1:1.5."* | grepped `mh_new.txt` | ✅ **verbatim** |
| Design-theory arm's SNiP II-L.1-62 cl. 1.19 and II-L.1-71\* cl. 3.4 | compared against my own independent reads (§2.1, §2.1a) | ✅ **identical text, same URLs, reached independently** |
| Palladio I.XXI, both quotations | I re-read the Ware 1738 OCR myself | ✅ **verbatim** (long-s spelling) |

So the handbook arm (§6) and the design-theory arm (§8) are corroborated at the
points that carry weight. **Only the Western-norm arm fabricated, and it retracted
itself.**

**2. An abridged primary source produced a confident FALSE NEGATIVE — mine, not
an agent's.** Belarus was recorded as a verified negative on a copy of
СНБ 3.02.04-03 that **silently omits clause 4.11**, the clause containing the rule
(§2.5a). The grep was correct; the document was incomplete. The numbering ran
`4.10 → 4.12` and nothing flagged it.

*Reusable rule:* **a negative from a document is only as good as the document's
completeness, and clause-number continuity is a cheap check that was not run.**
`ru_sp_54_13330.caution` already records this exact failure mode for SP 54 — the
repo knew about abridged mirrors and it still happened again. Any future
whitespace-insensitive negative should be paired with a **clause-sequence
continuity check**.

---

## 11. Confidence register

| finding | conf | basis |
|---|---|---|
| SNiP II-L.1-62 cl. 1.19 — depth ≤ 6 m and ≤ 2× width, unconditional, mandatory | **verified** | full text read first-hand |
| SNiP II-L.1-71\* cl. 3.4 — same, restricted to one-sided lighting | **verified** | full text; cross-validated against the repo's own 1:6,5 citation from the same document |
| The 1971 edition narrowed the rule to one-sided lighting | **verified** | both texts read; the diff is direct |
| SNiP 2.08.01-89\* does not carry it | **verified** (negative) | full text, whitespace-insensitive |
| SP 54.13330.2022 cl. 5.11 delegates room dimensions to *ergonomics*; no proportion rule | **verified** | unabridged 56-pp. PDF, cl. 5.7/5.8/5.11/5.12 all present |
| SP 55.13330.2016 and SP 31-107-2004 carry no proportion rule | **verified** (negative) | full texts; SP 31-107 cl. 6.1.1 states the furniture-fit principle |
| AzDTN 2.7-3 cl. 5.1 — length ≤ 2× width, *recommended* | **verified** | PDF read first-hand from the issuer; third independent confirmation in this repo |
| AzDTN 2.7-2 (apartments) carries no proportion rule | **verified** (negative) | full PDF |
| **Portugal RGEU art. 69.1 d) — mandatory 2:1 ≥ 15 m², waived for dual aspect** | **verified** | extracted text read first-hand; art. 69.1–3 in full |
| Portuguese RGEU current in-force status | **reported** | DL 10/2024 / DL 108/2026; gazette not read |
| **Belarus СНБ 3.02.04-03 cl. 4.11 and ТКП 45-3.02-230-2010 cl. 5.5 — depth ≤ 2× width** | **reported** | ⚠️ not read first-hand; adjacent cl. 4.10 widths independently corroborated against my copy, whose clause numbering skips 4.11 (§2.5a) |
| ТКП 45-3.02-230-2010 still in force | **NOT ESTABLISHED** | tnpa.by / normativka.by unreadable |
| Kazakhstan СП РК 3.02-101-2012 cl. 4.4.10.21/.22; Georgia Decree №41/2016 | **reported** | not read first-hand; Kazakh post-2014 amendments paywalled |
| Ukraine, Armenia, Moldova, Uzbekistan carry no proportion rule | **reported** (negative) | not read first-hand |
| UK NDSS — no proportion rule; widths 2,15 / 2,75 / 2,55 m | **verified** (negative + positive) | full text read first-hand from gov.uk, and independently by the Western arm |
| London Plan D6, LPG 2023, LHDG 2010, AD M — no proportion rule | **reported** | read by the Western arm from extracted files; not re-read by me |
| Germany MBO §47/§48, BayBO Art. 45, WoFlV — no proportion rule | **verified** (negative) | `Seitenverhältnis`/`Raumtiefe`/`Raumbreite` = 0, re-checked by me against the arm's extracted MBO files |
| DIN 18011, DIN 5034-1, DIN 18040-2, SIA 500 | **NOT READ** | paywalled; **no claim made about their contents** |
| USA — IRC R304.2 / IBC 1208.1 7 ft; NYC 8 ft; HUD MPS and FHA MPR/MPS state no ratio | **reported** | ICC site JS-gated (403); text from UpCodes + a Washington SBCC reproduction |
| FHA MPR 1947 cl. 301-C.3 (18 ft → 15 % glazing) and 301-B.6 (two rooms deep) | **reported** | two independent state editions read by the Western arm |
| Norway TEK17 §12-7 — no minimum room area at all | **reported** | read by the Western arm |
| **Spain, Ireland, Netherlands, France, Italy, Switzerland** | **NOT ESTABLISHED** | ⚠️ all material gathered was **retracted as fabricated** (§7, §10). Nothing is known |
| Neufert states no habitable-room ratio; 1:1,5 is for **offices** (2nd ed p. 234) | **verified** | 2nd + 4th English editions read in full |
| Metric Handbook states no housing ratio; 1:1,5 is for **studios** (Ch. 40) | **verified** | 2nd + 6th editions read in full |
| BRE / BS 8206-2 limiting-depth criterion `l/w + l/h > 2/(1−R_b)` | **verified** | Metric Handbook Ch. 9; found independently by two arms |
| the ~1:1,35–1:1,65 figures derived from it | **derived** | sub-agent's arithmetic, not a claim in the book |
| Palladio I.XXI — 2:1 ceiling for halls + seven-shape canon terminating at 2:1 | **verified** | Ware 1738 re-read first-hand by me; Leoni 1715 corroborates |
| Vitruvius VI.iii — 2:1 for dining/reception, **none for bedrooms** | **verified** | Morgan translation |
| Alberti's series runs to **1:4** | **verified**, OCR-degraded | Leoni 1755 |
| Ching p. 315 propagates Palladio's seven shapes | **verified** | in copyright — existence + numbers only |
| Alexander Pattern 191 gives **no** numeric ratio | **verified** (negative) | patternlanguage.cc |
| Serlio's seven ratios terminate at 1:2 | **reported** | NNJ article paywalled |
| Rasmussen denies canonical proportions | **NOT ESTABLISHED** | image-only scan |
| Höge (1997) refutes the golden-section preference | **verified** | abstract verbatim |
| Franz (2005) beauty peak at L:W ≈ 1,7, **and the author's own larger study calls it a possible artifact** | **verified** | MPI paper |
| Stamps (2011) elongation r = −.22, no threshold | **reported** | abstract only |
| the "1:1.2–1:1.5 preferred band" | **NOT ESTABLISHED** | two identical uncited lecture PDFs; contradicted at 1.5–2 by the same syllabus elsewhere |
| VLSI modal hard bound [1/3, 3]; GSRC benchmark [0.5, 2] | **reported** | companion note `room-proportion-constraints.md` |
| Swiss `room*` p95 = 1,94 | **verified** | `acceptance-thresholds.md` §2.1, this repo |
| cost of a 2,0 cap | **NOT ESTABLISHED** | extrapolation only; must be measured per ADR 0023 |
