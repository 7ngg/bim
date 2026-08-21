---
id: 26
title: H8 and the single-aspect flat
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: [19]
writes:
  - data/acceptance/rules.json
  - docs/spec/acceptance-bar.md
---

# H8 and the single-aspect flat

## Question

**Acceptance rule H8 — every habitable room touches an exterior wall over a
window's width — forbids the single-aspect flat above six rooms, and no amount of
solver, seed, τ or time limit changes that.** Decide what v1 does about it.

*Solver timing variance sweep* proved it arithmetically rather than
observing it. Habitable rooms do not overlap, so the stretches of exterior wall
they occupy are disjoint, and each consumes at least its own shorter minimum
dimension. That gives a necessary condition with no search in it:

```
sum over habitable rooms of min(min_w, min_h)   <=   total exterior run
```

| rooms | habitable | need (mm) | one exterior edge gives | verdict |
|---:|---:|---:|---:|---|
| 6 | 4 | 8 500 | 9 000 | ok, 500 mm slack |
| **7** | 5 | 10 500 | 9 500 | **dead by 1 000 mm** |
| 8 | 5 | 10 500 | 10 000 | dead |
| 12 | 7 | 14 500 | 13 000 | dead |
| 24 | 14 | 28 250 | 18 000 | dead by 10 250 |

`experiments/solver-toy/frontage.py`. The numbers are from the placeholder
standards table, which is why this is blocked on *Ergonomic minima and the
constraint table's missing half* — the real minima move the threshold, but they
cannot move it far, because the arithmetic is dominated by *how many* habitable
rooms a Brief names, not by 100 mm here or there.

**This is not an exotic case.** *Acquire the datasets* measured the exposure
distribution over 569 real Swiss dwellings: p25 is **0.23**, which is what
`flat_single_aspect` models. Roughly a quarter of real flats have this little
frontage, and the median dwelling holds 6.8 rooms — so the failing region is
adjacent to the corpus centre, not out in a tail.

The decision is not obviously any of these, and that is why it is a ticket:

1. **Relax H8 by room type.** A kitchen or a study on an internal wall is common
   and legal in much of the world; a bedroom without a window generally is not.
   H8 currently treats all five habitable types identically. Which types actually
   require frontage, and does that come from the same source as the minima?
2. **Relax H8 by count rather than by type** — e.g. every *bedroom* plus the
   living room needs frontage, the rest may borrow. This is closer to how the
   regulations that do exist are written.
3. **Bound the promise instead.** State that single-aspect dwellings above N rooms
   are out of v1's envelope, the way *The room-count envelope v1 promises* bounds
   the count. Cheap and honest, but it declines the corpus p25.
4. **Let the Envelope absorb it.** A single-aspect flat with 7+ rooms in the real
   world usually has a re-entrant light well — which ADR 0003's notch model can
   already express, and which *does* add exterior run. Whether real single-aspect
   flats solve the problem this way is measurable in Swiss Dwellings and nobody
   has looked.

Note the interaction with *Acceptance validator spec*, which made the hard rule
set **region-free** on purpose: whatever is decided here changes what is
*rejected*, so it cannot be pushed into a region profile without reopening that.

Also note what this ticket is **not**. *Solver timing variance sweep* closed the
adjacent rider: the three Swiss dwellings measuring ~0.00 exterior are annotation
fragments (6 rooms in 14.1 m²), not windowless homes, so H8 is not rejecting homes
that exist. The problem is specifically the 7-plus-room single-aspect flat, which
is real and which H8 forbids.

Deliverable: a decision recorded against `data/acceptance/rules.json`'s H8 entry
and `docs/spec/acceptance-bar.md`, plus whatever the Envelope model owes if
option 4 wins.

## A gap left open by *Rectangularising real rooms*

The corpus conversion (ADR 0008) preserves every real adjacency and every
separation direction, and it says **nothing about H8**. The fit does not know
which Envelope edges are exterior and which are party, so what it measured is
**boundary contact** — did a room that touched the Envelope's edge still touch it —
not window frontage. A room can keep its boundary run and have kept the *party*
side of it.

So: **whether the converted corpus still satisfies H8 is unverified**, and this
ticket should not assume it does. That matters here specifically, because
`flat_single_aspect` is arithmetically dead from 7 rooms and the corpus p25 is
0.23 exterior — if the conversion quietly moves habitable rooms off the exterior
run, the corpus will look worse against H8 than the real dwellings are, and the
fix would be aimed at the wrong thing.

The exposure machinery to close this already exists:
`experiments/corpus-smoke/exposure_swiss_dwellings.py` recovers the per-dwelling
exterior/party ring from the building hierarchy (*Acquire the datasets* §1.5,
150 floors, 569 dwellings). Joining it to the converted tiling is the measurement.
