---
id: 82
title: A time-capped solver is not a reproducible measurement
parent: map
labels: [wayfinder:task]
status: open
assignee:
blocked_by: []
writes:
  - experiments/warp/
---

# A time-capped solver is not a reproducible measurement

## Question

**Every warp and every projection this map has published was solved under a wall
clock cap, and the same input does not return the same answer twice.**

Ticket 65 measured it by accident. Two sweeps ran concurrently and warped **1 489
identical `(brief, donor)` pairs** — same seed, same targets, same
`--time=3.0`, same code. The results:

| | agreement |
|---|---:|
| `status` (OK / INFEASIBLE / NOPAIR) | **1 489 of 1 489** |
| `served` — the ergonomic floor verdict | **2.82 % DISAGREE** |
| `worst_room_dev` | **14.71 % DISAGREE** |

CP-SAT returns whatever incumbent it has reached when the cap fires. Under
different CPU load it reaches a different one. Feasibility is stable; **which
feasible solution you get is not**, and `served` and `dev` are both read off the
solution rather than off the status.

**This is a floor under every timed figure in the repo, and the repo quotes
through it.** `experiments/warp/` alone publishes served rates, decline rates and
best-of-pool percentiles to a tenth of a point; `project_join.py`,
`constrained_warp.py`, `floor_warp.py` and `experiments/plane-accounting/` all
solve under a cap and report the same way. ADR 0040's `+16,4 %` total solve time,
ADR 0032's `88.1 %` against `89.4 %` — a **1.3-point** served difference, which
is **under half this floor** — and ADR 0039's timing figures are all quoted at a
precision this measurement does not support.

⚠️ **It has already produced a wrong number once.** Ticket 65's dedupe took the
last occurrence per key, and the same analysis over the same file returned
`req ≤ 1` p90 **0.1196 on one read and 0.1217 on the next**. Nothing had changed
but which duplicate won.

**What has to be settled:**

1. **How big is it really, per rig?** 2.82 % / 14.71 % is one measurement, on the
   warp, at `--time=3.0`, under contention. It is not known whether the floor is
   the same at 15 s (the shipped cap the projection uses), whether it scales with
   the cap, or whether `experiments/solver-toy/` and
   `experiments/plane-accounting/` sit at the same place. A deliberate
   repeated-solve study, rather than an accident, is cheap: re-solve one sample
   `k` times and report the spread of every statistic the rigs publish.
2. **Which published figures move, and does any decision move with them?** The
   floor invalidates *precision*, not necessarily *conclusions* — ticket 65's own
   14.9- and 31.0-point gaps are an order of magnitude clear of it, while its
   0.3-point gap is not. Someone has to walk the ADRs that quote to tenths and
   mark which claims survive. ⚠️ **ADR 0032's original 1.3-point served margin is
   the first candidate and it is load-bearing** — it is the whole of *"it wins on
   all three axes"*.
3. **What reproduction discipline do the rigs owe?** First-wins dedupe and
   seed-keyed outputs landed under 65 and are a start, not the answer. The real
   options are a **deterministic solve** (`num_search_workers=1` plus a
   deterministic time limit, which CP-SAT supports and which trades wall clock for
   repeatability), **solve to OPTIMAL** where the model allows it, or **publish a
   spread** rather than a point and require `k` re-solves for any figure quoted to
   tenths. These have different costs and only the first is free of a rerun.
4. **Whether a figure may be quoted at all without its `k`.** The rigs already
   carry a rule — *if you add a statistic, add its inputs to the row record*. The
   analogous one here would be that a timed statistic carries the cap, the worker
   count and the number of re-solves behind it, and that a difference smaller than
   the measured floor is reported as "not resolved" rather than as a number.

**What this is not.** Not a claim that any decision on the map is wrong — no
conclusion has been shown to move, and ticket 65 checked its own and they hold.
Not a re-opening of the 15 s cap, which is a product constraint. Not a request to
re-run everything: the deliverable is the floor, the list of figures it reaches,
and the discipline, in that order.

**Where it goes.** `experiments/warp/` for the repeated-solve study, since the
accidental measurement is already there and `gate_depth.py`'s JSONL cache makes a
`k`-repeat cheap. ⚠️ **It also touches `experiments/solver-toy/` and
`experiments/plane-accounting/`, and this ticket deliberately claims NEITHER** —
43 and 78 are closed and 79 declares neither, so both stand unclaimed and could
have been taken; the reason not to is that the floor has to be characterised once,
in one rig, before a second and third are re-measured against it. Take the study in
`experiments/warp/` first and hand the other two their numbers as prose rather
than opening them, exactly as 73, 74 and 77 did.

## Raised by

*What the fourth gate term is worth at the shipped pool depth* (2026-08-30),
which measured the floor by accident and could not carry it.
