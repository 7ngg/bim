---
id: 38
title: What the engine says when the Envelope is bigger than the programme
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - docs/spec/brief.md
declared_on_resolution:
  - CONTEXT.md
  - docs/adr/0015-a-parse-time-bound-inherits-the-severity-of-the-rule-it-is-the-pre-image-of.md
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

---

## Handed here by *Whether a Room may be more than one rectangle* (2026-08-23)

**The dependency ADR 0013 drew is discharged, and it leaves you one edit to
`brief.md` §3.**

ADR 0013 found that `resolve` has to choose **how many** circulation Rooms to
invent before any geometry exists, that `brief.md` §3 does not say how many, and
that fixing it at one is safe *only* if a Room may be more than one rectangle —
too few leaves the Envelope untileable, too many fragments circulation against
`circ.fraction_hard`, and a wrong guess is not recoverable.

ADR [0014](../../adr/0014-a-room-is-one-or-two-rectangles-and-the-proposal-decides.md)
says a Room may be two rectangles. So:

**`resolve` invents at most one Room per circulation type, and never guesses a
count from the programme.** An L-shaped corridor reaches a wing that a rectangle
cannot, which is the case a second invented corridor existed to cover. Measured
over 46,800 Swiss dwellings
(`experiments/room-count-envelope/circulation_split.py`): k = 0 6.55 %, k = 1
**75.11 %**, k = 2 16.69 %, k ≥ 3 1.65 %.

⚠️ **What is NOT settled, and do not read it as settled.** Whether the 16.69 %
two-circulation mass is *lobby plus corridor* — two types, which `resolve`
already invents separately — or *corridor plus corridor*, which the L is supposed
to absorb, **is unmeasured**. The corpus cannot answer it as it stands: Swiss
Dwellings has one `CORRIDOR` label, and the ergonomic layer's
`hall` / `entrance_lobby` / `corridor` three-into-one gap is owed by *Two room
vocabularies in one file*. If that ticket lands a mapping that distinguishes
them, this becomes measurable and worth measuring before the rule is trusted at
the top of the band, where ADR 0013 shows the right k rising with the programme
(k = 2 is 18.9 % at six named rooms and **26.0 % at nine**).

Note also that k is inside the **engine room count** ADR 0013 hard-gates at
3–10, so a `resolve` that over-invents circulation spends the ceiling on
corridors and refuses Briefs that would otherwise have fitted. One per type is
the frugal reading as well as the correct one.

---

## Handed in by *Homeowner product surface*

**A stated Brief can contradict itself on its face and survive §9 entirely.**

You already hold §9.4's third and fourth bounds. This is a fifth check and it is
cheaper than any of them, because it needs no standards table at all.

§9.4 compares the sum of **realisable ergonomic minima** against `target_area`.
§9.2's ladder fills *silent* rooms from `market_default`, then the corpus median.
**Neither path ever compares the Homeowner's own stated `Room.target_area` values
against their own stated `target_area`.**

Worked, from the prototype: rooms stated at 18 + 8 + 12 + 11 + 11 + 4,2 m² =
**69,2 m²** inside a stated total of **45 m²**. That Brief clears all three of
§9.1's hard errors, clears §9.4's hard line (realisable minima are far below 45),
clears the warn line, generates, and **dies as zero survivors** — where
`acceptance-bar.md` §11 then explains it in terms of *ergonomic minima*, a set of
numbers the Homeowner never typed and cannot act on.

Two things make this yours rather than a UI concern:

- It is the same shape as the bound you are already fitting — arithmetic at parse
  time, naming the field whose edit resolves it — and it should be the **same
  function**, so §11's "the two produce the same sentence" keeps holding.
- **The severity is not obvious and is a real decision.** Stated-versus-stated is
  a contradiction rather than a shortfall, so it may deserve `hard` where the
  ergonomic bound is hard and the market bound only warns. But §9.5 forbids
  auto-repair and the partition footprint (~5,7 % at `t_int` 150) means an exact
  equality is wrong too — the stated sum is a *lower* bound on the interior, not
  an equal.

---

## Resolution — 2026-08-24

**`brief.md` §9.4 is six bounds and one function, and not one of its severities
was chosen.** ADR
[0015](../../adr/0015-a-parse-time-bound-inherits-the-severity-of-the-rule-it-is-the-pre-image-of.md):
a parse-time bound that is the arithmetic pre-image of a validator rule inherits
that rule's severity and its threshold, because firing softer promises a Plan the
validator will destroy and firing harder refuses Briefs it would have passed. Four
of the six bounds are pre-images; the other two are ADR 0013's scope gate, which
has no pre-image and says so.

