# AZ region profile — the drawing convention

Partial findings for *The Azerbaijani region profile*
(`docs/wayfinder/tickets/25-the-azerbaijani-region-profile.md`), items **4**, **5**
and **6**, plus the ticket's open question **"what language the drawing is in"**.

Consumed by `docs/spec/annotation.md` — §1 (decimal separator), §6 (schedules),
§7 step 2 (room-tag fallback), §8 (opening type marks), §10 (title block, general
notes), §11 (`DIMDSEP`, DXF version).

Sibling partials in this directory are owned by other sessions. This file touches
nothing else; `data/standards/room-constraints.json` is merged elsewhere.

---

## 0. Headline

**The single most important finding is that Azerbaijan has its own
Azerbaijani-language drafting standards, and they are freely published by the
state.** The profile does not have to be built out of Russian GOSTs labelled
`reported`. `AZS ГОСТ 21.101-2010` and `AZS ГОСТ 21.501-2010` are Azerbaijani
state standards, downloadable as PDFs from the issuing committee, and both were
**read first-hand for this document**. That moves items 4, 5 and the language
question from `reported` to `verified`.

Four answers, in one line each:

1. **Decimal separator: comma.** `DIMDSEP = 44`. Drafting standard and civil
   locale agree; there is no disagreement to flag. No thousands separator.
2. **Room-name abbreviations: no published set exists, in any of the three
   candidate languages.** This is a finding, not a gap. Two independent standards
   families prescribe the *same* different fallback — **room number + room
   schedule** — and we already ship that schedule.
3. **Opening keys are two-level**: a sequential plan mark in a circle, and a
   product designation (`ДГ 21-9`, `ОР 15-15`) in the schedule. Every opening
   dimension is even; every *block* height is odd.
4. **Language: Azerbaijani.** Required by decree for submitted documentation,
   and — because no room-name abbreviation set exists in any language — choosing
   it forces us to invent nothing.

**One consequence lands outside this slice and is urgent:** the Azerbaijani
alphabet is unrepresentable in DXF R2000. See §5.

---

## 1. Decimal separator

### The values

| field | value | src_key | ref | conf | note |
|---|---|---|---|---|---|
| `draw.decimal_separator` | `,` | `azs_21101_2010` | cl. 5.12 | verified | Level marks in metres to 0,001 precision; comma throughout the Azerbaijani text. |
| `draw.decimal_separator` (corroboration) | `,` | `gost_r_21101_2020` | cl. 5.4.1, 5.4.3 | verified | The one **explicit normative sentence** in the whole family: metre dimensions carry two decimals *"отделенными от целого числа запятой"*; level marks three decimals, same wording. |
| `draw.dimdsep` | `44` (`ord(',')`) | — | — | derived | From `decimal_separator`. Round-trip through `ezdxf` at R2010 confirmed on this machine. |
| `draw.thousands_separator` | *none* | `azs_21501_2010` | Annex 2 example plan | verified | Millimetre dimensions are printed ungrouped (`4000`, `23400`). **Do not enable grouping** — CLDR gives `.` as the `az` group separator, so a grouped `4.400` would read as 4,4 to a stop-decimal reader. |
| `locale.decimal_separator` | `,` | `cldr_az` | `numbers/latn/symbols/decimal` | verified | Read the raw XML myself: `<decimal>,</decimal>`, `<group>.</group>`. |
| `draw.area_format` | `16,06 m²` | `azs_21501_2010` | cl. 2.3.2(6) | verified | Area in the **lower-right corner of the room, underlined**. Two-decimal convention is figure-derived, not clause-derived — see the caveat below. |
| `draw.level_mark_format` | `+4,990` | `azs_21501_2010` | cl. 3.3.7 + Annex 2 | verified | Three decimals, comma. Our `FFL ±0.000` in annotation §2 must become **`±0,000`**. |

### Do drafting practice and the civil locale agree?

**Yes. Both are the comma, and no source found says otherwise.** The ticket asked
for the disagreement to be flagged; there is none to flag.

### Two honest caveats

- **No clause anywhere states "room areas are printed to two decimals."** The
  two-decimal convention is read off the standards' own worked example plans
  (`AZS ГОСТ 21.501-2010` Annex 2; `ГОСТ 21.501-2018` Fig. Б.2, where the areas
  read `11,02 / 17,25 / 8,69`). The *separator* is clause-backed; the *precision*
  is figure-backed. Annotation §1 already fixes 2 dp independently, so this
  corroborates rather than decides.
- `ГОСТ 2.307-2011`, the dimensioning standard the ticket named, **contains no
  clause naming the separator at all.** Every decimal in its own examples is a
  comma (17 comma-decimals, 0 point-decimals across the full text), but that is
  evidence, not a rule. The citable rule is in the SPDS layer, not ESKD.

### A finding that changes the spec

**`DIMDSEP` is inert on our sheets.** Annotation §11 sets `dimdec = 0`, so a
rendered dimension is `4400` with no decimal for the separator to sit in —
verified by rendering both `DIMDEC = 0` and `DIMDEC = 2` through ezdxf and reading
the text back out of the anonymous block. The separator's *real* consumers are
strings we format ourselves: the room-tag area, the level mark, and the preview's
metre dimensions. Set `DIMDSEP` anyway — it is correct and it matters the moment
someone edits the file downstream — but the profile field must not be plumbed
only to `DIMDSEP` or it will silently never fire.

---

## 2. Room-name abbreviations

### The answer: there is no published set, in any candidate language

Asked in all three languages, and the answer is negative in all three. Stating it
plainly, as the brief requires:

