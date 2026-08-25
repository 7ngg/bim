---
id: 27
title: Look at the converted corpus
parent: map
labels: [wayfinder:prototype]
status: closed
assignee: tng
blocked_by: []
writes:
  - experiments/rectangularise/ — no shared artifact
---

# Look at the converted corpus

## Question

**Does a converted dwelling read as a home? Nobody has looked.**

*Rectangularising real rooms* settled how a real dwelling becomes rectangles and
measured the conversion hard: zero adjacencies destroyed, zero separation
directions flipped, per-room IoU median 0.895 on Swiss Dwellings, cell agreement
0.90, area error −3.5 %. Every one of those is a number about cells and graph
edges. *Acquire the datasets* §6 recorded that **no plan from either corpus has
been rendered or eyeballed**, and that is still true — now of the converted
output too, which is worse, because the conversion is a transformation we
invented rather than data we received.

This is the one check the metrics cannot stand in for. A conversion can score
0.90 cell agreement and still put the bathroom door where a person would not walk,
or turn a hall into a room, or produce a plan whose proportions read as generated
at a glance. C2 holds the internal model to a Practitioner's standard, and a
Practitioner's judgement of a plan is visual before it is numeric.

**What has to be decided:**

1. **Whether the conversion is acceptable as it stands.** Render converted
   dwellings beside their originals and look. If the answer is no, this ticket
   says what specifically is wrong — that is the deliverable, not a score.
2. **What the failure modes are, named.** The measurement can rank dwellings by
   cell agreement but cannot say what a bad one looks like. Sample across the
   range — the median, the p5, and a few INFEASIBLE ones to see what was
   rightly dropped — and name the recurring kinds.
3. **Whether the 15.7 % of relations the conversion *adds* are the right
   choices.** Those are the pairs where one room wraps another and a rectangle
   model must pick a side. The fit picks whichever side costs fewer misassigned
   cells. Whether that matches what a person would draw is a visual question and
   has no metric.
4. **Whether cell agreement is the right headline number.** It was chosen because
   it is the objective; that makes it self-serving as an evaluation. If eyeballing
   disagrees with it, say which quantity tracked judgement better.

**Do not re-litigate.** The conversion itself (ADR 0008), the reject rule, or the
choice of rectangles over polygons. This ticket can find that the conversion is
wrong and say why; it cannot reopen whether v1 emits rectangles.

**Deliverable.** A rendered sheet — originals against conversions, sampled across
the agreement range and across room counts — plus a stated verdict and, if the
verdict is negative, the named failure modes. Renderer belongs in
`experiments/rectangularise/`.

**Why now.** It blocks nothing formally, and it is the cheapest possible check on
the most load-bearing transformation on the map. Everything the Proposer will ever
learn about arrangement comes through this conversion.

## Inherited from *Area measurement convention* — one thing to look at that nobody has

ADR 0010 moved the Space boundary to the **finished** face, and in doing so
exposed a gap in a number this map already treats as settled.

*Ergonomic minima and the constraint table's missing half* validated the hard
floor against Swiss Dwellings — *"the published floor rejects 0.0% of real living
rooms and bedrooms, 1.2% of kitchens, 4.6% of WCs and 7.8% of storerooms"*, and
the `BATHROOM` refutation that re-fitted the split at 2.4 m². **Every one of those
figures was measured against corpus polygons whose own face convention is
unrecorded.** Swiss Dwellings does not say, and nothing on this map has asked,
whether its space polygons are drawn to structural faces or to finished ones.

**It matters, and the direction is known even though the magnitude is not.** If
the corpus polygons are **structural**, every real room in the validation set was
roughly 30 mm larger per axis than the room a person actually occupies, so the
published ergonomic floor is **slightly lenient** — small, systematic, and in the
wrong direction, which is the same sentence ADR 0010 wrote about our own areas.
If they are **finished**, nothing moves and that is a clean result worth having.

Add to this ticket's looking: **for a handful of converted dwellings, check
whether the corpus's wall thicknesses and space polygons are mutually consistent
with a bare structural leaf or with a finished build-up.** The corpus records
both, so the question is answerable by arithmetic on data already on disk — the
wall thickness between two spaces against the gap between their polygons. A
negative result (the corpus does not distinguish, or is internally inconsistent)
is itself the finding.

This is a looking task, not a re-fit. If it shows the floor is lenient, the re-fit
is owed by whoever holds the ergonomic layer, not by this ticket.

## Amended by *One internal thickness* — the question above was the wrong one

The face-convention check handed to this ticket has been answered, and the answer
is that the question does not apply.

