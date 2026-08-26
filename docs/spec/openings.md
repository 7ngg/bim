# Opening spec: which opening, where, hinged which way

Where every door and window in a `Plan` goes. Resolves *Opening placement rules*.
Companion to [ADR 0021](../adr/0021-a-door-is-placed-by-walking-in-and-none-swings-into-circulation.md).

*Canonical geometry model* settled what an Opening **is** — hosted, typed from a
regional catalogue, three widths that are not the same number, swing structural
rather than decorative. It deliberately did not settle where each one goes,
because that is a rule and not a representation. This is that rule.

**The standard is a Practitioner's own output**, per C2: a door position an
architect would not move. A door mid-wall in a room that is otherwise
dimensionally fine is one of the two or three things that most makes a generated
plan read as generated, and §3 exists to prevent it rather than to hope.

Every number is in integer millimetres. Every width states which of the three it
is: **structural opening**, **block**, or **leaf**. There is no fourth, and
*clear* is deliberately not published — see §2.3.

---

## 1. What this document decides, and what it reads

| Decides | Reads |
|---|---|
| Which catalogue entry an Opening takes (§2) | The `AZ` catalogue and its marks — `profiles.AZ.openings` |
| Where along its segment it sits (§3) | `open.fits_segment`, `open.leading_edge_nib` |
| Hinge side, swing direction, handing (§4) | `open.swing_within_space`, `open.swings_disjoint` |
| Which openings carry a leaf (§5) | `is_private`, `is_wet` |
| How many windows a Space gets and how wide (§6) | `win.area_ratio`, `win.habitable_has_window` |
| Where the entrance door goes (§7) | `entry.exists`, `entry.single_primary`, ADR 0003's edge ring |
| What the solver must reserve so §3 is satisfiable (§8) | `circ.potential_reachability` |

It does **not** decide the catalogue's contents — those are *The Azerbaijani
region profile*'s and are shipped. It does not decide the entrance *edge*, which
ADR 0003 §7 fixes before the solve, one ring per candidate. It receives both.

---

## 2. Which catalogue entry

### 2.1 The mapping

Doors are chosen by the **receiving** Room — the more private of the pair, the
one the door belongs to when you name it out loud ("the bathroom door"). Where
both sides are equally private, the narrower entry wins, because a door is sized
by what it serves, not by what it is approached from.

| Receiving Room | Catalogue key | Mark | Structural opening |
|---|---|---|---:|
| `wc`, `bathroom`, `shower_room`, `storage` | `door_bathroom_wc` | DG 21-7 | 2100 × 700 |
| `bedroom_principal`, `bedroom_double`, `bedroom_single`, `study`, `kitchen`, `utility` | `door_kitchen` | DG 21-8 | 2100 × 800 |
| `living`, `dining`, `living_dining`, `kitchen_dining`, `living_dining_kitchen` | `door_living_glazed` | DO 21-9 | 2100 × 900 |
| flat entrance (C5 preset `flat_*`) | `door_flat_entrance` | DU 21-9 | 2100 × 900 |
| house entrance (C5 preset `house_*`) | `door_building_entrance` | DN 21-13 | 2100 × 1300 |

**800 is the interior door, not 900.** Neufert's rule of thumb — room doors
≈ 800 clear, bath/WC ≈ 700, entrance ≥ 900 — was the ticket's starting point and
lands on the same rung as the AZ catalogue's own series, which is the check that
matters: DG 21-8 is the ordinary interior door of a post-Soviet flat and DG 21-9
is what you draw for a *zal*. Taking 900 everywhere would have been Neufert read
one size up, and it costs 100 mm of reserved contact run on every internal door
under §8 for nothing.

**`storage` takes 700, not 800.** A pantry door is a *kladovaya* door, and the
catalogue's narrowest entry is what an AZ set draws for it. `utility` stays at
800 because a washing machine goes through it.

`hall`, `corridor` and `entrance_lobby` never appear in this table because they
are never the receiving Room: a door between a hall and a bedroom is the
bedroom's. `corridor` and `entrance_lobby` are in any case unreachable in v1 —
see §9.

### 2.2 The glazed living-room door is evidence, not decoration

