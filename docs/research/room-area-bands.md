# What a room's area is allowed to be

Findings for *What a room's area is allowed to be*
(`docs/wayfinder/tickets/37-what-a-rooms-area-is-allowed-to-be.md`).

Everything numeric here was measured on this machine on **2026-08-22** against the
corpora on disk under `data/corpora/`, through the committed conversions in
`experiments/rectangularise/out/`. Harness: `experiments/room-area-bands/`, which
is new and self-contained. Nothing in `data/acceptance/rules.json`,
`data/standards/room-constraints.json` or `docs/spec/` was edited — the ticket
declares itself read-only on those and is.

---

## Headline

**A maximum is enforceable, it is nearly free, and the number it should carry is
not the one the ticket's framing implied.**

**The anchor.** The ticket offered three anchors and asked which the data
supports. The answer is the **Room's own `target_area`**, which `brief.md` §9.3
already committed the Brief contract to — and the reason is an identity rather
than a measurement: §9.2 sets a silent Room's target from `market_default` →
**corpus median** → absent, all per-type constants, so *anchoring to the target
and anchoring to the room type absolutely are the same rule* for every Room a
Homeowner does not size by hand. They diverge only when the Homeowner states a
number, and there the statement must win. **Anchoring to a fraction of the
dwelling is refuted**: it is the *loosest* of the anchors tested, on 7 of 9 Swiss
classes and 4 of 5 ResPlan classes.

**The absorber, and this is the finding that costs the most.** A Swiss bedroom
**does not grow with the dwelling at all** — per-room slope 0.0020, r² **0.000**,
so 40 m² more dwelling buys a bedroom **0.08 m²**. Nor does a WC (0.08 m²), a
bathroom (0.43) or a storeroom (0.55). A bigger Swiss flat is not a flat of bigger
rooms; it is a flat with **more** rooms, a **bigger living room** (+7.99 m² per
40 m²), and **more corridor** (+4.00). So the absorber is not a Brief field to
invent — it is measured, it is the living room and then circulation, and it can
be expressed as a **soft weight per type taken from the type's own dispersion**.

**A circularity was found and removed, and it moved the WC cap by 2.2×.** The
first cut of the cap returned **2.40 m² for a WC at p95, p99, p99.5 *and* p99.9** —
because the reporting class `wc` is *defined* as `BATHROOM < 2.4 m²`, so every
percentile of it returns the splitter. Re-measured against Swiss Dwellings'
**fixture** ground truth — toilet present, no bath and no shower, 13,436 rooms —
a real WC's p99 is **5.29 m²** and one real WC is **18.23 m²**. **19.3 % of real
WCs are at or above the 2.4 m² splitter and are invisible to it.** ResPlan cannot
be corrected the same way and its WC figures are reported as unusable, not quoted.

**It is free in the solver.** H4 already builds `a = w·h` through
`AddMultiplicationEquality` to post the *minimum* area. A maximum is a domain
bound on a variable that already exists — and an upper bound on a product
*tightens* propagation on `w` and `h` rather than weakening it. So `site: both`
costs nothing, and there is no reason to make this validator-only.

⚠️ **The table below is keyed by `class` and the rule it feeds is keyed by
`type`, and for eight months nothing said which read which.** *Nineteen room
types and nine area-band classes* found that **nine of the nineteen Room types
resolved to no class at all**, so `dim.max_area` — hard, site `both` — silently
did not fire on them, and `hall` is one: `resolve` invents a hall wherever the
Brief names none, so **every Plan carried a Room with no upper bound**. The map
is now published, the class list is **eleven**, and §12 holds the whole of it.
None of the nine values below moved.

**And `dim.market_default_area` is a cause, not a bystander.** It is soft and
prefers Spaces *at or above* market default, so the objective **actively rewards
bloat** while `model.no_unassigned_area` makes the surplus compulsory. A maximum
alone leaves the incentive in place and simply moves the bloat to just under the
cap. The recommendation therefore has two halves.

---

## 1. What was measured, and on what

| corpus | dwellings | rooms | median total | source |
|---|---|---|---|---|
| Swiss Dwellings | 42,986 | 296,653 | 77.0 m² | `swiss_rects.json` |
| ResPlan | 16,617 | 110,802 | 101.5 m² | `resplan_rects.json` |

Both are the in-band (4–10 room, C13) populations produced by *Rectangularising
real rooms*. **Reported separately and never pooled**, per *Cross-dataset
unification*.

Two already-decided rules are applied and no others, because the corpus-to-
ergonomic vocabulary mapping belongs to *Two room vocabularies in one file* and
building one here would collide with its `writes:`:

- `{ROOM, BEDROOM, STUDIO}` collapse to one class, written `room*` (*What the
  model proposes*).
- `BATHROOM` splits at 2.4 m² into `wc` / `bathroom`
  (`ergonomic.corpus_label_split`) — **and §4 shows why that split cannot be used
  for the upper tail.**

### 1.1 The plane, and what "converted" turns out to mean

The ticket asks for distributions on the **converted** geometry rather than raw
polygons. Measured, that instruction points the wrong way for *area*, and the
reason is the plane.

The shipped conversion (ADR 0008, `fit_rects.py`) rasterises by **watershed**:
every wall cell goes to the nearest room, splitting each wall at its centreline.
A fitted rectangle is therefore a **centreline-plane** area. ADR 0010 makes every
published area a **finished-face** area, which is the corpus polygon. They are not
the same quantity, and the gap is not a constant:

