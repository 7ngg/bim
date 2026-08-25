# A parse-time bound inherits the severity of the rule it is the pre-image of

`brief.md` §9.4 was *"two bounds, two severities, one function"*. Four tickets
handed it four more bounds in one week — an upper area bound, a room-count gate, a
room-count promise, and a Brief-against-itself check — and every one of them
arrived with the same question attached: **is this a refusal or a warning?**

Answered case by case, that question has no defensible answer. It reads as a
product judgement, it is made by whoever happens to hold the file that week, and
six independent judgements will not agree with each other or with the validator.
*What the engine says when the Envelope is bigger than the programme* stated it
outright: *"The severity is not obvious and is a real decision."*

**It is not a decision. It is a read.**

## The pre-image

The Acceptance bar is one declaration with two consumers — a solver posting and a
validator check (`CONTEXT.md`, **Acceptance bar**). §9.4 is a third consumer, and
its bounds are not new rules. Each is the **arithmetic pre-image** of a rule the
validator already holds: the set of Briefs that cannot possibly produce a Plan
satisfying it, computed before any Plan exists.

```
Brief B fails the pre-image of rule R   ⟺   every Plan reachable from B fails R
```

If that implication holds, the severity is fixed. Firing the pre-image softer than
`R` promises a Plan that `R` will destroy; firing it harder refuses Briefs `R`
would have passed. Neither is a choice anyone is entitled to make in `brief.md`.

Applied, this decides four of §9.4's bounds outright — four of six when this was
written, four of **seven** since ADR 0020 added the stated-`shape` bound, which is
a third no-pre-image case alongside ADR 0013's two:

| bound | pre-image of | severity, read not chosen |
|---|---|---|
| Σ realisable ergonomic minima | `dim.min_area`, hard | hard |
| Σ `market_default` | `dim.market_default_area`, soft | warn |
| Σ `Room.target_area` vs `target_area` | `area.invented_envelope_hard` (hard) **or** `area.given_envelope_warn` (warn) | hard **or** warn, by Envelope provenance |
| Σ upper band vs a given interior | `dim.max_area` ∧ `model.no_unassigned_area`, both hard | hard |

The third row is the one that pays for this ADR. The same inequality carries two
severities, and nobody chose either: the shipped rules disagree because a drift an
invented Envelope causes is the engine's fault and a drift a given Envelope causes
is nobody's. `area.given_envelope_warn`'s own note already argued it —
*"rejecting on it would reject 100 percent of them for a fault none of them
caused"* — and that argument transfers to parse time unchanged.

The fourth row is the one that changes a product answer. Read as a product
question, *"the Homeowner owns that flat and cannot resize it, so do not refuse
them"* is a strong argument and it points at `warn`. Read as a pre-image, `warn` is
simply false: two hard rules at site `both` make the assignment illegal, so
proceeding produces a Plan with unassigned floor that the validator kills and C6
discards, and the Homeowner sees zero survivors with no explanation — the failure
§9.4 exists to prevent. The refusal is not the engine declining work. It is the
engine reporting that the arithmetic has no solution, and naming the two edits that
give it one.

## Soft becomes warn, and only there

`dim.market_default_area` is `soft` — a ranking term, not a filter. There is
nothing to rank at parse time, so its pre-image surfaces as `warn`. That is the
one place the mapping is not the identity, and it is a projection of the same fact:
soft says *this is worse*, and with a single Brief and no gallery, *worse* can only
be said.

## Two bounds are not pre-images, and they say so

ADR 0013's gate — engine room count outside 3–10 — refuses Briefs that would
otherwise generate perfectly good Plans. It is a **scope gate**: a claim about what
this product serves, not about what the geometry permits. It has no pre-image and
its severity is a genuine product decision, taken and argued in ADR 0013. The
promise, 1–4 otaq, is the same.

That is the boundary this ADR draws. A bound is either derived from a rule, in
which case its severity is not open, or it is a statement of scope, in which case it
belongs in an ADR of its own with the evidence attached. **What is not available is
a bound with an invented severity and no argument** — which is what §9.4 was
accumulating.

## Consequences

1. **A new dimensional rule now arrives with a question attached**: does it have a
   parse-time pre-image, and if so, is it computed? A rule whose pre-image is
   cheap and uncomputed is a zero-survivor screen waiting to happen. Three of the
   four bounds above were exactly that, and each was found by a different ticket,
   separately, after the rule shipped.
2. **§9.4's threshold values are inherited too, not only its severities.** Bound 5
   uses 5 %, and that is `area.invented_envelope_hard`'s shipped value rather than
   a new constant. A pre-image with a threshold of its own is a sign the
   implication does not actually hold.
3. **`rules.json` needs the pre-image evaluable against a `ResolvedBrief`.** The
   mechanism exists — `area.given_envelope_warn` already carries `scope: brief` —
   but nothing runs a brief-scoped predicate at parse time today. The bar becomes
   **one declaration, three consumers**, and `CONTEXT.md`'s **Acceptance bar** term
   is updated to say so.
4. **The same-sentence guarantee gets stronger rather than weaker.**
   `acceptance-bar.md` §11 requires that the parse-time check and the zero-survivor
   diagnosis produce the same sentence. If the parse-time bound *is* the validator
   rule's pre-image, that holds by construction and not by review.
5. **This does not license computing a pre-image where the implication is
   one-directional.** *Every Plan from B fails R* is what makes the severity
   transfer. *Some Plan from B might fail R* is a heuristic, and shipping one at
   `hard` refuses buildable Briefs. §9.4 bound 6 is the near miss: its right-hand
   side is not exact, because the partition footprint is only known after the
   solve — so it is stated at the **high** end of that footprint's distribution,
   which restores the implication at the cost of missing some true cases. The
   spread is not published; until it is, that bound rests on a point estimate and
   `brief.md` §13 says so.

## Considered and rejected

- **Severity as a product decision per bound.** What was happening. It produced
  four unresolved questions in four tickets, and the two answers already in the
  file — hard for the ergonomic floor, warn for the market line — turn out to be
  reads of `dim.min_area` and `dim.market_default_area`, arrived at
  independently and correctly. The rule was already being followed; it was not
  written down, so it could not be relied on.
- **All parse-time findings are warnings, because parse time is early.** Cheap and
  wrong. It makes bounds 1 and 6 promise Plans that cannot exist, and it is the
  behaviour C6 and `acceptance-bar.md` §11 were built to prevent.
- **All parse-time findings are refusals, because refusing early is kind.** It
  refuses the whole *served, not promised* zone ADR 0013 deliberately kept, and it
  turns `area.given_envelope_warn`'s 100 %-drift case — a fault no candidate
  caused — into a rejection.
- **Compute nothing at parse time; let the bar arbitrate.** This is what the code
  does today and it is the defect. The diagnosis is arithmetic over areas
  (`acceptance-bar.md` §11), so a Brief failing on a room count or on its own
  stated arithmetic is handed an *area* sentence — a wrong explanation, not a
  missing one, which ADR 0013 rejected on the same grounds.
