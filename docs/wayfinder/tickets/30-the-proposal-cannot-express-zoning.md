---
id: 30
title: The Proposal cannot express zoning
parent: map
labels: [wayfinder:grilling]
status: closed
assignee: tng
blocked_by: [28]
writes:
  - docs/spec/proposer.md
  # Declared on resolution rather than taken quietly.  The frontier was wholly
  # unclaimed at the time, so the map's concurrency rule held -- ticket 28's
  # precedent.  The entries are here so the next ticket to want them can see.
  - CONTEXT.md                    # Private room corrected; Sleeping room, Sleeping group
  - docs/research/zoning.md (new)
  - experiments/zoning/ (new)
---

# The Proposal cannot express zoning

## Question

**Everything this system optimises is pairwise, and the property architects rank
plans by is not.**

The Proposal transmits **separation directions** — for each pair of Rooms,
whether one is left of, right of, above or below the other, or abstains
(`CONTEXT.md`). The solver promotes those to hard linear constraints. The
arrangement metric scores per-pair agreement, and *Proposer architecture survey*
found per-pair agreement is what predicts survival. So the whole chain, from
corpus conversion to Proposal to objective to metric, is pairwise.

**No pairwise relation can express any of these:**

- **Day/night zoning.** "The bedrooms are grouped, and they are away from the
  entrance." That is a property of a *set* against another *set*, and it is the
  first thing any architect checks on a residential plan.
- **Served and servant.** Bathroom next to bedrooms, utility next to kitchen —
  clustering by function, not by direction.
- **Sequence.** Entry → hall → living is an ordered path, not a set of
  left-of relations. Two plans with identical pairwise separations can have
  completely different entry sequences.
- **Facade allocation.** Which rooms get the good elevation. H8 asks only whether
  a habitable room touches *an* exterior run; it cannot say the living room
  should get the long one and the bathroom should not.

A plan can satisfy every pairwise relation in a real dwelling and still put the
WC off the living room and the master bedroom next to the front door. The map has
two partial hooks and neither is zoning: **forbidden adjacency** (a blunt
per-pair veto) and **circulation** (private rooms receive but never forward,
which is a weak day/night proxy that fires only through the contact graph).

**What has to be decided:**

1. **Whether zoning belongs in the Proposal, the Acceptance bar, or the ranking.**
   Three different answers with different costs. In the Proposal it must be
   expressible as constraints the solver can post — a set-versus-set separation is
   posted as "every room in A is left of every room in B", which is cheap and
   linear. In the bar it is a predicate. In the ranking it is a soft score and
   changes nothing about what is generated.
2. **Whether zones are Brief-stated or inferred.** A Homeowner says "I want the
   bedrooms away from the living room" in prose, and C4 says the Brief is the real
   interface — so this is probably a Brief field, which makes it *program* like
   `access_via` rather than geometry. If it is inferred from room type instead,
   say from what.
3. **Whether the corpus can even supply it.** Swiss Dwellings has room types and
   geometry; whether real dwellings show consistent zoning that a model could
   learn is unmeasured. It is measurable — the converted corpus from
   *Rectangularising real rooms* has typed rectangles and an entrance side.
4. **What it does to the arrangement metric.** *What the model proposes* defines
   three numbers, all pairwise. If zoning is the thing that matters, the metric
   is measuring the wrong property well. Feeds *Validate the arrangement metric
   against the solver*, which is currently validating it against **solver
   survival** rather than against **plan quality** — those are different tests
   and only the first is scheduled.

**Why this is not the existing fog patch.** *Plan quality beyond the validator*
asks whether the soft-rule score correlates with human judgement. That is an
**evaluation** question. This is a **representation** question: the Proposal
contract, as specified, has no vocabulary in which zoning can be stated, so no
amount of eval will surface it and no training run can learn it. A metric can be
fixed later; a contract that cannot express the property has to be reopened.

