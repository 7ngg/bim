---
id: 53
title: A donor's enclosed void becomes area nobody asked for
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
writes:
  - docs/spec/proposer.md
---

# A donor's enclosed void becomes area nobody asked for

## Question

**10.0 % of converted dwellings carry an enclosed void ≥ 0.5 m²**, and every one
of them is admissible to the retrieval index. `void_census.py`, over 400 converted
dwellings, separating the Envelope's deliberate notch under-cut from real dwelling
floor: enclosed-by-Spaces unclaimed floor is p50 0.00 m², p90 **0.44 m²**, max
3.69 m² — **15.0 % of dwellings ≥ 0.25 m², 10.0 % ≥ 0.5 m², 4.8 % ≥ 1 m².**

⚠️ **Do not reach for `uncovered` in a fit record.** It sums the correct case
(Envelope over-reach) and the incorrect one together, which is exactly why nobody
had noticed. `void_census.py` splits them.

**This is not the acceptance bar's, and that was checked rather than assumed.**
*A dwelling with no toilet passes every check* was handed this as *"nothing in the
bar forbids floor that belongs to nothing"* and found the premise **false**:
`model.no_unassigned_area` is **hard**, `site: both`, `scope: plan` — *"The union
of all Space polygons and all Wall bodies equals the Envelope interior exactly"* —
and its own note says exact tiling is posted soft in the solver *for search speed*
and checked hard at the validator, *"the place where a 29× faster search is
prevented from shipping a hole."* An OPTIMAL candidate with a 1 m² unnamed hole
cannot be shown. No rule is owed.

**What survives is the proposer's.** The 10.0 % measured the *conversion*, so the
donor carries the void into the index; the warp has no term for it; and the solve
is then **required** to tile exactly. The void does not vanish — it is absorbed
into whichever bordering Room the objective finds cheapest, as floor the Brief did
not ask for and no Assumption surfaces.

Settle:

- **Does an enclosed void disqualify a donor from the index, or is it warped?**
  A threshold picked by eye is worse than none; the distribution above is the
  input. Note the interaction with `proposer.md` §2.2's exact-multiset gate —
  thinning the index at 0.5 m² costs coverage that ADR 0013 already measures as
  tight above nine rooms.
- **Which Room absorbs it, and is that a ranking term or a constraint?** Today it
  is neither: it falls out of the objective. A 3.69 m² void landing on a `wc` is a
  different plan from one landing on a `living`.
- **Does it reach the fidelity numbers?** ADR 0018's worst-room deviation is a
  **proportion** result — `fit_warp.py:373-384` normalises absolute area away — so
  a donor whose void is redistributed may score well on a metric that cannot see
  it. That measurement is `experiments/warp/`'s and the two should be read
  together.
- **Is a void ever *real*?** A duct, a chimney, a party recess. The conversion
  drops `SHAFT` and `VOID` as `NOT_A_ROOM` before fitting, so what remains is
  residue — but nobody has looked at one rendered. `render_sheet.py` exists.

The closing check: **a stated `target_area` and the Σ Space area of a plan built
from a voided donor agree for a reason**, not by the 5 % gate absorbing it.

## Concurrency

`docs/spec/proposer.md` is also claimed by *A third of real kitchens have no
window and the engine may not draw one*. Per the map's Notes this is a merge
hazard, not a dependency — do not run the two at once.

## Raised by

*Look at the converted corpus* measured it; *A dwelling with no toilet passes
every check* (2026-08-26) established it is not the bar's and re-homed it here.

---

## Resolution

**The enclosed void is charged to a Room and bounded in the warp, carried on the
Proposal, and no donor is refused for having one.** ADR
[0028](../../adr/0028-the-enclosed-void-is-charged-to-a-room-and-bounded.md);
`docs/spec/proposer.md` §2.2.8, with §1, §2.2.1, §2.2.2, §2.2.3, §2.2.4, §7 and
§8 amended. Seven probes in a new `experiments/void/`, which imports
`rectangularise/` and `warp/` and edits neither.

### The ticket's own numbers were the wrong quantity, measured on the wrong sample

