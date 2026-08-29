---
id: 74
title: A gas hob decides whether the open-plan type is buildable in AZ
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: m.farm4nov@gmail.com
blocked_by: []
writes:
  - data/standards/room-constraints.json
  - docs/spec/brief.md
---

# A gas hob decides whether the open-plan type is buildable in AZ

## Question

**`living_dining_kitchen` is one of `brief.md` §3's nineteen Room types, the AZ
profile maps it, and a mandatory Azerbaijani norm says the room it describes
cannot hold the cooking appliance the region actually fits.**

AzDTN 2.13-1 *Qaz təchizatı. Layihələndirmə normaları* cl. 8.31, read first-hand
from the PDF arxkom serves, mandatory register (`nəzərdə tutulmalıdır`):

> Yaşayış evlərində qaz pilətələrinin qoyulması nəfəslikli pəncərəsi, sorucu
> ventilyasiya kanalı və təbii işıqlandırılması olan, hündürlüyü 2,2 m-dən az
> olmayan **mətbəx otaqlarında** nəzərdə tutulmalıdır.

A gas hob **must** sit in a `mətbəx otağı`. AzDTN 2.7-3 cl. 4.7 files a
`mətbəx-yemək otağı` **inside** the word kitchen — *«mətbəx (o cümlədən
mətbəx-yemək otağı)»* — so a **kitchen-diner is compliant**. Neither norm
classifies a kitchen opened into a living room as a `mətbəx otağı`, so a
**`living_dining_kitchen` is not**, and needs an electric hob.