**Blocked by *Whether a Room may be more than one rectangle*.** Both tickets amend
the same object — `docs/spec/proposer.md` §1, the Proposal contract — and 28 changes
its shape rather than adding to it: if a Room may be *k* boxes, "exactly *n*
axis-aligned boxes, one per Brief Room" is no longer the contract a zoning
amendment would be written against. Settle the shape first, then what it carries.

**Deliverable.** A decision on where zoning lives, and if it enters the Proposal,
the amendment to `docs/spec/proposer.md` §1 and the constraint form for the
solver. Plus the corpus measurement in item 3, which is cheap and tells us
whether there is a signal to learn at all.

---

## Resolution

**Zoning lives in the solver and the Acceptance bar, never in the Proposal — and
the ticket's premise was half wrong, which is what made the answer cheap.**

`docs/research/zoning.md`, `docs/spec/proposer.md` §1/§6.1/§7, `CONTEXT.md`,
`experiments/zoning/` (2 500 Swiss dwellings, two passes plus a sensitivity run).

### The premise

*"Everything this system optimises is pairwise"* is false, and the
counter-example was already shipped: `solver-formulation.md` records that
*"reachable and clustered are the same constraint with different node sets"*, and
`wet.plumbing_group_count` is a hard, `site: both`, set-versus-set predicate
today. **The Proposal is pairwise; the system is not.** Three of the ticket's
four properties are that routine on a third node set, or a soft term over an edge
ring that already exists. One is not, and only that one needed new technology.

### The nine decisions

- **D1** zoning is **inferred from Room type**, never a Brief field — the whole
  surveyed market makes adjacency user-authored, and every one of those products
  sells to a practitioner who can draw a bubble diagram. C2's buyer cannot, and a
  Brief field would make the *unzoned* plan the default.
- **D2** the node set is a **new flag `is_sleeping`**, and **may not be `is_private`**.
- **D3** grouping is a **hard bound of two** plus a soft gradient — `wet`
  clustering's exact shape, landing independently on the same number.
- **D4** facade allocation is **soft, and reinstated**.
- **D5** **social transit** is soft, and it is a rule nobody had written.
- **D6** the front door opening onto circulation is a **warn**.
- **D7** **ordered sequence is out of v1** — the only property needing machinery
  that does not exist. Ticketed as *What an ordered entry sequence costs the solver*.
- **D8** **the Proposal gains no field, and that is the decision.**
- **D9** what zoning changes in this spec is **evaluation**.

### D8 is the ticket's actual answer, and it turns on where ADR 0014 stops

ADR 0014 put *shape* into the contract on a measured argument — told which Room
is an L the solver places **25 of 25 with none spurious**; left to find them it
places 10 of 18 and **invents 35**. The obvious move was to run that argument
again for zoning. **It does not transfer.** L-ness is a property of the *truth
being copied*, which only the Proposal has seen. A sleeping group is a property
of **Room type**, which the `ResolvedBrief` already carries — so the solver
derives the node set itself, and there is nothing the Proposal could tell it that
the Brief has not. The refusal is recorded in §1 *with* this reasoning so it is
not reopened as an oversight.

### D9 is what the ticket did not know it was for

Item 4 asked what zoning does to the arrangement metric. The answer is that it
does nothing to it, and supplies what it was never able to be: ticket 24
established the metric predicts **feasibility, not survival**, and nothing in
this system has ever measured whether a Plan is any *good*. Sleeping-group count,
longest-run allocation and social transit are **computable on a corpus dwelling
and a generated Plan by the same code** — which corner displacement is not, a real
dwelling having no Proposal to be displaced from. `proposer.md` §6.1 takes all
three, as evaluation terms and explicitly **not** as stop conditions.

### Measured

- **Sleeping groups**: 69.8 % one, 27.7 % two, **2.5 % three** — so ≤ 2 covers
  **97.5 %**, and demanding *one* would reject 30 % of real homes, the identical
  error `wet.plumbing_group_count`'s own note records against wet clustering.
