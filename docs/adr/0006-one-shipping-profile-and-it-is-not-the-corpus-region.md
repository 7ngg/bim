# One shipping region profile, and it is not the corpus's region

*Which region profiles ship in v1* inherited a tension its own body stated: the
best-verifiable standards profile (UK, Open Government Licence) and the
best-aligned training corpus (Swiss Dwellings) are different regions. The ticket
asked which one wins.

Neither. The tension rests on an assumption nobody had examined — that the
**shipped** profile and the **verification** profile must be the same profile —
and the standards research had already said they need not be, calling UK *"a
testing decision, not a claim that UK numbers are better."*

v1 ships **exactly one** selectable region profile, and its region is **`AZ`**.
**`UK` is retained as a test fixture** and is never selectable. The corpus
conditioning tag stays **`CH`**, differs from the profile on purpose, and is
**disclosed in product copy** rather than hidden.

## The construction

- `RegionProfile` and `CorpusProvenance` are **two fields with two enums**. In v1
  they hold `AZ` and `CH`. Their disagreement is the normal case, not a defect.
- The profile governs **printed and built conventions only**: the wall-thickness
  catalogue, decimal separator, room-name abbreviations, opening catalogue keys,
  two soft area targets, one soft window fraction, and the area measurement
  convention. It governs **no hard dimensional floor** — *Acceptance validator
  spec* moved those to the region-invariant ergonomic layer.
- A Plan **carries its profile id for its whole life**. The solver and the
  validator must read the same one, because `model.thickness_in_catalogue` is hard
  and a Plan solved under one catalogue fails validation under another.
- `region_model.must_match` in `data/standards/room-constraints.json` — *"the
  region enum MUST be the same enum as the training-data conditioning variable"* —
  is **struck**.
- `DE` and `US` are **deleted** from the region enum, along with the `IN` / `JP` /
  `AU` / `CN` stubs.

## Why AZ and not UK

The decision is a **construction system**, not a country, and country is a poor
proxy for it. What makes a plan buildable is that its wall thicknesses correspond
to real units where it is built.

1. **UK's construction system exists in neither corpus nor deployment context.**
   Timber and metal stud partitions with cavity brick externals are a British and
   North American build-up. A plan dimensioned to it is buildable in Britain and
   nowhere the operator is.
2. **The post-Soviet norms are written for flats**, and flats are all v1 has.
   Every corpus on the map is apartments (*Building scope and envelope handling*),
   C5 ships flats plus houses generated from apartment priors, and the SNiP-family
   residential norm is specifically a multi-apartment instrument. UK's NDSS and
   Approved Document M address dwellings in general.
3. **Its modules are expected to satisfy ADR 0004 where DIN cannot.** The
   post-Soviet fired-brick series (120 / 250 / 380 / 510) and panel series
   (80 / 140 / 160) are believed to be entirely even; DIN 4172's octametric series
   (115 / 365 / 490) is systematically **odd** and therefore illegal here.
   **Unverified — this is the first thing *The Azerbaijani region profile* checks**,
   and if it fails, the profile absorbs the cost the same way any profile would.
4. **Free primary sources.** The SNiP/SP corpus and its national derivatives are
   published, which keeps the copyright posture of findings §7.6 intact — the
   posture that rules out building a DE profile out of Neufert at all.
5. **It is the actual deployment context**, which is what "plans ready to use"
   means. A plan is usable somewhere specific or nowhere.

## Why DE was deleted rather than deprioritised

Three independent disqualifications, any one sufficient. Its canonical internal
partition is **115 mm**, which ADR 0004 forbids, and the whole octametric series
inherits the fault. Its numbers are all `REPORTED` from documents the research
records as **not read**. Building the profile would mean transcribing Neufert's
tables into a data file, which findings §7.6 item 7 names as the specific
infringement this project would walk into by accident. It survived only as a
`default_region` label that was itself a proxy for Swiss data.

## Consequences

1. **The engine will draw Swiss-shaped layouts to Azerbaijani conventions,
   permanently.** Retrieval-and-warp reads Swiss Dwellings only; no obtainable
   corpus is Azerbaijani. This is a **disclosed limit**, the third in the family
   *Building scope and envelope handling* started: single storey; houses from
   apartment priors; **conventions are local, layouts are European**.
2. **A region profile is a data file; a region's *layouts* are not.** Adding a
   second profile is ~30 numbers. Adding a second layout region is a corpus nobody
   has. Product copy must never let the first imply the second.
3. **At inference the model is conditioned on `CH`/`swiss`**, the tokens it was
   trained with. Setting an `AZ` token that never appeared in training is
   undefined behaviour, not localisation.
4. **The shipping profile is unpopulated at the moment of this decision.** Every
   number is owed by *The Azerbaijani region profile*. This is deliberate: an
   invented catalogue is the 90%-right artefact C2 calls worse than blank.
5. **`statutory_floor` becomes non-null for the first time.** SNiP-family norms
   prescribe minimum room areas, where German law prescribes none — so the tier
   the validator carries unread acquires a real consumer, as a `warn` driven by
   each source's `force` field, never as a gate. C8 is untouched.
6. **UK stays populated and tested.** Its seven OGL sources remain in
   `room-constraints.json`; the test suite asserts the profile *mechanism* against
   them. This preserves the one property the standards research valued in UK —
   end-to-end checkability — without shipping it to a user.
