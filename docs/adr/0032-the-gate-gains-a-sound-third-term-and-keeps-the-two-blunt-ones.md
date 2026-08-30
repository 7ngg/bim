# The gate gains a sound third term, and keeps the two blunt ones

> ⚠️ **AMENDED by ticket 65 — read the amendment at the foot before quoting
> anything here.** Everything below is correct **at `m = 3`** and was verified as
> such. The shipped `m` is 8, and at realised depth the decision below changes:
> the scalar pair is kept but becomes **depth-conditional**. Consequence 5's owed
> measurement is discharged there, and the probe it names is shown to be the wrong
> instrument. ⚠️ **Every figure on this page predates ADR 0037 and is computed
> with a `with-replacement` estimator that makes `m = 3` a best-of-2.11**; the
> amendment quantifies both. Do not quote this page's absolutes against any
> post-0037 number.

*The rig gate is not the shipped gate* (ticket 60) measured that total area
±10 % and envelope aspect ±15 % are worth **8.6 points of decline** — 27.6 %
against 36.2 %, paired within one Brief — and named the mechanism: ADR 0020 sizes
the box from the **Brief**, so a donor's own area and aspect never enter the
warp's arithmetic. What they bound is how hard the donor's **cut-line frame** has
to stretch to reach that box, and the stretch is what the ergonomic floor and
`dim.aspect_ratio_hard` refuse.

That makes the pair a **proxy**, and three measurements said a coarse one: the
effect is a dose rather than a step (28.3 → 30.1 → 40.2 → 55.2 %), **57.9 %** of
refusals fail one term only, and neither term *is* the stretch. *The gate
measures stretch with two blunt scalars* (ticket 63) asked what the direct
quantity is and whether it replaces the pair.

## What the measurement found

**The stretch has a closed form, and it was in the warp's own model all along.**
`warp_model` posts `Σ gx = W`, `gx_i ≥ 1`, and for each part
`Σ gx[a:b] ≥ MIN_SIDE[room]`. So for **any** set of parts with pairwise-disjoint
x-spans, `Σ MIN_SIDE ≤ W`. Maximising that sum over disjoint sets is an interval
DP — microseconds, pure Python, no solve, no new dependency — and it yields
`W_req`, the smallest box extent the donor's frame admits at the ergonomic floor.
Likewise `H_req`.

```
req = max( W_req / W , H_req / H )        W, H = ADR 0020's box, at scale 1.0
```

**The bound is sound, and that is the whole of its value.** `req > 1` is a
violated necessary condition of the model the warp actually solves, so it implies
INFEASIBLE. Measured over the 1,974 candidates `gate_effect.py` had already
warped: **103 of 103**, no exceptions. It is not *sufficient* — it does not model
the 2-D coupling `wv ≤ 3·hv` or the area objective — so 98 candidates it admits
were refused anyway. A sound term can only refuse a candidate the warp would have
declined, which is why it can be added to a hard gate with no coverage argument.

**It is a far better predictor of decline than either incumbent term, and it is
monotone where one of them is not.**

| band | decline | | band | decline |
|---|---:|---|---|---:|
| `req ≤ 0.7` | **16.2 %** | | `d_area ≤ 1` | 29.9 % |
| `0.7–0.85` | 35.0 % | | `1–2` | 37.4 % |
| `0.85–1` | **65.2 %** | | `2–4` | **31.6 %** ← non-monotone |
| `> 1` | **100 %** | | `> 4` | 53.3 % |

**The cut sits at 1.0 and is not fitted.** It is where the warp's own hard
constraint sits — the same licence `proposer.md` §2.2.4 gives `frontage_reach`
and explicitly denies `frame_residual`, which has "no knee to cut on".

**The ticket's own first candidate is not a new quantity.** The per-axis ratio of
donor frame extent to box extent is `√(area ratio × aspect ratio)` and
`√(area ratio ÷ aspect ratio)` — the `(1 − s)` cancels — a bijection with the
incumbent pair up to the donor's *void* share. It agrees with the incumbent
conjunction on **89.4 %** of candidates. It is the incumbent in polar
coordinates.