`door_living_glazed` (DO 21-9) is a **glazed** interior door, and its presence in
a catalogue derived first-hand from GOST 6629-88 is the strongest evidence in
this document about §5. A catalogue that ships a purpose-made glazed door to the
living room is describing a construction culture in which the living room
**has a door**. §5 follows that rather than the Western prior the ticket carried
in.

The drawing consequence — a glazed leaf draws a glazing line where a solid one
does not — is `annotation.md`'s, not this document's. Handed to its holder in
§10.

### 2.3 Three widths, and only two are published

CONTEXT requires that which width is meant is always stated. It does not require
that all three exist as data, and one of them should not.

- **Structural opening** — the void in the wall, `verified`, read off the GOST
  mark. `DG 21-8` is 2100 × 800: the mark reads *height*-then-*width*, so the
  second number is the width and never the reverse.
- **Block** — the frame-and-leaf assembly, `verified`: `block = opening − 30`
  wide, `2071` high for the 21-series. Every block height is **odd** and must
  never be keyed off, which the profile already says.
- **Leaf** — `derived` by the stated rule `leaf = opening − 100`. This is not an
  invented offset: applied to the catalogue's five door openings it reproduces
  GOST 6629-88's published leaf series exactly — 700 → 600, 800 → 700,
  900 → 800, 1300 → 1200 — which is the check that promotes it from a guess to a
  derivation. Leaf height is 2000.
- **Clear** — **not published in v1.** It is the block width less two frame
  sections, and the frame section is a joinery detail the region profile does not
  carry. No shipped rule consumes clear width; inventing one would be precisely
  the invented-dimension tell CONTEXT warns about. A Practitioner reading the
  schedule sees a structural opening and a leaf, both real.

Leaf width is load-bearing beyond the schedule: `open.swing_within_space` builds
the swing footprint from it, so a bathroom door sweeps a 600 mm square and not a
700 mm one. Getting this wrong would have made every wet room 100 mm harder to
satisfy than it is.

Every published opening dimension is even, so ADR 0004 holds on openings as it
does on thicknesses: 700/800/900/1300 structural, 670/770/870/1270 block,
600/700/800/1200 leaf, 2000 leaf height.

### 2.4 The 700 mm bathroom door stands, and the refusal is written down

The standards findings flag conflict C4: 700 mm collides with accessibility
minimums, which start at 800 mm clear.

**700 ships.** The `AZ` profile has already refused an accessibility-derived
figure once, with its reason on the record — `body_zone` is 300 mm, not AD M's
750 mm, because *"composing a private bathroom out of accessibility figures
produces a floor that rejects a third of real homes"*. Reversing here would make
the bathroom door the single accessible dimension in a dwelling that is
accessible nowhere else, which is worse than being consistently what it is. C8
forbids a compliance claim in either direction, so nothing is lost by being
plain: **v1 makes no accessibility claim, and this is one of the places that
shows.** Product copy says so; it does not say the doors are wide.

### 2.5 `balcony_door` is in the catalogue and can never be placed

`balcony_door` (BS 22-7,5) has no receiving Room in §2.1 and no rule anywhere
that would emit one, because **v1 models no balcony** — `brief.md` and
`acceptance-bar.md` both say so, and the area convention excludes balcony,
loggia, terrace and *eyvan* explicitly. It ships flagged `placeable_in_v1:
false`, the same marker `corridor` and `entrance_lobby` carry, rather than being
deleted: it is a real GOST entry and the day a balcony exists it should not have
to be re-sourced.

**One thing does rest on it and must stop.** `head_datum_mm` is 2200 and ADR 0012
justifies that number as *the balcony door's own catalogue head, because a
balcony door and the window beside it share a lintel* — a composition v1 cannot
draw. The **number is right and the reason is dead**: 2200 is the conventional AZ
window head, and it is right because window heads sit above door heads, which is
what a real elevation does and what makes doors read at their own 2100. Every
derived sill (700 / 700 / 1000) is unaffected. Re-anchoring to 2100 would collapse
the two head lines onto each other and is refused.

ADR 0012 is not this document's to edit. Handed to its holder in §10.

---

## 3. Where along the segment

### 3.1 The order is the order you walk in

Realised circulation is a tree rooted at the primary entrance. **Doors are placed
in breadth-first order from that root**, and each door is pushed to the end of
its shared run **nearest the point the path arrives at** — that is, nearest the
door through which the approaching Space was itself entered.

