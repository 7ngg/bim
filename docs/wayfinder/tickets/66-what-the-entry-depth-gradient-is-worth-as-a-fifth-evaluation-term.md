---
id: 66
title: What the entry-depth gradient is worth as a fifth evaluation term
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: claude
blocked_by: []
writes:
  - docs/spec/proposer.md
  - docs/research/zoning.md
---

# What the entry-depth gradient is worth as a fifth evaluation term

## Question

**The day/night gradient is real, unassertable as a constraint, and invisible to
all three plan-quality terms that shipped.** *What an ordered entry sequence
costs the solver* refused it as solver machinery — correctly, the H-list closes
at H10 — and then measured the step that decision had skipped: it is not merely
unassertable, it is **unowned**.

`proposer.md` §6.1 has four plan-quality terms. Term 3, **social transit**, is
the one that looks like it should cover this. It does not, and the two are
**negatively** associated:

| | transit 0 | transit 1 | total |
|---|---:|---:|---:|
| **inversion 0** | 1 035 | 416 | 1 451 |
| **inversion 1** | **267** | **38** | 305 |
| total | 1 302 | 454 | 1 756 |

χ² = **34,55** (Yates 33,71), df 1, **p ≈ 4,2 × 10⁻⁹**, odds ratio **0,354**;
expected in the both-cell under independence **78,9**, observed **38**. **15,2 %**
of all dwellings invert the gradient with **no transit defect at all**. Transit is
a *routing* property (is this bedroom reachable only through a social Space);
inversion is a *distance* one (is this bedroom nearer the front door than the
living room). A bedroom opening straight off the entry hall is the second and not
the first, and term 3 cannot see it.

**D10 in `zoning.md` proposes the answer and this ticket decides whether to take
it**: a **fifth §6.1 term**, the **inversion rate** — the fraction of dwellings
whose nearest private Room sits strictly nearer the entrance than its nearest
social Room — held against the corpus rate of **17,4 %**, in the shape the other
four already take (scored against the corpus *distribution*, never a threshold).

It qualifies on §6.1's own stated property: computable on a corpus dwelling and
on a generated Plan by the same code, off the hop distance `zoning.md` §2.2
already publishes. No new corpus pass, no new field, no solver variable.

## What has to be decided

1. **Whether a fifth term is taken at all.** The case against is real and should
   be argued rather than waved: none of the four existing terms has ever been
   measured on a generated Plan, because no Proposer has been run. A fifth
   unmeasured term is a fifth thing to re-read later, and §6.1 already warns that
   all four rates *"move when the §2.2.1 pass lands and must be re-read then"*.
   The case for is that this is the only plan-quality property the map has
   identified, measured, and then left with nowhere to live.

2. **Which statistic.** ⚠️ **Not the strict-order rate.** The corpus is **51,0 %
   ties**, so a model that ties everything and a model that reverses everything
   both score 0 % strict — a strict rate cannot tell them apart. The inversion
   rate (17,4 %) can. A third option is the full three-bucket distribution
   (31,6 / 51,0 / 17,4), which is more honest and does not match the shape of the
   other four terms; decide whether consistency or fidelity wins here, because
   the same question will return for every future term.

3. **Whether it needs a Room-class node set it does not have.** Terms 1 and 3
   need `is_sleeping`, which *Where a set-versus-set property lives* handed to
   `room-constraints.json` and which **may not be folded into `is_private`**
   (true on the wet types too). Inversion needs *sleeping* and *social* as two
   sets. Check whether the social side has a flag at all, or whether this term
   quietly adds a second one.

4. **What it is scored against for the `AZ` region.** Every rate here is Swiss
   (C5). The other four terms carry the same exposure and it has never been
   called out per-term; decide whether this one inherits that silently or states
   it.

## What this is not

Not a re-opening of the ordering constraint — that is refused with a published
corpus cost (`zoning.md` §6, `solver-formulation.md` Part VI) and this ticket must
not reintroduce it as an evaluation term's side effect. A term scores a Plan; it
never rejects one. Not a change to the Proposal contract, which D8 refused with
its own reasoning. Not the five zoning **rules** owed to `rules.json` at
`zoning.md` §5b, which are acceptance-bar work and unrelated.

