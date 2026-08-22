# The Brief — schema and parsing contract

**Ticket:** *Brief schema and parsing contract*.
**Depends on:** ADR 0003 (Envelope), ADR 0009 (derived minima and the grid),
ADR 0010 (finished faces, `az_umumi_sahe`), `docs/spec/acceptance-bar.md`,
`docs/spec/proposer.md` §2.2 and §4.1, `data/standards/room-constraints.json`.

C4 makes this the real interface. The prompt is the front door; the Brief is the
product. Its schema is a public contract, and everything downstream — retrieval,
the trained model, the solver, the Acceptance bar, the Drawing — reads it and
nothing else about what the Homeowner wanted.

---

## 1. Two objects, not one

A `StatedBrief` is **what the prose asserted**. It is sparse: a field is present
only if the Homeowner said it. A `ResolvedBrief` is **what the engine will
build**. It is dense: every field the pipeline needs is populated.

```
resolve(StatedBrief, RegionProfile, standards) -> ResolvedBrief
```

`resolve` is a pure function. Same inputs, same output, no clock, no network, no
model. It is the only place a default is chosen, and it lives in the engine next
to `room-constraints.json`.

Three consequences, and the third decides it.

1. **The Assumption set is derived, not authored.** It is
   `ResolvedBrief \ StatedBrief`, computed. The predecessor maintained two
   parallel lists — `inferred_fields` and `assumptions` — and had to write a
   validator asserting they paired. That bug class does not exist here.
2. **Editing is re-resolution.** A Homeowner edit writes into the `StatedBrief`
   and `resolve` runs again. C7's edit-the-brief-and-regenerate is one function
   call, and provenance maintains itself (§6).
3. **The model is never asked to invent a number.** Extraction is the only
   untestable component. Every default, every arithmetic check, every regional
   value is deterministic and unit-testable with no credential. This is what
   makes §10's *no retry loop* possible.

**Identity.** `RoomId` is assigned at first resolve, stable across edits and
regenerates, never reused. `CONTEXT.md` anchors identity in the Brief; this is
where that anchor is driven.

**Market position.** ARCHITEChTURES ships the richest structured input surveyed
and has **no text prompt at all** — a program table of net areas and minimum
dimensions per room per typology. That table is a `ResolvedBrief`. Accepting one
directly is therefore not a test seam but the Practitioner-grade entry point, and
it costs nothing extra: the parse is one of two ways to populate the same object.

---

## 2. `StatedBrief`

Every field optional. Absence means the prose did not say it.

| field | type | note |
|---|---|---|
| `rooms` | `[StatedRoom]` | may be empty — see §9 |
| `target_area` | integer mm² | §8 |
| `target_area_convention` | enum | **absence is a hard error**, §9 |
| `envelope` | `StatedEnvelope` | §5 |
| `occupancy` | integer | persons, §7 |
| `access_via` | on a `StatedRoom` | §4 |
| `adjacency_wish` | `[(RoomRef, RoomRef)]` | §4 |
| `adjacency_veto` | `[(RoomRef, RoomRef)]` | §4 |
| `unrepresented` | `[span]` | §7 |

`StatedRoom`: `type` (§3), optional `label`, optional `target_area`, optional
`count`, optional `access_via`.

`count` exists so "three bedrooms" is one assertion rather than three. `resolve`
expands it into `count` distinct Rooms with distinct ids; the split across size
classes is an Assumption (§3).

---

## 3. Room vocabulary

**The Brief speaks the ergonomic layer's key set, verbatim.** All eighteen:

```
living  dining  living_dining  kitchen  kitchen_dining  living_dining_kitchen
bedroom_principal  bedroom_double  bedroom_single  study
bathroom  shower_room  wc  utility
hall  entrance_lobby  corridor  storage
```

There is no separate Homeowner enum. Reasons, in order:

- **It is how a drawing works.** A schedule keys on type and prints a name from a
  separate column. `bedroom_double` is the type; "Guest room" is the label.
