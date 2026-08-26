---
id: 47
title: The two-notch cap is now evidenced, and more notches is not the fix
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - docs/adr/0003-the-envelope-is-an-inner-face-ring-of-typed-edges.md
  - experiments/rectangularise/
---

# The two-notch cap is now evidenced, and more notches is not the fix

## Question

**ADR 0003 caps the v1 Envelope at a bounding box minus at most two notches and
records the cap as *"unevidenced in both directions"*. It is now evidenced.** The
cap is defensible — it sits at the knee of its own ladder — and the population it
hurts is **not** hurt by the cap. ADR
[0017](../../adr/0017-three-of-the-conversions-fidelity-headlines-are-constraints-restated.md),
failure mode 4.

Envelope loss is the largest single quality term in the conversion, larger than
the rectangle count, the solver budget or the room count:

| envelope loss at k = 2 | dwellings | worst-room IoU | share with a room ≤ 0.5 |
|---|---:|---:|---:|
| < 0.01 | 39.8 % | 0.844 | 10.5 % |
| 0.03–0.06 | 16.6 % | 0.738 | 15.3 % |
| 0.10–0.20 | 8.0 % | 0.483 | **53.5 %** |
| ≥ 0.20 | 1.9 % | 0.293 | **77.8 %** |

**And the obvious response is wrong.** The corpus-wide ladder, median over 2,317
converted dwellings, with the marginal gain of each extra notch:

| notches | median loss | marginal |
|---:|---:|---:|
| 0 | 0.1610 | — |
| 1 | 0.0503 | −0.1107 |
| **2** | **0.0178** | **−0.0325** |
| 3 | 0.0114 | −0.0064 |
| 4 | 0.0096 | −0.0018 |

**Two is already the knee.** A third notch buys 0.6 percentage points of median
loss and a fourth buys 0.2. And on the 230 dwellings the cap supposedly hurts
most — those above 0.10 loss at k = 2 — raising the cap to four moves the median
only 0.136 → 0.105, and **56 % are still above 0.10 and 89 % still above 0.05**.
Their outlines are not bounding-box-minus-notches at *any* notch count: they are
chamfered, curved, or stepped more times than a rectilinear ring of typed edges
can express.

⚠️ **And a higher cap is measured to make the conversion worse.** The k ≤ 2
ablation (`out/ablate_k2.log`) has an *"up to 4 notches"* arm: it converts
**88.0 %** against the shipped **93.2 %**, 25 INFEASIBLE against 13. A tighter
Envelope leaves the rectangles less slack to satisfy the hard adjacency and area
constraints inside it. Raising the cap trades a fifth of the conversion yield for
moving 9 % of dwellings below 0.05 loss (26.6 % → 17.3 % above it).

**What has to be decided, then, is not the number.** It is what v1 does about the
dwellings whose *outline shape family* it cannot express — which is a different
question from how many notches it allows, and the one this evidence actually
raises:

1. **Nothing — the cap stands and the loss is the price.** Defensible on this
   evidence, and it is the cheapest answer, which is exactly why it needs
   arguing rather than assuming. It means roughly 10 % of the training corpus
   carries an Envelope that is visibly not the dwelling's own outline, and the
   Proposer learns from it.
2. **Refuse them.** An envelope-loss gate in the reject rule, thinning the corpus
   further on top of the 9.5 % already refused, and buying a corpus whose every
   Envelope is faithful.
3. **Widen the shape family rather than the count** — chamfered edges, or a
   general rectilinear ring with a vertex budget instead of a notch budget. This
   is the one that reaches production-plan territory and the one that costs
   most: ADR 0003's edges are **typed**, a notch is *"a garden in one case and a
   neighbour in the other"*, and any new edge kind has to be nameable to a
   Homeowner, drawable, dimensionable, and expressible in the IFC (ADR 0011).

**Whatever is decided, ADR 0003 must stop saying "unevidenced".** The ladder,
the ablation arm and the tail measurement above are the evidence; a reader who
takes the ADR at its word today will re-derive all three.

