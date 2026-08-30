---
id: 82
title: A time-capped solver is not a reproducible measurement
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
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

## Resolution

**ADR 0043.** The floor is two mechanisms, the ticket named the minor one, and
the major one is not a stopping rule at all.

### 1. How big is it really, per rig?

`experiments/warp/repro_floor.py`: a 2x2 over the objective-weight draw (fixed /
varied) crossed with the stopping rule (wall cap / `max_deterministic_time`), `k`
re-solves a pair, under deliberate CPU contention. Population sample of 25 pairs
drawn from the 3 834 the gate figures were computed on, `k = 3`, `--time=3.0`:

| cell | `served` | `dev` | hit the cap |
|---|---:|---:|---:|
| `wall/varied` -- this ticket's condition | 4,00 % | 36,00 % | 2,9 % |
| `wall/fixed` -- the wall clock alone | **0,00 %** | **4,00 %** | 2,9 % |
| `det/varied` -- the salted draw alone | 4,00 % | 32,00 % | 0,0 % |
| `det/fixed` -- control | **0,00 %** | **0,00 %** | 0,0 % |

**The wall clock is the minor term. `absolute_area.run_one` seeded its per-room
objective weights from `hash(key)`, and `hash()` on a `str` is salted per
process** -- so ticket 65's two concurrent sweeps did not solve one model twice
under different load, they solved **different objective functions**, `W_STATED` 8
against `W_INVENTED` 1. Six live sites carried it. It moves answers that were
proved OPTIMAL (`det/varied`: 46,7 % of the enriched sample, **0 of 90** solves
reaching a cap), so no stopping rule addresses it.

**It scales with the cap and is zero at the shipped one** -- same 25 pairs, the
wall clock alone reads 8,00 % at 0,5 s, 4,00 % at 3,0 s and **0,00 % at 15 s**,
where **no solve reaches the cap at all**. The salted draw reads 32,00 % at all
three, with identical p90 and max, which is the invariance it must show and a
check that the runs drew one sample.

⚠️ **`--load=0` exonerates the wall clock.** The idle smoke run put that cell at
0,00 % and would have been read as clearing it. Any re-measurement states its load.

### 2. Which published figures move, and does any decision move with them?

**None.** Two structural facts carry them, and one of them was worth measuring:

- **Arm comparisons are paired.** `gate_effect.warp_candidates` and
  `gate_depth.py` warp the union once and let the rules filter it, so every arm
  reads the same row per key and the draw cancels.
- **The CIs already carry it.** `gate_depth.boot_ci` resamples *Briefs*, each with
  its own realised draw, so the bootstrap propagates this variance.

⚠️ **But a per-pair rate is not the floor under a published figure**, and quoting
36 % against ADR 0032's 1,3-point margin compares two quantities. `agg_floor.py`
measures the aggregate directly -- 150 pairs, 6 draws, deterministic cap:
served **range 1,33 pts, sd 0,54**; `dev` p50 range 0,0011; `dev` p90 range 0,0132,
sd 0,0054. **ADR 0032's margin sits AT that range and only the pairing saves it**:
unpaired it would be ~2,4 sd from noise. ✅ Draw 0 -- the `crc32` value now
shipped -- lands mid-band at 70,67 %, so fixing the seed ships no outlier. ✅ And
ticket 65's refusal to call its pooled p90 is confirmed: its 0,0038 gap is below
the 0,0054 sd, while its thin-half 0,0266 is ~5 sd and clears.

**What is NOT protected: every cross-run delta.** A re-run in a new process
re-draws every weight vector. **The `market`-arm re-run 62 and 67 owe is exactly
that shape** and must now clear ~0,5 points of served. And **62's matched-pair
design never matched on the objective** -- different donors are different keys;
`run_one` now takes `wseed`, so passing one value to both members makes it real.

### 3. What reproduction discipline do the rigs owe?

`docs/research/solver-reproducibility.md`, from OR-Tools' own source. "Reproducible"
appears **nowhere** in `sat_parameters.proto`'s 1 925 lines.

- **The warp** (`num_workers = 1` + `max_deterministic_time`) measured **0,00 %**,
  at a median 1,34 s against the wall cap's 1,35 s. Per issue **#3948** -- fixed
  seed, differing optimal fingerprints, maintainer *"Reproduced."* -- and the
  absent cross-machine documentation, the claim is *"reproducible on this machine,
  verified by repeat"* and no more.
- **The shipped projection is not reproducible, and that is entailed.**
  `LaunchSubsolvers` branches on `interleave_search` and nothing else, so
  `max_deterministic_time` alone does **not** buy parallel determinism -- the
  common belief is false as stated. `interleave_search` is "Experimental",
  defaults false, and `DeterministicLoop` takes **no time limit**, so a wall cap
  firing first destroys determinism regardless. The projection cannot drop below
  2 workers (II.6) and 15 s is a product constraint. **A 15 s wall cap and a
  reproducible projection are mutually exclusive**, and `homeowner-surface.md`
  already discloses it.
- **Repair:** `zlib.crc32(key.encode())` at five sites in `experiments/warp/`.
  `PYTHONHASHSEED=0` endorsed as a second layer only -- it makes reproducibility a
  property of how the process was launched and cannot be asserted from inside.

### 4. May a figure be quoted without its `k`?

**No**, and the six-item list is adopted from the field rather than invented --
MLPerf fails a submission whose seeds are not logged and reports an olympic mean
over 3-10 runs; BenchExec exits non-zero when the machine cannot be measured.
ADR 0043 decision 6. **A difference below the floor is reported as unresolved,
never as a number.**

**And it is asserted, because it was already written down and skipped.**
`experiments/warp/salt_check.py` scans every `.py` outside `venv/`, blanks string
literals so it does not report its own prose, and exits 1 on any unowned site --
proven red on a reverted site and green on repair. Ticket 65 wrote this exact
trap into the README, naming `hash` and `PYTHONHASHSEED`, and five live sites went
on carrying the defect underneath it. Its home is `env_check.py`; it is written
here because that file belongs to no one and this ticket may not take it.

⚠️ **No timing from a non-interleaved parallel run may become a threshold.**
Every run in `solver-formulation.md` used `num_workers = 4` without
`interleave_search`, so all ran under `NonDeterministicLoop`.

⚠️ **The debt was already on the record and went unpaid.** II.6: *"Every timing
is a single run at seed 20260817. There is no variance estimate... must be
repeated over >= 10 seeds before any of them is quoted as a specification."*
Written before this ticket existed.

### Declared on resolution

- `docs/adr/0043-...` -- new, unclaimed.
- `docs/research/solver-reproducibility.md` -- new, unclaimed.
- `experiments/warp/` -- this ticket's own: `repro_floor.py`, `agg_floor.py`,
  `salt_check.py` new; `absolute_area.py` (`wseed`, `dtime`, `all_optimal`),
  `fit_warp.py` (`dtime`), plus the crc32 repair at five sites; README section.

**Deliberately NOT taken**, per this ticket's own instruction:
`experiments/solver-toy/` and `experiments/plane-accounting/`. Both still owe a
repeat and `arms.py:175` still carries the salt -- raised as its own ticket rather
than left as a prose line, because a one-line fix that nobody owns is how this
defect survived 65.
