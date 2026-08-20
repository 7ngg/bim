# Dataset inventory

Findings for *Acquire the datasets* (`docs/wayfinder/tickets/12-acquire-the-datasets.md`).
Everything here was measured on this machine on **2026-08-19** against the files
now on disk — no figure is quoted from a paper, a badge or a README without being
checked, per C11.

Corpora live under `data/corpora/`, which is **gitignored**. Nothing in this
inventory is committed except this document and the loader scripts in
`experiments/corpus-smoke/`.

---

## 0. The headline: the ≥16-room tail is empty

*Proposer architecture survey* §7.3(a) made this ticket's histogram the test that
decides between its recommendation (train a Brief-conditioned room-set
transformer) and its runner-up (retrieval-and-warp): **retrieval wins outright if
fewer than roughly 1,000 C5-surviving dwellings hold ≥16 areas**, and synthetic
pre-training fails to close the gap.

Counting the rooms a Brief actually names — no service shafts, no circulation
cores, no outdoor areas — across **both** committed corpora:

| Corpus | dwellings | mean rooms | ≥12 | ≥14 | **≥16** | ≥20 | ≥24 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Swiss Dwellings v3.0.0 | 46,800 | 6.82 | 708 | 164 | **66** | 11 | 1 |
| ResPlan 17k | 17,000 | 6.79 | 208 | 14 | **0** | 0 | 0 |
| **combined** | **63,800** | — | 916 | 178 | **66** | 11 | 1 |

**66, against a threshold of ~1,000.** The data half of §7.3(a) fires by a factor
of fifteen. The solver study's headline case — a 232.8 m² interior with 24 rooms
— has **exactly one** analogue in 63,800 real dwellings, and **none at all** if
bathrooms and kitchens are the only rooms counted alongside living and bedrooms.

Two cautions on reading it, both of which cut toward the same conclusion:

- **Ticket 18's own SQL returns 1,563, not 66,** and that gap *is* the finding —
  §1.3 below. It counts `entity_type='area'` unfiltered, and Swiss Dwellings
  carries **72,255 residential SHAFTs and 43,084 balconies**. Shafts are the
  single most common area subtype in the corpus. A shaft is not a room a Homeowner
  asks for, and the map's own *Structural and services reality* fog patch holds
  risers and stacks as explicitly unspecified for v1.
- **This settles only the data half.** Whether synthetic pre-training closes the
  gap at 16+ rooms is untested and belongs to *What the model proposes, and how it
  is trained*. What this ticket establishes is that **no amount of real data we can
  legally obtain covers the regime**, because RPLAN's maximum is 8 rooms and MSD is
  a subset of Swiss Dwellings — so a synthetic generator is now the *only* possible
  source of ≥16-room training examples, not merely the recommended first stage.

---

## 1. Swiss Dwellings v3.0.0 — acquired

### 1.1 Where it is, and what it is

