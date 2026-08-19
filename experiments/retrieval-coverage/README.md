# Retrieval coverage over Swiss Dwellings

Ticket 08, *What the model proposes, and how it is trained*. Answers whether
retrieval-and-warp can serve a Brief at all, and at what room counts.

Needs `data/corpora/swiss-dwellings/swiss-dwellings-v3.0.0/geometries.csv`
(1.09 GB, acquired per `docs/research/dataset-inventory.md`). `pandas`, `shapely`,
`numpy`. Seed 20260819 where randomness is used.

```
python experiments/retrieval-coverage/multiset_coverage.py   # pass 1: room multisets
python experiments/retrieval-coverage/joint_coverage.py      # pass 2: + envelope, self-paired
python experiments/retrieval-coverage/cross_coverage.py      # pass 3: + envelope, cross-paired
python experiments/retrieval-coverage/room_label_probe.py    # is generic ROOM usable?
python experiments/retrieval-coverage/collapsed_coverage.py  # pass 3 in Brief vocabulary
```

Pass 3 writes `out/dwelling_records.json`; `collapsed_coverage.py` reads that
cache, so run pass 3 first or it re-reads the 1 GB file.

## What each pass adds, and why the last one is the answer

| pass | question | why it is not the answer |
|---|---|---|
| 1 | does a corpus dwelling share the Brief's room multiset? | ignores that the plan must fit an Envelope |
| 2 | ...and match its size and proportion? | asks each dwelling for peers matching **its own** envelope — in the corpus the programme and the shape were designed together, which flatters retrieval |
| 3 | ...where the envelope came from a **different** dwelling of the same room count | counts `ROOM` and `BEDROOM` as different types, which splits a pool a Brief treats as one |
| label probe | is `ROOM` a bedroom or a grab bag? | — |
| collapsed | pass 3, in the vocabulary a Brief actually uses | **this is the answer** |

Tolerances throughout: room multiset exact, total floor area ±10 %, envelope
aspect ratio ±15 %. Those are the values `docs/spec/proposer.md` §2.2 adopts as
the warp budget — **stated, not fitted**.

Dwelling key is `(site_id, floor_id, apartment_id)` over `entity_type='area'` and
`unit_usage='RESIDENTIAL'`, excluding shafts, cores and outdoor areas, and
**dropping `apartment_id = md5("")`**. Without that drop the tail carries six
phantom 74-room dwellings; with it the room-count histogram reproduces *Acquire
the datasets* exactly — 46,800 dwellings, mean 6.82, 66 at ≥16, 1 at ≥24.

Envelope shape is the **minimum-area rotated rectangle** of the union of a
dwelling's rooms. Swiss Dwellings is geo-referenced, so an axis-aligned bounding
box would measure the site's north angle rather than the flat.

## Result

```
band     briefs   pool=0    pct   median   >=20
4-6      18,143    1,721   9.5%       92 12,785
7-10     24,785    3,074  12.4%       66 16,619
11-15     1,416      959  67.7%        0     78
16+          66       47  71.2%        0      0
```

Retrieval is viable in the common band and dead above ten rooms — which is why
`docs/spec/proposer.md` gives the Proposer two sources rather than one.