No search, no objective, no tie-break heuristic dressed up as a rule. Ties — the
two ends equidistant — break to the end with the smaller `x`, then smaller `y`,
so the output is deterministic and a regenerate with an unchanged Plan produces
an unchanged set.

This is the rule an architect follows without naming it. Its effect is the one
that matters: the door lands at a corner, and the **far wall of the receiving
room stays unbroken**. A room whose only door is mid-wall has no furniture wall,
and today's threshold does not merely permit that room — §8 shows it asks for it.

### 3.2 What "pushed to the end" means in millimetres

Measured in the **clear** run of the segment, from the finished face of the
perpendicular wall at that end:

```
jamb return          100 mm      the pushed-to end        (open.fits_segment)
structural opening   w
nib                  300 mm      the leading-edge end     (open.leading_edge_nib)
```

The nib is 300 mm **along the wall**, maintained 1200 mm back into the receiving
Space. So the minimum clear run a compliant door needs is `w + 400`, and it is
`w + 400` whichever end the door is pushed to — hinging at the far end merely
swaps which constant sits at which end. There is no cheaper arrangement, which is
why §8 is a change to the solver's reservation and not to this section.

Where the run is longer than `w + 400`, the surplus falls on the far side. The
door does not centre in it and does not distribute.

### 3.3 The receiving Space is the private one

Which of the two Spaces counts as "receiving" — for §2.1's catalogue choice, for
§3.2's nib, and for §4's swing — is fixed once:

1. The Space whose Room has `is_private` true, if exactly one does.
2. Otherwise the Space whose Room has `is_wet` true, if exactly one does.
3. Otherwise the Space further from the entrance in the circulation tree.
4. Otherwise the smaller Space.

---

## 4. Hinge, swing and handing

### 4.1 The hinge is derived from the position

**The hinge goes at the end the door was pushed to.** The leaf opens back against
that wall; the leading edge and its nib fall inboard, where §3.2 has already
reserved them. Handing is therefore never chosen — it is read off §3.1's output,
which is what keeps the door schedule's `Handing` column and the plan's swing arc
from being two independent decisions that can disagree.

### 4.2 A door swings into the private side, and never into circulation

**Swing direction is into the receiving Space of §3.3.** A bedroom door swings
into the bedroom, a bathroom door into the bathroom.

Fallback, in order:

1. Into the receiving Space. If `open.swing_within_space` or
   `open.swings_disjoint` fails there —
2. Into the other Space, unless that Space's Room is circulation
   (`hall`), which is never permitted for an internal door — see §4.3. If that
   fails too —
3. The Plan is **rejected**. It is not re-solved.

Step 3 is the residual risk *Acceptance validator spec* accepted and this
document confirms. With §8's reservation in place it should be rare, and when it
fires the cause is a Proposal that put two doors in one corner, which is a
Proposal-quality signal worth surfacing rather than papering over.

### 4.3 Exactly one door swings into circulation, and it is the front door

This is the whole of §11's corridor answer, so it is stated as a rule rather than
left as an outcome: **no internal door swings into a circulation Space.** The
entrance door does, into the hall, and it is the only one.

### 4.4 Cased openings have no hinge and no swing

A cased opening carries no leaf, so it has neither, and neither
`open.swing_within_space` nor `open.swings_disjoint` can fire on it — both are
hinged-only. §3.1 still positions it and §3.2's jamb returns still apply; the nib
does not, there being no leading edge. Its schedule handing cell reads `—` and it
draws no leaf and no arc.

This makes §5 a **feasibility** lever and not only a quality one, which is worth
knowing before reading §5's answer.

---

## 5. Which openings carry a leaf

**Every internal opening carries a leaf, except between `living` and `dining`,
which is cased.**

This reverses the ticket's premise, and the reversal is sourced rather than
preferred. The ticket asks *"what rule decides kitchen→living is cased and
hall→bedroom is not?"* — a question written from a Western prior, in which cased
openings are what make a plan read as a home rather than an institution. The one
profile v1 ships disagrees, in two independent places:

- **The catalogue ships a glazed living-room door** (§2.2). Nobody manufactures a
  purpose-made glazed interior door for a doorway that has no leaf.
