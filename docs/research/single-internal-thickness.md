# One internal thickness, against a corpus that has no module at all

Findings for *One internal thickness, against a corpus that has no module at all*
(`docs/wayfinder/tickets/33-one-internal-thickness-against-a-corpus-with-none.md`).

Everything numeric here was measured on this machine on **2026-08-21** against the
corpora on disk under `data/corpora/`. Harness:
`experiments/thickness-fidelity/`, which is new and self-contained. Nothing in
`data/standards/room-constraints.json` was edited — the ticket declares itself
read-only on the profile and is.

---

## Headline

**One internal thickness is defensible for v1 — more comfortably than the ticket
expected — the shipped value is nearly optimal, and what it costs is the drawing,
not the areas.**

**What it costs, precisely.** A real dwelling carries a visible wall-weight
hierarchy: a heavy envelope, a medium internal bearing wall, a light partition.
**76.1 % of real dwellings show all three at 1:50.** A uniform `t_int` draws
**two**, always. Only **7.0 %** of real dwellings have a single internal thickness;
the modal dwelling has three, and its heaviest internal wall is a median **2.00×**
its lightest. So the plan does **not** read as generated — nothing about uniform
partitions does what a 2750 × 8250 bedroom does — but it reads as **drawn by
someone who does not distinguish a partition from a bearing wall**. That is a C2
failure against the Practitioner standard the engine is held to, and it is
invisible to the Homeowner it is sold to.

**What it does not cost: area.** Three independent estimators of the area drift at
`t_int` = 150 land at **−0.91 % / −0.46 % / +0.68 %** of Σ Space area. They
straddle zero. The drift the ticket went looking for was **real at 120**
(+0.22 % / +0.68 % / +1.81 %) and **ADR 0010 accidentally deleted it** while moving
`t_int` for an unrelated reason.

**The shipped value survives its sanity check with room to spare.** The
length-weighted L1-optimal *single* internal thickness over 411 km of Swiss
internal wall is **146 mm**. `AZ` ships **150**, derived from an Azerbaijani
half-brick plus an Azerbaijani plaster thickness with no corpus involved. Two
construction traditions, 4 mm apart.

**Three things the map records are wrong or stale, and one of them changes the
argument.**

1. **The corpus percentiles the ticket quotes are the wrong population.** p25 109 /
   p50 169 is *all walls*, and 70 % of the wall length this study classifies is
   not partition. Internal only:
   p25 **100**, p50 **131**, p75 **169**. `t_int` = 150 sits at about the **p60**,
   not "near the p25". §6.2.
2. **The residue-class argument that "forced" one `t_int` currently forbids
   nothing.** It survives ADR 0010 intact — checked, not assumed — but ADR 0009
   plus a profile publishing **zero** linear minima means a second `t_int` would
   duplicate **zero rows**. The constraint actually holding the decision up is
   **ADR 0001 consequence 5** and the hard validator rule
   `model.space_matches_erosion`, and neither the ticket nor the profile's
   ship-gate note mentions it. §4.1, §4.3, §6.5.
3. **ADR 0010's own "roughly 4–5 %" partition footprint is stale at the thickness
   ADR 0010 shipped.** Verified at 4.8 % for the corpus and 4.5 % at `t_int` = 120;
   measured **5.7 %** at 150. Quoted in two places. §6.4.

**A fourth, which cuts the other way and is easy to misuse.** The prior's
*"an 8-entry catalogue matches 58.5 % of real walls"* is measured on all walls.
On **internal** walls the same catalogue covers **74.7 %**, twelve entries cover
84.1 %, and twenty snapped values cover **91.5 %**. The *no-module* conclusion
still holds — the modal internal value holds 9.6 %, under a tenth — but the
corpus is materially more regular than the map records, and the sentence that
reads as the clincher understates it by 16 points. §6.1a says why this is a
qualification and not a reversal.

**And the cheapest fidelity gain is not the one ADR 0009 made free.** With the best
achievable pair of thicknesses available, choosing one **per Plan** — a second
construction type — captures **1 %** of the available gain. The remaining **99 %
lives inside a dwelling**, where a per-Plan choice cannot reach it. If the wall
hierarchy is ever worth buying, it has to be bought as two thicknesses *in one
plan*, and that is the purchase that breaks a hard rule. §4.5.

**Recommendation, for the session that resolves this ticket:** keep one `t_int`,
keep 150, and stop justifying it by the residue classes. Record the real
justification (ADR 0001 c5 + `model.space_matches_erosion`), record the cost in the
register it is actually paid in (**one of three wall weights, in three-quarters of
dwellings**), and hand the area-gate bias to *Fit the ENGINE_CHOICE acceptance
thresholds to the corpora* rather than absorbing it here.

---

## 0. Method, and the one thing it does differently from the prior

The prior this ticket rests on is *Which region profiles ship in v1*, measured by
`experiments/corpus-smoke/wall_thickness_swiss.py`: the minor side of the minimum
rotated rectangle of every `separator/WALL` polygon, over a 200,000-wall sample,
giving **p25 109 · p50 169 · p75 267** and *"no module at all"*.

**That statistic mixes internal and external walls.** A `separator/WALL` row is
any wall — a dwelling's exterior skin, its party wall to the neighbour, the
corridor wall to the common stair, and its bedroom partition, all in one
population. `t_int` is an *internal partition* thickness. Comparing 120 or 150 mm
against the p25 or p50 of that mixed population compares a partition against a
distribution 70 % of which, by wall length, is not partitions — measured below.

So this study measures the population the profile actually names. Per dwelling
`(floor_id, apartment_id)`:

1. take that dwelling's room polygons — Swiss Dwellings stores **clear**
   polygons, inner faces, and no two ever touch (`probe_swiss.py`);
2. take every WALL on the same floor, whatever `apartment_id` it carries (20.9 %
   carry none, and a party wall is exactly the kind that would not);
3. keep walls that are genuine straight strips, `area / mrr.area ≥ 0.95` — the
   same gate the prior census used, so the two are comparable;
4. probe **7 stations** along each wall's centreline, casting perpendicular both
   ways and taking the nearest room within 600 mm whose nearest point is within
   300 mm of being square to the wall;
5. a station is **internal** when both sides land on *different rooms of this
   dwelling*, **boundary** when only one side does. A wall is internal in
   proportion to its internal stations, and contributes that share of its length.

Two numbers come out of each internal station, and after ADR 0010 they are
different questions:

| | |
|---|---|
| `t_mrr` | minor side of the wall polygon's own minimum rotated rectangle — what the surveyor drew as the wall body |
| `gap` | centreline-to-room-A plus centreline-to-room-B — the **face-to-face separation of two Spaces**, which is by construction the plane ADR 0010 puts our `t_int` **total** on |

Three independent estimators of the same drift are reported throughout, because
they fail in different directions and agreement is the only evidence available
that any of them is right: the per-wall `gap` sum, a morphological-closing area
estimate that also counts junction material, and a per-wall `t_mrr` sum that is
immune to a probe reaching past the wall into a duct.

**The classifier was checked by drawing it, not by trusting it.**
`classify_check.py` renders each dwelling with everything the probe called
internal in **red** and everything it called boundary in black
(`out/classify.png`). Across the sampled dwellings inspected, no perimeter wall is
red and no partition is black. The failure mode that would have mattered — a
perimeter wall called internal at a corner, dragging the internal distribution
up toward the exterior one — does not appear. One dwelling's table, verbatim, as
the shape of the evidence:

