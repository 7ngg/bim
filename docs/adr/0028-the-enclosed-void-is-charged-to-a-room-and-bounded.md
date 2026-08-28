# ADR 0028 — The enclosed void is charged to a Room and bounded, and no donor is refused for having one

Status: **accepted** · 2026-08-28 ·
[A donor's enclosed void becomes area nobody asked for](../wayfinder/tickets/53-a-donors-enclosed-void-becomes-area-nobody-asked-for.md)

## Context

*Look at the converted corpus* measured that **10.0 % of converted dwellings carry
an enclosed void ≥ 0.5 m²**, and every one of them is admissible to the retrieval
index. *A dwelling with no toilet passes every check* was handed it as a gap in
the acceptance bar, checked, found the premise false — `model.no_unassigned_area`
is hard — and re-homed it here as a **proposer** question: the donor carries the
void into the index, the warp has no term for it, and the solve is then *required*
to tile exactly, so the void does not vanish. It is absorbed into whichever
bordering Room the objective finds cheapest, as floor the Brief did not ask for
and no Assumption surfaces.

The ticket offered a gate on the index and asked which Room absorbs the residue.
Seven measurements over the full 2,317-dwelling converted index
(`experiments/void/`) moved the question three times.

**The quantity that was quoted is not the one the engine meets.**
`void_census.py` measures uncovered floor against the real dwelling. The engine
never sees the real dwelling — it sees `parts[]`. Measured on the enclosed
complement of the *parts* frame, over the whole index rather than the first 400
records in file order:

| | |
|---|---|
| index carrying any enclosed void | **15.49 %** |
| ≥ 0.5 m² | **6.73 %** · ≥ 1 m² 3.15 % · max 4.56 m² |
| p50 / p90 void area | **0.00** / 0.25 m² |
| room-count gradient | 0.55 % at n = 4 → **15.79 %** at n = 10 |

**It is not a duct.** `watershed`'s 350 mm `WALL_REACH` swallows any dropped
`NOT_A_ROOM` entity narrower than ~700 mm, so the census could not have told a
riser from residue. Separated: **1.4 %** of components and **2.0 %** of the void
area lie majority-inside a dropped `SHAFT`/`VOID`/`LIGHTWELL`/`ELEVATOR`/
`STAIRCASE`/`TECHNICAL_AREA`. **98 % is our own rectangularisation residue** —
donor floor the k ≤ 2 fit could not cover.

**The warp does not carry it. It amplifies it 2.2×.** With the box derived
exactly as ADR 0020 writes it, donor void p50 0.50 m² is realised at **0.81**,
p90 1.31 → **3.19**, and it grows in 62 % of cases. The cause is one line:
`fit_warp.warp_model` minimises worst-room deviation and the weighted sum and
**nothing else**, so the void — the one region of the frame carrying no target —
is where slack goes for free. This is the same class of defect ADR 0020's
amendment records for the notch, and larger in the tail.

**And it cannot be made to vanish upstream.** The warp cannot *create* one (0 of
51 clean donors), so it is a pure donor property; but only **42.3 %** of the void
area can be closed at conversion by growing bordering parts, and a void cannot
become a Room's second part — ADR 0014's leg floor is 900 mm clear on both axes,
realisable 1 100 mm, so a legal leg is ≥ 1.5625 m² and **only 16 of 389**
components clear it. The other 96 % are precisely what `acceptance-bar.md` §9.1
calls a **niche**: *"below 900 mm it is not a leg of a room, it is a niche, and
this system does not model niches."*

**The void is the visible residue of a decision already taken.** ADR 0014 caps a
Room at two rectangles and measured the cap — 52.9 % of real rooms are one
rectangle, 77.8 % are at most two. The remaining 22.2 % is where this shows up.

**Nothing on the market faces this, and that is a finding rather than a gap in
the reading.** `floorplan-generation-stack.md`: *not one published model emits
walls with thickness*, zero across ~20 generators 2020–2026, and RPLAN and LIFULL
are already orthogonal, so the second rectangle never arrives and the hole never
appears. `competitive-landscape.md`: eleven products, every one of which stops
*"until schematic design"* or *"BIM schematic design (LOD 200+)"* and hands the
model on for someone else to detail — Finch ships *generic walls needing manual
swap*, Snaptrude tells its own users to export to Revit for documentation. **A
plan that stops at schematic has no obligation to tile**, so no vendor has to say
whose floor an unnamed pocket is. `model.no_unassigned_area` is the rule that
puts this engine past them, and it is why the question cannot be punted.

## Decision

**The enclosed void is charged to a Room and bounded in the warp, carried on the
Proposal, and no donor is refused for having one.**

### 1. No gate and no ranking term

A gate costs **11.74 %** of the index after conversion-side absorption and
**15.49 %** without it, and it is worst where the index is thinnest — 16.2 % at
eight rooms, 20.5 % at nine. *The two-notch cap is now evidenced* refused a
17.2 % thinning on that exact ground and accepted 6.65 %; this sits above the
accepted figure and reaches the refused one in the band ADR 0013 already calls
tight. A ranking term is refused for §2.2.4's standing reason: it needs a weight
against area fidelity that nobody can fit.

The stronger reason is that the void is **our** residue, not the donor's defect.
Refusing a dwelling for a hole that ADR 0014's cap put there charges the corpus
twice for a decision this engine took on its own solver cost.

### 2. The void enters the warp objective — charged, and weighted

Each enclosed component's area is a product of the two gap vectors, exactly like
a Room's, and it is **added to its receiving Room's area sum**, so that Room's
deviation is measured on what it will actually hold once the solver closes the
hole. A penalty term on the same variable keeps it from growing.

| arm | realised void p50 / p90 / max | worst-room dev p50 / p90 | INFEASIBLE |
|---|---|---|---|
| **free** — what ships | 0.688 / 3.500 / 13.125 | 0.0652 / 0.2849 | 9/90 |
| weighted only | 0.375 / 1.500 / 10.625 | 0.0686 / 0.2979 | 9/90 |
| charged only | 0.688 / 3.000 / 10.000 | 0.0999 / 0.3554 | 9/90 |
| **both — shipped** | **0.375 / 1.500 / 8.125** | 0.0959 / 0.3293 | **9/90** |

⚠️ **The deviation column does not show a regression.** `free` measures a Room's
parts and ignores the floor it is about to be handed; `charged` measures the same
warp against what the Room will hold. The gap — p50 **0.0652 → 0.0959** — is the
size of the understatement, not a cost.

Cost: one `AddMultiplicationEquality` per component, p50 one component, on 15.5 %
of candidates. **No new dependency and no new variable class** — the same call
the Room areas already use. INFEASIBLE is unchanged.

### 3. The Proposal carries the void components and their receiving Room

This passes ADR 0014's own test for a contract field and fails the one that
refused zoning.

- *Only the Proposal knows it.* The receiving Room is **not derivable** from the
  boxes: largest shared edge agrees with the donor **28.4 %** of the time and is
  ambiguous on 28.4 % of components, largest bordering Room 38.1 %, geometric
  absorption 24.1 %.
- *The solver cannot infer it.* `solver-formulation.md`'s objective is L1
  displacement of all four corners and H3 posts exact tiling soft at weight
  100 000, so every bordering Room's repair costs the same. **Which Room receives
  between 0.3 and 2.8 m² is a tie broken by nothing the Brief said**, and an
  arbitrary 1.5 m² can push a small Room through `dim.max_area`, which is hard at
  `both`.

Source B emits an empty list; its boxes need not tile, so its slack is diffuse
rather than in identified components. That is an honest limit, not a contract
asymmetry — the field's *shape* is source-independent.

### 4. The receiving Room is the donor's own, recorded at conversion

The watershed already knows: ownership purity is p50 **1.00** and ≥ 0.80 on
**72.7 %** of components. Where it is unrecorded or impure, the fallback is the
largest bordering Room.

Not the geometric absorber. "Grow whichever part fits" returns the floor to the
Room that owned it **24.1 %** of the time — the solver's arbitrary tie-break moved
one layer upstream and dressed as a fix.

### 5. Conversion-side absorption is available and deliberately not taken

Unconstrained absorption closes 42.3 % of the void area and moves floor between
Rooms in the donor record three times in four, corrupting the arrangement the
index exists to preserve. Owner-constrained absorption is faithful and rare.
Neither is worth a transform on the donor record now that the charge removes the
harm; ADR 0017 is the standing reminder about transforms whose fidelity nobody
looks at.

## Consequences

1. **`fit_rects.py` owes a fourth per-record field** — the enclosed void
   components as frame spans, each with its donor owner — alongside the cut-line
   frame, per-pair relation provenance and `frontage_reach`. One pass over the
   same records; take them together.
2. **`fit_warp.warp_model` gains the void variables**, and every warp fidelity
   figure quoted on voided candidates is superseded by the charged measurement.
   `experiments/warp/`'s next holder re-reads them; **ticket 57 already holds that
   directory** and is re-running best-of-*m*.
3. **The Proposal contract grows one field**, `voids: [(span, receiving_room)]`,
   empty on source B and on 84.5 % of source A candidates.
4. **No acceptance-bar rule is added or moved.** `model.no_unassigned_area` was
   already hard and already correct; what changes is that the Proposal stops
   handing the solver a hole with no name on it.
5. **The 2.0 % that really is a duct is charged to a Room like everything else.**
   That is wrong and it is 0.3 m² on one dwelling in fifty; v1 models no vertical
   service void, and `docs/spec/proposer.md` §8 says so rather than hiding it.
6. **`dim.max_area`'s exposure on voided candidates is now bounded** rather than
   unbounded: p90 1.50 m² charged to a named Room instead of p90 3.50 m² to an
   arbitrary one.

## Alternatives weighed and refused

- **Gate the index at 0.5 m².** 11.74 % of the index, 20.5 % at nine rooms.
  Refused on 47's precedent and on the double-charging argument above.
- **A `void_share` ranking term.** Unfittable weight against area fidelity;
  §2.2.4's standing refusal.
- **Give the void to a Room as a second part.** ADR 0014's leg floor forbids it
  for 96 % of components. It is a niche, and this system does not model niches.
- **Let the solver choose.** It cannot — the repair is an L1 tie (§3 above).
- **Weight without charging.** Bounds the void and leaves the fidelity number
  understating the receiving Room by ~50 % on voided candidates.

---

## Amendment: the void is bounded by the **Envelope**, not by the parts

Added by *The notch is two components and a quarter of donors have more*
(ticket 61). `docs/adr/0028-…` was unclaimed; this amendment is declared on that
ticket's resolution rather than taken quietly, because it widens the object the
whole ADR is about.

**The enclosure test was a proxy, and it fails at the frame border.** This ADR
identifies the void as *the enclosed complement components of the parts frame* —
components touching nothing. `notch_share` draws the complementary line: the
boundary-touching components are *the building*. Ticket 61 measured that the
second half is false. The Envelope is `bbox` minus **at most two** inscribed
notch rectangles (`fit_rects.envelope_approx(domain, max_notches=2)`,
`notches_used` never exceeds 2), while **37.6 %** of donors have three or more
complement components of at least 0.25 m². Every component past the second is
inside the ring, and *touching the bounding box border* says nothing about
whether it is inside the building — it says only that the fit's residue happened
to reach an edge.

Measured on the same 2,317 converted donors: **27.2 %** carry a third
boundary-touching component; p50 **1.25 m²**, p90 4.12, max 9.0; **89.7 %**
perfectly rectangular, **99.7 %** seated at a corner or edge distinct from the
first two, 46.4 % one 250 mm cell thin. That is not the shape of a building's
outline — it is the shape of this ADR's own §2 residue, and it has the same
cause: 98 % of the void is the k ≤ 2 fit's leftovers, and so is this.

**The decision: a void is floor inside the Envelope that no Room covers.**
Enclosure is dropped as the test. Concretely, over a candidate's frame, the void
components are every complement component **other than the `notches_used`
notch spans** — enclosed ones as before, plus the boundary-touching ones the
notch spans do not account for.

Nothing else in this ADR changes. Each component is still charged to its
receiving Room's area sum and weighted against growth (§2), still carried on the
Proposal as `voids: [(span, receiving_room)]` (§3), still owned by the donor's
own watershed record with the largest-bordering-Room fallback (§4), and **no
donor is refused for having one** (§1) — the argument there is that the void is
our residue rather than the donor's defect, and a component the notch cap
declined to model is that argument's strongest case, not its weakest.

### What it costs

**The population roughly doubles and the mechanism does not change.** Donors
carrying at least one void go from **15.49 %** to about **40 %**; p50 is still
one component. Cost is still one `AddMultiplicationEquality` per component, the
same call the Room areas already use, and *What best-of-pool is worth at
production pool depth* priced that arm at **zero** — INFEASIBLE unchanged,
0 candidates lost against `free`, void p90 0.375 → 0.250.

**Total uncovered floor inside the Envelope is p50 2.47 % of it, mean 2.93 %** —
where this ADR previously charged only the enclosed slice, p50 0.00 / p90
0.25 m². The rest of it was being paid for by an over-sized box, and ADR 0020's
second amendment removes that compensation, which is why the two must land
together: re-basing `s` without widening the void takes Σ Space from **+0,4 %**
of `target_area` to about **−1,9 %**.

### What is owed

**`fit_rects.py`'s `voids` field widens rather than gains a sibling** — the same
field, computed against the notch spans instead of against enclosure. It is
already on the frozen five-field pass; this changes what that pass computes, not
how many passes there are. **The notch spans themselves are the sixth field** on
the same pass, per ADR 0020's second amendment, and the two are one computation:
`env_at` already returns the notch rectangles and discards them, and once they
are recorded the void is *defined* as the rest.

⚠️ **Ownership purity is measured on the enclosed population only.** §4's p50
1.00, and ≥ 0.80 on 72.7 % of components, was measured on enclosed components.
The widened population is dominated by corner- and edge-seated rectangles that
border fewer Rooms, so the fallback should fire *less* rather than more — but
that is a direction, not a measurement, and the pass that emits the field is
where to check it.
