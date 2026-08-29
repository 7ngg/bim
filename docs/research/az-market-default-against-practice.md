# `market_default` against actual practice — what a Baku kitchen-diner is built at

Findings for the research question *What area is a kitchen-dining room
(`mətbəx-yemək otağı`) actually built at in Baku, and how far is the `AZ`
profile's `market_default` tier from real Azerbaijani practice?*

**It closes the gap.** `docs/research/az-statutory-floor-transcription.md` §10
item 6 left it open (*"Nothing about `market_default` against actual Baku
practice"*), `docs/research/az-region-profile/minima.md` §7.4 left it open before
that (*"Baku private-sector practice and any MİDA space standard were NOT
obtained … worth closing before the profile ships"*), and
`room-constraints.json` ships the same statement as
`profiles.AZ.what_could_not_be_obtained.market_practice`. **All three are now
out of date** — see §6 — and the profile's field is the one that needs editing,
because it is published.

**C8 applies to every number below.** These are dimensional standards with a
citation, not a compliance claim. Nothing here is claimed to a Homeowner.

**This note edits no shipped artefact.** `data/standards/room-constraints.json`,
`data/acceptance/rules.json` and `docs/spec/` are untouched; the defects found are
handed on, not fixed.

**Its sibling, and the boundary between them.**
`docs/research/az-kitchen-diner-whole-room.md` was written alongside this note and
answers a **different** open item — ticket 70's *"what IS the whole-room statutory
floor for a `mətbəx-yemək otağı`"* — by sweeping the Azerbaijani norm corpus. This
note answers the **`market_default`** question: what the tier is, what it is
against a measured room population, and whether Baku practice can replace it. The
two agree everywhere they touch, and two side findings were reached independently
in both (§2.2's clause-citation defect, §2.3's aspect rule); where that happens it
is recorded as concurrence, which is stronger than either alone.

**Copyright posture is inherited, not relaxed.** `minima.md` §7.1 records that
AzDTN 2.7-2 cl. 5.1's Table 1 is substantially SNiP 2.08.01-89\* Table 5 carried
forward, and that transcribing its *selection and arrangement* is the specific
infringement findings §7.6 item 7 names. **The table is not reproduced here.**
Individual cells the product's own 1–4 otaq promise needs are cited one by one,
which is what §7.1 already did for three of them.

---

## 0. TL;DR

**The headline is a reversal.** Both prior notes recorded that no Baku or MİDA
per-room data could be obtained, and the profile ships a `what_could_not_be_obtained.market_practice`
entry saying so. **It can be obtained.** MİDA publishes a full room schedule for
every apartment type it sells, through an undocumented public JSON API its own
website calls. Against that population the shipped tier is mostly **right** — and
wrong in two specific places, one of which nobody was checking.

| # | Finding |
|---|---|
| **1** | ⭐ **`market_practice` is no longer a gap. 318 distinct Baku plan geometries with per-room areas were obtained, and the measurement plane is confirmed.** `api.mida.gov.az/api/front/getApartment/{id}` returns the published *eksplikasiya* per apartment type. Two endpoints were re-fetched first-hand and the room areas **sum to `internal_size` exactly**, which proves the schedule is **net internal** — the plane ADR 0010 makes the Space polygon. §6.1. |
| **2** | ⭐ **Three of the seven area cells land on Azerbaijani practice.** `kitchen` 9,0 against a MİDA median of **9,06** — agreement to 0,06 m². `bedroom_double` 12,0 against 13,20 and `living_room_2plus` 16,0 against 17,60, both ratio 1,10. The tier is much better than the Swiss comparison implied, because it is an Azerbaijani number answering an Azerbaijani question. §6.3. |
| **3** | ⚠️ **One cell is wrong in the direction nobody was checking: `bathroom_combined` 3,8 m² is ABOVE what Baku builds.** 63,5 % of MİDA's main sanitary rooms are smaller than the engine's soft target (p50 3,51). §5 measured this cell against Swiss rooms, found it on the median to two decimals, and concluded it *"needs nothing"*. **Two corpora, opposite verdicts, and the Azerbaijani one is the region the profile claims.** §6.3. |
| **4** | **`mətbəx-yemək otağı` does not occur in MİDA's vocabulary at all** — zero times in 5,954 type records; the whole residential vocabulary is **eight room names**. MİDA's open-plan room is `Mətbəx-studio`, it is in **5 of 318 plans (1,57 %)**, and it is in **0 multi-room apartments**. Every 2-, 3- and 4-otaq MİDA plan has a separate kitchen and a separate living room. §6.4. |
| **5** | ⭐ **Two independent measurements of what an open-plan cooking room costs agree at ≈18 m².** MİDA's `Mətbəx-studio` p50 **17,37** (n = 5 plans) and the Swiss `KITCHEN`+`DINING` sum p50 **18,83** (n = 1,308 dwellings). The shipped target is **6,0** — a factor of **2,9**. §4.4, §6.3. |
| **6** | ⭐ **A gas rule decides the open-plan question, and it splits the two open-plan types.** AzDTN 2.13-1 cl. 8.31 (mandatory) requires a gas hob to sit in a **`mətbəx otağı`**. AzDTN 2.7-3 cl. 4.7 files `mətbəx-yemək otağı` *inside* the word kitchen — so a **kitchen-diner is compliant with gas**, while a **kitchen-LIVING room is not**, absent an electric hob. MİDA fits gas hobs. §6.5. |
| **7** | **The whole `market_default` tier is a set of RECOMMENDED MINIMA, and the tier model calls it "what is actually built".** AzDTN 2.7-3 cl. 5.1's register is *«aşağıdakılardan **az olmamaqla** qəbul edilməsi tövsiyə edilir»* — "recommended to be adopted **not less than**". A not-less-than floor read as a target under-sizes; `soft_objective_target` reads it as a target. That the cells land near practice anyway (finding 2) is luck of a well-chosen minimum, not the tier being what it says it is. §2.1. |
| **8** | **All nine `market_default` values transcribe their clause correctly. Every one is confirmed verbatim, first-hand.** 16,0 / 9,0 / 12,0 / 9,0 / 6,0 / 3,2 / 3,8 and 3000 / 2600 mm. No numeric drift. §2. |
| **9** | ⚠️ **All six `clear_widths_mm` cells cite the wrong clause.** They carry `ref: "cl. 5.4"`. The width list is inside **cl. 5.1**, immediately after the area list; AzDTN 2.7-3 cl. 5.4 is about ground bearing and load-bearing structure and contains no room dimension at all. Same failure class as ticket 70 — the value is right and its referent is wrong. §2.2. |
| **10** | **AzDTN 2.7-3 constrains the kitchen ZONE too, so the referent defect is not a mis-transcription of one document — both instruments say zone.** cl. 5.1: *«mətbəx-yemək otağında **mətbəx zonası** - 6 m²»*. **No Azerbaijani instrument publishes a whole-room area for a `mətbəx-yemək otağı`, at any tier.** §3. |
| **11** | ⚠️ **The Swiss 23,67 m² that would replace it does not measure a kitchen-diner.** Re-measured first-hand: of the 41 `KITCHEN_DINING` rooms, **40 sit in a dwelling that also contains a separate `KITCHEN`**. The label is a dining room beside a kitchen, not a kitchen and dining in one room. It is not the same object as `mətbəx-yemək otağı`. §4.1. |
| **12** | ⚠️ **And 23,67 is an artefact of replication.** The 41 rooms are **21 distinct plans**; one site contributes 24 rooms that are 4 plans × 6 identical copies. Median over distinct plans is **35,68 m²**, not 23,67 — the replicated plans all sit at the bottom of the range, so duplication drags the median down **12,0 m²**. §4.2. |
| **13** | **The type is vanishingly rare on the retrieval side: 41 of 44,894 residential dwellings, 0,091 %.** Whatever is decided for `kitchen_dining` is decided for one dwelling in eleven hundred *of the corpus*. Low exposure is now measured on the supply side, not assumed. §4.3. |
| **14** | **A comparator that does match the object gives ≈18,8 m², on 32× the sample.** In dwellings holding both a `KITCHEN` and a `DINING` room, the two sum to p50 **18,83 m²** (p25 15,53, p75 22,51) over **1,308 dwellings in 160 sites** — against 41 rooms in 10 sites for the label. Still Swiss, still `fitted`, still not promotable — but it bounds the argument, and the shipped 6,0 is a third of it. §4.4. |
| **15** | **Against the Swiss pool the tier is not uniformly low — it is low on habitable rooms, HIGH on kitchens, and exactly on the median for sanitary units.** The AZ target sits at pool percentile **p1,6** for a single bedroom, **p9** for a living room, **p63** for a kitchen and **p51** for a combined sanitary unit. The pattern is real and cultural, not noise. §5. |
| **16** | ⚠️ **`rules.json` `dim.aspect_ratio_hard` says *"No surveyed source states an aspect rule"*, and that is now false.** AzDTN 2.7-3 cl. 5.1's last sentence recommends a habitable room's length not exceed **2× its width**. It is `tövsiyə olunur` (recommended) and detached-house scope — but it exists, and it lands beside the fitted soft threshold of 2,2. §2.3. |
| **17** | **AzDTN declines to speak about the housing this engine's Homeowner buys.** cl. 5.1's recommended totals are scoped to the **state and municipal** fund; for the **private** fund the same clause says area, room count and composition are *«sifarişçi tərəfindən müəyyən edilir»* — determined by the client. Baku new-build is overwhelmingly private. §7.1. |

---

## 1. What was read first-hand

Two Azerbaijani norms, from the copies already cached in this repo, re-extracted
and re-read for this note rather than inherited from `minima.md`.

| file | md5 | document |
|---|---|---|
| `experiments/finish-layer/src/azdtn_2_7_2.pdf` | `4b5da47dd11808cd0aef37a75b01b4e9` | **AzDTN 2.7-2** *Yaşayış binaları. Layihələndirmə normaları* — multi-apartment residential, Baku 2021 |
| `experiments/finish-layer/src/azdtn_2_7_3.pdf` | `d615accb5950c825bed4e3cfbadf6842` | **AzDTN 2.7-3** *Fərdi yaşayış evləri. Layihələndirmə normaları* — **individual (detached) houses**, Baku 2023 |

The 2.7-2 md5 matches the one
`docs/research/az-statutory-floor-transcription.md` §1 recorded, so this is the
same document that note verified, not a second copy.

A third norm was downloaded live from the issuing authority during this session
and read for §6.5:

| served from | document |
|---|---|
| `arxkom.gov.az/qanunvericilik/normativler/muhendis-sistemleri/qaz-techizati-layihelendirme-normalari` | **AzDTN 2.13-1** *Qaz təchizatı. Layihələndirmə normaları* (Gas supply. Design norms), 111 pp., order No. 17 of 2009-03-02, in force 2009-04-01, in place of СНиП 2.04.08-87\* |

And two Azerbaijani data sources, neither of them a document:

| source | what it is |
|---|---|
| `api.mida.gov.az/api/front/getApartment/{id}` | MİDA's published per-apartment room schedule — §6 |
| `data/corpora/swiss-dwellings/swiss-dwellings-v3.0.0/geometries.csv` | the retrieval corpus, measured for §4, §5 and §7.4 |

Harness: `experiments/baku-market-areas/azdtn_clauses.py`, which prints the
clause bodies verbatim so the quotations below can be re-checked in one command.

---

## 2. The nine `market_default` values, clause by clause

### 2.1 The areas — and the register that decides what they are

AzDTN 2.7-3 cl. 5.1, verbatim, with its own lead-in:

> Layihələndirilən və yenidən qurulan fərdi evlərin yerləşgələrinin sahələri
> **aşağıdakılardan az olmamaqla qəbul edilməsi tövsiyə edilir**:
>
> - ümumi otaqlar (və ya qonaq otağı) - 16 m²;
> - yataq otağı – 9 m² (iki nəfərə 12 m², mansardda yerləşdirdikdə - 8 m²);
> - təkərli oturacaq təyin edilmiş əlilliyi olan şəxslərin: yataq otağı - 9 m²;
> - mətbəx - 9 m²;
> - mətbəx-yemək otağında **mətbəx zonası** - 6 m²;
> - hamam otağı - 3,2 m²;
> - birləşdirilmiş sanitar qovşağı - 3,8 m².

*"It is **recommended** that the areas of rooms in individual houses being
designed or reconstructed be adopted **not less than** the following."*

| profile cell | value | confirmed | Azerbaijani term | conf |
|---|---|---|---|---|
| `living_room_1room_flat` / `living_room_2plus` | 16,0 | ✅ | *ümumi otaqlar (və ya qonaq otağı)* | `verified` |
| `bedroom_single` | 9,0 | ✅ | *yataq otağı* | `verified` |
| `bedroom_double` | 12,0 | ✅ | *iki nəfərə* | `verified` |
| `bedroom_mansard` | 8,0 | ✅ | *mansardda yerləşdirdikdə* | `verified` |
| `kitchen` | 9,0 | ✅ | *mətbəx* | `verified` |
| `kitchen_zone_in_diner` | 6,0 | ✅ **as a ZONE** | *mətbəx-yemək otağında mətbəx zonası* | `verified` |
| `bathroom` | 3,2 | ✅ | *hamam otağı* | `verified` |
| `bathroom_combined` | 3,8 | ✅ | *birləşdirilmiş sanitar qovşağı* | `verified` |
| `bedroom_single.accessible` | 9,0 | ✅ | *təkərli oturacaq … yataq otağı* | `verified` |

**Nine for nine on the number. Zero for nine on what kind of number it is.**

`tier_model.tiers.market_default` defines the tier as *"What is actually built and
what a Homeowner expects"*. Every value above is a **recommended minimum** — the
clause says *az olmamaqla* in the same breath as *tövsiyə edilir*. It is a floor
on the recommended, published by a regulator, for a building type that is not an
apartment. It is not a description of the market and does not claim to be.

The consequence is structural rather than per-cell:
`validator_binding.soft_objective_target` is `market_default`, and `brief.md` §9.2
sizes every silent Room to it. **A minimum used as a target under-sizes by
whatever the gap between the minimum and the ordinary is** — and §5 measures that
gap on the only room population on disk.

The `accessible` bedroom line also settles a question the profile left as a note:
AzDTN 2.7-3 really does put a wheelchair user's bedroom at the same 9 m² as an
ordinary one, in its own list. The profile's *"NOT an accessibility uplift"* note
is correct and is now `verified` from the clause rather than inferred.

### 2.2 The widths — right numbers, wrong clause

Immediately after the area list, still inside cl. 5.1:

> Otaq və yerləşgələrin eni aşağıda qeyd olunan ölçülərdən az olmayaraq **qəbul
> edilməlidir**:
> - yaşayış otaqları - 3,0 m;
> - mətbəx - 2,6 m;
> - dəhliz - 1,4 m;
> - hamam - 1,5 m;
> - ayaqyolu - 0,8 m, əl-üz yuyanla olduqda - 1,2 m.

| profile cell | value | confirmed | conf |
|---|---|---|---|
| `clear_widths_mm.habitable_room` | 3000 | ✅ | `verified` |
| `clear_widths_mm.kitchen` | 2600 | ✅ | `verified` |
| `clear_widths_mm.hall_corridor` | 1400 | ✅ | `verified` |
| `clear_widths_mm.bathroom` | 1500 | ✅ | `verified` |
| `clear_widths_mm.wc` | 800 | ✅ | `verified` |
| `clear_widths_mm.wc_with_basin` | 1200 | ✅ | `verified` |

⚠️ **All six cite `ref: "cl. 5.4"`. The text is in cl. 5.1.** AzDTN 2.7-3 cl. 5.4
reads *«Evin qrunt əsası və konstruksiyaları AzDTN 2.1-1-in tələblərinə görə
müvafiq normativ yüklərə və təsirlərə hesablanmalıdır»* — the house's ground base
and structures shall be calculated for normative loads — and contains no room
dimension.

Nothing numeric moves. What moves is checkability: a Practitioner following the
citation lands on a structural clause and concludes the profile invented the
number. That is the **referent** failure ticket 70 exists for, in a second place,
across six cells rather than one.

⚠️ **A register split inside one clause, and it is confirmed.** The AREA list is
`tövsiyə edilir` (recommended); the WIDTH list is **`qəbul edilməlidir`** — the
mandatory register. `az_azdtn_2_7_3`'s `force_note` already records this split
(*"Within cl. 5.1 the AREA list is recommended while the WIDTH list is
mandatory"*), and reading the clause confirms it. It changes nothing today,
because the widths are transferred to apartments and degrade to
`derived`/recommended anyway, and because `dim.market_default_area` is an area
term with no width counterpart — `rules.json` already records that the soft width
target is read by nobody.

### 2.3 A source for the aspect rule, which `rules.json` says does not exist

The last sentence of cl. 5.1:

> Yaşayış otağının uzunluğunun eninə nisbətən **2 dəfədən çox olmayaraq** qəbul
> edilməsi tövsiyə olunur.

*"It is recommended that a habitable room's length be adopted as not more than
**2 times** its width."*

`rules.json` `dim.aspect_ratio_hard` opens with *"No surveyed source states an
aspect rule."* **A surveyed source states one**, in the same clause every
`market_default` area comes from, and it was read past. It is `tövsiyə olunur`
(recommended) and detached-house scope, so it cannot bind an apartment hard —
but the fitted soft threshold `dim.aspect_ratio_soft` is **2,2**, the Swiss p95,
and AzDTN's recommendation is **2,0**. An engine_choice fitted from a Swiss corpus
landing within 10 % of the one regulatory statement in the shipping region is
corroboration worth recording, and the prose claim needs correcting either way.

**Handed on, not taken:** this is `rules.json`'s field and a profile cell that
does not exist yet. It is not this note's to write.

---

## 3. The kitchen-diner: no whole-room figure exists

AzDTN 2.7-2 cl. 5.7, verbatim:

> - mətbəx-yemək otağında **mətbəx zonası** - 6 m²-dən.

AzDTN 2.7-3 cl. 5.1, verbatim:

> - mətbəx-yemək otağında **mətbəx zonası** - 6 m².

**Both instruments constrain the zone. Neither constrains the room.** Ticket 70
established this for the statutory limb from 2.7-2; it holds identically for the
`market_default` limb from 2.7-3, which had not been checked. So the defect is not
one clause mis-read — the profile has **two cells pointing at the same zone
provision in two documents**, and a room type whose area no Azerbaijani instrument
states at any tier.

`profiles.AZ.rooms.mapping.rooms.living_dining_kitchen` already says the general
form of this out loud — *"AzDTN has no open-plan type"* — and that is confirmed:
the norm names `mətbəx-yemək otağı` only to floor the cooking zone inside it, and
never gives it a room area, a width, or a place in cl. 5.2's required composition.

**What this means for the tier.** `market_default` for `kitchen_zone_in_diner` is
6,0 and it is *correct as a zone recommendation*. There is no Azerbaijani number
to raise it to. Filling the whole-room cell requires either a measurement from
outside Azerbaijan (§4 shows the obvious candidate does not survive) or an
`engine_choice` labelled as one.

---

## 4. The Swiss comparator, re-measured — and why it cannot stand in

Measured on this machine against
`data/corpora/swiss-dwellings/swiss-dwellings-v3.0.0/geometries.csv`, 3,255,905
rows, **442,019 residential `area` polygons**, harness
`experiments/baku-market-areas/`. The class counts reproduce
`docs/research/dataset-inventory.md` §1.4 exactly (`ROOM` 82,618, `SHAFT` 72,255,
`BATHROOM` 68,434, `CORRIDOR` 53,392, `KITCHEN` 44,085), which is the check that
the harness reads the corpus the same way the rest of the map does.

`KITCHEN_DINING`, all 41 rooms: min **20,90**, p25 23,00, **p50 23,67**, p75
35,68, max 85,24 m², across **10 sites**. This reproduces the 23,67 already quoted
in `docs/spec/acceptance-bar.md` §11 and ticket 50. Three findings follow, and
each one on its own disqualifies the number.

### 4.1 It is not a kitchen-diner

| | n | share |
|---|---|---|
| `KITCHEN_DINING` rooms whose dwelling **also has a separate `KITCHEN`** | **40 / 41** | **97,6 %** |
| distinct plans whose dwelling also has a separate `KITCHEN` | **20 / 21** | **95,2 %** |
| dwellings that also have a `LIVING_ROOM` or `LIVING_DINING` | 2 / 41 | 4,9 % |

A `mətbəx-yemək otağı` is a room that **is** the kitchen and the dining room. A
Swiss `KITCHEN_DINING` room is, in 40 cases out of 41, a room in a dwelling that
has a kitchen somewhere else. Whatever the label denotes there — an eat-in dining
room, a second reception space — **it is not the object the AZ cell names**, and a
median of it is not a median of a kitchen-diner.

The single genuine open-plan case is site 3823: a 41,56 m² `KITCHEN_DINING` in a
dwelling of `BATHROOM` 6,9 + `CORRIDOR` 16,7 + `ROOM` 34,6 and no kitchen. **n = 1.**

### 4.2 It is an artefact of replication

The 41 rooms are **21 distinct apartment plans**. One site (`11176`) supplies 24 of
the 41 — as **four plans, each appearing six times**, identical room-for-room.

| statistic | over 41 rooms | over 21 distinct plans |
|---|---|---|
| median | **23,67** | **35,68** |
| min | 20,90 | 20,90 |
| max | 85,24 | 85,24 |

The four replicated plans sit at 22,96 / 23,00 / 23,51 / 23,67 m² — the **bottom**
of the range. Replication therefore drags the median down by **12,0 m²**, and the
figure the map has been quoting is close to *"one Swiss apartment type, counted
twenty-four times"*.

**Where the number is quoted, and whether it matters there.** 23,67 appears in
`docs/spec/acceptance-bar.md` §11 and in ticket 50, both times as the "Swiss p50"
column of a table whose point is that the 6,0 statutory floor rejects **0 %** of
real `KITCHEN_DINING` rooms. **That conclusion survives** — 0 % is 0 % whether the
class holds 41 rooms or 21 plans. What does not survive is reading the column as a
usable median. Neither site carries an n, and the row invites exactly the
substitution this note refuses.

### 4.3 The type is rare on the supply side too

| | value |
|---|---|
| residential dwellings in Swiss Dwellings v3.0.0 | **44,894** |
| dwellings containing a `KITCHEN_DINING` | **41** |
| share | **0,091 %** |
| sites | 10 of 1,459 |

So exposure is small on both sides at once: the type is 0,091 % of the retrieval
pool, and its prevalence in Baku is what §6 went looking for. This is the sentence
the question asked for — **the kitchen-diner is a low-exposure case** — and it is
now measured rather than asserted, at least for the corpus half.

⚠️ **`fitted`, and thinner than any `fitted` number on this map.** Every figure in
§4.1–§4.3 is a statistic of Swiss Dwellings, not of Azerbaijan. n = 21 distinct
plans across 10 sites is below anything the map elsewhere treats as measurable.
**Nothing in §4.1–§4.3 may be promoted into `market_default`.** Their only use is
negative: they remove 23,67 from consideration.

### 4.4 A comparator that does match the object, with 32× the sample

If the corpus label is the wrong object, ask the corpus the question the object
poses. A `mətbəx-yemək otağı` **is** the kitchen and **is** the dining room, and
the ergonomic key `kitchen_dining` is defined in this repo as *"packed from
kitchen and dining"*. So: in dwellings that hold **both** a `KITCHEN` and a
`DINING` room, what do the two sum to? That is the area one room must hold to do
both jobs.

Harness `experiments/baku-market-areas/swiss_kitchen_plus_dining.py`.
**n = 1,308 dwellings, 160 sites, largest site 12,2 %.**

| quantity | min | p25 | **p50** | p75 | p95 | max |
|---|---|---|---|---|---|---|
| `KITCHEN` + `DINING`, summed | 4,84 | 15,53 | **18,83** | 22,51 | 34,79 | 56,24 |
| `KITCHEN` alone, same dwellings | 1,39 | 6,87 | 7,53 | 9,24 | 12,70 | 29,15 |
| `DINING` alone, same dwellings | 2,37 | 8,20 | 10,41 | 14,01 | 25,02 | 44,36 |

**≈18,8 m², not 23,67 and not 6,0.** Against the `KITCHEN_DINING` sample that
§4.1–§4.3 disqualified, this is **32× the dwellings and 16× the sites**, and the
single-site concentration falls from 58,5 % to 12,2 %. It is the strongest
available number for the question, and it is still Swiss.

Three caveats, all in the same direction or stated:

- **It is an upper bound on the combined room.** Two rooms carry two sets of
  circulation and two door swings; one room carrying both jobs shares them. So a
  real combined room should land at or below the sum, not above it.
- **`DINING` is itself a thin, concentrated class** — 1,315 rooms over 160 sites
  with 12,1 % from one site. Better than 41 over 10, not good.
- **It is `fitted`, Swiss, and may not be promoted to `market_default` either.**
  What it can do is bound the argument: any whole-room figure for
  `mətbəx-yemək otağı` that comes out below the ergonomic 4,6 is wrong, and one
  that comes out near 6,0 is asserting that an Azerbaijani kitchen-diner is a
  third the size of a Swiss kitchen-plus-dining. The engine currently asserts
  exactly that.

**An AZ-internal cross-check, for the same order of magnitude.** AzDTN's own zone
recommendation is 6,0 m² for the cooking zone. The repo's ergonomic floor for a
standalone `dining` is 1,9 m² and for a `kitchen` 1,8 m² — body-derived minima,
not typical sizes — so AZ + ergonomics can only bound the room *below*, at 6,0
plus a dining part. It cannot produce a target. The Swiss 18,83 is the only
number in this note with a sample behind it.

⚠️ **Do not read the sibling note's ≈8 m² as a target.**
`az-kitchen-diner-whole-room.md` finding 4 derives ≈8,0 m² for the whole room two
independent ways — from AzDTN's own taxonomy (an unzoned `mətbəx`, which the norm
defines as also for eating, floors at 8) and from 6,0 + the ergonomic `dining`
1,9 = 7,9. **That is a FLOOR candidate and this is a TARGET question**, and the
two tiers are different fields with different bindings. A floor near 8 and a
target near 19 are consistent with each other and with §5's pattern; collapsing
them is the same tier confusion §2.1 identifies as the tier's main defect.

---

## 5. Where the tier actually sits in the pool the engine retrieves from

For each `market_default` cell, the share of real Swiss rooms **below** the number
the solver aims at. Harness `experiments/baku-market-areas/swiss_vs_az.py`.

| AZ cell | target | Swiss class | n | Swiss p50 | target's percentile in the pool | p50 ÷ target |
|---|---|---|---|---|---|---|
| `bedroom_single` | 9,0 | `ROOM`+`BEDROOM` | 105,615 | 14,28 | **p1,6** | 1,59 |
| `living_room_2plus` | 16,0 | `LIVING_DINING` | 24,200 | 28,44 | **p2,7** | 1,78 |
| `living_room_2plus` | 16,0 | `LIVING_ROOM` | 8,459 | 20,63 | **p9,1** | 1,29 |
| `bedroom_double` | 12,0 | `ROOM`+`BEDROOM` | 105,615 | 14,28 | p25,2 | 1,19 |
| `bathroom` | 3,2 | `BATHROOM` | 68,434 | 3,78 | p30,7 | 1,18 |
| `bathroom_combined` | 3,8 | `BATHROOM` | 68,434 | 3,78 | **p50,8** | 0,99 |
| `kitchen` | 9,0 | `KITCHEN` | 44,085 | 8,04 | **p63,3** | 0,89 |
| `kitchen_zone_in_diner` | 6,0 | `KITCHEN_DINING` | 41 | 23,67 | p0,0 | 3,94 |

**The tier is not uniformly low, and that is the finding.** Three regimes:

1. **Habitable rooms — the target is near the floor of the distribution.** The
   solver aims a single bedroom at a size **98,4 % of real rooms exceed**, and a
   living room at a size 97,3 % of real living/dining rooms exceed. This is
   exactly what §2.1 predicts: a recommended *minimum* used as a *target*.
2. **The kitchen — the target is ABOVE the median.** AZ wants 9,0 m² where the
   Swiss build 8,04. This is the one cell where `market_default` is more generous
   than the corpus, and it is not an error: post-Soviet norms treat the kitchen as
   a room, Swiss practice increasingly does not. It is also already known to bite —
   `acceptance-bar.md` records the statutory 8,0 landing on the corpus median and
   costing 16,88 of 19,98 marginal rejection points.
3. **Sanitary — the target is the median.** `bathroom_combined` 3,8 against a
   Swiss p50 of 3,78 is agreement to two decimal places, and the profile's own
   `reachable_in_v1` note independently measured 4,25 m² over 35,821 real bath+WC
   rooms.
   ⚠️ **This is the one conclusion §6 overturns.** Against MİDA's Baku schedules
   the same cell is the profile's most **over**-shot value — 63,5 % of Azerbaijani
   main bathrooms are smaller than 3,8. Two corpora, opposite verdicts, and this
   is the clearest demonstration in the note that a Swiss median is not a
   substitute for an Azerbaijani one. Read §6.3 before acting on this row.

⚠️ **What this comparison is and is not.** It is `fitted` on the Swiss side and
`verified` on the AZ side, and the two sides are different *kinds* of quantity — a
regulator's recommended minimum against a distribution of built rooms. A minimum
landing at p1,6 is not per se a defect; it is a defect **because the field is read
as `soft_objective_target`**. The comparison measures the tier against the pool the
engine actually retrieves from, which is the population that matters for what the
engine emits — it does **not** measure the tier against Baku, and cannot.

---

## 6. Baku practice — the negative does not hold

`minima.md` §7.4 and `az-statutory-floor-transcription.md` §10 item 6 both record
that no Baku or MİDA space data could be obtained. **That is no longer true.**
MİDA publishes a **full per-room schedule for every apartment type it sells**, and
the whole dataset is reachable without credentials.

### 6.1 Where it is, and why nobody found it

`mida.gov.az` is a client-side React application, so every prior attempt — this
repo's included — fetched the shell and concluded there was nothing there. The
React bundle calls an undocumented public JSON API:

```
https://api.mida.gov.az/api/front/getApartment/{id}
```

which returns, per apartment type, the published **eksplikasiya**: each room's
Azerbaijani name, its area in m², its legend order number, plus `internal_size`
and `external_size`.

**Verified first-hand, not taken on report.** Two endpoints were fetched directly
during this session and checked against the harvest:

| endpoint | `internal_size` | Σ of the room schedule |
|---|---|---|
| `getApartment/600007` (4-otaq, Hövsan 2) | 98,95 | 11,70 + 18,72 + 10,91 + 12,30 + 16,80 + 15,23 + 3,51 + 3,40 + 3,38 + 3,00 = **98,95** |
| `getApartment/100025` (3-otaq, Yasamal 2) | 75,88 | 10,06 + 18,76 + 10,27 + 12,93 + 14,65 + 1,97 + 2,40 + 3,64 + 1,20 = **75,88** |

**The rooms sum to `internal_size` exactly**, which settles the measurement
plane — the schedule is a **net internal** breakdown, the same quantity ADR 0010
makes the Space polygon. `external_size` runs a median **1,21×** larger, and
MİDA's own price list names the two columns *Xarici perimetr üzrə sahə* and
*Daxili perimetr üzrə sahə* (area by external / by internal perimeter). **There is
no balcony coefficient**: `Eyvan` is carried inside `internal_size` at full area.

### 6.2 What it says

The harvest covers the five populated Baku projects — Hövsan, Hövsan 2, Yasamal,
Yasamal 2, Binəqədi: **5,954 apartment-type records**, 4,701 after a sanity
filter, collapsing to **318 distinct plan geometries**. Statistics recomputed
independently by `experiments/baku-market-areas/mida_room_schedules.py` rather
than taken from the harvest's own report.

⚠️ **Deduplication is not optional here, and §4.2 is why.** MİDA repeats one plan
across floors and entrances up to sixty times. Counting type rows would reproduce
exactly the replication artefact that destroys the Swiss median. The unit of
analysis below is the **distinct plan geometry**, keyed on the exact multiset of
(room name, area).

| MİDA room name | plans | rooms | p25 | **p50** | p75 | range |
|---|---|---|---|---|---|---|
| `Qonaq otağı` (living) | 312 | 312 | 16,05 | **17,60** | 18,33 | 9,07–27,70 |
| `Mətbəx` (kitchen) | 312 | 312 | 8,16 | **9,06** | 10,19 | 6,87–18,76 |
| `Yataq otağı` (bedroom, pooled) | 287 | 481 | 11,55 | **12,26** | 14,16 | 7,76–21,30 |
| `Sanitar qovşağı` (pooled) | 318 | 492 | 2,24 | **3,12** | 3,70 | 1,61–17,40 |
| `Dəhliz` (hall/corridor) | 318 | 320 | 6,92 | **9,52** | 10,06 | 2,49–20,60 |
| `Qarderob` (wardrobe) | 19 | 19 | 2,10 | **2,10** | 2,10 | 1,87–2,60 |
| `Eyvan` (balcony) | 315 | 584 | 1,92 | **2,57** | 3,40 | 0,30–22,56 |
| **`Mətbəx-studio`** (open plan) | **5** | **5** | 15,14 | **17,37** | 17,70 | 15,14–17,74 |

**MİDA's whole residential vocabulary is eight room names.** That is the entire
list — there is no ninth.

### 6.3 The comparison the question asks for

Pooled classes are unfair to two cells — `Sanitar qovşağı` covers both the main
bathroom and a second small WC, and `Yataq otağı` covers principal and secondary
bedrooms — so those rows are **rank-matched within each plan** before comparing.

| AZ `market_default` | target | matched MİDA class | plans | **MİDA p50** | share below target | p50 ÷ target |
|---|---|---|---|---|---|---|
| `kitchen` | 9,0 | `Mətbəx` | 312 | **9,06** | 47,4 % | **1,01** |
| `bedroom_double` | 12,0 | largest `Yataq otağı` per plan | 287 | **13,20** | — | 1,10 |
| `living_room_2plus` | 16,0 | `Qonaq otağı` | 312 | **17,60** | 17,9 % | 1,10 |
| `bedroom_single` | 9,0 | smallest `Yataq otağı`, 2+-bed plans | 159 | **11,45** | 6,9 % | 1,27 |
| `bathroom_combined` | 3,8 | largest `Sanitar qovşağı` per plan | 318 | **3,51** | **63,5 %** | **0,92** |
| `bathroom` | 3,2 | largest `Sanitar qovşağı` per plan | 318 | **3,51** | 28,6 % | 1,10 |
| `kitchen_zone_in_diner` | 6,0 | `Mətbəx-studio` | 5 | **17,37** | 0 % | **2,90** |

**The tier is far better than the Swiss comparison made it look, and the reason is
that it is an Azerbaijani number being asked an Azerbaijani question.** Against
Swiss rooms the bedroom target sat at pool percentile p1,6; against MİDA it sits
at p6,9. The kitchen target lands on the MİDA median to within **0,06 m²** — 9,0
against 9,06, which is the closest agreement anywhere in this note and is
presumably not a coincidence, since MİDA designs to the same regulator.

**Three cells are close enough to leave alone**: `kitchen` (ratio 1,01),
`bedroom_double` (1,10) and `living_room_2plus` (1,10).

**One cell is wrong in the direction nobody was checking.** `bathroom_combined`
at 3,8 m² is **above** what MİDA builds — 63,5 % of MİDA's main sanitary rooms are
smaller than the engine's soft target. The Swiss comparison (§5) put this cell
exactly on the median and concluded it *"needs nothing"*; against Azerbaijani
practice it is the most over-shot cell in the profile. Two corpora, opposite
verdicts, and the Azerbaijani one is the one that matches the region the profile
claims.

**And `kitchen_zone_in_diner` remains the outlier by a factor of three.**

### 6.4 The kitchen-diner in Baku: the term is not used, and the room is a studio device

| question | answer | evidence |
|---|---|---|
| Does `mətbəx-yemək otağı` appear in MİDA's room vocabulary? | **No — zero occurrences** across all 5,954 type records | `mida_room_schedules.py`; the vocabulary is eight names and none contains *yemək* |
| Does MİDA build an open-plan room at all? | Yes, called **`Mətbəx-studio`** | 5 of 318 distinct plans = **1,57 %** |
| In multi-room apartments? | **Never. 0 of 318** | every 2-, 3- and 4-otaq MİDA plan has a separate `Mətbəx` **and** a separate `Qonaq otağı` |
| What is it? | kitchen + living + dining in one room, 35–40 m² studios | plan drawing `1681974345-e3b4e5e30b269ecec465412f8424630a.png`, whose numbered legend (1 Dəhliz, 2 Mətbəx-studio, 3 Yataq otağı, 4 Sanitar qovşağı, 5 Eyvan) matches the API `order_number` exactly |

**So the type is norm-real and market-marginal.** AzDTN defines
`mətbəx-yemək otağı` in §3 as *«mənzildə yeməyin hazırlanması və qəbulu üçün
ayrıca zonaları olan otaq»* — a room with **separate zones** for preparing and
taking food — and AzDTN 2.7-3 cl. 4.7 files it **inside the word kitchen**:
*«mətbəx (o cümlədən mətbəx-yemək otağı)»*, an auxiliary space, not a
`yaşayış otağı`. That independently corroborates the profile's
`counts_as_otaq: false` for `kitchen_dining`, which had been `derived`.

⚠️ **A search-based prevalence claim is a weak instrument and is labelled as
one.** Beyond MİDA, exact-phrase searches for `mətbəx-yemək otağı`,
`mətbəx-qonaq otağı` and `кухня-гостиная`+Баку returned ≈48 results across four
phrasings, of which **none** were Azerbaijani developer plan sets or portal
listings; the Azerbaijani-language open-plan content that exists is **renovation
and interior-design marketing**, not new-build plans. `fitted` on n≈48 search
results is not a prevalence measurement, and the honest statement is: *no
Azerbaijani developer or portal source labelling such a room was found.*

### 6.5 The gas rule, which is the sharpest constraint found

**AzDTN 2.13-1 *Qaz təchizatı. Layihələndirmə normaları*** — read first-hand for
this note. The PDF was downloaded during this session from the issuing authority
at `arxkom.gov.az/qanunvericilik/normativler/muhendis-sistemleri/qaz-techizati-layihelendirme-normalari`
(111 pp.) and its front matter reads: *«Azərbaycan Respublikasının Dövlət
Şəhərsalma və Arxitektura Komitəsinin 02.03.09 tarixli 17 №-li əmri ilə təsdiq
edilib və 01.04.2009-cu ildən qüvvəyə minib … **СНиП 2.04.08-87\*-nin əvəzinə***»
— approved by order No. 17 of 2009-03-02, in force from 2009-04-01, **in place of
СНиП 2.04.08-87\***. Amended 2015 and 2023. Cl. 8.31, verbatim, mandatory
register:

> Yaşayış evlərində qaz pilətələrinin qoyulması nəfəslikli pəncərəsi, sorucu
> ventilyasiya kanalı və təbii işıqlandırılması olan, hündürlüyü 2,2 m-dən az
> olmayan **mətbəx otaqlarında** nəzərdə tutulmalıdır.

A gas hob **must** sit in a **`mətbəx otağı`** — a kitchen room — with an opening
light (`nəfəslik`), an extract duct and natural lighting, height not less than
2,2 m; volume not less than **8 / 12 / 15 m³** for 2- / 3- / 4-burner hobs.
Register `nəzərdə tutulmalıdır` + `az olmamalıdır` = **məcburi**. `conf: verified`
— extracted from the served PDF, not quoted from a secondary source.

**The asymmetry this creates is the decision-relevant finding**, and it is
`derived`, by the stated rule *"cl. 8.31 requires the hob's room to be a
`mətbəx otağı`; AzDTN 2.7-3 cl. 4.7 classifies a `mətbəx-yemək otağı` as a
`mətbəx`; neither norm classifies a kitchen-living room as one"*:

- a **`kitchen_dining`** (`mətbəx-yemək otağı`) **is** a kitchen room, so it is
  compliant with a gas hob;
- a **`living_dining_kitchen`** (a kitchen opened into a living room) is **not** a
  `mətbəx otağı`, and is non-compliant with a gas hob — it needs an electric one.

Azerbaijan does **not** carry the Moscow-style blanket prohibition; it mandates
the mitigation instead (amended cl. 8.40: every apartment in a gasified building
must carry a 10 %-LEL gas detector wired to a solenoid cut-off at the apartment's
gas entry). And MİDA hands over its apartments with a **gas hob** fitted
(`reported`). At 2,7 m clear height the 15 m³ volume rule is only 5,6 m² of floor,
so it never binds a real kitchen-diner — **the binding constraint is the room's
category, not its size.**

⚠️ This bears on `living_dining_kitchen`, whose `az_area` currently points at
`living_room_2plus` (16,0). The profile already calls that mapping
under-targeted. This note adds that in AZ the type may not be buildable with the
cooking appliance MİDA actually fits.

### 6.6 Where MİDA is not the Baku market

**MİDA is the state housing fund.** It is precisely the segment AzDTN 2.7-2
cl. 5.1 addresses, and its plans are *subsidised güzəştli mənzil* housing sold at
administered prices. It is therefore the **regulated, affordable** end of Baku
construction, not the private market — and §7.1's carve-out says the private fund
answers to the client alone.

So the correct statement of what §6 establishes is: **this is what Azerbaijan
actually builds when a state agency builds it to its own regulator.** It is a real
Azerbaijani room population with n in the hundreds and a confirmed measurement
plane, and it is the first such population this repo has. It is *not* evidence
about Port Baku, Sea Breeze or Crescent, and where the private premium market
differs it will differ upward.

Two facts bound how well even MİDA follows the norm, and they are worth carrying
because they show a published schedule is design intent and not compliance:

| AzDTN 2.7-2 cl. 5.7, mandatory | MİDA plans meeting it |
|---|---|
| kitchen ≥ 8,0 m² | **84,0 %** (262/312) — smallest kitchen 6,87 m² |
| living ≥ 16,0 m² in 2+ otaq | **87,1 %** (244/280) |
| bedroom ≥ 8,0 m² | 98,6 % (283/287) |

**One in six MİDA kitchens is below the statutory minimum its own regulator
publishes.** That is `derived` — each verified room area tested against the
verified clause — and it is the single strongest caution in this note against
reading any published schedule as ground truth.

---

## 7. Apartment totals by otaq count

### 7.1 What Azerbaijan publishes, and who it is for

AzDTN 2.7-2 cl. 5.1, verbatim lead-in:

> Dövlət və bələdiyyə mənzil fondunun yaşayış binalarında mənzillərin, otaqların
> sayına və sahəsinə görə minimal ölçülərinin cədvəl 1 əsasında (balkonların,
> terrasların, eyvanların, lociyaların, şüşəbəndlərin, isidilməyən köməkçi
> otaqların və mənzilin tamburunun sahələri nəzərə alınmamaq şərtilə) qəbul
> edilməsi **tövsiyə olunur**.
>
> Özəl mənzil fonduna aid yaşayış binalarındakı mənzillərin sahəsi, otaqların sayı
> və tərkibi **sifarişçi tərəfindən müəyyən edilir**.

Two things decide how far this can be pushed.

**It is scoped to the state and municipal housing fund.** The second paragraph
says that for the **private** housing fund, apartment area, room count and
composition are determined **by the client**. Baku new-build is overwhelmingly
private. **So AzDTN, by its own terms, publishes no area guidance for the housing
this engine's Homeowner would actually buy.** That is not a gap in our reading; it
is the norm declining to speak.

**It excludes balconies, terraces, verandas, loggias, glazed enclosures, unheated
ancillary rooms and the apartment tambour** — a binary count of enclosed heated
space, which `minima.md` §7.1 already identified as closer to GIA than to a
weighted Wohnfläche.

**Cells cited individually, per the copyright posture.** For *şəhər, qəsəbə*
(town/settlement), recommended total area (`ümumi sahə`), by number of habitable
rooms — the four the 1–4 otaq promise needs:

| otaq | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| recommended total, m² | **28–38** | **44–53** | **56–65** | **70–77** |

`src: az_azdtn_2_7_2`, `ref: cl. 5.1 Table 1`, `conf: verified`, `force:
recommended`, scope: state and municipal fund only. Three of these four already
appear in `minima.md` §7.1 and §7.3; the 4-otaq cell is new here and completes the
promised band. The village row and the 5- and 6-room columns are **not
reproduced**.

⚠️ **How the row was identified, because the extraction does not label it
cleanly.** `pypdf` emits Table 1's row labels *after* their value rows, so
*şəhər, qəsəbə* (town/settlement) and *kənd* (village) each sit on the line below
the numbers they head. The town assignment is taken on two independent grounds:
`minima.md` §7.1 and §7.3 read the same document earlier and assigned **three** of
these four cells to the town row, and the other row is larger at every column
(38–44 against 28–38 at one room), which is the direction a Soviet-descended
town/village split runs. If a future reader has the typeset table, this is the one
thing in §7.1 worth re-checking against it.

### 7.2 The engine's own per-otaq series, against them

`brief.md` §9.4 publishes the Σ hard-minima series **26,5 / 37,5 / 47,5 /
57,5 m²** for 1/2/3/4 otaq, before the partition footprint.

| otaq | engine Σ hard floor | AzDTN recommended band (town) | engine floor vs band |
|---|---|---|---|
| 1 | 26,5 | 28–38 | **below the band** |
| 2 | 37,5 | 44–53 | below the band |
| 3 | 47,5 | 56–65 | below the band |
| 4 | 57,5 | 70–77 | below the band |

The engine's hard floor sits **under** the regulator's recommended band at every
otaq count, by 1,5 m² at 1 otaq widening to 12,5 m² at 4. That is the correct
direction — a hard floor must sit below a recommendation — and the widening gap is
the same effect §5 measures per room: a per-room minimum summed is a dwelling
minimum, and neither is a dwelling anyone builds.

### 7.3 What MİDA actually builds, against them

Same 318 distinct plan geometries, same harness. Three quantities, because they
are **not interchangeable and the difference is about a fifth**:

| otaq | plans | net internal p25 / **p50** / p75 | **p50 excl. balcony** | p50 external | ext ÷ int |
|---|---|---|---|---|---|
| studio | 5 | 34,97 / **35,57** / 40,10 | 34,97 | 43,10 | 1,21 |
| 1 | 32 | 33,08 / **36,44** / 38,50 | **32,55** | 45,36 | 1,24 |
| 2 | 122 | 53,09 / **56,74** / 57,70 | **52,40** | 68,56 | 1,22 |
| 3 | 125 | 69,40 / **72,23** / 74,57 | **67,19** | 86,68 | 1,21 |
| 4 | 33 | 84,70 / **96,53** / 98,99 | **85,60** | 110,87 | 1,21 |

Balconies excluded, which is the basis AzDTN's own table is stated on:

| otaq | MİDA p50 excl. balcony | AzDTN recommended band (town) | verdict |
|---|---|---|---|
| 1 | 32,55 | 28–38 | inside |
| 2 | 52,40 | 44–53 | inside, near the top |
| 3 | 67,19 | 56–65 | **above the band** |
| 4 | 85,60 | 70–77 | **above the band, by 8,6 m²** |

**The state agency builds above the regulator's recommendation at 3 and 4 otaq**,
and the gap widens with room count — the same shape §7.2 finds between the
engine's floor and the band, one tier up. A recommendation written for the state
fund is not what the state fund builds.

⚠️ **The number a Baku Homeowner will quote is the external one.** MİDA's own
price list sells on *Xarici perimetr üzrə sahə*, and the median ratio is **1,21**.
A Brief that takes an advertised Azerbaijani apartment area at face value and
allocates rooms inside it over-allocates by roughly a fifth — the layoutable net
internal is about **82 %** of the advertised figure. That is a Brief-parsing fact,
not a profile value, and it is handed to `brief.md`.

### 7.4 The Swiss pool, for comparison only

Median indoor area by count of otaq-like rooms (`ROOM`, `BEDROOM`, `LIVING_ROOM`,
`LIVING_DINING`, `DINING`, `STUDIO`), 44,894 residential dwellings:

| otaq-like | n dwellings | p25 | **p50** | p75 |
|---|---|---|---|---|
| 1 | 3,686 | 18,9 | **30,1** | 37,0 |
| 2 | 8,225 | 50,4 | **56,4** | 63,7 |
| 3 | 16,976 | 68,4 | **76,9** | 85,5 |
| 4 | 12,587 | 87,0 | **96,6** | 106,5 |

`fitted`, Swiss, n stated. The Swiss 3-otaq median (76,9) sits **above** the whole
Azerbaijani recommended 3-room band (56–65), and the divergence grows with room
count — which is what the disclosed `CorpusProvenance` ≠ `RegionProfile` mismatch
looks like when it is measured in square metres rather than described.

⚠️ **Not a like-for-like count.** "otaq-like" here counts the Swiss labels that
`counts_as_otaq` would mark true. It is a reconstruction, not the corpus's own
room count, and the indoor-area sum excludes balconies and loggias to match
AzDTN's exclusion list.

---

## 8. What could NOT be obtained

Stated plainly, and the first two are the ones that bound how far §6 may be
pushed.

1. **The Baku PRIVATE market.** §6 is the **state** housing fund. MİDA is exactly
   the segment AzDTN cl. 5.1 addresses, sold at administered prices, and cl. 5.1
   hands the private fund to the client. Sea Breeze (HTTP 403), Baku White City
   (buildings listed, no plans, no per-room areas) and PASHA / Crescent
   Residences (HTTP 403) were all attempted and none yielded a per-room schedule.
   **Where the premium private market differs from MİDA it will differ upward**,
   so §6's figures should be read as a floor on the market, not its centre.
2. **A per-room figure for a room actually called `mətbəx-yemək otağı`, anywhere
   in Azerbaijan.** MİDA has none — the term is absent from its eight-name
   vocabulary. No developer plan set and no portal listing using the label was
   found. The ≈18 m² in finding 5 is **two proxies agreeing**, not a measurement
   of the named room: MİDA's `Mətbəx-studio` is kitchen + living + dining (n = 5
   plans), and the Swiss figure is kitchen + dining summed across two rooms
   (n = 1,308). **Neither is a `mətbəx-yemək otağı`, and the agreement between
   them is the argument, not either one alone.**
3. **Any Azerbaijani space STANDARD in the design sense.** There is none. AzDTN
   publishes minima and one recommended totals table; MİDA publishes plans but no
   norm. The Housing Code (`Mənzil Məcəlləsi` art. 49) frames an allocation norm
   and an accounting norm, and the figure — **16 m² per family member**, Cabinet
   of Ministers decision no. 459 of 2019 — is `reported`, not `verified`: the
   decision text could not be opened, the adoption date is given variously as
   27 November and 5 December 2019, and **whether the 16 m² is `ümumi sahə` or
   `yaşayış sahəsi` is unresolved**. It is a welfare-entitlement norm in any
   case, not an architectural standard, and it constrains no geometry.
4. **Portal per-room data.** Azerbaijani property portals expose otaq count and a
   single total area. No per-room breakdown field was found on any of them.
5. **Whether MİDA's `internal_size` convention matches ADR 0010's finished-face
   plane exactly.** The rooms sum to `internal_size` to the cent, which proves the
   schedule is *internally consistent and net*, and MİDA's own price list names
   the column *Daxili perimetr üzrə sahə*. Whether that perimeter is the finished
   face or the bare structural face is **not stated by MİDA**, and the difference
   is a plaster thickness per room. Small, systematic, and unquantified.
6. **The `eni` / `işıqda` question on the two widths.** AzDTN 2.7-3 cl. 5.1 says
   only *eni* — width. It does **not** say *işıqda* (in the clear). Reading 3000
   and 2600 mm as **clear** widths, which is what the profile does, is an engine
   interpretation the norm does not license, and it is the second referent problem
   in the same clause after §2.2's.
7. **MİDA's gas-hob fitout, first-hand.** That MİDA hands over apartments with a
   gas hob is consistent across three Azerbaijani outlets but the `mida.gov.az`
   page is JS-rendered and could not be read. `reported`. It matters only to how
   often §6.5's asymmetry bites, not to whether the rule exists.
8. **Anything about how MİDA's plans were produced.** A published schedule is
   **design intent**, not an as-built survey. §6.6 measures how far that goes:
   16,0 % of MİDA kitchens are below the mandatory minimum MİDA's own regulator
   publishes. No as-built measurement of any Azerbaijani dwelling was obtained,
   and none is known to be public.

---

## 9. Harness

`experiments/baku-market-areas/`. Outputs are written next to the scripts and are
regenerable; nothing is committed.

| script | what it does | runtime |
|---|---|---|
| `azdtn_clauses.py` | re-prints AzDTN 2.7-2 cl. 5.1/5.7 and 2.7-3 cl. 5.1 verbatim from the cached PDFs' extracted text, with md5s | seconds |
| `swiss_room_areas.py` | per-`entity_subtype` area distributions with site and apartment counts and top-site concentration | ~3 min |
| `swiss_kd_context.py` | the dwellings the 41 `KITCHEN_DINING` rooms sit in; plan-level deduplication; indoor area by otaq-like count | ~3 min |
| `swiss_vs_az.py` | each `market_default` target's percentile inside the Swiss class it would be applied to | ~2 min |
| `swiss_kitchen_plus_dining.py` | `KITCHEN` + `DINING` summed in dwellings holding both — the comparator that matches the object §4.1 shows the label does not | ~2 min |
| `mida_room_schedules.py` | the whole of §6 and §7.3 from MİDA's published schedules: per-room distributions over distinct plan geometries, rank-matched comparisons against `market_default`, totals by otaq, MİDA's own compliance | seconds |

All three Swiss scripts stream `geometries.csv` (1,09 GB) once and hold only areas
in memory. `swiss_room_areas.py`'s class counts are the check that the harness
agrees with `dataset-inventory.md` §1.4; if they drift, the corpus on disk is not
the one the map was built on.

`mida_room_schedules.py` reads `out/mida_types.json`, the harvest of MİDA's API.
**`out/` is gitignored, so the harvest is on this branch's working tree and not in
the repo** — it is third-party data and the project does not redistribute
third-party material. The script's docstring carries the endpoint chain to
re-crawl it. Whoever picks this up should decide deliberately whether to commit
it: the API is undocumented and could disappear, and the analysis is not
reproducible without it.

---

## 10. Handoffs

Nothing here is fixed. Each item names its owner.

| what | where it lives | who owns it |
|---|---|---|
| `what_could_not_be_obtained.market_practice` is **out of date** and is a published field | `room-constraints.json` `profiles.AZ` | the profile's holder |
| `bathroom_combined` 3,8 sits **above** Baku practice (63,5 % of MİDA main bathrooms are smaller) — the first `market_default` cell with an Azerbaijani reason to move | `room-constraints.json` `areas_m2` | the profile's holder, under C14's monotone-raise rule |
| six `clear_widths_mm` cells cite **cl. 5.4**; the text is **cl. 5.1** | `room-constraints.json` | the profile's holder |
| the two widths are read as **clear** and the norm says only `eni` | `room-constraints.json` | the profile's holder |
| *"No surveyed source states an aspect rule"* is false — AzDTN 2.7-3 cl. 5.1 recommends length ≤ 2× width | `rules.json` `dim.aspect_ratio_hard` | `rules.json`'s holder |
| `kitchen_dining`'s 6,0 target against ≈18 m² of measured practice | ticket 70 | ticket 70 |
| `living_dining_kitchen` may be **non-compliant with a gas hob** in AZ (§6.5) | ticket 70 / the profile | not currently owned by anything on the map |
| an advertised Azerbaijani apartment area is the **external** figure; net internal is ≈82 % of it | `brief.md` parsing | `brief.md`'s holder |
| `counts_as_otaq: false` for `kitchen_dining` is now **corroborated by AzDTN 2.7-3 cl. 4.7**, which files the type inside `mətbəx` — the flag can move from `derived` toward `verified` | `room-constraints.json` | the profile's holder |