```
=== 28127|42e7c5d7b53bbc91e8b452b2b4bf2e1a   rooms=6  sum_area=75.0 m2
    INTERNAL  t_mrr 226  gap 228  len 5.94     <- the spine
    INTERNAL  t_mrr 174..182 (x4)              <- the ordinary partitions
    INTERNAL  t_mrr  80  gap 382  len 0.98     <- a stub, and a contaminated gap
    boundary  t_mrr 437, 437, 437, 479, 479, 373
```

**The `gap` estimator has a contaminated tail and it is visible in that table.**
An 80 mm wall reporting a 382 mm gap is a probe that crossed the wall, a void and
something else before finding the far room. For the *drift* question that is
arguably the right number — our engine puts exactly one 150 mm partition between
any two adjacent Spaces, whatever the real dwelling put there — but it is not a
wall thickness, and it can double-count length when two parallel walls both see
the same room pair. This is why three estimators are reported and why the
area-based one, which cannot double-count, is the arbiter for §3.

**Sample.** A deterministic 1-in-10 **floor** sample of `geometries.csv`, unioned
with every floor `experiments/rectangularise/out/swiss_fit.json` already fitted so
item 4 can join against ADR 0008 convert/drop status on the same dwellings.
`extract.py` read **3,255,905 rows**, which independently reproduces
`dataset-inventory.md` §1.3's row count exactly, and kept **3,507 of 13,905
floors** holding **14,857 residential dwellings**. `measure.py` measured
**14,691** of them (166 skipped, one geometry repair in the whole run), and the
analysis is restricted to the **14,063** inside C13's 4–10-room band that carry at
least 3 m of internal wall.

That is **190,181 internal wall runs, 411.4 km**, against **324,557 boundary runs,
957.2 km** — **70 % of the classified wall length is not partition**, which is the
size of the substitution §6.2 objects to. (A run is a wall seen from one dwelling;
a wall between two apartments is examined once from each, so these counts are not
a partition of the raw polygon count and are not used as one.) Of
3,603,166 probe stations, 29.3 % are internal, 57.0 % boundary and **13.8 % find no
room on either side within 600 mm**. That last figure is the method's own error
bar: a void station discards a wall, and a wall too thick to reach across is more
likely to be discarded, so the internal distribution below is if anything biased
**thin**.

---

## 1. Which plane the corpus records — and the answer is "there is only one"

ADR 0010 made `t_int` a layer-set **total**, and the ticket's inherited section
flagged the consequence: if corpus thicknesses are **structural** and ours is a
**total**, every comparison below is off by 2 × `t_finish` = 30 mm. Which one the
corpus records was recorded as unknown.

It is neither, and the distinction does not exist in the file.

Over every internal probe station, `gap − t_mrr` — the distance between the two
Space polygons minus the thickness of the wall polygon between them:

```
(gap between the two Space polygons) - (wall polygon thickness), n=1,054,371 stations
   [ -inf ,   -5 )   0.64%
   [   -5 ,    5 )  73.17%
   [    5 ,   12 )   1.02%
   [   12 ,   20 )   0.77%
   [   20 ,   26 )   0.45%
   [   26 ,   36 )   0.63%
   [   36 ,   60 )   1.20%
   [   60 ,  inf )  22.12%
   median 2.0 mm   modal bucket [(np.int64(2), 763589), (np.int64(3), 3345), (np.int64(4), 2852), (np.int64(6), 2057)]
```

**The mode is exactly +2.0 mm and it holds about seven stations in ten.** A
corpus room polygon sits **1 mm off each face of its wall body**. There is no
render allowance, no second polygon, no offset: Swiss Dwellings draws one line
per face and the Space stops on it.

Two consequences.

1. **The `gap` is the right comparator for our `t_int` total, and no ±30 mm
   correction applies.** Whatever the Archilyse surveyor's line physically
   represents, it is *the plane that bounds the corpus's Space*, which is the same
   role ADR 0010 gives our innermost finish face. Comparing 150 against it is
   like-for-like in the only sense available.
2. **The corpus cannot arbitrate structural-versus-finished, because it does not
   model the distinction.** That is a negative result and it closes the question
   this ticket was handed rather than answering it. The residual — whether that
   single line is masonry or render — is unobtainable and is listed as such.

**Corroborated from the other side, independently.** *What an Azerbaijani finish
layer actually is* reached the same conclusion from the **schema**: 93 distinct
`(entity_type, entity_subtype)` pairs over the same 3,255,905 rows and *"not one
names a finish, render, plaster or layer"*. That is a different method — counting
type labels — on the same file. This section reaches it from the **geometry**.
Two methods, one answer.

---

## 2. Item 1 — does a dwelling drawn with one internal thickness read as real?

### 2.1 Real dwellings do not have one internal thickness. Nine in ten have two or more.

This is the ticket's first question and the answer is not close. A thickness
"class" below is seeded by the longest unassigned internal wall and absorbs every
wall within the stated tolerance; a class holding under 5 % of the dwelling's
internal wall length is folded away as construction noise rather than counted as a
design choice.

```
length-weighted INTERNAL wall thickness (t_mrr), mm:
   p5=66  p10=77  p25=100  p50=131  p75=169  p90=204  p95=230
length-weighted BOUNDARY wall thickness (exterior + party), mm:
   p5=102  p10=144  p25=190  p50=261  p75=340  p90=421  p95=482
distinct internal thickness classes per dwelling, tol +/- 5 mm
   1:  5.5%  2: 15.0%  3: 22.5%  4: 22.9%  5: 17.8%  6: 16.4%
   >= 2 classes: 94.5%
distinct internal thickness classes per dwelling, tol +/-10 mm
   1:  7.0%  2: 21.6%  3: 29.1%  4: 24.1%  5: 12.6%  6:  5.6%
   >= 2 classes: 93.0%
distinct internal thickness classes per dwelling, tol +/-20 mm
   1: 12.1%  2: 34.7%  3: 32.7%  4: 15.9%  5:  3.7%  6:  0.9%
   >= 2 classes: 87.9%
distinct internal thickness classes per dwelling, tol +/-40 mm
   1: 22.6%  2: 52.3%  3: 20.9%  4:  3.9%  5:  0.3%  6:  0.0%
   >= 2 classes: 77.4%
heaviest / lightest internal class in one dwelling (tol +/-10 mm):
   p10=1.17  p25=1.50  p50=2.00  p75=2.71  p90=3.76  p95=4.72
   dwellings whose heaviest internal wall is >= 1.25x its lightest: 85.6%
   dwellings whose heaviest internal wall is >= 1.50x its lightest: 75.7%
   dwellings whose heaviest internal wall is >= 2.00x its lightest: 53.3%
   dwellings whose heaviest internal wall is >= 2.50x its lightest: 32.3%
   absolute spread (mm): p25=51  p50=92  p75=130  p90=172
   dwellings whose internal spread is >= 50 mm -- 1 mm of paper at 1:50, the
   threshold at which two solid poche bands read as different walls: 77.0%
   >= 100 mm (2 mm of paper): 45.2%
visible wall-weight hierarchy at 1:50 (>= 50 mm = 1 mm of paper between bands):
   dwellings showing THREE weights -- envelope, internal bearing, partition: 76.1%
   dwellings showing only two:                                          23.9%
   a uniform t_int always draws exactly TWO.
internal wall LENGTH at >= 200 mm (a plausible internal bearing wall): 11.4%
internal wall LENGTH at >= 300 mm (implausible as a partition -- the classifier's
   own error bar): 1.5%
dwellings holding at least 1 m of internal wall >= 200 mm: 35.6%
```