| language | published room-name abbreviation set? | evidence |
|---|---|---|
| **Azerbaijani** | **No.** | `AZS ГОСТ 21.101-2010` Əlavə D, Cədvəl D.1 is *the* published Azerbaijani drawing-abbreviation list (~55 entries), invoked by cl. 5.3. I read the whole table. It contains **one** term from our room set — `sanitar qovşağı → san. qov.` Nothing for otaq, yataq otağı, mətbəx, vanna, dəhliz, eyvan, lodjiya, anbar. |
| **Russian** | **No.** | `ГОСТ 2.316-2008` cl. 4.4 *forbids* abbreviation in drawing captions except those listed in its Annex A — and Annex A contains **zero** room-type words. `ГОСТ Р 21.101-2020` Annex E extends that list and yields exactly one of ours (`сан. узел`). `ГОСТ 7.12-93` is bibliographic and out of scope by its own cl. 1. |
| **English** | **Effectively no, and unusable.** | The one published set is US NCS UDS Module 5, which is **paywalled** — only the introduction is free, so no values were obtained and none are stated here. Its own §5.1.2 says *"It is not the objective of the Module to encourage the use of abbreviations… When the meaning of an abbreviation is in doubt, spell it out!"* No free federal equivalent republishes it: GSA, VA and USACE all adopt NCS by reference and publish nothing. |

So annotation §7's degradation ladder step 2 — *"substitute the region profile's
standard abbreviation (`WC`, `ST`, `UT`)"* — **has no source to draw on.** Those
three examples are not published abbreviations; they are plausible-looking
inventions, and the spec's own rule ("a published abbreviation, never a
truncation") forbids shipping them.

### What the standards prescribe instead, and it is better

Two independent standards families, which share no lineage, prescribe the same
fallback — and it is not abbreviation:

| field | value | src_key | ref | conf | note |
|---|---|---|---|---|---|
| `draw.room_tag_overflow` | `number_plus_schedule` | `azs_21501_2010` | cl. 2.3.2(6) | verified | *"Yerləşkələrin … adlarının … forma 2 üzrə eksplikasiyada göstərilməsinə yol verilir. Bu halda planlarda yerləşkələrin … əvəzinə onların **nömrələri** yazılır."* — the names may go in a Form 2 schedule; in that case the plan carries **numbers instead of names**. |
| `draw.room_schedule_optional_residential` | `true` | `azs_21501_2010` | cl. 2.3.2(6) | verified | *"Yaşayış binaları üçün yerləşkələrin eksplikasiyasının tərtib edilməsi vacib şərt deyildir."* — for residential buildings the room schedule is **not mandatory**. It is permitted, not required; we ship one anyway. |
| `draw.room_number_marker` | circle, Ø 12–15 mm | `gost_21501_2018` | cl. 5.3.2 е) | verified | The RF edition sizes the room-number circle. The AZ 2010 edition states the substitution rule but not the circle diameter. |
| corroboration, non-SPDS | `number + name in a table on the same sheet` | `iso_4157_2` | cl. 4.3.1–4.3.2 | verified | *"In small rooms, it is sufficient to indicate only the room numbers… However, the room names of such small rooms shall be indicated in tabular form on the same drawing sheet."* Also: room numbers and names **shall be underlined**. |

**This is the recommendation for annotation §7.** Replace ladder step 2 with:

> 2. Substitute the room's **schedule reference** (`R03`) for the room name, the
>    full name being carried in the room schedule on `A-102`.

It costs nothing to build — the room schedule and its `Ref` column already exist
in annotation §6, and `draw.schedule_complete` already asserts the join is total
in both directions, which is exactly the property that makes the substitution
safe. It is citable to two independent standards. And it removes the only step in
the whole spec that required inventing data.

ISO 4157-2 adds a rung below that we should note and **not** build: a *symbol*
(WC pan, basin) may stand in for the name of a small room. Out of v1 scope —
annotation §2 states fixtures are not modelled.

### Azerbaijani room names, for the tag itself

Needed regardless of the abbreviation answer. The Azerbaijani technical term for
*помещение* is **`yerləşkə`**, not `otaq` — verified throughout
`AZS ГОСТ 21.501-2010`. Per-room names are **not** fixed by the drafting
standards (they fix the *rule*, not the vocabulary), so these must come from the
AzDTN residential design norm and belong to whichever partial owns the room
table — flagged as a **gap this slice did not close**, not filled by guesswork.

The Russian canonical names *are* sourced, from `СП 54.13330.2022` §3.1, and are
recorded here only as the cross-check another partial may want: `общая жилая
комната` / `спальня` / `кухня` (3.1.16) / `кухня-столовая` (3.1.18) / `ванная
комната` (3.1.14) / `уборная` (3.1.36) / `совмещённый санузел` / `передняя`
(3.1.27 — *not* `прихожая`, which is colloquial) / `кладовая` / `балкон` (3.1.2)
/ `лоджия` (3.1.19).

### What Azerbaijani abbreviations we *did* get, and where they are useful

`AZS ГОСТ 21.101-2010` Əlavə D is a real, official, free, Azerbaijani-language
abbreviation table — just not for room names. Cited per value, only for the
handful the annotation spec actually consumes:

| use in annotation spec | Azerbaijani | src_key | ref | conf |
|---|---|---|---|---|
| §2 `FFL` level annotation | `t.d.s.` (təmiz döşəmə səviyyəsi) | `azs_21101_2010` | Əlavə D, Cədvəl D.1 | verified |
| ground level, if ever needed | `y.s.` (yerin səviyyəsi) | `azs_21101_2010` | Əlavə D | verified |
| §6 schedule quantity column | `əd.` (ədəd) | `azs_21101_2010` | Əlavə D | verified |
| §9 scale in title block | `M` (miqyas) | `azs_21101_2010` | Əlavə D | verified |
| storey reference | `mər.` (mərtəbə) | `azs_21101_2010` | Əlavə D | verified |
| area column heading | `sh.` (sahə) | `azs_21101_2010` | Əlavə D | verified |
| combined sanitary unit | `san. qov.` (sanitar qovşağı) | `azs_21101_2010` | Əlavə D | verified |

Əlavə D is marked **`tövsiyə olunan`** (recommended), so these are permitted, not
mandated. Per §7.6 the table is not reproduced — seven values our spec names,
selected by our schema, not the source's ordering.

### A title-block conflict this surfaces

