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
