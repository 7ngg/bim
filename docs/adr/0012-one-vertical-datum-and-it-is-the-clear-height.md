# One vertical datum, and it is the clear height

The Plan has no Z. `CONTEXT.md` defines a Wall as a centreline and a thickness and
an Opening by three widths; `ifc-export.md` §12 names **four** vertical inputs it
refuses to invent — `h_storey`, `h_clear`, per-opening `H`, per-window sill — and
`annotation.md` ships three schedule columns and one general note that cannot be
filled. **v1 adopts exactly one vertical datum, `h_clear`, floor to finished
ceiling.** Every other vertical value is expressed against it or refused.

Values: `profiles.AZ.rooms.clear_heights_mm` and `profiles.AZ.openings`.
Findings: `docs/research/vertical-dimensions.md`. Gates:
`experiments/region-profile/gate_check.py`.

## `h_storey` is deleted, not deferred

AzDTN 2.7-2 — the live 2021 instrument, read first-hand — **prescribes no storey
height.** `mərtəbə hündürlüyü` occurs twice: in the §3 definitions, as the term
that classifies a `zirzəmi` or `kürsülük` storey, and in the passenger-lift
table's Note 2, where the table is *"tərtib edilmişdir"* — compiled — on the basis
of a 2,8 m storey height, with Note 3 directing that the lift count be recomputed
where it differs.

That 2,8 is a **lift-traffic modelling assumption**, and publishing it as
`h_storey` would be ticket 25's trap wearing new clothes: a real number, from the
right live document, doing a job it was never written for. It fails arithmetically
too — 2,8 floor-to-floor over a 2,7 clear implies a slab plus floor build-up of
about 100 mm, which no reinforced-concrete slab is.

The alternative was to derive it: `h_clear` plus a slab, plus a floor build-up.
That is a **second layer set on the axis ADR 0010 has no reading for**, with no
Azerbaijani source — and `t_ext_total`'s 20 mm external finish is already
unsupported on a second axis, so the profile has form here.

So the question became: what does floor-to-floor actually buy? §12 named two
consumers and **both are empty**. `IfcBuildingStorey` spacing is vacuous — there
is exactly one storey, pinned at `Elevation = 0.0`. Wall extrusion height is a
*choice*, because the export authors **no `IfcSlab` and no `IfcRoof`**: nothing
sits on top of a wall in this file.

**This was not the cheap answer, and the cheap answer was not available.** A wall
body cannot omit its height the way `Pset_WallCommon.LoadBearing` omits itself —
an extrusion needs a number, so ADR 0011's *absent is unknown* escape does not
reach here. The choice was forced between a number derived from a statutory
`verified` figure and a number invented from an unsourced build-up. This is the
move ADR 0010 already made on the horizontal: name the plane the published number
measures to, and derive everything else from it.

**Declared consequence:** a wall body is **floor-to-ceiling, not slab-to-slab.**
It is an understatement, and the export says so rather than padding it.

## One `h_clear` per Plan, and the corridor allowance stays inert

AzDTN 2.7-2 cl. 5.8 gives two numbers, and the second is not a second requirement:

> Yaşayış otaqlarının və mətbəxin hündürlüyü **2,7 m**-dən az olmamalıdır.
> […] Mənzildaxili dəhlizlərin, holların, antresolların […] hündürlükləri
> **insanların hərəkətinin təhlükəsizliyini təmin etmək şərtilə** 2,1 m-dən az
> olmamalıdır.

The corridor figure is a **conditional allowance to reduce** — *provided the
safety of people's movement is ensured*. Exercising it asserts a safety judgement
this engine cannot make, and buys a dropped ceiling whose build-up the model does
not have. It stays in the file as `verified` data flagged **inert**, the same
posture `area_convention`'s balcony coefficients already hold: a dropped ceiling
later is a data change, not a redesign.

The clause also settles the **plane**, which the profile had never recorded: cl.
5.8 parenthesises the mansard case as *(döşəmədən tavanadək)* — floor to ceiling.
`h_clear` is the source's own quantity, not our reading of it.

## The Brief may state it

The first answer was to refuse the field, and it was wrong. An architect never
*invents* a floor-to-ceiling height — it is a building given, stated by the
client. Baku stock genuinely spans Soviet-era ≈2,5 to new-build 3,0–3,2, and
hard-coding 2700 asserts a fact about the user's building nobody told us. C4
exists for exactly this: state it, default it, surface the `Assumption`.

The defaults ladder has **two rungs here, not three** — the corpus rung is dead,
because Swiss Dwellings and ResPlan are both 2D and neither carries a height.
Bounded below by cl. 5.8's statutory 2700.

