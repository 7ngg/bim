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

Within one dwelling, mean private hop against mean social hop: private further
**65.4 %**, equal 18.5 %, **private nearer 16.1 %**. A rule saying bedrooms sit
further from the door than the living room rejects one real home in six. The
gradient is real and it is not a predicate.

### 2.3 What the front door opens onto

**93.2 %** circulation, 3.6 % social, 2.0 % private, 1.1 % kitchen, 0.2 % wet.

This is the first hop of the sequence property, and it needs none of the
machinery the rest of the sequence needs — it is a statement about one Space.

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
whole point of D2. `gate_check.py` should gate the divergence from `is_private`
the way it already gates `counts_as_otaq` against `is_habitable`: the sets differ
on exactly `bathroom`, `shower_room`, `wc`.

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

## 6. Reproducing this

```
./venv/Scripts/python.exe experiments/zoning/measure_zoning.py 2500
./venv/Scripts/python.exe experiments/zoning/report.py
./venv/Scripts/python.exe experiments/zoning/measure_zoning2.py 2500
./venv/Scripts/python.exe experiments/zoning/report2.py
./venv/Scripts/python.exe experiments/zoning/sensitivity.py
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