`AZS ГОСТ 21.101-2010` Əlavə A defines the Azerbaijani **drawing-set marks**:
architectural working drawings are **`MH`** (Memarlıq həlli) or **`MT`**
(Memarlıq-tikinti həlləri), where US practice says `A`. Annotation §9/§10 numbers
our sheets `A-101` / `A-102` on the US NCS convention, and §11 layers them
`A-WALL` etc. on AIA. **A drawing issued in Azerbaijani to an Azerbaijani builder
with a US sheet number is internally inconsistent.** Flagged, not decided — sheet
numbering is annotation §9's, and the layer names have a separate justification
(§11: "a Practitioner recognises the real ones on import"). My view: layer names
are a machine-facing interchange convention and should stay NCS; the *sheet
number*, which the builder reads, is the one worth reconsidering.

---

## 3. Opening catalogue keys

### The scheme is two-level, and the spec currently models only one level

This is the structural finding. Post-Soviet practice separates:

- the **plan mark** — a short sequential label in a circle, joining plan to
  schedule; and
- the **product designation** — `ДГ 21-9`, `ОР 15-15` — which encodes the size
  and names the standard, and lives in a schedule column.

Annotation §8 conflates them into one string (`D1`, `W2`). Both are needed: the
mark is what fits beside an opening at 2.5 mm; the designation is what tells a
builder what to buy.

| field | value | src_key | ref | conf | note |
|---|---|---|---|---|---|
| `draw.window_plan_mark` | `ОК1`, `ОК2`, … | `gost_21501_2018` | cl. 5.4.2, footnote | verified | *"Обозначения типов заполнения оконных проемов составляют из буквенного обозначения **ОК** и порядкового номера … (например, ОК1, ОК2)"*. **No hyphen** — `ОК-1` is common office practice but is not what the standard writes. |
| `draw.door_plan_mark` | bare sequential number | `gost_21501_2018` | cl. 5.3.2 г) | verified | For doors the standard gives **no letter prefix at all**. Confirmed against the standard's own worked example (Fig. В.3), where doors are `1, 2, 3…` and windows are `ОК1…ОК5`. There is no `Д1` in GOST 21.501-2018. |
| `draw.opening_mark_marker` | circle, Ø 5 mm | `azs_21501_2010` | cl. 2.3.2(4) | verified | *"Darvaza və qapıların boşluqlarının mövqe işarələməsinin diametri **5 mm** olan dairəciklərdə göstərilməsinə yol verilir."* The RF 2018 edition widens this to Ø 5–7 mm; **the Azerbaijani edition says 5**, and the Azerbaijani edition is the operative one. |
| `draw.opening_schedule_form` | GOST 21.101 Annex 7, form 7 or 8 | `azs_21501_2010` | cl. 2.3.6(2) | verified | The AZ standard defers the schedule layout to `ГОСТ 21.101` forms 7/8. |
| `draw.opening_schedule_columns` | `Poz. \| Obozn. \| Naimenovanie \| Kol. \| Massa \| Primech.` | `gost_21501_2018` | Fig. В.3 | verified | The `Примечание` column carries the **opening width × height** (`2070×1310`). |

**Consequence for annotation §6.** Our door and window schedule columns
(`Mark | Type | Structural opening W × H | …`) are close but not congruent: the
published form puts the opening size in a *notes* column and adds a mass column
we cannot populate. Our columns are defensible — they are ours, chosen by our
schema, which is also the right copyright posture (§7.6 item 13). Worth a
deliberate note in the spec that the divergence is chosen, not accidental.

### The designation scheme, re-derived as a rule

Not transcribed from any table — stated as the composition rule, per §7.6 item 12.

**Doors** (`ГОСТ 6629-88` cl. 1.1, 1.5): `[kind][type] [H]-[W][suffixes]`.
- kind: `Д` = complete door block; `П` = leaf only.
- type: `Г` solid, `О` glazed, `К` glazed double-swing, `У` solid-core reinforced
  **for apartment entrances** (cl. 1.1 says so in terms).
- `H` and `W` are the nominal **opening** in decimetres — the standard's own
  diagram labels them *"Высота проема, дм" / "Ширина проема, дм"*. They describe
  the hole, not the block and not the leaf.
- suffixes: `Л` left; `П` **with threshold, not "right"** — right-hand is the
  unmarked default, confirmed by the standard's own gloss of `ДО 21-10П`; `Н`
  rebated.

So `ДГ 21-9` = solid internal door, opening 2100 × 900. The ticket's example form
is confirmed.

**External doors** (`ГОСТ 24698-81` cl. 1.1, 1.5): same skeleton, type `Н`
entrance/vestibule, `С` service, `Л` hatches. Example strings the standard itself
prints: `ДН21-9ЛП`, `ДН24-15К`.

**Windows** (`ГОСТ 11214-86` cl. 1.1, 1.6): `[О|Б][С|Р] [H]-[W][letters]` — `О`
window, `Б` balcony door; `С` paired sashes, `Р` separate sashes; `H`-`W` again
the opening in decimetres. **Decimetre groups can be fractional** — the standard
prints `ОС 15-13,5` and `БС 22-7,5`. A key string must tolerate a comma, and a
parser that casts dm to `int` loses 1350 and 750.

### The residential subset

Room assignment is **ours**, not the standards': `ГОСТ 6629-88` names no rooms
except type `У` for apartment entrances (cl. 1.1) and a sanitary-cabin allowance
(cl. 2.6). Flagged as `derived` for that reason.

| use | key string | opening (mm) | src_key | ref | conf |
|---|---|---|---|---|---|
| bathroom / WC | `ДГ 21-7` | 2100 × 700 | `gost_6629_88` | черт. 2, Прил. 1 черт. 4 | derived (size verified; room mapping ours) |
| kitchen, small bedroom | `ДГ 21-8` | 2100 × 800 | `gost_6629_88` | as above | derived |
| bedroom, living room | `ДГ 21-9` | 2100 × 900 | `gost_6629_88` | as above | derived |
| living room, glazed | `ДО 21-9` | 2100 × 900 | `gost_6629_88` | as above | derived |
| apartment entrance | `ДУ 21-9` | 2100 × 900 | `gost_6629_88` | cl. 1.1, 1.5 | verified (type is clause-stated for apartment entrances) |
| building entrance | `ДН 21-13` | 2100 × 1300 | `gost_24698_81` | Прил. 1, черт. 1 | derived |
| living room window | `ОР 15-15` | 1500 × 1500 | `gost_11214_86` | Прил. 1 черт. 1 | derived |
| bedroom window | `ОР 15-12` | 1500 × 1200 | `gost_11214_86` | as above | derived |
| kitchen window | `ОС 12-9` | 1200 × 900 | `gost_11214_86` | as above | derived |
| balcony door | `БС 22-7,5` | 2200 × 750 | `gost_11214_86` | as above | derived |

