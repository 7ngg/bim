---
id: 51
title: A third of real kitchens have no window and the engine may not draw one
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - docs/spec/proposer.md
  - experiments/corpus-smoke/
---

# A third of real kitchens have no window and the engine may not draw one

## Question

**`win.habitable_has_window` rejects 43.3 % of real Swiss dwellings, and 23.0
points of that is the kitchen alone.** The corpus is the retrieval pool and the
training set. Decide what the engine does about a population it is learning from
and may not reproduce.

Measured by *H8 and the single-aspect flat* — first per-room evaluation of this
rule against real dwellings. 561 dwellings, 2 169 window-needing rooms, 150 floors,
same seed as the exposure run:

| | no window on its own boundary |
|---|---|
| BEDROOM | 5.9 % |
| ROOM | 6.9 % |
| LIVING_DINING | 9.0 % |
| LIVING_ROOM | 20.0 % |
| **KITCHEN** | **31.0 %** |

Per dwelling: **23.0 % fail on the kitchen alone**, 20.3 % on a non-kitchen room.

**The number is not an artefact.** Attribution audit found **zero orphan windows**
— every window on a dwelling boundary is attributed to at least one room — and
1 031 of 3 179 attributed to more than one, which biases *toward* finding a
window. The windowless kitchens are not niches: median **6.8 m²**, and **84.7 %
adjoin a windowed habitable room**. That is borrowed daylight — the `taxca-metbex`
arrangement AzDTN names and `profiles.AZ.windows.kitchen_niche_windowless`
deliberately holds `false`, on the reasoning that every instrument granting the
exception conditions it on electric hob plus mechanical extract plus an apartment
class the Brief does not carry.

**The rule is not the thing to change.** AzDTN 2.7-2 cl. 9.12 is `verified` and
mandatory, corroborated for houses at 2.7-3 cl. 8.14, and a Baku flat with a
windowless kitchen is not sellable. *H8 and the single-aspect flat* refused to
weaken it and refused to relax H8 by type to buy the coverage back.

## What is actually undecided

*What a room's area is allowed to be* set its cap at p99.5 rather than p95 on the
argument that *"the corpus is the retrieval and training population, so a rejection
there is coverage lost"* — at **26.6 %**. This is **43.3 %**, and unlike a
percentile it carries **no threshold to move**. So the question is not where to put
a number, it is which of these the engine does:

1. **Filter the retrieval and training population** to dwellings that satisfy the
   shipped hard bar. Honest, and it is a second drop on top of ADR 0016's, which
   fought Swiss 30.70 % → 9.74 % and ResPlan 40.10 % → 6.40 %. Nobody has measured
   whether the two drops overlap or compound.
2. **Keep the donors and repair on warp.** ADR 0018 makes the warp a solve; adding
   a kitchen window is a *topological* change, not a dimensional one, so it is not
   obviously something a warp can do. This needs the retrieval side to say whether
   its repair reaches it.
3. **Keep the donors and let the bar reject.** Retrieval returns donors that cannot
   survive; the measured rate says roughly two in five. That is a yield question
   and it feeds *The Proposal-quality floor, and how often the fallback fires*.
4. **Model the borrowed-daylight kitchen**, which is what 84.7 % of the real cases
   are — an open kitchen zone of a windowed living space. `kitchen_dining` and
   `living_dining_kitchen` already exist in the table as habitable types with their
   own windows; this would be a *third* reading where the kitchen is a Room with no
   window of its own. ⚠️ It reopens `kitchen_niche_windowless`, which was held
   `false` with reasons, so it must beat those reasons rather than ignore them.

⚠️ **Check the label before acting on the split.** `ROOM` is 914 of the 2 169 and
is the corpus's generic habitable label; `LIVING_ROOM`'s 20.0 % is measured on only
105 rooms and may be a labelling effect rather than a real arrangement. The kitchen
figure rests on 549.

⚠️ **This bites the training corpus and the retrieval pool differently.** A
retrieval donor that fails the bar wastes one candidate. A **trained** Proposer that
learned windowless kitchens from 31 % of its data will propose them everywhere, and
`proposer.md` §6.1's three plan-quality terms do not measure daylight.

## Deliverable

A decision recorded in `docs/spec/proposer.md` covering both sources, with the
overlap against ADR 0016's existing drop measured rather than assumed.

---

## Resolution

**The corpus is admitted unfiltered on glazing, for both sources — because
glazing is not a property a donor hands over.** All four options are refused as
posed: each treats the donor's windows as something retrieval inherits, and the
engine overwrites them in every case. `docs/spec/proposer.md` §4.5, ADR 0025.

