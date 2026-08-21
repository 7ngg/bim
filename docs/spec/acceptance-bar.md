# The Acceptance bar — predicate specification

Resolves [Acceptance validator spec](../wayfinder/tickets/07-acceptance-validator-spec.md).

Canonical form: **[`data/acceptance/rules.json`](../../data/acceptance/rules.json)** — 38 rules.
This document is a *reading* of that file, not a second source. Where the two
disagree, the registry wins.

Vocabulary is [`CONTEXT.md`](../../CONTEXT.md). Geometry is
[ADR 0001](../adr/0001-centreline-walls-over-a-dilated-solve-domain.md).
Numbers trace to [`data/standards/room-constraints.json`](../../data/standards/room-constraints.json)
and `docs/research/dimensional-standards.md`.

> **Not a building code.** C8. Every regulatory document cited here is cited as a
> source of *dimensional fact*, never as a compliance target. No legal
> code-compliance claim is made or implied by any rule in this spec.

---

## 1. The shape of the thing

C6 asked for one definition consumed twice — as the hard filter on candidates and
as the constraint set the solver projects onto — so the two could not drift.

**One definition cannot be one implementation, and pretending otherwise would
have been the drift.** The two consumers do genuinely different work:

| | Solver | Validator |
|---|---|---|
| When | before any geometry exists | on a finished Plan |
| Over | centreline integers on a 250 mm grid | clear integer millimetres, Spaces and Openings |
| Operation | **posts** linear inequalities | **evaluates** predicates |
| Can see Openings | **no** — they are placed post-solve | yes |

So a rule about a door swing is unpostable by construction, and a rule about
potential adjacency is unevaluable on a finished Plan without inverting it.

**The shared artifact is a registry, not a function.** Each rule declares an
**enforcement site** — `solver`, `validator`, or `both` — and drift is prevented
by a **conformance test over the `both` subset**, which is 14 of the 38 rules. The
test is: for a generated population of Plans spanning feasible and infeasible
Briefs, the solver's satisfaction of each `both` rule and the validator's
evaluation of it agree on every Plan. Disagreement is a test failure.

The registry is also what *Opening placement rules* and *Dimensioning and
annotation rules* read, rather than each re-deriving the numbers.

## 2. Severity, and how it is decided

`hard` rejects; `soft` scores; `warn` is shown beside a passing Plan; `deferred`
is a real rule with a recorded source that v1 cannot evaluate.

The ticket asked which failures reject and which are scored. For **dimensional**
rules that question is answered by the data, not by a per-rule flag: **the tier
the number came from decides it.** `ergonomic_min` is hard, `market_default` is
soft. That is the C10 split — model proposes, solver projects — expressed in the
constraint table rather than restated in the validator.

Rejecting on 29 of 38 rules sounds aggressive; it is not, because every hard
number is either a physical impossibility (a door that does not fit its wall, two
Spaces overlapping) or the point at which the room cannot contain its function.
The ticket's own test applies: *a rule that rejects 99% of candidates is a bug in
the rule.* Two rules were deliberately loosened to satisfy it — see §5 and §7.

## 3. Where the hard numbers come from — and why they carry no region

`room-constraints.json` binds `hard_reject_below: statutory_floor`. **That binding
is unusable.** Findings §8: *"`statutory_floor` areas … are `null` for `DE`
because German law prescribes none."* The default region is `DE`. So the hard set
under that binding is **empty**, and a 4 m² double bedroom passes.

Replaced by: **the hard floor is the ergonomic minimum** — the smallest clear
rectangle the room's required fixtures and their body clearances occupy.

This is not a workaround. It is the better rule, for three reasons:

1. **It is defensible where no law exists**, which is most of the world. Where a
   region prescribes nothing, "furniture fits" is a real bar; "no bar" is not.
2. **It is region-invariant, because bodies are.** The constraint table already
   splits an ergonomic layer from a conventional one for exactly this reason.
3. **It lets v1 ship without settling the region list.** Consequence, stated
   plainly: **the entire hard rule set carries no region.** Adding a region can
   change which Plans are *preferred*, never which are *rejected*. Region
   parameterises soft objectives only — `dim.market_default_area`,
   `win.area_ratio`, the thickness catalogue, the opening catalogue.

The validator therefore reads **two** of the table's four tiers.
`statutory_floor` and `accessible` stay in the schema, unread; adopting either
later is a configuration change, not a rewrite.

