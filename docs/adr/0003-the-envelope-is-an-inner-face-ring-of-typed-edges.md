# The Envelope is an inner-face ring of typed edges

Two questions about the Envelope were open, and they turn out to be one decision
about the same object. **Which face does the Envelope name** — a number like
"9 by 7 metres" is meaningless until it says so, and `CONTEXT.md` requires every
dimension to declare clear or centreline, which the Envelope never did. And
**what distinguishes a flat from a house** — the map treated it as a code-path
question and it is not one.

The Envelope is the **inner face of the external wall**, and it is an **ordered
ring of edges**, each carrying a boundary condition and an entrance flag.

## The construction

- The Envelope **is** the interior clear region. Not the footprint, not a
  centreline.
- ADR 0001's solve domain becomes `dilate(Envelope, t_int/2)`. `t_ext` does not
  appear.
- The ring is rectilinear: a bounding box minus at most two notch rectangles,
  which spans rect, L, U and T. ✅ The cap is **evidenced** — two notches is the
  knee of its own ladder, a higher cap converts *worse*, and widening the family
  is refused at a measured ceiling of 4.17 % of the corpus. See the second
  amendment at the foot of this ADR.
- Each edge carries `condition` in `{exterior, party}` and a boolean
  `entrance_side`.
- `exterior` may host windows. `party` is blind and shared. `entrance_side` marks
  where the primary door may go and is **orthogonal** to `condition`.
- Dwelling type is a **preset over the ring**, not a branch. ⚠️ The two examples
  this bullet gave — `terrace_mid` as two opposite `exterior` and two `party`,
  `flat_single_aspect` as one `exterior` and three `party` — are **superseded**:
  no preset is whole-edge any more, and a preset is now a quantile of measured
  exposure rather than a building form. See the amendment at the foot of this
  ADR. The *decision* stands: dwelling type is a preset over the ring.
- The gross external footprint is **derived** at export, per edge, from that
  edge's own thickness.

## Considered options

- **Envelope as the outer face.** Rejected. It matches the word "footprint" and
  nothing else. It forces `erode(Envelope, t_ext)` before the solve can start, and
  its one real consumer — a plot with setbacks — is out of scope. It also makes a
  Homeowner's tape measurement wrong by two wall thicknesses, silently.
- **Envelope as the exterior centreline.** Rejected. Superficially attractive
  because a `Wall` *is* a centreline and a thickness, and because a party wall's
  centreline is the ownership boundary. But v1 makes no ownership claim, and it
  buys a `t_ext/2` conversion on both the solver side and the human side rather
  than deleting one on each.
- **Flat and house as two code paths.** Rejected. The genuine difference is not
  where the Envelope came from — it is **which edges can hold a window**. A flat
  has party walls; a bungalow does not. Branch on dwelling type and that fact stays
  unrepresented, which is how a bedroom gets a window onto a neighbour's wall and
  passes every check.
- **`condition` as a three-value enum including `access`.** Rejected. It cannot
  express a house's front door, which sits in an `exterior` wall that also carries
  the entrance. The flag is orthogonal to the condition and has to be modelled that
  way.
- **Envelope provenance as one flag meaning flat-or-house.** Rejected, and it was
  already in the model as that. Provenance is **per-field** and means only *did the
  user supply this number*. A house owner who states a plot dimension has a stated
  Envelope; a flat whose dimensions we guessed has an invented one.

## Consequences

1. **The Homeowner's number passes through untouched.** "My flat is 9 by 7" is a
   clear dimension by `CONTEXT.md`'s own definition, and it *is* the Envelope. No
   conversion, so no place for the conversion to be forgotten.
2. **Per-edge external thickness is free.** ADR 0001's erosion constant is
   `t_int/2` everywhere and each edge's body grows outward from its own inner
   face. A 300 mm party wall beside a 250 mm external wall costs nothing.
3. **No third `Wall` class.** `External` and `Partition` stand. The edge's
   `condition` selects the thickness from the region profile. `load_bearing` stays
   `None` on party walls; v1 still makes no structural claim.
4. **The solver's exterior-wall constraint must filter the ring.** H8 — every
   habitable room touches an exterior wall over a window's width — reads
   `Envelope.exterior_faces()`, which today returns every boundary face. Under this
   ADR it returns only `exterior` ones.
5. **Every solver timing on the map describes a detached bungalow.** All measured
   runs had 100% exterior exposure. ⚠️ The sizes quoted here are **measured and
   wrong**: `terrace_mid` does not halve the available face set and
   `flat_single_aspect` does not quarter it. Against `detached` at seven rooms
   they deliver **0.67×** and **0.43×** of the exterior run per room. The
   *direction* was right and is now priced — see the amendment at the foot of
   this ADR.