**And replacement loses, once the population is corrected.** `gate_effect`'s
draw is 50/50 admitted/refused; a production bucket is **82.4 %** refused, and
that bias runs toward loosening the gate. Reweighting each row by its own Brief's
stratum size — no new warps — gives the bucket's real composition. Best-of-pool
worst-room deviation per Brief, 400 bootstrap draws at **m = 3**, the largest
depth both arms fill with distinct warps:

| gate | Briefs served | best-of-pool p50 | p90 |
|---|---:|---:|---:|
| incumbent ±10 %/±15 % | 88.1 % | 0.0596 | 0.2303 |
| **incumbent + `req ≤ 1`** | **89.4 %** | **0.0591** | **0.2294** |
| `req ≤ 1` alone | 89.4 % | 0.0643 | **0.2543** |
| `logd ≤ 0.30` + `req ≤ 1` | 89.1 % | 0.0638 | 0.2333 |

Dropping the scalar pair moves the **p90 the wrong way**, and p90 is the tail the
Homeowner and the acceptance bar both read. The pair is buying *proportion*; the
bound is buying *feasibility*. They are orthogonal, not competing.

## The decision

**`req ≤ 1` joins the gate as a third dimensional term. The ±10 % / ±15 % pair
stays exactly as it is.**

- **It refuses only corpses.** Per-candidate decline **27.6 % → 22.9 %** by
  removing 60 of the incumbent's 987 admitted candidates, every one of which the
  warp refused. Best-of-pool p50, p90 and Brief-level served rate are
  **identical** to the incumbent's in both bands, because a dead member was never
  the best member.
- **It is not free, it is better than free.** `m` is a warp budget, so a dead
  candidate wastes a draw. At the bucket's real composition and equal `m`, adding
  the term takes served Briefs **88.1 % → 89.4 %** and p90 0.2303 → 0.2294 — it
  wins on all three axes by spending the same budget on live members.
- **A third refuser is normally the wrong direction, and soundness is what makes
  this the exception.** Every other gate term on this page trades coverage for
  quality. This one trades nothing.
- **`dim.max_area` is unmoved.** Exact upper bound on the breach rate, from
  `dev > k_min − 1 = 1.02`: **1.96 %** incumbent, 1.96 % with the term added.

## Considered and rejected

- **Replace the pair with `req` alone.** Measured; at the bucket's real
  composition and equal depth it costs **2.4 points of best-of-pool p90**
  (0.2303 → 0.2543) for 1.3 points of served Briefs. The pair is not inert and it
  is not redundant with the bound.
- **Replace the pair with a smooth radial `logd ≤ 0.30`.** The honest version of
  a conjunction that fails one term only 57.9 % of the time, and it does behave
  better than the box — but 0.30 is a **fitted constant chosen for the look of a
  table**, which §2.2.4 refuses everywhere else, and it still loses to keeping the
  pair (p90 0.2333 against 0.2294).
- **Gate on a boundary shape distance, as Graph2Plan ranks on.** Graph2Plan
  filters on room types, counts and adjacencies and ranks by a turning function
  anchored at the front door — its shape match is a *rank*, not a gate. Adopting
  the quantity needs the donor's real boundary polygon, which the index record
  does not carry and the frozen `fit_rects.py` pass does not owe. Out for v1; the
  market prior it supplies is about *ranking*, and §2.2.4 already ranks.
- **Tighten to `req ≤ 0.7`**, which on the 50/50 population dominates the
  incumbent on four axes at once. Rejected: it is a fitted constant, it stops
  being sound the moment it drops below 1.0, and the population it wins on is the
  one §4e exists to correct.

## Consequences

1. **The gate is four terms, not three** — multiset, area, aspect, `req ≤ 1` —
   plus `worst_room_iou ≥ 0.30` and ADR 0018's notch-count term where `shape` is
   stated. `proposer.md` §2.2 and §2.2.4 step 1.
2. **The index record owes nothing new.** `req` is computed from the cut-line
   frame with per-part index spans, which ADR 0018 consequence 6 already owes,
   and the room types, which it already carries. The frozen `fit_rects.py` pass
   does **not** grow a seventh field.
