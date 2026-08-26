# ADR 0022 — A dwelling owes rooms, and the Brief is where that is checked

Status: **accepted** · 2026-08-26 ·
[A dwelling with no toilet passes every check](../wayfinder/tickets/42-a-dwelling-with-no-toilet-passes.md)

## Context

Every predicate in the acceptance bar was per-Space, per-Wall, per-Opening or
per-Plan-geometry, and each had the form *if a Room of type T exists, it is at
least this big.* None asked whether T existed at all. A Brief naming a living
room, a bedroom, a kitchen and a bathroom therefore resolved, solved, passed all
36 rules and exported a valid IFC of a flat **with no toilet**.

`CONTEXT.md` already carried the class this is about — [[Auxiliary space]],
AzDTN 2.7-2's `yardımçı sahələr` — and already stated that the norm *"requires
the rooms to exist, not merely to be big enough if present."* Nothing enforced
it. cl. 5.2 is first-hand in this repo and its register,
`nəzərdə tutulmalıdır`, is **məcburi** — mandatory.

Three things had to be settled: what shape such a rule takes, where it binds, and
what severity it carries when the source is a region document and C8 forbids
compliance claims.

## Decision

**1. Four rules, one per limb of cl. 5.2, not one rule for the clause.**
`prog.kitchen_exists`, `prog.washing_exists`, `prog.wc_exists` **hard**;
`prog.storage_exists` **warn**. The `holl` limb gets no rule — `resolve` invents a
hall when the Brief names none, so it holds by construction, and a rule that
cannot fire is what retired `win.habitable_touches_exterior`.

**2. They bind the Brief and have no plan-side twin.** `scope: brief`,
`site: validator`, evaluated as `brief.md` §9.4 bound 8. The Room set is frozen
when `resolve` returns, so a plan-side composition predicate could never fail on a
Plan whose Brief passed.

**3. The satisfying set for the WC limb is `{wc, shower_room, bathroom_combined}`,
and `bathroom_combined` is a nineteenth Room type**, 1500 × 1700 = 2.5 m². A plain
`bathroom` is **not** in the set.

**4. cl. 5.10's restriction of the combined unit to one-otaq social housing is
recorded and not enforced.**

**5. `resolve` does not invent a missing room.** The asymmetry with the invented
hall is deliberate.

## Why

**The severities are corpus-measured, not asserted.** 46,800 real Swiss
dwellings, fixtures as ground truth — Swiss Dwellings carries `TOILET`,
`BATHTUB`, `SHOWER`, `KITCHEN` and `BUILT_IN_FURNITURE`, each placed inside the
room polygon containing it, so composition is *observed*:

| limb | dwellings carrying it | rejected if hard |
|---|---:|---:|
| kitchen | 94.01 % | 5.99 % |
| bath or shower | 92.67 % | 7.33 % |
| WC, anywhere | 94.81 % | 5.19 % |
| storage | 26.65 % | **73.35 %** |

A single predicate over the clause would have taken the severity of its weakest
limb and the WC would have inherited it. Storage stays reachable as a `warn` —
the Homeowner resolves it by naming a `storage` — where hard it refuses three real
dwellings in four.

**Brief-scope is forced, not chosen.** `brief.md` §9.5 forbids auto-repair, §3
makes every Brief Room required, `proposer.md` §2.2 warps a donor onto a fixed
multiset, and `model.no_unassigned_area` turns every Room into a Space. Nothing
between `resolve` and export can add or remove a Room. These are consequently the
first rules on this map with an **image and no pre-image** — ADR 0015 runs the
other way, and the asymmetry is stated rather than smoothed.

**The WC rule cost a room type because without it the rule was wrong about half
the world.** Over the eighteen types that existed, `prog.wc_exists` rejected
**48.32 %** of real dwellings — and only 5.19 points of that were dwellings with
no toilet. The other **43.13** were dwellings that *have* one, in a room that also
has a bath, which the vocabulary could not express. Three findings, not choices,
closed the gap:

- **`bathroom` never contained a WC.** `build_ergonomic_layer.py` computes
  1000 × 1700 = 1.70 m² from `bath[0] + u × bath[1]`, then asserted *"Pan and
  basin occupy the same strip as the body zone."* Bath 1.19 + pan 0.35 + basin
  0.27 = **1.81 m²**. Impossible, not tight. Struck.