What replaces the filter is one index field and one ranking partition, on the
property the warp does inherit. **The population this ticket is about is 6.39 %,
not 43.3 %.**

### 1. The overlap the ticket demanded — measured, and it decides option 1

Paired on ADR 0016's own 2,600-dwelling sample, the only dwellings whose
conversion verdict is known. The conversion's refusal reproduces at **9.75 %**
against the published 9.74 %, which is the join's own check:

| | window PASS | window FAIL | total |
|---|---:|---:|---:|
| conversion **converts** | 1,413 | 902 | 2,315 |
| conversion **refuses** | 144 | 106 | 250 |

**They compound; they do not overlap.** Both refuse **4.13 %** against **3.83 %**
under independence — lift **1.08×**. Joint drop **44.91 %**, survive both
**55.09 %**, marginal cost on dwellings the conversion keeps **38.96 %**. ADR 0016
fought the Swiss drop 30.70 % → 9.74 %; option 1 hands back four times what that
bought. `experiments/corpus-smoke/window_rule_overlap.py`.

✅ **And no slope is restored** — window-fail runs 42.9 % at four rooms to 36.0 %
at ten, flat to *declining*, so ADR 0016's flattening survives.

### 2. Why all four options share a false premise

Three shipped documents, none written for this question:

- `proposer.md` §1 — a Proposal is **boxes**. *"No validity guarantee; no
  adjacency graph; no wall geometry."* No openings.
- `openings.md` §6.1 — the opening layer places **one window per Space**, on its
  longest `exterior`-condition run, **after** the solve.
- *H8 and the single-aspect flat* §4 — `win.habitable_has_window` sits at site
  `both`, so the **solver** posts the frontage budget hard: 1 100 mm kitchen,
  1 400 bedroom, 1 700 living.

⚠️ **This was already on the map and had been handed to this ticket by name.**
`acceptance-thresholds.md` §13: *"Both are opening-layer rules, placed after the
solve, so a candidate's prior of clearing the bar is set by a layer the Proposal
does not carry"* — addressed to this ticket and to *A donor's enclosed void
becomes area nobody asked for*. The resolution is that handoff worked out, not a
new claim. **Its other half is still open on 53.**

So: option 2 is mis-posed — nothing needs repairing on the warp, because the
opening layer already does it and is the only layer that could. Option 3 is
mis-described — the failure is not at the bar but **INFEASIBLE at the solve**, and
*"roughly two in five donors cannot survive"* is false.

### 3. The residue that is inherited, measured at index scale

`experiments/corpus-smoke/boundary_contact.py`, 46,565 dwellings:

| | dwellings |
|---|---:|
| hold a dark `needs_window` Room — the shipped rule's corpus cost | **38.55 %** |
| …and hold that Room **on the boundary**, where this engine glazes it | 33.17 % |
| hold a `needs_window` Room reaching **no** boundary | **5.88 %** |
| …or reaching less than the frontage budget the solver posts | **6.39 %** |

**86.04 %** of every dwelling the rule rejects is reglazed for free, and **88.36 %**
of the corpus's 12,717 windowless kitchens reach a wall. Per room the kitchen is
28.90 % dark and **3.54 %** landlocked.

### 4. Three published figures move, and one was this ticket's own warning

The ticket said *"check the label before acting on the split — `LIVING_ROOM`'s
20.0 % is measured on only 105 rooms and may be a labelling effect."* Checked, at
80× the sample. **It was.**

| | 561 dwellings | **46,565** |
|---|---:|---:|
| dwellings rejected | 43.3 % | **38.55 %** |
| kitchen alone | 23.0 pts | **21.64 pts** |
| `KITCHEN` | 31.0 % | **28.90 %** |
| **`LIVING_ROOM`** | **20.0 %** | **10.09 %** |
| `DINING` | not reported | **19.54 %** (n = 1,315) |

Restricted to h8's own population — floors carrying two or more dwellings — the
headline is 38.77 %, so the gap is **sample size, not population**.

⚠️ **`rules.json`'s `corpus_cost` 0.4519 is not contradicted and must not be
overwritten.** It is `acceptance-thresholds/`'s **raw** arm over 42,985
unconverted dwellings; its own leave-one-out puts the rule's contribution to the
bar at **15.97 points**. Three numbers, three questions. `acceptance-bar.md`'s
holder should say which is which — handed on, not taken here.

### 5. What retrieval owes: `frontage_reach`, ranked and not gated