**MİDA hands over its apartments with a gas hob fitted.** Azerbaijan does not
carry the Moscow-style blanket prohibition on open-plan gas — it mandates the
mitigation instead (amended cl. 8.40: a 10 %-LEL detector wired to a solenoid
cut-off at every apartment's gas entry) — but the category rule in cl. 8.31 is
untouched by that.

⚠️ **The binding constraint is the room's category, not its size.** At 2,7 m
clear height cl. 8.31's 15 m³ volume rule is only 5,6 m² of floor, so it never
binds a real open-plan room. Nothing the engine can do to the *geometry* fixes
this, which is what makes it a product question rather than a dimensional one.

**Found by *The market tier has an Azerbaijani source now* (§6.5 of
`az-market-default-against-practice.md`), which recorded it as owned by nothing.**
That note's own handoff table says so in as many words: *"not currently owned by
anything on the map"*. It is the C8 failure seen from the inside — the engine
emitting a plan that cannot be built as drawn in the one region v1 ships.

## What has to be decided

1. **Whether `living_dining_kitchen` remains offerable in the `AZ` profile at
   all.** C5 says flats and houses ship through one code path; nothing says every
   Room type ships in every profile, and the profile has never refused a *type*
   before — only sized one.
2. **If it ships, what the engine says.** An Assumption on the Brief naming the
   electric hob is the cheap answer and it is not obviously the right one: C2's
   Homeowner "cannot read a dimension string", and an appliance-compliance
   footnote is further from them than that. ⚠️ This is also the first time the
   profile would carry a **fixture** consequence rather than a dimensional one,
   and `what_belongs_in_this_block` (ADR 0024) is the membership test that
   decides whether it may live in `room-constraints.json` at all.
3. **Whether `living_dining_kitchen`'s `az_area` mapping is right either way.**
   It currently points at `living_room_2plus` with `referent: part` and
   `compose_with: [kitchen_zone_in_diner]`; the profile's own note already calls
   that mapping under-targeted, and ADR 0034 set the compound targets at rung 2.
4. **Whether `kitchen_dining` inherits anything from this.** It does **not** —
   cl. 4.7 puts it inside `mətbəx`, so it is gas-compliant. Stating that
   explicitly is half the value of the ticket, because the two types are one
   letter apart in every table on this map.

## What this is not

Not a code-compliance claim — C8 forbids one, and this ticket must not turn the
profile into a gas-safety authority. The finding is that a **stated norm** and a
**shipped type** disagree; disclosing that is inside C8, certifying it is not.

Not a change to any area value: `kitchen_zone_in_diner` is ADR 0034's and the
`market_default` tier is ADR 0035's.

⚠️ **`data/standards/room-constraints.json` would be this ticket's THIRD open
claimant** (with 71 and 72). The Notes' concurrency rule applies: do not start
this while either of those is claimed.

## Raised by

*The market tier has an Azerbaijani source now* (2026-08-30), whose §6.5 read the
gas norm first-hand and found the finding unowned.

---

## Resolution (2026-08-30) — ADR 0036

**The type ships, disclosed and never enforced — and the ticket's own premise about
the evidence was wrong, which changed the answer to decision 3.**

### The evidence was misread, and the correction cuts both ways

§6.4's *"In multi-room apartments? **Never. 0 of 318**"* — repeated by this ticket
and by ADR 0034 consequence 3 — is withdrawn. Re-read from
`experiments/baku-market-areas/mida_plans_318.json`, which was in the repo when the
sentence was written: MİDA builds **5 open-plan rooms in 318 distinct geometries**
(1,57 %), and **all five sit in dwellings carrying a separate `Yataq otağı`**. They
are **one-bedroom flats with an open-plan kitchen-living room**, 34,97–40,10 m²
internal, LDK **15,14 / 15,14 / 17,37 / 17,70 / 17,74** m², p50 **17,37**.
`nrooms: 0` is MİDA's sales label, not a room count.

The claim survives only as *"zero plans holding an open-plan room **and** a separate
`Qonaq otağı`"*. So Baku practice **agrees** with cl. 8.31 in multi-otaq stock and
**departs** from it in five one-bedroom flats. Both directions are real — which is
why neither a refusal nor an enforcement fits, and why this is not a re-run of the
cl. 5.10 / `bathroom_combined` precedent, where the corpus simply contradicted the
norm.

### Decision 1 — it ships

The profile refuses no Room type. A refusal would refuse the one open-plan dwelling
the Baku state housing fund actually builds; enforcing a fuel rule is the C8 breach
outright. `reachable_in_v1: false` was refused for a second reason as well — the
flag is region-invariant, so a fact about Azerbaijani gas supply would remove the
type everywhere, including from the type list `openings.md` §5 relies on to express
open plan at all.

### Decision 2 — what the engine says, in two channels

`brief.md` **§7.1** (new) carries the Homeowner's half and names **both** ways out —
an electric hob, **or** a `kitchen_dining` instead, which cl. 4.7 makes
gas-compliant. An architect asked this in Baku gives two answers, not a footnote.
`annotation.md` **general note 9** (new, and the list's **first conditional** note)
carries the builder's half, emitted only where the Plan holds a Room of this type.
Two readers, two channels — ADR 0024's `what_belongs_in_this_block` distinction.

⚠️ **The cheap answer this ticket named was unavailable as written.** An Assumption
cannot carry it: the Assumption set is `ResolvedBrief \ StatedBrief`, *computed*
(`brief.md` §1), so a **stated** type invents nothing and reinterprets no value,
none of §6's three kinds reaches it, and §6 closes the taxonomy — *"There is no
fourth kind."* Opening a fourth was refused: it reopens a closed taxonomy and
mislabels the thing, because an Assumption is something *we* filled in. §7 already
houses prose the engine must say and cannot model, and it already holds a refusal
and a warning that are not Assumptions either.

### Decision 3 — the mapping was not merely under-targeted, it was unlicensed

**This is the part that moved a number, and the ticket expected it not to.**

ADR 0034 decision 4 grants an entailed sum for *"cells whose disjointness **the
norm's own type definition** establishes"*, naming `«ayrıca zonaları»` as the
licence — then applies it to `living_dining_kitchen`, whose own `name_az` note in
the same file reads *"A compound with no norm equivalent — AzDTN has no open-plan
type."* **The ADR states the rule and breaks it in the same decision.** Neither the
`compose_with` **nor the underlying `part` read** is licensed: nothing in the norm
entails that a room it has no word for contains a `qonaq otağı` meeting cl. 5.7.

And the unlicensed floor was refusing real rooms. **21,0** at one otaq / **22,0** at
two-plus against five observed rooms of 15,14–17,74 — **5 of 5 below**, by
3,3–5,9 m². ADR 0034's soundness rule for `part` is *"never rejects a room the law
admits"*; its consequence 1 quotes 17,37 and its consequence 2 posts 21,0 four
paragraphs later.

**`az_area` → `null`.** Both limbs withdrawn. The hard floor falls to the ergonomic
`min_area` **8,5 m²**, which all five clear with margin. `null` is a defined,
already-occupied state — `dim.statutory_min_area`'s `value_source`: *"A null
`az_area` means NO STATUTORY FLOOR, not an error; ten of nineteen keys are silent in
AZ."* This row is the eleventh.

⚠️ **C14 is not weakened.** C14 forbids a profile *lowering* a floor below the
region-free base; the base is the ergonomic minimum and this returns to it. A raise
posted on a read the licence does not grant was never a valid exercise of C14.
**First withdrawal of a profile raise on this map** — reuse the reasoning, not the
precedent.

**The soft side does not move**: ADR 0034 already barred a `part` read from the soft
tier, so the target was rung 2 before and is rung 2 now.

### Decision 4 — `kitchen_dining` inherits nothing, and now says so

A sibling `gas_note` on the `kitchen_dining` row. Its `part` limb **stays**: cl. 4.7
plus `«ayrıca zonaları»` is exactly the norm-side type definition the licence
requires. **Same licence, opposite results, and the difference is whether the norm
has a word for the room.** ADR 0034's refusal of "empty the limb" turned on
*"information the law entails"* — for `kitchen_dining` the law entails it, here it
entails nothing. The note exists because **the absence of a note is unreadable**
when two types are one letter apart.

### A third defect, found while checking the second

`absolute_area.py`'s `LIVING_FAMILY = ("LIVING_ROOM", "LIVING_DINING")` has **no
open-plan limb**, so `floors_for` returns `None` for this type — while
`dim.statutory_min_area` binds at site `both` and demanded 22,0. **ADR 0033's
invariant did not cover this type**, and no gate could see it: ADR 0034's four owed
referent gates are still unwritten, and none of the four checks the licence anyway.
Handed to **69** with a fifth gate: *every `compose_with` names the clause whose
type definition licenses it*.

### What was NOT touched, and why

- **`counts_as_otaq`** — ADR 0013's unit, and **75** writes ADR 0013. The five plans
  are a **2-otaq engine count against MİDA's 0**; handed on with the schedules.
- **`rules.json`** — claimed by **71 and 72**. Its `dim.statutory_min_area`
  `value_source` now says *"Two AZ reads are `part`"* where one remains; handed on
  as prose, exactly as 73 did for `circ.fraction_hard`.
- **The 36,5 rung-2 target**, which runs **2,1×** MİDA's 17,37. Recorded on the
  cell, not fixed: rung 2 is a corpus median (CH by construction, C14) and replacing
  it is a market-tier act owed to ADR 0035, which requires a published cost and may
  only move a cell up. n = 5 is thin.
- **`brief.md` §3's nineteen types** — the set is unchanged; §3 gains a paragraph
  naming which of the two open-plan types is gas-compliant.

### Artifacts

| file | |
|---|---|
| `docs/adr/0036-…` | **new.** Amends ADR 0034 decision 4 and consequence 2 |
| `data/standards/room-constraints.json` | `az_area` → `null` + `az_area_note`; `gas_note` rewritten; `kitchen_dining.gas_note` added; `corpus_medians` note corrected; `referent_model.counts_at_authoring` re-counted **15 → 13** entries, **12 → 11** rows, part **3 → 1** |
| `docs/spec/brief.md` | §3 paragraph; **§7.1** new |
| `docs/spec/annotation.md` | **declared on resolution** — unclaimed; general note **9**. ⚠️ 36's drafted general note is still owed on this file |
| `docs/research/az-market-default-against-practice.md` | **declared on resolution** — unclaimed; §6.4 row split and the withdrawn sentence recorded |

`gate_check.py` **238 → 235** — exactly V2's two key-exists gates plus one
fallthrough on the removed guard entries. V4 passes because it accepts *"a soft
target **or an explicit null**"*; V5 because both living cells stay reachable via
`living` and `kitchen_zone_in_diner` via `kitchen_dining`. Gate lists diffed before
and after: **no named gate lost**.