This is what makes a vertical **predicate** possible at all. The solver is 2D and
cannot violate a height, but a *Brief* can state 2400. That is a hard Brief error
on the exact precedent of `area.convention_agrees`: it rejects the request, not
the candidates.

## A sill is derived from one head line

AzDTN 2.7-2 publishes **no window sill height** — `pəncərə altlığı` returns zero
hits in the full 2021 text. A sill therefore cannot be quoted, and a per-room-type
table would be four invented numbers.

So: one datum, `openings.head_datum_mm` = **2200**, and `sill = head_datum −
catalogue H`. The datum is not invented either — 2200 is the **balcony door's own
catalogue head** (`BS 22-7,5`), taken because a balcony door and the window beside
it share a lintel, which is the ordinary post-Soviet living-room composition. The
tallest catalogue opening sets the head line and every window hangs from it; doors
sit 100 mm below at their own 2100, which is what a real elevation does.

Structure derived, one constant chosen from the catalogue rather than from
nowhere — ADR 0009's shape. On the shipped catalogue: living **700**, bedroom
**700**, kitchen **1000**, the last clearing a 900 mm counter, which is why the
kitchen window is the short one. All even, so ADR 0004 holds on derived sills too.

A sill is **not** a catalogue column: the same `OR 15-15` sits at one height in a
living room and another over a counter. The catalogue fixes H × W; the datum fixes
placement.

## The guarding height is published and its trigger is refused

cl. 8.3, mandatory register:

> Pilləkən, balkon, lociya, terras, dam və **yıxılma təhlükəsi olan digər
> yerlərdə** məhəccərlərin hündürlüyü **1,2 m**-dən az olmamalıdır.

The height is `verified` and statutory, corroborated at cl. 8.10. Windows are
never named — the clause reaches them only through *other places where there is a
risk of falling* — and **no sill threshold is stated anywhere in the norm**.

An `engine_choice` threshold was drafted and then withdrawn, because the trigger
is not a missing constant: it is **unknowable at v1's scope**. Whether a window is
a place with a risk of falling depends on the drop below it, which depends on
which storey the dwelling is on and what lies outside. v1 has one Storey at
elevation 0, `IfcSite` is out of scope, and the site is ruled out of scope on the
map. A ground-floor window needs no barrier; the same window eight floors up does;
**nothing in the model distinguishes them.**

So v1 publishes the height and refuses the trigger. `annotation.md`'s `Fall
barrier` column reads `—` for every window, which that spec already provides for.
Choosing a threshold would have been a **safety** claim with no source and no way
to evaluate it — the C8 breach ticket 25 exists to prevent. A refusal in the same
class as accessibility, and as the ergonomic layer's height below.

## The ergonomic layer owes no height

ADR 0009's floor is region-invariant and derived from **fixture footprints, all of
them in plan**. A height is not a footprint. The layer carries zero vertical
figures, and its own source corpus turned out to be accessibility clearances
throughout. No region-free ergonomic height is derivable, and the refusal is
recorded in the layer rather than left as an absence — this layer has already
refused one number it was handed.

## Consequences

- `ifc-export.md` §12 drops from four inputs to two, and **§6**'s `IfcSpace.Body`
  *"extruded to storey height"* is corrected to `h_clear`. A Space is
  floor-to-ceiling; §6 and §12 contradicted each other inside one document.
  ✅ **Both landed** by *What geometry an `IfcSpace` actually gets*, which also
  found that the correction was not one word: IFC4 defines
  `Qto_SpaceBaseQuantities.Height` from the **base slab**, not the finished floor,
  so this ADR's declared understatement had to be published in the file rather than
  merely declared here — `ifc-export.md` §8.4a.
- `annotation.md`'s three schedule columns and general note 4 are all fillable;
  the `Fall barrier` column is deliberately `—`.
- `gate_check.py` grows a vertical section: 33 → **67 gates, all pass**. With
  `h_storey` gone there is no floor-to-floor left to hide a bad opening in, so
  every catalogue head is asserted against `h_clear` and every derived sill
  against the datum and ADR 0004.
- A **Wall gains no height field.** Height is a property of the Storey that every
  Wall reads. ADR 0001's `load_bearing` hook is the precedent for paying for a
  field early, but that hook exists because a wall's load-bearing status *varies
  between walls and is genuinely unknown*. A single-storey dwelling with no
  dropped ceilings has one height, known, shared — a per-Wall field would record
  the same number N times, which is the justification *One internal thickness*
  already killed by count.
