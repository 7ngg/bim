---
id: 80
title: Land the sleeping flag and retire the private corpus-label copies
parent: map
labels: [wayfinder:task]
status: open
assignee:
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
