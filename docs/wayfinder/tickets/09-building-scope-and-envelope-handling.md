---
id: 9
title: Building scope and envelope handling
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
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
