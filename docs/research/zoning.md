# Zoning — where a set-versus-set property lives

Ticket 30, *The Proposal cannot express zoning*.
Harness: `experiments/zoning/`. Corpus: Swiss Dwellings v3.0.0, 2 500 measured
dwellings per pass, deterministic by key hash.

---

## 0. The word

**"Zoning" is not used as a system term, and this document is the only place it
appears.** Every product in `competitive-landscape.md` uses *zoning* for
land-use control — FAR, setbacks, 日影規制 shadow law, Zoneomics data. That is a
different subject from the one this ticket names, and a system that used one
word for both would be unreadable to anyone from the industry.

The canonical term is **[[Sleeping group]]**, chosen to sit beside the shipped
**Plumbing group**, because it turned out to be the same object.

---

## 1. The ticket's premise is half wrong, and that halves the problem

The ticket opens: *"Everything this system optimises is pairwise, and the
property architects rank plans by is not."*

The first clause is false, and the counter-example is shipped.
`solver-formulation.md`:

> The same routine, instantiated over the wet-room subset with no blocked nodes,
> gives H9 wet-room clustering — one plumbing-connected cluster rather than
> scattered bathrooms. Writing it once and calling it twice is not an
> optimisation; it is **the observation that "reachable" and "clustered" are the
> same constraint with different node sets.**

And `rules.json` carries `wet.plumbing_group_count`, hard, `site: both` — *"the
wet Spaces form at most two plumbing groups"*. That is a set against a set,
posted as a constraint and checked as a predicate, today.

**The Proposal is pairwise. The system is not.** The ticket was written from
`CONTEXT.md`'s **Adjacency wish / Adjacency veto** note — *"Neither can express a
set against a set"* — which is true of that field and was read as true of the
engine.

So the four properties the ticket names do not share a price:

| property | shape | machinery |
|---|---|---|
| day/night grouping | clustering over a node set | **exists** — the flow routine, a third node set |
| served and servant | clustering over a node set | **exists** — same |
| facade allocation | ranked claim on a scarce resource | **exists** — a soft term over the Envelope's typed edge ring |
| sequence (entry → hall → living) | *order* on the circulation graph | **does not exist** — needs per-Room hop-count integers |

Three of four are node-set instantiations of routines already written. One is
not, and §6 prices it.

---

## 2. What the corpus shows

> ⚠️ **RE-MEASURED 2026-08-31, and one published figure moved.** *Land the
> sleeping flag and retire the private corpus-label copies* (ADR 0044) replaced
> `measure_zoning.CLASS` — a private copy of the corpus-label projection that
> **did not map `KITCHEN_DINING`** — with a read of the published bridge. Three
> rooms in three dwellings of the 2 500 move `other → social`. The rig is
> deterministic (md5-keyed ordering, no `hash()`, no solver), and the re-run
> reproduces the skip counts exactly: 1 206 / 126 / 144 / 144 / 6.
>
> | figure | was | is | moved? |
> |---|---:|---:|:--|
> | §2.1 sleeping groups, 1 / 2 / 3 | 69.8 / 27.7 / 2.5 % | **69.8 / 27.7 / 2.5 %** | no |
> | §2.2 mean hop, further / equal / nearer | 65.4 / 18.5 / 16.1 % | **65.3 / 18.5 / 16.3 %** | yes, n 1 756 → 1 759 |
> | §2.4 longest exterior run to social | 73.7 % | **73.7 %** | no (1 294/1 756 → 1 297/1 759) |
> | §2.5 social transit, per sleeping Room | 11.1 % (666/5 990) | **11.1 %** | no |
> | §6.5 min hop, tie / inverted | 51.0 / 17.4 % | **50.9 / 17.5 %** | yes |
>
> **The one that matters downstream is the inversion rate**, because `proposer.md`
> §6.1 term 5 and ADR 0042 quote it as a **ceiling**: **17.4 % → 17.5 %**
> (305/1 756 → 308/1 759). Stratified by habitable-room count, 12.3 → **12.5** at
> 3 and 15.0 → **15.3** at 5; 21.9 % at 4 is unmoved. The move *loosens* the
> ceiling by a tenth of a point, and its cause is three dwellings acquiring a
> social Room they always had. ⚠️ `proposer.md` has two claimants (67, 81) and is
> not this ticket's to edit — the correction is recorded here, where §6.1 already
> cites its provenance, and on the map's conflict-table row.