**Swiss Dwellings records exactly one plane, and no finish layer at all.** A
corpus Space polygon is not offset from its wall: the polygons sit on the wall
body's own faces to within 1 mm a side, and `gap − t_mrr` has a mode at **exactly
2.0 mm**. So the corpus is not "structural" and not "finished" — the distinction
that ADR 0010 introduced **does not exist in the file**.

Two consequences, and the second is the one worth looking at:

1. **The leniency worry is unresolvable from this corpus**, not merely unmeasured.
   *Ergonomic minima*' Swiss validation compared our rectangle against a corpus
   plane that is neither of ours. That is a **stated limit** on those figures now,
   not a pending measurement. Nothing further is owed here.
2. **What is still worth looking at is the shape, not the plane.** This ticket's
   own reason stands untouched — no converted plan has ever been looked at, and
   everything the Proposer will learn about arrangement comes through that
   conversion. Do the looking.

`experiments/thickness-fidelity/` did the arithmetic (see its README, *"A corpus
room polygon is not offset from its wall"*); do not repeat it.

---

## Handed here by *What a room's area is allowed to be* (2026-08-22)

⚠️ **A labelling defect in `swiss_fit.json`, found while reading it.**
`fit_rects.py` line 727 labels a fitted dwelling with
`[t for t, _ in dw[k]][:n]` — the **unfiltered** head of the source list — while
`load_swiss_geoms` (line 628) has already dropped polygons below
`MIN_ROOM_AREA`. Where a dropped polygon is not last, **every label after it is
off by one**.

Measured against `measure_swiss`'s correctly-filtered list
(`experiments/room-area-bands/plane_check.py`): **22 of 1,787 fitted dwellings,
1.23 %**. This ticket renders converted dwellings, so it will render
mislabelled rooms unless it relabels from `swiss_rects.json` — which is keyed
identically and filters correctly. Fix the source or work around it, but do not
read `swiss_fit.json`'s `types` as-is.

**Also relevant to what this ticket is looking for.** The fitted rectangles are
on the **watershed / centreline** plane and the corpus polygons are on the
corpus's own (clear-ish) plane. The ratio is **1.243** at dwelling level but runs
**1.17× for `living_dining` to 1.58× for `wc`** — a small room's share of the
walls around it is a much larger share of its own floor. A rendering that
overlays the two without saying which plane is which will look like the
conversion inflated the wet rooms. It did not; that is the plane.

---

## Handed here by *Whether a Room may be more than one rectangle* (2026-08-23)

⚠️ **`why_k.clean()` does not do what it is documented to do, and its numbers
should not be quoted.** The function is described as *"opening then closing: drop
protrusions and fill notches narrower than r"* with `CLEAN_CELLS = 2` labelled a
500 mm structuring element. Measured against synthetic masks
(`experiments/room-rectangles/morphology.py`, which carries a selftest):

- `_shift_all` pads and then slices back to the **original array shape**, so a
  dilation cannot grow past the array bounds. `why_k.py` rasterises each room
  over its own **tight bounding box**, so every room fills its array to the edge
  and the dilation is a no-op on it.
- The composition therefore reduces to erosion. On a tight-bbox 3.0 × 4.0 m
  rectangle `clean()` returns **96 of 192 cells** — the room eroded by 500 mm on
  every side, never restored.
- A **500 mm strip is deleted outright**, so the real deletion threshold is about
  750 mm, not 500 mm.
- On a padded mask it fills **no notch at any size** — 250, 500, 750 and 1000 mm
  corner notches all survive.

So `why_k.log`'s *"0.5833 of k ≥ 3 rooms are k ≤ 2 once features narrower than
500 mm are erased"* and *"0.3103 become a plain rectangle"* measure **the room
eroded by 500 mm all round**, which is a far larger operation than the one
claimed. Re-measured with a corrected opening and closing at a real 500 mm, the
share of rooms that are a single rectangle barely moves — see
`docs/research/room-rectangles.md` §5.

`experiments/room-rectangles/morphology.py` is a drop-in replacement with the
properties asserted rather than assumed, including the one that bounds what any
morphological clean-up can claim: **closing fills a bite in the middle of an edge
and never one at a corner**, and a corner bite is exactly the shape that turns a
rectangle into an L.

This ticket renders converted dwellings. If it reaches for a clean-up to make a
rendering legible, use that module, not `why_k`'s.

**One thing to look *for*, while you are rendering.** ADR 0014 puts the room tag
at the centroid of the Space's **largest constituent rectangle**, not the Space's
own centroid, because an L's centroid can land outside its own Space — proved in
`experiments/room-rectangles/erosion_check.py`, not merely feared. What is *not*
proved is that the resulting placement **reads well**: whether an L's tag sitting
in the fat leg looks deliberate or looks like it slid there. Ticket 28 item 4
asked for a drawn example and there is no renderer on this map to give one, so it
is owed by whichever ticket draws first, which is this one.

---

## Handed here by *Re-measure the conversion at two rectangles per Room* (2026-08-25)

**Two things: one of your instructions is discharged, and the thing you are going
to look at has changed shape.** ADR
[0016](../../adr/0016-the-conversion-names-its-own-ls.md),
`docs/research/rectangularisation.md` §11.

✅ **The labelling defect is fixed at source.** `fit_rects.load_swiss_geoms` now
collects `entity_subtype` from the **filtered** polygon list, so a dropped
sub-minimum polygon no longer shifts every label after it. The instruction above
to relabel from `swiss_rects.json` is **discharged for any file produced from
now on** — `out/swiss_fit_k1.json` and `out/swiss_fit_k2.json` are correct.
⚠️ The original `out/swiss_fit.json` is untouched and still carries the 1.23 %
off-by-one; regenerate rather than repair it.

⚠️ **A converted room is now one *or two* rectangles, and your renderer must draw
both.** The record schema changed: a k ≤ 2 file carries **`parts`** — a list of
rectangle lists, one per Room — and **no `rects` key**. A k = 1 file still carries
both. `k_used` gives the count per Room and `k_offered` what the naming allowed.
`experiments/rectangularise/validate_k2.py` is the reference reader.

**What you will see that you would not have seen before.** 9.85 % of Swiss rooms
are two rectangles, and they are not spread evenly — **42.2 % of open-plan
living/dining rooms and 22.0 % of corridors**, against 0.3 % of bathrooms and
0.5 % of storerooms. So the L-shaped corridor wrapping a wing is the thing to look
for first, and it is the case the one-rectangle conversion was mangling.

**And the reason to look is stronger than it was.** The worst room in a converted
dwelling gains **0.157 of IoU** on Swiss and **0.341** on ResPlan — on ResPlan it
was previously getting less than a quarter of itself right. That is precisely the
room a person's eye lands on, and no statistic in §11 can say whether it now reads
as a home.

⚠️ **Sequencing note now resolved.** This ticket was told to wait because the
conversion was about to move. **It has moved and settled**; render against
`swiss_fit_k2.json`. The plane caveat above is unchanged — the fitted rectangles
are still on the watershed/centreline plane, and the 1.17×–1.58× per-type ratio
still applies.

⚠️ **371 of 2,317 conversions are FEASIBLE rather than OPTIMAL**, so a small
minority are not the best available tiling. If one renders badly, check its
status before concluding the conversion is at fault.

---

## Resolution

**A converted dwelling reads as a home. The conversion is accepted, with four
failure modes named and three of its own fidelity headlines demoted from
evidence to restatement.** ADR
[0017](../../adr/0017-three-of-the-conversions-fidelity-headlines-are-constraints-restated.md).

67 dwellings rendered beside their originals across ten sampled bands —
`experiments/rectangularise/render_sheet.py`, sheets at `out/sheets/SHEET.html`.
Three panels each: the corpus polygons, the conversion **drawn as a plan** with
150 mm walls straddling every rectangle edge, and the two overlaid. Drawing the
walls is the part that makes the test valid: an outline drawing of the same
rectangles reads as a diagram and flatters the conversion, and what a person
judges is a plan.

### 1. Is the conversion acceptable as it stands? Yes.

At p95 it is effectively lossless — the original with its walls straightened. At
the median (cell agreement 0.935) it is a plausible flat that keeps the
original's arrangement, circulation and room sizes. ADR 0016's L-shaped
corridors read as real circulation spines rather than as two rooms with the wall
left out, which is what k = 1 was producing.

### 2. The failure modes, named

Full evidence in ADR 0017. In order of how much they matter:

1. **Off-frame wings.** `dwelling_frame` rotates a dwelling onto **one** angle.
   A dwelling built on two — a wing splayed off a spine — is sheared into a
   **different flat**: plausible, but not the one converted. 1.5 % of dwellings
   have a room off frame by 10–20° and score cell agreement 0.705 with
   worst-room IoU **0.167**; 1.2 % are worse. The whole p5 tail, and *not* a
   solver failure — they come back OPTIMAL. Ticket *The dwelling that is built
   on two angles*.
2. **Floor no Room claims.** Median **1.19 m²** of real dwelling floor unclaimed;
   **10.0 % of dwellings carry an enclosed void ≥ 0.5 m²** — a room-shaped hole
   with walls round it and no name. Invisible because it hides inside
   `uncovered`, which also counts the Envelope's correct notch under-cut.
   Handed to *A dwelling with no toilet passes*.
3. **Lost façade.** 4.1 % of façade-facing rooms lose frontage, 22.5 % of
   dwellings lose at least one. Handed to *H8 and the single-aspect flat*.
4. **Envelope loss is the dominant quality term — but the two-notch cap is not
   what causes it.** Above 0.10 loss, 53.5 % of dwellings have a room at
   IoU ≤ 0.5; above 0.20, 77.8 %. Yet the cap sits at the **knee of its own
   ladder** (median loss 0.161 / 0.050 / **0.018** / 0.011 / 0.010 at k = 0…4),
   raising it to four leaves 56 % of the worst 230 dwellings still above 0.10,
   and the four-notch ablation arm converts 88.0 % against 93.2 %. Ticket *The
   two-notch cap is now evidenced, and more notches is not the fix*.

### 3. Are the added relations the right choices? Yes — and the question was asked the wrong way round.

They are not *"the pairs where one room wraps another and the fit picks a side"*.
By construction a `spurious` relation is a pair whose bounding boxes
**overlapped** on that axis in the corpus and no longer do after squaring;
squaring necessarily turns an ambiguous separation into a definite one, and that
is the **only** free choice the fit makes about relations at all. Rendered, the
picks are what a person would draw.

The 15.7 % in the question above is the k = 1 figure. **Two k ≤ 2 rates are both
correct**: **13.58 %** paired over the 1,779 dwellings both arms converted (the
like-for-like measure, and the only one `rectangularisation.md` §11.4 publishes),
and **12.62 %** over all 2,317 conversions and 97,090 axis-pairs — what the
corpus the Proposer sees actually contains, and the one to quote downstream. The
538 dwellings k ≤ 2 rescued carry a *lower* spurious rate than the ones both
arms managed.

### 4. Is cell agreement the right headline? Honest, but it must not travel alone — and three companions are not evidence.

It ranks dwellings the way looking at them does (rank correlation **0.825** with
worst-room IoU), and of the 69.6 % scoring ≥ 0.90 only **0.8 %** hide a room at
IoU ≤ 0.30. So it is not self-serving in the damaging way. But it averages over
cells and a person looks at the worst room: in the 0.88–0.92 band the worst room
runs p10 0.45 to p90 0.82. **Publish worst-room IoU beside it.**

The larger finding is about the numbers standing *next* to it. `edges_lost = 0`,
"zero separation directions flipped" and per-room area error inside ±10 % are all
**hard constraints restated** — a dwelling that would violate any is *refused*,
not converted. **"Zero adjacencies destroyed" and "9.5 % refused" are one fact
stated twice**, and only one of them was in the headline. What is genuinely free:
cell agreement, the IoU distribution, the refusal rate, and `boundary_lost`.

### 5. What was refused

242 of 2,549 (**9.5 %**) INFEASIBLE. Rendered, they are **ordinary flats** —
nothing a person would call unrepresentable. The ablation names hard **adjacency**
as the cause (99.2 % convert without it against 93.2 % shipped; relaxing the area
band to ±25 % recovers only 5 of 13). Refused dwellings are slightly larger
(median 8 rooms against 7) and slightly thinner (55.4 % against 42.6 % have a room
below the 1.25 m centreline leg floor). Not reopened here — the reject rule is
ADR 0008's and this ticket was forbidden it — but recorded: **the refusal rate is
where the adjacency guarantee's cost is actually paid.**

### 6. Discharged from other tickets

✅ **ADR 0014's tag placement reads as deliberate.** An L-shaped Space tagged at
the centroid of its **largest constituent rectangle** looks placed, not slid.
*Whether a Room may be more than one rectangle* item 4 asked for a drawn example
and there was no renderer to give one; there is now, and the answer is yes.

✅ **The face-convention check** was already discharged by
*One internal thickness* and was not repeated.

✅ **The `swiss_fit.json` labelling defect** was fixed at source by ADR 0016;
`render_sheet.py` reloads types and asserts they match the record rather than
working around it. No mismatch fired over 67 dwellings.

### Assets

- `experiments/rectangularise/render_sheet.py` — the renderer. **A prototype;
  it must not become the engine's.** Picks: `spread`, `median`, `p5`, `p95`,
  `worstroom`, `k2`, `corridor`, `spurious`, `infeasible`, `feasible`.
- `experiments/rectangularise/void_census.py` — the unassigned-floor split and
  the frame-residual measurement.
- `out/sheets/SHEET.html` — the sheet index. Regenerate; `out/` is gitignored.
- `experiments/rectangularise/README.md` — updated with both, and with the
  constraint-restated table.

⚠️ **There is still no renderer on this map**, and this is the second ticket to
need one and have to build it first. *The annotation spec is US-shaped*, the IFC
tickets and the acceptance bar will each need to look at a plan.