| | bound | pre-image of | severity |
|---:|---|---|---|
| 1 | below Σ realisable ergonomic minima | `dim.min_area`, hard | hard |
| 2 | below Σ `market_default` | `dim.market_default_area`, soft | warn |
| 3 | engine room count outside 3–10 | — scope gate, ADR 0013 | hard |
| 4 | inside 3–10, outside 1–4 otaq | — scope gate, ADR 0013 | warn |
| 5 | Σ `Room.target_area` more than 5 % from `target_area` | `area.invented_envelope_hard` / `area.given_envelope_warn` | hard / warn |
| 6 | Σ upper band below a given Envelope's interior | `dim.max_area` ∧ `model.no_unassigned_area` | hard |

### The four questions

**1. The severity of the upper bound is `hard`, and the architect argument is
answered rather than overruled.** Both rules behind it are hard at site `both`, so
no legal assignment exists and *warn and proceed* is a false promise — H3 posts
tiling soft at 100 000, so the Brief returns a Plan with unassigned floor, dies on
`model.no_unassigned_area`, and reaches the Homeowner as zero survivors. A
professional handed a 95 m² flat and a four-room brief does not refuse the client,
and does not silently draw a 60 m² living room either: they say the programme does
not fill the flat and **ask what to add**. The bound is that sentence, and a
refusal naming both edits is a question.

**2. It proposes nothing, and names two edits.** Raise a `Room.target_area` — a
stated target is sovereign, so raising it raises that Room's cap by `k`, usually
one number — or add a Room. §9.5 forbids the engine choosing either: adding a Room
is inventing programme, and silently lifting the cap ships `dim.max_area`'s own
defect one storey up. **A 60 m² living room in a one-otaq flat is the 40 m² WC
wearing a better name**, and that is why the option *widen the bands for this
Brief* was rejected rather than deferred. Which Room would absorb is knowable —
§6.2's weights measure it, 40 m² more dwelling buying the living room +7.99 m² and
a bedroom +0.08 — and knowing is not licence.

**3. `target_area` and the Envelope are two bounds, not one, and the ticket's
premise for merging them was false.** The handoff said the stated sum *"is a lower
bound on the interior, not an equal"* because of the ~5,7 % partition footprint.
**Under ADR 0010 there is no partition term on that comparison at all**:
`target_area` is `ümumi sahə`, which sums room areas and does not count partitions,
and a `Room.target_area` is that same quantity for one Room. Both sides are net, so
bound 5 is exact integer arithmetic at the 5 % `area.invented_envelope_hard`
already ships. The partition term is correct in exactly one place — bound 6 — where
a stated `overall_dimension` is a **clear** dimension and the area it fixes is the
interior, gross of partitions. One term, and it is what separates the two
sentences.

**4. It is said in `engine_view`.** Four new fields — `engine_room_count`,
`otaq_count`, `programme_area`, `programme_ceiling` — plus `room_ceiling[RoomId]`
beside the existing `room_floor[RoomId]`, because bound 6's refusal names *raise a
`Room.target_area`* and a Homeowner cannot act on that without seeing which Room
has headroom. *Homeowner product surface* reads them; nothing recomputes.

### The three handoffs this ticket was carrying

**ADR 0013's bounds 3 and 4 are transcribed**, in their two units, with the
non-conversion warning intact.

**ADR 0014's circulation rule is settled, and it turned out to be sourced rather
than chosen.** `resolve` invents **exactly one circulation Room and it is a
`hall`** — one if the ResolvedBrief has none, otherwise nothing. Not a `corridor`,
for three reasons and none is a preference: **AzDTN 2.7-2 cl. 5.2 puts `holl` in
`yardımçı sahələr`, the auxiliary spaces a dwelling must have**, so inventing it is
transcription; it is the only one of the three circulation types with an `az_area`
row, so §9.2's ladder has something to default from; and it is the type a Homeowner
may name, which is how the 16.7 % of dwellings with two circulation spaces are
reached — by the Brief stating one, never by the engine guessing a second. Safe at
one because ADR 0014 lets it be an L.