6. **Notch edges need their own condition**, defaulted by dwelling type —
   `exterior` for houses, `party` for flats — and always surfaced as an Assumption,
   because a notch is a garden in one case and a neighbour in the other.
7. **The entrance edge is fixed before the solve.** It is the source node of the
   circulation flow, so it cannot be a post-solve choice. ⚠️ **Read this as *per
   candidate*, before that candidate's solve** — ADR 0020 gives each candidate
   its own notch share and so its own ring edge *count*, and two candidates for
   one Brief do not share a ring. The edge is identified by **side**, never by
   ring index, which is what makes that safe. See the second amendment at the
   foot of this ADR.
8. **The area rule in the Acceptance bar re-keys** from dwelling type to per-field
   provenance, which corrects a case it got wrong: a stated house Envelope is not
   subject to a hard area-drift reject.

## Amendment — the presets were fitted to a measurement of one room (2026-08-26)

*The exposure presets were fitted to a measurement of one room* re-fitted
`EXPOSURE_PRESETS` and re-ran what had been measured at the old values. The ADR's
**decision is untouched** — the ring, the two conditions, the entrance flag and
"preset over the ring, not a branch" all stand. What moved is every *number*
attached to a preset, and two claims made in the ADR's own voice.

**Why they were wrong.** `dataset-inventory.md` §1.5's exposure distribution
described the **largest single room** of each dwelling rather than the dwelling:
a dwelling's `area` polygons are disjoint, so their union is a `MultiPolygon` and
the script took its largest part. Corrected, the median exterior fraction is
**0.68**, not 0.37. `corpus_median` and `flat_single_aspect` had both been tuned
against the wrong column.

**What replaces them.** Presets are now fitted on **exterior run per room** over
2,238 Swiss dwellings — `experiments/envelope-exposure/`, series committed. Run,
not fraction, because a fraction only transfers between dwellings whose
perimeters match and these do not: at eight rooms the toy Envelope carries 36.0 m
of perimeter around 75.0 m² where the real median dwelling carries 47.6 m around
94.1 m². H8 reads run — a room needs a window's width of façade and cannot spend
a percentage. Anchored at n = 7, the corpus median room count and the centre of
C13's band. Corpus run per room: p5 **2.09 m**, p25 **3.28**, median **4.19**,
p75 **5.09**, p95 **6.94**.

**A preset is now a quantile with a ring shape, not a building form.** This is
the amendment's one real departure from the ADR's framing, and it is forced by
measurement. Real dwellings are **63.3 % four-sided** and **26.0 % three-sided**
— 89.3 % between them. The forms the presets name — one aspect, an adjacent
pair, an opposite pair — are **10.6 %** of the corpus between them, and there was
**no three-sided preset at all**. The finding is threshold-insensitive: three-
and four-sided stays above 80 % anywhere from a 0.05 to a 0.33 material-side cut,
and is still 62.5 % at 0.50. The five keys survive only because they are named in
`brief.md`, `acceptance-bar.md`, `room-constraints.json`, `CONTEXT.md`, this ADR
and three experiment directories that ticket could not write; `flat_corner` and
`terrace_mid` are now a **matched pair**, the same exposure on a different ring,
so the two isolate shape at fixed run.

**Three published results did not survive the re-fit**, all of them measured at
`corpus_median` or `flat_single_aspect` and therefore at roughly half the real
exposure:

| Result | Was | Now |
|---|---|---|
| H8 kills the Brief at six rooms, corpus-median exposure | 0/5 seeds | **5/5** — gone |
| `flat_single_aspect` "fails at 6, 7, 8, mostly at 9" | 0/5 at 7 and 8 | fails at **6** only, 3/5 at 8 |
| The flat-versus-house **diversity gap** | 0.54× at 5 rooms, 0.73× at 7 | **1.00× and 0.98×** — gone |

The third is the largest. `envelope-exposure/README.md` held the gap as a second
and independent cause of the diversity asymmetry, alongside the missing diversity
axis. At corrected exposure **there is no gap**: the ranges overlap almost
exactly (0.514–0.524 against 0.515–0.525 at five rooms). The asymmetry goes back
to the diversity axis alone, and *Variant generation and ranking* should stop
carrying a second cause.

**What survives.** The headline that no real flat resembles the fully-exposed
geometry the 6.25 s-at-24-rooms timing assumed **stands** — 1.1 % of dwellings at
≥ 0.99 exterior. So does the non-monotonicity in room count: `flat_single_aspect`
still fails at six rooms and passes at seven, and n = 6 is still the worst row
across three presets, because `envelope_for(6)` picks an L. "Dead from n rooms"
is still measuring the envelope n selects, not n.

**⚠️ Two limits this amendment cannot remove**, both structural, both inside
`experiments/solver-toy/`, which that ticket may not write. They are handed on as
*The toy Envelope is more compact than a real dwelling*:

1. **Every preset drifts across C13's band.** `envelope_for(n)` scales area
   linearly and perimeter as its root, so a constant four-vector delivers a
   *falling* run per room against a corpus that is flat in n (median 3.97–4.41 m
   from four rooms to twelve). `corpus_median` sits at the corpus **p85 at four
   rooms and p25 at twelve** — a 60-percentile swing from one number. Published
   as a drift table rather than hidden.
2. **Above nine rooms the corpus median is unreachable at any preset**,
   `detached` included, because it needs more exterior run than the Envelope has
   perimeter. The toy Envelope is more compact than a real dwelling and gets more
   so with n — perimeter/area **0.390 against the corpus 0.572** at twelve rooms
   — and `AREA_PER_ROOM_M2` is **9.65 against a corpus median of 11.36 m²**.

**⚠️ One defect found in passing.** `Envelope.exterior_fraction` — the quantity
every old preset was tuned to hit — **double-counts**. `all_faces()` emits each
bbox edge in full *and* all four faces of every notch, so the stretch a corner
notch removed is counted twice; at eight rooms the true perimeter is 144 grid
units and it counts 180, a denominator 25 % too large. The phantom faces reach
`exterior_faces()` too, which H8 reads, but that half is harmless: `contains`
forbids a room inside a notch, so no room can be flush with the removed stretch
and claim its daylight. Corrected in
`experiments/envelope-exposure/true_fraction.py`, which is what the new presets
were fitted against; the fix in `geometry.py` is handed on with the two limits
above, because it changes what the solver is given.

## Amendment — the notch cap is evidenced, and the shape family stands (2026-08-26)

*The two-notch cap is now evidenced, and more notches is not the fix* held this
file to close the standing charge that the ≤ 2-notch cap was **"unevidenced in
both directions"** — the map's *Non-orthogonal geometry* fog patch said so, and
this ADR gave no evidence either way, which is what made the charge stick. It is
retracted. The cap is **evidenced and vindicated**, the shape family is
**deliberately not widened**, and the population the cap appeared to fail was
never the cap's to serve.

### The evidence

Three measurements, none of them new to this amendment, all now cited here so a
reader stops re-deriving them. `docs/research/rectangularisation.md` §6.4 and
§13, ADR [0017](0017-three-of-the-conversions-fidelity-headlines-are-constraints-restated.md)
failure mode 4, `experiments/rectangularise/`.

1. **Two notches is the knee of its own ladder.** Median envelope loss over
   2,317 converted dwellings at k = 0…4 is 0.1610 / 0.0503 / **0.0178** / 0.0114
   / 0.0096. A third notch buys 0.6 percentage points and a fourth 0.2. Two
   notches describe **61.8 %** of real dwellings exactly; a plain rectangle
   misdescribes 16.5 % of envelope area at the median, so the L/U/T family is
   doing real work and is not decoration.
2. **A higher cap makes the conversion worse.** The k ≤ 2 ablation's *"up to 4
   notches"* arm converts **88.0 %** against the shipped **93.2 %**, 25
   INFEASIBLE against 13. A more articulated Envelope leaves the rectangles less
   slack to satisfy the hard adjacency and area constraints inside it. Fidelity
   of outline and feasibility of tiling trade against each other, and the cap
   sits on the right side of that trade.
3. **The dwellings the cap appears to fail are not failed by the budget.**
   283 dwellings (10.92 %) lose > 0.10 of envelope area at k = 2. Sixteen of them
   are **inside the cap already** and still lose > 0.10 — at `notches_all` = 1
   the loss is identical at every k. A notch is one **rectangle**; a complement
   component need not be one. Where it is L-shaped, stepped or chamfered, the
   budget never bound.

### The shape family is not widened, and this is the number that closes it

The evidence questions the shape *family*, not the count, so the family was put
on trial. §13.2–13.3 price the two ways to widen it:

- **A general rectilinear ring with a vertex budget** rescues the rectilinear
  half of the tail: **108 dwellings, 4.17 % of the corpus**, of which **46.3 %
  are still above 0.10 loss even at four notches**. That 4.17 % is the entire
  ceiling of the widening.
- **Chamfered or angled edges** would be needed for the other half — **8.76 %**
  of the corpus is more than 10 % off-axis in its own frame and holds **49.5 %**
  of the tail — and they break axis alignment for the 250 mm grid,
  `AddNoOverlap2D` and every dimension chain.

**Refused, on measurement rather than on cost.** The rectilinear widening buys at
most 4.17 % of the corpus, and it spends the property that makes this ring cheap
everywhere else: the edges are **typed**. A notch is *"a garden in one case and a
neighbour in the other"* — a nameable thing with a boundary condition, an
Assumption surfaced to the Homeowner (consequence 6), a drawable and
dimensionable edge, and an IFC entity (ADR 0011). An arbitrary rectilinear vertex
has no such story, and inventing one costs `annotation.md`, `homeowner-surface.md`
and `ifc-export.md` for a twenty-fifth of the corpus.

