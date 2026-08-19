# The Proposer has two sources, and the Acceptance bar arbitrates

The map treated "retrieval **or** a trained model" as a fork with a trigger:
*Proposer architecture survey* §7.3 recommended the trained model and named
retrieval as the runner-up, to win outright if the ≥16-room tail proved empty.
*Acquire the datasets* then measured the tail at **66 dwellings against a ~1,000
threshold** — a factor of fifteen.

The fork is a false one, and the trigger measures a band v1 does not sell.

**The Proposer is two sources behind one Proposal contract. Retrieval-and-warp
over Swiss Dwellings, and a Brief-conditioned room-set transformer. Both emit the
same object, both are projected by the same solver, and the Acceptance bar picks
the survivors.**

## The construction

- **Source A, retrieval-and-warp.** Ships first. Admissible only inside a stated
  warp budget — exact room-multiset match, area within ±10 %, envelope aspect
  ratio within ±15 %. Outside it, retrieval declines and source B carries the
  Brief.
- **Source B, the trained transformer.** The survey's §7.1 architecture,
  unchanged, **minus synthetic pre-training**. Always answers.
- **`source` is not a Proposal field.** The job record carries it. The solver must
  not be able to prefer one source, or the design becomes a ranking policy.
- **Per-pair confidence is promoted from optional to required**, because two
  sources need a source-independent statement of which relations to trust.
- v1 serves **4–10 Brief-named rooms**, where the corpora are thick.

## Why, and what was measured

`experiments/retrieval-coverage/`, over all 46,800 Swiss Dwellings dwellings, in
the Brief's own room vocabulary, with each Brief taking one dwelling's programme
and a **different** dwelling's envelope — because a Homeowner's flat shape did not
come paired with the rooms they want:

| Brief rooms | retrieval pool = 0 | median pool |
|---|---:|---:|
| 4–6 | **9.5 %** | 92 |
| 7–10 | **12.4 %** | 66 |
| 11–15 | **67.7 %** | 0 |

Neither source survives alone against "v1 produces plans that are ready to use":

- **Retrieval blanks on roughly one common-band Brief in nine.** A product that
  refuses that often is not ready to use, and it is dead above ten rooms.
- **A trained model fails quietly.** It always emits something, so nothing signals
  the failure, and it throws away 46,800 arrangements that are a real home's by
  construction wherever they apply.

C6 already generates many candidates and rejects most. Nothing ever required them
to come from one source, so the second source costs a component and no new
architecture.

## Considered options

- **Retrieval only.** Rejected on the 9.5–12.4 % blank rate, and on 67.7 % above
  ten rooms. It is the cheapest answer and the survey's own runner-up, and it
  cannot ship a product that promises usable plans.
- **The trained model only, per the survey's recommendation.** Rejected because it
  discards a free, permanent, *live* baseline for §7.3(b) — the survey's own
  surviving condition, that retrieval must be beaten rather than assumed inferior.
  Under one source that comparison is a report written once; under two it is
  measured continuously in production.
- **Retrieval as a cold-start stopgap, replaced by the model once trained.**
  Rejected. It reads as the same design and is not: it makes retrieval's
  disappearance a schedule event rather than a measurement, and retrieval's real
  arrangements stay better than a model's inside the warp budget for reasons that
  do not expire.
- **Widening the warp budget so retrieval covers everything.** Rejected, and this
  is the one that would have been easiest. Retrieval's whole claim is that the
  arrangement is a real home's; a plan stretched 40 % in proportion is not one,
  and what comes out is the 90 %-right artefact C2 calls worse than a blank sheet.
  The budget is what makes the claim true, so it is a hard gate and not a ranking
  term.

## Consequences

- **Synthetic pre-training is cut from v1.** Its stated purpose was the 12–32 room
  regime; v1 does not promise it, and in-band the corpora hold ~60,600 dwellings
  against the survey's own ~4,000-record floor. Training drops from 10–25
  GPU-hours to 5–15. It returns only if the ceiling is raised.
- **§7.3(a)'s trigger no longer decides the route.** It counted the tail. §7.3(b)
  survives and becomes a production measurement.
- **Two failure modes to hold apart.** Retrieval fails loudly, by declining; the
  model fails quietly, by being subtly wrong. The mix is a **stated ratio in v1,
  never adaptive**, or the ablation confounds itself.
- **A stop condition exists**: 50 GPU-hours. Past it, v1 ships retrieval-only and
  states the room-count limit in the product copy alongside the two limits C5
  already commits to. Shippable, not a failure state.

Full spec: [`docs/spec/proposer.md`](../spec/proposer.md).
