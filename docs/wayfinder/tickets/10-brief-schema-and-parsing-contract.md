---
id: 10
title: Brief schema and parsing contract
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: [5, 9, 17]
writes:
  - docs/spec/brief.md (new)
  - CONTEXT.md
---

# Brief schema and parsing contract

## Question

What is the **structured brief** — the object a prompt is parsed into, and the
thing the rest of the system actually consumes?

C4 makes this the real interface: the prompt is the front door, the brief is the
product, and it stays editable. So its schema is a public contract, not an
implementation detail.

Decide:

1. **Fields.** Room list with types and target areas; total area; envelope (from
   *Building scope and envelope handling*); adjacency wishes; orientation and
   aspect preferences; occupancy ("a family of four"); style or lifestyle notes
   that have no geometric meaning — are those captured or discarded?
2. **How adjacency is expressed by a Homeowner.** "Kitchen open to living" is a
   prompt phrase; what does it become? Required adjacency, shared opening, or a
   merged space? Forbidden adjacencies matter too and nobody thinks to state them.
3. **Defaults.** Every unstated field is filled from the constraint table produced
   by *Dimensional standards corpus*. Which fields are defaultable and which make
   the brief invalid if absent?
4. **Assumption surfacing.** C4 requires that every invented value is visible.
   What does the user see — a marker per field, a summary block, both? An invented
   *room* and an invented *area* are different in kind; does the interface
   distinguish them?
5. **Validation and repair of the brief itself.** A brief can be internally
   impossible before any geometry exists — nine rooms in 45 m², a bedroom count
   that contradicts the occupancy. What is checked, and does the system correct,
   reject, or ask?
6. **Which LLM, and what contract.** Structured output, function calling, or
   constrained decoding? What happens on a malformed response — retry with the
   model's own output, or fail? What is the offline story so the pipeline is
   testable without credentials or tokens?

The sibling project built exactly this and has 235 offline tests behind it. Per
C11 nothing is inherited — but its `parser/` and `schema/` are worth reading as a
source of *questions already discovered*, then answering them independently.

Deliverable: the schema, the defaulting rules, and the parse contract, with the
vocabulary landed in `CONTEXT.md`.

---

## Inherited from *Acceptance validator spec*, now closed — do not re-derive

- **The Brief needs `access_via: RoomId` on a Room.** C6 item 1 rejects every plan
  with an ensuite without it: `is_private` is true on bedrooms *and* bathrooms, and
  an ensuite is reachable only through a bedroom. Access-through is **program, not
  geometry**, so it is declared here and never inferred from the plan. Not optional
  decoration — `circ.no_private_transit` and `circ.dependent_room_host` both read
  it, and the second requires a dependent Room to have exactly one passable
  Opening, to its declared host. Covers ensuites, walk-in wardrobes, and a utility
  off the kitchen. A new field neither this ticket nor the standards ticket asked
  for.
- **`area_convention` is a hard *Brief* error when absent**, not a warning. Two of
  the 37 acceptance rules are `scope: brief` — they reject the request, not the
  candidates — and this is one. The same building differs by 20–30% between
  Wohnfläche and GIA.
- **Defaults come from `market_default`, and the hard floor is `ergonomic_min`,
  not `statutory_floor`.** That tier is `null` in the default region and is
  **unread in v1**. Do not default any field from it.
- **The entry Room and the front-door position are Assumptions, not required
  fields.** The engine defaults and surfaces them; `entry.single_primary` requires
  exactly one primary entrance door but does not require the Brief to say where.
- **Item 5's "internally impossible brief" now has a cheap check.** The sum of
  ergonomic minima for the Brief's rooms plus a circulation allowance is a lower
  bound on feasible GIA — arithmetic, no search. It is also exactly the diagnosis
  the Homeowner sees when no candidate survives, so the two must produce the same
  sentence.

---

## Inherited from *Building scope and envelope handling*, now closed — do not re-derive