Sizes that exist in `ГОСТ 6629-88`: heights **21 and 24 dm only**; 21-series
widths 7, 8, 9, 10, 12, 13 dm. **There is no 20 dm or 23 dm size** — `20-7`
appears only inside a cl. 1.5 *example string* and in no size drawing. Do not
ship it.

### Opening vs block vs leaf — and this is where the even-mm rule bites

| relationship | value | src_key | ref | conf |
|---|---|---|---|---|
| door opening width | nominal + 10 mm | `gost_6629_88` | Прил. 1 черт. 4 | verified |
| door opening height | 2070 (21 dm) / 2370 (24 dm) | `gost_6629_88` | Прил. 1 черт. 4 | verified |
| door block width | nominal − 30 (single) | `gost_6629_88` | черт. 2 | verified |
| door **block height** | **2071 / 2371** | `gost_6629_88` | cl. 1.4, черт. 2 | verified |
| door leaf width | nominal − 100 | `gost_6629_88` | черт. 2 | verified |
| door leaf height | 2000 / 2300 | `gost_6629_88` | черт. 2 | verified |
| window opening | nominal + 10 both axes | `gost_11214_86` | Прил. 1 черт. 1 | verified |
| window block | nominal − 30 wide, − 40 high | `gost_11214_86` | черт. 1 | verified |

### Even-millimetre verdict — the hard filter

> **PASS, conditionally: every *opening* dimension in the GOST series is an even
> number of millimetres. Every *block* height is odd. Ship openings; never key
> off block sizes.**

- Door nominal openings 700 / 800 / 900 / 1000 / 1200 / 1300 / 2100 / 2400 — even.
- Door openings as drawn 710 / 810 / 910 / 1010 / 1210 / 1310 / **2070** / 2370 — even.
- Window openings 610 / 760 / 910 / 1210 / 1360 / 1510 / 1810 / 2110 / 2210 — even.
- **Odd, and quarantined:** `2071` / `2371` door block heights (`ГОСТ 6629-88`
  cl. 1.4 names 2071 explicitly); `2085` / `2385` external door blocks; `2175` /
  `2375` balcony-door blocks; glass sizes `375 / 475 / 575 / 1305 / 1605`.

This is the same shape of hazard that killed DE, and it is survivable here only
because the *opening* series — the one the geometry model actually consumes — is
clean. Annotation §4.4 and §4.5 both dimension to **structural opening** edges, so
the spec is already on the right side of this. Worth an explicit assertion in the
profile test alongside `even_thickness_required`: **`even_opening_required`, over
opening dimensions only.**

Second, non-parity trap already noted: fractional decimetres in window marks.

---

## 4. THE DRAWING LANGUAGE — recommendation

> ## Recommendation: **Azerbaijani** (Latin script).

### The reasoning, strongest first

**1. It is legally required for the artefact's actual destination, and this is
the only hard fact in the whole question.**

The Urban Planning and Construction Code (2012) contains **zero** language
provisions — verified by full-text scan of all 99 articles. The requirement lives
one level down, in a single operative sentence:

> **"Ekspertizaya təqdim edilən tikinti layihələri dövlət dilində tərtib
> olunmalıdır."**
> — *Tikinti layihələrinin ekspertizadan keçirilməsi Qaydaları*, cl. 8.1,
> Presidential Decree of 17 November 2014

Construction projects submitted for state expertise **must be drawn up in the
state language**, and expertise is mandatory for essentially every permit-bearing
object (Code Art. 88.1). Backed generally by the State Language Law (No 365-IIQ,
2002) Art. 1.4, which puts record-keeping in *all legal persons* into Azerbaijani,
and Art. 14, which fixes the alphabet as Latin-script Azerbaijani.

Note honestly what this does *and does not* prove. Our output is stamped
`PRELIMINARY — NOT FOR CONSTRUCTION` (annotation §10) and is not going to
expertise. So cl. 8.1 does not bind us. What it establishes is **the register the
builder is trained on**: the drawings that constitute real documentation in
Azerbaijan are in Azerbaijani, so an Azerbaijani drawing is the one that looks
like a drawing to its reader.

**2. The builder is the constituency, and the ticket says so.** *Opening
placement rules* puts it flatly: opening catalogue keys "are not internal ids …
so a key is read by a builder." ADR 0006 chose AZ because "it is the actual
deployment context." A drawing whose room tags are in English is a drawing
produced for the person who wrote the generator, not the person holding it on
site. C2 makes the Practitioner the standard, and the Practitioner here is
Azerbaijani.

**3. And the usual argument against it does not hold.** The brief anticipated the
trap: *"if the published abbreviation set only exists in Russian, choosing
Azerbaijani means inventing one, which this project forbids."* **That trap is not
armed.** §2 establishes there is no published room-name abbreviation set in
Russian, in English, or in Azerbaijani. Nobody has one. So the abbreviation
question does not discriminate between the languages at all — and the fallback
that *is* published (number + schedule) is language-neutral, because `R03` reads
the same in every language on the sheet.

Better still, Azerbaijani turns out to be the language with the **most** usable
published drafting vocabulary for our purposes, because `AZS ГОСТ 21.101-2010`
Əlavə D is free, official, and in Azerbaijani, and it supplies `t.d.s.`, `əd.`,
`M`, `mər.`, `sh.` — the abbreviations our title block and schedules actually
need. Choosing Russian would mean citing a foreign national standard to a
builder whose own state has published the translation.

