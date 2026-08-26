---
id: 50
title: A statutory floor, posted soft, in the one region v1 ships
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - data/acceptance/rules.json
  - docs/spec/acceptance-bar.md
  - CONTEXT.md
---

# A statutory floor, posted soft, in the one region v1 ships

## Question

**C14 says a region profile never rejects a Plan. AzDTN 2.7-2 fixes habitable-room
and kitchen areas by law. Both cannot be honoured, and today the law loses.**
Decide which one moves, or decide deliberately that neither does.

The hard bar binds against the **region-invariant ergonomic layer**, which is
fixture-derived. The region profile carries *soft* targets. So in the only region
v1 ships:

| | AzDTN, `verified`, statutory | hard floor actually enforced |
|---|---|---|
| living room, 2+ rooms | **16.0 m²** (cl. 5.7) | 3.7 m² |
| `bedroom_double` | **10.0 m²** (cl. 5.7) | **3.1 m²** |
| `bedroom_single` | 8.0 m² | 2.2 m² |
| kitchen | 8.0 m² | 1.8 m² |
| glazing ratio | **1:8** (cl. 9.13), mandatory | `win.area_ratio`, **soft** |

`win.area_ratio` is **the only statutory minimum on the map posted soft**.
*Opening placement rules* §10 flagged it and declined to move it; *H8 and the
single-aspect flat* held it soft for the same reason and ticketed it here: C14
names it explicitly — *"two soft area targets and one soft window fraction"* — so
changing it is amending a standing constraint, and neither of those tickets was
the right door.

## Why this is not merely tidy

The engine can emit a `bedroom_double` of **1.85 × 1.68 m = 3.1 m²**, clear every
hard rule, and be shown to a Homeowner as a survivor. `min_clear_short` 1650 is
derived as *double bed 1350 × 1900 + body zone 300 to one side* — a **fits** floor,
not a **habitable** floor. AZ's own market default for a habitable room's clear
width is **3 000 mm**; 19.3 % of real Swiss rooms sit below it.

C6 makes the bar a hard filter and the objective a ranking, so the defence is *the
soft objective pulls rooms to `target_area`*. That defence has two holes worth
pricing:

1. **A survivor is shown.** C6's contract is generate-many-reject-most-show-
   survivors, and `homeowner_surface.no_survivors` insists a failing Plan is never
   shown precisely because a Homeowner cannot judge a defective plan. A 3.1 m²
   bedroom is not annotated as defective — it *passed*.
2. **The pull is weakest exactly where it is needed.** `area.invented_envelope_hard`
   pins total floor only where the Envelope is *invented*. Where a Homeowner states
   a small Envelope, the hard minima are the whole story.

## The three ways out, and none is free

1. **Amend C14 to "a region profile may raise a floor, never lower one."** The
   reject set becomes region-dependent, which C14 was written to prevent — but the
   argument it was written on is *"a region we have never surveyed still gets a
   defensible hard bar"*, and C12 ships exactly one profile. Cost: reopens
   *Which region profiles ship in v1*, and `UK` as a test fixture stops being a
   free choice.
2. **Raise the region-invariant ergonomic floor.** Region-clean, but it asserts a
   habitability number the fixture derivation does not support and C8 forbids
   sourcing from Neufert. Cost: a number nobody can cite.
3. **Leave the floor and fix it in the objective**, e.g. a `warn` at the statutory
   figure so the Homeowner sees it. Cheapest, and it declines to reject a plan that
   is illegal in the region it is drawn for.

⚠️ Read together with *What a room's area is allowed to be*, which set the
**maximum** side of this and chose `target_area` as the anchor; and with the
`is_habitable`/`needs_window` invariant, which is what the retired
`win.habitable_touches_exterior` was mistaken for.

⚠️ **C8 cuts both ways here and the ticket should say which.** C8 forbids claiming
code compliance. It does not forbid *being* compliant, and shipping a 3.1 m²
bedroom into a market whose law says 10 is the failure C8 exists to prevent in the
other direction.

## Deliverable

A decision recorded against C14 on the map, `win.area_ratio`'s severity in
`rules.json`, and — if the reject set moves — a line in `acceptance-bar.md` §3,
whose whole argument is that the hard set carries no region.
