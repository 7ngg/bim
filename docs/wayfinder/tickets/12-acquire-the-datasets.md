---
id: 12
title: Acquire the datasets
parent: map
labels: [wayfinder:task]
status: open
assignee:
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