**Also owed:** ticket 15's solver timings were measured against a two-notch
Envelope, so any cap change re-prices them. That is a reason to decide before
the timings are quoted again, not a reason to leave the cap alone.

## Resolution

**The cap stands at two, the shape family is not widened, and the tail is not
the Envelope's problem.** ADR 0003 gains a second amendment; the reframing is
this ticket's real contribution and it moves the open question off this row
entirely.

### The question was mis-posed, and the measurement says so

The ticket asked what v1 does about *"the dwellings whose outline shape family it
cannot express"*. That framing assumes the generated Envelope can be unfaithful
to something. It cannot: `brief.md` §5.1 takes `shape` out of the `ResolvedBrief`
altogether, and ADR 0020 derives every candidate's box from its **donor's**
recorded notch share. There is no ground truth on the generation side. Whatever
donor is drawn, what v1 *draws* is a legitimate real outline — 61.8 % of real
dwellings are bbox-minus-≤2-notches exactly, and read materially the corpus is
15.67 % `rectangular`, 52.96 % `L`, 25.42 % `U`/`T`.

What a tail donor carries is a distorted **arrangement**, and *"the arrangement
is a real home's"* is the entire claim of source A.

### More notches was never the fix, and now the mechanism is known

`envelope_family.py`, new, seconds off the cached fit. `rectangularisation.md`
§13.

**Sixteen of the 283 tail dwellings are inside the cap already** and still lose
more than 0.10 of envelope area; at `notches_all` = 1 the loss is **identical at
every k** — 0.1025 at k = 1, 2, 3 and 4. A notch is one *rectangle*; a complement
component need not be one. The budget never bound on them, and §6.4's flat curve
had only shown the shape of that without naming it.

### The tail is two populations and only one is even addressable

| outline class | n | share of corpus | > 0.10 loss at k = 2 | share of the tail |
|---|---:|---:|---:|---:|
| rectilinear (≤ 2 % off-axis) | 2,102 | 81.10 % | 5.1 % | 38.2 % |
| mixed (2–10 %) | 263 | 10.15 % | 13.3 % | 12.4 % |
| off-axis (> 10 %) | 227 | **8.76 %** | 61.7 % | **49.5 %** |

Off-axis share is measured **in the dwelling's own frame**, after
`dwelling_frame` has done its best. Half the tail is chamfered, angled or curved:
no rectilinear family of any budget expresses it.

### Option 3 refused, at a measured ceiling

- **Vertex budget instead of notch budget** (the only coherent rectilinear
  widening): rescues **108 dwellings, 4.17 % of the corpus**, of which 46.3 %
  are *still* above 0.10 loss at four notches. 4.17 % is the whole ceiling.
- **Chamfered edges**: breaks axis alignment for the 250 mm grid,
  `AddNoOverlap2D` and every dimension chain.

Refused on measurement, not on cost. The rectilinear widening spends the property
that makes the ring cheap everywhere else — the edges are **typed**, a notch is
*"a garden in one case and a neighbour in the other"*, nameable to a Homeowner,
drawable, dimensionable and an IFC entity — for a twenty-fifth of the corpus.

### Option 2 refused, and the reason is that envelope loss is the wrong instrument

Gating the corpus on envelope loss was the ticket's second option. It is a
**predictor** — ADR 0017 says so in as many words — and the predicted quantity,
**worst-room IoU**, sits in the same fit record. Over the 2,317 converted
dwellings the index actually holds:

- **42.2 %** of the loss tail converts *faithfully anyway* (worst-room IoU ≥ 0.50).
- **12.70 %** of everything **outside** the tail does not.
- An IoU < 0.50 cut removes **10.09 % of the most faithful envelope band**
  (loss < 0.01) — dwellings whose outline the Envelope describes exactly and
  whose rooms the fit still got wrong. No envelope-loss threshold can see them.

The population that matters is its own: **worst-room IoU < 0.30 is 154 dwellings,
6.65 % of the index**, and only 35.7 % of it is in the loss tail and 33.1 % is
off-axis. **Two thirds of it is invisible to either proxy.**

