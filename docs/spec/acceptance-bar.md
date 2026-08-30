# The Acceptance bar — predicate specification

Resolves [Acceptance validator spec](../wayfinder/tickets/07-acceptance-validator-spec.md).

Canonical form: **[`data/acceptance/rules.json`](../../data/acceptance/rules.json)** — 43 rules,
**44 once `dim.leg_join` lands** (§9.1). ✅ It was 42 until *A statutory floor,
posted soft, in the one region v1 ships* added `dim.statutory_min_area` (§3.1) —
the first hard rule in this file that carries a **region**. ✅ It was 40 until
*Fit the `ENGINE_CHOICE` acceptance thresholds to the corpora* added `dim.max_area`
and `dim.stated_target_implausible`; the count in this file was stale at 40
through both moves and is now current. ✅ It was 36 until *A dwelling with no
toilet passes every check* added the four **programme** rules of §13 — the first
rules in this file whose subject is the dwelling's programme rather than one
Space, Wall or Opening. ⚠️ It was 38 before that, until *H8 and the
single-aspect flat* retired `win.habitable_touches_exterior` and
`win.kitchen_windowless`, neither of which could fire; both are kept in that
file's `retired` block rather than deleted (§7.1). ⚠️ That row is specified here and is
**not written**: `rules.json` is claimed by three other tickets and authoring into
it from a fourth is the parallel-write hazard the map warns about. Until its
holder lands it, this document and that file disagree by exactly one rule — which
is the drift the conformance test exists to catch, so it will be caught.
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
by a **conformance test over the `both` subset**, which is 17 of the 43 rules —
18 of 44 once `dim.leg_join` lands, since it is a `both` rule. §13's four
programme rules do not join it and **cannot**: they are brief-scope with no
plan-side twin, so there is no second implementation to agree with. That subset held at
14 across §7.1's retirement: `win.habitable_touches_exterior` left it and
`win.habitable_has_window` joined it, which is the trade §7.2 describes; it then
moved 14 → 15 at `dim.max_area`, and **15 → 17** at §3.1: `dim.statutory_min_area`
is `both` because it is `dim.min_area`'s posting with a larger constant, and
`win.area_ratio` moves `validator` → `both` because §7.4 turns it into a frontage
budget the solver can post — one that **subsumes** `win.habitable_has_window`'s
rather than duplicating it. The
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
the number came from decides it.** `ergonomic_min` is hard, `statutory_floor` is
hard where a profile publishes one (§3.1), `market_default` is
soft. That is the C10 split — model proposes, solver projects — expressed in the
constraint table rather than restated in the validator.

Rejecting on 34 of 43 rules — 35 of 44 with `dim.leg_join` — sounds aggressive;
it is not, because every hard
number is either a physical impossibility (a door that does not fit its wall, two
Spaces overlapping) or the point at which the room cannot contain its function.
The ticket's own test applies: *a rule that rejects 99% of candidates is a bug in
the rule.* Two rules were deliberately loosened to satisfy it — see §5 and §7.

## 3. Where the hard numbers come from — and why their *base* carries no region

> ⚠️ **This section's title used to end "and why they carry no region", and that
> is now false in one direction only.** *A statutory floor, posted soft, in the
> one region v1 ships* amends C14: a Region profile may **raise** a hard floor and
> may never lower one. Everything below still holds of the **base** — read it, then
> read §3.1, which says exactly what changed and what did not.

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
3. ~~**It lets v1 ship without settling the region list.**~~ **Spent** — C12
   settled the list at exactly one profile, `AZ`, with `UK` a never-selectable
   test fixture. This reason was the only one of the three that argued the hard
   set must carry **no** region rather than merely a **defensible** one, and it
   was buying insurance against a case v1 does not have. §3.1.

Reasons 1 and 2 are untouched and are what keep the **base** of the hard set
region-free: the predicates and their region-free floors are the same everywhere,
and no profile may add a predicate, remove one, or weaken one.

The validator therefore reads **three** of the table's four tiers —
`ergonomic`, `market_default` and, since §3.1, `statutory_floor`. Only
`accessible` stays in the schema unread; adopting it later is a configuration
change, not a rewrite.

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
>
> ✅ **Closed, and the warn is gone.** *Opening placement rules* flipped
> `ergonomic.rooms.kitchen.needs_window` to `true` — the region-invariant fix this
> block named — which made `win.kitchen_windowless` unreachable, and *H8 and the
> single-aspect flat* retired it (§7.1). `win.area_ratio` keeps its 0.125 and its
> `soft`, and §7.4 records why that severity is now challenged rather than settled.

### 3.1 A region may raise a floor, and `dim.statutory_min_area` is the first one

**The rule this section is proudest of does nothing.** `dim.min_area` rejects
**0.19 %** of 42,985 real Swiss dwellings and adds **0.00 %** to the hard union —
the only rule in the registry that changes no outcome — while being the sole
predicate between a Homeowner and the **1,85 × 1,68 m = 3,1 m²** double bedroom
this section was written to forbid. `min_clear_short` 1650 is a *fits* floor —
double bed 1350 plus a 300 body zone on one side — and AzDTN 2.7-2 cl. 5.7
publishes the *habitable* one, `verified`, in the only region v1 ships.

**C14 is amended, monotonically: a Region profile may raise a hard floor and may
never lower one.** The hard area floor for a Room becomes
`max(ergonomic minimum, region statutory floor)`. The guarantee the old wording
protected survives exactly, because raising is monotone — an unsurveyed region
still gets the **full** ergonomic bar and cannot lose a rule to a profile. What
the old wording additionally bought is spent (reason 3 above).

Ten of nineteen keys are silent in `AZ`, and silence is not an error: where a
profile publishes no statutory floor, the ergonomic minimum is the whole floor.

**The corpus number is not this rule's rejection rate, and the section says so
before anyone quotes it.** Measured against the cached Swiss census: **54,51 %**
of dwellings hold at least one Space below its AZ statutory floor, **+19,98
points** marginal over the fitted/real-pier union — which would be half the
surviving pool if it were a pool statistic. It is not, for two reasons:

1. **The bar does not gate the retrieval index.** Admission is conversion
   fidelity — `proposer.md` §2.2.1, plus worst-room IoU per *The two-notch cap is
   now evidenced* — not the bar. A donor below the floor stays in the pool, so the
   coverage argument that refused a p95 cap in `room-area-bands.md` §6.1 does
   **not** transfer here.
2. **`market_default` sits at or above `statutory_floor` in every reachable AZ
   cell** — living 16/16, `bedroom_double` 12 > 10, `bedroom_single` 9 > 8,
   kitchen 9 > 8, `kitchen_zone_in_diner` 6/6. A Plan that reaches its soft target
   clears this rule *by construction*. The rule fires only where the solve failed
   to reach it, which is the case it exists for.

**Per limb**, so a later ticket amends a limb and not the rule (marginal over the
fitted/real-pier union):