A new index record field (§2.2.1): the minimum, over a dwelling's `needs_window`
Rooms, of the boundary run that Room holds ÷ the frontage budget posted for it.
A **partition** in the pre-rank at 1.0 (§2.2.4) — not a weighted term, because
§2.2.4 already refuses weights that cannot be fitted, and this needs none: the cut
is 1.0 because that is where the solver's own hard constraint sits. **No free
parameter, no fitted constant.**

⚠️ **Deliberately not following *The two-notch cap is now evidenced*'s
gate-then-rank precedent.** Worst-room IoU is a pure donor-fidelity fact.
`frontage_reach` is not: §2.2.6 records that the conversion knows boundary
**contact** and not `exterior`-versus-`party`, so it is **necessary and not
sufficient** — a joint fact about the donor *and* the Brief's Envelope. A gate
would claim what it does not know. Supporting: the residue is small, and a gate
thins hardest where ADR 0013 already calls the index tight — landlocked runs
**0.73 %** at three rooms to **10.91 %** at ten and **12.83 %** at twelve.

### 6. Source B — the ticket's own warning is false as stated

*"A trained Proposer that learned windowless kitchens from 31 % of its data will
propose them everywhere."* **§2.3's model has no window token** — two box slots
per Room and a presence token. The only thing it can learn from a windowless
kitchen is an **interior** kitchen, and that prior is **5.88 %**, not 31 %.

The training set is therefore not filtered either: a landlocked room is a fact
about real housing that the solver already refuses hard, and trading 5.88 % of a
corpus ADR 0013 calls thin to suppress a case the projection rejects anyway buys
nothing. Instead §6.1 gains a **fourth** plan-quality term — `frontage_reach` on a
generated Plan, by the same code, against the corpus's own 5.88 %. It is also the
answer to the ticket's *"§6.1's three plan-quality terms do not measure daylight"*:
now one does.

**ResPlan needs no separate decision.** Training-only (§4.3), and its schema does
carry a first-class `window` field — checked — but nothing above depends on the
donor's windows.

### 7. Option 4 refused again, and not for being small

⚠️ **It is the largest lever this ticket priced.** A borrowed-daylight exception
retains **91.47 %** of the index against 61.45 % as shipped — thirty points. It is
refused because **v1 has no producer and no consumer**: the engine glazes kitchens
itself, and no Brief can ask for a niche — there is no `taxça-mətbəx` Room type,
which ADR 0022 §4 already records as a partly unsatisfiable limb. A rule with
neither is a rule that cannot fire, and *H8 and the single-aspect flat* retired two
rules on that test.

⚠️ **And the evidence for it does not say what two documents read it as saying.**
This ticket and *H8 and the single-aspect flat* §6 both glossed *"84.7 % adjoin a
windowed habitable room"* as *"the `taxça-mətbəx` arrangement"*. **Adjacency is
not openness.** cl. 5.7's niche is a recess **open to** the room it sits in; a
separate kitchen with a **door** onto a windowed living room is a windowless
kitchen, which cl. 9.12 forbids outright. Swiss Dwellings ships the openings, so
`experiments/corpus-smoke/kitchen_niche_test.py` separates them in one direction —
of the 11,139 windowless kitchens adjoining a lit room, **5,227 (46.93 %) carry a
DOOR on that shared boundary**, and a niche has no door. The other 53.07 % is
**undetermined**, not confirmed: a missing door polygon is not evidence of an open
threshold. Nearly half is positively not a niche and nothing licenses reading the
rest as one. The statistic stands; **the gloss is withdrawn**, in both documents.

### 8. What this hands on

| obligation | to |
|---|---|
| **`frontage_reach` as a per-record field** — one intersection per `needs_window` Room, and the fit already holds both inputs. `boundary_contact.py` is the reference implementation. Joins the cut-line frame and per-pair relation provenance that file already owes | `experiments/rectangularise/fit_rects.py` — held by *The dwelling that is built on two angles* |
| **What `select_relations`' positive-cost filter actually posts.** §5's choice of a rank over a gate turns on it: a landlocked donor is only *provably* infeasible if the separations enclosing that Room survive selection. Measure it and the gate becomes arguable | `experiments/solver-toy/` — *What an ordered entry sequence costs the solver* and *The toy Envelope is more compact than a real dwelling* |
| **`win.habitable_has_window` has three corpus costs answering three questions** (§4). None wrong, none the others. Say which is which rather than let a reader take 0.4519 for the retrieval cost | `docs/spec/acceptance-bar.md` — no claimant |
| **The `taxça-mətbəx` gloss is withdrawn** — §6's "84.7 % are borrowed daylight" reading is not evidenced and nearly half is refuted | *H8 and the single-aspect flat* is closed; recorded here and in `CONTEXT.md` under **Borrowed daylight** so it is not re-inherited |
| **A named, unproven lead for the six-room mystery.** *The toy Envelope…* has `flat_single_aspect` at **0/5 at six rooms with 5 250 mm of frontage slack** and nothing identified. `kitchen.needs_window` went `true` **after** those presets were fitted, so the kitchen is a frontage claimant the arithmetic there may not carry. Not a claim — the one unexamined candidate | *The toy Envelope is more compact than a real dwelling* |