- **AzDTN 2.7-2 requires no kitchen door — and that is a negative result, read
  first-hand, not an absence of evidence.** Every clause naming `mətbəx` — 5.2,
  5.7, 5.8, 9.12, 9.13, 9.14, 9.20 and the gas-appliance clauses at 7.3.7 and
  9.7 — is about area, height, daylight or ventilation. None mentions a door.
  So a cased kitchen is *permitted* in AZ, and it is still not what is built: a
  gas hob is the Baku norm and the smell and steam it makes are what the leaf is
  for.

The rule is therefore **not** a privacy-and-wet predicate. A predicate over
`is_private` and `is_wet` was the tidy answer and it produces the wrong plan
twice: it cases `hall`↔`living`, where the catalogue says a glazed door goes,
and it would have leafed nothing between `living` and `dining`, where the two
Rooms are one space in every real dwelling that has both.

**The Homeowner who wants an open kitchen gets it through the Brief, not through
placement.** `living_dining_kitchen` and `kitchen_dining` are Room types; a
merged Room hosts no internal opening at all, so the open plan is expressed by
merging Rooms rather than by deleting a leaf between two Rooms that still exist.
That keeps one fact in one place: whether two functions share a space is a
programme decision, and the acceptance bar's area, daylight and ventilation rules
all key off the merged type.

`kind` is therefore legible from this section's output — `door`, `entrance_door`,
`cased_opening` — which `annotation.md` §Doors requires in order to know whether
to draw an arc.

---

## 6. Windows

### 6.1 One window, sized from a series

> **Amended by *The annotation spec is US-shaped and the drawing is now
> Azerbaijani* (ADR 0024).** This section used to fix three catalogue sizes and
> vary the **count**. `win.area_ratio` has since moved from soft to **hard**
> (*A statutory floor, posted soft, in the one region v1 ships*), and against
> three fixed sizes a hard rule fails **21,20 %** of real dwellings against
> **5,39 %** against a width series — three quarters of the cost a catalogue
> artefact rather than a layout fact. The width now varies and the count does
> not. `openings.md` is amended by a ticket that does not hold it, because
> leaving it would ship two contradictory window rules.

**Height is fixed by the Space's Room; width is selected from a series.**

| Space's Room | Height | Sill |
|---|---:|---:|
| `living`, `dining`, `living_dining`, `living_dining_kitchen` | 1500 | 700 |
| `bedroom_*`, `study` | 1500 | 700 |
| `kitchen`, `kitchen_dining`, `utility` | 1200 | 1000 |

Heights are the ones the three retired catalogue entries already carried, so
every sill is unmoved — `sill = head_datum_mm − H` (§6.3), and the kitchen window
is still the short one that clears a 900 mm counter.

The width series is `profiles.AZ.openings.width_series_mm`: **600, 750, 900,
1200, 1350, 1500, 1800, 2100** on the published GOST grid, then **2400, 2700,
3000, 3300** as an engine extension of it. Every member is even, so ADR 0004
holds across the whole series.

**Selection.** One window per Space:

1. Take the Space's **longest** exterior run — Envelope edges only, and only
   those whose `condition` is `exterior`. A **party edge hosts no window**, so
   the run is computed over filtered faces and not over every boundary face.
2. Take the smallest series member reaching the region profile's **soft target**
   (0.154) that also satisfies `open.fits_segment` on that run — `w + 2 × 100`
   of jamb return within the clear run.
3. If no member reaches the target on that run, take the smallest member
   reaching the **hard floor** (`win.area_ratio`, 0.125) that still fits.
4. If no member reaches the floor either, the Space **cannot be glazed to
   cl. 9.13 on the run it has**. That is a hard failure of `win.area_ratio` and
   is reported as one. It is never quietly downgraded to the widest member that
   fits, which would ship an under-glazed room that the validator then rejects
   for a reason the placement layer already knew.

A single window centres on its clear run, rounded to even millimetres per
ADR 0004 — which keeps it off the corners without a separate corner rule.

**Why the count no longer varies.** Adding a window costs a **pier** that
produces no glazing, so on a constrained run one wide opening strictly dominates
two narrow ones — ticket 50 measured exactly this. The old algorithm's own
worked example shows both failure modes it produced: a `living` of 18,0 m² on a
4200 mm run got a second 1500 window to close a 0,029 gap and landed at ratio
**0,250**, nearly twice the target; a `kitchen` of 9,0 m² landed at **0,120**,
*below the floor*, and the example described it surviving on a soft penalty —
which under the hard rule is now a **rejected Plan**. Under the series the same
two rooms take one window each at 0,175 and 0,160.