> **The numbers do not exist yet.** `data/standards/room-constraints.json` is a
> 9 KB stub ending in `PLACEHOLDER_NOTE: "DE and US sources, the ergonomic layer,
> and the room table are appended below in the completed file."` It has UK
> sources and the region/tier/flag models; it has **no ergonomic layer, no room
> table, and no DE or US sources**. The room table exists only as prose in the
> findings doc §8, `DE`/`market_default` column only. *Dimensional standards
> corpus* and the map both record the table as shipped. It is not.
>
> Three rules — `dim.min_area`, `dim.min_clear_width`, `dim.min_clear_depth` —
> are therefore `conf: pending`. **Their structure is final; their values are not
> authored.** One further consequence: `win.area_ratio` cites `de_baybo`, which is
> a dangling key until the DE sources land. Ticketed as *Ergonomic minima and the
> constraint table's missing half*.
>
> ✅ **The `de_baybo` half is closed.** *The Azerbaijani region profile* re-sourced
> both consumers to **AzDTN 2.7-2**, read first-hand: `win.area_ratio` to cl. 9.13
> (1:8, a *lower* bound with no cap — value unchanged at 0.125, now agreed by two
> independent regulatory traditions) and `win.kitchen_windowless` to cl. 9.12. That
> second one **inverted its own premise**: the rule was a warn because Bayern
> *permitted* a windowless kitchen, and Azerbaijan *requires* the window. It stays
> a warn only because C14 forbids a region changing the reject set; flipping the
> table's `needs_window` for kitchen is the region-invariant fix and is owed by the
> ticket named above. The three `conf: pending` rules are untouched.

## 4. Circulation — two graphs, not one

C6 item 1 asked for a defined graph. There are two, and they answer different
questions.

**Potential circulation** (`circ.potential_reachability`, solver only) runs over
the **contact graph**: an edge exists where two Rooms share a wall run of at least
*structural opening width + t_int*. It asserts a door *could* be placed. It is
solver-only because it runs before any Opening exists.

**Realised circulation** (`circ.realised_reachability`, validator only) runs over
the **opening graph**: an edge exists where the WallSegment between two Spaces
hosts a passable Opening — `door`, `sliding_door`, `cased_opening`,
`entrance_door`. **A window is never an edge.** It asserts a door *is* there.

Both are hard. Keeping them separate is what lets the system notice a valid solve
that was handed no door — a failure potential circulation cannot see and realised
circulation cannot prevent.

### 4.1 The ensuite defect

C6 item 1 as written — *"every room reachable from the entry without passing
through a bedroom or bathroom"* — **rejects every plan with an ensuite.** The
constraint table sets `is_private: true` on `bedroom_*`, `bathroom`,
`shower_room` and `wc`; an ensuite is reachable only *through* a bedroom; both
ends are private. The solver has the same break, its rule being *private rooms may
receive flow but never forward it*.

Fixed in the **Brief**, not in the predicate: a Room may declare
**`access_via: RoomId`** — an ensuite, a walk-in wardrobe, a utility off the
kitchen. Access-through is **program**, not geometry, so it is declared and never
inferred.

```
every Space is reachable from the entry Space by at least one path
traversing no private Space,
  EXCEPT a dependent Room, which is reached through its declared host
```

The exception makes the rule **stronger**, not weaker: `circ.dependent_room_host`
requires a dependent Room to have exactly one passable Opening, to its host — so
an ensuite that opens onto the hall now **fails**, which it should. Propagates to
*Brief schema and parsing contract*.

## 5. Wet rooms — the one place the two consumers disagreed

*Solver formulation* posts wet clustering as hard flow over the wet subset, which
demands **one** group. That rejects a kitchen at the front and a bathroom at the
back — a real home, not a defect — and with `is_wet` true on `kitchen`,
`kitchen_dining`, `bathroom`, `shower_room`, `wc` and `utility`, an ordinary
two-bed must get four wet rooms mutually touching.

Scoring it purely soft has the opposite failure: a candidate passes with five
isolated stacks.

Resolved as a bound on the **number of plumbing groups**: at most **2**, hard,
postable in CP-SAT, with shared wet-wall length as the soft gradient inside it.
Two is the shape real dwellings take — a front wet zone and a rear one.
`ENGINE_CHOICE`; no surveyed source supplies a number.

## 6. Openings — composing a swing predicate with no fixtures

The corpus hands over components, not a predicate. Composed as follows, all
integer, all evaluable with no furniture model:

| Component | Rule | Source |
|---|---|---|
| Door fits its wall | structural width + 2 × 100 mm jamb return ≤ segment length | `ENGINE_CHOICE` — no source gives a minimum return |
| Swing footprint | the leaf-side **square** of side `leaf_width` anchored at the hinge — the bounding box of the swept quarter-disc | derived; conservative on purpose |
| Swing stays inside | footprint ⊆ receiving Space | derived |
| Swings do not collide | no two footprints overlap | generalises AD M ¶2.22i (1500 mm between lobby doors *and* between swings) |
| Leading edge | 300 mm nib, maintained 1200 mm back | **VERIFIED**, AD M M4(2) ¶2.22; BS 9266 |

