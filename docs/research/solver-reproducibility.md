# Solver reproducibility — findings

Research note on what OR-Tools CP-SAT actually guarantees about repeatable
results, and on the reporting discipline the surrounding fields enforce.

Method note, and please read it before trusting anything below. Every OR-Tools
claim here is backed by **the upstream source or the parameter proto**, quoted
with a file and line number, not by a blog post or a summary. Where a source
does **not** answer a question, this note says *not documented* rather than
inferring an answer. Where a claim is reasoning over the sources rather than
something a source states, it is tagged **[INFERENCE]**. Where a source could
not be retrieved in this pass, it is tagged **[NOT CHECKED]**.

**Version pinned here: `ortools 9.15.6755`** (`pip show ortools`). The quoted
proto and C++ text was fetched from
`raw.githubusercontent.com/google/or-tools/stable/…` and **diffed against the
`v9.15` tag**: the `max_deterministic_time` block and the `interleave_search`
block are byte-identical between `stable` and `v9.15`, so the line numbers below
apply to the pinned build. Line numbers are into
[`ortools/sat/sat_parameters.proto`](https://github.com/google/or-tools/blob/v9.15/ortools/sat/sat_parameters.proto)
(1,925 lines), and into the matching files under
`https://github.com/google/or-tools/blob/stable/`.

---

## Verdict

| Question | Answer |
|---|---|
| 1. Is `num_workers=1` + `max_time_in_seconds` reproducible? | **No.** The *search trajectory* is deterministic; the *stopping point* is wall-clock, so an interrupted solve returns whatever it had reached on that machine under that load. Only a run that terminates with a proof (OPTIMAL/INFEASIBLE) before the cap is cap-independent. |
| 1b. Is `max_deterministic_time` reproducible? | **Yes for the stopping point**, single-worker: the counter is operations, not seconds. Cross-machine bit-identity is **not documented anywhere** — treat as unestablished, not as promised. |
| 2. Is `num_workers=4/8` + a deterministic cap reproducible? | **No.** `max_deterministic_time` alone is **not sufficient**. `interleave_search=true` is **required** — it is the flag that selects `DeterministicLoop()` over `NonDeterministicLoop()` in the solver's own dispatch. This contradicts the common belief that a deterministic time limit is what buys parallel determinism. |
| 3. Units of `max_deterministic_time` | A weighted **operation count**, scaled so one unit ≈ one second on the machine the coefficients were least-squares-fitted on. Portable as a *budget*; its wall-clock cost is **not** portable, and the maintainer states the time↔dtime correlation is bad for some code. |
| 4. Does `random_seed` matter at `num_workers=1` when OPTIMAL is proved? | **Yes** — it changes the search path, the runtime, and **which** optimal solution is returned when several are optimal. OR-Tools' own test policy exists specifically to stop clients relying on that. The optimal *objective value* cannot change **[INFERENCE]**. |
| 5. Reporting discipline | Seed, cap (type **and** value), repeat count and machine, all of them; report a distribution, not one number; and state the tolerance a claim must survive. All four are enforced somewhere in the field, and one of them by OR-Tools' own parameter comment. |
| 6. Mechanical enforcement | **Yes, in two suites:** MLPerf's `package_checker`/`seed_checker` **fails a submission** that does not log seeds correctly; BenchExec's `check_cgroups` **exits non-zero** when the machine cannot be measured reliably. MIPLIB ships a solution checker (correctness, not timing). ACM badging is human review. |

---

## 1. What OR-Tools guarantees about `CpSolver` reproducibility

### 1.1 The word "reproducible" appears nowhere in the parameters

`grep -i reproduc sat_parameters.proto` → **zero hits** across all 1,925 lines.
There is no reproducibility guarantee in the public parameter surface. The only
reproducibility *claim* found anywhere in the primary sources is about the
limit class, not about CP-SAT:

> ` * The deterministic limit is used to ensure reproductibility. As a consequence`
> ` * the deterministic time has to be advanced manually using the method`
> ` * AdvanceDeterministicTime().`
>
> — [`ortools/util/time_limit.h:54-56`](https://github.com/google/or-tools/blob/stable/ortools/util/time_limit.h#L54)
> (the typo "reproductibility" is upstream's)

That is a statement about *why the class exists*, not a warranty about the
solver's output. Read it as intent.

### 1.2 `num_workers=1` — the scheduling is deterministic, by code path

Traced end to end:

1. `cp_model_solver.cc:3038-3040` — the parallel path is taken only if
   `params.num_workers() > 1 || params.interleave_search() ||
   !params.subsolvers().empty() || !params.filter_subsolvers().empty() ||
   params.use_ls_only()`.
2. Otherwise (`cp_model_solver.cc:3046-3054`) exactly one subsolver is built —
   `FullProblemSolver("main", params, /*split_in_chunks=*/false, &shared)` —
   and handed to `LaunchSubsolvers`.
3. `cp_model_solver.cc:823-836` — `interleave_search` defaults to `false`, so
   `NonDeterministicLoop(subsolvers, params.num_workers(), shared->time_limit)`
   is called.
4. [`ortools/sat/subsolver.cc:195-201`](https://github.com/google/or-tools/blob/stable/ortools/sat/subsolver.cc#L195) —
   `NonDeterministicLoop` opens with
   `CHECK_GT(num_threads, 0); if (num_threads == 1) { return SequentialLoop(subsolvers); }`.

So at `num_workers=1` the badly-named `NonDeterministicLoop` degenerates to a
sequential loop, and no thread scheduling enters the result. Given a fixed
model, parameters and seed, the sequence of decisions is fixed. **[INFERENCE]**
from the code path; no document states it.

### 1.3 …but the stopping point is not, under a wall-clock cap

> `  // Maximum time allowed in seconds to solve a problem.`
> `  // The counter will starts at the beginning of the Solve() call.`
> `  optional double max_time_in_seconds = 36 [default = inf];`
>
> — `sat_parameters.proto:329-331`, verbatim

A wall-clock cap truncates a deterministic trajectory at a machine-dependent
point. Same path, different truncation → **different incumbent, different
bound, potentially a different status**. `TimeLimit` makes this worse in a
useful way: it stops *early* by a safety margin derived from measured recent
call intervals, i.e. from observed machine speed —

> ` * The limit is very conservative: it returns true (i.e. the limit is reached)`
> ` * when current_time + max(T, ε) >= limit_time, where ε is a small constant (see`
> ` * TimeLimit::kSafetyBufferSeconds), and T is the maximum measured time interval`
> ` * between two consecutive calls to LimitReached() over the last kHistorySize`
> ` * calls`
>
> — [`time_limit.h:60-65`](https://github.com/google/or-tools/blob/stable/ortools/util/time_limit.h#L60)

A loaded machine has a larger `T` and therefore stops *sooner in dtime*. CPU
load is not a second-order effect on the stopping point; it is the mechanism.

**Consequence.** A run that ends with a proof (`OPTIMAL` / `INFEASIBLE`) before
the cap is unaffected by the cap, and its *objective value* is reproducible. A
run that ends `FEASIBLE` at the cap is a measurement of the machine, not of the
model.

### 1.4 Single-worker determinism has been broken in practice

[google/or-tools#3948, "Non-determinism for CP-SAT with num_workers=1"](https://github.com/google/or-tools/issues/3948)
(2023-10-11, v9.7.3120): a user reported different optimal-solution fingerprints
across runs with `num_workers=1` **and a fixed seed**, same presolve
fingerprint. Laurent Perron's reply the next day, in full: "Reproduced. Thanks".
The issue is closed; **the thread contains no comment identifying a fix or a
version** (two comments in total). Treat single-worker determinism as a property
that has empirically failed at least once, not as a guarantee.

### 1.5 Cross-machine — not documented

No primary source found states that CP-SAT returns identical results across
different CPUs, OSes or compilers, even under a deterministic cap. The proto is
silent; `time_limit.h` is silent. **Not documented.** Do not assert it.

---

## 2. Multi-worker determinism, and what `interleave_search` is actually for

### 2.1 The two parameters, verbatim

`sat_parameters.proto:333-336`:

```proto
  // Maximum time allowed in deterministic time to solve a problem.
  // The deterministic time should be correlated with the real time used by the
  // solver, the time unit being as close as possible to a second.
  optional double max_deterministic_time = 67 [default = inf];
```

`sat_parameters.proto:767-774`:

```proto
  // Experimental. If this is true, then we interleave all our major search
  // strategy and distribute the work amongst num_workers.
  //
  // The search is deterministic (independently of num_workers!), and we
  // schedule and wait for interleave_batch_size task to be completed before
  // synchronizing and scheduling the next batch of tasks.
  optional bool interleave_search = 136 [default = false];
  optional int32 interleave_batch_size = 134 [default = 0];
```

Note what each says. `max_deterministic_time`'s comment claims **nothing about
determinism of the search** — it defines a *limit* and asserts a correlation
with real time. `interleave_search`'s comment is the one that says "The search
is deterministic (independently of num_workers!)". It is also labelled
**"Experimental."** and defaults to **false**.

### 2.2 The dispatch settles it

`cp_model_solver.cc:823-836`, in `LaunchSubsolvers`:

```cpp
  // Launch the main search loop.
  if (params.interleave_search()) {
    int batch_size = params.interleave_batch_size();
    if (batch_size == 0) {
      batch_size = params.num_workers() == 1 ? 1 : params.num_workers() * 3;
      …
    }
    DeterministicLoop(subsolvers, params.num_workers(), batch_size,
                      params.max_num_deterministic_batches());
  } else {
    NonDeterministicLoop(subsolvers, params.num_workers(), shared->time_limit);
  }
```

`interleave_search` is the **only** predicate. `max_deterministic_time` does not
appear in it. With `num_workers=4` and `interleave_search=false`, the solver
runs `NonDeterministicLoop` whatever the time limit is set to.

**So: `interleave_search=true` is required for deterministic parallel search;
`max_deterministic_time` does not suffice on its own.** This is the main place
the docs contradict common belief — "set a deterministic time limit and parallel
CP-SAT becomes reproducible" is false as stated. The deterministic cap governs
*when* the search stops; `interleave_search` governs *whether the search is a
function of the input at all*.

### 2.3 Why batching is the mechanism

[`subsolver.h:205-217`](https://github.com/google/or-tools/blob/stable/ortools/sat/subsolver.h#L205)
documents the contract:

> `// Similar to NonDeterministicLoop() except this should result in a`
> `// deterministic solver provided that all SubSolver respect the Synchronize()`
> `// contract.`
> `//`
> `// Executes the following loop:`
> `// 1/ Synchronize all in given order.`
> `// 2/ generate and schedule up to batch_size tasks using an heuristic to select`
> `//    which one to run.`
> `// 3/ wait for all task to finish.`
> `// 4/ repeat until no task can be generated in step 2.`
> `//`
> `// If max_num_batches is > 0, stop after that many batches.`

and `subsolver.cc:154-156` states the invariant that would otherwise break:

> `    // We first generate all task to run in this batch.`
> `    // Note that we can't start the task right away since if a task finish`
> `    // before we schedule everything, we will not be deterministic.`

The information a worker sees is frozen between synchronisation points
(`subsolver.h:55-58`: "The intended implementation for determinism is that tasks
update asynchronously (and so non-deterministically) global 'shared' classes,
but this global state is incorporated by the Subsolver only when Synchronize()
is called."). That is what removes thread timing from the result.

Note the conditional in the contract: **"provided that all SubSolver respect the
Synchronize() contract"**. Determinism here is a property maintained by every
subsolver, not enforced by the framework. One counterexample already ships:

> `  // Warning: This currently non-deterministic.`
> `  optional bool share_linear2_bounds = 326 [default = false];`
>
> — `sat_parameters.proto:786-787`

Default false, so the default configuration is safe; enabling it destroys
determinism even with `interleave_search=true`.

### 2.4 The genuinely deterministic stopping rules

`DeterministicLoop(subsolvers, num_threads, batch_size, max_num_batches)`
(`subsolver.cc:130-131`) **takes no time limit argument at all**. Its own
termination conditions are "no task can be generated" and:

> `  // Stops after that number of batches has been scheduled. This only make sense`
> `  // when interleave_search is true.`
> `  optional int32 max_num_deterministic_batches = 291 [default = 0];`
>
> — `sat_parameters.proto:338-340`, verbatim

So there are two machine-independent caps: `max_deterministic_time` (accounted
per subsolver via `SubSolver::AddTaskDeterministicDuration`,
`subsolver.h:115-118`) and `max_num_deterministic_batches` (a pure counter).
**If `max_time_in_seconds` is also set and fires first, determinism is lost
again regardless of `interleave_search`.** **[INFERENCE]**, from the fact that
the wall clock is then what decides where the run ends.

Two edge cases worth knowing: `batch_size == 1` makes `DeterministicLoop` fall
straight through to `SequentialLoop` (`subsolver.cc:134-136`), and
`interleave_search=true` with `num_workers=1` defaults `batch_size` to 1
(`cp_model_solver.cc:826-828`) — i.e. that combination is sequential, with one
feasibility-jump worker forced in (`cp_model_solver.cc:2150-2153`).

**Cost not measured here.** `interleave_search` is "Experimental" and
synchronises at every batch boundary; what it costs in solution quality per
wall-second on this repo's models is **[NOT CHECKED]** and must be measured
before it is made the default. Also listed unread in the tracker:
[#4875 "Interleave search option ignores assumptions"](https://github.com/google/or-tools/issues/4875)
(title only — **[NOT CHECKED]**).

---

## 2.5 — the prescription, measured (ticket 83)

§2.2 concluded from `LaunchSubsolvers` that `interleave_search` is the only route
to a deterministic parallel solve, and ADR 0043 decision 5 turned that into a
prescription: a stable gate needs `interleave_search=true` +
`max_deterministic_time` + pinned `random_seed` and `num_workers`, asserting
**status and objective, never seconds**. `solver-formulation.md` Part X.2 runs
that exact configuration, twice per cell, 36 cells.

**It is necessary and it is not sufficient, and the boundary falls on C13's band.**

| n | status repeats | objective repeats | Plan repeats |
|---:|---:|---:|---:|
| 8 | 12/12 | 12/12 | 11/12 |
| 12 | 12/12 | 12/12 | 1/12 |
| 24 | 12/12 | **0/12** | 0/12 |

Inside the shipped 3–10 band the prescription delivers a reproducible run. At 12
it delivers exactly the plane ADR 0043 decision 5 tells a gate to assert — status
and objective stable, cover not — which is independently what ADR 0046 decision 4
found on the conversion model. At 24 it delivers neither.

⚠️ **The unqualified reading of decision 5 — "this configuration makes a run
reproducible" — is false above ten rooms.** The decision is not withdrawn: its
guard, *assert status and objective and never seconds*, is what survives, and it
survives because it was written conservatively. Read it as **band-limited**.
This is google/or-tools [#3948](https://github.com/google/or-tools/issues/3948)
again — §1.4 could not confirm it in this repo, ADR 0046 decision 3 confirmed it
on the conversion model, and Part X confirms it on the projection model.

---

## 3. Units of `max_deterministic_time`

The proto says only "the time unit being as close as possible to a second"
(§2.1). `time_limit.h` says what the quantity actually is:

> `// TODO(user): The expression "deterministic time" should be replaced with`
> `//                 "number of operations" to avoid confusion with "real" time.`
>
> — [`time_limit.h:95-96`](https://github.com/google/or-tools/blob/stable/ortools/util/time_limit.h#L95)

It is a **weighted count of operations**. The weights are fitted, not derived —
`time_limit.h:77-89` gives the procedure: collect counter values in debug mode,
measure real time in optimised mode, then solve
`C_1*c_1 + C_2*c_2 + … + C_N*c_N + Err = T` for the coefficients "e.g. using the
least squares method". The counters are compiled out in optimised builds
(`time_limit.h:91-93`), and dtime never advances on its own — it "has to be
advanced manually using the method AdvanceDeterministicTime()"
(`time_limit.h:54-56`).

Three consequences:

- **The budget is machine-independent.** Same binary, same model, same
  parameters → the same operation count is consumed regardless of how fast the
  machine executes it. That is exactly why it is the right cap for a regression
  gate.
- **The wall-clock mapping is machine-dependent by construction**, since the
  coefficients were fitted against real time on *some* machine. "≈1 second" is
  the calibration target, not a property of your CPU.
- **The correlation is an aspiration, not a contract.** The proto hedges
  ("should be correlated"), and the maintainer confirms it fails in places. On
  [#5199](https://github.com/google/or-tools/issues/5199), where a user reported
  interleaved chunks with a hardcoded `max_deterministic_time = 1.0` consuming
  "several minutes of wall time each", Laurent Perron replied (2026-05-30): "the
  real issue is that for some code, the correlation between time and dtime is
  bad." That issue is still **open**.

Practical rule for this repo: **a dtime cap is publishable; the wall time it
costs is an observation of one machine and must be reported with the hardware
named.** Converting between them across machines is not supported.

---

## 4. `random_seed` at `num_workers=1` with a proved OPTIMAL

`sat_parameters.proto:385-392`, verbatim:

```proto
  // At the beginning of each solve, the random number generator used in some
  // part of the solver is reinitialized to this seed. If you change the random
  // seed, the solver may make different choices during the solving process.
  //
  // For some problems, the running time may vary a lot depending on small
  // change in the solving algorithm. Running the solver with different seeds
  // enables to have more robust benchmarks when evaluating new features.
  optional int32 random_seed = 31 [default = 1];
```

So, changing the seed at `num_workers=1`:

- **changes the search path** ("may make different choices during the solving
  process") and therefore the runtime, "a lot" on some problems;
- **can change which optimal solution is returned.** OR-Tools states this by
  building a test policy around it (`sat_parameters.proto:394-400`, verbatim):

```proto
  // This is mainly here to test the solver variability. Note that in tests, if
  // not explicitly set to false, all 3 options will be set to true so that
  // clients do not rely on the solver returning a specific solution if they are
  // many equivalent optimal solutions.
  optional bool permute_variable_randomly = 178 [default = false];
  optional bool permute_presolve_constraint_order = 179 [default = false];
  optional bool use_absl_random = 180 [default = false];
```

Google randomises *its own tests* precisely so that no client can depend on
which of several optimal solutions comes back. That is the closest thing to an
anti-guarantee in the file, and it applies at any `num_workers`.

- **cannot change the optimal objective value**, since `OPTIMAL` asserts the
  bound was proved. **[INFERENCE]** — definitional; no primary source states it.

Direct consequence for this repo: a golden-file test that pins a *layout* is
pinning one of many optima and will break on any solver upgrade. Pin the
*objective value and the status*, plus the checker's verdict — never the
geometry, unless the geometry is provably unique.

---

## 5. Reporting discipline for time-capped / stochastic solvers

Four conventions worth adopting, each with its primary source.

**(a) Multiple seeds — from OR-Tools itself.** "Running the solver with
different seeds enables to have more robust benchmarks when evaluating new
features" (`sat_parameters.proto:389-391`). The vendor's own advice is that a
single-seed figure is not a benchmark.

**(b) Performance profiles (Dolan & Moré).** *Benchmarking Optimization Software
with Performance Profiles*, E. D. Dolan and J. J. Moré,
[arXiv:cs/0102001](https://arxiv.org/abs/cs/0102001), published as Math. Program.
91(2):201-213, 2002. Abstract, verbatim: "We propose performance profiles —
distribution functions for a performance metric — as a tool for benchmarking and
comparing optimization software. We show that performance profiles combine the
best features of other tools for performance evaluation." The point for us: plot
the cumulative distribution of each configuration's performance *ratio* to the
best on each instance, rather than ranking by mean time or by wins at one fixed
cap — a single time-capped mean is exactly the statistic a profile is designed
to replace.

**(c) Fixed repeat counts, olympic scoring, mandatory seed logging — MLPerf.**
From [`mlcommons/training_policies/training_rules.adoc`](https://github.com/mlcommons/training_policies/blob/master/training_rules.adoc):

- Minimum number of runs per benchmark is a published table (currently 3 to 10
  depending on benchmark; `training_rules.adoc:531-541`).
- "Each benchmark result is computed by dropping the fastest and slowest runs,
  then taking the mean of the remaining times." (`:543`)
- "An MLPerf submission score is intended to represent the median expected
  result across a large number of runs." (`:552`)
- Seeds must be logged, must be valid integers, and **must not repeat**: "If one
  run logs one seed on a certain line in a certain source file, no other run can
  log the same seed on the same line in the same source file." (`:179`)
- Running extra sets of N to find the best is "against the spirit of MLPerf and
  is prohibited"; the M>N sliding-window escape requires "an objective and
  deterministic method, such as submission timestamps" for ordering (`:556-560`).

**(d) How to report a difference below noise — ACM.** From the
[ACM Artifact Review and Badging policy, v1.1](https://www.acm.org/publications/policies/artifact-review-and-badging-current):
badges are *Artifacts Available*, *Artifacts Evaluated — Functional*, *Artifacts
Evaluated — Reusable*, *Results Reproduced* (obtained by others **using** the
authors' artifacts) and *Results Replicated* (obtained **without** them). The
operative sentence for us, verbatim:

> "In each cases, exact replication or reproduction of results is not required,
> or even expected. Instead, the results must be in agreement to within a
> tolerance deemed acceptable for experiments of the given type. In particular,
> differences in the results should not change the main claims made in the
> paper."

That is the discipline: declare the tolerance up front, and require that the
*claim*, not the number, survives it. A difference inside the seed spread is
reported as "no measured difference at N seeds, spread ±x", never as an
improvement.

**(e) MIPLIB.** [miplib.zib.de](https://miplib.zib.de/) distributes "the
instance sets as well as supplementary data, run scripts and the solution
checker" and accepts solution submissions for verification. No MIPLIB rule
prescribing seeds, caps or repeat counts for *reported timings* was found —
**not found in this pass**; do not cite MIPLIB for that.

### What a figure in this repo must carry

Adopting (a)-(d), any solver number quoted in a doc or a commit message needs:

1. `ortools` version (`9.15.6755` today);
2. the parameters that decide determinism — `num_workers`, `interleave_search`,
   `random_seed`, and any `subsolvers` / `filter_subsolvers` override;
3. the cap, **by type and value** — `max_deterministic_time=D` is publishable,
   `max_time_in_seconds=T` is machine-local;
4. N runs × which seeds, reported as a distribution (min / median / max), with
   the olympic mean if a single number is unavoidable;
5. the machine, for any wall-clock figure;
6. the tolerance under which the claim is asserted.

---

## 6. Who enforces this mechanically

Two suites enforce it with a check that **fails**, not a convention that is
read.

**MLPerf — yes, a submission gate.** `training_rules.adoc:176-183`: "The only
way to log seeds is through `mllog`. Any seed logged via any other method is
discarded. … Unsatisfying any of the above requirements will result in seed
checker failures reported by the
[package checker](https://github.com/mlcommons/logging/tree/master/mlperf_logging/package_checker)."
The checker family is code in `mlcommons/logging`: `package_checker` (with
`seed_checker.py`, which even defines which files count as source files),
`compliance_checker` (per-benchmark YAML configs) and `rcp_checker` (reference
convergence points). A submission failing the RCP test can only proceed with
`--rcp-bypass`, which obliges the submitter to notify the results chair and face
an audit (`:591`). Resubmitting old logs requires passing the current round's
checker (`:512`). This is the strongest model available: the reproducibility
metadata is machine-checked before a number may be published.

**BenchExec (SoSy-Lab, the harness behind SV-COMP) — yes, on the measurement
environment.** `python -m benchexec.check_cgroups` calls `sys.exit(1)` when the
required cgroup controllers are missing or when a probe run terminates
abnormally
([`benchexec/check_cgroups.py:33-39, 58-63`](https://github.com/sosy-lab/benchexec/blob/main/benchexec/check_cgroups.py)) —
its docstring is literally "@raise SystemExit: if cgroups are not usable". The
guidance it enforces or warns on
([`doc/benchmarking.md`](https://github.com/sosy-lab/benchexec/blob/main/doc/benchmarking.md)):
container mode must not be turned off (`:36-40`); "Without a fixed memory limit,
the amount of memory available for benchmarking is non-deterministic" (`:43-45`);
"In certain situations, BenchExec will issue a warning during benchmarking, e.g.,
if Turbo Boost is enabled, the system overheated etc." (`:47-50`); "Runs with I/O
suffer from non-deterministic performance" (`:60-61`). Rationale is published as
Beyer, Löwe & Wendler, *Reliable Benchmarking: Requirements and Solutions*, STTT
2019, [doi:10.1007/s10009-017-0469-y](https://doi.org/10.1007/s10009-017-0469-y).
Note the scope: BenchExec gates the *machine*, not the reported figure.

**MIPLIB 2017 — partially.** A solution checker and run scripts ship with the
instance sets, and submitted solutions are verified before the solufile is
updated. Mechanical for *solution validity*; nothing found that mechanically
checks a timing claim.

**SAT Competition — mechanical for correctness, not for reproducibility.** The
[2024 rules](https://satcompetition.github.io/2024/rules.html) disqualify a
solver that "produces a wrong answer" and require UNSAT certificates (proofs) in
the Main track — both machine-checked. Searching that rules page for
"deterministic", "seed", "wall" and "CPU time" returned **no matches**: **no**
mechanical reproducibility requirement was found there.

**ACM badging — no.** Human review by a committee; the badge asserts a
judgement, not a passing check.

**Not checked in this pass:** MiniZinc Challenge rules, SV-COMP's own
competition rules beyond BenchExec, and the Mittelmann benchmarks.

---

## What this note does not establish

- Whether CP-SAT is bit-identical **across machines** under a deterministic cap.
  Undocumented, unmeasured. The cheap experiment — same model, same params, two
  machines, compare status / objective / `solution_info` — has not been run here.
- Whether [#3948](https://github.com/google/or-tools/issues/3948) (single-worker
  non-determinism, reproduced by the maintainer) was fixed, and in which version.
  9.15 may or may not still contain it.
- ~~The **cost** of `interleave_search=true` on this repo's models.~~
  **Measured — ticket 83, `solver-formulation.md` Part X.3.** It is not
  affordable as a default and the wall cap is why: at 8 rooms it costs **10,2×**
  the wall time for the same proved-optimal objective, at 12 it buys total
  determinism at **2,36×** the objective (165 against 70), and at 24 under the
  shipped 15 s cap it returns **0 valid Plans of 24** where the default portfolio
  returns 18. Given a *deterministic* budget and no wall cap it is instead the
  **best** arm at 24 rooms — 24/24 valid, zero coverage slack — at 24,7 s p50
  against a 15 s product cap. So: a **gate** configuration, never a product one.
  ⚠️ And a gate only inside C13's band: see §2.5.
- Whether presolve is deterministic when a *wall-clock* cap truncates it.
  Presolve carries its own dtime limits
  (`presolve_probing_deterministic_time_limit`, `sat_parameters.proto:480`),
  which suggests it is dtime-bounded by design, but a wall-clock cap firing
  mid-presolve is a different question and was not traced.

## Bearing on what is already in this repo

`docs/research/solver-formulation.md` records "**Workers** — `num_workers = 4`
for every run below" alongside wall-clock timings (6.25 s for the 24-room case).
By §2.2 those runs used `NonDeterministicLoop`, so **they are not reproducible
runs**: they are valid single-machine observations and must not be promoted into
regression thresholds. A gate that needs to be stable belongs on
`interleave_search=true` + `max_deterministic_time` + pinned `random_seed` and
`num_workers`, and must assert **status and objective**, not seconds.

⚠️ **Read that last sentence with §2.5.** Ticket 83 ran the prescription and it
holds inside C13's 3–10 band and stops holding above it — status and objective
repeat 12/12 at 8 and 12 rooms, and the objective repeats **0/12** at 24. The
guard (*assert status and objective, never seconds*) is what makes the decision
survive its own measurement; the promise of a reproducible run is band-limited.
