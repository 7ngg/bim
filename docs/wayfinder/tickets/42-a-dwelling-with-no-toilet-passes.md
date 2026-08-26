---
id: 42
title: A dwelling with no toilet passes every check
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - data/acceptance/rules.json
  - docs/spec/acceptance-bar.md
declared_on_resolution:
  - docs/spec/brief.md (§9.4 bound 8, §9.1, §3, §12 — no claimant)
  - CONTEXT.md (Programme rule, Combined sanitary unit, Room type, Auxiliary space — no claimant)
  - docs/adr/0022-a-dwelling-owes-rooms-and-the-brief-is-where-that-is-checked.md (new)
  - data/standards/room-constraints.json (nineteenth type + three corrections; listed as 32's, unclaimed at the time)
  - experiments/region-profile/build_ergonomic_layer.py (nineteenth programme; preserve-merge fix)
---

# A dwelling with no toilet passes every check

## Question

**Nothing in this system requires a dwelling to contain any particular room.**
Every dimensional rule is of the form *if a Room of type T exists, it is at least
this big*. Not one asks whether T exists at all. So a Brief naming a living room,
a bedroom, a kitchen and a bathroom resolves, solves, passes all 38 predicates,
and exports a valid IFC of a flat **with no toilet**.

"A bathroom implies a WC" is not available as a defence. The ergonomic floor for
`bathroom` is **1000 × 1700 mm** — a bath and nothing beside it — and
`CONTEXT.md` treats `wc` as a separate Room type that a Brief names separately.
Found while building the room vocabulary mapping (*Two room vocabularies in one
file*), which is where the absence became visible: the mapping is total over room
*types*, and total over types says nothing about which types a **dwelling** owes.

### The source is already read, and it is mandatory

AzDTN 2.7-2 **cl. 5.2**, in the file at
`experiments/finish-layer/out/azdtn_2_7_2.txt`:

> «Mənzillərdə yaşayış otaqları və yardımçı sahələr: mətbəx (və ya taxça-mətbəx),
> holl, vanna otağı (və ya duş) və tualet (və ya birləşdirilmiş sanitar qovşağı),
> yığnaq otağı (və ya divar təsərrüfat şkafı) nəzərdə tutulmalıdır.»

Register `nəzərdə tutulmalıdır` = **məcburi**, mandatory, per the file's own
`source_force_vocabulary`. Every flat shall have: a kitchen **or** kitchen-niche;
a hall; a bath **or** shower; a **WC or combined sanitary unit**; a storage room
**or** a built-in utility cupboard.

This is a **composition** requirement — a shape of rule the acceptance bar does
not currently have. All 38 predicates are per-Room, per-Wall, per-Opening or
per-Plan-geometry. None is *per-programme*.

Settle:

- **Does the rule bind the Brief, the Plan, or both?** It reads like a §9
  parse-time check — cheaper to tell a Homeowner "this needs a toilet" before a
  generate cycle than after. But `resolve` invents circulation, so a `hall` can be
  satisfied by invention while a `wc` cannot, and the two halves may not enforce
  in the same place. Note `site: both` is the shape *Acceptance validator spec*
  uses when a rule must hold in the solver and the validator; this may want a
  third site the registry has no word for.
- **Hard or soft, and does that differ per room.** A missing WC is a defect
  nobody would ship. A missing `yığnaq otağı` is a storage cupboard, and the norm
  offers `divar təsərrüfat şkafı` — a *built-in wardrobe* — as an alternative,
  which is furniture this engine does not model. One clause, and its five limbs
  do not obviously carry the same severity.
- **Whether `resolve` should add the missing room rather than reject.** C4 says
  gaps are filled from standards and every assumption surfaced, and `resolve`
  already invents circulation. Inventing a WC is the same move. But it changes the
  Engine room count, which C13's band gates on, and a Brief at 10 rooms that gains
  an eleventh is refused *because we added it*.
- ⚠️ **The alternatives are disjunctions the model may not be able to express.**
  `mətbəx (və ya taxça-mətbəx)` — the Brief has no `kitchen_niche` type at all
  (*Two room vocabularies* recorded that narrowing). `tualet (və ya birləşdirilmiş
  sanitar qovşağı)` — no ergonomic key can say the WC sits inside the bathroom, so
  the second limb is **inexpressible**, and a rule that demands a `wc` Room would
  reject the combined-unit layout the norm permits. Deciding this rule may require
  deciding whether the room vocabulary grows.
- **What C8 permits us to say about it.** The source is statutory and the register
  is mandatory, so `statutory_floor_binding: warn` is the established posture for
  *dimensional* AZ numbers. A composition rule that only warns produces a flat with
  no toilet and a warning. If it is hard, it is the **first hard rule sourced to a
  region document**, and C14 says a profile may never change which Plans are
  rejected — so it would have to live on the region-invariant layer, and the
  justification cannot be "Azerbaijani law says so".

The closing check: **a Brief that names no `wc` and no combined unit cannot reach
export**, and a conformance test asserts the composition rule at whichever site
the answer puts it.

### Concurrency

`data/acceptance/rules.json` is also claimed by 16, 20 and 26;
`docs/spec/acceptance-bar.md` by 26. Per the map's Notes this is a merge hazard,
not a dependency — do not run this at the same time as any of them.

---

## Handed here by *Look at the converted corpus* (2026-08-25)

⚠️ **The acceptance bar has nothing to say about a Plan with a hole in it, and
that gap is now measured rather than suspected.** ADR
[0017](../../adr/0017-three-of-the-conversions-fidelity-headlines-are-constraints-restated.md),
failure mode 2.

Exact tiling is posted **soft** (C10's amendment), so an Envelope cell no Space
claims is legal and the objective merely charges for it. **Nobody had ever drawn
one.** Rendered, it is floor with walls round it and no name —
indistinguishable on a drawing from a room, and a Practitioner has nothing to
call it.

Measured over 400 converted dwellings
(`experiments/rectangularise/void_census.py`), separating the Envelope's
deliberate notch **under-cut** — correctly left empty — from real dwelling floor:

| | median | p90 | max |
|---|---:|---:|---:|
| uncovered, total | 2.31 m² | 6.63 m² | 11.00 m² |
| — Envelope over-reach *(correct)* | 0.44 m² | 4.06 m² | 8.56 m² |
| — real floor, unclaimed | **1.19 m²** | 3.25 m² | 8.38 m² |
| — of that, **enclosed** by Spaces | 0.00 m² | 0.44 m² | 3.69 m² |

Most of the unclaimed floor opens onto the Envelope edge and reads as a
re-entrant in the outline, which is harmless. The enclosed remainder is not:
**15.0 % of dwellings carry an enclosed void ≥ 0.25 m², 10.0 % ≥ 0.5 m², 4.8 %
≥ 1 m².**

**Why this is yours and not the corpus's.** The number above is the conversion's,
but the rule is the acceptance bar's. **C6 already discards an expired candidate
whose best objective is ≥ `soft_weight`** — that is a candidate with unassigned
floor at *timeout*. It says nothing about an **OPTIMAL** candidate that carries a
1 m² unnamed hole because the tiling term simply lost to another. A ticket about
what a dwelling must contain to pass is the right home for *"and it must contain
no floor that belongs to nothing"*.

**What to decide:** whether unassigned floor inside the Envelope is a finding at
all, and if so whether it is severity-graded by area, by enclosure (enclosed
versus edge-open, which the census separates), or refused outright. A threshold
picked by eye is worse than none — the distribution above is the input to
choosing one.

⚠️ **Do not reach for `uncovered` in a fit record as the quantity to gate on.**
It sums the correct case and the incorrect one together, which is exactly why
nobody had noticed this. `void_census.py` splits them.

---

## Resolution (2026-08-26)

**Four `programme` rules, one per limb of AzDTN cl. 5.2, binding the Brief and
nothing else. Three hard, one warn. The WC limb cost a nineteenth Room type, and
that was the decision.** ADR
[0022](../../adr/0022-a-dwelling-owes-rooms-and-the-brief-is-where-that-is-checked.md);
`acceptance-bar.md` §13; `brief.md` §9.4 bound 8.

| limb | rule | severity | rejects real dwellings |
|---|---|---|---:|
| `mətbəx (və ya taxça-mətbəx)` | `prog.kitchen_exists` | **hard** | 5.99 % |
| `holl` | — asserted by construction | — | — |
| `vanna otağı (və ya duş)` | `prog.washing_exists` | **hard** | 7.33 % |
| `tualet (və ya birləşdirilmiş sanitar qovşağı)` | `prog.wc_exists` | **hard** | 5.19 % |
| `yığnaq otağı (və ya divar təsərrüfat şkafı)` | `prog.storage_exists` | **warn** | 73.35 % |

The bar is **40 rules**, 41 once `dim.leg_join` lands. The `both` conformance
subset **stays at 14** and cannot grow here.

### The ticket's five questions

**Brief, Plan or both — Brief only, and it is forced rather than chosen.** The
Room set is frozen when `resolve` returns: §9.5 forbids auto-repair, §3 makes
every Brief Room required, the warp maps a donor onto a fixed multiset, and
`model.no_unassigned_area` turns every Room into a Space. A plan-side composition
predicate could never fail on a Plan whose Brief passed, and §7.1 already retired
a rule for exactly that. The ticket asked whether this wants "a third site the
registry has no word for" — **it does not**. `scope: brief` already exists and
three rules ship on it. These are the first rules with an **image and no
pre-image**, which inverts ADR 0015 rather than extending it.

**Hard or soft, per limb — and it does differ per limb, which is why it is four
rules and not one.** A single predicate over the clause takes the severity of its
weakest limb, and the WC would have inherited storage's 73.35 %.

**Whether `resolve` should add the missing room — refused.** §9.5, and the hall's
exemption does not transfer: ADR 0013 needs the room count fixed before geometry
exists and no Homeowner states circulation. Inventing a WC also spends a room out
of C13's 3–10 gate, so a Brief at ten rooms would be refused *because we added
one*.

**The disjunctions — ⚠️ this bullet's premise was half false, and the false half
was the load-bearing one.** The ticket held that the combined unit is
*inexpressible*, so a hard `wc` rule would reject a layout the norm permits. In
fact **`shower_room` has composed a WC pan since the ergonomic layer was
authored** — `max(tray 900, pan 700 + 300) × (tray 900 + pan 500)` — so a combined
unit was already reachable, while `room-constraints.json`'s AZ bridge asserted the
layer *"carries no way to say the WC is inside."* The `taxça-mətbəx` half of the
bullet **is** true and is unchanged: no Brief type, expressed as a `kitchen`.

**What C8 permits — it permits the hard rules and forbids the restriction.** C14
binds *region profiles*; these are not in a profile, they sit in the
region-invariant set and key on region-invariant Room types. AzDTN supplies the
fact that a home owes a kitchen, a washing room and a WC, and 94.01 % / 92.67 % /
94.81 % of real Swiss dwellings corroborate it — which is the test that the fact
is about homes rather than about Azerbaijan. C8 then cuts the other way on
**cl. 5.10**; see below.

### What it cost: a nineteenth Room type

Read against the eighteen types that existed, `prog.wc_exists` **rejects 48.32 %
of real dwellings** — and only **5.19** of those points are dwellings with no
toilet. The other **43.13** are dwellings that *have* a toilet, in a room that
also has a bath, that the vocabulary could not say had one. Same shape as the
43.3 % this map already calls large on `win.habitable_has_window`, and no
threshold to move — but here the defect is **ours**.

Three findings closed it, none of them a preference:

- ⚠️ **`bathroom` does not contain a WC and the file said it did.**
  `build_ergonomic_layer.py:77-80` computes `bath[0] + u × bath[1]` =
  1000 × 1700 = 1.70 m², then asserted *"Pan and basin occupy the same strip as
  the body zone, which is shared."* Fixtures alone: bath 1.19 + pan 0.35 + basin
  0.27 = **1.81 m²**. Not tight — impossible. The sentence was a gloss on a sum
  that never ran. **Struck.**
- ⚠️ **`shower_room` is a combined sanitary unit** and two documents denied it.
  Said out loud in the programme now.
- ✅ **`bathroom_combined`, 1500 × 1700 = 2.5 m²** — bath 1700 × 700 along one
  wall, pan 700 + basin 600 = 1300 ≤ 1700 opposite at 500 deep, one shared 300
  body aisle, which is what a real 1500 mm bathroom does. It rejects **6.17 %** of
  35,821 real bath+WC rooms, in family with the layer's ~5 % calibration target,
  and the corpus's own short-side **p5 of 1477 mm** independently reproduces the
  derived 1500. Its AZ soft target was already in the data, sourced and unused, at
  **3,8 m²**; real such rooms run a median 4,25 m², p25 3,71.

With the type the WC rule costs 5.19 %.

### cl. 5.10 is recorded and deliberately not enforced

`areas_m2.bathroom_combined.reachable_in_v1: false` rested on two reasons and both
are spent. The first — *no ergonomic key can say the WC is inside* — was false
when written. The second is **cl. 5.10**, which confines the combined unit to
«dövlət və bələdiyyə sosial təyinatlı və xüsusi təyinatlı mənzil fondunun
birotaqlı mənzilləri».

**That is a compliance target and C8 forbids reading one.** cl. 5.2 states what
rooms a home has — a fact about homes. cl. 5.10 states which flats may combine — a
permission. And the corpus refutes it as a description of practice: of 44,372 real
dwellings with a placed toilet, **67.24 % put every toilet in a room with a bath
or a shower**; only 32.76 % have a separate WC room, at a median 1.84 m² which
independently reproduces `corpus_label_split`'s 1.85 m². Declining to draw the
majority configuration to honour a permission we make no claim to satisfy would
have been the error. The marker is **reversed**, with the restriction recorded
beside the type.

### The second half — the premise was false

⚠️ **The unassigned-floor handoff from *Look at the converted corpus* rests on a
claim that is not true, and the map's Acceptance-bar row repeats it.**
`model.no_unassigned_area` is **hard**, `site: both`, `scope: plan`: *"The union
of all Space polygons and all Wall bodies equals the Envelope interior exactly."*
Its own note says why: *"Posted soft in the solver for search speed and checked
hard here… the place where a 29× faster search is prevented from shipping a
hole."* So exact tiling is soft **in the solver** and hard **in the validator**,
and an OPTIMAL candidate carrying a 1 m² unnamed hole **cannot be shown**. No rule
is added and none is owed.

What survives is smaller and is not the bar's: the 10.0 % figure measured the
**conversion**, so a donor with an enclosed void enters the retrieval index, and
the warp has no term for it — the solve must then absorb it into a bordering Room
as area the Brief did not ask for. Raised as
[A donor's enclosed void becomes area nobody asked for](53-a-donors-enclosed-void-becomes-area-nobody-asked-for.md).

### A destructive generator, found by tripping it

⚠️ **`build_ergonomic_layer.py` deleted three later tickets' work on every
re-run, in silence.** It authors the arithmetic and the four definitional flags
and nothing else, but ticket 31 added `counts_as_otaq`, `brief_nameable` and
`counts_as_otaq_sourcing` by hand, *Brief schema and parsing contract* added
`reachable_in_v1`, and *What a room's area is allowed to be* added
`corpus_medians` — none reproducible from the generator. Re-running dropped all
of it without a word, which is the exact drift the module docstring claims
generation prevents. **This ticket tripped it**, restored from git, and fixed it:
the generator now carries forward every key it does not author, and **fails loudly**
if a room type has no `counts_as_otaq`/`brief_nameable` to carry or supply. Any
ticket that has run this file since ticket 31 landed should check its own work
survived.

### Written

| file | what |
|---|---|
| `data/acceptance/rules.json` | four `prog.*` rules, `item: programme`, `scope_meanings`, a `programme_rules` block. 36 → **40** |
| `docs/spec/acceptance-bar.md` | new **§13** (six subsections); counts at four sites; three §12 handoffs |
| `docs/spec/brief.md` | §9.4 **bound 8**; §9.4 preamble seven → eight; §9.1 fourth hard error; §3 eighteen → **nineteen** types; §12 discharged one row, added three |
| `docs/adr/0022-…` | new |
| `CONTEXT.md` | **Programme rule** and **Combined sanitary unit** are new terms; **Room type** moves to nineteen with an `_Avoid_` on growing the set for a preference; **Auxiliary space** gains what enforces it |
| `data/standards/room-constraints.json` | `bathroom_combined` ergonomic row + AZ mapping row; `bathroom`'s false note struck; `shower_room`'s programme states the pan; three `bridge` notes corrected; `areas_m2.bathroom_combined.reachable_in_v1` **reversed** |
| `experiments/region-profile/build_ergonomic_layer.py` | the nineteenth programme and its flags; **preserve-merge** and a loud failure |

**Declared on resolution, not in `writes:`** — `brief.md`, `CONTEXT.md`,
`docs/adr/`, `room-constraints.json` and `build_ergonomic_layer.py`. The first
three had no claimant. `room-constraints.json` is listed as **32's** and 32 was
unclaimed at the time; the edits are the nineteenth type and three factual
corrections, and they touch none of the annotation material 32 will write. Handing
the type to another file's holder was refused for the reason *The partition
footprint has a mean and no spread* records: a second handoff recreates the defect.

**Gates:** `gate_check.py` 229 → **238** (the mapping-totality test picked up the
new row unprompted), `ergonomic_check.py` **230**, `env_check.py` **28**,
`room-count-envelope/check.py` **16**. All pass.

### Left open

- **Bound 8 fights bounds 1, 3 and 6.** Adding the `wc` a refusal asks for raises
  Σ minima, adds an engine room, and can push a Brief out of 3–10 — so a nine-room
  Brief with no toilet is told to add a room *and* told it may not. The findings
  set surfaces both; nothing orders them. `homeowner-surface.md`'s.
- **Two limbs are partly unsatisfiable**: `taxça-mətbəx` has no Brief type,
  `divar təsərrüfat şkafı` is furniture. `brief.md` §3's.
- **`prog.storage_exists`'s 73.35 % is not clean evidence** — a Swiss flat's store
  is typically a *Keller* outside the dwelling, invisible to a dwelling-scoped
  corpus. It overstates the case against the room, which argues for `warn` from
  the opposite direction to the rejection rate.
- **`corpus_label_split` needs a third class** now `bathroom_combined` exists. The
  fixture ground truth is already in the corpus.
- **Four more messages owing the locale dimension** — 36 → 40, one schema change.
