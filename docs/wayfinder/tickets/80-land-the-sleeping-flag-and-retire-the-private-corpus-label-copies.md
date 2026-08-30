---
id: 80
title: Land the sleeping flag and retire the private corpus-label copies
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
blocked_by: []
writes:
  - data/standards/room-constraints.json
  - experiments/zoning/
---

# Land the sleeping flag and retire the private corpus-label copies

## Question

**`is_sleeping` is defined, specified, depended on by shipped rules — and is not
in the data. It has been handed over as prose twice and landed neither time.**

`data/standards/room-constraints.json` ships exactly three class flags:
`is_private`, `is_wet`, `is_habitable`, twenty types each. There is no fourth.
Meanwhile:

- `CONTEXT.md` defines **Sleeping room** as *"a bedroom or a study, as one class:
  `is_sleeping` in …"*.
- `zoning.md` §5b specifies it in full, ready to transcribe: true on
  `bedroom_principal`, `bedroom_double`, `bedroom_single`, `study`; false on
  everything else **including every wet type**, which is the whole of D2.
- `rules.json:877` says so in its own note — *"Needs
  data/standards/room-constraints.json's is_sleeping flag"* — and five `zone.*`
  rules are written against it.
- `proposer.md` §6.1 terms **1, 2, 3 and 5** all read it. **Four of the five
  plan-quality terms are uncomputable today**, which ADR 0042 recorded and could
  not fix.

Ticket 30 (D2) handed it over. `zoning.md` D10 §5b handed it over again. Ticket 66
declined to hand it a third time and raised this instead, on the grounds that a
prose handoff which has failed twice is not a mechanism.

**What has to be done:**

1. **Land the flag**, with the values `zoning.md` §5b already fixes. Gate the
   divergence from `is_private` the way `gate_check.py` already gates
   `counts_as_otaq` against `is_habitable`: the sets differ on exactly
   `bathroom`, `shower_room`, `wc`.

2. **Sweep the surviving private copies of the corpus-label projection.** ADR 0037
   published that projection precisely because *"each of the four tables that
   carried the corpus one privately was free to disagree with the profile and with
   the others"*. **`experiments/zoning/measure_zoning.py:33-43` is a fifth copy and
   ADR 0037's sweep never reached it**, because ticket 69's write scope was
   `experiments/warp/`. Its `CLASS` dict:
   - names a `{ROOM, BEDROOM, STUDIO}` collapse in its comment and maps only
     `BEDROOM` and `ROOM` — so `STUDIO` falls to `"other"`;
   - maps neither **`OFFICE`** (376 rooms, 86 apartments) nor **`KITCHEN_DINING`**
     (44 / 42).

   ⚠️ **Harmless today and only by luck**: `STUDIO` does not appear among the
   corpus's `area` entities at all. The disagreement is latent, not benign.

3. **Decide what `OFFICE` maps to, because it is the one that bites.** The engine's
   sleeping set includes `study`; the corpus's closest label is `OFFICE` and it is
   unmapped. §6.1's *one* qualifying property is that a term be *"computable on a
   corpus dwelling and on a generated Plan by the same code"*, and that property
   does not currently hold for any term reading the sleeping set. 86 apartments is
   small; the principle is not.

**What this is not.** Not a re-opening of D2 — the flag's values are settled and
this ticket transcribes them. Not the five `zone.*` rules owed to `rules.json` at
`zoning.md` §5b: that file has two claimants (72, 76) and this ticket claims
neither. Not a corpus re-conversion.

⚠️ **`data/standards/room-constraints.json` is also claimed by *A regulator states
an aspect rule and the engine says none does*.** Per the map's concurrency rule the
two may be worked in either order but **not at once**.

## Raised by

*What the entry-depth gradient is worth as a fifth evaluation term* (2026-08-30),
ADR 0042 consequences 2 and 3.

## Resolution

**ADR 0044.** The flag lands, and so does a second one the ticket did not ask for
and the measurement required. Three of the ticket's four premises were wrong.

