# ADR 0046 — The conversion is reproducible where it is published, and the cover is not published

- **Status**: accepted
- **Date**: 2026-08-31
- **Ticket**: [The conversion is a time-capped, unseeded solve and every corpus figure rests on it](../wayfinder/tickets/85-the-conversion-is-a-time-capped-unseeded-solve.md)
- **Extends**: ADR 0043 — its decision 6 provenance list now binds the conversion,
  and its consequence 8 (*"`interleave_search`'s cost is unmeasured"*) is
  discharged here, negatively.
- **Amends**: ADR 0045 consequence 3 — *"which mechanism dominates is unmeasured"*
  is answered and the **43,1 % floor is struck**. Its conclusion stands. See ADR
  0045's `⚠️ Amended by ADR 0046`.
- **Supersedes nothing**
- **Evidence**: `docs/research/rectangularisation.md` §16;
  `experiments/rectangularise/determinism.py`, `repeat_check.py`, `run_arms*.sh`;
  records in `experiments/rectangularise/out/det/`.

## Context

`fit_rects.py` ran CP-SAT at `num_search_workers = 4` under a 10 s wall-clock cap
and never set `random_seed`. Every corpus figure on this map is quoted from
`swiss_fit_k2.json` or a sibling, and ADR 0041 published 1 535 two-part Rooms
where the current file yields 1 543 — two runs, one input, different answers.

**The ticket's premise was half wrong, and the wrong half changes the fix.**
CP-SAT's own default `random_seed` is **1**, asserted against the pinned build
rather than read off documentation, so the rig was never unseeded and
`random_seed = 1` is a no-op. Varying the seed to 7 produces disagreement
indistinguishable from running seed 1 twice. What varies is which of four workers
finishes first, and a tiling model whose objective is a sum of misassigned cells
has a large space of tied optima. **A defect caused by a race is not repaired by
keying a draw.**

`WORKERS = 4` cites *"ticket 15: two workers is a floor for correctness"*. That
floor was measured on the **shipped projection at 24 rooms** (`solver-formulation.md`
II.6). The conversion corpus is filtered to the 3–10 engine-room band and its
maximum is **10 rooms**, so the condition that justified four workers occurs in
**0,000 %** of this rig's inputs.

## Decision

**1. The conversion runs at `num_search_workers = 1`, and `random_seed` is set
explicitly.** One worker takes cover disagreement between two runs from 26,5 % to
**0,27 %** and per-Room shape-class disagreement from 7,5 % to **0 in 243**, at
**identical wall cost** (3,31 s/dwelling against 3,28–3,33) and a marginally
*better* conversion rate (0,9244 against 0,9219–0,9239). It costs ~5 proofs in
400. The seed is set not because it changes anything today but because a default
is not a decision: ADR 0043 decision 6 item 2 requires the seed be *recorded*, and
an implicit one becomes false the day the library changes it.

**2. The conversion's cap moves from 10 s to 30 s wall.** This goes one step
beyond reproducibility and the step is argued, not assumed. At 30 s the rig
returns **zero UNKNOWN** on 400 dwellings against three to six at 10 s, which
recovers ADR 0008's *"the tier is decidable, not a timeout"* — recorded as **dead**
on the map's Corpus-conversion row at 1,27 % UNKNOWN. It costs **1,73x** the wall
time (5,73 s/dwelling against 3,31), about **4,1 h** for the full 2 600 against
2,6 h, on an offline batch rig where nothing user-facing depends on the number.
It is also the repo's established escalation rather than a new one:
`rectangularisation.md` §11.0 re-ran ResPlan at 30 s when 16,5 % came back
undecided and *"every plan resolved"*. And it is what makes decision 1 exact — at
30 s the single-worker pair is byte-identical, cover included, where at 10 s one
record in 366 still moved.

⚠️ **The cap is a bias, not a band**: 10 s against 30 s moves pooled not-L by
1,3 points *directionally*, where the race moves it 0,77 points symmetrically. Any
figure quoted at 10 s is displaced, not merely noisy.

**3. `interleave_search` is refused, and the refusal is measured rather than
inherited.** At four workers with a deterministic budget it costs **1,85×** the
wall time, loses three proofs in sixty, drops the wall bound entirely — a
deterministic budget has none, by ADR 0043 decision 4's own reasoning — and
**still returns different covers**, three of them on records both runs proved
OPTIMAL at an identical objective. That is google/or-tools **#3948**, which ADR
0043 cited and could not confirm in this repo. It is confirmed. **ADR 0043
consequence 8 is discharged: the flag is not made a default anywhere.**

**4. The published plane of a conversion record is `status`, `objective`,
`k_used`, and the shape class its Parts make. The cover is not publishable.**
A document may quote the published plane; a figure derived from the specific
rectangles is a figure derived from a tie-break.

**And the plane is stable exactly where the record is proved.** Split by status,
two runs of the shipped configuration disagree on **0** shape classes in 139
proved-optimal Rooms and **17** in 88 truncated ones; objectives differ **0** times
on proved records and 18 times on truncated ones. The race swaps tied optima
without changing their shape; **the cap is what reaches the figures**, and it
reaches them because FEASIBLE dwellings carry 41,2 % of all two-part Rooms. This
is why decisions 1 and 2 are one decision and not two.