- **`shower_room` always did.** Its programme is
  `max(tray 900, pan 700 + u) × (tray 900 + pan 500)` — it composes the pan. So a
  combined unit was already reachable while the AZ mapping asserted the layer
  *"carries no way to say the WC is inside."*
- **`bathroom_combined` = 1500 × 1700 = 2.5 m²**, derived: bath 1700 × 700 along
  one wall, pan 700 + basin 600 = 1300 ≤ 1700 opposite at 500 deep, one shared
  300 body aisle. It rejects **6.17 %** of 35,821 real bath+WC rooms — in family
  with the layer's ~5 % target — and the corpus's own short-side **p5 of 1477 mm**
  independently reproduces the derived 1500. Its AZ soft target, 3,8 m², was
  already sourced and sitting unused.

With the type, the WC rule costs 5.19 %: the defect, not the vocabulary.

**cl. 5.10 is a compliance target and C8 forbids reading one.** It confines the
combined unit to one-otaq state and municipal social stock — a class v1 cannot
detect. cl. 5.2 states *what rooms a home has*, which is a fact about homes that
94 % of Swiss dwellings corroborate. cl. 5.10 states *which flats may combine*,
which is a permission — and the corpus refutes it as a description of practice:
of 44,372 dwellings with a placed toilet, **67.24 % put every toilet in a room
with a bath or a shower**; only 32.76 % have a separate WC room. Declining to draw
the majority configuration in order to honour a permission we make no claim to
satisfy would have been the error.

**These are the first hard rules on this map sourced to a region document, and
C14 is not bent.** C14 binds *region profiles*: a profile may change which Plans
are preferred, never which are rejected. These rules are not in a profile. They
sit in the region-invariant set and key on region-invariant Room types; AzDTN
supplies the fact, and the corpus is the test that the fact is about homes rather
than about Azerbaijan.

**Inventing the missing room was available and is refused.** C4 fills gaps from
standards and `resolve` already invents circulation. The hall is exempt for a
reason that does not transfer: ADR 0013 needs the engine room count fixed before
any geometry exists, and no Homeowner states circulation — it is invented in
93.5 % of real dwellings. A Homeowner who omits a toilet has made a statement
about the home. Inventing one also spends a room out of C13's 3–10 gate, so a
Brief at ten rooms would be refused *because we added one*.

## Consequences

1. The bar is **40 rules**, 41 once `dim.leg_join` lands. The `both` conformance
   subset **stays at 14** — programme rules have no second implementation to agree
   with, by construction.
2. The Room type set is **nineteen**. `brief.md` §3, `CONTEXT.md`,
   `room-constraints.json` ergonomic + `profiles.AZ.rooms.mapping` all move
   together; `gate_check.py` goes 229 → **238** gates and its mapping-totality
   test picked the row up unprompted.
3. **A new failure interaction, unresolved.** Adding the `wc` a refusal asks for
   raises Σ ergonomic minima, adds an engine room, and can push a Brief out of
   3–10. A nine-room Brief with no toilet is told to add a room *and* told it may
   not. §9.4 returns the findings set whole so both appear, but nothing orders
   them. `homeowner-surface.md`'s.
4. **Two limbs remain partly unsatisfiable.** `taxça-mətbəx` has no Brief type and
   is expressed as a `kitchen`; `divar təsərrüfat şkafı` is furniture v1 does not
   model. The second is why storage is warn on two independent grounds.
5. **`prog.storage_exists`'s 73.35 % is not clean evidence.** A Swiss flat's
   storage is usually a *Keller* outside the dwelling, invisible to a
   dwelling-scoped corpus. The figure overstates the case against the room.
6. `ergonomic.corpus_label_split` splits `BATHROOM` two ways at 2.4 m² and now
   needs a third class. The fixture ground truth for it is already in the corpus.
7. Four more rule messages owing the locale dimension — the schema change grows
   from 36 rules to 40 rather than becoming a second change.
8. **`build_ergonomic_layer.py` was silently destructive and now is not.** It
   authors the arithmetic and four flags and nothing else, but three later tickets
   hand-edited the block it emits (`counts_as_otaq`, `brief_nameable`,
   `reachable_in_v1`, `counts_as_otaq_sourcing`, `corpus_medians`). A re-run
   deleted all of it without a word — the exact drift the module docstring claims
   generation prevents. Found by tripping it. It now carries forward every key it
   does not author and **fails loudly** if a room type has no `counts_as_otaq` to
   carry or supply.