- **The Envelope is the inner face of the external wall**, so a stated dimension is
  a **clear** dimension and needs no conversion. Its fields: a rectilinear shape
  (bbox minus at most 2 notches, spanning rect/L/U/T), an **ordered ring of edges**
  each carrying `condition` in `{exterior, party}` plus a boolean `entrance_side`,
  and a north angle used only for the Drawing's north arrow and as a soft
  preference. See ADR 0003.
- **Provenance is per-field, `stated` or `invented`** — the existing **Assumption**
  concept applied to the Envelope. Not one flag on the object, because "a corner
  flat, about 9 m wide" states an exposure and one dimension and invents the rest.
  This replaces *Acceptance validator spec*'s given-flat / invented-house wording:
  the area rule keys on whether the **area-determining fields** were stated.
- **A Homeowner never states edge conditions directly. They state a dwelling type**,
  which is a preset resolving to a ring — `detached`, `semi_detached`,
  `terrace_end`, `terrace_mid`, `flat_single_aspect`, `flat_corner`,
  `flat_dual_aspect`. Parsed from prose, surfaced as an Assumption, editable per
  edge. The preset table belongs in this ticket's schema; the ring topology is
  region-invariant and only its label is regional.
- **Notch edges default by dwelling type** — `exterior` for houses, `party` for
  flats — and are always Assumptions.
- **Unstated area is derived**: `sum(room target areas) / efficiency`, then a
  default aspect ratio for the rectangle. Both constants are `ENGINE_CHOICE`, owned
  by *Fit the ENGINE_CHOICE acceptance thresholds to the corpora*.
- **Item 5's feasibility pre-check gains a second form.** With a stated Envelope
  the ergonomic-minima lower bound is compared against **a real area**, not just a
  room-sum — so "six bedrooms in 9 by 7 m" is refused at parse time rather than
  after zero candidates survive. Same sentence, earlier.

## Inherited from *Area measurement convention* — the blocker is discharged, and it lands two fields

`blocked_by: [17]` is discharged. ADR 0010 settles what an area *is*; what remains
here is what the Brief carries and what the Homeowner is told.

**Two fields, not one.**

- `Brief.target_area_convention` — the convention the Homeowner's number is in.
  Separate from `Plan.area_convention`, which is **derived from the region
  profile**, held once per Plan, and never per Space. The two are allowed to
  disagree, and a disagreement is a **hard Brief error**: `area.convention_agrees`
  in `rules.json`. v1 does not convert between conventions, because the deductions
  that separate them are unrepresentable in a model with no balcony and no ceiling
  height, so a mismatch has no honest resolution but to ask.
- `Brief.target_area` — defined as **interior `ümumi sahə`, with balcony, loggia,
  terrace and *eyvan* excluded.**

**The default is the interesting part, and it is an Assumption in C4's exact
sense.** A Baku property listing quotes `ümumi sahə` per Area Qaydalar cl. 3.8,
which **includes** an *eyvan* at coefficient **1.0 — full area, not reduced** —
and a balcony at 0.3, a loggia at 0.5. v1 has no such element. So a Homeowner
saying *"about 90 m²"* from their listing is quoting a number that may be several
percent larger than the rooms they will actually get.

The engine **does not guess a balcony share back out of the number.** Inventing a
deduction from a figure the user did not decompose is fabricating data, and it
would be invisible to them. It surfaces the reading instead — *"read as 90 m² of
rooms; if that figure came from a listing it may have included a balcony or
eyvan, in which case your rooms will be larger than that listing's"* — and lets
them correct it. That is an Assumption on `target_area`, surfaced like any other.

**The retrieval-line question this sharpens.** *What a corpus-shaped product looks
like* asks what a Homeowner is told when their Brief crosses a line the engine can
see at parse time. This is a second instance of the same shape and the same
answer: the engine knows the convention gap exists, cannot resolve it, and says
so.

