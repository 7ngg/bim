---
id: 85
title: The conversion is a time-capped, unseeded solve and every corpus figure rests on it
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
blocked_by: []
writes:
  - experiments/rectangularise/
  - docs/research/rectangularisation.md
  # declared on resolution, all unclaimed at the time:
  - docs/adr/0046-the-conversion-is-reproducible-where-it-is-published.md
  - docs/adr/0045-shape-is-arrangement-and-the-contract-admits-every-shape-two-parts-make.md
  - docs/research/room-rectangles.md
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
## Resolution

**The conversion is reproducible where it is published once it runs on one
worker, the ticket's named mechanism was not a mechanism, and the index is not
regenerated for this.** ADR 0046; `rectangularisation.md` §16.

### The premise, corrected — and the correction changes the fix

**CP-SAT's own default `random_seed` is 1.** Asserted against the pinned build in
`determinism.selftest`, not read off documentation. The rig was never unseeded and
`random_seed = 1` is a no-op. The seed arm proves it empirically: varying the seed
to 7 gives disagreement indistinguishable from running seed 1 twice (cover 103 vs
95, shape 16 vs 17, status 8 vs 9). **A defect caused by a race is not repaired by
keying a draw** — and had only the seed arm been run, its 103 disagreements would
have "confirmed" the premise and shipped a fix that changes nothing.

Two of the ticket's own figures were also wrong in a way that mattered to
planning. **0,78 s/dwelling is the k1 rig**; the k2 rig that produced
`swiss_fit_k2.json` runs at **3,3–3,9 s/dwelling**, so a 400-dwelling arm is
~25 min, not five. Eleven arms were run, serially, over about five hours.

### What was measured

Four configurations, on one 400-dwelling paired key list (60 for the probes):

| config | cover ≠ on repeat | shape class ≠ | mean wall | UNKNOWN |
|---|---:|---:|---:|---:|
| shipped — 4 workers, 10 s wall | **95 / 358** | **17 / 227** | 3,3 s | 3–6 |
| **1 worker, 10 s wall** | **1 / 366** | **0 / 243** | **3,31 s** | 3 |
| 4 workers, `interleave` + det 8 | 5 / 50 | 0 / 26 | 6,6 s | 6 |
| 1 worker, det 10 / det 30 | — | — | 9,4 s / **30,3 s** | 5 / 0 |

**One worker takes cover disagreement from 26,5 % to 0,27 % at identical wall
cost** (3,31 s against 3,28–3,33) and a marginally better conversion rate (0,9244
against 0,9219–0,9239), for ~5 proofs in 400. Both single-worker runs report the
published plane identically to every digit.

**`WORKERS = 4` was imported from a regime this rig cannot enter.** Its comment
cites *"ticket 15: two workers is a floor for correctness"*, measured on the
**shipped projection at 24 rooms**; the conversion corpus is filtered to the 3–10
engine-room band and tops out at **10 rooms**, so the justifying condition occurs
in **0,000 %** of inputs. A citation records where a number came from, not that it
still applies.

**ADR 0043's consequence 8 is discharged, negatively.** `interleave_search` costs
1,85× the wall time, loses three proofs in sixty, drops the wall bound entirely,
and **still returns different covers — three of them on records both runs proved
OPTIMAL at an identical objective**. That is google/or-tools **#3948**, cited by
ADR 0043 from the tracker and unconfirmed in this repo until now.

**And ADR 0043 decision 3's own config does not transfer.** One worker plus
`max_deterministic_time` was free in the warp (1,34 s against the wall cap's
1,35 s); here it is **2,6×** at budget 10 and **8,4×** at budget 30, with a
145 s tail — because those models finish inside the budget and these do not.

### Where the instability actually is, which is not where the ticket looked

**Split by proof status, the pooled rates fall apart — and the mechanism inverts.**

| rep1 vs rep2 | records | cover ≠ | objective ≠ | two-part Rooms | shape class ≠ |
|---|---:|---:|---:|---:|---:|
| **OPTIMAL** | 307 | 63 | **0** | 139 | **0** |
| **FEASIBLE** | 51 | 32 | 18 | 88 | **17 (19 %)** |