### Why not the other two

**Russian.** It has the deepest corpus and it is genuinely still in professional
use — ARXKOM's own live register is majority-Russian (31 of 47 documents in the
structures category carry Cyrillic titles; the older consolidated register runs
СНиП 137 / ГОСТ 418 against AzDTN 13), and Azerbaijani drafting textbooks cite
`ГОСТ 2.317-69` by its Cyrillic designation with no Azerbaijani equivalent
offered. So the *reference* corpus a professional consults is Russian. But the
*deliverable* is not: that is the distinction, and it is the one that matters
here, because we are producing a deliverable and not a reference. Choosing
Russian also picks a fight with the State Language Law for no gain, and it is
strictly worse in DXF R2000 than Azerbaijani is (§5 — cp1251 cannot encode `²`).

**English.** The only real argument for it is that it is free of every encoding
problem in §5, and that our internal room taxonomy is already English
(`LIVING_ROOM`, `KITCHEN_DINING`). Both are engineering conveniences, and CLAUDE.md
is explicit that ease of implementation is never the reason. An English drawing
is not what an Azerbaijani builder is issued. It also has no published
abbreviation set we can lawfully use — the one that exists is paywalled and its
own text discourages abbreviating.

### What it costs, stated honestly

1. **It costs the DXF R2000 floor.** This is the real price and it is not small —
   see §5. R2000 cannot represent `ə`. We must target R2007+.
2. **It costs SHX fonts.** Every stock AutoCAD SHX font lacks the Azerbaijani
   letters. The text style must name a TrueType font.
3. **It leaves a vocabulary gap this slice did not close.** The drafting
   standards fix the *rule* for room naming, not the *words*. Azerbaijani
   per-room names must come from an AzDTN residential norm; I did not obtain one.
   Until they do, the room tag has no strings. **This is the one thing that could
   still overturn the recommendation** — if no Azerbaijani residential room
   vocabulary is published, the choice reopens.
4. **It makes the US sheet numbering incongruent** (§2 last note).
5. **It does not localise the layouts.** ADR 0006 consequence 1 already discloses
   that we draw Swiss-shaped plans to Azerbaijani conventions. Language is one
   more convention, and it must not be allowed to imply the layouts moved.

### Not in scope, but adjacent and worth handing on

`AZS ГОСТ 21.501-2010` cl. 2.3.2 states that for **residential** buildings the
area is annotated **as a fraction — living area over useful area**
(*"sahəni kəsr şəklində, surətdə yaşayış, məxrəcdə isə faydalı sahə göstərilir"*),
verified first-hand. That is ticket item 7 (*общая* vs *жилая*) appearing as a
concrete drawing convention, and it goes to *Area measurement convention*, not
here. It implies the room tag may need **two** area numbers, which would change
annotation §7.

---

## 5. DXF character encoding — measured on this machine

Everything in this section was run locally against `ezdxf` 1.4.4. Harnesses:
`experiments/az-drawing/dxf_encoding_probe.py`, `dxf_font_probe.py`.

### The finding

> **DXF R2000 cannot represent the Azerbaijani alphabet. Neither can any legacy
> code page. `docs/research/bim-cad-export-stack.md` names R2000 the hard floor;
> that floor is incompatible with an Azerbaijani drawing.**

| ver | lossless round-trip | how the text is stored |
|---|---|---|
| R2000 (AC1015) | **NO** | `\U+015e` escapes; ezdxf's own reader hands them back **undecoded** |
| R2004 (AC1018) | **NO** | as R2000 |
| R2007 (AC1021) | yes | native UTF-8 |
| R2010 (AC1024) | yes | native UTF-8 |
| R2018 (AC1032) | yes | native UTF-8 |

Code-page coverage of the Azerbaijani alphabet `ƏəĞğİıÖöŞşÜüÇç`, tested by
attempting to encode each letter:

| code page | missing |
|---|---|
| cp1254 (Turkish) | **`Ə` `ə`** |
| iso8859-9 | **`Ə` `ə`** |
| cp1250 | `Ə ə Ğ ğ İ ı` |
| cp1252 (ezdxf default) | `Ə ə Ğ ğ İ ı Ş ş` |
| cp1251 (Cyrillic) | **all fourteen** |
| utf-8 | none |

**The schwa is the whole problem.** `Ə` / `ə` (U+018F / U+0259) is essentially
unique to Azerbaijani and appears in **no** single-byte code page — not even the
Turkish one, which carries every other Azerbaijani letter. There is no legacy
encoding to fall back to.

### Three further measured consequences

- **Russian is *worse* at R2000, not better.** `cp1251` round-trips Cyrillic
  fine, but **cannot encode `²`** — so a Russian drawing at R2000 forces a choice
  between Cyrillic room names and the m² sign that every area string needs. Both
  work at R2010. Verified.
- **The downgrade path is the realistic failure.** Authoring at R2010 and saving
  down to R2000 — exactly what "R2000 is the hard floor" invites — re-escapes
  every Azerbaijani letter. Verified.
- **The escape is recoverable but not automatically.** `has_dxf_unicode()` is
  `True` and `decode_dxf_unicode()` restores the string exactly, but plain
  `ezdxf.readfile()` does not call it. A naive consumer displays the literal
  `\U+0259`. Also reported (not verified here): ezdxf emits `\x%02x` — *not* a
  DXF escape — for characters ≤ 0xFF that the code page cannot hold, which
  silently corrupts rather than escaping.

### Fonts, which is a separate problem from encoding

Reported, from the source agent's binary inspection of the shipped Autodesk
fonts: **every stock SHX font** (`txt`, `romans`, `simplex`, `isocp`, `isoct`,
`monotxt`, `complex`, `italic`, `romanc`) lacks `ə Ə` *and* `ğ Ğ ı İ ş Ş`. Even
`isocpeur.ttf` has the Turkish letters but no schwa. Verified by me: a `STYLE`
naming a TrueType font round-trips, `set_extended_font_data()` works, and ezdxf's
own renderer emits substantial glyph geometry for the Azerbaijani letters.