**Only 7.0 % of real dwellings have a single internal thickness** at a ±10 mm
tolerance, and only 22.6 % at a generous ±40 mm. The modal dwelling carries
**three** classes. The heaviest internal wall in a dwelling is a median **2.00×**
its lightest, and **35.6 %** of dwellings hold at least a metre of internal wall at
200 mm or more — a wall that is not a partition.

**This is not the same finding as "the corpus has no module."** The corpus has no
module *across* dwellings — no shared catalogue, verified again at §6.1. What §2.1
adds is that it has no single thickness *within* one either. Those are independent
facts and only the second one bears on item 1.

**Where the shipped value sits, now that the population is the right one.**
`t_int` = 150 lands between the internal p50 (**131**) and p75 (**169**) — call it
the p60. It is *above* the internal median, not below it, and it is nowhere near
the p25 the ticket cites. §6.2.

### 2.2 What that costs the drawing, in millimetres of paper

`annotation.md` fills cut walls with **solid poché** at **1:50**. So a wall's
weight on the sheet is literally its thickness ÷ 50:

| | mm of wall | mm of paper at 1:50 |
|---|---:|---:|
| corpus internal, p25 | 100 | 2.0 |
| corpus internal, p50 | **131** | 2.6 |
| corpus internal, p75 | 169 | 3.4 |
| corpus internal, p90 | 204 | 4.1 |
| **shipped `t_int`** | **150** | **3.0** |
| a second `t_int` (250 + 2 × 15) | 280 | 5.6 |
| corpus boundary, p50 | 261 | 5.2 |
| `t_ext_total` | 500 | 10.0 |

The visible-difference threshold between two solid bands is about **1 mm of
paper**, which is **50 mm of wall**. Measured, **77.0 %** of real dwellings cross
that threshold *inside their own partition set*, and **45.2 %** cross 100 mm.

Put the two together and the cost has a name:

| | |
|---|---|
| real dwellings showing **three** distinct wall weights at 1:50 — envelope, internal bearing, partition | **76.1 %** |
| real dwellings showing only two | 23.9 % |
| what a uniform `t_int` draws, always | **two** |

**Three-quarters of real dwellings carry a wall-weight hierarchy that a uniform
`t_int` cannot draw.** That is the answer to "what does it cost the drawing", and
it is a number rather than an impression.

### 2.3 Drawn, three ways, so it can be looked at rather than argued about

`draw_compare.py` renders each dwelling three times: **as surveyed**, **uniform at
its own length-weighted median internal thickness**, and **uniform at
`t_int` = 150**. The middle panel exists to separate *uniformity* from
*thickness*, which are two different complaints and the ticket asks about the
first. `out/compare.png`; the classifier behind it is checked in
`out/classify.png`.

What is visible, stated as what it is — a reading, not a measurement:

- **The plan still reads as a plan.** Nothing about a uniform partition set makes
  a dwelling look generated the way a 2750 × 8250 bedroom does. Whatever `t_int`
  costs, it does not cost that.
- **What is lost is the third wall weight.** A real drawing carries a visible
  hierarchy: a heavy envelope, a medium internal bearing wall, a light partition.
  Uniform `t_int` collapses that to **two** — envelope and everything else. The
  spine that organises the plan stops announcing itself.
- **At 150 specifically, the drawing is unremarkable.** The five dwellings in
  `compare.png` have own-median internal thicknesses of 102, 120, 120, 141 and
  182 mm; 150 sits inside that range and the right-hand panel is neither
  conspicuously fat nor conspicuously thin. **The value is not the problem. The
  uniformity is.** That is why the middle panel exists — it looks nearly as wrong
  as the right one, and it is drawn at the dwelling's *own* thickness.

Who notices matters. C2's Homeowner *"cannot read a dimension string"* and will
not notice a missing wall-weight hierarchy. A Practitioner will, because the
hierarchy is how a plan is read at a glance. So the honest verdict on item 1 is
**not** "it reads as generated": it is **"it reads as a plan drawn by someone who
does not distinguish a partition from a bearing wall"** — which is a C2 failure
against the standard the engine is held to, and invisible to the audience it is
sold to.

---

## 3. Item 2 — does area drift systematically?

ADR 0001 re-derives every clear rect as `erode(solved, t_int/2)`, and
`proposer.md` §2.2 spells out the mechanism precisely: *"the converted room is a
centreline rectangle… a converted room's area includes half of every wall around
it. Per ADR 0001 the clear rectangle is that eroded by `t_int/2`."* So a real
dwelling's rooms, re-drawn by us, gain or lose `(real separation − 150)/2` on
every internal side.

Three estimators, because they fail differently:

```
t_int = 120 mm  (pre-ADR-0010)
   drift per dwelling, % of Sum(Space area)   [+ = our rooms bigger than the corpus's]
      wall (gap)      p5=-0.7  p25=+0.5  p50=+1.5  p75=+2.7  p95=+5.2   mean +1.81%
      area (closing)  p5=-1.7  p25=-0.5  p50=+0.2  p75=+0.9  p95=+2.2   mean +0.22%
      body (t_mrr)    p5=-1.2  p25=-0.1  p50=+0.6  p75=+1.4  p95=+2.8   mean +0.68%
      dwellings drifting POSITIVE: 86.2% (wall)   70.8% (body)
   absolute, m^2 per dwelling: p5=-0.44  p25=+0.33  p50=+1.10  p75=+2.19  p95=+4.62   mean +1.477
t_int = 150 mm  (SHIPPED)
   drift per dwelling, % of Sum(Space area)   [+ = our rooms bigger than the corpus's]
      wall (gap)      p5=-1.8  p25=-0.5  p50=+0.4  p75=+1.6  p95=+4.0   mean +0.68%
      area (closing)  p5=-3.0  p25=-1.7  p50=-0.9  p75=-0.1  p95=+1.2   mean -0.91%
      body (t_mrr)    p5=-2.4  p25=-1.3  p50=-0.5  p75=+0.3  p95=+1.7   mean -0.46%
      dwellings drifting POSITIVE: 61.0% (wall)   33.9% (body)
   absolute, m^2 per dwelling: p5=-1.33  p25=-0.36  p50=+0.28  p75=+1.25  p95=+3.41   mean +0.599
t_int = 280 mm  (t_bearing+finish)
   drift per dwelling, % of Sum(Space area)   [+ = our rooms bigger than the corpus's]
      wall (gap)      p5=-7.3  p25=-5.7  p50=-4.4  p75=-2.9  p95=-0.8   mean -4.23%
      area (closing)  p5=-9.2  p25=-7.2  p50=-5.8  p75=-4.4  p95=-2.6   mean -5.82%
      body (t_mrr)    p5=-8.3  p25=-6.7  p50=-5.4  p75=-4.1  p95=-2.3   mean -5.37%
      dwellings drifting POSITIVE: 2.6% (wall)   0.2% (body)
   absolute, m^2 per dwelling: p5=-6.21  p25=-4.39  p50=-3.16  p75=-1.96  p95=-0.52   mean -3.203
```

### 3.1 The drift was real, and ADR 0010 accidentally deleted it

The ticket's item 2 says: *"A `t_int` at the corpus p25 makes our rooms
systematically **larger** than the same solved rect would give at the corpus
median."* That sentence was written about **120**, and about 120 it is **correct**:
all three estimators are positive there, at **+0.22 % / +0.68 % / +1.81 %**, and
between 71 % and 86 % of dwellings drift positive. The mechanism the ticket named
was really operating.

At the **150 that ADR 0010 shipped**, it is not. The three estimators land at
**−0.91 % / −0.46 % / +0.68 %** — they **straddle zero**, and the share of
dwellings drifting positive falls from 71–86 % to 34–61 %. **There is no defensible
systematic drift at the shipped value.** The most that can be said is that the
robust pair leans very slightly negative, by under one percent, inside the corpus's
own stated area accuracy.