⚠️ **`docs/spec/proposer.md` is also claimed by *Should the warp post the
statutory floor*.** Per the map's concurrency rule these two may be worked in
either order but **not at once**.

## Raised by

*What an ordered entry sequence costs the solver* (2026-08-29), which refused the
solver encoding and found the property had no owner anywhere else.

## Resolution

**The term is taken, and its corpus rate is a ceiling rather than a target — which
is a defect in §6.1's shape, not in D10's proposal.** ADR 0042; `proposer.md`
§6.1; `zoning.md` D10, §6.7 and §6.8.

All four items answered, plus a scoring defect the ticket did not carry that turns
out to be §6.1-wide, and a corpus-model mismatch that decided item 3 against the
answer this ticket started with.

### Item 1 — taken, and the benign reading was tested rather than argued away

The case against was *"a fifth unmeasured term is a fifth thing to re-read later"*.
The real state is worse and is now recorded: **four of the five terms are
uncomputable today**, because terms 1, 2, 3 and 5 all read `is_sleeping` and
`room-constraints.json` ships `is_private`, `is_wet` and `is_habitable` and no
fourth flag. §6.1 read as though four terms shipped; it now says otherwise.

The case *for* is stronger than the ticket knew. The benign reading — that a
shallow private Room is a deliberate front-office, which Alexander's Patterns 141
and 157 put at **both** ends of his own gradient, and which Hanson calls *"a more
flexible use of space and a more heterogeneous and rich disposition"* — is
testable and **fails**: the shallow Room in an inversion is a terminal cell in
**4.9 %** of cases against **26.5 %** when ordered, the opposite of the
front-office signature. The corpus's inversions are bedrooms off the hall.

⚠️ **`study` never entered the measurement.** D2's sleeping set includes it and the
Swiss corpus has **no `STUDIO` among its `area` entities at all**; the closest
label, `OFFICE` (376 rooms, 86 apartments), is unmapped. The engine-side and
corpus-side sets differ, which §6.1's *"same code both sides"* property does not
currently survive — for terms 1, 2 and 3 as much as for 5.

### Item 2 — not the strict-order rate, and not the three-bucket either

D10 refused the strict-order rate correctly. It proposed the inversion rate or the
full three-bucket split and asked whether consistency or fidelity wins. **Neither
framing survives measurement: the three-bucket is confounded by dwelling size.**

| habitable rooms | n | ordered | tie | inverted |
|---:|---:|---:|---:|---:|
| 3 | 367 | 56.9 % | 30.8 % | 12.3 % |
| 4 | 723 | 30.8 % | 47.3 % | 21.9 % |
| 5 | 560 | 19.1 % | 65.9 % | 15.0 % |
| 6 | 98 | 15.3 % | 67.3 % | 17.3 % |

Tie mass runs **30.8 → 67.3 %**, monotone; `ordered` collapses **56.9 → 15.3 %**.
A large dwelling is hall-centred and everything sits at equal depth, so the tie
bucket is a **topology artefact**, not a quality signal — the argument that it is
"the modal outcome and worth keeping" is wrong. Inversion is the least confounded
of the three (12.3 / 21.9 / 15.0 / 17.3, non-monotone), so it is the quantity; and
the pooled scalar is a mixture over the corpus size mix, so the term **stratifies**
3 / 4 / 5 and pools 6+. House-GAN++ publishes the precedent — stratify, never pool.

⚠️ **The divergence question dissolves rather than being answered.** Priced against
this distribution, every candidate is broken: **KL is infinite for the generator
that never inverts** — the outcome most wanted; **TV and EMD score "never inverts"
and "inverts twice as often" identically** at 0.174 / 0.348, because a symmetric
divergence is blind to sign; chi-squared at N = 2 500 flags a **2 pp** deviation.
A defect rate minimised against a ceiling needs none of them.

### Item 3 — no new flag, and the coverage argument for one was measuring a label

The social set is `is_habitable` true and `is_sleeping` false — the construction
`zone.no_social_transit` and `zone.facade_to_living` already use — so the term
adds **no second flag**, which is what item 3 feared.

