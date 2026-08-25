---
id: 48
title: What shape an Envelope is when the Brief does not say
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - docs/spec/brief.md
declared_on_resolution:
  - docs/adr/0020-a-candidate-pool-shares-a-floor-area-not-a-box.md
  - CONTEXT.md
---

# What shape an Envelope is when the Brief does not say

## Question

`brief.md` §5 step 2 says `shape` fixes the **notch count**, at most 2, and that
**notch positions are never statable** — a Homeowner who can place a notch can
draw, and C2 says they cannot. It does not say what happens when `shape` is
absent, which is the common case. Two things now depend on that silence and they
pull in opposite directions.

**1. A default of "rectangular" would silently delete retrieval.** *The retrieval
index and warp procedure* measured the corpus: **90.16 %** of converted dwellings
use both notches, 8.72 % one and **1.12 % none**; by area, only **6.5 %** leave
under 2 % of their bounding box unoccupied and 15.0 % under 5 %. A source with
two notches cannot serve an Envelope with none, because the notch cells would be
floor no Room claims and `model.no_unassigned_area` is hard. So
`shape = rectangular`, taken as a *stated* gate term, admits single-digit
percentages of the index — and taken as an unstated **default** it does that to
almost every Brief without anyone deciding it.

The obvious reading — absence means unknown, not rectangular — is probably right
and has a cost of its own: a Homeowner with a genuinely rectangular flat gets an
L-shaped plan and has to notice and correct it.

**2. ADR 0018 made the Envelope per-candidate, and nothing has been checked
against that.** Where `shape` is `invented`, each retrieved candidate carries its
own notch geometry, scaled from a real dwelling — which is why the position is a
measured number instead of an invented constant. But the Envelope was a per-job
object everywhere else on this map. Specifically owed:

- **What `area.invented_envelope_hard` compares against.** It is ±5 %, hard, over
  the area-determining fields. If two candidates have different notch geometry
  they have different interior areas, so the rule can pass on one candidate and
  fail on another for the same Brief. Is that correct, or does the rule bind the
  bbox rather than the interior?
- **What the Assumption surface says.** `brief.md` §6 has three Assumption kinds
  and the notch is an `invented_value`. A value that differs per candidate has no
  representation there today.
- **Whether `shape` stated should gate on notch count or notch *area share*.**
  Count is crude: a 2-notch envelope losing 3 % of its bbox reads as rectangular
  to a person, and the p10 of that share is **0.032**.

**What has to be decided:**

1. What `shape` resolves to when absent, and with what provenance.
2. Whether a stated `shape` gates retrieval on notch count, on notch area share,
   or on neither.
3. Whether an Envelope field may vary per candidate at all, and if so which
   consumers have to be told — `area.invented_envelope_hard` above all.
4. What the Homeowner is shown when it does. (The *presentation* half is fog on
   the map under *A Homeowner shown candidates whose outlines differ*; this
   ticket owes only whether the model permits it.)

**Why this is not `The retrieval index and warp procedure`'s to answer.** That
ticket writes `docs/spec/proposer.md` and this is `brief.md`'s shape. It found
the defect, measured it, and could not write the file.

**Deliverable.** `brief.md` §5 amended, and a line in §9.4 if any of it becomes a
pre-image bound. Mints an ADR only if answer 3 is *yes* — that one is hard to
reverse.

---

## Resolution

**A candidate pool shares a floor area, not a box.** ADR
[0020](../../adr/0020-a-candidate-pool-shares-a-floor-area-not-a-box.md),
`docs/spec/brief.md` §5 / §5.1 / §5.2 / §6 / §9.4 bound 7 / §12 / §13,
`CONTEXT.md`.

### The defect was in an ADR, not in a spec

ADR 0018 asserts both readings, four paragraphs apart. Its *decision* makes the
Envelope "per-candidate in its `invented` fields only"; its *consequence 3* prices
the 6.9 % Brief-level decline loss on the Envelope being what "every candidate for
one Brief **shares**". Everything downstream — `area.invented_envelope_hard`,
`brief.md` §5's sizing rung, ADR 0003 §7's *"the entrance edge is fixed before the
solve"* — was written against the second reading while the ADR shipped the first.

### The notch is 12.55 % of the bounding box

Re-measured first-hand over the 2,317 converted Swiss dwellings in
`experiments/rectangularise/out/swiss_fit_k2.json` — the share of bbox taken by
the two largest boundary-touching complement components:

| notch share of bbox | p10 | p25 | **p50** | p75 | p90 | p95 |
|---|---:|---:|---:|---:|---:|---:|
| | 0.0313 | 0.0783 | **0.1255** | 0.1794 | 0.2330 | 0.2692 |

A twenty-point swing between two candidates for one Brief, against a ±5 % hard
gate. **The ticket's own p10 of 0.032 is vindicated at 0.0313** — it was the only
number in the ticket body traceable to nothing.

So the two readings are not a wording slip. Sizing one box at the median notch
puts **56.15 %** of the index outside `area.invented_envelope_hard` on donor
geometry alone — before the warp deviates a room, before the solver places a
partition. At the 2 % soft preference, 81.61 %.

### And no measurement had ever seen that, because the harness divides it out

`experiments/warp/fit_warp.py:373-384` scales the Brief's room targets onto the
donor's *covered* area rather than its bounding box, with the reason in the
comment: *"Asking the fit for `W*H` would demand 13 % more floor than the
arrangement holds."* Correct for what that harness measured, and it means ADR
0018's headline — best-of-8 worst-room deviation p50 **0.056** — is a statement
about **proportion** with absolute area normalised away. **The warp has never been
measured against a stated `target_area`.** The quantity the hard gate binds is the
one the rig removes.

### What was decided

1. **The pool invariant is floor area.** `resolve` fixes
   `interior = target_area × (1 + f)` once; each candidate derives
   `W × H = interior / (1 − s)` from its own notch share, aspect held. Every
   candidate delivers `interior` **by construction** — 1.0000 against 0.4385, and
   not by widening a tolerance. The box may flex **only where `overall_dimension`
   is invented**, which is exactly where the hard gate applies; where a dimension
   is stated the box is fixed, the floor absorbs the notch, and the applicable
   rule is already `area.given_envelope_warn`. One rule, two provenance branches,
   **no new threshold and no new severity.**
2. **`shape` leaves the `ResolvedBrief`.** §1 makes that object dense, so ADR 0018
   consequence 5's *"absence means unknown"* had nowhere to live. `shape` is a
   retrieval gate term on the `StatedBrief`; nothing downstream of the Proposal
   reads it. A **default** was the dangerous option and is refused in both forms:
   `rectangular` admits 1.12 % of the index, and the corpus mode would surface
   "two notches" as an Assumption inviting correction when it is not a fact about
   the Homeowner's home at all.
3. **A stated `shape` gates on notch *area share*, and the count gate was
   mis-labelling the entire index** — not merely starving rectangles:

   | stated `shape` | shipped count gate | material-notch gate (≥ 5 % of bbox) |
   |---|---:|---:|
   | `rectangular` | 1.12 % | **15.67 %** |
   | `L` | 8.72 % | **52.96 %** |
   | `U`/`T` | 90.16 % | **25.42 %** |

   Raw count says 90 % of real flats are U/T-shaped and 8.7 % are L. The material
   reading says half are L, a quarter U/T, a sixth read as rectangles. **The
   largest gain is the common case, `L`, at 6×**, which is the opposite of where
   the ticket expected the win. 5 % rather than 2 % because 2 % is 1,8 m² on a
   90 m² dwelling and ticket 28 already measured that class as real architecture
   rather than pipe boxings — counting it as shape double-counts that evidence.
4. **A stated `shape` is §9.4 bound 7, warn, with no pre-image.** No rule governs
   retrieval coverage, so there is no severity to inherit — ADR 0015's third case,
   which ADR 0013's scope gate already occupies. When the pool empties the Brief
   falls through to **source B** and the change of provenance is surfaced.
   **Refusal would be wrong in a way the other bounds' refusals are not**: bounds
   1, 3, 5 and 6 refuse Briefs the engine cannot serve; this one would decline a
   request it *can* serve — the 40 m² WC's error with the sign flipped.

### What was **not** decided, deliberately

- **`area.invented_envelope_hard` is not edited.** The ticket assumed a threshold
  or quantity change and the answer is a modelling change instead. With floor
  invariant, the only thing left that can move Σ Space area is the **partition
  footprint** — which is what ADR 0010 rewrote the rule to catch and what `f` only
  predicts. `rules.json` sees no change. Re-fitting the gate upward to ~±13 % was
  available and cheap (ticket 20 holds the threshold) and is **refused as a
  modelling defect laundered into a looser tolerance**.
