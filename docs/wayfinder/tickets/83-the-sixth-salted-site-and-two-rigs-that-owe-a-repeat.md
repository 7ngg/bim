---
id: 83
title: The sixth salted site, and two rigs that owe a repeat
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: []
writes:
  - experiments/plane-accounting/
  - experiments/solver-toy/
---

# The sixth salted site, and two rigs that owe a repeat

## Question

**ADR 0043 keyed five of the six salted draws and `salt_check.py` reports the
sixth as OWED rather than as a failure. That entry is this ticket, and the check
stays amber until it is discharged.**

`experiments/plane-accounting/arms.py:175` still carries

```python
rng = random.Random(SEED ^ (hash(key) & 0xFFFF))
```

`hash()` on a `str` is salted per process, so that rig draws a **different
objective function** — `W_STATED` 8 against `W_INVENTED` 1, per room — in every
process it runs in. Ticket 82 measured the cost of exactly this line's twin in
`experiments/warp/`: **32 of 36 points** of per-pair `dev` disagreement and
**4 of 4** of `served`, at every time cap including caps no solve reaches.

⚠️ **82 could have taken it and deliberately did not.** The directory is
unclaimed — 77 created it, 78 re-took it, both are closed and 79 declares
neither — and 82's own text says to characterise the floor in one rig before
re-measuring a second, and to hand the other two their numbers as prose exactly
as 73, 74 and 77 did. That reasoning is discharged now: the floor **is**
characterised, so the reason to hold the boundary is spent.

**What has to be done:**

1. **Key the sixth draw.** `zlib.crc32(key.encode())`, the same repair and the
   same reason as the five. Then move `experiments/plane-accounting/` out of
   `salt_check.py`'s `OWED` map so the check goes green rather than amber —
   ⚠️ **and check the map is then EMPTY**: an `OWED` entry without a live ticket
   is the state that hides a defect behind a note.
2. **Say which of ADR 0039 and ADR 0040's figures were computed across
   processes.** ADR 0040's paired A/B over 307 candidates is protected if both
   arms ran in one process on the same key — `arms.py` seeds per `key`, so
   within a process both arms share a weight vector and the *paired difference*
   is clean. That needs confirming rather than assuming, and it is the whole
   question for the ADR's `2,36x` variables / `1,85x` constraints and its
   **16,4 %** solve-time claim. ⚠️ ADR 0040's *structural* counts are exact and
   are not at risk; only the timings and the `served`-shaped figures are.
3. **Repeat what `solver-formulation.md` II.6 already says it owes, and it is
   not this ticket's invention:** *"Every timing is a single run at seed
   20260817. There is no variance estimate. CP-SAT's portfolio search is
   stochastic across workers; these numbers could move materially on a re-run
   and must be repeated over ≥ 10 seeds before any of them is quoted as a
   specification."* That was written before ticket 82 existed and never
   discharged. ⚠️ **ADR 0043 decision 5 now forbids promoting any of those
   timings into a threshold** — every run there was `num_workers = 4` with no
   `interleave_search`, so all of them ran under `NonDeterministicLoop`.
4. **Price `interleave_search`.** It is the *only* predicate that buys parallel
   determinism (`cp_model_solver.cc:823-836`), it is marked **"Experimental."**,
   it defaults to false, and what it costs in solution quality per wall-second on
   this repo's models is unmeasured. It cannot be made a default until it is
   priced. ⚠️ Note that it does **not** rescue the shipped projection, which is
   wall-capped at 15 s by product constraint — `DeterministicLoop` takes no time
   limit, so a wall cap firing first destroys determinism regardless. This is
   about making a *gate* stable, not the engine.

**What this is not.** Not a re-run of the warp figures — ADR 0043 consequence 6
settles that they are labelled rather than re-derived. Not a challenge to the
15 s cap or to the projection's non-determinism, which is entailed and already
disclosed in `homeowner-surface.md`. Not a request to make `interleave_search`
the default; that needs its own evidence.

## Raised by

*A time-capped solver is not a reproducible measurement* (2026-08-31), which held
the write-set boundary deliberately and refused to leave a one-line repair as a
prose handoff — a one-line fix that nobody owns is how this defect survived
ticket 65's own fix of it.