### What the ticket got wrong

| claim | measured |
|---|---|
| *"ships exactly three class flags … twenty types each"* | **six** flags over **nineteen** types |
| *"`OFFICE` … is the one that bites"* (376 rooms, 86 apartments) | **zero RESIDENTIAL rooms.** 241/82 COMMERCIAL + 131/1 PUBLIC + 4/3 JANITOR reproduces 376/86 exactly, and `load()` filters RESIDENTIAL. It cannot reach `cls()` |
| *"`STUDIO` does not appear among the corpus's `area` entities at all"* | **7 rooms in 7 apartments**, RESIDENTIAL. Latent, not absent |
| §5b: divergence is *"exactly `bathroom`, `shower_room`, `wc`"* | **four types.** `bathroom_combined` is `is_private: true`; ADR 0022 added it after §5b was written. Transcribing §5b verbatim ships a failing gate |

`LOBBY` (118 COMMERCIAL / 17 PUBLIC / **0** residential) and
`CORRIDORS_AND_HALLS` (42 / 499 / **0**) were also mapped by the private table
and could never fire. Three of its entries were dead.

### Item 1 — the flag lands, and it is gated as an agreement

`is_sleeping` on `zoning.md` §5b's values, authored in
`build_ergonomic_layer.py`'s `FLAGS` table and added to `AUTHORED_ROOM` — not
hand-edited into the JSON, so a re-run cannot revert it the way
`kitchen.needs_window` reverted under ticket 42.