The one thing splitting does buy is reach past the top of a bounded catalogue,
and the series extension removes that case: 3300 mm covers ticket 50's measured
p90 requirement of 3,23 m for `living_dining`. **Ticket 50 wrote that splitting
"buys nothing"; that is true when the wall run binds and false when the catalogue
top binds, and the two cases had not been distinguished.**

**What is given up, stated rather than glossed.** The old rule's even
distribution produced a regular facade rhythm, and a real elevation has one.
That argument is real and it is refused on measurement: the rhythm is bought
with glazing the room did not ask for, or — on a tight run — with a rejection.
`min_pier_mm` is now **250** and gates nothing in v1, because no shipped path
places two windows on one run; it binds again the day a balcony-door composition
is modelled.

### 6.2 The kitchen must have a window, and that is a change

Three shipped places disagreed about one window:

| Where | What it said |
|---|---|
| `ergonomic.rooms.kitchen.needs_window` | `false` |
| `profiles.AZ.windows.kitchen_windowless` | `false` — i.e. a windowless kitchen is **not** allowed |
| `win.kitchen_windowless` | severity **`warn`** |

AzDTN 2.7-2 cl. 9.12 is `verified` and mandatory: living rooms **and** kitchens
must have natural light, corroborated for individual houses at AzDTN 2.7-3
cl. 8.14. A Baku flat with a windowless kitchen is not buildable and not
sellable. **`kitchen.needs_window` becomes `true`**, which makes
`win.habitable_has_window` — already hard, already keyed on `needs_window` and
already requiring the window to sit on an External segment *of that Space* —
carry the rule at full strength.

Note what this does **not** need: `win.habitable_touches_exterior` keys on
`is_habitable`, and `kitchen` is `is_habitable: false` and stays so, because the
kitchen's daylight requirement and its habitability are different questions that
AzDTN answers differently. The facade contact arrives through
`win.habitable_has_window` instead, which is the rule that actually needs it.

**This costs exposure, and the cost is named rather than absorbed.** Forcing the
kitchen onto the facade adds one more room competing for frontage, which is
exactly the arithmetic *H8 and the single-aspect flat* is measuring. Handed there
in §10 with the delta stated.

`win.kitchen_windowless` can no longer fire once `needs_window` is true. Whether
the bar keeps it as belt-and-braces or retires it changes the 38-rule count, and
`acceptance-bar.md` is not this document's file. Handed on in §10; the rule is
left in place and annotated meanwhile.

### 6.3 Sills, heads and fall barriers are not placement

`sill = head_datum − catalogue H`, derived and never stored per instance (ADR
0012). On the shipped catalogue that is 700 for both window types at H 1500 and
1000 for the kitchen's H 1200, which clears a 900 mm counter — which is *why* the
kitchen window is the short one, and is the check that the datum is doing real
work. Every Fall barrier reads *unknown* and the schedule prints `—`: the height
is statutory and the trigger is refused, v1 having one Storey at elevation zero
and no site.

---

## 7. The entrance door

**The primary entrance is hosted on the segment between the invented `hall` and
the exterior that lies on an `entrance_side` edge.**

No search and no preference ordering, because the pieces already determine it.
`resolve` invents exactly one `hall`. ADR 0003 §7 fixes the entrance edge before
the solve — one ring per candidate, identified **by side and never by ring
index**. `proposer.md` §2.2.6 chooses the orientation variant that puts the
source dwelling's entrance-adjacent circulation on that edge. The hall exists to
be the room the front door opens into; if it does not touch an `entrance_side`
edge the candidate is already dead at `entry.exists`, before this rule is
consulted.

- **Position on that segment** follows §3, with the hall as the receiving Space:
  pushed to one end, jamb 100, nib 300. Its "point the path arrives at" is the
  segment itself, so the tie-break of §3.1 decides the end.
- **Swing is inward, into the hall**, and this is the one door that swings into
  circulation (§4.3). A common corridor is not in the model, so an outward swing
  is one this engine cannot check; swinging into the Space we own is the only
  direction whose clearance is verifiable. AzDTN cl. 7.2.x requires an outward
  swing from a *tambour* to a stair, which is the building's door and not the
  flat's.