| class | fitted / polygon, p50 |
|---|---|
| `living_dining` | 1.174 |
| `room*` | 1.233 |
| `corridor` | 1.255 |
| `kitchen` | 1.279 |
| `bathroom` | 1.395 |
| `storeroom` | 1.539 |
| `wc` | **1.582** |

Dwelling-level the ratio is **1.243** (p5 1.168, p95 1.377), but per room it runs
from 1.17 to 1.58 because a small room's share of the walls around it is a much
larger share of its own floor. **No single scalar converts between the planes.**

Deflating the fitted areas by the dwelling ratio and comparing back to the polygon
(`plane_check.py` (d)) shows the *shape* change from rectangularisation is
negligible for the large classes — `room*` p95 21.97 → 21.71, `corridor` 15.44 →
15.32 — and that everything which moves for the small wet classes is the plane,
not the conversion.

**So the band is measured on the corpus polygon, and stated as a finished-face
area.** That is the plane ADR 0010 mandates and the plane `dim.min_area` already
declares. Inherited caution, carried rather than smoothed: `dim.min_area`'s note
already records that *the corpus polygons' own face convention is unrecorded*, and
*One internal thickness* found Swiss Dwellings **records one plane and no finish
layer**, so the corpus can never say which it is. Every number below inherits that
uncertainty, in the same direction and of the same size as the floor already does.

### 1.2 A defect in a committed artifact, found in passing

`fit_rects.py` line 727 labels a fitted dwelling with
`[t for t, _ in dw[k]][:n]` — the **unfiltered** head of the source list — while
`load_swiss_geoms` (line 628) has already dropped polygons below
`MIN_ROOM_AREA`. Where a dropped polygon is not last, every label after it is off
by one.

Measured against `measure_swiss`'s correctly-filtered list: **22 of 1,787 fitted
dwellings are mislabelled, 1.23 %**. Any per-type reading taken off
`swiss_fit.json` inherits it. Everything in this document relabels from
`swiss_rects.json`. Handed to *Look at the converted corpus*, which is the ticket
that will read that file next.

---

## 2. Which anchor the data supports

Scored identically: the **narrowest interval admitting 90 % of real rooms** of the
class, as `hi/lo`. A tighter interval is a band that says more.

Four anchors, not the ticket's three — the fourth, *a multiple of this dwelling's
own mean room area*, was added because it is the natural way to let a band scale
with dwelling size without depending on the total alone.

**Swiss Dwellings**

| class | n | A1 absolute m² | A2 fraction | A4 × mean room | tightest |
|---|---:|---|---|---|---|
| `room*` | 97,776 | 9.62–20.18 (**×2.10**) | 0.103–0.319 (×3.10) | 0.84–1.88 (×2.23) | **A1** |
| `bathroom` | 51,415 | 2.74–6.31 (×2.30) | 0.029–0.097 (×3.35) | 0.25–0.57 (**×2.28**) | tie |
| `corridor` | 49,697 | 2.46–18.22 (×7.40) | 0.037–0.230 (×6.14) | 0.27–1.62 (**×6.02**) | A4 |
| `kitchen` | 41,661 | 5.09–14.80 (×2.91) | 0.063–0.179 (×2.86) | 0.46–1.25 (**×2.72**) | A4 |
| `living_dining` | 23,169 | 17.01–42.67 (×2.51) | 0.218–0.524 (×2.41) | 1.68–3.58 (**×2.13**) | A4 |
| `wc` | 11,973 | 1.23–2.40 (**×1.94**) | 0.012–0.031 (×2.47) | 0.11–0.23 (×2.13) | A1 |
| `storeroom` | 11,907 | 0.79–5.88 (×7.43) | 0.009–0.072 (×8.11) | 0.07–0.50 (**×6.71**) | A4 |
| `living_room` | 7,932 | 14.96–32.16 (×2.15) | 0.182–0.501 (×2.75) | 1.48–2.86 (**×1.93**) | A4 |
| `dining` | 1,083 | 5.03–18.96 (×3.77) | 0.061–0.254 (×4.16) | 0.53–1.89 (**×3.56**) | A4 |

