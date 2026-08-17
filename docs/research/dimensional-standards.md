# Dimensional standards for residential layout — what we adopt, and why

Research note for **ticket 5, Dimensional standards corpus**. Consumed directly by
*Acceptance validator spec* (7) and *Brief schema and parsing contract* (10).

The instruction was: **adopt Neufert where it fits, survey the other reference
works, and think rather than copy blindly.** This note is therefore not a
transcription. Where the sources disagree, the disagreement is treated as the
finding, and the resolution is argued rather than averaged.

The deliverable table lives at **`data/standards/room-constraints.json`**. The
same table is reproduced in §8 below for reading. The JSON is canonical; if the
two ever disagree, the JSON wins.

**C8 applies to every number here: Neufert-grade dimensional standards, no legal
code-compliance claim, ever.** Several numbers below are *quoted from* building
regulations. That is a statement about where a number came from, not a claim that
a plan carrying it complies with anything.

---

## 1. TL;DR — the decisive findings

| # | Finding | Consequence |
|---|---|---|
| **1** | **A `region` parameter is required — but only on half the corpus.** Body-derived clearances are invariant; convention-derived numbers are not. | §3. Split the table into an ergonomic layer (shared) and regional profiles (~30 numbers each). |
| **2** | **`region` alone is not enough — you also need a tier.** England alone yields **five** different "minimum bedroom areas" (7.5, 8.5, 11.5, 12.5, 13.5 m²) depending on which instrument you invoke. The intra-national spread is as wide as the international one. | §4. Every cell carries `statutory_floor` / `market_default` / `accessible`. |
| **3** | **Minimum areas and minimum clearances are not the same kind of number and must not sit in one table without a marker.** Neufert issues *no* prescriptive minimum room areas at all, and neither does German building law. | §5.1. The engine's default areas are *our* choices, derived from clearances, not quoted minima. |
| **4** | **The window rule is a method conflict, not a number conflict.** England has no daylight requirement of any kind; Germany has a 1/8 area fraction; Japan has a site-geometry-dependent factor; the Metric Handbook uses a daylight-factor formula. These are not interconvertible. | §5.4. C6 item 4's "gets a window" must be defined by us, as topology, not borrowed as a ratio. |
| **5** | **Minimum areas are not comparable across regions even after unit conversion,** because the *measurement conventions* differ. German Wohnfläche counts 1.00–2.00 m headroom at 50% and balconies at 25–50%; UK GIA is binary. | §5.7. A minimum-area value must carry its measurement convention or it is meaningless. |
| **6** | **The kitchen "work triangle" is not in Neufert.** It is a Metric Handbook / US number. Do not attribute it to Neufert. | §5.3. Cite it correctly or drop it. |
| **7** | **Door widths propagate into masonry.** DIN 18040-2's baseline 800 mm clear forces an 860 mm leaf; the R level's 900 mm forces a 985 mm leaf, which changes the structural opening, which sits on the 125 mm octametric grid, which changes the wall layout. | §5.2. Doors are not a schedule; they are a layout constraint. |
| **8** | **Copyright: the numbers are safe, the tables and diagrams are not, and the "it's incorporated into law" safe harbour does not reach Neufert or the Metric Handbook.** | §7. Practical rule: prefer freely-published regulatory sources, re-derive rather than transcribe, never strip-mine one work. |
| **9** | **The verification-grade corpus is free.** UK Approved Documents and the NDSS are Open Government Licence v3.0 — reusable commercially and non-commercially, with attribution. Japanese law is on e-Gov. Bavarian and Saxon law are machine-readable. | §7.5. The test suite asserts against the UK profile because it is the only one checkable end-to-end. |

---

## 2. Method, and how to read the confidence labels

Every number carries one of:

- **VERIFIED** — read first-hand in the primary document named.
- **REPORTED** — a credible third party attributes it to the named source; not read first-hand.
- **DERIVED** — computed from a verified value by a stated rule.
- **ENGINE_CHOICE** — no source dictates it; we chose it, and the reason is given.

Read directly, first-hand, in this session:

| Document | How |
|---|---|
| Technical housing standards — nationally described space standard (2015) | gov.uk HTML |
| Approved Document M Vol 1 (2015 + 2016 am.) | gov.uk PDF, text-extracted |
| Approved Document K (2013) | gov.uk PDF, text-extracted |
| Approved Document F Vol 1 (2021) | gov.uk PDF, text-extracted |
| Approved Document B Vol 1 (2019 + am.) | gov.uk PDF, text-extracted |
| Building Regulations 2010, Schedule 1 | legislation.gov.uk |
| Building (Scotland) Regulations 2004, Schedule 5 | legislation.gov.uk |
| Copyright and Rights in Databases Regulations 1997, regs 13 & 16 | legislation.gov.uk |
| Open Government Licence v3.0 | nationalarchives.gov.uk |
| 建築基準法 (Building Standards Act) Art. 28 | e-Gov law API, official |
| 建築基準法施行令 (Enforcement Order) Arts. 20, 21, 23 | e-Gov law API, official |
| BayBO Arts. 32, 33, 34, 45, 46, 48 | gesetze-bayern.de, official |
| Feist v. Rural Telephone, 499 U.S. 340 (1991) | Cornell LII |
| ASTM v. UpCodes, No. 24-2965 (3d Cir. 7 Apr 2026) | ca3.uscourts.gov PDF |

Not read first-hand, and flagged accordingly throughout:

- **All DIN standards.** DIN is paywalled. Every DIN 18040 / 18065 / 18101 / 4172
  number here is REPORTED from nullbarriere.de, Baunetz Wissen, Baunormenlexikon
  or German Wikipedia citing the clause. **Two of these sources are known to be
  unreliable in specific ways** — nullbarriere mixes DIN 18040 Part 1 and Part 2
  values on some pages, and has at least one cm/mm unit typo; German Wikipedia
  gives *contradictory* MBO ceiling heights (2.40 m in one article, 2.50 m in
  another). Where the LBOs could be checked against primary law they say 2.40 m.
- **Neufert and the Metric Handbook.** Read as full OCR text of openly-hosted
  copies on the Internet Archive — **Neufert 4th English ed. (2012), not the
  current 6th (2023); Metric Handbook 6th ed. (2018), not the current 7th
  (2021)**. Those uploads are not publisher-authorised. Numbers marked VERIFIED
  below mean "read in the book's own text", not "lawfully licensed". OCR
  frequently destroyed dimension strings printed alongside line drawings, so
  several Neufert figure-carried values are recorded as **not found** rather than
  guessed. See §7 for why we do not ship or depend on those copies.
- **ISO 21542, EN 17210, CEN/TR 17621, RICS Code of Measuring Practice, IPMS,
  ANSI Z765** — all paywalled or unreachable. Genuine gaps.

**A constraint on the session:** the WebSearch budget was exhausted before this
work started. Everything was obtained by navigating directly to primary sources.
That is arguably better for provenance, but it means discovery was narrower than
it would otherwise have been — notably for non-Western standards (§6.4).

---

## 3. The region answer

**Yes, this system needs a `region` parameter on the standards — and it must be
the same enum as the training-data conditioning variable in ticket 6.**

But the interesting half of the answer is *what it applies to*. The corpus splits
cleanly into two layers, and only one of them varies:

### Layer A — ergonomic. Region-invariant.

Body-derived clearances. A person needs the same space to pass a doorway, reach
a worktop, or get past the foot of a bed in Munich as in Manchester. Across every
source surveyed these agree to within roughly ±10%, and where they diverge it is
because one source is quoting an *accessibility* tier rather than a body:

| Quantity | Neufert | Metric Handbook | DIN 18040-2 base | AD M Cat 2 | Spread |
|---|---|---|---|---|---|
| One person passing | — | 750 mm | — | 750 mm | none |
| Worktop depth | 600 mm | 600 mm | — | — | none |
| Worktop height | 850–950 mm | ~900 mm (830–1005) | — | — | overlap |
| Bed-side access | (figures) | 750 mm | 900–1200 mm | 750 mm | tier, not region |
| Turning circle | 1500 mm | 1500 mm | 1500 mm (R) | 1500 mm | none |
| Manoeuvring square | — | 1200×1200 | 1200×1200 | 1200×1200 | none |

This is the layer where **Neufert genuinely wins and C8's posture is right**.
Neufert is an ergonomics book. Its residential section is clearance tables and
worked layouts, not a schedule of minima. Adopt it here without a region.

### Layer B — conventional. Region-dependent, and the differences are not noise.