- **A party edge may host it.** A party wall is `External` (CONTEXT, *Wall*), so
  a flat's front door onto a common corridor is already expressible; the
  `entrance_side` flag is orthogonal to `condition` for exactly this reason. A
  party edge hosts **no window** (§6.1) and **no entrance unless flagged**.
- **`is_primary`** is true on this door. A house may carry a second
  `entrance_door` with `is_primary` false — a back door — placed by the same rule
  on a different `exterior` edge. A flat gets exactly one.

Which Room holds the entrance and where on its segment it sits are both
**Assumptions** in the C4 sense: defaulted from knowledge, surfaced to the
Homeowner, editable in the Brief.

---

## 8. What the solver must reserve

`circ.potential_reachability` today admits a contact edge when the shared wall run
is at least `structural opening width + t_int`. ADR 0001 consequence 3 is explicit
that `+ t_int` is only the centreline-to-clear correction — *"a centreline contact
of length L yields a clear run of L − t_int, half a perpendicular wall eaten at
each end"*. So the reserved **clear** run is exactly `w`, with **zero** jamb and
**zero** nib.

§3.2's floor is `w + 400`. The two disagree by 400 mm, and the disagreement is not
academic: a solve can pass potential circulation on a run and then be hard-rejected
by `open.fits_segment` or `open.leading_edge_nib` the moment a door is placed on
that same run.

**The threshold becomes `structural opening width + t_int + 400`.** ADR 0021 part
1 carries the reasoning and the rejected alternative. Three things follow:

- A **corner-biased** door is now feasible by construction, which is what makes
  §3.1 a rule rather than a preference. Under the old threshold, a minimum-length
  contact admits exactly one door position — mid-wall — so the threshold was not
  merely permitting the room an architect would redraw, it was specifying it.
- Contact edges are lost and INFEASIBLE will rise. The arithmetic is exact, so the
  threshold ships on it; the **rate** needs `experiments/solver-toy/`, which
  belongs to *What an ordered entry sequence costs the solver*. Handed there.
- `open.fits_segment` must declare which face it measures. It reads *"the length
  of the WallSegment"* and a WallSegment's length is a centreline length, so
  `w + 2 × 100 ≤ L` is 50 mm looser than it reads. Every dimension in this system
  declares clear or centreline; this one did not. It now states **clear**, which
  is the reading §3.2 assumes and the stricter of the two.

---

## 9. Two room types this document cannot use

`corridor` and `entrance_lobby` are unreachable in v1 — nothing invents them,
no Brief may name them (`brief_nameable: false`), and `resolve` invents exactly
one `hall`. They ship with `reachable_in_v1: false`, the marker `kitchen_niche`
and `wardrobe_1room_entry` already carry, which `brief.md` §12 handed to
whichever ticket next held `room-constraints.json`. That is this one, and it is
done here rather than handed on a third time.

They are absent from §2.1's mapping for that reason and not by oversight. A room
type added later must arrive with a mapping row or `gate_check.py` fails.

---

## 10. What this document hands on

| Handed | To |
|---|---|
| **The INFEASIBLE cost of §8's threshold**, measured on the published rig. The arithmetic is exact; the rate is not | *What an ordered entry sequence costs the solver*, which holds `experiments/solver-toy/` |
| **The exposure cost of §6.2** — one more Room competing for frontage, on the arithmetic that ticket already measures | *H8 and the single-aspect flat* |
| **`win.kitchen_windowless` can no longer fire** (§6.2). Retire or keep as belt-and-braces; either way it moves the 38-rule count | *A dwelling with no toilet passes every check* or *Fit the ENGINE_CHOICE acceptance thresholds*, whichever next holds `acceptance-bar.md` |
| ~~**`win.area_ratio` counts party faces**~~ — ✅ **discharged** by *H8 and the single-aspect flat*, which added the exterior-face clause to the rule statement, and re-stated in §6.1 step 1 |
| ~~**`win.area_ratio` is `soft`**~~ — ✅ **discharged** by *A statutory floor, posted soft, in the one region v1 ships*: it is **hard**, rescoped to living rooms and kitchens, and its satisfiability is what rewrote §6.1 |
| **`open.leading_edge_nib`'s justification moves** from AD M accessibility to the region-invariant ergonomic layer (ADR 0021). The constant does not move; its `src` and `note` should | same |
| **ADR 0012's head-datum justification is dead** (§2.5). 2200 stands and its reason must stop being the balcony door's lintel | ADR 0012's holder |
| ~~**A glazed leaf draws a glazing line**~~ — ✅ **discharged** by ADR 0024. `annotation.md` §6 and §8 carry the schedule columns and the two-level mark scheme; the plan mark is a bare number for a door and `ОК<n>` for a window, and the GOST product designation moves to the schedule's `Type` column |
| ~~**The `min_pier_mm` 600 is `engine_choice`**~~ — ✅ **fitted to 250** by *Fit the ENGINE_CHOICE acceptance thresholds to the corpora* and written by ADR 0024. It now gates nothing, because §6.1 places one window per Space; it binds again the day a balcony-door composition is modelled |

