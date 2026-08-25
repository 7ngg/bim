---
id: 48
title: What shape an Envelope is when the Brief does not say
parent: map
labels: [wayfinder:grilling]
status: open
assignee:
blocked_by: []
writes:
  - docs/spec/brief.md
---

# What shape an Envelope is when the Brief does not say

## Question

`brief.md` §5 step 2 says `shape` fixes the **notch count**, at most 2, and that
**notch positions are never statable** — a Homeowner who can place a notch can
draw, and C2 says they cannot. It does not say what happens when `shape` is
absent, which is the common case. Two things now depend on that silence and they
pull in opposite directions.

**1. A default of "rectangular" would silently delete retrieval.** *The retrieval
index and warp procedure* measured the corpus: **90.16 %** of converted dwellings
use both notches, 8.72 % one and **1.12 % none**; by area, only **6.5 %** leave
under 2 % of their bounding box unoccupied and 15.0 % under 5 %. A source with
two notches cannot serve an Envelope with none, because the notch cells would be
floor no Room claims and `model.no_unassigned_area` is hard. So
`shape = rectangular`, taken as a *stated* gate term, admits single-digit
percentages of the index — and taken as an unstated **default** it does that to
almost every Brief without anyone deciding it.

The obvious reading — absence means unknown, not rectangular — is probably right
and has a cost of its own: a Homeowner with a genuinely rectangular flat gets an
L-shaped plan and has to notice and correct it.

**2. ADR 0018 made the Envelope per-candidate, and nothing has been checked
against that.** Where `shape` is `invented`, each retrieved candidate carries its
own notch geometry, scaled from a real dwelling — which is why the position is a
measured number instead of an invented constant. But the Envelope was a per-job
object everywhere else on this map. Specifically owed:

- **What `area.invented_envelope_hard` compares against.** It is ±5 %, hard, over
  the area-determining fields. If two candidates have different notch geometry
  they have different interior areas, so the rule can pass on one candidate and
  fail on another for the same Brief. Is that correct, or does the rule bind the
  bbox rather than the interior?
- **What the Assumption surface says.** `brief.md` §6 has three Assumption kinds
  and the notch is an `invented_value`. A value that differs per candidate has no
  representation there today.
- **Whether `shape` stated should gate on notch count or notch *area share*.**
  Count is crude: a 2-notch envelope losing 3 % of its bbox reads as rectangular
  to a person, and the p10 of that share is **0.032**.

**What has to be decided:**

1. What `shape` resolves to when absent, and with what provenance.
2. Whether a stated `shape` gates retrieval on notch count, on notch area share,
   or on neither.
3. Whether an Envelope field may vary per candidate at all, and if so which
   consumers have to be told — `area.invented_envelope_hard` above all.
4. What the Homeowner is shown when it does. (The *presentation* half is fog on
   the map under *A Homeowner shown candidates whose outlines differ*; this
   ticket owes only whether the model permits it.)

**Why this is not `The retrieval index and warp procedure`'s to answer.** That
ticket writes `docs/spec/proposer.md` and this is `brief.md`'s shape. It found
the defect, measured it, and could not write the file.

**Deliverable.** `brief.md` §5 amended, and a line in §9.4 if any of it becomes a
pre-image bound. Mints an ADR only if answer 3 is *yes* — that one is hard to
reverse.