### 9. What this did NOT do, and why

- **It did not touch the rule.** `win.habitable_has_window` stays hard,
  `verified`, unchanged, and so does `kitchen_niche_windowless: false`. The ticket
  forbade re-litigating them and nothing measured here argues for it.
- **It did not overwrite `rules.json`'s `corpus_cost`.** That number is a
  different population and a different question; changing it from here would
  destroy a measurement rather than improve one.
- **It did not write `acceptance-bar.md`, `rules.json`, `room-constraints.json` or
  `fit_rects.py`.** All are other tickets' under the map's `writes:` rule; §8 hands
  them on instead. `docs/spec/proposer.md` and `experiments/corpus-smoke/` are this
  ticket's, and `CONTEXT.md` and `docs/adr/` are declared on resolution with no
  competing claimant.
- **It did not measure the residue's upper end.** `frontage_reach` reads boundary
  contact, and the conversion cannot tell `exterior` from `party`, so 6.39 % is a
  **floor**. Bounding it needs the Brief's Envelope; `proposer.md` §8 records it as
  an honest limit rather than a handoff, because nothing on the map is positioned
  to take it until a Proposer runs.

### 10. What the market does, checked because CLAUDE.md requires it

`floorplan-generation-stack.md`: of ~20 published generators 2020–2026, **exactly
one emits windows** (GFLAN, no code). Graph2Plan states the field's position
plainly — doors and windows are *"added afterwards"*, and its limitations section
lists that they *"aren't captured in the model"*. RPLAN carries none; WinNet's are
raster masks its own paper calls weak.

**So the whole field treats glazing as a post-hoc layer over a room topology**,
which is why the premise behind all four options is easy to hold and wrong:
nothing anyone trains on carries windows, so *"the donor's windows"* were never
something a proposer could inherit. This engine is not unusual in placing them
late; it is unusual only in **hard-constraining the room to the façade first**.

`competitive-landscape.md`: eleven products, **none documenting a daylight or
glazing rule** at unit-plan scale. Forma has sun-hours and daylight and is a
**site and massing** tool — a different question one storey up. The frontage
budget is therefore a differentiator worth protecting, and cl. 9.12 makes it
mandatory in the one region v1 ships.

### 11. Technology and refactor, per CLAUDE.md

**No new technology.** Everything measured here ran on the pinned environment;
28/28 `env_check.py`, 238/238 `gate_check.py`, 233/0 `ergonomic_check.py` after
the change.

**One refactor, and it should be taken as one pass, not three.**
`experiments/rectangularise/fit_rects.py` is now owed three per-record fields —
the cut-line frame and per-pair relation provenance from *The retrieval index and
warp procedure*, and `frontage_reach` from here. All three are functions of
records the fit already holds; emitting them separately means three passes over a
2,600-dwelling fit for no reason.

⚠️ **One repo-wide papercut, recorded rather than fixed here.** This project's
console is **cp1252**. `kitchen_niche_test.py` printed every number it had
computed and then died on the schwa in `taxça-mətbəx`, losing a nine-minute run's
JSON. Python files under `experiments/` should keep **stdout ASCII** and put the
Azerbaijani in docstrings, comments and Markdown, which are read as UTF-8. Three
existing scripts already do this by habit; nothing states it.

### 12. Map repair found while checking this ticket's own row

⚠️ **The done-test table's own invariant was violated and nothing had caught it.**
*"Every open ticket appears here exactly once. A row with no ticket is unowned,
and that is the failure this table exists to catch."* Ticket 51 appeared **nowhere
in the table** — and neither did *One wall weight where a real plan draws three*,
open since *One internal thickness against a corpus with no module* closed. 51 is
closed by this resolution; **36 is now placed on the Plan geometry model row**,
because its subject is the Wall and both its live shapes reach ADR 0001.

Also fixed: the **Acceptance bar row carried a stray `|`**, splitting it into four
cells in a three-column table, so everything after *"staffable, with named
owners"* — the whole ADR 0023 paragraph and every ⚠️ below it — rendered outside
the table or not at all.