`open.fits_segment` does double duty: it is also what catches a window too wide
for its exterior wall.

**One rule is `deferred`, visibly.** AD M ¶1.17d — the entrance-level WC door
opens outwards, overlapping the pan by 250 mm — needs a pan, and fixtures are
still fog. It is carried in the registry with its source and its number so that
adopting it when fixtures land is a data change. A validator that silently omits
a rule it cannot evaluate is indistinguishable from one that never knew about it.

## 7. Windows — topology hard, ratio soft

The four regimes surveyed are **not interconvertible**: England imposes no
daylight requirement at all; Germany measures the *structural opening* against
net floor area at 1/8; Japan's ratio is a function of the distance to the site
boundary and the zoning district, so no `window_area >= k · floor_area` can
express it; the Metric Handbook needs glazing transmittance and surface
reflectances a Plan does not carry.

So the hard rule is the part all four agree on — **topology**:

- `win.habitable_touches_exterior` — every habitable Space shares a segment with
  the EXTERIOR.
- `win.habitable_has_window` — every Space needing a window hosts one on an
  External segment of that Space. Physical fit comes from `open.fits_segment`.

The numeric ratio is **soft and region-parameterised**, defaulting to 1/8 on the
structural opening (BayBO Art. 45(2), read first-hand). Hard would encode one
country's method as universal and be unsatisfiable for `JP` by construction.

`win.kitchen_windowless` is a **warn**. The table sets `needs_window: false` for
`kitchen`, following BayBO Art. 46(1)'s allowance of a windowless kitchen *where
effective ventilation is provided* — and we do not model ventilation. The
permission is honoured; the fact is surfaced.

## 8. The two the seven items missed

**Entry.** One primary by default, more allowed. At least one `entrance_door` on
an External segment; **exactly one** carries `is_primary`, and it is the source
node of the realised circulation graph. A house may have a back door
(`is_primary: false`); a flat gets exactly one, because its Envelope is given and
a second exterior door is a Brief error rather than a layout choice. **Which Room
holds the entrance, and where on its segment the door sits, are Assumptions the
engine defaults and surfaces** — not Brief requirements. The defaulting rule
belongs to *Opening placement rules*.

**Total-area agreement — two rules, because `Envelope` has two modes.**

**The quantity is the sum of Space areas**, not GIA. *Area measurement
convention* / ADR 0010: v1 measures `az_umumi_sahə` per Area Qaydalar cl. 3.8,
which **sums room areas** and therefore does **not** count internal partitions.
GIA counts them. On a 90 m² dwelling that difference is roughly **4–5%** — the
width of the gate below — so this was a change of *quantity*, not of tolerance,
and the earlier "GIA" wording is struck rather than adjusted.

| Envelope | Rule | Why |
|---|---|---|
| **Invented** (house) | Σ Space area within **5%** of `target_area`, hard; 2% soft | the engine chose the footprint, so drift is the engine's fault |
| **Given** (flat) | **warn only**, surfaced against the Brief | area is fixed by the Envelope, so *every* candidate drifts nearly identically. Rejecting would reject 100% of them for a fault none caused — the ticket's own 99%-rejection test, at its limit |

Two consequences of the quantity change, both recorded rather than smoothed:

- **The invented-Envelope gate stops being near-vacuous.** Against GIA an engine
  that sets the Envelope inner area to `target_area` passes by construction.
  Against Σ Space it must also control the partition footprint, which is not
  known until the layout is solved. The 5% is unchanged and remains **unfitted**
  — it was never measured against the old quantity either — and it is now a
  materially harder gate. Re-fit once a real Proposer has run. How an *invented*
  Envelope is sized against this target is fog, under *Variant generation and
  ranking*.
- **The given-Envelope rule's stated reason is now only mostly true.** Σ Space is
  *not* fixed by the Envelope: it falls as the layout adds partitions, so unlike
  GIA it does vary between candidates of one Envelope. It stays a warn, because
  that variation is small against the Brief-versus-Envelope gap that dominates
  it — but the justification is weaker than it reads.

Both sides stamped with `area_convention`, and **presence is not agreement**.
`area.convention_declared` checks a `target_area` carries one at all;
`area.convention_agrees` checks it is *the same one* as the Plan's region
profile. Presence without agreement is the silent failure this whole section
exists to prevent — two numbers compared that are not the same quantity, with
nothing raising a hand. v1 does not convert between conventions, because the
deductions that separate them (balcony coefficients, headroom grading) are
unrepresentable in a model with no balcony and no ceiling height. So a mismatch
is a **hard Brief error**: it rejects the request, not the candidates.