### What this obliges

| field | value | conf | note |
|---|---|---|---|
| `export.dxf_version_floor` | `R2007` (AC1021) | verified | Raised from R2000. Below this, Azerbaijani text is structurally unrepresentable. |
| `export.dxf_version_default` | `R2010` (AC1024) | verified | Unchanged from annotation §11 — already above the new floor, so the default is safe today. |
| `export.text_font` | a TrueType font, never an SHX | reported | Independent of encoding: a perfect UTF-8 file still renders boxes in `txt.shx`. |
| `export.downgrade_below_R2007` | forbidden | verified | Must be refused, not warned. |

Annotation §11 already writes R2010, so **nothing currently emitted is broken.**
What must change is the *stated floor* in `docs/research/bim-cad-export-stack.md`
§2.5 and the summary table, which say R2000. That claim was measured before any
region had a language; it was correct for the entities and wrong for the text.

The export research's line *"Non-ASCII (`²`) survived the round trip — R2000+ DXF
is unicode-capable"* is the specific sentence to correct. `²` is in cp1252, so
that test proved only that cp1252 works. It does not generalise, and for
Azerbaijani it is false.

---

## 6. What I could NOT obtain

- **Azerbaijani per-room vocabulary.** The drafting standards fix the naming
  *rule*, not the words. No AzDTN residential design norm giving `yataq otağı`,
  `mətbəx` etc. as normative room names was obtained. **This is the largest
  remaining gap in this slice** and it gates the room tag.
- **Any AZS/AzDTN opening standard.** Not found. The whole of §3 is Russian
  GOST, labelled accordingly. Per the ticket's binding rule these are named as
  the **ancestor** standards, `reported`/`derived`, never as Azerbaijani
  documents. The lineage is documented — `AzDTN 1.1-1` cl. 1.5(a) keeps
  ex-all-Union ГОСТ/СНиП in force in Azerbaijan as temporary until replaced,
  verified — but lineage is not identity.
- **Official status of the opening GOSTs.** `ГОСТ 6629-88` is **superseded by
  `ГОСТ 475-2016`** since 01.07.2017. Search prose also claims `11214-86` and
  `24698-81` were cancelled; unverified against a registry. **This matters**: if
  true, the size series in §3 is historical, and the live authorities
  (`23166-99`, `11214-2003`, `31173-2016`) fix **no opening grid at all** —
  `ГОСТ 23166-99` cl. 4.9 explicitly makes opening sizes a project decision. A
  discrete catalogue may therefore have to be `engine_choice` bounded by the old
  series rather than `verified` from a live standard. **Flagged as the open
  question in this slice.**
- **`docs.cntd.ru` was unreachable all session** (connection refused). Every
  Russian GOST text came from `meganorm.ru` / `files.stroyinf.ru` mirrors —
  full text, but not the issuer. No issuer-hosted GOST PDF was obtained.
- **NCS Module 5 tables** — paywalled; no English abbreviation values stated.
- **No real issued Azerbaijani drawing set** was inspected. The language finding
  rests on the decree, the standards and teaching materials, not on a drawing.
- **No first-hand AutoCAD test** of `\U+0259`; the ezdxf results are first-hand,
  the AutoCAD behaviour is reported.
- The web-search budget (200 calls) was exhausted partway through, which
  truncated the AzDTN hunt in particular.

---

## `sources`

Format matches `data/standards/room-constraints.json`. **Do not merge this block
directly** — another session owns that file.