- **Day/night gradient**: private mean hop **1.66** against social 1.21, but
  within one dwelling private is *nearer* the door **16.1 %** of the time. Real,
  directional, and not a predicate.
- **Facade**: longest single exterior run **12.24 m** social against 8.22 m
  private, and the social Room wins it **73.7 % to 26.3 % with no ties**; dual
  aspect **19.9 %** against 8.2 %. Topological — no site, which is out of scope.
- **Social transit**: **11.1 %** of real bedrooms are reachable only through a
  social Space, in **18.2 %** of dwellings, and it **rises with dwelling size**
  (14.4 % at n = 6, **35.4 % at n = 10**) rather than concentrating in
  corridor-less small flats, which was the hypothesis.
- **Front door**: **93.2 %** opens onto circulation.

### Four corrections to this session's own claims

Listed rather than quietly dropped — ticket 28's precedent.

1. ⚠️ **The facade refutation was withdrawn, and the withdrawal was the error.**
   Pass 1 normalised boundary share by area, found social rooms hold *less*
   facade per m² (0.93 against 1.05), and reported the property as unmeasurable.
   Wrong correction: "the living room gets the best elevation" is a claim about an
   **absolute, indivisible, scarce** resource, and daylight-per-m² already has two
   rules. Measured absolutely the property is strong. **The proposed drop would
   have deleted a real differentiator on a bad statistic.**
2. ⚠️ **The candidate hard rule "every private Room touches circulation" is
   threshold-dominated and supports nothing** — 52.9 % of private Rooms at the
   shipped 1.00 m contact run, **66.2 %** at 0.80 and **78.4 %** at 0.60. Same
   confound class as H8's *"dead from 7 rooms"*.
3. ⚠️ The *"dwellings without circulation almost never route through a social
   room — 1.0 %"* cell is an **artefact** of the cut test excluding dwellings
   whose entry *is* the social Room. Not quotable.
4. ⚠️ Sequence was first deferred wholesale as too expensive; its **first hop is
   free** — 93.2 %, one Space, no new machinery — and shipped as D6.

### Found on the way, in settled documents

- ⚠️ **`is_private` does not mean what `CONTEXT.md` said it meant.** The flag is
  true on `bathroom`, `shower_room` and `wc`; the glossary described the sleeping
  set. The flag is **right for its rule** — you should not route through a
  bathroom either — and the glossary was describing a different class. Corrected
  here, and it is load-bearing: a zoning rule reaching for "the bedrooms" and
  finding `is_private` **silently acquires the bathrooms**.
- ⚠️ **29 % of real dwellings come out disconnected** on the contact graph at the
  shipped 1.00 m run. Confounded by this session's buffer method, so it is a flag
  and not a finding — but if it survives a cleaner measurement,
  `circ.potential_reachability` over-rejects real homes. Handed to
  *Look at the converted corpus* and *Re-measure the conversion at two rectangles
  per Room*, which own the conversion.

### Written, and not written

Written: `docs/research/zoning.md`, `docs/spec/proposer.md`, `CONTEXT.md`,
`experiments/zoning/`. The last three are **declared on resolution** rather than
taken quietly — the frontier was entirely unclaimed at the time, so the map's
concurrency rule held; ticket 28's precedent.

Not written, and specified in full at `zoning.md` §5b so the holder transcribes
rather than re-decides: **one flag** to `room-constraints.json` (two claimants)
and **five rules** to `rules.json` (four claimants). One is hard, four are soft or
warn.

⚠️ **The honest limit on D3**: 97.5 % of *real* dwellings already pass the hard
bound, so as a filter it barely binds. Its value is insurance against a generator
nobody has run — **no Proposer exists**, so the violation rate on generated plans
is unmeasured, and the four soft rules carry the work.