**What `target_area` means to a Homeowner** is settled and belongs on the Brief:
interior `ümumi sahə`, **balcony, loggia, terrace and *eyvan* excluded**. A Baku
listing quotes `ümumi sahə` *including* them at cl. 3.8 coefficients, and an
*eyvan* enters at **1.0 — full area, not reduced**. The engine does not guess a
balcony share back out of the number; it surfaces the reading as an Assumption
(C4).

## 9. Model integrity, and the tolerance question that was deleted

ADR 0001's integer millimetres mean the ticket's tolerance questions — *what
counts as a closed junction, a coincident wall, a zero-area sliver* — are
**integer equalities**. There are no tolerances in this spec. Tolerance exists
only at import boundaries, which this spec does not describe.

Three consequences worth stating because they remove work:

- **"No unusable slivers" is not a separate predicate.** Spaces are
  `erode(rect, t_int/2)` — rectangles. A rectangle meeting min width *and* min
  depth has no sliver. Folded into item 2.
- **The overlap-metric question dissolves.** Bounding-box and true-polygon
  overlap are the same computation on integer rectangles. The sibling project's
  bbox-vs-polygon comparison is discharged **by construction**; no C11
  re-measurement is owed.
- **The corridor pinch allowance is dropped.** AD M ¶2.22b's 750 mm relief over
  ≤2 m describes a *localised* narrowing, and a rectangular Space has no localised
  anything. Carrying it would be a rule that can never fire. Minimum hall and
  corridor clear width is **900 mm**, hard (AD M M4(2) ¶2.22a, VERIFIED).

`model.no_unassigned_area` deserves a note: the solver posts exact tiling **soft**
for a 29× faster search, and this is where that trade is prevented from shipping a
hole. The 24-room `INVALID` row in the solver findings — 141 cells unassigned — is
precisely what it catches.

`model.space_matches_erosion` is the honesty check on a cheap derivation, and it
fails the day internal wall thickness stops being uniform. That is the point of
keeping it.

## 10. The rule nothing in C6 asked for

**Aspect ratio.** A bedroom at 2750 × 8250 meets its minimum area, meets its
minimum width, and is a bowling alley. Nothing in the seven items catches it, and
it is the most likely way a passing Plan still reads as generated.

Habitable and wet Spaces: hard reject above **3.0**, soft prefer at or below
**2.2**. `corridor`, `hall` and `storage` exempt — legitimately high-aspect. Both
`ENGINE_CHOICE`; no surveyed source states an aspect rule.

This is the cheapest rule in the spec that moves output from *passes* to *usable*.

## 11. What the Homeowner sees

**A predicate id is never shown.** Every rule carries a plain-language message
and, where one exists, the Brief field whose edit resolves it. A shown Plan
carries its `warn` and `soft` results; its `hard` results are uninteresting,
because it passed them all.

**When nothing survives, diagnose — never show a failing Plan.** `CONTEXT.md`
states that a Plan failing the bar is not shown, and that invariant is the whole
point of the bar; relaxing the hard set to fill a gallery makes it advisory, and a
Homeowner cannot judge a plan annotated with three defects.

The diagnosis is **arithmetic, not search**: the sum of hard minimum areas for the
Brief's rooms, plus a circulation allowance, is a lower bound on a feasible
**Σ Space area** — which, since ADR 0010, is exactly what `target_area` means, so
the two sides of the comparison need no conversion between them.

> *Three bedrooms, a bathroom and a kitchen need at least 58 m². Your brief says
> 45 m².*

Alongside it, the dominant hard failure across the rejected batch, in Homeowner
language, leading with the Brief field to edit.

## 12. Open, and deliberately so

| What | Where it goes |
|---|---|
| The **ergonomic layer** — the entire hard number set | *Ergonomic minima and the constraint table's missing half* — blocks the numeric half of this spec |
| ~~`de_baybo` is a dangling source key~~ — **closed** by *The Azerbaijani region profile*; both consumers re-sourced to AzDTN 2.7-2 | — |
| The table's `needs_window: false` for kitchen, which AZ contradicts | *Ergonomic minima and the constraint table's missing half* |
| Aspect thresholds, circulation fraction, plumbing group count, jamb return — all `ENGINE_CHOICE` placeholders | *Fit the ENGINE_CHOICE acceptance thresholds to the corpora*, blocked on *Acquire the datasets* |
| `open.wc_door_outward_pan_overlap` | `deferred` until fixtures leave the fog |
| Where the entrance door actually goes | *Opening placement rules* |
| `access_via` and `area_convention` on the Brief | *Brief schema and parsing contract* |
