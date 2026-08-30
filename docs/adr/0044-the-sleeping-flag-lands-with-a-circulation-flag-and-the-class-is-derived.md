# ADR 0044 — The sleeping flag lands with a circulation flag, and the class is derived rather than published

- **Status**: accepted
- **Date**: 2026-08-31
- **Ticket**: [Land the sleeping flag and retire the private corpus-label copies](../wayfinder/tickets/80-land-the-sleeping-flag-and-retire-the-private-corpus-label-copies.md)
- **Amends**: ADR 0037 (its sweep reaches a fifth copy it missed), ADR 0022
  (records that `zoning.md` §5b's gate spec went stale when the nineteenth type
  landed). **Does not amend ADR 0042**, and decision 4 exists to keep it that way.
- **Supersedes nothing**

## Context

`is_sleeping` was defined in `CONTEXT.md`, specified in full in `zoning.md` §5b,
depended on by `rules.json`'s own note, and read by four of the five plan-quality
terms in `proposer.md` §6.1. It was not in the data. It had been handed over as
prose twice — ticket 30's D2, then §5b — and landed neither time; ADR 0042
consequence 2 recorded that four of five terms were uncomputable and could not
fix it.

**The ticket's own premises were wrong in four ways, and three of the four
changed the work.**

1. **The file ships six class flags over nineteen types**, not *"exactly three
   … twenty types each"*: `is_habitable`, `is_wet`, `is_private`, `needs_window`,
   `counts_as_otaq`, `brief_nameable`.
2. **`OFFICE` cannot bite.** The ticket called it *"the one that bites"* and
   asked what it maps to. Censused over the whole of `geometries.csv`: **zero
   RESIDENTIAL rooms**. Its 376 rooms / 86 apartments — the ticket's own figures,
   reproduced exactly — are 241/82 COMMERCIAL, 131/1 PUBLIC and 4/3 JANITOR, and
   `measure_zoning.load()` filters `unit_usage == "RESIDENTIAL"`. So does
   `LOBBY` (118 COMMERCIAL, 17 PUBLIC, 0 residential) and
   `CORRIDORS_AND_HALLS` (42 / 499 / 0), **both of which the private table
   mapped**. Three of its entries could never fire.
3. **`STUDIO` does exist**, against *"does not appear among the corpus's `area`
   entities at all"* — 7 RESIDENTIAL rooms in 7 apartments. None reached the
   measured 2 500, so the defect was latent, not benign, and not for the reason
   given.
4. **`zoning.md` §5b's gate spec was one type stale.** It fixes the
   `is_private` / `is_sleeping` divergence at *"exactly `bathroom`,
   `shower_room`, `wc`"*. `bathroom_combined` is `is_private: true` and is not a
   sleeping room, so the divergence is **four**. ADR 0022 added it after §5b was
   written. **A holder transcribing §5b verbatim ships a gate that fails.**

### The flags do not span the type set, and that is why a table existed

The obvious repair — derive the rig's classes from the flags with a precedence,
holding no table, ADR 0037 decision 2's pattern — **is impossible**, and the
measurement says so rather than the design taste. Over the six older flags the
nineteen types collapse into five collision classes:

| collision class | lands in |
|---|---|
| `living`, `dining`, `living_dining` | one class (social) |
| `bedroom_principal`, `bedroom_double`, `bedroom_single`, `study` | one class (sleeping) |
| `bathroom`, `bathroom_combined`, `shower_room`, `wc` | one class (wet) |
| `entrance_lobby`, `corridor` | one class (circ) |
| **`hall`, `storage`** | **circ and other — different classes** |

`hall` and `storage` are **identical** over all six flags and must be separated.
No precedence over those six does it. That single collision is the whole reason
`experiments/zoning/measure_zoning.py` carried a private corpus-label table —
the fifth copy of the projection ADR 0037 published, which its sweep missed
because ticket 69's write scope was `experiments/warp/`.

### `is_sleeping` is a conjunction today, and that is a coincidence

`is_sleeping ≡ is_habitable ∧ is_private` holds on all nineteen types. It is not
an accident of arithmetic: the conjunction picks out exactly one of the five
collision classes above. It is still a **coincidence of the current type set** —
`flag_semantics` calls these DEFINITIONS, and a library, or a home office that is
not a study, is habitable and private and not for sleeping.

