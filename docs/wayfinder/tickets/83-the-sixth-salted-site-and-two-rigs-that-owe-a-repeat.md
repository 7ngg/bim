---
id: 83
title: The sixth salted site, and two rigs that owe a repeat
parent: map
labels: [wayfinder:task]
status: closed
assignee: tng
blocked_by: []
writes:
  - experiments/plane-accounting/
  - experiments/solver-toy/
  # declared on resolution, all unclaimed at the time:
  - docs/research/solver-formulation.md
  - docs/research/solver-reproducibility.md
  # a single dict entry in a directory 62 and 67 claim -- see the resolution:
  - experiments/warp/salt_check.py
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

## Handed on by ticket 79 (2026-08-31)

⚠️ **Two clauses in `selftest_parts.py` P9 are now false, and 79 caused it.**
ADR 0045 widened `experiments/room-rectangles/erosion_check.py` from one
hand-built L to all four shapes two Parts make. P9's docstring reads

> P9  ADR 0001's erosion identity at TWO reflex corners. `erosion_check.py`
>     checks it at one and asserts `reflex == 1`; 44,8 % of the corpus's …

and its runtime note repeats it. **`erosion_check.py` now checks all four shapes**
— it asserts `(vertices, reflex)` per shape, so the `reflex == 1` half survives as
the L case and *"checks it at one"* does not.

79 holds `experiments/room-rectangles/erosion_check.py` but **not** this
directory, which this ticket claims. No value moves and no assertion changes —
all ten P9 checks pass unchanged. The 44,8 % figure is still right; ADR 0045
restates it on both planes (**44,8 %** pooled, **43,1 %** proved-optimal only) for
the reason ticket 85 exists.

## Resolution (2026-08-31)

**All four items are discharged. The sixth site is one line and it was under
FOUR rigs, not two; ADR 0043 decision 5's prescription is measured for the first
time and it is band-limited; and `interleave_search` is refused for the
projection on evidence, not by inheritance.**

`docs/research/solver-formulation.md` **Part X**; `docs/research/solver-reproducibility.md`
**§2.5** and two discharged "not established" clauses.

⚠️ **The corpora are absent from this working copy** (`data/corpora/` is
gitignored, "acquired per `dataset-inventory.md`"), so nothing in
`experiments/plane-accounting/` or `experiments/warp/` could be *re-run* here.
Items 1 and 2 are therefore discharged by repair, by code reading and by a
corpus-free experiment; items 3 and 4 by measurement, in
`experiments/solver-toy/`, which is standalone. What is owed on a machine with
the corpus is named in *Owed* below.

---

### Item 1 — the sixth draw is keyed, and the OWED map is empty

`experiments/plane-accounting/arms.py:175` now reads
`random.Random(SEED ^ (zlib.crc32(key.encode()) & 0xFFFF))` — the same repair and
the same expression as `project_join.py:227`, the line it copies. `salt_check.py`'s
`OWED` map is **`{}`** and the check prints *"0 site(s) owed to a ticket, 0
unowned. PASS"*, so the ⚠️ this item carried — *an `OWED` entry without a live
ticket is the state that hides a defect behind a note* — is closed by
construction rather than by promise.

**The repair is proved, not asserted, and it is proved without the corpus.** The
weight draw is pure arithmetic on the key, so it can be exercised directly under
three real process salts:

| key | `hash()` under PYTHONHASHSEED 1 / 2 / 3 | `crc32` under 1 / 2 / 3 |
|---|---|---|
| `brief-0007\|donor-1421` | 3 different vectors | **identical** |
| `brief-0031\|donor-0885` | 3 different vectors | **identical** |
| `brief-0102\|donor-2011` | 3 different vectors | **identical** |

⚠️ **The ticket says "two rigs" and it is four.** `arms.py`, `arms_parts.py`,
`seeds.py` and `seeds_parts.py` all route their warp through `arms.warp_floor`,
so the one line sat under **ADR 0039, ADR 0040 and ADR 0041**. One line, one
repair, four rigs.

