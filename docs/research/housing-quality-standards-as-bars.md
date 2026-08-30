# Housing quality standards as bars — WBS 2015 and СП 54.13330

Findings for the research question *do the human housing-quality instruments that
already govern the engine's two corpora score a dwelling against a **bar** or
against the **observed distribution of existing stock**?*

**Research date:** 2026-08-30.
**Method:** primary sources only — the issuing body's own PDF, the standard's own
text, or a first-hand transcription already committed to this repo. Anything not
read first-hand is marked **UNCONFIRMED**; §9 lists every source that could not be
reached.

**Scope, deliberately narrow.** Two lineages only:

- **WBS 2015** — *Wohnungs-Bewertungs-System*, Bundesamt für Wohnungswesen (BWO),
  Switzerland. The engine's corpus is Swiss; this is the same country's own answer
  to the same question.
- **СП 54.13330** — *Здания жилые многоквартирные*, the Russian SNiP successor,
  with **AzDTN 2.7-2** — its Azerbaijani sibling, which *expressly repealed*
  СНиП 2.08.01-89* on Azerbaijani territory. This is the lineage the engine's
  Azerbaijani profile sits in.

⛔ **Out of scope by instruction:** the UK, German and Dutch instruments.

**Companion note.** `docs/research/plan-quality-metrics-in-practice.md`
(2026-08-30) covers the generative-tool and academic-metric half of this question
and is not redone here. It establishes the negative result this note tests against
a second family of sources: **nothing in the research literature or the market
scores a plan against a corpus distribution of a named architectural quantity.**
It quotes WBS 2015's points scheme in its §2.8 in passing; this note goes to the
criteria themselves.

**This note edits no shipped artefact and runs no corpus pass.** Nothing in
`docs/spec/`, `experiments/`, `src/`, `data/` was touched.

---

## 0. TL;DR

**Neither instrument scores against a distribution — and the two answer the
`proposer.md` §6.1 defect from opposite directions.** WBS declines to encode
zoning at all and draws its authority from a hand-picked panel. СП/AzDTN encode
the passage-room rule as a **hard prohibition** and draw it from a normative
tradition. **The one place in either lineage where a threshold is indexed to
observed stock, it is a monotone ratchet that rises as the stock improves — never
a target to match.**

| # | Finding |
|---|---|
| **1** | ⭐ **WBS 2015 is a graded points bar against a printed lookup table** — 25 criteria, 0–4 points each, 100 total. *"Jedes Kriterium erhält … zwischen 0 und maximal 4 Punkte."* Every `Quantität` sub-score is a step function keyed to the dwelling's room count. **No corpus, no percentile, no statistic.** §2.1. |
| **2** | ⭐⭐ **WBS 2015 added a *maximum* net floor area in the 2015 revision — the bar moved *against* the direction the stock was moving.** *"neu nicht mehr nur eine minimale, sondern auch eine **maximale** Nettowohnfläche pro Wohnungsgrösse"*, and the failure text names *"die fehlende, bzw. **überdurchschnittliche** Nettowohnfläche"*. **A distribution-matching score would have tracked the stock upward by construction. WBS deliberately did not.** §2.1. |
| **3** | ⭐ **WBS's one mention of comparison to other buildings is presentational, not scoring** — *"anhand von **Objektbeispielen**, die online zur Verfügung stehen"*. Named exemplars shown beside a score that is already complete. ⭐ **This is a directly copyable pattern for §6.1**: score against a bar, show the corpus *beside* the number rather than folding it in. §2.1. |
| **4** | ⚠️ **WBS does not score zoning, day/night separation, or entry sequence. At all.** Over the full 43-page brochure: `Zonierung` **0**, `Durchgangszimmer` **0**, `Tag/Nacht` **0**, `Intimität` **0**, `Privatheit` **1** — and that one is about the inside/outside boundary. §3.1. |
| **5** | ⭐ **WBS's entire privacy provision for a bedroom is that it is `abschliessbar` — lockable — and it declares rooms *use-neutral* on purpose.** *"Zimmer sind **nutzungsneutral** … individuell genutzte und **abschliessbare** Aufenthaltsbereiche wie Arbeits- oder Schlafräume."* ⚠️ **A bedroom off the hall with a lock satisfies WBS completely** — the corpus's 17.4 % entry-depth inversion is not a defect under Swiss federal assessment. §3.2. |
| **6** | ⭐⭐ **СП 54.13330.2022 cl. 5.6 is the passage-room rule, and it is a hard prohibition — exactly the quantity `zoning.md` D10 measures.** *«…в 2-, 3- и 4-комнатных квартирах спальни и общие жилые комнаты (гостиные) проектируют **непроходными**»*. Bedrooms **and** living rooms must be non-passage. §3.4. |
| **7** | ⭐⭐ **And its exemption is by *tenure*, not by rate.** *«В квартирах частного жилищного фонда и жилищного фонда коммерческого использования общие жилые комнаты (гостиные) **допускается предусматривать проходными**»* — the *living room* may be a passage room in private/commercial housing. **The bedroom limb is never relaxed.** The standard splits the rule the way the engine's social/private partition splits it, and it relaxes only the social half. §3.4. |
| **8** | ⭐⭐ **AzDTN 2.7-2 cl. 5.9 states the same rule for the engine's own AZ profile, in mandatory register, and it is already transcribed first-hand in this repo** — *«Mənzillərdə yataq otaqları digər otağa keçid kimi layihələndirilməməlidir»* (bedrooms shall not be designed as a passage to another room). It is already `is_private` in `data/standards/room-constraints.json`. §3.5. |
| **9** | ⭐⭐⭐ **The one observed-stock hook in either lineage, and it is a ratchet, not a match.** СП 54.13330.2022's Table 5.1 note permits deviation *«с учетом демографических требований, **достигнутого уровня обеспеченности населения жилищем** и ресурсообеспеченности»*, via ЖК РФ art. 50 §2: *«Норма предоставления устанавливается органом местного самоуправления **в зависимости от достигнутого … уровня обеспеченности жилыми помещениями**»*. **A floor indexed to attained provision — it rises when the stock improves and can never be satisfied by reproducing the stock's failures.** §4.3. |
| **10** | ⭐ **WBS's bar was set by a named eleven-person `Expertengruppe`, and no statistical basis is named for any threshold.** `Perzentil`, `Stichprobe`, `Median`, `Quantil`: zero occurrences. §4.1. |
| **11** | ⭐ **Where WBS states its source of authority it is a *selected* exemplar set, not an average** — *"in Wohnungen der 1920er- oder 1950er-Jahre viele Merkmale … die noch heute hohe Qualitäten … zeigen: Klare Typologien … **kluge Raumbeziehungen** im Innern"*; *"verbindet **Bewährtes** mit Neuem"*. The surviving good ones, chosen because they are good. §4.2. |
| **12** | ⚠️ **Neither instrument contains a sentence saying "reproducing existing stock is the wrong objective."** Q4's answer is **no explicit statement, in either**. What exists is structural: three mechanisms that would be incoherent under a distribution-matching objective. §5. |
| **13** | ⚠️ **The two lineages disagree about whether the living room may be a passage room, and the disagreement is about tenure, not about quality.** WBS: silent. СП: forbidden in social housing, permitted in private. **A rate measured over a mixed-tenure corpus mixes two populations the standard treats differently** — and Swiss Dwellings is overwhelmingly private-tenure stock. §6. |

