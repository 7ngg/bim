---
id: 12
title: Acquire the datasets
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
blocked_by: []
---

# Acquire the datasets

## Question

Nothing to decide — but training and schema work is blocked until the corpora are
on disk and their access terms are recorded. Mostly AFK; the parts needing a human
signature or an application form get handed over as a checklist.

Obtain and verify:

1. **Swiss Dwellings v3.0.0** — Zenodo record `10.5281/zenodo.7788422`, one
   ~932 MB zip of CSVs. CC BY 4.0. Direct download, no application.
2. **ResPlan** — from its published repository. Data CC BY 4.0, code MIT.
3. **RPLAN** — usable under C9, but access is granted by application rather than
   direct download. If a form or email is required, that part is the human's.
   Record what was signed and by whom.
4. **MSD** — Kaggle (CC BY-SA 4.0) and 4TU (CC BY 4.0) releases differ in licence.
   Take the 4TU one; note the repo *code* is unlicensed.
5. **ProcTHOR-10k** — Apache 2.0, synthetic, for pre-training augmentation.

For each, record in a findings doc:

- Where it now lives on disk, its size, and its checksum.
- The **verbatim licence text** from the raw file, not the badge. The research
  pass found three of the most-starred repos in this field would pass an automated
  licence check and are actually research-only.
- Attribution string required by CC BY, so it can be pasted into the eventual
  product credits.
- Row/plan counts as actually loaded, checked against the published figures — a
  mismatch is a signal worth catching now.
- A single-file loader smoke test per corpus: open it, parse one plan, print its
  room types and geometry bounds.

Deliverable: the data on disk, plus `docs/research/dataset-inventory.md`
recording all of the above.

## Resolution

**Two corpora on disk and verified; two deliberately not acquired; one waiting on
a human — and the blocking histogram answered against the recommendation.**

Full inventory: [`docs/research/dataset-inventory.md`](../../research/dataset-inventory.md).
Loaders: `experiments/corpus-smoke/`. Data lives in `data/corpora/`, gitignored.

### The blocking query, and it fires

*Proposer architecture survey* §7.3(a) made this ticket's histogram the test
between its recommendation and its runner-up: **retrieval-and-warp wins outright
if fewer than ~1,000 C5-surviving dwellings hold ≥16 areas** (and synthetic
pre-training does not close the gap). Counting the rooms a Brief actually names:

| Corpus | dwellings | mean rooms | ≥14 | **≥16** | ≥20 | ≥24 |
|---|---:|---:|---:|---:|---:|---:|
| Swiss Dwellings | 46,800 | 6.82 | 164 | **66** | 11 | 1 |
| ResPlan | 17,000 | 6.79 | 14 | **0** | 0 | 0 |
| combined | 63,800 | — | 178 | **66** | 11 | 1 |

**66 against a threshold of 1,000.** The 24-room case the solver study is built
around has **exactly one** analogue in 63,800 real dwellings, and none at all
counted by habitable rooms. Only the *data* half of §7.3(a) is settled — whether
synthetic pre-training closes the gap belongs to *What the model proposes*. But
the corpus side is now closed with a hard number, and it closes the map's old
*"whether the proposer is worth training at all"* question with evidence rather
than a shrug.

**The stronger version of the finding:** RPLAN's maximum is 8 rooms and MSD is a
subset of Swiss Dwellings, so **no legally obtainable real corpus reaches the ≥16
regime**. A synthetic generator is not the recommended first stage any more — it
is the only possible source of training data in the band that decides the product.

### Ticket 18's SQL is wrong three ways, and the gap is the finding

Run literally it returns **1,563**, not 66. The difference is not a rounding
argument:

1. **It counts every `entity_type='area'`.** Swiss Dwellings holds **72,255
   residential SHAFTs** — shafts outnumber bathrooms — plus 43,084 balconies. A
   shaft is not a room a Homeowner asks for, and the map's own *Structural and
   services reality* patch holds risers as unspecified for v1.
2. **It groups by `(site_id, apartment_id)` while its own comment says "single
   floor".** 1,672 `apartment_id`s span more than one `floor_id`, so it merges
   floors into fake oversized dwellings — its largest holds **690 areas**.
3. **`d41d8cd98f00b204e9800998ecf8427e` is `md5("")`** — 5,091 rows of
   unattributed areas that group into non-existent 74-, 37- and 34-room dwellings
   sitting at the top of the histogram.

Corrected query in §1.3 of the inventory. The filtered mean of **6.82
independently corroborates Ospici's separately-measured 6.20**, which the
unfiltered 9.44 does not — that agreement is why the filtered number is the one
to quote.

### Acquired