- **It is already market vocabulary on both sides.** "Double bedroom" and "single
  bedroom" are ordinary estate-agent English, and `AZ` independently ships
  `bedroom_single` and `bedroom_double` from AzDTN 2.7-2 cl. 5.7.
- Every Brief-nameable type resolves to a hard floor by construction, so *Two room
  vocabularies in one file*'s closing cross-file check is satisfiable, and that
  ticket has **one** mapping to build (ergonomic → `AZ`) rather than three.

**`label` is display-only.** `nursery`, `master bedroom`, `kids' room`, `snug` are
labels on a typed Room. The tag prints the label; the schedule, the minima, the
retrieval key and the solver all read the type. A Homeowner's word is never lost
and never load-bearing.

**Open-plan is a type, not an adjacency.** "Kitchen open to the living room" is
one Room of type `living_dining_kitchen`. `proposer.md` §4.1 refuses to collapse
`LIVING_ROOM` / `LIVING_DINING` / `DINING` precisely because open-plan versus
separate is real programme a Homeowner states, and the ergonomic layer already
carries the three merged types with their own minima. A cased opening between two
*separate* Rooms is a different thing and belongs to *Opening placement rules*.

**Not every type is Brief-nameable.** `corridor` and `entrance_lobby` are
normally invented by `resolve`, because `model.no_unassigned_area` means
circulation must be Brief Rooms or the Envelope cannot be tiled. The distinction
is data: `room-constraints.json` gains a `brief_nameable` flag per ergonomic key,
and the JSON Schema generator (§10) reads it. **This spec does not write that
file** — see §12.

**Three vocabularies exist and they are ordered, not competing.**

| layer | granularity | consumer |
|---|---|---|
| Brief / ergonomic | 18 types | hard floors, the Drawing, this spec |
| Region profile | `AZ`'s own keys | soft targets, `dim.market_default_area` |
| Retrieval class | `PRIVATE` etc. | `proposer.md` §4.1, retrieval multiset only |

The retrieval class is a **lossy projection of the Brief type**, defined in
`proposer.md` §4.1 and never the other way round. Granularity here is a direct
lever on retrieval coverage — §4.1's collapse cut distinct multisets from 1,190 to
916 and roughly doubled pool sizes — which is a reason to keep the projection, not
a reason to coarsen the Brief.

**Every Brief Room is required.** There is no `required: bool`. Retrieval's gate
is exact multiset match (`proposer.md` §2.2), so an optional room makes the pool
two-valued and every coverage figure ambiguous. "A study if it fits" resolves to
*included*, and §9's pre-check answers the "if" immediately, which is a better
answer than dropping it silently after a solve. The Brief is editable; that is the
mechanism for optionality. **Known narrowing:** a real schedule of accommodation
does carry essential-versus-desirable, and v1 does not.

**`storeys` is not a field.** C5 and `model.single_storey` fix it at one. A field
whose only legal value is 1 misrepresents what the product does.

---

## 4. Relations

Three relational statements. There is no general edge list.

**`access_via: RoomId`** — settled by *Acceptance validator spec*, hard, enforced
by `circ.dependent_room_host` and read by `circ.no_private_transit`. Access-through
is programme, never inferred from geometry. Covers ensuites, walk-in wardrobes, a
utility off the kitchen.

**`adjacency_wish: [(a, b)]`** — soft. Enters the Proposal as conditioning and
the bar as one new soft rule. Soft because a Homeowner's casual "the kitchen near
the dining" must not be able to empty the gallery, and because Synaps — the
closest surveyed analogue — treats a user's adjacency sketch explicitly as *"a
soft constraint… a directional prior, not a template"*.

**`adjacency_veto: [(a, b)]`** — hard, `site: validator`. A veto the engine
accepts and ignores is worse than offering none, and vetoes are how the plan that
passes everything and still reads as generated gets killed: a WC opening off the
living room, the principal bedroom against the front door. An unsatisfiable veto
must appear in §9's diagnosis so it explains itself rather than emptying the
gallery in silence.

