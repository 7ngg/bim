---
id: 39
title: The Plan has no vertical dimension, and three artefacts already assume one
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - CONTEXT.md
  - data/standards/room-constraints.json
  - docs/research/vertical-dimensions.md (new)
  - docs/adr/0012-one-vertical-datum-and-it-is-the-clear-height.md (new)
  - experiments/region-profile/gate_check.py
  # openings.md DROPPED -- see Resolution item 7; 16 creates it and inherits the
  # boundary from CONTEXT.md instead. Three shared artifacts -> two.
---

# The Plan has no vertical dimension, and three artefacts already assume one

## Question

**The geometry model has no Z.** `CONTEXT.md` defines a Wall as *"a centreline and
a thickness"* and an Opening by **three widths**. Nothing in the model says how
tall anything is. Grep for a ceiling height, storey height, room height or opening
head height across `room-constraints.json`, `acceptance-bar.md`, `brief.md` and
`CONTEXT.md` and **nothing comes back**.

Surfaced by *What IFC the engine actually emits*. It is not an IFC problem — IFC
is just the first consumer that cannot proceed without one. **Three artefacts
already assume a vertical dimension that nothing supplies:**

1. **`annotation.md`'s door schedule** ships a `Structural opening W × H` column,
   and its **window schedule** ships `Structural opening W × H` *and* `Sill
   height`. Three columns that cannot be filled from the model as it stands.
2. **`CONTEXT.md`'s Storey** — *"the level a Plan's geometry sits on… It exists
   because the model would otherwise have to invent it on export."* It exists for
   export and carries no height, so export still has to invent one.
3. **`ifc-export.md` §12** — every wall body is an extrusion, every `IfcSpace`
   needs a `Height` and `NetVolume`, every window a sill and every door a head.
   The spec names the four inputs and **refuses to default them**.

A real unowned component, of exactly the class the map's done-test exists to
catch: *Opening placement rules* writes `openings.md` and its body does not
mention height at all; nothing else is near it.

**This is one ticket, not two, and that is deliberate.** Finding the numbers and
deciding where they live cannot be split, because *where* a number lives changes
*which* number you need — a height on the Region profile is one value for the
dwelling, a height on the Opening catalogue is a value per door type, and a height
on the Wall is a per-instance field that only a model with parapets or dropped
ceilings can justify. Answer the model question and the research question in the
same session, in that order.

