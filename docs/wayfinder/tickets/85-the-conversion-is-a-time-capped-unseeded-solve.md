---
id: 85
title: The conversion is a time-capped, unseeded solve and every corpus figure rests on it
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: []
writes:
  - experiments/rectangularise/
  - docs/research/rectangularisation.md
---

# The conversion is a time-capped, unseeded solve and every corpus figure rests on it

## Question

**ADR 0043 established that a measurement keyed to nothing is not reproducible, 82
measured what that costs in the warp, and 83 is closing the last salted site. The
same defect is upstream, in the conversion, and nobody has looked at it.**

`experiments/rectangularise/fit_rects.py`:

```python
s.parameters.max_time_in_seconds = time_limit    # TIME_LIMIT = 10.0
s.parameters.num_search_workers = WORKERS        # WORKERS = 4
```

**No `random_seed`.** Four racing workers with no seed means a non-unique
optimum — and a tiling problem is full of them — returns a different cover per
process. That reaches `OPTIMAL` records, not only capped ones. And **16,0 % of
converted dwellings return `FEASIBLE`**, where the cap stopped the search; those
dwellings contribute **41,2 %** of all two-part Rooms.

The shipped solver rig *is* seeded (`SolveConfig(..., seed=sd)`). The conversion
alone carries this.

⚠️ **`salt_check.py` cannot see it.** It scans `ROOT.rglob("*.py")` — the whole
repo, so `fit_rects.py` is in scope — and reports nothing, because it looks for
the `hash()`-salting pattern and this is a different one. The check that exists to
catch this family is blind to its second instance. `salt_check.py` lives in
`experiments/warp/`, which **62 and 67 claim**, so this ticket may note that and
not extend it.

## How it surfaced, which is the whole argument for taking it

*A two-part Room is a T or a Z as often as it is an L* re-measured the shape
distribution and got **1 543** two-part Rooms where ADR 0041 published **1 535**
from an earlier run of the same rig — L 851/847, T 334/332, Z 331/329, rect 27/27.
**No population filter reconciles the 8**: status, room-count band and gate
filters all return 1 543. Two runs, one input, different answers.

**Every corpus number on this map is quoted from `swiss_fit_k2.json` or its
siblings** — ADR 0014's 52,9 / 77,8 / 87,6 % and its 87,2 % coverage figure, ADR
0020's notch spans, ADR 0041's part counts, the area bands, ADR 0045's whole §8.

## What has to be done

1. **Seed it, and separate the two mechanisms.** Add `random_seed` and re-run a
   sample varying **seed at fixed cap** and **cap at fixed seed**, independently.
   ⚠️ Doing only the cap arm attributes both mechanisms to one — the error 82
   caught in the warp. At **0,78 s/dwelling** a 400-dwelling arm is about five
   minutes per cell.
2. **Report which published figures move, and by how much.** The deliverable is a
   drift band per quoted figure, not a verdict. A figure that moves inside its own
   quoted precision needs nothing; one that does not needs restating at its
   source.
3. **Decide the shipped cap and worker count for the conversion**, and whether the
   index is regenerated or the existing one is kept with a stated band. Note the
   asymmetry: regenerating invalidates every figure already published against the
   current file, including 85's own baseline.
4. **Decide whether `salt_check.py` grows a determinism check** — unseeded
   multi-worker CP-SAT is a second pattern in the same family — or whether that
   belongs to `env_check.py`. Do not edit `salt_check.py` here; 62 and 67 claim it.

## What is already known, so it is not re-derived

- **The distribution is stable where the records are not.** Not-L is **44,8 %**
  pooled and **43,1 %** over the 907 proved-optimal Rooms; cap-hit dwellings are
  T/Z-richer at **47,3 %**, so a longer cap moves the headline **down**, bounded
  at 43,1 %. ADR 0045 published every figure on both planes for this reason and
  none of its conclusions moves.
- **Status counts on the current file**: OPTIMAL 1 946, FEASIBLE 371, INFEASIBLE
  242, UNKNOWN 33, ROOM_LOST_IN_RASTER 8. Only the first two carry `parts`.
- **This is not 83.** 83 is `hash()` salting in `experiments/plane-accounting/`
  and `experiments/solver-toy/`; this is worker nondeterminism plus a wall-clock
  cap in `experiments/rectangularise/`. Different rigs, different mechanisms,
  neither blocks the other.

## Raised by

*A two-part Room is a T or a Z as often as it is an L* (2026-08-31), ADR 0045
consequence 3.