- **§6 gains no fourth Assumption kind, and that is derived.** The set is
  `ResolvedBrief \ StatedBrief`; a field absent from `ResolvedBrief` yields no
  Assumption — correctly, because an Assumption is something we filled in on the
  **request** and the notch is a property of the **result**. The pressure moves to
  the gallery, which is the same request-versus-result confusion *A request and a
  result in one typeface* is open on.
- **"Fill the notch"** — let the target outline differ from the donor's and assign
  the leftover cells to a bordering Room, which ADR 0014 already permits as an L.
  Any donor could then serve any shape and the stated-shape cliff disappears
  entirely. **Not rejected on merit.** It re-opens ADR 0018's monotone-warp
  theorem (zero confident-wrong over 21,074 relations) and it is a `proposer.md`
  change this ticket does not hold. Recorded in ADR 0020 and §12.

### What the market does

Ten of eleven surveyed products **take the boundary as user input** and none
invents one — TestFit (parcel GIS/DXF/KML), ARCHITEChTURES (plot DWG), Forma
(IFC/OBJ site), Digital Blue Foam (GeoJSON/SHP), Snaptrude (polygon drawn
in-app), Synaps ("site dimensions" in the brief, or DWG). The eleventh is
**Maket** — the only pure-consumer tool, C2's own buyer — which resolves it by
disclaiming *"measurements, dimensions, or scale"* in its terms. **There is no
precedent to copy here**, which is why this ticket had no template, and it is the
reason bound 7 exists rather than being assumed away.

### Handoffs

| owed | to |
|---|---|
| the material-notch gate term (§2.2.3), and where `W × H = interior/(1−s)` is computed (§2.2.1's record must carry `s`) | whoever next holds `docs/spec/proposer.md` — **no claimant** |
| **ADR 0003 §7 re-read as *one ring per candidate*** — the entrance edge is identified by **side, never by ring index**, which is what makes it survive a topology change; the ADR does not say so today | *The two-notch cap is now evidenced*, which holds `docs/adr/0003-…`. **Not edited from here** — that is the map's concurrency rule, and blind parallel writes created two rework tickets already |
| re-run `fit_warp.py` against an absolute `target_area` — now possible, because `interior` is fixed before the warp | whoever next holds `experiments/warp/` — **no claimant** |
| "fill the notch" as a candidate design | whoever next holds `docs/spec/proposer.md` |

### Ticket item 4, and what it is not

*"What the Homeowner is shown when it does"* — this ticket owed only whether the
model permits it. **It permits it**, and by decision 2 the per-candidate outline
generates no Assumption, so the presentation question is entirely the gallery's.
It stays fog under *A Homeowner shown candidates whose outlines differ*, now with
its magnitude attached: the bounding box can differ by up to **30 %** at the p90
notch between two candidates that agree on floor to the millimetre.

### Claims withdrawn during this session

- **"The rule may need to bind the bbox rather than the interior"** (ticket item
  3, first bullet). Withdrawn: once floor is the invariant the rule binds neither
  differently — it binds Σ Space area, unchanged.
- **"The residual unassigned floor is a problem for this ticket."** Measured and
  withdrawn: inside a two-notch Envelope it is p50 **0**, mean 0.59 %, above 5 %
  on 1.34 % of dwellings. The two-notch Envelope is an honest tiling; the problem
  was sizing, not tiling. The enclosed-void half stays with the acceptance bar,
  where ticket 27 sent it.

### Written

- `docs/adr/0020-a-candidate-pool-shares-a-floor-area-not-a-box.md` (new) — declared
  on resolution, per the ticket's *"mints an ADR only if answer 3 is yes"*. No
  other claimant.
- `docs/spec/brief.md` — §5 step 1 and step 2 rewritten, §5 rung 1 annotated, new
  §5.1 and §5.2, §6 gains the per-candidate note, §9.4 goes **six bounds → seven**
  with bound 7 and its own subsection, §12 gains five handoffs, §13 gains two
  limits.
- `CONTEXT.md` — declared on resolution; **no claimant** at the time. **Envelope**
  gains the one-area-many-boxes reading and an `_Avoid_` naming ADR 0018
  consequence 3 as false; **Notch** is a new term carrying the material threshold
  and the 12.55 % median.