**ResPlan** agrees on the shape: A4 wins `room*`, `bathroom`, `kitchen`; A2 wins
`living` (×1.66); A1 wins `wc` decisively (×1.62 against A4's ×2.59).

**A2, the fraction anchor, loses almost everywhere** and is refused. Its failure
has a mechanical cause: a room's share of the dwelling must fall as the room count
rises, so a fractional band is fitted across a trend it cannot see. A4 is A2
multiplied by the room count, which is exactly the correction, and A4 beats A2 on
**every class in both corpora**.

**A4 wins on the score and is still refused, on a ground the score cannot show.**
`cap = k × total / n` makes every room's maximum a function of how many *other*
rooms there are. A Homeowner who adds a study silently shrinks the maximum allowed
living room. That is an interaction no product surface can explain and no
Homeowner would predict, and C2's user "cannot read a dimension string". Where A4
does win, it wins narrowly and for a reason §3 captures directly and better.

**A1 and A3 are the same rule**, by the identity in the Headline, and A3 is the
better statement of it because it degrades correctly: where the Homeowner states
a target, the band follows the statement rather than a Swiss percentile.

---

## 3. Where the slack actually goes

Two tables that look like they answer this, and only one of them does.

**The one that does not.** Regressing a *type's total area within a dwelling* on
the dwelling total gives `room*` a slope of **0.422** — apparently the largest
absorber in the corpus. It is not. That slope is almost entirely *more bedrooms*,
not *bigger* ones. The same confound sits inside the naive slack attribution
(`bands.py` (C)), which credits `room*` with **31.2 %** of all above-median area:
there are ~2.3 of them per dwelling, so small per-room excesses sum.

**The one that does.** Regressing **one room's** area on the dwelling total:

| class (Swiss) | slope | r² | +40 m² of dwelling buys this room |
|---|---:|---:|---:|
| `room*` | 0.0020 | **0.000** | **+0.08 m²** |
| `wc` | 0.0020 | 0.010 | +0.08 m² |
| `bathroom` | 0.0108 | 0.044 | +0.43 m² |
| `storeroom` | 0.0138 | 0.011 | +0.55 m² |
| `kitchen` | 0.0540 | 0.163 | +2.16 m² |
| `dining` | 0.0565 | 0.042 | +2.26 m² |
| `corridor` | 0.1001 | 0.215 | +4.00 m² |
| `living_room` | 0.1433 | 0.225 | +5.73 m² |
| `living_dining` | 0.1997 | 0.280 | **+7.99 m²** |

**A Swiss bedroom is 14.4 m² and stays 14.4 m²** across dwellings from 41 m² to
115 m². The absorbers are the **living room** and then **circulation**, and
nothing else moves.

**ResPlan dissents on one row and the dissent is a labelling artefact.** Its
`living` absorbs harder still (+14.66 m² per 40, r² 0.716), but its `room*` also
grows (+3.52, r² 0.426) where Swiss's does not. ResPlan carries **four room types
and no corridor at all**, so its `bedroom` is absorbing what Swiss would label
`ROOM`, `STOREROOM` and `CORRIDOR`. Swiss Dwellings is the backbone per
*Cross-dataset unification*; Swiss governs and the dissent is recorded, not pooled.

### 3.1 This is the soft weight, and it is measured rather than chosen

Where slack should go does not need a Brief field. Rank the classes by area
dispersion and the ordering *is* the absorber ordering above:

| class | CV | soft weight (1/CV, normalised) |
|---|---:|---:|
| `wc` | 0.23 | **1.00** |
| `bathroom` | 0.23 | 0.99 |
| `room*` | 0.26 | 0.88 |
| `living_dining` | 0.28 | 0.82 |
| `living_room` | 0.29 | 0.80 |
| `kitchen` | 0.35 | 0.65 |
| `dining` | 0.50 | 0.46 |
| `corridor` | 0.58 | 0.40 |
| `storeroom` | 1.04 | 0.22 |

A tight class resists growth; a loose one absorbs. Asking a Homeowner *which room
should get the leftover space* is an architect's question put to someone C2 says
cannot read a dimension string — and `brief.md`'s whole discipline is that the
model is never asked to invent a number. **No new Brief field. The corpus already
answers it.**

---

## 4. The WC cap was circular, and the fix moves it 2.2×

`recommend.py` (F) returned a `wc` cap of **2.40 m² at p95, p99, p99.5 and
p99.9** — four percentiles, one number. That is not a distribution with a tail;
it is a class truncated at its own definition. `wc` *is* `BATHROOM < 2.4 m²`.

Swiss Dwellings carries `BATHTUB`, `SHOWER`, `TOILET` and `SINK` point features —
the same ground truth `bathroom_fixture_split.py` used to fit the splitter. Read
directly, restricted to the same in-band dwellings (`wc_fixture_truth.py`):

| in-band `BATHROOM` rooms | 63,388 |
|---|---|
| bathroom (bath or shower present) | 48,282 — 76.2 % |
| **wc (toilet, no bathing fixture)** | **13,436 — 21.2 %** |
| no fixture found, unusable | 1,389 — 2.2 % |

| class | n | p50 | p95 | p99 | p99.5 | p99.9 | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| `bathroom` (fixture) | 48,282 | 4.10 | 6.53 | 8.23 | 9.15 | 11.32 | 24.52 |
| **`wc` (fixture)** | 13,436 | **1.85** | 3.71 | **5.29** | **6.20** | 6.99 | **18.23** |
| `wc` (2.4 threshold) | 11,973 | 1.76 | 2.31 | 2.38 | 2.39 | 2.40 | 2.40 |

**19.3 % of real WCs sit at or above 2.4 m²** and **3.94 % above 4.0 m²**. The
splitter cannot see any of them, so a cap fitted through it would have been
**2.2× too tight at p99** and would have rejected a fifth of the real WCs in the
retrieval corpus.

**The fixture median reconciles exactly.** `ergonomic.corpus_label_split` records
"real WCs sit at a median 1.85 m² and real bathrooms at 4.17"; this measures
**1.85** and **4.10**, the bathroom differing only by the 4–10 room band filter.
Reconciled, per the ticket's instruction, not re-derived.

**ResPlan cannot be corrected.** It carries a `bathroom` label and no fixtures, so
every ResPlan `wc` figure in this ticket is the splitter reflected back and is
**reported as unusable rather than quoted**. This is the same permanent limit
*What an Azerbaijani finish layer actually is* found: ResPlan carries one scalar
per plan and Swiss's separator taxonomy is `WALL/RAILING/COLUMN`.

---

## 5. What the cap costs

A real dwelling dies if **any** of its rooms is over cap, so the dwelling-level
rate is the one that matters — this is the retrieval and training corpus, so what
the cap rejects here is coverage lost.

| caps at | rooms rejected | **dwellings rejected** | worst classes |
|---|---:|---:|---|
| p95 | 4.78 % | **26.63 %** | `room*`, `bathroom`, `corridor` |
| p99 | 0.97 % | **6.02 %** | same |
| p99.5 | 0.49 % | **3.10 %** | same |
| p99.9 | 0.10 % | **0.66 %** | same |

p95 is unusable. **p99.5 is the recommendation**, and the reason is the design
philosophy `circ.fraction_hard` already states in `rules.json`: *"an outer bound,
not a quality bar. Set where it only ever catches Plans that are visibly
broken."* At p99.5 the hard rule costs 3.1 % of the corpus and the *soft* term
of §6.2 does the shaping.

### 5.1 Can a maximum make a Brief impossible? Yes — at four rooms, and only there

`model.no_unassigned_area` is hard and exact. For a **given** Envelope — a flat,
C5's majority case — Σ Space area is fixed before the solve. If every Room also
carries a maximum and Σ maxima falls below it, no assignment is legal.

Real dwellings cannot show this, since they all fit by construction. So: sweep the
corpus's own commonest room *mix* at each room count, and compare Σ cap against
what dwellings of that size actually are.

| n | commonest mix | Σ cap @p99 | corpus p99 | verdict |
|---:|---|---:|---:|---|
| 4 | bathroom+corridor+kitchen+room* | **77.9** | **79.7** | **tight** |
| 5 | + living_dining | 130.0 | 84.0 | OK |
| 6–10 | — | 158–231 | 98–169 | OK |

At **p99.5** the 4-room row clears (85.7 against 79.7) and every other row has
double the headroom it needs. So the risk is real, confined to the **4-room
case**, and priced out by the same percentile chosen on cost grounds in §5.

Worth noting where that lands: four rooms is the **bottom of C13's band**, and
*Ergonomic minima* already found the 250 mm grid **charging the 5-room case**. The
small-dwelling end keeps taking the hits, from independent directions.

**And the failure mode is not solver INFEASIBLE.** H3 posts exact tiling **soft**
at weight 100,000, so an over-tight cap yields a Plan with unassigned floor, which
the validator kills on `model.no_unassigned_area`, which C6 discards and never
shows. The observable symptom is **zero survivors** — which is precisely the case
`brief.md` §9.4's pre-check exists to explain, and §6.4 puts it there.

---

## 6. Recommendation

Handed to whoever holds `rules.json` — currently claimed by *Opening placement
rules*, *Fit the ENGINE_CHOICE acceptance thresholds to the corpora* and *H8 and
the single-aspect flat*. This ticket writes none of it.

### 6.1 `dim.max_area` — new, hard, site `both`

> **Every Space area is at most the upper band for its Room type.** Where the
> Room has a `target_area` — stated by the Homeowner, or set by `brief.md`
> §9.2's ladder — the bound is `k[type] × target_area`. Where no target exists at
> all, the bound is `absolute_cap[type]`.

| class | target (corpus p50) | `absolute_cap` (p99.5) | **k** | source |
|---|---:|---:|---:|---|
| `room*` | 14.29 | 31.09 | **2.18** | polygon |
| `bathroom` | 4.10 | 9.15 | **2.23** | **fixture** |
| `wc` | 1.85 | 6.20 | **3.36** | **fixture** |
| `kitchen` | 8.04 | 20.59 | **2.56** | polygon |
| `living_dining` | 28.32 | 57.12 | **2.02** | polygon |
| `living_room` | 20.51 | 48.12 | **2.35** | polygon |
| `corridor` | 7.58 | 24.84 | **3.28** | polygon |
| `dining` | 9.79 | 35.91 | **3.67** | polygon |
| `storeroom` | 2.24 | 18.23 | **8.15** | polygon |
| `kitchen_dining` | 18.82 | 49.77 | **2.64** | **composed** ⬅ §12 |
| `living_dining_kitchen` | 37.11 | 69.00 | **1.86** | **composed** ⬅ §12 |

⚠️ **The last two rows are ticket 71's, not this ticket's**, and they are the
only rows here fitted on a population no corpus label names. Everything above
them is unchanged. See §12.4 for how they were measured and why borrowing a
donor's `k` would have been wrong by −3 % to +39 % with an unguessable sign.

**`k` is not one constant** — 2.02 to 8.15 — and the spread is not noise. The
habitable rooms `AZ` actually sizes cluster at **2.0–2.6**; the outliers are
exactly the four types `AZ` ships as `market_default: None` plus `dining` and
`storeroom`. A single global `k` would be the invented number this ticket exists
to avoid.

**A stated target is sovereign, and the absolute cap is a fallback, not a
ceiling.** A Homeowner who asks for a 30 m² living room gets a band around 30, not
around a Swiss percentile. C4 makes the Brief the real interface; the defect this
ticket fixes is an area the engine **invented**, never one the Homeowner asked
for.

### 6.2 `dim.market_default_area` becomes two-sided — amend, do not add

Today: *"prefer Spaces at or above the market_default area"*. That one-sidedness
is **half the defect**. Replace the reward with a distance penalty

```
soft_w[type] × |area − target_area|
```

with `soft_w` from §3.1. A maximum alone would leave the objective still pushing
every room upward and simply relocate the bloat to just under the cap.

### 6.3 `dim.stated_target_implausible` — new, warn

A `warn` when a **stated** target exceeds `absolute_cap[type]`, surfaced against
the Brief exactly as `area.given_envelope_warn` is. It keeps the Homeowner
sovereign while catching an LLM parse that put a decimal in the wrong place.

### 6.4 `brief.md` §9.4's pre-check gains its upper bound

§9.4 is *"two bounds, two severities, one function"* and **both are currently
lower**. Add the upper: where the Envelope is given and Σ upper band < interior
minus partitions, say so at parse time — *this Envelope is larger than this
programme can fill* — rather than after a silent zero-survivor solve. §5.1 says
this bites the 4-room case and nothing else.

### 6.5 Provenance

Every number in §6.1 is **Swiss** and the shipping profile is **`AZ`**. This is
the third documented instance of C14's `RegionProfile` / `CorpusProvenance`
mismatch and the second that is a number rather than a layout, so it is disclosed
per value in the same form `brief.md` §9.2 already uses:
`src: swiss_dwellings_p99_5`. It is **not** region-free the way `dim.min_area` is:
the ergonomic floor is region-free because a body is a body, and a maximum is a
market fact with no such defence.

---

## 7. The 40 m² WC

`brief.md` §9.3's worked case: a **5.8 × 6.9 m WC**, clearing `dim.min_area`
(≥ 0.8 m²), clearing `dim.aspect_ratio_hard` (1.19 ≤ 3.0), and unable to trip
`dim.market_default_area` because `AZ` ships `wc.market_default: None`.

Under §6.1 the ladder's second rung now supplies **1.85 m²** where `AZ` is silent,
so the target exists and the band binds: the WC's maximum is
**3.36 × 1.85 = 6.20 m²**, and 40 m² is **6.5×** it. Rejected hard, at both the
solver and the validator.

The loop closes on itself: the rule had nothing to bind to *because* the profile
was silent, and the same measurement that fixes the cap is the one that fills the
silence.

---

## 8. What this hands to other tickets

| what | to |
|---|---|
| `dim.max_area` predicate text, `k` and `absolute_cap` per type (§6.1); the `dim.market_default_area` amendment (§6.2); `dim.stated_target_implausible` (§6.3) | whoever next holds `data/acceptance/rules.json` |
| §9.4's upper pre-check bound (§6.4); §9.3's band now has numbers | whoever next holds `docs/spec/brief.md` |
| corpus medians for the silent `AZ` types (§9) | *Two room vocabularies in one file*, which holds `room-constraints.json` |
| `fit_rects.py`'s 1.23 % label misalignment (§1.2) | *Look at the converted corpus* |
| the fixture-truth `wc` / `bathroom` tail (§4) — `corpus_label_split` records medians and no upper tail | *Two room vocabularies in one file* |
| the bedroom-count → total-area joint distribution (§10) | *Homeowner product surface*, *The room-count envelope v1 promises* |
| **the two `gate_check.py` assertions — class totality, and `market_default ≤ absolute_cap` (§12.2, §12.6)** | whoever next holds `experiments/region-profile/` |
| **`reject.py` / `census.py`'s private class copies, their key disagreement, and the `kitchen_dining`-exempt re-run of `corpus_cost` (§12.7)** | whoever next holds `experiments/acceptance-thresholds/` |
| **the `k × target` cross-provenance inversion (§12.5)** | *A cap fitted in one country and a target set in another* |

---

## 9. Corpus medians for the silent `AZ` types

`brief.md` §9.2's ladder, rung 2. `AZ` ships `market_default: None` for four keys.

| `AZ` key | corpus median | n | note |
|---|---:|---:|---|
| `wc` | **1.85 m²** | 13,436 | **fixture** ground truth, not the 2.4 splitter |
| `hall` | **7.58 m²** | 49,697 | ⚠️ **this is `CORRIDOR`** — see below |
| `kitchen_niche` | — | 0 | **no corpus type**; ladder falls through to absent |
| `wardrobe_1room_entry` | — | 0 | **no corpus type**; ladder falls through to absent |

⚠️ **`hall` is not supplied and should not be recorded as if it were.** The
ergonomic layer carries `hall`, `entrance_lobby` **and** `corridor` as three
distinct types; Swiss Dwellings carries **one** label, `CORRIDOR`, and ResPlan
carries none at all. 7.58 m² is the median of all three merged. Whether that is a
usable `hall` default is a **vocabulary** question and belongs to *Two room
vocabularies in one file*, not here. It is offered as a measurement with its
limit attached, not as a default.

**Two of the four rungs are therefore empty**, and `brief.md` §9.2 already
specifies the outcome: the field stays absent, the Room is sized against its
ergonomic floor alone, and an Assumption says exactly that. **A Room with no
target has no `k`, and §6.1's `absolute_cap` is the only thing bounding it** —
which is why the fallback in §6.1 is not decorative.

---

## 10. Bedroom count → total area

Owed to `brief.md` §7, which records *"Bedroom count to total area is measured
from the corpus… This replaces the predecessor's invented area column with a real
joint distribution."*

**Swiss Dwellings**, count of `room*` per dwelling, total area m²:

| bedrooms | n | p5 | p25 | **p50** | p75 | p95 |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 1,671 | 26.7 | 33.1 | **41.7** | 52.9 | 68.4 |
| 1 | 7,548 | 30.9 | 47.8 | **56.3** | 64.6 | 78.6 |
| 2 | 15,667 | 48.1 | 65.4 | **76.5** | 85.8 | 100.4 |
| 3 | 14,005 | 59.0 | 73.9 | **90.8** | 102.1 | 118.2 |
| 4 | 3,618 | 72.5 | 82.8 | **94.7** | 112.1 | 138.7 |
| 5 | 455 | 89.7 | 100.7 | **105.8** | 114.5 | 134.4 |

**ResPlan**, same computation, and it does not agree:

| bedrooms | n | p5 | p25 | **p50** | p75 | p95 |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1,789 | 42.2 | 50.2 | **55.5** | 62.0 | 148.7 |
| 2 | 8,022 | 62.4 | 78.6 | **90.0** | 102.1 | 120.9 |
| 3 | 6,094 | 89.3 | 113.3 | **128.8** | 146.1 | 186.2 |
| 4 | 706 | 122.9 | 149.3 | **170.3** | 195.6 | 252.5 |

⚠️ **The two corpora disagree by ~40 % at three bedrooms** (90.8 against 128.8),
and the cause is the same labelling artefact as §3: `room*` in Swiss is
`ROOM ∪ BEDROOM ∪ STUDIO` competing with `CORRIDOR` and `STOREROOM` for the count,
while ResPlan has only four types and no circulation at all. **Do not pool, and
do not average.** Swiss is the backbone; the ResPlan column is the dissent, on the
record.

⚠️ **`room*` is not "bedrooms".** Swiss labels 76,052 rooms `ROOM` against 21,717
`BEDROOM` — 78 % of the class is the generic label — so what is measured is
*habitable non-living rooms*. After the `{ROOM, BEDROOM, STUDIO}` collapse that is
what a Brief's bedroom count becomes anyway, but the table should not be quoted as
a bedroom count without that sentence attached.

---

## 11. Harness

`experiments/room-area-bands/`, outputs in `out/` (gitignored; regenerate by
running the scripts).

| script | what it does | runtime |
|---|---|---|
| `distributions.py` | per-type absolute and fractional distributions, both corpora | seconds |
| `bands.py` | the four-anchor comparison, marginal allocation, slack attribution, bedroom→area joint | ~1 min |
| `recommend.py` | per-room slopes, candidate caps, reject rates, silent-type medians | ~1 min |
| `wc_fixture_truth.py` | the non-circular `wc` / `bathroom` tail, from Swiss fixture features | ~6 min (1 GB CSV) |
| `plane_check.py` | watershed vs polygon plane, and `fit_rects.py`'s label misalignment | seconds |
| `expressibility.py` | can the caps make a Brief infeasible; the `k` table | ~2 min |
| `final_table.py` | the recommendation table in §6.1 and the soft weights in §3.1 | ~1 min |

Order: `wc_fixture_truth.py` before `expressibility.py` and `final_table.py`,
which read its JSON.

**One thing that will bite whoever runs this next.** `np.percentile` over a
97,000-element array inside a 43,000-dwelling loop is what made the first run of
`expressibility.py` time out at two minutes. The caps are memoised now; keep them
that way.

---

## 12. The type-to-class map, and what it was hiding

**Added by *Nineteen room types and nine area-band classes* (ticket 71), 2026-08-30.**
Everything in §§1–11 is ticket 37's and none of its values moved. This section
adds the bridge that was missing between them and the rule they feed, and reports
what the bridge exposed.

### 12.1 Nine of nineteen types had no bound at all

`dim.max_area` states `k[type] × Room.target_area`, and `absolute_cap[type]`
where no target exists. §6.1's table is keyed by **class**, and the classes are
**corpus labels**. Nothing published the correspondence, so the rule resolved
against a key that did not exist for nine of `brief.md` §3's nineteen types:

| bound before ticket 71 | types |
|---|---|
| `k × target` | `living`, `living_dining`, `kitchen`, `bedroom_double`, `bedroom_single`, `bathroom`, `wc` |
| `absolute_cap` | `dining`, `corridor`, `storage` |
| **none — a hard rule that silently did not fire** | `hall`, `bedroom_principal`, `study`, `shower_room`, `utility`, `bathroom_combined`, `kitchen_dining`, `living_dining_kitchen`, `entrance_lobby` |

Eight of the nine are reachable in v1 and **all eight are Brief-nameable**.

**`hall` is the one that matters.** `brief.md` §3.1 invents a `hall` wherever the
Brief names none, so the circulation Room count is always exactly one and **100 %
of Plans carried a Room with no upper bound**. Its only ceiling was
`circ.fraction_hard` at 30 % of Σ Space — **27 m² of hall on a 90 m² dwelling
passes every rule in the file**. That is §7's 40 m² WC, reached through a
different door, in every plan rather than in a worked example. It is also the
worst possible case for it: `hall` has no target at either rung of §9.2's ladder
(`AZ` is silent, and `corpus_medians.hall_entrance_lobby_corridor` is explicitly
null), so `dim.market_default_area` had nothing to pull against either — a floor
of 1.0 m², no ceiling, and no preference anywhere between.

**The same map breaks the soft term.** `soft_w[type]` reads the same nine
classes, so `bedroom_principal`, `bathroom_combined` and `living_dining_kitchen`
each carried a target and **no soft term to apply it with**.

⚠️ **Correction to the ticket that raised this.** Ticket 71 states that every
class carries `"members": null`. The field did not exist at all — absent rather
than null, which is the weaker of the two states, because a null at least
declares the slot a reader should fill.

### 12.2 The resolution ladder

Published as data at
`data/standards/room-constraints.json#/ergonomic/area_band_classes`, beside
`corpus_label_map` rather than beside the table it feeds, because it is a
**vocabulary projection** and ADR 0037 put every other projection there. Four
rungs, and every row declares which it used:

| rung | meaning | rows |
|---|---|---:|
| `contains(label)` | the class was fitted on a corpus label whose population **contains** this type | 11 |
| `contains(fixture)` | the same, where the population was cut by fixture presence rather than by label | 4 |
| `composed` | no usable label, but the type's **target** is already a per-dwelling sum of clean donor classes, so the same composition yields the band | 2 |
| `analogy` | no population contains it and none can be composed | **1** |

**Containment is not borrowing, and that distinction is the whole section.** The
ticket framed the choice as *borrow a neighbour's class, or earn your own*, and
warned correctly that borrowing is a smaller version of the invented number the
rule exists to avoid. There is a third reading it did not name. A **target** must
be type-specific — it says *a hall should be about this big* — and a merged
population cannot supply one, which is exactly why rung 2 of §9.2's ladder is
null for `hall`. A **band** is a dispersion statistic over a population, and the
population `corridor` was fitted on **is** `hall ∪ entrance_lobby ∪ corridor`,
merged by the corpus itself and declared as such in `corpus_label_map`. Assigning
all three types to it is not borrowing a neighbour's number; it is naming the
class's real membership. The same reading resolves `bedroom_principal` and
`study` onto `room*` (Swiss `ROOM` is the generic label — 76,052 of the class
against 21,717 `BEDROOM` — which §10 already says), and `bathroom_combined` and
`shower_room` onto `bathroom`, of which combined units are in fact the majority.

**Totality is gated, not assumed.** All nineteen resolve or `gate_check.py`
fails. A type with no class is worse than a wrong bound, because a wrong bound
reports itself and a missing one does not.

### 12.3 `utility` — the one analogy, and it is flagged as one

No population contains it and none can be composed. Swiss Dwellings has **no
laundry label** — its room label set is ten and this is not among them. Neither
does the shipping market: over MIDA's published Baku schedules the room-name
vocabulary is **eight names** — `Eyvan`, `Yataq otağı`, `Sanitar qovşağı`,
`Mətbəx`, `Dəhliz`, `Qonaq otağı`, `Qarderob`, `Mətbəx-studio` — and **there is
no utility room and no storeroom in Azerbaijani market practice at all**.

Refusing the type in v1 was considered and rejected: AzDTN 2.7-2 puts
`camaşırxana` in the mandatory `yardımçı sahələr` list, so the norm keeps it
reachable whatever the market builds.

**It takes `bathroom`, and not `storeroom`.** Containment onto `STOREROOM` is the
tempting read and it is **wrong on the mechanism**. `STOREROOM` is dry residual
space — CV 1.04, `k` 8.15, the loosest class in the table — while a utility is
`is_wet: true`, a **plumbed appliance room** whose size is set by a machine plus
a body zone. That is the construction the ergonomic layer already uses for both:
`utility.min_area` is 900 × 1500 (washer + body zone) exactly as
`bathroom.min_area` is 1000 × 1700 (bath + body zone). It also decides the
number, and the production difference is not marginal: `storeroom` would cap a
utility at **18.23 m²** against `bathroom`'s **9.15 m²**, and 18 m² is not a
bound an architect would recognise on a laundry.

Recorded as `conf: derived` and as the table's only non-containment row, with its
retirement condition named: **any corpus carrying a laundry label**. Re-fit then;
do not re-argue.

### 12.4 The two compound types were measured, not borrowed

`kitchen_dining` and `living_dining_kitchen` are the two the ticket called *no
plausible class at all* — one label disqualified, one nonexistent. They are now
the **best**-evidenced rows in the table, because both **targets are already
per-dwelling sums of clean donor classes**, so the same composition yields the
band. Measured on ticket 70's own population,
`experiments/warp/out/dwelling_rooms.json`, dwellings holding both donors:

| class | n | p50 | p99.5 = `absolute_cap` | `k` | CV | `soft_w` |
|---|---:|---:|---:|---:|---:|---:|
| `kitchen_dining` | 1,308 | 18.82 | **49.77** | **2.64** | 0.37 | 0.63 |
| `living_dining_kitchen` | 24,046 | 37.11 | **69.00** | **1.86** | 0.23 | 1.00 |

`kitchen_dining`'s p50 reproduces the shipped `corpus_medians.kitchen_dining`
(18.8) exactly, which is the check that the composition is the same one.

**Borrowing would have been wrong, and the sign is not guessable.**

| type | borrow from | gives | against measured |
|---|---|---:|---:|
| `kitchen_dining` | `kitchen` (`k` 2.56) | 48.1 | **−3 %** |
| `kitchen_dining` | `dining` (`k` 3.67) | 69.0 | **+39 %** |
| `living_dining_kitchen` | `living_dining` (`k` 2.02) | 73.7 | **+7 %** |

And the bias has a mechanism: **a compound's `k` is always below its donors'**,
because summing partly decorrelates and a compound room is more predictable in
size than its parts (2.64 < 3.67; 1.86 < 2.02). So borrowing is systematically
**lenient** — it loosens a hard rule — while looking conservative.

⚠️ **Site clustering was checked, because `kitchen_dining`'s n is small and one
site is 12.2 % of it.** `k` re-read two further ways holds: **2.49** on site
medians (n = 160) and **2.58** with the heaviest site dropped, against 2.64 on
all dwellings. `living_dining_kitchen` is not exposed (top site 1.1 %; `k` 1.93
on site medians). The published arm is all-dwellings, matching how the nine
shipped classes were fitted.

⚠️ **Two different statistics carry the name `living_dining_kitchen` and both are
right.** The class `target` here is **37.11**, the median of the per-dwelling
**sum**. `corpus_medians.living_dining_kitchen` is **36.5**, the sum of two
**independent** medians. They are 1.7 % apart, they answer different questions —
the first exists only to define `k`, the second is §9.2 rung 2 — and they must
not be reconciled into one number.

⚠️ **`soft_w` for `living_dining_kitchen` is published at 1.00, not 1.01.** Its
CV of 0.2277 lands marginally below the normalisation anchor, but the anchor
back-solved from the nine shipped cells spans 0.2275–0.2320, so it **ties** the
tightest class rather than displacing it. Re-normalising nine ADR 0023 values on
a 0.8 % difference would be a re-fit, and this ticket does not do those.

### 12.5 `k × target` is a cross-provenance product, and it inverts

⚠️ **Named here, not fixed here.** `k` is a ratio fitted about a **CH** class
median; `target` is an **AZ** number. Their product is the class's p99.5 only
where the two agree, and across the seven types taking this limb it runs **62 %
to 114 %** of the class's own `absolute_cap`. The visible symptom is an
inversion:

| type | bound | class `absolute_cap` |
|---|---:|---:|
| `living` | 2.35 × 17.6 = **41.4 m²** | 48.12 |
| `living_dining` | 2.02 × 17.6 = **35.6 m²** | 57.12 |

**The room that contains a dining area caps smaller than the one that does not.**
Both read the same AZ target (`living_room_2plus`, 17.6) because
`living_dining`'s `az_area` guard resolves there with `referent: undetermined`,
while their `k` were fitted about Swiss medians of 20.51 and 28.32.

Neither limb is ticket 71's to move — the target belongs to ADR 0035's market
tier and `k` to ADR 0023's fitted set — so it is measured, named and ticketed.

### 12.6 The C14 lever, closed

`az-market-default-against-practice.md` §14 recorded an unowned lever and handed
it here: **raising a profile `market_default` raises a hard cap**, and C14
authorises a profile to raise a *floor* while saying nothing about loosening a
*cap*. Settled without amending C14, because the rule has **two limbs of
different character**:

- **`k × target_area`** is a *proportionality band around a requested size*. It
  moves with the request **by design**, identically whether the request came from
  a Homeowner (C4, sovereign — §6.1's own *a stated target is sovereign*) or from
  the profile's measured practice (ADR 0035, may only move up, floored by
  regulator recommendation). C14's guarantee never attached to a band around a
  number the Brief itself supplies.
- **`absolute_cap`** is the region-free outer bound, and **no profile touches
  it**. This is where C14's *no profile may weaken a predicate* lives.

What makes that safe rather than merely asserted is a **build-time gate**, owed
to `experiments/region-profile/gate_check.py` and not written here: for every
profile cell feeding `dim.market_default_area`, `market_default ≤ absolute_cap`
of the class its ergonomic key resolves to. **Run over the 11 profile cells, all pass**, and the
tightest is `kitchen` at 9.0 / 20.59 = **2.29×**, then `bedroom_principal` and
`bedroom_double` at 13.2 / 31.09 (2.36×) and `bathroom_combined` at 3.8 / 9.15
(2.41×). ⚠️ `bedroom_principal` is only checkable because §12.2 resolves it; before
the map it had no class to look a cap up in, which is the defect one layer down.

`dim.stated_target_implausible` is widened from *a **stated** target* to **any
target, whichever rung of §9.2's ladder supplied it** — the check is about the
number, not its provenance, and the narrow reading left uncovered the one
provenance a Homeowner cannot correct. Severity stays `warn` and scope stays
`brief`. Scope correction, not a new rule: `rule_count` stays **43**.

### 12.7 ADR 0037 was under-scoped, and the corpus cost has a footnote

⚠️ ADR 0037 published the third vocabulary after finding it living in the
comments of four Python dicts in `experiments/warp/`. **Two more private copies
sit in `experiments/acceptance-thresholds/`** — `reject.py`'s `ERG`, `ABS_CAP`
and `classify_parts`, and `census.py`'s `COLLAPSE` — and their class keys
**disagree with the shipped table**: `living` and `storage` against `living_room`
and `storeroom`. `reject.py` also carries `EXEMPT_ASPECT = {corridor, hall,
storage}`, naming a `hall` the corpus cannot produce.

⚠️ **`dim.max_area`'s published `corpus_cost: 0.0311` was measured with
`kitchen_dining` silently exempt.** `ABS_CAP` has no entry for it and the guard
is `if cap is not None`, so the branch never ran on those rooms — the same
silent-pass this section is about, inside the rig that priced the rule. The
population is **40 rooms in 40 dwellings, 0.093 %** of the in-band census, so
**the number survives and its provenance does not**. Re-run when someone next
holds that directory; do not re-quote 3.11 % as though the eleven-class table
produced it.

⚠️ Neither file is edited here. Ticket 71 holds `rules.json` and this document,
declares `room-constraints.json` on resolution, and hands the rigs on as prose —
the same discipline 69, 73 and 74 used.
