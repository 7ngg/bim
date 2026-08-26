---
id: 54
title: The warp has never been measured against a stated target area, and a hard rule now rests on it
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: []
writes:
  - experiments/warp/
  - docs/research/proposer-architecture.md
---

# The warp has never been measured against a stated target area, and a hard rule now rests on it

## Question

**ADR 0018's headline warp fidelity is a *proportion* result, and the quantity
every downstream decision reads it as is an *absolute area* one.**
`fit_warp.py:373-384` scales the Brief's targets onto the donor's covered area
before comparing, which normalises absolute area away. So the p50 0.056 worst-room
deviation says the warp preserves the *shares* a donor allocates. It says nothing
about whether a Room asked for 12 m² gets 12 m².

*What shape an Envelope is when the Brief does not say* found this and left it as
an obligation on `experiments/warp/` with **no claimant**. It also made the
measurement newly possible: ADR 0020 fixes `interior` before the warp runs, so
there is now a stable denominator to measure against.

**What makes it a ticket rather than an obligation is that a hard rule now rests
on it.** *A statutory floor, posted soft, in the one region v1 ships* posted
`dim.statutory_min_area` **hard** — living 16 m², `bedroom_double` 10, kitchen 8 —
on the argument that `market_default` sits at or above `statutory_floor` in every
reachable AZ cell, so **a Plan that reaches its soft target clears the rule by
construction**. That argument is exactly as good as the warp's ability to deliver a
stated `target_area`, and nobody has measured it.

The same ticket accepted the risk explicitly, and named this as the trigger that
would reverse it:

> A hard rule that is too strict is **discovered** — at build time, on the first
> Proposer run, and rolled back by one field. A soft rule that is too lax
> **ships**.

This ticket is that discovery, brought forward so it happens before the build
rather than during it.

## What to measure

1. **Per-Room absolute area deviation** between a stated `target_area` and the
   Space the warp delivers, over the index — not the proportion `fit_warp.py`
   currently reports. Distribution, not a point estimate: the tail is the whole
   question.
2. **Direction.** A systematic *undershoot* is what kills the statutory rule; a
   symmetric spread does not, because `dim.market_default_area` is two-sided and
   pulls from both sides with fitted weights.
3. **Conditioned on the limb that matters.** The kitchen is where the rule is
   tightest against the corpus — AZ floors it at 8,0 m² and the Swiss p50 is
   8,04 — so the kitchen's deviation is worth reporting on its own.
4. **The yield number.** What share of warped candidates would fail
   `dim.statutory_min_area`, and how that compares to the 15,59 % the shipped bar
   already leaves.

⚠️ **Do not re-measure it as a proportion.** That is the defect, and reproducing
ADR 0018's number would look like confirmation.

⚠️ **`experiments/warp/` imports `solver-toy` read-only** and never edits it, the
arrangement `envelope-exposure/` and `h8-frontage/` already use. It reads
`rectangularise/out/swiss_fit_k2.json` as a **copied-in input**, not as a claim on
that directory.

## What this ticket does NOT decide

- **Whether `dim.statutory_min_area` stays hard.** It supplies the number; the
  severity is `rules.json`'s, and `acceptance-bar.md` §3.1 states what a bad
  result would mean.
- **The engine's own reachable maximum partition footprint**, which
  `brief.md` §13 records as validated against the corpus rather than the engine.
  That one is ruled **out of scope** — it needs the build — and this is not it:
  the warp runs today.
