# The drawing layer, executed — findings from the first run

Research note for the first time a `Plan` on this map has been **drawn**. It
records what happened when `docs/spec/openings.md` and `docs/spec/annotation.md`
stopped being documents and started being code.

Method note, and please read it before trusting anything below. Every number in
this document was measured on this machine by running
`experiments/demo-sheet/run.py` and `src/bim_engine/selftest.py`. Nothing is
estimated. Where a claim is about a *specification* rather than about a run, it
cites the clause and quotes it.

---

## The findings, in one table

| | Finding | Where it lives |
|---|---|---|
| F1 | `annotation.md` §14's `t_ext` is 300; the profile ships 500 | spec, stale |
| F2 | §6.1's "rounded to even millimetres" contradicts §14's own chain | spec, contradictory |
| F3 | `bathroom_combined` has no `door_for_room` row, and it is Baku's commonest wet room | profile, incomplete |
| F4 | the projection admits contacts no door can be placed in — **16,7 % of candidates**, and ADR 0021's threshold takes it to **0** | code, ADR undelivered |
| F5 | `entry.exists` is not implemented; a landlocked hall passes the bar | rig, missing predicate |
| F6 | the bar's H8 is a run length where `win.area_ratio` is an area ratio | rig, weaker rule |
| F7 | tier 2b has a datum side AND a rung side; §4.3 names one | spec, underspecified |
| F8 | tier 3's "one chain per Envelope edge" does not cover a notch reveal | spec, gap |
| F9 | §7's tag ladder must test obstacles, not just the room box | implementation trap |
| F10 | §5 has no rule for two tier-2b runnings on one rung, and they always collide | spec, gap |
| F11 | a Baku listing's headline is **6,6 %** more than the Brief's target area | measured |
| F12 | the drawn plans make the warp's tail visible: worst-room deviation p50 **8,3 %**, max **134,9 %** | product |
| F13 | the warp returns different tilings for identical inputs at a fixed seed — **1 of 12 pairs** | code, reproducibility |

F4, F5 and F6 are the ones that change what the engine does. F1, F2, F7, F8 and
F10 are documents to correct. F3 is a decision for whoever holds the profile.
F12 is the one that could not have been found any other way. F13 was found by
two runs disagreeing and then confirmed by a check written for it.

---

## Why this exists

Three specifications on this map were complete, detailed, sourced — and had
never been executed. Between them they are 2 620 lines:

| Spec | Lines | Code before this |
|---|---:|---|
| `docs/spec/openings.md` | 570 | none |
| `docs/spec/annotation.md` | 1 220 | none |
| `docs/spec/ifc-export.md` | 830 | none |