**5. Every figure already quoted from `swiss_fit_k2.json` stands, with a band,
and the band is quoted as an sd.** Over **five** runs of the shipped
configuration on one 400-dwelling key list: not-L **sd 0,77 points**, conversion
rate sd **0,0011**, two-part per Room sd **0,049 points**, two-part count sd
**2,2 Rooms**. **No published conclusion moves.**

⚠️ **Quote the sd, never the range.** The not-L range went 0,58 points at four
runs to 2,08 at five, because a range is an order statistic and climbs with n.
Four realisations understated the spread ~2x with nothing to signal it, which is
ADR 0043 decision 6 item 4 — *"N runs, as a distribution"* — earning its keep.

ADR 0041's 1 535-versus-1 543 is **0,52 %** relative against a two-part count sd
of **0,91 %** relative: roughly **0,6 sd**, an ordinary and smaller-than-typical
draw. It needed no population filter because it was never a population
difference — and it is mostly *population churn* rather than Rooms changing
shape, since only 2–3 Rooms per pair change part count while the decided
population moves by up to 28 Rooms at the cap.

**6. The index is NOT regenerated for this, and the fix rides the pass that is
already owed.** `proposer.md` §2.2: *"Until the pass runs, the conversion is
frozen and every figure quoted here is on the union-mrr frame."* ADR 0031 replaces
`dwelling_frame` with the area-weighted modal room angle, which re-bases the file
wholesale, and the Corpus-conversion row already owes six per-record fields on
that same run with the instruction to take them in one pass. **This is the
seventh item on it.** A standalone regeneration would spend the whole re-fit cost
to invalidate every published figure once, and the frame pass would invalidate
them again — the asymmetry the ticket named is real and it points the other way.

**7. `salt_check.py` does not grow this check, and neither does `env_check.py`.**
That check catches a defect that is static and unconditional. `num_search_workers
= 4` is **correct** in `solver.py` and defended by ADR 0043 decision 4, so a
pattern firing on both the defect and the defended decision cannot separate them:
it would sit in the OWED table beside `solver.py` and go quiet.
`experiments/rectangularise/repeat_check.py` asserts the **behaviour** on the rig
that claims it — solve, solve again, compare the published plane — and
deliberately does not assert the cover, because a check that is red on an upstream
defect nobody here can repair is a check that gets switched off.

## Consequences

1. **The conversion's reproducibility claim has a form, and it is the same one the
   warp uses.** *"Reproducible on this machine, verified by repeat"* — never
   "reproducible", never cross-machine (ADR 0043 decision 3, issue #3948).

2. **ADR 0045's 43,1 % floor is struck and its conclusion is strengthened.**
   *"Proved optimal at 10 s"* is not a fixed population, it is the **easy**
   dwellings; raising the cap moves T/Z-rich dwellings into it. The two planes
   converge on **~45–46 %**, above the struck bound and above the published
   44,8 %, so the contract admitting all four shapes is better evidenced than when
   it was decided.

3. **The cap is a bias, not a band, and it is a bigger effect than the race.**
   Ten seconds against thirty moves pooled not-L by **1,3 points** directionally,
   where the race moves it 0,4 points symmetrically. Any figure quoted at the 10 s
   cap is displaced, not merely noisy — which is why decision 4's band is stated
   on the race and this is stated separately.

4. **ADR 0008's *"decidable, not a timeout"* is recovered, not merely
   recoverable.** The Corpus-conversion row records it as **dead** at 1,27 %
   UNKNOWN; decision 2 takes it to **zero** on 400 dwellings. That row's ⚠️ can
   be struck once the frame pass runs — not before, because the guarantee is a
   property of the shipped file and the shipped file has not been rebuilt yet.

5. **A configuration change shifts a published figure by more than the noise
   band.** Four workers and one worker at the same 30 s cap, on the 369 dwellings
   both decide to the same quality, report **46,4 %** and **50,2 %** not-L — 3,8
   points against a within-configuration sd of 0,77, with zero status and zero
   part-count differences. Neither is more correct: both are optimal covers of an
   objective that does not determine shape. **A figure computed under one
   configuration may never be quoted against one computed under another** — which
   costs nothing here only because decision 6 re-derives every figure on the frame
   pass. ⚠️ A *systematic* worker preference is **not** established: the per-Room
   sign test gives p = 0,021 at 30 s and p = 0,50 with the opposite sign at 10 s.

6. **A threshold that names its source can still be wrong, and this is the second
   one.** `WORKERS = 4` carried *"ticket 15"* in a comment, which is why nobody
   re-examined it; the citation made it look checked. ADR 0043 consequence 7
   caught the same shape in `solver-formulation.md` II.6's *"single run at seed
   20260817"*. **A citation records where a number came from, not that it still
   applies.**

7. **`resplan_fit_k2.json` carries the same defect and is not re-run here.** The
   argument transfers and the numbers do not; it is named so the next reader does
   not assume this decision reached it.
