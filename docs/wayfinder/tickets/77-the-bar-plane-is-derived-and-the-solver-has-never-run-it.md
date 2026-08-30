---
id: 77
title: The bar plane is derived and the solver has never run it
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: []
writes:
  - experiments/plane-accounting/
  - docs/research/solver-formulation.md
---

# The bar plane is derived and the solver has never run it

## Question

**ADR 0039 is an identity and two hand-checks.** It says `solver.py` should
subtract the erosion band per *side* rather than on all four, so `amm_i` becomes
the area ADR 0001 publishes:

```
amm_i = 62 500 · a_i  −  75 · Σ_{s ∈ 4 sides} interior_len_mm(i, s)
```

The arithmetic is exact and it spends no second `AddMultiplicationEquality`. What
it does spend is **auxiliary integers and reified literals, bounded by
rooms × 4 sides × faces**, and not one of them has ever been built. The 15 s cap,
τ = 4 and every timing on this map were fitted against a model without them.

⚠️ **Until this closes, `acceptance-bar.md` §11.1 and `CONTEXT.md`'s Space plane
both describe a decision as though it were a shipped state.** That is deliberate
and it is the debt this ticket pays.

**What has to be measured:**

1. **Build time and solve time**, against the incumbent, at the shipped
   configuration verbatim — `mm_affine`, eroded minima, τ = 4, σ = 0,5 m, 15 s,
   4 workers. Part II's rig is the comparator and its seed-to-seed spread is the
   bar the cost has to clear. ⚠️ A finding that this does not fit is a finding,
   and ADR 0039 decision 6 already carries the fallback: floors only, forward-only
   literals, `dim.max_area` left to the validator.
2. **The INFEASIBLE delta on the floor.** The incumbent's number is **14 of 273**
   with all fourteen attributed to `dim.statutory_min_area` by ablation. Re-run
   the same arm with the corrected plane; the difference is what the plane defect
   was actually costing, and it is the number `acceptance-bar.md` §11.1 should
   carry in place of the 5,1 % upper bound it carries now. ⚠️ That figure is
   **pre-ADR 0033** — the warp did not post the floor when it was measured — so
   the incumbent arm has to be re-run too, not quoted.
3. **The cap side, which no arm on this map has ever exercised.** `dim.max_area`
   is hard and `site: both` and the toy solver **does not post it at all** — H4
   posts `min_w`, `min_h`, `min_area` and aspect, and nothing else. So the false
   pass ADR 0039 describes is a property of the *spec*, not of anything measured.
   Post the cap under both readings and find out whether it binds, and on which
   Rooms. ⚠️ If it turns out never to bind at production geometry, ADR 0039
   decision 4's biconditional requirement is the expensive half of the change and
   is bought for nothing.
4. **Whether the corner residual is worth recovering after all.** ADR 0039 drops
   it at ≤ 0,0225 m² per Room, conservative on floors and *lenient* on the cap.
   Exact recovery needs contact at a point rather than over a length. Measure the
   realised distribution before accepting the bound as decorative.

**What this is not.** Not a re-opening of ADR 0039's decision — a measurement that
the encoding is unaffordable selects its own stated fallback, it does not restore
the two planes. Not a change to any threshold: ADR 0027, ADR 0033 and
`acceptance-bar.md` §3.2 settle `dim.statutory_min_area` three times over. Not a
change to `_add_exterior`, which keeps its forward-only literals by decision 4.

**Where it goes.** `experiments/plane-accounting/`, **new**, importing
`solver-toy/` and `warp/project_join.py` read-only and editing neither — the
idiom `envelope-exposure/` and `h8-frontage/` already use, and the right one here
because an A/B needs both arms live. `experiments/solver-toy/` is claimed by
*What an ordered entry sequence costs the solver* and `experiments/warp/` by
three tickets; this takes neither.

## Raised by

*The projection discards a fifth of the guarantees the warp now buys*
(2026-08-30), ADR 0039 consequence 5.