`void_census.py` measures uncovered floor against the **real dwelling**. The
engine never sees the real dwelling — it sees `parts[]` — so the quantity that
decides anything is the enclosed complement of the **parts frame**. That split
already existed and was already committed: `warp/absolute_area.py:notch_share`
returns the boundary-touching share (ADR 0020's `s`) and the enclosed share
separately, and its docstring says why — *"`uncovered` in a fit record sums the
two together and that is why nobody had noticed."*

Over the whole index rather than the first 400 records in file order:

| | ticket | measured |
|---|---|---|
| ≥ 0.25 m² | 15.0 % | **10.01 %** |
| ≥ 0.5 m² | 10.0 % | **6.73 %** |
| ≥ 1 m² | 4.8 % | **3.15 %** |
| any void | — | 15.49 %, p50 **0.00 m²**, p90 0.25, max 4.56 |

The cause is a strong room-count gradient — **0.55 %** at four rooms to **15.79 %**
at ten — so a sample in file order over-states by about half.

### It is our residue, and ADR 0014 already said what it is

**Not a duct: 1.4 % of components and 2.0 % of the void area.** Worth checking
rather than assuming, because `watershed`'s 350 mm `WALL_REACH` swallows any
dropped `NOT_A_ROOM` entity narrower than ~700 mm, so the census could not have
told a riser from residue. 98 % is what the k ≤ 2 fit could not cover.

**And it cannot become a Room's part.** `acceptance-bar.md` §9.1's leg floor is
900 mm clear on both axes, realisable 1 100 mm, so a legal leg is ≥ 1.5625 m² —
**16 of 389** components clear it. The other 96 % are exactly what that section
calls a niche: *"below 900 mm it is not a leg of a room, it is a niche, and this
system does not model niches."* The void is the visible residue of ADR 0014's cap,
which was measured and accepted: 77.8 % of real rooms are at most two rectangles,
and this is where the other 22.2 % shows up.

### The four questions

**Does an enclosed void disqualify a donor? No — no gate and no rank term.**
A gate costs **11.74 %** of the index after conversion-side absorption and
**15.49 %** without, worst where the index is thinnest: 16.2 % at eight rooms,
20.5 % at nine, against 4–6 rooms' 3.1 %. Thinning factor in the 7–10 band is
**0.794** at any-void and 0.904 at > 0.5 m², and **22.4 %** of the sample's
singleton buckets are emptied. *The two-notch cap is now evidenced* accepted a
6.65 % thinning and refused a 17.2 % one; this reaches the refused figure in the
band ADR 0013 already calls tight. A rank term is refused on §2.2.4's standing
ground — a weight against area fidelity nobody can fit.

The stronger reason: refusing a dwelling for a hole **our own cap** put there
charges the corpus twice for a decision this engine took on its own solver cost.

⚠️ **47's IoU gate does not already cover it.** worst-room IoU is p50 0.770 with
no void and 0.640 above 1 m²; of the 156 donors above 0.5 m², only **10.9 %** fall
under the hard 0.30, against 6.65 % index-wide. Nearly orthogonal — which is why
the void needed its own field rather than riding on that one.

**Which Room absorbs it, and is that a ranking term or a constraint? Neither —
it is a Proposal field, and the warp pre-pays for it.**

The premise had to be re-checked first, and it inverted. The warp does not
*carry* the void, it **amplifies it 2.2×**: donor p50 0.50 → 0.81 m², p90 1.31 →
3.19, growing in 62 % of cases and shrinking in 29 %. One line explains it —
`fit_warp.warp_model:146` minimises worst-room deviation and the weighted sum and
nothing else, so the void, the one region of the frame carrying no target, is
where slack goes **for free**. Same class of defect as the notch float ticket 56
found, and larger in the tail.

| arm | realised void p50 / p90 / max | worst-room dev p50 / p90 | INFEASIBLE |
|---|---|---|---|
| free — what ships | 0.688 / 3.500 / 13.125 | 0.0652 / 0.2849 | 9/90 |
| weighted only | 0.375 / 1.500 / 10.625 | 0.0686 / 0.2979 | 9/90 |
| charged only | 0.688 / 3.000 / 10.000 | 0.0999 / 0.3554 | 9/90 |
| **charged and weighted** | **0.375 / 1.500 / 8.125** | 0.0959 / 0.3293 | **9/90** |

⚠️ **The deviation column is not a regression.** `free` measures a Room's parts
and ignores the floor it is about to be handed; `charged` measures the same warp
against what the Room will actually hold. The gap — p50 **0.0652 → 0.0959** — is
the size of the understatement in every warp fidelity figure quoted on a voided
candidate, and it is the biggest thing this ticket found.

Cost of the fix: one `AddMultiplicationEquality` per component, p50 one
component, on 15.5 % of candidates. **No new dependency and no new variable
class** — the same call the Room areas already use. INFEASIBLE unchanged.

**Why a contract field rather than letting the solver work it out.** It passes
ADR 0014's test and fails the one that refused zoning. *Only the Proposal knows
it*: the receiving Room is **not derivable** — largest shared edge agrees with the
donor **28.4 %** of the time and is ambiguous on 28.4 % of components, largest
bordering Room 38.1 %, the part that can geometrically absorb it 24.1 %. And the
solver cannot infer it: `solver-formulation.md`'s objective is L1 displacement of
all four corners with H3 posting exact tiling soft at 100 000, so **every
bordering Room's repair costs the same**. Which Room receives 0.3–2.8 m² is a tie
broken by nothing the Brief said, and an arbitrary 1.5 m² can push a small Room
through `dim.max_area`, hard at `both`.

The receiving Room is the **donor's own**, recorded at conversion — watershed
ownership purity is p50 **1.00** and ≥ 0.80 on **72.7 %** of components — falling
back to the largest bordering Room. Not the geometric absorber, which is right
24.1 % of the time and is the solver's arbitrary tie-break moved one layer
upstream and dressed as a fix.

⚠️ **Conversion-side absorption is available and deliberately not taken.** Greedy
growth of bordering parts to fixpoint, aspect held, closes **42.3 %** of the void
area and leaves residue on 11.74 % of the index — and it returns floor to the
wrong Room three times in four, corrupting the arrangement the index exists to
preserve. Now that the void is charged it buys nothing worth a transform on the
donor record. ADR 0017 is the standing reminder about transforms whose fidelity
nobody looks at.

**Does it reach the fidelity numbers? Yes, and in a way the rig cannot see.**
On the published arms, voided donors are statistically indistinguishable at Brief
level — `cross` Σ Space/target p50 **0.9894** clean against **0.9923** voided,
`ring` 1.0041 against 1.0025 — so **no published number moves and 55's 25,5 % and
3,6 % stand**. That is not reassurance: `absolute_area.py` reports Σ Space and
per-room deviation and **has no output for realised unassigned area at all**,
which is why this had to be measured from outside the rig. The per-room figure
*is* affected, by the 0.0652 → 0.0959 above. Handed to `experiments/warp/`.

**Is a void ever real? 2.0 % of the area, and v1 has no object for it either
way.** No shaft or riser type among the nineteen, and an enclosed pocket could not
be a Room in any case — `circ.potential_reachability` refuses it. So the 2 % is
charged to a bordering Room like the other 98 %: wrong, about 0.3 m² on one
dwelling in fifty, and written into §8 rather than hidden inside the residue
figure. ⚠️ **Still not rendered** — `render_sheet.py` exists and no voided
candidate has been drawn after its warp.

### The closing check

*"A stated `target_area` and the Σ Space area of a plan built from a voided donor
agree for a reason, not by the 5 % gate absorbing it."* **They now agree for a
reason**: the void's area is a term in the receiving Room's `area_r`, so that
Room's deviation is measured on what it will hold after H3 closes the hole, and
Σ Space is unaffected because the void was never outside the Envelope. What the
5 % gate was absorbing was not Σ Space at all — it was the *distribution*, and
the distribution is what this fixes.

### Two handoffs this file was owed, taken rather than passed on

`docs/spec/proposer.md` had no other claimant and both were addressed to its
holder. Passing either a third time is the defect that created ticket 44.

- **From 56 — §2.2.3's "the notch warps along with everything else, for free"** —
  is what makes ADR 0020's by-construction guarantee false, worth **1,5 % of
  `interior`** and **5,6 points** of plan-level `dim.statutory_min_area`. The
  sentence is struck and replaced with the constraint that holds the share, its
  measurement (`covered ÷ interior` 0.9833 free, 0.9986 held), and the statement
  that this is **not** ADR 0003 consequence 7.
- **From 47 — `worst_room_iou`** is now an index field, a **hard gate at 0.30**
  costing 6.65 % of the index at `conf: fitted`, and a **rank above the gate**
  rather than a 0.50 gate that would cost 17.2 %. §2.2.4 also records why it is
  gated where `frontage_reach` is only partitioned: worst-room IoU is a pure donor
  fact, `frontage_reach` is joint with the Brief's Envelope and §2.2.6 says the
  conversion cannot tell `exterior` from `party`.

### Declared on resolution

`docs/adr/0028-…` (new), `CONTEXT.md` (**Enclosed void** is a new term;
**Notch** gains an `_Avoid_` against reading the two as one quantity, which
`uncovered` does and which is why neither was noticed; **Proposal** gains its
membership test) and `experiments/void/` (new). None had a claimant.

### What it hands on

- **`fit_rects.py` owes a fourth per-record field** — the void components with
  their donor owner. Both inputs are in hand; `experiments/void/provenance.py` is
  the reference. Take it with the cut-line frame, per-pair relation provenance and
  `frontage_reach`: four statistics, one pass.
- **`experiments/warp/` — ticket 57's** — the void variables in
  `fit_warp.warp_model`, and an output for realised unassigned area that the rig
  has never had.
- ⚠️ **The constrained notch and the charged void are ONE unmeasured cost.** Both
  constrain the warp solve; `experiments/warp/`'s `ring` arms reach the notch
  invariant by *re-sizing the box* instead, so the genuinely constrained model's
  INFEASIBLE rate is unmeasured. Measure it once, for both.
- **`solver-formulation.md`** does not know the `voids` field exists, and H3 plus
  L1 corner displacement is what makes it necessary.
- **Source B has the same defect in a form nobody can measure** — diffuse slack
  rather than named components, so it emits an empty list not because it has none
  but because it cannot name them. The Proposer source B row's.