⚠️ **The defect had grown past irreproducibility and nobody could see it.**
`arms.py`'s own selftest asserts *"`warp_floor(post_floor=False)` IS
`project_join.warp_geom`"* and checks `gx`/`gy` **cut vector for cut vector**.
Ticket 82 repaired `project_join.py:227` to `crc32` and left this copy on
`hash()` — so since 82, that assertion has been comparing **two different
objective functions** and could only pass by luck. It needs the corpus and was
never re-run. The fix restores it; running it is owed.

**Ticket 79's handoff is also discharged** — it named this directory and could
not take it. `selftest_parts.py` P9's docstring and runtime note both claimed
`erosion_check.py` *"checks it at one and asserts `reflex == 1`"*; ADR 0045
widened it to all four shapes with `(vertices, reflex)` per shape. Both clauses
corrected. **All ten P9 checks pass unchanged and no value moved**, exactly as 79
predicted. 44,8 % stands as the pooled figure; the 43,1 % floor ticket 85 struck
is not restated.

---

### Item 2 — which figures were computed across processes

Answered from the rigs' own persistence format, which turns out to record it.
`arms.py` rewrites a whole-list `.json` from an empty list every pair, so a
resumed run would have destroyed its predecessor; `arms_parts.py` **appends** to
`.jsonl` and carries `--skip`, which exists only to resume.

| run | evidence | processes | standing |
|---|---|---|---|
| `arms.py` → **ADR 0039, ADR 0040** | 340 rows, whole-list dump, `brief_i` 0–119 contiguous, `_meta.secs` **2 983,7** covering all 340 | **one** | internally consistent |
| `seeds.py` → the seed-spread bar | 35 rows, whole-list dump | **one** | internally consistent |
| `arms_parts.py` → **ADR 0041** | 332 rows, append log; its own comment records dying *"at pair 174 of 332"* and resuming, and `solver-formulation.md`'s *Reproducing Part IX* repeats it | **≥ 2** | a blend of ≥ 2 objective draws |

**The blend is unbiased and the log is clean.** Weights are drawn from the same
Bernoulli(0,30) either way, so a mixed-salt population is still an i.i.d. sample;
and the append log holds **332 unique `(brief, cand)` pairs, monotonic in
`brief_i`, zero duplicates**, so no row is corrupted and none was solved twice.
**ADR 0041's figures are not wrong.**

**What is lost is re-derivability, and it is nearly total.** Two processes keep a
key's objective only if every room's weight survives, at
`p² + (1−p)² = 0,58` per room. Over the real room counts in the rows:

- `arms.py`: **11,9 of 340 pairs — 3,5 %** would keep their objective on a re-run.
- `arms_parts.py`: **10,5 of 332 — 3,2 %**.

So **~96,5 % of both runs is unreproducible**, and the salts are gone. This is
the concrete content of ADR 0043 consequence 6's *"labelled rather than
re-derived"*.

⚠️ **One cross-process comparison exists in ADR 0040 and it is distributional,
not paired.** Decision 1 sets the cost (from `arms.py`) against the seed spread
(from `seeds.py`) — *"over six CP-SAT seeds only 6 of 35 candidates have a
difference inside their own seed spread"*. Each run is internally consistent, but
`seeds.py` **re-warps**, so the two measured different geometries of the same
pairs. The argument survives as a comparison of distributions; it is not a paired
one and should not be read as one.

**Classify the figures three ways, not two:**

1. **Paired within a row, so salt-independent** — every A-vs-B delta, because
   `one()` warps once and all five arms consume that geometry. ADR 0040's
   **2,36×** variables, **1,85×** constraints, **+16,4 %**, cap exhaustion 17 → 16;
   ADR 0041's **1,82×**, **+13,2 %**, *18 of 19 inside spread*. ⚠️ Still exposed to
   CP-SAT non-determinism, which is what Part X now bounds.
