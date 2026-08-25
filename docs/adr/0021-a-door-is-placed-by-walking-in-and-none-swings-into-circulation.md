# A door is placed by walking in, and none of them swings into circulation

*Opening placement rules* had to answer where each Opening goes, and found that
the three rules already shipped do not agree with each other. The solver reserves
`structural opening width + t_int` of shared wall for a door (ADR 0001
consequence 3), which — since `+ t_int` is only the centreline-to-clear
correction — reserves **exactly the structural opening and nothing else**. The
validator then hard-requires, on that same segment, a jamb return of 100 mm per
side (`open.fits_segment`) and a 300 mm nib clear at the leading edge
(`open.leading_edge_nib`). The floor is therefore `w + 400` of clear run, and
hinging at either end of the segment gives the same number.

**A solve could pass `circ.potential_reachability` and be hard-rejected the
moment a door was placed on the run it had just certified.** Nothing on the map
had noticed, because the two constants live in different files and were written
by different tickets.

The obvious repair — give the solver a door-position variable — was rejected.
It makes Openings partly postable, reopens *Acceptance validator spec*'s
enforcement-site table, and spends time on a solver the map already describes as
sitting on the edge of the p95 cliff rather than below it. It is also not what
anyone else does: of the ~20 published generators surveyed in
`docs/research/floorplan-generation-stack.md`, **none emits a wall with thickness
at all**, so none places a door; the commercial tools in
`docs/research/competitive-landscape.md` place openings by rule after the layout.
Post-solve placement is both the cheap path and the industry's path, which is
exactly the coincidence that needs checking rather than accepting.

It survives the check, but only once the reservation is corrected and the
placement rule is written to *use* the correction.

## The decision

Four parts, and they interlock — each one is what makes the next affordable.

1. **The contact threshold becomes `structural opening width + t_int + 400`.**
   A constant, not a new variable: `circ.potential_reachability` keeps its shape
   and 15 s and τ = 4 stand. What changes is that the run the solver certifies is
   now long enough for a **corner-biased** door rather than only for a door.

2. **Doors are placed in breadth-first order from the primary entrance, and each
   one is pushed to the end of its shared run nearest the point the path arrives
   at.** Realised circulation is a tree rooted at the entrance, so the order is
   well defined without a search. This is the rule an architect follows without
   naming it — you place doors as you walk in — and it is what preserves the
   unbroken furniture wall on the far side of the room.

3. **The hinge goes at the corner end the door was pushed to**, so the leaf opens
   back against that wall and both the leading edge and its 300 mm nib fall
   inboard, where there is room for them. Handing is therefore *derived* from
   position, not chosen separately.

4. **A door swings into the more private of the two Spaces it joins, and never
   into circulation.** Fallback is the other side, then rejection. Since exactly
   one door in a dwelling swings into circulation — the entrance door, into the
   hall — Neufert's 1400 mm corridor case cannot arise.

## Consequence: the corridor constant is derived, not assumed

*Canonical geometry model* left a provisional answer here: **pre-size corridors
conservatively from the region profile's worst-case door arrangement**. That is
now **replaced rather than confirmed**, and the replacement is smaller.

Part 4 removes the worst case instead of sizing for it. AD M makes corridor width
a function of the door widths opening onto it; Neufert makes it a function of
swing *direction* — 900 mm where doors open into rooms, 1400 mm where they open
into the corridor. Under part 4 every internal door opens into a room, so the
1400 mm arm is unreachable. The hall must still contain **one** swing footprint,
the entrance door's, which for a 900 mm flat entrance is an 800 mm square
(`leaf = opening − 100`) anchored on the entrance wall — satisfied by a hall
depth of 900.

So **the pre-sizing constant stays at the 900 mm clear floor that *Acceptance
validator spec* posted, and it is now derived from the swing rule rather than
asserted against an unknown arrangement.** Two independent readings agree on
900: this derivation, and the ergonomic floor's `min_clear_short` for `hall`.

## Consequence: the leading-edge nib is re-based, not re-sourced

`open.leading_edge_nib` is `verified` against AD M, whose nib exists so that a
wheelchair user can reach the handle. The `AZ` profile has already refused an
AD M accessibility figure once, on the record — `body_zone` is 300 mm, and its
note says *"NOT 750 mm: AD M's 750 is a wheelchair transfer space, and composing
a private bathroom out of accessibility figures produces a floor that rejects a
third of real homes."* Keeping AD M's 300 while refusing AD M's 750 needs a
reason that is not "we liked this one".

The reason is that the 300 mm **along the wall** is ergonomic before it is
accessible: it is architrave, handle and elbow, and it is what any architect
leaves whether or not the door is ever approached from a chair. The 1200 mm
*depth* it is maintained back into the room is the accessibility half, and it
costs no wall run, so it is kept unchanged rather than defended. The constant
stands; its justification moves from accessibility to the region-invariant
ergonomic layer, which is where the rest of the hard floor already lives.

## What this costs, and who prices it

Part 1 removes contact edges, so INFEASIBLE will rise. The arithmetic behind
`w + 400` is exact — it is two shipped hard rules added together — so the
threshold ships on it, because the alternative is shipping a known
contradiction. The **rate** is a measurement this ticket could not take:
`experiments/solver-toy/` belongs to *What an ordered entry sequence costs the
solver*, and the map's concurrency rule forbids writing into a claimed
directory. It is handed there.

The bite is on short contact runs, which are precisely the runs on which the only
legal door position is mid-wall. If the measurement comes back expensive, the
cases lost are the ones part 2 exists to prevent.