`experiments/zoning/measure_zoning.py`, `measure_zoning2.py`. Room classes follow
`CONTEXT.md`'s **Private room** and `proposer.md` §4.1's collapse of
`{ROOM, BEDROOM, STUDIO}`: *private* is the sleeping set, *social* is
`LIVING_ROOM / LIVING_DINING / DINING`.

Contact, not doors — `measure_swiss.contact_graph`, τ 0.30 m, run 1.00 m. That is
**potential circulation**, the layer the solver constrains.

### 2.1 Sleeping groups — the finding the decision rests on

Components of the private set, where two private Rooms are one group if they
touch **or share a circulation neighbour** ("off the same hall" is grouped;
bedrooms rarely touch). Of 1 989 dwellings with two or more private Rooms:

| groups | dwellings | share |
|---:|---:|---:|
| 1 | 1 388 | **69.8 %** |
| 2 | 551 | 27.7 % |
| 3 | 50 | 2.5 % |

**At most two sleeping groups covers 97.5 % of real dwellings** — the same
sentence as `wet.plumbing_group_count`, reached independently and landing on the
same number. One group is *not* the rule: demanding it would reject 30 % of real
homes, the identical error `wet.plumbing_group_count`'s note already records
against wet clustering.

### 2.2 The day/night gradient is directional, not assertable

Mean hop distance from the entrance:

| class | mean | median |
|---|---:|---:|
| circulation | 0.32 | 0 |
| social | 1.21 | 1 |
| kitchen | 1.46 | 1 |
| wet | 1.54 | 1 |
| **private** | **1.66** | **2** |