| | |
|---|---|
| Source | Zenodo record [7788422](https://zenodo.org/records/7788422), DOI `10.5281/zenodo.7788422` |
| Version | **3.0.0**, published 2022-09-20 (the v3.0.0 changelog entry itself is dated 2023-03-31) |
| On disk | `data/corpora/swiss-dwellings/swiss-dwellings-v3.0.0.zip` |
| Size | **931,868,205 bytes** — matches the Zenodo record exactly |
| md5 | `3b7915ecd5bf8e492a3e78c598b74123` — **matches the publisher's md5 exactly** |
| sha256 | `382e528fae3220b7747f4e6bc7d79261fee1b5d4d7902f18c548c0e6f22ef80a` (computed here) |
| Access | Direct download, no application, no account |

Extracted to `data/corpora/swiss-dwellings/swiss-dwellings-v3.0.0/`:

| File | Bytes | Extracted? |
|---|---:|---|
| `geometries.csv` | 1,093,732,415 | yes — sha256 `7fa5e6c81102e997c82e2c5355949ccd75f3ff223c10f397b76b136e4a6d0f8f` |
| `simulations.csv` | 1,594,839,853 | **no** — daylight, viewshed, noise and centrality simulations. Nothing on this map consumes them; left in the zip rather than spending 1.6 GB |
| `locations.csv` | 5,551,909 | yes |
| `location_ratings.csv` | 87,232 | yes |

Total on disk: **1.9 GB**.

### 1.2 Licence — and an honest note about what "verbatim" could mean here

The ticket asks for the verbatim licence text from the raw file rather than the
badge. **For this corpus there is no raw file.** The zip contains four CSVs and
nothing else — no `LICENSE`, no `COPYING`, no notice file. The CC BY 4.0 grant
exists solely as structured metadata on the Zenodo deposit:

```json
"license": {"id": "cc-by-4.0"}
```

with `rights: null` and no free-text rights statement. That is materially weaker
evidence than ResPlan's checked-in licence file, and it is worth recording as a
difference rather than flattening both to "CC BY 4.0". It is not a defect —
Zenodo's deposit record *is* the authoritative licence statement for a Zenodo
deposit — but nothing travels with the files themselves, so anyone who receives
the CSVs alone receives no licence text at all.

**Provenance is the strongest of any corpus here**, and it is a named corporate
rights-holder rather than a scrape. From the deposit description, verbatim:

> The data is sourced from commercial clients of Archilyse AG specializing on the
> digitization and analysis of buildings. The existing building plans of clients
> are converted into a geo-referenced, semantically annotated representation and
> undergo a manual Q/A process to ensure the accuracy of the data and to ensure a
> maximum 5%-deviation in the apartments' areas (validated with a median deviation
> of 1.2%).

**Attribution string** (CC BY 4.0 requires attribution; paste into product credits):

> Swiss Dwellings: A large dataset of apartment models including aggregated
> geolocation-based simulation results covering viewshed, natural light, traffic
> noise, centrality and geometric analysis (v3.0.0) — Matthias Standfest, Michael
> Franzen, Yvonne Schröder, Luis Gonzalez Medina, Yarilo Villanueva Hernandez,
> Jan Hendrik Buck, Yen-Ling Tan, Milena Niedzwiecka, Rachele Colmegna.
> Zenodo, DOI 10.5281/zenodo.7788422. Licensed under CC BY 4.0.

### 1.3 Row counts as loaded, against the published figures

`geometries.csv` holds **3,255,905 rows**. Against the deposit's own stated
figures:

| Quantity | Published | Measured | |
|---|---:|---:|---|
| separators (walls, railings) | ~1.7 M | 1,700,813 | ✓ |
| openings (windows, doors) | ~715,000 | 714,936 | ✓ |
| areas | ~520,000 | 522,183 | ✓ |
| features (sinks, toilets, baths) | ~315,000 | 317,973 | ✓ |
| **apartments** | **45,176** | **46,800** | ✗ — see below |
| rooms | ~370,000 | — | not reconcilable under any filter tried |

Everything reconciles except the apartment count, and the apartment count is the
one that matters, because it is the denominator of the blocking histogram. Three
defensible keys give three different answers:

| Key | Count |
|---|---:|
| `apartment_id` alone | 44,894 |
| `(site_id, apartment_id)` — **ticket 18's SQL** | 44,957 |
| `(site_id, floor_id, apartment_id)` | 46,830 |
| `(site_id, floor_id, apartment_id)`, excluding the null-hash key | **46,800** |

**Three defects in ticket 18's blocking SQL, all found by running it:**

1. **It groups by `(site_id, apartment_id)`, and 1,672 `apartment_id`s span more
   than one `floor_id`.** Its own comment says "single floor"; its `GROUP BY` does
   not enforce it. Merging an apartment's areas across floors manufactures
   oversized dwellings — which is precisely the population the query exists to
   count. It also inflates the top of the histogram absurdly: its largest
   "dwelling" holds **690 areas**.
