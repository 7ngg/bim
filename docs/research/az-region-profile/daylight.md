# AZ region profile — daylight, the kitchen window, and the area-measurement convention

Partial findings for `docs/wayfinder/tickets/25-the-azerbaijani-region-profile.md`,
items **3** (`win.area_ratio`, `win.kitchen_windowless`) and **7** (the area
measurement convention pair).

- **Owns:** `win.area_ratio`, `win.kitchen_windowless`, and the *report* on
  общая / жилая площадь for the *Area measurement convention* ticket.
- **Does not own, and does not touch:** `data/standards/room-constraints.json`
  (another session owns the merge); the wall-thickness catalogue; the room-area
  table; the decimal separator; the abbreviation table.
- **Sibling partials** in this directory are written by other agents. This file
  touches only itself.
- Researched 2026-08-20.

---

## 0. The headline, before the detail

Three things overturn the ticket's stated expectations, and all three are
verified against primary text:

1. **Azerbaijan has its own multi-apartment residential norm, and it was
   obtained in full.** `AzDTN 2.7-2 "Yaşayış binaları. Layihələndirmə
   normaları"` (2021). The ticket assumed we would have to fall back on a SNiP
   ancestor and label `reported`. We do not. **The headline values are
   `verified` against an Azerbaijani document.**
2. **`СНиП 2.08.01-89*` is no longer in force in Azerbaijan.** AzDTN 2.7-2
   terminated its legal force on AZ territory on its own commencement,
   2021-11-30, in terms printed on its own cover. Anything sourced to it is
   **superseded** for AZ.
3. **The famous "1:5.5 to 1:8" band is not the Azerbaijani rule.** AzDTN 2.7-2
   cl. 9.13 states **a lower bound only — not less than 1:8**. The 1:5.5 *upper
   cap* was in the repealed Soviet norm and is in the current *Russian* norm; it
   is **not in force in Azerbaijan**. Reporting it as the AZ rule would be
   exactly the kind of claim outrunning its source that this ticket warns about.

Also worth stating plainly: **Russian `СП 54.13330` has no legal force in
Azerbaijan.** It is a Russian Federation national document. Azerbaijan's chain
of authority (§1 below) admits Soviet-era SNiP/GOST retained by the 1992 decision
and CIS *interstate* МСН/МСП/ГОСТ — not post-1991 Russian national documents.
`СП 54.13330` appears in this file only as comparative context, never as a source
for an AZ value.

---

## 1. Legal status — which instruments bind in Azerbaijan today

Required by the ticket, and it determines every `force` field below.

**The chain, from primary text:**

- **Şəhərsalma və Tikinti Məcəlləsi** (Urban Planning and Construction Code),
  Law 392-IVQ of 2012-06-29, in force 2013-01-01. **Art. 14.3** makes compliance
  with urban-planning and construction normative documents **mandatory** in
  construction activity. **Art. 14.2** has the executive authority publish the
  list of those documents periodically. **Art. 15.3** admits foreign or
  international norms only where an international treaty Azerbaijan is party to
  so provides.
- **Cabinet of Ministers Decision No. 217 of 2008-09-18** (still `Qüvvədədir`)
  assigns *design* norms to the State Committee on Urban Planning and
  Architecture (ARXKOM), and — decisively — permits, **until replaced by new
  national documents**, reference without translation to (a) the Soviet
  SNiP/GOST corpus retained by Cabinet Decision No. 217 of 1992-04-15, and (b)
  CIS **interstate** documents (МСН / МСП / ГОСТ) brought into force in
  Azerbaijan.

**So: Azerbaijan supersedes SNiP document-by-document, not wholesale.** A Soviet
SNiP remains binding in Azerbaijan until an AzDTN replaces it. That mechanism is
visible on the face of AzDTN 2.7-2 itself, which both kills СНиП 2.08.01-89* and
continues to bind live Soviet/CIS references (TNvəQ 2.08.02-89*, TNvəQ 2.04.01-85*,
DTN 2.02-01-97, DTN 2.04-05-95, ГОСТ 30494-2011, …).

Two consequences for our labelling:

- **AzDTN 2.7-2 and the 2012 area-calculation Qaydalar are `statutory`** — they
  are technical normative legal acts registered in the State Register of Legal
  Acts, and Art. 14.3 makes conformity mandatory.
- **`СНиП 2.08.01-89*` is `superseded` for AZ.** It is retained here only to
  explain where the 1:5.5 figure came from and why it is gone.

> **Note on the "TN və Q" prefix.** Azerbaijani normative documents transliterate
> SNiP as *TNvəQ* (Tikinti Normaları və Qaydaları) and MSN as *DTN*. So
> `DTN 2.04-05-95` in an AzDTN reference list is **МСН 2.04-05-95 "Естественное
> и искусственное освещение"**, the CIS interstate lighting norm, brought into
> force on AZ territory from **2006-01-01** by decision No. 13 of 2005-12-15 of
> the then State Committee on Construction and Architecture. Seeing a SNiP number
> inside an AzDTN is not evidence of sloppiness; it is the retention mechanism
> working as designed.

---

## 2. `win.area_ratio` — the light-opening ratio against floor area

### 2.1 The Azerbaijani rule, verified

**AzDTN 2.7-2, clause 9.13**, read first-hand in the official ARXKOM publication
(short quotation for provenance):

> «Yaşayış otaqlarında və mətbəxlərdə işıqlandırma açıqlıqlarının (pəncərələr,
> lociyanın açıq sahəsi) sahəsinin döşəmənin sahəsinə nisbəti **1:8**-dən az
> olmamalıdır; pəncərələri maili divar konstruksiyalarında yerləşən yuxarı
> mərtəbələr üçün bu nisbət, pəncərələrin işıq buraxma xüsusiyyətləri və
> qarşıdakı binaların kölgə salması nəzərə alınmaqla, **1:10**-dan az olmayaraq
> qəbul edilməlidir.»

Reading it out:

| Question the ticket asked | Answer |
|---|---|
| Exact clause | AzDTN 2.7-2 **cl. 9.13** |
| Exact bounds | **≥ 1:8** (= 0.125). **No upper bound.** |
| Exception | **≥ 1:10** (= 0.100) for top storeys whose windows sit in *inclined* wall constructions, accounting for glazing light transmission and shading by opposing buildings |
| Which rooms | **Living rooms (`yaşayış otaqları`) and kitchens (`mətbəxlər`)** — both, explicitly. Not corridors, not wet rooms. |
| Ratio, KEO, or both | **Ratio only, in this document.** AzDTN states no KEO number of its own; cl. 9.15 delegates normalised daylight/artificial-light indicators to **DTN 2.04-05** (= МСН 2.04-05-95). See §2.3 — the two forms live in two different documents, by design, throughout the whole SNiP family. |
| What counts as the opening | **`pəncərələr, lociyanın açıq sahəsi`** — windows *and the open aperture of a loggia*. A room lit through a loggia is measured against the loggia's open face, not its own window. |