Within one dwelling, mean sleeping hop against mean social hop: sleeping further
**65.3 %**, equal 18.5 %, **sleeping nearer 16.3 %** (n = 1 759; was 65.4 / 18.5 /
16.1 over 1 756 before ADR 0044's `KITCHEN_DINING` repair). A rule saying bedrooms sit
further from the door than the living room rejects one real home in six. The
gradient is real and it is not a predicate.

✅ **Refined by §6.5, and the refinement is the number a rule would cost.** The
16.3 % above is *mean* against *mean*. On the **minimum** each side — what a rule
binds, since it binds the nearest offender — it is **17.5 %**, and the fact this
section missed is that **50.9 %** of dwellings are a **tie**. The gradient is not
only unassertable, it is *absent* in half the population.

### 2.3 What the front door opens onto

**93.2 %** circulation, 3.6 % social, 2.0 % private, 1.1 % kitchen, 0.2 % wet.

This is the first hop of the sequence property, and it needs none of the
machinery the rest of the sequence needs — it is a statement about one Space.

✅ **And in the engine it is not even that** — §6.4. `openings.md` §7 hosts the
primary entrance on the invented `hall` by construction, so the engine's rate is
**100 %**, not 93.2 %, and no predicate is owed. D6's *warn* stands for a Brief
that overrides the default, not for the default.

### 2.4 Facade: the pass-1 measurement was the confound

Pass 1 measured each Room's **share of the outer boundary**, normalised by area
share, and found social rooms hold *less* facade per m² than private ones
(0.93 against 1.05) — which read as a refutation and was reported as one.

**The normalisation was wrong.** "The living room gets the best elevation" is a
claim about an **absolute, indivisible, scarce** resource, not about daylight per
square metre — and daylight adequacy already has two rules,
`win.habitable_has_window` and `win.area_ratio`. Measured absolutely:

| class | mean elevations | dual-aspect | longest single run | mean m² |
|---|---:|---:|---:|---:|
| social | 1.20 | **19.9 %** | **12.24 m** | 26.1 |
| private | 1.08 | 8.2 % | 8.22 m | 14.7 |
| kitchen | 1.05 | 7.7 % | 5.78 m | 8.5 |
| wet | 0.94 | 4.9 % | 3.55 m | 3.8 |

Per dwelling, the best social Room beats the best private Room on the **longest
single exterior run 73.7 % to 26.3 %, with no ties**. Dual aspect — two
elevations more than 20° apart — is **2.4× more common** for a social Room.

Both quantities are **topological**: they read the Envelope's typed edge ring
(ADR 0003) and need no site, no orientation and no solar model, all of which the
map has ruled out of scope. 73.7 % is a gradient, not a floor.

### 2.5 Social transit — a rule nobody had written

`circ.no_private_transit` blocks routing *through* a private Room. **Nothing
blocks routing through the living room**, which is the plan-reads-amateur
signature. Measured as a cut set — is every path from the entrance to this
bedroom through a social Room?

**11.1 %** of private Rooms (666 of 5 990), in **18.2 %** of dwellings.

It does **not** concentrate in corridor-less small flats, which was the
hypothesis:

| engine rooms | dwellings | with such a bedroom |
|---:|---:|---:|
| 4 | 110 | 0.0 % |
| 5 | 354 | 19.8 % |
| 6 | 527 | 14.4 % |
| 7 | 505 | 17.6 % |
| 8 | 506 | 16.8 % |
| 9 | 311 | 28.0 % |
| 10 | 99 | **35.4 %** |

It **rises** with dwelling size. ⚠️ The "without circulation → 1.0 %" cell in
`report2.txt` is an **artefact** and must not be quoted: the cut test excludes
dwellings whose entry Space *is* the social Room, which is most corridor-less
plans.

18.2 % is far too expensive to be hard — compare *Ergonomic minima*, where
rejecting 36 % of real bathrooms was treated as a failed derivation, and ADR
0009, which took a 23 %-against-56 % rejection trade seriously enough to exempt a
whole layer.

---

## 3. One measurement that cannot support a rule, and is reported anyway

The obvious candidate rule — **every private Room touches circulation** — holds
for 53.3 % of private Rooms and 26.6 % of dwellings at the shipped 1.00 m contact
run. It is **threshold-dominated**:

| contact run | private Rooms touching circulation | dwellings, all of them |
|---|---:|---:|
| **1.00 m** (shipped) | 52.9 % | 27.0 % |
| 0.80 m | 66.2 % | 43.3 % |
| 0.60 m | 78.4 % | 62.0 % |

The direction is real; the level measures the threshold, not the architecture.
Same confound class as H8's *"dead from 7 rooms"*, which measured
`envelope_for(n)`'s shape choice rather than n. **No rule rests on it.**

⚠️ Related and unresolved: **29 % of real dwellings come out disconnected** on
the contact graph at 1.00 m. Confounded by the buffer method used here, so it is
not called a defect — but if it survives a cleaner measurement,
`circ.potential_reachability` over-rejects real homes. Handed to
*Look at the converted corpus* and *Re-measure the conversion at two rectangles
per Room*, which own the conversion.

---

## 4. What the market does

`competitive-landscape.md`, eleven products. Every one that models Room
relationships at all models them as **adjacency**, **user-authored**, and
**soft**:

- **Synaps** — a sketched bubble diagram, *"a soft constraint… a directional
  prior, not a template"*; it *"reasons about spatial fit, adjacencies, light,
  and circulation"*.
- **Finch** — *"user-authored graph rules"*; users *"specify requirements such
  as minimum square footage, daylight minimums, and spatial relationships"*.
- **Snaptrude** — "AI Adjacency", "auto-adjacencies from building codes".
- **Digital Blue Foam** — "clinical adjacency rules".
- **ARCHITEChTURES** — adjacency in a typed program table.

**No surveyed product asserts a set-versus-set property, and none claims day/night
separation.** Two things follow.

First, this is a differentiator on the same line as C3: unglamorous, and nobody
has done it.

Second — and this is why the market's answer cannot be copied — **every one of
those products sells to a practitioner**, who can draw a bubble diagram. C2's
buyer cannot. A user-authored adjacency graph is the correct interface for their
user and the wrong one for ours, which is §5.

---

## 5. Decisions

### D1 — Zoning is **inferred from Room type**, never a Brief field in v1

A Homeowner does not ask for day/night separation; they notice its absence. A
Brief field makes the *default* output the unzoned one, which is backwards for
C2's buyer, and it asks the Homeowner for the one thing §4 shows the whole market
only ever asks an architect.

It costs almost nothing: the node set is a Room-type flag, beside the four that
already ship (`is_habitable`, `is_private`, `counts_as_otaq`, `brief_nameable`).

### D2 — The node set is a **new flag**, and it may not be `is_private`

`room-constraints.json` sets `is_private: true` on `bathroom`, `shower_room` and
`wc` as well as the four sleeping types. That is **correct** for
`circ.no_private_transit` — you should not route through a bathroom either — and
it is **wrong** for a sleeping group, which would silently acquire the bathrooms.

⚠️ `CONTEXT.md`'s **Private room** entry reads *"a Brief's bedroom, study or
nursery, as one class"*, which is the narrow set and does not describe the
shipped flag. Two sets, one word — ticket 31's defect, one file over. The
glossary is corrected here; the flag is not renamed, because the rule that reads
it is right.

The new flag is **`is_sleeping`**, true on `bedroom_principal`, `bedroom_double`,
`bedroom_single` and `study`.

### D3 — Grouping is a **hard bound on the count, plus a soft gradient inside it**

Precisely `wet.plumbing_group_count` + `wet.shared_wall_length`, whose note
already argues this case: *"A bound on the group COUNT stays postable as a hard
constraint and matches the shape real dwellings take."*

**At most two sleeping groups**, `site: both`, hard. Soft gradient: prefer fewer.

⚠️ **State the limit honestly.** 97.5 % of *real* dwellings already pass, so as a
filter the hard bound barely binds. Its value is insurance against a generator
nobody has run — **no Proposer exists, so the violation rate of generated plans
is unmeasured**. The soft gradient is where the work happens, and if the bound
turns out to bind on real output the number is refittable without reopening this
decision.

### D4 — Facade allocation is **soft**, and it is reinstated

Prefer the longest single exterior run, and dual aspect, to go to a Room that is
habitable and not sleeping. 73.7 % and 2.4× are gradients, not floors.

### D5 — Social transit is **soft**, and it is new

Prefer that no sleeping Room is reachable only through a social Space. 18.2 % of
real dwellings violate it; hard is unaffordable.

### D6 — The front door opens onto circulation: **warn**

93.2 %. Hard rejects 6.8 % of real homes for a property that is a courtesy, not a
floor. `warn` is the severity `win.kitchen_windowless` already uses for exactly
this shape of claim.

### D7 — Ordered sequence is **out of v1**, and it is the only one that needed
new technology

Entry → hall → living as an *ordered path* needs per-Room hop-count integer
variables the single-commodity flow does not produce; every solver number on the
map was fitted without them, and the flow encoding was chosen partly because it
needs *"no auxiliary integers"* (H8's note). Its cost is unmeasured and the rig
that would measure it is `experiments/solver-toy/`, which ticket 29 claims and is
about to change. Ticketed, blocked on 29.

✅ **Settled, and the cost was never the deciding question** — §6, ticket 43.
The rig was freed (ADR 0019 moved nothing) and the encoding was then **refused on
the corpus before it was priced**: of the three readings this decision left open,
two are the *negation* of the slogan they encode, the third is a construction
`openings.md` §7 already ships, and the only reading that needs the integers is a
**tie in 50.9 %** of real dwellings and inverted in **17.5 %**. **No hop-count
integer is owed and the H-list closes at H10.** D7's verdict stands; its stated
reason — *cost unmeasured* — does not, and should not be quoted, because the cost
was never reached.

### D8 — **The Proposal contract gains no field, and that is the decision**

ADR 0014 put *shape* in the Proposal on a measured argument: told which Room is
an L the solver places 25 of 25; left to find them it places 10 of 18 and invents
35. **That argument does not transfer.** L-ness is a property of the truth being
copied and only the Proposal knows it. A sleeping group is a property of **Room
type**, which the `ResolvedBrief` already carries — so the solver derives the node
set itself and there is nothing the Proposal could tell it that the Brief has
not.

`proposer.md` §1 records the refusal *with* this reasoning, so the next reader
does not reopen it as an oversight.

### D9 — What zoning *does* change in the Proposer spec is **evaluation**

Ticket 24 established that the arrangement metric predicts **feasibility, not
survival**, and is *"a training and evaluation instrument only"*. The map's
*Plan quality beyond the validator* patch has wanted a plan-quality signal and
had none.

Sleeping-group count, longest-run allocation and social transit are all
**computable on a corpus dwelling and on a generated Plan by the same code** —
which is exactly what a held-out evaluation term needs and what corner
displacement is not. `proposer.md` §6 takes them.

### D10 — The day/night gradient is an **evaluation term**, and §2.2's *directional, not assertable* was only half the finding

§2.2 stopped at *the gradient is real and it is not a predicate*, and D7 read
that as *therefore out of v1*. §6.6 measures the step that was skipped: the
gradient is not merely unassertable, it is **invisible to the three terms D9
shipped**. Entry-depth inversion against social transit over the same 2 500
dwellings is χ² = 34.55, p ≈ 4.2 × 10⁻⁹, odds ratio **0.354** — *negatively*
associated, 38 dwellings carrying both where 78.9 are expected under
independence. **15.2 %** of dwellings invert the gradient with no transit defect
at all.

So the property has a home, and it is neither a constraint nor nothing: a
**fifth `proposer.md` §6.1 plan-quality term**, scored against the corpus
**rate** rather than a threshold, in the shape the other four already take.
The quantity is the **inversion rate** — the fraction of dwellings whose nearest
sleeping Room sits strictly nearer the entrance than its nearest social Room —
real **17.5 %**. Not the strict-order rate: a model that ties everything and a
model that reverses everything both score 0 % strict, and the corpus is 50.9 %
ties, so a strict rate cannot tell the two apart.

It qualifies on D9's own property — computable on a corpus dwelling and on a
generated Plan by the same code, off the hop distance §2.2 already publishes.
**This file specifies it and does not write it**: `proposer.md` is claimed, so
the term is handed over as its own ticket rather than as a sentence here.

✅ **Taken, as `proposer.md` §6.1 term 5 — and three things D10 proposed were
wrong.** ADR 0042, *What the entry-depth gradient is worth as a fifth evaluation
term*. What it got right is the part that mattered: the property is real, it is
unowned, and term 3 cannot see it. What it got wrong:

- ⚠️ **"Scored against the corpus rate" is refused; the rate is a CEILING.**
  D10 asked to *match* 17.4 % while §6.5 calls the − bucket a **violation**, and
  those cannot both stand — matching rewards producing as many bad plans as real
  housing. Neither standards lineage supports matching. СП 54's Table 5.1 note and
  ЖК РФ art. 50 §2 do index a threshold to observed stock, but as a **one-sided
  minimum on a quantity where more is better**, which *rises* as practice improves;
  transplanted onto a defect rate that is a ceiling and never a target. WBS 2015
  went further and added a **maximum** net floor area in its 2015 revision because
  Swiss areas were rising — **the bar moved against the stock**, which a
  distribution-matching instrument cannot do.
- ⚠️ **The private/social sets are `is_sleeping` and `is_habitable ∧ ¬is_sleeping`,
  and the second needs no new flag.** D10's item 3 feared the term "quietly adds a
  second one". It does not: that construction is the one `zone.no_social_transit`
  and `zone.facade_to_living` already use. Plain `kitchen` stays out, which the
  measurement in §2.2 already assumed — `KITCHEN` is its own class there, in
  neither set.
- ⚠️ **The pooled 17.4 % must never be quoted alone.** By habitable-room count it
  is **12.3 / 21.9 / 15.0 %** at 3 / 4 / 5 and the tie mass runs **30.8 → 67.3 %**,
  monotone — a large dwelling is hall-centred and everything sits at equal depth.
  §6.5's three-bucket split is therefore a **mixture over the corpus's size mix**,
  and a generated population with a different Brief mix would score as deviating
  while being perfectly zoned. This is Hillier's own acceptance test, failed.
  House-GAN++ publishes the fix and it is the one taken: stratify, never pool.

✅ **And one thing D10 could not have known, which argues *for* it.** The benign
reading — that a shallow private Room is a front-office or guest room, a
*desirable* pattern Alexander's Patterns 141 and 157 place at both ends of his own
gradient — is testable and **fails**: the shallow Room in an inversion is a
terminal cell in **4.9 %** of cases against **26.5 %** when ordered, the opposite
of the front-office signature. The corpus's inversions are bedrooms off the hall.
`docs/research/plan-quality-metrics-in-practice.md`.

---

## 5b. Handoff — what this ticket specifies and does not write

`rules.json` has four claimants (16, 20, 26, 42) and `room-constraints.json` two
(16, 32). This ticket claims **neither**, and the map's concurrency rule is a rule
about *files*, not about decisions. So the rows are specified here in full, ready
to transcribe, and whichever ticket next opens those files takes them — the
precedent set by *What a room's area is allowed to be* and *Two room vocabularies
in one file*.

**To `room-constraints.json`'s holder — one flag.** `is_sleeping`, beside the four
that ship. True on `bedroom_principal`, `bedroom_double`, `bedroom_single`,
`study`. False on everything else, **including every wet type** — that is the
whole point of D2. `gate_check.py` should gate the divergence from `is_private` the way it already gates
`counts_as_otaq` against `is_habitable`: the sets differ on exactly
~~`bathroom`, `shower_room`, `wc`~~ — **four types, not three**.

✅ **LANDED, and this paragraph was one type stale when it landed** — ADR 0044.
`bathroom_combined` is `is_private: true` and is not a sleeping room, so the
divergence is `bathroom`, `bathroom_combined`, `shower_room`, `wc`. It did not
exist when this was written: ADR 0022 added it as the nineteenth type afterwards.
A holder transcribing this paragraph verbatim would have shipped a gate that
fails. `gate_check.py` Z6 asserts the four.

⚠️ **And one flag was not enough.** Retiring `measure_zoning.py`'s private label
table needed a *second* new bit, `is_circulation`: `hall` and `storage` carry
identical vectors over all six older flags and belong in different classes, so no
precedence over those six separates them. It is also exactly this section's own
three-name literal list in `entry.opens_onto_circulation`, which reads the flag
instead. ADR 0044.

**To `rules.json`'s holder — four rules.** `item` numbers are for the holder to
assign against `acceptance-bar.md`'s own sectioning.

| id | severity | site | statement |
|---|---|---|---|
| `zone.sleeping_group_count` | **hard** | both | The Spaces whose Room has `is_sleeping` true form at most **two** sleeping groups, where a group is a maximal set connected by a shared WallSegment or by a shared circulation neighbour. |
| `zone.prefer_one_sleeping_group` | soft | both | Prefer fewer sleeping groups. |
| `zone.no_social_transit` | **soft** | both | Prefer that no Space whose Room has `is_sleeping` true is reachable from the entry Space only by paths traversing a Space whose Room is habitable and not sleeping. |
| `zone.facade_to_living` | soft | validator | Prefer that the longest single exterior run of the Envelope's edge ring is held by a Space whose Room is habitable and `is_sleeping` false. |
| `entry.opens_onto_circulation` | **warn** | validator | Warn when the entry Space's Room is not `hall`, `entrance_lobby` or `corridor`. |

Each carries `src: engine_choice`, `conf: derived` — every threshold is measured
here, none is quoted from a standard, and AzDTN says nothing about any of them.
Provenance for the numbers is `docs/research/zoning.md` §2 and the harness in
`experiments/zoning/`.

⚠️ Note for whoever takes them: `zone.sleeping_group_count` is the *only* hard one,
and §5's D3 states plainly that at 97.5 % real coverage it barely binds. Do not
fit it against the corpus and conclude it is doing nothing — it is insurance
against generated output nobody has produced yet. The soft four carry the work.

⚠️ And a **locale** note, inherited not created: `acceptance-bar.md` §11 requires a
plain-language message per rule, all existing 38 are English, and the Homeowner
surface is Azerbaijani. These five arrive with the same debt as the other 38 and
must not be given English-only messages that deepen it.

---

## 6. The entry sequence, measured — and refused before it was priced (ticket 43)

D7 ticketed *entry → hall → living* as the one property of the four that needed
technology this formulation does not have. The ticket asked three things in
order: **what the property is**, **what it costs**, and **whether the corpus
supports it**. Answering the third made the second moot.

**The outcome is the one the ticket named itself as genuinely open to — no new
solver machinery is owed — but it collapses a *third* way.** Not into a cheap
predicate over the existing graph, which is what the ticket predicted. Into a
construction that is already shipped, plus a distribution no constraint may
assert.

### 6.1 The plane, and why a refutation here is a refutation where it counts

`dist` is BFS from the located entry over `measure_swiss.contact_graph`
(τ 0.30 m, door run 1.00 m). `solver-formulation.md` reifies `door_ij` as *"true
exactly when the two rooms share a wall segment at least a door's width long"* —
**the same layer**. A rule refuted on this graph is refuted on the graph it would
have been posted on.

⚠️ One residual, and its direction is stated because it does not rescue anything.
Contact ⊇ realised doors, so a contact hop **understates** how far a person
actually walks. That matters if you read these numbers as *walking distance*; it
does not matter for the decision, because the constraint would be posted over the
contact literals, where the match is exact — and a rule forbidding *contact*
between the entry and a habitable Room is strictly harsher than one forbidding a
*door*.

### 6.2 The three readings, over the same 2 500 dwellings

| candidate | holds | needs `d_r`? |
|---|---:|---|
| **R1** no otaq at hop 1 | **9.6 %** | no — one existing literal |
| **R1h** no habitable Room at hop 1 | **1.8 %** | no |
| **R2** every otaq at hop ≥ 2 | **7.7 %** | no |
| **R2h** every habitable Room at hop ≥ 2 | **1.6 %** | no |
| **R5** every private Room at hop ≥ 2 | **25.1 %** | no |
| **R3** circulation nearer than any social Room | 96.8 %† | no — ≡ §6.4 |
| **R4** nearest private ≥ nearest social | **82.6 %**† | **yes** |
| **R6** strict entry < social < private | **26.9 %**† | **yes** |

† on the population where both class sets are present (68–70 % of dwellings).

"hop ≥ 2 from a **fixed** node" is not a hop count: it is exactly
`door_{entry,r} == 0`, one literal H6 already reifies. Only R4 and R6 need a
per-Room integer.

### 6.3 R1 and R2 are the negation of the slogan they were written to encode

The nearest social Room sits at hop **1** in **73.4 %** of dwellings — the modal
case by a factor of four.

| nearest social Room at | share |
|---|---:|
| hop 0 (it *is* the entry) | 5.1 % |
| **hop 1** | **73.4 %** |
| hop 2 | 18.8 % |
| hop 3+ | 2.7 % |

*Entry → hall → living* **means the living room is at hop 1**. R1 and R2 forbid
precisely that. Stated positively, the slogan already holds on **72.9 %** of
dwellings with a social Room, with no rule posted by anyone.

And there is no buffer to assert even if you wanted one — what actually sits at
hop 1 from the entrance is dominated by the rooms a buffer rule exists to push
away:

| class at hop 1 | share of all hop-1 Rooms |
|---|---:|
| private | 33.9 % |
| wet | 28.1 % |
| kitchen | 16.8 % |
| social | 15.2 % |

### 6.4 The first hop is not a predicate — it is a construction, and it is shipped

§2.3 measured 93.2 % of real front doors opening onto circulation and called it
*"a statement about one Space"*. It is less than that in the engine, and better.
`openings.md` §7: **"The hall exists to be the room the front door opens into."**
`resolve` invents exactly one `hall`, the primary entrance is hosted on its
segment on an `entrance_side` edge, and a candidate whose hall does not touch one
*"is already dead at `entry.exists`, before this rule is consulted"*.

The engine's rate is **100 % by construction** against the corpus's 93.2 %. R3 is
that fact restated and carries no information beyond it.

### 6.5 The one reading that needs integers is a tie half the time

`d(nearest private) − d(nearest social)`, over the 1 756 dwellings holding both:

| gap | share | |
|---|---:|---|
| − (private **nearer**) | **17.4 %** | violation |
| 0 | **51.0 %** | tie |
| + (private further) | **31.6 %** | strict order |

**Half of real dwellings say nothing at all.** A per-Room hop-count integer would
buy a relation the population is silent on in 51.0 % of cases and contradicts in
17.5 % — one in **5.7**, against the ticket's own stated bar of *"a rule real
dwellings break one time in six is not worth new integers"*.

⚠️ **This refines §2.2 and does not restate it.** §2.2's 16.3 % compares the
dwelling's *mean* sleeping hop to its *mean* social hop. This is the **minimum**
on each side — the quantity a rule would actually be posted on, since a rule
binds the nearest offender. Same signal, 16.3 % → **17.5 %**; quote the mean-based
figure for the gradient's *shape* and this one for any rule's cost.

### 6.6 The three shipped terms do not capture it, and they are *anti*-correlated with it

The judgement D7 deferred — *whether the three cheap properties already shipped
capture most of what "reads as designed" means* — is **false**, and now measured
false. Entry-depth inversion against **social transit** (D9's term 3), joined on
key over the same 2 500 dwellings:

| | transit 0 | transit 1 | total |
|---|---:|---:|---:|
| **inversion 0** | 1 035 | 416 | 1 451 |
| **inversion 1** | **267** | **38** | 305 |
| total | 1 302 | 454 | 1 756 |

χ² = **34.55** (Yates 33.71), df 1, **p ≈ 4.2 × 10⁻⁹**, odds ratio **0.354**.
Expected under independence in the both-cell: **78.9**; observed **38**.

They are not merely different properties — they are **negatively** associated,
and **15.2 %** of all dwellings invert the gradient while showing no transit
defect whatever. Term 3 is structurally blind to them: social transit is a
*routing* property (is this bedroom reachable only through a social Space) and
inversion is a *distance* one (is this bedroom nearer the door than the living
room). A bedroom opening straight off the entry hall is an inversion and is not
transit.

⚠️ **Two rates, two denominators.** §2.5 and `proposer.md` §6.1 quote social
transit as **11.1 %**, which is *per sleeping Room* (666 / 5 990). The 454 above
is *per dwelling*, and 454 / 1 759 = 25.8 % because the table is restricted to
dwellings holding both a sleeping and a social Room. `report2.txt`'s 18.2 % is the
same 454 over all 2 500. Do not put any two of these three in one sentence.

That is D10.

### 6.7 What the market does, re-checked for this question

Nothing in the reviewed stack posts an ordering constraint, and the reason is
structural rather than an omission: Graph2Plan and HouseDiffusion are
**conditioned on a supplied access graph** — the user hands them the bubble
diagram, so privacy depth is an *input*, never solved for and never scored.
§4's finding for adjacency holds unchanged for order: *user-authored, and soft*.
Nobody is measuring this, which is consistent with D9's premise and is not an
argument against D10.

✅ **Re-checked a third time, against the human standards rather than the tools,
and the finding widens rather than moves.** Not only does no generator score this
— no *regulator* does either, in either shipping lineage. СП 54.13330.2022 cl. 5.6
and AzDTN 2.7-2 cl. 5.9 forbid a bedroom being **on the path**; neither constrains
**depth from the entrance**. WBS 2015 does not score zoning at all. So the
statutory half of the gradient is term 3 and is already a hard rule; **the ordering
half has no backing anywhere**, which is exactly why it is a term and not a rule —
and why it ships `conf: derived`, never `verified`.
`docs/research/plan-quality-metrics-in-practice.md` and
`docs/research/housing-quality-standards-as-bars.md`.

### 6.8 What §6 does not establish

- **The cost of a per-Room hop-count integer is still unmeasured**, deliberately.
  It was refused on the corpus before it was priced, so no figure exists and none
  should be invented. A general *"what an auxiliary integer costs this
  formulation"* number is a fair question and belongs to its own ticket against a
  fixture that is fixed first — not to this one.
- **The corpus is Swiss** (C5). The gradient's direction is not plausibly
  region-specific, and a 17.4 % inversion rate would need an implausible regional
  shift to become assertable, but the AZ rate is unmeasured like every other
  corpus rate on this map.
  ⚠️ **That argument was made for a RULE and must not be read across to the term
  as written.** A rate can be wrong for AZ without the direction shifting at all,
  and assertability is not the question a scored term asks. What actually limits
  the exposure is the **ceiling**: a ceiling only has to be *not worse*, where a
  matched target has to be *right*. ⚠️ And the 17.4 % is measured over
  **mixed-tenure** stock, where cl. 5.6 is the one standard that makes tenure
  decisive for this exact quantity — under a ceiling that is harmless, under
  matching Swiss tenure structure would have become part of the target.
- **The disconnection skip stands** (§3, §7): 1 206 dwellings dropped, biasing
  toward well-connected homes. It cannot plausibly move R1/R2 from 9.6 %/7.7 % to
  anything shippable, and its effect on the tie mass is unmeasured.

---

## 7. Reproducing this

```
./venv/Scripts/python.exe experiments/zoning/measure_zoning.py 2500
./venv/Scripts/python.exe experiments/zoning/report.py
./venv/Scripts/python.exe experiments/zoning/measure_zoning2.py 2500
./venv/Scripts/python.exe experiments/zoning/report2.py
./venv/Scripts/python.exe experiments/zoning/sensitivity.py

# §6 (ticket 43) -- all three read the JSON above, no corpus pass, seconds each
./venv/Scripts/python.exe experiments/zoning/entry_order.py
./venv/Scripts/python.exe experiments/zoning/entry_order2.py
./venv/Scripts/python.exe experiments/zoning/entry_depth_vs_transit.py
```

Outputs in `experiments/zoning/out/`. Sample is the first 2 500 measurable
dwellings in key-hash order, the ordering every other experiment on this map
uses.

⚠️ **Skip accounting, stated rather than buried**: of the dwellings examined to
reach 2 500, **1 206 were dropped as disconnected**, 144 had no entrance door,
144 no private Room, 126 fell outside 3–12 Rooms and 6 could not have their entry
located. The disconnection rate is §3's open question, and it biases this sample
toward well-connected dwellings — which, for §2.1, biases *toward* fewer groups
and therefore makes the ≤ 2 bound a **floor** on the true coverage rather than a
ceiling.