3. **`W_req`/`H_req` are per-donor and Brief-free.** Only the division by the box
   is per-candidate, so the two DPs can be precomputed into the index and the
   serving cost is two divisions. `experiments/warp/stretch_terms.py`.
4. **The 8.6-point figure is now decomposed.** Of the incumbent's advantage,
   4.7 points are certain-decline candidates the bound removes for free; the
   remainder is proportion fidelity the pair buys and the bound cannot.
5. ⚠️ **The `m = 8` comparison is still owed.** The bootstrap saturates at each
   arm's distinct-warp count — three against six — so at `m = 8` it compares
   best-of-3 with best-of-6 and is not quotable. A real answer needs
   `gate_effect.py --k=8`, ~2 h of warps. The shipped `m` is 8, and every figure
   in this ADR is at 3.
6. **`experiments/warp/README.md` carries the three traps**: quote §4e and never
   §4b, never quote the `m = 8` block, and `ext` is a control and not a
   candidate.

---

# Amendment (ticket 65): at the shipped depth the pair becomes conditional

*What the fourth gate term is worth at the shipped pool depth* discharged
consequence 5. **The decision above is right at `m = 3` and does not survive
`m = 8` unchanged.** `experiments/warp/gate_depth.py`; two seeds, 6 421 warps.

## The amended decision

**The `req ≤ 1` bound stays. The ±10 % / ±15 % pair stays, but stops being an
unconditional gate: apply the pair, count what it admits, and where it admits
fewer than `m`, top the pool up from `req ≤ 1` until it holds `m`.**

Where the pair admits `m` or more this **is** the gate above, member for member.
Only where it would otherwise hand the engine a short pool does the sound bound
fill the draw.

## Why the original decision does not transfer

**The argument above is stated "at equal `m`", and at the shipped `m` the arms
are not at equal `m`.** The pair admits a median pool of **8** and fills `m = 8`
on **51.7 %** of Briefs; `req ≤ 1` admits a median **52** and fills it on 85.4 %.
The joined gate of the decision above is the **shallowest of the three** — a
conjunction only removes members — and leaves an empty pool on **12.5 %** of
Briefs against the pair's 9.7 % and the bound's 0.0 %.

At realised depth, over 288 Briefs, seed 20260819:

| gate | Briefs served | 95 % CI | p90 |
|---|---:|---|---:|
| incumbent pair | 83.0 % | [78.8–87.2] | 0.1369 |
| **as decided above (join)** | **83.0 %** | [78.8–87.2] | 0.1285 |
| `req ≤ 1` alone | 97.9 % | [96.2–99.7] | 0.1196 |
| **amended (depth-conditional)** | **97.6 %** | [95.8–99.3] | 0.1234 |

**The whole of the effect is in the Briefs the pair starves, and it is absent
where it does not.** Splitting on whether the pair fills `m`:

| | pair | `req ≤ 1` | join | **amended** |
|---|---:|---:|---:|---:|
| **pair short of `m`** (n = 139) | 64.7 % / p90 0.2124 | 95.7 % / 0.1820 | 64.7 % / 0.2124 | **95.0 % / 0.1554** |
| **pair fills `m`** (n = 149) | 100 % / **0.0673** | 100 % / 0.0744 | 100 % / **0.0671** | 100 % / **0.0673** |

In the lower half the pair costs **31.0 points of served Briefs**, CIs disjoint
([56.8–72.7] against [92.1–98.6]). In the upper half every rule serves every
Brief and the pair holds the **best** p90 — the decision above, reproduced
exactly. Repeated at seed 20260830 (194 Briefs) every one of those claims holds.

**Why conditional rather than replacement.** `req ≤ 1` alone buys the same served
rate and is **worse on p90 in both halves separately** — 0.1820 against 0.1554
where the pair is short, 0.0744 against 0.0673 where it is not, on seed 1, and
the same ordering on seed 2. The pair is buying proportion, exactly as the
decision above found; it is only failing to buy *depth*. Making it conditional
keeps the first and stops paying for the second.