Promoting the veto to `site: both` is a solver question — non-contact over the
contact graph is disjunctive and costs a boolean per pair — and belongs to *The
solver has only ever seen guillotine layouts* if late-rejection rates justify it.

**Set-versus-set zoning is out of scope here.** "Bedrooms grouped, away from the
entrance" is *The Proposal cannot express zoning*. That ticket's item 2 asks
whether zones are Brief-stated; this section is the pairwise answer and does not
pre-empt the set-wise one.

---

## 5. Envelope

ADR 0003 fixed the object. This fixes what may be **stated** and the order the
rest is derived in.

Four statable facts, independently provenanced:

| fact | example prose |
|---|---|
| `dwelling_type` | "a corner flat", "a bungalow", "mid-terrace" |
| `shape` | "L-shaped" |
| `overall_dimension` | "about 9 m wide", "12 by 8" |
| `target_area` | "90 m²" |

Resolution order:

1. `dwelling_type` resolves to the ordered ring of typed edges. The presets are
   `detached`, `semi_detached`, `terrace_end`, `terrace_mid`,
   `flat_single_aspect`, `flat_corner`, `flat_dual_aspect`. A Homeowner never
   states an edge condition; they state a type, and the ring is editable per edge
   afterwards.
2. `shape` fixes the notch count, at most 2. **Notch positions are never
   statable** — a Homeowner who can place a notch can draw, and C2 says they
   cannot. Notch edge conditions default by dwelling type (`exterior` for houses,
   `party` for flats) and are always Assumptions.
3. Dimensions and area reconcile **in one direction**. A stated dimension is never
   overridden. An unstated one derives from `sum(room target areas) / efficiency`
   then a default aspect ratio; both constants are `ENGINE_CHOICE` and owned by
   *Fit the ENGINE_CHOICE acceptance thresholds to the corpora*.
4. Where both dimensions **and** an area are stated and they disagree, the
   dimensions win and `target_area` receives a `reading` assumption (§6). A tape
   measurement is evidence; a listing figure is hearsay.

Because the Envelope is the **finished inner face** (ADR 0010), a stated dimension
is already a clear dimension and needs no conversion.

---

## 6. Provenance and Assumptions

**Two provenance values, per field: `stated` and `invented`.** ADR 0003.

**An edit flips `invented` to `stated`. An acknowledgement does not.** The fork
matters: `area.invented_envelope_hard` (±5 %, hard) applies when *we* chose the
area-determining fields and have no excuse for missing; `area.given_envelope_warn`
applies when *they* chose them and we can only warn. Editing is asserting; clicking
past an assumption is not. Provenance is per field, so a partly-edited envelope
composes correctly — the area rules already key on "the area-determining fields",
not on the object.

**Assumption is a different axis from provenance, and has three kinds.**

| kind | provenance of the field | meaning |
|---|---|---|
| `invented_room` | `invented` | we added a Room the prose did not name |
| `invented_value` | `invented` | we filled a field the prose left empty |
| `reading` | **`stated`** | we interpreted a value they did give |

The predecessor made this 1:1 with provenance and therefore could not express the
third. It is not hypothetical: `target_area` is the live case. A Baku listing
quotes `ümumi sahə` per Area Qaydalar cl. 3.8, which counts an *eyvan* at
coefficient **1.0** and a balcony at 0.3, and v1 has no such element. A Homeowner
saying "about 90 m²" may be quoting a figure several percent larger than the rooms
they will get.

The engine **does not guess a balcony share back out of the number.** Inventing a
deduction from a figure the user never decomposed is fabricating data, and it
would be invisible to them. It surfaces the reading and lets them correct it:

> read as 90 m² of rooms; if that figure came from a listing it may have included
> a balcony or *eyvan*, in which case your rooms will be larger than that
> listing's

Every Assumption carries `field`, `value`, `kind`, and one sentence a
non-architect can act on. How they are presented — marker per field, summary
block, or both — is *Homeowner product surface*.

---

## 7. Occupancy, and prose the engine cannot represent

**`occupancy` splits in two, because the halves have different evidence.**

