---
id: 19
title: Ergonomic minima and the constraint table's missing half
parent: map
labels: [wayfinder:research]
status: closed
assignee: tng
blocked_by: []
---

# Ergonomic minima and the constraint table's missing half

## Question

**`data/standards/room-constraints.json` is a stub, and *Acceptance validator
spec* has just made its missing half the entire hard rule set.**

*Dimensional standards corpus* records the table as shipped. It is not. The file
is 9 KB and ends:

```json
"PLACEHOLDER_NOTE": "DE and US sources, the ergonomic layer, and the room table are appended below in the completed file."
```

Present: UK sources, `region_model`, `tier_model`, `flag_semantics`,
`value_format`. **Absent: the ergonomic layer, the room table, and the DE and US
sources.** The room table exists only as prose in `docs/research/dimensional-standards.md`
§8, and only for the `DE` / `market_default` column.

This is not a transcription job. *Acceptance validator spec* changed what the
missing layer has to be:

- The validator's hard floor is no longer `statutory_floor` — that tier is `null`
  for the default region, so it yields an **empty hard set**. It is the
  **ergonomic minimum**: the smallest clear rectangle a room's required fixtures
  and their body clearances occupy.
- The hard rule set therefore **carries no region**. This layer is the only thing
  standing between a Plan and rejection, in every region, including ones never
  surveyed.
- Three registry rules — `dim.min_area`, `dim.min_clear_width`,
  `dim.min_clear_depth` — are `conf: pending` until it lands. Their structure is
  final. Only the values are missing.

Settle:

- **Derive, do not quote.** Per §7 of the findings, numbers are facts and tables
  are expression. Each ergonomic minimum must be *composed* from fixture
  footprints plus stated body clearances, with the arithmetic shown, so its
  provenance is a derivation rather than a transcription. §5.3 already carries
  much of the clearance material.
- **Width and depth are directional for `bathroom` and `wc` and not for the
  rest** (§8). Establish whether that survives derivation, or whether more room
  types turn out directional once fixtures drive the rectangle.
- **The ergonomic minimum for rooms with no fixtures** — `living`, `dining`,
  `study`, `hall`, `storage`. Furniture is not a fixture and is still fog on the
  map. Decide what the floor is for a room whose function is not a plumbed object,
  and mark it honestly.
- **`de_baybo` is a dangling source key** — `win.area_ratio` in
  `data/acceptance/rules.json` cites it, and the DE sources block does not exist.
- Complete the room table as data for all defined regions, and finish or
  explicitly re-stub the US profile (findings §10 gap 1: US light-frame wall
  thicknesses are the largest geometric divergence in the corpus and were never
  written up).

Cross-check every value against `data/acceptance/rules.json`: the registry is the
consumer, and any minimum it cannot read is a rule that silently does not fire.

Deliverable: the completed `data/standards/room-constraints.json` with an
`ergonomic` layer, each value carrying `v` / `src` / `ref` / `conf` / `note` per
the file's own `value_format`, and the three `pending` registry rules flipped to
real numbers.

## New obligation from *What the model proposes, and how it is trained*: the WC/bathroom split

Both Proposer sources read Swiss Dwellings, and **the corpus has one `BATHROOM`
label spanning p5 1.5 m² to p95 6.3 m²** — a WC at one end, a family bathroom at
the other (measured, `experiments/retrieval-coverage/room_label_probe.py`). A
Brief distinguishes them and this table already does: `dim.min_area` is a
different number for `wc` and for `bathroom`, and both are `conf: pending` here.

So the corpus has to be split by area before either source can use it, and **the
splitting threshold is this ticket's**, not the Proposer's. It is derived from the
same fixture footprints and body clearances this ticket is already deriving — a WC
is a pan plus its clearance, a bathroom is a pan plus a basin plus a bath or
shower plus theirs. Inventing a second number on the Proposer side would create a
table to drift against this one, which is exactly the failure *Acceptance
validator spec* closed for the acceptance rules.

