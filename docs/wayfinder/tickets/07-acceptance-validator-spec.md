---
id: 7
title: Acceptance validator spec
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: [5]
---

# Acceptance validator spec

## Question

Turn C6's seven-item bar into **precise, machine-checkable predicates with real
numbers and real tolerances**.

This is the spec for the layer that makes output correct rather than merely
plausible, and it is used twice: as the hard filter on generated candidates, and
as the constraint set the solver is projecting onto. Those two uses must not
drift apart, so the predicates are written once and consumed by both.

The bar as agreed while charting:

1. Circulation is correct — every room reachable from the entry without passing
   through a bedroom or bathroom.
2. Minimum dimensions per room type met; no unusable slivers, no sub-1m corridors.
3. Every door physically fits its wall and its swing hits nothing.
4. Every habitable room touches an exterior wall and gets a window.
5. Wet rooms clustered so plumbing shares walls or stacks.
6. Walls orthogonal, thicknesses standard, junctions closed — no gaps, no overlaps.
7. Circulation area within a sane fraction of the total.

For each, settle:

- **The exact predicate.** "Reachable without passing through a bedroom" needs a
  defined graph: what are the nodes, what makes an edge, is a door required or
  does an opening count?
- **The number, and where it came from.** Comes from the constraint table produced
  by *Dimensional standards corpus*. "Sane fraction" and "sub-1m" are placeholders
  and must become values with a citation.
- **The tolerance.** Floating-point geometry never closes exactly. What
  counts as a closed junction, a coincident wall, a zero-area sliver?
- **Hard or soft.** Which failures reject a plan outright, and which are scored
  and surfaced as warnings? A rule that rejects 99% of candidates is a bug in the
  rule, not a quality bar.
- **What the Homeowner sees when a rule fires.** C4 established that assumptions
  are surfaced; failures deserve the same treatment.

Also settle two things the seven items do not cover:

- **Entry.** What defines the front door, and is exactly one required?
- **Total-area agreement.** The brief states a target area. How far may the
  produced plan drift before that is a failure?

**Inherited from *Canonical geometry model*, now closed** — do not re-derive:

- **The tolerance question is deleted, not answered.** The model is **integer
  millimetres**, so "closed junction", "coincident wall" and "zero-area sliver" are
  integer equalities, not tolerances. Tolerance exists only at import boundaries.
- **C6 item 2's "sub-1m corridors" placeholder resolves to 900 mm** — minimum clear
  width of every hall or landing, AD M M4(2) ¶2.22a, with a 750 mm pinch allowed
  for no more than 2 m (¶2.22b). VERIFIED, OGL-licensed.
- **Two new predicates** the geometry model asks for: `len(storeys) == 1`, and
  *Space polygon equals the centreline rect eroded by `t_int/2`* — the second is
  what keeps a cheap derivation honest, and it fails the day internal wall
  thickness stops being uniform.
- **Item 3's swing clearance has no finished predicate in the corpus** — only
  components: a 300 mm nib to the door's leading edge maintained back 1200 mm; 1500
  mm between lobby doors and between swings; the entrance-level WC door opening
  outwards overlapping the pan by 250 mm. Composing them is this ticket's job, and
  *Opening placement rules* consumes the result.
- **Areas are measured on the Space polygon** — but which measurement convention
  that is remains open, in *Area measurement convention*. Until it closes, do not
  assume the minimum areas in `data/standards/room-constraints.json` and the
  computed Space areas are the same quantity.

Deliverable: the predicate spec, with each number traced to its source. Note for
the session: the sibling project measured overlap by both bounding box and true
polygon intersection and found they agreed for a box-emitting backend — the
polygon metric is the one that survives a change of generator. Re-verify per C11
rather than inheriting the finding.

## Resolution

**37 predicates, 28 hard, shipped as a registry rather than a function — and the
hard set carries no region at all.**

Canonical: **`data/acceptance/rules.json`**. Prose spec, with every number traced:
**`docs/spec/acceptance-bar.md`**.

### The five decisions that shaped it

1. **"Written once, consumed twice" is a *declaration*, not an implementation.**
   The solver posts inequalities over centreline grid integers before geometry
   exists; the validator evaluates finished geometry in clear millimetres; rules
   about Openings are **unpostable by construction**, because Openings are placed
   post-solve. Every rule declares an enforcement site — `solver` (1), `validator`
   (22), `both` (14) — and drift is prevented by a **conformance test over the
   `both` subset**, not by shared code. Forcing one function would have made the
   unpostable rules lie.

