# thickness-fidelity

Harness for *One internal thickness, against a corpus that has no module at all*
(ticket 33). Findings live in `docs/research/single-internal-thickness.md`.

Corpora come from `data/corpora/`, which is gitignored — see
`docs/research/dataset-inventory.md` to acquire them. Outputs go to `out/`, also
gitignored; regenerate by running the scripts.

| script | what it does | runtime |
|---|---|---|
| `extract.py [stride]` | one streaming pass over `geometries.csv`; caches rooms, non-room areas and walls for a 1-in-`stride` FLOOR sample plus every floor `swiss_fit.json` already fitted | ~25 s |
| `measure.py [n]` | classifies every wall as internal-to-a-dwelling or boundary by perpendicular probing, and measures both the wall body and the Space-to-Space gap | **~48 min** for 14,857 dwellings |
| `analyse.py` | the four ticket items; writes nothing, redirect it to `out/analysis.txt` | seconds |
| `verify_prior.py` | reproduces *Which region profiles ship in v1*'s exact statistic on a different sample (C11), then splits it internal / boundary | ~3 min |
| `resplan_thickness.py [n]` | the second corpus's wall depth, and the fact that its schema holds only one per plan | ~2 min |
| `reprice.py` | item 3's three arithmetic terms, off `room-constraints.json` | instant |
| `draw_compare.py [n] [seed]` | item 1's looking question: each dwelling drawn three ways — as surveyed, uniform at its OWN median internal thickness, uniform at `t_int`. The middle panel is what separates *uniformity* from *thickness* | seconds |
| `classify_check.py [n] [seed]` | draws the internal/boundary classifier in red and black, and prints the per-wall table, so the classification can be checked rather than trusted | seconds |

Order: `extract.py` → `measure.py` → everything else. `reprice.py` and
`resplan_thickness.py` are independent of both.

`measure.py` writes only at the end and holds every record in memory (~600 MB at
the 1-in-10 stride). It re-scans every wall on a floor once per apartment on that
floor, which is where the runtime goes; indexing per floor instead would be about
4x faster and was not worth the rewrite mid-study.

## Read-only on the profile

Ticket 33 declares itself read-only on `data/standards/room-constraints.json`.
Nothing here writes to it; `reprice.py` reads it and never opens it for writing.

## Two things that will bite whoever runs this next

**The prior's thickness census mixes internal and external walls.**
`experiments/corpus-smoke/wall_thickness_swiss.py` measures the minor side of
every `separator/WALL` polygon. A dwelling's exterior and party walls are in
there, and they are two to three times a partition. Any statement of the form
"`t_int` sits at the corpus p*N*" that quotes those percentiles is comparing an
internal thickness against a mixed population. `verify_prior.py` reproduces the
prior's number and then splits it.

**A corpus room polygon is not offset from its wall.** The Space polygons sit on
the wall body's own faces to within 1 mm a side, so `gap - t_mrr` has a mode at
exactly 2.0 mm. Swiss Dwellings therefore records **one** plane and no finish
layer at all. Do not read its thicknesses as either "structural" or "finished" —
the distinction does not exist in the file.