**One consequence for the total-area gate**, which this ticket's feasibility
pre-check should know: the gate now measures **Σ Space area**, not GIA, so
`target_area` is compared against the sum of rooms rather than the Envelope
interior. The two differ by the partition footprint — roughly **4–5%** on a 90 m²
dwelling. Item 5's pre-check must sum against the same quantity or it will
pre-approve Briefs the bar then rejects.

---

## Resolution

**The Brief is two objects, the parser is the only untestable component, and the
biggest finding was not in this ticket's scope.**

Spec: `docs/spec/brief.md`. Vocabulary landed in `CONTEXT.md`.

### The shape

**`StatedBrief` and `ResolvedBrief`, joined by a pure `resolve`.** The stated one
is sparse — present only where the prose asserted something. The resolved one is
dense. Three consequences and the third decides it: the Assumption set becomes
*derived* rather than a second list to keep in step (the predecessor had to write
a validator asserting `inferred_fields` and `assumptions` paired); a Homeowner
edit is a write to the stated layer plus a re-resolve, so C7 is one function call;
and **the model is never asked to invent a number**, which shrinks the untestable
surface from "the whole Brief" to extraction alone.

Corroborated by the market rather than reasoned alone: **ARCHITEChTURES ships the
richest structured input surveyed and has no text prompt at all** — a program
table of net areas and minimum dimensions per room per typology. That table *is* a
`ResolvedBrief`, so accepting one directly is the Practitioner entry point, not a
test seam, and the parse becomes one of two ways to fill the same object.

### The vocabulary

**The Brief speaks the ergonomic layer's 18 keys verbatim**, with a display-only
`label`. Not a fourth taxonomy: `nursery`, `master bedroom`, `kids' room` are
labels on a typed Room, which is how a drawing schedule already works. Every
Brief-nameable type therefore resolves to a hard floor by construction, and *Two
room vocabularies in one file* is left with **one** mapping to build rather than
three. Its fourth bullet — "the Brief's is the one a Homeowner actually speaks" —
is answered: it is the ergonomic set, because "double bedroom" is ordinary market
English and `AZ` independently ships `bedroom_single` / `bedroom_double`.

**Open-plan is a room type, not an adjacency.** `proposer.md` §4.1 refuses to
collapse `LIVING_ROOM` / `LIVING_DINING` / `DINING`, and the ergonomic layer
already carries all three merged types with their own minima — so "kitchen open to
the living room" is one `living_dining_kitchen`, and item 2's headline example
never becomes an edge at all.

**Every Brief Room is required.** No `required: bool`: retrieval's gate is exact
multiset match, so an optional room makes the pool two-valued and every coverage
figure ambiguous. Recorded as a **known narrowing** — a real schedule of
accommodation does carry essential-versus-desirable.

**`storeys` is deleted.** A field whose only legal value is 1 misrepresents the
product.

### Relations — three, no general edge list

`access_via` (settled, hard), `adjacency_wish` (**soft**), `adjacency_veto`
(**hard**). Neither of the last two has any predicate in `rules.json` today, which
is the gap: a Brief that can state a relation nothing enforces is the silent-ignore
failure C4 exists to kill. Synaps — the closest surveyed analogue — treats a user's
adjacency sketch explicitly as *"a soft constraint… a directional prior, not a
template"*, which is independent support for the wish/veto asymmetry. Set-versus-set
zoning is untouched and stays with *The Proposal cannot express zoning*.

### ⚠️ The finding that matters most, and it is a defect in the Acceptance bar

**A 40 m² WC passes all 38 rules.** Every area predicate is a lower bound or a
total: `dim.min_area` is a floor, `dim.market_default_area` is soft and prefers
Spaces *at or above* market default so it rewards growth, and `circ.fraction_hard`
is the only per-class upper bound and binds circulation only. **No
non-circulation Space has a maximum area.**