```json
{
  "azs_21501_2010": {
    "title": "AZS ГОСТ 21.501-2010. Tikinti üçün layihə sənədləri sistemi. Memarlıq-tikinti işçi cizgilərinin işlənilməsi qaydaları",
    "issuer": "Azərbaycan Respublikası Dövlət Şəhərsalma və Arxitektura Komitəsi (ARXKOM)",
    "date": "approved by order 83 of 29.06.2010; in force by SCSMP order 120 of 12.08.2010",
    "url": "https://arxkom.gov.az/qanunvericilik/normativler/yasayis-ictimai-istehsalat-kend-teserrufati-binalari/tikinti-ucun-layihe-senedleri-sistemi-memerliq-tikinti-isci-cizgilerinin-islenilmesi-qaydalari",
    "licence": "freely published by the issuing state committee; no redistribution right asserted here",
    "force": "state_standard",
    "force_note": "Azerbaijani state standard, authentic Azerbaijani translation of the interstate ГОСТ 21.501-93. THE OPERATIVE DOCUMENT for architectural working drawings in Azerbaijan. Read first-hand for this research (51 pp).",
    "reusable": false
  },
  "azs_21101_2010": {
    "title": "AZS ГОСТ 21.101-2010. Tikinti üçün layihə sənədləri sistemi. Layihə və işçi sənədlərinə əsas tələblər",
    "issuer": "ARXKOM; prepared by «Azərmemarlayihə» Dövlət Baş Layihə İnstitutu",
    "date": "approved by ARXKOM order 33 of 17.03.2010; in force by SCSMP order 082 of 03.05.2010",
    "url": "https://arxkom.gov.az/qanunvericilik/normativler/yasayis-ictimai-istehsalat-kend-teserrufati-binalari/tikinti-ucun-layihe-senedleri-sistemi-layihe-ve-isci-senedlerine-esas-telebler",
    "licence": "freely published by the issuing state committee",
    "force": "state_standard",
    "force_note": "Authentic Azerbaijani translation of ГОСТ 21.101-97, stated in its own front matter. Carries Əlavə A (drawing-set marks) and Əlavə D (abbreviations, marked `tövsiyə olunan` = recommended). Read first-hand (52 pp).",
    "reusable": false
  },
  "az_expertise_rules_2014": {
    "title": "Tikinti layihələrinin ekspertizadan keçirilməsi Qaydaları",
    "issuer": "President of the Republic of Azerbaijan (decree under Urban Planning and Construction Code Art. 90.4)",
    "date": "2014-11-17",
    "url": "https://president.az/az/articles/view/13427",
    "licence": "official state publication, openly accessible",
    "force": "statutory_instrument",
    "force_note": "Cl. 8.1: construction projects submitted for expertise must be drawn up in the state language. Expertise is mandatory under Code Art. 88.1 for essentially every permit-bearing object. Does NOT bind our PRELIMINARY output; establishes the register the builder reads.",
    "reusable": false
  },
  "az_state_language_law_2002": {
    "title": "Azərbaycan Respublikasında dövlət dili haqqında Azərbaycan Respublikasının Qanunu, No 365-IIQ",
    "issuer": "Milli Məclis / President of the Republic of Azerbaijan",
    "date": "2002-09-30, consolidated through 2020 amendments",
    "url": "https://e-qanun.az/framework/1865",
    "licence": "official legal database, open",
    "force": "statutory",
    "force_note": "Art. 1.4 record-keeping in the state language across all legal persons; Art. 14 alphabet is Latin-script Azerbaijani; Art. 15.3 Cyrillic only in special cases. Contains NO article on technical documentation or standards — verified by full-text scan.",
    "reusable": false
  },
  "azdtn_1_1_1": {
    "title": "AzDTN 1.1-1. Tikinti normativ sənədləri sistemi",
    "issuer": "Azərdövləttikintikom",
    "date": "decision 6 of 30.12.1999, in force 01.01.2000",
    "url": "https://arxkom.gov.az/qanunvericilik/normativler/rehberedici-ve-metodiki-senedler/azdtn-11-1-1-tikinti-normalari-islenmesi-qaydalari",
    "licence": "freely published",
    "force": "mandatory_state_construction_norm",
    "force_note": "Cl. 1.5(a): former all-Union documents (СНиП, СН, ВСН, ГОСТ, ОСТ) remain part of Azerbaijan's construction normative system, treated as temporary until replaced. This is the lineage warrant for citing GOST as ANCESTOR — it is not a warrant for calling a GOST an Azerbaijani document.",
    "reusable": false
  },
  "gost_r_21101_2020": {
    "title": "ГОСТ Р 21.101-2020. СПДС. Основные требования к проектной и рабочей документации",
    "issuer": "Rosstandart (Russian national standard)",
    "date": "order 282-ст of 23.06.2020, in force 2021-01-01",
    "url": "https://meganorm.ru/Data2/1/4293720/4293720404.htm",
    "licence": "full text on a third-party mirror; official text sold by Standartinform. NOT the issuer.",
    "force": "voluntary",
    "force_note": "Russian national standard, voluntary application under FZ-162 art. 26 unless invoked by a technical regulation or contract. NO force in Azerbaijan. Cited only as the clearest normative statement of the decimal-comma rule (cl. 5.4.1, 5.4.3), corroborating the Azerbaijani standards.",
    "reusable": false
  },
  "gost_21501_2018": {
    "title": "ГОСТ 21.501-2018. СПДС. Правила выполнения рабочей документации архитектурных и конструктивных решений",
    "issuer": "Interstate Council for Standardization (МГС); enacted in RF by Rosstandart order 1121-ст of 18.12.2018",
    "date": "2018, in force 2019-06-01",
    "url": "https://meganorm.ru/Data2/1/4293732/4293732743.htm",
    "licence": "full text on a third-party mirror. NOT the issuer.",
    "force": "voluntary",
    "force_note": "Azerbaijan is NOT among the voting parties (AM, BY, KG, RU, UZ only) — verified from the preface. AZ remains on AZS ГОСТ 21.501-2010. Cited for the ОК1/ОК2 window-mark rule (cl. 5.4.2 fn), the unprefixed door mark (cl. 5.3.2 г), and the room-number substitution (cl. 5.3.2 е), where the AZ edition is silent or less specific.",
    "reusable": false
  },
  "gost_2316_2008": {
    "title": "ГОСТ 2.316-2008. ЕСКД. Правила нанесения надписей, технических требований и таблиц на графических документах",
    "issuer": "Interstate Council for Standardization / Rosstandart",
    "date": "2008-12-25",
    "url": "https://vashdom.ru/gost/2.316-2008/",
    "licence": "full text on a third-party mirror",
    "force": "voluntary",
    "force_note": "Cl. 4.4 PROHIBITS abbreviation in drawing captions except those listed in Annex A, which is справочное (informative) and contains zero room-type words. Referenced by AZS ГОСТ 21.101-2010 cl. 5.3 as the base list its Əlavə D extends.",
    "reusable": false
  },
  "gost_6629_88": {
    "title": "ГОСТ 6629-88. Двери деревянные внутренние для жилых и общественных зданий. Типы и конструкция",
    "issuer": "Gosstroy USSR, decision 325 of 31.12.1987",
    "date": "in force 1989-01-01; reissued March 1999",
    "url": "https://meganorm.ru/Data2/1/4294853/4294853218.htm",
    "licence": "full text and drawings on a third-party mirror. NOT the issuer.",
    "force": "superseded",
    "force_note": "SUPERSEDED by ГОСТ 475-2016 from 2017-07-01. Cited as the ANCESTOR standard for the door designation scheme and opening series. Its Azerbaijani status is unverified; AzDTN 1.1-1 cl. 1.5(a) keeps ex-all-Union GOSTs nominally in force. Not an Azerbaijani document.",
    "reusable": false
  },
  "gost_24698_81": {
    "title": "ГОСТ 24698-81. Двери деревянные наружные для жилых и общественных зданий. Типы, конструкция и размеры",
    "issuer": "Gosstroy USSR, decision 51 of 1981",
    "date": "in force 1984-01-01; reissued Standartinform 2009",
    "url": "https://files.stroyinf.ru/Data2/1/4294853/4294853205.htm",
    "licence": "full text on a third-party mirror",
    "force": "status_unverified",
    "force_note": "Search prose claims cancellation by an order of 12.05.2009, which conflicts with the 2009 reissue. NOT verified against a registry. Cited as ancestor only.",
    "reusable": false
  },
  "gost_11214_86": {
    "title": "ГОСТ 11214-86. Окна и балконные двери деревянные с двойным остеклением. Типы, конструкция и размеры",
    "issuer": "Gosstroy USSR, decision 191 of 14.11.1985",
    "date": "in force 1987-01-01",
    "url": "https://meganorm.ru/Data1/3/3482/index.htm",
    "licence": "full text and drawings on a third-party mirror",
    "force": "status_unverified",
    "force_note": "Search prose claims cancellation by Minregion order of 16.03.2015 without replacement. NOT verified. Cited as ancestor for the window designation scheme and residential opening series.",
    "reusable": false
  },
  "gost_23166_99": {
    "title": "ГОСТ 23166-99. Блоки оконные. Общие технические условия",
    "issuer": "Interstate Council for Standardization",
    "date": "in force 2001-01-01, with Amendment 1",
    "url": "https://meganorm.ru/Data2/1/4294849/4294849159.htm",
    "licence": "full text on a third-party mirror",
    "force": "voluntary",
    "force_note": "IMPORTANT: cl. 4.9 explicitly refuses to fix opening sizes — window and wall-opening dimensions are 'установлены в проектной документации'. Its Table 2 series is only рекомендуемые. If 11214-86 really is cancelled, there is NO live standard fixing a residential opening grid, and our catalogue becomes engine_choice.",
    "reusable": false
  },
  "sp_54_13330_2022": {
    "title": "СП 54.13330.2022. Здания жилые многоквартирные (СНиП 31-01-2003)",
    "issuer": "Minstroy of the Russian Federation",
    "date": "2022, with amendments 1 and 2",
    "url": "https://proekt-kom.ru/laws/sp-54.13330.2022/",
    "licence": "full text on a third-party mirror",
    "force": "partly_mandatory_in_RF",
    "force_note": "Cited here ONLY for canonical Russian room names (§3.1). No force in Azerbaijan. The Russian names are recorded as a cross-check, not as the drawing vocabulary.",
    "reusable": false
  },
  "iso_4157_2": {
    "title": "ISO 4157-2:1998. Construction drawings — Designation systems — Part 2: Room names and numbers",
    "issuer": "ISO/TC 10/SC 8",
    "date": "2nd edition 1998-12-01, confirmed 2023",
    "url": "https://www.iso.org/standard/26190.html",
    "licence": "paid; the normative text was read via a publicly published preview",
    "force": "voluntary_international",
    "force_note": "Cited as the INDEPENDENT corroboration that the published fallback for a room name that will not fit is number-plus-table, not abbreviation (cl. 4.3.1-4.3.2). Shares no lineage with SPDS, which is what makes the agreement meaningful.",
    "reusable": false
  },
  "us_ncs_uds5": {
    "title": "United States National CAD Standard, UDS Module 5: Terms and Abbreviations",
    "issuer": "National Institute of Building Sciences with CSI and AIA",
    "date": "V6 (2014) / V7",
    "url": "https://www.nationalcadstandard.org/ncs6/pdfs/ncs6_uds5.pdf",
    "licence": "PAYWALLED — only the introduction is free. No values from its tables are stated in this research.",
    "force": "voluntary_consensus",
    "force_note": "The only published English architectural abbreviation set found. Its own §5.1.2 discourages abbreviating: 'When the meaning of an abbreviation is in doubt, spell it out!' GSA, VA and USACE adopt it by reference and republish nothing.",
    "reusable": false
  },
  "cldr_az": {
    "title": "Unicode CLDR locale data, az.xml (numbers/latn/symbols)",
    "issuer": "Unicode Consortium",
    "date": "CLDR main branch, © 1991-2026",
    "url": "https://raw.githubusercontent.com/unicode-org/cldr/main/common/main/az.xml",
    "licence": "Unicode-3.0 (SPDX)",
    "force": "informative",
    "force_note": "The civil/locale convention, read first-hand: decimal ',' and group '.'. Agrees with the drafting standards on the decimal; the group separator is irrelevant because drawings never group thousands.",
    "reusable": true
  },
  "ezdxf_probe_local": {
    "title": "DXF encoding and font probes, ezdxf 1.4.4, run on this machine",
    "issuer": "this research (C11)",
    "date": "2026-08-20",
    "url": "experiments/az-drawing/dxf_encoding_probe.py, experiments/az-drawing/dxf_font_probe.py",
    "licence": "ours",
    "force": "measured",
    "force_note": "Source of every claim in §5 marked verified: per-version round-trip, code-page coverage, the cp1251/superscript-two conflict, the R2010->R2000 downgrade, DIMDSEP round-trip, and DIMDSEP being inert at DIMDEC=0.",
    "reusable": true
  }
}
```

