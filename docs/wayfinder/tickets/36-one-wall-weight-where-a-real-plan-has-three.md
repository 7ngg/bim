---
id: 36
title: One wall weight where a real plan draws three
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - docs/adr/ (new ADR)
  - the consequences route to the owners of annotation.md, acceptance-bar.md
    and the Homeowner surface — see "What this ticket does NOT write"
---

# One wall weight where a real plan draws three

## Question

Surfaced by *One internal thickness, against a corpus that has no module at all*,
which was sent to ask whether one `t_int` is defensible. **It is** — the shipped
150 mm lands **4 mm** from the corpus-optimal single value of 146, area drift
straddles zero, and the single-`t_int` conclusion survives. So this is not that
question. It is the one that measurement left behind:

> **A uniform internal thickness draws two wall weights. 76.1% of real dwellings
> draw three** — envelope, internal bearing wall, partition.

The failure mode is **not** the one the map has been guarding against. A plan with
one partition weight does not read as *generated*. It reads as **drawn by someone
who does not distinguish a partition from a bearing wall** — which is worse,
because it is a competence signal rather than a novelty signal, it is invisible to
the Homeowner it is sold to, and it is the first thing the Practitioner in C2 sees.

Measured, `docs/research/single-internal-thickness.md` §2:

| | |
|---|---|
| dwellings with ≥2 internal thickness classes (±10 mm) | **93.0%** |
| dwellings showing three weights — envelope / bearing / partition | **76.1%** |
| dwellings with a *single* internal thickness | **7.0%** |
| heaviest ÷ lightest internal class, median | **2.00×** |
| dwellings whose internal spread ≥ 50 mm — 1 mm of paper at 1:50 | **77.0%** |
| dwellings holding ≥1 m of internal wall ≥ 200 mm | 35.6% |

`out/compare.png` draws it three ways — as surveyed, uniform at the dwelling's
*own* median, uniform at 150 — which separates **uniformity** from **thickness**.
Look at it before deciding: the thickness is fine and the uniformity is the loss.

## Decide

The research priced three shapes. Pick one, or refuse all three and say what the
product says instead.

**A — Accept it.** One weight, and the product copy says the engine does not
distinguish load-bearing from partition, alongside the C5 and C8 statements it
already makes. Costs nothing to build. The honest version of this is not silence:
`Wall.load_bearing` is already *unknown, not false*, and this would make that
admission visible on the drawing rather than only in the model.

**B — Solve thick, draw thin.** Dilate the solve domain by `t_max/2` uniformly so
every tiling edge is still a centreline and the tiling still closes, then draw
selected partitions at 150 against a bearing wall at 280. ADR 0001's uniformity
survives exactly where it is load-bearing — the solve — and the drawing gets two
internal weights. Priced, and not free:

- **19 of 36 ergonomic room-axes need one more 250 mm solve cell** at 280 than at
  150 (253 → 272 cells; +132 mm per room-axis). ADR 0009 already found 250 mm
  charging the **5-room case**, the bottom of C13's band and the corpus's
  commonest size. This makes that worse in exactly that band. **Whether it makes
  it fatal is unmeasured** and needs a solver run.
- **A second bill, in area.** The delivered Σ Space area would exceed what the
  solve computed, by the thickness difference over every internal wall. So
  `area.invented_envelope_hard` stops reading the number the solve produced. That
  is a **hard rule to re-derive**, not a tolerance to widen.

**C — Two `t_int` in one Plan.** What actually buys the fidelity: measured,
**per-plan selection captures 1% of the available gain; 99% lives inside a single
dwelling.** It breaks **ADR 0001 consequence 5** and the **hard** validator rule
`model.space_matches_erosion`, and — this is the part the map had wrong — **ADR
0009 does not make it cheaper.** ADR 0009 cheapens the *per-Plan* purchase, whose
cost for `AZ` was already zero rows. Shape C's cost is a hard geometric invariant,
untouched.

## What is already settled and must not be re-litigated

- **The single `t_int` is not in question, and 150 is not in question.** Both were
  measured and both hold. This ticket is about how many weights are *drawn*, which
  is a separate axis from how many are *solved*.
- **`t_int_bearing` = 250 is `verified` and sitting unused** in the profile. It is
  the second weight shape B or C would draw. It exists already; nothing needs
  sourcing.
- **The old justification is dead.** *"A second `t_int` needs N copies of every
  dimensional minimum"* is false by count — `profiles.AZ` publishes **zero** linear
  minima. Do not reach for it; the argument that survives is ADR 0001, not ADR 0007.

## What this ticket does NOT write

It writes an ADR and nothing else. Whichever shape wins routes its consequences to
the tickets that own the files: **A** to the Homeowner surface and the product
copy; **B** and **C** to *The annotation spec is US-shaped* for the poché weights
and to whoever holds `acceptance-bar.md` for the re-derived area rule. Do not edit
those files from here — that is the collision the map's `writes:` rule exists to
stop, and it has already happened twice.

Deliverable: the shape, an ADR recording why the other two lost, and a named
hand-off per consequence.