`occupancy` to bedroom count is a small, visible **`ENGINE_CHOICE`**, claiming no
authority. AzDTN conditions on room count, not occupancy (`living_room_1room_flat`
versus `living_room_2plus`); the only occupancy-conditioned rule found anywhere is
AD M's `25 + 2 × (bedspaces − 2)` and `UK` is a test fixture that is never
selectable; Swiss Dwellings carries no occupancy field at all. So it is a starting
guess, marked `invented_room`, and one edit away. Dressing it in a citation would
be the C8 breach *The Azerbaijani region profile* was nearly caught by.

Bedroom count to total area is **measured from the corpus**, which has both fields
for 63,800 dwellings. This replaces the predecessor's invented area column with a
real joint distribution. Owed by *What a room's area is allowed to be*.

Occupancy also earns a second job: a **consistency warning**. Four people and one
bedroom is a coherent request and worth flagging as a reading, not refusing.

**`unrepresented`** carries prose the parser recognised as a request and cannot
represent — "south-facing garden", "underfloor heating", "warm minimalist" — and
it is echoed back as *not used*. Telling someone what you ignored is the same
discipline as telling them what you invented.

**One carve-out is a refusal, not an ignore.** A Brief asking for an accessible
dwelling is **refused**, in the same voice as C8's no-compliance line:

> this engine does not produce accessible layouts

*Ergonomic minima and the constraint table's missing half* found that every
clearance in the entire source corpus is an accessibility figure, and deliberately
calibrated **away** from them — composed straight, they reject 36 % of real Swiss
bathrooms. So this system's floors are explicitly not accessible floors. Silently
ignoring the request is the one ignore that could hurt someone.

---

## 8. Units

**Lengths integer millimetres. Areas integer square millimetres.**

Sum of Space areas is exactly integer mm² because every Space is an
integer-millimetre rectangle, so the area gates are exact integer arithmetic with
no tolerance question — the same deletion ADR 0001 performed on the validator:

```
area.invented_envelope_hard :  20 * |sum - target|  <=  target
area.invented_envelope_soft :  50 * |sum - target|  <=  target
```

Display is m² to one decimal with a **decimal comma**, per `profiles.AZ.drawing`.
"About 90 m²" parses to `90_000_000` carrying a `reading` assumption.

---

## 9. Validity

### 9.1 What makes a Brief invalid

Three hard errors. Each rejects the **request**, not the candidates, and each
names the field whose edit resolves it.

| error | rule |
|---|---|
| `target_area_convention` absent | `area.convention_declared` |
| `target_area_convention` differs from the region profile's | `area.convention_agrees` |
| **zero rooms** | new — see below |

v1 does not convert between area conventions: the deductions that separate them
are unrepresentable in a model with no balcony and no ceiling height, so a
mismatch has no honest resolution but to ask.

**Zero rooms** is new here. Prose with no dwelling in it — a greeting, a pasted
article — yields an empty `StatedBrief` and is refused with *"we could not find a
home in that description"*. It is **never** an LLM retry (§10).

Everything else defaults. Nothing else is fatal.

### 9.2 The defaulting ladder

```
market_default  ->  corpus median  ->  absent
```

`tier_model.default_tier` is `market_default` and names this ticket:
*"A plan built to the statutory floor is legal and unliveable."* `statutory_floor`
is **read by nothing in v1** — C14 says a region profile never rejects a Plan, and
every hard floor is the region-invariant ergonomic minimum.

The second rung exists because a profile silent on a room type is the normal case,
not an error: `AZ` ships `market_default: None` for `wc`, `hall`, `kitchen_niche`
and `wardrobe_1room_entry`. The fallback is the **corpus median**, because 63,800
real dwellings are on disk and two of the medians are already measured — wc
1.85 m², bathroom 4.17 m², in `ergonomic.corpus_label_split`. Inventing a constant
where the measurement exists is not available to us.

It costs a third instance of the disclosed `CorpusProvenance` versus
`RegionProfile` mismatch, and this one is a number rather than a layout, so it is
disclosed per value: `src: swiss_dwellings_median`. Where neither rung answers,
the field stays **absent** and the Room is sized by the solver against its
ergonomic floor alone, surfaced as an Assumption saying exactly that.