2. **`apartment_id` is a hash, not a per-site integer**, contradicting the deposit
   documentation's "an apartment id is only unique per site". It is near-globally
   unique — 44,894 distinct values across 44,957 site-apartment pairs — though 49
   ids genuinely do span more than one site, so the site key is still needed.
3. **`d41d8cd98f00b204e9800998ecf8427e` is `md5("")`.** 5,091 rows carry it. These
   are unattributed areas, and grouping them yields fake dwellings of 74, 37 and 34
   rooms — six of which sit at the very top of the histogram and are not dwellings
   at all. Any query over this corpus must exclude that id.

**Corrected query**, as run:

```sql
-- per-dwelling room counts: one floor, one apartment, real rooms only
SELECT n_rooms, COUNT(*) FROM (
  SELECT site_id, floor_id, apartment_id, COUNT(*) AS n_rooms
  FROM geometries
  WHERE entity_type = 'area'
    AND unit_usage  = 'RESIDENTIAL'
    AND apartment_id <> 'd41d8cd98f00b204e9800998ecf8427e'
    AND entity_subtype NOT IN (
      'SHAFT','VOID','OUTDOOR_VOID','LIGHTWELL','ELEVATOR','STAIRCASE',
      'TECHNICAL_AREA','BALCONY','LOGGIA','TERRACE','GARDEN','PATIO','WINTERGARTEN')
  GROUP BY site_id, floor_id, apartment_id
) GROUP BY n_rooms ORDER BY n_rooms;
```

One thing checked and found **not** to be a problem: `plan_id` was expected to
duplicate layouts across floors sharing a plan. It does not — 46,816 distinct
`(site_id, plan_id, apartment_id)` against 46,822 dwellings, i.e. **6 repeats
total**. There is no hidden deduplication to do.

### 1.4 The histograms

Residential areas, 46,800 dwellings, keyed `(site, floor, apartment)`, null-hash
excluded. Three filters, because the choice of filter moves the answer by an order
of magnitude and the ticket that consumes it deserves to see that:

| Filter | mean | max | ≥12 | ≥14 | ≥16 | ≥20 | ≥24 |
|---|---:|---:|---:|---:|---:|---:|---:|
| all residential areas | 9.44 | 108 | — | — | 1,563 | 285 | 94 |
| **interior rooms** (no shafts, cores, outdoor) | **6.82** | 31 | 708 | 164 | **66** | 11 | 1 |
| habitable only (bed/living/dining/kitchen/bath) | 5.40 | 17 | 43 | 10 | 2 | 0 | 0 |

Interior-room histogram in full:

```
 1:  948   2:  317   3: 1119   4: 2973   5: 6343   6: 8828   7: 8580   8: 8175
 9: 5844  10: 2191  11:  774  12:  374  13:  170  14:   66  15:   32  16:   27
17:   18  18:    2  19:    8  20:    7  22:    1  23:    2  31:    1
```

The interior-room mean of **6.82 independently corroborates Ospici's
separately-measured 6.20** — the only prior independent measurement on the map —
where the unfiltered 9.44 does not. That agreement is the reason to trust the
filtered number as the one that describes real dwellings.

24 residential area subtypes exist. The five largest are `ROOM` 82,618,
`SHAFT` 72,255, `BATHROOM` 68,434, `CORRIDOR` 53,392, `KITCHEN` 44,085 — note
that shafts outnumber bathrooms.

Two documentation mismatches worth recording: `unit_usage` carries a fifth value,
`PLACEHOLDER` (82 rows), absent from the deposit's documented list of
RESIDENTIAL / COMMERCIAL / PUBLIC / JANITOR; and 77 distinct `entity_subtype`
values exist across all entity types, which no published summary enumerates.

### 1.5 Exposure — confirmed, and it is worse than the presets assumed