| limb | AzDTN cl. 5.7 | Swiss p50 | share below | marginal |
|---|---|---|---|---|
| kitchen | 8,0 m² | **8,04 m²** | 49,57 % | **16,88 %** |
| `room*` as `bedroom_double` | 10,0 m² | 14,29 m² | 5,44 % | 5,73 % |
| living / `living_dining` | 15/16 m² | 26,59 m² | 4,33 % | 1,03 % |
| `room*` as `bedroom_single` | 8,0 m² | — | 0,37 % | 0,30 % |
| `kitchen_zone_in_diner` | 6,0 m² | 23,67 m² | 0 % | 0 % |

⚠️ **The kitchen limb lands on the corpus median** and is 16,88 of the 19,98
points. It is taken anyway, on §7.5's own precedent: `win.habitable_has_window`'s
45,19 % was *"handed to the retrieval and conversion side, not paid for by
weakening a statutory rule"*, and this is the same object.

⚠️ **What is unmeasured, and the trigger to revisit.** The rule's true cost is on
engine output and **no Proposer has been run**. ADR 0018's warp fidelity is a
*proportion* result — `fit_warp.py:373-384` normalises absolute area away — so the
warp has never been measured against a stated `target_area`, and that measurement
is owed by `experiments/warp/`. If the first Proposer run shows the warp
systematically undershooting per-room area, this rule collapses yield and
`homeowner_surface.no_survivors` fires.

**That asymmetry is the decision.** A hard rule that is too strict is
**discovered**, at build time, and rolled back by one field. A soft rule that is
too lax **ships**: a 6,6 m² kitchen goes to a Baku Homeowner as a survivor,
unannotated, indistinguishable from a good one, because C6 shows survivors and
nothing marks it defective. The second failure is the one C2's *"would I live
here"* cannot catch.

**Brief-side pre-image**, per ADR 0015. Σ hard minima rises: a one-otaq dwelling
goes from **9,0 m²** (living 3,7 + kitchen 1,8 + `bathroom_combined` 2,5 + hall
1,0) to **26,5**; two-otaq **37,5**, three **47,5**, four **57,5**, before the
partition footprint. Those are ordinary Baku flat sizes and nothing leaves C13's
3–10 band. The 9,0 m² one-otaq flat the old floor admitted **is** the defect,
restated at parse time. `brief.md` §9.4 bounds 1 and 3 must read the raised floor.

**C8 cuts both ways, and this is the direction it cuts here.** C8 forbids
*claiming* code compliance; it does not forbid *being* compliant, and shipping a
3,1 m² bedroom into a market whose law says 10 is the failure C8 exists to prevent
from the other side. No Homeowner-facing message on this rule names a law: it is
`hard`, so a failing Plan is discarded and never shown, and the only text a
Homeowner sees is the Brief-side arithmetic above — *your Envelope cannot hold n
otaq* — which is a statement about addition.

⚠️ **Two shipped files disagreed, and both were wrong.**
`room-constraints.json` bound `statutory_floor_binding: "warn"` (from *Which
region profiles ship in v1*, with a `force`-derived disclosure note);
`rules.json` listed `statutory_floor` under `unread_in_v1`. The tier was
simultaneously bound as a warn and not read at all, and **neither statement had a
rule behind it** — no rule of severity `warn` sourced from a region profile has
ever existed in the registry. That absence is the finding: C14's *"a region
profile never rejects a Plan"* had been implemented as *"a region profile never
**appears** in the hard set"*, which is a stronger claim C14 never made. Both
bindings are superseded.

⚠️ **The one genuine schema change**, and it is owed rather than written:
`hard_reject_below` was a **scalar** tier name and is now the **list**
`["ergonomic", "statutory_floor"]`. `rules.json` carries the list;
`room-constraints.json`'s `tier_model.validator_binding` still carries the scalar
and its `statutory_floor_binding` still reads `warn`. The conformance test that
asserts the two files carry the same string must assert the same **list**. That
file is claimed by *The annotation spec is US-shaped and the drawing is now
Azerbaijani*, so it is handed there rather than written from here — the
parallel-write hazard the map's Notes exist to prevent.

### 3.2 The trigger fired, and the rule does not move

**ADR 0027** records the general form and its scope: *where a hard rule is the thing that
distinguishes this engine from what the market ships, its cost is a debt owed by the stage
that produced the failure — never a reason to weaken the rule.* It is scoped to this rule
and to no other in the registry.

§3.1 named its own revisit condition — *"if the first Proposer run shows the warp
systematically undershooting per-room area, this rule collapses yield"* — and
*The warp has never been measured against a stated target area* fired it inside a
week. **The rule stays hard, at all five limbs.** The premise §3.1 argued from is
**true and its conclusion is false**: `market_default` does sit at or above
`statutory_floor` in every reachable AZ cell, and a Plan that *reaches* its soft
target does clear the rule — but the warp does not reach the target, it reaches a
**proportion** of it.

**The corrected price**, same sample, same seed, after *The sizing rung
under-delivers* removed two defects in the measuring rig's Envelope:

| | as first measured | **corrected** |
|---|---:|---:|
| candidates losing a Room below its floor | 31,1 % | **25,5 %** |
| Briefs with no clearing candidate, pool of 8 | 6,7 % | **3,6 %** |
| kitchens delivered under 8,0 m² when asked for 9,0 | 21,8 % | **17,4 %** |
| lower quartile margin of the kitchens that pass | +0,085 m² | **+0,518 m²** |

⚠️ **3,6 % is an upper bound, not a shipped figure.** It is measured at
**pool-of-8**, and `proposer.md` §2.2.7 is explicit that the fidelity sample is
the 2,317 converted dwellings of the ADR 0016 sample — *"a pool of 87 in
production is a pool of 8 here"* — against a production median pool of **86.6**
at 4–6 rooms and **58.7** at 7–10. ⚠️ And do not reconstruct it by compounding
the per-candidate 25,5 %: declines are **correlated within a pool**, because every
candidate for one Brief is sized from one Envelope. *What best-of-pool is worth at
production depth* measures the curve.

**Four reasons, in the order they bind.**

1. **The asymmetry was never conditional on the price.** §3.1 posted this rule on
   *discovered versus shipped*, and discovery is what just happened. Weakening the
   rule now spends the argument on the single event that vindicates it.
2. **The price halved and it is an upper bound.** 3,6 %, not 6,7 %, against ADR
   0018's 6,9 % for every dimensional decline combined.
3. **The 17,4 % is the warp's, not the rule's.** No sizing constant reaches it —
   `f = 0.0575` is vindicated and the level lands at **+0,4 %** — so what survives
   is the warp's per-room *distribution*, which a perfect level leaves intact.
   §7.5's precedent is this same object from the same side:
   `win.habitable_has_window`'s 45,19 % was *"handed to the retrieval and
   conversion side, not paid for by weakening a statutory rule."* A predicate is
   the wrong instrument against a proposer defect.
4. **The market settles it.** `competitive-landscape.md` §5.2: *code compliance is
   claimed by six vendors and implemented by approximately zero* — user-authored
   graph rules, LLM Q&A over a PDF that never touches the geometry, or a ToS
   disclaimer. A curated, first-hand, geometrically-enforced statutory floor is the
   one thing this engine has that the surveyed market does not. Trading it for
   3,6 % of yield sells the differentiator to cover a debt the proposer owes.

