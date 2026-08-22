# The room-count gate and the room-count promise are two numbers in two units

The engine gate binds on the **engine room count** — every Space including the
circulation `resolve` invents — at **3–10**. The product promises **1–4 otaq**,
the habitable-room count AzDTN and the Baku market use. They are deliberately
different numbers in different units, because the count the solver is limited by
is not a count a Homeowner has ever said out loud.

## Why there are two

The map has carried C13 as *"4–10 **Brief-named** rooms"* since *What the model
proposes*. No Brief names them. `brief.md` §3 makes `corridor` and
`entrance_lobby` **invented by `resolve`**, and every coverage figure on this map
was measured over corpus dwellings that include them — `CORRIDOR` is not in
`dataset-inventory.md` §1.3's exclusion list. Measured over 46,800 Swiss
dwellings (`experiments/room-count-envelope/circulation_split.py`), a dwelling
carries **k = 1** invented circulation Room in 75.1 % of cases, k = 2 in 16.7 %,
k = 0 in 6.6 %.

So "4–10 rooms" said to a Homeowner is false in their units. A Homeowner naming
ten rooms lands outside the engine band **99.8 %** of the time; naming nine,
**31.9 %**. The band was never wrong — it was never in a unit anyone could check.

And the unit a Homeowner checks in is not "rooms I would list" either. The
shipping profile is `AZ` (C12, ADR 0006), and AzDTN 2.7-2 cl. 5.7 legislates by
**otaq** — habitable rooms, bedrooms and living rooms only, no kitchen, no
bathroom, no corridor. It is how a flat is advertised in Baku, and it is already
in the shipped data: `living_room_1room_flat` (15.0 m²) and
`wardrobe_1room_entry` (2.5 m²) are two `verified` statutory floors that exist
**only** for the one-otaq case.

## Where the edges sit, and why not at round numbers

`proposer.md` §2.1 measured retrieval coverage in three bands, which hid the
shape. Per engine room count, same method, same cache
(`experiments/room-count-envelope/coverage_per_n.py`):

| engine n | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| pool = 0 | 10.8 % | **42.6 %** | 24.2 % | 17.2 % | 8.3 % | 7.9 % | 9.3 % | 9.1 % | 15.7 % | 28.5 % | **58.0 %** |

The plateau is 5–8. **n = 2 is the worst point anywhere below 11** — worse than
n = 10, which the old band included, and worse than n = 3, which it excluded.
n = 11 is where retrieval dies, and above it only source B answers; `proposer.md`
§2.1 says source B **fails quietly**, and *Validate the arrangement metric*
established there is no serving-time ground truth to catch it. So 10 is the
ceiling and it is drawn at the last measured source, not at a round number.

The floor is **3, not 4**, and the reason is the shipped profile rather than the
corpus. An engine floor of 4 makes `living_room_1room_flat` and
`wardrobe_1room_entry` permanently unreachable — two `verified` statutory numbers
with a legal citation that no Brief could ever satisfy, the same dead-data defect
ADR 0012 deleted `h_storey` for. Floor 3 takes the one-otaq case from **57.4 %**
in band to **78.2 %**, and total corpus coverage from 91.7 % to **94.1 %**.

The floor is close to non-binding by construction, and that is the intent: a
Brief that names one habitable room, a kitchen and a bathroom is already at 3
before `resolve` adds anything. What it refuses is engine 1 and 2 — a single
Space has no arrangement to project, and n = 2's 42.6 % blank rate is the worst
retrieval regime in the product's whole range.

## Three zones, not two

| zone | rule | share of corpus | behaviour |
|---|---|---:|---|
| **promised** | engine 3–10 **and** 1–4 otaq | 89.87 % | runs; the copy claims it works |
| **served, not promised** | engine 3–10, outside 1–4 otaq | 4.26 % | runs, with a warning |
| **refused** | outside engine 3–10 | 5.87 % | hard refusal at parse time, naming the count |

The middle zone is mostly 5 otaq — 75.6 % of which resolves inside the engine
band, at a 33.4 % expected retrieval blank. The engine can serve it; we decline
to *claim* it. Collapsing the two boundaries into one would force a choice
between over-refusing that zone and over-claiming it, and neither is honest.

## Considered and rejected

- **One number in one unit.** Simplest, and wrong in every direction: stated in
  engine rooms it is unintelligible; stated in otaq it does not bind the solver.
- **No ceiling — generate and let the Acceptance bar arbitrate.** The bar tests
  dimensions and topology, not whether an arrangement reads as a home, and
  `acceptance-bar.md` §11's zero-survivor diagnosis is **arithmetic over areas**.
  Past the ceiling the Homeowner would be handed an area sentence that is not the
  real reason — a wrong explanation, not merely a missing one.
- **Warn rather than refuse past the ceiling.** Rejected on C2: above engine 10
  the only source that answers is unmeasured there and fails silently, which is
  the 90 %-right artefact C2 calls worse than a blank sheet.
- **A ceiling of 24 rooms**, inherited from *Solver formulation for layout
  projection*. That case is **one dwelling in 63,800**, and its 6.25 s VALID was
  measured at 100 % exterior exposure that ADR 0003's own census says no real
  flat has (median 0.37). Demoted to headroom evidence; it is not a requirement
  and nothing may quote it as the supported ceiling.

## Consequences

- `brief.md` §9.4 grows from "two bounds, two severities" to **four bounds, three
  severities**: the two existing area bounds, plus a hard room-count refusal and
  an unpromised-band warning. That file belongs to *What the engine says when the
  Envelope is bigger than the programme*.
- `room-constraints.json` needs a **`habitable` flag** per ergonomic key so otaq
  is computable from a Brief — the same shape as the existing `brief_nameable`
  flag. That file belongs to *Two room vocabularies in one file*.
- **`resolve` must choose k before the solver runs**, and the corpus says the
  right k is 1 in 75.1 % of dwellings and 2 in 16.7 %. Fixing k = 1 is safe only
  if a Room may be more than one rectangle — an L-shaped corridor reaching a wing
  a single rectangle cannot. That is *Whether a Room may be more than one
  rectangle*, and this is a dependency nobody had drawn.
- The market states no room-count limit at all. Across eleven products in
  `docs/research/competitive-landscape.md` the only scope limits published are
  building-type (ARCHITEChTURES: multi-family only) and experimental-feature
  disclaimers (Autodesk Forma's Building Layout Explorer: *"some outputs will be
  more useful than others"*). Stating a band is the same kind of differentiator
  as C3's annotation gap — nobody else does it, and the reason nobody does is
  that they never refuse.