On a proved record the published plane is stable **even at four workers**: the
race swaps tied optima without changing their shape. Every disagreement that
reaches a figure is in the cap-truncated population — which carries **41,2 %** of
all two-part Rooms, the ticket's own number. **So the cap is what reaches the
figures and the race matters mainly because it moves where the cap bites**, which
is the reverse of the emphasis this ticket was raised with, and why decisions 1
and 2 are one decision.

### The drift band

Aggregate, over five runs of the shipped configuration on identical keys: not-L
**sd 0,77 points**, conversion rate sd **0,0011**, two-part per Room sd **0,049
points**, two-part count sd **2,2 Rooms**. **No published conclusion moves.**

⚠️ **A configuration change is a shift, not drift, and it is bigger than the
band.** Four workers and one worker at the same 30 s cap, on the 369 dwellings
both decide to the same quality, give **46,4 %** and **50,2 %** not-L — 3,8 points
against sd 0,77, with zero status and zero part-count differences. Neither is more
correct; the objective does not determine the shape. **Never quote a figure from
one configuration against one from another.** A *systematic* worker preference is
**not** established: the per-Room sign test gives p = 0,021 at 30 s and p = 0,50
with the opposite sign at 10 s.

⚠️ The range on not-L went 0,58 points at four runs to 2,08 at five — quote the
**sd**, not the range. Four realisations understated the spread ~2×, which is why
ADR 0043's *"N runs, as a distribution"* is not ceremony.

**ADR 0041's 1 535 against 1 543 is reconciled and needed no filter.** It is
0,52 % relative against a two-part count sd of 0,91 % relative — **~0,6 sd**, an
ordinary and smaller-than-typical draw. ⚠️ And it is mostly *population churn*,
not Rooms changing shape: only 2–3 Rooms per pair change part count, while the
decided population moves by up to 28 Rooms as marginal dwellings flip in and out
at the cap.

### Two published claims corrected at source

**ADR 0045 consequence 3 and `room-rectangles.md` §8.6** both asserted a
proved-optimal *floor* of 43,1 %. **Struck.** *"Proved optimal at 10 s"* is not a
fixed population — it is the **easy** dwellings, and raising the cap moves
T/Z-rich ones into it: the 41 dwellings newly proved at 30 s carry **51,5 %**
not-L against **41,8 %** for those already proved. The two planes converge
(47,7/41,1 % at 10 s to 46,4/**45,0 %** at 30 s) rather than the pooled falling to
the optimal-only. The convergent value is **~45–46 %**, above the struck bound and
above the published 44,8 %, so **ADR 0045's decision is untouched and mildly
better evidenced than when it was taken.** ⚠️ The 41,8-vs-51,5 contrast alone is
~1,3 sd; the convergence is the robust part.

### The four items

1. **Seeded and separated.** Seed contributes nothing; the race is the whole of
   the run-to-run instability; the **cap is a distinct and larger effect, and a
   bias rather than a band** — 1,3 points directionally against the race's 0,77.
2. **Band published per figure**, above and in §16.5, with the sd-not-range and
   400-vs-2600 caveats stated.
3. **Shipped config decided — `WORKERS = 1`, `TIME_LIMIT = 30.0`, `SEED = 1`,
   applied to `fit_rects.py`. The index is NOT regenerated for this.** One worker
   is byte-identical at 30 s (0 differences of any kind over 369 dwellings and
   2 511 Rooms) and costs nothing; 30 s returns **zero UNKNOWN** for 1,73× the
   wall time — ~4,1 h for the full corpus against 2,6 — which **recovers ADR
   0008's *"decidable, not a timeout"***, recorded as dead on this row.
   `proposer.md` §2.2 already freezes the conversion pending the ADR 0031 frame
   pass, which re-bases the file wholesale and already owes six per-record fields
   on the same run. **This is the seventh item on that pass.** A standalone
   regeneration would spend the whole re-fit cost to invalidate every figure once
   and the frame pass would invalidate them again — the asymmetry the ticket
   named is real and points the other way.
4. **`salt_check.py` does not grow this, and neither does `env_check.py`.** That
   check catches a defect that is static and unconditional; `num_search_workers =
   4` is **correct** in `solver.py` and defended by ADR 0043 decision 4, so a
   pattern firing on both cannot separate them and would go quiet in the OWED
   table beside it. `repeat_check.py` asserts the **behaviour** on the rig that
   claims it, and deliberately does not assert the cover.

