---
id: 17
title: Area measurement convention
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: [14]
---

# Area measurement convention

## Question

Graduated from **Not yet specified**, which held it as *"minimum areas are not
comparable across regions even after unit conversion, because German Wohnfläche,
UK GIA and the IPMS family count differently — too diffuse to ticket yet."*

*Canonical geometry model* sharpened it into something answerable, by accident and
then on purpose: it defined a **Space** as *the polygon bounded by the inner faces
of the surrounding walls*, and made its area exactly computable. That is no longer
a vague worry — **we have silently adopted one measurement convention**, and this
ticket names which, and decides what travels with it.

Settle:

1. **Which published convention the inner-face polygon actually is**, per region.
   It is close to a net internal area, but "close to" is what this ticket exists to
   eliminate. Name it against IPMS, the RICS Code of Measuring Practice, GIA, and
   Wohnflächenverordnung.
2. **What the Brief's target area means.** A Homeowner saying "about 90 m²" is
   using a convention they have never heard of, probably whatever their local
   property listings quote — which is Wohnfläche in Germany and something else in
   England. If the Brief's number and the Plan's number use different conventions,
   the system is wrong in a way no validator currently catches.
3. **Whether an area value carries its convention everywhere it travels.** The
   original fog note's worry, and it is a real one: it touches the geometry model,
   the Brief and the validator at once. A tagged quantity type, or a single
   convention fixed per project?
4. **What the exports declare.** IFC has `Pset_SpaceCommon` / `Qto_SpaceBaseQuantities`
   with defined semantics; a room tag on a drawing quoting a different number from
   the IFC quantity is exactly the sort of defect a Practitioner notices first.
5. **Whether the deductions matter at v1 scale** — Wohnfläche discounts sloped
   ceilings and counts balconies at a fraction; those are the rules that make the
   conventions actually diverge rather than merely differ in name. Single-storey
   scope may make most of them moot, which would be a welcome finding, but it needs
   checking rather than assuming.

The reason this cannot be deferred much further: **the numbers in
`data/standards/room-constraints.json` are minimum *areas*, and they were sourced
per region.** If they are not all in the same convention as the Space areas the
validator computes, the acceptance bar is comparing two different quantities and
will do so silently.

Waits on *Which region profiles ship in v1*, since the conventions are regional
and the answer is scoped by which regions actually ship.

Deliverable: the convention named per region, the tagging decision, and an
explicit statement of what the Brief's area number means to a Homeowner.

## Inherited from *Dimensioning and annotation rules*

This ticket now has a **third consumer that quotes the number in public**, and one
rule that follows its answer rather than keeping its own.

- The area appears in three places on an issued drawing: the **room tag**, the
  **room schedule** on sheet `A-102` — which also states the Envelope inner area
  and the difference, so a Practitioner can reconcile the schedule against the
  plan — and the title block's **`AREAS`** attribute, which names the convention in
  words. Question 3 ("does an area carry its convention everywhere it travels")
  therefore has at least one answer already: **on the drawing it is declared once
  in the title block, not per tag.**
- **ADR 0004's tier-1 overall follows this ticket.** Tier 1 spans the footprint
  and currently measures a party edge **to its centreline**, chosen because GIA and
  IPMS both do. If this ticket lands on a convention that treats party walls
  differently, tier 1 changes with it — one drawing must not quote a footprint on
  one convention and an area on another, and that is a defect a Practitioner spots
  before anything else.
- A drawing is also the artefact that makes question 2 concrete. A Homeowner
  reading `16.06 m²` on a plan they asked to be "about 90 m² total" is comparing
  our number against a listing convention they have never named.

## Inherited from *Which region profiles ship in v1*

**Item 5 is checked, and the answer is the welcome one it hoped for.** The
deductions that make Wohnfläche, GIA and the IPMS family genuinely diverge —
part-height ceilings discounted at 50%, balconies at 25–50% — **cannot fire in
v1**, because v1's geometry model contains **no ceiling height and no balcony**.
Neither term appears anywhere in `CONTEXT.md` or in *Canonical geometry model*.
So this ticket is not choosing between four conventions that disagree; it is
naming one, in one region.

**One region, not several.** ADR 0006 ships exactly one selectable profile, `AZ`,
so item 1's "per region" collapses. The live pair is the post-Soviet one —
*общая площадь* (total) against *жилая площадь* (living) — which is a real
distinction with real consequences for what a room tag prints and what
`Qto_SpaceBaseQuantities` declares, and it is now the only one in scope. `UK` is
retained only as a test fixture, so GIA still needs naming *for the fixture*, not
for a user.

**Item 2 gets sharper, not easier.** A Homeowner saying "about 90 m²" is quoting
whatever their local property listings quote. Under the AZ profile that is
*общая площадь*, which counts differently from the inner-face polygon a **Space**
is defined as. Naming the convention is exactly what stops the Brief's number and
the Plan's number silently disagreeing.

**The pair itself belongs here, not to the profile ticket.** *The Azerbaijani
region profile* is instructed to surface the two terms and hand them over rather
than decide between them.