Deliver it as part of the `ergonomic` layer, not as a one-off constant: the
threshold is the boundary between two rooms' minima, so it falls out of the table
rather than being added to it.

Note the direction it cuts. Set the threshold too high and real WCs are relabelled
as undersized bathrooms and dropped from training; too low and real bathrooms
enter the WC class and pull its minimum down. State which error the value prefers.

## Constrained by ADR 0007, from *Solver timing variance sweep*

Every minimum this ticket publishes must satisfy

```
minimum_mm + t_int  is congruent to 0  (mod grid_mm)
```

for every internal wall thickness the profile offers. At the v1 grid of 250 mm
and `t_int = 100` that admits 1650, 1900, 2150, 2400 ... and forbids the round
numbers a source is likeliest to quote: 1750, 2000, 2250, 2500.

This is not tidiness. ADR 0001 makes the published minimum a **clear** dimension,
so `250w - t_int >= minimum` forces `w >= minimum/250 + 1` whenever `minimum` is
a multiple of the grid — one whole grid unit of rounding loss per room per axis,
to pay for a 100 mm wall. Measured, that **provably deletes 4-, 5- and 6-room
dwellings**: no exact tiling exists and no Brief can even be constructed. Extra
Envelope area does not fix it (swept to +40%, non-monotone). Grid-aligned minima
restore the pre-ADR-0001 baseline exactly.

So a source quoting 1750 mm is honoured by publishing **1650 mm clear**, with the
derivation recorded in the provenance field so nobody later "corrects" it back.
Same move ADR 0004 made for dimensions, and it needs the same paper trail.

Note the trap ADR 0007 leaves open: a profile offering **two** internal
thicknesses has no common solution at a 250 mm grid, because 100 and 200 want
minima congruent to 150 and 50 respectively. Either the minima become
per-thickness, or the profile ships one `t_int`, or the grid changes.

## Handed over by *The Azerbaijani region profile*

Both tickets share `data/standards/room-constraints.json`. That one wrote
`profiles` only and left `ergonomic` untouched; the two blocks now coexist in the
file with no collision. Three things it found bear directly on this layer.

**1. Azerbaijani law points at this layer by name — so it is load-bearing, not a
fallback.** AzDTN 2.7-2 cl. 5.6 delegates every intra-apartment clear dimension to
*erqonomika* explicitly, as does СП 54.13330.2022 cl. 5.11. That is why **all six
width cells at AZ's `statutory_floor` are `null` by design**, and it means the
region that ships has no linear minima of its own at all. Whatever this layer
publishes is what the solver posts, in the only region v1 sells.

**2. ADR 0007 collides with this layer, and 36 of 36 values are affected.**
Measured by `experiments/region-profile/gate_check.py` against the layer as
authored and the shipped `t_int = 120`:

```
hard linear minima published by profile AZ: 0
hard linear minima published by the region-INVARIANT 'ergonomic' layer:
    36, of which 36 miss the residue class 130
```

Costs run to **+230/+242 mm per room per axis**, worst on `corridor` and `hall` —
the rooms the solver's circulation model rests on. This is **not** a defect in this
layer's numbers: this layer's own `reading` field already states the reason, and
states it correctly — *"Nothing here is nominal or centreline, so nothing here has
`t_int` to subtract."* Exactly so, and that is precisely why ADR 0007's
publish-below-the-source move cannot be applied here: it is legitimate for a
*convention*-derived figure and illegitimate for a *body*-derived one.

✅ **Already settled by this ticket's own ADR 0009**, which landed while the AZ
profile was being merged and reaches the same conclusion from the other side. No
action owed. A ticket drafted for it in the AZ session was **retracted rather than
filed**. The 36 rows stay in `gate_check.py`'s output as evidence that the
exemption is load-bearing, not cosmetic.

