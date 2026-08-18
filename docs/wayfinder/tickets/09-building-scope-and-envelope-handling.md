---
id: 9
title: Building scope and envelope handling
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: []
---

# Building scope and envelope handling

## Question

Where does the outline come from, and does v1 honestly ship houses as well as
flats?

Two unresolved threads, joined because they are the same decision seen from two
sides.

**The envelope.** C4 settled that the Homeowner may state a shape and area, and
that the app fills the gap otherwise. Unresolved:

- What shapes are on offer — rectangle, L, T, U, free polygon? A Homeowner cannot
  draw a boundary, so what is the picker, and what does "specify the shape" mean
  in an interface they can use?
- What does the default envelope look like when they say nothing at all? Derived
  from total area and room count, or a small set of curated presets?
- Every learned generator in this field *fills* a given boundary; none invents
  one. Does v1 generate a footprint from a plot and program, or is that deferred?
- A flat has a **given** envelope — it exists in a real building. A house has an
  **invented** footprint. Is that one code path or two?

**The scope.** C5 scopes to single-dwelling, single-storey, flats and houses. But
most real houses are not single-storey, and multi-storey is out of scope for this
map. So:

- Does v1 ship **flats only**, honestly — with houses arriving alongside
  multi-storey in a later effort?
- Or do single-storey houses (bungalows, small detached) carry enough weight to
  ship, and if so, what is the honest description of what v1 does *not* do?
- If flats only: does that change the corpus ranking in *Cross-dataset
  unification*, given Swiss Dwellings and ResPlan are both apartment corpora?

The answer here sets the input contract for *Brief schema and parsing contract*
and bounds the boundary geometry that *Solver formulation for layout projection*
must handle — a rectangle-only v1 is a materially easier solve than arbitrary
polygons.

---

## Resolution

**v1 ships flats and single-storey houses through one code path, because the
Envelope becomes an ordered ring of typed edges and the dwelling type is data on
that ring.** The Envelope is the **inner face** of the external wall — it *is* the
interior clear region — so the Homeowner's tape measurement is literal, ADR 0001's
solve domain is `dilate(Envelope, t_int/2)` with no `t_ext` term anywhere, and the
gross footprint becomes derived.

### The Envelope, defined

| Property | Decision |
|---|---|
| Reference face | **Exterior inner face.** The Envelope *is* the interior clear region. |
| Shape | **Rectilinear: bbox minus at most 2 notch rectangles.** Offers rect, L, U, T. |
| Edges | An **ordered ring**. Each edge carries `condition` in `{exterior, party}` and a boolean `entrance_side`. |
| Provenance | **Per-field**, `stated` or `invented`. Not per-Envelope, and not tied to dwelling type. |
| Orientation | A north angle, stored, used **only** for the Drawing's north arrow and as a soft Brief preference. |
| Timing | **Fixed before the solve, always.** |

`condition` is two values, not three. A flat's front door pierces a **party** edge
— the wall to a common corridor is shared and blind, which is geometrically a
party wall whatever it separates. `entrance_side` is therefore an orthogonal
**flag**, not a third condition: a house's front edge is `exterior` *and*
`entrance_side`; a flat's is `party` *and* `entrance_side`. Collapsing them into
one enum would have made "exterior wall with a front door in it" unsayable.

### Why the inner face

Three candidates: outer face (the footprint), centreline (matches `Wall` =
centreline + thickness), inner face (the clear boundary). Inner face wins because
it makes two independent conversions vanish at once.

- **Toward the solver.** ADR 0001 anchors the solve domain at
  `exterior-inner-face + t_int/2` and proves the erosion holds **for any `t_ext`**.
  With the Envelope *at* that face, the domain is `dilate(Envelope, t_int/2)` and
  `t_ext` never enters the solve.
- **Toward the Homeowner.** `CONTEXT.md` defines a **Clear dimension** as what a
  Homeowner would measure with a tape. "My flat is 9 by 7" therefore *is* the
  Envelope, with no silent conversion — which is exactly the class of confusion the
  clear-versus-centreline rule exists to prevent.

The outer face's only real argument was the plot, which this ticket rules out of
scope. The gross external footprint is now **derived** at export; which area the
5% rule measures stays *Area measurement convention*'s call.

**Per-edge `t_ext` is free.** ADR 0001's erosion constant is `t_int/2` everywhere
and each edge's exterior body grows outward from its own inner face, so a thick
party wall beside a thin external one costs nothing. **No third `Wall` class is
needed** — `condition` selects the thickness from the region profile, and
`External` / `Partition` stand as `CONTEXT.md` has them. `load_bearing` stays
`None` on party walls too; v1 still makes no structural claim.

### Exposure presets

A Homeowner will never say "the north edge is party". They state a **dwelling
type**, which is a named preset resolving to a ring — parsed from prose, surfaced
as an Assumption, editable per edge. Same move as the Opening catalogue: a
discrete set beats free specification.

