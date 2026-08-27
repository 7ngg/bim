# `experiments/void/` — the enclosed void a donor carries into retrieval

Ticket [53](../../docs/wayfinder/tickets/53-a-donors-enclosed-void-becomes-area-nobody-asked-for.md),
ADR [0028](../../docs/adr/0028-the-enclosed-void-is-charged-to-a-room-and-bounded.md).

**This directory imports `experiments/rectangularise/` and `experiments/warp/` and
edits neither**, the arrangement `envelope-exposure/` and `h8-frontage/` already
use against `solver-toy/`. Both of those directories are declared by open tickets
(46 and 57), so a probe that lived in either would have been a merge hazard for
work this ticket does not own.

## The quantity, and why it is not the one that was quoted

`rectangularise/void_census.py` measures uncovered floor against the **real
dwelling** — `uncovered ∧ inside the watershed's room labels`. The engine never
sees the real dwelling. It sees `parts[]`, so the quantity that decides anything
is the **enclosed complement of the parts frame**: a component of the bounding
box that no part covers and that touches no border.

That split already exists and is already committed —
`warp/absolute_area.py:notch_share` returns the boundary-touching share (the
[[Notch]], ADR 0020's `s`) and the enclosed share separately, and its docstring
says why: *"`uncovered` in a fit record sums the two together and that is why
nobody had noticed."* Everything here reads that function rather than
re-implementing the split.

⚠️ **Do not quote `void_census.py`'s 15.0 / 10.0 / 4.8 % as index figures.** They
are the first 400 records in file order, and the void has a strong room-count
gradient (0.55 % at four rooms, 15.79 % at ten), so a sample in file order
over-states by about half. The index figures are `parts_census.py`'s.

## The probes

| file | what it answers | cost |
|---|---|---|
| `parts_census.py` | the census over all 2,317 converted dwellings; the room-count gradient; whether worst-room IoU already sees it; the thinning factor a gate would cost | seconds |
| `can_the_warp_create_one.py` | can a clean donor acquire a void under the warp | ~1 min |
| `is_it_a_duct.py` | is the void a dropped `SHAFT`/`VOID`/`TECHNICAL_AREA`, or our own fit residue | ~3 min, re-parses the 1.09 GB geometry CSV |
| `provenance.py` | does the void have a clean donor owner, and does geometric absorption return it to that owner | ~2 min |
| `derivable_owner.py` | can the owner be derived from the Proposal alone — the question that decides whether a contract field is warranted | ~2 min |
| `absorb.py` | how much of the void can be closed at conversion by growing bordering parts | seconds |
| `treatment.py` | the four-arm sweep: void `free` / `weighted` / `charged` / `both` in the warp objective | ~6 min |

## What they found

- **15.49 %** of the index carries an enclosed void; ≥ 0.5 m² on **6.73 %**,
  ≥ 1 m² on 3.15 %, max 4.56 m². p50 is **0.00**.
- **The warp cannot create one** — 0 of 51 clean donors. A gap is ≥ 1 cell and the
  frame's incidence is fixed, so it is a pure donor property.
- **It is not a duct.** Only **1.4 %** of components and **2.0 %** of the void area
  lie majority-inside a dropped `NOT_A_ROOM` polygon. 98 % is rectangularisation
  residue — donor floor the k ≤ 2 fit could not cover.
- **The warp amplifies it 2.2×** at the shipped objective, because the void is in
  that objective at **weight zero**. Realised p90 **3.50 m²** against a donor p90
  of 1.31, max 13.1.
- **It has a clean owner** — watershed purity p50 **1.00**, ≥ 0.80 on 72.7 % of
  components — **and no derivable rule finds it**: largest shared edge agrees
  **28.4 %** of the time and ties in 28.4 % of components, largest bordering Room
  38.1 %, geometric absorption 24.1 %.
- **Charging it to a Room is what makes the number honest.** Worst-room deviation
  on voided candidates is p50 0.0652 measured on parts alone and **0.0959**
  measured on parts plus the void the Room is about to be handed.

## Traps

1. **Never quote a `void_census.py` figure beside a `parts_census.py` one.** They
   are different regions measured against different references. One is about the
   conversion's honesty, the other about what the engine is handed.
2. **`weighted` and `charged` are not alternatives and the sweep is easy to
   misread.** `charged` reports a *worse* deviation than `free` and it is not
   worse — it is the same warp measured against what the Room will actually hold.
   Reading that row as a regression is the mistake this table exists to prevent.
3. **`is_it_a_duct.py` re-parses the corpus CSV.** Everything else reads
   `rectangularise/out/swiss_fit_k2.json` and `out/swiss_dw.pkl`. If you add a
   statistic about the void, add its inputs to `parts_census.py`'s record —
   `acceptance-thresholds/`'s rule, and the reason a new percentile off this study
   costs seconds.
4. **The receiving Room in `treatment.py` is the derivable fallback**, largest
   shared edge, because the rig has no index. The **engine** uses the donor's
   recorded owner and falls back to this. Do not read the rig's arm as the
   engine's fidelity.