One thing ADR 0009 does **not** cover, and it is narrower: ADR 0007 still binds
region profiles, and as written it binds *every* dimensional minimum there. Only a
linear minimum the solver posts on a room's **clear rect** is eroded by `t_int` —
areas in m², storey heights, door clear widths and wheelchair turning squares are
not. Moot for AZ, which publishes no hard linear minimum at all, but owed before a
second profile does.

**3. `de_baybo` is closed, and one of its rules inverted its premise.** Both
consumers in `data/acceptance/rules.json` are re-sourced to AzDTN 2.7-2:
`win.area_ratio` → cl. 9.13 (1:8 lower bound, no cap; value unchanged at 0.125),
and `win.kitchen_windowless` → cl. 9.12.

**That second one needs this ticket.** The rule was a `warn` and the table sets
`needs_window: false` for kitchen *because Bayern permitted a windowless kitchen*
where ventilation is provided. **Azerbaijan requires the window** — AzDTN 2.7-2
cl. 9.12, `force: statutory`, corroborated for houses by AzDTN 2.7-3 cl. 8.14. So
in the only region v1 ships, the table currently permits something that is a breach.

It was **not** promoted to `hard` from the region side, because C14 forbids a
region changing which Plans are rejected. **Flipping `needs_window` to `true` for
kitchen is region-invariant, is this layer's call, and is the honest fix** — the
flag's own semantics already say the window requirement is an engine decision made
because a Homeowner judges by "would I live here". AZ evidence supports applying it
universally rather than regionally.

Detail: `docs/research/az-region-profile.md`.

---

## Resolution

**The layer is authored, and the ticket's own method had to be corrected twice
before a single number could be published.** Data:
`data/standards/room-constraints.json` key `ergonomic`, generated by
`experiments/region-profile/build_ergonomic_layer.py` so the numbers and the
arithmetic cannot drift. Findings: `docs/research/ergonomic-minima.md`. ADR
[0009](../../adr/0009-a-derived-minimum-is-not-rounded-onto-the-solve-grid.md).
Harnesses in `experiments/region-profile/` and
`experiments/solver-toy/ergonomic_minima_tiling.py`.

### The two corrections, because they are the finding

**A derived floor is not self-justifying.** Composed from the clearances the
sources actually state, the `bathroom` floor lands at 4.0 m² — which **rejects
36% of real, built, QA'd Swiss bathrooms**. The mistake was treating **AD M's
750 mm as a body clearance when it is a wheelchair transfer space**. Every
clearance in the whole source corpus is an accessibility figure, because those are
the ones regulators write down; the ordinary private bathroom has no regulator,
which is exactly why §5.1 said the engine's dimensions have to be its own choices.
*Rectangularising real rooms* had already set the principle that catches this: a
hard rule that rejects real homes measures what our model cannot express.

**And the low tail is real, so there is no escape hatch.** Checked against the
corpus's own fixture entities — Swiss Dwellings carries `BATHTUB`, `SHOWER` and
`TOILET` — **0% of `wc` rooms fail to hold a pan and 0.8% of `bathroom` rooms fail
to hold a 1700 mm bath.** Not annotation debris. Homes.

So: **structure derived, one constant calibrated.** Every value is published
footprints plus `u`, the body zone that cannot be shared with another fixture's
zone — and the modelling rule that does most of the work is that zones **may** be
shared while a zone may never overlap another fixture's *footprint*. Fitted so no
room type rejects more than ~5% of fixture-consistent real rooms, `u` lands on
**300 mm**, which is also **Neufert's stated minimum from a WC pan's free side to
a wall**. Fitted and cited agree, which is §7.6 item 10's test for a body fact.

The corpus is allowed to **falsify** a number and never to supply one.

### The table

18 room types, clear, `(shorter side, longer side)` — `wc` 800×1000 / 0.8 m²,
`bathroom` 1000×1700 / 1.7, `bedroom_double` 1650×1900 / 3.1, `living`
1850×2000 / 3.7, up to `living_dining_kitchen` 1850×4050 / 8.5. Published reject
rates against the corpus: 0.0% living, 0.0% private, 1.2% kitchen, 4.6% wc, 7.8%
storage. `min_area` is `short × long` rounded **down**, or the rule would reject
the rectangle it was derived from.