**All five limbs stay, and the kitchen is the one that had to be argued.** It is
**16,88 of the 19,98** marginal corpus points and the limb the warp fails, so it
is the only one worth dropping — and dropping it does not lower the kitchen floor,
it **removes** it. The ergonomic `kitchen.min_area` is **1,8 m²** (900 × 2100 mm,
a galley strip) against a statutory 8,0: a 3 m² kitchen would pass. The Swiss p50
of **8,04** against a floor of 8,0 is not evidence the floor is too high. It is
evidence the floor sits exactly where people build, which is what a *habitable*
minimum is for.

**What moved instead.** The rule now states **only its own half**. The composed
number is a named term — **[[Hard area floor]]** in `CONTEXT.md`,
`max(ergonomic minimum, statutory floor)`, per Room and never per part — because
every consumer wants the composition and every amendment touches one half.
Composing the `max` inside the rule statement made a limb amendment read as a rule
amendment; it is a **value** edit. §11 and `brief.md` §9.4 read the term.

**And the Brief gains a bound that is not a pre-image.** `brief.md` §9.4 **bound
9**: a *stated* per-room target below its own hard area floor, at **`warn`**.
⚠️ **ADR 0015 does not decide that severity, and this is the first bound where it
cannot.** The implication fails in the direction ADR 0015 cares about:
`model.no_unassigned_area` fixes Σ Space at the interior exactly and §9.3 targets
are two-sided bands, so a kitchen stated at 6 m² **can** be delivered at 8 with
another Room absorbing the loss. Per ADR 0015 consequence 5 a `hard` bound there
is a heuristic refusing buildable Briefs; per consequence 2, a bound needing a
fitted slack threshold of its own is the tell that it is not a pre-image. §9.5
forbids the tidy fix as well — raising a stated 6 to an 8 in the defaulting ladder
is auto-repair, and that ladder fills only **absent** fields.

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

## 7. Windows — two hard rules, and one of them is the frontage budget

The four regimes surveyed are **not interconvertible**: England imposes no
daylight requirement at all; Germany measures the *structural opening* against
net floor area at 1/8; Japan's ratio is a function of the distance to the site
boundary and the zoning district, so no `window_area >= k · floor_area` can
express it; the Metric Handbook needs glazing transmittance and surface
reflectances a Plan does not carry.

So the hard rule is the part all four agree on — **topology**. There used to be
two of them, and **there is now one**:

- `win.habitable_has_window` — every Space needing a window hosts one on a
  WallSegment of that Space whose Envelope edge **condition is `exterior`**.
  Hard, site **`both`**.

### 7.1 Two rules retired, and why a rule that cannot fire is not free

`win.habitable_touches_exterior` keyed on `is_habitable`; `win.habitable_has_window`
keys on `needs_window`. **No row of the 18-type table has the first without the
second**, and hosting a window on an exterior segment implies sharing one, so the
first was strictly implied by the second and could never fire alone. Measured
against 561 real Swiss dwellings it rejects **11.9 %** where `has_window` rejects
**43.3 %**, and its rejections are a subset.

`win.kitchen_windowless` went the same way for the reason *Opening placement
rules* §6.2 recorded and handed here: once `ergonomic.rooms.kitchen.needs_window`
became `true`, the hard rule carries the kitchen and the warn is unreachable. It
was left standing only because retiring it moves the rule count and this file was
claimed elsewhere at the time. This ticket holds the file, so the count moves.

Both are recorded in `rules.json`'s `retired` block with their statements, not
deleted silently. **The bar was 36 predicates at that point; §13 takes it to 40 —
41 once `dim.leg_join` lands.**

The invariant `touches_exterior` looked like it protected — *a habitable type
always needs a window* — was never carried by it. It is a property of the **table**,
not of a Plan, and `experiments/region-profile/ergonomic_check.py` asserts it
directly. That is the right site: a rule can only be exercised by a Plan that
violates it, and no Plan can violate this one.

### 7.2 What the solver posts

`win.habitable_has_window` inherits the retired rule's `both` site, and inherits
it **stronger**. The old solver posting was mere contact with the exterior. What
the solver posts now is the frontage budget itself: each `needs_window` Room holds
a run of `exterior`-condition Envelope edge of at least its catalogue window's
structural width plus **twice the 100 mm jamb return** — `window_bedroom` 1200 mm
becomes 1400 mm of frontage, `window_living` 1500 becomes 1700, `window_kitchen`
900 becomes 1100.

This is not new machinery. ADR 0003 types the edge ring **before** the solve, and
`open.fits_segment` already carries the jamb constant. Posting anything weaker
throws away yield on a constraint the solver can already express: candidates that
cannot seat their windows would be generated, solved and then rejected by the
validator, which is exactly the waste C6's *generate many, reject most* is
supposed to be paying for something in return.

### 7.3 Which part it binds

Per §9.1 every dimensional predicate must say which part of a two-part Room it
binds, and this one has a **split** answer:

- **Per Room** for the requirement itself — a Room reaches its window through
  *any* of its parts.
- **Per part** for the part that carries the window: it must meet that Room's own
  `min_clear_short`.

That is option 2 of the three *Whether a Room may be more than one rectangle*
handed here, and it costs nothing today, at one rectangle per Room. It is taken
now because the alcove it prevents is cheap to prevent and expensive to discover:
a habitable Room whose only daylight comes down a 900 mm leg is an alcove with a
window, not a room with an aspect. `open.fits_segment` already forces such a leg
to 1400 mm for a bedroom window; requiring the Room's own published minimum is
the number an architect would hold, and it needs no new constant.

### 7.4 The ratio is hard, scoped to living rooms and kitchens, and the window is sized rather than picked

