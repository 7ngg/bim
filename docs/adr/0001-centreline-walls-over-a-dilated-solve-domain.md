# Centreline walls over a dilated solve domain, in integer millimetres

The solver places room rectangles that **tile exactly** — shared edges have zero
width — and real walls occupy space. The research note that established the solver
formulation named this mismatch *the largest open risk on the architecture*. We
reconcile it by choosing what the tiling is a tiling **of**: the solver tiles a
**solve domain** equal to the interior clear region **dilated outward by half an
internal wall thickness**, which makes every edge of the tiling a wall centreline
and lets a single uniform erosion recover the real rooms.

## The construction

- `t_int` is the internal partition thickness, `t_ext` the external.
- Solve domain = interior clear region dilated outward by `t_int / 2`.
- Rooms tile that domain exactly, exactly as measured.
- Interior tiling edges are internal wall centrelines; bodies straddle `± t_int/2`.
- A tiling edge on the domain boundary sits at exterior-inner-face + `t_int/2`, so
  eroding `t_int/2` lands it precisely on the exterior wall's inner face — **for
  any `t_ext`**.
- Therefore: **clear room rect = solved rect eroded by `t_int/2` on all four
  sides.** One rule, no special case for perimeter rooms.
- The exterior wall body is authored from the Envelope, outside the domain. It
  never participates in the tiling.

The point of the dilation — and the reason it looks arbitrary until you see it —
is that it makes the perimeter case and the interior case the *same* case. Without
it, a room's erosion depends on which of its sides happen to land on the boundary,
which is a solve-time variable.

Structurally the measured formulation is **unchanged**: same variables, same
`AddNoOverlap2D`, same soft-coverage amendment. Only constants move.

## Considered options

- **Carry thickness as a solve variable.** Rejected: it needs walls as
  first-class solver objects, and the only thickness genuinely unknown before the
  solve is internal load-bearing versus partition — which is structural, and
  structural is out of scope for v1.
- **Solve on inner faces, wall bodies in the gaps.** Rejected as a distinct
  option, because it is not one: inflate each room by `t/2` per side and require
  the inflated rects to tile, and you have written this decision with worse
  bookkeeping.
- **Floating-point metres.** Rejected: it turns "junctions closed, no gaps, no
  overlaps" — an acceptance predicate — into a tolerance question. Integer
  millimetres make it integer equality and delete a family of tolerance decisions
  from the validator spec rather than answering them.

## Consequences

1. **Minimum dimensions inflate by `t_int` per axis**, posted as
   `w_cells >= ceil((min_clear + t_int) / grid)`. Rounding up to the grid is
   conservative by under one cell.
2. **Wall faces sit off-grid** at `± t_int/2`, and that is fine — the grid
   constrains the *solve*, the model is millimetres. **No grid change is needed**,
   which retires the research note's worry that 100 mm might be forced by real
   wall thicknesses.
3. **The door contact threshold is `structural opening width + t_int`** — not leaf
   width, not clear width. A centreline contact of length L yields a clear run of
   `L − t_int`, half a perpendicular wall eaten at each end.
4. **Area constraints must be posted on eroded dimensions, in millimetres.** This
   is the one genuine perturbation: operands move from ~10² to ~10⁴ and products to
   ~10⁸, and area products are already the formulation's flagged weak spot. It must
   be re-measured, not assumed — that is *Solver timing variance sweep*'s job.
5. **Uniform `t_int` is load-bearing, not a simplification.** The single erosion
   constant is what makes the cheap form (`erode(rect, t_int/2)`) exactly equal the
   real definition (the polygon bounded by surrounding wall inner faces). Vary
   internal thickness per wall and the cheap form is silently wrong. The validator
   asserts the two agree, so the day it stops being true we find out.
6. **Two exports declare two different units, from one model.** DXF at 1 unit =
   1 mm with `DIMLFAC = 1.0`, which neutralises the shipped-dimstyle trap that
   prints a 4000 mm wall as "400000". IFC declared in **metres**, which is also the
   only unit under which `add_door_representation` does not emit a schema-invalid
   negative extrusion depth.
7. **Walls export as centrelines offset by `t/2` *and* with
   `OffsetFromReferenceLine = -t/2`**, so the geometry and the IFC semantics agree
   instead of relying on importers honouring the attribute. Winding is recorded,
   because it selects which side of the line the material occupies.