**The cap stays at two. `rect`, `L`, `U`, `T` stays the family.**

### What the tail actually is, and where it goes

The tail is a **donor-quality** fact, not an Envelope fact — and that is the
reframing this ticket contributes. There is no ground truth on the generation
side to be unfaithful to: `brief.md` §5.1 takes `shape` out of the `ResolvedBrief`
entirely, and ADR [0020](0020-one-brief-one-envelope-area-many-envelope-boxes.md)
derives each candidate's box from its **donor's** recorded notch share. What v1
draws is a legitimate real outline whatever the donor was. What a bad donor
carries is a distorted **arrangement**, and retrieval's whole claim is that the
arrangement is a real home's.

§13.4 measures that envelope loss is a poor instrument for finding those donors:
**42.2 %** of the loss tail converts faithfully anyway, **12.70 %** of everything
outside the tail does not, and a worst-room IoU cut removes **10.09 %** of the
*most faithful* envelope band — dwellings whose outline the Envelope describes
exactly and whose rooms the fit still got wrong. The quantity to act on is
**worst-room IoU**, which is in the same fit record, and the population it names
(154 dwellings, **6.65 %** of the index) is two thirds invisible to either proxy.

That is `proposer.md` §2.2's to implement and this ADR does not write it —
see the ticket's resolution for the handoff. This ADR records only that **the
Envelope's shape family is not the lever**, so nobody comes back to the cap for it.

### §7 re-read: one ring per candidate

Consequence 7 says *"the entrance edge is fixed before the solve."* Written
before ADR 0020, it reads as **one ring for the job**, and that is now wrong: a
per-candidate notch share changes the ring's **edge count**, so two candidates
for one Brief do not share a ring. Held over twice by *A dwelling that states a
shape gets a box nobody measured* and *The exposure presets were fitted to a
measurement of one room*, both of which declined to write blind into a claimed
file.

**Consequence 7 must be read as: the entrance edge is fixed per candidate,
before that candidate's solve.** What makes this safe already exists — the
entrance edge is identified **by side**, never by ring index, so a changed edge
count cannot move it — but the ADR never said so, and a reader who assumed index
identity would have written a real bug. Consequence 7 is amended to say it.

Nothing else in consequence 7 moves: the entrance edge is still the source node
of the circulation flow and still cannot be a post-solve choice.

---

## Note: what the cap costs downstream, which the cap's own evidence never priced

Added by *The notch is two components and a quarter of donors have more*
(ticket 61). **The cap does not move and this is not a challenge to it** —
`docs/adr/0003-…` was unclaimed and this is a price, not a decision.

*The two-notch cap is now evidenced* priced the cap two ways: as index thinning
(**6.65 %** at `worst_room_iou` < 0.30) and as a refused shape-family widening
(a vertex budget rescues **4.17 %** of the corpus, 46.3 % of which still fails at
four notches, and half the tail is chamfered or curved). Both stand.

**Neither is the price a Room pays.** `envelope_approx` caps at two by cutting
the two largest complement components and leaving the rest **inside** the ring —
deliberately, and the docstring says why: an inscribed rectangle under-cuts, and
*"under-cutting leaves a little non-dwelling inside the Envelope, which shows up
as envelope loss and costs a room nothing."* Measured over the 2,317 converted
donors, it is not always a little and it does not cost nothing:

| | |
|---|---|
| donors whose complement needs 3+ components of ≥ 0.25 m² (`notches_needed`) | **37.6 %** |
| `notches_used` | 2 on **90.16 %**, and never more |
| `envelope_loss` — non-dwelling left inside the Envelope | p50 **1.78 %** of the domain, p90 **9.92 %**, mean **3.72 %** |

That floor is inside a ring the solver must tile exactly
(`model.no_unassigned_area`, hard), so a Room receives it. *It costs a room
nothing* was true of the **conversion**, whose fit is scored against the real
dwelling, and false of the **engine**, which hands the floor to whichever Room
the objective finds cheapest. ADR 0020's second amendment and ADR 0028's
amendment are where that is now accounted for: the notch is the `notches_used`
spans, and everything else uncovered inside the ring is a void, charged to a
named Room.

**Nothing in the cap's own reasoning weakens.** Two is still the knee (median
envelope loss 0.161 / 0.050 / **0.018** / 0.011 / 0.010 at k = 0…4), a higher
cap still converts *worse*, and the widening is still refused on measurement.
What changes is that the loss the cap accepts now has a name and an owner
downstream instead of disappearing into a Room nobody chose.
