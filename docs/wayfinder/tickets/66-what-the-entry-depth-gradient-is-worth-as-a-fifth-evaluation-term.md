---
id: 66
title: What the entry-depth gradient is worth as a fifth evaluation term
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
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