The individual-house norm agrees, independently. **AzDTN 2.7-3 "Fərdi yaşayış
evləri" (2023), clause 8.14**, verified first-hand from the same issuer:
ratio of light-opening area to floor area of living rooms and kitchen **not less
than 1:8**; **not less than 1:10** permitted for mansard storeys. Two AZ
instruments, drafted two years apart, state the same floor and no cap.

### 2.2 Where 1:5.5 actually lives, and why it is not ours

The ticket's "classic REPORTED figure … between 1:5.5 and 1:8" is real, but it
belongs to documents that do not govern Azerbaijan:

- **СНиП 2.08.01-89\* cl. 1.3\*** — the ratio for all living rooms and kitchens
  "as a rule shall not exceed **1:5.5**"; the minimum "not less than **1:8**";
  **1:10** permitted for mansard storeys with roof windows. Verified from full
  text on two independent mirrors. **Repealed for AZ on 2021-11-30 by AzDTN 2.7-2.**
  Note the direction: **1:5.5 is the maximum glazing, 1:8 the minimum** — the
  band is usually quoted backwards.
- **СНиП II-L.1-71\* cl. 3.13** — the ancestor, with a *climate-dependent* cap:
  not more than **1:6.5** in the colder subdistricts, **1:5.5** elsewhere,
  minimum **1:8**.
- **СП 54.13330.2016 cl. 9.13** (Russia) — dropped the cap: **≥ 1:8** only, and
  **≥ 1:10** for top floors with inclined glazing.
- **СП 54.13330.2022 cl. 7.13** (Russia, current) — restored it: **not more than
  1:5.5 and not less than 1:8**; **≥ 1:10** for inclined top-floor glazing. It
  also permits taking the minimum opening area **by KEO calculation** per
  СП 52.13330 and СП 367.1325800 instead of by ratio. All verified first-hand.

So the band exists, it oscillates across editions, and **Azerbaijan currently
sits on the lower-bound-only side of that oscillation.**

> **A jurisdictional contrast that matters for our `force` fields.** In Russia,
> mandatory application is set **clause by clause** by government decree —
> Постановление Правительства РФ № 815 of 2021-05-28 lists which parts of which
> SPs are binding. Under it, **СП 54.13330.2016 cl. 9.13 (the 1:8 ratio) is
> *not* mandatory**, while СП 52.13330.2016 Приложение Л (the 0.5 % KEO) **is**.
> The ratio is voluntary and the KEO is binding — the inverse of the intuition.
> **Azerbaijan has no equivalent clause-level carve-out that we could find.**
> Şəhərsalma və Tikinti Məcəlləsi Art. 14.3 makes conformity with the normative
> document mandatory, full stop. So `force: statutory` attaches to **AzDTN 2.7-2
> cl. 9.13 as a whole**, and the AZ ratio is binding in a way the Russian one is
> not. Anyone tempted to reason about AZ by analogy with the Russian mandatory
> list would get this backwards.

### 2.3 The KEO side — and why the ticket's "ratio or KEO or both" has a clean answer

The ticket asked whether the requirement is expressed as a ratio, a KEO
percentage, or both. **Both — but never in the same document.** Verified by
reading all of them:

- **The lighting norm carries KEO and no ratio.** СП 52.13330 (2011 and 2016,
  all amendments) and СНиП 23-05-95* contain **no window-to-floor ratio
  requirement whatsoever**. СП 52.13330.2016 cl. 3.49 *defines* «относительная
  площадь световых проемов» as a term and then never norms it. Verified by grep
  of all three full texts.
- **The residential norm carries the ratio and no KEO.** AzDTN 2.7-2, AzDTN
  2.7-3, СНиП 2.08.01-89*, СП 54.13330 — all state a ratio and delegate KEO
  onward by reference.

So the division of labour is structural and stable across thirty years, and our
`win.area_ratio` field is consuming the residential-norm form, which is the
correct one for a geometry engine. Good.

**The KEO numbers themselves, and why they are `reported` for AZ.**
AzDTN 2.7-2 cl. 9.15 delegates to **DTN 2.04-05** = **МСН 2.04-05-95**, the CIS
interstate lighting norm, in force in Azerbaijan from 2006-01-01. We could not
obtain an Azerbaijani-published copy of that document (§7). What we *did* read
first-hand is its Russian twin, **СНиП 23-05-95\***, Appendix И* (mandatory),
items 63 and 64:

| Room | KEO, top / combined | KEO, **side** |
|---|---|---|
| Living rooms, lounges, bedrooms | 2.0 % | **0.5 %** |
| Kitchens | 2.0 % | **0.5 %** |

Stable at 0.5 % side-lighting across СНиП 23-05-95*, СП 52.13330.2011 (Прил. К
items 79/80) and СП 52.13330.2016 (Прил. Л items 187/188, renumbered 190/191 by
Amendment 2) — four editions, one number.

**These are `reported` for AZ, not `verified`, and the distinction is exactly the
one this ticket warns about.** МСН 2.04-05-95 and СНиП 23-05-95* are two document
numbers issued by two bodies. They are near-identical twins and Azerbaijan's own
in-force list records МСН 2.04-05-95 as replacing СНиП II-4-79 — but we have not
read the МСН text, and "near-identical" is a claim we have not checked
clause-by-clause.

**The design point, which is the part a solver would get wrong.**
СНиП 23-05-95* cl. 5.4* item (a), and identically СП 52.13330.2016 cl. 5.3 item
(a): the side-lighting KEO is checked **at floor level, 1 m from the wall
furthest from the light openings** — and only **in one room for 1-, 2- and
3-room flats, in two rooms for 4-room flats and larger**. In every *other* room
of a multi-room flat, **and in the kitchen**, the value is checked **at the
centre of the room on the floor plane**.

That asymmetry — one worst-case room per flat, room-centre everywhere else —
mirrors the insolation rule AzDTN inherits, and it means a naive
"every room must hit 0.5 % at the deepest point" checker is **over-strict** and
would reject conforming plans. **We are not implementing KEO in v1** — it needs
sky models, orientation, obstruction angles and a light-climate coefficient that
varies by region group *and* window orientation, none of which our geometry
carries. Recorded so that if KEO is ever added, it is added correctly.