> ⚠️ **This subsection's title used to read "the ratio is soft … and the severity
> is challenged".** *A statutory floor, posted soft, in the one region v1 ships*
> settled it. Three changes, and the third is what makes the first safe.
>
> **1. Scope, and it is a precondition rather than a tidy-up.** The shipped
> statement bound **every Space**. cl. 9.13 binds **living rooms and kitchens
> only**, and `room-constraints.json` says so verbatim — *"a LOWER bound, applying
> to living rooms and kitchens"*. Soft, the over-reach cost a wrong objective term
> on bedrooms and wet rooms; **hard, it would have rejected a windowless WC for
> its glazing ratio.** `binds_room_types` is the corrected set, and every cost
> below is measured on it.
>
> **2. The measurement that changed the answer.** Against the shipped three-entry
> catalogue — `window_living` 1500 × 1500 = 2,25 m², `window_kitchen` 900 × 1200 =
> 1,08 m² — the rule demands **2+ windows on 72,7 % of living rooms, 93,6 % of
> `living_dining` and 40,7 % of kitchens**, and the required exterior run p50 is
> **3,80 m against an available window-run p50 of 3,84 m**: a rule sitting exactly
> on the feasibility cliff. **33,68 %** of real dwellings could not fit it at
> `min_pier` 600, **21,20 %** at 250. Size the *opening* to the room instead and
> the same test costs **5,39 %** (living 6,95 %, `living_dining` 7,73 %, kitchen
> 1,98 %). **Three quarters of the cost was a catalogue artefact, not a layout
> fact** — rejecting on it would have been rejecting a room an architect keeps for
> a window they would widen.
>
> **3. The window is selected, not mapped.** `window_for_room` stops being a fixed
> `key → key` map and becomes the **smallest member of the profile's width series
> for that room family which satisfies cl. 9.13**, at the family's catalogue
> height, even per ADR 0004, and fitting the run the Space has. A **series**, not
> a free derivation: the catalogue's own comment is *"a facade with two different
> windows in one room is a tell"*, and free per-room widths would put six widths on
> one elevation — the generated look `dim.aspect_ratio_hard` exists to avoid.
> Splitting into two openings buys **nothing**: total glazing width is fixed and
> the pier is pure loss, so this rule never asks for a second window.
>
> **`min_pier_mm` is therefore not load-bearing here.** At one opening per room
> there is no pier between windows, so this decision does **not** rest on the
> 600 → 250 move handed to *The annotation spec is US-shaped*. The 33,68/21,20
> pair is kept only to show what the catalogue reading would have cost.
>
> ⚠️ **What is owed, and it is blocking.** The **width series values** are
> `room-constraints.json`'s, and that file is claimed by *The annotation spec is
> US-shaped and the drawing is now Azerbaijani* — same holder that already carries
> `min_pier_mm` in the same `openings` block. Measured reach requirement, written
> out so it is transcribed and not re-derived: **the series must reach p90 2,47 m
> living, 3,23 m `living_dining`, 1,34 m kitchen.** A top member below those turns
> the residual cost back up. `catalogue_may_be_dead` is the cover —
> `gost_23166_99` cl. 4.9 makes the opening grid a **project decision**, so a
> published series is `engine_choice` bounded by `gost_11214_86`, which is *more*
> defensible than three fixed entries rather than less. The derived Type mark
> rides with it — the GOST mark reads **height-then-width** — and is
> `annotation.md`'s, same holder. Writing the rule `hard` now is writing the
> **decision**: C1 means no validator exists to be inconsistent with, and the
> series is owed before any build.
>
> ⚠️ **The residual 5,39 % is real and it is frontage** — the same object as
> `win.habitable_has_window`'s cost, and it goes the same way as §7.5 sent that
> one: to the retrieval and conversion side, not paid for by weakening a statutory
> rule.

`win.area_ratio` **was** soft and region-parameterised, defaulting to AzDTN
2.7-2 cl. 9.13's 1:8 on the structural opening. Its statement gains one clause it
should always have had: the windows counted are those on **`exterior`-condition**
segments. Computed over every boundary face, a mid-block flat satisfied its
glazing ratio on a wall shared with a neighbour. A party edge hosts no window
(`openings.md` §6.1).

~~⚠️ **Held soft, and flagged rather than settled.**~~ **Resolved, and the box
above is the resolution.** cl. 9.13 is `verified` and mandatory, which made this
the only statutory minimum on the map posted soft. C14 named it — *"one soft
window fraction"* — so amending it meant amending a standing constraint, which is
what §3.1 does: a profile may raise a hard floor and may never lower one. The same
ticket took AzDTN's statutory **area** floors (living 16 m², `bedroom_double` 10,
kitchen 8) hard against an ergonomic floor of 3,1 m² for that bedroom. **The two
halves were decided together and by the same argument, and only one of them
needed a second decision to be safe** — the area floors are satisfiable by making
a room bigger, which the Envelope permits, while the glazing floor is satisfiable
only by frontage the Envelope may not have, which is why the window had to stop
being picked from three fixed entries first.

### 7.5 What H8 turned out to be

The frontage crisis this section was expected to resolve — *"the single-aspect flat
is arithmetically dead from 7 rooms"* — **does not exist**, and both halves of the
number that produced it were wrong.

The minima were placeholders. `experiments/solver-toy/scenarios.py` says so in its
own comment; its bedroom was 2000 mm where the shipped ergonomic layer is 1650
(realisable 1850), its living room 2750 against 1850. Re-run against the shipped
layer, the first arithmetically dead cell moves from **7 rooms to 16** — outside
C13's 3–10 engine band entirely.

And the exposure was measured on one room. `exposure_swiss_dwellings.py` unioned a
dwelling's disjoint room polygons, got a `MultiPolygon`, and took the largest part
— so every published exposure figure described the largest **room** in the
dwelling. Corrected: median exterior fraction **0.67**, not 0.37; p25 **0.51**, not
0.23. `flat_single_aspect` was fitted to that p25 and is roughly half the real
thing.

So H8 is **not relaxed by type, not relaxed by count, and the room-count promise is
not bounded on its account.** All three of those options existed to buy back
frontage that was never missing.

⚠️ **What the measurement did find is a different rule.** `win.habitable_has_window`
as posted rejects **43.3 % of real Swiss dwellings**, and the kitchen is most of it:
**31.0 % of real kitchens carry no window**, against 5.9 % of bedrooms. Those
kitchens are not niches — median 6.8 m² — and **84.7 % of them sit adjacent to a
windowed habitable room**, the borrowed-daylight arrangement AzDTN names
`taxca-metbex` and `profiles.AZ.windows.kitchen_niche_windowless` holds `false`.
The rule is right for Baku and cl. 9.12 is not negotiable; what it costs is
**corpus coverage**, in the population the engine retrieves and trains on.

Split by cause, over 561 dwellings: **23.0 % fail on the kitchen alone** and
**20.3 % on a non-kitchen room**. So more than half the rejection is one clause,
and it is the clause that is least negotiable. *What a room's area is allowed to
be* set its cap at p99.5 rather than p95 on exactly this argument — *"the corpus is
the retrieval and training population, so a rejection there is coverage lost"* — at
26.6 %. This is 43.3 %, and it cannot be bought back by moving a threshold,
because the rule carries no threshold to move.

That is handed to the retrieval and conversion side, not paid for by weakening a
statutory rule.

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
GIA counts them. That difference is **5.7%** of Σ Space area at the shipped
`t_int` of 150 mm — **wider than the 5% gate below**, measured over 14,063
dwellings by *One internal thickness, against a corpus that has no module at all*.
So this was a change of *quantity*, not of tolerance, and the earlier "GIA"
wording is struck rather than adjusted.

> The figure first written here was "roughly 4–5%". That is verified for the
> corpus's own partitions (4.8%) and for the `t_int` of 120 mm that ADR 0010
> replaced (4.5%) — and stale for the 150 mm it shipped. Corrected, and it widens
> the gap rather than narrowing it.

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

- **"No unusable slivers" is not a separate predicate.** A rectangle meeting min
  width *and* min depth has no sliver. Folded into item 2. ⚠️ **The reasoning
  this used to rest on is dead** — see §9.1 — but the conclusion survives on a
  different argument, and no predicate is added.
- **The overlap-metric question dissolves.** Bounding-box and true-polygon
  overlap are the same computation on integer rectangles. The sibling project's
  bbox-vs-polygon comparison is discharged **by construction**; no C11
  re-measurement is owed.
