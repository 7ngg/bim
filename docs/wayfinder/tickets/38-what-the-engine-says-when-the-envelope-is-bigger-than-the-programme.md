---
id: 38
title: What the engine says when the Envelope is bigger than the programme
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - docs/spec/brief.md
---

# What the engine says when the Envelope is bigger than the programme

## Question

*What a room's area is allowed to be* measured the upper band and found that
putting a maximum on every Room creates a case the spec has no answer for.

`brief.md` §9.4's feasibility pre-check is **"two bounds, two severities, one
function"** — and **both bounds are lower**. It refuses below the sum of
realisable ergonomic minima and recommends below the sum of market defaults.
There is no upper check at all, because until now nothing had an upper bound.

Now something does. `model.no_unassigned_area` is hard and exact, and a **given**
Envelope — a flat, C5's majority case — fixes Σ Space area before the solve. So if

```
sum( upper band per Room )  <  interior - partitions
```

no legal assignment exists. Measured (`experiments/room-area-bands/`,
`docs/research/room-area-bands.md` §5.1): at p99 caps the corpus's commonest
4-room mix sums to **77.9 m²** against a corpus p99 of **79.7**, so the largest
1 % of real 4-room dwellings cannot be expressed. At p99.5 it clears, and every
room count above 4 has double the headroom it needs. **The case is real, it is
narrow, and it is at the bottom of C13's band** — where *Ergonomic minima* already
found the 250 mm grid charging the 5-room case.

**The failure mode is not a crash and that is the problem.** H3 posts exact tiling
**soft** at weight 100 000, so an over-constrained Brief does not come back
INFEASIBLE. It comes back as a Plan with unassigned floor, the validator kills it
on `model.no_unassigned_area`, C6 discards it, and the Homeowner sees **zero
survivors with no explanation**. §9.4 exists precisely so that never happens.

## What to decide

1. **The severity of the upper bound.** The lower one is a hard refusal. Is the
   upper one a refusal too, a warn that proceeds, or something else? An architect
   handed a 95 m² flat and a four-room brief does not refuse the client — they say
   *you have more space than this programme needs* and propose what to do with it.
   A refusal here would be the engine declining work a person can obviously do.
2. **What it proposes, if anything.** The options are real and different: widen
   the bands for this Brief, add a room, or accept rooms above their band with the
   overage disclosed. Each is a different product. §6.2's soft weights already say
   *where* the slack would land — the living room, then circulation — so the
   engine can name the room it would grow.
3. **Whether the check belongs to `target_area` or to the Envelope.** The same
   arithmetic is reachable from two directions: a Brief whose rooms are too small
   for its flat, and a Brief whose flat is too big for its rooms. They are the same
   inequality and probably not the same sentence.
4. **Where it is said.** §11's `engine_view` block is Homeowner-visible and
   uneditable, and already carries `hard_area_floor` and
   `market_area_recommendation`. If this becomes a third field, *Homeowner product
   surface* reads it rather than recomputing — which is the pattern
   `retrieval_pool_size` already set.

## Boundaries

- **Does not write `rules.json`.** `dim.max_area` and its thresholds are handed to
  whoever holds that file — currently *Fit the ENGINE_CHOICE acceptance thresholds
  to the corpora*, which has been given the obligation. This ticket is the
  **parse-time** half.
- **Does not re-measure the band.** The numbers are settled in
  `docs/research/room-area-bands.md` §6.1 and are read, not re-derived.
- **Not the Homeowner-facing copy.** How the sentence is presented is *Homeowner
  product surface*. This decides what the engine *knows* and at what severity.
- **Not envelope sizing.** How an *invented* Envelope is sized against
  `target_area` is the map's **Variant generation and ranking** fog patch. This is
  the **given** Envelope case, which is the one that cannot be fixed by resizing.

---

## Handed in by *The room-count envelope v1 promises* (ADR 0013)

**§9.4 grows from two bounds and two severities to four bounds and three.** You
hold `brief.md`; this is yours to write. Both new bounds are room-count, not area,
and both belong in the *same function* so §11's same-sentence guarantee keeps
holding by construction:

| bound | severity | rule |
|---|---|---|
| existing | hard | sum of **realisable** ergonomic minima |
| existing | warn | sum of `market_default` |
| **new** | **hard refusal** | engine room count outside **3–10** |
| **new** | **warn** | inside 3–10 but outside **1–4 otaq** |

Two things to carry rather than re-derive:

- The hard one **must be explicit**. `acceptance-bar.md` §11's zero-survivor
  diagnosis is arithmetic over *areas* and cannot voice a room-count failure — so
  without this check a Homeowner past the ceiling is handed an area sentence that
  is not the real reason. A wrong explanation, not a missing one.
- **The two bounds are in different units on purpose** (ADR 0013). The gate is
  engine rooms, post-`resolve`, including invented circulation. The warn is otaq,
  habitable rooms only. Do not convert one into the other by a constant — the
  spread at each otaq is two to three engine rooms wide.

The refusal names the count. `CONTEXT.md` **Supported band**, **Engine room
count**, **Otaq**.