### 2.4 What the engine should carry

`win.area_ratio` is **soft**. The ticket permits a range with a defensible
midpoint provided we say which is which. Here it is:

- **Sourced floor: 0.125 (1:8).** `verified`, AzDTN 2.7-2 cl. 9.13, `statutory`.
  A plan below this is non-conforming in Azerbaijan. This is the only number in
  the field with legal weight.
- **Sourced relaxation: 0.100 (1:10)** for inclined top-floor glazing.
  `verified`, same clause. **Our v1 geometry has no roof or storey model, so
  this cannot fire** — record it, do not implement it.
- **Upper bound: none in force in AZ.** Do not encode 0.182 as an AZ constraint.
  It may be carried as an *advisory* comfort/overheating cap with an explicit
  note that its source is foreign and, for the Soviet ancestor, repealed — Baku
  is in a hot-summer climate where the historical cap had a real purpose, and
  AzDTN 2.7-2 cl. 9.17 does require adjustable solar shading on living-room and
  kitchen openings in climate region III. But it is not AZ law.
- **Defensible soft target if a single number is wanted: 0.154 (≈ 1:6.5).**
  This is `engine_choice`, not sourced. Two things make it defensible rather
  than arbitrary: it is the midpoint of the historical [1:8, 1:5.5] band, and
  **1:6.5 is itself a published cap** in СНиП II-L.1-71* cl. 3.13 for the colder
  climate subdistricts — so it is a ratio the SNiP family actually printed, not
  one we invented by averaging.

**Coupling warning for the solver.** The rule keys on the *floor area of the
room*, so window sizing and room sizing are one problem, not two. A post-processing
pass that places windows after the plan is solved cannot satisfy cl. 9.13 except
by luck. This is the same shape of coupling ADR 0007 found for minima and grid.

---

## 3. `win.kitchen_windowless` — re-sourced from AZ

The `de_baybo` source key is dead: it never existed in the file and it pointed at
a deleted region. Replaced as follows.

### 3.1 The kitchen must have natural light. Verdict: `false`.

**AzDTN 2.7-2, clause 9.12**, verified first-hand:

> «TNvəQ 2.08.02-yə əsasən zirzəmi mərtəbəsində yerləşdirilməsinə yol verilən
> sahələr istisna olmaqla, **yaşayış otaqları və mətbəxlərin**, binanın
> hüdudlarında yerləşən ictimai təyinatlı sahələrin **təbii işıqlandırılması
> olmalıdır**.»

Living rooms **and kitchens** must have natural lighting, along with
public-function spaces inside the building, excepting spaces permitted in the
basement storey under TNvəQ 2.08.02.

AzDTN 2.7-3 cl. 8.14 says the same for individual houses:
«Yaşayış otaqlarında və mətbəxdə təbii işıqlanma təmin olunmalıdır.»

**So the SNiP-family expectation in the ticket is confirmed: AZ is stricter than
German law here. `win.kitchen_windowless = false`, `verified`, `statutory`.**

### 3.2 The kitchen-niche exception — and it is genuinely unresolved in AZ

This is the one place where the AZ text will not give a clean answer, and it
should be recorded as an ambiguity rather than papered over.

- **AzDTN 2.7-2 cl. 5.7** (verified) permits a **`taxça-mətbəx`** (kitchen niche)
  of **not less than 5 m²** in one-room apartments, against a general kitchen
  minimum of 8 m² and a kitchen-zone-in-a-kitchen-diner minimum of 6 m².
- **`taxça-mətbəx` is named as a term distinct from `mətbəx`** in the norm's
  own vocabulary (§3, and again in cl. 5.2, which offers «mətbəx (və ya
  taxça-mətbəx)» as alternatives).
- **cl. 9.12 names only `mətbəxlər`.** It does *not* carry an express carve-out
  for the niche.
- **cl. 9.14's not-normalised list** names «köməkçi otaqlar» (auxiliary rooms)
  and sanitary units, but **does not name `taxça-mətbəx` either**.

So the norm neither clearly requires nor clearly excuses natural light for a
kitchen niche. **That is a real gap in the source, not a gap in the search.**

Contrast, and this is instructive — the Russian successor closes exactly this
gap explicitly, in both editions, verified first-hand:

- **СП 54.13330.2016 cl. 9.12**: natural lighting required for living rooms and
  kitchens «**кроме кухонь-ниш**» — kitchen niches expressly excepted; and
  cl. 9.14 lists kitchen-niches, bathrooms, toilets, sanitary units and laundries
  among spaces where natural lighting **is not normalised**.
- **СП 54.13330.2022 cl. 7.12/7.14**: same carve-out, and 7.14 not-normalised for
  auxiliary rooms of flats *except* kitchens and kitchen-diners.
- **СНиП 2.08.01-89\* cl. 1.3\*, Note** (repealed for AZ) was narrower and
  conditional: a windowless kitchen niche only in dormitory cells serving ≤ 2
  rooms and in **type 1A one-room flats**, and only **with electric cookers and
  artificial exhaust ventilation**. Gas cooking ruled it out.

**Recommendation for the engine:** hold `win.kitchen_windowless = false`
unconditionally in v1 and do **not** implement a niche exception. Three reasons.
The AZ text does not grant one. Every instrument that *does* grant one
conditions it on an electric hob plus mechanical extract plus an apartment-type
classification — conditions our Brief does not carry. And C2's "would I live
here" test is not met by a windowless kitchen in a market where the norm plainly
expects a window. If a niche is ever modelled, the gate is: one-room apartment,
≥ 5 m², electric hob, mechanical supply-exhaust — and it should be flagged as an
`engine_choice` reading of an ambiguous clause, not as a sourced rule.

### 3.3 Bathrooms and WCs may be windowless. Confirmed.

**AzDTN 2.7-2, clause 9.14**, verified first-hand — natural lighting is **not
normalised** for: spaces under a mezzanine without direct light; dressing rooms,
auxiliary rooms, clothes-storage rooms **and sanitary units (`sanitar
qovşaqları`)**; entrance rooms and intra-apartment corridors and halls; apartment
tambours, out-of-apartment corridors, vestibules and halls.

The trade is mechanical extract, exactly as the ticket expected:

- **AzDTN 2.7-2 cl. 9.7** (verified): air is extracted from kitchens, sanitary
  units and food-storage rooms; air from spaces emitting harmful substances or
  odours goes **directly outside** and must not pass into other rooms including
  via ventilation ducts; those ducts **may not be joined** to ducts serving
  in-building car parking or gas-equipment spaces.