2. **The hard floor is the ergonomic minimum, not a legal one — so the hard rule
   set is region-free.** The table's own binding (`hard_reject_below:
   statutory_floor`) is **unusable**: that tier is `null` for the default region
   because German law prescribes no minimum room areas, so it yields an *empty
   hard set* and a 4 m² double bedroom passes. Replaced by the smallest clear
   rectangle the room's fixtures and body clearances occupy — defensible where no
   law exists, region-invariant because bodies are, and it lets v1 ship without
   settling the region list. **Consequence: adding a region can change which Plans
   are preferred, never which are rejected.** Region touches soft objectives only.
   The validator reads **two** of the four tiers; `statutory_floor` and
   `accessible` stay in the schema, unread.

3. **C6 item 1 as written rejects every plan with an ensuite.** `is_private` is
   true on bedrooms *and* bathrooms, and an ensuite is reachable only through a
   bedroom — so both the predicate and the solver's *private rooms never forward
   flow* break on the commonest plan in the market. Fixed in the **Brief**, not
   the predicate: a Room may declare **`access_via`**, because access-through is
   **program**, not geometry. The exception makes the rule *stronger* — an ensuite
   opening onto the hall now fails. Circulation also splits into two named graphs,
   **potential** (solver, contact graph, "a door could go here") and **realised**
   (validator, opening graph, "a door is here"), which is what lets the system
   notice a valid solve handed no door.

4. **Two rules were deliberately loosened to survive contact with real homes.**
   Wet clustering: the solver posts it as hard flow demanding *one* group, which
   rejects a front kitchen with a rear bathroom — so it becomes **at most 2
   plumbing groups**, hard and still postable, with shared wet-wall length as the
   soft gradient inside. Total area: **two rules, because `Envelope` has two
   modes** — invented (house) is ±5% hard, given (flat) is **warn only**, since
   area is fixed by the Envelope and every candidate drifts identically. Rejecting
   there is the ticket's own 99%-rejection bug at its limit: 100%.

5. **One rule nothing asked for.** A 2750 × 8250 bedroom meets its minimum area
   and its minimum width and is a bowling alley; nothing in the seven items
   catches it. **Aspect ratio ≤ 3.0 hard, ≤ 2.2 soft**, corridor/hall/storage
   exempt. `ENGINE_CHOICE` — no surveyed source states an aspect rule. Cheapest
   rule in the spec that moves output from *passes* to *usable*.

### Composed, deleted, and deferred

- **Swing clearance composed** with no fixture model: a **swing footprint** = the
  leaf-side square of side `leaf_width` at the hinge (bounding box of the swept
  quarter-disc), required inside its Space and disjoint from every other, plus the
  VERIFIED 300 mm nib maintained 1200 mm back. Footprint disjointness *generalises*
  AD M's 1500 mm lobby rule to every arrangement.
- **Three questions deleted rather than answered**, all by ADR 0001's integer
  millimetres: "no unusable slivers" is not a predicate (Spaces are rectangles;
  min width + min depth covers it); the bbox-vs-polygon overlap comparison is
  **discharged by construction**, so no C11 re-measurement is owed; and AD M's
  750 mm corridor pinch allowance is dropped, because a rectangle has no localised
  narrowing and the rule could never fire. Corridors: **900 mm hard**, VERIFIED.
- **Windows stay topological**, because the four regimes are not interconvertible
  and Japan's is a function of the site, not the room. Ratio soft, default 1/8.
  Windowless kitchen: **warn** — the German rule that permits it assumes
  mechanical extract we do not model.
- **One rule is `deferred`, visibly**: AD M's outward-opening WC door overlapping
  the pan by 250 mm needs a pan. Carried with its source so adopting it later is a
  data change. A validator that silently omits a rule it cannot evaluate is
  indistinguishable from one that never knew about it.
- **Zero survivors: diagnose, never show a failing Plan.** The bar's invariant is
  the point of the bar. The diagnosis is arithmetic, not search — the sum of hard
  minima plus a circulation allowance is a lower bound on feasible GIA:
  *"Three bedrooms, a bathroom and a kitchen need at least 58 m². Your brief says
  45 m²."*

### ⚠️ The deliverable it depends on does not exist

`data/standards/room-constraints.json` is a **9 KB stub** ending in
`PLACEHOLDER_NOTE: "DE and US sources, the ergonomic layer, and the room table are
appended below in the completed file."` It has UK sources and the
region/tier/flag models; it has **no ergonomic layer, no room table, no DE or US
sources**. The room table exists only as prose in the findings doc §8, `DE` /
`market_default` column only. *Dimensional standards corpus* and the map both
record it as shipped.

So `dim.min_area`, `dim.min_clear_width` and `dim.min_clear_depth` are
`conf: pending`, and `win.area_ratio` cites a dangling `de_baybo` key. **Their
structure is final; only their values are missing.** Ticketed as *Ergonomic minima
and the constraint table's missing half*. 19 of 37 rules are `ENGINE_CHOICE` and
are ticketed for a corpus fit in *Fit the ENGINE_CHOICE acceptance thresholds to
the corpora*.

### Landed in `CONTEXT.md`

**Dependent room**, **Swing footprint**, **Potential circulation**, **Realised
circulation**, **Plumbing group**, **Ergonomic minimum** — and the **Acceptance
bar** entry corrected: it claimed one definition that cannot drift, which was the
thing this ticket found to be false.