---

## 1. What was read first-hand

| Source | What it is | Read |
|---|---|---|
| **WBS 2015 Broschüre** — *Wohnbauten planen, beurteilen und vergleichen: Wohnungs-Bewertungs-System WBS, Ausgabe 2015*, Bundesamt für Wohnungswesen | The instrument itself: methodology, all 25 criteria with their `Quantität` tables, `Qualität` checklists, glossary and colophon | **Full text extracted locally**, `pdftotext`, 230 167 chars, from [bwo.admin.ch](https://www.bwo.admin.ch/dam/de/sd-web/OylvhDAe-yQv/wbs_2015_broschuere_de.pdf) |
| **WBS 2015 Kriterientabelle** | The one-page scoring form the applicant fills in; authoritative criteria list and per-area point totals | **Full text extracted**, [bwo.admin.ch](https://www.bwo.admin.ch/dam/de/sd-web/ZBH79VvRtmLn/wbs_kriterientabelle_de_web.pdf) |
| **СП 54.13330.2022** — *СНиП 31-01-2003 Здания жилые многоквартирные*, approved by Minstroy order **13.05.2022 № 361/пр** | The Russian multi-apartment residential design code; §5 *Требования к зданиям и помещениям* including Table 5.1, cl. 5.6 and cl. 5.11 | **Full 39-page PDF downloaded and text-extracted locally** (252 176 chars) |
| **ЖК РФ ст. 50** — Housing Code of the Russian Federation, *Норма предоставления и учетная норма площади жилого помещения* | The statute СП 54's Table 5.1 note delegates to | **Parts 1, 2, 4, 5 verbatim**, [consultant.ru](https://www.consultant.ru/document/cons_doc_LAW_51057/8ee8fdbac7a0891b1da140bccadaf9da69aea369/) |
| **AzDTN 2.7-2** — *Yaşayış binaları. Layihələndirmə normaları*, Dövlət Şəhərsalma və Arxitektura Komitəsi, Baku 2021, 28 pp., State Register No. 15202111300003 | The Azerbaijani residential design norm; cl. 5.1, 5.2, 5.6, 5.7, 5.8, 5.9, 5.10 | **First-hand transcription already committed to this repo** — `docs/research/az-statutory-floor-transcription.md` §2.3 and `docs/research/az-region-profile/minima.md`; provenance in `data/standards/room-constraints.json` |

---

## 2. Q1 — bar, graded scale, or observed distribution?

**Answer: a graded points bar (WBS) and a hard threshold code (СП / AzDTN).
Neither instrument computes anything over a population of existing dwellings.**

### 2.1 WBS 2015 — a graded points bar against a printed lookup table

**The scoring clause**, verbatim, WBS 2015 brochure, *Beurteilen*:

> *"Jedes Kriterium erhält aufgrund der Beurteilung von **Quantität oder
> Potenzial, Qualität und Innovation zwischen 0 und maximal 4 Punkte**. Insgesamt
> können 100 Punkte erreicht werden. Die addierten Einzelresultate ergeben den
> **Gebrauchswert** des Wohnobjekts."*

and the procedure clause:

> *"Anhand einer **Selbstdeklaration** werden in einem schrittweisen Vorgehen die
> Quantität, das Potenzial, die Qualität sowie allfällige Innovationen der
> einzelnen Kriterien ermittelt. **Jedes Kriterium ergibt maximal 4 Punkte, der
> Gebrauchswert kann damit maximal 100 Punkte betragen.**"*

⭐ **Every `Quantität` sub-score is a printed step function keyed to the dwelling's
room count.** The instrument does not compute a statistic over a population; it
looks the measured value up in a table printed in the brochure and reads off a
point value. Two worked examples, transcribed from the brochure's own tables:

| criterion | `Messwert` (what is measured) | table structure |
|---|---|---|
| **K17 / Vielfältige Nutzbarkeit** | *"Anzahl Zimmer, in denen ein Flächenmodul Platz findet"* — the count of rooms into which a 14 m² rectangular module fits (380×368 cm to 467×300 cm), where *"Eine Seite des Flächenmoduls muss an einem mindestens 300 cm langen Wandstück **ohne Tür- und Fensteröffnung** liegen"* | one column per dwelling size, **1-Zimmer through 7-Zimmer**; the measured count 1…7 maps to a point value |
| **K22 / Anpassungsfähigkeit des privaten Raums** | *"Anzahl entfernbarer nichttragender Wände und Möglichkeiten zusätzlicher Trennwände"* | size bands **1-Zimmer / 2–3-Zimmer / 4–5-Zimmer / 6–7-Zimmer**; counts 1…6 map to a scale printed as **3 / 2.5 / 2 / 1.5 / 1** |

⭐⭐ **And K15 is a *two-sided* band — the instrument penalises being *above* the
stock as well as below it.** The `Quantität` table for **K15 / Nettowohnfläche**
prints two rows of m² figures across the dwelling sizes 1-Zimmer … 7-Zimmer — a
floor and a ceiling — and the rule attached to it names the *upper* failure
explicitly:

> *"Werden bei der Quantität keine Punkte erreicht, muss mittels einer Innovation
> nachgewiesen werden, wie die **fehlende, bzw. überdurchschnittliche**
> Nettowohnfläche kompensiert wird. Erzielt die Innovation keinen Punkt, kann die
> Qualität nicht angerechnet werden."*

The preface says the ceiling was **new in the 2015 edition**:

> *"Zudem wird **neu nicht mehr nur eine minimale, sondern auch eine maximale
> Nettowohnfläche pro Wohnungsgrösse** thematisiert."*

⭐ **This is the finding that most directly answers the defect in `proposer.md`
§6.1.** Swiss dwelling floor area per person has risen for decades; WBS 2015
responded by adding a **ceiling** — it moved the bar *against* the direction the
stock was moving. An instrument that scored against the observed distribution
would have done the opposite by construction: it would have tracked the stock
upward, and a dwelling at the growing mean would have kept scoring well. WBS's
authors chose to be normative exactly where the stock was drifting. **That is the
structural argument against "match the corpus rate", made by the official
instrument for the engine's own corpus, in the same country, about the same
dwellings.**

⚠️ **The one place WBS mentions comparison to other buildings, it is
presentational, not scoring.** *Vergleichen*, verbatim:

> *"Beim Vergleichen wird der Gebrauchswert in einen **Kontext** gestellt. Die
> Auswertung über eine Infografik stellt die drei Bereiche … dar. Zudem können die
> ermittelten Gebrauchswerte anhand von **Objektbeispielen, die online zur
> Verfügung stehen**, mit anderen Wohnbauten verglichen werden."*

Named example objects on a website, shown beside your score. **Not a distribution,
not a percentile, not a fitted reference.** The score is complete before any
comparison happens. ⭐ **This is a directly usable pattern for §6.1**: report the
number against a bar, and put the corpus rate *beside* it as context rather than
folding the corpus into the score.

### 2.2 The full WBS 2015 criteria list — 25 criteria, 100 points

Transcribed from the **Kriterientabelle**, the one-page scoring form. Each
criterion is `max. 4` points; the three area totals are printed on the form.

| # | criterion | area |
|---|---|---|
| K1 | Wohnungsangebot | **Wohnstandort** — assessed on *Potenzial*, not *Quantität* |
| K2 | Ergänzende Nutzungen | Wohnstandort |
| K3 | Mobilität und Verkehr | Wohnstandort |
| K4 | Räumliche Anbindung | Wohnstandort |
| K5 | Grossflächiges Freiraumangebot | Wohnstandort |
| K6 | Partizipation | Wohnstandort |
| | **Gebrauchswert Wohnstandort** | **max. 24 Punkte** |
| K7 | Langsamverkehr | **Wohnanlage** |
| K8 | Gemeinsamer Aussenbereich | Wohnanlage |
| K9 | Motorisierter Individualverkehr | Wohnanlage |
| K10 | **Hauseingangszone und Wohnungszugänge** | Wohnanlage |
| K11 | Gemeinsame Abstellräume | Wohnanlage |
| K12 | Mehrzweck- und Gemeinschaftsräume | Wohnanlage |
| K13 | Wasch- und Trocknungsräume | Wohnanlage |
| K14 | Veränderbares Raumangebot | Wohnanlage |
| | **Gebrauchswert Wohnanlage** | **max. 32 Punkte** |
| K15 | Nettowohnfläche | **Wohnung** |
| K16 | Zimmergrösse und zusätzliches Flächenangebot | Wohnung |
| K17 | Vielfältige Nutzbarkeit | Wohnung |
| K18 | Möblierbarkeit der Zimmer | Wohnung |
| K19 | Koch- und Essbereich | Wohnung |
| K20 | Ausstattung Sanitärbereich | Wohnung |
| K21 | Möblierbarkeit Abstellbereich | Wohnung |
| K22 | **Anpassungsfähigkeit des privaten Raums** | Wohnung |
| K23 | Privater Aussenbereich | Wohnung |
| K24 | Übergänge Innen/Aussen | Wohnung |
| K25 | Private Abstellräume ausserhalb der Wohnung | Wohnung |
| | **Gebrauchswert Wohnung** | **max. 44 Punkte** |
| | **Gebrauchswert** | **max. 100 Punkte** |

⭐ **Note what the 44-point dwelling block is made of: area, room size, furniture
fit, kitchen/dining, sanitary fit-out, storage fit, adaptability, outdoor space.
There is no criterion for the *arrangement* of rooms relative to the entrance, and
none named for privacy or zoning.** §3.1 makes that negative precise.

⚠️ **The dwelling block is also scored twice**: once per `Wohnungstyp` on its own
form, and once as *"Wohnung (Ø aller Wohnungstypen)"* — the **average over the
dwelling types in the submitted project** — on the object-level form. That is the
only averaging in the instrument, and it averages *within a project*, never across
the national stock.

### 2.3 СП 54.13330.2022 — a hard threshold code with no score at all

⭐ **The Russian instrument is not a scoring system.** It has no points, no
weights, no aggregate, and no notion of a better or worse plan — only compliant
and non-compliant. Its normative vocabulary is three modal forms, and every plan
requirement in §5 is written in one of them:

| form | force | example |
|---|---|---|
| `должна быть … не менее` | mandatory floor | cl. 5.11 |
| `проектируют` / `следует предусматривать` | mandatory prescription | cl. 5.6, cl. 5.8 |
| `не допускается` | prohibition | cl. 5.10 |
| `допускается` | permission / exemption | cl. 5.5, cl. 5.6 second sentence |

**Table 5.1**, cl. 5.2, is the dwelling-size floor — *"Площади квартир (без учета
площадей балконов, лоджий, террас, холодных кладовых и приквартирных тамбуров) в
зависимости от числа их жилых комнат"*:

| Число жилых комнат | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|---:|
| **Минимальная площадь квартир, м²** | **28** | **44** | **56** | **70** | **84** | **103** |

and **cl. 5.11** is the per-room floor, verbatim:

> *"Площадь жилых комнат и вспомогательных помещений в квартирах должна быть, м²,
> **не менее**: **14** — общей жилой комнаты в однокомнатной квартире; **16** —
> общей жилой комнаты в квартирах с числом жилых комнат две и более; **8** —
> спальни (**10** — на двух человек); **8** — кухни; **6** — кухонной зоны в
> кухне-столовой."*

⭐ **A single threshold per room type, with one conditional refinement (10 m² for a
two-person bedroom).** No band, no distribution, no percentile. Compare WBS, which
converts the same quantity into 0–4 points against a table: **the Russian lineage
does not grade at all.** A plan either clears the floor or is not a plan.

⚠️ **`не менее` is one-sided.** Unlike WBS's K15, СП 54 sets no ceiling on room or
dwelling area. The two lineages diverge exactly here, and §5 returns to it.

### 2.4 AzDTN 2.7-2 — the same threshold code, with the bar split by grammatical register

The Azerbaijani norm is the engine's own profile source and **expressly repealed
СНиП 2.08.01-89\*** on Azerbaijani territory, which is what puts it in this
lineage. Its mechanism for separating a bar from a recommendation is unusual
enough to record: **grammatical register**, fixed by the AzDTN system's governing
document (*«Əsas müddəalar (Konsepsiya)»*, Bakı 1994, §§3.1, 3.2, 3.4, 3.6):

| register | force | example |
|---|---|---|
| `az olmamalıdır` / `edilməlidir` / `-məlidir` | **məcburi** — mandatory | cl. 5.7 room-area minima; cl. 5.8 heights; **cl. 5.9 the passage-room rule** |
| `tövsiyə olunur` / `tövsiyə edilir` | **tövsiyə** — recommended | cl. 5.1 apartment totals |

⭐ **Two tiers, both fixed, neither statistical.** The recommended tier is the
nearest thing in the lineage to a graded scale, and it is still a printed number —
a *recommendation to reach a figure*, not a position in a distribution. `cl. 5.6`
is the one clause that delegates outward, and it delegates to **ergonomics**, not
to observed practice: *«Mənzilin yaşayış otaqlarının və digər sahələrinin ölçüləri
**erqonomikanın tələblərinə uyğun** … müəyyənləşdirilir»*.

⚠️ **AzDTN 2.13-1 is not a housing-quality instrument** and does not belong to this
question. It is the gas/engineering-systems norm; its one clause that bears on a
plan is **cl. 8.31**, requiring a gas hob to stand in a `mətbəx otağı` — a hard
categorical rule, already recorded in `data/standards/room-constraints.json` under
`gas_note`, and enforced nowhere in this engine by design.

---

## 3. Q2 — does either score ZONING, PRIVACY or ENTRY SEQUENCE?

**Answer: WBS, no — comprehensively and deliberately. СП/AzDTN, yes — as a hard
prohibition, and it is nearly the exact quantity `zoning.md` D10 measures.**

### 3.1 ⭐ WBS: the negative result, stated as word counts over the full brochure

Searched over the complete extracted text of the 43-page brochure (230 167
characters):

| term | occurrences | where |
|---|---:|---|
| `Zonierung` | **0** | — |
| `Durchgangszimmer` (passage room) | **0** | — |
| `Tag/Nacht`, `Tagbereich`, `Nachtbereich` | **0** | — |
| `Intimität` | **0** | — |
| `Privatheit` | **1** | K24, and it is about the **inside/outside** transition, not room-to-room |

The single `Privatheit` occurrence, verbatim (K24 / Übergänge Innen/Aussen,
*Zielsetzung*):

> *"Der funktionale und visuelle Übergang vom Inneren der Wohnung in den
> Aussenraum ist so gestaltet, dass Übergänge bewusst erfahrbar und die Qualitäten
> des Aussenraums erlebbar werden. Sichtbezüge zwischen innen und aussen geben
> Orientierung und das Gefühl von Grosszügigkeit. **Abgestufte Öffentlichkeitsgrade
> gewährleisten eine angemessene Privatheit.**"*

⭐ **"Abgestufte Öffentlichkeitsgrade" — graded degrees of publicness — is
Alexander's intimacy gradient by name, and WBS applies it to the dwelling's
*outer* boundary only.** The gradient *inside* the dwelling, from front door to
bedroom, is not scored anywhere in the 25 criteria.

### 3.2 ⚠️ WBS's privacy proxy is a *lock*, not a position in the graph

The glossary entry for **Zimmer** is load-bearing, because the room count drives
every `Quantität` table in §2.1:

> *"**Zimmer** Zimmer sind **nutzungsneutral**. Als Zimmer gelten gemeinsame
> Aufenthaltsbereiche wie offene Wohnbereiche mit angegliedertem Kochbereich oder
> **individuell genutzte und abschliessbare Aufenthaltsbereiche wie Arbeits- oder
> Schlafräume**. Zimmer sind natürlich belichtet, belüftet und beheizt. **Das erste
> Zimmer einer Wohnung weist mindestens 14 m² auf. Alle weiteren Zimmer sind
> mindestens 10 m² gross**, sofern kantonale Bestimmungen nicht kleinere Zimmer
> zulassen."*

⭐ **Three things follow, and all three touch this engine.**

1. **WBS's entire privacy provision for a bedroom is that it is `abschliessbar` —
   lockable.** A door with a lock, not a depth from the entrance. `K18 /
   Möblierbarkeit der Zimmer` reinforces it: *"Bei **abschliessbaren** Zimmern ab
   12 m² wird die Anzahl der Stellungen eines Doppelbetts oder zweier Einzelbetten
   gemessen"*, and the criterion averages *"aller **abschliessbaren** Zimmer"*.
2. **WBS declines the social/private distinction outright** — *"Zimmer sind
   **nutzungsneutral**"*. A `Zimmer` is a neutral container; living room and
   bedroom are the same object to the instrument, separated only by the 14 m²
   first-room rule. This is the opposite of the engine's social/private partition
   and it is a *deliberate* position rather than an omission: use-neutrality is the
   stated design goal of K17 — *"Vielfältig nutzbare Zimmer lassen sich für diverse
   Bedürfnisse einrichten."*
3. ⚠️ **A lockable room off the hall satisfies WBS completely.** The 17.4 %
   entry-depth inversion measured in `zoning.md` §6.5 is, under Swiss federal
   assessment, **not a defect at all** — provided the bedroom locks and is ≥ 10 m².
   That is a real argument that the Swiss corpus rate is not measuring a violation
   the Swiss system recognises, and it belongs in the §6.5 defect-or-typology
   discussion. ⚠️ **But note the asymmetry: WBS's silence is not an endorsement.**
   It scores no room-relationship quantity of any kind, so its silence on entry
   depth is the same silence it keeps about day/night separation, which nobody
   disputes is real.

### 3.3 The two WBS criteria that come closest, and how far short they fall

**K10 / Hauseingangszone und Wohnungszugänge** is the only criterion with the
entrance in its title, and it measures **area**:

> *"Die Hauseingangszonen und Wohnungszugänge werden **anhand der Gesamtfläche**
> quantitativ beurteilt. Dabei wird die Erschliessungszone abgezogen … Die
> **Gesamtfläche wird durch die Gesamtzimmerzahl aller betroffenen Wohnungen
> geteilt.**"*

Square metres per room, in the *common* entrance hall of the building — outside
the dwelling. **Nothing about what the front door of the dwelling opens onto.**

**K22 / Anpassungsfähigkeit des privaten Raums** contains the one no-passage-room
rule in the whole instrument, and it is conditional:

> *"Die Anpassungsfähigkeit wird anhand der Anzahl von entfernbaren nichttragenden
> Wänden und / oder durch die Möglichkeit, zusätzliche Wände einzubauen, quantitativ
> beurteilt. … **Jedes neu entstehende Zimmer oder jeder Raumteil muss selbständig
> erschlossen sein**, mindestens 10 m² Fläche aufweisen, in der geringsten
> Raumabmessung mindestens 270 cm betragen sowie natürlich belichtet und belüftet
> sein."*

⭐ **"Selbständig erschlossen" — independently accessed — is a genuine
no-through-room rule, but it applies only to the *hypothetical* rooms created by
removing or adding a non-load-bearing wall**, as the test of whether that wall
counts toward the criterion's count. A dwelling whose *as-built* bedroom is reached
through the living room loses nothing under K22, or anywhere else.

K22's `Qualität` checklist adds the **Schaltzimmer** — the switch room — the
nearest thing WBS has to an access-graph statement:

> *"**Schaltzimmer** erfüllen dieselben Anforderungen wie ein Zimmer, lassen sich
> jedoch nicht nur einer, sondern mehreren Wohnungen zuordnen. **Ein Schaltzimmer
> ist immer direkt von einer angrenzenden Wohnung und nicht von der
> halböffentlichen Erschliessungszone aus zugänglich.**"*

**K19 / Koch- und Essbereich** carries the only room-to-room adjacency threshold in
the dwelling block, and it is metric, not topological:

> *"Der Essbereich mit Tischmodul muss sich **neben dem Kochbereich oder der
> Erschliessungszone** befinden, die Flächen dürfen sich nicht überschneiden."*
> *"**Die Distanz zwischen der Mitte des Kochbereichs bis zur Mitte des Essbereichs
> beträgt weniger als 300 cm.** … **Der Durchgang vom Koch- zum Essbereich ist
> breiter als 120 cm.**"*

### 3.4 ⭐⭐ СП 54.13330.2022 cl. 5.6 — the passage-room rule, and it splits by tenure

This is the clause the SNiP tradition was expected to carry, and it is sharper than
expected. **Verbatim, complete:**

> **5.6** *В квартирах государственного и муниципального жилищных фондов согласно
> [4] в **2-, 3- и 4-комнатных квартирах спальни и общие жилые комнаты (гостиные)
> проектируют непроходными**. В квартирах частного жилищного фонда и жилищного
> фонда коммерческого использования **общие жилые комнаты (гостиные) допускается
> предусматривать проходными**.*

*"In apartments of the state and municipal housing funds …, in 2-, 3- and 4-room
apartments, **bedrooms and common living rooms (living rooms) are designed as
non-passage**. In apartments of the private housing fund and the commercial-use
housing fund, **common living rooms (living rooms) may be provided as passage
rooms.**"*

⭐ **Four things this settles for `proposer.md` §6.1.**

1. **It is a bar, and a binary one.** `проектируют непроходными` is a mandatory
   prescription with no points, no grading, no rate. There is no reading of cl. 5.6
   on which a plan is *17.4 % non-compliant*.
2. **Its scope is the room count, exactly as House-GAN++ and this engine
   stratify.** The rule binds **2-, 3- and 4-room** apartments — it does not reach a
   one-room flat (where the question is vacuous) and does not state itself for 5+.
   ⭐ **A standard writing the same room-count stratification the companion note's
   finding 2 recommends is independent corroboration that the quantity is
   room-count-dependent.**
3. ⭐⭐ **It splits exactly along the engine's social/private partition, and it
   relaxes only the social half.** Both `спальни` (bedrooms) and `гостиные` (living
   rooms) are non-passage in social housing; in private housing **only the living
   room's** limb is lifted. **The bedroom limb is never relaxed, in any tenure.**
   That is the strongest available external warrant that the private set is the
   load-bearing one, and that a bedroom on a through-route is a different kind of
   fault from a living room on one.
4. ⚠️ **The exemption is by *tenure*, not by observed frequency.** The standard's
   answer to "lots of private flats have passage living rooms" is not to set the bar
   at that rate — it is to **say which building programme the bar binds**. That is a
   categorically different move from scoring against a corpus rate, and it is
   available to this engine: the Brief knows its programme.

⚠️ **What cl. 5.6 does *not* say.** It says nothing about *depth from the
entrance* — a bedroom directly off the entry hall is fully compliant, exactly as
under WBS. **The SNiP lineage forbids the through-route; it does not order the
sequence.** `zoning.md` D10's quantity is *nearer the entrance than*, which is
strictly weaker than *on the path to*, and the standard addresses only the latter.
⭐ **The engine already encodes the standard's version** — `room-constraints.json`'s
`is_private` drives the C6 item 1 reachability predicate — so the part of D10 that
has statutory backing is **already a hard rule**, and the residual §6.1 term is the
part that does not.

Two neighbouring clauses complete the picture, and neither adds a zoning rule:

> **5.3** *…предусматривают жилые комнаты: **общие** — в однокомнатных, **общие
> жилые комнаты (гостиные) и спальни** — в квартирах с числом комнат 2 и более, а
> также вспомогательные помещения: кухню (или кухню-столовую), **переднюю
> (прихожую)**, уборную (или туалет), ванную комнату и (или) душевую, или
> совмещенный санузел…*
> **5.10** *Размещение квартир и жилых комнат в подвальных и цокольных этажах
> многоэтажных жилых зданий **не допускается**.*

⭐ **cl. 5.3 makes the social/private split part of the required room schedule
itself** — a 2+-room dwelling must contain both a `гостиная` and a `спальня`, and
must contain a `передняя (прихожая)`, an entrance hall. **The standard mandates the
entrance room the engine's hall construction produces**, which is why `zoning.md`
§6.4's has-circulation stratum is the right one.

### 3.5 ⭐⭐ AzDTN 2.7-2 cl. 5.9 — the same rule, for the engine's own region

Already transcribed first-hand in this repo
(`docs/research/az-statutory-floor-transcription.md` §2.3,
`docs/research/az-region-profile/minima.md`):

> **cl. 5.9** — *«Mənzillərdə **yataq otaqları digər otağa keçid kimi
> layihələndirilməməlidir**»* — *"In dwellings, bedrooms shall not be designed as a
> passage to another room."* Register `-məlidir` = **məcburi**, mandatory.

⭐ **AzDTN keeps only the bedroom limb and drops the living-room limb entirely** —
no tenure split, no `гостиная` clause, no exemption. The Azerbaijani successor
therefore states the *strictest and simplest* form of the rule in the lineage: the
bedroom is never a through-route, in any dwelling, full stop.

`room-constraints.json` already records the relationship correctly, and its wording
is worth preserving because it is the right posture for §6.1 too:

> *"**CORROBORATED, NOT SOURCED, FOR BEDROOMS**: AzDTN 2.7-2 cl. 5.9 makes this
> statutory in AZ … The flag stays region-invariant and engine-defined per C14;
> this records only that one shipping region independently makes it law."*

---

## 4. Q3 — how was the bar's level chosen?

**Answer: WBS, a named expert panel plus a curated historical exemplar set. СП, a
normative tradition — with one delegation to observed stock that turns out to be a
ratchet.**

### 4.1 ⭐ WBS: a named expert panel of eleven, with no statistical instrument anywhere

The brochure's colophon names the body outright — an **Expertengruppe** of eleven:
academics, architects, a sociologist, a housing-fund manager and a trade-journal
editor:

> *"**Expertengruppe** Patrick Clémençon, Chefredaktor Habitation, Fribourg ·
> Cornelia Estermann, MAS REM, Pensimo Management AG, Zürich · Marie Antoinette
> Glaser, Dr. phil. I, **ETH Wohnforum – ETH Case**, Zürich · Andreas Hofer, dipl.
> Architekt ETH, Archipel GmbH, Zürich · Richard Hunziker, VR-Präsident Pensimo
> Management AG, Zürich · Amelie-Theres Mayer, dipl. Ing. Architektur, HSLU –
> Technik & Architektur, Horw · Georg Precht, dipl. Ing. Architektur, ETH Wohnforum
> – ETH Case, Zürich · Kathrin Schnellmann, dipl. Architektin ETH, arc Consulting,
> Zürich · Christina Schumacher, Soziologin, Prof. FHNW Institut Architektur,
> Muttenz · Jürg Sollberger, dipl. Architekt ETH, reinhardpartner Architekten und
> Planer AG, Bern · Pascal Vincent, dipl. Architekt ETH, Aebi & Vincent Architekten
> SIA AG, Bern"*

and the preface credits the revision to *"dem **Projektteam und der
Expertengruppe**"*.

⚠️ **No percentile, no survey, no sample, no statistical basis of any kind is named
for any threshold in the brochure.** The `Quantität` tables arrive without
derivation. The instrument's own account of why it changes is *periodic
re-examination for fitness*, not measurement:

> *"Qualitätsvorstellungen unterliegen jedoch einem steten Wandel, Wohnformen
> verändern sich. **Ein Werkzeug zur Beurteilung von Wohnüberbauungen muss daher
> periodisch auf seine Tauglichkeit überprüft werden.**"*

### 4.2 ⭐ Where WBS's levels *did* come from: selected historical exemplars, not the average

The nearest the instrument comes to stating its own source of authority is the
opening of *Wohnstandort / Wohnanlage / Wohnung*, and it is the passage most worth
carrying into `proposer.md`:

> *"Wohnbedürfnisse und Wohnvorstellungen sind stetem Wandel unterworfen.
> Gleichzeitig weisen sie erstaunliche Konstanten auf. **So lassen sich
> beispielsweise in Wohnungen der 1920er- oder 1950er-Jahre viele Merkmale erkennen,
> die noch heute hohe Qualitäten und erfrischende Selbstverständlichkeiten zeigen:
> Klare Typologien und robuste Strukturen, nutzungsneutrale und damit auch
> anpassbare Räume, kluge Raumbeziehungen im Innern und gegen aussen, hohe
> Gebrauchstauglichkeit.**"*
> *"Das Wohnungs-Bewertungs-System WBS **verbindet Bewährtes mit Neuem und
> Zukunftsfähigem.**"*

⭐ **That is a corpus argument — and it is explicitly a *selected* corpus.** The
authority is *"Wohnungen der 1920er- oder 1950er-Jahre"* whose qualities are *still*
recognised: the surviving good ones, picked by the panel because they are good. It
is not the 1920s stock's *distribution*; it is an exemplar set, and *"kluge
Raumbeziehungen im Innern"* — clever internal room relationships — is named as one
of the properties taken from it. **A rate computed over all of that stock would
include everything the panel left out. That is the difference between a retrieval
corpus and a reference corpus, stated by a federal instrument.**

### 4.3 ⭐⭐⭐ СП 54.13330: the one observed-stock hook in either lineage — and it is a ratchet

**This is the answer to the question the task called the most valuable thing that
could be found, and it is a qualified yes.**

СП 54.13330.2022 attaches this note to Table 5.1, verbatim:

> *"**Допускается отклонение** от приведенных значений в таблице 5.1 к числу жилых
> комнат и площади квартир **в соответствии с [4, статья 50]** с учетом
> демографических требований, **достигнутого уровня обеспеченности населения
> жилищем** и ресурсообеспеченности жилищного строительства."*

*"Deviation from the values given in Table 5.1 … is permitted in accordance with
[the Housing Code], **article 50**, taking into account demographic requirements,
**the attained level of housing provision of the population**, and the resource
availability of housing construction."*

Reference [4] is the **Жилищный кодекс РФ**. Article 50, read first-hand, parts 1
and 2:

> **1.** *"Нормой предоставления площади жилого помещения по договору социального
> найма является **минимальный размер площади** жилого помещения, исходя из
> которого определяется размер общей площади жилого помещения, предоставляемого по
> договору социального найма."*
> **2.** *"**Норма предоставления устанавливается органом местного самоуправления
> в зависимости от достигнутого в соответствующем муниципальном образовании уровня
> обеспеченности жилыми помещениями**, предоставляемыми по договорам социального
> найма, и других факторов."*
> **5.** *"Учетная норма устанавливается органом местного самоуправления. **Размер
> такой нормы не может превышать размер нормы предоставления**, установленной
> данным органом."*

⭐⭐ **So one threshold in this lineage genuinely is indexed to observed stock — and
the way it is indexed is the whole finding.**

| property | ЖК РФ art. 50 | "match the corpus rate" |
|---|---|---|
| what is observed | the **attained level of provision** (m² per person actually achieved) | the **rate of a defect** |
| what the observation sets | a **minimum** (`минимальный размер`) | a **target** |
| direction of movement as stock improves | the bar **rises** | the target is unchanged — the defect rate is preserved |
| direction as stock worsens | the bar falls — ⚠️ **the one weakness of the mechanism** | the target follows down |
| who applies it | a **municipality**, per jurisdiction, publicly, once | a scoring function, per plan |
| what it can never license | producing dwellings *below* the attained level | — it licenses exactly that |

⭐ **The mechanism is a monotone ratchet on a *good* quantity, not a match on a
*bad* one.** Housing provision is a quantity where more is better, so indexing a
floor to the attained level is coherent: it says *whatever we have already managed
for people, do not now do worse.* Entry-depth inversion is a quantity where **less
is better**, and the same mechanism transplanted onto it would say *keep failing at
the rate we already fail* — which is the §6.1 defect, precisely.

⭐ **The transplantable form, if the engine wants an observed-practice bar:** take
the corpus statistic as a **one-sided bound in the improving direction**, never as
a two-sided target. On the inversion rate that is *"no more often than the corpus
does"* — a ceiling at 17.8 %, with a generator that never inverts scoring
perfectly. That is exactly what the companion note's §2.7 calls the one-sided
reading, and **ЖК РФ art. 50 is the statutory precedent for it.** ⚠️ It is a
precedent for the *shape*, not for the *level*: nothing in either lineage sets a
bar at an observed **percentile**, and the search for that specific construction
came up empty in both.

⚠️ **UNCONFIRMED and out of scope:** no municipal `норма предоставления` bylaw was
read, so how a Russian municipality actually computes "attained level" is not
established here. The statutory delegation is confirmed; its implementation is not.

### 4.4 AzDTN — delegated to ergonomics, not to practice

AzDTN 2.7-2 cl. 5.6, read first-hand and already in this repo, delegates room
dimensions **outward and downward to the human body**, not sideways to the market:

> *«Mənzilin yaşayış otaqlarının və digər sahələrinin ölçüləri **erqonomikanın
> tələblərinə uyğun** … müəyyənləşdirilir»*

⭐ **That is a third answer to "how was the level chosen": neither panel nor
practice, but a derivation from furniture and body clearances** — which is exactly
what `room-constraints.json`'s region-free ergonomic tier already is. The engine's
own two-tier structure (ergonomic base, statutory raise) mirrors the norm's.

---

## 5. Q4 — is either explicit that reproducing existing stock is the wrong objective?

⚠️ **No. Neither instrument contains a sentence to that effect, and this note
should not be cited as if one did.** Standards do not argue against alternative
methodologies; they state requirements. **The honest answer to Q4 is that the
question is not asked in either document.**

⭐ **What exists instead is three structural facts, each of which would be
incoherent if the instrument's objective were to reproduce the stock:**

1. **WBS 2015's new *maximum* net floor area** (§2.1). Swiss dwelling area was
   growing; the 2015 revision added a ceiling. A stock-matching instrument moves
   *with* its stock. This one moved against it, in the revision it describes as
   *"verbindet Bewährtes mit Neuem und Zukunftsfähigem"*.
2. **WBS's authority is a *selected* exemplar set** (§4.2) — the 1920s and 1950s
   dwellings *"die noch heute hohe Qualitäten … zeigen"*. Selection is the whole
   mechanism. An average over that stock would include what was selected out.
3. **СП 54.13330 cl. 5.6 forbids the passage room outright in social housing**
   (§3.4) while acknowledging in the same clause that private housing does it. The
   standard **knows the practice exists and prohibits it anyway** for the programme
   it governs. That is the clearest available statement in either lineage that
   observed frequency is not a defence — expressed as law rather than as
   methodology.

⚠️ **And one fact that cuts the other way, recorded so this note is not one-sided:**
ЖК РФ art. 50 §2 (§4.3) *does* index a statutory minimum to attained practice, and
СП 54's own Table 5.1 note *does* permit deviation on that basis. **The lineage is
not purely normative.** The defensible summary is: *where a quantity improves
monotonically, this lineage will index a floor to what has already been attained;
where a quantity is a defect, it prohibits it outright regardless of frequency.*

---

## 6. ⚠️ One correction this note owes the corpus rate

`zoning.md` §6.5's 17.4 % (17.8 % in the has-circulation stratum) is measured over
**Swiss Dwellings**, which is overwhelmingly private-tenure stock. СП 54.13330
cl. 5.6 treats exactly that distinction as decisive: the passage living room is
**forbidden** in the social fund and **permitted** in the private and commercial
funds.

⭐ **So a rate measured over a mixed-tenure corpus is a mixture of two populations
that the one standard addressing this quantity deliberately holds to different
requirements.** Under a *bar*, the fix is trivial — pick which programme the Brief
is for. Under *distribution matching*, there is no fix: the mixture proportion of
the corpus silently becomes part of the target, and it is a property of Swiss
housing tenure rather than of good design.

⚠️ **This is not a claim that Swiss Dwellings' tenure mix has been measured.** It
has not been, here or anywhere in the repo. The point is that the corpus rate
*inherits* a mixing parameter it does not record, and a bar does not.

---

## 7. What this hands `proposer.md` §6.1

Six things, in decreasing order of how much they change the decision:

1. ⭐⭐ **The bedroom limb of D10 already has statutory backing in the engine's own
   region and is already a hard rule** — AzDTN 2.7-2 cl. 5.9, `is_private`, C6 item 1
   (§3.5). **What §6.1's fifth term would add is the *ordering* half, which has no
   statutory backing in either lineage.** Say so in the term's scope statement:
   *"on the path to"* is law; *"nearer the entrance than"* is engine choice.
2. ⭐⭐ **If the term is scored against corpus practice at all, make it one-sided,
   and cite ЖК РФ art. 50 for the shape** (§4.3). An observed-practice bound in the
   improving direction is a real legal construction; a two-sided match on a defect
   rate is not, anywhere in either lineage.
3. ⭐ **Take WBS's `Vergleichen` pattern for the reporting** (§2.1): score against a
   bar, and print the corpus rate *beside* the score as context. That is what the
   only official instrument for this corpus does, and it costs nothing.
4. ⭐ **Cite СП 54.13330 cl. 5.6 for the social/private asymmetry** (§3.4). Both
   room classes are constrained; only the social one is ever relaxed. The engine's
   partition matches a standard's partition, and the standard says which half is
   load-bearing.
5. ⚠️ **Record that WBS — the Swiss federal instrument for the Swiss corpus —
   scores none of this and treats rooms as `nutzungsneutral`** (§3.2). Anyone who
   asks *"if this mattered, wouldn't the Swiss score it?"* deserves the answer in
   the file rather than in a reviewer's head.
6. ⚠️ **Note the tenure mixing in the corpus rate** (§6), or drop the claim that the
   rate is a property of good design rather than of Swiss tenure structure.

---

## 8. Direct answers

**Q1 — bar or distribution?** **Bar, in both, unambiguously.** WBS: a graded
0–4-point scale per criterion against a printed lookup table, 100 points total
(§2.1, scoring clause quoted). СП 54.13330 / AzDTN 2.7-2: hard thresholds with no
score at all — `должна быть не менее`, `проектируют`, `не допускается`;
`məcburi` / `tövsiyə` (§2.3, §2.4). **Neither computes anything over a population of
existing dwellings.** WBS's only reference to other buildings is presentational
(`Objektbeispiele`) and happens after scoring.

**Q2 — zoning / privacy / entry sequence?** **WBS: no, on all three, and
deliberately** — `Zonierung` 0, `Durchgangszimmer` 0, `Tag/Nacht` 0, rooms declared
`nutzungsneutral`, privacy provided by a lock (§3.1, §3.2). **СП 54.13330: yes, one
of the three.** cl. 5.6 — *«в 2-, 3- и 4-комнатных квартирах спальни и общие жилые
комнаты (гостиные) проектируют непроходными»*, with the living-room limb lifted in
private and commercial tenure (§3.4). **AzDTN 2.7-2 cl. 5.9** states the bedroom
limb alone, mandatory, no exemption (§3.5). ⚠️ **Neither СП nor AzDTN constrains
depth from the entrance** — the passage prohibition is about being *on the path*,
not about being *nearer the door*.

**Q3 — how was the level chosen?** WBS: a named eleven-member `Expertengruppe`,
with no statistical basis given for any threshold, and an authority argument built
on a *selected* set of 1920s/1950s exemplars (§4.1, §4.2). СП: normative tradition,
**with one delegation to observed stock** — ЖК РФ art. 50 §2's provision norm, set
by the municipality *"в зависимости от достигнутого … уровня обеспеченности
жилыми помещениями"* (§4.3). AzDTN: delegated to **ergonomics** (§4.4).

**Q4 — is reproducing existing stock named as wrong?** **No explicit statement, in
either.** Three structural facts point that way — WBS's new area ceiling, its
selected-exemplar authority, and СП's outright prohibition of a practice it
acknowledges is common in private housing — and one fact points the other way,
ЖК РФ art. 50's indexation to attained provision (§5).

**Does anything found support scoring a defect rate against the corpus's own
rate?** ⚠️ **Nothing supports it. One thing partially supports its *shape* and
refutes its *symmetry*.** ЖК РФ art. 50 shows a real legal system indexing a
threshold to observed practice — as a **one-sided floor on a quantity where more is
better**, which rises as practice improves. Applied to a defect rate the same
construction yields a **ceiling**, not a target: *no more often than observed*, with
zero occurrences scoring best. **Every other mechanism in both lineages refutes
corpus-rate scoring outright**, most sharply WBS 2015's decision to add a *maximum*
floor area precisely where the Swiss stock was drifting upward, and СП 54.13330
cl. 5.6's decision to prohibit the passage room in the fund it governs while
recording that the other fund does it routinely.

---

## 9. What could not be read

⚠️ **WebFetch cannot read either BWO PDF.** Both requests returned the raw
compressed PDF object stream and the summarising model correctly refused to guess
at it. Both files were downloaded to the tool-results directory by WebFetch itself
and were then extracted with `pdftotext -layout -enc UTF-8`. **Anyone re-running
this note must do the same; do not trust a WebFetch summary of a BWO PDF.** The
same is true of the СП 54.13330.2022 PDF, which was fetched with `curl` and
extracted locally.

| not obtained | why | where it was looked for |
|---|---|---|
| **AzDTN 2.7-2 PDF, fetched fresh in this session** | The web-search budget for the session was exhausted before the Azerbaijani leg. **Not needed**: the norm was already read first-hand for tickets 31/69 and its clauses 5.1–5.10 are transcribed in `docs/research/az-statutory-floor-transcription.md` and `docs/research/az-region-profile/minima.md`, with full provenance in `data/standards/room-constraints.json` (`az_azdtn_2_7_2`) | [arxkom.gov.az](https://arxkom.gov.az/qanunvericilik/normativler/binalarin-muhendis-sistemleri/zhilye-zdaniya), [e-qanun.az/framework/48625](https://e-qanun.az/framework/48625) |
| **AzDTN 2.13-1 full text** | Out of scope on inspection — it is the gas/engineering-systems norm, not a housing-quality instrument (§2.4). Its one plan-bearing clause, 8.31, is already transcribed in this repo | `data/standards/room-constraints.json`, `gas_note` |
| **The СП 54 Табл. 5.1 column headers as laid out in the original** | `pdftotext` reflows the table; the six values 28/44/56/70/84/103 and the room counts 1–6 were recovered from adjacent text runs and are ⚠️ **reconstructed pairings**, not read off a rendered table | local PDF, both `-layout` and reading-order extractions |
| **Any municipal `норма предоставления` bylaw** | Would establish how "attained level of provision" is computed in practice. Not attempted — out of the two-lineage scope, and the statutory delegation is what the question needed | — |
| **WBS's underlying working papers / the 2015 revision report** | Would settle whether the `Expertengruppe` consulted any survey data. Nothing beyond the brochure and the criteria table is published on the BWO page | [bwo.admin.ch/wbs](https://www.bwo.admin.ch/de/wohnungs-bewertungs-system-wbs) |
| **A bar set at an observed *percentile* of real stock** | ⭐ **Searched for in both lineages and not found.** The nearest construction is ЖК РФ art. 50's indexation to an attained *level*, which is a ratchet on a mean-like quantity, not a percentile of a distribution (§4.3). **If this construction exists in a housing standard, it is not in these two** | full text of both instruments |

⚠️ **Session limitation:** the WebSearch budget (200 calls) was exhausted by earlier
work in this session before the Azerbaijani leg began. All Azerbaijani findings
above therefore rest on transcriptions already committed to this repo and marked
`read_first_hand: true`, not on a fresh reading of the norm.