- **AzDTN 2.7-2, Table 6** (verified, values re-derived per cited value, table
  not reproduced): bath / shower / WC / combined sanitary unit — **25 m³/h** in
  working mode, **0.5** air changes per hour otherwise. Kitchen with electric
  hob — **60 m³/h**.
- **AzDTN 2.7-3 cl. 8.7** (verified, individual houses): extract not less than
  **60 m³/h** from the kitchen and **25 m³/h** from bath, WC, shower and combined
  sanitary unit.
- The repealed СНиП 2.08.01-89* Appendix 4 carried the same 25 / 50 / 60 family,
  which is why the numbers look familiar.

**So: `is_wet` rooms do not need a window in AZ. `needs_window` stays false for
them, and that is now sourced from an AZ instrument rather than asserted.**

Two adjacent planning constraints, verified, that a plan generator will hit and
that are **not** in our current predicate set — flagging them for whoever owns
adjacency rules, not resolving them here:

- **AzDTN 2.7-2 cl. 9.20**: a sanitary unit **may not** sit above living rooms or
  a kitchen; the exception is a two-level apartment, where it may sit above that
  same apartment's kitchen. (v1 is single-storey, so this cannot fire — record
  only.)
- **AzDTN 2.7-2 cl. 5.9**: bedrooms must not be pass-through. Our `is_private`
  predicate already expresses this shape; it is now sourced for AZ.

---

## 4. The area measurement convention pair — **REPORT ONLY**

**This section decides nothing.** Per the ticket, the choice of which convention
the engine publishes belongs to *Area measurement convention*. What follows is
written so that ticket can consume it directly.

### 4.1 The finding that matters most: AZ has no *жилая площадь*

The ticket frames this as *общая площадь* against *жилая площадь*. **In
Azerbaijan that pair does not exist.** There is one published metric, and there
is no second one.

- The **2012 area-calculation Qaydalar** define **`mənzillərin ümumi sahəsi`**
  (total area of apartments). The term **`yaşayış sahəsi` in the summed-metric
  sense does not appear in that document at all** — I grepped the full text.
- **AzDTN 2.7-2** uses `yaşayış sahəsi` loosely to mean *a dwelling unit*, not
  *the sum of habitable rooms*.
- The repealed **СНиП 2.08.01-89\*** already behaved this way: its Appendix 2
  defines `площадь квартиры` and `общая площадь квартиры` and defines
  `жилая площадь` **only for dormitories**. For flats, "living area" was never a
  defined term — it was implicit in the phrase «жилых комнат».
- **`СП 54.13330.2016` and `.2022` do not define `жилая площадь` either.** They
  define `площадь квартиры` and `общая площадь квартиры`. Verified by grep of
  both full texts.

**So, answering the ticket's sub-question directly:** the modern instruments do
**not** merely "add" *площадь квартиры* alongside the old pair. They **replaced
the pair**. The live distinction is `площадь квартиры` (heated rooms only) vs
`общая площадь квартиры` (heated rooms plus unheated at coefficients) — and
Azerbaijan publishes only the latter. *Жилая площадь* is a Soviet housing-
allocation and statistical concept that the design norms do not carry.

### 4.2 Definition A — `mənzillərin ümumi sahəsi`, the design/inventory metric

**Source:** *Tikinti obyektlərinin sahəsinin və həcminin hesablanması qaydaları*,
approved by ARXKOM Kollegiya decision **No. 07 of 2012-12-04**, register
15201212040007, in force from **2012-12-15**, status **`Qüvvədədir`** (in force,
confirmed against the register API). **Clause 3.8**, verified first-hand:

**Counted:** living rooms; auxiliary rooms (sanitary unit, kitchen, corridor,
storage); plus balconies, loggias, terraces, glazed enclosures and eyvans
**multiplied by reduction coefficients**.

**Coefficients — verified, and they differ from the classic reported pair:**

| Element | Coefficient into `ümumi sahə` |
|---|---|
| `balkon` (balcony), `terras` (terrace) | **0.3** |
| `şüşəbənd` (glazed enclosure), `lociya` (loggia) | **0.5** |
| `eyvan` / veranda | **1.0** |

The ticket's reported "0.3 balconies, 0.5 loggias" is **confirmed**, with the
addition that **terraces share the balcony 0.3** and **verandas/eyvans enter at
full 1.0** — they are not reduced at all. The same 0.3 / 0.5 / 1.0 triple is in
the repealed СНиП 2.08.01-89* App. 2 п.2, which is where AZ inherited it.

*(Historical drift, for the record: СНиП II-L.1-71* cl. 1.9 excluded summer
spaces from total area entirely and used a different set — 0.5 / 0.35 / 0.25 —
for a separate "reduced total area" indicator. The 0.3 / 0.5 convention is a 1989
invention, not an eternal one.)*

**Other deductions, verified, clause 3.8:**

- Area under an intra-apartment stair is **excluded** where clear height from
  floor to the underside of the structure is **1.6 m or less**.
- In a mansard apartment, the part with ceiling height **< 2.7 m** counts at
  coefficient **0.7**, and that sub-2.7 m part **may not exceed 50 %** of the
  apartment's total area.

**Measurement plane — this is what our geometry model needs. Clause 3.2,
verified:**

> Room and other space areas in a residential building are determined by
> measurement **between the finished surfaces of walls and partitions, at floor
> level, skirtings not counted**.

Also excluded from room area: the footprint of a stove/fireplace forming part of
the building's heating system, and of vertical ventilation voids.

**Clause 3.3** (verified): open spaces — balcony, loggia, terrace, eyvan — are
measured **along their inner contour, between the building wall and the railing,
excluding the railing footprint**.

> **Note the divergence from the current Russian practice.** СНиП 2.08.01-89*
> п.6* and СП 54.13330.2016 А.1.4 also measure at **floor level**. But
> **СП 54.13330.2022 А.1.4 / А.2.2 moved the measurement plane to a height of
> 0–1.10 m, taken around the whole perimeter at 1.1–1.3 m from the floor.** AZ
> stayed at floor level. For a model with vertical walls the two agree; they
> diverge only with battered or sloping walls, which v1 does not have. Record it
> so nobody later "harmonises" us onto the Russian 2022 plane by accident.

### 4.3 Definition B — `yaşayış sahəsinin ümumi sahəsi`, the housing-law metric

**And it contradicts Definition A.** This is the single most important thing in
this section for the *Area measurement convention* ticket.

