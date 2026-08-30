---
id: 81
title: What each §6.1 term is scored for
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - docs/spec/proposer.md
---

# What each §6.1 term is scored for

## Question

**§6.1 says its terms are scored against the corpus distribution. For at least two
of them that means a generator scores best by reproducing the housing stock's
defect rate.**

The section's own words are *"the held-out target is the corpus distribution, not a
threshold"*. ADR 0042 amended that for term 5 alone and deliberately left the rest,
because term 5's kind is decided by its own evidence and the others are not.

The collision is visible in one place already: `zoning.md` §6.5 calls the entry-depth
− bucket a **violation**, while D10 asked to **match** its rate. Both cannot stand.
The same question applies term by term:

| term | corpus | matching would mean | reading |
|---|---:|---|---|
| 1. sleeping-group count | 69.8 / 27.7 / 2.5 | reproduce a real population mix | **distribution** — probably right |
| 2. longest-run allocation | 73.7 % | misallocate the best facade 26.3 % of the time | **open** |
| 3. social transit | 11.1 % | produce 11.1 % transited bedrooms | **defect rate** |
| 4. `frontage_reach` < 1.0 | 5.88 % | produce 5.88 % landlocked rooms | **fidelity**, per §4.5 |
| 5. entry-depth inversion | 17.4 % | — | **ceiling**, settled by ADR 0042 |

**Term 4 is the one that proves this is not a blanket rule.** §4.5 rules that *"a
landlocked room is not a defect in the donor, it is a fact about real housing"*, and
§6.1 calls term 4 *"the term that says whether a **trained** source has learned the
interior kitchen the corpus is full of"*. A source producing 0 % has failed to
learn. Matching is correct there and minimising would be wrong.

**Term 2 is the genuinely open one.** 73.7 % give the longest exterior run to a
habitable non-sleeping Room. Whether the other 26.3 % is a defect or a legitimate
choice — a corner unit, a dual-aspect plan, a principal bedroom given the view — is
an architectural judgement nobody has made, and it decides whether the term is
maximised or matched.

**What has to be decided:**

1. **A declared *kind* per term** — distribution, fidelity, defect rate — written
   into each term's own line rather than inferred from the section header.
2. **Term 2's kind**, which needs the judgement above and possibly a corpus split
   on what the 26.3 % actually are.
3. **Whether "the held-out target is the corpus distribution" survives as §6.1's
   framing sentence at all**, now that it is false for at least two of five.

⚠️ **A possible degeneracy in term 4, flagged not asserted.** `proposer.md` §4.5
says the solver posts the frontage budget **hard**. If so, `frontage_reach < 1.0` on
a generated Plan is **0 % by construction**, and the term would report constant
deviation from 5.88 % while measuring nothing. Whether it is computed pre-solve on
the Proposal or post-solve on the Plan is unconfirmed and is the first thing to
check, because it may retire the term rather than classify it.

**What this is not.** Not a re-opening of ADR 0042 — term 5's ceiling is settled
and evidenced. Not a change to any term's measured rate. Not a threshold change: a
term scores a Plan and never rejects one, and §6.2's stop conditions stay as they
are.

⚠️ **`docs/spec/proposer.md` is also claimed by *The posted floor is a seed-shape
estimate*.** Per the map's concurrency rule the two may be worked in either order
but **not at once**.

## Raised by

*What the entry-depth gradient is worth as a fifth evaluation term* (2026-08-30),
ADR 0042 consequences 5 and 6.