---

## 7. Handoffs

| to | what |
|---|---|
| `docs/spec/annotation.md` §7 | Replace degradation ladder step 2. There is no published abbreviation set; the published fallback is **room number + room schedule**, which §6 already ships. Delete `WC` / `ST` / `UT`. |
| `docs/spec/annotation.md` §8, §6 | Opening marks are **two-level**: `ОК1` / bare number in a Ø 5 mm circle on the plan, product designation (`ДГ 21-9`) in the schedule. `D1` / `W2` matches no published convention. |
| `docs/spec/annotation.md` §2, §11 | `FFL ±0.000` → `±0,000`. `DIMDSEP = 44`, and note it is inert at `DIMDEC = 0`. |
| `docs/research/bim-cad-export-stack.md` §2.5 | **The R2000 hard floor is wrong for any non-ASCII language.** Raise to R2007. Correct the claim that the `²` round-trip proves R2000 is Unicode-capable. |
| profile test suite | Add `even_opening_required` beside `even_thickness_required` — over **opening** dimensions only; block heights (2071, 2085, 2175) are odd by design. |
| *Area measurement convention* | `AZS ГОСТ 21.501-2010` cl. 2.3.2 annotates residential area as a **fraction, living over useful**. May force two area numbers into the room tag. |
| whichever partial owns the room table | Azerbaijani per-room vocabulary is **not obtained**. The term for *помещение* is `yerləşkə`. This gates the room tag. |