| Preset | Ring (4-edge case) |
|---|---|
| `detached` | 4 exterior; one flagged `entrance_side` |
| `semi_detached` | 3 exterior, 1 party |
| `terrace_end` | 3 exterior, 1 party (differs from `semi_detached` by which edge is entrance) |
| `terrace_mid` | 2 opposite exterior, 2 party |
| `flat_single_aspect` | 1 exterior, 2 party, 1 party + `entrance_side` |
| `flat_corner` | 2 **adjacent** exterior, 1 party, 1 party + `entrance_side` |
| `flat_dual_aspect` | 2 **opposite** exterior, 1 party, 1 party + `entrance_side` |

The last two carry the same counts and differ only in **order**, which is what
forces the ring to be ordered rather than a multiset. **The ring topology is
region-invariant; only the label is regional** — "terrace" is British, the
two-exterior-two-party ring is not.

**Notch edges default by dwelling type — `exterior` for houses, `party` for
flats — always flagged as an Assumption.** Not one generous default: `exterior` on
a flat's notch invents windows onto a neighbour's wall, which passes the window
rule and is wrong on site. A house's notch is garden.

**The entrance edge is chosen by the system for invented Envelopes and stated for
given ones.** It must be fixed pre-solve regardless: it is the source node of the
circulation flow and the subject of `entry.single_primary`.

### The derived Envelope

When the Homeowner states neither area nor dimensions:

    envelope_clear_area = sum(room target areas) / efficiency

with a default aspect ratio applied to get a rectangle. **Both `efficiency` and
the default aspect ratio are `ENGINE_CHOICE`** — ship constants (~0.85, ~1.35) and
fit them on *Fit the ENGINE_CHOICE acceptance thresholds to the corpora*. Curated
preset libraries were rejected: a preset's fixed dimensions fight the room-area
targets carried in the same Brief.

### Findings that bind other tickets

- **The 6.25 s figure at 24 rooms was measured with 100% exterior exposure, and
  does not transfer to a flat.** `Envelope.exterior_faces()`
  (`experiments/solver-toy/geometry.py:103`) returns all four bbox faces plus all
  four faces of every notch, unfiltered — so H8, *"every habitable room touches an
  exterior wall over a window's width"* (`experiments/solver-toy/solver.py:392`),
  was posted against the largest possible face set in every run on the map.
  `terrace_mid` halves that set and `flat_single_aspect` cuts it to a quarter, with
  the same rooms competing for it. This is a **new axis for *Solver timing variance
  sweep***, and it is not a refinement — the numbers currently quoted describe a
  detached bungalow.
- **`exterior_faces()` is the exact seam.** One function, already isolated, already
  the sole consumer of boundary geometry in H8. The exposure ring filters it. No
  other solver code reads the Envelope's shape.
- **Corpus ranking is unchanged, and now confirmed rather than assumed.** Swiss
  Dwellings (45,176 apartments), ResPlan (single flats), RPLAN (apartments), MSD
  (multi-apartment) — **every corpus is flats**, so shipping houses cannot improve
  the corpus fit and dropping them cannot damage it. Houses are generated from
  apartment priors either way. That is the honest limit to state in product copy,
  alongside single-storey.
- **Swiss Dwellings can supply the exposure distribution.** It is the one corpus
  with a building hierarchy, so which edges of an apartment abut a neighbour is
  derivable from its own data rather than guessed — a fit for *Acquire the
  datasets* to confirm and *Fit the ENGINE_CHOICE acceptance thresholds to the
  corpora* to use.
- ***Acceptance validator spec*'s area rule re-keys.** It currently reads "invented
  (house) 5% hard, given (flat) warn-only". Provenance is now per-field and
  independent of dwelling type, so the rule keys on **whether the area-determining
  fields were stated** — which also fixes a case it got wrong: a bungalow whose
  owner states "the plot takes 12 by 9 m" is stated, and rejecting it on area drift
  is the same 100%-rejection bug the ticket already diagnosed.
- ***Brief schema and parsing contract*** gains the Envelope fields, the preset
  table, and one extension to the feasibility pre-check it already inherited: with
  a stated Envelope the lower bound is compared against **a real number**, not just
  a room-sum, so an impossible request is caught before a solve rather than after
  zero survivors.
- ***Opening placement rules*** must read the ring. A **party edge hosts no window
  and no entrance**; only an `entrance_side` edge may carry the primary door. The
  window ratio rule needs the exterior run per Space computed against filtered
  faces.

### Accepted asymmetry

Invented Envelopes get 2 to 3 aspect ratios as a candidate-diversity axis.
**Stated Envelopes get none** — every candidate differs only in the Proposal. That
means flats, the corpus-backed case and the v1 buyer's likelier case, get *less*
variety than bungalows, which is backwards from where demand sits. Recorded for
*Variant generation and ranking* rather than patched here with envelope jitter.

### Honest limits

- **The 2-notch cap has no evidence beyond the toy**, which ran one L and two U
  envelopes. Nothing establishes that a third notch is unaffordable, only that two
  are affordable.
- **`efficiency` and the default aspect ratio are unfitted constants** shipping as
  `ENGINE_CHOICE`.
- **No exposure figure is measured.** The claim that H8 gets harder under `party`
  edges is structural and certain in direction; its cost in seconds is unknown
  until the sweep runs.

ADR [0003](../../adr/0003-the-envelope-is-an-inner-face-ring-of-typed-edges.md).