**ADR 0010 did not know it was doing this.** It moved `t_int` for a reason that had
nothing to do with the corpus — a 1700 mm bath that did not fit inside its own
1700 mm minimum — and the same move took the area drift from clearly positive to
centred on nothing. That is luck, not design, and it should be recorded as luck: had
`t_finish` come back at 25 mm rather than 15, `t_int` would be 170 and the drift
would be as clearly negative as it was once positive.

The percentile clause in the ticket's sentence is separately wrong and stays wrong
at either thickness — neither 120 nor 150 is at the corpus p25 of *internal* walls
(p25 = 100). §6.2.

### 3.2 How much, against the rules that read this quantity

```
what the drift at t_int = 150 is worth against the rules that read Sum(Space area):
   wall (gap)       mean |drift| 0.68%  =  14% of the 5% hard gate, 34% of the 2% soft one
   area (closing)   mean |drift| 0.91%  =  18% of the 5% hard gate, 45% of the 2% soft one
   body (t_mrr)     mean |drift| 0.46%  =   9% of the 5% hard gate, 23% of the 2% soft one
```

The gates are `area.invented_envelope_hard` (5 %, hard) and `_soft` (2 %), both
`engine_choice` and both **unfitted**. Under a fifth of the hard gate, and the sign
is not consistent between estimators, so this is **not a systematic bias to correct
for** — it is a contribution to the spread the gate has to accommodate. That is a
weaker statement than "there is a bias", and it is the one the data supports.

**Per room it is a different story, and this is where the drift actually lives.**

| | mean drift at `t_int` = 150 |
|---|---:|
| per **dwelling** | −0.9 % … +0.7 % |
| per **room**, all types | **+1.54 %**, p5 −4.0 %, p95 **+13.3 %** |
| `BATHROOM`, n = 20,744 | **+5.06 %** |
| `STOREROOM`, n = 3,421 | +2.08 % |
| `KITCHEN`, n = 13,252 | +1.24 % |
| `BEDROOM` / `ROOM` | +0.12 % / +0.18 % |

A dwelling-level near-zero is hiding a strongly skewed per-room distribution: the
drift is a fixed millimetre change on a variable denominator, so the small rooms
wear it, and the small rooms are the wet rooms the ergonomic floors bind hardest
on. A bathroom drawn by us comes out about **5 % larger** than the same bathroom in
the corpus.

**The bathroom figure is the least reliable number in this document and is flagged
rather than featured.** The per-room allocation uses the `gap` estimator, whose
contaminated tail (§0) is concentrated exactly where service voids are — which is
around bathrooms. Read the sign and the ordering; do not quote the magnitude.

### 3.3 ADR 0010 moved this by more than a percentage point, and nobody measured it

| `t_int` | wall (gap) | area (closing) | body (`t_mrr`) | our partition footprint, % of Σ Space |
|---|---:|---:|---:|---:|
| 120 (pre-ADR-0010) | +1.81 % | +0.22 % | +0.68 % | 4.5 % |
| **150 (shipped)** | **+0.68 %** | **−0.91 %** | **−0.46 %** | **5.7 %** |
| 280 (a second `t_int`) | −4.23 % | −5.82 % | −5.37 % | 10.6 % |
| *the corpus's own partitions* | — | — | — | **4.8 %** |

Three readings, and the third is the one that travels furthest.

1. **ADR 0010 cost about 1.1 points of Σ Space area** on every estimator, in the
   same direction on all three. That is a real consequence of a decision taken for
   a different reason, and no line in ADR 0010 or `acceptance-bar.md` §8 predicts
   it.
2. **A second `t_int` at 280 would cost 4–6 points** — the width of the hard gate,
   spent on one construction decision. §4.4 prices the same choice in solve cells;
   this is the same choice priced in area, and the two agree that it is expensive.
3. **ADR 0010's own "roughly 4–5 %" partition footprint is verified for the corpus
   (4.8 %) and for the 120 it replaced (4.5 %), and understated for the 150 it
   shipped (5.7 %).** §6.4.

### 3.4 Robustness of the area-based estimator

The `area` estimator is the one doing most of the work above, and it rests on a
morphological closing at a chosen radius. Swept:

```
closing-radius sensitivity on the area-based partition footprint:
   r=0.25 m   t_eff median 120 mm   p25 101  p75 140
   r=0.35 m   t_eff median 125 mm   p25 106  p75 146
   r=0.5 m    t_eff median 128 mm   p25 109  p75 152
```

Doubling the radius moves the implied effective internal thickness by **8 mm** —
under a third of the difference between 120 and 150. The estimator is not the
free parameter. Non-room areas an apartment holds (shafts, stairs, balconies) are
subtracted before the closing, so they are not counted as partition; without that
subtraction the footprint would be overstated and the drift understated.

---

## 4. What a second thickness would actually buy

### 4.1 There are three purchases, and the ticket's re-pricing applies to the one nobody wants

The profile's own `ship_gates.adr_0007_single_t_int_decision` and
`docs/research/az-region-profile/thickness.md` §9 both frame the choice as *one
`t_int`* against *minima keyed by construction type*. Those are shapes A and B
below. Item 3 is asking about shape C, and neither document names it.

| | shape | what it is | ADR 0001 c5 |
|---|---|---|---|
| **A** | one `t_int`, one construction type | what ships | intact |
| **B** | a second **construction type**, each with its own single `t_int` | a Plan is `brick` *or* `stone`; every partition in it is that type's | intact |
| **C** | two `t_int` **inside one Plan** | a partition *and* a heavier internal bearing wall — what real dwellings do | **broken** |

**The ticket's re-pricing instruction is right, and it re-prices a cost that was
already nil.** ADR 0009's exemption applies to B *and* to C — ADR 0007 binds "every
internal wall thickness the profile offers" either way. Measured,
`experiments/thickness-fidelity/reprice.py`, reading `room-constraints.json`:

- linear minima published by `profiles.AZ`: **0**  (`verified` — every one of the
  six `widths_mm` cells at `statutory_floor` is `null`, and the profile's own
  comment says so: *"ALL SIX width cells at statutory_floor are null"*)
- linear minima published by the ergonomic layer: **36**, all exempt under ADR 0009
- so a second `t_int` duplicates **zero rows today**, in either shape

So the standards-table cost is nil, and it would have been nil for AZ even without
ADR 0009, because AZ publishes nothing for the congruence to bind on. **The
re-pricing does not change which shape is affordable, because the cost it removed
was never the one doing the work.** What remains is different for B and for C, and
that difference is the whole of item 3:

- **B's remaining cost is small and its remaining benefit is measured at zero**
  (§4.5). A second construction type gives a Plan a different single thickness. It
  does not give one Plan two. Against §2's finding — the mixing real dwellings show
  is **within** a dwelling — B buys a different *product claim* (`stone`, which the
  profile itself calls "the one real fidelity cost of the single-`t_int`
  decision"), and buys nothing for the question item 1 asks.
- **C's remaining cost is a hard acceptance rule and the solver's model**, §4.3, and
  ADR 0009 does not touch it.

### 4.2 The residue argument survives ADR 0010, checked rather than assumed

The ticket asserts that adding a uniform finish translates the whole candidate set
without changing which pairs share a residue class. Recomputed directly over the
19 sourced candidates in `thickness.md` §9:

```
structural (pre-ADR-0010), 19 candidates: pairs sharing a class mod 250 = []
total (+2 x t_finish = +30),  19 candidates: pairs sharing a class mod 250 = []
shipped t_int total 150 -> residue 100
second t_int from t_int_bearing 250 + 2 x 15 = 280 -> residue 220     same class? False
```

`derived` — the arithmetic is mine, the 19 candidate values are `reported` from
`thickness.md` §9, which sourced each first-hand. **The ticket's claim holds.** It
had to: a common translation preserves differences, and pair-sharing depends only
on differences.

But note what that means. The residue argument was never a reason to avoid a
second thickness *per se* — it is a reason a second thickness needs its own minima
table. With ADR 0009 in force and AZ publishing no linear minimum, **the residue
argument currently forbids nothing.** The single-`t_int` decision has quietly lost
the constraint that "forced" it. It survives on a different one.

### 4.3 The constraint that actually forces it is ADR 0001, and it is already a hard rule

> **Uniform `t_int` is load-bearing, not a simplification.** The single erosion
> constant is what makes the cheap form (`erode(rect, t_int/2)`) exactly equal the
> real definition (the polygon bounded by surrounding wall inner faces). Vary
> internal thickness per wall and the cheap form is silently wrong.
> — ADR 0001 consequence 5

It is not a note. It is enforced, `hard`, at the validator:

> `model.space_matches_erosion` — *"Every Space polygon equals its solved
> centreline rectangle eroded by `t_int/2`."*
> Its own note: *"It fails the day internal wall thickness stops being uniform,
> which is the point of keeping it."*

Shape C therefore is not a data change. It deletes a hard acceptance predicate,
changes what a Space is derived *from*, and pushes thickness into the solver's
decision variables — precisely the move ADR 0001 rejected, because a per-room
clear width `grid·w − (t_left + t_right)/2` depends on which walls bound the room,
and which walls bound the room is a solve-time variable.

### 4.4 One cheap version of C exists, and it should be named now rather than found later

**Solve at the thicker value; draw the thinner one.** Dilate the solve domain by
`t_max/2` uniformly, so every tiling edge is still a centreline and the tiling
still closes, then draw selected partitions at 150 instead of 280. Every room is
then *at least* its minimum, `clear = erode(solved, t/2)` becomes an inequality
the validator can still check exactly per wall segment, and ADR 0001's uniformity
survives where it is load-bearing (the solve) while the drawing gets two weights.

It is not free, and the price is in the currency ADR 0007's deletion is measured
in — solve cells, not millimetres (`reprice.py`):

| | summed over 36 ergonomic room-axes |
|---|---|
| solve cells at `t_int` = 120 | **253** |
| solve cells at `t_int` = 150 | **253** |
| solve cells at `t_int` = 280 | **272** |
| room-axes needing one more 250 mm cell at 280 than at 150 | **19 of 36 (53 %)** |
| extra solve domain | **+4,750 mm summed, +132 mm per room-axis** |

Two things fall out, and the first is a free gift to a ticket that is not this one.

**ADR 0010's 120 → 150 move cost the solver nothing.** 253 cells either way; not a
single room-axis changed its ceiling. That is *partial* evidence toward the
re-owed room-count deletion analysis (map: *"Ticket 19's room-count deletion
analysis is re-owed… computed at `t_int` = 120, and ADR 0010 makes it 150"*) — it
shows the per-room ceiling is unmoved. It does **not** settle it, because the
deletion also turns on the Envelope's own re-snapping, which this arithmetic does
not touch. Reported so the owner of that item has a starting point, not a
conclusion.

**Solving at 280 charges 53 % of room-axes an extra cell.** ADR 0009 already found
250 mm charging the 5-room case — the bottom of C13's band and the corpus's
commonest dwelling size. Shape C's cheap version makes that worse, in exactly that
band. Whether it makes it *fatal* is unmeasured: it needs a solver run, and
`experiments/solver-toy/` belongs to other tickets.

**And it has a second bill, in area.** §3.3 measures the same choice in Σ Space
area: at 280 the partition footprint is **10.6 %** against the corpus's 4.8 %, and
the drift is **−4.2 % to −5.8 %** — the width of the hard area gate. Under
"solve at 280, draw at 150" that arrives as a *positive* surprise instead: the
delivered Σ Space area exceeds what the solve computed, by the difference between
the two thicknesses over every internal wall. Either way, the number
`area.invented_envelope_hard` reads is no longer the number the solve produced,
and that is a second hard rule to re-derive, not just a tolerance to widen.

### 4.5 What the second thickness buys, measured

"Misplaced material" below is the length-weighted L1 distance between the real
Space-to-Space separation and the thickness we would draw there, summed over every
internal wall in the sample and expressed as a share of the real internal
partition material. Zero means a perfect per-wall thickness; it is a fidelity
measure, not an area error, and it is the honest way to price a *catalogue*.

```
real internal partition material in the sample: 70,133 m^2
   A. one t_int = 150 everywhere (SHIPPED)             misplaced 26,734 m^2    38.1%
   B. one t_int per PLAN, better of {150, 280}         misplaced 25,993 m^2    37.1%    (plans picking 280: 6.3%)
   C. two t_int WITHIN a plan, {150, 280} per wall     misplaced 19,526 m^2    27.8%
   best single value, length-weighted L1: t = 146 mm   misplaced 26,685 m^2    38.0%
   best PAIR, per wall:  t = (136, 380)         misplaced 17,771 m^2    25.3%
   ceiling: a perfect per-wall thickness would misplace 0 m^2.
   with the SAME best pair (136, 380) available:
      chosen once per PLAN : misplaced 26,619 m^2   38.0%   (plans picking the heavier: 2.3%)
      chosen per WALL      : misplaced 17,782 m^2   25.4%
      of the 12.7 points a second thickness can win, per-plan selection
      reaches 1% and the remaining 99% lives INSIDE a dwelling.
   drift at each option (mean % of Sum(Space area) per dwelling):
      A one t_int = 150          mean +0.68%   p50 +0.40%   |drift| p90 3.09%
      B one per plan {150,280}   mean +0.39%   p50 +0.22%   |drift| p90 2.60%
      C two per wall {150,280}   mean -0.16%   p50 -0.23%   |drift| p90 2.09%
      D two per wall (136, 380)  mean +0.09%   p50 +0.04%   |drift| p90 1.86%
```

**Read the B row first, because it decides the ticket.** A second *construction
type* — one `t_int` per Plan, chosen from two — is the purchase ADR 0009 makes
free. Measured, it takes 38.1 % misplaced to 37.1 %: **one point out of the 12.7
that a second thickness can win.** And with the **best possible** pair made
available the decomposition is blunt:

> of the 12.7 points a second thickness can win, per-plan selection reaches
> **1 %** and the remaining **99 % lives inside a dwelling.**

**Shape B is not a cheaper version of shape C. It is a different purchase that buys
almost none of what C buys.** A second construction type is a product decision
about `stone` versus `brick`; it is not an answer to item 1.

Three further readings.

- **The shipped 150 is within 4 mm of the corpus-optimal single value.** The
  length-weighted L1-optimal single thickness over 411 km of Swiss internal wall is
  **146 mm**; `AZ` ships **150**, reached from an Azerbaijani half-brick dimension
  plus an Azerbaijani plaster thickness with no reference to any corpus. 38.0 %
  misplaced against 38.1 %. **That is the sanity check the ticket asked for, and it
  passes about as well as a sanity check can.**
- **What a second thickness buys is real but bounded.** The best achievable pair
  (136, 380) reaches 25.3 %; *our own* pair (150, 280) reaches **27.8 %** — 10.3 of
  the 12.8 available points, **80 % of the achievable gain, using values already in
  the profile**. If shape C is
  ever built, it does not need new numbers — `t_int_bearing` is already there,
  `verified`, and unused.
- **The heavier fitted value is 380, not 280, and that is partly an artefact.**
  1.5 % of internal wall length measures ≥ 300 mm, which is implausible as a
  partition and is this method's own error bar (§0). The fitted pair chases that
  tail. Read (136, 380) as "a light one and a heavy one", not as a catalogue.

---

## 5. Item 4 — sanity-check the shipped value, and do the biases compound?

The ticket asks whether two known biases compound. There are **three**, they line
up rather than cancel, and the third was already measured on this map without
anyone putting it next to the other two.

| | bias | direction | source |
|---|---|---|---|
| 1 | `t_int` = 150 against a corpus whose internal separation is thinner in small dwellings than in large ones | **relatively worse the smaller the dwelling** | §3, measured here |
| 2 | ADR 0008 conversion drops the **large** dwellings, so the precedent pool skews small | **dwellings smaller** | *Rectangularising real rooms* §6.6, reproduced here |
| 3 | the conversion's own per-room area error, median **−3.45 %** | **rooms smaller** | `experiments/rectangularise/out/fit_analysis.txt`, `reported` — read first-hand from that artefact, not recomputed |

```
Sum(Space area) in the sample, m^2: p5=40  p10=47  p25=60  p50=76  p75=93  p90=106  p95=114
rooms per dwelling:                 p5=4  p10=5  p25=6  p50=7  p75=8  p90=9  p95=9
drift vs dwelling size, by Sum(Space area) quintile:
   Q1  area p50   47.4 m^2  n= 2813  median internal t   115 mm  drift mean +0.33% (wall)  -0.74% (body)
   Q2  area p50   63.8 m^2  n= 2812  median internal t   123 mm  drift mean +0.45% (wall)  -0.65% (body)
   Q3  area p50   76.3 m^2  n= 2813  median internal t   127 mm  drift mean +0.58% (wall)  -0.48% (body)
   Q4  area p50   88.8 m^2  n= 2812  median internal t   132 mm  drift mean +0.80% (wall)  -0.38% (body)
   Q5  area p50  105.7 m^2  n= 2813  median internal t   142 mm  drift mean +1.24% (wall)  -0.03% (body)
drift vs room count:
    4 rooms  n= 1158  median internal t   122 mm   drift mean +0.58% (wall)  -0.58% (body)
    5 rooms  n= 2205  median internal t   128 mm   drift mean +0.53% (wall)  -0.48% (body)
    6 rooms  n= 2794  median internal t   127 mm   drift mean +0.54% (wall)  -0.52% (body)
    7 rooms  n= 2791  median internal t   130 mm   drift mean +0.73% (wall)  -0.47% (body)
    8 rooms  n= 2661  median internal t   127 mm   drift mean +0.72% (wall)  -0.46% (body)
    9 rooms  n= 1786  median internal t   130 mm   drift mean +0.82% (wall)  -0.36% (body)
   10 rooms  n=  668  median internal t   140 mm   drift mean +1.26% (wall)  -0.06% (body)
joined to ADR 0008 conversion status (experiments/rectangularise/out/swiss_fit.json):
   converted n=1787   dropped n=805
   converted  median area   71.7 m^2   median rooms 6   median internal t   127 mm   drift mean +0.57% (wall)  -0.50% (body)
   dropped    median area   90.1 m^2   median rooms 8   median internal t   138 mm   drift mean +1.04% (wall)  -0.21% (body)
```

### 5.1 First, the sanity check itself: the shipped value is nearly optimal

Before the compounding question, the ticket's own: is 150 well placed? Measured
three ways, it is.

| | |
|---|---|
| corpus-optimal **single** internal thickness, length-weighted L1 over 411 km | **146 mm** |
| shipped `t_int` | **150 mm** |
| misplaced material at 146 vs at 150 | 38.0 % vs **38.1 %** |
| corpus internal median | 131 mm (150 sits ≈ p60) |
| area drift at 150 | straddles zero, §3 |

`t_int` = 150 was reached from AzDTN 2.17-1's half-brick and AzDTN 2.12-4\*'s
plaster, with no corpus involved. It lands **4 mm** from the value a Swiss corpus
would have chosen. Two independent construction traditions, one number. **The
shipped value is not the problem this ticket was looking for.**

### 5.2 The biases do compound, and there are three of them

Bias 2 is reproduced here independently, on a different sample and by a different
route — this study never runs the ADR 0008 fit, it joins its recorded status and
measures the areas itself. *Rectangularising real rooms* reported dropped dwellings
at a median **8 rooms / 89.9 m²** against converted at **6 / 71.7 m²**. Measured
here: **8 / 90.1 m²** against **6 / 71.7 m²**. That is as close to an exact
reproduction as two independent measurements get, and it means the retained
precedent pool really is the smaller dwellings.

Bias 1's *sign* at 150 is ambiguous (§3.1) but its *gradient* is not, and the
gradient is what compounds. On the robust `body` estimator the drift runs
**−0.74 %** in the smallest area quintile to **−0.03 %** in the largest, monotone
across all five; on the `gap` estimator it runs +0.33 % to +1.24 %, monotone in the
same direction. Both say the same thing: **a uniform 150 mm partition costs a small
dwelling relatively more area than a large one**, because a small dwelling packs
more partition per m² of Space.

The two biases are therefore not independent draws that happen to align. They are
driven by the same variable — partition density — and the join confirms it:
converted dwellings sit at −0.50 % (body), dropped at −0.21 %.

### 5.3 What that is worth, and what it is not

Each bias is small on its own; the third, at −3.45 % per room, is the largest and
is not this ticket's. Together, all pointing the same way, on a quantity gated at
5 % hard and 2 % soft, in the room-count band C13 promises and the corpus is
densest in — that is worth writing down, and it is **not** worth changing `t_int`
for. Bias 1 is the only one this ticket owns, its source is a `verified`
Azerbaijani masonry dimension plus a `verified` Azerbaijani plaster thickness, and
moving a `verified` number to cancel two artefacts of a Swiss corpus is exactly the
laundering C11 forbids. §5.1 says it does not need moving anyway.

The right consumer is *Fit the ENGINE_CHOICE acceptance thresholds to the
corpora*, which owns both area gates, and *The room-count envelope v1 promises*,
which owns the small-dwelling end of the band where all three biases land hardest.
Neither currently has reason to know this.

---

---

## 6. What this contradicts, named

C11 and the map's own standard: a measurement that disagrees with something
already recorded says so, and names it.

### 6.1 VERIFIED, not contradicted — "there is no module in the corpus at all"

*Which region profiles ship in v1* is reproduced on an independent sample, and it
holds. `verify_prior.py`, over **467,690** usable WALL separators from the 1-in-10
floor sample (the prior used a 200,000-wall random sample, 199,210 usable):

| | prior | reproduced here |
|---|---:|---:|
| p1 / p5 | 42 / 61 | **42 / 61** |
| p25 | 109 | **105** |
| p50 | 169 | **168** |
| p75 | 267 | **263** |
| p95 / p99 | 440 / 590 | **433 / 579** |
| within ±2 mm of a multiple of 10 | 59.1 % | **59.8 %** |
| even millimetres | 59.2 % | **60.3 %** |
| modal snapped value | 80 mm at 5.60 % | **80 mm at 6.22 %** |
| top 20 snapped, cumulative | 70.5 % | **71.0 %** |
| 8-entry catalogue at ±10 mm | 58.5 % | **59.3 %** |
| 12-entry catalogue | 70.9 % | **71.2 %** |

Every cell within about two points, on a sample twice the size drawn a different
way. The strip gate discards only **1,772 of 469,462** polygons (0.38 %), so it is
not hiding a population. **C11 is satisfied: the prior is reproduced, not
inherited.**

**But splitting it changes how strong the finding is, and the split has never been
done.** Same statistic, same method, same sample, partitioned by §0's classifier
(these are per-wall figures, unweighted, to match the prior's method exactly — §2's
length-weighted percentiles differ slightly and are the right ones for a drawing
question):

| | all walls | **internal only** | boundary only |
|---|---:|---:|---:|
| n | 467,690 | **200,017** | 339,646 |
| p25 · p50 · p75 | 105 · 168 · 263 | **91 · 127 · 170** | 154 · 228 · 322 |
| within ±2 mm of a multiple of 10 | 59.8 % | 58.8 % | 61.1 % |
| modal snapped value | 80 mm at **5.6 %** *(prior)* / 6.2 % | **80 mm at 9.6 %** | 200 mm at 4.4 % |
| top 20 snapped values, cumulative | 71.0 % | **91.5 %** | 61.4 % |
| **8-entry catalogue at ±10 mm** | 58.5 % *(prior)* / 59.3 % | **74.7 %** | 48.9 % |
| 12-entry catalogue | 70.9 % *(prior)* / 71.2 % | **84.1 %** | 63.1 % |

### 6.1a QUALIFIED — "an 8-entry catalogue covers 58.5 % of real walls" is true of the wrong walls

*Which region profiles ship in v1* used the coverage row to argue that the
thickness catalogue is `ENGINE_CHOICE` **unavoidably**. Restricted to the walls a
`t_int` catalogue actually governs, the same 8-entry catalogue covers **74.7 %**,
twelve entries cover **84.1 %**, and **twenty snapped values cover 91.5 %** of real
internal walls against 71.0 % of all walls. The dilution was the exterior and party
walls, whose build-ups genuinely do vary continuously, and they outnumber the
partitions.

**The conclusion survives; the evidence for it was overstated.** The corpus still
hands us no *values*: the modal internal thickness holds 9.6 %, under a tenth, and
58.8 % near a multiple of 10 against 50 % for uniform noise is a weak module at
best. `ENGINE_CHOICE` remains right and for the reason ADR 0006 gives — no readable
standard and no corpus supplies the contents. But the sentence *"an 8-entry
catalogue matches 58.5 % of real walls"*, which appears in the ticket's own summary
table and reads as the clincher, understates the corpus's regularity by about
16 points on the population it is being used to talk about.

This is filed as a **qualification, not a reversal**, and deliberately: it is the
kind of number that would make a future session think the corpus could supply a
catalogue after all. It cannot. 91.5 % of internal walls fall in the top twenty
*snapped* values — twenty entries, none holding a tenth of the mass, with no
arithmetic relationship between them. That is not a module; it is a wide
distribution measured coarsely.

### 6.2 CONTRADICTED — the all-walls percentiles are being read as partition percentiles

Ticket 33's own summary table says `t_int` is *"below the corpus median, near the
p25"*, citing p25 109 / p50 169. The map's **Standards table** row inherits the
framing. Those percentiles are the **all-walls** statistic, and the population
`t_int` names is not that population — **70 % of the wall length in it is not
partition** (§0).

| | all walls (the prior, and what the ticket quotes) | **internal only** (measured here) |
|---|---:|---:|
| p25 | 105 | **100** |
| **p50** | **168** | **131** |
| p75 | 263 | **169** |
| p90 | — | **204** |
| n | 467,690 walls | 190,181 runs, 411.4 km |

The two distributions differ most exactly where the argument was made. Against the
right one, `t_int` = 150 sits at roughly the **p60** — **above** the internal
median, not below it, and not remotely at the p25.

**What survives**: the *no-module* finding, which does not depend on the split
(§6.1). **What does not**: any sentence placing `t_int` against "the corpus" that
does not say which walls.

### 6.3 PARTLY CONTRADICTED, PARTLY DISSOLVED — item 2's stated expectation

> *"A `t_int` at the corpus p25 makes our rooms systematically **larger** than the
> same solved rect would give at the corpus median."* — ticket 33, item 2

Split it in two.

- **The percentile clause is wrong**, and stays wrong at either thickness (6.2).
- **The consequence was right about 120 and is not true of 150.** At 120 all three
  estimators are positive and 71–86 % of dwellings drift positive; at the shipped
  150 they straddle zero and the positive share falls to 34–61 %. §3.1.

So this is not a case of the map recording something false. It is a case of ADR
0010 moving the number between the ticket being written and the ticket being
worked, and the move happening to null the effect the ticket was written to
measure. Recorded as such rather than scored as an error.

### 6.4 CORRECTED — ADR 0010's own partition-footprint figure is understated at the thickness ADR 0010 shipped

> *"On a 90 m² dwelling the partition footprint is roughly **4–5%** — the width of
> the 5% gate itself."* — ADR 0010, consequence 4; repeated in
> `docs/spec/acceptance-bar.md` §8

Measured, as a share of Σ Space area over 14,063 dwellings:

| | mean | p50 |
|---|---:|---:|
| the corpus's own partitions | **4.8 %** | 4.7 % |
| our footprint at `t_int` = 120 | **4.5 %** | 4.6 % |
| **our footprint at `t_int` = 150** | **5.7 %** | **5.7 %** |
| our footprint at `t_int` = 280 | 10.6 % | 10.7 % |

"Roughly 4–5 %" is **verified** for the corpus and for the 120 it replaced. At the
**150 ADR 0010 actually shipped it is 5.7 %** — wider than the 5 % gate it is being
compared to, not the same width as it.

This *strengthens* ADR 0010's argument rather than weakening it — the quantity
change it flagged is larger than it said — but the number as written is stale, and
it is quoted in two places. Filed as a correction for whoever next touches
`acceptance-bar.md` §8; not edited here, because this ticket does not write that
file.

### 6.5 SUPERSEDED — "a second `t_int` needs N copies of every dimensional minimum"

> *"**Per-thickness minima was rejected**, not overlooked: it needs *N* copies of
> every dimensional minimum…"* — `docs/research/az-region-profile.md` §2, and the
> same sentence in `profiles.AZ.construction.ship_gates.adr_0007_single_t_int_decision`

True when written. **False now**, and by a count rather than an argument: ADR 0009
exempts the ergonomic layer, `profiles.AZ` publishes **0** linear minima, so *N*
copies of zero rows is zero rows (§4.1). The single-`t_int` decision is unchanged
but its recorded justification is no longer the operative one, and the ship-gate
note should say so the next time that file is opened.

### 6.6 NARROWED — "ADR 0009 makes this markedly cheaper than it looked"

Ticket 33, item 3. It does, and the cost it cheapens was already zero for `AZ`.
The cost that binds is ADR 0001 consequence 5 and the hard validator rule
`model.space_matches_erosion`, and ADR 0009 does not touch either. §4.1, §4.3.

---

## 7. Provenance of every number used

| number | value | grade | where it comes from |
|---|---|---|---|
| `t_int_structural` | 120 mm | **verified** — *by ticket 25, not re-read first-hand here* | AzDTN 2.17-1 cl. 4.3; Table 29 n.2 |
| `t_finish` | 15 mm | **verified** — *by ticket 35, concurrently, not re-read here* | AzDTN 2.12-4\* App. 8\* Table 1 rows 27–28. Was `engine_choice` when this ticket was written; upgraded during this session. The **value did not move**, so every figure below stands; had it moved, `t_int` moves by 2 × Δ and so does every drift number |
| `t_int` total | 150 mm | **derived** | `t_int_structural + 2 × t_finish`, ADR 0010 |
| `t_int_bearing` | 250 mm | **verified** — *by ticket 25* | AzDTN 2.17-1 cl. 6.9 |
| a second `t_int` total | 280 mm | **derived** | `t_int_bearing + 2 × t_finish`, by ADR 0010's own rule |
| the 19 candidate `t_int` values | — | **reported** | `docs/research/az-region-profile/thickness.md` §9, which sourced each first-hand |
| residue classes, pair-sharing | — | **derived** | computed here from the above, `reprice.py` |
| solve cells per room-axis | — | **derived** | `⌈(m + t)/250⌉` over the ergonomic layer's own 18 room types, `reprice.py` |
| every Swiss Dwellings figure | — | **verified** | read first-hand from `data/corpora/swiss-dwellings/swiss-dwellings-v3.0.0/geometries.csv`, sha256 recorded in `dataset-inventory.md` §1.1 |
| every ResPlan figure | — | **verified** | read first-hand from `data/corpora/resplan/ResPlan.pkl`, per-plan metre scale recovered as `sqrt(area / polygon_area)` per `dataset-inventory.md` §2.4 |
| corpus internal thickness, length-weighted | p25 100 · p50 131 · p75 169 · p90 204 | **verified** | `measure.py` + `analyse.py`, 190,181 runs / 411.4 km |
| corpus internal thickness, per wall (prior's method) | p25 91 · p50 127 · p75 170 | **verified** | `verify_prior.py`, n = 200,017 |
| corpus-optimal single internal thickness | 146 mm | **derived** | length-weighted L1 minimisation over the `gap` histogram, `analyse.py` |
| "≥ 200 mm is an internal bearing wall" | — | **engine_choice** | the corpus carries no structural attribute; this threshold is ours and it is the weakest thing in §2 |
| "≥ 50 mm of wall = 1 mm of paper = a visible difference in poché" | — | **engine_choice** | the 1:50 arithmetic is `derived`; that 1 mm is the *legibility* threshold is a judgement and nothing here measures it |
| paper widths at 1:50 | — | **derived** | `thickness / 50`, against `annotation.md`'s solid poché |
| the 5 % / 2 % area gates | — | **engine_choice** | `rules.json` `area.invented_envelope_hard` / `_soft`, both unfitted |
| the corpus's own area accuracy | median 1.2 % | **verified** | Swiss Dwellings deposit description, quoted in `dataset-inventory.md` §1.2 |

---

## What could not be obtained

This list is load-bearing; several conclusions above are weaker than they look
because of it.

1. **Any Azerbaijani dwelling geometry at all.** No corpus on this map holds one,
   and none is obtainable. Every geometric statement here is measured on Swiss
   dwellings and read against an Azerbaijani profile. That is C14's permanent
   condition — v1 draws *Swiss-shaped layouts to Azerbaijani conventions* — and it
   is why the corpus is this ticket's **sanity check and not its source**. The
   corpus cannot set `t_int`; it can only price what `t_int` costs.
2. **A third corpus.** `data/corpora/rplan/`, `msd/` and `procthor/` are **empty
   directories**. RPLAN needs a human through a Google Form
   (`dataset-inventory.md` §3) and MSD is a subset of Swiss Dwellings anyway. So
   the corroboration available is one-and-a-bit corpora, not three.
3. **A per-wall thickness in ResPlan.** Its schema holds a single scalar
   `wall_depth` per plan — measured, **17,000 of 17,000 plans carry exactly one**,
   and 99.0 % of plans' own `wall` geometry holds a single width because that
   geometry is generated from the scalar. ResPlan therefore **cannot corroborate
   or refute within-dwelling mixing. It assumes uniformity.** Recorded as an
   assumption rather than used as agreement.
4. **Which physical plane the Swiss surveyor drew.** §1 establishes that Swiss
   Dwellings records **one** plane and no finish layer — the Space polygon sits on
   the wall body's own face. Whether that face is masonry or render is *not*
   recoverable: there is no field for it and no second polygon to difference. The
   full version of this check belongs to *Look at the converted corpus*
   (ticket 27), which is open and unclaimed; what is here is the minimum needed to
   know which of our two numbers — 120 structural or 150 total — the corpus is
   comparable to, and the answer is that the question does not arise on the corpus
   side.
5. **A load-bearing flag.** `separator/WALL` carries no structural attribute, so
   "is this 250 mm internal wall load-bearing?" cannot be answered from the file.
   The ≥ 200 mm proxy used in §2 is ours and is `engine_choice`.
6. **Solve time at a second thickness.** Item 3's shape-C pricing is arithmetic
   over the ergonomic table and the grid, not a solver run. `experiments/solver-toy/`
   was **not** re-run: the ticket forbids touching existing experiment directories,
   and the harness is owned by other tickets. So the cost is stated in solve cells,
   which is the quantity ADR 0007's deletion turns on, and **not** in seconds or in
   feasibility.
7. **Whether a Practitioner calls the uniform plan generated.** Nobody has been
   shown one. `experiments/thickness-fidelity/out/compare.png` is the artefact and
   §2 reports what is visible in it; the judgement is not a measurement and is not
   claimed as one.
8. **The SIGN of the area drift at `t_int` = 150.** Three estimators, three
   different answers straddling zero (§3.1). This study can bound the magnitude —
   under one percent of Σ Space area — and cannot resolve the direction. Anyone
   quoting a signed drift at 150 from this document is quoting one estimator and
   should say which. The sign at **120** *is* resolved: positive on all three.
9. **The magnitude of the per-room bathroom drift.** The +5.06 % figure in §3.2 uses
   the `gap` estimator, whose contamination is concentrated exactly around service
   voids and therefore around bathrooms. The **ordering** across room types is
   robust; the **number** is not, and no estimator available here can fix it,
   because the area-based one does not decompose to rooms.
10. **Baku's degree-day figure**, and therefore a derivable `t_ext_total`. Unchanged
   from *The Azerbaijani region profile*, still `engine_choice`, not this ticket's
   to settle — but noted because §3's drift arithmetic holds the Envelope fixed and
   so is insensitive to it.

---

## Coordination with two sibling tickets

**Ticket 35, *What an Azerbaijani finish layer actually is*, was resolving in
parallel with this one and its result landed mid-session.** It upgraded
`t_finish` = 15 mm from `engine_choice` to `verified` against AzDTN 2.12-4\*
App. 8\* Table 1 rows 27–28. **The value did not change**, so nothing here moves.
This is stated rather than left implicit because every figure in §3 scales with
`t_int`, and `t_int` is `120 + 2 × t_finish`.

**Ticket 27, *Look at the converted corpus*, owns the full structural-versus-
finished check** and is open and unclaimed. §1 answers only the sliver this ticket
could not proceed without — that the corpus's Space polygons sit on its wall
bodies' own faces, so there is one plane and not two — and deliberately does not
go further. Whether the plane the Archilyse survey drew is masonry or render is
recorded in §1 as unobtainable, not guessed.

---

## Reproducing

```
python experiments/thickness-fidelity/extract.py 10        #  ~25 s
python experiments/thickness-fidelity/measure.py           #  ~45 min
python experiments/thickness-fidelity/analyse.py           #  seconds
python experiments/thickness-fidelity/verify_prior.py      #  ~3 min
python experiments/thickness-fidelity/resplan_thickness.py #  ~2 min
python experiments/thickness-fidelity/reprice.py           #  instant
python experiments/thickness-fidelity/draw_compare.py 5 1  #  seconds
python experiments/thickness-fidelity/classify_check.py 3 1
```

`experiments/thickness-fidelity/README.md` carries the two things that will bite
whoever runs this next.
