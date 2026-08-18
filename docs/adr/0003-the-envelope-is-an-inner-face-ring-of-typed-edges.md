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
  which spans rect, L, U and T.
- Each edge carries `condition` in `{exterior, party}` and a boolean
  `entrance_side`.
- `exterior` may host windows. `party` is blind and shared. `entrance_side` marks
  where the primary door may go and is **orthogonal** to `condition`.
- Dwelling type is a **preset over the ring**, not a branch. `terrace_mid` is
  two opposite `exterior` and two `party`; `flat_single_aspect` is one `exterior`
  and three `party`, one of them `entrance_side`.
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
   runs had 100% exterior exposure. `terrace_mid` halves the available face set and
   `flat_single_aspect` quarters it, against the same room count. The direction is
   certain; the cost is unmeasured.
6. **Notch edges need their own condition**, defaulted by dwelling type —
   `exterior` for houses, `party` for flats — and always surfaced as an Assumption,
   because a notch is a garden in one case and a neighbour in the other.
7. **The entrance edge is fixed before the solve.** It is the source node of the
   circulation flow, so it cannot be a post-solve choice.
8. **The area rule in the Acceptance bar re-keys** from dwelling type to per-field
   provenance, which corrects a case it got wrong: a stated house Envelope is not
   subject to a hard area-drift reject.