**Source:** *Azərbaycan Respublikasının Mənzil Məcəlləsi* (Housing Code),
**Article 12.5**, on the official state legal portal, verified first-hand:

> «Yaşayış sahəsinin ümumi sahəsi vətəndaşların yaşayış sahəsində yaşaması ilə
> əlaqədar onların məişət və digər ehtiyaclarının ödənilməsi üçün nəzərdə tutulan
> yardımçı sahələrin **(balkon və ya eyvanlar istisna olmaqla)** sahəsi daxil
> olmaqla həmin yaşayış sahəsinin bütün hissələrinin sahəsinin məcmusundan
> ibarətdir.»

Total area of a dwelling = the sum of the areas of all its parts, including the
auxiliary spaces provided for the occupants' domestic and other needs,
**excluding balconies and eyvans**.

**So Azerbaijan carries two different, both-in-force definitions of "total area"
of a dwelling:**

| | Housing Code Art. 12.5 | Area Qaydalar cl. 3.8 |
|---|---|---|
| Purpose | housing-law entitlement, tenure, technical passport | design, inventory, construction statistics |
| Balcony / eyvan | **excluded outright** | **included at 0.3 / 1.0** |
| Loggia, terrace, glazed enclosure | not addressed | included at 0.5 / 0.3 / 0.5 |
| Force | statutory (Code) | statutory (registered normative act) |

They are not reconcilable by reading; they are two metrics for two purposes that
share a name. **The *Area measurement convention* ticket must pick one and say
which, on the drawing.** The design-side metric (Qaydalar 3.8) is what an
architect issuing a plan computes; the Code metric is what a notary or a housing
authority computes. Our consumer is a builder reading a drawing — which argues
for Qaydalar 3.8 — but that is a recommendation for that ticket to weigh, and
this file does not decide it.

### 4.4 Why this may not matter at all in v1 — and the ticket asked for this

The ticket's own note is correct and worth stating sharply: **our v1 geometry
model has no ceiling height and no balcony.** Walking the deduction list against
that:

| Deduction | Fires in v1? |
|---|---|
| Balcony / loggia / terrace / eyvan coefficients (0.3 / 0.5 / 1.0) | **No** — no such element exists in the model |
| Mansard sub-2.7 m coefficient 0.7 and the 50 % cap | **No** — no ceiling height, no roof pitch |
| Under-stair exclusion below 1.6 m clear | **No** — no intra-apartment stair, no clear height |
| Stove / fireplace footprint exclusion | **No** — not modelled |
| Vertical ventilation void exclusion | **No** — not modelled |
| Measurement between **finished** wall faces at floor level | **Yes** — this is the only one that binds |

**Every clause that makes the two conventions diverge is unreachable in v1.**
With no balcony and no ceiling height, `ümumi sahə` under the Housing Code and
`ümumi sahə` under the Qaydalar **compute the same number**, and both equal the
naive sum of room areas measured to the inner finished face.

That is a real finding, not a shrug: **the convention question is currently
undecidable from our geometry and therefore cheap to defer — but only until a
balcony or a ceiling height enters the model, at which point it becomes
load-bearing and the two AZ instruments disagree.** The right move for the
*Area measurement convention* ticket is to name the convention now, cite it, and
note that the divergent terms are inert in v1.

**One clause that *does* bind v1, and needs checking against our geometry:**
clause 3.2's "**finished** surfaces" (`tamamlanmış səthləri`). ADR 0001 erodes by
`t_int/2` from a structural centreline, which yields the **structural** inner
face, not the finished one. Finishes are typically 10–20 mm per face. If the
engine publishes an area computed to the structural face and calls it
`ümumi sahə`, it **overstates** the area by roughly 20–40 mm of perimeter width
per room. That is small but it is systematic and it is in the wrong direction.
Flagging for the *Area measurement convention* ticket; not resolving it here.

---

## 5. Extractable values

Format per `data/standards/room-constraints.json` §`value_format`, plus `force`
per the ticket. `note` given wherever `conf` is `derived` or `engine_choice`, as
that file requires.