**These are floors, not targets** — the `living` floor is 3.7 m² against a corpus
median of 20.6, and that is correct. Liveability is the region profile's job, and
C14 already guarantees a profile can change what is *preferred* and never what is
*rejected*.

**§8's directional/orientation-free distinction dissolves.** It is not that
`bathroom` and `wc` are directional and the rest are not: the rules are stated over
the **shorter and longer** clear dimension rather than over x and y, so no room
type needs an axis binding at all — and once fixtures drive the rectangle, *most*
types are non-square. Only `corridor` is square, because it has no second
dimension of its own.

**Composite rooms are a permissive envelope.** `living_dining` and friends can be
packed more than one way and a `(short, long)` pair cannot say "contains packing A
*or* B", so the smallest short, smallest long and smallest area over all packings
are published. That under-rejects and never over-rejects, which for a hard floor
is the correct error direction.

**The four flags now exist as data.** `is_habitable`, `is_wet`, `is_private`,
`needs_window` were defined in `flag_semantics` and tabulated only as prose in §8,
while four registry rules consume them — a flag the registry cannot read is a
predicate that silently does not fire, the same failure as a missing minimum. Each
consuming rule now carries a `flag_source`. **One correction:** §8 sets `study`
`is_private: false`; `CONTEXT.md` defines the Private room class as *"a Brief's
bedroom, study or nursery, as one class"* and the Proposer spec collapses `{ROOM,
BEDROOM, STUDIO}` on the same reasoning. A study that is a thoroughfare is not a
study. Set **true**.

### ADR 0007 does not bind here, and that was the session's one HITL decision

ADR 0007 rounds published minima **down** onto the lattice, and its justification
is a **unit conversion** — the source quoted a nominal or centreline figure, so
subtracting `t_int` recovers the clear one. Sound for a **quoted** number. **A
derived number has nothing to subtract**: it is already clear, and a derived
1700 mm *is* the bath. Rounding it to 1650 deletes 50 mm of bathtub.

So the layer can only round **up** — and rounding up is arithmetically *identical*
to leaving the minimum unaligned, which is the row ADR 0007 measured as fatal.
There is no third option.

Measured cost of obeying ADR 0007 here: the `wc` floor goes from 23.0% to **56.1%**
of real WCs rejected, because **the entire real WC width distribution — p1 744 to
p50 1099 — spans less than two grid steps**. At the shipped `u` it is ≈10 points.

**Decided with the map's owner: the ergonomic layer is exempt; ADR 0007 keeps
binding on the region profile; the grid stays 250 mm.** A 50 mm grid would make
the congruence vacuous and the bath exactly representable, and was rejected for v1
because every solver number on the map — 15 s, τ = 4, 6.25 s at 24 rooms, the
two-worker floor — was fitted at 250 mm. Nothing published here is snapped, so
**changing the grid later changes no published minimum**, which is the opposite of
where ADR 0007 alone would have left us. C15 must now be read as naming two
constraints on two different layers.

Re-running ADR 0007's own counts at 8 seeds reproduces its deletion cleanly on the
placeholder table — **0/8 at n = 4, 5 and 6, no Brief constructible at all**.

⚠️ **The corroborating half came back mixed, and it is reported as mixed.** Against
the derived floor's own baseline, the clear reading **recovers n = 4 outright**
(0/8 → 8/8) and **still loses n = 5 entirely** (8/8 → 0/8, Briefs constructible, no
valid tiling found). n = 6 is **not assessable** — the derived table fails it under
the baseline reading too, where the congruence question does not arise, so that
cell is the harness's Brief generator meeting much smaller minima rather than
evidence about the grid. **The deletion narrows from `{4,5,6}` to `{5, and 6
unknown}`; it is not removed.** The magnitude hypothesis is half right.

**The decision still stands, and not on that measurement.** ADR 0007's remedy is a
nominal-to-clear conversion and a derived minimum has none to apply, so the
alternative is not a smaller table but a bathroom floor that cannot hold a bath.
What the result does change is the fog: *whether the solve grid should be finer
than 250 mm* now carries a **measured cost of staying** — the 5-room case, the
bottom of C13's promised band and the commonest dwelling size in the corpus, is
paying for the 250 mm grid.

### The `BATHROOM` split — the obligation's stated premise is refuted

*What the model proposes* handed this ticket the threshold on the reasoning that
it is *"the boundary between two rooms' minima"* and *"falls out of the table"*.
**It does not, and it cannot.** Two floors are both floors: `wc` is 0.8 m² and
`shower_room` 1.4 m², and a threshold there misclassifies 19% of the corpus. The
classes differ in their **distributions** — `wc` median 1.85 m², `bathroom` 4.17 —
not their minima, and a splitter is not recoverable from the bottom of two
overlapping distributions.

It did not have to be invented either. Fitted against **fixture ground truth** over
66,386 labelled rooms: **2.4 m²**, 5.9% total misclassification, against a measured
optimum of 5.8% at 2.45. The derived candidates score 23.3% (3.6 m²) and 36.9%
(4.0 m²). A second term on the long side buys nothing — the best two-term rule
collapses back onto the area term.

Direction: it over-assigns to `bathroom` about three to one. An over-large `wc`
wastes floor and breaks nothing; a `bathroom` that is really a WC still clears the
1.7 m² floor and is still a real Swiss room, so it yields a small bathroom, not an
invalid Plan. Neither error moves a published minimum, because none is fitted.
*(The obligation's own sentence about the direction inverts the mapping — above the
threshold is `bathroom`, so setting it too high moves real bathrooms into the WC
class.)*

### The registry

All three `pending` rules flipped: `dim.min_area`, `dim.min_clear_width`,
`dim.min_clear_depth` — **`rules.json` now carries zero `pending` rules.** Each
points at its value by JSON pointer rather than copying it. `hard_reject_below` is
`ergonomic` in **both** files, where the two previously disagreed (`null` against
`ergonomic_min`). `dim.corridor_min_width` cross-checked: the `hall` floor is also
900, so the two agree rather than one silently subsuming the other.

**`de_baybo` was closed by someone else, better.** This ticket added the missing
BayBO source block; *The Azerbaijani region profile*, running concurrently,
**re-sourced both consumers to AzDTN 2.7-2** instead. That is the stronger fix, and
not only because it removes a dependency on a deleted region's law: it caught what
adding the block would have hidden — **AZ requires a kitchen window where Bayern
expressly permitted its absence**, so `win.kitchen_windowless` had an *inverted*
premise, not just a missing citation. The block added here was withdrawn once
nothing cited it; an unused source in a data file is the drift this project keeps
killing. The generator carries a comment so it is not re-added.

### Not done, and why

- **The US profile is discharged, not answered.** *Which region profiles ship in
  v1* deleted `US` outright, so §10 gap 1 blocks nothing.
- **`study` is the weakest number in the file** — a one-desk programme, no corpus
  label to falsify it, no source that states a study minimum. `utility`, `hall`
  and `entrance_lobby` are likewise unfalsified.
- **`storage` rejects 7.8%**, the worst published rate. Its low tail is p1
  358 × 658 mm, which are built-in cupboards rather than rooms. Flagged, not fitted.
- **The AZ profile landed in this same file concurrently and uses a different room
  vocabulary** (`living_room_1room_flat`, `living_room_2plus`) from the ergonomic
  layer's. Ordering is consistent — AZ's `living` statutory floor of 15.0 m² sits
  far above the ergonomic 3.7 — so nothing contradicts, but **a Plan cannot resolve
  one key from the other**. Ticketed rather than fixed inside someone else's
  vocabulary.