**`is_sleeping ≡ is_habitable ∧ is_private` on all nineteen types**, and it is
gated as an **agreement** rather than used as a derivation (gate Z5, the mirror of
V6's divergence gate). It is a coincidence of the current type set, not the
meaning of the word: a library, or a home office that is not a study, is habitable
and private and not for sleeping. Deriving would silently rezone every Plan the
day such a type lands; the gate makes it a decision.

### Item 2 — the sweep, and the bit the flags could not supply

Retiring `measure_zoning.CLASS` by deriving from the flags **is impossible, and
the measurement says so.** Over the six older flags the nineteen types collapse
into five collision classes, and one of them straddles a class boundary:

| collision class | lands in |
|---|---|
| `living`, `dining`, `living_dining` | one class |
| `bedroom_principal`, `bedroom_double`, `bedroom_single`, `study` | one class |
| `bathroom`, `bathroom_combined`, `shower_room`, `wc` | one class |
| `entrance_lobby`, `corridor` | one class |
| **`hall`, `storage`** | **circ and other** |

So **`is_circulation`** ships too — the minimal new bit, and gate Z9 asserts both
that the collision exists and that this flag is the only thing resolving it, so a
later "simplification" trips a gate instead of restoring the table. It is *also*
exactly the three-name literal list in the owed rule
`entry.opens_onto_circulation`, which reads the flag rather than naming types.

`measure_zoning` now calls `profile_read.zone_class_for_label`. The rig holds no
table; the published bridge carries the `{ROOM, BEDROOM, STUDIO}` collapse, so
`STUDIO` is handled by data.

### Item 3 — `OFFICE` is refused, and `study` is indistinguishable, not unreachable

No `OFFICE` row: a bridge entry for a label the residential pipeline cannot
produce is a claim nobody can check — the shape of the four dead copies ADR 0037
removed.

The consequence the ticket was reaching for is real but different. The corpus
sleeping set is **79,5 % `ROOM`** (the unlabelled bedroom-proportioned label)
against 20,5 % `BEDROOM`, so a Swiss study is **inside** the measurement, counted
as a bedroom. Area cannot separate them: p5 is **9,97 m²** against `study`'s
ergonomic minimum of **0,8 m²** — **zero of 5 990 rooms** fall in a band that
could identify one. §6.1's qualifying property holds; what it cannot do is say how
many studies it saw. Recorded in `CONTEXT.md`.

### What the market check changed

`docs/research/room-classification-standards.md`, fired to test whether a private
six-valued `zone_class` should be invented. **It answered no, and the answer
reversed two decisions taken in this session.**

- **IFC ships a socket, not a vocabulary.** Read out of this repo's pinned
  `ifcopenshell 0.8.5` EXPRESS schema, not off a website: `IfcSpaceTypeEnum` is
  `SPACE, PARKING, GFA, INTERNAL, EXTERNAL, USERDEFINED, NOTDEFINED`; IFC4.3 adds
  `BERTH` and nothing else in a decade; `Pset_SpaceCommon.Reference` says outright
  *"non-classification driven"*.
- **A `zone_class` would restate ADR 0042 decision 3** — *"The social set is
  `is_habitable ∧ ¬is_sleeping`, and no new flag is added"* — in a second
  authoring site, and `zone_class.wet` would duplicate `is_wet`.

So the class is a **function**, `profile_read.zone_class()`, and no enum is
published. ⚠️ It raised [An IfcSpace carries no room use](84-an-ifcspace-carries-no-room-use.md):
every `IfcSpace` we emit is silent about what its room is for, against a
Destination that names valid IFC and a C2 that holds the model to Practitioner
grade.

### Evidence

- `gate_check.py` **384 → 446 gates, all pass**, and **10/10 mutations caught** —
  run, not asserted, by flipping and deleting flags one at a time.
- `ergonomic_check.py` 233 pass / 0 fail. `env_check.py` 28/28.
- **The gate count now ratchets.** `GATE_FLOOR` is asserted by the runner, because
  *"all N gates pass"* is true of a file with every gate deleted — and the count
  went **146 behind** in prose (map C15 at 238 against 384) across four tickets
  that each moved it. C15 keeps the rule and loses the number.
- **Re-run: deterministic, and the delta is exact.** md5-keyed ordering, no
  `hash()`, no solver, so **ADR 0043's reproducibility floor does not reach this
  rig**; skip counts reproduce exactly (1 206 / 126 / 144 / 144 / 6).

### What moved

Three `KITCHEN_DINING` rooms in three dwellings, `other → social`. **Unmoved:**
§2.1 sleeping groups (69,8 / 27,7 / 2,5), term 2 (73,7 %), term 3 (11,1 %,
666/5 990).

⚠️ **Moved: §6.1 term 5, and it is ADR 0042's ceiling.** Entry-depth inversion
**17,4 % → 17,5 %** (305/1 756 → 308/1 759); strata 12,3 → **12,5** at three
habitable rooms, 15,0 → **15,3** at five, 21,9 % at four unmoved. It *loosens* the
ceiling by a tenth, and the cause is three dwellings acquiring a social Room they
always had. §2.2 goes 65,4 / 16,1 → **65,3 / 16,3** and §6.5's tie 51,0 →
**50,9 %**.

**`proposer.md` has two claimants (67, 81) and was not opened.** The correction is
written into `docs/research/zoning.md` §2 — unclaimed, and the file §6.1 cites for
provenance — rather than handed on as prose, and onto the map's conflict-table
row. §5b is corrected in place: three → four, plus the note that one flag was not
enough.

### Declared on resolution

`experiments/region-profile/` (`build_ergonomic_layer.py`, `gate_check.py`,
`profile_read.py`), `CONTEXT.md`, `docs/research/zoning.md`,
`docs/research/room-classification-standards.md`, `docs/adr/0044-…` — all
unclaimed. Taken rather than handed on: ticket 83 exists because ticket 82 chose
prose for a one-line repair, and its own text is the argument — *"a one-line fix
that nobody owns is how this defect survived ticket 65's own fix of it."* A third
prose handoff of `is_sleeping` was the failure this ticket was raised to end.

### Still owed, and not this ticket's to take

The five `zone.*` rules to `rules.json` (two claimants, 72 and 76). Their blocker
is gone. ⚠️ `entry.opens_onto_circulation` should now read `is_circulation` rather
than naming `hall`, `entrance_lobby`, `corridor`.
