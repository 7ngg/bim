# A derived minimum is not rounded onto the solve grid

**Status:** accepted
**Date:** 2026-08-21
**Ticket:** *Ergonomic minima and the constraint table's missing half*
**Narrows:** [ADR 0007](0007-published-minima-must-erode-onto-the-solve-grid.md)
**Related:** [ADR 0001](0001-centreline-walls-over-a-dilated-solve-domain.md),
[ADR 0004](0004-published-dimensions-measure-wall-faces.md),
[ADR 0008](0008-a-corpus-dwelling-is-converted-by-solving-it.md)

## Decision

ADR 0007's congruence rule — `minimum + t_int ≡ 0 (mod grid)` — binds on the
**region profile**, whose numbers are *quoted from a source*. It does **not** bind
on the **ergonomic layer**, whose numbers are *derived from fixture footprints*.

The ergonomic layer publishes millimetre-precise minima and the solver's ceiling
absorbs the remainder. **The v1 solve grid stays at 250 mm.**

## Why the two kinds of number are not the same kind of number

ADR 0007's worked example rounds **down**: *"a source specifying a 1750 mm kitchen
is honoured by publishing 1650 mm clear."* Read its justification closely — it is a
**unit conversion**. The source's 1750 was a nominal or centreline figure, so
subtracting `t_int` recovers what an occupant can actually tape. That is exactly
ADR 0004's move, and for a quoted number it is right.

A derived minimum has no such conversion available. It is a sum of footprints and
body clearances, every term of which is already measured in **clear** space. There
is no centreline to subtract, and no nominal figure hiding a wall.

**A derived 1700 mm *is* the bath.** Rounding it down to 1650 does not honour a
convention. It deletes 50 mm of bathtub and publishes a `bathroom` floor that
provably cannot hold the fixture that defines the room — the 90 %-right artefact
C2 calls worse than blank.

So the ergonomic layer can only round **up**. And rounding up is arithmetically
*identical* to leaving the minimum unaligned, because `grid·⌈(m + t)/grid⌉` is the
same number either way. There is no third option: for a derived minimum, ADR 0007
is either violated or it destroys the derivation.

## What each option costs, measured

`experiments/region-profile/floor_calibration.py`, against 317,341 Swiss Dwellings
rooms, on the fixture-consistent subset:

| room type | raw derivation | reject | snapped to 250 | reject |
|---|---|---:|---|---:|
| `wc` | 950 × 1150 | 23.0 % | 1150 × 1150 | **56.1 %** |
| `bathroom` | 1150 × 1700 | 0.1 % | 1150 × 1900 | 2.8 % |
| `kitchen` | 1050 × 2100 | 1.2 % | 1150 × 2150 | 1.6 % |

The **WC is the binding room**: its entire real width distribution — p1 744 mm to
p50 1099 mm — **spans less than two grid steps**, so one snap moves the floor
across most of the population. At the shipped body zone the cost is ≈ 10 points of
real corpus on that room alone.

And these are real homes, not annotation debris. Checked against the corpus's own
fixture entities: **0 %** of `wc` rooms fail to hold a WC pan, **0.8 %** of
`bathroom` rooms fail to hold a bath. There is nothing to discount.

## The deletion is narrowed, not removed

ADR 0007 measured its 4-, 5- and 6-room deletion against the **placeholder**
standards table — `living` 2750 mm / 12.0 m², `bedroom` 2000 mm / 7.0 m². The
derived ergonomic floor is roughly half that: `living` 1850 × 2000, `bedroom`
1650 × 1900. The deletion was a function of the minima's *magnitude* against the
Envelope, not of the congruence as such.

`experiments/solver-toy/ergonomic_minima_tiling.py` re-runs ADR 0007's own counts
at 8 seeds with both tables. The placeholder table reproduces the deletion exactly
and unambiguously — **0/8 at n = 4, 5 and 6**, with no Brief constructible at all.

**Measured, the magnitude hypothesis is half right.** Against the derived floor's
own baseline, the clear reading **recovers n = 4 outright** (0/8 → 8/8) and
**still loses n = 5 entirely** (8/8 → 0/8, with Briefs constructible and no valid
tiling found). n = 6 is not assessable: the derived table fails it under the
baseline reading too, where the congruence question does not arise, so that cell
is the harness's Brief generator meeting much smaller minima rather than evidence
about the grid.

So the deletion narrows from `{4, 5, 6}` to `{5, and 6 unknown}`. **That is a real
cost and this ADR does not hide it.** The decision rests on the argument above —
ADR 0007's remedy is a nominal-to-clear conversion and a derived minimum has none
to apply, so the alternative is not "a smaller table" but "a bathroom floor that
cannot hold a bath". The tiling counts were expected to corroborate and instead
came back mixed. See `docs/research/ergonomic-minima.md` §5.2.

## Alternatives rejected

**A 50 mm solve grid.** Makes the congruence vacuous — `t_int = 100 ≡ 0 (mod 50)`,
so every multiple of 50 is admissible — and makes every derived minimum exactly
representable, including the 1700 mm bath. Rejected for v1 because **every solver
number on the map was fitted at 250 mm**: the 15 s time limit, τ = 4, the 6.25 s
at 24 rooms, the two-worker floor. Trading a measured configuration for an
unmeasured one buys correctness we can already obtain by not rounding. The map's
*"whether the solve grid should be finer than 250 mm"* patch now has this ADR's
arithmetic as one more input — **and a measured cost of staying at 250 mm**: the
5-room case, the bottom of C13's promised band and the commonest dwelling size in
the corpus, is currently paying for it.

**A 125 mm grid.** Halves the rounding loss and still leaves the bath
unrepresentable — the lattice is `≡ 25 (mod 125)`, so 1700 becomes 1775. Pays most
of the re-measurement cost for part of the benefit.

**Round the wet rooms down anyway.** Publishes a `wc` floor of 900 × 1150 and a
`bathroom` floor that cannot hold a bath. Rejects almost nothing real and needs no
change anywhere — and it is the option that quietly stops the ergonomic minimum
being derivable from fixtures at all, leaving a number with a derivation-shaped
story and no fixture behind it.

## Consequences

- **The standards table's two arithmetic constraints now apply to different
  layers.** ADR 0004's even-thickness rule is global. ADR 0007's congruence rule
  is a **region-profile ship gate only**. C15 must be read that way.
- **The solver must post minima in millimetres, not grid units**, for the
  ergonomic layer. The toy harness's `minima_are_clear_grid` reading stays correct
  for profile numbers.
- **A finer grid becomes strictly easier to adopt later, never harder.** Nothing
  published here is snapped to 250 mm, so changing the grid changes no published
  minimum — which is the opposite of the position ADR 0007 alone would have left
  us in.
- **The exemption is *not* a licence to ignore the erosion.** `clear = grid·w −
  t_int` still governs; the solver still pays `⌈(m + t)/grid⌉`. What changes is
  only that we no longer move the *published* number to make that ceiling land
  flat.