Plain `kitchen` stays out, and this was the hardest call on the ticket because it
reversed twice. Excluding it leaves **744 of 2 500** dwellings with no social Room,
which looked like an unacceptable coverage gap and is not — it is a **label**.
Those dwellings' largest private Room runs a median **20.2 m²** against **15.3 m²**
where a social Room *is* labelled (all social Rooms: 25.5 m²), and admitting them
by widening the social set makes them invert at **32.4 %** against **7.3 %** for
the labelled population. The pooled 14.7 % that widening produces is 7.3 % real
mixed with 32.4 % artefact — a figure that looks reasonable and is composed wrong.

⚠️ **The 744 are not mislabelled; they are `nutzungsneutral`.** WBS 2015 declares
Swiss rooms use-neutral and scores no zoning at all, so 70.1 % of the private set
is the unlabelled `ROOM` and the living room is often simply not designated. **A
heuristic relabel is therefore refused** — it would impose a typology the source
deliberately withholds. Recorded as a C5 corpus-model mismatch, not a repair.

⚠️ Note the kitchen decision is a **10-point** swing on the clean population
(17.4 % against 7.3 %), not the 2.7 points the pooled figures suggest.

### Item 4 — stated once for §6.1, and the exposure is smaller than a target's

Every rate in §6.1 is Swiss (C5) for all five terms, said once rather than
per-term. §6.8's *"the gradient's direction is not plausibly region-specific"* was
argued for a **rule** and must not be read across: a rate can be wrong for AZ
without the direction shifting. What limits the exposure is the **ceiling** — it
only has to be *not worse*, where a matched target has to be *right*.

### The defect the ticket did not carry, and it is §6.1's

`zoning.md` §6.5 calls the − bucket a **violation**; D10 asks to **match** its
rate. Both cannot stand — matching rewards producing as many bad plans as real
housing. §6.1 conflates two kinds of quantity, and **only term 5's is settled
here**: term 4 is **fidelity** by §4.5's explicit ruling that *"a landlocked room
is not a defect in the donor, it is a fact about real housing"*, term 3 is a defect
rate, term 1 is a genuine distribution, and term 2 is open. Raised as *What each
§6.1 term is scored for*, which 66 does **not** block on, because term 5's kind is
decided by its own evidence.

⚠️ **A possible degeneracy in term 4, flagged not asserted**: §4.5 says the solver
posts the frontage budget hard, so `frontage_reach` below 1.0 on a generated Plan
may be 0 % by construction. Pre- or post-solve is unconfirmed; it belongs to the
audit.

### Why the ceiling, since it is the reversal

No standard in either lineage scores a defect rate against observed stock. **ЖК РФ
art. 50 §2**, reached through СП 54.13330.2022's Table 5.1 note, does index a
threshold to observed stock — but as a one-sided **minimum on a quantity where more
is better**, which *rises* as practice improves; on a defect rate that is a ceiling.
**WBS 2015 added a *maximum* net floor area in 2015 because Swiss areas were
rising** — the bar moved *against* the stock, which a distribution-matching
instrument cannot do.

⚠️ **And no regulator scores this property at all.** СП 54.13330.2022 cl. 5.6 and
AzDTN 2.7-2 cl. 5.9 forbid a bedroom being **on the path** — that is term 3, already
hard — and neither constrains depth from the entrance. So the term ships
`src: engine_choice`, `conf: derived`, and §6.1 says so; it must never be presented
as standards-backed.

### Handed on as prose, files not opened

- **`experiments/zoning/measure_zoning.py` is a surviving private copy of the
  corpus-label projection ADR 0037 published.** Its comment names a
  `{ROOM, BEDROOM, STUDIO}` collapse and its code maps only `BEDROOM` and `ROOM`;
  `OFFICE` and `KITCHEN_DINING` are unmapped. Harmless today only because `STUDIO`
  is absent from the corpus. ADR 0037's sweep missed it because ticket 69's write
  scope was `experiments/warp/`. Handed to *Land the sleeping flag…*, which takes it.
- **`data/acceptance/rules.json`** was not opened — 72 and 76 both claim it — even
  though its `zone.*` rows depend on the `is_sleeping` flag that does not exist.

## Raised on resolution

- *Land the sleeping flag and retire the private corpus-label copies* — the flag has
  been handed as prose twice and landed neither time, so it is a ticket.
- *What each §6.1 term is scored for* — the matched-versus-minimised audit of
  terms 1–4.