### 9.3 A target area is a band, not a floor

**A `Room.target_area` is two-sided.** This is a change of kind, and it exists
because of a defect this spec found in the bar rather than a preference.

Every area predicate in `rules.json` is a lower bound or a total. `dim.min_area`
is a floor; `dim.market_default_area` is soft and prefers Spaces *at or above*
market default, so it rewards growth; `circ.fraction_hard`'s 30 % is the only
per-class upper bound and it binds circulation only. **No non-circulation Space
has a maximum area.**

The surplus is not optional. `model.no_unassigned_area` requires the union of
Spaces and Wall bodies to equal the Envelope interior **exactly**, so when the sum
of Room target areas falls short of the interior minus partitions, the difference
*must* be assigned to some Space — and the objective (L1 corner displacement plus
soft tiling) expresses no preference about which.

Worked: a **5.8 × 6.9 m WC** clears `dim.min_area` (at least 0.8 m²), clears
`dim.aspect_ratio_hard` (1.19, at most 3.0), and cannot trip
`dim.market_default_area` because `AZ` ships `wc.market_default: None`. **A 40 m²
WC passes all 38 rules.**

So the Brief contract states the band. The predicate, its anchor, its thresholds
and its enforcement site are measured and recommended by *What a room's area is
allowed to be*, and written by whoever holds `rules.json`.

### 9.4 The feasibility pre-check

Two bounds, two severities, one function — called at parse time and again when no
candidate survives, so `acceptance-bar.md` §11's requirement that the two produce
the same sentence holds by construction.

**Hard refusal below the sum of realisable ergonomic minima.** Realisable, not
published: ADR 0009 exempts the ergonomic layer from grid congruence but is
explicit that *"the exemption is not a licence to ignore the erosion —
`clear = grid*w - t_int` still governs; the solver still pays
`ceil((m + t)/grid)`."* So the floor that binds is

```
realisable(m) = grid * ceil((m + t_int) / grid) - t_int      grid = 250, t_int = 150
```

`bedroom_double` is published 1650 × 1900 = 3.1 m². Realisable it is
**1850 × 2100 = 3.9 m², 25 % higher.** Summing published minima pre-approves
Briefs the solver cannot fit — the exact failure this check exists to prevent.

**No circulation allowance term.** Circulation Rooms are Brief Rooms (§3) and
carry their own realisable minima, so the constant the inherited note assumed is
deleted rather than fitted.

**Warning at the sum of `market_default`.** Above the hard line and below this one
the Brief fits, and every room lands at the ergonomic floor rather than at what
people build. That is worth saying, and it is what stops the engine shipping a
technically valid 20 m² three-bed.

**`acceptance-bar.md` §11's worked example is not reproducible from the shipped
table.** It reads *"Three bedrooms, a bathroom and a kitchen need at least
58 m²"*; the realisable ergonomic minima give about 18 m² and `AZ`
`market_default` gives about 48 m². The sentence must quote the computed pair —
the market number as the recommendation, the ergonomic number as the hard line.
Handed on in §12; this spec does not hold that file.

### 9.5 Nothing is auto-repaired

The system never deletes a Room, shrinks a programme, or relaxes a veto to make a
Brief fit. It refuses, or it warns, and it names the field. A brief saying nine
rooms in 45 m² is a Homeowner's decision to revisit; an engine that quietly
rewrites it has invented programme.

---

## 10. The parse contract

**The BFF owns the call. The engine owns the artefacts. There is no re-prompt
loop.**

**Placement.** The Next.js BFF makes the LLM call. The engine holds no LLM
credential and makes no outbound network call, which is what keeps it a pure
function from Brief to Plans — testable, batchable, and able to become the queue
worker with no HTTP surface that *Language and runtime split* names as the honest
end state.