## Decision

**1. Two flags land, and both are authored at the generator.**
`is_sleeping` and `is_circulation`, in `build_ergonomic_layer.py`'s `FLAGS` table
and in `AUTHORED_ROOM` — not hand-edited into the JSON, so a re-run cannot revert
them the way `kitchen.needs_window` reverted under ticket 42. `is_sleeping` takes
`zoning.md` §5b's values unchanged; `is_circulation` is true on `hall`,
`entrance_lobby`, `corridor`.

**2. `is_sleeping` is gated as an AGREEMENT, never used as a derivation.**
Gate Z5 asserts `is_sleeping == is_habitable ∧ is_private` — the mirror of V6,
which gates a *divergence*. `profile_read.is_sleeping()` reads the flag. A
consumer that derived instead would silently rezone every Plan on the day a
habitable non-sleeping private type lands; the gate makes that a decision.

**3. `is_circulation` is the minimal new bit, and Z9 is the proof it stays.**
Z9 asserts that `hall` and `storage` are identical over the six older flags *and*
that `is_circulation` is the only bit separating them, so a later ticket
"simplifying" the flag away trips a gate instead of restoring the table. It is
also **exactly** the three-name literal list in the owed rule
`entry.opens_onto_circulation`, which reads the flag rather than naming types.

**4. No `zone_class`, and the six-way class is a FUNCTION, not data.**
A published six-valued enum over the nineteen types was designed, measured
against the rig, and **refused**:

- it **restates ADR 0042 decision 3** — *"The social set is `is_habitable ∧
  ¬is_sleeping`, and no new flag is added"* — in a second place where the two can
  drift, which is the defect ADR 0024 names as *"a second place to state it"*;
- `zone_class.wet` duplicates `is_wet`;
- **there is no standard to align it to.** Read out of this repo's pinned
  `ifcopenshell 0.8.5` EXPRESS schema: `IfcSpaceTypeEnum` is `SPACE, PARKING,
  GFA, INTERNAL, EXTERNAL, USERDEFINED, NOTDEFINED`, IFC4.3 adds `BERTH` and
  nothing else in a decade, and `Pset_SpaceCommon.Reference` says outright
  *"non-classification driven"*. IFC ships a socket, not a vocabulary.
  `docs/research/room-classification-standards.md`.

`profile_read.zone_class()` is the single statement, and each limb cites what
fixes it. The rigs hold nothing.

**5. `study` is corpus-INDISTINGUISHABLE, not corpus-unreachable, and no
`OFFICE` row is added.** The corpus sleeping set is **79.5 % `ROOM`** — the
unlabelled bedroom-proportioned label — against 20.5 % `BEDROOM`. A Swiss study
is inside that 79.5 %, so the §6.1 terms *do* see studies and count them as
bedrooms. Area cannot separate them either: the set's p5 is **9.97 m²** against
`study`'s ergonomic minimum of **0.8 m²**, so **zero of 5 990 rooms** fall in a
band that could identify one. Recorded in `CONTEXT.md` beside the term.

**6. The rig's class is renamed `private` → `sleeping`, across
`experiments/zoning/`.** `CONTEXT.md` already carries the ⚠️ that *"a rule
reaching for `the bedrooms` and finding `is_private` silently acquires the
bathrooms"*; a rig calling the sleeping set `private` is that confusion in code.
`priv_components` → `sleeping_groups`, which is the name `CONTEXT.md` gives the
object.

**7. The gate count ratchets.** `GATE_FLOOR` in `gate_check.py`, asserted by the
runner. *"All N gates pass"* is true of a file with every gate deleted, and the
count was previously carried in prose — map C15, three ADRs, two tickets — where
it went **146 behind** (238 against 384) across four tickets that each moved it.
C15 keeps the rule and loses the number.

### Considered and refused

**Publish `zone_class` as data on the ergonomic type.** Refused at decision 4 —
it restates a landed ADR in a second authoring site. ⚠️ It was the recommended
option until the market check came back and the flag-collision measurement was
run; both are recorded because the *reasoning* that survives is the general one:
a projection is published (ADR 0037) when a consumer keys on it, and derived when
one already-published field determines it.

**Publish `zoning_class` on the corpus label instead.** Worse: ADR 0037 requires
a second corpus to bring its own `corpus_label_map` block, so a class parked on
the label is re-authored per corpus while the room types are the same everywhere.

**Derive `is_sleeping` and ship no flag.** Refused. Four documents name it as a
*field* — `CONTEXT.md`, `zoning.md` §5b, `rules.json`'s owed note,
`proposer.md` §6.1 — and three of them have claimants this ticket cannot edit.
Shipping only a predicate means three prose corrections, and a prose handoff that
fails is the exact failure this ticket was raised to end.

**Map `OFFICE`.** Refused at decision 5: a bridge entry for a label the
residential pipeline cannot produce is a claim nobody can check, which is the
shape of the four dead copies ADR 0037 removed.

**Adopt Uniclass `SL_45_10` as the internal leaf vocabulary.** Out of scope here
and refused as framed — the research is explicit that the leaf key stays ours and
Uniclass is a *mapping target* for export. It is raised as
[An IfcSpace carries no room use](../wayfinder/tickets/84-an-ifcspace-carries-no-room-use.md).

## Consequences

**1. Four of five §6.1 plan-quality terms become computable**, and the five owed
`zone.*` rules lose their blocker. ADR 0042 consequence 2 is discharged.

**2. `gate_check.py` 384 → 446, all pass, 10/10 mutations caught.** The mutations
were run rather than asserted: flipping `study.is_sleeping`, `bathroom.is_sleeping`,
`living.is_sleeping`, `storage.is_circulation`, `hall.is_circulation`,
`study.is_private`, `hall.is_habitable`, `bedroom_single.needs_window`, and
deleting `wc.is_sleeping` and `corridor.is_circulation` — every one caught, by
1 to 6 gates each.

**3. The re-run moved three rooms and one published figure.** The rig is
deterministic — md5-keyed ordering, no `hash()`, no solver — and the re-run
reproduces the skip counts exactly (1 206 / 126 / 144 / 144 / 6), so **ADR 0043's
reproducibility floor does not reach this rig and the delta is exact, not a
spread.** `KITCHEN_DINING` 3 rooms in 3 dwellings move `other → social`. Unmoved:
§2.1 (69.8 / 27.7 / 2.5), §2.4 / term 2 (73.7 %), §2.5 / term 3 (11.1 %,
666/5 990).

⚠️ **Moved: term 5, and it is a ceiling.** The entry-depth inversion rate goes
**17.4 % → 17.5 %** (305/1 756 → 308/1 759), with strata 12.3 → **12.5** at three
habitable rooms and 15.0 → **15.3** at five; 21.9 % at four is unmoved. The move
*loosens* ADR 0042's ceiling by a tenth of a point and its cause is three
dwellings acquiring a social Room they always had. **`proposer.md` has two
claimants (67, 81) and could not be edited**; the correction is written into
`docs/research/zoning.md` §2, which §6.1 cites for provenance, and onto the map's
conflict-table row. §2.2 and §6.5 also move — 65.4/16.1 → **65.3/16.3**, tie
51.0 → **50.9 %**.

**4. `zoning.md` §5b is corrected in place rather than handed on.** The file was
unclaimed. Its divergence set goes three → four, and it now records that one flag
was not enough.

**5. One artifact is retired from the conflict table and one bit of scope is
handed back.** `experiments/zoning/` returns to no claimant.
`data/standards/room-constraints.json` returns to one (72). ⚠️ The five `zone.*`
rules are **still owed** to `rules.json`, which has two claimants (72, 76) and
which this ticket did not open — but their blocker is gone, and
`entry.opens_onto_circulation` should now read `is_circulation` rather than
naming three types.

**6. A market check was fired and it changed two decisions and raised a ticket.**
`docs/research/room-classification-standards.md`: IFC has no room-use vocabulary
at all, Uniclass `SL_45_10` publishes 21 residential entries at our granularity,
and **SP 54.13330's «жилые комнаты» / «помещения вспомогательного использования»
partition is arithmetic rather than vocabulary** — cl. 5.2 / Table 5.1 keys
minimum apartment area to «число жилых комнат». ⚠️ This engine may already carry
that partition under another name (`counts_as_otaq`, AzDTN cl. 5.5's unit, which
diverges from `is_habitable` on exactly `kitchen_dining`); whether they are one
partition or two is ticket 84's first question.
