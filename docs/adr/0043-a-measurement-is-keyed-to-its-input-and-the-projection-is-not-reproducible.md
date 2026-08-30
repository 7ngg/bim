# ADR 0043 — A measurement is keyed to its input, and the projection is not reproducible

**Status:** accepted
**Ticket:** [A time-capped solver is not a reproducible measurement](../wayfinder/tickets/82-a-time-capped-solver-is-not-a-reproducible-measurement.md)
**Supersedes:** nothing. **Amends:** nothing. **Constrains:** every rig that solves.

## Context

Ticket 65 measured a reproducibility floor by accident. Two sweeps ran
concurrently and warped 1 489 identical `(brief, donor)` pairs — same seed, same
targets, same `--time=3.0`, same code — and disagreed on `served` **2,82 %** of
the time and on `dev` **14,71 %**. It attributed this to the wall clock, and
ticket 82 was raised to characterise that floor and say which published figures
it reaches.

**The attribution was wrong, and it was wrong in a way that mattered.** Two
concurrent sweeps are two *processes*, and every warp drew its per-room objective
weights through `random.Random(SEED ^ (hash(key) & 0xFFFF))`. `hash()` on a `str`
is salted per process. The two sweeps did not solve one model twice under
different load — **they solved different objective functions**, `W_STATED` 8
against `W_INVENTED` 1, re-drawn per process.

`experiments/warp/repro_floor.py` separates the two with a 2×2 — the weight draw
fixed or varied, crossed with a wall-clock cap or `max_deterministic_time` —
under deliberate CPU contention, because an idle machine reports the wall clock
at 0,00 % and exonerates it.

| cell | `served` | `dev` | solves hitting the cap |
|---|---:|---:|---:|
| `wall/varied` — ticket 65's condition | 4,00 % | 36,00 % | 2,9 % |
| `wall/fixed` — the wall clock alone | **0,00 %** | **4,00 %** | 2,9 % |
| `det/varied` — the salted draw alone | 4,00 % | 32,00 % | 0,0 % |
| `det/fixed` — control | **0,00 %** | **0,00 %** | 0,0 % |

The salted draw is **32 of the 36 points** of `dev` and **4 of the 4** of
`served`. It moves answers that were *proved OPTIMAL* — `det/varied` disagrees on
46,7 % of the enriched sample with **0 of 90** solves reaching a cap — so no
stopping rule addresses it. The wall clock's effect is conditional and sharp
rather than diffuse: it binds on 18,9 % of solves on the hard population and
`dev` moves on **85,7 %** of the pairs where it bound.

**It scales with the cap and vanishes at the shipped one.** Same 25 pairs:

| cap | solves hitting it | wall clock alone | salted draw alone |
|---:|---:|---:|---:|
| 0,5 s | 34,8 % | 8,00 % | 32,00 % |
| 3,0 s | 2,9 % | 4,00 % | 32,00 % |
| **15,0 s** | **0,0 %** | **0,00 %** | 32,00 % |

`docs/research/solver-reproducibility.md` establishes what OR-Tools actually
guarantees, from its own source. The word "reproducible" appears **nowhere** in
`sat_parameters.proto`'s 1 925 lines. `LaunchSubsolvers`
(`cp_model_solver.cc:823-836`) branches on `interleave_search` and on nothing
else; `max_deterministic_time` does not appear in the predicate.
`DeterministicLoop` (`subsolver.cc:130-131`) takes **no time-limit argument at
all**. And single-worker determinism has failed in practice — google/or-tools
issue **#3948**, fixed seed, differing optimal fingerprints, maintainer reply
*"Reproduced."*

## Decision

**1. A rig seeds every draw from its INPUT, never from the process.**
`zlib.crc32(key.encode())`, not `hash(key)`. Same distribution, keyed to the
thing being measured. Applied at five sites in `experiments/warp/`;
`experiments/plane-accounting/arms.py:175` is the sixth and is owed to its own
ticket. `PYTHONHASHSEED=0` is endorsed as a **second layer only** — it makes
reproducibility a property of how the process was launched, is silently lost by
any re-exec, and cannot be asserted from inside the code.

**2. `experiments/warp/salt_check.py` is a ship gate.** It scans every `.py`
outside `venv/`, blanks string literals so it does not report its own prose, and
exits 1 on any unowned site. It is proven in both directions — red on a
reverted site, green on repair. **This is a check because it was already a
README line**: ticket 65 wrote the trap into `experiments/warp/README.md`, naming
`hash`, `PYTHONHASHSEED` and the fix, and five live sites went on carrying the
defect underneath it in the same directory. Its home is
`experiments/environment/env_check.py`; it is written here because that file
belongs to no one and this ticket may not take it.

**3. The warp is reproducible on one machine and says no more than that.**
`num_workers = 1` plus `max_deterministic_time` measured **0,00 %** on both
fields in every run, at a median 1,34 s against the wall cap's 1,35 s. Per
issue #3948 and the absent documentation, the publishable claim is *"reproducible
on this machine, verified by repeat"* — **not** "reproducible", and never
cross-machine.