**Anti-drift.** The engine generates the `StatedBrief` **JSON Schema** and the
prompt's vocabulary section **from `room-constraints.json`** as a build artefact,
which the BFF embeds. The model is told exactly the enum the resolver will accept,
and the two cannot drift because there is one source. The `brief_nameable` flag
(§3) is what the generator reads to decide which types a prompt may assert.

**Model.** `claude-opus-5` via the Anthropic SDK, **structured outputs**
(`output_config.format`) rather than function calling, adaptive thinking at
`effort: "medium"`. This is the front door and a mis-parse poisons everything
downstream. Haiku 4.5 is the available cost lever and is not taken by default.

**Retries — three kinds, and only one of them exists here.**

| kind | handling |
|---|---|
| transport (429, 5xx) | SDK `max_retries`, invisible |
| schema conformance | **cannot fail** — structured outputs guarantees it |
| semantic | **never retried** — surfaced |

The predecessor re-prompted up to three times with its own output plus the
validation errors, because it had no schema guarantee and because its model was
asked to invent numbers. Neither holds here. A `StatedBrief` records only what the
prose said, so there is nothing for the model to get *semantically* wrong that a
Homeowner should not see and correct. Re-prompting until a brief looks sane is the
engine inventing programme, which §9.5 forbids.

`stop_reason: "refusal"` surfaces; it is not retried.

**Offline.** A `BriefParser` protocol with a recorded-fixture fake, plus a path
that accepts a `StatedBrief` JSON directly (§1, and the ARCHITEChTURES point).
`resolve` — where every rule in this document lives — has no LLM in it at all, so
the whole pipeline below the front door is testable with no credential.

---

## 11. `engine_view`

The `ResolvedBrief` carries one block the Homeowner **cannot** edit, because
editing it would mean editing a measurement:

| field | source |
|---|---|
| `retrieval_pool_size` | `proposer.md` §2.2's gate — a lookup, computable before any solve |
| `hard_area_floor` | §9.4 |
| `market_area_recommendation` | §9.4 |
| `room_floor[RoomId]` | the realisable ergonomic minimum per Room |

This turns "what do we tell a Homeowner whose Brief crosses the retrieval line"
from a UI question into a data question. *Homeowner product surface* and *The
room-count envelope v1 promises* read the field; neither re-implements the
computation. The engine already knows the answer at parse time; this is where it
says so.

---

## 12. What this hands to other tickets

| obligation | to |
|---|---|
| `brief_nameable` flag per ergonomic key; the ergonomic-to-`AZ` resolution rule for silent types | *Two room vocabularies in one file* — holds `room-constraints.json` |
| the `adjacency_wish` soft rule and the `adjacency_veto` hard rule | whoever next holds `rules.json` |
| `dim.max_area`: anchor, thresholds, severity, enforcement site | *What a room's area is allowed to be*, then `rules.json`'s holder |
| §11's worked example replaced by the computed pair | whoever next holds `acceptance-bar.md` |
| corpus medians for silent profile types; bedroom-count to total-area distribution | *What a room's area is allowed to be* |
| `efficiency` and default aspect ratio for a derived Envelope | *Fit the ENGINE_CHOICE acceptance thresholds to the corpora* |
| whether the band's parse-time notice is shown, and how | *Homeowner product surface* |
| whether a room count outside 4–10 is refused at parse time | *The room-count envelope v1 promises* — §9.4's check is the place to carry it |

---

## 13. Honest limits

- **No essential-versus-desirable.** Every Brief Room is required (§3). A real
  schedule of accommodation carries the distinction and v1 does not.
- **No existing-plan input.** Every Homeowner-facing product surveyed — Maket,
  Snaptrude, Synaps — accepts an image, PDF or DWG of a plan. v1 accepts prose or
  a `StatedBrief`. Ruled out of scope, not deferred.
- **No set-wise zoning.** Pairwise wishes and vetoes only (§4).
- **Occupancy to bedroom count has no authority behind it** (§7), and is marked as
  such rather than cited.
- **The band's numbers do not exist yet** (§9.3). Until they do, a Plan can pass
  all 38 rules with a room several times the size anyone would build it.