```jsonc
[
  {
    "field": "win.area_ratio",
    "value": 0.125,
    "unit": "ratio (window area / room floor area)",
    "src_key": "az_azdtn_2_7_2_2021",
    "ref": "cl. 9.13",
    "conf": "verified",
    "force": "statutory",
    "note": "Lower bound, 1:8. Applies to living rooms AND kitchens. This is the only bound in force in AZ. The light opening counts windows plus the open aperture of a loggia."
  },
  {
    "field": "win.area_ratio.relaxed_inclined_glazing",
    "value": 0.100,
    "unit": "ratio",
    "src_key": "az_azdtn_2_7_2_2021",
    "ref": "cl. 9.13",
    "conf": "verified",
    "force": "statutory",
    "note": "1:10, for top storeys with windows in inclined wall constructions. UNREACHABLE in v1: no roof or storey model. Record, do not implement."
  },
  {
    "field": "win.area_ratio.upper_bound",
    "value": null,
    "unit": "ratio",
    "src_key": "az_azdtn_2_7_2_2021",
    "ref": "cl. 9.13",
    "conf": "verified",
    "force": "statutory",
    "note": "EXPLICITLY NULL. AZ states no upper cap. The 1:5.5 (0.182) cap belongs to SNiP 2.08.01-89* cl.1.3* — repealed for AZ 2021-11-30 — and to SP 54.13330.2022 cl.7.13, a Russian document with no force in AZ. Do not encode 0.182 as an AZ constraint."
  },
  {
    "field": "win.area_ratio.soft_target",
    "value": 0.154,
    "unit": "ratio",
    "src_key": null,
    "ref": null,
    "conf": "engine_choice",
    "force": "voluntary",
    "note": "≈1:6.5. NOT sourced as an AZ rule. Midpoint of the historical [1:8, 1:5.5] band, chosen because 1:6.5 is itself a published cap in SNiP II-L.1-71* cl.3.13 for colder climate subdistricts rather than an invented average. Use as the solver's soft objective; 0.125 remains the only hard AZ floor."
  },
  {
    "field": "win.keo_side_habitable",
    "value": 0.5,
    "unit": "percent (coefficient of natural illumination, side lighting)",
    "src_key": "cis_msn_2_04_05_95",
    "ref": "App. И* items 63-64, as read in the SNiP 23-05-95* twin",
    "conf": "reported",
    "force": "statutory",
    "note": "REPORTED, NOT VERIFIED, and deliberately so. AzDTN 2.7-2 cl.9.15 delegates KEO to DTN 2.04-05 = МСН 2.04-05-95, which is in force in AZ but whose text we could not obtain from any Azerbaijani source. The 0.5% (side) / 2.0% (top or combined) pair for living rooms AND kitchens was read first-hand in its Russian twin SNiP 23-05-95* App. И* items 63/64, and is stable across SP 52.13330.2011 (App. К 79/80) and .2016 (App. Л 187/188, renumbered 190/191). Two document numbers from two issuers: not the same document. NOT IMPLEMENTED IN V1 — KEO needs sky model, orientation, obstruction angle and a light-climate coefficient our geometry does not carry."
  },
  {
    "field": "win.keo_design_point",
    "value": "floor level, 1 m from the wall furthest from the openings, in ONE room for 1-3-room flats and TWO rooms for 4+; room centre on the floor plane for all other rooms and for the kitchen",
    "unit": "definition",
    "src_key": "cis_msn_2_04_05_95",
    "ref": "cl. 5.4* item (a), as read in the SNiP 23-05-95* twin",
    "conf": "reported",
    "force": "statutory",
    "note": "Recorded because it is the part a naive implementation gets wrong. Checking 0.5% at the deepest point of EVERY room is over-strict and would reject conforming plans. Same caveat as win.keo_side_habitable: the AZ instrument is МСН 2.04-05-95, read only in its Russian twin."
  },
  {
    "field": "win.kitchen_windowless",
    "value": false,
    "unit": "boolean",
    "src_key": "az_azdtn_2_7_2_2021",
    "ref": "cl. 9.12",
    "conf": "verified",
    "force": "statutory",
    "note": "Replaces the dead `de_baybo` key. Living rooms and kitchens must have natural lighting. Corroborated for individual houses by AzDTN 2.7-3 cl. 8.14."
  },
  {
    "field": "win.kitchen_niche_windowless",
    "value": false,
    "unit": "boolean",
    "src_key": "az_azdtn_2_7_2_2021",
    "ref": "cl. 5.7 / 9.12 / 9.14",
    "conf": "engine_choice",
    "force": "statutory_guidance",
    "note": "AMBIGUOUS IN SOURCE. AzDTN permits a taxça-mətbəx of >=5 m2 in one-room flats (5.7) and names it as a term distinct from mətbəx, but 9.12 names only mətbəxlər and 9.14's not-normalised list omits the niche. The norm neither requires nor excuses daylight for it. We hold false in v1: the AZ text grants no exception, and every instrument that does (SP 54.13330 9.12/7.12; SNiP 2.08.01-89* 1.3* Note) conditions it on an electric hob plus mechanical extract plus an apartment-type class our Brief does not carry."
  },
  {
    "field": "win.bathroom_windowless",
    "value": true,
    "unit": "boolean",
    "src_key": "az_azdtn_2_7_2_2021",
    "ref": "cl. 9.14",
    "conf": "verified",
    "force": "statutory",
    "note": "Natural lighting not normalised for sanitar qovşaqları (bathroom/WC/combined units), auxiliary rooms, dressing rooms, intra-apartment corridors and halls."
  },
  {
    "field": "win.wc_windowless",
    "value": true,
    "unit": "boolean",
    "src_key": "az_azdtn_2_7_2_2021",
    "ref": "cl. 9.14",
    "conf": "verified",
    "force": "statutory",
    "note": "Same clause; sanitar qovşağı covers WC, bathroom and combined unit."
  },
  {
    "field": "vent.extract_wet_room",
    "value": 25,
    "unit": "m3/h",
    "src_key": "az_azdtn_2_7_2_2021",
    "ref": "Table 6",
    "conf": "verified",
    "force": "statutory",
    "note": "Working mode, for bath / shower / WC / combined sanitary unit; 0.5 ACH otherwise. This is the trade that buys the windowless wet room. Not a v1 field — recorded so the windowless permission is not carried without its condition."
  },
  {
    "field": "vent.extract_kitchen_electric",
    "value": 60,
    "unit": "m3/h",
    "src_key": "az_azdtn_2_7_2_2021",
    "ref": "Table 6",
    "conf": "verified",
    "force": "statutory",
    "note": "Kitchen with electric hob. Corroborated by AzDTN 2.7-3 cl. 8.7."
  },
  {
    "field": "area.convention.published_metric",
    "value": "ümumi sahə",
    "unit": "name",
    "src_key": "az_area_rules_2012",
    "ref": "cl. 3.8",
    "conf": "verified",
    "force": "statutory",
    "note": "REPORT ONLY — the choice belongs to the Area measurement convention ticket. AZ publishes no жилая площадь equivalent: `yaşayış sahəsi` as a summed metric appears in neither the 2012 Qaydalar nor AzDTN 2.7-2."
  },
  {
    "field": "area.balcony_coefficient",
    "value": 0.3,
    "unit": "coefficient",
    "src_key": "az_area_rules_2012",
    "ref": "cl. 3.8",
    "conf": "verified",
    "force": "statutory",
    "note": "balkon and terras both 0.3. INERT IN V1 — no balcony in the geometry model."
  },
  {
    "field": "area.loggia_coefficient",
    "value": 0.5,
    "unit": "coefficient",
    "src_key": "az_area_rules_2012",
    "ref": "cl. 3.8",
    "conf": "verified",
    "force": "statutory",
    "note": "lociya and şüşəbənd (glazed enclosure) both 0.5. INERT IN V1."
  },
  {
    "field": "area.veranda_coefficient",
    "value": 1.0,
    "unit": "coefficient",
    "src_key": "az_area_rules_2012",
    "ref": "cl. 3.8",
    "conf": "verified",
    "force": "statutory",
    "note": "eyvan / veranda enters at FULL area, not reduced. INERT IN V1."
  },
  {
    "field": "area.measurement_plane",
    "value": "finished inner face of walls and partitions, at floor level, skirtings excluded",
    "unit": "definition",
    "src_key": "az_area_rules_2012",
    "ref": "cl. 3.2",
    "conf": "verified",
    "force": "statutory",
    "note": "THE ONLY AREA CLAUSE THAT BINDS V1. Note the mismatch: ADR 0001 erodes by t_int/2 from a centreline, yielding the STRUCTURAL inner face. Finishes are typically 10-20 mm per face, so publishing the structural figure as `ümumi sahə` systematically overstates area. Flagged for the Area measurement convention ticket."
  },
  {
    "field": "area.mansard_low_height_coefficient",
    "value": 0.7,
    "unit": "coefficient",
    "src_key": "az_area_rules_2012",
    "ref": "cl. 3.8",
    "conf": "verified",
    "force": "statutory",
    "note": "Applies to the part of a mansard apartment with ceiling height below 2.7 m; that part may not exceed 50% of the apartment's total area. INERT IN V1 — no ceiling height in the geometry model."
  },
  {
    "field": "area.understair_exclusion_clear_height",
    "value": 1600,
    "unit": "mm",
    "src_key": "az_area_rules_2012",
    "ref": "cl. 3.8",
    "conf": "verified",
    "force": "statutory",
    "note": "Area under an intra-apartment stair is excluded where clear height to the underside of the structure is 1.6 m or less. INERT IN V1."
  }
]
```