---

## 11. Worked example

A 3-otaq flat, `flat_dual_aspect`, entrance on the north edge. Rooms after
`resolve`: `hall`, `living`, `kitchen`, `bedroom_double`, `bedroom_single`,
`bathroom`, `wc` — seven engine rooms, inside C13's 3–10 gate.

**Placement order** (§3.1, breadth-first from the entrance): entrance →
hall; then hall → living, hall → kitchen, hall → bedroom_double, hall →
bedroom_single, hall → bathroom, hall → wc.

| Opening | Entry | Structural | Leaf | Receiving | Pushed to | Swings into |
|---|---|---:|---:|---|---|---|
| entrance | `door_flat_entrance` | 900 | 800 | `hall` | tie-break, smaller x | `hall` |
| hall → living | `door_living_glazed` | 900 | 800 | `living` | end nearest entrance door | `living` |
| hall → kitchen | `door_kitchen` | 800 | 700 | `kitchen` | end nearest entrance door | `kitchen` |
| hall → bedroom_double | `door_kitchen` | 800 | 700 | `bedroom_double` | end nearest entrance door | `bedroom_double` |
| hall → bedroom_single | `door_kitchen` | 800 | 700 | `bedroom_single` | end nearest entrance door | `bedroom_single` |
| hall → bathroom | `door_bathroom_wc` | 700 | 600 | `bathroom` | end nearest entrance door | `bathroom` |
| hall → wc | `door_bathroom_wc` | 700 | 600 | `wc` | end nearest entrance door | `wc` |

Seven doors, no cased openings — there is no `dining` Room. Six swing away from
the hall and one into it, so the hall carries exactly one swing footprint, an
800 mm square, and its 900 mm clear floor contains it (§4.3, ADR 0021).

**Contact runs the solver had to reserve** (§8): 1300 clear for each 900 door,
1200 for each 800, 1100 for each 700 — against 900 / 800 / 700 under the old
threshold.

**Windows** (§6.1). One per Space, width selected from the series at the fixed
height for its Room, aiming at the 0.154 soft target and floored at the 0.125
hard rule:

| Space | Area | Run | H | 0.154 needs | Member | Ratio |
|---|---:|---:|---:|---:|---:|---:|
| `living` | 18.0 m² | 4200 | 1500 | 1848 | **2100** | 0.175 |
| `bedroom_double` | 12.0 m² | 3000 | 1500 | 1232 | **1350** | 0.169 |
| `bedroom_single` | 9.0 m² | 2400 | 1500 | 924 | **1200** | 0.200 |
| `kitchen` | 9.0 m² | 2400 | 1200 | 1155 | **1200** | 0.160 |

`bathroom` and `wc` are windowless, permitted at AzDTN cl. 9.14.

**Two of these rows are why this section changed.** Under the retired
fixed-size rule `living` took a *second* 1500 window to close a 0.029 gap and
landed at **0.250** — nearly twice the target, because the increment was a whole
window rather than a width. And `kitchen` landed at **0.120**, which this
example described as carrying a soft penalty and surviving; `win.area_ratio` is
now **hard**, so that same candidate is a rejected Plan. The series puts both
just above target on one window each.

⚠️ **This example also used to omit `bedroom_single`'s window entirely** — it
counted four window rows as two for `living` plus one each for `bedroom_double`
and `kitchen`, leaving a habitable Room with no window at all, which
`win.habitable_has_window` rejects hard. Corrected above: four windows, one per
habitable Space.

Sheet 2 carries **seven door rows and four window rows.**