- **Swiss Dwellings v3.0.0** — 931,868,205 bytes, **md5 matches the publisher's
  exactly**. Every published count reconciles (separators 1,700,813 vs ~1.7 M;
  openings 714,936 vs ~715,000; areas 522,183 vs ~520,000; features 317,973 vs
  ~315,000) **except the apartment count** — 45,176 published against 46,800
  measured, because the key is ambiguous three ways. `simulations.csv` (1.6 GB of
  daylight and noise sims) left unextracted; nothing consumes it.
- **ResPlan 17k** — every published figure reconciles, one **exactly**: 137,131
  room polygons. That exact match also *defines* "functional room" as their five
  indoor classes, and shows "43.2% rectangular" means exactly rectangular (42.1%
  measured; 62.3% at a 2% tolerance).

### Licences, verified from source rather than badge

- **ResPlan** — verbatim dual licence checked in: **CC BY 4.0 data / MIT code**.
  Its promised `REMOVED.md` takedown ledger **does not exist (HTTP 404)**.
- **Swiss Dwellings** — **there is no licence file at all.** The zip holds four
  CSVs and nothing else; CC BY 4.0 exists only as Zenodo deposit metadata
  (`"license": {"id": "cc-by-4.0"}`, `rights: null`). Authoritative, but nothing
  travels with the files. Provenance is the strongest here — a named corporate
  rights-holder, Archilyse AG, with a stated manual Q/A to ≤5% area deviation.
- Attribution strings for both in the inventory, ready to paste into credits.

### Three corrections to what the map already recorded about ResPlan

- **Its geometry is not in metres**, despite the README's *"Metric-scale
  coordinates in metres"*. Polygons sit on a ~256-unit canvas whose scale **varies
  per plan** — median 0.0545 m/unit, range 0.0014–0.1667, only 3.6% within 1% of
  the median — and the authors' own utils contain no conversion. Scale must be
  recovered per plan as `sqrt(area / polygon_area)`. This bites *Proposer
  architecture survey*'s per-room target-area conditioning directly.
- **`storage`, `stair` and `area_change_sqft` do not exist** as per-plan keys.
- **Seven plans carry a square-feet unit bug**: ids 5981–5985 report areas that
  are exactly 1–5 **square feet** while their `net_area` is a sane 98–137 m².
  Filter before training or an area-conditioned loss is poisoned.

Also: the 683 augmented plans are **inside** the 17,000, not additional. Usable
non-augmented plans are **16,317**.

### Exposure — confirmed, and every timing on this map describes a house nobody lives in

*Building scope and envelope handling* asked this ticket to confirm the corpus can
supply the real exterior/party distribution. **It can.** 11,997 floors carry ≥2
apartments. Over 569 dwellings on 150 sampled floors:

| p5 | p25 | median | p75 | p95 | ≥0.99 |
|---:|---:|---:|---:|---:|---:|
| 0.16 | 0.23 | **0.37** | 0.47 | 0.59 | **0 of 569** |

Not one real flat resembles the 100%-exposed geometry behind 6.25 s at 24 rooms.
The presets can now be fitted rather than guessed — `flat_single_aspect` sits near
p25, `terrace_mid` near p75. Appended to *Solver timing variance sweep*.

### Not acquired, on purpose

- **MSD** and **ProcTHOR-10k** — ruled out of the training set by *Cross-dataset
  unification* **after this ticket was written** (MSD "a strict subset of Swiss
  Dwellings, filtered away by C5"; ProcTHOR "take the generator idea, not the
  dataset"). ~10.5 GB not spent on corpora the map has already rejected; access
  facts and the CC BY 4.0 / CC BY-SA 4.0 split recorded so either is minutes away
  if reopened.
- **RPLAN** — the one genuinely HITL item. Access is a Google Form presuming an
  academic requester (**live, HTTP 200, checked 2026-08-19**); under C9 the
  non-commercial terms are acceptable, so the obstacle is a signature, not a
  licence. Checklist in §3 of the inventory. **Recommendation: don't sign it yet.**
  RPLAN's maximum is 8 rooms, so it adds volume only in the band already saturated
  by 63,800 dwellings and contributes nothing to the tail that decides the proposer
  question.

### Honest limits

- The exposure figure is a **150-floor sample**, and the 0.45 m party threshold is
  a judgement, not a fitted value.
- **`simulations.csv` never opened**; the published **~370,000 rooms** figure never
  reconciled under any filter tried.
- **No plan has been rendered or eyeballed.** Geometric validity — self-intersections,
  degenerate polygons, whether rooms tile their envelope — is unmeasured, and *Fit
  the ENGINE_CHOICE acceptance thresholds to the corpora* will hit it first.