The surplus is not optional. `model.no_unassigned_area` requires the union of
Spaces and Wall bodies to equal the Envelope interior *exactly*, so when Σ Room
target areas falls short of the interior minus partitions the difference **must**
be assigned to some Space, and the objective — L1 corner displacement plus soft
tiling — expresses no preference about which. It lands wherever displacement is
cheapest.

Worked: a **5.8 × 6.9 m WC** clears `dim.min_area` (≥ 0.8 m²), clears
`dim.aspect_ratio_hard` (1.19 ≤ 3.0), and cannot even trip
`dim.market_default_area` because `AZ` ships `wc.market_default: None`.

This is a reported production failure of the predecessor — *"some rooms got too
small, others too big, sometimes the WC got to 40 m²"* — still present in the
successor's spec. The Brief-contract half is settled here: **a Room's target area
is a band, not a floor.** The measurement, anchor and thresholds are a new
research ticket, *What a room's area is allowed to be*.

### ⚠️ The pre-check must sum realisable minima, not published ones

ADR 0009 exempts the ergonomic layer from grid congruence but is explicit that the
exemption *"is not a licence to ignore the erosion"* — `clear = grid·w − t_int`
still governs and the solver still pays `⌈(m + t)/grid⌉`. So the binding floor is
`realisable(m) = grid·⌈(m + t_int)/grid⌉ − t_int`.

`bedroom_double` is published 1650 × 1900 = 3.1 m²; **realisable it is
1850 × 2100 = 3.9 m², 25 % higher.** Summing published minima pre-approves Briefs
the solver cannot fit — exactly the failure the inherited note warned about, with
the mechanism now named.

Two consequences. The **circulation allowance term is deleted rather than fitted**:
circulation Rooms are Brief Rooms, so they carry their own realisable minima and
there is no percentage to invent. And **`acceptance-bar.md` §11's worked example is
not reproducible from the shipped table** — it says three bedrooms, a bathroom and
a kitchen need at least 58 m², where realisable ergonomic minima give ≈ 18 m² and
`AZ` `market_default` gives ≈ 48 m². The pre-check therefore returns **two bounds,
two severities, one function**: hard refusal at the realisable-ergonomic sum,
warning at the market-default sum, and the Homeowner sentence quotes the pair.

### Defaults

`market_default` → **corpus median** → absent. The middle rung exists because a
profile silent on a room type is the normal case, not an error — `AZ` ships
`market_default: None` for `wc`, `hall`, `kitchen_niche` and
`wardrobe_1room_entry`. The fallback is measured, not invented: 63,800 real
dwellings are on disk and two medians are already computed (wc 1.85 m², bathroom
4.17 m², in `ergonomic.corpus_label_split`). Cost: a **third instance of the
disclosed `CorpusProvenance ≠ RegionProfile` mismatch**, and this one is a number
rather than a layout, so it is disclosed per value.

**`statutory_floor` stays unread in v1** — but note the inherited instruction that
justified it (*"that tier is null in the default region"*) is **stale**: `AZ`'s
statutory floors are populated and `verified`. The conclusion survives on C14
instead — a region profile never rejects a Plan. Checked and harmless:
`market_default ≥ statutory_floor` on every AZ row that has both.

**Occupancy splits, because its halves have different evidence.** `occupancy →
bedroom count` is a bare `ENGINE_CHOICE` claiming no authority: AzDTN conditions on
room count not occupancy, the only occupancy-conditioned rule found anywhere is AD
M's `25 + 2 × (bedspaces − 2)` and `UK` is never selectable, and Swiss Dwellings
has no occupancy field. `bedroom count → total area` is **measured** — the corpus
has both fields for 63,800 dwellings, replacing the predecessor's invented area
column. Occupancy gains a second job: a consistency warning.

### Assumption is not the same axis as provenance