| Quantity | DE | UK (England) | JP | Spread |
|---|---|---|---|---|
| Habitable-room clear height | **2400 mm** (2500 Berlin; GK 1–2 exempt in Bayern) | **2300 mm** over 75% GIA — *and only as planning policy; no Building Regulations requirement since 1985* | **2100 mm**, averaged | **300 mm / 14%** |
| Window rule for habitable rooms | **≥1/8 of net floor area**, measured on the *structural opening* | **none** | **1/5–1/10 by room type, modified by a site-geometry correction factor** | rule *exists or does not* |
| Ventilation opening | (via DIN/MVV TB) | **1/20** of floor area | **1/20** of floor area | UK and JP agree exactly |
| Door leaf module | **125 mm** octametric grid (DIN 18101:2014); leaves 610/735/860/985/1110 | **imperial-dominant** — 1981 mm × 457…864; metric alternative 2040 × 526…926 | — | incompatible modules |
| External wall | **365 mm** monolithic masonry typical (300/425/490 variants) | ~300 mm cavity (102.5 brick + cavity + 100 block) + finishes | — | **~65 mm+**, and rising for US frame |
| Internal partition | **115 mm** masonry | ~100 mm stud | — | small |
| Stair: dwelling limits | 2s+a **590–650**; riser ≤190; going 260–320 | 2R+G **550–700**; rise 150–220; going 220–300; pitch ≤42° | riser **≤230**; tread **≥150**; width ≥750 | see below |
| Area measurement | Wohnfläche: **50%** at 1.00–2.00 m headroom, **25–50%** for balconies | GIA: binary, internal face of perimeter walls | — | not interconvertible |

The stair row is the sharpest illustration. A dwelling stair that is legal in
Japan — 230 mm riser, 150 mm tread — has a tread **47% below** the UK minimum
going of 220 mm and would be rejected outright. Meanwhile Neufert's stated
*optimum* of 170/290 at 30° is legal everywhere but is nowhere near any of the
legal limits. Averaging these produces a stair belonging to no building tradition
and comfortable for nobody.

### Why the parameter is not optional

Three arguments, in increasing order of force.

1. **The numbers differ by more than tolerance.** A 300 mm ceiling-height spread
   and a 65 mm external-wall spread are not rounding. On a 100 m² footprint, the
   DE-vs-UK external wall difference alone moves the internal area by roughly
   2 m² — larger than the tolerance any sane brief-agreement check would allow.

2. **C12 does not say otherwise.** C12 reads *"Not tied to any region. Combine
   corpora where it can be made to work."* That is a prohibition on hard-coding
   one region, plus a conditional. It is not an instruction to blend. Here it
   cannot be made to work for Layer B, and it can for Layer A. The parameter is
   how we honour C12 rather than violate it.

3. **C10 makes it mandatory, not merely advisable.** The model proposes and the
   solver projects onto the feasible set. If the model is conditioned on region
   (ticket 6's question) and the constraint set is not, the solver takes a
   proposal drawn from one convention and drags it onto another convention's
   constraints. That is strictly worse than either alone, and the sibling
   project's measurement is the warning: a model scoring 0.909 on RPLAN scores
   **0.592** on ResPlan. **The two enums must be the same enum.** If ticket 6
   concludes region should *not* condition the model, this ticket's answer does
   not change — but the pairing must then be re-argued, not silently dropped.

### What we actually ship in v1

- `region` values defined: **`DE`, `UK`, `US`**. Stubs declared, not populated:
  `IN`, `JP`, `AU`, `CN`.
- **Default: `DE`.** C8 names Neufert; the primary geometry corpus (Swiss
  Dwellings) is DE/CH; a European-convention proposal should meet
  European-convention constraints.
- **Verification profile: `UK`.** Every UK number here was read first-hand from a
  document published under the Open Government Licence v3.0 — free, complete,
  independently checkable, and lawfully redistributable. It is the only profile
  that can be regression-tested against its own sources without buying anything.
  That is a *testing* decision, not a claim that UK numbers are better.
- A profile is ~30 numbers. Adding a region is a data task, not a code task.

### The refinement: `region` is necessary but not sufficient

See §4. The parameter is really `(region, tier)`, and shipping only `region`
would leave the worst ambiguity unresolved.

---

## 4. The biggest conflict is *inside* a country, not between countries

This was the most surprising result, and it reframes everything above.

Ask "what is the minimum area of a bedroom in England?" and the honest answer is
five numbers, all currently in force, all from the same government:

| Value | Instrument | Force |
|---|---|---|
| **7.5 m²**, min width 2.15 m (single) | NDSS ¶10(c) | Planning policy, **optional** — applies only where a local authority adopted it in its Local Plan |
| **11.5 m²**, min width 2.75 m / 2.55 m (double) | NDSS ¶10(d)–(e) | as above |
| **8.5 m²**, min width 2.4 m (single) | AD M ¶3.35(i), M4(3) | Optional requirement — applies only if imposed as a planning condition |
| **12.5 m²**, min width 3.0 m (other double) | AD M ¶3.35(f), M4(3) | as above |
| **13.5 m²**, min width 3.0 m (principal double) | AD M ¶3.35(d), M4(3) | as above |
| *(nothing)* | Building Regulations 2010, Schedule 1 | **Mandatory — and it imposes no minimum room area at all** |

A 1.8× spread, within one jurisdiction, in one year. That is as wide as the
DE-vs-UK-vs-JP spread on most quantities.

The structural fact underneath it: **England prescribes minimum room areas only
inside the accessibility tier and inside optional planning policy, and nowhere in
mandatory building regulations.** Germany is more extreme — the MBO and the
Landesbauordnungen prescribe *no* numeric minimum floor area for any room, only
"eine für ihre Benutzung ausreichende Grundfläche" (a floor area sufficient for
its use). Neufert prescribes none either; its only residential *area table* is a
German subsidised-housing **maximum** (50/60/75/85 m² for 1/2/3/4 persons).

So: a `region` lookup returning a single "minimum bedroom area" would be
fabricating a consensus that does not exist. The cell needs a tier.

### The three tiers, and why the default is not the floor

| Tier | Meaning | Used as |
|---|---|---|
| `statutory_floor` | The hardest number any instrument in that region imposes. | **Hard constraint.** Reject below it. |
| `market_default` | What is actually built and what a Homeowner expects. | **Soft objective**, and the value that fills unstated brief fields. |
| `accessible` | The region's wheelchair-user tier. Not a v1 default. | Carried so adopting it later is a parameter change. |

**The default tier is `market_default`, not `statutory_floor`.** This matters
more than it looks. C2 says the Homeowner judges by "would I live here". A plan
built to the statutory floor is a plan of 7.5 m² bedrooms with 2.15 m widths and
2.3 m ceilings — legal, and reliably something nobody wants. Defaulting to the
floor would make the engine systematically produce plans that pass and fail.

This also answers ticket 7's "hard or soft?" question **per value rather than by
a separate flag**: a number is hard because it came from the `statutory_floor`
tier and soft because it came from `market_default`. The C10 split — hard rules
are constraints, plausibility is a soft objective — is expressed in the data
itself.

---

## 5. The numbers, by ticket item

### 5.1 Minimum room areas and clear dimensions

**The headline structural finding: three of the five surveyed works issue no
minimum room areas at all.**

| Work | Prescriptive minimum room areas? |
|---|---|
| **Neufert, *Architects' Data*** | **No.** Ergonomic clearances and worked example layouts. Areas appear as *descriptions of what a drawing achieves* — "bedrooms with minimal space of approx. 13 m² … and approx. 8 m²", kitchens "from approx. 10 m²", workroom kitchens 5.5–9.5 m². Where a hard number appears it is quoted *from German regulation* (2.40 m height, 1/8 window, DIN 1053 wall thicknesses), not authored by Neufert. |
| **Metric Handbook** | **Yes, and scrupulous about provenance.** Ch. 21 is organised as statutory → non-statutory → design data. It relays the NDSS, GLC and London Housing Design Guide tables and states outright that since 2015 *"there are no mandatory minimum areas for these types of housing in England"*. |
| **Ramsey/Sleeper, *Architectural Graphic Standards*** | See §5.8 — detail-and-assembly oriented, not space-programme oriented. |
| **Time-Saver Standards** | See §5.8. |
| **DIN 18040 / MBO / LBO** | **No.** Accessibility clearances only; the LBOs give no numeric minimum area. |

Because of this, **the engine's default room areas are our own choices**, derived
from clearances plus furniture footprints, corroborated against whatever
regulatory and reference values exist. That is deliberate — see §7.6, where it is
also the strongest copyright hygiene move available.

The area values that *do* exist, for corroboration:

| Room | NDSS (UK, planning policy) | AD M M4(3) (UK, accessible) | London Housing Design Guide | GLC (widely adopted) | Neufert (illustrative) |
|---|---|---|---|---|---|
| Single bedroom | 7.5 m² / 2.15 m | 8.5 m² / 2.4 m | — | — | ≈8 m² |
| Double bedroom | 11.5 m² / 2.75 m, others 2.55 m | 12.5 m² / 3.0 m | — | — | ≈13 m² |
| Principal double | (as double) | 13.5 m² / 3.0 m | — | — | ≈13 m² |
| Living room | — | — | — | 11–17 m² by occupancy and kitchen type | 5.0 × 6.0 m drawn |
| Combined LKD | — | **25 / 27 / 29 / 31 / 33 / 35 / 37 m²** for 2–8 bedspaces | 23/25/27/29/31 m² for 3–7p, min width 2.8 m (3–4p) / 3.2 m (5p+) | — | — |
| Dining kitchen | — | — | — | 8–14 m² by occupancy | "from approx. 10 m²"; good L-shape ≈14 m² |
| Galley kitchen | — | — | — | 5.5–9 m² by occupancy | 5.5–9.5 m² |
| Bathroom | — | — | **4.4 m²** | — | overall room dims ≥2.15/2.35/2.70 m |
| Shower room | — | — | **3.6 m²** | — | ≥1.90/2.00 m |
| Built-in storage | 1.0–4.0 m² by bedroom count | 1.5–4.0 m² by bedroom count | — | — | — |
| Whole dwelling | Table 1, 39–138 m² by bedrooms/bedspaces/storeys | — | — | — | German subsidy **maximum** 50/60/75/85 m² |

The AD M Table 3.2 LKD row is worth noting because it is a **formula in
disguise**: 25 m² at 2 bedspaces, +2 m² per additional bedspace to 37 m² at 8.
That is directly encodable and scales with occupancy, which is exactly what the
Brief supplies (ticket 10 field: "a family of four").

**A modelling caveat the ticket's schema forces us to confront.** The ticket asks
for `min width` **and** `min depth`. Almost no source distinguishes them: rooms
have no canonical orientation, so standards give a single *minimum clear
dimension*. We therefore set `min_width = min_depth = min_clear_dimension` and
mark the room `orientation_free: true`. Two room types are genuine exceptions —
kitchens (the aisle between opposing runs is directional) and corridors — and
those carry a real directional minimum. Pretending the others have a distinct
width and depth would be inventing data.

### 5.2 Door leaf widths, swing clearances, corridors

**Leaf sizes are the clearest example of module incompatibility.**

| | Germany (DIN 18101) | UK |
|---|---|---|
| Leaf widths | 1985 ed.: **610 / 735 / 860 / 985 / 1110 mm** at 1985 mm height. 2014 ed.: a **125 mm grid**, widths 485–1360, heights 1610–2735, independent. | Imperial-dominant: **1981 mm × 457 / 533 / 610 / 686 / 762 / 838 / 864 mm**. Metric alternative **2040 mm × 526 / 626 / 726 / 826 / 926 mm**. |
| Grid | **125 mm** — the DIN 4172 octametric module, shared with masonry | **100 mm** (BS) or none (imperial) |
| Commonest internal door | **860 × 1985** | **762 or 838 × 1981** |
| Clear height achieved | ≥2050 mm required by DIN 18040-2; Neufert wants ≥2100, "better 2100–2250" | 1981 mm leaf → clear height **below 2100 mm** |

DIN 18101:2014 and DIN 4172 share the 125 mm step. That is a load-bearing
coupling: **doors, wall openings and masonry all sit on one grid in Germany, and
they do not in the UK.** A layout engine that snaps to 100 mm will produce German
walls that do not course.

**Clear opening widths and the corridor pairing.** AD M Volume 1 gives a table
(Table 1.1 for M4(1), identical Table 2.1 for M4(2)) that is one of the most
directly encodable things in the whole corpus, because it makes corridor width a
*function of* door width and approach direction:

| Doorway clear opening width | Corridor clear passageway width |
|---|---|
| 750 mm or wider | **900 mm** when approached head-on |
| 750 mm | **1200 mm** when approach is not head-on |
| 775 mm | **1050 mm** when approach is not head-on |
| 800 mm | **900 mm** when approach is not head-on |

VERIFIED, AD M Vol 1 Table 1.1. With the note that *"a standard 826 mm door leaf
up to 44 mm thick will be deemed to satisfy a requirement for a clear opening
width of 775 mm"* — i.e. the leaf-to-clear-width conversion is about **51 mm** in
UK practice.

A localised obstruction may reduce the corridor to **750 mm** for no more than
**2 m** (AD M ¶2.22b). Minimum clear width of every hall or landing under M4(2):
**900 mm** (¶2.22a). This **resolves C6 item 2's "no sub-1m corridors"
placeholder**: the number is 900 mm, conditional on the door pairing above, with
a 750 mm pinch allowance.

German equivalents, all REPORTED (DIN 18040-2 not read first-hand):

| | Baseline "barrierefrei" | R "uneingeschränkt mit dem Rollstuhl nutzbar" |
|---|---|---|
| Clear width, internal doors | **800 mm** | **900 mm** |
| Clear height | 2050 mm | 2050 mm |
| Threshold | ≤20 mm, preferably ≤10 mm | same |
| Corridor width | **not isolable** — the figures found are probably Part 1 values contaminating the Part 2 page. Recorded as a gap. | — |

Neufert's own rule-of-thumb clear widths: room doors ≈800 mm; **bath/WC ≈700 mm**;
flat entrance ≥900 mm. Note the 700 mm — see conflict C4 in §6.

**Neufert's corridor table** (minimum widths by door arrangement, light / heavy
traffic) is the only source surveyed that makes corridor width a function of
*door swing direction*, which is a better model than a flat number:

| Arrangement | Little traffic | Heavy traffic |
|---|---|---|
| Doors one side, opening into rooms | 900 mm | 1300 mm |
| Doors both sides, opening into rooms | — | 1600 mm |
| Doors one side, opening into corridor | 1400 mm | 1800 mm |
| Doors both sides, opening into corridor | — | 2200 mm |
| Doors both sides, opposite, opening into corridor | 2400 mm | 2600 mm |

**Swing clearance.** No source gives a general "door swing hits nothing"
predicate; they give components of one. The encodable pieces: a **300 mm nib** to
the leading edge of the door, maintained back 1200 mm (AD M M4(2) ¶2.22, and BS
9266 for all rooms); doors in lobbies **1500 mm apart with 1500 mm between
swings** (AD M ¶2.22i); the entrance-level WC door must **open outwards** with the
opening overlapping the pan by **250 mm** (AD M ¶1.17d and Diagram 1.3). C6 item 3
will have to compose these; the corpus does not hand over a finished predicate.

### 5.3 Furniture and circulation clearances

**Furniture footprints.** AD M Volume 1 **Appendix D** is a furniture schedule
published under the Open Government Licence — free to encode and redistribute
with attribution. This is the single most useful artefact found, because a solver
needs footprints, not just clearances. VERIFIED, though the PDF's table columns
were mangled by extraction and reconstructed by item ordering:

| Item | Size (mm) |
|---|---|
| Double bed, principal bedroom | **2000 × 1500** |
| Double bed, other | **1900 × 1350** |
| Single bed | **1900 × 900** |
| Bedside table | 400 × 400 |
| Chest of drawers | 450 × 750 (alt. 500 × 1050) |
| Double wardrobe | **600 × 1200** |
| Table and chair | 500 × 1050 |
| Dining table | **800 × (800 / 1000 / 1200 / 1350 / 1500 / 1650)** for 2–7 persons |
| Armchair | 850 × 850 |
| 2-seat settee | 850 × 1300 |
| 3-seat settee | 850 × 1850 |
| WC + cistern | **500 × 700** |
| Bath | **700 × 1700** |
| Wash hand basin | 600 × 450 |
| Hand rinse basin | 350 × 200 |
| Manoeuvring square | 1200 × 1200 |
| Turning circle | 1500 diameter |
| Turning ellipse | 1400 × 1700 |

**Bed surrounds.** Tiered, and the tiers disagree with the regional stereotype:

| Source | Clearance |
|---|---|
| AD M M4(2) ¶2.25 | **750 mm** clear route doorway→window; 750 mm to **both** sides and foot of the principal double; 750 mm to one side + foot of other doubles; 750 mm to one side of singles/twins |
| AD M M4(3) ¶3.35 | **1000 mm** equivalents, **plus 1200 × 1200 mm** manoeuvring inside every bedroom door and on **both** sides of the principal bed |
| DIN 18040-2 baseline | 1200 mm one long side, **900 mm** the other |
| DIN 18040-2 R | 1500 mm one long side, 1200 mm the other |
| Neufert (DIN 18025) | **1200 mm** along the access side for a *non*-wheelchair user; 1500 mm in front of the long side for a wheelchair user |
| Neufert, general (non-accessible) | **Not found in text.** Carried in the figures; OCR did not preserve it. |

Note the inversion: **Neufert's accessible-housing figure for an ambulant user
(1200 mm) exceeds the UK's wheelchair-dwelling figure (1000 mm).** The German
baseline is more generous than the British accessible tier.

**Kitchen.** The single most consequential residential clearance, and the one
where the sources disagree most usefully:

| Source | Clearance in front of / between units |
|---|---|
| Metric Handbook (own design advice) | **1000 mm** recommended minimum |
| AD M M4(2) ¶2.24b | **1200 mm** |
| DIN 18040-2 baseline | **1200 mm** |
| **Neufert** | **1500 mm required, 1200 mm absolute minimum** |
| AD M M4(3) ¶3.32b | **1500 mm** |
| DIN 18040-2 R | **1500 mm** |

**Neufert's stated minimum equals the UK's Category 2 accessibility upgrade, and
Neufert's recommendation equals both the UK Category 3 wheelchair figure and the
German R level.** A German-normal galley kitchen is 500 mm wider than a
UK-normal one: Neufert derives a minimum kitchen width of **2700 mm** (600 mm
units each side + 1500 mm gangway), absolute minimum 2400 mm, where the Metric
Handbook's 1000 mm implies 2200 mm.

Other kitchen values: worktop depth **600 mm** (Neufert and MH agree); worktop
height **850–950 mm** (Neufert) / normally **900 mm**, ergonomic range 830–1005 mm
(MH). Appliance modules on a **600 mm** grid (Neufert lists base cupboards
300–1500 × 600, fridge/freezer/oven/dishwasher/hob all 600 × 600, single-basin
sink+drainer ≥900 × 600).

**The work triangle is not Neufert's.** A full-text search of the 4th English
edition found no occurrence. Neufert gives a work *sequence* instead —
store → wash → prepare → cook → serve. The triangle rule (sink + cooker + fridge,
total leg length **5–7 m**) is the Metric Handbook's, and in US practice the
NKBA's. **Attribute it correctly or drop it.** This is the clearest instance of
why "adopt Neufert" cannot mean "assume Neufert contains the rules everyone
attributes to it".

**Dining.** Neufert is the only source that gives a per-person module *and* a
pull-out clearance:

- Table area per person **600 × 400 mm**, plus a **200 mm** central strip for
  serving.
- **800 mm movement area** to left and right of the table — this is the chair
  pull-out plus circulation figure. With a corner bench, +800 mm per seat above
  three people.
- Round table ≥900 mm diameter, 1100–1250 mm preferable.
- Worked: 6 people → 1950 mm table width, 1800/2000 mm depth = 3.51 m² without /
  3.9 m² with chair pull-out.

The Metric Handbook gives table sizes (800 mm deep × 800–1650 mm long for 2–7
people) but **no explicit pull-out clearance**. So the dining rule is a place
where Neufert is adopted essentially unmodified, because it is the only source
that answers the question.

**Bathroom fixture clearances.**

| | AD M M4(1) (UK, mandatory) | DIN 18040-2 baseline | DIN 18040-2 R | Neufert (DIN 18025) |
|---|---|---|---|---|
| In front of WC | **750 mm** transfer space | 1200 × 1200 mm | 1500 × 1500 mm | — |
| Beside WC | 450 mm* each side (500 preferred), or 400/450 oblique | 900 mm preferred one side, 200 mm other | **900 mm** one side, 300 mm other | **950 mm wide × 700 mm deep** to one side; ≥300 mm from the other side to wall |
| WC compartment width | **1000 mm** front-access (min 900); 900 mm oblique (min 850) | — | — | — |
| Washbasin | positioned not to impede access | top 800–900 mm | top ≤800 mm, knee space ≥550 mm | ≥600 × ≥550 footprint |
| Bath | — | — | — | 1500 mm deep in front of the access side |
| Shower | — | 800–1000 mm clear | 1500 × 1500 mm | tray **900 mm** wide, also 750 mm |

Neufert carries an explicit warning worth honouring: the German standard for
bathroom movement areas **was withdrawn in 2007 without replacement**, so its
bathroom figures should be treated as absolute minimums and accessible-building
dimensions preferred.

### 5.4 Windows — a method conflict, not a number conflict

This is the deepest disagreement in the corpus, and the one that most directly
threatens a validator predicate.

| Regime | Rule | Status |
|---|---|---|
| **England — Building Regulations 2010, Schedule 1** | **No daylight or window-area requirement exists.** Verified by reading Schedule 1: no Part imposes one. | VERIFIED |
| England — AD F Table 1.4 | Purge **ventilation**: openable area **1/20** of floor area (windows opening ≥30°); **1/10** for 15–30°; <15° not suitable | VERIFIED |
| England — AD B ¶2.10 | Escape window: unobstructed openable area **≥0.33 m²**, **≥450 mm** height *and* **≥450 mm** width, bottom of opening **≤1100 mm** above floor | VERIFIED |
| **Scotland — Building (Scotland) Regs 2004, Sch. 5** | Mandatory **Standard 3.16 Natural lighting**, applying **only to a dwelling**. The numeric fraction sits in the Technical Handbook, which could not be retrieved. | VERIFIED that the standard exists; number is a **gap** |
| **Germany — BayBO Art. 45(2), SächsBO §47** | Windows with a **Rohbaumaß** (structural opening) of **≥1/8 of the room's Netto-Grundfläche**, including glazed projections and loggias. The fraction varies **1/8 or 1/10 by Land**. | VERIFIED (Bayern first-hand) |
| **Japan — Building Standards Act Art. 28** | Daylight openings **between 1/5 and 1/10** of floor area, the exact ratio fixed by Cabinet Order per room type; effective area computed via a **採光補正係数 daylight correction factor** that depends on distance to the site boundary and the zoning district (Order Art. 20). Ventilation openings **≥1/20**. | VERIFIED |
| **Metric Handbook** | No area fraction. **Average daylight factor** formula; >5% generous, <2% gloomy. | VERIFIED |

Four incompatible things are going on:

1. **England says nothing.** You cannot fail a daylight test that does not exist.
   *Scotland, in the same country, mandates one.* Intra-UK divergence again.
2. **Germany measures the structural opening against net floor area.** Comparing
   Germany's 1/8 (12.5%, rough opening) with a US 8% (glazed area) is not
   like-for-like — a rough opening is meaningfully larger than the glazed area,
   so the real gap is smaller than 12.5 vs 8 suggests. Naive comparison
   overstates it.
3. **Japan's rule is not a room property at all.** It depends on the distance to
   the neighbouring boundary and the zoning district. **No `window_area >= k *
   floor_area` constraint can represent it**, because `k` is a function of the
   site, not the room.
4. **The Metric Handbook's method needs glazing transmittance, sky angle, room
   surface areas and reflectances** — none of which exist in a Plan at the stage
   this constraint would be checked.

**Resolution.** C6 item 4 says *"every habitable room touches an exterior wall and
gets a window."* Keep that as a **topological** predicate — exterior-wall adjacency
plus at least one hosted window opening — because topology is the part all four
regimes agree on. Put the *numeric* ratio in the region profile as a soft
objective, defaulting to the German 1/8 (on rough opening) for `DE`, and to a
chosen value with `ENGINE_CHOICE` provenance for `UK`, where no regulatory number
exists to borrow. Do not attempt a universal ratio. Do not attempt Japan's rule at
all in v1; declare it out of scope for the `JP` stub.

**Sill and head heights — two constraints on two components, not one number.**
The German case makes this unavoidable:

| Driver | Requirement | Direction |
|---|---|---|
| Fall protection — MBO §38 / SächsBO §38 | Fensterbrüstung **≥800 mm** where the fall is ≤12 m; **≥900 mm** above 12 m. Trigger at a **>1 m** drop. | **UP** |
| Accessibility — DIN 18040-2 | Sill **≤600 mm** so a seated person can see out (phrased as *"erleichtern"*, facilitate — a recommendation, not a requirement) | **DOWN** |

A 200 mm irreconcilable gap. **There is no masonry sill height that satisfies
both.** German practice resolves it by decoupling: glaze down to ≤600 mm and
provide fall protection separately, as fall-resistant glazing (DIN 18008) or a
railing in front. SächsBO §38(1) expressly disapplies the guarding duty *"wenn die
Umwehrung dem Zweck der Flächen widerspricht"*.

England has the same squeeze, and it is tighter:

- AD K Diagram 3.1: guarding **at opening windows — 800 mm** (and 900 mm for
  internal floor edges in single-family dwellings, 1100 mm for external
  balconies). VERIFIED.
- AD M ¶2.24c / ¶3.31c: glazing to the principal window of the principal living
  area must **start at most 850 mm** above floor level, *or* at the minimum height
  necessary to comply with Part K. VERIFIED.
- AD B ¶2.10a(iii): bottom of an escape window's openable area **≤1100 mm**.

So the principal living-room window sill in England is pinned into an **800–850 mm
band**, from three different Approved Documents. That is a fully-verified,
OGL-licensed, directly-encodable cross-constraint — and a good demonstration of
what this table is for.

**Modelling decision:** the Plan carries `sill_height` on the window and a
separate optional `fall_barrier` component. Collapsing them into one attribute
makes the German case unsolvable.

### 5.5 Ceiling heights

