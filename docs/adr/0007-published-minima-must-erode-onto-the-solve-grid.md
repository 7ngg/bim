# ADR 0007 — a published minimum must erode onto the solve grid

**Status:** accepted
**Date:** 2026-08-19
**Ticket:** *Solver timing variance sweep*
**Supersedes:** nothing. **Constrains:** *Ergonomic minima and the constraint
table's missing half*, *The Azerbaijani region profile*.
**Related:** [ADR 0001](0001-centreline-walls-over-a-dilated-solve-domain.md),
[ADR 0004](0004-published-dimensions-measure-wall-faces.md)

## Decision

**Every dimensional minimum published in a region profile must satisfy**

```
minimum_mm + t_int  ≡  0   (mod grid_mm)
```

**for every internal wall thickness `t_int` the profile offers.** At the v1 grid
of 250 mm and `t_int = 100`, admissible minima are 1650, 1900, 2150, 2400, 2650,
2900 … — not 1750, 2000, 2250, 2500.

A minimum that fails the rule is not merely inelegant. It silently costs a whole
grid unit on the room dimension it governs, and the cost compounds per room.

## Why

ADR 0001 makes a room's published rect the **clear** rect, `erode(solved, t_int/2)`.
So a published minimum width binds as

```
clear_w = grid·w − t_int  ≥  minimum_mm
     ⟺   w  ≥  (minimum_mm + t_int) / grid
```

and `w` is an integer. When `minimum_mm` is itself a multiple of the grid — which
is the natural way to write a round number, and what every value in the current
placeholder table does — that ceiling lands **one whole grid unit** above
`minimum_mm / grid`. The room grows by 250 mm in each axis to pay for a 100 mm
wall, and 150 mm of that is pure rounding loss.

The rooms still have to tile the Envelope exactly (H3). Exact tiling has no slack
to give, so the loss does not shrink the rooms' comfort margin — it removes
tilings from the feasible set outright.

### Measured

`experiments/solver-toy/erosion_cost.py` and `grid_aligned_minima.py`, 3 seeds,
9.65 m² of interior per room, exact tiling achieved / seeds:

| reading | n=4 | n=5 | n=6 | n=7 | n=8 | n=10 | n=12 |
|---|---|---|---|---|---|---|---|
| minima on the solved rect (pre-ADR-0001) | 3/3 | 3/3 | 2/3 | 2/3 | 3/3 | 2/3 | 3/3 |
| minima on the clear rect, **unaligned** | 0/3 | 0/3 | 0/3 | 2/3 | 3/3 | 2/3 | 3/3 |
| minima on the clear rect, **grid-aligned** | 3/3 | 3/3 | 2/3 | 2/3 | 3/3 | 2/3 | 3/3 |

The unaligned middle row **deletes 4-, 5- and 6-room dwellings entirely** — no
Brief could even be constructed — which is the bottom half of the 4–10-room band
C13 promises and the commonest dwelling sizes in the corpus. The aligned row is
indistinguishable from the pre-ADR-0001 baseline: **the erosion becomes free.**

## Alternatives rejected

**Give the Envelope more area.** Swept from +0 % to +40 % interior area per room.
Four rooms never recovers, and the response is not even monotone — 4 rooms passes
2/3 at +10 % and 0/3 at +15 % — because the Envelope's bounding box re-snaps to
the 250 mm grid as area changes. The defect is arithmetic, so area cannot buy it
off, and pretending otherwise would inflate every dwelling the engine draws.

**Use a finer solve grid.** A 125 mm grid halves the rounding loss and a 50 mm
grid removes it for `t_int = 100`. But the grid is the solver's search space and
ADR 0001 chose 250 mm deliberately; the ticket-15 sweep did not re-measure solve
time at a finer grid, so trading a measured cost for an unmeasured one is not
available. Left open — if the grid ever changes, this ADR's arithmetic changes
with it and the standards table must be restated.

**Let the coverage slack absorb it.** This is what happens if nothing is done, and
it is the worst option: the solver returns `OPTIMAL` while paying slack, which
means a Plan with unassigned interior floor that the acceptance validator then
rejects on H3. A provably-optimal invalid answer is the shape of failure hardest
to notice.

## Consequences

- **The standards table now carries two arithmetic constraints, not one.**
  ADR 0004 requires every wall thickness to be an even number of millimetres so
  that `t/2` stays integral. This ADR requires every dimensional minimum to be
  congruent to `−t_int` modulo the grid. Both are checks a region profile must
  pass before it ships, and both are cheap to assert in a test.
- **Published minima drop by `t_int` against the number a source quotes.** A
  source specifying a 1750 mm kitchen is honoured by publishing 1650 mm clear —
  because the source's number was a centreline-to-centreline or nominal figure
  and 1650 is what the occupant can actually tape. This is the same move ADR 0004
  made for dimensions and should be documented the same way, in the profile's
  provenance field, so nobody later "corrects" 1650 back to 1750.
- **A profile offering more than one `t_int` must satisfy the rule for each.** With
  `t_int ∈ {100, 200}` at a 250 mm grid, admissible minima are congruent to 150
  and to 50 modulo 250 respectively — which have no common solution, so a profile
  with two internal thicknesses needs either per-thickness minima or a grid that
  divides their difference. This is a real constraint on
  *The Azerbaijani region profile*, which ships its catalogue empty on purpose.
- **The toy harness enforces it.** `scenarios.fits_kind(rect, kind, clear_t)` takes
  the reading as a parameter, so the ground truth is generated against whatever
  the solver will enforce. Before this, the two disagreed and the harness's
  guarantee that every Brief is known-feasible silently stopped holding.