2. **Geometry-dependent, so salt-dependent** — every delivered area and anything
   counted off one. ADR 0040's **10 Rooms of 1 993 above the band / 9 candidates /
   worst 10,2 m² over**, the headroom distribution, `item4_residual` in full.
   These are single-draw figures.
3. **Objective-independent** — feasibility. Weights change *which* optimum is
   found, never *whether* one exists, so the INFEASIBLE counts (33 warp-INFEASIBLE
   of 340, A's 4 of 307) do not move with the salt.

**No `solver-formulation.md` timing has actually leaked into a shipped threshold**
— checked: `rules.json` carries no seconds-valued rule and `acceptance-bar.md`
cites 15 s as the product constraint. ADR 0043 decision 5 is currently *respected*,
so this item unblocks quoting rather than repairing anything.

---

### Items 3 and 4 — the owed repeat, and the price of determinism

`experiments/solver-toy/repeat_seeds.py`, **216 solves, 2 737 s**. It imports
`sweep.get_scenario` and `sweep.run_one` verbatim, and its selftest asserts arm
`base`'s `SolveConfig` equals `sweep.execute`'s **field for field**, so this is a
repeat rather than a new experiment. Full write-up at Part X.

⚠️ **READ FIRST: this is a different machine from every published figure on this
map.** `Intel64 Family 6 Model 141` (Tiger Lake-H, **12 logical cores**) against
Parts I–IX's `Model 58` (Ivy Bridge, **4**). `num_workers = 4` meant the whole
contended machine there and four of twelve uncontended here. **No wall figure
here is comparable with any wall figure above**, and ADR 0043 decision 6 item 5 —
*the machine, for any wall-clock figure* — is the discipline that keeps the note
coherent. It is the first time it bites.

**Item 3 — eight seeds never discharged this, and the reason is one line.**
`sweep.py` feeds `BASE_SEED + s` to **both** the scenario builder and
`SolveConfig.seed`, so S2's "8 seeds" is a spread over *instances*. The owed
clause is about *portfolio* stochasticity. Only **S7** separates them and it ran
4 seeds, for a different purpose. The nearest real precedent is
`plane-accounting/seeds.py` — S7's design, 6 seeds, scoped to ADR 0039/0040.
Part X is S7's design at S2's scale: one instance per room count, **12 seeds ×
2 replicates**, shipped configuration.

| n | status | distinct objectives | valid | distinct Plans |
|---|---|---:|---:|---:|
| **8** — inside C13's band | OPTIMAL 24/24 | **1** of 24 | **24/24** | 4 of 24 |
| 12 | FEASIBLE 24/24 | 5 of 24 (70–76) | 24/24 | 16 of 24 |
| 24 | FEASIBLE 24/24 | 21 of 24 | **18/24** | 24 of 24 |

**Inside the band the engine ships in, the seed moves nothing a gate would
assert** — only the tie-break. At 24 rooms **validity itself moves**: six seeds
return a Plan paying 1–41 unassigned cells. ⚠️ That does **not** contradict II.6's
100 % validity, which is a **30 s** figure; it means II.6's validity does not
transfer to the shipped 15 s cap. 24 rooms is far outside C13's 3–10 band.

**Does a run repeat itself** — every cell solved twice, 36 cells per arm:

| arm | status | objective | **Plan** | n=8 | n=12 | n=24 |
|---|---:|---:|---:|---:|---:|---:|
| `base` — shipped | 36/36 | 19/36 | **4/36** | 3/12 | 1/12 | 0/12 |
| `il` — interleave at the 15 s wall cap | 32/36 | 28/36 | 26/36 | 10/12 | 12/12 | 4/12 |
| `det` — decision 5's full prescription | 36/36 | 24/36 | 12/36 | 11/12 | 1/12 | 0/12 |

⚠️ **ADR 0043 decision 5's prescription is necessary and NOT sufficient, and the
boundary falls on C13's band.** `interleave_search` + `max_deterministic_time` +
pinned seed and workers reproduces the Plan **12 times in 36**: effectively
reproducible at 8, **published plane only** at 12 (status and objective 12/12,
cover 1/12), and **neither at 24** (objective 0/12). The decision is not
withdrawn — its guard, *assert status and objective, never seconds*, is exactly
what survives, and it survives because it was written conservatively. **Read it
as band-limited.** The n=12 row is ADR 0046 decision 4's *"the cover is not
publishable"* reproduced on the **projection** model by an independent rig,
having been established on the **conversion** model.

**Item 4 — the price, and the verdict.**

| n | `il` status | objective vs `base` | valid | wall p50 |
|---|---|---|---:|---:|
| 8 | OPTIMAL 24/24 | **equal** (37) | 24/24 | 0,369 → **3,777 s** |
| 12 | FEASIBLE 24/24 | **worse 24/24** — 165 vs 70 | 24/24 | 15,021 → 10,872 s |
| 24 | FEASIBLE 20, **UNKNOWN 4** | worse 20/20 | **18/24 → 0/24** | 15,030 → 15,075 s |

**`interleave_search` must not be a default, and the wall cap is why.** 10,2× the
wall for nothing at 8 rooms; total determinism bought at **2,36×** the objective
at 12; and at 24 it destroys the answer — **zero** valid Plans, four returning no
Plan at all, 120–351 unassigned cells against `base`'s worst of 41.

**The flag is not the problem; the flag under a wall cap is.** Arm `det` — same
flag, deterministic budget, no wall cap — is the **best** arm at 24 rooms:
**24/24 valid** against 18/24, zero slack, objectives 115–213 against
116–4 100 159. It costs **24,7 s** p50 against a 15 s product cap. So it is a
**gate** configuration and never a product one, which is ADR 0043 decision 4's
*"mutually exclusive"* with the quality cost now attached rather than only the
determinism argument. This **corroborates ADR 0046 decision 3 by a different
route** — that refusal was measured on the conversion rig and rested on
non-determinism; this one is measured on the projection model and rests on
quality under the cap.

---

### What was deliberately not done

**No ADR was written or amended, and that is a `writes:` decision rather than an
omission.** `docs/adr/` is claimed as a **bare directory** by *An IfcSpace carries
no room use*. The map's Notes have now flagged the invisible-directory-claim shape
three times — most recently that ticket 85 took the number 0046 while 84 could
equally have taken it. Taking it a fourth time for convenience, when the finding
lands cleanly in two research documents this ticket can hold outright, would be
choosing convenience over the one rule that section exists to enforce. **The
ADR 0043 amendment is handed on as prose**, exactly as tickets 73, 74 and 77 did:

> ADR 0043 decision 5's *"a gate that must be stable needs `interleave_search=true`
> + `max_deterministic_time` + pinned `random_seed` and `num_workers`"* is
> **band-limited**. Measured over 12 seeds × 2 replicates: reproducible at 8
> rooms, published-plane-only at 12, neither at 24. Its guard — *assert status
> and objective, never seconds* — is what carries the decision through its own
> measurement. ADR 0043 consequence 8 and ADR 0046 decision 3 (`interleave_search`
> is not a default anywhere) are **re-affirmed on the projection model**, on
> quality rather than on determinism.

**`salt_check.py` was not relocated.** ADR 0043 decision 2 says its home is
`experiments/environment/env_check.py`; it still lives in `experiments/warp/`.
That directory belongs to *What a sheared donor costs a warped candidate* and
*The posted floor is a seed-shape estimate*, and moving a repo-wide gate is not
one of this ticket's four items. The edit that **was** made there is the single
`OWED` dict entry item 1 names, held to that and nothing else.

### Owed, on a machine that has the corpus

1. `python experiments/plane-accounting/arms.py --selftest` — the assertion that
   has been comparing two objective functions since ticket 82. Expected to pass
   now; **unverified here**.
2. `arms_parts.py --selftest` and `seeds.py` likewise inherit the repair.
3. **No figure needs re-deriving.** ADR 0043 consequence 6 settles that they are
   labelled, and items 2's classification says which label each takes.