Ticket 59 joined the warp to the projection and measured what came out. Nothing
then asked the result for a drawing. The one rendered plan in the repo —
`experiments/homeowner-surface/` on branch `prototype/homeowner-surface` — draws
six layouts from **invented** Envelopes (ticket 58's complaint) and places its
doors and windows with a JavaScript heuristic in `prototype.src.html`, not with
`openings.md`.

So: `src/bim_engine/` implements the first two, and `experiments/demo-sheet/`
runs a Baku Brief through the whole pipeline into a two-sheet set.

## The oracle

`annotation.md` §14 is the only fully computed Plan on this map — a
single-aspect one-bedroom flat with every clear rectangle, area, chain, window
selection and setting-out dimension worked out by hand, before any of this code
existed. `src/bim_engine/selftest.py` reproduces it.

**Every number agrees**: five clear rectangles, five printed areas, the
Envelope inner area, `yaşayış sahəsi`, five doors with their catalogue widths,
leaves and setting-out datums, two windows with their series widths, positions,
GOST designations and sills, four tier-2 chains, an empty tier 2b, two tier-3
chains, and four setting-out dimensions each reading 100.

That is the strongest evidence in this note. A worked example written by a
person and an implementation written from the same prose agreeing to the
millimetre means the prose was unambiguous, which is not the usual outcome.

Two disagreements survived, and both are the **spec's**, not the code's.

### F1 — §14's `t_ext` is stale at 300; the profile ships 500

§14 states *"S exterior `t = 300`, W exterior `t = 300`"* and computes
`overall_x = 7850 + 300 = 8150`. `profiles.AZ.construction.catalogue.brick.
t_ext_total` is **500** — `engine_choice`, provisional, 380 brick leaf + 100
insulation + 20 finish, blocked on Baku's degree-day figure. Nothing in §14
mentions the discrepancy, and its opening note claims the example follows
*"the shipped profile"*.

Tier 1 at the shipped profile is **8350 / 6350**. The rest of §14 is unaffected:
`t_ext` enters no clear dimension, no area, no chain but tier 1, and no opening.

**Consequence.** The number is wrong on a sheet, in the one place a house is set
out from. It is also the only `engine_choice` in the construction block that
carries a stated blocker, so it will move again. Whoever next holds
`annotation.md` should either re-derive §14 at 500 or say in §14 that its tier-1
row is illustrative.

### F2 — §6.1's "rounded to even millimetres" contradicts §14's own chain

`openings.md` §6.1: *"A single window centres on its clear run, rounded to even
millimetres per ADR 0004."* §14's tier-3 south chain:
`1275 | 1800 | 2425 | 1350 | 1000`. The first and third ticks are odd, so the
jamb positions in the spec's own worked example are **not** even.

Both cannot hold. ADR 0004 binds *published dimensions* — thicknesses and
opening widths — and every opening width here is even either way; forcing an
even jamb moves the window 1 mm off centre for no rule's benefit. The
implementation centres exactly and floors the near jamb where the surplus is
odd, which reproduces §14. **§6.1's clause should be struck or narrowed to the
opening width.**

---

## What the first real dwellings found

### F3 — `bathroom_combined` has no row in `door_for_room`, and it is Baku's commonest wet room

`profiles.AZ.openings.door_for_room.map` carries `wc`, `bathroom`,
`shower_room`, `storage`, the four bedroom limbs, `study`, `kitchen`, `utility`
and the five living-family types. It does **not** carry `bathroom_combined`.

`bathroom_combined` is in the ergonomic layer, is in the AZ name table
(*birləşdirilmiş sanitar qovşağı*, `verified` from AzDTN 2.7-2 cl. 5.2), and is
what MIDA's own schedules call **Sanitar qovşağı** — 492 of the rooms in 318
published Baku apartments, the second commonest room word after *Eyvan*.

`openings.md` §9 is explicit: *"A room type added later must arrive with a
mapping row or `gate_check.py` fails."* This one arrived without one, and
`gate_check.py` did not fail, because the gate checks the room table and not the
door map.

**Not patched here.** Inventing the row would be the unlabelled `engine_choice`
the profile exists to prevent. The demo maps *Sanitar qovşağı* onto the corpus
`BATHROOM` label, which resolves to `bathroom` and takes DG 21-7 at 700 — which
is very likely the right answer, and is a decision for whoever holds
`room-constraints.json`.

### F4 — the projection admits contacts no door can be placed on, and ADR 0021's threshold fixes it

**This is the load-bearing finding, and it is now measured rather than argued.**

`openings.md` §8 predicts it in terms:

> a solve can pass potential circulation on a run and then be hard-rejected by
> `open.fits_segment` or `open.leading_edge_nib` the moment a door is placed on
> that same run.

ADR 0021 answered it: **the threshold becomes `structural opening width +
t_int + 400`.** That is 1250 mm centreline for a 700 door, 1350 for an 800 and
1450 for a 900.

`experiments/solver-toy/real_arm.py` posts `DOOR_MIN_ADR = mm(1.0)` — **1000 mm
centreline, one scalar for every pair**, which is 850 mm clear at the shipped
`t_int` of 150. `experiments/warp/project_join.py` imports the same constant.
So the rig admits a contact **250 to 450 mm shorter** than any door in the
catalogue can occupy, and ADR 0021's decision has never reached the code.

#### The measurement

Three arms, **paired on the same ten MIDA Briefs and the same 72 donors**, seed
`20260830`, pool `k = 8`, everything else identical. `Brief.door_min` is one
scalar for the whole Plan, so ADR 0021's per-pair rule can only be forced into
it two ways — at the narrowest catalogue door, or at the Brief's widest
receiving door — and both are run:

| arm | posted `door_min` | Plans no door can be placed in | Briefs served |
|---|---|---:|---:|
| `rig` | 1000 mm — what the map posts today | **12 / 72 = 16,7 %** | 7 / 10 |
| `min` | 1250 mm — ADR 0021 at a 700 door | **6 / 72 = 8,3 %** | 7 / 10 |
| `max` | 1500 mm — ADR 0021 at the Brief's widest | **0 / 72** | 7 / 10 |

Every one of those 12 is a Plan that **passed the acceptance bar** and in which
at least one Room has no run any door can occupy:

```
rig   5x  no door run reaches R03
      2x  no door run reaches R01, R05
      2x  no door run reaches R02
      1x  no door run reaches R01
      1x  no door run reaches R07
      1x  no door run reaches R03, R05
```

**Three things follow, and the third is the useful one.**

1. **ADR 0021 is right and its threshold works.** Posted at the widest door the
   Brief can require, the failure class it was written for goes to **zero** on
   this sample. The ADR did not need re-deciding; it needed running.
2. **Half the cost is already bought at the narrowest door.** 1250 mm — the
   cheapest reading of ADR 0021 — halves the class. So a rig that cannot afford
   the widest reservation is not stuck with the status quo.
3. **The Homeowner does not notice, because best-of-pool absorbs it.** Brief
   level service is **7 / 10 on all three arms**, identical, with the same three
   Briefs failing. The threshold changes how many candidates are wasted, not
   what is delivered — at a pool depth of 6 to 11. That is a real defence of the
   pool, and it is also why this defect survived: nothing that measured Briefs
   could see it, and everything on this map measured Briefs.

The extra reservation is not free — INFEASIBLE rises as contacts are lost, which
is what §8 said it would do — but on this sample it is paid entirely out of pool
depth.

#### What the demo does, and what it does not

`run.py` defaults to the `max` arm. Making the threshold **per-pair** is a change
to `solver-toy/solver.py`'s `_contact`, which is a solver change and belongs to
whoever holds ticket 43; §8 already handed the *rate* there, and this is the same
handoff with a reproduction and three measured arms attached.

### F5 — `entry.exists` is not implemented, and the placement layer is the first thing to notice

Once the door-run class is gone, six of the `max` arm's eight remaining
placement refusals are one thing:

```
the hall touches no Envelope edge; `entry.exists` fails
```

`openings.md` §7 says such a candidate *"is already dead at `entry.exists`,
before this rule is consulted"*. It is not: `experiments/solver-toy/validate.py`
implements ten predicates, H1 to H10, and **none of them is `entry.exists`**. So
a Plan whose hall is landlocked in the middle of the dwelling passes the bar as
the rig implements it, and the first thing in the pipeline to object is the
front door having nowhere to go.

That is 6 of 72 candidates — **8,3 %** — on this sample. Cheap to fix and
cheaply detected: the predicate is one contact test between the invented hall
and the Envelope's `entrance_side` edges.

### F6 — the bar's H8 is a run length; `win.area_ratio` is an area ratio

The eighth refusal:

```
R01 (kitchen) cannot be glazed to cl. 9.13 on its 1350 mm run
```

`validate.check`'s H8 asks whether a Space that needs a window has **an exterior
wall run of `window_min`** — 4 grid units, 1000 mm. `win.area_ratio` (AzDTN
2.7-2 cl. 9.13, **hard**) asks whether the structural opening reaches 0,125 of
the Room's net floor area. Those are different rules, and a 1350 mm run passes
the first and fails the second: the widest series member that fits with its jamb
returns is 1200, and 1200 x 1200 is 1,44 m² against a kitchen needing more.

`openings.md` §6.1 anticipated exactly this and refuses to paper over it — *"it
is never quietly downgraded to the widest member that fits, which would ship an
under-glazed room the validator then rejects for a reason the placement layer
already knew"*. The placement layer does know, and the validator does not
reject, because the validator is checking the weaker rule.

### F7 — tier 2b has two sides and §4.3 names one

§4.3: *"Each such face gets a running dimension from the Envelope inner face on
the nearest side."* For a vertical partition face that reaches neither S nor N,
the nearest Envelope inner face is W or E — that is the **datum**. But the
dimension is horizontal, and a horizontal dimension line can only be drawn on a
horizontal rung, which is S or N.

The first implementation carried one field for both and drew an x-axis running
dimension on the E rung: a horizontal dimension line placed at an x coordinate
read as a y, landing inside the plan. Caught by eye on the first real dwelling,
which is the argument for drawing things.

**§4.3 should name both**: the datum side (nearest, per axis) and the rung side.

### F8 — tier 3's "one chain per Envelope edge" does not cover a notch reveal

§4.4: *"One chain per Envelope edge holding an Opening."* Its worked example has
a rectangular Envelope, where an edge and a bbox line are the same thing. ADR
0003 makes a real Envelope a **bbox minus notches**, and a converted dwelling
leaves a median 13,1 % of its bbox as notch — so a window can sit on a notch
reveal that lies on no bbox line at all.

A bbox test silently drops such an opening from every chain.
`draw.every_opening_positioned` caught it on the first run, which is that
predicate earning its place. The implementation reads the side off the **hosting
Space** — the wall is west of its room, or east of it, which is true on a reveal
as much as on the perimeter.

### F9 — the tag ladder has to test obstacles, not just the room box

§7's ladder degrades *"until the tag fits its Space with a 1 × text-height
margin clear of walls, openings and in-plan dimensions."* An implementation that
reads only *fits its Space* passes its own test and fails
`draw.no_text_overlap` with `tag R03 overlaps mark 4`. Not a spec defect — the
clause says what it means — but it is the one place where the cheap reading and
the correct one look identical until a real plan is drawn.

### F10 — §5 has no rule for two tier-2b runnings on one rung, and they always collide

§5(c) covers *"an in-plan setting-out dimension against another"*. It does not
cover two **running** dimensions, and those collide by construction: both faces
of one un-reaching partition are measured from the same datum and differ by
`t_int`, so their two texts land 75 mm apart in model space — 1,5 paper
millimetres at 1:50.

The implementation applies §5(c)'s own remedy — the second steps out one further
increment, deterministically, never dropped — and tier 1 moves outboard of
whatever that reaches. **§5 should say so**, because the case is not rare:
§4.3's own measurement is that nearly half of a large plan's partitions reach no
Envelope edge.

### F11 — a Baku listing's headline is not the Brief's target area

`area_convention.brief_semantics` says a Homeowner's "90 m²" can be several
percent more than the rooms they get, because `ümumi sahə` counts eyvan at a
coefficient of 1,0 and v1 models none.

Measured on MIDA's 318 published apartments: the eyvan **is** inside the
published `internal_size` — on record 0 the five rooms sum to 34,97, which is
`internal`, and one of them is a 3,91 m² eyvan. Over the 85 Briefs this note's
runs use, the median eyvan share is **6,6 %** of the listed area.

So the prose is right and the number is now attached to it: a 2- or 3-otaq Baku
listing loses about a fifteenth of its headline before the engine sees it.

---

### F12 — the drawn plans make the warp's tail visible, and a percentile table did not

Not a specification defect and not a code defect: a **product** observation that
only a drawing could produce.

Worst-room area deviation of the candidate that was actually drawn, over the
eight served Briefs of the last run:

```
p50   8,3 %        seven of eight between 5,0 % and 11,4 %
max 134,9 %        one 3-otaq plan whose bathroom is 8,97 m2 against ~3,8
```

An earlier run of the same twelve Briefs (see F13) drew nine and carried a
second tail entry at 44,4 %.

The tail is not a selection failure — best-of-pool picked the **minimum** worst
deviation available, so it was the best its pool held. On a percentile table a
134,9 % entry is a row. On a sheet it is a bathroom the size of the kitchen,
tagged `VANNA OTAĞI 8,97 m²`, next to a living room, and nobody who looks at it
needs the table explained.

Every warp fidelity study on this map — tickets 54, 56, 57, 60 — reported
distributions. This is the first time the distribution has been **looked at**,
and the tail is worse to the eye than it reads on the page. Whether the fix is a
deeper pool (57's curve), a fourth gate term (65), or a refusal rather than a
delivery, is not this note's call; that the tail is a product problem and not a
statistics problem is.

### F13 — the warp is not reproducible at a fixed seed, and reproducibility is a product promise

**Observed, then diagnosed by the check this section originally only proposed.**

Two runs of `run.py 12 --k=8 --time=2.5 --limit=10.0`, same seed `20260830`,
same code on the solve path, same machine, minutes apart:

| run | Briefs served | drawn |
|---|---:|---:|
| first | 9 / 12 | 9 |
| second | 8 / 12 | 8 |

`mida-125` flipped from served (worst-room 44,4 %) to `no_survivor`, with all six
of its donors refused. Nothing on the solve path changed between the two — the
only edits were the area-fraction position in `dxf.py` and an empty-notes guard
in `preview.py`.

**What is measured.** Both CP-SAT stages are capped on WALL CLOCK, not on
deterministic time: `fit_warp.warp_model` sets `max_time_in_seconds = tlim` with
`num_workers = 1`, and `solver.project` runs `workers = 4`. On this sample
**32 of 88 warps ran at or past their 2,5 s cap** (`warp_s` p90 7,34 s, max
11,79 s — the cap is per inner solve and `hold_ring` iterates), while no
projection came close to its own (p90 0,78 s of 10). A time-truncated
optimisation returns whatever incumbent it held when the clock ran out, so a
warp that is cut off can hand the projection a different tiling on a different
run, and the projection then answers a different question.

**The check.** `experiments/demo-sheet/_determinism.py` solves the same
(Brief, donor) pairs repeatedly **in one process** and compares the warp's own
output — both gap vectors, the tiling's index spans, and the delivered per-room
areas — so the answer is about the solvers and not about anything the run loop
does between them. Twelve pairs, four repeats:

```
warp non-deterministic on 1 of 12 pairs        (two distinct tilings, same inputs)
pipeline outcome non-deterministic on 0 of 12  (status / valid / placed stable)
```

So **the warp genuinely returns different tilings for identical inputs at a
fixed seed**, at a rate around 8 % per candidate on this sample. That is the
mechanism, and it is enough on its own: a different tiling is a different
Envelope, a different Proposal and a different projection problem.

**What is still NOT established.** `mida-125`'s own warps all finished well
inside the cap (0,25 – 1,46 s) and its projections all proved INFEASIBLE in under
0,2 s, and the twelve pairs above showed no outcome flip at four repeats. So the
warp's non-determinism is confirmed while the specific `mida-125` flip is not
attributed to it — a bigger repeat count on that Brief's own pool would settle
that, and was not run.

**Why it matters.** `annotation.md` §3.1's tie-break exists so that *"a
regenerate with an unchanged Plan produces an unchanged set"* — that promise is
about the DRAWING and it holds. Nothing on this map has ever promised the
**Plan** is reproducible, and C7 makes edit-and-regenerate the whole
post-generation story: a Homeowner who changes one room and gets a different
dwelling back has not edited anything. If reproducibility is a product promise,
`max_time_in_seconds` has to become `max_deterministic_time` on both stages, and
the cost of that is unmeasured.

`num_workers = 1` is already set on the warp, so the remaining source is the
clock: `max_time_in_seconds` interrupts the search at a wall-clock instant that
moves with machine load. `max_deterministic_time` is the parameter that does not,
and swapping it is a one-line change whose cost — in refusals, and in the tail
`fit_warp` currently buys with those extra seconds — is unmeasured.

## What the drawing layer is

`src/bim_engine/` — the first shipping code in this repo, and the split is
deliberate. `experiments/` holds measurement rigs that are thrown away;
`openings.md`, `annotation.md` and the Drawing check are specifications the
engine uses verbatim, so they are implemented once, in `src/`, and the demo
harness imports them.

| Module | Implements |
|---|---|
| `profile.py` | the region profile, READ. No dimensional constant is transcribed |
| `model.py` | Plan, Space, Face, Opening, on the clear plane in integer mm |
| `build.py` | ADR 0001's erosion forwards; wall bodies at per-edge thickness |
| `openings.py` | `openings.md` §2–§7 |
| `dimensions.py` | `annotation.md` §4, tiers 1 / 2 / 2b / 3 and setting-out |
| `tags.py` | §7's tag and its degradation ladder, §7.2's area fraction |
| `schedules.py` | §6's three schedules, totals computed from printed cells |
| `sheet.py` | §9's sheet ladder, §10's title block and general notes |
| `dxf.py` | §11, avoiding all three traps it names |
| `preview.py` | a rendered sheet, from the same derivation |
| `check.py` | §13's twelve predicates |
| `selftest.py` | §14, number by number |

`ifc-export.md` is **not** implemented. It is the third unrun spec and it is the
obvious next one; nothing in this note bears on it.

## Two things this note does not establish

**It is not a quality judgement of the plans.** The sheets are correct against
their specifications and the geometry is what the warp and the projection
produced. Whether a Baku architect would issue them is a different question and
needs a Baku architect; `plan-quality-metrics-in-practice.md` is the note that
would hold the answer.

**It measures twelve Briefs and 88 candidates, and F4's arms ten and 72 — not a
population.** F4's three arms
are paired and their ordering is stable, but 72 is a small denominator and the
Briefs were drawn from one seed. What is established is that the failure modes
exist, that they are reproducible, and that the `rig` -> `min` -> `max`
ordering on the door threshold is monotone; the *rates* are indicative and
should be re-measured at the depth `experiments/warp/best_of_m.py` runs at
before anything is decided on their exact values.