## 6. `sources` block

Shape matches `data/standards/room-constraints.json` §`sources`. **Do not merge
this yourself** — another session owns that file.

```jsonc
{
  "az_azdtn_2_7_2_2021": {
    "title": "AzDTN 2.7-2 «Yaşayış binaları. Layihələndirmə normaları» (Residential buildings. Design norms)",
    "issuer": "Azərbaycan Respublikasının Dövlət Şəhərsalma və Arxitektura Komitəsi (State Committee on Urban Planning and Architecture)",
    "date": "approved by Kollegiya decision No. 03 of 2021-11-30; in force from 2021-11-30; State Register of Legal Acts No. 15202111300003",
    "url": "https://arxkom.gov.az/qanunvericilik/normativler/binalarin-muhendis-sistemleri/zhilye-zdaniya",
    "url_alt": "https://e-qanun.az/framework/48625",
    "licence": "Azerbaijani state normative legal act, freely published by the issuer as RƏSMİ NƏŞR (official publication) and in the State Register of Legal Acts. No open licence is asserted; individual values cited, no tables reproduced.",
    "force": "statutory",
    "force_note": "A technical normative legal act registered in the State Register of Legal Acts. Şəhərsalma və Tikinti Məcəlləsi Art. 14.3 makes conformity with construction normative documents mandatory. On commencement it TERMINATED the legal force of СНиП 2.08.01-89* «Жилые здания» on the territory of Azerbaijan — stated on the document's own cover. Scope: new multi-apartment residential buildings up to 75 m; above 75 m requires project-specific special technical conditions.",
    "reusable": false,
    "read_first_hand": true
  },
  "az_azdtn_2_7_3_2023": {
    "title": "AzDTN 2.7-3 «Fərdi yaşayış evləri. Layihələndirmə normaları» (Individual residential houses. Design norms)",
    "issuer": "Azərbaycan Respublikasının Dövlət Şəhərsalma və Arxitektura Komitəsi",
    "date": "approved by Kollegiya decision No. 3-35/3-2-6/2023 of 2023-11-21; in force from 2023-12-06; State Register No. 15202311235326; first edition",
    "url": "https://arxkom.gov.az/qanunvericilik/normativler/binalarin-muhendis-sistemleri/azdtn-27-3-ferdi-yasayis-evleri-layihelendirme-normalari",
    "licence": "As above.",
    "force": "statutory",
    "force_note": "Applies to individual (single-family) houses of not more than 3 above-ground storeys — NOT the multi-apartment case our corpus contains. Carried here only as independent corroboration of the 1:8 ratio and the wet-room extract rates.",
    "reusable": false,
    "read_first_hand": true
  },
  "az_area_rules_2012": {
    "title": "Tikinti obyektlərinin sahəsinin və həcminin hesablanması qaydaları (Rules for calculating the area and volume of construction objects)",
    "issuer": "Azərbaycan Respublikasının Dövlət Şəhərsalma və Arxitektura Komitəsi",
    "date": "approved by Kollegiya decision No. 07 of 2012-12-04; registered 2012-12-14, No. 15201212040007; in force from 2012-12-15",
    "url": "https://e-qanun.az/framework/25005",
    "licence": "Azerbaijani state normative legal act on the official State Register of Legal Acts portal. Individual values cited; the coefficient set is stated per value, the source's tables are not reproduced.",
    "force": "statutory",
    "force_note": "Status confirmed `Qüvvədədir` (in force) against the register's own metadata on 2026-08-20. This — not AzDTN 2.7-2 — is where the AZ area-calculation rules and the balcony/loggia coefficients live; AzDTN 2.7-2 carries no area appendix.",
    "reusable": false,
    "read_first_hand": true
  },
  "az_housing_code": {
    "title": "Azərbaycan Respublikasının Mənzil Məcəlləsi (Housing Code of the Republic of Azerbaijan)",
    "issuer": "Milli Məclis (Parliament of the Republic of Azerbaijan)",
    "date": "2009 (as amended)",
    "url": "https://frameworks.e-qanun.az/0/c_c_19.html",
    "licence": "Statute published on the official state legal information portal e-qanun.az.",
    "force": "statutory",
    "force_note": "Primary legislation. Art. 12.5 defines `yaşayış sahəsinin ümumi sahəsi` for housing-law purposes and EXCLUDES balconies and eyvans outright — which CONTRADICTS the 0.3/1.0 inclusion in az_area_rules_2012 cl. 3.8. Two in-force AZ definitions of `total area` for two different purposes. See section 4.3.",
    "reusable": false,
    "read_first_hand": true
  },
  "cis_msn_2_04_05_95": {
    "title": "МСН 2.04-05-95 / DTN 2.04-05-95 «Естественное и искусственное освещение» (Natural and artificial lighting)",
    "issuer": "CIS Intergovernmental Council on Construction; brought into force in Azerbaijan by decision No. 13 of 2005-12-15 of the State Committee on Construction and Architecture",
    "date": "1995; in force in Azerbaijan from 2006-01-01, replacing СНиП II-4-79",
    "url": null,
    "url_of_twin_read": "https://files.stroyinf.ru/Data2/1/4294854/4294854801.htm",
    "licence": "Not obtained from any Azerbaijani-hosted source. The Russian twin text is mirrored on commercial aggregators carrying a 'free for familiarisation, not for commercial use' notice; individual normative values are cited, no text redistributed.",
    "force": "statutory",
    "force_note": "IN FORCE in Azerbaijan as a CIS interstate document retained under Cabinet Decision No. 217 of 2008-09-18. AzDTN 2.7-2 cl. 9.15 delegates all normalised daylight indicators (KEO) to it. WE DID NOT OBTAIN THE МСН TEXT — see section 7. Values attributed to this key were read in its Russian twin СНиП 23-05-95* and are therefore `reported`, never `verified`. Two document numbers, two issuing bodies; near-identical is not identical, and we have not checked clause by clause.",
    "reusable": false,
    "read_first_hand": false
  },
  "ru_snip_23_05_95": {
    "title": "СНиП 23-05-95* «Естественное и искусственное освещение»",
    "issuer": "Minstroy of Russia / Gosstroy",
    "date": "1995, with amendments",
    "url": "https://files.stroyinf.ru/Data2/1/4294854/4294854801.htm",
    "licence": "Freely mirrored normative text; individual values cited, no tables reproduced.",
    "force": "superseded",
    "force_note": "The Russian twin of МСН 2.04-05-95, read first-hand to obtain the KEO figures AZ's own lighting norm is presumed to carry. Superseded in Russia by СП 52.13330. Carried ONLY as the read-source behind the `reported` KEO values; it is NOT the instrument in force in Azerbaijan.",
    "reusable": false,
    "read_first_hand": true
  },
  "su_snip_2_08_01_89": {
    "title": "СНиП 2.08.01-89* «Жилые здания» (Residential buildings)",
    "issuer": "Gosstroy USSR; amendments 1-4 to 2000 (Amdt. 4 — Gosstroy RF res. No. 112 of 2000-11-20)",
    "date": "1989, 2000 reissue with amendments 1-4",
    "url": "https://files.stroyinf.ru/Data2/1/4294854/4294854790.htm",
    "licence": "Soviet-era normative text, freely mirrored. Read to establish provenance of the 1:5.5 figure; not the source of any AZ value.",
    "force": "superseded",
    "force_note": "SUPERSEDED IN AZERBAIJAN — legal force on AZ territory terminated 2021-11-30 by AzDTN 2.7-2. Separately repealed in Russia by Gosstroy RF res. No. 109 of 2003-06-23. Carried here ONLY to explain where the reported 1:5.5 to 1:8 band came from and to document that it no longer binds AZ. NO value in our data may cite this source as current AZ practice.",
    "reusable": false,
    "read_first_hand": true
  },
  "ru_sp_54_13330_2022": {
    "title": "СП 54.13330.2022 «СНиП 31-01-2003 Здания жилые многоквартирные» (with amendments 1, 2)",
    "issuer": "Minstroy of the Russian Federation",
    "date": "in force from 2022-06-14",
    "url": "https://tiflocentre.ru/documents/sp_54.13330.2022.php",
    "licence": "Russian Federation normative text, freely published.",
    "force": "voluntary",
    "force_note": "NO LEGAL FORCE IN AZERBAIJAN. A Russian Federation national document; the AZ chain of authority admits only Soviet-era SNiP/GOST retained by the 1992 decision and CIS interstate МСН/МСП/ГОСТ. Present here as comparative context ONLY — it is the document that restored the 1:5.5 cap (cl. 7.13) that AZ does not have. Modelling Azerbaijan on СП 54.13330 would be legally wrong.",
    "reusable": false,
    "read_first_hand": true
  }
}
```

