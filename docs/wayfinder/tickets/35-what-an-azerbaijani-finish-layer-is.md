---
id: 35
title: What an Azerbaijani finish layer actually is
parent: map
labels: [wayfinder:research]
status: closed
assignee: tng
blocked_by: []
writes:
  - docs/research/ (new findings doc) — read-only on the profile
---

# What an Azerbaijani finish layer actually is

## Question

**ADR 0010 made the finish layer load-bearing and shipped its thickness as
`engine_choice`.** `profiles.AZ.construction.catalogue.brick.t_finish` is
**15 mm**, and no Azerbaijani document read on this map states a plaster
thickness. Every published dimension and every area in v1 now measures to that
plane, so this is the single weakest number under the largest number of
consumers.

The value is not a guess in the ordinary sense — it is corroborated **from
inside**: `t_party`'s shipped 250 mm leaf was derived from an acoustic table
whose rows read *"brick + 15 plaster both sides"* (250 → 52 dB, passes AzDTN
2.7-2's 50 dB; 120 → 49 dB, fails). So 15 is already load-bearing in a
`verified`-sourced derivation, and changing it re-opens `t_party`. That is
self-consistency, not a source, and *The Azerbaijani region profile* established
exactly why that gap matters: a `REPORTED` number off a repealed ancestor is not
a safe degradation of `VERIFIED`, and publishing folklore is the C8 breach this
map keeps nearly committing.

**Find:**

1. **The normative plaster/render thickness for internal brick masonry in
   Azerbaijan**, read first-hand. `arxkom.gov.az` served the AzDTN corpus on an
   unauthenticated GET for *The Azerbaijani region profile*; start there. The
   likely instruments are the finishing-works norm and the masonry norm
   (`az_azdtn_2_17_1` is already in `sources`). Russian ancestors —
   СП 71.13330, ГОСТ 31377 — may be read for **shape** (that plaster is
   specified by quality class, and how many classes there are) but their
   **numbers must not be transferred**: AzDTN 2.7-2 terminated SNiP's force in
   Azerbaijan in 2021 and the same trap caught this map once already.
2. **Whether it is one number or a class ladder.** If the norm grades plaster by
   quality class — simple / improved / high-quality — then `t_finish` is a
   *choice among published values*, not an invention, and the profile should say
   which class it ships and why. That is a materially better answer than a single
   `engine_choice` even if the shipped millimetres do not move.
3. **Whether the number is a thickness or a tolerance.** Finishing norms often
   publish a *maximum deviation from plane* rather than a build-up depth. Those
   are not the same quantity, and reading one as the other is the failure mode
   this ticket exists to avoid.
4. **What the corpus says, if anything.** Swiss Dwellings and ResPlan record wall
   thicknesses; whether either records a finish layer separately is unknown and
   is a cheap check. A negative result is a finding — *Which region profiles
   ship in v1* got its most useful answer that way.

**Consequences of a different number, so the cost of getting it wrong is
visible.** `t_int = t_int_structural + 2 · t_finish`. At 15 that is 150. At 10 it
is 140, at 20 it is 160. Each of those:

- moves the ADR 0007 residue class (`min + t_int ≡ 0 mod 250`) — 100, 110 or 90;
- shifts every Space area by roughly 1% of the dwelling;
- leaves ADR 0004's even-thickness gate **unbound** — already settled by ADR 0010
  consequence 2, which binds evenness on the numbers that get *halved* and exempts
  a layer component that only ever enters a total *doubled*. `120 + 2 · t_finish`
  is even for every integer `t_finish`. **Do not rule out an odd answer**; the
  gate asserts the exemption explicitly and passes at 15;
- re-opens `t_party` if it contradicts the acoustic table's assumption.

**Deliverable:** the value with `conf: verified` if a document supports it, or an
explicit statement that no Azerbaijani instrument publishes one — in which case
`engine_choice` stands and the note must say that the search was made rather than
skipped. Either outcome closes this ticket; only silence does not.

## Findings pointer

Research complete. Findings: **[`docs/research/az-finish-layer.md`](../../research/az-finish-layer.md)**.
Evidence and scripts: `experiments/finish-layer/`.

**Headline:** `t_finish` stays **15 mm**; its provenance moves from
`engine_choice` to **`verified`** — **AzDTN 2.12-4\* Əlavə 8\*, Cədvəl 1, row 27**
(cement-sand plaster over stone or brick masonry, column *Layın qalınlığı, mm*),
read first-hand and confirmed by glyph coordinates. Nothing downstream re-opens:
`t_int` 150, ADR 0007 residue 100 mod 250, `t_party` 280 and its 52 dB derivation
all stand.

Item 2's hypothesis is **refuted** — the finishing-works norm's three quality
classes are **flatness tolerances (1–3 mm/m), not thicknesses**, which is item 3's
trap live in the real document. Item 4 is **negative in both corpora**. Azerbaijan
has issued **no AzDTN for finishing works**; the retained СНиП 3.04.01-87 bounds
plaster thickness without specifying it.

The proposed `t_finish` cell is in §7 of the findings doc. **The profile was not
edited** — this ticket is read-only on it, per its own `writes:`.

## Resolution

**15 mm, and it is `verified`.** The shipped number does not move; its provenance
does, from `engine_choice` to read-first-hand. Nothing downstream re-opens.
Findings: `docs/research/az-finish-layer.md`. Scripts:
`experiments/finish-layer/`.

**Source:** **AzDTN 2.12-4\*** *Binaların istilik mühafizəsi* (in force
2022-06-10, State Register 15202206100224, new redaction Baku 2025), **Əlavə 8\*,
Cədvəl 1, rows 27–28** — *plastering with cement-sand mortar / with lime mortar
over stone or brick masonry* — column **`Layın qalınlığı, mm` = 15**. Served by
`arxkom.gov.az` on an unauthenticated GET, as ticket 25 found.

### The column assignment was not taken on trust

`pdftotext -layout` scrambles the top of that table, so the extracted text is not
evidence for which column a number sits in. It was verified from **glyph
coordinates** instead — `experiments/finish-layer/verify_appendix8_columns.py`,
re-run and reproduced during resolution:

```
27. Daş və ya kərpic hörgü üzrə sement-qum məhlulu ilə suvaqlanma   [15]@x=341  [373]@x=482
28. Daş və ya kərpic hörgü üzrə əhəng məhlulu ilə suvaqlanma        [15]@x=341  [142]@x=482
29. Taxta üzrə əhəng-gips məhlulu ilə suvaqlanma                    [20]@x=341   [17]@x=486
```

The x ≈ 325–349 column holds `1,5 / 1,5 / 3–4 / 100 / 15 / 15 / 20 / 250–400`.
Those are layer thicknesses and nothing else. The x ≈ 470–495 column holds
`490 / 2900 / 14 / 373 / 142 / 17` — air-permeation resistances, whose spread of
three orders of magnitude is itself the tell. **The 15 is in the thickness
column.**

### Why this is not the trap ticket 25 fell into and climbed out of

The distinction is legal, not rhetorical. There, СНиП 2.08.01-89\* had been
**terminated** in Azerbaijan by AzDTN 2.7-2, so its numbers were folklore *and*
repealed. Here, **AzDTN 2.12-4\* is the instrument that suspended СНиП II-3-79\***
and carries the row forward into its own text. The quote is from the live
Azerbaijani instrument.

The genealogy was checked and disclosed rather than hidden: СНиП II-3-79\* Прил.
9\* rows 30–32 carry the identical 15/15/20 and 373/142/17. The AZ redaction
re-edited other rows in the same table (19 620 → 20 000, 2940 → 2900), so it is
not a photocopy.

**Scope, stated in the shipped cell:** Əlavə 8\* is a *characteristics* table —
it states a resistance **at** a stated layer thickness. The norm **tabulates**
15 mm; it does not **require** it. C8 holds.

### The trap that was live, and would have shipped silently

Item 2 asked whether the answer is a class ladder. **It is not, and the hypothesis
is refuted rather than merely unconfirmed** — this is the most valuable finding
after the number itself.

Azerbaijan has issued **no finishing-works norm of its own**; the retained
instrument is СНиП 3.04.01-87. It *does* grade plaster simple / improved /
high-quality. But **Table 9's column heading is `Предельные отклонения` and every
row is a flatness tolerance** — 3 / 2 / 1 mm per metre, ≤15 / ≤10 / ≤5 mm over
room height. **No thickness anywhere in it.** Table 10 gives thickness *maxima*
(single-layer ≤20 non-gypsum, ≤15 gypsum; обрызг ≤5, грунт ≤5–7, накрывка ≤2) —
a ceiling, not a value, with cl. 3.16 handing the actual thickness to the project.

The magnitudes **overlap**: *"улучшенная — 2"* and *"накрывка — до 2"* are both
"2 mm in a table about plaster". Taking the ladder for thickness would have
shipped `t_finish` = 1 / 2 / 3, given `t_int` = 122 / 124 / 126, and been
internally consistent all the way down. **No arithmetic gate on this map would
have caught it** — the evenness rule is unbound on a layer component, and the
residue class would simply have been a different legal number.

### The competing Azerbaijani number, and why it loses on product

**AzDTN 2.17-1 cl. 8.24 note 1** implies **10 mm per face**: the panel series
8.5 / 14 / 27 cm "includes the outer and inner mortar layers", a three-point exact
fit (65→85, 120→140, 250→270). Current, statutory, Azerbaijani.

It loses on **product, not authority.** It is a factory mortar face cast against a
flat pallet, for **brick panels** — construction type `B1`, which
`thickness.md` §8 already recommends not shipping. The profile ships hand-laid
masonry, whose plaster must absorb bricklaying deviation, and thicker is the
physically expected direction. Recorded against `B1` if `B1` ever ships.

### Item 4 — negative twice, and permanently

Swiss Dwellings: 3,255,905 rows, 93 distinct `(entity_type, entity_subtype)`
pairs, and the whole `separator` taxonomy is `WALL / RAILING / COLUMN`. ResPlan:
one scalar `wall_depth` per plan (n = 17,000, median 4.14), no material, no
per-wall thickness. **Neither corpus can ever corroborate a finish thickness** —
this is not "we did not find it", it is a closed question against those sources.

### What was written

`data/standards/room-constraints.json` — `t_finish` promoted to `verified` with
its clause, its glyph-coordinate check and both the trap and the competing number
recorded in the cell · `sources.az_azdtn_2_12_4.force_note` corrected, which the
findings doc §7.1 flagged and correctly declined to make itself: it said the
instrument *"supplies no wall thickness"*, true of the thermal tables and
incomplete once Əlavə 8\* is read · ADR 0010 consequence 5 struck through and
discharged.

`experiments/region-profile/gate_check.py`: **33 gates, all pass**, unchanged —
which is the point. The value did not move, so nothing it asserts moved either.

### What this did not settle

- **`t_ext_total`'s 20 mm external finish is now unsupported on a second axis.**
  Əlavə 8\*'s only 20 mm row is lime-gypsum over **timber**; the document's
  external-render reference gives colours, not thicknesses. It stays
  `engine_choice`, still blocked on Baku's `Dd`, and the profile note now says so.
  Out of this ticket's four items and deliberately not closed here.
- **The 01.01.2026 normative `SİYAHI` was not read first-hand.** The register used
  is the same official list served via `sukanal.az`, undated internally, 2016
  upload path, corroborated against today's live `arxkom.gov.az` category
  listings. So *"Azerbaijan has issued no finishing-works norm"* is verified
  against that register and corroborated, but not certified against the 2026
  edition. **It does not touch the 15 mm**, whose instrument was downloaded
  first-hand and carries its own in-force date.
- **ГОСТ 28013-98** full text — 404 on the URL tried; governs mix properties, not
  layer geometry, so low expected value. **ГОСТ 31377** deliberately **not** read:
  it could only have supplied numbers this ticket forbids transferring.
- **No page image** — no `pdftoppm` on this machine. The glyph-coordinate check
  substitutes for it and is reproducible, which is why it is committed.