*Building scope and envelope handling* asked this ticket to confirm that Swiss
Dwellings' building hierarchy can supply the real exterior/party exposure
distribution, since ADR 0003 makes the Envelope a ring of typed edges and every
solver timing on the map was measured at 100% exterior exposure.

**It can, and it does.** 11,997 floors carry two or more residential apartments.
Measuring per dwelling what fraction of its Envelope perimeter faces neither
another apartment nor a communal area — 150 sampled floors, 569 dwellings,
`experiments/corpus-smoke/exposure_swiss_dwellings.py`:

| | exterior fraction of perimeter |
|---|---|
| p5 | 0.16 |
| p25 | 0.23 |
| **median** | **0.37** |
| p75 | 0.47 |
| p95 | 0.59 |
| **≥0.99 — what every timing on this map assumed** | **0 of 569 (0.0%)** |

Not one real flat in the sample resembles the fully-exposed geometry the
6.25 s-at-24-rooms figure was measured against. The dwelling-type presets are
well-chosen but should now be fitted rather than guessed: `flat_single_aspect`
at a quarter sits near the measured **p25 of 0.23**, and `terrace_mid` at a half
sits near the **p75 of 0.47**. Nine dwellings scored ~0.00 exterior — genuinely
windowless units, which would fail acceptance rule H8 outright and are worth
inspecting before they are treated as noise.

Appended to *Solver timing variance sweep*, which owns the sweep itself.

### 1.6 Loader smoke test

`experiments/corpus-smoke/smoke_swiss_dwellings.py` — streams `geometries.csv` in
chunks with pandas, prints entity/subtype distributions, dwelling counts under all
four keys, and the four histograms. Runs in ~2 minutes. Geometry is **WKT in
metres** in a site-local coordinate system, per the deposit documentation and
confirmed on load.

---

## 2. ResPlan 17k — acquired

### 2.1 Where it is