---

## 7. What I could NOT obtain

Stated plainly, per the ticket.

1. **The text of МСН 2.04-05-95 / DTN 2.04-05-95 from any Azerbaijani source.**
   This is the real gap. It is the document AzDTN 2.7-2 cl. 9.15 delegates all
   normalised daylight indicators to, and it is **in force in Azerbaijan** — that
   much is verified from the official in-force list. But ARXKOM does not publish
   its text on the normativler pages, and no `.az` government host serving it was
   reachable. The KEO figures in §2.3 and §5 come from **first-hand reading of
   its Russian twin СНиП 23-05-95\***, cross-checked against three later Russian
   editions that carry the same 0.5 % unchanged — which is why they are labelled
   **`reported`** and keyed to `cis_msn_2_04_05_95` with the read-source named.
   **Do not promote them to `verified` without an Azerbaijani-published copy.**
   This does not block the profile: `win.area_ratio` is fully sourced from the
   ratio rule, which is the form our engine consumes, and KEO is not implemented
   in v1.
2. **Whether AzDTN 2.7-2 cl. 9.12/9.13 bind a `taxça-mətbəx`.** This is an
   ambiguity *in the norm*, not a failure of search — see §3.2. Both readings are
   textually available. Resolved as an `engine_choice` and labelled as one.
3. **A definition of `yaşayış sahəsi` as a summed metric.** Absent from the 2012
   Qaydalar (verified by grep of the full text) and used only loosely in
   AzDTN 2.7-2. I believe it does not exist as a published AZ design metric; §4.1
   argues that from the pattern across four instruments, but "does not exist" is
   an argument from absence and is labelled as such.
4. **The official in-force normative list from a government host.** The list
   corroborating МСН 2.04-05-95's commencement came via a state water utility
   re-hosting it, not from arxkom.gov.az. Its content is consistent with the
   primary documents (it correctly showed СНиП 2.08.01-89* as then-current,
   later repealed in 2021), but provenance is secondary.
5. **Приказ Минстроя РФ 854/пр** (the Russian 0.5 / 1.0 / 0.3 / 0.3 coefficients
   under 214-ФЗ) was read only via full-text mirrors, and two mirrors disagree on
   whether the 1.0 attaches to veranda or terrace. Irrelevant to AZ — the AZ
   coefficients come from az_area_rules_2012 cl. 3.8, read first-hand — and
   recorded here only so nobody re-treads it.

**A caution worth passing on.** One fetch of a paywalled aggregator page for
СНиП 2.08.01-89* returned **fabricated clause text**, with an invented clause
number and invented coefficients, rather than an error. Every value in this file
was taken from a source whose full text was retrieved and read; where a mirror
was the only route, a second independent mirror was checked for identical
wording. Paywalled or JS-gated legal aggregators should be treated as adversarial
inputs, not as sources.

---

## 8. Copyright posture

Per `docs/research/dimensional-standards.md` §7.6, and observed here:

- **Individual values with per-value citations** — §7.6 item 1. Every number
  above carries its own clause reference.
- **Short verbatim clause quotations for provenance** — §7.6 item 4. Four short
  clauses are quoted, each for provenance of a specific value.
- **No source table reproduced with its own selection and ordering** — §7.6
  item 5. AzDTN 2.7-2 Table 6 was *read*; two values were re-derived from it and
  cited individually. The table's row set, column set and ordering are not
  reproduced. The coefficient table in §4.2 is a three-row restatement of one
  clause's prose, arranged by us.
- **No systematic extraction of one work's tables into a data file** — §7.6
  item 7. The §5 value list draws on five different instruments and is organised
  by *our* field names, not by any source's structure.
- **No source PDFs committed** — §7.6 item 8. Documents were fetched to a
  scratch directory for reading and are not added to the repo.