⚠️ **`writes:` collision, read before claiming.** This ticket touches `CONTEXT.md`
(shared with 21, 31), `room-constraints.json` (shared with 16, 31, 32) and
`openings.md` (**16's sole artifact**). It is the widest write-set on the map. The
`openings.md` overlap with *Opening placement rules* is the sharp one — see item 2.

**Decide:**

1. **What the model gains, and where.** At minimum `h_storey` (floor to floor) and
   `h_clear` (floor to ceiling) — and whether the difference is *modelled* (a slab
   plus a build-up, which is a second layer set and a second ADR 0010 problem) or
   whether the two are simply two published numbers with the gap left unexplained.
   Then the harder half: does a **Wall** gain a height field, or is height a
   property of the **Storey** that every Wall reads? v1 is single-storey with no
   dropped ceilings, so a per-Wall height has no user today — but ADR 0001's
   `load_bearing` hook is the precedent for paying for a field before its consumer
   exists, and that precedent was recently vindicated. Decide which case this is.

2. **Whether opening heights are catalogue or instance**, and settle the boundary
   with *Opening placement rules*. `CONTEXT.md` already says an Opening is
   **typed** from a regional catalogue *"rather than dimensioned freely"* — *"a
   door of an invented width is the clearest tell that a plan was generated"*. If
   width is catalogue, height almost certainly is too, and then the door head is a
   catalogue column and not a placement rule. **Sill height is the one that
   probably is not** — it varies by room and by what is outside. Draw the line and
   write it into `openings.md` so 16 inherits it rather than colliding with it.

3. **What the Azerbaijani source says**, read first-hand. **AzDTN 2.7-2** is the
   live residential design norm and the ticket-25 trap applies with full force: a
   number off **СНиП 2.08.01-89\***, whose legal force in Azerbaijan terminated
   2021-11-30, is folklore *and* repealed, and publishing it would be the exact C8
   breach ticket 25 existed to prevent. Baku sits in a climate sub-region and this
   norm family has historically varied minimum room height by one, so check
   whether AzDTN 2.7-2 does. `conf` flag per value like every other cell.

4. **Whether any of it is `hard`.** A minimum room height is the first plausible
   *statutory* vertical floor on this map. If AzDTN 2.7-2 publishes one, decide
   whether it reaches `rules.json` as a predicate or stays a profile value the
   engine simply obeys — noting there is **nothing for it to constrain**, because
   the solver is 2D and could not violate it. That may well be the answer: **a
   published value with no predicate**. Record it as a deliberate outcome rather
   than inventing a rule to give the number a home.

5. **Whether the ergonomic layer owes a height too.** ADR 0009's floor is
   region-invariant and derived from fixture footprints, all of them in plan. A
   *height* is not a fixture footprint, and every clearance in that source corpus
   turned out to be an accessibility figure. If no region-free ergonomic height is
   derivable, **say so** — an empty answer recorded is worth more than a borrowed
   one, and this layer has already refused one number it was handed.

6. **Whether the Brief may state a height.** C4 makes the Brief the real
   interface and its defaults ladder is `market_default` → corpus median →
   absent. The corpus rung is **dead here** — Swiss Dwellings and ResPlan are both
   2D and neither carries a height — so the ladder has two rungs, not three, for
   this field. Decide whether a Homeowner can ask for a high ceiling at all, and
   what the `Assumption` reads when they do not.

**Explicitly not this ticket:** multi-storey, stair alignment, or anything that
follows from more than one `IfcBuildingStorey`. C5 and the map's Out of scope
section already rule those out. Exactly one storey; this ticket gives it a height.

Deliverable: the vertical values in `room-constraints.json` with `conf` flags and
sources; the model decision in `CONTEXT.md`; the catalogue-versus-instance
boundary in `openings.md`; findings in `docs/research/vertical-dimensions.md`; and
a one-line statement of which of `annotation.md`'s three schedule columns each
value fills.

---

## Resolution

**v1 has exactly one vertical datum, `h_clear`, and every other vertical value is
expressed against it or refused.** ADR 0012. Findings
`docs/research/vertical-dimensions.md`; values `profiles.AZ` in
`room-constraints.json`; gates `experiments/region-profile/gate_check.py`,
**33 → 67 assertions, all pass**.

### The premise was half false

A grep for a ceiling, storey, room or opening head height **does not** return
nothing. Ticket 25 had already landed `clear_heights_mm` (2700 / 2100, `verified`,
AzDTN 2.7-2 cl. 5.8, **statutory**, "nationally, with no climatic carve-out" —
item 3's climate worry answered before this ticket opened) and the opening
catalogue already carried head heights in its marks. The IFC session that raised
this grepped for *names*, not values. Two of §12's four inputs were shipped; the
work was **two numbers and a model decision**.

Two further unfilled slots the ticket did not list, one of them a safety number:
`annotation.md` general note 4's *"Clear ceiling height `H` mm"*, and the
window-schedule **`Fall barrier`** column — `CONTEXT.md` defines the term,
`annotation.md` prints the column, and **no guarding value existed anywhere**.

### 1. What the model gains, and where

**`h_storey` is deleted, not deferred.** AzDTN 2.7-2 **prescribes no storey
height**: `mərtəbə hündürlüyü` occurs only in the §3 definitions and in the
passenger-lift table's Note 2, where the table is *compiled on the basis of* 2.8 m
with Note 3 directing recomputation when it differs. That is a **lift-traffic
modelling assumption**, and publishing it would be ticket 25's trap in new
clothes — a real number, from the right *live* document, doing a job it was never
written for. It fails arithmetically anyway: 2.8 over a 2.7 clear leaves ≈100 mm
for slab plus build-up.

Both consumers §12 claimed for it are empty: `IfcBuildingStorey` spacing is vacuous
at one storey pinned to `Elevation = 0.0`, and wall extrusion height is a *choice*
because the export authors **no `IfcSlab` and no `IfcRoof`** — nothing rests on a
wall. **The cheap answer was not available**: an extrusion cannot omit its depth,
so ADR 0011's *absent is unknown* does not reach here, and the choice was forced
between a number derived from a statutory `verified` figure and one invented from
an unsourced build-up. Same move ADR 0010 made on the horizontal.

Declared consequence: **a wall body is floor-to-ceiling, not slab-to-slab**, and
the export states the understatement rather than padding it.

**A Wall gains no height field.** Height is a property of the Storey every Wall
reads. ADR 0001's `load_bearing` hook is the precedent for paying early, but it
exists because load-bearing *varies between walls and is genuinely unknown*; one
storey with no dropped ceilings has one height, known and shared, and a per-Wall
field would store the same number N times — the justification *One internal
thickness* already killed by count.

**One `h_clear` per Plan**, resolving `annotation.md`'s single general note against
the profile's two values in annotation's favour. cl. 5.8's corridor figure is a
**conditional allowance to reduce** — *insanların hərəkətinin təhlükəsizliyini
təmin etmək şərtilə* — not a second requirement; exercising it asserts a safety
judgement this engine cannot make and buys a dropped ceiling with no build-up.
Kept as `verified` data flagged **inert**, the posture balcony coefficients hold.
cl. 5.8 also settles the **plane** the cells never recorded: *(döşəmədən
tavanadək)*, floor to ceiling, in the source's own words.

### 2. Catalogue versus instance

**Height is catalogue, placement is not.** A GOST mark is `<type> <height>-<width>`
— height first, so `OR 15-12` is 1500 × 1200. **AzDTN publishes no sill**
(`pəncərə altlığı`: zero hits in the full 2021 text), so a per-room-type table
would be four invented numbers. Instead one identity: `sill = head_datum −
catalogue H`, with **`head_datum_mm` = 2200** taken from the **balcony door's own
catalogue head**, because a balcony door and the window beside it share a lintel.
Structure derived, one constant taken from the catalogue rather than from nowhere —
ADR 0009's shape. Yields **700 / 700 / 1000**, the kitchen clearing a 900 mm
counter, which is why the kitchen window is the short one — a relationship nobody
had noticed and the gate now asserts.

### 3–4. The Azerbaijani source, and what is hard

Read first-hand from the live 2021 instrument (`pymupdf`, not `pdftotext`, per
ticket 35). cl. 5.8 confirms both shipped heights verbatim. **cl. 8.3** supplies
the missing safety number: guarding **1.2 m**, `az olmamalıdır` = **məcburi**, so
**statutory**, corroborated at cl. 8.10.

**No predicate reaches `rules.json` from the solver side** — it is 2D and cannot
violate a height, exactly as the ticket anticipated. But item 6 flipping makes one
possible from the *Brief* side, and that one is real: a Brief can state 2400
against a statutory 2700. Hard Brief error on `area.convention_agrees`' precedent —
rejects the request, not the candidates. The profile-level checks (every catalogue
head under `h_clear`, every window under the datum) judge the **profile**, not the
Plan, so they go in `gate_check.py` on the Drawing-check and IFC-check reasoning.

### 5. The ergonomic layer owes nothing

Zero vertical figures in the layer; every number in it is a fixture footprint **in
plan**. No region-free ergonomic height is derivable. **Recorded as an explicit
refusal** rather than left as an absence — the ticket's own instruction, and this
layer has refused a handed number once already.

### 6. The Brief may state a height — REVERSED mid-session

The first answer was to refuse the field, and it was the easy one. An architect
never *invents* floor-to-ceiling; it is a building given. Baku stock spans Soviet
≈2.5 to new-build 3.0–3.2, so hard-coding 2700 asserts a fact about the user's
building nobody stated. C4 exists for this. Ladder has **two rungs, not three** —
the corpus rung is dead, both corpora being 2D. Floored at cl. 5.8's statutory
2700.

### 7. `openings.md` was deliberately not created

The ticket instructed writing the boundary into it. **The file does not exist** and
ticket 16 creates it; authoring a new spec file another ticket owns, to carry two
sentences, maximises the exact collision the map's `writes:` rule prevents — and 39
already had the widest write-set on the map. The boundary lives in `CONTEXT.md`'s
**Opening** and new **Head datum** terms and in the profile data, so 16 inherits it
rather than colliding. Write-set: three shared artifacts → two.

### What bites hardest

**The `Fall barrier` trigger is refused, and the refusal is the finding.** An
`engine_choice` threshold of 1000 mm was drafted and gated — and it returned *every
catalogue window guarded*, including the kitchen, which is visibly wrong for a
post-Soviet flat. That exposed the real question: not *what threshold*, but
**whether this model can evaluate one at all.** It cannot, and not for want of a
constant. cl. 8.3 reaches windows only through *yıxılma təhlükəsi olan digər
yerlər* — other places with a **risk of falling** — which depends on the **drop
below the window**: which storey, and what is outside. v1 has one Storey at
elevation 0, `IfcSite` is out of scope, and the site is ruled out of scope on the
map. **A ground-floor window needs no barrier; the same window eight floors up
does; nothing in the model distinguishes them.** So the height is published and the
trigger refused; the schedule column reads `—`, which `annotation.md` already
provides for. Picking a number would have been a **safety** claim with no source
and no way to evaluate it — C8, and the breach ticket 25 exists to prevent. Gated,
so a later session cannot quietly supply one.

⚠️ **The gate corrected this ticket twice.** It caught the `OR 15-12` mark read
width-first (bedroom sill 900 → **700**), and it is what surfaced the
guarded-kitchen absurdity that killed the trigger. Both errors were ours; the
profile's own catalogue notes were right throughout.

⚠️ **`ifc-export.md` contradicts itself and this ticket cannot fix it**: §5 gives
`IfcSpace.Body` as *"extruded to storey height"* while §12 assigns `h_clear` to it.
A Space is floor-to-ceiling. Routed with the rest in `vertical-dimensions.md` §9,
along with the Brief field (38), the Brief predicate (16/20/26), and the annotation
columns (32).