- **The corridor pinch allowance is dropped.** AD M ¶2.22b's 750 mm relief over
  ≤2 m describes a *localised* narrowing, and a rectangular Space has no localised
  anything. Carrying it would be a rule that can never fire. Minimum hall and
  corridor clear width is **900 mm**, hard (AD M M4(2) ¶2.22a, VERIFIED).
  ⚠️ **"A rectangular Space has no localised anything" stopped being true**: a
  two-rectangle Room has exactly one localised place, where its legs meet. The
  question returns as `dim.leg_join` in §9.1 — with the opposite sign, a floor
  rather than a relief.

`model.no_unassigned_area` deserves a note: the solver posts exact tiling **soft**
for a 29× faster search, and this is where that trade is prevented from shipping a
hole. The 24-room `INVALID` row in the solver findings — 141 cells unassigned — is
precisely what it catches.

`model.space_matches_erosion` is the honesty check on a cheap derivation, and it
fails the day internal wall thickness stops being uniform. That is the point of
keeping it.

### 9.1 A Room is one or two rectangles

ADR [0014](../adr/0014-a-room-is-one-or-two-rectangles-and-the-proposal-decides.md).
A Room is the union of at most two axis-aligned **parts**; the Proposal decides
which Rooms have two. Every dimensional predicate on this page has to say which
of the two it binds, and the answer is not the same for all of them.

| Predicate family | Binds |
|---|---|
| minimum clear width and depth (§3) | **per part** |
| aspect ratio (§10) | **per part** |
| area, and every area rule (§8) | **per Room**, over the union |
| circulation, wet cluster, entry, windows | **per Room** — a Room reaches a window, or the entrance, through *any* of its parts |
| forbidden adjacency (H7) | **per part pair** — no leg of *i* may touch any leg of *j* |

Per-part clear dimensions are also what an architect means: **each leg of an L
must be usable.** A Room whose 4.0 m leg passes while its 0.6 m return does not
is not a room with a usable return.

**The leg floor.** The *first* part carries the Room's own ergonomic minimum.
Any further part carries **900 mm clear on both axes** — the hall and corridor
minimum already in §9, AD M M4(2) ¶2.22a, VERIFIED. Below 900 mm it is not a leg
of a room, it is a niche, and this system does not model niches. **The number is
not new**, so it inherits §9's provenance and ADR 0009's treatment rather than
creating a second question: a leg you cannot walk down is not a leg.

Its **realisable** value is 1 100 mm (`CONTEXT.md`, *Realisable minimum*). Clear
= 250w − `t_int`, so at the shipped grid and `t_int` 150 a 900 mm floor needs
w = 5 and lands at 1 100 — and so would a 1 000 mm floor. The published number
and the bound it actually posts are two different figures here, as ADR 0009 says
they will be everywhere in this layer.

**One new hard predicate, `dim.leg_join`:** the two parts of a Room share an edge
of at least **900 mm** clear. Anything narrower is a pinch — two rooms with no
door between them wearing one name. Enforcement site `both`: the solver posts it
as a reified contact, the validator measures the shared edge.

⚠️ **This kills §9's sliver argument, and the fix is not the obvious one.** That
argument reads *"Spaces are `erode(rect, t_int/2)` — rectangles"*, and for a
two-part Room the Space is `erode(A ∪ B, t_int/2)`, which is **strictly larger**
than `erode(A, t_int/2) ∪ erode(B, t_int/2)`: the band across the shared edge is
interior to the union and survives erosion. So the Space is a rectilinear polygon
with one reflex corner, not a rectangle, and "a rectangle has no sliver" no longer
reaches it.

What rescues the conclusion is that binding the minima **per solved part** is
*conservative*: it under-states the true clear leg by exactly that band, so a
part that passes cannot hide a sliver the union would have had. No predicate is
added; the reasoning is replaced.

**`model.space_matches_erosion` is restated, not weakened.** A Space is
`erode(⋃ parts, t_int/2)` — still exact integer arithmetic, still a rectilinear
polygon, still failing the day `t_int` stops being uniform. ADR 0001's erosion
is untouched: eroding a rectilinear polygon by a `t_int/2` square gives exactly
the region bounded by the surrounding wall inner faces, reflex corner included.

**A soft rule is owed, and it is not authored here.** Under ADR 0014 the solver
cannot invent an L, so it cannot bloat one into existence — but a *Proposer* can
over-produce them, and nothing in the hard set would notice. A soft
`dim.prefer_single_part` — all else equal, prefer the simpler Room — belongs with
`rules.json`'s holder. This is the same shape of defect *What a room's area is
allowed to be* found in `dim.market_default_area`: an objective that rewards
something nobody asked for.

## 10. The rule nothing in C6 asked for

**Aspect ratio.** A bedroom at 2750 × 8250 meets its minimum area, meets its
minimum width, and is a bowling alley. Nothing in the seven items catches it, and
it is the most likely way a passing Plan still reads as generated.

Habitable and wet Spaces: hard reject above **3.0**, soft prefer at or below
**2.2**. `corridor`, `hall` and `storage` exempt — legitimately high-aspect. Both
`ENGINE_CHOICE`; no surveyed source states an aspect rule.

**Measured per part** (§9.1), with the same exemptions. A bowling-alley *leg* is
a bowling alley, and a Room's bounding box would exempt exactly the shape this
rule exists to catch: an L whose return is 900 × 4 500 has a near-square bbox.

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

The diagnosis is **arithmetic, not search**: the sum of the
[[Hard area floor]] over the Brief's rooms is a lower bound on a feasible
**Σ Space area** — which, since ADR 0010, is exactly what `target_area` means, so
the two sides need no conversion between them. Every bound runs after `resolve`,
so the invented `hall` is inside the sum and there is no separate circulation
allowance term.

⚠️ **The sentence quotes computed numbers and this spec does not hard-code one.**
The example this section shipped — *"three bedrooms, a bathroom and a kitchen need
at least 58 m²"* — was reproducible from nothing: realisable ergonomic minima give
about 18 m² and `AZ` `market_default` about 48. Since §3.1 the hard side is
dominated by the statutory half, and the series that **is** published is per otaq,
before the partition footprint: **26,5 / 37,5 / 47,5 / 57,5 m²** for one to four
otaq. Quote the **pair** — the market number as the recommendation, the hard area
floor as the line:

> *Dörd otaqlı mənzil ən azı 57,5 m² tələb edir. Sizin brifinizdə 45 m² yazılıb.*
> — a four-otaq dwelling needs at least 57,5 m²; your brief says 45.

Alongside it, the dominant hard failure across the rejected batch, in Homeowner
language, leading with the Brief field to edit.

### 11.1 The starved Brief that has no defect to name

**A Brief can pass every bound and still be starved.** Ticket 55: every stated
target at or above `market_default`, §9.4 silent, and **3,6 %** of such Briefs
(pool-of-8, an upper bound — §3.2) have no candidate that clears
`dim.statutory_min_area`, because the warp delivers a proportion of a target
rather than the target.