| | |
|---|---|
| Source | <https://github.com/m-agour/ResPlan>, file `ResPlan.zip` on `main` |
| Paper | arXiv [2508.14006](https://arxiv.org/abs/2508.14006) — still a preprint; the repo withholds citation details pending peer review |
| On disk | `data/corpora/resplan/` — zip, extracted `ResPlan.pkl`, plus `LICENSE`, `README.md`, `TAKEDOWN.md`, `split.json`, `croissant.json`, `resplan_utils.py`, `requirements.txt` |
| `ResPlan.zip` | **100,106,537 bytes**, sha256 `f718de8865e51bbe93b49b584798e3c536ed6b4b8a5d32f01b56812f389aeb46` |
| `ResPlan.pkl` | **258,453,658 bytes**, sha256 `103edd854a5f365aa875ed832e6cef0d8bc72c4b34e5df0856c01b6970684cb5` |
| Total on disk | 343 MB |

**The GitHub *release* asset is a different file from the one on `main`**: release
`1.0.0` (2025-08-26) ships `ResPlan.zip` at **100,583,052 bytes** against `main`'s
100,106,537. The `main` copy was taken, being the newer of the two (last push
2026-07-28) and the one the takedown policy implies is current. The discrepancy is
unexplained by anything in the repo and is recorded here rather than resolved.

### 2.2 Licence — verbatim, dual, and unusually candid

Verified from the raw file, not the badge. `data/corpora/resplan/LICENSE` is a
dual licence:

- **DATA** — `ResPlan.pkl`, `split.json`, `croissant.json`: **CC BY 4.0**.
- **CODE** — `resplan_utils.py`, `ResPlan_demo.ipynb`, `baselines/`: **MIT**,
  "Copyright (c) 2025 The ResPlan Authors".

GitHub's auto-detector reports `NOASSERTION` for the repo purely because the file
is a composite; the text itself is unambiguous. The scope clause, verbatim:

> This licence is granted over the contributions the authors hold rights in: the
> annotations, the semantic taxonomy, the room-connectivity graph construction, the
> metric-scale conversion, the curation and filtering decisions, and the canonical
> splits.
>
> The underlying spatial arrangement of a building is a matter of fact rather than
> creative expression, and facts are not subject to copyright. No licence is
> therefore asserted, required, or granted over the spatial arrangements
> themselves.

Provenance is a computer-vision derivation from real-estate listing renderings
with the source platforms withheld. Under **C9 this is not a gate** — the project
is non-commercial and licence is explicitly not the filter. Recorded for accuracy,
not as a blocker.

**`REMOVED.md` does not exist — verified, HTTP 404.** Both the licence and
`TAKEDOWN.md` promise that removed plan identifiers are recorded so downstream
users can update their splits. Either no takedown has occurred, or the promise is
unhonoured; there is no way to tell from outside. It matters only if a future
release silently drops ids we have trained on.

**Attribution string:**

> ResPlan: A Large-Scale Vector-Graph Dataset of 17,000 Residential Floor Plans —
> Mohamed Abouagour and Eleftherios Garyfallidis. arXiv:2508.14006.
> Dataset licensed under CC BY 4.0; utilities under MIT.

### 2.3 Counts as loaded, against the published figures

Every published figure checked reconciles, one of them exactly:

| Quantity | Published | Measured | |
|---|---:|---:|---|
| total plans | 17,000 | 17,000 | ✓ |
| splits | 13,053 / 1,632 / 1,632 (+683 aug) | identical, and they **sum to 17,000** | ✓ |
| room polygons | 137,131 | **137,131** | ✓ exact |
| rectangular share | 43.2% | **53.9% exact / 62.1% at 2% tolerance** | ⚠️ see below |
| avg functional rooms | 8.1 | 8.07 | ✓ |
| median floor area | 110 m² | 109.6 m² | ✓ |
| median wall thickness | 21 cm | 22.6 cm | ✓ |

The exact match on 137,131 also **defines what the paper means by a functional
room**: five classes — `living`, `kitchen`, `bedroom`, `bathroom`, `balcony`.
Counting all eight classes present gives 138,336, and the difference of 1,205 is
exactly `garden` 853 + `parking` 351 + `pool` 1.

**Correction, from *Rectangularising real rooms*.** The line that used to stand
here — "the published 43.2% likewise means *exactly* rectangular" — is wrong, and
so is the 42.1% in the table above. Re-run over all 137,131 polygons:

| definition | share |
|---|---:|
| **exactly four exterior vertices** | **43.18 %** |
| area equal to bounding-box area, float equality | 51.32 % |
| **area equal to bounding-box area, 1e-9** | **53.88 %** |
| within 2 % of bounding-box area | 62.11 % |

The 2 % figure reproduces the paper (62.3 %) and the original probe (62.5 % on
its first 2,000 plans). The *exact* figure does not, under any area-based
definition — but **43.18 % of polygons have four vertices**, which lands on the
paper's 43.2 %. So the paper's "exactly rectangular" is a statement about
**storage**, not shape: 10.7 % of ResPlan's rooms are rectangles written down with
redundant collinear vertices. Every use of 43.2 % as a shape figure — this table,
`docs/spec/proposer.md` §4.4, and the map — was pessimistic by that margin.

The splits are worth stating plainly because the map has carried them wrong: the
683 augmented plans are **inside** the 17,000, not additional to it. Usable
non-augmented plans are **16,317**.

### 2.4 Three corrections to the map's existing record

- **The per-plan key list on the map is wrong on three of its entries.**
  `storage`, `stair` and `area_change_sqft` **do not exist**. The 19 actual keys
  are: `id`, `land`, `inner`, `wall`, `wall_depth`, `front_door`, `door`,
  `window`, `living`, `kitchen`, `bedroom`, `bathroom`, `balcony`, `garden`,
  `parking`, `pool`, `neighbor`, `area`, `net_area`.
- **The geometry is not in metres, and the README's claim that it is should not be
  relied on.** README bullet: *"Metric-scale coordinates in metres"*. Measured:
  polygons live on a ~256-unit canvas whose scale **varies per plan** — median
  0.0545 m/unit, range 0.0014 to 0.1667, and only **3.6% of plans** sit within 1%
  of the median. The authors' own `resplan_utils.py` contains no metric conversion
  and its comments speak of "a 256-unit canvas" and plans at "different coordinate
  scales". The only metric anchors are the scalar `area` and `net_area` fields, so
  **metres per unit must be recovered per plan** as `sqrt(area / polygon_area)`.
  This bites directly on *Proposer architecture survey*'s per-room target-area
  conditioning, which is metric by definition.
- **Seven plans carry a square-feet unit bug in `area`.** Ids 5981–5985 report
  areas of 0.0929, 0.1858, 0.2787, 0.3716 and 0.4645 m² — which are **exactly 1,
  2, 3, 4 and 5 square feet** — while their `net_area` is a sane 98–137 m². Plan
  5227 reports `net_area` of 0.0. One augmented plan, 855303, is a duplicate of the
  broken 5985. Ten plans in total sit below 30 m². Trivial to filter and
  catastrophic not to: a loss conditioned on target area would be poisoned by them.

### 2.5 Loader smoke tests

- `experiments/corpus-smoke/smoke_resplan.py` — loads the pickle **through a
  restricted unpickler that whitelists globals**, so a third-party pickle cannot
  execute arbitrary code on load. The only globals it in fact references are
  `shapely.io.from_wkb`, `numpy.dtype` and `numpy._core.multiarray.scalar` — which
  independently confirms the prior opcode-scan finding. Prints per-plan keys, one
  plan's room types and bounds, and the split sizes.
- `experiments/corpus-smoke/resplan_probe.py` — corpus-wide counts, unit scale,
  wall thickness and rectangularity. **Count rooms via `.geoms`**: a class key
  holds a MultiPolygon when a plan has several rooms of that type, so `len()` on it
  silently undercounts — it gives a mean of 4.96 against the true 8.14.

---

## 3. RPLAN — not acquired; needs a human

**Access is a Google Form, not a download link**, and the form presumes an
academic requester: name, position, **principal investigator's name**, and
affiliation. Verified live on 2026-08-19 — the form still returns HTTP 200 at

<https://docs.google.com/forms/d/e/1FAIpQLSfwteilXzURRKDI5QopWCyOGkeb_CFFbRwtQ0SOPhEg0KGSfw/viewform>

Under **C9 the terms are acceptable** — non-commercial research use is exactly what
this project is, and clause 7's reach into a for-profit employer does not bite on a
non-commercial project. Licence is not the obstacle. The obstacle is that someone
has to sign it.

### Checklist, if it is judged worth doing

1. Open the form above. Supply name, position, PI name, affiliation.
2. Agree to the terms — non-commercial research and educational use only; no
   redistribution in any format; new access only through the form.
3. Record here **what was signed, by whom, and on what date**, plus the reply
   address the download link arrives at.
4. On arrival: land it in `data/corpora/rplan/`, checksum it, and **do not commit
   it or any derivative** — clause 2 forbids redistribution, which includes
   pushing a preprocessed copy to a public repo.

### The evidence now says don't bother yet

RPLAN's **maximum is 8 rooms**. The regime this project is short of is ≥16, and
the corpora already on disk hold 63,800 dwellings averaging 6.8 rooms. RPLAN adds
volume exclusively in the band that is already saturated, contributes nothing to
the tail that decides the proposer question, and is raster-only so its vectors
must be derived. *Cross-dataset unification* had already demoted it to optional
pre-training that must earn its place on an ablation. Section 0 above weakens that
further: the only useful ≥16-room data is synthetic, and RPLAN is not synthetic.

**Recommendation: leave unacquired until an ablation in *What the model proposes,
and how it is trained* actually calls for raster pre-training volume.** Signing a
non-redistribution agreement is not free, and nothing on the map currently needs
what it buys.

---

## 4. MSD and ProcTHOR-10k — deliberately not acquired

Both are listed in the ticket, and **both were ruled out of the training set by
*Cross-dataset unification* after this ticket was written**:

| Corpus | Ruling | Why |
|---|---|---|
| MSD | Not training data | "a strict subset of Swiss Dwellings, filtered away by C5" — multi-apartment buildings |
| ProcTHOR-10k | "Take the generator idea, not the dataset" | synthetic; the idea is wanted, the 10k plans are not |

Downloading them would cost ~10.5 GB to acquire corpora the map has already
rejected. Their access facts are recorded instead, so either can be fetched in
minutes if a later ticket reopens the question:

- **MSD** — two releases with **different licences**. Take the
  [4TU record `e1d89cb5-6872-48fc-be63-aadd687ee6f9`](https://data.4tu.nl/datasets/e1d89cb5-6872-48fc-be63-aadd687ee6f9)
  (2023 challenge set, 4,167 train plans, 5.54 GB, **CC BY 4.0**) over the
  [Kaggle ECCV-2024 set](https://www.kaggle.com/datasets/caspervanengelenburg/modified-swiss-dwellings)
  (5,372 plans / 18,943 apartments, 4,996,692,802 bytes, **CC BY-SA 4.0** —
  copyleft). The repo *code* is unlicensed. Note the 4TU JSON API did not resolve
  the record by DOI on 2026-08-19 (returned `[]`); the landing page is the route in.
- **ProcTHOR-10k** — `allenai/procthor-10k`, **Apache 2.0**, re-verified from the
  raw `LICENSE` on 2026-08-19. Zero provenance risk.

ProcTHOR's *generator* becomes more interesting, not less, in light of section 0:
it is the published precedent for exactly the synthetic corpus that is now the only
possible source of ≥16-room training data.

---

## 5. What this hands to other tickets

- ***What the model proposes, and how it is trained*** — unblocked, and its
  central decision is materially changed. §7.3(a)'s data half **fires**: 66 against
  a threshold of 1,000. It must now either show synthetic pre-training closes the
  ≥16-room gap, or take the runner-up. It also inherits a concrete task the survey
  could not state: **specify the synthetic generator**, since no legally obtainable
  real corpus reaches the regime.
- ***Solver timing variance sweep*** — its exposure axis now has measured numbers
  instead of assumed presets: median 0.37 exterior, p25 0.23, p75 0.47, and
  **0 of 569 real dwellings above 0.99**.
- ***Fit the ENGINE_CHOICE acceptance thresholds to the corpora*** — its data is on
  disk with a verified loader, and it should fit against the **interior-room**
  filter defined in §1.3, not raw area counts.
- **A product question this ticket cannot settle.** The engine's headline capacity
  — 24 rooms — describes one dwelling in 63,800. Whether that capacity is worth
  holding as a v1 requirement, or whether the real target is the 4–10 room band
  where 95% of the corpus lives, belongs with the variant-and-scope economics.

## 6. What this note does not establish

- **`simulations.csv` was never opened.** 1.6 GB of daylight, viewshed, noise and
  centrality results. If any acceptance rule ever wants a real daylight figure,
  it is there and unexamined.
- **The exposure measurement is a 150-floor sample, not the corpus.** 569
  dwellings of 46,800. The distribution is stable enough to quote to two decimals
  but has not been run at scale, and the party threshold of 0.45 m is a judgement
  rather than a fitted value.
- **The "rooms ~370,000" published figure was never reconciled** under any filter
  tried. Every other Swiss Dwellings count matched to within 0.5%.
- **No plan from either corpus has been rendered or eyeballed.** Everything here is
  counts, bounds and checksums. Geometric validity — self-intersections, degenerate
  polygons, whether rooms actually tile their envelope — is unmeasured, and *Fit
  the ENGINE_CHOICE acceptance thresholds to the corpora* will hit it first.