| Regime | Value | Status |
|---|---|---|
| **Bayern — BayBO Art. 45(1)** | **2400 mm**; attic 2200 mm over half the usable area, ignoring parts under 1500 mm. **Does not apply to habitable rooms in residential buildings of building classes 1 and 2** — i.e. exactly the detached/small houses C5 scopes us to. | **VERIFIED** |
| Sachsen — SächsBO §47 | 2400 mm | VERIFIED |
| Berlin — BauO Bln §44(1) | **2500 mm**; attic 2300 over ≥50% | REPORTED |
| Other Länder | 2400 mm modal; attic relaxations 2200–2300; Hessen down to 2200 in cellars/attics | REPORTED |
| MBO §47 | **Contested — 2.40 m and 2.50 m are both asserted by German Wikipedia in different articles.** Both Länder checked against primary law say 2400. | **UNRESOLVED** |
| **England** | **No Building Regulations requirement since 1985.** NDSS ¶10(i): **2300 mm over at least 75% of the GIA** — planning policy, optional. Metric Handbook's own position: 2300 minimum reasonable, **2400 preferable**; London SPG encourages 2500 over 75%. | VERIFIED |
| **Japan — Enforcement Order Art. 21** | **2100 mm**, measured from the floor, **averaged** where the ceiling varies. | **VERIFIED** |

Spread **2100–2500 mm**. The Bavarian GK 1–2 exemption is worth flagging: for
single-family houses, Bavaria imposes no minimum room height at all, which means
the 2400 mm figure the engine would use for `DE` is a *convention*, not a
requirement, for precisely our building type.

### 5.6 Wall thicknesses by construction type

| | Germany (masonry) | UK (cavity + stud) |
|---|---|---|
| Internal partition | **115 mm** | ~100 mm timber/metal stud + linings |
| Internal load-bearing | **175 mm** or **240 mm** | 100 mm block + linings |
| External, monolithic | **365 mm** typical without added insulation, excluding render; 300 / 425 / 490 mm variants | n/a |
| External, cavity | load-bearing leaf ≥115 mm; outer weather leaf ≥90 mm; cavity 40–150 mm (Neufert) or 60–80 mm (DIN 1053) | 102.5 mm brick + cavity + 100 mm block ≈ 300 mm + finishes |
| Unit format | DF 240×115×52; **NF 240×115×71**; 2DF 240×115×113 | work size **215 × 102.5 × 65**; coordinating **225 × 112.5 × 75** |

The German series derives from the **125 mm octametric module** (DIN 4172):
Baunennmaß = Baurichtmaß − one 10 mm joint, so 125→115, 250→240, 375→365,
500→490. **175 and 300 do not follow that rule** and appear to be independently
standardised thicknesses for modern perforated and calcium-silicate units. Do not
present the series as a single arithmetic progression — that would be inventing a
derivation. All REPORTED; DIN 1053 and DIN 4172 were not read.

Neufert supplies a plannable wall-thickness table (DIN 1053-1: internal ≥115,
solid external ≥175, cavity load-bearing leaf ≥115, with tabulated clear-height
and imposed-load limits). **The Metric Handbook supplies no equivalent** — it
handles masonry by load capacity and slenderness and gives wall build-ups only in
U-value contexts. So for UK defaults there is no book to quote; 102.5 + cavity +
100 is convention, not standard.

**This is the largest single geometric divergence in the corpus.** A 365 mm German
external wall against a ~300 mm UK cavity wall changes the internal area of a
100 m² footprint by roughly 2 m². US light frame (§5.8) widens the gap further.

### 5.7 Floor area measurement — the conflict beneath all the area numbers

**Germany, Wohnflächenverordnung** (VERIFIED, gesetze-im-internet.de):

- §3 — measured on **interior finished dimensions**. Components projecting >1.50 m
  high and covering >0.1 m² are deducted.
- §4 — **100%** where clear height ≥2.00 m; **50%** where ≥1.00 m and <2.00 m;
  **0%** below 1.00 m; **50%** for unheated winter gardens; **25%, up to a maximum
  of 50%**, for balconies, loggias, roof gardens and terraces.
- §2 — excludes cellars, storage rooms, laundry, attics, drying and heating
  rooms, garages.

**UK GIA** (NDSS ¶8, VERIFIED): *"the total floor space measured between the
internal faces of perimeter walls that enclose the dwelling"* — binary, no
headroom grading, balconies excluded.

**These produce different numbers for the same building.** An attic dwelling can
lose 20–30% of its Wohnfläche to the 1.00/2.00 m bands while its GIA is unchanged.
A flat with a balcony gains up to half the balcony in Germany and none in the UK.
DIN 277 (BGF/NRF/NUF) is a *third* system that counts under-slope areas below 2 m
**in full**.

**Consequence for the schema: a minimum-area value that does not carry its
measurement convention is meaningless.** The JSON therefore records
`area_convention` per region profile, and the brief's `target_area` must be
stamped with one. This is a real requirement propagating to ticket 10.

RICS Code of Measuring Practice, IPMS 1/2/3 and US ANSI Z765 could not be
reached; the US convention is a declared gap.

### 5.8 The US works — Time-Saver Standards, Graphic Standards, IRC

*This section pending the US research pass; see §10.*

### 5.9 Stair geometry — captured for the record

Multi-storey is out of scope (C5), but a stair may appear in a single-storey
plan's entry, and the geometry is cheap to carry.

| | UK — AD K Table 1.1 (private stair) | Germany — DIN 18065:2020-08 | Neufert | Japan — Order Art. 23 |
|---|---|---|---|---|
| Rise / riser | **150–220 mm** | ≤190 mm (or 140–200) | 170 optimum | ≤220 general; **≤230 for dwelling stairs** |
| Going / tread | **220–300 mm** | 260–320 design (260–370 outer limit) | 290 optimum | ≥210 general; **≥150 for dwelling stairs** |
| Step rule | **2R + G = 550–700 mm** | **2s + a = 590–650 mm** | **2R + G ≈ 625 mm** (stride 590–650) | — |
| Max pitch | **42°** | (22°–45° range of the rule) | 30° stated optimum | — |
| Headroom | **2000 mm** | ≥2000 mm, 2100 recommended | not recovered | — |
| Min clear width | no legal minimum for houses; AD M **850 mm** for stair-lift capability; MH's own advice **800 mm** | **UNCONFIRMED** — the LBOs deliberately omit it and delegate to DIN | 800 mm (≤2 dwellings); 1000 mm (flats); 1250 mm (high-rise) | **750 mm** |
| Guarding | 900 mm internal in single-family dwellings; 1100 mm external balconies; 800 mm at opening windows | 900 mm to 12 m; 1100 mm above | — | — |

The three step rules nest: Neufert's point value 625 sits inside DIN's 590–650,
which sits inside AD K's 550–700. **Neufert is the strictest and the UK the
loosest.** A stair at AD K's 550 or 700 extreme would be rejected by Neufert's
rule. And Japan's dwelling minimum (230 rise / 150 tread) is outside all three.

For the record: German building law **deliberately contains no stair geometry** —
BayBO Art. 32(5) and SächsBO §34 say only that the usable width *"must be
sufficient for the greatest expected traffic"*, delegating the numbers to DIN
18065 via the MVV TB. So the `DE` stair profile cannot be sourced from law at all,
only from a paywalled standard. That is a structural argument for why the `UK`
profile is the verification profile.

---

## 6. Where the sources conflict, which number wins

### 6.1 The resolution rule

Applied in order:

1. **If the quantity is body-derived, take the ergonomic source (Neufert or the
   Metric Handbook's anthropometrics) and do not regionalise it.**
2. **If the quantity is convention-derived, take the region profile. Never
   average across regions.** An averaged corridor width beside an un-averaged
   bedroom minimum describes no real building tradition.
3. **Within a region, prefer the source with the strongest force**, and record
   the force: statutory > statutory guidance > planning policy > warranty
   standard > book. This is why the tier exists.
4. **Where a book and a regulation disagree inside the same region, the
   regulation wins for `statutory_floor` and the book informs `market_default`.**
   Neufert's kitchen gangway is the model case: the UK regulation says 1200 mm
   for M4(2), Neufert says 1500 mm recommended — so 1200 is the floor and Neufert
   pushes the default up.
5. **Where the disagreement is about the *form* of the rule, not its value, do
   not resolve it numerically — model both.** Windows and sills, §5.4.
6. **Where a number cannot be verified from a source we may lawfully rely on,
   re-derive it from clearances and furniture footprints and mark it
   `ENGINE_CHOICE`.** §7.6.

### 6.2 The conflicts that matter, resolved

| # | Quantity | The disagreement | Resolution |
|---|---|---|---|
| **C1** | **Minimum bedroom area** | 7.5 / 8.5 / 11.5 / 12.5 / 13.5 m² *within England*; **no number at all** in German or Neufert; ≈8 / ≈13 m² illustrative in Neufert | **Tier, not region, is the discriminator.** Floor = NDSS; default = an ENGINE_CHOICE between NDSS and Neufert's illustrative; accessible = M4(3). §4. |
| **C2** | **Ceiling height** | 2400 (DE) vs 2300 (UK, optional) vs 2100 (JP) vs 2500 (Berlin) | **Region.** 2400 for `DE`, 2300 for `UK` floor with 2400 as `UK` default (following the Metric Handbook's own "2.4 m is preferable"). Never blend. |
| **C3** | **Kitchen gangway** | MH 1000 · AD M M4(2) 1200 · DIN base 1200 · **Neufert 1200 min / 1500 rec** · AD M M4(3) 1500 · DIN R 1500 | **Neufert wins the default.** 1200 as floor, **1500 as `market_default`** — because C2's "would I live here" test and because two regions' accessibility tiers independently land on 1500. The MH's 1000 is its own unsourced advice and is the outlier. |
| **C4** | **WC door clear width** | Neufert ≈700 mm vs AD M **750 mm** minimum | **Regulation wins.** A Neufert-standard 700 mm WC door is non-compliant in England. Use 750 as the universal floor; this is one of the few places a UK number should propagate to `DE` too, because 700 mm is simply tight for a body. |
| **C5** | **Door module** | DIN **125 mm** grid vs UK imperial/100 mm | **Region, hard.** Not an ergonomic disagreement — a product incompatibility. 860 mm and 826 mm are different manufactured objects. Snap to the region's grid or the walls will not course. |
| **C6** | **Internal door clear height** | Neufert ≥2100 ("better 2100–2250"); DIN 18040-2 ≥2050; the commonest UK leaf (1981 mm) gives **less than 2100** | **Region.** Neufert's minimum is unmeetable with standard UK doors. `DE` 2050, `UK` ~1981 leaf. Do not impose Neufert's figure globally. |
| **C7** | **2R + G constant** | Neufert **625** (point) · DIN **590–650** · AD K **550–700** | **Neufert as the objective, AD K as the constraint.** Target 625; accept the region's band. Classic C10 shape. |
| **C8** | **Bed-side clearance** | AD M M4(2) 750 · DIN base 900/1200 · AD M M4(3) 1000 · Neufert/DIN 18025 1200 · DIN R 1500 | **Tier.** Floor 750, default 900, accessible 1200. Note the German baseline exceeds the UK accessible tier — so the tier ladder is *region-relative*, not absolute. |
| **C9** | **Window rule** | 1/8 rough opening (DE) · nothing (England) · Standard 3.16 exists (Scotland) · 1/5–1/10 × site factor (JP) · daylight factor (MH) | **Do not resolve numerically.** Keep topology as the hard rule; ratio is a per-region soft objective. §5.4. |
| **C10** | **Window sill** | ≥800 fall protection vs ≤600 accessibility (DE); 800–850 band (UK, three documents) | **Model two components, not one number.** §5.4. |
| **C11** | **Corridor for two people** | Neufert **1000** ("allows two people to pass") vs MH **1200–1400** | **MH wins**, and note this reverses the usual pattern — here Neufert is the *less* generous source. 1000 as floor (it is also AD M's head-on 900 rounded up), 1200 as default. |
| **C12** | **Work triangle** | **Absent from Neufert.** MH 5–7 m. | Attribute to the Metric Handbook. Carry as a soft objective only; it is a layout heuristic, not a clearance. |
| **C13** | **Wall thickness** | DE 115/175/240/365 tabulated; UK has **no book table at all** | **Region, and accept the asymmetry.** `DE` from DIN 1053 via Neufert; `UK` from convention (102.5 + cavity + 100), marked ENGINE_CHOICE because no source prescribes it. |
| **C14** | **Area measurement convention** | Wohnfläche graduated vs GIA binary vs DIN 277 full | **Not a number conflict — a units conflict.** Stamp every area with its convention. §5.7. |

### 6.3 What "blending" would actually have produced

Worth stating concretely, because the ticket asked whether a blended table would
be incoherent. Take the arithmetic mean of the surveyed values and you get: a
2333 mm ceiling, a 1233 mm kitchen gangway, a 240 mm external wall, and a stair
step rule of 2R+G ≈ 620 with a 190 mm going. That building has German wall
proportions with a British ceiling, a kitchen too tight for the German fittings it
implies, and a stair that is illegal in the UK and impossible in Germany. **It is
not a compromise; it is a fourth thing that nobody builds.**

### 6.4 Non-Western contrast — partial

Japan was verified first-hand and is reported above (2100 mm ceilings, 230/150
dwelling stairs, 750 mm stair width, site-dependent daylight, 1/20 ventilation).

India's National Building Code 2016 and Model Building Byelaws 2016 — widely
cited for a 9.5 m² habitable-room minimum, 2.75 m ceiling height and a 5.0 m²
kitchen minimum — **could not be verified.** Every route to the primary documents
returned 403 or 404, and the WebSearch budget was exhausted. **These figures are
deliberately not recorded in the data file.** If real, a 2.75 m ceiling minimum
would widen the international spread from 400 mm to 650 mm and strengthen §3
further; but an unverified number is worse than no number.

Australia's NCC and China's GB 50096 were not reached. All four are `region`
stubs with `status: "declared, not populated"`.

---

## 7. Copyright posture

**Not legal advice.** This is a practical risk posture for a non-commercial
research project (C9), written from primary case law and licence text. It states
what the cases held and what follows practically; it does not tell you what a
court would do with these specific facts.

### 7.1 Facts are free; the arrangement of facts may not be

*Feist Publications v. Rural Telephone Service*, 499 U.S. 340 (1991), is the
foundation and it is favourable:

- *"No one may claim originality as to facts."* The discoverer *"merely finds and
  records."*
- The **"sweat of the brow" doctrine is rejected** — it *"eschewed the most
  fundamental axiom of copyright law, that no one may copyright facts or ideas."*
  Effort in compiling is not protected.
- Protection *"extends only to those components of the work that are original to
  the author, not to the facts themselves."* **"The copyright in a factual
  compilation is thin."**
- Decisively: *"A subsequent compiler remains free to use the facts contained in
  another's publication to aid in preparing a competing work, so long as the
  competing work does not feature the same selection and arrangement."*

That last sentence is close to a licence for what this ticket does — provided the
selection and arrangement are ours.

### 7.2 The crux: is "minimum clearance 750 mm" a fact or an authored judgement?

This is where an honest posture has to slow down, because two circuits have held
that numbers which *look* like facts are protected when they are the author's
estimates rather than observations:

- ***CCC Information Services v. Maclean Hunter Market Reports***, 44 F.3d 61
  (2d Cir. 1994) — the *Red Book* used-car valuations were held protectable,
  because they were the editors' predictions of future prices in a region, not
  reports of actual transactions.
- ***CDN Inc. v. Kapes***, 197 F.3d 1256 (9th Cir. 1999) — wholesale coin prices
  in a price guide were held to have sufficient originality, because they were the
  compiler's own estimates derived from judgement, not a listing of trades.

*(Both are REPORTED here: the full opinion texts were behind 403s and the
CourtListener opinion API required authentication. The citations and holdings are
standard; the reasoning above should be checked against the opinions before
anyone relies on it.)*

Applied to our corpus, the answer **splits, and the split maps exactly onto the
region/tier structure**:

| Kind of number | Closer to | Why |
|---|---|---|
| *"Bath 700 × 1700 mm"* | **fact** | A measurement of a manufactured object. |
| *"Rise 150–220 mm, going 220–300 mm"* in AD K | **fact, and also law** | A published regulatory limit, not an estimate. |
| *"Minimum single bedroom 7.5 m²"* in the NDSS | **fact, and also policy** | A promulgated government standard. |
| **"Recommended kitchen gangway 1500 mm"** in Neufert | **arguably an authored judgement** | Nobody measured 1500; a designer concluded it. This is the *CDN* shape. |
| **Neufert's illustrative "≈13 m² double bedroom"** | **authored judgement** | It is a description of a drawing Neufert made. |

**Practical consequence, and it drives the whole design:** the numbers most exposed
to a *CDN*-style argument are precisely the ones we are **least** relying on — the
recommended-value layer of the commercial books. The numbers we lean on hardest
are regulatory. And where we *do* take a Neufert recommendation, §7.6's rule
applies: re-derive it or corroborate it, and mark it `ENGINE_CHOICE` so it is our
judgement in our arrangement, not a transcription of theirs.

### 7.3 EU / UK: the database right is a separate hazard, and it is the sharper one

Copyright originality in the EU/UK is *"the author's own intellectual creation"*
(*Infopaq*, C-5/08; *Football Dataco*, C-604/10) — a similar threshold to Feist.
But there is a **second, independent right** that does not depend on originality
at all.

UK implementation, read verbatim from legislation.gov.uk:

- **Reg 13(1):** *"A property right ('database right') subsists … in a database if
  there has been a substantial investment in obtaining, verifying or presenting
  the contents of the database."*
- **Reg 16(1):** infringement is to *"extract or re-utilise all or a substantial
  part of the contents"*.
- **Reg 16(2):** *"The repeated and systematic extraction or re-utilisation of
  insubstantial parts of the contents of a database may amount to the extraction
  or re-utilisation of a substantial part of those contents."*

Two things follow.

**Reg 16(2) is the real constraint on a project like this.** Taking one number
from Neufert is plainly insubstantial. Systematically walking Neufert's
residential chapter and lifting every clearance into a machine-readable file is
exactly what 16(2) describes. **The hygiene rule that follows is: never
strip-mine a single work.** Draw from many sources, prefer the freely-licensed
ones, and let the shape of the extraction be driven by our schema rather than by
their chapter order.

**There is a counter-argument, and it cuts both ways.** *British Horseracing Board
v William Hill* (C-203/02) held that investment in *"obtaining"* means resources
spent seeking out and collecting **pre-existing** materials, not resources spent
**creating** the data. If Neufert's recommended clearances are *created* by
Neufert (§7.2), then to that extent there may be **no database right** in them.
But the same premise strengthens the *CDN* copyright argument. You cannot have it
both ways: the more "authored" the numbers, the weaker the database right and the
stronger the copyright; the more "obtained", the reverse. Assume the worse of the
two for any given number.

### 7.4 The "it's the law now" safe harbour — real, and it does not reach our books

There is a strong and recently-strengthened line of US authority that standards
incorporated into law may be republished:

- ***Veeck v. Southern Building Code Congress Int'l***, 293 F.3d 791 (5th Cir.
  2002) (en banc) — model codes, once enacted into law by a municipality, may be
  copied as the law. *(REPORTED — the opinion text was not retrievable this
  session.)* Its limit is important: model codes **not** enacted remain protected.
- ***ASTM v. Public.Resource.Org***, 82 F.4th 1262 (D.C. Cir. 2023) — non-profit
  posting of 184 standards directly incorporated by reference into law was fair
  use; the use *"serve[d] a different purpose than the plaintiffs' works"*.
- ***ASTM v. UpCodes***, No. 24-2965 (3d Cir., 7 April 2026) — **read
  first-hand.** A **commercial** building-code platform's republication was held
  likely fair use; the court affirmed denial of a preliminary injunction. The use
  was transformative because it *"achieves the distinct objective of making the
  law freely accessible and educating the public on the contents of binding
  laws"*, and the court rejected the argument that verbatim republication cannot
  be transformative: *"This position overlooks the first factor's focus on
  purpose, not merely expressive similarity."*

**This does not help us with Neufert, the Metric Handbook, Time-Saver Standards
or Graphic Standards, because none of them is law.** The entire doctrine turns on
the work having the force of law. It *does* support treating the IRC, DIN 18040
where a Land's MVV TB makes it a Technische Baubestimmung, and any
incorporated-by-reference standard as materially safer than a trade book. It is
one more reason to prefer the regulatory layer.

For completeness: the CJEU decided *Public.Resource.Org v Commission* (C-588/21 P)
on 5 March 2024 concerning access to **harmonised EN standards**. Its text was
not retrievable this session and its holding is therefore not stated here. Note in
any case that **DIN 18040 is a national DIN standard, not a harmonised EN**, so
that case would likely not reach it. German §5 UrhG (*amtliche Werke*, official
works free of copyright) covers the Landesbauordnungen — which is why quoting
BayBO Art. 45 verbatim above is unproblematic — but is generally **not** accepted
as covering DIN standards, which DIN e.V. sells through Beuth.

### 7.5 What is affirmatively free

Read verbatim from the National Archives:

> **Open Government Licence v3.0** — you are free to *"copy, publish, distribute
> and transmit the Information; adapt the Information; exploit the Information
> commercially and non-commercially … by including it in your own product or
> application"*, provided you *"acknowledge the source"* and link to the licence.

gov.uk carries this on every Approved Document and on the NDSS. **So the entire UK
regulatory layer used in this note — AD M, AD K, AD F, AD B, the NDSS, and AD M
Appendix D's furniture schedule — may be encoded, reproduced and redistributed,
including commercially, with attribution.** The exclusions (personal data, logos,
Royal Arms, third-party rights) are irrelevant to dimensional data.

Also free in practice: `legislation.gov.uk` (OGL), Japanese law via e-Gov,
Bavarian and Saxon law via their official portals, US federal works under
17 U.S.C. §105 (so the ADA Standards for Accessible Design).

**This is why the `UK` profile is the verification profile.** It is the only
complete regional profile the project can hold, publish, and regression-test
without licence risk.

### 7.6 The concrete posture

**May do:**

1. **State an individual dimensional value with a citation.** *"Minimum single
   bedroom 7.5 m², NDSS ¶10(c)"* — a fact from a document we are licensed to
   reproduce anyway. Even from a copyrighted book, a single number is
   unprotectable under Feist.
2. **Publish a table of ~30 room types × 7 attributes** where the row set, the
   column set and the ordering are ours, each cell traced to a different source,
   and no single source supplies a substantial part. This is precisely Feist's
   *"free to use the facts … so long as the competing work does not feature the
   same selection and arrangement."*
3. **Reproduce OGL material as much as we like**, with attribution — including
   AD M's furniture schedule and AD M Table 1.1 verbatim.
4. **Quote a short regulatory clause verbatim** for provenance (BayBO Art. 45,
   AD K Table 1.1). Government material, and short quotation for criticism or
   review is within CDPA s.30 in any event.

**May not do:**

5. **Reproduce Neufert's or the Metric Handbook's own table** — its ordering, its
   selection of which quantities to tabulate, its row groupings. That is the thin
   copyright Feist leaves intact, and it is the thing most easily proven.
6. **Reproduce any diagram or figure, from any of the books.** Categorically. A
   drawing is a pictorial work protected as expression independently of the facts
   it depicts; there is no fact/expression escape hatch for a drawing. Redrawing
   from the same dimensions is fine; tracing, cropping or reproducing is not.
7. **Systematically extract one work's tables into a data file.** UK Databases
   Regs reg 16(2). This is the specific failure mode a project like this walks
   into by accident.
8. **Ship the source PDFs**, including the Internet Archive OCR copies of Neufert
   and the Metric Handbook that this research read. They are not
   publisher-authorised uploads. Reading them to establish facts is one thing;
   redistributing them is another, and the project must not do it.

**Does attribution cure it?** **No.** Attribution answers *plagiarism*, which is
an academic-ethics failure, not *infringement*, which is a property right. People
conflate them constantly. The one exception is the OGL, where attribution is
literally the licence condition — there, crediting the source *is* what makes the
use lawful.

**Does non-commercial use cure it?** **No, and this needs saying plainly given
C9.** In the US, non-commercial purpose is **one sub-factor of one of four**
fair-use factors (17 U.S.C. §107(1)) — it helps, it does not decide. In the EU and
UK there is **no general fair use at all**, only enumerated exceptions; the
relevant ones are CDPA **s.29** (research and private study, and that exception is
itself limited to **non-commercial** research) and **s.30** (quotation, criticism,
review), both narrow. C9's non-commercial posture meaningfully reduces exposure.
It does not remove it, and it would evaporate the moment the project changed
posture — which is an argument for building the hygiene in now rather than later.

**Hygiene practices, in force from this ticket onward:**

9. **Prefer freely-published regulatory sources over commercial books** for every
   number the engine actually depends on. This is why the constraint table leans
   on OGL and statutory material and treats the books as corroboration.
10. **Corroborate every load-bearing number against at least two independent
    sources**, and record both. A number that appears in AD M *and* in DIN
    18040-2 is a fact about human bodies, not a Neufert expression.
11. **Cite to clause, not to page.** A clause reference is a fact about the
    source; a page reference is a pointer into a specific edition's layout.
12. **Re-derive rather than transcribe wherever a derivation exists.** Worked
    example, used in the data file: the dining-room minimum is *not* copied from
    anywhere. It is computed — a 6-person table at Neufert's 600 mm per place is
    1950 × 800 mm; add Neufert's 800 mm movement area on each side; the room is
    3550 × 2400 mm ≈ 8.5 m², rounded to 9.0 m². The output is our arithmetic over
    two clearance primitives, which is a different thing in kind from lifting a
    tabulated area.
13. **Let our schema drive the extraction, not their chapter order.** The room
    taxonomy in the data file exists because the solver needs it, and it does not
    match any surveyed work's organisation.
14. **Mark provenance in the artefact itself.** Every value in the JSON carries
    `src`, `ref` and `conf`. If a source is later found to be
    unreliable or unusable, the affected values can be found and replaced rather
    than the whole table being suspect.

---

## 8. The constraint table

Canonical machine-readable form: **`data/standards/room-constraints.json`**.

The four booleans are **definitions, not measurements** — no reference work
supplies them. They are stated operationally because ticket 7's predicates depend
on them:

- **`is_habitable`** — intended for sustained occupation. Drives the window and
  exterior-wall requirement. **Deliberately not any national legal definition**
  (see the kitchen note below).
- **`is_wet`** — contains a plumbed fixture. Drives wet-room clustering, C6 item 5.
- **`is_private`** — must not lie on the circulation path to any other room.
  Drives the reachability predicate, C6 item 1.
- **`needs_window`** — set true wherever `is_habitable` is true. **An engine
  decision**, per §5.4, because England imposes no such rule and the others
  disagree about its form.

**The kitchen is the disagreement to be aware of.** Under BayBO Art. 46(1) a
German dwelling must have a kitchen or kitchenette, and *"fensterlose Küchen oder
Kochnischen sind zulässig, wenn eine wirksame Lüftung gewährleistet ist"* — a
windowless kitchen is permitted with effective ventilation. So a German kitchen is
**not** an Aufenthaltsraum unless it is a Wohnküche. The Metric Handbook records
that in UK density calculations a dining kitchen counts as a habitable room
**only if larger than 13 m²**. We set `is_habitable: true` for `kitchen_dining`
and `false` for `kitchen`, and `needs_window: false` for `kitchen` — following
the German rule, because it is the one that is actually stated.

### The default profile (region `DE`, tier `market_default`)

Lengths in mm, areas in m². `min_width` and `min_depth` are equal wherever the
room is orientation-free.

| Room type | Min area | Min width | Min depth | Needs window | Is wet | Is habitable | Is private |
|---|---|---|---|---|---|---|---|
| `living` | 16.0 | 3200 | 3200 | yes | no | yes | no |
| `dining` | 9.0 | 2400 | 2400 | yes | no | yes | no |
| `kitchen` | 6.5 | 1800 | 1800 | no | yes | no | no |
| `kitchen_dining` | 11.0 | 2600 | 2600 | yes | yes | yes | no |
| `living_dining_kitchen` | 25.0 + 2.0/bedspace over 2 | 3200 | 3200 | yes | yes | yes | no |
| `bedroom_principal` | 13.0 | 2750 | 2750 | yes | no | yes | **yes** |
| `bedroom_double` | 12.0 | 2750 | 2750 | yes | no | yes | **yes** |
| `bedroom_single` | 8.0 | 2200 | 2200 | yes | no | yes | **yes** |
| `study` | 7.0 | 2200 | 2200 | yes | no | yes | no |
| `bathroom` | 4.4 | 1900 | 1700 | no | **yes** | no | **yes** |
| `shower_room` | 3.6 | 1600 | 1600 | no | **yes** | no | **yes** |
| `wc` | 1.8 | 1000 | 1650 | no | **yes** | no | **yes** |
| `utility` | 3.0 | 1600 | 1600 | no | **yes** | no | no |
| `hall` | 3.0 | 1200 | 1200 | no | no | no | no |
| `corridor` | — | 1050 | — | no | no | no | no |
| `entrance_lobby` | 1.5 | 1200 | 1200 | no | no | no | no |
| `storage` | 1.0–4.0 by bedroom count | 600 | 600 | no | no | no | no |

Directional notes: `kitchen` min width 1800 is a **single-run** kitchen (600 unit
+ 1200 clearance); two opposing runs require **2700** (600 + 1500 + 600) and that
is enforced as an aisle clearance, not a room minimum. `bathroom` and `wc` are the
only rooms with a genuinely distinct width and depth, both driven by fixture
footprints (bath 1700 long; WC pan ~700 + 750 transfer space + cistern).

Every cell's `statutory_floor` and `accessible` variants, and the per-value source
and confidence, are in the JSON. Summarising the provenance pattern:

- **`statutory_floor` areas** come from the NDSS and AD M M4(3) (`UK`), and are
  **`null` for `DE`** because German law prescribes none. A null floor means "no
  hard area constraint in this region", not "unknown".
- **`market_default` areas are all `ENGINE_CHOICE`**, each with the corroborating
  range recorded. This is deliberate, per §7.6.
- **`accessible` values** come from AD M M4(3) (`UK`) and DIN 18040-2 R (`DE`,
  REPORTED).
- **Clearances** are in the shared ergonomic layer and carry no region.

---

## 9. What this hands to the tickets that consume it

**To *Acceptance validator spec* (7):**

- C6 item 2's *"no sub-1m corridors"* → **900 mm** head-on, **1050 mm** with a
  775 mm door not approached head-on, **1200 mm** with a 750 mm door not head-on;
  a **750 mm** pinch permitted for ≤2 m. AD M Table 1.1, OGL.
- C6 item 2's *"minimum dimensions per room type"* → §8, with the tier deciding
  hard vs soft. The `statutory_floor` tier **is** the hard predicate set.
- C6 item 3's *"door fits its wall and its swing hits nothing"* → the corpus gives
  components, not a predicate: 300 mm leading-edge nib maintained 1200 mm; 1500 mm
  between opposed door swings in a lobby; outward-opening WC door overlapping the
  pan by 250 mm; leaf-to-clear-width conversion ≈51 mm (UK) — and a **125 mm
  module constraint** on the structural opening for `DE`. Ticket 7 must compose
  these.
- C6 item 4's *"gets a window"* → keep as **topology**. Do not adopt a ratio as a
  hard rule; §5.4.
- C6 item 6's *"thicknesses standard"* → §5.6, region-dependent, and note the UK
  values are ENGINE_CHOICE because no source prescribes them.
- **Every number needs its tier and its region stated in the predicate**, or the
  validator will silently encode one country's conventions.

**To *Brief schema and parsing contract* (10):**

- Defaults for unstated fields come from `market_default`, **not**
  `statutory_floor`. §4.
- The Brief needs an **`area_convention`** field, or its `target_area` is
  ambiguous by up to 20–30% for the same building. §5.7. This is a new
  requirement this ticket discovered.
- The Brief needs a **`region`** field, or the defaults cannot be resolved. It
  should be the same enum as ticket 6's.
- Occupancy is directly usable: the LKD area rule is `25 + 2 × (bedspaces − 2)`
  m², and storage is a function of bedroom count. "A family of four" resolves to
  real numbers.
- An invented **area** is a different kind of Assumption from an invented
  **room** (CONTEXT.md already says so); this table adds a third — an invented
  **region**, which silently changes every other default. It should be surfaced
  the most loudly of the three.

---

## 10. Gaps, and what would close them

Stated as unknown rather than filled in.

1. **The US layer is not in this note.** Time-Saver Standards, Architectural
   Graphic Standards, the IRC (R304 areas, R305 ceiling height, R310 escape
   openings, R303 8%/4% light and ventilation, R311.7 stairs), ICC A117.1/ADA,
   and — most important geometrically — **US light-frame wall thicknesses (2×4 and
   2×6 stud walls)**, which are the largest divergence from European masonry in
   the whole corpus. The `US` profile in the JSON is a declared stub. A research
   pass was launched and had not reported when this note was written.
2. **The imperial-vs-metric rounding problem** is therefore also unquantified.
   The expectation is that US-native numbers are round in inches and ugly in
   millimetres (36 in = 914 mm, not 900), which matters because it means the `US`
   profile cannot share the metric grid. Unverified.
3. **No DIN standard was read.** Every DIN 18040 / 18065 / 18101 / 4172 / 1053
   number is REPORTED. Closing this costs money, not effort.
4. **MBO §47 room height: 2.40 or 2.50 m** — sources contradict; both Länder
   checked say 2400. The MBO PDF is behind a session-bound download.
5. **DIN 18065 minimum stair width** — no source. The LBOs deliberately omit it.
6. **DIN 18040-2 corridor width** — the figures found are probably Part 1 values
   contaminating a Part 2 page.
7. **Which Länder use 1/10 rather than 1/8** for window area.
8. **Scotland's Standard 3.16 numeric fraction** — the standard is verified to
   exist; the Technical Handbook PDF exceeded the fetch size limit.
9. **India NBC 2016, Australia NCC, China GB 50096** — unverified; §6.4.
10. **ISO 21542, EN 17210, CEN/TR 17621** — paywalled. Note that EN 17210 is
    **functional/performance-based and contains no millimetres**; the numbers are
    in CEN/TR 17621, a non-binding Technical Report. So EN 17210 is not a drop-in
    numeric source even if bought.
11. **RICS Code of Measuring Practice, IPMS 1/2/3, ANSI Z765** — unreachable, so
    the measurement-convention comparison in §5.7 has a US-shaped hole.
12. **Neufert 6th ed. (2023) and Metric Handbook 7th ed. (2021)** — everything
    here is from the 4th and 6th editions. Neufert's 6th is advertised as revising
    stairs and lighting, so several §5.9 numbers may have moved.
13. **Neufert's general bed-surround clearance and stair headroom** — carried in
    figures the OCR destroyed. Present in the printed book; not invented here.
14. ***CDN*, *CCC* and *Veeck* opinion texts** were not retrievable; §7.2 and §7.4
    rest on standard statements of their holdings, not on read text. *Feist* and
    *ASTM v. UpCodes* were read.