⚠️ **This section's same-sentence guarantee does not reach that case.** The
guarantee is that the parse-time check and the zero-survivor diagnosis produce the
same sentence. Here **there is no parse-time sentence**, because there is nothing
wrong with the Brief. Naming it is the point: a guarantee with a silent hole is
worse than a stated exception.

**Starvation is declared on the Plan, never on the Proposal.** *Can a starved
candidate be refused before the solve* put warped Proposals through `project()`
for the first time and the ordering turned out to be load-bearing. The solver
**posts** this rule — it is `site: both` — so it sizes the Rooms *subject to* the
floors and will shrink a Room above its floor to feed one below it. Σ Space is
unmoved doing so (p50 **0,0000**), which is §3.2's own reasoning for bound 9's
severity, measured: the solve does not create floor, it moves it.

So a candidate that looks starved on its warped rectangles usually is not
starved: **41 of 50 are served by the projection**, 82,0 % [71,4–92,6]. Declaring
starvation on the Proposal throws those away. The figure quoted above is
therefore an **upper bound on a quantity measured at the wrong site**: read at the
Plan on the same Briefs it is about half — 3,28 % → **1,64 %** — and that
re-reading is worth more than every step below.

⚠️ **That halving is measured on 61 Briefs and 2 starved cases, and it is a
direction rather than a number.** The Plan-level twin of §3.2's best-of-*m* curve
does not exist; `proposer.md` §2.2.9 owes it.

**And no pre-solve screen may be added to buy the difference back.** The
projection on a warped candidate costs **less than the warp that produced it** —
wall p50 **0,145 s** against the warp's 0,674 — so a gate sitting between them
skips the cheaper of the two steps. There is nothing to save.

**Three steps, in order, and the hard set is not one of them.**

1. **Deepen the pool before declaring starvation.** No failing Plan is shown and
   no predicate moves — this is spending more search, which this section has never
   forbidden. ⚠️ **It is not the answer, and both halves of that are now
   measured.** *What best-of-pool is worth at production pool depth*: an
   eightfold deepening buys **one point** (4,1 % → 3,1 %), the curve is flat by
   m ≈ 12, at 7–10 rooms it buys **nothing at all**, and under it sits a floor of
   **π = 2,8 %** [0,3–5,6] no depth reaches. So this is a **config value** and not
   a re-shape of the proposer service: `POOL_DEPTH_ON_STARVATION = 16`, past
   57's knee with margin.
   **It is, however, comfortably affordable, and the arithmetic that said
   otherwise was off by an order of magnitude.** One extra pool member costs a
   **mean 2,17 s** — warp 1,12 plus projection 1,05 — so eight more members on a
   starving Brief is ~17 s, spent on the ~3 % of Briefs that reach this step. The
   10,11 s figure that made this look unaffordable is 58's **real-boundary** arm,
   which no candidate ever presents.
2. **Fall through to source B**, per ADR 0005, which is already the declared
   behaviour where retrieval cannot answer. ⚠️ **Source B's per-room absolute area
   fidelity is unmeasured** — `proposer.md` §6.1's evaluation has four
   plan-quality terms and delivered-versus-stated area is not among them. This is
   where the Brief **goes**; it is not a step this spec may claim will succeed.
3. **Only then, the no-survivor sentence — and it is a new kind.** Every other one
   names a Brief defect and the field that edits it. This one names none, because
   there is none. It reports the *engine's* limit and offers the two edits that
   widen the search — raise `target_area`, or drop a Room — and it must not imply
   the Homeowner asked for something wrong.

**Not available:** relaxing the hard set to fill a gallery, and any sentence on
this rule that names a law (C8). The rule is `hard`, so a failing Plan is
discarded and never shown; everything the Homeowner reads here is arithmetic about
areas. **Nor a Proposal-level *screen*.** A filter sitting between the warp and the solve
was weighed and refused — 82 % of what it refuses the solve serves, its only
*sound* form is arithmetic that never fires (Σ hard floors against the candidate's
own derived box: p50 0,566, **max 0,736**), and it would skip the cheaper of the
two steps. ⚠️ **That is a refusal of a filter, not of a third site.**

**And the third site is now taken.** *Should the warp post the statutory floor*
decided it: the warp posts `dim.statutory_min_area` **hard, per Room, on this
bar's plane, in a single pass** — ADR 0033. That is ADR 0027's *"the stage that
misses it owns the miss"* being paid by the stage the ADR named, and none of the
screen's three grounds transfers to it, because a constraint does not refuse, it
re-sizes.

**What it changes for this section is the base rate, not the escalation.**
Starvation is still declared on the Plan; the screen is still refused; the three
steps still run in order. What moves is the population they run on. The warp as
`proposer.md` §2.2.2 specified it emits **31,6 %** of candidates carrying a Room
below the law — median miss **1,356 m²**, tail to **8,444** — and posted, that is
**4,6 %**, the residual being grid dust from a seed-shape estimate (p50 0,038 m²).
At Brief level, m = 8 over 199 Briefs: service 96,48 % → 94,97 %, *legal* service
**90,95 % → 94,97 %**, and the share of served Briefs holding a floor-clean
candidate **94,27 % → 100 %**. So **18,3 % Proposal-level starvation is no longer
the number to quote at step 1** — it was measured on the unposted warp.

⚠️ **A two-pass warp was measured and refused, and the reason generalises.**
Re-warping without the floor on INFEASIBLE recovers every lost candidate and
takes violations to 14,0 % with nothing lost, which reads as strictly dominant.
It is not: every second-pass candidate violates *by construction*, since it is
exactly the one the floor refused. It buys a rate and buys **no invariant**, so
this section would still have to reason about starved Proposals and nothing here
would simplify. A guarantee that holds except when it doesn't is not one.

✅ **The solver reads this bar's plane, and the defect was arithmetic rather than
geometry.** `solver.py` bound H4 on `(250w − t_int)(250h − t_int)`, eroding all
four sides of every Room; ADR 0001 does not erode at the Envelope, because the
tiling edge there already sits at exterior-inner-face + `t_int/2`. That made the
projection **strictly stricter** than the rule it posts, by a median **3,9 %** of
a perimeter Room's area — measured over 1 786 warped Rooms, **1,51 %** clear their
floor on this bar's plane and fail on the solver's. It is closed by **ADR 0039**:
the solver subtracts the erosion band per *side*, over the sides that face another
Room, and claims nothing at the boundary.

```
amm_i = 62 500·a_i − 75·Σ_{s ∈ 4 sides} interior_len_mm(i, s)
```

`a_i = w_i·h_i` is the multiplication H4 already builds, and the boundary contact
comes off `Envelope.all_faces()`, the decomposition H8 already consumes. The form
is **affine in `a_i` and linear in the segment lengths**, so it costs no second
`AddMultiplicationEquality` — the same identity `mm_affine` used to make ADR
0001's clear reading free.

**There was never a dilated domain to reach for, and the ADR says so plainly**
because it is the first thing a reader will try. `brief.md` §5.3 describes the
solve frame as `dilate(Envelope, t_int/2)`; `absolute_area.space_m2` implements
that by eroding `parts ∪ outside`, under which a boundary edge is *interior to
the union and survives*. The domain boundary already **is** the exterior inner
face. Dilating it would be a second geometry, not a correction.

