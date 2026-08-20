---
id: 20
title: Fit the ENGINE_CHOICE acceptance thresholds to the corpora
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: [12, 19]
---

# Fit the ENGINE_CHOICE acceptance thresholds to the corpora

## Question

*Acceptance validator spec* shipped 19 of 37 rules with `conf: engine_choice` —
no source dictates them, and for several **no source in the surveyed corpus
supplies a number at all**. They were set by judgement so that v1 could ship a
bar rather than wait for one. Now measure them.

The corpora make this cheap: Swiss Dwellings and ResPlan are real, built plans.
Every threshold below is a distribution question about plans that people actually
live in.

Fit, and report the distribution alongside the chosen value:

| Rule | Placeholder | Question |
|---|---|---|
| `circ.fraction_soft` | 8–18% of GIA | C6 item 7's "sane fraction". No surveyed source gives one. What is the real distribution of circulation share? |
| `circ.fraction_hard` | ≤30% | Where does the tail actually stop? |
| `dim.aspect_ratio_hard` | ≤3.0 | What is the worst aspect ratio a real habitable room has? A hard bound below the observed maximum rejects real homes. |
| `dim.aspect_ratio_soft` | ≤2.2 | Is the mode where we guessed? |
| `wet.plumbing_group_count` | ≤2 | How many disconnected wet clusters do real dwellings have? If the tail reaches 3, the hard bound is wrong. |
| `open.fits_segment` | 100 mm jamb return | No source gives a minimum return. Measurable from plans that carry wall and opening geometry. |
| `area.invented_envelope_hard` | 5% | Not corpus-measurable — it is a product tolerance. Decide it against the solver's observed GIA spread instead. |

Two rules that matter more than their numbers:

- **`dim.aspect_ratio_hard` is the one rule in the spec with no precedent
  anywhere.** It was added because nothing in C6 catches a room that satisfies its
  minimum area and minimum width by being long. If the corpus shows real rooms
  above 3.0, the rule is wrong in a way that rejects good plans — the ticket's own
  failure mode. Check it first.
- **Every hard `engine_choice` threshold is a candidate 99%-rejection bug.** Run
  the full registry against the corpora *as plans* and report the per-rule
  rejection rate. Any hard rule rejecting a large share of real, built dwellings is
  a bug in the rule, not a quality bar.

Blocked on *Acquire the datasets*, and on *Ergonomic minima and the constraint
table's missing half* — without the ergonomic layer, `dim.min_*` cannot be
evaluated and the rejection-rate measurement is incomplete.

Deliverable: measured distributions, revised values in
`data/acceptance/rules.json` with `conf` upgraded where the corpus supports it,
and the per-rule rejection rate against real dwellings.

---

## Added by *Building scope and envelope handling*, now closed

Two more constants land here, both shipping as `ENGINE_CHOICE` with no source:

- **`efficiency`** in `envelope_clear_area = sum(room target areas) / efficiency`,
  the factor absorbing circulation and internal wall footprint when a Homeowner
  states no area at all. Shipping at ~0.85. Swiss Dwellings has the geometry to fit
  it directly.
- **The default Envelope aspect ratio** applied to that area to get a rectangle.
  Shipping at ~1.35.

And one distribution worth fitting rather than guessing:

- **The exposure mix.** Swiss Dwellings is the one corpus with a building
  hierarchy, so which edges of an apartment abut a neighbour is **derivable from
  its own data**. That gives a real distribution over the dwelling-type presets
  (`flat_single_aspect`, `flat_corner`, `flat_dual_aspect`) instead of an invented
  one, and it tells *Solver timing variance sweep* which exposure case is typical
  rather than merely possible. Confirm the hierarchy survives extraction on
  *Acquire the datasets* first.

## Two obligations from *Rectangularising real rooms*

**Fit against the converted corpus, and erode before you compare.** A corpus
dwelling is now a rectangular tiling produced by a CP-SAT fit (ADR 0008), and its
rectangles are **centreline** rectangles: the conversion splits each wall at its
axis, so a converted room's area includes half of every wall around it. Per
ADR 0001 the clear rectangle is that eroded by `t_int/2`. **Every threshold here
is stated in clear dimensions** (*Acceptance validator spec*: the hard floor is
the ergonomic minimum, which is a clear number), so fitting against unroded
rectangles makes every fitted minimum generous by `t_int` per axis — and by
ADR 0007's arithmetic that is exactly the error that deletes 4-, 5- and 6-room
dwellings.

**The population you are fitting to is not the corpus.** The conversion drops
**31 % of Swiss Dwellings and 40 % of ResPlan**, and it drops them
non-uniformly — 83 % of 4-room dwellings convert against 46 % of 10-room. A
threshold fitted to the surviving population is fitted to a corpus that is
**biased toward the small and the simple**, because what fails to convert is
disproportionately the dwelling whose arrangement a rectangle model cannot hold.
Say which population each fitted number came from. Fitting against the *raw*
polygons is also available and is the right choice for any predicate that is
well-defined on a polygon (area, aspect via bbox); it is not available for
anything that needs a tiling.

Also relevant: *Acquire the datasets* §6 flagged that geometric validity was
unmeasured and this ticket would hit it first. Partly discharged — 46 invalid
polygons in 296,653 were repaired by `make_valid`, none dropped
(`experiments/rectangularise/measure_swiss.py`).
