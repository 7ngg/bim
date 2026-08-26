# H8 frontage — the harness behind ticket 26

Three probes. The first re-runs the ticket's own arithmetic against the shipped
standards; the other two are the first evaluation of the window rules against real
dwellings rather than against a toy.

Run everything from the repo root with the pinned interpreter:

```
./venv/Scripts/python.exe experiments/h8-frontage/frontage_shipped.py
./venv/Scripts/python.exe experiments/h8-frontage/window_rules_corpus.py
./venv/Scripts/python.exe experiments/h8-frontage/kitchen_audit.py
```

The two corpus probes stream `swiss-dwellings-v3.0.0/geometries.csv` twice and
take about two minutes each. They use **the same seed and floor count** as
`experiments/corpus-smoke/exposure_swiss_dwellings.py`, so every dwelling here is
one that appears there.

## `frontage_shipped.py`

The ticket's necessary condition — *sum over window-needing rooms of their facade
consumption ≤ total exterior run* — recomputed against
`data/standards/room-constraints.json` instead of `solver-toy/scenarios.STANDARDS`,
which its own comment marks as a placeholder. It imports `solver-toy` for
`envelope_for` and `composition` and **never writes to it**.

Four readings of what a room consumes at the facade, so the choice is visible
rather than assumed:

| rule | binds |
|---|---|
| `B_width` | the Room's `min_clear_short` — whole room at the facade, one rectangle |
| `E_option2` | `max(min_clear_short, window + 2 × jamb)` — **what shipped**, §7.3 |
| `D_leg` | `max(900 leg floor, window + 2 × jamb)` — ADR 0014 relief taken in full |
| `C_window` | window fit alone |

Every figure passes through `realisable()`, which applies ADR 0007/0009 erosion:
a published 1 650 mm floor posts at 1 850 on the 250 mm grid at `t_int` 150.

**Result:** at the shipped layer the first arithmetically dead cell is **n = 16**,
not n = 7. The gap between `B_width` and `D_leg` at n = 7 is 750 mm, which is what
the ADR 0014 alcove was worth and why option 2 costs nothing to take.

## `window_rules_corpus.py`

Per-room evaluation of `win.habitable_has_window` and the retired
`win.habitable_touches_exterior` over 561 real dwellings, on **corrected**
envelopes — the rooms are bridged across their walls before unioning, because
`area` polygons are disjoint and a raw union yields one part per room. It also
sweeps the bridge distance, which is the only judgement the correction adds:
p25/median/p75 hold at 0.51/0.67/0.78 anywhere in 0.10–0.30 m.

**Result:** `has_window` rejects **43.3 %** of real dwellings — 23.0 points on the
kitchen alone, 20.3 on a non-kitchen room. `touches_exterior` rejects 11.9 %, a
subset.

## `kitchen_audit.py`

Written because 31 % windowless kitchens against 9.7 % with no facade at all is
the shape of a measurement error, and the decision turned on it.

**Result:** it is not an error. **Zero orphan windows** — every window on a
dwelling boundary attributes to at least one room — and 1 031 of 3 179 attribute to
more than one, which biases toward *finding* a window. The windowless kitchens are
real rooms (median 6.8 m², not niches) and **84.7 % adjoin a windowed habitable
room**: borrowed daylight, `taxca-metbex`, not a dark box.

## What is deliberately not here

The `exterior`/`party` typing is recovered geometrically, from a 0.45 m gap to the
next occupied area, exactly as `exposure_swiss_dwellings.py` does it. Swiss
Dwellings carries no edge-condition attribute, so this is a heuristic in both
places, and the *H8 and the single-aspect flat* resolution does not lean on it for
anything finer than exterior-versus-not.