⚠️ **The seam was never one predicate's, and it runs in both directions.** Seven
rules are `site: both` and read a clear dimension. Five are floors, where the
solver's plane refuses what this bar admits. `dim.aspect_ratio_hard` reads a
ratio of two clear dimensions and moves either way. And **`dim.max_area` is a
cap, where the solver's plane is the *lenient* one** — it reads a perimeter Room
~3,9 % smaller, so the cap does not bind exactly where `model.no_unassigned_area`
sends surplus. No Plan reaches a Homeowner that way, because this bar re-checks on
its own plane and discards it; what is lost is yield and the propagation the
rule's own note claims the solver post buys. ADR 0039 requires the contact
literals to be **biconditional** for that reason: H8's are forward-only, which is
correct for a floor — a Room must prove contact to claim the correction — and
wrong for a cap, which would leave every literal false and stay loose.

⚠️ **19,5 % is not this section's number and must not be quoted as one.** ADR 0033
consequence 4 read it off `project_join.planes()`, which compares two planes on
warped rectangles and runs **no solver**. This rule is `site: both`: the
projection *posts* the floor, so a Room short on the solver's plane is re-sized,
not refused, and a refusal can only appear as INFEASIBLE. That is measured — 273
candidates reaching the solve, **14 INFEASIBLE**, all fourteen attributed to the
statutory limb by ablation (drop it, keep the ergonomic floor: 10 OPTIMAL, 4
FEASIBLE). **5,1 %**, and it is an upper bound containing genuine starvation as
well as plane victims. It is the same error this section already caught itself
making at 3,6 % — a quantity measured at the wrong site — one stage further on.
The two are **not** comparable with the 1,51 % above either, which is per-Room
over all warped Rooms.

⚠️ **A corner residual of at most 0,0225 m² per Room survives, deliberately.**
Subtracting a band per side double-subtracts the 75 × 75 square where two
interior sides meet, and adding it back exactly needs contact at a *point* rather
than over a length. Dropped: it is conservative on every floor, it is bounded at
`4 × 5625 mm²`, and it is smaller than the **0,038 m²** grid dust *The posted
floor is a seed-shape estimate* is already deciding what to do with on the warp
side. That ticket owns both.

⚠️ **The rule this section escalates on no longer has one kind of limb.** ADR 0034
reclassifies `dim.statutory_min_area`'s `KITCHEN_DINING` limb: four limbs
transcribe a whole-room figure, and this one is a **sound lower bound entailed
from a part** — AzDTN cl. 5.7 floors the kitchen *zone* inside the room and
publishes no whole-room figure at all (`az-kitchen-diner-whole-room.md`). The
value, the severity, the site and the enforcement order are all unmoved. What
moves is what a clearing Plan *guarantees*: on that one limb the room clears the
part's floor, not the room's, and the room's is unpublished. It is orthogonal to
the plane — `KITCHEN_DINING` is 41 Rooms of 319 222 and `STAT_FLOOR` does not
move — so no figure above changes.

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
| §13's four messages, in Azerbaijani — the **locale dimension**, now over 43 rules rather than 36 | whoever next holds `rules.json` |
| A **three-way** `corpus_label_split`, now `bathroom_combined` exists — the fixture ground truth is already in the corpus | whoever next holds `experiments/rectangularise/` |
| Whether a **nineteenth-and-twentieth** type is owed: `taxça-mətbəx`, and a Brief-nameable built-in wardrobe (§13.6) | whoever next holds `brief.md` §3 |
| ~~§11's worked example is not reproducible~~ — **closed by §11**, which quotes §3.1's published per-otaq series instead of a number nobody could derive | — |
| **What best-of-pool is worth at production depth** — 3,6 % is measured at pool-of-8 and the fidelity sample cannot hold a pool of 87. §3.2 | *What best-of-pool is worth at production pool depth* |
| **Source B's per-room absolute area fidelity** — §11.1 step 2 routes the starved Brief there and `proposer.md` §6.1 has no term that measures it | whoever next holds `proposer.md` §6 |
| ~~The **`escalation` block's step 1** — how much deeper the pool goes, and who pays the solve time~~ — **closed** by *Can a starved candidate be refused before the solve*: `POOL_DEPTH_ON_STARVATION = 16`, a mean **2,17 s** per extra member, on the ~3 % of Briefs that reach the step | — |
| **The Plan-level twin of §3.2's best-of-*m* curve.** §11.1's 1,64 % is 61 Briefs and 2 starved cases; the curve itself was measured at the Proposal | `proposer.md` §2.2.9 |
---

## 13. What a dwelling owes — the four programme rules

Every rule above this section is per-Space, per-Wall, per-Opening or
per-Plan-geometry. Each is of the form *if a Room of type T exists, it is at
least this big.* **Not one of them asks whether T exists at all**, so a Brief
naming a living room, a bedroom, a kitchen and a bathroom resolved, solved,
passed all 36 predicates and exported a valid IFC of a flat **with no toilet**.

The source is first-hand and mandatory. AzDTN 2.7-2 **cl. 5.2**, in
`experiments/finish-layer/out/azdtn_2_7_2.txt`:

> «Mənzillərdə yaşayış otaqları və yardımçı sahələr: mətbəx (və ya taxça-mətbəx),
> holl, vanna otağı (və ya duş) və tualet (və ya birləşdirilmiş sanitar qovşağı),
> yığnaq otağı (və ya divar təsərrüfat şkafı) nəzərdə tutulmalıdır.»

Register `nəzərdə tutulmalıdır` = **məcburi**, mandatory, per
`room-constraints.json`'s own `source_force_vocabulary`. `CONTEXT.md` already
carries the class this clause defines — [[Auxiliary space]] — and already says
the norm *"requires the rooms to exist, not merely to be big enough if present."*
Nothing enforced it.

### 13.1 Five limbs, four rules, one invariant

| limb | rule | severity | rejects |
|---|---|---|---:|
| `mətbəx (və ya taxça-mətbəx)` | `prog.kitchen_exists` | **hard** | 5.99 % |
| `holl` | — *asserted by construction* | — | — |
| `vanna otağı (və ya duş)` | `prog.washing_exists` | **hard** | 7.33 % |
| `tualet (və ya birləşdirilmiş sanitar qovşağı)` | `prog.wc_exists` | **hard** | 5.19 % |
| `yığnaq otağı (və ya divar təsərrüfat şkafı)` | `prog.storage_exists` | **warn** | 73.35 % |

**One rule per limb, not one rule for the clause.** A single predicate would take
the severity of its weakest limb — storage — and the WC would inherit it. The
split is what lets three be hard and one warn, each carrying its own corpus cost
on the record.

**The `holl` limb gets no rule at all.** `brief.md` §3.1: if the `ResolvedBrief`
contains no `hall`, `resolve` invents one, so every `ResolvedBrief` has exactly
one and the predicate is true by construction. Writing it anyway would add a rule
that can never fire — which is precisely what retired
`win.habitable_touches_exterior` in §7.1. It is recorded rather than written, so
the clause's coverage stays legible.