Three kinds — `invented_room`, `invented_value`, and **`reading`**, which attaches
to a **stated** field. The predecessor made it 1:1 with provenance and so could not
express the live case: `target_area` from a Baku listing is stated, and still needs
an assumption, because `ümumi sahə` counts an *eyvan* at coefficient 1.0. The
engine does not guess a balcony share back out of the number; it surfaces the
reading. Provenance stays two-valued, and **an edit flips `invented` → `stated`
while an acknowledgement does not** — which is what decides whether
`area.invented_envelope_hard` or `area.given_envelope_warn` fires.

### Parse contract — and there is no retry loop

**BFF owns the call; the engine owns the artefacts.** The engine holds no LLM
credential and makes no outbound call, which is what keeps it the pure function
that can become the queue worker with no HTTP surface. The engine **generates the
`StatedBrief` JSON Schema and the prompt's vocabulary section from
`room-constraints.json`** as a build artefact the BFF embeds, so prompt and
resolver cannot drift.

`claude-opus-5`, **structured outputs** (`output_config.format`), adaptive thinking
at `effort: "medium"`. Three retry kinds and only one exists: transport (SDK),
schema (**cannot fail** — structured outputs guarantees it), semantic (**never
retried**). The predecessor re-prompted three times because it had no schema
guarantee *and* asked its model to invent numbers; neither holds once the model
emits only what the prose said. Re-prompting until a brief looks sane is the engine
inventing programme.

**Offline:** a `BriefParser` protocol with recorded fixtures, plus direct
`StatedBrief` JSON entry. `resolve` — where every rule lives — has no LLM in it,
so everything below the front door tests with no credential.

### `engine_view`

The one block a Homeowner cannot edit, because editing it would be editing a
measurement: `retrieval_pool_size` (the gate is a lookup, so it is known at parse
time), the two feasibility bounds, and the realisable floor per Room. This makes
"what do we tell someone whose Brief crosses the retrieval line" a data question
rather than a UI one — *Homeowner product surface* and *The room-count envelope v1
promises* read a field instead of re-implementing the computation.

### Also settled

- **Accessibility is refused, not ignored.** *Ergonomic minima* calibrated
  deliberately **away** from accessibility figures — composed straight they reject
  36 % of real Swiss bathrooms — so this system's floors are explicitly not
  accessible floors. Of everything in `unrepresented`, this is the one silent
  ignore that could hurt someone.
- **Envelope statement forms**: four statable facts (`dwelling_type`, `shape`,
  `overall_dimension`, `target_area`), fixed resolution order, **notch positions
  never statable**, and where dimensions and area disagree the **dimensions win**
  with a `reading` on the area — a tape measurement is evidence, a listing figure
  is hearsay.
- **Units**: integer mm, integer mm². The area gates become exact integer
  arithmetic — `20·|Σ − target| ≤ target` — the same deletion ADR 0001 performed on
  the validator.
- **Nothing is auto-repaired.** Zero rooms is a new hard Brief error; nine rooms in
  45 m² is refused, never silently trimmed.

### Obligations handed on

| obligation | to |
|---|---|
| `brief_nameable` flag per ergonomic key; resolution rule for profile-silent types | *Two room vocabularies in one file* |
| `adjacency_wish` soft rule, `adjacency_veto` hard rule | whoever next holds `rules.json` |
| `dim.max_area` — anchor, thresholds, severity, site | *What a room's area is allowed to be*, then `rules.json`'s holder |
| §11's worked example replaced by the computed pair | whoever next holds `acceptance-bar.md` |
| corpus medians for silent types; bedroom-count → total-area | *What a room's area is allowed to be* |
| `efficiency`, default aspect ratio | *Fit the ENGINE_CHOICE acceptance thresholds to the corpora* |
| whether a room count outside 4–10 refuses at parse time | *The room-count envelope v1 promises* |

### New technology, acknowledged rather than assumed

The Anthropic SDK in the Next.js BFF — the repo's first LLM dependency and first
browser-tier credential — and a build step that generates the JSON Schema from
`room-constraints.json`. No refactor: there is no code yet, and the only shared
artefact this touched besides its own spec is `CONTEXT.md`.