Two consequences. **`corridor` and `entrance_lobby` become unreachable in v1** —
nothing invents them, no Brief may name them — handed to `room-constraints.json`'s
holder as `reachable_in_v1: false`, the marker `kitchen_niche` and
`wardrobe_1room_entry` already carry; a by-product is that `entrance_lobby`'s
`giriş holu`, **the one unsourced Azerbaijani name in that table**, is now on no
shipping path. And **the ⚠️ this ticket inherited is retired rather than owed**:
whether the 16.69 % two-circulation mass is lobby-plus-corridor or
corridor-plus-corridor no longer needs measuring, because the Brief decides it. What
*is* owed instead is narrower and goes to *Re-measure the conversion at two
rectangles per Room* — whether one two-part hall actually covers that mass, which
matters most at the top of the band where ADR 0013 shows k = 2 reaching 26.0 % at
nine named rooms.

**The stated-Brief contradiction is bound 5**, hard where the Envelope is invented.
The prototype's case — 69,2 m² of stated rooms inside a stated 45 m² — is refused at
parse naming both the total and the room fields, instead of clearing every check and
dying as zero survivors explained in ergonomic minima the Homeowner never typed.

### A third case, which was in neither the ticket nor the handoffs

**§5 discarded a stated `target_area` entirely.** Step 3 derived an unstated
dimension from `Σ Room.target_area / efficiency` and step 4 reconciled only when
dimensions *and* area were both stated — so a lone `target_area` fell through every
rule in the section. *"95 m², four rooms"* sized a box from the room defaults,
roughly 48 m², and never mentioned the 95: the Envelope-bigger-than-programme case
in its stated-total form **never reached a solve to fail at**. Fixed here, because
bound 5 would otherwise refuse a Brief the sizer had already silently rewritten.
§5 rung 1 now reads `interior = target_area × (1 + f)`, which also **retires
`efficiency` on that path** — the quantity it stood in for is the partition
footprint and that is measured.

### What the market does

`competitive-landscape.md`, checked because the shape of this answer is a product
decision. **No surveyed product refuses on a programme-versus-envelope mismatch,
and only one ships the absurd room.** ARCHITEChTURES — the only other tool taking a
full net-area programme table against an envelope — surfaces the mismatch as a
**violation tracker** the designer resolves; TestFit returns a **pass/fail** per
scheme; Maket generates regardless and disclaims measurement in its contract, and
Maket is the product C3 differentiates from. Bound 6 is the tracker's discipline
moved to **parse time**, where it costs a second instead of a wait, and where C2's
user — who cannot read a violation list — gets a sentence and two buttons.

### Technology and refactor

**No new technology, one schema change, and it merges with one already owed.**
§9.4 must return a **set of findings** — severity, Brief field, message — rather
than a verdict, and all six messages are Azerbaijani per `homeowner-surface.md` §2,
which is the same **locale dimension** already owed on the 38 rule messages: one
schema change to `rules.json`, not two. The other requirement is architectural and
already half-built: a **brief-scoped** predicate must be evaluable against a
`ResolvedBrief`. `area.given_envelope_warn` already carries `scope: brief`, so the
declaration supports it; nothing runs one at parse time yet. That is why
`CONTEXT.md`'s **Acceptance bar** now reads *one declaration, three consumers*.

### Written

`docs/spec/brief.md` §3.1 (new), §5 rung 1, §9.3, §9.4 (rewritten), §11, §12, §13.
ADR 0015. `CONTEXT.md` — **Pre-image bound** and **Invented circulation** new,
**Acceptance bar** and **Engine room count** amended.

### Not written, and handed on

| what | to |
|---|---|
| `f_hi` / `f_lo` — p5 and p95 of the per-dwelling partition footprint at `t_int` 150. Mean and p50 are published at 5.7 %, the spread is not, and until it lands bound 6 is a **point estimate** with its refusal and warning coincident | ***The partition footprint has a mean and no spread***, created here. The obligation was first written as *"whoever next runs `experiments/thickness-fidelity/`"* and there was no such person — *One wall weight where a real plan draws three* is about how many weights a **drawing** prints |
| `reachable_in_v1: false` on `corridor` and `entrance_lobby` | `room-constraints.json`'s holder — *Opening placement rules*, *The annotation spec is US-shaped* |
| §9.4 returns findings, each with a locale — one schema change with the owed message-locale one | `rules.json`'s holder |
| cl. 5.2's composition rule may now **assert** the `holl` half rather than test it | *A dwelling with no toilet passes every check* |
| whether one two-part `hall` covers the 16.7 % two-circulation mass | *Re-measure the conversion at two rectangles per Room* |
| `efficiency` unused where `target_area` is stated | *Fit the ENGINE_CHOICE acceptance thresholds to the corpora* |
| `acceptance-bar.md` §11's worked example, still not reproducible from the shipped table | whoever next holds `acceptance-bar.md` |