⚠️ **And the practical argument is the strongest one: this amendment needs
nothing from `proposer.md` §2.2.** Replacement would strand §2.2's *"stretch a
plan 40 % in proportion and the claim is false"* on the rank alone. The
conditional gate leaves that sentence true wherever the pair is not starving —
**51.7 %** of Briefs — and changes no text in that file. §6.1 gained a fifth term
and ADR 0042 under ticket 66 while this was measured; neither is touched.

## What this amendment does NOT claim

⚠️ **Read this section before quoting a number above.**

- ⚠️ **No pooled dominance over `req ≤ 1` is claimed, and none was found.** The
  per-half p90 advantage is stable on both seeds; **the pooled p90 changes sign
  between them** — seed 1 has the replacement ahead 0.1196 to 0.1234, seed 2 has
  the amendment ahead 0.1096 to 0.1179. That comparison is a mix effect over
  differently-served Brief sets and is **not resolvable at this sample size. Do
  not quote a pooled p90 in either direction.**
- ⚠️ **The 0.3-point served gap between the amendment and the replacement is not
  real.** It sits below the noise floor below. The two arms are level on served.
- ⚠️ **This is not a re-opening of `req ≤ 1`.** The bound is sound, its cut is
  unfitted, and it is unchanged.
- ⚠️ **It is not a threshold change.** ±10 %, ±15 % and 1.0 all keep their values;
  only *when the pair is consulted alone* changes.
- ⚠️ **`m` itself is not re-decided.** Whether 8 is the right budget is a separate
  question this measurement does not answer.

## The precision floor every figure here is subject to

⚠️ **CP-SAT at a time cap is not deterministic, and no figure from these rigs may
be quoted to tenths of a point without reproduction.** Two sweeps warped 1 489
identical `(brief, donor)` pairs — same seed, same targets, same `--time=3.0`.
Status agreed every time; **2.82 % disagreed on `served`** and **14.71 % on
`dev`**. Which claims here survive that floor:

- **Survives**: the 14.9-point served gap between the pair and the amendment; the
  31.0-point gap in the lower half; the 100 %/64.7 % split; the pool-depth
  medians. All are an order of magnitude clear of it.
- **Does not survive**: the 0.3-point served gap to `req ≤ 1`; the pooled p90
  comparison; any comparison of two arms differing by under ~3 points of served.

This floor is not specific to this ADR — it sits under every timed figure
`experiments/warp/` has published, several of which are quoted to tenths
elsewhere. **Ticket 82** carries it.

## Amended consequences

6. **The gate's fourth term is conditional, not unconditional.** `proposer.md`
   §2.2.4 step 1 gains the pool-size test — *apply the pair; if it admits fewer
   than `m`, extend from `req ≤ 1`*. **Owed to that file's next holder as prose;
   ticket 65 did not hold it.**
7. **Serving cost is unchanged.** The top-up reads terms already computed for
   every bucket member and draws from a set already ranked; it adds no solve, no
   index field, and no warp. Measured: the arm costs **zero** additional warps,
   because every member it can draw is inside `req ≤ 1`'s own first-`m` draw.
8. ⚠️ **Consequence 5's named probe was the wrong instrument, and this is the
   part most worth carrying forward.** `gate_effect.py --k=8` drops any Brief
   without `K` members in **both** strata, so it keeps a Brief **iff the pair
   already admits 8** — 229 of 500, median admitted pool **17** against **2**
   among the dropped. It therefore retains **none** of the 54.2 % of Briefs where
   the effect lives, and on the population it does retain the decision above is
   confirmed. The ~2 h run it prescribes would have returned "confirmed" and been
   wrong at population level.
9. ⚠️ **This page's own estimator understates depth.** §4e draws `m` **with
   replacement**, so its `m = 3` is best-of-**2.11** and its `m = 8` is shallower
   still. Re-scoring ticket 65's data under that estimator reproduces **77 % of
   the served gap and 69 % of the p90 gap** to this page's figures — the
   difference between the two pages is mostly the estimator, not the corpus.
10. ⚠️ **`gate_effect.py`'s draw was never reproducible.** It seeded per Brief
   with `hash()`, salted per process, so this page rests on a sample no rerun can
   reconstruct. Fixed to `crc32` under ticket 65; the run-to-run variance of the
   figures above has never been measured and now cannot be.