The better gate also subsumes the off-axis finding rather than competing with it:
off-axis dwellings carry a median worst-room IoU of 0.522 against 0.777
rectilinear, 26.0 % below 0.30 against 4.5 %. §12.3's sheared dwellings — cell
agreement 0.705, worst-room IoU 0.167, returning **OPTIMAL** — are in that 26.0 %.

### What ADR 0003 now says

Second amendment at the foot, plus two in-body pointers:

- The cap bullet is marked evidenced and points at it.
- **Consequence 7 is amended**: *"the entrance edge is fixed before the solve"*
  now reads **per candidate, before that candidate's solve**, with the reason it
  is safe stated — the edge is identified by **side**, never by ring index, so a
  per-candidate notch changing the edge count cannot move it. Held over twice
  before this ticket; both holders declined to write blind into a claimed file,
  correctly.

### The handoff, and it is the whole open question now

**`proposer.md` §2.2 — donor fidelity is neither in the index record nor in the
ranking.** §2.2's eleven index fields carry none, and §2.2.4 pre-ranks on the
**warp's** worst-room deviation, which is a fact about the *fit to this Brief*,
not about whether the donor was a faithful conversion in the first place. Owed:

1. **Add worst-room IoU to the index record.** `fit_rects.py` already emits
   per-room `iou`; nothing new is computed and no re-fit is needed.
2. **Gate hard below 0.30.** By §2.2's own argument — *"outside the gate, do not
   retrieve … the entire claim of retrieval is that the arrangement is a real
   home's"* — a donor whose worst room bears no resemblance to the room it came
   from is not a real home's arrangement, it is the conversion's artefact, and
   C2's *90 %-right is worse than a blank sheet* applies. Cost: **6.65 %** of the
   index. `conf: fitted` in ADR 0023's vocabulary, not `verified` — the corpus's
   own p10 is 0.369 and p5 is 0.241, and 0.30 is chosen against a published cost.
3. **Rank on it above the gate**, joining §2.2.4 step 2, so faithful donors are
   warped first. A hard gate at 0.50 would cost 17.2 % of an index C13 already
   records as thin (58.0 % blank at 11+ rooms); ranking costs nothing.

`proposer.md` is claimed twice (*A third of real kitchens have no window*,
*A donor's enclosed void becomes area nobody asked for*) so this ticket may not
write it — the concurrency rule binds. Written out here in full so its next
holder transcribes rather than re-derives.

**Ticket 46, *The dwelling that is built on two angles*, is handed the 8.76 %.**
It currently scopes §12.3's **1.5 %** — a room off frame by 10–20°. The outline
measure here is a different and much larger population, and 46 should see it
before it decides. Not ruled out of scope from here: 46 is open and unworked, and
ruling on its behalf would pre-empt a ticket rather than resolve one.

### Two things deliberately not done

- **Ticket 15's timings are not re-priced.** They were measured against a
  two-notch Envelope and the cap did not move, so there is nothing to re-price.
  The ticket flagged this as a reason to decide *before* quoting them again; the
  decision is now made and the quotation is safe.
- **"Fill the notch" is not taken.** 48 recorded it against `proposer.md` and it
  stays there. It is a warp-side design, not an Envelope shape-family question,
  and it re-opens ADR 0018's monotone-warp theorem.

### Artifacts

- `docs/adr/0003-…` — second amendment, cap bullet, consequence 7.
- `docs/research/rectangularisation.md` §13 (13.1–13.5).
- `experiments/rectangularise/envelope_family.py`, log at
  `out/envelope_family.log`, README row and the *add the statistic here* rule.

### Declared on resolution, not taken quietly

`docs/research/rectangularisation.md` shares its claim with ticket 46, which was
**unclaimed** at the time, so the concurrency rule held. §13 is a self-contained
section at the foot and touches nothing 46 will write; its §13.5 hands 46 the
off-axis population explicitly rather than leaving it in a log.