**The percentages are measured, not asserted.** 46,800 real Swiss dwellings, with
**fixtures as ground truth** rather than room labels: Swiss Dwellings carries
`TOILET`, `BATHTUB`, `SHOWER`, `KITCHEN` and `BUILT_IN_FURNITURE` features, so
each is placed inside the room polygon that contains it and composition is
*observed*. CH provenance against an AZ rule is C14's normal case, and here it is
also the test: a clause that 94 % of Swiss dwellings satisfy is describing homes,
not Azerbaijan.

### 13.2 They bind the Brief, and they have no plan-side twin

Every programme rule is `scope: brief`, `site: validator`, evaluated at parse time
as `brief.md` §9.4 **bound 8**.

That is not a preference for the cheaper site. **The Room set is frozen at
`resolve`** and nothing downstream can change it: §9.5 forbids auto-repair, §3
makes every Brief Room required, the warp maps a donor onto a fixed multiset
(`proposer.md` §2.2), and `model.no_unassigned_area` forces every Room to become a
Space. So a plan-side composition predicate **could never fail on a Plan whose
Brief passed**. §7.1's argument applies unchanged: a rule that cannot fire is a
lie about coverage.

These are therefore the **first rules on this map with an image and no
pre-image**. ADR [0015](../adr/0015-a-parse-time-bound-inherits-the-severity-of-the-rule-it-is-the-pre-image-of.md)
runs the other way — from a shipped Plan rule back to the parse-time bound that is
its arithmetic pre-image, which inherits its severity. Here the parse-time check
*is* the rule, and the severity is chosen against the corpus rather than
inherited. The asymmetry is stated rather than smoothed.

### 13.3 The WC rule cost a room type, and that is the decision

Read literally against the eighteen Room types that existed when this ticket
opened, `prog.wc_exists` **rejects 48.32 % of real dwellings** — and only
**5.19** of those points are dwellings with no toilet. The other **43.13** are
dwellings that *have* a toilet, in a room that also has a bath, which the
vocabulary could not say had one. That is the same shape as the 43.3 % §7.5
records against `win.habitable_has_window`, and like it there is no threshold to
move — but unlike it, the defect is **ours**.

Two corrections and one addition make the rule shippable, and all three are
findings rather than choices:

- **`bathroom` does not contain a WC, and the file said it did.**
  `build_ergonomic_layer.py` computes it as `bath[0] + u × bath[1]` =
  1000 × 1700 = 1.70 m², then asserted *"Pan and basin occupy the same strip as
  the body zone, which is shared."* The fixtures alone are bath 1.19 + pan 0.35 +
  basin 0.27 = **1.81 m²**. Not tight — impossible. The arithmetic never included
  them; the sentence was a gloss on a sum that never ran. Struck.
- **`shower_room` *is* a combined sanitary unit.** Its programme is
  `max(tray 900, pan 700 + u) × (tray 900 + pan 500)` — it composes the pan. So
  one of the eighteen types already put the WC inside the washing room, while
  `room-constraints.json`'s AZ bridge asserted *"the ergonomic layer… carries no
  way to say the WC is inside."* That sentence was false when written, and
  `areas_m2.bathroom_combined.reachable_in_v1: false` rested on it.
- **`bathroom_combined` is a nineteenth Room type**, 1500 × 1700 = **2.5 m²**:
  bath 1700 × 700 along one wall, pan 700 + basin 600 = 1300 ≤ 1700 opposite at
  500 deep, one shared 300 body aisle between — what a real 1500 mm bathroom does.
  It rejects **6.17 %** of 35,821 real bath+WC rooms, in family with the layer's
  ~5 % calibration target, and the corpus's own short-side **p5 of 1477 mm**
  independently reproduces the derived 1500. Its AZ soft target was already in the
  data, sourced and unused, at 3,8 m²; real such rooms run a median 4,25 m².

With the type in place the WC rule costs **5.19 %**, which is the defect and not
the vocabulary.

### 13.4 The second reason `bathroom_combined` was blocked, and why it does not hold

`reachable_in_v1: false` gave a second reason: **cl. 5.10** confines the combined
unit to «dövlət və bələdiyyə sosial təyinatlı və xüsusi təyinatlı mənzil
fondunun birotaqlı mənzilləri» — one-otaq flats of the state and municipal social
and special-purpose housing stock — a class v1 cannot detect.

**That is a compliance target, and C8 forbids reading one.** The banner at the top
of this document is not decoration: *every regulatory document cited here is cited
as a source of dimensional fact, never as a compliance target.* cl. 5.2 tells us
**what rooms a home has**, which is a fact about homes and which the corpus
corroborates at 94 %. cl. 5.10 tells us **which class of flat is permitted to
combine**, which is a permission, and the corpus **refutes** it as a description
of practice: of 44,372 real dwellings with a placed toilet, **67.24 % put every
toilet in a room with a bath or a shower**. Only 32.76 % have a separate WC room.

So v1 may draw a combined unit, makes no compliance claim about it, and the
restriction is recorded in the data beside the type. Declining to draw the
majority configuration in order to honour a permission we are not claiming to
satisfy would have been the error.

### 13.5 `resolve` does not invent the missing room

C4 fills gaps from standards and `resolve` already invents circulation, so
inventing a WC is the same move — and it is **refused**.

`brief.md` §9.5: the system never deletes a Room, shrinks a programme or relaxes a
veto to make a Brief fit. The hall is exempt for a reason that does not transfer:
ADR 0013 requires the **engine room count fixed before any geometry exists**, and
no Homeowner has ever stated circulation out loud — it is invented in 93.5 % of
real dwellings. A Homeowner who omits a toilet has made a statement about the
home. Inventing one silently also **spends a room out of C13's 3–10 gate**, so a
Brief at ten rooms would be refused *because we added one*.

The refusal names the field instead, and that is §9.4's contract: a set of
findings, each with a severity, a Brief field and a message.

### 13.6 What this section does not close

- **Two limbs are satisfied by a type the Brief cannot name.**
  `taxça-mətbəx` (kitchen-niche) is expressed as a `kitchen`, and
  `divar təsərrüfat şkafı` (built-in wardrobe) is furniture v1 does not model. The
  first is a recorded narrowing that under-targets; the second is why
  `prog.storage_exists` is **partly unsatisfiable**, not merely expensive.
- **`prog.storage_exists`'s 73.35 % is not clean evidence.** A Swiss flat's
  storage is typically a *Keller* outside the dwelling, invisible to a
  dwelling-scoped corpus. The number overstates the case against the room, which
  is an argument for `warn` and against `hard` in both directions at once.
- **The four messages are English and the surface is Azerbaijani.** These rules
  arrive already owing the locale dimension the other 36 owe. They do not make
  that schema change; they enlarge it from 36 to 40.
- **`bathroom_combined` needs a corpus splitter.** `ergonomic.corpus_label_split`
  divides the `BATHROOM` label two ways at 2.4 m². With a third class the split
  should become three-way on the fixture ground truth that is already there —
  which is retrieval and conversion data, not the bar.