**4. The shipped projection is NOT reproducible, and this is entailed rather
than broken.** It runs 4 workers and cannot drop below 2 —
`solver-formulation.md` II.6: *"Two workers is the floor. A single-worker
deployment is not a slower product, it is a broken one at the top of the room
range."* A parallel solve is deterministic only under `interleave_search=true`,
which is marked **"Experimental."** and defaults to false; and `DeterministicLoop`
takes no time limit, so **a `max_time_in_seconds` that fires first destroys
determinism regardless**. The 15 s wall cap is a product constraint (C6, C10).
**A 15 s wall cap and a reproducible projection are mutually exclusive.**
`homeowner-surface.md` already discloses this — *"the link carries the request,
not the results: generation is not reproducible from a Brief alone"* — and
nothing here asks for it to change.

**5. No timing from a non-interleaved parallel run may become a threshold.**
Every run in `solver-formulation.md` used `num_workers = 4` with no
`interleave_search`, so all of them ran under `NonDeterministicLoop`. They are
valid single-machine observations. A gate that must be stable needs
`interleave_search=true` + `max_deterministic_time` + pinned `random_seed` and
`num_workers`, and must assert **status and objective, never seconds**.

**6. A solver figure carries its provenance, and a difference below the floor is
reported as unresolved rather than as a number.** Six items, adopted from the
field rather than invented — MLPerf fails a submission whose seeds are not
logged, and reports an olympic mean over 3–10 runs; BenchExec exits non-zero
when the machine cannot be measured reliably:

1. `ortools` version;
2. `num_workers`, `interleave_search`, `random_seed`, any subsolver override;
3. the cap **by type and value** — `max_deterministic_time=D` is publishable,
   `max_time_in_seconds=T` is machine-local;
4. N runs × which seeds, as a distribution, olympic mean if one number is forced;
5. the machine, for any wall-clock figure;
6. the tolerance the claim is asserted under.

**7. The floor under a published figure is the AGGREGATE floor, not the per-pair
rate.** Quoting 36 % per-pair `dev` disagreement against a 1,3-point served
margin compares two different quantities. Measured directly by `agg_floor.py`,
150 pairs, 6 draws, deterministic cap:

| statistic | range | sd |
|---|---:|---:|
| served rate | **1,33 pts** | **0,54 pts** |
| `dev` p50 | 0,0011 | 0,0004 |
| `dev` p90 | 0,0132 | 0,0054 |

## Consequences

1. **Published arm orderings stand, and now it is known what carries them.**
   Every arm table in `experiments/warp/` is computed on warp rows *shared per
   key* — `gate_effect.warp_candidates` and `gate_depth.py` both warp the union
   once and let the rules filter it — so the draw cancels between arms.
   `gate_depth.boot_ci` resamples *Briefs*, each carrying its own realised draw,
   so the published CIs propagate this variance rather than understating it.
   **No published conclusion moves.**

2. **And the pairing is doing more work than anyone knew.** ADR 0032's margin is
   1,3 points of served against an aggregate range of 1,33. Unpaired, that
   headline would sit ~2,4 sd from pure objective-draw noise. The orderings are
   safe *because* of the shared rows, not despite the salt being small.

3. **Every cross-run delta on this map is unmeasurable until the draw is keyed —
   and the `market`-arm re-run is exactly that shape.** A re-run in a new process
   re-drew every weight vector, so "what moved" mixed the change under test with
   a re-drawn objective. **62 and 67 own that debt**; it must now clear ~0,5
   points of served before it means anything and may not be quoted to tenths.

4. **62's matched-pair design never matched on the objective.** It pairs an
   off-frame donor against an on-frame one at matched `worst_room_iou`; different
   donors are different keys, hence different weight vectors, so the pairing's
   variance reduction was partly illusory. `run_one` now takes **`wseed`** —
   pass the same value to both members and the pairing becomes real.

5. **Ticket 65's own refusal is confirmed quantitatively.** Its pooled p90 gap of
   0,0038 is below the 0,0054 sd measured here, so it was genuinely unresolvable;
   its thin-half gap of 0,0266 is ~5 sd and clears.

6. **Pre-fix figures are unbiased estimates and are not re-derivable, and this
   is accepted rather than repaired.** Re-running the load-bearing sweeps would
   cost roughly a day and move figures under three in-flight tickets to
   re-derive numbers that were never wrong. Draw 0 — the `crc32` value now
   shipped — sits mid-band at 70,67 %, so fixing the seed does not ship an
   outlying realisation. **Everything measured from today is reproducible; what
   came before is labelled, not re-run.**

7. **The debt was already on the record in another rig and went unpaid.**
   `solver-formulation.md` II.6: *"Every timing is a single run at seed 20260817.
   There is no variance estimate… must be repeated over ≥ 10 seeds before any of
   them is quoted as a specification."* Written before ticket 82 existed. That is
   the failure decision 2 exists to stop repeating.

8. **`interleave_search`'s cost is unmeasured** and it is "Experimental". What it
   costs in solution quality per wall-second on this repo's models is **not
   checked** and must be measured before anything makes it a default.
